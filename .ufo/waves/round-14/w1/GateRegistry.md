# R14 w1 — GateRegistry (draft gate-registry rows for C1 and C2)

Seat: `SoujiR14.GateRegistry` (scribe, leaf). Axes: **calibration**, **operability**.
Certification remains **OFF**. Receipts remain advisory. Nothing here grants deletion authority.

## Evidence separation

- **Code inspection (read, not executed):** `SKILL.md` (read tag `#BED7`, gate table at lines 118–138), `corpus/QUALITY.md` (Q4, Q6, Q7, Q9, Q10, Q17, Q18, Q19), `AGENTS.md`, `tools/souji-census.sh` (lines 1–83, 345–346, 357–420, 470–520, 600–612, 700–827), `tests/fixtures/r12-maintenance-guard.sh` (SELFTEST_EXPECTED_IDS pattern), `tests/fixtures/r13-quarantine-bounds.sh` (`--tool` baseline pattern, EXPECTED_IDS), `tests/fixtures/r13-repo-structure.sh` (ids pattern), `tools/souji-cert-evidence.py` (finding-id convention `finding <id>: <detail>`, exit map), `.ufo/waves/round-13/w1/RegistryDraft.md` (row shape precedent), `.ufo/waves/round-14/w1-spec.json`, `w1-dispatch.json` (task texts for CacheGate, CensusBoundary, GateRegistry), `w1/swarm-registry.json`, `~/.omp/agent/RULES.md` (read per directive; no other file under `~/.omp/agent/` opened).
- **Exercised evidence:** none. No command was run by this seat (no selftest, fixture, census, shellcheck, or git subcommand). Every expected value below is a design target to be confirmed by L1 against the landed files.
- **Not opened:** `census/operator-sweep-20261019/`, `census/operator-sweep-20261018/`, any credential path, any real protected store.
- **Landed state at read time:** `tools/souji-evidence-cache.py` and `tests/fixtures/r14-evidence-cache.py` do **not** exist yet (C1 executor pending). `tests/fixtures/r14-census-boundary.py` does **not** exist yet (C2 executor pending). `tools/souji-census.sh` is the pre-r14 version (827 lines as read; C2 edits pending).

## Installs / upgrades

None. This seat needed no tool and ran nothing. If L1 finds `shellcheck` absent, the channel is `sudo pacman -S --needed --noconfirm shellcheck` (RULES channel 1), and L1 must record tool, version, channel, and reason in its verification fragment.

## 1. Registry decision

Per the PROTOCOL gate standard quoted in round 13, "a tool that cannot fail is a probe." Therefore:

- `souji-census` **stays a probe** (legacy debt: its unpinned `--compare`, setup code 1, and `${TMPDIR:-/tmp}` fallbacks remain). Its verdict map gains the protected-path refusal code 2 and a finding id. Its boundary behavior is pinned by a **new gate row** `r14-census-boundary`, not by promoting the legacy probe.
- `souji-evidence-cache` is a **gate** (its verdict map can fail: 1 stale/failed; its self-test pins finding ids). Its external fixture is a second gate row `r14-evidence-cache`, following the `r13-quarantine-bounds` / `souji-cert-evidence` pattern.
- The census boundary fixture is a gate. The C2 fixture needs a baseline red arm: `--tool` pointing at the pre-r14 census must fail on the protected-path cases for the **right** reason (spy evidence), not for a missing file.

## 2. Exact replacement table for SKILL.md gate registry

Replace the whole table body under `## Gate registry` (working-tree lines ~127–138 at read time; re-locate by anchor `| name | kind | entry command |`). Keep the header row and separator row. Rows 1–2 and 4–9 are verbatim from the current table; row 3 (`souji-census`) changes; rows 10–12 are new. No `|` appears inside any cell.

