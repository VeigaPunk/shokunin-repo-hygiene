# S66ConnectorOverlap — seat report (souji round 66, post-freeze w1)

Godspeed axes (round-declared): **C1 operability** (receipt-binding, 28-row matrix: env-route
refusals E1–E6, mode-bit recording MOD2/MOD3, symlink retarget SY3), **C2 calibration** (SKILL.md
statement population s1–s5 vs writer bytes; M-ENV kill power). Connector constraint observed: this
seat judges overlap only; no frozen byte, instrument, predicate, or sibling file was touched.
Read-only throughout.

## Deliverables (all under `.ufo/waves/round-66/w1/S66ConnectorOverlap/`)

1. `sibling-overlap.md` — 8-term scan of 20 sibling lanes (`*.md *.py *.sh`, case-sensitive,
   gitignore off), per-hit path:line + ground owner + C1/C2 overlap verdict.
2. `merge-check.md` — shokuknow souji merge package read; term scan zero; no theme overlaps.
3. `considerthese-check.md` — `considerthese/` ABSENT (expected).

## Measured numbers

- Term file-counts (siblings): GIT_CONFIG_COUNT 438 · GIT_OBJECT_DIRECTORY 363 ·
  GIT_REPLACE_REF_BASE 91 · core.excludesFile 72 · status.showUntrackedFiles 4 (fully enumerated) ·
  **RECEIPT-INDEX 0** · receipt writer 64 · st_mode 2823.
- Merge package: 134 rows accepted / 0 refused / 68 knowledge entries; term alternation
  (8 round-66 terms + setuid/setgid/sticky/showUntracked) = **0 hits** across MERGE-REPORT.md,
  MERGE-REPORT.json, SOURCES.append.md, knowledge/. No staged theme touches env routes,
  untracked visibility, or mode bits.
- considerthese: ABSENT.
- Deviation, declared in `sibling-overlap.md`: full per-hit enumeration is feasible only for
  RECEIPT-INDEX (0) and status.showUntrackedFiles (4); volume terms enumerate all same-round and
  all C1/C2-relevant hits plus one representative per incidental class, with complete counts.

## Key findings

1. **No sibling overlaps C1's claim surface.** No sibling receipt writer refuses caller-injected
   git env routes at accept-time, records permission bits, or refuses symlink retarget. kumitate
   r90 A9c is the live sibling defect of exactly E6's shape (GIT_REPLACE_REF_BASE survives
   `gitEnv()`, judged blob redirected, verdict green, RD-5 fix "untested"); kama r35 observed its
   sanitizer passing GIT_CONFIG_*; chousa r61 observed sibling counters comparing digests but
   "never st_mode".
2. **Closest lane: mado r66** — same-round, same variable class (ambient GIT_REPLACE_REF_BASE
   RED/1 → blanket `${!GIT_@}` unset GREEN), but scrub-side on its landing-gate reads, not a
   receipt writer; its `R66ConnSiblings.md:87` already indexes tsukuroi's 16-name REDIRECT_ENV and
   tameshi's full GIT_* removal. Runner-up: kengaku r45–49 (fence refuses repo-local
   `core.excludesFile` at fixture admission — L1's limit on another surface).
3. **RECEIPT-INDEX has zero sibling hits** — souji-internal class token since r62; no sibling text
   can satisfy or shadow C2's lexical needles (`RECEIPT-ENV-*`, `RECEIPT-INDEX-*`), which is a
   C2-positive uniqueness fact.
4. **Canonical env-name prior art**: kumitate r46 `GIT_LOCAL_ENV_VARS` = host
   `git rev-parse --local-env-vars` (git 2.56.0, 15 names) contains all six vars souji refuses;
   the residual 9 (GIT_CONFIG, GIT_DIR, GIT_WORK_TREE, GIT_IMPLICIT_WORK_TREE, GIT_GRAFT_FILE,
   GIT_INDEX_FILE, GIT_PREFIX, GIT_SHALLOW_FILE, GIT_COMMON_DIR) are neither refused by the six-var
   rule nor pinned by the four frozen pins (L2).

## Non-obvious move (compatible synthesis; no frozen byte changes)

**Name the residual `--local-env-vars` set as the leading candidate for a named limit / next-round
E-row class**, in SoujiR66's round report (not in SKILL.md, not in the matrix, not in the prereg —
post-freeze). Evidence: (a) kumitate r90 A9c — the env survives a partial scrub and redirects what
the verdict binds, while output stays green; (b) souji's own r62 reviewer probe — inherited
GIT_INDEX_FILE is honored by the writer's git children (rc 2 "cannot read index flags … index file
smaller than expected", fail-closed today only because the env value was malformed; a *valid*
caller-supplied index would be the store the clean-tree claim reads); (c) kake r28 gate-envfix
repaired false-cleans by dropping exactly the `--local-env-vars` set; (d) chousa r53 already
documents "export no GIT_DIR/GIT_WORK_TREE/GIT_OBJECT_DIRECTORY" as a fleet operator precondition.

- Affected axes: improves C1 (declares what the refusal does not cover — converts silent exposure
  into a named bound, same epistemic status as frozen L1–L5: named, not counted as passes); cannot
  harm C2 (no population/needle/SKILL.md byte proposed for change).
- Risks: (1) if the candidate writer's `git()` helper already pins more than the four frozen pins,
  the residual list overstates — the design reviewer should check the candidate bytes before
  adopting the wording; (2) must be phrased as a named limit/next-round candidate, never as a pass
  or as a defect in the frozen matrix; (3) review/mut seats should not widen this round's scope to
  probe it (post-freeze rule).
- Verification (not runnable by this seat — no candidate-dependent checks assigned): the accepting
  seat confirms the six-var refusal + four pins in the candidate bytes, then one scratch probe
  (caller sets GIT_INDEX_FILE to a valid crafted copy of the lane index on an honest fixture):
  receipt written ⇒ limit is real and worth naming; refused ⇒ drop the proposal.
- Routing: pointer sent to S66ReviewerDesign; SoujiR66 holds the integration seat.

## Tooling / scratch / hygiene

- Tools installed: none. No pacman/uv/npx activity; no host state touched.
- Scratch `/fast/scratch/hyaku/souji-r66/S66ConnectorOverlap/` created, unused (no fixture was run),
  left empty for trap-free cleanup. No git/jj command was executed anywhere. Writes were limited to
  this seat's wave dir and the report file.

Report: .ufo/waves/round-66/w1/S66ConnectorOverlap.md
