# Round 13 W1 — ReviewQuality (QUALITY.md routing map, Q17/Q18 proposals)

Seat: `SoujiR13.ReviewQuality` (leaf, read-only). Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Baseline HEAD `31984f4`.
Writes: this file only. No commits, no build/lint/test runs, no edits to QUALITY.md, LOG.md or any lesson.
Tool installs/upgrades: none. Probes used: `read`, `grep`, `git -C … ls-files / merge-base / cat-file / reflog` (read-only, `-c maintenance.auto=false`), `sha256sum` on two tool files. Operator sweep not scanned.

## 0. Corrections to my own early probe
- A broad `tests/**` glob hit the 200-result cap; it wrongly suggested `tests/fixtures/` held only `r12-maintenance-guard.sh`. `git ls-files tests/fixtures` lists 34 tracked entries (`case-F1`…`case-F10`, `r12-maintenance-guard.sh`). Conclusions below use `ls-files`, not globs.

## 1. Facts verified (paths, lines, digests)

| fact | evidence |
|---|---|
| Installed quarantine tool sha256 `141c0fdc…` equals the digest K5 cites | `sha256sum tools/souji-quarantine.sh` = `141c0fdc4eaf9d0a…`; `corpus/knowledge/quarantine-same-filesystem-rename.md:45` |
| No `timeout` in the quarantine tool (Q8/M43 tool fix absent) | `grep timeout tools/souji-quarantine.sh` → no matches |
| No FIFO or stalled-target selftest (Q8/M44) | `grep -E 'mkfifo\|FIFO\|stall'` on the tool → no matches |
| Two definitions each of `file_sha` and `dir_digest` in the same tool | `tools/souji-quarantine.sh:184` and `:722`; `:186` and `:727` |
| Early `dir_digest` fails closed on symlinks; later one does not show that check | `:186-188` (`-type l … return 2`); `:727-729` (`s18_path_ok … s18_scope_ok`, no `-type l`) |
| Early `file_sha` has no regular-file test; later one adds `[ -f ]` | `:184` (`sha256sum -- "$1"`); `:722-724` (`[ -f "$1" ] \|\| return 1`) |
| `content_digest` routes non-dir, non-symlink targets (incl. FIFO) to `file_sha` | `:196-198` |
| Certifier relay: candidate writes a fixed shared path | `tools/cand-s16-cert.py:1856-1860` (`fragment = R10 / "cert-16.json"`) |
| K5 fixture not committed | `git ls-files \| grep -iE 'same-filesystem\|k5\|rename'` → only `corpus/knowledge/quarantine-same-filesystem-rename.md` and unrelated `tests/vault/vadv-52/ledger-k5.tsv` |
| K5 Evidence admits it was not committed | `quarantine-same-filesystem-rename.md:21` ("scratch-only script, not committed"), `:53-54` (HELD) |
| K5 Gate row still says the fixture is committed | `corpus/lessons/round-12.md:136` |
| Non-author spot-check reported "pending" though the verifier file exists | `round-12.md:158` vs `round-12-verifier-spotcheck.md:13` |
| Verifier says "15 criteria"; QUALITY has 16 rows, 14 active (Q15, Q16 withdrawn) | `round-12-verifier-spotcheck.md:17`; `corpus/QUALITY.md:24-40` |
| SKILL checklist lines exist (right-repo, `-c maintenance.auto=false`, no `git add -A`, pins) | `SKILL.md:98`, `:99`, `:100` |
| Maintenance guard exists and records shellcheck clean | `tests/fixtures/r12-maintenance-guard.sh` tracked; `tests/results/r12-maintenance-guard.txt:5-6` |
| Fleet-root M53 residue: `c095ea1` still an object, not an ancestor of fleet HEAD; 5 reflog entries match `r12` | `git -C /home/vgpnk/Projects/shokunin merge-base --is-ancestor c095ea1 HEAD` → rc 1; `cat-file -t` → commit; `reflog … \| grep -c r12` → 5. Repair status unverified; orchestrator-owned. |
| `tests/fixtures/case-F10/creds.pem` is tracked (credential-shaped name, outside my slice) | `git ls-files tests/fixtures` (route to L1 to confirm synthetic) |

