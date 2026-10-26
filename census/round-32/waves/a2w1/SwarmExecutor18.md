# SwarmExecutor18 — independent replication of C3 at a92e1aae (r32 a2w1)

STATUS: PASS — from a `git archive` export of a92e1aae the C3 fixture replays twice with RESULT lines byte-identical to the committed record; the mtime clock reproduces by hand in both a plain git repo and a fresh colocated jj 0.45.1 repo; c3-counter.py prints `legs=14 fail=0` and c3-counter-v2.py prints `legs=17 fail=0`. No counter FAIL line occurred anywhere.

## Evidence

Revision under test: `a92e1aae91dbf46c2d7eff713932cfc820186970` (landing commit); base `85b61a151923986e7e6b48f7084b9122561b5f3d`; list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`. Host bins: `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`, `git version 2.56.0` (same as the record's version lines).

### 1. Fixture replay from an export of the landing commit

```
mkdir -p /fast/scratch/hyaku/souji-r32/ReplicateC3/{exp,t1,t2}
git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive a92e1aae91dbf46c2d7eff713932cfc820186970 | tar -x -C .../exp
TMPDIR=.../t1 bash tests/fixtures/r32-jj-mtime-clock.sh   # rc=0, 24 lines (2 version + 22 RESULT)
TMPDIR=.../t2 bash tests/fixtures/r32-jj-mtime-clock.sh   # rc=0, 24 lines
diff <(grep '^RESULT ' run1.txt) <(grep '^RESULT ' exp/census/round-32/records/jj-mtime-clock-run.txt)  # empty, IDENTICAL_RUN1
diff <(grep '^RESULT ' run2.txt) <(the same record)                                                    # empty, IDENTICAL_RUN2
sha256sum exp/census/round-32/records/jj-mtime-clock-run.txt
  01cf6dc0011ae8f22d16922846b6834641df5dbce6e3a26cd0c267ede97e8254   (1887 B, 22 RESULT lines)
```

The committed fixture, entry and record bytes at the lane tip equal the export bytes:
`tests/fixtures/r32-jj-mtime-clock.sh` f184cb17a31ca01fd32bacba2db569a99e00fde6a22177430ac47a52e109056b (12188 B, last touched by a92e1aa),
`corpus/knowledge/jj-abandoned-object-mtime-clock.md` d7901ad3997d441b607104797a5fc73a932086ba870e4be8a09c657165561197 (24692 B).
The record hash also equals the w1 delivery file named by the entry (`.ufo/waves/round-32/w1/deliver-jj-mtime-clock-run.txt`, 1887 B) and the entry's claimed hash.

### 2. Hand reproduction, plain git (no fixture code)

Built A, B (child of A), moved the branch back and expired all reflogs, so B is unreachable and loose; then ran gc.

```
case recent (default git gc):      B loose before -> after_default_gc where=cruft present=yes
case old (3 loose objects touched 30 days back, epoch 1790427625): after_default_gc where=absent present=no
mixed (B old, C recent, gc --prune=never): pre B=loose C=loose -> B=cruft C=cruft
   after_gc_prune_never .mtimes: B_commit mtime=1790427682 age=old ; C_commit mtime=1793019682 age=recent
   after default git gc:        B_present=no ; C_present=yes (remaining cruft pack all recent)
never (git -c gc.pruneExpire=never gc): B present in cruft, .mtimes value 1790427741 (old); C 1793019741 (recent)
nocruft (git -c gc.cruftPacks=false gc): B absent; C loose; zero .mtimes files
```

Backdate epoch `now-30d` = 1790427xxx, "recent" values 1793019xxx (`date +%s` = 1793019631..1793019789 during the runs); the 15-day cut separates them unambiguously.

### 3. Hand reproduction, fresh colocated jj repo (jj 0.45.1)

`jj git init --colocate`, describe A, `jj new`, describe B, `jj abandon '@'`, drop every `refs/jj/keep` ref naming B or a descendant, `git reflog expire --expire=now --expire-unreachable=now --all`:

```
arm old:    A=8a44d7b9... B=7332ed4f... keep_refs_seen=7 dropped=1
            after_seal where=loose present=yes ; backdated_objects=3 ; git gc rc=0 -> where=absent present=no
arm recent: A=332690a8... B=cc6c25ed... keep_refs_seen=7 dropped=1
            after_seal where=loose present=yes ; git gc rc=0 -> where=cruft present=yes
```

### 4. Counters at the landing commit

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c3-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev a92e1aae91dbf46c2d7eff713932cfc820186970 \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --scratch /fast/scratch/hyaku/souji-r32/ReplicateC3/cnt
  L1..L14 all PASS; SUMMARY legs=14 fail=0 f1_entries=5 rev=a92e1aae91dbf46c2d7eff713932cfc820186970   (rc=0)

python3 -B .../c3-counter-v2.py <same args, --scratch .../cntv2>
  L1..L17 all PASS; SUMMARY legs=17 fail=0 f1_entries=5 rev=a92e1aae91dbf46c2d7eff713932cfc820186970   (rc=0)
  L15 PASS probe recent_present=True old_present=False record recent=yes old=no
  L16 PASS abandon=7 nonzero=0 gc=6 nonzero=0 cat_file_e=44 rc0=38 results=22
  L17 PASS refetched=4 bad=[]
```

No FAIL lines exist in either run. Scratch `/fast/scratch/hyaku/souji-r32/ReplicateC3` removed after the runs.

### 5. Fixture guards

