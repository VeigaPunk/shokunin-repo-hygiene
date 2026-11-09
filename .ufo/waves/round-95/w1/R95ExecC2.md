# R95ExecC2 — C2 re-derivation (round 95, souji lane)

Seat: R95ExecC2. Lane: souji-shokunin. Scope: C2 after arm, do-nothing control, forgery controls, pin table, r94→r95 probe diff hunk inventory, direct probe runs. Read-only on lane; receipts in `.ufo/waves/round-95/w1/R95ExecC2/`; scratch under `/fast/scratch/hyaku/souji-r95/R95ExecC2/` (deleted before yield).

## Verdict: all C2 numbers reproduce — no mismatch

Every predicate number reproduced exactly on committed bytes. No falsification found.

## 1. AFTER arm (r95 probe)

Command (empty --work, sequential):
`python3 -B census/round-95/c2-setup-arms.py --probe census/round-95/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>`
Exit: 0. Wall: 120.52 s.

Receipt (`arms-after.stdout`, `arms-after.exit=EXIT=0`):
```
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
ARM S9 exit=2 want=2 line=yes conform=yes
ARM S10 exit=2 want=2 line=yes conform=yes
ARM S11 exit=2 want=2 line=yes conform=yes
ARM S12 exit=2 want=2 line=yes conform=yes
ARM S13 exit=2 want=2 line=yes conform=yes
ARM S14 exit=2 want=2 line=yes conform=yes
ARMS-SUMMARY arms=16 conform=16
```
S9/S10/S11/S12 now exit 2 (was 1/1/1/hung in r94). S12 ends via the probe's own 120 s timeout, not the counter's 300 s kill.

## 2. CONTROL (r94 probe, do-nothing)

Command: same with `--probe census/round-94/c2-forgery-probe.py`.
Exit: 1. Wall: 300.54 s.

Receipt (`arms-control.stdout`, `arms-control.exit=EXIT=1`):
```
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
ARM S9 exit=1 want=2 line=no conform=no
ARM S10 exit=1 want=2 line=no conform=no
ARM S11 exit=1 want=2 line=no conform=no
ARM S12 exit=hung want=2 line=no conform=no
ARM S13 exit=2 want=2 line=yes conform=yes
ARM S14 exit=2 want=2 line=yes conform=yes
ARMS-SUMMARY arms=16 conform=12
```
Matches P2 control receipt (`census/round-95/controls/c2-control-r94-probe.txt`) line-for-line.

## 3. FORGERY controls (r95 probe, GA/GB/GC)

Command: `python3 -B census/round-95/c2-forgery-controls.py ...` Exit: 0. Wall: 587.56 s.

Receipt (`forgery-controls.stdout`, `forgery-controls.exit=EXIT=0`):
```
FORGERY GA sha256=025f673e59416eb743a85f3a26ad4ec2bbc30f1e0c7055dbfac19dd89a444c01 arms_exit=1 summary=arms=16,conform=15 refused=yes
  GA ARM P2 exit=2 want=1 line=yes conform=no
FORGERY GB sha256=270eb32b431c68029a26eadf135570573dbcf82a739a7a359d092f6d34472656 arms_exit=1 summary=arms=16,conform=14 refused=yes
  GB ARM S9 exit=1 want=2 line=no conform=no
  GB ARM S10 exit=0 want=2 line=no conform=no
FORGERY GC sha256=9d959ec458fb628fb254c2195dcf6683dcbe6700440235272e29e3d5d0032528 arms_exit=1 summary=arms=16,conform=15 refused=yes
  GC ARM S12 exit=hung want=2 line=no conform=no
C2-FORGERY-CTL-SUMMARY forgeries=3 refused=3
```
Matches P2 (`census/round-95/controls/c2-forgery-controls.txt`) exactly, including forgery sha256s.

## 4. Pin table (sha256, all vs prereg §C2 INSTRUMENTS + P2 receipts)

