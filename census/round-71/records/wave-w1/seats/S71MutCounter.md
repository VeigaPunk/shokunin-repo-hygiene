# S71MutCounter — round 71 / wave 1: mutation probe of the r71 counter's own self-check

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin (read-only). Scratch: /fast/scratch/hyaku/souji-r71/S71MutCounter (removed at exit).
Target: census/round-71/c1-counter.py, sha256 7e5a694a6aafa436383321e6be363482cbf255b1785c26fa825405592f62a3cc (102979 B).
Mission: falsify the C2 self-check beyond the frozen X6-X10 and carried CM1-CM4, by mutating the r71 additions.

## Baseline control (pristine bytes, same detector)
- selftest: `SELFTEST cases=39 pass=39 fail=0` / `EXIT=0` (29.7 s) — matches preregistration disclosure (i).
- C1 arm: `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0`.
- Per-row CASE lines for AS1 AS2 FC1 FC2 FC3 FM1 FM2 are byte-identical to census/round-71/records/c1-after.txt. Baseline is green, so every killed mutant below is a real kill.

## Commands (from /home/vgpnk/Projects/shokunin/souji-shokunin)
    python3 -B <MUTANT> --selftest --root <LANE> --matrix census/round-71/c1-matrix.tsv \
        --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --work <SCRATCH>/w/st-<id>
    python3 -B <MUTANT> --root <LANE> --matrix census/round-71/c1-matrix.tsv \
        --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 \
        --rev a1db6c8514771c0a0321c29741831606d09cc2a5 --tool tools/souji-receipt-write.py \
        --work <SCRATCH>/w/c1-<id>
Each mutant is one exact single-occurrence string edit (count asserted == 1 before writing); full table in results.tsv.

## Mutant table (killed iff EXIT != 0)
| id | edit | selftest | C1 arm | verdict |
|----|------|----------|--------|---------|
| Y1 | MEMBER_RE accepts `/`: `[A-Za-z0-9/_-]` | 39/39 EXIT=0 | SUMMARY == frozen (base_forgeries=7) EXIT=0 | **SURVIVED (both)** |
| Y2 | drop SHA256SUMS non-plain-name check | 38/39 EXIT=1 (`a SHA256SUMS line naming a non-plain file is refused`) | not run | killed (selftest) |
| Y3 | drop symlinked-member check | 38/39 EXIT=1 (`a symlinked member is refused`) | not run | killed (selftest) |
| Y4 | `_row_env`: attr-source-filter never sets GIT_ATTR_SOURCE | 39/39 EXIT=0 | base_forgeries=5, new_* frozen, class_mismatches=0, EXIT=0 | survived the EXIT verdict; SUMMARY differs (base_forgeries) |
| Y5 | mutate(): committed-filter skips `filter.t.clean` | 39/39 EXIT=0 | class_mismatches=2 EXIT=1 (FC1 FC2 refuse with findings `-`) | killed by C1 arm only |
| Y6 | FORGED_SAMESIZE size-changing (`counter FORGED`) | 39/39 EXIT=0 | base_forgeries=2, new_* frozen, class_mismatches=0, EXIT=0 | survived the EXIT verdict; SUMMARY differs (base_forgeries) |
| Y7 | local-filemode skips chmod_notes | 39/39 EXIT=0 | new_forgeries=1 class_mismatches=1 EXIT=1 (FM1 new=accept) | killed by C1 arm only |
| Y8 | edit-counter-samesize writes committed bytes | 39/39 EXIT=0 | new_forgeries=1 class_mismatches=1 EXIT=1 (AS2 new=accept) | killed by C1 arm only |
| Y9 | non-plain check drops only the `startswith('.')` half | 39/39 EXIT=0 | SUMMARY == frozen EXIT=0 | **SURVIVED (both)** |
| Y10 | FILTER_CLEAN no longer reverses the forgery (`s/v2/v9/`) | 39/39 EXIT=0 | base_forgeries=2, new_* frozen, class_mismatches=0, EXIT=0 | survived the EXIT verdict; SUMMARY differs (base_forgeries) |

## Findings
- **F1 HIGH — claim_upheld never reads the base slot.** base_forgeries/base_honest are printed but not in the verdict (c1-counter.py:1164-1168). Y6 and Y10 turn every filter fixture into a non-forgery (base AS1/AS2/FC1/FC2/FC3 all `base=refuse`, base_forgeries 7->2) yet EXIT stays 0 with all new-slot counts frozen; Y4 does the same for the AS route (7->5). The r71 C1 verdict therefore cannot tell "the new rows measure a forgeable filter route" from "the new rows cannot forge at all". Only the frozen SUMMARY text (base_forgeries=7) catches F1's mutants — the counter's own claim_upheld blesses them.
- **F2 HIGH — AS1/AS2 have no new-slot discriminating power for the GIT_ATTR_SOURCE route.** Their expected classes are exactly what an unfiltered dirty tree yields: AS1 `lane worktree is dirty` (observed, records/c1-after.txt), AS2 `RECEIPT-STATE-CHANGED-DURING-RUN`. Y4 removes GIT_ATTR_SOURCE entirely and the new slot still prints new_forgeries=0, class_mismatches=0. The route is witnessed only by the base slot (F1), which the verdict ignores.
- **F3 MEDIUM — the selftest pins none of the r71 fixture-shaping constants.** No section-(8) check asserts `len(FORGED_SAMESIZE)==len(SEED_COUNTER)` (both 11 B), that FILTER_CLEAN maps v2->v1, that FM1 chmods, or that edit-counter-samesize edits. Y5/Y7/Y8 are killed only by a full 70-row C1 run; Y6/Y10 not at all by EXIT.
- **F4 MEDIUM — the r71 member-name hardening (S70Sentinel F3/F4) is half-unpinned.** Each clause of `MEMBER_RE` and of the non-plain-line test is exercised by exactly one selftest input that violates BOTH clauses (`../M1`, `../M1.py`). In-process probe: Y9 returns OK for a SHA256SUMS line `.hidden.py` (dot-only) that pristine refuses (`SHA256SUMS line 2 names a non-plain file`); Y1 lets the name `sub/M1` past the name rule (refused later only as `not listed`). Both mutants are green under selftest and C1.
- **F5 LOW — seven dead CLASS_* constants** (CLASS_STATE, CLASS_FLAG, CLASS_ENV, CLASS_DIRTY, CLASS_ENVCFG, CLASS_ENVRED, CLASS_CD, incl. the r71 CLASS_FILTER) are defined and never referenced (c1-counter.py:184-190 and :209); expected classes come only from the matrix, so editing a constant is undetectable by construction.

## Item 4 — X6-X10 match check
Each `old` string occurs exactly once in census/round-71/c1-counter.py (X6..X10: 1,1,1,1,1). Applying each edit to census/round-70/c1-counter.py reproduces census/round-70/records/wave-w1/seats/S70MutCounter/mutants/X{6,7,8,9,10}.py byte for byte (5/5 True) — the preregistration's reproduction claim holds.

## Files written (under /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-71/w1/)
- S71MutCounter.md (this report)
- S71MutCounter/results.tsv, S71MutCounter/mutants.json
- S71MutCounter/mutants/Y1.py .. Y10.py
- S71MutCounter/logs/{base.txt,st-Y1..Y10.txt,c1-base.txt,c1-Y1,c1-Y4..Y10}.txt
No lane tracked file was modified; no git/jj mutation; no tool installed this seat.
