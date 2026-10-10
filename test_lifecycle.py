import unittest
from datetime import date

from lifecycle import Employee, audit_access, plan_offboarding, plan_onboarding

TODAY = date(2026, 10, 10)


class LifecycleTests(unittest.TestCase):
    def test_onboarding_creates_account_then_access(self):
        steps = plan_onboarding(Employee("jdoe", "engineer", "mlee"))
        self.assertEqual(steps[0], "create account jdoe")
        self.assertIn("add to group: VPN Users", steps)
        self.assertIn("assign license: M365 Business Premium", steps)
        self.assertEqual(steps[-1], "notify manager mlee")

    def test_unknown_role_is_rejected(self):
        with self.assertRaises(ValueError):
            plan_onboarding(Employee("x", "intern", "m"))

    def test_offboarding_cuts_access_before_reclaiming_licenses(self):
        steps = plan_offboarding("jdoe", {"Engineering", "All Staff"}, {"M365 Business Premium"}, "mlee")
        self.assertTrue(steps[0].startswith("disable sign-in"))
        self.assertLess(steps.index("remove from group: Engineering"), steps.index("remove license: M365 Business Premium"))
        self.assertTrue(steps[-1].startswith("archive account"))

    def test_audit_finds_extra_missing_and_stale(self):
        directory = {
            "ann": {"role": "sales", "groups": {"All Staff", "Sales", "CRM Users"}, "enabled": True, "last_signin": date(2026, 10, 1)},
            "bob": {"role": "sales", "groups": {"All Staff", "Finance Share"}, "enabled": True, "last_signin": date(2026, 5, 1)},
            "cy": {"role": "janitor", "groups": set(), "enabled": True, "last_signin": TODAY},
        }
        found = audit_access(directory, today=TODAY)
        self.assertNotIn("ann", " ".join(found))
        self.assertIn("bob: extra group 'Finance Share' not in sales profile", found)
        self.assertIn("bob: missing group 'CRM Users'", found)
        self.assertTrue(any(f.startswith("bob: enabled but no sign-in") for f in found))
        self.assertIn("cy: unknown role 'janitor'", found)

    def test_disabled_stale_account_is_not_flagged_as_stale(self):
        directory = {"dee": {"role": "finance", "groups": {"All Staff", "Finance", "Finance Share"}, "enabled": False, "last_signin": date(2025, 1, 1)}}
        self.assertEqual(audit_access(directory, today=TODAY), [])


if __name__ == "__main__":
    unittest.main()
