# R13 w1 · ReviewQuarantine — baseline audit of `tools/souji-quarantine.sh` staging and digest flow

Seat: `SoujiR13.ReviewQuarantine` (reviewer, leaf, read-only). Scope: control flow only.
No tests, builds, lint, waits, or commits were run. No tools were installed or updated by this seat.
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.

Evidence keys: `Q:<line>` = `tools/souji-quarantine.sh`; `E:<line>` = `tools/cand-merge-verify.sh` (the receipt engine the quarantine actually invokes, see F6); `R9:<line>` = `tools/souji-round9-selftest.sh`.
Status tags: **FACT** = read directly in the file at the cited line. **INFERENCE** = derived from code reading or bash semantics, not executed. **UNVERIFIED** = needs a fixture run by L1.

---

## 0. Summary

| # | Severity | Axis | Finding |
|---|----------|------|---------|
| F1 | High | calibration / exit | `set -euo pipefail` (Q:121) turns unguarded `x=$(digest)` assignments into process exits on the digest-failure paths. Those exits skip the designed fail-closed branches and skip RESULT/SUMMARY. Exit 2 collides with the usage code. |
| F2 | High | special-file | No special-file classification anywhere in the quarantine flow. A FIFO or unreadable top-level target earns engine SAFE(stale) and then dies at the stage-1 pin (Q:498). The only protection is the `[ -f ]` guard in `file_sha` (Q:722-723), which fails by exit, not by refusal. |
| F3 | High (latent) | timeout | Zero `timeout` bindings in the quarantine, the engine, or the r9 runner. Engine invocation is unbounded at Q:1067-1068 (called at Q:413 and Q:560). No reachable hang was proven by reading; the hang guard is the `-f` check alone. |
| F4 | Medium | exit / list | `--list` usage errors fire mid-run (Q:649, Q:652) after earlier rows have already been staged, deleted, or aborted. The contract says malformed rows are usage errors (Q:21-22). |
| F5 | Medium | exit / signal | No INT/TERM/HUP handling. A signal during the hold (Q:556) leaves a staged copy with no RESULT line and an undocumented exit code. |
| F6 | Medium | calibration / authority | The engine actually run is `cand-merge-verify.sh` (Q:134-135), not the documented `souji-verify.sh` (Q:6-7, Q:109-110). The engine has no special-file refusal (E:767-787). |
| F7 | Low | maintainability | Large dead block (Q:683-1213) plus shadowed base definitions (Q:184-194, Q:212-229, Q:241-255). Some dead calls point at functions that do not exist in this file (s18_try_ledger, finish_mismatch, scratch_type). |
| F8 | Medium | coverage | Selftest has no fixtures for FIFO, unreadable file, symlink-in-quarantine, vault-missing, dir-vault symlink, digest or engine timeout, malformed-after-valid list rows, or signal. R9 has none for FIFO or symlink. |
| F9 | Low | operability | Same-day collision: an ABORTED copy stays at `.ufo-quarantine/<date>/<rel>`. A re-run the same UTC day is refused as `quarantine-collision` (Q:477-480). |

Restore-vs-stay: the documented policy is **stay and report ABORTED, never restore, never delete on inconclusive** (Q:68-72; implemented at Q:565-573). Every crash path in F1 violates the reporting half of that policy, not the stay half.

---

## 1. Control flow as read (baseline, `tools/souji-quarantine.sh`)

Overrides and load order (FACT):
- Base definitions at Q:184-255 (`file_sha`, `dir_digest`, `run_verify`, `ledger_row_for`) are shadowed by later definitions: `file_sha` Q:722, `dir_digest` Q:727, `run_verify` Q:1061, `ledger_row_for` Q:1087. Shadowing happens because the `S18_KIND=quarantine` override block (Q:1041-1149) and the unconditional S18 block (Q:683-1039) are sourced after the base.
- Live entry chain: `main` Q:1517-1569 → `run_mode` Q:601-669 → `flow_one` Q:1100-1120 (override) → `s18_flow_one` Q:405-599 → `run_verify` override Q:1061-1085 → engine `bash "$VERIFY_BIN"` Q:1067-1068.

Per-target stage map (FACT, line numbers in `s18_flow_one`):

