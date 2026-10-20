STATUS: DONE — 17 status decision sites (15 literal `git ... status` lines + 2 mediated helper calls) across the four governed tools; only the census one decides a clean row (C1/D1 holds statically); no mode-less status call can flip a verdict to SAFE; the D1-class remainder is receipt/evidence-only.

# ScoutStatusCallSites — every `git ... status` in the four governed tools

Round 17 / WAVE 1 / lane `souji-shokunin`, base `5fa6017ddcae9f6bd4412df44765f6360cb16294` (branch `master`).
Pure static recon: `git show` bytes only. Nothing was executed against any repository; no census, verify, vault or quarantine run.

## Question

For `tools/souji-census.sh`, `tools/souji-verify.sh`, `tools/souji-vault-verify.sh`, `tools/souji-quarantine.sh`: list every `git ... status` invocation, its untracked-files mode, whether its result decides a clean/dirty/SAFE verdict, and whether repo-local (`$GIT_DIR/config`, an included file, or `config.worktree`) `status.showUntrackedFiles=no` can therefore produce a false clean/SAFE. Mark C1 scope vs D1-class gaps elsewhere.

## Revision bindings (observed)

```
git show 5fa6017:tools/souji-census.sh        | sha256sum  -> 64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c
git show 5fa6017:tools/souji-verify.sh       | sha256sum  -> 9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd
git show 5fa6017:tools/souji-vault-verify.sh | sha256sum  -> f9e778ca478c7aa8b33234ee793030df631c1b9fcebc942b1ff41d0008ed9c5b
git show 5fa6017:tools/souji-quarantine.sh   | sha256sum  -> df4075112c36bae804b98766c4eb66b0e5b2b80b76d7333475ede27b06b168c4
git diff --stat 5fa6017 -- <those four>      -> (empty)
```

`64a60fd0…` matches C1's declared census digest. Worktree bytes equal the pinned revision for all four tools.

## Semantics used (documented, not executed)

git 2.56.0 local man pages:

- `git-status(1)`: `-u` modes are `no|normal|all`; "When -u option is not used, untracked files and directories are shown (i.e. the same as specifying normal)… The default can be changed using the status.showUntrackedFiles configuration variable."
- `git-status(1)` (under `--ignored`): "The --untracked-files=no flag or the status.showUntrackedFiles=no config (see above for both): indicate that git status should not report untracked files."
- `git-status(1)` (`--porcelain`): the *format* "will remain stable … regardless of user configuration". That sentence is about format; it does not freeze the entry set (same reading as r16 lesson S044).
- `git-config(1)` FILES: `$GIT_DIR/config` is read; `$GIT_DIR/config.worktree` "is only searched when extensions.worktreeConfig is present"; `include.path` / `includeIf.*.path` pull files in place; "last value found" wins.

Therefore: a `status` call with no `-u`/`--untracked-files` honours the key from repo config (direct, included, or worktree config when enabled). A call that passes `--untracked-files=all` is not suppressible by that key.

Host-level note: sibling `ScoutFleetUntrackedCfg.md` (this wave) observed the key absent from all 21 lanes + fleet root and no `extensions.worktreeConfig`, so the exposure is latent here; it is a control defect, not a live fleet event.

## Complete inventory — 17 sites (15 literal + 2 mediated)

`live?` = reachable from the script's single dispatch. `decides` = what the status result can change.

