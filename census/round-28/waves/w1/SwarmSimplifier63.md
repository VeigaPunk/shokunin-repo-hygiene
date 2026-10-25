# SwarmSimplifier63 — dead-reference scan, round 28 wave 1 (godspeed)

## Status
STATUS: PASS — scan complete; table delivered; no deletions performed (read-only seat). Measured at lane HEAD `0c96332932e66bbaf9cf1c246091d3275a0ab612` (frozen prereg base `3a2a80d0d18940a5e352ebc526da22a57dad83c4`), worktree dirty (32 porcelain lines) and being mutated concurrently by C3 seats during the scan.

## Evidence
- Corpus: `SKILL.md`, `SCORECARD.md`, `corpus/knowledge/**`, reports = `census/**` (round records, verification JSONs, matrices, wave manifests at scan time). Match rule: whole-token regex per basename, then stem, then family stem (`.impl-N`/`.r9-s18` stripped), boundary-guarded `(?<![A-Za-z0-9_])...(?![A-Za-z0-9_])`; identical analysis re-run twice (record-only corpus then full-census corpus) for consistency.
- Inventory at scan time: `tools/` top level 137 files; `tests/fixtures/` top level 42 files; 49 nested fixture data files (`case-F1..F10`, `r13-cert-frozen`, `r14-cache-frozen`, `r15-preservation-frozen`).
- Required-corpus zero-hit set (exactly these 4, all fixtures): `q54-mutant-entry.md`, `r25-q57-check.sh`, `r25-receipt-stderr.py`, `r25-slice-mapping.py`.
- Elsewhere-cited proof: `corpus/QUALITY.md:128` verbatim: "the committed mutant `tests/fixtures/q54-mutant-entry.md` must exit nonzero"; `corpus/lessons/round-25.md:44` verbatim: "The bounded Q57 checks are `tests/fixtures/r25-slice-mapping.py` and `tests/fixtures/r25-q57-check.sh`"; `corpus/lessons/round-25.md:77` verbatim: "`python3 -B tests/fixtures/r25-receipt-stderr.py --root . --rev 728b2ce...`".
- Table row counts (full-census corpus): every one of the 137 tool scripts has ≥1 cite (cand-,impl-,r9-s18 variants via `census/round-10/round-11` certification JSONs, e.g. `cand-census-01.sh` r=18, `impl-21.sh` r=115, `souji-round9-selftest.sh` r=713); 38/42 fixtures have ≥1 cite in required corpora; 0 tools uncited.

| candidate class | never cited in SKILL+SCORECARD+knowledge+reports | cited only outside those corpora | verdict |
|---|---|---|---|
| `tools/` scripts (137) | 0 | 0 | all cited; no removal candidate |
| `tests/fixtures/` scripts (42) | 4: q54-mutant-entry.md, r25-q57-check.sh, r25-receipt-stderr.py, r25-slice-mapping.py | 0 | cited in QUALITY/LOG/lessons; Q54/Q57 instrument references; not removal candidates |
| nested fixture data (49) | 0 (≥1 token hit: `census` reports) | — | generic-name matches (`expected.json` etc.) are [INFERENCE] incidental tokens, not per-file citations; frozen dirs are pinned in SKILL rows |
| `tools/__pycache__` | — | — | EXISTS: souji-axis-check/gate-check/landing-gate cpython-314 pyc |
| `tests/fixtures/__pycache__` | — | — | EXISTS: r26-axis-check.cpython-314.pyc |

## Findings
1. No script-level tool is citationless: 0/137 removal candidates from the tool set; the 61 `cand-*`/`impl-*`/`r9-s18` lineage variants are cited only in historical certification reports and stay load-bearing as recorded bytes (`git ls-files` confirms they are tracked).
2. The only required-corpus-uncited items are 4 fixtures, each still referenced by authority/lesson files (locations above) — removing any of them would break the Q54/Q57 check cells (QUALITY.md:128,141) that name them; they are low-citation, not dead.
3. Internal cross-refs keep some uncited-looking files reachable as build inputs: `cand-g1-vault.sh` ← `cand-g1-build.sh`; `souji-round9-selftest.sh` ← cand-a1/a2/b1/b2 quarantine/vault/verify suites; `souji-guard.r9-s18.sh` ← the three r9-s18 variants.
4. Runtime residue present at both asked locations: `tools/__pycache__/` (3 pyc, untracked, covered by the `__pycache__/` rule in the new worktree `.gitignore`) and `tests/fixtures/__pycache__/` (1 pyc: `r26-axis-check.cpython-314.pyc` — evidence r26-axis-check.py executed). Additional lane-wide residue: **tracked** `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (gitignore cannot untrack it) and leftover copies inside `.ufo/waves/round-26/assimilation/validate/{tools,tests/fixtures}/__pycache__` and `census/round-26/waves/assimilation/validate/` (C3 capture surface).
5. Snapshot caveat: the corpus mutated during the scan (new C3 files `tools/souji-wave-evidence-capture.sh` and `tests/fixtures/r28-wave-evidence-capture.sh` appeared; `census/round-26/waves/` receipts landed), so exact counts are wave-point-in-time; the qualitative result (no uncited scripts) held across both scan passes.

## Attack log
None — no counter/predicate/target disputes from this seat.

Report: .ufo/waves/round-28/w1/SwarmSimplifier63.md