| Stage | Lines | Operation | Failure behaviour today |
|---|---|---|---|
| pre-flight | 437-467 | canon, secret, repo-root, relpath, `..` checks | `block_one` → RC=3 (Q:399) |
| existence/symlink/collision | 469-480 | `[ -e ]`, `[ -L ]`, `[ -e qpath ]` | `block_one` |
| dirty tracked | 485-495 | `git status` | `block_one dirty-tracked` |
| **pin (stage 1)** | **497-499** | `pin_sha=$(content_digest "$ct")` ; `stat` | **unguarded: set -e exit (F1, F2)** |
| dry-run | 504-520 | prints CMD lines | RESULT DRY-RUN-PASS |
| stage 2 | 523-542 | `mkdir -p`, `git mv` / `mv` | `STAGE2-FAILED`, RC=3, no restore (correct: nothing moved) |
| hook (test-only) | 546-551 | `SOUJI_Q_TEST_HOOK` | logs `hook-failed`, continues |
| stage 3 | 554-557 | `sleep $HOLD` | intended wait |
| stage 4 prong1 | 560-562 | `run_verify "$qpath"` | rc≠0 → V_VERDICT=ERROR (handled, Q:1069-1070) |
| **stage 4 second** | **564 → 280-389** | `s18_second_check`, `second_check` | **digest sites unguarded: set -e exit (F1)** |
| stage 5 | 575-597 | `rm -rf`, `git rm --cached`, rmdir | `ABORTED` + RC=3 on rm failure (Q:576-581) |

Digest/hash call sites (FACT, exhaustive from full read):

| Call site | Line | Context | Guarded? |
|---|---|---|---|
| `content_digest` def | Q:196-199 | `[ -L ]` → rc2; `[ -d ]` → `dir_digest`; else `file_sha` | n/a |
| `file_sha` override def | Q:722-725 | `s18_path_ok && [ -f ] || return 1`, then `sha256sum` | returns 1 on specials; **no timeout** |
| `dir_digest` override def | Q:727-734 | `s18_path_ok && [ -d ] && s18_scope_ok || return 2`; subshell `find -type f … sha256sum` | returns 2 on symlink/special; **no timeout** |
| pin, stage 1 | Q:498 | `pin_sha=$(content_digest "$ct")` | **unguarded** |
| pin, stage 4 | Q:284 | `now_sha=$(content_digest "$QPATH"); local dig_rc=$?` | **unguarded** (the `dig_rc` read at Q:284 is never reached on failure) |
| ledger pin | Q:340 | `ledger_pin=$(file_sha "$SV_LEDGER")` | **unguarded** |
| ledger re-check | Q:369 | `[ "$(file_sha "$SV_LEDGER")" != … ]` | inside `[`: not errexit-sensitive |
| vault file digest | Q:348 | `vault_sha=$(file_sha "$vp")` | **unguarded** |
| vault dir digest | Q:352 | `vault_sha=$(dir_digest "$vp"); vault_rc=$?` | **unguarded**; the `vault_rc -eq 2` branch at Q:353 is unreachable |
| intro blob | Q:328 | `git cat-file … \| sha256sum \| cut \|\| true` | guarded |
| engine call | Q:1067-1068 | `V_RAW=$(… bash "$VERIFY_BIN" …) \|\| rc=$?` | errexit-safe; **no timeout** |

Git and staging call sites (FACT): `git_tracked` Q:233-235 (`ls-files`), `git_dirty_tracked` Q:237-239, `q_default_ref` Q:257-275 (used by base `s18_second_check` Q:312), pushed checks Q:1130-1146, `git mv` Q:529, `mv` Q:536, `git rm --cached` Q:583, `rm -rf` Q:576, `mkdir -p` Q:523, `sleep` Q:556, `stat` Q:285 and Q:499.

---

## 2. F1 — set -e exits bypass the designed fail-closed branches (High, calibration + exit)

**Mechanism (FACT + bash semantics, INFERENCE on reachability):**
`Q:121` sets `set -euo pipefail`. In bash, a simple assignment whose command substitution fails makes the assignment fail, which triggers errexit (`x=$(false)` exits the shell; `local x=$(false)` does not, because `local` masks the status). The following plain assignments are errexit-sensitive:

