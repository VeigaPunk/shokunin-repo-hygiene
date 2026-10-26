# Id-collision guard — proof and run (souji round 29, C3 assimilation)

STATUS: PASS — guard proven on the required indented fixture (2-space and 3-space rows collide, 4-space row does not, column-zero-only pattern false-greens to an empty `collisions`), then run over the real registry and package. Real result: 31 collisions, registry max id **S215**, adopted rows renumber **S117→S216, S118→S217, S122→S218, S136→S219** reproduced by document (URL + anchor), never by arithmetic; the census's own E03 detector independently confirms exactly S117/S118/S122 of the four.

Contract basis, read before any command:
- `.ufo/waves/round-29/records/preregistration.txt` (frozen; C3 names the two entries, rows S216–S219, and "SOURCES rows 139 -> 143").
- `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md:470-491` — addendum item 10, "Id collision check in scratch, before any append", and its guard commands. Lines 485-488 state the proof obligation: "a scratch registry with an indented row the staged set collides with must produce a nonempty `collisions` — if it does not, the guard is broken and nothing appends."
- `/home/vgpnk/Projects/shokunin/CORPUS.md:152-153` — "accepts 0–3 leading ASCII spaces … 4 or more spaces are indented code and are ignored."
- `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:540-541,574` — `table_re='^ {0,3}\|'`, `row_pass()`.

Inputs, pinned: lane registry `corpus/SOURCES.md` — working tree equals HEAD blob at `b8cb4b31ce80e2e3314b88e85d40ea9873180804`, sha256 `5dccd4f916d3ef9a53a285b40678ed3155edf09a212767ed214f9a6da162f61d`; package `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` (134 staged rows, S109–S242), read-only.

## Guard instrument

Scratch repo `/var/tmp/souji-r29-C3CollisionGuard.fObzBj` (commit `06ec868`); `git -C … rev-parse --show-toplevel` printed the scratch root before the only commit. Old and new differ in exactly one token — the indentation class:

```bash
#!/usr/bin/env bash
# usage: guard.sh <new|old> <registry.md> <staged.md> <outdir>
set -u
mode=$1; reg=$2; staged=$3; outdir=$4
case $mode in
  new) re='^ {0,3}\|[[:space:]]*S[0-9]{3,}' ;;   # census-compatible: 0-3 leading ASCII spaces
  old) re='^\|[[:space:]]*S[0-9]{3,}' ;;         # pre-fix: column zero only
  *) echo "usage: $0 <new|old> <registry.md> <staged.md> <outdir>" >&2; exit 2 ;;
esac
mkdir -p "$outdir"
grep -oE "$re" "$reg"    | grep -oE 'S[0-9]+' | sort > "$outdir/reg-ids"
grep -oE "$re" "$staged" | grep -oE 'S[0-9]+' | sort > "$outdir/staged-ids"
comm -12 "$outdir/reg-ids" "$outdir/staged-ids" > "$outdir/collisions"
printf 'mode=%s reg-ids=%s staged-ids=%s collisions=%s\n' \
  "$mode" "$(wc -l < "$outdir/reg-ids")" "$(wc -l < "$outdir/staged-ids")" "$(wc -l < "$outdir/collisions")"
```

## Proof (scratch fixtures)

Registry fixture built from the pinned registry with three rows re-indented (`S002` 2 spaces, `S005` 3 spaces, `S006` 4 spaces):

```bash
awk -F'|' '{ id=""; if (NF>=13) { id=$2; gsub(/^[ \t]+|[ \t]+$/,"",id) }
  if (id=="S002") print "  " $0; else if (id=="S005") print "   " $0;
  else if (id=="S006") print "    " $0; else print }' corpus/SOURCES.md > fixtures/SOURCES.indented.md
```

| # | registry | staged set | pattern | reg-ids | collisions | verdict |
|---|---|---|---|---|---|---|
| A | indented | S002, S005, S006, S109 | new (0–3) | 138 | **S002 S005 S109** | 2-space and 3-space caught; 4-space S006 ignored |
| B | indented | S002, S005, S006, S109 | old | 136 | S109 | **false green**: S002, S005 invisible |
| C | indented | S002, S005 | new | 138 | **S002 S005** | collision nonempty |
| D | indented | S002, S005 | old | 136 | *(0 bytes)* | **broken guard shape** — would have allowed the append |
| E | column-zero baseline | S002, S005, S006, S109 | both | 139 | S002 S005 S006 S109 (identical) | divergence is exactly the indent class |
| F | indented | staged side indented for S005 | new | 138 | **S002 S005** | extractor symmetric on both sides |
| G | indented | staged side indented for S005 | old | 136 | *(0 bytes)* | old pattern misses the staged side too |

Census agreement (same fixtures, `scripts/sources-census.sh`):

```
baseline registry      validate --file → exit 0, 35 W04, no E;  rows 139
indented registry      validate --file → exit 0, 34 W04, no E;  rows 138
```

The one-warning difference is the 4-space `S006` row: the census drops it, which removes the duplicate-URL warnings `S036`/`S049` derived from it — direct evidence that 4-space rows are not registry rows, matching the guard's `S006` behaviour. `S002` (2-space) and `S005` (3-space) remain census rows, matching A.

## Real run

