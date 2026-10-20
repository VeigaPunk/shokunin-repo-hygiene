# Round 13 — mistake draft (MistakeLedger seat, w1)

author: SoujiR13.MistakeLedger (scribe, leaf) · date: 2026-10-20 · baseline HEAD `31984f4`
status: DRAFT for L1 integration. Not written into `corpus/lessons/round-13.md`. Prior lesson
`corpus/lessons/round-12.md` and `corpus/lessons/round-12-verifier-spotcheck.md` are unchanged.

Scope: round-13 mistake rows sourced to (a) the r11 certifier relay, (b) the r12 nonexistent
K5 fixture, (c) M43/M44 quarantine timeout and FIFO defects, (d) the Q15 circular criterion; plus
every routed r12 verifier item (Table 3). IDs M54–M62 continue r12's M01–M53 as draft numbers;
L1 renumbers at integration.

Conventions:
- `kind`: as r12 (`defect` · `process` · `honest-stop` · `caught`).
- `captured-by`: a `path:line` or criterion row. `no-check` = a rule exists with no executable
  check. The r12 count command counts a `no-check` criterion as mapped (r12 convention); Table 4
  shows which rows have an executable check. None of the rows below has one.
- `status` is stated in the class cell: `demonstrated` = observed in a cited artifact or re-run
  read-only this session (command in Table 2); `planned` = fix named here, not in the tree.
- `[INFERENCE]` = not observed.
- Read-only probes only: `git show`, `git ls-files`, `grep`, `sha256sum`, `test -e`. No build,
  lint, test, format, or tool run. No write outside this file and the report trailer.

## Table 1 — draft rows