Lesson pointers resolved by reading the cited lines (all match their claim): Q1 `round-9.md:14`, `round-6.md:20`; Q2 `round-5.md:38`; Q3 `round-5.md:9`; Q4 `round-8.md:24`, `round-4.md:21`, `round-3.md:27`; Q5 `LOG.md:58`, `round-7.md:19`, `round-6.md:8`; Q6 `round-11.md:14`, `:16`; Q7 `LOG.md:381`; Q8 `LOG.md:373`, `:403`; Q9 `census/round-10/S02-cluster-A.md:19`; Q10 `round-9.md:16`; Q11 `round-2.md:12`, `:19`, `round-3.md:22`, `:25`; Q12 `round-3.md:29`; Q14 `LOG.md:421`. Every `round-12 M<nn>` pointer resolves to a `## Mistakes` row. Not checked: `tests/runner-23.sh:38` (Q4 pointer text).

## 2. Routed-item map: every M-row to its fix or debt

Classification of all 53 `## Mistakes` captured-by cells (my count from `corpus/lessons/round-12.md:61-115`):

| class | n | rows |
|---|---|---|
| code/selftest-backed | 9 | M02, M14, M15, M29, M32 (partial), M33, M34, M38, M51 (gate exists; not run at commit time) |
| prose-only, no check | 12 | M01, M03, M05, M16, M17, M18, M19, M20, M22, M24, M31, M35 (partial) |
| lesson, decision rule, manual protocol, handoff file | 8 | M08, M12, M21, M26, M36, M46, M47, M48 |
| criterion-only (QUALITY row, no runtime enforcement) | 22 | M04, M06, M07, M09, M10, M11, M13, M23, M25, M28, M30, M37, M40, M41, M42, M43, M44, M45, M49, M50, M52, M53 |
| none / external | 2 | M27, M39 |

Sum 53. The published "51/53" (`round-12.md:57`) counts any non-`none` cell, so 12 prose-only cells and 8 lesson/handoff cells count as calibration. Only 9 of 53 rows (17%) have executable backing. Treat 51/53 as a rule-mapping count, as the verifier already said.

Routed or open debt, each checked above:
- **M43 → Q8, tool fix open.** No `timeout` in `tools/souji-quarantine.sh`. Stage-2 `mv` is unwrapped (K5 cites the move at `:529/:536`; line not re-read by me). Owner: round-13 C2 seat.
- **M44 → Q8, FIFO.** Digest path `:184` / `:722`: whether the `[ -f ]` version is effective is [INFERENCE] (bash redefines at execution time; main body follows `:722`). Even if effective, no selftest proves FIFO fail-closed, so the capture is unproven.
- **M40, M41 → Q6, relay and selection.** Q6's test checks only sha equality. The one-author-per-fragment clause and the candidate-selection clause have no test. Live counterexample: `tools/cand-s16-cert.py:1859`. Owner: round-13 C1 seat.
- **M50 → Q9.** No shellcheck call in the installed quarantine tool. Q9 binds only "new scripts", so the installed tool that C2 touches stays ungated.
- **M51, M42, M53 → Q7/Q13 + SKILL.** Enforced only as SKILL checklist text (`SKILL.md:98-100`) plus one fixture. `git ls-files` shows the fixture is tracked.
- **M53 residue.** See the §1 row for `c095ea1`. Repair not verified; orchestrator-owned. Not my write set.
- **M10, M11, M30 (host `/tmp`, object residue).** Routed to operator/tsukuroi (`round-3.md:27-29`, `round-8.md:24-27`). Q4 covers fixtures only, so host hygiene is uncaptured. External debt.
- **M47 (kotodama re-sweep).** Lesson says "scheduled ≈2026-10-20", which is today. No evidence of the re-sweep in lane. Date-due debt.
- **M27, M39.** External, `none`. Accepted as operator-owned.
- **Q4 has no fixture to test.** K1–K4 have no committed fixture; their `recheck:` lines are inline `curl`/`man`/`grep`. Q4's test (`grep -c 'TMPDIR:-/tmp' <fixture>`) is vacuous for the admitted entries. The Q16 test (no fixture writes outside `/var/tmp`) is satisfied by K1–K4 only because their rechecks write nothing.
- **K3 recheck fetches `main`, not `v0.35.0`.** Its `verified-at` names the tag (`dupe-finders-detect-then-act.md:2`), but `recheck:` (`:3`) uses `…/fclones/main/…`. Q1 wants the recheck pinned to the verified version. Calibration gap; not a fabricated catch.

