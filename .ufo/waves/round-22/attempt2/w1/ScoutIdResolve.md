STATUS: PASS

# ScoutIdResolve — every cited source id in the two adopted entries resolves to exactly one lane registry row

Assigned question: after the campaign→lane reassignment, do all `source:` ids the
two adopted entries cite resolve to exactly one row of `corpus/SOURCES.md`, and does
each id follow its **document** (not arithmetic)? Read-only; no repo writes beyond this
report and `evidence/ScoutIdResolve.tsv`.

## Inputs actually used

1. `find /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2 -name 'DraftEntry*'`
   → **no output**: `DraftEntryNoCopy.md` / `DraftEntryOrigin.md` do not exist.
2. Therefore the adopted entries were taken at their committed lane paths, which are
   already the in-round re-grounded versions (not the staged copies):
   - `corpus/knowledge/quarantine-staging-no-copy-r23.md`
   - `corpus/knowledge/quarantine-origin-record-fields-r24.md`
   Both `git cat-file -e 4edb25d:<path>` → **absent at base**, `git log` →
   introduced by `a211e4d round-22: declared-evidence audit tool, assimilation entries and gate checker`.
3. Staged originals read-only from `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/`
   (same two filenames) to recover the campaign ids and documents being remapped.
4. Campaign side of the map read at `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/SOURCES-PROPOSED.md`
   and `round3/SOURCES-PROPOSED.md`.

## Executed evidence

### E1 — lane id space before/after the reassignment

```
$ git show 4edb25d:corpus/SOURCES.md | grep -o '^| S[0-9]\{3,\}' | sed 's/^| //' | sort | tail -2
S107
S108
$ grep -o '^| S[0-9]\{3,\}' corpus/SOURCES.md | sed 's/^| //' | sort | tail -2
S113
S114
$ git show --stat --oneline a211e4d -- corpus/SOURCES.md
a211e4d round-22: declared-evidence audit tool, assimilation entries and gate checker
 corpus/SOURCES.md | 6 ++++++
 1 file changed, 6 insertions(+)
```

Base max = S108 ⇒ next free S109 (matches the preregistration), and the append added
**exactly six rows** (S109–S114), lines 129–134. There is no separate append-block file
in the lane (`find . -name '*append*'` → nothing): the "proposed append block" was applied
directly into `corpus/SOURCES.md`, so that file is the only thing to check.

### E2 — each mapped id occurs exactly once as a row id

```
$ for id in S022 S109 S110 S111 S112 S113 S114 S115 S116 S117 S124 S126 S137; do ...; done
S022 rows=1
S109 rows=1
S110 rows=1
S111 rows=1
S112 rows=1
S113 rows=1
S114 rows=1
S115 rows=0
S116 rows=0
S117 rows=0
S124 rows=0
S126 rows=0
S137 rows=0
```

Every **lane** id cited resolves to one row; every **campaign** id cited is absent from the
lane registry (correct: they were remapped, not carried). Whole-file duplicate-id census
(`awk` counting every `^| S…` id cell) printed **no duplicates**.

### E3 — campaign id → document → lane id (the map), and uniqueness on the campaign side

```
$ for id in S115 S116 S117 S124 S126 S137; do grep -rn "^| $id " lanes/souji/ | wc -l; done
S115  mv(1), GNU coreutils — https://man7.org/linux/man-pages/man1/mv.1.html            occurrences=1
S116  rename(2), renameat2(2) — Linux man-pages 6.19 — …/man2/rename.2.html             occurrences=1
S117  statx(2) — Linux man-pages 6.19 — …/man2/statx.2.html                             occurrences=1
S124  souji round-2 probe noreplace_probe.py — lanes/souji/round2/evidence/noreplace_probe.py  occurrences=1
S126  GLib GIO, g_file_trash() method reference — https://docs.gtk.org/gio/method.File.trash.html  occurrences=1
S137  gio(1) — GIO commandline tool (glib2 2.90.1) — https://man.archlinux.org/man/gio.1.en    occurrences=1
```

### E4 — document-follows-id equality (entry citation vs registry row)

