# S44mutationtester50 — always-findings control

**Result: KILLED, not a crash.** Axes: calibration / operability / coverage; assigned axis operability. Admission and numerical score changes are outside this probe.

## Scope and execution

Read the preregistration and frozen C2 instruments. All source snapshots came from `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:<path>`, not mutable worktree source.

Actual bounded command (exit 0):

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44mutationtester50/probe.py
```

`probe.py` compiles the exact frozen audit and counter into in-process modules. For each candidate state it calls the same frozen `audit.main(['--tool', '/fast/scratch/hyaku/souji-r44/S44mutationtester50/candidate.py', '--work', '/fast/scratch/hyaku/souji-r44/S44mutationtester50/<state>-work'])`, captures output/exit, then applies frozen `counter.audit_verdict`. The command arrays in receipts describe equivalent CLI arguments, not additional subprocess executions of the audit. Actual fixture tools execute as `python3 -B candidate.py --root <fixture> --prereg prereg.txt --rev <fixture-tip>`; h10 uses the missing preregistration path.

The only behavior substitution is the frozen counter's exact `STUB_FINDINGS`: an input-insensitive tool printing `FINDING C1 NO-CLAIMS x`, `SUMMARY claims=0 findings=1`, and exiting 1. Candidate and fixtures lived exclusively in seat scratch. Frozen instruments were not edited. A subprocess guard asserts fixture toplevel equals fixture directory before each git add/commit; git initialization is constrained to seat scratch. 138 guarded mutations were observed across the three audit executions.

## Actual results

| Candidate | Audit exit | Audit output | Counter parser `(pass,fail,total)` |
|---|---:|---|---|
| Pristine | 0 | `SUMMARY scenarios=10 pass=10 fail=0` | `(10,0,10)` |
| Always-findings | 1 | `SUMMARY scenarios=10 pass=0 fail=10` | `(0,10,10)` |
| Exact restoration | 0 | `SUMMARY scenarios=10 pass=10 fail=0` | `(10,0,10)` |

Pristine/restored: all ten scenarios PASS. Mutated: all ten FAIL. h1–h9 each report `got rc=1 classes=C1:NO-CLAIMS`; h10 fails its refusal expectation. The audit completed its summary with empty stderr, so rejection is behavioral detection, not audit failure/crash. The counter's stub predicate (`fail > 0 and pass < total`) evaluates true for the observed tuple, corresponding to `findings_stub=REJECTED`.

Direct control invocation, captured in `receipts.json`:

```sh
/usr/bin/python3 -B /fast/scratch/hyaku/souji-r44/S44mutationtester50/candidate.py --root /fast/scratch/hyaku/souji-r44/S44mutationtester50 --prereg absent.txt --rev d314fd6e85d62565344fa6c4b102f52f62297884
```

Exit 1, empty stderr, stdout:

```text
FINDING C1 NO-CLAIMS x
SUMMARY claims=0 findings=1
```

## Hash and restoration evidence

SHA-256:

- Frozen counter: `0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252` (matches preregistration).
- Frozen audit: `50872b0da7a36d377ced9cf0e51579ef00f0f0ae402eebad8c579fce6e5e843e`.
- Candidate before: `f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999`.
- Always-findings: `5f03cda41b129cb3e0045304ecc6c95e48a6b7110b6c46ec130af9a25b6a0611`.
- Restored candidate: `f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999`.

Byte equality restoration was true before scratch deletion. `scratch_removed=true` records cleanup of the explicitly created seat scratch. Receipts preserve full per-state stdout/stderr, exact source snapshots, candidate bytes, reproduction driver, commands, and hashes. No production/sibling/fleet/index/shared-log writes or tool installations occurred.

## Limits

This establishes discrimination against this one always-findings control only. The full C2 counter main (retention, selftest, TMPDIR legs) was intentionally not executed; no whole-counter target or general oracle soundness is claimed. No mutation to the frozen audit or counter and no shipping/integration decision was made.

Self-evaluation: accuracy 4 (full counter not exercised, explicitly scoped); completeness 5 (same detector pristine/mutated/restored with receipts); clarity 4 (in-process harness requires distinguishing CLI-equivalent receipt arrays); actionability 5 (retained executable driver and snapshots); conciseness 4 (hashes and execution details add necessary audit length). Overall 4.4/5. Improvement priority: consumers should use the actual probe command, not treat receipt arrays as additional CLI runs. Would the user agree? Evidence and stated limits support the scoped result.
