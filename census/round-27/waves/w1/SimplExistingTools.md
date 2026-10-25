## Status
STATUS: PARTIAL — identified historical/duplicate candidates, but no removals are safe to recommend from text grep alone; broad historical callouts remain.

## Evidence
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `e78ac7c4837b81b634db4a927605a751a7f006ba`.
- `git -C ... ls-files 'tools/impl-*' 'tools/cand-*' 'tools/souji-round9-s18*' 'tools/*counter*' 'census/*counter*'` lists the candidate families as tracked.
- Literal grep across the lane finds many historical references in `.ufo/waves/round-13/w1/FixtureAudit.md` and later evidence. It is not semantic proof of live callers.

## Findings
1. `tools/cand-census-01.sh` — superseded as a candidate: `census/round-10/final-30.json:61-63` records its selftest with 2 failures, while `cand-census-02/03` report green. `census/round-11/cert-13.json:320-323` says 01 matches the failed in-place rewrite and 02/03 have green selftests. Historical evidence explicitly names it; grep found references, so removal is NOT established safe.
2. `tools/cand-census-07.sh` — failed candidate: `census/round-11/cert-09.json:31-36` records it as a landed candidate; `census/round-11/cert-13.json:323` records its empty/near-empty/CRLF failure. Historical references exist; removal NOT established safe.
3. `tools/souji-round9-s18-test.py` — potentially duplicate battery: `.ufo/waves/round-13/w1/FixtureAudit.md:60-62` describes the round-9 battery; same document lines 241-244 explicitly calls it redundant with `cand-merge-selftest.sh` but requires retaining historical reference artifacts. Removal is NOT safe under that explicit retention instruction; grep also finds many historical references.
4. `tools/impl-*.sh`, `tools/souji-*.impl-*.sh`, `tools/*r9-s18*.sh` — candidate lineage, not demonstrably dead. Historical rounds and evidence cite specific variants (e.g. `census/round-11/cert-09.json:50-53`; `.ufo/waves/round-15/w1/GitSourceHooks.md:111`). Grep finds references; do not remove.
5. `census/round-26/c1-counter.sh`, `c2-counter.sh`, `c3-counter.sh` — likely round-local frozen counter snapshots, not duplicates proven obsolete. No superseding round-27 counter-script equivalence was established; retain absent evidence they are unused. Grep of historical mentions is not semantic proof.

## Attack log
- Literal grep is insufficient for the requested “nothing references it” proof. No language server references result was available in this read-only leaf assignment; therefore no candidate is certified safe to delete. No deletions made.