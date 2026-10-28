# R40connector45 — C3 coverage attack: the invalid-UTF-8 branch is measured through a fixture-side lens that hides it

Seat: connector. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base revision: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (round-39 verified tip).
Scratch: `/fast/scratch/hyaku/souji-r40/R40connector45` (removed at end of seat; see §12).
No commit, no push, no git/jj/index mutation. Read-only git only (`rev-parse`, `show`, `ls-files`, `status`).
No lane production file written. This report is the seat's only write.

**Axis attacked:** coverage (C3).
**Distinct item 45 — the edge case I name explicitly:** *the invalid-UTF-8 record branch is
discriminated by the fixture's own output-capture and failure-reporting path, not by the tool's
refusal class.* Every other r40 seat on C3 works the tool side (which refusal, which drift class).
This seat works the **harness side**: the bytes the fixture writes, the way it captures the tool's
stdout/stderr, and the way the frozen kill contract reads the fixture's own output. The named edge
case is **"the tool's `errors="replace"` decode turns an invalid record byte into U+FFFD, so the
invalid-byte branch is a *silent-rename* branch, not a refusal branch — and the two r40 fixture
styles that could observe it each destroy the observation in a different way."**

## Verdict (one line)

**C3 is NOT falsified, but it is currently UNREACHABLE as written.** The frozen A5 kill contract
cannot score a kill for *any* mutant whose failure mode is a tool-side traceback, and cannot score
a kill for *any* mutant that makes the tool emit a lone non-UTF-8 byte, unless the r40 fixture
deviates from the r39 house style in two specific ways (§3, §4). Both deviations were measured,
and with them a candidate fixture kills **15/15** candidate mutants, with pristine passing and
**base_killed=0** against both candidate base fixtures (§8). The C3 predicate is satisfiable — but
only through a fixture that is not a house-style clone, and the round's own plan text does not say so.

---

## 1. Byte binding — the measurement is on committed bytes

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --show-toplevel
/home/vgpnk/Projects/shokunin/souji-shokunin
$ git rev-parse HEAD
be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e
$ sha256sum tools/souji-worktree-drift.py | cut -c1-12
e48ed08e6728
$ git show HEAD:tools/souji-worktree-drift.py | sha256sum | cut -c1-12
e48ed08e6728
$ git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py | sha256sum | cut -c1-12
e48ed08e6728
$ sha256sum census/round-39/c3-counter.py | cut -c1-12
5d856aade016
```

All three revisions carry identical tool bytes (`e48ed08e6728`), so the base, HEAD, and working
tree are one code object. The kill contract was **imported verbatim** from the frozen
`census/round-39/c3-counter.py` (`spec_from_file_location` on the committed path) rather than
re-typed, so no measurement below can drift from the frozen A5 contract.

## 2. The frozen contract under attack

`census/round-39/c3-counter.py:87-103` (`score()`), inherited by `tests/fixtures/r38-drift-mutants.py:49-65`:

```python
proc = subprocess.run([...fixture...], stdout=PIPE, stderr=PIPE, text=True, check=False)
summaries = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
if not summaries:
    return False, "NO-SUMMARY rc=%d" % proc.returncode, None
...
crash = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)
killed = proc.returncode == 1 and fails > 0 and not crash
```

Two clauses are load-bearing for the invalid-UTF-8 branch:

* `crash` is computed on the **fixture's** stdout+stderr. Its stated purpose (r38 A5, see the
  comment at `tests/fixtures/r38-drift-mutants.py:58-60`) is to catch a *crashing fixture* that
  would otherwise report a bogus kill.
* `text=True` on the fixture subprocess means the **tool's** stdout is decoded as UTF-8 with the
  default strict handler before the fixture ever sees it.

Neither clause was ever exercised by the r36–r39 batteries, because none of M7–M14 produces a
tool-side traceback or a non-UTF-8 tool byte. Measured (§7):

```
r39 battery M11-M14 against tests/fixtures/r39-drift-record-rules.py:
  M11 killed=yes rc=1 fails=1 crash=False
  M12 killed=yes rc=1 fails=1 crash=False
  M13 killed=yes rc=1 fails=1 crash=False
  M14 killed=yes rc=1 fails=1 crash=False
