from enum import Enum

class RuleAction(Enum):
    BROADCAST = 1
    PROCEDURE = 2
    MANAGERTASK = 3
    TASK = 4
    EMAIL = 5
    ASSEMBLY = 6
    ENTITYCHANGES = 7