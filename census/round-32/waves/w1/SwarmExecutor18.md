# SwarmExecutor18 — r32 w1 C3 fixture (abandoned object's own mtime clock)

## Status

STATUS: PASS — `tests/fixtures/r32-jj-mtime-clock.sh` and its record are built to the frozen C3
fixture contract: 22 RESULT lines with the contract's six keys, three replays byte-identical, the
L12-equivalent logging shim prints the same lines and shows every required call, both M2/M3
subtraction mutants change the record and drop every `object_present=no` line, and every refusal
path exits 2. Nothing is integrated: the L1 owns placement, the C3 counter run (L1-L14) and the
entry.

## Evidence

Revisions read (read-only): lane HEAD `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`, lane base
`85b61a151923986e7e6b48f7084b9122561b5f3d`, prereg `3ec84fc81b3243429c834a051880b0bcde06291c`.
`git cat-file blob 3ec84fc…:census/round-32/c3-contract.txt | cmp - census/round-32/c3-contract.txt`
→ equal; contract sha256 `9fe3ccd4e2e21b18c8d5351e8074bff2e486d3e7f45d22830bf82592bb2239ad`.

Tools, unmodified, nothing installed: `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`,
`git version 2.56.0`, `GNU bash 5.3.20(1)`.

Three replays (`TMPDIR=/fast/scratch/hyaku/souji-r32/C3Fixture/run/tmpN bash deliver-r32-jj-mtime-clock.sh`,
N=1,2,3): rc=0 each, 24 stdout lines, 22 `RESULT ` lines, 3 `object_present=no` lines.

```
diff run1.out run2.out   -> empty (exit 0)
diff run1.out run3.out   -> empty (exit 0)
```

Record = exact stdout of run 1 (`deliver-jj-mtime-clock-run.txt`, sha256
`01cf6dc0011ae8f22d16922846b6834641df5dbce6e3a26cd0c267ede97e8254`; fixture sha256
`f184cb17a31ca01fd32bacba2db569a99e00fde6a22177430ac47a52e109056b`):

```
jj-version: jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5
git-version: git version 2.56.0
RESULT arm=recent step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=recent step=gc-default obj=B mtime=recent where=cruft object_present=yes
RESULT arm=old step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=old step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=old step=gc-default obj=B mtime=old where=absent object_present=no
RESULT arm=mixed step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=mixed step=start obj=C mtime=recent where=loose object_present=yes
RESULT arm=mixed step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=mixed step=backdate obj=C mtime=recent where=loose object_present=yes
RESULT arm=mixed step=gc-prune-never obj=B mtime=old where=cruft object_present=yes
RESULT arm=mixed step=gc-prune-never obj=C mtime=recent where=cruft object_present=yes
RESULT arm=mixed step=gc-default obj=B mtime=old where=absent object_present=no
RESULT arm=mixed step=gc-default obj=C mtime=recent where=cruft object_present=yes
RESULT arm=never step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=never step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=cruft object_present=yes
RESULT arm=nocruft step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=nocruft step=start obj=C mtime=recent where=loose object_present=yes
RESULT arm=nocruft step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=nocruft step=backdate obj=C mtime=recent where=loose object_present=yes
RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=absent object_present=no
RESULT arm=nocruft step=gc-cruft-disabled obj=C mtime=recent where=loose object_present=yes
```

L14-equivalent, run with the frozen counter's own functions
(`c3-counter.py:83` `contract_bad`, loaded by importlib from the lane path):

```
lines=22 bad=0 []
arms: ['mixed', 'never', 'nocruft', 'old', 'recent']
steps: ['backdate', 'gc-cruft-disabled', 'gc-default', 'gc-prune-never', 'gc-pruneexpire-never', 'start']
wheres: ['absent', 'cruft', 'loose']
no-lines: 3
```

L12-equivalent (logical shims over `jj`, `git`, `touch`, each exec'ing the absolute real binary;
`PATH` led by the shim dir): rc=0, `cmp run1.out shim.out` equal, log counts `jj abandon` 7,
`git reflog expire` 5, `git update-ref -d` 14, `git … gc` 367, `git cat-file -e` 44, `touch` 16
(32 jj calls, 368 git calls).

