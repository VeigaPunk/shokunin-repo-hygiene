# ScoutPromisorConsumers — why `git status` dies on an invalid `remote.<n>.promisor`, and what `GIT_NO_LAZY_FETCH=1` actually guarantees (round 16, W1)

Seat: `SoujiR16.ScoutPromisorConsumers`. Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Axis: operability (C1). Recon only; no edits outside this report, no test run, no census run.

## Verdict

**The failure is a config-parse `die()` on the promisor subsystem's lazy init, reached by every `git status`; it is not a fetch decision, so `GIT_NO_LAZY_FETCH=1` is irrelevant to it.** `git status` calls `diffcore_std`, which evaluates `repo_has_promisor_remote()` *before* and independently of any diff-format or fetch logic; that call initialises the promisor subsystem, whose config callback parses `remote.<n>.promisor` with `git_config_bool()` and dies on a non-boolean, non-numeric value (`promisor = maybe`). Exit is 128; the census maps that to `dirty=0, status-unverifiable`, exactly as the script header (`:105-107`) and fixture case_07 say.

**`GIT_NO_LAZY_FETCH=1` does prevent every lazy fetch, but at the fetch chokepoint (`fetch_objects`), not at `fetch_if_missing`.** In git 2.55/2.56 `fetch_objects()` returns -1 before building the `git fetch` child when the variable is true (`promisor-remote.c:34-42`), and that function is the only place the promisor machinery spawns a fetch. Every census git call inherits the variable (exported at `tools/souji-census.sh:147`, after the inherited `GIT_*` clear at `:139-143`), and the census never runs `fetch`/`pull`/`clone`. So the header/scan-arm claim "cannot fetch under GIT_NO_LAZY_FETCH=1" (`:644`) is **true**, and stronger than the comment's wording suggests.

Residuals worth carrying: the failure reason is invisible (status stderr is discarded, `:947-955`), so a promisor-degraded row has no diagnostic while the filter-driver case has one (`:940`); and the fixture only exercises complete repositories, so a genuine partial clone (missing blobs) under the census is untested — it cannot fetch, but it can still fail status.

## Access record

- Docs opened **2026-10-20**: `https://git-scm.com/docs/git-config` (page header "git-config last updated in 2.56.0"), `https://git-scm.com/docs/partial-clone`, `https://git-scm.com/docs/git` (page header "git last updated in 2.56.0").
- Source read **2026-10-20** at tag `v2.55.0` (the L1-observed version), with spot checks at `v2.56.0` and `master`: `https://raw.githubusercontent.com/git/git/v2.55.0/{setup.c,promisor-remote.c,diff.c,diffcore-rename.c,diff-lib.c,odb.c,config.c,parse.c,wt-status.c,builtin/{commit.c,for-each-ref.c,worktree.c},revision.c}`.
- Lane state observed: HEAD of `tools/souji-census.sh` is `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`, and the working copy is byte-identical to that commit (`git diff --quiet` → `SAME_AS_CBF`), so the line numbers below are the cited commit's lines.

## Quotes (each ≤25 words, accessed 2026-10-20)

1. `https://git-scm.com/docs/git-config` § `remote.<name>.promisor`:
   > When set to true, this remote will be used to fetch promisor objects.
2. `https://git-scm.com/docs/git-config` § `extensions.partialClone`:
   > The value of this key is the name of the promisor remote.
3. `https://git-scm.com/docs/partial-clone` § Handling Missing Objects:
   > Git invokes promisor_remote_get_direct() to try to get the object from a promisor remote
   (13 words)
4. `https://git-scm.com/docs/partial-clone` § Using many promisor remotes:
   > Remotes that are considered "promisor" remotes are those specified by the following configuration variables
5. `https://git-scm.com/docs/git` § Environment Variables `GIT_NO_LAZY_FETCH`:
   > Setting this Boolean environment variable to true tells Git not to lazily fetch missing objects from the promisor remote on demand.
   (21 words)
6. `https://git-scm.com/docs/git` § Options `--no-lazy-fetch`:
   > This is equivalent to setting the `GIT_NO_LAZY_FETCH` environment variable to `1`.
   (11 words)

The partial-clone doc lists exactly three markers (`extensions.partialClone`, `remote.<name>.promisor`, `remote.<name>.partialCloneFilter`), which matches the three keys the census scan accepts without an arm (`tools/souji-census.sh:644`).

## Q1 — why `git status` fails with `bad boolean config value`

