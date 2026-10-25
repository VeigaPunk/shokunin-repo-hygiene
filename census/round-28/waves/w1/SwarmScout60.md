# SwarmScout60 — precedent receipts runbook for L1 (r24/r26/r27 assimilation)

## Status
STATUS: PASS — precedent receipts collected from r24/r26/r27 (gate-check invocation shapes, mirror-lane gate procedure, collision-check receipts) and summarized as a runbook below; read-only, no lane edits, no tools installed (existing git/grep/coreutils only).

## Evidence

### 1. Gate-check invocation shapes (verbatim from committed receipts)

Tool CLI (stable across r24-r27): argparse `--root` (default `.`), `--round-date` + `--entries` (nargs="+") REQUIRED unless `--selftest`; `--snapshot-dir` default `census/round-22/attempt2/sources`; `--slice`/`--slice-verdicts` resolve relative to `--root`. Summary line `entries=N ok=N slice_verdicts=N slice_total=N fail=N`; exit 0 iff ok==len(entries) AND v==t AND total_f==0 (`tools/souji-gate-check.py:194-196`); verdict classes {present,accepted,unverifiable,refused} (line 48); slice ids = unanchored `S\d{3,}` tokens (line 45). Tool blobs d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d at r24/r26.

- r24 (`census/round-24/records/gate-check-r24-entry.tsv:5,9`; `gate-final.tsv:5,9` identical, rev 778747eb → 315422ba):
  `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/count-objects-linked-worktree-garbage.md --snapshot-dir census/round-24/sources --slice census/round-24/records/quarantine-slice --slice-verdicts census/round-24/records/slice-verdicts.tsv`
  → `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0` rc=0 (slice/quarantine files distinct).
- r26 (`.ufo/waves/round-26/preregistration.txt:107` frozen K2; executed `census/round-26/records/c2-gate.tsv:5,9` @ 50443f57):
  `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts`
  → `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0` rc=0 (both slice arms = empty files; T=0, V==T vacuous).
- r27 (argv shape from `.ufo/waves/round-27/w1/c2-gate.sh:44-50`; executed result `census/round-27/records/c2-after.tsv:2` @ 6cb22dc): `python3 -B $LANE/tools/souji-gate-check.py --root $LANE --round-date <ISO> --entries corpus/knowledge/origin-record-writer-r27.md corpus/knowledge/origin-record-mechanism-set-r33.md --snapshot-dir census/round-27/sources --slice census/round-27/records/slice-verdicts.tsv --slice-verdicts census/round-27/records/slice-verdicts.tsv` → gate_entries=2 gate_ok=2 slice_verdicts=8 slice_total=8 gate_fail=0 census_rc=0 (both flags point at the SAME slice-verdicts.tsv; its 8 rows carry S-ids so T=8, V=8). Wrapper features: `SOUJI_ROUND_DATE` env override; missing tool → exit 2; writes nothing.

### 2. Mirror-lane gate procedure

- r26 frozen (`.ufo/waves/round-26/preregistration.txt:124-128`): SCRATCH MIRROR GATE before any registry append — copy corpus/ + append block + admitted entries at `.ufo/waves/round-26/assimilation/validate/`, then `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <mirror>/corpus/SOURCES.md` must exit 0 BEFORE the first real append (warnings allowed). Evidence: `.ufo/waves/round-26/assimilation/validate/mirror-validate.out` → `file ok`, W04 warnings only, no E01–E12.
- r27 executed (`.ufo/waves/round-27/w1/ExecAssimMirror.md`): mirror build `cp -a <lane>/corpus <mirror>/corpus`, `diff -r` clean, base SOURCES.md sha256 identical; ALSO copy lane `tools/souji-size-census.py` into mirror root because E11 resolves used-by relative to the registry file's parent (base rows S120/S122 reference tools/). Pre-append validate → RC=0 `file ok`, 34 W04, zero E01–E12. Append block: 11 columns, no literal/escaped `|`, status=mined, opened=2026-10-25, teaches ≤25 words, used-by exactly the admitted entries. Post-append validate → RC=0, 35 W04 (34 base + 1 new cross-scope duplicate), no E03/E04. Manual mirror greps: row count `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`; malformed `awk -F'|'` NF=13 → 0; duplicate ids `sort|uniq -d` → empty; enum/tier violations → 0; mined used-by paths all exist.

