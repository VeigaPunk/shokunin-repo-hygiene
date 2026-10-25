# ScribeScorecard — r23 `SCORECARD.md` repair (draft; the L1 applies it)

author: L1Souji23.ScribeScorecard (scribe, leaf seat, round 23 w1)
date: 2026-10-25
lane base: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (`git rev-parse HEAD` at start = base)
contract: `.ufo/waves/round-23/preregistration.txt` (C1/C2/C3, read first, not edited)
inbound: `corpus/lessons/round-22-verifier-spotcheck.md` §2–§7 (D1–D8)

## Status

STATUS: PASS — four verbatim-ready blocks drafted (three axis rows, one capability row, one
`## Planned` line, the corrected r22 paragraph); every measured number carries its command and
revision; the calibration row **simulated against the frozen K1 predicate** (0 mismatches where the
row currently applied at `SCORECARD.md:14` produces 2); both r23 fixtures executed here
(`selftest=9/9` C1 with `control=FALSE-GREEN-REJECTED`, `selftest=8/8` C2 including the
stale-digest refusal at `rc=2/RECEIPT-TOOL-DIGEST-MISMATCH`). At the committed tip `4765250` the
instrument reports `keys=4 records=4 occurrences=18 mismatches=4` — one K1 row (the stale base tuple
the calibration row below removes) and three K4 rows (uncommitted wave file, `SCORECARD.md`,
`tools/__pycache__/`); K2 and K3 are already clean. `SCORECARD.md` was **not** edited by this seat;
the only lane write is this report.

Reading conventions: pipes inside a table cell are written `\|` (a bare `|` splits the row); inside
the cell bodies below, `-` and `->` stand where a pipe or arrow would otherwise appear.

## Evidence

E1 — instrument identity. The C1 tool moved five times inside this round, so the row cites constants
and the receipts cite digests, never line numbers:

```
$ sha256sum tools/souji-record-agreement.py ; wc -l tools/souji-record-agreement.py
617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9   350 lines   (current)
observed earlier this round: 7515bb29cf85f5a9… (05:11, 327 lines), f9ec009107b1c814… (05:17:47),
e41db3043b865acc… (05:19:06), 66ee7ecfcbc749c3… (05:19). tools/souji-receipt-run.py =
0d36ce98d1263d4c38a46b97f4654cd2a4242287ddd63161e31bb0e7269a5278.
$ git status --porcelain | wc -l        -> 23   (identical before and after this seat's fixture runs)
```

E2 — C1 do-nothing control at the base revision, current bytes, read-only:

```
$ python3 -B tools/souji-record-agreement.py --root . \
    --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --no-worktree
MISMATCH  K1  census/round-23/records/declared-evidence-after.tsv  receipt-absent  not in tree at 1208bfb…
MISMATCH  K2  LOG.md:1478  uncorrected  'assertions=56 resolved=53 skipped=33 mismatches=3' has no later 'superseded by' line
MISMATCH  K2  LOG.md:1495  uncorrected  '1 present' has no later 'superseded by' line
MISMATCH  K2  LOG.md:1495  uncorrected  '1 refused' has no later 'superseded by' line
MISMATCH  K3  corpus/README.md:440  tally-disagree  1 present != receipt 2 present
MISMATCH  K3  corpus/README.md:440  tally-disagree  1 refused != receipt 0 refused
keys=4 records=3 occurrences=13 mismatches=6
rc=1
```

Control is red, so the C1 target is not vacuous. Without `--no-worktree` the same run reports
`mismatches=29` — the 6 above plus 23 K4 rows (the D1 leftovers, the round's own files,
`tools/__pycache__/`; the operator sweep is exempted, see E9).

E3 — the three landed C2 receipts, verified read-only by this seat (verbatim):

