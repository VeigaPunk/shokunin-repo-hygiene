# S57sentinel01 — round 57 / wave w1 — write-scope, special-file, diagnostics, scale review

Seat: sentinel. Scope: the two new instruments (`c1-counter.py` v6, `c2-counter.py`),
the fixture builder, the matrix driver and the receipt recorder. Frozen bytes were
read only; no lane file was edited. Raw receipts: `w1/S57sentinel01/receipts/`.

Definitions used in every command below:

```
S=/fast/scratch/hyaku/souji-r57/S57sentinel01          # my scratch (deleted before yield)
L=/home/vgpnk/Projects/shokunin/souji-shokunin          # lane repo
```

**Verdict.**
- C1 predicate (B4/C4 refused, C6/F29/F17/F18/F19 kept, all-findings selftest): **AGREE** —
  reproduced on this session's run; matrix byte-identical to the committed dry-run.
- C2 predicate (before manifest refused, selftest passes): **AGREE**.
- Hardening claims (“writes nothing outside --work”, “scrubbed environment”, “never
  writes outside `<out-file>`”, “the inline class follows the markdown grammar”):
  **DISAGREE** in five concrete, reproducible ways below.
- **ATTACK-FOUND:** one HIGH (silent over-accept introduced by the v6 inline class) and
  ten MEDIUM/LOW robustness defects, each with command + observed output.
- Frozen instruments are unchanged (five sha256 equal the preregistration pins).

---

## 0. Precondition: frozen bytes

```
$ cd $L/census/round-57 && sha256sum c1-counter.py c2-counter.py fixtures/build-fixtures.py \
    fixtures/run-matrix.sh record-receipt.sh
e18872d6584bdf7252a695a7ba19da875e2d7b53f1c5b46e5b524c70fcdf78d4  c1-counter.py
174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2  c2-counter.py
2b8b657b8d86541d4a6f38345cd8d67f1a520603a7cda08f0a5bc3038924633b  fixtures/build-fixtures.py
72adf821938713b74a3b2cfab93f72981374b3c4d98ac7c8939a0f4ffe34a4d5  fixtures/run-matrix.sh
84148011abc9574048fc77e02427bee9010850418beeeaaa1babe59185109aa9  record-receipt.sh
```

All five equal `preregistration.txt`. No frozen file was touched; no tool was installed.

---

## 1. Scratch discipline — every write path, /tmp, TMPDIR, `--work`/`--scratch`

### 1.1 Inventory (code read + syscall proof)

| instrument | writes it can make | hardcoded `/tmp` | reads `TMPDIR`? | steering |
|---|---|---|---|---|
| `c1-counter.py` | selftest: `--work/c1-fixtures/<fixture>/` only (via `build-fixtures.build_one`); real mode: none | no (`grep` finds no `/tmp`) | no | `--work`, `--scratch` alias (`main`: `work = ns.work or ns.scratch`) |
| `c2-counter.py` | selftest: `--work/c2-fixtures/{repo,*.manifest.tsv}`; real mode: none | no | no (only the docstring mentions it) | `--work`, `--scratch` alias |
| `fixtures/build-fixtures.py` | `--work/<fixture>/` + `--manifest` (default `--work/fixture-manifest.tsv`) | no | no (git subprocess env is a constructed dict) | `--work` (must pre-exist), `--manifest` |
| `fixtures/run-matrix.sh` | `mkdir -p "$OUT"` + two TSVs under `$OUT` | no | it *sets* `TMPDIR="$S"` for the counters (unused) | positional `<scratch> <outdir>` |
| `record-receipt.sh` | `"$OUT"` only (line 33 `} > "$OUT"`) | no | no | `<out-file>` |

`grep -nE '/tmp|TMPDIR|tempfile|mkstemp|mkdtemp|TemporaryDirectory'` over the five files
returns only docstring text and `run-matrix.sh:23` (which *passes* `TMPDIR`, never reads it).

### 1.2 Proof that `--work`/`--scratch` steer all writes (clean environment)

