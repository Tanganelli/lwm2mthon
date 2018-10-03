from enum import Enum
from typing import Union, Any

from lwm2thon.objects.LWM2Mobjects import LWM2MObject, LWM2MObjectInstance, LWM2MResource, LWM2MResourceInstance
from lwm2thon.registered_clients.client_context import ClientContext
from lwm2thon.server.LWM2Mserver import LWM2MServer


class InformationReportingResponse(Enum):
    OK = 0
    CLIENT_NOT_AVAILABLE = 1
    OBJECT_NOT_AVAILABLE = 2
    RESOURCE_ID_NOT_NONE = 3
    RESOURCE_INSTANCE_ID_NOT_NONE = 4
    INSTANCE_NOT_AVAILABLE = 5
    RESOURCE_NOT_AVAILABLE = 6
    RESOURCE_INSTANCE_NOT_AVAILABLE = 7


class InformationReporting(object):
    def __init__(self, server: LWM2MServer):
        self._server = server

    def observe(self, client_context: ClientContext, object_id: LWM2MObject,
             object_instance_id: LWM2MObjectInstance = None, resource_id: LWM2MResource = None,
             resource_instance_id: LWM2MResourceInstance = None) -> Union[InformationReportingResponse, Any]:
        # TODO change Any to Value
        client = self._server.get_client(client_context)
        if client is None:
            return InformationReportingResponse.CLIENT_NOT_AVAILABLE

        obj = client.get_object(object_id.id)
        instance = None
        resource = None
        resource_instance = None
        if obj is None:
            return InformationReportingResponse.OBJECT_NOT_AVAILABLE
        if object_instance_id is not None:
            instance = obj.get_instance(object_instance_id.id)
            if instance is None:
                return InformationReportingResponse.INSTANCE_NOT_AVAILABLE
            if resource_id is not None:
                resource = instance.get_resource(resource_id.id)
                if resource is None:
                    return InformationReportingResponse.RESOURCE_NOT_AVAILABLE
                if not resource.multiple_instance and resource_instance_id is not None:
                    return InformationReportingResponse.RESOURCE_INSTANCE_ID_NOT_NONE
                if resource.multiple_instance and resource_instance_id is not None:
                    resource_instance = resource.get_resource_instance(resource_instance_id.id)
                    if resource_instance is None:
                        return InformationReportingResponse.RESOURCE_INSTANCE_NOT_AVAILABLE
            elif resource_instance_id is not None:
                return InformationReportingResponse.RESOURCE_INSTANCE_ID_NOT_NONE
        elif resource_id is not None:
            return InformationReportingResponse.RESOURCE_ID_NOT_NONE
        elif resource_instance_id is not None:
            return InformationReportingResponse.RESOURCE_INSTANCE_ID_NOT_NONE

        uri = "/" + obj.id
        if instance is not None:
            uri += "/" + instance.id
        if resource_id is not None:
            uri += "/" + resource.id
        if resource_instance.id is not None:
            uri += "/" + resource_instance.id

        # TODO call the coap client to retrieve the resource
        # TODO Add client to list of observer and remember token
        # TODO check and update value with object, instance, resource or resource_instance
        response = ""

        return InformationReportingResponse.OK

    def notify(self, client_context: ClientContext, new_value) -> InformationReportingResponse:
        client = self._server.get_client(client_context)
        if client is None:
            return InformationReportingResponse.CLIENT_NOT_AVAILABLE
        # TODO find uri depending on received token
        # TODO check and update value with object, instance, resource or resource_instance
        response = ""

        return InformationReportingResponse.OK

    def cancel_observe(self, client_context: ClientContext, object_id: LWM2MObject,
                       object_instance_id: LWM2MObjectInstance = None, resource_id: LWM2MResource = None,
                       resource_instance_id: LWM2MResourceInstance = None) -> InformationReportingResponse:
        client = self._server.get_client(client_context)
        if client is None:
            return InformationReportingResponse.CLIENT_NOT_AVAILABLE

        obj = client.get_object(object_id.id)
        instance = None
        resource = None
        resource_instance = None
        if obj is None:
            return InformationReportingResponse.OBJECT_NOT_AVAILABLE
        if object_instance_id is not None:
            instance = obj.get_instance(object_instance_id.id)
            if instance is None:
                return InformationReportingResponse.INSTANCE_NOT_AVAILABLE
            if resource_id is not None:
                resource = instance.get_resource(resource_id.id)
                if resource is None:
                    return InformationReportingResponse.RESOURCE_NOT_AVAILABLE
                if not resource.multiple_instance and resource_instance_id is not None:
                    return InformationReportingResponse.RESOURCE_INSTANCE_ID_NOT_NONE
                if resource.multiple_instance and resource_instance_id is not None:
                    resource_instance = resource.get_resource_instance(resource_instance_id.id)
                    if resource_instance is None:
                        return InformationReportingResponse.RESOURCE_INSTANCE_NOT_AVAILABLE
            elif resource_instance_id is not None:
                return InformationReportingResponse.RESOURCE_INSTANCE_ID_NOT_NONE
        elif resource_id is not None:
            return InformationReportingResponse.RESOURCE_ID_NOT_NONE
        elif resource_instance_id is not None:
            return InformationReportingResponse.RESOURCE_INSTANCE_ID_NOT_NONE

        uri = "/" + obj.id
        if instance is not None:
            uri += "/" + instance.id
        if resource_id is not None:
            uri += "/" + resource.id
        if resource_instance.id is not None:
            uri += "/" + resource_instance.id

        # TODO call the coap client to cancel observing
        # TODO Delete client from list of observers
        response = ""

        return InformationReportingResponse.OK

    # TODO Observe-composite

    # TODO cancel-observation-composite