1. `Q:284` — `now_sha=$(content_digest "$QPATH"); local dig_rc=$?`. The `dig_rc -eq 2` branch that emits `pin=FAIL symlink-present-in-quarantine` (Q:290-291) is therefore unreachable. Any non-zero from `content_digest` exits the process.
2. `Q:498` — `pin_sha=$(content_digest "$ct")`. Exits before stage 2, so no RESULT for that target.
3. `Q:340` — `ledger_pin=$(file_sha "$SV_LEDGER")`.
4. `Q:348` — `vault_sha=$(file_sha "$vp")`. If the vault copy is missing, `file_sha` returns 1 (Q:723) and the shell exits. The designed `vault-sha-mismatch` evidence (Q:350) is never written.
5. `Q:352` — `vault_sha=$(dir_digest "$vp"); vault_rc=$?`. A vault directory with a symlink returns 2 (Q:729 via `s18_scope_ok`), the shell exits with 2, and the `vault_rc -eq 2` branch (Q:353) never runs.

**Observable consequences (INFERENCE, UNVERIFIED):**
- Stage-1 crash (Q:498): the target gets no RESULT; the run ends with no SUMMARY (Q:665-667 never reached); exit code = 1 or 2 depending on the digest status; later targets in a `--list` are never processed.
- Stage-4 crash (Q:284, Q:348, Q:352): the staged copy stays in quarantine as desired, but the output has no `stage5 ABORTED`, no `RESULT ABORTED`, and no SUMMARY. The exit code is the raw digest status (1 or 2), so an operator cannot tell it from a usage error (exit 2, Q:159/Q:88-92).
- No false success: none of these paths reaches `rm` (Q:576), so no content is deleted on a crash path.

**Exit code contract violated:** Q:88-92 documents exactly `0,1,2,3,4` and "No other codes". Exit 2 is documented for usage only (Q:89, Q:159). A runtime exit 2 is a contract violation.

**Reachability (INFERENCE, UNVERIFIED):**
- Q:284 reachable by a tamper during hold that replaces the staged file with a FIFO or symlink, or inserts a symlink into a staged directory. The `SOUJI_Q_TEST_HOOK` hook (Q:546-551) can express this.
- Q:348 reachable by deleting the vault copy during hold (the ledger row still exists).
- Q:352 reachable by inserting a symlink into a vault directory during hold. Stage 4 re-derives the vault digest itself (Q:352), so nothing before stage 4 covers this window.
- Q:498 reachable by any top-level target the engine classifies SAFE that cannot be hashed (F2).

**Fix requirement (proposal for L1):** every digest in the table above must be `if x=$(…); then … else <fail-closed branch> fi` or `x=$(…) || rc=$?`. Map: stage-1 digest failure → NOT-AUTHORIZED with a named reason and RC=3 (nothing staged yet). Stage-4 digest failure → `pin=FAIL …` → ABORTED, RC=3, copy stays. Exit 2 must not occur after the first mutation.

---

## 3. F2 — special-file (FIFO, socket, device, unreadable) handling (High, calibration)

**Current behaviour (FACT, by reading):**
- No file-type pre-check exists in `flow_one` (Q:1100-1120), `s18_flow_one` (Q:405-599), or `s18_second_check` (Q:280-389). The only pre-checks are existence (Q:469), symlink (Q:473-476), collision (Q:477-480), and secret shape (Q:438-441).
- `file_sha` (Q:722-725) guards with `s18_path_ok "$1" && [ -f "$1" ] || return 1`. This prevents `sha256sum` from opening a FIFO (which would block). It does not classify the target. It returns 1, and the caller's errexit (F1 item 2) ends the process.
- The engine classifies specials as SAFE. `try_stale` (E:767-787) checks only scratch-type basename (E:179-195: `*.out|*.log|*-draft.*|checkpoint…`), `ls-files` emptiness, mtime age (E:779-781) and unreferenced basename (E:782). It never checks `-f`/`-p`/`-S`/`-b`/`-c` nor readability. `s18_old_scope` (E:739-753) uses only `stat`. Conclusion: a FIFO named `*.out` or an unreadable regular file, older than `STALE_DAYS`, untracked, unreferenced, at a top-level path, gets **SAFE(stale)** from the engine (INFERENCE from code, UNVERIFIED).
- In the quarantine that verdict proceeds: `QVERDICT stage1` is emitted (Q:414) and then `pin_sha=$(content_digest "$ct")` at Q:498 exits 1 (F1). The target is not staged, not deleted, and not reported. The run ends.
- Inside a directory, specials are refused by the engine (`s18_scope_ok` E:510-523 → NOT-SAFE secrets-refusal) and by the quarantine (`dir_digest` Q:729). Only top-level specials reach the pin.
- At stage 4, a special that replaces the staged regular file is caught by `content_digest` → `file_sha` (Q:723) → crash (F1 item 1).

