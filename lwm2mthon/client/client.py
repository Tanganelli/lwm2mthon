import json
from multiprocessing import Queue
from coapthon import utils
from coapthon.messages.request import Request
import os
from threading import Thread
import uuid
from coapthon.messages.response import Response
from coapthon.server.coap import logging
from coapthon.utils import create_logging
import coapthon.defines as coap_defines
from lwm2mthon import defines
from lwm2mthon.defines import LWM2MInstance, ObjectId, DeviceIds, InstanceItem, LWM2MResource, ResourceItem, \
    LWM2MInstanceType, LWM2MResourceType, LWM2MOperations
import lwm2mthon.resources.device as DeviceResources
import lwm2mthon.resources.lwm2mserver as LWM2MResources
from lwm2mthon.coap_server_client.coap import CoAP
__author__ = 'jacko'

if not os.path.isfile("logging.conf"):
    create_logging()

logger = logging.getLogger(__name__)
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)


class Client(object):
    def __init__(self, client_address, description_file, resources_file):
        self.server = None
        self.server_thread = None
        self.server_address = None
        self.client_address = client_address
        self.description_file = description_file
        self.description = self.get_description(description_file)
        self.resources_file = resources_file
        self.queue = Queue()

    def _wait_response(self, message):
        if message.code != coap_defines.Codes.CONTINUE.number:
            self.queue.put(message)

    def read_device(self):
        device_description = self.description["instances"][str(ObjectId.DEVICE)]
        self.server.add_resource(str(ObjectId.DEVICE), DeviceResources.Device())
        device_instance_key = device_description.keys()[0]
        device_instance = device_description[device_instance_key]

        paths = str(ObjectId.DEVICE) + "/" + str(device_instance_key)
        device_instance_res = DeviceResources.DeviceInstance(name=str(device_instance_key), children=None,
                                                             coap_server=self.server)
        self.server.add_resource(paths, device_instance_res)

        children = {}

        for k, v in device_instance.items():
            tmp = paths + "/" + str(k)
            res_class = getattr(DeviceResources, defines.Registry[tmp])
            if isinstance(v, dict):
                # Multiple Resource
                res = res_class(name=str(k), children=None, resource_id=str(k), coap_server=self.server)
                self.server.add_resource(tmp, res)
                children1 = {}
                for k1, v1 in v.items():
                    tmp1 = tmp + "/" + str(k1)
                    res_class1 = getattr(DeviceResources, defines.Registry[tmp]+"Item")
                    res1 = res_class1(name=str(k1), value=v1, resource_id=str(k1), coap_server=self.server)
                    children1[k1] = res1
                    self.server.add_resource(tmp1, res1)
                res.set_children(children1)
                children[k] = res
            else:
                if hasattr(res_class, "get_value"):
                    res = res_class(name=str(k), value=v, resource_id=str(k), coap_server=self.server)
                    self.server.add_resource(tmp, res)
                    children[k] = res
                else:
                    res = res_class(name=str(k), resource_id=str(k), coap_server=self.server)
                    self.server.add_resource(tmp, res)
                    children[k] = res

        device_instance_res.set_children(children)

    def read_lwm2mserver(self):
        server_description = self.description["instances"][str(ObjectId.LWM2M_SERVER)]
        self.server.add_resource(str(ObjectId.LWM2M_SERVER), LWM2MResources.LWM2MServer())
        for server_instance_key in server_description.keys():
            server_instance = server_description[server_instance_key]

            paths = str(ObjectId.LWM2M_SERVER) + "/" + str(server_instance_key)
            server_instance_res = LWM2MResources.LWM2MServerInstance(name=str(server_instance_key), children=None,
                                                                     coap_server=self.server)
            self.server.add_resource(paths, server_instance_res)

            children = {}

            for k, v in server_instance.items():
                registry_id = str(ObjectId.LWM2M_SERVER) + "/X/" + str(k)
                res_class = getattr(LWM2MResources, defines.Registry[registry_id])
                tmp = paths + "/" + str(k)
                if isinstance(v, dict):
                    # Multiple Resource
                    res = res_class(name=str(k), children=None, resource_id=str(k), coap_server=self.server)
                    self.server.add_resource(tmp, res)
                    children1 = {}
                    for k1, v1 in v.items():
                        tmp1 = tmp + "/" + str(k1)
                        res_class1 = getattr(LWM2MResources, defines.Registry[registry_id]+"Item")
                        res1 = res_class1(name=str(k1), value=v1, resource_id=str(k1), coap_server=self.server)
                        children1[k1] = res1
                        self.server.add_resource(tmp1, res1)
                    res.set_children(children1)
                    children[k] = res
                else:
                    if hasattr(res_class, "get_value"):
                        res = res_class(name=str(k), value=v, resource_id=str(k), coap_server=self.server)
                        self.server.add_resource(tmp, res)
                        children[k] = res
                    else:
                        res = res_class(name=str(k), resource_id=str(k), coap_server=self.server)
                        self.server.add_resource(tmp, res)
                        children[k] = res

            server_instance_res.set_children(children)

    def init_resources(self, resources_file):
        # with open(resources_file) as f:
        #     resources = json.load(f)
        #
        # tree = {}
        # for obj in resources:
        #     assert isinstance(obj, dict)
        #     name = obj.get(LWM2MInstance.NAME)
        #     instancetype = obj.get(LWM2MInstance.INSTANCE_TYPE)
        #     mandatory = obj.get(LWM2MInstance.MANDATORY)
        #     description = obj.get(LWM2MInstance.DESCRIPTION)
        #     instance_id = obj.get(LWM2MInstance.ID)
        #     tree[instance_id] = InstanceItem(instance_id=instance_id, name=name, instancetype=instancetype,
        #                                      mandatory=mandatory, description=description)
        #     resourcedefs = obj.get(LWM2MInstance.RESOURCEDEFS)
        #     for r in resourcedefs:
        #         res_operations = r.get(LWM2MResource.OPERATIONS)
        #         res_mandatory = r.get(LWM2MResource.MANDATORY)
        #         res_name = r.get(LWM2MResource.NAME)
        #         res_id = r.get(LWM2MResource.ID)
        #         res_range = r.get(LWM2MResource.RANGE)
        #         res_units = r.get(LWM2MResource.UNITS)
        #         res_type = r.get(LWM2MResource.TYPE)
        #         res_instancetype = r.get(LWM2MResource.INSTANCE_TYPE)
        #         res_description = r.get(LWM2MResource.DESCRIPTION)
        #         res = ResourceItem(operations=res_operations, name=res_name, resource_id=res_id,
        #                            mandatory=res_mandatory, resource_range=res_range, units=res_units,
        #                            resource_type=res_type, instancetype=res_instancetype, description=res_description)
        #         tree[instance_id].add_resourcedef(res_id, res)
        self.read_lwm2mserver()
        self.read_device()

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
        self.init_resources(self.resources_file)
        self.server_thread = Thread(target=self.server.listen, args=(10,))
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        # self.server.listen(10)
        logger.debug("Client Server started")

    def _register(self, server_address):
        self.server_address = server_address
        request = Request()
        request.destination = self.server_address
        request.code = coap_defines.Codes.POST.number
        request.token = utils.generate_random_token(2)
        ep = uuid.uuid4()
        path = "/rd?ep=" + str(ep)
        request.uri_path = path
        request.payload = '</>;rt="oma.lwm2m",</3/0>,</1/1>'
        self.server.send_message(request)
        response = self.queue.get(block=True)
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

    def get_description(self, description_file):
        with open(description_file) as j:
            self.description = json.load(j)

        return self.description
