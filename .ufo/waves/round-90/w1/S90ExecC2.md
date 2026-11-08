# S90ExecC2 — souji r90 C2 independent re-derivation (operability 8)

Seat: S90ExecC2 (executor, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (id souji).
HEAD measured: `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (F, the preregistration alone).
Host tools: Python 3.14.8, git 2.56.0. No installs/upgrades were needed (PACMAN untouched).
All runs were `python3 -B` on committed bytes; no git mutation, no file outside my seat dir/scratch was written.

## Instrument bytes measured (working tree clean vs HEAD: `git diff --stat` on these four printed nothing, rc=0)

| path | sha256 (working tree == HEAD blob) |
|---|---|
| `tools/souji-record-agreement.py` | `d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561` |
| `tests/fixtures/r90-k4-flagfail.py` | `d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa` |
| `census/round-90/controls/c2-before-tool.py` | `f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd` |
| `census/round-87/c2-k4-counter.py` | `4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e` |

`git cat-file -p HEAD:<path> | sha256sum` reproduces the same three tool/fixture/control hashes, so the
receipts below are measured on the COMMITTED bytes at F, not on a dirty working copy.
HEAD blobs: tool `f485265af6933b094b35647dccd94a77d6787b19`, fixture `b7ddb4105420ae739b716f226eba9fff22d32b4f`,
control `bcde780fc9b0c7130c530a639954c65ac14d6cee`, counter `42efc1b43db0e22086c03878d4e37b8191f5270f`.

Identity check of the do-nothing control (independent of the prereg's claim):
`git cat-file -p bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2:tools/souji-record-agreement.py | sha256sum` =
`f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd`, and
`diff <(git cat-file -p bd76043…:tools/souji-record-agreement.py) census/round-90/controls/c2-before-tool.py`
printed nothing (rc=0). The before arm IS the r89 lane-base filed bytes. Between bd76043 and F only
`4cb3a06f` ("round-90: C2 repair — U+0085 takes the \u0085 spelling and the dead escape-first _one_line is
deleted") touches the tool.

## Arm A — after fixture (target)

Command (from the lane root):
```
python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-90/controls/c2-before-tool.py --work /fast/scratch/hyaku/souji-r90/S90ExecC2/work-after
```
Receipt: `receipt-after.txt` (seat dir), EXIT 0. Full output:
```
# tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py sha256=d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561
# before path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-90/controls/c2-before-tool.py sha256=f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd
# fixture sha256=d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa
CASE KFF1 tool=pass before=pass
CASE KFF2 tool=pass before=pass
CASE KFF3 tool=pass before=pass
CASE KFF4 tool=pass before=pass
CASE KFF5 tool=pass before=pass
CASE KFC1 tool=pass before=pass
CASE KFC2 tool=pass before=pass
CASE KFF6 tool=pass before=pass
CASE KFF7 tool=pass before=pass
CASE KFF8 tool=pass before=pass
CASE KFF9 tool=pass before=fail
CASE KFF10 tool=pass before=fail
SUMMARY cases=12 tool_pass=12 before_pass=10
```
Verdict Arm A: **PASS** — matches the frozen predicate verbatim (`SUMMARY cases=12 tool_pass=12
before_pass=10`, EXIT 0). The only verdict delta vs the control is KFF9/KFF10, exactly the pair the claim adds;
the ten r89 cases are pass on both arms.

## Arm B — do-nothing control (r89 bytes as BOTH arms)

Command:
```
python3 -B tests/fixtures/r90-k4-flagfail.py --tool census/round-90/controls/c2-before-tool.py \
  --before census/round-90/controls/c2-before-tool.py --work /fast/scratch/hyaku/souji-r90/S90ExecC2/work-control
```
Receipt: `receipt-control.txt`, EXIT 1. Output:
```
# tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-90/controls/c2-before-tool.py sha256=f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd
# before path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-90/controls/c2-before-tool.py sha256=f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd
# fixture sha256=d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa
CASE KFF1 tool=pass before=pass
CASE KFF2 tool=pass before=pass
CASE KFF3 tool=pass before=pass
CASE KFF4 tool=pass before=pass
CASE KFF5 tool=pass before=pass
CASE KFC1 tool=pass before=pass
CASE KFC2 tool=pass before=pass
CASE KFF6 tool=pass before=pass
CASE KFF7 tool=pass before=pass
CASE KFF8 tool=pass before=pass
CASE KFF9 tool=fail before=fail
CASE KFF10 tool=fail before=fail
SUMMARY cases=12 tool_pass=10 before_pass=10
R90-FIXTURE-FAIL: the tool under test does not pass every case
```
Verdict Arm B: **control behaves as frozen** — cannot reach `tool_pass=12`; the two new cases fail on both
arms and the run exits 1. No no-work path reaches the target.

## Regression — r87 12-row K4 counter on the filed tool

Command:
```
python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py \
  --work /fast/scratch/hyaku/souji-r90/S90ExecC2/work-k4
```
Receipt: `receipt-k4.txt`, EXIT 0. Summary + all rows (verbatim in receipt):
```
ROW KH1 expect=clean k4=0 named=- rc=1 match=yes
ROW KH2 expect=clean k4=0 named=- rc=1 match=yes
ROW KU1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['a.txt|uncommitted-path']
ROW KU2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['untracked-scratch.txt|uncommitted-path']
ROW KF1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KF2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KF3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KG1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|index-flag-concealed']
ROW KG2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KN1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KN2 expect=header k4=0 named=yes rc=1 match=yes writer_sha=70bbf1c2a92e appended_sha=1b8ecf328ed3
ROW KN3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['bad\\nname2.txt|uncommitted-path']
SUMMARY rows=12 mismatches=0 errors=0
```
Verdict: **PASS** — `rows=12 mismatches=0 errors=0`, EXIT 0. The counter printed its own hashes:
counter `4e2b7c06…`, writer `70bbf1c2a92e9ea6…`, clone rev `e295278b97d7513900e2f9a0e48bffad602a7479`.

## Hand-driven pair (independent of the fixture)

Driver: seat-dir `pair_driver.py` (copied from scratch), which loads the given tool with
`importlib.util.spec_from_file_location` and prints `_escape_text(_decode_record(raw))` for
`b"fatal: nel \x85 marker\n"` (raw byte 0x85) and `b"fatal: nel \xc2\x85 marker\n"` (U+0085 UTF-8), plus the
public-path cell `_one_line_bytes(raw)` for both.

Filed tool (`pair-filed.txt`, EXIT 0):
```
raw0x85_cell='fatal: nel \\x85 marker\\n'
u0085char_cell='fatal: nel \\u0085 marker\\n'
cells_distinct=True
raw0x85_cell_bytes=b'fatal: nel \\x85 marker\\n'
u0085char_cell_bytes=b'fatal: nel \\u0085 marker\\n'
one_line_bytes_raw0x85='fatal: nel \\x85 marker\\n'
one_line_bytes_u0085char='fatal: nel \\u0085 marker\\n'
direct_escape_text_char='fatal: nel \\u0085 marker'
direct_escape_text_surrogate='fatal: nel \\x85 marker'
```
The raw byte 0x85 cell is `fatal: nel \x85 marker\n` (one physical line, `\n` escaped); the U+0085 character
cell is `fatal: nel \u0085 marker\n`. They differ, and each is one physical line.

r89 tool (`pair-before.txt`, EXIT 0):
```
raw0x85_cell='fatal: nel \\x85 marker\\n'
u0085char_cell='fatal: nel \\x85 marker\\n'
cells_distinct=False
one_line_bytes_raw0x85='fatal: nel \\x85 marker\\n'
one_line_bytes_u0085char='fatal: nel \\x85 marker\\n'
direct_escape_text_char='fatal: nel \\x85 marker'
direct_escape_text_surrogate='fatal: nel \\x85 marker'
```
The collision is reproduced independently: the r89 tool renders both members as the same cell `\x85`.

Extra hand checks on the filed tool (scratch probe):
```
literal_text_x85   = 'lit \\\\x85 tail'      # literal backslash-x85 text doubles the backslash
literal_text_u0085 = 'lit \\\\u0085 tail'
escape_record c285 = '\\xc2\\x85'            # _escape_record is byte-based; U+0085 path bytes were never ambiguous
escape_record 85   = '\\x85'
quartet_distinct   = True                    # {byte, char, literal \x85, literal \u0085} = 4 distinct cells
```
This confirms stated limit (i): the repair is in `_escape_text` only; `_escape_record` prints `\xc2\x85` for
the character's bytes and `\x85` for a lone 0x85 — different spellings, both byte-based.

## Dead-code deletion

Counts (`grep -c`/`grep -n`):
```
filed tool:  def _one_line=0   _one_line( total=0   non-def refs=0
before tool: def _one_line=1   _one_line( total=1   non-def refs=0
r89 base blob (bd76043:tools/souji-record-agreement.py): one match only —
  297:def _one_line(text: str, limit: int = 200) -> str:
```
So the r89 helper had zero callers (the sole match is its definition; r89's live path used `_one_line_bytes`),
and the r90 filed tool has no definition and no reference. `grep -n 'one_line'` on the filed tool shows only
`_one_line_bytes` (`def` line 216, docstring line 218, K4 call site line 406).

Parse/import: `ast.parse` succeeded on both modules (rc 0), and the filed tool loaded cleanly under
`importlib` in the hand-driven run (all attributes used were present; `--help` also exits 0). The 12 fixture
cases each execute the tool through its public CLI (`python -B <toolcopy> --root <repo> --rev <rev>`:
`run_case` line 129), so the public path is exercised 12 times per arm plus 4 pair re-runs per arm (16
invocations/arm, 32 total). No dynamic dispatch to `_one_line` exists in the filed tool: the only
`exec(compile(...))` in it is inside the embedded writer bootstrap string (line 343), which loads
`souji-receipt-write.py`, not the tool module; `getattr`/`globals()` do not appear. This matches stated limit
(iv): runtime dispatch is not exhaustively excluded, and none is claimed.

## Fixture wording check (r89 ten cases "unchanged")

AST comparison of `tests/fixtures/r89-k4-flagfail.py` vs `tests/fixtures/r90-k4-flagfail.py`:
- All ten `case_*` check functions (`case_short`, `case_trace`, `case_long`, `case_controls`, `case_empty`,
  `case_clean`, `case_refused`, `case_badbyte`, `case_literal`, `case_headctl`) are BYTE-IDENTICAL.
- `run_case` differs only in the env-var rename `R89_STDERR_MODE/R89_REFUSED` → `R90_STDERR_MODE/R90_REFUSED`
  (each fixture's fake writer reads its own prefix); `make_kit` differs only in the seed commit message
  ("r89 fixture seed" → "r90 fixture seed"). No semantic change to the ten checks.
- `main` gains the KFF9/KFF10 cases and applies the KFF6/KFF7 pair check to BOTH arms (r89 applied it to the
  after arm only). Disclosed as the frozen kill rule's "pair check runs on BOTH arms (z90's change)".
  On my measurements this changes no verdict: KFF6/KFF7 are pass on both arms (filed tool and before tool both
  render `\xff` and `\\xff` distinctly), so the ten verdicts stay pass/pass.
- `CASES` entries 1-10 are identical; entries 11-12 are the new KFF9/KFF10.

Independent cross-run of the r89 fixture on the filed tool (`receipt-r89fixture.txt`):
`CASE KFF1..KFF8, KFC1, KFC2 tool=pass before=pass`, `SUMMARY cases=10 tool_pass=10 before_pass=10`, EXIT 1
from its own "the do-nothing control passes as many cases (no measured delta)" guard — a no-delta guard, not a
case failure. So the ten r89 checks did not regress on the filed tool.

## Verdict

Both C2 arms re-derive on committed bytes at F: **after 12/12 EXIT 0; control 10/12 EXIT 1; r87 K4 regression
12/0/0 EXIT 0**. Hand-driven cells are injective on the filed tool and collide on the r89 bytes exactly as the
claim states. `_one_line` is gone from the filed tool (0 definitions, 0 references) and had zero callers in the
r89 base. No case changed verdict since r89 except KFF9/KFF10 (fail → pass on the filed tool; unchanged fail on
the control). Nothing in my measurements falsifies the C2 stated wording.

## What I could NOT check (stated limits / out of seat)

- S353 (UAX #14 capture) was not re-fetched or re-quoted; not this seat's assignment and I did not want to
  substitute a different source review. The capture hash `296df533…` is taken from the prereg, unverified here.
- Universal injectivity is not claimed and not tested; I tested the enumerated KFF9/KFF10 pair plus the two
  literal-spelling variants. A stderr pair differing only inside the elided middle could still collide (the
  prereg's stated limit ii).
- Runtime dispatch of `_one_line` is excluded only by static grep + import (stated limit iv); no exhaustive
  dynamic analysis was run.
- C1/LD2b was not re-derived by this seat.
- I did not re-run the fixture more than once per arm (no repeatability battery); each arm ran once, fresh
  empty `--work`.
- The pre-freeze receipts (`prefreeze-c2-*`) were not compared to my runs beyond the summary strings.

## Scratch / side effects

- Scratch used: `/fast/scratch/hyaku/souji-r90/S90ExecC2` (fixture `--work` dirs, driver, receipts). Deleted
  before yielding (`rm -rf`); nothing left behind. Receipts copied into this seat dir first.
- Writes: this report + `.ufo/waves/round-90/w1/S90ExecC2/` (7 files: 6 receipt/driver artifacts). No git/jj
  mutation; no PACMAN; no host service/sysctl change; no credentials or secrets read.
