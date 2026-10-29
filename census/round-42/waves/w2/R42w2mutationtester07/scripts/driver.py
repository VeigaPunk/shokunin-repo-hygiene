#!/usr/bin/env python3
"""R42w2mutationtester07 — mutate a COPY of the frozen r42 C2 counter and re-score both artifacts."""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

FROZEN = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester07"
CLONE = os.path.join(SCRATCH, "clone-tip")
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
CONTROL_TOOL = "census/round-42/controls/c2-stub-tool.py"
LANDED_TOOL = "tools/souji-freeze-check.py"

BASE = open(FROZEN, encoding="utf-8").read()

# (id, region, description, old, new)
MUTANTS = [
 # ---------------- A: CASES expectation table ----------------
 ("A01", "CASES", "dup-target expectation class KEY-DUPLICATE -> FIELD-MISSING (expectation no longer the r42 class)",
  '("dup-target", {"dup": ("Target", "something else")}, 1, [("C1", "KEY-DUPLICATE")])',
  '("dup-target", {"dup": ("Target", "something else")}, 1, [("C1", "FIELD-MISSING")])'),
 ("A02", "CASES", "heading-valid-tail expects 6 FIELD-MISSING -> 5",
  '[("C2", "FIELD-MISSING")] * 6),', '[("C2", "FIELD-MISSING")] * 5),'),
 ("A03", "CASES", "population-empty expectation POPULATION-EMPTY -> POPULATION-DIGEST",
  '("population-empty", {"population": "id\\tname\\n"}, 1, [("C1", "POPULATION-EMPTY")])',
  '("population-empty", {"population": "id\\tname\\n"}, 1, [("C1", "POPULATION-DIGEST")])'),
 ("A04", "CASES", "counter-symlink expectation COUNTER-SYMLINK -> COUNTER-DIGEST (the r41 tool's actual class: weakens the control's rejection, reddens the landed tool)",
  '("counter-symlink", {"counter_symlink": True}, 1, [("C1", "COUNTER-SYMLINK")])',
  '("counter-symlink", {"counter_symlink": True}, 1, [("C1", "COUNTER-DIGEST")])'),
 ("A05", "CASES", "population-symlink expectation POPULATION-SYMLINK -> POPULATION-DIGEST (r41 emits the pair DIGEST+EMPTY, so the stub still fails but for a different reason)",
  '("population-symlink", {"population_symlink": True}, 1, [("C1", "POPULATION-SYMLINK")])',
  '("population-symlink", {"population_symlink": True}, 1, [("C1", "POPULATION-DIGEST")])'),
 ("A06", "CASES", "dispatch-spec-before claim label C0 -> C1 (prereg-wide label no longer prereg-wide)",
  '("dispatch-spec-before", {"before_files": ["w1-spec.json"]}, 1, [("C0", "DISPATCH-BEFORE-FREEZE")])',
  '("dispatch-spec-before", {"before_files": ["w1-spec.json"]}, 1, [("C1", "DISPATCH-BEFORE-FREEZE")])'),
 ("A07", "CASES", "clean case expects no finding -> expects NO-CLAIMS",
  '("clean", {}, 0, []),', '("clean", {}, 0, [("C0", "NO-CLAIMS")]),'),
 ("A08", "CASES", "case_ok drops the want_rc / want-class comparison entirely (counter accepts any non-crashing tool that prints a SUMMARY: vacuity)",
  '    ok = (rc == want_rc and got == sorted(want) and not crash and summ is not None\n          and summ[1] == len(want))',
  '    ok = (not crash and summ is not None)'),

 # ---------------- B: build() fixture helpers ----------------
 ("B01", "build", "the duplicated key is never written (dup fixture becomes a clean prereg)",
  '        claim["__extra"] = [(key, claim["Counter"] if value == "CLAIMCOUNTER" else value)]',
  '        claim["__extra"] = []'),
 ("B02", "build", "base_side fixture points Base at the main tip (BASE-NOT-ANCESTOR can no longer occur)",
  '    if mut.get("base_side"):\n        claim["Base"] = side',
  '    if mut.get("base_side"):\n        claim["Base"] = base'),
 ("B03", "build", "dispatch_before fixture writes a name the dispatch rule does not match (w1-notes.json)",
  '        write(".ufo/waves/round-42/w1-dispatch.json", "{}\\n")\n        commit("early dispatch")',
  '        write(".ufo/waves/round-42/w1-notes.json", "{}\\n")\n        commit("early dispatch")'),
 ("B04", "build", "the counter symlink is replaced by a regular file copy (the symlink case becomes a clean counter)",
  '        os.symlink("real-c1.py", os.path.join(d, "census/c1.py"))',
  '        write("census/c1.py", counter)'),
 ("B05", "build", "the prereg tail is never appended (the four malformed-heading fixtures lose their heading)",
  '        write("prereg.txt", prereg_text(claims) + mut.get("tail", ""))',
  '        write("prereg.txt", prereg_text(claims))'),
 ("B06", "build", "the post-freeze counter edit is a no-op rewrite of identical bytes (FROZEN-EDITED fixture becomes clean)",
  '        write("census/c1.py", counter + "# edited after freeze\\n")',
  '        write("census/c1.py", counter)'),

 # ---------------- C: the legs ----------------
 ("C01", "leg:real", "real leg drops the claims=3 requirement (only 'no findings' is left)",
  'if r_rc == 0 and not r_find and r_summ == (3, 0) and not r_crash:',
  'if r_rc == 0 and not r_find and r_summ is not None and not r_crash:'),
 ("C02", "leg:retro", "retro leg accepts >=1 finding instead of >=3",
  'if t_rc == 1 and len(t_find) >= 3 and not t_crash:',
  'if t_rc == 1 and len(t_find) >= 1 and not t_crash:'),
 ("C03", "leg:retro", "retro leg demands exit 0 instead of exit 1",
  'if t_rc == 1 and len(t_find) >= 3 and not t_crash:',
  'if t_rc == 0 and len(t_find) >= 3 and not t_crash:'),
 ("C04", "leg:retro_clean", "retro_clean leg drops the no-findings requirement",
  'retro_clean = "ok" if (c_rc == 0 and not c_find and c_summ == (3, 0) and not c_crash) else "FAIL"',
  'retro_clean = "ok" if (c_rc == 0 and c_summ == (3, 0) and not c_crash) else "FAIL"'),
 ("C05", "leg:selftest", "selftest leg accepts >=1 self-test case instead of >=12",
  'st_sum[0] >= 12', 'st_sum[0] >= 1'),
 ("C06", "leg:selftest", "selftest leg drops pass==cases",
  'st_sum[1] == st_sum[0]', 'st_sum[1] >= 0'),
 ("C07", "leg:patches", "only patch P1 is injected (patches=1/3)",
  'for patch in ("P1", "P2", "P3"):', 'for patch in ("P1",):'),
 ("C08", "leg:patches", "a patch counts as detected unless it timed out (an always-green selftest now counts 3/3: the control's patches leg is vacuous)",
  'patches += 1 if (selftest == "ok" and p_rc not in (0, 124)) else 0',
  'patches += 1 if (selftest == "ok" and p_rc != 124) else 0'),
 ("C09", "verdict", "the met() gate drops the requirement that the built-in clean stub is REJECTED",
  'met = (n == 37 and passed == n and stubs["control_clean"] == "REJECTED"',
  'met = (n == 37 and passed == n'),
 ("C10", "verdict", "the met() gate drops the patches==3 requirement",
  'and selftest == "ok" and patches == 3)', 'and selftest == "ok")'),

 # ---------------- D: the built-in stubs ----------------
 ("D01", "stubs", "STUB_CLEAN announces claims=0 instead of claims=1",
  "STUB_CLEAN = (\"import sys\\nprint('SUMMARY claims=1 findings=0')\\nsys.exit(0)\\n\")",
  "STUB_CLEAN = (\"import sys\\nprint('SUMMARY claims=0 findings=0')\\nsys.exit(0)\\n\")"),
 ("D02", "stubs", "STUB_FINDINGS emits FIELD-MISSING instead of NO-CLAIMS",
  "print('FINDING C1 NO-CLAIMS x')", "print('FINDING C1 FIELD-MISSING x')"),
 ("D03", "stubs", "a stub that passes every case is still labelled REJECTED (sp <= sn): the stub-rejection gate is vacuous",
  'stubs[label] = "REJECTED" if sp < sn else "ACCEPTED"',
  'stubs[label] = "REJECTED" if sp <= sn else "ACCEPTED"'),

 # ---------------- E: SITECUSTOMIZE / patch injection ----------------
 ("E01", "SITECUSTOMIZE", "P1 no longer reverses the digest (the patch is inert: the tool's own digest logic is not exercised)",
  "            return self._h.hexdigest()[::-1]", "            return self._h.hexdigest()"),
 ("E02", "SITECUSTOMIZE", "P2 matches a diff-filter the tool never uses (the patch is inert)",
  "if _p == 'P2' and argv[:1] == ['git'] and '--diff-filter=A' in argv:",
  "if _p == 'P2' and argv[:1] == ['git'] and '--diff-filter=AM' in argv:"),
 ("E03", "SITECUSTOMIZE", "P3 matches a git subcommand the tool never runs (the patch is inert)",
  "if _p == 'P3' and argv[:1] == ['git'] and 'merge-base' in argv:",
  "if _p == 'P3' and argv[:1] == ['git'] and 'merge-baseX' in argv:"),
 ("E04", "SITECUSTOMIZE", "PYTHONPATH is emptied, so sitecustomize never loads (no patch reaches the tool)",
  '        e["PYTHONPATH"] = pdir', '        e["PYTHONPATH"] = ""'),
 ("E05", "SITECUSTOMIZE", "the patch id is passed under a different env name than sitecustomize reads (the two halves of the patch mechanism are coupled by a literal)",
  '        e["SOUJI_R42_PATCH"] = patch', '        e["SOUJI_R42_PATCH_ALT"] = patch'),
 ("E06", "SITECUSTOMIZE", "the patch id default is P1 instead of empty (dead branch: sitecustomize is only on PYTHONPATH when a patch is requested)",
  '''    "_p = os.environ.get('SOUJI_R42_PATCH', '')\\n"''',
  '''    "_p = os.environ.get('SOUJI_R42_PATCH', 'P1')\\n"'''),

 # ---------------- F: run_tool / refusal checks ----------------
 ("F01", "run_tool", "the FINDING regex captures only the claim label, never the class (the class multiset is never compared)",
  're.finditer(r"^FINDING (\\S+) (\\S+)", p.stdout, re.M)',
  're.finditer(r"^FINDING (\\S+) ", p.stdout, re.M)'),
 ("F02", "run_tool", "the SUMMARY regex loses its anchors (a second SUMMARY line anywhere would be read)",
  're.findall(r"^SUMMARY claims=(\\d+) findings=(\\d+)\\s*$", p.stdout, re.M)',
  're.findall(r"SUMMARY claims=(\\d+) findings=(\\d+)", p.stdout, re.M)'),
 ("F03", "refusal", "the unresolved-revision refusal check drops the no-crash requirement",
  'r1[0] == 2 and "COULD-NOT-EVALUATE" in r1[4] and not r1[3],',
  'r1[0] == 2 and "COULD-NOT-EVALUATE" in r1[4],'),
 ("F04", "refusal", "the absent-prereg refusal check drops the no-crash requirement",
  'r2[0] == 2 and "COULD-NOT-EVALUATE" in r2[4] and not r2[3]]',
  'r2[0] == 2 and "COULD-NOT-EVALUATE" in r2[4]]'),
]


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_mutant(mid, old, new):
    if BASE.count(old) != 1:
        raise RuntimeError("%s: anchor occurs %d times" % (mid, BASE.count(old)))
    src = BASE.replace(old, new, 1)
    out = os.path.join(SEAT, "mutants", "%s.py" % mid)
    with open(out, "w", encoding="utf-8") as h:
        h.write(src)
    return out, src


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
    return {
        "id": mid, "tool": tool, "rc": p.returncode,
        "summary": summ[-1] if summ else None,
        "summary_fields": dict(re.findall(r"(\w+)=([^\s]+)", summ[-1])) if summ else None,
        "n_fail_cases": len(fails), "fail_cases": fails,
        "out": os.path.join(SEAT, "receipts", "%s.%s.txt" % (mid, "landed" if tool == LANDED_TOOL else "control")),
        "stdout": p.stdout,
    }


