from coapthon.resources.resource import Resource
from lwm2mthon import defines
from lwm2mthon.defines import LWM2MResourceType
from lwm2mthon.utils import TreeVisit

__author__ = 'giacomo'


class LWM2MSecurity(Resource):
    def __init__(self, name="0"):
        super(LWM2MSecurity, self).__init__(name)


class LWM2MSecurityInstance(Resource):
    def __init__(self, name, children):
        super(LWM2MSecurityInstance, self).__init__(name)
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


class LWM2MServerUri(Resource):

    def __init__(self, name="0", value="", resource_id="0"):
        super(LWM2MServerUri, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_POST(self, request):
        pass

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value

