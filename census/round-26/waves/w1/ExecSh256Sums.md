# ExecSh256Sums — round 26 / w1

## Status

STATUS: PASS — recipe and proof delivered at `.ufo/waves/round-26/w1/sha256sums-recipe.md`.
The recipe's generate → verify → assert chain exits 0 on a fresh copy of `census/round-25/sources/`
(`OK files=5`, `sha256sum -c` 5/5 OK) and on a copy of `census/round-26/sources/` (`OK files=7`,
7/7 OK); it is idempotent and it is falsified by a one-byte snapshot change. One decision is handed
to the L1: the already-landed r26 file verifies but is not in the recipe's LC_ALL=C order (§6.1 of
the recipe). No write, stage, commit, `jj`, `rm` or `mv` was done inside the lane; all runs used
`/var/tmp/souji-r26-ExecSh256Sums`, now removed.

## Evidence

Revision facts (read-only `git` against the lane):

```
$ git -C <lane> rev-parse HEAD
07f83e69979b1032f9de4fe876739a8dccc7242b
$ git rev-parse HEAD:census/round-25/sources/SHA256SUMS   -> dc9a5c74eab62192ca2218f7bcf2ad8b27034f36
$ git rev-parse HEAD:census/round-26/sources/SHA256SUMS   -> 894e9fad756ee23df53caab606522b1aa62a7ce7
$ git log --diff-filter=A -- census/round-26/sources/SHA256SUMS
0833de9591a7db81cdfa4efda2cdad2e75606f58  (only commit; no later commit touches the dir)
$ git status --porcelain census/round-26/sources/          -> (empty)
$ git ls-tree HEAD census/round-26/sources/SHA256SUMS     -> 100644
```

The lane tip advanced while this seat ran (`07f83e6` → `ba8b54b`); the r26 sums blob is still
`894e9fad756ee23df53caeb606522b1aa62a7ce7` at `ba8b54b`, no commit in `0833de9..ba8b54b` touches
the file, and `sha256sum -c SHA256SUMS` in the dir re-ran to exit 0 after the advance.

r25 format, measured (`census/round-25/sources/SHA256SUMS`, `cat -A`; two lines shown):

```
dabaeb5b7001e6c5efcb37f3e2544c7aee86527272d244b9a3a43508d5d61cf6  gitrepository-layout.5.txt$
da58bd50ffba03669cf89b8d171b9eb4f15d6f0f0d600d05aa6d7d0641b73554  git.1.txt$
```

Final byte `0a`, CR count `0`, on-disk mode `644`, for r24/r25/r26 alike.

Dry-run against the r25 dir (fresh copy under scratch, recipe from the delivery file):

```
$ bash <recipe> /var/tmp/.../final25
OK files=5
recipe_exit=0
$ cd /var/tmp/.../final25 && sha256sum -c SHA256SUMS
git-rev-parse.1.txt: OK
git-worktree.1.txt: OK
git.1.txt: OK
gitglossary.7.txt: OK
gitrepository-layout.5.txt: OK
verify_exit=0
$ diff <(LC_ALL=C sort <generated>) <(LC_ALL=C sort <lane r25 committed>)
LINE_SET_IDENTICAL=yes
```

Generated r25 bytes (C order; the committed r25 file holds the same five lines unsorted):

```
24b4c179610d9f4058a269e97d97cc42c84e6ed8b5932c35a8a11148f2318f31  git-rev-parse.1.txt
78e6a56be3b5ba04691236507d6d1035463eb48a11e258522a0eccf57945d8b2  git-worktree.1.txt
da58bd50ffba03669cf89b8d171b9eb4f15d6f0f0d600d05aa6d7d0641b73554  git.1.txt
8f0b851f5964f7573bfbc1d646db0c87cef60166607da2c8ec17e8ff9d7b45c0  gitglossary.7.txt
dabaeb5b7001e6c5efcb37f3e2544c7aee86527272d244b9a3a43508d5d61cf6  gitrepository-layout.5.txt
```

Other measured arms (all in scratch): recipe on an r26-dir copy → `OK files=7`, `sha256sum -c`
7/7 OK; second application → `cmp` clean (idempotent); one appended byte in a snapshot →
`sha256sum -c` exit 1; GNU coreutils 9.12 (`/usr/bin/*`) and the shell's uutils 0.8.0 builtins
produced byte-identical files (`cmp` clean).

## Findings

1. r25 format is `64 lowercase hex` + two spaces + basename + LF, basename only, final `0a`, no CR,
   mode 644 — `census/round-25/sources/SHA256SUMS` (5 lines). r24 and r26 share the shape; r23 is
   the outlier that stores repo-relative paths (`census/round-23/sources/SHA256SUMS`).
