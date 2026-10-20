STATUS: DONE — R18-M5 history and recorded-run impact traced

# R18-M5 — landing-gate early-error totality

Axes: commit provenance; claimed exit contract; recorded-run impact.

## Finding and evidence chain

**The defect-causing commit is `4f4834390ad4845b76804e94cc04d8f867ef9b54` (Round 17 wave 2).** Precisely, it did not first add the `checked_measured` output field: its diff retains the field in `emit()` while deleting the default from `evaluate()`'s result initializer. The later `3f822e85c6a5f866c4003be0ad039d5583d14364` Round 18 build restores the default. The `git log -S` result, newest first:

```text
3f822e8 round-18: build — C1 bounded census + fixture session kill, C2 LG-DANGLING-PTR, C3 proc census, R1 recipe owner, R2 pointer repairs; wave-1 evidence
4f48343 round-17: wave-2 fixes — census empty/locale/dot-admin + both soft diagnostics, jj_keep_novel leaf-blob/SIGPIPE-safe/fail-closed, gate exit-2 totality + mutant killers, seat-audit survivors, fixtures R17-27..29 and J10..J12
ddb7347 round-17: C1 census D1/D2, C2 seat-audit precision + r16 transcripts bundle, C3 jj-aware receipt roots/novelty, D6 gate exact ids + replays, vadv54 stub, regenerate verdict
```

The decisive `4f48343` diff hunks are:
Command producing the diff excerpt:

```text
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --format= --unified=0 4f48343 -- tools/souji-landing-gate.py
```

```diff
@@ -597,0 +615 @@ def evaluate(root, rev, round_no, base=None):
+        "checked_changed": 0,
@@ -601 +618,0 @@ def evaluate(root, rev, round_no, base=None):
-        "checked_measured": 0,
@@ -682 +711 @@ def emit(result, json_out=None):
-        "SUMMARY\tfindings=%d\tchecked_reg=%d\tchecked_pins=%d\tchecked_measured=%d ..."
+        "SUMMARY\tfindings=%d\tchecked_reg=%d\tchecked_changed=%d\tchecked_pins=%d\tchecked_measured=%d ..."
```

This changed an initialized counter into a counter that was only populated on the success path. On an unknown `--rev`, `resolve_commit()` raises `EvalError` before the measured-pin assignment (`tools/souji-landing-gate.py:908-918`, `:962-968`). `evaluate()` catches that and returns exit 2 (`:1024-1029`), but the old result lacks `checked_measured`; `emit()` unconditionally indexes it while constructing SUMMARY (`:1037-1049`). `main()` calls `emit()` after its `evaluate()` exception handler (`:1963-1985`), so the `KeyError` escaped as a traceback and process exit 1 instead of the promised exit 2.

The regression is present at the Round 18 baseline: ancestry checks returned success for `4f48343` ancestor of `d98065d`, `d98065d` ancestor of `b576341`, and `b576341` ancestor of `3f822e8`. The repair is in `3f822e8`: it adds the missing default at `evaluate()` initialization (current `tools/souji-landing-gate.py:896-900`). The same commit adds explicit unknown-revision and malformed-exemption CLI cases at `:1389-1414`; these cases were inspected, not executed here. Round 18 documentation then records the correction at `SKILL.md:165`.

## Which SKILL claims were false

- **Round 17:** false. The `d98065d` SKILL landing-gate row (`SKILL.md:165` in the current file) states “2 could-not-evaluate and total” and includes unknown revision. `4f48343` precedes that row and had removed the default; therefore the row overstated behavior for the Round 17 gate.
- **Round 18 pre-fix baseline (`b576341`):** the same inherited totality guarantee was still false. The defect remained in the baseline, until `3f822e8` restored the default.
- **Round 16:** not affected. Its earlier SKILL row, introduced in `163158a`, stated exit 2 for unknown revision before the `4f48343` removal; the parent state still had the default that `4f48343` deleted.
- **Round 18 final correction:** not a false claim. `42d9ff3` updates the row after the code repair, explicitly records that `b576341` crashed with exit 1, and claims total behavior for the corrected gate.

