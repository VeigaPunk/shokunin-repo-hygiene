# R92Sentinel: robustness and safety of the C2 cut and the C1 survivor search (souji r92)

Seat: R92Sentinel (sentinel, leaf, no subagents). Lane base 5339b2ac. Lane read-only; no git/jj mutation; no edits to
MANIFEST, .ufo/state, .scratch, watchdog. Receipts (text only) in `.ufo/waves/round-92/w1/R92Sentinel/`. Scratch
`/fast/scratch/hyaku/souji-r92/R92Sentinel/` deleted before yield. Tools: no install, no upgrade (`/usr/bin/strace`
was already present and was used read-only for tracing). Sentinel scripts `probe_one_line.py`, `inject.py`,
`sigtest.py` in the seat dir reference the scratch path; they rebuild their own kits under it when re-run.

FALSIFIES-WORDING: none.
FALSIFIES-NUMBER: none.
NO-FALSIFICATION (C2): item 1 (adversarial stderr through `_one_line_bytes`), item 2 (public-path injection), and the
fuzz check of the prefix/suffix property found nothing that contradicts the C2 sentences. Details below.
NO-FALSIFICATION (C1): this seat ran `--ids` on two of the 47 targets only (a214c12-==-to-!=, a222c19-!=-to-==); both
killed with rc 1, consistent with the predicate. I did not re-run the full 47, the control, or the pristine harness.

Predicates re-run under strace (outputs in the seat dir, `c2a.out`, `c2b.out`, `c2c.out`): C2 fixture
`SUMMARY cases=20 tool_pass=20 before_pass=16` rc 0; forgery probe `FORGERY-SUMMARY forgeries=5 rejected=5
positive=pass` rc 0 (N0 rejected 16/20); r87 K4 `SUMMARY rows=12 mismatches=0 errors=0` rc 0.

## Findings (ranked)

### MEDIUM M1: SIGKILL of the survivor search leaves one harness clone per in-flight mutant
- Repro: `sigtest.py kill` (SIGKILL to the search parent at +10 s, `--jobs 2`, two ids). Output `s2.out`.
- Observed: parent rc -9. `du -sb` of `--work` is 646,523,972 bytes at +10 s and still 646,523,972 at +20, +40, +60 s.
  Left: `m0000/w/fixture` and `m0001/w/fixture` (forge-*.tsv, full clones). No harness process survives the parent,
  and no `harness.out` is written, so the orphans die (most likely on the broken stdout pipe) and never reach
  `shutil.rmtree` in `score()`.
- Impact: about 0.65 GB per in-flight mutant; with `--jobs 4`, one kill strands about 2.6 GB. A re-run needs an empty
  `--work`, so an operator must clean up by hand. The clean-run path is fine (see item 3).
- Smallest fix (not applied; lane frozen): wrap the harness call in `score()` in try/finally that removes `d/w`, and
  have the parent kill process groups on SIGTERM/SIGINT before it exits.

### LOW L1: SIGINT drains the queue instead of stopping the search
- Repro: `sigtest.py int` (SIGINT at +6 s, `--jobs 1`, two ids). Output `s3.out`.
- Observed: the parent exits 34.8 s after the signal with a KeyboardInterrupt traceback (rc -2). The queued mutant still
  ran: `m0001/harness.out` exists. `--work` is 83,398 bytes afterwards, so this path leaks nothing; it only fails to
  stop.
- Cause: the `with cf.ThreadPoolExecutor` exit calls `shutdown(wait=True)` with futures still pending.
- Smallest fix: `ex.shutdown(cancel_futures=True)` in an except-KeyboardInterrupt branch.

### LOW L2: the `--work` guard misses the bare /tmp, /var/tmp and /dev/shm paths
- Repro: `os.path.realpath("/tmp").startswith(("/tmp/","/var/tmp/","/dev/shm/"))` is False (same for the other two).
  `c1-survivor-search.py --work /tmp` exits 2 only with "not empty" (/tmp is not empty here). An empty /tmp or
  /dev/shm would be accepted, and mutant trees would be written there.
