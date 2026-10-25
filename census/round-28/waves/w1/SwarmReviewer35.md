## Status
STATUS: PARTIAL — the frozen §10 collision check reproduces 27 known collisions at base and in the current registry; the required S212–S214 adoption and citation remapping are not present in the lane snapshot, so those claims cannot be confirmed.

## Evidence
- Fresh frozen extractor, lane `corpus/SOURCES.md` and staged `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`, pattern `^ {0,3}\|[[:space:]]*S[0-9]{3,}` followed by extracted/sorted ids and `comm -12`: registry=135 ids, staged=134 ids, collisions=27. Full collision set: S109–S132, S152, S210, S211. Duplicate registry ids=0.
- Repeated against `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3a2a80d0d18940a5e352ebc526da22a57dad83c4:corpus/SOURCES.md`: 135 ids, same 27 collisions; diff of base and working-tree extracted ids is empty. Lane HEAD observed as `0c96332932e66bbaf9cf1c246091d3275a0ab612` (working tree has unrelated in-flight changes); registry ends at S211.
- Staged source mapping, `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:56-57,71`: POSIX open() is S158, rename() S159, fsync() S173. Quote: “IEEE Std 1003.1-2024 (POSIX.1-2024) · open()” (SOURCES.append.md:56). The staged package’s S212/S213/S214 instead identify the r35 fleet-prune census, HAL metadata, and Gitea v1.15 docs, respectively (same file:110-112).
- Current lane registry `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md:154-156` has S152, S210, S211, but no S212–S214. Its existing origin-record mechanism entries are instead S152, S210, S211. The intended r28 knowledge files `corpus/knowledge/origin-record-exclusivity-r28.md` and `origin-record-durability-r28.md` are absent from the lane tree; no landed citations can be checked.
- The round-28 draft gate table `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-28/records/gate-table-draft.md:5-7` maps POSIX open/rename/fsync to S212/S213/S214, but it is explicitly a draft and conflicts with the currently opened staged S212–S214 rows. Its quote: “S212 POSIX open()”.

## Findings
1. **Required adopted-id mapping is not established in the current lane state.** By-document mapping supported by the opened source registry is POSIX open() → staged S158, rename() → S159, fsync() → S173. The draft proposes new lane IDs S212/S213/S214, but these rows and the knowledge entries are absent. Meanwhile staged IDs S212–S214 name three different documents. Do not treat numeric equality as identity; the draft’s mapping needs the actual lane rows and citations before adoption can be verified.
2. **Citation re-pointing is unverified / not landed.** Neither intended r28 knowledge entry exists in the lane tree, so there is no entry citation to confirm against the POSIX documents. Draft table rows are not evidence that adopted entries cite the correct source rows.

## Attack log
None. This is a review of the assigned collision/mapping check, not an attack on a frozen predicate.