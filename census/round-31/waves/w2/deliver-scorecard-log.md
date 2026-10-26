# deliver-scorecard-log — `### Round 31 measurements`, `### Round 31 capability rows`, `### Planned (appended at round 31)`, LOG.md entry

Seat SwarmScribe33, round 31 wave 2 (scribe; leaf, no dispatch). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`,
branch `master`, base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, preregistration
`1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, lane tip read `2c16d018e40db7c23420a2c3bb546b52957bcc25`.
Frozen contract and amendments A0-A5 read first.

Every number below was produced by this seat this run from committed bytes (private `--no-local` clones, origin
removed, under `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe33/`); the seat report
`.ufo/waves/round-31/w2/SwarmScribe33.md` `## Evidence` carries the commands and raw SUMMARY lines. Record file
contents of `census/round-31/records/` were read and their SUMMARY lines are quoted below; where this seat re-ran
the counter, the observed line is the one quoted.

Insertion points:

- Block A: append to `SCORECARD.md` after the last line of the file at the tip (end of the
  `### Round 31 capability-cell supersessions` table; file is 406 lines, the C1 block ends it).
- Block B: append after Block A.
- Block C: append after Block B.
- Block D: append at the end of `LOG.md` (after the `## 2026-10-26 — Round 30 attempt 1` entry and its
  `Owned axis scores unchanged …` line).

---

## Block A — `### Round 31 measurements`

