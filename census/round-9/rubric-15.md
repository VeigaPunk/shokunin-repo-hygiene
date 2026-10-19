# S15 — round-9 scorecard rubric (draft v1)

Axes: **calibration, operability, coverage**. This is a proposed evidence-to-score mapping, not a new score award or a round-admission verdict. Only this fragment is changed; the parent owns SCORECARD.md/LOG.md integration.

## Measured baseline and verdict

- Lane HEAD: `14916c075c7de4b905d92c472e6312026d12d44a`.
- SCORECARD.md sha256: `7c0039a528a2a760622ce9d9b69427e2ee695a993b7acca72968fc048cfd2378`.
- Latest commit touching SCORECARD.md: `ce58c2b457c8ffb7886b36a509bf957f90d1f296` (r5).
- Freshly reproduced **numeric contradictions: 2**, both within SCORECARD.md: calibration is 7 in the axis table versus 6 in the saturation paragraph; operability is 8 versus 7. Coverage agrees at 8. See `SCORECARD.md:13-15,44-46`.
- **Capability-table omissions: 2**, counted separately, not inflated into numeric contradictions: installed `souji-census.sh` and `souji-quarantine.sh` have no row. The parent recorded their demonstrations at `LOG.md:229-237,272-278`; these old reports are evidence pointers, not fresh live-operation proofs.
- **Runtime defects confirmed by S15: 0.** This seat drafted a rubric and ran regression baselines; it did not perform a complete adversarial audit. There are no S15 attack claims to label CONFIRMED or NOT-REPRODUCED.
- Four copied-tool selftests passed in isolated fixtures: verify **24/24**, vault **35/35**, quarantine **63/63**, census **32/32**; total **154/154**, each exit 0. All live tool hashes still matched their copies immediately after the runs. `bash -n` also exited 0 for all four installed scripts.
- Raw baseline logs and JSON: `/var/tmp/souji-s15-rubric-cj79rujw/`. These are temporary supporting artifacts; the replay below is the durable evidence.

Pinned tool hashes (do not attribute these results to a later S17/S18 candidate):

```text
souji-verify.sh        a91049c96e5fba7c3db83df288a261717156c3834532e54d712ed0c555e350c4
souji-vault-verify.sh  53f92421b254426c7e4882c1da9cfaa444bddde7ff90ee30afcd48fa229328b1
souji-quarantine.sh    5780ad751aa49d1bb587690154cab98ab6aa71b4def518673c2f383301c51c4f
souji-census.sh        11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381
```

**Rubric verdicts:** current numeric scores are **LEGACY-UNMAPPED** (no reproducible mapping from observations to 8/7/8); current scorecard consistency is **FAIL** (two contradictory values); capability inventory is **INCOMPLETE** (two omissions); the four built-in regression suites are **PASS**, not a safety certificate. New axis scores remain **UNRATED** until the gates below are adjudicated. Do not silently reinterpret an old 8 as a new-rubric 8.

## Evidence rules and asymmetric safety

A scored observation names the exact command sequence, fixture construction, expected result, actual stdout/stderr and exit status, independent oracle, UTC measurement time, source revision, full hashes of all relevant tools/documents, and durable evidence pointer. For quarantine, inspect resulting filesystem/index state as well as printed tokens. Do not accept a fixture path or a historical JSON pointer alone as a reproduction.

