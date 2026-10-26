## Status
STATUS: PASS — no sibling claims F3 (duplicate / identity / byte-equality verdicts). Zero hits for `statx`, `Broder`, `cmp(1)`, `hard link` across 904 sibling files; every remaining hit is incidental or an adjacent identity check on a different object. No contested rows. Read-only; no installs.

## Evidence
Revision: fleet root /home/vgpnk/Projects/shokunin, working tree as read 2026-10-25 (souji lane base 691dd29, not touched). souji-shokunin excluded.

Command (bash, run from the fleet root):
```
shopt -s nullglob; files=()
for d in *-shokunin; do [ "$d" = souji-shokunin ] && continue
  for f in $d/PROVINCE.md $d/SKILL.md $d/corpus/README.md $d/corpus/knowledge/*.md; do [ -f "$f" ] && files+=("$f"); done; done
grep -n -i -o -E 'duplicate|byte-identical|hard link|inode|cmp\(1\)|statx|Broder|resemblance|near-duplicate|dedup' "${files[@]}"
```
Result: 904 files scanned, 1738 matches.

Per-lane matrix (match counts, case-insensitive; `-o` so a count is occurrences, not lines):

| lane | inode | resemblance | near-duplicate | byte-identical | duplicate | dedup |
|---|---|---|---|---|---|---|
| audio | 0 | 0 | 0 | 6 | 2 | 0 |
| chousa | 9 | 0 | 0 | 81 | 29 | 1 |
| game-dev-2d | 0 | 0 | 0 | 1 | 3 | 0 |
| game-dev-3d | 0 | 0 | 0 | 1 | 1 | 0 |
| kagi | 2 | 0 | 0 | 2 | 40 | 1 |
| kaidoku | 12 | 0 | 0 | 269 | 22 | 14 |
| kake | 5 | 0 | 0 | 29 | 26 | 18 |
| kama | 19 | 0 | 0 | 3 | 45 | 1 |
| kasegi | 0 | 0 | 0 | 17 | 61 | 11 |
| kengaku | 0 | 0 | 0 | 28 | 18 | 8 |
| kotoba | 0 | 0 | 2 | 32 | 54 | 8 |
| kotodama | 0 | 1 | 0 | 8 | 11 | 7 |
| kumitate | 24 | 0 | 0 | 36 | 106 | 79 |
| lore | 1 | 3 | 0 | 29 | 85 | 4 |
| mado | 1 | 0 | 0 | 66 | 14 | 1 |
| mori | 3 | 0 | 0 | 39 | 41 | 12 |
| revenger | 0 | 0 | 0 | 10 | 8 | 0 |
| tabi | 0 | 0 | 0 | 68 | 28 | 1 |
| tameshi | 2 | 1 | 0 | 62 | 40 | 0 |
| tsukuroi | 12 | 0 | 0 | 39 | 13 | 2 |

Column order was read from the awk header (`lane inode resemblance near-duplicate byte-identical duplicate dedup`) of the run; the `statx`, `Broder`, `cmp(1)` and `hard link` columns do not appear because their count is 0. Per-file rows (612) are in the delivery TSV.

Supplementary semantic sweep (same file set, `grep -n -i -E 'hard-?link|st_ino|st_nlink|link count|same inode|dupe|fdupes|jdupes|rdfind|rmlint|fclones|duplicate file|duplicate-find|duplicate verdict|identical file|minhash|simhash|shingl|jaccard'`): 441 lines incl. noisy `\bcmp\b`/`containment` terms (not in the requested list). Zero hits for fdupes, jdupes, rdfind, rmlint, fclones, minhash, simhash, shingl, jaccard, st_ino, "duplicate verdict", "duplicate file".

Souji's own claim (read): `souji-shokunin/PROVINCE.md:86` "Sweep r12: no sibling claims F1/F3/F4 ground" and `:69-70` "F3 duplicate verdicts — byte-identical copies; a `duplicate` receipt class would be a taxonomy change (operator decision)."

