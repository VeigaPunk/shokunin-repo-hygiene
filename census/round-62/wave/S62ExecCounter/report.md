# S62ExecCounter — C1 counter delivery report (souji round 62, wave w1)

Seat: S62ExecCounter (leaf executor, one seat of the single v1 wave).
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, base
`16fa821fdce00e709d6895ccfc7aaffa465af195` (verified present; `git rev-parse HEAD`
printed the same hash and `git status --porcelain` was empty at round start, rc=0).

## Delivered files (absolute paths)

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ExecCounter/c1-counter.py`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ExecCounter/c1-matrix.tsv`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ExecCounter/do-nothing.txt`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ExecCounter/stubs.txt`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ExecCounter/SHA256SUMS`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ExecCounter/report.md` (this file)
- Scoped findings: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ExecCounter.md`

No lane production file was touched; the lane was only read (`git show`, `rev-parse`,
`cat-file`, fixture read). Scratch `/fast/scratch/hyaku/souji-r62/S62ExecCounter/` was
removed before yield. No tools were installed (stdlib sufficed; nothing recorded under
the tooling authorization).

## Frozen expectation files

`c1-matrix.tsv` (233 bytes, tab-separated):

```
case	expect	expected_class
A	accept	-
B	accept	-
C	refuse	lane worktree is dirty
D	refuse	RECEIPT-INDEX-FLAG-CONCEALED
E	refuse	RECEIPT-INDEX-FLAG-CONCEALED
F	refuse	RECEIPT-INDEX-FLAG-CONCEALED
G	refuse	RECEIPT-INDEX-FLAG-CONCEALED
```

## Counter semantics (as implemented)

- CLI: `python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv --base-rev FULL40
  --rev FULL40|none --tool PATH --work DIR [--arm tool|plain]`.
- Base slot bytes: `git -C ROOT show <base-rev>:tools/souji-receipt-write.py` →
  `WORK/slots/base.py` (sha256 `367a0ca3bdea35714f1c1dba7bca407f05e8ec8d8f6e9c16f071d6e20e503d2c`,
  identical to the extracted bytes used for the self-checks). New slot: `WORK/slots/new.py`
  from `--tool` bytes (`--arm tool`) or the base bytes (`--arm plain`).
- Per case: fresh repo `WORK/<case>/repo` via `git init -q`; toplevel asserted equal to the
  repo dir before the first commit; local identity `C1 Counter <c1-counter@invalid>`;
  `GIT_AUTHOR_DATE=GIT_COMMITTER_DATE=2026-11-05T12:00:00Z`; one seed commit of
  `tools/instr.sh` (`#!/bin/sh\necho instrument-ok\n`, mode 755), `tools/counter.py`
  (`counter v1\n`), `tools/notes.txt` (`notes v1\n`); `REV = git rev-parse HEAD`.
- Mutations exactly as frozen: B/C append `dirty\n` to notes; D `update-index --skip-worktree
  tools/counter.py` + write `counter FORGED\n`; E same with `--assume-unchanged`; F
  `--skip-worktree tools/counter.py` with bytes unchanged; G `--skip-worktree tools/instr.sh`
  + write `#!/bin/sh\necho FORGED\n`.
- Each slot runs: `python3 -B SLOT --root REPO --rev REV --instrument tools/instr.sh --out
  OUT --allow-outside [--allow-dirty] -- sh -c 'echo ok'` with cwd=REPO. OUT is
  `WORK/<case>/out-base/receipt.txt` for the base slot and `WORK/<case>/out-new/receipt.txt`
  for the new slot — deliberately separate directories, because a base-slot accept would
  otherwise leave OUT present and destroy the new slot's refuse detection (the r60 writer
  refuses an existing OUT). The out dir is pre-created; the writer requires it to exist.
- Accept = exit 0 and OUT present; refuse = exit 2 and OUT absent; any other exit is an
  error verdict for the case. `findings` = the row's expected_class when it appears as a
  substring of that slot's stderr, else `-`.
