# SwarmConnector53 — Cross-Axis Sibling-Overlap Scan & Synthesis Report (Round 28 w1)

## Status
STATUS: PASS — 20/20 sibling lanes scanned read-only; identified 7 lanes with uncommitted `.ufo/waves` residue (up to 81k files), all 20 lanes with dangling pointer citations (317 total in scanned files), and fleet-wide Q57/Q59-class composite/pseudo-path citations; delivered one bounded, non-obvious cross-axis synthesis move improving operability and calibration without harming coverage.

## Evidence
- Lane base commit: `3a2a80d0d18940a5e352ebc526da22a57dad83c4` (branch master); HEAD: `0c96332932e66bbaf9cf1c246091d3275a0ab612`.
- Frozen preregistration verified: `census/round-28/records/preregistration.txt:1` ("Souji round 28 — preregistration (FROZEN before any after-data; lane base commit 3a2a80d0d18940a5e352ebc526da22a57dad83c4, branch master, ahead=0, remote verified). Attempt 1.").
- Scope scanned: all 20 sibling lane repositories under `/home/vgpnk/Projects/shokunin/*-shokunin` (excluding `souji-shokunin`).
- Scanned surfaces per sibling lane: `corpus/lessons/round-2*.md`, `SCORECARD.md`, `corpus/QUALITY.md`.
- Read-only execution commands:
  - `git -C <lane> rev-parse HEAD`
  - `git -C <lane> status --porcelain=v1 --untracked-files=all` (filtered for `.ufo/waves`)
  - `git -C <lane> ls-tree -r --name-only HEAD` (checked tree existence)
  - Pointer extraction applying canonical landing-gate regex `(?<![A-Za-z0-9_./<>*])(?:(?:\.\./)+|\./)?(?:census|tests|tools|corpus|\.ufo/waves|\.ufo/quarantine)/[^\s`"'()\[\]]+`.

## Sibling lane scan