- Same tuple test: `c1-survivor-search.py:125`, `c1-false-row-harness.py:393`, `c2-forgery-probe.py:70`,
  `r92-k4-flagfail.py:406`.
- Smallest fix: `p == root or p.startswith(root + "/")`.

### LOW L3: fixture git writes freshen objects in the LANE's `.git` (mtime only)
- Cause: the harness clones with `git clone --shared` (alternates point at the lane's object store). A git write of an
  object the lane already holds utimes the lane's loose object or pack. Content is not changed.
- Reproducer (scratch demonstration): source loose object mtime set to 2000-12-31; `git -C B hash-object -w` of the same
  blob in a `--shared` clone; the source object's mtime became 2026-11-09 00:12:58. Content unchanged.
- Lane evidence: `.git/objects/pack/pack-96aeb1765f9627698b304e08b017662532cbe6b3.pack` mtime 2026-11-09 00:12:31
  while its `.idx` is 2026-10-29 00:35:54; loose `.git/objects/68/1a91217d59d0be1adbfdd276c1b4da490c84d0` (a 30,863-byte
  blob) has the same 00:12:31 mtime. Timing puts these in this seat's runs, not proven by pid (siblings also run
  harnesses).
- Answer to item 3's "writes outside --work": yes, but only timestamps in the lane's object store. No lane file content
  changed, and no lane path was created by the search (see item 3).
- Smallest fix: `git clone --no-local` (copies objects, no alternates) in `build_fixture`.

### LOW L4: fixture symlinks point outside --work (latent escape route)
- The harness plants symlinks inside `--work` whose targets are absolute lane paths or `/dev/null`. Traced in s1:
  `tests/vault/vadv54-run/p/alias-link.md -> <lane>/tests/vault/vadv54-run/p/p2.md`, `.../q/led-devnull.tsv -> /dev/null`,
  `.../q/led-outside.tsv -> <lane>/tests/vault/vadv54-run/elsewhere/led-outside.tsv`, and others. `copytree(symlinks=True)`
  copies the lane's symlinks as they are.
- Observed: no write-mode open in the three traced runs resolves through one of these links. The 47 symlinks at BASE do
  not include any `put()`/append target (checked against `git ls-tree` of 5339b2ac).
- Latent risk: a future `put()` or append aimed at one of them writes into the lane or `/dev/null`.
- Smallest fix: `put()` refuses any path with a symlink component, or opens with `O_NOFOLLOW`.

### LOW L5: the rendered cell is not bounded at 202; the bound is on raw octets (observation, no claim falsified)
- The 202 bound is on the raw window (the docstring says so). Rendered cells are longer: 10 MB of 0x80 renders to 797
  characters (799 UTF-8 bytes); 10 MB of NUL to 797 characters; the public-path NUL run to 856 characters. The raw window
  stayed at or under 199 octets in every case (`probe-one-line.out`, `inject.out`).

### LOW L6: format characters and noncharacters pass `_escape_text` unescaped
- `_escape_text` escapes C0, DEL, U+0085, U+2028/2029, and surrogates. It does not escape category Cf (bidi U+202E,
  U+2066-2069, zero-width characters) or noncharacters.
- Repro (public path): `inject.out` case `bidi-rlo-report-only` puts raw U+202E into the K4 cell. Case
  `u10ffff-noncharacter` puts raw U+10FFFF there. Neither creates a second row or splits a line. A terminal may show the
  detail reversed. The C2 claim covers ill-formed bytes, separators and controls, so this is outside its wording.

### LOW L7: the forgery probe and the C2 fixture leave residue under --work
- After the run: `c2b/work` (forgery probe) 1,017,102 bytes; `c2a/work` (fixture) 136,542 bytes. The fixture docstring says
  it "removes what it builds". Nothing touched /tmp.

## No finding (what was tried)

Item 1 (adversarial stderr through `_one_line_bytes`), `probe-one-line.out`:
- 2,028 length-boundary cases: sizes 200-203, 28 byte tokens (valid, overlong, surrogate-encoded, truncated, C0/C1/F5+,
  F4 90+, NEL, LS, NUL, ESC, random) placed at offsets 92-109, plus three hand-made A/B and control payloads. `fails=0`.
