# W1RevC2Legs — C2 leg-by-leg falsification (r39 wave 1, reviewer)

Seat: reviewer. Role: attack C2's six legs — for each leg in `census/round-39/c2-counter.py`,
find the cheapest wrong implementation that satisfies it, name the discriminating property, and
propose one extra case that closes the widest gap.

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (read-only; I committed nothing, landed
nothing, mutated nothing in the lane). Scratch:
`/fast/scratch/hyaku/souji-r39/W1RevC2Legs/` (harnesses `harness.py`, `harness2.py`; fixture repos
`D/`, `D2/`, `anc/repo`; **left on disk intentionally** for the L1 to inspect).
Runtime: `Python 3.14.8`, `git version 2.56.0`. No tool installed or upgraded (pacman untouched).

## 0. Bottom line

- **The frozen C2 predicate is VERIFIED as stated**, at two revisions: `SUMMARY legs=6 pass=6
  fail=0 harm=0`, rc 0 (see §1). The do-nothing control reproduces `pass=2 fail=4` (§1.2).
- **But four of the six legs are satisfiable by implementations that do not resolve anything.**
  The widest: a tool that resolves `--rev` as *"is an ancestor of HEAD"* — the exact conflation
  R11 was routed for — passes **all six legs** (`SUMMARY legs=6 pass=6 fail=0 harm=0`, rc 0; §3 V2).
- A tool that prints `REFUSAL REV-UNRESOLVED` and exits 1 satisfies **no** leg (rc 2 is
  load-bearing; §3 V7). A tool that exits 2 for every input satisfies **L1/L2/L3** and is stopped by
  L5/L6 (§3 V1) — the task's hypothesis, confirmed.
- L5 and L6 read **worktree** bytes, not committed bytes: a forged *committed* fixture with the real
  worktree fixture passes L5, and a zero-case consumer fixture passes L6 (§3 E, Z).

## 1. Verification of the frozen predicate

### 1.1 Counter at the lane tip (two revisions, because the tip moved mid-review)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ git rev-parse HEAD                      # first read: 2201778e7736af82e7d8a42dec2494f115bf3923
$ TMPDIR=/fast/scratch/hyaku/souji-r39/W1RevC2Legs/tmp timeout 600 \
  python3 -B census/round-39/c2-counter.py --root "$PWD" --rev 2201778... --base-rev ed30b7f5... --scratch ...
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
counter rc=0
```

```
$ git log --oneline -5
d4c1755 round-39: C3/scratch — honour the caller's TMPDIR in c3-counter git children ...
2201778 round-39: PROVINCE boundary note — two tool contracts repaired, ...
$ git rev-parse HEAD    -> d4c17557b92fd98044e4c8f0ddc79c6d75701b15
$ (same counter, --rev d4c1755...)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
rc=0
```

**Verdict:** C2's frozen predicate holds at both `2201778` and `d4c1755` (6/6, harm 0, rc 0).
The `fixture_sha` moved because a peer landed `d4c1755` (the A1 fixture amendment) between my two
reads; the leg verdicts did not move.

### 1.2 Do-nothing control (kill-rule arm)

```
$ cat census/round-39/records/c2-before.txt
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 5, 3, 1) old=(8, 5, 3, 1)
LEG L6 PASS ...
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=c142c1bc28b8

