import os
from threading import Thread
import uuid
from coapthon.client.helperclient import HelperClient
from coapthon.messages.response import Response
from coapthon.server.coap import logging, CoAP
from coapthon.utils import create_logging
import coapthon.defines as coap_defines

__author__ = 'jacko'

if not os.path.isfile("logging.conf"):
    create_logging()

logger = logging.getLogger(__name__)
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)


class Client(object):
    def __init__(self, client_address):
        self.server = None
        self.server_thread = None
        self.server_address = None
        self.client_address = client_address

    def _start_client_server(self):
        logger.debug("Start Client server")
        self.server = CoAP(self.client_address)
        self.server_thread = Thread(target=self.server.listen, args=(10,))
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        # self.server.listen(10)
        logger.debug("Client Server started")

    def _register(self, server_address):
        self.server_address = server_address
        client = HelperClient(self.server_address)
        ep = uuid.uuid4()
        path = "/rd?ep=" + str(ep)
        response = client.post(path, '</>;rt="oma.lwm2m", </0>, </1>, </3/0>, </6/0>')
        assert isinstance(response, Response)
        if response.code != coap_defines.Codes.CREATED.number:
            logger.error("Registration Error")
            return
        registration_id = "/" + str(response.location_path)
        logger.debug(registration_id)

    def close(self):
        logger.debug("Close Client Server")
        self.server.close()

    def start(self):
        # self.server_thread = Thread(target=self._start_client_server)
        # self.server_thread.start()
        self._start_client_server()
        self._register(("127.0.0.1", 5683))