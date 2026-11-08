# S88Reviewer — Independent re-derivation (round 88)

## 1. Per-end re-derivation table (own scratch at `/fast/scratch/hyaku/souji-r88/S88Reviewer`, now removed)

| End | Command (run from lane root, `--work` under scratch) | Observed SUMMARY | Exit | Verdict |
|---|---|---|---|---|
| C1 after | `python3 -B census/round-88/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work $S/c1after2 --only r87,r88 --expect-killed 22` | `SUMMARY mutants=12 sets=r87,r88 pristine_r87=ok pristine_r88=ok killed_r87=10 killed_r88=12 killed_total=22`; `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`, `pop=r88 rows=53 mismatches=0 errors=0 exit=0`; 12/12 MUTANT-PAIR killed=yes | 0 | AGREE |
| C1 before | same, `--only r87 --expect-killed 10` | `SUMMARY mutants=12 sets=r87 pristine_r87=ok killed_r87=10 killed_total=10`; survivors `m17-duplicate-id killed=no`, `m18-whole-before killed=no` | 0 | AGREE |
| C1 belt | same after command, `--mutants census/round-88/c1-mutants-dead.json --expect-killed 22` | `SUMMARY mutants=13 sets=r87,r88 pristine_r87=ok pristine_r88=ok killed_r87=10 killed_r88=12 killed_total=22`; `m19-len-half killed=no` on both sets | 0 | AGREE |
| C2 after | `python3 -B tests/fixtures/r88-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-88/controls/c2-before-tool.py --work $S/c2after` | 7 CASE lines all `tool=pass`; `SUMMARY cases=7 tool_pass=7 before_pass=3` | 0 | AGREE |
| C2 before | same fixture, r87 tool as both `--tool` and `--before` | KFF2–KFF5 `tool=fail`; `SUMMARY cases=7 tool_pass=3 before_pass=3`; `R88-FIXTURE-FAIL` | 1 | AGREE |

The filed after-receipts at tip (`census/round-88/records/c1-after.txt`, `c1-dead-belt.txt`, `c2-after.txt`) carry the identical SUMMARY lines. Nothing in the reruns contradicts C1 or C2 stated wording.

## 2. Chronology

Branch log (`git log` on `refs/heads/master`): P `e60ea25f` (07:39:24 -0300, instruments + controls + before receipts) → F `f74092b2` (08:02:50 -0300, prereg alone) → `ce29e5bc` (wave spec) → `01a2fa55` (C2 repair + after receipts) → `486826df` (C1 after/belt receipts). P and F both precede every after receipt's commit. F's file set is exactly one file (`census/round-88/preregistration.txt`).

P's 18-file list contains one name carrying "after": `census/round-88/records/sources-census-after.txt` — a sources-registry snapshot whose header reads `# AFTER state: the lane working tree at round 88` (90 lines, differs from the base-reconstructed `sources-census-before.txt`). It is census evidence, not a claim-measurement receipt; it is not filed as an after run of C1 or C2. **No pre-freeze after run filed as evidence — none found.** (Disclose only, per spec.)

Note: P landed after the lane base `7defe9c5` (07:22:13) but before F — consistent with the prereg §1 statement that F lands alone while P holds instruments/controls/before receipts.

## 3. Instrument binding — hash table (measured at tip, sha256sum)

| File | Expected | Measured | Verdict |
|---|---|---|---|
| `census/round-88/c1-false-rows.tsv` (53) | `b710e368…88a68c3` | `b710e368…88a68c3` | AGREE |
| `census/round-88/c1-mutants.json` (12) | `baec8026…bc66cec9c` | same | AGREE |
| `census/round-88/c1-mutants-dead.json` (13) | `e7963787…160fa46e0525b015281` | same | AGREE |
| `census/round-88/c1-false-row-harness.py` | `1ae0cd39…72814042b` | same | AGREE |
| `census/round-88/c1-clause-battery.py` | `6842ca47…a2c5ff7` | same | AGREE |
| `census/round-87/c1-pointer-counter.py` | `fd0a8e24…f74a755220b` | same | AGREE |
| `census/round-87/c1-items.tsv` | `ce80195d…c455178d2e9` | same | AGREE |
| `tests/fixtures/r88-k4-flagfail.py` | `aa79133a…43e8335d` | same | AGREE |
| `tools/souji-record-agreement.py` | `c0604b4a…73e4fdef` | same | AGREE |
| `census/round-88/controls/c2-before-tool.py` | `e1b00e8a…c8ac67ccc` | same | AGREE |
| `census/round-88/controls/c2-before.txt` | `28e5ad68…37c8133dc2` | same | AGREE |
| `census/round-88/controls/c1-before.txt` | `ce1352d2…c7f` | same | AGREE |