| file | sha256 | match |
|---|---|---|
| census/round-95/c2-forgery-probe.py | bd83e120a71fe01073f63f5bdbafedd468bd772b9fc46fc12b893abc479fdc73 | prereg bd83e120… ✓ |
| census/round-95/c2-setup-arms.py | dd2da59b7c9f5ecbc043ff826a13fe848c5f99ef31b775aa4fee274353b2569d | prereg dd2da59b… ✓ |
| census/round-95/c2-forgery-controls.py | 337fae896bcacfe66fb670c0f63296273c1ae02eedf46300d326acb6e0d7a7a8 | prereg 337fae89… ✓ |
| census/round-94/c2-forgery-probe.py | e3ebe6e9318a9a557da3402822b8f508bc286dba60ee8497119ca3a08ceaea93 | P2 ✓ |
| tests/fixtures/r93-k4-flagfail.py | ed15094e9ff17c159df9dd04d3b4d3878b2a1f23ecdc6175dc1759d1146e7a6a | P2 ✓ |
| tests/fixtures/r92-k4-flagfail.py | 2c9bd76c77c609bfaf2fd1a86a5bd022fc8549cd58bc2f198a029e3ea90feeae | P2 ✓ |
| tools/souji-record-agreement.py | fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75 | P2 ✓ |
| census/round-92/controls/c2-before-tool.py | 21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c | P2 ✓ |

Synthetic inputs written by the counter (printed in receipts, identical across after/control runs): fixture-mute 2239d46e…, fixture-crash c959e718…, fixture-hang 2202a032…, tool-nonutf8 4625634c…, before-nonutf8 d7c3a243…, tool-edit-twice 32405926… — all match P2.

## 5. Diff census/round-94/c2-forgery-probe.py → census/round-95/c2-forgery-probe.py — hunk inventory

Full diff: `.ufo/waves/round-95/w1/R95ExecC2/diff-r94-r95.txt` (141 lines). Every hunk classified:

| hunk | class | description |
|---|---|---|
| 2,3c2,13 | docstring only | header rewritten; describes Fatal/timeout/read_utf8/write/cli additions |
| 40a51 | behavior: import | `import signal` (for process-group kill) |
| 45a57,60 | behavior: new exception | `class Fatal(Exception)` |
| 76,79c91,103 | behavior: timeout in run() | subprocess.run → Popen + communicate(timeout) + killpg(SIGKILL) + Fatal on TimeoutExpired; new params `timeout, label` |
| 83a108,124 | behavior: new helpers | `read_utf8()` (non-UTF-8 → Fatal) and `write()` (OSError → Fatal) |
| 89a131 | behavior: new CLI arg | `--timeout` default 120 |
| 93,94c135 / 96,97c137 / 99,100c139,141 | refactor: error channel | print+return 2 → `raise Fatal(...)` for --work under /tmp|/var/tmp|/dev/shm, not-a-dir, not-empty; same exit-2 semantics now via cli() |
| (new) 138-140 | behavior: validation | `--timeout <= 0` → Fatal |
| 104,106c145,150 | behavior+refactor | not-readable-file → Fatal; input bytes read via read_utf8 (was open(utf-8).read()); makedirs wrapped in try/OSError → Fatal |
| 109,110c153 | refactor: call site | run() gains timeout/label args |
| 112,114c155 | refactor: error channel | positive-control no-SUMMARY print+return → Fatal |
| 123,124c164 | refactor: error channel | edit-not-applied-once print+return → Fatal |
| 127,129c167,169 | refactor | forgery tool write via write(); run() gains timeout/label |
| 131,137c171 | refactor | no-SUMMARY-for-forgery → Fatal; redundant second .out write dropped (now single write()) |
| 146a181,192 | behavior: catch-all | new `cli()` wraps main(): Fatal → `C2-FORGERY-FATAL:` exit 2; OSError → fatal line exit 2; any other Exception → `C2-FORGERY-FATAL: internal error …` exit 2 (never exit 1) |
| 148c194 | refactor: entry point | sys.exit(main) → sys.exit(cli) |

VERDICT-INVARIANT CHECK: the FORGERIES tuple is byte-identical between r94 and r95 (verified via ast.dump equality: True). The verdict computation is byte-identical: `rej = rc == 1 and res is not None and res[0] < res[1]`, `rejected += rej`, the FORGERY print, `FORGERY-SUMMARY … positive=…`, and `return 0 if positive and rejected == len(FORGERIES) else 1` are unchanged (modulo the refactored error-channel lines above). No hunk touches forgery ids, edit strings, or verdict logic.