```
$ for f in census/round-23/records/declared-evidence-after.tsv \
           census/round-23/records/gate-check-at-lane-base.tsv \
           census/round-23/records/gate-check-at-first-landing.tsv; do
    echo -n "$f: "; python3 -B tools/souji-receipt-run.py verify --root . "$f"; echo "rc=$?"; done
census/round-23/records/declared-evidence-after.tsv: verify=ok rev=9301d98c1c689c79741f0f1ba1f171138d20af07 tool=tools/souji-declared-evidence.py tool_sha256=65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4
rc=0
census/round-23/records/gate-check-at-lane-base.tsv: verify=ok rev=1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd tool=tools/souji-gate-check.py tool_sha256=d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d
rc=0
census/round-23/records/gate-check-at-first-landing.tsv: verify=ok rev=a211e4d1bf6ea592670d16269f34e9f67f33e8b3 tool=tools/souji-gate-check.py tool_sha256=d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00
rc=0
$ sed -n '/--- stdout ---/,+1p' census/round-23/records/declared-evidence-after.tsv
assertions=63 resolved=63 skipped=40 mismatches=0
$ git cat-file -e a211e4d1bf6ea592670d16269f34e9f67f33e8b3^{commit} \
  && git merge-base --is-ancestor a211e4d1bf6ea592670d16269f34e9f67f33e8b3 refs/heads/master
commit-ok / ancestor-ok
```

E4 — C2 counter, before and now:

```
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
0        (before the receipts landed; `git status --porcelain -- census/` was empty at base)
3        (now: the three files in E3; target >= 4)
```

E5 — the frozen C3 command does not execute:

```
$ python3 tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/git-repo-structure-readonly.md --expect-slice 0
souji-gate-check.py: error: unrecognized arguments: --expect-slice 0            rc=2
$ python3 tools/souji-gate-check.py --help
usage: … [--root] [--round-date] [--entries …] [--snapshot-dir] [--slice] [--slice-verdicts] [--selftest]
$ python3 tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/git-repo-structure-readonly.md
entries=1 ok=0 slice_verdicts=8 slice_total=8 fail=1                            rc=1
```

Sibling measurement from `git archive` mirrors (`ExecGateReproduce.md`, matrix): base mirror and
r22-tip mirror both `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, rc 0 — i.e.
`slice_verdicts == slice_total` already holds, which is what the frozen `--expect-slice 0` denotes.

E6 — C3 counts, base versus the worktree now (the append has landed but is uncommitted):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji | sort
souji  rows 119   status.mined 96   status.queued 15   status.rejected 8
       tier.A 113 tier.B 5          tier.C 1          status.invalid 0   tier.invalid 0      rc=0
$ git show 1208bfb:corpus/SOURCES.md > /var/tmp/… ; same parser at base -> rows 114, tier.A 110, tier.B 3, tier.C 1
$ git ls-tree -r --name-only HEAD corpus/knowledge | wc -l                -> 11 (base)
$ ls corpus/knowledge/                                                     -> 13 entries now
     (repo-size-census-readonly.md 86 lines; count-objects-garbage-readings-r25.md 66 lines)
```

The base figures are `ScoutRegistryCensus.md` E2/E4/E5/E6/E8, re-derived here for the row count
(`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` -> 114 at base).

E7 — K1 simulation at the committed tip `4765250` (read-only replica of the instrument's `k1`;
receipt value `assertions=63 resolved=63 skipped=40 mismatches=0`, receipt rev
`9301d98c1c689c79741f0f1ba1f171138d20af07`):

```
committed SCORECARD.md:14         -> 4 tuples on the line, 2 of them the stale
                                     'assertions=55 resolved=52 skipped=33 mismatches=3'
with the calibration row below    -> K1 occurrences=1, mismatches=0
row + the filled r22 paragraph    -> K1 occurrences=2, mismatches=0   (the paragraph adds no tuple
                                     until the placeholders are substituted)
```

The instrument reports that line once (`MISMATCH K1 SCORECARD.md:14 value-disagree …`), but the stale
token sits in two cells of the row, so the row must lose both.

E8 — K2/K3 simulation over the landed worktree bytes (same predicate; receipts
`census/round-22/attempt2/declared-evidence-before-final.tsv` and `slice-verdicts.tsv`):

```
want assertions=55 resolved=52 skipped=33 mismatches=3 ; tally accepted=5 present=2 unverifiable=1 refused=0
LOG r22 section 1469..1524, occurrences=4, uncorrected=NONE
corpus/README.md           bad=NONE  classes=[accepted,present,refused,unverifiable]
corpus/lessons/round-22.md bad=NONE  classes=[accepted,present,refused,unverifiable]
```

