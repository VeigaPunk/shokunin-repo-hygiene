STATUS: PASS

Slice: SCORECARD.md capability data rows 21–25 (the end of the capability table).
Item: declared-evidence calibration audit, round 22 attempt 2, seat AuditCap5.
Measured revision: **4edb25dfe262515d0da63224bbba71e02e36cba5** (preregistration base).
Report: read-only. No repo write, no git write, no deletion authority, no tool install.

## 1. Slice identity and the one scope correction

At the measured revision the capability table runs `SCORECARD.md:45-68` = **24 data rows**;
the 25th row (`declared-evidence calibration audit (r22 attempt 2)`) is added by the four
commits after the freeze and exists only at HEAD `70af563c3086d5799a7fdaf988ba3b687f3b128c`
(`git rev-list --count 4edb25d..HEAD` → `4`, working tree clean for SCORECARD.md).

Rows 21–24 are **byte-identical** at both revisions, verified:

    diff <(git show 4edb25d:SCORECARD.md | sed -n '65,68p') <(sed -n '70,73p' SCORECARD.md)
    → no output (IDENTICAL)

So the slice is measured as: rows 21–24 at `4edb25d` (file lines 65–68 there, 70–73 now) and
row 25 at `70af563` (line 74). Measuring row 25 against `4edb25d` would report
`mismatch:path-absent` for a tool and receipt created *after* the freeze — a fabricated
finding — so it is not done. TSV line numbers are the current-file lines (70–74).

## 2. Commands, per frozen class

    # class A — backticked repo-relative path ending .py/.sh/.json/.tsv/.md/.txt
    git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r <REV> --name-only | grep -Fx -- <path>
    # cross-check (blob must exist):
    git -C … cat-file -e <REV>:<path>

    # class B — bare 7..40 hex in a revision-context cell
    git -C … cat-file -e <tok>^{commit}

    # class C — 64-hex in the same cell as exactly one backticked path
    git -C … show <REV>:<path> | sha256sum

Token enumeration over the five rows (executed):

    awk 'NR>=70&&NR<=74' SCORECARD.md | grep -oE '`[^`]+`'            → 5 spans
    awk 'NR>=70&&NR<=74' SCORECARD.md | grep -oE '[0-9a-f]{7,40}'     → (empty)
    awk 'NR>=70&&NR<=74' SCORECARD.md | grep -oE '[0-9a-f]{64}'       → (empty)
    awk 'NR>=70&&NR<=74' SCORECARD.md | grep -oE '[0-9A-Fa-f]{7,40}'  → (empty)
    awk 'NR>=70&&NR<=74' SCORECARD.md | grep -c '\*'                  → 0 (no glob token)

**There is no class-B or class-C assertion anywhere in this slice**, so `cat-file -e <tok>^{commit}`
and the sha256 comparison had no input. The command forms were exercised instead on the
slice's own pointers: `git show 4edb25d:census/round-21/accepted-matrix.json | sha256sum` →
`48ea837ab8e00ca4ea527e8d8d67756b16dae2360525d5211ef8bb993486151e`.

## 3. Results — 5 class-A assertions, 0 mismatches

Evidence: `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap5.tsv` (22 rows, all 5 columns:
5 A, 17 skipped, 0 B, 0 C, 0 mismatch; skipped rows carry `-` in the class column because the
frozen enum excludes them).

| row | line | token | class | observed | command output |
|---|---|---|---|---|---|
| 21 durable revision stamps | 70 | `tools/souji-rev-pin.py` | A | resolved | `ls-tree` FOUND @4edb25d; `cat-file -e` blob `ee952a2ca992` |
| 21 | 70 | `tests/fixtures/r19-rev-pin.py` | A | resolved | FOUND @4edb25d; blob `07a85ff0017c` |
| 24 clone-isolated replay | 73 | `census/round-21/accepted-matrix.json` | A | resolved | FOUND @4edb25d; blob `be8e96cdc80d` |
| 25 declared-evidence audit | 74 | `tools/souji-declared-evidence.py` | A | resolved | FOUND @70af563 (blob `f388642ca182`); absent @4edb25d — expected, post-freeze |
| 25 | 74 | `census/round-22/attempt2/declared-evidence-before.tsv` | A | resolved | FOUND @70af563 (blob `26db2196c1b8`, 5471 B); absent @4edb25d — expected |

`mismatch:path-absent` = 0, `mismatch:rev-unresolved` = 0, `mismatch:digest` = 0.
Because no `mismatch:*` exists, **no truth-preserving repair is required by this slice**.

Skipped, with reasons (all 17 rows are in the TSV, none dropped): counts `11/0`, `13/0`,
`18-step`, `selftest118/0`, `base12`, `base11`, `3/3`, `18/18`, `8/8` (counts, not a frozen
class); `r19-seat-audit-shapes17/0`, `r20-audit-contract78/0` (unbackticked receipt names with
counts); `agreement-pin-check` (unbackticked, no extension); `remote-source-after.json`,
`final-code-verification.json` (unbackticked — see F2); `/var/tmp scratch` (not repo-relative);
`S102`, `S109–S114` (source ids, a C2/SOURCES concern, not a C1 class). Round labels
(`r19`/`r20`/`r21`/`r22`) and prose words are not candidate tokens for any class and were
never enumerated.

