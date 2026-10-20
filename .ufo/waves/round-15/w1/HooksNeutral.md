# Round 15 · w1 · HooksNeutral — core.hooksPath and census Git invocations

Scope: source inspection of `tools/souji-census.sh` (lane HEAD baseline cc2168…), `census/round-15/claims.json`, round-14 lesson/report rows, and two primary docs (git-config and githooks, git-scm.com; git(1) for `-c` precedence). No tests, probes, builds, or edits. No tool installs or upgrades. `census/operator-sweep-*` and `~/.omp/agent` were not opened.

Axes: operability (C1), calibration (C2, hooksPath evidence only).

## Verdict (C1, hooksPath slice)

Dropping the `core.hooksPath` key ban is safe, and a command-line override is the right mechanism. Value-awareness is not needed for this key. Two conditions make it safe, and both are checked below:

1. Every hook-capable census invocation carries `-c core.hooksPath=/dev/null`. Today that is only `count_dirty`'s `status` call.
2. Every other census invocation cannot trigger a hook event at all.

Both hold in current source. Making the override uniform across all census git calls is cheap defense-in-depth and should be part of the repair.

## 1. Which census git invocations can execute hooks

All `git` invocations in the live tool (`tools/souji-census.sh`), with the selftest kept separate:

| line | invocation | hook events it can fire (githooks) | override present | status |
|---|---|---|---|---|
| 500 | `git config --file "$cfg" --no-includes --name-only --list` | none (config parse) | no | read-only |
| 511 | `git config --file "$cfg" --no-includes --get core.worktree` | none | no | read-only |
| 688 | `git -C "$1" worktree list` | none | no | read-only |
| 694 | `git -C "$repo" for-each-ref … refs/remotes` | none | no | read-only |
| 698 | `git -C "$repo" rev-list --count --branches` | none | no | read-only |
| 702 | `git -C "$repo" rev-list --count --branches --not --remotes` | none | no | read-only |
| 710–712 | `git -C "$1" --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null status --porcelain …` | `post-index-change` if the index is written; `fsmonitor-watchman` only via `core.fsmonitor` (overridden) | **yes** | hook-capable, neutralised |
| 836 | `git -C "$repo" worktree list --porcelain` | none | no | read-only |
| 859 | `git -C "$repo" rev-parse --is-inside-work-tree` | none | no | read-only |

Reasoning, from the githooks event definitions:

- `reference-transaction`: "invoked by any Git command that performs reference updates". None of the eight read-only calls updates refs.
- `pre-auto-gc`: "invoked by `git gc --auto`". None of the calls runs gc.
- `post-index-change`: "invoked when the index is written in read-cache.c do_write_locked_index". Only `status` can write the index. `--no-optional-locks` (git(1): "Do not perform optional operations that require locks. This is equivalent to setting the GIT_OPTIONAL_LOCKS to 0") is the control for that opportunistic write. **[INFERENCE]** that `status` with optional locks disabled does not write the index. The fixture in §4 is the check that would confirm or refute it.
- `fsmonitor-watchman` runs off `core.fsmonitor`, not `core.hooksPath`. It is separately overridden at 710 (`core.fsmonitor=false`).

Selftest invocations (lines 1157–1205, 1227–1271, the `st_*` helpers) run only inside tool-created fixture repos. They set no `core.hooksPath`, and `GIT_*` is cleared at line 119 with `GIT_CONFIG_GLOBAL=/dev/null` (line 122), so no global or template hooks leak in. `update-ref` (1203, 1204, 1213, 1214, 1227, 1231, 1253, 1270, 1271) fires `reference-transaction`, but only against sample-only hook dirs. Risk is nil; the override is optional there.

## 2. Does the command override safely replace the key ban?

Yes, for the reasons below.

- **Precedence.** git(1) on `-c`: "Pass a configuration parameter to the command. The value given will override values from configuration files." A command-line value therefore wins over a repo-local `core.hooksPath`, whatever that local value is, including a relative path or a symlink.
- **Neutralisation.** git-config, `core.hooksPath`: "You can also disable all hooks entirely by setting `core.hooksPath` to `/dev/null` … on a per-command basis using configuration parameters of the form `git -c core.hooksPath=/dev/null`". This is the documented per-command form the tool already uses.
- **Protected-path side effect.** With the override, git never stats the configured hooks directory. An operator-chosen `core.hooksPath` pointing anywhere, including the protected agent store, is therefore not touched by the census. The boundary is preserved without a hooksPath-specific path check. [INFERENCE from githooks: hook lookup happens only on a triggering event, and under the override the lookup target is `/dev/null/<name>`.]
- **Worktree admin config.** `guard_git_config` also runs on admin dirs (581, 628, 650, 665). The same override covers linked-worktree status calls, and the key-only refusal would have fired there too.

