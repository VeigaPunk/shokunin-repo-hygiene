# CritC2Coverage — evidence trail

Read-only. No writes outside this file and the sibling report. No tool installed;
no pacman transaction; no git/jj write; no service action.

Base: `4edb25dfe262515d0da63224bbba71e02e36cba5`. Measured HEAD when noted:
`3216c1998fe04d7e23793ffd4e135bd37c3a11f4`.

## E1 — F4's existing entries already name both halves of the theme

`grep -n 'RENAME_NOREPLACE\|no-copy\|info file\|Path\|MUST NEVER\|not overwrite' corpus/knowledge/trash-spec-restorable-quarantine.md corpus/knowledge/quarantine-same-filesystem-rename.md`

```
trash-spec-restorable-quarantine.md:10: info file created FIRST, atomically (O_EXCL)
trash-spec-restorable-quarantine.md:19: §6 "each subsequent trashing must not overwrite a previous copy"
trash-spec-restorable-quarantine.md:20: §6 "A filename in the $trash/files directory MUST NEVER be used
                                        to recover the original filename; use the info file …"
trash-spec-restorable-quarantine.md:21: §6 "The key "Path" contains the original location"
trash-spec-restorable-quarantine.md:32: souji-quarantine.sh writes no per-item info record; origin encoded
                                        in the staged path (what §6 says MUST NEVER be relied on)
trash-spec-restorable-quarantine.md:35: adopting a trashinfo-style record is a tool/format change:
                                        OPERATOR DECISION
quarantine-same-filesystem-rename.md:8:  mv first tries renameat2(…, RENAME_NOREPLACE); cross-device copies
                                         then unlinks
quarantine-same-filesystem-rename.md:10: `mv --no-copy` turns the cross-device case into a hard failure
                                         (exit 1, source untouched): a fail-closed guard for staging
quarantine-same-filesystem-rename.md:28: renameat2(AT_FDCWD, "$D/a/f", AT_FDCWD, "$D/b/f", RENAME_NOREPLACE) = 0
```

Status of those two files (coverage map + r13 correction in `corpus/README.md`):

```
| F4 restorable quarantine, file-system semantics | frontier, entries held |
  knowledge/trash-spec-restorable-quarantine.md, knowledge/quarantine-same-filesystem-rename.md |
```
```
The r12 coverage-map word "held" meant entries were held in the corpus, not the later HELD
rejection status: … F4's trash-spec entry [is] admitted. Only K5
`quarantine-same-filesystem-rename.md` is HELD.
```

Frontier row (`corpus/README.md:46`):
```
- F4 restorable quarantine — next: per-item origin records (trashinfo-style) and `mv --no-copy`
  staging are tool changes for the operator.
```

## E2 — the staged package and the adopted deltas

`diff -u /home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/<file> corpus/knowledge/<file>`

- staged `quarantine-staging-no-copy-r23.md` → adopted `-r23.md`: same claim and same
  five-device probe; `verified-at: 2026-10-23` + `recheck: re-run …/noreplace_probe.py`
  become `2026-10-25` + `recheck: re-open …/{man7-rename.2,man7-mv.1}.txt`; the body adds
  "vendored, not this lane's execution"; ids S124/S116/S115 → S109/S110/S111.
- staged `quarantine-origin-record-fields-r24.md` → adopted `-r24.md`: title nearly verbatim
  ("…because that is what restore **uses**" → "**consumes**"); ids S137/S126/S117 → S112/S113/S114;
  S022 cited instead of appended. The staged text already says "The write-side contract and the
  layout are already held (S126, S022)".
- lane `recheck: 180d — re-open census/round-22/attempt2/sources/{arch-gio.1,gtk-filetrash,
  freedesktop-trash,man7-statx.2}.txt` — all four resolve:
```
arch-gio.1.txt 12626   gtk-filetrash.txt 4904   freedesktop-trash.txt 25138   man7-statx.2.txt 19343
```

Package's own admission caveat (`MERGE-REPORT.md`, "Rows whose source the lane's registry already holds"):
```
A page often supports several distinct claims, so this is not automatically a duplicate — but it is
where a lane ends up with two rows about one document. The operator should check that the staged row
adds an aspect the held row does not already carry.
```
Package `Dangling citations` table lists `quarantine-origin-record-fields-r23.md | S022 | round2`
and `…-r24.md | S022 | round3` — S022 is the lane's own existing row, not missing.

## E3 — Q3 province

`PROVINCE.md:3-4` and `:7-8`:
```
**Domain:** fleet repository & workspace hygiene (掃除) — receipt-gated removal of stale, duplicate,
and already-preserved artifacts.
## Owns
- The fleet root repo's hygiene surfaces: stray checkpoint/scratch files, superseded config
  snapshots, quarantine staging.
```
F4 restorable quarantine is a declared frontier row in the same file.

## E4 — Q4 census rule, executed

