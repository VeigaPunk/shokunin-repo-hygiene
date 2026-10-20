STATUS: DONE — tools/souji-quarantine.sh carries C3(a') durable roots (`--exclude='refs/jj/'`), C3(b') keep-novelty gate at the three live unpushed sites, and F1/F4 jj runbook/index-reason lines; selftest 101/0 in a clean tree, 101/1 in-lane with the single failure being a pre-existing empty `.ufo-quarantine` owned by another seat.

Seat `SoujiR17-3.QuarantineJjRoots` · 2026-10-20 · lane `/home/vgpnk/Projects/shokunin/souji-shokunin` · base `5fa6017` · file owned: `tools/souji-quarantine.sh` (only).

## 1. Diff summary (base `5fa6017` → worktree)

```
$ git diff --stat 5fa6017 -- tools/souji-quarantine.sh
 tools/souji-quarantine.sh | 186 +++++++++++++++++++++++++++++++++++++++++++---
 1 file changed, 174 insertions(+), 12 deletions(-)
```

Five independent changes:

| # | claim | site (base numbering) | change |
|---|---|---|---|
| 1 | C3(a') | `s18_evaluate_worktree_one` :1069-1073 | roots list `for-each-ref --format='%(objectname)'` → `for-each-ref --exclude='refs/jj/' --format='%(objectname)'`. Every ref except `refs/jj/*` stays a root; `refs/stash`, `refs/original`, notes and HEAD-independent refs keep their old force, and a head held only by `refs/jj/keep/*` is NOT-SAFE. `R_EVIDENCE ... durable-refs-only=yes` string untouched. |
| 2 | C3(b') | `s18_second_check` :299 | after the unchanged `--branches --not --remotes` count, `jj_keep_novel "$CREPO" "$REL"`: `0` → `class=FAIL unpushed-touching=0 jj-keep-novel`; `1` → unchanged `unpushed-touching=0`; `2` → `class=FAIL unpushed-touching=unverifiable` (fail-closed). |
| 3 | C3(b') | `try_pushed` :931 | touching revset unchanged; then `jjrel=${target#"$repo"/}` (repo-relative, absolute would silently never match `C:<rel>`) and `jj_keep_novel`: `0` → `NOTES+=("pushed=unpushed-commits-touching intro=… jj-keep-novel")`, `2` → `pushed=history-unverifiable`. |
| 4 | C3(b') | `second_check` override :1251 | touching revset unchanged; `kn != 1` → `SC_PASS=0; SC_EV="$SC_EV head-history=FAIL"`. **No new SC_EV token** (that stream is a fixed parsed token set; the token surfaces from stage 1 / the S18 prong). |
| 5 | F1/F4 | `s18_flow_one` dry-run/stage-2/stage-5 | `q_jj_colocated` (`.jj` beside `.git`); in a jj repo the dry-run prints a worktree `mv` (no `git mv`), no `git rm --cached`, and the final CMD `jj-lane.sh commit <repo> --as souji -m … -- <rel> <qpath>` naming BOTH paths; the real run emits the same recipe right after `QSTAGE stage2`; on `git rm --cached` failure the reason says `jj-owns-index` (`… index-cleanup-skipped <qpath> jj-owns-index`). Plain repos emit the old `git mv` / `rm --cached` runbook unchanged. |

Helper (byte-identical to the body `VerifyJjRoots` landed in `souji-verify.sh` and `VaultJjRoots` landed in `souji-vault-verify.sh`):

```bash
jj_keep_novel() { # $1 repo, $2 path relative to the repo root
  local repo=$1 rel=$2 c obj known
  [ -n "$(git -C "$repo" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>/dev/null)" ] || return 1
  if ! known=$(git -C "$repo" rev-list --objects --remotes -- "$rel" 2>/dev/null | cut -d' ' -f1); then return 2; fi
  if ! c=$(git -C "$repo" rev-list "--glob=refs/jj/keep/*" --not --branches --tags --remotes -- "$rel" 2>/dev/null); then return 2; fi
  while IFS= read -r c; do
    [ -n "$c" ] || continue
    obj=$(git -C "$repo" rev-parse -q --verify "$c:$rel" 2>/dev/null) || continue
    printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0
  done <<< "$c"
  return 1
}
```

Header r17 paragraph rewritten to exactly this (“every ref except `refs/jj/*`”, glob quoted and before `--not`, blob novelty, `jj-keep-novel`, `jj 0.45.1 git_backend.rs`); the false `refs/jj/bookmarks` claim is gone (`grep -n refs/jj/bookmarks` → no match).

## 2. Behavioural evidence

### 2.1 Plain repos are unchanged (byte-identical stdout)

Base tool extracted read-only with `git show 5fa6017:tools/souji-quarantine.sh`; two identical fixtures (`refs/jj` absent), engine pinned to a base copy of `souji-verify.sh` (`sha256 9adb17645a5f452a…`), real run over `keep/keep.txt keep/obs.txt` plus a dry run:

```
$ diff -u out.base out.new && echo IDENTICAL-PLAIN-OUTPUT
IDENTICAL-PLAIN-OUTPUT
$ diff -u d.base d.new && echo IDENTICAL-DRYRUN
IDENTICAL-DRYRUN
```

### 2.2 Keep-novelty matrix (git-only `refs/jj/keep/<sha>` emulation, base engine so stage 1 stays SAFE)

```
plain      rc=0  DELETED pushed
identical  rc=0  DELETED pushed        (keep-only commit restores already-pushed blob)
deletion   rc=0  DELETED pushed        (keep-only deletion; no blob at <rel>)
novel      rc=3  ABORTED pushed  jj-keep-novel
```
`novel` row, full second-check line:
`FAIL pin=ok mtime=ok intro=… default-ref=ok class=FAIL unpushed-touching=0 jj-keep-novel intro-blob=ok prong1=NOT-SAFE(none) prong1-tolerated class-not-path-local head-history=FAIL`

Roots at tool level (clean sjc, in the selftest): same head only in `refs/stash` → `verdict=SAFE receipt=metadata-prune`; same head only in `refs/jj/keep` → `verdict=NOT-SAFE receipt=none`.

### 2.3 F1/F4 runbook and index reason

```
$ ... --dry-run <plain repo> keep/keep.txt     # unchanged
CMD  timeout … git -C <repo> mv -- keep/keep.txt <repo>/.ufo-quarantine/2026-10-20/keep/keep.txt
CMD  git -C <repo> rm --cached --quiet -- …/keep/keep.txt   # after rm

$ ... --dry-run <repo with .jj> keep/keep.txt
CMD  timeout … mv --no-copy -T -- <repo>/keep/keep.txt <repo>/.ufo-quarantine/2026-10-20/keep/keep.txt
CMD  jj-lane.sh commit <repo> --as souji -m 'souji-quarantine: stage keep/keep.txt into quarantine' \
       -- keep/keep.txt .ufo-quarantine/2026-10-20/keep/keep.txt   # jj owns the index; commit the move through the lane helper naming BOTH the source and the quarantine path -- never a git index/commit recipe
$ ... --dry-run … | grep -E 'git (add|commit)( |$)'      → none
```
Stage-5 reason, F4 emulated by dropping the index entry after stage 2 (`SOUJI_Q_TEST_HOOK`, selftest-only):
```
jj  : …/keep/keep.txt jj-owns-index
plain: …/keep/keep.txt
```
Stage 2/5 mechanics are untouched in both repo kinds (`git mv` still stages the rename under jj — jj treats the index as advisory, which is precisely F4; the recipe is the operator path).

## 3. Static checks

```
$ bash -n tools/souji-quarantine.sh           → SYNTAX-OK
$ shellcheck -S warning tools/souji-quarantine.sh → rc=0 (no findings)
$ git --version                                → 2.56.0 (`--exclude=`, `--count=1` supported; `for-each-ref --exclude='refs/jj/'` exercised)
```

## 4. Selftest

```
$ TMPDIR=/var/tmp/qj-tmp bash <pristine copy>/tools/souji-quarantine.sh --selftest
selftest: 101 checks, 0 failed          (ROUND9 28/0)

$ TMPDIR=/var/tmp/qj-tmp bash tools/souji-quarantine.sh --selftest   (live lane)
selftest: 101 checks, 1 failed
FAIL H3 no live .ufo-quarantine (absent before+after)
```
New checks (8): `JJ0` no `refs/jj/keep/*`; `JJ1` no keep refs → no novelty; `JJ2` keep-only deletion → no novelty; `JJ3` identical-content predecessor → no novelty; `JJ4` novel keep-only blob → novelty; `JJ5` flow refuses (`NOT-AUTHORIZED|ABORTED`, never `DELETED`) and carries `jj-keep-novel`; `JJ6` head only in `refs/stash` → SAFE(metadata-prune); `JJ7` head only in `refs/jj/keep` → NOT-SAFE. Fixture additions: a pushed revision `p2` moving `keep/novel.txt` to v2 (so the pushed blob set is `{v1,v2}`) and `st_keep_commit` (temp-index tree builder; no worktree/index pollution).

H3 is environmental, not a regression: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo-quarantine/2026-10-20/tests/vault` exists as empty directories with `mtime 2026-10-20 13:33`, git-ignored, created before this seat's first selftest; the check reports `before=yes`. The identical tree with no `.ufo-quarantine` scores 101/0. Deleting it is outside this seat's scope.

## 5. Risks / limits (disclosed, not silently absorbed)

1. Keep-ref receipts are now *novelty*-based, so a keep-only metaedit/rebase predecessor that **changes** content relative to every pushed revision still refuses — correct, but it means a rebase that reflows a file (e.g. LOG.md) manufactured by jj can block a receipt until pushed. Conservative by design.
2. `git mv` is still executed at stage 2 under colocation; the index entry it writes is advisory (F4) and the tool never commits. If the operator commits with plain git instead of the emitted helper recipe, the F1 half-commit hazard returns — the recipe line is guidance, not enforcement.
3. The recipe pins `--as souji`; a different lane identity must override it.
4. `jj_keep_novel` is called per target after the untouched touching query; for very long `rel` histories `rev-list --objects --remotes -- <rel>` is the added cost (one call), gated off entirely when `refs/jj/keep/` is empty.
5. The S18 copy of `try_pushed`/`s18_evaluate_worktree_one` inside quarantine is only reachable through `evaluate_path`, which no live flow calls; it was still updated per contract, and its unit checks (`JJ6/JJ7`) exercise it directly.

Tooling: nothing installed or upgraded (no pacman/uv/npx); no pacman transaction attempted.

## 6. Commands run (exact, abbreviated)

`bash -n`, `shellcheck -S warning`, `git diff 5fa6017`, `git show 5fa6017:tools/souji-verify.sh`, `sha256sum`, `git for-each-ref --exclude=… --count=1`, the tool `--selftest` (lane + pristine copy), and the tool `--dry-run`/real runs on synthetic repos under `/var/tmp/souji-r17-QuarantineJjRoots/`. No write to any fleet repo, no `jj` invocation, no lane mutation beyond this file and this report.
