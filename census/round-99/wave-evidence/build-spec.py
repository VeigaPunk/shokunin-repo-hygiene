#!/usr/bin/env python3
"""Build the souji r99 wave-1 spec (one v1 wave, 14 seats).

Run: python3 .ufo/waves/round-99/build-spec.py > .ufo/waves/round-99/w1-spec.json
Shape follows .ufo/waves/round-98/build-spec.py. Seats write only under their own wave dirs.
"""
import json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b"
W = f"{LANE}/.ufo/waves/round-99/w1"
SCR = "/fast/scratch/hyaku/souji-r99"
ROUND = 99
WAVE = "w1"

GOD = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

"""

CONTEXT = f"""# Goal
souji round 99 (lane repo {LANE}, lane id souji; lane base {BASE}). Two claims, successors routed by the round-98
non-author spot-check (corpus/lessons/round-98-verifier-spotcheck.md):
- C1 (calibration 7): the declared-exit shape table's labels are read from a L1-frozen file (census/round-99/shapes.tsv),
  not hard-coded, so the mismatched count cannot be moved by relabelling (M6). Hook stays the r98 object-keyed latch.
- C2 (operability 8): the arms counter's reap is restricted to the spawn pid and its ppid-chain descendants. Counter-
  descendant carriers that are not spawn-chain members are NEVER killed (branch (c) removed); the cross-arm probe must
  show them spared (R98Sentinel FINDING 4).
