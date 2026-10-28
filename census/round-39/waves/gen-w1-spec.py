#!/usr/bin/env python3
"""Generate the r39 wave-1 spec: one v2 wave (72 seats) carrying build and attack items.

Usage: python3 gen-w1-spec.py > w1-spec.json   (run from the lane repo root)
"""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FREEZE = "b769bfb84a264d8b284c09bc211d99f39a3e9126"
BASE = "ed30b7f5b77939c9073348d810730bc4f355708d"
GODSPEED = (
    "/skill:godspeed\n\n"
    "You are a Godspeed-enabled subagent.\n\n"
    "1. **Name the axes.**\n"
    "2. **Iterate cheap, in parallel.**\n"
    "3. **Keep moves that improve any axis and harm none.**\n"
    "4. **Don't aim \u2014 let the frontier walk itself.**\n\n"
    "## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large "
    "batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or "
    "verbose plans. Act directly via tool calls.\n\n"
)

CONTEXT = f"""# Goal
souji round 39, wave 1 (hyaku run 11), one v2 wave. Lane repo: {LANE}.
souji is the fleet repository/workspace-hygiene shokunin; its axes are calibration, operability and
coverage. This round closes the 16 defects the round-38 non-author spot-check routed and the
limits the round-38 lesson named.

# Frozen contract
`{LANE}/census/round-39/preregistration.txt` (freeze commit {FREEZE}, lane base {BASE}) is the
claim contract. Read it first. Its claims:
C1 calibration 7 (lowest non-retired axis): 16 routed defects closed in lane bytes, one anchored
   line each (`census/round-39/c1-items.tsv`), plus a citation register whose rows include at least
   two with `commit != receipt_rev`; counter `census/round-39/c1-counter.py` must read
   `items=16 open=0 register_cells>=6 register_mismatches=0 commit_distinct>=2`.
C2 operability 8: `tools/souji-citation-reconcile.py` resolves `--rev`/`--register-rev` and refuses
   a non-commit revision with exit 2 (`REFUSAL REV-UNRESOLVED`); `tools/souji-worktree-drift.py`'s
   RECORD-MISSING/RECORD-MALFORMED docstring matches the classes it actually raises; fixture
   `tests/fixtures/r39-citation-rev.py` (8 cases) discriminates the base bytes; counter
   `census/round-39/c2-counter.py` must read `legs=6 pass=6 fail=0 harm=0`.
C3 coverage 8: four record-rule mutants (M11-M14) that every existing drift fixture leaves alive
   are killed by `tests/fixtures/r39-drift-record-rules.py`; counter
   `census/round-39/c3-counter.py` must read `mutants=4 killed=4 survived=0 pristine=ok
   base_killed=0`.
Control receipts measured before any after-data: `census/round-39/records/c1-before.txt`
(`open=16`), `c2-before.txt` (`pass=2 fail=4`), `c3-before.txt` (`killed=0 survived=4`).

# Hard rules
- Absolute paths only. Every tool starts in the fleet root, so a relative path lands in the wrong
  repo. Write every file under `{LANE}/...`.
- Every `Report:` trailer path is relative to {LANE} — write it at {LANE}/<that path>.
- Seats never commit, push, or run a mutating git or jj command anywhere (`git add`, `commit`,
  `stash`, `checkout`, `switch`, `reset`, `pull`, `push`, `jj <mutation>` are all forbidden). The L1
  lands bytes through the lane helper. Read-only git (`log`, `show`, `diff`, `status`, `rev-parse`,
  `merge-base --is-ancestor`, `cat-file`) is fine.
- Never write the fleet repo ({os.path.dirname(LANE)}), any sibling lane, `.ufo/state/`,
  `.ufo/watchdog.log`, `~/.omp/**`, `~/.config/**`, `templates/` or `scripts/` under the fleet root.
  Do not edit `census/round-39/preregistration.txt`, `census/round-39/*-items.tsv`,
  `census/round-39/*.json` specs, or any frozen receipt.
- Any git fixture is `D=$(mktemp -d) && git -C "$D" init -q`; name `-C "$D"` on every later git
  call; verify `git -C "$D" rev-parse --show-toplevel` equals `$D` before the first commit.
- Scratch: `mkdir -p /fast/scratch/hyaku/souji-r39/<your-seat-name>`, pass it explicitly
  (`TMPDIR=... --work ...`), `trap 'rm -rf -- "$S"' EXIT` or `finally: shutil.rmtree`, and report
  it if your tree is still on disk when you finish. `/tmp` is only for files under 50 MB. Never
  clone a whole lane repo; cite revisions and commands instead.
- Tooling authorization (operator 2026-10-19): you may install or upgrade a tool that helps your
  item — read `/home/vgpnk/.omp/agent/RULES.md` first (official channels only), record
  tool/version/channel/reason in your report. **pacman is paused host-wide**: install via
  `uv tool`, `npx`, or an official binary in `~/.local/bin`; never `pacman -S/-Sy/-Syu/-U/-R`.
- Your report is `{LANE}/.ufo/waves/round-39/w1/<YourSeatName>.md`: what you ran (exact command),
  the observed output lines, and an explicit verdict. An unrun check has not passed; do not
  fabricate evidence, numbers or verdicts. You are advisory: the L1 integrates.
"""


def item(name, role, axes, body):
    return {
        "name": name,
        "role": role,
        "axes": axes,
        "prompt": GODSPEED + "# Target\nsouji round 39 wave 1 item %s (role %s).\n# Task\n%s\n"
                  "# Acceptance\nYour report at %s/.ufo/waves/round-39/w1/%s.md names every command "
                  "you ran, quotes its output lines, and states a verdict per check.\n"
                  % (name, role, body.strip(), LANE, name),
    }


ITEMS = []


