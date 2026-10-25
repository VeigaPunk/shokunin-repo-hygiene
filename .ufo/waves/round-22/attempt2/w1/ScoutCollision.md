STATUS: PASS

All three steps executed read-only in `/var/tmp` scratch. One measured result
contradicts the ticket's stated expectation and is reported as measured rather
than massaged: the **verbatim** registry-vs-staged collision count is **6, not 0**.
Zero is reachable only after an id map is applied, and both candidate maps are
quantified below.

Evidence: `.ufo/waves/round-22/attempt2/w1/evidence/ScoutCollision.txt`
(full transcript). No registry edit, no git/jj write, no cleanup run.

---

## 1. The two id lists and the real collision

Frozen extraction pattern, verbatim:

```
PAT='^ {0,3}\|[[:space:]]*S[0-9]{3,}'
grep -oE "$PAT" <file> | grep -oE 'S[0-9]{3,}' | sort -u
```

| side | file | count | range |
|---|---|---|---|
| registry | `corpus/SOURCES.md` | **114** | S001..S114, contiguous |
| staged | `shokuknow/merge/souji/SOURCES.append.md` | **134** | S109..S242, contiguous |

Registry contiguity proved with `diff` against a generated `S001..S114` list →
`CONTIGUOUS S001..S114: no gaps`.

```
$ comm -12 reg.raw app.raw > collisions
COLLISIONS count: 6
S109 S110 S111 S112 S113 S114
```

**Collision count for the real pair = 6.**

This is a *numbering* collision, not a content collision — the same id window
carries two unrelated themes:

| id | registry row (line) | staged row (line) |
|---|---|---|
| S109 | 129 — round-2 RENAME_NOREPLACE probe, vendored | 7 — git-fetch(1) |
| S110 | 130 — rename(2), man-pages 6.19 | 8 — builtin/fetch.c, merge.c, rebase.c, am.c, commit.c |
| S111 | 131 — mv(1), GNU coreutils | 9 — builtin/pull.c |
| S112 | 132 — gio(1), GIO commandline tool | 10 — git-count-objects(1) |
| S113 | 133 — GLib GIO `g_file_trash()` | 11 — git-fsck(1) |
| S114 | 134 — statx(2), man-pages 6.19 | 12 — git-prune(1) |

So a verbatim append of `SOURCES.append.md` would mint six duplicate ids for
unrelated rows. **The precondition fails for the verbatim pair**, and the
ticket's "must be 0" is the post-map figure, not the raw one.

## 2. Guard proof — the 0-3-space pattern is load-bearing

Scratch registry carrying an **indented** colliding row, scratch staged file
carrying the same id:

```
registry.md:
| S001 | scratch row one | ...
  | S002 | scratch INDENTED row two (two leading spaces) | ...     <-- 2 spaces
| S003 | scratch row three | ...
staged.md:
| S002 | staged row colliding on S002 | ...
| S004 | staged row with a fresh id | ...
```

```
$ grep -n 'S002' registry.md
2:  | S002 | scratch INDENTED row two (two leading spaces) | ...
```

| pattern | registry side extracts | `comm -12` result | count |
|---|---|---|---|
| `^ {0,3}\|…` (frozen) | S001 **S002** S003 | **S002** | **1 — NONEMPTY** |
| `^\|…` (column-zero only) | S001 S003 | *(empty)* | **0 — MISS** |

**Guard PASS.** On identical bytes the frozen pattern reports the collision and
the column-zero-only pattern returns a false clean — precisely the defect the
0-3-space allowance exists to prevent.

Live-file scope note: neither real file currently has an indented row
(`grep -cE '^ +\|'` → `0` for both), so the allowance is precautionary for
today's bytes, not a defence currently in use.

## 3. Rows the two adopted entries cite, and the campaign→lane map

Actual citation lists (`grep -oE '\bS[0-9]{3}\b' | sort -u`):

- `corpus/knowledge/quarantine-staging-no-copy-r23.md` → **S109 S110 S111 S123**
- `corpus/knowledge/quarantine-origin-record-fields-r24.md` → **S022 S112 S113 S114**

Resolved by source identity rather than by number, the campaign rows behind
them are:

| campaign | lane | source |
|---|---|---|
| S115 | **S111** | `man7.org/…/mv.1.html` |
| S116 | **S110** | `man7.org/…/rename.2.html` |
| S117 | **S114** | `man7.org/…/statx.2.html` |
| S124 | **S109** | `lanes/souji/round2/evidence/noreplace_probe.py` (own-work) |
| S126 | **S113** | `docs.gtk.org/gio/method.File.trash.html` |
| S137 | **S112** | `man.archlinux.org/man/gio.1.en` |
| — | S022 | FreeDesktop Trash spec, already in registry |

**All six adopted sources already exist in the lane registry at S109..S114.**
The adopted theme needs **zero new registry rows**.

Lane's next free id: **S115** (contiguous S001..S114, no gaps).

**Map A — uniform offset, `lane = campaign + 6`** (offset `115 − 109`):

```
campaign S109..S242  ->  lane S115..S248   (134 ids)
MAPPED_COLLISION_COUNT = 0
six cited rows: S115→S121, S116→S122, S117→S123, S124→S130, S126→S132, S137→S143
```

Collision-free by construction (mapped min 115 > registry max 114) — but it
gives the lane a **second row for each of the six sources**, duplicating
S111/S110/S114/S109/S113/S112.

**Map B — identity map** (what the entry text already does):

```
S115→S111, S116→S110, S117→S114, S124→S109, S126→S113, S137→S112, S022→S022
collisions added = 0, duplicate source rows = 0
```

**Recommendation: Map B for the adopted theme** (six sources, zero new rows,
zero collisions), holding Map A's +6 arithmetic only for campaign rows the lane
has *not* yet assimilated. Map A applied wholesale duplicates six
already-assimilated sources.

## 4. Bounded findings

**Executed (observed from command output):**

- F1. Verbatim collision count = 6, ids S109..S114.
- F2. The collision is a numbering collision across two unrelated themes.
- F3. All six cited sources are already at lane S109..S114; no new row needed.
- F4. Map A → 0 collisions over the full 134-row block, range S115..S248, at
  the cost of six duplicate sources.
- F5. Guard discriminates: frozen 1, column-zero-only 0, same bytes.
- F6. Neither real file has an indented row today (0 each).
- F7. `S123` is cited only in the r23 entry's REJECT line and exists in no
  registry row (corpus max id S114). Reported as a citation observation only —
  this lane does not edit entries.

**Not claimed / unresolved:** which map the appending seat adopts (both
quantified; Map B recommended). No row created, moved, renumbered or deleted.

**Tooling:** none installed or updated — only `grep`/`awk`/`sort`/`comm`/`sed`/
`diff`/`mktemp`. No package transaction run.
