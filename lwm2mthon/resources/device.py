import ctypes
import json
import struct
from coapthon.messages.option import Option
from coapthon.resources.resource import Resource
from lwm2mthon import defines
import coapthon.defines as coap_defines
from lwm2mthon.tlv import RESOURCE_TLV, TLV

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
        # Object Instance
        # encode as JASON SenML
        resources = {"e": []}
        # option = Option()
        # option.number = coap_defines.OptionRegistry.ACCEPT.number
        # option.value = defines.Content_types["application/vnd.oma.lwm2m+tlv"]
        # request.add_option(option)
        # self._required_content_type = defines.Content_types["application/vnd.oma.lwm2m+tlv"]
        for c in self.children.keys():
            assert isinstance(self.children[c], Resource)
            if "Read" in self.children[c].__class__.__name__:
                res = self.children[c].render_GET(request)
                try:
                    payload = json.loads(res.payload)
                except ValueError:
                    payload = res.payload
                path = res.path[2 + len(request.uri_path):]
                if isinstance(payload, dict):
                    tmp = payload["e"]
                    for i in tmp:
                        resources["e"].append(i)
                else:
                    resources["e"].append({"n": path, "v": payload})

        self._required_content_type = defines.Content_types["application/vnd.oma.lwm2m+tlv"]
        tlv_bytes = []
        for res in resources["e"]:
            r_id = res["n"]
            if "/" not in r_id:
                # Single Resource
                tlv = TLV(RESOURCE_TLV, None, res["v"], r_id)
                tlv_bytes.append(tlv.encode())
                print r_id

        g_fmt = "!"
        g_values = []
        for fmt, values in tlv_bytes:
            g_fmt += fmt[1:]
            for v in values:
                g_values.append(v)

        s = struct.Struct(g_fmt)
        tlv_packed = ctypes.create_string_buffer(s.size)
        s.pack_into(tlv_packed, 0, *g_values)

        self._payload[self._required_content_type] = tlv_packed.raw
        return self


class SingleReadString(Resource):
    def render_GET(self, request):
        # if request.accept == defines.Content_types["application/vnd.oma.lwm2m+tlv"]:
        #     r_id = self.path[2 + len(request.uri_path):]
        #     tlv = TLV(RESOURCE_TLV, None, self.payload, r_id)
        #     self.required_content_type = defines.Content_types["application/vnd.oma.lwm2m+tlv"]
        #     self._payload[request.accept] = tlv.encode()
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
        resources = {"e": []}
        for c in self.children.keys():
            assert isinstance(self.children[c], Resource)
            if "Read" in self.children[c].__class__.__name__:
                res = self.children[c].render_GET(request)
                resources["e"].append({"n": res.path[2 + len(request.uri_path):], "v": res.payload})
        self.payload += json.dumps(resources)
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