L13-equivalent, shim bodies copied from `c3-counter.py:107`/`:126` and re-pointed at absolute real
binaries; `mno` compared with the record's 3:

```
M2: rc=0 lines=22 differs=yes no=0<3
M3: rc=0 lines=22 differs=yes no=0<3
```

M2 output (`git` with a `gc`, `prune` or `repack` word neutered to exit 0):

```
RESULT arm=recent step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=recent step=gc-default obj=B mtime=recent where=loose object_present=yes
RESULT arm=old step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=old step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=old step=gc-default obj=B mtime=old where=loose object_present=yes
RESULT arm=mixed step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=mixed step=start obj=C mtime=recent where=loose object_present=yes
RESULT arm=mixed step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=mixed step=backdate obj=C mtime=recent where=loose object_present=yes
RESULT arm=mixed step=gc-prune-never obj=B mtime=old where=loose object_present=yes
RESULT arm=mixed step=gc-prune-never obj=C mtime=recent where=loose object_present=yes
RESULT arm=mixed step=gc-default obj=B mtime=old where=loose object_present=yes
RESULT arm=mixed step=gc-default obj=C mtime=recent where=loose object_present=yes
RESULT arm=never step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=never step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=loose object_present=yes
RESULT arm=nocruft step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=nocruft step=start obj=C mtime=recent where=loose object_present=yes
RESULT arm=nocruft step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=nocruft step=backdate obj=C mtime=recent where=loose object_present=yes
RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=loose object_present=yes
RESULT arm=nocruft step=gc-cruft-disabled obj=C mtime=recent where=loose object_present=yes
```

M3 output (`touch` neutered to exit 0, no backdating; sha256 `572c778e…`, identical byte for byte
to the naive single-object backdate run of finding 3):

```
RESULT arm=recent step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=recent step=gc-default obj=B mtime=recent where=cruft object_present=yes
RESULT arm=old step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=old step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=old step=gc-default obj=B mtime=old where=cruft object_present=yes
RESULT arm=mixed step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=mixed step=start obj=C mtime=recent where=loose object_present=yes
RESULT arm=mixed step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=mixed step=backdate obj=C mtime=recent where=loose object_present=yes
RESULT arm=mixed step=gc-prune-never obj=B mtime=old where=cruft object_present=yes
RESULT arm=mixed step=gc-prune-never obj=C mtime=recent where=cruft object_present=yes
RESULT arm=mixed step=gc-default obj=B mtime=old where=cruft object_present=yes
RESULT arm=mixed step=gc-default obj=C mtime=recent where=cruft object_present=yes
RESULT arm=never step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=never step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=cruft object_present=yes
RESULT arm=nocruft step=start obj=B mtime=recent where=loose object_present=yes
RESULT arm=nocruft step=start obj=C mtime=recent where=loose object_present=yes
RESULT arm=nocruft step=backdate obj=B mtime=old where=loose object_present=yes
RESULT arm=nocruft step=backdate obj=C mtime=recent where=loose object_present=yes
RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=loose object_present=yes
RESULT arm=nocruft step=gc-cruft-disabled obj=C mtime=recent where=loose object_present=yes
```

Refusals, each run to exit (stdout empty in all six):

```
env -u TMPDIR bash fx.sh                       rc=2  ERROR: TMPDIR is unset or empty; refusing to run
TMPDIR= bash fx.sh                             rc=2  ERROR: TMPDIR is unset or empty; refusing to run
TMPDIR=/nonexistent-r32 bash fx.sh             rc=2  ERROR: TMPDIR=/nonexistent-r32 is not a directory
TMPDIR=<lane>/souji-shokunin bash fx.sh        rc=2  ERROR: … is inside the lane; refusing to run
TMPDIR=<fleet>/shokunin bash fx.sh             rc=2  ERROR: … is inside the fleet root; refusing to run
TMPDIR=<scratch> PATH=/nonexistent bash fx.sh  rc=2  ERROR: jj is not on PATH
```

The `mktemp` base guard (fixture header, and the second `case` after `BASE=$(mktemp -d …)`) is
unexercised because the TMPDIR guard fires first; it is defence in depth, not claimed as measured.

