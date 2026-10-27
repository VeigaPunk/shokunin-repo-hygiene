# Deliverable — r34 w1 skill/quality rows (seat SwarmScribe35)

Paste targets: (a) `SKILL.md` `## Gate registry` (append after the `r33-c2-counter` row, same
column count: name, kind, entry, verdict map, self-test, pinned-value path, write scope,
owner); (b) `corpus/QUALITY.md` — new `## Round 34 criteria` section (next free id is Q79:
the last row is Q78 under `## Round 33 criteria`); (c) `SKILL.md` bullet appended to
`## Error patterns (false-SAFE signatures)` (last bullet today is the r33 trailing-slash
entry).

Every command below was read from the counter sources at the lane tip; the two `--selftest`
commands were executed by this seat at 2026-10-27 (rc 0, output shown verbatim). Readings this
seat did **not** take are labelled with the committed record that carries them.

---

## (a) Two `## Gate registry` rows

| name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r34-c1-counter | gate | `python3 -B census/round-34/c1-counter.py --root LANE --rev REV --list-rev PREREG --scratch DIR [--only G01,...]` | 0 `SUMMARY items=60 agree=60 mismatches=0 restated=<n>` (exit 0 iff `mismatches=0`); 1 any ITEM line that is not `AGREE`, i.e. a MISMATCH run or a `BAD-ROW(...)`, `BAD-CAUSE(...)` or `RUN-FAILED(...)` detail on a restated item; 2 could-not-evaluate (a required argument missing, non-40-hex or unresolvable `--rev`/`--list-rev`, `--scratch` under `/tmp`, `/var/tmp` or `/dev/shm`, `census/round-34/c1-items.tsv` absent or malformed at `--list-rev`, `SCORECARD.md` or `SKILL.md` absent at either revision or not starting with its `--list-rev` bytes, unknown `--only` id). `--only` also prints `partial=1` and is diagnostic, never a pass. A restatement binds only when its seven cells after the id (where, kind, exit, run, statement, cause, reason) hold: `where` equals the item's `file:line`, exit is a number or `*`, a corrected argv names one of the item's files, the statement equals the run's collapsed last digit-bearing line (or a `RESULTS:<path>:<n>` with n at least 1), the cause is a full-40 ancestor of `--list-rev` and is executed (value drift at the cause's parent, or an argv correction whose cause wrote the row and whose original argv already failed there) | `python3 -B census/round-34/c1-counter.py --selftest` → `SELFTEST pass always-zero rejected RESULTS:0 rejected foreign argv rejected`, rc 0; this is a literal tripwire over the three frozen trust-boundary predicates (`0 > 0`, `0 >= 1`, `row-own-argv` vs `foreign-argv`), so it returns 1 only when a literal is edited; the behavioral self-test is the junk fixture `python3 -B tests/fixtures/r34-c1-junk.py --counter census/round-34/c1-counter.py --scratch DIR` → `cases=3 pass=3 control=STUB-REJECTED` — an always-zero emitter, a vacuous `RESULTS:<path>:0` row and an argv correction naming a foreign script each MISMATCH (`census/round-34/records/junk-c1.txt`) | `census/round-34/c1-items.tsv` read at PREREG and never at REV (60 items: 23 registry G01-G26 and 37 SCORECARD E01-E34); frozen target required at the C1 landing commit and at the tip; do-nothing red arm recorded in `census/round-34/records/controls.txt` — `items=60 agree=35 mismatches=25 restated=0` rc 1 at base over list `2b59192` (the full per-item record `controls-c1-do-nothing.txt` is on disk but uncommitted — commit it before a row cites that path) | read-only on `--root`; one private `git clone --no-local --no-checkout` per item under `--scratch` (origin removed, detached at the run revision, `{SCRATCH}` a fresh dir), removed after the run; one global `flock` at `--scratch/c1.lock`; never the lane worktree | souji |
| r34-c2-counter | gate | `python3 -B census/round-34/c2-counter.py --root LANE --rev REV --base 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev PREREG --scratch DIR` | 0 printed `SUMMARY legs=13 pass=13 fail=0 harm=0` (exit 0 iff `fail=0`; `harm=0` is a constant this counter prints, not a measured field — see the builder note); 1 any LEG line that is not `PASS`, including a failed guard; 2 could-not-evaluate (a required argument missing, non-40-hex `--rev`/`--base`/`--list-rev`, `--scratch` under `/tmp`, `/var/tmp` or `/dev/shm`, `census/round-34/c2-legs.tsv` absent or malformed at `--list-rev`, a legs file the frozen contract refuses — witness clauses dropped, no junk control, a witness-only or guard-only set — and any exception raised outside a leg) | `python3 -B census/round-34/c2-counter.py --selftest` → `SELFTEST pass witness-required rejected junk-only rejected`, rc 0, rc 1 when a weakened legs set is accepted; the J1 leg is the stub control `python3 -B tests/fixtures/r34-sandbox-junk.py --counter census/round-34/c2-counter.py --scratch DIR` → `cases=5 pass=5 control=STUB-REJECTED` — a stub printing the base exit code and line with no work must FAIL W1-W4 and N3 | `census/round-34/c2-legs.tsv` read at PREREG (witness W1-W4, nsbind N3, anchor N4, junk J1, guards G1-G6); NAMESPACE pin `tests/fixtures/r14-census-boundary.py` sha256 `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2` re-verified at REV (G6), r33 bytes untouched (G1); do-nothing red arm prints `COULD-NOT-EVALUATE legs absent at --list-rev` rc 2 at base but is held only in the uncommitted `census/round-34/records/controls-c2-do-nothing.txt` (`controls.txt` does not yet carry this arm — commit it or the arm before a row cites a path) | read-only on `--root`; per-leg private `git clone --no-local --no-checkout` under `--scratch`, each run inside bwrap (`--dev-bind / /`, an empty dir ro-bound over `/tmp` and `/dev/shm`, a private dir bound over `/var/tmp`, `TMPDIR=<scratch>/tmp`), strace logs and scratch removed per leg; one global `flock` at `--scratch/c2.lock`; the nsbind leg writes and removes its own real `/var/tmp` canary; never the lane worktree | souji |

