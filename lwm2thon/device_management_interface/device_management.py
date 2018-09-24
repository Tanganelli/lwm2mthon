from enum import Enum
from typing import Union, Any

from lwm2thon.objects.LWM2Mobject import LWM2MObject, LWM2MObjectInstance, LWM2MResource, LWM2MResourceInstance
from lwm2thon.registered_clients.client_context import ClientContext
from lwm2thon.server.LWM2Mserver import LWM2MServer


class DeviceManagementResponse(Enum):
    OK = 0
    CLIENT_NOT_AVAILABLE = 1
    OBJECT_NOT_AVAILABLE = 2
    RESOURCE_ID_NOT_NONE = 3
    RESOURCE_INSTANCE_ID_NOT_NONE = 4
    INSTANCE_NOT_AVAILABLE = 5
    RESOURCE_NOT_AVAILABLE = 6
    RESOURCE_INSTANCE_NOT_AVAILABLE = 7


class DeviceManagement(object):
    def __init__(self, server: LWM2MServer):
        self._server = server

    def read(self, client_context: ClientContext, object_id: LWM2MObject,
             object_instance_id: LWM2MObjectInstance = None, resource_id: LWM2MResource = None,
             resource_instance_id: LWM2MResourceInstance = None) -> Union[DeviceManagementResponse, Any]:
        # TODO change Any to Value
        client = self._server.get_client(client_context)
        if client is None:
            return DeviceManagementResponse.CLIENT_NOT_AVAILABLE

        obj = client.get_object(object_id.id)
        instance = None
        resource = None
        resource_instance = None
        if obj is None:
            return DeviceManagementResponse.OBJECT_NOT_AVAILABLE
        if object_instance_id is not None:
            instance = obj.get_instance(object_instance_id.id)
            if instance is None:
                return DeviceManagementResponse.INSTANCE_NOT_AVAILABLE
            if resource_id is not None:
                resource = instance.get_resource(resource_id.id)
                if resource is None:
                    return DeviceManagementResponse.RESOURCE_NOT_AVAILABLE
                if not resource.multiple_instance and resource_instance_id is not None:
                    return DeviceManagementResponse.RESOURCE_INSTANCE_ID_NOT_NONE
                if resource.multiple_instance and resource_instance_id is not None:
                    resource_instance = resource.get_resource_instance(resource_instance_id.id)
                    if resource_instance is None:
                        return DeviceManagementResponse.RESOURCE_INSTANCE_NOT_AVAILABLE
            elif resource_instance_id is not None:
                return DeviceManagementResponse.RESOURCE_INSTANCE_ID_NOT_NONE
        elif resource_id is not None:
            return DeviceManagementResponse.RESOURCE_ID_NOT_NONE
        elif resource_instance_id is not None:
            return DeviceManagementResponse.RESOURCE_INSTANCE_ID_NOT_NONE

        uri = "/" + obj.id
        if instance is not None:
            uri += "/" + instance.id
        if resource_id is not None:
            uri += "/" + resource.id
        if resource_instance.id is not None:
            uri += "/" + resource_instance.id

        # TODO call the coap client to retrieve the resource
        # TODO check and update value with object, instance, resource or resource_instance
        response = ""

        return DeviceManagementResponse.OK

    def discover(self, client_context: ClientContext, object_id: LWM2MObject,
                 object_instance_id: LWM2MObjectInstance = None,
                 resource_id: LWM2MResource = None) -> Union[DeviceManagementResponse, str]:
        client = self._server.get_client(client_context)
        if client is None:
            return DeviceManagementResponse.CLIENT_NOT_AVAILABLE

        obj = client.get_object(object_id.id)
        instance = None
        resource = None
        if obj is None:
            return DeviceManagementResponse.OBJECT_NOT_AVAILABLE
        if object_instance_id is not None:
            instance = obj.get_instance(object_instance_id.id)
            if instance is None:
                return DeviceManagementResponse.INSTANCE_NOT_AVAILABLE
            if resource_id is not None:
                resource = instance.get_resource(resource_id.id)
                if resource is None:
                    return DeviceManagementResponse.RESOURCE_NOT_AVAILABLE
        elif resource_id is not None:
            return DeviceManagementResponse.RESOURCE_ID_NOT_NONE

        uri = "/" + obj.id
        if instance is not None:
            uri += "/" + instance.id
        if resource_id is not None:
            uri += "/" + resource.id

        # TODO call the coap client to discover resources
        # TODO update attributes and objects, instances, resources or resource_instances

        response = ""
        return DeviceManagementResponse.OK

    def write(self, client_context: ClientContext, object_id: LWM2MObject,
              object_instance_id: LWM2MObjectInstance, new_value, resource_id: LWM2MResource = None,
              resource_instance_id: LWM2MResourceInstance = None) -> DeviceManagementResponse:
        client = self._server.get_client(client_context)
        if client is None:
            return DeviceManagementResponse.CLIENT_NOT_AVAILABLE
        obj = client.get_object(object_id.id)

        if obj is None:
            return DeviceManagementResponse.OBJECT_NOT_AVAILABLE

        instance = obj.get_instance(object_instance_id.id)
        if instance is None:
            return DeviceManagementResponse.INSTANCE_NOT_AVAILABLE

        resource = None
        resource_instance = None
        if resource_id is not None:
            resource = instance.get_resource(resource_id.id)
            if resource is None:
                return DeviceManagementResponse.RESOURCE_NOT_AVAILABLE
            if not resource.multiple_instance and resource_instance_id is not None:
                return DeviceManagementResponse.RESOURCE_INSTANCE_ID_NOT_NONE
            if resource.multiple_instance and resource_instance_id is not None:
                resource_instance = resource.get_resource_instance(resource_instance_id.id)
                if resource_instance is None:
                    return DeviceManagementResponse.RESOURCE_INSTANCE_NOT_AVAILABLE
        elif resource_instance_id is not None:
            return DeviceManagementResponse.RESOURCE_INSTANCE_ID_NOT_NONE

        uri = "/" + obj.id + "/" + instance.id

        if resource_id is not None:
            uri += "/" + resource.id
        if resource_instance.id is not None:
            uri += "/" + resource_instance.id

        # TODO validate new value
        # TODO call the coap client to write the new value
        response = ""
        return DeviceManagementResponse.OK

    def write_attributes(self, client_context: ClientContext, object_id: LWM2MObject, new_attribute,
                         object_instance_id: LWM2MObjectInstance = None, resource_id: LWM2MResource = None,
                         resource_instance_id: LWM2MResourceInstance = None) -> DeviceManagementResponse:
        client = self._server.get_client(client_context)
        if client is None:
            return DeviceManagementResponse.CLIENT_NOT_AVAILABLE

        obj = client.get_object(object_id.id)
        instance = None
        resource = None
        resource_instance = None
        if obj is None:
            return DeviceManagementResponse.OBJECT_NOT_AVAILABLE
        if object_instance_id is not None:
            instance = obj.get_instance(object_instance_id.id)
            if instance is None:
                return DeviceManagementResponse.INSTANCE_NOT_AVAILABLE
            if resource_id is not None:
                resource = instance.get_resource(resource_id.id)
                if resource is None:
                    return DeviceManagementResponse.RESOURCE_NOT_AVAILABLE
                if not resource.multiple_instance and resource_instance_id is not None:
                    return DeviceManagementResponse.RESOURCE_INSTANCE_ID_NOT_NONE
                if resource.multiple_instance and resource_instance_id is not None:
                    resource_instance = resource.get_resource_instance(resource_instance_id.id)
                    if resource_instance is None:
                        return DeviceManagementResponse.RESOURCE_INSTANCE_NOT_AVAILABLE
            elif resource_instance_id is not None:
                return DeviceManagementResponse.RESOURCE_INSTANCE_ID_NOT_NONE
        elif resource_id is not None:
            return DeviceManagementResponse.RESOURCE_ID_NOT_NONE
        elif resource_instance_id is not None:
            return DeviceManagementResponse.RESOURCE_INSTANCE_ID_NOT_NONE

        uri = "/" + obj.id
        if instance is not None:
            uri += "/" + instance.id
        if resource_id is not None:
            uri += "/" + resource.id
        if resource_instance.id is not None:
            uri += "/" + resource_instance.id
        # TODO validate new attribute
        # TODO call the coap client to write the new attribute
        response = ""
        return DeviceManagementResponse.OK

    def execute(self, client_context: ClientContext, object_id: LWM2MObject,
                object_instance_id: LWM2MObjectInstance, resource_id: LWM2MResource,
                arguments: str = None) -> DeviceManagementResponse:

        client = self._server.get_client(client_context)
        if client is None:
            return DeviceManagementResponse.CLIENT_NOT_AVAILABLE

        obj = client.get_object(object_id.id)
        if obj is None:
            return DeviceManagementResponse.OBJECT_NOT_AVAILABLE
        instance = obj.get_instance(object_instance_id.id)
        if instance is None:
            return DeviceManagementResponse.INSTANCE_NOT_AVAILABLE
        resource = instance.get_resource(resource_id.id)
        if resource is None:
            return DeviceManagementResponse.RESOURCE_NOT_AVAILABLE

        uri = "/" + obj.id + "/" + instance.id + "/" + resource.id

        # TODO call the coap client to execute
        response = ""
        return DeviceManagementResponse.OK

    def create(self, client_context: ClientContext, object_id: LWM2MObject,
               new_value) -> DeviceManagementResponse:
        client = self._server.get_client(client_context)
        if client is None:
            return DeviceManagementResponse.CLIENT_NOT_AVAILABLE
        obj = client.get_object(object_id.id)
        if obj is None:
            return DeviceManagementResponse.OBJECT_NOT_AVAILABLE
        uri = "/" + obj.id
        # TODO validate new_value
        # TODO call the coap client to create new object instance
        response = ""
        return DeviceManagementResponse.OK

    def delete(self, client_context: ClientContext, object_id: LWM2MObject,
               object_instance_id: LWM2MObjectInstance) -> DeviceManagementResponse:
        client = self._server.get_client(client_context)
        if client is None:
            return DeviceManagementResponse.CLIENT_NOT_AVAILABLE
        obj = client.get_object(object_id.id)
        if obj is None:
            return DeviceManagementResponse.OBJECT_NOT_AVAILABLE
        instance = obj.get_instance(object_instance_id.id)
        if instance is None:
            return DeviceManagementResponse.INSTANCE_NOT_AVAILABLE

        uri = "/" + obj.id + "/" + instance.id
        # TODO call the coap client delete object instance
        response = ""
        return DeviceManagementResponse.OK

    # TODO Read-composite

    # TODO Write-composite

    # TODO send

