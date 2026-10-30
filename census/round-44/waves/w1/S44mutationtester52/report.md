# S44mutationtester52 — C2 scenario multiplicity

Axes: calibration / operability / coverage. Assigned axis: operability.
Frozen revision: `d314fd6e85d62565344fa6c4b102f52f62297884`.

## Result: KILLED, not a crash

One plausible defect at freeze-check line 197: replace `sorted(dups)` with `sorted(set(dups))`. This accidentally treats duplicate keys as unique offending key names, losing repeated occurrences. No counter or audit bytes were mutated. The expected detector was hidden-audit h6, which requires two `C1:KEY-DUPLICATE` findings for three Base occurrences.

| Tool bytes | Audit exit | Exact summary | Counter audit_verdict |
|---|---:|---|---|
| pristine | 0 | `SUMMARY scenarios=10 pass=10 fail=0` | `(10, 0, 10)` |
| mutated | 1 | `SUMMARY scenarios=10 pass=9 fail=1` | `(9, 1, 10)` |
| restored | 0 | `SUMMARY scenarios=10 pass=10 fail=0` | `(10, 0, 10)` |

Mutant diagnostic:
```
scenario-h6-duplicate-three-occurrences=FAIL
#   got rc=1 classes=C0:FROZEN-EDITED,C1:KEY-DUPLICATE
```
All nine other scenarios passed. All three stderr captures were empty. The mutant produced a normal findings exit (1) and a complete audit summary; this was behavioral detection, not a crash. Frozen counter lines 150–151 would classify the observed mutant verdict as `hidden_v2=RED` because fail is nonzero; that field consequence is inferred from source, not an executed full counter run.

## Exact bounded commands and evidence

Read-only extraction for each source:
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:tools/souji-freeze-check.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:census/round-44/c2-hidden-audit.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:census/round-44/c2-counter.py
```
The extraction driver wrote stdout bytes to owned scratch. With cwd `/fast/scratch/hyaku/souji-r44/S44mutationtester52`, the same detector command was run for each phase:
```
/usr/bin/python -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44mutationtester52/run-audit.py pristine-work
/usr/bin/python -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44mutationtester52/run-audit.py mutated-work
/usr/bin/python -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44mutationtester52/run-audit.py restored-work
```
The runner imports unchanged frozen audit bytes and invokes its main with the owned tool/work paths. It guards fixture git add/commit operations with `git rev-parse --show-toplevel` equality assertions and confines fixture git calls to owned scratch. Parent invocation timeout: 180 seconds each. Each audit tool call retains its frozen 300-second bound. Actual full outputs: `pristine.stdout.txt`, `mutated.stdout.txt`, `restored.stdout.txt`; corresponding `.stderr.txt` files are empty. Commands, exits and parser results: `receipts.json`. Preserved source snapshots: `frozen-tool.py`, `frozen-audit.py`, `frozen-counter.py`; one-line patch: `mutation.diff`.

## Hashes and restoration

SHA256:
- Pristine/restored tool: `f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999`
- Mutated tool: `e8e76686f4b2786941e128c93833af125f68c0b0c75ea28f89f4919ba85ee303`
- Unchanged audit: `50872b0da7a36d377ced9cf0e51579ef00f0f0ae402eebad8c579fce6e5e843e`
- Unchanged counter: `0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252`

A finally block restored exact original tool bytes before the restoration audit. `restoration.json` records exact-byte equality and scratch deletion (`scratch_removed=true`). Production, sibling files and shared git state were not modified. Fixture repos existed only in owned scratch, now deleted. No tools installed or updated.

## Limits

This single mutation establishes discrimination for duplicate-key occurrence multiplicity in h6. It does not establish arbitrary scenario, missing-field or summary-forgery discrimination. Only the bounded hidden audit and frozen counter's `audit_verdict` parser ran; the complete C2 counter, retention, selftest and stub legs did not run. No score change or admission/closure claim is made.

Self-evaluation: accuracy 4 (full counter consequence is source inference, labeled above); completeness 4 (one assigned defect, not general multiplicity proof); clarity 4 (raw scenario detail lives in receipts); actionability 4 (runner needs preserved snapshots copied back into named scratch); conciseness 4 (explicit commands repeat long paths). Overall 4.0. Main can use the existing receipts without rerunning unrelated checks. User agreement expected because the observed kill and limits are separated.
