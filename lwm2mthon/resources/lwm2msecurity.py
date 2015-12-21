from coapthon.messages.request import Request
from coapthon.resources.resource import Resource

__author__ = 'giacomo'


class LWM2MSecurity(Resource):
    def __init__(self, name="/0"):
        super(LWM2MSecurity, self).__init__(name)

    def render_POST(self, request):
        return self.init_resource(request, Instance(request))


class Instance(Resource):
    def __init__(self, request):
        assert isinstance(request, Request)
        name = request.uri_path
        super(Instance, self).__init__(name)

    def render_GET(self, request):
        pass