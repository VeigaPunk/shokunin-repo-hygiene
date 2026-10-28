# W1ExecScratch — scratch discipline of the round-39 instruments (r39 C1/C2/C3)

Seat: executor, item W1ExecScratch. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
(lane HEAD at audit time `2201778e7736af82e7d8a42dec2494f115bf3923`; frozen base
`ed30b7f5b77939c9073348d810730bc4f355708d` resolves: `cat-file -e ...^{commit}` → exit 0).
Scratch root used for every run:
`/fast/scratch/hyaku/souji-r39/W1ExecScratch` (`probe/`, `env/`, `work/`, `relprobe/`, `repo-empty/`,
`repo-bare/`). No tool installed, no git/jj mutation, no write outside this report and my scratch.

Audited instruments (worktree bytes at lane HEAD):

| instrument | sha256 (12) | bytes |
|---|---|---|
| `census/round-39/c1-counter.py` | `d892b74f8358` is the items sha it prints, not the file sha — see note N1 | 10470 |
| `census/round-39/c2-counter.py` | — | 12557 |
| `census/round-39/c3-counter.py` | — | 8374 |
| `tests/fixtures/r39-citation-rev.py` | `7ab7c3d85a81` (sha the c2 counter computes) | 5967 |
| `tests/fixtures/r39-drift-record-rules.py` | `567c37a679f5` (sha the c3 counter computes) | 5994 |

N1: the counters print `items_sha` / `fixture_sha` / `tool_sha` (content digests of their inputs), not
their own file digest; I therefore did not fabricate a file sha for c1/c2/c3.

---

## 1. Static grep — exact command and output

Command (run from the lane root):

```
for f in census/round-39/c1-counter.py census/round-39/c2-counter.py census/round-39/c3-counter.py \
         tests/fixtures/r39-citation-rev.py tests/fixtures/r39-drift-record-rules.py; do
  echo "== $f"; grep -nE '/tmp|mkdtemp|TMPDIR|--work|--scratch|shutil\.rmtree|tempfile|atexit|trap|try:|except|finally' "$f"
done
```

Output (line numbers and matched text exact; long env-dict literals condensed to `...` on the
`c1-counter.py:172`, `c3-counter.py:63` and `c2-counter.py:148` lines only):

```
== census/round-39/c1-counter.py
27:      [--register-rev REV] [--min-cells N] [--min-commit-distinct N] [--scratch DIR]
40:import tempfile
172:        env={"PATH": ..., "TMPDIR": scratch},
195:    try:
199:    except ValueError as exc:
203:    scratch = tempfile.mkdtemp(prefix="souji-r39-c1.", dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp")
205:    try:
229:        try:
232:        except ValueError as exc:
237:    finally:
238:        shutil.rmtree(scratch, ignore_errors=True)
259:    ap.add_argument("--scratch")

== census/round-39/c2-counter.py
25:  python3 -B census/round-39/c2-counter.py --root LANE --rev REV --base-rev REV [--scratch DIR]
39:import tempfile
72:        env["TMPDIR"] = scratch
148:    cmd = ["python3", "-B", fixture] + list(extra or ["--tool", tool]) + ["--work", work]
162:    ap.add_argument("--scratch")
171:    base_scratch = tempfile.mkdtemp(
172:        prefix="souji-r39-c2.", dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp")
180:    try:
273:    except (ValueError, OSError) as exc:
276:    finally:
277:        shutil.rmtree(base_scratch, ignore_errors=True)

== census/round-39/c3-counter.py
23:  python3 -B census/round-39/c3-counter.py --root LANE --rev REV --base-rev REV [--scratch DIR]
36:import tempfile
63:    env = {"PATH": ..., "TMPDIR": scratch}
71:        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=child_env("/var/tmp"), check=False,
81:        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=child_env("/var/tmp"),
89:        ["python3", "-B", fixture, "--tool", tool, "--work", work],
113:    ap.add_argument("--scratch")
119:    scratch = tempfile.mkdtemp(prefix="souji-r39-c3.",
120:                               dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp")
121:    try:
141:            ["python3", "-B", candidate, "--tool", pristine_tool, "--work", scratch],
182:    finally:
183:        shutil.rmtree(scratch, ignore_errors=True)

== tests/fixtures/r39-citation-rev.py
22:  python3 -B tests/fixtures/r39-citation-rev.py [--tool PATH] [--work DIR]
30:import tempfile
91:    ap.add_argument("--work")
95:    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
100:        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
102:    scratch = tempfile.mkdtemp(prefix="souji-r39-cite-rev.", dir=work)
104:    try:
117:    finally:
118:        shutil.rmtree(scratch, ignore_errors=True)

== tests/fixtures/r39-drift-record-rules.py
18:  python3 -B tests/fixtures/r39-drift-record-rules.py [--tool PATH] [--work DIR]
26:import tempfile
68:    fd, record = tempfile.mkstemp(prefix="record-", suffix=".tsv", dir=root)
84:    scratch = tempfile.mkdtemp(prefix="souji-r39-record.", dir=work)
86:    try:
94:        fd, crlf = tempfile.mkstemp(prefix="record-crlf-", suffix=".tsv", dir=root)
112:    finally:
113:        shutil.rmtree(scratch, ignore_errors=True)
120:    ap.add_argument("--work")
124:    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
129:        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
```