```

`crash=False` on all four. **The blind spot is latent, not historical** — r40's invalid-UTF-8
branch is the first thing in the lane to walk into it.

## 3. FINDING 1 — the crash detector fires on the *tool's* traceback, so a real kill reads ALIVE

The r39 house style captures the tool's output and re-prints it verbatim into the fixture's own
FAIL detail line (`tests/fixtures/r39-drift-record-rules.py:76-80`):

```python
out = proc.stdout + proc.stderr
...
results.append((name, ok, "rc=%d want=%d missing=%r out=%r" % (
    proc.returncode, want_rc, missing, out.replace("\n", " ")[:160])))
```

So when the **tool** dies with an uncaught exception, the tool's traceback text is re-emitted by
the **fixture** into the fixture's stdout — and the contract's `crash` detector, which is looking
for a broken fixture, fires on it. The mutant is then scored ALIVE even though the fixture
correctly detected it.

Measured with a strict-decode mutant `M18` (`decode("utf-8","replace")` → `decode("utf-8","strict")`
at `tools/souji-worktree-drift.py:147`; anchor occurs exactly once, so this is a real single-defect
mutant and not a battery defect):

```
A (text=True, echo)    x pristine           killed=no  rc=0 fails=0 crash=False
A (text=True, echo)    x M18 strict-decode  killed=no  rc=1 fails=2 crash=True   <-- NOT a kill
B (echo + redact)      x pristine           killed=no  rc=0 fails=0 crash=False
B (echo + redact)      x M18 strict-decode  killed=yes rc=1 fails=2 crash=False  <-- IS a kill
v2 (bytes + redact)    x M18 strict-decode  killed=yes rc=1 fails=2 crash=False
```

Fixture B is fixture A with one change: the tool's stderr is redacted before it reaches the
fixture's stdout (`out.replace("Traceback (most recent call last)", "<TOOL-TRACEBACK>")`). The
**only** difference between the two verdicts is that redaction. The fixture's own stderr is empty
in both runs (`fixture stderr empty: True`), so the fixture did not crash — the tool did, and the
tool's crash was laundered through the fixture's stdout.

**Consequence for the frozen C3 predicate.** "each declared single-defect mutant is killed by the
r40 fixture" is **unreachable for any mutant whose failure mode is a tool-side exception**, under
a house-style fixture. The r40 C3 battery will almost certainly include a decode-error mutant
for the invalid-UTF-8 branch — it is the most natural single-defect mutant there — and that mutant
will read ALIVE for a reason that has nothing to do with the tool's behavior.

## 4. FINDING 2 — `text=True` makes the *fixture* die on a lone `0xff`, losing every case

The second half of the same lens. `text=True` decodes the tool's stdout as strict UTF-8. A mutant
whose decode handler is `surrogateescape` (`M25`) makes the tool emit the raw byte `0xff` on
stdout. The fixture then raises `UnicodeDecodeError` **inside `subprocess.communicate()`** — the
fixture dies before it can print its own `SUMMARY`, so all 8 of its cases are lost at once.

```
A (text=True, echo)    vs M25-surrogateescape: fixture rc=1  stderr-lines=31
      UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 15: invalid start byte
v2 (bytes)             vs M25-surrogateescape: fixture rc=0  stderr-lines=0

