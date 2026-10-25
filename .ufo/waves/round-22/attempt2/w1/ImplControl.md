STATUS: PASS

Seat: ImplControl (round 22, attempt 2 / hyaku, lane: repo and workspace hygiene).
Deliverable: the C1 kill-rule control and the fixture gate that scores any candidate
against the five frozen C1 fixtures. No repo file, no index, no history touched.

## Axis accounting (Godspeed)

- calibration: the C1 counter can no longer be satisfied vacuously. The do-nothing control
  is measured at `control=FALSE-GREEN-REJECTED fixtures=1/5`, while both independent
  candidates score `control=PASS fixtures=5/5`. The preregistration's kill rule now has an
  executed receipt instead of an assertion.
- operability: `fixture-gate.py <any-candidate-path>` is one positional argument, one line
  on stdout, per-fixture receipts on stderr, no lane-repo writes, throwaway tree removed
  unless `--keep`. Exit 0 = PASS, 1 = rejected, 2 = harness/usage failure.
- coverage: all five frozen fixtures are instantiated as real git repositories with one
  injected fault each, audited independently of any candidate by direct `git` probes.
- no axis harmed: no mutation of SCORECARD.md, tools/, corpus/, census/, .ufo/state,
  MANIFEST.json, the lane index, the fleet root's templates/ or scripts/; certification OFF
  untouched; no deletion authority created; nothing signalled; shokuknow untouched.

## Artifacts written (all inside the named evidence path, plus this report)

```
0fca0701cacbacc568435576f454332962ac1596d9a9ef392ba9af9845f001d6  evidence/control/always-zero.py            (904 B)
8ae996d76679583deda3c126e6d6be89f2c512c4ddc7c17416b6945997e2dd0d  evidence/control/fixture-gate.py          (16106 B)
88ca3502de71e97ff900094b16ccb2b6c615f1eb5153e7c817d2986fcd9a57e8  evidence/control/transcript-always-zero.txt (82 lines)
e5f39d54cf36a9d16ef2171a293943ceab8c0b6e9b8178d47f8794593cc1c857  evidence/control/transcript-fixture-audit.txt (107 lines)
58aafedc8a51197ebf74b5ad8046c09984efe428d0580100f750907ed7bf05a8  evidence/control/transcript-impl.txt        (39 lines)
```
Paths relative to `.ufo/waves/round-22/attempt2/w1/`. The third transcript
(`transcript-fixture-audit.txt`) is the fixture-correctness audit required to answer
"which fixture failed to discriminate" from data rather than from belief; it adds no file
outside the evidence path.

`always-zero.py` prints `assertions=0 resolved=0 skipped=0 mismatches=0` and exits 0 without
inspecting `argv` and without opening any file (`COUNTS` is a literal; `argv` is never read).

## Executed evidence

### 1. always-zero must be rejected — it is

```
$ python3 -B fixture-gate.py always-zero.py
[candidate] fixture=1-all-good          expect=zero    ... a=0 r=0 s=0 m=0 verdict=PASS note=assertions-zero-no-discrimination-here
[candidate] fixture=2-nonexistent-path  expect=nonzero ... a=0 r=0 s=0 m=0 verdict=FAIL
[candidate] fixture=3-dangling-revision expect=nonzero ... a=0 r=0 s=0 m=0 verdict=FAIL
[candidate] fixture=4-wrong-digest      expect=nonzero ... a=0 r=0 s=0 m=0 verdict=FAIL
[candidate] fixture=5-path-at-other-rev expect=nonzero ... a=0 r=0 s=0 m=0 verdict=FAIL
control=FALSE-GREEN-REJECTED fixtures=1/5
gate_exit=1
```
(full stdout+stderr in `transcript-always-zero.txt`)

