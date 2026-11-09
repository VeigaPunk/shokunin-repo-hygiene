#!/usr/bin/env python3
"""Build the souji r92 wave-1 spec. Run: python3 .ufo/waves/round-92/build-spec.py > .ufo/waves/round-92/w1-spec.json
P1, P2 and F hashes are read from the lane's git branch (P1 = instruments, P2 = C1 control, F = the preregistration)."""
import json
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "5339b2ac79f81aa446f6a2cd4700321cf4982fd3"
W = f"{LANE}/.ufo/waves/round-92/w1"
SCR = "/fast/scratch/hyaku/souji-r92"

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


P1 = find("round-92: instruments")
P2 = find("round-92: C1 control")
F = find("round-92: preregistration")

C1_AFTER = ("python3 -B census/round-92/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py "
            "--harness census/round-92/c1-false-row-harness.py --population census/round-92/c1-false-rows.tsv "
            f"--lane . --fleet-root {FLEET} --work <empty> --jobs 4 --ids census/round-92/c1-targets.json")
C2_AFTER = ("python3 -B tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before "
            "census/round-92/controls/c2-before-tool.py --work <empty>")

CTX = f"""# Goal
souji round 92 (lane repo {LANE}, lane id souji). The L1 (SoujiR92a2) holds the planner seat and is the ONLY
integration owner: it froze the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 13 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion. All commands below run
with cwd {LANE} (use `cd {LANE} && ...`); every path is relative to {LANE} unless absolute.

# Frozen round (read {LANE}/census/round-92/preregistration.txt FIRST — it is the contract)
Lane base {BASE} (r91 closed; its non-author spot-check is corpus/lessons/round-91-verifier-spotcheck.md). P1 {P1}:
survivor search, r92 population + harness pin, the 47-target set, the C2 well-formed cut repair
(tools/souji-record-agreement.py), the r92 fixture, the forgery probe, C2 controls, the S355 capture. P2 {P2}: the C1
do-nothing control on the r91 population and the pre-freeze survivor census. F {F}: the preregistration alone. The
filed instruments are FROZEN: do not modify census/round-92/, tests/fixtures/, tools/ or corpus/ — copy what you
need into your own seat dir or scratch and write receipts in your seat dir. Nothing in the claim wording may be
widened by this wave; the wave's job is to FALSIFY it (Amendment 59: a claim verifies only if no artifact produced by
this round's own wave falsifies its STATED WORDING; numbers re-deriving is necessary, not sufficient).

Claims (verbatim targets; read the prereg for the full predicate, kill rule and stated limits):
- C1 calibration 7: a single-token mutation census of the frozen r87 counter (census/round-87/c1-pointer-counter.py,
  sha256 fd0a8e24...) generates 270 mutants; on the r91 63-row population 9 are ambiguous, 1 hangs, 260 are scored and 124 survive (no r91 row asserts exit code
  0 on success). ONE appended row LD4r (LD4 with expect_rc 0) in census/round-92/c1-false-rows.tsv (64 rows, sha256
  f66341fc...) kills the 47 survivors in census/round-92/c1-targets.json (sha256 5a8f6087...). Predicate: `{C1_AFTER}`
  prints `SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=47 survived=0` EXIT 0, and the
  pristine harness on the r92 population prints `SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0`
  with LD4r `rc=0 match=yes`, exit 0. Control: the same search with `--population census/round-91/c1-false-rows.tsv`
  prints `killed=0 survived=47`. Kill rule: a kill is a non-zero harness exit on that population. ONE harness run
  clones the lane fixture (~0.7 GB) and takes ~15 s; the search deletes each per-mutant tree once scored. Use
  --jobs 4 at most.
- C2 operability 8: the r91 tool moved the tail cut by the lead byte's structural length, so an ill-formed lead
  before the tail cut absorbed bytes of the next well-formed sequence (payloads A/B rendered one cell). The filed
  tool (sha256 fc0e35c2...) moves a cut only across ONE well-formed UTF-8 sequence (strict decode = every Unicode
  Table 3-7 row; S355). Predicate: `{C2_AFTER}` prints `SUMMARY cases=20 tool_pass=20 before_pass=16` EXIT 0; the
  forgery probe (python3 -B census/round-92/c2-forgery-probe.py --fixture tests/fixtures/r92-k4-flagfail.py --tool
  tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>) prints
  `FORGERY-SUMMARY forgeries=5 rejected=5 positive=pass` EXIT 0; the r87 K4 regression (python3 -B
  census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <empty>) prints `SUMMARY rows=12
  mismatches=0 errors=0` EXIT 0. Control: the r91 tool as both arms reads `tool_pass=16 before_pass=16` EXIT 1.

# Evidence durability and the pre-file ledger (Amendment 59)
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every argument, output line and falsifying reproducer you want the ledger to read must live under {W}/ (your seat
dir {W}/<your name>/ or your report). If an artifact of yours falsifies a sentence of either claim, say so plainly
in the report under a heading `FALSIFIES-WORDING` (or `FALSIFIES-NUMBER`) with the exact sentence and the
reproducer path; the L1 records it as an amendment in plans/round-92.md, never silently. If nothing falsifies, say
`NO-FALSIFICATION` with what you tried. Every `Report:` trailer path is relative to {LANE} — write it at
{LANE}/<that path>.

# Write scope and scratch
Write only under your own seat dir {W}/<your name>/ and your own report file. Read the lane read-only. Scratch
(clones, fixtures, counter --work dirs) lives under {SCR}/<your name>/; create it with mkdir -p and DELETE it before
you yield (trap 'rm -rf -- \"$S\"' EXIT in shell, finally: shutil.rmtree in Python), copying receipts (text only,
never clones) into your seat dir first. Keep your scratch under 20 GB: never hold more than 4 harness work trees at
once (the attempt-1 survivor search held 260 lane clones, 185 GB, and stalled the fleet). /tmp is for files under
50 MB only and is never citable evidence. Any git fixture is `D=$(mktemp -d -p {SCR}/<your name>)` + `git -C \"$D\"
init -q`, every later call names `-C \"$D\"`, and you assert `git -C \"$D\" rev-parse --show-toplevel` equals `$D`
before the first commit; never pass an empty or unchecked variable to `git -C` (it falls back to the fleet root and
has committed a stray file there, r70 incident). Do not run mutating git/jj anywhere else. Never mutate host
sysctls, never sudo, never spin CPU burners.

# Tooling authorization (operator, 2026-10-19)
You may install or upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels,
update-safety gate; record tool/version/channel/reason in your report). pacman transactions are PAUSED host-wide
until the operator resolves the host-recovery L0 question: install via `uv tool`/`npx`/an official binary in
~/.local/bin, or file an L0 question; before any future pacman -S run `pacman -Sp --print-format '%n %v' <pkgs>` and
never -Sy/-Syu/-U/-R. No tool install is needed for this round.

# Round shape
One v1 wave, 13 seats (policy band 8-16). Attack seats under the addendum's four-role definition: 2 reviewer +
critic + 2 mutation-tester = 5/13 = 38.5 % (>= 25 %); the prefile gate's broader ATTACK_ROLES set also counts the
connector and sentinel (7/13). 4 executors, 1 scribe, 1 scout, 1 connector, 1 sentinel. Residual calls: none. The
L1 holds the canonical planner seat (the validator rejects `planner`); the bounded planning data-walk rides the
connector seat.
"""


