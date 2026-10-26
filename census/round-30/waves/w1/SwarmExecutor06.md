## Status

STATUS: PASS — the C3 measurement is built and delivered: `tests/fixtures/r30-jj-keep-expiry.sh` (delivered as `deliver-r30-jj-keep-expiry.sh`) was run twice with byte-identical stdout, exercises the assigned six steps plus two replacement controls, and answers the F1 question for jj 0.45.1: the abandoned commit's own `refs/jj/keep/*` ref is deleted by `jj util gc --expire=now`, the commit object is not deleted anywhere in the sequence, and a future `--expire` cannot be expressed in 0.45.1.

## Evidence

Lane revision: read-only seat, no lane bytes written outside `.ufo/waves/round-30/w1/` (gitignored, `.gitignore:1`). Base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; lane HEAD observed `df6afe817d096e4ad71ba2b9cc21a83f126eb658` at run time. The measurement does not read lane bytes; it runs the workspace binaries.

Toolchain: `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`, `git version 2.56.0`. Nothing installed or upgraded this seat; no pacman transaction was attempted.

Run, twice (rc 0 both):

```
export TMPDIR=/fast/scratch/hyaku/souji-r30/C3JjFixture
bash r30-jj-keep-expiry.sh > run1.txt
bash r30-jj-keep-expiry.sh > run2.txt
cmp run1.txt run2.txt      # BYTE-IDENTICAL
```

Delivered record (`deliver-jj-keep-expiry-run.txt`, 10 lines; line numbers are cited below):

```
1  jj-version: jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5
2  git-version: git version 2.56.0
3  RESULT step=1-commit-A-B keep_refs=7 object_present=yes note=target_keep=yes commits=2
4  RESULT step=2-abandon-B keep_refs=8 object_present=yes note=target_keep=yes abandoned=B
5  RESULT step=3-git-gc-prune-now keep_refs=8 object_present=yes note=target_keep=yes cmd=git-gc-prune-now
6  RESULT step=4-util-gc-expire-now keep_refs=6 object_present=yes note=target_keep=no cmd=jj-util-gc-expire-now
7  RESULT step=5-op-abandon-util-gc-expire-now keep_refs=2 object_present=yes note=target_keep=no op_range=..@- ops_naming_target=1
8  RESULT step=6-future-expire-control keep_refs=8 object_present=yes note=target_keep=yes expire=tomorrow rc=1 rejected
9  RESULT step=7-default-expire-control keep_refs=8 object_present=yes note=target_keep=yes cmd=jj-util-gc-default-2weeks
10 RESULT step=8-control-expire-now keep_refs=6 object_present=yes note=target_keep=no cmd=jj-util-gc-expire-now
```

Refusal guards, each `rc=2` and no directory created (the TMPDIR check runs before `mktemp`):

```
( unset TMPDIR; bash r30-jj-keep-expiry.sh )
  ERROR: TMPDIR is unset or empty; refusing to run                                        rc=2
TMPDIR=/home/vgpnk/Projects/shokunin/souji-shokunin bash r30-jj-keep-expiry.sh
  ERROR: ... resolves inside the souji lane (/home/vgpnk/Projects/shokunin/souji-shokunin); refusing to run   rc=2
TMPDIR=/home/vgpnk/Projects/shokunin bash r30-jj-keep-expiry.sh
  ERROR: ... resolves inside /home/vgpnk/Projects/shokunin; refusing to run               rc=2
TMPDIR=/nonexistent/x bash r30-jj-keep-expiry.sh
  ERROR: TMPDIR=/nonexistent/x is not a directory; refusing to run                        rc=2
```

Mechanism probe (receipt `receipt-SwarmExecutor06-keepref-mechanism.txt`, script plus output of one run): after steps 1-5, `Number of heads: 2` in the index, exactly one visible head, the pre-abandon working-copy commit `hidden=true`, and the one remaining keep ref that descends from the abandoned commit is that working-copy commit's (`B_ancestor=yes`). Scratch `/fast/scratch/hyaku/souji-r30/C3JjFixture/` removed after the three delivery files were copied and `cmp`-verified.

## Findings

1. **The kept ref for the abandoned commit is deleted by the gc threshold, not by `jj op abandon`.** After step 4 (`jj util gc --expire=now`, no op abandon yet) the tracked commit has no keep ref any more: `deliver-jj-keep-expiry-run.txt:6` reads `keep_refs=6 ... note=target_keep=no`, while at step 3 it was still present (`:5`, `keep_refs=8 ... target_keep=yes`).

2. **`jj op abandon '..@-'` then `jj util gc --expire=now` drops the four further refs that only abandoned operations were keeping**: `deliver-jj-keep-expiry-run.txt:7` shows `keep_refs=2`. `..@-` is the range form the 0.45.1 help names — `jj op abandon --help`: "To discard recent operations, use `jj op restore <operation ID>` followed by `jj op abandon <operation ID>..@-`".