`strace -f -y` of the full 36-fixture C1 selftest, classifying every
`openat(O_WRONLY|O_RDWR|O_CREAT|O_TRUNC)`, `creat`, `mkdir*`, `rename*`, `unlink*`,
`rmdir`, `symlink`, `link*` by resolving relative paths against the per-pid
`AT_FDCWD</dir>` (including `chdir`) — receipt `receipts/scopes.txt`:

```
inside $S: 6419   outside $S: 0   /dev/null config opens: 870
$ python3 -B c1-counter.py --selftest --work $S/c1work3      → SELFTEST pass cases=36, rc=0
```

C2 selftest clean environment: strace classification = 185 write-ish events inside `$S`,
33 `/dev/null` opens, 0 outside `$S`; `SELFTEST pass cases=8`, rc=0. `--scratch` alias
writes `c1-fixtures/`/`c2-fixtures/` under the named dir. The canary dir `$S/tmpcanary`
was empty after every run that pointed `TMPDIR` at it; `TMPDIR=/nonexistent` changes
nothing (rc=0 both selftests) — TMPDIR is not consulted, so it is not trusted.

Real-lane modes are read-only: c1 real-mode run has 8 write-ish syscalls, all
`/dev/null`; c2 real-mode has 4, all `/dev/null` (the scrubbed `GIT_CONFIG_GLOBAL`).
Matrix driver: inside `$S` 4 events, outside `$S` 5 = `mkdir()` attempts on existing
ancestors of `$S` returning `EEXIST` plus one `openat("/dev/tty")` `ENXIO` from bash job
control; the only successful `mkdir` in the trace is `mkdir("mxout2") = 0` (inside `$S`);
the two TSV writes land under `$OUT`. No stray directories at the fleet root:

```
$ ls -d /home/vgpnk/Projects/shokunin/{scratch,hyaku,souji-r57,S57sentinel01,mxout}
ls: cannot access '.../scratch': No such file or directory   (… all five absent)
```

`run-matrix.sh` reproduces the committed dry-run **byte for byte**:

```
$ diff -q $S/mxout/c1-matrix-v5.tsv $L/census/round-57/records/matrix-dryrun/c1-matrix-v5.tsv  → identical
$ diff -q $S/mxout/c1-matrix-v6.tsv $L/census/round-57/records/matrix-dryrun/c1-matrix-v6.tsv  → identical
rows=36  exit0 v5=10  v6=8  changed rows = B4-INLINE-NBSP-OPENER, C4-INLINE-CLOSED-COMMENT
```

### 1.3 Where the write discipline fails

- **M7 (MEDIUM, write escape): the C2 selftest builder inherits the whole environment for git.**
  `c2-counter.py:181` `env = dict(os.environ, **git_env())`, then `run('git','init',…)`
  with `cwd=repo` but no `GIT_DIR` purge. With `GIT_DIR` pointing at another repository the
  builder initialises/adds/commits **inside that repository, outside `--work`**:

  ```
  $ (cd $L && GIT_DIR=$S/c2attacks/foreign/.git python3 -B census/round-57/c2-counter.py \
        --selftest --work $S/c2gitdir2)
  foreign before: HEAD=8642b53c… log=1 status=clean
  rc=1  SELFTEST fail cases=8
  foreign after:  HEAD=21b1a99d… log=2 status=1          ← an entire fixture commit written outside --work
  ```

  The C1 builder is safe here: `build-fixtures.git_env()` returns a constructed dict, so
  `GIT_DIR` is dropped. Verified on the same victim repo:

  ```
  $ (cd $L && GIT_DIR=$S/c2attacks/foreign/.git python3 -B census/round-57/c1-counter.py \
        --selftest --work $S/c1gitdir)
  rc=0  SELFTEST pass cases=36
  foreign: HEAD=21b1a99d… log=2 status=1 before and after  ← unchanged
  ```
  *Smallest remediation:* construct the git env as a dict (as `build-fixtures.py` does) and
  explicitly delete `GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE/GIT_OBJECT_DIRECTORY/GIT_ALTERNATE_OBJECT_DIRECTORIES/GIT_REPLACE_REF_BASE`.