- **CONFIRMED:** a fresh fixture sequence violates an independently stated invariant on the pinned bytes. A false SAFE, unjustified clean/no-change certification, unauthorized staging/deletion, or protected read/write is material. Distinguish a printed false DELETED from actual data loss.
- **NOT-REPRODUCED:** a claimed defect lacks a fresh working sequence or the asserted unsafe result does not occur. It is not counted as confirmed, fixed, or a passing regression.
- **EXPECTED-REFUSAL:** NOT-SAFE / NOT-AUTHORIZED / ABORTED / DRY-RUN-BLOCKED / an explicit error with no unsafe side effects is not a safety defect. Correctly rejecting uncertainty earns a defensive test PASS. ABORTED requires the quarantined bytes to remain recoverable; a token alone is insufficient.
- A missing positive demonstration is **UNMEASURED** or **BLOCKED**, not a false SAFE and not a reason to weaken a gate. A tool that refuses every input cannot pass positive-capability gates.
- Compare verify and vault on the **same oracle-defined input and receipt**, not by majority vote. A disagreement is not automatically a defect: vault checks ledger integrity before fallback, while verify tries pushed first (`tools/souji-vault-verify.sh:573-576`; `tools/souji-verify.sh:365-371`). Different refusal reasons alone are harmless. Record raw output and classify directional mismatches; never average an unsafe acceptance away with many refusals.
- Dry-run PASS proves only its stated preflight, not successful staging, hold, second check, or deletion. Fixture remote-tracking refs prove fixture behavior only; they do not prove a real push or operator authorization. Census flags are observations, never removal receipts; main-worktree `clean` does not certify every linked worktree clean.
- Freeze the test manifest and expected outcomes before candidate results. Same-class variants/seats deduplicate by root cause plus violated invariant. Publish both case count and unique-class count. Parallel seat failures, quota problems, timeouts, and unreadable inputs are not missing passes to drop from the denominator.
- No live attacks, real secret content, GUI launches, network mutation, operator-config changes, or driver-state access. All fixture state and scratch logs belong under `/var/tmp`; default to dry-run. Do not set the live-mutation override.

## Scoring: ten fixed gates per axis

Each gate is a conjunction: **PASS = every listed requirement evidenced**; **FAIL = a fresh observation falsifies one**; otherwise **UNMEASURED / BLOCKED / NOT-REPRODUCED**. Each gate contributes one point only when PASS. The denominator is always 10: no N/A removal, duplicate-seat credit, defect-discovery bonuses, or +1 simply because a new tool exists.

A complete axis score is `sum(PASS)` out of 10, with all ten gates adjudicated PASS/FAIL. An incomplete axis publishes `verified_points/10`, missing gate IDs and **UNRATED**, not a made-up score. Source inspection supports but does not replace runtime demonstrations. Broader gates cannot be marked PASS from the baseline selftest totals alone.

### Calibration (CAL01–CAL10)

1. **CAL01 — Re-derivable rows.** Every current axis row has the rubric version, explicit numerator/denominator or full gate set, counting command, timestamp, measured revision plus tool hashes, evidence pointer and last-change round. Historical snapshots are explicitly historical.
2. **CAL02 — One current value.** Axis table, saturation paragraph and any current summary agree for all three axes; no contradictory current round status or unresolved competing score is presented as settled.
3. **CAL03 — Evidence integrity.** Every current claim's required pointer resolves to the asserted artifact/content at the pinned revision; commands reproduce the cited result. A living but unrelated file is not a valid pointer. Historical drift is labelled rather than rewritten away.
4. **CAL04 — Capability inventory.** Every asserted installed capability has a matching row, actual passing demonstration and first-working round; withdrawn/unexercised features are not claimed. Census/quarantine omissions are resolved without pretending a rejected round became admitted.
5. **CAL05 — Directional oracle.** Every audit case records expected authorization/refusal independently of tool output, separates false SAFE/DELETE from safe refusal, and distinguishes preflight prediction from actual execution.
6. **CAL06 — Defect accounting.** Every claimed finding has a fresh reproduction or NOT-REPRODUCED disposition, severity, root-cause deduplication and owner; counts satisfy reported = confirmed + not-reproduced + explicitly pending. Fixed findings retain pre-fix reproduction and post-fix evidence.
7. **CAL07 — Differential accounting.** For every planned tool pair/case, raw outputs are preserved and classified as equivalent, expected semantic divergence, unsafe directional divergence or unresolved. Input/snapshot drift is excluded explicitly, not mistaken for disagreement.
8. **CAL08 — Stable denominators.** Planned/completed/failed seats, unique cases, passes, failures and blocked/not-run cases reconcile. Partial results, quota failures and omissions cannot become 100% coverage by shrinking the denominator.
9. **CAL09 — Baseline/candidate separation.** Before/after use the same manifest, oracle and rubric; findings distinguish pre-existing failures from introduced regressions. Historical r6/r7 rejection and amendments remain intact; a later fix does not retroactively admit a failed round.
10. **CAL10 — Honest closure.** All unresolved material contradictions/safety findings, external approvals and unverified surfaces appear in the final handoff and scorecard qualification. No blanket SAFE, SATURATED or "no harm" assertion exceeds the available evidence.

