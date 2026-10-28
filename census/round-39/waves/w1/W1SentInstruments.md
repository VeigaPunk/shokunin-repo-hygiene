# W1SentInstruments — security review of the r39 instruments

seat: sentinel (leaf, no dispatch)
lane: /home/vgpnk/Projects/shokunin/souji-shokunin
measured revision: `e9958ee517668fa8aa8a86a8b936b5b2ad56473e` (lane HEAD at final re-probe);
first pass at `d4c17557b92fd98044e4c8f0ddc79c6d75701b15`. `git diff --name-only d4c1755..e9958ee -- census/round-39 tests/fixtures/r39-*.py tools/`
shows **no instrument change** in that interval (only the frozen control receipts), so every
finding below was re-verified at the final rev.
scratch: `/fast/scratch/hyaku/souji-r39/W1SentInstruments` (left on disk — it holds the strace
captures `st2.txt`/`st3.txt` and the probe repos; nothing outside it was left behind).
tooling installed: **none** (no package was needed; `strace`, `git 2.56.0`, `python3 3.14.8`
were already present).

## Verdicts

| # | check | verdict |
|---|-------|---------|
| 1 | child git env is a whitelist, config discovery neutralised | **PARTIAL** — whitelist holds everywhere; one child env (c1-counter's register leg) omits `GIT_ENV`, so `/etc/gitconfig` is still consulted |
| 2 | no symlink-following / FIFO read that can hang or escape `--root` | **FAIL** on the three new counters (`--items`, `--fixture` hang forever on a FIFO); **PASS** on both tools (r38 A4/A7 preserved) |
| 3 | no write into the measured tree or the lane | **PASS** for the three counters and the drift `--json` writer; **FAIL (latent)** for `census/round-39/make-cells.py --write`, which resolves its outputs against CWD |
| 4 | no secret-shaped argv recorded in a receipt | **PASS** |
| 5 | every scratch root honours the caller | **PARTIAL** — c1-counter's git children, c2-counter's `git()`/`run_drift()` children and `r39-drift-record-rules.py`'s child env carry no `TMPDIR`, so they fall back to `/tmp` |

r38 envelope preservation: **A4 preserved, A7 preserved** by the tool code paths (both re-probed);
**neither envelope is extended to the counters' own input files**, and neither r39 fixture asserts
it (coverage gap, see F5).

---

## Check 1 — child git environment

### 1a. The whitelist holds (PASS)

All five r39 instruments build the child env from a literal dict, never `os.environ.copy()`:
`census/round-39/c1-counter.py:43`, `c2-counter.py:43`, `c3-counter.py:39`,
`tests/fixtures/r39-citation-rev.py:32`, `tests/fixtures/r39-drift-record-rules.py:28`.

Hostile-parent probe (a real c3 run, from the lane root, with injected git env):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
GIT_TRACE=$S/trace.log GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor \
GIT_CONFIG_VALUE_0=/bin/false GIT_DIR=/nonexistent \
timeout 180 python3 -B census/round-39/c3-counter.py --root $L --rev $REV \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $S
```

```
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
trace.log present? ls: cannot access '/fast/scratch/hyaku/souji-r39/W1SentInstruments/trace.log': No such file or directory
```

Verdict 1a: PASS — `GIT_TRACE`, `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0` and
`GIT_DIR` never reach a child (no trace file, no config injection), and the counter's own score is
unchanged by the hostile parent.

### 1b. F1 — c1-counter's register leg omits `GIT_ENV` (config discovery live) — PARTIAL

`census/round-39/c1-counter.py:172` builds the citation-reconciler child env inline:

```
env={"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch},
```

It is a whitelist (so no inherited `GIT_*` leaks — 1a holds), but it drops all seven `GIT_ENV`
keys, so system config discovery is **not** neutralised. Reproduced with the exact child env:

```
env -i PATH=/usr/bin:/bin TMPDIR=$S strace -f -e trace=openat,statx,newfstatat,access \
  -o $S/st2.txt git -C $L cat-file -e HEAD
grep -nE 'gitconfig|/etc/git' $S/st2.txt
```

```
12:680737 access("/etc/gitconfig", R_OK)   = -1 ENOENT (No such file or directory)
36:680737 access("/etc/gitconfig", R_OK)   = -1 ENOENT (No such file or directory)
39:680737 access("/etc/gitconfig", R_OK)   = -1 ENOENT (No such file or directory)
```

Control, same command plus `GIT_CONFIG_NOSYSTEM=1`:

```
env -i PATH=/usr/bin:/bin TMPDIR=$S GIT_CONFIG_NOSYSTEM=1 strace ... -o $S/st3.txt git -C $L cat-file -e HEAD
grep -cE 'gitconfig|/etc/git' $S/st3.txt
0
```

So the system config is read by the register-leg child whenever `/etc/gitconfig` exists; today it
does not (`ls -la /etc/gitconfig` → `No such file or directory`), so the gap is **latent, not
exploitable on this host**. `HOME`/`XDG_CONFIG_HOME` are absent from the child env, so the global
and XDG files stay out of reach.

For contrast, `c1.child_env()`, `c2.child_env()`, `c3.child_env()` all carry
`NOSYSTEM='1' GLOBAL='/dev/null' SYSTEM='/dev/null'` (printed from the loaded modules), i.e. the
defect is the one inline dict, not the helper.

Exploit path (latent): a writable `/etc/gitconfig` (package install, mis-set image) could set
`core.fsmonitor`, `include.path`, `core.hooksPath` or `diff.external` and influence the
reconciler's `git show`/`merge-base` children during the C1 register leg, while every other r39
child is immune. Impact: integrity of the C1 register verdict on a hostile host; no containment
breach. Smallest remediation: replace the inline dict with
`dict(child_env(), TMPDIR=scratch)` (one line) so the register leg inherits the same whitelist.

### 1c. Fixture env gaps (low)

`tests/fixtures/r39-citation-rev.py:32-42` and `tests/fixtures/r39-drift-record-rules.py:28-38`
set `GIT_CONFIG_NOSYSTEM/GLOBAL/SYSTEM` and the identity vars, but not the three keys the tools'
`CHILD_ENV` carries: `GIT_ATTR_NOSYSTEM`, `GIT_OPTIONAL_LOCKS`, `GIT_TERMINAL_PROMPT`
(`tools/souji-worktree-drift.py:79-88`). A system `gitattributes` therefore still applies to the
fixture's own `git add`/`commit`, and a credential prompt is not disabled. Low (fixtures build
disposable repos from literals). Smallest remediation: add the three keys to both `ENV` dicts.

Both fixtures also run `git init` without `-C` and without the host-mandated toplevel assertion:
`sh(["git", "init", "-q", "-b", "main", repo])` (r39-citation-rev.py:62),
`sh(["git", "init", "-q", "-b", "main", path])` (r39-drift-record-rules.py:51). Every later call
does name `-C <dir>`, so the repository operated on is the one named, but the rule's
`rev-parse --show-toplevel` assertion is absent in both.

---

## Check 2 — symlink / FIFO / escape

### 2a. Tools: A4 and A7 are preserved (PASS)

Record FIFO (r38 A4 class), `--record` a real FIFO:

```
mkfifo $S/fifo.tsv
timeout 20 python3 -B tools/souji-worktree-drift.py --root $S/fleet --record $S/fifo.tsv --timeout 10
REFUSAL RECORD-MALFORMED: /fast/scratch/hyaku/souji-r39/W1SentInstruments/fifo.tsv is not a regular file
rc=2 elapsed_ms=27
```

Symlink → FIFO, and symlink → `/dev/zero`:

```
ln -sfn $S/fifo.tsv $S/link-fifo.tsv   → REFUSAL RECORD-MALFORMED: ... is not a regular file   rc=2 elapsed_ms=28
ln -sfn /dev/zero  $S/link-zero.tsv    → REFUSAL RECORD-MALFORMED: ... is not a regular file   rc=2 elapsed_ms=27
```

Register FIFO and symlink (r38 A7 class):

```
mkfifo $S/reg.fifo
timeout 20 python3 -B tools/souji-citation-reconcile.py --root $L --rev $REV --register $S/reg.fifo
REFUSAL USAGE: register /fast/scratch/.../reg.fifo is not a regular file
rc=2 elapsed_ms=27

ln -sfn $S/reg-real.tsv $S/reg-link.tsv
timeout 20 python3 -B tools/souji-citation-reconcile.py --root $L --rev $REV --register $S/reg-link.tsv
REFUSAL USAGE: unreadable register /fast/scratch/.../reg-link.tsv: [Errno 40] Too many levels of symbolic links: ...
rc=2
```

Containment of record rows and of the write target (all refused, rc=2):

```
printf 'REPO\t/etc\tregs=1\tprunable=0\n'                     → REFUSAL RECORD-OUTSIDE-ROOT: /etc resolves outside /fast/scratch/.../fleet
ln -sfn /etc $S/fleet/escape; row "escape"                    → REFUSAL RECORD-OUTSIDE-ROOT: escape resolves outside /fast/scratch/.../fleet
git init --separate-git-dir=$S/outside-git $S/fleet/gamma     → REFUSAL RECORD-OUTSIDE-ROOT: gamma gitdir resolves outside /fast/scratch/.../fleet
--json $S/fleet/alpha/out.json                                → REFUSAL JSON-INSIDE-MEASURED-TREE: ... is under /fast/scratch/.../fleet
--json $S/alias.tsv (symlink to the record)                   → REFUSAL JSON-IS-RECORD: ... is the record file
--json $S/out.fifo                                            → REFUSAL JSON-NOT-REGULAR: ... is not a regular file   (rc=2, 31 ms)
```

Verdict 2a: **A4 and A7 preserved** at `e9958ee`; the `--json` write envelope (r37 A2/r38 C2) is
also intact.

### 2b. F2 — the three new counters hang forever on a FIFO input — FAIL (highest severity here)

`c1-counter.py:196` (`open(args.items)`), `c2-counter.py:170`
(`open(os.path.join(os.path.abspath(root), "tests/fixtures/r39-citation-rev.py"))`) and
`c3-counter.py:124-125` (`open(args.fixture)`, `open(args.base_fixture)`) are plain blocking,
symlink-following reads — exactly the class r37 A2.4 / r38 A4 / r38 A7 closed in the tools.

Reproduced (each with an 8 s wall clock; `rc=124` = the `timeout` wrapper killed a run that had
produced no output and no receipt):

```
mkfifo $S/items.fifo; mkfifo $S/fix.fifo
c1 --items  $S/items.fifo  → rc=124 elapsed_ms=8002
c3 --fixture $S/fix.fifo   → rc=124 elapsed_ms=8001
c2 fixture (FIFO at <root>/tests/fixtures/r39-citation-rev.py, root = $S/c2root) → rc=124 elapsed_ms=8001
```

(re-verified at `e9958ee`: `c1 --items rc=124 8002 ms`, `c3 --fixture rc=124 8001 ms`,
`c2 fixture rc=124 8001 ms`.)

Escape variant — the items file is read through a symlink to a path outside `--root`, and the
counter scores those outside bytes under the lane's name:

```
printf 'id\tfile\tanchor\tmust\tmustnot\nX1\tLOG.md\tR39\tround-39\t-\n' > $S/outside-items.tsv
ln -sfn $S/outside-items.tsv $S/link-items.tsv
timeout 30 python3 -B census/round-39/c1-counter.py --root $L --rev $REV \
  --items $S/link-items.tsv --register census/round-39/c1-items.tsv --scratch $S
ITEM X1 OPEN PREDICATE-MISSING LOG.md missing=['round-39'] hits=3
REFUSAL COULD-NOT-EVALUATE: register row with 5 fields
rc=2
```

The item row from the out-of-root file was parsed and evaluated before the register leg refused.

Exploit path: a FIFO (accidental, or planted by any process that can write the worktree or the
caller's `--items`/`--fixture` path) freezes the gate instrument with zero output — the run burns
its wall clock and leaves no receipt, which is precisely the failure mode the round is closing.
A killed run also leaks its scratch directory, because the `finally: shutil.rmtree` never runs:
my two `timeout`-killed c3 runs left `souji-r39-c3.gh85gick` and `souji-r39-c3.rekkmpnb` behind
(empty, `drwx------`, 15:14 and 15:22).
No privilege boundary is crossed. Impact: availability/operability of the three counters.
Smallest remediation: one shared `read_text_nofollow(path)` using
`os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)` + `stat.S_ISREG(fstat)` +
`set_blocking`, applied to `--items`, `--fixture`, `--base-fixture` and the c2 fixture read; and
resolve each against `--root` with the `commonpath` check the tools already use.

### 2c. F3 — the drift record read still follows a symlink leaf (low)

`tools/souji-worktree-drift.py:132` opens the record with `O_RDONLY | O_NONBLOCK` (no
`O_NOFOLLOW`), so a symlinked `--record` is followed. Observed:

```
ln -sfn $S/outside-rec.tsv $S/link-rec.tsv      # target lives outside --root
timeout 20 python3 -B tools/souji-worktree-drift.py --root $S/fleet --record $S/link-rec.tsv --timeout 10
SUMMARY record=/fast/scratch/.../link-rec.tsv record_repos=2 record_regs=2 record_prunable=0 live_repos=2 live_regs=2 live_prunable=0 drift_rows=0 unreachable=0
rc=0
```

No hang (the `O_NONBLOCK` + `fstat` pair from A4 still holds), and the record *rows* are still
contained by `--root`, so this is integrity (which record got measured), not containment. It is
also the one place where the record and register envelopes diverge (the register read is
`O_NOFOLLOW`). Low; smallest remediation: add `O_NOFOLLOW` to the record open and keep the
`RECORD-MISSING`/`RECORD-MALFORMED` mapping the C2 docstring now documents.

---

## Check 3 — writes into the measured tree or the lane

### 3a. Counters and `--json` (PASS)

Marker audit — all three counters, `--scratch $S`, then everything in the lane newer than the
marker:

```
touch $S/marker
cd $L && python3 -B census/round-39/c1-counter.py ... --scratch $S   → c1 rc=1
cd $L && python3 -B census/round-39/c2-counter.py ... --scratch $S   → c2 rc=0
cd $L && python3 -B census/round-39/c3-counter.py ... --scratch $S   → c3 rc=0
find $L -path $L/.git -prune -o -type f -newer $S/marker -print
<lane>/.ufo/waves/round-39/w1/W1CritDisclosure.md        # a sibling seat's report, not a counter output
```

No `census/`, `tools/` or `tests/` file was created or modified; `git -C $L status --porcelain`
showed only the concurrent sibling edits (`M LOG.md`, `M SKILL.md`, `M corpus/QUALITY.md`) and the
pre-existing untracked receipts. c3 applies its mutants to `git show` bytes in scratch only
(`c3-counter.py:129` `source = git_show(args.root, args.rev, args.tool)`), never to the lane file.
The drift writer's guards are quoted in 2a (`JSON-INSIDE-MEASURED-TREE`, `JSON-IS-RECORD`,
`JSON-NOT-REGULAR`, plus the `st_nlink > 1` refusal before `ftruncate`).

One observation, not a defect: `census/round-39/__pycache__/c1-counter.cpython-314.pyc` exists in
the lane (gitignored, `git check-ignore -v` → `.gitignore:3:__pycache__/`), so some earlier run
imported a counter without `-B`. My own `importlib` probes created the `c2`/`c3` `.pyc` files and I
removed exactly those two; the `c1` one predates this seat and was left alone.

### 3b. F4 — `make-cells.py --write` resolves its outputs against CWD, not the lane (latent FAIL)

`census/round-39/make-cells.py:59-64` writes `census/round-39/cells.tsv` and
`census/round-39/cells-lines.md` as **relative** paths, and the tool has no `--root`:

```
cd $S && python3 -B $L/census/round-39/make-cells.py --commit $REV --late $REV --freeze $REV --write
FileNotFoundError: [Errno 2] No such file or directory: 'census/round-39/cells.tsv'
rc=1
```

with the directory present under an arbitrary CWD it writes there:

```
mkdir -p $S/fake/census/round-39; cd $S/fake && python3 -B $L/census/round-39/make-cells.py ... --write
wrote census/round-39/cells.tsv (6 rows) and census/round-39/cells-lines.md
rc=0
<scratch>/fake/census/round-39/cells.tsv
<scratch>/fake/census/round-39/cells-lines.md
```

Every tool starts in the fleet root (`/home/vgpnk/Projects/shokunin`); `census/round-39` does not
exist there today (`ls -d /home/vgpnk/Projects/shokunin/census/round-39` → `No such file or
directory`), so the run tracebacks instead of writing — but the fleet repo is one `mkdir` away from
receiving a `census/round-39/cells.tsv`, which is outside the round's write scope. Latent
write-scope breach plus a non-graceful failure. Smallest remediation: take `--root` (or
`__file__`-relative) output paths and refuse when the resolved path leaves the lane.
Separately, the docstring says the tool *appends* the anchored lines while the code opens
`cells-lines.md` with `"w"` — the doc and the bytes disagree.

---

## Check 4 — secret-shaped argv in receipts

```
grep -rnE 'AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY|Authorization: *Bearer|password *=|api[_-]?key *= *[A-Za-z0-9]' \
  census/round-39/ tests/fixtures/r39-citation-rev.py tests/fixtures/r39-drift-record-rules.py
none
```

and over the receipts specifically:

```
grep -rniE 'token|passw|secret|api[_-]?key|AKIA|ghp_|BEGIN [A-Z ]*PRIVATE|Authorization|bearer' census/round-39/records/
no secret-shaped token
```

The receipts now carry their command lines (`c1-before.txt:1-2`, `c2-before.txt:1-3`,
`c3-before.txt:1-3`); none of them contains a credential, and the only argv that reaches a SUMMARY
line is counts and content hashes (`items_sha=`, `tool_sha=`, `fixture_sha=`). No counter echoes
`sys.argv` or the environment (grep for `argv`/`os.environ` in the three counters shows only
`argparse` plumbing and the `TMPDIR` fallback). PASS.

Two reproducibility notes on those command lines (calibration, not secrecy): they name `--root .`
and `--scratch $S` literally — `$S` is unexpanded and `--root .` is relative, so the recorded
command cannot be re-run as written from a different CWD.

---

## Check 5 — scratch root honours the caller

`--scratch` is honoured by all three counters for their own `mkdtemp`
(`c1:203`, `c2:171`, `c3:120`, all `dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp"`),
and c3's `child_env()` now defaults `TMPDIR` to `scratch or TMPDIR or /var/tmp` (fixed in
`d4c1755`). What a child actually sees:

