# ScoutKnowledgeDrafts — round 27 wave 1

## Status
STATUS: PASS — both proposed knowledge entries read in full (merge/knowledge/corpus/knowledge/origin-record-writer-r27.md, origin-record-mechanism-set-r33.md); PROVINCE F4 fit confirmed; QUALITY Q1–Q59 clause-by-clause re-grounding list produced; every quote re-located this run against fresh GLib tag 2.84.0 bytes (glocalfile.c 83391 B, gfileutils.c 86909 B, fetched 2026-10-25). Key log: verbatim copies of the staged entries do NOT satisfy the frozen C1/C2 counters without (a) Gate sections, (b) registry-row re-shaping, (c) amendment-note pointer rewriting (see Findings 4, 6, 7).

## Evidence
- `curl -fsSL https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c` → 83391 bytes, sha256 `66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f`
- `curl -fsSL https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c` → 86909 bytes, sha256 `5161ae435ee57448c280323de064e1d6d62dc1ba3ba2771c5982b913888dfad5`
- `python3 -B tools/souji-landing-gate.py --root <sim> --rev <sim tip> --round 27 --fleet-root /home/vgpnk/Projects/shokunin` → `SUMMARY findings=2` (only the two frozen C1 base findings) AFTER applying the fixes in Findings 4/6/7 to a sim copy; with the verbatim staged entries findings rose to 4 (2 new LG-DANGLING-PTR).
- `python3 -B tools/souji-gate-check.py --root <sim> --round-date 2026-10-25 --entries corpus/knowledge/origin-record-writer-r27.md corpus/knowledge/origin-record-mechanism-set-r33.md --snapshot-dir census/round-27/sources` → `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0` (rc 0) once rows S152/S210/S211 were registered and Gate sections supplied.
- `python3 -B tests/fixtures/r23-locator-heading.py --entries <both> --snapshot-dir census/round-27/sources` → `entries=2 locators=0 locators_bad=0` (rc 0) — Gate uses line-style locators, not `§` tokens.
- `bash scripts/sources-census.sh validate --file <sim>/corpus/SOURCES.md --today 2026-10-25` → 0 E-codes for rows S152/S210/S211 once rows were re-shaped to 13 fields, bare `365d` recheck, and `opened` 2026-10-25 (baseline lane validate rc 0, `souji ok`).

## Findings

1. **Both staged entries are the raw campaign files; neither contains a `## Gate` section.** The frozen C2 counter requires `gate entries=2 ok=2 fail=0` via `tools/souji-gate-check.py`, whose `check1-no-gate` fails both as staged (`FAIL ... check1-no-gate`). Each admitted entry needs a `## Gate` block with `url:`, `snapshot:` (inside `--snapshot-dir`), `opened: 2026-10-25`, ≥1 ADMIT and ≥1 REJECT row each carrying `reason:` and a ≤25-word verbatim quote present in the snapshot. My candidate Gates (Evidence above) reproduce exactly `entries=2 ok=2 fail=0`.
   Location: merge/souji/knowledge/corpus/knowledge/origin-record-writer-r27.md, origin-record-mechanism-set-r33.md (no `## Gate`), and preregistration C2 ("each entry carries a `## Gate` section").

2. **Campaign `opened` dates prove nothing.** Staged front matter (`opened 2026-10-23/24`, `verified-at: 2026-10-23/24`) are campaign dates; the prereg requires re-grounding this round with our own access date. Re-grounding must set `opened: 2026-10-25` and `verified-at: 2026-10-25` in both entries and in the appended SOURCES rows (also satisfies validator E08).
   Location: both staged entries' front matter; `SOURCES.append.md` rows S152/S210/S211 (opened cells).

3. **All quotes re-locate correctly at tag 2.84.0 (checked against fresh bytes):**
   - glocalfile.c:2261 `fd = g_open (infofile, O_CREAT | O_EXCL | O_CLOEXEC, 0666);` ✓; :2256 `trashname = get_unique_filename (basename, i++);` ✓; :2340 `original_name_escaped = g_uri_escape_string (original_name, "/", FALSE);` ✓; :2354–2355 `data = g_strdup_printf ("[Trash Info]\nPath=%s\nDeletionDate=%s\n", ...)` ✓; :2359–2361 `g_file_set_contents_full (infofile, data, -1, G_FILE_SET_CONTENTS_CONSISTENT | G_FILE_SET_CONTENTS_ONLY_EXISTING, 0600, error)` ✓; :2383 `if (g_rename (local->filename, trashfile) == -1)` ✓; unlink sites :2288, :2363, :2387 ✓.
   - gfileutils.c:1366 `tmp_filename = g_strdup_printf ("%s.XXXXXX", filename);` ✓; :1369 `fd = g_mkstemp_full (tmp_filename, O_RDWR | O_BINARY | O_CLOEXEC, mode);` ✓; :1696–1697 `return get_tmp_file (tmpl, wrap_g_open,` / `flags | O_CREAT | O_EXCL, mode);` ✓; :1041 `if (g_rename (old_name, new_name) == -1)` ✓; :1107–1117 ONLY_EXISTING handling in `fd_should_be_fsynced` ✓; header glib/gfileutils.h:91–94 ("Only apply consistency and durability guarantees if the file already exists.") ✓.
   - Anchor drifts to correct when re-grounding: `SOURCES.append.md` S210 anchor cites the g_close at "2282" but the close is at 2281 (`(void) g_close (fd, NULL);`); S211 anchor cites the XXXXXX template at "1367" but it is at 1366. S152's anchor list is exact.
   Location: `SOURCES.append.md` rows S210/S211 anchor cells.

