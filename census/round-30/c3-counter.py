#!/usr/bin/env python3
"""r30 C3 coverage counter (frozen at the r30 preregistration): F1 keep-ref expiry entry.

Reads only committed bytes at --rev (an exported copy is used to run the gate tools that read a tree).
Legs:
  L1 F1-grounded entries: files in corpus/knowledge/ with a line `ground: F1` (word boundary) == 3 (base 2)
  L2 coverage agreement (tools/souji-coverage-agreement.py@REV) prints exactly
     `grounded=16 mapped=16 dangling=0 mismatches=0` (base grounded=15 mapped=15)
  L3 gate: tools/souji-gate-check.py@REV over the export, --round-date 2026-10-26 --entries ENTRY
     --snapshot-dir census/round-30/sources --slice census/round-30/records/empty-slice
     --slice-verdicts census/round-30/records/empty-verdicts -> rc 0 and
     `entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0`
  L4 snapshots: every `snapshot:` path in ENTRY's `## Gate` is a blob >= 512 bytes whose sha256 equals its
     census/round-30/sources/SHA256SUMS line and its census/round-30/records/fetch-receipts.tsv row (http 200);
     at least one snapshot is named
  L5 quotes: every double-quoted span in ENTRY's `## Gate` has 4..25 words; at least one quote
  L6 rows: every S-id on ENTRY's `source:` lines is a registry row; at least one of them has opened=2026-10-26;
     every https URL in the Gate occurs in the source cell of a cited row
  L7 no reserved-TLD host (.test .example .invalid .localhost) in ENTRY or its cited rows
  L8 measured: ENTRY names census/round-30/records/jj-keep-expiry-run.txt; that blob exists at REV, has a line
     starting `jj-version: jj 0.45.1` and >= 3 lines starting `RESULT `; ENTRY contains `refs/jj/keep` and `util gc`
  L9 sources-census: scripts/sources-census.sh validate --file <exported corpus/SOURCES.md> exits 0
SUMMARY legs=9 fail=<n> f1_entries=<k> rev=REV ; exit 0 iff fail=0, 1 otherwise, 2 could-not-evaluate.
"""
import argparse, hashlib, os, re, shutil, subprocess, sys, tempfile

ENTRY = "corpus/knowledge/jj-keep-ref-expiry.md"
RUN = "census/round-30/records/jj-keep-expiry-run.txt"
FLEET_CENSUS = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"


