# SwarmCritic28 — attack on C1 (calibration, bookkeeping-file)

## Status

STATUS: PASS — attack executed and reproduced. The frozen C1 target `unbound=0 mismatches=0` is reachable in full (41/41 MATCH, rc 0), but 38 of the 41 bindings are two-integer record matches — 17 of them demonstrably to unrelated or cross-wired text (line selectors, a version string, HTML captures, a counter's own source, a `STATUS: OPEN` disclaimer, one file shared by three cells) — 1 is a re-quotation of the same command's own output line, and 2 require a 4-line edit to an audited fixture. `mismatches=0` measures bookkeeping, not calibration. No counter or contract was changed; the lane was read-only for this seat.

## Evidence

All counters were run from the lane working tree, whose tip is `1b811368461785040e955f41f9c97e62f61fd67c` (clean except untracked `census/round-31/records/c*-after-*.txt` written by other seats). `tools/souji-capability-cells.py` is blob `84e4f68744071255057cb125648190e18ab0e4ec` at both `1d45496a` and the tip.

Base reproduction (my run, not copied from `controls.tsv`):

```
python3 -B tools/souji-capability-cells.py --root <lane> --rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 \
  --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=1d45496a...
```

Attack state: one `--no-local` clone of the lane with `origin` removed, under `/fast/scratch/hyaku/souji-r31/AttackC1/`, nine appended commits on top of the lane tip. Diff against base: `SCORECARD.md 49/0`, `tests/fixtures/r16-landing-gate.py 4/0`, `tests/fixtures/r23-record-agreement.py 4/0` — zero deletions, every capability cell byte-identical.

```
ed1ccd6 attack: L32 via byte-changed fixture
5843a22 attack: remaining arbitrary-text bindings incl. tab and JSON-escape literals
79ef324 attack: literals that are not the cell's number
2961426 attack: L08 run row with off-line script
23a4b73 attack: L08 only record candidate is a transcript
6213530 attack: fixture accepts flag that prints 18/18
9d3a061 attack: L06 run row + literal-printing flag in the audited fixture
343e3cb attack: L06 run row, unedited fixture
e3dfc9b attack: mechanical record bindings
```

Final full scoring of that state (no `--only`, so `partial` is absent):

```
ITEM  L40  SCORECARD.md:355  literal=7, f'bad={bad7  superseded binding=record MATCH census/round-29/c3-integrity.py
ITEM  L41  SCORECARD.md:355  literal=7 no reserved-TLD host (.test .example .invalid .localhost) in an F3  superseded binding=record MATCH census/round-29/c3-integrity.py
SUMMARY items=41 bound_run=3 bound_record=38 unbound=0 mismatches=0 rev=ed1ccd60df454846eb0a32a5cabb6d80f03751be
rc=0
```

Intermediate states used to isolate each guard:

| state | rows | result |
|---|---|---|
| `e3dfc9b` | 21 rows found by plain `git grep -F <literal> <base> -- census/round-<N>/` | `bound_record=21 mismatches=0` |
| `79ef324` | 6 rows whose literal is not the cell's number (`15CFG-15`, `4a4`, `27d6`, an HTML footnote, an HTML anchor, a Python source fragment) | `bound_record=6 mismatches=0` |
| `343e3cb` | L06 run row, fixture unedited | `RUN-MISMATCH observed=SUMMARY total=15 failed=0` |
| `6213530` | L06 run row, fixture accepts `--ci-satisfy` and prints `18/18` | `MATCH observed=18/18` |
| `23a4b73` | L08 bound to `census/round-16/transcripts/w1/RevengeProbeRecurrence.txt` | `BAD-ROW(record-shape)` |
| `2961426` | L08 run row naming `tools/souji-cert-evidence.py` | `BAD-ROW(run-shape)` |
| `5843a22` | 14 more record/run rows (tabs and JSON `\t`/`\n` escapes) | `bound_run=1 bound_record=13 mismatches=0` |
| `ed1ccd6` | L32 run row, fixture accepts `--ci-satisfy` and prints `selftest=9/9` | `MATCH observed=selftest=9/9` |

Record-candidate scan (same rule the counter applies: maximal digit-run pairs inside one line, no `\|`, path under `census/round-<N>/` for a round in the item's parsed `rounds`, no `waves`/`transcripts` path part, no `:`, blob unchanged base→rev): **38 of 41 items have at least one candidate record**. The three without are L06, L11, L32. L11's only non-record route is re-quoting its own command's line as `29 failed=0` (truthful in meaning, but not the cell's literal); L06 and L32 have neither a record nor a truthful re-quotation.

Enumeration-gap extraction from `SCORECARD.md` at base (`census/round-31/c1-cells.tsv` header rule applied to lines 147-175, 313-314, 354-355): the 41 items are the `N/M` and `cases=N pass=N` tokens of the third cell only. The same rows carry at least 24 further count statements and the axes section four more — examples with locations in Findings 7.

Scratch was removed after this report was written (`rm -rf /fast/scratch/hyaku/souji-r31/AttackC1`). No tools were installed or upgraded.

## Findings

1. **The record rule is integer-pair matching, not evidence.** `tools/souji-capability-cells.py:253-265` accepts `record:` when the path is under `census/round-<N>/` for a round parsed off the row's base line, is not under `waves/`/`transcripts/`, has no `:`, is byte-identical at `--base` and `--rev`, and contains the row's literal at digit bounds; the only literal constraint is `sorted(ints(lit)) != sorted(ints(lit0))` (line 258) — integer **multiset**, not string equality. I reproduced 38/41 that way with plain `git grep` plus a generic two-integer scan, e.g. `| L07 | SCORECARD.md:158 | 15CFG-15 | record: census/round-16/c1-matrix-final.json |` and `| L20 | SCORECARD.md:165 | 27d6 | record: census/round-21/read-root-oracle-provenance.json |` — both scored `MATCH` (`79ef324`).

2. **The appended literal need not be the cell's literal.** Because of the same multiset check, rows can state text the cell never contains: L10 (`4/4`) accepted as `4-4` from `census/round-21/read-root-oracle-w1-partial.tsv` — a README-selector line, "(:4-4:raw selector stripped); never V-READ-ROOT" — and as `4a4`; L17 (`11/0`) accepted as `11.0` from `census/round-16/c1-matrix-final.json`, whose only occurrence is the version string `"version: 0.11.0"`; L27 (`3/3`) accepted as `3-3` from `...(:raw:3-3 selector stripped)`; L30 (`8/8`) accepted as an HTML footnote from `census/round-22/attempt2/sources/freedesktop-trash.raw` (a raw web capture) or as the axis-score substring `stay7/8/8`; L39, L40, L41 accepted from `census/round-28/sources/open.html` and `census/round-29/c3-integrity.py` (a counter's own source fragment, `7, f'bad={bad7`).