def add(name, role, axes, body):
    ITEMS.append(item(name, role, axes, body))


# ---------------------------------------------------------------- executors (20)
add("W1ExecC1Base", "executor", ["calibration"], f"""
Re-measure the C1 control on a clean checkout state and confirm the frozen control receipt.
Run from {LANE}:
  mkdir -p /fast/scratch/hyaku/souji-r39/W1ExecC1Base
  TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecC1Base python3 -B census/round-39/c1-counter.py --root . --rev {BASE} --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r39/W1ExecC1Base
Compare its SUMMARY line with `census/round-39/records/c1-before.txt` (must be `items=16 open=16`,
same `items_sha`). Then run the counter with the freeze revision `{FREEZE}` as `--rev` and report
the difference (the freeze only adds instruments, so items that name r38 files should still be
OPEN). List every item id that is OPEN at the freeze, by class.
""")

add("W1ExecC1Items", "executor", ["calibration"], f"""
Audit the 16 item predicates in `{LANE}/census/round-39/c1-items.tsv` for decidability.
For each row: does the named file exist at base `{BASE}` (git cat-file -e)? Does the anchor string
occur fewer than 1 time (expected at base) and is the anchor distinctive enough that no unrelated
line would satisfy it? Report, per row, the file, the exit of `git cat-file -e {BASE}:<file>`, and
whether the `must` tokens are individually satisfiable by the kind of line the round intends to
write. Flag any row whose `must` token set is ambiguous (e.g. a token that could appear on a line
about something else).
""")

add("W1ExecC2Repro", "executor", ["operability"], f"""
Reproduce the two C2 defects from committed bytes only, at base `{BASE}`.
  git -C {LANE} show {BASE}:tools/souji-citation-reconcile.py > /fast/scratch/hyaku/souji-r39/W1ExecC2Repro/new.py
For `--rev 0000000000000000000000000000000000000000` and for a blob id (`git rev-parse
{BASE}:corpus/SOURCES.md`) record the exit code and whether `REV-UNRESOLVED` appears. Also record
`--register-rev` unresolvable behaviour. For the drift tool, extract `{BASE}:tools/souji-worktree-drift.py`
and record the printed class for (a) a non-existent record path, (b) a `chmod 000` record file,
(c) a directory as record path. Tabulate rc + class per case.
""")

add("W1ExecC2Docstring", "executor", ["operability"], f"""
Derive the drift tool's documented class map with `ast` only and compare with behaviour.
  python3 - <<'EOF'  (ast.get_docstring(ast.parse(open(path).read()), clean=False); print each line
  that starts with RECORD-MISSING / RECORD-MALFORMED / RECORD-EMPTY)
Run against the base blob `git show {BASE}:tools/souji-worktree-drift.py` and against the current
worktree file. For each, print the two class lines verbatim and state whether the line starting with
the class the tool actually raises for a missing path contains the word "missing", and whether the
line for the class raised on EACCES names "EACCES". This is C2 L4's discriminator; report the base
gap precisely.
""")

add("W1ExecC3Baseline", "executor", ["coverage"], f"""
Measure whether any pre-round fixture kills the four C3 mutants.
Run `python3 -B census/round-39/c3-counter.py --root . --rev {BASE} --base-rev {BASE} --fixture
tests/fixtures/r38-drift-record.py --scratch /fast/scratch/hyaku/souji-r39/W1ExecC3Baseline` and
compare against `census/round-39/records/c3-before.txt`. Then run the same battery twice more with
`--fixture` set to `tests/fixtures/r36-worktree-drift.py` and `tests/fixtures/r37-drift-discrimination.py`
(the second needs `--base-fixture tests/fixtures/r38-drift-record.py` to keep the pristine arm sane;
if the fixture CLI has no matching cases the pristine arm will fail — report that as a defect of the
request, not a survivor). Report which mutants survive each existing fixture.
""")

add("W1ExecC3Fixture", "executor", ["coverage"], f"""
Exercise the new C3 fixture on its own.
Run `python3 -B tests/fixtures/r39-drift-record-rules.py --tool tools/souji-worktree-drift.py --work
/fast/scratch/hyaku/souji-r39/W1ExecC3Fixture` and report per-case PASS/FAIL and the SUMMARY. Then
run each case's record file content by hand against the tool to confirm the case is testing what its
name says (quote the record bytes and the tool's output). Flag any case that passes for the wrong
reason (e.g. refused earlier than the class under test).
""")

add("W1ExecSources", "executor", ["coverage"], f"""
Run the SOURCES census at both ends of this round.
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
now, and again after the wave if new rows exist. Report the registry row count
(`grep -cE '^\\|[[:space:]]*S[0-9]{3,}[[:space:]]*\\|' {LANE}/corpus/SOURCES.md`), the W04 warning
count, and the exit code. Compare with the round-38 spot-check's closing reading (`162 -> 170` rows,
47 W04) and state whether the lane's registry is unchanged since then.
""")

add("W1ExecReportGate", "executor", ["operability"], f"""
Put the round-39 report under the lane's own report-contract gate before it exists.
Read `tools/souji-report-contract.py` (its required sections, SHONEN rule, trend rule, stale-lane
line, measurement row, claim ids). Then run it on the filed r38 report
(`/home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md`) and on an empty scratch file, and
report both verdicts. Produce the exact checklist the r39 report must satisfy, including the
`grep -c '^## SHONEN'` value and one line per SHONEN.md box.
""")

