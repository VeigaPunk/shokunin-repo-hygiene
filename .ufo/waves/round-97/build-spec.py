#!/usr/bin/env python3
"""Build the souji r97 wave-1 spec. Run: python3 .ufo/waves/round-97/build-spec.py <P2> <F> > .ufo/waves/round-97/w1-spec.json
Shape and prose follow .ufo/waves/round-95/build-spec.py.
"""
import json, sys
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "210084b24de1dd1f1fd499f49b0c70744f099f5f"
P1 = "053287d4eea5dc6c0e1aff9c2295cff0f0a2a3d9"
P2, F = sys.argv[1], sys.argv[2]
W = f"{LANE}/.ufo/waves/round-97/w1"
SCR = "/fast/scratch/hyaku/souji-r97"
GOD = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

"""
C1_ARGS = ("--counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py "
           f"--population census/round-93/c1-false-rows.tsv --lane . --fleet-root {FLEET}")
C1_AFTER = (f"python3 -B census/round-97/c1-survivor-search.py {C1_ARGS} --work <empty> --jobs 5 "
            "--ids census/round-97/c1-targets.json")
C1_CTL = C1_AFTER.replace("census/round-97/c1-survivor-search.py", "census/round-97/c1-control-r95-rule.py")
C1_FORG = (f"python3 -B census/round-97/c1-forgery-controls.py --search census/round-97/c1-survivor-search.py {C1_ARGS} "
           "--ids census/round-97/c1-targets.json --jobs 5 --shapes census/round-97/declared-shapes.py "
           "--scripts census/round-97/shapes --work <empty>")
C1_SHAPES = "python3 -B census/round-97/declared-shapes.py --search census/round-97/c1-survivor-search.py --scripts census/round-97/shapes --work <empty>"
C2_ARGS = ("--fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py "
           "--tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>")
C2_AFTER = f"python3 -B census/round-97/c2-setup-arms.py --probe census/round-97/c2-forgery-probe.py {C2_ARGS}"
C2_CTL = f"python3 -B census/round-97/c2-setup-arms.py --probe census/round-95/c2-forgery-probe.py {C2_ARGS}"
C2_FORG = f"python3 -B census/round-97/c2-forgery-controls.py --probe census/round-97/c2-forgery-probe.py {C2_ARGS}"
CTX = f"""# Goal
souji round 97 (lane repo {LANE}, lane id souji). The L1 (SoujiR97) holds the planner seat and is the ONLY
integration owner: it froze the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 13 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion. All commands below run
with cwd {LANE} (use `cd {LANE} && ...`); every path is relative to {LANE} unless absolute.

