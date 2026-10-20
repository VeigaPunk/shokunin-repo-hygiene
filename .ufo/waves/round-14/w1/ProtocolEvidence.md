# ProtocolEvidence — round 14 wave w1

Seat: `SoujiR14.ProtocolEvidence` (scout, leaf).
Axes: calibration, operability.
Contract & Execution: read-only evaluation. No execution of gates, suites, fixtures, builds, linters, or smoke runs. No tool installs or updates performed (tooling directive: none installed, none upgraded). Reads confined to lane files, canonical `PROTOCOL.md`, and peer communication channels. No writes except this report.

---

## 1. Summary Determination

**Determination: YES.** Under the canonical PROTOCOL Gate standard (`PROTOCOL.md` lines 375–424, specifically lines 390–397 "Two evidences"), the standalone eligibility gate (`tools/souji-evidence-cache.py`) grades mutable fleet artifacts and strictly requires a committed frozen input snapshot fixture with an `expected.json` pinning the SHA-256 digests of all snapshot inputs.

Without a committed frozen input snapshot:
1. The eligibility gate evaluates mutable artifacts: the cache record JSON itself (which declares `{name, matched, measured_commit, dependencies}`) and the dependency files in `--root DIR` (lane tools, shell scripts, fixtures, data tables).
2. Any edit, update, deletion, or movement of those files modifies the live verdict dynamically (e.g. flipping exit 0 `reusable` to exit 1 `stale/failed` via `digest-mismatch`).
3. Running solely an embedded `--selftest` in a temporary directory proves capability only, not an immutable measurement ("Self-test green is capability, not a measurement", `PROTOCOL.md:390`).
4. To satisfy the PROTOCOL Gate standard, a gate whose verdict depends on mutable fleet artifacts must ship a committed frozen input snapshot with its committed expected verdict, so any future mutation or tampering is detected as `snapshot_tampered` (exit 2, could-not-evaluate) rather than a silently shifted verdict.

---

## 2. Canonical Gate Standard Analysis

### 2.1 Gate Definition vs. Probe Definition
Per `PROTOCOL.md:377–379`:
- A **gate** is a committed, re-runnable verdict script a lane owns: it reads surfaces, compares them against expected values persisted in its own repo, and returns a verdict.
- A **probe** is a tool that cannot fail, and is registered as one.
- In `SKILL.md:118–138`, receipt tools (`souji-verify`, `souji-vault-verify`, `souji-census`, `souji-quarantine`) are registered as probes because their live verdicts are data and expected baselines are unpinned. In contrast, `r12-maintenance-guard`, `souji-cert-evidence`, and `r13-quarantine-bounds` are registered as gates with explicit exit maps and pinned expected values.

### 2.2 The "Two Evidences" Obligation
Per `PROTOCOL.md:390–397`:
- **Clause 1 (Self-test):** Every gate must expose a self-invocation mode over isolated fixtures under `/var/tmp` asserting both the exit code and a stable expected finding-id, with expected values committed and independent of recomputation.
- **Clause 2 (Frozen run):** A gate whose verdict depends on a mutable fleet artifact *must also ship a run over a committed input snapshot with its committed expected verdict*, so a later hand-edit of that artifact contradicts the frozen run.
- **Clause 3 (Digest pinning):** A frozen baseline's `expected.json` *MUST pin the digest of every snapshot input file*, and the gate verifies those digests before comparing verdicts. An edited snapshot is `snapshot_tampered` (could-not-evaluate, exit 2), not a compared verdict, and a baseline without digests is reported `unpinned (legacy)`.

### 2.3 Evaluation of `tools/souji-evidence-cache.py` Against the Standard
The C1 shared interface (`w1-spec.json`) defines `souji-evidence-cache.py`:
- CLI: `--root DIR --record JSON` (plus `--frozen DIR` and `--selftest`).
- Record schema: `{name, matched: bool, measured_commit: str, dependencies: {relative-path: sha256}}`.
- Verdict: exit 0 `reusable`, 1 `stale/failed`, 2 `malformed/could-not-evaluate`.

Because the inputs (the record JSON and the files cited in `dependencies`) are mutable workspace files:
- If evaluated against the live repository (`--root . --record <some-record.json>`), the outcome is non-deterministic with respect to git working-tree state.
- If dependency files are modified or uncommitted edits exist, the gate reports `stale` (exit 1).
- If the record is edited by a human or model, the gate evaluates whatever was written.
- Therefore, the gate cannot stand as a conformant PROTOCOL gate on live inputs alone: it requires the frozen baseline path (`--frozen DIR`) operating on a committed directory with an `expected.json` digest manifest.

---

## 3. Minimum Real Committed Frozen Input Snapshot Schema

To satisfy `PROTOCOL.md:390–397` with zero superfluous abstraction, the committed frozen snapshot requires exactly three files in a dedicated directory:

