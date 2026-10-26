# SwarmMutationTester59 — C3 gate mutation battery (souji r29, w1)

## Status

STATUS: PASS — 18 mutants built from a stub F3 entry pair in an isolated scratch clone at lane base 691dd29211c53d0ef94fa072394cb9c8a69fe92e; 17 killed by the targeted instrument, 1 survivor of the C3 gate pair (R8, killed only by `sources-census.sh validate` E07 and the C1 counter K1); all baselines green before data; scratch bytes restored exactly (hash-verified); lane repo untouched.

## Evidence

Environment: scratch clone `/var/tmp/souji-r29-MutateC3Gates/c`, created with `git clone -q --no-local` from the lane, `git -C <c> rev-parse --show-toplevel` printed `/var/tmp/souji-r29-MutateC3Gates/c` before the first commit; throwaway identity configured only inside that clone. Instrument selftests before any mutation: `souji-gate-check.py --selftest` `selftest=9/9` rc 0; `sources-census.sh selftest` rc 0.

Detector argv (frozen, identical on pristine / mutated / restored bytes):

- GATE: `python3 -B tools/souji-gate-check.py --root <clone> --round-date 2026-10-25 --entries corpus/knowledge/mut-stub-a.md corpus/knowledge/mut-stub-b.md --snapshot-dir census/round-29/sources --slice census/round-29/records/quarantine-slice --slice-verdicts census/round-29/records/slice-verdicts.tsv`
- COV: `python3 -B tools/souji-coverage-agreement.py --root <clone> --rev <full40>`
- CEN: `sources-census.sh validate --file <clone>/corpus/SOURCES.md --today 2026-10-25`
- REG1 (context for R8 only): `python3 -B tools/souji-registry-agreement.py --root <clone> --rev <full40>`

Round-29 records do not exist at base 691dd29, so the slice pair was copied verbatim from `census/round-24/records/` (8 ids, 8 verdict rows — the preregistered `slice_verdicts=8 slice_total=8` shape) and the frozen K2 list copied byte-identical from b8cb4b31ce80e2e3314b88e85d40ea9873180804 `census/round-29/stale-statements.tsv` (sha256 dccc57f235ff210ab19cc306afc75c9daf57e7ac069984e8132be14de61116fa).

Pristine baselines (all green, so every kill below is conclusive):

- COV at 691dd29: `grounded=13 mapped=13 dangling=0 mismatches=0`, rc 0 — matches the preregistered before-value.
- CEN on the pristine registry: rc 0, warnings only (36 W lines, cross-scope W04; count carries this command).
- M0 fixture commit (valid stub pair: two `ground: F3` entries, two S900/S901 rows, README F3 stub row, snapshots under `census/round-29/sources/`): GATE rc 0 `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`; COV rc 0 `grounded=15 mapped=15 dangling=0 mismatches=0`; CEN rc 0; REG1 rc 1 `SUMMARY k1=6 k2=4 mismatches=10 rev=fba71b8cb2e459c06de1db8014996f43025fb9c6` — exactly the preregistered do-nothing control, i.e. the fixture adds no K1/K2 debt.

Restoration: after the battery, `git -C <clone> reset --hard <M0>`; all 9 fixture files sha256-identical to their M0 values (`hashes_match=True`, `git status --porcelain` empty); GATE rc 0, COV@M0 15/15/0/0, COV@base 13/13/0/0 re-verified on restored bytes. The lane itself was only read (`log/show/ls-tree/cat-file/rev-parse`); no install or upgrade was performed (stock python3, git, gawk 5.4.1).

## Findings

