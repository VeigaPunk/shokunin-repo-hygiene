# S61ReviewerC2 — C2 receipt-writer operability review (round 61)

Scope: design + r60 bytes (`tests/fixtures/r60-receipt-write.py`, `tools/souji-receipt-write.py`).
`.ufo/waves/round-61/w1/S61ExecC2Fixture/` was **empty** at review time (rechecked at the end: 0 files),
so the new 10-case fixture, the two new cases, and the counter implementation were NOT attacked as
code; findings on them are design-level and must be re-checked when delivered.

Environment: git 2.56.0 (`git --version`); strace present at /usr/bin/strace (used, not installed);
/fast and /tmp are xfs, /dev/shm is tmpfs. No tools installed by this seat. All fixture repos lived
under my scratch dir, each verified with `git -C D rev-parse --show-toplevel == D` before use; scratch
removed at the end. The lane was never mutated.

## Severity-graded findings

### HIGH-1 — The honest writer accepts skip-worktree concealment of a NON-instrument tracked file
The dirty check (`tools/souji-receipt-write.py:131`, `git status --porcelain`) is blind to
skip-worktree entries, and the byte-binding (line 173, `wt_bytes != blob.stdout`) covers only the
instrument. So a tracked file the wrapped command reads can be tampered and hidden, and the writer
still emits a receipt at a clean-looking rev.

Evidence (repro, scratch fixture `swtest2`):
```
committed tracked.txt @rev = "clean"
printf 'tampered-source\n' > tracked.txt; git update-index --skip-worktree tracked.txt
git status --porcelain  -> []            (empty)
python3 -B souji-receipt-write.py --root D --rev REV --instrument tools/instrument.sh \
    --out OUT --allow-outside -- cat tracked.txt ; echo rc=$?   -> rc=0
receipt:  instrument_sha256=8f513b9f... rev=353174a1... command=cat tracked.txt
          tampered-source
          EXIT=0
```
The receipt binds rev, yet the recorded output comes from bytes that are not at rev. This defeats the
"clean lane tree" invariant for the receipt.

Candidate guard (tested in scratch): refuse when any `git ls-files -v` line starts with `[a-zS]`
(`S` = skip-worktree, `h`/lowercase = assume-unchanged).
- Tampered skip-wt repo: `git ls-files -v` prints `S tracked.txt` → guard fires ("concealment flag present").
- Clean repo after `--no-skip-worktree` + checkout: no flagged lines → guard clean (no false positive).

Required action: (a) either fix the writer with the guard above, or (b) the new C2 case set must
include a non-instrument concealed-divergence variant so the fixture pins it. A case that covers only
the instrument leaves this hole in the honest writer, which would still "pass" the 10-case fixture.

### HIGH-2 — Partial-visibility detection is timing-dependent; a sampling reader can miss the mutant
Measured against the chunked-publish mutant (`mutant-chunked.py`: `O_CREAT|O_EXCL` on OUT after the
command completes, then 4 KiB `write`+`flush` chunks, 51 writes for 200 KB). Detection = at least one
observed OUT size strictly between 0 and final. 20 trials each:

| reader | payload | detected/20 |
|---|---|---|
| busy-poll (no sleep) | 200 KB | **20** |
| sleep 1 ms | 200 KB | **1** |
| sleep 5 ms | 200 KB | **0** |
| sleep 1 ms | 250 KB | 1 |
| sleep 1 ms, tmpfs (/dev/shm) | 200 KB | 1 |
| busy-poll | 150 B | 0 (expected: single chunk) |

Honest writer, busy-poll, 200 KB: **0/20** trials show a partial state (first observed size is the
final size). The write window is roughly 8–10 ms on this host; a fixture reader that sleeps between
polls will almost never see it, so the case would pass the mutant and the mutant would survive.

Required design: the continuous reader must busy-poll with no sleep (separate process, or C-level
loop; a Python thread shares the GIL with the stat loop and was not tested), use a payload near the
256 KiB default `--max-bytes`, run N trials, and require mutant detection on every trial. Pass criteria
for the honest writer: zero partial states over N trials. Not tested: detection under host CPU load,
and busy-poll on tmpfs (only sleep-1ms on tmpfs was measured).

### MEDIUM-1 — r60 case 4 (kill-residue) never reaches the honest writer's temp path
The honest writer creates its temp only AFTER the wrapped command finishes (`proc.wait()` at line 217,
`mkstemp` at line 244). Case 4 SIGKILLs at 0.4 s into a 1 s command (`time.sleep(0.4)`, fixture line 252),
so no temp ever exists when the kill lands. The case catches early-temp mutants (a temp created before the
command would survive SIGKILL), but it exercises nothing about the honest temp+link code. Do not cite it
as evidence of temp-residue safety; the honest temp path is only covered by the case-3/case-1 "no temp" checks.

### MEDIUM-2 — Link failure exits 1 with a traceback, not the documented refusal code 2
Line 254–255 catches only `FileExistsError`. Any other `os.link` OSError (e.g. EPERM on a filesystem
without hardlinks) propagates. Simulated by monkeypatching `os.link` to raise `PermissionError` in-process:
`eperm-writer-rc=1`, Python traceback on stderr, OUT absent, temp removed by the `finally` (`temp left: 0`).
The writer's own contract says every refusal is exit 2 (`refuse()` docstring). Not tested on a real
no-hardlink filesystem.

