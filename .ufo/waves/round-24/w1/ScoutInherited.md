# ScoutInherited — inherited lane state at round-24 start

## Status
STATUS: PASS — both inherited round-23 edits are classified, the watchdog was checked (no `lane-dead-no-report souji round=24` line), and the new W2K1 F4 claim was reproduced on the committed tool.

## Evidence
All read-only against lane HEAD `f9db2181647d91470a724a12d626bd6106805076`. Watchdog times are -0300.

1. `git status --porcelain` shows a second inherited edit that the assignment did not name:
   ` M .ufo/waves/round-23/w2/W2D3.md`, ` M .ufo/waves/round-23/w2/W2K1.md`, plus round-24 untracked files and `?? census/operator-sweep-20261019/`. The census directory is operator-owned: not read, not staged.
2. `git diff --no-ext-diff --stat`: W2K1.md has +88/−131 (the whole body rewritten). W2D3.md has +12/−1 (a new section A6, appended).
3. File mtimes (`stat`): W2K1.md `06:08:37`, W2D3.md `06:09:40`. Timeline:
   - Last commit touching either file: `2f96bf4` at 06:03:53.
   - Round-23 `complete`: watchdog.log:1289, `2026-10-25T06:04:05-03:00 complete souji round=23; hyaku-inline attempt=1`.
   - `a65fac9` committed at 06:06:38.
   - Round-24 launch: watchdog.log:1296, at 06:08:06.
   - Preregistration commit `f9db218` at 06:14:49.

   Both edits were made after round 23 completed and before the preregistration was frozen.
4. Watchdog check: grep for `souji` in /home/vgpnk/Projects/shokunin/.ufo/watchdog.log. For round 24 the only line is 1296, `launch souji round=24 pgid=1754039 driver=hyaku-inline attempt=1`. There is **no** `lane-dead-no-report souji round=24` line.
5. Tool digests (`git show <rev>:tools/souji-record-agreement.py | sha256sum`):
   - `466f539`: `59d687a3…`
   - `c872eec`, `eb1aa49`, `2f96bf4`, `a65fac9`: `dd53c228b8cca68cfe6dd51630c4ed3473a7c20db36a0effcf5a18259049bb0f`

   `2f96bf4:census/round-23/records/agreement-after.tsv` contains `rev=eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a` and `tool_sha256=dd53c228…`. This matches the new W2K1 header exactly.
6. Reproduction in scratch `/var/tmp/souji-r24-ScoutInherited/` (a `--no-local` clone detached at `a65fac9`, using the committed tool `dd53c228`; scratch has been removed):
   - Baseline: `keys=4 records=4 occurrences=17 mismatches=0` rc=0.
   - M-a: the receipt stdout is changed to `mismatches=7`, and `assertions=63 resolved=63 skipped=40 mismatches=0` is appended after `--- stderr ---` (scratch commit `b628e97b`). Result: `mismatches=0` rc=0. **False green.**
   - M-b (control): the same stdout change to `mismatches=7` with no trailing line. Result: two `value-disagree` mismatches, `mismatches=2`, rc=1.

## Findings
1. **W2K1.md is a genuine late update by the seat, with real content changes, not a stray edit.** The seat line is unchanged ("Seat: L1Souji23.W2K1. Scope: C1, key K1 only."). The new header names the later tips `c872eec → eb1aa49` and the closing commit `2f96bf4`. The F1–F6 findings were re-verified against the hardened tool, using new scratch revisions such as `0a5c2cd3` and `9068ffbf`.
   - F1 and F3 are marked "closed by c872eec".
   - F2 is kept.
   - F4 is redefined: old version "first `assertions=` match *anywhere*"; new version "last-match parsing accepts a trailing shadow after stdout".
   - The facts I could check all hold: the digest and receipt rev (Evidence 5); `counts_of` uses `matches[-1]` (c872eec, lines 121-125); the `unbound-tuple` and `receipt-rev-object` guards exist (tool lines 171 and 201; fixture line 281). The scratch revisions it cites were removed by the seat and cannot be checked.
2. **W2D3.md is the same kind of late update.** Its new section A6 replays the mutants "at `eb1aa49` (tip `a65fac9`)" and says M3c "is the same class as W2K1's open F2 (`0a5c2cd3`…)". So W2D3's uncommitted text cites W2K1's **new** text.
3. **Committed round-23 bytes cite only the old W2K1 text, and one statement is now contradicted.**
   - `corpus/lessons/round-23.md:144-147` says the parser was "switched counts parsing to last-wins so a pre-fence summary line cannot shadow the measured output. All three holes now have fixture cases".
   - The new W2K1 F4, and my reproduction (Evidence 6, M-a), show that last-wins lets a trailing post-stderr line shadow the real stdout and produce a false green.
   - Tool docstring `tools/souji-record-agreement.py:117-119` says "Only the header region before the `--- stdout ---` fence is a receipt's own claim". However, `STDOUT_FENCE` (line 70) is defined and never referenced.
   - [INFERENCE] The lesson's "all three holes now have fixture cases" is also inaccurate. `tests/fixtures/r23-record-agreement.py` has 12 `variant ==` arms; one is `unbound-tuple`, and none is a receipt-rev-object or shadow/fence case.
   - The comments at `tools/souji-record-agreement.py:199` ("W2K1 F1 moves the rev off-line") and `tests/fixtures/r23-record-agreement.py:282` cite F1. They are consistent with both versions.
   - No committed file cites any scratch hash from either version (`git grep` over HEAD for the old hashes and the new hashes: no hits).
   - `corpus/lessons/round-23.md:197` lists W2K1 as "wave-2 verdict: mixed". That still fits the new verdict.
4. **Is W2K1 still running? Unresolved.** A live /proc census is out of bounds, and the visible roster does not list `L1Souji23.W2K1`; 89 live peers are not shown. The last write was at 06:08:37 and nothing has changed since. `swarm-registry.json` at HEAD has `"agentId": null` for W2K1. [INFERENCE] The seat most likely finished just after round-23's `complete` line and its final write was never collected.
5. **Recommendation: leave both files for their authors and the L1. Do not commit them as round-24 inherited state.** Reasons:
   - Both are round-23 seat reports written after round 23 completed. Committing them under round 24 would silently rewrite a round-23 record after its lesson was published (`corpus/lessons/round-23.md` cites the old text), and the lane would carry two versions with no supersession note.
   - The author may still be running. A round-24 seat may not stage or commit them.
   - The material fact they contain does not depend on committing them: the F4 trailing-shadow false green is confirmed independently (Evidence 6). Round 24 should record it in its own bytes, citing this report, as a residual disclosure. That is not a counter change to K1 or C3.
   - If the L1 integrates them anyway, do it as one separate commit labelled "round-23 late seat updates (W2K1, W2D3), written 06:08–06:09 after round-23 complete". Do not fold them into a claim commit.
6. **Relevance to round-24 claims [INFERENCE].** The trailing-shadow class is a counts-line-parsing issue in K1, which belongs to round 23. Round-24 C3 (`souji-receipt-run.py verify`) is a different tool, but any C3 fixture that parses receipt stdout should anchor parsing between `--- stdout ---` and `--- stderr ---`, or it inherits this hole.

## Tooling
None installed or updated. Used git 2.56.0 and python3, both already on the host.
