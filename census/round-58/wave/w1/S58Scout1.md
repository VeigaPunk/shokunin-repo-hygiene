# S58Scout1 — round-58 C1 prereg/counter verification and C2 receipt inventory (read-only recon)

Date 2026-11-04. Leaf scout; no edits to production, fleet, or siblings. All repo reads revision-scoped or sha-verified against the frozen commit; no git/jj mutation anywhere (scratch needed no fixtures); no installs (nothing was needed — tooling record: none, pacman untouched).

## 1. Preregistration and freeze verified

- Preregistration: `census/round-58/preregistration.txt` (read in full; line 5 raw). Base declared `83d3813257648e99fb4ab2ddef217124f39cf324`; frozen predicate commit `e7f64f30324e8ddb3f2266302daa9066054cdbb3`.
- `git log` at the frozen commit: `e7f64f30 round-58: freeze bounded fresh-start claims and calibration control`, parent exactly `83d38132` = the declared base. `e7f64f30` is an ancestor of current HEAD.
- Byte-identity (sha256, prefix-16) between the `e7f64f30` blobs and the worktree — all identical: `census/round-58/c1-counter.py` (52ccdb1be66dd837), `census/round-58/c1-before.txt` (083f6784f0f52823), `census/round-58/preregistration.txt` (f40bcff3850d7a45), `census/round-58/sources-before.txt` (b516cfe0e2159831), `census/round-57/manifests/after.tsv` (208091cb2bf7e608), `after-pre.tsv` (ac6c27a476c589d3), `census/round-57/records/c1-matrix-v5.tsv` (4cce7f59d97b453d), `c1-matrix-v6.tsv` (27b8e7a2412d88a6), `census/round-57/c2-counter.py` (174d7b8a3c105875). Full digests in `SHA256SUMS` (evidence dir).
- Fleet-root working tree is dirty (`M LOG.md`, `M SCORECARD.md`) and HEAD has moved to `dccdc469f4c2e0415e1a1dcc317364e1b4d3191e` ("round-58: correct two r57 self-assessment discrepancies without grammar cutover", +6 LOG / +7 SCORECARD lines over the freeze). None of my measurements touch the worktree; they run at explicit revs.

## 2. Frozen C1 counter and control verified

Counter `census/round-58/c1-counter.py` (frozen bytes): revision-scoped; reads the two committed matrices at `--rev`, computes `carry_identical` as pairwise `exit`+`findings_all` equality (zip), `exit_zero` per matrix from positional column 5, and asserts the two `R58-CALIBRATION` correction notes are present in `SCORECARD.md` at the same rev. Exit 1 iff a note is missing.

Run receipts (command + output + EXIT preserved verbatim in the evidence dir):

| rev | result | EXIT |
|---|---|---|
| `83d3813…` (base) | both notes MISSING; `SUMMARY assertions=2 mismatches=2 carry_identical=34 exit_zero=10,8` | 1 |
| `e7f64f30…` (freeze) | same as base | 1 |
| `dccdc469…` (HEAD, L1 integration) | both notes MATCH; `SUMMARY assertions=2 mismatches=0 carry_identical=34 exit_zero=10,8` | 0 |

- Base run is byte-identical to the frozen `census/round-58/c1-before.txt` ("observed c1-before" control reproduced on this host); the only diff line is the COMMAND prefix my harness prepends (`compare-c1-before.diff`, diff EXIT=1 with that sole difference).
- Control validity: the before arm does NOT reach target at base or at freeze (mismatches=2) — the prereg kill condition ("a control reaching target invalidates its claim") is not tripped as of the freeze.
- Observed at HEAD only (not my score): the landed correction commit reaches the frozen target `mismatches=0 carry_identical=34 exit_zero=10,8` EXIT=0. Scoring/adjudication belongs to L1.

## 3. Independent r57 enumeration (own parser, not the counter's code path)

Parsed the dumped base-rev matrices (`matrix-v5.base.tsv`, `matrix-v6.base.tsv` in the evidence dir; parser `enumerate.py`, receipt `enumeration.out`):