**Hang analysis (INFERENCE):** A hang would require `sha256sum` to open a FIFO. That is prevented by the `-f` guard at Q:723 and by `find -type f` (Q:731) in directories. The engine has the same guard at E:528 and E:534. I found no reachable hang in the quarantine digest path. Two unguarded open-capable paths remain for UNVERIFIED evaluation: (a) the engine `rg` walk in `count_live_refs` (E:697, `rg -l --hidden --no-ignore --text … .`), which I believe skips non-regular entries; (b) `git status --untracked-files=all` in `try_pushed` (E:658), whose handling of FIFOs is unknown to me.

**Fix requirement (proposal for L1):**
1. Add a classification step in `s18_flow_one` after Q:476 and before Q:482: refuse anything that is not `-f` or `-d` (and, for `-f`, not readable with `-r`) with `block_one "$raw" special-file "<type>"`. Emit RC=3 and continue to the next target. This must run before Q:498.
2. Keep the Q:723 guard as defence in depth, but make it unreachable from the flow.
3. Engine-side refusal (E:767-787) changes the receipt verdict shared by any caller of the engine. Route that to C1 review; the quarantine-side refusal alone closes the operator-visible crash.

---

## 4. F3 — timeout (High-latent)

**Facts:**
- `grep -n timeout` over `tools/souji-quarantine.sh`, `tools/cand-merge-verify.sh`, and `tools/souji-round9-selftest.sh` returns no timeout binding. The only `timeout` text is in prose elsewhere; no `timeout` command is invoked.
- The per-target work that can be unbounded, in order of cost:
  1. Engine invocation `bash "$VERIFY_BIN"` at Q:1067-1068, called twice per target: stage 1 (Q:413) and stage 4 prong 1 (Q:560). Each invocation runs `scan_worktrees` over `"$SHOKUNIN_ROOT"/*` (E:967-989, called at E:1311), `git worktree list` per sibling repo, plus `count_live_refs` (`rg`, E:697) for stale candidates, plus `git log --branches --not --remotes` (E:658-676 region).
  2. Digest reads of regular files of arbitrary size: `file_sha` (Q:722-725) and `dir_digest` (Q:727-734).
  3. Git read probes: Q:306, Q:317, Q:328, Q:1113-1114, Q:1130-1146.
- Staging writes: `mkdir` Q:523, `git mv` Q:529, `mv` Q:536, `rm -rf` Q:576, `git rm --cached` Q:583.

