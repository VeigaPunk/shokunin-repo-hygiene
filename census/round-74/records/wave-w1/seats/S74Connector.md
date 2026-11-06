# S74Connector — cross-claim & sibling-overlap scan (r74) — read-only

Verdict: C1/C2 are **SEPARABLE** at receipt level; one shared held-constant input (writer 70bbf1c2…) and one common-mode predicate risk. 3 lane tool families still certify bytes from the index stat cache; 2 sibling gate families do.

## 1 Causal separation — SEPARABLE
Commands: `grep -nE '^# (command|bind|gate|slot)'` over records/c1-after.txt, controls/c1-K-*.txt, records/c2-after-*.txt, controls/c2-before-*.txt; `git show <rev>:tools/souji-receipt-write.py|sha256sum`; `sha256sum` on gate/counter/variants.
- C1 read set (c1-after.txt:3-7): c1-gate-counter.py ac28f7d1, gate 3162de98, writer 70bbf1c2. `grep -l c1-counter.py` over all 4 C1 receipts → NONE.
- C2 read set (c2-after-D6.txt:3-11): c1-counter.py e3fc47c2, defang 06ae459e, matrix f2ced976, base slot 118597e0, new slot 70bbf1c2. `grep -l pre-report-gate` over all 18 C2 receipts → NONE.
- Named coupling: both arms read tools/souji-receipt-write.py at the same sha — C1 imports `_truth_refusal` (tools/souji-pre-report-gate.sh:42-54), C2 uses it as its `new` slot. **Input held constant** (sha-bound in both receipts, no writer byte change this round), not a coupling of the claims. Residual: C1 certifies a predicate it does not own; GF1-GF3 are the only evidence `_truth_refusal` is correct and C2 asserts the counter's witness, not the predicate → a predicate defect outside GF1-GF3 leaves both arms green. [MEDIUM]
- Reproduced from committed bytes: `SUMMARY rows=9 mismatches=0 errors=0`/`EXIT=0` (c1-after); K-a/K-b/K-c = 3/4/1 mismatches, EXIT=1; D6/D7/D8 `base_forgeries=14 … base_unwitnessed=1`, edited rows FWw/FC1/FC2 `base_witness=no`; D1..D5 5×`base_unwitnessed=1`; pristine `base_forgeries=15 base_unwitnessed=0` EXIT=0; M08/M14/M15/M17 fail=1/1/2/1 EXIT=1; r74 selftest `cases=62 pass=62 fail=0`.
- Evidence gaps: C1(iii) records/c1-domain-trial.txt absent at 8fe48c86 [INFO]; C2 edit/survivor receipts never bind census/round-73/apply-edit.py — mutant bytes pinned only by `APPLIED out_sha256` [LOW]; C1 row match `ok = clean == expect and rc == want_rc` (c1-gate-counter.py:230) does not bind the refusal class [LOW].

## 2 Lane tools still accepting the index stat cache as byte proof (empty status or empty stat-trusting diff)
| tool:line | what empty status buys | vulnerable | stage-W pattern |
|---|---|---|---|
| tools/souji-pre-report-gate.sh:43-56 | base: clean PASS; W: re-hash | base YES / W no | applied (reference) |
| tools/souji-verify.sh:377,421,713 (+696-708) | clean→NOT-SAFE; pushed needs fresh-index diff | no | n/a |
| tools/souji-vault-verify.sh:550,594,908,1085 (+899) | same | no | n/a |
| tools/souji-quarantine.sh:1037,1198 (+992) | same | no | n/a |
| tools/cand-merge-verify.sh:322,366,658,820 (+649) | same | no | n/a |
| tools/cand-{a1,a2,b1,b2,c1,c2,e1,e2,f1,f2,g1,g2}-verify.sh (e.g. cand-a1:264-290, cand-g2:219-245; cand-d1:232-290 adds index-flag closure) | SAFE(pushed) from ancestry only, no worktree content compare | content-deaf, not status-class | use s18_snapshot_equal |
| tools/souji-guard.r9-s18.sh:153,175 | `git diff --quiet <ref> -- <tgt>` trusts the repo index → forged stat hides | **YES** | applies as-is (bash + writer beside) |
| tools/souji-record-agreement.py:351-366 | K4 pass = no status path | **YES** | import applies, but `_truth_refusal` is repo-aggregate, not per-path; K4 exemptions need a per-path API → not as-is |
| tools/souji-idx-repair.py:146,408-418 | clean-noop exit 0 | **YES** | same per-path API need |
| tools/{souji,cand-*}-census*.sh:133-142 (count_dirty) | `dirty=0` field | measurement only | applies, changes output contract |
| tools/souji-receipt-write.py:603-610,735 | refuses on status + `_truth_refusal` | no (this is the fix) | n/a |

## 3 Sibling overlap (read-only, /home/vgpnk/Projects/shokunin)
| lane | file:line | check | vulnerable |
|---|---|---|---|
| souji | tools/souji-pre-report-gate.sh:43 | pre-report check 4 | base YES → W fixed |
| kama | tools/pre-report-gate.py:668-681 (arm 6) | `git status --porcelain -uall -- .ufo/waves/round-N`; wave files are tracked | **YES** |
| kama | tools/round67-worktree-landing-check.py:88-114 | `read_bytes() == git show HEAD:rel` | no |
| kama | tools/report-landing-audit.py | errata/doc only, no status | no |
| mado | quality/landing-counters.sh:271-272 | citecheck dirty guard | **YES** |
| fleet | scripts/hyaku/inline.sh:157 | report-committed sweep (auto-commits) | LOW |
| kotoba, tsukuroi, kengaku, mori, kotodama, chousa, kagi, tameshi | gate-named files carry no `status --porcelain` | — | no |

Findings: MEDIUM ×3 (shared `_truth_refusal` common-mode; souji-guard.r9-s18:175; kama arm 6). LOW ×4 (apply-edit unbound; row class unbound; census `dirty` status-derived; inline sweep). INFO ×2 (domain-trial receipt absent; gate check-4 cost 4.98 s warm / 19,144 files / 306.8 MB, `_truth_refusal` returned None at scan start — lane clean then; stage-B edits appeared during the scan, not mine).
Files written: .ufo/waves/round-74/w1/S74Connector.md only; no scratch retained.
