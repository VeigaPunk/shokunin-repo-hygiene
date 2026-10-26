# SwarmMutationTester30 — C3 counter mutation test (souji round 30, wave 1)

Report: .ufo/waves/round-30/w1/SwarmMutationTester30.md

## Status

STATUS: PASS — all 8 assigned mutants of `census/round-30/c3-counter.py` killed (M2 by the committed C3-junk control, the other 7 by constructed scratch states); no survivors; the lane counter's bytes untouched (sha256 identical before/after, `git status` clean).

## Evidence

- Scratch: `/fast/scratch/hyaku/souji-r30/MutateC3Counter/` — clone `c` (origin removed immediately), mutant copies `m/M1-M8.py`, kill-state commits, run logs `runs/`; removed after delivery. Consolidated receipts: `SwarmMutationTester30-receipts.txt` in this directory.
- Detector: `python3 -B <counter> --root <clone> --rev <state> --scratch <scratch>/ctmp` per state; a mutant is killed when its SUMMARY on a frozen-control state deviates from the frozen receipt, or when it prints the target SUMMARY (`fail=0 f1_entries=3`) on a state the pristine counter rejects. Pristine = the lane's committed counter, sha256 `21bc8a5d0237a4d8b7e6e8b58e591110ae25135593e3a1c063c9c32389a67d18`.
- Baselines reproduced with the pristine counter:
  - base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` → `SUMMARY legs=9 fail=8 f1_entries=2` rc=1 — equals the frozen C3-do-nothing receipt.
  - junk `f582b63fe60d5b9ae2e3c4b03015cc12e58a5cac` (C3-junk recipe from `census/round-30/controls.sh:56`, "C3 junk: a sourceless F1 entry named in the F1 map row, with the run-record path string but no record") → `SUMMARY legs=9 fail=5 f1_entries=3` rc=1 — equals the frozen C3-junk receipt. The recorded control rev `bfdeeeaaa44b…` is not an object in the lane or fleet repos; the recipe reconstruction is tree-identical and receipt-identical.
  - target-state fixture `P = efac366f765d596bc47b04868c58ca40e0b58c93` → `SUMMARY legs=9 fail=0 f1_entries=3` rc=0 — the exact C3 target ("Kill rule: any other SUMMARY is a miss.", `census/round-30/records/preregistration.txt:9`). Fixture honesty: its two `jj help` snapshots and `git_backend.rs` are real bytes (jj 0.45.1-7c41cdeb on this host; source fetched at tag v0.45.1), the run record is a real jj 0.45.1 measurement in a scratch repo (keep refs 3 → 3 after `jj op abandon` → 0 after `jj util gc --expire now`; never a lane repo), but the entry prose and rows S220–S222 are synthetic fixture content — not a proposed lane landing; the real C3 entry belongs to the C3 seat.

## Attack log

| id | single-point patch (c3-counter.py line) | C3-junk control kills? | kill state (scratch commit) | verdict |
|---|---|---|---|---|
| M1 | L1 anchor dropped: `r"^ground: F1\b"` → `r"ground: F1\b"` (:55) | no — junk output unchanged (`fail=5 f1_entries=3`) | K-M1b `d1d48d15`: entry re-grounded `ground: F2`, named in the F2 map row, `ground: F1` only mid-line → mutant `fail=0 f1_entries=3` (false PASS) vs pristine `fail=1 f1_entries=2` | KILLED (scratch) |
| M2 | L2 literal swapped to `grounded=16 mapped=15 dangling=0 mismatches=0` (:67) | YES — junk prints `grounded=16 mapped=16 …` → mutant L2 FAIL → junk SUMMARY `fail=6 f1_entries=3` ≠ frozen `fail=5` | — | KILLED (junk control) |
| M3 | L4 fetch-receipts sha comparison dropped (:106) | no — junk L4 fails on absent snapshots either way | K-M3 `568d0fc2`: receipts sha for `jj-util-gc-help.txt` zeroed, SHA256SUMS still true → mutant `fail=0` vs pristine `fail=1` (`L4 … bad=['census/round-30/sources/jj-util-gc-help.txt']`) | KILLED (scratch) |
| M4 | L5 upper word bound dropped: `<= 25` removed (:110) | no — junk gate has no quotes | K-M4 `161867a6`: 43-word quoted span spanning a newline → mutant `fail=0` vs pristine `fail=1` (L5 only; L3 PASS — gate-check cannot see the span) | KILLED (scratch) |
| M5 | L6 `opened` read from recheck column `rows[i][10]` (:114) | no | K-M5 `7d414cca`: cited rows `opened=2026-10-25`, `recheck=2026-10-26` (validate-clean) → mutant `fail=0` vs pristine `fail=1` (`opened_today=[]`) | KILLED (scratch) |
| M6 | L8 `jj-version:` clause dropped (:122) | no — junk run record absent | K-M6 `34241bc1`: run record keeps 4 `RESULT ` lines, no `jj-version:` line → mutant `fail=0` vs pristine `fail=1` | KILLED (scratch) |
| M7 | L9 verdict hardcoded `True` (:124) | no — junk L9 passes anyway | K-M7 `abb00bc2`: row S999 duplicates S220's url+scope (E04, validate rc 1) → mutant prints `L9 PASS sources-census rc=1` and `fail=0` vs pristine `fail=1` | KILLED (scratch) |
| M8 | entry read from the working tree instead of `blob(R, V, ENTRY)` (:93) | no — working tree matched the junk checkout | K-M8 `d452ff2a`: committed entry lacks the Measured/run-record line, working tree has it → mutant `fail=0` vs pristine `fail=1` (L8) on the same rev | KILLED (scratch) |

Survivors: none. Corroborating false-negative probes (mutant rejects a state pristine PASSes): M1 on K-M1a `f976dd64` (`fail=1 f1_entries=4` vs pristine `fail=0 f1_entries=3`); M2 and M5 on P (`fail=1` vs pristine `fail=0`).

## Findings

1. The committed C3-junk control kills only M2 of the eight. It is broad but shallow: its five failing legs (L3, L4, L5, L6, L8) each still fail under a single-leg mutant, so only a mutant moving a leg the junk state already exercises in a divergent direction (L2) is caught. The seven other kills needed "junk-with-everything-else-fixed" states — my K-state recipes (receipts §C/§C2) are candidate material if the L1 ever wants controls that catch counter mutants directly; stricter-only amendment, L1's call. [INFERENCE on intent; the receipts are the evidence.]
2. L5's 4–25-word rule is the only check that sees a quoted span spanning a newline: the counter matches over the whole Gate string (`census/round-30/c3-counter.py:109`, `quotes = re.findall(r'"([^"]{2,400})"', gate)`) while gate-check matches per line (`tools/souji-gate-check.py:83`, `for lineno, line in enumerate(gate.splitlines(), 1):`). K-M4 shows a two-line 43-word span failing L5 alone (L3 PASS). No defect in the committed counter; but if L5 were weakened, nothing else catches multi-line over-long quotes.
3. M2's alternative reading — accept either the mapped=16 or the mapped=15 exact line — is an equivalent mutant: `grounded=16 mapped=15 dangling=0 mismatches=0` is unreachable, because the coverage tool appends a MISSING-FROM-MAP mismatch for every unmapped grounded entry (`tools/souji-coverage-agreement.py:160`, "mapped += not missing"). Probe K-M2probe `1500d047` (entry grounded, map row reverted): `grounded=16 mapped=15 dangling=0 mismatches=1`.
4. M8 is the sharpest risk class: a counter reading the entry from the working tree certifies a landing whose committed entry omits the measurement reference. The committed-bytes-only `blob()` helper (`census/round-30/c3-counter.py:32`, `p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)`) is load-bearing for L4–L8.
5. Provenance: the C3-junk control's recorded rev `bfdeeeaaa44b…` resolves in neither the lane nor the fleet repo (`git cat-file` fails in both); the receipt reproduces exactly from the `controls.sh` recipe (reconstruction `f582b63f`). The frozen receipt binds; the control commit object was discarded with the L1's scratch.
6. Tooling: nothing installed or upgraded (nothing needed); no pacman transaction; no lane git/jj mutation (read-only `git log/show/grep/cat-file/rev-parse` against the lane only).

## Deliveries

- `.ufo/waves/round-30/w1/SwarmMutationTester30.md` — this report.
- `.ufo/waves/round-30/w1/SwarmMutationTester30-receipts.txt` — consolidated run receipts: pristine baselines, full 42-run mutant matrix, decisive full outputs, mutant patches, M2 equivalence probe, restoration evidence, state shas.