## 3. Circular lesson rationale (Q15/Q16 standard)

A criterion is circular when its only lesson pointer is a `round-12 M<nn>` row that names this same criterion in its captured-by cell.

- **Q13: fully circular.** Cites `round-12 M45` and `M53`; both have `captured-by = QUALITY.md Q13` (`round-12.md:107`, `:115`). No independent anchor. Remedy: ground in a non-round-12 event or withdraw via a superseding row.
- **Q7: partial.** Cites `round-12 M51` and `M53`, both captured by Q7. Independent anchor `LOG.md:381` exists, so Q7 stands on it, but the two round-12 pointers add no evidence.
- **Q9: partial.** Cites `round-12 M50` (captured by Q9). Independent anchor `census/round-10/S02-cluster-A.md:19` is verified.
- **Q10: partial.** Cites `round-12 M52` (captured by Q10). Independent anchor `round-9.md:16` is verified.
- **Q16: weak.** Its pointer is a post-review section, not a `## Mistakes` row, so the file's own form rule does not apply. Its rationale is the K5 admission it reacted to; the non-circular anchor is the absence of any mined `/dev/shm` lesson, which is itself a negative claim.

## 4. Unproven catches (captured-by without an executable check)

- **M41 → Q6, clause 3.** No test. Capture unproven.
- **M40 → Q6, clause 2.** No test. Capture unproven. `cand-s16-cert.py:1859` still writes a fixed shared path.
- **M43 → Q8.** Tool fix absent (see §2). Q8's test as written, `grep -nE 'timeout [0-9]+[smh]? .*(mv\|sha256sum)' <tool>` (`QUALITY.md:32`), contains `\|`. In ERE `\|` is a literal pipe [INFERENCE: GNU grep ERE semantics, not executed], so the command matches the string `mv|sha256sum` and returns 0 for any tool. Markdown renders the cell as `|`, but the raw text is what a reader copies. Fix: move the command into a fenced block.
- **M44 → Q8, FIFO.** No FIFO selftest (see §2).
- **M45, M53 → Q13.** Test is `git show --stat` on one commit. Nothing enforces it at commit time.
- **M20 → SKILL.md:100.** Line 100 has a count command, but no gate runs it.
- **Q9 scope.** Applies to "new scripts" only, so the installed tool is outside it.

## 5. Missing mistake row: the K5 defect

The r12 K5 defect is in the lesson record but has no `## Mistakes` row. `round-12.md` `## Mistakes` runs M01–M53 and none names a Gate claim of a committed fixture. The defect appears only in `## Post-review fixes` item 2 (`round-12.md:353-358`), `round-12-verifier-spotcheck.md:13`, and the K5 HELD note. A Q-criterion can cite a mistake only through a `round-12 M<nn>` row, so Q17 needs M54 first.

## 6. Proposed criteria

