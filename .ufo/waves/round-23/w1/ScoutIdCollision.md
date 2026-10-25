# ScoutIdCollision — frozen id-collision step (C3)

## Status

STATUS: PASS — the frozen collision step ran at lane revision
`1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` and returns **6 colliding ids (S109–S114)**, not the 3
the preregistration names; every collision is resolved by document (both sides' title and URL
pasted below), the 0–3-space extractor is proven to catch an indented collision that a
column-zero-only pattern misses, and the staged rows for git-count-objects / git-fsck / git-prune
are confirmed **S112 / S113 / S114**. Two counter-level defects found (see Attack log) and two
adoption defects the id step cannot see (E09 recheck form, stale `used-by`) are recorded with
receipts.

## Evidence

All paths absolute. Lane = `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Staged package = `/home/vgpnk/Projects/shokuknow/merge/souji/`.
Scratch = `/var/tmp/souji-r23-ScoutIdCollision` (removed after this report).
No tool installs or upgrades were performed this run.

### E1 — the frozen step, verbatim

```
$ S=/home/vgpnk/Projects/shokuknow
$ A=/var/tmp/souji-r23-ScoutIdCollision; mkdir -p "$A"
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > "$A/reg-ids"
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' "$S/merge/souji/SOURCES.append.md" | grep -oE 'S[0-9]+' | sort > "$A/staged-ids"
$ comm -12 "$A/reg-ids" "$A/staged-ids" > "$A/collisions"
reg count: 114
staged count: 134
=== collisions ===
S109$
S110$
S111$
S112$
S113$
S114$
collision count: 6
```

Both id sets are contiguous ranges, verified against `seq`:

```
$ seq -f 'S%03g' 1 114   | diff -q - "$A/reg-ids"    -> identical  (reg  = S001..S114)
$ seq -f 'S%03g' 109 242 | diff -q - "$A/staged-ids" -> identical  (staged = S109..S242)
```

Registry shape at the revision (no intra-registry duplicate, all rows at column 0):

```
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort | uniq -d
(empty)
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | sed -E 's/^([ ]*).*/\1/' | awk '{print length($0)}' | sort | uniq -c
    114 0
$ registry loose rows: 114  frozen: 114
$ staged   loose rows: 134  frozen: 134
```

The frozen extractor loses nothing on either file: the loose `| S### |` count equals the frozen
count on both sides (114/114, 134/134).

### E2 — every colliding id, resolved by document

Lane side (`corpus/SOURCES.md`, lines 129–134) versus staged side
(`/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`, lines 7–12).

| id | LANE title | LANE URL | STAGED title | STAGED URL |
|---|---|---|---|---|
| S109 | souji round-2 RENAME_NOREPLACE probe, vendored (`lanes/souji/round2/evidence/noreplace_probe.py` + `noreplace-probe.out`) | *(own-work — no URL)* | git-fetch(1) | https://git-scm.com/docs/git-fetch |
| S110 | rename(2), man-pages 6.19 | https://man7.org/linux/man-pages/man2/rename.2.html | git/git v2.56.0 builtin/fetch.c, merge.c, rebase.c, am.c, commit.c | https://github.com/git/git/blob/v2.56.0/builtin/fetch.c |
| S111 | mv(1), GNU coreutils | https://man7.org/linux/man-pages/man1/mv.1.html | git/git v2.56.0 builtin/pull.c | https://github.com/git/git/blob/v2.56.0/builtin/pull.c |
| S112 | gio(1), GIO commandline tool (glib2 2.90.1) | https://man.archlinux.org/man/gio.1.en | **git-count-objects(1)** | **https://git-scm.com/docs/git-count-objects** |
| S113 | GLib GIO g_file_trash() method reference | https://docs.gtk.org/gio/method.File.trash.html | **git-fsck(1)** | **https://git-scm.com/docs/git-fsck** |
| S114 | statx(2), man-pages 6.19 | https://man7.org/linux/man-pages/man2/statx.2.html | **git-prune(1)** | **https://git-scm.com/docs/git-prune** |

Not one of the six pairs is the same document. The preregistration's claim that "S112-S114 are the
quarantine rows" is true for those three and **incomplete for the other three** (S109–S111 are the
round-22 rename/mv/probe rows).

### E3 — the confirmation asked for: git-count-objects / git-fsck / git-prune

