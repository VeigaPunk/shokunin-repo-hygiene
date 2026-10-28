# R41w2reviewer03: independent re-measure of C3 and R1 (reviewer, coverage)

Seat: R41w2reviewer03 (leaf, read-only). Lane tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f. uid 1000 (not root). No tool installed or upgraded. No git mutation, no lane write.

## Verdict

- **C3 (coverage, 19 sites / 21 probes): REPRODUCED.** The committed counter at a1144120611b00091ac4839559d8ebf38aa9a83a and at the tip gives a SUMMARY identical to `records/c3-after.txt`. Line-by-line reading and a raise-site trace agree: all 21 probes reach the site `c3-sites.tsv` maps them to, and each asserts `rc == 2` and `REFUSAL <CLASS>:`.
- **R1 (record order / root repo, 11 mutants): REPRODUCED** at 97eeb01e73a9baa3e4191b9052fed9e505c70215 and at the tip; SUMMARY identical to `records/r1-after.txt`.
- **Gap found (counter, not the landed fixture):** `c3-counter.py` does not test the fixture's exit-2 assertion. A fixture with that check removed still scores `killed=19`. The landed fixture does assert exit 2 (line 78), so the landed verdict stands, but the counter's kill result does not prove the exit-2 half. This was verified only by reading and by the trace below.

## Commands run and output

Revisions and blobs (`git rev-parse`, read-only): lane tip `1d41c13` = HEAD; `a1144120…:tests/fixtures/r41-refusal-sites.py` = `85f3aca…` = tip blob; `97eeb01…:tests/fixtures/r41-drift-record-order.py` = `ccfb424…` = tip blob; `census/round-41/c3-sites.tsv` sha256 `be363c0d…` (pinned value matches); `tools/souji-worktree-drift.py` sha256 `b2a603cf…` (pinned value matches). `git status --short` in the lane: empty.

Counter runs (scratch `/fast/scratch/hyaku/souji-r41/R41w2reviewer03`, removed afterwards):

```
$ python3 -B census/round-41/c3-counter.py --root <lane> --rev a1144120611b00091ac4839559d8ebf38aa9a83a --scratch <S>
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01 RECORD-MALFORMED killed failing=P01 mapped=P01 rc=1
... (S02–S19 all "killed", failing == mapped, rc=1) ...
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2
EXIT=0

$ ... c3-counter.py --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f ...
(identical 19 SITE lines and SUMMARY, fixture_sha=f32022e28fe2)   EXIT=0

$ python3 -B census/round-41/r1-counter.py --root <lane> --rev 97eeb01e73a9baa3e4191b9052fed9e505c70215 --scratch <S>
MUTANT M11 ... killed=yes ... M21 owner=r41-drift-record-order.py killed=yes ...
SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106
EXIT=0

$ ... r1-counter.py --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f ...
(identical 11 MUTANT lines and SUMMARY)   EXIT=0
```

Diff against records: the c3 and r1 SUMMARY and per-site lines match `records/c3-after.txt` and `records/r1-after.txt` exactly.

Fixture run, pristine tool (`git show 1d41c13:tools/souji-worktree-drift.py`, sha `b2a603cf…`) and fixture bytes from `a1144120` (sha `f32022e2…`):

```
probe-P01=PASS rc=2 ... probe-P19=PASS rc=2   (21 lines, all PASS)
SUMMARY probes=21 pass=21 fail=0
EXIT=0
```

Raise-site trace. A logging wrapper (`importlib` loads the pristine tool, patches `Refusal.__init__` to log `f_lineno`, then calls `main`) was run as the fixture's `--tool`. The wrapper logged 20 invocations. The 21st, P19, is written by `main()` directly (line 448), so it is not logged. The log, in probe order, with the `tools/souji-worktree-drift.py` line that raised:

| probe | raise line | site (c3-sites.tsv) | class asserted by fixture | class in log |
|---|---|---|---|---|
| P01 | 136 | S01 | RECORD-MALFORMED | RECORD-MALFORMED |
| P02a | 137 | S02 | RECORD-MISSING | RECORD-MISSING |
| P02b | 137 | S02 | RECORD-MISSING | RECORD-MISSING |
| P03 | 140 | S03 | RECORD-MALFORMED | RECORD-MALFORMED |
| P04 | 161 | S04 | RECORD-MALFORMED | RECORD-MALFORMED |
| P05 | 173 | S05 | RECORD-MALFORMED | RECORD-MALFORMED |
| P06 | 175 | S06 | RECORD-EMPTY | RECORD-EMPTY |
| P07 | 178 | S07 | RECORD-MALFORMED | RECORD-MALFORMED |
| P08 | 180 | S08 | RECORD-MALFORMED | RECORD-MALFORMED |
| P09 | 182 | S09 | RECORD-MALFORMED | RECORD-MALFORMED |
| P10a (FIFO) | 271 | S10 | JSON-NOT-REGULAR | JSON-NOT-REGULAR |
| P10b (dir) | 271 | S10 | JSON-NOT-REGULAR | JSON-NOT-REGULAR |
| P11 (/dev/null) | 276 | S11 | JSON-NOT-REGULAR | JSON-NOT-REGULAR |
| P12 | 286 | S12 | USAGE | USAGE |
| P13 | 300 | S13 | RECORD-OUTSIDE-ROOT | RECORD-OUTSIDE-ROOT |
| P14 | 317 | S14 | RECORD-OUTSIDE-ROOT | RECORD-OUTSIDE-ROOT |
| P15 | 341 | S15 | JSON-IS-RECORD | JSON-IS-RECORD |
| P16 | 348 | S16 | JSON-INSIDE-MEASURED-TREE | JSON-INSIDE-MEASURED-TREE |
| P17 | 425 | S17 | JSON-HARDLINKED | JSON-HARDLINKED |
| P18 | 435 | S18 | JSON-UNWRITABLE | JSON-UNWRITABLE |
| P19 | 448 | S19 | USAGE | (direct run below) |

