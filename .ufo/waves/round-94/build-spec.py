#!/usr/bin/env python3
"""Build the souji r94 wave-1 spec. Run: python3 .ufo/waves/round-94/build-spec.py > .ufo/waves/round-94/w1-spec.json
Shape and prose follow .ufo/waves/round-93/build-spec.py."""
import json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536"
P1 = "24cd67b0eff2cf3ec98cbfe74e3f4ef3fdaab88a"
P2 = "39d4163a66c350f219287530a5aed6ac9d5e7224"
F = "4ad74b9df466eff28bdf3785c33f6c5fc50bf966"
W = f"{LANE}/.ufo/waves/round-94/w1"
SCR = "/fast/scratch/hyaku/souji-r94"

GOD = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

"""

C1_AFTER = ("python3 -B census/round-94/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py "
            "--harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv "
            f"--lane . --fleet-root {FLEET} --work <empty> --jobs 5 --ids census/round-94/c1-targets.json")
C1_CTL = C1_AFTER.replace("census/round-94/c1-survivor-search.py", "census/round-94/c1-control-r93-rule.py")
C1_FORG = ("python3 -B census/round-94/c1-forgery-controls.py --search census/round-94/c1-survivor-search.py "
           "--counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py "
           f"--population census/round-93/c1-false-rows.tsv --lane . --fleet-root {FLEET} "
           "--ids census/round-94/c1-targets.json --work <empty>")
C2_ARGS = ("--fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py "
           "--tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>")
C2_AFTER = f"python3 -B census/round-94/c2-setup-arms.py --probe census/round-94/c2-forgery-probe.py {C2_ARGS}"
C2_CTL = f"python3 -B census/round-94/c2-setup-arms.py --probe census/round-93/c2-forgery-probe.py {C2_ARGS}"
C2_FORG = f"python3 -B census/round-94/c2-forgery-controls.py --probe census/round-94/c2-forgery-probe.py {C2_ARGS}"

CTX = f"""# Goal
souji round 94 (lane repo {LANE}, lane id souji). The L1 (SoujiR94) holds the planner seat and is the ONLY
integration owner: it froze the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 12 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion. All commands below run
with cwd {LANE} (use `cd {LANE} && ...`); every path is relative to {LANE} unless absolute.

