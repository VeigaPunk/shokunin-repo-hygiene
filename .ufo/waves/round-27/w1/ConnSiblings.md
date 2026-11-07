# ConnSiblings — SIBLING-OVERLAP Scan & Cross-Axis Connector Synthesis (Souji Round 27, w1)

## Status
STATUS: PASS — Read-only reconnaissance across 20 sibling lane repos and fleet root reveals zero surface collisions on pointer exemptions, staged merge rows, or SOURCES.md dependencies; synthesized C2 E04 collision attack falsification with atomic landing sequence and C3 fixture scratch cleanup to advance calibration (7), coverage (8), and operability (8) without harming any axis.

## Evidence
- Lane base commit: `e78ac7c4837b81b634db4a927605a751a7f006ba` (master, ahead=0); fleet root commit: `ecd8086c`.
- Sibling repository audit command: `for d in /home/vgpnk/Projects/shokunin/*-shokunin; do [ -d "$d/.git" ] && echo "$(basename "$d"): $(git -C "$d" log -1 --format="%h %ci %s")"; done` (20 sibling repos examined).
- Surface (a) scan: `grep -r "pointer-exemptions" /home/vgpnk/Projects/shokunin/*-shokunin` returned zero production citations. Sole hit was an isolated spec validator copy in `tabi-shokunin/.ufo/waves/round-27/scratch/TabiR27.ScoutStagedGround/souji-validator-check/` (read-only scratch).
- Surface (b) scan: `grep -rE "merge/souji|glocalfile|gfileutils" /home/vgpnk/Projects/shokunin/*-shokunin` returned zero hits in sibling production or assimilation branches. Sibling lanes currently assimilate from their own distinct merge packages: tabi from `merge/tabi` (RFC 9110), kasegi from `merge/kasegi` (IPA/JPCERT), kengaku from `merge/kengaku` (Toolathlon).
- Surface (c) scan: `grep -r "souji-shokunin/corpus/SOURCES.md" /home/vgpnk/Projects/shokunin` confirmed zero external write operations. References are confined to read-only fleet validators (`scripts/sources-census.sh`, `.ufo/prompts/souji-round-27.md` id extractor) and historical spot-check notes in chousa and kagi.
- Census validation reproduction in isolated scratch (`/var/tmp/souji-r27-ConnSiblings/`): appending `sources-add.md` (rows S152, S210, S211) into `corpus/SOURCES.md` alongside admitted knowledge drafts yielded `W04 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes` (advisory warning, exit code 0; zero E-level errors), disproving the E04 fatal collision claimed in `CritC2Attack.md`.

## Overlap Table

| Sibling | Surface | Round / Evidence | Conflict Risk |
|---|---|---|---|
| **tabi-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 27 in flight (`5ed6484`). Scratch held spec copy in `TabiR27.ScoutStagedGround/souji-validator-check/`; assimilates RFC 9110 from `merge/tabi` (S107); historical r16/r17 notes cite souji receipt standards. | **None**. Disjoint merge source, zero production writes to souji surfaces. |
| **kasegi-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 28 in flight (`94f387c`). C1 audits local `anchorcheck.py`; C2 assimilates from `merge/kasegi` (S042); r25 `ConnectorSiblings.md` notes souji landing-gate `bash -n` and S015 secret boundaries. | **None**. Disjoint merge package, local instrument focus. |
| **kengaku-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 33 in flight (`77ac8c1`). C1 assimilates from `merge/kengaku` (S103/S104); C2 N3/N4 appends errata to fleet reports `round-31/kengaku.md` and `round-32/kengaku.md`. | **None**. No writes to souji; fleet report edits strictly confined to kengaku round logs. |
| **kaidoku-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 34 closed (`aa04633a`). REA reverse-engineering province; historical r16 citations of souji measured revisions. | **None**. Inactive; no surface overlap. |
| **tsukuroi-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 36 closed (`564db0b`). Host operability and toolchain maintenance; pacman transaction pause observed. | **None**. No surface overlap. |
| **mado-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 38 closed (`08be4eb`). Desktop compositor craft; r19 note cited npm install. | **None**. Inactive; no surface overlap. |
| **kama-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 35 closed (`873c5d77`). Local model serving and endpoint health; r13/r14 cited revision vocabulary. | **None**. Inactive; no surface overlap. |
| **tameshi-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 44 closed (`5891bdb`). Verification fixture craft. | **None**. Inactive; no surface overlap. |
| **mori-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 46 closed (`2d85e33d`). Host/fleet observability; read-only watchdog and process monitors. | **None**. Read-only observer. |
| **chousa-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 48 closed (`414a2ec`). Deep research method; historical r30/r45 citations of souji S034/S038 timeout rows. | **None**. Inactive; no surface overlap. |
| **kake-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 54 closed (`fcaf4b8`). Web publishing craft. | **None**. Inactive; no surface overlap. |
| **kumitate-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 62 closed (`dfa6fca`). Tooling and orchestration. | **None**. Inactive; no surface overlap. |
| **revenger-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 69 closed (`3f5edbc`). RE evidence ledgers. | **None**. Inactive; no surface overlap. |
| **kotoba-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 71 closed (`c69711e`). Prompt and skill verification (`verify_skill_checklist.py`). | **None**. Inactive; no surface overlap. |
| **kotodama-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 72 closed (`8841ad3`). Linguistics/worldbuilding research. | **None**. Inactive; no surface overlap. |
| **kagi-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 28 closed (`69b61db`). Secrets and vaults; r25/r26 noted souji S015 yields secret handling to kagi. | **None**. Inactive; no surface overlap. |
| **lore-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 21 checkpoint (`380ef3a`). World bible consistency. | **None**. Inactive; no surface overlap. |
| **audio-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | Round 101 reflection (`7a2fcd4f`). Mix audio protocols. | **None**. Inactive; no surface overlap. |
| **game-dev-2d-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | 2026-10-21 checkpoint (`7753d49b`). 2D gameplay craft. | **None**. Inactive; no surface overlap. |
| **game-dev-3d-shokunin** | (a) exemptions, (b) merge rows, (c) SOURCES | 2026-10-21 checkpoint (`89dd182`). 3D gameplay craft. | **None**. Inactive; no surface overlap. |
| **Fleet Root (`/home/vgpnk/Projects/shokunin`)** | (a) exemptions, (c) SOURCES dependency | `ecd8086c`. `scripts/sources-census.sh` validates `corpus/SOURCES.md`; `prompts/souji-round-27.md` scans IDs. | **Controlled**. Read-only fleet scripts; souji seats must never write to fleet root. |