Observed chain (v2.55.0 line numbers; v2.56.0 identical at each hop I re-checked):

1. `git status` → `cmd_status` (`builtin/commit.c:1537`) → `wt_status_collect` → `wt_status_collect_changes_worktree`, which sets `DIFF_FORMAT_CALLBACK` and calls `run_diff_files` (`wt-status.c:621-623`, `:662`); `wt_status_collect_changes_index` likewise calls `run_diff_index` (`wt-status.c:692-708`).
2. `run_diff_files` ends with `diffcore_std(&revs->diffopt)` (`diff-lib.c:294`); `run_diff_index` at `diff-lib.c:652`.
3. `diffcore_std` evaluates `repo_has_promisor_remote(options->repo)` as the **left operand of an `&&`**, unconditionally for every diff (`diff.c:7498`; v2.56.0 `diff.c:7478`). It does not matter that `DIFF_FORMAT_CALLBACK` is not a prefetch format: the call is made before the format test.
4. `repo_has_promisor_remote` → `repo_promisor_remote_find` → `promisor_remote_init` (`promisor-remote.c:211-225`, `:166-177`), which runs `repo_config(r, promisor_remote_config, config)`.
5. The callback hits `remote.<name>.promisor` and calls `git_config_bool(var, value)` (`promisor-remote.c:132-136`).
6. `git_config_bool` dies when the value does not parse (`config.c:1291-1296`):
   > `die(_("bad boolean config value '%s' for '%s'"), value, name)`
   — this is the exact text L1 observed.
7. `git_parse_maybe_bool` semantics (`parse.c:166-193`) decide which values die:
   - bare key (NULL) → 1; empty value → 0; `true|yes|on` → 1; `false|no|off` → 0;
   - any decimal integer (`2`, `-1`, …) → `!!v`, so `promisor = 2` is **true**, not an error;
   - anything else (`maybe`, `banana`, `tru`) → -1 → **die**.

Consequences that match the lane's documented behaviour:

- The key needs no matching `[remote "<x>"] url` and no promisor packfile; a stray `remote.o.promisor = maybe` is enough.
- The die happens before `fetch_objects` is ever considered, so `GIT_NO_LAZY_FETCH=1` cannot change this outcome (it is not consulted on this path).
- `die()` exits 128; `count_dirty` treats any non-zero status as `unverifiable` (`tools/souji-census.sh:947-955`) and the row becomes `dirty=0 ... status-unverifiable` (`:1135-1137`), with the run still exiting 0. This is precisely header `:105-107` ("an invalid promisor boolean fails git's own status, giving status-unverifiable as before round 14") and fixture case_07 (`tests/fixtures/r15-census-config.py:1136-1139`).
- Only `status` is affected among census commands. `rev-list` touches the promisor subsystem only under `--exclude-promisor-objects` (`revision.c:2715-2719`, `:3999-4001`), which the census never passes; `for-each-ref` (`builtin/for-each-ref.c`) and `worktree list` (`builtin/worktree.c`) contain no promisor reference in v2.55.0. So `unpushed`/`worktrees` stay honest while only `dirty` degrades — consistent with case_07's expected `("1","0","0","status-unverifiable")`.

## Q2 — which code path/doc reads the key "at repository setup"

`remote.<n>.promisor` is **not** read at repository setup. Setup only reads:

| Key | Site | Parse |
|---|---|---|
| `extensions.partialClone` | `setup.c:621-628` (`handle_extension_v0`), stored as `data->partial_clone = xstrdup(value)`; `config_error_nonbool` if no value; attached at `setup.c:1781-1782`; consumed by `promisor_remote_init` at `promisor-remote.c:178-188` | **string remote name**, never boolean — `partialClone = false` names a remote called "false" (partial-clone doc `:366-372`); cannot produce this die |
| `remote.<n>.partialCloneFilter` | not setup; `promisor_remote_config` at `promisor-remote.c:146-153` creates a promisor entry for the remote with **no boolean parse** | string filter; cannot produce this die |
| `GIT_NO_LAZY_FETCH` | `setup.c:1065-1067`, inside `setup_git_env_internal()`: `if (git_env_bool(NO_LAZY_FETCH_ENVIRONMENT, 0)) fetch_if_missing = 0;` | boolean env var, read once per process at gitdir setup |

