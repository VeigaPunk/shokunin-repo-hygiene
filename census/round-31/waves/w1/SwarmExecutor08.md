# SwarmExecutor08 — r31 wave 1 — C3 object clock (fixture + measured record)

## Status

STATUS: PASS — fixture `tests/fixtures/r31-jj-object-clock.sh` delivered and measured with jj 0.45.1
and git 2.56.0; three runs byte-identical (full stdout md5 `3bf8e6a533627b113f7a7acff21f559d`); the
record reaches `object_present=no` and `object_present=yes` in every one of its three arms, satisfying
frozen L8; the L12 shim conditions hold under a local replica of the counter's shim leg.

## Evidence

Lane HEAD `1b811368461785040e955f41f9c97e62f61fd67c`, base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`,
preregistration `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, controls `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc`.
Everything below ran under `/fast/scratch/hyaku/souji-r31/SwarmExecutor08/` with
`TMPDIR=/fast/scratch/hyaku/souji-r31/SwarmExecutor08/tmp`; no install was needed (both binaries were
already at the pinned versions, so no pacman/uv/npx transaction ran).

1. Syntax and three runs (fixture itself, then the delivered copy):
   ```
   $ bash -n final-fixture.sh            -> syntax ok
   $ for i in 1 2 3; do bash final-fixture.sh > drun$i.txt; done   -> rc=0, rc=0, rc=0
   $ md5sum drun1.txt drun2.txt drun3.txt
   3bf8e6a533627b113f7a7acff21f559d  drun1.txt
   3bf8e6a533627b113f7a7acff21f559d  drun2.txt
   3bf8e6a533627b113f7a7acff21f559d  drun3.txt
   $ bash .ufo/waves/round-31/w1/deliver-r31-jj-object-clock.sh > delivered-check.txt
   $ diff drun1.txt delivered-check.txt        -> (no output) delivered copy reproduces the record
   ```
2. Refusal contract (exit 2, four states, each exercised once):
   ```
   TMPDIR unset                    -> ERROR: TMPDIR is unset or empty; refusing to run          rc=2
   TMPDIR=<lane>                   -> ERROR: TMPDIR=.../souji-shokunin is inside the fleet root; refusing to run  rc=2
   TMPDIR=/home/vgpnk/Projects/shokunin -> ERROR: TMPDIR=... is inside the fleet root; refusing to run            rc=2
   TMPDIR=/nonexistent-r31         -> ERROR: TMPDIR=/nonexistent-r31 is not a directory; refusing to run          rc=2
   ```
3. L12 pre-check, a local replica of `census/round-31/c3-counter-v2.py:126-139,189-196` (shim dir
   first on PATH, `jj`/`git` logged and forwarded, fresh TMPDIR):
   ```
   fixture_rc 0   results_equal True   n_results 17   jj_calls 26   git_calls 111
   need {'jj abandon': True, 'jj util gc': True, 'git reflog expire': True, 'git gc': True, 'git cat-file -e': True}
   jj_calls_without_-R: ['jj --version', 'jj ... git init --colocate <repo>' (x3)]
   git_calls_without_-C: ['git --version', 'git --git-dir=. gc --prune=@<unix> +0000' (x5, issued by jj's backend)]
   ```
