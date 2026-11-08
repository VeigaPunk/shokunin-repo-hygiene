#!/usr/bin/env python3
"""Build the souji r85 wave-1 spec. Run: python3 .ufo/waves/round-85/build-spec.py > .ufo/waves/round-85/w1-spec.json
P and F hashes are read from the lane's git branch (P = instruments + controls + before receipts, F = prereg alone)."""
import json
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"

GOD = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim \u2014 let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

"""


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], stdout=subprocess.PIPE, text=True,
                          check=True).stdout.strip()


base = git("rev-parse", "master")
log = git("log", "--format=%H %s", "-6", "master").splitlines()


def find(prefix):
    for l in log:
        h, _, s = l.partition(" ")
        if s.startswith(prefix):
            return h
    return "<" + prefix + ": not found yet>"


p_hash = find("round-85: instruments")
f_hash = find("round-85: preregistration")

CTX = f"""# Goal
souji round 85 (lane repo {LANE}, lane id souji). The L1 (SoujiR85) holds the planner seat and is the ONLY
integration owner: it freezes the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 12 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every `Report:` trailer path is relative to {LANE} \u2014 write it at {LANE}/<that path>.

# Write scope and scratch
Write ONLY under {LANE}/.ufo/waves/round-85/w1/<YourSeatName>/ and your report file. Everything else in the lane is
read-only to you. All clones, mirrors, fixtures and counter `--work` dirs live under
/fast/scratch/hyaku/souji-r85/<YourSeatName>/ (mkdir -p; never /tmp). Delete your scratch dir before you yield
(`trap 'rm -rf -- "$S"' EXIT`), copying receipts into your seat dir first.

# Frozen round (read {LANE}/census/round-85/preregistration.txt FIRST \u2014 it is the contract)
Lane base: {base} (r84 closed admitted; spot-check corpus/lessons/round-84-verifier-spotcheck.md). P {p_hash}:
instruments, populations, mutants, controls and the before receipts. F {f_hash}: the preregistration alone.
C1 (calibration 7, the lane's lowest owned non-retired axis): the lane's false-row population is the instrument that
certifies the pointer counter's rule. The r85 population census/round-85/c1-false-rows.tsv (47 rows: the r84 44
byte-for-byte plus NF-R, TF11 and NF-S, all at the new fixture revision R8) adds the row that reaches the counter's
ledger-class enum guard. claim: on that population the counter census/round-85/c1-pointer-counter.py is green and
census/round-85/c1-clause-battery.py kills all six frozen single-edit mutants (m6..m10 unchanged, plus m11-class-enum)
where the same battery on the r84 44-row population kills five and leaves m11 alive.
C2 (operability 8): tools/souji-record-agreement.py key K4 (uncommitted round work) reads `git status` and nothing
else, so an index stat-cache forgery reads clean. claim: K4 re-hashes status-clean stage-0 tracked paths against the
index object id through the receipt writer's `_truth_refusal`, so census/round-85/c2-k4-counter.py reports 3
mismatches on the base tool bytes and 0 on the filed bytes, with the honest rows unchanged.
Both claims are instruments-plus-code: an instrument mutation (C1) and a tool repair (C2), each re-derivable from
committed bytes by one command. Nothing here authorises deletion, quarantine or a signal to a process you did not
start.

# Tooling authorization (operator, 2026-10-19)
You may install or upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels,
update-safety gate) and record tool/version/channel/reason in your report.
**pacman guard (orchestrator ruling 2026-10-20):** ALL pacman transactions are PAUSED host-wide. Install via
`uv tool`/`npx`/an official binary in ~/.local/bin only; never `-Sy`/`-Syu`/`-U`/`-R`/downgrade, never restart a host
service, never mutate a host sysctl.

# Hard rules
- Never run a mutating git/jj command in {LANE}: no add/commit/stash/checkout/switch/reset/pull/push, no jj write.
  Fixture repos are yours: `D=/fast/scratch/hyaku/souji-r85/<YourSeatName>/fx && git init "$D"` and every later call
  is `git -C "$D" ...`; assert `git -C "$D" rev-parse --show-toplevel` equals `$D` before the first commit.