- 33,000 random payloads of 196-3000 bytes. Each is checked for one line, no raw separators or controls, and head
  prefix / tail suffix of `_escape_text(_decode_record(raw))`, independent of the cut helpers. `fails=0`.
- 10 MB inputs (0x80, F4 8F BF BF, NUL, ED A0 80, C2 85, E2 80 A8, E2 82 truncated, random bytes, mixed tokens, plus
  201/202-byte straddle samples): no exception, time under 1 ms, one line, raw window at most 199 octets. The
  `_one_line_bytes` cut path never sees a clamped `t < h` for len > 200.

Item 2 (injection through the public path), `inject.out`:
- Hermetic kit: a tool copy plus a fake writer whose `git()` returns a payload file as stderr with rc 1, which drives the
  FLAGFAIL branch with real base64 framing. Tool run as a subprocess; MISMATCH rows read back as a line consumer would.
- 16 small payloads (LF, CR, NEL char and byte, LS, PS, TAB, VT/FF/FS/GS/RS, ESC, bidi, U+10FFFF, 200-203 ASCII), 80
  boundary payloads (n=201-260, injected line at offsets 92-107 with four separators), 24 tail-straddle payloads, and five
  10 MB payloads (repeated injection line, F4 8F BF BF, NEL, NUL, 0x80).
- Every run: exactly one `MISMATCH\tK4` row with 5 tab fields, and no raw CR, LF, NEL, LS, PS, TAB or other control in the
  cell. The `SUSPECT` tags in `inject.out` are my own heuristic misfiring on escaped text; the raw-separator field is the
  real test and is empty in every case.

Item 3 (survivor search), `s1.out`, `s1-search-write-syscalls-under-work.txt`:
- `--work` under /tmp, /var/tmp, /dev/shm, and a symlink whose target is under /tmp: refused with rc 2 before any write
  (`--work /tmp` only by the non-empty check; see L2).
- Two targets, `--jobs 2`, strace (TMPDIR set to an empty probe dir): both `SEARCH ... killed=yes rc=1`,
  `SEARCH-SUMMARY generated=2 ... killed=2 survived=0`. `du -sb --work` afterwards: 83,398 bytes (two `harness.out` and
  two counter copies); no `w` trees left. The per-mutant rmtree works on the clean path.
- Every write-mode syscall the search tree made fell under `--work` (the fixture clones, counter copies and `harness.out`),
  except the external effects in L3 (lane object mtimes) and L4 (symlink targets, not written through). I checked
  relative-path writes by confirming the pids' cwd is not the lane: they created `.ufo/waves/round-22/w1/
  original-failed-seat-continuation.txt` with O_EXCL, and that file exists in the lane.
- Killed-run behaviour: M1. Ctrl-C behaviour: L1.

Item 4 (/tmp writes), `tmp-access-counts.txt`:
- strace with TMPDIR pointing at an empty probe dir, for the search and the three C2 instruments (fixture, forgery
  probe, r87 K4 counter): zero syscalls naming /tmp, /var/tmp, /dev/shm or the probe dir; the probe dirs stayed empty.
- Receipt writer `tools/souji-receipt-write.py`: all five `tempfile` call sites pass `dir=` (lines 771, 820, 857, 1066,
  1703). Its self-test sets `TMPDIR` to a work subdir inside its own selftest only.
- `souji-record-agreement.py`, the C1 harness and search, the C1 counter, and the C2 fixture and probe do not import
  tempfile. The only /tmp strings are guard messages.

## Receipts (seat dir `.ufo/waves/round-92/w1/R92Sentinel/`)
`probe_one_line.py`, `probe-one-line.out`, `inject.py`, `inject.out`, `sigtest.py`, `ids2.json`, `s1.out`, `s2.out`,
`s3.out`, `c2a.out`, `c2b.out`, `c2c.out`, `tmp-access-counts.txt`, `s1-search-write-syscalls-under-work.txt`.
