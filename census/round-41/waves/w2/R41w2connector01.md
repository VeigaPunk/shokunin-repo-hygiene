# R41w2connector01 — cross-claim and adjacency re-scan of the landed round-41 state

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin, tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f (clean `git status`).
Role: connector, read-only. Mutations ran only in scratch clones (`git clone --shared`, toplevel asserted, identity via env), removed afterwards. Receipts: `.ufo/waves/round-41/w2/R41w2connector01/receipts/connector-probes.sh` (script) and `connector-probes.txt` (its captured output, re-run at tip).

## Pinned bytes (sha256, observed)
- tools/souji-worktree-drift.py b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 (matches the prereg pin; unchanged by the landing)
- tools/souji-freeze-check.py 3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b
- census/round-41/c1-counter.py 8860dc7a…, c2-counter.py 85ffe263…, c3-counter.py 9ef99e8f…, r1-counter.py 8352eed4…, c2-cases.tsv 4854335a…, c3-sites.tsv be363c0d…, c1-items.tsv 2d2a548e… (all equal the prereg Counter/Population pins)
- kasegi-shokunin/corpus/instruments/freeze-check.py 6809c99c…; mori-shokunin/tools/mori-freeze-order.py ec1be305…

## Commands run and observed output (verbatim from connector-probes.txt)
```
## P0a freeze-check on r41 prereg at tip
SUMMARY claims=3 findings=0
rc=0
## P0b freeze-check on r40 prereg at tip (retro arm)
SUMMARY claims=3 findings=18
rc=1 findings=18
## M1 C1 Target line edited after freeze (rule 1 says frozen)
 census/round-41/preregistration.txt | 2 +-
SUMMARY claims=3 findings=0
rc=0
## M2 C1 Control file appended after freeze (rule 1 says frozen)
SUMMARY claims=3 findings=0
rc=0
## M3 C1 Counter appended after freeze (positive control)
FINDING C1 FROZEN-EDITED census/round-41/c1-counter.py differs between freeze e2a74312af42 and f65a14998269
SUMMARY claims=3 findings=1
rc=1
## M4 C1 Kill line edited after freeze
SUMMARY claims=3 findings=0
rc=0
## P1 probe claim C4 (Target "SUMMARY items=999 impossible=1 (exit 0)", printed by no counter)
SUMMARY claims=4 findings=0
rc=0
### same claim through kasegi replay tool (base = the C4 clone)
claim P1 base_read=EXIT=1 verdict=FAIL
finding P1 FC-NO-MATCH no output line equals expect_before '...never printed by any counter'
freeze-check claims=1 base_ok=0 exit=1
rc=1
## X1 mori-freeze-order selftest under the seat scratch
SELFTEST freeze-order FAIL 0/11
rc=1
## X2 committed C2 counter at tip
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8
rc=0
```
Not run: kasegi's own `--selftest` (its 18b case scans /proc and SIGKILLs any process whose cmdline contains `sleep 59.37`/`sleep 59.38`, which is not limited to processes this seat spawned; the seat rule forbids that). mori's `--selftest` cannot run from the seat scratch: it refuses any TMPDIR outside its own checkout, and running it inside /home/vgpnk/Projects/shokunin/mori-shokunin would write a sibling lane. Not run: the C1/C3/R1 counters (the lead measured them; they read nothing this connector changed).

## Findings (at most six)

**F1 — C2 freeze check enforces digests for Counter and Population only (calibration/coverage; the C2 prose overstates it).**
- Prereg rule 1 (census/round-41/preregistration.txt, "Frozen rules") freezes "No Counter, Population, Control, pinned tool, or this file".
- tools/souji-freeze-check.py: `check_path_sha` (lines 114-133) and `evaluate` (136-179) compare freeze vs rev only for Counter and Population (`FROZEN-EDITED`, line 131). Control (167-177) reads the freeze blob only. Target/Kill are checked for presence/non-emptiness (145-147) and never against the freeze. The prereg file itself is parsed from --rev with no freeze comparison. The pinned drift tool has no key, so it is unreachable.
- Observed: M1 (Target edited) exit 0; M2 (Control appended) exit 0; M4 (Kill edited) exit 0; M3 (Counter edited) exit 1 with FROZEN-EDITED. The counter's 21 cases (census/round-41/c2-cases.tsv) include `frozen-edited-counter` and `frozen-edited-population` only, so the counter cannot see the gap.
- The landed lesson names this as "Limit: the check reads the preregistration's shape, digests and order" (corpus/lessons/round-41.md:104-106) but does not name the unchecked Control/Target/Kill/prereg/pinned-tool surfaces. The gap is in the tool's own docstring (lines 13-15 list FROZEN-EDITED for Counter/Population only) but not in the lesson or the C2 claim text.
- Harm to axes: none to the frozen instruments (they are digest-checked). It is a calibration gap in what C2 says it guarantees. Recommended: the L1 adds this as a named limit (not an edit to the frozen tool).

**F2 — the C2 tool never replays a Target; kasegi's does (coverage).**
- Probe P1 (a claim whose Target "SUMMARY items=999 impossible=1 (exit 0)" no counter prints, with real pinned Counter/Population/Control digests): souji tool `SUMMARY claims=4 findings=0`, rc=0. kasegi's replay of the same claim: `FC-NO-MATCH`, rc=1 (kasegi freeze-check.py lines 149-175 run the counter; line 164-165 require an output line equal to expect_before).
- This is the round-44 defect class kasegi's header describes (a frozen counter that can never read its claim). The souji tool cannot detect it, and the C2 counter has no case for it. It is the same class as the landed N8 limit (corpus/lessons/round-41.md:162: "preregistration Targets are printed prefixes … no counter prints"), which the lesson records as a limit but which C2's "operability" claim does not cover.
- Recommended: name it in the lesson beside N8; do not claim the tool closes it.

