#!/usr/bin/env python3
"""Tests for bin/public_check.py.

    python3 -m unittest discover -s bin/tests -v
    python3 bin/tests/test_public_check.py

Credential cases are assembled from fragments at runtime rather than stored as
fixture files, so no key-shaped bytes are ever committed.
"""
import os
import sys
import tempfile
import unittest

BIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(BIN)
sys.path.insert(0, BIN)

import public_check as pc  # noqa: E402

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

# Unsafe-shaped literals are assembled at runtime. Written out in full they would
# make this very file fail the repo-wide scan, which is the correct behaviour of
# the scanner and a bad property for a test.
SERIALS = ["X7K92" + "MNP4Q", "R4T88" + "WQZ2V6", "A1B2C3" + "D4E5F6"]
NOT_SERIALS = ["SHA256" + "SUMS", "CONTRI" + "BUTING", "0123456789" + "AB",
               "REA" + "DME", "ABCDE" + "FGHIJ", "HTTP2" + "SERVER"]
PRIVATE_DOMAIN = ".".join(("acmecorp", "io"))
PRIVATE_EMAIL = "hi@" + PRIVATE_DOMAIN
OTHER_EMAIL = "other@" + PRIVATE_DOMAIN
EMPLOYER = "Acme" + "Corp"
# Hostnames the rule must catch, assembled from bare labels so no matchable host
# literal exists in this file. Written out, they would make the test file itself
# fail the repo-wide scan.
INTERNAL_HOSTS = [".".join(parts) for parts in (
    ("wiki", "acme-internal", "acmeco", "com"),
    ("metrics", "corp", "acmeco", "net"),
    ("internalwiki", "acmeco", "org"),
    ("intranet", "acmeco", "com"),
    ("corp-build", "acmeco", "io"),
)]
# Ordinary and reserved hosts do not match, so they are safe to spell out.
ORDINARY_HOSTS = [PRIVATE_DOMAIN, "incorporated.io", "github.com",
                  "docs.example.com", "external.acmeco.com"]
RESERVED_HOSTS = ["wiki.internal.example.com", "intranet.example.org",
                  "build.corp.example.net"]


def scan(text, rules=None, relpath="sample.md", allowlist=None):
    return pc.scan_text(text, rules or pc.load_builtin(), relpath, allowlist or [])


def rule_ids(findings):
    return {f["rule"] for f in findings}


class CredentialRules(unittest.TestCase):
    """Built from fragments so the repo never stores a key-shaped literal."""

    def test_private_key_header(self):
        text = "-----BEGIN " + "RSA PRIVATE" + " KEY-----\nAAAA\n"
        self.assertIn("private-key", rule_ids(scan(text)))

    def test_cloud_access_key(self):
        text = "key: " + "AKIA" + "IOSFODNN7EXAMPLE"
        self.assertIn("aws-access-key", rule_ids(scan(text)))

    def test_hardcoded_credential(self):
        text = 'api_key = "' + "sk-live-" + '9f3ab2c7d5e1"'
        self.assertIn("credential-assignment", rule_ids(scan(text)))

    def test_bearer_header(self):
        text = "Authorization: " + "Bearer " + "eyJhbGciOiJIUzI1NiwidHlwIjoiSldU"
        self.assertIn("bearer-token", rule_ids(scan(text)))

    def test_placeholder_credentials_are_not_flagged(self):
        for value in ["<your-api-key>", "${DB_PASSWORD}", "changeme", "example", "xxxxxxxx"]:
            text = 'password = "%s"' % value
            self.assertNotIn("credential-assignment", rule_ids(scan(text)),
                             "placeholder should not flag: %s" % value)


class FixtureFiles(unittest.TestCase):
    def _scan_file(self, group, name):
        path = os.path.join(FIXTURES, group, name)
        with open(path, encoding="utf-8") as f:
            return scan(f.read(), relpath="%s/%s" % (group, name))

    def test_internal_infra_fixture(self):
        found = rule_ids(self._scan_file("should_fail", "internal_infra.md"))
        for expected in ("internal-hostname", "internal-tld", "dev-host-id", "absolute-home-path"):
            self.assertIn(expected, found)

    def test_identifiers_fixture(self):
        found = rule_ids(self._scan_file("should_fail", "identifiers.md"))
        for expected in ("machine-serial", "ticket-id", "long-numeric-id", "corporate-email"):
            self.assertIn(expected, found)

    def test_benign_fixture_is_clean(self):
        findings = self._scan_file("should_pass", "benign.md")
        self.assertEqual([], findings, "false positives: %s" % [
            (f["rule"], f["match"]) for f in findings])

    def test_warn_fixture_warns_without_erroring(self):
        findings = self._scan_file("should_warn", "certs.md")
        self.assertTrue(findings)
        self.assertEqual({pc.WARN}, {f["severity"] for f in findings})


class SerialShape(unittest.TestCase):
    def test_accepts_serial_shapes(self):
        for s in SERIALS:
            self.assertTrue(pc._looks_like_serial(s), s)

    def test_rejects_lookalikes(self):
        for s in NOT_SERIALS:
            self.assertFalse(pc._looks_like_serial(s), s)


class HostnameRule(unittest.TestCase):
    def test_flags_internal_hosts(self):
        for host in INTERNAL_HOSTS:
            self.assertIn("internal-hostname", rule_ids(scan("see %s today" % host)), host)

    def test_does_not_flag_ordinary_hosts(self):
        for host in ORDINARY_HOSTS:
            self.assertNotIn("internal-hostname", rule_ids(scan("see %s today" % host)), host)

    def test_does_not_flag_reserved_documentation_domains(self):
        for host in RESERVED_HOSTS:
            self.assertNotIn("internal-hostname", rule_ids(scan("see %s today" % host)), host)


