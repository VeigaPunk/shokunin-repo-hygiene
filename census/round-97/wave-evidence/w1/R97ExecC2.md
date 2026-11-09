# R97ExecC2 — C2 re-derivation on committed bytes (r97 after arms, do-nothing control, forgery controls)

Seat: R97ExecC2 (leaf, no dispatch). Lane: souji-shokunin. Scratch removed at end (/fast/scratch/hyaku/souji-r97/R97ExecC2/ deleted; text receipts copied here).
Lane master at run time: fd0be377371a8f792d428f601fa546554caf2ba8 (receipts from 07:36 to 07:45). The P2 receipts record 053287d4…; every committed file in the pin table below matches its P2-recorded sha256, so the probe/counter/fixture/tool bytes are unchanged between the two masters.
Receipts and copies: `.ufo/waves/round-97/w1/R97ExecC2/` — `receipt-*.txt`, `arms-out-after/` (21 per-ARM .out), `arms-out-r96-committed/`, `arms-out-r95/`, `forgery-ctl-out/` (GA–GD .out and forged probe copies), `diff-r96-r97-probe.diff`.

VERDICT: the after-arm numbers reproduce exactly. Three prereg control sentences do NOT reproduce, and one wording sentence is falsified by this seat's own runs. Details in FALSIFIES-WORDING and FALSIFIES-NUMBER below. Per the mismatch rule, all of these are HIGH.

## 1. Receipts (exact lines, exit codes)

### 1a. After arms — r97 probe, committed counter  (receipt-after-arms-r97-probe.txt)
Command: `python3 -B census/round-97/c2-setup-arms.py --probe census/round-97/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty a1> --jobs 4`
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
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARM T2 exit=2 want=2 line=yes conform=yes
ARM T3 exit=2 want=2 line=yes conform=yes
ARM T4 exit=2 want=2 line=yes conform=yes
ARMS-SUMMARY arms=20 conform=20
EXIT 0
```
Matches the prereg predicate line `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0` and `ARMS-SUMMARY arms=20 conform=20`, EXIT 0. Reproduced.
T1.out (arms-out-after/T1.out): `C2-FORGERY-FATAL: the fixture run for the positive control exceeded --timeout 120s; its process group was killed` then `--survivors 0 planted-killed 1--`.

### 1b. Do-nothing control, r95 probe  (receipt-control-r95-probe.txt)
```
ARM S12 exit=2 want=2 line=yes conform=yes
ARM T1 exit=hung want=2 line=no conform=no survivors=0
ARM T2 exit=2 want=2 line=yes conform=yes
ARMS-SUMMARY arms=20 conform=19
EXIT 1
```
(Other arms: same as 1a, all conform=yes; full text in receipt.) Matches prereg control (T1 hung, conform=19, EXIT 1). Reproduced.

### 1c. Do-nothing control, r96 probe, committed counter  (receipt-control-r96-probe-committed-counter.txt)
```
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=20
EXIT 0
```
Prereg says for this control: "conform=20 with `survivors=1` on T1". Observed survivors=0. See H-2 / FALSIFIES-NUMBER.

### 1d. Forgery controls, r97 probe  (receipt-forgery-controls-r97.txt)
```
FORGERY GA sha256=a84f0b90647c725a944bc7f665e57bf7f64ee525e6fd5044774fdb60c16ecd1d arms_exit=1 summary=arms=20,conform=19 refused=yes
  GA ARM P2 exit=2 want=1 line=yes conform=no
FORGERY GB sha256=f0f3ef94c3c3049c35784698a0748abef4a57122db0d7ee860e66753d6c17f4b arms_exit=1 summary=arms=20,conform=18 refused=yes
  GB ARM S9 exit=1 want=2 line=no conform=no
  GB ARM S10 exit=0 want=2 line=no conform=no
FORGERY GC sha256=c946fd03b8aadabdf348454cfc43fe236bb0c7779b43f00dabe97f4d482481ce arms_exit=1 summary=arms=20,conform=0 refused=yes
  (GC: every ARM exit=1, line=no, conform=no — P1 through T4; see H-3)