1. SURVIVOR (the assignment's false-green candidate): a registry row whose only mention of the admitted entry sits in the status column with `used-by` em-dash is ACCEPTED by both C3 gates — GATE rc 0, COV rc 0 at rev b8b31720a385. Gate-check resolves only cited ids against row ids (tools/souji-gate-check.py:117-124, `fails.append("check5-dangling-source: %s" % sid)`); coverage-agreement never opens corpus/SOURCES.md at all. It is killed by CEN (`file E07 S901 status=mined corpus/knowledge/mut-stub-b.md`, rc 1) and by the C1 counter (REG1 rc 1, k1 6→7: `K1 cited-not-in-used-by S901 corpus/knowledge/mut-stub-b.md`). Coverage gap, not a contract defect: the prereg already compensates by putting `sources-census.sh validate` in the C3 enumerate and counting C3 rows under C1 at the final tip. No predicate change proposed.
2. By-design blindness is symmetric: gate-check is blind to the README coverage map (M8–M10 GATE rc 0) and coverage-agreement is blind to Gate content (E1–E7 COV rc 0), and both are blind to registry well-formedness (R1–R7 green on both). The C3 battery closes only as the preregistered trio (gate-check + coverage-agreement + `sources-census.sh validate`); every mutant is killed by at least one member of that trio.
3. Positive kill worth recording: the README status column cannot smuggle an entry past coverage-agreement — M10 (entry named only in the map's status cell) dies with `MISMATCH MISSING-FROM-MAP corpus/knowledge/mut-stub-b.md ground=F3 map_rows_F3=2` because map names are read only from the entries cell (tools/souji-coverage-agreement.py:87, `yield lineno, row[0], (row[2] if len(row) >= 3 else "")`).
4. The C1 counter is not evaluable at lane base 691dd29 (rc 2, `COULD-NOT-EVALUATE stale list 691dd29211c53d0ef94fa072394cb9c8a69fe92e:census/round-29/stale-statements.tsv unreadable`): the tool and its frozen list land with prereg commit b8cb4b31, consistently with the prereg's "evaluable at its own landing commit". Context only; not an ATTACK. REG1 bytes I ran are byte-identical to b8cb4b31 (`git diff --stat b8cb4b31 -- tools/souji-registry-agreement.py` empty).
5. Cosmetic: a single quote defect makes gate-check emit the specific code plus `check3-no-located-quote-with-snapshot` (E1–E4 report fail=2 for one defect). Exit code unaffected. No action.

## Attack log

Stub pair: `corpus/knowledge/mut-stub-a.md` + `mut-stub-b.md` (valid at M0, GATE ok=2, COV 15/15). One behavior point per mutant; mutated-file sha256 (12 hex) at the mutant state; expected = targeted instrument rc 1.

| Mutant | rev | Mutated file (sha) | GATE | COV | CEN | Verdict |
|---|---|---|---|---|---|---|
| E1 quote absent from snapshot | 8dd9ff56e7dd | mut-stub-a.md f4aabbeac10e | rc1 `check4-quote-absent-from-snapshot-line-6` | rc0 | rc0 | killed (GATE) |
| E2 quote 26 words (in snapshot) | ae846d8fdbc4 | mut-stub-a.md 068a17656539 + snapshot 692190a96bb1 | rc1 `check3-quote-26-words-gate-line-6` | rc0 | rc0 | killed (GATE) |
| E3 no locator token | 4254c9691017 | mut-stub-a.md 6f00fd5b73de | rc1 `check3-no-locator-gate-line-6` | rc0 | rc0 | killed (GATE) |
| E4 snapshot outside --snapshot-dir | 1b895e84f209 | mut-stub-a.md 3511d7192dc7 | rc1 `check4-snapshot-outside-dir-line-6` (gate-check.py:96-97, `fails.append("check4-snapshot-outside-dir-line-%d" % lineno)`) | rc0 | rc0 | killed (GATE) |
| E5 missing ADMIT line | a4189c6c563b | mut-stub-a.md a10a9f2f213b | rc1 `check6-no-admit` | rc0 | rc0 | killed (GATE) |
| E6 missing REJECT line | 67bf4b372dfa | mut-stub-a.md 9d744bb37b14 | rc1 `check6-no-reject` | rc0 | rc0 | killed (GATE) |
| E7 `source:` id with no row | e7dabc8a9813 | mut-stub-a.md 2a6cef433b7f | rc1 `check5-dangling-source: S999` | rc0 | rc0 | killed (GATE) |
| M8 `ground: F3` entry not in README map | 707feb9133fd | README.md e40eaa01e6d2 | rc0 | rc1 `MISSING-FROM-MAP mut-stub-b` | rc0 | killed (COV) |
| M9 map entry path does not exist | a583db7de9f4 | README.md 772eac889235 | rc0 | rc1 `DANGLING-MAP-PATH mut-stub-c` | rc0 | killed (COV) |
| M10 status-column mention only (README map) | 2633f5f559f0 | README.md 9c5cc5a63e17 | rc0 | rc1 `MISSING-FROM-MAP mut-stub-b` | rc0 | killed (COV) |
| R1 duplicate id | 17c3f68c0838 | SOURCES.md 44f87082f46e | rc0 | rc0 | rc1 `E03 S900 duplicate id` + `E04 duplicate url ... within scope lane` | killed (CEN) |
| R2 12-column row | ec1ce1b9bd33 | SOURCES.md be4f26f17cc9 | rc0 | rc0 | rc1 `E01 S902 fields=12` | killed (CEN) |
| R3 10-column row | cf22a45b61ef | SOURCES.md bd459799e11e | rc0 | rc0 | rc1 `E01 S903 fields=10` | killed (CEN) |
| R4 bad tier | fb7f70feab6f | SOURCES.md a0c2883c0d91 | rc0 | rc0 | rc1 `E06 S901 tier=D` | killed (CEN) |
| R5 bad status | 56abf0043593 | SOURCES.md d20703e63ed8 | rc0 | rc0 | rc1 `E07 S901 status=watch` | killed (CEN) |
| R6 recheck prose | 6bee98e20eda | SOURCES.md dd2ece8ff93a | rc0 | rc0 | rc1 `E09 S901 recheck=2 weeks` | killed (CEN) |
| R7 used-by missing path, status mined | dcae8a5ae763 | SOURCES.md af699e2fb39a | rc0 | rc0 | rc1 `E11 S901 missing used-by corpus/knowledge/mut-stub-missing.md` | killed (CEN) |
| R8 status-column mention only (SOURCES row, used-by em-dash) | b8b31720a385 | SOURCES.md 38acf11756be | rc0 — FALSE GREEN | rc0 — FALSE GREEN | rc1 `E07 S901 status=mined corpus/knowledge/mut-stub-b.md`; REG1 rc1 k1=7 `K1 cited-not-in-used-by S901 corpus/knowledge/mut-stub-b.md` | SURVIVOR of the C3 gate pair; killed by CEN and by C1-at-tip |

Battery transcript: `/var/tmp/souji-r29-MutateC3Gates/battery.log` (scratch; removed with the scratch after this report was written).

## Deliveries

- `.ufo/waves/round-29/w1/SwarmMutationTester59.md` — this report (only lane file written).
