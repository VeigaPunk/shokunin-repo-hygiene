# S44mutationtester49 — always-clean control

Axes: calibration, operability (assigned), coverage. Admission remains outside non-author closure.

## Result

**KILLED, not a crash.** The frozen repaired audit discriminates the always-clean tool replacement. Pristine and byte-restored tools both pass 10/10. The always-clean candidate exits normally with a plausible SUMMARY but passes only the two genuinely clean cases; the audit returns 1, pass=2, fail=8. Frozen counter `audit_verdict` parses `(2,8,10)` and its exact stub-rejection predicate evaluates true.

Frozen revision: `d314fd6e85d62565344fa6c4b102f52f62297884`. Preregistration and both C2 instruments were read. Only private scratch tool bytes were replaced; neither frozen counter nor audit was edited.

## Mutant and expected detector

Candidate `always-clean.py` is byte-identical to counter `STUB_CLEAN`:

```python
import sys
print('SUMMARY claims=1 findings=0')
sys.exit(0)
```

Defect: every invocation reports clean, including malformed, duplicate, premature-dispatch and missing-prereg inputs. Expected detector: the ten-scenario frozen hidden audit must reject with exit 1 and fewer than ten passes. Then the frozen counter's parser and rejection expression must recognize that failure rather than classify a crash as detection.

## Exact execution

Frozen inputs were extracted using `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:<path>` for `tools/souji-freeze-check.py`, `census/round-44/c2-counter.py`, and `census/round-44/c2-hidden-audit.py`.

With cwd `/fast/scratch/hyaku/souji-r44/S44mutationtester49`, each phase ran:

```text
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44mutationtester49/run_probe.py pristine
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44mutationtester49/run_probe.py mutated
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44mutationtester49/run_probe.py restored
```

The preserved runner imports unchanged frozen modules, invokes audit `main(['--tool', scratch+'/tool.py', '--work', scratch+'/fixtures-'+phase])`, captures its returned CLI exit and output, and applies frozen counter `audit_verdict` and its stub predicate. Each tool invocation inside the audit is an actual `python3 -B` subprocess. Runner exit is 0 for all three phases; that is distinct from the audit exit below. Before every fixture git add/commit a guard asserts its git top-level equals the fixture path; all fixture git targets are restricted to this seat's scratch.

| Phase | Audit exit | Exact summary | Counter parsed | Stub rejected |
|---|---:|---|---|---|
| Pristine | 0 | `SUMMARY scenarios=10 pass=10 fail=0` | `(10,0,10)` | false |
| Mutated | 1 | `SUMMARY scenarios=10 pass=2 fail=8` | `(2,8,10)` | true |
| Restored | 0 | `SUMMARY scenarios=10 pass=10 fail=0` | `(10,0,10)` | false |

Mutation passes h1 and h8, fails h2–h7, h9 and h10. Failed non-refusal cases report `got rc=0 classes=-`. All three captured audit stderr streams are empty. Full outputs: `pristine.txt`, `mutated.txt`, `restored.txt`.

A separate direct control invocation, recorded verbatim in `direct-control.json`, returned exit 0, stdout `SUMMARY claims=1 findings=0\n`, stderr empty. Therefore rejection is behavioral detection, not a broken control process.

## Byte restoration and cleanup

SHA-256:

| Input | Before and restored |
|---|---|
| Tool | `f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999` |
| Counter | `0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252` |
| Audit | `50872b0da7a36d377ced9cf0e51579ef00f0f0ae402eebad8c579fce6e5e843e` |

Mutant tool SHA-256: `24d8f6df9b71e560ed211ffd1b4aa6b445ee26e6fd0973ef68594cbb57680e5e`. Exact restored tool bytes equal the extracted original, not just its digest (`hashes.json`). Restoration occurred in a finally block. Assigned scratch was removed; `cleanup.json` records exists_after_cleanup=false. No installations, production writes, shared bookkeeping, or git/index changes outside fixtures.

## Limitations

This is one bounded always-clean control probe, not whole-counter certification: counter `main`, retention, selftest, TMPDIR and always-findings legs were not run. The audit was invoked through its unchanged `main` under a fixture-location guard, not through its standalone CLI. No score delta or admission conclusion is claimed. Report stays inside the explicitly owned seat directory; the conflicting flat trailer path was not written.

## Self-evaluation

Accuracy 4/5: raw receipts separate runner exit from audit return; standalone audit process exit was not exercised. Completeness 4/5: assigned always-clean probe is complete; full counter is intentionally outside this bounded run. Clarity 4/5: table summarizes outputs; exact full traces are separate files. Actionability 4/5: runner and candidate retained; frozen extraction must be repeated after required scratch cleanup. Conciseness 4/5: detailed command/restoration evidence adds length. Overall 4.0/5. Improvement priorities: use the receipts for this control only; do not infer full counter acceptance. Self-check: this scope and these limitations should match the requested mutation evidence.
