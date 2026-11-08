#!/usr/bin/env python3
"""Build the souji r89 wave-1 spec. Run: python3 .ufo/waves/round-89/build-spec.py > .ufo/waves/round-89/w1-spec.json
P and F hashes are read from the lane's git branch (P = instruments + controls + before receipts, F = prereg alone)."""
import hashlib
import json
import os
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "a2cef94a"

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


def sha(rel):
    with open(os.path.join(LANE, rel), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


log = git("log", "--format=%H %s", "-12", "master").splitlines()


def find(prefix):
    for line in log:
        h, _, s = line.partition(" ")
        if s.startswith(prefix):
            return h
    return "<" + prefix + ": not found yet>"


P = find("round-89: instruments")
F = find("round-89: preregistration")
CTX = f"""# Goal
souji round 89 (lane repo {LANE}, lane id souji). The L1 (SoujiR89) holds the planner seat and is the ONLY
integration owner: it froze the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 12 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every `Report:` trailer path is relative to {LANE} — write it at {LANE}/<that path>.

# Write scope and scratch
Write ONLY under {LANE}/.ufo/waves/round-89/w1/<YourSeatName>/ and your report file. Everything else in the lane is
read-only to you. All clones, mirrors, fixtures and counter `--work` dirs live under
/fast/scratch/hyaku/souji-r89/<YourSeatName>/ (mkdir -p; never /tmp). Delete your scratch dir before you yield
(`trap 'rm -rf -- "$S"' EXIT`), copying receipts into your seat dir first. Disclose any scratch you left behind.

# Frozen round (read {LANE}/census/round-89/preregistration.txt FIRST — it is the contract)
Lane base a2cef94a (r88 closed; spot-check corpus/lessons/round-88-verifier-spotcheck.md). P {P}: instruments,
populations, mutants, controls and the before receipts. F {F}: the preregistration alone (frozen before any
after-data). Nothing in the claim wording may be widened by this wave; the wave's job is to FALSIFY it (Amendment 59:
a claim verifies only if no artifact produced by this round's own wave falsifies its STATED WORDING; numbers
re-deriving is necessary, not sufficient).

Claims (verbatim targets; read the prereg for the full predicate, kill rule and stated limits):
- C1 calibration 7: on the frozen 57-row population census/round-89/c1-false-rows.tsv (the r88 53 rows byte-for-byte
  plus NF6h/NF6i at fixture revision R12 and LD1b/LD2), the r89 clause battery reports the UNCHANGED r87 counter
  green on both pinned populations and kills all SIXTEEN mutants (census/round-89/c1-mutants.json):
  killed_r88=12, killed_r89=16, killed_total=28, EXIT 0; the do-nothing control on the r88 53-row population alone
  kills twelve and leaves m18b-alnum-before, m17b-target-keyed, m17c-no-malformed and m18d-first-only alive.
  Command (after): python3 -B census/round-89/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py
  --work DIR --only r88,r89 --expect-killed 28 ; (before): the same with --only r88 --expect-killed 12.
- C2 operability 8: tools/souji-record-agreement.py's FLAGFAIL branch decodes base64 with surrogateescape and bounds
  RAW bytes first (head-100 / tail-99) before escaping, so the detail is injective on the bytes and the head carries
  content. The frozen 10-case fixture tests/fixtures/r89-k4-flagfail.py reports cases=10 tool_pass=10 before_pass=8,
  EXIT 0; the r88 tool bytes census/round-89/controls/c2-before-tool.py pass eight (failing KFF6/KFF8).
  Command: python3 -B tests/fixtures/r89-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-89/controls/c2-before-tool.py --work DIR
  (before arm: the same fixture with the r88 tool as BOTH --tool and --before).

Instrument hashes (re-measure them; a mismatch is a finding):
  c1-false-rows.tsv        {sha('census/round-89/c1-false-rows.tsv')} (57 rows)
  c1-mutants.json          {sha('census/round-89/c1-mutants.json')} (16 members)
  c1-mutants-dead.json     {sha('census/round-89/c1-mutants-dead.json')} (13 members, m19 is the belt)
  c1-false-row-harness.py  {sha('census/round-89/c1-false-row-harness.py')}
  c1-clause-battery.py     {sha('census/round-89/c1-clause-battery.py')}
  c1-pointer-counter.py    {sha('census/round-87/c1-pointer-counter.py')} (UNCHANGED r87 bytes)
  c1-items.tsv             {sha('census/round-87/c1-items.tsv')} (UNCHANGED r87 bytes)
  r89-k4-flagfail.py       {sha('tests/fixtures/r89-k4-flagfail.py')}
  tools/souji-record-agreement.py {sha('tools/souji-record-agreement.py')}
  controls/c2-before-tool.py {sha('census/round-89/controls/c2-before-tool.py')} (r88 tool bytes)

# Round-88 debts this round answers (do not re-declare them as new)
- (C1) S88MutCounter F1-F4 carried four named clause families with the exact row each would bind them by (NF6h, LD1b,
  LD2, NF6i). This round row-binds all four and names the spelling each covers. Five spellings stay carried:
  p2 basename granularity, p3 the punctuation lookahead, p7 `_regular`'s symlink leg, p8 `token_ok`'s hyphen
  marker, and the `fleet:` symlink leg.
- (C2) S88Sentinel F1 (injectivity lost on the composed decode+escape pipeline, MEDIUM) and F2 (25 leading control
  bytes consume the escaped head, LOW–MEDIUM). This round bounds raw bytes first and decodes with `surrogateescape`.
  F3 (forged-`CLEAN` fail-open, inherited) and F4 (`_stderr_tail` sibling branches, inherited) stay carried.
- r88 spot-check routed defects: fleet report attribution (kagi-shokunin 5c10e33d) — the lane should land its report
  through a lane-attributed path; S349 word-count self-correction (documentation, verified, no action); launch-
  workdir convention (receipts do not name the workdir — cosmetic).

# Tooling authorization (operator, 2026-10-19)
You and every seat may install or upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first
(official channels, update-safety gate, record tool/version/channel/reason). PACMAN GUARD (orchestrator ruling,
2026-10-20): all pacman transactions are PAUSED host-wide; install via `uv tool`/`npx`/an official binary in
~/.local/bin, and never -Sy/-Syu/-U/-R or restart a host service. Never mutate host sysctls.

# Fixture hygiene (run-6 incident)
Any fixture repo: D=$(mktemp -d) under your scratch root && git -C "$D" init -q, and every later git/jj call names
-C "$D" explicitly; assert `git -C "$D" rev-parse --show-toplevel` equals $D before the first commit. Never pass an
empty variable to git -C. Never run `git commit`/`jj` with a throwaway identity outside $D. A seat that writes no code
may skip this.

# Fleet rules
Never message agent://all (it reaches every lane's seats) — message the L1 by id: SoujiR89. Do not signal, kill or
reap processes you did not start. Do not run `git fetch`/`push` anywhere. Read-only git in the lane is fine, but
under jj colocation HEAD is detached: read the tip with `git rev-parse refs/heads/master`, never @{{u}} or HEAD.
"""


def seat(name, role, target, change, accept):
    return {"name": name, "role": role,
            "prompt": GOD + f"# Target\n{target}\n\n# Change\n{change}\n\n# Acceptance\n{accept}\n\n"
                            f"Report: .ufo/waves/round-89/w1/{name}.md\n"}


ITEMS = [
    seat("S89ExecC1", "executor",
         "Re-derive BOTH C1 arms and the belt end to end on committed bytes, independently of the L1. OWN ONLY "
         f"{LANE}/.ufo/waves/round-89/w1/S89ExecC1/.",
         "1. Run the after, before and belt commands from the context into your scratch; save all three receipts.\n"
         "2. For EACH new row — NF6g (m18) and LD1 (m17) — drive the pristine counter and the corresponding mutant "
         "by hand through census/round-89/c1-false-row-harness.py (importable) on your own fixture clone and record "
         "got/why for both, so the kill is attributable to that row and no other. For LD1 also run the counter with "
         "the SAME duplicate ledger but no mutant and show `LEDGER-REFUSED id=P01` + exit 1.\n"
         "3. Diff census/round-89/c1-false-row-harness.py, c1-clause-battery.py and c1-mutants.json against their "
         "r87 predecessors; list every changed line and flag any line that is not the pin, the R11 fixture block, "
         "the `where=ledger` row type, a mutant or a docstring.\n"
         "4. Re-derive the belt: run the 13-member file and report m19-len-half's per-set verdict; if it is killed, "
         "the belt sentence in the prereg is falsified — say so as a HIGH finding.",
         "Verdict per arm with exact SUMMARY lines, the per-row attribution table (row -> clause -> mutant -> sole "
         "killer yes/no), the instrument-diff list with unexpected lines flagged, and the belt result.",
         ),
    seat("S89ExecC2", "executor",
         "Re-derive BOTH C2 arms and attack the new FLAGFAIL detail for regressions. OWN ONLY "
         f"{LANE}/.ufo/waves/round-89/w1/S89ExecC2/.",
         "1. Run the C2 command from the context (after) and the same fixture with the r87 tool as both arms "
         "(before); save both receipts.\n"
         "2. Regression: run the r87 12-row counter `python3 -B census/round-87/c2-k4-counter.py --tool "
         "tools/souji-record-agreement.py --work <scratch>` — it must still be rows=12 mismatches=0 errors=0 EXIT 0; "
         "report any row that moves.\n"
         "3. Attack the new leg in YOUR OWN scratch copy of the fixture (never edit the lane's): a 4000-byte stderr, "
         "a stderr that is not valid UTF-8 (e.g. b'\\xff\\xfe'), a stderr carrying only U+2029, a bootstrap forged "
         "to print a non-base64 FLAGFAIL payload (does the parent fail closed?), and a forged writer that prints its "
         "own fake `WRITER` line. For each, report the K4 detail and whether it is one physical line.\n"
         "4. Check the excerpt arithmetic: for a 400-character line, is the rendered excerpt exactly the head 100 + "
         "… + tail 99, and is the whole K4 cell still one line?",
         "Verdict per arm, the r87-counter regression line, the five attack results with exact detail cells, and "
         "the excerpt arithmetic check.",
         ),
    seat("S89MutCounter", "mutation-tester",
         "Attack the new population and mutant set: is each new row load-bearing, does it bind more than one "
         f"spelling, and what else is reachable but unrowed? OWN ONLY {LANE}/.ufo/waves/round-89/w1/S89MutCounter/.",
         "1. Reproduce the after and before arms.\n"
         "2. For m17 and m18 write at least one DIFFERENT single edit of the same clause (not the filed text) and "
         "score it on both populations. A second edit that survives both means the row binds only one spelling; say "
         "which spelling.\n"
         "3. Probe the four carried survivors (p2 basename granularity, p3 the punctuation lookahead, p7 "
         "`_regular`'s symlink leg, p8 `token_ok`'s hyphen marker) on the r88 population and report each verdict; a "
         "survivor not named in the prereg's limits is a HIGH finding.\n"
         "4. Attack NF6g: can another declaration shape satisfy it (the token preceded by each PATHCH class, the "
         "token at line start, the token after a tab)? And LD1: does a duplicate id with the SAME class/target still "
         "fail closed, and does a 3-column malformed row take the same path?",
         "Table: edit, killed on r87, killed on r88, classification, and the row that would bind it. Name every "
         "survivor not already carried in the prereg's limits.",
         ),
    seat("S89Scribe", "scribe",
         "Drafts for the L1 to integrate. OWN ONLY "
         f"{LANE}/.ufo/waves/round-89/w1/S89Scribe/.",
         "1. Draft the `## Gate` row for S348 (Python str.splitlines) in the registry schema used by the newest "
         "corpus/SOURCES.md rows: id, title+URL, class docs, tier A, the named scope, the capture path+sha256, a "
         "<=25-word located quote with its anchor, status `mined`, recheck, used-by. Verify the quote against the "
         "capture byte for byte and count its words with a pasted command.\n"
         "2. Draft one knowledge section (<=35 lines) for corpus/knowledge/: 'a diagnostic cell is one escaped "
         "line' — which characters a str.splitlines reader breaks on, why the escape is applied to the text and not "
         "only to the path, and the both-ends bound. Cite S348 and the lane's own r87 entry.\n"
         "3. Draft one QUALITY.md criterion in the lane's numbering style (next free Q): a delegated failure detail "
         "must be one escaped line and keep the head; a tail-only excerpt that drops an exception's type name is a "
         "defect.\n"
         "4. Do not edit any committed file; deliver drafts as files in your seat dir.",
         "Three draft files + a quote-verification receipt (capture line, quote, byte-check command and output) and "
         "the word count.",
         ),
    seat("S89ScoutSources", "scout",
         "Open the source C2 rests on, THIS ROUND, with URL + access date + a located quote of <=25 words. OWN "
         f"ONLY {LANE}/.ufo/waves/round-89/w1/S89ScoutSources/.",
         "1. Read corpus/SOURCES.md for the contract shape and the highest existing id (the r87 lesson says S347 is "
         "the last admit).\n"
         "2. Open https://docs.python.org/3/library/stdtypes.html#str.splitlines (or the /3.14/ page the host "
         "interpreter matches) live: record HTTP status, byte count, sha256 and a capture under "
         "census/round-89/srcs/. Give the anchor, the rendered text and a <=25-word quote naming the line "
         "boundaries a str.splitlines reader breaks on (LF, CR, CRLF, VT, FF, FS/GS/RS, NEL, LS, PS).\n"
         "3. Check duplicate URLs/scopes against the registry: stdtypes.html rows already exist (S061, S105); state "
         "whether this row's scope is distinct and cite the existing rows' scopes.\n"
         "4. Open one more page you judge load-bearing and propose exactly ONE reject with its flip condition "
         "(candidates: base64 module docs for the frame; subprocess docs for the child's stderr; pathlib for the "
         "single-line record rule). Give the same treatment.",
         "A candidates file with, per row: id, title, url, access date, tier, class, status, used-by, anchor, quote "
         "(<=25 words), admit/reject + reason, duplicate-URL check; plus the capture sha256 and the word count.",
         ),
    seat("S89Connector", "connector",
         "Sibling-overlap, separability and carry audit for round 88. OWN ONLY "
         f"{LANE}/.ufo/waves/round-89/w1/S89Connector/.",
         "1. Separability: prove or falsify that C1 (census/round-89/c1-* + census/round-87/c1-pointer-counter.py) "
         "and C2 (tools/souji-record-agreement.py + tests/fixtures/r89-k4-flagfail.py + the controls) are each "
         "verifiable without the other having landed — run each after-arm in a scratch clone with the other's "
         "change absent.\n"
         "2. Carry audit: take plans/round-87.md A4/A10 (seven carried clauses + six deletion dispositions), the "
         "r87 spot-check's routed defects D4/D6 and its three carried limits (corpus/lessons/"
         "round-87-verifier-spotcheck.md), and the r86 routed debts; say for each: answered this round (pointer), "
         "carried (where recorded), or missed (a finding).\n"
         "3. Sibling overlap: do kagi/mori/tsukuroi/tameshi provinces touch either surface (writer delegation, "
         "stderr diagnostics, duplicate-id registries)? Cite the sibling files you read; absorb nothing.\n"
         "4. Prior-art: grep tools/ and census/ for an existing implementation of `_one_line`, the base64 frame and "
         "the duplicate-ledger row; a duplicate implementation is a finding.",
         "Three sections (separability with receipts, carry table one row per item, overlap with citations) plus the "
         "prior-art grep table.",
         ),
    seat("S89Reviewer", "reviewer",
         "Independent re-derivation of both claims on committed bytes, plus chronology and instrument binding. OWN "
         f"ONLY {LANE}/.ufo/waves/round-89/w1/S89Reviewer/.",
         "1. Re-run both frozen commands yourself (all four ends: C1 after/before/belt; C2 after/before) in your "
         "own scratch and report each exact SUMMARY line and exit code.\n"
         "2. Chronology: read the lane branch log and say whether P (instruments+controls+before receipts) and F "
         "(prereg alone) precede every after receipt's commit; check the prereg's file set in F is exactly one "
         "file. A pre-freeze after run filed as evidence is a finding (disclose only).\n"
         "3. Instrument binding: sha256 every instrument named in the prereg's hash list and compare; report any "
         "mismatch and any instrument the prereg names but does not hash.\n"
         "4. Do-nothing check: confirm from the before receipt that the control's kill count (10) is strictly below "
         "the after target (22), and that the two carried clauses (m17/m18) are the only survivors there.",
         "Per-end table (command, observed SUMMARY, exit, verdict AGREE/DISAGREE), the chronology result, the hash "
         "table, and the control check.",
         ),
    seat("S89Critic", "critic",
         "Falsify the WORDING of both claims before the round files them. OWN ONLY "
         f"{LANE}/.ufo/waves/round-89/w1/S89Critic/.",
         "1. C1 attacks: (a) the sentence says the battery 'kills all twelve'; LD1's kill depends on a row TYPE the "
         "harness gained this round — is that a kill of the counter's clause or of the harness's new code? (b) The "
         "belt says m19 'survives both sets' — does it survive because the clause is dead or because no row reaches "
         "it, and does the prereg's sentence claim the stronger of the two? (c) 'the frozen r87 counter, UNCHANGED' "
         "— verify byte identity and whether the population-only change makes C1 a coverage claim mislabelled as "
         "calibration. (d) Does NF6g's row bind the before-byte half or merely the `_declared` call order?\n"
         "2. C2 attacks: (a) the detail is 'at most 200 characters' — the excerpt is 200 but the K4 CELL is longer; "
         "is the sentence true as written? (b) 'keeps both ends' — the middle is lost; is that stated? (c) Does the "
         "base64 frame change what a forged writer can inject? (d) Is 'ONE escaped physical line' true for the "
         "whole K4 record, including a detail carrying the `…` marker and the prefix/suffix?\n"
         "3. For every falsified wording, name a NARROWING sentence the L1 can record in plans/round-88.md, or the "
         "honest stop that withdraws it. Do not edit the prereg.",
         "Attack table: claim, sentence, artifact/repro, verdict PASS/NARROW/WITHDRAW, and the exact narrowing "
         "sentence for each NARROW.",
         ),
    seat("S89Sentinel", "sentinel",
         "Adversarial security review of the FLAGFAIL re-framing and the duplicate-ledger row as privilege "
         f"boundaries. OWN ONLY {LANE}/.ufo/waves/round-89/w1/S89Sentinel/.",
         "1. Read the repaired truth_refusal/bootstrap, `_one_line`, `_escape_text` and the FLAGFAIL branch in "
         "tools/souji-record-agreement.py. Enumerate what a writer beside the tool can make the parent print: a "
         "forged `WRITER` line (can it name bytes that did not run?), a FLAGFAIL payload of invalid base64, a "
         "payload that decodes to 10 MB, a payload with a raw U+2028 after decoding, and a payload that is valid "
         "base64 but not UTF-8. For each, build a stub writer and report the K4 detail and whether it is one line.\n"
         "2. Check the parent's order: the WRITER line is stripped before any branch; a FLAGFAIL payload beginning "
         "`WRITER ` cannot impersonate; the base64 decode is bounded by what the child printed. Say what a forged "
         "writer can still achieve inside the prereg's stated limit (a writer inside the audited tree is outside "
         "the claim, S85Sentinel F5).\n"
         "3. LD1: read the counter's `_ledger` and the harness's duplicate-ledger builder. Can a duplicate id make "
         "the counter resolve an item it should refuse? Can the harness write outside its --work? Report the "
         "fail-closed properties and any finding with a reproducer.",
         "Per-probe table (probe, detail, one-line yes/no, fail-closed yes/no), the parent-order check, and the LD1 "
         "fail-closed verdict.",
         ),
    seat("S89Simplifier", "simplifier",
         "Dead-arm and duplication audit of the r88 instruments, with verified deletion patches. OWN ONLY "
         f"{LANE}/.ufo/waves/round-89/w1/S89Simplifier/.",
         "1. Test by deletion in YOUR OWN scratch copies (never the lane files): the harness's `where=ledger` "
         "`cls`/`target` columns (ignored for that row type — a belt?), `RESOLVING_NOT`'s use for the ledger "
         "branch, the battery's `--mutants`/`--expect-killed` defaults, and `_one_line`'s duplication of "
         "`_stderr_tail`'s bound (should one call the other?).\n"
         "2. For each deletion, score the frozen commands (C1 after/before, C2 after/before) and report pristine "
         "green/red and pass counts. A deletion that keeps every command's numbers unchanged is behaviour-"
         "preserving on the frozen inputs.\n"
         "3. Say which you would land, which you would keep as belts, and why; supply the exact diff for the dead "
         "ones. Do not apply anything to the lane.",
         "Table: deletion, C1 after/before, C2 after/before, verdict (dead / belt / load-bearing), and the "
         "recommended diff for the dead ones.",
         ),

    seat("S89Distiller", "reviewer",
         "Deduplicate the wave's findings against the claims and prior rounds. OWN ONLY "
         f"{LANE}/.ufo/waves/round-89/w1/S89Distiller/.",
         "1. Read the preregistration and the plans/round-89.md amendments as they appear.\n"
         "2. For every finding a sibling seat reports (mutant survivors, sentinel probes, critic narrowings), say which prior round already recorded it and whether this round's evidence changes its disposition.\n"
         "3. Name any finding that duplicates another seat's finding, and any locus this round's seats never attacked.\n",
         "A dedup table (finding, first recorded in, disposition, this round's delta) and the unattacked-loci list.",
         ),
    seat("S89Labrat", "revenger",
         "Bounded empirical probe for one falsifiable hypothesis: the `_whole` loop's second-occurrence claim. OWN ONLY "
         f"{LANE}/.ufo/waves/round-89/w1/S89Labrat/.",
         "1. Take the counter's `_whole` function and drive it with synthetic (needle, line) pairs in YOUR scratch:\n"
         "   the NF6i shape (first occurrence non-whole, later whole), the NF6h shape (slash predecessor), and the m18d\n"
         "   mutant's view (first-occurrence-only). Report for each pair whether pristine `_whole` agrees with the\n"
         "   population row's expectation and whether the mutant disagrees. One falsified pair is a finding: name it.\n"
         "2. Do NOT edit any lane file; test the counter by importing a scratch copy.\n",
         "A probe table (pair, pristine agrees yes/no, mutant agrees yes/no) and the falsifiable verdict.",
         ),
]


def main():
    print(json.dumps({"wave": "souji-r89-w1",
                      "milestone": "souji r89: C1 binds the two r87-carried unrowed clauses (NF6g before-byte, LD1 "
                                   "duplicate ledger) and re-measures the third dead as a belt (calibration); C2 "
                                   "makes the K4 FLAGFAIL detail one escaped line that keeps both ends "
                                   "(operability)",
                      "reportDir": ".ufo/waves/round-89/w1",
                      "context": CTX,
                      "items": ITEMS}, indent=1))


if __name__ == "__main__":
    main()