class Allowlist(unittest.TestCase):
    def test_exact_match_is_suppressed(self):
        entries = [{"glob": "docs/*.md", "rule": "corporate-email",
                    "text": PRIVATE_EMAIL, "reason": "sample"}]
        text = "write to %s" % PRIVATE_EMAIL
        self.assertEqual([], scan(text, relpath="docs/a.md", allowlist=entries))

    def test_other_paths_still_flag(self):
        entries = [{"glob": "docs/*.md", "rule": "corporate-email",
                    "text": PRIVATE_EMAIL, "reason": "sample"}]
        text = "write to %s" % PRIVATE_EMAIL
        self.assertIn("corporate-email", rule_ids(scan(text, relpath="src/a.md", allowlist=entries)))

    def test_different_text_still_flags(self):
        entries = [{"glob": "*", "rule": "corporate-email",
                    "text": PRIVATE_EMAIL, "reason": "sample"}]
        text = "write to %s" % OTHER_EMAIL
        self.assertIn("corporate-email", rule_ids(scan(text, allowlist=entries)))

    def test_repo_allowlist_parses(self):
        entries = pc.load_allowlist(os.path.join(BIN, "rules", "allowlist.tsv"))
        for e in entries:
            self.assertTrue(e["reason"], "allowlist entry without a reason: %s" % e)


class ExtraRulesFile(unittest.TestCase):
    def test_loads_and_applies(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("# comment\n\nERROR\temployer-name\t\\b%s\\b\temployer name\n" % EMPLOYER)
            path = f.name
        try:
            rules = pc.load_builtin() + pc.load_rules_file(path)
            self.assertIn("employer-name", rule_ids(scan("built at %s today" % EMPLOYER, rules)))
            self.assertEqual([], scan("built at a company today", rules))
        finally:
            os.unlink(path)

    def test_example_denylist_parses(self):
        rules = pc.load_rules_file(os.path.join(BIN, "rules", "denylist.example.txt"))
        self.assertTrue(rules)
        self.assertIn("employer-name", {r.rule_id for r in rules})

    def test_bad_rules_file_is_rejected(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("NOPE\tid\tregex\tmsg\n")
            path = f.name
        try:
            with self.assertRaises(SystemExit):
                pc.load_rules_file(path)
        finally:
            os.unlink(path)


class RepoGuards(unittest.TestCase):
    def test_gitignore_protects_every_private_dir(self):
        self.assertIsNone(pc.check_gitignore(REPO))

    def test_gitignore_gap_is_reported(self):
        """The skip is only safe while the ignore holds, so a gap must fail."""
        for gap in sorted(pc.PRIVATE_DIRS):
            with tempfile.TemporaryDirectory() as d:
                kept = [x for x in sorted(pc.PRIVATE_DIRS) if x != gap]
                with open(os.path.join(d, ".gitignore"), "w", encoding="utf-8") as f:
                    f.write("".join("%s/\n" % x for x in kept))
                problem = pc.check_gitignore(d)
                self.assertIsNotNone(problem, "missing %s should fail" % gap)
                self.assertIn(gap, problem)

    def test_missing_gitignore_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNotNone(pc.check_gitignore(d))

    def test_private_dirs_are_never_scanned(self):
        scanned = list(pc.iter_files([REPO]))
        for d in pc.PRIVATE_DIRS:
            self.assertFalse([p for p in scanned if os.sep + d + os.sep in p],
                             "%s must not be scanned" % d)

    def test_fixtures_are_never_scanned_repo_wide(self):
        scanned = list(pc.iter_files([REPO]))
        self.assertFalse([p for p in scanned if os.sep + "fixtures" + os.sep in p])

    def test_rule_definitions_are_never_scanned_repo_wide(self):
        scanned = list(pc.iter_files([REPO]))
        rules_dir = os.path.join(BIN, "rules") + os.sep
        self.assertFalse([p for p in scanned if os.path.abspath(p).startswith(rules_dir)])

    def test_tracked_tree_is_publishable(self):
        findings = pc.scan_paths([REPO], pc.load_builtin(), pc.load_allowlist(
            os.path.join(BIN, "rules", "allowlist.tsv")), base=REPO)
        errors = [f for f in findings if f["severity"] == pc.ERROR]
        self.assertEqual([], errors, "tracked tree is not publishable: %s" % [
            (f["path"], f["line"], f["rule"], f["match"]) for f in errors])

    def test_scanned_set_covers_every_trackable_file(self):
        """A skip that hides a file git would happily commit is the failure mode.

        Ask git for the files a push could carry, and require the scanner to
        have looked at every text one of them.
        """
        import subprocess
        out = subprocess.run(
            ["git", "-C", REPO, "ls-files", "-z", "--cached", "--others",
             "--exclude-standard"],
            capture_output=True, check=True)
        trackable = {p for p in out.stdout.decode().split("\0") if p}
        scanned = {os.path.relpath(p, REPO) for p in pc.iter_files([REPO])}
        missed = sorted(
            p for p in trackable - scanned
            if os.path.splitext(p)[1].lower() not in pc.BINARY_EXT
            and os.path.basename(p) not in pc.SKIP_FILES
            and "fixtures" + os.sep not in p
            and not p.startswith("bin" + os.sep + "rules" + os.sep)
            and os.path.isfile(os.path.join(REPO, p))
            and not os.path.islink(os.path.join(REPO, p)))
        self.assertEqual([], missed, "trackable but unscanned: %s" % missed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
