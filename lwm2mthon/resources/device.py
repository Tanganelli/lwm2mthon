import ctypes
import json
import struct
from coapthon.messages.option import Option
from coapthon.resources.resource import Resource
from lwm2mthon import defines
import coapthon.defines as coap_defines
from lwm2mthon.defines import LWM2MResourceType
from lwm2mthon.tlv import RESOURCE_TLV, TLV, RESOURCE_INSTANCE_TLV, MULTIPLE_RESOURCE_TLV

__author__ = 'giacomo'


class TreeVisit(object):

    @staticmethod
    def get_children(children, resource=None):
        resources = {}
        i = 0
        path = ""
        lwm2m_type = ""
        if resource is not None:
            i = resource.keys()[0]
            p, path, lwm2m_type = resource[i]
        for c, v in children.items():
            if hasattr(v, "get_value"):
                payload = v.get_value()
                resources[v.resource_id] = (payload, v.path, v.lwm2m_type)
        if resource is not None:
            resources = {i: (resources, path, lwm2m_type)}
        return resources

    @staticmethod
    def encode(resources, request_path, encode_type):
        if encode_type == defines.Content_types["application/vnd.oma.lwm2m+json"]:
            ret = {"e": []}
            for i, t in resources.items():
                d = TreeVisit.get_child(t, request_path)
                for n, v in d.iteritems():
                    ret["e"].append({"n": n, "v": v})

            return encode_type, json.dumps(ret)
        elif encode_type == defines.Content_types["application/vnd.oma.lwm2m+tlv"]:
            tlv_bytes = []
            for i, t in resources.items():
                p, path, resource_type = t
                if isinstance(p, dict):
                    # has children
                    tlv = TLV(MULTIPLE_RESOURCE_TLV, None, None, i, resource_type)

                    print i
                    children_len = 0
                    children = []
                    for i1, t1 in p.iteritems():
                        p1, path1, resource_type1 = t1
                        children_len += 1
                        tlv1 = TLV(RESOURCE_INSTANCE_TLV, None, p1, i1, resource_type1)
                        print str(i) + "/" + str(i1)
                        if int(i1) < 256:
                            children_len += 1
                        else:
                            children_len += 2

                        if tlv1.length < 8:
                            children_len += 0
                        elif tlv1.length < 256:
                            children_len += 1
                        elif tlv1.length < 65536:
                            children_len += 2
                        else:
                            children_len += 3

                        children_len += tlv1.length
                        children.append(tlv1)

                    tlv.length = children_len
                    tlv_bytes.append(tlv.encode())
                    for c in children:
                        tlv_bytes.append(c.encode())

                else:
                    # Single Resource
                    tlv = TLV(RESOURCE_TLV, None, p, i, resource_type)
                    print i
                    tlv_bytes.append(tlv.encode())

            g_fmt = "!"
            g_values = []
            for fmt, values in tlv_bytes:
                g_fmt += fmt[1:]
                for v in values:
                    g_values.append(v)

            s = struct.Struct(g_fmt)
            tlv_packed = ctypes.create_string_buffer(s.size)
            s.pack_into(tlv_packed, 0, *g_values)

            return defines.Content_types["application/vnd.oma.lwm2m+tlv"], tlv_packed.raw



    @staticmethod
    def get_child(t, request_path):
        p, path, resource_type = t
        d = {}
        if not isinstance(p, dict):
            d = {path[2 + len(request_path):]: p}
        else:
            for i, t in p.iteritems():
                tmp = TreeVisit.get_child(t, request_path)
                for n, v in tmp.iteritems():
                    d[n] = v
        return d


class Device(Resource):
    def __init__(self, name="3"):
        super(Device, self).__init__(name)