```
c1.child_env()                  NOSYSTEM='1' GLOBAL='/dev/null' SYSTEM='/dev/null' TMPDIR=None
c2.child_env()                  NOSYSTEM='1' GLOBAL='/dev/null' SYSTEM='/dev/null' TMPDIR=None
c2.child_env(scratch)           NOSYSTEM='1' GLOBAL='/dev/null' SYSTEM='/dev/null' TMPDIR='/x'
c3.child_env()                  NOSYSTEM='1' GLOBAL='/dev/null' SYSTEM='/dev/null' TMPDIR='/var/tmp'

c2 child_env()                  -> TMPDIR=None tempdir=/tmp
c2 child_env(existing scratch)  -> TMPDIR='/fast/scratch/hyaku/souji-r39/W1SentInstruments/td' tempdir=/fast/scratch/.../td
```

### F6 (low) — the gaps

- `c1-counter.py:54` `child_env()` never sets `TMPDIR`, and `git_show`/`git_resolves` use it, so
  every `git show`/`cat-file` child of the C1 counter resolves temp files to `/tmp`.
- `c2-counter.py:68` only sets `TMPDIR` when a scratch argument is passed, but `git()` and
  `run_drift()` call `child_env()` with no argument — the C2 git children and the drift tool it
  spawns in L4 see `TMPDIR=None` → `/tmp` (measured above).
