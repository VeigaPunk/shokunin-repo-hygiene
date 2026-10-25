# ScoutR17RecordAgreement-2 — residuals R15/R17/R19 (record-agreement counter)

Seat: `L1Souji25.ScoutR17RecordAgreement-2` (scout, read-only). This seat has the same brief as the
live peer `L1Souji25.ScoutR17RecordAgreement`. To avoid clobbering the peer, I wrote this report to a
`-2` path and used `/var/tmp/souji-r25-ScoutR17RecordAgreement-2/` as scratch, and messaged the peer.
I removed my scratch before finishing. For 1 s I wrote `old.py`/`base.py`/`fixture.py` into the peer's
unsuffixed dir and then moved them out; the peer's files there were not touched.

The lane moved during the run, from `6e4737e` to `de736c2` (prereg amendments 1–2). At both commits the
tool blob is `716731f` and the fixture blob is `2ff3cbb`. Neither amendment mentions R15, R17 or
record-agreement (grep, no matches). Versions used: git 2.56.0, Python 3.14.8. Nothing was installed.

## Status

STATUS: PARTIAL — the shadow behaviour reproduces, and the frozen 14/15 → 15/15 witness reproduces.
Two premises of the brief are false at the lane base, though:

- **(a)** The blob at `a6d2d15` is already the r24 fix. It reports `mismatches=7` on the shadow
  receipt. The contradicting old blob is `c872eec:tools/souji-record-agreement.py`.
- **(b)** The committed record does name both the shadow shape and the fix: `corpus/lessons/round-24.md`
  R24-M12. Only `corpus/lessons/round-23.md` still carries the false claim.

The brief's three case names do not reach 15/15 on the fixed tool, because "decoy" is R15, and R15
needs a K1 code change.

## Evidence

Blob identities, from `git rev-parse <rev>:tools/souji-record-agreement.py` and sha256 of the
`git show` bytes:

| rev | tool blob | sha256 | fixture blob |
|---|---|---|---|
| c872eec (r23 final), 315422b~1 | 3a90ddc | dd53c228… | 2ff3cbb |
| 315422b (r24 final), a6d2d15 (base), 6e4737e, de736c2 | 716731f | 41db9ca8… | 2ff3cbb |

`git log` on the tool shows the change landed at `315422b` ("r23 F4 stdout-section fix"), which is an
ancestor of the base (`merge-base --is-ancestor` → true).

### Code vs docstring

- **Old blob** `c872eec:tools/souji-record-agreement.py`. Line 118 says: "Only the header region before
  the `--- stdout ---` fence is a receipt's own claim;". The code at :121 is
  "matches = COUNTS_RE.findall(text)", and at :126 it is "m = matches[-1]". So the docstring and the
  code contradict each other (confirmed).
- **Base blob** `a6d2d15:tools/souji-record-agreement.py`. Lines 119–120 say: "A fenced receipt's
  measured value is its recorded stdout section, between `--- stdout ---` and `--- stderr ---`".
  Lines 124–133 slice `lines[start:end]` before `findall`. Here the docstring and the code agree.

### Direct `counts_of` probe (scratch, both blobs loaded via importlib)

The receipt has stdout `mismatches=7`, then the stderr fence, then `mismatches=0`.

```
old   shadow       -> assertions=63 resolved=63 skipped=40 mismatches=0     # brief's expectation holds for c872eec
base  shadow       -> assertions=63 resolved=56 skipped=40 mismatches=7     # a6d2d15 blob: already fixed
old   stderr-only  -> ...mismatches=0      base stderr-only -> None (receipt-malformed)
```

### Fixture matrix

The committed fixture bytes (`eda4fafa…`) were imported unmodified. Only `SCRATCH_ROOT` was overridden,
and the extra cases were appended in a wrapper. Every row ends with `control=FALSE-GREEN-REJECTED`.

The mutants are single-clause mutants of the base blob:

- `first`: `matches[0]`
- `noguard`: the `receipt-rev-object` elif is deleted
- `noend`: the section runs to EOF
- `nofence`: whole text is read (the r23 behaviour)
- `nostart`: the section starts at line 0

| case set | old dd53c228 | base 41db9ca8 | first | noguard | noend | nofence | nostart |
|---|---|---|---|---|---|---|---|
| committed 12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 |
| W (r24 W2R23F4: post-stderr-shadow, pre-fence-summary, receipt-rev-object) | **14/15** | **15/15** | 15/15 | 14/15 | 14/15 | 14/15 | 15/15 |
| B (brief: token-moved, decoy, trailing-shadow) | 13/15 | **14/15** | 14/15 | 14/15 | 13/15 | 13/15 | 14/15 |
| W2 (recommended, below) | **14/15** | **15/15** | 14/15 | 14/15 | 14/15 | 14/15 | 15/15 |
| W2 + pre-fence-only (16) | 14/16 | 16/16 | 15/16 | 15/16 | 15/16 | 14/16 | 15/16 |
| ExecR17 draft `w1/r23-record-agreement.py` (sha 857fc166…) | **14/15** (fails 15) | **15/15** | **15/15** | 14/15 | 14/15 | 14/15 | 15/15 |