$ python3 -B census/round-39/c2-counter.py --root "$PWD" --rev ed30b7f5... --base-rev ed30b7f5...
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
LEG L6 PASS ...
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=e555d8281484
```

**Verdict:** the receipt is honest (`pass=2 fail=4`; base is not `pass=6`). Its L5 detail differs
from today's (`(8,5,3,1)` vs `(8,4,4,1)`) because the receipt predates A1 — and its
`fixture_sha=c142c1bc28b8` is the fixture **at the freeze commit `b769bfb`**:

```
$ for c in $(git log --format=%H -8 -- .../r39-citation-rev.py); do ... sha256sum ...; done
d4c1755 ... fixture_sha=e555d8281484
bbd9b97 ... fixture_sha=7ab7c3d85a81
b769bfb round-39: freeze — ... fixture_sha=c142c1bc28b8
```

So the control *is* reconcilable to a commit — but only by scanning history, because the SUMMARY
carries a bare worktree hash and no revision (finding H1).

### 1.3 What the legs actually assert (counter line refs)

| leg | assertion (source line) |
|---|---|
| L1 | `new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr` and `not old_has` (189–192) |
| L2 | same predicate, `--rev` = a **blob id of `corpus/SOURCES.md` at `--base-rev`** (197, 200) |
| L3 | `new_p.returncode == 2 and old_p.returncode == 2` for `--register-rev 000…0` (210) |
| L4 | observed class for ENOENT / EACCES ∈ docstring classes, and that class's *first* line contains `missing` (lowercased) / `EACCES` (case-sensitive) (226–231) |
| L5 | fixture from `lane_root_of(args)` (**worktree**, 237) → `cases==8 and fail==0 and rc==0` on new, `fail>=2` on old (243–246) |
| L6 | five consumer fixtures from the **worktree**, `green = cases==pass and fail==0`, `harm` if `new_pass < old_pass` (265–269) |
| exit | `0 if passed == len(legs) and harm == 0 else 1` (282) |

## 2. Method (cheapest-wrong-implementation search)

Every probe ran the **real counter bytes** (`census/round-39/c2-counter.py`, worktree copy) against
a synthetic fixture repo under my scratch, because the counter needs two revisions in *one* repo:

```
$ D=/fast/scratch/hyaku/souji-r39/W1RevC2Legs/D2
$ git -C "$D" init -q -b main
$ git -C "$D" rev-parse --show-toplevel
TOPOLEVEL OK /fast/scratch/hyaku/souji-r39/W1RevC2Legs/D2
```

`D2` gets commit 1 = the lane **base** bytes of both tools (+ register, corpus, consumers), commit 2
= the lane **tip** bytes of all 11 files, then one **stub** commit per variant (each variant re-based
on lane tip bytes first, so no variant inherits another's defect — the first harness run had a
re-base bug, was fixed, and every number below is from the fixed run):

```
$ python3 -B harness2.py
    land ed30b7f5b779 wrote 9/11 (absent at rev: ['census/round-39/c2-counter.py', 'tests/fixtures/r39-citation-rev.py'])
    land d4c17557b92f wrote 11/11 (absent at rev: [])
