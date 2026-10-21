# Acceptance runner steps 7–12: relocatability findings

Axes checked: **root selection**, **file/directory read-write scope**, and **Git/history plus network/proc dependencies**. Static source review only; no acceptance program or test was executed. No LSP device is available in the mounted tool inventory, so the findings below are literal source evidence, not semantic LSP proof. No tools were installed.

## Step order and launcher context

At the pinned source, `make_steps()` creates 13 explicit steps and then appends `COUNTER_EXPECTATIONS` (runner lines 272–331). Thus the requested steps are exactly 7 `landing-gate-selftest`, 8 `r18-landing-pointers`, 9 `r16-landing-gate`, 10 `carry-invariant-probe`, 11 `r19-revision-pin-fixture`, and 12 `agreement-pin-check` (runner lines 301–315).

The runner invokes each command with `cwd=root` and its fixed child environment (runner lines 107–117, 540–543). That environment sets `PYTHONDONTWRITEBYTECODE=1` and `GIT_NO_LAZY_FETCH=1`. Separately from these individual-step verdicts, the runner itself resolves `--root` and refuses anything other than the literal `LANE` path, then requires `HEAD == --rev` (runner lines 24, 505–519). So a detached clone elsewhere cannot run this pinned runner successfully even where an individual step is relocatable.

## Step findings

### 7. `landing-gate-selftest` — **YES, the step is relocatable**

- **Root:** No repository root is selected. Runner invokes `tools/souji-landing-gate.py --selftest` (runner lines 272–275, 301–302). In `main`, `--selftest` branches directly to `run_selftest()` before checking `--root`/`--rev` (gate lines 2278–2303).
- **Reads:** It uses its own script (`__file__`) for self-reinvocation (gate lines 1588–1596, 1632–1645, 1785–1795, 2244–2253). It builds synthetic repositories and evaluates their committed Git trees: `git ls-tree`/`cat-file` provide the source bytes (gate lines 196–250, 1022–1048). Evaluated inputs include synthetic `SKILL.md`, cited `.sh`/`.py` files, frozen `expected.json`/record/pin entries, pointer-exemption TSV where present, corpus/LOG pointer sources, wave `.md` reports, and the round lesson (gate lines 467–539, 554–734, 876–992). Bash scripts are written to a temporary mirrored snapshot and checked with `bash -n`; Python files are compiled in memory (283–322). The selftest's synthetic source files are defined/written under its temporary top directory (1217–1353, 1338 onward); its synthetic fleet JSON is also read back there (1610–1645).
- **Writes:** `/var/tmp/souji-landing-gate-selftest-*` contains synthetic Git repos and their fixture files; each `evaluate()` creates `/var/tmp/souji-landing-gate-*` parser snapshots and removes them in `finally` (1022–1023, 1143, 1338–1353, 2266–2268). The selftest's `pointer-fleet-only.json` is under that same temporary tree (1631–1645). No caller-clone/lane path is written; the runner does not pass `--json`.
- **Git/history:** Synthetic `git init`, `add`, `commit`, and `rev-parse` calls build test history (1217–1253); the gate uses `ls-tree`, `cat-file`, `rev-parse`, and in selected synthetic cases `diff` (196–250, 1055–1076). No original repository revision or `HEAD == --rev` is required by this selftest; it supplies its own synthetic commits. `bash -n` parses but does not run repository scripts (module docstring lines 16–25; 283–322).
- **Network/proc:** No network or live `/proc` access is present in the step's selftest path. Git and `bash -n` are subprocesses.

### 8. `r18-landing-pointers` — **NO, not relocatable**