`grep -rn '/tmp'` over exactly these five files: **no `/tmp` literal**; the only absolute literals are
the three `"/var/tmp"` fallbacks plus the two hardcoded `child_env("/var/tmp")` calls in c3.

```
== /tmp literal occurrences in r39 instruments
census/round-39/c1-counter.py:203: ... or "/var/tmp")
census/round-39/c2-counter.py:172: ... or "/var/tmp")
census/round-39/c3-counter.py:71: ... env=child_env("/var/tmp"), check=False,
census/round-39/c3-counter.py:81: ... env=child_env("/var/tmp"),
census/round-39/c3-counter.py:120: ... or "/var/tmp")
tests/fixtures/r39-citation-rev.py:95: ... or "/var/tmp"
tests/fixtures/r39-drift-record-rules.py:124: ... or "/var/tmp"
```

House pattern check (so the `/var/tmp` fallback is scored as inherited, not new):
`grep -rln '/var/tmp' census/round-3[5-8]/*.py tests/fixtures/r3[5-8]-*.py` lists 13 prior files
(`census/round-35/c1-counter.py`, `c2-counter.py`, `r36-report-gate.py`, `r36-worktree-drift.py`,
`r37-citation-reconcile.py`, `r37-drift-discrimination.py`, `r37-drift-escapes.py`,
`r37-drift-mutants.py`, `r38-citation-commit.py`, `r38-counter-arms.py`, `r38-drift-mutants.py`,
`r38-drift-record.py`, `r38-drift-write-envelope.py`) — identical `args.work or TMPDIR or "/var/tmp"`
chain, and `r38-drift-record.py:135` is the same line as the r39 fixtures'.

### 1.1 Code between `mkdtemp` and `try` (the "exception before the try" question)

Read directly at those line numbers:

- `c1-counter.py`: 203 `mkdtemp` → 204 `open_count = 0` → 205 `try:`.
- `c2-counter.py`: 171-172 `mkdtemp` → 173 `legs = []`, 174 `harm = 0`, 176-178 `def leg(...)` → 180 `try:`.
- `c3-counter.py`: 119-120 `mkdtemp` → 121 `try:`.
- `r39-citation-rev.py`: 102 `mkdtemp` → 103 `results = []` → 104 `try:`.
- `r39-drift-record-rules.py`: 84 `mkdtemp` → 85 `results = []` → 86 `try:`.

`mkdtemp` is the last operation that can fail before the `try` in all five; the statements in between
are assignment/`def` only. The "exception before the try" window is therefore empty (verdict V2
below).

---

## 2. Runtime evidence — every command, quoted output

All runs use `TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecScratch/env` (a *different* directory from
the explicit `--scratch`/`--work`) so the two can be distinguished, and every run is followed by a
leftover sweep.

### T1 — c1 counter, explicit `--scratch`, base rev

```
TMPDIR=$S/env python3 -B $L/census/round-39/c1-counter.py --root $L --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --items $L/census/round-39/c1-items.tsv --register census/round-38/cells.tsv --scratch $S/probe
```
Tail:
```
ITEM R39-C1-16 OPEN ANCHOR-ABSENT corpus/lessons/round-36.md anchor='R39-C1-16'
REGISTER cells=10 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=10 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```
Reproduces the frozen `c1-before` `items=16 open=16` (and shows the r38 register's ten rows all carry
`commit == receipt_rev`: `commit_distinct=0`). Scratch removed; nothing in `$S/probe` or `$S/env`.