4. Record (`deliver-jj-object-clock-run.txt`, 19 lines, sha256 `085b87c781dcd323a1576ee92a4a2779c1fa69dce3b62e978e0db315bad207e5`):
   ```
   RESULT arm=solo step=abandon keep_refs=8 target_keep=yes reflog_hits=1 object_present=yes
   RESULT arm=solo step=pack-and-util-gc keep_refs=6 target_keep=no reflog_hits=1 object_present=yes
   RESULT arm=solo step=git-gc-prune-now keep_refs=6 target_keep=no reflog_hits=1 object_present=yes
   RESULT arm=solo step=reflog-expire-then-prune keep_refs=6 target_keep=no reflog_hits=0 object_present=yes
   RESULT arm=solo step=op-abandon-and-util-gc keep_refs=2 target_keep=no reflog_hits=0 object_present=yes
   RESULT arm=solo step=delete-descendant-keep-refs-and-prune keep_refs=1 target_keep=no reflog_hits=0 object_present=no
   RESULT arm=descendant step=abandon keep_refs=12 target_keep=yes reflog_hits=1 object_present=yes
   RESULT arm=descendant step=pack-and-util-gc keep_refs=8 target_keep=no reflog_hits=1 object_present=yes
   RESULT arm=descendant step=git-gc-prune-now keep_refs=8 target_keep=no reflog_hits=1 object_present=yes
   RESULT arm=descendant step=reflog-expire-then-prune keep_refs=8 target_keep=no reflog_hits=0 object_present=yes
   RESULT arm=descendant step=op-abandon-and-util-gc keep_refs=2 target_keep=no reflog_hits=0 object_present=yes
   RESULT arm=descendant step=abandon-descendant-and-op-abandon-and-util-gc keep_refs=2 target_keep=no reflog_hits=0 object_present=no
   RESULT arm=descendant step=git-gc-prune-now-again keep_refs=2 target_keep=no reflog_hits=0 object_present=no
   RESULT arm=reflog-only step=abandon keep_refs=8 target_keep=yes reflog_hits=1 object_present=yes
   RESULT arm=reflog-only step=drop-keep-refs-naming-target keep_refs=6 target_keep=no reflog_hits=1 object_present=yes
   RESULT arm=reflog-only step=git-gc-prune-now keep_refs=6 target_keep=no reflog_hits=1 object_present=yes
   RESULT arm=reflog-only step=reflog-expire-then-prune keep_refs=6 target_keep=no reflog_hits=0 object_present=no
   ```
   Lines 1-2 are the version lines (`jj-version: jj 0.45.1-7c41cdeb…`, `git-version: git version 2.56.0`).
   No id, timestamp or path reaches a RESULT line.

## Findings

1. **The four assigned steps do not remove the object in either assigned arm.** In `solo` and
   `descendant`, `object_present=yes` at steps 1-4 (record lines 3-6 and 9-12). The fixture needed
   two further steps per arm to reach `object_present=no` (L8 of the frozen counter demands at least
   one `no`); the reason each extra step exists is in the fixture header. Location:
   `deliver-jj-object-clock-run.txt:3-15`, `deliver-r31-jj-object-clock.sh:19-40`.
2. **`jj abandon` manufactures a hidden descendant, and that descendant's keep ref is the keeper in
   `solo`.** After `jj abandon '@-'` the working-copy commit is rewritten onto A, and the pre-rewrite
   commit (empty description, parent = B) keeps a `refs/jj/keep/*` ref with `B-is-ancestor ahead=1`.
   It survives two `jj util gc --expire=now` runs and `jj op abandon ..@-` (keep_refs 8 → 6 → 2, one
   descendant ref still standing). Running `jj abandon` on it prints
   `Skipping 1 revisions that are already hidden.` / `No revisions to abandon.` — measured, not
   inferred. Only `git update-ref -d` on that ref plus `git gc --prune=now` removes the object
   (record line 8). Location: `deliver-r31-jj-object-clock.sh:177-181` (the `solo` removal step) and
   the fixture header lines 14-17.
3. **A live descendant outranks jj's own levers.** In `descendant`, C alive holds B through all four
   assigned steps and through `op-abandon-and-util-gc` (record line 13); B goes only when C itself is
   abandoned and the operation views are dropped (line 14) and stays gone at the next prune (line 15).
   Location: `deliver-jj-object-clock-run.txt:9-15`.
4. **The reflog that holds B is the HEAD reflog, and it is a keeper only when no keep ref names B or
   a descendant.** `logs/HEAD` is the only reflog file in the repository (HEAD detached, no
   `refs/heads`, no reflog for `refs/jj/keep/*`); the entry naming B is `HEAD@{1}` with message
   `export from jj`. `reflog-only` isolates it: present with `reflog_hits=1` after every keep ref
   naming B or a descendant is deleted (line 18), absent with `reflog_hits=0` after expire + prune
   (line 19). In `solo` the same expiry leaves the object present (line 6: `reflog_hits=0
   object_present=yes`), so reflog expiry is neither necessary nor sufficient there. Location:
   `deliver-jj-object-clock-reflog-note.md`, `deliver-jj-object-clock-run.txt:6,16-19`.