```
| name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| souji-verify | probe | `bash tools/souji-verify.sh <path>...` | 0 clean, SAFE/NOT-SAFE data; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage | `TMPDIR=/var/tmp bash tools/souji-verify.sh --selftest` | none; no pinned complete id set | read-only targets; isolated selftest under TMPDIR | souji |
| souji-vault-verify | probe | `bash tools/souji-vault-verify.sh --fallback <path>...` | 0 clean, VERIFIED/NOT-VERIFIED data; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage | `TMPDIR=/var/tmp SOUJI_CLI_BIN=/bin/false bash tools/souji-vault-verify.sh --selftest` | none; no pinned complete id set | read-only source/vault; isolated selftest under TMPDIR | souji |
| souji-census | probe | `bash tools/souji-census.sh [--root DIR] [--compare PREV.tsv]` | 0 clean; 3 failed differential comparison; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage, malformed baseline, or protected root/ancestor/alias/compare refused before access (finding SOUJI-R14-CENSUS-protected-path) | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` | caller comparison is unpinned; no pinned complete selftest id set; boundary behavior pinned in tests/fixtures/r14-census-boundary.py (row r14-census-boundary) | read-only census; protected-path refusal precedes any git/find/du/content access; isolated selftest under TMPDIR | souji |
| souji-quarantine | probe | `bash tools/souji-quarantine.sh --dry-run <repo> <target>...` | 0 clean target outcome; 3 failed/refused/aborted; 4 could-not-evaluate live guard; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage | `TMPDIR=/var/tmp bash tools/souji-quarantine.sh --selftest` | no complete safety-suite baseline; receipts advisory, certification OFF | dry-run read-only; explicitly authorized action moves targets within owning repo; selftest under TMPDIR | souji |
| r12-maintenance-guard | gate | `bash tests/fixtures/r12-maintenance-guard.sh` | 0 clean; 1 failed; 2 could-not-evaluate | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` | expected counts and SELFTEST_EXPECTED_IDS in fixture; `tests/results/r12-maintenance-guard.txt` | isolated `/var/tmp/souji-r12-maintenance.*` | souji |
| souji-cert-evidence | gate | `python3 tools/souji-cert-evidence.py --root PATH --manifest PATH` or `--frozen DIR` | 0 clean declared consistency; 1 failed honest fragment; 2 could-not-evaluate malformed/inconsistent/tampered input | `python3 tools/souji-cert-evidence.py --selftest`; `python3 tests/fixtures/r13-cert-evidence.py` | embedded expected exit/finding ids; `tests/fixtures/r13-cert-frozen/expected.json` pins every input | inputs read-only; selftests isolated `/var/tmp`; never executes recorded commands | souji |
| souji-repo-structure | probe | `bash tools/souji-repo-structure.sh --repo PATH` | 0 clean metadata emitted; 2 could-not-evaluate usage/repo/promisor; 3 could-not-evaluate unsupported Git; 4 could-not-evaluate config/stderr/command/output | corresponding gate below | no live-data expected baseline | repository reads; capture-only `/var/tmp` directory removed on exit | souji |
| r13-repo-structure | gate | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | 0 clean; 1 failed; 2 could-not-evaluate | same `--selftest --probe` command | fixture SELFTEST_EXPECTED_IDS and case expectations; recorded run `census/round-13/verification.json` | isolated `/var/tmp/souji-r13-repo-structure.*` | souji |
| r13-quarantine-bounds | gate | `bash tests/fixtures/r13-quarantine-bounds.sh [--tool PATH]` | 0 clean; 1 failed case or id set; 2 could-not-evaluate usage/environment | same command, isolated positive/negative controls; baseline red arm uses `--tool` | fixture EXPECTED_IDS and per-case exit/finding/retention assertions; `census/round-13/verification.json` | isolated `/var/tmp/r13-qbounds.*` only | souji |
| souji-evidence-cache | gate | `python3 tools/souji-evidence-cache.py --root DIR --record FILE.json` (form per decision D1) | 0 reusable: every dependency a regular in-root file with digest equal to the recorded sha256, record matched true, measured_commit echoed verbatim; digest eligibility only, NOT proof that the measured run executed; 1 stale/failed: digest-mismatch, matched-false, dependency-missing, legacy-no-dependencies, empty-dependencies; 2 could-not-evaluate: record-malformed, dependency symlink/nonregular/escape/protected, root-not-directory | `python3 tools/souji-evidence-cache.py --selftest` | finding ids and exit per case pinned in the tool's selftest; must equal the id set in tests/fixtures/r14-evidence-cache.py (EXPECTED_IDS); no live digest pinned | read-only `--root` dependencies; selftest isolated under `/var/tmp` (hard-coded); never executes recorded commands; never opens protected store | souji |
| r14-evidence-cache | gate | `python3 tests/fixtures/r14-evidence-cache.py --tool tools/souji-evidence-cache.py` | 0 all cases pass (installed arm); 1 any case fails, including the baseline red arm; 2 fixture could-not-evaluate (setup, `/var/tmp` unavailable) | red arm: `python3 tests/fixtures/r14-evidence-cache.py --tool /var/tmp/r14-absent-cache.py` must exit 1 with every case failing tool-missing; the fixture itself is the self-test (no --selftest flag) | EXPECTED_IDS tuple and per-case (exit, finding-id set, measured_commit echo) assertions in fixture; input sha256 values as literals (out-of-band oracle, not computed by the tool) | isolated `/var/tmp/r14-evidence-cache.*` synthetic roots, removed by trap | souji |
| r14-census-boundary | gate | `python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh` | 0 all cases pass (installed arm); 1 any case fails, including the baseline red arm; 2 fixture could-not-evaluate (setup, `/var/tmp` unavailable, spy install failure) | red arm: `python3 tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-census.r14-baseline.sh` must exit 1 with R14C2-01, -05, -08 failing by spy evidence; the fixture itself is the self-test (no --selftest flag) | EXPECTED_IDS tuple and per-case expected exit, finding id, and spy-log assertions in fixture; baseline = pre-r14 committed census recorded by commit hash in the L1 verification fragment | isolated `/var/tmp/r14-census-boundary.*` with synthetic HOME, PATH command spies, mode-000 sentinel; never the real HOME; trap removes tree | souji |
```

