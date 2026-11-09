# R92ExecC2Fixture — C2 re-derivation on committed bytes

Seat: R92ExecC2Fixture. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
(HEAD e8d31f06c381249bdeaa8ea1a8f2bebe3f5bf81e, commit F, verified via `git rev-parse HEAD`).
All runs: `cd /home/vgpnk/Projects/shokunin/souji-shokunin`, `python3 -B`, work dirs under
/fast/scratch/hyaku/souji-r92/R92ExecC2Fixture/ (deleted after receipts copied; see end).
Receipts (text only, in `.ufo/waves/round-92/w1/R92ExecC2Fixture/`):
- receipt-c2-after.txt (sha256 f6ec53c4...)
- receipt-c2-control.txt (sha256 3dfe8b9a...)
- receipt-forgery.txt (sha256 2f154054...)
- receipt-k4-regression.txt (sha256 d0b51a61...)
- receipt-kff13-spaced.txt (sha256 a3178ebb...)
- receipt-kff13-docstring.txt (sha256 c3733a79...)

## Pin table (sha256sum on committed bytes)

| File | sha256 | Prereg value | Verdict |
|---|---|---|---|
| tools/souji-record-agreement.py (filed tool) | fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75 | fc0e35c2... | MATCH |
| census/round-92/controls/c2-before-tool.py (before arm) | 21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c | 21e5c7408fef... | MATCH |
| tests/fixtures/r92-k4-flagfail.py (fixture) | 2c9bd76c77c609bfaf2fd1a86a5bd022fc8549cd58bc2f198a029e3ea90feeae | 2c9bd76c77c6... | MATCH |
| census/round-92/c2-forgery-probe.py (probe) | 9dac4cde51d1cee96ba479900fa221e29a4b0b3bc7386ca2a94dc094531ca690 | (run-header self-report) | — |
| census/round-87/c2-k4-counter.py (r87 regression counter) | 4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e | (run-header self-report) | — |

Before-arm identity: `git show 5339b2ac79f81aa446f6a2cd4700321cf4982fd3:tools/souji-record-agreement.py
| sha256sum` = 21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c, and
`diff <(git show ...:tools/souji-record-agreement.py) census/round-92/controls/c2-before-tool.py`
is empty (IDENTICAL). So the r91 control copy is byte-for-byte the lane-base tool.

## 1. After arm (filed tool)

Command:
`python3 -B tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py
 --before census/round-92/controls/c2-before-tool.py --work <fresh scratch>`
EXIT=0. Full receipt: receipt-c2-after.txt. Lines quoted verbatim:

```
# KFF13 selfcheck spaced=detected docstring=clean
# tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py sha256=fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75
# before path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-92/controls/c2-before-tool.py sha256=21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c
# fixture sha256=2c9bd76c77c609bfaf2fd1a86a5bd022fc8549cd58bc2f198a029e3ea90feeae
# KFF18 tool=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py payloads=29700 unfaithful=0
# KFF18 tool=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-92/controls/c2-before-tool.py payloads=29700 unfaithful=28
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
CASE KFF9 tool=pass before=pass
CASE KFF10 tool=pass before=pass
CASE KFF11 tool=pass before=pass
CASE KFF12 tool=pass before=pass
CASE KFF13 tool=pass before=pass
CASE KFF14 tool=pass before=fail
CASE KFF15 tool=pass before=fail
CASE KFF16 tool=pass before=fail
CASE KFF17 tool=pass before=pass
CASE KFF18 tool=pass before=fail
SUMMARY cases=20 tool_pass=20 before_pass=16
```

Predicate `SUMMARY cases=20 tool_pass=20 before_pass=16` + EXIT 0: **REPRODUCED exactly.**

## 2. Control (r91 tool as both arms)

Command:
`python3 -B tests/fixtures/r92-k4-flagfail.py --tool census/round-92/controls/c2-before-tool.py
 --before census/round-92/controls/c2-before-tool.py --work <fresh scratch>`
EXIT=1. Full receipt: receipt-c2-control.txt. Quoted verbatim:

