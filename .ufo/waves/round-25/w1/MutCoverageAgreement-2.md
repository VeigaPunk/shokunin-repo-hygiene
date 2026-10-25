# MutCoverageAgreement-2 (mutation-tester, wave 1) — coverage-agreement tool clauses

## Status
STATUS: PASS — 37 clause mutants scored against BOTH the r24 fixture (9 cases) and the final r25 fixture (16 cases, k1–k7). Pristine draft tool (w1 final bytes, sha256 `bb506469…`) passes 9/9 and 16/16; red-arm OLD tool fails k1–k7; always-zero + veto-less controls rejected. Tool bytes restored exactly (before=after=`bb506469…`).

## Evidence
- Files: draft tool = w1 `souji-coverage-agreement.py` sha256 `bb506469…`; r25 fixture = w1 `r25-coverage-agreement.py` sha256 `2a65d8c0…` (16 cases); r24 fixture = round-24 w1 `r24-coverage-agreement.py` sha256 `42259756…`; OLD tool = round-24 w1 `souji-coverage-agreement.py` sha256 `71b89eb3…`.
- Pristine draft vs r24: rc=0 `cases=9 pass=9 control=FALSE-GREEN-REJECTED`. vs r25: rc=0 `cases=16 pass=16 control=FALSE-GREEN-REJECTED`.
- Red arm OLD tool vs r25: rc=1 `pass=9`; k1–k7 all FAIL (`counts_lines=0 exit=2`, refuses `--base-rev`); always-zero control 0/16; veto-less control fails k1/k2 → FALSE-GREEN-REJECTED.
- Always-zero emitter control: fails all 9 (r24) and all 16 (r25) cases → rejected. Veto-less control (accepts `--base-rev`, prints `kill_tested=0 kill_violations=0`, exits 0): fails k1/k2 → rejected.
- Real-lane probe (read-only): draft tool `--root lane --rev 6e4737e --base-rev a6d2d15` → `grounded=6 mapped=6 dangling=0 mismatches=0 kill_tested=6 kill_violations=0`, rc=0. Base a6d2d15 has exactly 6 grounded entries (listed below).

## Findings — mutant table (killed = fixture rc≠0/pass<total)
| mutant | clause defect | r24 kills? | r25 kills? | r25 failing cases |
|---|---|---|---|---|
| M01 | drop FRONT_GROUND parse | killed | killed | 1–8, k1–k7 |
| M02 | GROUND_TOKEN drop lookahead (F21→F2) | survived | survived | — |
| M03 | GROUND_TOKEN drop end-of-string alt | killed | killed | 6 |
| M04 | GROUND_TOKEN drop '-' alt | killed | killed | 6 |
| M05 | GROUND_TOKEN unanchored search | survived | survived | — |
| M06 | swap mapped/mismatch counting | survived | survived | — |
| M07 | DAANGLING always counted | killed | killed | 1–8 |
| M08 | drop DANGLING check | killed | killed | 5 |
| M09 | DANGLING scans status cell | killed | killed | 4–7 |
| M10 | header drops entries test | killed | killed | 1–3,5,6,7,8 |
| M11 | header drops ground test | killed | killed | 2 |
| M12 | same-F check dropped | killed | killed | 1,2,4,5,6 |
| M13 | ignore extra ground lines (first F only) | survived | killed | k5 |
| M14 | front matter not #-terminated | survived | killed | k2 |
| M15 | read HEAD instead of --rev | killed | killed | 1–8, k1–k5 |
| M16 | drop full-40 rev check | killed | killed | 9 |
| M17 | always exit 0 | killed | killed | 1–3,5,6,8,k1,k2,k5 |
| M18 | drop .md/blob filter | survived | survived | — |
| M19 | drop de-dup | survived | survived | — |
| M20 | split on any \| (escaped pipe breaks) | killed | killed | 4–7 |
| M21 | KNOWLEDGE_PATH unanchored suffix | survived | survived | — |
| K01 | drop kind!=blob check | survived | survived | — |
| K02 | drop same-F-set check | survived | killed | k2,k5 |
| K03 | kill_tested counts (entry,F) pairs | survived | killed | k4,k5 |
| K04 | exit ignores kill_violations | survived | killed | k1,k2,k5 |
| K05 | base side read from --rev | survived | killed | k1,k2,k5 |
| K06 | base side read from HEAD | survived | killed | k3 |
| K07 | kill rule checks only first base F | survived | killed | k5 |
| K08 | kill rule rejects extra tip grounds | survived | killed | k6 |
| K09 | one row per lost F (not per entry) | survived | survived | — |
| K10 | KILL-RULE folded into mismatches | survived | killed | k1,k2,k5 |
| K11 | kill keys never printed | survived | killed | k1–k7 |
| K12 | kill keys printed without --base-rev | killed | killed | 1–8 |
| K13 | --base-rev not validated | survived | survived | — |
| K14 | skip entries absent at rev | survived | killed | k1 |
| K15 | KILL-RULE rows not emitted | survived | killed | k1,k2,k5 |
| K16 | base knowledge tree read at rev | survived | killed | k1 |

