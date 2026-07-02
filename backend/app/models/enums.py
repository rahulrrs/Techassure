from enum import StrEnum


class Role(StrEnum):
    admin = "Admin"
    auditor = "Auditor"
    manager = "Manager"


class Severity(StrEnum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class FindingStatus(StrEnum):
    open = "Open"
    in_progress = "In Progress"
    remediated = "Remediated"
    accepted = "Accepted"
