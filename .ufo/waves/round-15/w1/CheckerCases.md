# CheckerCases — C2 case-ID universe, vacuity and expected-set review (round 15, w1)

Seat: `SoujiR15.CheckerCases` (reviewer). Axes: operability, calibration.
Scope: case-ID identity (missing / duplicate / unknown), zero-case vacuity, and the independent literal expected universe for the C2 preservation checker.
Mode: **design-only.** `tools/souji-preservation-evidence.py` and `tests/fixtures/r15-preservation-evidence.py` are **absent** from the working tree and from `HEAD` (`cc21683`). Findings below are grounded in committed round-14 artifacts, the round-15 contract, and the canonical rules. Nothing was executed.

Executed by this seat: read-only inspection (`read`, `grep`, `glob`, `git log -S`, `git show <rev>:<path>`). No fixture, tool, census, or checker was run. No credential, operator-sweep, `agent.db*`, or sibling file was opened. No tools were installed or updated.

## Verdict

**Not admissible as specified.** The contract names the right properties (pinned literal expected ids, strict expected set, zero-case rejection), but the round-14 artifacts that a round-15 checker would most naturally inherit already violate them. The round-14 plan pins 9 ids while the landed fixture has 12, and the fixture's own id-set guard cannot fire. A checker that trusts those artifacts would certify missing or failing cases 10–12. The acceptance criteria in section 4 are required before the checker is built.

## 1. Evidence: the r14 case universe is 12, and the plan pins 9

| Artifact | Ids | Source |
|---|---|---|
| Landed fixture `tests/fixtures/r14-census-boundary.py` (commit `48f8945`) | **12**: `R14C2-01`..`R14C2-12` | `:45–58` `EXPECTED_IDS` tuple; `:629–` `CASES` dict |
| Recorded changed-arm run `census/round-14/verification.json` (measured `552cae4`) | 12 `CASE` rows, all PASS (`R14C2-01`..`12`) | line 78 (`stdout`) |
| Recorded baseline-arm run (a31642d) | 12 cases, `PASS=2 FAIL=10`, `SUMMARY total=12 failed=10` | `corpus/lessons/round-14-verifier-spotcheck.md:96` |
| `.ufo/waves/round-14/w1/CensusBoundary.md` (report) | "all twelve PASS"; `total=12` | `:147–149`, `:176–178`, `:208` |
| `census/round-14/verification-plan.json` (committed at `cc21683`) | **9**: `R14C2-01`..`09` | `:891–900` `expected_ids`; `:903–911` `case_meanings_from_code` (9 entries) |

The plan's note at `verification-plan.json:914` says *"This plan uses the landed case table."* That is false for the case count. `cc21683` contains zero occurrences of `R14C2-1[0-2]` in the plan. Cases 10–12 were added in `48f8945` (`git log -S'R14C2-10'`), and the plan was not updated.

## 2. Findings

### F1 — High, calibration: the plan's green and red checks are blind to cases 10–12

- Green (`verification-plan.json:858`): `grep -c '^CASE\tR14C2-0[1-9]\tPASS\tok$' … = 9`. The regex `0[1-9]` matches only `01`–`09`. If `R14C2-10`, `-11`, `-12` all FAIL, the count is still 9 and the check passes. The comment at `:861` ("Every one of the nine named cases must PASS") is therefore not what the check enforces.
- Red (`:872`): the baseline loop covers `01 02 03 04 05 06 09` plus positive controls `07`, `08`. Cases `10`–`12` are never asserted red on baseline.
- Consequence: the plan would have accepted a run in which the three newest namespace protections (linked-worktree commondir, two-hop alternates, fleet child symlink) fail, and it would not have detected a baseline that passes them. This is the same class as the round-14 closure's "narrow tested cases cannot cancel contraction" (`round-14-verifier-spotcheck.md:104–106`).
- Operability corollary: the round-15 `RoundRunner` must not reuse this plan's mapping, or it will either green-light a 12-case run with 10–12 broken or reject a correct 12-case run.