### Q17 — committed-fixture claims must name a tracked path (grounded in r12 K5)
- **Criterion:** A Gate row, knowledge entry or lesson that calls a fixture "committed" or cites a fixture path must name a path that is tracked at the closing commit. Evidence that says "not committed" or "scratch-only" cannot support admission under Q2 or Q4.
- **Applies to:** knowledge, round evidence.
- **Test:** for each cited fixture path `P`: `git -C <lane> -c maintenance.auto=false ls-files --error-unmatch -- "$P" >/dev/null; echo $?` → 0. Cross-check: every entry carrying `## Admission status — HELD` must not appear in the admitted-count command at `round-12.md:373`.
- **Lesson pointer (required):** new row `round-12 M54` in `corpus/lessons/round-12.md ## Mistakes`: "Gate row claimed a committed fixture for K5; none existed (`round-12.md:136` vs `quarantine-same-filesystem-rename.md:21`; `round-12.md:353-358`; `round-12-verifier-spotcheck.md:13`)". The rationale is the defect, not K5's admission, so the criterion would stand if K5 were later admitted with a real fixture.
- **Limitation:** checks existence only, not that the fixture's output matches.

### Q18 — verdict fragments have one writer and a unique path; supersedes Q6 (grounded in r11 relay)
- **Criterion:** Each certifier writes `census/round-<N>/<certifier-id>.json` and refuses to overwrite (exclusive create or `noclobber`). The aggregator fails when two fragments carry the same measured sha256, or when that sha differs from `sha256sum` of the installed tool. Supersedes Q6, which is kept unchanged per the file's rule.
- **Applies to:** round evidence, tools.
- **Test:** `grep -nE 'cert-[0-9]+\.json|R10 / "cert' tools/*.py tools/*.sh` → 0 for certifier writers (currently `tools/cand-s16-cert.py:1859` → 1). Plus `sha256sum tools/<tool>` equals the fragment digest.
- **Lesson pointers:** `corpus/lessons/round-11.md:14` (relay overwritten), `:16` (selection rule); M40, M41. Non-circular: round-11 events, not round-12 rows.
- **Limitation:** the candidate-selection clause (M41) is still not executable. Keep M41 criterion-only and say so.

## 7. Checks for L1 to run after integration (not run by me)
1. `grep -c timeout tools/souji-quarantine.sh` → expect 0 now, ≥1 after C2 (M43).
2. `grep -nE '^(file_sha|dir_digest|content_digest)\(\)' tools/souji-quarantine.sh` → currently 2/2 for the first two; expect 1 each after cleanup.
3. Q8 test as corrected: `grep -nE 'timeout [0-9]+[smh]? .*(mv|sha256sum)' tools/souji-quarantine.sh; echo $?` → expect 1 now.
4. FIFO fixture in `mktemp -d /var/tmp/…` with `trap` cleanup: a pinned target that is a FIFO must exit fail-closed within a bound. Expected: no such case exists today.
5. `shellcheck -S warning tools/souji-quarantine.sh; echo $?` (Q9, record the result, do not infer it).
6. `git -C <lane> ls-files | grep -ciE 'same-filesystem|k5-rename'` → 0 (K5 fixture still absent).
7. `grep -c 'cert-16.json' tools/cand-s16-cert.py` → 2 now (`:1856`, `:1859`); 0 after Q18 fix.
8. Dangling-Q check from `round-12.md:58-59`: must print nothing.
9. Bookkeeping: `round-12.md:158` says "pending" while `round-12-verifier-spotcheck.md` exists. Fix in the closing commit (Q10).
10. Verifier count: `round-12-verifier-spotcheck.md:17` says "15 criteria"; the correct figure is 16 rows, 14 active.

## 8. Limitations and residual risk
- I did not execute any tool, test, shellcheck, or selftest. Every claim about behaviour is a source-line or grep fact, or marked [INFERENCE].
- The shadowing of `file_sha` and `dir_digest` (§1) is an observed duplicate definition. Its effect on the symlink fail-closed and FIFO behaviour is [INFERENCE] and needs L1 to confirm by sourcing the tool in a `/var/tmp` probe.
- The 22 criterion-only rows are not proven failures. They are unverified at runtime, and that is the claim this file makes.
- `c095ea1` repair status and the kotodama re-sweep date are outside lane evidence.
- `tests/fixtures/case-F10/creds.pem` is outside my slice; L1 should confirm it is synthetic.
- Proposed criteria are not admitted. Q17 requires M54 first; Q18 requires L1/aggregator review.
