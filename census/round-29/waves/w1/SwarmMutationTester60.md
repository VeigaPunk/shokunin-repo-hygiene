# SwarmMutationTester60 — round 29 w1 — mutation probe: id-collision guard + row-normalization rules

## Status

STATUS: PASS — guard caught every real collision shape (column-zero, 1/2/3-space, CRLF, Paths-prose) and correctly ignored 4-space and tab rows in agreement with `sources-census.sh`; all four normalization mutants of S117/S118/S122/S136 were killed by `sources-census.sh validate --file` (E01/E09/E11/E10); no survivors; pristine baselines clean before each battery and byte-identical after.

## Evidence

- Lane: /home/vgpnk/Projects/shokunin/souji-shokunin, HEAD `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (`git rev-parse HEAD`), base `691dd29211c53d0ef94fa072394cb9c8a69fe92e` verified present (`rev-parse --verify …^{commit}` → BASE-OK). Read-only git only.
- Guard source: /home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md:477-484 (the 3-command grep/sort/comm pipeline; seat header named a lane path — the file lives at the fleet root).
- Detector under test: `sources-census.sh` /home/vgpnk/Projects/shokunin/scripts/sources-census.sh (selftest untouched, not run to completion; validate used in `--file` mode per the sanctioned gate shape, `--today 2026-10-25`).
- Fixtures: scratch only, /var/tmp/souji-r29-MutateGuardAndRows.Z9ytCEF/ (removed at close; sha256 ledger below).
- Tools: none installed or upgraded (pacman guard observed; system gawk 5.4.1, bash, coreutils used as-is).
- Preread per contract: census/round-29/records/preregistration.txt (frozen contract; clause "The collision guard is proved on a scratch indented row before any append" — preregistration.txt:9).

### Part A — guard battery (mutant, expected detector, output, verdict)

Baseline F0 (registry S901 vs staged S210, no shared id): `collisions=[]` — detector conclusive. Each mutant = one collision/indentation shape injected into pristine fixture bytes.

| Mutant | Expected | Actual output (guard = reg/staged/collisions) | Verdict |
|---|---|---|---|
| F1 column-zero `\| S216 \|` both sides | collisions=[S216] | `reg=[S216,S901] staged=[S216] collisions=[S216]` | killed |
| F2 1-space ` \| S216 \|` | caught | `collisions=[S216]` | killed |
| F3 2-space | caught | `collisions=[S216]` | killed |
| F4 3-space | caught | `collisions=[S216]` | killed |
| F5 4-space `    \| S216 \|` in registry only | ignored (indented code); S216 absent from reg-ids | `reg=[S901] staged=[S216] collisions=[]`; `validate --file` → rc 0 `file ok`; `census --file` → `file rows 1` | correct-ignore, guard↔parser agree |
| F6 leading tab `\t\| S216 \|` (registry side) | ignored | `reg=[S901] … collisions=[]`; validate rc 0; census `rows 1` | correct-ignore, agree |
| F6b tab on staged side | ignored | `staged=[] collisions=[]` | correct-ignore, agree |
| F7 staged S2160 vs registry S216 (and F7b reverse) | no collision (distinct ids); no S216 truncation of S2160 | `collisions=[]` both ways; `printf '\| S2160 \|' \| grep -oE 'S[0-9]+'` → `S2160`; P1 probe: S216+S2160 in one file → validate rc 0, `rows 2`, no E03 | correct (no false collision) |
| F8 CRLF rows both sides, colliding id | caught | `collisions=[S216]` (extraction \r-immune); but `validate --file` on the same CRLF registry → rc 1, `E12` on every row (see Finding 5) | killed; parser divergence documented |
| F9 colliding id only in a `## Paths` prose row | caught (guard greps whole file) | `collisions=[S216]`; validator → `E12 S216 row outside Registry section` rc 1 | killed (over-approximation, see Finding 6) |
| F0 restored control (F0 bytes rebuilt, detector rerun) | collisions empty | `collisions=[]` | restoration confirmed |

Part A fixture sha256 (snapshot ledger): f0-reg 1202633a…2b6d5f, f1-reg 042f2621…473a21, f2-reg c9b809bc…3f49ee, f3-reg 0a7c4950…184628f, f4-reg 05c09143…510d6ba, f5-reg c4af6227…2566da40, f6-reg 341af9f2…3a1c5 (f6b-reg = f0 bytes, 1202633a…), f7-reg 042f2621…473a21, f7b-reg 00d87d25…57e81e, f8-reg 2f51b3e4…614e34, f9-reg de7828bb…71265; staged snapshots f1–f5/f6/f7b/f9 all f9b6daa4…68e244, f6b e9b9901c…6ad8d, f7 acdcac20…67cf9b, f8 6ec54f06…a61e2ba.

### Part B — normalization mutants of staged rows (mutant, expected detector, output, verdict)

Rows taken verbatim this run from /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:15 (S117), :16 (S118), :20 (S122), :34 (S136); normalized per prompt ("recheck becomes a valid ISO date, `NNd`, or symbolic cadence" — .ufo/prompts/souji-round-29.md:490): recheck prose stripped (`on-release` / `365d`), all other cells verbatim, status mined, used-by = staged citing entries, mirror layout `part-b/validate/corpus/SOURCES.md` with the cited entry files present.