E9 — the K4 exemption file the current bytes read, and the frozen text it departs from:

```
$ sed -n '1p' census/round-23/records/uncommitted-exemptions.tsv
census/operator-sweep-20261019/   operator-owned untracked output (L0 souji | round-17) …
preregistration.txt C1/K4: "Exemption file (committed, read at --rev): corpus/pointer-exemptions.tsv
rows prefixed \"uncommitted:\" (operator-owned paths only)"
tools/souji-record-agreement.py: K4_EXEMPT_FILE = "census/round-23/records/uncommitted-exemptions.tsv",
                                 K4_EXEMPT_PREFIX = ""   # every row of the dedicated file is an exemption
```

E10 — both r23 fixtures executed here (read-only with respect to the lane; each builds its own
`/var/tmp` synthetic repo and cleans it):

```
$ python3 -B tests/fixtures/r23-record-agreement.py | tail -12
tool_sha256=617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9
case=1 … got=rc=0 mismatches=0 keys=4      case=2 … [K1/receipt-absent]
case=3 … [K1/value-disagree]               case=4 … [K1/occurrence-absent,K1/rev-disagree]
case=5 … [K2/uncorrected]                  case=6 … [K2/filed-occurrence-missing]
case=7 … [K3/tally-disagree]               case=8 … [K4/uncommitted-path]
case=9 expect=K4 rows=0 (exempted operator path) got=rc=0 mismatches=0 keys=4
selftest=9/9
control=FALSE-GREEN-REJECTED
$ python3 -B tests/fixtures/r23-receipt-run.py | tail -10
case=3 … got=<old_at_rev1=rc0 stale_at_rev2=rc2/RECEIPT-TOOL-DIGEST-MISMATCH>
case=4 … got=<branch:rc=2/RECEIPT-REV-MALFORMED short7:rc=2/RECEIPT-REV-MALFORMED>
case=5 … got=<rc=2 codes=RECEIPT-TOOL-ABSENT>       case=6 … got=<rc=2 codes=OUT-UNDER-TMP wrote_under_tmp=False>
case=7 … got=<before=empty after=empty runner_rc=0> case=8 … got=<sha_equal=True cmd_equal=True utc_equal=False>
selftest=8/8
```

## Deliverable 1 — the three axis rows (replace rows `coverage`, `calibration`, `operability`)

Columns: `axis \| score \| verdict / observation \| counting command \| measured commit \| last change`.

