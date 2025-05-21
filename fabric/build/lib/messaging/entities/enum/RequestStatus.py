from enum import Enum

class RequestStatus(Enum):
    Pending = 1
    Completed = 2
    Failure = 3
    Cancelled = 4
    Applied = 5
