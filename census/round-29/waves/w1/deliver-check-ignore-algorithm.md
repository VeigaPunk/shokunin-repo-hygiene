# Wave-evidence capture: deciding which destination paths git will ignore

Seat SwarmExecutor05 — r29 w1, lane fleet-repo/workspace hygiene (掃除). Read-only probe;
no lane index, no lane write. All probe commands ran in a throwaway clone
`/var/tmp/souji-r29-C2CheckIgnoreProbe/c` (`git clone -q --no-local
/home/vgpnk/Projects/shokunin/souji-shokunin`), toplevel confirmed by
`git -C /var/tmp/souji-r29-C2CheckIgnoreProbe/c rev-parse --show-toplevel`. Probe input =
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26` copied verbatim to
`census/round-26/waves/` inside the clone. The census tree is byte-identical at lane base
`691dd29211c53d0ef94fa072394cb9c8a69fe92e` and prereg commit
`b8cb4b31ce80e2e3314b88e85d40ea9873180804` (`git diff --stat 691dd29 b8cb4b3 -- census/round-26/`
printed nothing), so counters measured here apply to both revisions.

Instrument: git 2.56.0.

## 1. Verdict — recommended exact sequence

`git check-ignore` is the only one of the three candidates that decides per path by rule, so it
is the only one that can enumerate ignored destination paths inside ignored directories and
nested repositories. `git ls-files --others --ignored --exclude-standard` and
`git status --porcelain --ignored` both stop at an ignored directory / nested repository and
report the directory, not its contents; they are unsuitable as the deciding instrument.

Run from anywhere; `-C "$lane"` fixes the work tree. Nothing below writes the index.

```bash
lane=/home/vgpnk/Projects/shokunin/souji-shokunin
round=26
dst=$lane/census/round-$round/waves            # receipt being built, source already copied
tmp=$(mktemp -d /var/tmp/souji-capture.XXXXXX)

# Step 1 — enumerate the DESTINATION entries exactly as git will see them: regular files and
# symlinks only (not directories, never descending through a symlink), NUL-separated.
find "$dst" -mindepth 1 \( -type f -o -type l \) -print0 | LC_ALL=C sort -z > "$tmp/entries.z"