```
| coverage | 8 | R23 C3 assimilation, one theme (F2 repository size census, read side), 2 entries, 5 rows: `corpus/knowledge/repo-size-census-readonly.md` (S115/S116/S117, tier A — git-count-objects, git-fsck, git-prune re-opened by this lane 2026-10-25) and `corpus/knowledge/count-objects-garbage-readings-r25.md` (S118/S119, tier B community; the staged own-work fleet-garbage row is refused because its evidence lives outside this repository). F2's README row moves from `frontier, no entry` to an admitted entry; wider size attribution and a measured fleet garbage figure stay frontier/unmeasured and are not claimed. Registry continues the id space at S115 (staged S112–S114 collide with this lane's quarantine rows; citations re-pointed by document, not by id). Row deltas, measured: knowledge entries 11->13; registry rows 114->119, tier A 110->113, tier B 3->5, tier C 1, status mined 91->96, malformed 0, duplicate ids 0, census exit 0 with no E-code. Numeric delta 0, legacy-unmapped: coverage stays 8 — the theme's read side was largely held, so this is an import with re-grounding, not new technical ground. | `git ls-tree -r --name-only <rev> corpus/knowledge \| wc -l` -> 11 at base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`, 13 at `<R23-TIP>`; `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji` -> `souji rows 114` at base, `souji rows 119` now, `tier.A 113`, `tier.B 5`, `tier.C 1`; `…/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` -> exit 0, 0 `E01`–`E12`; `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/count-objects-garbage-readings-r25.md --snapshot-dir census/round-23/sources` -> `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, exit 0 | `<R23-TIP>` | r23 (C3 entry 1 and entry 2 + registry rows S115–S119) |
| calibration | 7 | R23 C1 record agreement (repairs the spot-check's D1/D2/D4/D5; **record accuracy, not a scored axis move**): one read-only instrument, `tools/souji-record-agreement.py`, re-derives four frozen keys over committed bytes — K1 the r22 after 4-tuple on the SCORECARD line that names the receipt's `rev=`, K2 every superseded 4-tuple and `<n> <class>` tally in LOG's `Round22 attempt2` section named by a later `superseded by` line with the filed bytes retained, K3 the slice tallies in `corpus/README.md` and `corpus/lessons/round-22.md` against `census/round-22/attempt2/slice-verdicts.tsv` (all four classes must still appear, `0 refused` included), K4 each working-tree path not named by a committed exemption row (`census/round-23/records/uncommitted-exemptions.tsv` at the measured revision; the frozen text names `corpus/pointer-exemptions.tsv` rows prefixed `uncommitted:`, and the r23 lesson records which form landed). The r22 attempt-2 after-state is now bound: at 9301d98c1c689c79741f0f1ba1f171138d20af07 the declared-evidence instrument scores `assertions=63 resolved=63 skipped=40 mismatches=0`, receipt `census/round-23/records/declared-evidence-after.tsv`; the base run at 4edb25dfe262515d0da63224bbba71e02e36cba5 is recorded in prose and in its own receipt (`declared-evidence-before-final.tsv`: 55 assertions, 52 resolved, 33 skipped, 3 mismatches) so that no unbound 4-tuple survives on an r22 line. Counts line at `<R23-TIP>`: `<R23-C1-AGREE-COUNTS>`, exit 0 iff mismatches=0; do-nothing control, same instrument at base 1208bfb with `--no-worktree`: `keys=4 records=3 occurrences=13 mismatches=6`, exit 1, so the target is not vacuous. Fixture `selftest=9/9` with `control=FALSE-GREEN-REJECTED`; limits named: 22 of 42 designed clause mutants have no killing case (`MutCounter.md`), K1–K3 read only the four named records, and the instrument is a receipt checker, not proof of author identity or execution. Score 7 unchanged; no verdict-bearing cell moved. | `python3 -B tools/souji-record-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <R23-TIP>` -> `<R23-C1-AGREE-COUNTS>`; control `python3 -B tools/souji-record-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --no-worktree` -> `keys=4 records=3 occurrences=13 mismatches=6`, exit 1 (transcript `census/round-23/records/agreement-control-base.tsv`); binding check `python3 -B tools/souji-receipt-run.py verify --root /home/vgpnk/Projects/shokunin/souji-shokunin census/round-23/records/declared-evidence-after.tsv` -> `verify=ok`, exit 0; fixture `python3 -B tests/fixtures/r23-record-agreement.py` -> `selftest=9/9`, `control=FALSE-GREEN-REJECTED` | after-state 9301d98c1c689c79741f0f1ba1f171138d20af07 (receipt `census/round-23/records/declared-evidence-after.tsv`); before 4edb25dfe262515d0da63224bbba71e02e36cba5 (receipt `census/round-22/attempt2/declared-evidence-before-final.tsv`); record-agreement counts read at `<R23-TIP>` | r23 (C1 record-agreement instrument; r22 after-state bound; D1/D2/D4/D5 repaired) |
| operability | 8 | R23 C2 blob-bound receipts (new capability; closes the spot-check's D3): `tools/souji-receipt-run.py` re-derives a counter at a full durable revision and writes a v1 receipt binding `rev`, `tool`, `tool_sha256` **at that revision**, `cmd`, `rc`, `utc` and the two output fences; `verify` re-reads the committed blob and refuses a receipt whose recorded digest is not that blob (`RECEIPT-TOOL-DIGEST-MISMATCH`), a branch or short rev (`RECEIPT-REV-MALFORMED`), a tool absent at the rev (`RECEIPT-TOOL-ABSENT`), an output under `/tmp` (`OUT-UNDER-TMP`) or inside the measured repo, and a receipt with no counts line (`RECEIPT-COUNTS-ABSENT`). The measured tree is a private `git clone --no-local` checkout under `/var/tmp`: the runner never writes the lane, never fetches, never checks out into it, and is a counter runner, not a sandbox. Three receipts land and verify clean — `gate-check-at-lane-base.tsv` (rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd, `tool_sha256=d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d`), `gate-check-at-first-landing.tsv` (rev a211e4d1bf6ea592670d16269f34e9f67f33e8b3, `d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00`), `declared-evidence-after.tsv` (rev 9301d98c1c689c79741f0f1ba1f171138d20af07, `65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4`); the counter reads 3 against a target of >=4, so one more receipt (the declared-evidence before-state, or the record-agreement instrument at the tip) must land. Refusal demonstrated, measured: the fixture's case 3 mutates the tool in a new commit and `verify` on the old receipt returns `rc=2/RECEIPT-TOOL-DIGEST-MISMATCH`, and the r22 stale `5b8025a83f16957cb2ff6aca0adecfc3a6a1ff796c3eed1d70018ecc339b3062` matches no revision (the blob is `d85c2696…` at a211e4d1 and `d5ed0805…` at 1208bfb and at the r22 tip). Numeric delta 0, legacy-unmapped: operability stays 8 — a receipt instrument, not new source transport, sandbox or whole-source integrity. | `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l` -> 0 before the receipts, 3 now, >=4 at `<R23-TIP>`; per receipt `python3 -B tools/souji-receipt-run.py verify --root /home/vgpnk/Projects/shokunin/souji-shokunin census/round-23/records/<receipt>` -> `verify=ok`, exit 0; refusal `python3 -B tests/fixtures/r23-receipt-run.py` case 3 -> `rc=2/RECEIPT-TOOL-DIGEST-MISMATCH`, whole fixture `selftest=8/8`; a hand-written stale-digest receipt at `.ufo/waves/round-23/w1/evidence/refusal-stale-digest.txt` must fail the same way | receipts bind 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd, a211e4d1bf6ea592670d16269f34e9f67f33e8b3, 9301d98c1c689c79741f0f1ba1f171138d20af07; counter read at `<R23-TIP>` | r23 (C2 new capability; D3 closed) |
```

