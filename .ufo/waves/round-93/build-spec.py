#!/usr/bin/env python3
"""Build the souji r93 wave-1 spec. Run: python3 .ufo/waves/round-93/build-spec.py > .ufo/waves/round-93/w1-spec.json
P1, P2, F and A hashes are read from the lane's git branch."""
import json
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "91c9bcb1041b18be154ca466ac3c047ac7862fe1"
W = f"{LANE}/.ufo/waves/round-93/w1"
SCR = "/fast/scratch/hyaku/souji-r93"

GOD = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

"""


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], stdout=subprocess.PIPE, text=True,
                          check=True).stdout.strip()


log = git("log", "--format=%H %s", "-12", "master").splitlines()


def find(prefix):
    for line in log:
        h, _, s = line.partition(" ")
        if s.startswith(prefix):
            return h
    raise SystemExit(f"commit '{prefix}' not found")


P1 = find("round-93: instruments")
P2 = find("round-93: controls")
F = find("round-93: preregistration")
A = find("round-93: after receipts")

C1_AFTER = ("python3 -B census/round-93/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py "
            "--harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv "
            f"--lane . --fleet-root {FLEET} --work <empty> --jobs 2 --ids census/round-93/c1-targets.json")
C1_PRISTINE = ("python3 -B census/round-93/c1-false-row-harness.py --counter census/round-87/c1-pointer-counter.py "
               f"--lane . --fleet-root {FLEET} --work <empty> --population census/round-93/c1-false-rows.tsv")
C2_PROBE = ("python3 -B census/round-93/c2-forgery-probe.py --fixture tests/fixtures/r93-k4-flagfail.py --tool "
            "tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>")
C2_FIX = ("python3 -B tests/fixtures/r93-k4-flagfail.py --tool tools/souji-record-agreement.py --before "
          "census/round-92/controls/c2-before-tool.py --work <empty>")

CTX = f"""# Goal
souji round 93 (lane repo {LANE}, lane id souji). The L1 (SoujiR93) holds the planner seat and is the ONLY
integration owner: it froze the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 13 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion. All commands below run
with cwd {LANE} (use `cd {LANE} && ...`); every path is relative to {LANE} unless absolute.

# Frozen round (read {LANE}/census/round-93/preregistration.txt FIRST — it is the contract)
Lane base {BASE} (r92 closed; its non-author spot-check is corpus/lessons/round-92-verifier-spotcheck.md). P1 {P1}:
instruments (r93 harness + population with LD5/LD6, the r93 survivor search, C1 targets and the written prediction
census/round-93/c1-prediction.txt, the r93 fixture with KFF19/KFF20, the 8-forgery probe, the S356 capture, the S356
row and the knowledge entry corpus/knowledge/utf8-cut-position-reference.md). P2 {P2}: controls. F {F}: the
preregistration alone. A {A}: after receipts (census/round-93/records/). The filed instruments are FROZEN: do not
modify census/, tests/fixtures/, tools/ or corpus/ — copy what you need into your seat dir or scratch and write
receipts in your seat dir. Nothing in the claim wording may be widened by this wave; the wave's job is to FALSIFY it
(Amendment 59: a claim verifies only if no artifact produced by this round's own wave falsifies its STATED WORDING;
numbers re-deriving is necessary, not sufficient).