add("W1ExecConsumers", "executor", ["operability"], f"""
Re-run every consumer fixture the round will harm-check, at the current worktree bytes, and record
counts: `tests/fixtures/r38-drift-record.py` (`--tool tools/souji-worktree-drift.py`),
`tests/fixtures/r36-worktree-drift.py`, `tests/fixtures/r38-drift-write-envelope.py`,
`tests/fixtures/r37-citation-reconcile.py`, `tests/fixtures/r38-citation-commit.py` (both `--tool
tools/souji-citation-reconcile.py`), and `bash tests/fixtures/r27-pre-report-gate.sh` (with
`TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecConsumers`). Report each SUMMARY line and any failure
with its detail line.
""")

add("W1ExecC1Anchors", "executor", ["calibration"], f"""
For each C1 item, count occurrences of its anchor across the WHOLE lane tree at base
(`git -C {LANE} grep -c -F <anchor> {BASE} -- .`), not only in the named file. A nonzero count in a
file other than the named one is a collision the counter cannot see. Report per item: named-file
hits at base (expected 0), other-file hits at base, and any item whose `must` tokens already appear
on some line of the named file at base (which would make the item vacuously closeable).
""")

add("W1ExecCapture", "executor", ["operability"], f"""
Validate the wave-evidence capture path the round needs for R4 (`.ufo/waves/` is git-ignored).
Read `tools/souji-wave-evidence-capture.sh` and its fixture, then run the capture into a scratch
target (never into the lane): `bash {LANE}/tools/souji-wave-evidence-capture.sh {LANE} 39 --out
/fast/scratch/hyaku/souji-r39/W1ExecCapture/capture` (adjust to the tool's real CLI; report the
usage banner if your guess is wrong) and report the CLI it actually accepts, the record count, and
whether `--verify` works over a revision. State whether round 38's waves (specs, dispatches,
results, seat reports) can be captured by the same command and how many records that would add.
""")

add("W1ExecPrereg", "executor", ["calibration"], f"""
Prove the r38 preregistration file can receive R8/R9 as APPENDED amendments without altering a
frozen sentence. Record `sha256sum` of the file at base and of its first 227 lines; then, in a
scratch copy (`cp` to /fast/scratch), append a two-line amendment and show that the prefix digest is
unchanged and that the appended bytes parse as plain text. Report the exact append shape you would
use (heading + A10/A11 text) and the file's last three lines, so the L1 can distinguish an append
from the in-place rewrite R9 describes.
""")

add("W1ExecRegistry", "executor", ["operability"], f"""
Build the R6 evidence: enumerate the gate-registry table in `{LANE}/SKILL.md` (rows after
`| name | kind | entry command |`) and report which of these are present or absent:
`r38-citation-commit`, `r38-drift-write-envelope`, `r38-drift-record`, `r38-drift-mutants`,
`r38-counter-arms`, plus the new `c1-counter`, `c2-counter`, `c3-counter`, `r39-citation-rev`,
`r39-drift-record-rules`. Give the exact grep commands and counts, and quote the two nearest existing
rows verbatim so the new rows can match the column shape.
""")

add("W1ExecStaleLiterals", "executor", ["calibration"], f"""
Gather the exact bytes behind R13. Print `{LANE}/LOG.md` lines 1855 and 1862 and
`{LANE}/corpus/QUALITY.md` line 209 with line numbers, and for each state which committed r37/r38
receipt (path + revision + its `SUMMARY` line) carries the value the line should have carried. If no
receipt carries it, say so. Then grep the whole lane at base for the tokens those lines quote
(`cases=9`, `pass=3`, `fail=6`, `escapes=9`) and report every other line that carries them, so the
correction block does not create a new stale literal.
""")

add("W1ExecCommitList", "executor", ["calibration"], f"""
Produce the R15 evidence from committed history. `git -C {LANE} log --format='%h %s' ca4369a..fcdecaa`
(the r38 round range) and, for each commit, list whether the r38 filed report
(`/home/vgpnk/Projects/shokunin git show <report commit>:.ufo/reports/round-38/souji.md`) names that
hash in its Landed-changes table. Report the nine commits the spot-check says are unnamed and the
report's own last-row placeholder. Do not edit any file.
""")

add("W1ExecRound36", "executor", ["calibration"], f"""
Establish R16's facts. Print `{LANE}/corpus/lessons/round-36.md` around line 23 with line numbers
(`sed -n '15,30p'`), then `git -C {LANE} log --format='%h %ad %s' --date=short -- corpus/lessons/round-36.md`
and `git -C {LANE} diff --numstat ca4369a fcdecaa -- corpus/lessons/round-36.md`. State whether the
line was rewritten in place, which commit wrote it, and the exact appended-correction shape that
would satisfy the r37 routed defect 4 without editing the frozen bytes.
""")

add("W1ExecScratch", "executor", ["operability"], f"""
Audit the new round-39 instruments for scratch discipline. For each of
`census/round-39/<c1|c2|c3>-counter.py`, `tests/fixtures/r39-citation-rev.py`,
`tests/fixtures/r39-drift-record-rules.py`: grep for `/tmp`, `mkdtemp`, `TMPDIR`, `--work`,
`shutil.rmtree`, and report whether every temporary root is caller-controlled, whether cleanup runs
on every exit path (including an exception before the try), and whether a `--scratch`/`--work`
argument is honoured. Flag any path that ignores the caller's scratch root.
""")

add("W1ExecExitMatrix", "executor", ["operability"], f"""
Build the exit-code matrix for `tools/souji-citation-reconcile.py` at base `{BASE}` over revision
shapes: 40-hex absent, blob id, tree id, tag name, 12-hex prefix, 40-hex commit, `HEAD`,
`refs/jj/keep/...`-only commit if one exists, plus `--register-rev` absent/valid. For each: rc,
stdout's first MISMATCH class and whether a SUMMARY line was printed. Then state which shapes a
"could-not-evaluate exit 2" contract must cover and which must stay exit 1 (findings) — the base tool
must not be able to print findings for a revision it never resolved.
""")

