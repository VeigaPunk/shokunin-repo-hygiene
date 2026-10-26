#!/usr/bin/env python3
"""r32 C3 coverage counter v2 = v1 (census/round-32/c3-counter.py, frozen at the preregistration
3ec84fc81b3243429c834a051880b0bcde06291c) plus amendment A1 (stricter-only, after wave-1 SwarmCritic35 met the v1 target
with a fixture that issues the shimmed calls, ignores their results and prints RESULT lines from constants, and with a
hand-written snapshot whose fetch receipt claims http 200 for a URL answering 404). v1 must also meet its target.
  L15 independent probe: the counter itself, with plain git (no jj, no fixture code), makes a repository with an
      unreachable commit B (refs and reflogs dropped), runs a default `git gc` once with B's loose files recent and
      once (fresh repository) with them backdated 30 days by os.utime; ok iff the record's
      `arm=recent step=gc-default obj=B` line says object_present=yes exactly when the probe's recent B is present,
      and the `arm=old step=gc-default obj=B` line says object_present=no exactly when the probe's old B is absent,
      and the probe's two outcomes differ.
  L16 call outcomes: in the L12 shim run the shims also log each call's exit status; ok iff every `jj ... abandon`
      and every `git ... gc` call exited 0, `git cat-file -e` calls exited both 0 and non-zero, and the number of
      `git cat-file -e` calls is at least the number of RESULT lines.
  L17 live provenance: every snapshot in census/round-32/records/fetch-receipts.tsv is re-fetched from its URL now
      (curl -fsSL, 60 s); ok iff each fetch succeeds and its sha256 equals the receipt's and the committed blob's.
SUMMARY legs=17; target (v2, A1): `legs=17 fail=0 f1_entries=5`; v1 `legs=14 fail=0 f1_entries=5` too.

v1 header follows. F1 — the abandoned object's own mtime clock.

Round 31 measured what keeps an abandoned jj commit's object present after its keep ref is gone (a descendant's
keep ref, a reflog entry) and named one keeper as sourced, not measured: the object's own modification time inside
the `gc.pruneExpire` window, and whether git's cruft packs change that keeper's reach (`corpus/README.md`
`### Frontier (r31)`; `corpus/knowledge/jj-dropped-keep-object-lifetime.md` wave-2 corrections). This claim moves
that F1 edge class: one new entry, measured with real jj 0.45.1 and git 2.56.0, on how the mtime clock decides an
unreferenced object's fate under `git gc`, including inside a cruft pack (per-object `.mtimes`).
Reads committed bytes at --rev; the fixture is replayed from a `git archive` export of --rev.

Legs:
  L1  F1-grounded entries: files in corpus/knowledge/ with a line `ground: F1` == 5 (base 4)
  L2  coverage agreement (tools/souji-coverage-agreement.py@REV) prints exactly
      `grounded=18 mapped=18 dangling=0 mismatches=0` (base grounded=17 mapped=17)
  L3  gate: tools/souji-gate-check.py@REV over the export, --round-date 2026-10-26 --entries ENTRY
      --snapshot-dir census/round-32/sources --slice census/round-32/records/empty-slice
      --slice-verdicts census/round-32/records/empty-verdicts -> rc 0 and
      `entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0`
  L4  snapshots: every `snapshot:` path in ENTRY's `## Gate` is a blob >= 512 bytes whose sha256 equals its
      census/round-32/sources/SHA256SUMS line and its census/round-32/records/fetch-receipts.tsv row (http 200);
      at least one snapshot is named
  L5  quotes: every double-quoted span in ENTRY's `## Gate` has 4..25 words; at least one quote
  L6  rows: every S-id on ENTRY's `source:` lines is a registry row at REV; at least one cited row is absent from
      the registry at --base and has opened=2026-10-26; every https URL in the Gate occurs in the source cell of
      a cited row
  L7  no reserved-TLD host (.test .example .invalid .localhost) in ENTRY or its cited rows
  L8  measured: ENTRY names RUN; RUN exists at REV with a line starting `jj-version: jj 0.45.1`, a line starting
      `git-version: git version 2.56`, >= 8 lines starting `RESULT `, at least one with `object_present=no` and
      one with `object_present=yes`; every arm of the contract (recent old mixed never nocruft) has a RESULT line
      whose step starts `gc-`; arm `mixed` has gc-step lines for both obj=B and obj=C
  L9  replay: FIXTURE@REV run twice from the export with TMPDIR under --scratch; both exit 0 and their `RESULT `
      lines equal RUN's exactly (same lines, same order)
  L10 sentence-to-record: ENTRY carries >= 3 backticked spans starting `RESULT `; every one is a whole line of RUN
  L11 sources-census: scripts/sources-census.sh validate --file <exported corpus/SOURCES.md> exits 0
  L12 reality: FIXTURE@REV run once more with PATH led by a shim dir whose `jj`, `git` and `touch` log their argv
      and exec the real binaries; ok iff exit 0, RESULT lines equal RUN's, and the log holds a jj call with
      `abandon`, git calls with `reflog expire`, `update-ref -d`, `gc` and `cat-file -e`, and >= 1 touch call
  L13 remover/clock subtraction: FIXTURE@REV run twice more with one shim neutered (exit 0, nothing executed):
      M2 neuters every git call carrying a `gc`, `prune` or `repack` argument; M3 neuters every `touch` (no
      backdating). ok iff each mutant run exits 0, prints as many RESULT lines as RUN, its RESULT lines differ from
      RUN's, and it has strictly fewer `object_present=no` lines than RUN
  L14 contract (the r31 D1 guard): every RUN line starting `RESULT ` matches census/round-32/c3-contract.txt as
      frozen at --list-rev (keys in order, values in their enumerated sets), and that contract blob is unchanged
      at REV
SUMMARY legs=14 fail=<n> f1_entries=<k> rev=REV ; exit 0 iff fail=0, 1 otherwise, 2 could-not-evaluate.
Frozen target (preregistration): `legs=14 fail=0 f1_entries=5` at the C3 landing commit and at the tip.
"""
import argparse, hashlib, os, re, shutil, subprocess, sys, tempfile, time