### 3. Collision-check receipts (`census/round-27/assimilation/`)

Procedure (`README.txt:5-10`, verbatim):
```
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <lane>/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > "$A/reg-ids"
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' "$S/merge/souji/SOURCES.append.md" | grep -oE 'S[0-9]+' | sort > "$A/staged-ids"
comm -12 "$A/reg-ids" "$A/staged-ids" > "$A/collisions"
```
- r27: reg-ids=132, staged-ids=134, collisions=24 (S109–S132); `renumber-map.tsv` (staged_id/decision/lane_id/canonical_name_or_reason) accounts for all 24: 14 aliases to already-held rows, 2 rejected, 8 quarantined/not adopted; adopted ids S152/S210/S211 ∉ collisions and > base max S132 → no arithmetic renumbering; post-append reg ∩ staged = 27.
- r24 (`.ufo/waves/round-24/assimilation/`): reg-ids=119, staged-ids=134, collisions=11 (S109–S119); `renumber-map.tsv` by-document: S153→S120 (git path.c v2.56.0), S153→S121 (path.c v2.30.0), S122 (builtin/count-objects.c opened this round), S123 (git-worktree; staged S230 names different URL, lane scope §REFS). One staged row may map to multiple lane rows (two tags read).
- Parser note (r27 README): extractor accepts 0–3 leading spaces; indented-row false-negative independently demonstrated in `.ufo/waves/round-27/w1/LabCensusProbe.md`.

## Findings

1. Gate-check CLI/output contract is stable r24→r27; every past invocation ran `python3 -B`, full paths relative to `--root`, always the four flags `--round-date --entries --snapshot-dir --slice --slice-verdicts`. Location: `tools/souji-gate-check.py:45,48,194-196,294-309`; receipts above.
2. Slice-arm usage diverges by round: r24 distinct quarantine-slice + slice-verdicts.tsv (T=8); r26 both flags at empty files (T=0); r27 both flags at the same slice-verdicts.tsv (T=8). r28 frozen C2 enumerates `python3 -B tools/souji-gate-check.py` without argv; the r27 shape (same-file slice/verdicts, 8 verdict rows) is the closest precedent for the F4 origin-record round.
3. Mirror gate runs before the first real append, on a byte-exact corpus copy plus the lane tools referenced by base used-by rows; `sources-census.sh validate --file` must exit 0 (W04 warnings allowed, E* not); post-append re-run must add no E03/E04. Location: r26 preregistration.txt:124-128; ExecAssimMirror.md.
4. Collision proof is a committed 3-file set (reg-ids, staged-ids, collisions) + renumber-map.tsv accounting for every collision id; adopted ids must be absent from the collision set and above base max, else renumber by document (URL is evidence, never arithmetic). Location: `census/round-27/assimilation/README.txt`, `renumber-map.tsv`; r24 counterpart under `.ufo/waves/round-24/assimilation/`.
5. Round-28 state (observed, not precedent): r28 collision receipts already exist at `census/round-28/records/assimilation/` (reg-ids=135, staged-ids=134, collisions=27); wave w1 already carries r28 drafts `slice-verdicts.tsv` (8 rows, S114/S118/S123/S124/S126/S131/S133/S138, same verdicts as r27), `quarantine-slice.tsv`, `origin-record-exclusivity-r28.md`, `origin-record-durability-r28.md`, `snapshots/`. L1 should reconcile runbook steps with these.

## Attack log
None — scout seat; no counter/predicate challenged.

## Tooling
No tools installed or upgraded (git/grep/coreutils/awk only; no pacman transaction).
