"""c2-counter.py — souji round-63 C2 counter: concealment-class refusals (edge classes).

Frozen matrix census/round-63/c2-matrix.tsv (5 rows, CASE_SPECS must cover exactly these rows):
  P1 honest-clean                 accept
  P2 dirty-visible                refuse  lane worktree is dirty
  H1 unmerged-conflict            refuse  RECEIPT-INDEX-UNMERGED
  H2 gitlink-flagged              refuse  RECEIPT-GITLINK-CONCEALED
  H3 flagged-absent               refuse  RECEIPT-INDEX-CONCEALED-ABSENT

The sparse-checkout row of round 63's draft was REMOVED before freeze: a present sparse-excluded
file is tagged H and never reaches the flag loop (sentinel F6), so no writer can produce its class.
Sparse-induced S with an absent worktree file takes the ABSENT class (named limit, not claimed).

Arms: --arm tool runs --tool bytes in the new slot; --arm plain runs the base bytes there (the
do-nothing control). Base bytes come from `git show <base-rev>:tools/souji-receipt-write.py`.
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
SIDE_COUNTER = b"counter SIDE\n"
MAIN_COUNTER = b"counter MAIN\n"
FORGED_COUNTER = b"counter FORGED\n"
GITLINK_REL = "tools/sub"

GIT_ID_NAME = "C2 Counter"
GIT_ID_EMAIL = "c2-counter@invalid"
GIT_DATE = "2026-11-05T12:00:00Z"

REV_RE = re.compile(r"^[0-9a-f]{40}$")

CASE_ORDER = ["P1", "P2", "H1", "H2", "H3"]
CASE_SPECS = {
    "P1": {"name": "honest-clean"},
    "P2": {"name": "dirty-visible", "mutation": "dirty"},
    "H1": {"name": "unmerged-conflict", "mutation": "unmerged"},
    "H2": {"name": "gitlink-flagged", "mutation": "gitlink"},
    "H3": {"name": "flagged-absent", "mutation": "absent"},
}
class CaseError(Exception):
    """A fixture build or mutation failure; the case is judged as error."""


def git_run(repo: str, args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    e = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    e["GIT_OPTIONAL_LOCKS"] = "0"
    if env:
        e.update(env)
    return subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, env=e, timeout=120)


def _must(r: subprocess.CompletedProcess, what: str) -> str:
    if r.returncode != 0:
        raise CaseError(f"{what} failed rc={r.returncode}: {r.stderr.strip()}")
    return r.stdout


def build_repo(work: str, letter: str) -> tuple[str, str]:
    case_dir = os.path.join(work, letter)
    repo = os.path.join(case_dir, "repo")
    if os.path.isdir(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(repo)
    _must(git_run(repo, ["init", "-q"]), "git init")
    top = git_run(repo, ["rev-parse", "--show-toplevel"])
    if top.returncode != 0 or os.path.realpath(top.stdout.strip()) != os.path.realpath(repo):
        raise CaseError(f"toplevel mismatch before first commit: {top.stdout.strip()!r}")
    _must(git_run(repo, ["config", "user.name", GIT_ID_NAME]), "git config user.name")
    _must(git_run(repo, ["config", "user.email", GIT_ID_EMAIL]), "git config user.email")
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
    _must(git_run(repo, ["add", "-A"], env=dates), "git add")
    _must(git_run(repo, ["commit", "-q", "-m", "c2 seed"], env=dates), "git commit")
    rev = _must(git_run(repo, ["rev-parse", "HEAD"]), "git rev-parse HEAD").strip()
    if not REV_RE.match(rev):
        raise CaseError(f"bad seed HEAD: {rev!r}")
    return repo, rev


def _commit(repo: str, msg: str) -> None:
    dates = {"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE}
    _must(git_run(repo, ["add", "-A"], env=dates), "git add")
    _must(git_run(repo, ["commit", "-q", "-m", msg], env=dates), "git commit")


def _write(repo: str, rel: str, data: bytes) -> None:
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)


def mutate(repo: str, letter: str, rev: str) -> None:
    kind = CASE_SPECS[letter].get("mutation")
    if kind is None:
        return
    if kind == "dirty":
        with open(os.path.join(repo, "tools/notes.txt"), "ab") as f:
            f.write(DIRTY_APPEND)
        return
    if kind == "unmerged":
        main = _must(git_run(repo, ["symbolic-ref", "--short", "HEAD"]), "symbolic-ref").strip()
        _must(git_run(repo, ["checkout", "-q", "-b", "side"]), "checkout side")
        _write(repo, "tools/counter.py", SIDE_COUNTER)
        _commit(repo, "c2 side")
        _must(git_run(repo, ["checkout", "-q", main]), "checkout main")
        _write(repo, "tools/counter.py", MAIN_COUNTER)
        _commit(repo, "c2 main")
        merge = git_run(repo, ["merge", "--no-edit", "-q", "side"])
        if merge.returncode == 0:
            raise CaseError("merge did not conflict")
        u = _must(git_run(repo, ["ls-files", "-u", "-z", "--", "tools/counter.py"]), "ls-files -u")
        if not u:
            raise CaseError("no unmerged stages after conflicting merge")
        return
    if kind == "gitlink":
        _must(git_run(repo, ["update-index", "--add", "--cacheinfo",
                             f"160000,{rev},{GITLINK_REL}"]), "update-index --add gitlink")
        _must(git_run(repo, ["update-index", "--skip-worktree", GITLINK_REL]),
              "update-index --skip-worktree gitlink")
        s = _must(git_run(repo, ["ls-files", "-s", "-z", "--", GITLINK_REL]), "ls-files -s gitlink")
        if not s.split("\0")[0].startswith("160000 "):
            raise CaseError(f"gitlink not in index: {s!r}")
        return
    if kind == "absent":
        _must(git_run(repo, ["update-index", "--skip-worktree", "tools/counter.py"]),
              "update-index --skip-worktree counter")
        os.remove(os.path.join(repo, "tools/counter.py"))
        if os.path.lexists(os.path.join(repo, "tools/counter.py")):
            raise CaseError("worktree counter still present after delete")
        return
    raise CaseError(f"unknown mutation {kind!r}")


def fixture_state(repo: str) -> str:
    """Diagnostic only: non-H tags and porcelain line count, read like the writer (no -c)."""
    fl = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z"], capture_output=True,
                        env={k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")})
    tags = []
    for rec in fl.stdout.split(b"\0"):
        if rec and not rec.startswith(b"H "):
            tags.append(rec.decode("utf-8", "replace"))
    st = subprocess.run(["git", "-C", repo, "status", "--porcelain"], capture_output=True)
    lines = len([l for l in st.stdout.decode("utf-8", "replace").splitlines() if l.strip()])
    return f"fixture_tags={';'.join(tags) if tags else '-'} status_lines={lines}"


def run_slot(slot: str, repo: str, rev: str, out: str) -> tuple[int, str, str]:
    argv = [sys.executable, "-B", slot, "--root", repo, "--rev", rev,
            "--instrument", "tools/instr.sh", "--out", out, "--allow-outside",
            "--", "sh", "-c", "echo ok"]
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
    print(f"C2-COUNTER-FATAL: {msg}", file=sys.stderr)
    print("EXIT=2")
    return 2


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="c2-counter.py",
        description="round-63 C2 counter: refusal class of the receipt writer's flag loop",
    )
    ap.add_argument("--root", required=True, help="lane root (read-only)")
    ap.add_argument("--matrix", required=True, help="c2-matrix.tsv path")
    ap.add_argument("--base-rev", required=True, help="full 40-hex lane base revision")
    ap.add_argument("--rev", required=True, help="full 40-hex revision under test, or 'none'")
    ap.add_argument("--tool", "--new-tool", dest="tool", required=True,
                    help="candidate tool PATH (new slot when --arm tool)")
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

    print(f"# c2-counter root={root} base-rev={ns.base_rev} rev={ns.rev} arm={ns.arm}")
    print(f"# slot base={base_slot} sha256={base_sha}")
    print(f"# slot new={new_slot} sha256={new_sha}")

    honest = refusals = base_forgeries = new_forgeries = 0
    base_cm = new_cm = 0
    all_new_match = True

    for letter, expect, klass in rows:
        spec = CASE_SPECS[letter]
        try:
            repo, rev = build_repo(work, letter)
            mutate(repo, letter, rev)
        except CaseError as exc:
            print(f"CASE {letter} expect={expect} base=error base_findings=- "
                  f"new=error new_findings=-")
            print(f"# detail {letter} name={spec['name']} build_failed: {exc}")
            all_new_match = False
            base_cm += 1
            new_cm += 1
            continue
        state = fixture_state(repo)
        out_base_dir = os.path.join(work, letter, "out-base")
        out_new_dir = os.path.join(work, letter, "out-new")
        for d in (out_base_dir, out_new_dir):
            if os.path.isdir(d):
                shutil.rmtree(d)
            os.makedirs(d)

        b_out = os.path.join(out_base_dir, "receipt.txt")
        b_rc, b_so, b_se = run_slot(base_slot, repo, rev, b_out)
        b_v = judge(b_rc, b_out)
        b_f = findings_for(b_v, b_se, klass)

        n_out = os.path.join(out_new_dir, "receipt.txt")
        n_rc, n_so, n_se = run_slot(new_slot, repo, rev, n_out)
        n_v = judge(n_rc, n_out)
        n_f = findings_for(n_v, n_se, klass)

        print(f"CASE {letter} expect={expect} base={b_v} base_findings={b_f} "
              f"new={n_v} new_findings={n_f}")
        print(f"# detail {letter} name={spec['name']} rev={rev[:12]} "
              f"base_rc={b_rc} new_rc={n_rc} {state} "
              f"base_stderr={one_line(b_se)} new_stderr={one_line(n_se)}")

        if expect == "refuse":
            if b_v == "accept":
                base_forgeries += 1
            if n_v == "accept":
                new_forgeries += 1
            if not (b_v == "refuse" and klass and klass in b_se):
                base_cm += 1
            if not (n_v == "refuse" and klass and klass in n_se):
                new_cm += 1
        else:
            if b_v != "accept":
                base_cm += 1
            if n_v != "accept":
                new_cm += 1
            if n_v == "accept":
                honest += 1
        if n_v == "refuse":
            refusals += 1
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

    print(f"SUMMARY matrix={len(rows)} honest={honest} refusals={refusals} "
          f"base_class_mismatches={base_cm} new_class_mismatches={new_cm}")
    print(f"FORGERIES base={base_forgeries} new={new_forgeries}")
    ok = (new_forgeries == 0 and new_cm == 0 and honest == 1
          and regress == "PASS" and all_new_match)
    rc = 0 if ok else 1
    print(f"EXIT={rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
