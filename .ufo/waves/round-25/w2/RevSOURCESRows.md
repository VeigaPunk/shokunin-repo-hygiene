# RevSOURCESRows — round 25, wave 2 (falsify SOURCES S124–S127 + census)

Seat: `L1Souji25.RevSOURCESRows` (reviewer, leaf; no subagent dispatch). Lane:
`/home/vgpnk/Projects/shokunin/souji-shokunin`. Attack target: the W1 integration draft bytes —
`corpus/SOURCES.md` rows S124–S127, `corpus/knowledge/git-repo-structure-common-dir.md`,
`census/round-25/sources/`, and the SOURCES validation contract (`CORPUS.md:131–147`, frozen).
Read-only; report written at this path only. No installs (gawk/coreutils/git 2.56.0 present).

## Status

STATUS: PARTIAL — every enumerated row/registry check **passes**; two referenced evidence
artifacts are **missing** (S127's snapshot `gitglossary.7.txt`; the round-25 lesson
`corpus/lessons/round-25.md`), and the landed S125 row deviates from preregistration
amendment-2's source pin (see Findings 1–3). Registry rows themselves: well-formed.

## 1. SOURCES validation re-run (live)

Command: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
→ **EXIT=0**. Output: 34 `W04` (duplicate URL across scopes) lines + `souji	ok	…/corpus/SOURCES.md`.
0 E-codes. W04 is a warning class (`scripts/sources-census.sh:33`), does not fail the lane.
New W04 rows vs base (31, per `ScoutGateCensus` receipt): S124, S125, S126 (same-URL scopes:
S033/S079/S003-S058-S123 respectively), so 31 → 34.

Frozen manual census (CORPUS.md:131–147, run from lane root; exact commands in Appendix):

