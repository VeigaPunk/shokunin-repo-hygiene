# R14 BoundaryReviewGit — census git traversal and env overrides (C2 final re-review)

Seat: SoujiR14.BoundaryReviewGit (reviewer, leaf). Supersedes the earlier C2 re-review in this file.

## Evidence basis

- Static reading and `bash -n` only. No census, selftest, fixture, strace, spy, or git experiment was run by this seat.
- Pins re-read by this seat (`sha256sum`): `tools/souji-census.sh` = `034a518e423d206e7de94cc62e2df2695bd6be33a497a5d4919bdebae47317a3` (1515 lines); `tests/fixtures/r14-census-boundary.py` = `a118225bce416fe8ac7f5ccd5e5a6745d37ade02cc9f9aeda6429e36c788825f`. Both match the CensusBoundary IRC pins.
- Stale pin: `.ufo/waves/round-14/w1/CensusBoundary.md` still lists 1453 lines and `2cf44ee9…`. That is the pre-N1 file. CensusBoundary should refresh its table.
- Tool installs/updates this seat: none. Observed git 2.55.0 (earlier turn).
- Bash semantics cited from `man bash`: command substitutions clear `-e` unless `inherit_errexit` is set. The C2 fix sidesteps this by putting `|| exit 2` on every capture, which is correct regardless of that option.
- Files read: `tools/souji-census.sh` (lines 394-1088 and the main section), fixture grep for R14C2-09/10/11 and env setup, CensusBoundary report (read only).

## Disposition of the N-series from the previous pass

| id | sev | status (static) | evidence |
|---|---|---|---|
| N1 | HIGH | closed | Admin `commondir` and admin `gitdir`/`HEAD`/links are guarded from `guard_worktree_registrations` (lines 537-577) before `worktree list` runs. The call path is `census_one` → `guard_git_surface` (line 823) → rev-parse (835) → `worktree_extra_flags` (848, `|| exit 2`). Refusal in the inner `$(…)` now propagates. |
| N2 | MEDIUM | closed | Every capture of a guard now has `|| exit 2`: lines 403, 412, 435, 447, 530, 553, 586, 601, 623, 638, 790, 822, 848, 951, 983, 1062. The only captures without it are the `if can=$(…)`/`if omp=$(…)` probes in `build_protected_roots` (lines 241, 256), which are intentionally tolerant; a failed probe skips a canonical root only, and the lexical roots are still seeded. |
| N3 | MEDIUM | closed | `guard_alternates_file` recurses with depth; depth > 5 refuses (`git-alternates-depth`); symlinked `info/alternates` refuses; a quoted (unparsed) line refuses; each hop is `guard_target`-resolved before recursion. Relative alternates resolve against `objects/` (line 433). |
| N4 | LOW | closed | `stat -L -c %h` at line 462. |
| N5 | LOW | closed, differently | `count_dirty` now passes `-c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` (lines 686-688). An explicit config key replaces the XDG default, so the default `$XDG_CONFIG_HOME/git/{ignore,attributes}` is not read by `status`. `rev-parse`/`rev-list`/`for-each-ref`/`worktree list` do not read those files. |
| N6 | LOW | closed | `guard_git_links` uses `find -P "$dir" -type l -print0` with no `-maxdepth` (line 452). |

Earlier F1-F9 remain closed as recorded in the previous pass.

## New findings (final bytes)

### P1 — LOW-MEDIUM — `guard_git_links` fails open when `find` cannot list a directory (line 452)

`while … done < <(find -P "$dir" -type l -print0 2>/dev/null || true)` ignores find's exit status and stderr. A subdirectory inside the gitdir that is traversable but not readable (`--x`, no `r`) is not listed, so a symlink whose name is known to git (for example `refs/heads/<name>`) is never resolved or checked, and `git status` follows it. Git itself can follow such a name without listing the directory. This needs an owner-initiated `chmod` inside a `.git` directory, so it is not a default path; it still violates the stated "fail closed" contract.