### 3.1 Recommended Directory Layout
```text
tests/fixtures/r14-cache-frozen/
├── expected.json
├── record.json
└── dependency.txt
```

### 3.2 Schema Specifications

#### File 1: `record.json`
The target record to evaluate, strictly conforming to the C1 shared interface:
```json
{
  "name": "r14-cache-frozen-sample",
  "matched": true,
  "measured_commit": "15d95e380ca9ab61495448e3901899bcb276d4b3",
  "dependencies": {
    "dependency.txt": "<sha256-of-dependency.txt>"
  }
}
```
*Constraints:*
- `name`: non-empty string label.
- `matched`: JSON boolean literal `true` (not string, not integer, not null).
- `measured_commit`: 40-character lowercase hex git SHA (retained from measured baseline).
- `dependencies`: non-empty object mapping safe relative path to 64-character lowercase hex SHA-256.

#### File 2: `dependency.txt`
A regular, non-symlink file with fixed, deterministic content, e.g.:
```text
souji-r14-evidence-cache-frozen-sample-v1
```

#### File 3: `expected.json` (The Trust Anchor)
Conforms to the PROTOCOL Gate standard `expected.json` specification:
```json
{
  "schema": "souji-evidence-cache-expected-v1",
  "gate": "tools/souji-evidence-cache.py",
  "record": "record.json",
  "expected_exit": 0,
  "expected_verdict": "reusable",
  "expected_finding": "eligible",
  "files": {
    "record.json": "<sha256-of-record.json>",
    "dependency.txt": "<sha256-of-dependency.txt>"
  }
}
```

### 3.3 Gate Enforcement Behavior for `--frozen DIR`
When invoked as `python3 tools/souji-evidence-cache.py --frozen DIR`:
1. **Manifest pre-check:** Reads `DIR/expected.json`. If missing or unparseable → exit 2 (`frozen-unreadable` / `frozen-malformed`).
2. **Digest validation:** For every entry in `files`:
   - Checks that the file exists under `DIR`, is a regular file (`O_NOFOLLOW`, `st_nlink == 1`), and has no directory escapes (`..`).
   - Computes SHA-256; if digest does not match declared value → emits `finding snapshot_tampered: <relpath> digest mismatch` and exits 2.
3. **Residue / completeness check:** Checks that no unlisted regular files exist in `DIR` (excluding `expected.json`). Any unlisted file emits `finding snapshot_tampered: unlisted file <relpath>` and exits 2.
4. **Eligibility evaluation:** Evaluates the target record (`DIR/record.json`) against root `DIR`.
5. **Verdict comparison:** Compares observed exit code and finding against `expected_exit` and `expected_verdict`. Disagreement emits `finding snapshot-verdict-mismatch` and exits 2. Matching produces exit 0 (`clean`).

---

## 4. Ownership and Write Scope Analysis

### 4.1 Historical Debt and Lesson
In Round 13 (`ReviewGateStandard.md:30–35`), Finding F1 noted:
> "F1 (HIGH, calibration/operability) — the mandated frozen snapshot has no owner. EvidenceGate owns only tools/souji-cert-evidence.py and tests/fixtures/r13-cert-evidence.py... A single .py fixture that builds its inputs in a mktemp dir produces no committed snapshot, so the obligation cannot be met by construction."

### 4.2 Round 14 Assignment & Coordination
- In Round 14 initial dispatch (`w1-spec.json`), `CacheGate` was assigned two files (`tools/souji-evidence-cache.py` and `tests/fixtures/r14-evidence-cache.py`).
- During wave execution, parent steering message (`history://SoujiR14.CacheGate:94–96`) explicitly expanded C1 scope:
  > "Additional C1 protocol need: own tests/fixtures/r14-cache-frozen/ too; committed minimal dependency.txt + record.json + expected.json pinning every input digest and expected clean result. Add --frozen DIR verifies input pins before --record validation, tampered → snapshot_tampered exit2. No tests now. C1 scope declared eligibility only, not universal complete dependency set or historical execution. Main will run frozen fixture once."
- **Recommended Ownership:**
  - **Author / Initial Committer:** `SoujiR14.CacheGate` writes the frozen directory snapshot (`tests/fixtures/r14-cache-frozen/{expected.json, record.json, dependency.txt}`) alongside the tool and fixture.
  - **Integrator / Final Verification:** L1 (`SoujiR14` / main agent) verifies that `expected.json` matches independent SHA-256 sums and commits it in the round integration commit.
  - **Registry Scribe:** `SoujiR14.GateRegistry` drafts the SKILL.md registry row referencing `tests/fixtures/r14-cache-frozen/expected.json` as the pinned-value path.

---

## 5. Recommended SKILL.md Gate Registry Row