3. **A record row silently suppresses the row's own command.** `elif iid in sup:` (line 218) is taken before the `basecmd` branch, so the `basecmd` from `c1-cells.tsv` is never executed. My base run shows L04 `RUN-MISMATCH ... observed=SUMMARY total=5 failed=0 hung=0` and L05 `RUN-MISMATCH ... observed=selftest=PASS ids=7/7`; after the record rows both score `MATCH` at `e3dfc9b` with `binding=record`, i.e. a cell whose own command now prints a different number is counted as calibrated.

4. **Run bindings are not pinned to committed bytes.** The run-shape test (lines 233-240) requires the script to exist at `--base` **and** at `--rev` but never compares the two blobs (`blob_oid(root, a.base, script) is None` / `blob_oid(root, a.rev, script) is None`, no `!=`). A 4-line edit to `tests/fixtures/r16-landing-gate.py` (`--ci-satisfy` prints `18/18`, returns 0) turns L06 from `RUN-MISMATCH` to `MATCH` at `6213530`; the same edit to `tests/fixtures/r23-record-agreement.py` (`selftest=9/9`) turns L32 to `MATCH` at `ed1ccd6`. Both are row-legal: the stem is on the row line, the literal is not in argv, and no banned flag is used.

5. **The run rule also accepts a re-quoted output line.** `at_bounds(lit, s)` matches the last digit-bearing line, so a row may quote a different textual slice of the same output than the cell states: L11's cell says `29/0` (line 160) while the row states `29 failed=0` and the unmodified command prints `SUMMARY total=29 failed=0` — `MATCH` at `5843a22`. The same move works for L04 (`5 failed=0` from `SUMMARY total=5 failed=0 hung=0`), L07 (`15 failed=0`), L21, L22, L23 — all without any record or edit.