add("W1ExecDeadSeats", "executor", ["calibration"], f"""
Re-derive R2 from disk, not from the report. Count the seat reports in
`{LANE}/.ufo/waves/round-38/w1` and `w2`, list the seats named in
`{LANE}/.ufo/waves/round-38/w1-spec.json` and `w2-spec.json` that have no report, read
`{LANE}/.ufo/waves/round-38/w2-results.json` (seat count and per-seat status) and report the true
numbers: reports on disk per wave, seats per spec, seats settled per results file, and the number of
dead seats. State when `W2MutBattery.md` was written (mtime) relative to the r38 report commit's
author time, since the r38 filing predates it.
""")

# ---------------------------------------------------------------- reviewers (10)
add("W1RevC1Forge", "reviewer", ["calibration"], f"""
Attack C1's instrument by trying to forge a pass. Write a scratch copy of
`census/round-39/c1-items.tsv` in /fast/scratch with one row whose anchor already exists at base and
whose `must` tokens are satisfiable by an unrelated base line, run the counter at base with
`--items <scratch copy>`, and report whether that row closes without any round work. Then try the
hardest forgery: an author who writes a correction line that quotes the required tokens but names no
evidence and no commit. State whether the counter can detect it, and what the honest limit is.
Report under .ufo/waves/round-39/w1/W1RevC1Forge.md.
""")

add("W1RevC1Register", "reviewer", ["calibration"], f"""
Attack the C1 register leg. Read `census/round-39/c1-counter.py` (register_leg + parse_register) and
the frozen `tools/souji-citation-reconcile.py`. Construct, in scratch, register rows that (a) name a
`commit` that is an ancestor but where the receipt blob reads a different token, (b) name a
`receipt_rev` that is not an ancestor, (c) carry `commit == receipt_rev` so `commit_distinct` stays
below 2, and report which of them the counter refuses and how. Then state precisely what
`commit_distinct>=2` proves and what it does not prove.
""")

add("W1RevC2Legs", "reviewer", ["operability"], f"""
Attack C2's six legs. For each leg in `census/round-39/c2-counter.py`, find the cheapest way a wrong
implementation satisfies it: e.g. a tool that returns exit 2 for EVERY input satisfies L1/L2 but
must lose L3/L5/L6; a tool that prints REV-UNRESOLVED to stderr while still exiting 1 satisfies what?
Report leg by leg the discriminating property and any leg that a stub could satisfy. Propose one
extra case (not a new claim) that would close the widest gap, and say why it is not a claim change.
""")

add("W1RevC2Doc", "reviewer", ["operability"], f"""
Attack C2 L4 (the docstring → behaviour mapping). Show that a docstring can name both triggers and
still be wrong: write a scratch drift-tool copy whose RECORD-MALFORMED line says "missing path" but
whose code raises RECORD-MISSING for a missing path, and report whether L4's rule catches it. Then
state the honest limit of a token-presence docstring check (r38 M5) for the two class lines and
whether the round should disclose it instead of widening the rule.
""")

add("W1RevC2Harm", "reviewer", ["operability"], f"""
Attack C2 L6 (harm). Read the consumer list in `census/round-39/c2-counter.py` and the five fixtures.
Find a regression the leg would miss: a change that keeps every fixture's pass count but breaks a
documented behaviour (e.g. a looser exit contract on a shape no fixture exercises), or a fixture whose
pass count can rise while a case changes meaning. Report concrete candidates with commands and
outputs; say which are in scope for r39 and which are named limits for r40.
""")

add("W1RevC3Battery", "reviewer", ["coverage"], f"""
Attack C3's battery. Read `census/round-39/c3-counter.py` and `tests/fixtures/r39-drift-record-rules.py`.
Check: are the four mutant anchors unique in the base tool (count exactly once)? Does each mutant
change exactly one documented behaviour? Could a mutant die for the wrong reason (an unrelated case
failing)? Independently re-apply each mutant by hand in scratch and score it with both fixtures,
reporting rc and the failing case names for the candidate fixture. Flag any mutant whose kill is not
attributable to the case that names it.
""")

add("W1RevC3Fixture", "reviewer", ["coverage"], f"""
Attack the new fixture's case independence. For each case, delete every other case in a scratch copy
and run the reduced fixture against (a) the pristine tool and (b) the mutant the case is supposed to
kill. Report a matrix: case x (pristine, its mutant). A case that passes under its own mutant, or
whose kill needs another case, is a finding. Also check the fixture's control arm: case `good` must
fail if the tool is replaced by a stub that always exits 0 or always exits 2.
""")

add("W1RevSeparability", "reviewer", ["calibration"], f"""
Test claim separability. For each pair of claims, state the command that verifies claim X while claim
Y's work is absent, and run it: C1's counter at the freeze (C2/C3 unimplemented) — what does it read?
C2's counter with the C1 corrections absent — does it depend on any r39 lesson/SCORECARD text? C3's
battery with C2's tool fix absent — does the docstring change affect a mutant? Report any coupling
you find with the exact line.
""")

add("W1RevFreeze", "reviewer", ["calibration"], f"""
Compare the frozen prereg against the instruments. For each frozen predicate in
`census/round-39/preregistration.txt`, quote the clause and the code line in the counter or fixture
that implements it, and flag every divergence (a predicate clause with no code, or a code check with
no clause). Also verify the three control receipts in `census/round-39/records/` reproduce exactly at
`{BASE}` and that their SUMMARY parsers match the counter's output format.
""")

add("W1RevScope", "reviewer", ["adjacency"], f"""
Audit write scope for the round so far. `git -C {LANE} status --porcelain` and
`git -C {LANE} log --format='%h %an %s' {BASE}..HEAD`, plus `git -C /home/vgpnk/Projects/shokunin
status --porcelain` for fleet-root strays naming souji/round-39. Report every path outside the
round's write scope (lane repo, the r39 report, `.ufo/l0-questions.md`), and every file under
`.ufo/waves/round-39` that is untracked because of the ignore rule (R4) so the capture step covers it.
""")