### Operability (OPS01–OPS10)

1. **OPS01 — Runnable entry points.** All four installed tools pass shell syntax checking and invoke their documented normal/help/usage interfaces with required dependencies available; invocation errors have documented non-success behavior.
2. **OPS02 — Receipt engine.** On known-good fixtures verify produces the correct pushed, moved-to-obsidian, stale and metadata-prune results; matched no-receipt/unpushed/dirty cases remain protected. Confirm artifact presence and receipt provenance, not exit 0 alone.
3. **OPS03 — Preservation verifier.** Vault verification accepts independent intact preservation and refuses absent/changed/self-referential/contained copies and incomplete rows. Explicit fallback stays headless; advisory shim lies/absence/timeouts cannot manufacture a receipt.
4. **OPS04 — Census and compare.** A golden fixture census has correct seven columns, main-repo/worktree semantics, numeric values and flags; repeated unchanged runs match; unchanged compare exits 0/header-only, real deltas exit 3 with exact fields, corrupt baselines cannot certify no change.
5. **OPS05 — Mutation-free dry run.** Authorized and unauthorized positional/list inputs produce correct predictions and receipt pins, with unchanged fixture content/index/worktree registrations and no quarantine creation or hold sleep.
6. **OPS06 — Positive quarantine flow.** Actual fixture runs complete stage→hold→class-aware second check→DELETED for pushed, moved-to-obsidian and stale. Check content/index state and preserved external copies; metadata-prune is SKIPPED, not a deletion demonstration.
7. **OPS07 — Failed second check.** Between staging and deletion, change bytes, mtime and each relevant receipt context (pushed refs/unpushed state; ledger/vault; stale references). Every invalidated case aborts/refuses and retains recoverable bytes. No predicted second check substitutes for an actual one.
8. **OPS08 — Error containment.** Engine failures, unavailable hashes/status, invalid arguments, permissions and malformed lists/ledgers/comparisons cannot become authorization, clean or unchanged claims. A safe explicit refusal is acceptable; assert side effects and structured exit/status as well as text.
9. **OPS09 — Protocol integrity.** For spaces, tabs/newlines/control characters, leading dashes and multi-target inputs, JSON parses and record attribution/order stays unambiguous, or the input is explicitly refused without mutation. No forged SAFE/RESULT can cross a record boundary.
10. **OPS10 — Isolation and boundedness.** Instrumented fixture runs verify read-only interfaces/dry-runs do not alter inputs/index, mutation stays within authorized fixture quarantine, forbidden paths/content are not read, no GUI/network mutation occurs, and missing/hanging helpers are bounded. An absence-of-text source scan alone is insufficient.

### Coverage (COV01–COV10)

One point governs one fixed surface group, not one artifact, byte count or seat. Each group needs an inventory/spec decision rule, positive path where allowed, negative/boundary cases, and evidence for **every applicable installed consumer**; exclusions name an owner and remaining gap. Positive paths never include accessing real secrets or protected live state.

