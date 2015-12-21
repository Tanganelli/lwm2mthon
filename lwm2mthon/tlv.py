import ctypes
import struct

__author__ = 'jacko'

RESOURCE_TLV = 0


class TLV(object):
    def __init__(self, tlv_type, children, value, identifier):
        self.tlv_type = tlv_type
        self.children = children
        self.value = str(value)
        self.identifier = identifier

    def encode(self):
        values = []
        fmt = "!"
        if self.tlv_type == RESOURCE_TLV:
            tmp = 0b11000000
            length = len(self.value)
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
        if len(self.identifier) < 256:
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

        if self.tlv_type == RESOURCE_TLV:
            for b in str(self.value):
                fmt += "c"
                values.append(b)
        else:
            raise NotImplementedError

        return fmt, values