## 6. Direct probe runs (not via arms counter)

### 6a. P1 inputs (r93 fixture)
Command: `python3 -B census/round-95/c2-forgery-probe.py --fixture tests/fixtures/r93-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>`
Exit: 0 (probe-direct.exit=EXIT=0). Wall: 142.94 s.

```
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
```
Byte-identical to the FORGERY lines in `census/round-94/records/c2-after-arms-out/P1.out` (diff of the two FORGERY line sets: empty). Stderr empty.

### 6b. r92 fixture
Same with `--fixture tests/fixtures/r92-k4-flagfail.py`. Exit: 1 (probe-r92.exit=EXIT=1). Wall: 37.94 s.

```
POSITIVE tool exit=0 tool_pass=20/20 pass
FORGERY F1 sha256=fe4ba3d65d25afb270cf93a56a5f3115837bcf17d4cbd70e8dc70602a4c72301 exit=1 tool_pass=18/20 rejected=yes failed=KFF16,KFF18
FORGERY F2 sha256=2fb79e5f5987899fcefc3797a0a75dec8270bb7dcc8886060f0e57437324dc0d exit=1 tool_pass=19/20 rejected=yes failed=KFF16
FORGERY F3 sha256=69bf77c3c48baaf626377029b206a8d21e36cf7969676a62ad9480f543d83873 exit=1 tool_pass=18/20 rejected=yes failed=KFF11,KFF18
FORGERY F4 sha256=43043c835953ba22361bba0e57d97e8a48350c1556af593ce4aaeabf23bdab5f exit=1 tool_pass=18/20 rejected=yes failed=KFF17,KFF18
FORGERY N0 sha256=21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c exit=1 tool_pass=16/20 rejected=yes failed=KFF14,KFF15,KFF16,KFF18
FORGERY F5 sha256=ed62852641bb1c3998d9b6bc74e52624dae4949cc3522c6fb1b4dd47b8f52727 exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY F6 sha256=99e30616c3dff96fc8383bd5b235defb20db5a9406b89cbf80095e16da32e60a exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY F7 sha256=027393918b46ac9d356aa3bd09567fa6abcc92e158e37766f7690b4baa42c3f3 exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass
```
`rejected=5`, exit 1, as specified. F5/F6/F7 edits are no-ops on the r92 fixture (tool_pass 20/20, exit 0) — same behaviour as r94's record (P2.out).

## 7. Receipts inventory (`.ufo/waves/round-95/w1/R95ExecC2/`)

- arms-after.stdout / .stderr / .exit (EXIT=0) + P1,P2,S1–S14 .out
- arms-control.stdout / .stderr / .exit (EXIT=1) + P1,P2,S1–S14 .out (S12/S9/S10/S11 empty — r94 probe died before writing)
- forgery-controls.stdout / .stderr / .exit (EXIT=0)
- probe-direct.stdout / .stderr / .exit (EXIT=0) + F1–F7,N0 .out
- probe-r92.stdout / .stderr / .exit (EXIT=1) + F1–F7,N0 .out
- diff-r94-r95.txt

## 8. NO-FALSIFICATION

No mismatch against the C2 claim wording, predicate, control or forgery numbers. Tried: all three full runs + both direct probe runs + FORGERIES AST-equality + verdict-line byte comparison + 8-file pin table + diff hunk classification.

## 9. Caveats / hazards

1. First forgery-controls attempt hit the 300 s harness background cap and left a partial receipt; re-ran with timeout=900 (completed in 587.56 s, EXIT 0). The .exit file was rewritten to the clean final EXIT=0.
2. Arms S12 (hang fixture) is inherently slow: after-arm ~120 s, control ~300 s (counter kill). Any future re-run needs timeout ≥ 800 s for the full forgery-controls suite.
3. P1.out/S1.out under the arms work dirs are probe stdout captures, not fixture .out files — copied for completeness.

Report: .ufo/waves/round-95/w1/R95ExecC2.md
