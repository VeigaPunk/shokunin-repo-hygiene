# SwarmScribe35 — r34 w1, skill/quality rows

## Status

STATUS: PASS — three artifacts drafted at the named delivery path (two `## Gate registry`
rows, one QUALITY criterion Q79, one error-pattern bullet); both counters' `--selftest`
executed rc 0; eleven findings routed, including the committed C2 red arm the L1 must not
land a green row over.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`,
freeze `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`, base `9c76c7222a8abff027af42e37f0d160d52526bba`.

1. `TMPDIR=/fast/scratch/hyaku/souji-r34/SwarmScribe35/tmp python3 -B census/round-34/c1-counter.py --selftest`
   → `SELFTEST pass always-zero rejected RESULTS:0 rejected foreign argv rejected`, rc 0 (load 28.54).
2. `… python3 -B census/round-34/c2-counter.py --selftest`
   → `SELFTEST pass witness-required rejected junk-only rejected`, rc 0 (load 28.54).
3. `git -C <lane> log --oneline -6` → `51acb5f round-34: record frozen control outcomes`,
   `60def78 round-34: record C2 counter re-pin`, `2b0171e round-34: verify N3 pin and real
   var-tmp isolation`, `73f029e … repair sandbox legs …`, `2b59192 … freeze (attempt 2, A1-A4) …`,
   `9c76c72 round-33 verifier spot-check …`.
4. `git -C <lane> diff --stat 2b591924 2b0171e2 -- census/round-34 tests/fixtures` →
   `c2-counter.py | 63 +`, `preregistration.txt | 13 +`, `tests/fixtures/r34-c1-junk.py | 120 +-`
   (3 files; `c1-items.tsv` and `c1-counter.py` unchanged between the two freezes).
5. `git -C <lane> diff 2b0171e2 51acb5f -- census/round-34/preregistration.txt` → one hunk
   replacing "the repaired counter must be committed before subsequent data, and its commit
   becomes the re-pinned --list-rev" with the landed hash sentence.
6. Read at the tip: `census/round-34/c1-counter.py:230-401`, `census/round-34/c2-counter.py:1-329`,
   `census/round-34/c1-items.tsv`, `census/round-34/c2-legs.tsv`, `SKILL.md:188-262` (registry
   column shape, last row `r33-c2-counter`), `SKILL.md:99-168` (error patterns, last bullet at
   line 159), `corpus/QUALITY.md:181-188` (last row Q78), `corpus/lessons/round-33.md:49,52`,
   `corpus/lessons/round-33-verifier-spotcheck.md:147`.
7. Committed r34 records read (not re-run by this seat): `controls.txt` (tracked — carries the
   C1 do-nothing `items=60 agree=35 mismatches=25 restated=0` rc 1 at base over list `2b59192`,
   and states C2 `legs=13 pass=9 fail=4 harm=0` rc 1), `junk-c1.txt` →
   `cases=3 pass=3 control=STUB-REJECTED`, `feasibility-final.txt` →
   `SUMMARY legs=13 pass=9 fail=4 harm=0 rev=60def78d…`, `junk-c2-final.txt` → a
   `subprocess.TimeoutExpired` traceback (inner counter run, `timeout=900`).
   `git -C <lane> ls-files census/round-34/records` lists only those plus `census-start.txt`
   and `closure-sweep.txt`; `git -C <lane> status --porcelain -- census` shows
   `controls-c1-do-nothing.txt`, `controls-c2-do-nothing.txt`, `feasibility.txt`,
   `feasibility-repaired.txt`, `junk-c2.txt`, `junk-c2-repaired.txt` as untracked.

## Findings

1. **C2 target is not reached at any committed reading.** `census/round-34/records/feasibility-final.txt`
   (rev 60def78) reads `SUMMARY legs=13 pass=9 fail=4 harm=0`; failing legs W2, W3, N3, J1.
   The row drafted for `r34-c2-counter` must land with that red arm stated (or after repair).
2. **The junk control is a 900 s timeout, not a rejection.** `census/round-34/records/junk-c2-final.txt`
   is a `TimeoutExpired` traceback from `tests/fixtures/r34-sandbox-junk.py:117` running the
   counter on a stub clone; `census/round-34/records/controls.txt` states "no pass is claimed".
   J1 therefore currently FAILs by exception, and the counter's junk branch spends up to
   `--timeout` per attempt (`census/round-34/c2-counter.py:287-288`).
3. **The witness's "half of base" clause is vacuous.** `census/round-34/c2-counter.py:157` traces
   only the rev run (`if strace and check_rev == rev`), so `base_run[2]` is always 0 and line 201
   (`tip_run[2] * 2 < max(base_run[2], 1)`) degenerates to "at least one create". The printed
   detail `creates=0/209` (W1, feasibility-final) is the base count first, i.e. an untraced 0 —
   the sustained claim "at least half of base's" (`census/round-34/c2-legs.tsv:7`) is not measured.
4. **No scratch-path normalization, against the frozen legs header.** `c2-legs.tsv:7` says the
   rev run must print the base line "scratch paths normalized to <TMP>", but
   `census/round-34/c2-counter.py:82` (`last_digit`) collapses whitespace only. W3 FAILs with
   `base/rev mismatch rc=1/1` over two random `bwrap.*` temp names — an instrument defect, not a
   tool defect.
5. **N3 fails on its own summary literal.** `feasibility-final.txt` N3 detail is
   `cases=12 pinned=True summary=False`: 12 CASE lines and the pin digest hold, the required
   `SUMMARY\ttotal=12\tfailed=0` substring does not (`c2-counter.py:194`). The L1 should read the
   fixture's actual summary line before judging the leg.
6. **W2's fixture itself fails one case under bwrap.** `feasibility-final.txt` W2:
   `CASE=20 summary=SUMMARY total=20 failed=1` (base==rev comparison is bypassed only when the
   summary is clean, `c2-counter.py:303-311`).
7. **`harm=0` is a literal.** `census/round-34/c2-counter.py:323` prints
   `SUMMARY legs={len(results)} pass={passed} fail={failed} harm=0 rev={a.rev}`; the frozen
   C2 summary's `harm=0` is unconditional and no leg can turn it red.
8. **The C1 `--selftest` is a literal tripwire, not a fixture-driven test.**
   `census/round-34/c1-counter.py:328-333` compares `0 > 0`, `0 >= 1` and two unequal words, so
   it exits 1 only if those literals are edited. r33 routed defect D4
   (`corpus/lessons/round-33-verifier-spotcheck.md:147`) asked for "a self-invocation mode over
   isolated fixtures with committed expected finding-ids"; for C1 that is
   `tests/fixtures/r34-c1-junk.py` (`junk-c1.txt`), not `--selftest`. The drafted row says so.
9. **The C1 do-nothing control cites list-rev `2b591924`, not the frozen `2b0171e2`.**
   `census/round-34/records/controls-c1-do-nothing.txt` (on disk, untracked) header: list
   `2b591924f607…`. Between
   the two freezes (evidence 4) `c1-items.tsv` and `c1-counter.py` are byte-identical, so the
   60-item set and instrument are the same `[INFERENCE]`; A6 re-pins C2 readings only, so this
   is a consistency note, not a re-score requirement.
10. **25 items are the correction batch.** From `controls-c1-do-nothing.txt`: G05 G11 G17a G17b
    G21 G23 G24 E04 E05 E07 E08b E09a E14a E14b E15c E18 E23a E23b E24 E25 E26 E27 E29 E31 E32
    (7 registry, 18 SCORECARD). The frozen target needs all 60 AGREE at the C1 landing commit.
11. **Post-freeze prereg edit.** `census/round-34/preregistration.txt` changed in `51acb5f`
    (evidence 5), i.e. after the C2 data commit `60def78`. The change records the re-pin hash and
    alters no predicate/target/item; reported for the canonical judge, not asserted as a breach.
12. **Legs-file doc residue.** `census/round-34/c2-legs.tsv` junk-kind header names
    `--tool <path> --counter …`, but both fixtures take `--counter`/`--scratch` only
    (`tests/fixtures/r34-sandbox-junk.py:58-59`, `tests/fixtures/r34-c1-junk.py:68-69`).
13. **Six r34 records are untracked, and the C2 do-nothing arm has no committed receipt.**
    `git -C <lane> ls-files census/round-34/records` lists `census-start.txt`, `closure-sweep.txt`,
    `controls.txt`, `feasibility-final.txt`, `junk-c1.txt`, `junk-c2-final.txt` only.
    `controls-c1-do-nothing.txt`, `controls-c2-do-nothing.txt`, `feasibility.txt`,
    `feasibility-repaired.txt`, `junk-c2.txt`, `junk-c2-repaired.txt` are on disk. The frozen
    contract's C2 do-nothing arm (`--rev <base>` → `COULD-NOT-EVALUATE`, exit 2) appears in no
    tracked file — `controls.txt` carries the C1 do-nothing line and the C2 repaired-feasibility
    line, not the C2 do-nothing. The drafted C2 row names that arm and flags the missing commit
    rather than citing an uncommitted path.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-skill-quality.md` — (a) two `## Gate registry` rows
  `r34-c1-counter` / `r34-c2-counter` (kind `gate`, owner souji, read-only targets + isolated
  scratch, selftest + junk control, do-nothing red arms), (b) `corpus/QUALITY.md` Q79 under a new
  `## Round 34 criteria` section (witness + stub control + load-recorded anchor, each able to
  fail), (c) the corrected-argv error-pattern bullet with the basename check and last-line
  statement rule, citing r33 lesson finding 1.

Scratch `/fast/scratch/hyaku/souji-r34/SwarmScribe35/` removed after the receipts above were
copied; nothing outside this lane was written.
