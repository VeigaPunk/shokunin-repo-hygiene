# R40connector57 — the C3 counter has no arm for "base fixture × pristine candidate tool"

Seat: connector. Item: R40connector57 (wave 1, round 40). Judged axis: **coverage**.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Frozen claim attacked: `census/round-40/preregistration.txt:11` → **C3**.
Scratch: `/fast/scratch/hyaku/souji-r40/R40connector57` (removed before yield, §10).
No commit, no push, no mutating git/jj. **No lane file written other than this report.**
Seat rule honoured: every fixture `git` command used `git -C <fixture dir>` and asserted
`git rev-parse --show-toplevel` equals that dir before the commit (`r40-fixture.py:47-51`).

> **Timing note (material).** The r40 instruments landed at commit `128e412b0ced` *while this
> seat was measuring*. This report was rewritten against the landed instrument. Two of the
> three measures this seat originally proposed were adopted in that commit by wave-1 seat
> **R40reviewer18**; the third — the subject of this report — was not. §3.1 records what
> landed and §3.2 records what did not.

---

## 0. Named distinct edge case (item 57)

> **The r40 C3 counter measures its base arm as `BASE fixture × MUTANT tool`. There is no
> arm `BASE fixture × PRISTINE candidate tool`.** Consequently `base_killed` is a
> **compound** signal: it means *"the base fixture rejects this mutant"* **or** *"the base
> fixture is already red against the candidate tool and this mutant inherited that redness"* —
> and the counter cannot tell the two apart. `--base-rev` is validated for resolvability
> (`census/round-40/c3-counter.py:133`) and then **never used again**: the counter has no
> notion of a base *tool* at all, only a base *fixture*.

This is distinct from the four sibling connectors' edges, which are all *inside* the
candidate-fixture leg or about *which file* is the base fixture:

| sibling | edge | mine (57) |
|---|---|---|
| R40connector09 | base-fixture reading matrix; r39-battery retention; TOTAL-row contract stability | **the counter has no cell comparing the base fixture to the pristine candidate tool**, so `base_killed` is compound |
| R40connector21 | crash-gate misattribution inside `score()` | corroborates the same `score()` defect from the tool-raises side |
| R40connector33 | base-arm asymmetry (which file is "the base fixture") | **the two readings are not the whole defect: the *cell* is missing, so `base_killed` loses its meaning** |
| R40connector45 | crash detector on the tool's traceback; `text=True` kills the fixture | same `score()` defect family |
| R40reviewer18 | the `score()` crash probe (F1–F4) — **landed** in `128e412` | I measure what that repair did **not** fix: the base-arm cell |

---

## 1. Verdict

**C3 is not falsified. The landed C3 receipt is correct — and the measurement that produced
it is still one cell short of what the claim asserts.**

- The three named branches are genuinely uncovered and the landed battery kills all four
  mutants; the landed receipt is
  `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8`, exit 0 (§3.1).
- **At HEAD the verdict is correct**: the r40 round did **not** change the tool
  (`tool_sha=e48ed08e6728` == the r39 base tool sha), so the base fixture is green against
  the pristine candidate tool and there is nothing to regress.
- **But the counter would not know that.** The gap is **latent, not active**: it activates
  the moment a candidate revision changes the tool. Then:
  - `base_killed` flips from `0` to `N` **without any mutant's defect having changed** —
    measured: all four landed mutants are `base_killed=no` on the unchanged tool and
    `base_killed=yes` on a contract-changing tool (§3.4). The same mutants, opposite verdicts.
  - The counter then exits 1 with `base_killed=N`, and the receipt reads as *"the base
    fixture catches these mutants"* — which is **false**: the base fixture is already red
    against the pristine candidate tool, and the mutants merely inherited that redness.
  - The operator's available responses are then wrong: *shrink the battery* or *change the
    base fixture* — when the actual defect is in the **candidate tool**.

**Verdict: the frozen C3 predicate's "all mutants survive the r39 base fixture" arm is
not decidable from the receipt as printed.** The counter needs one more cell. This is a
**latent instrument defect**, honestly labelled: it does not affect the landed r40 receipt,
which is correct.

---