### LOW-1 — Receipt file mode is 0600
`mkstemp` creates the temp 0600 (strace: `openat(... O_CREAT|O_EXCL ..., 0600)`), and `link` publishes
that inode. `stat` on a honest receipt: `600`. The mutant with `O_CREAT` writes 0644. The r60 contract is
silent on mode; any reader running as another account will fail to read the receipt.

### LOW-2 — Fixture dirty coverage is untracked-only
r60 case 8 adds an UNTRACKED file. Modified-but-not-concealed tracked files are not in the fixture. The
honest writer does refuse them (verified: a modified tracked instrument without skip-wt → `refused:
lane worktree is dirty ... rc=2`), but no case pins it. Concealment (HIGH-1) lives in exactly that gap.

### LOW-3 — Ignored files are not bound
`git status --porcelain` lists neither ignored nor concealed content; a command that reads an
ignored file is not bound by any check. Not tested; design limit to record.

## Verified (named mutants, r60 fixture bytes, git 2.56.0)

- **Concealed-divergence (instrument), honest writer**: `git update-index --skip-worktree tools/instrument.sh`,
  worktree bytes `TAMPER` ≠ committed. `git status --porcelain` → empty (concealed, confirmed). Honest
  writer → `refused: worktree tools/instrument.sh differs from committed bytes at <rev>`, **rc=2**, OUT absent.
  The refusal comes from the byte compare (line 173), not the dirty check. `--assume-unchanged` gives the
  same result (rc=2). Deleted instrument + skip-worktree → `refused: cannot read worktree instrument` rc=2.
- **Clean control** (same fixture, no tamper): writer → RECORD rc=0, digest `8f513b9f…` = `git show REV:tools/instrument.sh | sha256sum`.
- **Mutant wt-hash** (`mutant-wt-hash.py`: hashes worktree bytes; built by replacing the blob read at
  line ~160 with a worktree read): on the concealed instrument it emits a receipt with
  `instrument_sha256=ae07251a…` (worktree) vs committed `8f513b9f…` → rc=0 (the wrong digest is confirmed).
  **Old-case kill power: r60 fixture on the mutant → 8/8 pass, SUMMARY pass=8 fail=0, exit 0.** The old
  cases never diverge worktree from committed bytes (case 8 only adds untracked), so the mutant is
  indistinguishable on all eight — the named r60 gap is confirmed. The new concealed-divergence case
  kills it (the honest writer refuses, the mutant does not).
- **Mutant chunked** (`mutant-chunked.py`): **r60 fixture → 8/8 pass, exit 0**. Confirms the named gap.
  Strace (`mutB`): `openat(OUT, O_WRONLY|O_CREAT|O_EXCL, 0644)` then **51** `write()` calls. Honest writer
  strace: `openat(tmp, O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW, 0600)` → `write` → `fsync(3)` →
  `linkat(tmp, OUT)` → `unlink(tmp)` → `fsync(dirfd)`. OUT is never opened for write; it appears only through
  `linkat`, which is atomic and only ever links a fully-written, fsync'd inode.
- **Skip-worktree on git 2.56.0**: concealment survives `git status --porcelain` (empty output, rc=0).
  `git ls-files -v` shows `S tracked.txt`.

## Counter / fixture design (r60 bytes)

- **Order independence (verified)**: `order_probe.py` ran the 8 case functions in forward, reverse and
  shuffled order (`[1,4,6,3,7,5,2,8]`) against the honest writer and against the chunked mutant. Verdicts were
  identical in all three orders for both tools. Each `build_case(n)` removes and recreates `case-n/`, so case
  dirs are not reused within a run. Control stubs run in separate `control-always-write/` and
  `control-always-refuse/` subdirs, and `stubs/` is regenerated each run.
- **Shared state between arms**: none found in the r60 code. Cases 3 and 4 use `start_new_session=True`, so
  `killpg` in case 4 targets only the tool's own process group. Case 4's `killpg` is wrapped in a
  `ProcessLookupError` guard.
- **Fake-kill check**: the controls are scored by failed-case set (always-write must fail {2,4,5,6,7,8}; always-refuse must fail 1). Fine for r60. The new counter's killed_old/killed_new/pass/fail logic was not delivered, so it is not attacked. Re-check required: count killed_new only from the mutant that is killed by the new case and not by the old, and require the honest writer's 10-case pass on the same run.

## Verification gaps (not run)

- The new 10-case fixture and the counter were not delivered (`S61ExecC2Fixture` empty); not run.
- Partial-visibility not measured under host load; not measured on tmpfs with a busy-poll reader.
- Link EPERM simulated by monkeypatch, not on a real no-hardlink filesystem.
- Mutant "per-chunk fsync" variant (which would widen the window) was not built.
- No ignored-file test.
- No tool installs; strace used from /usr/bin.

## Recommended fixes (for the L1)

1. Add the `ls-files -v` `[a-zS]` guard (or equivalent) to the honest writer before the dirty check, and add a non-instrument concealed-divergence case to the C2 fixture.
2. Build the partial-visibility case around a busy-polling reader, a ~250 KB payload, N trials, with mutant detection required on every trial and honest zero partials.
3. Add a modified-tracked (non-concealed) dirty case to the fixture.
4. Widen the link exception handling to refuse with exit 2 on any `OSError` from `os.link`, and consider the 0644 mode.
5. Note in the r60 fixture docs that case 4 does not exercise the honest temp path.