ENTRY = "corpus/knowledge/jj-abandoned-object-mtime-clock.md"
RUN = "census/round-32/records/jj-mtime-clock-run.txt"
FIXTURE = "tests/fixtures/r32-jj-mtime-clock.sh"
CONTRACT = "census/round-32/c3-contract.txt"
FLEET_CENSUS = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"
ARMS = ("recent", "old", "mixed", "never", "nocruft")


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


def fields(line):
    return dict(f.split("=", 1) for f in line.split()[1:] if "=" in f)


def contract_bad(lines, ctext):
    prefix, keys = None, []
    for raw in (ctext or "").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        k, _, v = s.partition(":")
        if k == "prefix":
            prefix = v.strip()
        else:
            keys.append((k.strip(), set(v.strip().split("|"))))
    if prefix != "RESULT" or not keys:
        return ["contract unreadable"]
    bad = []
    for l in lines:
        got = [f.split("=", 1) for f in l.split()[1:]]
        if any(len(g) != 2 for g in got) or [g[0] for g in got] != [k for k, _ in keys]:
            bad.append(l[:60])
            continue
        if any(v not in allowed for (_, allowed), (_, v) in zip(keys, got)):
            bad.append(l[:60])
    return bad


def write_shim(d, name, body):
    with open(os.path.join(d, name), "w") as f:
        f.write(body)
    os.chmod(os.path.join(d, name), 0o755)