Count after integration: 12 rows (9 existing, 3 new). Names are unique. Only `souji-census` changes in place.

## 3. Verdict maps and stable finding ids (proposed; CacheGate and CensusBoundary land the actual strings; L1 pins equality with the fixture)

Ids follow the r12/r13 `SOUJI-R<n>-<AREA>-<kebab>` shape and the cert-evidence `finding <id>: <detail>` line format. The fixture asserts the **set** (missing and extra both fail), as r12 and r13 do.

### 3a. souji-evidence-cache

| exit | class | finding ids (one or more) | rule |
|---|---|---|---|
| 0 | reusable | none | every dependency: regular file, contained in `--root`, no symlink component, sha256 equal to recorded value; `matched` is JSON `true`; `measured_commit` echoed unchanged |
| 1 | stale/failed | `SOUJI-R14-CACHE-digest-mismatch`, `SOUJI-R14-CACHE-matched-false`, `SOUJI-R14-CACHE-dependency-missing`, `SOUJI-R14-CACHE-legacy-no-dependencies`, `SOUJI-R14-CACHE-empty-dependencies` | well-formed record that does not establish eligibility |
| 2 | could-not-evaluate | `SOUJI-R14-CACHE-record-malformed`, `SOUJI-R14-CACHE-dependency-symlink`, `SOUJI-R14-CACHE-dependency-nonregular`, `SOUJI-R14-CACHE-dependency-escape`, `SOUJI-R14-CACHE-dependency-protected`, `SOUJI-R14-CACHE-root-not-directory` | record or environment that cannot be safely evaluated; malformed includes bad sha256 shape, bool-as-int, duplicate JSON keys, missing/empty `measured_commit`, missing `name` |

Calibration rule: a clean exit 0 is **digest eligibility over the listed dependencies only**. It is not proof that the measured command ran historically, not transitive-dependency coverage, and not a deletion verdict. That sentence must appear in the tool's `--help`/header and in the report that cites the gate.

### 3b. souji-census (C2 additions only; legacy codes unchanged)