1. **COV01 — Scope/ownership.** Fleet root and immediate child main repos; canonical in-scope targets versus repo root, outside paths, protected driver/config and unknown owner; operator-gated surfaces stay blocked without authorization.
2. **COV02 — Pushed files/directories.** Ancestor/default-ref resolution, missing/ambiguous remote refs, later local commits, dirty/staged/untracked descendants, current bytes versus preserving commit, and detached/local-branch cases.
3. **COV03 — Stale artifacts.** `.scratch`, supported output/log/draft/checkpoint families versus unsupported lookalikes; strict age boundary/future time, active references and sweep exclusions/errors. Live active scratch is never reclassified simply to gain cleanup coverage.
4. **COV04 — Preservation.** File and directory manifests, both hashes, independent surviving vault location, self/descendant aliases, missing/duplicate/incomplete/relative ledger rows, no-final-newline input and source/vault mutation.
5. **COV05 — Worktree metadata.** Missing/present, detached/named, unique/unpushed commits, locks/pins, dirty and unverifiable worktrees; registration pruning remains distinct from filesystem removal and branch deletion.
6. **COV06 — Quarantine states.** Tracked/untracked staging, all three removable receipt classes, receipt-pinned list and positional entry, collisions, hold/second-check drift, abort recovery, cleanup and metadata SKIPPED. Zero-hold fixtures do not prove a production hold elapsed.
7. **COV07 — Census/delta.** Main root optionality, immediate-child versus linked worktree, scratch sizes/mtime/flags, no remote, unborn or broken repo, added/removed repo, header-only/changed/corrupt comparisons and stable ordering.
8. **COV08 — Paths/object types.** Symlinks/ancestor aliases, files versus directories and special/unreadable objects; spaces, tabs/newlines, Unicode, leading dash, dot-dot, pathspec/glob metacharacters and nested repos. Refuse unsupported representations safely.
9. **COV09 — Safety/failure boundaries.** Secret-shaped and forbidden names are tested only with non-secret fixture sentinels; instrument absence of content access, read-only behavior, helper/tool errors, malformed output and timeouts across all relevant entry points.
10. **COV10 — Fleet use cases and handoff.** Fixture analogues cover approval-list checkpoints, active unpushed scratch and pinned dead registrations; the runbook maps each real blocked class to its owner/approval/push prerequisite. No fresh live census or live deletion is claimed from fixture success.

## Counting command and admission safeguards

Parent-adjudicated TSV: exactly `axis<TAB>gate<TAB>status<TAB>evidence`, 30 unique rows, gate IDs above. Axis names are `calibration`, `operability`, `coverage`. PASS/FAIL rows require an evidence pointer to the full observation tuple; unknown statuses remain unscored. The scorer validates bookkeeping, not evidence truth; a reviewer still verifies each asserted PASS/FAIL.

Run the following Python with the adjudicated TSV as its first argument (`python3 - /var/tmp/<gate-file>.tsv`). This file format does not exist yet; it is an integration contract, not a claim that all gates were measured.

<!-- S15-SCORER-BEGIN -->
```python
import csv, json, sys
spec = {"calibration": "CAL", "operability": "OPS", "coverage": "COV"}
expected = {(axis, f"{prefix}{i:02}") for axis, prefix in spec.items()
            for i in range(1, 11)}
allowed = {"PASS", "FAIL", "UNMEASURED", "BLOCKED", "NOT-REPRODUCED"}
with open(sys.argv[1], newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    if reader.fieldnames != ["axis", "gate", "status", "evidence"]:
        raise SystemExit("invalid rubric TSV header")
    rows = list(reader)
seen = set()
for row in rows:
    key = (row["axis"], row["gate"])
    if (None in row or any(value is None for value in row.values())
            or key not in expected or key in seen
            or row["status"] not in allowed
            or (row["status"] in {"PASS", "FAIL"} and not row["evidence"].strip())):
        raise SystemExit("invalid, duplicate, or unevidenced rubric row")
    seen.add(key)
if seen != expected:
    raise SystemExit("incomplete gate inventory: retain all 30 rows")
result = {}
for axis in spec:
    group = [r for r in rows if r["axis"] == axis]
    points = sum(r["status"] == "PASS" for r in group)
    unknown = [r["gate"] for r in group if r["status"] not in {"PASS", "FAIL"}]
    result[axis] = {"verified_points": points, "denominator": 10,
                    "score": None if unknown else points,
                    "status": "UNRATED" if unknown else "RATED",
                    "unmeasured_gates": unknown}
print(json.dumps({"rubric": "souji-r9-s15-v1", "axes": result}, sort_keys=True))
```
<!-- S15-SCORER-END -->