```
=== URL of each staged row S109-S114 ===
S109  title=git-fetch(1)                        url=https://git-scm.com/docs/git-fetch
S110  title=git/git v2.56.0 builtin/fetch.c,... url=https://github.com/git/git/blob/v2.56.0/builtin/fetch.c
S111  title=git/git v2.56.0 builtin/pull.c      url=https://github.com/git/git/blob/v2.56.0/builtin/pull.c
S112  title=git-count-objects(1)                url=https://git-scm.com/docs/git-count-objects
S113  title=git-fsck(1)                         url=https://git-scm.com/docs/git-fsck
S114  title=git-prune(1)                        url=https://git-scm.com/docs/git-prune
```

CONFIRMED: staged **S112 = git-count-objects(1) → https://git-scm.com/docs/git-count-objects**,
**S113 = git-fsck(1) → https://git-scm.com/docs/git-fsck**,
**S114 = git-prune(1) → https://git-scm.com/docs/git-prune**. By document these are the lane's
proposed S115/S116/S117 (`corpus/lessons/round-22.md:432` and the preregistration C1 "Sourced
ground: S115/S116/S117 (git-count-objects, git-fsck, git-prune)").

### E4 — guard proof: the 0–3-space extractor catches an indented collision

Scratch fixture, lane side carrying `  | S115 |` (two leading spaces — still a markdown table row),
staged side carrying `| S115 |` at column 0:

```
$ cat -A "$F/reg-fixture.md" | sed -n '4,6p'
| S114 | lane-row-B M-bM-^@M-^T https://example.invalid/b | ... |$
  | S115 | lane-row-C-INDENTED M-bM-^@M-^T https://example.invalid/c | ... |$

=== FROZEN pattern (0-3 leading spaces) on fixture registry ===
S113
S114
S115

=== COLUMN-ZERO-ONLY pattern (control) on fixture registry ===
S113
S114

=== frozen collisions ===
S114
S115
frozen collision count: 2

=== control (column-zero) collisions ===
S114
control collision count: 1
```

The column-zero-only pattern reports **1** collision and silently drops the S115 row; the frozen
pattern reports **2**, including the indented one. The guard is real, not decorative.

Boundary probe — a **4**-space indent is *not* a table row (markdown indented code block), and the
frozen pattern correctly declines it:

```
$ printf '    | S999 | four-space — https://example.invalid/z | ...\n' > "$F/fourspace.md"
$ grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' "$F/fourspace.md"
0
```

So the frozen `{0,3}` bound is exactly the markdown table-row bound: it widens past column zero and
stops at the code-block threshold.

### E5 — the C3 control and the adoption arms, run against `sources-census.sh validate`

Each arm is a **copy** of the lane corpus under scratch plus a scratch `shokunin.conf`; no lane byte
was written. Rows were inserted inside `## Registry` (before `## Paths`, line 136) so E12 does not
fire.

Lane baseline, unmodified (read-only, sanctioned by the preregistration):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
rc=0
30 x souji  W04  S### duplicate url <url> across scopes
souji  ok  /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
E-codes: 0
```

**CONTROL arm** — the three staged rows appended **as-is** (ids S112/S113/S114):

```
rc=1
souji	E03	S112 duplicate id
souji	E09	S112 recheck=on-release — re-read `man git-count-objects` after a host git upgrade
souji	E03	S113 duplicate id
souji	E09	S113 recheck=on-release — re-read `man git-fsck` after a host git upgrade
souji	E03	S114 duplicate id
souji	E09	S114 recheck=on-release — re-read `man git-prune` after a host git upgrade
souji	E11	S112 missing used-by corpus/knowledge/repo-size-census-readonly.md
souji	E11	S112 missing used-by corpus/knowledge/count-objects-garbage-semantics-r23.md
souji	E11	S113 missing used-by corpus/knowledge/repo-size-census-readonly.md
souji	E11	S113 missing used-by corpus/knowledge/count-objects-garbage-semantics-r23.md
souji	E11	S114 missing used-by corpus/knowledge/repo-size-census-readonly.md
```

The preregistered control **fires**: `E03 duplicate id` on all three, exit 1.

**FIX arm** — rows re-pointed **by document** to S115/S116/S117, other cells untouched:

```
rc=1
souji	E09	S115 recheck=on-release — re-read `man git-count-objects` after a host git upgrade
souji	E09	S116 recheck=on-release — re-read `man git-fsck` after a host git upgrade
souji	E09	S117 recheck=on-release — re-read `man git-prune` after a host git upgrade
souji	E11	S115 missing used-by corpus/knowledge/repo-size-census-readonly.md
souji	E11	S115 missing used-by corpus/knowledge/count-objects-garbage-semantics-r23.md
souji	E11	S116 missing used-by corpus/knowledge/repo-size-census-readonly.md
souji	E11	S116 missing used-by corpus/knowledge/count-objects-garbage-semantics-r23.md
souji	E11	S117 missing used-by corpus/knowledge/repo-size-census-readonly.md
```

`E03` is gone (id re-pointing works) but **two non-id defects survive**, so re-pointing the id alone
does not make the rows landable (Findings 3 and 4).

**FIX2 arm** — id re-pointed **and** `recheck` normalised to `90d` **and** `used-by` re-pointed to
the two entries this round adopts:

```
rc=1
souji	E11	S115 missing used-by corpus/knowledge/repo-size-census-readonly.md
souji	E11	S115 missing used-by corpus/knowledge/count-objects-garbage-semantics-r24.md
souji	E11	S116 missing used-by corpus/knowledge/repo-size-census-readonly.md
souji	E11	S116 missing used-by corpus/knowledge/count-objects-garbage-semantics-r24.md
souji	E11	S117 missing used-by corpus/knowledge/repo-size-census-readonly.md
souji	E11	S117 missing used-by corpus/knowledge/count-objects-garbage-semantics-r24.md
E-codes: 6  E03: 0  E09: 0  E11: 6
```

All six residual findings are exactly "the two adopted entries do not exist on disk yet", one per
row per entry. Nothing else is wrong with the re-pointed rows. This fixes the **order** of landing
(Findings 5).

### E6 — frozen collision step re-run on each arm

```
control: reg=117 collisions=S109 S110 S111 S112 S113 S114
fix:     reg=117 collisions=S109 S110 S111 S112 S113 S114 S115 S116 S117
```

The FIX arm's collision list **grew** from 6 to 9. See Attack 2.

## Findings

1. **Six collisions, not three.** `corpus/SOURCES.md:129-134` × `SOURCES.append.md:7-12`: S109,
   S110, S111, S112, S113, S114. The preregistration C3 line "registry holds 114 rows (max S114);
   staged S112-S114 collide" understates the set by three. The frozen *command* is right; the
   frozen *prose* is not. Adoption and re-pointing must be done against the 6-id set.

2. **The two id spaces are both contiguous ranges, so the overlap is arithmetic, not accidental.**
   reg = S001..S114, staged = S109..S242 (`seq` diff, E1). Overlap = S109..S114 exactly. Any lane id
   in **[115, 242]** collides with a staged id by construction (Attack 2).

3. **The staged `recheck` cell fails the lane's own validator (E09), independent of ids.**
   `SOURCES.append.md:10-12` carry `recheck = "on-release — re-read `man git-count-objects` after a
   host git upgrade"`. `scripts/sources-census.sh:28` accepts only "ISO date, NNd, or symbolic
   cadence"; the em-dash prose makes it neither. Lane rows S109–S114 use `90d`/`180d`. Receipt: E5
   FIX arm, 3 × E09. The adoption must rewrite this cell (e.g. `90d`) or the census never exits 0.

4. **The staged `used-by` cell names the wrong entry, and this is a document-level error the id
   step cannot see.** `SOURCES.append.md:10-11` cite
   `corpus/knowledge/count-objects-garbage-semantics-r23.md`; the entry round 23 adopts is
   `count-objects-garbage-semantics-r24.md`. `corpus/knowledge/count-objects-garbage-semantics-r23.md`
   is **ABSENT** in the lane (checked), so appending verbatim leaves a dangling used-by even after a
   perfect id re-point. Receipt: E5 FIX arm, E11 lines naming `-r23.md`.

5. **Landing order is load-bearing: entries before rows.** With `used-by` pointed at the two adopted
   entries, the only residual findings are `E11 missing used-by` for those two paths (E5 FIX2 arm,
   6 findings = 3 rows × 2 entries). Appending the registry rows before the entry files exist
   guarantees census exit 1. The rows must land **after** the two knowledge files.

6. **Nine staged rows duplicate a lane document by URL, not just by id.** Computed over field 2 of
   every row: staged S115→lane S111 (mv(1)), S116→S110 (rename(2)), S117/S125→S114 (statx(2)),
   S126→S113 (g_file_trash), S137→S112 (gio(1)), S143→S042/S057 (git-config),
   S169→S002/S063 (git-gc), S170→S001 (git-maintenance). Appending any of these verbatim adds a
   second row for a document the lane already holds. The URL, not the id, is what makes re-pointing
   safe — this is the map the "by document" rule needs.

7. **The lane already cites S118 with no row behind it.** `corpus/lessons/round-22.md:354` and
   `corpus/lessons/round-22-verifier-spotcheck.md:204` both cite `S118`; the registry holds **0**
   S118 rows (`grep -c` = 0). Staged S118 is the DOI paper
   (`https://doi.org/10.1109/SEQUEN.1997.666900`). This is a dangling id from the *staged* space
   living in the lane's prose — exactly the leak the collision step is supposed to prevent, and it
   sits in committed lesson text, so it is append-only and cannot be edited away.

8. **The collision is a recurrence, not a first occurrence.** `corpus/lessons/round-22.md` M16
   already recorded the same shape: "Adopting the staged rows verbatim would have opened the lane
   registry at S115–S137 with S109–S114 unused", and the same fix discipline ("every citation is
   re-pointed by document: campaign S124→S109, S116→S110, S115→S111, S137→S112, S126→S113,
   S117→S114"). The staged package was re-staged on 2026-10-24 with the same S109+ numbering, so
   round 23 meets the identical collision the round-22 fix created.

9. **The frozen extractor is complete on the live bytes.** Loose `| S### |` row count equals frozen
   count on both files (114/114, 134/134), and the registry has 0 intra-file duplicate ids. No row in
   either file hides behind indentation or a fence today.

## Attack log

**Attack 1 — the C3 prose names 3 collisions where the frozen command yields 6.** Not repairable by
me (predicates are frozen after data), reported instead. Any adoption plan written against
"S112-S114 collide" leaves S109–S111 unexplained, and the round-22 record shows what happens when
that residue is left implicit: the fix map had to be reconstructed by hand a round later.

**Attack 2 — the frozen collision predicate cannot distinguish a *same-document* collision from a
*different-document* one, and it makes the preregistered adoption unsatisfiable.** The step is
`comm -12` over id sets. Staged ids are S109..S242 contiguous (E1). Therefore **every** lane id in
115..242 is a "collision" the moment it is adopted, even though the row it collides with is a
different document. Measured: the FIX arm adopts the three rows correctly re-pointed by document,
and the frozen step's output **grows** from 6 to 9 (E6) — S115/S116/S117 now "collide" with staged
S115 = mv(1), S116 = rename(2), S117 = statx(2), i.e. with the lane's *own* S111/S110/S114
documents at other numbers. Under the frozen kill rule — its C3 text ends "collides, lands nothing and
the round reports the refusal" — the
preregistered S115/S116/S117 adoption is forbidden by the counter; under `sources-census.sh
validate` it is clean of E03 (E5 FIX arm). The two instruments disagree, and the census one is
right. The collision receipt is only meaningful as a **pre-append** control on the specific staged
rows being adopted (which is what the C3 control paragraph actually asks for), never as an
emptiness acceptance gate — the round-22 M16 record's "is empty: reg 108 ids, staged 134 ids, 0
collisions" was true only while the lane max sat at S108, and became false the instant its own fix
map landed. A document-level (URL-set) intersection is the predicate that would survive adoption;
the id-set one cannot.

**Attack 3 — `used-by` is not covered by the re-pointing rule, and it silently rots.**
`SOURCES.append.md:10-11` cite `count-objects-garbage-semantics-r23.md` while round 23 adopts
`-r24.md`. The preregistration's re-pointing sentence covers citations by id ("Citation
re-pointing is BY DOCUMENT"); it says nothing about the `used-by` column, which is a *path* citation
and drifts independently of the id. Receipts: E5 FIX arm E11 lines, and Finding 5's FIX2 arm
showing the column must point at the two entries that will actually exist.
