#!/usr/bin/env python3
"""Batch G: second single-point mutant set for the r42 C2 counter + stacked vacuity combinations."""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess

FROZEN = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester07"
CLONE = os.path.join(SCRATCH, "clone-tip")
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
CONTROL_TOOL = "census/round-42/controls/c2-stub-tool.py"
LANDED_TOOL = "tools/souji-freeze-check.py"
BASE = open(FROZEN, encoding="utf-8").read()

# single-point mutants of the frozen counter
G = [
 ("G01", "CASES", "one case is deleted from the table (the counter's own case count drops below the target)",
  '    ("dup-base-differs", {"dup": ("Base", "0" * 40)}, 1, [("C1", "KEY-DUPLICATE")]),\n', ''),
 ("G02", "CASES", "the PRISTINE FAIL case count is off by one (dead path while the tool is present)",
  'total = len(CASES) + 2', 'total = len(CASES) + 1'),
 ("G03", "leg:retro", "the retro leg reads the r41 preregistration instead of the r40 one",
  'RETRO_PATH = "census/round-40/preregistration.txt"', 'RETRO_PATH = "census/round-41/preregistration.txt"'),
 ("G04", "leg:retro_clean", "the retro_clean leg reads the r40 preregistration instead of the r41 one",
  'CLEAN_RETRO_PATH = "census/round-41/preregistration.txt"', 'CLEAN_RETRO_PATH = "census/round-40/preregistration.txt"'),
 ("G05", "leg:real", "the real leg reads the r40 preregistration instead of this round's",
  'PREREG_PATH = "census/round-42/preregistration.txt"', 'PREREG_PATH = "census/round-40/preregistration.txt"'),
 ("G06", "build:prereg_text", "the emitted claim block omits the Kill key (every fixture claim is short one key)",
  'for key in ("Base", "Counter", "Population", "Control", "Target", "Kill"):',
  'for key in ("Base", "Counter", "Population", "Control", "Target"):'),
 ("G07", "build:prereg_text", "the emitted heading loses its em dash (the tool's heading grammar still accepts it)",
  'out.append("## C%d — claim %d" % (n, n))', 'out.append("## C%d claim %d" % (n, n))'),
 ("G08", "build:prereg_text", "the emitted heading becomes a level-3 heading (no claim block is opened at all)",
  'out.append("## C%d — claim %d" % (n, n))', 'out.append("### C%d — claim %d" % (n, n))'),
 ("G09", "case_ok", "the summary findings count check is weakened to a tautology (the class multiset check is the only one left)",
  'and summ[1] == len(want))', 'and summ[1] >= 0)'),
 ("G10", "case_ok", "the class multiset comparison becomes a set comparison (duplicate identical findings are forgiven)",
  'got = sorted(findings)\n    ok = (rc == want_rc and got == sorted(want)',
  'got = sorted(findings)\n    ok = (rc == want_rc and set(got) == set(want)'),
 ("G11", "build", "the duplicated key always carries the identical value (the 'differs' variant is never built)",
  'claim["__extra"] = [(key, claim["Counter"] if value == "CLAIMCOUNTER" else value)]',
  'claim["__extra"] = [(key, claim["Counter"])]'),
 ("G12", "build", "the fixture git identity is removed (the fixture commit cannot be made)",
  '"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",\n', ''),
 ("G13", "tool_sha", "the tool digest printed in SUMMARY is a constant instead of the scored bytes' digest",
  'hashlib.sha256(blob.stdout).hexdigest()[:12]))', '"0" * 12))'),
 ("G14", "verdict", "the met() gate accepts any case count at or above 30 (the 37-case table is not pinned)",
  'met = (n == 37 and passed == n', 'met = (n >= 30 and passed == n'),
 ("G15", "run_tool", "the crash detector is narrowed to the word Traceback anywhere in stderr",
  '    crash = "Traceback (most recent call last)" in p.stderr\n    return p.returncode, findings,',
  '    crash = "Traceback" in p.stderr\n    return p.returncode, findings,'),
]

