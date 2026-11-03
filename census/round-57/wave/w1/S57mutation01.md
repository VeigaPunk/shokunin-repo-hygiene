# S57mutation01 — round 57 w1, C2 gate mutation report

Seat: `S57mutation01` (mutation-tester, leaf). Target: `census/round-57/c2-counter.py`
(C2 operability 8, receipt revision-binding gate), frozen at
`sha256 174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2`
(preregistration pin, freeze `d749f7ee`, base `b4ef0bc8`). Expected file:
`census/round-57/records/c2-selftest-expected.tsv`
(`sha256 a2bc835ffa4e2ce3d822a28a344770b3bd106a770918483854669e4238ae1d24`,
8 rows). The committed control `controls/c2-stub.py`
(`sha256 6d7f7534…56555c1`) and every other frozen byte was read-only; all
mutants are scratch copies, scored, then destroyed with the scratch tree.

## Detector (the bounded behavioral check, identical in all arms)

```
TMPDIR=<scratch>/tmp python3 -B <arm>/c2-counter.py --selftest \
  --work <scratch>/work/<arm> \
  --expected <LANE>/census/round-57/records/c2-selftest-expected.tsv
```

A mutant is **KILLED** when this exits non-zero (some `SELFTEST-CASE … fail`),
**SURVIVED** when it exits 0 (`SELFTEST pass cases=8`). One fresh `--work`
dir per arm (the fixture builder `git init`s its own repo there). `--expected`
is passed explicitly because the gate's `DEFAULT_EXPECTED` is relative to the
copy's own directory (`HERE`), which would be empty in a scratch copy.

Baseline on pristine frozen bytes (re-run this session, `c2-baseline-selftest.txt`):

```
SELFTEST-CASE ABSENT pass rc=1 want_rc=1 findings=RECEIPT-REV-ABSENT want_findings=RECEIPT-REV-ABSENT
SELFTEST-CASE DIGEST-MISMATCH pass rc=1 want_rc=1 findings=RECEIPT-INSTRUMENT-DIGEST-MISMATCH want_findings=RECEIPT-INSTRUMENT-DIGEST-MISMATCH
SELFTEST-CASE KEEP-ONLY pass rc=1 want_rc=1 findings=RECEIPT-REV-KEEP-ONLY want_findings=RECEIPT-REV-KEEP-ONLY
SELFTEST-CASE MISSING-REV pass rc=1 want_rc=1 findings=RECEIPT-REV-MISSING want_findings=RECEIPT-REV-MISSING
SELFTEST-CASE NO-EXIT pass rc=1 want_rc=1 findings=RECEIPT-EXIT-MISSING want_findings=RECEIPT-EXIT-MISSING
SELFTEST-CASE NOT-FULL40 pass rc=1 want_rc=1 findings=RECEIPT-REV-NOT-FULL40 want_findings=RECEIPT-REV-NOT-FULL40
SELFTEST-CASE REV-OK pass rc=0 want_rc=0 findings=- want_findings=-
SELFTEST-CASE SHORT-REV pass rc=1 want_rc=1 findings=RECEIPT-REV-SHORT want_findings=RECEIPT-REV-SHORT
SELFTEST control=FALSE-GREEN-REJECTED stub_meets=1 cases=8
SELFTEST pass cases=8
baseline-rc=0
```

Every mutant is an exact single-occurrence replacement (the harness asserts
`count(old) == 1` before writing; diffs in `c2-mutant-diffs.txt`). Result:
**21 mutants — 9 killed, 12 SURVIVED, 0 errors** (`c2-mutation-matrix.txt`).

## Table

