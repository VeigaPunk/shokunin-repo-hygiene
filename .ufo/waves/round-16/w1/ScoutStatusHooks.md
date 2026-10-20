# ScoutStatusHooks — does `git status --porcelain` run hooks or write the index?

Seat: SoujiR16.ScoutStatusHooks · Round 16 · read-only recon · 2026-10-20
Target: `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (1784 lines)
Host git: `git version 2.56.0` (recorded in `census/round-16/c1-matrix.json` field `git_version`;
local man pages at `/usr/share/man/man1/git*.1.gz`, `/usr/share/man/man5/githooks.5.gz` contain
the same text as the web docs below).
All URLs accessed **2026-10-20**.

## Question

Does `git status --porcelain` (invoked with `GIT_OPTIONAL_LOCKS=0` and `--no-optional-locks`)
ever run a hook — `post-index-change`, the fsmonitor hook, or any other — or write the index?
And is `-c core.hooksPath=/dev/null` therefore belt-and-braces?

## Verdict

- **Index write: no.** With optional locks disabled, `git status` does not perform its
  default index write-back. `post-index-change` is invoked **only when the index is written**,
  so that hook cannot fire from the census's status call.
- **fsmonitor hook: yes, still runs.** Optional locks do not suppress it; `core.fsmonitor`
  naming a hook command is executed during status's index refresh. So
  `-c core.fsmonitor=false` at `:947` is **load-bearing**, not belt-and-braces.
- **`core.hooksPath=/dev/null` at `:948`: belt-and-braces for the current invocation.** It is
  strictly redundant with `GIT_OPTIONAL_LOCKS=0` (`:142`) plus `--no-optional-locks` (`:947`)
  for the only hooks-directory hook status would have run (`post-index-change`). It is *not*
  what disables the fsmonitor hook — an fsmonitor command path is executed from the config
  value and is unaffected by `core.hooksPath`. Keep it: it is the only defense if the optional-
  locks suppression ever regresses, because the config guard deliberately accepts any
  `core.hooksPath` value (`:640-646`) and never path-guards it.
- **Operability (C1): no defect in the shipped invocation.** The header claim (`:101-102`) and
  the guard comment (`:640-646`) match the code; "every status carries …" holds because there
  is exactly one status call site.
- **Calibration (C2) gap:** the fixture has **no positive control** for the `post-index-change`
  sentinel. Deleting `-c core.hooksPath=/dev/null` from `:948` is predicted — from the observed
  pre-harm differential (F7), not from a mutant run — to leave all 20 r15-config cases green.
  The fsmonitor sentinel *is* independently live (observed firing on the pre-harm arm). See
  F7/F8.

## Observed facts

### F1 — one status call site, used for the main repo and every linked worktree (high confidence)

`count_dirty()` is defined at `:935-952`; its only git command is:

```
947:  if ! st=$(git -C "$1" --no-optional-locks -c core.fsmonitor=false \
948:      -c core.hooksPath=/dev/null -c core.excludesFile="$ex" \
949:      -c core.attributesFile="$at" status --porcelain --ignore-submodules=all -- . \
```

Callers: `:1115` (`census_one`, main work tree row) and `:1072` (`worktree_extra_flags`,
each present linked worktree). `GIT_OPTIONAL_LOCKS=0` is exported once at `:142`, after every
inherited `GIT_*` variable is unset, so neither the environment nor repo config can re-enable
optional locks. The header statement at `:101-102` ("every status carries
`-c core.hooksPath=/dev/null -c core.fsmonitor=false`") is therefore literally true.
No other `status` invocation exists in the production path. The only index-writing / mutating
git calls in the file (`git add -A` at `:1402`, plus `write-tree` / `commit-tree` /
`update-ref` / `worktree add`) run only inside the `--selftest` fixture world (`:1402-1412`)
and in fixtures created by `tests/fixtures/*.py`, never against an operator repository.

### F2 — `git status` writes the refreshed index by default (high confidence)

`git-status(1)`, BACKGROUND REFRESH:

> "By default, `git status` will automatically refresh the index, updating the cached stat
> information from the working tree and writing out the result."

and, for exactly this census pattern:

> "Scripts running `status` in the background should consider using `git --no-optional-locks
> status`"

### F3 — optional locks suppress that write (high confidence)

`git(1)`, ENVIRONMENT VARIABLES:

> "If this Boolean environment variable is set to false, Git will complete any requested
> operation without performing any optional sub-operations that require taking a lock. For
> example, this will prevent `git status` from refreshing the index as a side effect."

`git(1)`, OPTIONS: `--no-optional-locks` is documented as "Do not perform optional operations
that require locks. This is equivalent to setting the `GIT_OPTIONAL_LOCKS` to `0`." The census
carries the environment variable *and* the flag; they are documented as equivalent, so the
duplication is redundant rather than harmful.

### F4 — `post-index-change` fires only on an index write (high confidence)

`githooks(5)`:

> "This hook is invoked when the index is written in `read-cache.c do_write_locked_index`."

With no index write (F2/F3), status cannot reach this hook. That is the whole hooks-directory
surface `git status` could otherwise touch.

### F5 — the fsmonitor hook is a distinct channel driven by `core.fsmonitor` (high confidence)

`githooks(5)`, fsmonitor-watchman:

> "This hook is invoked when the configuration option `core.fsmonitor` is set to
> `.git/hooks/fsmonitor-watchman` …"

`git-config(1)`, `core.fsmonitor`:

> "Otherwise, this variable contains the pathname of the "fsmonitor" hook command."

The hook is executed from that config value during status's index refresh, independent of
`GIT_OPTIONAL_LOCKS` and independent of `core.hooksPath`. Only `-c core.fsmonitor=false`
(boolean support git ≥ 2.36; host is 2.56.0) neutralizes it. The peer seat
`ScoutFsmonitorValues` covers the boolean/hook-path semantics and version caveats in depth;
this seat confirms the *hook-vs-index-write* split only.

### F6 — the overrides are effective and `/dev/null` disables hooks (high confidence)

`git(1)`: "The value given will override values from configuration files." Command-line `-c`
is applied last, so repo config (including `include.*`/`includeIf.*` and `config.worktree`)
cannot outvote either override.

`git-config(1)`, `core.hooksPath`:

> "You can also disable all hooks entirely by setting `core.hooksPath` to `/dev/null`."

### F7 — empirical differential from the lane's own matrix (high confidence)

`census/round-16/c1-matrix.json`, arm `pre-harm` (`a31642d`), case `R15CFG-08`, observed detail:

> `env: GIT_NO_LAZY_FETCH values [...] want all 1; exec: fsmonitor sentinel sentinel-fsmonitor
> was created`

No `exec: hooks sentinel …` problem is reported. `a31642d` has `GIT_OPTIONAL_LOCKS=0` at
`:73` and `git -C "$1" --no-optional-locks status --porcelain -- .` at `:131` — so it carries
both optional-lock forms but **neither** `-c core.fsmonitor=false` **nor**
`-c core.hooksPath=/dev/null`. In that same invocation:
the fsmonitor hook executed (marker created), and the `post-index-change` hook did **not**
(marker absent). This is a direct, same-process differential confirming F3/F4/F5: status
executes the fsmonitor command under optional locks, and does not write the index.
The changed arm (`cbf688a`) passes all 20 r15-config cases including the sentinel class
(`failed: 0`); `r14-harm` (`cc21683:710-712`) already carried both overrides.

### F8 — the hooks sentinel has no positive control in the fixture (high confidence)

`tests/fixtures/r15-census-config.py`:

- `init_repo` (`:314-325`) runs `git init`, writes `kept.txt`, `git add`, `git commit`,
  `update-ref`, and only **then** appends `extra_config`.
- The `s-hooks` sentinel (`:390-397`) creates `post-index-change` and `pre-index-change`
  scripts in `.git/githooks` and appends `core.hooksPath = …` **after** `init_repo`.
- The other sentinel repo `r-hooks-marker` (`:534-542`) is explicitly "presence-only (asserted
  nowhere)".

So no test step ever writes an index while a hooks-directory hook is configured. The sentinel's
absence is indistinguishable from a dead sentinel: it validates the *combined* invocation but
cannot detect removal of `-c core.hooksPath=/dev/null` while optional locks remain in place.
The fixture's own comment (`:925`) concedes exec sentinels are asserted only in safety-class
cases because "a correct pre-harm arm may legitimately fire them" — observationally, only the
fsmonitor one does.

### F9 — no other production census command can run hooks (high confidence)

Production git invocations at the pinned revision, from `:852-1104`:
`worktree list` (`:852`, `:1076`), `for-each-ref` (`:858`), `rev-list --count` (`:862`,
`:866`), `config --get` (`:876`), `config -z --get-regexp` (`:910`), `ls-files`/`check-attr`
(`:922-925`), `rev-parse --is-inside-work-tree` (`:1104`). None refreshes the index and none
is a documented hook-invoking command in `githooks(5)`. `--ignore-submodules=all` (`:949`) is
documented as hiding all submodule changes, so submodule work trees are not inspected and no
per-submodule git process is spawned. `pre-auto-gc` requires
`git gc --auto`, which `git-gc(1)` describes for "common porcelain operations that create
objects"; status creates no objects. So `git status` is the entire hook surface.

## Inference (not directly observed)

1. **`-c core.hooksPath=/dev/null` becomes load-bearing under a specific regression**
   [INFERENCE]. If `--no-optional-locks`/`GIT_OPTIONAL_LOCKS=0` were dropped (or an
   index-writing command added to the production path), status/that command writes the index,
   `post-index-change` runs from the repo-controlled `core.hooksPath`, and — because the config
   guard intentionally accepts any `core.hooksPath` value (`:640-646`) — arbitrary
   repo-controlled code executes before any measurement. Deleting `:948` today changes nothing
   observable; deleting `:142`/`--no-optional-locks` *and* `:948` makes hook execution live.
   Both must stay.
2. **Removing `-c core.fsmonitor=false` is immediately observable and harmful** [F7 observed,
   consequence inferred]. The pre-harm arm shows the repo-owned fsmonitor script running under
   the census's own env. The config guard does not path-guard `core.fsmonitor` values, so the
   override is the only barrier.
3. **The two overrides neutralize two different channels, so "belt-and-braces" applies only to
   hooksPath** [INFERENCE from F4/F5]. A reviewer reading `:101-102` could misread the pair as
   mutually redundant; the code comment at `:640-643` ("overridden on every status") is
   accurate but does not say which flag covers which channel.

## Residual unknowns

- **No executed experiment by this seat.** The probe rule forbids running any copy of the
  census. F2-F6 rest on docs; F7 is observation of another seat's recorded run, not a run I
  performed. (The fsmonitor peer also did not execute; its source reading agrees.)
- **Old-git behavior.** `-c core.fsmonitor=false` as a boolean requires git ≥ 2.36; the script
  has no version floor (`:1775` area checks presence only). On ≤ 2.35.1 the value is treated as
  a hook pathname. Out of scope here (peer seat owns it), but it means "belt-and-braces" is
  only fully true on modern git for the fsmonitor side.
- **Future git versions** could add a new hook invocation to `status`; `core.hooksPath=/dev/null`
  would cover hooks-directory hooks but not a config-path command (as fsmonitor shows).
- I did not verify the exact index-write code path in git source; the claim "no write" rests on
  the two docs plus the absence of the hook marker in the pre-harm arm.

## Sources (URL · quote ≤25 words · accessed 2026-10-20)

| # | URL | Quote |
|---|---|---|
| S1 | https://git-scm.com/docs/git-status#_background_refresh | "By default, `git status` will automatically refresh the index … and writing out the result." (23 words) |
| S2 | same as S1 | "Scripts running `status` in the background should consider using `git --no-optional-locks status`" (12 words) |
| S3 | https://git-scm.com/docs/git#Documentation/git.txt-GITOPTIONAL_LOCKS | "this will prevent `git status` from refreshing the index as a side effect" (13 words) |
| S4 | https://git-scm.com/docs/git | "Do not perform optional operations that require locks. This is equivalent to setting the `GIT_OPTIONAL_LOCKS` to `0`." (17 words) |
| S5 | https://git-scm.com/docs/githooks#_post_index_change | "This hook is invoked when the index is written in `read-cache.c do_write_locked_index`." (13 words) |
| S6 | https://git-scm.com/docs/githooks#_fsmonitor_watchman | "This hook is invoked when the configuration option `core.fsmonitor` is set to `.git/hooks/fsmonitor-watchman`" (15 words) |
| S7 | https://git-scm.com/docs/git-config#Documentation/git-config.txt-corehooksPath | "You can also disable all hooks entirely by setting `core.hooksPath` to `/dev/null`." (14 words) |
| S8 | https://git-scm.com/docs/git | "The value given will override values from configuration files." (10 words) |
| S9 | https://git-scm.com/docs/git-config#Documentation/git-config.txt-corefsmonitor | "Otherwise, this variable contains the pathname of the "fsmonitor" hook command." (12 words) |
| S10 | https://git-scm.com/docs/git-gc | "common porcelain operations that create objects … run `git gc` automatically" (10 words) |

## Concrete follow-ups (advisory, for L1)

1. Keep both `-c` overrides and both optional-lock forms; do not "simplify" `:947-948`.
2. Add a positive control for `post-index-change` liveness (e.g., in the fixture's world build,
   touch `kept.txt` and run `git add -- kept.txt` in `s-hooks` *after* the hook config is
   written, proving the sentinel can fire). Without it, `:948` is untested; alternatively add a
   mutation arm that strips `--no-optional-locks`+`GIT_OPTIONAL_LOCKS=0` and expects the hooks
   marker.
3. Optionally clarify `:101-102`/`:640-643` that `core.fsmonitor=false` is the fsmonitor guard
   and `core.hooksPath=/dev/null` guards the index-write hook channel — this prevents a future
   "dead flag" removal.

STATUS: none — read-only recon completed; all listed documents were reachable and the only
failed probes were nonexistent man paths (`/usr/share/man/man5/git-config.5.gz`) and
backslash-escaped grep patterns, which did not affect any finding.

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools tests/fixtures | sed -n '1,80p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -E 'GIT_OPTIONAL_LOCKS|no-optional-locks|hooksPath|fsmonitor|status|porcelain|protected|namespace|promisor|partialClone|alternateRefs' | sed -n '1,200p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --short cbf688ab2ab28e38103e5a9417ca525b5f2ed423 cc21683 b410186 2>&1; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -1 --format='%h %s' cbf688ab2ab28e38103e5a9417ca525b5f2ed423
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '1,120p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '130,180p;600,700p;925,1000p'
gzip -dc /usr/share/man/man1/git.1.gz | grep -n -A6 -B2 'GIT_OPTIONAL_LOCKS\|optional-locks' | sed -n '1,60p'
gzip -dc /usr/share/man/man1/git-status.1.gz | grep -n -A14 'BACKGROUND REFRESH' | sed -n '1,40p'
gzip -dc /usr/share/man/man5/git-config.5.gz | grep -n -A18 'core\.hooksPath' | sed -n '1,60p'; echo '---FSMONITOR---'; gzip -dc /usr/share/man/man5/git-config.5.gz | grep -n -A22 'core\.fsmonitor' | sed -n '1,45p'
gzip -dc /usr/share/man/man1/git-config.1.gz | grep -n -B2 -A16 'core\.hooksPath' | sed -n '1,60p'
gzip -dc /usr/share/man/man1/git-config.1.gz | grep -n -B2 -A26 'core\.fsmonitor' | sed -n '1,70p'
gzip -dc /usr/share/man/man5/githooks.5.gz | grep -n -B3 -A14 'post-index-change' | sed -n '1,50p'
gzip -dc /usr/share/man/man1/git-config.1.gz | grep -n -A30 '^\.IP.*fsmonitor\|core.*fsmonitor' | sed -n '1,80p'
gzip -dc /usr/share/man/man5/githooks.5.gz | grep -n -A16 'post.index.change' | sed -n '1,50p'
gzip -dc /usr/share/man/man1/git-config.1.gz | grep -n -A20 'hooksPath' | sed -n '1,50p'
ls -l /usr/share/man/man5/githooks.5.gz; gzip -dc /usr/share/man/man5/githooks.5.gz | wc -l; gzip -dc /usr/share/man/man5/githooks.5.gz | grep -c 'index'
gzip -dc /usr/share/man/man5/githooks.5.gz | grep -n 'index.change\|fsmonitor' | sed -n '1,30p'
for r in a31642d cc21683 b410186; do echo "== $r"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify "$r^{commit}" 2>&1; done
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show a31642d:tools/souji-census.sh 2>/dev/null | grep -n -B3 -A6 'status --porcelain' | sed -n '1,40p'; echo '=== cc21683 ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cc21683:tools/souji-census.sh 2>/dev/null | grep -n -B3 -A6 'status --porcelain' | sed -n '1,40p'
for r in a31642d b410186; do echo "== $r"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show "$r":tools/souji-census.sh 2>/dev/null | grep -n 'GIT_OPTIONAL_LOCKS\|no-optional-locks\|core.fsmonitor\|core.hooksPath' | sed -n '1,20p'; done
gzip -dc /usr/share/man/man1/git-gc.1.gz | grep -n -B4 -A18 'AUTO\|auto' | sed -n '1,60p'
gzip -dc /usr/share/man/man1/git.1.gz | grep -n -B2 -A10 '^\.IP.*\\-c\|Pass a configuration parameter' | sed -n '1,40p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'status --porcelain\|status -s\|git -C' | sed -n '1,60p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '1030,1145p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- census/round-16 | sed -n '1,40p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -A12 '^count_dirty()' | sed -n '1,20p'; echo '---'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'GIT_OPTIONAL_LOCKS\|hooksPath\|fsmonitor' | sed -n '1,30p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n -B8 -A12 'R15CFG-08' | sed -n '1,60p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n -B4 -A18 '^def init_repo' | sed -n '1,40p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n 'run_git\|"add"\|update-index\|sentinel-neutral\|positive control\|liveness' | sed -n '1,40p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '610,640p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '90,140p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '330,410p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '520,560p;835,935p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n -i 'hooksPath\|fsmonitor\|post-index\|marker\|hook' | sed -n '1,80p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '700,930p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -i 'git version\|version 2\|minimum\|2\.36\|2\.35' | sed -n '1,30p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '386,404p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'count_dirty' | sed -n '1,20p'
gzip -dc /usr/share/man/man5/githooks.5.gz | grep -n '^\.SS\|^\.SH' | sed -n '1,80p'
gzip -dc /usr/share/man/man5/githooks.5.gz | sed -n '536,546p'
```