frozen contract reads A (text=True, echo)    killed=no NO-SUMMARY rc=1 cases=None
frozen contract reads v2 (bytes)             killed=no rc=0 fails=0 crash=False cases=7
```

Note the second line: with bytes capture the fixture *runs to completion* and reports
`rc=0 fails=0` — it thinks the mutant is pristine, because `errors="replace"` on the *tool* side
and `errors="replace"` on the *fixture* side collapse both `0xff` and U+FFFD to the same text.
Fixing the crash is necessary but **not sufficient**: the fixture must also discriminate at the
**byte** level (§5).

## 5. FINDING 3 — text-level assertions cannot discriminate the decode handlers at all

The three decode handlers produce three different byte sequences on the tool's stdout for the
same invalid record byte. Measured directly (`REPO\tal\xffpha\t…`, fleet root with repo `alpha`):

```
tool-pristine.py            b'DRIFT\tABSENT\tal\xef\xbf\xbdpha\trecorded regs=1'   (U+FFFD, errors="replace")
tool-M25-surrogateescape.py b'DRIFT\tABSENT\tal\xffpha\trecorded regs=1'            (raw 0xff)
tool-M26-backslashreplace.py b'DRIFT\tABSENT\tal\\xffpha\trecorded regs=1'         (ASCII \xff)
tool-M28-latin1.py          b'DRIFT\tABSENT\tal\xc3\xbfpha\trecorded regs=1'         (U+00FF, latin-1)
```

Every one of those decodes to a *different* Python string, but `errors="replace"` on the fixture
side maps **all** of them to a text containing U+FFFD. So a text-level assertion
(`"DRIFT\tABSENT\tal�pha"`) is satisfied by `replace` and by `surrogateescape` alike.
The measured consequence:

```
mutant                 v2 (bytes, text assert)   v3 (bytes, BYTE assert)
M25-surrogateescape    no  [rc=0 fails=0]         K
M19-ignore             K                          K
M26-backslashreplace   K                          K
M28-latin1             K                          K
```

`v3` adds exactly one case — `run_case_bytes`, which asserts on the tool's **raw** stdout bytes
(`b"DRIFT\tABSENT\tal\xef\xbf\xbdpha"`) rather than on decoded text — and M25 becomes killable.
Without that one case the surrogateescape handler is invisible to the whole battery.

## 6. FINDING 4 — the `--skip-unrecorded` branch's *obvious* mutant is already killed by r36/r37

The r40 planned row names three uncovered branches. Two of them (multiple TOTAL rows, invalid
UTF-8) are genuinely uncovered. The third is not, at least not by the mutant one would write first.

`M17` inverts the flag at `tools/souji-worktree-drift.py:370` (`if not args.skip_unrecorded:` →
`if args.skip_unrecorded:`). Measured across the whole pre-existing fixture set:

```
M17 invert-flag        r36=K r37=K r38=. r39=. v4=K
M21 flag-present-only  r36=. r37=. r38=. r39=. v4=K
M22 flag-ignored       r36=. r37=. r38=. r39=. v4=K
```

`M17` is killed by **r36 and r37** on their existing `unrecorded` cases — because inverting the
flag makes the *flag-absent* path skip unrecorded repos, which breaks r37's `case-unrecorded-exact`
and `case-unrecorded-unreachable` (verified by running the r37 fixture directly against M17:

```
case-unrecorded-exact=FAIL rc=0 ... 'drift_rows': '0' ...
case-unrecorded-unreachable=FAIL rc=0 ... 'drift_rows': '0' ...
SUMMARY cases=6 pass=4 fail=2
```

). This is the *marginality* hazard the C3 predicate does not name. The C3 control clause reads
"r39 fixture/counter has no cases for these branches and kills none of the new mutants" — true
against the r39 fixture alone, but the *lane-wide* union of existing fixtures already discriminates
the natural `--skip-unrecorded` mutant. Only the flag-**present**-only mutants (`M21`:
`if not args.skip_unrecorded or args.skip_unrecorded:`; `M22`: `if True:`) survive all four
existing fixtures and are genuinely new coverage.

**Practical consequence:** if the r40 battery picks `M17` (the natural inversion), the counter will
still print `base_killed=0` against the r39 base fixture and the C3 predicate will read as
satisfied — while two pre-existing fixtures already kill it. The new fixture would then be
credited with coverage the lane already had, and the round's coverage evidence would overstate
the delta. The battery must use `M21`/`M22`-class mutants to make the claim honest.

## 7. FINDING 5 — the C3 base leg has two mutually exclusive readings; the round must pick one

The C3 predicate's base clause — "all mutants survive the r39 base fixture" — is ambiguous, and
the two readings demand different fixtures. Measured:

```
Reading A (base_killed = 0 on the NEW mutants; r40 fixture may be a superset):
    base(r38) killed=0 for all 15 new mutants
    base(r39) killed=0 for all 15 new mutants
    -> satisfied by both v3 and v4.

Reading B (the r39 BASELINE mutants M11-M14 must SURVIVE the r40 fixture):
    r40-drift-record-branches-v3.py   r39 baseline mutants killed = 0/4   (Reading B satisfied)
    r40-drift-record-branches-v4.py   r39 baseline mutants killed = 4/4   (Reading B VIOLATED)