| id | kind | class | evidence pointer | captured-by | fix (proposed) |
|---|---|---|---|---|---|
| M54 | defect | Shared certifier relay: `census/round-10/cert-16.json` was overwritten by ≥3 concurrent r11 certifier passes; r11 then recorded restoration to sha256 `6293283e` and that bytes equal HEAD. HEAD now hashes to `662294df`. — status: demonstrated (overwrite per r11 record; restore claim contradicted by current HEAD bytes) | `census/round-11/final-27.json:30-34` (concurrent_drift_observed) and `:121-125` (process_incidents, `cert-16-relay`, PROCESS DEFECT); `census/round-11/dissent-32.md:49-51` (§4 relay) and `:62-68` (§5, "restored ... 6293283e"); `census/round-11/cert-12.json:2660` (restored from git, sha256 6293283e4…); `corpus/lessons/round-11.md:14-15`. Re-check: `git show e879ba0:census/round-10/cert-16.json \| sha256sum` → `6293283e…`; `git show HEAD:census/round-10/cert-16.json \| sha256sum` → `662294df…`; `git show --stat --format= 1ccf11b -- census/round-10/cert-16.json` → 260 insertions, 307 deletions | `corpus/QUALITY.md:30` (Q6, `no-check`: its test is a manual sha equality, no script) | planned: one certifier fragment per author; the `restored from git` claim is a check (`git show HEAD:<path> \| sha256sum` equals the digest named in the claim) run at close, not prose. [INFERENCE: commit `1ccf11b` ("pre-reboot sweep: remaining r11 fragments + results") is the commit that changed the bytes after `e879ba0`; the cause was not read beyond its stat.] |
| M55 | defect | CERTIFIED verdict attached to bytes other than the installed bytes (false success): committed `census/round-10/cert-16.json` reports `certification_ready: true` for census `60aef4c0…` (S16 measurement); the installed census is `6a000c59…` (observed this session); r11 had recorded `462dabd2…` as installed, with its selftest 2/36 red. — status: demonstrated (bytes observed; r11 record; not re-run) | `census/round-11/cert-14.json:322-328` (s16_cert_crosscheck, `BYTE MISMATCH`), `:331`; `census/round-11/final-27.json:36-41` and `:118-119`; `census/round-11/dissent-32.md:15-19`; `census/round-10/cert-16.json:2618` (`certification_ready: true`), `:10`, `:20` | `corpus/QUALITY.md:30` (Q6, `no-check`) | planned: a verdict fragment names the sha256 of the measured tool bytes; the validator fails when that sha differs from the installed file; a verdict whose census is not installed cannot be CERTIFIED. |
| M56 | process | Evidence paths outside the lane: certification fragments cite `/var/tmp` scratch roots that are not in the repo, so a verdict cannot be re-read from the commit. — status: demonstrated (paths cited; one resolves on this host only). | `census/round-10/cert-16.json:8-9` (`freeze_dir` `/var/tmp/s16-r11-cert`), `:24` (report `/var/tmp/s16-r11-cert/CERT-16-R11.json`); `census/round-11/cert-13.json:10` (scratch_root `/var/tmp/s13-r11`); `census/round-11/cert-12.json:2660` (`/var/tmp/s12-run/cert.py`). Observed: `test -e /var/tmp/s16-r11-cert/CERT-16-R11.json` → present, sha256 `2844fc13…`; the file is not tracked in the lane. | none | planned: the validator rejects any evidence path that is outside the lane root, absent from the commit, or unresolvable; a fragment cites lane-relative committed paths only. |
| M57 | defect | r12 K5 claimed a committed fixture that does not exist; its Gate row said the recheck line "is the committed fixture". — status: demonstrated (r12 reviewer; re-grep this session) | `corpus/knowledge/quarantine-same-filesystem-rename.md:21` ("FIXTURE (scratch-only script, not committed)"), `:3` (recheck one-liner); `corpus/lessons/round-12.md:136` (Gate row for ART C6 → K5); `corpus/lessons/round-12.md:357-359` (post-review item 2, K5 admitted → HELD); `census/round-12/postreview.md:17` (defect 3 row) and `:92` (item 5). Observed: `git -C <lane> ls-files tests \| grep -ci k5` → `1`, and that one file is `tests/vault/vadv-52/ledger-k5.tsv` (an r6 vault fixture, not the K5 recheck; content not read); `grep -rl 'souji-k5' tests` → no match. | `corpus/QUALITY.md:26` (Q2 "cites … or a committed fixture", `no-check`) | planned: an admission lint: every `FIXTURE`/`recheck` claim in `corpus/knowledge/*.md` resolves to a tracked path, or the entry is refused; K5 stays HELD until a committed `/var/tmp`-only fixture exists. |
| M58 | defect | Circular criterion: Q15 (`/dev/shm` as a second device) was written to admit K5 and cites K5's own admission as its only lesson pointer. Q16 withdraws it. — status: demonstrated (text of QUALITY.md; r12 post-review item 3) | `corpus/QUALITY.md:39` (Q15), `:40` (Q16 "WITHDRAWN … circular"); `corpus/QUALITY.md:11-12` (rule: a criterion is superseded by a new row, never rewritten); `census/round-12/postreview.md:90` (defect 3: "QUALITY Q4 was rewritten after the entry needed it"); `corpus/README.md:59-62` (F4 entry HELD). Observed: `corpus/QUALITY.md:28` (Q4) has no `/dev/shm` clause. | `corpus/QUALITY.md:40` (Q16 withdrawal row; a row, no check that admitted entries cite no withdrawn criterion, `no-check`) | planned: a lint that each admitted knowledge entry's criterion ids resolve to non-withdrawn rows, and each criterion's lesson pointer resolves to a lesson that predates the admission it serves. |
| M59 | defect | Quarantine per-target staging has no timeout; a staging loop hung to the 20-min driver timeout (M43 restated with the r13 tool check). — status: demonstrated (incident in LOG; installed-tool grep); fix planned | `LOG.md:373-378` (staged 3 files then hung; 93 staged by hand; 2 files missing post-timeout, restored from origin). `tools/souji-quarantine.sh` (sha256 `141c0fdc…`): `:529` (`git -C "$crepo" mv -- "$rel" "$qpath"`) and `:536` (`mv -- "$ct" "$qpath"`) are unwrapped; `grep -c timeout tools/souji-quarantine.sh` → `0`. | `corpus/QUALITY.md:32` (Q8; its test `grep -nE 'timeout [0-9]+[smh]? .*(mv\|sha256sum)'` ≥1 is unmet; no selftest case) — the criterion is unmet, not merely unenforced | planned: wrap each per-target `mv` and digest in `timeout`; fail-closed ABORT with diagnostics; a selftest case with a stalled target. Deletion certification stays OFF for this tool. |
| M60 | defect | FIFO digest hang (M44): three operator-sweep judge fixtures stuck ~9 h on `sha256sum` of a FIFO in `wait_for_partner`. — status: incident demonstrated in LOG; installed-tool mechanism `[INFERENCE]`; fixture provenance not in the lane | `LOG.md:402-404` (ppid=systemd, do_wait, `sha256sum` of a FIFO, `wait_for_partner`). `grep -cE 'FIFO\|mkfifo' tools/souji-quarantine.sh` → `0`; same for `tools/souji-vault-verify.impl-17.sh` → `0`; `wait_for_partner` occurs only at `LOG.md:404` among `tools/`, `tests/`, `census/round-12/`, `corpus/`. Installed digest helpers: `tools/souji-quarantine.sh:184` (`file_sha` unguarded) and `:722-725` (`file_sha` with `[ -f "$1" ]`); see M61 for which definition runs. | vault verifier: `tools/souji-vault-verify.sh:606` (`if [ ! -f "$target" ] && [ ! -d "$target" ]` → unreachable; r12 pointer `:608` is its evidence string). Quarantine: none. `corpus/QUALITY.md:32` (Q8 FIFO selftest clause, unmet). | planned: digest readers accept regular files only (`[ -f ]` and not `-L`), under `timeout`; a FIFO selftest case under `/var/tmp` exits fail-closed. |
| M61 | process | Shadowed helpers: the installed quarantine and vault tools define `file_sha` and `dir_digest` twice each. The later, guarded definitions shadow the earlier ones only by bash last-definition-wins, so the safety property depends on file order. — status: demonstrated (4 definitions per file, by grep); effective-definition claim `[INFERENCE]` (not executed) | `grep -cE '^(file_sha\|dir_digest)\(\)' tools/souji-quarantine.sh` → `4` (`:184`, `:186`, `:722`, `:727`); `tools/souji-vault-verify.sh` → `4` (`:109`, `:111`, `:717`, `:722`). Dispatch `run_mode` at `tools/souji-quarantine.sh:1568`, after the second definitions. | none | planned: each function defined once; the unguarded copies are deleted (cutover, no shim); a check counts definitions per name and fails at ≠1. |
| M62 | process | Calibration counting: the r12 `captured-by` figure (51/53) counts a row as captured when its cell names a rule, including criteria whose test is a manual grep or a hash comparison with no script. — status: demonstrated (r12 post-review item 5 says it is a coverage count; this draft confirms the test column) | `corpus/lessons/round-12.md:57` (51/53), `:368-369` (post-review item 5). Criteria with no executable check: `corpus/QUALITY.md:26` (Q2), `:28` (Q4), `:30` (Q6), `:31` (Q7, `grep` test only), `:32` (Q8, unmet), `:37` (Q13), `:40` (Q16). | none (this row is the calibration note) | planned: QUALITY rows gain a `check` cell naming an executable command and expected output; the calibration count reports executed checks separately from named rules. |

