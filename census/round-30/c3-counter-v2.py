#!/usr/bin/env python3
"""r30 C3 counter v2 — AMENDMENT A2 (stricter-only; the frozen census/round-30/c3-counter.py still runs and must also
meet its target). Written after wave-1 seat SwarmCritic26 reached the frozen SUMMARY with a typed run record (A), a
`ground: F1` label on a stub instead of the admitted entry (D2) and a `ground: F1-jj` token (B).

Extra legs, all read from committed bytes at --rev (a private `git clone --no-local`, origin removed):
  E1 ENTRY itself carries a `ground: F1` line whose token F1 ends at a blank or end of line (the house form is
     `ground: F1 — <scope>`), and exactly 3 files in corpus/knowledge/ carry such a line (an `F1-jj` or other
     suffixed token does not count)
  E2 ENTRY is named, as backticked `knowledge/jj-keep-ref-expiry.md`, in a corpus/README.md table row whose first
     cell starts with the token `F1 ` (the plain F1 row; the `F1-jj` edge-class row does not satisfy it)
  E3 replay: tests/fixtures/r30-jj-keep-expiry.sh@REV, run with TMPDIR under --scratch, exits 0 and its
     `jj-version:`, `git-version:` and `RESULT ` lines equal, in order, those of
     census/round-30/records/jj-keep-expiry-run.txt@REV (binds the record to a committed fixture execution)
  E4 re-fetch: every `snapshot:` path in ENTRY's `## Gate` has a census/round-30/records/fetch-receipts.tsv row
     whose URL, fetched now with `curl -fsSL -m 60`, hashes to that row's sha256 and to the committed blob
     (a fetch failure is could-not-evaluate, never a pass)
SUMMARY-V2 e1=.. e2=.. e3=.. e4=.. f1_exact=<k> rev=REV ; exit 0 iff all ok, 1 otherwise, 2 could-not-evaluate.
"""
import argparse, hashlib, os, re, shutil, subprocess, sys, tempfile

ENTRY = "corpus/knowledge/jj-keep-ref-expiry.md"
RUN = "census/round-30/records/jj-keep-expiry-run.txt"
FIX = "tests/fixtures/r30-jj-keep-expiry.sh"


def blob(root, rev, path, text=True):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    if p.returncode:
        return None
    return p.stdout.decode("utf-8", "replace") if text else p.stdout


def keep(text):
    return [l for l in text.splitlines() if l.startswith(("jj-version:", "git-version:", "RESULT "))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r30/c3v2-counter")
    a = ap.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", a.rev):
        print("COULD-NOT-EVALUATE rev must be a full 40-hex revision")
        return 2
    R, V = os.path.abspath(a.root), a.rev
    e = blob(R, V, ENTRY) or ""
    names = subprocess.run(["git", "-C", R, "ls-tree", "-r", "--name-only", V, "corpus/knowledge/"], capture_output=True, text=True).stdout.split()
    exact = [n for n in names if n.endswith(".md") and re.search(r"^ground: F1(?:[ \t]|$)", blob(R, V, n) or "", re.M)]
    entry_exact = bool(re.search(r"^ground: F1(?:[ \t]|$)", e, re.M))
    e1 = entry_exact and len(exact) == 3
    print(f"E1 {'PASS' if e1 else 'FAIL'} entry_exact={entry_exact} f1_exact={len(exact)}")
    readme = blob(R, V, "corpus/README.md") or ""
    e2 = any(re.match(r"^\|\s*F1 ", l) and "`knowledge/jj-keep-ref-expiry.md`" in l for l in readme.splitlines())
    print(f"E2 {'PASS' if e2 else 'FAIL'}")
    os.makedirs(a.scratch, exist_ok=True)
    w = tempfile.mkdtemp(prefix="c3v2.", dir=a.scratch)
    try:
        c = os.path.join(w, "c")
        for s in (["git", "clone", "-q", "--no-local", "--no-checkout", R, c], ["git", "-C", c, "remote", "remove", "origin"],
                  ["git", "-C", c, "-c", "core.hooksPath=/dev/null", "checkout", "-qf", "--detach", V]):
            if subprocess.run(s, capture_output=True).returncode:
                print("COULD-NOT-EVALUATE clone failed")
                return 2
        tmp = os.path.join(w, "tmp")
        os.makedirs(tmp)
        rec = blob(R, V, RUN) or ""
        if os.path.isfile(os.path.join(c, FIX)):
            p = subprocess.run(["bash", FIX], cwd=c, env=dict(os.environ, TMPDIR=tmp), capture_output=True, timeout=900)
            got = keep(p.stdout.decode("utf-8", "replace"))
            e3 = p.returncode == 0 and got and got == keep(rec)
            print(f"E3 {'PASS' if e3 else 'FAIL'} rc={p.returncode} replay_lines={len(got)} record_lines={len(keep(rec))}")
        else:
            e3 = False
            print("E3 FAIL fixture absent")
        gate = e[e.find("\n## Gate"):] if "\n## Gate" in e else ""
        snaps = sorted(set(re.findall(r"snapshot:\s*`?([^\s`]+)", gate)))
        fr = {}
        for l in (blob(R, V, "census/round-30/records/fetch-receipts.tsv") or "").splitlines()[1:]:
            f = l.split("\t")
            if len(f) >= 6:
                fr[f[5].split(" ")[0]] = (f[0], f[4])
        bad = []
        for sp in snaps:
            if sp not in fr:
                bad.append(f"{sp}:no-receipt")
                continue
            url, want = fr[sp]
            q = subprocess.run(["curl", "-fsSL", "-m", "60", url], capture_output=True)
            if q.returncode:
                print(f"COULD-NOT-EVALUATE fetch {url} rc={q.returncode}")
                return 2
            live = hashlib.sha256(q.stdout).hexdigest()
            b = blob(R, V, sp, text=False)
            if live != want or b is None or hashlib.sha256(b).hexdigest() != want:
                bad.append(f"{sp}:hash")
        e4 = bool(snaps) and not bad
        print(f"E4 {'PASS' if e4 else 'FAIL'} snapshots={len(snaps)} bad={bad}")
    finally:
        shutil.rmtree(w, ignore_errors=True)
    ok = e1 and e2 and e3 and e4
    print(f"SUMMARY-V2 e1={'ok' if e1 else 'fail'} e2={'ok' if e2 else 'fail'} e3={'ok' if e3 else 'fail'} e4={'ok' if e4 else 'fail'} f1_exact={len(exact)} rev={V}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
