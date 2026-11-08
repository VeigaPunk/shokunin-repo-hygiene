#!/usr/bin/env python3
"""Build the souji r90 wave-1 spec. Run: python3 .ufo/waves/round-90/build-spec.py > .ufo/waves/round-90/w1-spec.json
P and F hashes are read from the lane's git branch (P = instruments + controls + pre-freeze receipts, F = prereg alone)."""
import json
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2"

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


log = git("log", "--format=%H %s", "-14", "master").splitlines()


def find(prefix):
    for line in log:
        h, _, s = line.partition(" ")
        if s.startswith(prefix):
            return h
    return "<" + prefix + ": not found yet>"


P = find("round-90: instruments")
F = find("round-90: preregistration")
CTX = f"""# Goal
souji round 90 (lane repo {LANE}, lane id souji). The L1 (SoujiR90) holds the planner seat and is the ONLY
integration owner: it froze the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 12 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion.

# Frozen round (read {LANE}/census/round-90/preregistration.txt FIRST — it is the contract)
Lane base {BASE} (r89 closed; spot-check corpus/lessons/round-89-verifier-spotcheck.md). P {P}: instruments,
population, harness, battery, mutants, controls, captures and the pre-freeze receipts. F {F}: the preregistration
alone (frozen before any after-data). Nothing in the claim wording may be widened by this wave; the wave's job is to
FALSIFY it (Amendment 59: a claim verifies only if no artifact produced by this round's own wave falsifies its
STATED WORDING; numbers re-deriving is necessary, not sufficient).

Claims (verbatim targets; read the prereg for the full predicate, kill rule and stated limits):
- C1 calibration 7: the r89 sixteen mutants' SOLE survivor `m17c-no-malformed` (the `_ledger` `len(r) < 3` guard) is
  bound by the new row LD2b, which appends the 2-column ledger row `ZZ9<TAB>ABSENT` under an id ABSENT from the frozen
  r77 ledger. Population census/round-90/c1-false-rows.tsv sha256 d64d7695… (58 rows = the r89 57 byte-for-byte plus
  LD2b); counter census/round-87/c1-pointer-counter.py sha256 fd0a8e24… (UNCHANGED); 16 mutants census/round-90/
  c1-mutants.json sha256 39252248…. Predicate (after): python3 -B census/round-90/c1-clause-battery.py --counter
  census/round-87/c1-pointer-counter.py --work <empty> --only r89,r90 --expect-killed 31 must print
  `SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31` and
  EXIT 0. Do-nothing control (committed before F): the same battery `--only r89 --expect-killed 15` reads
  `killed_r89=15` with m17c alive, EXIT 0.
- C2 operability 8: the K4 FLAGFAIL detail is injective on the byte/character pair the r89 repair left colliding —
  raw byte 0x85 keeps `\\x85`, the CHARACTER U+0085 (NEL) takes `\\u0085`; the dead escape-first helper `_one_line`
  (zero callers) is deleted. Fixture tests/fixtures/r90-k4-flagfail.py sha256 d4417213… (12 cases); filed tool
  tools/souji-record-agreement.py sha256 d095b52f…; before tool census/round-90/controls/c2-before-tool.py sha256
  f6fce6d1…. Predicate (after): python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py
  --before census/round-90/controls/c2-before-tool.py --work <empty> must print `SUMMARY cases=12 tool_pass=12
  before_pass=10` and EXIT 0. Do-nothing control (committed before F): the r89 bytes as BOTH arms read
  `SUMMARY cases=12 tool_pass=10 before_pass=10`, KFF9/KFF10 fail, EXIT 1.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every `Report:` trailer path is relative to {LANE} — write it at {LANE}/<that path>.

# Write scope and scratch
Write ONLY under {LANE}/.ufo/waves/round-90/w1/<YourSeatName>/ and your report file. Everything else in the lane is
read-only to you. All clones, mirrors, fixtures and counter `--work` dirs live under
/fast/scratch/hyaku/souji-r90/<YourSeatName>/ (mkdir -p; never /tmp; never $HYAKU_SCRATCH outside that subdir).
Delete your scratch dir before you yield (`trap 'rm -rf -- "$S"' EXIT`), copying receipts into your seat dir first.
Disclose any scratch you left behind. The lane's `census/`, `corpus/`, `tools/` and `tests/` are committed evidence:
read them, never edit them.

# Isolation and git rules
Never run a mutating git/jj command anywhere: no add/commit/push/checkout/reset/stash, no jj write. Read-only git
(log, show, cat-file, diff, status, rev-parse) is fine. A fixture repository is created as
`D=$(mktemp -d {LANE}/.ufo/waves/round-90/w1/<YourSeatName>/tmp.XXXXXX)` (the template MUST end in XXXXXX) and every
git call names `git -C "$D"`; assert `git -C "$D" rev-parse --show-toplevel` equals `$D` before the first commit.
Never pass an empty or unchecked variable to `git -C` (a souji r70 seat committed to the FLEET root through
`git -C ""`). Never touch history, credentials or secrets; a credential-shaped finding is reported, never copied.

# Tooling authorization and host guard
You may install or upgrade tools that help the task, first reading /home/vgpnk/.omp/agent/RULES.md (official
channels only; record tool/version/channel/reason). PACMAN IS PAUSED host-wide: install via `uv tool`/`npx`/an
official binary into ~/.local/bin, or route around it. Never run pacman -S/-Sy/-Syu/-U/-R, never restart a host
service, never mutate a host sysctl.

# Reporting
Record every command you ran and its exact output tail in your report; name the revision or sha256 you measured.
State what you could NOT check. A no-work control that passes the target is a HIGH finding: say so.

# Depth
You are a leaf. Do not spawn subagents, do not run your own swarm, do not message other seats or lanes.

"""