## Table 2 — evidence (read-only, lane root as cwd, absolute paths; observed this session)

| id | command | observed |
|---|---|---|
| M54 | `sha256sum census/round-10/cert-16.json`; `git show HEAD:census/round-10/cert-16.json \| sha256sum`; `git show e879ba0:census/round-10/cert-16.json \| sha256sum`; `git rev-parse HEAD:census/round-10/cert-16.json` | `662294df…` (worktree); `662294df…` (HEAD); `6293283e…` (e879ba0); HEAD blob `07b9dd87`, e879ba0 blob `dda75eaf` |
| M54 | `git log --oneline -n 3 -- census/round-10/cert-16.json` | `1ccf11b pre-reboot sweep…`, `e879ba0 round-10: REJECTED…` (plus `git show --stat` above) |
| M54/M56 | `test -e /var/tmp/s16-r11-cert/CERT-16-R11.json`; `sha256sum` of it | present; `2844fc13…` |
| M55 | `sha256sum tools/souji-census.sh`; `git show HEAD:census/round-10/cert-16.json \| grep -nE 'certification_ready\|60aef4c0\|462dabd2'`; read `census/round-11/cert-14.json:322-331` | installed census `6a000c59…` (= cand-census-02 per `census/round-11/cert-13.json:206`), not `60aef4c0…` (named by HEAD cert-16 `:10`, `:20`), not `462dabd2…` (`:26`, `:30-31`); HEAD cert-16 `certification_ready: true` at `:2618`; cert-14 `BYTE MISMATCH` (`:326`), live census selftest `36 checks, 2 failed` (`:331`) |
| M57 | `git -C <lane> ls-files tests \| grep -ci k5`; `grep -rl 'souji-k5' tests` | `1` (`tests/vault/vadv-52/ledger-k5.tsv`); no match |
| M58 | read `corpus/QUALITY.md:26-40`; grep `/dev/shm` in `corpus/QUALITY.md` | Q15 active text at `:39`, Q16 withdrawal at `:40`; no `/dev/shm` clause in Q4 (`:28`) |
| M59 | `grep -c timeout tools/souji-quarantine.sh`; `sha256sum tools/souji-quarantine.sh` | `0`; `141c0fdc4eaf9d0a3d628b381cc5386f6d4be71565ddfb98aa10f6eb3c9573c9` |
| M60 | `grep -cE 'FIFO\|mkfifo' tools/souji-quarantine.sh tools/souji-vault-verify.impl-17.sh`; grep `wait_for_partner` in `tools/`, `tests/`, `census/round-12/`, `corpus/`, `LOG.md` | `0`, `0`; `wait_for_partner` only at `LOG.md:404` |
| M61 | `grep -cE '^(file_sha\|dir_digest)\(\)' tools/souji-quarantine.sh tools/souji-vault-verify.sh` | `4`, `4` |
| M62 | read `corpus/QUALITY.md:23-40` test column | Q2, Q4, Q6, Q7, Q8, Q13, Q16 tests are prose or manual; Q8 test unmet (`timeout` count 0) |

