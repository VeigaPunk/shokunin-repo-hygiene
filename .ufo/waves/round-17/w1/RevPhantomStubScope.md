STATUS: DONE — Static answer: **zero** nested `.git` (or `.jj`) under any tracked directory at scan time; the only nested `.git` that can ever sit inside a tracked tree is `tests/vault/vadv54-run/p/p6repo/.git`, recreated by `tests/vault/vadv54-harness.sh` at HEAD `5fa6017`; the seven `tests/vault/vadv-49/fixture/*/.git` are ignored and have **zero tracked files beneath**, so they cannot make jj report tracked-file deletions.

# RevPhantomStubScope — nested `.git` audit, round 17 w1

Scope: static question only, pinned to HEAD `5fa6017ddcae9f6bd4412df44765f6360cb16294` and worktree reads at 2026-10-20 13:33–13:38 -0300. No `jj` (any subcommand), no harness/tool run, no git write, no file written outside this report. The harness file was being edited concurrently by another seat during this review; every claim about it names the observed sha256 and timestamp.

## 1. Question and method

Asked: (a) is `tests/vault/vadv54-run/p/p6repo/.git` the ONLY nested `.git` inside tracked trees of the lane; (b) are `tests/vault/vadv-49/fixture/*/.git` under ignored paths; (c) which nested `.git` directories can make jj report phantom deletions of **tracked** files.

Method (assignment-prescribed loop, no recursive `find`):

```text
git -C <lane> rev-parse HEAD --show-toplevel --is-inside-work-tree   -> 5fa6017… | <lane> | true
git -C <lane> ls-files -z                                            -> 1951 tracked files
  loop: for every ancestor directory of every tracked path (174 dirs),
        test os.path.lexists(<dir>/.git) and os.path.lexists(<dir>/.jj)
        (lexists covers directories, files, and dangling symlinks — jj's own
         check is a symlink_metadata presence test, so this matches it)
glob <lane>/tests/vault/vadv-49/fixture/*/.git                        -> 7 hits
git -C <lane> check-ignore -v --no-index -n --stdin <candidate paths>
git -C <lane> ls-files -- tests/vault/vadv54-run/p/p6repo            -> 2 files
git -C <lane> ls-files -- tests/vault/vadv-49 ; … -- tests/vault/vadv-49/fixture -> 18 ; 0
git -C <lane> ls-files -s -z                 -> modes: 1729x100644, 208x100755, 14x120000, 0x160000 (no gitlinks)
git -C <lane> show HEAD:tests/vault/vadv54-harness.sh ; sha256sum
git -C <lane> diff --quiet/--stat/-- <paths> ; stat -c on the fixture dirs
```

`ls-files -z` was used because two tracked paths contain literal newlines (`tests/vault/vadv54-run/r/…`); NUL splitting keeps them intact.

## 2. Result: the complete nested-`.git` set relevant to tracked files

| path | shape | tracked files beneath | ignored? (`check-ignore -v`) | can jj report tracked-file `D` rows? | present now |
|---|---|---|---|---|---|
| `tests/vault/vadv54-run/p/p6repo/.git` | empty **directory** when generated (`mkdir -p`) | **2**: `p6repo/one.txt`, `p6repo/inner/keep.txt` | **no** — rc 1, `::\t<path>` (no rule matches) | **YES** — jj skips `p6repo/` whole, so both tracked files snapshot absent | **NO** — removed at 13:33:25 today (see §3) |
| `tests/vault/vadv-49/fixture/{control,a1,a2,a4,a5,b,c}/.git` | full repos (dirs mode 0755 with `HEAD config description hooks info objects refs`) | **0** | **yes** — rc 0, `tests/vault/vadv-49/.gitignore:1:fixture/` for every one (and for their `HEAD`) | **NO** — no tracked path lies under `fixture/`; `git ls-files -- tests/vault/vadv-49/fixture` = 0 | yes (7 dirs) |

No other hits: the ancestor loop returned **0 `.git` and 0 `.jj`** across all 174 directories that contain tracked files (160 of them hold tracked files directly). The repo root's own `.git` is the repository, not a nested entry. No tracked entry has a `.git` or `.jj` path component; the index has no `160000` gitlinks (only regular files, executables, and 14 symlinks).

### Why the ignored fixture repos cannot cause phantom deletions

The jj rule (peer-sourced upstream: `jj` CHANGELOG v0.46.0 `## [0.36.0]` "Sub-repos are no longer tracked. Any directory containing `.jj` or `.git` is ignored."; implementation `RESERVED_DIR_NAMES = [".git", ".jj"]`, presence-only `symlink_metadata` check returning `Ok(None)` for the whole directory, located before the ignore matcher) is a **name-presence** skip, not a validity check. A directory is skipped whenever the entry exists, so:

- an **empty** `.git` stub is enough (this is exactly `p6repo/.git`);
- `.gitignore` cannot rescue a subtree: the ignore check runs after the reserved-name check. The vadv-49 fixtures are therefore safe **because `git ls-files` has no tracked path beneath them**, not because of `fixture/`. If a tracked file ever existed under `tests/vault/vadv-49/fixture/`, ignore rules would not prevent the deletion rows.

