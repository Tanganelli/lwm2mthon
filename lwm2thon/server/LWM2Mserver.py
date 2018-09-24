from lwm2thon.registered_clients.client import Client
from lwm2thon.registered_clients.client_context import ClientContext


class LWM2MServer(object):
    def __init__(self):
        self._registered_clients = {}

    def get_client_keys(self):
        return self._registered_clients.keys()

    def get_client(self, key: ClientContext):
        return self._registered_clients.get(key, None)

    def add_client(self, key: ClientContext, client: Client):
        self._registered_clients[key] = client

    def remove_client(self, key: ClientContext):
        del self._registered_clients[key]