Not run: any selftest, build, or the quarantine tool itself; `census/operator-sweep-20261019/` was not
opened or searched.

## Table 3 — routed r12 verifier items: disposition

Source: `corpus/lessons/round-12-verifier-spotcheck.md` (read-only; not rewritten) and
`corpus/lessons/round-12.md` `## Post-review fixes` (read-only; not rewritten).

| item | source | r12 disposition | round-13 draft status |
|---|---|---|---|
| K1–K4 admissions, spot-check | verifier table row 1 (`agree`) | admitted | no new row; agreement recorded in the verifier lesson |
| K2 recheck | verifier row 1 + post-review item 4 (`MANWIDTH=2000`, 6/6 defaults) | corrected, admitted | no new row |
| K5 admission → HELD | verifier row 2 (`agree` with the hold) + post-review item 2 | held; `## Admission status — HELD` appended | M57 (fixture absent) and M58 (circular Q15); K5 remains HELD |
| Q15 withdrawn by Q16 | post-review item 3; `corpus/QUALITY.md:39-40` | withdrawn | M58 |
| S030 recheck `—` → `365d` | post-review item 1 | fixed in place | no new row |
| C1 restated as a rule-coverage count (28/52 → 51/53) | post-review item 5; verifier "Per-axis" line | restated | M62 |
| C3 (size census) reject | `corpus/lessons/round-12.md:133`; postreview row 4 | rejected, reason premise noted | no new row |
| Debt: quarantine tool timeout | verifier "Debts" line | open | M59 (Q8 unmet), M60 (FIFO) |
| Debt: certification OFF | verifier "Debts" line | OFF | M54–M56 (what must hold before ON) |
| Non-author spot-check "pending" | `corpus/lessons/round-12.md:158` | superseded by the verifier lesson file | no edit to the r12 lesson |