# ---------------------------------------------------------------- critics (8)
add("W1CritC1Axis", "critic", ["calibration"], f"""
Criticize C1's axis attribution. Is closing 16 routed self-assessment defects calibration (mismatches
between the lane's self-assessment and observed repo state) or is it quality/bookkeeping? Apply the
r25 axis-attribution lesson and AXES.md's definition. Name the surface the round changes and the
counter that would show it unmoved if the work were skipped. If the attribution is wrong, say what
the honest verdict line should be; do not rewrite the frozen predicate.
""")

add("W1CritC3Axis", "critic", ["coverage"], f"""
Criticize C3's axis and magnitude. The claim is a mutation-coverage move on the drift tool's record
parser. Determine the marginal coverage: which documented behaviours are newly asserted, which were
already asserted by r36/r37/r38 fixtures (run them), and whether the four mutants are distinct
classes or variants of one. Report the exact marginal class count and whether the claim's wording
("four record-rule mutants ... every existing drift fixture leaves alive") is supported.
""")

add("W1CritSizing", "critic", ["calibration"], f"""
Criticize claim sizing against addendum section 9. For each claim, state the after-state as one
concrete value, the single command that re-derives it, and whether a do-nothing control can reach it.
Specifically test: can C1's `open=0` be reached by writing 16 lines of prose that quote tokens but
change nothing? can C2's `pass=6` be reached by a tool that always exits 2? can C3's `killed=4` be
reached by a fixture that always fails? Report each with the executed control you built.
""")

add("W1CritDisclosure", "critic", ["calibration"], f"""
Criticize what the claims should disclose. Read the three counters and list every limit their
measurement carries: instruments read from the worktree rather than the audited revision, author-
chosen anchors, the `commit_distinct` floor, mutant selection bias, fixture case count as a floor.
For each, say whether the round can close it or must disclose it in the report's named limits. Produce
the disclosure list the report must carry, with the receipt/line that proves each.
""")

add("W1CritSources", "critic", ["coverage"], f"""
Criticize the sources plan for section 2b. Read `corpus/README.md` (frontier map),
`corpus/QUALITY.md` and the r38 Gate block. The round needs at least one claim resting on a SOURCES
row opened THIS round. Name the three candidate pages (gitrevisions(7) `^<commit>` peeling, Python
`ast.get_docstring`, Python `argparse` exit status) and for each state: which claim it would ground,
whether the page actually states the fact (check the installed docs or the canonical URL), and
whether it duplicates an existing row's scope. Report an admit/reject recommendation per candidate
with the ≤25-word quote you located.
""")

add("W1CritReport", "critic", ["calibration"], f"""
Criticize the report plan. Read the r38 filed report and the r38 spot-check's 16 routed defects, then
list which of them the r39 report must state explicitly to avoid repeating them (R1 numbers, R2 dead
seats, R3 filing order, R4 capture, R5 prompt commit, R15 landed-changes coverage). Produce a
per-section checklist the L1 can execute, and name the two sections the marker rule does not require
but the contract does.
""")

add("W1CritWave", "critic", ["calibration"], f"""
Criticize the wave shape. Read `{LANE}/.ufo/waves/round-39/w1-spec.json` when it exists (or the
generator `gen-w1-spec.py`): count seats, roles, attack share (reviewer+critic+mutation-tester+
sentinel+revenger), and check the addendum's rules — 64-128 band, >= 25 % attack, planner mask,
few connector seats, one batched wave, distinct prompts. Also check that no item asks a seat to write
a lane file the L1 must integrate and that every item names absolute paths. Report violations with
item names.
""")

add("W1CritAssimilation", "critic", ["coverage"], f"""
Criticize the assimilation decision for this round. Read `/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md`
and the staged entries under `merge/souji/knowledge/` (read-only; never write there). State whether
any staged entry serves one of the three frozen claims (citation auditing, tool output envelope,
record-parser coverage). If none does, draft the one report line that says `Assimilation: none` with
its reason; if one does, name the entry, the claim it serves, and the re-grounding steps §10 requires.
""")

# ---------------------------------------------------------------- mutation-testers (5)
add("W1MutC1", "mutation-tester", ["calibration"], f"""
Mutate `census/round-39/c1-counter.py` and score the control. In scratch copies, apply: (1) drop the
`mustnot` check, (2) accept a row when ANY hit line satisfies a subset of `must`, (3) treat a missing
file as CLOSED, (4) hard-code `open=0`. For each mutant, run it at base `{BASE}` and report whether
the control receipt still reads `open=16`. A mutant the control cannot distinguish is a defect of the
control. Report mutant x (control reading) x verdict.
""")

add("W1MutC2", "mutation-tester", ["operability"], f"""
Mutate `census/round-39/c2-counter.py` and score its legs. Apply: (1) L1 passes when new rc==2 only
(drop the class check), (2) L5 passes when the base arm fails 0 cases, (3) L6's harm check removed,
(4) L4's token check made case-insensitive on the class name. Run each mutant at base `{BASE}` with
`--rev {BASE}` and report which legs change verdict. Then state, per leg, the property a correct
implementation must hold that the mutant does not.
""")

add("W1MutC3", "mutation-tester", ["coverage"], f"""
Mutate the C3 battery's kill rule and score it. Apply: (1) a kill needs only rc==1, (2) a kill
accepts a traceback, (3) `base_killed` is not computed, (4) the pristine arm is skipped. Run each
against the pristine tool and the four mutants at base `{BASE}`, and report which mutants become
falsely killed or which control line changes. Report whether the packaged battery would notice each
mutation with its own output.
""")