Mechanism observed for `p6repo` (not re-run here, per probe rule): `JjTrialSouji.md` hazard 1 — `jj status` reports `D p6repo/one.txt`, `D p6repo/inner/keep.txt` while both exist and are tracked; a directory pathspec `jj commit -- tests/vault/vadv54-run` ships the deletion (commit `c31a345`), file-exact pathspecs do not. Version gate: jj ≥ 0.36.0; the trial recorded jj 0.45.1 in the lane.

### Completeness argument

A nested `.git` can only produce `D` rows for tracked paths **below it**. The scan tested every ancestor directory of the complete tracked set (1951 paths), so it is complete for the phantom-deletion question even though it is not a full filesystem census. `.jj` was tested as well because the upstream reserved set is `.git` + `.jj`.

## 3. Current worktree state and the in-flight generator fix

The stub is **absent right now** and its parent directory pins the removal:

```text
tests/vault/vadv54-run/p/p6repo/            mtime=ctime 2026-10-20T13:33:25.395324 -0300
  inner/            (tracked)               mtime 2026-10-18T14:51:47
  one.txt           (tracked)               mtime 2026-10-18T14:51:47
  .git                                      os.path.lexists -> False (ENOENT)
git diff --quiet -- tests/vault/vadv54-run tests/vault/vadv-49 -> rc 0 (tracked bytes unchanged)
```

So the "ONLY nested `.git`" question splits by time:

- **Now:** none inside any tracked tree.
- **At HEAD / after any run of the committed harness:** `tests/vault/vadv54-harness.sh` recreated it unconditionally — HEAD sha256 `966ee19a4d33467f3ae2673c5649b4a62c0b9d15c4556501bdb9fd427ac0f3a4`, `WORK="$SCRIPT_DIR/vadv54-run"` (:46), `rm -rf -- "$WORK"` (:47), `mkdir -p "$P/p6repo/.git" "$P/p6repo/inner"` (:176). A plain deletion of the stub in the worktree is therefore **not durable**; the generator is the durable defect.

The harness was under active edit during this review; three worktree sha256s were observed within ~4 minutes:

| sha256 | shape |
|---|---|
| `966ee19a…` (= HEAD) | creates the stub permanently with the run tree |
| `6df283ad…` | one-line deletion of `.git` from the early `mkdir` — durable for jj, but P6 loses its repo-root classification |
| `b55df92d…` (mtime 13:37:48, size 28077; **snapshot reviewed**) | early `mkdir` drops `.git`; P6 block now `mkdir -- "$P/p6repo/.git"`, `trap 'rmdir -- … ' EXIT`, `run_tool`, `rmdir … || warn`, `trap - EXIT` |

Verdict on the current shape (`b55df92d…`): **right approach**. It keeps the stub only for the P6 window and removes it fail-closed (`rmdir` refuses a non-empty stub; the EXIT trap covers interruption). Two supporting facts:

- the stub is semantically required: `tools/souji-verify.sh:423` classifies a directory as a repo-root via `[ -d "$target/.git" ]`; plain deletion (`6df283ad…`) would silently change what P6 tests;
- digest ordering is immaterial: the stub is an **empty** directory, `dir_digest` (`tools/souji-verify.sh:155`) ignores `.git`, and `P6_DIG` is taken before the transient `mkdir`; an empty dir contributes no `find -type f` entries either way.

Why the phantom deletions are "phantom": `git diff --stat HEAD -- tests/vault/vadv54-run/p/p6repo` is empty and `git log --diff-filter=D master -- tests/vault/vadv54-run/p/p6repo` is empty (re-derived in `ScoutKeepOnlySouji.md`); both files exist on disk and in the index. The deletion rows live only in jj keep-ref snapshots. Re-derived read-only here (independently; ConnSiblingJj reports the same numbers): **8** `refs/jj/keep/*` refs; **6** heads are keep-only vs `master` + `origin/master` (`0254661`, `1e0d8d1`, `41ab059`, `719154d`, `dcc1512`, `dd2e322`); exactly **4** of those diff `D` for both `p6repo/one.txt` and `p6repo/inner/keep.txt` (`0254661`, `1e0d8d1`, `41ab059`, `719154d`; the other keep heads are master/origin tips or content-free). For every keep head `git rev-list --count <head> --not --all` = **0** while `--not --branches --tags --remotes` = **1** for the six keep-only heads: a receipt that roots only on branches/tags/remotes sees no unpushed work here (live false SAFE), which is C3(a)/(b) scope and not changed by this seat.

## 4. Durable-generator sweep (why this is the only one)

Tracked scripts that run `git init` / create `.git`, and where they write:

