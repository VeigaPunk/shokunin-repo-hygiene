# S55critic01 — round 55 critic report (C1 calibration v4, C2 coverage v4)

Base f056aaa031bb (r54 spot-check). Lane tip checked: 3ce0ba036275, content tip 4b10ddd1741a.
Freeze e8f33867, capture 9a1eaaa2, receipt correction 4b10ddd1. Frozen pins re-verified by sha256 before any probe (all six match the prereg).
Read-only against the lane; every counter run from the lane root with TMPDIR in scratch; no commits, no git mutation, no subagents.

## Verdicts

| claim | verdict | basis |
|---|---|---|
| C1 calibration 7 — v4 counter instruments the r54 routed surfaces (27 fixtures) | **SURVIVES** on the literal kill rule. Five under-disclosed limits found (N1–N5) plus three documentation items (N11, N13, N14); routed to r56 as named limits. | All kill clauses evaluate as written (table §2). Vacuity holds (§1). Probes show the disclosed limits hold (§3), and a fenced/commented pair-filing false pass that the named-limit list does not state (N1). |
| C2 coverage 8 — capture counter v4 (NL surfaces, FA9/FB4 arms) | **SURVIVES** on the literal kill rule. Receipt-grammar shapes outside `#KEY=VALUE` are silently ignored (N6); kill-row naming is convention, not enforced (N12). | All kill clauses evaluate as written (§2). Vacuity holds for FB1–FB3 (§1). |

No claim is FALSIFIED. Every finding below is a named limit, not an edit of frozen bytes.

## 1. Vacuity (v3-arm acceptance control)

Re-ran `census/round-55/fixtures/run-matrix.sh` from a fresh scratch build of the frozen builder (`build-fixtures.py --work`). All four regenerated matrices are byte-identical to `records/matrix-dryrun/` and `records/c{1,2}-matrix-v{3,4}.tsv` (receipts/c*-matrix-*.tsv). Two independent builder runs produce identical fixture revs (REBUILD-SAME).

v3 (frozen r54) exit codes on the acceptance attacks, reproduced:
- C1: F7-FF 0, F13 0, F14 0, F15 0, F16 0, F20 0, F21 0, F22 0 (all eight exit 0, so the frozen v3 counter cannot have killed them).
- C2: FB1 0, FB2 0, FB3 0.

v4 on the same rows: C1 exits 1 on all eight (F7-FF CORRECTION-IN-FENCE, F13 ANCHOR-ALIAS-MISMATCH, F14 PAIR-FILING-INERT, F15/F16/F22 UNFILED-SOURCES-ANNOTATION, F20/F21 BOGUS-RECOMPUTED). C2: FB1 COMMENT-AMBIGUOUS-NAME, FB2 and FB3 RECEIPT-UNKNOWN-KEY.

Vacuity does not hold as a problem: the work is not vacuous.

## 2. Kill-rule audit (clause by clause, against committed evidence)

| clause | evidence | status |
|---|---|---|
| C1: v4 exits 0 on F7-FF,F13,F14,F15,F16,F20,F21,F22 | v4 rc 1 on all eight | not triggered |
| C1: v4 exit 1 on F17,F18,F19,F12c,F1,F12b | v4 rc 0 on all six | not triggered |
| C1: v4 exit 1 on the real lane at content tip | rc 0 at 4b10ddd1 and at 3ce0ba03; the frozen fields reproduce (`unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0`). The committed receipts c1-tip.txt / c2-tip.txt do not record exit codes; the rc is from my re-run. | not triggered (see N15) |
| C1: v3 kills any of the eight | v3 rc 0 on all eight | vacuity holds |
| C1: carry-over, v4 failing F2–F12 with their r54 findings | finding ids identical for F2–F12 (exit 1 each). F10 SUMMARY changed (mismatches 2→1, filed 2→1): see N11. | not triggered; N11 recorded |
| C1: changing F1/F12b/F12c green states | 0/0/0 under v3 and v4 | not triggered |
| C1: "any finding the wave attacks raise … recorded as a named limit" | N1–N10 below | routed |
| C2: v4 exit 0 on FB1, FB2 or FB3 | rc 1 each | not triggered |
| C2: v4 exit 1 on FH-HONEST, FH2-SYMLINK-HONEST, fresh capture | FH rc 0, FH2 rc 0, fresh capture rc 0 at 4b10ddd1 and 3ce0ba03 | not triggered |
| C2: v3 kills any of FB1–FB3 | v3 rc 0 each | vacuity holds |
| C2: selftest FA9 rc 1 TOOL-SHA-ARG-MISMATCH; FB4 rc 2 named refusal | `SELFTEST-CASE FA9-WRONG-TOOL-PIN pass rc=1 … TOOL-SHA-ARG-MISMATCH`; `FB4-PIN-SHAPE pass rc=2 … TOOL-SHA-ARG-MALFORMED` | not triggered |
| C2: carry-over, v4 changing any FH/FA1–FA8/FH2 exit | v3 and v4 exits identical; only FA8's finding id changes (`class` → `CLASS-MISMATCH`), which is the intended fix | not triggered |