- Never pass an empty or unchecked variable to `git -C`.
- A counter's `--work` dir must not be under /tmp; every tool in this round refuses it.
- No `agent://all`. Findings go in your report file and your final yield.
"""

ITEMS = []
ITEMS.append({"name": "S85ExecC1", "role": "executor", "prompt": GOD + f"""# Target
Re-derive both C1 arms end to end on the committed bytes, independently of the L1. OWN ONLY
{LANE}/.ufo/waves/round-85/w1/S85ExecC1/.

# Change
1. Run `python3 -B {LANE}/census/round-85/c1-clause-battery.py --counter census/round-85/c1-pointer-counter.py
   --work <your empty scratch> --only r85 --expect-killed 6` and the same command with `--only r84 --expect-killed 5`.
   Record both outputs byte-for-byte in your seat dir.
2. Derive from census/round-85/c1-pointer-counter.py `judge()` exactly why NF-S goes red under m11-class-enum and why
   the r84 population cannot kill m11 (which branch each row reaches). Quote the branch line numbers.
3. Attack the pins: change one byte of census/round-85/c1-false-rows.tsv and confirm the harness and the battery
   refuse (FATAL, exit 2); confirm the same for census/round-85/c1-items.tsv against the counter.
4. Report the tool/counter/harness/mutants sha256 you ran, and whether every number the preregistration names
   reproduces.

# Acceptance
Your report carries: both ARM/SUMMARY blocks verbatim, the branch derivation with line numbers, the three pin
refusals with their stderr, and a one-line verdict per frozen sentence (reproduces / does not).
"""})
ITEMS.append({"name": "S85ExecEvade", "role": "executor", "prompt": GOD + f"""# Target
Try to make the r85 C1 population green while the counter is wrong: build false rows the 47-row population does not
carry. Read-only on the lane; all work in your scratch. OWN ONLY {LANE}/.ufo/waves/round-85/w1/S85ExecEvade/.

# Change
1. Copy census/round-85/c1-pointer-counter.py and census/round-85/c1-false-row-harness.py into your scratch and add
   rows of your own design (a new fixture rev is allowed; the harness's `build_fixture` is yours to extend in YOUR
   copy, never in the lane).
2. Attack the resolution classes: a MOVED target that keeps the basename and round but changes case; a QUARANTINED
   row whose declaration sits in a file outside AUTHORITY; a TOKEN row with a trailing artefact whose continuation is
   a prefix; an ABSENT row whose token is only in a keep ref; a LOCAL-POLICY row outside the frozen prefixes.
3. For each attack say what the counter returns, whether the population would have caught it, and the exact sentence
   of the C1 claim it falsifies (if any).

# Acceptance
A table of attacks with the counter's actual output lines. Attacks that survive are the round's routed defects; do
not soften them.
"""})
ITEMS.append({"name": "S85ExecK4", "role": "executor", "prompt": GOD + f"""# Target
Attack the C2 repair in tools/souji-record-agreement.py key K4. OWN ONLY
{LANE}/.ufo/waves/round-85/w1/S85ExecK4/.

# Change
1. Read the repair (grep -n truth_refusal tools/souji-record-agreement.py) and the frozen counter
   census/round-85/c2-k4-counter.py. Run the counter on the filed tool (expect SUMMARY rows=7 mismatches=0) and on
   census/round-85/controls/c2-K-a-base-tool.py (expect 3).
2. Break it: (a) remove tools/souji-receipt-write.py from a COPY of the tool dir and confirm the tool fails closed
   rather than reporting clean; (b) make the writer refuse (a tree the writer exits 2 on) and confirm K4 still
   reports; (c) a status-clean path whose index entry is stage-2 (conflict) or intent-to-add; (d) a submodule
   (gitlink) whose commit changed; (e) a path with a newline in its name.
3. Say for each: does K4 report, with which class/record, and does the class name the path a reader can act on.

# Acceptance
Each probe has a command, its output, and a verdict (protected / escapes / fails open). Anything that escapes is a
routed defect for the report.
"""})
ITEMS.append({"name": "S85Scribe", "role": "scribe", "prompt": GOD + f"""# Target
Drafts for the L1 to integrate, under {LANE}/.ufo/waves/round-85/w1/S85Scribe/.