- `tests/fixtures/r39-drift-record-rules.py:28` `ENV` has no `TMPDIR` and `run_case` passes `env=ENV`
  straight to the drift tool, so the tool and its git children use `/tmp`:
  `fixture ENV TMPDIR=None -> child tempdir=/tmp`.
  `r39-citation-rev.py` does better for the tool child (`case()` sets `TMPDIR=os.path.dirname(register)`),
  but its `build()` git calls (`git init/add/commit`) still run under `ENV` without `TMPDIR`.

Impact: child temp files (git lock/odb temp) land in `/tmp` rather than the caller's scratch root —
the round's "no `/tmp` roots" rule is met only for the counters' own mkdtemp. Smallest
remediation: give `c1.child_env()` and `c2.child_env()` the same `TMPDIR` default c3 now has, and
add `TMPDIR` to both fixtures' `ENV` (or pass `--work` through to `run_case`'s env).

---

## r38 A4 / A7 preservation by the new code paths

- **A4 (no special-file wait on the record; TOCTOU closed)** — preserved by
  `tools/souji-worktree-drift.py:132-141` (`O_NONBLOCK` open, `fstat` `S_ISREG`, then
  `set_blocking`). Probed: FIFO record, symlink→FIFO, symlink→`/dev/zero` all refuse in 27-28 ms
  with `RECORD-MALFORMED`, never blocking. **Not extended**: the new fixtures and counters read
  their own inputs with plain `open()` and hang (F2).