- **M8 (MEDIUM, false record + symlink follow): `record-receipt.sh` reports success when it
  wrote nothing, and writes through a symlinked `OUT`.** Line 33 redirection failure is not
  checked, and line 23/25 follow a symlinked `OUT`:

  ```
  $ (cd $L && bash census/round-57/record-receipt.sh $L d749f7ee… census/round-57/c1-counter.py \
        $S/c2attacks/rr/nodir/out.txt -- true)
  census/round-57/record-receipt.sh: line 33: …/nodir/out.txt: No such file or directory
  RECORD …/nodir/out.txt rev=d749f7ee… instrument=census/round-57/c1-counter.py rc=0
  rc=0 exists=no                         ← success line, no receipt

  $ ln -sfn $S/rr/target.txt $S/rr/link-out.txt
  $ (cd $L && bash census/round-57/record-receipt.sh $L d749f7ee… … $S/rr/link-out.txt -- true)
  RECORD …/rr/link-out.txt … rc=0
  target now: instrument=census/round-57/c1-counter.py …   ← target.txt overwritten through the symlink
  ```

  *Impact:* the docstring says “never writes outside `<out-file>`”; a claim can cite a
  `RECORD` line whose receipt does not exist, and a symlinked out-path overwrites an
  arbitrary file. *Remediation:* check the redirection status and exit 2 on failure; refuse
  `[ -L "$OUT" ]` and non-regular `OUT`; create/validate the parent directory first.

- **L7 (LOW, lane write): non-`-B` imports write `__pycache__` into the frozen round dir.**
  Reproduced on a copy (`cp -a $L/census/round-57 $S/copy3/round-57`, then
  `python3 round-57/c1-counter.py --selftest`): only
  `round-57/fixtures/__pycache__/build-fixtures.cpython-314.pyc` is created — the selftest
  imports the builder from the instrument directory, outside `--work`. Documented commands
  use `-B`, so the committed receipts are unaffected.
  **Disclosure:** the *lane* currently contains
  `census/round-57/__pycache__/{c1-counter,c2-counter}.cpython-314.pyc` (mtime 20:31 and
  20:34). The 20:31 `c1-counter.pyc` is **mine**: an eval-cell microbenchmark did
  `importlib.util.spec_from_file_location(…, $L/census/round-57/c1-counter.py); exec_module()`
  without `-B`. The 20:34 `c2-counter.pyc` has no matching import of mine (every counter
  invocation of mine used `python3 -B`); it is another seat's. I did **not** delete them:
  lane edits are outside my grant. Recommend the L1 run
  `rm -rf $L/census/round-57/__pycache__` before the final receipt; no frozen byte changed.

- **L6 (LOW, operability): the matrix command in the preregistration does not create `--work`.**
  `build-fixtures.py` refuses a non-existent work dir (`--work must exist: …`, rc=1); the
  prereg’s `--work <scratch>/selftest` shape needs a preceding `mkdir -p` (the peer receipt
  `w1/S57executor01/build-initial-missing-work.txt` hit the same). Add the `mkdir` to the
  documented command.

---

## 2. Symlink and special-file handling (C2 gate)

Receipt fixture repo `$S/c2attacks/repo` (my own `git init`; toplevel asserted). Command:
`(cd $L && timeout 10 python3 -B census/round-57/c2-counter.py --root $S/c2attacks/repo --manifest <MF>)`.
Full table: `receipts/c2-special.txt`.

| case | rc | wall | observed |
|---|---|---|---|
| honest regular receipt | 0 | 0.056s | `SUMMARY receipts=1 findings=0` |
| receipt is a symlink (valid target) | 1 | 0.053s | `FINDING RECEIPT-SYMLINK receipts/link.txt` |
| receipt is a broken symlink | 1 | 0.056s | `FINDING RECEIPT-SYMLINK receipts/broken.txt` |
| receipt is a FIFO | 1 | **0.053s** | `FINDING RECEIPT-MISSING receipts/fifo` — no hang |
| receipt is a directory | 1 | 0.051s | `FINDING RECEIPT-MISSING receipts/dir` |
| parent-directory symlink inside root | **0** | 0.057s | `SUMMARY receipts=1 findings=0` (read-through) |
| `../outside-valid.txt` | **0** | 0.058s | `SUMMARY receipts=1 findings=0` (escape) |
| absolute `/fast/.../outside-valid.txt` | **0** | 0.054s | `SUMMARY receipts=1 findings=0` (escape) |
| `/dev/null` (absolute) | 1 | 0.051s | `FINDING RECEIPT-MISSING /dev/null` |
| `--root` through a symlink | 0 | — | `SUMMARY receipts=1 findings=0` |
| `--root` symlink loop | 2 | — | `CANNOT-EVALUATE --root is not a directory: …/loop` |

