# SwarmScribe28 — round 32 wave 1 report (skeleton scribe)

## Status

STATUS: PASS — five L1-fill skeletons delivered; every pre-filled cell is a committed reading or hash opened this run; no measurement claimed, no target, predicate, predicate-set or counter touched, and nothing written outside the lane.

## Evidence

Lane HEAD at every read: `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` (base `85b61a151923986e7e6b48f7084b9122561b5f3d`, prereg `3ec84fc81b3243429c834a051880b0bcde06291c`).

- `read census/round-32/records/preregistration.txt` (32 lines) — targets, kill rules and the fixture contract, quoted not paraphrased.
- `git rev-parse HEAD` → `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`; `git show --stat 7a6667c` → 5 files (`c1-counter-v2.py`, `controls-a0.sh`, `records/amendments.txt`, `records/controls-a0.tsv`, `records/controls.tsv`); `git show --stat 3ec84fc` → 16 files.
- `read census/round-32/records/controls.tsv` — base rows used verbatim in the skeleton:
  - `C1-do-nothing(prereg) c1 SUMMARY items=44 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=44 mismatches=44 rev=3ec84fc…`
  - `C2-do-nothing(prereg) c2 SUMMARY items=27 pass=1 fail=26 rev=3ec84fc…`
  - `C3-do-nothing(prereg) c3 SUMMARY legs=14 fail=13 f1_entries=4 rev=3ec84fc…`
- `read census/round-32/records/controls-a0.tsv:2` — v2 do-nothing `unbound=44 mismatches=44` (same as v1).
- `read census/round-32/records/m1-red-before.txt` — `BAD 16..19 arm=reflog-only outside descendant|solo`, `lines=17 bad=4`, `exit=1`.
- `read census/round-32/c3-contract.txt` — `prefix: RESULT`, keys `arm step obj mtime where object_present`.
- `read census/round-32/measure.sh` — the L1's runner: every counter invoked with `--scratch` under `${HYAKU_SCRATCH:-/fast/scratch/hyaku}`.
- `grep -c '^N[0-9]' census/round-32/c1-items.tsv` → 43, plus one `L29` row = 44 items; `head/tail` of `c2-items.tsv` → 27 items over 22 files incl. the three disclosed removals.
- `grep -c W04 census/round-32/records/census-start.txt` → 36; `tail -3` → `souji ok …/corpus/SOURCES.md`, `exit=0`.
- `wc -l SCORECARD.md` → 428; headings: `### Round 31 measurements` 408, table header `| claim | axis | before | after | counting command | measured commit |` 410, `### Round 31 capability rows (appended)` 418, `### Planned (appended at round 31)` 426. The r32 block therefore appends at EOF (file is append-only).
- `git show 85b61a1:corpus/SOURCES.md | grep -cE '^…S[0-9]{3,}…'` → 146; same at HEAD → 146; `grep -rl '^ground: F1' corpus/knowledge/ | wc -l` → 4.
- `wc -l census/round-31/records/jj-object-clock-run.txt` → 19; `grep -c '^RESULT '` → 17.
- `wc -l LOG.md` → 1806; last entry `## 2026-10-26 — Round 31 attempt 1: …` at 1799. House style read from `/home/vgpnk/Projects/shokunin/.ufo/reports/round-31/souji.md`.
- `git status --porcelain` → one untracked file, `census/round-32/measure.sh` (the L1's runner; not mine, untouched).

## Findings

1. **C3's disclosed base is a class, its committed control a number.** `census/round-32/records/preregistration.txt:11` says base `legs=14 fail=14`-class, while `census/round-32/records/controls.tsv:4` reads `legs=14 fail=13 f1_entries=4` at the prereg commit. The `-class` wording covers the gap and the target is untouched, but the "before" cell must quote the control row, not the prose. The skeleton does.
2. **The C1 target is a conjunction the assignment sentence abbreviates.** `census/round-32/records/amendments.txt` A0 makes the target v1 AND v2 each `unbound=0 mismatches=0 withdrawn<=8`; the committed SUMMARY also carries `bound_field`, which neither target sentence names. Skeleton keeps all five fields and both instruments, so a v1-only or v2-only reading cannot be pasted as a pass.
3. **Tracked counters default their scratch outside TMPDIR, but inside the permitted root.** `census/round-32/c1-counter.py:159`, `c1-counter-v2.py:187` (both to `souji-r32/c1-counter`), `c2-counter.py:97` and `c3-counter.py:119` default `--scratch` to `${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r32/…`. They are outside C2's enumerated set (`census/round-32/c2-items.tsv` covers `tools/` and `tests/fixtures/` only) and write under the operator's scratch root, not `/tmp`, so no target is affected; recorded so wave 2 does not file it as an unannounced violation.
4. **M1's receipt mixes two line-number bases.** `tools/souji-record-contract.py:41-63` prints `BAD <i>` with `i` the record's file line and `lines=<n>` with `n` counting prefix-matching lines only; `census/round-32/records/m1-red-before.txt` reads `BAD 16..19` beside `lines=17`. Verified consistent against the record (19 lines, 17 `RESULT` lines, the four `arm=reflog-only` lines at file lines 16-19), but a wave-2 critic will likely read it as a contradiction. Reporting only; the tool and contract are the L1's to keep or clarify.
5. **Inherited state includes one untracked lane file.** `census/round-32/measure.sh` is present and untracked at HEAD `7a6667c`; it is the L1's measurement runner and its `--scratch` convention is what the skeleton's command cells assume. I did not add, modify or remove it.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-records-skeleton.md` — (1) `### Round 32 measurements` block with the r31 column layout and the three base readings pre-filled from `controls.tsv`; (2) four `### Round 32 capability rows` candidates (C1 v2, C2, C3, M1) with M1's committed `lines=17 bad=4` receipt; (3) `### Planned (appended at round 32)` r33 bullet as `<planned>` with a fill shape; (4) LOG.md entry skeleton in the r31 entry's shape; (5) the `round-32/souji.md` report skeleton in the assignment's section order, with the r31 house-style header, wave table and "Other report lines" bullets.

Scratch: none created (`/fast/scratch/hyaku/souji-r32/SwarmScribe28` does not exist; no clone, fixture run or download). Tool installs: none. Not an attack seat; no attack log. Lane writes: the two files above only.
