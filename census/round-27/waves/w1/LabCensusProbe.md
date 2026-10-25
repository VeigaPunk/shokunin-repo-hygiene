# LabCensusProbe — round-27 C2 census/collision probe

## Status

STATUS: PASS — manual registry-row grep and `sources-census.sh validate` agree (132→135) on a scratch append mirror; `validate` exits 0 with W04 warning-only (35 W04, 0 E findings); the 0-3-space indented-collision guard produces a nonempty `collisions` file on the synthetic fixture, while a column-zero-only control misses the indented row (false clean).

## Evidence

Scratch: `/var/tmp/souji-r27-LabCensusProbe/` (lane copy extracted from `git -C <lane> archive e78ac7c4837b81b634db4a927605a751a7f006ba`; the two admitted knowledge entries placed at `corpus/knowledge/origin-record-writer-r27.md` (w1 draft bytes) and `corpus/knowledge/origin-record-mechanism-set-r33.md` (merge-package bytes); three normalized fleet-schema rows S152/S210/S211 inserted inside the `## Registry` section just before `## Paths`).

1. Manual row grep (frozen C2 counter command) — before/after:
   - `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `132` (HEAD mirror) → `135` (after append).
2. `bash scripts/sources-census.sh validate <scratch-lane>` → rc `0`, final line `souji-shokunin	ok	/var/tmp/souji-r27-LabCensusProbe/souji-shokunin/corpus/SOURCES.md`; 35 W04 lines incl. the new `souji-shokunin	W04	S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes` (S152/S210 share a URL, distinct scopes); 0 E findings. W04 stays warning-only (exit 0).
3. `bash scripts/sources-census.sh census <scratch-lane>` → `souji-shokunin	rows	135`; `FLEET	rows	135`; malformed NF=13 check → `0`; duplicate-id check → empty; mined used-by missing-path check → empty. Census rows (135) == manual grep (135).
4. Baseline: same validate on a non-appended HEAD mirror → rc `0`, rows `132`.
5. Real-registry × this round's staged subset: `comm -12` of HEAD registry ids (132, frozen 0-3-space pattern) vs {S152,S210,S211} → collisions file empty (E03 clear).
6. Collision-guard proof (synthetic fixture, pasted verbatim):

```
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' reg.md | grep -oE 'S[0-9]+' | sort -u > reg-ids
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' staged.md | grep -oE 'S[0-9]+' | sort -u > staged-ids
$ comm -12 reg-ids staged-ids > collisions
$ cat reg-ids
S001
S210          <- indented "  | S210 |" row was seen by the frozen pattern
$ cat staged-ids
S210
$ cat collisions
S210
$ wc -l < collisions
1             <- NONEMPTY, as required
$ # control: column-zero-only pattern
$ grep -oE '^\|[[:space:]]*S[0-9]{3,}' reg.md | grep -oE 'S[0-9]+' | sort -u > reg-ids-cz
$ comm -12 reg-ids-cz staged-ids-cz | wc -l
0             <- false clean: the indented row is invisible
```

Source quote (read this run, `scripts/sources-census.sh:40`): `Maintained parser accepts 0–3 leading ASCII spaces before Markdown rows/headings;`

## Findings

1. Manual grep and validator agree at every stage: 132 before, 135 after; validator census rows = 135 (identical); malformed/dup/missing checks all clean — the append of S152/S210/S211 keeps the registry well-formed (no E01/E03/E11).
2. W04 is warning-only: `validate` rc 0 with 35 W04 lines and 0 E lines; the appended S152/S210 pair contributes exactly one new W04 (S210, same URL across scopes), which does not flip status (matches the script's documented exit contract, `scripts/sources-census.sh:16-18`).
3. The frozen 0-3-space guard is load-bearing: it sees the indented `  | S210 |` row; the column-zero-only alternative misses it and would false-green a real collision. The real HEAD registry × {S152,S210,S211} produces an empty `collisions` set, so appending the three rows cannot trip E03.
4. Normalization is mandatory before append: the campaign rows in `SOURCES.append.md` are campaign-schema (escaped `\|` cells, prose recheck cells with backslash line-continuations; S210 splits to NF=12). The probe used a fleet-schema normalization satisfying the ExecRowsNormalize contract (11 columns, recheck `365d`, opened `2026-10-25`, status `mined`, used-by exactly the two admitted entries, no `|` in cells).

## Attack log

Not an attack item; no counter was attacked or proposed for change. Observation for L1 (not a counter defect): the three staged rows must be normalized (finding 4) before the C2 append; appending `SOURCES.append.md` rows as-is would fail the lane's own census.