Syscall proof (receipt `receipts/` raw `symfifo.strace` excerpt):

```
newfstatat(…, "…/receipts/link.txt", {st_mode=S_IFLNK|0777, …}, AT_SYMLINK_NOFOLLOW) = 0
newfstatat(…, "…/receipts/fifo",     {st_mode=S_IFIFO|0644, …}, AT_SYMLINK_NOFOLLOW) = 0
newfstatat(…, "…/receipts/fifo",     {st_mode=S_IFIFO|0644, …}, 0) = 0
openat calls naming the symlink target: 0
openat calls naming the FIFO: 0
```

The final-component symlink refusal is correct and does not read through; the FIFO is
refused via `S_ISREG` before any `open` — **no hang**, so the task’s HIGH criterion for a
FIFO receipt is not met.

**M5 (MEDIUM, path containment).** The gate never requires the receipt to live under
`--root`. `check_receipt` does `p = root / rel` (c2-counter.py:105-110); with an absolute
`rel`, `pathlib` discards `root`, and `..` / a symlinked parent simply resolve outside.
Three rows above pass with `findings=0` while reading a receipt outside the measured tree
(the fixture receipt has `instrument=-`; with a pin the rev/digest are resolved in `root`’s
git, so the file itself is still foreign). *Exploit path:* a manifest row that names a
receipt in another checkout/`/tmp` satisfies the gate for a receipt the lane never
contains. *Smallest remediation:* `resolved = (root / rel).resolve()` and refuse unless
`os.path.commonpath([root, resolved]) == str(root)`; add one fixture per escape shape.

**L3 (LOW): a manifest that is a FIFO blocks.** `timeout 5 … --manifest <FIFO>` → rc=124
(5.00 s). The receipt FIFO is safe; this is the adjacent caller-supplied-manifest case.
*Remediation:* document manifests as regular files or open with `O_NONBLOCK` and refuse
non-regular manifests.

---

## 3. Diagnostics: control bytes and a 1 MiB line

### M2 (MEDIUM) — finding details echo raw terminal control bytes

C1: a correction path token containing `ESC [31m` and `BEL` still lexes and is printed
verbatim (`ctrl-leak` fixture, site at 79, correction names a non-site path):

```
$ grep -a '^FINDING' $S/attacks/out/ctrl-leak.v6.out | od -c
F I N D I N G   I N E R T - C O R R E C T I O N  033 [ 3 1 m S C O R E C A R D . m d \a : 2
  n a m e s   n o n - s i t e   p a t h  033 [ 3 1 m S C O R E C A R D . m d \a \n
```

C2: a receipt whose rev token is `ESC[31mHEAD BEL`:

```
$ grep -a '^FINDING' $S/c2attacks/out/ctrl.out | od -c
… r e v = 033 [ 3 1 m H E A D \a \n
```

*Impact:* findings are written into receipts and read in terminals/editors; `ESC` can
recolor or forge adjacent output, `BEL`/other C0 bytes are invisible. *Remediation:* escape
non-printables in every interpolated token (`token.encode('unicode_escape')` or
`backslashreplace`) and cap the echoed length.

### M3 (MEDIUM) — one control byte after the line number silently drops a correction

`R52-CORRECTION SCORECARD.md:2\x07 stale=79 recomputed=83` no longer matches
`CORR_RE` (`(\d+)` must be followed directly by ` stale=`); the line is treated as prose:

```
bel-hides-bogus  v6 rc=0   SUMMARY … bogus=0     (no finding at all)
bogus-clean      v6 rc=1   FINDING BOGUS-RECOMPUTED SCORECARD.md:2 recomputed=83 but record count is 79
```

Same in v5. On an agreeing site the bogus filing escapes judgment; on a stale site the
missing filing is still caught by `unfiled` (safe direction). *Remediation:* generalise
`CORRECTION-FILE-BINARY` beyond NUL — refuse a correction-like line carrying C0 controls,
or strip `[\x00-\x08\x0b\x0c\x0e-\x1f]` before lexing — and add the BEL fixture.