- **Root:** `LANE` is the literal `/home/vgpnk/Projects/shokunin/souji-shokunin`; `DEFAULT_TOOL` also points there (fixture lines 30–32). The runner does override `--tool` with the selected root's gate path (runner lines 303–304; fixture lines 179–194), but the historical replay still calls `gate.run(LANE, REPLAY_REV, REPLAY_ROUND)` with fixed revision `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (fixture lines 282–306). The test does not derive that replay root from `--tool`, `__file__`, or `cwd`.
- **Reads:** It checks that the selected gate file exists and that `git` is on `PATH` (183–191). It creates synthetic repos with `SKILL.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/knowledge/authority.md`, `LOG.md`, `corpus/lessons/round-N.md`, `.ufo/waves/round-N/w1/Seat.md`, and `tools/ok.sh` (48–56, 81–109), then adds case files including `census/round-18/kept.json`, `census/round-18/source.md`, `census/round-18/a.json`, `census/round-6..11/receipt.txt`, `corpus/pointer-exemptions.tsv`, and a temporary `empty-tool.py` (198–279, 308–313). The selected gate reads those synthetic Git trees and blobs. For the fixed historical replay it also reads the Git tree/blob inputs at `LANE` and the pinned old commit; gate input selectors include `SKILL.md`, frozen expected/record/pinned files, pointer exemption TSV, pointer-source documents/LOG, round wave reports, and lesson (gate lines 1022–1048, 1078–1120; 467–539, 554–734, 876–992).
- **Writes:** Fixture repositories, all their generated files and `.git` data, and `empty-tool.py` are under a fresh `/var/tmp/souji-r18-pointer-fixture-*` directory removed in `finally` (74–109, 195–196, 308–329). The gate may create and remove its `/var/tmp/souji-landing-gate-*` parsing snapshot (gate lines 283–301, 1022–1023, 1143). No fixture write targets the lane.
- **Git/history:** Fixture Git commands initialize/configure/commit synthetic repos and resolve their `HEAD` (59–71, 81–109). The gate resolves the supplied commit and reads trees/blobs with `rev-parse`, `ls-tree`, and `cat-file` (196–250); the historical run needs the fixed historical commit object and any measured-commit objects it checks to exist in the hardcoded repository. It does **not** require `HEAD` to equal the historical replay revision; it selects that revision explicitly. No complete history walk is specified.
- **Network/proc:** No network or live `/proc` access is present. Git and the selected Python gate are subprocesses.
- **Relocatability counterexample:** Even if the runner passes a clone-local `--tool`, the replay root remains the absolute `LANE` at fixture line 285. A fresh clone at another path is not the root used for this mandatory case.

### 9. `r16-landing-gate` — **NO, not relocatable**

- **Root:** Same literal root pattern: `LANE` and `DEFAULT_TOOL` are hardcoded (fixture lines 64–67); `--tool` can select the clone-local gate (197–201), but the fixture additionally requires `LANE/.git` (208–214) and runs the historical case against `gate.run(LANE, REPLAY_REV, REPLAY_ROUND)` (229–236). The replay revision is abbreviated `b410186` (66). Neither root is derived from the selected tool or fixture path.
- **Reads:** The fixture checks the selected gate path and Git availability, then `LANE/.git` (197–214). It creates and commits synthetic repos under `/var/tmp`; their files include `SKILL.md`, `tools/*`, `.ufo/waves/round-77/w1/*.md`, `corpus/lessons/round-77.md`, and `tests/fixtures/*-frozen/{expected.json,record.json,...}` (102–135, 238–495). The gate reads synthetic committed tree/blob inputs; the historical round-15 run reads the tree at `LANE`/`b410186`, including cited scripts, frozen-pin inputs, round-15 reports, and `corpus/lessons/round-15.md` (gate lines 467–539, 554–734, 1002–1085). This step uses round 15, so the round-18 pointer scan is not selected (gate lines 1086–1099).
- **Writes:** Synthetic repositories and `empty-tool.py` are under `/var/tmp/souji-r16-lgfixture-*`, removed in `finally` (91–135, 225–227, 497–525). Gate parser snapshots are temporary under `/var/tmp` and removed (283–301, 1022–1023, 1143). No lane write is specified.
- **Git/history:** The fixture initializes, commits, and resolves synthetic repos (91–124). The historical gate resolves `b410186` and reads its tree/blob objects (gate lines 196–250). The fixed historical commit and referenced measured commits must be available in the hardcoded repo; the gate does not require `HEAD` to equal `b410186`. No complete history traversal is specified. Runner-level `HEAD == --rev` is a separate precondition noted above.
- **Network/proc:** No network or live `/proc` access is present. Git, Python gate invocations, and `bash -n` parsing use subprocesses.
- **Relocatability counterexample:** The explicit `LANE/.git` precondition (208–209) and historical `gate.run(LANE, ...)` call (229–236) make the fresh clone path irrelevant.

### 10. `carry-invariant-probe` — **YES, the step is relocatable**

- **Root:** `Path(__file__).resolve().parents[2]` selects the checkout root containing `census/round-19/probe-carry-invariants.py`; `GATE` is then that root's `tools/souji-landing-gate.py` (probe lines 25–26). Runner invokes this script by absolute path below its selected root (runner lines 278, 308–310).
- **Reads:** It checks `GATE.is_file()` and imports that one gate source file (probe lines 31–43); all invariant inputs are generated in memory from seeded words (44–81). No repository files beyond the gate module are read.
- **Writes:** The program declares no file writes (docstring line 15); with the runner's `PYTHONDONTWRITEBYTECODE=1` environment (runner lines 107–117), the import does not need to leave bytecode in the clone. It prints to stdout only.
- **Git/history:** No Git commands, revision lookup, or history requirement. No `HEAD == --rev` requirement.
- **Network/proc:** None observed in source; no live `/proc` access.

