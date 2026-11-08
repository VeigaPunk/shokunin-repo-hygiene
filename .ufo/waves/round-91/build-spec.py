#!/usr/bin/env python3
"""Build the souji r91 wave-1 spec. Run: python3 .ufo/waves/round-91/build-spec.py > .ufo/waves/round-91/w1-spec.json
P and F hashes are read from the lane's git branch (P = instruments + controls, F = the preregistration alone)."""
import json
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "681f6c72b242d410d0e8654efadb2a1553fb111d"

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


log = git("log", "--format=%H %s", "-16", "master").splitlines()


def find(prefix):
    for line in log:
        h, _, s = line.partition(" ")
        if s.startswith(prefix):
            return h
    return "<" + prefix + ": not found yet>"


P1 = find("round-91: instruments")
P2 = find("round-91: C1 control")
F = find("round-91: preregistration")
CTX = f"""# Goal
souji round 91 (lane repo {LANE}, lane id souji). The L1 (SoujiR91) holds the planner seat and is the ONLY
integration owner: it froze the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 13 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion.

# Frozen round (read {LANE}/census/round-91/preregistration.txt FIRST — it is the contract)
Lane base {BASE} (r90 closed; its non-author spot-check is corpus/lessons/round-90-verifier-spotcheck.md). P1 {P1}:
instruments, population, harness, battery, mutants, the C2 boundary repair, the r91 fixture, variants, controls and
pre-freeze validation receipts. P2 {P2}: the C1 do-nothing control on the r90 population. F {F}: the preregistration
alone (frozen before any after-data). The filed instruments are FROZEN: do not modify census/round-91/,
tests/fixtures/, tools/ or corpus/ — copy what you need into your own wave dir and write receipts there. Nothing in
the claim wording may be widened by this wave; the wave's job is to FALSIFY it (Amendment 59: a claim verifies only
if no artifact produced by this round's own wave falsifies its STATED WORDING; numbers re-deriving is necessary,
not sufficient).

Claims (verbatim targets; read the prereg for the full predicate, kill rule and stated limits):
- C1 calibration 7 (the lane's lowest owned non-retired axis): SIX mutant edits that survive the r90 population —
  `ld1c-class-keyed`, `ld1d-conflict-keyed`, `nf6i2-last-occurrence`, `nf6j-pathch-narrow`, `s1-exact-width`,
  `s3-equal-two` — are bound by five new population rows (LD1c identical duplicate, LD3 one column, LD4
  ledger-resolve, NF6i2 R13 whole-first, NF6j R13 PATHCH predecessors). Population census/round-91/c1-false-rows.tsv
  (63 rows = the r90 58 byte-for-byte plus five; sha256 fdc3d238…); harness census/round-91/c1-false-row-harness.py
  (sha256 5c6a1cf9…); battery census/round-91/c1-clause-battery.py (sha256 5f717a1b…); mutants
  census/round-91/c1-mutants.json (sha256 3c26051e…, 22 members); counter census/round-87/c1-pointer-counter.py
  (sha256 fd0a8e24…, UNCHANGED). Predicate (after): python3 -B census/round-91/c1-clause-battery.py --counter
  census/round-87/c1-pointer-counter.py --mutants census/round-91/c1-mutants.json --work <empty> --only r90,r91
  --expect-killed 38 must print `SUMMARY mutants=22 sets=r90,r91 pristine_r90=ok pristine_r91=ok killed_r90=16
  killed_r91=22 killed_total=38` and EXIT 0. Control: the same battery `--only r90 --expect-killed 16` reads
  killed_r90=16 with ALL SIX new members killed=no, EXIT 0.
- C2 operability 8: the r90 tool's 200-octet window cut ignored UTF-8 sequence boundaries, so a 201-byte stderr
  whose U+0085 straddles the tail cut printed the orphan 0x85 as the raw byte's spelling (S90Reviewer2 F1/A4). The
  filed tool (sha256 21e5c740…) moves both cuts to sequence boundaries; the r91 fixture tests/fixtures/
  r91-k4-flagfail.py (sha256 f815abbc…, 15 cases) enforces the four clauses the r90 wording claimed. Predicate
  (after): python3 -B tests/fixtures/r91-k4-flagfail.py --tool tools/souji-record-agreement.py --before
  census/round-91/controls/c2-before-tool.py --work <empty> prints `SUMMARY cases=15 tool_pass=15 before_pass=14`
  and EXIT 0; python3 -B census/round-91/c2-variant-probe.py --fixture r91 --work <empty> prints
  `SUMMARY variants=3 fixture=r91 detected=3` EXIT 0; the control `--fixture r90` prints
  `SUMMARY variants=3 fixture=r90 detected=0` EXIT 0; the r87 12-row K4 regression stays rows=12 mismatches=0
  errors=0 EXIT 0.

# Evidence durability and the pre-file ledger (Amendment 59)
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every argument, output line and falsifying reproducer you want the ledger to read must live under
{LANE}/.ufo/waves/round-91/w1/ (your seat dir or your report). If an artifact of yours falsifies a sentence of
either claim, say so plainly in the report under a heading `FALSIFIES-WORDING` (or `FALSIFIES-NUMBER`) with the exact
sentence and the reproducer path; the L1 records it as an amendment in plans/round-91.md, never silently.
Every `Report:` trailer path is relative to {LANE} — write it at {LANE}/<that path>.

# Write scope and scratch
Write only under your own seat dir {LANE}/.ufo/waves/round-91/w1/<your name>/ and your own report file. Read the lane
read-only. Scratch (clones, fixtures, counter --work dirs) lives under /fast/scratch/hyaku/souji-r91/<your name>/;
create it with mkdir -p and DELETE it before you yield (trap 'rm -rf -- \"$S\"' EXIT in shell, finally: shutil.rmtree
in Python), copying receipts into your seat dir first. /tmp is for files under 50 MB only and is never citable
evidence. Any git fixture is `D=$(mktemp -d)` + `git -C \"$D\" init -q`, every later call names `-C \"$D\"`, and you
assert `git -C \"$D\" rev-parse --show-toplevel` equals `$D` before the first commit; an empty or unchecked
`git -C \"$v\"` with an empty variable falls back to the fleet root and has committed a stray file there (r70
incident) — never do it. Do not run mutating git/jj anywhere.

# Tooling authorization (operator, 2026-10-19)
You may install or upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels,
update-safety gate; record tool/version/channel/reason in your report). pacman transactions are PAUSED host-wide
until the operator resolves the host-recovery L0 question: install via `uv tool`/`npx`/an official binary in
~/.local/bin, or file an L0 question. Never mutate host sysctls. No tool install is needed for this round.

# Round shape
One v1 wave, 13 seats (policy band 8-16). Attack seats under the addendum's four-role definition: 2 reviewer +
critic + mutation-tester = 4/13 = 30.8 % (>= 25 %); the prefile gate's broader ATTACK_ROLES set also counts the
connector, sentinel and revenger (7/13). 4 executors, 1 scribe, 1 scout, 1 connector, 1 revenger, 1 sentinel.
Residual calls: none. The L1 holds the canonical planner seat (the validator rejects `planner`); the bounded
planning data-walk rides the connector seat.
"""