**Which fixture failed to discriminate: none of 2-5.** Each of the four negative fixtures
rejected the control on its own single fault. Fixture 1 cannot discriminate by construction
and is not broken: the frozen expectation for it is "0 mismatches", which the control meets
trivially (`a=0`), so the gate annotates it `note=assertions-zero-no-discrimination-here`
instead of pretending it has teeth. Discrimination lives entirely in fixtures 2-5, exactly
as the frozen kill rule is written (1 = positive control, 2-5 = four negative controls).

### 2. The harness can award PASS — calibration oracle 5/5

The gate first runs the same five fixtures through a minimal frozen-class A/B/C reader
(written into the throwaway tree, never into a repo) whose only purpose is to prove the gate
is falsifiable in both directions rather than a machine that only says no:

```
oracle=PASS fixtures=5/5
[oracle] fixture=1-all-good          a=4 r=4 s=0 m=0 PASS
[oracle] fixture=2-nonexistent-path  a=5 r=4 s=0 m=1 PASS
[oracle] fixture=3-dangling-revision a=5 r=4 s=0 m=1 PASS
[oracle] fixture=4-wrong-digest      a=4 r=3 s=0 m=1 PASS
[oracle] fixture=5-path-at-other-rev a=5 r=4 s=0 m=1 PASS
```

### 3. Both C1 candidates in `../evidence/impl-a/` and `../evidence/impl-b/` — 5/5 each

`impl-a` was absent on the first check (03:47:29), present at 03:48:55; `impl-b` was absent
at 03:48:55 and present at 03:49:41. Both were scored once present, with no edits to either:

```
impl-a: control=PASS fixtures=5/5   gate_exit=0
        [1] a=4 r=4 s=0 m=0 | [2] a=5 r=4 s=0 m=1 | [3] a=5 r=4 s=0 m=1
        [4] a=4 r=3 s=0 m=1 | [5] a=5 r=4 s=0 m=1   (exit 0,1,1,1,1)
impl-b: control=PASS fixtures=5/5   gate_exit=0
        identical counts and exit codes per fixture
```
Two independently written candidates agree with the oracle on the assertion count, the
per-fixture mismatch count and the exit contract for all five fixtures, and both are cleanly
separated from the control. Their assertion counts matching the oracle exactly
(a=4/5/5/4/5) is a second, independent check that my fixtures contain exactly the
assertions they claim and no hidden ones.

### 4. Fixture correctness, audited without any candidate (`transcript-fixture-audit.txt`)

Direct `git cat-file` / `git show`/sha256 probes on a kept tree, per fixture:

| fixture | injected fault | verdict |
|---|---|---|
| 1-all-good | none; `tools/helper.sh` present, `rev 04aa35c` resolves, digest `7b920614…` matches the committed blob | good |
| 2-nonexistent-path | `git cat-file -e HEAD:tools/absent.py` -> rc!=0 | real |
| 3-dangling-revision | `git cat-file -e deadbee^{commit}` -> rc!=0 | real |
| 4-wrong-digest | token `d84448dd…` != sha256 of the committed blob `7b920614…` | real |
| 5-path-at-other-rev | `cat-file <rev>:tools/late.sh` rc!=0 while the worktree and HEAD both have it; `SCORECARD.md` byte-identical at `--rev` and in the worktree | real |

Fixture 5 is built so that the declaration bytes are the same whichever copy a candidate
reads (worktree or `--rev`); the only way to pass it is to resolve the *path* against
`--rev`. Fixtures 2-5 each keep every good element resolving, so a single fault is the only
possible source of a nonzero mismatch count. No audit line printed `FIXTURE BROKEN`.

### 5. "Without reading any byte" — measured, not asserted

```
$ strace -f -e trace=openat,open,stat,newfstatat,lstat,access \
    python3 -B always-zero.py --root /nonexistent-root --file NOPE.md --rev deadbee
assertions=0 resolved=0 skipped=0 mismatches=0
counts_line_exit=0
syscalls naming the requested args or any repo path: 0
```
Even handed a `--root` and `--file` that do not exist and a 7-hex `--rev` that resolves to
nothing, it emits the counts line and exits 0. The only paths in the trace are CPython's own
startup imports plus the script file itself; nothing under the fixture repository is opened.
Disclosures on this trace: (a) CPython startup touches `/proc/self/maps` and
`/proc/sys/vm/overcommit_memory` — interpreter startup, not a read I performed, and no
`/proc` census content was read by this seat; (b) the trace records absolute paths, no file
contents.