The draft tool `w1/souji-record-agreement.py` (sha 04811c24…) also scores 15/15 on the draft fixture.
Its diff against the base is docstring-only (K1 paragraph at :11–12 and `counts_of` at :120–127).

Per-case results on the base blob for set B. Case 17 is "decoy", the W2K1 F2 shape: the calibration-row
tuple is `mismatches=9` and bound to another real commit, and a prose decoy line at the receipt rev
quotes the true tuple.

```
case=17 expect=rc!=0 K1 >=1 (decoy must not supply the binding) got=rc=0 mismatches=0 keys=4 -> FAIL
```

Old and base give the same result on this case.

### Lane exposure scan

I checked every committed `census/round-2[345]/records/*.tsv` at HEAD. None has more than one 4-tuple
line inside its stdout section, so the `first` survivor is latent on lane K1 receipts today.

## Findings

1. **The brief's premise (a) is false.** "OLD tool blob at a6d2d15" is the fixed blob (`716731f`, sha
   `41db9ca8`), which returns `mismatches=7`. The blob that returns `mismatches=0` is
   `c872eec:tools/souji-record-agreement.py` (`3a90ddc`, sha `dd53c228`). The red-arm receipt must name
   that blob. A red arm run on `a6d2d15` bytes scores 15/15 and witnesses nothing.
   - Prereg line: "R15/R17 record-agreement docstring correction plus three new fixture cases (14/15 ->
     15/15 red-before witness)."
2. **The R17 docstring correction already landed in r24 (`315422b`).** The r25 "docstring correction"
   for R17 is therefore a no-op on behaviour. The ExecR17 draft tool changes docstring bytes only. It
   does not add an R15 disclosure: the K1 paragraph still does not say that K1 accepts any scoped line
   and is not anchored to the calibration row.
3. **The brief's premise (b) is false for the record as a whole, and true for the r23 lesson.**
   - `corpus/lessons/round-24.md:160` (R24-M12) says: "the r23 lesson says last-wins closed shadowing;
     a post-fence counts line still shadows stdout".
   - `:338-340` says: "an extended fixture scores 14/15 on the old tool and 15/15 on the fix" and "the
     three extra fixture cases are not committed this round (routed to r25)".
   - The r23 lesson is uncorrected. `corpus/lessons/round-23.md:144-146` still says "switched counts
     parsing to last-wins so a pre-fence summary line cannot shadow the measured output. All three holes
     now have fixture cases (selftest 12/12)."
   - `git grep` finds no append-only correction for these lines; R24-M12 asked for one.
4. **SCORECARD is stale about this counter.**
   - `SCORECARD.md:21` pins "sha256 `dd53c228b8cca68cfe6dd51630c4ed3473a7c20db36a0effcf5a18259049bb0f`;
     fixture `tests/fixtures/r23-record-agreement.py` 11/11". The tool at HEAD is `41db9ca8` and the
     fixture holds 12 cases.
   - `:93` says "`tests/fixtures/r23-record-agreement.py` 9/9".
   - None of these is the current 12/12. This is a calibration item for the integrator. It is outside
     R17's frozen surface.