### T2 — c1 `--scratch` pointing at a nonexistent directory (does the flag win over TMPDIR?)

```
... --scratch $S/does-not-exist
    _os.mkdir(file, 0o700)
    ~~~~~~~~~^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/fast/scratch/hyaku/souji-r39/W1ExecScratch/does-not-exist/souji-r39-c1.q7mj819h'
rc=1
```
The error names the `--scratch` path although a valid writable `TMPDIR` existed → `--scratch` is
honoured and takes precedence. Exit is 1 with a traceback, not the docstring's exit 2 (finding F5).

### T3 — c1 with a register absent at the rev (REGISTER-ABSENT path)

```
--register census/round-39/c1-items.tsv
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 ... items_sha=d892b74f8358
rc=1
```
No leftovers.

### T4 — c1 with a register that *is* present but malformed → `ValueError` raised inside the `try`

```
--register corpus/SOURCES.md
ITEM R39-C1-16 OPEN ANCHOR-ABSENT corpus/lessons/round-36.md anchor='R39-C1-16'
REFUSAL COULD-NOT-EVALUATE: register row with 1 fields
rc=2
```
Post-`mkdtemp` exception → `finally` ran: `find $S/probe $S/env -maxdepth 1 -name 'souji-r39*'`
printed nothing.

### T5 — c2 counter, base arms (control reproduction)

```
TMPDIR=$S/env python3 -B $L/census/round-39/c2-counter.py --root $L --rev ed30b7f... --base-rev ed30b7f... --scratch $S/probe
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=7ab7c3d85a81
rc=1
```
`pass=2 fail=4` matches `census/round-39/records/c2-before.txt`; the `fixture_sha=7ab7c3d85a81`
matches `c2-after.txt` and differs from the `c2-before` value `c142c1bc28b8` (the L5 case tightened by
amendment A1). `L5 new=(8,4,4,1)` is the current fixture's base-arm reading (receipt `c2-before`
recorded `(8,5,3,1)` on the pre-amendment bytes). No leftovers.

### T6 — c3 counter launched from the fleet root (its fixture paths are CWD-relative)

```
sys.exit(main(sys.argv[1:]))
    candidate_src = open(args.fixture, encoding="utf-8").read()
FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/r39-drift-record-rules.py'
rc=1
```
Traceback with `--root` naming the lane; `finally` still ran (no leftovers). Finding F6.

### T7 — c3 counter from the lane cwd, explicit `--scratch`, base rev for both arms

```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
rc=0
```
`fixture_sha=567c37a679f5` matches `c3-after.txt`. The tool sha is the **base** tool
(`14e9c0f77d7e`), i.e. this rc=0 was produced by base tool bytes + worktree fixture bytes — see
finding F7 (outside my scratch scope, escalation for the L1/critic).

### T8 / T9 — c3 and c2 with a nonexistent `--scratch`

```
FileNotFoundError: [Errno 2] No such file or directory: '/fast/scratch/hyaku/souji-r39/W1ExecScratch/nope/souji-r39-c3.ivmb5z6h'
FileNotFoundError: [Errno 2] No such file or directory: '/fast/scratch/hyaku/souji-r39/W1ExecScratch/nope/souji-r39-c2.xc0qmu64'
```
Both name the `--scratch` root → honoured. Both exit 1 with a traceback (F5).

### T10 / T11 — the two new fixtures with explicit `--work`

```
TMPDIR=$S/env python3 -B $L/tests/fixtures/r39-citation-rev.py --work $S/work
case-rev-unknown=PASS
case-rev-blob=PASS
case-rev-tree=PASS
case-rev-short=PASS
case-rev-symbolic=PASS
case-clean=PASS
case-register-rev-gone=PASS
case-register-absent=PASS
SUMMARY cases=8 pass=8 fail=0
rc=0

TMPDIR=$S/env python3 -B $L/tests/fixtures/r39-drift-record-rules.py --work $S/work
case-good=PASS
case-trailing-space=PASS
case-total-before-rows=PASS
case-crlf=PASS
case-outside-root=PASS
case-indented-comment=PASS
case-comments-total-only=PASS
SUMMARY cases=7 pass=7 fail=0
rc=0
```
No leftovers in `$S/work`; `find /tmp /var/tmp -maxdepth 1 -user vgpnk -newer $S/stamp` printed
nothing → these runs created no system-temp entries.