Full log: `.ufo/waves/round-41/w2/R41w2reviewer03/c3-sitelog-tip-trace.tsv` (sha256 `567715ec…`).

P19 direct run: `python3 -B tools/souji-worktree-drift.py --root <S>/p19/root --record <S>/p19/root/none --timeout 0` prints `REFUSAL USAGE: --timeout must be >= 1` and exits 2.

Exhaustiveness: `grep -n 'Refusal\|REFUSAL' tools/souji-worktree-drift.py` shows 18 `raise Refusal("<CLASS>: …` lines (136, 137, 140, 161, 173, 175, 178, 180, 182, 271, 276, 286, 300, 317, 341, 348, 425, 435) plus the `REFUSAL USAGE` write at 448. That is 19, matching `c3-sites.tsv`. The 10 classes match the docstring list. Argparse errors (exit 2, no REFUSAL token) and `raise OSError("path is not absolute")` (line 253, caught and reported as JSON-UNWRITABLE) are outside the docstring's refusal classes.

Falsification of the counter (exit-code dimension):

```
variant-noexit.py   (fixture check: ("REFUSAL %s:" % cls) in stderr only)
$ bash census/round-41/score-candidate.sh c3 <S> tests/fixtures/r41-refusal-sites.py=<variant-noexit.py>
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=14e307e2ab76
EXIT=0

variant-exitonly.py (fixture check: returncode == 2 only)
SUMMARY sites=19 probes=21 pristine=ok killed=0 survived=19 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=89e5904b2d62
EXIT=1
```

The class token is enforced by the counter (exit-only variant fails 19/19). The exit-2 check is not enforced (no-exit variant still kills 19/19), because the counter mutates only the class label and never the exit status. The variants are kept as receipts at `.ufo/waves/round-41/w2/R41w2reviewer03/c3-falsify-variant-noexit.py` and `…/c3-falsify-variant-exitonly.py`.

## Evidence pointers

- `tests/fixtures/r41-refusal-sites.py:50-72` (probe table), `:75` (argv), `:78` (`good = p.returncode == 2 and ("REFUSAL %s:" % cls) in p.stderr`), `:83` (PASS/FAIL print), `:84` (SUMMARY).
- `tools/souji-worktree-drift.py:452-454` (main: Refusal → `REFUSAL <exc>`, return 2); `:447-449` (USAGE on timeout < 1).
- `census/round-41/c3-counter.py:50` (`SITE_RE`), `:140` (killed iff failing == mapped and rc == 1), `:172` (target), `:232-233` (uid 0 refused).
- `census/round-41/r1-counter.py` — target and kill rules as printed in the counter header; M19/M20/M21 owned by `r41-drift-record-order.py`, killed by that fixture and not by old fixtures (per the SUMMARY `old_fixtures_killed_new=0`).

## Residual risk and gaps

1. Counter blind to exit-2 assertion (above). Remedy before the C3 wording "asserts exit 2" is counter-verified: add a status-mutation dimension, for example a second mutant set that rewrites `return 2` to `return 1` in the refusal paths, so that a fixture without `rc == 2` is killed. Not part of this seat's assignment; not changed here.
2. The probes assert only the class token (substring), not the site-specific message text. Site attribution rests on the counter's mutation test, which the trace above confirms for all 19 sites.
3. Environment dependencies: P02a and P18 need a non-root uid (fixture and counter refuse uid 0); P11 needs `/dev/null` as a character device; P14 needs git to accept a `.git` file whose gitdir has HEAD/objects/refs. All held on this host.
4. The trace shows P19 is not raised through `Refusal`; it is covered by the direct run above.

## Cleanup

Scratch `/fast/scratch/hyaku/souji-r41/R41w2reviewer03` deleted after copying receipts into `.ufo/waves/round-41/w2/R41w2reviewer03/`. Lane unchanged (`git status --short` empty). Candidate/variant bytes exist only under the seat directory and inside score-candidate's own clone, which the script removed.
