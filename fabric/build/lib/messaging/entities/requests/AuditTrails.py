from datetime import datetime
from messaging.entities.enum.AuditStatus import AuditStatus
from messaging.entities.enum.RuleAction import RuleAction

class AuditTrails(object):
    def default(self, o):
        return o.__dict__
    
    id:int = None
    requestid:int = None
    auditid:int = None
    actiontype:RuleAction
    rulename:str = None
    status:AuditStatus
    fields:str = None
    ruleobject:str = None
    ruleobjectvalue:str = None
    createondate:str = datetime.now()
    modifyondate:str = datetime.now()