| exit | finding id | rule |
|---|---|---|
| 2 | `SOUJI-R14-CENSUS-protected-path` | root, ancestor-of-root, or --root/SHOKUNIN_ROOT/--compare path that lexically or canonically equals, lies under, or contains the protected store, or reaches it through a symlink component; refused before any git/find/du/read |
| 0 | none | a symlink repo root or symlink `.scratch` is **skipped** (scratch_bytes 0, no follow), not refused (decision D4) |
| 2 | `SOUJI-R14-CENSUS-protected-path` | a `.git` gitfile/commondir that resolves into the protected store refuses the run (decision D3) |

Stable finding line on stderr (decision D5): `finding SOUJI-R14-CENSUS-protected-path: <which input> refused before access`. The census emits no finding ids today (only `souji-census: ...` prose), so this line is new.

Protected store definition (decision D7): `realpath($HOME/.omp/agent)`, where `$HOME` is read from the environment and the fixture sets it to a synthetic directory. Protected set = the store, its descendants, and its **ancestors** (`$HOME/.omp`, `$HOME`, `/home`, `/`). A root that is an ancestor of the store is refused because enumeration would traverse it.

## 4. Fixture case rows (exact ids; expectations are design targets)

### 4a. `tests/fixtures/r14-evidence-cache.py` (C1)

| id | scenario | expected exit | expected finding ids | assertion beyond exit |
|---|---|---|---|---|
| R14C1-01 | positive: all deps match, matched true, measured_commit set | 0 | none | output echoes measured_commit byte-identical |
| R14C1-02 | listed dependency bytes changed | 1 | digest-mismatch | — |
| R14C1-03 | unlisted file changed, listed deps unchanged | 0 | none | documents the bounded scope (nonclaim) |
| R14C1-04 | listed dependency deleted | 1 | dependency-missing | — |
| R14C1-05 | listed dependency is a symlink to a valid file | 2 | dependency-symlink | no follow (content not read) |
| R14C1-06 | malformed sha256 (wrong length / non-hex) | 2 | record-malformed | — |
| R14C1-07 | dependency path `../` escape | 2 | dependency-escape | outside file not read |
| R14C1-08 | matched is JSON false | 1 | matched-false | — |
| R14C1-09 | legacy record with no `dependencies` key | 1 | legacy-no-dependencies | never reusable |
| R14C1-10 | `dependencies` is `{}` | 1 | empty-dependencies | never reusable |
| R14C1-11 | matched is `1` (bool-as-int) | 2 | record-malformed | — |
| R14C1-12 | duplicate JSON key | 2 | record-malformed | — |
| R14C1-13 | measured_commit missing or empty | 2 | record-malformed | never substituted with HEAD |
| R14C1-14 | dependency is a FIFO or directory | 2 | dependency-nonregular | refused by lstat before open (a FIFO open would hang) |
| R14C1-15 | dependency path inside synthetic `$HOME/.omp/agent` | 2 | dependency-protected | store never opened |
| R14C1-16 | root is not a directory | 2 | root-not-directory | — |
| R14C1-17 | red arm: `--tool` points at absent file | 1 (fixture) | all 16 cases FAIL with tool-missing | fixture exit 1, not 2 |

Falsifier for the fixture: its expected sha256 values are hard-coded literals computed out-of-band with `sha256sum`. A fixture that derives expected digests by importing the tool's hash function is a tautology and must be rejected.

### 4b. `tests/fixtures/r14-census-boundary.py` (C2)

Synthetic layout under `/var/tmp/r14-census-boundary.*`: a fake `HOME` containing `.omp/agent/` (mode 000 sentinel file inside, so any read attempt yields `Permission denied` on stderr, which the fixture asserts is absent); a fake lane with `tools/` copy; PATH shim directory whose stubs for `git`, `find`, `du`, `cat`, `head`, `grep`, `stat`, `sha256sum` log argv and cwd to a file and then exec the real binary.

