# SwarmMutationTester29-2 — r30 W2 mutation test of census/round-30/c3-counter-v2.py (A2 counter)

## Status
STATUS: PASS — all six assigned mutants ran end-to-end against the counter at the C3 landing rev 76c94eb41fc38093d7143a016006b6275e102d5d and lane tip 9dcd367655fc28ba73d679a0e2cadaff96d2bcb8; 6/6 SURVIVED the frozen-state detector (byte-identical output, rc=0) and 6/6 were KILLED by an adversarial committed-state detector (pristine rejects, mutant accepts). PASS means the attack ran; it does not mean the target is broken — verdicts below.

## Evidence
- Read first: census/round-30/records/preregistration.txt (frozen; C3 enumerate line), census/round-30/records/amendments.txt (A2: "Target: `SUMMARY-V2 e1=ok e2=ok e3=ok e4=ok f1_exact=3`").
- Target file: census/round-30/c3-counter-v2.py, lane worktree sha256 98d4bd43965206ef8bbf87864e2516927573bf33b020afb463baaa0781d01a45, byte-identical to HEAD blob at 9dcd367655fc28ba73d679a0e2cadaff96d2bcb8 before and after all runs; `git status --porcelain` on the path empty throughout. The lane file was never edited; all mutants were separate scratch copies.
- Baseline (pristine, my scratch clone, origin removed): rc=0 at both revs, `E1 PASS entry_exact=True f1_exact=3`, `E2 PASS`, `E3 PASS rc=0 replay_lines=10 record_lines=10`, `E4 PASS snapshots=4 bad=[]`. Deterministic across both revs. Baseline failures would have been inconclusive; none occurred.
- Tools used (operator 2026-10-19; RULES.md read; NO installs, pacman untouched): jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5, git 2.56.0, python3 -B 3.14.8, curl 8.23.0, bash 5.3.20.
- Full raw outputs, mutant sha256s, adversarial revs: .ufo/waves/round-30/w2/SwarmMutationTester29-receipts.txt

## Findings
1. **No committed state can kill any A2 guard — C3-v2 ships without a negative fixture.** At every rev where the counter can pass (landing, tip), each of the six guard-weakening mutants produces byte-identical output and rc=0; `diff` against pristine is empty. Contrast C2, which landed a dedicated adversarial fixture (tests/fixtures/r30-landing-gate-discovery.py per the tasking); A2 mandates only the happy-path replay, so E1/E2/E4's rejection branches are exercised by no committed bytes.
2. **The E1 `F1-jj` boundary guard is vacuous on committed corpus.** `grep 'ground: F1-'` over corpus/ returns no matches; exactly 3 knowledge files carry plain `ground: F1` (git-auto-maintenance-trigger-set.md, git-auto-maintenance-trigger-set-r23.md, jj-keep-ref-expiry.md) and README:39 is the only `F1 ` row ("F1 git-native housekeeping vs receipts", entries cell ends "`knowledge/jj-keep-ref-expiry.md`"). The guards are correct code, but a regression planting a suffixed token would need an adversarial probe to catch — none exists in-tree.
3. **E4's live fetch is the only leg whose pass is never distinguishable at a fixed rev.** Mutant m6 (skip curl, `live = want`) is invisible whenever committed receipts and committed blobs agree — which is every passing rev. Within committed-state evaluation E4 degenerates to `blob == receipt` (both lane-authored bytes); only a lying receipt+blob pair or a fetch failure (COULD-NOT-EVALUATE, exit 2) changes observable behavior. The L1's "v2 e1..e4=ok" reading therefore certifies blob/receipt agreement and replayability, not live-world agreement, at the evaluated rev.
4. **E3 is the one adversarially self-binding leg by design.** Replay-vs-record is state+execution bound: m4 (content tampered, rc=0) and m5 (correct lines, rc=3) are each caught by a separate tripwire in the pristine counter. This is the model the other legs lack.
5. **L1 reading "C3 met" survives this mutation battery.** None of the six mutants can flip a SUMMARY on committed bytes, so the landed claim is not overthrown; the exposure is a coverage/robustness gap (finding 1), reported as an ATTACK suggestion, not a contract change — amendments are stricter-only and the frozen A2 target is met as written.

## Attack log
| # | Mutant (smallest behavior-bearing point) | Frozen-state @76c94eb + @9dcd367 | Adversarial state (scratch rev) | Verdict |
|---|---|---|---|---|
| M1 | E1 enumeration regex `^ground: F1(?:[ \t]|$)` -> `^ground: F1` (accepts `F1-jj`) | IDENTICAL, rc=0 — SURVIVED | adv-m1 5db56119: 4th knowledge file with `ground: F1-jj`; pristine f1_exact=3 ok, mutant f1_exact=4 FAIL | KILLED (guard HOLDS; vacuous in-tree) |
| M2 | E1 `e1 = entry_exact and len(exact) == 3` -> `e1 = len(exact) == 3` | IDENTICAL, rc=0 — SURVIVED | adv-m2 3118082d: entry's ground line stripped + decoy plain-F1 file; pristine E1 FAIL entry_exact=False, mutant E1 PASS | KILLED (guard HOLDS) |
| M3 | E2 row matcher `^\|\s*F1 ` -> `^\|\s*F1` (accepts `F1-jj` edge row) | IDENTICAL, rc=0 — SURVIVED | adv-m3 37fab3a6: plain row renamed `F0 `, F1-jj row names the entry; pristine E2 FAIL, mutant E2 PASS | KILLED (guard HOLDS; vacuous in-tree) |
| M4 | E3 `got == keep(rec)` -> `len(got) == len(keep(rec))` | IDENTICAL, rc=0 — SURVIVED | adv-m4 b752ba21: fixture prints `cmd=tampered-note`, exits 0; pristine E3 FAIL, mutant PASS | KILLED (guard HOLDS) |
| M5 | E3 drops `p.returncode == 0 and` | IDENTICAL, rc=0 — SURVIVED | adv-m5 cf546cce: fixture `exit 3` after identical lines; pristine E3 FAIL rc=3, mutant PASS | KILLED (guard HOLDS) |
| M6 | E4 curl block -> `live = want` (skip live fetch) | IDENTICAL, rc=0 — SURVIVED | adv-m6 2996ae11: receipt URL -> file:// decoy (sha 24810e5f...) with blob still matching receipt; pristine E4 FAIL `...:hash`, mutant PASS | KILLED (leg HOLDS; finding 3) |
| — | Frozen claim "C3 met, v2 e1..e4=ok at landing" | not overthrown: no mutant flips committed-state output | n/a | HOLDS; coverage gap = DEFECT-NOT-FATAL (finding 1) |

Method note: adversarial states are single probe commits in disposable scratch clones (adv-m1..adv-m6, origin removed, identity `SwarmMutationTester29-2-scratch`, never pushed, removed after capture). Scratch-internal git use mirrors the frozen counter's own scratch clone/checkout behavior; the lane and all shared paths were only read. Restoration evidence: lane target sha256 98d4bd43... before == after; porcelain empty; scratch clone worktree clean at 9dcd3676.

## Deliveries
- .ufo/waves/round-30/w2/SwarmMutationTester29.md (this report)
- .ufo/waves/round-30/w2/SwarmMutationTester29-receipts.txt (raw per-run outputs, mutant sha256s, adversarial revs, restoration hashes)
- Scratch /fast/scratch/hyaku/souji-r30/MutateC3v2/ removed after capture.