- **A7 (register read `O_NOFOLLOW|O_NONBLOCK` + `receipt_rev` bound)** — preserved by
  `tools/souji-citation-reconcile.py:180-201` (open at :185); FIFO register refuses (`rc=2`, 27 ms), symlink
  register refuses (`ELOOP`, `rc=2`), and the reconciler still refuses a non-commit `--rev` /
  `--register-rev` with `REFUSAL REV-UNRESOLVED` (exit 2) as C2 claims. **Not extended**: the
  counters' `--items`/`--fixture` reads have neither guard (F2), and the record leaf lost
  `O_NOFOLLOW` relative to the register read (F3).
- **F5 (coverage, adjacent to C3)** — neither `tests/fixtures/r39-citation-rev.py` nor
  `tests/fixtures/r39-drift-record-rules.py` carries a FIFO, a symlink, or a `/dev/*` case, so the
  C2 L5 / C3 candidate fixtures cannot catch a regression of A4/A7 in either direction. The eight
  C2 cases are revision classes; the seven C3 cases are record-schema classes. Adding one FIFO and
  one symlink case per fixture would make the envelope testable rather than merely asserted.

---

## Adjacency — what the round contract reads at `e9958ee`

Measured with the contract's own commands (absolute paths, `--scratch` in my root):

