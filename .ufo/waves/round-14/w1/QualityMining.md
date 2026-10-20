# Round 14 W1 — QualityMining (Q20/Q21 proposal)

Seat: `SoujiR14.QualityMining` (leaf, executor). Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Axes: **calibration** (Q20, retained-evidence digest eligibility) and **operability** (Q21, pre-access census boundary).
Baseline: `a31642d14006830ec62edf40b0354c3699728c4a`. Write set: `census/round-14/quality-proposal.json` and this report. No code, tests, corpus, LOG, SCORECARD, SHONEN or registry edits. Certification is OFF; no deletion authority and no comprehensive recertification is claimed.

## 0. Evidence separation

**Code inspection only** (no execution): `census/round-13/run-verification.py`, `census/round-13/verification.json`, `corpus/lessons/round-13.md`, `corpus/lessons/round-13-verifier-spotcheck.md`, `corpus/lessons/round-14.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`, `PROVINCE.md`, `SKILL.md`, `tools/souji-census.sh` (baseline bytes), `tools/souji-evidence-cache.py`, `tests/fixtures/r14-evidence-cache.py`, `census/round-14/cache-demonstration.py`, `census/round-14/run-verification.py`, `census/round-14/verification-plan.json`.

**Exercised evidence:** none. This seat ran no selftest, fixture, demonstration, census, shellcheck, parse-check, git write, or source-census command. Every expected id/exit below is read from source or is a planned assertion. No tool was installed or upgraded.

## 1. Prior spotcheck pointer (required by the target)

`corpus/lessons/round-13-verifier-spotcheck.md:132`, `## Routed findings and review adjudication`, item 3:

> “Retention caveat, not a current claim failure: the runner's retained-green selection does not itself compare tool digests before retaining an old observation. … Actual per-result revisions plus the report's explicit retained-run disclosure are authoritative; top-level measured_commit must not erase them.”

Supporting observation at `:80`: the retained frozen/replay observations name `6ed10a7` individually. This is a **routed finding, not a `## Mistakes` row**; R14-M1 in `corpus/lessons/round-14.md:9` supplies the round-14 mistake row. Q20 encodes the caveat as a criterion.

## 2. Q20 — retained-evidence digest eligibility

### Exact failure precondition

In `census/round-13/run-verification.py`:

- `:31-33` loads a prior `verification.json` only with `--retry-failed`; `RETRY_NAMES` is the set of prior results whose `matched` is **false**. A prior green is therefore never re-run.
- `:48-54` `run()` returns `dict(PREVIOUS_RESULTS[name])` for every name not in `RETRY_NAMES`; it sets `measured_commit` only via `.get(...)` (falling back to the record-level revision), adds `retained_from`, and returns without reading, hashing, or even naming any dependency. `retained_from` is provenance, not eligibility.

Observed consequence in `census/round-13/verification.json` (at `a31642d`, sha256 `088eebd7…`): `evidence-frozen`, `structure-selftest`, and both `historical-replay-*` results are green with `measured_commit` `6ed10a7`, while the record-level revision is `6f8ee0f`. The r13 closure checked the unchanged bytes manually (`round-13-verifier-spotcheck.md:69-82`); the selector did not.

**Causal red-before:** a record with `matched: true` and a dependency digest captured at time T is reusable (exit 0). Change one dependency byte; the old matched-only branch still returns green, while the gate returns exit 1 `dependency-digest-mismatch`. `census/round-14/cache-demonstration.py` implements this red-before by isolating the historical `run()` branch with `ast.parse` and executing it against a synthetic record; source inspection of that design is not an executed result.

### Proposed Q20 row

A retained green observation is eligible only after a nonempty declared dependency map matches current regular non-symlink file digests, and a caller-declared required minimum is enforced so a record cannot silently narrow what is measured. The dependency digests must be captured with the original observation, not manufactured from current bytes at retention time, and the before/after dependency state must agree. Legacy/absent/empty dependencies, false or non-boolean `matched`, malformed record fields, missing/non-regular/symlink/hardlink/escaping/protected dependencies, and digest mismatches are ineligible and never reported green. Retention preserves each result's own `measured_commit`. This does not infer dependency completeness beyond the declared/required set, bind external runtimes or environment, authenticate execution, or prove the producer was re-run.

The landed gate adds an interface face beyond the shared contract: `--require REL` (repeatable) enforces a caller-chosen minimum dependency set; an undeclared required path is `dependency-undeclared`, exit 2. It raises the floor but does not prove completeness. The gate also supports `--frozen DIR` and a committed pinned snapshot; these are useful but not substitutes for the external fixture.