class DeviceInstance(Resource):
    def render_DELETE(self, request):
        return True

    def __init__(self, name, children):
        super(DeviceInstance, self).__init__(name)
        self.children = children

    def set_children(self, children):
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
        resources = TreeVisit.get_children(self.children)
        # encode as JASON SenML
        self.payload = TreeVisit.encode(resources, request.uri_path,
                                        defines.Content_types["application/vnd.oma.lwm2m+tlv"])
        print self.payload

        # resources = {"e": []}
        # # option = Option()
        # # option.number = coap_defines.OptionRegistry.ACCEPT.number
        # # option.value = defines.Content_types["application/vnd.oma.lwm2m+tlv"]
        # # request.add_option(option)
        # # self._required_content_type = defines.Content_types["application/vnd.oma.lwm2m+tlv"]
        # for c in self.children.keys():
        #     assert isinstance(self.children[c], Resource)
        #     if "Read" in self.children[c].__class__.__name__:
        #         res = self.children[c].render_GET(request)
        #         try:
        #             payload = json.loads(res.payload)
        #         except ValueError:
        #             payload = res.payload
        #         path = res.path[2 + len(request.uri_path):]
        #         if isinstance(payload, dict):
        #             tmp = payload["e"]
        #             for i in tmp:
        #                 resources["e"].append(i)
        #         else:
        #             resources["e"].append({"n": path, "v": payload})
        #
        # self.actual_content_type = defines.Content_types["application/vnd.oma.lwm2m+tlv"]
        # tlv_bytes = []
        # for res in resources["e"]:
        #     r_id = res["n"]
        #     if "/" not in r_id:
        #         # Single Resource
        #         tlv = TLV(RESOURCE_TLV, None, res["v"], r_id)
        #         tlv_bytes.append(tlv.encode())
        #         print r_id
        #
        # g_fmt = "!"
        # g_values = []
        # for fmt, values in tlv_bytes:
        #     g_fmt += fmt[1:]
        #     for v in values:
        #         g_values.append(v)
        #
        # s = struct.Struct(g_fmt)
        # tlv_packed = ctypes.create_string_buffer(s.size)
        # s.pack_into(tlv_packed, 0, *g_values)
        #
        # self.payload = (defines.Content_types["application/vnd.oma.lwm2m+tlv"], tlv_packed.raw)
        return self


