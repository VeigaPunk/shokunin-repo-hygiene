# R94ExecC2 — C2 re-derivation (after arm, do-nothing control, forgery controls)

Seat: R94ExecC2 (executor). Lane: souji-shokunin at /home/vgpnk/Projects/shokunin/souji-shokunin.
Work dir: .ufo/waves/round-94/w1/R94ExecC2/. Scratch: /fast/scratch/hyaku/souji-r94/R94ExecC2/ (deleted before yield).
HEAD at run time: b065b7f036b32aa2114f3dedd9d0ec88b43dfcb2. All pins are on committed bytes.

## 1. After arm (r94 probe) — `c2-after.txt`, exit 0

Command:
`python3 -B census/round-94/c2-setup-arms.py --probe census/round-94/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <scratch work-after (existing empty)>`

Full receipt (c2-after.txt in seat dir; per-ARM .out under work-after-outs/):
```
# probe path=.../census/round-94/c2-forgery-probe.py sha256=e3ebe6e9318a9a557da3402822b8f508bc286dba60ee8497119ca3a08ceaea93
# fixture-pass path=.../tests/fixtures/r93-k4-flagfail.py sha256=ed15094e9ff17c159df9dd04d3b4d3878b2a1f23ecdc6175dc1759d1146e7a6a
# fixture-fail path=.../tests/fixtures/r92-k4-flagfail.py sha256=2c9bd76c77c609bfaf2fd1a86a5bd022fc8549cd58bc2f198a029e3ea90feeae
# tool path=.../tools/souji-record-agreement.py sha256=fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75
# before path=.../census/round-92/controls/c2-before-tool.py sha256=21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c
# counter path=.../census/round-94/c2-setup-arms.py sha256=3bb8c1b9c128c135b4a116498f6708bee0dd092bdf950bc96f268e77d20ea6e0
# fixture-mute sha256=2239d46e73842753b900cae6478ca064d4615bb411cc9ad8c998345e5789a69a
# fixture-crash sha256=c959e718cb2193e534b7d065a71dc68fbb8efedb12d276ec13a06e867ecd0810
ARM P1 exit=0 want=0 line=yes conform=yes
ARM P2 exit=1 want=1 line=yes conform=yes
ARM S1 exit=0 want=0 line=yes conform=yes
ARM S2 exit=2 want=2 line=yes conform=yes
ARM S3 exit=2 want=2 line=yes conform=yes
ARM S4 exit=2 want=2 line=yes conform=yes
ARM S5 exit=2 want=2 line=yes conform=yes
ARM S6 exit=2 want=2 line=yes conform=yes
ARM S7 exit=2 want=2 line=yes conform=yes
ARM S8 exit=2 want=2 line=yes conform=yes
ARMS-SUMMARY arms=10 conform=10
EXIT=0
```
Result: `ARMS-SUMMARY arms=10 conform=10`, EXIT 0 — predicate met.
FATAL lines seen in after outs (work-after-outs/*.out):
- S2.out: `C2-FORGERY-FATAL: --work .../S2 is not empty`
- S3.out: `C2-FORGERY-FATAL: --work .../S3 exists and is not a directory`
- S4.out: `C2-FORGERY-FATAL: --fixture .../absent-path is not a readable regular file`
- S5.out: `C2-FORGERY-FATAL: --tool .../absent-path is not a readable regular file`
- S6.out: `C2-FORGERY-FATAL: --before .../absent-path is not a readable regular file`
- S7.out: `C2-FORGERY-FATAL: the fixture printed no SUMMARY line for the positive control (exit 1)`
- S8.out: `C2-FORGERY-FATAL: the fixture printed no SUMMARY line for forgery F1 (exit 1); its verdict is unknown`

## 2. Do-nothing control (r93 probe) — `c2-control.txt`, exit 1

Command: same, with `--probe census/round-93/c2-forgery-probe.py`.

Full receipt (c2-control.txt; outs under work-control-outs/):
```
# probe path=.../census/round-93/c2-forgery-probe.py sha256=f3c84c49ac32cef40c96b875cb604ce83d63f2046b6031d65983130238705272
# fixture-pass sha256=ed15094e... / fixture-fail sha256=2c9bd76c... / tool sha256=fc0e35c2... / before sha256=21e5c740...
# counter path=.../census/round-94/c2-setup-arms.py sha256=3bb8c1b9c128c135...
# fixture-mute sha256=2239d46e... / fixture-crash sha256=c959e718...
ARM P1 exit=0 want=0 line=yes conform=yes
ARM P2 exit=1 want=1 line=yes conform=yes
ARM S1 exit=1 want=0 line=no conform=no
ARM S2 exit=2 want=2 line=yes conform=yes
ARM S3 exit=1 want=2 line=no conform=no
ARM S4 exit=1 want=2 line=no conform=no
ARM S5 exit=1 want=2 line=no conform=no
ARM S6 exit=1 want=2 line=no conform=no
ARM S7 exit=1 want=2 line=no conform=no
ARM S8 exit=1 want=2 line=no conform=no
ARMS-SUMMARY arms=10 conform=3
EXIT=1
```
Result: `ARMS-SUMMARY arms=10 conform=3`, EXIT 1 — control predicate met (identity with P2 receipt census/round-94/controls/c2-control-r93-probe.txt except WALL timing line). S1's .out shows the FileExistsError traceback (r93 probe dies in os.makedirs on the existing empty dir); only S2 found C2-FORGERY-FATAL (pre-existing in r93 for a non-empty --work).

## 3. Forgery controls (GA/GB) — `c2-forgeries.txt`, exit 0

Command: `python3 -B census/round-94/c2-forgery-controls.py --probe census/round-94/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>`

Full receipt (c2-forgeries.txt):
```
# probe path=.../census/round-94/c2-forgery-probe.py sha256=e3ebe6e9318a9a557da3402822b8f508bc286dba60ee8497119ca3a08ceaea93
FORGERY GA sha256=c718bf7e47d3f26df1da6aae744571545a55171df19cffaec1b29d1ed5e7d166 arms_exit=1 summary=arms=10,conform=9 refused=yes
  GA ARM P2 exit=2 want=1 line=yes conform=no
FORGERY GB sha256=153286eb89dd736effd7a5f2a16f50be22e8be3983ab12281fa3a76c1ad04376 arms_exit=1 summary=arms=10,conform=9 refused=yes
  GB ARM S1 exit=2 want=0 line=no conform=no
C2-FORGERY-CTL-SUMMARY forgeries=2 refused=2
EXIT=0
```
Result: `C2-FORGERY-CTL-SUMMARY forgeries=2 refused=2`, EXIT 0 — forgery predicate met; byte-identical to P2 receipt census/round-94/controls/c2-forgery-controls.txt (GA/GB sha256 and per-arm lines match).

## 4. Pins vs preregistration (prereg line 71, and instrument headers)

| file | sha256 (measured) | expected | match |
|---|---|---|---|
| census/round-94/c2-forgery-probe.py | e3ebe6e9318a9a55… | e3ebe6e9318a9a55… (P1 pin, prereg:71) | YES |
| census/round-94/c2-setup-arms.py | 3bb8c1b9c128c135… | 3bb8c1b9c128c135… | YES |
| census/round-94/c2-forgery-controls.py | 5f2e8916adecee4b… | 5f2e8916… | YES |
| tests/fixtures/r93-k4-flagfail.py | ed15094e9ff17c15… | ed15094e… | YES |
| tests/fixtures/r92-k4-flagfail.py | 2c9bd76c77c609bf… | 2c9bd76c… | YES |
| tools/souji-record-agreement.py | fc0e35c208331de8… | fc0e35c2… | YES |
| census/round-92/controls/c2-before-tool.py | 21e5c7408fef10f2… | 21e5c740… | YES |
| census/round-93/c2-forgery-probe.py | f3c84c49ac32cef4… | matches r93 record sha256 | YES |

Full hashes also in seat-dir pins.txt. Synthetic S7/S8 fixture-mute/fixture-crash sha256 (2239d46e…, c959e718…) match P2 receipts.

## 5. Hunk inventory: diff r93 probe → r94 probe (probe-r93-r94.diff)

Six hunks (diff exit 1), no others:
1. Docstring header rewrite (lines 2–3 → 2–3, plus 4a5–13): new r94 title documenting exit-2 discipline; r93 description retained ("r93 docstring follows…"). Doc only.
2. Line 86 `os.path.exists(work) and os.listdir(work)` → `os.path.lexists(work) and not os.path.isdir(work)` + FATAL + `return 2`: —work that exists and is not a directory now exits 2 (S3 arm).
3. Line 89 `os.makedirs(work)` deleted; after line 90 region, a loop checking fixture/tool/before are readable regular files → FATAL + `return 2` (S4/S5/S6 arms); `os.makedirs(work, exist_ok=True)` replaces `os.makedirs(work)`: an EXISTING EMPTY --work is now used (S1 arm; fixes r93 FileExistsError→exit-1).
4. `if res is None:` after positive control → writes absent-SUMMARY FATAL + `return 2` (S7 arm).
5. `if res is None:` inside forgery loop → writes the forgery's .out file then FATAL + `return 2` (S8 arm).
6. Non-empty --work check (`os.path.isdir(work) and os.listdir(work)`) → FATAL + `return 2` (S2 arm; replaces an earlier r93 fatal path).

FORGERIES tuple: extracted lines 41–80 of r93 and 50–89 of r94, diffed — byte-identical (FORGERIES_IDENTICAL). All eight tuples (F1,F2,F3,F4,N0,F5,F6,F7) present unchanged.
Verdict lines byte-identical modulo line numbers: `print(f"FORGERY {fid} sha256=...")` (r93:115, r94:141) and `print(f"FORGERY-SUMMARY forgeries={len(FORGERIES)} rejected={rejected} positive=...")` (r93:117, r94:143); final `return 0 if positive and rejected == len(FORGERIES) else 1` identical in both. Exit 1 is reserved for verdict failure; exit 2 only for setup FATALs.

## 6. Direct r94 probe run (not via arms counter) — `c2-direct.txt`, exit 0

`python3 -B census/round-94/c2-forgery-probe.py --fixture tests/fixtures/r93-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <existing empty scratch dir>`:

```
# probe path=.../census/round-94/c2-forgery-probe.py sha256=e3ebe6e9318a9a557da3402822b8f508bc286dba60ee8497119ca3a08ceaea93
POSITIVE tool exit=0 tool_pass=22/22 pass
FORGERY F1 sha256=fe4ba3d65d25afb270cf93a56a5f3115837bcf17d4cbd70e8dc70602a4c72301 exit=1 tool_pass=18/22 rejected=yes failed=KFF16,KFF18,KFF19,KFF20
FORGERY F2 sha256=2fb79e5f5987899fcefc3797a0a75dec8270bb7dcc8886060f0e57437324dc0d exit=1 tool_pass=19/22 rejected=yes failed=KFF16,KFF19,KFF20
FORGERY F3 sha256=69bf77c3c48baaf626377029b206a8d21e36cf7969676a62ad9480f543d83873 exit=1 tool_pass=19/22 rejected=yes failed=KFF11,KFF18,KFF19
FORGERY F4 sha256=43043c835953ba22361bba0e57d97e8a48350c1556af593ce4aaeabf23bdab5f exit=1 tool_pass=19/22 rejected=yes failed=KFF17,KFF18,KFF19
FORGERY N0 sha256=21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c exit=1 tool_pass=16/22 rejected=yes failed=KFF14,KFF15,KFF16,KFF18,KFF19,KFF20
FORGERY F5 sha256=ed62852641bb1c3998d9b6bc74e52624dae4949cc3522c6fb1b4dd47b8f52727 exit=1 tool_pass=21/22 rejected=yes failed=KFF19
FORGERY F6 sha256=99e30616c3dff96fc8383bd5b235defb20db5a9406b89cbf80095e16da32e60a exit=1 tool_pass=21/22 rejected=yes failed=KFF19
FORGERY F7 sha256=027393918b46ac9d356aa3bd09567fa6abcc92e158e37766f7690b4baa42c3f3 exit=1 tool_pass=21/22 rejected=yes failed=KFF19
FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass
EXIT=0
```
Comparison vs census/round-93/records/c2-forgery-after.txt: every FORGERY line (incl. per-forgery sha256, exit, tool_pass, failed set) and POSITIVE line is identical (mechanically diffed: FORGERY_LINES_IDENTICAL). Differences are only: the probe path/sha256 header (r94 vs r93), the leading tool/fixture/before headers (absent in r93 record), and EXIT=0 label vs EXIT=0/EEXIT=0 — i.e. sha256-aside, identical verdict content. Matches prereg P1 expectation `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass` EXIT 0.

## 7. Verdict

NO-FALSIFICATION. All three predicates re-derive on committed bytes at HEAD b065b7f:
after (10/10, EXIT 0), control (3/10, EXIT 1), forgeries (GA/GB refused, EXIT 0). Pins match prereg/P2. The r93→r94 probe delta is purely exit-code discipline: FORGERIES tuples and every verdict/output line are byte-identical; six setup hunks convert setup failures from exit 1 to exit 2 + C2-FORGERY-FATAL. Direct run reproduces the r93 forgery lines exactly (sha256-aside).

Risks / blockers: none. Checks for the main agent: none beyond routine integration; all evidence is text receipts in the seat dir. No tool installs (nothing needed). Scratch work trees deleted before yield; only text receipts remain in the seat dir.

Report: .ufo/waves/round-94/w1/R94ExecC2.md
