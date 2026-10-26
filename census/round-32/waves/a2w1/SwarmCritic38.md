# SwarmCritic38 — adjudication of attempt-1 wave-1 reports (r32 a2w1)

## Status

STATUS: PASS — all 20 assigned wave-1 reports (Critic33-37, Reviewer32, MutationTester38-39, Connector41-42,
Revenger29, Sentinel43, Simplifier44, Scribe22-28) adjudicated: 157 findings and attacks classified into
`resolved@<full40>` / `amended:A0|A1` / `disclosed:<path>:<line>` / `open` in
`.ufo/waves/round-32/a2w1/deliver-w1-adjudication-b.md`. The three claims were re-derived at the tip instead of
trusting the salvage records: C1 misses under v1 and v2, C2 misses (T18), C3 meets its target under v1 and v2.
Five open defects are filed with reproduced states. No lane byte, index, jj state or fleet path was written; scratch
`/fast/scratch/hyaku/souji-r32/SwarmCritic38` removed.

## Evidence

Frozen contract read first: `census/round-32/records/preregistration.txt` (3ec84fc81b3243429c834a051880b0bcde06291c);
then `records/amendments.txt` (A0 line 3, A1 line 13, the C1/C2 miss block lines 24-31), `records/controls.tsv`,
`c3-contract.txt`, the three counters, `c3-counter-v2.py`, `tools/souji-record-contract.py`. Landing set:
`git -C … log --format='%h %s' 85b61a1..master` → `4e56c48` (salvage), `9e8982b` (C1), `a92e1aa` (C3 + A1 + routed
defect 2), `98e5203` (C2), `7a6667c` (A0/controls), `3ec84fc` (prereg).

Re-derived at tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`, `python3 -B`, `TMPDIR` under my scratch,
`--base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`:

```
c1-counter.py       SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6
c1-counter-v2.py    SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6
c2-counter.py --only T18
                    ITEM T18 FAIL base=rc0:W4236:…baseline_mismatches=26 sbox=rc0:W4229:…baseline_mismatches=32 regress
c3-counter.py       SUMMARY legs=14 fail=0 f1_entries=5
c3-counter-v2.py    SUMMARY legs=17 fail=0 f1_entries=5
```

Instrument freeze check — `git log 85b61a1..master -- census/round-32/c1-counter.py census/round-32/c2-counter.py
census/round-32/c2-items.tsv census/round-32/c3-contract.txt tools/souji-record-contract.py
tools/souji-vault-verify.sh tools/souji-axis-check.py tools/souji-registry-agreement.py` prints nothing, so every
finding that depends on those files is open by construction.

Landed C1 rows: `git show 9e8982b:SCORECARD.md` → 38 appended rows (21 bound, 17 withdrawn; N28-N31, N33, N34 absent).
Landed C3: `census/round-32/sources/SHA256SUMS` + `records/fetch-receipts.tsv` (4 rows, http 200, live sha256);
entry Gate 23 quotes, 8 record spans, three source lines (S223, S063, S002).
Registry: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file corpus/SOURCES.md --today
2026-10-26` → `file ok`, rc 0, 36 W04, no E line.

## Findings

1. **C1 missed and the miss is not a flake** — `SCORECARD.md` appended block lines 434-471; readings above at
   `4e56c48b8fc828f9aba2746e324dc46aa538bdbf` under both `census/round-32/c1-counter.py` and `c1-counter-v2.py`.
   Six items (N28, N29, N30, N31, N33, N34, all `SCORECARD.md:422`) stay unbound and 17 withdrawals exceed the cap 8;
   the six unbound are exactly the residue SwarmCritic33 F10 and SwarmRevenger29 F3 predicted for that line.
2. **C2's T18 is defeated by C2's own repairs, not only by C3's entry** — `tests/fixtures/r20-input-binding.py:1136-1160`
   (`compare_baseline`) diffs a 66-file closure against `12516f7d…`. In a scratch clone, the fixture reports
   `BASELINE_SUMMARY … files=66 mismatches=26` at base and `mismatches=32` at the tip; the six added paths are the C3
   entry plus five files `98e5203` patched (`tools/souji-census.sh`, `tools/souji-cert-evidence.py`,
   `tools/souji-evidence-cache.py`, `tools/souji-repo-structure.sh`, `tools/souji-round9-selftest.sh`). No landing that
   performs those repairs can pass T18, so SwarmCritic37 A1's "remove or replace T18" is the only route and a C3-only
   remedy restores nothing. `amendments.txt:26-29` already names "C2's own repairs", so the disclosure is complete.
3. **C3 meets its target at the tip under both instruments** — readings above; `L2`, `L3`, `L11` pass after C2 landed,
   so SwarmCritic37 A3's coupling produced no movement. A1's three legs are present and load-bearing:
   `c3-counter-v2.py:333` (L15), `:335-339` (L16), `:341` (L17).