Wording (not a verdict change): the prereg uses "kill" for two things. In the "Kill:" heading it is the falsifier. In the vacuity sentence ("v3 counter killing any of …") it is the detection outcome. Both read correctly once you know which, but a reader can invert the clause. Recommend r56 uses "falsified when" for the heading.

Controls (receipts/): C1 and C2 negative-pin runs both return rc 2 with the verbatim PIN-MISMATCH lines the controls quote. Absent-instrument: `git cat-file -e` at base returns rc 128 for both counters. Full selftests pass (C1 27 cases, C2 15 cases, output byte-identical to records/c{1,2}-selftest.txt). Every row the control files embed (C1 F-rows, C2 FB rows) equals the regenerated matrix line byte-for-byte.

S278 quotes (SOURCES frontier step): all three located quotes occur as substrings of the captured `census/round-55/sources/s278-python-stdtypes.html` after the stated recipe.

## 3. Named limits: probe results and classification

Probe harness: `receipts/probe.py`, `probe2.py`, `probe3.py`; outputs `receipts/probe-results.txt`, `receipts/probe2-results.txt`. Every C1 probe fixture is a git repo built by the frozen builder helpers; every C2 probe is an edited clone of the frozen FH-HONEST fixture. Frozen counter bytes unmodified.

Classes: (a) disclosed and confirmed; (b) under-disclosed (behaviour worse than the prereg states); (c) over-disclosed.

Requested probes:
- **Pointer-shaped fake `x.md:1`** — rc 0 (c1-P1). Disclosed verbatim ("a pointer-shaped fake such as `x.md:1` still does") → **(a)**. Acceptable under the disclosure, but see N4.
- **Single unknown key** — `# GENERATOR=x` plus `# HOST=y`: rc 1, only GENERATOR named (c2-P1) → **(a)** (disclosed: "only the FIRST unknown receipt key is reported"). The unknown-key shapes outside `#KEY=VALUE` are a different and worse matter: see N6.
- **Beyond-zone exit 2** — sole annotation at column 40: rc 2, `CANNOT-EVALUATE no annotation in zone` (c1-P5) → **(a)**. A second anchor occurrence whose annotation sits beyond the zone is not judged (c1-P6, rc 0) → **(a)** with a wording gap (N9).

Other probes (all rc on the frozen counter):