| # | mutant | edit | verdict | killed by / surviving line |
|---|---|---|---|---|
| M1 | drop-exit-check | `if not EXIT_RE.search(text)` → `if False` | **KILLED** | NO-EXIT |
| M2 | accept-short-rev | short-hex branch emits nothing | **KILLED** | SHORT-REV |
| M3 | skip-durability | full40 token never classified (no ABSENT/KEEP-ONLY emission) | **KILLED** | ABSENT, KEEP-ONLY |
| M4 | skip-keep-only | keep-only branch emits nothing | **KILLED** | KEEP-ONLY |
| M5 | skip-instrument-pin | whole pin/digest block disabled | **KILLED** | DIGEST-MISMATCH |
| M6 | skip-digest-compare | pin presence kept, committed-blob comparison dropped | **KILLED** | DIGEST-MISMATCH |
| M7 | first-finding-only | selftest compares `got[:1] == want[:1]` | SURVIVED | `SELFTEST pass cases=8` |
| M8 | accept-symlink | `is_symlink()` refusal becomes `pass` (reads through the link) | SURVIVED | `SELFTEST pass cases=8` |
| M9 | skip-column-check | `len(f) != 2` guard demoted to `len(f) > 2` | SURVIVED | `SELFTEST pass cases=8` |
| M10 | accept-symbolic-rev | NOT-FULL40 branch emits nothing | **KILLED** | NOT-FULL40 |
| M11 | skip-rev-missing | a receipt with no `rev=` returns clean | **KILLED** | MISSING-REV |
| M12 | rc-never-fails | `run_manifest` always returns 0 | SURVIVED | `SELFTEST pass cases=8` (with `rc=0 want_rc=1`) |
| M13 | heads-only-durability | refs scanned = `refs/heads` only | SURVIVED | `SELFTEST pass cases=8` |
| M14 | file-name-keyed | fake gate: finding chosen from the receipt basename, receipt and git never read | SURVIVED | `SELFTEST pass cases=8` |
| M15 | drop-keep-only-case | fixture builder stops building the KEEP-ONLY case | SURVIVED | `SELFTEST pass cases=7` |
| M16 | rev-no-boundary | `REV_RE` loses its `(?:^|\s)` left boundary | SURVIVED | `SELFTEST pass cases=8` |
| M17 | gate-first-finding-only | `check_receipt` returns `findings[:1]` | SURVIVED | `SELFTEST pass cases=8` |
| M18 | drop-name-mismatch | receipt-vs-manifest `instrument=` mismatch not emitted | SURVIVED | `SELFTEST pass cases=8` |
| M19 | pin-working-tree | pin compared to `root/instrument` bytes, not `rev:path` | SURVIVED | `SELFTEST pass cases=8` |
| M20 | ref-tip-equality | durability = `rev-parse <ref> == rev` (tip equality, not reachability) | SURVIVED | `SELFTEST pass cases=8` |
| M21 | always-refuse (mirror control) | every receipt carries an extra `RECEIPT-ALWAYS-REFUSE` | **KILLED** | ABSENT, DIGEST-MISMATCH, KEEP-ONLY, NO-EXIT, NOT-FULL40, REV-OK, SHORT-REV |

### Kill roster (exact `SELFTEST-CASE` lines, `c2-kill-evidence.txt`)

```
M1  SELFTEST-CASE NO-EXIT fail rc=0 want_rc=1 findings=- want_findings=RECEIPT-EXIT-MISSING
M2  SELFTEST-CASE SHORT-REV fail rc=0 want_rc=1 findings=- want_findings=RECEIPT-REV-SHORT
M3  SELFTEST-CASE ABSENT fail rc=0 want_rc=1 findings=- want_findings=RECEIPT-REV-ABSENT
    SELFTEST-CASE KEEP-ONLY fail rc=0 want_rc=1 findings=- want_findings=RECEIPT-REV-KEEP-ONLY
M4  SELFTEST-CASE KEEP-ONLY fail rc=0 want_rc=1 findings=- want_findings=RECEIPT-REV-KEEP-ONLY
M5  SELFTEST-CASE DIGEST-MISMATCH fail rc=0 want_rc=1 findings=- want_findings=RECEIPT-INSTRUMENT-DIGEST-MISMATCH
M6  SELFTEST-CASE DIGEST-MISMATCH fail rc=0 want_rc=1 findings=- want_findings=RECEIPT-INSTRUMENT-DIGEST-MISMATCH
M10 SELFTEST-CASE NOT-FULL40 fail rc=0 want_rc=1 findings=- want_findings=RECEIPT-REV-NOT-FULL40
M11 SELFTEST-CASE MISSING-REV fail rc=0 want_rc=1 findings=- want_findings=RECEIPT-REV-MISSING
M21 SELFTEST-CASE REV-OK fail rc=1 want_rc=0 findings=RECEIPT-ALWAYS-REFUSE want_findings=-
    (+ ABSENT, DIGEST-MISMATCH, KEEP-ONLY, NO-EXIT, NOT-FULL40, SHORT-REV fail with the id prepended)
    SELFTEST-CASE MISSING-REV pass …            <- the early return discards every other check
```