| Sibling Lane | HEAD Rev | Dirty .ufo/waves | (a) Composite / Pseudo-path Cites | (b) Uncommitted .ufo/waves Leftovers | (c) Dangling Pointer Cites (absent from tree) | Key Evidence Pointer |
|---|---|---|---|---|---|---|
| `audio-shokunin` | `7a2fcd4f0883` | 0 | 36 hits | Clean (0 dirty) | 22 dangling | SCORECARD.md:31 (`corpus/live/runs`); corpus/QUALITY.md:9 (`corpus/lessons/round-101.md#M11`) |
| `chousa-shokunin` | `414a2ec6cde0` | 2 | 31 hits | 2 dirty paths | 14 dangling | .ufo/waves/round-40/w1/swarm-registry.json; SCORECARD.md:95 (`corpus/URL/session`) |
| `game-dev-2d-shokunin` | `7753d49b1667` | 0 | 5 hits | Clean (0 dirty) | 3 dangling | SCORECARD.md:177 (`census/refusals`); corpus/QUALITY.md:25 (`corpus/...:line`) |
| `game-dev-3d-shokunin` | `89dd182b7094` | 0 | 4 hits | Clean (0 dirty) | 1 dangling | SCORECARD.md:298 (`corpus/knowledge/unreal-mcp/README.md:12-48`); SCORECARD.md:348 (`corpus/live/runs`) |
| `kagi-shokunin` | `69b61db46be4` | 0 | 16 hits | Clean (0 dirty) | 4 dangling | SCORECARD.md:490 (`corpus/knowledge/handler-trust-boundary.md:3-6`); round-26.md:267 (`tests/no-private-read`) |
| `kaidoku-shokunin` | `aa04633a686d` | 0 | 47 hits | Clean (0 dirty) | 18 dangling | SCORECARD.md:294 (`tools/list`); SCORECARD.md:2650 (`census/guard`); tools/evidence-timestamps.py |
| `kake-shokunin` | `fcaf4b85ce32` | 0 | 63 hits | Clean (0 dirty) | 19 dangling | SCORECARD.md:18 (`corpus/claims`); SCORECARD.md:549 (`;313`); QUALITY.md:238 (en-dash `11–13`) |
| `kama-shokunin` | `873c5d7774b9` | 1233 | 90 hits | 1233 dirty paths | 22 dangling | .ufo/waves/round-35/w1/out/ConnSibling/seat.log; SCORECARD.md:544 (`tools/registry`) |
| `kasegi-shokunin` | `002e92ce07ed` | 33 | 7 hits | 33 dirty paths | 26 dangling | .ufo/waves/round-30/assimilation/collisions; SCORECARD.md:44 (`census/full`) |
| `kengaku-shokunin` | `adaf25dfd27d` | 81305 | 11 hits | 81305 dirty paths | 7 dangling | .ufo/waves/round-34/assimilation/captures/geniac-s105.html; round-24.md:140 (`census/scripts/sources-census.sh`) |
| `kotoba-shokunin` | `c69711ee0827` | 0 | 16 hits | Clean (0 dirty) | 1 dangling | corpus/QUALITY.md:13 (`census/exhaustiveness`) |
| `kotodama-shokunin` | `8841ad3b896a` | 2 | 23 hits | 2 dirty paths | 45 dangling | .ufo/waves/round-72/w1/ScoutMergeScan.md; QUALITY.md:29 (`round-49.md#post-review-corrections`) |
| `kumitate-shokunin` | `dfa6fca8f362` | 0 | 20 hits | Clean (0 dirty) | 8 dangling | SCORECARD.md:996 (`corpus/SKILL`); QUALITY.md:350 (`.ufo/waves/round-$N/plan.md`); QUALITY.md:607 (`corpus/##`) |
| `lore-shokunin` | `380ef3abc7c7` | 0 | 30 hits | Clean (0 dirty) | 20 dangling | SCORECARD.md:353 (`corpus/tool`); SCORECARD.md:452 (`corpus/README`); QUALITY.md:12 (`#mistakes`) |
| `mado-shokunin` | `08be4eb7fd13` | 3 | 17 hits | 3 dirty paths | 8 dangling | .ufo/waves/round-38/w1/reports/RevEntryBound.md; SCORECARD.md:1888 (`tools/knowledge/skill`) |
| `mori-shokunin` | `2d85e33d1419` | 0 | 35 hits | Clean (0 dirty) | 28 dangling | SCORECARD.md:419 (`tools/mori-census.sh:1783/:1809`); SCORECARD.md:675 (`census/oracle`); en-dash `134–140` |
| `revenger-shokunin` | `3f5edbc20635` | 1 | 98 hits | 1 dirty paths | 1 dangling | .ufo/waves/round-69/R69CounterReplay.md; SCORECARD.md:167 (`.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`) |
| `tabi-shokunin` | `ef8aa4a3256c` | 0 | 64 hits | Clean (0 dirty) | 74 dangling | SCORECARD.md:395 (`.ufo/waves/kaika/steer.md:32`); QUALITY.md:12 (`round-1.md#mistakes`) |
| `tameshi-shokunin` | `5891bdb77aba` | 0 | 53 hits | Clean (0 dirty) | 5 dangling | SCORECARD.md:1830 (`.ufo/waves/round-38/calibration/`); QUALITY.md:365 (`corpus/instruction`) |
| `tsukuroi-shokunin` | `564db0b614b2` | 0 | 19 hits | Clean (0 dirty) | 16 dangling | SCORECARD.md:1237 (`tools/corpus`); SCORECARD.md:1823 (`tools/score-census-handoff-r32.py:source`) |

## Findings
1. **Pervasive Uncommitted `.ufo/waves` Workspace Residue (Axis: Operability)**:
   Seven sibling lanes (`kengaku`: 81,305 paths; `kama`: 1,233 paths; `kasegi`: 33 paths; `mado`: 3 paths; `chousa`: 2 paths; `kotodama`: 2 paths; `revenger`: 1 path) leave active or stale wave artifacts dirty in the working tree. This demonstrates that souji's C3 problem (163 dirty `.ufo/waves` files at base) is a fleet-wide operational defect caused by lack of an automated evidence-capture pipeline. Location: sibling `git status --porcelain=v1 --untracked-files=all`.
2. **Systemic Dangling Citations to `.ufo/waves` (Axis: Calibration / Operability)**:
   Fifteen sibling lanes (`chousa`, `kagi`, `kake`, `kama`, `kasegi`, `kengaku`, `kotodama`, `kumitate`, `lore`, `mado`, `mori`, `revenger`, `tabi`, `tameshi`, `tsukuroi`) directly cite `.ufo/waves/...` paths in `SCORECARD.md`, `corpus/QUALITY.md`, or lessons. Because `.ufo/waves/` is ephemeral and untracked in git, every such citation dangles in `git ls-tree`, exactly mirroring souji's Q57 defect where `.ufo/waves/round-24/assimilation/slice-verdicts.tsv` had to be replaced by committed census records.
3. **Q59-Class Conceptual Prose Pseudo-Paths (Axis: Calibration)**:
   In every scanned sibling lane, prose conceptual phrases written with forward slashes (e.g. `census/guard`, `census/full`, `tools/list`, `corpus/claims`, `tools/registry`, `census/validate`, `corpus/instruction`, `tools/counters`, `census/exhaustiveness`, `tools/corpus`, `tools/path`) match the `POINTER_PATH_RE` scanner because they begin with scanned roots (`census/`, `tools/`, `corpus/`). This is identical in mechanism to souji's base finding `LG-DANGLING-PTR corpus/knowledge/registry` (fixed by C1(b) rewording to `knowledge-registry`).
