#!/usr/bin/env python3
"""c1-counter.py — souji round-62 C1 counter (seat S62ExecCounter).

Judges the frozen C1 claim: the receipt writer's clean-tree assertion must not
survive index flags (skip-worktree `S` / assume-unchanged `h`) that hide
worktree divergence from `git status --porcelain`.

Per matrix row the counter builds a fresh fixture repo under WORK/<case>/repo
(git init, toplevel assert, local identity, fixed dates, one seed commit of
tools/instr.sh + tools/counter.py + tools/notes.txt), applies the frozen
mutation, then runs TWO slots of the receipt writer:

  base slot — tools/souji-receipt-write.py bytes at --base-rev, fetched via
              `git -C ROOT show <base-rev>:tools/souji-receipt-write.py`
              (read-only plumbing; the lane itself is never written).
  new slot  — the --tool PATH bytes (--arm tool, default), or the base bytes
              again (--arm plain: the do-nothing control).

Accept = exit 0 and OUT present. Refuse = exit 2 and OUT absent. Any other
exit is an error for the case. Refusal class = the row's expected_class
substring found on the slot's stderr. Base and new slots use separate OUT
directories (out-base/, out-new/) so a base accept can never contaminate the
new slot's refuse detection.

Regression arm: tests/fixtures/r60-receipt-write.py runs from the lane root
against BOTH slots (base bytes and --tool bytes); REGRESS=PASS iff exit 0 and
the last output line contains `pass=8 fail=0`.

Stdlib only. Writes ONLY under --work (must exist, must not be under /tmp or
/var/tmp). Never mutates the lane; read-only git plumbing only.

Usage:
  python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv \
      --base-rev FULL40 --rev FULL40|none --tool PATH --work DIR \
      [--arm tool|plain]

Exit: 0 = claim upheld per SUMMARY; 1 = claim fails; 2 = could not evaluate
(bad rev, missing matrix, missing or /tmp work dir, base bytes unreadable,
unreadable --tool).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys

BASE_REL = "tools/souji-receipt-write.py"
FIXTURE_REL = os.path.join("tests", "fixtures", "r60-receipt-write.py")
FIXTURE_LAST_WANT = "pass=8 fail=0"

SEED_INSTR = b"#!/bin/sh\necho instrument-ok\n"
SEED_COUNTER = b"counter v1\n"
SEED_NOTES = b"notes v1\n"
DIRTY_APPEND = b"dirty\n"
FORGED_COUNTER = b"counter FORGED\n"
FORGED_INSTR = b"#!/bin/sh\necho FORGED\n"

GIT_ID_NAME = "C1 Counter"
GIT_ID_EMAIL = "c1-counter@invalid"
GIT_DATE = "2026-11-05T12:00:00Z"

REV_RE = re.compile(r"^[0-9a-f]{40}$")

# Frozen mutations, exactly as specified. Order inside mutate(): index flag
# first, then forged bytes, then the visible dirty append.
CASE_SPECS = {
    "A": {"name": "honest-clean"},
    "B": {"name": "honest-allow-dirty", "dirty": True, "allow_dirty": True},
    "C": {"name": "dirty-visible", "dirty": True, "allow_dirty": False},
    "D": {"name": "skip-worktree-forged", "flag": "skip-worktree",
          "target": "tools/counter.py", "forged": FORGED_COUNTER},
    "E": {"name": "assume-unchanged-forged", "flag": "assume-unchanged",
          "target": "tools/counter.py", "forged": FORGED_COUNTER},
    "F": {"name": "skip-worktree-unmodified", "flag": "skip-worktree",
          "target": "tools/counter.py"},
    "G": {"name": "instrument-skip-worktree-forged", "flag": "skip-worktree",
          "target": "tools/instr.sh", "forged": FORGED_INSTR},
}
CASE_ORDER = ["A", "B", "C", "D", "E", "F", "G"]


class CaseError(Exception):
    """A fixture build/mutation failure; the case is judged as error."""


def git_run(repo: str, args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    e = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    e["GIT_OPTIONAL_LOCKS"] = "0"
    if env:
        e.update(env)
    return subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, env=e, timeout=120)


def build_repo(work: str, letter: str) -> tuple[str, str]:
    case_dir = os.path.join(work, letter)
    repo = os.path.join(case_dir, "repo")
    if os.path.isdir(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(repo)
    r = git_run(repo, ["init", "-q"])
    if r.returncode != 0:
        raise CaseError(f"git init failed: {r.stderr.strip()}")
    top = git_run(repo, ["rev-parse", "--show-toplevel"])
    if top.returncode != 0 or os.path.realpath(top.stdout.strip()) != os.path.realpath(repo):
        raise CaseError(f"toplevel mismatch before first commit: {top.stdout.strip()!r}")
    for key, val in (("user.name", GIT_ID_NAME), ("user.email", GIT_ID_EMAIL)):
        r = git_run(repo, ["config", key, val])
        if r.returncode != 0:
            raise CaseError(f"git config {key} failed: {r.stderr.strip()}")
    os.makedirs(os.path.join(repo, "tools"), exist_ok=True)
    seeds = {
        "tools/instr.sh": SEED_INSTR,
        "tools/counter.py": SEED_COUNTER,
        "tools/notes.txt": SEED_NOTES,
    }
    for rel, data in seeds.items():
        with open(os.path.join(repo, rel), "wb") as f:
            f.write(data)
    os.chmod(os.path.join(repo, "tools/instr.sh"), 0o755)
    dates = {"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE}
    r = git_run(repo, ["add", "-A"], env=dates)
    if r.returncode != 0:
        raise CaseError(f"git add failed: {r.stderr.strip()}")
    r = git_run(repo, ["commit", "-q", "-m", "c1 seed"], env=dates)
    if r.returncode != 0:
        raise CaseError(f"git commit failed: {r.stderr.strip()}")
    h = git_run(repo, ["rev-parse", "HEAD"])
    rev = h.stdout.strip()
    if h.returncode != 0 or not REV_RE.match(rev):
        raise CaseError(f"bad seed HEAD: {rev!r}")
    return repo, rev


def mutate(repo: str, spec: dict) -> None:
    if spec.get("flag"):
        r = git_run(repo, ["update-index", f"--{spec['flag']}", spec["target"]])
        if r.returncode != 0:
            raise CaseError(f"update-index --{spec['flag']} failed: {r.stderr.strip()}")
    if spec.get("forged") is not None:
        with open(os.path.join(repo, spec["target"]), "wb") as f:
            f.write(spec["forged"])
    if spec.get("dirty"):
        with open(os.path.join(repo, "tools/notes.txt"), "ab") as f:
            f.write(DIRTY_APPEND)


def run_slot(slot: str, repo: str, rev: str, out: str, allow_dirty: bool) -> tuple[int, str, str]:
    argv = [sys.executable, "-B", slot, "--root", repo, "--rev", rev,
            "--instrument", "tools/instr.sh", "--out", out, "--allow-outside"]
    if allow_dirty:
        argv.append("--allow-dirty")
    argv += ["--", "sh", "-c", "echo ok"]
    try:
        p = subprocess.run(argv, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return 124, "", "timeout after 180s"
    except OSError as exc:
        return 125, "", f"launch failed: {exc}"
    return p.returncode, p.stdout, p.stderr


def judge(rc: int, out: str) -> str:
    if rc == 0 and os.path.isfile(out):
        return "accept"
    if rc == 2 and not os.path.lexists(out):
        return "refuse"
    return "error"


def findings_for(verdict: str, stderr: str, klass: str) -> str:
    if verdict == "refuse" and klass and klass in stderr:
        return klass
    return "-"


def one_line(text: str, limit: int = 160) -> str:
    s = " ".join((text or "").split())
    return (s[: limit - 3] + "...") if len(s) > limit else s


def load_matrix(path: str) -> tuple[list[tuple[str, str, str]] | None, str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as exc:
        return None, f"cannot read matrix: {exc}"
    lines = [l for l in raw.splitlines() if l.strip()]
    if not lines:
        return None, "matrix is empty"
    if lines[0].split("\t") != ["case", "expect", "expected_class"]:
        return None, f"bad header: {lines[0]!r}"
    rows: list[tuple[str, str, str]] = []
    for i, line in enumerate(lines[1:], 2):
        parts = line.split("\t")
        if len(parts) != 3:
            return None, f"line {i}: expected 3 tab-separated fields, got {len(parts)}"
        case, expect, klass = parts
        if expect not in ("accept", "refuse"):
            return None, f"line {i}: expect must be accept|refuse, got {expect!r}"
        if expect == "refuse" and not klass:
            return None, f"line {i}: refuse row needs a non-empty expected_class"
        if expect == "accept" and klass != "-":
            return None, f"line {i}: accept row must use '-' as expected_class"
        rows.append((case, expect, klass))
    if [r[0] for r in rows] != CASE_ORDER:
        return None, f"matrix rows must be {CASE_ORDER} in order, got {[r[0] for r in rows]}"
    return rows, ""


def fetch_base_bytes(root: str, base_rev: str, dest: str) -> str:
    r = subprocess.run(["git", "-C", root, "show", f"{base_rev}:{BASE_REL}"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    if r.returncode != 0 or not r.stdout:
        detail = r.stderr.decode("utf-8", "replace").strip()
        raise SystemExit(fatal(f"base bytes unreadable ({base_rev}:{BASE_REL}): {detail or 'empty'}"))
    with open(dest, "wb") as f:
        f.write(r.stdout)
    os.chmod(dest, 0o755)
    return hashlib.sha256(r.stdout).hexdigest()


def run_fixture(root: str, fixture: str, slot: str, wdir: str) -> tuple[bool, str, str]:
    os.makedirs(wdir, exist_ok=True)
    if not os.path.isfile(fixture):
        return False, "fixture missing", ""
    try:
        p = subprocess.run([sys.executable, "-B", fixture, "--tool", slot, "--work", wdir],
                           cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, timeout=900)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return False, f"fixture launch failed: {exc}", ""
    lines = [l for l in (p.stdout or "").splitlines() if l.strip()]
    last = lines[-1] if lines else ""
    ok = p.returncode == 0 and FIXTURE_LAST_WANT in last
    return ok, f"rc={p.returncode}", last


def fatal(msg: str) -> int:
    print(f"C1-COUNTER-FATAL: {msg}", file=sys.stderr)
    print("EXIT=2")
    return 2


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="c1-counter.py",
        description="round-62 C1 counter: index-flag concealment vs the receipt writer",
    )
    ap.add_argument("--root", required=True, help="lane root (read-only)")
    ap.add_argument("--matrix", required=True, help="c1-matrix.tsv path")
    ap.add_argument("--base-rev", required=True, help="full 40-hex lane base revision")
    ap.add_argument("--rev", required=True, help="full 40-hex revision under test, or 'none'")
    ap.add_argument("--tool", required=True, help="candidate tool PATH (new slot when --arm tool)")
    ap.add_argument("--work", required=True, help="work directory (must exist, not under /tmp)")
    ap.add_argument("--arm", choices=("tool", "plain"), default="tool",
                    help="tool: run --tool bytes in the new slot; plain: run base bytes there")
    ns = ap.parse_args(argv)

    root = os.path.abspath(ns.root)
    work = os.path.abspath(ns.work)
    if not os.path.isdir(work):
        return fatal(f"work directory does not exist: {work}")
    rp = os.path.realpath(work)
    if rp in ("/tmp", "/var/tmp") or rp.startswith("/tmp/") or rp.startswith("/var/tmp/"):
        return fatal(f"work directory must not live under /tmp or /var/tmp: {rp}")
    if not os.path.isdir(root):
        return fatal(f"root is not a directory: {root}")
    if ns.rev != "none" and not REV_RE.match(ns.rev):
        return fatal(f"--rev must be full 40-hex or 'none', got {ns.rev!r}")
    if not REV_RE.match(ns.base_rev):
        return fatal(f"--base-rev must be full 40-hex, got {ns.base_rev!r}")
    if ns.arm == "tool" and not os.path.isfile(ns.tool):
        return fatal(f"--tool is not a readable file: {ns.tool}")
    rows, err = load_matrix(os.path.abspath(ns.matrix))
    if rows is None:
        return fatal(f"matrix unusable: {err}")

    slots = os.path.join(work, "slots")
    if os.path.isdir(slots):
        shutil.rmtree(slots)
    os.makedirs(slots)
    base_slot = os.path.join(slots, "base.py")
    base_sha = fetch_base_bytes(root, ns.base_rev, base_slot)
    if ns.arm == "tool":
        with open(ns.tool, "rb") as f:
            new_bytes = f.read()
    else:
        with open(base_slot, "rb") as f:
            new_bytes = f.read()
    new_slot = os.path.join(slots, "new.py")
    with open(new_slot, "wb") as f:
        f.write(new_bytes)
    os.chmod(new_slot, 0o755)
    new_sha = hashlib.sha256(new_bytes).hexdigest()

    print(f"# c1-counter root={root} base-rev={ns.base_rev} rev={ns.rev} arm={ns.arm}")
    print(f"# slot base={base_slot} sha256={base_sha}")
    print(f"# slot new={new_slot} sha256={new_sha}")

    base_forgeries = base_honest = new_forgeries = new_honest = class_mismatches = 0
    all_new_match = True

    for letter, expect, klass in rows:
        spec = CASE_SPECS[letter]
        try:
            repo, rev = build_repo(work, letter)
            mutate(repo, spec)
        except CaseError as exc:
            print(f"CASE {letter} expect={expect} base=error base_findings=- "
                  f"new=error new_findings=-")
            print(f"# detail {letter} name={spec['name']} build_failed: {exc}")
            all_new_match = False
            continue
        out_base_dir = os.path.join(work, letter, "out-base")
        out_new_dir = os.path.join(work, letter, "out-new")
        for d in (out_base_dir, out_new_dir):
            if os.path.isdir(d):
                shutil.rmtree(d)
            os.makedirs(d)
        allow_dirty = bool(spec.get("allow_dirty"))

        b_out = os.path.join(out_base_dir, "receipt.txt")
        b_rc, b_so, b_se = run_slot(base_slot, repo, rev, b_out, allow_dirty)
        b_v = judge(b_rc, b_out)
        b_f = findings_for(b_v, b_se, klass)

        n_out = os.path.join(out_new_dir, "receipt.txt")
        n_rc, n_so, n_se = run_slot(new_slot, repo, rev, n_out, allow_dirty)
        n_v = judge(n_rc, n_out)
        n_f = findings_for(n_v, n_se, klass)

        print(f"CASE {letter} expect={expect} base={b_v} base_findings={b_f} "
              f"new={n_v} new_findings={n_f}")
        print(f"# detail {letter} name={spec['name']} rev={rev[:12]} "
              f"base_rc={b_rc} new_rc={n_rc} base_stderr={one_line(b_se)} "
              f"new_stderr={one_line(n_se)}")

        if expect == "refuse":
            if b_v == "accept":
                base_forgeries += 1
            if n_v == "accept":
                new_forgeries += 1
            if not (n_v == "refuse" and klass and klass in n_se):
                class_mismatches += 1
        else:
            if b_v == "accept":
                base_honest += 1
            if n_v == "accept":
                new_honest += 1
        if n_v != expect:
            all_new_match = False

    fixture = os.path.join(root, FIXTURE_REL)
    reg_base_ok, reg_base_detail, reg_base_last = run_fixture(
        root, fixture, base_slot, os.path.join(work, "r60-base"))
    reg_new_ok, reg_new_detail, reg_new_last = run_fixture(
        root, fixture, new_slot, os.path.join(work, "r60"))
    regress = "PASS" if (reg_base_ok and reg_new_ok) else "FAIL"
    print(f"REGRESS base={'PASS' if reg_base_ok else 'FAIL'} "
          f"new={'PASS' if reg_new_ok else 'FAIL'}")
    print(f"# regress-detail base {reg_base_detail} last={one_line(reg_base_last)}")
    print(f"# regress-detail new {reg_new_detail} last={one_line(reg_new_last)}")

    print(f"SUMMARY matrix={len(rows)} base_forgeries={base_forgeries} "
          f"base_honest={base_honest} new_forgeries={new_forgeries} "
          f"new_honest={new_honest} class_mismatches={class_mismatches} "
          f"regress={regress}")
    ok = (new_forgeries == 0 and new_honest == 2 and class_mismatches == 0
          and regress == "PASS" and all_new_match)
    rc = 0 if ok else 1
    print(f"EXIT={rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