### L4 (LOW) — 1 MiB tokens are echoed whole

- C1: 1 MiB correction path → wall **0.081 s** (baseline 0.060 s), stdout 1 MiB+ (the
  token is repeated in the `INERT-CORRECTION` detail).
- C2: 1 MiB `rev=` token → wall **0.066 s**, stdout **1,048,662 bytes**.
No crash, no superlinearity at this size; the issue is output amplification (and it is the
carrier for M2). *Remediation:* truncate token echoes to e.g. 200 chars with an explicit
`…` marker.

---

## 4. Scale: 20,000-line SCORECARD and the inline scan

Fixture: `SCORECARD.md` = the site line + N prose lines. Exact v6 real-lane argv shape, one
`--root` run, timed with `date +%s.%N`; receipt `receipts/scale.txt`:

| fixture (N lines, 1 opener/line) | v6 wall | v5 wall |
|---|---|---|
| 5,000 unclosed mid-line openers | 0.737 s | — |
| 10,000 unclosed | 3.123 s | — |
| **20,000 unclosed** | **12.396 s** | **0.098 s** |
| 20,000 closed same-line openers | 0.119 s | — |
| 1,000 correction lines (20k-line file) | 0.150 s | — |
| 2,000 correction lines | 0.311 s | — |
| 4,000 correction lines | 0.949 s | — |

`hidden_lines()` alone (microbenchmark, `importlib` on a scratch copy):

```
unclosed: 1,000 0.026 s | 2,000 0.111 s | 4,000 0.439 s | 8,000 1.712 s   (~4.0x per doubling)
closed:   1,000 0.001 s | 4,000 0.002 s | 8,000 0.005 s | 20,000 0.012 s  (linear)
```

**M4 (MEDIUM) — the inline scan is quadratic for unclosed mid-line openers.** For each
line the branch finds `<!--`, then walks `j` to end-of-file looking for `-->`; when there is
no closer (the F29 prose-mention shape the repair is meant to keep visible) it walks to EOF
for *every* such line (c1-counter.py:299-324). At 20,000 lines the counter takes 12.4 s vs
0.098 s under v5 (126×); extrapolation is ~50 s at 40k and ~5 min at 100k. The lane
SCORECARD is 1,460 lines in the working tree at audit time, so this is a robustness/cost
finding, not a lane blocker.
Secondary (same run, lines 420/424): `corr.count('\n', 0, m.start())` per correction makes
correction numbering O(N²) in the number of corrections (4,000 corrections → 0.949 s on a
20k-line file). *Remediation:* precompute the next-closer line (one reverse pass) and, for
unclosed openers, memoise the “no closer after here” result per line; keep a running line
offset instead of `count()` per match.

---

## 5. Write-scope audit of the round

```
$ find $L/.ufo/waves/round-57 -type f | sort        # 411 files when counted (written concurrently)
```

Every file whose name starts with a seat id (`S57executor01/02/03`, `S57reviewer01/02`,
`S57scribe01`, `S57scout01`, `S57mutation01`, `S57connector01`, `S57revenger01`,
`S57critic01`, …) sits under `w1/<that seat>/` or is that seat’s `w1/<seat>.md`. **No
seat-named file appears in another seat’s directory or at the `w1/` or `round-57/` root.**
The five non-seat files at the round root are wave infrastructure (`w1-spec.json`,
`w1.ready`, `w1.ready.dispatched`, `w1-dispatch.json`, `w1/swarm-registry.json`) written
by the driver/L1, not by a seat writing into a peer’s space.

The only outside-seat writes found this session are the two `census/round-57/__pycache__`
files described in L7 (lane tree, not `.ufo`); one of them is mine and is disclosed above.

---

## Findings (severity order)

### HIGH

**H1 — Inline-comment scan is purely textual: an inline code span opens a “comment” and
silently suppresses a real LOG/README overstatement (v6 regression).**