| id | probe | rc | class | note |
|---|---|---|---|---|
| c1-P0 | control: overstated `274 -> 275` in LOG.md, no filing | 1 (UNFILED) | — | counter works |
| c1-P1b | `(ratio 2.5:1)` on an overstated line | 0 | (b) | N4 |
| c1-P1c | `(v2.1:3)` on an overstated line | 0 | (b) | N4 |
| c1-P2 | `1 -> 2 rows and … 274 -> 275 rows`, no filing | 0 | (b) | N2 |
| c1-P2b | reversed order, same two pairs | 1 | — | order-dependence confirms N2 |
| c1-P3 | honest unfenced pair filing | 0 | — | correct |
| c1-P3-fenced | same filing inside a ```` ```text ```` fence in SCORECARD.md | **0** | (b) | N1, false pass |
| c1-P3b | same filing inside `<!-- … -->` | **0** | (b) | N1, false pass |
| c1-P4 | prose `now holds 274 rows` | 0 | (b) | N3 |
| c1-P4b | `274 => 275 rows` | 0 | (b) | N3 |
| c1-P4c | `274 to 275 rows` | 0 | (b) | N3 |
| c1-P7 | overstatement in NOTES.md (outside LOG.md / README) | 0 | (a) | AF4c disclosed |
| c2-P0b | control: `#BUILDHOST=` | 1 | — | FB3 works |
| c2-P2 | `# BUILD-HOST=fixture` | 0 | (b) | N6 |
| c2-P3 | `# BUILDHOST: fixture` | 0 | (b) | N6 |
| c2-P4 | `# BUILDHOST=fixture build` (space in value) | 0 | (b) | N6 |
| c2-P5 | `# BUILD HOST=fixture` (space in key) | 0 | (b) | N6 |
| c2-P6 | `# GENERATOR=` (empty value) | 0 | (b) | N6 |
| c2-P7 | `# ENTRIES: 999` alongside the true `ENTRIES=3` | 0 | (b) | N6, a known key silently ignored |
| c2-P7b | `#  ENTRIES = 999` (spaced, recognised) | 1 (RECEIPT-MALFORMED) | — | recognised and validated, as claimed |
| c2-hdr | capture header typo, receipt rebound to altered bytes | 1, first FINDING `column header mismatch` | (b) | N12 |
| M7 mutant (drop PTR exemption) | F12c | mutant 1 | — | kill-power real |
| M2 mutant (any-length closing fence) | F8b | mutant 0 (frozen 1) | — | kill-power real |
| N5 mutant (drop SOURCES recompute) | F23 | mutant 0 (frozen 1) | — | kill-power real |

## 4. Named-limit list for r56 (N1…)

