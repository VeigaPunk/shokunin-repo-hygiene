## Status
STATUS: PASS — id-collision guard proven on the mandated indented fixture (2- and 3-space rows caught, 4-space row ignored, old column-zero-only pattern false-greens to an empty `collisions`), then run over committed registry bytes: 31 collisions, registry max id S215, and the four adopted rows renumber S117→S216, S118→S217, S122→S218, S136→S219 reproduced by document (URL+anchor), never arithmetic.

## Evidence

Preregistration read first: `.ufo/waves/round-29/records/preregistration.txt` (frozen C1/C2/C3, rows S216–S219, "SOURCES rows 139 -> 143"). Guard contract read at `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md:470-491` (item 10); row rule at `CORPUS.md:152-153` and `scripts/sources-census.sh:540-541,574`.

Registry read == committed bytes: `git rev-parse HEAD` → `b8cb4b31ce80e2e3314b88e85d40ea9873180804`; `sha256sum corpus/SOURCES.md` = `5dccd4f916d3ef9a53a285b40678ed3155edf09a212767ed214f9a6da162f61d` = `git cat-file -p HEAD:corpus/SOURCES.md | sha256sum`. Registry rows 139, unique ids 139, ids S001–S132 + S152 + S210–S215, max S215.

Proof matrix in scratch `/var/tmp/souji-r29-C3CollisionGuard.fObzBj` (one git repo, `rev-parse --show-toplevel` = scratch root before the only commit, `06ec868`); old/new guard share everything but the regex token (`^ {0,3}\|` vs `^\|`):

| registry fixture | staged | new (0–3) | old (column-zero) |
|---|---|---|---|
| `S002` at 2 spaces, `S005` at 3 spaces, `S006` at 4 spaces | S002 S005 S006 S109 | reg 138, collisions **S002 S005 S109** | reg 136, collisions **S109** |
| same | S002 S005 | collisions **S002 S005** | collisions **empty, 0 bytes** (false green) |
| column-zero baseline | S002 S005 S006 S109 | 139 / S002 S005 S006 S109 | 139 / identical |
| indented, staged side also indented | mixed | 138 / S002 S005 | 136 / empty |

Census agreement on the same fixtures: `scripts/sources-census.sh validate --file` exit 0 both times; rows 139 baseline vs 138 indented; W04 35 vs 34 (the 4-space `S006` row being dropped removes the S036/S049 duplicate-URL warnings) — the census and the new pattern agree on 0–3 spaces and on ignoring 4.

Real run (exact pipeline, output redirected to `.ufo/waves/round-29/w1/assimilation/`): `reg-ids=139 staged-ids=134 collisions=31`; collisions `S109…S132, S152, S210…S215`; all three files byte-identical under `LC_ALL=C`. Sha256: reg-ids `eb211710…c8792`, staged-ids `639868f1…158277`, collisions `0192286f…50ec`.

