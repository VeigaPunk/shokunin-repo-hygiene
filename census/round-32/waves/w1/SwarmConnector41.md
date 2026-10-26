# SwarmConnector41 — souji round 32 wave 1, sibling-overlap scan

## Status
STATUS: PASS — read-only sibling-overlap scan of the round's three surfaces completed for all
20 non-souji lanes plus `scripts/hyaku/*.sh`; no contested scope found (C3's cruft/object-mtime
ground is unclaimed), delivery `deliver-sibling-overlap.md` written to the wave w1 dir; no
scratch was created (no clones/downloads needed), so nothing to clean; no tools installed.

## Evidence
Commands (all read-only; grep tool over the fleet root, souji excluded from lane scans):
- `grep [cruft|pruneExpire|mtimes]` over `*/PROVINCE.md`, `*/SKILL.md`, `*/corpus/README.md`,
  `*/corpus/knowledge/*.md` (20 lanes) + `scripts/hyaku/*.sh`; paged to completion
  (44 knowledge files). Result: zero `cruft`/`pruneExpire` hits anywhere; `mtimes` hits are
  incidental metadata claims (listed in Findings 2-6).
- `grep [cruft]` over the same top-doc set: no matches.
- `grep [/var/tmp|TMPDIR|bwrap|tmpdir]` and `grep [capability]` over the same set, paged
  per lane group; hits transcribed in the delivery file (27 numbered items).
- Reads of the frozen preregistration
  (`souji-shokunin/census/round-32/records/preregistration.txt`, base 85b61a151923986e7e6b48f7084b9122561b5f3d)
  and of c3-contract.txt, c1-items.tsv, c2-items.tsv to fix the three surfaces before scanning.
- Verbatim quotes (<=25 words, no pipes) are inline in the delivery file, e.g.:
  - kumitate `jj-workspace-seat-containment.md:102`: "abandoned commits still remain in the
    repository's object store and op log; only `jj op abandon` + `jj util gc` or a separate
    clone excludes them from storage".
  - tsukuroi `package-state-plane.md:79-80`: "pacman preserves upstream file mtimes on
    download; **mtime ≠ datetime of the local sync**".
  - kaidoku `SKILL.md:449`: "else `/var/tmp` (`/tmp` never — EDQUOT hazard)".
  - mori `SKILL.md:605`: "do not let an invalid TMPDIR fall back to /tmp".
  - tameshi `executable-self-assessment.md:7`: "A standing capability row says what a tool
    can do and quotes what its command printed."
  - mori `source-drift-content-anchor-r38.md:33`: "Every path the SCORECARD capability row
    cites must resolve at the measured revision from the repository root."
  - kama `SKILL.md:1030`: "honors an existing caller TMPDIR rather than a host-specific
    shared root".

## Findings
1. C3 ground is uncontested: no sibling document claims cruft-pack handling, `gc.pruneExpire`,
   or per-object `.mtimes` clock behavior under `git gc`. Nearest neighbor is kumitate's jj
   abandoned-object persistence claim (`jj-workspace-seat-containment.md:102`), which covers
   persistence/exclusion only and is compatible with C3's planned entry.
2. Fleet `scripts/hyaku/disk-guard.sh:291-293,976` uses the exact `${TMPDIR:-/var/tmp}`
   fallback pattern C2 flags, and passes `TMPDIR` explicitly to a child at `:936-937`;
   outside souji's write scope (reported, not absorbed).
3. Norm split on scratch locations: kaidoku (SKILL.md:449; knowledge entries r3/r4/r11/r12)
   and kotodama (SKILL.md:456-459) treat /var/tmp as the sanctioned scratch; revenger
   (SKILL.md:180-182,471-475) and historical mado use /tmp; kama, mori, kake, tabi, kotoba
   claim TMPDIR-honoring on their own tools. Directionally opposite norms, all lane-owned;
   none claims souji's tools.
4. mori's r44 write-scope supersessions (`SKILL.md:193-196`) show sibling prior art of the
   exact overclaim class C2 catches ("writes only under the caller TMPDIR" was false because
   counters ran rows through `bash -c` with the caller's env).
5. C1's cell-binding class has sibling instruments on their own cards (tameshi executable
   self-assessment; mori capability-path resolution; kama repertoire audit; chousa
   line/receipt binding counters) — methodological overlap, no contested repository.
6. tsukuroi `SKILL.md:2754` strips ambient TMPDIR from probe children (SentinelAllowKeep);
   C2 requires children to inherit caller TMPDIR. Different subjects; flagged so C2's rule
   is not read as a fleet-wide convention.
7. No lane claims ownership of souji's counters/SCORECARD/tools; per the frozen preregistration
   causal separability sections, no wave-2 falsifier ground is pre-empted by these neighbors.

## Attack log
None (connector seat; no counter attack filed).

## Deliveries
- `souji-shokunin/.ufo/waves/round-32/w1/deliver-sibling-overlap.md` (delivery file).
- This report: `souji-shokunin/.ufo/waves/round-32/w1/SwarmConnector41.md`.