# Change
1. A new section for {LANE}/corpus/knowledge/own-tree-pointer-binding.md: "A shadowed clause is not an unbound
   clause" — the difference between a rule clause with no row and a clause another belt makes unreachable, how to
   tell them apart (a single-edit mutant survives both populations AND the branch cannot be reached, versus a mutant
   killed by a new row), and why the census-in-tree branch is the first class (quote the branch order from
   census/round-85/c1-pointer-counter.py `judge()` with line numbers).
2. A new section for {LANE}/corpus/knowledge/gate-signal-handling.md OR a new entry proposal (your judgement, name
   which): "the audit tool is not exempt from the rule it audits" — record-agreement K4 trusted `git status` while
   the lane's writer and pre-report gate had already stopped doing so, with the pointer to
   tools/souji-record-agreement.py truth_refusal and census/round-85/c2-k4-counter.py.
3. Two QUALITY.md rows (Q156, Q157) in the round-84 style: one for the shadow-vs-unbound distinction, one for
   "a tool that reads a lane signal must re-derive it, not trust the tool that produced it".
4. Keep drafts in your seat dir; do not edit the lane's corpus files.

# Acceptance
Drafts with resolvable pointers to committed paths/line numbers, and a `## Gate` note naming which draft is which
entry. Quote only what you opened this round.
"""})
ITEMS.append({"name": "S85ScoutShapes", "role": "scout", "prompt": GOD + f"""# Target
Reconnaissance: which `census/round-<N>/` shapes the lane really holds, and whether the census-token refusal has a
reachable clause at all. OWN ONLY {LANE}/.ufo/waves/round-85/w1/S85ScoutShapes/.

# Change
1. Census the lane's `census/round-*` subtrees at the lane base: for each round, the immediate children and their
   kinds (`waves/`, `records/`, `records/wave-*`, `decoy/`, plain files). Give one command and its output.
2. For the branch order in census/round-85/c1-pointer-counter.py `judge()`, decide by construction whether the
   census-in-tree branch (`token[:kr.start(0)] == "census" and target[:tr.start(0)] == "census"`) can ever be the
   first refusing branch: enumerate the (token root, target root) pairs and say which branch fires.
3. Name which of the lane's real `census/round-<N>/` paths already appear on a committed authority line (LOG.md,
   SCORECARD.md, SKILL.md, corpus/) so a future population row can point at one without fabricating a line.

# Acceptance
A table of real shapes, the branch-order argument, and the list of census-token source lines with file:line.
"""})
ITEMS.append({"name": "S85ScoutSources", "role": "scout", "prompt": GOD + f"""# Target
Open the sources the two knowledge sections need, this round, with URL + access date + a located quote of <=25 words
each. OWN ONLY {LANE}/.ufo/waves/round-85/w1/S85ScoutSources/.

# Change
1. Read {LANE}/corpus/SOURCES.md's shape (contract v1 in {FLEET}/CORPUS.md) and the highest S id in the registry.
2. Open and capture, each into your seat dir with a sha256: (a) git-status(1) or git-update-index(1) as installed
   (`man git-status`), the section that states status compares the index to the work tree; (b) gitformat-index(5)
   as installed, the entry-fields list showing cached stat data beside the object name; (c) one authoritative page
   on mutation testing adequacy (an accessible abstract or a spec, e.g. the PIT/docs or an ACM/IEEE abstract you can
   fetch) that states a test suite's adequacy is measured by the mutants it kills.
3. For each: the row you would write (id, source, kind, tier, scope, anchor with revision, teaches), the exact
   located quote, and whether it is already in the registry (check by URL, not by title).

# Acceptance
Three draft rows with quotes at a named location and a revision, plus the duplicate-URL check command and its
output. A source you could not fetch is reported as unreachable, not fabricated.
"""})
ITEMS.append({"name": "S85Connector", "role": "connector", "prompt": GOD + f"""# Target
Cross-claim and sibling-overlap scan for round 85. OWN ONLY {LANE}/.ufo/waves/round-85/w1/S85Connector/.