The v6 inline class (c1-counter.py:299-324) sees the four characters `<!--` anywhere on a
line without four leading spaces. CommonMark parses inline code spans *before* raw HTML, so
`` `<!--` `` in backticks is literal text; v6 does not model backticks. The pair scan
(`phidden = hidden_lines(ptext)`, c1-counter.py:536) then skips the lines the phantom span
covers.

Fixture `log-codespan` (registry = 3 rows; LOG.md):

```
# log
- a code span `<!--` opens nothing.
- the note said corpus/SOURCES.md 999 -> 1000 rows.
- another code span `-->` closes nothing.
```

Exact same command shape as the real-lane recompute (`--sources-rev-before/after` = tip):

```
=== log-codespan v6 rc=0
SUMMARY sites=2 mismatches=0 filed=0 unfiled=0 … logunfiled=0 logrecomp=0 …
=== log-codespan v5 rc=1
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:3 claims 999 -> 1000 rows but the registry holds 3; …
=== log-codespan-base (control without the two code-span lines) v6 rc=1
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 …
```

The overstatement line itself contains neither `<!--` nor `-->`; it is suppressed only by
the two backticked tokens. v5 (line-start-only opener) is immune — this is a v6
over-acceptance, the silent direction. Impact: a LOG.md/README.md that documents the
`<!--` token in a code span, with any later `-->` (also commonly documented in a code span),
hides an unrelated overstating pair line and the counter exits 0 with `logunfiled=0`. The
same shape over-hides real filings in SCORECARD.md (`sc-codespan`: v6 rc=1
`CORRECTION-IN-FENCE … hidden_by=inline`, v5 rc=0) — a false refusal, the safe direction.
*Smallest remediation:* make the inline scan skip `<!--` occurrences inside a backtick code
span (track the backtick runs on the line), or restrict the inline class to the trace the
renderer actually produces; add a pair-scan fixture (above) and a SCORECARD fixture
(`sc-codespan`) and assert their outcomes in the selftest.

### MEDIUM

**M1 — Line-start `<!-->` and `<!--->` are not self-closing in the block branch (contradicts
the v6 docstring).** The docstring says “the CommonMark `<!-->` / `<!--->` forms end on
their own line”; the inline branch implements that (line 306), but the block branch tests
`'-->' not in ln[4:]` (lines 292-296), which misses the `-->` formed by the opener’s own
dashes. The block then runs to the next `-->`, or to EOF.

```
=== abrupt-only (SCORECARD: site 78 + `<!-->` + honest filing) v6 rc=1
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:4 (site SCORECARD.md:2) hidden_by=block
SITE path=SCORECARD.md … status=mismatch filed=no
=== abrupt-only-ctrl (same without the `<!-->` line) v6 rc=0
SITE path=SCORECARD.md … status=mismatch filed=yes
```

The same shape in LOG.md is a **silent over-accept** (both arms):

```
log-base  v6 rc=1  FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 …
log-abrupt v6 rc=0  SUMMARY … logunfiled=0 …        (LOG.md line 2 is `<!-->`)
<!---> behaves identically (abrupt-dash-only rc=1 vs abrupt-only-ctrl rc=0).
```

This is carried over from v5 (v5 output identical apart from `hidden_by=`), but v6’s
docstring now asserts the opposite of its behaviour. *Remediation:* in the block branch
treat `ln[4:].startswith('>')` / `ln[4:].startswith('->')` as closed on the opener’s own
line; add both forms (SCORECARD + LOG) as fixtures.

**M2 — Raw terminal control bytes in findings.** See §3; `ESC`/`BEL` bytes appear verbatim
in `INERT-CORRECTION` (C1) and `RECEIPT-REV-NOT-FULL40` (C2) details.

**M3 — A C0 byte after the correction line number silently drops the filing.** See §3.

**M4 — Quadratic inline scan for unclosed mid-line openers.** See §4 (12.396 s at 20,000
lines; v5 0.098 s).

**M5 — C2 receipt path is not contained to `--root`.** See §2 (absolute, `../`, and
symlinked-parent rows all pass).

**M6 — `record-receipt.sh` inherits the environment for git, so `instrument_sha256` can bind
a foreign repository’s bytes while reporting rc=0.**

