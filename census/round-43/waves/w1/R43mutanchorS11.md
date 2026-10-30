# R43mutanchorS11 — anchor-to-probe fidelity

Axes: anchor fidelity, observable discrimination, exact restoration, isolation.

Attack target: frozen C3 population row S11 (`total-junk`), not candidate fixture completeness. Instrument revision: `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373`; pinned tool revision: `619a75034dd6324e1a725f73034c59f7bf9558ef`.

| mutant | anchor count | pristine rc+token | mutant rc+token | flip holds (yes/no) | defect text if no |
|---|---:|---|---|---|---|
| S11: remove `$` from TOTAL regex | 1 | 2; stderr `REFUSAL RECORD-MALFORMED: line 2 does not match the census schema` | 0; stdout `SUMMARY … drift_rows=0 unreachable=0`; stderr empty | yes | none |

Verdict: **killed by the bounded behavioral detector; population description holds**. Removing the end anchor lets `TOTAL.match` accept the valid numeric prefix before `JUNK`. The unchanged TOTAL arithmetic then agrees with the single repository. This probe found no S11 population defect; it does not establish whether any candidate battery kills S11.

## Exact reproduction and observations

Run from this seat's directory:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43mutanchorS11/probe.py
```

Observed command exit: 0. The retained reproducer contains the full setup, extraction, mutation, detector and restoration commands; the retained receipt records **every subprocess argv, rc, stdout and stderr**, including read-only `git show` invocations, `git -C <fixture> init -q`, the successful fixture-top-level assertion, and the identical three tool invocations. No fixture commit was needed.

- Reproducer: `.ufo/waves/round-43/w1/R43mutanchorS11/probe.py`
- Actual output receipt: `.ufo/waves/round-43/w1/R43mutanchorS11/receipt.json`

Scenario: one initialized Git repository named `r`, explicitly bounded root, `--skip-unrecorded`, `--timeout 5`, explicit `TMPDIR`, subprocess deadline 30 seconds. Record bytes:

```text
REPO\tr\tregs=1\tprunable=0\n
TOTAL\trepos=1\tregs=1\tprunable=0JUNK\n
```

Here `\t` and `\n` denote actual tab and newline bytes. Detector expects rc 2 and stderr containing `REFUSAL RECORD-MALFORMED:`. Pristine passed; mutant failed by accepting the record with rc 0 and zero drift; restored passed with the identical pristine refusal. Both refusal runs had empty stdout. The mutant had empty stderr.

## Hashes and restoration

- Old anchor SHA-256: `46fb33c9ee47d87d8ed047be024b3cb830952224b2632a02778125fcd998ee3a`
- Replacement SHA-256: `016ae3828e6b2a44163e7fc0d16c112f40cd5559f87282c1041df1d53e4259b7`
- Pristine full tool: `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`
- Mutated full tool: `2fbfdc90735eb4fee0bb2285fad6889f2d5eb2405e4d40356552292eb036fdc8`
- Restored full tool: `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`

Observed `restored_exact=true` and `scratch_removed=true`; restoration and cleanup execute in `finally` blocks. No tracked lane file was modified; no tools installed. Scratch follows the wave-wide explicitly named fast-scratch root; only retained evidence resides in the seat.

Self-assessment: accuracy 5 (captured triplet), completeness 5 (row, anchors, behavior, restoration), clarity 4 (full command streams live in linked receipt), actionability 5 (retained executable reproducer), conciseness 4 (hashes and reproduction details retained for audit); overall 4.6/5. The receipt is authoritative for complete stdout rather than the shortened table token.