```markdown
### Round 31 measurements (2026-10-26; base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc; preregistration 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525; amendments ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc, 26153a421374db2497e451230f33b2af78b3d128, 6fdd69673e3aec5ef64ce4f9f25f452c4f4447d3, 2c16d018e40db7c23420a2c3bb546b52957bcc25)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 capability-cell literal binding | calibration 7 | `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` (22 UNBOUND + 12 RUN-MISMATCH) | at the landing commit and again at the tip `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` under v1 and under A2+A4 alike: **missed** the frozen target `unbound=0 mismatches=0` by one item — L29 (`remote-source-after.json18/18`, `SCORECARD.md:170`) states its count only as scalar fields, so no honest binding exists and the row was left out (40 of 41 items carry a row) | `python3 -B tools/souji-capability-cells.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; v1 = the blob at 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525, same args | `census/round-31/records/c1-before.txt`, `census/round-31/records/c1-after-v1.txt`, `census/round-31/records/c1-after-a4.txt`; landing 24f343c8ffc820c0f89b4252cbdc94ab9a673aab |
| C2 landing-gate reading precision | operability 8 | `SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same` (the v3 counter's base control adds `shift=fail`) | at the landing commit and again at the tip `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same` under v1 and v2, `shift=ok` under v2 and two v3 runs with fresh random probes: **met** (fixture G1-G10 `cases=10 pass=10 control=FALSE-GREEN-REJECTED`; base tool `cases=10 pass=3`, failing G1 G3 G4 G5 G6 G7 G8) | `python3 -B census/round-31/c2-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --fleet-root /home/vgpnk/Projects/shokunin`; `census/round-31/c2-counter-v2.py` (A3 SHIFT) and `census/round-31/c2-counter-v3.py` (A5 random SHIFT), same args | `census/round-31/records/c2-after-v1.txt`, `census/round-31/records/c2-after-v2.txt`, `census/round-31/records/c2-after-v3.txt`; landing 8024b540b04d677d47cf51a0d1132ec8705ef14a |
| C3 F1 dropped-keep-ref object lifetime entry | coverage 8 | v1 `SUMMARY legs=11 fail=10 f1_entries=3`; v2 `SUMMARY legs=12 fail=11 f1_entries=3` | at the landing commit and again at the tip v1 `legs=11 fail=0 f1_entries=4`, v2 `legs=12 fail=0 f1_entries=4`, v3 `legs=13 fail=0 f1_entries=4` (L13's two remover-subtraction mutants differ from the record with strictly fewer `object_present=no` lines): **met** under v1, A0 and A1 | `python3 -B census/round-31/c3-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; `census/round-31/c3-counter-v2.py` (A0 L12) and `census/round-31/c3-counter-v3.py` (A1 L13), same args | `census/round-31/records/c3-after-c3-counter.txt`, `census/round-31/records/c3-after-c3-counter-v2.txt`, `census/round-31/records/c3-after-c3-counter-v3.txt`; landing 1baf4da02b71b012ee2426ea7c309496c0c3aca0 |

Owned scores unchanged (calibration 7, coverage 8, operability 8): C1 misses its frozen target by one item, so no calibration evidence accrued, and no reproducible 0-10 mapping exists. C2 and C3 hold at their landing commits and at the tip; C1's failure is the round's only unmet target. No round admission is claimed; the non-author closure rules. The final-tip re-measurement of all three claims is to be committed as `census/round-31/records/final-tip-measure.txt` when this table lands (this seat's tip readings: C1 `unbound=1 mismatches=1`, C2 v1/v2/v3 as above at `2c16d018e40d`, C3 v1/v2/v3 as above at `2c16d018e40d`).
```

---

## Block B — `### Round 31 capability rows (appended)`

```markdown
### Round 31 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| capability-cell binding audit (r31) | reads the SCORECARD capability cells themselves (not an append-only correction block) and binds each of the 41 enumerated count literals to a run whose command it re-executes from the base blob in a private clone, or to an unchanged record of the row's own round outside `waves/`, `transcripts/`, `sources/` and code suffixes; 40 of 41 cells now carry such a row and the one refusal is reported, not hidden | `python3 -B tools/souji-capability-cells.py --root <lane> --rev 24f343c8ffc820c0f89b4252cbdc94ab9a673aab --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` -> `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` (`census/round-31/records/c1-after-a4.txt`; base `census/round-31/records/c1-before.txt` `unbound=22 mismatches=34`); `census/round-31/c1-cells.tsv` (41 items) | r31 (claim missed: L29 unbound) |
| landing-gate reading precision (r31) | the landing gate reads the committed record as written: it unions `.ufo/waves/round-N/` with `census/round-N/waves/`, reads every `## Seat-reported failures` section including append-only carries (fenced headings are text), and keeps ellipsis placeholders, en-dash and hyphen line ranges, `:text` suffixes, `.captured` capture names, printf templates and prose slash alternations out of the dangling set while a real missing path is still flagged | `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` -> `cases=10 pass=10 control=FALSE-GREEN-REJECTED`; the same fixture against the base tool prints `cases=10 pass=3` (`census/round-31/records/c2-after-v1.txt`, its `REDARM` line: G1 G3 G4 G5 G6 G7 G8 FAIL, G2 G9 G10 PASS); reading at the landing commit `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same` (`census/round-31/records/c2-after-v1.txt`), `shift=ok` in `census/round-31/records/c2-after-v2.txt` and `census/round-31/records/c2-after-v3.txt` | r31 |
| jj dropped-keep-ref object-clock fixture (r31) | a real jj 0.45.1 + git 2.56.0 fixture measuring what keeps an abandoned commit's object present after its own keep ref is gone (a descendant's keep ref, a HEAD reflog entry) and what removes it; the record's 17 `RESULT` lines replay identically, a PATH shim logs 26 jj and 111 git calls including `abandon`, `util gc`, `reflog expire`, `gc` and `cat-file -e`, and neutering either remover changes the outcome | `TMPDIR=<scratch> bash tests/fixtures/r31-jj-object-clock.sh` -> `jj-version: jj 0.45.1-…`, `git-version: git version 2.56.0`, 17 `RESULT arm=… step=… object_present=yes|no` lines byte-identical to `census/round-31/records/jj-object-clock-run.txt`; counter readings v1 `legs=11 fail=10` -> `legs=11 fail=0` (`census/round-31/records/c3-after-c3-counter.txt`), v2 `fail=11` -> `legs=12 fail=0` (`c3-after-c3-counter-v2.txt`), v3 `legs=13 fail=0` (`c3-after-c3-counter-v3.txt`) | r31 |
```

---

## Block C — `### Planned (appended at round 31)`

```markdown
### Planned (appended at round 31)

- **r32 (planned r31):** calibration: L29's count stays unbound because its record states scalars only (`SCORECARD.md:170`), and the 41-item enumeration is notation-selected — at least two dozen count statements in the same cells stay outside it (`SCORECARD.md:147` `(246 rows)`, `:151` `baseline 33 rows, mined=16 queued=15`, `:161` `tools: 13 fail`, `:168` `(base12)`, `:170` `3/3 each18/18`), while the record rule stays file-granular and cannot tell a supporting sentence from a contradicting one; operability: the gate's tokenizer cannot tell an extension-less prose alternation from a really dangling one (a scratch commit citing `corpus/knowledge/absentdir` and `census/waves` reports neither, while a control `.md` path is reported), its LANE reading counts dangling pointers only and leaves the 54 uncarried seat-failure lines of rounds 15 (1), 19 (3), 23 (10), 24 (17) and 25 (23) to the fixture, and its parse snapshot and selftest still write under `/var/tmp` ignoring `TMPDIR` (`tools/souji-landing-gate.py:1182` and `:1499`, disclosed by wave 1); the dangling pair `census/round-3/garbage-census.out` and `tools/__pycache__/` stays accepted at the tip by the frozen `real=2`. Certification OFF, K5 HELD.
```

---

## Block D — LOG.md entry

```markdown
## 2026-10-26 — Round 31 attempt 1: capability-cell binding, landing-gate reading precision, F1 dropped-keep-ref object lifetime

Preregistration 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 and controls ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc (base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc) before any seat data; start census rc 0 with 36 W04 duplicate-url warnings (`census/round-31/records/census-start.txt`). Wave-1 attacks led to stricter-only amendments A1-A3 at 26153a421374db2497e451230f33b2af78b3d128 (C3 remover subtraction, C1 count shape, C2 SHIFT) and A4 at 6fdd69673e3aec5ef64ce4f9f25f452c4f4447d3 (C1 record/run binding rules); A5 at 2c16d018e40db7c23420a2c3bb546b52957bcc25 (C2 SHIFT probes drawn at random per run) landed after C2, and C2 was re-measured under it; A0 (C3 v2 reality leg) was landed by the L1 before wave 1 dispatched (`census/round-31/records/amendments.txt`).
- C1 calibration (24f343c8ffc820c0f89b4252cbdc94ab9a673aab): capability-cell literals `items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` -> `bound_run=20 bound_record=20 unbound=1 mismatches=1` under v1 and A2+A4 alike; 40 append-only binding rows. Missed by the frozen kill rule: L29 states its count only as scalar fields, so no honest binding exists and the claim is one item short of `unbound=0 mismatches=0`.
- C2 operability (8024b540b04d677d47cf51a0d1132ec8705ef14a): landing gate `fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same` -> `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same`, `shift=ok` under v2 and two v3 runs with fresh random probes; fixture G1-G10 `cases=10 pass=10 control=FALSE-GREEN-REJECTED` (base tool `cases=10 pass=3`); the 29 capture-only round-26 reports are now read (466 -> 495). Met.
- C3 coverage (1baf4da02b71b012ee2426ea7c309496c0c3aca0): `corpus/knowledge/jj-dropped-keep-object-lifetime.md` (`ground: F1`), row S222 new (`corpus/SOURCES.md` 145 -> 146), fixture `tests/fixtures/r31-jj-object-clock.sh`, record `census/round-31/records/jj-object-clock-run.txt` (17 `RESULT` lines, jj 0.45.1, git 2.56.0); v1 `legs=11 fail=10 f1_entries=3` -> `legs=11 fail=0 f1_entries=4`, v2 `legs=12 fail=11` -> `legs=12 fail=0`, v3 `legs=13 fail=0` (both remover mutants differ from the record with fewer `object_present=no` lines). Met.
- Mined mistake M1: append-only `## Seat-reported failures` sections in `corpus/lessons/round-2{6,7,8}.md` (26 + 29 + 19 entries, each ending `open` or `resolved@<full40>`); the base gate read 18 / 29 / 19 LG-SEAT-UNCARRIED there plus 2 dangling in round 28 (`census/round-31/records/m1-red-before.txt`), and both the base and the tip gate now report `findings=0` for all three rounds (`census/round-31/records/m1-after.txt`).
- Routed r30 defects: SKILL keep-ref bullet fixed with C3's docs; the A1 regress regex defect receipted, not claimed (`census/round-31/records/a1-regex-receipt.txt`); discovery precedence and multi-section carries closed by C2; the per-landing-commit gate run remains a process item.
- Frontier: `corpus/SOURCES.md` 145 -> 146 rows, S222 opened this round with its snapshot and fetch receipt (`census/round-31/sources/`); census rc 0 at the start (`census/round-31/records/census-start.txt`), the end census committed with this entry; F1 map row in `corpus/README.md` `## Round 31` and the boundary note in `PROVINCE.md` (`## Round 31 boundary note (F1 object lifetime)`).
- QUALITY Q67-Q69, SKILL gate-registry rows for the r31 instruments, and the round lesson are drafted in the wave-2 deliveries and land at integration (`corpus/lessons/round-31.md`). Waves: w1 38 seats, 38 result payloads (`census/round-31/waves/w1-results.json`); w2 36 seats dispatched (`census/round-31/waves/w2-spec.json`), its report capture and seat count committed with this entry.
Owned axis scores unchanged (calibration 7, coverage 8, operability 8). C1 misses its frozen target by one item, so no calibration evidence accrued and no round admission is claimed. No tools installed; pacman stayed paused. Certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged. Residuals routed to r32: L29, the notation-selected enumeration, the letters-only tokenizer blind spot, the 54 uncarried seat-failure lines of rounds 15/19/23/24/25 and the gate's `/var/tmp` parse snapshot.
```

---

## Notes for the L1 (integration)

1. Block A's "measured commit" column names each claim's own landing commit; the tip readings quoted in the after
   cells were re-run by this seat at `2c16d018e40db7c23420a2c3bb546b52957bcc25`, not copied from the landing
   records. `git diff --stat 8024b540b04d677d47cf51a0d1132ec8705ef14a..2c16d018e40d -- tools/souji-landing-gate.py tests/fixtures/r31-landing-gate-precision.py`
   and the same diff for the C3 entry/fixture/record are empty, so no claim byte moved after its landing.
2. `census/round-31/records/c3-after-v3.txt` and `c2-after-v3.txt` exist and are cited; the C3 v3 record's name
   carries the counter, not a round-31 claim id — keep the names as committed.
3. Block C deliberately does not promote any residual to a target (preregistration closing rule). The counts in it
   (1/3/10/17/23, 54 total) were measured at the tip with `--fleet-root`; without `--fleet-root` the gate also
   reports three fleet-resolvable `../.ufo/waves/hyaku/jj-w1/` paths in every round, which disappear under it.
4. No `| Lnn | SCORECARD.md:` binding row appears in this file or in the blocks above; the C1 counter reads only
   `SCORECARD.md`, so pasting these blocks cannot add or move an item.