### F2 — High, calibration: the fixture's id-set guard is tautological

`tests/fixtures/r14-census-boundary.py`:

- `:674` `selected = list(args.case) if args.case else list(EXPECTED_IDS)`. With no `--case`, `selected` *is* the fixture's own tuple.
- `:708–721` appends every `cid` in `selected` to `ran` with no skip path (exceptions propagate; there is no `continue`).
- `:722` `if not args.case and tuple(ran) != EXPECTED_IDS:`. When `--case` is absent, `ran == list(EXPECTED_IDS)` by construction, so this comparison is always False. **The id-set FAIL at `:724–727` can never fire.**
- `:670–671` `--list` prints the same tuple. The fixture therefore agrees with itself; nothing independent pins the universe.
- `CASES` (`:629–`) is never cross-checked against `EXPECTED_IDS`. A case present in `CASES` but dropped from the tuple is silently never run, and nothing fails.
- `:674` / `:722`: with `--case`, the id-set check is skipped entirely. `--case R14C2-07` yields `SUMMARY total=1 failed=0`, exit 0, which is a partial-run green. `--case` also accepts repeats, so duplicate `CASE` rows are possible.
- The gate table at `SKILL.md:140` lists "fixture EXPECTED_IDS … 1 failed case/id-set" as a control. As landed, the id-set failure mode is unreachable.

Required: the checker must not trust any fixture-internal tuple, `--list` output, or `SUMMARY` line as its expected universe (see §4 A1–A3).

### F3 — High, calibration: zero-case and SUMMARY-only acceptance

- `all(...)` over an empty `CASE` list is `True` in Python. A checker written as `all(c.status == "PASS" for c in cases)` passes a zero-case record.
- `verification-plan.json:82` already defines the correct rule: "the fixture executes zero cases … Record as could-not-evaluate; never count it as pass." `:861` says "the SUMMARY line alone could be forged by a zero-case run." The r15 checker must enforce both, and the plan's only defence (the count of 9, F1) is itself broken.
- `SUMMARY total=N` must be checked as a derived count, not trusted: `N` must equal the number of `CASE` rows, which must equal the pinned literal cardinality.

### F4 — High, calibration: missing, duplicate and unknown ids are not specified

The round-15 spec (`w1-spec.json` AdmissionChecker prompt) says "strict expected case set" but does not define the comparison. A count-only check is insufficient. Example: 12 rows containing `R14C2-05` twice and no `R14C2-12` pass `count == 12`.

Required comparison: multiset equality between the record's `CASE` ids per arm and the pinned literal (`Counter(ids) == Counter(PINNED)`), so that missing, duplicate and unknown ids each fail independently. Note that `R14C2-1O` (letter O) and `R14C2-13` are the realistic typos and must be caught as unknown.

### F5 — High, calibration: baseline "FAIL" is not evidence of red

- The r14 baseline arm recorded exit-2 fixture-setup failures in attempt 1. The closure states these "are not counted as baseline red proof" (`round-14-verifier-spotcheck.md:102`). A checker that counts any `FAIL` as red would admit setup breakage as discrimination.
- `R15-M1`'s fix text requires the baseline red to be "for the routed reason" (`corpus/lessons/round-15.md:9`). Each baseline-red id must pin its expected finding or reason, not just `FAIL`.
- `tests/fixtures/r14-census-boundary.py:710–715` keys its baseline expectations to one digest (`BASELINE_SHA = 6a000c59…`, the a31642d bytes). The round-15 baseline is `cc216…`, whose bytes are the r14 installed tool, so `TOOL-KIND` will read `other` and the access requirement is skipped. The checker must bind arms by the **record's declared digest** against the pinned bytes, not by the fixture's `TOOL-KIND` text. The r14 per-id expectations (`07`/`08` PASS, rest FAIL) describe a31642d and must not be reused for the r15 baseline.