Also pinned in prereg prose: r87 population `census/round-87/c1-false-rows.tsv` = `b066fa0f…69220` (measured AGREE), matching the battery's own `# population r87 … rows=51` header.

The prereg names more instruments than the hash list — that gap is inside the prereg text itself (it hashes the four core items inline: both populations, items, before-tool; the battery/harness/mutants/fixture bytes are pinned by the battery's own printed `# counter/harness/mutants path=… sha256=…` headers and by P-era receipt headers, all reproduced in the reruns above). Every file the prereg names exists at the stated path; no hash mismatch anywhere.

## 4. Do-nothing control checks

- **C1:** filed `controls/c1-before.txt` matches my before-rerun byte-for-output: 10 killed, exactly m17/m18 surviving. 10 < 22 strictly. The two r87-carried clauses (m17 duplicate-id, m18 whole-before) are the only survivors on r87 and are both killed on r88 (`m18-whole-before pop=r88 killed=yes mismatches=1`; m17 likewise per the 12/12 pair count). AGREE.
- **C2:** r87 tool passes exactly KFF1/KFC1/KFC2 and fails KFF2/KFF3/KFF4/KFF5, before_pass=3 < 7. AGREE.

## 5. Round-87 debts D4/D6 disposition (not absorbed)

- **D4** (CRITICAL routed defect from the r87 spot-check: a rejected Gate row not written). The rejected candidate is now written as row **S350** (git-config `core.quotePath`, REJECTED with flip) in `corpus/SOURCES.md`, landed in P `e60ea25f`. Disposition: resolved on committed bytes. I reran neither spot-check procedure; I read the row text only.
- **D6** (precision nit: S346 quote at roff 698 is the Porcelain v1 alternate-`-z` paragraph, not the OPTIONS `-z` entry at roff 211–217). S346's teaches cell now names both: "the OPTIONS `-z` entry at roff 211-217 states the NUL termination, and the roff 698 paragraph inside `Porcelain Format Version 1` states the no-quoting rule." Disposition: resolved in wording; the quote itself is unchanged and byte-exact per the spot-check.

## 6. Findings and residual risk

**No finding against the stated wording of C1 or C2 in this reviewer's scope.** Observations (not claims):

1. `sources-census-after.txt` landing inside P (pre-freeze) is a naming trap for future readers; functionally it records working-tree state, not a measurement. Recommend the integrators rename or note it; not a kill-rule item.
2. The prereg's stated "Measured at print time" hashes are inline prose, while `eval` tooling byte-compares via the battery's printed sha headers — self-consistent here, but the battery could also pin mutants/fixture shas cryptographically. Minor.
3. C1 battery wall-clock is minutes (the first attempt hit the 300s runner default); before-rerun scripts should raise the deadline — operator nit, not a claim issue.

Residual risk: **LOW for C1/C2 stated wording.** This seat re-derived all five ends on committed bytes; every number, survivor set, and hash reproduces. I did not audit the harness's judgement code line-by-line (mutant `old` text occurrence etc. — battery EXIT 2 would have tripped and did not). D4/D6 accepted as dispositioned per seat scope, not re-litigated.

## Verification gaps
- lsp tooling was not invoked: the seat brief requires sparing lsp only as an escalation tool; all checks here are byte/CLI/JSON verifications whose evidence does not depend on language-server semantics, so no grep-instead-of-semantics risk arises.
- Scratch was removed after receipt capture (`/fast/scratch/hyaku/souji-r88/S88Reviewer` deleted); rerun logs were captured to that dir and are summarized above, not preserved as files. Nothing in the lane writes beyond this report.

*(Scratch left behind: none.)*
