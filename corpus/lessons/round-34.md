# Round 34 — registry calibration (C1 missed), sandboxed measurement (C2 missed)

author: souji L1 (SoujiR34a2), fresh-start round after rejected round-31, round-32 and round-33 closures. The closure sweep is `census/round-34/records/closure-sweep.txt`.

Frozen contract: `census/round-34/preregistration.txt` (initial freeze `2b591924f607940febbb99f922cc9bb090508eb6`; C2 repair/re-pin `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`). Controls are summarized in `census/round-34/records/controls.txt`; C1 do-nothing was 60 items, 35 agree / 25 mismatches, rc 1. Attempt-1 counter and fixture gaps were logged as amendments; the post-amendment C2 feasibility remains red.

## Claims

- **C1 calibration — registry/outcome agreement.** Sixty frozen SKILL/SCORECARD items; base do-nothing `SUMMARY items=60 agree=35 mismatches=25 restated=0`. Five individually validated, append-only corrections landed (E04, E05, E18, E23a, G23). The full `agree=60` target was **missed and is not claimed**: W1/W2 reproduced unreachable frozen items/predicates including G05, G17b, G24, E23b and E26, plus false-cause acceptance for G17a/G21. W2 corrected W1's blanket claim that no SKILL mismatch was restatable: G23 is a valid, engine-accepted correction because its true authoring commit wrote both the stale `where` line and its own adjacent registry row. That exception does not repair the other blocked items.
- **C2 operability — sandboxed work witness.** Thirteen frozen legs. The base absence control is CNE/exit 2. After repair/re-pin, feasibility at `60def78d16017be528ba6b439e350918587cb80b` reported `SUMMARY legs=13 pass=9 fail=4 harm=0` (W2, W3, N3 and J1 failed). The C2 target was **missed**; no landing/tip pass is claimed.

Scores unchanged (calibration 7, operability 8, coverage 8). Four post-freeze operational amendments are documented in the preregistration; none changes a frozen target or predicate. No tool install or update occurred; no pacman transaction occurred. Certification OFF, K5 HELD, NAMESPACE hold unchanged.

## Gate

opened: 2026-10-27 — wave-1 scribe SwarmScribe33 opened S230 live. The captured source bytes are `census/round-34/waves/w1/src-S230.html` (manifested in the committed wave receipt); sha256 `2cb77df2f4be0b2a0302bb2f0a260fdb4d9e1299b76481ea66ed34c40f5be1da`, HTTP 200, 33,289 bytes. Host bubblewrap version: 0.13.1.

| Candidate | Decision | Source reopened | Located quote / evidence | Reason / flip |
|---|---|---|---|---|
| `S230` bubblewrap(1) man page source, `bwrap.xml` at tag v0.13.1 | ADMIT (new row, `mined`; scope restricted to `--bind`/`--ro-bind` mount semantics) | https://github.com/containers/bubblewrap/blob/v0.13.1/bwrap.xml — HTTP 200, 33,289 bytes, sha256 `2cb77df2…be1da`, fetched 2026-10-27; captured bytes `census/round-34/waves/w1/src-S230.html` | § DESCRIPTION `:56`: “creates a new mount namespace for the sandbox.” | The man page documents a new sandbox mount namespace and says `--bind`/`--ro-bind` bind SRC on DEST (writable/read-only). It does not explicitly say the host destination is unaffected; that consequence is an inference from the per-sandbox namespace, not a quote. N3 uses the private bind to keep the pinned fixture's host bytes untouched. |

