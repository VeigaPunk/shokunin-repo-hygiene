# SHA256SUMS recipe — census/round-26/sources/ (souji r26, L1-owned commit)

Owner of the commit: L1. This file is a recipe + proof only; the seat that wrote it
(ExecSh256Sums) is read-only on the lane and did not write, stage or commit anything.

All facts below were measured this run at lane HEAD `07f83e69979b1032f9de4fe876739a8dccc7242b`;
the target dir was clean (`git status --porcelain census/round-26/sources/` empty) and no
commit after `0833de9591a7db81cdfa4efda2cdad2e75606f58` touched it.

## 1. Format contract (derived from the r25 bytes, corroborated by r24 and r26)

Committed `census/round-25/sources/SHA256SUMS`, `cat -A` (and the same shape in r24/r26):

```
dabaeb5b7001e6c5efcb37f3e2544c7aee86527272d244b9a3a43508d5d61cf6  gitrepository-layout.5.txt$
da58bd50ffba03669cf89b8d171b9eb4f15d6f0f0d600d05aa6d7d0641b73554  git.1.txt$
```

- `<64 lowercase hex><SP><SP><basename><LF>` — exactly two spaces (text mode, no `*` marker).
- basename only, no `census/...` path prefix (r24/r25/r26; r23 is the one outlier that uses
  full repo-relative paths).
- one line per regular file in the dir, excluding `SHA256SUMS` itself.
- final byte is `0x0a`, zero `0x0d` (measured on r24/r25/r26).
- on-disk mode 644 (`100644` in the index) for r25 and r26.

## 2. Generation (run from the lane root; the `cd` is part of the recipe)

Minimal in-place form:

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-26/sources
find . -maxdepth 1 -type f ! -name SHA256SUMS -printf '%f\n' \
  | LC_ALL=C sort \
  | xargs -r sha256sum -- > SHA256SUMS
```

Atomic form used by the test harness below (no partial file is ever named `SHA256SUMS`, and the
mode is forced back to 644 because `mktemp` creates 0600):

```bash
dir=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-26/sources
tmp=$(mktemp) && trap 'rm -f "$tmp"' EXIT
( cd "$dir" && find . -maxdepth 1 -type f ! -name SHA256SUMS -printf '%f\n' \
    | LC_ALL=C sort | xargs -r sha256sum -- > "$tmp" ) \
  && mv "$tmp" "$dir/SHA256SUMS" && chmod 0644 "$dir/SHA256SUMS"
```

Why it is written this way:
- `find ... -printf '%f\n'` gives basenames, keeps the recipe independent of the caller's cwd.
- `! -name SHA256SUMS` prevents self-hashing; the redirect form would otherwise hash its own
  truncated output (observed: a differently-named output file produced
  `e3b0c442...b855  <outfile>` — the empty-file digest).
- the sort is on **filenames**, then `sha256sum` is fed in that order, so the emitted line order
  is the LC_ALL=C filename order. Sorting the `sha256sum` *output* instead needs
  `LC_ALL=C sort -k2`; a bare `sort` sorts by the hash and is wrong (observed on the r25 copy:
  the whole-line sort left `git-rev-parse.1.txt` first and `gitrepository-layout.5.txt` last,
  i.e. hash order, not name order).

## 3. Verification (cwd MUST be the sources dir)

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-26/sources
sha256sum -c SHA256SUMS        # 7 files: OK, exit 0
```

The path-relative form recorded in `corpus/lessons/round-25.md:78`
(`sha256sum -c census/round-25/sources/SHA256SUMS`, run at the lane root) does **not** reproduce
for bare-name files: every entry resolves against the cwd and fails. Measured this run:

```
sha256sum: git.1.txt: No such file or directory (os error 2)
git.1.txt: FAILED open or read
...
sha256sum: WARNING: 5 listed file(s) could not be read
exit=1
```

`sha256sum -c` alone also does not detect a file that is present but *not listed*. The full
assertion closes that hole.

## 4. Full assertion (pasteable; exit 0 iff content + shape + order + file-set all hold)

Tested verbatim this run against fresh copies of r25 and the r26 dir: both exit 0 with
`OK files=5` / `OK files=7`, and the r25 line-set is identical to the committed r25 file.

```bash
#!/usr/bin/env bash
# usage: bash assert-sums.sh <sources-dir-absolute>
set -euo pipefail
dir=${1:?usage: assert-sums.sh <sources-dir>}
[ -d "$dir" ] || { echo "no-dir: $dir" >&2; exit 2; }
( cd "$dir" && sha256sum -c --quiet SHA256SUMS ) || { echo "content-FAILED" >&2; exit 1; }
LC_ALL=C awk '
  NF != 2                { print "bad-shape:" NR > "/dev/stderr"; bad = 1; next }
  $1 !~ /^[0-9a-f]{64}$/ { print "bad-hash:" NR > "/dev/stderr"; bad = 1 }
  { name[NR] = $2 }
  END {
    if (NR == 0) { print "empty" > "/dev/stderr"; bad = 1 }
    for (i = 2; i <= NR; i++)
      if (name[i-1] >= name[i]) { print "not-c-sorted:" i > "/dev/stderr"; bad = 1 }
    exit (bad ? 1 : 0)
  }' "$dir/SHA256SUMS" || exit 1
diff <( cd "$dir" && find . -maxdepth 1 -type f ! -name SHA256SUMS -printf '%f\n' | LC_ALL=C sort ) \
     <( awk '{ print $2 }' "$dir/SHA256SUMS" | LC_ALL=C sort ) \
  || { echo "file-set-mismatch" >&2; exit 1; }
echo "OK files=$(wc -l < "$dir/SHA256SUMS")"
```

