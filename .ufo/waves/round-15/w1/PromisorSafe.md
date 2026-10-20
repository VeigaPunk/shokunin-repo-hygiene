# Round 15 · w1 · PromisorSafe (reviewer, source inspection only)

Axes: operability, calibration. Scope: `remote.*.promisor` (false/true/invalid boolean), `extensions.partialClone` values, and the promisor membership that git itself derives from config.
Mode: source inspection only. No tests, probes, builds, or edits. Round-15 repairs have not landed (`git status`: `tools/` unchanged from HEAD `cc21683`), so every finding below is against the round-14 baseline and is a design acceptance target for the repair.

Sources read:
- Lane: `tools/souji-census.sh` (header 79-99; env 120-123; `guard_git_config` 493-522; `git worktree list`/`for-each-ref`/`status`/`rev-parse` call sites 687-696, 836, 859).
- Lane: `tools/souji-repo-structure.sh` (env 149-154; `GIT` array 177; partial/promisor refusal 197-233).
- Fixtures: `tests/fixtures/r13-repo-structure.sh` (env 165-169; promisor-refusal case 543-565). `tests/fixtures/r14-census-boundary.py`: grep finds zero `promisor`, `partialClone`, `partialclonefilter` cases.
- External primary, git tag v2.55.0 (raw.githubusercontent.com): `setup.c` (`handle_extension_v0`, lines 630-633), `promisor-remote.c` (`promisor_remote_config`, `promisor_remote_init`, `repo_has_promisor_remote`, `fetch_objects`), `config.c` (`git_config_bool` 1297-1301), `odb.c` (604-607), `Documentation/config/extensions.adoc`, `Documentation/config/remote.adoc`, `Documentation/git.adoc` (`--no-lazy-fetch`; `--type=bool` empty value and value-less key semantics).

Install/update record: none. No tools installed or upgraded. No pacman transaction.

## Git semantics the repair must match (source-verified at v2.55.0)

| Key | Git behaviour | Consequence |
|---|---|---|
| `remote.<n>.promisor` | `promisor_remote_config` calls `git_config_bool` per occurrence; only a true occurrence creates a promisor entry. Value-less key = true (git.adoc). Empty value = false (git.adoc: `--type=bool` converts empty to `false`). | `false` is a no-op. Any true occurrence makes the repo promisor (sticky across later false lines). Invalid value dies (`config.c:1301`, `bad boolean config value`). |
| `extensions.partialClone` | `setup.c:630-633`: any non-NULL value sets `partial_clone`; value-less key → `config_error_nonbool`. `promisor_remote_init` then creates a promisor entry named by that value. | Any value makes the repo promisor, including `false`, `""`, `origin`. The value is a remote name, not a boolean. |
| `remote.<n>.partialclonefilter` | `promisor_remote_config`, branch `partialclonefilter`: creates the entry via `promisor_remote_new` when absent, **without** requiring `promisor=true`. Value irrelevant. | Makes `repo_has_promisor_remote()` true, so promisor membership is value-independent for this key. |
| Lazy fetch | `odb.c:604-607`: `fetch_if_missing && repo_has_promisor_remote(...) && !SKIP_FETCH` → `promisor_remote_get_direct` → `git fetch <name> --filter=blob:none` (`fetch_objects`). `GIT_NO_LAZY_FETCH=1` clears `fetch_if_missing`. | `GIT_NO_LAZY_FETCH=1` is the write-free control; `GIT_OPTIONAL_LOCKS=0` is not. |

## Findings

### F1 · HIGH · operability · census refuses `remote.*.promisor=false` (value-blind harm)
- `tools/souji-census.sh:500-506`: `git config --name-only --list` output, lowercased, then a substring `case` match on `*remote.*.promisor*`. Key names only; the value is never read. `remote.origin.promisor = false` → `protected_fail git-config-unsupported` (exit 2).
- Git treats `false` as a no-op (table above). This is the round-14 operability harm the wave is meant to repair.
- Acceptance for the repair: value-aware parse, e.g. `git config --file "$cfg" --no-includes --type=bool --get-regexp '^remote\..+\.promisor$'`. Refuse on any line whose value is `true`. Exit 1 (no match) = benign. Any other exit (e.g. 128 on an invalid boolean) = could-not-evaluate or refuse, never clean. Mirror the probe's classification at `souji-repo-structure.sh:215-233`.

