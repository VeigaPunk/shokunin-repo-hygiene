# R91ExecC1Battery — C1 both-arm re-derivation (in progress)

Seat: R91ExecC1Battery. Lane: souji-shokunin. Read-only on lane; writes only this file and
.ufo/waves/round-91/w1/R91ExecC1Battery/; scratch at /fast/scratch/hyaku/souji-r91/R91ExecC1Battery/ (deleted before yield).

## Pin table (independent sha256sum vs prereg)

| instrument | path | prereg sha256 | measured sha256 | match |
|---|---|---|---|---|
| population r91 | census/round-91/c1-false-rows.tsv | fdc3d23839527fc1b67ef78945d0e537811ba28a8a2156fb9c598946a02bc460 | fdc3d23839527fc1b67ef78945d0e537811ba28a8a2156fb9c598946a02bc460 | YES |
| population r90 (control) | census/round-90/c1-false-rows.tsv | d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45 | d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45 | YES |
| counter | census/round-87/c1-pointer-counter.py | fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b | fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b | YES |
| harness | census/round-91/c1-false-row-harness.py | 5c6a1cf9825689a964a7ff104be2a7124095b03eba7727ec7c3ebe7026f601fc | 5c6a1cf9825689a964a7ff104be2a7124095b03eba7727ec7c3ebe7026f601fc | YES |
| battery | census/round-91/c1-clause-battery.py | 5f717a1bf162f4ca26b1a8e25dab21d52564787118547156ead5e58fde541b0e | 5f717a1bf162f4ca26b1a8e25dab21d52564787118547156ead5e58fde541b0e | YES |
| mutants | census/round-91/c1-mutants.json | 3c26051e2b18e387bb267ec68630d34b781ed3f064b0c05c7943520c04ef6ad9 | 3c26051e2b18e387bb267ec68630d34b781ed3f064b0c05c7943520c04ef6ad9 | YES |

Counter byte-unchanged claim: fd0a8e24... also appears in .ufo/waves/round-87/w1/S87Critic/receipts/instrument-hashes.txt
and other r87 receipts, so the bytes are continuous from r87 through r91 (no r88-r91 edit).

The remaining population pins the battery prints (r83..r89) were re-measured independently; all nine equal the
battery's PINS dict.

## Composition checks (independent)

- r91 rows = 63; r90 rows = 58; r91[:58] byte-identical to the r90 58 rows in order; appended ids exactly
  `LD1c, LD3, LD4, NF6i2, NF6j`; zero duplicate ids.
- mutants: 22 members; r91[:16] ids equal the r90 16 in order and every r90 member object is byte-identical in the
  r91 file; the six new ids are exactly the claim's six; each new member's `old` occurs exactly once in the counter.

## Instrument lineage diffs (r90 -> r91), read-only