| # | site | function | untracked mode | live? | decides | false clean / SAFE? | class |
|---|---|---|---|---|---|---|---|
| 1 | census `:1037` | `count_dirty` `:1021` | **none** (`status --porcelain --ignore-submodules=all -- .` + pathspec excludes) | yes | `dirty` column `:1205`, `wt-dirty` flag `:1162-1165`, `clean` flag `:1226-1239` | **false clean row: YES** (no SAFE concept) | **C1/D1 (claim scope)** |
| 2 | verify `:322` | `evaluate_repo_root` `:318` | **none** | yes | receipt `dirty` vs `none` `:325-329`; verdict pinned `NOT-SAFE` `:324` | false `dirty=0` receipt/evidence; **not** SAFE | D1-class elsewhere (evidence) |
| 3 | verify `:366` | legacy `evaluate_worktree` `:333` | **none** | **no** — redefined at `:1004`, single dispatch `:1311` | would set receipt `dirty`/`none`; verdict `NOT-SAFE` | n/a (dead) | dead site |
| 4 | verify `:658` | `try_pushed` `:655` (this later def is the live one) | **`--untracked-files=all`** + `--ignored=matching` | yes | SAFE(pushed) eligibility `:683` | no — mode pinned | immune |
| 5 | verify `:820` | `s18_evaluate_worktree_one` `:789` | **none** | yes (via `:1004` → `evaluate_path` `:829`) | dirty count / receipt `dirty` vs `none` `:824-826`; verdict starts `NOT-SAFE` `:793`, SAFE only absent-dir branch `:816` | false clean evidence; **not** SAFE | D1-class elsewhere (evidence) |
| 6 | verify `:923` | `flow_one` `:909` in `if S18_KIND = quarantine` `:850` | none (via `git_dirty_tracked`) | **no** — `S18_KIND=verify` `:487`; helper also undefined | would block dirty-tracked targets | n/a (dead) | dead site |
| 7 | vault `:488` | `evaluate_repo_root` `:484` | **none** | yes | receipt `dirty` vs `none` `:491-493`; verdict pinned `NOT-SAFE` `:490` | false `dirty=0` receipt/evidence; **not** SAFE | D1-class elsewhere (evidence) |
| 8 | vault `:532` | legacy `evaluate_worktree` `:499` | **none** | **no** — redefined at `:1192`, single dispatch `:1627` | would set receipt; verdict `NOT-SAFE` | n/a (dead) | dead site |
| 9 | vault `:846` | `try_pushed` `:843` | **`--untracked-files=all`** + `--ignored=matching` | yes | SAFE(pushed) `:871` | no — mode pinned | immune |
| 10 | vault `:1008` | `s18_evaluate_worktree_one` `:977` | **none** | yes (via `:1192`) | dirty count / receipt `:1012-1013`; verdict starts `NOT-SAFE` `:981`, SAFE only `:1004` | false clean evidence; **not** SAFE | D1-class elsewhere (evidence) |
| 11 | vault `:1111` | `flow_one` in `if S18_KIND = quarantine` `:1038` | none (via helper) | **no** — `S18_KIND=vault` `:677`; helper undefined | would block dirty-tracked targets | n/a (dead) | dead site |
| 12 | quarantine `:220` | `git_dirty_tracked` `:219` | **none** (`status --porcelain -- "$2"`) | yes — callers `:469` (stage gate) and `:1222` (pre-move gate) | blocks `dirty-tracked` only when the path is tracked (`:468`, `:1221`); never a SAFE verdict | limited: tracked file dirt is still shown under `-uno`; a tracked **directory** whose only dirt is untracked members passes the gate (moves with the dir — inference) | D1-class elsewhere (low) |
| 13 | quarantine `:919` | `try_pushed` `:917` | **`--untracked-files=all`** + `--ignored=matching` | yes | SAFE(pushed) `:943`, consumed by stage-4 `V_VERDICT = SAFE` gate `:397` | no — mode pinned | immune |
| 14 | quarantine `:1080` | `s18_evaluate_worktree_one` `:1050` | **none** | yes (before the quarantine-kind block, top-level) | dirty count / receipt `:1084-1085`; verdict starts `NOT-SAFE` `:1053`, SAFE only `:1076` | false clean evidence; **not** SAFE | D1-class elsewhere (evidence) |
| 15 | quarantine `:1424` | `run_selftest` | **none** | yes under `--selftest` | paired with `:1598` for live-lane porcelain-count equality | sentinel sensitivity only (untracked churn invisible); no verdict | D1-class elsewhere (test) |
| 16 | quarantine `:1515` | `run_selftest` P1 | **none** | yes under `--selftest` | asserts the moved tracked path appears in porcelain | none — a staged deletion of a tracked path is reported under any `-u` mode | unaffected |
| 17 | quarantine `:1598` | `run_selftest` | **none** | yes under `--selftest` | as `:1424` | sentinel sensitivity only | D1-class elsewhere (test) |