## Findings

1. **Surface (a) — Zero Sibling Contestation on Pointer Exemptions:** `corpus/pointer-exemptions.tsv` is an internal souji mechanism consumed exclusively by `tools/souji-landing-gate.py`. No sibling repository contains a citation, symlink, or dependency on it. Tabi-shokunin's r27 scratch copy was a passive validation harness of souji's prompt spec (`tabi-shokunin/.ufo/waves/round-27/scratch/TabiR27.ScoutStagedGround/souji-validator-check/`), producing zero persistent artifacts or conflicts.
2. **Surface (b) — Disjoint Assimilation Themes Across the Fleet:** The staged rows S109–S242 in `/home/vgpnk/Projects/shokuknow/merge/souji/` and GLib 2.84.0 origin-record sources (`gio/glocalfile.c`, `glib/gfileutils.c`) are untouched by any sibling lane. Sibling assimilation active today is strictly partitioned: tabi works `merge/tabi` (HTTP semantics), kasegi works `merge/kasegi` (vulnerability disclosure), and kengaku works `merge/kengaku` (eval benchmark graders).
3. **Surface (c) — Strict External Read-Only Boundary:** Zero sibling processes write to `/home/vgpnk/Projects/shokunin/souji-shokunin`. External dependencies on `souji-shokunin/corpus/SOURCES.md` are limited to fleet verification scripts (`scripts/sources-census.sh validate`) and orchestrator prompt generation.
4. **Resolution of C2 Contradiction (`CritC2Attack` vs `ExecRowsNormalize`):** `CritC2Attack.md` claimed C2 is unsatisfiable because S152 and S210 share a URL, asserting a fatal E04 error (`duplicate url within scope`) and arguing the 132→135 row count must be amended down to 134. Direct inspection of `scripts/sources-census.sh:643-654` and empirical execution in isolated scratch reveal that `CritC2Attack`'s failure was an artifact of setting `scope="A"` for both rows. In `sources-add.md`, S152 (writer sequence/guarantees) and S210 (complementary mechanism roles) have distinct, non-identical `scope` texts. `sources-census.sh` keys on `scope_key = u SUBSEP scope`; different scope text generates `W04` (duplicate URL across scopes), which is an advisory warning, exiting 0. The frozen 132→135 target and C2 counter ARE fully achievable without contract amendment.
5. **C2/C3 Landing Order and Scratch Hygiene Second-Order Effects:**
   - *Atomic Commit Requirement:* `sources-census.sh` validates `used-by` existence (`E11`). If `corpus/SOURCES.md` is committed without the accompanying `corpus/knowledge/*.md` entries, E11 fails (rc 1). If entries are committed without `SOURCES.md`, `souji-gate-check.py` fails check 5 (`check5-dangling-source`). The L1 integrator must land both in the exact same commit transaction.
   - *Scratch Residue Defect in C3 Fixture:* `w1/r27-pre-report-gate.sh:52-62` sets `HOME="$WORLD_ROOT/home"` and creates `$WORLD_ROOT/home`, but its cleanup trap only loops over `for w in $WORLDS; do rm -rf "$WORLD_ROOT/$w"; done`, leaving `/var/tmp/souji-r27-ExecFixtureC3Tests/home` behind. Amending line 60 to `rm -rf "$WORLD_ROOT"` prevents uncommitted scratch debris from breaching fleet hygiene boundaries.

