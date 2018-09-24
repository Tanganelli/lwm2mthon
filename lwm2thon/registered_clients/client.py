import datetime
from typing import List, Dict

from lwm2thon.objects.LWM2Mobject import LWM2MObject
from lwm2thon.registered_clients.client_context import Binding


class Client(object):
    def __init__(self, endpoint_client_name: str, lifetime: int, lwm2m_version: float, objects: Dict[str, LWM2MObject],
                 binding_mode: List[Binding] = Binding.U, queue_mode: bool = None, sms_number: str = None):
        if endpoint_client_name is not None:
            self._endpoint_client_name = str(endpoint_client_name)
        self._lifetime = int(lifetime)
        self._lwm2m_version = float(lwm2m_version)
        if isinstance(binding_mode, list):
            self._binding_mode = binding_mode
        elif isinstance(binding_mode, Binding):
            self._binding_mode = [binding_mode]
        if queue_mode is not None:
            self._queue_mode = bool(queue_mode)
        if sms_number is not None:
            self._sms_number = str(sms_number)
        self._objects = objects
        self._timestamp = datetime.datetime.now().timestamp()
        self._registered = True

    def update(self, lifetime: int=None, binding_mode: List[Binding]=None, sms_number: str=None,
               objects: Dict[str, LWM2MObject]=None):
        if lifetime is not None:
            self._lifetime = int(lifetime)
        if binding_mode is not None:
            if isinstance(binding_mode, list):
                self._binding_mode = binding_mode
            elif isinstance(binding_mode, Binding):
                self._binding_mode = [binding_mode]
        if sms_number is not None:
            self._sms_number = str(sms_number)
        if objects is not None:
            self._objects = objects
        self._timestamp = datetime.datetime.now().timestamp()

    def de_register(self) -> bool:
        self._registered = False
        return True

    def get_object(self, uri: str) -> LWM2MObject:
        return self._objects.get(uri, None)