```
# KFF13 selfcheck spaced=detected docstring=clean
# tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-92/controls/c2-before-tool.py sha256=21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c
# before path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-92/controls/c2-before-tool.py sha256=21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c
# fixture sha256=2c9bd76c77c609bfaf2fd1a86a5bd022fc8549cd58bc2f198a029e3ea90feeae
# KFF18 tool=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-92/controls/c2-before-tool.py payloads=29700 unfaithful=28
# KFF18 tool=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-92/controls/c2-before-tool.py payloads=29700 unfaithful=28
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
CASE KFF9 tool=pass before=pass
CASE KFF10 tool=pass before=pass
CASE KFF11 tool=pass before=pass
CASE KFF12 tool=pass before=pass
CASE KFF13 tool=pass before=pass
CASE KFF14 tool=fail before=fail
CASE KFF15 tool=fail before=fail
CASE KFF16 tool=fail before=fail
CASE KFF17 tool=pass before=pass
CASE KFF18 tool=fail before=fail
SUMMARY cases=20 tool_pass=16 before_pass=16
R92-FIXTURE-FAIL: the tool under test does not pass every case
```

Predicate `SUMMARY cases=20 tool_pass=16 before_pass=16`, KFF14/KFF15/KFF16/KFF18 red, EXIT 1:
**REPRODUCED exactly.** Line-for-line identical to the committed
census/round-92/controls/c2-control-r91-tool-both-arms.txt.

## 3. Forgery probe

Command:
`python3 -B census/round-92/c2-forgery-probe.py --fixture tests/fixtures/r92-k4-flagfail.py
 --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py
 --work <fresh scratch>`
EXIT=0. Full receipt: receipt-forgery.txt. Quoted verbatim (after the 4 `# ...` header lines):

```
POSITIVE tool exit=0 tool_pass=20/20 pass
FORGERY F1 sha256=fe4ba3d65d25afb270cf93a56a5f3115837bcf17d4cbd70e8dc70602a4c72301 exit=1 tool_pass=18/20 rejected=yes failed=KFF16,KFF18
FORGERY F2 sha256=2fb79e5f5987899fcefc3797a0a75dec8270bb7dcc8886060f0e57437324dc0d exit=1 tool_pass=19/20 rejected=yes failed=KFF16
FORGERY F3 sha256=69bf77c3c48baaf626377029b206a8d21e36cf7969676a62ad9480f543d83873 exit=1 tool_pass=18/20 rejected=yes failed=KFF11,KFF18
FORGERY F4 sha256=43043c835953ba22361bba0e57d97e8a48350c1556af593ce4aaeabf23bdab5f exit=1 tool_pass=18/20 rejected=yes failed=KFF17,KFF18
FORGERY N0 sha256=21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c exit=1 tool_pass=16/20 rejected=yes failed=KFF14,KFF15,KFF16,KFF18
FORGERY-SUMMARY forgeries=5 rejected=5 positive=pass
```

Predicate `FORGERY-SUMMARY forgeries=5 rejected=5 positive=pass` + EXIT 0: **REPRODUCED exactly.**
Note: N0 is the r91 tool (sha256 21e5c740...), rejected 16/20, as prereg states.

## 4. r87 K4 regression

Command:
`python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <fresh scratch>`
EXIT=0. Full receipt: receipt-k4-regression.txt. Quoted verbatim:

```
# tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py sha256=fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75
# writer path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-write.py sha256=70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa
# counter sha256=4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e
# fixture clone=/fast/scratch/hyaku/souji-r92/R92ExecC2Fixture/w4/clone rev=e295278b97d7513900e2f9a0e48bffad602a7479
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
ROW KN3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['bad\nname2.txt|uncommitted-path']
SUMMARY rows=12 mismatches=0 errors=0
```

Predicate `SUMMARY rows=12 mismatches=0 errors=0` + EXIT 0: **REPRODUCED exactly.**

## 5. Diff: filed tool vs r91 tool (hunk inventory)

`diff -u census/round-92/controls/c2-before-tool.py tools/souji-record-agreement.py` — exactly two
hunks, 91 diff lines, no other changes anywhere in the file (imports, CLI, K4 logic untouched):