So the selftest does guard: the EXIT= requirement, the short-rev refusal, the
absent/keep-only durability classes, pin presence, the committed-blob digest,
the symbolic-rev refusal, the missing-rev refusal, and (via M21) false
positives on the honest receipt. Each of the 8 expected rows is live.

## Fixture-completeness attack (item 3) — 12 named coverage gaps

`c2-survivor-evidence.txt` and `c2-probes.txt`; the probes run in a scratch
repo the driver created (`$S/probe-repo`, `git rev-parse --show-toplevel`
asserted equal to `$S/probe-repo` before the first commit).

| gap | survivor(s) | why it survives | concrete wrongness proven this session |
|---|---|---|---|
| G1 no multi-finding case | M7, M17 | every expected row names exactly one id; the gate's two-finding output is never asserted | P4: receipt `rev=<12hex>` + no `EXIT=` → pristine `findings=2` (`REV-SHORT`+`EXIT-MISSING`), M17 `findings=1` |
| G2 no symlink case | M8 | the builder never creates a symlink; `RECEIPT-SYMLINK` has no row | P3: pristine `FINDING RECEIPT-SYMLINK receipts/link.txt` rc=1; M8 `SUMMARY receipts=1 findings=0` rc=0 |
| G3 no manifest-shape case | M9 | no wrong-column-count manifest is built | P6: pristine `CANNOT-EVALUATE manifest line 2: 1 columns` rc=2; M9 `IndexError: list index out of range` rc=1 |
| G4 the selftest never asserts `rc` | M12 | `passed = (got == want)` only; `want_rc` is printed, not checked | 7 of 8 cases print `pass rc=0 want_rc=1`; P7 over frozen `manifests/before.tsv`: pristine rc=1, M12 rc=0 with the identical `RECEIPT-REV-MISSING` finding |
| G5 no ref-class case (tag/remote) | M13 | only `refs/heads/main` and `refs/jj/keep` exist | P1: rev reachable only from `refs/tags/v1` → pristine clean rc=0; M13 `RECEIPT-REV-ABSENT` (false positive) |
| G6 id-only comparison | M14 | `got = [ln.split(' ')[1] …]` drops the path and every `rev=`/`pin=` detail | M14 reads neither the receipt nor git and passes all 8 with `control=FALSE-GREEN-REJECTED` |
| G7 unbuilt case is silently ignored | M15 | `for name in sorted(cases)`; expected rows not in `cases` are never looked up | `SELFTEST pass cases=7` — one whole row vanished and the selftest still prints pass |
| G8 no token-boundary case | M16 | no receipt contains a decoy `…rev=` token | P2: `sourcerev=<full40>` → pristine `RECEIPT-REV-MISSING`; M16 clean rc=0 |
| G9 no name-mismatch case | M18 | every fixture receipt names the same instrument as the manifest | P5: `instrument=tools/other.py` vs manifest `tools/instr.py` → pristine `RECEIPT-INSTRUMENT-NAME-MISMATCH`; M18 clean |
| G10 pin source not distinguished | M19 | the fixture worktree is left at the measured rev and never dirtied, so worktree bytes == `rev:path` bytes | semantically the Q109 defect itself: the pin no longer binds the committed blob at the named rev (a dirty or advanced worktree passes) |
| G11 ancestor vs tip equality not distinguished | M20 | both fixture revs *are* ref tips | a rev reachable from a branch but not a tip is judged `absent` (false positive) |
| G12 table-shape assumption | (M11/M21 evidence) | `RECEIPT-REV-MISSING` is an early `return`, so that row can never carry a second finding | M21's injected finding is dropped on MISSING-REV — the row passes while 7 others fail |

Finding-id census: the gate can emit **11** ids; the docstring names **9**
(`RECEIPT-MISSING` and `RECEIPT-INSTRUMENT-NAME-MISMATCH` are emitted but
undocumented, so C2's "see the gate docstring for the finding ids" is short by
two); the expected TSV exercises **7**. Untested by the selftest:
`RECEIPT-MISSING`, `RECEIPT-INSTRUMENT-PIN-MISSING`, `RECEIPT-INSTRUMENT-NAME-MISMATCH`,
`RECEIPT-SYMLINK`.