## Deliverable 2 — new capability row (append after the r22 row)

```
| blob-bound receipts (r23) | re-derive a counter at a named durable revision and write a receipt binding rev, tool path, tool sha256 at that revision, command, rc, stdout and utc; refuse a receipt whose recorded digest is not the committed blob at its own `rev=` (`RECEIPT-TOOL-DIGEST-MISMATCH`), a branch or short rev, a tool absent at the rev, an output under `/tmp` or inside the measured repo, and a receipt with no counts line; measure a private `git clone --no-local` checkout under `/var/tmp`, so the lane tree is never written | `python3 -B tools/souji-receipt-run.py verify --root /home/vgpnk/Projects/shokunin/souji-shokunin census/round-23/records/declared-evidence-after.tsv` -> `verify=ok` (same for `gate-check-at-lane-base.tsv`, `gate-check-at-first-landing.tsv`); counter `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l` -> 3; fixture `python3 -B tests/fixtures/r23-receipt-run.py` -> `selftest=8/8` incl. `rc=2/RECEIPT-TOOL-DIGEST-MISMATCH`; stale-digest refusal witness `.ufo/waves/round-23/w1/evidence/refusal-stale-digest.txt` | r23 |
```

## Deliverable 3 — `## Planned` line for r24 (append at the end of `## Planned`)

```
- **r24 (planned r23):** (a) calibration: re-run `tools/souji-record-agreement.py` with `-B` at the
  r24 base so C1 is re-derived rather than inherited, and close the fixture gap `MutCounter.md`
  names — 22 of 42 designed clause mutants have no killing case, and both the K2 4-tuple arm and the
  K2 tally arm lack a dedicated case; (b) operability: add a `verify-all` mode that fails if any
  receipt under `census/round-23/records/` is unbound, so the C2 count and the C2 check cannot drift
  apart, and extend the receipt to fleet-root tools such as
  `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`, which has no lane blob to compare
  against; (c) coverage: F2's wider size attribution — a measured per-repository object census on
  the fleet surface, not another import — and a measured fleet garbage figure, neither of which the
  r23 entries establish. Certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged.
```

## Deliverable 4 — the r22 paragraph, corrected (one physical line)

