# R93ExecC2 — C2 re-derivation and beyond-sweep reference test

Status: complete. Seat dir: `.ufo/waves/round-93/w1/R93ExecC2/`.

## 1. Five runs (all saved in seat dir)

| # | Command (cwd = lane) | Receipt | Result |
|---|----------------------|---------|--------|
| a1 | probe after: `census/round-93/c2-forgery-probe.py --fixture tests/fixtures/r93-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>` | `a1-probe-after.txt` | `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass` EXIT 0 — matches prereg C2 after arm |
| a2 | probe control: same with `--fixture tests/fixtures/r92-k4-flagfail.py` | `a2-probe-control-r92.txt` | `FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass` EXIT 1 — matches prereg control (F5/F6/F7 `rejected=no` 20/20) |
| a3 | fixture after: `tests/fixtures/r93-k4-flagfail.py --tool tools/souji-record-agreement.py --before ...` | `a3-fixture-after.txt` | `SUMMARY cases=22 tool_pass=22 before_pass=16` EXIT 0; `# KFF19 ... payloads=14586 inexact=0`, `# KFF18 ... payloads=29700 unfaithful=0` |
| a4 | r91 both arms: `tests/fixtures/r93-k4-flagfail.py --tool census/round-92/controls/c2-before-tool.py --before census/round-92/controls/c2-before-tool.py` | `a4-r91-both.txt` | `SUMMARY cases=22 tool_pass=16 before_pass=16` EXIT 1; `R93-FIXTURE-FAIL` — matches filed control |
| a5 | r87 K4 regression: `census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <empty>` | `a5-r87-k4.txt` | `ROW` lines KH1–KN3 all `match=yes`; `SUMMARY rows=12 mismatches=0 errors=0` EXIT 0 |

Quoted lines (verbatim from receipts):