```

`v3` covers only the three new branches and therefore kills none of M11–M14 (its `good` case and
`total-last-wins` case do not exercise the r39 rules). `v4` is `v3` **plus** r39's five regression
cases (`trailing-space`, `crlf`, `outside-root`, `indented-comment`, `comments-total-only`) and
therefore kills all four of M11–M14.

Under Reading A the r40 fixture should be a **superset** (`v4`): the r39 fixture would otherwise
be orphaned and the lane would carry two drifting fixtures. Under Reading B the r40 fixture must
be **disjoint** (`v3`), which leaves M11–M14 with no single fixture that kills them.

The preregistration text supports Reading A ("all mutants survive the r39 base fixture" — the
subject is the *new* mutants, and the control says the r39 counter "kills none of the new
mutants"), and the round's own measurement convention supports it (the r39 counter's `base_killed`
counts kills of *the battery under test* by the base fixture, `census/round-39/c3-counter.py:178`).
**Reading A is the correct one and I adopt it.** But the wording admits Reading B, and the two
readings are not distinguishable from the preregistration text alone — a round that wanted to
count M11–M14 kills toward the r40 claim would be reading B and would need to say so.

## 8. The measurement that satisfies C3, end to end

`v4` = `v3` + r39's five regression cases, bytes capture, marker redaction, one byte-level
assertion. All scored by the **frozen** `score()` imported from `census/round-39/c3-counter.py`.

```
0. BYTE BINDING
tool sha (worktree)          e48ed08e6728
tool sha (HEAD)              e48ed08e6728
tool sha (r40 base rev)      e48ed08e6728
scratch pristine copy sha    e48ed08e6728
frozen contract module       census/round-39/c3-counter.py  sha 5d856aade016

1. PRISTINE CONTROL over all five fixtures
  r36     killed=no  rc=0 fails=0 crash=False     cases=12
  r37     killed=no  rc=0 fails=0 crash=False     cases=6
  r38     killed=no  rc=0 fails=0 crash=False     cases=10
  r39     killed=no  rc=0 fails=0 crash=False     cases=7
  A echo  killed=no  rc=0 fails=0 crash=False     cases=7
  B redact killed=no  rc=0 fails=0 crash=False     cases=7
  v2 bytes killed=no  rc=0 fails=0 crash=False     cases=7
  v3 +byte killed=no  rc=0 fails=0 crash=False     cases=8
  v4 super killed=no  rc=0 fails=0 crash=False     cases=13

2. KILLER MATRIX (rows=mutant, cols=fixture; K=kill, . = alive)
mutant               r36    r37    r38    r39    v2      v3      v4
--- r40-new battery ---
M15                 .      .      .      .      K      K      K
M16                 .      .      .      .      K      K      K
M17                 K      K      .      .      K      K      K
M18/M18-strict      .      .      .      .      K      K      K
M19/M19-ignore      .      .      .      .      K      K      K
M20/M28-latin1      .      .      .      .      K      K      K
M21                 .      .      .      .      K      K      K
M22                 .      .      .      .      K      K      K
M23                 .      .      .      .      K      K      K
M25-surrogateescape .      .      .      .      .      K      K
M26-backslashreplace.      .      .      .      K      K      K
M27-nonascii        .      .      .      .      K      K      K
--- r39 battery M11-M14 ---
M11                 .      .      .      K      .      .      K
M12                 .      .      .      K      .      .      K
M13                 .      .      .      K      .      .      K
M14                 .      .      .      K      .      .      K

   TOTAL r40-new battery: 15 mutants, v4 killed=15, base(r39) killed=0
   TOTAL r39 battery M11-M14: 4 mutants, v4 killed=4, base(r39) killed=4
