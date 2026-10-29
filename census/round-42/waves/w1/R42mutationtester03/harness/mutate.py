#!/usr/bin/env python3
"""R42mutationtester03 mutant generator. Reads the FROZEN census/round-42/c3-counter.py (read only),
applies one single-point change per mutant (each anchor must occur exactly once), writes the mutant
files into the scratch root and the manifest (id, change, anchor count, sha256 of the mutant) into the
seat directory. MUT00 is the identity control: it must reproduce the frozen counter's output exactly.
"""
import hashlib
import json
import os
import sys

FROZEN = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c3-counter.py"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester03"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42mutationtester03"

# (id, class, change, old, new). `old` must occur exactly once in the frozen counter text.
M = [
    ("M00", "identity", "no change (control: mutant copy must equal the frozen counter)", "", ""),
    # --- killed(): the candidate-kill definition
    ("M01", "killed", "killed(): rc == 1 relaxed to rc != 0",
     "and rc == 1 and failed > 0 and not crash", "and rc != 0 and failed > 0 and not crash"),
    ("M02", "killed", "killed(): failed > 0 relaxed to failed >= 0",
     "and failed > 0 and not crash", "and failed >= 0 and not crash"),
    ("M03", "killed", "killed(): crash leg dropped",
     "and failed > 0 and not crash", "and failed > 0"),
    # --- clean(): the pristine-run test
    ("M04", "clean", "clean(): passed == cases relaxed to passed <= cases",
     "and passed == cases and not crash", "and passed <= cases and not crash"),
    ("M05", "clean", "clean(): rc == 0 leg dropped",
     "and rc == 0 and failed == 0", "and failed == 0"),
    ("M06", "clean", "clean(): crash leg dropped",
     "and passed == cases and not crash", "and passed == cases"),
    # --- run(): fixture execution and parsing
    ("M07", "run", "run(): last SUMMARY read as first (m[-1] -> m[0])", "m[-1]", "m[0]"),
    ("M08", "run", "run(): SUMMARY regex loses the probes= alternative",
     "(?:cases|probes)", "cases"),
    ("M09", "run", "run(): per-fixture timeout 300 s -> 4 s",
     "env=e, timeout=300)", "env=e, timeout=4)"),
    ("M10", "run", "run(): traceback test inverted (not in)",
     "in proc.stderr", "not in proc.stderr"),
    ("M11", "run", "run(): crash flag forced False on return",
     "return proc.returncode, c, p, f, crash", "return proc.returncode, c, p, f, False"),
    ("M12", "run", "run(): timeout branch crash flag False (equivalent: cases is None guards)",
     "return 124, None, None, None, True", "return 124, None, None, None, False"),
    ("M13", "run", "run(): no-SUMMARY branch reports cases 0 instead of None",
     "return proc.returncode, None, None, None, crash", "return proc.returncode, 0, 0, 0, crash"),
    ("M57", "run", "SUMMARY_RE loses re.M (anchored to string start only)",
     'fail=(\\d+)", re.M)', 'fail=(\\d+)")'),
    # --- main(): counting, labels and printed fields
    ("M14", "count", "killed_n counts every mutant", "killed_n += 1 if cand else 0", "killed_n += 1"),
    ("M15", "count", "old_killed counts mutants with no prior kill",
     "old_killed += 1 if by else 0", "old_killed += 1 if not by else 0"),
    ("M16", "count", "prior list keeps prior fixtures that ran, not only kills",
     "if (mid, p) in res and killed(res[(mid, p)])]\n            killed_n",
     "if (mid, p) in res]\n            killed_n"),
    ("M43", "count", "MUTANT prior= field prints full path, not basename",
     "[os.path.basename(p) for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]\n            killed_n",
     "[p for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]\n            killed_n"),
    ("M17", "count", "equiv_killed never counted", "equiv_killed += 1 if cand else 0",
     "equiv_killed += 0"),
    ("M18", "label", "EQUIV label KILLED/survived swapped", '"KILLED" if cand else "survived"',
     '"survived" if cand else "KILLED"'),
    ("M44", "label", "MUTANT label killed/SURVIVED swapped", '"killed" if cand else "SURVIVED"',
     '"SURVIVED" if cand else "killed"'),
    ("M19", "guard", "MUTANT candidate verdict defaults True when the fixture is absent",
     "if (mid, args.fixture) in res else False\n            by = [os.path.basename(p) for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]\n            killed_n",
     "if (mid, args.fixture) in res else True\n            by = [os.path.basename(p) for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]\n            killed_n"),
    ("M20", "guard", "MUTANT candidate lookup without its absent-fixture guard",
     "cand = killed(res[(mid, args.fixture)]) if (mid, args.fixture) in res else False\n            by = [os.path.basename(p) for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]\n            killed_n",
     "cand = killed(res[(mid, args.fixture)])\n            by = [os.path.basename(p) for p in PRIOR if (mid, p) in res and killed(res[(mid, p)])]\n            killed_n"),
    ("M21", "threshold", "pristine threshold cases >= 13 relaxed to >= 12", "cand_pre[1] >= 13",
     "cand_pre[1] >= 12"),
    ("M22", "threshold", "pristine threshold cases >= 13 tightened to > 13", "cand_pre[1] >= 13",
     "cand_pre[1] > 13"),
    ("M23", "guard", "pristine_ok drops the clean() leg", "(cand_pre is not None and clean(cand_pre) and cand_pre[1] >= 13)",
     "(cand_pre is not None and cand_pre[1] >= 13)"),
    ("M27", "guard", "pristine_ok drops the absent-candidate guard", "(cand_pre is not None and clean(cand_pre)",
     "(clean(cand_pre)"),
    ("M24", "printed", "cases printed as 0 always", "cases = cand_pre[1] if cand_pre and cand_pre[1] else 0",
     "cases = 0"),
    ("M25", "guard", "prior_ok without the presence guard", "if p in fixtures and clean(pre[p].result())",
     "if clean(pre[p].result())"),
    ("M26", "guard", "prior_ok counts a prior fixture as clean without checking it",
     "if p in fixtures and clean(pre[p].result())", "if p in fixtures and True"),
    ("M28", "met", "target met: EQUIV count 6 relaxed to 5", "and len(EQUIV) == 6 and equiv_killed",
     "and len(EQUIV) == 5 and equiv_killed"),
    ("M29", "exit", "exit code always 1 (met path lost)", "return 0 if met else 1", "return 1"),
    ("M30", "anchors", "population header row not skipped", "if n and len(f) >= 3:", "if len(f) >= 3:"),
    ("M31", "anchors", "population digest column read as column 1", "got[f[0]] = f[2]", "got[f[0]] = f[1]"),
    ("M32", "anchors", "expected digest computed from the NEW text",
     'old.encode("utf-8")).hexdigest() for mid, _d, old, _n in MUTANTS',
     '_n.encode("utf-8")).hexdigest() for mid, _d, old, _n in MUTANTS'),
    ("M33", "anchors", "anchors compares ids only, not digests",
     'anchors = "ok" if got == want else "FAIL"', 'anchors = "ok" if set(got) == set(want) else "FAIL"'),
    ("M34", "anchors", "anchor pre-check skips EQUIV (dead under pinned sha)",
     "for mid, _d, old, _new in MUTANTS + EQUIV:", "for mid, _d, old, _new in MUTANTS:"),
    ("M35", "anchors", "anchor pre-check count relaxed to > 1 (dead under pinned sha)",
     "if source.count(old) != 1:", "if source.count(old) > 1:"),
    ("M39", "pin", "PRISTINE_SHA256 first hex digit changed", 'PRISTINE_SHA256 = "b2a603', 'PRISTINE_SHA256 = "b2a604'),
    ("M71", "pin", "pinned-tool test inverted (!=)", "hashlib.sha256(tool_b).hexdigest() != PRISTINE_SHA256",
     "hashlib.sha256(tool_b).hexdigest() == PRISTINE_SHA256"),
    # --- rev / root / scratch
    ("M36", "rev", "REV regex accepts 39 hex digits", 'REV = re.compile(r"^[0-9a-f]{40}$")',
     'REV = re.compile(r"^[0-9a-f]{39,40}$")'),
    ("M37", "rev", "resolvability check dropped",
     "if not REV.match(args.rev) or not resolves(args.root, args.rev, scratch_root):",
     "if not REV.match(args.rev):"),
    ("M38", "root", "root refusal inverted (!= 0)", "os.geteuid() == 0", "os.geteuid() != 0"),
    ("M54", "root", "root refusal removed (equivalent for a non-root seat)",
     'if hasattr(os, "geteuid") and os.geteuid() == 0:', "if False:"),
    ("M40", "scratch", "scratch root prefers TMPDIR over --scratch",
     'scratch_root = args.scratch or os.environ.get("TMPDIR")',
     'scratch_root = os.environ.get("TMPDIR") or args.scratch'),
    ("M51", "scratch", "scratch directory not removed", "shutil.rmtree(scratch, ignore_errors=True)", "pass"),
    # --- execution shape
    ("M41", "exec", "fixture pool 8 workers -> 1 (timing only)", "max_workers=8", "max_workers=1"),
    ("M42", "exec", "prior fixtures not run in survey pass (or True removed)", "if args.survey or True:",
     "if args.survey:"),
    ("M47", "exec", "MUTANT lines printed in reverse order", "for mid, desc, _o, _n in MUTANTS:",
     "for mid, desc, _o, _n in reversed(MUTANTS):"),
    ("M48", "printed", "PRISTINE FIXTURE-ABSENT line printed when the fixture is present",
     "if args.fixture not in fixtures:", "if args.fixture in fixtures:"),
    ("M49", "exec", "mutant text replaced by itself (no mutation applied)",
     "source.replace(old, new), 0o755)", "source.replace(old, old), 0o755)"),
    ("M50", "exec", "EQUIV mutants not scheduled", "for mid, _d, old, new in MUTANTS + EQUIV:",
     "for mid, _d, old, new in MUTANTS:"),
    ("M52", "guard", "candidate grid scheduled without the presence guard",
     "if args.fixture in fixtures:\n                for mid, mp in jobs.items():",
     "if True:\n                for mid, mp in jobs.items():"),
    ("M53", "guard", "prior survey grid without the presence guard",
     "if p in fixtures:\n                            grid[(mid, p)]", "if True:\n                            grid[(mid, p)]"),
    ("M58", "run", "crash flag inverted in run()", "crash = \"Traceback (most recent call last)\" in proc.stderr",
     "crash = \"Traceback (most recent call last)\" not in proc.stderr"),
    ("M59", "printed", "SUMMARY survived= prints len(MUTANTS) regardless of kills",
     'len(MUTANTS) - killed_n, "ok"', 'len(MUTANTS), "ok"'),
    ("M60", "printed", "tool_sha printed to 11 hex digits", "hexdigest()[:12]))", "hexdigest()[:11]))"),
    ("M61", "clean", "clean(): failed == 0 relaxed to failed >= 0 (kill/clean share the leg)",
     "and rc == 0 and failed == 0 and passed", "and rc == 0 and failed >= 0 and passed"),
    ("M62", "anchors", "anchor sha of MUTANT rows not read (population row index)",
     "got[f[0]] = f[2]", "got[f[0]] = f[2] if False else f[2][:-1]"),
]


def main():
    sys.dont_write_bytecode = True
    with open(FROZEN, "rb") as h:
        src = h.read().decode("utf-8")
    mdir = os.path.join(SCRATCH, "mutants")
    os.makedirs(mdir, exist_ok=True)
    rows = []
    for mid, cls, desc, old, new in M:
        if mid == "M00":
            text, count = src, 1
        else:
            count = src.count(old)
            if count != 1:
                raise SystemExit("%s anchor occurs %d times" % (mid, count))
            text = src.replace(old, new)
        if text == src and mid != "M00":
            raise SystemExit("%s changed no bytes" % mid)
        path = os.path.join(mdir, "%s.py" % mid)
        with open(path, "wb") as h:
            h.write(text.encode("utf-8"))
        rows.append({"id": mid, "class": cls, "change": desc, "anchor_count": count,
                     "old": old, "new": new,
                     "mutant_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
                     "bytes_changed": len(text) - len(src)})
    with open(os.path.join(SEAT, "harness", "mutants.json"), "w") as h:
        json.dump(rows, h, indent=1)
    print("mutants written:", len(rows))
    for r in rows:
        print(r["id"], r["class"], r["mutant_sha256"], r["change"])


if __name__ == "__main__":
    main()