### F6 — Medium, calibration: the benign-control universe does not exist yet

Q22 (`corpus/QUALITY.md:56`) requires paired controls the round-14 universe lacks: benign-local-config (for example `core.hooksPath=/dev/null`), mixed-fleet survival of unaffected rows, and preserved dirty counts. None are in any committed fixture. The round-14 closure found the 12 namespace cases contain no benign preservation control (`round-14-verifier-spotcheck.md:106`). The r15 universe is therefore `R14C2-01..12` (namespace, pinned at **12**, not 9) plus a new, explicitly versioned benign family. The new ids are unknown until `ConfigFixture` lands; the checker must pin them at landing, not infer them.

### F7 — Medium, operability: a stale pin would wrongly reject valid evidence

If the checker pins 12 and R15 adds benign ids without a versioned pin change, every valid R15 record is rejected (`exit 1`/`2`), and the operator cannot tell a regression from a stale pin. Conversely, pinning 9 (the plan's count) would accept a record that omits cases 10–12. The pin must be a single versioned literal tied to the fixture's sha256 (see A4), with a changelog line in the checker's header.

### F8 — Low: the exit mapping for case-ID failures is unpinned

The contract maps 1 = honest failed evidence and 2 = malformed or tampered. It does not say which case-ID failure is which. Recommended mapping (for the checker owner to pin):

- `2`: missing required arm or case, duplicate id, unknown id, zero cases, `--case`-partial record, fixture digest mismatch, baseline arm exit 2 / setup failure.
- `1`: complete well-formed record where a changed-arm id is FAIL, a baseline benign control PASSes (no discrimination), or namespace is not 12/12 on changed.
- `0`: all of the above hold for both arms.

## 3. What is sound in the contract

- Pinned literal ids are the correct direction. `r13-quarantine-bounds.sh:278–279` and `r12-maintenance-guard.sh` already pin an independent expected set, and `QUALITY.md` Q19 names "independent expected finding ids" as the admission bar.
- Exit 2 for "fixture executes zero cases" is the correct could-not-evaluate mapping (`verification-plan.json:82`).
- The checker's own selftest should be discriminating, not merely green (AdmissionChecker prompt).

## 4. Acceptance needed (design-only; binding for the checker build)

**A1 — literal universe owned by the checker.** The checker carries its own literal tuple for `R14C2-01..12` and the R15 benign ids. It never derives expected ids from the fixture's `EXPECTED_IDS`, `--list`, `CASES`, or `SUMMARY`. Note the tension in the spec ("pinned literal expected ids in fixtures"): if the literal lives only in the fixture, a tampered fixture can shrink its own tuple. Require both: the fixture literal is asserted equal to the checker literal, and the fixture's sha256 is pinned in the checker (A4).

**A2 — set-and-multiplicity comparison per arm.** `Counter(record_ids) == Counter(PINNED)` for baseline and changed separately. Any missing, duplicate or unknown id fails. Zero rows fails.

**A3 — derived counts only.** `SUMMARY total` must equal `len(CASE rows)` and the pinned cardinality. The `SUMMARY` line alone never satisfies a check. A record with no `CASE` rows is exit 2 (could-not-evaluate).

**A4 — fixture and arm digest binding.** The record carries the fixture sha256 and each arm's tool sha256. The checker compares them to pinned constants; it does not trust the record's own digest field alone, and it does not execute the fixture to check.

**A5 — no partial runs.** A record produced with `--case` (any subset) is exit 2. The recorded command must be the full-universe invocation.

**A6 — per-id expected verdict map.** Pinned per arm: namespace ids PASS on changed and on the r14-installed baseline (12/12); each benign id FAIL on baseline **with its pinned routed reason** and PASS on changed; mixed-fleet and dirty-count ids as pinned. A baseline `exit 2` or setup failure for any id is exit 2, never red.

**A7 — discriminating selftest.** The checker's self-invocation negative controls must each produce the mapped exit and must include at least: (a) one id missing, (b) one duplicate with one missing, (c) one unknown (`R14C2-1O`), (d) zero rows, (e) SUMMARY-only forgery, (f) a `--case`-partial record, (g) the stale **9-id** plan universe presented as complete, (h) green-only baseline (no red), (i) baseline setup exit 2 presented as red, (j) fixture digest mismatch. The positive control is the complete 12 namespace plus pinned benign set on both arms.

**A8 — do not inherit the r14 plan.** `census/round-14/verification-plan.json` (9-id mapping, `:858`, `:872`, `:891–900`) is historical and is not an input to the r15 checker or runner. `RoundRunner` must take the pinned universe from the checker/fixture, and the r14 plan must be left unedited (historical).

## 5. Residual risk and verification gaps

- No r15 fixture or checker exists, so none of A1–A8 can be exercised. Every finding is source-level. Nothing was run.
- Benign-family ids are unknown until `ConfigFixture` lands. A6 for benign ids is design-only.
- The r14 namespace case *content* (the `contract:`/`access:` oracles) was not reviewed here; that belongs to the fixture reviewers (`FixtureOracles`, `FixtureAccess`).
- Digest binding of the installed tool to measured bytes is `CheckerBindings`' scope; A4 only states the case-level requirement.
- Round-14 `verification.json` case rows were read from committed text, not re-executed; the 12-row figure is observed committed evidence, not a fresh measurement.

## 6. Unrun checks for L1

Only after the checker and fixture land (none were run here):

1. `python3 tests/fixtures/r15-preservation-evidence.py --selftest`, expect pass and the A7 controls each mapped to their exit.
2. Static check: the fixture literal and the checker literal are equal (no execution).
3. Confirm no `--case` path in the recorded command; confirm `SUMMARY total` equals the `CASE` row count on each arm.
4. Confirm `census/round-14/verification-plan.json` is unedited and unused by the r15 runner.


## 7. Agreed with CheckerSchema (controlling statements)

- CASE rows carry structured fields: `observed_exit`, `observed_finding`, `observed_stdout_empty`. Free-text detail is not evidence.
- Benign IDs: `R15C1-B1` (hooksPath=/dev/null), `R15C1-B2` (other pinned benign local keys), `R15C1-M1` (mixed fleet), `R15C1-D1` (dirty-count control). The superseded names `B1`/`B2`/`M1` are not used.
- Arm role: a baseline arm is red only if the repo uses a key the cc21683 guard refuses; otherwise it is a retention control with changed-green only. The routed reason applies only to red arms. R14C2-01..12 are retention controls on the r14-installed baseline.
- R15C1-M1 baseline: `observed_exit` 2 and zero census data rows, with its own CASE verdict. The zero-row abort is census-level, not zero CASE rows.
- Zero-CASE rule: counted per arm over CASE rows, never read from `observed_exit`. A row with `observed_exit` 2 is a valid CASE row. A record with zero CASE rows on either arm is exit 2.
- Known residual: r14 refusal checks match only the substring `path-protected`, not the reason (`tests/fixtures/r14-census-boundary.py:486-487`).

## Tooling

No tools were installed, upgraded or removed by this seat. `git` was used read-only (`log -S`, `show <rev>:<path>`).

## 8. No-query boundary disclosure

Early in this seat, before the boundary reminder, two broad calls ran over the whole lane root, which includes the operator-authored `census/operator-sweep-20261019/`: a glob of `/home/vgpnk/Projects/shokunin/souji-shokunin` (limit 200, gitignore false) and a grep for `checker|admission|preservation` over the same root (gitignore false). The glob returned operator-sweep file and directory names; the grep output was truncated at 200 results, so whether it matched operator-sweep content is unknown. No operator-sweep file was opened, copied, edited or staged. Later calls were limited to named source, tool, test and round-14/round-15 paths, plus read-only `git log`/`git show` of committed revisions. No runtime probe or test was run.
