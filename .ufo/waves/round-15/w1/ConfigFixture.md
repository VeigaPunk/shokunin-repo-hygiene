# ConfigFixture — round 15, w1 (executor, leaf)

Scope: `tests/fixtures/r15-census-config.py` only. C1 operability paired red/green gate for the r14 rejected-harmed value-blind Git config refusals; C2 interface for the admission checker. Axes: operability, calibration.
Mode: SOURCE INSPECTION ONLY for tool/reports; the fixture itself was written, never executed (no probes, no compile run, no fixture run — L1 executes acceptance).

## Files changed

- `tests/fixtures/r15-census-config.py` (new, ~1330 lines) — sole owned file.

## Interface (reported to SoujiR15.RoundRunner / AdmissionChecker / ConfigRepair)

- CLI: `python3 -B tests/fixtures/r15-census-config.py --tool PATH`. Optional `--case ID` (repeatable; gate/admission runs must omit — the no-`--case` run asserts `ran == EXPECTED_IDS` exactly), `--list`, `--json`. Default tool: lane `tools/souji-census.sh`.
- Exit: 0 all-pass, 1 any case fail, 2 usage/setup/oracle failure (exit 2 emits zero CASE rows — root-uid refused, missing tool, missing strace/git, or strace probe not observing EACCES on the mode-000 store).
- Records: `TOOL\t<abs>\tsha256=<hex>`; `TOOL-KIND\tr14-harm-baseline` (sha256 fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9, current installed r14 tool — verified via `sha256sum` this session), `pre-harm-a31642d` (6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026, same digest as r14 fixture's BASELINE_SHA), else `other`; `CASE\t<ID>\tPASS|FAIL\t<detail>` with `observed_exit=<int>` and `observed_finding=<finding:reason|none>` (parsed from `souji-census: <finding>: <reason>` stderr) appended to every detail; `SUMMARY\ttotal=N\tfailed=M`; `--json` appends one `JSON\t{...}` line (ids, classes, harm set, tool digest/kind, per-case exit/finding/problems/runs).
- Timing: per-invocation timeout 90s (strace probe 20s, setup 60s). ~30 tool invocations total — well inside RoundRunner's 240s bound.

## Pinned EXPECTED_IDS (20) and classes

| id | class | content |
|---|---|---|
| R15CFG-01 | benign | include.path in-gitdir relative, out-of-repo `../../` fleet file, missing target, `~`; includeIf onbranch/gitdir/hasconfig with benign targets |
| R15CFG-02 | refusal | include/includeIf targets into store: direct, gitdir-nonmatch, hasconfig-nomatch, unknown-condition, nested via accepted file, symlink into store |
| R15CFG-03 | refusal | include cycle (a↔b), `~user` form, FIFO target, NUL-containing config |
| R15CFG-04 | benign | hooksPath /dev/null + store + in-gitdir dir w/ post-index-change sentinel (never runs); fsmonitor command sentinel (never runs); attributesFile /dev/null + safe in-gitdir path honored; excludesFile /dev/null +untracked → dirty=1, excludesFile '*' → clean (both equal pre-harm rows) |
| R15CFG-05 | preserve | dirty fidelity: modified+untracked → dirty=2 flag dirty; repo `.gitignore` honored → clean |
| R15CFG-06 | benign | complete-repo promisor markers: all spellings (false/empty/off/0/true/bare/yes/2) + partialCloneFilter → 9 clean rows; no lazy-fetch pin (moved to 08) |
| R15CFG-07 | refusal | promisor invalid booleans only (maybe, banana) → could-not-evaluate |
| R15CFG-08 | safety | sentry fleet: hooks/fsmonitor exec sentinels must not fire; GIT_NO_LAZY_FETCH=1 pinned on observed git calls |
| R15CFG-09 | benign | extensions.partialClone false/empty/origin = remote-name markers, inert on a complete repo |
| R15CFG-10 | benign | worktreeConfig false/empty/off incl. hostile stray config.worktree (no_open asserted); true + benign config.worktree: main relative core.worktree=.. and linked admin absolute core.worktree → worktrees=2 clean |
| R15CFG-11 | refusal | worktreeConfig true+hostile config.worktree (include→store, core.worktree→store), invalid value, attributesFile→store, excludesFile→store |
| R15CFG-12 | benign | alternateRefsCommand empty value + plain control |
| R15CFG-13 | benign | unbound filter.* drivers incl. a command sentinel (no reachable attributes binding) — never executed |
| R15CFG-14 | refusal | attribute-bound filter.clean/process; non-empty alternateRefsCommand |
| R15CFG-15 | benign | key-parse FPs: remote include.d, remote+branch promisor pair, filter.required+diff.clean.driver span, x.promisor-mirror |
| R15CFG-16 | benign | mixed fleet a-benign/m-safe-config/z-benign: exact row set, basename order, pinned fields |
| R15CFG-17 | refusal | mixed fleet with unsafe child: rc 2, empty stdout |
| R15CFG-18 | preserve | poisoned HOME/.gitconfig + GIT_CONFIG_GLOBAL/GIT_DIR/GIT_CONFIG_* env: census still emits exact rows; spy pins GIT_CONFIG_GLOBAL=/dev/null and GIT_DIR="" |
| R15CFG-19 | refusal | retained namespace: --root <store> and --root <HOME ancestor> → path-protected |
| R15CFG-20 | preserve | --compare identical rc 0, drift rc 3, malformed rc 2 |

HARM_CASES (expected FAIL on fcff8b05, descriptive for the checker): 01,04,06,08,09,10,12,13,15,16. The fixture applies the identical behavioral oracle to every arm — no digest-keyed verdicts (L1 correction applied); non-discrimination is the admission checker's refusal, not a fabricated fixture FAIL.
## Access oracles (r14 patterns retained, tightened)

- PATH spies: find/du/git/cat/head/tail/readlink/stat/realpath log cwd+argv+12 GIT_* vars; spy hits containing the synthetic store are failures on every case; `spy_git_env` extracts per-invocation pinned env values (lazy-fetch, global config, GIT_DIR).
- strace oracle: strict mode — ANY stat/open/getdents64/readlink/exec naming the synthetic store is a hit (r14 allowed a root stat for its scratch-symlink control; no such case exists here). EACCES anywhere is a hit; first execve ignored; store root mode 000, sessions/canary planted before chmod.
- Execution sentinels split by class: inert (altrefs command, unbound filter command) asserted arm-independently — no census command can fire them; exec sentinels (hook script, fsmonitor command) asserted ONLY in the safety case R15CFG-08 — a correct pre-harm arm may legitimately fire them, so benign rows never carry the assertion. Neutral-fleet helper markers are presence-only and asserted nowhere.
- `no_open` strace assertion on `.git/config.worktree` for the worktreeConfig-off fleet (inertness control).
- Dirty fidelity is field-exact (not exit-0): dirty counts and verdict flags pinned per repo, row-set equality (catches the rows=("$row") overwrite mutation — single-repo controls stay green, multi-repo fleets catch it).
- Helper files (hooks, fm.sh, crypt.sh, altrefs.sh, attrs/ignore files, include targets) live under `.git/` so they are invisible to `git status` and cannot inflate dirty counts; include.path values are gitdir-relative, matching git's lexical-base rule.

## Design decisions / conflicts flagged (not pinned without L0)

1. **alternateRefsCommand non-empty**: fixture encodes REFUSE (ConfigRepair lock: "no safe non-empty value"). AlternateRefs.md argues any value is inert (census invokes no alternate-refs consumer) and wants A4-style green + sentinel. If L0 rules green, move r-altrefs-cmd/exit/bare to the benign fleet — case is isolated for the flip.
2. **promisor markers on complete repos**: RESOLVED by L1 — all valid promisor spellings, partialCloneFilter, and partialClone (remote names incl. "false") are benign; only invalid booleans refuse. Encoded in 06/07/09.
3. **unbound non-empty filters green** (L1 directive) vs ConfigRepair's "non-empty = refuse" — fixture follows L1: r-filter-crypt (command sentinel, unbound) is green.
4. **includeIf gitdir:/nonexistent + store target**: fixture encodes REFUSE (condition-blind fail-closed, IncludeIfSafe F4). ConfigRepair's "skip inactive includeIf" would make it green — conflict disclosed.
5. **r-wtc-on `core.worktree = ..`**: legitimate per git (resolves to worktree); if repair refuses `..` values this subcase fails — contested shape disclosed to ConfigRepair.
6. **hooksPath→store accepted-neutralized** (no hook event ever fires) — alternative boundary-check repair would fail this subcase; disclosed.
7. Unsafe-value findings allowed reasons tuple CONFIG_REASONS (git-config-*|git-include-*|git-metadata-*|*-protected) — exact reason strings are the repair's; only the `path-protected:` prefix is required.

## Risks / limitations

- Fixture not executed (contract: source-only wave). Row-field expectations derive from committed census schema (HEADER, `clean`/`dirty`/`wt-*` flags) — a repaired tool changing verdict vocabulary needs the expectation table re-pinned; flagged.
- `r-inc-out` (out-of-repo, unprotected `../../` include) is green per IncludeIfSafe N1 (fleet file admitted). If repair restricts includes to in-repo only, this subcase fails — boundary breadth is the contested bit.
- `no_open` matches literal `config.worktree` in open/openat lines only (not stat) — stat coverage is the store oracle's job for protected paths.
- One boundary-read performed: `sha256sum tools/souji-census.sh` to pin the harm digest (fcff8b05…) — matches FixtureCounts.md D2. No census/operator-sweep path opened; all reads were explicit fixture/tool/report paths.

## Unrun checks for L1

1. `python3 tests/fixtures/r15-census-config.py --tool tools/souji-census.sh` — all 20 PASS (once repair lands).
2. Same on the r14-harm copy → exactly HARM_CASES fail; on a31642d → all benign cases pass, new-guard refusal cases fail (expected).
3. `--list | wc -l` == 20; JSON arm consumed by AdmissionChecker/expected.json.
4. `shellcheck`/selftest on the repaired tool (parent owns).

Tool installs/updates: none. No pacman transactions.