- Regression arm: `python3 -B tests/fixtures/r60-receipt-write.py --tool SLOT --work W`
  run from the lane root (`cwd=LANE`), for BOTH slots — base bytes at `WORK/r60-base`,
  tool bytes at `WORK/r60`. REGRESS=PASS iff exit 0 and the last output line contains
  `pass=8 fail=0`; the fixture writes only under its `--work` (verified by reading its
  source: all writes are `mkdtemp(dir=work)` / case dirs / `work/stubs`).
- Exit 0 iff new_forgeries=0 ∧ new_honest=2 ∧ class_mismatches=0 ∧ regress=PASS ∧ every
  NEW verdict equals expect; else exit 1. Exit 2 = could not evaluate (bad rev, missing
  matrix, missing or /tmp|/var/tmp work dir, base bytes unreadable, unreadable --tool).

## Exact commands and observed outputs (all run by this seat)

### 1. Extract base bytes

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show \
  16fa821fdce00e709d6895ccfc7aaffa465af195:tools/souji-receipt-write.py \
  > /fast/scratch/hyaku/souji-r62/S62ExecCounter/base-writer.py
```
rc=0; `sha256sum` = `367a0ca3bdea35714f1c1dba7bca407f05e8ec8d8f6e9c16f071d6e20e503d2c`;
`wc -l` = 694. `git cat-file -e 16fa821…^{commit}` rc=0; lane `rev-parse HEAD` =
`16fa821fdce00e709d6895ccfc7aaffa465af195`; porcelain line count 0.

### 2. Do-nothing control (`--arm plain`, base bytes as --tool)

```
python3 -B .../w1/S62ExecCounter/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --matrix .../w1/S62ExecCounter/c1-matrix.tsv \
  --base-rev 16fa821fdce00e709d6895ccfc7aaffa465af195 --rev none \
  --tool /fast/scratch/hyaku/souji-r62/S62ExecCounter/base-writer.py \
  --work /fast/scratch/hyaku/souji-r62/S62ExecCounter/work-donothing --arm plain