Fix: refuse before the walk when any directory inside the gitdir is not readable, so find never silently skips a subtree:
```bash
unreadable=$(find -P "$dir" -type d ! -readable -print -quit 2>/dev/null) || unreadable="?"
[ -z "$unreadable" ] || protected_fail "git-metadata-unavailable" "$dir" "${unreadable:-?}"
```
Then keep the existing `find -P … -type l -print0` loop. `! -readable` is GNU find (present here: coreutils/findutils on Arch). Verify the exact GNU findutils version under L1; this seat did not exercise it.

### P2 — LOW — fixture R14C2-09 does not exercise the poisoning it names (fixture lines 555-561)

The case injects `GIT_CONFIG_KEY_0=core.fsmonitor`, `GIT_CONFIG_VALUE_0=false`. That value is benign and matches the census's own override, so the case cannot show that an injected `core.worktree` into the store is ignored. The CensusBoundary report describes R14C2-09 as "poisoned `GIT_*` env … git gets store `GIT_COMMON_DIR`". The `GIT_COMMON_DIR` entry is present, so the poisoning is partly covered, but the config-injection branch is not. Recommend `GIT_CONFIG_KEY_0=core.worktree` with `GIT_CONFIG_VALUE_0=<store path>` and expect a positive clean row with no store access (the variable is cleared before any git call).

### P3 — LOW — residual hardlink gaps (documented, restating for L1)

Not checked for `nlink > 1`: `info/attributes`, `worktrees/*/HEAD`, `worktrees/*/commondir` beyond the first hop, every file under `refs/`, `objects/`, and alternate object dirs (only the alternates file itself is checked at each hop). Git reads several of these. Stated in CensusBoundary's residuals; no change requested this round beyond acknowledging them in the header.

### P4 — INFO / verification gap — work-tree symlinks are not guarded

Only gitdir and admin metadata are guarded. `git status` lstat()s tracked symlinks and does not follow them. In-tree `.gitignore`/`.gitattributes` that are symlinks: git ≥2.32 does not follow them for in-tree lookups `[INFERENCE]`, not verified here. Recommend L1 either accept this or add one fixture (`repo/.gitignore -> <store file>`; expect no store open in strace).

## Requested fixture coverage: R14C2-10 and R14C2-11

- R14C2-10 (`case_10`): owner `worktrees/<n>/gitdir` → `WT_BAD/.git`; admin `commondir` → store GD. Code path: `guard_worktree_registrations` → `guard_target git-common-dir` (line 560 or 569) → `exit 2`. Static: refused before any `worktree list`/`status`. Expected rc 2 is supported by the code.
- R14C2-11 (`case_11`): `ALT_REPO/.git/objects/info/alternates` → `SAFE_ALT`; `SAFE_ALT/info/alternates` → GD. Code path: `guard_alternates_file` depth 0 → `guard_target` on `SAFE_ALT` (allowed) → depth 1 → `guard_target` on GD (refused, exit 2). Expected rc 2 is supported by the code.

## Final L1 commands (not run by this seat)

1. `sha256sum tools/souji-census.sh tests/fixtures/r14-census-boundary.py` — expect the pins above.
2. `bash -n tools/souji-census.sh`
3. `shellcheck -S warning tools/souji-census.sh` (if installed; not installed by this seat)
4. `python3 -B tests/fixtures/r14-census-boundary.py` — expect total=11 (the fixture ids list has 11 entries) with R14C2-10 and R14C2-11 passing as rc 2 refusals; after P2, R14C2-09 should exercise `core.worktree` injection.
5. `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest`
6. `git status --short` — only the assigned write set.

## Verdict

Static review (final bytes 1533 lines `e2a1d502…`, fixture 726 lines `fda498d0…`): N1-N6 closed; P1 closed; P2 closed; R14C2-10/11/12 trace statically. Further static confirmations on the same bytes: ALT_REPO's objects exist only in the store (fixture copies them into GD/objects), so case_11 refusal is the sole access path and is refused at depth 1 before git reads it; a suffix-lexical refusal before lstat (line 382) refuses protected suffixes before `-L`/`readlink`; `/proc`, `/dev/fd`, `/dev/std*` compare paths return finding `special-path` at line 1004 before any open. P3/P4 remain documented residuals. No exercised verification was performed by this seat.