5. **A third repository was required, and is a superset of the assignment, not a substitution.** The
   assigned order expires the reflog at step 4, before any descendant ref is dropped, so no ordering
   of the assigned steps can show whether a reflog entry alone holds the object. `reflog-only` only
   deletes refs and runs git; it uses no `jj util gc`. Location:
   `deliver-r31-jj-object-clock.sh:207-215`.
6. **Sibling entry draft was corrected and now matches the record.** My first read of
   `.ufo/waves/round-31/w1/deliver-entry-jj-dropped-keep-object-lifetime.md` had a role-2 placeholder
   claiming `solo`'s `reflog-expire-then-prune` removes the object, which the record contradicts
   (line 6). Delivered the correction to `SwarmScribe15-2`; the current draft
   (`deliver-entry-jj-dropped-keep-object-lifetime.md:91-110`) now assigns roles 1-2 to `reflog-only`
   and roles 3-4 to `solo`/`descendant`, with the same arm and step names the record emits.
   Residual nit for the L1: line ~112 brackets as `[INFERENCE]` the claim that `jj abandon` treats
   the rewritten working-copy commit as already hidden; finding 2's `Skipping 1 revisions that are
   already hidden.` output is a measurement, so the bracket can be dropped.
7. **Counter-compatibility pre-check** (not the counter itself): the record has 17 `RESULT` lines,
   `object_present` both `yes` and `no`, and the version lines L8 matches (`jj 0.45.1`, `git version
   2.56`); the L12 shim sees `jj abandon`, `jj util gc`, `git reflog expire`, `git gc`,
   `git cat-file -e`, and the shim's RESULT lines equal the record's exactly. Jj calls without `-R`
   are `jj --version` and the three `jj git init --colocate` calls (`-R` needs an existing jj repo;
   documented in the fixture); git calls without `-C` are `git --version` and jj's own backend
   `git --git-dir=. gc --prune=@<unix> +0000`, which the fixture does not issue.

## Attack log

Not an attack seat. No counter, target or case set is challenged; the only claim-level correction is
finding 6, which is inside another seat's delivery file and was reported to its owner and to the L1
by this report rather than edited (read-only seat).

## Deliveries

- `.ufo/waves/round-31/w1/deliver-r31-jj-object-clock.sh` — the fixture, to land at
  `tests/fixtures/r31-jj-object-clock.sh` (sha256 `780a68233e10ce1268ad9fea7bdb6b3eea89955346fe45918125962c352b4266`, mode 0755).
- `.ufo/waves/round-31/w1/deliver-jj-object-clock-run.txt` — exact stdout of one run, to land at
  `census/round-31/records/jj-object-clock-run.txt` (sha256 `085b87c781dcd323a1576ee92a4a2779c1fa69dce3b62e978e0db315bad207e5`, 19 lines).
- `.ufo/waves/round-31/w1/deliver-jj-object-clock-reflog-note.md` — which reflog held B, with the
  command output behind it.

Risks: the `keep_refs` counts are a function of jj 0.45.1's keep-ref policy (8 at `abandon` for a
two-commit repo, 12 for three), so a jj upgrade changes the numbers even when the mechanism holds;
the record is pinned to jj 0.45.1 and git 2.56.0 by its own version lines. The `solo` removal step
uses `git update-ref -d`, which is deliberate (no jj command removes a hidden head's keep ref) and is
disclosed in the fixture header. Scratch `/fast/scratch/hyaku/souji-r31/SwarmExecutor08` was removed
after the deliveries were copied into the lane; no lane file outside this wave directory was written,
and no `git`/`jj` mutation ran against the lane or the fleet.
