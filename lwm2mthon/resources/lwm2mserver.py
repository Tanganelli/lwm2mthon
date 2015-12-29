from coapthon.resources.resource import Resource
from lwm2mthon import defines
from lwm2mthon.defines import LWM2MResourceType
from lwm2mthon.utils import TreeVisit

__author__ = 'giacomo'


class LWM2MServer(Resource):
    def __init__(self, name="2"):
        super(LWM2MServer, self).__init__(name)


class LWM2MServerInstance(Resource):
    def __init__(self, name, children, coap_server):
        super(LWM2MServerInstance, self).__init__(name, coap_server=coap_server)
        self.children = children

    def set_children(self, children):
        self.children = children

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


class ShortServerID(Resource):

    def __init__(self, name="0", value="", resource_id="0", coap_server=None):
        super(ShortServerID, self).__init__(name, coap_server=coap_server)
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


class Lifetime(Resource):

    def __init__(self, name="1", value="", resource_id="1", coap_server=None):
        super(Lifetime, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def render_PUT(self, request):
        self.set_value(request.payload)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class DefaultMinimumPeriod(Resource):

    def __init__(self, name="2", value="", resource_id="2", coap_server=None):
        super(DefaultMinimumPeriod, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def render_PUT(self, request):
        self.set_value(request.payload)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class DefaultMaximumPeriod(Resource):

    def __init__(self, name="3", value="", resource_id="3", coap_server=None):
        super(DefaultMaximumPeriod, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def render_PUT(self, request):
        self.set_value(request.payload)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class Disable(Resource):

    def __init__(self, name="4", resource_id="4", coap_server=None):
        super(Disable, self).__init__(name, coap_server=coap_server)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_POST(self, request):
        pass


class DisableTimeout(Resource):

    def __init__(self, name="5", value="", resource_id="5", coap_server=None):
        super(DisableTimeout, self).__init__(name, coap_server=coap_server)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def render_PUT(self, request):
        self.set_value(request.payload)
        return self

    def set_value(self, value):
        self.value = int(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class NotificationStoring(Resource):

    def __init__(self, name="6", value="", resource_id="6", coap_server=None):
        super(NotificationStoring, self).__init__(name, coap_server=coap_server)
        self.value = bool(value)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.BOOLEAN

    def render_GET(self, request):
        self.payload = str(int(self.value))
        return self

    def render_PUT(self, request):
        self.set_value(request.payload)
        return self

    def set_value(self, value):
        self.value = bool(value)
        self._coap_server.notify(self)

    def get_value(self):
        return self.value


class Binding(Resource):

    def __init__(self, name="7", value="", resource_id="7", coap_server=None):
        super(Binding, self).__init__(name, coap_server=coap_server)
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


class RegistrationUpdateTrigger(Resource):

    def __init__(self, name="8", resource_id="8", coap_server=None):
        super(RegistrationUpdateTrigger, self).__init__(name, coap_server=coap_server)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_POST(self, request):
        pass

