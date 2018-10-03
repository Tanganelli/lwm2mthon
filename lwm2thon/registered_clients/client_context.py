from enum import Enum


class ClientContext(object):
    def __init__(self, address: tuple=None, private_key: str=None, public_key: str=None, certificate: str=None):
        self._address = address
        self._private_key = private_key
        self._public_key = public_key
        self._certificate = certificate

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, a: tuple):
        self._address = a

    @property
    def private_key(self):
        return self._private_key

    @private_key.setter
    def private_key(self, key: str):
        self._private_key = key

    @private_key.deleter
    def private_key(self):
        self._private_key = None

    @property
    def public_key(self):
        return self._public_key

    @public_key.setter
    def public_key(self, key: str):
        self._public_key = key

    @public_key.deleter
    def public_key(self):
        self._public_key = None

    @property
    def certificate(self):
        return self._certificate

    @certificate.setter
    def certificate(self, key: str):
        self._certificate = key

    @certificate.deleter
    def certificate(self):
        self._certificate = None


class Binding(Enum):
    U = 1
    T = 2
    S = 3
    N = 4


class Instances(Enum):
    SINGLE = 1
    MULTIPLE = 2


class Operation(Enum):
    READ = 1
    WRITE = 2
    EXECUTE = 3


class ResourceType(Enum):
    STRING = 1
    INTEGER = 2
    FLOAT = 3
    BOOLEAN = 4
    OPAQUE = 5
    TIME = 6
    OBJLINK = 7
    NONE = 8
