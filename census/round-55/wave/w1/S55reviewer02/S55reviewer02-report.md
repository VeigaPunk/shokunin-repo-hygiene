# S55reviewer02 — C2 counter v4 attack report (round 55, reviewer)

Target: `census/round-55/c2-counter.py` sha256 `e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c` (verified).
Lane tip at dispatch `3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f`; measured revision `4b10ddd1741a948c89d283358affd1da2ab3fd95`.
Pins verified before probing: c1-counter, c2-counter, build-fixtures.py, run-matrix.sh, both selftest expected TSVs, tool digest `e7e7…a067a5b` (all match the prereg).

## Verdict

- **Frozen kill rule holds on the committed bytes.** No attack state changed the committed verdicts (see §1).
- **One regression against the prereg Target clause** ("keeps every v3 check"): v4 silently accepts receipt unknown keys beginning with a digit or underscore (`1KEY=x`, `_KEY=x`, `2=x`), which the frozen v3 refused as RECEIPT-UNKNOWN-KEY. The committed fixtures do not cover this, so the kill rule is not tripped. Routed as R-A (§4). I did not edit frozen bytes.
- Four routed defects / named limits beyond the regression (R-B..R-E, §4), and two prediction errors of mine that are corrected below (§5).
- Zero edits, zero commits, zero git mutations; no tools installed; scratch deleted.

## 1. Frozen kill rule — checks run

| Check | Command (from lane root, TMPDIR=scratch) | Result |
|---|---|---|
| Real lane at dispatch tip | `c2-counter.py --root LANE --rev 3ce0ba036275… --capture census/round-55/records/fleet-root-census.tsv --receipt …-run.txt --tool-sha256 e7e7…a067a5b` | exit 0, `receipt=ok sorted=ok tool_pin=ok` |
| Real lane at measured revision | same, `--rev 4b10ddd1741a…` | exit 0, `tool_pin=ok` |
| Committed selftest (builder + expected pins) | `--selftest --work SCRATCH --builder-sha256 e629… --expected-sha256 6339…` | exit 0, `SELFTEST pass cases=15` |
| Matrix regenerated with the L1's `run-matrix.sh` | rebuilt fixtures into scratch, ran all four arms | `c1-matrix-v3`, `c1-matrix-v4`, `c2-matrix-v3`, `c2-matrix-v4` **byte-identical** to committed |
| FH-HONEST / FH2 under v4 | matrix row | exit 0 |
| FB1 / FB2 / FB3 under v4 | matrix row | exit 1 (named COMMENT-AMBIGUOUS-NAME / RECEIPT-UNKNOWN-KEY ×2) |
| FB1 / FB2 / FB3 under frozen v3 | matrix row | exit 0 (v3 arm acceptance control holds) |
| FA1–FA8 carry-over | matrix rows + selftest | identical exit and finding |
| FA9 / FB4 arms | selftest | FA9 rc 1 `TOOL-SHA-ARG-MISMATCH`; FB4 rc 2 `TOOL-SHA-ARG-MALFORMED` |

Receipts: `real-lane-and-selftest.txt`, `matrix-regen/` (4 TSVs + `diff-vs-committed.txt`).

## 2. Attack states (54 real-lane fixture commits, each run through v4 AND frozen v3)

Each state is a scratch git repo built from the FH-HONEST grammar; `CAPTURE_SHA256`/`ENTRIES` recomputed from the edited bytes so only the tested surface fires. Predictions were written from the counter source before running. Full command, exit, stdout, and capture/receipt bytes per state: `receipts/A01.txt`…`receipts/A54.txt`; table: `attack-table.tsv`.

Classes: **NEW** = v4 instruments (refuses by name or recognizes-and-validates) where v3 did not; **CO** = carry-over (v3 and v4 agree); **NL** = named limit (prereg list); **RD** = routed defect proposal.

