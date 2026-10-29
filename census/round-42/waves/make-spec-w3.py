#!/usr/bin/env python3
"""Builds .ufo/waves/round-42/w3-spec.json (run-12 resume residual: complete the wave-2
items the operator wrap-up stopped — 4 attack seats, <=8 residual cap). Run: python3 make-spec-w3.py"""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
RD = LANE + "/census/round-42"
W = LANE + "/.ufo/waves/round-42/w3"
W2 = LANE + "/.ufo/waves/round-42/w2"
W1 = LANE + "/census/round-42/waves/w1"
SCR = "/fast/scratch/hyaku/souji-r42"
BASE = "bf618f6c5c09d302994871c94903abbea2deb60d"
FREEZE = "afe17f416eec04dcf3f480b580a8f928de61d19d"
STOP = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
TIP = "6a3f75941d3604e3459011d599c2c16f3a97b44c"
GODSPEED = ("/skill:godspeed\n\n" + open(os.path.expanduser("~/.agents/skills/godspeed/directive.md"),
                                          encoding="utf-8").read().rstrip("\n") + "\n\n")

CONTEXT = f"""# Goal
souji round 42, wave 3 (resume falsification, run 12). Lane: {LANE}. The round landed during run 11 (base {BASE}, freeze {FREEZE}, SCORECARD landing {STOP}); the operator wrap-up (2026-10-28 ~23:35 -03) stopped wave 2 mid-flight and killed three seats; the round was re-dispatched and the final tip is now {TIP} (read `git -C {LANE} show {TIP}:<path>` or the working tree, which equals it; never write the lane). Wave 3 completes ONLY the stopped items: the axis-harm audit (was R42w2critic08, never started) and two mutation attacks (R42w2mutationtester01 — partial work exists; R42w2mutationtester03 — never started). Everything else already landed and is FROZEN for this wave.
# What landed (unchanged from run 11)
C1 calibration: {RD}/c1-register.tsv + corpus/lessons/round-42.md CORRECTION lines (counter {RD}/c1-counter.py; receipt {RD}/records/c1-after.txt). C2 operability: {LANE}/tools/souji-freeze-check.py (counter {RD}/c2-counter.py; receipt {RD}/records/c2-after.txt). C3 coverage: {LANE}/tests/fixtures/r42-drift-conditions.py (counter {RD}/c3-counter.py; receipt {RD}/records/c3-after.txt). R1: the two citations repointed to {RD}/jj-w1-reports/ (receipt {RD}/records/gate-both-modes.txt). Bookkeeping: SCORECARD.md (Round 42 sections at the end), LOG.md (Round 42 entry), corpus/QUALITY.md Q103-Q105, SKILL.md gate rows r42-*, corpus/README.md, corpus/SOURCES.md S259. Run-11 wave-1 attack reports: {W1}/; run-11 wave-2 attack reports: {W2}/<seat>.md; the round report: /home/vgpnk/Projects/shokunin/.ufo/reports/round-42/souji.md; the round lesson {LANE}/corpus/lessons/round-42.md carries `## Mistakes` M42-1..M42-6 and `## Corrections to filed statements` E-1..E-10.
Read {RD}/preregistration.txt first, then the lesson, then the artifacts your item names. The preregistration, the three counters, the populations, the controls, the pinned tool tools/souji-worktree-drift.py and every prior fixture are FROZEN: never edit them; a defect you find is a finding for the L1, never a fix by you.
# Scope and rules
Read-only findings unless your item assigns candidate files; a candidate, mutant or probe goes ONLY under its own directory {W}/<seat-name>/ and never into tests/, tools/, census/, corpus/, SKILL.md or any tracked file. No overlapping writers. Seats never commit, push or run any mutating git or jj command in the lane or fleet; the L1 alone lands through jj-lane.sh. Never write the fleet repo, sibling lanes, .ufo/state, the watchdog log, operator config, templates or fleet scripts. Use absolute lane paths. Never run as root; never signal processes you did not spawn. Leaf members: no subagent dispatch.
Scratch: every clone, mirror, fixture and work dir lives under {SCR}/<seat-name>/ (mkdir -p it, pass TMPDIR and --work/--scratch explicitly, never rely on an inherited TMPDIR; the counters refuse a --scratch that does not exist — create it first); /tmp only for files under 50 MB; delete your scratch dir before you yield (trap rm -rf in shell, finally: shutil.rmtree in Python) after copying any receipt you need into your report directory. A report may cite only paths that are committed or inside your seat directory; a /tmp or scratch path is never evidence.
Scoring or re-measuring: the counters run over a revision of a clone: `bash {RD}/score-candidate.sh <c1|c2|c3|r1> {SCR}/<seat-name> <dest=file>...` (dest allowlist: tools/souji-freeze-check.py, tests/fixtures/r42-drift-conditions.py, census/round-42/c1-register.tsv, corpus/lessons/round-42.md, SCORECARD.md, corpus/SOURCES.md, corpus/pointer-exemptions.tsv, corpus/README.md, corpus/knowledge/jj-colocation-receipts.md) scores your candidate over the committed tip plus your file; with no pairs it re-measures the tip. Or run a counter directly: `python3 -B {RD}/<claim>-counter.py --root {LANE} --rev {TIP} --scratch {SCR}/<seat-name>`. An unrun check has not passed. Paste SUMMARY lines verbatim.
Git fixtures: D=$(mktemp -d -p {SCR}/<seat-name>) then every git call names -C "$D" and git -C "$D" rev-parse --show-toplevel must equal $D before the first commit; pass any author identity through GIT_AUTHOR_*/GIT_COMMITTER_* environment variables only. Never use git commit, jj or git config anywhere else. Read-only jj in the lane only with --ignore-working-copy.
Tooling authorization (operator, 2026-10-19): you may install or upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate; record tool, version, channel, reason in your report). pacman guard: ALL pacman transactions are paused host-wide; install via uv tool/npx/an official binary in ~/.local/bin or file the need in your report; never -Sy, -Syu, -U, -R, downgrade or restart a host service.
Every Report trailer path is relative to {LANE}: write it at {LANE}/<that path>. Report exact commands run, their observed output and a verdict; unrun is not pass; never fabricate. Every finding names what it attacks. Return a summary of at most 10 lines."""