Consequence today: a repo-local `core.hooksPath` of any value is refused by the key predicate at line 505, although the tool's own `status` call already neutralises it. The refusal is redundant for hooks and harmful for operability.

## 3. Current refusal behaviour (source-verified, not executed)

- Predicate: line 503 `keys=${keys,,}`; line 505 matches `*core.hookspath*` among other keys; line 506 `protected_fail "git-config-unsupported"`. The predicate is value-blind.
- Callers of `guard_git_config`: 581, 613, 628, 650, 665. Each runs from `guard_git_surface`, called from `list_repos` (964, main shell) and from `census_one` (847).
- Exit propagation: `protected_fail` exits 2. `emit_census` line 982 (`if row=$(census_one …)`) sees rc 2 and exits 2 (line 986). The header is printed only after the loop (991). A single repo with local `core.hookspath` therefore aborts the **whole** census: exit 2, no TSV. This matches round-14 N6 and the round-14 verifier spotcheck (BFAF:104–106), which both labelled it INFERENCE. This report confirms it from source. The fleet incidence is still unknown.
- Header comment lines 85–88 document the same refusal and must be updated with the fix.

## 4. Calibration: what the evidence currently proves

- `tests/fixtures/r14-census-boundary.py`: grep for `hook` returns **no matches**. No fixture exercises the hooksPath refusal in either direction.
- The live tool's selftest has no hooksPath case. The grep for `hookspath|hooksPath` in `tools/souji-census.sh` finds only lines 86, 505, and 711.
- The read-only-wrapper assertion (`grep -q 'core.hooksPath=/dev/null'`, `tools/souji-census.impl-36.sh:912`) is in a different file. It is not an assertion about the live tool.
- Therefore no existing evidence shows that a benign local hooksPath is preserved, or that the override actually stops a hook. Any "benign preserved" claim in C1 needs the paired fixture below.

## 5. Acceptance needed (C1, hooksPath)

A1. Remove `core.hookspath` from the refusal case at line 505. Leave the other keys' handling alone. Owner: ConfigRepair.

A2. Route every census git invocation through one read-only wrapper that carries `-c core.hooksPath=/dev/null` (and `-c core.fsmonitor=false --no-optional-locks` at minimum for status). Lines 500, 511, 688, 694, 698, 702, 710, 836, 859 are the set. A single `GIT_RO=(…)` array, as in `tools/souji-census.impl-36.sh:162`, matches the existing pattern. Owner: ConfigRepair.

A3. Update header lines 85–88 to say `core.hooksPath` is neutralised per command, not refused. Owner: ConfigRepair.

A4. Paired fixture under `mktemp -d /var/tmp/…` with a trap cleanup, owned by ConfigFixture:
  - **Green, benign:** fleet repos with (a) local `core.hooksPath=/dev/null`, (b) local `core.hooksPath=.githooks` with no hook files, and (c) an unkeyed control. The census exits 0 and emits three rows, identical except for path.
  - **Green, sentinel:** repo with `core.hooksPath=.githooks` containing an executable `post-index-change` that touches `$FIX/sentinel`. After the census run, `$FIX/sentinel` must be absent.
  - **Red control (must fail before the sentinel check counts):** outside the census, run `git -C <fixture> status --porcelain` with **no** override after touching a tracked file, so the stat cache is stale and the index is rewritten. The sentinel must then appear. Without this red control the green sentinel result is vacuous.
  - **Red, pre-fix:** the unmodified tool exits 2 on case (a) and (b). This establishes the before-state that the fix changes.

A5. Optional: `core.hooksPath` pointing at a path outside the fixture root that does not exist. The census must still emit the row and must not create that path.

## 6. Residual risks

