#!/usr/bin/env python3
"""R41w2mutationtester04 helper: single-defect mutants of tools/souji-worktree-drift.py scored by
r39, r40 and r41 fixtures separately, using the r1-counter.py kill contract:
  killed = fixture SUMMARY `cases=` present AND rc==1 AND fail>0 AND no Traceback on the fixture's stderr.
Reads the pinned revision with `git show` (read-only). Writes only under SCR (scratch) and prints results.
CLI: python3 -B mutate-r1.py [--scratch DIR]
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import py_compile
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "1d41c13574db80fdd9a4bde490b712da7ce2a85f"
TOOL = "tools/souji-worktree-drift.py"
PRISTINE_SHA256 = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"
FIXTURES = {
    "r39": "tests/fixtures/r39-drift-record-rules.py",
    "r40": "tests/fixtures/r40-drift-record-branches.py",
    "r41": "tests/fixtures/r41-drift-record-order.py",
}
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}

# (id, description, old anchor, new text, predicted killers before running)
MUTANTS = [
    ("X01", "discover: symlinked child no longer skipped",
     "        if os.path.islink(path):", "        if False:", []),
    ("X02", "discover: worktree-style `.git` file no longer recognised (child)",
     '        if os.path.isdir(os.path.join(path, ".git")) or os.path.isfile(os.path.join(path, ".git")):',
     '        if os.path.isdir(os.path.join(path, ".git")):', []),
    ("X03", "repo_path: direct branch ignores a `.git` file",
     '    if os.path.isdir(os.path.join(direct, ".git")) or os.path.isfile(os.path.join(direct, ".git")):',
     '    if os.path.isdir(os.path.join(direct, ".git")):', []),
    ("X04", "repo_path: direct branch returns None (positive control)",
     "        return direct", "        return None", ["r39", "r40", "r41"]),
    ("X05", "main: --skip-unrecorded guard inverted",
     "    if not args.skip_unrecorded:", "    if args.skip_unrecorded:", ["r40", "r41"]),
    ("X06", "discovery loop: recorded names no longer filtered out",
     "            if name not in recorded:", "            if True:", ["r41"]),
    ("X07", "run: live_recorded not incremented (SUMMARY live_repos)",
     "        live_recorded += 1", "        pass", ["r41"]),
    ("X08", "run: live_regs accumulates the RECORD figure, not the live one",
     "        live_regs += regs", '        live_regs += row["regs"]', []),
    ("X09", "run: PRUNABLE-CHANGED class never emitted",
     '        if prunable != row["prunable"]:', "        if False:", []),
    ("X10", "run: REGS-CHANGED emitted only when live < record",
     '        if regs != row["regs"]:', '        if regs < row["regs"]:', ["r41"]),
    ("X11", "measure: `worktree list` failure ignored",
     "    if listed.returncode != 0:", "    if False:", []),
    ("X12", "measure: `worktree prune --dry-run` failure ignored",
     "    if dry.returncode != 0:", "    if False:", []),
    ("X13", "run: drift rows printed in discovery order, not sorted",
     "    for cls, name, detail in sorted(drift):", "    for cls, name, detail in drift:", []),
    ("X14", "parse_record: duplicate REPO name accepted",
     '                raise Refusal("RECORD-MALFORMED: line %d duplicates %s" % (lineno, name))',
     "                pass", []),
    ("X15", "parse_record: RECORD-EMPTY refusal removed",
     "    if not rows:", "    if False:", ["r39"]),
    ("X16", "parse_record: TOTAL regs checked with `<` (only short totals refused)",
     '        if total["regs"] != sum(r["regs"] for r in rows):',
     '        if total["regs"] < sum(r["regs"] for r in rows):', ["r41"]),
    ("X17", "parse_record: TOTAL repos checked with `>` (only long totals refused)",
     '        if total["repos"] != len(rows):', '        if total["repos"] > len(rows):', ["r40", "r41"]),
    ("X18", "run: SUMMARY drift_rows subtracts unreachable",
     '        "drift_rows": len(drift),', '        "drift_rows": len(drift) - unreachable,', []),
    ("X19", "run: SUMMARY record_regs sums the prunable column",
     '        "record_regs": sum(r["regs"] for r in rows),',
     '        "record_regs": sum(r["prunable"] for r in rows),', []),
    ("X20", "run: REGS-CHANGED emitted only when live > record (complement of X10)",
     '        if regs != row["regs"]:', '        if regs > row["regs"]:', ["r41"]),
    ("X21", "run: live_prunable not accumulated (SUMMARY live_prunable)",
     "        live_prunable += prunable", "        pass", []),
    ("X22", "run: RECORD-OUTSIDE-ROOT gitdir refusal disabled (.git file pointing outside root)",
     "                if not gitdir_inside:", "                if False:", []),
    ("X23", "repo_path: root-basename fallback returns None (root row reads ABSENT)",
     "        return root", "        return None", ["r41"]),
    ("X24", "discover: root repository inserted at the end, not the front (equivalent under sorted output)",
     "        names.insert(0, os.path.basename(root.rstrip(\"/\")) or \"root\")",
     "        names.append(os.path.basename(root.rstrip(\"/\")) or \"root\")", []),
]


def show(path):
    proc = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (REV, path)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=dict(GIT_ENV, PATH=os.environ["PATH"]),
                          check=False)
    if proc.returncode != 0:
        raise SystemExit("git show failed for %s: %s" % (path, proc.stderr.decode(errors="replace")))
    return proc.stdout


def run_fixture(tag, fname, fixture_path, tool_path, work):
    os.makedirs(work, exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": work}
    env.update(GIT_ENV)
    proc = subprocess.run(["python3", "-B", fixture_path, "--tool", tool_path, "--work", work],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
                          check=False, timeout=900)
    summ = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
    m = re.search(r"cases=(\d+) pass=(\d+) fail=(\d+)", summ[-1]) if summ else None
    crash = "Traceback (most recent call last)" in proc.stderr
    failing = [l.split("=", 1)[0][5:] for l in proc.stdout.splitlines()
               if l.startswith("case-") and "=FAIL" in l]
    tool_tb = sum(1 for l in proc.stdout.splitlines() if l.startswith("case-") and "=FAIL" in l
                  and "Traceback" in l)
    res = {"fixture": tag, "rc": proc.returncode, "cases": None, "pass": None, "fail": None,
           "crash_stderr": crash, "failing": failing, "tool_traceback_in_failing_case": tool_tb,
           "summary": summ[-1] if summ else None}
    if m:
        res["cases"], res["pass"], res["fail"] = int(m.group(1)), int(m.group(2)), int(m.group(3))
    res["killed"] = (res["cases"] is not None and proc.returncode == 1 and res["fail"] > 0
                     and not crash)
    return res


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default="/fast/scratch/hyaku/souji-r41/R41w2mutationtester04")
    args = ap.parse_args(argv)
    scr = os.path.abspath(args.scratch)
    os.makedirs(os.path.join(scr, "fx"), exist_ok=True)
    os.makedirs(os.path.join(scr, "mut"), exist_ok=True)
    src_bytes = show(TOOL)
    sha = hashlib.sha256(src_bytes).hexdigest()
    print("pristine tool sha256=%s match=%s" % (sha, sha == PRISTINE_SHA256))
    if sha != PRISTINE_SHA256:
        return 2
    src = src_bytes.decode("utf-8")
    fx_paths = {}
    for tag, path in FIXTURES.items():
        p = os.path.join(scr, "fx", os.path.basename(path))
        with open(p, "wb") as handle:
            handle.write(show(path))
        fx_paths[tag] = p
    pristine_tool = os.path.join(scr, "mut", "pristine.py")
    with open(pristine_tool, "wb") as handle:
        handle.write(src_bytes)
    jobs = []
    for tag in FIXTURES:
        jobs.append(("PRISTINE", tag, fx_paths[tag], pristine_tool))
    anchor_problems = []
    for mid, desc, old, new, _pred in MUTANTS:
        n = src.count(old)
        if n != 1:
            anchor_problems.append((mid, n))
            continue
        msrc = src.replace(old, new)
        if msrc == src:
            anchor_problems.append((mid, "no-op"))
            continue
        mpath = os.path.join(scr, "mut", mid + ".py")
        with open(mpath, "w", encoding="utf-8") as handle:
            handle.write(msrc)
        try:
            py_compile.compile(mpath, cfile=os.path.join(scr, "mut", mid + ".pyc"), doraise=True)
            compiles = True
        except py_compile.PyCompileError:
            compiles = False
        if not compiles:
            anchor_problems.append((mid, "does-not-compile"))
            continue
        for tag in FIXTURES:
            jobs.append((mid, tag, fx_paths[tag], mpath))
    if anchor_problems:
        print("ANCHOR-PROBLEMS", anchor_problems)
        return 2
    results = {}
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        futs = {}
        for mid, tag, fxp, tp in jobs:
            work = os.path.join(scr, "work", mid, tag)
            futs[pool.submit(run_fixture, tag, os.path.basename(fxp), fxp, tp, work)] = (mid, tag)
        for fut in cf.as_completed(futs):
            results[futs[fut]] = fut.result()
    out = {"pristine": {t: results[("PRISTINE", t)] for t in FIXTURES}, "mutants": []}
    print("PRISTINE " + " ".join("%s:cases=%s,fail=%s,rc=%s,clean=%s" % (
        t, results[("PRISTINE", t)]["cases"], results[("PRISTINE", t)]["fail"],
        results[("PRISTINE", t)]["rc"],
        results[("PRISTINE", t)]["rc"] == 0 and results[("PRISTINE", t)]["fail"] == 0) for t in FIXTURES))
    print("%-4s %-6s %-40s %-14s %-14s %-14s %s" % ("id", "kills", "desc", "r39", "r40", "r41", "predicted"))
    for mid, desc, old, new, pred in MUTANTS:
        row = {"id": mid, "desc": desc, "predicted": pred, "by": []}
        cells = []
        for tag in FIXTURES:
            r = results[(mid, tag)]
            row[tag] = r
            if r["killed"]:
                row["by"].append(tag)
            cells.append("%s(%s/%s)" % ("KILL" if r["killed"] else "live", r["fail"], r["cases"]))
        row["pred_match"] = sorted(pred) == sorted(row["by"])
        out["mutants"].append(row)
        print("%-4s %-6s %-40s %-14s %-14s %-14s %s match=%s" % (
            mid, ",".join(row["by"]) or "-", desc[:40], cells[0], cells[1], cells[2],
            ",".join(pred) or "-", row["pred_match"]))
    with open(os.path.join(scr, "results.json"), "w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=1, sort_keys=True)
    survive_all = [r["id"] for r in out["mutants"] if not r["by"]]
    print("SURVIVE-ALL-THREE " + ",".join(survive_all))
    print("KILLED-COUNT %d/%d" % (len(out["mutants"]) - len(survive_all), len(out["mutants"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
