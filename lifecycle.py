"""IT user lifecycle: onboarding and offboarding plans, plus an access audit that finds drift.

The directory is a plain dict, a stand-in for Active Directory / Microsoft Entra ID. Plans are lists of actions, so a
person (or a script wired to the real directory) can review them before anything changes.
"""
from dataclasses import dataclass
from datetime import date, timedelta

# Role -> access every person in that role should have.
MATRIX = {
    "sales": {"groups": {"All Staff", "Sales", "CRM Users"}, "licenses": {"M365 Business Standard"}},
    "engineer": {"groups": {"All Staff", "Engineering", "VPN Users"}, "licenses": {"M365 Business Premium"}},
    "finance": {"groups": {"All Staff", "Finance", "Finance Share"}, "licenses": {"M365 Business Standard"}},
}


@dataclass
class Employee:
    username: str
    role: str
    manager: str


def plan_onboarding(emp: Employee, matrix: dict = MATRIX) -> list[str]:
    if emp.role not in matrix:
        raise ValueError(f"no access profile for role '{emp.role}'")
    access = matrix[emp.role]
    steps = [f"create account {emp.username}", "require MFA enrollment at first sign-in"]
    steps += [f"assign license: {lic}" for lic in sorted(access["licenses"])]
    steps += [f"add to group: {g}" for g in sorted(access["groups"])]
    steps.append(f"notify manager {emp.manager}")
    return steps


def plan_offboarding(username: str, groups: set[str], licenses: set[str], mailbox_owner: str) -> list[str]:
    """Order matters: cut access first, then reclaim licenses, then hand over data."""
    steps = [f"disable sign-in for {username}", f"revoke active sessions and tokens for {username}"]
    steps += [f"remove from group: {g}" for g in sorted(groups)]
    steps.append(f"convert mailbox to shared and grant access to {mailbox_owner}")
    steps += [f"remove license: {lic}" for lic in sorted(licenses)]
    steps.append(f"archive account {username} after retention review")
    return steps


def audit_access(directory: dict, matrix: dict = MATRIX, today: date | None = None, stale_days: int = 90) -> list[str]:
    """directory: username -> {role, groups, enabled, last_signin (date)}. Returns findings, one per issue."""
    today = today or date.today()
    findings = []
    for user, info in sorted(directory.items()):
        expected = matrix.get(info["role"], {}).get("groups")
        if expected is None:
            findings.append(f"{user}: unknown role '{info['role']}'")
            continue
        for g in sorted(info["groups"] - expected):
            findings.append(f"{user}: extra group '{g}' not in {info['role']} profile")
        for g in sorted(expected - info["groups"]):
            findings.append(f"{user}: missing group '{g}'")
        if info["enabled"] and today - info["last_signin"] > timedelta(days=stale_days):
            findings.append(f"{user}: enabled but no sign-in for {(today - info['last_signin']).days} days")
    return findings