## Table 4 — pointer corrections and open points (for L1; no prior row rewritten)

1. r12 M44 pointer `tools/souji-vault-verify.sh:608` → the guard is `:606`; `:608` is its evidence string.
2. r12 M44 "the stuck readers were elsewhere": `wait_for_partner` is not in the lane (Table 2). Its
   provenance is `[to-verify]`; the LOG is the only in-lane source.
3. r12 K5: the only tracked `k5` path is an unrelated vault fixture; no K5 recheck file is tracked.
4. The r12 round-count command (`round-12.md:55`) reads `$6` as captured-by. Draft rows keep the 6-column
   shape, so the same command applies unchanged.

## Proposed final checks (for L1; none run here)

1. `git show e879ba0:census/round-10/cert-16.json | sha256sum` equals `6293283e…`, and `git show HEAD:census/round-10/cert-16.json | sha256sum` equals `662294df…` (pre-fix state; re-check after any fix).
2. `sha256sum tools/souji-quarantine.sh` equals `141c0fdc…` before any fix; record the new sha after.
3. `grep -c timeout tools/souji-quarantine.sh` is `0` now; Q8 test `grep -nE 'timeout [0-9]+[smh]? .*(mv|sha256sum)' tools/souji-quarantine.sh` must be ≥1 after the fix.
4. `grep -cE 'FIFO|mkfifo' tools/souji-quarantine.sh` is `0` now; must be ≥1 after a FIFO selftest case is added.
5. `grep -cE '^(file_sha|dir_digest)\(\)' tools/souji-quarantine.sh` is `4` now; must be `2` after the shadowed copies are removed; same for `tools/souji-vault-verify.sh`.
6. `grep -rl 'souji-k5' tests` is empty now; K5 leaves HELD only when a committed `/var/tmp`-only fixture matches its recheck.
7. `grep -oE 'QUALITY\.md Q[0-9]+' corpus/lessons/round-13.md | sort -u` — each id resolves to a non-withdrawn `^| Qn |` row.
8. `shellcheck -S warning <each new or edited shell script>` exits 0 (QUALITY Q9).
9. Any new fixture: `grep -c 'TMPDIR:-/tmp' <fixture>` is `0` and `grep -c '/var/tmp' <fixture>` ≥ 1, with a trap removing the mktemp dir (QUALITY Q4).
10. Calibration count: `awk -F'|' '/^\| M[0-9]+ \| (defect|process|honest-stop|caught) \|/{n++; if ($6 !~ /^[[:space:]]*none/) c++} END{print c"/"n}' corpus/lessons/round-13.md` (the r12 convention; counts `no-check` as mapped).

## Limits

- Draft IDs; L1 renumbers. Rows are not independent non-author evidence. Do not claim non-author status.
- M54's cause (commit `1ccf11b`) is `[INFERENCE]`; the commit's diff was only read as a stat.
- M60's FIFO mechanism in the installed tool is `[INFERENCE]` from bash last-definition-wins (M61); it was not executed.
- No fix is proposed as implemented. Deletion certification stays OFF; no live target was touched.