The L1 (SoujiR99) holds the planner seat and is the ONLY integration owner: it freezes predicates, commits through the
lane helper, measures and writes the report. You are one seat of ONE v1 wave of 12 seats. Seats deliver files and
findings only: never commit, never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit
MANIFEST.json, .ufo/state/*, .scratch/* or .ufo/watchdog.log, never touch /home/vgpnk/Projects/shokunin/considerthese
or /home/vgpnk/Projects/shokuknow (read-only or absent). A finding with a reproducer beats an opinion.

# Contract
- Every path in this wave is absolute under {LANE}. Relative paths land in the FLEET repo: never use them.
- Every `Report:` trailer path is relative to {LANE} — write it at {LANE}/<that path>.
- Scratch root: {SCR}/<your-seat-name>/ (mkdir -p; pass it explicitly, e.g. `--work <dir>`). Never use /tmp for anything
  over 50 MB; never write under /tmp for a counter; delete your scratch dir before you yield
  (`trap 'rm -rf -- "$S"' EXIT`). A seat that ends with its tree on disk reports that as its own defect.
- Routing: never pass `model`; the operator's `task.agentModelOverrides` decides.
- Tooling authorization (operator, 2026-10-19): you and every seat may install or upgrade tools that help the task; read
  /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate; record tool/version/channel/reason in your
  report). pacman guard: all pacman transactions are PAUSED host-wide — install via `uv tool`, `npx`, or an official binary
  in ~/.local/bin, or file an L0 question. Never `-Sy`, `-Syu`, `-U`, `-R`, or a downgrade.
- Seats must not mutate host sysctls (operator incident 2026-11-05): name a need in the report instead.
- Read-only git only (log, show, diff, status, ls-files, rev-parse). Never run git add/commit/stash/checkout/reset/pull/push
  and never run a mutating jj command.
- L0 questions: do not append to /home/vgpnk/Projects/shokunin/.ufo/l0-questions.md; report the question in your result and
  the L1 will append it.
- Honesty: an unrun check has not passed. Report exact commands, exit codes and the observed output lines.
- Reference instruments at lane base {BASE}: census/round-98/c1-survivor-search.py (r98 hook), census/round-98/declared-
  shapes.py, census/round-98/shapes/ (17 shapes), census/round-98/c2-setup-arms.py (r98 counter), census/round-98/
  c2-decoy-test.py, census/round-98/c2-cm8-mutant.py, census/round-98/c2-forgery-probe.py, census/round-98/controls/.
  Read them; do not edit them. Round-99 instruments are written under census/round-99/ by the executor seats named in
  your item; no seat edits a census/round-98 file.
- Predicates are frozen by the L1 after the wave lands; a seat that finds a predicate wrong reports it as a finding with a
  reproducer, never edits the predicate in place.

# Claims (round 99, for seat orientation)
- C1 (calibration 7): `census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv` prints
  `SHAPES-SUMMARY shapes=17 mismatched=0` with the r98 hook, kinds read from the frozen file; a relabelled copy of the
  file (same hook) moves the count, so the frozen file hash is part of the claim.
- C2 (operability 8): the r99 arms counter reaps only the recorded spawn pid and its ppid-chain descendants; a planted
  counter-descendant carrier outside the spawn chain survives (cross-arm probe), a foreign decoy survives (decoy test),
  and the r98 CM8 argv-only mutant is still killed by the decoy test.
- Sources: S372 (RERAISE), S075 (fields 5/6/22; field 4 via S332), S368 (setsid new process group). Re-open each live.

# Shape of the answers
Each seat returns, in its report file and final result: the command(s) run, exit code(s), the observed summary line(s), and a
list of findings each with a reproducer path under its own wave dir. No seat summarises without numbers.
"""

ITEMS_RAW = [
    ("R99ExecC1", "executor",
     "C1 freeze-file build. Create census/round-99/declared-shapes.py: a copy of census/round-98/declared-shapes.py whose "
     "SHAPES tuple is REMOVED and replaced by reading --freeze <tsv>. The tsv has header `name<TAB>kind<TAB>plain<TAB>comment` "
     "and one row per shape (17 rows, same names and kinds as census/round-98/declared-shapes.py). The runner must (a) refuse "
     "with rc 2 if --freeze is missing, (b) print the freeze file's sha256 on a line `FREEZE sha256=<hex>`, (c) print one "
     "`SHAPE <name> kind=<kind> plain=.. hooked=.. ok|MISMATCH` line per row and `SHAPES-SUMMARY shapes=N mismatched=M`, "
     "(d) print the three MISMATCH rows by name (not only a count). Create census/round-99/shapes.tsv from census/round-98/"
     "declared-shapes.py SHAPES verbatim (kinds as r98). Create census/round-99/c1-survivor-search.py as a byte copy of "
     "census/round-98/c1-survivor-search.py (the r98 hook is unchanged in this round). Run: `python3 -B census/round-99/"
     f"declared-shapes.py --freeze census/round-99/shapes.tsv --search census/round-99/c1-survivor-search.py --scripts "
     f"census/round-98/shapes --work {SCR}/R99ExecC1/shapes-work` and report the three lines' exit code and output. Then "
     "make a RELABELLED copy of shapes.tsv under your scratch dir (q1o kind=declared, q1q kind=declared, q1i kind=crash) and "
     "run the same command against it: report the mismatched count and its rows (this is the Q173 movability attack; the "
     "count must move). Also run the r97 hook (census/round-98/controls/c1-r97-search.py) against shapes.tsv and report "
     "`SHAPES-SUMMARY` and the mismatched rows. Scratch only under the seat scratch dir."),
    ("R99ExecC1b", "executor",
     "C1 do-nothing control. Using census/round-98/controls/c1-r95-search.py and census/round-98/controls/c1-r97-search.py "
     f"as hooks, run census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv --scripts census/round-98/shapes "
     f"--work {SCR}/R99ExecC1b/ctrl-<hook> (one fresh empty dir per hook: ctrl-r95, ctrl-r97; --work must be empty under the seat scratch). Report every "
     "`SHAPES-SUMMARY` line, the MISMATCH rows, and exit codes. Expected: the r95 hook shows mismatched>=3 (q1i among them); "
     "the r97 hook shows mismatched>=2 (q1o, q1q). If either control reaches mismatched=0 under the frozen file, report it as "
     "a FALSIFIED control with the observed line (do not edit anything)."),
    ("R99ExecC2", "executor",
     "C2 counter build. Create census/round-99/c2-setup-arms.py as a copy of census/round-98/c2-setup-arms.py with ONE change "
     "in _reap_owned: delete the branch `elif _is_descendant(pid, os.getpid()): pass` (the subreaper branch (c)). Replace it "
     "with: a pid is owned iff it equals the spawn pid (starttime verified) or is a ppid-chain descendant of the spawn pid. "
     "For the T1 escapee use the spawn-chain only: at spawn, record the spawn pid's own identity; the T1 escapee is a spawn-"
     "chain member if its ppid chain reaches the spawn pid, and otherwise it is NOT killed (report that as an open limit "
     "with the observed evidence of whether the escapee is reachable from the spawn pid after its parent exits; do not "
     "invent a rule). Keep argv as candidate selection only. Also update the survivors count to the same spawn-chain rule. "
     "Create census/round-99/c2-decoy-test.py as a copy of census/round-98/c2-decoy-test.py (unchanged logic). Run "
     "`python3 -B census/round-99/c2-decoy-test.py --counter census/round-99/c2-setup-arms.py --probe census/round-98/"
     "c2-forgery-probe.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work "
     f"{SCR}/R99ExecC2/decoy --arm-timeout 200 --plant-delay 2` and report every line, counter exit, DECOY-SUMMARY verdict. "
     "Then run the r97 counter (census/round-97/c2-setup-arms.py) with the same decoy test and report its verdict (must be "
     "killed). Report exact command lines and exit codes."),
    ("R99ExecC2b", "executor",
     "C2 cross-arm probe. Write census/round-99/c2-cross-arm-probe.py: plants a counter-descendant carrier (a process whose "
     "argv carries the T1 reap token, forked from ANOTHER arm's process tree, NOT a spawn-chain member of the T1 arm) and "
     "then runs census/round-99/c2-setup-arms.py with its T1 arm, then asserts the carrier is ALIVE after the counter exits "
     "(verdict spared). Run it against census/round-99/c2-setup-arms.py (expect spared) and against census/round-98/"
     "c2-setup-arms.py (expect killed; this is the do-nothing control). Report DECOY/CROSS-ARM lines and exit codes. Scratch "
     "under the seat scratch dir only."),
    ("R99ExecCensus", "executor",
     "No-harm: over the 278 generated mutants of census/round-98/c1-survivor-search.py run the population search with the "
     "r99 search (copy census/round-99/c1-survivor-search.py from census/round-98/c1-survivor-search.py byte-exact; no hook "
     "change). Run: `python3 -B census/round-99/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py "
     "--harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane "
     f"{LANE} --fleet-root /home/vgpnk/Projects/shokunin --work {SCR}/R99ExecCensus/search --jobs 5`. Report the SEARCH-SUMMARY "
     "line, its exit code, and the survivors-r99 count. Compare against census/round-98/records/search-r98.log. Survivor "
     "identity: `sort` both survivor lists and report the symmetric difference size (must be 0). Do not claim equality "
     "unless you measured it."),
    ("R99Reviewer1", "reviewer",
     "Correctness review of census/round-99/declared-shapes.py (once R99ExecC1 has written it; read the r98 runner as the "
     "baseline). Find any way the runner's mismatched count can reach 0 without the hook's behaviour being correct: a "
     "relabelled freeze row, a shape missing from the freeze file, a freeze-file row ordering change, a missing-file path. "
     "Each finding: a runnable reproducer under your wave dir and its observed SHAPES-SUMMARY line."),
    ("R99Reviewer2", "reviewer",
     "Review census/round-99/c2-setup-arms.py branch changes: read the diff against census/round-98/c2-setup-arms.py. Decide "
     "whether the spawn-chain rule can still signal a process that is not a spawn-chain member (for example via pid reuse "
     "between the _is_descendant walk and os.kill; check the starttime re-read). Each finding with a reproducer and its "
     "observed output. Name any sentence in the claim C2 wording you consider falsified by the code."),
    ("R99Critic", "critic",
     "Falsify both claim wordings against the r99 bytes. C1: is `shapes=17 mismatched=0` movable by relabelling the frozen "
     "file (run the relabel and report)? Is the frozen file hash binding meaningful? C2: does the wording 'spawn pid and its "
     "ppid-chain descendants only' match the code exactly? Is the counter-descendant case now spared (cross-arm probe) and "
     "does that falsify the r98 claim sentence? Output a verdict per sentence (holds / narrowed / falsified) with reproducer."),
    ("R99MutC1", "mutation-tester",
     "Mutation-test the r99 C1 runner (census/round-99/declared-shapes.py): one-edit mutants (drop the MISMATCH row print; read "
     "kinds from a hard-coded tuple; ignore the freeze file; invert the declared comparison; accept a missing shape). Run "
     "each against census/round-99/shapes.tsv and report which mutants the SHAPES-SUMMARY line fails to kill. Name every "
     "survivor and whether it is equivalent. Mutants under your scratch dir only."),
    ("R99MutC2", "mutation-tester",
     "Mutation-test the r99 C2 counter (census/round-99/c2-setup-arms.py): one-edit mutants (restore branch (c); drop the "
     "ppid walk; match argv only; drop the starttime check; kill the recorded pid without the descendant test). For each run "
     "census/round-99/c2-decoy-test.py and census/round-99/c2-cross-arm-probe.py. Report which mutants pass both predicates, "
     "with exit codes. Include the restore-branch-(c) mutant result explicitly."),
    ("R99Sentinel", "sentinel",
     "Safety review of the r99 reap: can any process that is not a spawn-chain member of the arm be signalled? Probe with a "
     "foreign own-uid process that (a) carries the T1 token in argv, (b) is reparented to init after its parent exits, (c) is "
     "a setsid grandchild of a different arm. State for each whether census/round-99/c2-setup-arms.py kills it, with the "
     "observed result. Report any signal sent to a non-owned pid as HIGH with a reproducer. Also check that no counter writes "
     "under /tmp regardless of TMPDIR."),
    ("R99Connector", "connector",
     "Cross-lane overlap scan and planning data-walk. Read-only grep under /home/vgpnk/Projects/shokunin/*-shokunin/tools and "
     "/home/vgpnk/Projects/shokunin/scripts for argv-identity kills (kill/killpg with argv matching) and report any sibling "
     "that shares the crash-sentinel or probe-timeout surface. Data-walk: from census/round-98/records/*.txt and the r98 "
     "wave seats' reports under .ufo/waves/round-98/w1/, count the surviving classes and say which the r99 claims target. "
     "Report with command output."),
    ("R99ScoutSources", "scout",
     "Re-open live the sources the claims cite: (1) https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html (S075: fields "
     "5/6/22; field 4 is S332's emission order) — locate the starttime (field 22) wording and quote ≤25 words with location; "
     "(2) https://man7.org/linux/man-pages/man2/setsid.2.html (S368) — locate the new process group sentence; (3) "
     "https://docs.python.org/3/library/sys.monitoring.html (S372) — RERAISE wording. Capture each under your scratch and "
     "report sha256 and whether each quote occurs exactly once. Do not append rows; report the verification only."),
    ("R99Scribe", "scribe",
     "Draft round-99 lesson blocks from committed evidence only: inputs plans/round-99.md, corpus/lessons/round-98.md "
     "## Mistakes, corpus/lessons/round-98-verifier-spotcheck.md §routed defects 1–4. Draft into your wave dir only: (a) a "
     "`## Gate` block listing the two frozen predicates in one sentence each; (b) one `## Mistakes` row per mistake you can "
     "evidence from the wave's outputs, in the form class · evidence pointer · captured-by · fix; if none, paste the sweep "
     "command and its output that found none."),
]


def seat(name, role, target):
    body = (f"# Target\n{target}\n\n# Acceptance\nReport at {W}/{name}.md with the commands, exit codes and observed summary "
            f"lines. OWN ONLY {W}/{name}/ and {W}/{name}.md; scratch {SCR}/{name}/. Delete your scratch dir before you yield.\n\n")
    return {"name": name, "role": role,
            "prompt": GOD + body + f"Report: .ufo/waves/round-{ROUND}/{WAVE}/{name}.md\n"}


def main():
    items = [seat(n, r, t) for n, r, t in ITEMS_RAW]
    spec = {
        "wave": f"souji-r{ROUND}-{WAVE}",
        "milestone": "souji r99: shape labels frozen in a file the runner reads (calibration, M6/Q173) and reap restricted to spawn pid + ppid chain with a cross-arm probe (operability, S075/S368)",
        "reportDir": f".ufo/waves/round-{ROUND}/{WAVE}",
        "maxLanes": 16,
        "context": CONTEXT,
        "items": items,
    }
    print(json.dumps(spec, indent=1))


if __name__ == "__main__":
    main()
