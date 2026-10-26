# deliver-docs-f1.md — documentation that lands with the C3 entry (round 31, F1)

Seat: SwarmScribe17 (leaf scribe, item `DocsF1`). Integration owner: the L1. Nothing here is
applied; these are the exact texts the C3 landing commit needs.

**Landing rule (Q56, `corpus/QUALITY.md:135`):** items 1-3 land in the SAME commit as
`corpus/knowledge/jj-dropped-keep-object-lifetime.md`. Item 1 is what makes
`tools/souji-coverage-agreement.py` print `grounded=17 mapped=17` (c3-counter leg L2); without it
the new entry is a `MISSING-FROM-MAP` mismatch and C3 cannot reach `fail=0`. Items 4-5 are the
routed r30-closure defect 1 (`corpus/lessons/round-30-verifier-spotcheck.md:131-133`) plus the new
error pattern; they may land in the same commit or in an immediately following docs commit, but
before the round's final tip.

**Path convention:** paths inside fenced blocks are written as they must read at their
destination — `../census/...` is `corpus/README.md` text (corpus-relative); the PROVINCE and
SKILL blocks are lane-root-relative. This delivery file is not a seat report and is not a gate
input.

**Provenance of the run facts below.** Not measured by this seat. Read from the C3 fixture seat's
output this run:
`/fast/scratch/hyaku/souji-r31/SwarmExecutor08/final-fixture.sh` (step list, lines 2-35) and
`/fast/scratch/hyaku/souji-r31/SwarmExecutor08/frun{1,2,3}.txt` — three byte-identical runs
(`md5 3bf8e6a533627b113f7a7acff21f559d` each), 17 `RESULT` lines, headed
`jj-version: jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5` and
`git-version: git version 2.56.0`. The fixture seat reports the delivery as
`deliver-r31-jj-object-clock.sh` and `deliver-jj-object-clock-run.txt` under this wave directory;
at this seat's last look those two files were not yet on disk, so the scratch paths above were the
bytes read. The committed record does not exist yet at
`census/round-31/records/jj-object-clock-run.txt`. **L1 check before applying items 2-3:** both
must agree with the landed record's `RESULT` lines; if the landed fixture renames a step or moves
an arm, the prose below is the text to adjust, not the counter.