Renumber resolver (`resolve-renumber.py`, scratch commit `06ec868`): statx URL hits staged S117 **and** S125, anchor recall 1.000 vs 0.875 (only S117 carries `STATX_BTIME`); S118/S122/S136 unique URL hits. Declared map reproduced: S117→S216, S118→S217, S122→S218, S136→S219 — all four match. Counterfactuals: id-preserving append gives duplicate ids at S117/S118/S122 (census `E03` confirms exactly those three, none for gap id S136); constant +99 gives S216 S217 **S221** **S235**. Renumbered append probe on the mirror: 143 rows, no E03/E04 (E09 ×4 prose recheck, E11 ×6 unadopted used-by — normalization is the append seat's).

Deliverable: `.ufo/waves/round-29/w1/deliver-collision-guard-proof.md` sha256 `637419005a603a33a64679e0d27e9d4b9eb55f0207acbbf99fab0ce271731afb`.

## Findings

1. **Guard proven, false-green demonstrated.** A registry row carrying `S002` at 2 leading spaces and `S005` at 3 is a census row (`validate --file` exit 0) yet the column-zero-only pattern returns an empty `collisions`; the 0–3-space pattern returns both. Location: scratch `out/D-old/collisions` (0 bytes) vs `out/C-new/collisions`; rule `/home/vgpnk/Projects/shokunin/CORPUS.md:152-153`.
2. **4-space negative holds and agrees with the census.** `S006` at 4 spaces is absent from `reg-ids` and from `collisions` under the new pattern, and the census drops the same row (rows 138 vs 139, W04 35 vs 34). Location: scratch `out/A-new/`, `out/validate-indented.tsv`.
3. **Real collision set is 31, not 4.** Staged S109–S242 vs registry S001–S132/S152/S210–S215 intersects at S109–S132 (24), S152, S210–S215 (6). Mass drift of the package id space; the four adopted rows are resolved in scratch by document. Location: `.ufo/waves/round-29/w1/assimilation/collisions`.
4. **Registry max id is S215; S216–S219 are unoccupied in the lane.** Location: `.ufo/waves/round-29/w1/assimilation/reg-ids` (tail `S215`); `grep -cE '^ {0,3}\|S21[6-9] '` on `corpus/SOURCES.md` = 0 each.
5. **Renumber map (document order, URL + anchor):** S117 statx→S216, S118 Broder DOI→S217, S122 link→S218, S136 cmp→S219. statx needs the anchor, not the URL alone: the page has two staged scopes (S117, S125). Location: `merge/souji/knowledge/corpus/knowledge/duplicate-verdict-identity.md:1-3`; package `SOURCES.append.md` rows S117/S118/S122/S136.
6. **The same map is independently visible in the wave's own deliveries** (data read, not instruction): `.ufo/waves/round-29/w1/deliver-sources-append-block.md:25-28` carries the same four-row map, and `deliver-duplicate-verdict-byte-equality.md:1` cites `S219 — cmp(1)`. No conflict with this seat's result.
7. **A green guard is not append-safety.** The lane already holds statx(2) at `corpus/SOURCES.md:135` (S114, "the identity fields a per-item origin record can carry …"), and the staged S117 scope differs only in wording, so census `E04` (URL+scope) stays clean while the registry gains a second row for the same page. Whether S216 adds ground S114 lacks is a curation decision; the guard cannot answer it. Location: `corpus/SOURCES.md:135` vs package `SOURCES.append.md` row S117 scope cell.
8. **Campaign ids are not portable:** staged S216–S219 already denote four different documents (Breitinger chapter, Unpaywall record, `Documentation/config/gc.txt`, `Documentation/git-worktree.txt`), so later adoptions of those rows must re-point by document again. Location: package `SOURCES.append.md` rows S216/S217/S218/S219.
9. **Package gap:** `duplicate-verdict-byte-equality.md` does not exist in `merge/souji/knowledge/corpus/knowledge/` (68 files, none matching); the cmp ground is the frozen preregistration plus the lane's own wave delivery. The S136→S219 leg therefore rests on the prereg, not on package bytes. Location: directory listing of the package knowledge dir.
10. **Raw append is not appendable:** renumbered raw rows pass E03/E04 but raise E09 ×4 and E11 ×6 on the scratch mirror, so recheck/used-by normalization must precede the append. Location: scratch `out/validate-append-probe.tsv`.

## Attack log

Not an attack seat; no predicate, target, counter or case set is challenged. One observation filed for the L1, no amendment proposed: the guard and census `E04` are both blind to a *same-document* row whose `scope` cell is reworded (finding 7), so "collisions empty + E04 clean" does not by itself license the append — document-level review of the four URLs remains necessary.

## Deliveries

- `.ufo/waves/round-29/w1/assimilation/reg-ids`, `staged-ids`, `collisions`.
- `.ufo/waves/round-29/w1/deliver-collision-guard-proof.md` (guard source, fixture matrix, run, map, risks).
- Scratch `/var/tmp/souji-r29-C3CollisionGuard.fObzBj` committed as `06ec868` and then removed; nothing outside the lane's `.ufo/waves/round-29/w1/` was written.