Builder note for the L1 (not part of the row): a registry row is admissible only with a
reading that shows the gate able to fail. The committed C2 feasibility reads
`SUMMARY legs=13 pass=9 fail=4 harm=0` (`census/round-34/records/feasibility-final.txt`,
rev 60def78) and the J1 control record ends in `subprocess.TimeoutExpired` after 900 s
(`census/round-34/records/junk-c2-final.txt`), so the `r34-c2-counter` row must not land as a
green gate until those are closed — or it lands with that red arm stated in the pinned-value
cell, the way `r29-c2-counter` carries its `failed=152` arm.

Two more facts before landing the rows:

- `harm=0` in `census/round-34/c2-counter.py:323` is a literal in the summary print, not a
  counted field, so the frozen C2 summary's `harm=0` cannot be turned red by any leg; only a
  LEG line's detail can carry harm. The row above says so rather than implying a harm meter.
- The `--selftest` modes are not equivalent. The C2 one is behavioral (it calls the real
  `validate_legs` with a good set, a witness-dropped set and a junk-only set); the C1 one is a
  literal tripwire (`census/round-34/c1-counter.py:328-333` compares `0 > 0`, `0 >= 1` and two
  unequal words), so it cannot fail from a code change elsewhere. The r33 routed defect D4 asked
  for a self-invocation mode over isolated fixtures; the C1 row's behavioral control is therefore
  `tests/fixtures/r34-c1-junk.py` (scratch clones, three forged constructs MISMATCHed), and a
  strict reading of D4 still asks the C1 counter for a fixture-driven selftest.
- Only `census-start.txt`, `closure-sweep.txt`, `controls.txt`, `feasibility-final.txt`,
  `junk-c1.txt` and `junk-c2-final.txt` are tracked under `census/round-34/records/`
  (`git ls-files`). `controls-c1-do-nothing.txt`, `controls-c2-do-nothing.txt`,
  `feasibility.txt`, `feasibility-repaired.txt`, `junk-c2.txt` and `junk-c2-repaired.txt` are
  on disk only, so any row citing them is a dangling pointer until they are committed; the cells
  above cite the tracked `controls.txt` where it carries the reading and flag the rest.

---

