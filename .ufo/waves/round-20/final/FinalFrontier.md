# FinalFrontier — UFO-FSD Connector: S089–S095 Gate/Catalogue Accounting and Knowledge Boundary Synthesis

**Seat:** SoujiR20-2.FinalFrontier (connector, leaf).
**Subject:** Pinned-build attack on S089–S095 Gate/catalogue/search accounting; admitted paths versus corrected F5 entry; no source rows mistaken for knowledge expansion.
**Pinned target commit:** `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`.
**Preregistered baseline:** `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`.
**Constraint:** Read-only inspection; no subagent dispatch; no target-code execution; no edits to production or sibling lanes; author-side advisory only, not non-author closure.

---

## 1. Declared Axes

1. **Calibration (C1, lowest non-retired axis: score 7):** Truthfulness and exactness of authorizations, receipts, source accounting, rejection catalogues, and authority-layer alignment. C1 repair requires explicit parsed-write grants, consumed-byte audit receipts, and precise documentary claims.
2. **Operability (C2, score 8):** Bounded caller input boundaries (`tools/souji-rev-pin.py` raw-blob comparison and fail-closed enumeration) and clean consumer migration to full durable 40-hex IDs. Must not be harmed or relaxed.
3. **Coverage (score 8; legacy delta 0):** Ground and frontier tracking across F1–F5. Round 20 pre-registers zero coverage claims; admitted knowledge count must remain exactly 7, uninflated by new source rows or existing-entry edits.

---

## 2. Evidence and Explicit Contradictions

Inspection of named artifacts at pinned commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` reveals four explicit structural contradictions and accounting discrepancies across the gate, source registry, and lesson documentation:

### A. Chronological Inversion and Subtotal Contradiction in `corpus/lessons/round-20.md`
In `corpus/lessons/round-20.md`:
1. Lines 24–36 (`## Gate / ### Actual source decisions opened this round`) render a single unified Markdown table containing **all seven** opened rows: S089, S090, S091, S092, S093, S094, and S095.
2. Immediately below this 7-row table (lines 37–41), the narrative states:
   > "Registry changes: S089–S093 absent→opened2026-10-21; all tierA within the stated scope; S089/S091/S092/S093 mined, S090 rejected... New rows A+5/B+0/C+0 are not five knowledge entries. Search accounting: five distinct pages identified/screened, four admitted documentary decisions, one rejected cleanup-authority candidate..."
   This paragraph directly contradicts the table above it by accounting for only 5 rows (S089–S093) rather than the 7 displayed.
3. Lines 42–53 (`### Completed source-decision accounting`) then state:
   > "S094 and S095 were also opened/reopened by the replacement L1 on 2026-10-21... The current curation is S089–S095: tier A+7, B+0, C+0; six mined and one rejected. The seven distinct pages were identified/screened this round; six documentary decisions were admitted and one cleanup-authority candidate rejected."
4. However, after `## Held boundaries` (lines 54–58), lines 59–73 insert:
   > "### Additional located source correction: S038 → S094 ... Combined source accounting: 6 distinct pages, 5 admitted scoped documentary decisions, 1 actual rejected cleanup-authority candidate; new rows A+6/B+0/C+0, mined+5/rejected+1. These supersede the five-page subtotal above, not its individual decisions."
   This creates an untenable ordering: the intermediate 6-page subtotal (`A+6`, S089–S094) appears *after* the final 7-page total (`A+7`, S089–S095) in the lesson body, and claims to supersede the 5-page subtotal from line 37. Meanwhile, S095 lacks any standalone located quote or opening section comparable to S094's §23.6 treatment.

