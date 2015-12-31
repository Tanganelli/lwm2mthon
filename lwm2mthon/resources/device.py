from datetime import date, datetime
from coapthon.resources.resource import Resource
import time
from lwm2mthon import defines
from lwm2mthon.defines import LWM2MResourceType
from lwm2mthon.utils import TreeVisit

__author__ = 'giacomo'


class Device(Resource):
    def __init__(self, name="3"):
        super(Device, self).__init__(name)


class DeviceInstance(Resource):

    def __init__(self, name, children, coap_server):
        super(DeviceInstance, self).__init__(name, coap_server=coap_server)
        self.children = children

    def set_children(self, children):
        self.children = children

    def render_DELETE(self, request):
        return True

    def render_PUT(self, request):
        ret = TreeVisit.decode(request.payload, request.uri_path, request.content_type)

        for r in ret:
            c = str(r[1])  # identifier
            v = r[2]
            assert isinstance(self.children[c], Resource)
            method = getattr(self.children[c], 'set_value', None)
            if method is not None:
                self.children[c].set_value(v)
        return self

    def render_GET(self, request):
        # Object Instance
        resources = TreeVisit.get_children(self.children)
        # encode as TLV
        self.payload = TreeVisit.encode(resources, request.uri_path,
                                        defines.Content_types["application/vnd.oma.lwm2m+tlv"])
        return self


class Manufacturer(Resource):

    def __init__(self, name="0", value="", resource_id="0", coap_server=None):
        super(Manufacturer, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class ModelNumber(Resource):

    def __init__(self, name="1", value="", resource_id="1", coap_server=None):
        super(ModelNumber, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class SerialNumber(Resource):

    def __init__(self, name="2", value="", resource_id="2", coap_server=None):
        super(SerialNumber, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class FirmwareVersion(Resource):

    def __init__(self, name="3", value="", resource_id="3", coap_server=None):
        super(FirmwareVersion, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class Reboot(Resource):

    def __init__(self, name="4", resource_id="4", lwm2mclient=None):
        super(Reboot, self).__init__(name)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING
        self.lwm2mclient = lwm2mclient

    def render_POST(self, request):
        self.lwm2mclient.reboot()
        return self


class FactoryReboot(Resource):

    def __init__(self, name="5", resource_id="5", lwm2mclient=None):
        super(FactoryReboot, self).__init__(name)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING
        self.lwm2mclient = lwm2mclient

    def render_POST(self, request):
        self.lwm2mclient.factoryreboot()
        return self


class AvailablePowerSource(Resource):

    def __init__(self, name="6", children=None, resource_id="6", coap_server=None):
        super(AvailablePowerSource, self).__init__(name, coap_server=coap_server)
        self.resource_id = resource_id
        self.children = children
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def set_children(self, children):
        self.children = children

    def render_GET(self, request):
        resource = {self.resource_id: (None, self.path, self.lwm2m_type)}
        resources = TreeVisit.get_children(self.children, resource)
        self.payload = TreeVisit.encode(resources, request.uri_path,
                                        defines.Content_types["application/vnd.oma.lwm2m+tlv"])
        return self

    def get_value(self):
        return TreeVisit.get_children(self.children)


class AvailablePowerSourceItem(Resource):

    def __init__(self, name, value, resource_id, coap_server):
        super(AvailablePowerSourceItem, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class PowerSourceVoltage(Resource):

    def __init__(self, name="7", children=None, resource_id="7", coap_server=None):
        super(PowerSourceVoltage, self).__init__(name, coap_server=coap_server)
        self.resource_id = resource_id
        self.children = children
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def set_children(self, children):
        self.children = children

    def render_GET(self, request):
        resource = {self.resource_id: (None, self.path, self.lwm2m_type)}
        resources = TreeVisit.get_children(self.children, resource)
        self.payload = TreeVisit.encode(resources, request.uri_path,
                                        defines.Content_types["application/vnd.oma.lwm2m+tlv"])
        return self

    def get_value(self):
        return TreeVisit.get_children(self.children)


class PowerSourceVoltageItem(Resource):

    def __init__(self, name, value, resource_id, coap_server):
        super(PowerSourceVoltageItem, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class PowerSourceCurrent(Resource):

    def __init__(self, name="8", children=None, resource_id="8", coap_server=None):
        super(PowerSourceCurrent, self).__init__(name, coap_server=coap_server)
        self.resource_id = resource_id
        self.children = children
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def set_children(self, children):
        self.children = children

    def render_GET(self, request):
        resource = {self.resource_id: (None, self.path, self.lwm2m_type)}
        resources = TreeVisit.get_children(self.children, resource)
        self.payload = TreeVisit.encode(resources, request.uri_path,
                                        defines.Content_types["application/vnd.oma.lwm2m+tlv"])
        return self

    def get_value(self):
        return TreeVisit.get_children(self.children)


class PowerSourceCurrentItem(Resource):

    def __init__(self, name, value, resource_id, coap_server):
        super(PowerSourceCurrentItem, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class BatteryLevel(Resource):

    def __init__(self, name="9", value="", resource_id="9", coap_server=None):
        super(BatteryLevel, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class MemoryFree(Resource):

    def __init__(self, name="10", value="", resource_id="10", coap_server=None):
        super(MemoryFree, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class ErrorCode(Resource):

    def __init__(self, name="11", children=None, resource_id="11", coap_server=None):
        super(ErrorCode, self).__init__(name, coap_server=coap_server)
        self.resource_id = resource_id
        self.children = children
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def set_children(self, children):
        self.children = children

    def render_GET(self, request):
        resource = {self.resource_id: (None, self.path, self.lwm2m_type)}
        resources = TreeVisit.get_children(self.children, resource)
        self.payload = TreeVisit.encode(resources, request.uri_path,
                                        defines.Content_types["application/vnd.oma.lwm2m+tlv"])
        return self

    def get_value(self):
        return TreeVisit.get_children(self.children)


class ErrorCodeItem(Resource):

    def __init__(self, name, value, resource_id, coap_server):
        super(ErrorCodeItem, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class ResetErrorCode(Resource):

    def __init__(self, name="12", resource_id="12", coap_server=None):
        super(ResetErrorCode, self).__init__(name, coap_server=coap_server)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_POST(self, request):
        pass


class CurrentTime(Resource):

    def __init__(self, name="13", value=0, resource_id="13", coap_server=None):
        super(CurrentTime, self).__init__(name, coap_server=coap_server)
        self.start_time = int(time.time())
        if value == 0:
            self.value = self.start_time
        else:
            self.value = int(value)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.get_value())
        return self

    def render_PUT(self, request):
        self.set_value(request.payload)
        return self

    def set_value(self, value):
        self.start_time = int(time.time())
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        now = int(time.time())
        dif = now - self.start_time
        self.value += dif
        return self.value


class UTCOffset(Resource):

    def __init__(self, name="14", value="", resource_id="14", coap_server=None):
        super(UTCOffset, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.get_value())
        return self

    def render_PUT(self, request):
        self.set_value(request.payload)
        return self

    def set_value(self, value):
        self.value = str(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class Timezone(Resource):

    def __init__(self, name="15", value="", resource_id="15", coap_server=None):
        super(Timezone, self).__init__(name, coap_server=coap_server)

        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def render_PUT(self, request):
        self.set_value(request.payload)
        return self

    def set_value(self, value):
        self.value = str(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class Binding(Resource):

    def __init__(self, name="16", value="", resource_id="16", coap_server=None):
        super(Binding, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value
