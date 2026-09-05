#!/usr/bin/env python3
"""Fail the build when tracked content is not safe to publish.

    python3 bin/public_check.py [PATH ...]
    python3 bin/public_check.py --rules /path/to/extra_denylist.txt
    python3 bin/public_check.py --strict        # warnings fail too
    python3 bin/public_check.py --list-rules

Design
------
The built-in rules are deliberately company-agnostic. They match SHAPES that are
unsafe anywhere: private keys, credential assignments, absolute home directories,
hardware serials, ticket ids, internal-looking hostnames.

A repo-wide run scans the trackable surface. Directories that are gitignored
because they hold private material (PRIVATE_DIRS) are skipped and their ignore
status is verified instead, so the run reports what a push could actually carry.

Anything specific to one employer (its internal domains, repo names, product
codenames, colleague names) must NOT live in a public repo, so it is not hardcoded
here. Keep those patterns in a private rules file outside version control and pass
it with --rules. `bin/rules/denylist.example.txt` shows the format.

False positives are a real cost: a check people mute is a check that does not run.
Every rule below is either shape-tight or warning-tier, and `bin/rules/allowlist.tsv`
records reviewed exceptions with a reason.
"""
import argparse
import fnmatch
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

ERROR, WARN = "ERROR", "WARN"

# Directories that hold private material by design and are gitignored for that
# reason: private originals and adapters, rollback snapshots from a payload
# merge, quarantined incoming copies, and the backups the installer leaves
# behind. None of them is trackable, so scanning them reports findings that no
# push could ever carry.
#
# The skip is only safe while git actually ignores them, so check_gitignore()
# verifies every entry. An unignored one is an error, not a silent hole.
PRIVATE_DIRS = {".local-meta", ".merge-backups", ".incoming", "backups"}

# Directories never scanned during a repo-wide run.
#  PRIVATE_DIRS  gitignored, private by design, see above
#  fixtures      test data that is unsafe on purpose, so the tests have something to catch
# A fixture directory passed explicitly on the command line is still scanned,
# which is how the test suite drives it.
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "fixtures",
} | PRIVATE_DIRS
SKIP_FILES = {".DS_Store"}
# Rule and allowlist files quote the very strings they exist to block, so scanning
# them reports the definitions as findings. They are reviewed by reading them.
SKIP_PATHS = {os.path.join(REPO, "bin", "rules")}
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".gz", ".tgz",
    ".ico", ".woff", ".woff2", ".ttf", ".mp4", ".mov", ".lock",
}

# Placeholder shapes that make a credential-looking match harmless.
PLACEHOLDER = re.compile(
    r"(?i)^(?:<[^>]*>|\$\{?[a-z_][a-z0-9_]*\}?|x{3,}|\.{3,}|"
    r"your[_-]?\w*|my[_-]?\w*|some[_-]?\w*|example\w*|sample\w*|dummy\w*|"
    r"changeme|redacted|placeholder|todo|fixme|abc123|test\w*|fake\w*|none|null)$"
)

# Hosts that are public by definition.
PUBLIC_EMAIL_DOMAINS = {
    "example.com", "example.org", "example.net", "github.com",
    "users.noreply.github.com", "localhost",
}


def _looks_like_serial(text):
    """Hardware-serial shape: 10-12 uppercase alnum, mixed, no long letter runs.

    Tight on purpose. 'SHA256SUMS' has a four-letter run and is rejected;
    'CONTRIBUTING' has no digits; '0123456789AB' has too few letters.
    """
    if not re.fullmatch(r"[A-Z0-9]{10,12}", text):
        return False
    digits = sum(c.isdigit() for c in text)
    letters = sum(c.isalpha() for c in text)
    if digits < 3 or letters < 3:
        return False
    longest = max((len(m) for m in re.findall(r"[A-Z]+", text)), default=0)
    return longest <= 3


def _real_email(text):
    domain = text.rsplit("@", 1)[-1].lower()
    return domain not in PUBLIC_EMAIL_DOMAINS


# RFC 2606 / RFC 6761 reserved names. A host under one of these is documentation,
# never a real internal service, so flagging it is pure noise.
RESERVED_DOMAINS = ("example.com", "example.net", "example.org")
RESERVED_TLDS = (".example", ".test", ".invalid", ".localhost")


def _real_internal_host(text):
    host = text.lower().rstrip(".")
    if host in RESERVED_DOMAINS or host.endswith(tuple("." + d for d in RESERVED_DOMAINS)):
        return False
    return not host.endswith(RESERVED_TLDS)


