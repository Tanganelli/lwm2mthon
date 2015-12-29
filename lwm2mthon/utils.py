import json
import struct
import ctypes
from lwm2mthon import defines
from lwm2mthon.defines import RegistryType, LWM2MResourceType
from lwm2mthon.tlv import TLV, MULTIPLE_RESOURCE_TLV, RESOURCE_INSTANCE_TLV, RESOURCE_TLV, OBJECT_INSTANCE

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

                    children_len = 0
                    children = []
                    for i1, t1 in p.iteritems():
                        p1, path1, resource_type1 = t1
                        children_len += 1
                        tlv1 = TLV(RESOURCE_INSTANCE_TLV, None, p1, i1, resource_type1)
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

    @staticmethod
    def decode(payload, request_path, encode_type):
        ret = []
        if encode_type == defines.Content_types["application/vnd.oma.lwm2m+json"]:
            pass
        elif encode_type == defines.Content_types["application/vnd.oma.lwm2m+tlv"]:
            tlvs = TreeVisit.get_tlvs(payload, request_path)
            for i in tlvs:
                ret.append((i[0], i[1].identifier, i[1].value))
        return ret

    @staticmethod
    def get_tlvs(payload, request_path):
            fmt = "!"
            length = len(payload)
            pos = 0
            while pos < length:
                fmt += "c"
                pos += 1
            s = struct.Struct(fmt)
            values = s.unpack_from(payload)
            length_packet = len(values)
            tlvs = []
            pos = 0
            while pos < length_packet:
                first_byte = struct.unpack("B", values[pos])[0]
                pos += 1
                tmp = first_byte & 0b11000000

                if tmp == 0b00000000:
                    tlv_type = OBJECT_INSTANCE
                elif tmp == 0b01000000:
                    tlv_type = RESOURCE_INSTANCE_TLV
                elif tmp == 0b10000000:
                    tlv_type = MULTIPLE_RESOURCE_TLV
                elif tmp == 0b11000000:
                    tlv_type = RESOURCE_TLV
                else:
                    raise ValueError

                tmp = first_byte & 0b00100000
                if tmp == 0:
                    identifier = struct.unpack("B", values[pos])[0]
                    pos += 1
                else:
                    identifier = struct.unpack("H", str(values[pos:pos+1]))[0]
                    pos += 2

                tmp = first_byte & 0b00011000
                if tmp == 0b00000000:
                    # 2 bit length
                    length = first_byte & 0b00000111
                elif tmp == 0b00001000:
                    length = struct.unpack("B", values[pos])[0]
                    pos += 1
                elif tmp == 0b00010000:
                    length = struct.unpack("H", str(values[pos:pos+1]))[0]
                    pos += 2
                elif tmp == 0b00011000:
                    length = (struct.unpack("B", values[pos])[0] << 16) + \
                             struct.unpack("H", str(values[pos+1:pos+2]))[0]
                    pos += 3
                else:
                    raise ValueError

                if tlv_type == RESOURCE_TLV or tlv_type == RESOURCE_INSTANCE_TLV:
                    path = request_path + "/" + str(identifier)
                    res_type = RegistryType[path]
                    value = None
                    if res_type == LWM2MResourceType.STRING:
                        value = str(payload[pos:pos+length])

                    elif res_type == LWM2MResourceType.INTEGER or res_type == LWM2MResourceType.BOOLEAN:
                        i = 0
                        value = 0
                        while i < length:
                            value <<= 8
                            tmp = struct.unpack("B", values[pos])[0]
                            value += tmp
                            i += 1

                    tlv = TLV(tlv_type, None, value, identifier, res_type)
                    tlvs.append((path, tlv))
                else:
                    payload_children = str(payload[pos:pos+length])
                    tlvs_tmp = TreeVisit.get_tlvs(payload_children, request_path)
                    tlvs.extend(tlvs_tmp)
                pos += length
            return tlvs
