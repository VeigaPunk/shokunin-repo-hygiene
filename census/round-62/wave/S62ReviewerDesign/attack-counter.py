#!/usr/bin/env python3
"""S62ReviewerDesign attack counter: run the frozen 7-row A-G matrix against a
receipt-writer tool.  Build fixture repos in scratch; classify each run.

Usage: python3 counter.py --tool TOOL --work WORKDIR
Exit 0 iff: honest A,B accept; dirty-visible C refuses with 'lane worktree is
dirty'; D,E,F,G refuse with RECEIPT-INDEX-FLAG-CONCEALED; else 1.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

WRITER = "/fast/scratch/hyaku/souji-r62/S62ReviewerDesign/candidate.py"  # default tool

COUNTER_BYTES = b'#!/bin/sh\necho counter-body-v1\n'
NOTES_BYTES = b"notes\n"
INSTRUMENT_REL = "tools/instrument.sh"
INSTRUMENT_BODY = "#!/bin/sh\necho instrument-ok\n"
GIT_ID = ["-c", "user.name=S62Attack", "-c", "user.email=s62@example.invalid"]


def sh(argv, cwd=None, check=False):
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"setup failed rc={r.returncode}: {argv}\n{r.stderr}")
    return r


def make_repo(work, name, flags_on=None, forge=None, dirty=False, allow_dirty=False):
    d = tempfile.mkdtemp(prefix=name + ".", dir=work)
    sh(["git", "init", "-q", d], check=True)
    toplevel = sh(["git", "-C", d, "rev-parse", "--show-toplevel"], check=True).stdout.strip()
    assert toplevel == os.path.realpath(d), (toplevel, d)
    os.makedirs(os.path.join(d, "tools"))
    with open(os.path.join(d, "tools", "instrument.sh"), "wb") as f:
        f.write(INSTRUMENT_BODY.encode())
    with open(os.path.join(d, "counter.py"), "wb") as f:
        f.write(COUNTER_BYTES)
    with open(os.path.join(d, "notes.txt"), "wb") as f:
        f.write(NOTES_BYTES)
    sh(["git", "-C", d, *GIT_ID, "add", "-A"], check=True)
    sh(["git", "-C", d, *GIT_ID, "commit", "-q", "-m", "init"], check=True)
    rev = sh(["git", "-C", d, "rev-parse", "HEAD"], check=True).stdout.strip()
    # apply saved-flags / forgeries AFTER the commit, on the clean tree
    for rel, flag in (flags_on or {}).items():
        argv = {"skip": ["update-index", "--skip-worktree", "--", rel],
                "assume": ["update-index", "--assume-unchanged", "--", rel]}[flag]
        r = sh(["git", "-C", d, *argv])
        if r.returncode != 0:
            raise SystemExit(f"update-index failed rc={r.returncode}: {rel} {flag}: {r.stderr}")
    for rel, bytes_ in (forge or {}).items():
        with open(os.path.join(d, *rel.split("/")), "wb") as f:
            f.write(bytes_)
    os.makedirs(os.path.join(d, "receipts"))
    if dirty:
        with open(os.path.join(d, "notes.txt"), "wb") as f:
            f.write(NOTES_BYTES + b"EDITED-VISIBLE\n")
    return d, rev


def run_writer(repo, rev, out, allow_dirty=False):
    argv = ["python3", "-B", WRITER, "--root", repo, "--rev", rev,
            "--instrument", INSTRUMENT_REL, "--out", out,
            "--command", "/bin/echo hi-run"]
    if allow_dirty:
        argv.append("--allow-dirty")
    return subprocess.run(argv, capture_output=True, text=True, timeout=60)


def classify(repo, rev, out, allow_dirty):
    r = run_writer(repo, rev, out, allow_dirty);
    combined = (r.stdout + r.stderr).strip()
    wrote = os.path.exists(out)
    refused_flag = "RECEIPT-INDEX-FLAG-CONCEALED:" in combined
    refused_dirty = "lane worktree is dirty" in combined
    refused_uname = "cannot read index flags" in combined
    rc = r.returncode
    if rc == 0 and wrote:
        return "ACCEPT", rc, combined
    if rc == 2 and refused_flag:
        return "REFUSE-FLAG", rc, combined
    if rc == 2 and refused_dirty:
        return "REFUSE-DIRTY", rc, combined
    if rc == 2 and refused_uname:
        return "REFUSE-UNAME", rc, combined
    return f"OTHER({rc})", rc, combined


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", default=WRITER)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args()
    globals()["WRITER"] = ns.tool

    rows = []
    # A honest-clean
    d, rev = make_repo(ns.work, "A")
    rows.append(("A honest-clean", classify(d, rev, os.path.join(d, "receipts", "r.txt"), False)))
    # B honest-allow-dirty
    d, rev = make_repo(ns.work, "B", dirty=True)
    rows.append(("B honest-allow-dirty", classify(d, rev, os.path.join(d, "receipts", "r.txt"), True)))
    # C dirty-visible no allow
    d, rev = make_repo(ns.work, "C", dirty=True)
    rows.append(("C dirty-visible", classify(d, rev, os.path.join(d, "receipts", "r.txt"), False)))
    # D skip-worktree forged
    d, rev = make_repo(ns.work, "D", flags_on={"counter.py": "skip"}, forge={"counter.py": b"FORGED\n"})
    rows.append(("D skip-forged", classify(d, rev, os.path.join(d, "receipts", "r.txt"), False)))
    # E assume-unchanged forged
    d, rev = make_repo(ns.work, "E", flags_on={"counter.py": "assume"}, forge={"counter.py": b"FORGED\n"})
    rows.append(("E assume-forged", classify(d, rev, os.path.join(d, "receipts", "r.txt"), False)))
    # F skip-worktree unmodified
    d, rev = make_repo(ns.work, "F", flags_on={"counter.py": "skip"})
    rows.append(("F skip-clean", classify(d, rev, os.path.join(d, "receipts", "r.txt"), False)))
    # G skip-worktree on instrument + forged
    d, rev = make_repo(ns.work, "G", flags_on={INSTRUMENT_REL: "skip"}, forge={INSTRUMENT_REL: b"FORGED-INSTR\n"})
    rows.append(("G instr-skip-forged", classify(d, rev, os.path.join(d, "receipts", "r.txt"), False)))

    expect = {
        "A honest-clean": "ACCEPT",
        "B honest-allow-dirty": "ACCEPT",
        "C dirty-visible": "REFUSE-DIRTY",
        "D skip-forged": "REFUSE-FLAG",
        "E assume-forged": "REFUSE-FLAG",
        "F skip-clean": "REFUSE-FLAG",
        "G instr-skip-forged": "REFUSE-FLAG",
    }
    ok = True
    for name, (cls, rc, combined) in rows:
        want = expect[name]
        good = cls == want
        ok = ok and good
        first = (combined.splitlines() or [""])[0][:140]
        print(f"{name:24} want={want:13} got={cls:14} rc={rc} {'OK' if good else 'MISMATCH'}  | {first}")
    print("MATRIX", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