6. **Record targets need not be measurement records at all.** The only structural exclusions are `waves`, `transcripts` and `:`. Scanned and admitted targets include a counter's own Python source (`census/round-29/c3-integrity.py`), an HTML page capture (`census/round-28/sources/open.html`), a raw web source (`census/round-22/attempt2/sources/freedesktop-trash.raw`), a README-selector TSV (line ranges), and — found by scan, not scored — the L1's own junk harness `census/round-30/controls.sh:52`, whose only occurrence is `print('cases=7 pass=7 control=FALSE-GREEN-REJECTED')`: a cell can be "bound" to the fabricated output of a control script.

7. **The enumeration is notation-selected, so "every one of the 41" is not every count in the capability cells.** Count statements in the enumerated rows that the TSV header rule cannot see, with locations: `SCORECARD.md:147` second cell "at 64-seat parallelism, dry-run" and third cell "(246 rows)"; `:151` "baseline 33 rows, mined=16 queued=15 rejected=2 at 31984f473ce4bdab61a99b16cca194b28108cb81" (same cell class as the enumerated `12/9`); `:161` "(5fa6017 tools: 13 fail)"; `:165` "and160-byte bounds" and "leaks19→0"; `:168` "(base12)", "(base11)", "18-step"; `:173` "reject an always-zero emitter on eight of nine fixture cases"; `:174` "garbage: 1", "over 8 frozen cases", "one lane-bound figure"; `:175` "its fixture fails the always-zero emitter on all nine cases" and "6 of 13 at 778747e"; `:314` "records=1381 failed=0 uncovered=0". The axes section adds `:129` "SOURCES census mined=16 queued=15; calibration C1's 28/52 → 51/53 is a rule-coverage count, not calibration proof". Spelled-out counts ("eight of nine", "all nine", "five pinned replay verdicts", `:166`) are outside any digit rule by construction. None of these can appear in `unbound` or `mismatches`.

8. **One occurrence binds several cells.** Record bindings are file-granular, not line-granular: L03, L04 and L05 (three different capabilities) all scored `MATCH` against the same first `5/5` in `census/round-13/final-checks.md`; L28 and L29 both against one `18/18` sentence; L36, L37 and L38 all against `census/round-29/records/amendments.txt`. At most one of each group can be the intended measurement, so the counter cannot distinguish the true binding from the false one.

9. **A "genuine" historical record can certify the opposite of the claim.** L02's best record is `census/round-13/cert-protocol.md:307`, whose text is "which is why a matching number is not evidence that the same bytes were run"; L28/L29's is `census/round-20/recovery-status-catalog.json:226`, "the available `18/18` acceptance does not cover all final-tip hashed bytes". Both score `MATCH`. The counter has no notion of a record that supports versus contradicts.

10. **The claim's own arithmetic does not match its frozen enumeration.** The preregistration says "23 literals have no observable beside them at all" (preregistration.txt:4); `c1-cells.tsv` has 19 `basecmd` rows and 22 empty ones, and the base counter reports `unbound=22`. The prose partition (18 bound + 23 unbound = 41) is off by one, because L40 was added to the enumeration after r30's row enumeration (TSV header: "L40 added, its row was appended in r30 after that enumeration").

11. **The run executes with ambient environment and PATH** (`env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1")`, line 194), and `summary_line` has no banner/`Usage` refusal of the kind r30's stricter amendment A3 added. [INFERENCE] A run binding's output is therefore a function of uncommitted state at scoring time; I did not exercise a PATH shim, so I claim the mechanism, not an execution.