def seat(name, role, target, change, accept):
    return {"name": name, "role": role,
            "prompt": GOD + f"# Target\n{target}\n\n# Change\n{change}\n\n# Acceptance\n{accept}\n\n"
                            f"Report: .ufo/waves/round-91/w1/{name}.md\n"}


ITEMS = [
    seat("R91ExecC1Harness", "executor",
         "Audit the C1 population+harness and drive every new row by hand. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91ExecC1Harness/.",
         "1. Run the r91 harness with the pristine r87 counter on the r91 population; save the receipt and quote the "
         "eleven new-row `ROW` lines and the SUMMARY. Then run it on the r90 population and confirm 58 rows.\n"
         "2. Prove the population delta: `cmp -n <r90 size>` the r90 file and the r91 prefix; `diff` and say which "
         "five lines differ. Confirm the counter sha is fd0a8e24… (it must be byte-unchanged).\n"
         "3. Read the R13 fixture block and the leaf list in the harness: quote the two declaration lines the "
         "fixture writes, and confirm the two fresh leaves exist on the fixture disk. Then drive NF6i2 and NF6j by "
         "hand: run the counter with a one-row forge at R13 for the pristine counter and for `nf6i2-last-occurrence` "
         "/ `nf6j-pathch-narrow` (copy the counter and apply the one-line edit in your scratch); quote the "
         "`FORGE` lines.\n"
         "4. Drive LD1c, LD3 and LD4 by hand: build the three ledgers in your scratch and run the pristine counter "
         "plus `ld1c-class-keyed`, `ld1d-conflict-keyed`, `s3-equal-two`, `s1-exact-width`; quote the "
         "`ITEM P04` / `LEDGER-REFUSED` lines and exits. Say which row binds which mutant and whether any row is "
         "redundant.",
         "The pristine receipt lines, the population diff, the R13 declaration lines + leaf check, and the "
         "row x mutant hand-drive table with exact outputs. Name any mismatch to the prereg as HIGH.",
         ),
    seat("R91ExecC1Battery", "executor",
         "Re-derive BOTH C1 arms end to end on committed bytes, independently of the L1. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91ExecC1Battery/.",
         "1. Run the after command from the context (22 mutants, both populations, --expect-killed 38) into your "
         "scratch; save the receipt and quote every MUTANT-PAIR line and the SUMMARY.\n"
         "2. Run the control (--only r90 --expect-killed 16) and quote the six new members' `killed=no` lines and "
         "the SUMMARY.\n"
         "3. Verify every pin the battery prints (its own sha, counter, harness, mutants, both populations) against "
         "the prereg; flag any mismatch as HIGH.\n"
         "4. Check the kill rule can fail: take one new row, delete it from a COPY of the population (recompute the "
         "sha only inside your scratch run by passing the copy explicitly through the harness) and show the "
         "corresponding mutant survives. Do not modify the filed population.",
         "Verdict per arm with exact SUMMARY lines, the pin table, and the row-deletion kill-power probe with its "
         "output. Name any mismatch to the prereg.",
         ),
    seat("R91ExecC2Tool", "executor",
         "Validate the boundary repair at the unit level and its regression surface. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91ExecC2Tool/.",
         "1. Import the filed tool in a scratch interpreter and expose `_one_line_bytes`. For payloads of 201-260 "
         "bytes carrying 1-, 2-, 3- and 4-octet characters at every cut position, print (a) the cell, (b) its raw "
         "byte length (must be <= 202), (c) whether any `\\x85` or `\\u0085` escapes appear without a corresponding "
         "whole sequence in the payload. Save the matrix.\n"
         "2. Show the r90 tool (census/round-91/controls/c2-before-tool.py) produces an orphan `\\x85` for the "
         "101p+C285+98s payload and the filed tool does not; quote both cells.\n"
         "3. Preserve the raw-byte spelling: a lone 0x85 that belongs to no lead byte, and an invalid byte at a cut "
         "position, must still print `\\x85` / `\\xNN`; show the payloads and cells.\n"
         "4. Run the r87 12-row K4 regression on the filed tool (python3 -B census/round-87/c2-k4-counter.py "
         "--tool tools/souji-record-agreement.py --work <scratch>); quote rows/mismatches/errors/EXIT. Diff the "
         "tool against census/round-91/controls/c2-before-tool.py and classify every hunk (boundary helpers, "
         "docstring, UNEXPECTED).",
         "The cut matrix (payload -> boundary, cell, length, orphan check), the before/after cells, the raw-byte "
         "preservation cells, the regression line and the hunk inventory (UNEXPECTED empty or named).",
         ),
    seat("R91ExecC2Fixture", "executor",
         "Re-derive BOTH C2 arms and the variant discrimination on committed bytes. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91ExecC2Fixture/.",
         "1. Run the after fixture command and the control (the r90 tool as BOTH arms) into your scratch; save both "
         "receipts and quote every CASE line plus the SUMMARY and exit.\n"
         "2. Run the variant probe on the r91 fixture and on the r90 fixture; quote all VARIANT lines and both "
         "SUMMARies. For each detected variant, name the single case it fails and the exact check that fails.\n"
         "3. Verify the fixture's control claim: run the r91 fixture with the r90 tool as --tool and the r90 tool as "
         "--before; quote the CASE lines and SUMMARY (KFF11 must fail on both arms).\n"
         "4. Attack KFF13's source scan: show what a tool with a docstring that merely MENTIONS `_one_line(` does, "
         "and what a tool with a real dead helper does. Decide whether the check can false-green or false-fail, and "
         "report it as a limit or a defect.",
         "Verdict per arm with exact CASE/SUMMARY lines, the variant table (variant -> failing case -> check), and "
         "the KFF13 scan probe result with its verdict.",
         ),
    seat("R91MutCounter", "mutation-tester",
         "Attack C1's instrument: are the five rows load-bearing, minimal, and can any false-green or false-kill? "
         f"OWN ONLY {LANE}/.ufo/waves/round-91/w1/R91MutCounter/.",
         "1. Reproduce the after and control arms (quote the SUMMARYs).\n"
         "2. Per new row, build the counter-level matrix: pristine + every new mutant, against the row's ledger or "
         "fixture rev; say which row kills which mutant and whether any row kills nothing or was already bound.\n"
         "3. Q162 follow-up: try at least four alternative single edits of the same clauses that still survive all "
         "22-mutant scoring (e.g. an occurrence loop that stops after the second occurrence, a PATHCH that includes "
         "alnum + `/` + `.`, a ledger guard `len(r) < 4`, a duplicate rule keyed on the note cell) and score each "
         "on both populations with a copy of the battery. Each survivor needs a row shape or a named limit.\n"
         "4. False-kill probe: can a mutant be scored killed without changing the clause's behaviour (e.g. an edit "
         "that crashes the counter's argument parser)? Test one and say whether the kill rule distinguishes it.",
         "The row x mutant matrix, the alternative-edit survivors with their required row shape (or named limit), "
         "and the false-kill verdict. Name every artifact path under your seat dir.",
         ),
    seat("R91ReviewerC1", "reviewer",
         "Falsify C1's stated wording on committed bytes. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91ReviewerC1/.",
         "1. Re-derive the after and control numbers yourself (independent runs) and quote the SUMMARYs.\n"
         "2. Sentence-by-sentence: does `killed_r90=16` hold for the SIXTEEN r90 members, and do ALL SIX new members "
         "survive r90? Does `killed_r91=22` hold with both pristine arms green? Is the counter byte-unchanged? Is "
         "the population prefix byte-identical? Is each of the five rows actually load-bearing (delete it and show "
         "the loss)?\n"
         "3. Check the LD4 row's strength: it asserts an ITEM status and NO exit code. Can a counter that refuses "
         "the whole ledger still print MOVED for P04 by any other route? Read `judge()` and say yes/no with the "
         "reproducer.\n"
         "4. Write `FALSIFIES-WORDING` rows for every sentence you can refute, with the artifact path.",
         "The independent SUMMARYs, the sentence table (holds / neutral / falsifies-wording), the LD4 strength "
         "probe, and the explicit falsification list.",
         ),
    seat("R91ReviewerC2", "reviewer",
         "Falsify C2's stated wording on committed bytes. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91ReviewerC2/.",
         "1. Re-derive the after fixture run, the variant probe (both fixtures) and the K4 regression; quote "
         "SUMMARYs and exits.\n"
         "2. Byte-level check of the boundary case: reconstruct the nelcut payload, show the 201-byte length, the "
         "index of C2 and 85, the head-100 and tail-99 cuts, and prove the filed cell contains neither spelling and "
         "the r90 cell contains `\\x85`.\n"
         "3. Clause-by-clause: is `before_pass=14` the r90 tool's score and does it fail ONLY KFF11? Does KFF12 "
         "test a property that the r90 tool passes (it must: otherwise the before arm would fail it) and the "
         "newline variant fails? Is KFF13's static scan sound for the stated sentence?\n"
         "4. Write `FALSIFIES-WORDING` rows for every sentence you can refute, with the artifact path.",
         "The independent SUMMARYs, the byte-level boundary derivation, the clause table, and the explicit "
         "falsification list.",
         ),
    seat("R91Critic", "critic",
         "Attack both claims' wording and the instruments' certifying power. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91Critic/.",
         "1. Read the prereg and list every sentence that states more than its instrument enforces. Prioritize: "
         "`_cut_head`/`_cut_tail` on 3- and 4-octet characters and on invalid streams; a bound that only claims 202; "
         "the LD4 row's missing exit-code assertion; `killed_total=38` as a sum over two different populations; the "
         "`each of the five rows is load-bearing` sentence vs LD1c killing two mutants.\n"
         "2. Build the cheapest probe that falsifies each candidate sentence; run it; record the exact cell/output.\n"
         "3. Try a tool variant that passes the r91 fixture 15/15 without the boundary repair (hardcoded cells, a "
         "docstring-only change, a fixture-detecting branch) and say whether the fixture can see it.\n"
         "4. Write `FALSIFIES-WORDING` rows for each real counterexample, with paths.",
         "The sentence table with probes, the fixture-blindness attempt and its verdict, and the explicit "
         "falsification list.",
         ),
    seat("R91Sentinel", "sentinel",
         "Adversarial audit of the repaired tool and the fixture's escape guarantees. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91Sentinel/.",
         "1. Exhaustive small-payload sweep: every payload of length 190-210 built from the alphabet {{ASCII x, C2 85, "
         "E2 80 A8, F0 9F 98 80, raw FF}} at the cut region; for each, compare the filed tool's cell with the r90 "
         "tool's cell and flag (a) a cell that contains a `\\xNN` escape for a byte that was part of a wider "
         "character, (b) a cell whose raw byte length exceeds 202, (c) two materially different payloads with the "
         "same cell.\n"
         "2. Same-input-different-cut: for one payload, vary `limit` 180-260 and report any cut where the pair "
         "(raw byte 0x85 vs U+0085) collapses again.\n"
         "3. Attack the fixture: can a tool that never reads the payload pass 15/15? Test one hardcoded-output "
         "variant; report whether KFF9-KFF13 bind the public path or can be spoofed.\n"
         "4. Write `FALSIFIES-WORDING` rows for each counterexample, with paths.",
         "The sweep summary (cases, flags per class, worst case), the limit sweep, the fixture-spoof verdict, and "
         "the explicit falsification list.",
         ),
    seat("R91Connector", "connector",
         "Sibling-overlap and prior-art scan; the bounded planning data-walk for r92. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91Connector/.",
         "1. Search the lane's own history/corpus for prior boundary-cut, incremental-decoding or excerpt rules; say "
         "which round first recorded each and whether this round's evidence changes the disposition.\n"
         "2. Read sibling lanes' QUALITY/SOURCES only where readable under /home/vgpnk/Projects/ (read-only; never "
         "edit): does any sibling own UTF-8 cut boundaries, escaped-detail injectivity, or ledger row-width rules? "
         "Route contested scope explicitly.\n"
         "3. Planning data-walk (bounded): list the r92 candidates this round and the r90 spot-check leave open "
         "(the carried items in SCORECARD `### Planned (r91)` not taken, the r91 wave's survivors, the r85/r86 C2 "
         "list), each with status and the cheapest next measurement. Do not plan beyond r92.\n"
         "4. Dedup: name any finding of this wave's other seats (read their reports as they land) that duplicates a "
         "prior-round finding, and any locus the round does not attack.",
         "The overlap table, the sibling-ownership verdict, the r92 candidate list, and the dedup/unattacked list.",
         ),
    seat("R91ScoutSources", "scout",
         "Open and gate the round's source. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91ScoutSources/.",
         "1. Re-fetch https://www.rfc-editor.org/rfc/rfc3629.txt and compare it byte-for-byte with "
         "census/round-91/srcs/rfc3629.txt (sha256 a2a3a394…, 33856 bytes, HTTP status, access date). Record the "
         "HTTP code you observe and the date.\n"
         "2. Locate the prereg's quote (`In a sequence of n octets, n>1, the initial octet has the n higher-order "
         "bits set to 1, followed by a bit set to 0.`): capture line numbers, occurrence count, word count. Also "
         "locate the sentence describing the following octet(s), so the sequence boundary rule is grounded end to "
         "end.\n"
         "3. Open ONE reject candidate (e.g. RFC 3629 §2 `Security Considerations` or the Python codecs "
         "incremental-decoder docs at https://docs.python.org/3/library/codecs.html): decide admit/reject with a "
         "reason and a flip condition for THIS cell.\n"
         "4. Run the lane's sources census: /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root "
         "/home/vgpnk/Projects/shokunin souji; report exit code and row count. Also check the registry for a "
         "duplicate URL of rfc-editor.org/rfc/rfc3629.txt.",
         "The fetch table (URL, HTTP, bytes, sha, capture match), the quote location/word count, the reject verdict "
         "with reason+flip, the census line, and the duplicate-URL check.",
         ),
    seat("R91Scribe", "scribe",
         "Drafts for the L1 to integrate (row, entry, criterion, lesson mistake). OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91Scribe/.",
         "1. Draft the 11-cell S354 row in the registry schema (id, source with URL/capture/sha, kind docs, tier A, "
         "the named scope, anchor+located quote, teaches, status mined, opened date, recheck, used-by "
         "corpus/knowledge/utf8-window-sequence-boundary.md). Verify the quote against the capture byte for byte and "
         "count its words with a pasted command.\n"
         "2. Draft corpus/knowledge/utf8-window-sequence-boundary.md (<=40 lines): the UTF-8 sequence-as-unit rule, "
         "why a raw-byte window must cut at a boundary, the surrogateescape interaction, the head/tail repair, and a "
         "Gate block with URL, access date and <=25-word located quote. Cite S354.\n"
         "3. Draft the next QUALITY.md criterion in the lane's style (an excerpt is evidence only if its cuts are "
         "sequence boundaries and both spellings survive the cut).\n"
         "4. Draft `## Mistakes` for corpus/lessons/round-91.md from the r90 spot-check's routed defects: the "
         "non-existent `census/round-90/claims.json` citation and the attack-share arithmetic, with class, evidence "
         "pointer, captured-by and fix. One row is enough; make the fix able to fail (name the command that would "
         "have caught it).",
         "The row draft (with quote command+output), the entry draft, the QUALITY draft and the mistake draft, each "
         "ready to paste with no placeholder text.",
         ),
    seat("R91Revenger", "revenger",
         "Independent do-nothing control and causal separability for both claims. OWN ONLY "
         f"{LANE}/.ufo/waves/round-91/w1/R91Revenger/.",
         "1. C1 no-work: score the SIXTEEN-member r90 mutant set on both populations with the r90 battery; show it "
         "reaches at most 31, not 38. Score the 22-member set on the r90 population; show the six survive.\n"
         "2. C2 no-work: run the r90 fixture on the r90 tool (12/12) and the r91 fixture on the r90 tool "
         "(tool_pass=14); show neither reaches 15 and the variant probe is 0/3 on the r90 fixture.\n"
         "3. Separability: run the C1 after arm with the r90 tool in place (C2 not landed) and the C2 after arm "
         "with the r90 population in place (C1 not landed); each must still reach its own target, so neither claim "
         "needs the other.\n"
         "4. Say whether any target is reachable by a do-nothing run.",
         "The no-work numbers for both claims, the two separability runs, and the verdict 'reaches-by-no-work: no' "
         "or the counterexample.",
         ),
]


def main():
    print(json.dumps({"wave": "souji-r91-w1",
                      "milestone": "souji r91: C1 binds the four Q162 survivors and the two reachable ledger "
                                   "spellings (calibration); C2 cuts the K4 excerpt at UTF-8 sequence boundaries and "
                                   "the fixture enforces the four clauses the r90 wording claimed (operability)",
                      "reportDir": ".ufo/waves/round-91/w1",
                      "context": CTX,
                      "items": ITEMS}, indent=1))


if __name__ == "__main__":
    main()
