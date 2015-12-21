from coapthon.resources.resource import Resource

__author__ = 'giacomo'


class Device(Resource):
    def __init__(self, name="3"):
        super(Device, self).__init__(name)


class DeviceInstance(Resource):
    def render_DELETE(self, request):
        return True

    def __init__(self, name, children):
        super(DeviceInstance, self).__init__(name)
        self.children = children

    def render_PUT(self, request):
        for c in self.children.keys():
            assert isinstance(self.children[c], Resource)
            method = getattr(self.children[c], 'render_PUT', None)
            if method is not None:
                # TODO correct decoding
                self.children[c].render_PUT(request)
        return self

    def render_GET(self, request):
        self.payload = ""
        for c in self.children.keys():
            assert isinstance(self.children[c], Resource)
            res = self.children[c].render_GET(request)
            # TODO correct encoding
            self.payload += str(c) + "=" + res.payload
        return self


class SingleReadString(Resource):
    def render_GET(self, request):
        return self

    def __init__(self, name, value):
        super(SingleReadString, self).__init__(name)
        self.payload = value

    def set_value(self, value):
        self.payload = str(value)


class SingleExecuteString(Resource):

    def render_POST(self, request):
        # TODO execute
        pass

    def __init__(self, name="4", value=""):
        super(SingleExecuteString, self).__init__(name)
        self.execute = value


class MultipleReadInteger(Resource):
    def __init__(self, name, children):
        super(MultipleReadInteger, self).__init__(name)
        self.children = children

    def render_GET(self, request):
        self.payload = ""
        for c in self.children.keys():
            assert isinstance(self.children[c], Resource)
            res = self.children[c].render_GET(request)
            self.payload += str(c) + "=" + res.payload
        return self


class SingleReadInteger(Resource):
    def render_GET(self, request):
        return self

    def __init__(self, name, value):
        super(SingleReadInteger, self).__init__(name)
        assert isinstance(value, int)
        self.payload = str(value)

    def set_value(self, value):
        assert isinstance(value, int)
        self.payload = str(value)


class SingleReadWriteTime(Resource):
    def render_PUT(self, request):
        # TODO check time
        self.payload = request.payload
        return self

    def render_GET(self, request):
        return self

    def __init__(self, name, value):
        super(SingleReadWriteTime, self).__init__(name)
        # TODO check time
        self.payload = str(value)

    def set_value(self, value):
        # TODO check time
        self.payload = str(value)


class SingleReadWriteString(Resource):
    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_GET(self, request):
        return self

    def __init__(self, name, value):
        super(SingleReadWriteString, self).__init__(name)
        self.payload = str(value)

    def set_value(self, value):
        self.payload = str(value)


