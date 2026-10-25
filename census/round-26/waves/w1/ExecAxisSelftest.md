# ExecAxisSelftest — C3 `--selftest` design (round 26, w1)

## Status

STATUS: PASS — spec delivered at `.ufo/waves/round-26/w1/souji-axis-check-selftest.md` (27 embedded
cases, `selftest=N/N pass` terminal line, full exit contract, 7 unexercised frozen checks named).
Implementation is the C3 owner's: the committed tool has no `--selftest` at all (F1).

## Evidence

All commands from `/home/vgpnk/Projects/shokunin/souji-shokunin`, `python3 -B`, read-only.

| # | command | excerpt | revision |
|---|---|---|---|
| E1 | `git rev-parse HEAD` | started at `4453128`; C3 landed as `0833de9` mid-task; final HEAD `d6c13b0f00066cbb342fdc50167849a5f1c726e5` | d6c13b0 |
| E2 | `git show 0833de9:tools/souji-axis-check.py \| grep -c selftest` | `0` | 0833de9 |
| E3 | `sha256sum` on both blobs, at `0833de9` **and** at `d6c13b0` | tool `14bc9632e88ef58f18108011f6645bd970cd825d0ffc1664369dc60b0d579332`; fixture `2ffc18289fc82b9075ad3580cb9bec6a80384061c7d294b5aa17dbf9ca93c8da`; identical at both revisions | d6c13b0 |
| E4 | `python3 -B tools/souji-axis-check.py --selftest` | `usage: souji-axis-check.py [-h] --prereg PREREG --scorecard SCORECARD` / `error: ... required: --prereg, --scorecard`; `rc=2` | 0833de9 |
| E5 | `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` | `claims=3 flags=0`; `rc=0` | 0833de9 |
| E6 | `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py` | last lines `case=11 ... verdict=PASS` then `cases=11 pass=11`; `rc=0` | 0833de9 |
| E7 | same fixture with `--stub` | `cases=11 pass=4` / `control=FALSE-GREEN-REJECTED`; `rc=1` | 0833de9 |
| E8 | draft state before E1's landing (untracked `a3fb1859…`, mtime 14:24) | check mode died `KeyError: 0` at `main:143` and fixture read `cases=11 pass=1`; fixed in `0833de9:98` (`return scores, None`) | draft |

Sources opened this run, with located quotes (no `|`):

- `.ufo/waves/round-26/preregistration.txt`, C3 fixture section: "last stdout line: `cases=12 pass=12 control=FALSE-GREEN-REJECTED`".
- same file, R4: "a claim text containing a whole-word all/every/complete/none/no without a same-claim `enumerate:` line".
- `tools/souji-receipt-run.py:69-77`: "selftest=(?:PASS|FAIL) ids=\d+/\d+)(?=\s|$)".
- `tools/souji-axis-check.py:31` (committed): "OWNED_AXES = ("calibration", "operability", "coverage")".
- `tools/souji-rev-pin.py:252-264,386-389` and `tools/souji-gate-check.py:288-290`: the two selftest shapes the spec merges.

Scratch: none created (`/var/tmp/souji-r26-ExecAxisSelftest` never needed; no `souji-axis-check-selftest-*` remains).
No tool installed or upgraded.

## Findings

1. **F1 (blocker for the assigned mode) — `--selftest` does not exist.** `tools/souji-axis-check.py`
   argparse `:134-135` marks both paths `required=True` and the committed blob contains zero
   occurrences of `selftest` (E2, E4). The assignment's entry point exits 2 in argparse before any
   rule runs. Fix is spec §7.1: optional paths at parse time, `--selftest` short-circuit before any
   file open, check-mode requirement enforced in `main`.
2. **F2 — R3 is order-dependent under a tie.** `:126` `min(scores, key=lambda a: scores[a])` picks
   the first-inserted key of the parse order, so with `calibration 7` and `coverage 7` a claim on
   `coverage` is flagged. The real SCORECARD has a unique lowest (`calibration 7`), so K1 is
   unaffected; the defect is latent until an axis score moves. Remedy is a minima-set comparison
   (spec §7.2), which is an undefined-input clarification, not a predicate change.
3. **F3 — the axes-table scan is not bounded to the axes table.** `parse_scores:89` spans
   `^## Axes\b(.*?)(?=^## )`, and the `### Round NN measurements` blocks sit before the next `## `
   heading, so their rows are matched by the same table-row pattern (pipe, one word, pipe, one
   integer, pipe). A measurements row whose
   first cell is an owned axis name and second cell an integer would overwrite the score and move
   the R3 target. No current row has that shape; it is a one-edit-away false green. Spec case C13
   pins it.