**F3 — overlap with kasegi and mori: no duplicated behaviour, no contradiction; three "freeze" meanings in the fleet.**
- Inputs differ: kasegi reads `kasegi-round-claims-v2` JSON and replays counter_cmd at a base tree (FC-*); mori reads `mori-freeze-register-v1` JSON with frozen/impl path lists and labels commit order (`pre-build`/`co-evolved`/`no-implementation`/`absent`, mori-freeze-order.py `_row_result` ~250-321); souji reads a markdown prereg and checks digests, base ancestry, freeze-blob order and dispatch files (SOURCE-level grammar in tools/souji-freeze-check.py lines 10-16).
- The only shared mechanism is git commit ordering: souji `DISPATCH-BEFORE-FREEZE` (log `--diff-filter=A` of `.ufo/waves/round-41/` dispatch/.ready files) vs mori's pre-build verdict (first impl commit vs last frozen-path commit). Different objects, no conflicting verdict was observed.
- Three meanings of "freeze": souji FREEZE-REV = oldest commit adding the prereg; mori = frozen paths last changed before the first impl commit; kasegi = a counter replayed at a base tree. The name `freeze-check.py` is used by kasegi's file and by the souji tool's purpose; an operator grepping for "freeze-check" lands on kasegi's tool first. Nothing in the lane points at kasegi's or mori's tool.
- mori selftest adjacency: its refusal path prints `FAIL 0/11` while its success path prints `/12` (mori-freeze-order.py ~497-512 vs ~667-673), so the label count is inconsistent, and the selftest is not runnable under the fleet's /fast scratch rule.

**F4 — coupling between C1/C2/C3/R1: one intended direction, no hidden cross-reads (verified by grep and by M3).**
- C1 (census/round-41/c1-counter.py): reads `census/round-40/records/*` and `census/round-40/waves/` at rev (lines 81-88), `corpus/lessons/round-41.md`, `corpus/SOURCES.md`, its population. No tools/ or other-claim fixture.
- C2 (c2-counter.py): reads tools/souji-freeze-check.py at rev (line 276), and the two preregistrations (round-41 real, round-40 retro) through the tool. Through the prereg it transitively depends on the frozen Counter/Population digests of C1, C2 and C3 counters and populations. This is the only cross-claim read; M3 shows it works as a sentinel (C1 counter edit turns the real leg red through FROZEN-EDITED).
- C3 (c3-counter.py): reads tools/souji-worktree-drift.py (PRISTINE_SHA256 b2a603…, line 49; sha re-verified above) and tests/fixtures/r41-refusal-sites.py at rev. Reads no other claim's fixture.
- R1 (r1-counter.py): reads the same drift tool (PRISTINE b2a603…, line 53), fixtures r39/r40/r41 and the PRIOR list (lines 46-52). It does not read C3's fixture. C3 and R1 share the drift-tool pin and nothing else.
- Verdict: no counter reads another claim's measured artifact except C2's real leg reading the frozen prereg, which is designed to.

**F5 — SKILL.md/PROVINCE.md adjacency: no claim contradicted; registry rows missing for the round's gates (repeat of R39-C1-06 class).**
- grep: SKILL.md has no row for `tools/souji-freeze-check.py`, `tests/fixtures/r41-refusal-sites.py`, `tests/fixtures/r41-drift-record-order.py`, or the census/round-41 counters; `grep -c "r40-"` on SKILL.md is 0, so the round-40 fixtures also have no rows.
- SKILL.md:283 records R39-C1-06 ("four r38 gate fixtures had no registry row (r38 routed defect R6)… every one … names a failing arm"), so the lane's own precedent says gate fixtures need rows. The r41 gates repeat that defect class.
- The SKILL row for souji-worktree-drift (SKILL.md:254) lists self-test fixtures r36–r39 and not r40 or r41; not contradicted by the landing, since the tool bytes are unchanged (b2a603…).
- PROVINCE.md ends at its Round 39 section (lines 278-288); it has no round-40/41 statement, so it asserts nothing the new tools contradict. Its line 186 ("no tool change") and line 256 ("the round's one tool change") are historical, round-specific statements.
- No SKILL/PROVINCE sentence is contradicted by the C2 tool or by the C1/C3/R1 fixtures.

**F6 — C2's real and retro legs are exercised but the tool's exit semantics are split across two arms (operability, minor).**
- `tools/souji-freeze-check.py` documents exit 2 for could-not-evaluate (lines 7-8); the retro arm prints `SUMMARY … findings=18` with rc=1 (P0b), i.e. the retro red is an ordinary finding exit, not a refusal. This matches the C2 counter's expectations (retro=red) and is consistent with the documented contract. Recorded only so the L1 does not read the retro rc=1 as a tool failure.

## Verdict
- Cross-claim coupling (C1/C2/C3/R1): clean. The one cross-read (C2 real leg ↔ frozen counters) is intended and observed to fire (M3).
- Overlap with kasegi and mori: no duplicated or contradictory behaviour; different inputs; the name collision and the mori selftest's label/scratch problems are operability notes.
- SKILL.md/PROVINCE.md: nothing contradicted; r41 gates lack registry rows (F5), a repeat of a recorded defect class.
- C2 calibration/coverage: the tool meets its 21-case target, but its freeze coverage is narrower than the claim's prose: Control, Target, Kill and the prereg file are not checked against the freeze (F1), and Targets are never replayed (F2). These should be named limits in corpus/lessons/round-41.md before admission; they do not change any measured counter result, and they do not contradict C1, C3 or R1.
- Pass/fail of this item: no claim is refuted by the connector scan; F1 and F2 are recommended named-limit additions for the L1.
