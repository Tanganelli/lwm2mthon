from typing import Dict

import re

from lwm2thon.objects.LWM2Mobjects import LWM2MObject, LWM2MObjectInstance, LWM2MResource, LWM2MResourceInstance


class CoReLinkFormat(object):
    @staticmethod
    def parse(link_str: str) -> Dict[str, LWM2MObject]:
        objects = {}
        links = link_str.split(",")

        for l in links:
            pattern = "<([^>]*)>;"
            ret = re.match(pattern, l)
            if ret is None:
                return {}
            uri = ret.group(1)
            paths = uri.split("/")
            if len(paths) == 0:
                return {}

            object_id = None
            object_instance_id = None
            resource_id = None
            resource_instance_id = None
            for p in paths:
                if object_id is None:
                    object_id = LWM2MObject(p)
                elif object_instance_id is None:
                    object_instance_id = LWM2MObjectInstance(p, object_id)
                    object_id.add_instance(object_instance_id)
                elif resource_id is None:
                    resource_id = LWM2MResource(p, object_instance_id)
                    object_instance_id.add_resource(resource_id)
                elif resource_instance_id is None:
                    resource_instance_id = LWM2MResourceInstance(p, resource_id)
                    resource_id.add_resource_instance(resource_instance_id)

            link_format = l[ret.end(1) + 2:]
            if object_id is not None:
                object_id.parse(link_format)
                objects[object_id.id] = object_id
            if object_instance_id is not None:
                object_instance_id.parse(link_format)
            if resource_id is not None:
                resource_id.parse(link_format)
            if resource_instance_id is not None:
                resource_instance_id.parse(link_format)

        return objects


class LWM2MRegistrationQuery(object):
    @staticmethod
    def parse(query: str):
        endpoint_client_name = None
        lifetime = None
        lwm2m_version = None
        binding_mode = None
        queue_mode = None
        sms_number = None
        queries = query.split("&")
        for qu in queries:
            q = qu.split("=")
            if len(q) > 1:
                k = q[0]
                v = q[1]
                if k == "ep":
                    endpoint_client_name = v
                elif k == "lt":
                    lifetime = int(v)
                elif k == "lwm2m":
                    lwm2m_version = float(v)
                elif k == "b":
                    binding_mode = v
                elif k == "sms":
                    sms_number = v
            elif len(q) == 1:
                if q[0] == "Q":
                    queue_mode = True
        return endpoint_client_name, lifetime, lwm2m_version, binding_mode, queue_mode, sms_number