```
cd $L && python3 -B census/round-39/c1-counter.py --root $L --rev e9958ee... \
  --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch $S
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
c1 rc=1

c2 ... --rev e9958ee --base-rev ed30b7f...
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
c2 rc=0

c3 ... --rev e9958ee --base-rev ed30b7f...
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
c3 rc=0
```

- **C1 is not met at HEAD**: `open=2` (items R39-C1-03 and R39-C1-04 name
  `census/round-39/records/waves-wait.txt` and `waves-capture.txt`, both absent) and
  `register_cells=0` — `census/round-39/cells.tsv` does not exist; the generator
  `census/round-39/make-cells.py` is untracked (`?? census/round-39/make-cells.py`). The frozen
  predicate needs `open=0 register_cells>=6 commit_distinct>=2`.
- **C2 meets its predicate** (`legs=6 pass=6 fail=0 harm=0`). Note the untracked after-receipt
  `census/round-39/records/c2-after.txt` still records `fixture_sha=7ab7c3d85a81`, which does not
  match the fixture bytes the counter now hashes (`e555d8281484`, the value the re-measured
  `c2-before.txt` also records) — if that file is landed as the C2 evidence it misdescribes its own
  instrument (R14 class). `c2-before.txt`, `c3-before.txt`, `census-after.txt`,
  `census-before.txt` are likewise untracked (R4 class).
