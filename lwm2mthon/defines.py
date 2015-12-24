__author__ = 'giacomo'


class LWM2MInstance(object):
    ID = "id"
    NAME = "name"
    INSTANCE_TYPE = "instancetype"
    MANDATORY = "mandatory"
    DESCRIPTION = "description"
    RESOURCEDEFS = "resourcedefs"


class LWM2MResource(object):
    ID = "id"
    NAME = "name"
    INSTANCE_TYPE = "instancetype"
    MANDATORY = "mandatory"
    DESCRIPTION = "description"
    OPERATIONS = "operations"
    RANGE = "range"
    UNITS = "units"
    TYPE = "type"


class LWM2MInstanceType(object):
    SINGLE = "single"
    MULTIPLE = "multiple"


class LWM2MResourceType(object):
    STRING = "string"
    INTEGER = "integer"
    TIME = "time"


class LWM2MOperations(object):
    READ = "R"
    WRITE = "W"
    EXECUTE = "E"
    READWRITE = "RW"
    NONE = "NONE"


class ObjectId(object):
    LWM2M_SECURITY = 0
    LWM2M_SERVER = 1
    LWM2M_ACCESS_CONTROL = 2
    DEVICE = 3
    CONNECTIVITY_MONITOR = 4
    FIRMWARE_UPDATE = 5
    LOCATION = 6
    CONNECTIVITY_STATISTIC = 7


class DeviceIds(object):
    MANUFACTURER = 0


class InstanceItem(object):
    def __init__(self, instance_id, name, instancetype, mandatory, description):
        self.instance_id = instance_id
        self.name = name
        self.instancetype = instancetype
        self.mandatory = mandatory
        self.description = description
        self.resourcedefs = {}

    def add_resourcedef(self, key, resource_def):
        self.resourcedefs[key] = resource_def

    def get_resourcedef(self, key):
        return self.resourcedefs.get(key)


class ResourceItem(object):
    def __init__(self, operations, mandatory, name, resource_id, resource_range, units, resource_type, instancetype,
                 description):

        self.operations = operations
        self.mandatory = mandatory
        self.name = name
        self.resource_id = resource_id
        self.range = resource_range
        self.units = units
        self.resource_type = resource_type
        self.instancetype = instancetype
        self.description = description

Content_types = {
    "text/plain": 0,
    "application/link-format": 40,
    "application/xml": 41,
    "application/octet-stream": 42,
    "application/exi": 47,
    "application/json": 50,
    "application/vnd.oma.lwm2m+tlv": 1542,
    "application/vnd.oma.lwm2m+json": 1543
}

Registry = {
    "3/0/0":  "Manufacturer",
    "3/0/1":  "ModelNumber",
    "3/0/2":  "SerialNumber",
    "3/0/3":  "FirmwareVersion",
    "3/0/4":  "Reboot",
    "3/0/5":  "FactoryReboot",
    "3/0/6":  "AvailablePowerSource",
    "3/0/7":  "PowerSourceVoltage",
    "3/0/8":  "PowerSourceCurrent",
    "3/0/9":  "BatteryLevel",
    "3/0/10":  "MemoryFree",
    "3/0/11":  "ErrorCode",
    "3/0/12":  "ResetErrorCode",
    "3/0/13":  "CurrentTime",
    "3/0/14":  "UTCOffset",
    "3/0/15":  "Timezone",
    "3/0/16":  "Binding",
}