### 11. `r19-revision-pin-fixture` — **YES, the step is relocatable**

- **Root:** It derives `lane` as two parents above its own `__file__` location and resolves relative helper paths there (fixture lines 133–137). Runner supplies an absolute clone-local `--tool` and `--tool-dir root` (runner lines 272–278, 311–313), so helper and static wiring paths resolve into the detached clone.
- **Reads:** It executes the clone's `tools/souji-rev-pin.py` helper and opens these clone-root files for static wiring checks: `census/round-13/run-verification.py`, `census/round-14/run-verification.py`, `census/round-14/run-targeted.py`, `census/round-13/count-claims.py`, and `census/round-14/count-claims.py` (fixture lines 47–68, 195–213). Its behavioral tests operate on a synthetic sandbox's `tool.sh` and `record.json`; helper `input_snapshot()` compares selected filesystem files against Git blobs and traverses only the selected paths (helper lines 96–181).
- **Writes:** `/var/tmp/souji-r19-rev-pin.*` contains `base-stub.py`, the synthetic sandbox repository and its `.git` data, `tool.sh`, and `record.json`; the fixture mutates the sandbox `tool.sh` for dirty/commit cases, then removes the entire top directory (fixture lines 89–107, 143–155, 223–224). No clone/lane file is written.
- **Git/history:** Fixture and helper use only the synthetic sandbox: `init`, `config`, `add`, `commit`, `checkout`, `update-ref`, `rev-parse`; helper checks commit identity, enumerates durable refs, uses `merge-base --is-ancestor`, and verifies tracked selected file bytes with `ls-tree`/`cat-file` (fixture lines 71–107; helper lines 66–76, 79–93, 96–181, 184–229). Its generated three-commit history supplies the needed history; the historical-commit case explicitly tests an older commit with `--no-tree-check` (fixture lines 164–193; helper 356–369). It does not depend on clone `HEAD == --rev` or the clone's full history.
- **Network/proc:** No network or live `/proc` access; subprocesses are Git and Python helper invocations.

### 12. `agreement-pin-check` — **YES, the step is relocatable**

- **Root:** The runner passes `--root <selected-root>` and an absolute `--check <selected-root>/census/round-19/proc-agreement-pinned.json` (runner lines 314–315). The program normalizes `args.root` with `os.path.abspath()` (checker line 176); it does not use a literal lane path or `__file__` for data selection.
- **Reads:** It parses the record at `census/round-19/proc-agreement-pinned.json` (checker lines 177–184; this record names the inputs below). It then checks and hashes `tools/souji-proc-census.sh`, `census/round-18/leak-count.py`, `census/round-18/proc-agreement-counterfix.json`, `census/round-18/proc-agreement-final.json`, and `census/round-18/counter-exclusion-repair.json` relative to `root` (checker lines 70–99; pinned record; defaults at 37–43). `sha256()` opens each input read-only (47–52).
- **Writes:** None in `--check` mode. `--emit` can create a record, but the runner does not pass it; that branch is separate (checker lines 188–202).
- **Git/history:** No Git commands in `--check` mode and no commit/history or `HEAD == --rev` requirement.
- **Network/proc:** No network or live `/proc` access; this mode only reads the record and hashes named files.

## Verdict summary

| Step | Program | Fresh detached clone at another path? | Binding reason |
|---:|---|:---:|---|
| 7 | `tools/souji-landing-gate.py --selftest` | Yes | Self-contained synthetic `/var/tmp` repositories; no selected checkout root. |
| 8 | `tests/fixtures/r18-landing-pointers.py` | **No** | Mandatory historical replay uses hardcoded `LANE` (lines 30–32, 282–306). |
| 9 | `tests/fixtures/r16-landing-gate.py` | **No** | Hardcoded `LANE/.git` check and replay root (lines 64–67, 208–236). |
| 10 | `census/round-19/probe-carry-invariants.py` | Yes | Root is derived from `__file__`; only imports the clone's gate source. |
| 11 | `tests/fixtures/r19-rev-pin.py` | Yes | Root is derived from `__file__`, with runner-provided clone-local helper and tool-dir. |
| 12 | `census/round-19/verify-agreement-pin.py --check` | Yes | Runner passes clone-local root and check record; checks current files without Git. |

The only step-level relocatability failures in this 7–12 slice are steps 8 and 9; their literal lane references remain even though the runner passes a clone-local `--tool`.