Thus the false *historical claim* originated in Round 17 and was false when carried into the pre-fix Round 18 baseline; the final Round 18 statement describes the repaired state.

## Recorded gate runs

**No reviewed recorded gate invocation was affected by this specific early-error bug.** The tracked gate-record paths were enumerated with `git ls-files 'census/round-*/gate*' 'census/round-*/landing*' 'tests/results/*landing*'`. Their recorded inputs were resolvable revisions:
Enumeration command output:

```text
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files 'census/round-*/gate*' 'census/round-*/landing*' 'tests/results/*landing*'
census/round-16/gate-landing.json
census/round-17/gate-landing.json
census/round-17/gate-replays-4f48343.json
census/round-17/gate-replays-expected.json
census/round-17/gate-replays.py
census/round-18/gate-pointers-before-b576341.json
census/round-18/gate-replays-r18.json
census/round-8/gate-runbook-17.md
census/round-8/gate-runbook-18.md
census/round-8/gate-runbook.md
```


- `census/round-16/gate-landing.json:3-6`: exit 0 at resolved `6ff91f5…`.
- `census/round-17/gate-landing.json:3-6,8-16`: exit 0 at resolved `d98065d…`; `checked_measured=3` shows the normal measured-pin path populated the field.
- `census/round-17/gate-replays-4f48343.json:7-15`: the tested gate is exactly `4f48343`, top-level `match=true`; its replay set uses the pinned, resolvable revisions `a31642d`, `cc21683`, `b410186`, `6ff91f5`, and `79bbe7a`. Its `selftest` is `null`, so this record does not cover the early unknown-revision path.
- `census/round-18/gate-pointers-before-b576341.json:2-3,51-54,77-90`: the valid `b576341…` revision returns exit 2 for the late “no .md reports under” carry error, but its summary still has `checked_measured=3`; this is not the early `resolve_commit()` failure.
- `census/round-18/gate-replays-r18.json:7-15`: the post-fix worktree gate replay matches; the five replay target revisions are the same resolvable set above.

Therefore the records establish no affected recorded output, not that the defect was absent: none records an unknown-revision invocation under the buggy gate. The Round 17 replay is particularly informative because it exercised the buggy gate on valid revisions but left `selftest` null.

## Commands and observations

```text
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -S checked_measured --oneline -- tools/souji-landing-gate.py
3f822e8 round-18: build — C1 bounded census + fixture session kill, C2 LG-DANGLING-PTR, C3 proc census, R1 recipe owner, R2 pointer repairs; wave-1 evidence
4f48343 round-17: wave-2 fixes — census empty/locale/dot-admin + both soft diagnostics, jj_keep_novel leaf-blob/SIGPIPE-safe/fail-closed, gate exit-2 totality + mutant killers, seat-audit survivors, fixtures R17-27..29 and J10..J12
ddb7347 round-17: C1 census D1/D2, C2 seat-audit precision + r16 transcripts bundle, C3 jj-aware receipt roots/novelty, D6 gate exact ids + replays, vadv54 stub, regenerate verdict

$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor 4f48343 d98065d && printf '4f-before-d980=%s\n' "$?"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor d98065d b576341 && printf 'd980-before-b576=%s\n' "$?"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor b576341 3f822e8 && printf 'b576-before-3f=%s\n' "$?"
4f-before-d980=0
d980-before-b576=0
b576-before-3f=0
```

No gate, fixture, selftest, build, or other runtime was run for this investigation.

## Verdict and smallest fix

**Verdict: the Round 17 totality claim fails for unknown revisions; it also fails at the pre-fix Round 18 baseline. No inspected recorded run is shown affected.** The smallest fix is the missing `"checked_measured": 0` default in `evaluate()`; it is already present in the Round 18 build at `3f822e8`. The explicit CLI unknown-revision case is present in that build, but execution was out of scope here.