## Proposed Move (UFO-FSD Connector Synthesis)

- **Evidence:** `scripts/sources-census.sh:643-654`, `w1/sources-add.md:5-7`, `w1/r27-pre-report-gate.sh:52-62`, `tools/souji-landing-gate.py:905-961`.
- **Affected Axes:**
  - *Calibration (7):* Unlocked via C1 (resolving 2→0 dangling pointer findings in `corpus/pointer-exemptions.tsv`; `LG-DANGLING-PTR-EXEMPT-STALE` ensures no dead exemptions remain).
  - *Coverage (8):* Unlocked via C2 (132→135 rows, F4 grounded entries 2→4, `sources-census.sh` rc 0 with W04 advisory across distinct scopes).
  - *Operability (8):* Unlocked via C3 (`souji-pre-report-gate.sh` and `r27-pre-report-gate.sh` selftest 4/4 with `FALSE-GREEN-REJECTED`, augmented with full scratch directory teardown).
- **Proposed Move:**
  The L1 integrator integrates C1, C2, and C3 in a unified single-round synthesis:
  1. *C1:* Append the two truthful, specific rows from `w1/exemptions-add.tsv` to `corpus/pointer-exemptions.tsv` (`corpus/knowledge/registry` and `corpus/lessons/round-24.md:232:S118`).
  2. *C2:* Land `w1/origin-record-writer-r27.md`, `w1/origin-record-mechanism-set-r33.md`, and the 3 distinct-scope rows from `w1/sources-add.md` (S152, S210, S211) in an atomic commit, dismissing `CritC2Attack`'s false E04 objection as disproven by `sources-census.sh` W04 scope-key semantics.
  3. *C3:* Land `w1/souji-pre-report-gate.sh` at `tools/` and `w1/r27-pre-report-gate.sh` at `tests/fixtures/` with line 60 cleaned to `rm -rf "$WORLD_ROOT"`, executing the 4/4 selftest and minting `census/round-27/c3-counter.sh` receipt.
- **Risks:**
  - *Risk 1 (C2 E11 Stale Path):* If knowledge file paths in `used-by` do not match the exact committed file paths, `sources-census.sh` halts on E11. *Mitigation:* `sources-add.md` uses exact relative paths (`corpus/knowledge/origin-record-writer-r27.md` and `corpus/knowledge/origin-record-mechanism-set-r33.md`), verified in scratch.
  - *Risk 2 (C1 Exemption Over-matching):* If an exemption matches broadly, true dangling pointers could hide. *Mitigation:* Both rows are exact paths; gate's `LG-DANGLING-PTR-EXEMPT-STALE` check ensures that removing either cited token immediately turns the exemption into a fatal finding.
- **Verification:**
  1. `python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <tip> --round 27 --fleet-root /home/vgpnk/Projects/shokunin` → `SUMMARY findings=0`.
  2. `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok ...` rc 0 with S210 advisory W04.
  3. `bash tests/fixtures/r27-pre-report-gate.sh` → `cases=4 pass=4 control=FALSE-GREEN-REJECTED` rc 0, and `[ ! -d /var/tmp/souji-r27-ExecFixtureC3Tests ]`.

## Attack log
- *Attack on C2 Feasibility (E04 collision):* REJECTED. `CritC2Attack` assumed `scope` is checked as bare URL identity. `sources-census.sh:643` proves `scope_key` incorporates the full scope description string. S152 and S210 have distinct scopes, producing valid W04 advisory warnings without exit code failure.
- *Attack on C1 Calibration Integrity:* SURVIVES WITH MITIGATION. Reason-only path exemptions risk masking future defects; confirmed mitigated this round because the gate enforces `LG-DANGLING-PTR-EXEMPT-STALE` on unused rows and both tokens are demonstrated parser grammar over-matches.
- *Attack on C3 Teardown Hygiene:* ACCEPTED & REPAIRED. Original fixture draft left `$WORLD_ROOT/home` behind. Proposed move amends the trap to prune `$WORLD_ROOT` completely.