Non-vacuity measured: on the committed r25 file it prints `not-c-sorted:2`, `not-c-sorted:3`,
`not-c-sorted:4` and exits 1; on the landed r26 file it prints `not-c-sorted:2` and exits 1
(see §6); on the regenerated copies it exits 0. A one-byte change to any snapshot makes
`sha256sum -c` exit 1.

## 5. L1 commit step (not executed by this seat)

```bash
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain census/round-26/sources/
git -C /home/vgpnk/Projects/shokunin/souji-shokunin add census/round-26/sources/SHA256SUMS
git -C /home/vgpnk/Projects/shokunin/souji-shokunin commit -m "round-26: SHA256SUMS over census/round-26/sources"
```

Then re-run §4 at the landing tip and record the exit code in the round evidence.

## 6. Known deltas and decision for the L1

1. **The landed file is content-correct but not C-sorted.** `census/round-26/sources/SHA256SUMS`
   (blob `894e9fad756ee23df53caeb606522b1aa62a7ce7`, added in `0833de9`) verifies 7/7 and equals
   the recipe output as a line *set*, but line 1 is `git-fetch.1.txt` and lines 2-7 are
   `git-builtin-*.c`, so the file fails the §4 order check at line 2. Running §2 now reorders
   the 7 lines and changes **no digest**. Same pattern in r24 (fails at line 4: the
   `git-v2.*` rows precede `git-count-objects.1.txt`) and r25 (three order flags).
   So the "LC_ALL=C sorted" clause in the wave instruction is a *new, stricter* convention, not
   a r25 property. Either regenerate (order-only churn, deterministic from then on) or drop the
   sorted clause and keep §4's shape/content/file-set checks minus the order clause. Nothing in
   the frozen C1/C2/C3 counters reads this file, so both choices are claim-safe.
2. **If regenerating, expect exactly this diff** (measured on a copy of the r26 dir):
   line 1 `78324905... git-fetch.1.txt` moves to line 7; the six `git-builtin-*.c` lines shift up
   one. `diff` of the sorted line sets is empty.
3. **Coreutils identity.** In this shell `sha256sum`, `find`, `xargs`, `sort`, `diff`, `mktemp`
   resolve first to uutils 0.8.0 **builtins** (`type -a sha256sum` reports the builtin before
   `/usr/bin/sha256sum`), while `/usr/bin` GNU coreutils is 9.12. Both were run over the r25
   corpus and produced byte-identical output (`cmp` clean) and identical exit codes, so the
   recipe is implementation-agnostic here. Pin absolute `/usr/bin/...` paths only if byte
   stability must survive a different shell.
4. **Caveats.** `-type f` silently ignores a symlinked snapshot; `xargs` splits on whitespace, so
   a filename containing a space would break the recipe. Scanned all `census/*/sources` and
   `census/*/*/sources` dirs this run: 0 files with spaces, 0 non-ASCII names, 0 subdirectories,
   0 symlinks, so neither caveat is live for this corpus.
5. **Mode.** The `mktemp` form yields 0600 unless `chmod 0644` is kept; the direct-redirect form
   inherits umask 022 and yields 644. The git blob mode is `100644` either way.

## 7. Dry-run proof (r25, this run, scratch under /var/tmp/souji-r26-ExecSh256Sums)

Fresh copy of `census/round-25/sources/*`, then §2 + §3 + §4:

```
$ bash assert/recipe block against the r25 copy
OK files=5
recipe_exit=0
$ cd <copy> && sha256sum -c SHA256SUMS
git-rev-parse.1.txt: OK
git-worktree.1.txt: OK
git.1.txt: OK
gitglossary.7.txt: OK
gitrepository-layout.5.txt: OK
verify_exit=0
$ diff <(LC_ALL=C sort <generated>) <(LC_ALL=C sort <lane r25 committed>)
LINE_SET_IDENTICAL=yes
```

Generated bytes (note this is the C order; the committed r25 file has the same five lines in a
different, unsorted order):

```
24b4c179610d9f4058a269e97d97cc42c84e6ed8b5932c35a8a11148f2318f31  git-rev-parse.1.txt
78e6a56be3b5ba04691236507d6d1035463eb48a11e258522a0eccf57945d8b2  git-worktree.1.txt
da58bd50ffba03669cf89b8d171b9eb4f15d6f0f0d600d05aa6d7d0641b73554  git.1.txt
8f0b851f5964f7573bfbc1d646db0c87cef60166607da2c8ec17e8ff9d7b45c0  gitglossary.7.txt
dabaeb5b7001e6c5efcb37f3e2544c7aee86527272d244b9a3a43508d5d61cf6  gitrepository-layout.5.txt
```

Idempotency: a second application over the same dir produced byte-identical output (`cmp` clean).
The same recipe over a copy of `census/round-26/sources/` prints `OK files=7`, exit 0, and its
`sha256sum -c` reports 7/7 OK.

## 8. Not done here

Nothing was generated, staged or committed inside the lane. Scratch
`/var/tmp/souji-r26-ExecSh256Sums` was removed after the runs. No `git add/commit/push/stash`,
no `jj`, no writes outside this file.