## 2. Evidence pointers (committed artifacts)

Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`. Base revision
`0242085909fb6a4ee041c5443d76316ac6d59d4b` (r39 verified tip); r40 instruments at
`128e412b0ced`.

| pointer | what it shows |
|---|---|
| `census/round-40/preregistration.txt:11` | the frozen C3 predicate (three arms) |
| `census/round-40/c3-counter.py:196` | `base_killed, base_detail, _ = score(base_fixture, path, scratch)` — **base arm = base fixture × MUTANT tool** |
| `census/round-40/c3-counter.py:130` | `--base-fixture` default = `tests/fixtures/r39-drift-record-rules.py` |
| `census/round-40/c3-counter.py:133` | `--base-rev` is **validated for resolvability and then never used** |
| `census/round-40/c3-counter.py:115` | `crash = "Traceback (most recent call last)" in proc.stderr` — **the landed repair** (fixture's stderr only) |
| `census/round-40/c3-counter.py:144-146` | tool **and** fixtures now all bound to `--rev` via `git_show` — **the landed repair** |
| `census/round-40/c3-counter.py:182,202` | the `SUMMARY … base_killed=%d` line |
| `census/round-40/c3-counter.py:205` | the exit rule `return 0 if killed_n == len(results) and base_n == 0 else 1` |
| `census/round-40/c3-counter.py:61-71` | the landed battery M15–M18 and its anchors |
| `tests/fixtures/r40-drift-record-branches.py:100-124` | the landed candidate fixture's 8 cases |
| `tests/fixtures/r39-drift-record-rules.py:92-93` | `total-before-rows` case: `TOTAL + ROWS` ⇒ **rc 0** — pins the TOTAL-order contract |
| `tests/fixtures/r38-drift-record.py` | has **no** TOTAL-order case (grep `total-before`/`TOTAL + ROWS` ⇒ empty) |
| `tools/souji-worktree-drift.py:147` | `raw = b"".join(chunks).decode("utf-8", "replace")` — the invalid-UTF-8 branch |
| `tools/souji-worktree-drift.py:155-157` | the REPO-row branch (where this seat's T3 probe patches) |
| `tools/souji-worktree-drift.py:162-164` | the TOTAL branch: `total = {...}` — **the last TOTAL row silently wins** |
| `tools/souji-worktree-drift.py:166` | the schema refusal `Refusal("RECORD-MALFORMED: line %d does not match the census schema")` |
| `tools/souji-worktree-drift.py:370` | `if not args.skip_unrecorded:` — the `--skip-unrecorded` branch |
| `census/round-39/c3-counter.py:101` | the **pre-repair** crash line: `… in (proc.stdout + proc.stderr)` |
| `census/round-39/c3-counter.py:113` | the **pre-repair** default `--base-fixture` = `tests/fixtures/r38-drift-record.py` |
| `census/round-39/c3-counter.py:178` | the **pre-repair** base arm (same shape) |
| `census/round-39/records/c3-after.txt` | the frozen r39 C3 receipt (reproduced in §3.3) |
| `.ufo/waves/round-40/w1/R40reviewer18.md:22-25` | the wave-1 findings F1–F4 that landed as the `128e412` repair |

### 2.1 the three named branches really are uncovered (corroboration)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ grep -rn "skip-unrecorded" tests/fixtures/
(no output)
$ grep -rn 'xff\|surrogate\|backslashreplace' tests/fixtures/
tests/fixtures/r22-result-oracle.py:89-90            (unrelated fixture)
tests/fixtures/r28-wave-evidence-capture.sh:122,150 (unrelated fixture)
$ grep -n "total-before\|TOTAL + ROWS" tests/fixtures/r38-drift-record.py
(no output)
```
No committed fixture passes `--skip-unrecorded`, none writes an invalid UTF-8 record, and
the r38 fixture has no TOTAL-order case. The C3 premise is sound. **Not my finding** — this
is the corroboration that keeps the rest of the report honest.

---

## 3. Commands actually run, with outputs