def seat(name, role, target, change, accept):
    body = f"# Target\n{target}\n\n# Change\n{change}\n\n# Acceptance\n{accept}\n\n"
    body = body.replace("{BASE}", BASE).replace("{FLEET}", FLEET).replace("{LANE}", LANE)
    return {"name": name, "role": role,
            "prompt": GOD + body + f"Report: .ufo/waves/round-92/w1/{name}.md\n"}


def own(name):
    return f"OWN ONLY {W}/{name}/ and {W}/{name}.md; scratch {SCR}/{name}/."


ITEMS = [
    seat("R92ExecC1Search", "executor",
         "Re-derive C1's after arm and control end to end on committed bytes, independently of the L1. " + own("R92ExecC1Search"),
         "1. Run the C1 after search (47 targets, r92 population) and the control (same targets, r91 population) "
         "into your scratch; save both receipts in your seat dir; quote both SEARCH-SUMMARY lines and exits.\n"
         "2. Run the pristine harness on the r92 population; quote the LD4 and LD4r lines and the SUMMARY and exit.\n"
         "3. Verify every pin: sha256 of the counter, the r92 harness, both populations, the targets file and the "
         "search tool against the prereg; `cmp -n` the r91 population against the r92 prefix; diff the r92 harness "
         "against census/round-91/c1-false-row-harness.py and classify every hunk (pin, docstring, UNEXPECTED).\n"
         "4. Check that every target id in c1-targets.json appears as `killed=no` in "
         "census/round-92/records/c1-search-r91-full.txt (the pre-freeze census) — a target the r91 population "
         "already killed would make the claim's 'survivor' wording false.",
         "Both SUMMARY lines with exits, the pristine LD4r line, the pin table, the harness hunk inventory, and the "
         "target-membership check (count of targets that were survivors). Name any mismatch to the prereg as HIGH.",
         ),
    seat("R92ExecC1Cause", "executor",
         "Attribute every C1 kill to its row: is LD4r the ONLY row each of the 47 targets now fails? " + own("R92ExecC1Cause"),
         "1. For at least 12 targets spread across counter lines (include a552c28, a574c11, h-exit-always-1, a214c12, "
         "a323c41, a468c44, a541c27), build the mutant counter in scratch (apply the target's `old`->`new` once to a "
         "copy of census/round-87/c1-pointer-counter.py) and run the r92 harness on the r92 population; record "
         "which ROW lines read match=no and the counter's ITEM lines that changed (which r77 item turned "
         "unresolved). Keep at most 2 harness work trees at once.\n"
         "2. If any target fails a row OTHER than LD4r on the r92 population, it would have failed the same row on "
         "r91 — report that as FALSIFIES-NUMBER (the control would not be 0).\n"
         "3. Classify each sampled kill: exit-polarity (the success return/test/tally inverted) or resolution "
         "(a different r77 item becomes UNRESOLVED/REFUSED so the run is not all-resolved). Stated limit (iii) says "
         "kills may come from any r77 item; check whether the C1 CLAIM sentence ('no r91 row asserts the counter's "
         "exit code 0 on a successful run') is the true reason for every sampled kill.",
         "A table target -> failing rows -> changed ITEM lines -> class, and an explicit verdict on whether LD4r is "
         "the sole killing row and whether the claim's stated reason holds.",
         ),
    seat("R92ExecC2Fixture", "executor",
         "Re-derive C2's after arms, control and forgery probe on committed bytes. " + own("R92ExecC2Fixture"),
         "1. Run the C2 fixture after arm, the control (the r91 tool census/round-92/controls/c2-before-tool.py as "
         "BOTH --tool and --before), the forgery probe, and the r87 K4 regression; save all four receipts; quote "
         "every CASE line, every FORGERY line, the SUMMARY lines and exits.\n"
         "2. Verify the pins: tool sha256 fc0e35c2..., before-arm 21e5c740... (= `git show {BASE}:tools/"
         "souji-record-agreement.py`), fixture 2c9bd76c....\n"
         "3. Diff the filed tool against the r91 tool and classify every hunk (cut helpers, docstrings, UNEXPECTED).\n"
         "4. Exercise the fixture's KFF13 self-check: run the fixture against a scratch copy of the tool that "
         "re-adds a spaced `def _one_line (x): return x` (must fail KFF13) and one whose docstring merely mentions "
         "`_one_line(` (must pass KFF13); quote both.",
         "Exact CASE/FORGERY/SUMMARY lines with exits, the pin table, the hunk inventory, and both KFF13 probe "
         "outcomes. Name any mismatch to the prereg as HIGH.",
         ),
    seat("R92ExecC2Sweep", "executor",
         "Test the repaired cut beyond the fixture's finite sweep. " + own("R92ExecC2Sweep"),
         "1. Import the filed tool in scratch (importlib from tools/souji-record-agreement.py) and expose "
         "`_one_line_bytes`, `_escape_text`, `_decode_record`, `_cut_head`, `_cut_tail`.\n"
         "2. Property check on at least 200,000 payloads (seeded random: lengths 201-260, bytes drawn from a mix of "
         "ASCII, valid 2/3/4-octet sequences, every Table 3-7 boundary (C2, DF, E0 A0, ED 9F, EE, F0 90, F4 8F), "
         "ill-formed leads C0 C1 F5 FF, overlongs E0 80, surrogates ED A0, truncated sequences): (a) raw byte "
         "length of the excerpt window <= 202, (b) the head is a prefix and the tail a suffix of "
         "`_escape_text(_decode_record(raw))`, (c) one physical line (no raw line separators, `str.splitlines()` "
         "gives one element), (d) the cut never moves across bytes that do not form a single strict-decodable "
         "character. Save the generator, seed, counts and every counterexample.\n"
         "3. Compare with the r91 tool on the same payloads (counterexample count).\n"
         "4. Time `_one_line_bytes` on a 1 MB payload and on 10,000 payloads; report any super-linear cost.",
         "Counts per property for both tools, every counterexample of the filed tool (or 'none in N'), and the "
         "timing. Any filed-tool counterexample to a claimed property is FALSIFIES-WORDING with a reproducer.",
         ),
    seat("R92MutC1", "mutation-tester",
         "Attack C1's kill rule and target set: false kills, alternative survivors, residual triage. " + own("R92MutC1"),
         "1. False-kill probe: the kill rule counts ANY non-zero harness exit. Build two mutants that break the "
         "counter without touching exit polarity (e.g. a syntax-valid edit that raises at import, an argparse "
         "rename) and show what the search and the harness report (rc 1 vs rc 2); say whether a crash would be "
         "scored killed, and check whether any of the 47 kills in the L1's after run is a crash (rc 2) rather "
         "than a row mismatch.\n"
         "2. Alternative edits of the SAME clauses the targets hit that still survive the r92 population: at least "
         "six hand edits around lines 541-552 and 574 (e.g. `ok = counts['resolved'] >= len(pop) - 1 and not "
         "unknown`, `return 0 if ok or forged else 1`, `counts['unresolved'] += 0`), scored with the r92 harness "
         "(at most 2 work trees at once). Each survivor needs a row shape or a named limit.\n"
         "3. Triage the 77 residual survivors (census/round-92/records/c1-residual-survivors.json): sort them into "
         "forge-path, output-only (SUMMARY text), argparse/env, likely-equivalent, and bindable-by-a-row; name the row "
         "shape for the bindable ones. Do not score all 77.",
         "The false-kill verdict, the alternative-edit table with scores, and the residual triage table. Anything "
         "that refutes a C1 sentence goes under FALSIFIES-WORDING.",
         ),
    seat("R92MutC2", "mutation-tester",
         "Attack C2's fixture with forgeries the probe does not carry. " + own("R92MutC2"),
         "Write at least eight one-edit forgeries of the FILED tool (copy it to scratch; never edit the lane) and run "
         "each through the r92 fixture with the r91 tool as --before. Required: (a) `_straddling_sequence` search "
         "window 3 instead of 4 bytes back; (b) strict decode replaced by a lead-byte range table missing the E0/ED/"
         "F0/F4 second-byte restrictions; (c) decode with `surrogatepass`; (d) `len(...) == 1` relaxed to `>= 1`; "
         "(e) head cut moved forward instead of back; (f) tail cut moved back instead of forward; (g) end range off "
         "by one (`min(start + 3, ...)`); (h) the repro-pair special case keyed on the cell text. For each: rc, "
         "tool_pass/cases, failing cases. Every SURVIVING forgery (rc 0) is a gap: give the payload that "
         "distinguishes it from the filed tool and say which clause of C2's wording it falsifies, if any.",
         "A forgery table (edit, rc, tool_pass, failing cases) and, for each survivor, a distinguishing payload and a "
         "verdict under FALSIFIES-WORDING or 'limit (ii) covers it'.",
         ),
    seat("R92ReviewerC1", "reviewer",
         "Falsify C1's stated wording on committed bytes. " + own("R92ReviewerC1"),
         "1. Re-derive the after and control SEARCH-SUMMARY lines yourself (independent runs, --jobs 4) and quote "
         "them.\n"
         "2. Sentence by sentence: are 260 mutants scored and 124 alive on the r91 population (read "
         "census/round-92/records/c1-search-r91-full.txt; recount the SEARCH lines yourself)? Is 'no r91 row "
         "asserts the counter's exit code 0 on a successful run' true (grep every r91 row's expect_rc)? Is LD4r "
         "exactly LD4 with expect_rc 0? Is the r91 prefix byte-identical? Is the counter unchanged? Is the "
         "harness change only a pin and a docstring?\n"
         "3. Read the search tool: does `gen` enumerate what the prereg says (comparison flips, and/or, `not` "
         "deletion, True/False, 0/1, two hand edits)? Does `--ids` refuse unknown ids? Does `ambiguous` vs "
         "`uncompiled` reporting match its docstring?\n"
         "4. Write FALSIFIES-WORDING rows for every sentence you can refute, with the artifact path.",
         "Independent SUMMARYs, a sentence table (holds / neutral / falsifies-wording), the search-tool reading, and "
         "the explicit falsification list.",
         ),
    seat("R92ReviewerC2", "reviewer",
         "Falsify C2's stated wording on committed bytes. " + own("R92ReviewerC2"),
         "1. Re-derive the fixture after arm, the control and the forgery probe; quote SUMMARYs and exits.\n"
         "2. Rebuild payloads A and B (210 bytes: a*110 + F0 80 61 C2 85 + b*95 and a*110 + F0 80 61 62 85 + b*95) "
         "and show, byte by byte, where the r91 tool's tail cut lands and where the filed tool's lands; quote both "
         "cells for both payloads.\n"
         "3. Read `_straddling_sequence`: is 'the candidate bytes must decode strictly to exactly one character, "
         "which applies every Table 3-7 row' true? Check each Table 3-7 row and the ill-formed classes (C0/C1, "
         "F5..FF, E0 80..9F, ED A0..BF, F0 80..8F, F4 90..BF, missing continuation) against Python's strict "
         "decoder with a small script.\n"
         "4. Read KFF13-KFF18 and the KFF13 self-check: does each case test what the prereg says it tests? Could "
         "any pass for a tool that does not have the claimed property?\n"
         "5. Write FALSIFIES-WORDING rows for every sentence you can refute, with the artifact path.",
         "Independent SUMMARYs, the A/B byte derivation, the Table 3-7 decoder table, a case-by-case reading, and "
         "the explicit falsification list.",
         ),
    seat("R92Critic", "critic",
         "Attack both claims' wording, controls and certifying power. " + own("R92Critic"),
         "1. Do-nothing reach: can any no-work run reach either predicate? (C1: score the targets on the r91 "
         "population; C2: the r91 tool on the r92 fixture.) Quote the numbers from the committed controls and "
         "re-run one of them.\n"
         "2. Target selection: the 47 targets were chosen AFTER a feasibility run on the r92 population "
         "(census/round-92/controls/c1-feasibility-r92-prefreeze.txt). Is a claim whose target set is defined as "
         "'what the new row kills' falsifiable at all? State what result would have refuted it, and whether the "
         "claim says anything beyond its own construction (compare with the residual 77).\n"
         "3. Separability: run the C1 after arm with the r91 tool restored in a scratch copy of the lane (C2 not "
         "landed) and the C2 after arm with the r91 population (C1 not landed); each must still reach its own "
         "target.\n"
         "4. Axis naming: is C1 calibration (does it count a mismatch between the lane's self-assessment and repo "
         "state) or quality/coverage? Is C2 operability? Cite AXES.md ({FLEET}/AXES.md) and the lane SCORECARD.",
         "No-work numbers, the falsifiability verdict for C1's target construction, both separability runs, and the "
         "axis-naming verdict. Refutations go under FALSIFIES-WORDING.",
         ),
    seat("R92Sentinel", "sentinel",
         "Robustness and safety of the C2 tool change and the C1 search tool. " + own("R92Sentinel"),
         "1. Feed `_one_line_bytes` adversarial stderr: 10 MB of continuation bytes, 10 MB of F4 8F BF BF, NUL "
         "runs, lone surrogates' encodings, a payload that is exactly 200/201/202/203 bytes; report exceptions, "
         "time, and whether the cell stays one line and <= the bound.\n"
         "2. Injection: can a crafted stderr make the K4 record carry a second MISMATCH line, a tab, or a raw CR/LF/"
         "NEL/U+2028 through the new cut path? Use the public path (fixture-style hermetic run) where you can.\n"
         "3. The survivor search: does it ever write outside --work, follow symlinks out of it, leave clones behind "
         "on a killed run, or accept a --work under /tmp? Check the per-mutant cleanup by running it with --ids on "
         "two targets and measuring `du -s` of --work after.\n"
         "4. Scratch discipline: list any path the filed instruments write under /tmp regardless of TMPDIR/--work.",
         "A findings list (HIGH/MEDIUM/LOW) with reproducers, or an explicit 'no finding' per item with what was "
         "tried. Anything that refutes a claim sentence goes under FALSIFIES-WORDING.",
         ),
    seat("R92Connector", "connector",
         "Cross-claim and cross-lane pattern scan, plus the planning data-walk the L1's planner seat delegates. " + own("R92Connector"),
         "1. Sibling overlap: grep the fleet's sibling lane repos under {FLEET}/*-shokunin/ (read-only) for UTF-8 "
         "window/excerpt cutting, `surrogateescape` excerpt helpers or mutation-census harnesses; say whether any "
         "sibling owns this surface or already solved it, with paths.\n"
         "2. Cross-claim pattern: C1's gap (no row asserts rc 0 on success) and C2's gap (a cut trusted a lead "
         "byte's declared length) are both 'an instrument asserted the shape, not the success/whole'. Search the "
         "lane's census/round-8*/ and round-9*/ instruments for other rows/cases that assert a marker but no exit "
         "code, or a structural length without validation; list them with paths.\n"
         "3. Planning data-walk: read SCORECARD.md `### Planned (r92)` and the r91 spot-check's routed items 1-5; "
         "mark each as answered by this round (cite the file), partly answered, or carried; draft the `### Planned "
         "(r93)` bullet list.\n"
         "4. RFC 3629 §4 vs Unicode Table 3-7: open {LANE}/census/round-91/srcs/rfc3629.txt §4 (UTF8-octets ABNF) "
         "and the r92 Unicode capture; say whether they define the same well-formed set (the r91 spot-check routed "
         "item 4 asked to ground range checks on §4 syntax).",
         "Overlap verdict with paths, the pattern list, the routed-item table and the r93 draft, and the §4-vs-"
         "Table-3-7 verdict with quoted lines.",
         ),
    seat("R92ScoutSources", "scout",
         "Re-open the round's source and propose the reject sample. " + own("R92ScoutSources"),
         "1. Fetch https://www.unicode.org/versions/latest/core-spec/chapter-3/ live (curl -sSL, record HTTP code, "
         "final URL, byte size, sha256) into your scratch; compare with census/round-92/srcs/unicode-ch3.html "
         "(`cmp`).\n"
         "2. Verify the S355 row in corpus/SOURCES.md: the quoted sentence 'Ill-formed code unit subsequences do not "
         "overlap with minimal well-formed code unit subsequences.' — word count, occurrence count in the "
         "whitespace-normalized tag-stripped text, the section it sits in (D86?), and that anchor `id=\"G7404\"` "
         "is Table 3-7. Check the row parses as 11 cells and carries no `|` inside a cell.\n"
         "3. Read the knowledge entry corpus/knowledge/utf8-window-well-formed-cut.md against the source: is every "
         "Table 3-7 fact it states (C0/C1/F5..FF never lead; E0 A0..BF; ED 80..9F; F0 90..BF; F4 80..8F) exactly "
         "what the table says? Quote the table rows.\n"
         "4. Propose ONE reject sample from the same chapter or an adjacent source (e.g. §3.9 U+FFFD substitution "
         "of maximal subparts, Table 3-8..3-11) with a <=25-word located quote, the reason it grounds nothing this "
         "round claims, and a flip condition.",
         "Fetch receipt and cmp verdict, the row check, the entry-vs-table check with quoted rows, and the reject "
         "sample (URL, access date, quote, locator, reason, flip condition).",
         ),
    seat("R92Scribe", "scribe",
         "Draft the round lesson's Mistakes and the QUALITY criterion from evidence. " + own("R92Scribe"),
         "1. Mine mistakes into a draft `## Mistakes` block (format: class · evidence pointer · captured-by · fix; a "
         "fix counts only once shown able to fail). Candidates to verify from evidence: (a) attempt 1's survivor "
         "search held every per-mutant lane clone (260 x ~0.7 GB = 185 GB on /fast; orchestrator message; the "
         "search now deletes each tree — show the fix can fail by naming the check that would catch a regression); "
         "(b) the discarded NF1r draft row (census/round-92/controls/nf1r-draft-probe.txt): a row whose expectation "
         "the harness encodes differently than its column suggests; (c) r91 M3/A2: an instrument trusted a lead "
         "byte's declared length (corpus/lessons/round-91.md). Read the files; do not invent evidence.\n"
         "2. Draft one QUALITY.md criterion (next free Q number after the last in corpus/QUALITY.md) that would have "
         "caught (a) or (b), phrased as a checkable rule with a counting command.\n"
         "3. Draft the `## Gate` block skeleton for S355 (URL, access date 2026-11-08, quote, locator) and leave the "
         "reject-sample slot for the scout's proposal.",
         "Draft text blocks (Mistakes, QUALITY criterion, Gate skeleton) in your report, each line carrying its "
         "evidence path.",
         ),
]


def main():
    print(json.dumps({"wave": "souji-r92-w1",
                      "milestone": "souji r92: C1 one exit-polarity row kills 47 of the 124 survivors of a single-token "
                                   "mutation census (calibration); C2 the excerpt cut moves only across a well-formed "
                                   "UTF-8 sequence, Table 3-7 (operability)",
                      "reportDir": ".ufo/waves/round-92/w1",
                      "context": CTX,
                      "items": ITEMS}, indent=1))


if __name__ == "__main__":
    main()