2. No prior round's file is globally LC_ALL=C sorted, so "sorted" is a new, stricter convention
   here, not an inherited property: r24 fails at line 4 (`git-count-objects.1.txt` sorts before
   `git-v2.*`), r25 fails at lines 2-4, r26 fails at line 2 (`git-fetch.1.txt` sorts after
   `git-builtin-am.c`). Locations: `census/round-{24,25,26}/sources/SHA256SUMS`.
3. The landed round-26 file is content-correct: `sha256sum -c` at HEAD `07f83e6` gives 7/7 OK, and
   its line set equals the recipe output with zero digest changes. Regenerating per the recipe
   only moves `git-fetch.1.txt` from line 1 to line 7. Location:
   `census/round-26/sources/SHA256SUMS` (blob `894e9fad…`, added in `0833de9`).
4. The verify command recorded in `corpus/lessons/round-25.md:78` does not reproduce: run from the
   lane root it resolves the bare names against the cwd and exits 1 —
   `sha256sum: WARNING: 5 listed file(s) could not be read`. The working form is
   `cd census/round-25/sources && sha256sum -c SHA256SUMS` (5/5 OK, exit 0). The r24 lesson
   (`corpus/lessons/round-24.md:180`) records the working `cd` intent; r25 silently dropped it.
5. `sha256sum -c` cannot see a snapshot that is present but unlisted: with `EXTRA-unlisted.txt` in
   the dir it still exited 0, while the file-set diff in the recipe exited 1. This is why the
   delivery file's §4 assertion has a third step (dir listing vs declared names).
6. The `mktemp` atomic write yields mode 0600 unless `chmod 0644` is applied (measured); the direct
   redirect inherits umask 022 and yields 644, matching `census/round-25/sources/SHA256SUMS` and
   `census/round-26/sources/SHA256SUMS`. The git blob mode is `100644` either way.
7. Tooling identity on this host: `type -a sha256sum` reports a uutils 0.8.0 shell builtin *before*
   `/usr/bin/sha256sum` (GNU coreutils 9.12); same for `find`, `xargs`, `sort`, `diff`, `mktemp`.
   Both implementations gave identical bytes and exit codes over this corpus, so the recipe needs
   no absolute-path pinning; pin `/usr/bin/*` only if byte stability must survive another shell.
8. The corpus is hazard-free for this recipe: every `census/*/sources` and `census/*/*/sources`
   dir is flat (0 subdirs), 0 filenames with spaces, 0 non-ASCII names, 0 symlinks — so
   `-maxdepth 1 -type f` plus `xargs` are exact, not approximate, for these dirs.

## Attack log

This item is not an attack seat; the attack-shaped observations it produced are recorded here with
locations, no predicate touched and no claim re-scored.

- A1 — unverifiable-as-written evidence: `corpus/lessons/round-25.md:78` states the snapshots verify
  with the root-relative `sha256sum -c census/round-25/sources/SHA256SUMS` → 5/5. That exact command
  exits 1 today (Finding 4). The recorded result is therefore not reproducible from the record; a
  reader who re-runs it sees a red. The file bytes themselves are fine. Suggested (not applied):
  amend the lesson line to the `cd` form, or standardise on the recipe's §3 command.
- A2 — cwd-dependent receipts: any receipt that quotes a bare-name `sha256sum -c` without its cwd
  is under-specified. The r24 lesson and the r26 wave entry quote the directory-relative form
  (`corpus/lessons/round-24.md:180`; `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md:4`
  reports `sha256sum -c SHA256SUMS` → 7 files OK), so the risk is confined to the r25 lesson line.
- A3 — format clause gameability: "matches the r25 format" would have been *satisfied by the
  already-landed unsorted r26 file*, so a format-only gate would pass a file that a
  byte-diff-against-regeneration gate would fail forever. The recipe therefore makes the order
  clause explicit and the L1 must choose: regenerate (order-only churn) or drop the sorted clause
  (recipe §6.1). Nothing in the frozen C1/C2/C3 counters reads this file.
- A4 — cross-item literal mismatch, flagged only, not adjudicated and not touched: the frozen C3
  contract requires the fixture's last stdout line `cases=12 pass=12 control=FALSE-GREEN-REJECTED`
  (`.ufo/waves/round-26/preregistration.txt:179`, `:199`; amendment 1 and amendment 2 leave C3
  alone), while the integration commit that added the fixture describes it as an "11-case fixture
  (real 11/11, stub control FALSE-GREEN-REJECTED)" (`0833de9`, commit subject). Either the fixture
  prints 11/11 — which fails C3's K2 — or the subject is stale. C3's owner seats and the L1 hold
  that call.

Not done here: no subagent or labrat was dispatched (no dispatch tool exists in this seat); no
lane build/lint/test run; no `git add/commit/push/stash`, no `jj` mutation. Scratch
`/var/tmp/souji-r26-ExecSh256Sums` removed.