FORGERY GD sha256=3a91d275d663d970cd6326ea3a1e596ca004cb11bac50945d478c99ee50d3699 arms_exit=0 summary=arms=20,conform=20 refused=no
C2-FORGERY-CTL-SUMMARY forgeries=4 refused=3
EXIT 1
```
Forged-probe sha256 values match the P2 forgery receipt exactly (GA a84f0b90…, GB f0f3ef94…, GC c946fd03…, GD 3a91d275…), so the forged texts are the committed ones.
Prereg says `C2-FORGERY-CTL-SUMMARY forgeries=4 refused=4`, EXIT 0. Observed refused=3, EXIT 1. See FALSIFIES-NUMBER.

## 2. Pin table (sha256 of this seat's reads vs. P2 receipt headers)

| file | sha256 observed | P2/prereg record | match |
|---|---|---|---|
| census/round-97/c2-forgery-probe.py | e95a6d7423405b49edb2449f7e9f64419e68f83ca3b4144cd51ad11126959500 | e95a6d74… (P2 forgery receipt header) | yes |
| census/round-97/c2-setup-arms.py | da30593c210ed6c6c3dd6dab6e5af311c7fa8c401707281d51cc758436cdff76 | da30593c… (P2 r95-control receipt header) | yes |
| census/round-97/c2-setup-arms.py | (same) | b460c6f4… (P2 r96-control receipt header) | **NO** — H-2 |
| census/round-97/c2-forgery-controls.py | dadb12d2f32460439da252292eca9a35295359d600e4387eeb532294e0c43f21 | not recorded in prereg/P2 | n/a |
| tests/fixtures/r93-k4-flagfail.py | ed15094e9ff17c159df9dd04d3b4d3878b2a1f23ecdc6175dc1759d1146e7a6a | ed15094e… | yes |
| tests/fixtures/r92-k4-flagfail.py | 2c9bd76c77c609bfaf2fd1a86a5bd022fc8549cd58bc2f198a029e3ea90feeae | 2c9bd76c… | yes |
| tools/souji-record-agreement.py | fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75 | fc0e35c2… | yes |
| census/round-92/controls/c2-before-tool.py | 21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c | 21e5c740… | yes |
| census/round-96/c2-forgery-probe.py | 9f989da8ad49948189c71ab37e55225cf318cfda4bd15fab134df7b9c2fb695b | 9f989da8… (P2 r96 header) | yes |
| census/round-95/c2-forgery-probe.py | bd83e120a71fe01073f63f5bdbafedd468bd772b9fc46fc12b893abc479fdc73 | bd83e120… (P2 r95 header) | yes |

## 3. Hunk inventory: census/round-96/c2-forgery-probe.py -> census/round-97/c2-forgery-probe.py

Full diff: `diff-r96-r97-probe.diff` (105 lines, 4 hunks). Classification:
- H1 `@@ -87,28 +87,63 @@`: `_wait_output` replaced. `communicate(timeout)` becomes a selectors drain with an 8 MiB byte cap (A5); over-cap raises `Fatal` after killpg. Timeout path unchanged in effect (killpg, `killed=True`). `run()` gains `max_output` and forwards it. Operability (A5).
- H2 `@@ -140,6 +175,7 @@`: adds `--max-output` (default 8388608). Operability (A5).
- H3 `@@ -161,7 +197,7 @@`: positive-control `run(...)` call passes `ns.max_output`. Plumbing.
- H4 `@@ -176,7 +212,7 @@`: per-forgery `run(...)` call passes `ns.max_output`. Plumbing.

Byte identity of the forgery tuples and verdict:
- `FORGERIES = (...)` block (1399 bytes): sha256 `843209d750ac9c0424ec2b09603e95e751c3a812e382d9635dd94ad8d1155e7a` in BOTH r96 and r97. No hunk touches it. Eight tuples identical.
- Verdict line `return 0 if positive and rejected == len(FORGERIES) else 1` (r96 L189, r97 L225) and the `FORGERY-SUMMARY` print (r96 L188, r97 L224) are outside every hunk: identical.
- `FORGERY {fid}` and `POSITIVE tool` print lines: outside every hunk: identical.

## 4. Direct probe runs (not via the arms counter)  (receipt-direct-probe-r93-pass.txt, receipt-direct-probe-r92-fail.txt)

P1 inputs, r97 probe:
```
POSITIVE tool exit=0 tool_pass=22/22 pass
FORGERY F1 ... exit=1 tool_pass=18/22 rejected=yes failed=KFF16,KFF18,KFF19,KFF20
FORGERY F2 ... exit=1 tool_pass=19/22 rejected=yes failed=KFF16,KFF19,KFF20
FORGERY F3 ... exit=1 tool_pass=19/22 rejected=yes failed=KFF11,KFF18,KFF19
FORGERY F4 ... exit=1 tool_pass=19/22 rejected=yes failed=KFF17,KFF18,KFF19
FORGERY N0 ... exit=1 tool_pass=16/22 rejected=yes failed=KFF14,KFF15,KFF16,KFF18,KFF19,KFF20
FORGERY F5 ... exit=1 tool_pass=21/22 rejected=yes failed=KFF19
FORGERY F6 ... exit=1 tool_pass=21/22 rejected=yes failed=KFF19
FORGERY F7 ... exit=1 tool_pass=21/22 rejected=yes failed=KFF19
FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass
EXIT 0
```
Reproduced: `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass`, EXIT 0. Every FORGERY line (sha256 included) and the POSITIVE line are identical to `census/round-93/records/c2-forgery-after.txt`.

Note on the comparison target: the acceptance text names `census/round-95/records/` as the reference for the FORGERY lines. That directory contains no FORGERY lines (`grep -c '^FORGERY' census/round-95/records/c2-after.txt` = 0; it holds arm output only). I compared against the r93 record above, which is the same P1-input probe output.

r92 fixture, r97 probe:
```
POSITIVE tool exit=0 tool_pass=20/20 pass
FORGERY F1..F4, N0 ... rejected=yes (same tool_pass/failed fields as census/round-92/records/c2-forgery-after.txt)
FORGERY F5 ... exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY F6 ... exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY F7 ... exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass
EXIT 1
```
Reproduced: `rejected=5`, EXIT 1. Against `census/round-92/records/c2-forgery-after.txt` the only differences are the three added F5/F6/F7 lines and the summary line (`forgeries=5` there, `forgeries=8` here); that record predates the eight-forgery table. Expected, not a mismatch.

## 5. Findings

### FALSIFIES-WORDING

**W-1 (C2 forgery control GD, prereg lines 115-121 and the counter comment).** Prereg: "GD (the probe reports survivors=0 without reaping; the counter's identity check kills any arm whose T1 process is still alive) conform=19 ... Claiming reaping without doing it ... does not meet the predicate." And forgery-controls.py: "the counter's identity check counts surviving T1 processes and keeps survivors>0".
- Observed: GD `arms=20,conform=20 refused=no`. In the committed counter `c2-setup-arms.py` (lines 295-338) the T1 arm first SIGKILLs every own-uid process carrying the fixture path (`planted-killed`), and only then counts `survivors`. `survivors` can be > 0 only if the SIGKILL fails. Observed in every T1 run that compiles: `--survivors 0 planted-killed 1--` (a1 r97, a2 r95, a3 r96-committed, f/GA, f/GB, f/GD).
- Consequence: a probe that claims refusal without reaping cannot be caught by `survivors`. The counter reaps for it. The "GD refused" wording is false on committed bytes.
- Reproducer: `R97ExecC2/receipt-forgery-controls-r97.txt` (GD line) and `R97ExecC2/forgery-ctl-out/GD.out`, `GD-c2-forgery-probe.py` (T1 .out shows `planted-killed 1`).

**W-2 (C2 counted quantity and do-nothing control, prereg lines 97-98 and 113-114).** "the survivor quantity is what moves" and "No work does not reach survivors=0 with conform=20."
- Observed: the do-nothing control (r96 probe, unchanged) reaches `ARMS-SUMMARY arms=20 conform=20` with `ARM T1 ... survivors=0` on the committed counter (receipt-control-r96-probe-committed-counter.txt, EXIT 0). So survivors=0 with conform=20 is reached without any work on the probe. The predicate (survivors=0, conform=20) does not separate the r96 probe from the r97 probe on committed bytes; the survivor quantity does not move between them.
- The only thing that produced the "survivors 1/2" for the before side is an older counter (see H-2), not the r96 probe.
- Reproducer: `receipt-control-r96-probe-committed-counter.txt`, `arms-out-r96-committed/T1.out` (`--survivors 0 planted-killed 1--`).

### FALSIFIES-NUMBER

**N-1 (prereg, C2 control r96 probe).** "Against the r96 probe (census/round-96/c2-forgery-probe.py): conform=20 with `survivors=1` on T1."
- Observed on committed counter: `survivors=0`, conform=20 (receipt-control-r96-probe-committed-counter.txt). The P2 r96-control receipt also shows `survivors=0` (conform=20), but was produced by a different counter file (H-2). No run in this seat produced survivors=1.
- Reproducer: `receipt-control-r96-probe-committed-counter.txt`.

**N-2 (prereg, C2 control GC).** "GC (no fixture timeout) conform=18 (S12 and T1 exit 2 hung arms)."
- Observed: `summary=arms=20,conform=0`, all twenty arms `exit=1 ... line=no` (receipt-forgery-controls-r97.txt; also P2 receipt c2-forgery-controls.txt, identical).
- Cause (H-3): the GC edit replaces `"    if total > max_output:\n"` (12-space indent) with `"    pass  # GC forgery ...\n"`. The next line `sel.close()` keeps 16-space indent. `ast.parse` of the forged text: `SyntaxError: unexpected indent, line 129`. So the forged probe does not compile and every arm exits 1. The refusal happens for a syntax reason, not for the no-timeout reason the prereg describes. Reproducer: `forgery-ctl-out/GC.out`, `GC-c2-forgery-probe.py`; parse check run in this seat (see H-3 below).

**N-3 (prereg, C2 control GD).** "GD ... conform=19."
- Observed `conform=20` in the P2 receipt and in this re-run (both `arms_exit=0`, `refused=no`). Reproducer: receipt-forgery-controls-r97.txt.

**N-4 (prereg, C2 forgery-control summary).** "`C2-FORGERY-CTL-SUMMARY forgeries=4 refused=4`, EXIT 0."
- Observed: `C2-FORGERY-CTL-SUMMARY forgeries=4 refused=3`, EXIT 1 (both P2 receipt and this re-run). Reproducer: receipt-forgery-controls-r97.txt.

### Hypotheses/records

H-2 (provenance, HIGH): P2 receipt `census/round-97/controls/c2-control-r96-probe.txt` records counter sha256 `b460c6f4a25a97c8efd02c453025668e37dd31fe0008afd7469b2b2424d808bf`, which is not the committed `c2-setup-arms.py` (`da30593c…`). Its arms are therefore not from the committed counter. The prereg's control numbers (survivors=1) cannot be traced to any committed bytes. The P2 receipt's own survivors=0 contradicts the prereg (see N-1).

H-3 (GC forged probe is a syntax error): confirmed by `ast.parse` on the four forged texts in this seat: GA, GB, GD parse OK (each applies to exactly one occurrence); GC raises `SyntaxError: unexpected indent` at line 129 (`sel.close()`).

H-1 (GD refused=no) and H-4/H-5 below.

H-4 (GA and GB match prereg): GA conform=19 (P2 exit 2 on ARM P2), GB conform=18 (S9 exit 1, S10 exit 0). Reproduced.

H-5 (r95 control matches prereg): T1 hung, conform=19, EXIT 1. Reproduced.

## 6. Checks
- Tooling installed: none. No pacman, no sudo, no ~/.local/bin writes.
- Commands run: the three requested runs (all receipts above), the r96 do-nothing control on committed counter (an added control, needed to resolve N-1 and W-2), the direct probe runs on r93 and r92, and read-only AST parse checks on forged texts.
- Not run: the R96 probe's own process-level reaping with the counter's kill disabled (would isolate whether the probe itself leaves the S368 grandchild alive; out of the listed steps). Not claimed either way.
- Scratch `/fast/scratch/hyaku/souji-r97/R97ExecC2/` removed. Seat contains text receipts only.
- Main agent verification: none required from this seat beyond reading the receipts; the arms and direct-probe receipts are reproducible with the commands in each receipt header.

## 7. Summary of falsifications for the L1 (record in plans/round-97.md)
- FALSIFIES-WORDING W-1: C2 GD control "counter identity check ... keeps survivors>0" — false on committed counter (kills before counting). Reproducer: receipt-forgery-controls-r97.txt.
- FALSIFIES-WORDING W-2: C2 "survivor quantity is what moves" / "no work does not reach survivors=0 with conform=20" — the r96 probe reaches survivors=0 conform=20 on the committed counter. Reproducer: receipt-control-r96-probe-committed-counter.txt.
- FALSIFIES-NUMBER N-1: C2 r96 control `survivors=1` — observed 0. Reproducer above.
- FALSIFIES-NUMBER N-2: C2 GC control `conform=18` — observed 0 (forged probe is an IndentationError). Reproducer: forgery-ctl-out/GC.out.
- FALSIFIES-NUMBER N-3: C2 GD control `conform=19` — observed 20.
- FALSIFIES-NUMBER N-4: C2 control summary `forgeries=4 refused=4, EXIT 0` — observed `refused=3`, EXIT 1.
- HIGH provenance H-2: P2 r96-control receipt built from counter b460c6f4…, not the committed da30593c….
- No C2 after-arm number is falsified: `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0`, `ARMS-SUMMARY arms=20 conform=20`, EXIT 0 reproduced; forgery probe direct runs reproduced (`forgeries=8 rejected=8`, EXIT 0; `rejected=5`, EXIT 1).