## (b) `corpus/QUALITY.md` criterion row

Insert as a new section after `## Round 33 criteria`'s table (next free id: Q79).

```
## Round 34 criteria

| id | criterion | applies to | check | motivating evidence |
|---|---|---|---|---|
| Q79 | A sandboxed measurement claim carries three controls and each is shown able to fail. (a) Work witness: the run's file-creating syscalls are traced inside the same sandbox the run is judged in, at least one traced create names the sandbox scratch root or the writable bind, and the count is printed beside the leg verdict, so a stub that prints the base exit code and last digit-bearing line without doing the work FAILs; where nested tracing is impossible the fixture's own per-case assertions are the proof. (b) Stub control: a fixture feeds the counter a plausible-line stub and requires every stubbed leg to FAIL (`control=STUB-REJECTED`), and the counter's embedded `--selftest` behaviorally refuses a legs file with its witness clauses dropped and a junk-only set. (c) Load-recorded anchor: two adjacent base runs must print the measured run's line under one lock, the 1-min load is printed with every reading, and a reading at load > 48 is re-taken once and then FAILs — a flaky pass is never reported. | sandboxed counters, their legs, and census-selftest anchors | run the counter at base and candidate: every witness leg's detail carries the traced create count of the run it judges and a nonzero target-side count, `J1` prints `cases=<n> pass=<n> control=STUB-REJECTED`, the anchor detail prints `base=… base2=… rev=… load=…` with load at most 48, and `--selftest` prints `SELFTEST pass`; a create count printed for a base run that was never traced is not evidence, so the half-of-base clause must be either traced on both revisions or dropped from the claim | `corpus/lessons/round-33.md` `## Findings` 4 (sandbox-nt carries no work attestation, so a stub repair that prints the base line survives; the census-selftest anchor reads 0, 3, 6 and 7 failed across runs, so a PASS under load can be two flaky runs agreeing); `corpus/lessons/round-33-verifier-spotcheck.md` `## Routed defects` item 4 (counters registered as `gate` with no embedded selftest) |
```

---

## (c) Error-pattern bullet

Append to `SKILL.md` `## Error patterns (false-SAFE signatures)`, after the r33
trailing-slash-TMPDIR bullet:

```
- **A calibration row corrected by a command it does not state** (r34, C1; r33 lesson
  `corpus/lessons/round-33.md` `## Findings` 1): the r33 counter took any digit-bearing output
  line as a restatement's statement and any argv as an "argv correction", so an unrelated
  command — `echo 42` restating K18 — reached AGREE. Two rules close it, and both are
  machine-checked in `census/round-34/c1-counter.py`: a corrected argv must name one of the
  row's own files, matched on the file's basename (`BAD-ROW(argv correction names no row
  file)`), and a restated statement must equal the collapsed LAST digit-bearing line of that
  run, never a per-case or error line. A `RESULTS:<path>:<n>` statement keeps n >= 1. Recheck:
  `python3 -B census/round-34/c1-counter.py --selftest` prints `SELFTEST pass always-zero
  rejected RESULTS:0 rejected foreign argv rejected`, rc 0; the behavioral control
  `python3 -B tests/fixtures/r34-c1-junk.py` prints `cases=3 pass=3 control=STUB-REJECTED`,
  MISMATCHing a foreign-script argv correction, a vacuous `RESULTS:<path>:0` row and an
  always-zero emitter.
```

---

## Provenance

- Exit codes and CNE conditions: read from `census/round-34/c1-counter.py` (`selftest()`,
  `main()`) and `census/round-34/c2-counter.py` (`selftest()`, `main()`, `validate_legs`),
  lane tip 51acb5f, with the frozen contract `census/round-34/preregistration.txt`
  (freeze 2b0171e2, amendments A1-A6).
- Executed by this seat: `python3 -B census/round-34/c1-counter.py --selftest` and
  `python3 -B census/round-34/c2-counter.py --selftest` (both rc 0, output as printed above);
  1-min load at the run 28.54.
- Cited, not re-run by this seat: `census/round-34/records/junk-c1.txt`,
  `controls-c1-do-nothing.txt`, `controls-c2-do-nothing.txt`, `feasibility-final.txt`,
  `junk-c2-final.txt`.