| id | scenario | expected exit | expected finding | spy/sentinel assertion |
|---|---|---|---|---|
| R14C2-01 | --root equals synthetic `$HOME/.omp/agent` | 2 | protected-path | no git/find/du entry; no store-argv entry; no permission-denied |
| R14C2-02 | --root is a descendant of the store | 2 | protected-path | same |
| R14C2-03 | --root equals `$HOME` (ancestor of store) | 2 | protected-path | same |
| R14C2-04 | --root equals `$HOME/.omp` (ancestor of store) | 2 | protected-path | same |
| R14C2-05 | --root is a symlink in /var/tmp that resolves into the store | 2 | protected-path | canonical check before any stat of the root's children |
| R14C2-06 | --root lexically outside but spelled with `..` or trailing `/` into store | 2 | protected-path | — |
| R14C2-07 | no --root; `SHOKUNIN_ROOT=$HOME` (env poisoning) | 2 | protected-path | same guard as --root |
| R14C2-08 | --compare names a file inside the store | 2 | protected-path | baseline never read (no cat/head entry, no permission-denied) |
| R14C2-09 | --compare is a fleet symlink resolving into the store | 2 | protected-path | same as R14C2-08 |
| R14C2-10 | fleet repo `.git` gitfile/commondir resolves into the store | 2 | protected-path | no git invocation against that repo (decision D3) |
| R14C2-11 | repo `.scratch` is a symlink into the store | 0 | none | scratch_bytes 0; no find/du entry under store (decision D4) |
| R14C2-12 | repo root itself is a symlink | 0 | none | row skipped, not followed |
| R14C2-13 | positive: normal synthetic fleet, root outside store | 0 | none | header byte-identical to legacy `repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags`; two runs byte-identical |
| R14C2-14 | positive: default root (no --root, SHOKUNIN_ROOT unset), synthetic lane copy | 0 | none | default resolves to parent of copied lane, not protected |
| R14C2-15 | legacy compare preserved: identical baseline | 0 | none | header-only diff |
| R14C2-16 | legacy compare preserved: mutated baseline | 3 | none | diff rows present |
| R14C2-17 | red arm: `--tool` = pre-r14 baseline | 1 (fixture) | R14C2-01, -05, -08 FAIL | baseline spy log shows git/find/du access to protected root BEFORE refusal (proof the test discriminates) |

Note: R14C2-15/16 (`--compare` legacy) are included so the refusal logic cannot silently break the legacy interface. R14C2-17 fails for the right reason only if the spy log shows real pre-access (not a missing file).

## 5. Pinned-value paths (what is frozen and where)

| pinned value | location | notes |
|---|---|---|
| C1 expected finding-id set | `tests/fixtures/r14-evidence-cache.py` EXPECTED_IDS tuple | must equal tool `--selftest` id set; missing and extra both fail |
| C1 per-case exit and finding sets | same fixture, case table | per 4a |
| C1 input digests | same fixture, literal sha256 strings | out-of-band oracle |
| C2 expected finding ids | `tests/fixtures/r14-census-boundary.py` EXPECTED_IDS | per 4b |
| C2 forbidden-command list | same fixture, FORBIDDEN tuple (git, find, du, cat, head, grep, stat, sha256sum) | spy names taken from grep of the effective tool's external calls, not from memory |
| C2 baseline identity | L1 verification fragment: `git rev-parse HEAD` before edit, plus `git show <hash>:tools/souji-census.sh` digest | pre-r14 bytes are the red-arm input |
| Legacy census | no pinned baseline (unchanged) | probe only |

No pinned value contains a live fleet digest, a live repo SHA, or any path under the real `~/.omp/agent`.

## 6. Write scopes and owners