## 4. Cross-check against the lane's own counter (executed)

    python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev 4edb25dfe… --format tsv
    → assertions=56 resolved=53 skipped=33 mismatches=3      (reproduces the archived before-receipt)
    python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev HEAD --format tsv
    → assertions=56 resolved=56 skipped=36 mismatches=0      (matches the row-14 claim)

Instrument rows inside this slice at HEAD: lines 69×2, 70 (`tests/fixtures/r19-rev-pin.py`),
73 (`census/round-21/accepted-matrix.json`), 74 (`declared-evidence-before.tsv`) — i.e. **3 of
the slice's 5 class-A assertions** are inside the counter's totals; the remaining 2 are exactly
the F1 blind spot (spans carrying argv), which the counter books as `skipped` while I verified
them by direct `cat-file`/`ls-tree`. The two revs otherwise agree with my independent
enumeration on which rows contribute class-A assertions.

## 5. Findings (none is a false claim; all are enumeration gaps)

**F1 — class-A blind spot for a span that carries arguments (calibration, coverage).**
`SPAN_RE` captures the whole backticked span and `PATH_RE` requires the span to end in the
extension, so `tools/souji-rev-pin.py --selftest` (line 70) and
`python3 tools/souji-declared-evidence.py --selftest` (line 74) cannot classify as A and fall
into `skipped`. Confirmed executed: the instrument's TSV lists line 70 only
`tests/fixtures/r19-rev-pin.py` and line 74 only the before-TSV, never the two scripts.
Both scripts resolve, so nothing false is asserted — but a *dangling* path in this shape would
be invisible to `mismatches`. Minimal truth-preserving repair (strengthening, keeps the claim):
split argv out of the path span — `tools/souji-rev-pin.py` `--selftest` 11/0 and
`tools/souji-declared-evidence.py` `--selftest` 8/8. Effect: N 56→58, M still 0, both paths
already verified present. (Instrument-side alternative: extract the leading whitespace-delimited
token of a span when the remainder looks like argv — larger change, touches the frozen tool.)

**F2 — unbackticked evidence filenames never enumerated (coverage).**
Line 73 names `remote-source-after.json18/18` and `final-code-verification.json` unbackticked;
class A is defined only over backticked paths, so the counter cannot check them. Both are real
and resolve at `4edb25d` as `census/round-21/remote-source-after.json` (blob `f4123cf12614`) and
`census/round-21/final-code-verification.json` (blob `6483d98f7ea9`). Minimal repair: backtick
them at their repo-relative paths. Effect: N +2, M still 0, evidence role unchanged and now
machine-checkable.

**F3 — two of five rows carry no machine-checkable token at all (coverage).**
Line 71 (row 22) and line 72 (row 23) state their receipts only as prose (`118/0`, `17/0
(base12)`, `78/0 (base11)`, `agreement-pin-check`). They contribute 0 to N, so C1's `M=0` is
silent about them. Committed receipts do exist at `4edb25d`, so the repair is additive:
`census/round-21/step-inventory.json` holds the 18-step inventory with `auditor-selftest`
expecting `SELFTEST pass=118 fail=0`, the `r19-seat-audit-shapes` and `r20-audit-contract`
steps, and the `agreement-pin-check` step invoking `census/round-19/verify-agreement-pin.py`;
its `normalization` field records "r21 agreement root aliases ROOT because original bytes are
staged privately", which is exactly row 23's "stages original revision bytes". Also present:
`tests/fixtures/r19-seat-audit-shapes.py`, `tests/fixtures/r20-audit-contract.py`,
`census/round-19/verify-agreement-pin.py`; and `.ufo/waves/round-21/preregistration.txt:12`
states the harm guard "auditor --selftest stays SELFTEST pass=118 fail=0; … 17/0 base 12; …
78/78/0 base 11". Minimal repair: append one backticked pointer per row
(`census/round-21/step-inventory.json` for row 22; `census/round-21/step-inventory.json` +
`census/round-19/verify-agreement-pin.py` for row 23). Honest limit to keep stated: the counts
stay counts, so C1 still cannot falsify `118/0`, `17/0`, `78/0` — the instrument proves
*locators*, not numbers.

**F4 — slice label vs measured revision (operability).**
"Rows 21–25" is only satisfiable against the current file; at `4edb25d` the table ends at row
24. Row 25 is post-freeze text and its two class-A tokens resolve only at `70af563`. No repair
of the SCORECARD is needed; this note prevents a downstream re-run at the base rev from
producing a fabricated `mismatch:path-absent` for a tool that did not exist yet.

## 6. Residual risk / verification gaps

- Count claims (`11/0`, `13/0`, `8/8`, `118/0`, `17/0`, `78/0`) are outside the frozen enum. I
  did **not** run `--selftest` and do **not** report them as passed; `skipped` is the verdict.
- C1's "after" receipt is not in this slice: `census/round-22/attempt2/declared-evidence-after.tsv`
  does not exist at HEAD (only `-before.tsv`), so the final-tip `M=0` receipt is still the
  implementer's artifact, not mine.
- My reading of the instrument's skip arithmetic is source-verified (`PATH_RE`/`SPAN_RE`) and
  executed-verified (its TSV omits the two spans); the exact per-token attribution of
  `skipped=33→36` is not decomposed, only the slice's contribution.
- Tooling: no package installed, updated, or upgraded for this seat.