# Step 2 — one verdict per input path, index-independent and newline-safe.
git -C "$lane" check-ignore --no-index -n -v -z --stdin < "$tmp/entries.z" > "$tmp/verdicts.z"
```

`-n -v -z` emits **exactly one 4-field record per input path**:
`<source-file>\0<line>\0<pattern>\0<path>\0` (measured: 1398 inputs -> 1398 records). For a
non-ignored path the first three fields are empty. The decision is:

```
ignored  <=>  <pattern> is non-empty AND does not start with '!'
```

Negation matters: a path re-included by `!pattern` is printed by `-v` with that negative pattern
and exits 0 (measured on the two `.../.scratch/.gitignore` fixtures), so `-v` output must be
filtered on `!`. It is also why the verdict must not be taken from an exit status.

Steps 3-6 are the sequence the delivered capture tool implements
(`.ufo/waves/round-29/w1/deliver-souji-wave-evidence-capture.sh`, measured sha256
`3db37453e0fdbd253e9f8abaff970c88995eeaeb18bcbd2df42ca9a712397374`):

3. Neutralise copied rules inside `$dst` **before** the ignore decision: rename every file or
   symlink named `.gitignore` / `.gitattributes` (any depth) to `<same name>.captured`, refuse a
   stored-name collision, record the mapping in `renames.tsv`. The decision at step 2 is then
   taken on the **stored** path, i.e. the exact path that will be committed.
4. Re-run step 2. Every remaining `ignored` regular file is a path the commit would silently
   lose: do not put it in `manifest.sha256` and do not commit it. Record it in `excluded.tsv`
   (`path<TAB>sha256<TAB>reason`, reason `ignored`; the matched `<source>:<line>:<pattern>` may be
   carried in the reason for audit) so the drop is accounted and not silent.
5. Symlinks: enumerate them as entries (`find -type l`), record `path<TAB>target` in
   `symlinks.tsv` (target = `readlink` string exactly), never dereference them. They carry no
   manifest record.
6. Build `manifest.sha256` over the receipt's regular files except `manifest.sha256` itself, with
   `-z` sorting, GNU backslash-escaping record names containing newline/backslash. Verify by
   recomputing over the receipt. Commit; the independent judge is
   `python3 -B census/round-29/c2-counter.py --root <lane> --rev <landed-rev>`.

Per-path equivalent (what the delivered tool calls, one process per entry; measured identical
set to the bulk method on 1398 entries):

```bash
git -C "$lane" -c core.fsmonitor=false check-ignore --no-index -q -- "$destrel"
# rc 0 => ignored, rc 1 => not ignored, rc 128 => fatal (see pitfalls)
```

`-q` takes a single pathname only; it is not usable for attribution over `--stdin`.

## 2. Probe comparison against the 152 absent r26 records (answer 1)

Ground truth: the frozen counter at base reproduces `failed=152` from committed bytes
(`python3 -B census/round-29/c2-counter.py --root . --rev 691dd29...` ->
`r26 records=1382 failed=152 uncovered=14 floor_violation=0`); all 152 are **absent**, none is a
sha mismatch (recomputed independently in the clone: `absent=152 wrongsha=0`). The 1382 records
are the 1381 source regular files plus the generated `summary.tsv`.

With the source copy placed at `census/round-26/waves/`:

| probe | entries found | of the 152 | why it misses |
|---|---|---|---|
| `git check-ignore --no-index [-n] -v -z --stdin` | 155 (157 raw `-v`) | **152/152** | nothing — per-path rule match |
| `git ls-files --others --ignored --exclude-standard -z` | 21 | 14/152 | lists the 7 nested `.git` repos as one directory each; 126 `.git/*` files invisible |
| same + `--directory` | 12 | 6/152 | also collapses every ignored directory |
| `git status --porcelain --ignored -z` | 12 | 6/152 | `!!` directory entries only |
| `git status --porcelain --ignored -z -uall` | 21 | 14/152 | same nested-repo stop as ls-files |
| `git status --porcelain --ignored=matching -z` (+` -uall`) | 12 (12) | 6/152 | matching mode does not descend ignored dirs here |

Raw `-v` output was 157 paths = 152 records + 2 re-included (`!.gitignore`) + 3 ignored symlinks.
After dropping `!` patterns the set is 155 = the 152 records + these 3 symlinks, which are
ignored by `fixture/` and vanished from the r26 receipt without any counter noticing (they are
not manifest records and are not committed):

```
assimilation/validate/tests/vault/vadv-49/fixture/a1/source/link.txt
assimilation/validate/tests/vault/vadv-49/fixture/a2/source/link.txt
assimilation/validate/tests/vault/vadv-49/fixture/a4/vault/copy.txt
```

### The 152 by ignore source (source is repo-relative; every source file is inside the receipt)

| ignore rule `<source>:<line>:<pattern>` | records |
|---|---|
| `assimilation/validate/tests/vault/vadv-49/.gitignore:1:fixture/` | 138 |
| `.gitignore:3:__pycache__/` (lane root) | 4 |
| `assimilation/validate/tests/vault/case-V6/.gitignore:6:/ledger*.tsv` | 4 |
| `assimilation/validate/tests/vault/vadv-49/.gitignore:2:shims/` | 2 |
| `assimilation/validate/tests/fixtures/case-F7/repo-tree/.scratch/.gitignore:1:*` | 1 |
| `assimilation/validate/tests/fixtures/case-F8/repo-tree/.scratch/.gitignore:1:*` | 1 |
| `assimilation/validate/tests/vault/case-V6/.gitignore:4:/src/` | 1 |
| `assimilation/validate/tests/vault/case-V6/.gitignore:5:/vault/` | 1 |
| **total** | **152** |

This reproduces the r28 closure attribution exactly (138 `fixture/`, 4 `__pycache__/`,
4 `/ledger*.tsv`, 2 `shims/`, 2 `.scratch` `*`, 2 `/src/` + `/vault/`). Of the 138 under
`fixture/`, 126 are inside the 7 nested `.git` directories and 12 are ordinary files. The fifth
copied rule file, `assimilation/validate/tests/fixtures/.gitignore` (patterns
`tests/fixtures/*/repo/`), matched **0** entries: its patterns are anchored under its own
directory, so they would need a literal `tests/fixtures` subdirectory beneath it.

Full per-path list: see section 7 appendix; the same per-row data (path, manifest sha256,
ignore rule, source sha256) is in `.ufo/waves/round-29/w1/deliver-c2-152-classification.tsv`.

## 3. Neutralisation (answer 2)

Renaming the 5 copied `.gitignore` files to `.gitignore.captured` (in the destination, so the
commit sees no live rule) removes the nested ignores completely:

- pre: 155 entries true-ignored (152 records + 3 symlinks), produced by 8 rules in 5 `.gitignore`
  files (the lane root plus four of the five copied files; the fifth, `fixtures/.gitignore`,
  contributes 0).
- post: **4 entries ignored, all 4 by the lane root rule only** —
  `.gitignore:3:__pycache__/` — i.e. **4 of the 1382 r26 records remain ignored after
  neutralisation**, and 148 are unblocked.
- The renamed files themselves are not ignored and commit as `.gitignore.captured`
  (5 records under their new names). No stored-name collision existed
  (`find <src> -name .gitignore.captured` = 0).

The 4 survivors are precisely:

```
.../assimilation/validate/tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc
.../assimilation/validate/tools/__pycache__/souji-axis-check.cpython-314.pyc
.../assimilation/validate/tools/__pycache__/souji-gate-check.cpython-314.pyc
.../assimilation/validate/tools/__pycache__/souji-landing-gate.cpython-314.pyc
```

They are ignored by the **lane root** `.gitignore` (`/home/vgpnk/Projects/shokunin/souji-shokunin/.gitignore:3`:
`__pycache__/`, a bare name pattern that matches at any depth). The root's other two lines never
match inside `census/round-N/waves/`: `.ufo/waves/` and `census/operator-sweep-*/` contain a
slash and are therefore anchored at the repository root. That is why they cannot be neutralised
by renaming copied rule files — they are the lane's own policy, outside the receipt — and must be
accounted as exclusions (step 4), exactly matching the prereg's "root-ignored name accounted as
excluded, never silently dropped".

## 4. `git check-ignore` behaviour matrix (answer 3)

Measured in a controlled repo (`/var/tmp/souji-r29-C2CheckIgnoreProbe/probe-repo`) plus the r26
copy; every row below is an executed observation.

**Non-existent paths.** Pure lexical matching; the path does not have to exist.

| input | output | rc |
|---|---|---|
| `rootign/ghost.txt` (root rule `rootign/`) | `.gitignore:1:rootign/` | 0 |
| `sub/inner/ghost.txt` (nested rule `sub/.gitignore:1:inner/`) | `sub/.gitignore:1:inner/` | 0 |
| `sub/none.txt` (no rule) | (nothing) | 1 |
| `sub/keep.log` (nested `!keep.log`) with `-v` | `sub/.gitignore:2:!keep.log` | 0 — over-report |
| same without `-v` / with `-q` | (nothing) | 1 — correct |
| path outside the repo (`/etc/passwd`) | `fatal: ... is outside repository` | 128 |
| empty pathname on `--stdin` | `fatal: empty string is not a valid pathspec` | 128 |

Consequence for a capture tool: the ignore decision can be taken **before** copying (the
delivered tool runs it with the destination cleared), and it must never be fed paths outside the
work tree or empty records.

**Symlinks.** Matched lexically by their own path; never dereferenced; `find -type l` entries are
sufficient input.

| case | verdict |
|---|---|
| symlink named `abs-link.log` -> `/etc/hostname` (rule `*.log`) | ignored (`-v` shows `.gitignore:2:*.log`), rc 0 |
| dangling symlink named `dangling.log` | ignored, rc 0 |
| symlink named `to-ignored` -> `rootign/` (name matches no rule) | **not** ignored, rc 1 — target's directory rule is not inherited |
| dir-only rule `inner/` vs symlink named `inner` | **not** ignored, rc 1 — dir-only patterns need a real directory |
| dir-only rule `inner/` vs real directory `sub/inner` | ignored, rc 0 |
| query through a symlink: `sub/to-ignored/target.txt` | `fatal: pathspec ... is beyond a symbolic link`, rc 128 |
| same path inside a `--stdin` batch | whole batch aborts, rc 128, **no output at all** for valid entries in the batch |

Consequence: enumerate symlinks as entries; never feed a path that has a symlink as an ancestor
component, or one bad path destroys the entire batch's verdicts.

**Paths containing newlines.** `-z` is mandatory on both directions.

| form | observed |
|---|---|
| argv path `rootign/a\nb.txt`, no `-z` | output path is C-quoted: `"rootign/a\nb.txt"` |
| `-z --stdin` with NUL input | 4 NUL fields, path raw with the embedded newline |
| `--stdin` **without** `-z` | input is split at the newline: reports `rootign/a`, silently drops the `b.txt` fragment, rc 0 |
| `git ls-files -o -i` / `status` without `-z` | newline names C-quoted (`"sub/keep\n.log"`) |
| same with `-z` | raw, NUL-delimited |

The r26 data contains two such record names
(`assimilation/validate/tests/vault/vadv54-run/r/nl/first\nsecond.md`,
`assimilation/validate/tests/vault/vadv54-run/r/scratch/.scratch/old\nname.log`); a line-oriented
manifest/pipeline mis-splits them (this probe hit exactly that: 1382 NUL records became 1384
text lines).

## 5. Pitfalls (each measured)

1. `-v` is not a verdict: re-included paths are printed with their `!pattern` and rc 0. Filter
   `!`; never use the exit status of a `-v` run.
2. `-q` is single-path only (`--quiet is only valid with a single pathname`, rc 128 on two args)
   and is mutually exclusive with `-v` (`cannot have both --quiet and --verbose`, rc 128). The
   literal combination `check-ignore --no-index -v -q` is a usage error, not a mode.
3. `-q --stdin` returns only "was anything ignored" (rc 0 if >=1 ignored, 1 if none); it gives no
   per-path attribution.
4. `--no-index` deliberately bypasses the tracked-file exemption. Measured: a tracked regular
   file and a tracked symlink both answer "ignored" (rc 0) with `--no-index` and "not ignored"
   (rc 1) without it. The capture must use `--no-index`: it clears and rebuilds the receipt while
   the index still holds the previous receipt's paths, and a fresh receipt has nothing tracked.
   The over-report direction is safe because the answer is accounted in `excluded.tsv`, never
   silently lost.
5. `-v -z` output is **4** NUL fields per record, not 2; `tr '\0' '\n'` misaligns pattern/path.
   Prefer `-n -v -z`, which yields one record per input, non-matching paths included.
6. Paths are echoed exactly as supplied: absolute and `./`-prefixed inputs come back in the same
   form (`/var/tmp/.../ledger.tsv`, `./census/...`). Feed repository-relative paths without `./`
   so the output path compares byte-equal to the enumerated path.
7. A directory entry is not a valid input: enumerate `-type f` and `-type l` only. Passing a
   directory is unnecessary and a symlinked ancestor is fatal (see section 4).
8. A blank input record aborts the batch (`empty string is not a valid pathspec`, rc 128) —
   filter empty records produced by hand-built lists.

## 6. Measured counts and end-to-end result

- Before: 152/1382 r26 records ignored (11.0%), 155/1398 entries.
- After neutralisation: **4/1382 r26 records ignored (0.29%)**, 4/1398 entries, all by the lane
  root `.gitignore:3:__pycache__/`. 148 records unblocked; 17/17 symlinks committable.
- Delivered tool run in the throwaway clone (never the lane) against the real r26 source:
  `records=1255 renames=5 excluded=11 symlinks=17`, exit 0, tool's own verify passed. The 11
  `excluded.tsv` rows are 4 `ignored` (the `__pycache__` pyc, each with its source sha256) and 7
  `git-dir` (one digest per nested `.git` directory, covering its 126 files). Arithmetic:
  1381 source regular files - 130 excluded files + 4 accounting TSVs (`summary`, `renames`,
  `excluded`, `symlinks`) = 1255 manifest records.
- After committing that receipt in the clone
  (`f74a89e1459a415d18b5e36461ffbcc7a6265b69`), the frozen counter over committed bytes:

```
r26 records=1255 failed=0 uncovered=0 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=f74a89e1459a415d18b5e36461ffbcc7a6265b69
```

  rc 0. The tool's `--verify --rev f74a89e...` agrees:
  `verify-rev rev=f74a89e... records=1255 failed=0 uncovered=0`.

Scratch (`/var/tmp/souji-r29-C2CheckIgnoreProbe/`) was removed after these measurements; all git
writes above happened only inside it.

## 7. Appendix — all 152 records, by ignore source

Names are receipt-relative (under `census/round-26/waves/`).

### `.gitignore:3:__pycache__/` — 4
```
assimilation/validate/tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc
assimilation/validate/tools/__pycache__/souji-axis-check.cpython-314.pyc
assimilation/validate/tools/__pycache__/souji-gate-check.cpython-314.pyc
assimilation/validate/tools/__pycache__/souji-landing-gate.cpython-314.pyc
```

### `assimilation/validate/tests/fixtures/case-F7/repo-tree/.scratch/.gitignore:1:*` — 1
```
assimilation/validate/tests/fixtures/case-F7/repo-tree/.scratch/stale-probe-f7.tmp
```

### `assimilation/validate/tests/fixtures/case-F8/repo-tree/.scratch/.gitignore:1:*` — 1
```
assimilation/validate/tests/fixtures/case-F8/repo-tree/.scratch/stale-probe-f8.tmp
```

### `assimilation/validate/tests/vault/case-V6/.gitignore:4:/src/` — 1
```
assimilation/validate/tests/vault/case-V6/src/payload.md
```

### `assimilation/validate/tests/vault/case-V6/.gitignore:5:/vault/` — 1
```
assimilation/validate/tests/vault/case-V6/vault/payload.md
```

### `assimilation/validate/tests/vault/case-V6/.gitignore:6:/ledger*.tsv` — 4
```
assimilation/validate/tests/vault/case-V6/ledger-crlf-truncated.tsv
assimilation/validate/tests/vault/case-V6/ledger-crlf.tsv
assimilation/validate/tests/vault/case-V6/ledger-lf-control.tsv
assimilation/validate/tests/vault/case-V6/ledger.tsv
```

### `assimilation/validate/tests/vault/vadv-49/.gitignore:2:shims/` — 2
```
assimilation/validate/tests/vault/vadv-49/shims/electron43
assimilation/validate/tests/vault/vadv-49/shims/obsidian
```

### `assimilation/validate/tests/vault/vadv-49/.gitignore:1:fixture/` — 138
```
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/HEAD
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/config
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/description
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/applypatch-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/fsmonitor-watchman.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/post-update.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/pre-applypatch.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/pre-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/pre-merge-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/pre-push.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/pre-rebase.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/pre-receive.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/prepare-commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/push-to-checkout.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/sendemail-validate.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/hooks/update.sample
assimilation/validate/tests/vault/vadv-49/fixture/a1/.git/info/exclude
assimilation/validate/tests/vault/vadv-49/fixture/a1/vault/alpha.txt
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/HEAD
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/config
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/description
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/applypatch-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/fsmonitor-watchman.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/post-update.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/pre-applypatch.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/pre-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/pre-merge-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/pre-push.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/pre-rebase.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/pre-receive.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/prepare-commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/push-to-checkout.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/sendemail-validate.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/hooks/update.sample
assimilation/validate/tests/vault/vadv-49/fixture/a2/.git/info/exclude
assimilation/validate/tests/vault/vadv-49/fixture/a2/elsewhere/decoy.txt
assimilation/validate/tests/vault/vadv-49/fixture/a2/vault/alpha.txt
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/HEAD
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/config
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/description
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/applypatch-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/fsmonitor-watchman.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/post-update.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/pre-applypatch.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/pre-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/pre-merge-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/pre-push.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/pre-rebase.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/pre-receive.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/prepare-commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/push-to-checkout.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/sendemail-validate.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/hooks/update.sample
assimilation/validate/tests/vault/vadv-49/fixture/a4/.git/info/exclude
assimilation/validate/tests/vault/vadv-49/fixture/a4/source/alpha.txt
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/HEAD
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/config
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/description
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/applypatch-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/fsmonitor-watchman.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/post-update.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/pre-applypatch.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/pre-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/pre-merge-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/pre-push.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/pre-rebase.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/pre-receive.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/prepare-commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/push-to-checkout.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/sendemail-validate.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/hooks/update.sample
assimilation/validate/tests/vault/vadv-49/fixture/a5/.git/info/exclude
assimilation/validate/tests/vault/vadv-49/fixture/a5/source/self.txt
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/HEAD
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/config
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/description
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/applypatch-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/fsmonitor-watchman.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/post-update.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/pre-applypatch.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/pre-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/pre-merge-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/pre-push.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/pre-rebase.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/pre-receive.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/prepare-commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/push-to-checkout.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/sendemail-validate.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/hooks/update.sample
assimilation/validate/tests/vault/vadv-49/fixture/b/.git/info/exclude
assimilation/validate/tests/vault/vadv-49/fixture/b/source/alpha.txt
assimilation/validate/tests/vault/vadv-49/fixture/b/vault/alpha.txt
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/HEAD
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/config
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/description
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/applypatch-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/fsmonitor-watchman.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/post-update.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/pre-applypatch.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/pre-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/pre-merge-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/pre-push.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/pre-rebase.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/pre-receive.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/prepare-commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/push-to-checkout.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/sendemail-validate.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/hooks/update.sample
assimilation/validate/tests/vault/vadv-49/fixture/c/.git/info/exclude
assimilation/validate/tests/vault/vadv-49/fixture/c/source/#weird.txt
assimilation/validate/tests/vault/vadv-49/fixture/c/source/alpha.txt
assimilation/validate/tests/vault/vadv-49/fixture/c/vault/alpha.txt
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/HEAD
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/config
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/description
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/applypatch-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/fsmonitor-watchman.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/post-update.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/pre-applypatch.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/pre-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/pre-merge-commit.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/pre-push.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/pre-rebase.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/pre-receive.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/prepare-commit-msg.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/push-to-checkout.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/sendemail-validate.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/hooks/update.sample
assimilation/validate/tests/vault/vadv-49/fixture/control/.git/info/exclude
assimilation/validate/tests/vault/vadv-49/fixture/control/source/alpha.txt
assimilation/validate/tests/vault/vadv-49/fixture/control/vault/alpha.txt
```
