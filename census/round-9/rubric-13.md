## Reproducible numeric rubric — souji-r9-v1

**Draft section for SCORECARD.md; not a retroactive re-score.** Axes are
calibration, operability, and coverage, as defined in the fleet AXES.md.
The existing 7/8/8 are historical increments, not outputs of this rubric.
A score measures the committed evidence for a specified revision; it never
constitutes removal authorization. Zero authorized removals is compatible
with full credit: correct refusals are useful evidence, not defects.

### Frozen denominator and evidence classes

There are ten equally weighted strata per axis. Their mandatory checks are
listed below and in the reference evaluator's `REQ`. Every check remains in
the denominator, including blocked, missing, and NOT-REPRODUCED checks.
Changing a check, scope, weight, threshold, or oracle requires a new rubric
version and re-measurement of both sides of any before/after comparison.
Do not remove hard cases or add repeated easy cases to raise a score.

An admissible run contains a complete fixture/committed-artifact reproducer,
its actual harness exit status, normalized stdout, named author, full target
commit, and all four tool hashes. Its report must be a regular JSON blob in
the evidence commit. The evaluator reads blobs with `git show`, not the
working tree, and checks tool hashes against the target commit. Raw fixture
paths alone, prose votes, old implementation results, and uncommitted files
are not admissible evidence. The scorer never executes report commands.

| Evidence class | Mechanical condition | Credit for each mandatory check |
|---|---|---:|
| E0: absent / blocked / NOT-REPRODUCED | No committed primary run; incomplete execution; unavailable oracle; or a supplied replay is incomplete or disagrees | 0 |
| E1: primary measurement | One committed COMPLETED run with the required check exercised; no independent replay supplied | 1/2 if the axis condition below holds |
| E2: independently replayed | E1 plus a second COMPLETED run by a different named author, on the same target/tool hashes, with identical normalized facts | 1 if the axis condition below holds |

For **calibration**, the check must be exercised and its assertion of honest
self-assessment must pass. A correctly labeled known gap can pass the
`gap-labels` assertion; it cannot substitute for the other required checks.
For **operability**, the advertised operation/control must actually pass.
A refusal on a promised positive path is lack of capability credit, not a
false-SAFE defect. For **coverage**, exercising the check with a decidable
oracle is sufficient even when the tool fails it. Thus a discovered bug can
increase coverage without increasing correctness or runnable capability.
A blocked or uncertain probe is not an explored surface for numeric credit.

For each stratum, `p = sum(check credits) / number of mandatory checks`.
For each axis, `raw = sum(p for its ten strata)`, and
`score = floor(raw)`, an integer from 0 through 10. Use exact fractions, not
rounded percentages. The common mapping is:

| Raw evidence points | Score |
|---|---:|
| [0, 1) | 0 |
| [1, 2) | 1 |
| [2, 3) | 2 |
| [3, 4) | 3 |
| [4, 5) | 4 |
| [5, 6) | 5 |
| [6, 7) | 6 |
| [7, 8) | 7 |
| [8, 9) | 8 |
| [9, 10) | 9 |
| exactly 10 | 10 |

A fresh, COMPLETED reproduction of any false-SAFE, false-DELETE, protected
content read, or write outside the permitted fixture/artifact scope sets
**calibration = 0 and operability = 0**, regardless of averages. Coverage
is not reset: it measures explored surfaces. Safety counts are observations
on this exact target, not lifetime bug totals. A repair clears the override
only after a new target commit and replays; prose saying "fixed" cannot clear
it. Suspicion without a completed reproducer is NOT-REPRODUCED and gets no
credit, not a confirmed defect. Repeated observations of one unsafe case
are reported as unsafe strata, not as independently counted defects.

### Mandatory strata and check semantics

Each backticked label is a mandatory check ID consumed by R9-SCORE-v1.
Commands referenced by a check must be committed with its run, including
fixture construction, oracle, normalization, and postcondition checks.
Assertions mean the entire stated predicate, not one convenient example.
All mutation probes use `mktemp -d -p /var/tmp`; all actual tool runs point
only at fixture fleets. Census/receipt expectations for real surfaces are
replayed from committed, explicitly scoped inventory snapshots, never by
mutating or content-scanning the live fleet.

