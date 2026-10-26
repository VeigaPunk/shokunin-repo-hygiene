# SwarmScout37 — w1 adjudication A (Executor01-19, Scout20-21)

## Status

STATUS: PASS — all 21 attempt-1 reports adjudicated into 71 rows (28 resolved, 7 amended, 16 disclosed, 20 open by first token); delivery written; two counters re-derived at the lane tip.

## Evidence

- Lane tip `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse master` = 4e56c48b8fc828f9aba2746e324dc46aa538bdbf; `git log --format='%H %s' 85b61a151923986e7e6b48f7084b9122561b5f3d..master` lists 4e56c48 (salvage), 9e8982b (C1 rows), a92e1aae (C3/A1), 98e5203 (C2), 7a6667c (controls/A0), 3ec84fc (prereg).
- Blob comparison: for each `deliver-*` file under `.ufo/waves/round-32/w1/`, `git hash-object` against `git rev-parse master:<path>`; differing only for `tools/souji-seat-audit.py`, `tests/fixtures/r20-audit-contract.py`, `tests/fixtures/r20-input-binding.py`; the four `census/round-13|14` entrypoints are absent from the landing. Fetch receipts, the four `sources/*` snapshots, SHA256SUMS, the C3 run record: `cmp` equal to the deliveries.
- C1 re-derivation (scratch `--scratch` under /fast/scratch/hyaku/souji-r32/SwarmScout37): `python3 -B census/round-32/c1-counter.py --root <lane> --rev 4e56c48b8fc828f9aba2746e324dc46aa538bdbf --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c` and the same with `c1-counter-v2.py`: both `SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6`, rc=1.
- `--only` false green: `python3 -B tools/souji-capability-cells.py --root <lane> --rev 24f343c8ffc820c0f89b4252cbdc94ab9a673aab --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --only X01,X02` -> `SUMMARY items=2 bound_run=0 bound_record=0 unbound=0 mismatches=0 partial=1`, rc=0.
- T12: clone of the lane at 4e56c48 in scratch (origin removed), `bwrap --dev-bind / / --ro-bind <empty> /tmp --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm ... bash tools/souji-census.sh --selftest` with TMPDIR scratch: `selftest: 69 checks, 0 failed`, rc=0, once plain and once under `strace -f -qq -e trace=mkdir,mkdirat,creat,open,openat,openat2`. The L1's records read T12 FAIL (`census/round-32/records/a2-l1-salvage-tip-measure.txt:109,145,147`) and PASS with both arms failing 6 (`c2-after-v1.txt:13`).
- Staged package check (read-only): `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:121` holds a staged S223 row (cnblogs), the lane row is `corpus/SOURCES.md:168`.
- Tooling: none installed or upgraded; `python3 -B` only.

## Findings

1. Open, tool: `tools/souji-capability-cells.py:153` `--only` with non-item ids prints `unbound=0 mismatches=0 partial=1` and exits 0 (reproduced above; Executor05 A1).
2. Open, counter: the glued-literal acceptance in `census/round-32/c1-counter.py` and `c1-counter-v2.py` (Executor04 A2: `k13` MATCH on `census/round-30/records/c1-before.txt:29`, honest `k1=13` refused). Not amended, not disclosed in `amendments.txt`; neither counter changed after 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1.
3. Open, landed text: `corpus/knowledge/jj-abandoned-object-mtime-clock.md:85-93` claim 7 quotes `Do not prune any loose objects` (git-gc.adoc:89-90) as the description of `--prune=never`; in `census/round-32/sources/git-gc.adoc:81-90` that line documents `--no-prune`. Scout20 F2 explains the observed mixed-arm outcome from source (`odb/source-files.c:490-493`), which the entry calls unexplained (entry:164-166).
4. Open, landed text gaps from Scout20 (`--prune=now` takes the `-a` branch; `gc.cruftPacks=false` on an existing cruft pack explodes with the pack mtime; rewrite and `touch` behaviour): none appear in the entry. Entry claim 5 and Consequence (c) hold only for an all-loose start.
5. Open, C2: T12 reading is unstable under the counter (records above; my two sandbox runs passed). `c2-after-v1.txt:13` shows a PASS where both arms fail 6 selftest checks, so the frozen predicate passes a red anchor. [INFERENCE] cause: the base arm runs the unpatched blob in the host `/var/tmp` next to other seats' live `souji-census-now.*` directories (Executor12 F6).
6. Open, C2: landed r20 fixtures use a bwrap re-exec (`tests/fixtures/r20-audit-contract.py:664-685`, `r20-input-binding.py:1292-1313`) that silently runs unprotected when `bwrap` is absent; the C2 contract text says honour TMPDIR. The commit subject discloses the mechanism; `amendments.txt` and SKILL.md do not.
7. Open, docs: C2 landed with no doc edit; stale cells listed in the delivery Notes 2 (SKILL.md:216, 204, 205, 203, 207, 214, SCORECARD.md:171 and others).
8. Open, auditor: `tools/souji-seat-audit.py:90,128,203-209` know no `/fast/scratch` root (Executor10 F5, Executor14 F2); landed file keeps only the three selftest hunks.
9. Open, disclosure: `amendments.txt:24-26` omits A0(a)/(b) from the C1 miss cause although 13 of the 17 withdrawals are attributed to them by the reports.
10. Open, minor: unusable TMPDIR falls back to `/tmp` (Executor08 F4, Executor13 F5, Executor09 F3 exit code); r23 fixed-leaf scratch collision (Executor15 F7); `where=pack` undisclosed in the entry (Executor18 F4); `command -v` shim pitfall (Executor18 F5) for the lesson; the lane S223 now collides with staged S223 (39th collision).
11. Policy split on `withdrawn` vs unbound between C1 seats (Executor05 vs 01/03/04/06) is outcome-neutral: C1 misses the cap of 8 either way.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/a2w1/deliver-w1-adjudication-a.md` — the 71-row table plus notes.
- this report.

Scratch `/fast/scratch/hyaku/souji-r32/SwarmScout37` removed after writing both files.