### 3.1 the LANDED r40 counter, run as the round would run it

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ export TMPDIR=/fast/scratch/hyaku/souji-r40/R40connector57
$ git rev-parse HEAD
128e412b0ced3c243dc27c3dd3332054a611bc2e
$ python3 -B census/round-40/c3-counter.py --root . --rev 128e412b0ced... \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $TMPDIR
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
rc=0
```
The landed counter's receipt is **GREEN and correct**: all four mutants killed, none base-killed,
pristine ok, 8 cases.

### 3.2 what the `128e412` repair did and did not fix

```
landed r40 c3-counter.py:115   crash = "Traceback (most recent call last)" in proc.stderr
landed r40 c3-counter.py:144   source = git_show(args.root, args.rev, args.tool)
landed r40 c3-counter.py:145   candidate_src = git_show(args.root, args.rev, args.fixture)
landed r40 c3-counter.py:146   base_src = git_show(args.root, args.rev, args.base_fixture)
landed r40 c3-counter.py:130   ap.add_argument("--base-fixture", default="tests/fixtures/r39-drift-record-rules.py")
landed r40 c3-counter.py:196   base_killed, base_detail, _ = score(base_fixture, path, scratch)
landed r40 c3-counter.py:202   print("SUMMARY mutants=%d killed=%d survived=%d pristine=ok base_killed=%d cases=%d "
```
```
$ grep -c "base_pristine" census/round-40/c3-counter.py
0
$ grep -n "base_rev" census/round-40/c3-counter.py
133:    for flag, rev in (("--rev", args.rev), ("--base-rev", args.base_rev)):
```
**Landed** (credit R40reviewer18 F1, and the fixture binding): the crash probe reads the
fixture's **stderr** only; the fixtures are bound to `--rev` via `git_show`; the base fixture
is named explicitly as `tests/fixtures/r39-drift-record-rules.py`; the receipt prints the
failing case names, so a kill is attributable to a case.

**NOT landed — this report's subject:** there is still **no**
`BASE fixture × PRISTINE candidate tool` cell (`base_pristine` occurrences = 0), and
`--base-rev` is still validated-only (`:133`) — the counter still has no base *tool*.

### 3.3 the frozen r39 receipt still reproduces exactly (control)

```
$ python3 -B census/round-39/c3-counter.py --root . \
    --rev 2f6e981a105fc759205767d2a749a5f7d4fd0b8a \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $TMPDIR
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
```
Byte-identical to `census/round-39/records/c3-after.txt`. The instrument is faithful; the
instrument is what is under attack. (Operational limit: the counter resolves
`--fixture`/`--base-fixture` relative to the **CWD**, not `--root`; running it from another
directory raises `FileNotFoundError`. The landed counter binds them via `git_show(root,…)`,
which removes this — §3.2.)

### 3.4 the misattribution, measured on the LANDED instrument

**T3** = the candidate tool refuses a REPO row placed **after** a TOTAL row ("the TOTAL row
must come last"), patched at `tools/souji-worktree-drift.py:155-157`. It is the smallest
plausible r40 refinement of the TOTAL branch that regresses a contract the r39 base fixture
pins.

**ARM D** (base fixture × pristine candidate tool):

```
r39 base fixture  x pristine T0 (tool unchanged)        GREEN  SUMMARY cases=7 pass=7 fail=0
r39 base fixture  x pristine T3 (contract change)       RED    SUMMARY cases=7 pass=6 fail=1
                                                        failing: ['total-before-rows']
landed r40 fixture x pristine T0                       GREEN  SUMMARY cases=8 pass=8 fail=0
landed r40 fixture x pristine T3                       GREEN  SUMMARY cases=8 pass=8 fail=0
r38 fixture        x pristine T3                       GREEN  SUMMARY cases=10 pass=10 fail=0
```

**The landed battery, each mutant applied to the unchanged tool (control) and to T3:**

```
mut   on T0 (control)     on T3 (candidate)
M15   base_killed=no      base_killed=yes
M16   base_killed=no      base_killed=yes
M17   base_killed=no      base_killed=yes
M18   base_killed=no      base_killed=yes
```
**The same four mutants, opposite base verdicts, with no change to any mutant's defect.**
On T0 the base fixture does **not** catch any of them. On T3 it "catches" all four — because
it is *already red against the pristine T3* and each mutant inherited that redness.

### 3.5 the ARM D cell separates the two regimes

```
regime                        base_killed (existing arm)   ARM D (missing arm)
tool unchanged (T0)           base_killed=0                ARM D=GREEN  cases=7 pass=7 fail=0
tool contract-changed (T3)    base_killed=4                ARM D=RED    cases=7 pass=6 fail=1
```
ARM D is the cell that says whether `base_killed` is **earned** (the base fixture really
rejects that mutant) or **inherited** (the base fixture is already red against the candidate
tool). Without it, `base_killed` is ambiguous exactly when it matters.

### 3.6 the disambiguation table — two scenarios, opposite responses

```
K1  WEAK r40 fixture (candidate tool unchanged T0)
    SUMMARY mutants=5 killed=4 survived=1 pristine=ok base_killed=1
    surviving mutant: the TOTAL-position mutant
    ARM D (base fixture x PRISTINE candidate tool) = GREEN  cases=7 pass=7 fail=0
    => correct response: the r40 fixture is too weak; extend it

K2  CONTRACT CHANGE (candidate tool T3; r40 fixture pins the new contract)
    SUMMARY mutants=5 killed=5 survived=0 pristine=ok base_killed=4
    surviving mutant: none
    ARM D (base fixture x PRISTINE candidate tool) = RED    cases=7 pass=6 fail=1
    => correct response: the r40 CANDIDATE TOOL changed a contract the r39 base fixture
       pins; the r40 fixture and the base fixture disagree about the contract
```
Both print a non-zero `base_killed`; the responses are opposite (extend the fixture vs
revert the tool). Without ARM D the receipt cannot tell them apart.

### 3.7 the two readings of "the r39 base fixture" flip in **both** directions

The frozen M7–M14 battery (`tests/fixtures/r38-drift-mutants.py:MUTANTS` +
`census/round-39/c3-counter.py:MUTANTS`; all 8 anchors count = 1), scored with the frozen
r39 `score()`:

```
mut   r40 kills   base r39 rules   base r38 rec   FLIP
M7    yes         survived          KILLED         YES
M8    no          survived          KILLED         YES
M9    no          survived          KILLED         YES
M10   no          survived          KILLED         YES
M11   no          KILLED            survived       YES
M12   no          KILLED            survived       YES
M13   no          KILLED            survived       YES
M14   no          KILLED            survived       YES
```
The two readings disagree on **every** frozen mutant, in opposite directions. This is
sibling R40connector33's asymmetry, reproduced because §3.4 depends on it. **The landed
counter has resolved it** by naming `tests/fixtures/r39-drift-record-rules.py` at `:130` —
the stricter of the two on all eight frozen mutants, and the one whose `total-before-rows`
case gives ARM D teeth.

### 3.8 the branch mutants the inherited contract could not credit (now fixed)

With the **pre-repair** r39 `score()` and the **frozen** r39 fixture file, a mutant that
makes the tool raise instead of refuse is scored a survivor even though the fixture
detected it — `census/round-39/c3-counter.py:101` scans the **fixture's** stdout, and
`tests/fixtures/r39-drift-record-rules.py:80` echoes the **tool's** stdout+stderr into it:

```
frozen r39 fixture vs a tool that raises: rc=1
  per-case: trailing-space FAIL, indented-comment FAIL, others PASS
  fixture's own summary: SUMMARY cases=7 pass=5 fail=2
  traceback text present in FIXTURE stdout? True
  inherited score(): killed=no   rc=1 fails=2 crash=True
```
This is the invalid-UTF-8 branch's natural mutant (strict decode ⇒ the tool raises), and it
is why the landed repair matters. **Landed** (`census/round-40/c3-counter.py:115`), verified
a **no-op** on the frozen M11–M14 battery:
```
mut   frozen killed            fixed killed             identical?
M11   KILLED rc=1 fails=1 crash=False  KILLED rc=1 fails=1 crash=False  YES
M12   KILLED rc=1 fails=1 crash=False  KILLED rc=1 fails=1 crash=False  YES
M13   KILLED rc=1 fails=1 crash=False  KILLED rc=1 fails=1 crash=False  YES
M14   KILLED rc=1 fails=1 crash=False  KILLED rc=1 fails=1 crash=False  YES
```
and it credits the tool-raising mutant while still refusing a fixture-side crash:
```
D2  strict decode -> TOOL raises        frozen=survived crash=True   fixed=KILLED crash=False
D4  surrogateescape -> FIXTURE raises   frozen=survived NO-SUMMARY    fixed=survived NO-SUMMARY
```
Credit R40reviewer18 F1/F4 for this; reproduced here because it bounds which mutants are
admissible and because the same reasoning exposes the *remaining* gap (§3.4).

### 3.9 the invalid-UTF-8 branch's ground truth, and a locale hazard

`tools/souji-worktree-drift.py:147` decodes with `errors="replace"`, so an invalid byte
becomes **U+FFFD** and the record still parses:
```
stdout-bytes=b'DRIFT\tABSENT\tal\xef\xbf\xbdpha\trecorded regs=1\nSUMMARY ...'
```
A fixture asserting the *verdict* (`ABSENT`) cannot discriminate the decode handler; one
asserting the **content** can (D3 `backslashreplace` survives a verdict-only assertion and is
killed by a content-asserting one). The landed fixture asserts the verdict
(`invalid-utf8-in-repo-name` ⇒ `ABSENT`), which is why M17 (`ignore`) is the admissible
mutant and not a strict-decode mutant. **This is a fixture-design choice, not a defect**, and
it is the landed round's call.

Locale hazard the counter does not pin: `child_env()` scrubs `PYTHON*` but sets `LC_ALL=C`.
```
counter child_env                                          -> stdout=utf-8 preferred=utf-8
counter child_env + PYTHONCOERCECLOCALE=0                  -> stdout=utf-8 preferred=utf-8
counter child_env + PYTHONUTF8=0 + PYTHONCOERCECLOCALE=0   -> stdout=ascii preferred=ANSI_X3.4-1968
```
Under the last configuration the fixture's own capture of the tool's U+FFFD output fails
(`decoding with 'ANSI_X3.4-1968' codec failed`, rc=1, no SUMMARY) and the counter reads
`NO-SUMMARY` — a survivor for a reason unrelated to the mutant. Host locales here:
`C C.utf8 en_US.utf8 POSIX`. The r40 counter should pin `PYTHONUTF8=1` or capture bytes, or
its invalid-UTF-8 branch is host-locale dependent. **This is a live, unlanded gap.**

---

## 4. Affected axes

- **coverage (C3) — directly.** The base arm of the counter is compound; the receipt cannot
  distinguish an earned `base_killed` from an inherited one. **The landed r40 receipt is
  correct** (the round did not change the tool), but the instrument would mis-report the
  moment a candidate revision does.
- **operability (C2) — second-order, benign.** Measured: a duplicate-TOTAL refusal or an
  invalid-UTF-8 refusal keeps **all five** r39 C2 L6 consumer fixtures green on the committed
  base bytes (`r38-drift-record` 10/10, `r36-worktree-drift` 12/12,
  `r38-drift-write-envelope` 12/12, `r37-citation-reconcile` 16/16, `r38-citation-commit`
  14/14). **No C2 harm** from the tool changes C3 implies. The C2 L4 leg reads the tool
  docstring; a new refusal class must be added there, but the *set* of class names is
  unchanged by a duplicate-TOTAL/invalid-UTF-8 refusal (both reuse `RECORD-MALFORMED`).
- **calibration (C1) — unaffected.** C1 reads anchored lane lines and the register.

---

## 5. Proposed move (one move; no aim)

**Add the missing cell to the r40 C3 counter: `BASE fixture × PRISTINE candidate tool`.**
Concretely, before the battery:

```
ARM D  base_fixture × pristine_candidate_tool  ->  must be rc=0
```
and print it in the `SUMMARY` line, e.g. `base_pristine=ok` / `base_pristine=FAIL`. This
turns `base_killed` from a compound signal into an interpretable one and gives the receipt a
statement about **non-regression**, not only about kill counts.

Two sub-measures, both bounded, neither touching the frozen claim text:

1. **Add ARM D** (one extra subprocess run, before the battery). Fail the run if it is not
   rc=0. This is the same shape as the existing `pristine` arm (`c3-counter.py:146`), applied
   to the *base* fixture instead of the candidate one.
2. **Pin `PYTHONUTF8=1`** in `child_env()` (or have the fixture capture bytes and decode
   explicitly). §3.9: today the invalid-UTF-8 branch's verdict depends on the host's PEP 538
   coercion availability, which the counter does not control.

**Not proposed, deliberately:** changing the crash probe or the fixture byte-binding — both
were proposed by this seat and **both landed** in `128e412` (§3.2). Also not proposed:
renaming the base fixture — the landed counter already names it (`:130`), and §3.7 shows that
naming is the right choice.

---

## 6. Risks and limits

- **This is not a falsification of C3.** The three named branches are real and covered; the
  landed receipt is GREEN and correct. **The defect is latent**: it activates only when a
  candidate revision changes the tool. Reported honestly, not inflated.
- **T3 is a constructed candidate tool**, not a proposed r40 change. It is the smallest
  change that (a) is a plausible r40 refinement of the TOTAL branch and (b) regresses a
  contract the r39 base fixture pins. A real r40 tool change might be contract-preserving;
  the counter gap exists regardless, and ARM D detects it either way.
- **`base_killed` semantics.** I assert `base_killed` is *ambiguous* — not wrong — in the
  regime where the base fixture is already red against the pristine candidate tool. §3.4
  measures the flip with a control (the same mutants on the unchanged tool). The claim is
  about ambiguity, not about a wrong number in the landed regime.
- **The landed r40 counter was written by another seat and I am not proposing to rewrite
  it.** The proposal is one added cell and one env var, both in `census/round-40/c3-counter.py`
  — the L1's file, not mine. This report writes **no** lane file.
- **Scratch-only.** Every measurement ran on scratch copies of the committed tool bytes
  (`git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py`,
  sha256 `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`) and scratch
  fixtures. The working tree is clean; `git status --porcelain` → empty. Only this report
  (`.ufo/waves/…`, gitignored) was written.
- **Tooling.** No installs. `python3` 3.14 only; `git`, `grep`, `sed` from the base system.
  No `pacman`, no `uv tool install`, no network. **No package was installed or updated.**
- **Counter `--fixture` paths.** The r39 counter resolved them against the CWD; the landed
  r40 counter binds them via `git_show(root, …)` and so is CWD-independent. Noted for
  completeness; no action needed.

---

## 7. Verification the main agent / L1 should run

1. Reproduce §3.1 (the landed r40 receipt) — must be
   `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8`, exit 0.
2. Reproduce §3.3 (the frozen r39 receipt) — must be byte-identical to
   `census/round-39/records/c3-after.txt`.
3. Reproduce §3.4: apply the landed M15–M18 to (a) the committed tool and (b) the T3 probe;
   the base verdict must flip `no`→`yes` for all four with no change to the mutants.
4. Reproduce §3.5: fill ARM D and confirm it is GREEN for T0 and RED for T3.
5. After the proposed change: re-run step 1 and confirm the `SUMMARY` line carries
   `base_pristine=`, and that step 1's numbers are **unchanged** (ARM D is GREEN at HEAD, so
   `base_killed=0` must still hold).
6. Confirm the locale fix: run the counter with `PYTHONUTF8=0 PYTHONCOERCECLOCALE=0` in the
   environment and confirm the invalid-UTF-8 case still resolves deterministically.

---

## 8. Affected axes, proposed move, risks, verification (summary)

| axis | effect |
|---|---|
| **coverage (C3)** | the base arm is compound; ARM D missing; **landed receipt correct**, gap latent |
| operability (C2) | **no harm** — all five L6 consumers green under both plausible tool changes |
| calibration (C1) | unaffected |

**Move:** add `BASE fixture × PRISTINE candidate tool` as a fourth counter cell
(`base_pristine=`), and pin `PYTHONUTF8=1` in `child_env()`. One cell, one env var, no
change to the frozen claim.

**Risk:** the proposal touches `census/round-40/c3-counter.py`, which is the L1's file. It is
a **measurement** change only; it cannot change whether C3's *branch* claims hold, only
whether the receipt can be read correctly.

**Verification:** §7, six steps, all runnable from the lane root with the committed bytes.

---

## 9. Scratch inventory and cleanup

```
/fast/scratch/hyaku/souji-r40/R40connector57/
  pristine.py, mut-*.py, p3-*.py … p15-*.py     (scratch tool/fixture variants)
  r40-fixture.py                    candidate r40 fixture (7 cases) — a MEASUREMENT artefact
  p4-quiet.py p6-content-fixture.py p11-f-new.py p12-f-new.py …
  harness.py probe2.py … probe15.py
```
All removed before yield. The scratch `r40-fixture.py` is a **measurement artefact, not a
proposed lane file** — the landed `tests/fixtures/r40-drift-record-branches.py` is the
round's own fixture and is not superseded by it.

---

## 10. Cleanup confirmation

Scratch removed after the measurements above were captured; no `git`/`jj` mutation was
performed at any point; the lane working tree is clean (`git status --porcelain` → empty);
the only file this seat wrote in the lane is this report.