```
$ (cd $L && GIT_DIR=$S/c2attacks/victim/.git bash census/round-57/record-receipt.sh $L \
      cdd629219525b0a5d4dc3be2fa4999ab7e41481f census/round-57/c1-counter.py \
      $S/c2attacks/rr/foreign-env.txt -- true)
RECORD …/foreign-env.txt rev=cdd629… instrument=census/round-57/c1-counter.py rc=0
receipt: instrument_sha256=67e947e2aff4f2fd697a04bcb1292bd337652fa3d83e6bf38184655f0bafc3cc
victim file digest            = 67e947e2aff4f2fd697a04bcb1292bd337652fa3d83e6bf38184655f0bafc3cc
lane: git -C $L cat-file -e cdd629…:census/round-57/c1-counter.py
      fatal: path 'census/round-57/c1-counter.py' exists on disk, but not in 'cdd629…'
```

The recorder is the Q109 repair; under an inherited `GIT_DIR` (git hooks, CI wrappers,
`jj`/`git` shells) it records a digest that is **not the lane’s committed blob**. The gate
(whose `git()` builds a scrubbed dict) later refuses with `RECEIPT-REV-ABSENT` +
`RECEIPT-INSTRUMENT-PIN-MISSING` (rc=1), so the pair is safe end-to-end, but the recorded
artifact is wrong. The recorder also omits `GIT_NO_REPLACE_OBJECTS=1`, so a replace ref in
the lane can change what it digests. *Remediation:* apply the same constructed environment
and `-c core.fsmonitor=false -c core.hooksPath=/dev/null` used by the counters, and reject
`GIT_DIR`/`GIT_WORK_TREE`/`GIT_REPLACE_REF_BASE` explicitly.

**M7 — C2 selftest builder writes outside `--work` under an inherited `GIT_DIR`.** See §1.3.

**M8 — Recorder prints `RECORD … rc=0` with no receipt, and follows a symlinked OUT.** See §1.3.

**M9 — T1’s `hidden_by=` detail clause is asserted by nothing.** The selftest compares only
the ordered finding-id list (`got_find = [ln.split(' ')[1] …]`); the expected TSV has no
detail column. A scratch copy with the detail expression replaced by the constant `'block'`:

```
$ (cd $S/copy2 && python3 -B round-57/c1-counter.py --selftest --work $S/c1mut3)
rc=0   SELFTEST pass cases=36
```

So a mutant that mislabels every inline finding survives; the B4/C4 `hidden_by=inline`
requirement holds only by manual inspection (I did verify it this session: both details read
`hidden_by=inline`). *Remediation:* add a detail-match column (e.g. `name<TAB>rc<TAB>ids<TAB>detail-regex`)
or assert `hidden_by=inline` for the B4/C4 rows.

**M10 — The C2 selftest’s `control=FALSE-GREEN-REJECTED` is arithmetic on the expected file,
not a stub run.** `c2-counter.py` never imports or executes `controls/c2-stub.py`; it counts
expected rows with an empty finding list (`stub_meets`) and fails only if that count > 1
(lines 245-265). The committed expected has exactly one clean case (`REV-OK`), so the green
control is tautological. Tampering two expected rows to `-` flips it:

```
rc=1   SELFTEST control=FALSE-GREEN-ACCEPTED stub_meets=3
```

*Impact:* the prereg says “a discarded always-clean stub is scored over the same cases”; the
printed control asserts something the code did not test. *Remediation:* actually run the
committed stub over the same manifests (in-process or subprocess) and require it to meet
zero non-clean cases, or reword the control to what is computed.

### LOW

- **L1** `--work` pointing at a regular file → `NotADirectoryError` traceback, rc=1, both
  counters (`mkdir`/`parents=True`); `--expected /nonexistent/exp.tsv` → `FileNotFoundError`
  traceback, rc=1. Wrap in `CANNOT-EVALUATE` (exit 2).
- **L2** `c2-counter.py --selftest` is not rerunnable in the same `--work`:
  first `rc=0`, second `rc=1` `fixture build failed: ('git','commit','-q','-m','fixture base')`
  (the reused repo makes the base commit empty). c1 is idempotent (fixtures are rmtree’d).
  *Remediation:* remove/re-init `--work/c2-fixtures/repo`, as the C1 builder does.