| ID | State | v4 exit / first finding | v3 exit | Class |
|---|---|---|---|---|
| A01 | `#` body row, 1 tab | 1 COMMENT-AMBIGUOUS-NAME | 0 | NEW |
| A02 | `#` body row, 2 tabs | 1 COMMENT-AMBIGUOUS-NAME | 0 | NEW |
| A03 | `#` body row, 3 tabs | 1 COMMENT-AMBIGUOUS-NAME | 0 | NEW |
| A04 | `#` body row, 4 tabs (5 fields; FB1 replicate, new name) | 1 COMMENT-AMBIGUOUS-NAME | 0 | NEW |
| A05 | tab-only comment `#\t` | 1 COMMENT-AMBIGUOUS-NAME | 0 | NEW |
| A06 | header `# FLEET_HEAD=…<TAB>x` | 1 COMMENT-AMBIGUOUS-NAME | 1 CAPTURE-RECEIPT-MISMATCH | NEW |
| A07 | header `# ENTRIES=3<TAB>` | 1 COMMENT-AMBIGUOUS-NAME | 1 CAPTURE-RECEIPT-MISMATCH | NEW |
| A08 | `#a<TAB>b<TAB>c<TAB>d<TAB>e` (**labelled "5-tab" in receipt — actually 4 tabs**, see §5) | 1 COMMENT-AMBIGUOUS-NAME | 0 | NEW |
| A09 | header `# SCOPE=…<TAB>…` | 1 COMMENT-AMBIGUOUS-NAME | 0 | NEW |
| A10 | capture header `#  TOOL_SHA256=<valid>` (two spaces) | 1 CAPTURE-RECEIPT-MISMATCH TOOL_SHA256 … capture=- | 1 same | RD-C |
| A11 | capture header `#ENTRIES=3` | 1 CAPTURE-RECEIPT-MISMATCH ENTRIES … capture=- | 1 same | RD-C |
| A12 | capture header `# ENTRIES=3 ` (trailing space) | 1 CAPTURE-RECEIPT-MISMATCH ENTRIES … capture=- | 1 same | RD-C |
| A13 | capture header `# entries=3` (lowercase) | 1 CAPTURE-RECEIPT-MISMATCH ENTRIES … capture=- | 1 same | RD-C |
| A14 | capture header unknown `# GENERATOR=x` | 0 | 0 | NL (prereg: CAPTURE-header unknown keys ignored) |
| A15 | capture header prose comment, no tab | 0 | 0 | NL (NL-2) |
| A16 | receipt `#  TOOL_SHA256=x` (two spaces, non-hex) | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | CO (named) |
| A17 | receipt `#  TOOL_SHA256=<valid>` | 0 | 1 MALFORMED | NEW (recognized+green) |
| A18 | receipt `#TOOL_SHA256=<valid>` (no space) | 0 | 1 MALFORMED | NEW (recognized+green) |
| A19 | receipt `# receipt_version=1` (lowercase known) | 0 | 1 MALFORMED | NEW (recognized+green, as prereg requires) |
| A20 | receipt `# Receipt_Version=1` (mixed-case known) | 0 | 1 MALFORMED | NEW |
| A21 | receipt `# tool_sha256=x` (lowercase known, bad value) | 1 RECEIPT-MALFORMED | 1 | CO |
| A22 | receipt `# Generator=x` (mixed-case unknown) | 1 RECEIPT-UNKNOWN-KEY | 0 | NEW |
| A23 | receipt `# GENERATOR=x   ` (unknown, trailing spaces) | 1 RECEIPT-UNKNOWN-KEY | 1 | CO |
| A24 | receipt `#BUILDHOST=fixture` (no space; FB3 replicate) | 1 RECEIPT-UNKNOWN-KEY | 0 | NEW |
| A25 | receipt `# GENERATOR=fixture builder` (internal space) | **0 (silent)** | 0 | RD-B |
| A26 | receipt `# BUILD-HOST=x` (hyphen) | **0 (silent)** | 0 | RD-B |
| A27 | receipt `# GENERATOR=` (empty value) | **0 (silent)** | 0 | RD-B |
| A28 | receipt `# 1KEY=x` (digit-initial unknown) | **0 (silent)** | **1 RECEIPT-UNKNOWN-KEY** | **RD-A (regression)** |
| A29 | receipt `# GENERATOR=x<TAB>y` | **0 (silent)** | 0 | RD-B |
| A30 | receipt duplicate `ENTRIES` (`# ` and `#`) | 1 RECEIPT-MALFORMED | 0 | NEW |
| A31 | receipt duplicate `TOOL_SHA256` (upper + lower) | 1 RECEIPT-MALFORMED | 0 | NEW |
| A32 | receipt `CAPTURE_SHA256` uppercase hex | 1 RECEIPT-MALFORMED | 1 | CO |
| A33 | receipt `ENTRIES=03` | 1 CAPTURE-RECEIPT-MISMATCH | 1 | CO |
| A34 | receipt `FLEET_HEAD=<head>=x` | 1 RECEIPT-MALFORMED | 1 | CO |
| A35 | receipt known key, valid value, trailing spaces | 0 | 1 MALFORMED | NEW (tolerance) |
| A36 | CRLF receipt, LF capture | 1 RECEIPT-CRLF | 1 | CO |
| A37 | CRLF capture + CRLF receipt | 1 CAPTURE-CRLF (first) | 1 | CO |
| A38 | CRLF receipt + correct pin | 1 RECEIPT-CRLF (first); `tool_pin=ok` in SUMMARY | — | CO |
| A39 | single CR on the `ENTRIES` receipt line | 1 RECEIPT-CRLF | — | CO |
| A40 | CRLF capture with `#`-tab comment | 1 CAPTURE-CRLF (first; CR check precedes comment check) | — | CO (ordering) |
| A41 | pin 63-hex | 2 CANNOT-EVALUATE TOOL-SHA-ARG-MALFORMED | 2 generic `must be 64-hex` | NEW (NL-5 named) |
| A42 | pin 65-hex | 2 TOOL-SHA-ARG-MALFORMED | 2 generic | NEW |
| A43 | pin uppercase 64-hex | 2 TOOL-SHA-ARG-MALFORMED | 2 generic | NEW |
| A44 | pin mixed-case 64-hex | 2 TOOL-SHA-ARG-MALFORMED | 2 generic | NEW |
| A45 | pin correct lowercase | 0; `tool_pin=ok` | — | NEW (tool_pin field) |
| A46 | pin wrong lowercase | 1 TOOL-SHA-ARG-MISMATCH | 1 | CO (FA9 shape) |
| A47 | pin empty string | 2 TOOL-SHA-ARG-MALFORMED | 2 generic | NEW |
| A48 | pin with leading space | 2 TOOL-SHA-ARG-MALFORMED | 2 generic | NEW |
| A49 | malformed pin AND capture absent | 1 PRISTINE FAIL FLEET-CENSUS-ABSENT | 1 same | NL (ordering: pin check runs after capture/tool reads; still non-zero, not named as pin) |
| A50 | malformed pin AND tool absent at rev | 2 CANNOT-EVALUATE tool absent | 2 same | NL (ordering) |
| A51 | capture absent, no pin | 1 PRISTINE FAIL | 1 | CO |
| A52 | receipt absent | 1 RECEIPT-MALFORMED | 1 | CO |
| A53 | receipt present, empty | 1 RECEIPT-MALFORMED | 1 | CO |
| A54 | rev 12-hex (not full 40) | 2 CANNOT-EVALUATE full 40-hex | 2 | CO |