| file | status | owner (writes) | must not write |
|---|---|---|---|
| `tools/souji-evidence-cache.py` | new | CacheGate (executor) | any other file |
| `tests/fixtures/r14-evidence-cache.py` | new | CacheGate (executor) | tool file |
| `tools/souji-census.sh` | edit | CensusBoundary (executor) | fixtures, registry |
| `tests/fixtures/r14-census-boundary.py` | new | CensusBoundary (executor) | tool file |
| `census/round-14/cache-demonstration.py` | new | RetentionRunner (executor) | everything else |
| `census/round-14/verification-plan.json` | new | FinalEvidencePlan (executor) | everything else |
| `SKILL.md` gate table (section 2 block) | edit | **L1 only** | this seat, all labrats |
| `SCORECARD.md`, `LOG.md`, `SHONEN.md`, `corpus/SOURCES.md`, `corpus/QUALITY.md` | shared bookkeeping | **L1 only** (Bookkeeping, SourceLedger propose; L1 integrates) | — |
| `.ufo/waves/round-14/w1/*.md` | per-seat reports | each seat writes its own | others |
| `census/round-14/verification*` (verification fragments) | recorded run output | **L1 only** | — |

Per AGENTS.md, workers write only their own evidence fragments. This seat wrote only `.ufo/waves/round-14/w1/GateRegistry.md`.

## 7. Decisions that must be settled before the rows are pinned

These are the places where the draft has to bend to what the executors land. Each is a calibration or operability question, not a design preference.

- **D1 `--record` form.** The shared-interface text says `--record JSON`. If argparse takes a file path, the row reads `--record FILE.json` (as drafted). If it takes inline JSON, the row must read `--record '<json>'`. L1 must copy the landed argparse help, not this draft.
- **D2 legacy/empty deps exit.** Drafted as **1** (well-formed, not eligible). Malformed hashes and malformed records are **2**. CacheGate must confirm; a mismatch changes the verdict map and the 4a expectations together.
- **D3 gitdir alias into store.** Drafted as **refuse the run, exit 2** (fail closed), not skip. Rationale: a gitfile that reaches credentials is an access path, and "when uncertain, NOT-SAFE" applies. CensusBoundary may choose skip-only if it documents why, but then R14C2-10 changes.
- **D4 scratch/repo symlink.** Drafted as **skip, exit 0**, scratch_bytes 0. Matches the census header ("Does not follow symlinks").
- **D5 finding line.** `finding SOUJI-R14-CENSUS-protected-path: ...` on stderr. The census prints no finding ids at HEAD, so this is new output; the default TSV on stdout must stay byte-identical (R14C2-13).
- **D6 oracle independence.** Fixture digests are literals. Reject any fixture that computes its expected digest with the tool's own code.
- **D7 protected set.** Store = `realpath($HOME/.omp/agent)`; ancestors refused. Confirm CensusBoundary uses `$HOME` from env and that the fixture sets it to a synthetic path.
- **D8 Q4 debt in the census.** `tools/souji-census.sh` has `${TMPDIR:-/tmp}` at lines 418 and 516 (grep-observed at read time). The new code path added by C2 must use a hard-coded `/var/tmp`. Whether the legacy lines are also changed is CensusBoundary's call; the registry command sets `TMPDIR=/var/tmp` either way, and the probe row keeps its legacy-debt wording.
- **D9 stale header.** `tools/souji-census.sh` lines 9–10 name `tools/souji-census.impl-33.sh`. Fix to `tools/souji-census.sh` in the C2 edit (Q2/Q10 drift). Not a registry change.

## 8. Conformance debt observed (not fixed by this seat)

| debt | location | rule | owner for fix |
|---|---|---|---|
| `${TMPDIR:-/tmp}` fallbacks | `tools/souji-census.sh:418`, `:516` | Q4 | CensusBoundary (D8) |
| setup failure exit 1 (gate map says 1 = failed) | `tools/souji-census.sh:818–819` | gate convention | legacy debt, keep wording in probe row |
| protected-root/compare checks absent; baseline read before any guard | `tools/souji-census.sh:414–416`, `:821–822` | pre-access refusal | CensusBoundary (C2 target) |
| stale tool name in header | `tools/souji-census.sh:9–10` | Q2/Q10 | CensusBoundary (D9) |
| no finding ids in census output | whole tool | stable finding contract | CensusBoundary (D5) |

## 9. Final L1 commands (ordered; L1 only; this seat ran none)

