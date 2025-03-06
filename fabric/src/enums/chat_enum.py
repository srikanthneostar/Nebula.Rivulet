from enum import Enum

class ChatHistoryType(Enum):
    FILE = "file"
    REDIS = "redis"
    ELASTIC = "elastic"