`remote.<n>.promisor` is read lazily, the first time `promisor_remote_init()` runs. For `git status` that first time is `diffcore_std` (`diff.c:7498`); for object access it is `odb.c:598`. Docs: git-config § `remote.<name>.promisor` (quote 1) and partial-clone § Using many promisor remotes (quote 4); partial-clone § Handling Missing Objects describes the on-demand call (quote 3).

Because `repo_config` is used, the offending boolean can also live in `config.worktree` (when `extensions.worktreeConfig` is true) — the census's `scan_config_file` has no arm for `remote.*.promisor` (`tools/souji-census.sh:640-646`), so it passes the guard and surfaces only as the status failure.

## Q3 — does `GIT_NO_LAZY_FETCH=1` prevent any fetch for every census command?

Yes, and the mechanism is sharper than `fetch_if_missing`:

1. **Single chokepoint.** `fetch_objects()` opens with `if (git_env_bool(NO_LAZY_FETCH_ENVIRONMENT, 0)) { … warning(_("lazy fetching disabled; some objects may not be available")); return -1; }` before it builds `git fetch <remote> --filter=blob:none --stdin` (`promisor-remote.c:22-51`). Every promisor call funnels through `promisor_remote_get_direct` → `try_promisor_remotes` → `fetch_objects` (`promisor-remote.c:271-323`), including the diff-output prefetch (`diff.c:7430-7471`, gated by format) and the rename-detection prefetch (`diffcore-rename.c:101-129`, `:837-899`, `:989-992`, `:1576-1579`). Under the env var none of them can spawn a child.
2. **Secondary gate.** `setup.c:1066` sets `fetch_if_missing = 0`, so the ODB read path does not even attempt: `odb.c:598-601` requires `fetch_if_missing && repo_has_promisor_remote(...)`.
3. **Inheritance in the census.** `tools/souji-census.sh` unsets inherited `GIT_*` first (`:139-143`) and then exports `GIT_NO_LAZY_FETCH=1` (`:146-147`); it is exported, so all `git -C …` calls (`:852`, `:858`, `:862`, `:866`, `:947-955`, `:1076`, `:1104`, `:1402-1516`), the `git config --file` guard calls (`:589`, `:592`, `:635`) and the selftest git calls inherit it. Verified command set: `rev-parse`, `worktree list`, `for-each-ref`, `rev-list --count`, `config`, `ls-files`, `check-attr`, `status`, plus selftest `add`/`write-tree`/`update-ref`/`symbolic-ref` — **no `fetch`/`pull`/`clone`**.
4. **Caveats that are not fetches.**
   - The gate converts a fetch into a *failure*: a genuine partial clone whose rename detection needs a missing blob still dies, either via `promisor_remote_get_direct`'s final `die("could not fetch %s from promisor remote")` (`promisor-remote.c:318-321`, when the missing oid `is_promisor_object`) or via `diff.c:4616-4617` `die("unable to read %s")` after the refused prefetch. Result: `status-unverifiable`, no network, no object write.
   - `GIT_NO_LAZY_FETCH` does not stop an explicit `fetch`; the census has none.
   - Version floor: the `fetch_objects` gate exists at v2.55.0 and v2.56.0; on git < 2.45 the variable is undocumented/ignored (sibling `ScoutGitHostVersion.md` establishes the 2.45 floor). The script contains no version gate.
   - The one-time "lazy fetching disabled" warning goes to the git process's stderr, which `count_dirty` discards (`:947-955`).

## Findings

**F1 (high, confirmed from source) — root cause is `diffcore_std`'s unconditional `repo_has_promisor_remote`, and the die is a hard exit 128.** Chain in Q1. The observed `bad boolean config value` is expected behaviour, correctly documented at `tools/souji-census.sh:105-107` and correctly oracled by fixture case_07. No repair needed; do not "fix" the guard to type-check this key unless the documented degrade is intentionally changed.

**F2 (high, confirmed) — `GIT_NO_LAZY_FETCH=1` is a real no-fetch guarantee, enforced in `fetch_objects` (`promisor-remote.c:34-42`), not merely by `fetch_if_missing`.** The scan-arm wording "cannot fetch under GIT_NO_LAZY_FETCH=1" (`:644`) is accurate. For precision it could name the gate (`fetch_objects` returns -1 before spawning), but this is wording, not a defect.

