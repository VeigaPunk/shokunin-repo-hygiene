#!/usr/bin/env python3
"""Build the souji r86 wave-1 spec. Run: python3 .ufo/waves/round-86/build-spec.py > .ufo/waves/round-86/w1-spec.json
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
log = git("log", "--format=%H %s", "-8", "master").splitlines()


def find(prefix):
    for l in log:
        h, _, s = l.partition(" ")
        if s.startswith(prefix):
            return h
    return "<" + prefix + ": not found yet>"


p_hash = find("round-86: instruments")
f_hash = find("round-86: preregistration")
c2_hash = find("round-86: C2 repair")

CTX = f"""# Goal
souji round 86 (lane repo {LANE}, lane id souji). The L1 (SoujiR86) holds the planner seat and is the ONLY
integration owner: it freezes the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 12 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every `Report:` trailer path is relative to {LANE} \u2014 write it at {LANE}/<that path>.

# Write scope and scratch
Write ONLY under {LANE}/.ufo/waves/round-86/w1/<YourSeatName>/ and your report file. Everything else in the lane is
read-only to you. All clones, mirrors, fixtures and counter `--work` dirs live under
/fast/scratch/hyaku/souji-r86/<YourSeatName>/ (mkdir -p; never /tmp). Delete your scratch dir before you yield
(`trap 'rm -rf -- "$S"' EXIT`), copying receipts into your seat dir first.