To satisfy `PROTOCOL.md:398–406` (8-field schema), the registry row for C1 should be:

| Field | Value |
|---|---|
| **name** | `souji-evidence-cache` |
| **kind** | `gate` |
| **entry command** | `python3 tools/souji-evidence-cache.py --root DIR --record JSON` or `--frozen DIR` |
| **verdict map (code → class)** | `0 clean (reusable); 1 failed (stale/digest-mismatch); 2 could-not-evaluate (malformed/tampered/symlink)` |
| **self-test command** | `python3 tools/souji-evidence-cache.py --selftest; python3 tests/fixtures/r14-evidence-cache.py` |
| **pinned-value path** | embedded finding ids in fixture; `tests/fixtures/r14-cache-frozen/expected.json` pins snapshot inputs |
| **write scope** | inputs read-only; selftests isolated `/var/tmp`; never executes recorded commands |
| **owner** | `souji` |

---

## 6. Code Inspection vs. Exercised Evidence

Per round contract:
- **Code Inspection (Observed Facts):**
  - Canonical `PROTOCOL.md` lines 375–424 read at fleet root; lines 390–397 define the mandatory two evidences (self-test + frozen input snapshot with `expected.json` digest pins).
  - `SKILL.md` lines 118–138 read at lane root; confirms distinction between legacy receipt probes and PROTOCOL-compliant gates (`r12-maintenance-guard`, `souji-cert-evidence`, `r13-quarantine-bounds`).
  - `census/round-13/run-verification.py:49–54` and `corpus/lessons/round-13-verifier-spotcheck.md:70–80` read; demonstrates how retained green results in round 13 lacked digest-bound invalidation, motivating round 14 C1.
  - `w1-spec.json` and `w1-dispatch.json` read; confirms C1 interface (`--root`, `--record`, exit 0/1/2) and CacheGate write scope.
  - `history://SoujiR14.CacheGate` read; confirms parent instruction to author `tests/fixtures/r14-cache-frozen/`.
- **Exercised Evidence (Runtime Execution):**
  - **None performed.** As a leaf scout, this seat executed zero commands, builds, fixtures, or tests.
  - All executable assertions are specified below for L1.

---

## 7. Recommended Final L1 Commands

The following commands are recommended for the main agent (L1) during final round integration:

```bash
# 1. Static validation of Python syntax (no runtime execution)
python3 -m py_compile tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py

# 2. Confirm no command execution capability in cache gate (Q18 safety)
grep -nE 'subprocess|os\.system|eval\(|exec\(|shell=True' tools/souji-evidence-cache.py
# Expect: 0 hits

# 3. Confirm hermetic scratch isolation in fixture (Q4, Q16)
grep -c '/dev/shm' tests/fixtures/r14-evidence-cache.py
# Expect: 0
grep -c '/var/tmp' tests/fixtures/r14-evidence-cache.py
# Expect: >= 1

# 4. Independent re-derivation of frozen snapshot digests (anti-self-blessing)
python3 - <<'PY'
import hashlib, json, pathlib, sys
frozen_dir = pathlib.Path("tests/fixtures/r14-cache-frozen")
expected = json.loads((frozen_dir / "expected.json").read_text(encoding="utf-8"))
for rel, expected_sha in expected["files"].items():
    actual_sha = hashlib.sha256((frozen_dir / rel).read_bytes()).hexdigest()
    assert actual_sha == expected_sha, f"Digest mismatch on {rel}: {actual_sha} != {expected_sha}"
print("Frozen digests match expected.json exactly.")
PY

# 5. Run gate self-test (capability check)
python3 tools/souji-evidence-cache.py --selftest; echo "selftest_rc=$?"
# Expect: exit 0

# 6. Run gate frozen snapshot check (measurement check)
python3 tools/souji-evidence-cache.py --frozen tests/fixtures/r14-cache-frozen; echo "frozen_rc=$?"
# Expect: exit 0

# 7. Run external discriminating fixture
python3 tests/fixtures/r14-evidence-cache.py --tool tools/souji-evidence-cache.py; echo "fixture_rc=$?"
# Expect: exit 0

# 8. Isolated tamper falsifier test (Q18 integrity check)
TMP_SCRATCH=$(mktemp -d /var/tmp/souji-r14-tamper.XXXXXX)
trap 'rm -rf -- "$TMP_SCRATCH"' EXIT
cp -r tests/fixtures/r14-cache-frozen "$TMP_SCRATCH/frozen"
echo "tampered-content" >> "$TMP_SCRATCH/frozen/dependency.txt"
python3 tools/souji-evidence-cache.py --frozen "$TMP_SCRATCH/frozen" >/dev/null 2>&1
echo "tamper_rc=$?"
# Expect: exit 2 with snapshot_tampered
rm -rf -- "$TMP_SCRATCH"
trap - EXIT
```