## Attack log

**Q1 — can a cheap mechanical binder reach the target with unrelated text?** Yes, and it reaches it completely. Plain `git grep -F` for the literal in the allowed round dirs finds 17/41 unchanged files; widening the search to any single-line two-integer span of the same multiset (still mechanical: no semantics, no command, no re-run) finds 38/41. With those 38 record rows plus three run rows I scored `SUMMARY items=41 bound_run=3 bound_record=38 unbound=0 mismatches=0` (`ed1ccd6`). The bindings include line selectors, a JSON version string, an HTML anchor, a JSON-escaped `32\tpass=32`, two Python source fragments, and a `STATUS: OPEN` disclaimer.

**Q2 — the run-binding guards.** Stem-on-line, literal-not-in-argv and the four banned flags all held in every attempt; the missing guard is byte-pinning. The cheapest legal printer of an arbitrary literal is therefore a committed script on the row's line whose `--rev` bytes differ from its `--base` bytes: 4 added lines in `tests/fixtures/r16-landing-gate.py` produced `MATCH ... observed=18/18` at `6213530`, and 4 added lines in `tests/fixtures/r23-record-agreement.py` produced `MATCH ... observed=selftest=9/9` at `ed1ccd6`. Second-cheapest, needing no change at all: quote a different slice of the command's own last digit line (Finding 5). I also confirmed the two shape guards do bite on the only L08 near-miss shapes (`23a4b73`, `2961426`).

**Q3 — is binding a stale cell to a historical record honest calibration?** No, as implemented. It is honest only when the record is the measurement of *that* capability at *that* round; the rule checks neither. For counts that grew, the record does not merely preserve a stale number, it removes the only live observable: L05's cell states `5/5` while `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` prints `selftest=PASS ids=7/7`, and the record row makes that cell `MATCH` without ever running the command (Finding 3). The r30 routed defect asked for old literals to be *superseded*; this target lets them stand. What the target actually measures is "every cell has a two-integer token somewhere in its round", i.e. accountability, not agreement.

**Q4 — enumeration coverage.** The 41 are the evidence-cell tokens of two notations only. At least 24 further count statements sit in the same cells and four in the axes section (Finding 7), including keyed and unit counts in cells the enumeration does treat (`:151`, `:161`, `:168`, `:314`), so "every one of the 41 count literals" is a true statement about a notation subset, not about the cells.

## Verdict and smallest safe correction

Fixable defects, all stricter-only (the L1 logs them; I changed nothing):

1. Run bindings: require `blob_oid(base, script) == blob_oid(rev, script)`, i.e. `BAD-ROW(unpinned-instrument)` otherwise. Kills the `6213530`/`ed1ccd6` route and would force L06/L32 to be reported as unbound, which is the honest reading.
2. Literal identity: require `lit == lit0` (after backtick/space strip) instead of integer-multiset equality. Kills `4a4`, `27d6`, `15CFG-15`, `11.0`, the HTML and source fragments, and the `29 failed=0` re-quotation.
3. Record scope: require the target to be the cell's own named evidence pointer, or at least a `census/round-<N>/records/`/verification record that contains the cell's `basecmd` string; exclude `.py`, `.html`, `.raw` and `sources/` targets. Kills Findings 1, 6 and 8.
4. When the enumeration supplies a `basecmd`, forbid (or additionally execute and report) the record branch, so a stale cell cannot become green by provenance alone.

Rejected as a tradeoff, not a defect: a calibration axis cannot be closed by a counter that reads self-assessment records while the cells stay as written. If the L1 wants this target, the axis attribution must be restated as bookkeeping/accountability; if it keeps the calibration attribution, the target has to be about re-derived counts, not pointers. That is a judgment call the canonical judge must reject either way — no counter change can make a historical pointer into a current measurement.

## Deliveries

- `.ufo/waves/round-31/w1/SwarmCritic28.md` (this report). No other file was written outside `/fast/scratch/hyaku/souji-r31/AttackC1/`, which was removed.