5. **The three cases to add.** These keep the frozen arms exactly (old 14/15 → fixed 15/15). On the
   fixed tool, each case is the sole killer of at least one of my mutants.
   - **13 `post-stderr-shadow`** (= "trailing-shadow", R17). Fenced `receipt=v1` K1 receipt: stdout
     `assertions=63 resolved=61 skipped=40 mismatches=2` (any wrong tuple), then `--- stderr ---`, a
     blank line, and the true tuple.
     - Expect: rc≠0 with K1 `value-disagree`.
     - Old: FAIL (the only red case). Kills `noend` and `nofence`.
   - **14 `stdout-two-line`** (replaces W2R23F4's `pre-fence-summary` / the draft's `decoy-line`). Header
     line `# summary <wrong>` before the fence; stdout `<wrong>` then `<true>`.
     - Expect: green (`case_repaired`).
     - Old: PASS. Kills `first`. The r23 pre-fence direction is kept, because the wrong summary is
       still in the header.
   - **15 `receipt-rev-object`** (the draft's "token-moved"). The receipt `rev=` and the SCORECARD token
     both move to `cd`×20, which names no commit.
     - Expect: rc≠0 with K1 `receipt-rev-object`.
     - Old: PASS. Kills `noguard`.
   - **Red arm:** `--tool <c872eec blob>` gives `selftest=14/15`, failing only case 13. Green arm:
     `--tool tools/souji-record-agreement.py` (`716731f`) gives `selftest=15/15`. Both were observed
     in scratch.
6. **The draft fixture's own docstring overclaims.** ExecR17's draft says "Each new case kills one
   instrument mutant the 12-case set lets through (r24 W2R23F4):". On the tool it ships against, case 14
   (`decoy-line`, a pre-fence summary with a single stdout line) kills no single-clause mutant: `first`
   and `nostart` both score 15/15. The claim held only for W2R23F4's `mut-first` of the r23 whole-text
   tool.
7. **R19 coverage, measured over the five r24 `counts_of`/guard clauses.**
   - The committed 12 cases kill 0/5.
   - Draft and set W kill 3/5.
   - W2 kills 4/5.
   - W2 plus a fourth `pre-fence-only` case kills 5/5. That case has the true tuple only in the header
     and empty stdout, and expects K1 `receipt-malformed`. Old fails it, which gives 14/16; the fixed
     tool passes 16/16.
   - R19's 28-mutant figure (`corpus/lessons/round-23.md:131`) is not re-measured here. Three cases do
     not close R19.
8. **Out-of-scope residual.** An in-band fence is not escaped. If a measured program prints a literal
   `--- stderr ---` line on stdout, both `counts_of` and `souji-receipt-run.py:300`
   (`end = lines.index("--- stderr ---", idx + 1)`) truncate the section at that line.
   - Probe: stdout `<true>`, then an in-band fence, then `<wrong>`, then the real fence. Base reads
     `mismatches=0`; old reads `mismatches=7`.
   - The runner only rewrites control characters (`CTRL_RE`, :91).
   - The two instruments agree with each other here, so this is not an R17 regression.

## Attack log

- **A1 — the "decoy" case is not a fixture extension; it needs a code change (R15).** The brief's set
  B includes "decoy" (W2K1 F2). Committed W2K1.md:65-66 says: "The prereg says “the r22 C1 after
  4-tuple”; K1 instead accepts any scoped occurrence anywhere in SCORECARD."
  - On the fixed tool the decoy case is green (`mismatches=0`), so set B scores 14/15 at the green arm.
    The frozen 15/15 is unreachable.
  - The only ways to make it pass are a K1 anchoring change, which goes beyond a "docstring correction"
    and touches the tool, or an expectation of green. An expectation of green would pin a known false
    green as correct, which harms calibration.
  - Neither is a plain fixture extension. R15 must stay a disclosed limit this round, with the K1
    docstring saying so.
- **A2 — the draft's labels launder R15.** The draft calls a pre-fence summary case `decoy-line` and a
  non-commit rev case `token-moved`. In the record, "decoy" means the K1 row-anchoring hole (R15, W2K1
  F2) and "token moved off line" means W2D3 M3c (`.ufo/waves/round-23/w2/W2D3.md:157`). A lesson line
  saying "decoy-line case added" would read as R15 covered when it is open (A1). The cases should carry
  their shape names (`post-stderr-shadow`, `stdout-two-line`, `receipt-rev-object`), and the lesson
  should say R15 is open.
- **A3 — the red arm is not discriminating if it is run on base bytes.** See Finding 1. A red receipt
  whose `tool_sha256` is `41db9ca8…` scores 15/15. The witness exists only with `dd53c228…`.
- **A4 — 14/15 → 15/15 is reachable by a fixture that tests one clause.** In set W, case 15 passes on
  old and on fixed alike. Case 14 kills nothing on the fixed tool. So the "three new cases" counter can
  be met while only case 13 carries information. W2 meets the same frozen numbers, and each of its cases
  is the sole killer of at least one fixed-tool mutant. Prefer W2; this is a choice of case content, and
  no predicate changes.
- **A5 — concurrency hazard in the counter itself.** The committed fixture and the draft both hard-code
  `SCRATCH_ROOT = "/var/tmp/souji-r23-ExecFixtureAgreement"`, and `main()` calls `cleanup()`
  (`shutil.rmtree`) before running. Two seats running the counter at the same time delete each other's
  case repos, which can produce spurious FAILs or false results. This is an operability issue. My runs
  avoided it by overriding the attribute through an import wrapper.
- **A6 — "fixed docstring + fixture" overstates what r25 changes.** The behaviour fix is r24's. If r25
  records R17 as "closed by docstring correction", that misattributes it. What r25 actually adds is the
  fixture witness for r24's fix plus the r23-lesson append-only correction (Finding 3), which is still
  owed.

Checks for the integrator to run:

- `python3 -B tests/fixtures/r23-record-agreement.py --tool <extracted c872eec blob>`: expect 14/15.
- `python3 -B tests/fixtures/r23-record-agreement.py --tool tools/souji-record-agreement.py`: expect
  15/15.
- Run the two serially, because of A5.