| Axis / stratum | Mandatory checks and predicates |
|---|---|
| calibration C01 — numbers | `recompute`: published counts/scores derive from their named pipeline; `denominators`: counts use a frozen inventory, not a selected subset |
| calibration C02 — provenance | `commit`: every measured revision resolves to a full commit; `hashes`: cited tool/artifact hashes match that revision |
| calibration C03 — commands | `cwd`: documented commands reproduce from the declared working directory; `statuses`: stdout, stderr, and every pipeline exit status match the claim (no failed producer hidden by a successful counter) |
| calibration C04 — verdict honesty | `oracle`: SAFE/REFUSE claims match the fixture oracle; `scope`: fixture-only, installed, historical, and approval-blocked claims are labeled distinctly |
| calibration C05 — pushed claims | `remote`: no local-only ref is described as pushed; `edits`: later unpushed/dirty bytes are not described as preserved |
| calibration C06 — preservation claims | `distinct-copy`: the preserved copy survives deletion of the source; `hash-pair`: both source and vault hashes are independently established |
| calibration C07 — stale claims | `age-boundary`: age claims include the threshold/equality boundary; `references`: unknown or failed reference scans are not called zero references |
| calibration C08 — differential audit | `disagreements`: identical normalized inputs are compared across receipt engines; `triage`: every mismatch has a named contract ruling or an explicit unresolved/NOT-REPRODUCED label |
| calibration C09 — contradiction register | `enumeration`: conflicting score/report/pointer claims are individually enumerated; `gap-labels`: unresolved, corrected-and-replayed, and NOT-REPRODUCED states match fresh evidence |
| calibration C10 — closure | `final-bytes`: installed/claimed bytes equal the tested bytes; `summary`: score table, saturation paragraph, capability scope, and unresolved counts agree |
| operability O01 — verify | `selftest`: final verify selftest completes with zero failures; `positive-negative`: independent permitted and forbidden fixtures produce their promised verdicts |
| operability O02 — vault verify | `selftest`: final vault selftest completes with zero failures; `positive-negative`: distinct valid copy verifies and mismatch/self-reference refuse |
| operability O03 — quarantine | `selftest`: final quarantine selftest completes with zero failures; `physical-flow`: permitted fixture executes stage, hold, second check, and delete, with actual filesystem assertions |
| operability O04 — census | `selftest`: final census selftest completes with zero failures; `snapshot-delta`: identical fixture snapshots compare empty and a known change produces the exact delta |
| operability O05 — refusal preservation | `no-receipt`: absent receipt refuses without mutation; `dirty-unpushed`: dirty/unpushed fixture work remains intact |
| operability O06 — second check | `hold`: hold cannot be bypassed; `tamper`: content/receipt/reference drift during hold aborts and preserves the staged copy |
| operability O07 — original authority | `pushed`: second check binds original provenance and bytes, not the new quarantine introduction; `vault`: second check re-establishes an external surviving vault copy |
| operability O08 — error handling | `malformed`: malformed inputs and engine failures refuse; `dependencies`: missing dependencies, unreadable inputs, and scan errors cannot become SAFE/DELETE |
| operability O09 — repeatability | `repeat`: two runs on unchanged fixtures have identical normalized results; `bounded`: the named timeout bounds completion, with timeout treated as blocked/refusal |
| operability O10 — side effects | `dry-run`: pre/post hashes, names, modes, refs, index and file contents show no dry-run changes; `confinement`: headless probes read no protected content and mutate no surface outside the fixture |
| coverage K01 — fleet-root artifacts | `inventory`: exact frozen root candidate set, including zero-candidate/blocked dispositions; `classification`: every member has a receipt or explicit refusal with an oracle |
| coverage K02 — lane repositories | `inventory`: exact frozen roster of main repos plus explicit exclusions (no silent missing lanes); `classification`: clean/dirty/unpushed/no-remote states and linked-worktree ownership represented for every member |
| coverage K03 — artifact forms | `file-directory`: files and directories, including missing/empty targets; `links`: symlink, hardlink and containment cases, with protected-target contents never opened |
| coverage K04 — worktree metadata | `registration`: present/absent, detached/named registrations; `locks`: locked pins, unpushed tips, and exact-ticket metadata-only pruning on fixtures |
| coverage K05 — stale surfaces | `clock`: below/equal/above age threshold and future mtime; `scan`: hidden, ignored, binary and live-reference inputs plus scan-error refusal |
| coverage K06 — pushed provenance | `refs`: valid, absent, ambiguous and local-only default refs; `changes`: later local commits, dirty bytes, directory descendants and path encodings |
| coverage K07 — preservation ledger | `rows`: valid, malformed, duplicate, missing-hash and missing-source/vault rows; `survival`: distinct copy, same inode/path, inside-source copy, digest drift and directory links |
| coverage K08 — protected surfaces | `names`: secret-shaped path families and aliases tested with synthetic sentinels/no-read tracing only; `operator-runtime`: operator configuration and driver-runtime exclusions tested in fixtures only |
| coverage K09 — quarantine lifecycle | `stages`: normal and refusal paths through every stage; `adversarial`: hold races, collision, escape, control-character paths and failed second-check preservation |
| coverage K10 — census/differential boundary | `enumeration`: inventory, zero/no-remote, linked-worktree and error-row handling; `comparison`: repeated snapshot, known delta, malformed baseline and normalized cross-engine disagreement |

### Committed report interface