items = []


def add(name, role, axes, task, accept):
    prompt = GODSPEED + (f"# Target\nsouji round 42 wave 3 item {name} (role {role}; re-issued from the wrap-up-stopped wave 2"
                         f"{' — reuse the partial work after re-verifying it, citing reused vs redone' if name != 'R42w3critic01' and name != 'R42w3mutationtester01' else ''}).\n# Task\n{task}\n"
                         f"# Acceptance\nWrite your evidence report at {W}/{name}.md with exact evidence pointers, "
                         f"the commands you actually ran and their output, and a verdict. {accept}")
    items.append({"name": name, "role": role, "axes": axes, "prompt": prompt})


add("R42w3critic01", "critic", ["calibration", "operability", "coverage"],
    (f"Axis-harm audit (re-issues R42w2critic08, updated to the final tip). The admission rule says a trade anywhere is not an improvement; check each owned axis for harm by the round's landed changes, measured at {BASE} vs {TIP}: "
     f"(1) operability: the landed {LANE}/tools/souji-freeze-check.py is also invoked by other gate rows or fixtures (grep {LANE}/SKILL.md {LANE}/tests/ {LANE}/census for `freeze-check` consumers): run each cheap consumer against the base tool (`git -C {LANE} show {BASE}:tools/souji-freeze-check.py`) and the tip tool and compare exit codes and findings; "
     f"(2) coverage: prior drift fixtures unchanged — `git -C {LANE} diff {BASE} {TIP} --stat -- tests tools census/round-41` and name every changed file, judging each change (expected: the new r42 fixture and r42 census only); "
     f"(3) calibration: SCORECARD.md and LOG.md base lines unchanged (the diff must be pure appends — show any removed line) and the declared-evidence mismatch count not increased: `python3 -B {LANE}/tools/souji-declared-evidence.py --root {LANE} --rev {TIP} --file SCORECARD.md --format counts` (70 mismatches expected); "
     f"(4) run every SKILL.md `## Gate registry` row that has a cheap self-test or entry command at the base revision (a `git clone --shared` checkout of {BASE} under your scratch) and at the tip, same command: identical exit code and SUMMARY = identical (the six new r42-* rows exist only at the tip — an EXPECTED difference; a CHANGED result on a pre-r42 row is the harm signal; r41's N19 audit found 59 of 61 identical, use it as the baseline). Also audit the two post-landing errata commits `git -C {LANE} show {STOP}..{TIP}` for any base-line change beyond the lesson/SCORECARD errata text. "
     f"End with a per-axis verdict table: axis | harmed or unchanged | evidence."),
    "Table: gate row or check | base result | tip result | identical? Plus the per-axis harm verdict with counts.")