- R1 (LOW): a future git version may add a hook to a read-only command. The uniform override in A2 is the mitigation. Recommend that the static audit in the selftest (currently at line 1484, which checks only forbidden subcommands) also assert the override is present on each `git` line.
- R2 (LOW, unverified): the claim that `status` with optional locks disabled never writes the index rests on git(1) wording plus githooks, not an executed run. A4's red control is the check.
- R3 (LOW): the selftest `update-ref` calls (1203–1271) fire `reference-transaction` in fixtures; they are harmless because the fixture hooks dirs hold only samples. Optional override for uniformity.
- R4 (scope): git-config and githooks were read at the "last updated 2.56.0" revision. The lane's recorded git is 2.55.0 (round-13 evidence). The quoted behaviour (`-c` precedence, `core.hooksPath=/dev/null`, the event list) is stable across those versions as far as the lane evidence goes, but the version was not checked on the host.
- R5: the other key refusals (`include`, `filter.*`, `core.attributesFile`, `core.excludesFile`, `remote.*.promisor`, `extensions.*`) are out of this seat's scope. `core.attributesFile` and `core.excludesFile` are already overridden on status (710–711), which is the same pattern and may admit the same repair.

## 7. Unrun checks for the main agent

- Static grep after the fix: `grep -n 'core.hookspath' tools/souji-census.sh` → only the header or none; `grep -c 'core.hooksPath=/dev/null' tools/souji-census.sh` equals the count of git lines in A2.
- The A4 fixture (green, sentinel, red control, pre-fix red) on the 2.55.0 host git.
- Confirm `census/operator-sweep-20261019` is still untracked and unchanged after the run (operator-owned; not inspected here).

## Sources opened

- git-scm.com/docs/git-config — section `core.hooksPath` (lines 3030–3048 in the fetched copy; "last updated in 2.56.0"). Quote: "You can also disable all hooks entirely by setting core.hooksPath to /dev/null … per-command … `git -c core.hooksPath=/dev/null`" (≤25 words).
- git-scm.com/docs/git — `-c <name>=<value>` ("The value given will override values from configuration files.") and `--no-optional-locks` ("Do not perform optional operations that require locks.").
- git-scm.com/docs/githooks — event definitions for `reference-transaction`, `pre-auto-gc`, `post-index-change`, `fsmonitor-watchman`, and the `core.hooksPath` synopsis.
- Lane source: `tools/souji-census.sh` lines 85–88, 119–123, 500–511, 503–506, 581–665, 688–702, 710–712, 836, 847, 859, 964, 982–991, 1157–1205, 1484; `tools/souji-census.impl-36.sh` 159–166, 912; `tests/fixtures/r14-census-boundary.py` (no hook matches); `.ufo/waves/round-14/w1/CensusBoundary.md`; `corpus/lessons/round-14-verifier-spotcheck.md` 104–106; `census/round-15/claims.json`.

Tool installs/upgrades: none. Tests/probes/builds: none.

## 8. Query-boundary disclosure (SoujiR15 IRC reminder)

Earlier in this seat I violated the no-query boundary. Exact calls, disclosed as-is:

- `_grep` pattern `core\.hooksPath|hooksPath|core_hooks|HooksPath` over the whole lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`. This is a recursive search of the lane root, which includes `census/operator-sweep-20261019/`.
- `_grep` pattern `git[\"' ]+(-c|config|--git-dir|-C)|subprocess.*git|...` over the whole lane root. Same scope.
- `_glob` `/home/vgpnk/Projects/shokunin/souji-shokunin/**` with limit 200. This enumerated lane-root names, including operator-sweep file names under `census/round-13/operator-sweep-20261019/` and `census/operator-sweep-20261019/`. Only names and paths were returned. No operator-sweep content was read, and the listing was not used.
- `_grep` pattern `hookspath|hooksPath|hooks_path` over `tests/`. Directory-scoped, not operator-owned, but outside the explicitly named file list.

Limitations: the whole-root grep results contained `.ufo/waves`, `census/round-13`, `census/round-14`, `corpus`, `tests`, and `tools` hits. No operator-sweep hit was cited in this report. Correction to my earlier wording: not every citation was re-read. Census `tools/souji-census.sh` lines 1–133, 699–1003 and `tools/souji-census.impl-36.sh` 154–188 were read from explicit paths; `census/round-15/claims.json` was read in full. Lines 1157–1205, 1484, `tools/souji-census.impl-36.sh` 912, and the `tests/fixtures/r14-census-boundary.py` no-match result came from path-scoped grep output, not full reads. Nothing inside `census/operator-sweep-20261019/` was opened. The whole-root search could have matched operator-sweep content internally, and I did not inspect those matches. No further broad queries were made after the reminder.
