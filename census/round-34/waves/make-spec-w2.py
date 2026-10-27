import collections
import json

L = "/home/vgpnk/Projects/shokunin/souji-shokunin"
W = L + "/.ufo/waves/round-34/w2"
W1 = L + "/.ufo/waves/round-34/w1"
SCR = "/fast/scratch/hyaku/souji-r34"
BASE = "9c76c7222a8abff027af42e37f0d160d52526bba"
LIST = "2b0171e2071fdc9c16a69bed12b0d040e574d8c8"
REPAIR = "2b0171e2071fdc9c16a69bed12b0d040e574d8c8"

CONTEXT = f"""# Goal
Round 34 souji wave w2 — adversarial falsification of W1's concrete C1/C2 attack findings. Lane {L}; base {BASE}; frozen C1/C2 list revision {LIST}; C2 counter repair/re-pin {REPAIR}; read the frozen preregistration and W1 reports first. W1 returned 40 seats and identified ≥32 distinct falsification targets: the 25 C1 do-nothing mismatches plus seven separate C2 instrument/leg failures or attack surfaces. This wave has 32 seats, each assigned one distinct attack target below.

# Contract
- Read-only. Do not edit lane files, change frozen items/predicates, commit, push, or touch other repositories. Report only a reproduced defect or a clearly labeled source-level hypothesis; do not claim execution you did not perform.
- Scratch roots, if needed, are item-specific under {SCR}/<item>/; avoid large clones or fixture execution. Main has imposed a <50 MB scratch ceiling unless explicitly approved. Prefer inspection of existing committed evidence under {W1}/.
- For each assigned target, test the specific W1 claim adversarially: try to falsify its reasoning, identify a benign alternate explanation, or independently confirm the impossibility/escape with a bounded reproduction. Distinguish reproduced evidence from inference. No duplicate findings across seats; report the target's finding and any counter-evidence.
- Reports only under {W}/. Format: ## Status, ## Evidence, ## Findings, ## Attack log, ## Deliveries. Use exact file:line and committed revisions.
"""

C1 = ["G05", "G11", "G17a", "G17b", "G21", "G23", "G24", "E04", "E05", "E07", "E08b", "E09a", "E14a", "E14b", "E15c", "E18", "E23a", "E23b", "E24", "E25", "E26", "E27", "E29", "E31", "E32"]
C2 = ["C2W2Timeout", "C2W3PathNormalization", "C2N3Timeout", "C2J1Timeout", "C2WitnessScope", "C2G5Disjointness", "C1WildcardExit"]
ITEMS = []

def add(role, item, attack):
    report = f"{W}/{item}.md"
    ITEMS.append({"item": item, "role": role, "prompt": f"""Adversarially falsify the W1 finding for {item}: {attack}
Read the relevant report(s) and existing receipts under {W1}; use read-only source/revision inspection and at most small bounded probes. Is the alleged defect real, unreachable under another frozen clause, or a measurement artifact? Give exact reproduction commands/output if actually run; otherwise label inference. Do not alter frozen artifacts. Write your report to {report}."""})

for i, target in enumerate(C1):
    role = "critic" if i % 2 == 0 else "reviewer"
    add(role, "Attack" + target, f"Target C1 item {target}; inspect its frozen row in {L}/census/round-34/c1-items.tsv, the base do-nothing record, and the corresponding W1 deliverable. Independently test whether the W1 proposed blockage/correction is valid under the frozen cause, argv, exit, statement, and Q76 rules; identify any honest rule-conforming route the seat missed, or confirm no route.")

c2attacks = [
    "Target C2 W2 timeout: inspect the repaired sandbox execution and R15CFG-01 timeout evidence. Determine whether timeout is caused by the bwrap/TMPDIR boundary, external load, or fixture behavior, and whether the frozen leg can pass without changing the pinned fixture.",
    "Target C2 W3 output mismatch: inspect the scratch-bearing last digit line and the frozen comparison. Determine whether path normalization is required by the frozen leg contract and whether the counter currently implements it.",
    "Target C2 N3: inspect the private bind, staged tool, 12 CASE results, pin digest and canary evidence. Determine whether a genuine 12/0 result is achievable under the frozen fixture with current host resources.",
    "Target C2 J1 timeout: inspect the fixture's five stub cases and counter timeout behavior. Identify whether the failure is from test cost, deadlock, or a real missed failure; don't repeat an oversized run.",
    "Target C2 witness scope: evaluate whether any traced file creation is sufficient evidence that the named tool did work; seek a minimal counterexample or explain why the W1 mutation/stub controls close it.",
    "Target C2 G5: inspect the frozen path-set disjointness guard and the amendment/re-pin commits. Determine whether the mixed C1/C2 freeze commit defeats G5's claimed whole-set guarantee.",
    "Target C1 wildcard exit: inspect the reproduced E18 wildcard survivor and the frozen judge. Determine whether any other frozen rule rejects it; do not amend the counter.",
]
for i, (item, attack) in enumerate(zip(C2, c2attacks)):
    add("critic" if i % 2 == 0 else "reviewer", "Attack" + item, attack)

roles = collections.Counter(x["role"] for x in ITEMS)
assert len(ITEMS) == 32 and len({x["item"] for x in ITEMS}) == 32
assert sum(roles[r] for r in ("critic", "reviewer", "mutation-tester")) * 4 >= len(ITEMS)
spec = {"wave": "souji-r34-w2", "reportDir": ".ufo/waves/round-34/w2", "maxLanes": 64, "context": CONTEXT, "items": ITEMS}
with open(L + "/.ufo/waves/round-34/w2-spec.json", "w") as f:
    json.dump(spec, f, ensure_ascii=False, indent=1)
print(len(ITEMS), dict(roles))
