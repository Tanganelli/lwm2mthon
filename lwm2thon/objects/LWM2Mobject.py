import re


class LWM2MBaseEntity(object):
    def __init__(self):
        self._rel = None
        self._anchor = None
        self._rev = None
        self._hreflang = None
        self._media = None
        self._title = None
        self._type = None
        self._rt = None
        self._if = None
        self._sz = None
        self._ct = None
        self._obs = False
        self._parmnames = {}

    def parse(self, link_format: str) -> bool:
        pattern = "([^<,])*"
        ret = re.match(pattern, link_format)
        if ret is None:
            return True
        attributes = ret.group(0)
        if len(attributes) > 0:
            attributes = attributes.split(";")
            for att in attributes:
                a = att.split("=")
                if len(a) > 1:
                    key = a[0]
                    if key == "rel":
                        self._rel = a[1]
                    elif key == "anchor":
                        self._anchor = a[1]
                    elif key == "rev":
                        self._rev = a[1]
                    elif key == "hreflang":
                        self._hreflang = a[1]
                    elif key == "media":
                        self._media = a[1]
                    elif key == "title":
                        self._title = a[1]
                    elif key == "type":
                        self._type = a[1]
                    elif key == "rt":
                        self._rt = a[1]
                    elif key == "if":
                        self._if = a[1]
                    elif key == "sz":
                        self._sz = a[1]
                    elif key == "ct":
                        self._ct = a[1]
                    else:
                        self._parmnames[key] = a[1]
                else:
                    key = a[0]
                    if key == "obs":
                        self._obs = True
                    else:
                        self._parmnames[key] = a[0]
        return True


class LWM2MObject(LWM2MBaseEntity):
    def __init__(self, object_id: str):
        super().__init__()
        self._id = object_id
        self._object_instances = {}

    @property
    def id(self):
        return self._id

    def add_instance(self, object_instance: LWM2MObjectInstance):
        self._object_instances[object_instance.id] = object_instance

    def get_instance(self, object_instance_id: str):
        return self._object_instances.get(object_instance_id, None)


class LWM2MObjectInstance(LWM2MBaseEntity):
    def __init__(self, object_instance_id: str, parent_object: LWM2MObject):
        super().__init__()
        self._parent_object = parent_object
        self._id = object_instance_id
        self._resources = {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def parent(self):
        return self._parent_object

    def add_resource(self, resource: LWM2MResource):
        self._resources[resource.id] = resource

    def get_resource(self, resource_id: str):
        return self._resources.get(resource_id, None)


class LWM2MResource(LWM2MBaseEntity):
    def __init__(self, resource_id: str, parent_instance: LWM2MObjectInstance):
        super().__init__()
        self._parent_object_instance = parent_instance
        self._id = resource_id
        self._resource_instances = {}
        self._multiple_instance = False
        self._value = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    @property
    def multiple_instance(self) -> bool:
        return self._multiple_instance

    @multiple_instance.setter
    def multiple_instance(self, b: bool):
        self._multiple_instance = b

    @property
    def parent(self):
        return self._parent_object_instance

    def add_resource_instance(self, resource_instance: LWM2MResourceInstance):
        self._resource_instances[resource_instance.id] = resource_instance

    def get_resource_instance(self, resource_instance_id: str):
        return self._resource_instances.get(resource_instance_id, None)


class LWM2MResourceInstance(LWM2MBaseEntity):
    def __init__(self, resource_instance_id: str, parent_resource: LWM2MResource):
        super().__init__()
        self._parent_resource = parent_resource
        self._id = resource_instance_id
        self._value = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    @property
    def parent(self):
        return self._parent_resource

