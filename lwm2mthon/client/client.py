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
from lwm2mthon.defines import LWM2MInstance, ObjectId, DeviceIds, InstanceItem, LWM2MResource, ResourceItem, \
    LWM2MInstanceType, LWM2MResourceType, LWM2MOperations
import lwm2mthon.resources.device as DeviceResources
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

    def init_resources(self, resources_file):
        with open(resources_file) as f:
            resources = json.load(f)

        tree = {}
        for obj in resources:
            assert isinstance(obj, dict)
            name = obj.get(LWM2MInstance.NAME)
            instancetype = obj.get(LWM2MInstance.INSTANCE_TYPE)
            mandatory = obj.get(LWM2MInstance.MANDATORY)
            description = obj.get(LWM2MInstance.DESCRIPTION)
            instance_id = obj.get(LWM2MInstance.ID)
            tree[instance_id] = InstanceItem(instance_id=instance_id, name=name, instancetype=instancetype,
                                             mandatory=mandatory, description=description)
            resourcedefs = obj.get(LWM2MInstance.RESOURCEDEFS)
            for r in resourcedefs:
                res_operations = r.get(LWM2MResource.OPERATIONS)
                res_mandatory = r.get(LWM2MResource.MANDATORY)
                res_name = r.get(LWM2MResource.NAME)
                res_id = r.get(LWM2MResource.ID)
                res_range = r.get(LWM2MResource.RANGE)
                res_units = r.get(LWM2MResource.UNITS)
                res_type = r.get(LWM2MResource.TYPE)
                res_instancetype = r.get(LWM2MResource.INSTANCE_TYPE)
                res_description = r.get(LWM2MResource.DESCRIPTION)
                res = ResourceItem(operations=res_operations, name=res_name, resource_id=res_id,
                                   mandatory=res_mandatory, resource_range=res_range, units=res_units,
                                   resource_type=res_type, instancetype=res_instancetype, description=res_description)
                tree[instance_id].add_resourcedef(res_id, res)

        device_description = self.description["instances"][str(ObjectId.DEVICE)]
        self.server.add_resource(str(ObjectId.DEVICE), DeviceResources.Device())
        device_instance_key = device_description.keys()[0]
        device_instance = device_description[device_instance_key]
        children = {}
        for k, v in device_instance.items():
            children1 = {}
            res_item = tree[ObjectId.DEVICE].get_resourcedef(int(k))
            assert isinstance(res_item, ResourceItem)
            new_res = ""
            if res_item.instancetype == LWM2MInstanceType.SINGLE:
                new_res += "Single"
            elif res_item.instancetype == LWM2MInstanceType.MULTIPLE:
                new_res += "Multiple"

                children1 = {}
                for k1, v1 in v.items():
                    new_res1 = "Single"
                    if res_item.operations == LWM2MOperations.READ:
                        new_res1 += "Read"
                    elif res_item.operations == LWM2MOperations.WRITE:
                        new_res1 += "Write"
                    elif res_item.operations == LWM2MOperations.READWRITE:
                        new_res1 += "ReadWrite"
                    elif res_item.operations == LWM2MOperations.EXECUTE:
                        new_res1 += "Execute"
                    else:
                        raise AttributeError("Unknown Operation: " + res_item.operations)
                    if res_item.resource_type == LWM2MResourceType.STRING:
                        new_res1 += "String"
                    elif res_item.resource_type == LWM2MResourceType.INTEGER:
                        new_res1 += "Integer"
                    elif res_item.resource_type == LWM2MResourceType.TIME:
                        new_res1 += "Time"
                    else:
                        raise AttributeError("Unknown Resource Type: " + res_item.resource_type)
                    new_item1 = getattr(DeviceResources, new_res1)
                    children1[k1] = new_item1(name=res_item.name, value=v1)
            else:
                raise AttributeError("Unknown InstanceType: " + res_item.instancetype)

            if res_item.operations == LWM2MOperations.READ:
                new_res += "Read"
            elif res_item.operations == LWM2MOperations.WRITE:
                new_res += "Write"
            elif res_item.operations == LWM2MOperations.READWRITE:
                new_res += "ReadWrite"
            elif res_item.operations == LWM2MOperations.EXECUTE:
                new_res += "Execute"
            else:
                raise AttributeError("Unknown Operation: " + res_item.operations)

            if res_item.resource_type == LWM2MResourceType.STRING:
                new_res += "String"
            elif res_item.resource_type == LWM2MResourceType.INTEGER:
                new_res += "Integer"
            elif res_item.resource_type == LWM2MResourceType.TIME:
                new_res += "Time"
            else:
                raise AttributeError("Unknown Resource Type: " + res_item.resource_type)

            new_item = getattr(DeviceResources, new_res)
            if len(children1) > 0:
                children[k] = new_item(name=res_item.name, children=children1)
            else:
                children[k] = new_item(name=res_item.name, value=v)
            # print k, v
            # print tree[ObjectId.DEVICE].get_resourcedef(int(k)).name
        self.server.add_resource(str(ObjectId.DEVICE) + "/" + device_instance_key,
                                 DeviceResources.DeviceInstance(name=str(device_instance_key), children=children))
        path = str(ObjectId.DEVICE) + "/" + device_instance_key
        self.add_children(path, children)

    def add_children(self, path, children):
        if len(children) == 0:
            return
        key = children.keys()[0]
        item = children.pop(key)
        self.server.add_resource(path + "/" + key, item)
        if hasattr(item, "children"):
            self.add_children(path + "/" + key, item.children)

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
        request.payload = '</>;rt="oma.lwm2m", </3/0>'
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