# ScoutFrontierClaim — F2 frontier/core determination after C3 (W2, round 25)

STATUS: PASS

Scope: read-only inspection of PROVINCE.md and corpus/README.md in the lane working tree
(base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe; W1 draft uncommitted). No edits made.

## Determination

**F2 remains frontier. It does NOT move to Core.** README and PROVINCE agree.

The promotion rule (PROVINCE.md:61): "each row moves to Core only with an admitted
`corpus/knowledge/` entry and a SKILL rule; index in `corpus/README.md`".

After C3, of the two required conditions:

1. **Admitted knowledge entry — present.** `corpus/knowledge/git-repo-structure-common-dir.md`
   exists (untracked, W1 draft), front-matter `ground: F2`, sources S124/S125/S126, with a
   `## Gate` ADMIT section. It is named in the README Round-25 F2 row's entries column (Q56).
2. **SKILL rule — absent.** `SKILL.md` is byte-identical to base (git diff vs a6d2d15
   returns 0 lines; SKILL.md is not in the working-tree modified set). Its only F2 section,
   `## Repository structure census (F2, bounded r13 capability)` (SKILL.md:245-265), still
   documents the r13 probe capability and cites `git-repo-structure-readonly.md` (S035-S037).
   No common-git-dir no-write-manifest rule and no colocated-vs-plain precondition rule were
   added; those rules live only in the knowledge entry's decision table, not in SKILL.md.

Because the SKILL-rule half is missing, the F2 row stays frontier. The lane's own SCORECARD
round-25 append-only correction states the same: "Sources S124–S127 are opened this round.
New F2 knowledge on existing frontier ground does not promote F2 to Core." (SCORECARD.md
Round 25 append-only corrections, last bullet).

## Evidence (located quotes)

- PROVINCE.md:61 — "each row moves to Core only with an admitted `corpus/knowledge/` entry
  and a SKILL rule; index in `corpus/README.md`".
- PROVINCE.md:66-68 — F2 row (under `## Core / Frontier / Adjacent`): "F2 repository size
  census (`git repo structure`, `count-objects`) — bounded structure probe and isolated
  write-safety fixture acquired r13; whole-workspace size attribution and unreachable-object
  census remain frontier."
- PROVINCE.md:94-97 (Round 13 boundary refinement) — "Core now includes the bounded read-only
  `git repo structure --format=lines` probe … This reports reachable objects, not recoverable
  disk space and not removal authorization. F2 as a whole stays frontier."
- PROVINCE.md:143 (Round 19 boundary refinement) — "F1, F2, F3 and F4 are unchanged."
- PROVINCE.md is unchanged from base (not in `git status --porcelain` modified set) — no
  round-25 amendment exists in it.
- corpus/README.md:544 (Round 25 F2 coverage-map row) — status cell: "frontier; five sourced
  entries now cover the read-side facts, r24 debris counter, and r25 common-directory
  envelope."
- corpus/README.md:548 (`### Frontier (r25)`) — "F2 — the common-directory no-write envelope
  and colocated/plain precondition are now measured for the r13 structure probe. Next: one
  lane-bound structure baseline from a plain `--no-local` clone … Size attribution by
  object/path and any fleet figure remain frontier/unclaimed."
- SKILL.md:245 — "## Repository structure census (F2, bounded r13 capability)" — the only F2
  section; no common-dir/colocated rules in it.

## Findings

1. F2 remains frontier in both documents: README Round-25 row status = "frontier" and the
   r25 Frontier list retains F2; PROVINCE retains F2 under Frontier (unchanged from base).
2. README and PROVINCE agree; no disagreement found. PROVINCE simply has no round-25 section
   at all (still ends at the Round-21 privacy boundary), so its F2 row is the r12-era row +
   r13/r19 refinements — all frontier.
3. The C3 deliverable was a frontier *move* (entry + README map row + fixture cases), not a
   Core promotion: the admission rule's second half (SKILL rule) was not landed. Even if the
   entry is considered admitted, the rule is conjunctive, so no promotion.
4. Nuance: since r13, a bounded subset of F2 — the read-only `git repo structure` probe — is
   already Core (its own entry + SKILL section). C3 extended the probe's envelope coverage
   (common-dir manifest, colocated/plain precondition) inside that same probe surface but
   added no SKILL rule; the F2 row as a whole remains frontier, and the r25 Frontier next-step
   (lane-bound plain-clone baseline; size attribution; fleet figure) is explicitly unclaimed.
5. Forward-looking: if a future round adds a SKILL rule for the common-dir/colocated
   envelope (and the entry stays admitted), the rule's conditions would then both be met for
   that surface — but that change is not present in this tree.

## Attack log

- Inspected PROVINCE.md (full, 172 lines) and confirmed no round-25 modification.
- Inspected corpus/README.md in full; read the Round-13/23/24/25 F2 rows and the
  `### Frontier` sections (r23/r24/r25).
- Read the C3 knowledge entry `git-repo-structure-common-dir.md` in full (Gate/ADMIT,
  ground, decision table).
- Ran `git -C <lane> diff a6d2d15 --stat`: 20 files changed; SKILL.md and PROVINCE.md
  absent from the set; `git diff a6d2d15 -- SKILL.md PROVINCE.md | wc -l` = 0.
- Searched SKILL.md for common-dir/colocated/F2/frontier references: only the r13 F2
  section and checklist mention of `--git-common-dir`; no new rule.
- Read preregistration amendments 1–3 (append-only; confirm C3 is a frontier move with no
  Core-promotion intent) and SCORECARD.md's Round-25 measurements + append-only corrections
  (which explicitly record "New F2 knowledge on existing frontier ground does not promote F2
  to Core").

Remaining unknowns: none for the stated question. (The round is not yet committed; admission
of the entry and the C3 claim are L1's judgment, but that does not affect the frontier/core
classification, which depends on the rule conditions in the current documents.)
