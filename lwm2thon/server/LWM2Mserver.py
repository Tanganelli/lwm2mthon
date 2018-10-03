import json
import threading

from lwm2thon.registered_clients.client import Client
from lwm2thon.registered_clients.client_context import ClientContext
from lwm2thon.registration_interface.registration import Registration
from lwm2thon.requests.incoming_request import IncomingRequest


class LWM2MServer(object):
    def __init__(self, registry: str = "../../complete.json"):
        self._registered_clients = {}
        self._stopped = threading.Event()
        self._stopped.clear()
        self._register_thread = threading.Thread(name="register_thread", target=self._listen, daemon=True)
        self._register_thread.start()
        self._registry = None
        self._read_registry(registry)
        self._registration_object = Registration(self)

    def get_client_keys(self):
        return self._registered_clients.keys()

    def get_client(self, key: ClientContext):
        return self._registered_clients.get(key, None)

    def add_client(self, key: ClientContext, client: Client):
        self._registered_clients[key] = client

    def remove_client(self, key: ClientContext):
        del self._registered_clients[key]

    def _listen(self):
        # TODO start server for incoming registrations

        while not self._stopped.is_set():
            ip, port, queries, payload = IncomingRequest()
            client_context = ClientContext()
            client_context.address = (ip, port)
            if client_context not in self._registered_clients:
                # New registration
                req_request = self._registration_object.registration(client_context,queries,payload)

    def _read_registry(self, registry):
        with open(registry) as f:
            self._registry = json.load(f)

server = LWM2MServer()