def blob(root, rev, path, text=True):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    if p.returncode:
        return None
    return p.stdout.decode("utf-8", "replace") if text else p.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r30/c3-counter")
    a = ap.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", a.rev):
        print("COULD-NOT-EVALUATE rev must be a full 40-hex revision")
        return 2
    R, V = os.path.abspath(a.root), a.rev
    res = []

    def leg(n, ok, why=""):
        res.append(bool(ok))
        print(f"{n} {'PASS' if ok else 'FAIL'} {why}")

    g = subprocess.run(["git", "-C", R, "grep", "-lE", r"^ground: F1\b", V, "--", "corpus/knowledge/"], capture_output=True, text=True).stdout.split()
    leg("L1", len(g) == 3, f"f1_entries={len(g)}")
    os.makedirs(a.scratch, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="c3.", dir=a.scratch)
    try:
        t = subprocess.run(["git", "-C", R, "archive", V], capture_output=True)
        ok = t.returncode == 0 and subprocess.run(["tar", "-x", "-C", tmp], input=t.stdout, capture_output=True).returncode == 0
        if not ok:
            print("COULD-NOT-EVALUATE export failed")
            return 2
        cov = subprocess.run([sys.executable, "-B", os.path.join(tmp, "tools/souji-coverage-agreement.py"), "--root", R, "--rev", V],
                             capture_output=True, text=True).stdout.strip()
        leg("L2", cov == "grounded=16 mapped=16 dangling=0 mismatches=0", f'coverage="{cov}"')
        if os.path.isfile(os.path.join(tmp, ENTRY)):
            gc = subprocess.run([sys.executable, "-B", "tools/souji-gate-check.py", "--root", ".", "--round-date", "2026-10-26",
                                 "--entries", ENTRY, "--snapshot-dir", "census/round-30/sources",
                                 "--slice", "census/round-30/records/empty-slice",
                                 "--slice-verdicts", "census/round-30/records/empty-verdicts"],
                                capture_output=True, text=True, cwd=tmp, env=dict(os.environ, TMPDIR=tmp))
            line = [x for x in (gc.stdout + gc.stderr).splitlines() if x.startswith("entries=")]
            leg("L3", gc.returncode == 0 and line == ["entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0"],
                f'gate="{line[0] if line else "none"}" rc={gc.returncode}')
        else:
            leg("L3", False, "entry absent")
        cz = subprocess.run([FLEET_CENSUS, "validate", "--file", os.path.join(tmp, "corpus/SOURCES.md")], capture_output=True, text=True)
        census_rc = cz.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    reg = blob(R, V, "corpus/SOURCES.md") or ""
    rows = {}
    for l in reg.splitlines():
        if re.match(r"^ {0,3}\|\s*S\d{3,}\s*\|", l):
            c = [x.strip() for x in l.split("|")]
            rows[c[1]] = c
    e = blob(R, V, ENTRY) or ""
    gate = e[e.find("\n## Gate"):] if "\n## Gate" in e else ""
    sums = {}
    for l in (blob(R, V, "census/round-30/sources/SHA256SUMS") or "").splitlines():
        f = l.split()
        if len(f) == 2:
            sums[f[1]] = f[0]
    fr = {}
    for l in (blob(R, V, "census/round-30/records/fetch-receipts.tsv") or "").splitlines()[1:]:
        f = l.split("\t")
        if len(f) >= 6:
            fr[f[5].split(" ")[0]] = (f[1], f[4])
    snaps = sorted(set(re.findall(r"snapshot:\s*`?([^\s`]+)", gate)))
    bad4 = []
    for sp in snaps:
        data = blob(R, V, sp, text=False)
        h = hashlib.sha256(data).hexdigest() if data is not None else None
        if data is None or len(data) < 512 or sums.get(os.path.basename(sp)) != h or fr.get(sp, ("", ""))[1] != h or fr.get(sp, ("", ""))[0] != "200":
            bad4.append(sp)
    leg("L4", e and snaps and not bad4, f"snapshots={len(snaps)} bad={bad4}")
    quotes = re.findall(r'"([^"]{2,400})"', gate)
    bad5 = [q[:30] for q in quotes if not 4 <= len(q.split()) <= 25]
    leg("L5", quotes and not bad5, f"quotes={len(quotes)} bad={bad5}")
    cited = set(re.findall(r"S\d{3,}", " ".join(l for l in e.splitlines() if re.match(r"^(?:- )?source:", l))))
    missing = sorted(i for i in cited if i not in rows)
    fresh = sorted(i for i in cited if i in rows and rows[i][9] == "2026-10-26")
    cellurls = " ".join(rows[i][2] for i in cited if i in rows)
    bad6 = [u for u in set(re.findall(r'https://[^\s)"`>|]+', gate)) if u.rstrip(".,;") not in cellurls]
    leg("L6", cited and not missing and fresh and not bad6, f"cited={sorted(cited)} missing={missing} opened_today={fresh} url_unbound={bad6}")
    bad7 = [u for u in re.findall(r"https?://([^/\s)\"`>|]+)", e + cellurls) if re.search(r"\.(test|example|invalid|localhost)$", u)]
    leg("L7", e and not bad7, f"bad={bad7}")
    run = blob(R, V, RUN) or ""
    nres = sum(1 for l in run.splitlines() if l.startswith("RESULT "))
    ok8 = RUN in e and any(l.startswith("jj-version: jj 0.45.1") for l in run.splitlines()) and nres >= 3 and "refs/jj/keep" in e and "util gc" in e
    leg("L8", ok8, f"run_record={'present' if run else 'absent'} results={nres}")
    leg("L9", census_rc == 0, f"sources-census rc={census_rc}")
    print(f"SUMMARY legs={len(res)} fail={res.count(False)} f1_entries={len(g)} rev={V}")
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