Pre-flight and pinning (read-only except the baseline file in /var/tmp):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show <PRE_R14_HEAD>:tools/souji-census.sh > /var/tmp/souji-census.r14-baseline.sh
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-evidence-cache.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-evidence-cache.py /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py /var/tmp/souji-census.r14-baseline.sh
```

Containment (Q17) and Q4 conformance:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py tools/souji-census.sh tests/fixtures/r14-census-boundary.py; do test -f "$f" && ! test -L "$f" || echo "NOT-REGULAR $f"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c 'TMPDIR:-/tmp' tests/fixtures/r14-evidence-cache.py tests/fixtures/r14-census-boundary.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c '/var/tmp' tests/fixtures/r14-evidence-cache.py tests/fixtures/r14-census-boundary.py
```
Expected: the first `grep -c` prints 0 for each file; the second prints ≥1 for each file. Any `NOT-REGULAR` line is a stop.

Lint (Q9; shellcheck absent → install per channel 1 and record):

```
shellcheck -S warning /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; echo rc=$?
shellcheck -S warning /var/tmp/souji-census.r14-baseline.sh; echo rc=$?
```
Expected: installed census rc=0. If the baseline has pre-existing warnings, record both outputs; the requirement is no **new** warnings in the edited file.

C1 gate (CacheGate):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tools/souji-evidence-cache.py --selftest; echo rc=$?
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tests/fixtures/r14-evidence-cache.py --tool tools/souji-evidence-cache.py; echo rc=$?
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tests/fixtures/r14-evidence-cache.py --tool /var/tmp/r14-absent-cache.py; echo rc=$?
```
Expected: 0; 0 with every case PASS; **1** with every case FAIL (tool-missing). An exit 2 on the third line means the red arm could not evaluate and is not a valid red.

C2 gate (CensusBoundary):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-census.r14-baseline.sh; echo rc=$?
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh; echo rc=$?
```
Expected: first **1** with R14C2-01, -05, -08 FAIL by spy evidence (not by missing file); second **0** with all cases PASS.

Legacy probe (recorded, not gated):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && TMPDIR=/var/tmp bash tools/souji-census.sh --selftest; echo rc=$?
```
Expected: 0; record the last line. Not a pin.

Demonstration (RetentionRunner's output; L1 runs only if RetentionRunner lands):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 census/round-14/cache-demonstration.py; echo rc=$?
```

Forbidden for every L1 and seat command (protected store):

- no `bash tools/souji-census.sh --root ~`, `--root /home/vgpnk`, `--root /`, or any `--root` that is an ancestor of `~/.omp/agent`
- no `ls`, `cat`, `grep`, or `find` under `~/.omp/agent`
- no `census/operator-sweep-20261019/` or `census/operator-sweep-20261018/` reads or writes

Integration (L1 only): replace the table block in section 2 of this report into `SKILL.md`, re-locating by anchor; confirm no duplicate names; confirm the 12 rows; record the registry commit or working-tree digest in the verification fragment.

## 10. Nonclaims carried into the registry

- The cache gate, if green, establishes **digest eligibility over listed dependencies**. It does not prove the measured command ran, does not cover transitive dependencies, and does not authorize deletion.
- The census boundary gate establishes **refusal before access for the enumerated cases**. It does not certify the census, does not cover every filesystem alias the kernel can produce, and does not replace the per-artifact receipt workflow.
- Certification remains OFF. Q18: the integrity verdict never grants deletion authority.
- No row cites S038 or S039. If SourceTimeout's S038 lands, L1 may cite it only in the round LOG entry, not in these gate rows.

## 11. Risks and blockers

- **Moving targets (risk).** Both executor files are absent at read time. Every expected id and exit above is a design target until the files land. The rows must be re-derived from landed argparse and fixture tables, not copied from this draft.
- **Ambiguous `--record` (risk).** See D1. A wrong form makes the row unrunnable and must not be pinned.
- **Shared SKILL.md (risk).** Round-13 notes show SKILL.md is edited by other seats. L1 re-locates the table by anchor.
- **No blocker.** Everything needed for the draft was reachable by read.