### B. Contrast with Monotonic Search Log in `corpus/SOURCES.md`
In contrast to the lesson's out-of-order text, `corpus/SOURCES.md` records three monotonic chronological search blocks:
- Lines 130–136 (`Round-20 repair-source search`): 5 distinct pages identified/screened, 4 admitted (S089, S091–S093), 1 rejected (S090).
- Lines 137–141 (`Round-20 S038 drift repair`): 1 distinct page screened, 1 admitted (S094). Cumulative: 6 distinct pages, 5 admitted, 1 rejected.
- Lines 142–148 (`Round-20 fd access attribution`): 1 distinct page screened, 1 admitted (S095). Cumulative: 7 distinct pages, 6 admitted, 1 rejected.
The lesson text failed to integrate these three increments monotonically, resulting in fractured prose where `A+5`, `A+7`, and `A+6` coexist in disjoint sections.

### C. Admitted Knowledge Paths vs. Corrected F5 Entry
As measured by `census/round-13/count-claims.py 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`:
- Total paths under `corpus/knowledge/*.md` satisfying the admission prefix (`source:`, `verified-at:`, `recheck:`) and lacking `## Admission status — HELD`: **exactly 7**.
  1. `dupe-finders-detect-then-act.md` (F3)
  2. `git-auto-maintenance-prunes-worktrees.md` (F1)
  3. `git-grace-periods-and-expire-to.md` (F1)
  4. `git-repo-structure-readonly.md` (F2)
  5. `jj-colocation-receipts.md` (F1-jj)
  6. `process-residue-observations.md` (F5)
  7. `trash-spec-restorable-quarantine.md` (F4)
- Held paths: `quarantine-same-filesystem-rename.md` (K5, held since r12).
- Ledger: `obsidian-ledger.tsv`.
- In Round 19, `process-residue-observations.md` was admitted as the initial F5 observation entry (increasing count from 6 to 7).
- In Round 20, **zero** new knowledge paths were admitted.
- Instead, `process-residue-observations.md` underwent three layers of precision correction:
  1. Lines 101–130: Narrowed read/enumeration scope, bound implementation hashes (`tools/souji-proc-census.sh`, `tests/fixtures/r18-proc-census.sh`, `census/round-18/leak-count.py`), and substituted S086–S088 for superseded S083–S085 teachings.
  2. Lines 131–138 (Q43): Explicitly defined the 512-hop bounded parent-chain snapshot exclusion of recognized self/descendants and unreadable/racing data skips.
  3. Lines 139–147: Mapped `proc_pid_fd(5)` symlink access to S095 (`PTRACE_MODE_READ_FSCREDS`).
None of these changes adds an admitted path or expands coverage ground; they refine an existing Core observation entry.

### D. Conflation Risk: "No Knowledge Growth" vs. Active Quality Improvement
Recovery report `CorpusAdmission.md` accurately identified that line 140 of `corpus/SOURCES.md` ("no knowledge growth") was terminologically overbroad. Round 20 actively improved knowledge quality through rigorous F5 boundary corrections, even while adding zero new knowledge entries. However, confusing source row additions (`SOURCES.md` 88→95, delta +7) with knowledge expansion would violate Q23 and SCORECARD calibration.

---

## 3. Affected Axes

- **Calibration (C1):** Direct positive impact. Harmonizing the source-decision progression (S089–S095) eliminates internal numeric contradictions (`A+5` vs `A+7` vs `A+6`) and accurately states the 6-admit / 1-reject curation. Calibrates the distinction between source rows, existing-entry updates, and admitted paths.
- **Operability (C2):** Preserved without harm. Does not alter `tools/souji-rev-pin.py` durable revision checks, `input_snapshot` blob comparisons, or the full-ID consumer index in `corpus/README.md`.
- **Coverage:** Preserved without inflation. Reaffirms exact admitted knowledge count at 7 (delta 0), preventing 7 new source rows from being scored as coverage expansion.

---

## 4. Proposed Move: Unified 4-Tier Provenance and Accounting Boundary Synthesis

Synthesizing `CorpusAdmission`'s classification, `F5Enumeration`'s multi-authority harmonization, and `SourceRefs`/`SourceTimeout`'s attribution disciplines, we propose one bounded, non-obvious move:

**Formalize a 4-Tier Provenance and Accounting Contract in the landing documentation and verification harnesses:**

