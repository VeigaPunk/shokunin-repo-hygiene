# Round 9 — S19 rubric judgment and merged specification

**Winner: `rubric-13.md`**, for reproducibility of the scoring calculation. This is a prospective rubric and integration contract, **not a replacement score award, safety clearance, or round-admission verdict**.

Axes: repo-only reproducibility, complete numeric mapping, evidence provenance, and current-scorecard consistency. Required wait: `sleep 600`, completed in **600.001 seconds**, exit 0, before reading the four candidates. S19 writes only this file; SCORECARD.md and shared bookkeeping remain unchanged.

## Candidate verdicts

- **S13 — strongest.** Thirty fixed strata, sixty named mandatory checks, exact fractional arithmetic, an executable scorer, committed-blob inputs, full target/evidence commit IDs, all four tool hashes, scope hash, and primary/replay linkage. Missing, malformed, uncommitted, mismatched and disagreeing evidence have defined outcomes. This most nearly lets a reader recompute every reported number using only the repository.
- **S15 — runner-up.** Its executable TSV scorer has a fixed thirty-gate inventory, rejects duplicate/missing rows, and leaves incomplete axes UNRATED. However, the evidence column is only checked for nonempty text: a nonexistent pointer, wrong revision or unjustified PASS is outside its mechanical validation. Good publication/admission safeguards are retained below.
- **S14 — strong policy, less mechanized scoring.** Explicit P/F/U arithmetic, uncertainty bounds and broad requirements; its executable material checks the scorecard and a limited smoke, not a complete gate ledger. A reader still has to invent the aggregation input interface and adjudicate broad checklist items.
- **S16 — clear arithmetic, weakest identity binding in the calculator.** The reference function validates ten anonymous PASS/FAIL/UNKNOWN values, not unique gate IDs, evidence paths or target hashes. Its prose supplies those obligations, but the calculator cannot verify them. Its distinction between an expected refusal and an unproved positive capability is retained.

None of the four submissions re-derives the existing 8/7/8 scores. No complete, committed round-9 assessment exists yet. **S13 wins as a reproducible specification, not as an already measured current-lane score.** A reader can presently reproduce the unsupported-score flags and contradictions below; non-provisional new scores require the parent to integrate the defined evidence.

Reviewed input SHA-256 values:

```text
532c8bf18426dbb4b70b7bd21fc1268146ea3d1c834dccb993b93b3ac8daf09e  census/round-9/rubric-13.md
a6d16212e24f0f247284c5c0860f1bf12bcfc245eb980deb9de9191c97975da6  census/round-9/rubric-14.md
e9824a7d62557ca14eaa72fb8c381baa04ce433394158fbd074649a93f27d89e  census/round-9/rubric-15.md
c57471ef5dacabed71ad6783ab2c480f6ef66089e77201820bb9000840182735  census/round-9/rubric-16.md
```

## Current SCORECARD flags — all three numeric rows are unmapped

Snapshot: lane commit `14916c075c7de4b905d92c472e6312026d12d44a`; SCORECARD.md SHA-256 `7c0039a528a2a760622ce9d9b69427e2ee695a993b7acca72968fc048cfd2378`.

| Current row | Flag | Why the evidence cannot re-derive that score |
|---|---|---|
| coverage **8**, SCORECARD.md:13 | LEGACY-UNMAPPED | The 21/21 prune observation and 20→1 / 6→4 worktree counts have no defined mapping to 8. The commands require sibling live repositories and cannot replay a historical transition from a standalone lane checkout. |
| calibration **7**, SCORECARD.md:14 | LEGACY-UNMAPPED | Three corrected findings and zero unresolved claims do not specify a denominator or conversion to 7. Judge files and prose are observations, not the normalized sixty-check assessment. |
| operability **8**, SCORECARD.md:15 | LEGACY-UNMAPPED | The saved parent battery contains four impl-20 `ok=true` cases, but 4/4 and a selftest exit of 0 do not imply 8 under any stated formula. The real-vault observation is historical/external, not a repo-only replay input. |

The `measured commit` cells are `r3 report`, `r5 report`, and `r4 report`, not resolvable commit identities. These are **three provenance gaps**, not three additional executable-tool defects. Keep useful historical counts; do not retrofit them into this new scale.

There are **two current numeric contradictions, one stale-summary class**:

- calibration: table **7** at SCORECARD.md:14 versus saturation paragraph **6** at :45;
- operability: table **8** at SCORECARD.md:15 versus saturation paragraph **7** at :45.

Coverage is 8 in both places, but agreement does not make its mapping reproducible. The repeated 6 and 7 are also unsupported current score statements. Saturation line **8** and stagnation window **3** are declared policy parameters, not measured axis scores; they are not counted as contradictory or underived observations.

Fresh, repo-only reproduction from the lane root:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, json, re, subprocess
T = '14916c075c7de4b905d92c472e6312026d12d44a'
data = subprocess.check_output(['git', 'show', T + ':SCORECARD.md'])
s = data.decode()
current = Path('SCORECARD.md').read_bytes()
rows = {}
for line in s.splitlines():
    if re.match(r'^\| (coverage|calibration|operability) \|', line):
        f = [v.strip() for v in re.split(r'(?<!\\)\|', line)[1:-1]]
        assert len(f) == 6
        rows[f[0]] = {'score': int(f[1]), 'measured_commit': f[4]}
m = re.search(r'Coverage (\d+),\s*operability (\d+), calibration (\d+)', s)
assert m and len(rows) == 3
summary = dict(zip(('coverage', 'operability', 'calibration'), map(int, m.groups())))
delta = {a: {'table': rows[a]['score'], 'summary': summary[a]}
         for a in rows if rows[a]['score'] != summary[a]}
battery_data = subprocess.check_output(['git', 'show', T + ':tests/results/parent-vault-battery.json'])
battery = json.loads(battery_data)['results']
print(json.dumps({'target': T, 'scorecard_sha256': hashlib.sha256(data).hexdigest(),
    'working_card_matches_snapshot': current == data, 'axis_rows': rows,
    'legacy_unmapped_axis_rows': sorted(rows), 'numeric_contradictions': len(delta),
    'stale_summary_classes': int(bool(delta)), 'details': delta,
    'saved_impl20_battery_ok': sum(x['souji-vault-verify.impl-20.sh']['ok'] is True
                                 for x in battery.values()),
    'saved_battery_cases': len(battery)}, sort_keys=True))