- Keep a **separate safety veto**: any unresolved confirmed unsafe acceptance/action/protected access blocks a clean deployment verdict, even if the raw gate sum is high. Never average it away or award "no harm" on green selftests alone.
- Keep **capability count**, **admitted-round count**, **case count**, **unique defect count**, **contradiction count**, and **axis scores** separate. This rubric does not promote r6/r7 to admitted rounds or waive operator gates.
- First adoption rebaselines the old unmapped scores; a changed measurement scheme is not itself demonstrated tool regression. Thereafter compare the same gates on baseline/candidate bytes. PASS→FAIL is harm; PASS→unknown prevents a no-harm conclusion. Finding a pre-existing defect can improve calibration without pretending operability improved.
- Round admission still follows `AXES.md:25-55`: 1–3 causally separable claims on distinct axes, lowest-axis obligation unless the documented nudge applies, all claims verified and no axis harmed. Exploratory credit needs the specified named non-author reviewer; a dispatched seat is not that reviewer.
- Preserve saturation line **8**, stagnation window **3**. Only fully measured, comparable axis scores can support saturation; unresolved safety/contradiction debt blocks a clean saturated verdict. One selftest run or one new script is not stagnation-window evidence.

## Fresh reproduction commands

From `/home/vgpnk/Projects/shokunin/souji-shokunin`; all commands below are read-only on the live lane. Baseline execution copies only the four scripts into a new fixture repo; the shipped selftests create synthetic refusal sentinels only inside their temporary fixtures. No live candidate, state, vault or secret contents are supplied.

### Reproduce scorecard consistency counts

<!-- S15-CONSISTENCY-BEGIN -->
```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, json, re, subprocess
p = Path('SCORECARD.md'); data = p.read_bytes(); text = data.decode()
rows = {m.group(1): int(m.group(2)) for m in re.finditer(
    r'^\| (coverage|calibration|operability) \| (\d+) \|', text, re.M)}
summary = {a: int(re.search(r'\b' + a + r'\s+(\d+)',
    text[text.index('Saturation line:'):], re.I).group(1)) for a in rows}
contradictions = [{'axis': a, 'axis_row': rows[a], 'summary': summary[a]}
                  for a in rows if rows[a] != summary[a]]
caps = text.split('## Capabilities\n', 1)[1].split('## Planned', 1)[0]
missing = [str(p) for p in (Path('tools/souji-census.sh'),
    Path('tools/souji-quarantine.sh')) if p.is_file() and p.name not in caps]
print(json.dumps({'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
    text=True).strip(), 'scorecard_sha256': hashlib.sha256(data).hexdigest(),
    'numeric_contradiction_count': len(contradictions),
    'numeric_contradictions': contradictions,
    'missing_capability_row_count': len(missing),
    'installed_tools_missing_from_capabilities': missing}, indent=2))
PY
```
<!-- S15-CONSISTENCY-END -->

Expected on the pinned SCORECARD bytes: contradiction count **2**, missing-capability row count **2**. If the parent corrects the scorecard, remeasure; do not perpetuate the old counts as current.

### Reproduce the isolated regression baseline