4. **Verbatim admission breaks C1's counter (findings=0 at the landing tip).** The staged amendment notes cite `corpus/knowledge/origin-record-format-gvfs-r26.md` and `corpus/knowledge/origin-record-exclusivity-r28.md`, which do not exist in the lane tree. The landing gate scans `corpus/knowledge/*.md` (depth 2) and would add 2 LG-DANGLING-PTR findings (sim: findings 2→4). Fix (verified in sim): rewrite the cross-references to the campaign package form used by the admitted `quarantine-origin-record-fields-r24.md` — e.g. "the campaign's round-5 entry (package file `merge/souji/knowledge/corpus/knowledge/origin-record-format-gvfs-r26.md`, not adopted in this lane, so it has no lane path)". With this, the landing gate returns findings=2 (only the two frozen C1 rows). Do NOT add pointer-exemptions rows for these; C1's mechanism is exactly two rows.
   Location: origin-record-writer-r27.md final note (cites gvfs-r26.md); origin-record-mechanism-set-r33.md final note (cites exclusivity-r28.md).

5. **Registry rows S152/S210/S211 must be re-shaped, not copied.** The merge rows carry literal `|` inside cells (e.g. `O_CREAT\|O_EXCL`, `curl ... | grep ...`) which awk field-splitting counts as extra separators: NF=15/14/16, not 13 → validator E01 malformed row; additionally the S210/S211 recheck cell contains prose+pipe → the used-by cell shifts (E11 noise/path corruption) and the recheck cell would fail E09. Lane house style: 11 columns (13 fields), no pipes in cells, and a bare cadence (`365d`) in the recheck cell. I verified a corrected 13-field form passes `validate --file` with 0 E-codes for the three new rows. Also keep `status=mined`, `opened=2026-10-25`, and `used-by` exactly the two admitted entries (S152 → origin-record-writer-r27.md; S210/S211 → origin-record-mechanism-set-r33.md).
   Location: `SOURCES.append.md` rows S152/S210/S211 (verbatim copies fail E01/E09/E11).

6. **p-collision proof must scope to the three appended rows.** The merge `SOURCES.append.md` contains 134 rows with ids S109–S242; ids S109–S132 overlap the lane's existing ids with different content (e.g. merge S109 is git-fetch(1) vs lane S109 RENAME_NOREPLACE probe) → a wholesale import gives 24 duplicate-id collisions (E03). The appended set {S152, S210, S211} is disjoint from the lane's S001–S132 (verified: grep finds none), so the collision set for the three rows is empty; document that proof rather than importing the merge file.
   Location: `SOURCES.append.md` id list vs lane `corpus/SOURCES.md` id list.

7. **Q56 requires the README coverage map to name both entries in the F4 row, same commit.** Both entries declare `ground: F4`; `corpus/README.md` line 42 F4 row (ground cell starts with "F4") must add backticked `knowledge/origin-record-writer-r27.md` and `knowledge/origin-record-mechanism-set-r33.md` to its entries column in the same commit the entries land. Counter `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l` is 2 today → 4 after.
   Location: `corpus/README.md:42`.

8. **Q54 (locator-heading) is satisfied only with line-style locators.** Gate rows must name `snapshot:` paths (gate-check check4). If the Gate used `§ NAME` locators, the r23-locator-heading fixture would flag them: I verified GLib C sources yield 0 heading-like lines under the fixture's heuristics (`glocalfile.c headings: 0`, `gfileutils.c headings: 0`), so any `§ X` → LOCATOR-BAD. Use `— line 2261 —`/`— line 1696 —` style locators (matches gate-check's LOCATOR_RE; zero `§` tokens → fixture passes). Verified: `locators=0 locators_bad=0`.
   Location: `tests/fixtures/r23-locator-heading.py`; candidate Gates in Evidence.