PY
```

Observed on the reviewed bytes: `working_card_matches_snapshot=true`, three legacy/unmapped axis rows, two contradictory fields, one stale-summary class, and saved battery **4/4**. The command measures the contradictions and saved count; the missing evidence-to-score formula is established by the row contents and the four draft specifications, not inferred from an arbitrary numerical threshold.

## Merged rubric — souji-r9-v1 / R9-SCORE-v1

Retain S13's scoring definitions and reference evaluator unchanged. S14/S15/S16 strengthen publication and interpretation, not the weights or historical numbers.

### Fixed denominator, exact arithmetic

There are ten equally weighted strata per axis and two mandatory checks per stratum. No missing, blocked or NOT-REPRODUCED check leaves the denominator. Changing a check, scope, weight, threshold or oracle requires a new rubric version and a remeasured baseline.

Check evidence credit:

- **E0 = 0:** absent, incomplete, blocked, NOT-REPRODUCED, or a supplied replay that is incomplete or disagrees;
- **E1 = 1/2:** one committed COMPLETED primary run, with no independent replay supplied;
- **E2 = 1:** primary plus a COMPLETED matching replay by a genuinely different named executor, on identical target/tool/scope pins.

For calibration, eligibility requires an exercised, passing honest-self-assessment assertion. For operability, it requires an exercised, passing operation/control assertion. For coverage, it requires exercising a check with a decidable independent oracle; a discovered bug can earn explored-surface credit without earning correctness or capability credit. This coverage number is explicitly an **evidence-backed exploration measure**, not a percentage of all possible attacks or a claim that every explored surface is safely governed.

For each stratum: `points = sum(eligible check credits) / 2`. For each axis: `raw = sum(points over its ten strata)` and `score = floor(raw)`. Use exact fractions. Thus [0,1)→0, [1,2)→1, …, [9,10)→9, and exactly 10→10. Repetition, seat counts, file counts, deleted bytes, judge votes and round counts earn no bonus.

A fresh COMPLETED reproduction of false SAFE, false DELETE, protected-content read or outside-scope write activates the retained S13 safety override: calibration and operability scores become 0; coverage remains the explored-surface count. The raw pre-override points remain visible. This is a conservative scoring convention, not a claim that honestly discovering a pre-existing defect introduced that defect.

### Publication and admission safeguards

- Provisional points are **lower-bound evidence accounting only**. The supplied empty `seat-13.json` assessment does not mean that the tools have zero capability. Publish current replacement scores as **UNRATED** until the assessment is closed, committed, independently reviewed and its source evidence is complete.
- The evaluator's `MEASURED` means its arithmetic inputs meet the structural closure rule. It is **not** operational certification: BLOCKED/NOT-REPRODUCED checks, incomplete predicate demonstrations, conflicting replays, open contradictions, and unknown safety remain visible. Do not claim exhaustive coverage, saturation or verified no-harm from an incomplete assessment.
- A confirmed unsafe acceptance/action/protected access is a separate, non-compensable certification veto. Even after a numerical override, keep the finding and affected-tool scope; fixing a score cannot clear a defect. A fix needs a new pinned target plus the exact failing reproducer, affected variants, applicable permitted regressions and integrated engine→quarantine flow re-run on final bytes.
- A correct fail-closed refusal is not a tool defect. Refusing a promised positive control leaves that capability unproved; it cannot be manufactured into a PASS or reclassified as unsafe authorization. An ABORTED token is insufficient without retained recoverable bytes.
- Differential comparisons use identical fixture/root/ledger/time context and independent ground truth. Verify's pushed-first precedence and vault's matching-ledger-first precedence can legitimately differ. A different reason string or conservative refusal is not automatically a contradiction; agreement can reproduce a shared bug.
- Every attack executes only against fresh `/var/tmp` fixtures, with headless/no-protected-content instrumentation. No secret-shaped contents or prohibited driver-state surfaces may be read to earn points. Unsafe reproduction cannot justify violating the exercise boundary.
- Numeric scores never authorize removal. Operator approval, receipt, quarantine, hold and act-time re-verification remain separate. Fixture remote refs do not prove a live push. Census `clean` is not a removal receipt.
- Keep capability acquisition, axis scores, case counts, unique root causes, contradictions and admitted-round counts separate. Preserve historical r6/r7 rejection. Compare before/after only on a common frozen rubric/manifest; a lost PASS or lost evidence cannot be averaged away by a higher total. Admission still requires the declared distinct-axis claims to verify with no axis harmed.

### Mandatory strata and check predicates

Each row has exactly two check IDs. Every compound predicate must be demonstrated, not one convenient example. Raw fixture/oracle/output/postcondition evidence accompanies the normalized facts. Frozen fleet inventories are committed snapshots; a standalone reader never needs to interrogate or modify the live fleet.

| Stratum | Mandatory check IDs and complete meaning |
|---|---|
| C01 numbers | `recompute`: published numbers derive from named pipelines; `denominators`: frozen complete inventories, not selected subsets |
| C02 provenance | `commit`: every measured revision resolves to a full commit; `hashes`: cited tool/artifact hashes match that revision |
| C03 commands | `cwd`: commands replay from declared cwd; `statuses`: actual stdout/stderr and every pipeline status agree, without hidden producer failures |
| C04 verdict honesty | `oracle`: claims match independent fixture ground truth; `scope`: fixture, installed, historical and approval-blocked claims stay distinct |
| C05 pushed claims | `remote`: local-only refs are never described as pushed; `edits`: dirty/later-unpushed bytes are not described as preserved |
| C06 preservation claims | `distinct-copy`: copy survives source removal; `hash-pair`: both source/vault hashes independently established |
| C07 stale claims | `age-boundary`: strict/equality age boundary covered; `references`: unknown/failed scans never called zero |
| C08 differential audit | `disagreements`: normalized identical inputs compared across engines; `triage`: every mismatch ruled on or explicitly unresolved/NOT-REPRODUCED |
| C09 contradictions | `enumeration`: individually enumerate conflicting assertions/pointers/scores; `gap-labels`: open, corrected-and-replayed and unreproduced labels match evidence |
| C10 closure | `final-bytes`: tested bytes equal claimed/installed bytes; `summary`: current table, saturation, capabilities and unresolved counts agree |
| O01 verify | `selftest`: final selftest zero failures; `positive-negative`: independent allowed/forbidden controls produce promised verdicts |
| O02 vault verify | `selftest`: final selftest zero failures; `positive-negative`: distinct valid copy works, mismatch/self-reference refuse |
| O03 quarantine | `selftest`: final selftest zero failures; `physical-flow`: stage, hold, second check and deletion asserted on actual filesystem |
| O04 census | `selftest`: final selftest zero failures; `snapshot-delta`: identical comparison empty and known change exact |
| O05 refusal preservation | `no-receipt`: refusal without mutation; `dirty-unpushed`: dirty/unpushed fixture work remains intact |
| O06 second check | `hold`: configured hold cannot be bypassed; `tamper`: during-hold content/receipt/reference drift aborts with recoverable staged bytes |
| O07 original authority | `pushed`: original provenance/bytes, not quarantine introduction; `vault`: re-establish independent surviving vault copy |
| O08 errors | `malformed`: invalid inputs/engine failures refuse; `dependencies`: absent helpers, unreadable inputs and scan errors never become SAFE/DELETE |
| O09 repeatability | `repeat`: unchanged fixture normalized outputs identical; `bounded`: named timeout bounds completion, timeout classified blocked/refusal |
| O10 side effects | `dry-run`: names, bytes, hashes, modes, refs and index unchanged; `confinement`: no protected reads or outside-fixture writes/GUI effects |
| K01 fleet-root artifacts | `inventory`: exact root candidate set including empty/blocked dispositions; `classification`: every member has oracle-backed receipt/refusal |
| K02 lane repos | `inventory`: exact main-repo roster and exclusions; `classification`: every member's clean/dirty/unpushed/no-remote state and linked ownership represented |
| K03 artifact forms | `file-directory`: files/directories/missing/empty targets; `links`: symlink, hardlink and containment cases without protected-content reads |
| K04 worktree metadata | `registration`: present/absent, named/detached; `locks`: pins, unpushed tips and exact-ticket metadata-only fixture pruning |
| K05 stale surfaces | `clock`: below/equal/above age threshold and future mtime; `scan`: hidden/ignored/binary/live refs and scan-error refusal |
| K06 pushed provenance | `refs`: valid/absent/ambiguous/local-only default refs; `changes`: local commits, dirty bytes, directory descendants and path encodings |
| K07 ledger | `rows`: valid/malformed/duplicate/missing hashes or endpoints; `survival`: distinct copy, same inode/path, nested copy, digest drift and directory links |
| K08 protected surfaces | `names`: refusal families/aliases with no-read instrumentation, never protected payload reads; `operator-runtime`: config/runtime exclusions validated without accessing forbidden live surfaces |
| K09 quarantine | `stages`: normal/refusal paths every stage; `adversarial`: races, collisions, escape/control characters and failed-check preservation |
| K10 census/differential | `enumeration`: inventory, zero/no-remote, linked worktree and error rows; `comparison`: repeat, known delta, malformed baseline and cross-engine mismatch |

### Committed evidence interface

Retain `census/round-9/seat-13.json` as the assessment input so the supplied scaffold remains usable without editing another seat's files. The parent fills and commits it; S19 does not. Assessment fields are:

- `rubric: "souji-r9-v1"`, full `subject_commit`, exact `tool_sha256` for all four tools, and SHA-256 of the subject's PROVINCE.md as `scope_sha256`;
- Boolean `closed`, and `cells` mapping stratum IDs to `{"primary":{"path":"census/round-9/seat-NN.json","run":"id"},"replay":null}`; a supplied replay uses the same reference form;
- each referenced report has `rubric_runs[id]` containing `cell`, named `author`, identical subject/tool/scope pins, `scope` equal to `fixture` or `committed-artifacts`, full reproducible `command`, integer harness `exit_code`, and captured normalized JSON `stdout`;
- normalized stdout contains exactly `state`, `exercised`, `passed`, and `safety`. State is COMPLETED/BLOCKED/NOT-REPRODUCED; the check maps have both required Boolean entries; passing implies exercised. Safety has nonnegative integer `false_safe`, `false_delete`, `protected_read`, `outside_scope_write` counts. Incomplete runs cannot claim confirmed safety events.

A COMPLETED harness has exit 0 or 1; refusal statuses are captured internally, not mistaken for harness failure. A nonzero all-pass harness is invalid. Preserve raw stdout/stderr, oracle facts and postconditions alongside normalization. An arbitrary JSON PASS or nonempty command string is not proof; independent executors must validate that the command actually implements the predicates. Names are not cryptographic identity; changing an author's label is not independent execution.

Reports, assessment, tools and scope must be regular committed blobs. Paths outside the exact allowlist, symlink reports, uncommitted reports, duplicate JSON keys, hash drift, unknown strata and false closure refuse as INVALID-EVIDENCE/exit 2. The scorer never executes commands embedded in reports or scans the working tree.

### Canonical repo-only counting command

After parent integration, set `E` to the full evidence commit containing **this file**, the assessment and every referenced report. The subject/tool commit `T` is independently pinned inside the assessment. Git and Python 3 standard library suffice; no network, real fleet, external vault or disposable prior fixture is required.

```bash
set -euo pipefail
E=<full-40-hex-evidence-commit>
git show "$E:census/round-9/rubric-final.md" |
python3 -c 'import sys; s=sys.stdin.read(); marker="```python rubric-scorer-v1\n"; assert s.count(marker)==1; exec(compile(s.split(marker,1)[1].split("\n```",1)[0],"R9-SCORE-v1","exec"))' "$E"
```

```python rubric-scorer-v1
import functools
import hashlib
import json
import re
import subprocess
import sys
from fractions import Fraction

