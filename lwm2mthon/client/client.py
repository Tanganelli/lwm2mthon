import json
from multiprocessing import Queue
from threading import Thread
import uuid

from coapthon import utils
from coapthon.messages.request import Request
import os
from coapthon.messages.response import Response
from coapthon.server.coap import logging
from coapthon.utils import create_logging
import coapthon.defines as coap_defines
import time

from lwm2mthon import defines
from lwm2mthon.defines import ObjectId
import lwm2mthon.resources.device as DeviceResources
import lwm2mthon.resources.lwm2mserver as LWM2MResources
from lwm2mthon.coap_server_client.coap import CoAP
from lwm2mthon.utils import TreeVisit, create_description

__author__ = 'jacko'

if not os.path.isfile("logging.conf"):
    create_logging()

logger = logging.getLogger(__name__)
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)


class Client(object):
    def __init__(self, client_address, description_file):
        self.server = None
        self.server_thread = None
        self.server_address = None
        self.ep = None
        self.lifetime = None
        self.registration_id = None
        self.registration_thread = None
        self.queue = Queue()

        self.client_address = client_address
        self.description_file = description_file
        if self.description_file is None:
            self.description_file = create_description()

        self.description = self.get_description(self.description_file)

    def clear(self):
        self.server = None
        self.server_thread = None
        self.server_address = None
        self.ep = None
        self.lifetime = None
        self.registration_id = None
        self.registration_thread = None
        self.queue = Queue()

    def _wait_response(self, message):
        if message.code != coap_defines.Codes.CONTINUE.number:
            self.queue.put(message)

    def read_attributes(self):
        self.ep = self.description.get("endpointClientName", None)
        if self.ep is None or self.ep == "":
            self.ep = uuid.uuid4()
        self.lifetime = self.description.get("lifetime", None)
        if self.lifetime is None or self.lifetime == "":
            self.lifetime = 60

    def read_device(self):
        to_be_added = []
        device_description = self.description["instances"][str(ObjectId.DEVICE)]
        # self.server.add_resource(str(ObjectId.DEVICE), DeviceResources.Device())
        to_be_added.append((str(ObjectId.DEVICE), DeviceResources.Device()))
        device_instance_key = device_description.keys()[0]
        device_instance = device_description[device_instance_key]

        paths = str(ObjectId.DEVICE) + "/" + str(device_instance_key)
        device_instance_res = DeviceResources.DeviceInstance(name=str(device_instance_key), children=None,
                                                             coap_server=self.server)
        # self.server.add_resource(paths, device_instance_res)
        to_be_added.append((paths, device_instance_res))

        children = {}

        for k, v in device_instance.items():
            tmp = paths + "/" + str(k)
            res_class = getattr(DeviceResources, defines.Registry[tmp])
            if isinstance(v, dict):
                # Multiple Resource
                res = res_class(name=str(k), children=None, resource_id=str(k), coap_server=self.server)
                # self.server.add_resource(tmp, res)
                to_be_added.append((tmp, res))
                children1 = {}
                for k1, v1 in v.items():
                    tmp1 = tmp + "/" + str(k1)
                    res_class1 = getattr(DeviceResources, defines.Registry[tmp]+"Item")
                    res1 = res_class1(name=str(k1), value=v1, resource_id=str(k1), coap_server=self.server)
                    children1[k1] = res1
                    # self.server.add_resource(tmp1, res1)
                    to_be_added.append((tmp1, res1))
                res.set_children(children1)
                children[k] = res
            else:
                if hasattr(res_class, "get_value"):
                    res = res_class(name=str(k), value=v, resource_id=str(k), coap_server=self.server)
                    # self.server.add_resource(tmp, res)
                    to_be_added.append((tmp, res))
                    children[k] = res
                else:
                    res = res_class(name=str(k), resource_id=str(k), lwm2mclient=self)
                    # self.server.add_resource(tmp, res)
                    to_be_added.append((tmp, res))
                    children[k] = res

        device_instance_res.set_children(children)
        return to_be_added

    def read_lwm2mserver(self):
        to_be_added = []
        server_description = self.description["instances"][str(ObjectId.LWM2M_SERVER)]
        # self.server.add_resource(str(ObjectId.LWM2M_SERVER), LWM2MResources.LWM2MServer())
        to_be_added.append((str(ObjectId.LWM2M_SERVER), LWM2MResources.LWM2MServer()))
        for server_instance_key in server_description.keys():
            server_instance = server_description[server_instance_key]

            paths = str(ObjectId.LWM2M_SERVER) + "/" + str(server_instance_key)
            server_instance_res = LWM2MResources.LWM2MServerInstance(name=str(server_instance_key), children=None,
                                                                     coap_server=self.server)
            # self.server.add_resource(paths, server_instance_res)
            to_be_added.append((paths, server_instance_res))
            children = {}

            for k, v in server_instance.items():
                registry_id = str(ObjectId.LWM2M_SERVER) + "/X/" + str(k)
                res_class = getattr(LWM2MResources, defines.Registry[registry_id])
                tmp = paths + "/" + str(k)
                if isinstance(v, dict):
                    # Multiple Resource
                    res = res_class(name=str(k), children=None, resource_id=str(k), coap_server=self.server)
                    # self.server.add_resource(tmp, res)
                    to_be_added.append((tmp, res))
                    children1 = {}
                    for k1, v1 in v.items():
                        tmp1 = tmp + "/" + str(k1)
                        res_class1 = getattr(LWM2MResources, defines.Registry[registry_id]+"Item")
                        res1 = res_class1(name=str(k1), value=v1, resource_id=str(k1), coap_server=self.server)
                        children1[k1] = res1
                        # self.server.add_resource(tmp1, res1)
                        to_be_added.append((tmp1, res1))
                    res.set_children(children1)
                    children[k] = res
                else:
                    if hasattr(res_class, "get_value"):
                        res = res_class(name=str(k), value=v, resource_id=str(k), coap_server=self.server)
                        # self.server.add_resource(tmp, res)
                        to_be_added.append((tmp, res))
                        children[k] = res
                    else:
                        res = res_class(name=str(k), resource_id=str(k), coap_server=self.server)
                        # self.server.add_resource(tmp, res)
                        to_be_added.append((tmp, res))
                        children[k] = res

            server_instance_res.set_children(children)
        return to_be_added

    def init_resources(self):

        self.read_attributes()
        to_add = self.read_lwm2mserver()
        to_add.extend(self.read_device())

        for t in to_add:
            path, resource = t
            self.server.add_resource(path, resource)

        print self.server.root.dump()

    def add_children(self, path, children):
        if len(children) == 0:
            return
        key = children.keys()[0]
        item = children.pop(key)
        self.server.add_resource(path + "/" + key, item)
        if hasattr(item, "children"):
            self.add_children(path + "/" + key, item.children.copy())

        self.add_children(path, children)

    def _start_client_server(self):
        logger.debug("Start Client server")
        self.server = CoAP(self.client_address, self._wait_response)
        self.init_resources()
        self.server_thread = Thread(target=self.server.listen, args=(10,))
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        logger.debug("Client Server started")

    def _register(self, server_address):
        self.server_address = server_address
        request = Request()
        request.destination = self.server_address
        request.code = coap_defines.Codes.POST.number
        request.token = utils.generate_random_token(2)
        path = "/rd?ep=" + str(self.ep) + "&lt=" + str(self.lifetime)
        request.uri_path = path
        lst = []
        tree = TreeVisit.make_tree(self.server.root.dump())
        for i in tree.keys():
            if len(tree[i]) != 0:
                for s in tree[i].keys():
                    resource = self.server.root["/"+i+"/"+s]
                    if resource.visible:
                        lst.append(self.server.resourceLayer.corelinkformat(resource)[0:-1])
            else:
                resource = self.server.root[i]
                if resource.visible:
                    lst.append(self.server.resourceLayer.corelinkformat(resource)[0:-1])

        payload = '</>;rt="oma.lwm2m",'
        for r in lst:
            payload += r + ","
        payload = payload[0:-1]
        request.payload = payload
        self.server.send_message(request)
        response = self.queue.get(block=True)
        assert isinstance(response, Response)
        if response.code != coap_defines.Codes.CREATED.number:
            logger.error("Registration Error")
            return
        self.registration_id = "/" + str(response.location_path)
        logger.debug(self.registration_id)
        self.registration_thread = Thread(target=self._update_registration)
        self.registration_thread.setDaemon(True)
        self.registration_thread.start()

    def _update_registration(self):
        while True:
            time.sleep(float(self.lifetime))
            request = Request()
            request.destination = self.server_address
            request.code = coap_defines.Codes.PUT.number
            request.token = utils.generate_random_token(2)
            path = str(self.registration_id) + "?lt=" + str(self.lifetime)
            request.uri_path = path
            self.server.send_message(request)
            response = self.queue.get(block=True)
            assert isinstance(response, Response)
            if response.code != coap_defines.Codes.CHANGED.number:
                logger.error("Registration Error")
                return

    def close(self):
        logger.debug("Close Client Server")
        self.server.close()
        self.clear()

    def start(self):
        self._start_client_server()
        self._register(("127.0.0.1", 5683))

    @staticmethod
    def get_description(description_file):
        with open(description_file) as j:
            description = json.load(j)

        return description

    def reboot(self):
        t = Thread(target=self._reboot)
        t.setDaemon(True)
        t.start()

    def _reboot(self):
        time.sleep(5)
        self.description = self.get_description(self.description_file)
        self.close()
        self.start()

    def factoyreboot(self):
        t = Thread(target=self._factory_reboot)
        t.setDaemon(True)
        t.start()

    def _factory_reboot(self):
        time.sleep(5)
        self.description_file = create_description()
        self.description = self.get_description(self.description_file)
        self.close()
        self.start()