- **C3 meets its predicate** (`mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7`).
  `c3-before.txt` records `cases=10 fixture_sha=ac0be0e7a49e` from the pre-round fixture set, which
  is consistent with its own note ("the pre-round fixture set is the candidate here").

## Severity summary

| id | severity | class | evidence |
|----|----------|-------|----------|
| F2 | medium | FIFO hang + symlinked out-of-root input in all three counters | P7/P9/P10 (rc=124 at 8 s), P8 |
| F4 | medium (latent) | `make-cells.py --write` writes relative to CWD; no `--root` | P21/P21b |
| F1 | low | c1 register-leg child env omits `GIT_ENV`; `/etc/gitconfig` consulted | strace `access("/etc/gitconfig")` ×3 vs 0 |
| F3 | low | drift record leaf opened without `O_NOFOLLOW` | P3 |
| F6 | low | `TMPDIR` not propagated to c1/c2 git children and the r39 record fixture's child | tempdir `/tmp` |
| F5 | low | no FIFO/symlink case in either r39 fixture | case lists |
| 1c | low | fixture `ENV` lacks `GIT_ATTR_NOSYSTEM`/`GIT_OPTIONAL_LOCKS`/`GIT_TERMINAL_PROMPT`; no toplevel assertion | static |

Nothing here is a privilege boundary crossed by untrusted input: the inputs the counters read are
lane files or caller-supplied paths, and the tools' `--root` containment held on every probe. The
defects are (a) a hang class reintroduced in the new gate instruments, (b) one latent config-
discovery gap, and (c) one latent write-scope gap in the untracked C1 register generator.