9. **PROVINCE fit = F4, frontier, no authority claim.** PROVINCE.md F4 row is "restorable quarantine and file-system semantics — trash layout, same-device rename vs copy+remove"; README F4 row already names "per-item origin records (trashinfo-style)" as F4's next step. Both entries ground F4 and add no staging/delete authority; keep F4 as frontier (a Core move needs a SKILL rule, not just an entry). Both entries' "What this does NOT establish" sections correctly avoid claiming souji must adopt GLib's format.
   Location: PROVINCE.md F4 row; README.md F4 row (lines 42, 49).

10. **Q17/Q55: snapshot files must be committed under `census/round-27/sources/`.** The Gate `snapshot:` paths and the entries' `recheck:` must resolve to committed regular non-symlink files at the landing revision (Q17), and the registry rows' opened/byte counts should be accompanied by the committed snapshots (house style: SHA256SUMS like round-26). Current `census/round-27/sources/` is empty; the two GLib byte copies (with the sha256s above) must be committed there, and recheck lines should say `re-open census/round-27/sources/{glocalfile,gfileutils}.c` rather than a live curl (Q4 self-contained / /var/tmp spirit; the staged recheck lines are network curls).
    Location: `census/round-27/sources/` (empty); staged entries' recheck lines.

## Attack log
None — this seat is the knowledge-drafts scout. The findings above are re-grounding requirements, not counter changes. All frozen counters (C1 findings=0, C2 registry rows 132→135 / grounded F4 2→4 / gate entries=2 ok=2 / sources-census rc 0, C3) remain unchanged and reachable (sim-verified for C1/C2 as described).

## Full text of the two proposed entries
Copied verbatim from the read-only source (with literal `|` retained in code spans; this is a mandated full-text copy, not a ≤25-word claim quote):

### Entry 1 — corpus/knowledge/origin-record-writer-r27.md
```
source: S152 — https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c — tag 2.84.0, `gio/glocalfile.c:2261`, `:2256`, `:2340`, `:2354`, `:2359`, `:2383`, `:2288`/`:2363`/`:2387` — opened 2026-10-23
verified-at: 2026-10-23 — GLib tag 2.84.0; the file was opened and the quoted lines read
recheck: 365d — re-fetch `gio/glocalfile.c` at tag 2.84.0; the normative format remains the FreeDesktop trash specification (the lane's existing row S022)
ground: F4 — restorable quarantine (who WRITES a per-item origin record, and with what guarantees)

# GLib writes the record, and its writer's guarantees are exactly the ones a receipt needs

## Claim (F4, sourced at a pinned revision)
The round-5 ledger asked "who **writes** a per-item origin record?" and
established that GVFS contains no writer at all. The writer is in **GLib** —
the library that owns `g_file_trash()` — and its code states the guarantees
explicitly.

1. **The record is created exclusively, never overwritten.**
   `fd = g_open (infofile, O_CREAT | O_EXCL | O_CLOEXEC, 0666);` — the `O_EXCL`
   flag makes an existing `.trashinfo` a failure rather than an overwrite, and
   the surrounding loop retries with a **new unique name** (`get_unique_filename`)
   when the name collides, incrementing until it succeeds. So a trash operation
   can never clobber a previous item's record.
2. **The record's content is fixed and the path is escaped.**
   `original_name_escaped = g_uri_escape_string (original_name, "/", FALSE);`
   and then `data = g_strdup_printf ("[Trash Info]\nPath=%s\nDeletionDate=%s\n", …)`.
   This is the writer side of the shape the round-5 entry (S146) read on the
   GVFS side: the group is `Trash Info`, the keys are `Path` and
   `DeletionDate`, and `Path` is **URI-escaped** (with `/` left unescaped, so
   the path stays readable and remains absolute-or-relative-to-the-topdir).
3. **The record is written BEFORE the payload moves.**
   The content is written with `g_file_set_contents_full(infofile, data, -1, …,
   0600, error)` and only afterwards does the payload move:
   `if (g_rename (local->filename, trashfile) == -1)`. So at every instant the
   on-disk state is one of "no record, no move" or "record, then move" — never
   "moved without a record".
4. **Every failure path removes the record it just created.** The three
   `g_unlink (infofile);` sites — after a failed content write, after a failed
   rename, and in the error return — mean a **half-made trash entry cannot be
   left behind**: if the payload cannot be moved, the record is deleted, and if
   the record cannot be written, the payload is never touched.

## What this does NOT establish
- **This is GLib's implementation, not the specification.** The normative
  format remains the FreeDesktop trash specification (the lane's S022); this
  row is the implementation that shows how the guarantees are realised, and it
  agrees with the specification rather than replacing it.
- **The `DeletionDate` format is not stated here.** The value is produced by
  `g_date_time_format (now, "%Y-%m-%dT%H:%M:%S")` in the same function, but the
  row's quotes are limited to the three lines above; the format string is
  available in the same file.
- **The writer is not a souji tool.** Nothing here says a souji receipt must
  reuse GLib's format — only that a *reference* implementation exists whose
  ordering and rollback a souji design can be measured against.

## Amendment note
This entry **adds** the write side to the lane's existing
`corpus/knowledge/trash-spec-restorable-quarantine.md` (the specification) and
to round 5's `corpus/knowledge/origin-record-format-gvfs-r26.md` (the record's
shape, read on the GVFS side). It replaces neither, and it answers the
round-5 ledger's "who writes one" with a named implementation.
```

