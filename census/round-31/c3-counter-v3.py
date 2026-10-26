#!/usr/bin/env python3
"""r31 C3 coverage counter v3 = v2 (census/round-31/c3-counter-v2.py, amendment A0) plus leg L13 (amendment A1,
stricter-only, after wave-1 SwarmCritic30 reached the v1 and v2 targets with a fixture that runs the commands and
prints a heredoc: census/round-31/records/amendments.txt). v1 and v2 must also meet their targets.

v2 header (A0): v1 plus leg L12 (landed before any wave seat ran).

v1 header follows. F1 object lifetime behind a dropped keep ref.

Round 30 measured when a `refs/jj/keep/*` ref goes; its entry states "Ref removal is measured; object
removal is not". This claim moves that F1 edge class: one new entry, measured with real jj 0.45.1 and
git 2.56.0, on what keeps the abandoned commit's object present after its keep ref is gone and what
finally removes it. Reads committed bytes at --rev; the fixture is replayed from an export of --rev.

Legs:
  L1  F1-grounded entries: files in corpus/knowledge/ with a line `ground: F1` == 4 (base 3)
  L2  coverage agreement (tools/souji-coverage-agreement.py@REV) prints exactly
      `grounded=17 mapped=17 dangling=0 mismatches=0` (base grounded=16 mapped=16)
  L3  gate: tools/souji-gate-check.py@REV over the export, --round-date 2026-10-26 --entries ENTRY
      --snapshot-dir census/round-31/sources --slice census/round-31/records/empty-slice
      --slice-verdicts census/round-31/records/empty-verdicts -> rc 0 and
      `entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0`
  L4  snapshots: every `snapshot:` path in ENTRY's `## Gate` is a blob >= 512 bytes whose sha256 equals its
      census/round-31/sources/SHA256SUMS line and its census/round-31/records/fetch-receipts.tsv row
      (http 200); at least one snapshot is named
  L5  quotes: every double-quoted span in ENTRY's `## Gate` has 4..25 words; at least one quote
  L6  rows: every S-id on ENTRY's `source:` lines is a registry row at REV; at least one cited row is
      absent from the registry at --base and has opened=2026-10-26; every https URL in the Gate occurs in
      the source cell of a cited row
  L7  no reserved-TLD host (.test .example .invalid .localhost) in ENTRY or its cited rows
  L8  measured: ENTRY names RUN; RUN exists at REV with a line starting `jj-version: jj 0.45.1`, a line
      starting `git-version: git version 2.56`, >= 4 lines starting `RESULT `, at least one RESULT line
      with `object_present=no` and at least one with `object_present=yes`
  L9  replay: FIXTURE@REV run twice from the export with TMPDIR under --scratch; both runs exit 0 and
      their `RESULT ` lines equal RUN's `RESULT ` lines exactly (same lines, same order)
  L10 sentence-to-record: ENTRY carries >= 3 backticked spans starting `RESULT `; every such span is a
      whole line of RUN
  L11 sources-census: scripts/sources-census.sh validate --file <exported corpus/SOURCES.md> exits 0
  L12 reality (A0): FIXTURE@REV run once more with PATH led by a shim dir whose `jj` and `git` log their argv
      and exec the real binaries (resolved before the shim); ok iff it exits 0, its RESULT lines equal RUN's,
      and the log holds jj calls with `abandon` and `util gc` and git calls with `reflog expire`, `gc` and
      `cat-file -e` (a fixture that prints or copies a record without running jj and git fails)
  L13 remover subtraction (A1): FIXTURE@REV run twice more with a PATH shim that turns one remover into a no-op
      (exit 0, nothing executed): M1 neuters every `git ... reflog expire`, M2 neuters every `git ... gc` and
      `git ... prune` (including the `git gc` that `jj util gc` shells out to); every other call execs the real
      binary. ok iff each mutant run exits 0, prints the same number of RESULT lines as RUN, its RESULT lines
      differ from RUN's, and it has strictly fewer `object_present=no` lines than RUN (removing a remover can
      only keep objects). A fixture whose output does not depend on what jj and git actually did fails.
SUMMARY legs=13 fail=<n> f1_entries=<k> rev=REV ; exit 0 iff fail=0, 1 otherwise, 2 could-not-evaluate.
Target (v3, A1): `legs=13 fail=0 f1_entries=4`; v2 `legs=12 fail=0 f1_entries=4` and v1 `legs=11 fail=0 f1_entries=4` too.
"""
import argparse, hashlib, os, re, shutil, subprocess, sys, tempfile

ENTRY = "corpus/knowledge/jj-dropped-keep-object-lifetime.md"
RUN = "census/round-31/records/jj-object-clock-run.txt"
FIXTURE = "tests/fixtures/r31-jj-object-clock.sh"
FLEET_CENSUS = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"