## Findings

1. Record shape holds against the frozen contract. 22 RESULT lines, six keys in the frozen order,
   values inside the enumerated sets: contract `census/round-32/c3-contract.txt:5-11`, checked with
   `census/round-32/c3-counter.py:83`. Arms in declared order recent, old, mixed, never, nocruft
   (`c3-contract.txt:6`); steps used are exactly `start`, `backdate`, `gc-prune-never`,
   `gc-default`, `gc-pruneexpire-never`, `gc-cruft-disabled` (`:7`); per-object `mtime` labels and
   `where`/`object_present` read-back are defined in the delivery's header and `where()` at
   `tests/fixtures/r32-jj-mtime-clock.sh:107`, `emit()` at `:122`.
2. What git did in these repositories (run record above): a recent B survives a default `git gc`
   inside a cruft pack; an old B is dropped (`where=absent`); `gc --prune=never` puts the old B and
   the recent C into one cruft pack and a following default gc drops the old B while keeping the
   recent C, so the per-object `.mtimes` clock is carried through the cruft pack; `gc.pruneExpire=never`
   keeps B (cruft); `gc.cruftPacks=false` drops B and leaves the recent C loose.
3. Reported deviation from the arm design, found before delivery and retained as evidence: with
   only B's own loose objects backdated, an old B was still kept — a recent rewritten working-copy
   descendant of B (an unreachable commit `jj abandon` left behind) held it through reachability.
   `diff` of that variant against the delivered record (all three changed pairs):

   ```
   < RESULT arm=old step=gc-default obj=B mtime=old where=absent object_present=no
   > RESULT arm=old step=gc-default obj=B mtime=old where=cruft object_present=yes
   < RESULT arm=mixed step=gc-default obj=B mtime=old where=absent object_present=no
   > RESULT arm=mixed step=gc-default obj=B mtime=old where=cruft object_present=yes
   < RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=absent object_present=no
   > RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=loose object_present=yes
   ```

   The delivered fixture therefore backdates the whole
   unreachable island that reaches B — `island_commits()` at
   `tests/fixtures/r32-jj-mtime-clock.sh:214`, `backdate_commit()` `:222`, `backdate_island()` `:231`
   — which is what isolates the object's own clock; `seal()` also asserts, before any gc, that no
   ref or reflog reaches any island member (`assert_unreachable()` `:185`). Without that isolation
   the record would measure r31's descendant keeper, not this round's clock.
4. `where=pack` never appeared in any arm (observed set loose, cruft, absent). The value stays in
   the contract's enumeration (`c3-contract.txt:10`); no arm is shaped to produce it.
5. Wave-2/seat pitfall: in this persistent shell `command -v touch` resolves to a shell function
   name, so a hand-built shim that does `exec "$R"` recursed into itself (one fixture run wrote
   126 964 log lines before a 90 s timeout). Build hand shims from `type -P`, not `command -v`.
   The frozen counter is unaffected: it resolves `real = {t: shutil.which(t) …}`
   (`census/round-32/c3-counter.py:126`), which returns absolute paths.
6. Determinism: the record carries no commit id, path or timestamp; three runs in three TMPDIRs
   produced identical bytes, and the fixture asserts unreachability (not presence) before the gc
   steps, so a changed git outcome fails loudly instead of silently changing fields.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-r32-jj-mtime-clock.sh` — fixture bytes, mode 755, sha256
  `f184cb17a31ca01fd32bacba2db569a99e00fde6a22177430ac47a52e109056b`; L1 installs as
  `tests/fixtures/r32-jj-mtime-clock.sh`.
- `.ufo/waves/round-32/w1/deliver-jj-mtime-clock-run.txt` — exact stdout of run 1, sha256
  `01cf6dc0011ae8f22d16922846b6834641df5dbce6e3a26cd0c267ede97e8254`; L1 installs as
  `census/round-32/records/jj-mtime-clock-run.txt` (the C3 counter reads that path, L8/L9/L12/L14).
- this report. Scratch `/fast/scratch/hyaku/souji-r32/C3Fixture` removed after copying the two
  deliveries; no lane file was written outside `.ufo/waves/round-32/w1/` and no git/jj state moved.
