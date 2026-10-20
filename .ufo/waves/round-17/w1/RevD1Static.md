STATUS: DONE — D1 is real at 5fa6017 in every config channel I could construct, `--untracked-files=normal` closes all of them, and the prescribed fix is safe on neighbours; three implementation constraints (option form, doc wording, exact-count fixture assertions) and one adjacent same-class defect in `souji-verify.sh` to route.

Verdict on C1-D1: **premise holds** (the false clean is reproducible with the real tool, not just by reading), **fix design holds** (CLI wins over repo config, includes and `config.worktree`; no whole-run abort; `all` repos deflate to the documented collapse), **claim text needs the additions in R1/R4**, and the census doc at `:35-36`/`:57-58` becomes factually wrong unless reworded.

Scope note: no lane file was edited. All execution used throwaway repos under `/var/tmp/souji-r17-RevD1Static/` (fleet, fleet2, fleet3, big); `souji-census.sh` was run against those roots only, never a real directory. `census/round-17/run-matrix.py` and `tests/fixtures/r17-census-hygiene.py` do not exist at 5fa6017 (`census/round-17/` is absent), so the claim's counting command cannot be exercised yet. Nothing installed; host git 2.56.0 and python3 were sufficient.

## F1 [high, confirmed] Base census emits a false `clean` row for `status.showUntrackedFiles=no`/`false` — every config channel

`count_dirty` (`tools/souji-census.sh:1021-1049`) runs

```
git -C "$1" --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null \
  -c core.excludesFile="$ex" -c core.attributesFile="$at" \
  status --porcelain --ignore-submodules=all -- . <excludes>          # :1037
```

with no untracked-files mode. Real census run (base script, `--root` on a sandbox fleet; each repo has one commit, `refs/remotes/origin/master` at it, one untracked file plus a 3-file untracked directory):

| repo (sandbox) | config source | base `dirty` / flags | with `--untracked-files=normal` | forced count |
|---|---|---|---|---|
| `t-local-no` | `.git/config` `status.showUntrackedFiles=no` | **0 / clean** | **2 / dirty** | 2 |
| `t-inc-no` | `include.path` → `[status] showUntrackedFiles = no` | **0 / clean** | **2 / dirty** | 2 |
| `t-wtc-no` | `extensions.worktreeConfig=true` + `config.worktree` `…=no` | **0 / clean** | **2 / dirty** | 2 |
| `t-local-all` | `.git/config` `…=all` | 4 / dirty | 2 / dirty | 2 |
| `clean-shokunin` | unset | 0 / clean | 0 / clean | 0 |

Plus, separately measured: `includeIf "gitdir:…"` → `base=0 forced=1`; boolean spelling `…=false` → `base=0 forced=2` (git docs: `false` is accepted as `no`).

Reproduce (base arm):
`HOME=<sandbox>/home TMPDIR=<sandbox>/tmp bash tools/souji-census.sh --root <sandbox>/fleet`
output rows include
```
…/fleet/t-local-no	1	0	0	0	…	clean
…/fleet/t-local-all	1	0	4	0	…	dirty
```
Changed arm (copy of the script with the flag sed-inserted at :1037):
```
…/fleet/t-local-no	1	0	2	0	…	dirty
…/fleet/t-local-all	1	0	2	0	…	dirty
…/fleet/t-inc-no	1	0	2	0	…	dirty
…/fleet/t-wtc-no	1	0	2	0	…	dirty
…/fleet/clean-shokunin	1	0	0	0	…	clean
```
Both runs `rc=0`, empty stderr.