- **L3** Manifest that is a FIFO blocks (timeout 5 → rc=124). Receipt FIFO is safe.
- **L4** 1 MiB token echoed whole (C1 stdout ~1 MiB; C2 1,048,662 bytes).
- **L5** An instrument that is a **tree** is accepted end-to-end: `record-receipt.sh` stores
  the digest of `git show rev:census/round-57` (tree listing), and the gate recomputes the
  same listing → `SUMMARY receipts=1 findings=0 rc=0`. `instrument_sha256` therefore does
  not prove “blob”. *Remediation:* require `git cat-file -t rev:instrument == blob` in both
  the recorder and the gate.
- **L6** `--work` must pre-exist; the prereg’s matrix command omits the `mkdir` (see §1.3).
- **L7** `__pycache__` written into the frozen round dir by non-`-B` imports (see §1.3;
  includes my disclosure).

Observation, not counted as a finding: the gate binds the **first** `rev=` token anywhere in
the receipt (prose and fenced examples included) and accepts any `EXIT=<int>` line as the
exit marker; this matches the prereg’s literal predicates (`rev=` token, `EXIT=` line) and
the recorder emits `rev=` before command output, so produced receipts are safe. Worth a
named limit if the gate is reused on hand-written receipts.

---

## Claim-adjacent confirmations on this session’s own run

- **C1 T1/T2/T3:** B4 and C4 exit 0 under v5 and 1 under v6 with
  `CORRECTION-IN-FENCE,CORRECTION-IN-FENCE` and each detail `hidden_by=inline` (manual;
  see M9 for the assertion gap); C6, F29, F17, F18, F19 exit 0 under both arms; exactly two
  of 36 rows change between arms; all other rows identical (full TSVs in `receipts/`).
- **C1 T4/T5:** v5 exit-0 = 10/36, v6 = 8/36; `SELFTEST pass cases=36` with the all-findings
  assertion (the M1 mutation record is consistent: first-finding-only survives, all-findings
  kills).
- **C1 T6/T7:** not re-run against the lane tip by me (that is the executor’s receipt);
  every receipt I cite in this report prints an `EXIT=` line.
- **C2 T1:** `--manifest manifests/before.tsv` → exactly one finding
  (`RECEIPT-REV-MISSING census/round-56/records/landing-suite-final.txt`), rc=1;
  `grep -cE '^rev=[0-9a-f]{40}$'` on that receipt = 0.
- **C2 T3:** `SELFTEST pass cases=8`, rc=0, `control=FALSE-GREEN-REJECTED stub_meets=1`
  (see M10 for what that line actually measures).
- **Reproducibility:** my official-shaped matrix run equals the committed dry-run TSVs byte
  for byte; the recorder’s normal-run digest equals the prereg pin
  `e18872d6…` for `c1-counter.py`.

## Positives that held under attack

- Final-component symlink receipts and broken symlinks are refused without any read
  (syscall proof), and FIFO receipts are refused in ~50 ms — **no hang**.
- Real-lane modes perform no writes (only `/dev/null` config opens).
- `--work`/`--scratch` steer every write in a clean environment (0 outside events across the
  36-fixture selftest); `TMPDIR` is not consulted at all.
- The matrix driver reproduces the frozen dry-run byte for byte and writes only `$OUT`.
- `record-receipt.sh` refuses short/non-hex revisions before running the command and its
  normal receipt carries `rev=` (full 40), `instrument_sha256=` (the lane blob) and `EXIT=`.
- `durable_kind` correctly distinguishes branch-reachable, jj-keep-only and absent revisions
  (selftest cases KEEP-ONLY/ABSENT); a receipt outside the root is still graded against the
  root’s git.

## Scratch / cleanup

All work was done in `$S` and `$S/attacks`, `$S/c2attacks` (own git repos, toplevel asserted
before every commit). Scratch and all fixture repos were deleted before yield; the receipts
kept are under `w1/S57sentinel01/receipts/`. No subagent, no background job, no tool
installation, no write to the lane repo, `.ufo/state/`, or any frozen byte. The only lane
artifact I caused is the disclosed `census/round-57/__pycache__/c1-counter.cpython-314.pyc`
(non-`-B` import in an eval cell); it is untracked and does not alter the frozen sources.