### Planned falsifiers (full text in the JSON)

1. `python3 -B tools/souji-evidence-cache.py --selftest` → exit 0, `selftest: N/N passed` where N is the installed `cases.append` count (32 at the last observation); re-derive if the gate digest moved.
2. `python3 -B tests/fixtures/r14-evidence-cache.py --tool tools/souji-evidence-cache.py` → exit 0, `fixture: N/N checks passed` (N≥20), exact immutable ids; missing `--tool` exits 2 with `fixture: tool missing`.
3. `python3 -B census/round-14/cache-demonstration.py` → exit 0; unchanged reusable, changed stale, legacy refused, original `measured_commit` preserved, historical branch red-before observed.
4. Direct changed-dependency probe under `/var/tmp`: first exit 0, one-byte edit, second exit 1 with `dependency-digest-mismatch`, same `measured_commit`.
5. Legacy/empty/false probes: exits 2/2/1 with `dependencies-legacy`, `dependencies-empty`, `matched-false`.
6. Required-minimum probe: declared `--require` passes; undeclared `--require` exits 2 `dependency-undeclared`.

**Current working tree (source inspection only):** `census/round-13/run-verification.py` is modified during this wave (162 insertions). Its retention branch now requires `dependencies_stable is true`, a prior per-result 40-hex `measured_commit`, and a nonempty dependency map, then calls the installed gate with a record built from the prior result's own revision and stored digests; legacy records and external-mutable commands are re-executed. The historical JSON outputs are not rewritten. This migration is **not exercised by this seat** and its gate-exit evidence is not yet in `census/round-14/verification.json`.

**Limits:** the gate never executes the recorded command. It cannot prove the dependency map was captured at observation time rather than manufactured later; Q20 forbids manufacture, but only procedure and demonstration ordering can evidence it. It cannot see undeclared/transitive dependencies, runtime versions, environment, or a post-evaluation byte change. No `--retry-failed` and no copied prior green may be used in the r14 run.

## 3. Q21 — pre-access census boundary

### Exact baseline precondition

At baseline `a31642d`, the committed `tools/souji-census.sh` (sha256 `6a000c59…`) has no protected-namespace guard. The working-tree tool changed during this wave (report-time observation sha256 `7bb73536…`, ~365 added lines) and now contains a source guard; the fixture is still absent, so no refusal is exercised. The baseline source path is:

- `main()` (`:797-830`) accepts `--root`/`--compare` with no protected-namespace guard.
- `emit_census()` (`:343`) canonicalizes `ROOT` and immediately enumerates.
- `list_repos()` (`:316`) tests `.git` and canonicalizes children.
- `emit_compare()` (`:414`) calls `load_census()` (`:362`) first; `load_census` opens the compare file before any boundary check.
- `newest_mtime()` (`:159`) runs `find` over the work tree; `worktree_extra_flags()` (`:216`) queries registered worktree paths; `scratch_bytes()` (`:140`) probes `.scratch`.

An arbitrary `--root`/`--compare` (or a repository/worktree/`.scratch` alias) can therefore reach the credential store, an ancestor, or a descendant before any refusal. This is a real access-order defect even though the census is “metadata-only”: names, modes, sizes, mtimes and git queries disclose structure.