Why the config channel reaches `status` at all: the census guard `scan_config_file` (`:594-693`) has entries for `include.path`/`includeIf.path`, `core.excludesFile`, `core.attributesFile`, `core.worktree`, `extensions.worktreeConfig`, and an explicit inert-key list; `status.*` matches no case and no default branch, so a valid `status.showUntrackedFiles` is simply ignored and the repo proceeds. Previously closed channels (so the residual set is exactly the one D1 names): `:145-163` unsets every `GIT_*` variable, pins `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, and exports `GIT_CONFIG_COUNT=2` for fsmonitor/hooks only. I also verified `alias.status` cannot shadow the builtin (install an alias, run `git status` → builtin output), so the config key is the lever.

## F2 [high, confirmed] The flag changes the COUNT, not just the boolean

`dirty` config matrix (same fixture, `--porcelain -- .` line counts):

| value | base | forced `normal` | delta |
|---|---|---|---|
| unset | 2 | 2 | none |
| `normal` | 2 | 2 | none |
| `true` | 2 | 2 | none (docs: `true` == `normal`) |
| `all` | **4** | **2** | −2 (one per extra file in each wholly-untracked dir) |
| `no` / `false` | **0** | **2** | +N (collapse: one line per untracked dir) |

So three observable surfaces change:
1. TSV column 4 `dirty` (`HEADER`, `:170`; emitted at `:1253`).
2. `verdict_flags` column 7: `dirty` added at `:1227-1228`, `clean` added only when no problem flag (`:1232-1239`); `wt-dirty` is *not* in the problem set.
3. `--compare` output: `names=(worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags)` at `:1443`, numeric delta at `:1465`. Measured, fixed-vs-base:
```
t-inc-no	dirty	0	2	+2
t-inc-no	verdict_flags	clean	dirty	changed
t-local-all	dirty	4	2	-2
t-local-no	dirty	0	2	+2
t-local-no	verdict_flags	clean	dirty	changed
t-wtc-no	dirty	0	2	+2
t-wtc-no	verdict_flags	clean	dirty	changed
```
(rc=3; and fixed-vs-fixed rc=0, one header line.)

No aggregate/summary line exists: `emit_census` (`:1308`) prints `HEADER` plus one row per repo and nothing else; grep for totals/clean aggregates found only per-row code. So the count is never printed anywhere else.

Consequence for the claim's counting command: a pre-fix baseline and the changed arm are not directly comparable for repos that set `no`/`false`/`all`; the fixture must compare *counts produced by the same build* or assert exact per-arm values (F6).

## F3 [medium] Option form is load-bearing — space-separated and short forms silently select the wrong mode

Measured on the same fixture (`t-local-no`, 1 top-level untracked file + 3 files in one untracked dir; expected forced count 2):

| spelling | lines | mode actually used |
|---|---|---|
| `--untracked-files=normal` | **2** | normal (correct; `?? ud/` collapsed) |
| `-unormal` | 2 | normal |
| `--untracked-files normal` (space) | **4** | `all`; `normal` became an extra pathspec |
| `-u normal` (space) | **4** | `all` |
| `-u` | **4** | `all` |
| `-uno` | **0** | no → false clean |

Git documents this: `Documentation/git-status.adoc:59-66` — "It is optional: it defaults to `all`, and if specified, it must be stuck to the option (e.g. `-uno`, but not `-u no`)". Therefore the fix MUST be the `=` form (or `-unormal`); a space-separated spelling is not rejected and degrades to `all`, and `-uno`/`-u` are catastrophic. The existing selftest would catch `all` (it asserts `dirty count=2 (untracked file + collapsed .scratch/)` at `:1657-1660`), but only for the default-config path; a new fixture that asserts merely "non-zero" would let the `all`/space-form regression through. Assert exact counts per config variant.

## F4 [medium] Doc lines become false after the fix

`tools/souji-census.sh:35-36` says "default untracked mode: a wholly untracked directory is one line, matching souji-verify", and `:57-58` says `wt-dirty` is "its own `git status --porcelain` is non-empty". After the fix the mode is forced, and (for `all` repos) it no longer matches `souji-verify`'s counting. Smallest honest rewording: "forced `--untracked-files=normal`: one line per wholly untracked directory; repo config cannot suppress or expand it" and "(same forced untracked mode)" for the `wt-dirty` bullet.

## F5 [medium, route] `souji-verify.sh` carries the identical hole — and the census doc's "matching souji-verify" is already inexact

Three plain status calls with no untracked mode: `tools/souji-verify.sh:322` (`evaluate_repo_root`), `:366` (`evaluate_worktree`), `:820` (`s18_evaluate_worktree_one`); contrast `:658`, which does force `--untracked-files=all`.

Line numbers below are as at base 5fa6017. While this review ran, a sibling added 33 lines to `tools/souji-verify.sh` above line 322 (additions only; the four status-call texts are unchanged), so in the live worktree they currently read `:355`, `:399`, `:853`, and `:691` — equivalently `base+33`. Re-check the numbers before citing them in a landing report.

Measured consequence is confined to evidence/receipt, not the verdict: both callers set `R_VERDICT=NOT-SAFE` unconditionally (`:325` in `evaluate_repo_root`, `:791` in `s18_evaluate_worktree_one`) and only derive `R_RECEIPT`/`R_EVIDENCE` from `dirty` (`:326-329`, `:823-826`). With `status.showUntrackedFiles=no`, a present worktree full of untracked files yields `dirty=0`, `R_RECEIPT=none`, `R_EVIDENCE="… dirty=0"` — a lying receipt that can misattribute a NOT-SAFE to another cause (or to `none`). It cannot by itself produce `SAFE`: the `SAFE` paths at `:814` (absent dir, `metadata-prune`) and `:786` (stale scratch) do not consult `status`. I did not run verify on a lane; this is a static read of the three status sites plus the verdict assignments.

Smallest fix if the operator wants census/verify consistency: add the same `--untracked-files=normal` at `:322`, `:366`, `:820` (or `-c status.showUntrackedFiles=normal` is *not* equivalent enough — CLI is what the census will use). C1's declared edit surface names only `count_dirty`, so route this rather than folding it in; at minimum reword `:35-36` so the "matching souji-verify" claim stays true.

## F6 [low] Arm discrimination is real; encode the r14 arm's whole-run refusal

Sandbox results for the arms C1 names:
- `a31642d` (pre-harm): rc=0, rows `t-inc-no 0 clean`, `t-local-no 0 clean`, `t-wtc-no 0 clean`, `t-local-all 4 dirty` → fails the fixture exactly as intended.
- `cc21683` (r14-harm), direct-key repo only: rc=0, `dirty=0 clean` → also fails by false clean.
- `cc21683`, fleet containing the `include.path` variant: **rc=2 whole-run**, stderr `souji-census: path-protected: git-config-unsupported (…/t-inc-no/.git: …/t-inc-no/.git/config)` — the value-blind refusal the lesson describes.

So the new fixture's expectations must be per arm: `a31642d` and direct-key `cc21683` produce the false-clean row (assert `dirty=0`/`clean` at those revisions), and the include/`config.worktree` variants make `cc21683` exit 2. If `run-matrix.py` compares rows only, keep the direct-key repo as the discriminating case and record the include/`config.worktree` variants as "arm fails (rc=2)".

## F7 [low] Neighbours are unaffected

- Unset-config repo: base and fixed both `0 clean`.
- `normal`/`true` repos: 2 both.
- Base-vs-fixed `--compare` reports only the four expected repos (five lines above) and nothing else.
- Census selftest: `--selftest` on base → rc=0, `38 checks, 0 failed`; on the flag-patched copy → rc=0, `38 checks, 0 failed`. The existing suite cannot detect the hole (no fixture sets the key — grep for `showUntracked` in the script and `tests/fixtures/r15-census-config.py` finds none), which is why the new fixture is required.

## F8 [low] No operability cost

20,000 untracked files in one untracked dir: `-uno` 1 ms / `normal` 1 ms (1 output line) / `all` 5 ms (20,000 lines). Forcing `normal` re-walks dirs that `-uno` skipped, but `normal` collapses and git does not recurse (`wt-status.c:813-818`: early return for `SHOW_NO_UNTRACKED_FILES`, `DIR_SHOW_OTHER_DIRECTORIES|DIR_HIDE_EMPTY_DIRECTORIES` unless `all`). Fleet-wide cost is nil.

## F9 [low, residual] A second config-driven count channel survives: rename detection

`status.renames` (inherits `diff.renames`) changes the porcelain line count for a staged rename: default 1 line, `status.renames=false` 2 lines (measured in a scratch repo). It cannot produce a false clean (a rename still yields ≥1 line), and C1 does not claim it, but the `dirty` column stays config-sensitive after the D1 fix. Fixtures must not assert exact counts on rename-shaped repos, and a future hardening (if wanted) is `-c status.renames=false` alongside the flag; do not add it without a decision, since it changes counts again.

## F10 [info] Failure edges stay safe

- Invalid enum (`status.showUntrackedFiles=bogus`) with the forced flag: git still parses the config and exits 128; `count_dirty`'s `if ! st=$(…)` turns that into `unverifiable` + `status-unverifiable`, rc 0, no whole-run abort. Verified `rc=128` from git and the existing `:1224-1226` mapping.
- `--porcelain=v2` with the flag behaves identically for line counting (2 lines), so the fix does not depend on v1.
- The flag is a no-op for repos with no untracked content, and does not touch tracked/ignored semantics: `.gitignore`/`info/exclude` still hide untracked files by design — the fix closes the *config* channel only. Say so in the claim if anyone reads "no false clean" as absolute.

## F11 [info] Second caller is covered by the same one-line edit

`count_dirty` is called from `emit_row` (`:1205`) and from `worktree_extra_flags` (`:1162`, function at `:1127`) for each non-main worktree. Measured end-to-end on a repo whose main worktree is clean and pushed and whose linked worktree holds one untracked file:
- base: `dirty=0 clean` (no `wt-dirty`) — secondary false clean;
- fixed: `dirty=0 clean,wt-dirty`.
Note the post-fix row still carries `clean` beside `wt-dirty`, because `has_problem` (`:1232-1236`) excludes `wt-dirty`. That is pre-existing vocabulary and consistent with the `:53-58` contract ("clean only when unpushed=0, dirty=0, and a remote tracking ref exists"), but it is worth one sentence in the claim so `clean,wt-dirty` rows are not read as a regression.

## Smallest fix (exact)

1. `tools/souji-census.sh:1037`:
```
-      -c core.attributesFile="$at" status --porcelain --ignore-submodules=all -- . \
+      -c core.attributesFile="$at" status --porcelain --ignore-submodules=all \
+      --untracked-files=normal -- . \
```
(`=` form only — F3.)
2. Reword `:35-38` and `:57-58` (F4).
3. New fixture `tests/fixtures/r17-census-hygiene.py` must contain, at minimum: direct key `no`, `false`, `include.path` `no`, `includeIf gitdir:` `no`, `config.worktree` `no` (with `extensions.worktreeConfig=true`), `all`, and an unset control; assert **exact** `dirty` values (2/2/2/2/2/2/0) and the `dirty`/`clean` flag, on both the main row and a `wt-dirty` linked-worktree case; record the per-arm expectations from F6 (a31642d/cc21683 fail, cc21683 include variant exits 2).
4. Route F5; do not edit `souji-verify.sh` inside C1.

## Residual risk / verification gaps

- `census/round-17/run-matrix.py` and the new fixture do not exist at 5fa6017; the claim's counting command was not runnable, so its pre-harm/r14/r16/changed arms are unverified by me. The flag-patched copy I ran is byte-identical to base except for the inserted option.
- All census executions were against `/var/tmp/souji-r17-RevD1Static` roots; no real fleet directory was scanned, consistent with the contract.
- Git version dependence: proven on 2.56.0. The census comment cites a 2.45 floor for `GIT_NO_LAZY_FETCH`; `--untracked-files=<mode>` predates that comfortably, but the arm evidence is single-version.
- Precedence is proven empirically (four config channels + `-c`) and by source read of git v2.56.0; I did not build git from source. Source anchors: `builtin/commit.c:208-215` (`status_init_config` → `repo_config`), `:1507-1513` (config key handler), `:1607-1615` (config, then `parse_options`, then `handle_untracked_files_arg`), `:1216-1227` (option handler assigns unconditionally); `wt_status.c` (fetched as `wt-status.c`): `:150` default `SHOW_NORMAL_UNTRACKED_FILES`, `:813-818` collapse vs `all`; `Documentation/config/status.adoc`: "This variable can be overridden with the -u|--untracked-files option"; `Documentation/git-status.adoc:59-72` option semantics. Docs were fetched from `raw.githubusercontent.com/git/git/v2.56.0` (the `.txt` paths 404; the `.adoc` paths served).
- I did not test `extensions.worktreeConfig` arriving through an `include` (git reads extensions only from the common config, per the census comment at `:666-668`); the `config.worktree` case used the ordinary path.
- F5 is a static read of three verify sites plus their verdict assignments; verify was not executed.

## Commands run (abridged, all outputs above)

- `git -C <lane> rev-parse HEAD` → `5fa6017…`; `sha256sum tools/souji-census.sh` = `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` = base blob (worktree untouched).
- `git show 5fa6017:tools/souji-census.sh | grep -n 'count_dirty|dirty|showUntracked|untracked'`, `sed -n '505,545p'`, `'560,700p'`, `'700,760p'`, `'1195,1260p'`, `'1425,1480p'`, `'1657,1660p'`.
- Sandbox repo construction + `git status --porcelain …` variants (mode matrix, spellings, invalid enum, rename, perf).
- `bash tools/souji-census.sh --root <sb>/fleet` (base) and the same on the flag-patched copy; `--compare` both ways; `--selftest` both (38/38).
- `git show a31642d:tools/souji-census.sh > c-a31642d.sh`, `git show cc21683:… > c-cc21683.sh`, run on `<sb>/fleet` and `<sb>/fleet3`.
- `curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/{builtin/commit.c,wt-status.c,Documentation/git-status.adoc,Documentation/config/status.adoc}` into the sandbox; grep for the anchors above.
- Tool installs: none. `/var/tmp/souji-r17-RevD1Static` deleted after the run.