4. **F4 — R4 as implemented is not the frozen R4.** Frozen text predicates on claim *text*; the tool
   parses only the MACHINE BLOCK, so claim text is not an input at all. The substitute (`:115-123`)
   (a) flags any claim block without `enumerate:` regardless of universal words, and (b) flags a
   universal word *inside the `enumerate:` value* — inverting the rule, since `enumerate:` is what
   the frozen sentence accepts as the discharge. The "naming its counting command" limb is unchecked.
   Recorded, not changed: K1 passes either way, and narrowing R4 now would be a post-data
   relaxation.
5. **F5 — the fixture's case 1 is not the frozen case 1.** Frozen C3 case 1 is the r25-C2 replica
   (a `fixture-expansion` claim declared on `operability`) flagged as the discriminator;
   `tests/fixtures/r26-axis-check.py` case 1 is `axis: freshness` (an R1 case) and the
   fixture-expansion mismatch appears only as case 3 on `calibration`. The discriminator shape is
   therefore not carried by the fixture. My spec covers it as C3, and its stub arm as C22 — but C3's
   K2 stays unmet by an additive instrument.
6. **F6 — frozen K2's literal is not producible by the committed fixture.** Frozen: one terminal
   line `cases=12 pass=12 control=FALSE-GREEN-REJECTED` (quote above). Measured: normal invocation
   ends `cases=11 pass=11` with no `control=` field, rc 0; the control verdict appears only in the
   separate `--stub` invocation, where `cases=11 pass=4` precedes it and rc is 1 (E6, E7). Two
   independent gaps: 11 cases, not 12; and no single invocation emits both the pass count and the
   control verdict on one line. K2 as frozen cannot be satisfied without either a fixture change or
   an amendment; that is an L1 call, reported here because it is a counter-shape fact.
7. **F7 — the assigned terminal line is invisible to the receipt binder.** `COUNTS_RE`
   (`tools/souji-receipt-run.py:69-77`) accepts a selftest spelling of the form `selftest=` plus
   PASS-or-FAIL plus ` ids=` plus two integers, and `cases=` plus a pass count; it does not match
   `selftest=N/N pass`. If `c3-counter.sh` echoes only the tool's terminal line, the receipt gets
   no counts line. Remedy belongs in the counter (print `cases=NN pass=NN`), not in a second tool
   convention; the spec's terminal spelling is kept as assigned.
8. **F8 — R1's "non-retired" limb is vacuous.** The rule filters on `OWNED_AXES`, which is exactly
   the three non-retired axes; a retired *owned* axis cannot be expressed, so R1 can never flag one.
   No harm today; the spec's `SC_RETIRED` world exercises the limb through R3 instead, and U-list
   records the residue.
9. **F9 — point-in-time correction, no action.** During this task the untracked draft crashed
   (`KeyError: 0`) on every check-mode run and the fixture read `1/11`; landing `0833de9` fixed
   `:98` and both readings moved to `claims=3 flags=0` / `11/11` (E8 → E5, E6). The spec was
   re-pinned to `0833de9` afterwards; no claim in it rests on the draft's behaviour except as
   labelled history.

## Attack log

Report-only; no amendment is proposed and no predicate is asked to move after data.

- **A1 — R2's neutral set is an escape hatch (strongest).** The frozen R2 map is closed at five
  surface classes. The tool adds `NEUTRAL_SURFACES = {"receipt-binding", "measurement"}` (`:41`),
  which pass on *any* axis. A claim can therefore relabel its surface `measurement` and clear R2 with
  no consistency obligation — exactly the misattribution R2 exists to catch, with a one-word
  bypass. The round's own C3 declares `instrument-acquisition`, so it is not self-serving today.
  Strictest available remedy (needs an L1 pre-data ruling, not a seat decision): reject any
  `surface-class` outside the frozen five, i.e. make the set closed rather than partly neutral.
  My spec pins the current behaviour as C7/T5 so the bypass is at least visible and not silent.
- **A2 — R4 reduces to "write any enumerate line".** Any non-universal `enumerate:` value clears the
  rule; `enumerate: bash true` names no counting command and passes. Combined with F4, a claim whose
  prose says "all" can always clear R4 by adding an arbitrary command string.
- **A3 — K2's count line is self-asserted.** `cases=N pass=N` is the fixture's own arithmetic over
  its own case list; nothing binds `N` to the frozen inventory. A fixture that declares 12 cases and
  runs 11 real ones plus a tautology still prints `cases=12 pass=12`. The only present defence is
  that the committed fixture honestly prints `11`. Counter-side fix would be an independent case-ID
  set check (the r23 `self-noise`/`REQUIRED_CASE_IDS` shape).
- **A4 — R3 accepts a decorative claim.** A claim on the lowest axis with a trivial enumerate
  discharges R3 while changing nothing. Frozen by design (R3 is an axis-presence rule, not a
  quality rule); recorded so no reader mistakes `flags=0` for evidence the round targets its weakest
  axis substantively.