4. **The landed C2 fix honours TMPDIR only when it is set** — six of the 26 patched files keep a literal-root fallback:
   `tests/fixtures/r27-pre-report-gate.sh:7` (`mktemp -d "${TMPDIR:-/tmp}/…"`, moved from `/var/tmp` to `/tmp` by the
   patch), `tools/souji-round9-selftest.sh:7,14`, `tests/fixtures/r13-repo-structure.sh:189,232`,
   `tools/souji-repo-structure.sh:266`, `tests/fixtures/r28-wave-evidence-capture.sh:51`, `tools/souji-census.sh:309`.
   The C2 predicate always sets TMPDIR (`census/round-32/c2-counter.py:154-176`), so `fail` never sees the fallback;
   the r32 fixture itself does refuse an unset or empty TMPDIR (`tests/fixtures/r32-jj-mtime-clock.sh:62-63`), so the
   round now contains two idioms. This is SwarmSimplifier44 D3 realized in landed bytes.
5. **The M1 guard is still narrower than its own contract** — `census/round-32/c3-contract.txt:3` says "Every line of
   the record that starts with `prefix` must carry exactly these keys", while `tools/souji-record-contract.py:44` and
   `census/round-32/c3-counter-v2.py:93` both require a following space, so a `RESULT<TAB>arm=reflog-only …` line is in
   scope and invisible (SwarmCritic36 F1, still open).
6. **The new entry's S002 attribution is landed unfixed** — `corpus/knowledge/jj-abandoned-object-mtime-clock.md:3` and
   Gate lines 218-222 label `gc.cruftPacks` and `gc.pruneExpire` quotes S002, whose scope cell
   (`corpus/SOURCES.md:23`) names `gc.reflogExpire`, `gc.reflogExpireUnreachable`, the two `gc.rerere*` keys and
   `gc.worktreePruneExpire` only. S063 gained the CONFIGURATION anchor (`corpus/SOURCES.md:84`) but the quotes were not
   relabelled, and no leg compares a Gate bullet's section to its row's scope cell, so L4, L5, L6 and L11 all pass.
   The r31 routed traceability defect is closed for S051 and reproduced here.
7. **Four of the seven committed control rows cannot be replayed** — `git cat-file -t` prints MISSING for
   `b0a0c718…` (`controls.tsv:4`), `d4930a15…` (:5), `bf984f0c…` (:6), `791c0725…` (:7); only the three do-nothing rows
   resolve. Two seats reported the C1/C2 instances; the C3-junk revision is the same class and was not reported.
8. **One hygiene residue** — `census/round-32/__pycache__/c1-counter-v2.cpython-314.pyc` (31585 B, 05:31) is still in
   the lane working tree, i.e. a counter ran without `-B`; gitignored, so the tree is clean.

## Attack log

A1 — **A pinned-baseline anchor inside the set it certifies is self-defeating.** State: `c2-items.tsv:29` (T18) with
`--only T18` at `4e56c48…` (`mismatches 26 → 32`) and the fixture's own per-path output at base vs tip (32 paths,
6 added, 5 of them from `98e5203`). Impacted axes: operability (C2's target), coverage (C3 blamed for a defect half of
which is C2's). Smallest safe correction, stricter-only: drop T18 from the item set or re-anchor it on a count that
excludes the claim's own files; the L1 owns it and `amendments.txt:26-29` already discloses the mechanism.

A2 — **"TMPDIR honoured" passes the predicate while a literal fallback survives.** State: `r27-pre-report-gate.sh:7`
(after `98e5203`) writes `${TMPDIR:-/tmp}`; the C2 sandbox always sets TMPDIR, so the item scores PASS and an unset-TMPDIR
run still writes `/tmp`. Impacted axis: operability (the sentence the receipt will claim, not the number).
Smallest safe correction: none needed to the target; the L1 states in the lesson and receipt that the property is
"honours TMPDIR when set", or a stricter pass replaces the fallback with `${TMPDIR:?}` in those six files.

A3 — **Committed control rows are not artifacts of the repo.** State: four revs MISSING (`cat-file -t` above).
Impacted axis: calibration (controls are gameability evidence, not the claim, so no target moves). Smallest safe
correction: the receipt records that those four states were scratch-only, or the states are committed.

A4 — **The contract's in-scope sentence and both parsers disagree.** State: `c3-contract.txt:3` vs
`tools/souji-record-contract.py:44` and `c3-counter-v2.py:93`; a tab-separated RESULT line carrying `arm=reflog-only`
passes `lines=22 bad=0` and moves no leg (SwarmCritic36's reproduced state, re-read at the tip). Impacted axis: coverage
(the D1 guard). Smallest safe correction: `line.split(None, 1)[0] == prefix` in both places; a bare prefix line then
matches zero keys and is BAD.

Negative results: C1's two counters agree exactly at the tip, so the miss is reproducible; C3's v1 and v2 both pass with
`f1_entries=5`; `sources-census.sh validate` is clean at the tip, closing SwarmSimplifier44 D7; the six instruments in
the freeze check are byte-identical to base, so nothing in Findings 4-5 moved during the landings. I did not re-run the
full 27-item C2 set (only T18), did not re-apply SwarmCritic34's cheat patches to the unchanged C2 counter, and did not
execute T14 or T28 — their statuses above rest on the attempt-1 reports and the unchanged bytes, and are labelled so.

Tooling: nothing installed or upgraded (bwrap 0.13.1, strace 7.2, git 2.56.0, python 3.14.8 were present); no pacman
transaction.

## Deliveries

- `.ufo/waves/round-32/a2w1/deliver-w1-adjudication-b.md` — the 157-row adjudication table over the 20 assigned
  reports, the re-derived readings, and findings N1-N6 with their reproductions.
- `.ufo/waves/round-32/a2w1/SwarmCritic38.md` — this report.