Arms and steps, in record order (verbatim from the record's `RESULT` lines):

```
solo         abandon, pack-and-util-gc, git-gc-prune-now, reflog-expire-then-prune,
             op-abandon-and-util-gc, delete-descendant-keep-refs-and-prune
descendant   abandon, pack-and-util-gc, git-gc-prune-now, reflog-expire-then-prune,
             op-abandon-and-util-gc, abandon-descendant-and-op-abandon-and-util-gc,
             git-gc-prune-now-again
reflog-only  abandon, drop-keep-refs-naming-target, git-gc-prune-now, reflog-expire-then-prune
```

Anchors are against lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; match on the text, not
the line number.

---

## 1. `corpus/README.md` line 39 — in-place F1 row replacement

Anchor: the r12 coverage-map row whose ground cell is `F1 git-native housekeeping vs receipts`
(rendered as `corpus/README.md:39`; matches once).

### Current line (verbatim)

```
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md`, `knowledge/jj-keep-ref-expiry.md` |
```

### Replacement line (verbatim)

```
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md`, `knowledge/jj-keep-ref-expiry.md`, `knowledge/jj-dropped-keep-object-lifetime.md` |
```

### What changes and what does not

- Entries cell gains exactly one backticked span, `knowledge/jj-dropped-keep-object-lifetime.md`,
  appended last; the five existing entries keep their order and wording.
- Status cell is untouched and already reads `frontier, entries held`. F1 is not promoted and no
  row is superseded by a later table (same in-place convention as r28's F4 row, r29's F3 row,
  r30's F1 row).
- The r17 `F1-jj` edge-class row (`:216`) is untouched: it is an edge class, not F1 itself.

Integrator check after the landing commit is made:

```
python3 -B tools/souji-coverage-agreement.py --root . --rev <full40> --base-rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
# expect: grounded=17 mapped=17 dangling=0 mismatches=0    (base: grounded=16 mapped=16)
```

---

## 2. `corpus/README.md` — append after line 641 (end of file)

Append with one blank line before the heading, matching the `## Round 30 — F1 keep-ref expiry
measured` section that ends the file.

```markdown
## Round 31 — F1 object lifetime behind a dropped keep ref

Appended; the sections above stand. One knowledge entry is admitted for F1, measured this round
with real jj 0.45.1 and git 2.56.0 in scratch repositories under the round's scratch root, never
against a lane:

- `knowledge/jj-dropped-keep-object-lifetime.md` — what keeps an abandoned commit's object
  present after its own keep ref is gone, and what removes it. Three arms of a seventeen-step
  fixture, each in its own colocated repository under the round's scratch root: `solo` (A, then B
  on A, B abandoned, nothing built on B), `descendant` (A, B, C on B; B abandoned while C stays
  alive) and `reflog-only` (the keep refs dropped by hand instead of by jj). In every arm B's own
  keep ref goes and B's object stays. In `solo` and `descendant` the ref goes under
  `git pack-refs --all` with `jj util gc --expire=now`, and B then survives `git gc --prune=now`,
  `git reflog expire --expire=now --expire-unreachable=now --all` before another
  `git gc --prune=now`, and `jj op abandon ..@-` with a third `jj util gc --expire=now`. Each arm
  isolates one holder: in `solo` B goes only when the keep refs whose commits descend from B are
  deleted and git is pruned; in `descendant` only when C is abandoned and the operation log
  dropped; in `reflog-only`, where no keep ref names B or a descendant of B, only when the reflog
  entries naming B are expired before the prune. So a dropped keep ref leaves the object held by
  a descendant's keep ref, by a reflog entry naming it, or — sourced from git-gc(1) rather than
  measured here — by its own modification time inside the two-week `gc.pruneExpire` window.
  Presence is not a receipt: a `git cat-file -e` that succeeds says no deletion has completed,
  and a receipt that cannot name both the reflog expiry and the prune date has not established
  one. Fixture `../tests/fixtures/r31-jj-object-clock.sh`; measured record
  `../census/round-31/records/jj-object-clock-run.txt` (`jj-version: jj 0.45.1`,
  `git-version: git version 2.56.0`, seventeen `RESULT` lines, deterministic across runs).

Coverage-map effect: the F1 row at `:39` now names a sixth entry with its status cell unchanged
(`frontier, entries held`); the five entries it already carried are unchanged. F1 stays frontier
— the entry closes the object-prune question, and a measured edge class does not promote a
frontier ground to Core (PROVINCE `## Round 31 boundary note`).

### Frontier (r31)

- F1 — the ref's removal is measured (`knowledge/jj-keep-ref-expiry.md`) and so is the object's
  lifetime behind it (the entry above; `../census/round-31/records/jj-object-clock-run.txt`).
  Remaining: the fleet exposure numerator re-census named at `:46`; and, disclosed rather than
  measured here, which reflog file carries the entry that names B, whether git's cruft-pack
  handling changes the mtime keeper's reach, and the real 90/30-day windows (sourced from
  git-reflog(1) and the `gc.*` config, not waited out by any arm).
- F2, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

### Round 31 corrections

- The r12 F1 row at `:39` was replaced in place rather than superseded by a later table: its
  entries cell gained `knowledge/jj-dropped-keep-object-lifetime.md` and its status cell, already
  `frontier, entries held`, was not reworded. Map rows are edited in place (r28 the F4 row, r29
  the F3 row, r30 this row); the append-only record is this section.
- The r30 boundary note (`PROVINCE.md` `## Round 30 boundary note`) said "the object-prune clock
  that follows a dropped keep ref is unmeasured here", and the r30 `### Frontier (r30)` bullet
  disclosed the same gap. Both stand as history and are not rewritten; the r31 entry is that
  clock's measurement, and the r31 boundary note records the closure.
- The r30 keep-ref section's eight-step description of its own record is unchanged here. What r31
  adds about that record is the packed-ref correction already carried by
  `knowledge/jj-keep-ref-expiry.md` `## Round 30 wave-2 corrections` and now stated in
  `SKILL.md`: a packed keep ref skips the loose-ref age gate, so packedness — not the `--expire`
  threshold — is what the r30 record discriminates.
```

---

## 3. `PROVINCE.md` — append after line 211 (end of file)

One paragraph, matching the shape of `## Round 30 boundary note (F1 keep-ref expiry)`.

```markdown
## Round 31 boundary note (F1 object lifetime)

F1 now holds a measured entry — `corpus/knowledge/jj-dropped-keep-object-lifetime.md` — beside
the four that carried the ground before it and the r30 keep-ref lifetime entry, all named by its
map row at `corpus/README.md:39`. The entry answers what the r30 note left open: after a
`refs/jj/keep/*` ref naming an abandoned commit is removed, that commit's object can still be
held, and three recordings isolate one holder each — a keep ref naming a descendant (the `solo`
arm keeps the object until those refs are deleted), a live descendant commit whose refs and
operation log keep the set alive (the `descendant` arm), and a reflog entry naming the commit
(the `reflog-only` arm, where the object goes only once every reflog entry naming it is expired
before the prune). Expiring the reflog is not by itself a removal: in the first two arms it left
the object present. A fourth holder is sourced, not measured: the object's own modification time
inside the two-week `gc.pruneExpire` window (`git-gc(1)`). One consequence is boundary, not
authority: an object that is present is not evidence of a completed deletion, so a receipt must
name the expiry and the prune date it observed, and the deletion it observed is one the lane ran
or whose argv it recorded. One entry does not promote F1 to Core: Core stays the `## Owns` and
`## Work surfaces` list above (`:60`), the F1 row keeps the status `frontier, entries held`, and
this round adds nothing to either list. What it does not record: which reflog file carries the
naming entries, git's cruft-pack handling of unreachable objects, and the real 90/30-day windows
(sourced from git-reflog(1) and the `gc.*` config, not waited out). Nothing in `tools/` changes —
no receipt class, gate or verdict is added, jj's store GC stays outside this lane, and the r17
receipt-root rule is untouched. Certification OFF, K5 HELD. Sources:
`census/round-31/records/preregistration.txt` claim C3; the entry and its Gate; the run record
`census/round-31/records/jj-object-clock-run.txt`.
```

---

## 4. `SKILL.md` line 115 — replacement of the r30 keep-ref bullet

Anchor: the bullet beginning `- **jj: a keep ref is removed by jj's own gc threshold, never by
`git gc` alone**` (`grep -n 'a keep ref is removed by jj' SKILL.md` → `115`; matches once).
Routed r30-closure defect 1 asks for two fixes, both applied here: the packed-ref caveat, and
`leaves two keep refs where eight stood` (the committed record's step 5 goes 6 → 2, not 8 → 2:
`census/round-30/records/jj-keep-expiry-run.txt` steps 4, 5).

### Current line (verbatim)

```
- **jj: a keep ref is removed by jj's own gc threshold, never by `git gc` alone** (r30, F1; headline corrected in round 30 wave 2, the first wording claimed the operation log owns the lifetime, refuted by step 4 of the record): `git gc --prune=now` leaves a `refs/jj/keep/*` ref naming an abandoned commit in place, while `jj util gc --expire=now` removes that ref and `jj op abandon ..@-` before a second `jj util gc` leaves two keep refs where eight stood; the commit object stayed present at every step, so a dropped keep ref is not a deleted object. The default threshold is two weeks ("By default, only obsolete objects and operations older than 2 weeks are pruned." — `jj util gc --help`, jj 0.45.1) and `--expire` accepts only the string `now`, so an unrun `util gc` keeps a keep-only head alive and a kept ref is not evidence the content is reachable from a durable root. Facts, source rows and limits: `corpus/knowledge/jj-keep-ref-expiry.md`; recheck `bash tests/fixtures/r30-jj-keep-expiry.sh`.
```

### Replacement (verbatim, one line)

```
- **jj: a keep ref is removed by jj's ref-set rewrite, and a packed one skips the age gate** (r30, F1; headline corrected in round 30 wave 2 — the first wording claimed the operation log owns the lifetime, refuted by step 4 of the record — and the lever corrected in round 31 from the routed closure defect: packedness, not the threshold, is what the record discriminates): `git gc --prune=now` leaves a `refs/jj/keep/*` ref naming an abandoned commit in place, while `jj util gc --expire=now` removes that ref, and `jj op abandon ..@-` before a second `jj util gc` takes six keep refs to two (`keep_refs` 6 to 2 at step 5, none of them naming the abandoned commit). The ref's storage form decides whether the age gate can save it: a ref packed by `git gc` or `git pack-refs --all` has no loose file whose mtime the gate reads, so a default-threshold `jj util gc` deleted it (8 to 6) while the loose control kept it — the `--expire=now` threshold is sourced (S220, S054), not measured. The default threshold is two weeks ("By default, only obsolete objects and operations older than 2 weeks are pruned." — `jj util gc --help`, jj 0.45.1) and `--expire` accepts only the string `now`, so an unrun `util gc` keeps a keep-only head alive and a kept ref is not evidence the content is reachable from a durable root. The commit object stayed present at every step of the record, so a dropped keep ref is not a deleted object; what holds or drops that object is `corpus/knowledge/jj-dropped-keep-object-lifetime.md`. Facts, source rows and limits: `corpus/knowledge/jj-keep-ref-expiry.md`; recheck `bash tests/fixtures/r30-jj-keep-expiry.sh`.
```

### Grounds for each changed clause

- `ref-set rewrite` in the headline: `recreate_no_gc_refs` builds the set
  (`corpus/knowledge/jj-keep-ref-expiry.md:19-24`, S054 `git_backend.rs:900-903,:917-961`).
- packed-ref caveat: `corpus/knowledge/jj-keep-ref-expiry.md:128` (wave-2 corrections) and its
  ground `census/round-30/waves/w2/SwarmCritic21.md:22` — packed arm `keep_refs` 8→6,
  `target_keep=no`, loose control kept; mechanism `git_backend.rs:939` loose-metadata fall-through.
- `six keep refs to two`: `census/round-30/records/jj-keep-expiry-run.txt` step 4 `keep_refs=6`,
  step 5 `keep_refs=2`, `note=target_keep=no` at both. The old `eight stood` named step 3's count,
  not the count the step began from.
- `--expire=now` sourced not measured: `corpus/knowledge/jj-keep-ref-expiry.md:133` (mutant with
  the default threshold printed a byte-identical record).
- the forward pointer to the r31 entry: item 1's entry, whose `## Claim` steps 2-6 carry the
  mechanism.

---

## 5. `SKILL.md` — one new bullet in `## Error patterns (false-SAFE signatures)`

Insert immediately after the bullet replaced in item 4 (still line 115 before this round's edits),
before the bullet beginning `- **jj: nested `.git` → phantom deletions**` (line 116).

```markdown
- **jj: an object outlives its keep ref, so presence is not a receipt** (r31, F1): once the `refs/jj/keep/*` ref naming an abandoned commit is gone, its object can still be held, and each arm of the recorded fixture isolates one holder — a keep ref naming a descendant (object present until those refs are deleted and git pruned), a live descendant commit whose refs the keep set is rebuilt from (S054), and a reflog entry naming the commit (S222, S063), which is the only holder left after the keep refs are dropped by hand and which releases the object only when the entries are expired before the prune. Expiring every reflog entry naming the commit removes no object while a keep ref still reaches it, and a fourth holder is sourced rather than measured: the object's own modification time inside the two-week `gc.pruneExpire` window (S063). So `git cat-file -e <id>` succeeding proves that no deletion completed, and nothing about whether one was attempted or authorised; the receipt-grade observation is the other direction — the id absent after a `git gc` whose prune date is at or after the object's mtime, with the reflog entries naming it expired (or their windows asserted), and that `git gc` must be one the lane ran or whose argv it recorded. Facts, source rows and limits: `corpus/knowledge/jj-dropped-keep-object-lifetime.md`; recheck `bash tests/fixtures/r31-jj-object-clock.sh`.
```

Grounds: the record's `RESULT` lines per arm (the file cited in the provenance block) plus the
r31 entry's `## Claim` steps 1-7 and its `## Consequence for souji receipts` paragraph;
`## What this does NOT establish` carries the limits (reflog windows sourced, not measured;
cruft-pack handling not read in depth). The bullet cites the entry, not new bytes.

Sentence-to-record map, so a later reader can check the bullet:

| bullet clause | record lines |
|---|---|
| keep ref naming a descendant holds the object | `solo`: present through `op-abandon-and-util-gc` (keep_refs 2), absent only at `delete-descendant-keep-refs-and-prune` |
| live descendant commit keeps the set alive | `descendant`: present through `op-abandon-and-util-gc`, absent only at `abandon-descendant-and-op-abandon-and-util-gc` |
| a reflog entry is the last holder, released only by expiry before the prune | `reflog-only`: present at `drop-keep-refs-naming-target` and `git-gc-prune-now` with `reflog_hits=1`, absent at `reflog-expire-then-prune` with `reflog_hits=0` |
| expiring the reflog removes nothing while a keep ref still reaches it | `solo` and `descendant`: `reflog-expire-then-prune` has `reflog_hits=0` and `object_present=yes` |
| mtime holder is sourced, not measured | no arm relies on the default window; every prune in the record uses `--prune=now` |

---

## Out of scope for this delivery (named, not drafted)

- `SKILL.md` `## Gate registry` row for `r31-jj-object-clock` — the C3 counter reads the entry's
  Gate, the fixture and the record, not the registry; a registry row is a separate landing.
- `corpus/SOURCES.md` rows for S222 and the re-cited held rows — item `SourcesRows`
  (`deliver-sources-rows.md`); this delivery cites no new S-id so the entry's `source:` line
  stays the single authority.
- `corpus/lessons/round-31.md` and the `## Gate` admission table, the README sections for C1/C2,
  the SCORECARD supersession rows and the M1 carry sections — other seats.
- `corpus/knowledge/jj-keep-ref-expiry.md` itself: its wave-2 corrections already state the
  packed-ref finding; r31 does not rewrite the r30 entry, only the SKILL bullet that lagged it.
- Promotions: nothing here promotes F1 to Core, changes a receipt class, or moves certification
  (OFF) or K5 (HELD).