1. **Tier 1 — Source Decisions (Screened / Admitted / Rejected):**
   - Unify the Gate accounting in `corpus/lessons/round-20.md` into one single, monotonically increasing record matching `corpus/SOURCES.md` search logs:
     - Total pages screened: **7**
     - Admitted documentary decisions: **6** (S089 Git worktree env, S091 rev-parse verify, S092 for-each-ref filtering, S093 diff quiet exit, S094 timeout 9.12 locator, S095 fd access-mode).
     - Explicitly rejected cleanup/rewrite candidate: **1** (S090 `git-filter-branch` warning, refused as cleanup authority).
   - Excise the out-of-order `A+5` and `A+6` narrative remnants from `round-20.md`, presenting the final curation `S089–S095: tier A+7, B+0, C+0 (6 mined, 1 rejected)` once and conclusively.
2. **Tier 2 — Admitted Knowledge Paths (Corpus Inventory):**
   - Assert in acceptance verification (`census/round-20/run-acceptance.py`) that the admitted knowledge path set equals the invariant 7-element set: `{dupe-finders, git-auto-maintenance, git-grace-periods, git-repo-structure, jj-colocation, process-residue, trash-spec}`.
   - Enforce that `admitted_entries_delta == 0` for Round 20.
3. **Tier 3 — Existing-Entry Precision Corrections (Quality without Expansion):**
   - Explicitly classify edits to existing knowledge files (specifically the three appended sections in `process-residue-observations.md`) under a distinct verification category: `Existing-Entry Quality Refinement`.
   - Prevent verifiers from interpreting "no knowledge expansion" as "zero learning", while barring authors from counting precision edits as coverage points.
4. **Tier 4 — Authority Exclusion Alignment:**
   - Verify that the recognized-self/descendant exclusion (512-hop parent chain snapshot, Q43) and unreadable/racing skip wording is aligned across all five governing files: `SKILL.md:143-149`, `PROVINCE.md:147-152`, `corpus/README.md:319-324`, `corpus/QUALITY.md:107-111` (Q43), and `process-residue-observations.md:131-138`.

---

## 5. Risks and Second-Order Effects

1. **Risk of Accidental Coverage Claims:** If a verifier sees 7 new rows in `corpus/SOURCES.md`, they might infer a coverage advance. The Tier 2 invariant explicitly guards against this by pinning admitted markdown entries to 7.
2. **Risk of Disregarding Legitimate Quality Work:** Stating "no knowledge growth" risks trivializing the genuine F5 corrections (S086–S088, S095, Q43). Tier 3 properly credits quality refinement without inflating coverage.
3. **Risk of Desynchronizing Lesson History:** The intermediate `A+5` and `A+6` subtotals reflect actual coordinator drafts during wave progression. Collapsing them into a clean `A+7` summary must preserve the search log's historical audit trail in `corpus/SOURCES.md`.
4. **Substrate and Verification Surface:** The proposed move requires zero changes to target code, runtime dependencies, or host packages. It is purely an authority-accounting and acceptance-contract refinement.

---

## 6. Verification and Deterministic Oracle

To verify this synthesis without executing target code:
1. **Source Accounting Oracle:**
   - Parse `corpus/SOURCES.md` registry table: verify rows S089–S095 exist, all tier A, exactly 6 `mined` and 1 `rejected` (`S090`).
   - Validate against `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`: confirm exit 0 with only expected W04 scope-duplicate notices.
2. **Knowledge Count Invariant Oracle:**
   - Execute `python3 census/round-13/count-claims.py 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`:
   - Assert `admitted_entries == 7`.
   - Assert `sources == 95`.
   - Assert `statuses.rejected == 3` (historical S030, S032 + current S090).
3. **Text-Contract Consistency Check:**
   - Assert that `Q43`, `SKILL.md`, `PROVINCE.md`, `README.md`, and `process-residue-observations.md` all state the bounded parent-chain exclusion and unreadable/racing skips without claiming exhaustive enumeration.

---

**STATUS:** Evaluated; scoped connector move formulated with exact pointers and invariants; no runtime execution performed. Ready for L1 post-wave integration.