Rule source (`scripts/sources-census.sh:25,33`):
```
E04 duplicate URL+scope (no supersedes)
W04 same URL across scopes (warnings do not affect clean lanes)
```
Implementation (`:644-649`):
```
if (u!="" && (u in url_seen) && !(scope_key in url_scopes))
  printf "%s\tW04\t%s duplicate url %s across scopes\n",lane,id,u
if (u!="" && (scope_key in url_scopes) && status!="rejected" &&
    url_scope_nonrejected[scope_key] && teaches !~ /supersedes S[0-9]{3}/)
  printf "%s\tE04\t%s duplicate url %s within scope %s\n",lane,id,u,scope
```
`url_of()` strips the fragment and trailing slash and lowercases host only; `scope_key = u SUBSEP scope`.

Executed:
`bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
```
… 30 W04 rows (S035 S036 S038 S049 S057 S058 S059 S063 S065 S072 S073 S075 S076 S077
   S086 S087 S088 S089 S090 S091 S092 S093 S094 S095 S096 S097 S098 S099 S106 S108) …
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
exit=0
```
Row counts: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `114`;
`… S022 …` → `1`. S022 `used-by` cell = `corpus/knowledge/trash-spec-restorable-quarantine.md` only.

The census reads only `corpus/SOURCES.md` (`sources-census.sh:2,7`); knowledge files are never parsed,
so an S022 citation inside an entry cannot produce E04/W04.

## E5 — executed landing-gate delta (blocking finding F1)

```
python3 tools/souji-landing-gate.py --root . --round 22 --rev 4edb25dfe262515d0da63224bbba71e02e36cba5
→ findings=4  exit=1
python3 tools/souji-landing-gate.py --root . --round 22 --rev 3216c1998fe04d7e23793ffd4e135bd37c3a11f4
→ LG-DANGLING-PTR  corpus/knowledge/quarantine-origin-record-fields-r23.md
                   corpus/knowledge/quarantine-origin-record-fields-r24.md:47 cites path absent at 3216c1998fe0
  findings=5  exit=1
```
The four base findings are pre-existing (README:217 fleet paths, jj entry:148, round-22 spot-check:32).
The fifth is introduced by the adopted r24 entry.

`corpus/pointer-exemptions.tsv` has 4 rows; none names that path.
`git ls-tree -r --name-only HEAD corpus/knowledge/ | grep -E 'quarantine|trash'`:
```
corpus/knowledge/quarantine-staging-no-copy-r23.md
corpus/knowledge/quarantine-origin-record-fields-r24.md
corpus/knowledge/quarantine-same-filesystem-rename.md
corpus/knowledge/trash-spec-restorable-quarantine.md
```
Extraction executed with the gate's own function:
```
m._pointer_paths("  The dedicated r23 entry `corpus/knowledge/quarantine-origin-record-fields-r23.md`",
                 "corpus/knowledge/quarantine-origin-record-fields-r24.md")
→ ['corpus/knowledge/quarantine-origin-record-fields-r23.md']
```
Gate scan set (`check_pointers`) includes every `corpus/knowledge/*.md`, so the entry's own bytes
are scanned once committed.

## E6 — committed r23 Gate locator is wrong (finding F2)

Snapshot `census/round-22/attempt2/sources/man7-mv.1.txt`:
```
29: NAME | SYNOPSIS | DESCRIPTION | AUTHOR | REPORTING BUGS | COPYRIGHT | SEE ALSO | COLOPHON
60: DESCRIPTION         top
91:  do not copy if renaming fails
```
No `OPTIONS` heading exists. Committed entry (HEAD) says:
`- ADMIT: "do not copy if renaming fails" — § OPTIONS --no-copy — snapshot: …man7-mv.1.txt`
Working tree (uncommitted) fixes it:
```
git diff corpus/knowledge/quarantine-staging-no-copy-r23.md
-  "do not copy if renaming fails" (S111, § OPTIONS `--no-copy`). …
+  "do not copy if renaming fails" (S111, § DESCRIPTION, option `--no-copy` — the page has no OPTIONS heading). …
- ADMIT: "do not copy if renaming fails" — § OPTIONS --no-copy — snapshot: …
+ ADMIT: "do not copy if renaming fails" — § DESCRIPTION, option --no-copy — snapshot: …
```

## E7 — C2's frozen counter passes (context, not a coverage proof)

```
python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
  --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
            corpus/knowledge/quarantine-origin-record-fields-r24.md \
  --snapshot-dir census/round-22/attempt2/sources \
  --slice census/round-22/attempt2/quarantine-slice \
  --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
exit=0
```
Slice rows: S114 S118 S123 S124 S126 S131 S133 S138 (8). Verdict classes present:
accepted×5, present×1, refused×1, unverifiable×1 — inside the frozen enum.

## E8 — id-space note

`slice-verdicts.tsv` keys are campaign ids; the lane registry now also holds S109–S114 for
different documents (lane S114 = statx(2); campaign S114 = the git-prune row whose verdict is
"accepted … git-repack[1]"). Mapping is only in `corpus/lessons/round-22.md` M16
(`S124→S109, S116→S110, S115→S111, S137→S112, S126→S113, S117→S114`), not in the TSV.