REQ = {
    "C01": ("recompute", "denominators"),
    "C02": ("commit", "hashes"),
    "C03": ("cwd", "statuses"),
    "C04": ("oracle", "scope"),
    "C05": ("remote", "edits"),
    "C06": ("distinct-copy", "hash-pair"),
    "C07": ("age-boundary", "references"),
    "C08": ("disagreements", "triage"),
    "C09": ("enumeration", "gap-labels"),
    "C10": ("final-bytes", "summary"),
    "O01": ("selftest", "positive-negative"),
    "O02": ("selftest", "positive-negative"),
    "O03": ("selftest", "physical-flow"),
    "O04": ("selftest", "snapshot-delta"),
    "O05": ("no-receipt", "dirty-unpushed"),
    "O06": ("hold", "tamper"),
    "O07": ("pushed", "vault"),
    "O08": ("malformed", "dependencies"),
    "O09": ("repeat", "bounded"),
    "O10": ("dry-run", "confinement"),
    "K01": ("inventory", "classification"),
    "K02": ("inventory", "classification"),
    "K03": ("file-directory", "links"),
    "K04": ("registration", "locks"),
    "K05": ("clock", "scan"),
    "K06": ("refs", "changes"),
    "K07": ("rows", "survival"),
    "K08": ("names", "operator-runtime"),
    "K09": ("stages", "adversarial"),
    "K10": ("enumeration", "comparison"),
}
TOOLS = tuple("tools/souji-" + n + ".sh" for n in
              ("verify", "vault-verify", "quarantine", "census"))