### F2 · HIGH · calibration · do NOT make `extensions.partialClone=false` benign
- Source: `setup.c:630-633` and `promisor_remote_init` make any non-NULL value an active promisor. `extensions.partialClone=false` would create a promisor remote named `false`. Git then attempts lazy fetch through it on missing objects.
- Current refusal is correct and must stay value-blind for this key: probe `souji-repo-structure.sh:203-208` (`config --local --get`, rc 0 → refuse) and census key match at `:505`.
- Risk: a repair that copies the `remote.*.promisor` bool logic onto `extensions.partialClone` would silently admit `false`/empty values. This is a calibration regression.
- Acceptance: fixture rows `extensions.partialClone` ∈ {`false`, `""`, `origin`} → refused in both tools; value-less key → refused (git itself errors on it).
- Note the contract wording "false must not value-blind refuse" applies to `remote.*.promisor` only, not to `extensions.partialClone`.

### F3 · HIGH · operability/write-safety · `remote.<n>.partialCloneFilter` is an unrefused promisor marker; census has no lazy-fetch guard (source-verified, runtime not observed)
- `promisor-remote.c` (`promisor_remote_config`, partialclonefilter branch) creates the promisor entry regardless of `promisor=`. `repo_has_promisor_remote` is then true, and `odb.c:604-607` fetches on a missing object. Neither tool refuses this key: census `:505` matches `*remote.*.promisor*` only; probe `:216` regex is `\.promisor$` only.
- Probe: mitigated. `GIT_NO_LAZY_FETCH=1` at `souji-repo-structure.sh:151`. A missing object fails rather than fetching.
- Census: **unmitigated.** `tools/souji-census.sh:120-123` exports `GIT_OPTIONAL_LOCKS=0`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`, `GIT_TERMINAL_PROMPT=0`, but not `GIT_NO_LAZY_FETCH`. Grep finds no `GIT_NO_LAZY_FETCH` in census. Census runs `git status --porcelain` (`:33`, `:688` area) and `rev-list`/`rev-parse`/`for-each-ref`/`worktree list` on the repo. Any of these reading a missing tree or blob can trigger `git fetch <remote> --filter=blob:none`. That is a network and write path inside a "read-only census".
- Repair acceptance (both required; the env var is the mandatory control):
  1. Census exports `GIT_NO_LAZY_FETCH=1` next to `GIT_OPTIONAL_LOCKS=0`. The r13 fixture already does this (`r13-repo-structure.sh:169`).
  2. Census classifies `remote.*.partialclonefilter` (any value, including empty) as a promisor marker. Membership is value-independent, so refusal must be too. Refusal is fail-closed. Document it as an operability boundary, not a promisor-clean result.
- Fixture row: a repo with `remote.origin.partialCloneFilter=blob:none` only and a missing blob must not emit a clean census row and must not produce a `git fetch` trace.

### F4 · MEDIUM · operability · census substring matching over-refuses benign remote names
- `tools/souji-census.sh:505`: patterns are unanchored substrings over the whole key list. `*include.*` matches `remote.include.url` (a remote named `include`, no includes at all). `*remote.*.promisor*` matches `remote.x.promisor-mirror.url` (a remote named `x.promisor-mirror`, which git does not treat as promisor).
- Repair: classify by exact parsed section, subsection and key (e.g. `remote` / `<sub>` / `promisor`), not by substring. This applies to the whole `case` list, not only promisor. Keep the `include.path` and `includeif.*.path` cases exact so that the IncludeIfSafe seat's work is not undone.
- Fixture acceptance: remote named `include` (benign URL) → not refused; remote subsection `x.promisor-mirror` → not refused.

### F5 · MEDIUM · operability/consistency · probe reads host-global and system config; census clears it
- Probe: env block `souji-repo-structure.sh:149-154` and `GIT` array at `:177` do not clear `GIT_CONFIG_GLOBAL` or `GIT_CONFIG_NOSYSTEM`. Census clears both (`souji-census.sh:122-123`); so does the r13 fixture (`r13-repo-structure.sh:165-166`).
- Probe's `--get-regexp` without `--local` therefore reads `~/.gitconfig` and `/etc/gitconfig`. A host-global `remote.<n>.promisor=true` makes probe refuse every repository (exit 2), while census ignores the same line. The two tools then disagree on the same repo.
- Repair options: clear global/system in the probe (match census and the r13 fixture) and say so in the header; or document that the probe deliberately includes global config. Either way the two tools must classify identically. I did not open the user's global config (not needed for source review; not an auth file).

### F6 · MEDIUM · calibration · fixtures cannot yet distinguish red from green on this axis
- `r13-repo-structure.sh:543-565` covers only `remote.origin.promisor true` and `extensions.partialClone origin`. No `false`, value-less, empty, invalid, case-variant, whitespace, `partialclonefilter`-only, or benign-remote-name cases.
- `r14-census-boundary.py` has zero promisor/partialClone/partialclonefilter cases (grep). The round-14 harm (F1) therefore has no red row in any fixture. A green-only repair could pass unchanged.
- Required rows for ConfigFixture (baseline red, repaired green, same command):
  - `remote.origin.promisor=false` → proceeds (green); baseline refuses (red).
  - `remote.origin.promisor` (value-less), `=true`, `=yes`, `=on`, `=1`, `=TRUE` → refused.
  - `remote.origin.promisor=` (empty) → proceeds.
  - `remote.origin.promisor=maybe` → could-not-evaluate or refused, never clean.
  - `extensions.partialClone` ∈ {`false`, `""`, `origin`} → refused; value-less → refused.
  - `remote.origin.partialCloneFilter=blob:none` alone → refused (F3).
  - Mixed fleet: one repo with `promisor=false`, one with `promisor=true`, same run → only the second refused; first's row exact.
  - Forbidden-access trace: the false-promisor repo must show no `git fetch` and no write-class syscall under the census.

### F7 · LOW · calibration (keep as is) · probe's multi-occurrence handling
- `souji-repo-structure.sh:218-227` refuses on any `… true` line. Git's `promisor_remote_config` makes the repo promisor on any true occurrence (later `false` does not undo it). The probe is correct; keep it. An invalid occurrence anywhere yields rc 128 → exit 4 (could-not-evaluate) before the loop. That is fail-closed and acceptable.

### F8 · cross-seat note · same bug class in `extensions.worktreeConfig`
- `setup.c:635-636`: `extensions.worktreeConfig` is `git_config_bool`. `extensions.worktreeConfig=false` is benign. Census `:505` refuses it on key presence. Owned by the WorktreeCfg seat; flagged here so the same value-aware parse is applied.

## Design-only status
Source is present (tools, fixtures, git v2.55.0 source), so this is not design-only. The repair itself is not in the tree yet. Acceptance above is the observable contract for the executor; the reviewer must re-verify it against the landed diff.

## Verification gaps (not run; no runtime evidence claimed)
- F3 is source-derived. The lazy-fetch-from-`partialCloneFilter` behaviour is not observed on this host. No probe was run, as the contract requires.
- The `git_parse_maybe_bool_text` empty-value rule is taken from `git.adoc` text ("empty value … converted to `false`"), not from re-reading the helper.
- Whether `extensions.partialClone` is read from repo-local config only (census `--no-includes`, probe `--local`) was not verified against `setup.c` read path. Current use is consistent with git's documented repo-scoped extensions, but I did not trace it.
- Whether census's `git status`/`rev-list` actually reach a missing object on a `partialCloneFilter`-only repo is `[INFERENCE]` from the call sites; the trigger is source-supported, the census path is not exercised.
- No shellcheck, selftest, or fixture run. L1 runs final acceptance.

## Messages
Material findings F1–F3 are sent to SoujiR15 by id.

## Boundary disclosure (no-query rule)
- Violated once, early: `_grep` for `promisor|partialClone|partialclone` over the whole lane root `/home/vgpnk/Projects/shokunin/souji-shokunin` (recursive, no path restriction). Its output was paginated ("Showing files 1-20 of 27+") and truncated, so I cannot rule out that it read `census/operator-sweep-20261019/` content. I did not open, copy, or edit any file from that path, and I used none of the matched lines from it in this report.
- Limitation: the result set contained only round-13/14/15 and top-level docs in the visible page; the hidden remainder is unknown. No operator-sweep text is quoted or relied on.
- `_bash` `ls -la` of the lane root (top level only) and `git status --short` / `git log --oneline -5` named `census/operator-sweep-20261019/` as an untracked name only; no contents read.
- `ls /home/vgpnk/.omp/agent/RULES.md` was an existence check only; the file was not read. No auth or credential path was touched.
- All later searches were restricted to explicit paths: `tools/`, `tests/fixtures/` (named files), `census/round-14`, `census/round-15`, `.ufo/waves/round-15/w1`, and the named `tools/souji-census.sh` / `tools/souji-repo-structure.sh`. No further runtime probes or tests were run.