3. **Abandoning B raises the count by one before any gc** (`:3` 7 to `:4` 8): the abandon rewrites the working copy, and the rewritten head gets its own keep ref. In the probe that second ref is the only one for which the abandoned commit is not an ancestor (`B_ancestor=no`).

4. **The commit object is never removed in this sequence** — `object_present=yes` on all eight steps (`:3`-`:10`). Mechanism, measured: the index still holds the pre-abandon working-copy commit as a head (`Number of heads: 2`, `hidden=true`, one visible head `fd3966775cd9`), that commit descends from the abandoned one, and its keep ref is legitimate. The source says the same: `lib/src/index.rs@v0.45.1:141` "Heads among all indexed commits at the associated operation."; `lib/src/git_backend.rs@v0.45.1:900-901` "Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other unreachable and non-head refs." (https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/index.rs, https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs).

5. **The deletion condition is a head check plus a loose-ref mtime check.** `lib/src/git_backend.rs@v0.45.1:925` `if new_heads.contains(&id) && name_good {` keeps a ref for an index head; `:941` `if mtime > keep_newer {` keeps a ref whose loose file is newer than the threshold; everything else is deleted. The threshold is set in `cli/src/commands/util/gc.rs@v0.45.1:55-56`: `None => SystemTime::now() - Duration::from_secs(14 * 86400),` and `Some("now") => SystemTime::now() - Duration::ZERO,`.

6. **A future `--expire` cannot be expressed in 0.45.1, so the assigned control was replaced.** `cli/src/commands/util/gc.rs@v0.45.1:57` `_ => return Err(user_error("--expire only accepts 'now'")),`; measured `expire=tomorrow rc=1 rejected` at `deliver-jj-keep-expiry-run.txt:8`, with no ref change. The real "not yet expired" arm is the default 14-day threshold: `:9` still `keep_refs=8` and `target_keep=yes`; the threshold is the lever, since `--expire=now` on the same repository (never op-abandoned) then removes the tracked ref (`:10`, `keep_refs=6 ... target_keep=no`).

7. **`git gc --prune=now` cannot prune the abandoned commit here.** At step 3 the commit is reachable through its own keep ref (`:5`, 8 refs, present); and jj's own gc runs git with the same threshold: `lib/src/git_backend.rs@v0.45.1:977` `.arg(format!("--prune=@{} +0000", keep_newer.as_secs()));`.

8. **A rewrite of the index does not free it either.** `jj debug reindex` after the full sequence reports `Finished indexing 5 commits.` and the index still shows 5 commits and 2 heads; the following `jj util gc --expire=now` leaves `keep_refs=2 B_present=yes` (receipt tail).

9. **What the C3 entry (`corpus/knowledge/jj-keep-ref-expiry.md`, not written by this seat) may state from these measurements:** a `refs/jj/keep/*` ref is deleted by the next backend gc whose threshold postdates the loose ref, provided its commit is not an index head — `jj util gc --expire=now` makes that immediate, the default is 14 days, and a future date is unrepresentable; `jj op abandon` is required only for refs that abandoned operations alone kept (8 to 2 here) and is not what removes the tracked commit's own ref; the commit object survives while any kept index head descends from it (measured through two gc rounds and a reindex). The existing Limits line stays true for the docs — `corpus/knowledge/jj-colocation-receipts.md`, section `## Limits`, first bullet: "Keep-ref lifetime. The docs read do not state it." — and the fixture now supplies the measurement instead.

10. **Fixture design decision for the integrator:** no commit ids and no timestamps are printed, so two runs are byte-identical; the tracked commit's keep ref is reported separately in the note as `target_keep=yes|no` so "the ref went" and "the object went" cannot be confused. The tracked ids vary between runs, which is why they are absent from stdout.

## Attack log

Not an attack seat. No counter, predicate or target was challenged; the C3 legs read a record this seat does not write.

## Deliveries

- `.ufo/waves/round-30/w1/deliver-r30-jj-keep-expiry.sh` — fixture payload, 6395 bytes, mode 755, `cmp`-identical to the executed bytes. L1 lands it at `tests/fixtures/r30-jj-keep-expiry.sh`.
- `.ufo/waves/round-30/w1/deliver-jj-keep-expiry-run.txt` — exact stdout of one run, 960 bytes. L1 lands it at `census/round-30/records/jj-keep-expiry-run.txt`; it satisfies C3 L8 (`jj-version: jj 0.45.1...` on line 1, 8 `RESULT ` lines on lines 3-10).
- `.ufo/waves/round-30/w1/receipt-SwarmExecutor06-keepref-mechanism.txt` — mechanism-probe script and its output.
- `.ufo/waves/round-30/w1/SwarmExecutor06.md` — this report.