class Manufacturer(Resource):

    def __init__(self, name="0", value="", resource_id="0"):
        super(Manufacturer, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class ModelNumber(Resource):

    def __init__(self, name="1", value="", resource_id="1"):
        super(ModelNumber, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class SerialNumber(Resource):

    def __init__(self, name="2", value="", resource_id="2"):
        super(SerialNumber, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class FirmwareVersion(Resource):

    def __init__(self, name="3", value="", resource_id="3"):
        super(FirmwareVersion, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class Reboot(Resource):

    def __init__(self, name="4", resource_id="4"):
        super(Reboot, self).__init__(name)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_POST(self, request):
        pass


class FactoryReboot(Resource):

    def __init__(self, name="5", resource_id="5"):
        super(FactoryReboot, self).__init__(name)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_POST(self, request):
        pass


class AvailablePowerSource(Resource):

    def __init__(self, name="6", children=None, resource_id="6"):
        super(AvailablePowerSource, self).__init__(name)
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

    def __init__(self, name, value, resource_id):
        super(AvailablePowerSourceItem, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class PowerSourceVoltage(Resource):

    def __init__(self, name="7", children=None, resource_id="7"):
        super(PowerSourceVoltage, self).__init__(name)
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

    def __init__(self, name, value, resource_id):
        super(PowerSourceVoltageItem, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class PowerSourceCurrent(Resource):

    def __init__(self, name="8", children=None, resource_id="8"):
        super(PowerSourceCurrent, self).__init__(name)
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

    def __init__(self, name, value, resource_id):
        super(PowerSourceCurrentItem, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class BatteryLevel(Resource):

    def __init__(self, name="9", value="", resource_id="9"):
        super(BatteryLevel, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class MemoryFree(Resource):

    def __init__(self, name="10", value="", resource_id="10"):
        super(MemoryFree, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class ErrorCode(Resource):

    def __init__(self, name="11", children=None, resource_id="11"):
        super(ErrorCode, self).__init__(name)
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

    def __init__(self, name, value, resource_id):
        super(ErrorCodeItem, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.INTEGER

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class ResetErrorCode(Resource):

    def __init__(self, name="12", resource_id="12"):
        super(ResetErrorCode, self).__init__(name)
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_POST(self, request):
        pass


class CurrentTime(Resource):

    def __init__(self, name="13", value="", resource_id="13"):
        super(CurrentTime, self).__init__(name)
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
        self.value = str(value)

    def get_value(self):
        return self.value


class UTCOffset(Resource):

    def __init__(self, name="14", value="", resource_id="14"):
        super(UTCOffset, self).__init__(name)
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

    def get_value(self):
        return self.value


class Timezone(Resource):

    def __init__(self, name="15", value="", resource_id="15"):
        super(Timezone, self).__init__(name)
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

    def get_value(self):
        return self.value


class Binding(Resource):

    def __init__(self, name="16", value="", resource_id="16"):
        super(Binding, self).__init__(name)
        self.value = value
        self.resource_id = resource_id
        self.lwm2m_type = LWM2MResourceType.STRING

    def render_GET(self, request):
        self.payload = str(self.value)
        return self

    def set_value(self, value):
        self.value = str(value)

    def get_value(self):
        return self.value


class SingleReadString(Resource):
    def render_GET(self, request):
        # if request.accept == defines.Content_types["application/vnd.oma.lwm2m+tlv"]:
        #     r_id = self.path[2 + len(request.uri_path):]
        #     tlv = TLV(RESOURCE_TLV, None, self.payload, r_id)
        #     self.required_content_type = defines.Content_types["application/vnd.oma.lwm2m+tlv"]
        #     self._payload[request.accept] = tlv.encode()
        return self

    def __init__(self, name, value, resource_id):
        super(SingleReadString, self).__init__(name)
        self.payload = value
        self.resource_id = resource_id

    def set_value(self, value):
        self.payload = str(value)


class SingleExecuteString(Resource):

    def render_POST(self, request):
        # TODO execute
        pass

    def __init__(self, name="4", value="", resource_id=0):
        super(SingleExecuteString, self).__init__(name)
        self.execute = value
        self.resource_id = resource_id


class MultipleReadInteger(Resource):
    def __init__(self, name, children, resource_id):
        super(MultipleReadInteger, self).__init__(name)
        self.children = children
        self.resource_id = resource_id

    def render_GET(self, request):
        self.payload = ""

        resources = {"e": []}
        for c in self.children.keys():
            assert isinstance(self.children[c], Resource)
            if "Read" in self.children[c].__class__.__name__:
                res = self.children[c].render_GET(request)
                resources["e"].append({"n": res.path[2 + len(request.uri_path):], "v": res.payload})

        if self.actual_content_type is None:
            # TLV
            tlv_bytes = []
            children_tlvs = []
            for res in resources["e"]:
                r_id = res["n"]
                # Single Resource
                tlv = TLV(RESOURCE_INSTANCE_TLV, None, res["v"], r_id)
                children_tlvs.append(tlv)
                tlv_bytes.append(tlv.encode())

            tlv = TLV(MULTIPLE_RESOURCE_TLV, children_tlvs, None, self.resource_id)
            bytes_def = [tlv.encode()]
            bytes_def.extend(tlv_bytes)
            g_fmt = "!"
            g_values = []
            for fmt, values in bytes_def:
                g_fmt += fmt[1:]
                for v in values:
                    g_values.append(v)

            s = struct.Struct(g_fmt)
            tlv_packed = ctypes.create_string_buffer(s.size)
            s.pack_into(tlv_packed, 0, *g_values)

            self.payload = (defines.Content_types["application/vnd.oma.lwm2m+tlv"], tlv_packed.raw)
        else:
            # jason
            self.payload = (defines.Content_types["application/vnd.oma.lwm2m+json"], json.dumps(resources))

        return self


class SingleReadInteger(Resource):
    def render_GET(self, request):
        return self

    def __init__(self, name, value, resource_id):
        super(SingleReadInteger, self).__init__(name)
        assert isinstance(value, int)
        self.payload = str(value)
        self.resource_id = resource_id

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

    def __init__(self, name, value, resource_id):
        super(SingleReadWriteTime, self).__init__(name)
        # TODO check time
        self.payload = str(value)
        self.resource_id = resource_id

    def set_value(self, value):
        # TODO check time
        self.payload = str(value)


class SingleReadWriteString(Resource):
    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_GET(self, request):
        return self

    def __init__(self, name, value, resource_id):
        super(SingleReadWriteString, self).__init__(name)
        self.payload = str(value)
        self.resource_id = resource_id

    def set_value(self, value):
        self.payload = str(value)


