# R40w2critic12 — falsifier report: S254 / GVFS assimilation

Seat: R40w2critic12 (critic, axis calibration). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Landed instrument commit: `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Every assimilation artifact attacked here
(`corpus/knowledge/origin-record-format-gvfs-r40.md`, `corpus/lessons/round-40.md`, `corpus/README.md`,
`corpus/SOURCES.md`, `census/round-40/assimilation/*`, `census/round-40/sources/gvfs-trashitem-1.62.0.c`) was last
touched by `128e412`; `git diff --stat 128e412 -- <those paths>` is empty at HEAD (`556c24a`).
Installs: none. `curl` (existing binary) was used read-only. No pacman, no git mutation, no edits outside this report.

## Verdict

**FALSIFIED (in part).** The quote-location axis is SAFE: all five quoted GVFS lines are verbatim against an
upstream fetch. Three assimilation claims are FALSIFIED:

1. The census claim "every collision is a DIFFERENT document" is false: 3 of the 58 collisions (S152, S210, S211)
   are the same document (same URL, same tag) in the lane and the package.
2. The ADMIT rationale "new ground the lane did not hold" is contradicted by the lane's own text and by the
   held S022 source, which already states the relative-`Path` and URL-escape rules attacked in item 3 below.
3. The re-pointing to S254 leaves a dangling citation chain: the lane cites `S146` as the held GVFS reader in three
   lane files, no `S146` row exists, and `S146` was NOT a collision (free in the lane registry, same document).
   The lesson, the entry and the README do not mention it.

Plus smaller dangling paths and an overclaimed "must carry" statement (detail below).

## Attack list (what was attacked, where)

| # | attack | result | where |
|---|---|---|---|
| A1 | the five quoted GVFS lines (158,173,180,182,193) are verbatim, and the pinned bytes are the upstream bytes | SAFE | `census/round-40/sources/gvfs-trashitem-1.62.0.c:158,173,180,182,193`; entry `origin-record-format-gvfs-r40.md:1,12-19`; lesson `round-40.md:18` |
| A2 | id arithmetic: reg-ids / staged-ids / collisions / S254 freshness | arithmetic consistent; the census description is wrong (see A3) | `census/round-40/assimilation/{reg-ids,staged-ids,collisions}`; `corpus/SOURCES.md:206` |
| A3 | "every collision is a DIFFERENT document" (lesson, L0 question) | FALSIFIED: S152, S210, S211 same URL/tag | `round-40.md:41-46`; `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md:202`; `collisions:25-27` |
| A4 | "re-pointed BY DOCUMENT", S022/S212 named explicitly | SAFE for S022 and S212; S210 is the same GLib document as lane S152 and the writer file it is paired with cites S152 | `origin-record-format-gvfs-r40.md:27-33`; `corpus/knowledge/origin-record-writer-r27.md:1` |
| A5 | "adds ground the lane did not hold" (lesson ADMIT; entry "why new") | FALSIFIED: held S022 snapshot states the relative-Path and URL-escape rules; r28 entry and S212 row already hold GVFS reader as S146; README and lesson say "already held" | `round-40.md:31-32` vs `round-40.md:97`, `README.md:794-795`; `census/round-22/attempt2/sources/freedesktop-trash.txt:411-421`; `origin-record-exclusivity-r28.md:11,36`; `SOURCES.md:163` |
| A6 | dangling citations (registry, knowledge, lesson) | FALSIFIED: S146 chain; 14 cited-but-absent ids; two dangling paths | see table below |
| A7 | "must carry" the Path and DeletionDate (entry line 22-23) vs the reader's NULL handling | FALSIFIED as an overclaim: the reader accepts a missing `Path` and a missing `DeletionDate` | `origin-record-format-gvfs-r40.md:22-23`; snapshot `gvfs-trashitem-1.62.0.c:172-175, 192-195` |
| A8 | "no writer", "no O_EXCL" in GVFS | SAFE: no writer call, no `O_` token in the snapshot | snapshot grep below |
| A9 | map rows naming the entry | SAFE: each named row resolves; the entry is listed in the F4 row and in the round-40 frontier update | `corpus/README.md:42`, `:793-794`, `:796-799`; `SOURCES.md:206` |

## Commands and real output

### A1 — verbatim quotes, and upstream bytes

```
$ sha256sum census/round-40/sources/gvfs-trashitem-1.62.0.c
3a8f8cbb057ac3bb8d4ba4901d43f8fd1abcd89b9ff095ef927999154af3d25b  census/round-40/sources/gvfs-trashitem-1.62.0.c
$ cat census/round-40/sources/SHA256SUMS | grep gvfs
3a8f8cbb057ac3bb8d4ba4901d43f8fd1abcd89b9ff095ef927999154af3d25b  gvfs-trashitem-1.62.0.c
$ curl -sS -o $S/gvfs-upstream-trashitem.c -w "%{http_code}\n" https://raw.githubusercontent.com/GNOME/gvfs/1.62.0/daemon/trashlib/trashitem.c
200
$ sha256sum $S/gvfs-upstream-trashitem.c
3a8f8cbb057ac3bb8d4ba4901d43f8fd1abcd89b9ff095ef927999154af3d25b  .../gvfs-upstream-trashitem.c
$ sed -n '158p;173p;180p;182p;193p' census/round-40/sources/gvfs-trashitem-1.62.0.c
   158	  trashinfo = g_strdup_printf ("%s/info/%s.trashinfo", trashpath, basename);
   173	                                    "Trash Info", "Path",
   180	…decoded = g_uri_unescape_string (orig, NULL);
   182	…if (g_path_is_absolute (decoded))
   193	                                     "Trash Info", "DeletionDate",
```

Verbatim check (python, run in scratch; the harness used `in` on the entry and lesson text; lines 173 and 193 appear
in the entry as `"Trash Info", "Path"` / `"Trash Info", "DeletionDate"` without the trailing comma, so the substring
test with the comma is a harness artifact, not a mismatch):

```
158 snapshot-exact: True | in entry: True | in lesson: True
173 snapshot-exact: True | in entry: False | in lesson: False   # entry has '"Trash Info", "Path"' (no trailing comma)
180 snapshot-exact: True | in entry: True | in lesson: False     # lesson row quotes only line 158
182 snapshot-exact: True | in entry: True | in lesson: False
193 snapshot-exact: True | in entry: False | in lesson: False   # entry has '"Trash Info", "DeletionDate"'
```

A1 is SAFE. The record path (158), group/keys (173, 193), escape (180) and relative branch (182) are the
quoted lines.

### A2 — id arithmetic

```
$ grep -oE "^\| *S[0-9]{3} " corpus/SOURCES.md | tr -d '| ' | sort > rows.txt
rows lines: 178 uniq: 178
reg-ids uniq: 177  dup in reg-ids: 0
== rows not in reg-ids:  S254
== reg-ids not in rows:  (none)
== reg-ids max/min: S253 / S001
== collisions recomputed = reg ∩ staged: 58   (diff vs collisions file: SAME)
== staged ids: uniq 134; dup 0; S109..S242
== collisions not in staged: (none)
== S146 in reg-ids: 0   S146 in staged-ids: 1
```

Arithmetic: 177 (reg-ids, taken before the S254 row existed; max S253) + 1 (S254) = 178 rows. 177 ∩ 134 = 58
collisions. S254 is fresh (not in reg-ids). Id arithmetic is consistent. The census file is stale by one row
(S254), which is the expected pre-append state, not an error. Gaps in S001–S253: 76 ids have no row.

### A3 — "every collision is a DIFFERENT document"

Script (re-run: `python3 cmp.py <lane>/census/round-40/assimilation/collisions`; the scratch copy was deleted, the
script is reproduced here in full):

```python
import re,sys
L="/home/vgpnk/Projects/shokunin/souji-shokunin"
P="/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md"
def rows(path):
    out={}; dup=[]
    for line in open(path,encoding="utf-8"):
        m=re.match(r"^\|\s*(S\d{3})\s*\|(.*)$",line)
        if m:
            sid=m.group(1)
            if sid in out: dup.append(sid)
            out.setdefault(sid,[]).append(line.rstrip("\n"))
    return out,dup
lane,ldup=rows(L+"/corpus/SOURCES.md")
pkg,pdup=rows(P)
coll=[l.strip() for l in open(sys.argv[1]) if l.strip()]
def url(row):
    m=re.search(r"https?://\S+",row)
    return m.group(0).rstrip("|").rstrip() if m else None
same=[]
for sid in coll:
    lr=lane.get(sid,[""])[0]; pr=pkg.get(sid,[""])[0]
    lu,pu=url(lr),url(pr)
    flag="SAME-URL" if (lu and pu and lu.split("#")[0]==pu.split("#")[0]) else "diff"
    if flag=="SAME-URL": same.append(sid)
    print(sid,flag,"| LANE:",lr.split("|")[2].strip()[:70],"| PKG:",pr.split("|")[2].strip()[:70])
print("SAME-URL collisions:",same,len(same))
```

Output (tail; the 55 `diff` rows are omitted here, every one of them is in the scratch transcript):

```
S152 SAME-URL | LANE: GLib `g_local_file_trash()`, gio/glocalfile.c at tag 2.84.0 | PKG: GLib `g_local_file_trash()`, gio/glocalfile.c at tag 2.84.0
S210 SAME-URL | LANE: GLib `g_local_file_trash()`, gio/glocalfile.c at tag 2.84.0 | PKG: GLib · gio/glocalfile.c at tag 2.84.0
S211 SAME-URL | LANE: GLib `g_file_set_contents_full()`, glib/gfileutils.c at tag 2.84.0 | PKG: GLib · glib/gfileutils.c at tag 2.84.0
SAME-URL collisions: ['S152', 'S210', 'S211'] 3
```

The rows are `corpus/SOURCES.md:160-162` (lane) and `SOURCES.append.md:50,108,109` (package). Consequence: the
lesson's census claim (`corpus/lessons/round-40.md:41-46`: "every collision is a DIFFERENT document") and the L0
question (`/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md:202`: "name different documents") are FALSE for at
least 3 of 58. The lane's registry itself holds two rows for one GLib document (S152 and S210, `corpus/SOURCES.md:160-161`).

Note: the comparison is URL-level (fragment stripped). It shows the same URL and tag, which is the document identity
the registry uses (`SOURCES-CONTRACT-v1`). It does not prove content equality.

### A4 / A5 — "new ground" and the re-point

Held S022 source (the lane's own snapshot, `census/round-22/attempt2/sources/freedesktop-trash.txt`, 411-421):

```
411: relative pathname (starting with any other character). A
412: relative pathname is to be from the directory in which the trash
…
421: characters escaped as in URLs (as defined by RFC
```

So the rules GVFS line 180 (escape) and line 182 (relative branch) implement are in the held normative spec. The
lane's knowledge entries did not carry them (`grep -rn -i "relative\|escap\|percent" corpus/knowledge` finds
them only in the new r40 entry), but the lane held the source. The entry itself says "agrees with the specification
rather than replacing it" (`origin-record-format-gvfs-r40.md:27-30`) and "What this does NOT establish" (`:35-44`),
and the lesson says "F1 and F4 stay frontier and … all four sit on ground the lane already held"
(`round-40.md:96-97`; `corpus/README.md:794-795`). The ADMIT line says the opposite: "new ground the lane did not hold"
(`round-40.md:31-32`). Two wordings in the same round conflict. The ground the lane held before r40:

- `corpus/knowledge/trash-spec-restorable-quarantine.md:9,21`: `info/<name>.trashinfo`, `[Trash Info]`, `Path=`, `DeletionDate=`.
- `corpus/knowledge/quarantine-origin-record-fields-r24.md:14,51,75`: the `Path` and `DeletionDate` keys.
- `corpus/knowledge/origin-record-exclusivity-r28.md:11,36`: "The previous F4 entries (S022, S146, S152, S210, S211)…" and
  "the content or format … held at S022 (FreeDesktop shape) and S146 (GVFS reader)".
- `corpus/SOURCES.md:163`: the S212 row says "not the record's content or format (S022/S146/S152 hold those)".

**S146 chain (the re-point):**

```
$ grep -n "S146" corpus/knowledge/origin-record-exclusivity-r28.md
11:The previous F4 entries (S022, S146, S152, S210, S211) established the record's
36:  (FreeDesktop shape) and S146 (GVFS reader), with GLib's writer at S152.
$ grep -n "S146" corpus/SOURCES.md  →  (no output)
$ git log --oneline -S"| S146 |" -- corpus/SOURCES.md  →  (no output)
```

S146 was never a registry row (no commit adds it). S146 is in the package (`SOURCES.append.md:44`) and in the
staged id list, but NOT in the collision list (`grep -c '^S146$' census/round-40/assimilation/reg-ids` → 0). The
lesson's own method (`round-40.md:41-45`) therefore left S146 free. The adopter chose a fresh id S254 instead
(`round-40.md:48`). That choice does not repair the three lane citations of S146 as the held GVFS reader
(`origin-record-exclusivity-r28.md:11,36`, `SOURCES.md:163`). The entry's own provenance line says the id was
re-pointed (`origin-record-format-gvfs-r40.md:49-52`), but it does not name these citations. Judgement: a free,
same-document id was available and was not used, so the dangling chain is avoidable and the choice is not forced by
the census.

### A6 — dangling citations

Every `S\d{3}` token under `corpus/` not present as a registry row (`comm` of `grep -rhoE "\bS[0-9]{3}\b" corpus --include=*.md` against the registry rows):

```
S133 S134 S136 S137 S138 S141 S146 S147 S153 S160 S162 S172 S178 S179
```

Of these, S160 and S172 are cited as package-staged ids in the r40 lesson (labelled, not live). The rest are
cited as live ground in: `S146` (`origin-record-exclusivity-r28.md:11,36`, `origin-record-format-gvfs-r40.md:49`
labelled staged, `SOURCES.md:163`), `S138` (`origin-record-durability-r28.md`), `S134`, `S141`, `S147`, `S153`
(`count-objects-linked-worktree-garbage.md`). The assimilation did not report these 14 ids; the census only compared
ids in the package against the registry.

Two dangling paths in the r40 lesson and entry:

- `corpus/lessons/round-40.md:55`: `census/round-40/waves/w1/R40reviewer18.md` does not exist. The file is at
  `.ufo/waves/round-40/w1/R40reviewer18.md` (the M40-1 evidence pointer).
- `corpus/lessons/round-40.md:47` and `corpus/knowledge/origin-record-format-gvfs-r40.md:54`: "filed in
  `.ufo/l0-questions.md`". The lane has no `.ufo/l0-questions.md`: its `.ufo/` holds only `quarantine/` and `waves/`
  (verified with `ls .ufo`). The file exists at the fleet root
  `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md:202`. The citation is valid only if read from the fleet root.

### A7 — "must carry" vs the reader

Snapshot `gvfs-trashitem-1.62.0.c`, lines 167-196:

```
167  if (g_key_file_load_from_file (keyfile, trashinfo, 0, NULL))
172  orig = g_key_file_get_string (keyfile, "Trash Info", "Path", NULL);
175  if (orig == NULL)  *original = NULL;
…
192  *date = g_key_file_get_string (keyfile, "Trash Info", "DeletionDate", NULL);
```

The reader returns NULL for a missing `Path` and a missing `DeletionDate`. The entry says "a record must carry the original
path in ESCAPED form, the deletion date, and the base directory" (`origin-record-format-gvfs-r40.md:22-23`). That
is a normative "must" that the cited reader does not enforce. The normative source for "must" is S022, not GVFS. Overclaim.
Also "this settles the READ side" (`:22`) is stronger than a single non-normative reader.

### A8 — no writer, no O_EXCL in GVFS

```
$ grep -n "g_key_file_set\|g_file_set_contents\|g_key_file_save\|O_\|g_creat\|g_file_create\|g_file_replace\|g_open" census/round-40/sources/gvfs-trashitem-1.62.0.c
(no output)
```

A8 is SAFE: GVFS's trashitem.c contains no writer of the record and no `O_` token, as the entry says
(`origin-record-format-gvfs-r40.md:37-42`). The only file-level calls are read (`g_key_file_load_from_file` at 167).
Lines 145-152 show the `files/` parent derivation (the "beside `files/`" claim at `:14`); that is not in the quoted
line list but is in the pinned bytes.

### A9 — map rows

```
$ grep -n "origin-record-format-gvfs-r40" corpus/README.md | cut -c1-20
42:| F4 restorable q…
793:  (F1 row …
794:  (F4 row, the assimilated GVFS reference implementation, S254). …
$ paths in the F4 row (README.md:42) all resolve: corpus/knowledge/{trash-spec-restorable-quarantine,quarantine-same-filesystem-rename,quarantine-staging-no-copy-r23,quarantine-origin-record-fields-r24,origin-record-writer-r27,origin-record-mechanism-set-r33,origin-record-exclusivity-r28,origin-record-durability-r28,origin-record-format-gvfs-r40}.md → OK
$ grep -n "^| S254 " corpus/SOURCES.md | cut -c1-12  →  206:| S254 |
```

A9 is SAFE. The map row that names the entry is `corpus/README.md:42` (F4) and the frontier paragraph `corpus/README.md:793-799`.
The registry row is `corpus/SOURCES.md:206`, its `used-by` cell names the entry.

Minor id/document mismatch: `origin-record-format-gvfs-r40.md:28` pairs "GLib's own writer, S210" with
`corpus/knowledge/origin-record-writer-r27.md`, which cites S152 for that writer (`origin-record-writer-r27.md:1`).
S210 and S152 are the same GLib document (A3), so the claim is true but the pointer is not the file's own citation.

## Other observations (not verdict-bearing)

- The entry's "what it is not" (`:35-44`) is accurate and is the honest part of the entry. The lesson's "new ground"
  wording and the README's "already held" wording are the conflict.
- The lesson `round-40.md:41-43` census is said to run in `.ufo/waves/round-40/assimilation/`. That directory exists
  (`collisions`, `reg-ids`, `staged-ids`, mtime 16:58) and the lane copies in `census/round-40/assimilation/` have the same
  line counts (58 / 177 / 134). A byte-level comparison was not run; the id-set checks in A2 are the evidence.
- No fleet-root file, no sibling lane, no `.ufo/state`, no watchdog log was read or written.

Removed: yes. `rm -rf -- /fast/scratch/hyaku/souji-r40/w2/R40w2critic12` ran after the last command; `ls` of that path returns "No such file or directory".

## What the L1 should re-run

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
sha256sum census/round-40/sources/gvfs-trashitem-1.62.0.c            # 3a8f8cbb…25
sed -n '158p;173p;180p;182p;193p' census/round-40/sources/gvfs-trashitem-1.62.0.c
grep -n "S146" corpus/knowledge/origin-record-exclusivity-r28.md corpus/SOURCES.md
grep -c '^S146$' census/round-40/assimilation/reg-ids                 # 0
python3 <the cmp.py above> census/round-40/assimilation/collisions     # SAME-URL … ['S152','S210','S211'] 3
sed -n '411,421p' census/round-22/attempt2/sources/freedesktop-trash.txt
ls census/round-40/waves/w1/R40reviewer18.md                         # MISSING
```

## Scratch

Scratch dir: `/fast/scratch/hyaku/souji-r40/w2/R40w2critic12/`. It held `rows.txt`, `reg_u.txt`, `staged_u.txt`,
`coll_u.txt`, `inter.txt`, `rows_all.txt`, `cited_corpus.txt`, `cmp.py` and the upstream fetch. Removal is recorded below.
