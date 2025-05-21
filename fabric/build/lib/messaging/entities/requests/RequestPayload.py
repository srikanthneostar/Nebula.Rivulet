from messaging.entities.requests.Entities import Entities
from messaging.entities.requests.EntityProperties import EntityProperties
from messaging.entities.requests.SystemRequest import SystemRequest


class RequestPayload:
    systemRequests: SystemRequest =   SystemRequest()
    properties: list = EntityProperties()
    entities: list = Entities()

    def __init__(self, my_dict):
        if my_dict is not None:
            for key in my_dict:
                setattr(self, key, my_dict[key])