# Frozen round (read {LANE}/census/round-97/preregistration.txt FIRST — it is the contract)
Lane base {BASE} (r96 closed admitted; its non-author spot-check is corpus/lessons/round-96-verifier-spotcheck.md,
routed items in §7). P1 {P1}: instruments (census/round-97/*.py, c1-targets.json, srcs/, the S372 row in
corpus/SOURCES.md, corpus/knowledge/crash-channels-beyond-excepthook.md, corpus/knowledge/deadline-owned-reaping.md). P2 {P2}: controls (census/round-97/controls/,
including prefreeze-feasibility-note.txt, which discloses that the L1 trial-ran both after arms in scratch before F).
F {F}: the preregistration alone. After receipts will land in census/round-97/records/. The filed instruments are
FROZEN: do not modify census/, tests/fixtures/, tools/ or corpus/ — copy what you need into your seat dir or scratch
and write receipts in your seat dir. Nothing in the claim wording may be widened by this wave; the wave's job is to
FALSIFY it (Amendment 59: a claim verifies only if no artifact produced by this round's own wave falsifies its
STATED WORDING; numbers re-deriving is necessary, not sufficient).

Claims (read the prereg for the full predicate, controls and stated limits):
- C1 calibration 7: the r96 search's SystemExit leg clears a foreign SystemExit on ANY module-level
  EXCEPTION_HANDLED (t1/t4 70→0 vs module `finally`/re-raise 70→1 wrong). The r97 search census/round-97/c1-survivor-search.py
  (a RERAISE-aware pending-clear latch, S372, so a finally-unwind or explicit re-raise cancels the clear; the
  excepthook/thread channels write before the traceback print (A2); the no-free-tool-id fallback restores fd 2
  blocking mode (A3)) keeps t1/t4 declared and x1/x2 errored on the 14-shape table, prints `SHAPES-SUMMARY shapes=14 mismatched=0`. Predicate: `{C1_AFTER}` prints the check line
  `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`
  and `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1`, EXIT 0;
  `{C1_SHAPES}` prints `SHAPES-SUMMARY shapes=14 mismatched=0`, EXIT 0. Control (the frozen r96 search on the same
  fourteen scripts) prints mismatched=2 (x1/x2 at 1, wrongly declared; the A1 trade); the r95 hook prints
  mismatched=2 (t1/t4 at 70). Forgeries `{C1_FORG}`: FA/FB/FC/FD/FE refused 5/5 (FD and FE leave the target summary
  unchanged and are refused by mismatched=2 on the table). One harness run clones the lane (~0.7 GB) and takes
  ~20 s; use --jobs 5 at most.
- C2 operability 8: the r96 probe refuses T1 (exit 2), but its counter leaves the escaped setsid grandchild alive
  (measured: 1 and 2 survivors after counter-style killpg) — the group kill cannot reach a new session (S368/A4);
  an unbounded-output fixture drives the r96 probe to 27.3 GB RSS and SIGTERM before the timeout (A5); a signal exit
  (-15) is printed with no distinct mark (A8). The r97 probe census/round-97/c2-forgery-probe.py caps captured output
  (--max-output, 8 MiB; over-cap is a setup failure), and the r97 counter reaps the T1 grandchild by argv identity
  (its absolute fixture path) and prints `survivors=<n>`. Predicate: `{C2_AFTER}` prints `ARM T1 exit=2 ... survivors=0`
  and `ARMS-SUMMARY arms=20 conform=20` EXIT 0 (~5 min at --jobs 4). Control `{C2_CTL}` (r95 probe): T1 hung,
  conform=19 EXIT 1; and the r96 probe: conform=20 with survivors=1. Forgeries `{C2_FORG}`: GA/GB/GC/GD refused 4/4
  (GD claims setup refusal without reaping; survivors>0 by identity).

# Evidence durability and the pre-file ledger (Amendment 59)
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every argument, output line and falsifying reproducer you want the ledger to read must live under {W}/ (your seat
dir {W}/<your name>/ or your report). If an artifact of yours falsifies a sentence of either claim, say so plainly
in the report under a heading `FALSIFIES-WORDING` (or `FALSIFIES-NUMBER`) with the exact sentence and the
reproducer path; the L1 records it as an amendment in plans/round-97.md, never silently. If nothing falsifies, say
`NO-FALSIFICATION` with what you tried. Every `Report:` trailer path is relative to {LANE} — write it at
{LANE}/<that path>. NEVER write anything under {FLEET}/.ufo/ or anywhere else in the fleet root; use absolute paths
under {W}/ for every file you write.

# Write scope and scratch
Write only under your own seat dir {W}/<your name>/ and your own report file. Read the lane read-only. Scratch
(clones, fixtures, search/arms --work dirs) lives under {SCR}/<your name>/; create it with mkdir -p and DELETE it
before you yield (trap 'rm -rf -- "$S"' EXIT in shell, finally: shutil.rmtree in Python), copying receipts (text
only, never clones) into your seat dir first. Keep your scratch under 20 GB: never hold more than 5 harness work trees
at once. /tmp and /var/tmp are for files under 50 MB only, are never citable evidence, and every temp dir you make
(TMPDIR, mkdtemp, hook dirs) goes under {SCR}/<your name>/. Any git fixture is `D=$(mktemp -d -p {SCR}/<your name>)`
+ `git -C "$D" init -q`, every later call names `-C "$D"`, and you assert `git -C "$D" rev-parse --show-toplevel`
equals `$D` before the first commit; never pass an empty or unchecked variable to `git -C` (it falls back to the
fleet root, r70 incident). Do not run mutating git/jj anywhere else. Never mutate host sysctls, never sudo, never
spin CPU burners, never leave background processes running. After a timed-out fixture run, kill any reaped
grandchildren you started.

# Tooling authorization (operator, 2026-10-19)
You may install or upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels,
update-safety gate; record tool/version/channel/reason in your report). pacman transactions are PAUSED host-wide
until the operator resolves the host-recovery L0 question: install via `uv tool`/`npx`/an official binary in
~/.local/bin, or file an L0 question; before any future pacman -S run `pacman -Sp --print-format '%n %v' <pkgs>` and
never -Sy/-Syu/-U/-R. No tool install is needed for this round.

# Round shape
One v1 wave, 13 seats (policy band 8-16): 3 executor, 3 reviewer, 1 critic, 2 mutation-tester, 1 sentinel,
1 connector, 1 scout, 1 scribe. Attack seats (reviewer, critic, mutation-tester): 6/13 = 46 %. The L1 holds the
canonical planner seat (the validator rejects `planner`); the bounded planning data-walk rides the connector seat.
Residual calls: none. The L1 holds the canonical planner seat (the validator rejects `planner`); the bounded planning data-walk rides the connector seat.
"""
def seat(name, role, target, change, accept):
    body = f"# Target\n{target}\n\n# Change\n{change}\n\n# Acceptance\n{accept}\n\n"
    body = body.replace("{BASE}", BASE).replace("{FLEET}", FLEET).replace("{LANE}", LANE)
    return {"name": name, "role": role,
            "prompt": GOD + body + f"Report: .ufo/waves/round-97/w1/{name}.md\n"}
def own(name):
    return f"OWN ONLY {W}/{name}/ and {W}/{name}.md; scratch {SCR}/{name}/."
ITEMS = [
    seat("R97ExecC1", "executor",
         "Re-derive C1's predicates (search + shape table), do-nothing control and forgery controls on committed bytes, independently of the L1. " + own("R97ExecC1"),
         f"1. Run `{C1_AFTER}`, `{C1_SHAPES}`, `{C1_CTL}` and `{C1_FORG}` (each with its own empty --work under your scratch; run them one after another, never as background jobs in one shell call). Save full receipts in your seat dir; quote the check line, every SEARCH/SHAPE line, every SUMMARY line and each exit code.\n"
         "2. Pins: sha256 of census/round-97/c1-survivor-search.py, c1-targets.json, c1-control-r95-rule.py, c1-forgery-controls.py, declared-shapes.py, every census/round-97/shapes/*.py, the r93 harness, the r93 population and the r87 counter vs the prereg and the P2 receipts.\n"
         "3. `diff census/round-96/c1-survivor-search.py census/round-97/c1-survivor-search.py` and classify EVERY hunk (docstring, HOOK, CHECK, CHECKS, HAND, rule, precondition, UNEXPECTED).\n"
         "4. For each of the ten targets, open its harness.out (keep the search's --work until you have read it): count ROW lines by rc value and match; find the `SOUJI-R97-CRASH` stderr evidence the harness keeps; confirm the two semantic kills have no rc=70 or negative rc row.\n"
         "5. Does the r95 control wrapper run the frozen r95 HOOK/verdict()/score()/main() unchanged?",
         "All receipts, the pin table, the hunk inventory, the per-target row table, the shape-table re-derivation. Any mismatch to the prereg is HIGH (FALSIFIES-NUMBER).",
         ),
    seat("R97ExecC2", "executor",
         "Re-derive C2's after arm, do-nothing control and forgery controls on committed bytes. " + own("R97ExecC2"),
         f"1. Run `{C2_AFTER}`, `{C2_CTL}` and `{C2_FORG}` sequentially (each its own empty --work). Save full receipts (and every ARM's .out file) in your seat dir; quote every ARM line and summary and each exit code.\n"
         "2. Pins: sha256 of census/round-97/c2-forgery-probe.py, c2-setup-arms.py, c2-forgery-controls.py, both fixtures, the tool and the before tool vs the prereg/P2 receipts.\n"
         "3. `diff census/round-96/c2-forgery-probe.py census/round-97/c2-forgery-probe.py`: classify EVERY hunk; confirm the eight FORGERIES tuples and the verdict computation are byte-identical to r96.\n"
         "4. Run the r97 probe directly (not via the arms counter) on P1's inputs and confirm `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass` EXIT 0 with the same FORGERY lines as census/round-95/records/ (sha256 aside); also on the r92 fixture (rejected=5, exit 1).",
         "All receipts, the pin table, the hunk inventory and the direct-run comparison. Any mismatch is HIGH.",
         ),
    seat("R97ExecCensus", "executor",
         "Reported, not claimed (the C1 no-harm check): does the r97 sentinel/rule change any verdict of a generated mutant that is not a crash? " + own("R97ExecCensus"),
         "Score EVERY generated mutant of the frozen r87 counter on the r93 population twice: (a) with the r97 search (no --ids; --jobs 5; --emit <seat dir>/survivors-r97.json) and (b) with the frozen r96 search census/round-96/c1-survivor-search.py (no --ids; --jobs 5; --emit <seat dir>/survivors-r96.json). Same harness/population/counter args as the C1 predicate. Each run is ~280 harness runs (~20 min at 5 jobs); run (a) then (b), never concurrently, and keep only the harness.out files you cite (copy the SEARCH lines, not the trees). Then list every id whose verdict differs between (a) and (b), with its harness.out rc values and any SOUJI-R97-CRASH reason. A differing id that is NOT a crash (no rc=70/negative row, no crash reason) falsifies the population census you expect (killed 139, survived 76; errored 53 vs 48 = the five new fixtures). Say FALSIFIES-WORDING if a non-crash id differs. Also compare the survivor sets; also run `{C1_SHAPES}` on the r96 search and quote its mismatched=2.",
         "Both SEARCH-SUMMARY lines, the difference table with reasons, the survivor-set diff, the r96-host shape table, and your verdict.",
         ),
    seat("R97ReviewerC1", "reviewer",
         "Correctness review of the r97 crash sentinel, the EXCEPTION_HANDLED clear, the signal-safe crash write and the kill rule against the C1 wording. " + own("R97ReviewerC1"),
         "Read census/round-97/c1-survivor-search.py (HOOK, CHECK, CHECKS, verdict, precondition), census/round-93/c1-false-row-harness.py (how it starts the counter; every ROW-printing branch) and the prereg C1. Check: (1) the top-level-handled clear: does it fire on a SystemExit caught at the top level but NOT on one caught inside main, one that passes through a finally, or one that terminates? Build scratch scripts for each and record rc with the frozen hook. (2) The signal-safe write: can the crash path deadlock when called from a signal handler or a thread, or hang on a full undrained pipe? Reproduce E3c/E16/E18 in scratch and record rc. (3) Can a non-crash mutant reach errored (e.g. a mutant whose counter legitimately exits 70, or a git child killed by a signal)? (4) Does the CHECK's reason assertion reject the cross-wired legs m02/m03 (a mutant that points threading.excepthook or os._exit at the excepthook function)? (5) Does the claim sentence say anything the predicate does not check?",
         "Per-question verdict with line numbers and receipts; FALSIFIES-WORDING/NUMBER or NO-FALSIFICATION.",
         ),
    seat("R97ReviewerC2", "reviewer",
         "Correctness review of the r97 probe's pipe-EOF-free timeout and the twenty-arm counter against the C2 wording. " + own("R97ReviewerC2"),
         "Read census/round-97/c2-forgery-probe.py, census/round-97/c2-setup-arms.py and the prereg C2. Check: (1) can the r97 probe still hang or exit 1 on any setup failure: a fixture that writes unbounded output, a fixture whose setsid grandchild is a daemon that reopens pipes, a --work symlink loop, a fixture that prints a SUMMARY then hangs? (2) Does each T arm (T1-T4) test what its label says? Run each directly against the probe and record exit codes. (3) Is the reaped grandchild reaped or left running after T1? (4) Does S13's /tmp refusal still bind the probe's own /tmp guard (mutant: remove the guard and see if S13 still conforms — A5)? (5) Any sentence wider than the predicate (e.g. 'refuses', 'keeps', 'stops waiting')?",
         "Per-question verdict with receipts; FALSIFIES-WORDING/NUMBER or NO-FALSIFICATION.",
         ),
    seat("R97ReviewerShapes", "reviewer",
         "Conformance of the Q172 declared-shape table against the r97 staged wording. " + own("R97ReviewerShapes"),
         "Re-run `{C1_SHAPES}` and the same table with the frozen r96 search (mismatched=2 expected) and the r94-rule control (mismatched=6). Count: how many of the twelve scripts exist under census/round-97/shapes/ vs the twelve scripts named in census/round-97/declared-shapes.py's SHAPES tuple; are the script hashes the R95Labrat ones (recompute against .ufo/waves/round-95/w1/R95Labrat/receipts/)? Read the prereg's C1 stated limits (i)-(iv) and the search docstring's r97 items: does each limit name something the table or the ten targets actually show? Does any sentence in the prereg claim a shape the table does not contain (e.g. a caught SystemExit at a non-module frame, an os._exit(0) call, a twin tool-id collision)?",
         "The two control receipts, the script census (present/named/hash), per-limit verdicts; FALSIFIES-WORDING/NUMBER or NO-FALSIFICATION.",
         ),
    seat("R97Critic", "critic",
         "Falsify both claims' wording, axis fit, separability and do-nothing controls. " + own("R97Critic"),
         "1. C1 is named calibration: does it count a mismatch between the lane's self-assessment (the search's verdict) and observed state (the counter's exit was a caught SystemExit)? Build one cheap alternative rule that is NOT the sentinel (e.g. 'no ITEM line printed' or 'stderr non-empty') and see whether it meets the C1 predicate (summary + shape table).\n2. C2 is named operability: build the cheapest probe edit that reaches 20/20 without real pipe discipline (special-casing T1's fixture basename, catching everything as exit 2) and say what that implies for the counted quantity.\n3. Separability: can C1 be verified with C2 not landed and vice versa?\n4. Any universal word ('all', 'every', 'never', 'any') in the prereg the counters do not enumerate?",
         "Per-item verdict with reproducers; FALSIFIES-WORDING/NUMBER or NO-FALSIFICATION per claim.",
         ),
    seat("R97MutC1", "mutation-tester",
         "Mutation-test the r97 search's sentinel, the top-level-handled clear, the CHECK reasons and the rule: which one-edit mutants of census/round-97/c1-survivor-search.py does the C1 predicate fail to catch? " + own("R97MutC1"),
         "Write at least 12 one-edit mutants of the r97 search (scratch copies), at least one per leg: dropping the EXCEPTION_HANDLED registration, flipping the `<module>` test, widening the clear to any frame, dropping one CHECK reason string, mis-pointing one CRASH reason, the os.set_blocking line, the RAISE callback (first-frame record, main-file test), the atexit registration, the tool-id loop, the negative-rc disjunct (row and harness), the CHECKS table (want codes), the precondition loop. Run each through the C1 predicate (the search command and the shape-table command; substitute your mutant for the search; --jobs 5). A mutant SURVIVES if it still prints the exact predicate summary, per-id verdicts, the exact check line and mismatched=0 with EXIT 0 both. Classify survivors equivalent / unbound and say which target, check or shape would bind each.",
         "Mutant table (edit, summary, shapes, killed/survived, classification); survivors are findings.",
         ),
    seat("R97MutC2", "mutation-tester",
         "Mutation-test the r97 probe's pipe-EOF-free timeout and the twenty-arm counter: which one-edit mutants does the C2 predicate fail to catch? " + own("R97MutC2"),
         "Write at least 8 one-edit mutants of census/round-97/c2-forgery-probe.py (_wait_output's wait(): p.wait() instead of the returncode wait; dropping the killpg; the Fatal raise; the cli() handlers; the --timeout <= 0 check) and at least 3 of census/round-97/c2-setup-arms.py (T1-T4 want codes or inputs, the arm timeout, the stream choice, the T1 fixture shape). Score probe mutants with the C2 predicate command (substitute the probe; expect ~5 min per full run, use --jobs 4); score arms-counter mutants on the r97 probe AND on the r96 probe (a counter mutant that gives the r96 probe 20/20 is a broken counter). Report each with its summary.",
         "Mutant tables; survivors are findings with classification.",
         ),
    seat("R97Sentinel", "sentinel",
         "Safety and robustness of the signal-safe crash write, the /tmp guard and the probe's timeout reap. " + own("R97Sentinel"),
         "1. The r97 crash write sets fd 2 non-blocking and never restores it: can that change the behaviour of a process that continues after the crash write (e.g. an unraisablehook handler that returns)? Show the outcome in scratch.\n2. The probe's --work /tmp guard is string-prefix only: does a symlink under --work resolve to /tmp and pass it? Show whether the guard follows symlinks (os.path.realpath) for --work and for fixtures/inputs.\n3. Do the C1/C2 instruments write under /tmp regardless of TMPDIR/--work (T2's chmod 0555 included; S13's /tmp path)?\n4. A descriptor leak check: after a timed-out fixture run, is the pipe-holder grandchild reaped?",
         "Findings HIGH/MEDIUM/LOW with reproducers, or 'no finding' per item with what was tried.",
         ),
    seat("R97Connector", "connector",
         "Cross-lane overlap scan plus the planning data-walk the L1's planner seat delegates. " + own("R97Connector"),
         "1. Sibling overlap: grep the sibling lane repos under {FLEET}/*-shokunin/ (read-only) for a sys.monitoring EXCEPTION_HANDLED callback, an os.write crash marker, or a probe fixture timeout that stops on pipe EOF; say whether any sibling owns this surface, with paths.\n2. Lane pattern: list other lane instruments under census/round-8*/ and census/round-9*/ that run fixtures with no timeout or read inputs with open(..., encoding='utf-8') without a setup refusal (same class as C2), with paths.\n3. Planning data-walk: read corpus/lessons/round-96-verifier-spotcheck.md §7 routed items and SCORECARD.md `### Planned (r97)`; mark each answered / partly / carried with the r97 file that answers it; draft the `### Planned (r98)` bullet list.\n4. SOURCES rule 2: `git -C {LANE} diff {BASE} -- corpus/SOURCES.md` must show only added rows (S365-S367), no edited cell.",
         "Overlap verdict with paths, the pattern list, the routed-item table and r97 draft, and the rule-2 check.",
         ),
    seat("R97ScoutSources", "scout",
         "Re-open the round's three new sources live and find one rejectable candidate. " + own("R97ScoutSources"),
         "1. Fetch the URL of the new S372 row (corpus/SOURCES.md) now; compare sha256 and size with the rows (the pages may differ: then diff the tag-stripped text). Confirm each row's quoted sentence occurs, its word count, its occurrence count in whitespace-normalized tag-stripped text, and that the row's locator names the right section.\n2. Do the rows claim more than the quotes say (e.g. S365 for the top-level-handled clear, S366 for the signal-safety, S367 for pipe-EOF semantics)? Check against the row's own 'teaches' cell.\n3. Find ONE more candidate source on reaping a timed-out fixture's grandchildren or on non-blocking writes (e.g. os.get_blocking, select.poll, setsid(2)) and judge it against corpus/QUALITY.md and PROVINCE.md: admit or reject with reason and flip condition; give URL, access date and a <=25-word located quote. Do not edit corpus/. Fetch with curl into your scratch dir only.",
         "Per-row verify table (hash/size/quote/count/locator) and one candidate verdict with quote.",
         ),
    seat("R97Scribe", "scribe",
         "Draft the round lesson blocks from committed evidence. " + own("R97Scribe"),
         "Read census/round-97/ (prereg, controls), corpus/lessons/round-96.md (format) and corpus/lessons/round-96-verifier-spotcheck.md. 1. Draft `## Mistakes` rows (class · evidence pointer · captured-by · fix; a fix counts only once shown able to fail): at least the r96 EH clear turning a terminating module-level finally/re-raise into a declared exit (x1/x2 70→1 wrong, A1) and the r96 counter leaving the T1 grandchild alive (1/2 survivors after killpg), each pointing at the r97 control receipt that shows the fix able to fail.\n2. Draft one corpus/QUALITY.md criterion (next free Q number after the last in corpus/QUALITY.md) that would have caught both: a crash sentinel that distinguishes terminating from handled exits names the events it registers and carries a table of exit shapes, with a counting command.\n3. Draft the `## Gate` block for S365-S367 (URL, access date 2026-11-09, quote, locator) leaving the reject slot for the scout.",
         "Draft text blocks in your report, each line carrying its evidence path.",
         ),
]
def main():
    print(json.dumps({"wave": "souji-r97-w1",
                      "milestone": "souji r97: the SystemExit leg's EH clear is RERAISE-aware so terminating module finally/re-raise stay errored (calibration, S372); the forgery probe caps output and the counter reaps the T1 grandchild by identity (operability, S368)",
                      "reportDir": ".ufo/waves/round-97/w1",
                      "context": CTX,
                      "items": ITEMS}, indent=1))
if __name__ == "__main__":
    main()