def _real_secret(match_text):
    value = re.split(r"[:=]", match_text, maxsplit=1)[-1].strip().strip("'\"")
    return not PLACEHOLDER.match(value)


BUILTIN_RULES = [
    # (severity, rule_id, pattern, message, predicate over the matched text)
    (ERROR, "private-key",
     r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----",
     "private key material", None),
    (ERROR, "aws-access-key",
     r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
     "cloud access key id", None),
    (ERROR, "credential-assignment",
     r"(?i)\b(?:api[_-]?key|secret|secret[_-]?key|password|passwd|client[_-]?secret|access[_-]?token|auth[_-]?token)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
     "hardcoded credential", _real_secret),
    (ERROR, "bearer-token",
     r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._\-]{16,}",
     "bearer token", None),
    # "internal"/"intranet" may prefix a label (internalwiki at some company) but
    # "corp" must be a whole label or a dash-delimited part, so ordinary names
    # like the acme-corp example in the tests do not flag. Reserved documentation
    # domains are exempt via the predicate.
    (ERROR, "internal-hostname",
     r"\b(?:[a-z0-9-]+\.)*(?:(?:[a-z0-9]+-)*(?:internal|intranet)[a-z0-9]*|(?:[a-z0-9]+-)*corp(?:-[a-z0-9]+)*)(?:\.[a-z0-9-]+)*\.(?:com|net|org|io|dev|co)\b",
     "internal-looking hostname", _real_internal_host),
    (ERROR, "internal-tld",
     r"\bhttps?://[a-z0-9.-]+\.(?:internal|corp|intranet|local)\b",
     "internal-only URL", None),
    (ERROR, "dev-host-id",
     r"\b(?:devvm|devbox|devserver|workstation|jumpbox)\d{2,}\b",
     "named development host", None),
    (ERROR, "absolute-home-path",
     r"/(?:Users|home)/(?!you\b|user\b|username\b|me\b|example\b|someone\b|<)[A-Za-z0-9._-]{2,}",
     "absolute home directory with a real account name", None),
    (ERROR, "machine-serial",
     r"\b[A-Z0-9]{10,12}\b",
     "hardware serial number", lambda t: _looks_like_serial(t)),
    (ERROR, "ticket-id",
     r"\b[A-Z]{1,3}\d{6,}\b",
     "internal ticket or revision id", None),
    (ERROR, "long-numeric-id",
     r"\b\d{15,}\b",
     "long numeric id (account, object, or user id)", None),
    (ERROR, "corporate-email",
     r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
     "email address", _real_email),
    (WARN, "certificate-path",
     r"/(?:var|etc|opt)/[A-Za-z0-9._/-]*(?:credentials|certs?|x509)[A-Za-z0-9._/-]*",
     "credential or certificate path", None),
    (WARN, "pem-file",
     r"\b[A-Za-z0-9._-]+\.pem\b",
     "certificate file reference", None),
]


class Rule:
    def __init__(self, severity, rule_id, pattern, message, predicate=None, source="builtin"):
        self.severity = severity
        self.rule_id = rule_id
        self.regex = re.compile(pattern)
        self.message = message
        self.predicate = predicate
        self.source = source


def load_builtin():
    return [Rule(s, i, p, m, pred) for s, i, p, m, pred in BUILTIN_RULES]


def load_rules_file(path):
    """severity<TAB>rule-id<TAB>regex<TAB>message, '#' comments, blank lines ignored."""
    rules = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            parts = [p for p in parts if p != ""]
            if len(parts) < 3:
                raise SystemExit("%s:%d: need severity, rule-id, regex [, message]" % (path, lineno))
            severity, rule_id, pattern = parts[0].strip(), parts[1].strip(), parts[2]
            message = parts[3].strip() if len(parts) > 3 else rule_id
            if severity not in (ERROR, WARN):
                raise SystemExit("%s:%d: severity must be ERROR or WARN" % (path, lineno))
            try:
                rules.append(Rule(severity, rule_id, pattern, message, None, source=path))
            except re.error as exc:
                raise SystemExit("%s:%d: bad regex: %s" % (path, lineno, exc))
    return rules


def load_allowlist(path):
    """path-glob<TAB>rule-id<TAB>matched-text<TAB>reason"""
    entries = []
    if not os.path.isfile(path):
        return entries
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            parts = [p for p in parts if p != ""]
            if len(parts) < 3:
                continue
            entries.append({
                "glob": parts[0].strip(),
                "rule": parts[1].strip(),
                "text": parts[2].strip(),
                "reason": parts[3].strip() if len(parts) > 3 else "",
            })
    return entries


