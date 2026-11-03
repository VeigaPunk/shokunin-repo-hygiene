# S56reviewer02 — differential review of the v5 receipt grammar (C2), souji round 56

Date: 2026-11-03 · Seat: S56reviewer02 (reviewer, attack on C2) · Wave: r56 w1
Measured revision: `cce21b555a617cadda782613ec1e9d3a0c12ac83` (base `fafe371694fea41c5d23f63083865d5ccf3f1d36`)

## Method and authority

- Read `census/round-56/preregistration.txt` first; freeze commit verified: `git log --diff-filter=A -1 cce21b55 -- census/round-56/preregistration.txt` → `cce21b55 round-56: freeze C1 counter v5 and C2 counter v5 …`.
- All eight frozen pins re-hashed from disk and matched byte-for-byte: `census/round-56/c1-counter.py` 975d3520…, `census/round-56/c2-counter.py` 56082011…, `fixtures/build-fixtures.py` 2f26d6aa…, `fixtures/run-matrix.sh` a7e1a892…, `records/c1-selftest-expected.tsv` 48a7cc0e…, `records/c2-selftest-expected.tsv` 90517c4d…, `census/round-55/c1-counter.py` 944feafa…, `census/round-55/c2-counter.py` e4eb34e6… (receipt `receipts/pincheck.txt`).
- Both counters read the capture, tool and run-receipt **only via `git show <rev>:<path>`** (`git_show_bytes`, scrubbed env). Shape injection therefore requires committed bytes. Mirror of the frozen fixture builder's own `init_repo`/`commit_all` pattern: a scratch-only git repo at `/fast/scratch/hyaku/souji-r56/S56reviewer02/diffrepo` seeded with the committed bytes of `census/round-55/records/fleet-root-census.tsv`, `…-run.txt` and `tools/souji-fleet-root-census.py` taken by read-only `git show cce21b555a61…:<path>`; one commit per shape. The lane repo was touched **only** with read-only `git show`; no mutating git/jj command ran anywhere; nothing was committed outside my scratch.
- Faithfulness control: base committed bytes in the mirror → v4 and v5 both exit 0, `receipt=ok sorted=ok tool_pin=ok` (`receipts/control.v4.out`, `control.v5.out`), and the prereg T5 invocation against the real lane root at `cce21b555a61…` prints the same SUMMARY and exits 0 (`receipts/reallane.out`).
- 75 shapes (task asked ≥ 60). Each shape = the committed receipt with exactly ONE line changed or inserted (byte-level shapes: CRLF, NUL, BOM applied to bytes). For every shape both frozen counters ran with `--capture census/round-55/records/fleet-root-census.tsv --tool-sha256 e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b` and the per-shape mirror rev. Every run's stdout+exit code is in `receipts/probes/<shape>.v4.out` / `.v5.out`, each ending `EXIT=<rc>`; the full table is `receipts/results.tsv` (ends `EXIT=0`).
- Grammars under test (read from frozen bytes): v5 `RECEIPT_KV = \s*#\s*([A-Za-z0-9_][A-Za-z0-9_]*)\s*=\s*(\S*)\s*` (fullmatch), v4 `\s*#\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S+?)\s*`; both match keys case-insensitively (`key.upper()` against `RECEIPT_KEYS`), both flag any `\r` in receipt bytes as RECEIPT-CRLF, both apply identical downstream checks.

## Control

```
v4: SUMMARY … receipt=ok sorted=ok tool_pin=ok rev=05f30ac527de  EXIT=0
v5: SUMMARY … receipt=ok sorted=ok tool_pin=ok rev=05f30ac527de  EXIT=0
real lane @ cce21b55: receipt=ok sorted=ok tool_pin=ok rev=cce21b555a61  EXIT=0
```

Corroboration: v5 selftest with pinned builder/expected shas prints `SELFTEST pass cases=18`, EXIT=0 (`receipts/c2-v5-selftest.out`).

## Full differential table (75 shapes)