```

Fidelity: with the real tip bytes in `D`, the counter prints the same six `PASS` lines and
`SUMMARY legs=6 pass=6 fail=0 harm=0` (harness `V0`), i.e. the synthetic repo reproduces the lane
reading.

## 3. Leg-by-leg results

### L1 — unresolvable `--rev` → rc 2 + `REFUSAL REV-UNRESOLVED`

- **Cheapest satisfiers found (all PASS L1):**
  - a tool that refuses *every* input: `sys.stderr.write('REFUSAL REV-UNRESOLVED: nope\n'); sys.exit(2)`
    → `LEG L1 PASS new rc=2 class=True old rc=1 class=False` (V1);
  - a tool that refuses every `--register-rev` (so L1's *valid* `register_rev=args.rev` is refused
    and the refusal happens to be rc 2 + token) → `LEG L1 PASS` (A);
  - a tool whose refusal **names the wrong flag** (`"--register-rev %s" % args.rev`) → `LEG L1 PASS`
    and the whole predicate passes (B).
- **Discriminating property actually checked:** exit status 2 **and** the token in stderr, on the
  base arm absent. Nothing binds the token to the flag or the value; nothing checks that the
  register was not read.
- **What it does not discriminate:** *resolution* vs *some refusal*. See V2 (ancestor-based
  resolver, 6/6) and §4 H2.
- **Token without rc 2 satisfies nothing** (the task's question): a tool that prints
  `REFUSAL REV-UNRESOLVED: token only` and `sys.exit(1)` gives
  `LEG L1 FAIL new rc=1 class=True old rc=1 class=False` and `SUMMARY legs=6 pass=1 fail=5 harm=3`
  (V7). The `returncode == 2` conjunct is load-bearing.

**Verdict L1:** verified, but non-discriminating in three directions (unconditional refusal, wrong
flag, refusal of another flag's value).

### L2 — `--rev` naming a blob

- **Cheapest satisfier:** the unconditional exit-2 stub → `LEG L2 PASS` (V1); wrong-flag stub →
  `LEG L2 PASS` (B); ancestor-resolver stub → `LEG L2 PASS` (V2).
- **Discriminating property that does work:** `^{commit}` vs `^{object}`. Replacing the gate with
  `cat-file -e <rev>^{object}` (V3) gives
  `LEG L2 FAIL new rc=1 class=False old rc=1 class=False` and `LEG L5 FAIL new=(8, 6, 2, 1)`
  — the fixture's `rev-blob` and `rev-tree` cases catch it. L2 is the one leg whose object class is
  pinned by the fixture rather than by the token.
- Fail-safe: the blob comes from `--base-rev:corpus/SOURCES.md` and the leg requires `bool(blob)`.

**Verdict L2:** verified and genuinely discriminating for commit-vs-object; not discriminating for
"refuses something" vs "resolves".

### L3 — harm leg: unresolvable `--register-rev` stays rc 2

- **Cheapest satisfier: any tool that exits 2 on that input.** The unconditional exit-2 stub passes
  (`LEG L3 PASS new rc=2 old rc=2`, V1). A tool that refuses **every** `--register-rev`, valid or
  not, also passes L3 (A) — and L3 is the *only* leg that is supposed to police `--register-rev`.
- L3 checks the exit code only: not the class token, not that a **valid** `--register-rev` is
  accepted, not that the refusal precedes the register read.
- The harm that A represents (refusing a valid `--register-rev`) is caught only downstream: L5
  `new=(8, 7, 1, 1)` (the `register-absent` case) and L6 `r37-citation=15/16`, `r38-citation-commit=13/14`,
  `harm=2`.
- L3 passes in the do-nothing state too (§1.2), so it is non-discriminating by design.

**Verdict L3:** verified, but it is a two-revision rc equality, not a contract check; a stub that
refuses every `--register-rev` satisfies it outright.

### L4 — drift docstring RECORD-MISSING / RECORD-MALFORMED mapping

- **Cheapest satisfier: a docstring-only edit.** Base tool bytes + a docstring whose two class
  lines each name both triggers pass:
  `LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False`
  → `SUMMARY legs=6 pass=6 fail=0 harm=0` (C). No behaviour changed; the R10 ambiguity (both
  classes claim both triggers) survives, and L4 cannot see it.
- L4 is a token-presence check on the **first** docstring line starting with the observed class
  (141–146): `missing` is matched case-insensitively, `EACCES` case-sensitively; the class *name*
  is treated as an arbitrary label (an inverted mapping with a matching docstring would pass).
- Two documented claims are never probed: `ELOOP` and "non-regular record path". Today they hold —
  `REFUSAL RECORD-MISSING: [Errno 40] Too many levels of symbolic links: '.../loop.tsv'` and
  `REFUSAL RECORD-MALFORMED: .../dir-record is not a regular file` (G) — but a regression in either
  would still print `pass=6`.
- **Residual defect the leg cannot see:** the tip bytes still emit a **false diagnosis** for a
  mistyped path — `REFUSAL RECORD-MALFORMED: /.../no-such-record.tsv is not a regular file`
  (rc 2) — i.e. the message R10 quoted survives the repair; only the docstring's class mapping was
  made honest. `RECORD-MISSING: [Errno 13] Permission denied: ...` for EACCES is fine.

**Verdict L4:** verified for the two probed triggers; it certifies "docstring self-consistent with
observed class", not "the diagnosis is true". It is satisfied by documentation alone.

### L5 — `tests/fixtures/r39-citation-rev.py` (8 cases) discriminates

- **Cheapest satisfier 1 — a fixture that never runs the tool.** A worktree fixture that greps the
  tool source for `REFUSAL REV-UNRESOLVED` and prints `cases=8 pass=8 fail=0` / `pass=6 fail=2`
  accordingly gives `LEG L5 PASS new=(8, 8, 0, 0) old=(8, 6, 2, 1)` → 6/6 (F). No case exercises
  the tool's behaviour; the only requirement is the pass/fail counts.
- **Cheapest satisfier 2 — uncommitted fixture bytes.** The fixture is read from
  `lane_root_of(args)` = `os.path.abspath(--root)` (237), and `fixture_sha` is computed from the
  same worktree file (170). Committing a forgery (`print('SUMMARY cases=8 pass=8 fail=0')`) while
  leaving the real fixture in the worktree gives
  `LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)` → 6/6 (E). The committed fixture was never read.
- **What it does discriminate:** an exit-2-always tool (`new=(8, 4, 4, 1)` → `LEG L5 FAIL`, V1) and
  an object-accepting gate (`new=(8, 6, 2, 1)` → FAIL, V3); the `clean` case (rc 0) and
  `register-absent` (rc 2 + `not at`) are the load-bearing positives. `cases==8` is pinned, so the
  case count cannot silently shrink.

**Verdict L5:** verified on the current worktree; the leg binds neither the fixture's *bytes* to
`--rev` nor its *cases* to runtime behaviour.

### L6 — five consumer fixtures green, no pass-count drop

- **Cheapest satisfier 1 — gut a consumer.** `tests/fixtures/r37-citation-reconcile.py` replaced in
  the **worktree** by `print('SUMMARY cases=1 pass=1 fail=0')`:
  `LEG L6 PASS ... r37-citation=1/1(base 1/1) ...` → 6/6, `harm=0` (D). Harm compares the *same*
  gutted fixture against both tools, so weakening is invisible.
- **Cheapest satisfier 2 — zero cases.** `print('SUMMARY cases=0 pass=0 fail=0')`:
  `LEG L6 PASS ... r37-citation=0/0(base 0/0) ...` → `SUMMARY legs=6 pass=6 fail=0 harm=0` (Z).
  `green = cases == pass and fail == 0` is satisfied by `0 == 0`.
- **What it does discriminate:** tool-caused regressions on the *same* fixture bytes — the
  exit-2-always stub (`r37-citation=0/16`, `r38-citation-commit=0/14`, `harm=2`, V1) and the
  always-refuse-`--register-rev` stub (`15/16`, `13/14`, `harm=2`, A).
- Fixtures are worktree bytes here too (D and Z pass with committed bytes untouched).

**Verdict L6:** verified, but it protects the *tools*, not the consumers' coverage; the consumer
suite can be emptied or uncommitted and the leg stays green.

## 4. Findings by severity

### H1 (HIGH, operability/reproducibility) — L5/L6 and the counter itself are worktree-bound

`--rev` selects only the two **tool** blobs (`extract()` → `git show`). The counter (237), both
fixtures, and the five consumers are read from the worktree, and `fixture_sha` (170) is a worktree
hash with no revision label. Consequence: the frozen predicate `SUMMARY legs=6 pass=6 fail=0
harm=0` can be produced from uncommitted bytes (E, F, D, Z), while the claim's L5/L6 name the
*committed* fixture. Contrast C1's counter, which audits every item with `git show <rev>:...`.
The control receipt only reconciles by scanning history (`c142c1bc28b8` = fixture at `b769bfb`).
This is declared in the counter's docstring ("Instrument (fixture) bytes come from the working
tree") but not in the claim, and it is not what an `--rev` receipt implies.

### H2 (HIGH, calibration) — an ancestor-based resolver passes all six legs

Stub: `--rev` gate replaced by `merge-base --is-ancestor <rev> HEAD` (a one-line reuse of the
tool's own `is_ancestor` helper, line 205–206):

```
LEG L1 PASS ... L2 PASS ... L3 PASS ... L4 PASS ...
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS ...
SUMMARY legs=6 pass=6 fail=0 harm=0  (rc 0, tool_sha=68e4833b808f/...)
```

That is the R11 conflation (`merge-base` collapse) re-entering through the front door. The tip
bytes behave correctly on the same input, and the stub does not:

```
$ (repo: c1=826683f, child c2=90b37ba, HEAD=c1, so c2 is NOT an ancestor of HEAD)
$ git -C repo merge-base --is-ancestor 90b37ba HEAD ; echo rc=$?
rc=1
$ python3 -B tools/souji-citation-reconcile.py --root repo --rev 90b37ba... --register reg.tsv
SUMMARY cells=1 mismatches=0        # tip rc=0
$ python3 -B <ancestor-resolver stub> --root repo --rev 90b37bab...
REFUSAL REV-UNRESOLVED: --rev 90b37bab40cc14b5533a4a878bb819f7993240d3 does not resolve to a commit
                                    # stub rc=2
