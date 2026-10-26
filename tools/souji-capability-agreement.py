#!/usr/bin/env python3
"""souji-capability-agreement.py — round-30 C1 calibration counter (frozen at the r30 preregistration).

Counts mismatches between the lane's self-assessment files and what committed bytes show, at a full
40-hex revision REV. The enumerated set is read from the preregistration commit (--list-rev), never
from REV, so a later commit cannot shrink it.

K1  capability rows. Each row of `census/round-30/c1-rows.tsv` (at --list-rev) names a SCORECARD.md
    line (numbered at --base), a stated literal and a command. The command runs as an argv list (no
    shell) in a private `git clone --no-local` of --root checked out at REV (origin removed;
    `checkout -f` + `clean -fdxq` before every row; TMPDIR is a fresh per-row directory under
    --scratch; timeout --timeout seconds). Its combined stdout+stderr is normalized (tmp/scratch
    paths -> <TMP>, hex runs of 12+ -> <HEX>, decimal durations `N.Ns` -> <DUR>); S is the last
    nonblank normalized line containing a digit, whitespace runs collapsed to one space (`NONE` if
    there is none); a mismatch is labelled kind=rc (exit != 0), kind=shape (the stated integers occur
    in S in order) or kind=value (diagnostic only). The row MATCHES iff the
    stated literal is a substring of S and the exit code is 0. A non-matching row is CORRECTED iff
    SCORECARD.md at REV carries, after the --base bytes, a line
        R30-CORRECTION SCORECARD.md:<line> <row-id> [cmd=<argv>] rc=<n> observed=<S>
    whose rc and observed equal what this run produced; with `cmd=` the counter runs that argv
    instead of the row's command, and its first path token must equal the row command's first path
    token (script identity). A row that neither matches nor is corrected is a K1 mismatch.
K2  SHONEN pointer tokens. Path-like tokens on the SHONEN.md pointer lines at --base (lines that do
    not start with `- [`), optionally `:<line>`. A token resolves iff the path is a blob at REV (and
    has at least <line> lines). An unresolved token is CORRECTED iff SHONEN.md at REV carries, after
    the --base bytes, `R30-CORRECTION SHONEN.md:<line> <token> -> <target>` with <target> either
    `WITHDRAWN` or a path that is a blob at REV with the same basename as the token. Otherwise it is
    a K2 mismatch.
Append-only: if SCORECARD.md (resp. SHONEN.md) at REV does not begin with its --base bytes, every K1
(resp. K2) item is a mismatch (fail closed).

Output: one `ROW`/`PTR` line per item, then
    SUMMARY k1=<a> k2=<b> mismatches=<a+b> rows=<n> pointers=<m> rev=<REV>
Exit 0 iff mismatches=0, 1 otherwise, 2 could-not-evaluate. Read-only on --root.
"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

FULL = re.compile(r"[0-9a-f]{40}")
PATHTOK = re.compile(r"^[A-Za-z0-9_.\-/]+\.(?:md|py|json|sh|tsv|txt)(?::\d+)?$")
GITC = ["-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null"]


def cne(msg):
    print(f"COULD-NOT-EVALUATE {msg}")
    sys.exit(2)


def git(root, *a, check=True):
    p = subprocess.run(["git", "-C", root, *GITC, *a], capture_output=True)
    if check and p.returncode:
        cne("git " + " ".join(a) + ": " + p.stderr.decode("utf-8", "replace").strip())
    return p


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return None if p.returncode else p.stdout.decode("utf-8", "replace")


def normalize(text, scratch):
    text = text.replace(scratch, "<TMP>")
    text = re.sub(r"(?:/var)?/tmp/[^\s'\"`:,)]+", "<TMP>", text)
    text = re.sub(r"/fast/scratch/[^\s'\"`:,)]+", "<TMP>", text)
    text = re.sub(r"\b[0-9a-f]{12,}\b", "<HEX>", text)
    text = re.sub(r"\b\d+\.\d+s\b", "<DUR>", text)
    return text


def summary_line(text):
    for line in reversed(text.splitlines()):
        s = " ".join(line.split())
        if s and re.search(r"\d", s):
            return s
    return "NONE"


def first_path(argv):
    for t in argv:
        if "/" in t:
            return t
    return None


def main():
    ap = argparse.ArgumentParser(prog="souji-capability-agreement.py")
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True, help="append-only base revision (frozen: the r30 lane base)")
    ap.add_argument("--list-rev", required=True, help="preregistration commit holding census/round-30/c1-rows.tsv")
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r30/c1-counter")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--only", default="", help="comma-separated row ids (diagnostic; SUMMARY then marks partial=1)")
    a = ap.parse_args()
    for name in ("rev", "base", "list_rev"):
        if not FULL.fullmatch(getattr(a, name)):
            cne(f"--{name.replace('_', '-')} must be a full 40-hex revision")
        git(a.root, "cat-file", "-e", getattr(a, name) + "^{commit}")
    root = os.path.abspath(a.root)
    rows_tsv = blob(root, a.list_rev, "census/round-30/c1-rows.tsv")
    if rows_tsv is None:
        cne("census/round-30/c1-rows.tsv absent at --list-rev")
    rows = []
    for ln in rows_tsv.splitlines():
        if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
            continue
        f = ln.split("\t")
        if len(f) != 4:
            cne(f"malformed c1-rows line: {ln!r}")
        rows.append((f[0], int(f[1]), f[2], f[3]))
    only = set(x for x in a.only.split(",") if x)

    sc_base, sc_rev = blob(root, a.base, "SCORECARD.md"), blob(root, a.rev, "SCORECARD.md")
    sh_base, sh_rev = blob(root, a.base, "SHONEN.md"), blob(root, a.rev, "SHONEN.md")
    if None in (sc_base, sc_rev, sh_base, sh_rev):
        cne("SCORECARD.md or SHONEN.md missing at --base or --rev")
    sc_append = sc_rev.startswith(sc_base)
    sh_append = sh_rev.startswith(sh_base)
    sc_tail = sc_rev[len(sc_base):] if sc_append else ""
    sh_tail = sh_rev[len(sh_base):] if sh_append else ""
    corr = {}
    for ln in sc_tail.splitlines():
        m = re.match(r"^R30-CORRECTION SCORECARD\.md:(\d+) (\S+) (?:cmd=(.+?) )?rc=(-?\d+) observed=(.*)$", ln)
        if m:
            corr.setdefault((int(m.group(1)), m.group(2)), []).append((m.group(3), int(m.group(4)), m.group(5).strip()))

    os.makedirs(a.scratch, exist_ok=True)
    work = tempfile.mkdtemp(prefix="c1.", dir=a.scratch)
    k1 = 0
    kinds = {"value": 0, "shape": 0, "rc": 0}
    try:
        clone = os.path.join(work, "c")
        p = subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, clone], capture_output=True)
        if p.returncode:
            cne("clone failed: " + p.stderr.decode("utf-8", "replace").strip())
        git(clone, "remote", "remove", "origin")
        if git(clone, "rev-parse", "--show-toplevel").stdout.decode().strip() != clone:
            cne("clone toplevel mismatch")

        def run(argv):
            git(clone, "checkout", "-qf", "--detach", a.rev)
            git(clone, "clean", "-fdxq")
            tmp = tempfile.mkdtemp(prefix="t.", dir=work)
            env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1")
            env.pop("GIT_DIR", None)
            env.pop("GIT_WORK_TREE", None)
            try:
                q = subprocess.run(argv, cwd=clone, env=env, capture_output=True, timeout=a.timeout)
                rc, out = q.returncode, (q.stdout + q.stderr).decode("utf-8", "replace")
            except subprocess.TimeoutExpired as e:
                rc, out = 124, ((e.stdout or b"") + (e.stderr or b"")).decode("utf-8", "replace")
            except OSError as e:
                rc, out = 127, f"exec error {e.errno}"
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            return rc, summary_line(normalize(out, work))

        for rid, line, stated, cmd in rows:
            if only and rid not in only:
                continue
            argv = shlex.split(cmd)
            rc, s = run(argv)
            if not sc_append:
                verdict = "MISMATCH(append-only-violated)"
            elif stated in s and rc == 0:
                verdict = "MATCH"
            else:
                verdict = "MISMATCH"
                for ccmd, crc, cobs in corr.get((line, rid), []):
                    if ccmd is not None:
                        cargv = shlex.split(ccmd)
                        if first_path(cargv) is None or first_path(cargv) != first_path(argv):
                            continue
                        rrc, rs = run(cargv)
                    else:
                        rrc, rs = rc, s
                    if crc == rrc and cobs == rs:
                        verdict = "CORRECTED"
                        rc, s = rrc, rs
                        break
            if verdict.startswith("MISMATCH"):
                k1 += 1
                nums_s = re.findall(r"\d+", stated)
                nums_o = re.findall(r"\d+", s)
                it = iter(nums_o)
                kind = "rc" if rc != 0 else ("shape" if all(n in it for n in nums_s) else "value")
                kinds[kind] += 1
                verdict += f" kind={kind}"
            print(f"ROW\t{rid}\tSCORECARD.md:{line}\tstated={stated}\trc={rc}\tobserved={s}\t{verdict}")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    k2, ptrs = 0, 0
    sh_lines = sh_base.splitlines()
    for i, ln in enumerate(sh_lines, 1):
        if not ln.strip() or ln.lstrip().startswith("- [") or ln.startswith("#") or not ln.startswith(" "):
            continue
        for tok in re.split(r"[\s;,()]+", ln.strip()):
            tok = tok.strip("`")
            if not PATHTOK.match(tok):
                continue
            ptrs += 1
            path, _, n = tok.partition(":")
            b = blob(root, a.rev, path)
            ok = b is not None and (not n or len(b.splitlines()) >= int(n))
            verdict = "RESOLVES" if ok and sh_append else ("MISMATCH(append-only-violated)" if not sh_append else "MISMATCH")
            if verdict == "MISMATCH":
                for cl in sh_tail.splitlines():
                    m = re.match(r"^R30-CORRECTION SHONEN\.md:(\d+) (\S+) -> (\S+)\s*$", cl)
                    if not m or int(m.group(1)) != i or m.group(2) != tok:
                        continue
                    tgt = m.group(3)
                    if tgt == "WITHDRAWN" or (blob(root, a.rev, tgt) is not None and os.path.basename(tgt) == os.path.basename(path)):
                        verdict = "CORRECTED"
                        break
            if verdict.startswith("MISMATCH"):
                k2 += 1
            print(f"PTR\tSHONEN.md:{i}\t{tok}\t{verdict}")
    partial = " partial=1" if only else ""
    print(f"SUMMARY k1={k1} k2={k2} mismatches={k1 + k2} rows={len(rows) if not only else len(only)} pointers={ptrs}{partial} rev={a.rev}")
    print(f"KINDS value={kinds['value']} shape={kinds['shape']} rc={kinds['rc']} (diagnostic; not part of the target)")
    return 0 if k1 + k2 == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