### Entry 2 — corpus/knowledge/origin-record-mechanism-set-r33.md
```
source: S210 — https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c — git tag 2.84.0; 83 391 bytes — opened 2026-10-24
source: S211 — https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c — git tag 2.84.0; 86 909 bytes — opened 2026-10-24
verified-at: 2026-10-24 — the product's own source at a pinned tag; both files read at the quoted lines
recheck: 365d — `curl -fsSL 'https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c' | grep -F 'flags | O_CREAT | O_EXCL, mode);'` (ran 2026-10-24)
ground: F4 — restorable quarantine (whether a per-item origin record needs `O_EXCL` uniqueness, its rollback, or a different scheme)

# The three mechanisms are complementary, and GLib uses all three

## Claim (F4, sourced at a pinned revision)

Round 7 closed the origin-record question at the POSIX level: uniqueness from
`O_EXCL`, visibility from `rename()`, durability bounded by the platform. The
residual question was which of the three candidate mechanisms a souji record
*needs*. GLib's own implementation answers it, and the answer is that the
candidates are **not a menu**.

**The exclusive create is a name reservation, not the write.** GLib's local
trash writer creates the `.trashinfo` file with `O_CREAT` and `O_EXCL`, and
then **closes the descriptor without writing through it** (S210). The content
is put in place afterwards, by *path*, with
`g_file_set_contents_full (infofile, data, -1, …)` under the flags
`G_FILE_SET_CONTENTS_CONSISTENT | G_FILE_SET_CONTENTS_ONLY_EXISTING`. The
rollback is the `g_unlink (infofile)` that removes the reservation when the
payload's `g_rename` fails.

**GLib's `O_EXCL` belongs to the temporary file.** In the content writer
itself, `g_file_set_contents_full` creates a uniquely named temporary file
(`%s.XXXXXX`) with `g_mkstemp_full`, which passes `O_CREAT` and `O_EXCL`,
writes the content into it, and publishes the result with a single
`g_rename (old_name, new_name)` (S211). Exclusivity of the *destination* is a
separate concern, and it is the `G_FILE_SET_CONTENTS_ONLY_EXISTING` flag that
enforces it: the write fails rather than create a target that does not exist.

So the three candidates divide the labour rather than compete:

| mechanism | what it actually buys in GLib |
|---|---|
| `O_EXCL` | a **name** — the temp file's uniqueness in the content writer, a reservation in the trash writer |
| the rollback | removal of that **reservation** when the payload never arrives — a cleanup, not a substitute for exclusivity |
| temp + `rename` | **atomic publication** of the content |

**The consequence for a souji record.** A writer that wants both "never
overwrite" and "never half-write" needs both mechanisms, and — the part that
matters for a receipt — **"the record file exists" is not the same as "the
record's content is final"**: between the exclusive create and the content
write the record exists and is empty. And the record-and-payload pair is still
not atomic *as a pair*: what GLib bounds is the window between the reservation
and the content write, not the window between the record and the payload.

## What this does NOT establish

- **This is GLib's implementation, not a specification.** The normative
  format remains the FreeDesktop trash specification (the lane's S022). The
  two round-6/round-7 files are untouched.
- It does not establish that a souji receipt should reuse GLib's format, only
  that a reference implementation exists whose ordering a souji design can be
  measured against.
- It does not close the **durability** half of the residual question. The
  trash writer's call uses `CONSISTENT` and `ONLY_EXISTING`, not `DURABLE`:
  the record's content is not fsync'd by this path, so the platform's
  crash-safety bound stands as the lane already recorded it.
- It does not establish anything about GVFS, which the lane has already shown
  contains no writer at all.

## Amendment note

A dated addition to the staged round-6 entry
`corpus/knowledge/origin-record-writer-r27.md` (S152), which recorded GLib's
writer's create / content / ordering / rollback sequence, and to the round-7
entry `corpus/knowledge/origin-record-exclusivity-r28.md`, which argued at
the POSIX level that the record needs `O_EXCL` and `rename` rather than
rollback. This entry **sharpens both**: it shows that the writer's exclusive
descriptor is closed unused, that the content write is by path under an
explicit "only existing" flag, and that GLib's own `O_EXCL` belongs to the
temporary file — so the three mechanisms are complementary rather than
alternatives. Both earlier files are untouched.
```