- Rows: v5 = 36 data rows, v6 = 36 (37 lines each incl. header). 8 columns both, header `fixture,counter,rev,base,exit,finding,findings_all,SUMMARY`.
- `exit=='0'`: v5 = 10, v6 = 8 — positional index 4 and named column `exit` agree, so the counter's positional method is sound on these bytes.
- Combined (the r57 two-file awk shape) = 18.
- Pairwise carry-identical (exit + findings_all, zip) = 34 of 36. Full-row identical = 0 (expected: `counter`/`rev`/`base` columns differ per arm).
- The exactly-2 differing pairs, named: `B4-INLINE-NBSP-OPENER` and `C4-INLINE-CLOSED-COMMENT` — v5 exit=0 (`-`) → v6 exit=1 `CORRECTION-IN-FENCE,CORRECTION-IN-FENCE` (`fenced=2` in their SUMMARY columns). This is precisely the r57 C1 v6-refuses-hidden-filings story.

Both prereg discrepancies are grounded in base SCORECARD.md@`83d3813` line 1432 (excerpt receipt `scorecard-base-line1432.txt`): the cell claims "all 33 carry-over rows identical in exit and full finding list" (measured: 34) and shows the two-file awk command annotated "(10, 8)" — that command prints one combined END total (18), not the pair. `R58-CALIBRATION` appears nowhere in base SCORECARD (grep: no matches), confirming both notes were absent at base and the freeze.

## 4. After-manifest three receipt paths (C2 inventory only — not scored)

`census/round-57/manifests/after.tsv` (header `receipt<TAB>instrument`), exactly three rows:

1. `census/round-57/records/c1-tip.txt` ← `census/round-57/c1-counter.py`
2. `census/round-57/records/c2-tip.txt` ← `census/round-57/c2-counter.py`
3. `census/round-57/records/standing.txt` ← `census/round-46/c1-counter.py`

Each receipt: regular file (not a symlink, `ls -l` type `-rw-r--r--`), present at both `83d3813` and `e7f64f30` (`git cat-file -e`), and carries a full-40 `rev=`, an `instrument_sha256=`, and `EXIT=0`:

- `c1-tip.txt`: `rev=d749f7ee081ec1b382b2f92577eb22bfba1c7761`, `SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 … recomputed=79`
- `c2-tip.txt`: `rev=44a983a3e72923d8e809100763a9fcd8c458a244`, `SUMMARY receipts=2 findings=0`
- `standing.txt`: `rev=44a983a3e72923d8e809100763a9fcd8c458a244`, `SUMMARY assertions=627 mismatches=76 registered=76 corrected=0 exempted=0 unfiled=0`

The mismatches=76 / receipts=2 values are the receipts' own recorded content, quoted as observed; I ran no C2 gate. The two-receipt pre-arm `census/round-57/manifests/after-pre.tsv` holds rows 1 and 3 only (c1-tip, standing), matching the r57 two-receipt/three-receipt manifest history in LOG.

## 5. Limitations and unrun legs (honest)

- C2 NOT scored: no gate run, no before-arm re-measurement of `census/round-57/c2-counter.py` (deferred until executor02 delivers acceptance, per instruction). Only the three receipt paths' existence/type/shape were enumerated.
- The v5/v6 pairwise alignment follows DictReader row order (the counter's own predicate); I named the 2 differing fixtures but did not independently cross-check fixture-name equality across all 36 pairs (spot-checked tail rows only).
- SCORECARD line 1432 numbering is base-rev-scoped (`83d3813`); the dirty worktree and `dccdc469` shift lines, and the counter matches text, not line numbers.
- `sources-before.txt` read but its duplicate-url listing not re-derived (out of scope).
- HEAD moved during recon (freeze → `dccdc469`); the HEAD reading is a point-in-time observation and may be stale by the time this is read.

## Evidence index

All under `.ufo/waves/round-58/w1/S58Scout1/` (digests in `SHA256SUMS`): `c1-at-base.out`, `c1-at-freeze.out`, `c1-at-HEAD.out` (frozen-counter receipts with COMMAND/EXIT), `enumeration.out` + `enumerate.py` (independent enumeration), `matrix-v5.base.tsv`, `matrix-v6.base.tsv` (base-rev dumps), `scorecard-base-line1432.txt` (superseded-claims excerpt), `compare-c1-before.diff` (control reproduction), `dump-provenance.txt`. Scratch `/fast/scratch/hyaku/souji-r58/S58Scout1/` removed after copying.