SAFETY = {"false_safe", "false_delete", "protected_read", "outside_scope_write"}
AXES = {"calibration": "C", "operability": "O", "coverage": "K"}

def need(condition, message):
    if not condition:
        raise ValueError(message)

def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result

def parse(text):
    return json.loads(text, object_pairs_hook=pairs)

def git(*args):
    return subprocess.check_output(["git", *args], stderr=subprocess.PIPE)

@functools.lru_cache(None)
def blob(commit, path):
    allowed = path in (*TOOLS, "PROVINCE.md", "census/round-9/seat-13.json")
    allowed = allowed or bool(re.fullmatch(r"census/round-9/seat-[0-9]{2}\.json", path))
    need(allowed, "non-allowlisted artifact: " + path)
    row = git("ls-tree", commit, "--", path).decode().strip().split()
    need(len(row) == 4 and row[0] in {"100644", "100755"}
         and row[1] == "blob" and row[3] == path, "not a regular committed blob: " + path)
    return git("show", commit + ":" + path)

def main():
    evidence = sys.argv[1]
    need(bool(re.fullmatch(r"[0-9a-f]{40}", evidence)), "evidence commit must be full SHA-1")
    need(git("rev-parse", "--verify", evidence + "^{commit}").decode().strip() == evidence,
         "evidence commit mismatch")
    doc = parse(blob(evidence, "census/round-9/seat-13.json"))
    a = doc["assessment"]
    need(a["rubric"] == "souji-r9-v1", "wrong rubric")
    target = a["subject_commit"]
    need(bool(re.fullmatch(r"[0-9a-f]{40}", target)), "target commit must be full SHA-1")
    need(git("rev-parse", "--verify", target + "^{commit}").decode().strip() == target,
         "target commit mismatch")
    hashes = {p: hashlib.sha256(blob(target, p)).hexdigest() for p in TOOLS}
    scope = hashlib.sha256(blob(target, "PROVINCE.md")).hexdigest()
    need(a["tool_sha256"] == hashes and a["scope_sha256"] == scope, "assessment hash drift")
    cells = a["cells"]
    need(isinstance(cells, dict) and set(cells) <= set(REQ), "unknown or invalid strata")
    need(type(a["closed"]) is bool, "closed must be Boolean")
    if a["closed"]:
        need(set(cells) == set(REQ) and all(c.get("replay") for c in cells.values()),
             "closure requires all 30 strata and an independent attempt for each")
    unsafe = set()
    disagreements = set()

    def run(ref, cell):
        need(isinstance(ref, dict) and set(ref) == {"path", "run"}, "invalid report reference")
        r = parse(blob(evidence, ref["path"]))["rubric_runs"][ref["run"]]
        need(r["cell"] == cell and r["subject_commit"] == target, "run target/cell drift")
        need(r["tool_sha256"] == hashes and r["scope_sha256"] == scope, "run hash drift")
        need(isinstance(r["author"], str) and bool(r["author"].strip()), "unnamed author")
        need(r["scope"] in {"fixture", "committed-artifacts"}, "invalid execution scope")
        need(isinstance(r["command"], str) and bool(r["command"].strip()), "missing reproducer")
        need(type(r["exit_code"]) is int and 0 <= r["exit_code"] <= 255, "invalid exit status")
        facts = parse(r["stdout"])
        need(set(facts) == {"state", "exercised", "passed", "safety"}, "invalid facts")
        need(facts["state"] in {"COMPLETED", "BLOCKED", "NOT-REPRODUCED"}, "invalid state")
        for field in ("exercised", "passed"):
            need(set(facts[field]) == set(REQ[cell]) and
                 all(type(v) is bool for v in facts[field].values()), "invalid check vector")
        need(all(not facts["passed"][k] or facts["exercised"][k] for k in REQ[cell]),
             "unexercised passing check")
        need(set(facts["safety"]) == SAFETY and
             all(type(v) is int and v >= 0 for v in facts["safety"].values()), "invalid safety counts")
        if facts["state"] != "COMPLETED":
            need(not any(facts["safety"].values()), "unreproduced hazard labeled confirmed")
        else:
            need(r["exit_code"] in {0, 1}, "aborted harness labeled completed")
            need(r["exit_code"] == 0 or not all(facts["passed"].values()),
                 "failing harness labeled all-pass")
            if any(facts["safety"].values()):
                unsafe.add(cell)
        return r["author"].strip().casefold(), facts

    points = {axis: Fraction(0) for axis in AXES}
    for axis, prefix in AXES.items():
        for cell in (prefix + f"{i:02d}" for i in range(1, 11)):
            if cell not in cells:
                continue
            entry = cells[cell]
            need(set(entry) == {"primary", "replay"}, "invalid cell entry")
            author, facts = run(entry["primary"], cell)
            weight = Fraction(1, 2) if facts["state"] == "COMPLETED" else Fraction(0)
            if entry["replay"] is not None:
                other, replay = run(entry["replay"], cell)
                need(author != other, "replay is not independent")
                weight = Fraction(0)
                if facts["state"] == replay["state"] == "COMPLETED":
                    if facts == replay:
                        weight = Fraction(1)
                    else:
                        disagreements.add(cell)
            successes = sum(facts["exercised"][k] and
                            (axis == "coverage" or facts["passed"][k]) for k in REQ[cell])
            points[axis] += weight * Fraction(successes, len(REQ[cell]))
    scores = {axis: int(value) for axis, value in points.items()}
    if unsafe:
        scores["calibration"] = scores["operability"] = 0
    result = {"rubric": a["rubric"], "evidence_commit": evidence, "subject_commit": target,
              "status": "MEASURED" if a["closed"] else "PROVISIONAL",
              "raw_points": {k: str(v) for k, v in points.items()}, "scores": scores,
              "safety_override": bool(unsafe), "unsafe_strata": sorted(unsafe),
              "unreconciled_replay_strata": sorted(disagreements),
              "unprovided_strata": sorted(set(REQ) - set(cells))}
    print(json.dumps(result, sort_keys=True))