`census/round-9/seat-13.json` holds the assessment and provenance, not hand-set
scores. The empty assessment supplied with this draft intentionally produces
PROVISIONAL zero evidence credit, **not a claim that the installed tools have
zero capability**. Parent integration must first freeze the final tool commit,
collect reports against it, and commit those reports and the filled assessment.
Never copy forward a historical run without rechecking its target/hash pins.

`assessment.cells` maps a stratum ID to
`{"primary":{"path":"census/round-9/seat-NN.json","run":"id"},"replay":null}`.
An independent replay uses the same reference shape instead of null. Each
referenced report contains `rubric_runs[id]` with these fields:

- `cell`, `author`, `subject_commit`, `tool_sha256`, `scope_sha256`;
- `scope`: `fixture` or `committed-artifacts`;
- `command`: full reproducible command sequence, not a disposable fixture path;
- `exit_code`: actual harness integer status. COMPLETED harnesses exit 0
  (all-pass) or 0/1 (one or more assertions failed), never a signal/timeout
  status; tool refusal statuses are captured inside the command's evidence
  and need not be zero. Authors are compared after trimming and case folding;
- `stdout`: captured JSON string, containing exactly `state`, `exercised`,
  `passed`, and `safety`. `state` is COMPLETED, BLOCKED, or NOT-REPRODUCED.
  `exercised` and `passed` map every check ID for that stratum to a Boolean.
  A passing check must have been exercised. `safety` maps `false_safe`,
  `false_delete`, `protected_read`, and `outside_scope_write` to nonnegative
  integer observations. An incomplete run must report zero confirmed safety
  events. The command must derive these facts from the actual oracle/output
  and postconditions, not print a preset PASS. Primary and independent replay
  compare these normalized facts, so random fixture path names are excluded.

The collector/independent reviewer validates the check predicates in the table;
a JSON field alone is not proof that its command implements the oracle. The
reference scorer checks provenance, shape, consistency, and arithmetic, not
arbitrary shell correctness or cryptographic author identity. Independent means
a genuinely different executor, not rerunning with a renamed `author` value.
Reports must preserve their command's raw oracle/tool observations alongside
this normalized interface for audit. No implicit normalization of old prose.

### R9-SCORE-v1 — canonical counting pipeline

Run from this lane repo after integration. Set `E` to the **full evidence
commit** containing both assigned files and all referenced reports. The target
commit `T` is independently pinned inside the assessment. This pipeline uses
only local committed blobs, Git, and Python 3's standard library; it performs
no network operations, fixture execution, or working-tree reads/writes.

```bash
set -euo pipefail
E=<full-40-hex-evidence-commit>
git show "$E:census/round-9/rubric-13.md" |
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

A malformed/missing referenced blob, hash drift, duplicate JSON key, unknown
stratum, or false closure produces INVALID-EVIDENCE and exit 2, never a
plausible zero or an inflated score. PROVISIONAL scores are lower-bound evidence
accounting only: they do not replace measured SCORECARD rows or trigger the
saturation/stagnation rule. A closed run may honestly have BLOCKED or
NOT-REPRODUCED strata; those checks earn zero and remain visible in its source
reports. Compare before/after only with the same rubric and frozen scope.
No round-count, judge-vote, file-count, bytes-deleted, or live gate-opening bonus.

### R9-CARD-CHECK — reproducible legacy contradiction check

At target `14916c075c7de4b905d92c472e6312026d12d44a`, the axes table says
calibration 7 / operability 8 / coverage 8, while the saturation sentence says
calibration 6 / operability 7 / coverage 8: **two internal numeric contradictions**.
This check reads only the committed SCORECARD, not live fleet surfaces.

```bash
python3 - <<'PY'
import json, re, subprocess
T = '14916c075c7de4b905d92c472e6312026d12d44a'
s = subprocess.check_output(['git', 'show', T + ':SCORECARD.md']).decode()
table = {a: int(v) for a, v in re.findall(r'^\| (coverage|calibration|operability) \| (\d+) \|', s, re.M)}
m = re.search(r'Coverage (\d+),\s*operability (\d+), calibration (\d+)', s)
assert m and len(table) == 3
paragraph = dict(zip(('coverage', 'operability', 'calibration'), map(int, m.groups())))
delta = {a: {'table': table[a], 'paragraph': paragraph[a]} for a in table if table[a] != paragraph[a]}
print(json.dumps({'target': T, 'contradictions': len(delta), 'details': delta}, sort_keys=True))
PY
```

Integration: replace both the legacy numeric rows and saturation prose only
when a closed R9-SCORE-v1 assessment has been committed and independently
reviewed. Otherwise retain the historical rows explicitly as legacy/unmapped,
correct the two stale saturation numbers, and publish no invented replacement
scores. This seat edits neither SCORECARD.md nor shared bookkeeping.