<!-- S15-BASELINE-BEGIN -->
```bash
python3 - <<'PY'
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, os, shutil, subprocess
root = Path.cwd()
work = Path(subprocess.check_output(['mktemp', '-d', '-p', '/var/tmp',
    'souji-s15-replay.XXXXXX'], text=True).strip())
repo = work / 'installed' / 'souji-shokunin'
(repo / 'tools').mkdir(parents=True)
(repo / 'LOG.md').write_text('S15 isolated fixture sentinel\n')
(repo / 'corpus' / 'knowledge').mkdir(parents=True)
(repo / 'corpus' / 'knowledge' / 'obsidian-ledger.tsv').write_text(
    'source_path\tsource_sha256\tvault_path\tvault_sha256\n')
subprocess.run(['git', 'init', '-q', str(repo)], check=True)
names = ('souji-verify.sh', 'souji-vault-verify.sh',
         'souji-quarantine.sh', 'souji-census.sh')
for name in names:
    shutil.copy2(root / 'tools' / name, repo / 'tools' / name)
    (repo / 'tools' / name).chmod(0o700)
env = {k: v for k, v in os.environ.items()
       if not (k.startswith(('GIT_', 'SOUJI_')) or k == 'SHOKUNIN_ROOT')}
(work / 'home').mkdir()
env.update(TMPDIR='/var/tmp', HOME=str(work / 'home'),
    GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
    GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0',
    GIT_AUTHOR_NAME='S15 fixture', GIT_AUTHOR_EMAIL='s15@fixture.local',
    GIT_COMMITTER_NAME='S15 fixture', GIT_COMMITTER_EMAIL='s15@fixture.local')
def run(name):
    path = repo / 'tools' / name
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    cp = subprocess.run(['timeout', '120', 'bash', str(path), '--selftest'],
        cwd=repo, env=env, text=True, capture_output=True)
    (work / (name + '.stdout')).write_text(cp.stdout)
    (work / (name + '.stderr')).write_text(cp.stderr)
    return {'tool': name, 'snapshot_sha256': sha, 'exit': cp.returncode,
        'summary': cp.stdout.strip().splitlines()[-1:],
        'source_unchanged': hashlib.sha256((root / 'tools' / name).read_bytes()).hexdigest() == sha}
with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(run, names))
report = {'fixture_root': str(work), 'results': results}
(work / 'baseline.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
raise SystemExit(0 if all(r['exit'] == 0 and r['source_unchanged'] for r in results) else 1)
PY
```
<!-- S15-BASELINE-END -->

Expected on the pinned tool bytes: **24, 35, 63, 32 checks; 0 failed each; exit 0**. Any different tool hash is a different baseline, even if counts match. Selftests passing is deliberately insufficient for OPS07–OPS10 or full coverage; round-9 fresh adversarial and differential results must supply those observations.

## Deliverable validation

Validation completed by `2026-10-18T23:52:25Z` against the pinned baseline:

- Executed the consistency command extracted directly from this Markdown: exit 0, exactly **2 numeric contradictions + 2 capability omissions**.
- Executed the baseline command extracted directly from this Markdown: exit 0, **154/154** selftest checks again passed, all four source hashes unchanged. Replay logs: `/var/tmp/souji-s15-replay.JA2cz9/`.
- Compiled and executed the exact embedded scorer with synthetic evidence under `/var/tmp/souji-s15-score-tests.JF7TEW/`: **16/16 validation cases passed**. All-PASS→10, all-FAIL→0, eight-PASS/two-FAIL→8; each unknown status retained a null score and nine verified points. Missing/duplicate gates, invalid status/axis/gate/header, absent PASS/FAIL evidence and extra/short columns all exited nonzero as intended. Synthetic PASS labels tested arithmetic only; they are not lane gate evidence.
- Checked that the document enumerates exactly **30 unique gate IDs**, ten for each owned axis. The gate TSV remains for parent adjudication; no new axis score or safety clearance was awarded.
