# ExecRenumberMap — R26 C2 staged->lane renumber map

## Status

STATUS: PASS — the 5 staged rows S109/S110/S111/S123/S131 are extracted byte-exactly, have **0 within-scope duplicates** in the lane registry (E04 clean at base and HEAD), their two own-work evidence files exist with matching sha256 prefixes, and the prereg's map (S109->S128, S110->S129, S111->S130, S123->S131, S131->S132) matches the rows already staged in the working tree. Two normalizations are required before append and one used-by observation needs an L1 decision (F4, F6).

Delivery file: `.ufo/waves/round-26/w1/renumber-map.md` (this report's data artifact; rows inside it verified byte-exact).

## Evidence

Lane revisions: base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` (127 rows, max S127); HEAD `44531281914ddd200432cdc7dae8ad958c5447e3` (committed registry still 127 rows); working tree `M corpus/SOURCES.md` with 5 added rows at lines 149-153.

1. Prereg order and obligation (`.ufo/waves/round-26/preregistration.txt:91-94`, opened this run): `ID COLLISION (staged ids collide with the lane registry S109-S127)` and `staged S109->S128, S110->S129, S111->S130, S123->S131, S131->S132.`
2. Staged rows opened this run at `SOURCES.append.md` lines 7, 8, 9, 21, 29. `awk -F'|' …` prints `cols=13` for each (11 columns), no in-cell pipe. Extract sha256 `3a1002bbf7a21e0b3690…` (5 lines).
3. Collision extractor (prereg form), run on both files:
   - staged: 134 ids, S109–S242 contiguous.
   - lane worktree: 132 ids; lane HEAD: 127 ids, S001–S127.
   - `comm -12` vs lane HEAD → `S109 S110 S111 S112 S113 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123 S124 S125 S126 S127`; adding the worktree registry extends this to S132 only because the appended rows are already present.
4. URL/path grep of each staged source against `git show HEAD:corpus/SOURCES.md` and `corpus/SOURCES.md` → **empty at HEAD for all five**; worktree hits are the new rows themselves (lines 149-153), one hit each.
5. Duplicate-rule predicate, `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:646-649`: `duplicate url … within scope`, i.e. E04 is same normalized URL plus same scope, non-rejected, no `supersedes` in `teaches`; own-work rows carry no `http` URL so the path grep in (4) is the only applicable check for them.
6. Own-work paths (row cells name `lanes/souji/round2/...`, campaign-root-relative; all three are MISSING under `merge/souji`):
   - `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/fixtures/r23-trigger-prune.sh` — 7597 bytes, executable.
   - `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out` — 1043 bytes.
   - `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out` — 1672 bytes.
   - `sha256sum` prefixes: `11c136aa`, `510722c1`, `1ac71c4f` — matching the cells (`510722c1…`, `1ac71c4f…`, and the fixture digest added by the live S131 row).
7. Live append cross-check: `git diff -- corpus/SOURCES.md` adds exactly 5 rows after S127; field comparison confirms S128<-S109, S129<-S110, S130<-S111, S131<-S123, S132<-S131 with documents, kind, tier and scope unchanged.
8. Delivered verbatim block re-verified against the source extract with `cmp` → `DELIVERED ROWS BYTE-EXACT (5/5)`.

Tooling: none installed or upgraded (no package manager invoked; `pacman` untouched). Scratch `/var/tmp/souji-r26-ExecRenumberMap/` used for the extract and the `cmp` checks, removed before yield.

## Findings

1. **No duplicate document; only numeric collision.** None of the five staged documents exists in the lane registry at base or HEAD. The five colliding numbers are different documents: lane S109 = noreplace probe, S110 = rename(2), S111 = mv(1), S123 = git-worktree(1) § REFS/§ DETAILS, S131 = absent (max S127). Location: `corpus/SOURCES.md` registry at `0eca7c8` and `4453128`.
2. **E04 cannot see the own-work rows.** `scripts/sources-census.sh:599-603` derives the duplicate key from a `https?://` regex; own-work source cells yield an empty key so E04/W04 skip them. Location: `scripts/sources-census.sh:601-603`. The path greps in Evidence 4 are what clears S123/S131.
3. **Own-work evidence is campaign-side, not lane-re-derivable.** The three files exist under `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/`, not under `merge/souji` and not in this lane repo (no `lanes/` tree). Digests match, but recheck of S131/S132 requires read access to a read-only campaign tree. Precedent: lane S109 at HEAD cites the campaign path plus a vendored lane copy; S131/S132 cite the campaign path only.
4. **Staged S131 cannot be appended verbatim — its `used-by` names a file that does not exist in this lane.** Cell value `corpus/knowledge/count-objects-garbage-semantics-r23.md`; `find` at lane root and `git ls-tree HEAD -- corpus/knowledge` both show no such file (only `count-objects-garbage-readings-r25.md` and `count-objects-linked-worktree-garbage.md`). `scripts/sources-census.sh:566-568` prints `missing used-by %s` (E11) for every non-existent used-by path on a mined row, so a verbatim append would fail the C2 K3 arm. The live S132 row already rewrites the cell to `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`; the map in the delivery file records that rewrite.
5. **The map agrees with the uncommitted live append.** Registry lines 149-153 implement exactly the prereg order, with `opened` re-dated 2026-10-25, snapshot anchors added for S128/S129/S130, `recheck` cadence stripped of prose, and the S131 used-by rewrite of F4 applied. My duplicate check treats HEAD (127 rows) as the pre-append registry; the `S128–S132` intersection against the working tree is the append itself.
6. **Used-by completeness observation on S131 (L1 decision needed).** `corpus/knowledge/git-auto-maintenance-trigger-set.md:45` carries a literal `(S131)` — "the behavioural gap … is closed by the sibling entry `…-r23.md` (S131)". The appended S131 `used-by` lists only `…-r23.md`. If a literal id reference counts as "an admitted entry citing it" (prereg: `used-by = exactly the admitted entries citing it`), S131's cell under-counts and the pre-append state of the entry also needs the citation re-pointed to the fixture row. E11 only checks path existence, so K3 will not catch this. Reported, not changed.
7. **Id-reuse ambiguity the lesson Gate must disambiguate.** Campaign S131 = the worktree census in `corpus/lessons/round-22.md:298,351,363` and `corpus/lessons/round-24.md:236`; after this append lane S131 = the fixture and lane S132 = the census. Campaign S128 (aliyun) / S129 (atlassian) / S130 also mean other documents in `.ufo/waves/round-24/w1/ScoutPkgEntries.md:41-48`. Write bare ids as `SOURCES S128`…`SOURCES S132`, as round 25 did for S124-S126.
8. **Minor citation/row URL divergence for S129.** `git-auto-maintenance-trigger-set.md:2` and `git-auto-maintenance-trigger-set-r23.md:2` cite `https://github.com/git/git/tree/v2.56.0/builtin` while row S129's canonical cell is `https://github.com/git/git/blob/v2.56.0/builtin/fetch.c`. No validator failure (E04 reads the row), but the entry citation resolves to a different URL than the row it names.

## Attack log

Not an attack seat; no predicate, target or case set is challenged. One measurement caveat for the C2 K3 arm: the E11 arm validates only used-by path existence, so "mined used-by paths missing 0" is satisfiable by pointing used-by at any existing entry and does not prove citation completeness (F6 is the live instance). Stricter-only would be a literal-id scan of admitted entries; not proposed as a change here.