- harness r90->r91: 7 removed / 56 added lines. Removed lines are exactly: the r90 docstring header, the r90 pin
  dict line, the R12 leaf tuple line, the R12 rev tuple line, and the three `where`-validation lines
  (`where not in ("lane","fixture","ledger")`, the `(where in ("lane","ledger")) != (rlabel == "BASE")` guard, and
  the `root, rev = ...` selector) that the `ledger-resolve` row type widens. No other deletion. Matches the prereg's description
  ("the r90 harness plus the R13 fixture block and leaves, the `ledger-resolve` row type, the LD1c/LD3 append shapes
  and the r91 pin").
- battery r90->r91: removed = the r90 docstring header and the r90 PINS entry (which in r90 was
  `os.path.join(HERE, "c1-false-rows.tsv")`); added = the r91 docstring, the retargeted r90 PINS entry
  (`FLEET/souji-shokunin/census/round-90/...`), the r91 PINS entry, and the `# battery path=... sha256=...` print.
  Matches "the r91 pin, the r90 pin path fix and its own sha256 print".
- mutants: `r90["members"] == r91["members"][:16]` as objects (order and content identical); six appended.

## Kill-power probe: does deleting a new row let its mutant survive?

Filed population and filed harness are untouched. The probe builds FIVE copies of the r91 63-row population, each
with exactly ONE of the five new rows deleted (62 rows, two header lines preserved), and a COPY of the filed harness
at /fast/scratch/.../probe/harness-probe.py whose `POP_PINS` dict is extended with the five derived shas -> 62
(needed because the filed harness refuses unpinned populations). Prereq: each derived population scores the
PRISTINE counter green (`rows=62 mismatches=0 errors=0 exit=0` for all five), so a mutant that survives there is
surviving the row deletion, not a broken copy.

Reproducer: `/fast/scratch/hyaku/souji-r91/R91ExecC1Battery/probe/probe.py census/round-87/c1-pointer-counter.py
census/round-91/c1-mutants.json <harness-probe.py> <lane> <work>`; full transcript in
`R91ExecC1Battery/probe/probe.txt`.

```
mutant                     drop-LD1c    drop-LD3    drop-LD4  drop-NF6i2   drop-NF6j
ld1c-class-keyed            SURVIVES      killed      killed      killed      killed
ld1d-conflict-keyed         SURVIVES      killed      killed      killed      killed
nf6i2-last-occurrence         killed      killed      killed    SURVIVES      killed
nf6j-pathch-narrow            killed      killed      killed      killed    SURVIVES
s1-exact-width                killed      killed    SURVIVES      killed      killed
s3-equal-two                  killed    SURVIVES      killed      killed      killed
```

Binding is exact and minimal: LD1c is the only row binding ld1c/ld1d, LD3 the only row binding s3, LD4 the only row
binding s1, NF6i2 the only row binding nf6i2, NF6j the only row binding nf6j. Every off-diagonal cell stays killed,
so each of the five rows carries real, exclusive kill power and the six members' r90 survival (control) is what the
five rows overturn. Deleting all five rows is the r90 58-row population (control arm).

Direct exemplar (ticket-required): rows-drop-NF6i2.tsv ->
`PROBE dropNF6i2__nf6i2-last-occurrence exit=0 SUMMARY rows=62 mismatches=0 accepted=0 refused_true=0 errors=0`
(the mutant SURVIVES without its row), while the same mutant on the unmodified 63 rows is killed (after arm below).

## Arm A — control (`--only r90 --expect-killed 16`)

Command (lane cwd, scratch work dir, filed bytes):
```
python3 -B census/round-91/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --mutants census/round-91/c1-mutants.json --work <fresh scratch> --only r90 --expect-killed 16
```
EXIT=0. Pristine: `ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0`.
The six new members (verbatim from R91ExecC1Battery/control.txt):
```
MUTANT-PAIR ld1c-class-keyed pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR ld1d-conflict-keyed pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR nf6i2-last-occurrence pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR nf6j-pathch-narrow pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR s1-exact-width pop=r90 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR s3-equal-two pop=r90 killed=no mismatches=0 errors=0 exit=0
```
`SUMMARY mutants=22 sets=r90 pristine_r90=ok killed_r90=16 killed_total=16`

My transcript (with my `EXIT=` line stripped) is byte-identical to the committed P2 control receipt
`census/round-91/controls/c1-control-r90.txt` (`diff` empty). All 22 MUTANT-PAIR lines present.
CONTROL ARM VERDICT: MATCHES the prereg wording and numbers.

## Arm B — after (`--only r90,r91 --expect-killed 38`)

Command (lane cwd, fresh scratch work dir, filed bytes; full transcript R91ExecC1Battery/receipts/after.txt):
```
python3 -B census/round-91/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --mutants census/round-91/c1-mutants.json --work <fresh scratch> --only r90,r91 --expect-killed 38
```
EXIT=0. Pristine arms:
```
ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0
ARM pristine pop=r91 rows=63 mismatches=0 errors=0 exit=0
```
All 22 MUTANT-PAIR lines, verbatim:
```
MUTANT-PAIR m6-digest-blind pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m7-round-blind pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m8-w-only-shapes pop=r90 killed=yes mismatches=2 errors=0 exit=1 | pop=r91 killed=yes mismatches=2 errors=0 exit=1
MUTANT-PAIR m9-basename-only pop=r90 killed=yes mismatches=4 errors=0 exit=1 | pop=r91 killed=yes mismatches=4 errors=0 exit=1
MUTANT-PAIR m10-records-as-wave pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m11-class-enum pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR c7-census-in-tree pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m14-short-shape pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m12-token-on-line pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m16-nf6b-punct pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m17-duplicate-id pop=r90 killed=yes mismatches=2 errors=0 exit=1 | pop=r91 killed=yes mismatches=3 errors=0 exit=1
MUTANT-PAIR m18-whole-before pop=r90 killed=yes mismatches=2 errors=0 exit=1 | pop=r91 killed=yes mismatches=3 errors=0 exit=1
MUTANT-PAIR m18b-alnum-before pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=2 errors=0 exit=1
MUTANT-PAIR m17b-target-keyed pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m17c-no-malformed pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=2 errors=0 exit=1
MUTANT-PAIR m18d-first-only pop=r90 killed=yes mismatches=1 errors=0 exit=1 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR ld1c-class-keyed pop=r90 killed=no mismatches=0 errors=0 exit=0 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR ld1d-conflict-keyed pop=r90 killed=no mismatches=0 errors=0 exit=0 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR nf6i2-last-occurrence pop=r90 killed=no mismatches=0 errors=0 exit=0 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR nf6j-pathch-narrow pop=r90 killed=no mismatches=0 errors=0 exit=0 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR s1-exact-width pop=r90 killed=no mismatches=0 errors=0 exit=0 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR s3-equal-two pop=r90 killed=no mismatches=0 errors=0 exit=0 | pop=r91 killed=yes mismatches=1 errors=0 exit=1
```
```
SUMMARY mutants=22 sets=r90,r91 pristine_r90=ok pristine_r91=ok killed_r90=16 killed_r91=22 killed_total=38
```

Machine check of the summary literal against the prereg string: EXACT (single SUMMARY line, equality True).
killed_r91 = 22 = mutants; every kill is a ROW MISMATCH with errors=0 (no kill rides a harness error, so STATED
LIMIT (v) is not what carries this run). The six new members read killed=no on r90 and killed=yes on r91.
AFTER ARM VERDICT: MATCHES the prereg wording and numbers.

Probe-harness integrity: `diff -u census/round-91/c1-false-row-harness.py <copy>` shows exactly ONE hunk — the
`POP_PINS` dict gains the five derived 62-row shas (plus two comment lines); nothing else changes
(R91ExecC1Battery/probe/harness-probe.diff). The five `rows-drop-*.tsv` copies, `pins.json`, `probe.py` and
`harness-probe.py` are archived in R91ExecC1Battery/probe/; the scratch run dir was deleted before yield, so the
durable reproducer is: copy R91ExecC1Battery/probe/ to a scratch, run
`python3 -B probe.py <lane>/census/round-87/c1-pointer-counter.py <lane>/census/round-91/c1-mutants.json
./harness-probe.py <lane> <scratch-work>`.

Standalone sanity of the first derived copy (sortie transcript, before the matrix):
```
ROW LD1c where=ledger rev=BASE item=P01 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD3 where=ledger rev=BASE item=ZY8 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD4 where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/- got=MOVED rc=0 match=yes
ROW NF6j where=fixture rev=R13 item=L06 class=QUARANTINED expect=REFUSED/- got=REFUSED rc=1 match=yes
SUMMARY rows=62 mismatches=0 accepted=0 refused_true=0 errors=0
```

## New-row semantics spot checks (from the source, independent of the run)

- LD1c appends `P01\tFLEET\t-\t...` (identical duplicate); the frozen r77 ledger row 2 is exactly
  `P01	FLEET	-	operator scope file under the fleet root, not lane bytes` -> same class/target, so a duplicate
  check keyed on class or class-or-target conflict accepts it and prints no marker.
- LD3 appends `ZY8` alone (one column); the counter's `_ledger` stores `ledger[r[0]] = (r[1], r[2])`, so an
  `len(r) == 2` spelling reaches IndexError on a 1-column row (harness error -> kill).
- LD4 uses the unchanged r77 ledger; P04 is a 4-column MOVED row, so an `len(r) != 3` reader refuses every entry and
  reports UNRESOLVED. LD4 asserts the ITEM status only and no exit code (STATED LIMIT (iii)); the observed rc was 0
  in the harness row line, and no exit assertion is made.
- NF6i2/NF6j rows are R13 fixture rows; the R13 block writes the token whole-first-then-suffix and the six
  punctuation predecessors `. _ @ + ~ -` into corpus/lessons/round-79-collision.md and commits them.

## Survival on EVERY pre-r91 pinned population (the claim's literal first sentence)

The claim says the six "survive every population the lane has pinned before this round", not only r90. The six were
scored through the FILED harness (its POP_PINS already carries r83..r90) on all eight pre-r91 populations, plus the
pristine counter on each. Receipt: R91ExecC1Battery/probe/survival-history.txt (driver survival-history.py).

```
mutant                         r83       r84       r85       r86       r87       r88       r89       r90
ld1c-class-keyed          SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES
ld1d-conflict-keyed       SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES
nf6i2-last-occurrence     SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES
nf6j-pathch-narrow        SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES
s1-exact-width            SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES
s3-equal-two              SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES  SURVIVES
```
All 56 runs (8 populations x (pristine + 6)) read `exit=0 ... mismatches=0 ... errors=0`. Independently, every
population is a strict prefix of its successor (r83(36) < r84(44) < r85(47) < r86(49) < r87(51) < r88(53) <
r89(57) < r90(58) < r91(63)), so the five appended rows are the only difference r91 introduces.
VERDICT: the six members survive all nine populations pinned before this round's five rows; the claim's first
sentence holds on measured bytes, not only on r90.

## FALSIFIES-WORDING

One sentence of C1's STATED LIMITS is not true of the run it describes.

Exact sentence (census/round-91/preregistration.txt, STATED LIMITS (iii)):
> (iii) LD4 asserts an ITEM status and no exit code: the base run is not all-resolved (the r77 population is mostly
> false rows), so exit 1 is expected and not asserted.

Reproducer (my artifact, this wave): the LD4 row performs exactly one counter invocation — `--root <lane> --rev
e65538e73c7f1a8f7570bc24a2215da8a90043f3 --fleet-root <fleet> --population census/round-77/c2-population.tsv
--ledger census/round-77/c2-pointer-ledger.tsv` (cwd lane). Measured (`R91ExecC1Battery/receipts/ld4-base-run.txt`):
```
ITEM P04 SCORECARD.md:598 status=MOVED
SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0
RC=0
```
So the run LD4 scores IS all-resolved and exits 0, not "not all-resolved ... exit 1". The "mostly false rows"
premise holds only for the LEDGERLESS run of the same population (contrast receipt
`R91ExecC1Battery/receipts/ld4-ledgerless-contrast.txt`: `SUMMARY items=35 resolved=4 unresolved=31 ...` RC=1), which
is not the command LD4 executes. The filed pre-freeze smoke `census/round-91/controls/c1-harness-smoke-r91.txt`
already prints the same contradicting cell: `ROW LD4 where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/-
got=MOVED rc=0 match=yes`, and controls/NOTES.txt records `LD4=MOVED/0`.

Impact: NONE on the predicate, the kill rule or any SUMMARY number — LD4's row asserts the ITEM status only and no
exit code, and the after/control arms are exact. It is a rationale/wording defect inside STATED LIMITS, so it is
recorded here for a narrowing amendment rather than repaired by this seat.

## Verdict

| arm | required | measured | verdict |
|---|---|---|---|
| after (`--only r90,r91 --expect-killed 38`) | `SUMMARY mutants=22 sets=r90,r91 pristine_r90=ok pristine_r91=ok killed_r90=16 killed_r91=22 killed_total=38`, EXIT 0 | identical single SUMMARY line, `EXIT=0` | MATCH |
| control (`--only r90 --expect-killed 16`) | `SUMMARY mutants=22 sets=r90 pristine_r90=ok killed_r90=16 killed_total=16`, EXIT 0, six new `killed=no` | identical line, `EXIT=0`, six `killed=no`; transcript byte-identical to committed P2 receipt | MATCH |
| pins | counter/harness/battery/mutants/r90/r91 as prereg | all six independent sha256 equal; remaining five population pins equal the battery PINS dict | MATCH, no HIGH mismatch |
| kill rule can fail | deleting a binding row lets the mutant survive | five derived 62-row copies; exact minimal binding; NF6i2 exemplar SURVIVES | MATCH |
| six survive every pre-r91 population | survive r83..r90 | 6 x 8 SURVIVES, pristine green on each | MATCH |
| C1 STATED LIMIT (iii) LD4 rationale | "the base run is not all-resolved ... exit 1 is expected" | all-resolved (35/35), RC=0 | FALSIFIES-WORDING (no predicate/number impact) |

C1 both arms RE-DERIVED on committed bytes, independently of the L1. No pin mismatch to the prereg. One STATED-LIMIT
sentence (LD4 rationale) is falsified by my artifact; the predicate, kill rule and every required number are exact.

## Tooling, host and cleanup

- No tool install or upgrade was made; no pacman/uv/npx invocation; host sysctls untouched. git/jj state not mutated
  (all fixture work happened in `git clone --shared` copies under scratch, toplevel asserted by the filed harness;
  the probe used the same harness code path).
- Scratch `/fast/scratch/hyaku/souji-r91/R91ExecC1Battery` held every transient (`--work` dirs, derived populations,
  probe harness copy); its receipts were copied into `R91ExecC1Battery/receipts/` and `R91ExecC1Battery/probe/` and
  the scratch tree was deleted before yield. `/tmp` was not used.
- Writes were confined to this report and `.ufo/waves/round-91/w1/R91ExecC1Battery/`. The lane's filed instruments,
  populations, fixtures, mutants, MANIFEST.json, `.ufo/state/*`, `.scratch/*` and `.ufo/watchdog.log` were read-only.

## Risks / stated limits of this seat

- Harness runs are slow (git fixture rebuild per row set); both arms were run once, exactly as the predicate states,
  with no retry: the receipts are the first runs.
- The probe harness copy differs from the filed harness only by the five extra POP_PINS entries
  (`R91ExecC1Battery/probe/harness-probe.diff`, one hunk), so `--population` accepts the derived 62-row copies.
- The LD4 wording finding does not invalidate the battery: LD4's row asserts the item status only; the after arm's
  kill of `s1-exact-width` is carried by that item status (probe: deleting LD4 lets s1 survive, 1 mismatch removed).