- `tests/vault/vadv-49/make-fixtures.sh` — `repogit() { git -C "$1" init -q; }` under `OUT="$HERE/fixture"` (in the lane), but `fixture/` is ignored and has 0 tracked files. Cannot cause tracked-file deletions.
- `tests/vault/case-V*/make-fixture.sh` — `git init` at `$OUT`; **defaults are `mktemp -d`** (V3 :233, V4 :100, V5 :98, V7 :135, V8 :186; V1/V2 usage "fresh mktemp -d") and re-running on a non-marker non-empty directory is refused (V1 usage :66-68, V2 :46-48). No default in-tree materialization.
- `tests/fixtures/case-F1..F6` — default `mktemp -d` (`case-F1:35`, `case-F2:36`, `case-F3:237`, `case-F4:61`, `case-F5:61`, `case-F6:235`); F4/F5 also refuse to wipe anything repo-shaped (`:66-71`).
- `tests/fixtures/case-F7/setup.sh`, `case-F8/setup.sh` — `git init` in a **caller-supplied** `$dest` (F7 :11/:22-25). A caller passing a tracked directory (e.g., the tracked `case-F7/repo-tree/`) would create a nested `.git` over tracked files; no default does this.
- `tools/*.sh` — `git init` only for temp fixtures/selftests (`cand-*` suites, `ST_*` roots); nothing creates `.git` inside the lane's tracked tree.
- `tests/fixtures/r17-census-hygiene.py` and `census/round-17/run-matrix.py` — no reference to `vadv54`/`p6repo` (the r17 fixture file did not exist at scan time), so the census matrix does not recreate the stub.

## 5. Residual risk

1. **Transient-window race (low).** While the P6 case runs (up to `timeout 30`), the stub exists. A concurrent `jj` command in the lane during that window would snapshot `p6repo/` as skipped and can put the two `D` rows into the working-copy commit; a directory-pathspec commit would ship them. The harness is manual (not referenced by any gate/runner), so likelihood is low under concurrent seats; a file-exact helper commit does not ship them.
2. **Cleanup failure is warn-only.** If `rmdir` fails (non-empty stub), the harness prints to stderr but still exits 0 by contract ("verdicts live in the JSON"). A leftover non-empty stub would be invisible to exit-code consumers. `b55df92d…`'s `rmdir` is fail-closed (refuses non-empty), which is the right direction; consider a `record` row or nonzero marker if the lane wants the condition auditable.
3. **Stale empty stub from an old-version run is self-healing:** `mkdir -- … .git` fails EEXIST, but the script uses `set -uo pipefail` (no `-e`), so it continues and the closing `rmdir` removes the empty stale stub.
4. **Interrupted harness runs** can leave the tracked run-tree files missing (`rm -rf "$WORK"` at :47 then selective recreation). Those would be *real* deletions, distinguishable from the stub hazard, and would also surface in `git status`/`git diff` rather than only in jj.
5. **Version gate:** the whole hazard requires jj ≥ 0.36.0; a plain-git lane is unaffected. Do not infer that ignore rules protect a tracked subtree — they do not.

## 6. Verdict and smallest fix

- **"Is `p6repo/.git` the only nested `.git` inside tracked trees?"** Yes, as a durable generator and as the only one that ever coexists with tracked files; at this scan it is absent (0 nested `.git`/`.jj` under all 174 tracked-directory ancestors). The vadv-49 class (7 dirs) exists but is disjoint from the tracked set.
- **"Which can make jj report phantom deletions of TRACKED files?"** Only `tests/vault/vadv54-run/p/p6repo/.git` while it is present, affecting exactly `p6repo/one.txt` and `p6repo/inner/keep.txt` (both tracked at HEAD, both present on disk). The vadv-49 fixture `.git` dirs cannot: 0 tracked files beneath; their ignore rule is not the reason.
- **Smallest fix:** land the transient-stub shape (`mkdir` immediately before the P6 `run_tool`, `rmdir` immediately after with the EXIT trap), i.e. the `b55df92d…` snapshot, not the plain deletion; keep the stub out of the tree at rest. Landing check: `stat tests/vault/vadv54-run/p/p6repo/.git` → ENOENT and `git ls-files tests/vault/vadv54-run/p/p6repo` → 2 files. If the lane prefers zero window, build the P6 source under `mktemp -d` with a `.git` child instead — at the cost of per-run absolute paths in the regenerated ledger.

## Probe and tooling record

- Read-only git on the lane: `rev-parse`, `ls-files` (plain, `-z`, `-s`, path-limited), `show HEAD:…`, `diff --quiet/--stat/--`, `log -- <path>`, `check-ignore -v --no-index -n --stdin` (the last was explicitly requested by the assignment). `sha256sum`, `stat`/`os.lstat`, `glob` on `tests/vault/vadv-49/fixture/*/.git`, and the `ls-files`-derived ancestor loop (Python, read-only).
- Never run: `jj` (any subcommand), the vadv54 harness, `souji-census.sh`, `souji-verify.sh`, `souji-vault-verify.sh`, `souji-quarantine.sh`; no git write; no recursive filesystem search.
- Installs/upgrades: none.
