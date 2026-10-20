STATUS: DONE — C1 landed in tools/souji-census.sh: D1 (`--untracked-files=normal` on the dirty count) and D2 (`info/attributes` hardlink/non-regular → per-repo `error` row) implemented, selftest 38→49 checks 0 failed, r15 20/20 and r14 12/12 fixtures still pass, plain-fleet rows byte-identical to base.

# CensusD1D2 — C1 operability (D1 + D2) in `tools/souji-census.sh`

Round 17 / WAVE 1 / lane souji-shokunin, base `5fa6017ddcae9f6bd4412df44765f6360cb16294`.
File owned: `tools/souji-census.sh` only. Base bytes `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` (1877 lines) → patched `cd41d26aca55f4859dd67762e4cd1cf22b4169ee75eae9396896c622c4fd81fa` (2064 lines). No other lane file touched (`git status --porcelain -- tools/` shows my one file plus sibling seats' files).

## Diff summary (216 insertions, 29 deletions)

| hunk | what |
|---|---|
| header `:2-8` | round-17 summary line |
| header `:35-40` | `dirty` field now documents explicit `--untracked-files=normal` |
| header `:97-122` | one `Round-17` paragraph: D1 scope (repo-local/included/config.worktree `no|all`), D2 class, degrade contract, directory/dangling-symlink outcomes, "every other metadata entry keeps exit 2" |
| `guard_git_files` `:533-576` | single `stat -L -c '%F %h'` type probe per entry (no open); `info/attributes` hardlink/non-regular → `meta_soft`, `soft=1`, **loop continues**; all other entries keep `protected_fail`; returns 1 only after the loop |
| new `:629-655` | `META_SOFT_REASON/PATH`, `meta_soft`, `emit_soft_diag` |
| `guard_git_surface` `:869-871`, `:903/921/945/963`, `:872` site | resets `META_SOFT_*` per repo; five `guard_git_files … \|\| exit 2` → `\|\| soft=1` (repo gitdir, common dir ×2, linked admin ×2); no early return anywhere |
| `count_dirty` `:1108-1114` | `status --porcelain --ignore-submodules=all --untracked-files=normal -- .` (flag before `--`, long form) |
| `worktree_extra_flags` `:1236`, `census_one` `:1256` | both diagnostic prints now `emit_soft_diag` (metadata finding wins over config finding) |
| selftest `:1898-2005` | hygiene fleet: `untrackedcfg`, `attrslink` (hardlink), `attrsfifo` (FIFO), `benign`; +11 checks |

Exact emitted shapes:

```text
stderr: souji-census: git-metadata-unsupported git-metadata-hardlink /var/tmp/.../a-reghl/.git/info/attributes
stderr: souji-census: git-metadata-unsupported git-metadata-nonregular /var/tmp/.../a-fifo/.git/info/attributes
row:    <repo>\t0\t0\t0\t0\t\terror
```

The claim text `git-metadata-unsupported <reason> <path>` is emitted literally (no colon, no parentheses), per SentinelFifoHostile's alignment note; `config-unsupported: <reason> (<repo>)` shape is unchanged.

## Parent constraint report

**(1) no early return / no skipped whole-run guard.** The loop finishes (a `objects/info/alternates` FIFO or hardlink after `info/attributes` still refuses), and the common-dir, `guard_alternates` and registration guards all run after the soft finding.
- paired hardlinked `info/attributes` + hardlinked `objects/info/alternates` → `rc=2`, `path-protected: git-metadata-hardlink (…/.git: …/objects/info/alternates)`, 0 stdout bytes.
- gitfile→gitdir, admin `info/attributes` FIFO + common-dir hardlinked `config`, via `--include-root` (a `.git`-file child is never a row by design) → `rc=2`, `path-protected: git-metadata-hardlink (…/E/common: …/E/common/config)`.
- protected include precedence: FIFO `info/attributes` + `[include] path=<synthetic store>/x.conf` → `rc=2`, `path-protected: include-protected`, 0 stdout bytes. Degradation does not swallow a protected refusal.
- single-entry controls: FIFO `objects/info/alternates` alone → `rc=2 git-metadata-nonregular`; hardlinked `index` → `rc=2 git-metadata-hardlink`.

**(2) stat-`-L` type check before any open; defined edge outcomes.** Classification is one `stat -L -c '%F %h'` per entry (statx in trace), before any git call.
- symlink→FIFO *inside* the gitdir → `error` row + `git-metadata-nonregular` (link target `attrs-fifo` in `info/`).
- symlink→`/dev/zero` → **`rc=2` `path-protected: git-metadata-symlink`** from the pre-existing r14 `guard_git_links` rule (a symlink leaving the gitdir is refused before any open; 0.098 s, no open of the link). Same for any symlink whose target leaves the gitdir — this fires before the D2 classification, so such a device link can never be degraded, only refused. Documented consequence: a `symlink→non-regular` is degraded only when the link resolves inside its own gitdir.
- dangling symlink → **treated as absent** (`stat -L` fails); also pre-empted in practice by `guard_git_links` when it leaves the gitdir (`rc=2 git-metadata-symlink`, observed).
- directory at `info/attributes` → **accepted, normal row** (git opens it, gets EISDIR, sees no attributes); observed `clean` row and the observed `openat(".git/info/attributes") = 4` in strace.
- symlink→regular file, `nlink=1` → accepted (pre-existing behaviour); `nlink=2` → degraded as hardlink.
- no-open proof: `strace -f -e trace=%file` over a fleet containing only FIFO, symlink→FIFO and hardlinked attributes → **zero** `open*()` of those three paths (only `statx`/`newfstatat`/`readlink`); the one `.git/info/attributes` open in that trace is the benign neighbour's ENOENT probe.

**(3) linked worktree / shared commondir.** Admin-dir FIFO `info/attributes` on a real `git worktree add` worktree: the owner row becomes `error` (the registration guard's `guard_git_files "$admin"` is soft), the linked worktree is never its own row (by design), exit 0, exactly one stderr line naming the admin's attributes file. Same result when the linked worktree itself is the `--include-root` (common-store FIFO reached through `commondir`): `error` row, exit 0, one line. No block.

**(4) fixtures untouched.** `tests/fixtures/r15-census-config.py` and `r14-census-boundary.py` were not edited (run read-only against my bytes); new cases live only in the census selftest. No new fixture file, no matrix runner — those are other seats.

## Before/after counts

| check | base `64a60fd0…` | patched `cd41d26a…` |
|---|---|---|
| `bash -n` | 0 | 0 |
| `shellcheck -S warning` | 0 findings | 0 findings |
| `--selftest` | 38 checks, 0 failed | **49 checks, 0 failed** |
| r15 config fixture | (r16 record 20/20) | **20/20 PASS** (`github`… ids R15CFG-01..20, `SUMMARY total=20 failed=0`) |
| r14 boundary fixture | (r16 record 12/12) | **12/12 PASS** (`SUMMARY total=12 failed=0`) |
| plain synthetic fleet (clean/dirty/untracked-dir/no-remote) | — | rows **and** stderr byte-identical to base |

Red/green on the routed defects:

| arm | base 5fa6017 | patched |
|---|---|---|
| only-untracked dirt + `status.showUntrackedFiles=no` | `… dirty=0 … clean` (**false clean**) | `… dirty=2 … dirty` |
| `status.showUntrackedFiles=all`, untracked dir with 2 files | `dirty=4` (no collapse) | `dirty=3` (collapse preserved) |
| same key via `include.path` | `0` | `3` |
| same key via `config.worktree` + `extensions.worktreeConfig=true` + `repositoryformatversion=1` | `0` | `3` |
| FIFO / hardlinked / symlink→FIFO `info/attributes` | `rc=2`, zero rows for the whole fleet | `rc=0`, that repo `error`, neighbours measured |
| `info/attributes` directory | normal row | normal row (unchanged) |

## Risks / disclosures

- **Capability reading of "no git call".** After the finding I still run `guard_git_config`, the commondir chain, `guard_alternates` and `guard_worktree_registrations`; those use `git config --file <cfg> --no-includes --list` and `--get-all`, which take an explicit file and cannot read `info/attributes`. A literal "no git process at all after detection" reading would instead drop protected-include refusal (FIFO attrs + `[include] path=<store>` would become an `error` row with exit 0 instead of exit 2) and break the documented "a soft finding never stops the scan" contract. Per SentinelFifoHostile S-C3 and CriticC1Harm §3/§6 I implement the capability reading; the precedence test above pins it. If L1 wants the stricter reading, the change is a `meta_bad_dir` short-circuit in `guard_git_surface` plus those four skips, and the precedence test must be renegotiated.
- Error rows keep the existing placeholder contract (`worktrees=0`, empty mtime) — including a degraded repo that really has 2 worktrees; unchanged from r16.
- `--compare` still computes numeric deltas against `error` placeholders (r16 S6, out of scope, not touched).
- A symlink→device/FIFO that leaves the gitdir is refused whole-run by the r14 link guard before D2 can see it (disclosed above); live exposure is nil either way (ScoutFleetInfoAttrs: 0/22 gitdirs have `info/attributes`).
- `tests/fixtures/r17-census-hygiene.py` and `census/round-17/run-matrix.py` are other seats' files; the counting command in the ticket cannot be run by this seat.

## Commands (excerpt; all under `/var/tmp/souji-r17-CensusD1D2`, since removed)

```sh
bash -n .../tools/souji-census.sh; shellcheck -S warning .../tools/souji-census.sh
bash .../tools/souji-census.sh --selftest                     # 49 checks, 0 failed
python3 tests/fixtures/r15-census-config.py --tool ...        # 20/20
python3 tests/fixtures/r14-census-boundary.py --tool ...      # 12/12
git show 5fa6017:tools/souji-census.sh > base.sh; bash base.sh --selftest   # 38 checks
# A/B and red/green fleets: direct-no / direct-all / inc-no / wt-no; a-fifo / a-fifolink / a-reghl / a-dir / a-reglink / a-benign
# paired: hardlink-attrs + hardlink-alternates; gitfile+commondir-hardlink-config; FIFO-attrs + protected include
strace -f -qq -e trace=%file -o st.log .../souji-census.sh --root <fleet>
```

Tooling installed/upgraded: none.
