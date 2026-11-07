# ExecC2GateCheck — C2 gate runner draft (round 27, w1)

## Status
STATUS: PASS — C2 gate runner drafted at `.ufo/waves/round-27/w1/c2-gate.sh` (sha256 `bc5f4cf9d7f935b116867309f2f92216eadf312e9130cb85876866edbad45512`), CLI and output contract confirmed against `tools/souji-gate-check.py` read in full this run. Draft not executed (wave in flight; parent owns post-integration gate execution). No tooling installed (nothing needed; pacman guard moot).

## Evidence
- Read `tools/souji-gate-check.py` (lines 1-313). Argparse (lines 294-309): `--root` default `.`; `--round-date` and `--entries` (nargs="+") REQUIRED unless `--selftest`; `--snapshot-dir` default `census/round-22/attempt2/sources`; `--slice` → `slice_rel`, `--slice-verdicts` → `verdicts_rel`.
- Summary line, lines 194-195: `out.write("entries=%d ok=%d slice_verdicts=%d slice_total=%d fail=%d\n"` (verbatim).
- Exit rule, line 196: `return 0 if ok == len(entries) and v == t and total_f == 0 else 1` (verbatim).
- Slice rule, lines 174-177: `a missing verdict row is a failure of the V==T condition and is counted in NEITHER V nor F` (verbatim comment); `check_slice` returns `verified, len(ids), fails`.
- Verdict classes, line 48: `CLASSES = {"present", "accepted", "unverifiable", "refused"}` (verbatim).
- Id extraction, line 45: `SLICE_ID_RE = re.compile(r"S\d{3,}")` (verbatim; unanchored — any S<3+ digits> token in the slice file counts).
- Delivered draft `c2-gate.sh` (2749 bytes, executable): invokes exactly `python3 -B $LANE/tools/souji-gate-check.py --root $LANE --round-date <ISO-today> --entries corpus/knowledge/origin-record-writer-r27.md corpus/knowledge/origin-record-mechanism-set-r33.md --snapshot-dir census/round-27/sources --slice census/round-27/records/slice-verdicts.tsv --slice-verdicts census/round-27/records/slice-verdicts.tsv`; echoes checker FAIL lines verbatim, then emits `entries<TAB>ok<TAB>fail<TAB>rc` header + row from the summary line and process rc; exits with the checker rc; `SOUJI_ROUND_DATE` env override; missing tool → exit 2; writes nothing to the lane.

## Findings
1. CLI contract confirmed — the frozen argv is valid: `--entries` takes two paths, `--round-date` required, `--slice`/`--slice-verdicts` both resolve relative to `--root`. Location: `tools/souji-gate-check.py:294-309`.
2. Output contract — the checker prints one summary line `entries=N ok=N slice_verdicts=N slice_total=N fail=N` (line 194) and exits 0 only when ok==entries AND slice_verdicts==slice_total AND fail==0 (line 196). The draft parses entries/ok/fail from that line and takes rc from the process; it never fabricates values when the summary line is absent (fields stay empty, rc still tells).
3. Slice semantics for L1 — `--slice` file: ids are any `S\d{3,}` token per line (line 45), empty file allowed (T=0, V=0 → condition holds vacuously). `--slice-verdicts` TSV rows: `id<TAB>class<TAB>evidence`, class must be in {present,accepted,unverifiable,refused}; short rows/bad classes/duplicates emit `FAIL slice …` lines; a MISSING verdict row is not a fail but cannot raise V (lines 174-177). Frozen argv points both flags at the same file, so to get T>0 that file's lines must carry S-ids (e.g. the verdict rows themselves).
4. Snapshot dir — tool default is the round-22 dir (line 299); the invocation overrides to `census/round-27/sources`. L1 must place the GLib 2.84.0 tag snapshots (`gio/glocalfile.c`, `glib/gfileutils.c`) there; missing snapshots or out-of-dir paths fail check4.
5. Informational — the two entries do not exist at base, so running the draft now yields `entry-missing` twice and rc 1; expected until L1 lands them. The runner needs no change after landing (paths are its defaults).
6. Env — `SOUJI_ROUND_DATE` pins the date for reproducible runs; default is `date +%F` (2026-10-25 today).

## Attack log
None — this seat's item is a delivery, not an attack; no counter/predicate challenged.