- **N1 (b, new; highest severity).** Pair filings (`R53-CORRECTION`) are accepted inside fenced code blocks and HTML comments in SCORECARD.md. `pair_filings` is built from raw `CORR2_RE` matches with no `hidden_lines` check, while single `R52-CORRECTION` filings are refused (CORRECTION-IN-FENCE, F4/F7/F8/F9). An overstated LOG.md or README annotation can therefore be "filed" by a documentation example. Repro: c1-P3-fenced and c1-P3b (both rc 0; the honest unfenced filing is also rc 0, which is correct). Fix in r56: apply the same hidden-region rule to pair filings.
- **N2 (b).** Only the first pair annotation per LOG.md/README line is scanned (`PAIR_ANNOT_RE.search`). A leading within-registry pair suppresses the rest of the line. Repro: c1-P2 rc 0 vs c1-P2b rc 1.
- **N3 (b).** The pair grammar is exactly `->` or `→` with optional `rows`. `=>`, `to`, and prose counts ("now holds 274 rows") are invisible and not in the named limits. Repro: c1-P4, c1-P4b, c1-P4c, all rc 0.
- **N4 (b).** The PTR exemption is a line-level search for `\w.\w{1,5}:\d` anywhere on the line. It is not limited to "extension-bearing paths": `2.5:1` and `v2.1:3` exempt a line (c1-P1b, c1-P1c, rc 0). The disclosure says "extension-bearing paths only", which the regex does not implement. Restate or tighten (require a path separator or a non-numeric extension).
- **N5 (b, scope).** The counter instruments two annotation sites (SCORECARD.md, census/round-51/preregistration.txt). The same anchor with a stated count exists elsewhere in committed bytes, e.g. census/round-54/wave/S54sentinel01.md:671 (`(78)`). Site-set scope is not in the named-limit list.
- **N6 (b).** The receipt key grammar `#\s*KEY\s*=\s*(\S+?)` silently ignores receipt lines that do not match it: hyphenated or colon-separated keys, spaces in the key or value, empty values, and a known key in a colon shape (`# ENTRIES: 999`). Repro c2-P2 to c2-P7, all rc 0. The prereg's FB2/FB3 claims hold literally; the omission is that no unparsed-receipt-line limit is stated.
- **N7 (a).** Only the first unknown receipt key is reported (c2-P1). Disclosed.
- **N8 (a).** Beyond-zone sole annotation exits 2 (c1-P5). Disclosed.
- **N9 (a, wording).** A second anchor occurrence whose annotation is beyond the zone is not judged (c1-P6, rc 0). The R2 sentence "the zone is evaluated after every occurrence" should say "every in-zone annotation".
- **N10 (a).** Pair annotations outside LOG.md/README are invisible (c1-P7, rc 0). Disclosed (AF4c).
- **N11 (b, carry-over drift).** v4 changes F10 SUMMARY (`mismatches` 2→1, `filed` 2→1) because a straddling site is now skipped in the count; exit and finding are unchanged. The prereg names only finding ids for carry-over, so this is not a kill, but it is an unlisted behaviour change. v4 also adds `alias=`/`pairinert=` fields to every SUMMARY, which is expected.
- **N12 (b).** `run-matrix.sh` names a row by the second token of the first FINDING line, without checking that it is an id. A capture header typo yields `column` (c2-hdr). The §5.2 criterion ("a counted kill row names its finding") is therefore met by convention, not by the taker. FA8 and FB rows do carry ids today.
- **N13 (b, verbatim discipline).** The control files' lines `PRISTINE FAIL C1V4-COUNTER-ABSENT` and `PRISTINE FAIL C2V4-COUNTER-ABSENT` are hand-written labels; no counter prints them. The observed output is `cat-file-rc=128`, which the control already records. Rewrite as the observed output or label as an assertion.
- **N14 (b, receipt base).** `records/c1-real-lane-base-preflight.txt` was run with `--base fe12daad2549` (the round-53 spot-check commit), not `f056aaa031bb`, which the prereg's Base line implies. Its `rev=f056aaa031bb` is correct and the fields match, and the same tip run at fe12daad still exits 0, so no verdict moves. The receipt's base field should be explained.
- **N15 (b, minor).** `c1-tip.txt`, `c2-tip.txt`, and `c2-r54-capture-preflight.txt` do not record exit codes. The prereg says "exit 0". I re-ran all three and each returns rc 0; the receipts should carry the rc.

Also noted (no action): the C2 receipt correction at 4b10ddd1 (ENTRIES=49) is consistent with the r54 capture pin: `census/round-54/records/fleet-root-census.tsv` at base returns rc 0 with tool_pin=ok, as claimed.

## 5. Receipts and tool record

Seat receipts: `.ufo/waves/round-55/w1/S55critic01/receipts/`:
- `c1-matrix-v3.tsv`, `c1-matrix-v4.tsv`, `c2-matrix-v3.tsv`, `c2-matrix-v4.tsv` (regenerated, byte-identical to records/)
- `c1-selftest-now.txt`, `c2-selftest-now.txt` (pinned selftests, byte-identical to records/)
- `c1-tip-*.txt`, `c2-tip-*.txt` (real-lane re-runs at 4b10ddd1 and 3ce0ba03, with rc 0)
- `probe.py`, `probe2.py`, `probe3.py`, `probe-results.txt`, `probe2-results.txt`

Tools: none installed or upgraded. Python 3.14 stdlib (`python3 -B`), git read-only (`cat-file`, `rev-parse`, `log`), `grep`. No pacman, no network.

Scratch: `/fast/scratch/hyaku/souji-r55/S55critic01/` deleted after the receipts were copied. Disk at start: /fast/scratch/hyaku 50% used, 409.2G free.

## 6. Path note

The task's Report line names `.ufo/waves/round-55/w1/S55critic01.md`, which is outside this seat's directory, while the seat spec and Bounds restrict writes to `.ufo/waves/round-55/w1/S55critic01/`. I followed the seat-directory rule and wrote this report to `S55critic01-report.md` there. The L1 should confirm which path to index.
