from enum import Enum


class ClientContext(object):
    def __init__(self):
        self._address = None


class Binding(Enum):
    U = 1
    T = 2
    S = 3
    N = 4