# Change
1. **Separability:** prove or falsify that C1 (census/round-85/* instruments, census/round-85/c1-items.tsv) and C2
   (tools/souji-record-agreement.py + census/round-85/c2-k4-counter.py) share no file, command, population, receipt
   or counter. Name every shared path you find.
2. **Sibling overlap:** does any other lane own record-agreement K4, the receipt writer's `_truth_refusal`, or the
   pointer-resolution counter? Check the sibling PROVINCE.md files under {FLEET} for a claim on those surfaces and
   report contested scope rather than absorbing it.
3. **Carry:** check the routed lists in {LANE}/corpus/lessons/round-84.md `## Routed to round 85` and the
   SCORECARD r85 planned block; say which items this round actually answered, which it silently dropped, and which
   are still open.
4. **Prior art:** is there already a lane tool that re-hashes status-clean paths (souji-receipt-write.py,
   tools/souji-pre-report-gate.sh check 4)? If so, is the C2 repair a second implementation of one rule (report it)
   or a reuse (say how)?

# Acceptance
Four numbered sections, each with a command or a quoted pointer. "No overlap" needs the sweep that shows it.
"""})
ITEMS.append({"name": "S85Reviewer", "role": "reviewer", "prompt": GOD + f"""# Target
Independent re-derivation of both claims on the committed bytes, plus chronology. OWN ONLY
{LANE}/.ufo/waves/round-85/w1/S85Reviewer/.

# Change
1. Re-run the C1 battery yourself: `--only r84 --expect-killed 5` and `--only r85 --expect-killed 6`, scratch under
   /fast/scratch/hyaku/souji-r85/S85Reviewer/. Report `ARM`/`SUMMARY` lines and exit codes, and whether they equal
   census/round-85/controls/c1-before-r84-population.txt and census/round-85/records/c1-after.txt (if the after
   receipt is absent, say so and report yours as the measurement).
2. Re-run the C2 counter on the filed tool and on census/round-85/controls/c2-K-a-base-tool.py; compare with
   census/round-85/controls/c2-before-base-tool.txt.
3. Chronology: `git log --format='%h %ci %s' -6 master`; P must carry the instruments/controls/before receipts and
   F the preregistration ALONE (`git show --name-only <F>`), both before any after-arm receipt. Say if any after-arm
   byte existed before F.
4. Verify the counter changed only its pin table: `git diff <r84 counter> <r85 counter>` (or `diff` of the two files)
   must show one POPS entry plus the docstring.

# Acceptance
Both claims re-derived, with the exact command and observed lines; chronology and the counter diff stated as pass or
fail with evidence.
"""})
ITEMS.append({"name": "S85Critic", "role": "critic", "prompt": GOD + f"""# Target
Falsify the WORDING of both claims before the round files them. OWN ONLY {LANE}/.ufo/waves/round-85/w1/S85Critic/.

# Change
1. C1: the claim says the population is the instrument and a kill is its discriminating power. Attack it: (a) can a
   counter with a *worse* rule also score 6/6 on these 47 rows (i.e. is the population separable from the rule)?
   (b) is NF-R/TF11 load-bearing or decoration (which mutant does each kill)? (c) does "the counter is green on the
   r84 44 rows" rest on the r84 counter's own pins, or on the r85 counter's pin table? (d) is m11 a *clause* of the
   rule or a guard of the harness interface?
2. C2: (a) is K4's repair the production path a reader runs, or a helper only the fixture calls? (b) does the claim
   hold when the writer is absent (fail-closed vs fail-open)? (c) are the three forged rows one class or three?
   (d) does "honest rows unchanged" include a row where the honest tree is dirty?
3. For each: the sentence of the preregistration it falsifies, or `neutral` with the reason.

# Acceptance
A verdict line per attack: `falsifies-wording` / `falsifies-number` / `neutral` plus the narrowing each falsification
would require. Write interim findings to your report file as you go (the L1 reads it before integration).
"""})
ITEMS.append({"name": "S85MutCounter", "role": "mutation-tester", "prompt": GOD + f"""# Target
Extend the mutation evidence for the C1 counter beyond the frozen six. OWN ONLY
{LANE}/.ufo/waves/round-85/w1/S85MutCounter/.

# Change
1. Take census/round-85/c1-mutants.json as the baseline (six mutants, all killed on the r85 population by
   construction).
2. Author new single-edit mutants in YOUR scratch copy of census/round-85/c1-pointer-counter.py: at least six, each
   dropping a different clause or guard (the R0 line check, the `not kr` guard, the `len(want) < 2` guard, the
   `_capture_ok` non-empty want, the NF6b punctuation allowance, the duplicate-id refusal in `_ledger`).
3. Score each on BOTH pinned populations with your own harness invocation (the harness accepts `--population`). A
   mutant that survives both is a clause no row binds — list it with the line it edits. A mutant killed by the r84
   population is not new coverage; say so.
4. Do not edit the lane's counter, mutants file or populations.

# Acceptance
A table: mutant id, edited line, killed on r84, killed on r85, verdict (new binding / already bound / unbound).
Your survivors are the round's routed defects.
"""})
ITEMS.append({"name": "S85MutK4", "role": "mutation-tester", "prompt": GOD + f"""# Target
Mutation-test the C2 repair: which clauses of the new K4 check does the frozen counter actually kill? OWN ONLY
{LANE}/.ufo/waves/round-85/w1/S85MutK4/.

# Change
1. Copy tools/souji-record-agreement.py and tools/souji-receipt-write.py into your scratch dir (the copy must hold
   both, the tool resolves the writer beside itself).
2. Author clause mutants of the repair: (a) `truth_refusal` returns None unconditionally; (b) the call site removed;
   (c) the call kept but its message discarded (no `bad()` row); (d) `_truth_refusal`'s stage-0 filter widened to
   every stage; (e) the writer's `hash-object` result compared to the wrong field.
3. Score every mutant with census/round-85/c2-k4-counter.py --tool <your mutant copy> and report which rows went red
   (and whether the red is a real forgery kill or a fixture error). A mutant that scores 0/7 survives — name the
   clause it drops and whether the population has a row for it.

# Acceptance
Table: mutant, edited line, SUMMARY line, killed/survived, the row that killed it. Survivors are routed defects.
"""})

ITEMS.append({"name": "S85Sentinel", "role": "sentinel", "prompt": GOD + f"""# Target
Adversarial review of the two claims' surfaces: can the C2 repair be made to run code it should not, and can the C1
population be made to certify a counter that resolves a wrong file? OWN ONLY
{LANE}/.ufo/waves/round-85/w1/S85Sentinel/.

# Change
1. **Import hijack (C2):** truth_refusal compiles tools/souji-receipt-write.py from a path resolved beside the tool
   (`__file__`). Probe: a tool copy in another directory with no writer (must fail closed); a tool copy beside a
   STUB writer whose `_truth_refusal` returns None (does K4 report clean? that is code execution from a path an
   attacker may control - state the threat model: same trust as the gate); a symlinked tool; a tool invoked through a
   relative path from another cwd; a writer that raises SystemExit and one that raises mid-run.
2. **Fail-open sweep (C2):** is there any path where truth_refusal's message is produced but no K4 row is emitted, or
   where status fails and the truth check is skipped? Read the k4 body line by line and say which branch order does
   it.
3. **Counter scope (C1):** can a ledger row with a class the counter implements but the population does not exercise
   (LOCAL-POLICY outside the frozen prefix, FLEET with a `fleet:` target) resolve a wrong file while both pinned
   populations stay green? One probe each, with the counter's output.
4. **Writes:** does either instrument write inside the lane at run time (`git status` index refresh counts)? Say what
   it writes and where.

# Acceptance
Each probe: command, output, verdict (protected / escapes / fails open), and the sentence of the preregistration it
constrains.
"""})

spec = {
    "wave": "souji-r85-w1",
    "milestone": ("souji r85: C1 the false-row population binds the counter's class-enum guard (calibration), "
                  "C2 record-agreement K4 re-derives tracked bytes instead of trusting git status (operability)"),
    "reportDir": ".ufo/waves/round-85/w1",
    "context": CTX,
    "items": ITEMS,
}


if __name__ == "__main__":
    json.dump(spec, sys.stdout, indent=1, ensure_ascii=False)
    sys.stdout.write("\n")