def main():
    os.makedirs(os.path.join(SEAT, "mutants"), exist_ok=True)
    os.makedirs(os.path.join(SEAT, "receipts"), exist_ok=True)
    os.makedirs(os.path.join(SCRATCH, "runs"), exist_ok=True)
    # pristine baseline through the same harness
    base_path = os.path.join(SEAT, "mutants", "BASE.py")
    with open(base_path, "w", encoding="utf-8") as h:
        h.write(BASE)

    jobs = [("BASE", base_path)]
    manifest = []
    for mid, region, desc, old, new in MUTANTS:
        path, src = build_mutant(mid, old, new)
        manifest.append({"id": mid, "region": region, "desc": desc,
                         "sha256": sha(src), "delta": src.count("\n") - BASE.count("\n")})
        jobs.append((mid, path))

    results = []
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        futs = {}
        for mid, path in jobs:
            for tool in (LANDED_TOOL, CONTROL_TOOL):
                futs[ex.submit(run_one, mid, path, tool)] = (mid, tool)
        for f in cf.as_completed(futs):
            mid, tool = futs[f]
            r = f.result()
            results.append(r)
            with open(r["out"], "w", encoding="utf-8") as h:
                h.write("$ python3 -B %s --root %s --rev %s --tool %s --scratch <scratch>\n"
                        % (os.path.join(SEAT, "mutants", mid + ".py"), CLONE, REV, tool))
                h.write(r["stdout"])
    results.sort(key=lambda r: (r["id"], r["tool"]))
    with open(os.path.join(SEAT, "receipts", "results.json"), "w", encoding="utf-8") as h:
        json.dump({"manifest": manifest, "results": results}, h, indent=1)
    print("done", len(results), "runs")


if __name__ == "__main__":
    main()