### Survivor set after kill-rule arm lands (r25 fixture)
**M02, M05, M06, M18, M19, M21, K01, K09, K13** (9 survivors).

1. **M06 (swap mapped counting)** — `mapped` is printed but never asserted by either fixture (`mapped=*` in both `expect_text`; verified in fixture source). Pristine prints `mapped=6` on the real lane; M06 prints `mapped=0`, rc still 0. A permanently-wrong mapped count ships silently. Strongest coverage finding.
2. **K01 (existence clause drop)** — behaviorally invisible: a deleted/absent/kind-changed entry has empty rev-grounds, so the same-F subset branch (`not base_ks <= got`) still emits the KILL-RULE row; only the MISMATCH detail string differs, and `score()` discards detail. The existence clause is not independently enforced by any frozen case (same conclusion as peer `L1Souji25.MutCoverageAgreement` M06).
3. **K09 (per-F vs per-entry rows)** — no case drops ≥2 F-groups from one entry (k5 drops exactly one), so per-F and per-entry row counts agree everywhere. A k5 variant with base F2+F3 → rev F2 (two lost Fs) would discriminate.
4. **K13 (--base-rev unvalidated)** — fixture only has a bad `--rev` case (9); no bad-`--base-rev` negative case. The exit-2 refusal surface for `--base-rev` is unexercised.
5. **M02** — GROUND_TOKEN lookahead drop: `F21` misreads as `F2`, but no fixture case has a cell where F<k> abuts alnum; real-lane risk is low but real for cell shapes like `F2caveat`.
6. **M05** — F<k> mid-cell search; no fixture cell contains `F<k>` inside a longer string.
7. **M18/M19** — non-.md knowledge members (only ungrounded ledger.tsv) and duplicate spans in one row never exercised; real-lane neutral today.
8. **M21** — knowledge path with trailing text after `` `knowledge/x.md` `` is not exercised.

### Verification note (resolved by amendment-1)
Base a6d2d15 has 6 grounded entries (verified via `git show`: count-objects-garbage-readings-r25 F2, count-objects-linked-worktree-garbage F2, git-repo-structure-readonly F2, repo-size-census-readonly F2, quarantine-origin-record-fields-r24 F4, quarantine-staging-no-copy-r23 F4). Draft tool at lane tip prints `kill_tested=6`; preregistration-amendment-1.txt (line 10) already corrects the C1 after-target literal to `kill_tested=6 kill_violations=0` — no live discrepancy. My probe output (kill_tested=6) matches the amended target.

## Attack log
No counter attack. The mapped-unasserted gap, the redundant existence clause, and the kill_tested=4-vs-6 discrepancy are reported as coverage/verification findings only.
