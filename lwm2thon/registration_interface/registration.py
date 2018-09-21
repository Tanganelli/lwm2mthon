from enum import Enum
from typing import List

from lwm2thon.registered_clients.client import Client
from lwm2thon.registered_clients.client_context import ClientContext, Binding


class RegistrationResponse(Enum):
    OK = 0
    ALREADY_REGISTERED = 1
    SECURITY_NOT_MATCH = 2
    NOT_REGISTERED = 3


class Registration(object):
    def __init__(self):
        self._registered_clients = {}

    def registration(self, client_context: ClientContext, endpoint_client_name: str, lifetime: int,
                     lwm2m_version: float, objects, binding_mode: List[Binding] = Binding.U,
                     queue_mode: bool = None, sms_number: str = None) -> RegistrationResponse:
        client = Client(endpoint_client_name, lifetime, lwm2m_version, objects, binding_mode, queue_mode, sms_number)
        if endpoint_client_name not in self._registered_clients.keys():
            if self.match_security(endpoint_client_name):
                self._registered_clients[client_context] = client
                return RegistrationResponse.OK
            return RegistrationResponse.SECURITY_NOT_MATCH
        return RegistrationResponse.ALREADY_REGISTERED

    def update(self, client_context: ClientContext, lifetime: int=None, binding_mode: List[Binding]=None,
               sms_number: str=None, objects=None) -> RegistrationResponse:
        client = self._registered_clients.get(client_context, None)
        if client is not None:
            assert isinstance(client, Client)
            client.update(lifetime, binding_mode, sms_number, objects)
            return RegistrationResponse.OK
        return RegistrationResponse.NOT_REGISTERED

    def de_register(self, client_context: ClientContext) -> RegistrationResponse:
        client = self._registered_clients.get(client_context, None)
        if client is not None:
            assert isinstance(client, Client)
            client.de_register()
            del self._registered_clients[client_context]
            return RegistrationResponse.OK
        return RegistrationResponse.NOT_REGISTERED

    def match_security(self, endpoint_client_name: str) -> bool:
        return True