$ python3 -B <base bytes> --root repo --rev 90b37bab...
SUMMARY cells=1 mismatches=0        # base rc=0 (so the proposed case is base-passing)
```

### M1 (MEDIUM, coverage) — L6 green at zero cases

`cases=0 pass=0 fail=0` is green and harm-free (Z). The leg should require a positive case count per
consumer and pin it to the base reading (the base reading is printed but only compared as `>=`).

### M2 (MEDIUM, calibration) — L1/L2/L3 do not bind the refusal to the flag or the value

V1 (refuse everything) passes L1/L2/L3. A (refuse every `--register-rev`) passes L1/L2/L3. B
(refusal diagnostic naming `--register-rev` for an unresolvable `--rev`) passes **all six legs**:

```
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
SUMMARY legs=6 pass=6 fail=0 harm=0   (tool_sha=b8300f6217af/...)
```

The fixture's `rev-unknown`/`register-rev-gone` cases assert only the token, so the fixture shares
the gap. A tool that tells an operator the wrong flag is broken is operability-negative and fully
green.

### M3 (MEDIUM, operability) — L4 certifies the docstring, not the diagnosis

C shows base behaviour + an ambiguous docstring passing 6/6. Independently, the tip bytes still
print `RECORD-MALFORMED: <path> is not a regular file` for a **nonexistent** path (the exact
message R10 quoted), and no leg reads message text. `ELOOP` and "non-regular" are unprobed claims
(they hold today, G).

### L1 (LOW) — L4's `classify()` token priority

`classify()` returns the first token present in MISSING → MALFORMED → EMPTY → OUTSIDE-ROOT order
(127–130), so a tool that prints two class tokens is classified by tuple order, not by its exit
path. No probe can distinguish that today; note it as a latent misclassification.

### L2 (LOW) — receipt carries no interpreter identity

The counter spawns `python3` from `PATH` (not `sys.executable`) for both arms, and the SUMMARY
records only `tool_sha`/`fixture_sha` — no `python3 -V`, no `git --version`. "One canonical
runtime" is therefore not attested by the receipt, only by convention.

## 5. Proposed extra case (one, closes the widest gap = H2)

`rev-descendant` — a commit that **exists** but is **not an ancestor** of the repo's HEAD.

Sketch in `tests/fixtures/r39-citation-rev.py::build`/`main` (2 lines of setup, 1 case):

```python
# in build(), after `rev` is read:
child = sh(["git", "-C", repo, "commit-tree", "HEAD^{tree}", "-p", rev, "-m", "child"]).stdout.strip()
# in main(), with the other cases:
case(tool, repo, register, "rev-descendant", ["--rev", child], 0, ["mismatches=0"], results)
```

Measured behaviour (all three arms, on the probe repo above): tip bytes `rc=0 mismatches=0`;
ancestor-resolver stub `rc=2 REFUSAL REV-UNRESOLVED`; base bytes `rc=0 mismatches=0`.

**Why this is not a claim change.**

- It measures the same frozen property on the same observable: a *resolvable* revision must be
  evaluated, a *non-commit* revision must be refused with exit 2. No new tool, no new axis, no new
  defect class, no new leg.
- It is **base-passing**, so it cannot move the base-arm control (`pass=2 fail=4` stays) and cannot
  weaken the discrimination floor (`old_f[2] >= 2`, currently 4).
- It touches no kill rule: `legs=6 pass=6 fail=0 harm=0` and the base-arm clause are unchanged.
- The only literal it moves is L5's case-count `8` (counter line 245 and the claim's parenthetical
  "(8 cases)"). That is the tighter-only bookkeeping amendment class of **A1**, which changed a
  case's expected class without touching any predicate. If the integrator will not move any
  literal, the same power is available with **zero** amendment: create the child commit in
  `build()` and add the second assertion inside the existing `clean` case, leaving `cases=8`.

## 6. Residual risk and verification gaps (not closed by the proposal)

- H1 (worktree binding) is not closed by `rev-descendant`; it needs the counter to read the fixture
  and consumers from `git show <rev>:...` and to print a revision-labelled `fixture_sha`.
- M2 (flag/value binding) is not closed by `rev-descendant`; it needs the case (or the leg) to
  assert the flag name in the diagnostic and to use a *valid* `--register-rev` in a positive case.
- M1 (zero-case green) and M3 (message text) are separate fixes: a positive `cases` floor per
  consumer, and a message-text assertion for ENOENT.
- I did not test the counter's behaviour under a symlinked `--root`, a read-only worktree, or a
  `--scratch` on another filesystem; I did not re-derive C1/C3.
- Every stub here is a *wrong implementation*, not a forged receipt: I did not test whether a
  receipt file can be hand-written to match a SUMMARY line (out of scope for this seat).

## 7. Command log (exact, in order)

1. `wc -l` on the four C2 files; `git log --oneline -6`; `git status --porcelain`.
2. `read` of `census/round-39/preregistration.txt`, `census/round-39/c2-counter.py` (1–133,
   130–286), `tests/fixtures/r39-citation-rev.py` (1–128).
3. `git rev-parse HEAD`; `git diff --stat HEAD -- <tools/counter/fixture>` (empty);
   counter at `--rev 2201778… --base-rev ed30b7f5…` (§1.1).
4. `grep -n "REV-UNRESOLVED|def main|cat-file|mismatches=" tools/souji-citation-reconcile.py`;
   `sed -n '1,60p' tools/souji-worktree-drift.py`.
5. `git show ed30b7f5…:tools/souji-citation-reconcile.py | sed -n '/def main/,/rows =/p'`;
   `git show ed30b7f5…:tools/souji-worktree-drift.py | grep -n "RECORD-MISSING\|RECORD-MALFORMED"`;
   `ls -la census/round-38/cells.tsv corpus/SOURCES.md`.
6. base-vs-tip grep for `is-ancestor|cat-file|REV-UNRESOLVED`.
7. `git show ed30b7f5…:tools/souji-worktree-drift.py | sed -n '40,50p' | cat -A`.
8. `sed -n '120,145p' tools/souji-worktree-drift.py`; `sed -n '104,128p' tests/fixtures/r39-citation-rev.py`.
9. `python3 -B harness.py` (V0–V6b; V4/V6a/V6b superseded by the isolated run; V0/V1/V2/V3/V5 quoted
   from it).
10. `python3 -B harness2.py` (A, B, C, D, E, F, Z, G, H — all isolated; first run discarded for the
    re-base bug, fixed and re-run).
11. `python3 -B tools/souji-worktree-drift.py --root <lane> --record <absent>` → false
    "is not a regular file"; same with a `chmod 000` record → `RECORD-MISSING … Permission denied`;
    `id -u` → `1000`.
12. `cat census/round-39/records/c2-before.txt`; counter at `--rev ed30b7f5… --base-rev ed30b7f5…`.
13. `for c in $(git log --format=%H -8 -- …); do git show $c:tests/fixtures/r39-citation-rev.py |
    sha256sum; done`; `sha256sum tests/fixtures/r39-citation-rev.py`.
14. `git log --oneline -5`; `git rev-parse HEAD`; counter at `--rev d4c1755…`.
15. `git init -q -b main repo` in `anc/`, `commit-tree` child, `update-ref` back to the parent,
    `merge-base --is-ancestor` (rc 1), tip tool (rc 0), ancestor stub (rc 2), base tool (rc 0).
16. Token-but-exit-1 stub through the counter → `LEG L1 FAIL new rc=1 class=True`;
    `python3 -V` → `Python 3.14.8`; `git --version` → `git version 2.56.0`.

Scratch `/fast/scratch/hyaku/souji-r39/W1RevC2Legs/` (≈ a few MB: `D/`, `D2/`, `anc/`, harnesses,
`tmp2/`) is **still on disk** for the L1 to re-run; nothing was written outside the lane's report
path and that scratch root.