try:
    main()
except (ValueError, KeyError, TypeError, AttributeError, IndexError, subprocess.CalledProcessError) as exc:
    print(json.dumps({"status": "INVALID-EVIDENCE", "scores": None, "reason": str(exc)}, sort_keys=True))
    sys.exit(2)
```

## S19 verification and integration handoff

Fresh S19 fixture: `/var/tmp/souji-r9-s19-judge.p6s6OL/`. Command: `python3 /var/tmp/souji-r9-s19-judge.p6s6OL/judge.py`. Result: **42/42 checks passed**, exit 0. The fixture harness reconstructs Git evidence with `init/add/write-tree/commit-tree`; no Git mutation occurred in a live repository. Synthetic PASS labels validate calculators, not lane safety or capability.

The checks covered:

- S13's thirty strata/sixty checks; every integer score 0–10 on all axes; primary-only half credit; four safety override classes; BLOCKED and NOT-REPRODUCED accounting;
- rejection of hash drift, unknown/missing strata, false closure, same-author replay, timeout-class completion, missing command, uncommitted/nonallowlisted reports, and duplicate JSON keys;
- visible disagreement with cancelled cell credit;
- S15 all-PASS/all-FAIL/8-of-10 arithmetic, all three incomplete statuses, and malformed/missing/duplicate/unevidenced rows;
- S14's exact two-field/one-class scorecard checker and S16's exact eleven calculator/refusal selfchecks.

Final-deliverable validation: `python3 /var/tmp/souji-r9-s19-judge.p6s6OL/verify-final.py` passed **5/5** additional checks. It extracted the scorer and scorecard reproduction from this actual Markdown, verified all thirty table rows/sixty check IDs, and executed this file's exact shell pipeline from a committed Git fixture. The embedded scorer is byte-identical to S13's, SHA-256 `ca78958b5afb2893bef787252f506fa75ee69dad0ba31c6a9222575185efbf44`. Both the final counting command and the documentary contradiction command therefore ran in the form a reader receives them.

The shared tools changed during concurrent hardening. A separate final syntax-only check passed `bash -n tools/souji-verify.sh tools/souji-vault-verify.sh tools/souji-quarantine.sh tools/souji-census.sh`, exit 0, with identical pre/post hashes:

```text
dfa564e29c219bc6638f185ed640a2210b2fdd10b17753699bf82be78a99ac4f  tools/souji-verify.sh
c2ce6a4fdcb6f08e63005094d9132abd73c3054c87b4a8517ab628a21568aa02  tools/souji-vault-verify.sh
0a601d6bd1e9ab154a61ad7d67bdc0e4071db57f4d57a7848e40b8e5cc888b16  tools/souji-quarantine.sh
11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381  tools/souji-census.sh
```

S19 did **not** execute receipt-tool attack suites or claim these concurrently patched tools' runtime safety. Earlier S14/S15/S16 runtime observations do not transfer to these new hashes. Other seats' selftests and findings remain their evidence, not S19 reproductions.

Parent actions:

1. Label the three current axis scores **LEGACY-UNMAPPED** or replace them only after a complete adopted assessment. Correct the two stale saturation restatements without inventing new grades. Preserve the declared saturation/window policy.
2. Freeze final installed tool bytes in a target commit; regenerate normalized reports and genuinely independent replays against that target. Current round-9 seat prose/JSON must be explicitly adapted and reviewed, never silently treated as this schema.
3. Commit this rubric, the populated assessment and referenced evidence in an evidence commit, then run the exact pipeline above. An uncommitted draft cannot serve as its own committed evidence.
4. Publish arithmetic plus uncertainty/safety/contradiction qualifications; admit no claim until its independent proof and no-harm requirements hold. Do not infer operational clearance from `MEASURED` or from a zero provisional point balance.

**Seat totals:** confirmed executable-tool defects established by S19 **0** (not assessed); documentary contradiction fields **2**, stale-summary classes **1**; unsupported numeric axis rows **3**; new current scores **UNRATED**. Rubric verdict: **S13 strongest; S15 runner-up; merged specification ready for parent integration, not yet a measured re-score**.
