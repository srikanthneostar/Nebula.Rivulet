from datetime import datetime
from messaging.entities.enum.Operation import Operation
from messaging.entities.enum.RequestStatus import RequestStatus
from messaging.entities.requests.ApplicationSystems import ApplicationSystems
from messaging.entities.requests.AuditTrails import AuditTrails


class SystemRequest(object):
    def default(self, o):
        return o.__dict__

    id: int = None
    isprocessed: bool = None
    requestor: str = None
    requesttype: str = None
    requeststatus: RequestStatus
    requestjson: str = None
    requesteddate: str = datetime.now()
    requestcomments: str = None
    messageid: str = None
    entityid: int = None
    entitytype: str = None
    createondate: str = datetime.now()
    modifyondate: str = datetime.now()
    objectid: int = None
    requestactions: str = None
    requestoperation: Operation
    originalrequest: bool = None
    forcebroadcast: bool = None
    updatecount: int = None
    system: ApplicationSystems
    originsystem: ApplicationSystems
    auditTrails: list = AuditTrails