Totals: 54 states; 4 prediction mismatches (A10–A13, all same cause, §5); v4 green where the prereg requires green: A14, A15 (named limits), A17–A20, A35, A45, A25–A27, A29 (silent, see RD-B), A28 (silent, see RD-A).

## 3. Selftest / pin attacks on the FA9/FB4 arms (modified expected TSVs in scratch; committed TSV untouched)

Receipts: `selftest-variants.txt`.

| Case | Edit | Result |
|---|---|---|
| ST02 | FA9 expected exit 0 | SELFTEST fail, rc 1 (`want_rc=0`, got 1) — kill power |
| ST03 | FA9 expected finding `ROWS-UNSORTED` | SELFTEST fail, rc 1 — finding is enforced |
| ST04 | FB4 expected exit 1 | SELFTEST fail, rc 1 (got 2) — kill power |
| ST05 | FA9 expected finding `-` | pass, rc 0 — wildcard skips finding check (RD-E) |
| ST06 | FB4 row dropped | fail, rc 1 (`want_rc=None`) — missing row is a fail |
| ST07 | FB1 expected finding `ROWS-UNSORTED` | fail, rc 1 — finding is enforced |
| ST08 | rows reordered | pass — order-independent (expected) |
| ST09 | expected TSV with CRLF endings | pass (splitlines) — expected |
| ST10 | FA9 row space-separated instead of tab | **rc 1, uncaught `IndexError` traceback, no SELFTEST line** (RD-D) |
| ST11 | FH-HONEST row dropped | fail, rc 1 |
| ST12 | FA1 expected exit 0 (carry-over) | fail, rc 1 — carry-over kill power |
| ST13 | FH2 expected exit 1 | fail, rc 1 — carry-over kill power |

## 4. Routed defects and named limits (no edits to frozen bytes)

**RD-A — v3 check regression (highest priority). Reproduction: `receipts/A28.txt`, `receipt-key-differential.txt`.**
v3 `RECEIPT_KV = re.compile(r'# ([A-Z0-9_]+)=(\S+)')` accepts any first character in `[A-Z0-9_]`, so `1KEY=x`, `_KEY=x`, `2=x` are refused as RECEIPT-UNKNOWN-KEY. v4 `RECEIPT_KV = re.compile(r'\s*#\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S+?)\s*')` requires a letter first, so these lines are silently ignored (exit 0). Differential: `1KEY=x` v3=1 / v4=0; `_KEY=x` v3=1 / v4=0; `2=x` v3=1 / v4=0. Prereg Target says "keeps every v3 check"; this clause is not satisfied for these shapes. Not in the kill set, not in any fixture. Proposed fix (r56): restore the first-character class to `[A-Za-z0-9_]` and add an FB5 fixture `# 1KEY=x` expecting RECEIPT-UNKNOWN-KEY.