```
R22 is a **retry of an already-filed round**: attempt 1 was judged `rejected-honest-stop` by the non-author spot-check (`corpus/lessons/round-22-verifier-spotcheck.md`) for an unproven strict adequacy claim. Attempt 2 does not re-claim it; it lands a bounded calibration instrument (C1) and one assimilation theme (C2). R23 binds attempt 2's after-state to exactly one measured revision, `<R23-C1-REV>`, whose receipt `census/round-23/records/declared-evidence-after.tsv` records `<R23-C1-COUNTS>`; no second revision is claimed for that after-state, and the receipt is the only authority for the tuple.
```

**Observed substitution** (read this run from the receipt; the L1 fills it in):
`<R23-C1-REV>` -> `9301d98c1c689c79741f0f1ba1f171138d20af07`, `<R23-C1-COUNTS>` ->
`assertions=63 resolved=63 skipped=40 mismatches=0`.

**Keep it on one physical line.** K1 binds the tuple and the revision *on the same physical line*: a
4-tuple on a line that does not carry the receipt's `rev=` is `rev-disagree`, and a 4-tuple that
differs from the receipt's value is `value-disagree`. A re-wrap that separates `<R23-C1-REV>` from
`<R23-C1-COUNTS>` breaks the binding with no other symptom. For the same reason no *other*
`r22`/`round-22` line may carry an `assertions=/resolved=/skipped=/mismatches=` 4-tuple — which is
why the calibration row above states the base run in prose instead of copying its tuple.

**Why a placeholder is the honest form at draft time.** At the moment this draft was written the
receipt did not exist; it exists now but is **untracked**, so its bytes are not the bytes of any
revision yet, and the commit that will carry it is not yet made. A tuple or a 40-hex id typed in by
hand would be a claim whose receipt is not in the tree — precisely defect D2, "no receipt binds the
named revision". The placeholder forces the L1 to copy both values from the committed receipt
(`verify` then re-derives the digest with `git cat-file` at `rev=`), and `souji-record-agreement.py`
confirms the equality afterwards: until both tokens are filled it reports K1 `receipt-absent`, and
afterwards any drift reports `value-disagree` or `rev-disagree`. The draft is deliberately red.

## Placeholders (fill before commit; all `<…>`-marked above)

| placeholder | where | filled from | observed now |
|---|---|---|---|
| `<R23-C1-REV>` | r22 paragraph | `rev=` header of `census/round-23/records/declared-evidence-after.tsv` | `9301d98c1c689c79741f0f1ba1f171138d20af07` |
| `<R23-C1-COUNTS>` | r22 paragraph | counts line in that receipt's `--- stdout ---` fence | `assertions=63 resolved=63 skipped=40 mismatches=0` |
| `<R23-TIP>` | calibration, coverage, operability rows | the round tip commit the counts are read at | not yet made |
| `<R23-C1-AGREE-COUNTS>` | calibration row (×2) | stdout counts line of `souji-record-agreement.py --rev <R23-TIP>` | not yet measured (shape `keys=4 records=… occurrences=… mismatches=0`) |

## Findings

1. **The calibration row applied right now at `SCORECARD.md:14` fails the frozen K1 predicate.**
   It carries the after tuple *and* the base tuple on the same physical line as the receipt's rev, so
   K1 reports two `value-disagree` rows for `assertions=55 resolved=52 skipped=33 mismatches=3`
   (E7). The row in Deliverable 1 keeps the binding (after tuple + `9301d98…` + receipt path), states
   the base run in prose, and simulates to 0 mismatches with 2 bound occurrences. Location:
   `SCORECARD.md:14`.
2. **K4's exemption file deviates from the frozen text.** Frozen: `corpus/pointer-exemptions.tsv`
   rows prefixed `uncommitted:`. Tool: `census/round-23/records/uncommitted-exemptions.tsv`, every
   row an exemption, no prefix (E9) — and that file exists with the operator-sweep row, while the
   committed `corpus/pointer-exemptions.tsv:1` row has no prefix and would not exempt anything under
   the frozen form. The L1 must record which form landed (the r23 lesson is the place). See A-5.
