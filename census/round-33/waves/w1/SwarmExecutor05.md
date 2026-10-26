# SwarmExecutor05 — C1 K05 restatement

STATUS: PASS — K05 does not reproduce at base; its one honest restatement row was drafted, its cause commit
(`ddb7347`) was found and executed independently, and the counter prints `ITEM K05 AGREE` / `mismatches=0` on the
exact canonical block delivered. The change is GROWTH (18 -> 28 -> 65 selftest cases, all passing); no capability lost.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `6017a482e7068d5afb7617640198fbb0fe743357`, list-rev
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. Scratch clone `/fast/scratch/hyaku/souji-r33/RestateK05/c`
(`git clone -q --no-local`, origin removed at once, toplevel verified, detached at the list-rev). `TMPDIR` always
`/fast/scratch/hyaku/souji-r33/RestateK05/tmp`, a fresh subdir per run. Python 3.14.8, git 2.56.0, no installs.

1. Frozen argv at the list-rev, 3 runs, fresh TMPDIR each:
   `cd $D/c && TMPDIR=$D/tmp-run<N> GIT_CONFIG_NOSYSTEM=1 python3 tools/souji-landing-gate.py --selftest`
   -> `rc=0` three times, stderr empty, outputs byte-identical
   (`sha256sum` = `088846868fb5d85ede739ca1c075da6a5723e05556268a260169b195828abd0c`); last line
   `SELFTEST	pass=65	fail=0`; 65 `CASE` lines, `grep -c 'CASE	FAIL'` = 0.
   Frozen predicate `\b18/18\b || \bpass=18\b && \bfail=0\b`: `18/18` absent, `pass=18` absent, `fail=0` present
   -> predicate fails, exit still 0. The row does not reproduce.

2. History walk (independent, not copied from `records/feasibility.txt`):
   `git -C $D/c log --reverse --format=%H -- tools/souji-landing-gate.py` = 11 commits; the frozen argv run at each
   with a fresh TMPDIR gives summary lines 18, 18, **28**, 33, 53, 53, 61, 65, 65, 65, 65 with rc 0 throughout.
   First failure `ddb73474433977ff54b015ac3e77669ff2537353`:
   holds at its first parent `5fa6017ddcae9f6bd4412df44765f6360cb16294` (`SELFTEST pass=18 fail=0`), fails at the
   cause (`SELFTEST pass=28 fail=0`); `git show --name-only --format= ddb7347` names
   `tools/souji-landing-gate.py`; `git merge-base --is-ancestor ddb7347 2d9bca55` -> true. Diffstat
   `1 file changed, 323 insertions(+), 88 deletions(-)`.

3. Proof of the row at the canonical block (scratch commit `12cdd87b84e94d2863c6c64dd43dd923535faf56`,
   SCORECARD.md +8 lines, throwaway identity, never pushed):
   `python3 -B census/round-33/c1-counter.py --root $D/c --rev 12cdd87b… --list-rev 2d9bca55… --scratch $D/cnt3 --only K05`
   ```
   ITEM	K05	AGREE	restated	rc=0 expect_exit=0 statement is an output line last=SELFTEST pass=65 fail=0
   SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=12cdd87b84e94d2863c6c64dd43dd923535faf56
   counter rc=0
   ```
   Same row, suffixed heading, scratch commit `194a939342d931388d88ad4f1676ba95f7ac5936`, two runs: identical
   `AGREE` line, `mismatches=0`, rc=0.

4. Falsifiers: do-nothing (`--rev 2d9bca55`, no row) -> `ITEM K05 MISMATCH original … predicate fails`,
   `mismatches=1`, rc=1 (row necessary). Non-causal cause (`4f4834390ad4`, a later gate commit where the outcome
   already failed at its parent) -> `BAD-CAUSE(original at parent=False at cause=False; need True/False)`, rc=1
   (cause field load-bearing; my cause is the first break).

5. Growth accounting: parent `5fa6017` 18 case names; cause `ddb7347` 28 (11 added, 1 removed); list-rev 65 names,
   17 of the 18 parent-era names present, 0 `CASE FAIL`.

## Findings

1. **K05 does not reproduce.** `SCORECARD.md:158` states the gate selftest as `18/18`; at
   `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` the same argv prints `SELFTEST	pass=65	fail=0` and exits 0.
   Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md:158`, frozen argv
   `python3 tools/souji-landing-gate.py --selftest`.

2. **The first break is `ddb73474433977ff54b015ac3e77669ff2537353`** (round-17 "D6 gate exact ids + replays"),
   which grew the selftest 18 -> 28. Holds at its first parent `5fa6017d…`, fails at the cause, cause touches
   `tools/souji-landing-gate.py`, cause is an ancestor of the list-rev. Location:
   `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py` (subject line of that commit).

3. **The 18 -> 28 step is not a pure addition:** the cause also renames case `fenced-and-table-ignored` to
   `benign-status-words`, keeping the three fixture literals byte-identical and strengthening the assertion with
   `expect_counts={"status_lines": 2}` at exit 0. Rename, not a lost capability. Location: same tool, the
   `# CASE benign-status-words` block at `2d9bca55` (and the removed `check("fenced-and-table-ignored", repo, 0, …)`
   at `5fa6017`).

4. **Further growth after the cause, all passing:** 28 -> 33 (`4f4834`), 53 (`3f822e85`), 61 (`4800fd79`),
   65 (`005f3d37`); `68447afe`, `8024b540`, `98e5203d` leave the count at 65. At the list-rev every one of the 65
   cases prints `CASE pass`. Location: `tools/souji-landing-gate.py` at those revisions.

5. **The row's stated form never matched the tool's output form:** from the tool's first commit `7a79dc2` the
   summary line is `SELFTEST	pass=N	fail=0`; `18/18` was never printed. The frozen predicate accepted either
   spelling, so the currency defect is the count only, and the restatement quotes the real line. Location:
   `SCORECARD.md:158` versus `tools/souji-landing-gate.py` selftest summary emitter.

6. **Integration constraints for the resting row:** the statement binds to the count at the landing revision
   (`pass=65 fail=0` at `2d9bca55`), and the counter only reads rows under a heading line that starts with
   `### Round 33 capability currency` (`load_restatements` uses `startswith`). `SCORECARD.md` is byte-identical at
   base `6017a48` and list-rev `2d9bca55` (`cmp` clean, 494 lines), so line 158 is the same row at both. Location:
   `census/round-33/c1-counter.py`, `load_restatements`.

## Attack log

No attack. My item is a restatement, and the frozen predicate, target, counter and item table are unchanged by me.
Two probe results are recorded because they are the plausible gaming routes and both are closed by the frozen
counter: a later real gate commit as the cause is rejected (`BAD-CAUSE`, `4f4834`), and an empty section is rejected
(`MISMATCH`, do-nothing at the list-rev). No amendment proposed.

## Deliveries

- `.ufo/waves/round-33/w1/deliver-c1-K05.md` — the row (verbatim, `ROW-BEGIN`/`ROW-END`), the canonical appended
  block as proved, all receipts (three runs with every digit-bearing line, history table, cause verification, counter
  and falsifier outputs), the growth/regression call, and L1 notes.
- `.ufo/waves/round-33/w1/SwarmExecutor05.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r33/RestateK05` (203 MB) removed after the receipts were copied. No lane file was
written; no commit, re-pin, or index operation in the lane; nothing outside `/home/vgpnk/Projects/shokunin/souji-shokunin/`
and my scratch dir was touched.
