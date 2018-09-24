from enum import Enum
from typing import List

from lwm2thon.registered_clients.client import Client
from lwm2thon.registered_clients.client_context import ClientContext, Binding
from lwm2thon.server.LWM2Mserver import LWM2MServer
from lwm2thon.utils.core_link_format import CoReLinkFormat


class RegistrationResponse(Enum):
    OK = 0
    ALREADY_REGISTERED = 1
    SECURITY_NOT_MATCH = 2
    NOT_REGISTERED = 3


class Registration(object):
    def __init__(self, server: LWM2MServer):
        self._server = server

    def registration(self, client_context: ClientContext, endpoint_client_name: str, lifetime: int,
                     lwm2m_version: float, objects: str, binding_mode: List[Binding] = Binding.U,
                     queue_mode: bool = None, sms_number: str = None) -> RegistrationResponse:

        resources = CoReLinkFormat.parse(objects)
        client = Client(endpoint_client_name, lifetime, lwm2m_version, resources, binding_mode, queue_mode, sms_number)
        lst = self._server.get_client_keys()
        if endpoint_client_name not in lst:
            if self.match_security(endpoint_client_name):
                self._server.add_client(client_context, client)
                return RegistrationResponse.OK
            return RegistrationResponse.SECURITY_NOT_MATCH
        return RegistrationResponse.ALREADY_REGISTERED

    def update(self, client_context: ClientContext, lifetime: int=None, binding_mode: List[Binding]=None,
               sms_number: str=None, objects: str=None) -> RegistrationResponse:
        client = self._server.get_client(client_context)
        if client is not None:
            assert isinstance(client, Client)
            if objects is not None:
                resources = CoReLinkFormat.parse(objects)
            else:
                resources = None
            client.update(lifetime, binding_mode, sms_number, resources)
            return RegistrationResponse.OK
        return RegistrationResponse.NOT_REGISTERED

    def de_register(self, client_context: ClientContext) -> RegistrationResponse:
        client = self._server.get_client(client_context)
        if client is not None:
            assert isinstance(client, Client)
            client.de_register()
            self._server.remove_client(client_context)
            return RegistrationResponse.OK
        return RegistrationResponse.NOT_REGISTERED

    def match_security(self, endpoint_client_name: str) -> bool:
        return True