def probe(scratch):
    """L15: plain-git measurement of the mtime clock, independent of the fixture. Returns (recent_present, old_present)."""
    out = []
    for age in ("recent", "old"):
        d = tempfile.mkdtemp(prefix="probe-" + age + ".", dir=scratch)
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", HOME=d,
                   GIT_AUTHOR_NAME="p", GIT_AUTHOR_EMAIL="p@localhost", GIT_COMMITTER_NAME="p", GIT_COMMITTER_EMAIL="p@localhost")
        g = lambda *a: subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=env)
        g("init", "-q")
        open(os.path.join(d, "a"), "w").write("a\n"); g("add", "a"); g("commit", "-qm", "A")
        open(os.path.join(d, "b"), "w").write("b-" + age + "\n"); g("add", "b"); g("commit", "-qm", "B")
        b = g("rev-parse", "HEAD").stdout.strip()
        objs = [b, g("rev-parse", "HEAD^{tree}").stdout.strip(), g("rev-parse", "HEAD:b").stdout.strip()]
        g("reset", "-q", "--hard", "HEAD~1")
        g("reflog", "expire", "--expire=now", "--expire-unreachable=now", "--all")
        if age == "old":
            t = time.time() - 30 * 86400
            for o in objs:
                p = os.path.join(d, ".git", "objects", o[:2], o[2:])
                if os.path.exists(p):
                    os.utime(p, (t, t))
        g("gc", "-q")
        out.append(g("cat-file", "-e", b).returncode == 0)
        shutil.rmtree(d, ignore_errors=True)
    return tuple(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--list-rev", required=True, help="preregistration commit holding census/round-32/c3-contract.txt")
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r32/c3-counter")
    a = ap.parse_args()
    for v in (a.rev, a.base, a.list_rev):
        if not re.fullmatch(r"[0-9a-f]{40}", v):
            print("COULD-NOT-EVALUATE revisions must be full 40-hex")
            return 2
    R, V = os.path.abspath(a.root), a.rev
    real = {t: shutil.which(t) for t in ("jj", "git", "touch")}
    if not all(real.values()):
        print(f"COULD-NOT-EVALUATE missing binary {real}")
        return 2
    res = []

    def leg(n, ok, why=""):
        res.append(bool(ok))
        print(f"{n} {'PASS' if ok else 'FAIL'} {why}")

    g = subprocess.run(["git", "-C", R, "grep", "-lE", r"^ground: F1\b", V, "--", "corpus/knowledge/"],
                       capture_output=True, text=True).stdout.split()
    leg("L1", len(g) == 5, f"f1_entries={len(g)}")
    os.makedirs(a.scratch, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="c3.", dir=a.scratch)
    replay, shim_res, mutants, rcs = [], (None, [], []), [], []
    try:
        exp = os.path.join(tmp, "x")
        os.makedirs(exp)
        t = subprocess.run(["git", "-C", R, "archive", V], capture_output=True)
        ok = t.returncode == 0 and subprocess.run(["tar", "-x", "-C", exp], input=t.stdout, capture_output=True).returncode == 0
        if not ok:
            print("COULD-NOT-EVALUATE export failed")
            return 2
        cov = subprocess.run([sys.executable, "-B", os.path.join(exp, "tools/souji-coverage-agreement.py"), "--root", R, "--rev", V],
                             capture_output=True, text=True, env=dict(os.environ, TMPDIR=tmp)).stdout.strip()
        leg("L2", cov == "grounded=18 mapped=18 dangling=0 mismatches=0", f'coverage="{cov}"')
        if os.path.isfile(os.path.join(exp, ENTRY)):
            gc = subprocess.run([sys.executable, "-B", "tools/souji-gate-check.py", "--root", ".", "--round-date", "2026-10-26",
                                 "--entries", ENTRY, "--snapshot-dir", "census/round-32/sources",
                                 "--slice", "census/round-32/records/empty-slice",
                                 "--slice-verdicts", "census/round-32/records/empty-verdicts"],
                                capture_output=True, text=True, cwd=exp, env=dict(os.environ, TMPDIR=tmp))
            line = [x for x in (gc.stdout + gc.stderr).splitlines() if x.startswith("entries=")]
            leg("L3", gc.returncode == 0 and line == ["entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0"],
                f'gate="{line[0] if line else "none"}" rc={gc.returncode}')
        else:
            leg("L3", False, "entry absent")
        fx = os.path.join(exp, FIXTURE)

        def run_fx(tag, path_prefix=None):
            td = os.path.join(tmp, "run-" + tag)
            os.makedirs(td)
            env = dict(os.environ, TMPDIR=td)
            if path_prefix:
                env["PATH"] = path_prefix + os.pathsep + os.environ.get("PATH", "")
            try:
                p = subprocess.run(["bash", fx], cwd=exp, capture_output=True, text=True, timeout=1200, env=env)
                return p.returncode, results(p.stdout)
            except subprocess.TimeoutExpired:
                return 124, []

        if os.path.isfile(fx):
            for i in range(2):
                replay.append(run_fx(f"r{i}"))
            shim = os.path.join(tmp, "shim")
            os.makedirs(shim)
            log = os.path.join(tmp, "shim.log")
            for tool in ("jj", "git", "touch"):
                write_shim(shim, tool, f'#!/bin/sh\n"{real[tool]}" "$@"\nrc=$?\nprintf "%s %s\\n" {tool} "$*" >> "{log}"\nprintf "RC %s %s %s\\n" "$rc" {tool} "$*" >> "{log}.rc"\nexit $rc\n')
            rc, lines = run_fx("shim", shim)
            calls = open(log).read().splitlines() if os.path.exists(log) else []
            rcs = open(log + ".rc").read().splitlines() if os.path.exists(log + ".rc") else []
            shim_res = (rc, lines, calls)
            for mname, tool, cond in (
                    ("M2", "git", 'for x in "$@"; do case "$x" in gc|prune|repack) exit 0;; esac; done'),
                    ("M3", "touch", "exit 0")):
                ms = os.path.join(tmp, "shim-" + mname)
                os.makedirs(ms)
                write_shim(ms, tool, f'#!/bin/sh\n{cond}\nexec "{real[tool]}" "$@"\n')
                mrc, ml = run_fx(mname, ms)
                mutants.append((mname, mrc, ml))
        pr = probe(tmp)
        live = []
        for l in (blob(R, V, "census/round-32/records/fetch-receipts.tsv") or "").splitlines()[1:]:
            f = l.split("\t")
            if len(f) >= 6:
                q = subprocess.run(["curl", "-fsSL", "-m", "60", f[0]], capture_output=True)
                data = blob(R, V, f[5].split(" ")[0], text=False)
                live.append((f[5], q.returncode == 0 and hashlib.sha256(q.stdout).hexdigest() == f[4]
                             and data is not None and hashlib.sha256(data).hexdigest() == f[4]))
        cz = subprocess.run([FLEET_CENSUS, "validate", "--file", os.path.join(exp, "corpus/SOURCES.md")], capture_output=True, text=True)
        census_rc = cz.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    rows = reg_rows(blob(R, V, "corpus/SOURCES.md"))
    base_rows = reg_rows(blob(R, a.base, "corpus/SOURCES.md"))
    e = blob(R, V, ENTRY) or ""
    gate = e[e.find("\n## Gate"):] if "\n## Gate" in e else ""
    sums = {}
    for l in (blob(R, V, "census/round-32/sources/SHA256SUMS") or "").splitlines():
        f = l.split()
        if len(f) == 2:
            sums[f[1]] = f[0]
    fr = {}
    for l in (blob(R, V, "census/round-32/records/fetch-receipts.tsv") or "").splitlines()[1:]:
        f = l.split("\t")
        if len(f) >= 6:
            fr[f[5].split(" ")[0]] = (f[1], f[4])
    snaps = sorted(set(re.findall(r"snapshot:\s*`?([^\s`]+)", gate)))
    bad4 = []
    for sp in snaps:
        data = blob(R, V, sp, text=False)
        h = hashlib.sha256(data).hexdigest() if data is not None else None
        if (data is None or len(data) < 512 or sums.get(os.path.basename(sp)) != h
                or fr.get(sp, ("", ""))[1] != h or fr.get(sp, ("", ""))[0] != "200"):
            bad4.append(sp)
    leg("L4", e and snaps and not bad4, f"snapshots={len(snaps)} bad={bad4}")
    quotes = re.findall(r'"([^"]{2,400})"', gate)
    bad5 = [q[:30] for q in quotes if not 4 <= len(q.split()) <= 25]
    leg("L5", quotes and not bad5, f"quotes={len(quotes)} bad={bad5}")
    cited = set(re.findall(r"S\d{3,}", " ".join(l for l in e.splitlines() if re.match(r"^(?:- )?source:", l))))
    missing = sorted(i for i in cited if i not in rows)
    fresh = sorted(i for i in cited if i in rows and i not in base_rows and len(rows[i]) > 9 and rows[i][9] == "2026-10-26")
    cellurls = " ".join(rows[i][2] for i in cited if i in rows)
    bad6 = [u for u in set(re.findall(r'https://[^\s)"`>|]+', gate)) if u.rstrip(".,;") not in cellurls]
    leg("L6", cited and not missing and fresh and not bad6, f"cited={sorted(cited)} missing={missing} new_opened_today={fresh} url_unbound={bad6}")
    bad7 = [u for u in re.findall(r"https?://([^/\s)\"`>|]+)", e + cellurls) if re.search(r"\.(test|example|invalid|localhost)$", u)]
    leg("L7", e and not bad7, f"bad={bad7}")
    run = blob(R, V, RUN) or ""
    rl = results(run)
    fl = [fields(l) for l in rl]
    arms_gc = {f.get("arm") for f in fl if f.get("step", "").startswith("gc-")}
    mixed_objs = {f.get("obj") for f in fl if f.get("arm") == "mixed" and f.get("step", "").startswith("gc-")}
    ok8 = (RUN in e and any(l.startswith("jj-version: jj 0.45.1") for l in run.splitlines())
           and any(l.startswith("git-version: git version 2.56") for l in run.splitlines()) and len(rl) >= 8
           and any(f.get("object_present") == "no" for f in fl) and any(f.get("object_present") == "yes" for f in fl)
           and set(ARMS) <= arms_gc and {"B", "C"} <= mixed_objs)
    leg("L8", ok8, f"run_record={'present' if run else 'absent'} results={len(rl)} arms_with_gc={sorted(x for x in arms_gc if x)} mixed_objs={sorted(x for x in mixed_objs if x)}")
    ok9 = len(replay) == 2 and all(rc == 0 and lines == rl for rc, lines in replay) and bool(rl)
    leg("L9", ok9, f"replays={[(rc, len(lines), lines == rl) for rc, lines in replay]}")
    spans = re.findall(r"`(RESULT [^`]+)`", e)
    bad10 = [s[:60] for s in spans if s not in rl]
    leg("L10", len(spans) >= 3 and not bad10, f"result_spans={len(spans)} not_in_record={bad10}")
    leg("L11", census_rc == 0, f"sources-census rc={census_rc}")
    src, slines, calls = shim_res
    jj = [c for c in calls if c.startswith("jj ")]
    gt = [c[4:] for c in calls if c.startswith("git ")]
    tc = [c for c in calls if c.startswith("touch ")]
    need = {"jj abandon": any(" abandon" in c for c in jj),
            "git reflog expire": any("reflog expire" in c for c in gt),
            "git update-ref -d": any(re.search(r"(^| )update-ref -d( |$)", c) for c in gt),
            "git gc": any(re.search(r"(^| )gc( |$)", c) for c in gt),
            "git cat-file -e": any("cat-file -e" in c for c in gt),
            "touch": bool(tc)}
    ok12 = src == 0 and bool(rl) and slines == rl and all(need.values())
    leg("L12", ok12, f"rc={src} results_equal={slines == rl and bool(rl)} jj_calls={len(jj)} git_calls={len(gt)} touch_calls={len(tc)} missing={[k for k, v in need.items() if not v]}")
    nno = sum(1 for f in fl if f.get("object_present") == "no")
    det, ok13 = [], len(mutants) == 2 and bool(rl)
    for mname, mrc, ml in mutants:
        mno = sum(1 for l in ml if fields(l).get("object_present") == "no")
        ok = mrc == 0 and len(ml) == len(rl) and ml != rl and mno < nno
        det.append(f"{mname}:rc={mrc},lines={len(ml)},differs={ml != rl},no={mno}<{nno}={mno < nno}")
        ok13 = ok13 and ok
    leg("L13", ok13, " ".join(det) or "fixture absent")
    c_list, c_rev = blob(R, a.list_rev, CONTRACT), blob(R, V, CONTRACT)
    bad14 = contract_bad(rl, c_list) if c_list else ["contract absent at --list-rev"]
    ok14 = bool(rl) and c_list is not None and c_list == c_rev and not bad14
    leg("L14", ok14, f"lines={len(rl)} contract_unchanged={c_list is not None and c_list == c_rev} bad={bad14[:3]}")
    def rline(arm):
        x = [f for f in fl if f.get("arm") == arm and f.get("step") == "gc-default" and f.get("obj") == "B"]
        return x[0].get("object_present") if len(x) == 1 else None
    ok15 = pr[0] != pr[1] and rline("recent") == ("yes" if pr[0] else "no") and rline("old") == ("yes" if pr[1] else "no")
    leg("L15", ok15, f"probe recent_present={pr[0]} old_present={pr[1]} record recent={rline('recent')} old={rline('old')}")
    rcl = [r.split(" ", 3) for r in rcs if r.startswith("RC ")]
    ab = [x for x in rcl if len(x) == 4 and x[2] == "jj" and " abandon" in " " + x[3]]
    gcs = [x for x in rcl if len(x) == 4 and x[2] == "git" and re.search(r"(^| )gc( |$)", x[3])]
    cfe = [x for x in rcl if len(x) == 4 and x[2] == "git" and "cat-file -e" in x[3]]
    ok16 = (bool(ab) and all(x[1] == "0" for x in ab) and bool(gcs) and all(x[1] == "0" for x in gcs)
            and any(x[1] == "0" for x in cfe) and any(x[1] != "0" for x in cfe) and len(cfe) >= len(rl) > 0)
    leg("L16", ok16, f"abandon={len(ab)} nonzero={sum(x[1] != '0' for x in ab)} gc={len(gcs)} nonzero={sum(x[1] != '0' for x in gcs)} cat_file_e={len(cfe)} rc0={sum(x[1] == '0' for x in cfe)} results={len(rl)}")
    leg("L17", bool(live) and all(ok for _, ok in live), f"refetched={len(live)} bad={[p for p, ok in live if not ok]}")
    print(f"SUMMARY legs={len(res)} fail={res.count(False)} f1_entries={len(g)} rev={V}")
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