# Frozen round (read {LANE}/census/round-86/preregistration.txt FIRST \u2014 it is the contract)
Lane base: {base} (r85 closed admitted; spot-check corpus/lessons/round-85-verifier-spotcheck.md). P {p_hash}:
instruments, populations, mutants, controls and the before receipts. F {f_hash}: the preregistration alone.
C2 repair commit {c2_hash} (tools/souji-record-agreement.py, sha256 4cc3b945…).
C1 (calibration 7, the lane's lowest owned non-retired axis): the lane's false-row population is the instrument that
certifies the pointer counter's rule, and a clause with no row is not certified. The r86 population
census/round-86/c1-false-rows.tsv is the r85 47 rows byte-for-byte plus NF-W (the census-in-tree shape r85 A1 /
S85Scribe F1 measured reachable-and-unrowed) and NF-Y (the own-tree short-shape r85 A4 / S85MutCounter m14 measured
the same way), at a new fixture revision R9. claim: on those 49 rows the counter
census/round-86/c1-pointer-counter.py is green and census/round-86/c1-clause-battery.py kills all eight frozen
single-edit mutants (m6..m11 unchanged, plus c7-census-in-tree and m14-short-shape), where the same battery and
mutants on the r85 47 rows kill six and leave c7 and m14 alive.
C2 (operability 8): record-agreement K4 applied the writer's `_truth_refusal`, which skips stage!=0 and mode 160000,
and the writer's `_flag_refusal` (the only implementation naming a concealed gitlink) lived in a path K4 never
called; a path name with a newline was space-joined out of the record. claim: K4 now runs the writer's index-flag
sweep too and C-escapes record paths, so census/round-86/c2-k4-counter.py reports 2 mismatches (KG1 gitlink concealed
under skip-worktree, KG2 a newline path not named) on the lane-base tool bytes and 0 on the filed bytes, with the
seven r85 rows unchanged.
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
  Fixture repos are yours: `D=/fast/scratch/hyaku/souji-r86/<YourSeatName>/fx && git init "$D"` and every later call
  is `git -C "$D" ...`; assert `git -C "$D" rev-parse --show-toplevel` equals `$D` before the first commit. Never
  pass an empty or unchecked variable to `git -C`.
- A counter's `--work` dir must not be under /tmp; every tool in this round refuses it.
- No `agent://all`. Findings go in your report file and your final yield.
"""

ITEMS = []
ITEMS.append({"name": "S86ExecC1", "role": "executor", "prompt": GOD + f"""# Target
Re-derive both C1 arms end to end on the committed bytes, independently of the L1. OWN ONLY
{LANE}/.ufo/waves/round-86/w1/S86ExecC1/.

# Change
1. Run `python3 -B {LANE}/census/round-86/c1-clause-battery.py --counter census/round-86/c1-pointer-counter.py
   --work <your empty scratch> --only r85,r86 --expect-killed 14`, then the same command with
   `--only r85 --expect-killed 6`. Record both outputs byte-for-byte in your seat dir.
2. Derive from census/round-86/c1-pointer-counter.py `judge()` exactly why NF-W goes red under c7 and NF-Y under m14,
   and why neither the r85 47 rows nor the r84 44 rows can kill them. Quote the branch line numbers and the guard.
3. Attack the pins: change one byte of census/round-86/c1-false-rows.tsv and of census/round-86/c1-items.tsv and
   confirm the harness, the battery, and the counter refuse (FATAL, exit 2 in each case).
4. Confirm the r86 counter differs from census/round-85/c1-pointer-counter.py only in its POPS table and docstring:
   `diff` the two files and classify every hunk.

# Acceptance
Your report carries: both ARM/SUMMARY blocks verbatim, the branch derivation with line numbers, the three pin
refusals with their stderr, and the diff classification.
"""})
ITEMS.append({"name": "S86ExecK4", "role": "executor", "prompt": GOD + f"""# Target
Re-derive the C2 arms and try to break the repaired K4 again. OWN ONLY
{LANE}/.ufo/waves/round-86/w1/S86ExecK4/.

# Change
1. Run `python3 -B {LANE}/census/round-86/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <scratch>`
   (expect SUMMARY rows=9 mismatches=0) and the same on
   census/round-86/controls/c2-before-base-tool.py (expect 2: KG1 k4=0, KG2 named=no). Record both verbatim.
2. Break the repair: (a) a copy of the tool with NO writer beside it; (b) a copy with a LYING writer beside it (the
   stub returns None and defines no `_flag_refusal`); (c) a tree where the writer's flag read fails (corrupt index);
   (d) an honest tree with a stale mtime; (e) a `--assume-unchanged` regular file whose bytes changed with a forged
   stat; (f) a stage-2 conflict whose worktree bytes match stage 0.
3. For each: command, output, verdict (protected / escapes / fails open), and the sentence of C2's wording it
   constrains.

# Acceptance
Every probe has its command, its output, and a verdict. An escape is a routed defect, not a softened note.
"""})
ITEMS.append({"name": "S86MutCounter", "role": "mutation-tester", "prompt": GOD + f"""# Target
Attack C1's mutant set and population: are the two new rows load-bearing for the clause they claim, and does a
different single edit of the same clause survive? OWN ONLY {LANE}/.ufo/waves/round-86/w1/S86MutCounter/.

# Change
1. Reproduce the frozen battery on both populations (commands in the preregistration).
2. Author at least six NEW single-edit mutants beyond the frozen eight, at least two of which edit the SAME clauses
   as c7 and m14 in a different way (e.g. drop only the `not` of the branch condition; replace the short-shape guard
   with `len(want) < 1`), and score each on both pinned populations with
   {LANE}/census/round-86/c1-false-row-harness.py.
3. For every survivor, split dead from reachable-but-unexercised with a differential probe on `judge()` /
   `_owntree_ok` (the r85 S85MutCounter method, `reach.py` is your model). Do not edit the lane's populations or
   mutants file; your mutants live in your seat dir.
4. Say whether NF-W and NF-Y each kill exactly one clause, and whether any frozen mutant is killed by them for the
   WRONG reason (an error rather than a mismatch).

# Acceptance
A table of mutants with killed/survived per population, the reachability verdict per survivor, and the
errors-vs-mismatches split. Your own instrument bytes and hashes recorded.
"""})
ITEMS.append({"name": "S86Scribe", "role": "scribe", "prompt": GOD + f"""# Target
Drafts for the L1 to integrate, under {LANE}/.ufo/waves/round-86/w1/S86Scribe/.

# Change
1. A new section for {LANE}/corpus/knowledge/own-tree-pointer-binding.md: "Grounding an unbound clause: the row is
   the work" - what r86 added (NF-W, NF-Y), how each row reaches exactly one clause, and the check that a row kills
   its mutant on the new population and not on the old one. Quote the branch lines from
   census/round-86/c1-pointer-counter.py `judge()` and the guard in `_owntree_ok`.
2. A new section for {LANE}/corpus/knowledge/filter-filemode-witness.md: "the audit tool's own concealment classes" -
   K4's two layers (truth re-hash, index-flag sweep), why skipping stage!=0 and mode 160000 left a class unmeasured
   (r85 A2, S85ExecK4 probe-d2b), and why a record must keep a path name one physical line.
3. Two QUALITY.md rows (Q158, Q159) in the round-85 style: one for "a tool that inherits a check inherits only the
   code path it calls; the classes the callee skips are unmeasured until the caller names them", one for "a record
   field that carries a filesystem name must be escaped, never space-joined".
4. Keep drafts in your seat dir; do not edit the lane's corpus files.

# Acceptance
Drafts with resolvable pointers to committed paths and line numbers, a `## Gate` note naming which draft is which
entry, and no claim the round's own receipts do not carry.
"""})
ITEMS.append({"name": "S86ScoutShapes", "role": "scout", "prompt": GOD + f"""# Target
Reconnaissance: are the two new rows' shapes real in the lane, and what do the r85-routed shapes still lack?
OWN ONLY {LANE}/.ufo/waves/round-86/w1/S86ScoutShapes/.

# Change
1. For NF-W's shape (a `census/round-<N>/` token landing in a wave directory under the same round) and NF-Y's (a
   token ONE component below its round landing in a wave capture under it): census the lane's working tree and the
   committed tree for each shape (`census/round-*` children by kind; `.ufo/waves/round-*` children by kind). One
   command per claim, with its output.
2. Name every real `census/round-<N>/` and `.ufo/waves/round-<N>/` path that appears on a committed authority line
   (LOG.md, SCORECARD.md, SKILL.md, corpus/) with file:line, and say which could carry a population row without
   fabricating a line.
3. Report the shape gap the r85 routed list still names (m12 token-on-line, m16 punctuation, m17 duplicate id, the
   basename clause) and, for each, whether a row is even expressible against the current harness population/ledger
   model. This is recon, not a claim.

# Acceptance
A table of shapes with counts from one command each, the authority-line list with file:line, and the expressibility
verdict per routed shape.
"""})
ITEMS.append({"name": "S86ScoutSources", "role": "scout", "prompt": GOD + f"""# Target
Open the sources the round's claims rest on, this round, with URL + access date + a located quote of <=25 words
each. OWN ONLY {LANE}/.ufo/waves/round-86/w1/S86ScoutSources/.

# Change
1. Read {LANE}/corpus/SOURCES.md's contract (v1 in {FLEET}/CORPUS.md) and the highest S id (S340).
2. Open and capture, each into your seat dir with a sha256: (a) git-ls-files(1) as installed (`man git-ls-files`),
   the `-v`/`-t` tag list that names what `H` and `S` mean; (b) git-update-index(1) as installed, the
   `--skip-worktree`/`--assume-unchanged` descriptions; (c) gitformat-index(5) or git-submodules(5) as installed,
   the sentence that a gitlink entry records a commit id rather than content.
3. For each: the row you would write (id, source, kind, tier, scope, anchor with revision, teaches), the exact
   located quote, and whether it is already in the registry (check by URL, not by title).
4. Say which of the three you would REJECT and why (a row that restates ground an existing row already holds is
   registry weight, not knowledge - quote the row it duplicates).

# Acceptance
Three draft rows with quotes at a named location and a revision, plus the duplicate-URL check command and its
output, plus one reject with its reason and flip. A source you could not fetch is reported as unreachable.
"""})
ITEMS.append({"name": "S86Connector", "role": "connector", "prompt": GOD + f"""# Target
Cross-claim, sibling-overlap and carry audit for round 86. OWN ONLY
{LANE}/.ufo/waves/round-86/w1/S86Connector/.

# Change
1. **Separability:** prove or falsify that C1 (census/round-86/c1-*, census/round-86/preregistration.txt) and C2
   (tools/souji-record-agreement.py + census/round-86/c2-k4-counter.py) share no file, command, population, receipt
   or counter. Name every shared path.
2. **Sibling overlap:** does any lane own record-agreement K4, the receipt writer's `_flag_refusal`, or the
   pointer-resolution counter? Check the sibling PROVINCE.md files under {FLEET} for a claim on those surfaces and
   report contested scope rather than absorbing it.
3. **Carry audit:** the r85 verifier's routed list R86-1..R86-4 and the SCORECARD r86 planned block. Say which items
   this round answered, which it silently dropped, and which are still open. R86-1 (registry count line) and R86-2
   (wave seat reports untracked) are process items: check both against the r86 wave as it lands.
4. **Prior art:** is the C2 repair a second implementation of one rule or a reuse of the writer's? Name the functions
   K4 now calls and the ones it still does not (`_witness_refusal`, `_content_snapshot`, the flag sweep's caller).

# Acceptance
Four numbered sections, each with a command or a quoted pointer. "No overlap" needs the sweep that shows it.
"""})
ITEMS.append({"name": "S86Reviewer", "role": "reviewer", "prompt": GOD + f"""# Target
Independent re-derivation of both claims on the committed bytes, plus chronology and instrument binding. OWN ONLY
{LANE}/.ufo/waves/round-86/w1/S86Reviewer/.

# Change
1. Re-run the C1 battery yourself: `--only r85 --expect-killed 6` and `--only r85,r86 --expect-killed 14`, scratch
   under /fast/scratch/hyaku/souji-r86/S86Reviewer/. Report ARM/SUMMARY lines and exit codes, and whether they equal
   census/round-86/controls/c1-before-r85-population.txt and census/round-86/records/c1-after.txt.
2. Re-run the C2 counter on the filed tool and on census/round-86/controls/c2-before-base-tool.py; compare with
   census/round-86/records/c2-after.txt and controls/c2-before-base-tool.txt. Check every receipt header digest
   against `sha256sum` of the file it names (the r85 receipt-binding defect class).
3. Chronology: `git log --format='%h %ci %s' -10 master`. P must carry the instruments/controls/before receipts, F
   the preregistration ALONE (`git show --name-only <F>`), and the C2 repair must come AFTER F; no after-arm receipt
   may have been measured before F.
4. Verify the counter diff (`diff census/round-85/c1-pointer-counter.py census/round-86/c1-pointer-counter.py`) is
   one POPS entry plus the docstring, and that the r86 ledger and r85 ledger are byte-identical.

# Acceptance
Both claims re-derived with the exact commands and observed lines; every digest checked; chronology stated as pass
or fail with evidence.
"""})
ITEMS.append({"name": "S86Critic", "role": "critic", "prompt": GOD + f"""# Target
Falsify the WORDING of both claims before the round files them. OWN ONLY
{LANE}/.ufo/waves/round-86/w1/S86Critic/.

# Change
1. C1: the claim says two clauses become certified coverage. Attack it: (a) is NF-Y's refusal really the short-shape
   guard, or does dropping the guard merely move the refusal to another clause on the SAME row (check the mutant's
   `why`)? (b) does NF-W kill c7 only because the own-tree belt is evaluated before the census branch - i.e. is
   "grounded" the right word for a branch that is never the first refusal for a real ledger row? (c) can a counter
   with a STRICTLY WEAKER rule also score 8/8 on these 49 rows? (d) do NF-W and NF-Y carry any clause other than
   their own?
2. C2: (a) is the index-flag sweep a NEW rule or the writer's rule re-run (does the claim's "same sweep the receipt
   writer runs" hold byte-for-byte in call order and config)? (b) does KG1 prove a gitlink class is measured, or only
   that a flag is read? (c) is KG2's escaped name a fix or a cosmetic change to a row that already fired?
3. For each: the sentence of the preregistration it falsifies, or `neutral` with the reason.

# Acceptance
One row per attack with the artifact and the sentence it touches. A falsified wording is more valuable than a green
check.
"""})
ITEMS.append({"name": "S86Sentinel", "role": "sentinel", "prompt": GOD + f"""# Target
Adversarial security review of the C2 repair as a privilege boundary. OWN ONLY
{LANE}/.ufo/waves/round-86/w1/S86Sentinel/.

# Change
1. Read `truth_refusal` in tools/souji-record-agreement.py and the writer's `_flag_refusal`/`git()`. Enumerate every
   way the repaired K4 can return a CLEAN verdict for a tree it did not measure: a writer that fails to define
   `_flag_refusal`; a writer whose `git()` differs; a stub that prints CLEAN/FORGED/REFUSED itself; a subprocess
   timeout; a writer path that is a symlink or a copy; an environment that changes `git ls-files -v` output.
2. Probe at least five of those, each in its own copy under your scratch (never edit tools/). For each: does K4 fail
   open, fail closed, or report a row, and does the record name the mechanism?
3. Check the escaping change: can a path name still split a record (tabs, CR, ESC, invalid UTF-8), or forge a second
   MISMATCH line inside a detail field?
4. Say which of the two repair halves is a security boundary and which is actionability, and whether the claim's
   wording says more than the probes support.

# Acceptance
Every probe with its command, output and a fail-open/fail-closed verdict; a named list of the mechanisms K4 still
does not measure, each with the reason it is out of the claim.
"""})
ITEMS.append({"name": "S86ExecEvade", "role": "executor", "prompt": GOD + f"""# Target
Try to make the r86 C1 population green while the counter is wrong, and try to make the C2 rows green while K4 is
wrong. Read-only on the lane; all fixtures in your scratch. OWN ONLY
{LANE}/.ufo/waves/round-86/w1/S86ExecEvade/.

# Change
1. C1: copy census/round-86/c1-pointer-counter.py, the harness and the battery into your scratch. Author at least
   three NEW false rows of your own design (extend the fixture in YOUR copy; the lane's files are read-only) that a
   submission-quality counter must refuse but the 49-row population/fixture cannot express. For each: what the
   counter returns, whether the population would have caught a wrong rule, and the exact sentence of C1 it
   constrains.
2. C1 attack on the new rows: can a counter that RESOLVES a wrong file still score 8/8 (e.g. a rule that also
   accepts a target whose digit-only difference is in a directory component)? One probe.
3. C2: build a tree where the repaired K4 emits a row but names the wrong path (a detail whose first 5 names are
   honest and the forged one is 6th - the writer truncates at 5 with an ellipsis). Does the record still let a reader
   act, and does the claim's wording ("names the path") survive?
4. Report every surviving attack as a routed defect, with the command and the output.

# Acceptance
A table of attacks with actual counter output. Surviving attacks are the round's routed defects; do not soften them.
"""})

spec = {
    "wave": "souji-r86-w1",
    "milestone": ("souji r86: C1 two r85-measured unreachable-in-population clauses get their rows (calibration), "
                  "C2 record-agreement K4 carries the writer's index-flag sweep and keeps record paths one line "
                  "(operability)"),
    "reportDir": ".ufo/waves/round-86/w1",
    "context": CTX,
    "items": ITEMS,
}


if __name__ == "__main__":
    json.dump(spec, sys.stdout, indent=1, ensure_ascii=False)
    sys.stdout.write("\n")
