STATUS: PARTIAL — all five pinned replays match under the runner’s semantic comparison, but literal byte-stability is not established.

# Attacked claim

C2 calibration — historical round-17 landing-gate verdicts remain stable at wave-1 tip `5efb519f00075d958c3d1109ef6fcb24c487eb87`.

# Findings

## Semantic replay check holds; byte-stability is narrower than the claim suggests

Ran at the required detached `5efb519` clone:

```text
$ python3 census/round-17/gate-replays.py --output /var/tmp/souji-r18w2-RerunGateReplays/r.json
name             rev      round  exit  findings  match
r15-landing      b410186  15     1     5         True
r13-admitted     a31642d  13     0     0         True
r14-landing      cc21683  14     0     0         True
r16-landing      6ff91f5  16     0     0         True
r16-precarry     79bbe7a  16     1     29        True
gate             rev=WORKTREE sha256=f8a2ebe7695e6009 expected_sha_match=False
gate-replays: wrote record to /var/tmp/souji-r18w2-RerunGateReplays/r.json
RC=0
```

The fixture also passed:

```text
$ python3 tests/fixtures/r16-landing-gate.py --tool tools/souji-landing-gate.py
...
SUMMARY total=15 failed=0
RC=0
```

The `match=True` result is specifically an exit-code plus `(finding id, path)` multiset comparison, not a byte comparison: `census/round-17/gate-replays.py:20-22,299-320`. The runner also retains raw stdout (`:127-149`). In the r15 replay, the `LG-PARSE-REG` diagnostic contains the generated scratch directory: the fresh record has `/var/tmp/souji-landing-gate-646769v_...` (`/var/tmp/souji-r18w2-RerunGateReplays/r.json:108`), whereas the committed record contains `/var/tmp/souji-landing-gate-r8if9ebp...` (`census/round-18/gate-replays-r18.json:108`). Thus the emitted diagnostic bytes differ despite the replay being counted as a match. The complete JSON records also differ: fresh SHA-256 `0279a0955a6337a0ca426ebd98a9d97ca9c07ab1a229cd04207e042dd0fe815f`; committed record SHA-256 `6adf3028acced8d4fc056dc9b94e2e720f4668ada4dd22f364954e530ca74933`. The record metadata itself is not expected to be byte-identical across runs/clones (the committed record’s `lane_head` is `42d9ff3930933cada8ba7e028d97b69a6889fc15`, while this replay was run at `5efb519`).

`expected_sha_match=False` is also reported by the replay runner: the current gate SHA is `f8a2ebe7…`, while the frozen expected-gate SHA is `e7d2439d…` (`census/round-18/gate-replays-r18.json:2-14`). This does not make any of the five verdict comparisons fail; it means the replayed gate bytes differ from the historical expected-gate bytes.

# Exact verification commands and outputs

```text
python3 census/round-17/gate-replays.py --output /var/tmp/souji-r18w2-RerunGateReplays/r.json
# Exit 0; five rows above all have match=True; expected_sha_match=False.

python3 tests/fixtures/r16-landing-gate.py --tool tools/souji-landing-gate.py
# SUMMARY total=15 failed=0; exit 0.

sha256sum r.json recorded-r18.json
# 0279a0955a6337a0ca426ebd98a9d97ca9c07ab1a229cd04207e042dd0fe815f  r.json
# 6adf3028acced8d4fc056dc9b94e2e720f4668ada4dd22f364954e530ca74933  recorded-r18.json
cmp r.json recorded-r18.json
# Nonzero: files differ (first reported at char 152, line 5).
```

# Verdict and smallest fix

**PARTIAL.** The declared five-replay semantic criterion holds, and the r16 fixture passes. A literal “byte-stable” claim does not: randomized scratch paths leak into replay diagnostics, and the comparator intentionally ignores diagnostic text, ordering, and summary/stdout bytes. Smallest fix: scope the claim to “exit code and `(id, path)` multiset match.” If byte stability is required, normalize temporary paths in emitted diagnostics and make the replay assertion compare the complete normalized verdict payload.

No tools installed or updated.