## Findings
1. **Verdict: no sibling claims F3.** No sibling PROVINCE.md, SKILL.md, README or knowledge entry holds a duplicate-file verdict, a byte-equality (`cmp`) contract, `statx` identity fields or Broder/resemblance vocabulary. Terms `statx`, `Broder`, `cmp(1)`, `hard link` (spaced) = 0 in 904 files.
2. **Adjacent (reported, not absorbed), identity checks on other objects:**
   - chousa `corpus/knowledge/hardlink-alias-r13.md:11-12` — quote: "A hardlink is different: every alias IS the file (same inode, no true path)". `SKILL.md:158` refuses `st_nlink != 1` sources unread at the research-gate chokepoint. Shares link-count vocabulary; issues no duplicate verdict. chousa owns research method (souji `PROVINCE.md:82-83`), so F3 sources are applied by souji, not restated.
   - kagi `corpus/knowledge/drift-gate.md:73` `LINK` verdict (symlink or `nlink>1`, "the path is not uniquely the file"); `adjacency-scope.md:228`.
   - kumitate `corpus/knowledge/local-ship.md:23` ("one name, one inode"), `singleton-and-queue-ownership.md:24` (inode-bound owner hardlink), `kimi-skills-plugins.md:281` (dev:inode intersection). Nearest by name: `SKILL.md:628` `source-dupes` gate (contract `kumitate-source-dupes-v1`, duplicate-URL groups in SOURCES registries) — URL rows, not file copies; plus `at-least-once-dedupe.md` (queue idempotency) and `distill-and-l3.md` (identity_hash dedupe).
   - kaidoku `2026-10-22-r27-renamed-copy-evidence-id-identity.md` — byte-identical renamed copy vs reverse-engineering evidence ids; content identity for REA, not a hygiene receipt.
3. **Hosts named in the brief (kasegi, mori, tsukuroi, kama, plus kake):** none touch dedup of host files. kasegi = duplicate bounty submissions / `DEDUPED` mission state (`SKILL.md:911`); mori = journal cursor dedup (`PROVINCE.md:25,54`) and `/proc/locks` inode of the watchdog lock (`SKILL.md:793`); tsukuroi = directory inode mode/mtime (`SKILL.md:1701-1703`); kama = directory/socket inodes in `listener-census.md` and Ollama duplicate JSON keys (`ollama-evidence-replay.md:136-154`); kake = canonical-URL variants and `fleet.dedupe-report.md`. All different senses.
4. **Incidental senses:** `byte-identical` (kaidoku 269, chousa 81, tabi 68, mado 66, tameshi 62) is gate/pin wording ("content pins byte-identical"); `resemblance` (lore 3, kotodama 1, tameshi 1) is provenance resemblance; `near-duplicate` (kotoba `SKILL.md:326`, `agent-def-audit-round6.md:81`) concerns near-duplicate agent/skill definitions; `--no-hardlinks` hits are git clone flags (kotoba, kumitate).
5. **Fleet root:** `grep -n -i -E 'duplicate|byte-identical|hard ?link|inode|dedup|near-dup|identical'` over AXES.md, MISSION.md, CORPUS.md, AGENTS.md, README.md, PROTOCOL.md, PROTOCOL-APPENDIX.md, ROADMAP.md, LEARNING.md, SCORECARD.md: AXES.md, MISSION.md, AGENTS.md, README.md, ROADMAP.md, LEARNING.md = 0 hits; hits in CORPUS.md:121,142 (duplicate ids check), PROTOCOL.md:432, PROTOCOL-APPENDIX.md:34, SCORECARD.md:155,198,350,489 are ID/registry/queue-key wording. No fleet-root text assigns duplicate-verdict ownership to any lane. [INFERENCE] F3 therefore rests only on souji's own PROVINCE.md frontier row.
6. **Caveat on the F3 entry text:** the F3 PROVINCE row (`:69-70`) says a `duplicate` receipt class is an operator taxonomy decision; the C3 entries should stay verdict vocabulary/contract knowledge and must not introduce a receipt class. [INFERENCE from PROVINCE.md:69-70, not a sibling claim].

## Deliveries
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-sibling-overlap.tsv — 629 lines (header + 628 rows), 7 tab columns (`kind lane file term count judgement note`): 612 `hit` rows (per file and term), 14 `judged` adjacency rows (adjacent / not-claimed), 2 `verdict` rows (`no-owner` for fleet-root texts, `no-sibling-claims-F3`).
