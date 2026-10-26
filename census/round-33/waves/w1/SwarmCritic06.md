# SwarmCritic06 — C1 K06 falsification (SCORECARD.md:158, `python3 tests/fixtures/r16-landing-gate.py`)

**Verdict: HOLDS.** Not NONDETERMINISTIC (6/6 byte-identical runs), not STRICT-PREDICATE (predicate = the cell's own
count), and not LAX for any class the fixture's 15 cases exercise; one saturation boundary and one environment
sensitivity are recorded below as attacks with reproduced state.

## Status

STATUS: PASS — at the prereg revision the frozen argv reproduces the row's stated `15/15` (rc=0, last line
`SUMMARY total=15 failed=0`) identically across five environment variants and two working directories; the frozen
predicate `\b15/15\b || \btotal=15\b && \bfailed=0\b` with exit 0 is a faithful, non-stricter reading of the cell; the
frozen C1 counter printed `AGREE` / `mismatches=0` on two independent runs. Two boundaries are reproduced as attacks
(F3 saturation by an uncovered row-claimed class, F4 `/var/tmp` hardcode) and neither falsifies the frozen item.

## Evidence

Measured revision: `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` (prereg commit; `6017a482e7068d5afb7617640198fbb0fe743357`
is its ancestor, verified with `git merge-base --is-ancestor`). Scratch clone
`/fast/scratch/hyaku/souji-r33/AuditK06/c`, `git clone -q --no-local`, origin removed, detached at that rev,
`git -C <clone> rev-parse --show-toplevel` printed the clone, `git status --porcelain` empty.

**Cell text (byte-identical at base and at the list-rev; `cmp` reported equal).**
`6017a482e7068d5afb7617640198fbb0fe743357:SCORECARD.md:158` (435 bytes, reproduced verbatim):

````
| landing-claim gate | flag, at a named revision, registry-cited scripts that do not parse, frozen pins or measured commits that disagree with committed bytes, and contract STATUS failure lines not carried into the round lesson; never executes repository code | `python3 tools/souji-landing-gate.py --selftest` 18/18; `python3 tests/fixtures/r16-landing-gate.py` 15/15; replays in `corpus/lessons/round-16.md` Gate; S043, S050 | r16 |
````

The claim under test is this command's outcome: **`python3 tests/fixtures/r16-landing-gate.py` → 15/15** (item row
`census/round-33/c1-items.tsv:22`: exit `0`, predicate `\b15/15\b || \btotal=15\b && \bfailed=0\b`).

**Determinism — six runs, identical output (md5 `8965373b51770e58de9d5cd223c462fa` for all six files).**
Run from the clone root unless stated; env scrubbed except PATH/HOME/GIT_CONFIG_NOSYSTEM and the TMPDIR noted:

| run | TMPDIR | rc | last line |
|---|---|---|---|
| 1 | `<scratch>/tmp1` (fresh) | 0 | `SUMMARY	total=15	failed=0` |
| 2 | `<scratch>/tmp2` (fresh) | 0 | `SUMMARY	total=15	failed=0` |
| 3 | unset | 0 | `SUMMARY	total=15	failed=0` |
| 4 | `/nonexistent-audit-k06` | 0 | `SUMMARY	total=15	failed=0` |
| 5 | `<scratch>/tmp1`, under `strace -f` | 0 | `SUMMARY	total=15	failed=0` |
| 6 | `<scratch>/tmp2`, cwd `<clone>/tests` | 0 | `SUMMARY	total=15	failed=0` |

15 `CASE` lines, all `PASS`, stderr empty (0 bytes) in every run. First and last case lines:
`CASE	replay-b410186	PASS	exit=1 lg_rows=5` … `CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions
failed as required: yes`.