### T12 — fixtures: `--work` beats a valid `TMPDIR`

```
TMPDIR=$S/env ... r39-citation-rev.py --work $S/no-such-work
usage: --work must name an existing directory (/fast/scratch/hyaku/souji-r39/W1ExecScratch/no-such-work)
rc=2
TMPDIR=$S/env ... r39-drift-record-rules.py --work $S/no-such-work
usage: --work must name an existing directory (/fast/scratch/hyaku/souji-r39/W1ExecScratch/no-such-work)
rc=2
```
`--work` honoured *and* validated (exit 2 as documented) — the fixtures are stricter than the counters.

### T13 — `--work` existing but unwritable (mode 500)

```
PermissionError: [Errno 13] Permission denied: '/fast/scratch/hyaku/souji-r39/W1ExecScratch/ro/souji-r39-record.affgeak9'
rc=1
```
`isdir` passed, `mkdtemp` raised; the fixture's own docstring promises exit 2 for usage (F5).

### T14 — child environment the fixtures hand to the tool they launch

Fake tool `$S/faketool.py` printing `TMPDIR` and `cwd`, invoked by each fixture with
`TMPDIR=$S/env` in the parent and `--work $S/work`:

```
case-rev-unknown=FAIL rc=2 want=2 missing=['REV-UNRESOLVED'] out="CHILD-TMPDIR=None CHILD-CWD='/home/vgpnk/Projects/shokunin/souji-shokunin' "
case-good=FAIL rc=2 want=0 missing=['SUMMARY', 'record_repos=2'] out="CHILD-TMPDIR=None CHILD-CWD='/home/vgpnk/Projects/shokunin/souji-shokunin' "
```
`CHILD-TMPDIR=None` for **both** fixtures: the child env (`ENV` dict, lines 33-44 / 33-44) has no
`TMPDIR`, so the caller's scratch root does not reach the child at all (finding F2). This run also
exercises the all-fail exit path: `rc=1`, `find $S/work -maxdepth 1 -name 'souji-r39*'` → nothing.

### T15 — c2 `ValueError` inside the `try` (scratch repo without `tools/`)

```
toplevel=/fast/scratch/hyaku/souji-r39/W1ExecScratch/repo-empty
rev=f736ac71e1fcd0136f5d231d97312e0a17aa0358
REFUSAL COULD-NOT-EVALUATE: tools/souji-citation-reconcile.py absent at f736ac71e1fcd0136f5d231d97312e0a17aa0358
rc=2
```
Fixture dir `D=$S/repo-empty` created with `git -C "$D" init -q`, and `git -C "$D" rev-parse
--show-toplevel` asserted `= $D` before the first commit. After the refusal:
`find $S/probe -maxdepth 1 -name 'souji-r39*'` → nothing.

### T16 — c2 with the fixture absent from `--root` (open happens *before* `mkdtemp`)