Registry row S230 was appended to `corpus/SOURCES.md`; no prior row changed.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| `reachability` | C1 W1/W2 attack reports in `census/round-34/waves/`: G05/G17b's frozen tab predicates cannot match after whitespace collapse; G24 pins a revision before its own script; E23b/E26 have no honest cause route; `feasibility-final.txt` shows C2 W2/N3/J1 timeouts | Q70a/Q78 — require target reachability and the full per-item call tree before freezing | Before data, run every item against the exact final counter at the candidate, including mutation cases for exit wildcard, tab-delimited predicates and cause/file binding; remove or repair impossible items before the frozen list lands. |
| `false-provenance` | W1/W2 G21 and G17a attack reports: the off-by-one SKILL `where` cell lets an unrelated neighboring-row writer be accepted as an argv-correction cause; W2 confirms G23 is an exception because the true author wrote both lines | Q75 — execute the cause and verify it wrote the exact row identified by the cell; add a wrong-neighbor negative control | Freeze `where` from the exact base row and test both the true writer and a foreign neighbor. Never land a mechanically accepted correction whose provenance is wrong. |
| `vacuous-exit` | `census/round-34/waves/w1/deliver-c1-attacks.txt` and W2 `AttackC1WildcardExit.md`: the C1 judge accepts exit `*`; the reproduced run happened to return 0, so nonzero false-green acceptance is source-level inference, not a second observed run | Q75 — concrete restated exit must bind the measured execution | Require a concrete integer exit in every restatement and mutate the exit cell to `*` as a negative control before freezing. |
| `measurement-feasibility` | `census/round-34/records/feasibility-final.txt`: W2 R15CFG-01 timed out; W3 compared randomized scratch paths without normalization; N3 ran 12 cases but one timed out; J1 exceeded its 900-second inner limit | Q70a/Q78 before freeze; Q79 now specifies witness, stub and case-count evidence | Make the sandboxed full call tree affordable and path-normalized, run it under the same namespace/TMPDIR contract, and require an observed 12/0 N3 summary and completed J1 control before claiming green. |
| `resource-conformance` | L1's settled W1 scratch root reached 59.7G; disk guard at an earlier check showed `/fast/scratch/hyaku` 83% used / 140.5G free. The owned root was removed after settlement; post-clean was 26% / 595.7G free. W2 scratch stayed 19.1MB and was also removed after settlement. Full readings and cleanup are summarized in `census/round-34/records/controls.txt`. | none — run-10 operator scratch cap, not a then-existing QUALITY row | Check `disk-guard.sh status` before a heavy pass; keep per-fixture scratch below 50MB unless explicitly declared, stop own jobs after evidence settles, and remove only the L1-owned scratch root. |

## Findings

1. **C1 did not meet its target.** The base control is committed; no full-width after reading was run. Five valid restatement rows were individually validated by W1/W2 scratch probes and landed append-only. W2 independently confirmed G23; it also showed E26 is honestly un-restatable because its only frozen file is the r30 C2 counter, the value drift is in later captured files, and the argv-correction's `rev=<measured commit>` statement is self-referential at landing. A `sed` route that strips that revision can satisfy the engine but would falsify the measured output and was not landed. G05/G17b remain unreachable due tab/whitespace mismatch; G24's pinned revision lacks its named tool; E23b's real drift touches no item file and its row-writing cause already holds. G21 and G17a demonstrate a neighboring-row false-cause acceptance. A wildcard exit is a reproduced survivor; the recorded attack run itself returned rc 0, so acceptance of a nonzero result is not claimed as executed.
2. **C2 did not meet its target.** The initial run exposed a missing N3 staged tool path and W2 outside the required bwrap envelope. A6 repaired those implementation defects and re-pinned the list. The repaired full feasibility still failed four legs: W2 and N3 hit fixture timeouts, W3's output comparison omitted the required scratch-path normalization, and J1 timed out running the full counter. W2 independently confirmed the W3 contract mismatch and found G5's disjointness check omits some mixed C1/C2 commits. No C2 green outcome is claimed.
3. **Round shape was completed.** W1 had 40 seats (17 executor, 4 critic, 2 mutation-tester, 4 reviewer, 3 scout, 3 connector, 4 scribe, 1 sentinel, 1 revenger, 1 simplifier); W2 had 32 seats (17 critic, 15 reviewer), total 72. The planner seat was held by the L1. All 72 seats settled; no dead seats were reported. W2 falsified/adjudicated 32 distinct W1 targets (25 C1 mismatch items plus seven C1/C2 attack surfaces). Wave reports and results are committed in `census/round-34/waves/`.

## Receipts

- Freeze/control summary and scratch cleanup: `census/round-34/records/controls.txt`.
- C1 base: `census/round-34/records/controls-c1-do-nothing.txt`; C1 behavioral junk: `census/round-34/records/junk-c1.txt`.
- C2 repaired feasibility: `census/round-34/records/feasibility-final.txt`; C2 junk timeout: `census/round-34/records/junk-c2-final.txt`.
- Wave receipt: `census/round-34/waves/manifest.sha256`, `summary.tsv`, and 170 captured records.
- SCORECARD restatements E04/E05/E18/E23a/G23 and Round-34 measurements/planned r35.

## Residuals

- C1 remains missed: fix the enumerator/counter provenance and predicate defects before any new freeze; do not use neighbor-cause false greens. Preserve W2's G23 correction as the valid exception and E26/G05/G17b/G24/E23b as named misses.
- C2 remains missed: close W2/W3/N3/J1 and G5 before re-running the full 13-leg target at landing and tip. Do not treat `harm=0` as measured; it is a literal in the summary printer.
- The C1 wildcard-exit survivor and fixture timeouts need new frozen controls in r35; no post-data counter mutation was made.
