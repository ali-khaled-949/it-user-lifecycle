# it-user-lifecycle

Onboarding and offboarding plans for IT accounts, plus an access audit that finds drift.

- **Onboarding:** a role-to-access matrix turns a new hire into an ordered list of steps: create the account, require MFA enrollment, assign licenses, add groups, notify the manager. An unknown role is rejected, not guessed.
- **Offboarding:** access is cut first (disable sign-in, revoke sessions), then groups are removed, the mailbox is handed over, licenses are reclaimed, and the account is archived. The order is tested.
- **Access audit:** compares each user's groups to their role profile and reports extra groups, missing groups, unknown roles, and enabled accounts with no sign-in for 90 days.

The directory is a plain dictionary standing in for Active Directory or Microsoft Entra ID. Plans are lists of actions to review, so nothing here changes a real system on its own. Connecting it to Graph or PowerShell is the next step.

## Limits

Small synthetic data and a three-role matrix. This shows the method, not a production tool. No third-party packages, Python 3.10 or newer.

## Run

```bash
python3 -m unittest
```

Files: `lifecycle.py`, `test_lifecycle.py`