```
FileNotFoundError: [Errno 2] No such file or directory: '/fast/scratch/hyaku/souji-r39/W1ExecScratch/repo-bare/tests/fixtures/r39-citation-rev.py'
rc=1
```
Nothing to clean (no scratch yet) — confirms the pre-`mkdtemp` hash read at c2 lines 169-170 and its
traceback-instead-of-refusal behaviour (F5'). `D2=$S/repo-bare`, `git init -q` with `-C "$D2"` on
every later call, toplevel verified.

### T17 — counters honour `TMPDIR` when `--scratch` is omitted

```
TMPDIR=$S/nope-env  (nonexistent)
c1: FileNotFoundError: ... '/fast/scratch/hyaku/souji-r39/W1ExecScratch/nope-env/souji-r39-c1.w0r1z5lq'
c2: FileNotFoundError: ... '/fast/scratch/hyaku/souji-r39/W1ExecScratch/nope-env/souji-r39-c2.c2ovh7_i'
c3: FileNotFoundError: ... '/fast/scratch/hyaku/souji-r39/W1ExecScratch/nope-env/souji-r39-c3.tr3wwvdq'
fixtures: usage: --work must name an existing directory (/fast/scratch/hyaku/souji-r39/W1ExecScratch/nope-env)
```
Every instrument names the `TMPDIR` value → the environment half of the caller control is real.

### T18 — relative `--work` is resolved against CWD, not `--root`

```
cd $S && TMPDIR=$S/env python3 -B $L/tests/fixtures/r39-drift-record-rules.py --work relprobe
SUMMARY cases=7 pass=7 fail=0      rc=0
find $S/relprobe -maxdepth 1  ->  /fast/scratch/hyaku/souji-r39/W1ExecScratch/relprobe   (scratch child already removed)
```
A relative value is accepted silently (F4); with `--root` naming the lane the two roots diverge.

### T19 — `--scratch` precedence with a read-only `--scratch` and a writable `TMPDIR`

```
--- c1 --- PermissionError: [Errno 13] Permission denied: '/fast/scratch/hyaku/souji-r39/W1ExecScratch/ro2/souji-r39-c1.i7q47r6d'
--- c2 --- PermissionError: [Errno 13] Permission denied: '/fast/scratch/hyaku/souji-r39/W1ExecScratch/ro2/souji-r39-c2.8kn5d50z'
--- c3 --- PermissionError: [Errno 13] Permission denied: '/fast/scratch/hyaku/souji-r39/W1ExecScratch/ro2/souji-r39-c3.dv_ef2nu'
```
No fallback to the writable `TMPDIR`: `--scratch` is authoritative in all three counters.

### Leftover sweeps (after every batch)

```
find $S -maxdepth 2 -name 'souji-r39*'            -> (empty)
find /tmp /var/tmp -maxdepth 1 -name 'souji-r39*' -> (empty)
```
Baseline before any run: same command, same empty result. Pre-existing unrelated legacy artefacts in
`/tmp` (`/var/tmp/souji-census-selftest.uFAiOl`, `/tmp/souji-r34-closure.json`,
`/tmp/k72-tip-spumbf__/souji-shokunin`, …) are older than my stamp and were not created here.

---

## 3. Verdicts per check

V1 — *every temporary root is caller-controlled*

| instrument | verdict | basis |
|---|---|---|
| `c1-counter.py` | **PASS** | own root `--scratch → TMPDIR → "/var/tmp"` (T1/T2/T17/T19); the extracted reconciler child gets `TMPDIR=scratch` (line 172) |
| `c2-counter.py` | **PASS** | same chain (T5/T9/T17/T19); tool/fixture children get `child_env(scratch)` → `TMPDIR=scratch` (line 72); its own `git` children inherit the ambient env (caller-controlled) |
| `c3-counter.py` | **FAIL (partial)** | own root caller-controlled, but its own git children are pinned to `child_env("/var/tmp")` at lines 71 and 81 (F1) |
| `r39-citation-rev.py` | **FAIL (partial)** | own root = `--work/TMPDIR` (T12/T17), but the tool child is launched with an `ENV` dict that drops `TMPDIR` → `CHILD-TMPDIR=None` (T14, F2) |
| `r39-drift-record-rules.py` | **FAIL (partial)** | same: `ENV` drops `TMPDIR` → `CHILD-TMPDIR=None` (T14, F2); record files use `dir=root` where `root` is inside the scratch (lines 68/94) — those *are* caller-controlled |

V2 — *cleanup runs on every exit path, including an exception before the `try`*

| instrument | verdict | basis |
|---|---|---|
| `c1-counter.py` | **PASS** | nothing but `open_count = 0` between `mkdtemp` (203) and `try` (205); `finally` → `rmtree` (237-238); measured on normal exit (T1), `ValueError` inside the `try` (T4, rc=2) and `REGISTER-ABSENT` (T3) |
| `c2-counter.py` | **PASS** | `legs/harm/def leg` only between 171 and 180; `finally` → `rmtree` (276-277); measured on normal exit (T5) and on `ValueError` inside the `try` (T15, rc=2) |
| `c3-counter.py` | **PASS** | `mkdtemp` 119-120 → `try` 121; `finally` 182-183; measured on normal exit (T7) and on the `FileNotFoundError` traceback path (T6, rc=1) |
| `r39-citation-rev.py` | **PASS** | `mkdtemp` 102 → `results = []` → `try` 104; `finally` 117-118; measured on 8/8 pass (T10) and the all-fail `rc=1` path (T14a) |
| `r39-drift-record-rules.py` | **PASS** | `mkdtemp` 84 → `results = []` → `try` 86; `finally` 112-113; measured on 7/7 pass (T11), all-fail `rc=1` (T14b) and `PermissionError` from `mkdtemp`-of-nested-run (T13 — nothing created, nothing left) |

Caveat, source-only: all five use `shutil.rmtree(..., ignore_errors=True)`, so a scratch tree that
cannot be removed is left silently with exit status unchanged. No such run was produced here (the
only unremovable-root probes failed at `mkdtemp`, before any tree existed).

V3 — *a `--scratch`/`--work` argument is honoured*

| instrument | verdict | basis |
|---|---|---|
| `c1-counter.py` | **PASS** | T2, T19, T17 |
| `c2-counter.py` | **PASS** | T9, T19, T17 |
| `c3-counter.py` | **PASS** | T8, T19, T17 |
| `r39-citation-rev.py` | **PASS** (+validated) | T12 (exit 2 with the path named), T10 |
| `r39-drift-record-rules.py` | **PASS** (+validated) | T12, T11 |

V4 — *any path that ignores the caller's scratch root* → **YES, four of them** (F1, F2×2, F3).

---

## 4. Findings (ordered by severity within this item's axis)

**F1 — `c3-counter.py:71,81`: hardcoded `/var/tmp` as the child `TMPDIR` for its own git calls.**
`git_show` and `resolves` call `child_env("/var/tmp")` instead of the caller's root, so a caller who
pins `--scratch`/`TMPDIR` to `$HYAKU_SCRATCH/souji-r39/<seat>` still hands `/var/tmp` to those two
children. Static (these calls run before `mkdtemp`, which explains the ordering but not the bypass);
no directory was created at `/var/tmp` in any run (sweep empty). Severity low, but it is exactly the
class this seat was asked to flag. A one-line fix: pass the already-selected root, e.g. compute
`root_dir = args.scratch or os.environ.get("TMPDIR") or "/var/tmp"` once, before the resolve checks,
and use `child_env(root_dir)` there and `mkdtemp(dir=root_dir)`.

**F2 — both fixtures drop `TMPDIR` from the child env (measured `CHILD-TMPDIR=None`).**
`r39-citation-rev.py` lines 33-44 and `r39-drift-record-rules.py` lines 33-44 build `ENV` from PATH +
`LC_ALL` + git config + author/committer only. `--work` steers the fixture's own `mkdtemp`, but the
tool under test and every child `git` run with no `TMPDIR`, i.e. the system default `/tmp` if a child
ever needs system temp. Severity low: the measured runs wrote nothing to `/tmp` or `/var/tmp`
(`find /tmp /var/tmp -maxdepth 1 -user vgpnk -newer $S/stamp` → empty). Fix: add
`"TMPDIR": scratch` to the child env in `case()`/`run_case()` (the fixture already knows its scratch).

**F3 — all five: the fallback chain ends in a hardcoded `"/var/tmp"`.**
With neither `--scratch`/`--work` nor `TMPDIR` set, the root is `/var/tmp`, not the round's declared
`$HYAKU_SCRATCH/souji-r39/<seat>` (`/fast/scratch/hyaku`). No `/tmp` literal anywhere, so the
preregistration's "no `/tmp` roots" is satisfied; and this is the r35-r38 house line verbatim (13
prior files). Informational only — flagging so the L1 can decide whether the round wants a stricter
default.

