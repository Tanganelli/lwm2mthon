import json
import struct
import ctypes
import os
from lwm2mthon import defines
from lwm2mthon.defines import RegistryType, LWM2MResourceType
from lwm2mthon.tlv import TLV, MULTIPLE_RESOURCE_TLV, RESOURCE_INSTANCE_TLV, RESOURCE_TLV, OBJECT_INSTANCE

__author__ = 'giacomo'


def create_description():
        json_dict = {
            "endpointClientName": "lwm2mthon",
            "lifetime": "60",
            "version": "1.0",
            "bindingMode": "U",
            "smsNo": "",
            "root": "/",
            "objects": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "instances": {
                "0": {
                    "0": {
                        "0": "coap://bootstrap.example.com:5684/",
                        "1": True,
                        "2": 0,
                        "3": "[identity string]",
                        "4": "[secret key data]",
                        "10": 0,
                        "11": 3600
                    },
                    "1": {
                        "0": "",
                        "1": False,
                        "2": 3,
                        "3": "",
                        "4": "",
                        "10": 101,
                        "11": 0
                    },
                    "2": {
                        "0": "coap://vs0.inf.ethz.ch:5686/",
                        "1": False,
                        "2": 3,
                        "3": "",
                        "4": "",
                        "10": 102,
                        "11": 0
                    }
                },
                "1": {
                    "1": {
                        "0": 101,
                        "1": 60,
                        "2": 20,
                        "3": 60,
                        "5": 3600,
                        "6": True,
                        "7": "U",
                        "8": "Lwm2mDevKit.Registration.update();"
                    }
                },
                "2": {
                    "0": {
                        "0": 1,
                        "1": 0,
                        "2": {
                            "101": 15
                        },
                        "3": 101
                    },
                    "1": {
                        "0": 1,
                        "1": 1,
                        "2": {
                            "102": 15
                        },
                        "3": 102
                    },
                    "2": {
                        "0": 3,
                        "1": 0,
                        "2": {
                            "101": 15,
                            "102": 1
                        },
                        "3": 101
                    },
                    "3": {
                        "0": 4,
                        "1": 0,
                        "2": {
                            "0": 1,
                            "101": 1
                        },
                        "3": 101
                    },
                    "4": {
                        "0": 5,
                        "1": 65535,
                        "2": {
                             "0": 1,
                             "101": 16
                        },
                        "3": 65535
                    }
                },
                "3": {
                    "0": {
                        "0": "Open Mobile Alliance",
                        "1": "Lightweight M2M Client",
                        "2": "345000123",
                        "3": "1.0",
                        "4": "document.location.reload();",
                        "6": {
                            "0": 1,
                            "1": 5
                        },
                        "7": {
                            "0": 3800,
                            "1": 5000
                        },
                        "8": {
                            "0": 125,
                            "1": 900
                        },
                        "9": 100,
                        "10": 15,
                        "11": {
                            "0": 0
                        },
                        "13": 0,
                        "14": "+01:00",
                        "15": "Europe/Rome",
                        "16": "U"
                    }
                },
                "4": {
                    "0": {
                        "0": 0,
                        "1": {
                            "0": 0
                        },
                        "2": 92,
                        "3": 2,
                        "4": {
                            "0": "192.168.0.100"
                        },
                        "5": {
                            "0": "192.168.1.1"
                        },
                        "6": 5,
                        "7": {
                            "0": "internet"
                        }
                    }
                },
                "5": {
                    "0": {
                        "0": "[firmware]",
                        "1": "",
                        "2": "alert('UPDATE');Lwm2mDevKit.client.instances[5][0][5]=1;Lwm2mDevKit.showInstanceScreen(5, 0);",
                        "3": 1,
                        "5": 0
                    }
                },
                "9": {
                    "0": {
                        "0": "Software_package_name",
                        "1": "1.0",
                        "2": "[software]",
                        "3": "",
                        "4": "alert('SOFTWARE INSTALLATION');Lwm2mDevKit.client.instances[9][0][9]=2;Lwm2mDevKit.showInstanceScreen(9, 0);",
                        "6": "alert('SOFTWARE UNINSTALL');Lwm2mDevKit.client.instances[9][0][9]=0;Lwm2mDevKit.showInstanceScreen(9, 0);",
                        "7": "1",
                        "9": "0",
                        "10": "alert('SOFTWARE ACTIVATION');Lwm2mDevKit.client.instances[9][0][12]=true;Lwm2mDevKit.showInstanceScreen(9, 0);",
                        "11": "alert('SOFTWARE DEACTIVATION');Lwm2mDevKit.client.instances[9][0][12]=false;Lwm2mDevKit.showInstanceScreen(9, 0);",
                        "12": False
                    }
                }
            },
            "attributes": {
                "1": {
                    "1": {
                        "pmin": 120,
                        "pmax": 600
                    },
                    "pmin": 300,
                    "pmax": 3600
                },
                "3": {
                    "0": {
                        "10": {
                            "pmin": 5,
                            "pmax": 45
                        },
                        "pmin": 10,
                        "pmax": 30
                    }
                }
            }
        }
        path = "conf_device.json"
        with open(path, "w") as f:
            json.dump(json_dict, f, indent=4, separators=(',', ': '))
        return os.path.abspath(path)


class TreeVisit(object):

    @staticmethod
    def make_tree(lst):
        tree = {}
        for item in lst:
            if item == "/":
                continue
            ids = item.split("/")
            ids = ids[1:]  # remove root
            tmp_tree = tree
            for i in ids:
                if i not in tmp_tree.keys():
                    tmp_tree[i] = {}

                tmp_tree = tmp_tree[i]

        return tree

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