First finding = first `FINDING`/`CANNOT-EVALUATE`/`PRISTINE` token; `—` = none (clean). Class: REPAIR-DIR = v4 passes, v5 refuses; NARROW-HARM? = v4 refuses, v5 passes; RELABEL = both refuse, different first finding.

| id | receipt change (one line) | v4 rc/first | v5 rc/first | class |
|---|---|---|---|---|
| S01 | insert `# buildhost=x` | 1 RECEIPT-UNKNOWN-KEY | 1 RECEIPT-UNKNOWN-KEY | SAME-REFUSE |
| S02 | insert `# BUILDHOST=x` | 1 RECEIPT-UNKNOWN-KEY | 1 RECEIPT-UNKNOWN-KEY | SAME-REFUSE |
| S03 | insert `# 1BUILDHOST=x` | 0 — | 1 RECEIPT-UNKNOWN-KEY | REPAIR-DIR |
| S04 | insert `# _BUILDHOST=x` | 0 — | 1 RECEIPT-UNKNOWN-KEY | REPAIR-DIR |
| S05 | insert `# BUILD-HOST=x` | 0 — | 0 — | SAME-PASS |
| S06 | insert `# .BUILDHOST=x` | 0 — | 0 — | SAME-PASS |
| S07 | insert `# BUILD.HOST=x` | 0 — | 0 — | SAME-PASS |
| S08 | L1 → three leading spaces + `# RECEIPT_VERSION=1` | 0 — | 0 — | SAME-PASS |
| S09 | L1 → leading TAB + `# RECEIPT_VERSION=1` | 0 — | 0 — | SAME-PASS |
| S10 | insert `# ÉBUILDHOST=x` | 0 — | 0 — | SAME-PASS |
| S11 | insert `# +BUILDHOST=x` | 0 — | 0 — | SAME-PASS |
| S12 | insert `# /BUILDHOST=x` | 0 — | 0 — | SAME-PASS |
| S13 | insert `# # BUILDHOST=x` | 0 — | 0 — | SAME-PASS |
| S14 | insert `# 2=x` | 0 — | 1 RECEIPT-UNKNOWN-KEY | REPAIR-DIR |
| S15 | insert `# _=x` | 0 — | 1 RECEIPT-UNKNOWN-KEY | REPAIR-DIR |
| S16 | L5 → `# =49` (empty key) | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S17 | insert `# X=1` | 1 RECEIPT-UNKNOWN-KEY | 1 RECEIPT-UNKNOWN-KEY | SAME-REFUSE |
| S18 | insert `# XY=1` | 1 RECEIPT-UNKNOWN-KEY | 1 RECEIPT-UNKNOWN-KEY | SAME-REFUSE |
| S19 | insert `# XYZ=1` | 1 RECEIPT-UNKNOWN-KEY | 1 RECEIPT-UNKNOWN-KEY | SAME-REFUSE |
| S20 | L5 → `# E=49` | 1 RECEIPT-UNKNOWN-KEY | 1 RECEIPT-UNKNOWN-KEY | SAME-REFUSE |
| S21 | L5 → `# 1=49` | 1 RECEIPT-MALFORMED | 1 RECEIPT-UNKNOWN-KEY | RELABEL |
| S22 | L1 → `# Receipt_Version=1` | 0 — | 0 — | SAME-PASS |
| S23 | L1 → `# RECEIPT_version=1` | 0 — | 0 — | SAME-PASS |
| S24 | L2 → `# tool_sha256=<good>` | 0 — | 0 — | SAME-PASS |
| S25 | L5 → `# Entries=49` | 0 — | 0 — | SAME-PASS |
| S26 | L1 → `#  RECEIPT_VERSION=1` (2 spaces after #) | 0 — | 0 — | SAME-PASS |
| S27 | L1 → `#\tRECEIPT_VERSION=1` | 0 — | 0 — | SAME-PASS |
| S28 | L1 → `## RECEIPT_VERSION=1` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S29 | L1 → `# RECEIPT_VERSION = 1` | 0 — | 0 — | SAME-PASS |
| S30 | L5 → `# ENTRIES = 49` | 0 — | 0 — | SAME-PASS |
| S31 | L2 → `# TOOL_SHA256 =<good>` | 0 — | 0 — | SAME-PASS |
| S32 | L3 → `# FLEET_HEAD= <good>` | 0 — | 0 — | SAME-PASS |
| S33 | insert `# BUILDHOST=` (empty value) | 0 — | 1 RECEIPT-UNKNOWN-KEY | REPAIR-DIR |
| S34 | L5 → `# ENTRIES=` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S35 | L1 → `# RECEIPT_VERSION=` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S36 | insert `# BUILDHOST = ` | 0 — | 1 RECEIPT-UNKNOWN-KEY | REPAIR-DIR |
| S37 | L3 → `# FLEET_HEAD=e5396bee 6496dd2c` (space in value) | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S38 | L5 → `# ENTRIES=49<TAB>` | 0 — | 0 — | SAME-PASS |
| S39 | L5 → `# ENTRIES=49 ` | 0 — | 0 — | SAME-PASS |
| S40 | L5 → `# ENTRIES=4 9` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S41 | L1 → `# RECEIPT_VERSION=1<TAB>extra` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S42 | L1 KV line ends CRLF | 1 RECEIPT-CRLF | 1 RECEIPT-CRLF | SAME-REFUSE |
| S43 | all lines CRLF | 1 RECEIPT-CRLF | 1 RECEIPT-CRLF | SAME-REFUSE |
| S44 | prose line ends CRLF | 1 RECEIPT-CRLF | 1 RECEIPT-CRLF | SAME-REFUSE |
| S45 | insert duplicate `# ENTRIES=49` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S46 | insert duplicate `# entries=49` (lowercase) | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S47 | insert duplicate `# TOOL_SHA256=<good>` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S48 | insert duplicate `# RECEIPT_VERSION=1` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S49 | all five KV keys lowercased | 0 — | 0 — | SAME-PASS |
| S50 | L4 → `# capture_sha256=<good>` | 0 — | 0 — | SAME-PASS |
| S51 | L5 → `# ENTRIES=49<NUL>` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S52 | prose L6 gains trailing NUL | 0 — | 0 — | SAME-PASS |
| S53 | insert `# BUILDHOST=x<NUL>` | 1 RECEIPT-UNKNOWN-KEY | 1 RECEIPT-UNKNOWN-KEY | SAME-REFUSE |
| S54 | BOM at byte 0 of file | 0 — | 0 — | SAME-PASS |
| S55 | L1 → `<BOM># RECEIPT_VERSION=1` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S56 | L5 → `# 9ENTRIES=49` | 1 RECEIPT-MALFORMED | 1 RECEIPT-UNKNOWN-KEY | RELABEL |
| S57 | L2 → `# _TOOL_SHA256=<good>` | 1 RECEIPT-MALFORMED | 1 RECEIPT-UNKNOWN-KEY | RELABEL |
| S58 | insert `# ENTRIES2=49` | 1 RECEIPT-UNKNOWN-KEY | 1 RECEIPT-UNKNOWN-KEY | SAME-REFUSE |
| S59 | L5 → `# ENTRIES  =  49` | 0 — | 0 — | SAME-PASS |
| S60 | insert whitespace-only line | 0 — | 0 — | SAME-PASS |
| S61 | insert `#KEY=VALUE` (no space) | 1 RECEIPT-UNKNOWN-KEY | 1 RECEIPT-UNKNOWN-KEY | SAME-REFUSE |
| S62 | insert `#_BUILDHOST=x` | 0 — | 1 RECEIPT-UNKNOWN-KEY | REPAIR-DIR |
| S63 | insert `#1BUILDHOST=x` | 0 — | 1 RECEIPT-UNKNOWN-KEY | REPAIR-DIR |
| S64 | L5 → `# ENTRIES==49` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S65 | L1 → `# RECEIPT_VERSION=1 # c` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S66 | L1 → `# RECEIPT_VERSION=01` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S67 | L5 → `# ENTRIES=+49` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S68 | L5 → `# ＥNTRIES=49` (fullwidth) | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S69 | L5 → `<NUL># ENTRIES=49` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S70 | L3 → `# FLEET_HEAD=é5396…` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S71 | L5 → `# ENTRIES=48` (off-by-one) | 1 CAPTURE-RECEIPT-MISMATCH | 1 CAPTURE-RECEIPT-MISMATCH | SAME-REFUSE |
| S72 | L2 → `# TOOL_SHA256=0{64}` | 1 CAPTURE-RECEIPT-MISMATCH | 1 CAPTURE-RECEIPT-MISMATCH | SAME-REFUSE |
| S73 | L4 → `# CAPTURE_SHA256=0{64}` | 1 CAPTURE-RECEIPT-MISMATCH | 1 CAPTURE-RECEIPT-MISMATCH | SAME-REFUSE |
| S74 | L1 → `# RECEIPT_VERSION=2` | 1 RECEIPT-MALFORMED | 1 RECEIPT-MALFORMED | SAME-REFUSE |
| S75 | insert empty line at top | 0 — | 0 — | SAME-PASS |

Totals: 75 shapes = 28 SAME-PASS + 36 SAME-REFUSE + 8 REPAIR-DIR + 3 RELABEL + **0 NARROW-HARM?**

## List 1 — narrowing harms (v4 refuses, v5 passes): NONE

Zero of 75 shapes. This matches the analytic argument: v5's KV language is a strict superset of v4's (first-char class `[A-Za-z0-9_]` ⊇ `[A-Za-z]`; value `\S*` ⊇ `\S+?`) with byte-identical downstream checks. Every extra line v5 parses can only (a) add RECEIPT-UNKNOWN-KEY, (b) mark a known-key duplicate malformed, or (c) fill a recv slot v4 left unset — but a digit/underscore-initial string never `.upper()`s to one of the five letter-initial known keys, and an empty value fails every per-key check (`!= '1'`, HEX64/HEX40, isdigit). No input moves v5 from refuse to pass relative to v4; the empirical sweep confirms it.

## List 2 — intended repairs (v4 passes, v5 refuses), 8 shapes, all first finding RECEIPT-UNKNOWN-KEY

| shape | line | prereg surface |
|---|---|---|
| S03 | `# 1BUILDHOST=x` | FC2 twin (digit-initial key) |
| S04 | `# _BUILDHOST=x` | FC1 twin (underscore-initial key) |
| S14 | `# 2=x` | digit-only key (v5 docstring shape) |
| S15 | `# _=x` | underscore-only key |
| S33 | `# BUILDHOST=` | FC3 twin (unknown key, empty value) |
| S36 | `# BUILDHOST = ` | empty value + spaces around `=` |
| S62 | `#_BUILDHOST=x` | no space after `#` variant of FC1 |
| S63 | `#1BUILDHOST=x` | no space after `#` variant of FC2 |

The repair family is consistent: every shape the r55 route named (RD-A first-character classes, S55-S5 empty value) is refused by name, and the no-space/only-key variants inherit the same refusal. Receipts: `receipts/probes/S03…S63.{v4,v5}.out` (e.g. S33: v4 `SUMMARY … receipt=ok … EXIT=0` silent; v5 `FINDING RECEIPT-UNKNOWN-KEY receipt carries unknown key BUILDHOST … EXIT=1`).

## List 3 — relabels (both refuse, different first finding), 3 shapes

| shape | line | v4 first finding | v5 first finding |
|---|---|---|---|
| S21 | `# 1=49` (replacing `# ENTRIES=49`) | RECEIPT-MALFORMED | RECEIPT-UNKNOWN-KEY (key `1`) |
| S56 | `# 9ENTRIES=49` | RECEIPT-MALFORMED | RECEIPT-UNKNOWN-KEY (key `9ENTRIES`) |
| S57 | `# _TOOL_SHA256=<good>` | RECEIPT-MALFORMED | RECEIPT-UNKNOWN-KEY (key `_TOOL_SHA256`) |

All three: exit 1 under both. v5 names the offending line and its key instead of a generic grammar failure — strictly more precise, no behavioral change. These are relabels in the intended direction (the digit/underscore repair now surfaces the actual culprit), not masking.

## Named limits (v5 exits 0 where a reasonable receipt reader would refuse)

All of these pass under v4 as well — pre-existing grammar tolerance, unchanged by v5, each reproducible from the committed receipt with the one-line edit; probes in `receipts/probes/`.

- **NL-A Case-insensitive known keys accepted.** `# receipt_version=1`, `# Receipt_Version=1`, `# tool_sha256=<good>`, `# Entries=49`, `# capture_sha256=<good>`, or all five keys lowercased → exit 0 (S22/S23/S24/S25/S50/S49). The grammar binds by `key.upper()`; only the exact-ASCII shapes are pinned anywhere. Note S46 shows the flip side is at least safe: a lowercase duplicate is still detected (malformed).
- **NL-B Whitespace tolerance around the KV shape.** Leading spaces/tab before `#` (S08/S09), extra spaces/tab between `#` and key (S26/S27), spaces around `=` (S29/S30/S31/S32/S59), trailing tab/space after the value (S38/S39), whitespace-only and empty lines (S60/S75) — all exit 0. A receipt whose machine block is `  #  ENTRIES  =  49   ` verifies as pristine.
- **NL-C Attempted-KV lines that miss fullmatch become invisible free-form comments.** `# BUILD-HOST=x`, `# .BUILDHOST=x`, `# BUILD.HOST=x`, `# ÉBUILDHOST=x`, `# +BUILDHOST=x`, `# /BUILDHOST=x`, `# # BUILDHOST=x`, `# =49` (empty key) — inserting any of them → exit 0 (S05/S06/S07/S10/S11/S12/S13/S16). The RD-A repair widens the key class to `[A-Za-z0-9_]` but a punctuation-initial, non-ASCII-initial, or empty-key attempt still parses as neither KV nor unknown key: it is silently ignored. A receipt reader that treats any `# X...=y` line as an attempted key would refuse; the counter cannot distinguish it from a scope comment.
- **NL-D NUL byte in a non-KV line ignored.** Appending `\x00` to the prose line → exit 0 (S52). (Adjacent to a KV line the NUL does break the fullmatch and the receipt is refused: S51/S53/S69 — so the NUL rule is positional, not a byte-level scan.)
- **NL-E Leading BOM accepted.** BOM at byte 0 → exit 0 (S54); only a BOM directly prefixing a KV line breaks that line's match → RECEIPT-MALFORMED (S55).

## Residual risk and verification gaps

- The differential covers the receipt grammar path (RECEIPT_KV, RECEIPT_KEYS, the parse loop) and its interactions with CRLF/NUL/BOM/bytes. It does not fuzz the capture-side checks (COUNT recount, CLASS-MISMATCH, COMMENT-AMBIGUOUS-NAME) — those are v4 carry-over and out of this seat's target.
- First-finding extraction treats the first `FINDING` line as the name; where findings accumulate (e.g. S21 v5 also carries RECEIPT-MALFORMED second) the full stdout is preserved in the probes, so nothing is hidden by the abbreviation.
- NL-C is the largest standing hole in strictness: an attacker can smuggle arbitrary `# <punct>KEY=value` lines past both v4 and v5. It is a limit to route, not a claim-killer: prereg C2 T1–T7 concern the committed fixtures and the real-lane invocation, all of which hold here.
- No tooling was installed or upgraded (none needed); no pacman transaction run.

## Verdict

No narrowing harm in 75 shapes; the intended repair family refuses by name; three precise relabels; five named limits, all shared with v4.

VERDICT: ATTACK-SURVIVED

Receipts copied into this seat dir under `receipts/`: pincheck.txt, results.tsv, probes/ (150 files, each ending EXIT=<rc>), control.v4.out, control.v5.out, reallane.out, c2-v5-selftest.out. Scratch tree deleted after copy.

EXIT=0