**F3 (medium) — silent degradation: the promisor-boolean row carries no diagnostic.** `count_dirty` discards status stderr (`:947-955`) and emits `status-unverifiable` with no stderr line, whereas the filter-driver skip prints `souji-census: status-skipped: filter-driver-bound (<repo>)` (`:940`). An operator sees `dirty=0, status-unverifiable` and cannot tell "bad promisor boolean" from "missing promisor object" from any other status failure. Advisory: either capture status stderr and print one bounded `status-skipped: git-status-failed (<repo>)` line, or state in the header that promisor-degraded and partial-clone-degraded rows are deliberately silent. This is the only operability gap I found in this item's scope.

**F4 (medium) — fixture coverage stops at complete repositories.** Fixture case_06 (`tests/fixtures/r15-census-config.py:1117-1131`) and case_07 only build complete repos, where no blob is missing, so the prefetch/rename path can never fire. The header's stronger case — a genuine partial clone under the census — is unexercised: under `GIT_NO_LAZY_FETCH=1` it cannot fetch, but `git status` can still fail (`could not fetch …` / `unable to read …`) and yield `status-unverifiable`, with the one-time warning suppressed. Advisory: one partial-clone fixture (local `file://` origin + `--filter=blob:none`, plus a rename candidate whose deleted blob is absent) would pin the no-fetch guarantee and the grade together.

**F5 (low) — fixture header prose is stale, oracle is right.** `tests/fixtures/r15-census-config.py:44-49` and `:477` still say invalid promisor booleans "refuse fail-closed as could-not-evaluate", while the round-16 revision bullet at `:14-21` and case_07 at `:1136-1139` say `status-unverifiable`. `UNSAFE` is only a directory name; case_07 runs `single_positive` on a per-repo root, so there is no oracle contradiction — but the stale sentences will mislead a reviewer. Fix belongs with the fixture's owner.

**F6 (low) — value table for reviewers.** Only non-boolean, non-numeric values die (`promisor = maybe`); `promisor = 2` is valid and true, `promisor` bare is true, `promisor =` empty is false, `promisor = false|no|off|0` is not a promisor marker (callback returns early). This matches the fixture's benign set (`:579-587`); worth stating explicitly if the fixture comment is revised.

## Remaining unknowns

- I did not execute `git status` against a repository carrying an invalid `remote.*.promisor` (probe rule): the chain is read from v2.55.0 source and cross-checked at v2.56.0, not reproduced. L1's observation is the empirical ground truth.
- I did not enumerate the scanned fleet for actual partial clones (`census/operator-sweep-20261019/` is off-limits; no real census run), so the reachability of F4's shape in this lane is unmeasured.
- Behaviour on git < 2.45 is inferred from the sibling version-floor finding, not observed here.
- Whether `repo_config` in `promisor_remote_init` re-reads `config.worktree` in every invocation shape was not traced beyond `repo_config` semantics; the die for a repo-local `config` key is confirmed.

STATUS: no behavioural probe executed; `git status` failure mechanism is source-verified (v2.55.0, spot-checked v2.56.0), not re-run. One out-of-enumeration probe (`git --version`) was run once and is disclosed below; no claim in this report depends on it.

## Commands

All bash calls, verbatim and in order:

```bash
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l
```

```bash
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --stat; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -8 cbf688ab2ab28e38103e5a9417ca525b5f2ed423
```

```bash
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -i -E 'promisor|partialclone|lazy|remote\.|GIT_NO_LAZY'
```

```bash
git --version; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log -1 --format='%H %s' -- tools/souji-census.sh && git diff --quiet cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh && echo SAME_AS_CBF || echo DIFFERS
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'status-unverifiable|status-skipped|cfg_soft|config-unsupported|guard_git_config' tools/souji-census.sh
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'GIT_NO_LAZY_FETCH|2>/dev/null; then|status-skipped: filter|--type=bool|remote\.\*\.promisor' tools/souji-census.sh; echo ---; grep -n -c 'git -C' tools/souji-census.sh
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'status --porcelain|git -C|git config|git rev-parse|git worktree' tools/souji-census.sh
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n -i -E 'promisor|partialclone' ; echo "---boundary---"; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r14-census-boundary.py | grep -n -i -E 'promisor|partialclone'
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'def single_positive|def positive_problems|UNSAFE =|def case_03|UNSAFE' tests/fixtures/r15-census-config.py
```

Non-shell tools used: `read`, `grep`, `glob` on the named files/URLs above. No installs, no updates, no pacman transactions. `git --version` (call 4) is outside the enumerated probe list; it read only the version string and supports no claim here.