```bash
S=/home/vgpnk/Projects/shokuknow/merge/souji
A=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/assimilation; mkdir -p "$A"
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md \
  | grep -oE 'S[0-9]+' | sort > "$A/reg-ids"
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' "$S/SOURCES.append.md" \
  | grep -oE 'S[0-9]+' | sort > "$A/staged-ids"
comm -12 "$A/reg-ids" "$A/staged-ids" > "$A/collisions"
```

```
reg-ids=139  staged-ids=134  collisions=31
```

- **registry ids (139, unique 139):** S001–S132, S152, S210–S215. **Max id S215.**
- **staged ids (134):** S109–S242.
- **collision count 31:** `S109 S110 S111 S112 S113 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123 S124 S125 S126 S127 S128 S129 S130 S131 S132 S152 S210 S211 S212 S213 S214 S215`.
- Byte-identical under `LC_ALL=C` for all three files (re-run compared with `cmp`).
- Delivered files: `reg-ids` sha256 `eb211710003137bf9a5bd2c3450ff1fdec5ed894447aaf60280de320964c8792`, `staged-ids` sha256 `639868f172b753dd8f4b998bb07163c6a56985587b02e10e94783b5232158277`, `collisions` sha256 `0192286f8ae87d481fe01bc5a8a5cb84303e025f30156143b474d2f1671850ec`.

The collision is the documented drift class (package built when the lane held 108 rows); it is resolved for the adopted subset only, in scratch, by re-pointing ids to documents.

## Renumber map (by document, never arithmetic)

Rule: the citation's **URL + anchor** identifies the document; the lane id is the next id after the registry maximum, assigned in the order the admitted entries cite the documents. The resolver (`resolve-renumber.py`, scratch commit `06ec868`) matches each cited URL against staged `source` cells, disambiguating same-URL rows by anchor-token recall, then assigns S216 upward.

| document cited | staged row | lane row | resolution evidence |
|---|---|---|---|
| statx(2), man-pages 6.19 | S117 | **S216** | URL hits S117 **and** S125 (two scopes of one page); anchor recall S117=1.000, S125=0.875 — only S117's anchor carries `STATX_BTIME`, the entry's fourth field |
| Broder, resemblance/containment (DOI) | S118 | **S217** | unique URL hit in the staged set |
| link(2), man-pages 6.19 | S122 | **S218** | unique URL hit |
| cmp(1), diffutils 3.12.26 | S136 | **S219** | unique URL hit; entry ground declared in the frozen preregistration (C3), the package has no byte-equality file |

Citation source (read this run): `merge/souji/knowledge/corpus/knowledge/duplicate-verdict-identity.md:1-3` cites S117/S118/S122 with the same URLs; the byte-equality ground is `preregistration.txt` C3 ("cmp(1) three-valued exit contract plus the same identity rule"), corroborated by `.ufo/waves/round-29/w1/deliver-duplicate-verdict-byte-equality.md:1` (`source: S219 — cmp(1) …`).

Counterfactuals, both rejected by the rule:
- **id-preserving append** → S117→S117, S118→S118, S122→S122 are *duplicate ids*; S136→S136 re-uses a gap inside the historical sequence. Census `E03` confirms exactly this: appending the four rows with their campaign ids yields `E03 S117`, `E03 S118`, `E03 S122`, and no E03 for S136.
- **constant +99 arithmetic** (the offset that happens to map S117→S216) → `S216 S217 S221 S235`: the third and fourth rows land on wrong ids. The offset "repairs one citation and breaks the next".

Also from the scratch mirror (append probe, not the lane):
- renumbered append of the four rows → rows 143, **no E03, no E04**; remaining findings are E09 ×4 (prose `recheck` cells) and E11 ×6 (raw `used-by` names the campaign entries, not the two admitted ones) — normalization work owned by the append seat, recorded here so nothing appends raw.
- registry targets S216–S219 are unoccupied in the lane (`0` rows each).

## Findings / risk notes for the L1

1. The guard is numeric-only: a green guard means "no id reused", not "append-safe". The lane already holds statx(2) at `corpus/SOURCES.md:135` (S114, scope "the identity fields a per-item origin record can carry …"), and the staged S117 scope differs only in wording, so census `E04` does not fire on a same-page second row. Whether S216 adds ground S114 does not hold is a curation decision, not a guard result.
2. Campaign ids are not portable: the staged set already uses **S216–S219 for four different documents** (Breitinger chapter, Unpaywall record, `config/gc.txt`, `git-worktree.txt`). Any later round adopting those rows must re-point by document again.
3. `duplicate-verdict-byte-equality.md` is absent from the package (68 knowledge entries; no such filename) — the cmp citation exists only as the preregistration's declared ground plus the lane's own delivery drafted this wave. Recorded as a dependency, not a guard defect.
4. Guard scope limits (deliberate): 4+ leading spaces are not rows (proven), tabs/CRLF/4-digit-id ordering are out of this seat's scope and belong to `MutateGuardAndRows`.

## Deliveries

- `.ufo/waves/round-29/w1/assimilation/reg-ids`, `staged-ids`, `collisions` (sha256 above).
- this file.
- scratch removed after recording commit `06ec868`; its content is the guard script, the staged fixtures, `resolve-renumber.py` and the validate/probe outputs transcribed above.
