from enum import Enum

class SyncStatus(str, Enum):
    PENDING = "pending"
    SYNCED = "synced"
    CONFLICT = "conflict"
    FAILED = "failed"

class ActivityType(str, Enum):
    SLEEP = "sleep"
    FEED = "feed"
    DIAPER = "diaper"
    OTHER = "other"

class CareTeamRole(str, Enum):
    PRIMARY = "primary"
    COPARENT = "coparent"