**F4 — all five: the caller root is never normalised to an absolute path.**
`args.scratch` / `args.work` / `TMPDIR` are used as given; a relative value resolves against the
process CWD, not `--root` (T18: `--work relprobe` created `$S/relprobe/...` while `--root` named the
lane). Since seats are spawned in the fleet root, a relative `--work` would land in a foreign repo —
the host guard's exact hazard. Cheap fix: `os.path.abspath()` the selected root once.

**F5 — the counters do not validate `--scratch`, so usage-class failures surface as tracebacks.**
`c1` T2, `c2` T9, `c3` T8/T19 and both fixtures on an unwritable `--work` (T13) exit **1 with a
`FileNotFoundError`/`PermissionError` traceback**, while the docstrings promise exit 2 for usage
(`c2`/`c3`: "2 usage or could-not-evaluate input"; fixtures: "2 usage"). The fixtures do better than
the counters on the missing-directory case (they `isdir`-check and print a usage line, T12). This is
the same doc-vs-behaviour class as R10, inside the new instruments.

**F5' — `c2-counter.py:169-170` reads `tests/fixtures/r39-citation-rev.py` from `--root` *before*
`mkdtemp` and outside any `except`, so an absent fixture ends in a traceback, rc 1 (T16), not the
documented refusal.** No leak (no scratch existed yet).

