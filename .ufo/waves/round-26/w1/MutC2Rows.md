# MutC2Rows — mutation test of the C2 append block

## Status
STATUS: PASS — probe ran to completion on a /var/tmp mirror of the lane base (127 rows, S001–S127) with the five staged rows (S109/S110/S111/S123/S131) appended verbatim inside the Registry section; verdicts below; scratch removed. No kill of the C2 contract: the raw staged bytes are NOT appendable as-is (4 id collisions, 5 recheck-schema violations, 1 missing used-by path), which is exactly what the frozen C2 normalization rules (preregistration.txt:91-101) mandate the lane fix before appending.

## Evidence

Mirror: `/var/tmp/souji-r26-MutC2Rows/lane/` (full lane tree copy; `corpus/SOURCES.md` rebuilt as base 127 rows + the five staged rows extracted with `awk 'NR==7||NR==8||NR==9||NR==21||NR==29' /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`). Pristine sha256 `1d019001d1cb1af6…` (verified before, between, and after mutations; final restore verified `132` rows).

### Staged-row shape (raw bytes, lines 7/8/9/21/29 of SOURCES.append.md)

```
LINE 7 pipes=12  LINE 8 pipes=12  LINE 9 pipes=12  LINE 21 pipes=12  LINE 29 pipes=12
```

- `NF=13` on all five (11 cells + 2 boundary pipes).
- No literal or escaped `|` inside any cell (12 pipes = 13 fields exactly).
- Recheck cells, verbatim: `on-release — host `git --version` is 2.56.0` (S109); `on-release — re-grep call sites at the next host git tag` (S110); `on-release — re-read builtin/pull.c at the next host git tag` (S111); `90d — re-run `bash fixtures/r23-trigger-prune.sh` (expect 7 PASS and exit 0)` (S123); `90d — re-run the read-only census (expect 5 registrations, 0 prunable)` (S131).
- Used-by cells: S109/S110/S111 name `corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`; S123 names `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`; S131 names `corpus/knowledge/count-objects-garbage-semantics-r23.md`.

### Frozen manual census (CORPUS.md:135-147), run in mirror

```
rows=132
malformed=0
dup S109
dup S110
dup S111
dup S123
(enum/tier-inflation: no output)
missing: corpus/knowledge/count-objects-garbage-semantics-r23.md
```

### Maintained CLI (`scripts/sources-census.sh validate --file`, the frozen K3 tool)

```
file E03 S109 duplicate id
file E09 S109 recheck=on-release — host `git --version` is 2.56.0
file E03 S110 duplicate id
file E09 S110 recheck=on-release — re-grep call sites at the next host git tag
file E03 S111 duplicate id
file E09 S111 recheck=on-release — re-read builtin/pull.c at the next host git tag
file E03 S123 duplicate id
file E09 S123 recheck=90d — re-run `bash fixtures/r23-trigger-prune.sh` (expect 7 PASS and exit 0)
file E09 S131 recheck=90d — re-run the read-only census (expect 5 registrations, 0 prunable)
file E11 S131 missing used-by corpus/knowledge/count-objects-garbage-semantics-r23.md
exit=1
```

E09 predicate: `sources-census.sh:663-666` — recheck must be `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, `^[0-9]+d$`, or symbolic cadence; `on-release — …` and `90d — …` fail both arms.

### Mutation M1 — indent staged S109 by 2 spaces

```
rows=131   (was 132)
dup S110 / dup S111 / dup S123   (S109 vanishes from the dup list)
```

Maintained CLI (same run): still reports `E03 S109 duplicate id` and `E09 S109 recheck=…` — the indented row is still parsed (0–3 leading spaces accepted, `sources-census.sh:40`; CORPUS.md:150-155). Manual row/dup/malformed counts silently drop the row; the maintained tool still sees and flags it.

### Mutation M2 — append row S200 with used-by `corpus/knowledge/not-admitted.md`

Manual missing-path loop prints `missing: corpus/knowledge/not-admitted.md`; maintained CLI prints `E11 S200 missing used-by corpus/knowledge/not-admitted.md`. Both fire.

## Findings

1. **All five staged rows are malformed by recheck-cell schema (E09).** Every staged recheck cell carries prose after the cadence (`on-release — …`, `90d — …`). The lane's renumber map (`.ufo/waves/round-26/w1/renumber-map.md:79`) already plans the fix ("cadence kept, trailing prose moved out of the cell"), so no contract kill — but as-appended-verbatim the maintained validator fails 5× E09.
2. **Staged S131's used-by names a path absent from the lane.** `corpus/knowledge/count-objects-garbage-semantics-r23.md` does not exist in `corpus/knowledge/` (verified by `grep`/mirror `[ -e ]`); maintained E11 fires. Renumber map F4 (renumber-map.md:81) records this and rewrites the cell. S109/S110/S111/S123 used-by paths all exist in the lane.
3. **4/5 staged id collisions (E03).** S109/S110/S111/S123 collide with base registry ids (both manual uniq -d and maintained E03); S131 is unique at base. Matches the frozen S109→S128/…→S132 mapping (preregistration.txt:94).
4. **Census indentation divergence (coverage finding).** The frozen manual census (CORPUS.md:135-147) is column-zero-only — a row indented 1–3 spaces is invisible to it (rows 132→131; its duplicate check silently loses S109). The maintained parser accepts 0–3 leading spaces and still flags it. Any future append that lands with leading spaces would produce a manual/automated count mismatch; the manual commands are also the ones used by the standing census section.
5. **Enum/tier checks pass.** kind ∈ {docs, code, own-work}, tier ∈ {A}, status=mined all valid; no community/tier-inflation. No literal or escaped `|` in any staged row.

## Attack log
None. The staged package's defects are all anticipated by the frozen C2 normalization rules and renumber map; no counter is gameable and no predicate change is proposed.

## Handoff
Main agent should re-run `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` at tip after the normalized append (K3) and confirm E03/E09/E11 are all gone; the manual census rows/dup/malformed commands must print 132/empty/0.
