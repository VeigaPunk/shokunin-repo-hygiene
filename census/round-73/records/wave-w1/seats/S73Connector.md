# S73Connector — round 73 cross-claim / sibling-overlap scan (read-only)

| # | item | verdict | evidence |
|---|------|---------|----------|
| 1 | C2 receipts read only lane-base writer bytes | SEPARABLE | all 10 receipts carry `# slot new=… sha256=b7790001…244d src=a789486…:tools/souji-receipt-write.py` (records/c2-after-D1.txt:10; controls/c2-before-r72-D1.txt:8). Counter resolves `--tool` from the git object (`git show rev:rel`, census/round-73/c1-counter.py:2195-2198), so stage-W bytes never run; `grep -c RECEIPT-WORKTREE-STAT-CONCEALED` = 0 in every C2 receipt. |
| 2 | C1 EXIT=0 ↔ C2 coupling | COUPLED (one term) | claim_upheld (c1-counter.py:1477-1483) gates `base_unwitnessed` only; `new_unwitnessed` is printed (1486-1494) but ungated; `base_mismatches` is base-slot expectation, not C2. |
| 3 | Sibling lane clean-tree gates | VULNERABLE / SAFE | see rows below |
| 4 | Other souji tools trusting clean status | VULNERABLE | see rows below |

Sibling gates (all fooled by the committed forge shape `census/round-73/probes/fx/idxcraft-run.py`, sha 3adb9f7b…a091):
- kama `tools/round73-round-scope-cases.py:23-27` case B (`status --porcelain -uall` = stray population) and `tools/pre-report-gate.py:38` arm 6 — VULNERABLE.
- kagi `corpus/laneguard.sh:28,40-50` snapshot (status+`diff --binary`) → CLEAN — VULNERABLE.
- kasegi `corpus/instruments/r36-closure.sh:465` / `r37-closure.sh:581` E9 quiescence and `r46-landing-gate.py:113-115` tree-clean — VULNERABLE (fail-closed read status does not help: the read succeeds and lies).
- kaidoku `tools/round-29/prefile-check.sh:22-28`, `tools/round-42/prefile-gate.py:265-286` — VULNERABLE.
- mado `quality/landing-counters.sh:271-272`, `quality/q36-successor-run.sh:43` — VULNERABLE.
- audio `corpus/live/r89-simplifier/proofs/run-all.sh:49-50` (`diff --quiet HEAD`) — VULNERABLE; r88 `:57` is log-only.
- tameshi `tools/mutate-and-run.sh:2059-2071` canary "index/worktree unchanged" — VULNERABLE.
- game-dev-3d `…/unreal-mcp/gate/run_gate.sh:230-236` clone-dirty limb — VULNERABLE for "clone worktree == pin", but the byte claim is independently re-derived at :243-250 (sha256 vs `git show PIN:`) → gate SAFE overall.
- SAFE: mori `tools/mori-index-clean.sh` (index-only predicate, worktree edits excluded by design); tsukuroi/chousa/kumitate/tabi/kotoba/kake/revenger/lore: no clean-tree gate in tools/ (grep over *.sh/*.py = 0).

Other souji tools (besides `tools/souji-receipt-write.py`, which is the fix):
- `tools/souji-pre-report-gate.sh:36-37` "No lane changes may remain before report filing" → clean PASS — VULNERABLE (HIGH: the L1's own filing gate).
- `tools/souji-verify.sh:377,421` and `tools/souji-vault-verify.sh:550,594` dirty=0 → SAFE verdict — VULNERABLE; same shape in 16 `tools/cand-*-verify.sh` (e.g. cand-a1-verify.sh:383,427).
- `tools/souji-record-agreement.py:351` K4 population — VULNERABLE (a concealed path is never a mismatch).
- `tools/souji-guard.r9-s18.sh:175` `diff --quiet "$ref" -- path` as snapshot equality — VULNERABLE.
- `tools/souji-idx-repair.py` — SAFE for what it asserts (repairs are sha256-verified against the rev blob) but blind to concealment: status is its population.

Re-derivation (scratch, own fixture): forge sha 3adb9f7b…; after forge `status --porcelain`=``, `diff --quiet HEAD -- tools/counter.py` rc=0, `diff-files --quiet` rc=0, `ls-files -m`=``, while `hash-object`=3607175e… vs `HEAD:tools/counter.py`=5cfa8c0b… (bytes `counter v2` vs `counter v1`).
Replays: main arm SUMMARY byte-identical to records/c1-after.txt, EXIT=0; D1 arm SUMMARY identical to records/c2-after-D1.txt (base_unwitnessed=1, FWr base=accept base_witness=no, EXIT=1); counter selftest 52/52; writer selftest 44/44 (d1ad5c79…). Before-controls: each Dk credits its row (`CASE FWr|FWi|FWp|FWs|FC3 … base=accept`), base_forgeries=12, EXIT=0.

Findings:
- HIGH — the stat-cache forgery defeats every gate above; two are load-bearing: kama's own round-73 scope counter (same defect class as souji D3, a sibling lane shipping it as its C1) and souji's pre-report clean gate.
- MEDIUM — SUMMARY `base_forgeries` is not witness-gated: c2-after-D1 prints base_forgeries=15 including the defanged FWr, while `classify_outcome` counts an unwitnessed accept as error (c1-counter.py:1503-1512). Verdict is right; the printed count still "credits" the row.
- LOW — witness `tree_divergence` raises only CaseError (c1-counter.py:1063-1110); an OSError aborts the run instead of failing closed into base_unwitnessed (runtime coupling beyond the one field).
- LOW — C2 receipts record `lane master=b84ff90` (stage W) in their header; provenance only, but readable as coupling.
- LOW — game-dev-2d `corpus/live/r93-verifier/probes/audit_committed.py:5` asserts "byte-equal to HEAD" from `git diff --quiet HEAD`; the script never re-verifies against the HEAD blob.

Files written: `.ufo/waves/round-73/w1/S73Connector.md`, `.ufo/waves/round-73/w1/S73Connector/replay.txt`. No tool installs. Scratch removed.