First run: baseline FAILED (`E11` on all 8 used-by paths) — my harness had placed the registry at `part-b/pristine.md`, so the validator resolved used-by against the scratch root. Per protocol that run was inconclusive, not a kill; fixed the harness placement to the sanctioned layout and reran. Harness defect, not a tooling finding.

Baseline B0 (normalized four rows): `validate --file` → rc 0, `file ok`. Then one mutant per row:

| Mutant | Expected | Actual output | Verdict |
|---|---|---|---|
| M1 S117: escaped pipe `\|` inside anchor cell | E01, rc 1 | `E01 S117 fields=12`, rc 1 (single clean finding; used-by pass skips the shifted row) | killed |
| M2 S118: recheck `365d — re-resolve the DOI and re-read § 2` (staged prose verbatim) | E09, rc 1 | `E09 S118 recheck=365d — re-resolve the DOI and re-read § 2`, rc 1 | killed |
| M3 S122: used-by only `corpus/knowledge/duplicate-verdict-byte-equality.md` (entry absent from mirror = unadopted) | E11, rc 1 | `E11 S122 missing used-by corpus/knowledge/duplicate-verdict-byte-equality.md`, rc 1 | killed |
| M4 S136: kind `community` at tier `A` | E10, rc 1 | `E10 S136 community-at-A`, rc 1 | killed |

Restoration: pristine `part-b/validate/corpus/SOURCES.md` sha256 `8209f32961cdad356d665c974f7491fccd07373ff3398ddf272b56b2d231f675` before and after the battery (mutants written to sibling paths m1…m4: ea6bc682…, c4987b68…, 72d54537…, 74ea9aff…); B0 rerun after mutants → rc 0 `file ok`. Probe files p1.md 3ba33bb4…ad3a, p2.md a788a85f…49a656.

## Findings

1. Guard catches every collision carrier the registry parser treats as a row: column-zero and 1/2/3-space indents (F1–F4), CRLF rows (F8), and — conservatively — row-shaped lines outside `## Registry` (F9). Location: /home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md:477-484. Quote (preregistration.txt:9): "The collision guard is proved on a scratch indented row before any append".
2. 4-space and tab rows: guard and parser agree — both ignore them. Parser rule quote (/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:40-41): "Maintained parser accepts 0–3 leading ASCII spaces before Markdown rows/headings;" and "4 or more spaces are indented code and ignored." Guard grep `^ {0,3}\|` shares the 0–3-space rule (prompt:478); the gawk row test is the same shape (:615), and `census --file rows 1` proves exclusion. A collision id living only in a 4-space/tab row is not a registry id, so ignoring it misses nothing real.
3. S2xx vs S2xxx (4-digit) ids are distinct everywhere: guard `comm -12` exact-match finds no collision either direction; prefix extraction is greedy (`S2160` never truncated to `S216`); validator E03 is exact-match (:641) and P1 shows S216+S2160 coexist clean (`rows 2`, rc 0). No false collision, no missed collision.
4. CRLF: the guard is CRLF-immune (F8 caught), but the validator's gawk section test `in_registry=(trim(substr(line,3))=="Registry")` (:611) leaves the trailing `\r` because `trim` strips only `[ \t]` (:581) — a CRLF registry yields `E12 … row outside Registry section` on every row (rc 1). The bash `usedby_findings` pass is CRLF-tolerant (`[[:space:]]` regexes, trim_cell, :540-541,567) and still fires E11 on the same file (probe P2: E12 + E11). Two passes disagree on section membership; net behavior fails closed, so no invalid registry passes. Observation, not a gameable hole; no attack filed.
5. Guard over-approximation (F9): an id in a `## Paths` prose row is counted as a registry id and can force a scratch renumber although the validator would reject that row as E12 (:621). Conservative-safe direction for a pre-append guard — it cannot miss a real row collision [INFERENCE from the one-directional overlap: guard's extraction set is a superset of parsed-registry ids for 0–3-space and CRLF shapes]. Cost is at most a spurious renumber in scratch.
6. Assignment-path correction: the seat header cited /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/prompts/souji-round-29.md, which does not exist; the file is at the fleet root /home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md (lane `.ufo/` holds only quarantine/ and waves/). Findings 1–5 above cite the fleet-root path.

## Attack log

Item is a mutation probe, not a counter attack. No attack filed: no survivor among the nine guard shapes and four normalization mutants; the one divergence found (Finding 4, CRLF section test) fails closed (rc 1), so it cannot green-light an invalid registry, and `sources-census.sh validate` is a C3 gate whose target registry is LF — a CRLF mutant would be rejected, not accepted.

## Deliveries

- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/SwarmMutationTester60.md (this report; the only lane byte I wrote; no git/jj/rm/mv against lane or fleet; shokuknow read-only).
- Scratch /var/tmp/souji-r29-MutateGuardAndRows.Z9ytCEF/ and /var/tmp/souji-r29-MutateGuardAndRows.location removed after evidence capture.