# Frozen round (read {LANE}/census/round-94/preregistration.txt FIRST — it is the contract)
Lane base {BASE} (r93 closed; its non-author spot-check is corpus/lessons/round-93-verifier-spotcheck.md, routed
defects in §5). P1 {P1}: instruments (census/round-94/*.py, c1-targets.json, srcs/, the S357/S358 rows in
corpus/SOURCES.md, corpus/knowledge/mutant-crash-is-not-a-kill.md). P2 {P2}: controls (census/round-94/controls/,
including prefreeze-feasibility-note.txt). F {F}: the preregistration alone. After receipts will land in
census/round-94/records/. The filed instruments are FROZEN: do not modify census/, tests/fixtures/, tools/ or corpus/
— copy what you need into your seat dir or scratch and write receipts in your seat dir. Nothing in the claim wording
may be widened by this wave; the wave's job is to FALSIFY it (Amendment 59: a claim verifies only if no artifact
produced by this round's own wave falsifies its STATED WORDING; numbers re-deriving is necessary, not sufficient).

Claims (read the prereg for the full predicate, controls and stated limits):
- C1 calibration 7: the r93 survivor search's kill rule scores a mutant whose counter raises an uncaught exception
  as killed (a Python crash exits 1, the counter's own "not all resolved" code). The r94 search adds a crash
  sentinel — a `sitecustomize.py` on PYTHONPATH under --work/hook whose sys.excepthook exits 70 (sysexits
  EX_SOFTWARE, S358), inherited by the harness and the counter it spawns — and the r94 rule (harness exit 70 or any
  ROW `rc=70` -> errored, after Stryker's Runtime error state, S357). Targets census/round-94/c1-targets.json: two
  crash fixtures (h-crash-late, h-crash-index), two semantic kills (h-ok-admits-one, a491c22-<-to-<=), one survivor
  (a127c26-True-to-False). Predicate: `{C1_AFTER}` prints `SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0
  hung=0 scored=5 errored=2 killed=2 survived=1` (crash fixtures `killed=errored`, the two kills `killed=yes`, the
  survivor `killed=no`) EXIT 0. Do-nothing control `{C1_CTL}` (the r93 rule): errored=0 killed=4 survived=1.
  Forgeries `{C1_FORG}`: FA/FB refused=2. One harness run clones the lane (~0.7 GB) and takes ~17 s; use --jobs 5
  at most.
- C2 operability 8: the r93 forgery probe exits 1 (its "a forgery survived" code) on 7 of the 8 setup arms of
  census/round-94/c2-setup-arms.py, so a setup failure reads as a surviving forgery. The r94 probe runs on an
  existing empty --work and refuses the other setup arms with exit 2 + a `C2-FORGERY-FATAL:` line, keeping its
  verdict arms (P1 exit 0 rejected=8; P2 exit 1 rejected=5). Predicate: `{C2_AFTER}` prints `ARMS-SUMMARY arms=10
  conform=10` EXIT 0. Control `{C2_CTL}`: conform=3 EXIT 1. Forgeries `{C2_FORG}`: GA/GB refused=2. One arms run
  takes ~50-90 s.

# Evidence durability and the pre-file ledger (Amendment 59)
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every argument, output line and falsifying reproducer you want the ledger to read must live under {W}/ (your seat
dir {W}/<your name>/ or your report). If an artifact of yours falsifies a sentence of either claim, say so plainly
in the report under a heading `FALSIFIES-WORDING` (or `FALSIFIES-NUMBER`) with the exact sentence and the
reproducer path; the L1 records it as an amendment in plans/round-94.md, never silently. If nothing falsifies, say
`NO-FALSIFICATION` with what you tried. Every `Report:` trailer path is relative to {LANE} — write it at
{LANE}/<that path>. NEVER write anything under {FLEET}/.ufo/ or anywhere else in the fleet root (r92 lesson M5: a seat
report landed in the fleet root); use absolute paths under {W}/ for every file you write.

# Write scope and scratch
Write only under your own seat dir {W}/<your name>/ and your own report file. Read the lane read-only. Scratch
(clones, fixtures, search/arms --work dirs) lives under {SCR}/<your name>/; create it with mkdir -p and DELETE it
before you yield (trap 'rm -rf -- \"$S\"' EXIT in shell, finally: shutil.rmtree in Python), copying receipts (text
only, never clones) into your seat dir first. Keep your scratch under 20 GB: never hold more than 5 harness work trees
at once. /tmp is for files under 50 MB only and is never citable evidence. Any git fixture is `D=$(mktemp -d -p
{SCR}/<your name>)` + `git -C \"$D\" init -q`, every later call names `-C \"$D\"`, and you assert `git -C \"$D\"
rev-parse --show-toplevel` equals `$D` before the first commit; never pass an empty or unchecked variable to `git -C`
(it falls back to the fleet root, r70 incident). Do not run mutating git/jj anywhere else. Never mutate host sysctls,
never sudo, never spin CPU burners, never leave background processes running.

# Tooling authorization (operator, 2026-10-19)
You may install or upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels,
update-safety gate; record tool/version/channel/reason in your report). pacman transactions are PAUSED host-wide
until the operator resolves the host-recovery L0 question: install via `uv tool`/`npx`/an official binary in
~/.local/bin, or file an L0 question; before any future pacman -S run `pacman -Sp --print-format '%n %v' <pkgs>` and
never -Sy/-Syu/-U/-R. No tool install is needed for this round.

# Round shape
One v1 wave, 12 seats (policy band 8-16): 3 executor, 2 reviewer, 1 critic, 2 mutation-tester, 1 sentinel,
1 connector, 1 scout, 1 scribe. Attack seats (reviewer, critic, mutation-tester, labrat): 5/12 = 42 %. Residual
calls: none. The L1 holds the canonical planner seat (the validator rejects `planner`); the bounded planning
data-walk rides the connector seat.
"""


def seat(name, role, target, change, accept):
    body = f"# Target\n{target}\n\n# Change\n{change}\n\n# Acceptance\n{accept}\n\n"
    body = body.replace("{BASE}", BASE).replace("{FLEET}", FLEET).replace("{LANE}", LANE)
    return {"name": name, "role": role,
            "prompt": GOD + body + f"Report: .ufo/waves/round-94/w1/{name}.md\n"}


def own(name):
    return f"OWN ONLY {W}/{name}/ and {W}/{name}.md; scratch {SCR}/{name}/."


ITEMS = [
    seat("R94ExecC1", "executor",
         "Re-derive C1's after arm, do-nothing control and forgery controls on committed bytes, independently of "
         "the L1. " + own("R94ExecC1"),
         f"1. Run `{C1_AFTER}`, `{C1_CTL}` and `{C1_FORG}` (each with its own empty --work under your scratch; run "
         "them one after another, never as background jobs in one shell call). Save full receipts in your seat dir; "
         "quote every SEARCH and SUMMARY line and each exit code.\n"
         "2. Pins: sha256 of census/round-94/c1-survivor-search.py, c1-targets.json, c1-control-r93-rule.py, "
         "c1-forgery-controls.py, the r93 harness, the r93 population and the r87 counter vs the prereg and the P2 "
         "receipts.\n"
         "3. `diff census/round-93/c1-survivor-search.py census/round-94/c1-survivor-search.py` and classify EVERY "
         "hunk (docstring, sentinel, rule, hand edits, UNEXPECTED).\n"
         "4. For each of the five targets, open its harness.out (keep the search's --work; it holds m000N/harness.out "
         "until you delete it): count ROW lines with rc=70 and match=no; confirm the two semantic kills have zero "
         "rc=70 rows and are killed by a semantic row (got= not '-').\n"
         "5. Does the r93 control wrapper run the frozen r93 verdict()/score() unchanged (read it)? Is its HAND "
         "extension byte-identical to the r94 tuples?",
         "All receipts, the pin table, the hunk inventory, the per-target row table. Any mismatch to the prereg is "
         "HIGH (FALSIFIES-NUMBER).",
         ),
    seat("R94ExecC2", "executor",
         "Re-derive C2's after arm, do-nothing control and forgery controls on committed bytes. " + own("R94ExecC2"),
         f"1. Run `{C2_AFTER}`, `{C2_CTL}` and `{C2_FORG}` sequentially (each its own empty --work). Save full receipts "
         "(and every ARM's .out file) in your seat dir; quote every ARM line and summary and each exit code.\n"
         "2. Pins: sha256 of census/round-94/c2-forgery-probe.py, c2-setup-arms.py, c2-forgery-controls.py, both "
         "fixtures, the tool and the before tool vs the prereg/P2 receipts.\n"
         "3. `diff census/round-93/c2-forgery-probe.py census/round-94/c2-forgery-probe.py`: classify EVERY hunk; "
         "confirm the eight FORGERIES tuples and the verdict line are byte-identical to r93.\n"
         "4. Run the r94 probe directly (not via the arms counter) on P1's inputs and confirm `FORGERY-SUMMARY "
         "forgeries=8 rejected=8 positive=pass` EXIT 0 and the same FORGERY lines as "
         "census/round-93/records/c2-forgery-after.txt (sha256 aside).",
         "All receipts, the pin table, the hunk inventory and the direct-run comparison. Any mismatch is HIGH.",
         ),
    seat("R94ExecCensus", "executor",
         "Reported, not claimed: how many of the r93 search's historical KILLS are crashes? " + own("R94ExecCensus"),
         "Score EVERY generated mutant of the frozen r87 counter on the r93 population twice: (a) with the r94 search "
         "(no --ids; --jobs 5; --emit <seat dir>/survivors-r94.json) and (b) with census/round-94/c1-control-r93-rule.py "
         "(the r93 rule; no --ids; --jobs 5). Same harness/population/counter args as the C1 predicate. Each run is "
         "~280 harness runs at ~17 s / 5 jobs (~16 min); run (a) then (b), never concurrently, and keep only "
         "harness.out files you cite (copy the SEARCH lines, not the trees). Then list every id whose verdict differs "
         "between (a) and (b) with its rc=70 row count, and every `errored`/`hung` id in (a). Is any non-crash "
         "verdict different between the two rules (that would contradict the claim that the rule only reclassifies "
         "crashes — FALSIFIES-WORDING if so)?",
         "Both SEARCH-SUMMARY lines, the difference table, the errored list and your verdict.",
         ),
    seat("R94ReviewerC1", "reviewer",
         "Correctness review of the r94 search's crash sentinel and kill rule against the C1 wording. " + own("R94ReviewerC1"),
         "Read census/round-94/c1-survivor-search.py, census/round-93/c1-false-row-harness.py (how it starts the "
         "counter and prints ROW lines: every branch) and the prereg C1. Check: (1) does every harness branch that "
         "runs the counter print `rc=<counter rc>` so rc=70 is visible (ledger, ledger-drop/trim, ledger-resolve, "
         "forge path, lane/fixture rows)? Name any branch where a counter crash would NOT show rc=70. (2) Can a "
         "non-crash mutant reach rc=70 (the counter or git returning 70)? (3) Is the precondition check equivalent "
         "to how the harness starts the counter (env, -B, cwd)? (4) Is `errored` counted in S = E + K + V? (5) Does "
         "the claim sentence say anything the predicate does not check? Run what you need in scratch (e.g. one-id "
         "searches) and keep receipts.",
         "Per-question verdict with line numbers and receipts; FALSIFIES-WORDING/NUMBER or NO-FALSIFICATION.",
         ),
    seat("R94ReviewerC2", "reviewer",
         "Correctness review of the r94 probe's setup discipline and the arms counter against the C2 wording. " + own("R94ReviewerC2"),
         "Read census/round-94/c2-forgery-probe.py and census/round-94/c2-setup-arms.py and the prereg C2. Check: "
         "(1) can the r94 probe still exit 1 on any setup failure (an unreadable-but-present file, a fixture that is a "
         "directory, a --work symlink to a directory, a --work whose parent is missing, a fixture that hangs)? Try "
         "each in scratch, recording exit code and stderr. (2) Does each arm test what its label says (e.g. S8: does "
         "the synthetic fixture really pass the positive control and crash only on forgeries)? (3) Does the arms "
         "counter's `line` check read the right stream? (4) Is the claim's '7 of the 8 setup arms' and 'before 3' "
         "exactly what census/round-94/controls/c2-control-r93-probe.txt shows? (5) Any sentence wider than the "
         "predicate?",
         "Per-question verdict with receipts; FALSIFIES-WORDING/NUMBER or NO-FALSIFICATION.",
         ),
    seat("R94Critic", "critic",
         "Falsify both claims' wording, axis fit, separability and do-nothing controls. " + own("R94Critic"),
         "1. C1 is named calibration: does it count a mismatch between the lane's self-assessment (the search's "
         "verdict) and observed state (a crash)? Is a hand-written crash fixture a fair target, or could any rule "
         "that greps something reach errored=2? Build one cheap alternative kill rule that is NOT the sentinel and "
         "see whether it meets the predicate (if it does, the claim's 'crash sentinel' is not what the number "
         "proves).\n2. C2 is named operability: is '10 arms chosen by the L1' a surface or a count? Build the "
         "cheapest probe edit that reaches 10/10 without real setup discipline (e.g. special-casing the arm inputs).\n"
         "3. Separability: can C1 be verified with C2 not landed and vice versa?\n4. Prereg vs claims: any "
         "universal word ('every', 'all') the counter does not enumerate?",
         "Per-item verdict with reproducers; FALSIFIES-WORDING/NUMBER or NO-FALSIFICATION per claim.",
         ),
    seat("R94MutC1", "mutation-tester",
         "Mutation-test the r94 search's sentinel and rule: which one-edit mutants of census/round-94/c1-survivor-search.py "
         "does the C1 predicate fail to catch? " + own("R94MutC1"),
         "Write at least 8 one-edit mutants of the r94 search (scratch copies), targeting: CRASH_RC value in the hook "
         "vs in verdict(); the ` rc=70 match=` substring; the `rc == CRASH_RC` disjunct; the `rc == 0` branch order; "
         "the endswith(' match=no') test; the PYTHONPATH prepend; the precondition check; the hook's flush. Run each "
         "through the C1 predicate command (substitute your mutant for the search; --jobs 5). A mutant SURVIVES if "
         "it still prints the exact predicate summary and per-id verdicts with EXIT 0. Report each with its edit, "
         "summary and verdict; classify survivors equivalent / unbound.",
         "Mutant table (edit, summary, killed/survived, classification); survivors are findings.",
         ),
    seat("R94MutC2", "mutation-tester",
         "Mutation-test the r94 probe's setup checks and the arms counter: which one-edit mutants does the C2 "
         "predicate fail to catch? " + own("R94MutC2"),
         "Write at least 8 one-edit mutants of census/round-94/c2-forgery-probe.py (each setup check removed or "
         "loosened; the res-is-None checks; exist_ok) and at least 3 of census/round-94/c2-setup-arms.py (want "
         "codes, stream choice, conform test). Score probe mutants with the C2 predicate command (substitute the "
         "probe); score arms-counter mutants by running them on the r94 probe AND on the r93 probe (a counter "
         "mutant that also gives the r93 probe 10/10 is a broken counter). Report each with its summary.",
         "Mutant tables; survivors are findings with classification.",
         ),
    seat("R94Sentinel", "sentinel",
         "Safety and robustness of the crash sentinel and the probe's setup handling. " + own("R94Sentinel"),
         "1. The sitecustomize hook under --work/hook: can it leak into anything outside the harness process tree "
         "(it is passed via env only)? Does it shadow an existing sitecustomize on this host? What happens with a "
         "pre-set PYTHONPATH, PYTHONNOUSERSITE, `python -I`, or a counter that spawns a thread that raises, calls "
         "os._exit(1), or is killed by SIGSEGV/SIGKILL? Build tiny scratch counters/harness copies to show each "
         "outcome (rc and verdict).\n2. Does the hook's os._exit(70) lose buffered stdout (flush order)?\n3. The "
         "r94 probe: a --work that is a symlink to /tmp — refused? A race where --work is created between the "
         "check and makedirs? Paths the probe or arms counter write outside --work?\n4. Do the C1/C2 instruments "
         "write under /tmp regardless of TMPDIR/--work?",
         "Findings HIGH/MEDIUM/LOW with reproducers, or 'no finding' per item with what was tried.",
         ),
    seat("R94Connector", "connector",
         "Cross-lane overlap scan plus the planning data-walk the L1's planner seat delegates. " + own("R94Connector"),
         "1. Sibling overlap: grep the sibling lane repos under {FLEET}/*-shokunin/ (read-only) for a mutation "
         "search that separates crashes from kills, a sys.excepthook/sitecustomize sentinel, or a setup-vs-verdict "
         "exit-code discipline; say whether any sibling owns this surface, with paths.\n2. Lane pattern: list other "
         "lane instruments under census/round-8*/ and census/round-9*/ whose exit 1 can come from an uncaught "
         "exception or a setup failure as well as from a verdict (same class as C1/C2), with paths and how you know.\n"
         "3. Planning data-walk: read corpus/lessons/round-93-verifier-spotcheck.md §5 routed items 1-5 and "
         "SCORECARD.md `### Planned (r94)`; mark each answered / partly / carried with the r94 file that answers it; "
         "draft the `### Planned (r95)` bullet list.\n4. SOURCES rule 2: `git -C {LANE} diff {BASE} -- "
         "corpus/SOURCES.md` must show only added rows (S357, S358), no edited cell.",
         "Overlap verdict with paths, the pattern list, the routed-item table and r95 draft, and the rule-2 check.",
         ),
    seat("R94ScoutSources", "scout",
         "Re-open the round's two new sources live and find one rejectable candidate. " + own("R94ScoutSources"),
         "1. Fetch https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ and "
         "https://man.freebsd.org/cgi/man.cgi?query=sysexits now; compare sha256 and size with the S357/S358 rows "
         "(dynamic pages may differ: then diff the tag-stripped text). Confirm each row's quoted sentence occurs, "
         "its word count, and its occurrence count in whitespace-normalized tag-stripped text.\n2. Find ONE more "
         "candidate source on how a mutation tool classifies a crashing run (e.g. PIT's mutation statuses, mutmut's "
         "result kinds, Python's sys.excepthook docs) and judge it against corpus/QUALITY.md and PROVINCE.md: admit "
         "or reject with reason and flip condition; give URL, access date and a <=25-word located quote. Do not edit "
         "corpus/.",
         "Per-row verify table (hash/size/quote/count) and one candidate verdict with quote.",
         ),
    seat("R94Scribe", "scribe",
         "Draft the round lesson blocks from committed evidence. " + own("R94Scribe"),
         "Read census/round-94/ (prereg, controls), corpus/lessons/round-93.md (format) and "
         "corpus/lessons/round-93-verifier-spotcheck.md. 1. Draft `## Mistakes` rows (class · evidence pointer · "
         "captured-by · fix; a fix counts only once shown able to fail): at least the r93 search docstring's false "
         "'(the counter crashed, rc 2)' assumption, and the r93 probe's FileExistsError exit 1, each pointing at the "
         "r94 control receipt that shows the fix able to fail.\n2. Draft one corpus/QUALITY.md criterion (next free Q "
         "number after the last in corpus/QUALITY.md) that would have caught both: an instrument's verdict exit code "
         "must not be reachable by an uncaught exception or setup failure, with a counting command.\n3. Draft the "
         "`## Gate` block for S357/S358 (URL, access date 2026-11-09, quote, locator) leaving the reject slot for the "
         "scout.",
         "Draft text blocks in your report, each line carrying its evidence path.",
         ),
]


def main():
    print(json.dumps({"wave": "souji-r94-w1",
                      "milestone": "souji r94: C1 a crash sentinel (exit 70) and kill rule score crashing mutants "
                                   "errored, not killed (calibration, S357/S358); C2 the forgery probe's setup "
                                   "failures exit 2, not its verdict code 1 (operability)",
                      "reportDir": ".ufo/waves/round-94/w1",
                      "context": CTX,
                      "items": ITEMS}, indent=1))


if __name__ == "__main__":
    main()