| check | result |
|---|---|
| row count (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`) | 127 |
| malformed rows `NF!=13` | 0 |
| tier histogram | A=120 B=5 C=2 |
| status histogram | mined=103 queued=15 rejected=9 |
| duplicate ids | none |
| enum / tier-inflation violations (kind/tier/status, A+community) | none |
| mined used-by paths missing on disk | none (109 paths checked) |
| id continuity (S001..S127) | contiguous, no gaps |
| literal `|` inside any cell | none |

Before→after row delta: 123 rows S001–S123 at base (`ScoutGateCensus` receipt, `git diff
--stat a6d2d15 HEAD -- corpus/` empty at that time) → 127 rows now: +3 mined (S124/S125/S126),
+1 rejected (S127); tier A +3, C +1. Consistent with the S124–S127 append.

## 2. Rows S124–S127 (parsed; NF=13, 11 columns)

| id | kind | tier | status | opened | recheck | used-by | checks |
|---|---|---|---|---|---|---|---|
| S124 gitrepository-layout(5) § commondir | docs | A | mined | 2026-10-25 | on-release | corpus/knowledge/git-repo-structure-common-dir.md | snapshot exists; sha256 `dabaeb5b…61cf` matches `census/round-25/sources/SHA256SUMS` and live `sha256sum` |
| S125 git-rev-parse(1) § --git-common-dir | docs | A | mined | 2026-10-25 | on-release | same | snapshot exists; sha256 `24b4c179…8f31` matches |
| S126 git-worktree(1) § DETAILS | docs | A | mined | 2026-10-25 | on-release | same | snapshot exists; sha256 `78e6a56b…d8b2` matches |
| S127 gitglossary(7) | docs | C | rejected | 2026-10-25 | on-release | same | **snapshot missing** (Finding 1) |

- Enums: kind=docs ∈ {spec,docs,paper,code,tool,dataset,talk,book,community,own-work}; tier
  A/A/A/C ∈ {A,B,C}; status mined/mined/mined/rejected ∈ {queued,mined,rejected}. ✓
- Dates: `opened` = 2026-10-25 (ISO, past/present); `recheck` = on-release (valid symbolic
  cadence). E08/E09 clean. ✓
- used-by paths exist on disk (the knowledge entry is present). ✓
- S127 rejection row: teaches reads `REJECTED: no common-directory definition (searched `common`
  over the opened page, 0 matches); flip: a later release adds a located definition` — reason
  present, flip present, status=rejected, tier=C. ✓ (W02 thin-reject did not fire.)

## 3. New knowledge cites only mined S124–S126; rejected glossary not cited as support

`corpus/knowledge/git-repo-structure-common-dir.md`:
- `source:` lines (1–3) cite **S124, S125, S126** (URL + anchor each), all mined. ✓
- Body citations: S124 § commondir, S125 § --git-common-dir (exact probe call), S126 § DETAILS. ✓
- S127 appears only in the entry's `## Gate` REJECT record (line 70); it is never used as a
  support citation. ✓
- No lesson cites S124–S127 (no round-25 lesson exists — Finding 2).
- README F2 row (`corpus/README.md:544`) and Paths bullet (`:156`) name `SOURCES S124–S126`
  with the entry — consistent.

## Findings

1. **S127's snapshot is missing (evidence gap).** S127's anchor names
   `census/round-25/sources/gitglossary.7.txt`; that file does not exist (the directory holds
   only `gitrepository-layout.5.txt`, `git-rev-parse.1.txt`, `git-worktree.1.txt`,
   `SHA256SUMS`; SHA256SUMS has no gitglossary line; `find` finds no gitglossary file in the
   lane). The knowledge entry's Gate grep (`grep -ciE 'common|COMMON_DIR'
   census/round-25/sources/gitglossary.7.txt` → 0) therefore cannot be re-run from committed
   bytes. The 0-match sweep is independently corroborated by W1 receipts (`ScoutSourcesOpen.md`
   F2, `sources-rows-2.md`): 0 case-insensitive `common` matches on the live HTML, installed
   roff and v2.56.0 `glossary-content.adoc`. Missing artifact, corroborated fact.
2. **`corpus/lessons/round-25.md` does not exist.** Contract rule 1 (`CORPUS.md:112–115`)
   requires the round lesson's `## Gate` to record URL, access date and ≤25-word located quote
   for every new row. Both `corpus/SOURCES.md:16` (round-25 provenance) and
   `corpus/README.md:544` (F2 row) point to that lesson file. W1 produced only a draft skeleton
   (`.ufo/waves/round-25/w1/lesson-skeleton.md`, marked "L1 assembles the final lesson") and the
   entry's embedded Gate; the lesson itself is not staged. Integration incompleteness — the
   landing commit needs `corpus/lessons/round-25.md`.
3. **S125 deviates from preregistration amendment-2's source pin.** Amendment 2 (frozen,
   append-only) designated `S125 = git(1) § GIT_COMMON_DIR`; the landed S125 row is
   `git-rev-parse(1) § --git-common-dir` (different URL). The rows, provenance paragraph and
   knowledge entry are mutually consistent; the W1 drafts documented the choice (e.g.
   `sources-rows-2.md` "primary S125", nesting A1/A2 note the prereg frame as "S124/S125 opened
   this round", not documents). No claim predicate, case set or kill rule changed; the entry
   still cites three rows opened this round. Whether amendment-2's pin was controlling is an
   L1 adjudication.
4. **Minor:** provenance line 16 says "S125 with S079" for the URL share, but S125's URL is
   also shared with S091/S099 (`ScoutSourcesOpen` F4). Documentation omission in the provenance
   note, not a row defect. W04 warnings are the only validator output.

## Residual risk / verification gaps

- The glossary negative sweep could not be re-run from the missing snapshot; the corroboration
  is wave-dir draft receipts (uncommitted), not committed evidence.
- The lesson Gate (URLs, access dates, quotes for S124–S127) exists only as W1 draft and as the
  knowledge entry's embedded Gate; no committed lesson to verify.
- Live re-fetch of the four URLs was not re-run by this seat (W1 fetched HTTP 200, sha256-pinned
  on 2026-10-25); URL liveness at write time is per those receipts.
- The `ld`/`--`/`--`-style quoted cells and 25-word quote ceilings were checked at draft time by
  ScribeSources-2 (15 substring matches, word counts 12–25); I re-read the rows but did not
  re-run the quote match against the pages.

## Attack log

- A1 (re-run validator): live `validate` rc 0, 34 W04/0 E; frozen manual census all green. PASS.
- A2 (rows S124–S127 shape): NF=13, no literal pipes, enums, ISO dates, contiguous ids,
  tier/status correct, used-by paths exist. PASS.
- A3 (S127 rejection): reason + flip present, status/tier correct, not cited as support. PASS.
- A4 (evidence completeness): S127 snapshot file missing → FAIL (Finding 1).
- A5 (round Gate): `corpus/lessons/round-25.md` missing → FAIL (Finding 2).
- A6 (frozen sourcing): S125 row ≠ amendment-2 pin → deviation (Finding 3).

## Appendix — exact commands (run from lane root)

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji   # rc 0
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md                                    # 127
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md  # 0
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md   # A=120 B=5 C=2
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md   # mined=103 queued=15 rejected=9
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' corpus/SOURCES.md | sort | uniq -d   # (empty)
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (t !~ /^[ABC]$/) print "tier", i, t; if (s !~ /^(queued|mined|rejected)$/) print "status", i, s; if (k !~ /^(spec|docs|paper|code|tool|dataset|talk|book|community|own-work)$/) print "kind", i, k; if (t=="A" && k=="community") print "tier-inflation", i}' corpus/SOURCES.md   # (empty)
cd census/round-25/sources && sha256sum gitrepository-layout.5.txt git-rev-parse.1.txt git-worktree.1.txt
#   dabaeb5b7001e6c5efcb37f3e2544c7aee86527272d244b9a3a43508d5d61cf6  gitrepository-layout.5.txt
#   24b4c179610d9f4058a269e97d97cc42c84e6ed8b5932c35a8a11148f2318f31  git-rev-parse.1.txt
#   78e6a56be3b5ba04691236507d6d1035463eb48a11e258522a0eccf57945d8b2  git-worktree.1.txt
```
Python parse (127 rows, contiguous S001–S127, no cell containing `|`, S124–S127 enums/dates
checked) and `find . -iname '*gitglossary*'` (no hits) support the above.
