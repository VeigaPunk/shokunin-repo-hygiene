# S69ExecD10 — D10 read-through-symlink killed by `tools/notes-copy.txt` seed (SY3) only?

**Hypothesis (from seat assignment):** D10 (read-through symlinks) is killed by row SY3
only because of the `tools/notes-copy.txt` seed in `c1-counter.py` `build_repo_at()` seeds map.

**Verdict: CONFIRMED.** Without the seed D10 survives; with it D10 is a forgery kill.

## Experimental setup

- Copied `census/round-69/c1-counter.py` (sha256 40757709e5adef00…)
  to scratch `c1-counter-noseed.py` (sha256 6a0393b0882617c…)
  and removed the one seeds entry `"tools/notes-copy.txt": SEED_NOTES`
  from the `build_repo_at()` seeds map (line 381). The root-level
  `"notes-copy.txt"` seed remains. No other change (`diff` shows only
  the 6-line block collapse at lines 376–381).
- Ran `--only D10` battery from the lane root with both counters,
  using the frozen matrix/manifest/battery dir and fresh `--work` dirs
  under `/fast/scratch/hyaku/souji-r69/S69ExecD10/`:
  - unmodified: `.../work1` → `orig-D10.txt`
  - noseed: `.../work2` → `noseed-D10.txt`

## Observed outputs

| Run | MUTANT D10 line | BATTERY line | rc |
|---|---|---|---|
| unmodified counter | `MUTANT D10 outcome=forgery expected=forgery forgeries=1 echo=0 honest=0 label=0 errors=0 regress=PASS` | `BATTERY mutants=1 kills=1 label_only=0 over_refusal=0 echo_violation=0 survived=0 error=0` | 0 (EXIT=0) |
| noseed scratch counter | `MUTANT D10 outcome=survived expected=forgery forgeries=0 echo=0 honest=0 label=0 errors=0 regress=PASS` | `BATTERY mutants=1 kills=0 label_only=0 over_refusal=0 echo_violation=0 survived=1 error=0` | 1 (EXIT=1) |

Full receipts copied to this seat directory: `orig-D10.txt`, `noseed-D10.txt`.

## Which row decides it (both arms)

Only SY3 flips. All other 46 rows identical across arms.

- with seed: `CASE SY3 ... base=refuse new=accept new_findings=-`
  `new_rc=0` — D10 mutant's `open(full,"rb").read()` follows
  `tools/extra/link -> ../notes-copy.txt` to the byte-identical
  `tools/notes-copy.txt` (SEED_NOTES), so pre/post payloads are
  identical `content:<sha of SEED_NOTES>`; no refusal; SY3 = forgery.
- without seed: `CASE SY3 ... new=refuse new_findings=RECEIPT-STATE-CHANGED-DURING-RUN`
  `new_rc=2 base_stderr=... new_stderr=refused: RECEIPT-STATE-CHANGED-DURING-RUN:
  content tools/extra/link changed during the wrapped command; no receipt written`
  — `tools/notes-copy.txt` does not exist, so the mutant's open()
  raises `OSError` → `_snapshot_entry` returns `b"symlink-unreadable"`
  post-run while pre-run returned `content:<notes.txt bytes>` (link
  initially `-> ../notes.txt`, readable). Pre/post mismatch →
  refusal with class `RECEIPT-STATE-CHANGED-DURING-RUN`, the honest class,
  so D10 = survived (no forgery, no label-only: refuse class matches honest class).

## Exact mechanism of the `open()` failure path

- D10 mutant (`census/round-69/battery/D10.py:167-171`, single edit vs
  honest `tools/souji-receipt-write.py:169` `b"symlink:" + os.readlink(full)`):
  `_snapshot_entry()` for `os.path.islink(full)` does
  `return b"content:" + open(full, "rb").read()`, `except OSError: return b"symlink-unreadable"`.
- Fixture SY3: `link` is created as `../notes.txt` (`mutate()`) and retargeted
  in-run to `../notes-copy.txt` (`inrun_argv("symlink-retarget-same")`,
  `tools/extra/link -> ../notes-copy.txt`, i.e. `<repo>/tools/notes-copy.txt`).
- With the seed, target exists with SEED_NOTES bytes == notes.txt bytes →
  hashes match → kill. Without the seed, open() fails with ENOENT →
  `symlink-unreadable` marker ≠ pre-run `content:<SEED_NOTES>` →
  payload-change refusal → no kill.

## Evidence pointers (repo files/lines)

- Seed map: `c1-counter.py:369-381` (scratch copy: `c1-counter-noseed.py:369-376`
  after removal); SY3 in-run argv: `c1-counter.py:304-309`; SY3 row
  `c1-matrix.tsv:29` (`SY3 refuse RECEIPT-STATE-CHANGED-DURING-RUN`).
- Mutant path: `census/round-69/battery/D10.py:167-171`.
- Preregistration itself calls this out: `preregistration.txt:125-127`
  ("fixed (K7, D10)") and counter comment `c1-counter.py:377-380`.

## Findings

- **[MEDIUM]** The frozen C1 kill for D10 is seed-dependent, not row-intrinsic:
  SY3 only observes the read-through if the fixture happens to seed a
  byte-identical file at the retarget path. The round-69 frozen claim
  (`preregistration.txt:46-56`, D10 listed under forgery kills) reproduces
  byte-for-byte with the frozen counter (confirmed above, rc=0), so C1
  itself is not falsified; but the D10 kill has no independent witness —
  remove the seed and the declared protection is unobserved. The counter's
  own comment acknowledges the probe (`d10repro`).
- No other discrepancy found in this lane: the rest of the battery with
  `--only D10` is unchanged between arms (identical CASE lines except SY3);
  rc flips 0→1 exactly because EXIT reflects outcome≠expected.

## Commands used (exact)

```sh
cp census/round-69/c1-counter.py /fast/scratch/hyaku/souji-r69/S69ExecD10/c1-counter-noseed.py
# (edit: removed "tools/notes-copy.txt": SEED_NOTES entry only)
python3 -B census/round-69/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e \
  --work /fast/scratch/hyaku/souji-r69/S69ExecD10/work1 \
  --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery --only D10
python3 -B /fast/scratch/hyaku/souji-r69/S69ExecD10/c1-counter-noseed.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e \
  --work /fast/scratch/hyaku/souji-r69/S69ExecD10/work2 \
  --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery --only D10
```

## Files written (seat dir + scratch)

- `.ufo/waves/round-69/w1/S69ExecD10.md` (this report; Report path)
- `.ufo/waves/round-69/w1/S69ExecD10/orig-D10.txt`, `noseed-D10.txt` (full receipts)
- scratch: `/fast/scratch/hyaku/souji-r69/S69ExecD10/c1-counter-noseed.py`,
  `orig-D10.txt`, `noseed-D10.txt`, `work1/`, `work2/`

Report: `.ufo/waves/round-69/w1/S69ExecD10.md`