```
quarantine-staging-no-copy-r23.md  S109  expected=lanes/souji/round2/evidence/noreplace_probe.py  row_url=None   match=True
quarantine-staging-no-copy-r23.md  S110  expected=https://man7.org/linux/man-pages/man2/rename.2.html  match=True
quarantine-staging-no-copy-r23.md  S111  expected=https://man7.org/linux/man-pages/man1/mv.1.html      match=True
quarantine-origin-record-fields-r24.md  S112  expected=https://man.archlinux.org/man/gio.1.en         match=True
quarantine-origin-record-fields-r24.md  S113  expected=https://docs.gtk.org/gio/method.File.trash.html match=True
quarantine-origin-record-fields-r24.md  S114  expected=https://man7.org/linux/man-pages/man2/statx.2.html match=True
quarantine-origin-record-fields-r24.md  S022  expected=https://specifications.freedesktop.org/trash/latest/ match=True
frontmatter_ids= ['S109','S110','S111'] / ['S112','S113','S114','S022']
```

**No case where the id and the document disagree.** Every remap was made from the document:
`S124→S109` (probe bytes), `S116→S110` (rename(2)), `S115→S111` (mv(1)), `S137→S112`
(gio(1)), `S126→S113` (GIO File.trash), `S117→S114` (statx(2)); `S022` was already the lane
row for the same FreeDesktop Trash spec URL and was **cited, not duplicated**.

The probe id was also checked at byte level, because S109 is the one `own-work` document:

```
$ sha256sum census/round-22/attempt2/sources/vendor-noreplace-probe.out
1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5
$ grep -o 'sha256 1634d206[0-9a-f]*' corpus/knowledge/quarantine-staging-no-copy-r23.md
sha256 1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5
```

### E5 — registry conformance of the adopted rows

```
$ bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
souji  W04  S035 duplicate url … (29 pre-existing W04 rows, none for S109–S114)
souji  ok   /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
exit=0
```

No E-code at all (so no E02 malformed id, E03 duplicate id, E04 duplicate URL+scope), and
no W04 for any of S109–S114: the six new rows are distinct documents at distinct ids.

### E6 — body citations and placeholders

`grep -n 'S[0-9]{3}'` over both entries: body citations are only S110/S111 (no-copy line 20,
24, 45, 55) and S022/S112/S113/S114 (origin lines 12, 14, 21, 23, 29, 33, 45, 49) — all of
them already-resolved ids. **No placeholder id exists** (`SXX`, `S…`, `S<digits>`): the only
ellipsis in either file is inside the abbreviated digest `1634d206…8bb5`, which is a digest,
not an id.

## Verdict table

| entry | cited id | document | mapped lane id | status |
|---|---|---|---|---|
| quarantine-staging-no-copy-r23.md | S109 (campaign S124) | `lanes/souji/round2/evidence/noreplace_probe.py`; vendored bytes `census/round-22/attempt2/sources/vendor-noreplace-probe.out` | S109 (line 129) | resolved, exactly one row, digest matches sha256sum |
| quarantine-staging-no-copy-r23.md | S110 (campaign S116) | https://man7.org/linux/man-pages/man2/rename.2.html | S110 (line 130) | resolved, exactly one row, URL identical |
| quarantine-staging-no-copy-r23.md | S111 (campaign S115) | https://man7.org/linux/man-pages/man1/mv.1.html | S111 (line 131) | resolved, exactly one row, URL identical |
| quarantine-origin-record-fields-r24.md | S112 (campaign S137) | https://man.archlinux.org/man/gio.1.en | S112 (line 132) | resolved, exactly one row, URL identical |
| quarantine-origin-record-fields-r24.md | S113 (campaign S126) | https://docs.gtk.org/gio/method.File.trash.html | S113 (line 133) | resolved, exactly one row, URL identical |
| quarantine-origin-record-fields-r24.md | S114 (campaign S117) | https://man7.org/linux/man-pages/man2/statx.2.html | S114 (line 134) | resolved, exactly one row, URL identical |
| quarantine-origin-record-fields-r24.md | S022 (already a lane id) | https://specifications.freedesktop.org/trash/latest/ | S022 (line 42) | resolved, exactly one row, reused not duplicated |
| quarantine-staging-no-copy-r23.md | `campaign-S123` (Gate REJECT token) | campaign row S123 — `lanes/souji/round2/fixtures/r23-trigger-prune.sh` | none | not a lane citation: explicitly prefixed; lane S123 has zero rows today |