**RD-B — silent gap for KV-shaped unknown receipt lines (not in the prereg named-limit list; present in v3 too).** Reproduction: `receipts/A25–A27,A29.txt`, `receipt-key-differential.txt`.
Silently accepted (exit 0): `KEY-1=x`, `KEY.1=x` (hyphen/dot in key), `KEY=x y` (internal space), `KEY=` (empty value), `KEY=x<TAB>y`. The unknown-key regex only matches a key of `[A-Za-z][A-Za-z0-9_]*` followed by `=` and a single non-space token, so any KV-looking line outside that is indistinguishable from a prose comment. Proposed: either a stricter definition of "KEY=VALUE-shaped line" (treat any `#` line containing `=` after a token as an unknown-key attempt) or add these to the named-limit list with a rationale.

**RD-C — capture header grammar stricter than receipt grammar (low).** Reproduction: `receipts/A10–A13.txt`.
The receipt header now tolerates two-space, no-space, trailing-space and lowercase known keys (NL-3/NL-4). The capture header does not: `#  TOOL_SHA256=…`, `#ENTRIES=3`, `# ENTRIES=3 `, `# entries=3` are free-form comments, so the key is missing. The counter fails closed (exit 1), but the first FINDING is `CAPTURE-RECEIPT-MISMATCH … capture=-`: the receipt-binding check fires before the header-missing check (which prints later as `FINDING missing header …`). The named id is therefore misattributed (the mismatch is actually an unreadable capture header). Proposed: either tolerate the same shapes in the capture header or name the missing-header cause first.

**RD-D — malformed expected TSV crashes the selftest (low).** Reproduction: `selftest-variants.txt` line ST10. `run_selftest` parses the expected TSV with no guard: `int(f[1])` / `f[2]` raise `IndexError`, so the process exits 1 with a traceback instead of a named could-not-evaluate (rc 2). Proposed: validate the TSV and emit `CANNOT-EVALUATE expected TSV malformed` with rc 2.

**RD-E — selftest wildcard finding (low).** Reproduction: ST05. `want_find in ('', '-')` skips the finding check, so a row with expected `-` is rc-only. Only FH-HONEST and FH2 use `-` in the committed TSV, so no current row is affected. Proposed: assert `-` only for rc-0 rows, or name the wildcard as a limit.

**Named limits observed (already on the prereg list, confirmed):** A14 (capture-header unknown key ignored), A15 (NL-2 prose comment), A49/A50 (pin-validation ordering after capture/tool reads). Not separately routed.

## 5. Corrections to my own work (recorded, not hidden)

- **Prediction errors:** A10–A13 were predicted as `missing header …`. The actual first FINDING is `CAPTURE-RECEIPT-MISMATCH … capture=-` because findings print before `problems_pre`. The actual behaviour is recorded as RD-C; my prediction was wrong, not the counter's exit.
- **Label error:** A08's receipt says "5-tab" but the string has four tabs (five fields). A true 5-tab row was not run separately; v4's rule (any tab in a `#` line) covers it by construction, but this is not an observed receipt.
- **Path deviation:** the task asked for the findings at `.ufo/waves/round-55/w1/S55reviewer02.md`, which is outside the seat bounds (`.ufo/waves/round-55/w1/<seat>/` only). I wrote the report here. The L1 can copy it to the w1 path if wanted.

## 6. Verification gaps

- The C1 counter was not attacked (another seat's scope); its matrix was regenerated only to confirm the committed rows.
- The attack set is a grammar probe, not exhaustive; the state list above is the complete set I ran.
- Real-lane legs ran at dispatch tip `3ce0ba…` and measured revision `4b10dd…` only; no other revisions.
- Predicted verdicts came from reading the source; actual outputs are the receipts.

## 7. Tools, installs, cleanup

- No tools installed or upgraded; no pacman, no PATH changes.
- No git/jj mutation anywhere; the lane worktree was only read (`git show` inside the counters, `git status` inspection by me).
- Scratch `/fast/scratch/hyaku/souji-r55/S55reviewer02/` deleted after copying receipts into this directory.

## 8. Receipts in this directory

- `attack-table.tsv` (54 rows), `receipts/A01.txt`…`A54.txt`
- `selftest-variants.txt` (ST02–ST13)
- `receipt-key-differential.txt` (15 unknown-key shapes, v3 vs v4)
- `real-lane-and-selftest.txt` (real-lane legs + committed selftest)
- `matrix-regen/` (regenerated c1/c2 v3/v4 matrices + `diff-vs-committed.txt`, all identical)