add("W1MutFixture", "mutation-tester", ["coverage"], f"""
Mutate the new fixture to prove the battery depends on its cases. In scratch copies of
`tests/fixtures/r39-drift-record-rules.py`: delete (1) the trailing-space case, (2) the crlf case,
(3) the outside-root case, (4) the indented-comment case. Run `census/round-39/c3-counter.py` with
`--fixture <mutated copy>` and report which mutant stops being killed. A case deletion that changes no
kill is a case with no discriminating power.
""")

add("W1MutDriftRules", "mutation-tester", ["coverage"], f"""
Hunt for record-parser behaviours the round's four mutants miss. Read
`tools/souji-worktree-drift.py::parse_record` and list every branch. For each branch not covered by
M11-M14 or the r38 battery, write a single-defect mutant in scratch and score it against the new
fixture and against the r38 fixture. Report the survivors with the class they represent, so the round
can name them as limits for r40 (do not widen C3).
""")

# ---------------------------------------------------------------- scouts (8)
add("W1ScoutRouted", "scout", ["calibration"], f"""
Turn `{LANE}/corpus/lessons/round-38-verifier-spotcheck.md` into a fact sheet the L1 can execute
against. For each of R1-R16, quote the spot-check's exact claim, name the file(s) it accuses, the
command that demonstrates it, and whether the fix is lane bytes (this round) or fleet bytes (errata
only). Mark which routed defects the r39 prereg's 16 items map to, and which routed defects have no
item — that gap is a finding.
""")

add("W1ScoutLaneFiles", "scout", ["calibration"], f"""
Map the lane files the 16 C1 items will touch. For each item's file, report: exists at base?, line
count at base, last commit touching it, whether it is append-only by the lane's own rules
(SCORECARD/LOG/SOURCES/lessons), and any gate that reads it (e.g. the landing gate, the capability
counter, the report-contract gate). Flag files where an append could break a frozen pin or a gate's
expected digest.
""")

add("W1ScoutReportGate", "scout", ["calibration"], f"""
Reconnaissance of `tools/souji-report-contract.py`. Enumerate its predicates, exit codes, and the
exact shape it expects for each required section (including the SHONEN line rule, the trend-verdict
line rule and the measurement-row rule). Then report which r38 report lines satisfied and which
missed each predicate, with `grep -n` evidence. Deliver a violation table the r39 report can be
checked against before filing.
""")

add("W1ScoutCapture", "scout", ["operability"], f"""
Reconnaissance of the wave-evidence capture tooling and the `.ufo` ignore rules. Report: what
`.gitignore` entries hide `.ufo/waves/`, what `tools/souji-wave-evidence-capture.sh` accepts and
writes (read its usage and fixture), how `census/round-29/waves` and `census/round-26/waves` were
captured, and the exact command that would capture round 39's wave dir with a verifiable record at a
revision. Name the files that must exist before capture (spec, dispatch, results, seat reports).
""")

add("W1ScoutOverlap", "scout", ["adjacency"], f"""
Sibling-overlap scan for the three claims. Search the fleet's sibling lanes read-only
(`/home/vgpnk/Projects/shokunin/*-shokunin/`, `grep -rl` on the tool/fixture names and on
`citation`, `record-parse`, `mutation battery`) for any sibling that already binds (a) revision
resolution for a citation counter, (b) a record-file parser with a documented class map, (c) a mutant
battery over a parser. For each hit, report the path, the entry point and whether the surface is
contested or merely adjacent. Do not write in any sibling lane.
""")

add("W1ScoutGitRev", "scout", ["coverage"], f"""
Open the gitrevisions(7) page on this host (`MANWIDTH=100 man 7 gitrevisions`, git 2.56.0) and locate
the `<rev>^<type>` peeling rule. Report: the section heading and line numbers, the ≤25-word quote
that states `<rev>^<commit>` requires the object to be a commit, the canonical URL with anchor, and
the access date. State exactly which r39 claim the fact grounds (C2's `--rev` resolution) and why the
existing git-merge-base rows (S239/S244) do not already cover it.
""")

add("W1ScoutAst", "scout", ["coverage"], f"""
Open the Python documentation for `ast.get_docstring` on this host (python3 -c
"import ast,inspect;print(ast.get_docstring.__doc__)" plus the docs page at docs.python.org for the
installed version). Report: the documented signature, whether it returns None when there is no
docstring, whether `clean` affects behaviour, the ≤25-word located quote, the URL and the access
date. State which r39 fact it grounds (the L4 docstring read is ast-only, not source slicing) and
whether it duplicates an existing SOURCES row's scope (check the registry).
""")

add("W1ScoutArgparse", "scout", ["coverage"], f"""
Establish the `argparse` usage-error exit status for the installed Python (3.14) from the library
reference page and from an executed probe: `python3 -c 'import argparse;ap=argparse.ArgumentParser();
ap.add_argument("--x",required=True);ap.parse_args([])'`. Report the exit status, the stream it
writes to, the ≤25-word located quote from the docs page (URL + access date), and whether an existing
SOURCES row covers argparse scope. State which r39 fact it grounds (C2's declared exit map includes
argparse's own exit 2) and whether the claim needs it or only discloses it.
""")

# ---------------------------------------------------------------- scribes (10)
add("W1ScribeR38Block", "scribe", ["calibration"], f"""
Draft the appended correction block for `{LANE}/corpus/lessons/round-38.md` covering routed defects
R1, R2 and R14. Requirements: three single lines anchored exactly `R39-C1-01`, `R39-C1-02` and
`R39-C1-14`; line 01 must carry the tokens `S246`, `SOURCES-rows=170`, `SOURCES-added=8`, `W04=47`
and name S244-S246; line 02 must carry `w1-reports=42/42`, `w2-reports=32/32`, `W2MutBattery`,
`dead=0`, `settled-after-closure` (W2MutBattery settled at 14:39, after the r38 report commit);
line 14 must carry `vacuity-operation=mismatches=3` and `three-rows` and state that a faithful
one-row substitution reads `mismatches=3` because `escapes=9` appears on three rows. Write the block
as markdown to your report file plus a ready-to-append snippet; state where in the file it belongs
(append-only, after the last block).
""")