Recount: census 1 literal (`:1037`); verify 4 literal (`:322`, `:366`, `:658`, `:820`) + 1 mediated (`:923`, dead); vault 4 literal (`:488`, `:532`, `:846`, `:1008`) + 1 mediated (`:1111`, dead); quarantine 6 literal (`:220`, `:919`, `:1080`, `:1424`, `:1515`, `:1598`) with mediated callers `:469` and `:1222` into the `:220` helper. That is **15 literal + 2 mediated = 17 rows**.

## Findings

**F1 (observed, high). C1/D1 holds at 5fa6017.** The census has exactly one status invocation, `count_dirty` `:1035-1041`, and it passes no untracked-files mode. The config scan has arms only for `include:path|includeif:path` `:634`, `core:excludesfile|core:attributesfile` `:650`, `core:worktree` `:658`, `extensions:worktreeconfig` `:666`; a `status.showUntrackedFiles` key falls through the `case` `:633` with no action, so it is neither refused nor neutralized. `guard_wt_config` `:696-710` does scan `config.worktree`, but again only forwards keys into `scan_config_file`, which ignores `status.*`. Census disables global/system config and clears inherited `GIT_*` (`:150-154`) but repository config is exactly what git still reads. Consequence chain: suppressed untracked entries → `st` empty → `count_dirty` prints `0` (`:1045`) → `census_one` adds no `dirty` flag (`:1226-1228`) and appends `clean` because no problem flag fired (`:1232-1239`); `worktree_extra_flags` adds no `wt-dirty` (`:1162-1165`). All three D1 vectors are reachable by construction: direct `$GIT_DIR/config`, `include.path` target, and `config.worktree` when `extensions.worktreeConfig` is true. C1's prescribed fix (explicit `--untracked-files=normal`) is not present at this revision.

**F2 (observed, high). No mode-less site outside the census can flip a verdict to SAFE.** The only status-dependent SAFE receipt in the suite is `pushed`, and all three live gates pin the mode: verify `:658`, vault `:846`, quarantine `:919` all pass `--untracked-files=all --ignored=matching` before returning SAFE (`:683`, `:871`, `:943`). The remaining live mode-less calls sit behind a hard `R_VERDICT=NOT-SAFE` initialization (verify `:324`, `:793`; vault `:490`, `:981`; quarantine `:1053`) whose only SAFE arm is the absent-directory `metadata-prune` branch reached earlier (verify `:816`, vault `:1004`, quarantine `:1076`). Quarantine additionally refuses any non-SAFE stage-1 verdict (`:397`). So D1 outside the census is a false **receipt/evidence** class ("NOT-SAFE(none) / dirty=0"), operator-facing, not a deletion hazard.

**F3 (observed). Four literal sites are unreachable; the dead quarantine-mode blocks are a latent fail-open trap.** `verify:366` and `vault:532` are the legacy `evaluate_worktree` definitions, overwritten by `:1004` / `:1192`; each file has a single dispatch at the end (`verify:1311-1316`, `vault:1627-1632`), so the later definition always wins. `verify:923` and `vault:1111` are inside `if [ "$S18_KIND" = quarantine ]` blocks (`verify:850`, `vault:1038`) while the literals are `S18_KIND=verify` (`:487`) and `S18_KIND=vault` (`:677`). The dead blocks also call `git_dirty_tracked`, `git_tracked`, `block_one`, `s18_flow_one` and `s18_second_check`, none of which is defined in verify/vault (the helper survives only in `souji-quarantine.sh:219`). If such a block were ever activated, the dirty gate would fail open: "command not found" yields empty `status`, so the `-n "$status"` test passes. No current exposure; worth deleting or guarding if the composed files are edited near it.