# stacked combinations (NOT single-point; reported separately)
STACKS = [
 ("S1", ["A08", "C08", "C10"], "case-set check removed + patch leg counts a green selftest + patches==3 dropped from the verdict gate"),
 ("S2", ["A08", "C08"], "case-set check removed + patch leg counts a green selftest"),
 ("S3", ["A08", "C10"], "case-set check removed + patches==3 dropped from the verdict gate"),
 ("S4", ["G01", "G14"], "one case deleted from the table + the verdict gate accepts any count >= 30"),
]


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def apply_mut(mid, old, new):
    if BASE.count(old) != 1:
        raise RuntimeError("%s anchor count %d" % (mid, BASE.count(old)))
    return BASE.replace(old, new, 1)


def write_mut(mid, src):
    out = os.path.join(SEAT, "mutants", "%s.py" % mid)
    with open(out, "w", encoding="utf-8") as h:
        h.write(src)
    return out


def run_one(mid, path, tool):
    work = os.path.join(SCRATCH, "runs", mid, tool.replace("/", "_"))
    os.makedirs(work, exist_ok=True)
    env = dict(os.environ)
    env["TMPDIR"] = work
    cmd = ["python3", "-B", path, "--root", CLONE, "--rev", REV, "--tool", tool, "--scratch", work]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       env=env, timeout=1200, cwd=work)
    summ = [ln for ln in p.stdout.splitlines() if ln.startswith("SUMMARY ")]
    cases = [ln for ln in p.stdout.splitlines() if ln.startswith("case-")]
    fails = [ln for ln in cases if "=FAIL" in ln]
    out = os.path.join(SEAT, "receipts", "%s.%s.txt" % (mid, "landed" if tool == LANDED_TOOL else "control"))
    with open(out, "w", encoding="utf-8") as h:
        h.write("$ python3 -B %s --root %s --rev %s --tool %s --scratch <scratch>\n"
                % (path, CLONE, REV, tool))
        h.write(p.stdout)
    return {"id": mid, "tool": tool, "rc": p.returncode,
            "summary": summ[-1] if summ else None,
            "summary_fields": dict(re.findall(r"(\w+)=([^\s]+)", summ[-1])) if summ else None,
            "n_fail_cases": len(fails),
            "fail_cases": [x.split("=")[0][5:] for x in fails],
            "out": out}


def main():
    os.makedirs(os.path.join(SEAT, "mutants"), exist_ok=True)
    os.makedirs(os.path.join(SEAT, "receipts"), exist_ok=True)
    manifest = []
    srcs = {}
    for mid, region, desc, old, new in G:
        srcs[mid] = apply_mut(mid, old, new)
        write_mut(mid, srcs[mid])
        manifest.append({"id": mid, "region": region, "desc": desc, "sha256": sha(srcs[mid])})
    # stacks: apply each single-point mutation of the stack on top of BASE
    for sid, parts, desc in STACKS:
        src = BASE
        for p in parts:
            mid = p
            rec = [m for m in G if m[0] == mid]
            if rec:
                src = src.replace(rec[0][3], rec[0][4], 1)
            else:
                # pull A/C mutants from the first driver
                import importlib.util
                spec = importlib.util.spec_from_file_location("d", os.path.join(SCRATCH, "driver.py"))
                d = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(d)
                rec = [m for m in d.MUTANTS if m[0] == mid]
                src = src.replace(rec[0][3], rec[0][4], 1)
        srcs[sid] = src
        write_mut(sid, src)
        manifest.append({"id": sid, "region": "STACK " + "+".join(parts), "desc": desc,
                         "sha256": sha(src), "stack": parts})
    jobs = [(mid, os.path.join(SEAT, "mutants", mid + ".py")) for mid in srcs]
    results = []
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        futs = {}
        for mid, path in jobs:
            for tool in (LANDED_TOOL, CONTROL_TOOL):
                futs[ex.submit(run_one, mid, path, tool)] = (mid, tool)
        for f in cf.as_completed(futs):
            mid, tool = futs[f]
            results.append(f.result())
    results.sort(key=lambda r: (r["id"], r["tool"]))
    with open(os.path.join(SEAT, "receipts", "results-g.json"), "w", encoding="utf-8") as h:
        json.dump({"manifest": manifest, "results": results}, h, indent=1)
    print("done", len(results), "runs")


if __name__ == "__main__":
    main()