def blob(root, rev, path, text=True):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    if p.returncode:
        return None
    return p.stdout.decode("utf-8", "replace") if text else p.stdout


def reg_rows(text):
    rows = {}
    for l in (text or "").splitlines():
        if re.match(r"^ {0,3}\|\s*S\d{3,}\s*\|", l):
            c = [x.strip() for x in l.split("|")]
            rows[c[1]] = c
    return rows


def results(text):
    return [l for l in (text or "").splitlines() if l.startswith("RESULT ")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r31/c3-counter")
    a = ap.parse_args()
    for v in (a.rev, a.base):
        if not re.fullmatch(r"[0-9a-f]{40}", v):
            print("COULD-NOT-EVALUATE revisions must be full 40-hex")
            return 2
    R, V = os.path.abspath(a.root), a.rev
    res = []

    def leg(n, ok, why=""):
        res.append(bool(ok))
        print(f"{n} {'PASS' if ok else 'FAIL'} {why}")

    g = subprocess.run(["git", "-C", R, "grep", "-lE", r"^ground: F1\b", V, "--", "corpus/knowledge/"],
                       capture_output=True, text=True).stdout.split()
    leg("L1", len(g) == 4, f"f1_entries={len(g)}")
    os.makedirs(a.scratch, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="c3.", dir=a.scratch)
    replay = []
    shim_res = (None, [], [])
    mutants = []
    try:
        exp = os.path.join(tmp, "x")
        os.makedirs(exp)
        t = subprocess.run(["git", "-C", R, "archive", V], capture_output=True)
        ok = t.returncode == 0 and subprocess.run(["tar", "-x", "-C", exp], input=t.stdout, capture_output=True).returncode == 0
        if not ok:
            print("COULD-NOT-EVALUATE export failed")
            return 2
        cov = subprocess.run([sys.executable, "-B", os.path.join(exp, "tools/souji-coverage-agreement.py"), "--root", R, "--rev", V],
                             capture_output=True, text=True).stdout.strip()
        leg("L2", cov == "grounded=17 mapped=17 dangling=0 mismatches=0", f'coverage="{cov}"')
        if os.path.isfile(os.path.join(exp, ENTRY)):
            gc = subprocess.run([sys.executable, "-B", "tools/souji-gate-check.py", "--root", ".", "--round-date", "2026-10-26",
                                 "--entries", ENTRY, "--snapshot-dir", "census/round-31/sources",
                                 "--slice", "census/round-31/records/empty-slice",
                                 "--slice-verdicts", "census/round-31/records/empty-verdicts"],
                                capture_output=True, text=True, cwd=exp, env=dict(os.environ, TMPDIR=tmp))
            line = [x for x in (gc.stdout + gc.stderr).splitlines() if x.startswith("entries=")]
            leg("L3", gc.returncode == 0 and line == ["entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0"],
                f'gate="{line[0] if line else "none"}" rc={gc.returncode}')
        else:
            leg("L3", False, "entry absent")
        fx = os.path.join(exp, FIXTURE)
        if os.path.isfile(fx):
            for i in range(2):
                td = os.path.join(tmp, f"run{i}")
                os.makedirs(td)
                p = subprocess.run(["bash", fx], cwd=exp, capture_output=True, text=True, timeout=900,
                                   env=dict(os.environ, TMPDIR=td))
                replay.append((p.returncode, results(p.stdout)))
            shim = os.path.join(tmp, "shim")
            os.makedirs(shim)
            log = os.path.join(tmp, "shim.log")
            for tool in ("jj", "git"):
                real = shutil.which(tool)
                with open(os.path.join(shim, tool), "w") as f:
                    f.write(f'#!/bin/sh\nprintf "%s %s\\n" {tool} "$*" >> "{log}"\nexec "{real}" "$@"\n')
                os.chmod(os.path.join(shim, tool), 0o755)
            td = os.path.join(tmp, "run-shim")
            os.makedirs(td)
            p = subprocess.run(["bash", fx], cwd=exp, capture_output=True, text=True, timeout=900,
                               env=dict(os.environ, TMPDIR=td, PATH=shim + os.pathsep + os.environ.get("PATH", "")))
            calls = open(log).read().splitlines() if os.path.exists(log) else []
            shim_res = (p.returncode, results(p.stdout), calls)
            for mname, cond in (("M1", 'case " $* " in *" reflog expire "*) exit 0;; esac'),
                                ("M2", 'for a in "$@"; do case "$a" in gc|prune) exit 0;; esac; done')):
                ms = os.path.join(tmp, "shim-" + mname)
                os.makedirs(ms)
                real = shutil.which("git")
                with open(os.path.join(ms, "git"), "w") as f:
                    f.write(f'#!/bin/sh\n{cond}\nexec "{real}" "$@"\n')
                os.chmod(os.path.join(ms, "git"), 0o755)
                td = os.path.join(tmp, "run-" + mname)
                os.makedirs(td)
                p = subprocess.run(["bash", fx], cwd=exp, capture_output=True, text=True, timeout=900,
                                   env=dict(os.environ, TMPDIR=td, PATH=ms + os.pathsep + os.environ.get("PATH", "")))
                mutants.append((mname, p.returncode, results(p.stdout)))
        cz = subprocess.run([FLEET_CENSUS, "validate", "--file", os.path.join(exp, "corpus/SOURCES.md")], capture_output=True, text=True)
        census_rc = cz.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    rows = reg_rows(blob(R, V, "corpus/SOURCES.md"))
    base_rows = reg_rows(blob(R, a.base, "corpus/SOURCES.md"))
    e = blob(R, V, ENTRY) or ""
    gate = e[e.find("\n## Gate"):] if "\n## Gate" in e else ""
    sums = {}
    for l in (blob(R, V, "census/round-31/sources/SHA256SUMS") or "").splitlines():
        f = l.split()
        if len(f) == 2:
            sums[f[1]] = f[0]
    fr = {}
    for l in (blob(R, V, "census/round-31/records/fetch-receipts.tsv") or "").splitlines()[1:]:
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
    fresh = sorted(i for i in cited if i in rows and i not in base_rows and rows[i][9] == "2026-10-26")
    cellurls = " ".join(rows[i][2] for i in cited if i in rows)
    bad6 = [u for u in set(re.findall(r'https://[^\s)"`>|]+', gate)) if u.rstrip(".,;") not in cellurls]
    leg("L6", cited and not missing and fresh and not bad6, f"cited={sorted(cited)} missing={missing} new_opened_today={fresh} url_unbound={bad6}")
    bad7 = [u for u in re.findall(r"https?://([^/\s)\"`>|]+)", e + cellurls) if re.search(r"\.(test|example|invalid|localhost)$", u)]
    leg("L7", e and not bad7, f"bad={bad7}")
    run = blob(R, V, RUN) or ""
    rl = results(run)
    ok8 = (RUN in e and any(l.startswith("jj-version: jj 0.45.1") for l in run.splitlines())
           and any(l.startswith("git-version: git version 2.56") for l in run.splitlines()) and len(rl) >= 4
           and any("object_present=no" in l.split() for l in rl) and any("object_present=yes" in l.split() for l in rl))
    leg("L8", ok8, f"run_record={'present' if run else 'absent'} results={len(rl)}")
    ok9 = len(replay) == 2 and all(rc == 0 and lines == rl for rc, lines in replay) and bool(rl)
    leg("L9", ok9, f"replays={[(rc, len(lines), lines == rl) for rc, lines in replay]}")
    spans = re.findall(r"`(RESULT [^`]+)`", e)
    bad10 = [s[:60] for s in spans if s not in rl]
    leg("L10", len(spans) >= 3 and not bad10, f"result_spans={len(spans)} not_in_record={bad10}")
    leg("L11", census_rc == 0, f"sources-census rc={census_rc}")
    src, slines, calls = shim_res
    jj = [c for c in calls if c.startswith("jj ")]
    gt = [c for c in calls if c.startswith("git ")]
    need = {"jj abandon": any(" abandon" in c for c in jj), "jj util gc": any("util gc" in c for c in jj),
            "git reflog expire": any("reflog expire" in c for c in gt), "git gc": any(re.search(r"(^| )gc( |$)", c[4:]) for c in gt),
            "git cat-file -e": any("cat-file -e" in c for c in gt)}
    ok12 = src == 0 and bool(rl) and slines == rl and all(need.values())
    leg("L12", ok12, f"rc={src} results_equal={slines == rl and bool(rl)} jj_calls={len(jj)} git_calls={len(gt)} missing={[k for k, v in need.items() if not v]}")
    nno = sum(1 for l in rl if "object_present=no" in l.split())
    det = []
    ok13 = len(mutants) == 2 and bool(rl)
    for mname, mrc, ml in mutants:
        mno = sum(1 for l in ml if "object_present=no" in l.split())
        ok = mrc == 0 and len(ml) == len(rl) and ml != rl and mno < nno
        det.append(f"{mname}:rc={mrc},lines={len(ml)},differs={ml != rl},no={mno}<{nno}={mno < nno}")
        ok13 = ok13 and ok
    leg("L13", ok13, " ".join(det) or "fixture absent")
    print(f"SUMMARY legs={len(res)} fail={res.count(False)} f1_entries={len(g)} rev={V}")
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