a1 (probe after):
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
EXIT=0
```
a2 (probe control, r92 fixture): `FORGERY F5/6/7 ... exit=0 tool_pass=20/20 rejected=no`, `FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass`, `EXIT=1`.
a3 (fixture after): `SUMMARY cases=22 tool_pass=22 before_pass=16`, `EXIT=0`; KFF19 inexact=0/14586, KFF18 unfaithful=0/29700.
a4 (r91 both): `SUMMARY cases=22 tool_pass=16 before_pass=16`, `R93-FIXTURE-FAIL`, `EXIT=1`; KFF19 inexact=3096, KFF18 unfaithful=28.
a5 (r87 K4): `SUMMARY rows=12 mismatches=0 errors=0`, `EXIT=0`.

Note: probe/fixture `--work` requires a NON-EXISTENT path (script calls `os.makedirs(work)`); two first attempts failed with `FileExistsError` — receipts `a1/a2` record the successful reruns. All values above re-derived on committed bytes; no re-run discrepancy with the filed controls in `census/round-93/controls/`.

## 2. Pins (sha256, measured)

| path | sha256 | prereg says |
|------|--------|-------------|
| `tests/fixtures/r93-k4-flagfail.py` | `ed15094e9ff17c159df9dd04d3b4d3878b2a1f23ecdc6175dc1759d1146e7a6a` | `ed15094e…` ✓ |
| `census/round-93/c2-forgery-probe.py` | `f3c84c49ac32cef40c96b875cb604ce83d63f2046b6031d65983130238705272` | `f3c84c49…` ✓ |
| `tools/souji-record-agreement.py` | `fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75` | `fc0e35c2…` ✓ |
| `census/round-92/controls/c2-before-tool.py` | `21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c` | `21e5c740…` ✓ |
| `tests/fixtures/r92-k4-flagfail.py` | `2c9bd76c77c609bfaf2fd1a86a5bd022fc8549cd58bc2f198a029e3ea90feeae` | — (control fixture) |
| `census/round-92/c2-forgery-probe.py` | `9dac4cde51d1cee96ba479900fa221e29a4b0b3bc7386ca2a94dc094531ca690` | — |
| `census/round-87/c2-k4-counter.py` | `4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e` | — |

AST count of `CASES`: r93 = 22, r92 = 20 ✓.

## 3. Hunk inventory (saved as diffs)

- `diff-fixture-r92-r93.txt` (149 lines): r93 fixture adds — (a) docstring r93 paragraph (KFF19/KFF20 rationale, R92MutC2 C/D/E); (b) `"headill"` payload (E0 80 80 across head cut); (c) the whole KFF19 reference block (`_ref_len` lines 370–386, `_ref_straddle` 389–396, `ref_cuts` 399–406, `EXACT_TOKENS`/`exact_payloads`/`case_exact`, `case_headill`); (d) `("KFF19", …)` and `("KFF20", …)` CASES entries; (e) case-name list for KFF19/KFF20. Nothing else changed — the diff is purely additive plus the docstring/case-table spellings.
- `diff-probe-r92-r93.txt` (34 lines): r93 probe adds the `--fixture` parameterisation plus F5/F6/F7 entries (the three one-edit tuples from the probe table); F1–F4/N0 byte-identical.
- `diff-tool-before.txt` (79 lines): filed tool vs r91 tool — replaces the r91 lead-length helpers with `_straddling_sequence` (strict decode == 1 char) and rewires `_cut_head`/`_cut_tail`; confirms tool change is the r92 repair, unchanged in r93 (sha matches P1 pin).

## 4. Independence of the reference (AST + grep)

`tests/fixtures/r93-k4-flagfail.py` source segment for `_ref_len`, `_ref_straddle`, `ref_cuts`:

- Called names: only `len`, `range`, `max`, and `_ref_len`/`_ref_straddle` (mutual).
- Needle search in source segment: `.decode` NO, `codecs` NO, `str(` NO, `bytes(` NO, `chr(` NO, `import` NO, `encode(` NO.
- Otherwise the file uses `.decode`/`chr(` in git helpers and case code outside the reference block (saved in `independence-excerpt.txt`).

The reference is a hand-coded WHATWG Table 3-7 boundary table (need + first-continuation lo/hi per lead: C0/C1 excluded, E0 lo=0xA0, ED hi=0x9F, F0 lo=0x90, F4 hi=0x8F, F5+ absent). No codec call — independence claim holds.

## 5. Beyond the fixture sweep (random, 300,000 payloads)

Script saved in seat dir as `sweep.py`; output as `sweep-output.txt`. Alphabet (388 tokens): all 128 ASCII bytes; every Table 3-7 boundary encoding at low and high second byte (`C2 80…F4 8F BF BF`, 24 tokens); ill-formed classes (C0/C1 leads, E0 overlong, ED surrogate, F0 overlong, F4 >U+10FFFF, F5–F7 leads, 5/6-byte leads, FE/FF, bare continuations, truncations); 200 random 2–6-byte tokens. Payloads: lengths 201–400, concatenated tokens truncated to length, RNG seed 20261109, compared `_one_line_bytes(raw)` vs the reference-cut cell (`_escape_text(_decode_record(raw[:h]) + "…" + _decode_record(raw[t:]))` with `h,t = ref_cuts(raw)`).

Results (300,000 payloads):
- **Filed tool: disagreements = 0.** No payload hex to report — nothing falsifies exact-position agreement on this class.
- F5 (`surrogatepass`): **2159** disagreements / 300,000.
- F6 (`len >= 1`): **157,463** / 300,000.
- F7 (head cut forward): **20,065** / 300,000.

F5–F7 disagree with the exact-position reference on the random class in the same direction they disagree in the fixture (rejected by KFF19), at rates the 14,586-payload sweep also exposes. No filed-tool disagreement.

## FALSIFICATION / wording

**NO-FALSIFICATION.** Tried: all five predicate/control/regression runs (all match prereg numbers exactly); pin re-hash (all four prereg pins match); AST/grep independence check (passes — no codec); a 300,000-payload random differential vs the reference (0 filed-tool disagreements). Nothing in this wave's artifacts falsifies a sentence of the C2 claim as worded, including its stated limits (finite sweep, eight named forgeries, no hardcoding defence claimed).

Scratch `/fast/scratch/hyaku/souji-r93/R93ExecC2/` deleted after copying receipts (`sweep.py`, outputs). No files outside seat dir + this report were written. No tools installed (none needed).

Report: .ufo/waves/round-93/w1/R93ExecC2.md