**F6 — `c3-counter.py:122-123` reads `--fixture`/`--base-fixture` relative to CWD, not `--root`.**
From the fleet root the counter dies with `FileNotFoundError: 'tests/fixtures/r39-drift-record-rules.py'`
(T6) even though `--root` named the lane; `c2` gets this right via `lane_root_of(args)`. Operability
hazard for any wrapper that does not `cd` into the lane first.

---

## 5. Cross-check observations (outside my scratch scope — for the L1 / C1-C2-C3 seats)

- **O1** `census/round-39/cells.tsv` **does not exist in the worktree** at audit time
  (`ls: cannot access 'census/round-39/cells.tsv'`) and `c1-before.txt` therefore records
  `register_cells=0`. Consequence: `c1-counter.py`'s frozen register arm
  (`register_cells>=6`, `commit_distinct>=2`) cannot currently be measured; T1 substitutes
  `census/round-38/cells.tsv` and reads `cells=10 mismatches=0 commit_distinct=0` — ten rows, all with
  `commit == receipt_rev`, i.e. the very r38 limit C1 claims to close. Until `cells.tsv` lands with
  ≥2 mismatched-commit rows, C1's register arm is unproven.
- **O2** `c3-counter.py` pins the **tool** to `--rev` but reads **both fixtures from the worktree**
  (lines 122-123, no `git show`). Measured consequence (T7): at the *base* rev with the current
  worktree fixture the counter already prints
  `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7` and exits 0. Under the
  frozen C3 kill rule the control is the `c3-before` receipt (old fixture bytes,
  `fixture_sha=ac0be0e7a49e`, `cases=10`, `killed=0`), so this does not falsify C3 — but the C3
  predicate is satisfied by fixture bytes alone, so `--rev` is not the discriminator a reader may
  assume. `c3-before` and `c3-after` also disagree on the case count (10 → 7) while both are frozen
  receipts for the same fixture path; the `>=6` floor still holds at 7.
- **O3** `c1` T1 and `c2` T5 reproduce the frozen control readings (`open=16`; `pass=2 fail=4`), so
  both counters are do-nothing-reachable in the base state, as the preregistration requires.
- **O4** `c2-before` (`fixture_sha=c142c1bc28b8`, `L5 new=(8,5,3,1)`) and `c2-after`
  (`fixture_sha=7ab7c3d85a81`, `L5 new=(8,8,0,0)`) were measured on *different* fixture bytes; the
  worktree fixture I audited is the after one (`7ab7c3d85a81`, reproduced in T5/T10).

---

## 6. Blocker / risk statement

- No blocker for this item: all four questions were answered with source lines and executed runs.
- Risk carried forward: **F1** and **F2** mean the round's instruments are only *partially* compliant
  with the preregistration line "Scratch root: `$HYAKU_SCRATCH/souji-r39/<seat>/` … no `/tmp` roots"
  — the *own* roots comply, two child paths do not. Neither produced any observed artefact outside
  the caller root.
- **O1** is the substantive one for C1: the register file its predicate needs is absent from the
  lane right now.
- Scratch state at finish: `/fast/scratch/hyaku/souji-r39/W1ExecScratch` **removed** at the end of
  the run (`rm -rf`, verified absent). No tool installed or upgraded (nothing needed). No git/jj
  mutation: only `init`, `add`, `commit`, `rev-parse`, `cat-file`, `show` inside
  `$S/repo-empty` and `$S/repo-bare`, each named with `-C "$D"` after asserting
  `git -C "$D" rev-parse --show-toplevel`.