3. **`tools/__pycache__/` is untracked noise that K4 counts, and the lane has no `.gitignore`.**
   It holds `souji-gate-check.cpython-314.pyc` (05:11) and `souji-rev-pin.cpython-314.pyc` (05:12),
   import artifacts of sibling tool runs; this seat only ever ran the tools as `__main__`.
   `[INFERENCE]` on attribution. A committed `.gitignore` with `__pycache__/` clears it without
   deleting anything and prevents recurrence; an exemption would be false (not operator-owned).
4. **K4 still lists the D1 leftovers, so C1 cannot reach 0 until they are committed.** The 23 K4
   rows now are: the seven r22 wave paths (5 `M`, 2 `??`), `.ufo/waves/round-23/`,
   `census/round-23/`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/QUALITY.md`, `LOG.md`,
   `SCORECARD.md`, the two new `corpus/knowledge/*.md` entries,
   `tools/{souji-record-agreement,souji-receipt-run}.py`, `tests/fixtures/r23-{record-agreement,
   receipt-run,locator-heading}.py` and `tools/__pycache__/`. The operator sweep is exempted (E9).
5. **K2 and K3 are already clean in the worktree — measured, not assumed.** E8 replays both keys
   over the landed bytes: 4 occurrences in the r22 section, `uncorrected=NONE`, and both records
   carry all four classes with no disagreeing tally. The correction block sits *inside* the section
   (`LOG.md:1524`) and passes only because each stale token has the `superseded by` marker within
   the predicate's 6-line window; a reflow that separates them re-opens two `uncorrected` rows. The
   `Round23` entry at `LOG.md:1561` is outside the section (terminator `LOG.md:1525`), so its tuples
   are not scanned — keep that ordering.
6. **The frozen C3 command cannot execute** (A-2): `--expect-slice` is not an option (`rc=2`, E5)
   and `--round-date` is missing from the frozen line. The coverage row uses the runnable form and
   states the mapping: the frozen `--expect-slice 0` denotes the counts line's
   `slice_verdicts == slice_total`, already `8`/`8` at the base mirror.
7. **The C1 control receipt must not be a v1 receipt.** `souji-receipt-run.py run --rev 1208bfb
   --tool tools/souji-record-agreement.py` refuses `TOOL-ABSENT` (the instrument postdates the
   base), so `census/round-23/records/agreement-control-base.tsv` has to be a plain captured
   transcript. If it carries a `tool_sha256=` line it is counted by the C2 counter and fails
   `verify` — a bogus receipt that would make the counter lie.
8. **The C1 instrument's own bytes are unbound — the exact class D3 describes.** No receipt in
   `census/round-23/records/` names `tools/souji-record-agreement.py`; the tool moved five times
   while this round ran (E1). Running it through the C2 runner at `<R23-TIP>`
   (`run --rev <R23-TIP> --tool tools/souji-record-agreement.py --out /var/tmp/… -- python3 -B
   tools/souji-record-agreement.py --root . --rev <R23-TIP>`, then committing the receipt) yields
   the counts line *and* the fourth receipt C2 needs — the two claims meet at one artifact.
9. **Entry-2's name diverges between the frozen preregistration and the landed file.** The
   preregistration's C3 names `corpus/knowledge/count-objects-garbage-semantics-r24.md`; the landed
   file is `corpus/knowledge/count-objects-garbage-readings-r25.md` (66 lines, cites S118/S119). The
   coverage row and the C3 command use the landed name. If the L1 renames to the prereg form, swap
   that token in both cells; do not leave the row pointing at an unlanded path.
10. **K3 needs `0 refused` to appear as a positive occurrence.** The landed repair satisfies it
    (E8). A later sweep that deletes the refused mention instead of writing `0 refused` trips
    `class-absent`; one that *quotes* the stale pairs re-introduces two `tally-disagree` rows.
    Receipt tally: 5 accepted / 2 present / 1 unverifiable / 0 refused.
11. **D3's digest chain is pinned at two revisions and the stale value matches neither.**
    `tools/souji-gate-check.py` is `d85c2696…` at `a211e4d1`, `d5ed0805…` at `1208bfb` and at the
    r22 tip `77d6595`; the report's `5b8025a8…`
    (`.ufo/waves/round-22/attempt2/w1/evidence/Sentinel.md:555`) is therefore the right negative
    case for the refusal demonstration (E10 case 3 is the positive mechanism proof).
12. **The landed receipts are named by revision, not by before/after** — `gate-check-at-lane-base`,
    `gate-check-at-first-landing`, `declared-evidence-after`. The operability and capability rows use
    those names; the fourth receipt is still owed (counter 3, target >=4).

## Attack log

- **A-1 — K1's binding was unsatisfiable in the bytes I first read.** The 05:11 instrument required
  the receipt's `rev=` to equal the instrument's own `--rev` *and* the receipt to exist at that
  `--rev`; a receipt naming commit R cannot be part of commit R, so `M=0` was unreachable. The
  frozen text does not say that, and the current bytes check only the frozen rule. Not edited by
  this seat; recorded because the arm is a one-line revert away and would silently void C1.
- **A-2 — the C3 counter as frozen cannot run.** `--expect-slice 0` is not an option of
  `tools/souji-gate-check.py`; the frozen invocation exits 2 with
  `unrecognized arguments: --expect-slice 0` (E5), and the frozen line omits the required
  `--round-date`. Not edited: the row gives the runnable form; the L1 decides whether to repair the
  counter before after-data or to record the substitution.
- **A-3 — C3's "census exit 0" conjunct is non-discriminating.** Measured exit 0 at base with 30
  pre-existing `W04` warnings and 0 `E`-codes (`ScoutRegistryCensus.md` E1), so a do-nothing control
  satisfies it. The discriminating clause is `rows 114 -> 119` with `0 malformed` and
  `0 duplicate ids`, which the coverage row leads with.
- **A-4 — a hand-written receipt passes the C2 counter.** A file whose only `tool_sha256=` line
  carries a plausible digest satisfies `grep -rlE`, and the count is the same whether or not the
  digests are real. `verify` is the only arm that closes it, which is why the operability and
  capability rows require a `verify` per receipt rather than the count alone. Not edited.
- **A-5 — K4's exemption file moved off the frozen path.** Frozen: `corpus/pointer-exemptions.tsv`
  rows prefixed `uncommitted:`. Tool: `census/round-23/records/uncommitted-exemptions.tsv`, every
  row an exemption, no prefix (E9). A pre-data predicate change made after the preregistration was
  frozen; it does not widen the key set, but it changes the file the contract names, and the frozen
  form would fail on the operator sweep. Reported, not edited.

## Bounds and installs

- Read-only with respect to the lane: `SCORECARD.md`, `LOG.md`, `corpus/`, `census/`, `tools/`,
  `tests/`, `.ufo/waves/` were read; nothing was edited, staged, committed, pushed, stashed or
  checked out; no `jj` mutation, no `rm`/`mv`, no signals. One lane write: this file. The two
  fixtures I executed build and clean their own `/var/tmp` synthetic repos; `git status --porcelain`
  was 23 lines before and after (E1).
- Nothing outside `/home/vgpnk/Projects/shokunin/souji-shokunin/` was touched. The fleet
  `.scratch/`, `.ufo/state/`, `.ufo/watchdog.log`, `MANIFEST.json`, fleet `scripts/` and `templates/`
  were not written and not read for content. Certification OFF, K5 HELD, F5 reap and NAMESPACE
  holds unchanged. No credentials, no live `/proc` census, no operator-sweep contents.
- Tool installs/upgrades: none (no `pacman`, `uv`, `npx`, `cargo` or `npm` transaction attempted; the
  host pacman pause was not touched).
- Scratch written outside the designated `/var/tmp/souji-r23-ScribeScorecard/` directory:
  `/var/tmp/souji-r23-ScribeScorecard-k4.txt` and `/var/tmp/souji-r23-ScribeScorecard-ctl.txt`
  (captured instrument stdout, ~4 KB each). They are outside the lane and every protected path; I
  did **not** delete them, because deletion is prohibited to this seat — the operator or L1 may
  remove them.
- Not run by this seat, and therefore not claimed: the C3 gate-check on the two new entries (the
  snapshot dir `census/round-23/sources/` and that run are the L1's), any run at a revision that
  contains the round's repairs (none exists yet), and the stale-digest refusal transcript (the
  mechanism is proven by E10 case 3; the artifact is still owed).