add("W1ScribeGate", "scribe", ["coverage"], f"""
Draft the round-39 lesson `## Gate` table rows from the three source scouts (gitrevisions, ast,
argparse). For each candidate: id placeholder, source URL, access date 2026-10-28, the ≤25-word
located quote with section + line numbers, verdict (admit/reject) and the claim it grounds. Check
against `{LANE}/corpus/SOURCES.md`'s existing rows for duplicate URLs/scope and against
`corpus/QUALITY.md`'s admission bar. Deliver the rows plus the census consequence (row count
170 -> 170+k). Do not write into `corpus/SOURCES.md`; the L1 appends.
""")

add("W1ScribeMistake", "scribe", ["calibration"], f"""
Mine one mistake for `corpus/lessons/round-39.md` `## Mistakes`, in the lane's four-field shape
(class · evidence pointer · captured-by · fix). Candidate material: (a) the c2-counter's first
control run printed `rc=2 class=False` for L1/L2 because the fixture passed an unresolvable
`--register-rev`, masking the rev arm — a control that could not fail; (b) the r38 wave-2 seat
settling after closure changed a frozen-looking count (31/32 -> 32/32). Choose the one whose fix you
can show was able to fail, write the entry, and state the sweeping command that found it.
""")

add("W1ScribeReport", "scribe", ["calibration"], f"""
Draft the shape (not the numbers) of `{LANE}/../.ufo/reports/round-39/souji.md`: the six required
sections in order, one sentence of instruction per section, the SHONEN block with one line per
SHONEN.md box, the trend-verdict line format, the stale-lane line, and the errata section for the
r38 report's fleet-side halves of R2 and R15. Include the `grep -c '^## SHONEN'` check and the
report-contract gate command. Do not invent measurements.
""")

add("W1ScribeR36", "scribe", ["calibration"], f"""
Draft the appended correction for `{LANE}/corpus/lessons/round-36.md` (R16 / r37 routed defect 4).
It must be append-only, anchored exactly `R39-C1-16`, and carry the tokens `in-place`, `correction`,
`line-23`, naming the sentence that was rewritten in place, the commit that wrote it, and the rule it
violated (PROTOCOL: append-only corrections). Ask the W1ExecRound36 facts if the item is still
running; otherwise derive them yourself with read-only git. Deliver the exact markdown block.
""")

add("W1ScribeStale", "scribe", ["calibration"], f"""
Draft three appended correction lines anchored `R39-C1-11` (LOG.md), `R39-C1-12` (LOG.md) and
`R39-C1-13` (corpus/QUALITY.md). Line 11 must carry `LOG-line-1855`, `cases=9`, `fail=6`; line 12
`LOG-line-1862`; line 13 must carry `QUALITY-line-209` and `escapes=9`. Each line states the value
the line should have carried, the receipt that carries it (path + revision + its SUMMARY line), and
why the original value was wrong. Verify the receipt text yourself before quoting it.
""")

add("W1ScribeRegistry", "scribe", ["operability"], f"""
Draft the SKILL.md gate-registry rows for the round: `c1-counter`, `c2-counter`, `c3-counter`,
`r39-citation-rev`, `r39-drift-record-rules`, plus the four r38 rows the spot-check found missing
(R6). Match the existing table columns exactly (name, kind, entry command, verdict map, self-test
command, pinned-value path, write scope, owner) and choose kind honestly (a counter that can print a
reading but whose write can fail is a `gate` only if it can fail; say which rows are `probe` and why).
Also draft the one-line `R39-C1-06` reconciliation line naming all four r38 counters.
""")

add("W1ScribeScorecard", "scribe", ["calibration"], f"""
Draft the SCORECARD.md additions: (a) the appended `R39-C1-10` line naming `fcdecaa` as the measured
revision of the r38 finality blocks (`measured-revision` token required); (b) the Round 39
measurements table (claim · axis · before · after · counting command · measured commit) with
placeholders the L1 fills from receipts; (c) the capability rows for the three counters and the two
fixtures. Keep the lane's append-only convention; do not edit earlier blocks.
""")

add("W1ScribeRoutedTable", "scribe", ["calibration"], f"""
Draft a routed-defect disposition table for the round-39 lesson: one row per R1-R16 with id, the
spot-check's claim in ≤15 words, the lane artifact that closes it, the C1 item id (or `errata` for
fleet bytes), and the verification command. Mark R3/R10/R11 explicitly (conduct/contract defects).
Deliver the markdown table; do not claim closure the receipts do not show.
""")

add("W1ScribeBeforeAfter", "scribe", ["calibration"], f"""
Draft the report's `## Before -> after measurements` section template from the three control receipts
(`census/round-39/records/<c1|c2|c3>-before.txt`) and the prereg's frozen predicates: one bullet per
claim with the exact command, the before literal, and a placeholder for the after literal + measured
commit. State the counting command verbatim (byte-exact, copy-pasteable) and flag any command whose
scratch argument would make it non-reproducible.
""")

# ---------------------------------------------------------------- connectors (4)
add("W1ConnOverlap", "connector", ["adjacency"], f"""
Cross-claim pattern scan: which surfaces do the three claims SHARE? Determine for each pair
(C1/C2, C1/C3, C2/C3) whether a byte touched by one claim is read by another claim's counter, and
report the exact file+line. A shared byte is coupling that breaks separability; a shared *instrument*
(citation tool bytes) is coupling of evidence. Report both, with commands, and recommend which the
report must disclose.
""")