**Proposal (L1 decision points):**
- **Bound (recommended):** the engine call at Q:1067-1068; digest reads at Q:284, Q:340, Q:348, Q:352, Q:498, and the bodies of Q:722-734; git read probes listed above.
  - Engine rc 124 is already handled as ERROR (Q:1069-1070, Q:1076-1077). Stage 1 → `block_one engine-error`. Stage 4 → `P1_VERDICT=ERROR` → FAIL (Q:1127-1129 in the flow's second_check). Adding `timeout` at Q:1067 needs no new fail-closed branches.
  - Digest timeout → `pin=FAIL digest-timeout` at stage 4 and NOT-AUTHORIZED at stage 1. Not PASS.
  - Use `timeout --kill-after=` with a bounded value and do not use `--foreground`. Without `--foreground` GNU timeout signals the child's process group, which covers `git`/`rg` under the engine.
  - Add `</dev/null` to the bounded children. Flag: `run_mode` reads the list on fd 0 (Q:636-640), and every child inherits it. The engine does not read stdin today (verified by reading all `read` sites in E), so this is latent, not active.
- **Do not bound (recommended):** `mkdir`, `git mv`, `mv`, `rm -rf`, `git rm --cached` (Q:523-583). A timeout that kills `mv` mid-tree can leave a split state. A rename within one filesystem is one syscall, but a cross-device `mv` copies first, so a kill can leave a partial copy with the source still present. `.ufo-quarantine` is inside the repo; a btrfs subvolume or bind mount inside the repo would make `mv` a copy (INFERENCE, check `stat -c %d` across the repo and quarantine paths before relying on rename atomicity). On timeout or failure after a move has begun, the policy is STAY + report, with no automatic cleanup of partial copies.
- **Do not bound:** `sleep $HOLD` (Q:556). It is intended, and see F5 for signal handling.
- Validate the new knob like the existing ones (Q:1549-1550): non-negative integer, `usage_err` otherwise. Also expose it to the selftest through a short value.

---

## 5. F4 — `--list` malformed rows fail after mutation (Medium)

- `run_mode` processes each row in order: the loop at Q:640-656 calls `flow_one` per row at Q:654.
- Malformed rows are detected inside the loop: `usage_err "list row without receipt column"` at Q:649 and `usage_err "list row malformed"` at Q:652.
- So a file `valid-row / malformed-row` stages or deletes the first target (Q:654, then mutations in `s18_flow_one`) and then exits 2 at Q:652. No SUMMARY. The contract (Q:21-22) says malformed rows are usage errors (exit 2), and selftest U5 (Q:1477-1478) only covers a file whose first row is malformed, which never mutates.
- Fix: pre-validate the whole list before the first `flow_one` call, using the same parse as Q:640-653. Then Q:649/Q:652 are pre-mutation usage errors. Add a selftest with `valid, malformed` and assert no mutation.

---

## 6. F5 — signals and exit traps (Medium)

- `ERRTMP` is created at Q:1519 and removed by `trap 'rm -f -- "$ERRTMP"' EXIT` at Q:1520. The selftest replaces that trap at Q:1311 with a version that also removes `$ST_TMP`.
- No INT/TERM/HUP trap exists. A signal during the hold (Q:556) ends the shell with a 128+n status. The staged copy stays, there is no `RESULT` and no `SUMMARY`, and the code is not in the documented set (Q:88-92).
- `RC` is only set at: Q:399 (block_one), Q:525, Q:532, Q:539 (STAGE2-FAILED), Q:571 (ABORTED), Q:580 (rm ABORTED). Exit 1 is returned by `exit 1` at Q:611 (engine missing) and by errexit. Exit 4 at Q:624. The final exit at Q:1569 is `exit "$RC"`.
- Fix proposal: trap INT/TERM/HUP to emit `QSTAGE stage5 <raw> ABORTED "interrupted left-in-quarantine qpath=…"` and `RESULT ABORTED` for the in-flight target only if `QPATH` has been staged; set RC=3; exit 3. Before staging, emit nothing mutating and exit 3. The trap must not run deletion.

---

## 7. F6 — engine authority and doc drift (Medium, calibration)

- Header says the receipt authority is `tools/souji-verify.sh` (Q:5-7, Q:109-110). Code selects `tools/cand-merge-verify.sh` whenever it sits next to this script (Q:134-138). That file's own header calls it a "round-10 S15 composed candidate" (E:481-485).
- Consequence: the quarantine's SAFE/NOT-SAFE authority is the candidate, not the documented engine. Reviewers must treat the candidate's behaviour as the real one.
- Header relative-path rule (Q:16: "relative paths resolve from cwd") is contradicted by code: Q:409 and Q:1102 resolve relative targets against `$REPO`. This needs a decision. Safest for removal authority is documenting repo-relative and refusing relative paths, but any change must keep the D2/N1/N2/N3/N4/P1/P2/SKIP1 fixtures passing (they pass repo-relative targets such as `local/unpushed.txt`, `keep/pushed.txt`, `wt-inside`; see Q:1345, Q:1365, Q:1373, Q:1378, Q:1391, Q:1412, Q:1435).
- Header usage name `tools/souji-quarantine.impl-01.sh` (Q:12) does not match the file name `souji-quarantine.sh`.

---

## 8. F7 — dead and broken code (Low, maintainability)

Live from `run_mode` (verified by reading the call graph): `flow_one` Q:1100, `s18_flow_one` Q:405, `s18_second_check` Q:280, `second_check` Q:1122, `run_verify` override Q:1061, `ledger_row_for` override Q:1087, `resolve_default_ref` Q:1042, `s18_q_storage_ok` Q:1054, `s18_path_ok` Q:687, `s18_scope_ok` Q:705, `is_hex64` Q:720, `s18_row_parse` Q:736, `s18_row_ok` (called from Q:902), `file_sha`/`dir_digest` overrides Q:722/Q:727, `content_digest` Q:196, `q_default_ref` Q:257, `canon_path`, `emit`, `block_one`, `git_tracked`, `git_dirty_tracked`, `is_secret_shaped`.

Dead (no caller reachable from `run_mode`):
- Q:761 `load_ledger`, Q:774 `ledger_lines`, Q:783 `try_obsidian`, Q:806 `try_ledger`, Q:832 `s18_snapshot_equal`, Q:846 `try_pushed`, Q:879 `count_live_refs`, Q:905 `s18_repo_gitdir`, Q:916 `s18_is_repo_root`, Q:930 `s18_old_scope`, Q:946 `s18_scope_unreferenced`, Q:958 `try_stale`, Q:980 `s18_evaluate_worktree_one`, Q:1020 `evaluate_path`, Q:1158 `scan_worktrees`, Q:1182 `_wt_record`, Q:1195 `evaluate_worktree`.
- Shadowed base definitions: Q:184-185 `file_sha`, Q:186-194 `dir_digest`, Q:212-229 `run_verify`, Q:241-255 `ledger_row_for`.
- Broken references in dead code: Q:821 calls `s18_try_ledger` and Q:826 calls `finish_mismatch`, neither defined in this file. Q:960 calls `scratch_type`, defined only in the engine (E:179). Q:1038 calls `s18_evaluate_path`, defined only in the engine (E:403). Q:1091-1094 are live; do not remove them.

Cutover rule (`Default clean cutover ... remove obsolete code`) makes the dead block in-scope for deletion once L1 confirms no caller. Removing it is not required for the F1-F5 fixes and can be a separate step.

---

## 9. F8 — coverage gaps (Medium)

Quarantine selftest (`Q:1304-1515`) cases: G1, D1-D3, N1-N4, P1-P3, SKIP1, L1, A1, U1-U5, H1-H3, plus R9 quarantine cases. Missing:

| Gap | Why it matters | Suggested fixture (for L1; not run) |
|---|---|---|
| top-level FIFO named `*.out`, aged, untracked | F2 crash path | `mkfifo` under mktemp, `touch -d '3 days ago'`, `--hold 0`; expect `RESULT NOT-AUTHORIZED special-file`, RC=3, and a later target still processed |
| unreadable aged regular file | F2 crash path (`sha256sum` rc1) | `chmod 000` on a mktemp file; expect `NOT-AUTHORIZED unreadable` |
| hook replaces staged file with FIFO | F1 stage-4 crash via Q:284 | `SOUJI_Q_TEST_HOOK` that `rm`s and `mkfifo`s qpath; expect `ABORTED`, `pin=FAIL`, RC=3, copy present |
| hook plants symlink in staged directory | F1 Q:284 exit 2 | dir target + hook `ln -s`; expect `ABORTED`, RC=3 |
| vault copy deleted during hold | F1 Q:348 crash | hook removes `$ST_TMP/vault/obs.txt`; expect `ABORTED` with `vault-sha-mismatch`, RC=3, vault unchanged |
| vault directory with symlink during hold | F1 Q:352 exit 2 | moved-to-obsidian dir row; hook adds symlink to vault dir; expect `ABORTED`, RC=3 |
| digest timeout | F3 | PATH shim for `sha256sum` that sleeps, as R9:196-199 already does; with a short digest timeout expect `pin=FAIL digest-timeout`, RC=3, copy retained, wall time bounded |
| engine timeout | F3 | `SOUJI_VERIFY_BIN` pointing to a sleeping stub; expect `NOT-AUTHORIZED engine-error` at stage 1, RC=3, no mutation |
| list `valid, malformed` | F4 | expect RC=2 and no staged or deleted target |
| SIGINT during hold | F5 | send INT to the tool during hold; expect copy retained, RESULT ABORTED, RC=3 |
| same-day re-run after ABORTED | F9 | expect `quarantine-collision` NOT-AUTHORIZED; documents the operability limit |

R9 currently has no FIFO or symlink quarantine fixture (grep for `fifo|mkfifo|symlink|ln -s` in R9 returns none).

---

## 10. Restore-vs-stay policy (baseline) and regression constraints

**Baseline policy:** Q:68-72 says on failure the copy STAYS in quarantine and the target is reported ABORTED. Implemented at Q:565-573 (second check FAIL) and Q:576-581 (rm failure). Stage-2 failure (Q:523-542) leaves nothing moved, so there is nothing to restore. There is no restore code path in the file.

**Recommendation:** keep stay-and-report. Restoring after an inconclusive check would be a second mutation without verification, and it could collide with a path reused in the meantime. Invariant for the fix: **inconclusive (timeout, crash-prone digest, engine error) → never delete; stage 4 → ABORTED with the copy kept; stage 1 → NOT-AUTHORIZED with no move.**

**Regression constraints (assertions that exist today and must keep passing):**
- A1 (Q:1451-1465): rc=3, `RESULT ABORTED` token for `keep/obs2.txt`, evidence contains `digest-mismatch`, staged copy present, vault untouched. Any new timeout token must not change `digest-mismatch`.
- P1 (Q:1390-1409): `QSTAGE stage2 … git-mv`, `QVERDICT stage4-second … PASS`, original gone, quarantine dir rmdir'd, porcelain still lists `keep/pushed.txt` (staged deletion via `git rm --cached` Q:583).
- P2 (Q:1411-1420): `prong1=SAFE(stale) binding`. P3 (Q:1422-1432): `prong1-tolerated class-not-path-local`.
- D1-D3, N1-N4, SKIP1, L1 tokens (Q:1333-1449), including `NOT-AUTHORIZED\tunreachable`, `dirty-tracked`, `receipt-mismatch`, `DRY-RUN-PASS\tpushed`, `DRY-RUN-BLOCKED`.
- U1-U5 (Q:1468-1478): all usage paths exit 2 before any mutation. F4 must keep this.
- G1 (Q:1323-1331): live-fleet guard exits 4 before anything else.
- H1 (Q:1482-1484): regex `git (-C …)? (fetch|push|commit|branch|checkout|reset|rebase)` must count 0 across the file. New git calls must avoid those subcommands.
- H2/H3 (Q:1485-1499): fixtures under `${TMPDIR:-/tmp}`; live `REPO_ROOT` porcelain, LOG.md sha, and `.ufo-quarantine` unchanged.
- R9 quarantine (R9:81-85, 214-226, 231-266): refusal exit 3 with `NOT-AUTHORIZED`; revoked-ledger → `ABORTED` with staged bytes retained; NUL list → rc 2 with no moves; default-ref rollback/missing → rc 3 `default-ref-unverifiable-or-not-ancestor` with staged bytes retained.
- Same-day collision (Q:477-480) remains unchanged; F9 is an operability note, not a fix target.

---

## 11. Proposed final checks for L1 (not run by this seat)

1. `bash -n` on `tools/souji-quarantine.sh` and `tools/cand-merge-verify.sh`.
2. `tools/souji-quarantine.sh --selftest` → exit 0 with zero FAIL, including the R9 runner summary line.
3. `tools/souji-round9-selftest.sh quarantine tools/souji-quarantine.sh` → summary `ROUND9` with zero failures.
4. The F8 fixtures above, each run under `timeout 120` so the test itself cannot hang, with expected tokens and exit codes as listed.
5. Exit-code audit: every reachable exit is in `{0,1,3,4}`, and exit 2 occurs only before the first `QSTAGE`/`QVERDICT` mutation line.
6. Grep H1 regex count stays 0.
7. Optional lint: `shellcheck tools/souji-quarantine.sh` if installed. I did not check for it or install it.

---

## 12. Limitations

- No execution: all claims about runtime behaviour (crashes, exit codes, FIFO handling, rg/git behaviour on FIFOs) are INFERENCE or UNVERIFIED until L1 runs the fixtures.
- Bash errexit semantics for `x=$(cmd)` with `set -e` are stated from bash behaviour, not demonstrated here.
- I did not verify git's handling of untracked FIFOs or ripgrep's handling of FIFOs during directory walks.
- The baseline git history was not consulted (no git commands run). The file read at tag `56F5` is the working copy under review.
- Sibling variants (`souji-quarantine.impl-*.sh`, `cand-*-quarantine.sh`, `souji-quarantine.r9-s18.sh`) were not audited; several share this code.
- Operator sweep directory and secrets were not read.

## 13. Tool installs

None. No tool was installed, upgraded, or executed by this seat.
