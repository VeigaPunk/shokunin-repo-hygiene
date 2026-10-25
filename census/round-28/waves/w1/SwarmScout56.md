# F4 screen — staged package for the origin-record-primitives theme (round 28, attempt 1)

## Status
STATUS: PASS — staged package screened for the F4 theme; C2's two admissions (origin-record-exclusivity-r28.md, origin-record-durability-r28.md) are confirmed the only genuinely new in-scope origin-record entries; all other in-scope candidates are already adopted or previously screened out with documented gate reasons; no counter/claim discrepancy found.

## Evidence
- `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` — 140 lines, rows S109–S242 (134 proposed rows), 11-column schema. Read full file this run (lines 1–140).
- `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/` — 68 staged knowledge entries (glob, this run).
- `/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md` — "proposed knowledge entries: **68**" (line 7).
- Lane registry `corpus/SOURCES.md` — 135 rows (grep `^| S` count), last ids S210/S211, used-by `corpus/knowledge/origin-record-mechanism-set-r33.md` / `corpus/knowledge/origin-record-writer-r27.md`. Base `3a2a80d0d18940a5e352ebc526da22a57dad83c4`, `661 status` shows only .ufo/waves/round-26/w1/* mods + untracked C1/C3 staging (pre-capture state).
- Lane `corpus/knowledge/` listing (this run): holds `origin-record-mechanism-set-r33.md`, `origin-record-writer-r27.md`, `quarantine-origin-record-fields-r24.md`, `quarantine-staging-no-copy-r23.md`, `quarantine-same-filesystem-rename.md`, `trash-spec-restorable-quarantine.md`; does NOT hold `origin-record-exclusivity-r28.md`, `origin-record-durability-r28.md`, `origin-record-format-gvfs-r26.md`, `quarantine-origin-record-fields-r23.md`, `quarantine-staging-no-copy.md`, `quarantine-staging-no-copy-r24.md` (grep `origin-record-exclusivity|origin-record-durability|format-gvfs` over the lane matches only preregistration.txt C2 text — no corpus file).
- Grounded F4 count in lane = 4: `origin-record-writer-r27.md` ("ground: F4 — restorable quarantine (the reference writer's per-item origin-record sequence)"), `origin-record-mechanism-set-r33.md` ("ground: F4 — restorable quarantine (the distinct roles of reservation, content write, and publication in this reference implementation)"), `quarantine-origin-record-fields-r24.md` ("ground: F4 — restorable quarantine (the read side of a per-item origin record)"), `quarantine-staging-no-copy-r23.md` ("ground: F4 — restorable quarantine (the staging primitive: no-clobber rename)"). → 4→6 after the two admits = C2 counter consistent.
- Pre-existing gate decisions in adopted lane entries:
  - `quarantine-origin-record-fields-r24.md` (:53-56): staged r23 package file is "not adopted in this lane, so it has no lane path"; r24 carries the restore-side requirement r23 lacked.
  - `quarantine-staging-no-copy-r23.md` Gate REJECT: staged r24 "does add EXCHANGE/WHITEOUT and extra mounts, but none of that is wired to a consequence this lane's staging plan can use".
  - `origin-record-writer-r27.md` Gate REJECT: staged S119 zh-Hans "decision-time version state is unrecoverable without a pinned snapshot and quote" — the C2 disposal of staged S119 is already recorded, consistent.

## Findings
1. **The two C2 admissions are genuinely new** — absent from lane corpus; both are in-scope F4 origin-record entries; staged heads confirm `ground: F4` and POSIX.1-2024 sourcing (exclusivity: S158 open()/S159 rename(), "The origin record needs O_EXCL and rename, not rollback"; durability: S173 fsync(), "Atomicity is not durability, and durability is the platform's to promise").
2. **`origin-record-format-gvfs-r26.md` is in-scope but unadopted and NOT in the frozen C2 admit set** — adopting it would exceed the claim (counter "grounded F4 4→6" counts only the two r28 entries). Leave staged; note for a later round.
3. **All other in-scope candidates are either already adopted (4) or previously screened out with documented gate reasons (3)** — see table; no re-adoption needed.
4. **Out-of-scope rejects (18)** — duplicate-verdict (2), near-duplicate (5), community-reclamation (5), GitLab housekeeping (6); plus 40 other staged entries belong to F1/F2 themes (prune-*, fleet-*, garbage-*, git-grace-*, reclamation-*, count-objects-*, git-auto-maintenance-*, repo-size-*, self-hosted-reclamation-shapes, community-literature-*), outside the F4 screen.
5. **No counter discrepancy** — registry 135 (ends S211) + 3 minted rows S212/S213/S214 = 138, matches "registry rows 135→138"; F4 4→6 matches; notes S119 disposal already present in adopted writer entry's gate.

## Screen table — in-scope F4 candidates (origin-record-* / quarantine-* / trash-*)
| staged entry | staged round | lane status | note/reason |
|---|---|---|---|
| origin-record-exclusivity-r28.md | r7 | **NEW — adopt (C2 admission 1)** | not in lane corpus; re-grounded from POSIX.1-2024 open() |
| origin-record-durability-r28.md | r8 | **NEW — adopt (C2 admission 2)** | not in lane corpus; re-grounded from POSIX.1-2024 fsync() |
| origin-record-format-gvfs-r26.md | r5 | NEW — NOT in C2 admit set | in-scope but unclaimed; leave staged |
| origin-record-mechanism-set-r33.md | r13 | already adopted | lane corpus has it (S210/S211, verified 2026-10-25) |
| origin-record-writer-r27.md | r6 | already adopted | lane corpus has it (S152) |
| quarantine-origin-record-fields-r24.md | r3 | already adopted | lane corpus has it; amends trash-spec-restorable-quarantine.md |
| quarantine-origin-record-fields-r23.md | r2 | not adopted — superseded | adopted r24 documents it as not adopted; r24 has the restore-side requirement r23 lacked |
| quarantine-staging-no-copy.md | r1 | not adopted — superseded | base entry; lane holds newer r23 variant |
| quarantine-staging-no-copy-r23.md | r2 | already adopted | lane corpus has it; ground F4 |
| quarantine-staging-no-copy-r24.md | r3 | not adopted — REJECTED at gate | reject recorded in adopted r23's Gate (EXCHANGE/WHITEOUT not wired to a consequence) |
| (no staged trash-* files) | — | — | lane-native `trash-spec-restorable-quarantine.md` (S022/S023) is not part of the staged package |

## Out-of-scope rejects (one-line reasons)
| staged entry | reason |
|---|---|
| duplicate-verdict-identity.md | duplicate-verdict receipt class (identity rule), not origin-record primitives |
| duplicate-verdict-taxonomy-r24.md | duplicate similarity taxonomy; different theme |
| near-duplicate-threshold-source-r34.md | operator-ruling threshold question, not F4 |
| near-duplicate-literature-identity-r33.md | bibliographic identity of threshold paper |
| near-duplicate-relations-r29.md | resemblance/containment relations |
| near-duplicate-operating-point-r28.md | measured threshold operating point |
| near-duplicate-threshold-r28.md | published threshold values |
| community-reclamation-practice-r28.md | community recipe practice records, not F4 |
| community-reclamation-practice-extended-r28.md | same |
| community-reclamation-practice-r29.md | same |
| community-reclamation-practice-r30.md | same |
| community-reclamation-practice-r31.md | same |
| gitlab-reclamation-settings-r28.md | GitLab housekeeping knobs |
| gitlab-reclamation-settings-r29.md | GitLab version boundary |
| gitlab-reclamation-config-r30.md | GitLab config constraints |
| gitlab-reclamation-old-shape-r31.md | pre-15.8 shape |
| gitlab-reclamation-name-window-r32.md | name-window narrowing |
| gitlab-reclamation-name-phantom-r33.md | phantom-name investigation |

## Attack log
None — all frozen counters (grounded F4 4→6, registry 135→138) verified consistent with lane state; no gameable predicate found. Staged S119 disposal is already recorded in an adopted entry's gate, matching C2's dispose directive.

## Handoff notes
- L1: adopt exactly the two r28 entries; leave origin-record-format-gvfs-r26.md staged; do not re-adopt r23/r24 quarantine entries already rejected/superseded on the record.