add("R42w3mutationtester01", "mutation-tester", ["operability"],
    (f"Mutation-test the LANDED tool {LANE}/tools/souji-freeze-check.py, part A (re-issues R42w2mutationtester01, which died mid-run). Inherited partial work: {W2}/R42w2mutationtester01/ holds scripts/ (mutants.py, run.py, classify.py, probes) and diffs/M01..M2x from the killed seat — re-verify what you reuse and say reused vs redone; finish the job it did not report. Generate at least 30 single-point mutants of the FIRST HALF of the file (comparisons, constants, regexes, branches, early returns, string literals of the finding classes), copy each into {SCR}/R42w3mutationtester01 and score each with the counter's case table ONLY (`bash {RD}/score-candidate.sh c2 {SCR}/R42w3mutationtester01 tools/souji-freeze-check.py=<mutant>`; read cases=, selftest= and patches= from the SUMMARY) and with the mutant's own `--selftest`. Classify each: killed by the counter cases / killed only by --selftest / survives both (equivalent — give the equivalence argument — or a gap). The survivors are the named coverage limits of C2."),
    "Table: mutant | change | counter cases | --selftest | verdict; survivor count with the equivalence/gap split.")

add("R42w3mutationtester02", "mutation-tester", ["coverage"],
    (f"Mutation-test the LANDED fixture {LANE}/tests/fixtures/r42-drift-conditions.py itself (re-issues R42w2mutationtester03, which never started). At least 30 single-point mutants of the FIXTURE (change an asserted exit code, a token, a count, remove a case's assertion, widen a timing bound, drop a case), each written under {SCR}/R42w3mutationtester02. Run each mutant fixture against the pristine tool and against the 13 population mutants listed by {RD}/c3-counter.py (see its MUTANTS table; score via `bash {RD}/score-candidate.sh c3 {SCR}/R42w3mutationtester02 tests/fixtures/r42-drift-conditions.py=<mutant-fixture>` in a scratch clone at {TIP}, or per the counter's docstring). A fixture mutant that still kills every population mutant and passes pristine is a redundant or vacuous assertion. C3 is load-sensitive: one mutant at a time, no parallel load, and report `uptime` before each batch. Report which cases are load-bearing (their removal loses a kill) and which assertions are never exercised."),
    "Table: fixture mutant | pristine | population mutants still killed | verdict; list of load-bearing cases.")

add("R42w3reviewer01", "reviewer", ["calibration", "operability", "coverage"],
    (f"Independent re-measurement of all three claims at the final tip (the run-11 receipts were taken at {STOP} and the L1 re-ran some; the closure needs an in-round independent receipt at {TIP}). Create {SCR}/R42w3reviewer01/c1 c2 c3 first (the counters refuse a missing --scratch). Run: `python3 -B {RD}/c1-counter.py --root {LANE} --rev {TIP} --scratch {SCR}/R42w3reviewer01/c1`; `python3 -B {RD}/c2-counter.py --root {LANE} --rev {TIP} --scratch {SCR}/R42w3reviewer01/c2`; `python3 -B tools/souji-landing-gate.py --root {LANE} --rev {TIP} --round 42` and the same with `--fleet-root /home/vgpnk/Projects/shokunin`; `python3 -B {RD}/c3-counter.py --root {LANE} --rev {TIP} --scratch {SCR}/R42w3reviewer01/c3` ONCE on as idle a host as you can get (check `uptime` first and after; do not run it under load — wave 2 established the load sensitivity, one idle-host measurement is the receipt). "
     f"Then compare every SUMMARY field against the committed receipts {RD}/records/c1-after.txt, c2-after.txt, c3-after.txt, gate-both-modes.txt and against the before→after table in /home/vgpnk/Projects/shokunin/.ufo/reports/round-42/souji.md (read-only). Report any field that differs from the receipts with the observed value, and say for each claim whether the after-state still reaches the frozen target at {TIP}."),
    "Table: counter | SUMMARY at tip | receipt value | every differing field. Verdict per claim: reaches target / not.")

if __name__ == "__main__":
    spec = {"wave": "souji-r42-w3", "milestone": "r42 resume: complete the wrap-up-stopped falsification",
            "reportDir": ".ufo/waves/round-42/w3",
            "context": CONTEXT, "items": items}
    out = os.path.join(LANE, ".ufo/waves/round-42/w3-spec.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(spec, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    from collections import Counter
    print(len(items), dict(Counter(i["role"] for i in items)))
