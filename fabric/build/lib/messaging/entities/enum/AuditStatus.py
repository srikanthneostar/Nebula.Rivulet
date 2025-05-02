from enum import Enum

class AuditStatus(Enum):
    Pending = 1
    Failure = 2
    Cancelled = 3
    Applied = 4