Claims (read the prereg for the full predicate, kill rule and stated limits):
- C1 calibration 7: two counter edits survive every r92 row because no r92 run reaches their clause:
  h-ok-admits-one (counter line 552 `resolved == len(pop)` -> `resolved >= len(pop) - 1`) and a491c22-<-to-<= (the
  `_ledger` width guard `len(r) < 3` -> `len(r) <= 3`). Two appended rows of two NEW harness row types bind both:
  LD5 (where=ledger-drop: P04's own row removed from the frozen r77 ledger in scratch; asserts UNRESOLVED, exit 1)
  and LD6 (where=ledger-trim: P04's row cut to three columns; asserts MOVED, exit 0). Population
  census/round-93/c1-false-rows.tsv (66 rows = r92 64 byte-for-byte + comment + LD5 + LD6). The r93 kill rule: killed
  only on harness exit 1 with >= 1 `ROW ... match=no`; exit 2 or match=error-only is `errored`. Predicate: `{C1_AFTER}`
  prints `SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0 scored=2 errored=0 killed=2 survived=0` EXIT 0;
  pristine `{C1_PRISTINE}` prints `SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=0`, LD5 `rc=1
  match=yes`, LD6 `rc=0 match=yes`, EXIT 0. Control (r92 population): killed=0 survived=2. ONE harness run clones the
  lane fixture (~0.7 GB) and takes ~15 s; the search deletes each per-mutant tree once scored. Use --jobs 4 at most.
- C2 coverage 8: the r92 fixture checks only prefix/suffix faithfulness, so three one-edit forgeries of the filed
  tool (F5 `surrogatepass`, F6 `len(...) >= 1`, F7 head cut moved forward; R92MutC2) pass it 20/20. The r93 fixture
  (22 cases) adds KFF19 (the excerpt must EQUAL the cell built from an independent reference cut written from the
  WHATWG UTF-8 decoder, S356 §8.1.1, on a 14,586-payload boundary-class sweep) and KFF20 (an overlong E0 80 80 across
  the HEAD cut). The tool is unchanged. Predicate: `{C2_PROBE}` prints `FORGERY-SUMMARY forgeries=8 rejected=8
  positive=pass` EXIT 0 and `{C2_FIX}` prints `SUMMARY cases=22 tool_pass=22 before_pass=16` EXIT 0. Control: the
  probe with `--fixture tests/fixtures/r92-k4-flagfail.py` prints `rejected=5` EXIT 1.

# Evidence durability and the pre-file ledger (Amendment 59)
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every argument, output line and falsifying reproducer you want the ledger to read must live under {W}/ (your seat
dir {W}/<your name>/ or your report). If an artifact of yours falsifies a sentence of either claim, say so plainly
in the report under a heading `FALSIFIES-WORDING` (or `FALSIFIES-NUMBER`) with the exact sentence and the
reproducer path; the L1 records it as an amendment in plans/round-93.md, never silently. If nothing falsifies, say
`NO-FALSIFICATION` with what you tried. Every `Report:` trailer path is relative to {LANE} — write it at
{LANE}/<that path>. NEVER write anything under {FLEET}/.ufo/ or anywhere else in the fleet root (r92 lesson M5: a seat
report landed in the fleet root); use absolute paths under {W}/ for every file you write.

# Write scope and scratch
Write only under your own seat dir {W}/<your name>/ and your own report file. Read the lane read-only. Scratch
(clones, fixtures, counter --work dirs) lives under {SCR}/<your name>/; create it with mkdir -p and DELETE it before
you yield (trap 'rm -rf -- \"$S\"' EXIT in shell, finally: shutil.rmtree in Python), copying receipts (text only,
never clones) into your seat dir first. Keep your scratch under 20 GB: never hold more than 4 harness work trees at
once. /tmp is for files under 50 MB only and is never citable evidence. Any git fixture is `D=$(mktemp -d -p
{SCR}/<your name>)` + `git -C \"$D\" init -q`, every later call names `-C \"$D\"`, and you assert `git -C \"$D\"
rev-parse --show-toplevel` equals `$D` before the first commit; never pass an empty or unchecked variable to `git -C`
(it falls back to the fleet root, r70 incident). Do not run mutating git/jj anywhere else. Never mutate host sysctls,
never sudo, never spin CPU burners.

# Tooling authorization (operator, 2026-10-19)
You may install or upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels,
update-safety gate; record tool/version/channel/reason in your report). pacman transactions are PAUSED host-wide
until the operator resolves the host-recovery L0 question: install via `uv tool`/`npx`/an official binary in
~/.local/bin, or file an L0 question; before any future pacman -S run `pacman -Sp --print-format '%n %v' <pkgs>` and
never -Sy/-Syu/-U/-R. No tool install is needed for this round.

# Round shape
One v1 wave, 13 seats (policy band 8-16): 3 executor, 2 reviewer, 1 critic, 3 mutation-tester, 1 sentinel,
1 connector, 1 scout, 1 scribe. The prereg's planned `labrat` seat (R93Labrat) runs as a mutation-tester: the wave
validator rejects `labrat` as a swarm role (plans/round-93.md A0.1). Attack seats under the addendum's four-role
definition (reviewer, critic, mutation-tester, labrat): 6/13 = 46 %. Residual calls: none. The L1 holds the canonical
planner seat (the validator rejects `planner`); the bounded planning data-walk rides the connector seat.
"""


def seat(name, role, target, change, accept):
    body = f"# Target\n{target}\n\n# Change\n{change}\n\n# Acceptance\n{accept}\n\n"
    body = body.replace("{BASE}", BASE).replace("{FLEET}", FLEET).replace("{LANE}", LANE)
    return {"name": name, "role": role,
            "prompt": GOD + body + f"Report: .ufo/waves/round-93/w1/{name}.md\n"}


def own(name):
    return f"OWN ONLY {W}/{name}/ and {W}/{name}.md; scratch {SCR}/{name}/."


ITEMS = [
    seat("R93ExecC1", "executor",
         "Re-derive C1's after arm, control and pristine run on committed bytes, independently of the L1. " + own("R93ExecC1"),
         "1. Run the C1 after search (r93 population) and the control (same targets, --population "
         "census/round-92/c1-false-rows.tsv); save both receipts in your seat dir; quote both SEARCH-SUMMARY lines.\n"
         "2. Run the pristine harness on the r93 population; quote LD4, LD4r, LD5, LD6 and SUMMARY lines and the exit.\n"
         "3. Pins: sha256 of the counter, the r93 harness, both populations, the targets file and the search vs the "
         "prereg; `cmp -n <size of r92 population>` the r92 population against the r93 prefix; `diff` the r93 harness "
         "against census/round-92/c1-false-row-harness.py and classify EVERY hunk (docstring, pin, new row types, "
         "UNEXPECTED); `diff` the r93 search against census/round-92/c1-survivor-search.py likewise.\n"
         "4. Prove the two new row types edit ONLY P04's own ledger row: write a scratch copy of the harness that "
         "also saves the edited ledger, run LD5/LD6 only, and `diff` each edited ledger against "
         "census/round-77/c2-pointer-ledger.tsv (one line removed / one line cut to three columns, nothing else).\n"
         "5. For each of the two kills, open the mutant's harness.out (rerun one mutant at a time with the search's "
         "--ids on a one-id JSON) and name which ROW lines read match=no. Is LD5 the killer of h-ok-admits-one and LD6 "
         "of a491c22? Any OTHER row red would contradict the control (FALSIFIES-NUMBER).",
         "Both SUMMARY lines, the pristine row lines, the pin table, the hunk inventories, the two ledger diffs and "
         "the per-kill killing-row table. Any mismatch to the prereg is HIGH.",
         ),
    seat("R93ExecResidual", "executor",
         "Score the 78-id residual set on both populations (reported, not claimed, in the prereg). " + own("R93ExecResidual"),
         "Run the r93 search with `--ids census/round-93/c1-residual-plus-e1.json --jobs 4` twice: once with "
         "--population census/round-92/c1-false-rows.tsv and once with census/round-93/c1-false-rows.tsv (both with "
         "--harness census/round-93/c1-false-row-harness.py, --emit <seat dir>/survivors-<pop>.json). Save both full "
         "receipts in your seat dir. Then: (a) list every id whose verdict differs between the two populations; (b) "
         "list every `errored` and `hung` id with the first failing ROW line from its harness.out; (c) say whether "
         "any id other than the two C1 targets is killed on r93 but not r92 (an unpredicted extra kill is not a "
         "falsification, but report it); (d) cross-check: the r92 receipt census/round-92/records/c1-search-r91-full.txt "
         "scored these 77 as survivors on r91 under the OLD kill rule — does any of them now read `errored` on the r92 "
         "population?",
         "Both SEARCH-SUMMARY lines, the difference list, the errored/hung list, and the extra-kill verdict.",
         ),
    seat("R93ExecC2", "executor",
         "Re-derive C2's after arms and controls, and test the reference beyond the fixture's sweep. " + own("R93ExecC2"),
         "1. Run the C2 probe after arm, the probe control (--fixture tests/fixtures/r92-k4-flagfail.py), the r93 "
         "fixture after arm, the r91-tool-both-arms control and the r87 K4 regression (python3 -B "
         "census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <empty>); save all five; "
         "quote every FORGERY/CASE/SUMMARY line and exit.\n"
         "2. Pins (fixture ed15094e..., probe f3c84c49..., tool fc0e35c2..., before 21e5c740...) and a hunk "
         "inventory of `diff tests/fixtures/r92-k4-flagfail.py tests/fixtures/r93-k4-flagfail.py` and of the two "
         "probes.\n"
         "3. Independence: show (grep/ast) that `_ref_len`, `_ref_straddle` and `ref_cuts` call no codec "
         "(no `.decode`, `codecs`, `str(`...).\n"
         "4. Beyond the sweep: import the fixture's `ref_cuts` and the filed tool in scratch; on >= 300,000 seeded "
         "random payloads (lengths 201-400, bytes from a mix of ASCII, every Table 3-7 boundary encoding, the "
         "ill-formed classes, truncations, random bytes) compare `_one_line_bytes(raw)` with the reference cell; "
         "report every disagreement with the payload hex. Also run F5/F6/F7 (rebuild them from the probe's edit "
         "table) on the same payloads and count their disagreements.",
         "The receipts' lines, pin table, hunk inventory, the independence check, and the random-sweep counts (filed "
         "tool: disagreements, each with hex; F5/F6/F7: counts). A filed-tool disagreement is FALSIFIES-WORDING.",
         ),
    seat("R93MutC1", "mutation-tester",
         "Attack C1: other spellings of the two clauses, and the new kill rule. " + own("R93MutC1"),
         "1. Alternative spellings that the r93 population should also see (score each with the r93 harness on the "
         "r93 population, at most 2 work trees at once; write the mutant files yourself): line 552 `resolved > "
         "len(pop) - 2`, `resolved >= len(pop) - 2`, `resolved + counts['unresolved'] == len(pop)`, `unresolved <= 1 "
         "and resolved >= len(pop) - 1`; line 491 `len(r) <= 3`-style variants (`len(r) < 4`, `len(r) not in (3, 4)`, "
         "`len(r) != 4`). Which survive? Each survivor needs a row shape or a named limit.\n"
         "2. Kill-rule probe: build a mutant that makes the counter crash on the LD5 run only (rc 2) and one that "
         "crashes at import; run the r93 search with --ids on hand-made copies (or call its `verdict()` on the "
         "harness outputs) and show they read `errored`, not `yes`. Show a harness exit 2 is `errored`.\n"
         "3. Does LD5 alone (not LD6) kill h-ok-admits-one, and LD6 alone a491c22? Build scratch populations with one "
         "of the two rows removed (pin them in a scratch harness copy) and score each target.",
         "A spelling table (edit, verdict, killing rows), the kill-rule verdicts, the one-row attribution, and "
         "FALSIFIES-WORDING for any C1 sentence an artifact refutes.",
         ),
    seat("R93MutC2", "mutation-tester",
         "Attack C2's r93 fixture with forgeries the probe does not carry. " + own("R93MutC2"),
         "Write at least eight one-edit forgeries of the FILED tool (scratch copies only) and run each through the "
         "r93 fixture with the r91 tool as --before. Required: (a) search window 3 back instead of 4 (R92MutC2 "
         "A_window3; equivalent?); (b) payload-length-keyed special case (`if len(raw) == 230: ...` falls back to the "
         "r92 behaviour otherwise — the sweep uses one length); (c) a repro-key on cell text (R92MutC2 H); (d) the "
         "head cut moved back one byte too far when a sequence straddles; (e) the tail cut's end off by one only for "
         "4-byte sequences; (f) strict decode replaced by a range table missing ONLY the F4 upper boundary; (g) ... "
         "missing ONLY the ED upper boundary; (h) a forgery that is correct only when the filler byte is `a`. For each: "
         "rc, tool_pass/cases, failing cases. Every SURVIVOR (rc 0) is a gap: give a distinguishing payload and say "
         "whether the prereg's stated limits (i)-(v) cover it.",
         "A forgery table and, per survivor, a distinguishing payload and a verdict (FALSIFIES-WORDING or the limit "
         "that covers it).",
         ),
    seat("R93ReviewerC1", "reviewer",
         "Falsify C1's stated wording on committed bytes. " + own("R93ReviewerC1"),
         "1. Re-derive the after and control SEARCH-SUMMARY lines yourself (independent runs) and quote them.\n"
         "2. Sentence by sentence: do both edits survive EVERY r92 row (score them with the r92 harness "
         "census/round-92/c1-false-row-harness.py and the r92 search on the r92 population; note the r92 search has "
         "no h-ok-admits-one, so apply that edit by hand)? Is 'no r92 run reaches their clause' true (read every r92 "
         "row type and the counter's lines 484-495 and 541-552)? Is LD5's run really 'exactly one item UNRESOLVED and "
         "no id unknown' (read the pristine counter's ITEM/SUMMARY lines for the LD5 run)? Is LD6's ledger three "
         "columns? Is the r92 64-row prefix byte-identical? Is the counter unchanged?\n"
         "3. Chronology: was census/round-93/c1-prediction.txt committed (P1) before any r93-population mutant "
         "receipt? Use git log/show on the lane branch.\n"
         "4. Read the new kill rule in the search: can a mutant be scored `yes` without a row mismatch, or `no` with "
         "one?",
         "Independent SUMMARYs, a sentence table (holds / neutral / falsifies-wording), the chronology check, the "
         "kill-rule reading, and the explicit falsification list.",
         ),
    seat("R93ReviewerC2", "reviewer",
         "Falsify C2's stated wording on committed bytes. " + own("R93ReviewerC2"),
         "1. Re-derive the probe after arm and its r92-fixture control; quote both FORGERY-SUMMARY lines and exits.\n"
         "2. Read `_ref_len`/`_ref_straddle`/`ref_cuts` against census/round-93/srcs/encoding.txt (§8.1.1, the UTF-8 "
         "decoder steps) and S355 Table 3-7 (census/round-92/srcs/unicode-ch3.txt): is every lead range, bytes-needed "
         "count and boundary exactly the spec's? Quote the spec lines next to the code lines.\n"
         "3. Is 'the r92 fixture checks only prefix/suffix faithfulness' true of KFF18, and do F5/F6/F7 pass it "
         "20/20 (control receipt)? Does each of F5/F6/F7 fail ONLY KFF19 on the r93 fixture, and is that because of "
         "the cut position (show one distinguishing payload per forgery, filed vs forgery vs reference cells)?\n"
         "4. KFF20: compute byte offsets of the headill payload and show the head cut lands between the two 0x80 "
         "bytes; would the r91 tool, F2 and a lead-length cut fail it?\n"
         "5. Is the 14,586 count what `exact_payloads()` yields, and is EXACT_N a literal, not computed?",
         "The SUMMARYs, a spec-vs-code table, per-forgery distinguishing payloads, the KFF20 derivation, the count "
         "check, and the explicit falsification list.",
         ),
    seat("R93Critic", "critic",
         "Attack both claims' wording, controls, chronology and certifying power. " + own("R93Critic"),
         "1. Do-nothing reach: re-run one control of each claim and quote it.\n"
         "2. C1 is two named edits. Is the claim's target chosen by construction (cf. r92 limit vi)? The prediction "
         "file was committed before scoring — check the commit order and say whether that makes it a test or still "
         "a construction. What result would have refuted C1?\n"
         "3. C2: is 'coverage' the right axis (AXES.md {FLEET}/AXES.md, lane SCORECARD.md; the prompt's §9 says a "
         "coverage claim names the surface it moves and the command that would show it unmoved)? Is the fixture's "
         "reference genuinely independent of the tool, or could a reference bug and a tool bug coincide?\n"
         "4. Separability: run C1's after arm in a scratch clone where the C2 fixture/probe are absent, and C2's "
         "after arm in a scratch clone with the r92 harness/population; each must still reach its target.\n"
         "5. Any sentence in the prereg that claims more than its instrument enforces.",
         "Control quotes, the construction verdict for C1, the axis verdict for C2, both separability runs, and the "
         "explicit falsification list.",
         ),
    seat("R93Labrat", "mutation-tester",
         "One falsifiable hypothesis: the r93 search's interrupt path leaves no work tree and no live process. " + own("R93Labrat"),
         "Hypothesis H: sending SIGTERM (and separately SIGINT) to a running `census/round-93/c1-survivor-search.py` "
         "(r93 population, --ids on a JSON of 4 generated ids, --jobs 2) after 6 s makes it exit 130 within 30 s, "
         "with zero `m*/w` directories left under --work and no surviving harness/counter process of that run. "
         "Measure: exit code, elapsed, `find WORK -mindepth 2 -maxdepth 2 -name w | wc -l`, `du -sk WORK`, and the "
         "process list filtered by the work path. Control: the r92 search (census/round-92/c1-survivor-search.py, "
         "r92 harness and population) under the same signal. Run each arm twice. Then: does a SIGKILL of the search "
         "still strand trees (expected: yes; it is a stated r92 residual)?",
         "H confirmed or refuted per arm with the raw measurements; any refutation is FALSIFIES-WORDING against the "
         "search's docstring change 3 (not a claim sentence) and must say so.",
         ),
    seat("R93Sentinel", "sentinel",
         "Safety and robustness of the new harness row types, the search changes and the r93 fixture. " + own("R93Sentinel"),
         "1. The ledger-drop/ledger-trim writer: where does the edited ledger go (must be under --work), what if the "
         "item occurs twice or has 3 columns (must be rc 2 setup), does a `#`-comment line that starts with the item "
         "id get edited (it must not)? Build scratch populations/ledgers to test, using a scratch copy of the harness "
         "with your scratch population pinned.\n"
         "2. The search: --emit under /tmp refused? --work symlink to /tmp refused? Does `_reap` delete anything "
         "outside --work (read it; test with a symlinked m0000/w)?\n"
         "3. The r93 fixture's KFF19: CPU/memory cost (time it), and whether an exception in the tool under test "
         "(e.g. a forgery raising IndexError) is caught and scored fail rather than crashing the fixture.\n"
         "4. List any path an r93 instrument writes under /tmp regardless of TMPDIR/--work.",
         "Findings HIGH/MEDIUM/LOW with reproducers, or 'no finding' per item with what was tried.",
         ),
    seat("R93Connector", "connector",
         "Cross-claim and cross-lane pattern scan, plus the planning data-walk the L1's planner seat delegates. " + own("R93Connector"),
         "1. Sibling overlap: grep the sibling lane repos under {FLEET}/*-shokunin/ (read-only) for a WHATWG Encoding "
         "Standard source, a reference UTF-8 decoder in a test, or a ledger-edit mutation row; say whether any "
         "sibling owns this surface, with paths.\n"
         "2. Cross-claim pattern: C1 (no run reached the clause) and C2 (a property every boundary-respecting cut "
         "satisfies) are both 'the instrument's inputs never exercise the distinguishing condition'. List other "
         "lane instruments under census/round-8*/ and round-9*/ with the same shape (a check satisfied by a whole "
         "family of wrong implementations), with paths.\n"
         "3. Planning data-walk: read corpus/lessons/round-92-verifier-spotcheck.md §7 routed items 1-5 and SCORECARD.md "
         "`### Planned (r93)`; mark each answered / partly / carried with the r93 file that answers it; draft the "
         "`### Planned (r94)` bullet list.\n"
         "4. Routed item 4 (SOURCES rule 2): did r93 edit any non-mutable cell of an existing SOURCES row? Check "
         "`git diff {BASE} -- corpus/SOURCES.md`.",
         "Overlap verdict with paths, the pattern list, the routed-item table and the r94 draft, and the rule-2 check.",
         ),
    seat("R93ScoutSources", "scout",
         "Re-open the round's source and propose the reject sample. " + own("R93ScoutSources"),
         "1. Fetch https://encoding.spec.whatwg.org/ live (curl -sSL, record HTTP code, final URL, byte size, sha256) "
         "into your scratch; compare with census/round-93/srcs/encoding.html (cmp; if it differs, diff the §8.1.1 "
         "text only and say whether the decoder steps changed).\n"
         "2. Verify the S356 row in corpus/SOURCES.md: the quoted sentence's word count (22?), its occurrence count "
         "in the whitespace-normalized tag-stripped text, that it sits under `id=\"utf-8-decoder\"` (§8.1.1), that "
         "the row parses as 11 cells with no `|` inside a cell, and the 'Last Updated' date.\n"
         "3. Read corpus/knowledge/utf8-cut-position-reference.md against the source: is every decoder fact it states "
         "(bytes needed per lead range, the four boundaries, 'any other lead is an error') exactly what §8.1.1 says? "
         "Quote the source lines.\n"
         "4. Propose ONE reject sample from the same standard or an adjacent source (e.g. the Encoding Standard's "
         "'UTF-8 decode' BOM handling, or Unicode's 'Best Practices for Using U+FFFD') with a <=25-word located quote, "
         "why it grounds nothing r93 claims, and a flip condition.",
         "Fetch receipt and cmp verdict, the row check, the entry-vs-source check with quotes, and the reject sample "
         "(URL, access date, quote, locator, reason, flip condition).",
         ),
    seat("R93Scribe", "scribe",
         "Draft the round lesson's Mistakes and one QUALITY criterion from evidence. " + own("R93Scribe"),
         "1. Mine mistakes into a draft `## Mistakes` block (class · evidence pointer · captured-by · fix; a fix "
         "counts only once shown able to fail). Candidates to verify from evidence (read the files; invent nothing): "
         "(a) r92's kill rule scored any non-zero exit as killed (R92MutC1 §1, plans/round-92.md A3) — r93 search "
         "`verdict()`; (b) r92's KFF18 property was satisfied by every boundary-respecting cut (R92MutC2 D/E, "
         "plans/round-92.md A1) — r93 KFF19; (c) r92's S355 anchor cell edited in place (r92 spot-check note 1(a), "
         "routed item 4); (d) the L1 ran three controls in one shell with `&` and the shell tool panicked, losing two "
         "of them (census/round-93/controls/ shows only the re-run receipts; ask nothing, just note the L1's account "
         "in plans/round-93.md if present, else mark 'L1 account pending').\n"
         "2. Draft one QUALITY.md criterion (next free Q number after the last in corpus/QUALITY.md) that would have "
         "caught (b): a faithfulness property must be paired with a position/exactness check against an independent "
         "reference, with a counting command (e.g. the probe's rejected count on a forgery that only moves the cut).\n"
         "3. Draft the `## Gate` block for S356 (URL, access date 2026-11-09, quote, locator) and leave the "
         "reject-sample slot for the scout.",
         "Draft text blocks (Mistakes, QUALITY criterion, Gate skeleton) in your report, each line carrying its "
         "evidence path.",
         ),
]


def main():
    print(json.dumps({"wave": "souji-r93-w1",
                      "milestone": "souji r93: C1 two ledger-edit rows bind two counter edits no r92 run reaches "
                                   "(calibration); C2 an exact-position reference cut (WHATWG decoder, S356) rejects "
                                   "three forgeries the r92 fixture passed (coverage)",
                      "reportDir": ".ufo/waves/round-93/w1",
                      "context": CTX,
                      "items": ITEMS}, indent=1))


if __name__ == "__main__":
    main()