```
env -u TMPDIR bash tests/fixtures/r32-jj-mtime-clock.sh                 -> rc=2, "TMPDIR is unset or empty; refusing to run"
TMPDIR=/home/vgpnk/Projects/shokunin/souji-shokunin bash ...fixture      -> rc=2, "is inside the lane; refusing to run"
```

### 6. Tooling

No install or upgrade was needed or performed: the record's exact jj and git versions are already on the host.

## Findings

1. The record is reproducible from the landing commit alone: two independent runs of `tests/fixtures/r32-jj-mtime-clock.sh` from a `git archive` export of a92e1aae print 22 RESULT lines identical, in the same order, to `census/round-32/records/jj-mtime-clock-run.txt:3-24` (verified with `diff`, rc 0). The fixture's RESULT lines carry no per-run token, so this is deterministic and not a hash luck.
2. The record's central pair is confirmed without any fixture code: `RESULT arm=recent step=gc-default obj=B ... where=cruft object_present=yes` (record line 4) matches my plain-git recent arm, and `RESULT arm=old step=gc-default obj=B ... where=absent object_present=no` (record line 7) matches my 30-day-backdated arm. The decision is the object's own loose-file mtime, not reachability: in both repos B was unreachable from every ref and reflog before the gc.
3. The mixed case is confirmed at both layers: after `git gc --prune=never` the cruft pack's `.mtimes` holds B's clock as old (1790427682, = run time minus 30 days) and C's as recent (1793019682); the following default `git gc` then drops B (`record line 14`) and keeps C in the cruft pack (`record line 15`). So the clock is genuinely per object inside one pack, not per pack.
4. The `never` and `nocruft` arms also reproduce by hand: `git -c gc.pruneExpire=never gc` leaves the old B in a cruft pack with its old mtime (`record line 18`), and `git -c gc.cruftPacks=false gc` drops the old B while the equally unreachable recent C survives loose with no `.mtimes` file at all (`record lines 23-24`). This isolates `gc.cruftPacks` as the sole switch for the where=loose/cruft difference, as the entry claims.
5. Measured `.mtimes` layout (extra detail the entry deliberately does not claim — `corpus/knowledge/jj-abandoned-object-mtime-clock.md:161-162` says "The `.mtimes` contents are never read"): 12-byte header `MTME` + big-endian u32 version 1 + u32 hash-type 1, then one big-endian u32 mtime per object in pack order, then the 20-byte pack hash, then a 20-byte checksum of the file. Sizes checked: 12+3*4+40=64 B for a 3-object cruft pack, 12+6*4+40=76 B for a 6-object pack. A backdated blob alone (commit and tree recent) received the old value while its commit/tree stayed recent, which confirms the per-object clock rather than a pack-level one.
6. The entry's provenance pins bind: its line 4 claims the run record is the w1 delivery with sha256 `01cf6dc0011ae8f22d16922846b6834641df5dbce6e3a26cd0c267ede97e8254`, 1887 B, 22 RESULT lines — the committed record, my export copy and the on-disk w1 delivery all hash to exactly that.
7. Hygiene note, not mine and not touched: `census/round-32/__pycache__/c1-counter-v2.cpython-314.pyc` (mtime 2026-10-26 05:31, attempt-1 origin) sits ignored under the lane (`git check-ignore` -> `.gitignore:3:__pycache__/`). It is untracked and invisible to `git status`; the L1 may want a `-B` discipline note in the round lesson rather than a tree change.
8. The lane worktree is currently dirty from other seats (`SKILL.md`, `tests/fixtures/r15-preservation-frozen/{expected,record}.json` modified, `?? census/round-32/records/a2-l1-salvage-tip-measure.txt`); the C3 files themselves are byte-identical to a92e1aae. Left untouched.

## Attack log

My item is a falsification attempt on the landed C3 claim; each vector below was executed, not reasoned about.

- A1 — "the fixture prints constants and never executes the commands". Counter-measure executed: the counter's shim run reports L16 `abandon=7 nonzero=0 gc=6 nonzero=0 cat_file_e=44 rc0=38 results=22`, i.e. seven successful `jj abandon` calls, six successful `git gc` calls and 44 `git cat-file -e` calls with both exit classes. Independently, my fixture-free builds in sections 2 and 3 reach the same present/absent outcomes, so no constant table can be the source. Not landed.
- A2 — "the record was hand-edited after the run". Counter-measure: replay from the pure `git archive` export (no `.git`, no wave scratch) reproduces every RESULT line byte-for-byte twice, and the record hash equals the pre-landing w1 delivery hash. Not landed.
- A3 — "the difference is not caused by gc or by backdating". Counter-measure: M2 (gc/prune/repack calls neutered) and M3 (touch neutered) both print 22 RESULT lines that differ from the record and have 0 `object_present=no` lines versus 3 in the record; my hand runs reproduce the same causal pair with real gc and real `touch -d`. Not landed.
- A4 — "where=cruft is a guess that could mislabel a plain pack". Counter-measure: every cruft pack I produced in the hand runs does carry a `.mtimes` sibling, every plain pack does not, and I read the table contents to confirm the ages (section 2/5). Not landed.
- A5 — "the fixture would run outside scratch". Counter-measure: both refusal guards exit 2 before creating anything. Not landed.
- A6 — "the landing commit's counters hold only through the counter's own helpers". Counter-measure: the hand reproductions above use only git/jj/touch with no lane code; they agree with the record on every arm. Not landed.

No attack landed; no ATTACK is filed against the frozen contract or counters.

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmExecutor18.md` (this report). No other lane file was written; scratch removed.
