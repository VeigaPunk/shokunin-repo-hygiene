# SourceBookkeeping — round-13 wave w1 (seat SoujiR13.SourceBookkeeping, scribe)

## Behaviour
Drafted proposed S005/S006 status and used-by cells, a conditional S034 timeout row, and the
before33 → after34 census expectation. Nothing was applied to `corpus/SOURCES.md`.
No sources were opened by this seat. No quotes were added. Round-12 quotes are cited only as round-12 observations.

## Gates
- Census script exists and is unrun by this seat: `census/round-12/sources-census.sh`.
- Baseline conflict: the stored `census/round-12/sources-census.txt:4` says mined=18 queued=13.
  The current registry rows `corpus/SOURCES.md:32-33` (S024, S025) read queued, giving a manual count of
  mined=16 queued=15 rejected=2. The stored file predates the post-review edits. UNRESOLVED; L1 must
  re-run the census.
- Mined-path gate: flipping S005/S006 to mined requires the F2 entry file to exist first
  (`census/round-12/sources-census.sh:16`).

## Touched surfaces
- Written: `census/round-13/source-draft.md` (new file; directory did not exist).
- Written: `.ufo/waves/round-13/w1/SourceBookkeeping.md` (this report).
- Not touched: `corpus/SOURCES.md`, `LOG.md`, the swarm registry, `census/operator-sweep-20261019/`, fleet repo, sibling repos.

## Findings
1. Baseline inconsistency (fact): `sources-census.txt:4` (mined=18 queued=13) disagrees with
   `corpus/SOURCES.md:32-33` (S024/S025 queued). Inference: stale after post-review edits
   (`census/round-12/postreview.md` row 3). Needs a fresh census run.
2. S005/S006 are queued with used-by `—` (`corpus/SOURCES.md:13-14`). Conditional flip to mined,
   with used-by set to the F2 entry path, is drafted in `census/round-13/source-draft.md` section 2.
3. S006 teaches cell calls the doc "the doc basis for a read-only census". The round-12 quote
   (`census/round-12/sources-gate.md:41`) supports only index refresh. [INFERENCE] the "read-only"
   wording overstates; the SourceLocks report must confirm before any change.
4. S034 is the next unused id (S033 is the maximum, `corpus/SOURCES.md:41`). The draft row has PENDING
   cells that make the census fail closed until filled.
5. Expected after34 (target scenario, F2 + S034 admitted): rows 34, malformed 0, A=30 B=3 C=1,
   mined=18 queued=14 rejected=2. Other scenarios are in the draft's section 4.
6. The SOURCES.md Paths section (`corpus/SOURCES.md:45-47`) has no F2 line, although C3 targets an F2 entry.
   Adding one is L1 bookkeeping, outside this seat's write set.

## Out of scope
- Opening any source (SourceRepo, SourceLocks, SourceTimeout own that).
- Admitting or writing the F2 entry (FrontierDraft / L1).
- The QUALITY and corpus README count claims (`census/round-12/postreview.md` row 5 lists the README "33 rows" without command).

## Tools
No tools installed or upgraded by this seat.

## Final checks for L1 (not run by this seat)
- `bash census/round-12/sources-census.sh` from the lane root; expect target output in draft section 6.
- `grep -c PENDING corpus/SOURCES.md` → 0 before S034 is admitted.
- `test -e` on the admitted F2 entry path before the S005/S006 flip.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat -- corpus/SOURCES.md` → only the intended rows change.

## Artifact paths
- /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/source-draft.md
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-13/w1/SourceBookkeeping.md
