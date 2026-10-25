#!/usr/bin/env python3
"""souji-receipt-run.py — blob-bound receipts (round 23, C2).

A counter run is only evidence if the bytes that produced it are pinned. This runner
re-derives a command at a named, durable revision and writes a receipt that binds the
revision, the tool path, the tool's sha256 AT THAT REVISION, the command, its exit code and
its output. `verify` re-reads the same bytes from git and refuses a receipt whose recorded
digest is not the committed blob at the named revision.

  run    --root <repo> --rev <full40> --tool <repo-relative> --out <abs path> -- <cmd...>
  verify --root <repo> <receipt>

Receipt v1 header, in this order, then the two fences:

  receipt=v1
  rev=<40 hex>
  tool=<repo-relative path>
  tool_sha256=<64 hex>
  cmd=<shell-quoted argv>
  rc=<int>
  utc=<ISO 8601>
  --- stdout ---
  <verbatim>
  --- stderr ---
  <verbatim>

Refusals (exit 2, no receipt written): --rev not a full 40-hex id; --rev not reachable from
refs/heads, refs/tags or refs/remotes (refs/jj/* never counts — Q37); --tool absent at --rev;
--out under /tmp (Q4); --out inside --root (a receipt is not a repo write).
`verify` exits 2 with one of: RECEIPT-MALFORMED, RECEIPT-TOOL-DIGEST-MISMATCH,
RECEIPT-TOOL-ABSENT, RECEIPT-REV-MALFORMED, RECEIPT-COUNTS-ABSENT.

The measured tree is a private `--no-local` clone under /var/tmp, checked out detached at <rev>:
the runner never writes the source repository and never fetches from a remote. It is a counter
runner, not a sandbox and not a proof that the command is side-effect free — the receipt records
what ran.

Frozen contract: .ufo/waves/round-23/preregistration.txt (C2).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
import shlex
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
import tempfile

SCRATCH_ROOT = "/var/tmp"
COUNTS_RE = re.compile(
    r"(?:assertions=\d+ resolved=\d+ skipped=\d+ mismatches=\d+"
    r"|keys=\d+ records=\d+ occurrences=\d+ mismatches=\d+"
    r"|entries=\d+ ok=\d+.*?fail=\d+)"
)
REV_RE = re.compile(r"^[0-9a-f]{40}$")
HEADER_ORDER = ("receipt", "rev", "tool", "tool_sha256", "cmd", "rc", "utc")


# ported from tools/souji-proc-census.sh redact_secrets: one convention, not a second one
REDACTIONS = (
    (re.compile(r"(?i)(authorization:\s*bearer\s+)\S+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(--token=)\S+"), r"\1[REDACTED]"),
    (re.compile(r"ghp_[A-Za-z0-9_-]+"), "[REDACTED]"),
    (re.compile(r"sk-[A-Za-z0-9_.-]+"), "[REDACTED]"),
    (re.compile(r"(?i)(password=)\S+"), r"\1[REDACTED]"),
    (re.compile(r"([A-Za-z][A-Za-z0-9.+-]*://)[^/@\s]*@"), r"\1[REDACTED]@"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED]"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9_.-]+"), "[REDACTED]"),
)
CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def redact(text: str) -> str:
    """Redact secret-shaped spans. Not a proof that the output is secret-free."""
    out = CTRL_RE.sub(" ", text)
    for pattern, repl in REDACTIONS:
        out = pattern.sub(repl, out)
    return out


DENY_SUBCOMMANDS = {
    "fsck-lost-found", "gc", "prune", "repack", "fetch", "push", "pull", "clean",
    "checkout", "reset", "restore", "switch", "filter-branch", "lost-found",
}


def command_refusal(argv: list[str]) -> str | None:
    """Refuse the measured command shapes that would defeat the scratch cwd."""
    if not argv:
        return None
    if os.path.basename(argv[0]) != "git":
        return None
    if "-C" in argv or "--git-dir" in argv or "--work-tree" in argv:
        return "GIT-DIRECTED-COMMAND: a -C/--git-dir/--work-tree command escapes the measured tree"
    if "--lost-found" in argv:
        return "WRITE-SIDE-EFFECT: git fsck --lost-found writes into the repository"
    # every token, not only the first non-dash one: `git -c k=v gc` must not slip through
    for token in argv[1:]:
        if token in DENY_SUBCOMMANDS:
            return f"MUTATING-SUBCOMMAND: git {token} is not a counter"
    return None


def git(root: str, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "core.fsmonitor"
    env["GIT_CONFIG_VALUE_0"] = "false"
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    return subprocess.run(["git", "-C", root, "-c", "maintenance.auto=false", *args],
                          capture_output=True, text=True, env=env)


def refuse(code: str, detail: str) -> int:
    print(f"{code}\t{detail}", file=sys.stderr)
    return 2


def durable_rev(root: str, rev: str) -> bool:
    """True when rev is a commit reachable from a durable ref (never refs/jj/*)."""
    proc = git(root, "for-each-ref", "--format=%(refname)", "--contains", rev,
               "refs/heads", "refs/tags", "refs/remotes")
    return proc.returncode == 0 and bool(proc.stdout.strip())


def blob_sha_bytes(root: str, rev: str, path: str) -> str | None:
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    proc = subprocess.run(["git", "-C", root, "-c", "maintenance.auto=false",
                           "cat-file", "blob", f"{rev}:{path}"],
                          capture_output=True, env=env)
    if proc.returncode != 0:
        return None
    return hashlib.sha256(proc.stdout).hexdigest()


def cmd_run(args: argparse.Namespace) -> int:
    root = os.path.abspath(args.root)
    rev = args.rev
    if not REV_RE.match(rev or ""):
        return refuse("REV-MALFORMED", "--rev must be a full 40-hex commit id")
    if git(root, "cat-file", "-e", f"{rev}^{{commit}}").returncode != 0:
        return refuse("REV-ABSENT", f"no commit {rev}")
    if not durable_rev(root, rev):
        return refuse("REV-NOT-DURABLE", f"{rev} is not reachable from refs/heads|tags|remotes")
    tool = args.tool
    if blob_sha_bytes(root, rev, tool) is None:
        return refuse("TOOL-ABSENT", f"{tool} does not exist at {rev}")
    out = os.path.realpath(args.out)
    if out.startswith("/tmp/") or out == "/tmp":
        return refuse("OUT-UNDER-TMP", "receipts go outside /tmp (Q4)")
    if out == root or out.startswith(root + os.sep):
        return refuse("OUT-IN-REPO", "the receipt must not be written inside the measured repo")
    if not args.command:
        return refuse("COMMAND-ABSENT", "nothing to run after --")
    why = command_refusal(args.command)
    if why:
        return refuse(why.split(":", 1)[0], why.split(":", 1)[1].strip())
    for protected in ("/.ufo/state/", "/.tower/", "/.scratch/", "/MANIFEST.json"):
        if protected in out:
            return refuse("OUT-PROTECTED", f"{protected} is operator or orchestrator runtime")
    if re.search(r"/[A-Za-z0-9_-]+-shokunin/", out) and not out.startswith(root + os.sep):
        return refuse("OUT-SIBLING-LANE", "a receipt is never written into another lane")

    scratch = tempfile.mkdtemp(prefix="souji-receipt-", dir=SCRATCH_ROOT)
    tree = os.path.join(scratch, "repo")
    try:
        # a private local clone: the measured tree is a real repository at <rev>, so a counter
        # that needs git plumbing works, and the source repo is only read
        clone = subprocess.run(["git", "clone", "--quiet", "--no-local", "--no-checkout",
                                root, tree], capture_output=True, text=True)
        if clone.returncode != 0:
            return refuse("CLONE-FAILED", clone.stderr.strip())
        # sparse-checkout: the lane's operator-sweep blob tree is bound materialized in the clone
        # (W2Bounds F1) — the receipt run must not copy those contents, even transiently
        sp = subprocess.run(["git", "-C", tree, "-c", "maintenance.auto=false",
                             "sparse-checkout", "init", "--no-cone"],
                            capture_output=True, text=True)
        if sp.returncode != 0:
            return refuse("SPARSE-INIT-FAILED", sp.stderr.strip())
        with open(os.path.join(tree, ".git", "info", "sparse-checkout"), "w") as fh:
            fh.write("/*")
            fh.write(chr(10))
            fh.write("!/census/operator-sweep-*")
            fh.write(chr(10))

        co = subprocess.run(["git", "-C", tree, "-c", "maintenance.auto=false",
                             "checkout", "--quiet", "--detach", rev],
                            capture_output=True, text=True)
        if co.returncode != 0:
            return refuse("CHECKOUT-FAILED", co.stderr.strip())
        run_env = {k: v for k, v in os.environ.items()
                   if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
        run_env["GIT_OPTIONAL_LOCKS"] = "0"
        run_env["GIT_NO_REPLACE_OBJECTS"] = "1"
        run_env["GIT_NO_LAZY_FETCH"] = "1"
        # the digest is taken from the tree the command runs in, never from a second read of
        # the source repo (a refs/replace ref makes the two disagree)
        try:
            with open(os.path.join(tree, tool), "rb") as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()
        except OSError as exc:
            return refuse("TOOL-UNREADABLE", f"{tool} in the measured tree: {exc}")
        # errors="replace": a non-UTF-8 byte must produce a receipt with a recorded
        # replacement, not an exception that leaves no evidence at all
        proc = subprocess.run(args.command, cwd=tree, capture_output=True, text=True,
                              errors="replace", env=run_env)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    lines = [
        "receipt=v1",
        f"rev={rev}",
        f"tool={tool}",
        f"tool_sha256={digest}",
        f"cmd={redact(shlex.join(args.command))}",
        f"rc={proc.returncode}",
        f"utc={dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "--- stdout ---",
        redact(proc.stdout.rstrip("\n")),
        "--- stderr ---",
        redact(proc.stderr.rstrip("\n")),
    ]
    body = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(body)
    counts = COUNTS_RE.search(proc.stdout)
    print(f"receipt={out} rev={rev} tool_sha256={digest} rc={proc.returncode} "
          f"counts={counts.group(0) if counts else 'none'}")
    return 0


def parse_receipt(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0] != "receipt=v1":
        return None
    header: dict[str, str] = {}
    idx = 0
    for name in HEADER_ORDER:
        if idx >= len(lines) or not lines[idx].startswith(name + "="):
            return None
        header[name] = lines[idx].split("=", 1)[1]
        idx += 1
    if idx >= len(lines) or lines[idx] != "--- stdout ---":
        return None
    header["_body"] = "\n".join(lines[idx:])
    return header


def cmd_verify(args: argparse.Namespace) -> int:
    root = os.path.abspath(args.root)
    try:
        with open(args.receipt, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return refuse("RECEIPT-UNREADABLE", str(exc))
    header = parse_receipt(text)
    if header is None:
        return refuse("RECEIPT-MALFORMED", "header order or fences do not match receipt v1")
    rev = header["rev"]
    if not REV_RE.match(rev):
        return refuse("RECEIPT-REV-MALFORMED", f"rev={rev!r}")
    tool = header["tool"]
    actual = blob_sha_bytes(root, rev, tool)
    if actual is None:
        return refuse("RECEIPT-TOOL-ABSENT", f"{tool} absent at {rev}")
    if actual != header["tool_sha256"]:
        return refuse("RECEIPT-TOOL-DIGEST-MISMATCH",
                      f"receipt {header['tool_sha256'][:12]} != tree {actual[:12]} at {rev}")
    if not COUNTS_RE.search(header["_body"]):
        return refuse("RECEIPT-COUNTS-ABSENT", "no counts line in the recorded output")
    print(f"verify=ok rev={rev} tool={tool} tool_sha256={actual}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="souji blob-bound receipt runner (C2)")
    sub = ap.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("run")
    r.add_argument("--root", default=os.getcwd())
    r.add_argument("--rev", required=True)
    r.add_argument("--tool", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("command", nargs=argparse.REMAINDER)
    v = sub.add_parser("verify")
    v.add_argument("--root", default=os.getcwd())
    v.add_argument("receipt")
    args = ap.parse_args(argv)
    if args.mode == "run":
        cmd = list(args.command)
        if cmd and cmd[0] == "--":
            cmd = cmd[1:]
        args.command = cmd
        return cmd_run(args)
    return cmd_verify(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