**F4 (observed). Quarantine's selftest sentinels are the only test-strength exposure.** `:1424` / `:1598` compare live-lane porcelain *counts* before and after; with the key set, untracked churn is invisible to both, so the H3 "live lane untouched" check can pass while untracked files changed. `:1515` is not exposed: it asserts the moved *tracked* path appears in porcelain, which `-uno` does not hide.

**F5 (inference). The quarantine `dirty-tracked` gate is not equivalent to `try_pushed`.** `git_dirty_tracked` `:220` is consulted only for tracked paths, and untracked suppression cannot hide tracked-file modifications (deletions/modifications still print). For a tracked directory whose extra content is untracked files, the gate sees clean and the flow proceeds to `git mv` of the directory. Directory renames carry untracked members into quarantine, i.e. preservation, not loss [INFERENCE: git-mv directory semantics were not executed here]. If the intended doctrine is the same "no untracked content in the target" rule as `try_pushed`, `:220` is inconsistent and should pin `--untracked-files=all` too; if not, document the asymmetry.

**F6 (observed). Global/user config is live in verify/vault/quarantine but not in census.** Those three tools inherit the caller's environment and do not disable global/system config, so a user-level or `GIT_CONFIG_*`-injected `status.showUntrackedFiles=no` produces the same receipt/evidence effects at sites 2, 5, 7, 10, 12 (and the selftest sentinels). Census clears all inherited `GIT_*` and sets `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null` (`:150-153`), so its only vector is repository-local/included/config.worktree — matching C1's wording.

## Verdict

**C1/D1: holds statically.** One flag is missing at exactly one place (`census:1037`); the key is accepted by the census's config scan through all three declared carriers.

**Elsewhere: partial (D1-class, non-SAFE).** Six live mode-less sites are exposed: verify `:322`, `:820`; vault `:488`, `:1008`; quarantine `:1080` (all receipt/evidence, never SAFE), plus quarantine `:220` through `:469`/`:1222` (block-gate, tracked paths only). Two selftest sentinels (`:1424`, `:1598`) lose sensitivity. The safety-critical SAFE(pushed) gates are correctly pinned and immune.

## Smallest fixes (advisory)

1. **C1, as claimed:** add `--untracked-files=normal` to the `status` call at `census:1037`. One edit covers both consumers (`census_one:1205`, `worktree_extra_flags:1162`); `normal` keeps the documented one-line untracked-directory collapse. (`-c status.showUntrackedFiles=normal` among the existing `-c` args would also work, but the explicit `-u` is the declared control.)
2. **Verify/vault evidence:** add `--untracked-files=normal` (or `=all` to match `try_pushed`) at verify `:322`, `:820` and vault `:488`, `:1008`. Verdicts do not change; the `dirty=` receipt and evidence become truthful.
3. **Quarantine gate:** decide the doctrine for `git_dirty_tracked` `:220`; if it is the `try_pushed` rule, add `--untracked-files=all`; otherwise comment the tracked-only intent.
4. **Quarantine selftest:** add `--untracked-files=normal` at `:1424` and `:1598` so H3 remains sensitive.
5. **Dead sites:** delete or clearly quarantine `verify:333-380`/`:850-965`-adjacent dead block and `vault:499-547`/`:1038-...`; at minimum do not let the undefined `git_dirty_tracked` call be activated without its helper.

## Residual unknowns

- No execution was permitted here: directory-rename behaviour for untracked members (F5) is the only inference; every other claim above is read from the pinned bytes and the local git 2.56.0 man pages.
- Whether the r17 hygiene fixture exercises the `include` and `config.worktree` carriers cannot be checked yet: `tests/fixtures/r17-census-hygiene.py` does not exist in this worktree (`ls`: ENOENT), and no census diff exists against 5fa6017.
- Global/system config and invocation environment were not enumerated (sibling scout covered the repo-local state; F6 is a code-scope statement, not a fleet measurement).
- `--porcelain` entry count is not config-independent even though the format is; S044's quote is format-only and does not support suppressing the `-u` concern.

## Tooling installed/updated

None. No pacman, uv, npm or cargo transaction; no file written except this report.