Same table, machine-readable: `evidence/ScoutIdResolve.tsv`.

## Findings (bounded)

**F1 — the campaign numbering collides with the lane's future id space (observed, medium).**
Campaign ids already occupy S115–S242 (`merge/souji/SOURCES.append.md`, and
`census/round-22/attempt2/assimilation/staged-ids` lists S109–S242). The lane's next free id
after this adoption is **S115** — numerically campaign S115 (`mv(1)`). From here on, a
campaign id copied into a lane entry *without* remapping may silently resolve to a
lane row that holds a different document. Today the only campaign token in the entries is
`campaign-S123` (no-copy line 69), which carries the prefix and therefore cannot be read as
a lane id; lane S123 has no row. Nothing in the registry or gate-check enforces that prefix
(`tools/souji-gate-check.py:39` only scans `^source:\s*S\d{3,}` at line start), so the
convention is the only protection. Verdict: no current defect, but the map must stay
document-driven and campaign ids must keep the `campaign-` prefix.

**F2 — an adopted entry points at a sibling that does not exist in the lane (observed, low,
outside the id-resolution predicate).** `corpus/knowledge/quarantine-origin-record-fields-r24.md:47`
says "The dedicated r23 entry `corpus/knowledge/quarantine-origin-record-fields-r23.md` is
**not replaced** by this one". That path is absent:

```
$ ls corpus/knowledge/quarantine-origin-record-fields-r23.md
ls: cannot access 'corpus/knowledge/quarantine-origin-record-fields-r23.md': No such file or directory
```

The staged package did carry such a file; the lane adopted only the r24 successor, so the
"not replaced" sentence now points at nothing. All *source ids* in the entry still resolve,
so the preregistered check-5 predicate is unaffected; this is a document pointer inside the
prose, not an id.

**F3 — no separate append block exists (observed, informational).** `find` for
`*append*` under the lane returns nothing; the six adopted rows are committed in
`corpus/SOURCES.md` at lines 129–134 by `a211e4d`. The check in step 2 of the assignment was
therefore performed against the committed registry, and the append block itself cannot drift
from it.

**F4 — campaign S022 is not in the campaign's proposed/append files (observed, low).**
`grep 'S022'` over `/home/vgpnk/Projects/shokuknow/lanes/souji/*.md` finds only prose
mentions (CANNOT-ANSWER.md, DOMAIN.md, REJECTIONS.md), not a registry row, and
`merge/souji/SOURCES.append.md` has no S022 row. The staged entry describes S022 as
"already in this registry" — i.e. the lane's row — and the lane S022 row's URL is exactly
the URL the staged entry cites. So no id drift; recorded because it means the campaign map
for S022 is inherited (same lineage, opened 2026-10-19 round 12), not re-derived.

**F5 — the rows' `used-by` cells agree with the adoption (observed, positive).** Each new
row names exactly the entry that cites it: S109/S110/S111 → `quarantine-staging-no-copy-r23.md`;
S112/S113/S114 → `quarantine-origin-record-fields-r24.md`. The validator's E11 (used-by path
missing on disk) did not fire, so the two-way link is real on disk.

## Not checked / remaining unknowns

- The promotion of the campaign's `SOURCES-PROPOSED.md` rows into the campaign's own final
  registry was not audited (the campaign repo is read-only here and its final registry is not
  at `lanes/souji/SOURCES.md`; only `SOURCES-PROPOSED.md` per round plus
  `merge/souji/SOURCES.append.md` exist in this checkout). The campaign documents above were
  read from those two artifacts, not from a single campaign registry.
- Whether `campaign-S123` should remain in the Gate at all is a curation decision, not a
  resolution defect; it is reported, not judged.
- Nothing here re-derives C2's gate predicate (snapshot quotes, ADMIT/REJECT counts); only
  the source-id limb (predicate check 5) and the registry conformance behind it were measured.

## Hygiene

Read-only against the lane repo and `/home/vgpnk/Projects/shokuknow`. Writes: this report and
`evidence/ScoutIdResolve.tsv` only. No git/jj writes, no commits, no tool installs or
upgrades, no mutating cleanup, no process signals.