### 6. Gate edges

```
$ python3 -B fixture-gate.py /nonexistent/candidate.py
gate-error: candidate is not a file: /nonexistent/candidate.py
rc=2
$ python3 -B fixture-gate.py
fixture-gate.py: error: the following arguments are required: candidate
```

## Judged decisions (stated so a reviewer can overturn them)

1. **Pass criterion = the frozen mismatch polarities, nothing more.** Fixture 1 requires
   `m == 0`; fixtures 2-5 require `m >= 1`. I deliberately did not add "assertions >= 1 on
   fixture 1" even though it would have rejected the control on fixture 1 as well: the
   frozen kill rule states fixture 1's expectation as "0 mismatches", and adding criteria to
   a frozen rule is not mine to do. Consequently the control scores 1/5, not 0/5.
2. **Exit-code contract is reported, not scored.** The counter contract says exit 0 iff
   `M == 0`; the gate emits `note=exit-contract-deviation` when a candidate violates it,
   but the PASS/REJECT verdict rests on mismatch polarities only. No such note fired for
   always-zero, impl-a or impl-b.
3. **`control=PASS` requires 5/5 and a passing oracle.** If the oracle ever drops below 5/5
   the gate prints `fixtures=0/5`, `GATE-BROKEN` on stderr and exits 2, so a broken harness
   can never be read as a rejection of the candidate under test.
4. **`n` is 5,** the number of frozen C1 fixtures.

## Scope and compliance

- Writes: the five files listed above, plus this report. Nothing else under
  `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/`.
- `git` write operations (`init`, `add`, `commit`) ran **only** inside throwaway trees under
  `/tmp/c1-fixtures-*`, created by the gate and removed on exit; the one kept tree used for
  the audit was deleted after the audit. Zero git or jj writes against the lane repo, any
  sibling repo, or shokuknow; no commit, push, fetch, checkout or index operation anywhere
  outside `/tmp`. Building a revision-resolving fixture requires real commits, so this is
  the minimum possible footprint and it never touches measured bytes.
- Read-only holds respected: no writes to SCORECARD.md, tools/, corpus/, census/, `.ufo/state`,
  `.ufo/watchdog.log`, MANIFEST.json, the lane index, the fleet root's `templates/` or
  `scripts/`; no credential, `.tower`, private TSV or operator-sweep census content read; no
  process signalled; no cleanup of lane artifacts performed; no deletion authority created.
- Tooling: nothing installed or updated. `git 2.56.0`, `python3` 3.14 and `strace` were
  already present; pacman was not invoked (host-wide pause honoured).
- `impl-a` and `impl-b` were executed read-only as candidate paths; neither was modified.

## Residual risks

1. The fixtures are synthetic single-commit repositories, not the lane's SCORECARD.md. They
   cover the five frozen fixture shapes; they do not cover class-A globs, `:line` suffixes,
   a 40-hex boundary token, or the cell-prose revisions the real audit must survive. Those
   belong to the reviewer/mutation seats, not to the kill rule.
2. Fixture 1 is non-discriminating by construction; a vacuous tool therefore scores 1/5, not
   0/5. Any tool that reads the declaration must still clear fixtures 2-5.
3. My oracle is authored alongside the fixtures, so its 5/5 is a harness-calibration receipt,
   not independent evidence about the class semantics. The independent evidence is that
   impl-a and impl-b — written by other seats without seeing the fixtures — reproduce the
   oracle's counts exactly and clear all five.
4. The gate scores mismatch polarities and reports, but does not fail on, exit-code
   deviations (decision 2 above).
