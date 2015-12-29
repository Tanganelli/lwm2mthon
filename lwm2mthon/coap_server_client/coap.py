import copy
import logging
import logging.config
import os
import random
import socket
import struct
import threading

from coapthon.messages.message import Message
from coapthon import defines
from coapthon.utils import Tree, create_logging
from coapthon.layers.blocklayer import BlockLayer
from coapthon.layers.observelayer import ObserveLayer
from coapthon.layers.requestlayer import RequestLayer
from coapthon.layers.resourcelayer import ResourceLayer
from coapthon.messages.request import Request
from coapthon.layers.messagelayer import MessageLayer
from coapthon.resources.resource import Resource
from coapthon.serializer import Serializer
import time
from lwm2mthon.layers.lwm2mobservelayer import LWM2MObserveLayer

if not os.path.isfile("logging.conf"):
    create_logging()

logger = logging.getLogger(__name__)
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)


class CoAP(object):
    def __init__(self, server_address, callback,  multicast=False, starting_mid=None):

        """
        Initialize the server.

        :param server_address: Server address for incoming connections
        :param multicast: if the ip is a multicast address
        :param starting_mid: used for testing purposes
        """
        self.stopped = threading.Event()
        self.stopped.clear()
        self.to_be_stopped = []
        self.purge = threading.Thread(target=self.purge)
        self.purge.start()

        # Resource directory
        root = Resource('root', self, visible=False, observable=False, allow_children=False)
        root.path = '/'
        self.root = Tree()
        self.root["/"] = root

        self._messageLayer = MessageLayer(starting_mid)
        self._blockLayer = BlockLayer()
        self._observeLayer = LWM2MObserveLayer(self._send_notifications, self.stopped, self.root)
        self._requestLayer = RequestLayer(self)
        self.resourceLayer = ResourceLayer(self)

        self._callback = callback

        self.server_address = server_address
        self.multicast = multicast

        addrinfo = socket.getaddrinfo(self.server_address[0], None)[0]

        if self.multicast:  # pragma: no cover

            # Create a socket
            self._socket = socket.socket(addrinfo[1], socket.SOCK_DGRAM)

            # Allow multiple copies of this program on one machine
            # (not strictly needed)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind it to the port
            self._socket.bind(('', self.server_address[1]))

            group_bin = socket.inet_pton(addrinfo[1], addrinfo[4][0])
            # Join group
            if addrinfo[0] == socket.AF_INET: # IPv4
                mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
                self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            else:
                mreq = group_bin + struct.pack('@I', 0)
                self._socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

        else:
            if addrinfo[0] == socket.AF_INET:  # IPv4
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            else:
                self._socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self._socket.bind(self.server_address)

    def purge(self):
        """
        Clean old transactions

        """
        while not self.stopped.isSet():
            self.stopped.wait(timeout=defines.EXCHANGE_LIFETIME)
            self._messageLayer.purge()

    def listen(self, timeout=10):
        """
        Listen for incoming messages. Timeout is used to check if the server must be switched off.

        :param timeout: Socket Timeout in seconds
        """
        self._socket.settimeout(float(timeout))
        while not self.stopped.isSet():
            try:
                data, client_address = self._socket.recvfrom(4096)
                if len(client_address) > 2:
                    client_address = (client_address[0], client_address[1])
            except socket.timeout:
                continue
            try:
                serializer = Serializer()
                message = serializer.deserialize(data, client_address)
                if isinstance(message, int):
                    logger.error("receive_datagram - BAD REQUEST")

                    rst = Message()
                    rst.destination = client_address
                    rst.type = defines.Types["RST"]
                    rst.code = message
                    rst.mid = self._messageLayer._current_mid
                    self._messageLayer._current_mid += 1 % 65535
                    self.send_datagram(rst)
                    continue

                logger.debug("receive_datagram - " + str(message))
                if isinstance(message, Request):
                    transaction = self._messageLayer.receive_request(message)
                    if transaction.request.duplicated and transaction.completed:
                        logger.debug("message duplicated, transaction completed")
                        if transaction.response is not None:
                            self.send_datagram(transaction.response)
                        return
                    elif transaction.request.duplicated and not transaction.completed:
                        logger.debug("message duplicated, transaction NOT completed")
                        self._send_ack(transaction)
                        return
                    args = (transaction, )
                    t = threading.Thread(target=self.receive_request, args=args)
                    t.start()
                # self.receive_datagram(data, client_address)
                elif isinstance(message, Message):
                    transaction = self._messageLayer.receive_empty(message)
                    if transaction is not None:
                        with transaction:
                            self._blockLayer.receive_empty(message, transaction)
                            self._observeLayer.receive_empty(message, transaction)

                else:  # is Response
                    transaction, send_ack = self._messageLayer.receive_response(message)
                    if transaction is None:  # pragma: no cover
                        continue
                    if send_ack:
                        self._send_ack(transaction)
                    self._blockLayer.receive_response(transaction)
                    if transaction.block_transfer:
                        transaction = self._messageLayer.send_request(transaction.request)
                        self.send_datagram(transaction.request)
                        continue
                    elif transaction is None:  # pragma: no cover
                        self._send_rst(transaction)
                        return
                    self._observeLayer.receive_response(transaction)
                    if transaction.notification:  # pragma: no cover
                        ack = Message()
                        ack.type = defines.Types['ACK']
                        ack = self._messageLayer.send_empty(transaction, transaction.response, ack)
                        self.send_datagram(ack)
                        self._callback(transaction.response)
                    else:
                        self._callback(transaction.response)
            except RuntimeError:
                print "Exception with Executor"
        self._socket.close()

    def _send_rst(self, transaction):  # pragma: no cover
        # Handle separate
        """
        Sends an RST message for the response.

        :param transaction: transaction that holds the response
        """

        rst = Message()
        rst.type = defines.Types['RST']

        if not transaction.response.acknowledged:
            rst = self._messageLayer.send_empty(transaction, transaction.response, rst)
            self.send_datagram(rst)

    def close(self):
        """
        Stop the server.

        """
        logger.info("Stop server")
        self.stopped.set()
        for event in self.to_be_stopped:
            event.set()
        self._socket.close()

    def receive_request(self, transaction):
        """
        Receive datagram from the udp socket.

        """

        with transaction:

            transaction.separate_timer = self._start_separate_timer(transaction)

            self._blockLayer.receive_request(transaction)

            if transaction.block_transfer:
                self._stop_separate_timer(transaction.separate_timer)
                self._messageLayer.send_response(transaction)
                self.send_datagram(transaction.response)
                return

            self._observeLayer.receive_request(transaction)

            self._requestLayer.receive_request(transaction)

            if transaction.resource is not None and transaction.resource.changed:
                self.notify(transaction.resource)
                transaction.resource.changed = False
            elif transaction.resource is not None and transaction.resource.deleted:
                self.notify(transaction.resource)
                transaction.resource.deleted = False

            self._observeLayer.send_response(transaction)

            self._blockLayer.send_response(transaction)

            self._stop_separate_timer(transaction.separate_timer)

            self._messageLayer.send_response(transaction)

            if transaction.response is not None:
                if transaction.response.type == defines.Types["CON"]:
                    self._start_retransmission(transaction, transaction.response)

                self.send_datagram(transaction.response)

    def send_datagram(self, message):
        """

        :type message: Message
        :param message:
        """
        if not self.stopped.isSet():
            host, port = message.destination
            logger.debug("send_datagram - " + str(message))
            message.timestamp = time.time()
            serializer = Serializer()
            message = serializer.serialize(message)

            self._socket.sendto(message, (host, port))

    def add_resource(self, path, resource):
        """
        Helper function to add resources to the resource directory during server initialization.

        :param path: the path for the new created resource
        :type resource: Resource
        :param resource: the resource to be added
        """

        assert isinstance(resource, Resource)
        path = path.strip("/")
        paths = path.split("/")
        actual_path = ""
        i = 0
        for p in paths:
            i += 1
            actual_path += "/" + p
            try:
                res = self.root[actual_path]
            except KeyError:
                res = None
            if res is None:
                if len(paths) != i:
                    return False
                resource.path = actual_path
                self.root[actual_path] = resource
        return True

    def _start_retransmission(self, transaction, message):
        """
        Start the retransmission task.

        :type transaction: Transaction
        :param transaction: the transaction that owns the message that needs retransmission
        :type message: Message
        :param message: the message that needs the retransmission task
        """
        with transaction:
            if message.type == defines.Types['CON']:
                future_time = random.uniform(defines.ACK_TIMEOUT, (defines.ACK_TIMEOUT * defines.ACK_RANDOM_FACTOR))
                transaction.retransmit_thread = threading.Thread(target=self._retransmit,
                                                                 args=(transaction, message, future_time, 0))
                transaction.retransmit_stop = threading.Event()
                self.to_be_stopped.append(transaction.retransmit_stop)
                transaction.retransmit_thread.start()

    def _retransmit(self, transaction, message, future_time, retransmit_count):
        """
        Thread function to retransmit the message in the future

        :param transaction: the transaction that owns the message that needs retransmission
        :param message: the message that needs the retransmission task
        :param future_time: the amount of time to wait before a new attempt
        :param retransmit_count: the number of retransmissions
        """
        with transaction:
            while retransmit_count < defines.MAX_RETRANSMIT and (not message.acknowledged and not message.rejected) \
                    and not self.stopped.isSet():
                transaction.retransmit_stop.wait(timeout=future_time)
                if not message.acknowledged and not message.rejected and not self.stopped.isSet():
                    retransmit_count += 1
                    future_time *= 2
                    self.send_datagram(message)

            if message.acknowledged or message.rejected:
                message.timeouted = False
            else:
                logger.warning("Give up on message {message}".format(message=message.line_print))
                message.timeouted = True
                if message.observe is not None:
                    self._observeLayer.remove_subscriber(message)

            try:
                self.to_be_stopped.remove(transaction.retransmit_stop)
            except ValueError:
                pass
            transaction.retransmit_stop = None
            transaction.retransmit_thread = None

    def _start_separate_timer(self, transaction):
        """
        Start a thread to handle separate mode.

        :type transaction: Transaction
        :param transaction: the transaction that is in processing
        :rtype : the Timer object
        """
        t = threading.Timer(defines.ACK_TIMEOUT, self._send_ack, (transaction,))
        t.start()
        return t

    @staticmethod
    def _stop_separate_timer(timer):
        """
        Stop the separate Thread if an answer has been already provided to the client.

        :param timer: The Timer object
        """
        timer.cancel()

    def _send_ack(self, transaction):
        """
        Sends an ACK message for the request.

        :param transaction: the transaction that owns the request
        """

        ack = Message()
        ack.type = defines.Types['ACK']
        # TODO handle mutex on transaction
        if not transaction.request.acknowledged and transaction.request.type == defines.Types["CON"]:
            ack = self._messageLayer.send_empty(transaction, transaction.request, ack)
            self.send_datagram(ack)

    def notify(self, resource):
        """
        Notifies the observers of a certain resource and its parent resources.

        :param resource: the resource
        """
        observers = self._observeLayer.notify(resource, self.root)
        pmin = self.root["/1/1/2"].get_value()
        for transaction in list(observers):
            timestamp = transaction.response.timestamp
            now = time.time()
            if timestamp is None or now > timestamp + pmin:
                pass
            else:
                observers.remove(transaction)

        self._send_notifications(observers)

    def _send_notifications(self, observers):
        logger.debug("Notify")
        for transaction in observers:
            with transaction:
                transaction.response = None
                transaction = self._requestLayer.receive_request(transaction)
                transaction = self._observeLayer.send_response(transaction)
                transaction = self._blockLayer.send_response(transaction)
                transaction = self._messageLayer.send_response(transaction)
                if transaction.response is not None:
                    if transaction.response.type == defines.Types["CON"]:
                        self._start_retransmission(transaction, transaction.response)

                    self.send_datagram(transaction.response)

    def send_message(self, message):
        if isinstance(message, Request):
            request = self._requestLayer.send_request(message)
            request = self._observeLayer.send_request(request)
            request = self._blockLayer.send_request(request)
            transaction = self._messageLayer.send_request(request)
            self.send_datagram(transaction.request)
        elif isinstance(message, Message):
            message = self._observeLayer.send_empty(message)
            message = self._messageLayer.send_empty(None, None, message)
            self.send_datagram(message)