**Did any row prove unreachable?** No — each of the 8 rows can fail, and each
is killed by at least one mutant (ABSENT←M3, DIGEST-MISMATCH←M5/M6,
KEEP-ONLY←M3/M4, MISSING-REV←M11, NO-EXIT←M1, NOT-FULL40←M10, REV-OK←M21,
SHORT-REV←M2). What *is* unreachable is every failure mode outside those eight
ids: a wrong rc, a second finding, a wrong path/detail, a symlinked receipt, a
malformed manifest, a tag-only rev, a non-tip reachable rev, a working-tree
pin, and any expected row whose fixture case is not built.

**Wrong gate that passes all 8:** found, three times — M14 (reads nothing,
returns the id its filename maps to), M19 (right ids, wrong pin source),
M20 (right ids, wrong durability rule). The first is inherent to id-only
comparison; M19/M20 are the meaningful ones: both defeat the Q109 purpose
while staying green.

## Control-line check (item 4)

The frozen arm prints `SELFTEST control=FALSE-GREEN-REJECTED stub_meets=1`
(baseline above). Mutating the **expected file in scratch only**
(`expected-one-row-clean.tsv`: `MISSING-REV` → `-`; `expected-all-clean.tsv`:
every row → `-`), pristine gate, same command with `--expected`:

```
CONTROL-MUT one-nonclean-row-marked-clean  rc=1
        SELFTEST control=FALSE-GREEN-ACCEPTED stub_meets=2
        SELFTEST fail cases=8
CONTROL-MUT all-rows-marked-clean          rc=1
        SELFTEST control=FALSE-GREEN-ACCEPTED stub_meets=8
        SELFTEST fail cases=8
```

So an always-clean gate does flip the line to `FALSE-GREEN-ACCEPTED` — but the
line is a **proxy**: `stub_meets` counts expected rows whose `want` is empty;
`controls/c2-stub.py` is never executed (`grep -c 'c2-stub\|controls/'` on the
gate = **0**). Invoked as if it were the gate under test the committed stub
prints `SUMMARY receipts=0 findings=0`, rc=0, ignoring `--selftest`. The control
therefore validates the expected TSV, not the gate: M14 is a functionally
always-clean gate for any receipt outside the eight fixture names and still
prints `FALSE-GREEN-REJECTED`.

## Disposition

- The C2 selftest target is reproduced on frozen bytes: `SELFTEST pass cases=8`,
  exit 0, `control=FALSE-GREEN-REJECTED` — **AGREE** with T3 as written.
- The claim that the selftest "guards each check" is **ATTACK-FOUND / not
  supported**: 12 of 21 mutants survive, four emitted finding ids have no row,
  the exit-code contract (T1/T2: exit 1 / exit 0) is unasserted, and a gate
  that reads nothing (M14) passes. These are named limits for round 58 — no
  frozen byte was edited (r57 rule).
- Not a dropped mutant to fix here: the frozen predicate is untouched; the
  report routes the gaps.

## Restoration / cleanliness

- Frozen bytes re-derived at the end of the run and unchanged:
  `c2-counter.py 174d7b8a…16ec2`, `c2-selftest-expected.tsv a2bc835f…1d24`,
  `controls/c2-stub.py 6d7f7534…55c1`, `build-fixtures.py 2b8b657b…633b`,
  `record-receipt.sh 84148011…09aa9`, `manifests/before.tsv 1c63e755…efd991`
  (all equal to the preregistration pins).
- No git/jj mutation outside scratch fixture repos: `$S/probe-repo` (created by
  `c2-probe-driver.py`, toplevel asserted before the first commit) and the
  gate's own `$S/work/<arm>/c2-fixtures/repo` (created by `build_fixtures`).
  Lane/fleet repos were read-only (`rev-parse`, `status --porcelain`).
- Scratch `/fast/scratch/hyaku/souji-r57/S57mutation01/` deleted before yield;
  nothing written under `/tmp`.
- Tooling: nothing installed (python3 3.14.8, git 2.56.0 already present).

Seat receipts kept: `c2-baseline-selftest.txt`, `c2-mutation-matrix.txt`,
`c2-mutant-diffs.txt`, `c2-kill-evidence.txt`, `c2-survivor-evidence.txt`,
`c2-probes.txt`, `c2-harness.py`, `c2-probe-driver.py`.