```

Every C3 leg holds for `v4`: pristine passes (`rc=0 fails=0`, 13 cases ≥ 6), all 15 new mutants
are killed, and **all 15 new mutants survive both candidate base fixtures**
(`base=r38: 15 new mutants, base_killed=0`; `base=r39: 15 new mutants, base_killed=0`) — so the
base leg passes under either reading of which file is "the r39 base fixture" (§7), because
`census/round-39/c3-counter.py:113` defaults `--base-fixture` to the **r38** fixture while the
preregistration names the **r39** one. Both are zero.

## 9. Exact commands run

All under `/fast/scratch/hyaku/souji-r40/R40connector45` with `TMPDIR` set to that directory.
Every git fixture was created with `mktemp`/`mkdtemp` under that scratch, every git command used
`-C <exact fixture dir>`, and `git rev-parse --show-toplevel` was asserted equal to the fixture
root before each commit (assertion in `mkfleets.py:35`, `probe.py:45`,
`r40-drift-record-branches-v2.py:56`).

```
python3 -B probe.py                                   # pristine behaviour on B1/B2/B3
python3 -B genmutants.py                              # M15-M20, anchor-count checked
python3 -B genmutants2.py                             # M21-M23
python3 -B matrix.py                                  # candidate fixture x mutants
python3 -B isolate.py                                 # LINK1-3 crash-detector isolation
python3 -B widematrix.py                              # all 5 fixtures x all mutants
python3 -B redact_proof.py                            # echo vs redact, frozen score()
python3 -B score2.py ; score3.py ; score_v2.py ; score_v3.py ; score_v4.py
python3 -B latency.py                                 # crash-latency of M11-M14
python3 -B basecheck.py                               # base leg vs r38 and r39 base fixtures
TMPDIR=$PWD python3 -B final_evidence.py              # the consolidated run quoted in §1-§8
```

Anchor discipline: every mutant anchor occurs **exactly once** in
`tools/souji-worktree-drift.py` (`genmutants.py:38-43` asserts `count != 1` → `ANCHOR-DEFECT`), so
no kill is a battery defect. The r39 battery M11–M14 was regenerated from the frozen
`census/round-39/c3-counter.py:50-58` `MUTANTS` tuple rather than re-typed.

## 10. Affected axes, proposed move, risks, verification

**Affected axis:** coverage (C3) — this attack changes nothing on calibration (C1) or operability
(C2), and touches no lane production file.

**Proposed move (one, bounded).** The r40 C3 work should adopt a **bytes-safe, marker-redacting,
byte-asserting fixture** and a **flag-present-only `--skip-unrecorded` mutant**, and the r40
counter should measure the base leg against **both** the r38 and r39 fixtures. Concretely:
(i) capture the tool's stdout/stderr as bytes and decode with `errors="replace"`; (ii) redact the
`Traceback (most recent call last)` marker before it can reach the fixture's stdout, or — cleaner
— have the counter read the **tool's** stderr for the crash marker instead of the fixture's;
(iii) add one byte-level assertion on the tool's raw stdout for the invalid-UTF-8 case;
(iv) use `M21`/`M22`-class mutants so the `--skip-unrecorded` claim is actually marginal.

**Risks.**
1. Fix (ii) weakens the A5 clause as written: the r39 counter's `crash` detector exists to catch a
   *crashing fixture*, and redaction makes the fixture's own stdout a slightly less faithful mirror.
   The safer variant is to keep the marker visible but have the counter scope the crash check to
   the tool's stderr — that changes the counter, not the evidence. **[INFERENCE]** the round should
   prefer that variant; I did not implement it, so I have not measured it.
2. A bytes-safe fixture that swallows decode errors with `errors="replace"` risks *concealing* a
   tool-side encoding defect (the M25 case in §4 is exactly that). The byte-level assertion in (iii)
   is what prevents the concealment; without it, bytes capture alone makes things worse, not better.
3. `v4`'s 13 cases are a superset of `v39`'s 7 and `r36/r37/r38`'s coverage still stands, but if
   the round prefers Reading B (§7), `v4` is the wrong shape and `v3` is right. The preregistration
   supports Reading A; I recommend it.
4. The `--skip-unrecorded` marginality finding (§6) means a battery containing `M17` produces a
   *green* receipt that overstates the lane's delta. This is a reporting risk, not a tool risk.

**Verification the main agent should run.** Re-run the r40 C3 counter with `--fixture` pointed at
the r40 candidate and `--base-fixture` at both `tests/fixtures/r38-drift-record.py` and
`tests/fixtures/r39-drift-record-rules.py`, and confirm `SUMMARY mutants=N killed=N survived=0
pristine=ok base_killed=0`. Then confirm the counter's crash clause reads the **tool's** stderr, not
the fixture's stdout, by checking that a decode-error mutant is scored `killed=yes`. Neither check
was run by me against an r40 artifact — the r40 fixture and counter do not exist yet — so both are
stated as **what to run**, not as results.

**Explicitly not claimed.** I do not claim the r40 C3 claim is false. I claim it is **unreachable
under a house-style fixture**, and that it is reachable under a measured alternative. I do not
claim the invalid-UTF-8 branch is covered by any committed r40 artifact — no r40 fixture exists in
the tree (`ls census/round-40/` shows only `preregistration.txt`).

## 11. Tooling

No installs, no updates. No pacman (paused by the operator directive). Python 3.14.8 and git
were already present; `python3 -B` was used throughout to avoid `__pycache__` writes into the lane.

## 12. Cleanup

`/fast/scratch/hyaku/souji-r40/R40connector45` was removed after the evidence was captured; the
report carries every number needed to reproduce it. Nothing under the lane repo was modified
(`git status --porcelain` shows only the pre-existing `?? census/round-40/`). No fleet, sibling
lane, `.ufo/state`, watchdog, operator config, template, or fleet script was touched.
