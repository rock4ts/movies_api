# Must match Auth service AccessLabel enum.
from enum import StrEnum


class AccessLabel(StrEnum):
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"