```
Captured in `do-nothing.txt` (stdout+stderr, plus `counter_shell_exit=1`). Observed:

```
CASE A expect=accept base=accept base_findings=- new=accept new_findings=-
CASE B expect=accept base=accept base_findings=- new=accept new_findings=-
CASE C expect=refuse base=refuse base_findings=lane worktree is dirty new=refuse new_findings=lane worktree is dirty
CASE D expect=refuse base=accept base_findings=- new=accept new_findings=-
CASE E expect=refuse base=accept base_findings=- new=accept new_findings=-
CASE F expect=refuse base=accept base_findings=- new=accept new_findings=-
CASE G expect=refuse base=refuse base_findings=- new=refuse new_findings=-
REGRESS base=PASS new=PASS
SUMMARY matrix=7 base_forgeries=3 base_honest=2 new_forgeries=3 new_honest=2 class_mismatches=4 regress=PASS
EXIT=1
counter_shell_exit=1
```

Required shape `new_forgeries=3` and exit 1: MET. This is also direct empirical
confirmation of the round claim on the lane base: the base writer accepts the
skip-worktree-forged (D), assume-unchanged-forged (E) and skip-worktree-unmodified (F)
repos (rc=0, receipts written) while refusing C (`lane worktree is dirty`) and G
(`worktree tools/instr.sh differs from committed bytes`). `class_mismatches=4` is the
expected control artifact (D/E/F accepted, G refused with the instrument reason — none
carry the flag class) and is not part of the control's pinned shape.

### 3. Stub arms (counter must fail both)

Stub sources: `stub-accept.py` (parses `--out`, creates OUT, `sys.exit(0)` — the same
shape the r60 fixture uses for its always-write control) and `stub-refuse.py`
(`sys.exit(2)`). Both runs used `--arm tool` with the stub as `--tool`, captured in
`stubs.txt` (stdout+stderr, plus per-run `shell_exit=`):

- stub-accept: `SUMMARY matrix=7 base_forgeries=3 base_honest=2 new_forgeries=5
  new_honest=2 class_mismatches=5 regress=FAIL` / `EXIT=1` / `shell_exit=1`. (The r60
  fixture also rejects the stub as a tool: `REGRESS new=FAIL`.)
- stub-refuse: `SUMMARY matrix=7 base_forgeries=3 base_honest=2 new_forgeries=0
  new_honest=0 class_mismatches=5 regress=FAIL` / `EXIT=1` / `shell_exit=1`.

Both fail the counter as required.

### 4. Exit-2 negative probes (evidence only; captured in scratch, now removed)

```
C1-COUNTER-FATAL: work directory does not exist: .../does-not-exist        -> EXIT=2, shell_exit=2
C1-COUNTER-FATAL: work directory must not live under /tmp or /var/tmp: /tmp/c1-counter-negcheck -> EXIT=2, shell_exit=2
C1-COUNTER-FATAL: --rev must be full 40-hex or 'none', got 'HEAD'          -> EXIT=2, shell_exit=2
```

### 5. SHA256SUMS (final delivered bytes)

```
c6a3159d32b099ba1730a2cc23ffe6eafce40a2c264f6f019fa3e8f468a2150a  c1-counter.py
89abc018ad0715e306de66982fbdbb5d973824f3170ff7c37d647b2ab8ba0b23  c1-matrix.tsv
```
(written with absolute paths into `SHA256SUMS`, rc=0)

Per the freeze, the counter was NOT run with the candidate tool — the L1 runs that
after the freeze (frozen predicate: new_forgeries=0, new_honest=2, class_mismatches=0,
G refused, r60 fixture `pass=8 fail=0` with both controls rejected).

## Named limits

- No concurrency coverage: the counter does not test flock, simultaneous writers, or the
  writer's TOCTOU/link-publishing behaviour under races; every run is serial.
- No sparse-checkout coverage: `git sparse-checkout` and submodule/gitlink paths are not
  represented in the matrix; the candidate's flag scan sees only plain blobs in these
  fixtures. A sparse-checkout cone that sets non-`H` tags (`S`) on skipped entries would
  be refused by a strict candidate — untested here and a plausible false-refuse source on
  real lanes (today's lane index is all-`H`, so no honest run is blocked).
- Expected classes are stderr substrings: the counter checks that the expected_class
  string appears in the new slot's stderr; it does not parse refusal structure, does not
  check that the candidate names the offending path and tag individually, and does not
  verify HOW the candidate reads flags (e.g. `git ls-files -v -z` usage) — only the
  observable verdict.
- The gate applies to the NEW slot only; base-slot verdicts (`base_forgeries`,
  `base_honest`) are recorded, not gated.
- `class_mismatches` counts an accepted (or errored) refuse row as a mismatch, per spec.
- The matrix file is an input: the counter validates its shape (header, exactly rows A–G
  in order, refuse rows need a class, accept rows must use `-`) but takes the
  expectations from the file; the shipped file is the frozen one (sha256 above).
- Verdict mapping is exact-code based (accept=0+OUT, refuse=2+absent). A candidate that
  refused with a different nonzero exit code would be judged `error`, i.e. a claim
  failure — the frozen design refuses with exit 2 via the r60 writer's `refuse()` path.
- Fixture repos are single-branch seeds; no rebase/history checks, no signing, no
  worktrees, no symlinks in the C1 matrix (symlink handling is the r60 fixture's job).
- The regression arm runs the r60 fixture with cwd=lane; it does not prove the candidate
  handles lane-scale repos (17350 index entries), only behavior on small fixtures.
- Scratch timing: fixture signal-timing cases (case_3/case_4) passed on this host; a
  heavily loaded host could in principle flake them; re-run the counter to confirm.