4. **Q57-Class Composite Selectors & Formatting Defects (Axis: Calibration)**:
   Sibling citations frequently incorporate delimiters that defeat pointer normalization:
   - Section anchors (`#M11`, `#mistakes`, `#post-review-corrections` in `audio`, `kotodama`, `lore`, `tabi`), which `_trim_pointer_token` does not strip.
   - Non-digit trailing tags (e.g. `tools/score-census-handoff-r32.py:source` in `tsukuroi`, `tools/mori-census.sh:1783/:1809` in `mori`, matching souji's `round-24.md:232:S118`).
   - Semicolon delimiters (e.g. `round-26-verifier-spotcheck.md;313` in `kake`).
   - Unicode en-dashes in line ranges (e.g. `11–13` in `kake`, `134–140` in `mori`), which bypass ASCII hyphen-range regexes.
5. **Cross-Claim Second-Order Tension in Souji R28 Proposals**:
   In souji, C3 introduces `.gitignore` entries for `.ufo/waves/`, and `tools/souji-wave-evidence-capture.sh` captures wave files into `census/round-<N>/waves/`. However, if documentation continues to cite `.ufo/waves/...` (as seen in `SwarmCritic46`'s analysis of r24 slice-verdicts), those pointers will permanently dangle against `git ls-tree` under `souji-landing-gate.py`.

## Synthesis & Proposed Move (UFO-FSD Connector)

- **Evidence**:
  - Sibling scan proves 15/20 sibling lanes suffer from unresolvable `.ufo/waves/...` citations in committed records, and 7/20 suffer from dirty `.ufo/waves/` clutter.
  - Souji C1 rectifies base landing-gate findings by replacing a `.ufo/waves/round-24` reference with committed `census/round-24/records/slice-verdicts.tsv` (`SwarmExecutor01.md`).
  - Souji C3 captures `.ufo/waves/round-<N>/` into `census/round-<N>/waves/` and gitignores `.ufo/waves/` (`SwarmCritic43.md`, `SwarmCritic46.md`).
- **Affected Axes**:
  - **Operability (+)**: Establishes a clean, reproducible separation between the ephemeral execution substrate (`.ufo/waves/`, gitignored) and durable committed evidence (`census/round-<N>/waves/`).
  - **Calibration (+)**: Eliminates current and future `LG-DANGLING-PTR` findings arising from seats citing uncommitted wave reports in `SCORECARD.md` or lessons.
  - **Coverage (Neutral / No Harm)**: Does not alter registry schemas, knowledge entries, or F4 groundings.
- **Proposed Move — "Durable Receipt Redirection Contract"**:
  Synthesize the C1 citation correction and C3 wave-capture instrument into a unified citation policy:
  1. Enforce that all round receipts cited in `SCORECARD.md`, `corpus/QUALITY.md`, and `corpus/lessons/round-*.md` point strictly to committed paths under `census/round-<N>/waves/` (e.g. `census/round-28/waves/summary.tsv` and `manifest.sha256`), never to ephemeral `.ufo/waves/round-<N>/...`.
  2. In `tools/souji-wave-evidence-capture.sh`, generate an immediate wave-manifest stub at capture time so committed paths are deterministically resolvable.
  3. Amend `tools/souji-landing-gate.py`'s pointer verification rule to disallow `.ufo/waves/` citations in committed self-assessment surfaces, catching any regression before landing.
- **Risks**:
  Timing dependency: during in-flight wave execution, seats drafting `SCORECARD.md` or lesson notes cite `census/round-<N>/waves/` before L1 runs the capture script. Mitigated by `tools/souji-wave-evidence-capture.sh` supporting a `--dry-run` or early staging manifest pass, or by L1 committing captured waves simultaneously with the scorecard.
- **Verification**:
  - `git grep -E '\.ufo/waves/' SCORECARD.md corpus/QUALITY.md corpus/lessons/` returns 0 hits in committed files.
  - `python3 -B tools/souji-landing-gate.py --root . --rev <tip> --round 28 --fleet-root /home/vgpnk/Projects/shokunin` returns SUMMARY `findings=0` with `LG-DANGLING-PTR` count = 0.

## Attack log
None. This connector proposal respects all frozen preregistration predicates, targets, and kill rules for round 28. It resolves a systemic fleet-wide defect identified by the cross-axis scan without relaxing any verification bar.