| Hunk | Lines | Class | Content |
|---|---|---|---|
| 1 | @@ -213,47 +213,39 @@ | cut helpers | Replaces `_utf8_seq_need` (structural length C0-DF/2, E0-EF/3, F0-F7/4) with `_straddling_sequence(raw, cut)`: scans back ≤3 start positions and forward ≤4 end positions, returns the (start, end) of the slice that strictly decodes (`utf-8`/`strict`) to exactly one character — applying every Unicode Table 3-7 row (no C0/C1/F5-FF lead, no E0 80-9F overlong, no ED A0-BF surrogate, no F4 90-BF beyond U+10FFFF, all continuations present). `_cut_head` body replaced with `_straddling_sequence` + return seq[0]; signature return annotation fixed `-> str` → `-> int` (the old annotation was wrong: it always returned a byte offset). `_cut_tail` body replaced with `_straddling_sequence` + return seq[1]. Docstrings updated (S355 provenance; head cut keeps ill-formed bytes rather than moving; tail cut keeps ill-formed bytes so the tail is always a suffix of the whole render). |
| 2 | @@ -268,7 +260,11 @@ | docstring | `_one_line_bytes` docstring appends an r92 (S355) paragraph: a cut moves only across a well-formed sequence; the excerpt's head is a prefix and its tail a suffix of `_escape_text(_decode_record(raw))`. No code change in this hunk. |

UNEXPECTED hunks: **none** — every changed hunk is a cut helper or docstring; no logic outside the
cut window (_decode, _escape_text, _one_line_bytes body, K4 cells, CLI) changed at all.

## 6. KFF13 self-check probes

The fixture's built-in self-check printed `# KFF13 selfcheck spaced=detected docstring=clean` in both
the after and control runs (both directions exercised: a spaced `def _one_line (text)` is AST-detected,
a docstring mention is not). This seat additionally ran the fixture against scratch copies of the filed
tool (work dirs under /fast/scratch/hyaku/souji-r92/R92ExecC2Fixture/, removed after receipts copied):

**Probe A — spaced definition (must fail KFF13):**
`cp tools/souji-record-agreement.py $S/tool-spaced.py` then append `def _one_line (x): return x`
(sha256 681e796b032bf20e5c1a27ba698925f74d3320235941696a92c7e373727961ea).
Fixture run quotes:
```
CASE KFF13 tool=fail before=pass
SUMMARY cases=20 tool_pass=19 before_pass=16
EXIT=1
```
Only KFF13 failed (19/20); all other cases unaffected. Receipt: receipt-kff13-spaced.txt.

**Probe B — docstring mention only (must pass KFF13):**
`cp tools/souji-record-agreement.py $S/tool-docstring.py` then append
`func _note() { """docstring merely mentions _one_line( here""" ... }`
(sha256 2ffb086b6a704658b76cde83fb818a45c6b271a03883de6139696fbc81de6ba3).
Fixture run quotes:
```
CASE KFF13 tool=pass before=pass
SUMMARY cases=20 tool_pass=20 before_pass=16
EXIT=0
```
Receipt: receipt-kff13-docstring.txt.

Both probe outcomes match the prereg's KFF13 description exactly (spaced detection fails KFF13;
docstring mention passes).

## NO-FALSIFICATION

All four C2 predicates reproduce to the byte on committed bytes; every quoted line matches the prereg;
the pin table matches (including the full 64-hex hashes the prereg abbreviates); the before-arm is
byte-for-byte the lane-base tool; the diff contains no UNEXPECTED hunks; both KFF13 probes behave as
specified. Nothing in this seat's artifacts falsifies any sentence of C2.

What was tried to falsify: fresh re-derivation of all four predicates (not copying committed receipts —
the control receipt was checked against my own run and agrees line-for-line), pin verification by
independent `sha256sum` and `git show`, full diff classification of the tool repair, and two
independent KFF13 probes against copies carrying the exact spaced-def/docstring shapes the prereg names.

Non-falsifying note: the forgery probe's first invocation failed with `FileExistsError` on `--work`
because I pre-created the dir (`os.makedirs` without exist_ok) — a caller error, not a claim issue;
re-run with a fresh work dir reproduced the predicate exactly.

## Scratch cleanup

All scratch lived under /fast/scratch/hyaku/souji-r92/R92ExecC2Fixture/ (peak well under 1 GB: four
fixture work dirs, the K4 regression clone, two tool copies, receipts). Text receipts were copied to
.ufo/waves/round-92/w1/R92ExecC2Fixture/ BEFORE `rm -rf /fast/scratch/hyaku/souji-r92/R92ExecC2Fixture`;
no clones remain. No git/jj mutation was run anywhere (the K4 regression's internal fixture clone
is inside the removed scratch). No fleet-root tracked file was touched; no host sysctl, sudo, or
pacman use. No tool installs (none needed).