add("W1ConnCoverage", "connector", ["coverage"], f"""
Map mutation coverage across the lane's drift fixtures. For each of M7-M10 (r38) and M11-M14 (r39),
report which fixture cases kill it: `r36-worktree-drift.py`, `r37-drift-discrimination.py`,
`r38-drift-record.py`, `r39-drift-record-rules.py`. Build the killer matrix by running each mutant
against each fixture in scratch. Report the marginal contribution of the new fixture and any mutant
killed by more than one (redundant) or by none (gap).
""")

add("W1ConnDuplicates", "connector", ["calibration"], f"""
Cross-check the new correction lines against the lane's existing correction blocks. Search
`SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md` and `corpus/lessons/round-<36|38|39>.md` for existing
corrections of the same cells (e.g. r34's E04/E18 blocks, r37's receipt reconciliation, r38's
R38-C1-* rows). Report a duplicate-correction table: new id x existing correction x whether the new
line adds a commit binding, a corrected value, or nothing. Name any new line that would duplicate an
existing one.
""")

add("W1ConnSources", "connector", ["coverage"], f"""
Registry adjacency for the three candidate sources. For each (gitrevisions `^<commit>`, ast
`get_docstring`, argparse exit status) find every existing SOURCES row whose URL shares host/path
family, quote its scope cell, and state whether the new fact is inside or outside that row's scope.
Report the W04 warning consequence (duplicate URL across scopes is allowed) and the row count delta
the census will print. Deliver a table the Gate block can cite.
""")

# ---------------------------------------------------------------- simplifiers (4)
add("W1SimpC1", "simplifier", ["operability"], f"""
YAGNI review of `census/round-39/c1-counter.py`: identify dead code, duplicate git invocations,
unused imports/parameters, and any branch no frozen predicate needs. Propose deletions that change no
reading (verify by running the counter at base before and after in scratch — `open=16` must hold,
`items_sha` unchanged). Deliver a patch sketch with the exact lines and the before/after SUMMARY.
""")

add("W1SimpC2", "simplifier", ["operability"], f"""
YAGNI review of `census/round-39/c2-counter.py`: the `lane_root_of` helper, the `harm` counter's two
increment sites, the `extract`/`run_fixture` duplication across fixtures, and the unused
`classify` classes. Propose the smallest equivalent form; verify by running at base and confirming
`legs=6 pass=2 fail=4 harm=0` is unchanged. Report any simplification that would change a leg's
verdict and must be refused.
""")

add("W1SimpC3", "simplifier", ["operability"], f"""
YAGNI review of `census/round-39/c3-counter.py` and the battery's overlap with
`tests/fixtures/r38-drift-mutants.py`. Could the r39 battery be a parameterised call to the r38
battery (mutant list argument) instead of a second script? Report what the r38 battery would need
(one option) and what would be lost (kill-rule provenance, per-mutant base arm). Recommend one option
with the reading it preserves: at base, `killed=0 survived=4` with the r38 fixture.
""")

add("W1SimpFixtures", "simplifier", ["operability"], f"""
YAGNI review of the two new fixtures. List duplicated helpers (`sh`, `make_repo`, `ENV`,
record-case runner) and say which duplication is deliberate isolation (fixtures must not import each
other) versus removable. Check for cases that assert the same behaviour twice (e.g. two schema-refusal
cases whose records differ only in whitespace) and report whether deleting one loses a mutant kill.
Verify any proposed deletion against the battery reading.
""")

# ---------------------------------------------------------------- sentinel (1)
add("W1SentInstruments", "sentinel", ["adjacency"], f"""
Security review of the new instruments. For `census/round-39/*.py` and `tests/fixtures/r39-*.py`
check: (1) child git environment is a whitelist with config discovery neutralised; (2) no
symlink-following read of a register/record/FIFO that could hang or escape `--root`; (3) no write
into the measured tree or the lane; (4) no secret-shaped argv recorded in a receipt; (5) every
scratch root honours the caller. Reproduce at least one escape or hang attempt per class in scratch,
report the observed behaviour, and state whether the r38 A4/A7 envelopes are preserved by the new
code paths.
""")

# ---------------------------------------------------------------- revengers (2)
add("W1RevHistory", "revenger", ["calibration"], f"""
Reverse-engineer why the r38 spot-check's defect classes recur across rounds. From committed history
(`git log --oneline ca4369a~40..HEAD -- SCORECARD.md LOG.md corpus/lessons/`), find the earlier
routing of the same classes: (a) a stated completion with an unevidenced count (R2/R15), (b) a
prereg file edited in place (R9), (c) a receipt naming a non-durable path (R7). For each, report when
it was first routed, what fix was attempted, and why the fix did not generalise — quote the old
correction line. Deliver the intent statement the r39 lesson can cite.
""")

add("W1RevExitContract", "revenger", ["operability"], f"""
Reverse-engineer the citation tool's intended exit contract from its own artefacts: the module
docstring, `SKILL.md`'s registry row, the r37/r38 prereg predicates, the fixtures' expectations, and
the r38 spot-check's R11 wording. Report every statement of the contract with file:line, resolve the
conflicts (which statement is authoritative and why), and state the minimal code change that makes
all of them true without relaxing a fixture. Do not modify the tool.
""")

SPEC = {
    "wave": "souji-r39-w1",
    "milestone": "souji round 39 wave 1: verify and first-falsify the frozen C1/C2/C3 contract",
    "reportDir": ".ufo/waves/round-39/w1",
    "context": CONTEXT,
    "items": ITEMS,
}

if __name__ == "__main__":
    print(json.dumps(SPEC, indent=1))
