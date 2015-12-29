
from lwm2mthon.defines import LWM2MResourceType

__author__ = 'jacko'

RESOURCE_TLV = 0
RESOURCE_INSTANCE_TLV = 1
MULTIPLE_RESOURCE_TLV = 2
OBJECT_INSTANCE = 4


class TLV(object):
    def __init__(self, tlv_type, children, value, identifier, resource_type):
        self.tlv_type = tlv_type
        self.children = children
        self.value = None
        self.length = None
        if resource_type == LWM2MResourceType.STRING and value is not None:
            self.value = str(value)
            self.length = len(str(value))
        elif (resource_type == LWM2MResourceType.INTEGER or resource_type == LWM2MResourceType.BOOLEAN) \
                and value is not None:
            self.value = int(value)
            if -128 <= self.value <= 127:
                self.length = 1
            elif -32768 <= self.value <= 32767:
                self.length = 2
            elif -2147484648 <= self.value < 2147484647:
                self.length = 4
            else:
                self.length = 8
        self.identifier = int(identifier)
        self.resource_type = resource_type

    def encode(self):
        values = []
        fmt = "!"
        if self.tlv_type == RESOURCE_TLV:
            tmp = 0b11000000
            length = self.length
        elif self.tlv_type == MULTIPLE_RESOURCE_TLV:
            tmp = 0b10000000
            length = self.length
        elif self.tlv_type == RESOURCE_INSTANCE_TLV:
            tmp = 0b01000000
            length = self.length
        else:
            raise NotImplementedError
        if self.identifier >= 256:
            # identifier length on 16 bits
            tmp |= 0b00100000

        if length < 8:
            tmp |= length
        elif length < 256:
            tmp |= 0b00001000
        elif length < 65536:
            tmp |= 0b00010000
        else:
            tmp |= 0b00011000

        fmt += "B"
        values.append(tmp)
        values.append(int(self.identifier))
        if self.identifier < 256:
            fmt += "B"
        else:
            fmt += "H"

        if length >= 8:
            if length < 256:
                values.append(length)
                fmt += "B"
            elif length < 65536:
                values.append(length)
                fmt += "H"
            else:
                msb = (length & 0xFF0000) >> 16
                values.append(msb)
                fmt += "B"
                values.append(length & 0x00FFFF)
                fmt += "H"

        if self.tlv_type == RESOURCE_TLV or self.tlv_type == RESOURCE_INSTANCE_TLV:
            if self.resource_type == LWM2MResourceType.STRING:
                for b in str(self.value):
                    fmt += "c"
                    values.append(b)
            elif self.resource_type == LWM2MResourceType.INTEGER or self.resource_type == LWM2MResourceType.BOOLEAN:
                if self.length == 1:
                    values.append(self.value)
                    fmt += "B"
                elif self.length == 2:
                    values.append(self.value)
                    fmt += "H"
                elif self.length == 4:
                    msb = (self.value & 0xFFFF0000) >> 16
                    values.append(msb)
                    fmt += "H"
                    values.append(self.value & 0x0000FFFF)
                    fmt += "H"
                elif self.length == 8:
                    msb = (self.value & 0xFFFF000000000000) >> 48
                    values.append(msb)
                    fmt += "H"
                    lsb = (self.value & 0x0000FFFF00000000) >> 32
                    values.append(lsb)
                    fmt += "H"

                    msb = (self.value & 0xFFFF0000FFFF0000) >> 16
                    values.append(msb)
                    fmt += "H"
                    lsb = (self.value & 0x000000000000FFFF)
                    values.append(lsb)
                    fmt += "H"
        elif self.tlv_type == MULTIPLE_RESOURCE_TLV:
            pass
        else:
            raise NotImplementedError

        return fmt, values