**Frozen counter (item 4), run twice, scratch `.../cnt` and `.../cnt2`, identical:**

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/AuditK06/cnt --only K06
ITEM	K06	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=15 failed=0
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
rc=0
```

**Mutation runs (throwaway copies of the same clone at the same rev, no origin, no commits made):**
- M1 gate replaced by a 23-byte `import sys; sys.exit(0)` stub → fixture `rc=1`, `SUMMARY	total=15	failed=14`.
- M4 `tools/souji-landing-gate.py:398` `if is_failure_line(...)` → `if False and is_failure_line(...)` → fixture
  `rc=1`, `SUMMARY	total=15	failed=5`; red ids `replay-b410186` (`missing LG-SEAT-UNCARRIED ~ ConfigRepair.md`),
  `marker-one-char-off`, `marker-rewordings`, `carry-inside-html-comment`, `open-marker-admitted-true`.
- M5 `tools/souji-landing-gate.py:714` `elif actual != pinned:` → `elif False and actual != pinned:` (kills the
  `record_sha256` mismatch finding) → fixture **`rc=0`, `SUMMARY	total=15	failed=0`** (green), while the same mutant
  tool's selftest prints `rc=1`, `SELFTEST	pass=64	fail=1`. Unmutated selftest at this rev: `rc=0`,
  `SELFTEST	pass=65	fail=0`.

**Environment probes.** `TMPDIR=/nonexistent-audit-k06` still exits 0 (TMPDIR is not consulted). `strace -f -e
trace=mkdir,mkdirat` shows the fixture's scratch root created at `mkdir("/var/tmp/souji-r16-lgfixture-ydwqkd4i", 0700)
= 0` while the gate's own temp lands under the caller's TMPDIR (`mkdir("<scratch>/tmp1/souji-landing-gate-i8i2j_sf",
0700)`). In a **private** mount namespace (`unshare -rm --propagation private`, a scratch dir bind-mounted over
`/var/tmp` and remounted `ro`; host untouched, no host path modified): `rc=1`,
`OSError: [Errno 30] Read-only file system: '/var/tmp/souji-r16-lgfixture-v7y3rvdh'`, no `SUMMARY` line.

**Source quotes (≤25 words, no pipe characters, opened this run at the measured rev):**
- `tests/fixtures/r16-landing-gate.py:225-227`: `scratch = tempfile.mkdtemp(prefix="souji-r16-lgfixture-",` then
  `dir="/var/tmp" if os.path.isdir("/var/tmp")`
- `tests/fixtures/r16-landing-gate.py:527-528`: `failed = sum(1 for _, ok, _ in results if not ok)` and
  `print("SUMMARY\ttotal=%d\tfailed=%d" % (len(results), failed))`
- `corpus/QUALITY.md:176` (Q71): `A committed tool, counter, probe or fixture takes its scratch root from the caller's
  TMPDIR`
- `census/round-33/c2-counter.py:151`: `"--ro-bind", empty, "/tmp", "--ro-bind", empty, "/var/tmp",`

## Findings

1. **K06's frozen statement is current and deterministic.** `SCORECARD.md:158` states the fixture yields 15/15; at
   `2d9bca5` it yields 15 `CASE … PASS` lines and `SUMMARY total=15 failed=0`, exit 0, stderr empty, in six
   runs over two fresh TMPDIRs, unset TMPDIR, a nonexistent TMPDIR, under strace, and from a subdirectory. The
   fixture computes `failed` from the case verdicts and returns 0 only when it is 0 (`r16-landing-gate.py:527-529`), so
   the SUMMARY line cannot read `failed=0` while a case is red.

2. **The predicate is faithful, neither laxer nor stricter for covered classes.** The cell states exactly "15/15";
   `\btotal=15\b && \bfailed=0\b` plus the frozen exit 0 is that statement and adds nothing (no per-line or per-id
   requirement was imposed). It is not inert: a vacuous gate (M1) and a dead seat-failure channel (M4) both turn it
   red with `failed>0` and rc=1. The `\b15/15\b` alternative is inert at these bytes (the fixture never prints that
   token), so the matched alternative is always `total=15 && failed=0`.

3. **Saturation boundary (attack A3, reproduced).** `tools/souji-landing-gate.py:714-722` carries the
   `record_sha256` mismatch finding — a class the row claims ("frozen pins … that disagree with committed bytes") that
   no case in the 15 exercises. Killing it leaves the fixture green (`SUMMARY total=15 failed=0`, rc=0) while the tool's own
   selftest catches it (`pass=64 fail=1`). So **K06 alone does not certify the row's frozen-pin class**; the row's
   discrimination on that branch rests on the same cell's other command, `python3 tools/souji-landing-gate.py
   --selftest`, which is item K05 — enumerated, already a declared base mismatch, and stale in its stated form
   (`18/18`; the tool now prints `SELFTEST	pass=65	fail=0`, run this session). Not a defect of the frozen item (its
   stated outcome is the fixture's own count, which reproduces), but the L1 should keep K06 paired with a K05
   restatement rather than treat K06 as independent evidence for the pin-digest branch.

4. **`/var/tmp` hardcode makes this reading environment-sensitive (attack A5, reproduced).**
   `tests/fixtures/r16-landing-gate.py:225-227` pins the scratch root to `/var/tmp` and ignores TMPDIR; with `/var/tmp`
   read-only the fixture dies before any case (`OSError … Read-only file system`, rc=1, no `SUMMARY`), which the frozen
   (exit 0, predicate) pair scores as MISMATCH. On the host this is not triggered: C2's read-only O1 leg uses bwrap
   namespace binds (`c2-counter.py:151`), not a host-wide mount, so C2 cannot perturb the C1 tip reading; the exposure
   is a verifier who runs `c1-counter.py` inside a sandbox with a read-only `/var/tmp`, which would score a false
   MISMATCH against unchanged lane bytes.

5. **Residual scratch-discipline defect, outside this round's routed five.** The same lines (F4) are exactly the r32
   routed pattern — a hard-coded `/var/tmp` instead of the caller's TMPDIR — and Q71 forbids it
   (`corpus/QUALITY.md:176`). The r16 fixture is not in `census/round-33/c2-legs.tsv` (grep: only `c1-items.tsv:22`
   names it), and it is not one of O1-O5, so it is a legitimate r34 routed-defect candidate, **not** something to fix
   in this round: a `tests/fixtures/` edit is C2 surface and would break C1/C2 separability.

6. **Out-of-set sweep of the same cell: no stale residual found.** The cell's other count `18/18` belongs to K05
   (in-set, stale as shown in F3, cause class = value drift). Its pointer "replays in `corpus/lessons/round-16.md`
   Gate" still checks out: the lesson's replay assertion (that section, line 21: `--rev b410186 --round 15` → exit 1, 5
   findings) reproduces as `CASE	replay-b410186	PASS	exit=1 lg_rows=5`. Sources `S043` and `S050` are present
   (`corpus/SOURCES.md:64,71`). The qualitative claim "never executes repository code" still holds at this rev: the
   gate's every exec site is git plumbing (`tools/souji-landing-gate.py:221-227`), `bash -n` over a snapshot copy
   (`:317-318`), and re-invocation of the gate itself in its selftest (`:1750-1757`); no repository script is run.

## Attack log

- **A1 determinism.** Two fresh TMPDIRs, unset TMPDIR, nonexistent TMPDIR, strace wrapper, shifted cwd → 6/6
  byte-identical output, rc 0. NONDETERMINISTIC refuted.
- **A2 lax via regressed tool (covered classes).** M1 vacuity stub → `failed=14`, rc=1. M4 dead seat-failure channel →
  `failed=5`, rc=1. Predicate discriminates. LAX for covered classes refuted.
- **A3 lax via uncovered row-claimed class.** M5 neutralized `record_sha256` mismatch → fixture green
  (`SUMMARY total=15 failed=0`), tool selftest red (`pass=64 fail=1`). Reproduced; recorded as a coverage boundary (F3), not
  a predicate-fidelity defect — the row's stated outcome for this command is the fixture's count.
- **A4 stricter-than-stated.** Predicate = 15 cases, none failed, exit 0 = "15/15"; no line-level or id-level demand.
  STRICT refuted.
- **A5 environment.** Read-only `/var/tmp` (private namespace) → OSError, no SUMMARY, rc=1 → would score MISMATCH on
  unchanged bytes. Recorded (F4); C2's bwrap legs verified not to create this state on the host.
- **A6 same-cell other counts.** `18/18` stale but in-set (K05); replay count and both source ids current; no
  out-of-set residual.

Frozen predicate, target, counter, item and leg were not changed or proposed to be changed; no lane file was edited
by this seat. No tool was installed or upgraded (no pacman, no uv/npx/binary install needed). Nothing outside the lane
repo was written: the read-only `/var/tmp` state existed only inside a private mount namespace.

## Deliveries

- `.ufo/waves/round-33/w1/SwarmCritic06.md` (this report).
- Scratch `/fast/scratch/hyaku/souji-r33/AuditK06` removed after copying these receipts (all mutant clones, run
  outputs, strace log and counter scratch were inside it).