def allowed(entries, relpath, rule_id, text):
    for e in entries:
        if e["rule"] != rule_id:
            continue
        if not fnmatch.fnmatch(relpath, e["glob"]):
            continue
        if e["text"] == "*" or e["text"] == text:
            return True
    return False


def _skipped_path(path):
    ap = os.path.abspath(path)
    return any(ap == s or ap.startswith(s + os.sep) for s in SKIP_PATHS)


def iter_files(roots):
    for root in roots:
        if os.path.isfile(root):
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d not in SKIP_DIRS and not _skipped_path(os.path.join(dirpath, d))]
            for fn in sorted(filenames):
                if fn in SKIP_FILES:
                    continue
                if os.path.splitext(fn)[1].lower() in BINARY_EXT:
                    continue
                full = os.path.join(dirpath, fn)
                if _skipped_path(full):
                    continue
                if os.path.islink(full) or not os.path.isfile(full):
                    continue
                yield full


def scan_text(text, rules, relpath, allowlist):
    findings = []
    for rule in rules:
        for m in rule.regex.finditer(text):
            matched = m.group(0)
            if rule.predicate and not rule.predicate(matched):
                continue
            if allowed(allowlist, relpath, rule.rule_id, matched):
                continue
            line = text.count("\n", 0, m.start()) + 1
            findings.append({
                "path": relpath,
                "line": line,
                "rule": rule.rule_id,
                "severity": rule.severity,
                "message": rule.message,
                "match": matched if len(matched) <= 60 else matched[:57] + "...",
            })
    return findings


def scan_paths(roots, rules, allowlist, base=None):
    base = base or REPO
    findings = []
    for full in iter_files(roots):
        try:
            with open(full, encoding="utf-8") as f:
                text = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        relpath = os.path.relpath(full, base)
        findings.extend(scan_text(text, rules, relpath, allowlist))
    findings.sort(key=lambda f: (f["path"], f["line"], f["rule"]))
    return findings


def check_gitignore(repo):
    """Every PRIVATE_DIRS entry must be ignored, or private material is publishable.

    The scan skips those directories, so an entry that stopped being ignored
    would be both unscanned and committable. Fail instead.
    """
    listed = ", ".join(sorted(PRIVATE_DIRS))
    gi = os.path.join(repo, ".gitignore")
    if not os.path.isfile(gi):
        return ".gitignore is missing, so these are not protected: %s" % listed
    with open(gi, encoding="utf-8") as f:
        ignored = {line.strip().rstrip("/") for line in f}
    missing = sorted(d for d in PRIVATE_DIRS if d not in ignored)
    if missing:
        return ".gitignore does not ignore: %s" % ", ".join(missing)
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="fail tracked content that is not safe to publish")
    ap.add_argument("paths", nargs="*", default=None, help="paths to scan (default: the repo root)")
    ap.add_argument("--rules", action="append", default=[], help="extra denylist file (repeatable)")
    ap.add_argument("--allowlist", default=os.path.join(HERE, "rules", "allowlist.tsv"))
    ap.add_argument("--strict", action="store_true", help="warnings fail the run too")
    ap.add_argument("--list-rules", action="store_true")
    ap.add_argument("--base", default=None, help="base directory for reported paths")
    args = ap.parse_args(argv)

    rules = load_builtin()
    for rf in args.rules:
        rules.extend(load_rules_file(rf))

    if args.list_rules:
        for r in rules:
            print("%-6s %-24s %s" % (r.severity, r.rule_id, r.message))
        return 0

    roots = args.paths or [REPO]
    base = args.base or (REPO if not args.paths else os.path.commonpath(
        [os.path.abspath(p) for p in roots] * 2))
    allowlist = load_allowlist(args.allowlist)
    findings = scan_paths(roots, rules, allowlist, base=base)

    gi_problem = None
    if not args.paths:
        gi_problem = check_gitignore(REPO)
        if gi_problem:
            findings.append({
                "path": ".gitignore", "line": 0, "rule": "private-dir-not-ignored",
                "severity": ERROR, "message": gi_problem, "match": "",
            })

    errors = [f for f in findings if f["severity"] == ERROR]
    warns = [f for f in findings if f["severity"] == WARN]

    for f in findings:
        print("%s:%d: %s [%s] %s" % (
            f["path"], f["line"], f["severity"], f["rule"],
            (f["match"] or f["message"])))

    print("\n%d error(s), %d warning(s) over %d rule(s)" % (len(errors), len(warns), len(rules)))
    if errors:
        return 1
    if warns and args.strict:
        return 1
    print("public check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