def seat(name, role, target, change, accept):
    return {"name": name, "role": role,
            "prompt": GOD + f"# Target\n{target}\n\n# Change\n{change}\n\n# Acceptance\n{accept}\n\n"
                            f"Report: .ufo/waves/round-90/w1/{name}.md\n"}


ITEMS = [
    seat("S90ExecC1", "executor",
         "Re-derive BOTH C1 arms end to end on committed bytes, independently of the L1. OWN ONLY "
         f"{LANE}/.ufo/waves/round-90/w1/S90ExecC1/.",
         "1. Run the after command from the context (both populations) and the control command (--only r89) into your "
         "scratch; save both receipts and quote their SUMMARY lines.\n"
         "2. Verify every pin the battery prints (counter, harness, mutants, population sha256 and row counts) against "
         "the prereg; flag any mismatch as HIGH.\n"
         "3. Drive the LD2b row BY HAND through census/round-90/c1-false-row-harness.py: once with the pristine "
         "counter and once with the m17c mutant text applied in your scratch copy; record the exact stdout/stderr "
         "and exits. Then do the same with m17 and m17b so the attribution table names the sole killer.\n"
         "4. Check the population: is it the r89 file byte-for-byte plus exactly one appended line? Use cmp/diff and "
         "say which line differs.",
         "Verdict per arm with exact SUMMARY lines, the pin table, the per-mutant hand-drive table (mutant -> rc, "
         "marker/IndexError, row verdict), and the population-diff result. Name any mismatch to the prereg.",
         ),
    seat("S90ExecC2", "executor",
         "Re-derive BOTH C2 arms and the regression on committed bytes, independently of the L1. OWN ONLY "
         f"{LANE}/.ufo/waves/round-90/w1/S90ExecC2/.",
         "1. Run the after fixture command and the control (r89 bytes as BOTH arms) into your scratch; save both "
         "receipts and quote every CASE line plus the SUMMARY.\n"
         "2. Run the r87 12-row regression: python3 -B census/round-87/c2-k4-counter.py --tool "
         "tools/souji-record-agreement.py --work <scratch>; it must stay rows=12 mismatches=0 errors=0 EXIT 0.\n"
         "3. Drive the pair by hand: import the tool in a scratch interpreter and print _escape_text of a stderr "
         "carrying the raw byte 0x85 and of one carrying U+0085 encoded UTF-8; quote both cells. Then confirm the r89 "
         "tool renders them identically, using census/round-90/controls/c2-before-tool.py in a second interpreter.\n"
         "4. Confirm the deletion: grep for `def _one_line(` and for `_one_line(` call sites; report counts. Check "
         "the module still parses and that the fixture's 12 cases exercise the public path.",
         "Verdict per arm with exact CASE/SUMMARY lines, the regression line, the two hand-driven cells for both "
         "tools, and the deletion counts. Name any case that changed verdict since r89.",
         ),
    seat("S90ExecC3", "executor",
         "Instrument-integrity audit: prove the r90 change is the population+harness only (C1) and the escaping "
         f"spelling+dead-code deletion only (C2). OWN ONLY {LANE}/.ufo/waves/round-90/w1/S90ExecC3/.",
         "1. Diff census/round-90/c1-false-row-harness.py, c1-clause-battery.py, c1-false-rows.tsv and "
         "c1-mutants.json against their r89 predecessors (git show master:census/round-89/...). List every changed "
         "line; flag any line that is not the pin, the LD2b branch/row, the docstring, or the mutants note.\n"
         "2. Confirm the counter is byte-identical: git show master:census/round-87/c1-pointer-counter.py | sha256sum "
         "must equal fd0a8e24…, and the battery's own header must print that sha.\n"
         "3. Diff tests/fixtures/r90-k4-flagfail.py against tests/fixtures/r89-k4-flagfail.py; list every changed "
         "line and register; confirm the ten r89 cases and their checks are unchanged, and that the pair checks now "
         "run on both arms.\n"
         "4. Diff the tool: git diff master -- tools/souji-record-agreement.py; classify every hunk as the U+0085 "
         "spelling, the dead-code deletion, a comment/docstring, or UNEXPECTED (HIGH).",
         "The four diff inventories with every line accounted for, the counter sha equality, and the UNEXPECTED list "
         "(empty or named).",
         ),
    seat("S90MutCounter", "mutation-tester",
         "Attack the C1 row: is LD2b load-bearing and sole, and which clauses of the counter remain reachable but "
         f"unrowed? OWN ONLY {LANE}/.ufo/waves/round-90/w1/S90MutCounter/.",
         "1. Reproduce the after and control arms.\n"
         "2. Sole-killer table: score the pristine counter and m17, m17b, m17c by hand against the LD2b ledger; say "
         "which mutant's behaviour changes and why (quote the traceback/marker).\n"
         "3. Alternative spellings (Q162): write at least three DIFFERENT single edits of the malformed guard (e.g. "
         "`len(r) != 3`, `len(r) <= 2` with a different exit, a guard that appends to bad but still stores the row) "
         "and score each on BOTH populations. A spelling that survives r90 means LD2b binds one spelling only: name "
         "it.\n"
         "4. Q162 probes for the r91 planned rows: score a class-keyed duplicate mutant (LD1c candidate), an "
         "identical-duplicate mutant already covered (LD1d), an occurrence-order mutant (NF6i2), and a narrower "
         "PATHCH predecessor mutant (NF6j). For each: survives every pinned population (-> needs a row, name the "
         "shape) or already killed (-> padding, name the killer row).",
         "The sole-killer table, the alternative-spelling table with per-population verdicts, and the Q162 probe "
         "table. Name any unrowed clause you can reach.",
         ),
    seat("S90Reviewer", "reviewer",
         "Independent re-measure of both claims and the S353 source. OWN ONLY "
         f"{LANE}/.ufo/waves/round-90/w1/S90Reviewer/.",
         "1. From committed bytes only, run both after commands and both controls; compare cell for cell with the "
         "prereg and with the L1's receipts under census/round-90/records/. Any number that differs is a HIGH "
         "finding with both values.\n"
         "2. Re-open S353's live URL (https://www.unicode.org/reports/tr14/) and compare the fetched bytes with "
         "census/round-90/srcs/tr14.html (sha256). Locate the quote \"The NL class acts like BK in all respects (there "
         "is a mandatory break after any NEL character).\" and report its occurrence count and tag-stripped offset; "
         "count its words. Check the UAX version/revision the capture names.\n"
         "3. Verify the C2 enumerated kill rule against the fixture source: read KFF9, KFF10 and the pair block and "
         "say whether each case can fail independently. Check the ten r89 cases' checks are unchanged.\n"
         "4. Verify the `_one_line` deletion and that nothing imports it; check the tool's diff for behavior beyond "
         "the claim (any line that changes a verdict outside the FLAGFAIL cell is a HIGH finding).",
         "Two claim verdicts with re-measured lines, the source re-fetch result (bytes/sha/offset/word count), the "
         "kill-rule reading, and the deletion/diff check.",
         ),
    seat("S90Reviewer2", "reviewer",
         "Amendment-59 duty: falsify the claims' STATED WORDING (not their numbers) and produce candidate "
         f"pre-file ledger rows. OWN ONLY {LANE}/.ufo/waves/round-90/w1/S90Reviewer2/.",
         "1. Read census/round-90/preregistration.txt sentence by sentence. For each sentence that makes a promise "
         "the instruments cannot enforce, write a ledger-row candidate: claim, artifact (a path under "
         ".ufo/waves/round-90/ that you create or that another seat created), verdict "
         "(falsifies-wording|falsifies-number|neutral), narrowing (a plan-amendment pointer only if an amendment "
         "exists), note.\n"
         "2. Specifically test: (a) C1's \"SOLE surviving clause\" premise — does any other r89 mutant survive on the "
         "r89 population in your own run? (b) C1's \"bound by one new population row\" — can a different row also "
         "bind m17c, and does LD2b bind anything else? (c) C2's \"injective on the byte/character pair\" — does the "
         "pair check enforce it, or only the two enumerated spellings? (d) C2's \"dead-code deletion\" — is the grep "
         "argument sufficient?\n"
         "3. Write the candidates to your seat dir as a TSV with the same 5 columns the pre-file gate expects.",
         "The sentence-by-sentence table with a verdict per promise and the candidate TSV. Name every sentence you "
         "believe must be narrowed before filing.",
         ),
    seat("S90Critic", "critic",
         "Falsify the claims and the controls: attack the target, the control's independence and the axis "
         f"attribution. OWN ONLY {LANE}/.ufo/waves/round-90/w1/S90Critic/.",
         "1. Reproduce both controls and both after arms; then ask of each: would a no-work change reach the "
         "target? Would a WORK change that is not the claim reach it (e.g. editing the counter instead of the "
         "population; editing the fixture expectation instead of the tool)? Try the cheapest such cheat in scratch "
         "and report whether it scores.\n"
         "2. Attack C1's axis label: the counter and rule are unchanged and only the population grows — is that a "
         "calibration move (binding a clause) or a coverage move (new rows)? Quote the AXES.md definition and give a "
         "verdict.\n"
         "3. Attack C2's before_pass arithmetic: the pair check binds KFF10, which passes alone on the r89 tool. Is "
         "`before_pass=10` a fair control, or does it hide that only KFF9's spelling changed? Say what the honest "
         "sentence is.\n"
         "4. Attack the demo: the claim says the repair makes the pair injective; show any OTHER byte/character pair "
         "in 0x80..0xFF that still collides or explain why none can.",
         "A cheat table (cheat -> score yes/no), the axis verdict, the before_pass reading, and the collision sweep. "
         "Name every sentence you think is falsified.",
         ),
    seat("S90Sentinel", "sentinel",
         "Security and robustness attack on the C2 repair and the K4 record. OWN ONLY "
         f"{LANE}/.ufo/waves/round-90/w1/S90Sentinel/.",
         "1. Inject: a stderr carrying both the raw byte 0x85 and U+0085; a stderr carrying `\\u0085` literally; a "
         "forged writer that prints its own `\\u0085`; a value that tries to make the cell look like a second "
         "MISMATCH row. For each, quote the K4 record and say whether a line-oriented reader can be fooled.\n"
         "2. Re-verify the r89 escapes still hold on the filed tool: 0xFF vs literal, KFF6/KFF7 pair, raw window "
         "202 bytes, head/tail preservation.\n"
         "3. Audit the deletion: confirm `_one_line` has no caller (grep + AST walk of the module for attribute/"
         "name loads) and that no test or fixture imports it from the tool. Report any dynamic reference.\n"
         "4. Check that the repair does not weaken `_escape_record` or the path cell: construct a path holding "
         "U+0085 and one holding a raw 0x85 byte and show both remain distinguishable.",
         "The injection table with exact records, the r89-escape regression lines, the deletion audit, and the path "
         "cell results. Mark any reader-visible ambiguity HIGH.",
         ),
    seat("S90Labrat", "revenger",
         "Bounded empirical probe: map the byte/character spelling collisions of the decode+escape pipeline. OWN "
         f"ONLY {LANE}/.ufo/waves/round-90/w1/S90Labrat/.",
         "1. For every raw byte 0x80..0xFF (single byte, invalid UTF-8) and every code point U+0080..U+00FF (valid "
         "UTF-8), print _escape_text(_decode_record(...)) on the filed tool and on the r89 control bytes; build a "
         "table of pairs that render identically. Report the pairs on each tool and the delta.\n"
         "2. Test the four boundary cases of the pipeline: a valid UTF-8 character above U+07FF, a lone continuation "
         "byte, a surrogate already in the input (U+DC85 as text), and an empty cell. Say what each renders.\n"
         "3. Do not edit any lane file; import scratch copies only. Keep the probe under 300 s.",
         "The collision table (pairs identical on each tool), the boundary results, and the falsifiable verdict: does "
         "the r90 repair make exactly one pair go from identical to distinct, or more?",
         ),
    seat("S90ScoutSources", "scout",
         "Open the round's source and one reject candidate; verify the capture. OWN ONLY "
         f"{LANE}/.ufo/waves/round-90/w1/S90ScoutSources/.",
         "1. Fetch https://www.unicode.org/reports/tr14/ (and the line-break data file "
         "https://www.unicode.org/Public/UCD/latest/ucd/LineBreak.txt) into your scratch; record HTTP status, bytes, "
         "sha256 and compare both with census/round-90/srcs/. Report the capture's Unicode version, revision and "
         "date.\n"
         "2. Locate the quote the prereg uses; count its words; report its occurrence count. Also quote the data-file "
         "line for `0085` and say which class it names.\n"
         "3. Open ONE reject candidate: https://www.unicode.org/reports/tr13/ (Unicode Newline Guidelines) or the "
         "ECMA-48 PDF; decide whether it teaches something this lane may act on that UAX #14 does not, and give "
         "admit/reject with a reason and a flip condition.\n"
         "4. Run the lane's sources census: /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root "
         "/home/vgpnk/Projects/shokunin souji; report its exit code and row count.",
         "The fetch table (URL, HTTP, bytes, sha, capture match), the quote location/word count, the data-file line, "
         "the reject verdict with reason+flip, and the census line.",
         ),
    seat("S90Scribe", "scribe",
         "Drafts for the L1 to integrate (row, entry, criterion, lesson mistake). OWN ONLY "
         f"{LANE}/.ufo/waves/round-90/w1/S90Scribe/.",
         "1. Draft the 11-cell S353 SOURCES row in the registry schema (id, source with URL/capture/sha, kind docs, "
         "tier A, the named scope, anchor+located quote, teaches, status mined, opened 2026-11-08, recheck, used-by "
         "corpus/knowledge/nel-byte-character-pair.md). Verify the quote against the capture byte for byte and count "
         "its words with a pasted command.\n"
         "2. Draft corpus/knowledge/nel-byte-character-pair.md (<=35 lines): the byte/character distinction, why the "
         "surrogate path and the character path used to collide, the `\\u0085` spelling, the pair rule, and a Gate "
         "block with the URL, access date and <=25-word located quote. Cite S353, S348, S351.\n"
         "3. Draft the next QUALITY.md criterion (Q165) in the lane's style: a byte/character pair that decodes to "
         "the same value must have distinct spellings, and the pair is measured, not asserted.\n"
         "4. Draft `## Mistakes` for corpus/lessons/round-90.md: the r89 wave-evidence durability defect "
         "(reports/receipts left gitignored so the pushed tip could not resolve the pre-file ledger's artifacts), "
         "with class, evidence pointer, captured-by (the pre-file gate's artifact-existence check) and the fix.",
         "The row draft (with quote command+output), the entry draft, the Q165 draft and the mistake draft, each "
         "ready to paste with no placeholder text.",
         ),
    seat("S90Connector", "connector",
         "Sibling-overlap and prior-art scan; the bounded planning data-walk for the round's claim set. OWN ONLY "
         f"{LANE}/.ufo/waves/round-90/w1/S90Connector/.",
         "1. Search the lane's own history and corpus for prior statements of the NEL/0x85 rule and the malformed-"
         "ledger guard; say which round first recorded each and whether r90's evidence changes the disposition.\n"
         "2. Read the sibling lanes' QUALITY/SOURCES only where they are readable under /home/vgpnk/Projects/"
         " (read-only; never edit): does any sibling lane own the newline/escape rule or a ledger-malformed rule? "
         "Route contested scope explicitly.\n"
         "3. Planning data-walk (bounded): list the r91 candidates the r89 spot-check and the r90 prereg leave open "
         "(the spot-check's routed defects 1-11 and the r89 C1 carry list), each with its current status and the "
         "cheapest next measurement. Do not plan beyond r91.\n"
         "4. Dedup: name any finding of this wave's other seats you can see in their reports that duplicates a "
         "prior-round finding, and any locus the round does not attack.",
         "The overlap table (rule, first recorded, delta), the sibling-ownership verdict, the r91 candidate list, and "
         "the dedup/unattacked list.",
         ),
]


def main():
    print(json.dumps({"wave": "souji-r90-w1",
                      "milestone": "souji r90: C1 binds the r89 mutant set's last survivor (the malformed-ledger "
                                   "guard, LD2b on an absent id) (calibration); C2 spells U+0085 as \\u0085 (byte/"
                                   "char pair injective) and deletes dead _one_line (operability)",
                      "reportDir": ".ufo/waves/round-90/w1",
                      "context": CTX,
                      "items": ITEMS}, indent=1))


if __name__ == "__main__":
    main()