**Grounding:** `corpus/lessons/round-14.md:11` R14-M3 (arbitrary census input can reach the credential store/ancestor; baseline `.git`/common-dir/`.scratch` readers); `corpus/lessons/round-13.md:21` R13-M7 (a guard that does not cover its claimed class is not a guard); `census/round-13/baseline-measures.md:89` (an unscoped read reached protected operator-sweep directories before narrowing — a **near-miss**, not a credential-store access); `PROVINCE.md:30,44-45` and `SKILL.md:44,59` (credentials are kagi's province; credential-shaped content is NOT-SAFE); S040 (pure path computation vs `Path.resolve` filesystem-aware resolution, so lexical rejection must precede resolution).

### Proposed Q21 row

A census invocation must refuse before repository enumeration or any `git`, `find`, `du`, digest, or content read when the effective root (explicit or default), the `--compare` input, a repository `.git`/common-dir/alternates target, or a worktree/`.scratch` target overlaps the protected credential namespace. Overlap includes the store root, any ancestor or descendant, lexical `.`/`..` aliases, and symlink aliases. Lexical component rejection runs first; filesystem-aware resolution is used only to catch aliases. Refusal is a stable named finding with exit 2 and emits no repo row; a normal out-of-boundary root keeps its legacy metadata output.

### Planned falsifiers

1. `python3 -B tests/fixtures/r14-census-boundary.py --tool <baseline>` → nonzero **for the named boundary reason**, with forbidden-access observations; not an unrelated setup failure. Baseline bytes are extracted from `a31642d` under `/var/tmp`.
2. Same fixture with `--tool tools/souji-census.sh` → exit 0; protected cases exit 2 with stable ids, no rows, no forbidden `git`/`find`/`du`/content access; safe normal root emits the legacy header plus its metadata row.
3. Direct synthetic-HOME probe: direct/descendant/ancestor/root-symlink/compare-alias → exit 2; safe root → exit 0. A synthetic prior TSV lives inside the synthetic store shape so the compare case can distinguish “read it” from “refused before open”.
4. Fixture-only gitdir/common-dir and `.scratch` symlink cases with command spies. The real credential store is never probed; tests must never use it.
5. `bash tools/souji-census.sh --selftest` and a normal fleet-root run → exit 0 (legacy interface control).

**Limits:** no universal filesystem sandbox, no race-free TOCTOU proof, no complete reader coverage beyond the enumerated census surfaces, and no real-store penetration test. A matching marker without spy/access-order evidence is not proof. Q21 is **not admitted** while the C2 fixture is absent or the guard is only source-observed.

## 4. Reconciliation with the working tree

`corpus/QUALITY.md` (working-tree sha256 `d5aeffe6…`) already contains draft Q20/Q21 rows and a `## Round 14 criteria` heading. This seat did not edit it. The JSON is the proposal/evidence record; L1 should merge, not append duplicates.

Two precise reconciliations:

- **Q20:** the draft test names the gate selftest and demonstration but not the external fixture. The JSON adds `tests/fixtures/r14-evidence-cache.py --tool …` and states that the **caller**, not the gate, re-runs the producer. It also adds the observation-time-capture clause and the `--require` floor.
- **Q21:** the draft test does not name exit 2 or the no-row requirement. The JSON adds both and adds the “protected lexical path that does not exist” case, which distinguishes lexical rejection from a resolution-dependent failure.

`corpus/lessons/round-14.md` (working-tree sha256 `e516eca5…`) already has R14-M1 and R14-M3. R14-M3's evidence pointer expects the baseline fixture observation in `census/round-14/verification.json`; that file is not present at report time, so the lesson's own capture is not yet demonstrated.

`corpus/SOURCES.md` appends S038 (coreutils timeout correction) and S040 (pathlib). **Q20/Q21 do not cite S038**; it is the C2 timeout-documentation correction, not a grounding for either criterion. S039 remains reserved and unused.

## 5. Retained evidence (paths and hashes observed)

| item | value |
|---|---|
| HEAD / baseline | `a31642d14006830ec62edf40b0354c3699728c4a` |
| prior spotcheck | `corpus/lessons/round-13-verifier-spotcheck.md` sha256 `439314a9…`; caveat at `:132`; retained note at `:80` |
| r13 runner | `census/round-13/run-verification.py` sha256 `4a304b1d…`; retention at `:31-33,48-54` |
| r13 evidence | `census/round-13/verification.json` sha256 `088eebd7…`; retained results at `6ed10a7` under record `6f8ee0f` |
| C1 gate | `tools/souji-evidence-cache.py` digest moved repeatedly during the wave; report-time observation `90ff0202…`; 32 selftest cases at that observation; `--require` present. Earlier observations: `6caaec30…`, `7b8045cd…`, `b5cf3e86…`. Re-hash; later edits may have moved it again. |
| C1 fixture | `tests/fixtures/r14-evidence-cache.py` sha256 `a6129b30…`; 361 lines; `--tool`, `MIN_CASES=20` |
| C1 demonstration | `census/round-14/cache-demonstration.py` sha256 `cb9a10b7…`; historical-branch red-before by design |
| r14 runner | `census/round-14/run-verification.py` sha256 `942283e3…`; re-runs checks, no `--retry-failed` |
| r13 runner (migrated) | baseline `a31642d:census/round-13/run-verification.py` retains by name; working tree sha256 `3c8e3f9f…` adds a gate call and dependency capture (162 insertions), source inspection only |
| verification plan | `census/round-14/verification-plan.json` sha256 `ddb96060…`; C1 literal provenance records gate `085f8edb…`, **stale against all observed gate digests**; its drift rule requires re-derivation |
| census baseline/current | baseline blob `a31642d:tools/souji-census.sh` sha256 `6a000c59…`; working tree moved repeatedly, report-time observation `7bb73536…` with a source guard, but **no C2 fixture and no exercised refusal** |
| C2 fixture | `tests/fixtures/r14-census-boundary.py` — **absent** at report time |

The gate digest changed repeatedly while this wave ran (`6caaec30…` → `7b8045cd…` → `b5cf3e86…` → `90ff0202…`), the census tool moved to `7bb73536…`, and the plan's pinned gate digest (`085f8edb…`) is older than all of them. Any expected case list must be re-derived from the installed gate at the measured commit; stale literals are could-not-evaluate, not a pass.

## 6. Risks and blockers

1. **Q21 is unproven and unadmitted.** The working-tree tool now contains a source guard, but `tests/fixtures/r14-census-boundary.py` is absent and no baseline-red/changed-green observation exists. A source guard is not a demonstrated refusal. Do not report Q21 as a fixed capability until both arms are observed with spies.
2. **Q20 is not independent yet.** The gate exists and has a 32-case self-matrix at the report-time observation; the external fixture and demonstration exist but were not run by this seat. The gate's own selftest cannot be the sole admission evidence.
3. **Observation-time manufacture is outside the gate.** A record written from current bytes at retention time can pass. Q20 forbids it; only the consumer's procedure/ordering evidences it. This is a documented limit, not a claim of complete freshness.
4. **Lexical-before-resolution is hard to prove.** The fixture should include a protected lexical path that does not exist (so lexical rejection is exercised without a resolution dependency) and spies that distinguish path metadata reads from enumeration/content reads.
5. **Digest drift.** The verification plan's C1 literals are pinned to an older gate digest. Re-derive at the final commit or classify the check could-not-evaluate.
6. **No real-store access.** Nothing here authorizes probing `~/.omp/agent`, the operator sweeps, or any sibling repo. All fixtures use synthetic HOME under `/var/tmp` with trap cleanup and no `/dev/shm`.
7. **Historical evidence is not rewritten; the runner now has an unexercised migration.** The r13 retained results and their per-result revisions stand. The working tree adds a gate call to the historical retention branch (source inspection only); until a run records its gate exit, that migration is not evidence. The baseline branch remains the documented red-before.

## 7. Final L1 commands (not run by this seat)

From `/home/vgpnk/Projects/shokunin/souji-shokunin`:

```sh
python3 -B -c 'import ast,sys; [ast.parse(open(p, encoding="utf-8").read(), p) for p in sys.argv[1:]]; print("parse-ok")' tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py tests/fixtures/r14-census-boundary.py census/round-14/cache-demonstration.py

python3 -B tools/souji-evidence-cache.py --selftest; echo "cache_selftest=$?"
python3 -B tests/fixtures/r14-evidence-cache.py --tool tools/souji-evidence-cache.py; echo "cache_fixture=$?"
python3 -B census/round-14/cache-demonstration.py; echo "cache_demo=$?"

S=$(mktemp -d /var/tmp/souji-q21-baseline.XXXXXX); trap 'rm -rf -- "$S"' EXIT
git show a31642d:tools/souji-census.sh > "$S/souji-census.baseline.sh"
chmod +x "$S/souji-census.baseline.sh"
python3 -B tests/fixtures/r14-census-boundary.py --tool "$S/souji-census.baseline.sh"; echo "boundary_red=$?"
python3 -B tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh; echo "boundary_green=$?"

bash tools/souji-census.sh --selftest; echo "census_selftest=$?"
bash tools/souji-census.sh --root /home/vgpnk/Projects/shokunin >/dev/null; echo "legacy_root=$?"
shellcheck -S warning tools/souji-census.sh; echo "shellcheck=$?"
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji; echo "sources=$?"
```

Expected: gate selftest `N/N passed` where N equals the installed `cases.append` count (32 at last observation); external fixture exit 0 with `N/N checks passed` (N≥20); demonstration exit 0 with unchanged-green/changed-stale/legacy-refused and preserved measured revision; boundary red nonzero for the named reason and boundary green exit 0 with a safe control; census selftest and normal root exit 0; shellcheck exit 0; sources census exit 0 with existing W04 advisories. The direct probe blocks and exact expected literals are in `census/round-14/quality-proposal.json` (`planned_falsifying_commands`, `final_l1_commands`).

## 8. Nonclaims

No code/test/corpus/LOG/SCORECARD/SHONEN/registry edits; only the JSON and this report. No command executed by this seat. No real credential store, operator sweep, sibling repo, or runtime state accessed. No commit, push, deletion, quarantine, or certification. Q20/Q21 remain proposed and unadmitted; certification OFF; scores remain legacy-unmapped 7/8/8. Tool installs/upgrades: none.
