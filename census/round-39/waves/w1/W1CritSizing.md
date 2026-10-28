# W1CritSizing — claim sizing against addendum §9 (souji r39, w1)

Role: critic. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Contract: `census/round-39/preregistration.txt` at freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`.
Lane base: `ed30b7f5b77939c9073348d810730bc4f355708d`. Measured revision: `2201778e7736af82e7d8a42dec2494f115bf3923`
(lane tip at the first measurement). The tip advanced during this session to
`d4c17557b92fd98044e4c8f0ddc79c6d75701b15` (all three counters re-measured there with the same
verdicts — see §1) and then to `f8ba3f3b4fdac9669182af1c2829d79c1658f314`, which changes only
`census/round-39/records/` and therefore no counter input.
Section 9 read from `/home/vgpnk/Projects/shokunin/scripts/hyaku/lane-addendum.md:389-406`.
Scratch: `/fast/scratch/hyaku/souji-r39/W1CritSizing` (2.1 MB, still on disk: `repo-c1`, `repo-c1b`, `repo-c2`, `c3/`).
No tool installed or upgraded.

The two §9 sentences this seat applies:

> Declare each after-state as one concrete value that the closure can re-derive with one command
> over committed bytes. [...] A calibration claim must count mismatches between the lane's
> self-assessment (SCORECARD/SHONEN) and observed repo state. It cannot be an assertion.
> [...] A target must be one a do-nothing control cannot reach [...] build the cheapest control
> that skips the claimed work, score it with the frozen counter, and commit that receipt.

## 1. Sizing table (after-state, one command, do-nothing reachability)

| Claim | After-state (one value) | One command that re-derives it | Do-nothing control reaches it? |
|---|---|---|---|
| C1 | `SUMMARY items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=6`, exit 0 | `python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <landing-40hex> --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv` | **YES** — 16 prose lines + 6 synthetic receipts on the base bytes reach the exact target (control 1). |
| C2 | `SUMMARY legs=6 pass=6 fail=0 harm=0`, exit 0 | `python3 -B census/round-39/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <landing-40hex> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d` | **NO** — an always-exit-2 tool reaches `pass=4 fail=2 harm=2`, not `pass=6` (control 2). |
| C3 | `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6`, exit 0 | `python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <landing-40hex> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d` | **YES** for a fixture that fails on any byte change: `killed=4 survived=0 pristine=ok base_killed=0 cases=6`, exit 0 (control 3b). An unconditional always-fail fixture is blocked (`pristine=FAIL`, control 3a). |

Current readings at the lane tip (`2201778`), for completeness:

- C1: `SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358`, rc=1.
  `R39-C1-03` and `R39-C1-04` are `OPEN FILE-ABSENT` (`census/round-39/records/waves-wait.txt`,
  `waves-capture.txt`); `census/round-39/cells.tsv` does not exist (`git ls-files` returns 0 rows).
  **C1 is not at its after-state at the measured tip.**
- C2: `SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81`, rc=0.
- C3: `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5`, rc=0.

Re-measured at the current tip `d4c17557b92fd98044e4c8f0ddc79c6d75701b15`:

```
C1  SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358   rc=1
C2  SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484   rc=0
C3  SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5   rc=0
```

Base controls re-derived (the committed before receipts are genuine for the *after* counters):

```
python3 -B census/round-39/c1-counter.py --root $L --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch $S/tmp
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358   rc=1
python3 -B census/round-39/c2-counter.py --root $L --rev ed30b7f... --base-rev ed30b7f... --scratch $S/tmp
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=e555d8281484   rc=1
python3 -B census/round-39/c3-counter.py --root $L --rev ed30b7f... --base-rev ed30b7f... --scratch $S/tmp
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5   rc=0
```

The C3 base re-run is **not** the committed control (`census/round-39/records/c3-before.txt` says
`killed=0 survived=4 ... cases=10 fixture_sha=ac0be0e7a49e`); see defect D4.

## 2. Control 1 — C1 `open=0` from prose that changes nothing

Built `/fast/scratch/hyaku/souji-r39/W1CritSizing/repo-c1` (`git init`; `git rev-parse
--show-toplevel` == that dir asserted):

- `c0 = 30656b3dd989cd631817f5cd0b8a6afe5c51d4e3` — the ten named item files copied from lane
  base `ed30b7f`, six receipt files each containing `SUMMARY legs=6 pass=6 fail=0 harm=0`, and the
  frozen `tools/souji-citation-reconcile.py` copied verbatim from `2201778`.
- `c1 = 3ef19b734cfcf93e35f29aa90158401429004ece` — `git commit --allow-empty` (the commit arm's
  target).
- `c2 = d2047ad22ce9c0bbc6c02d3ac2d3edf44eee8422` — 16 prose lines (one per item, carrying every
  `must` token and no `mustnot` token), a 6-row `census/round-39/cells.tsv`, and 6 citation
  sentences naming `c1` and their receipt. **No lane tool and no routed defect is repaired**; the
  diff is `11 files changed, 29 insertions(+)` (16 item sentences + 7 register file lines + 6
  register sentences).

```
$ python3 -B $L/census/round-39/c1-counter.py --root $S/repo-c1 --rev d2047ad22ce9c0bbc6c02d3ac2d3edf44eee8422 \
    --items $L/census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch $S/tmp
ITEM R39-C1-01 CLOSED
[... all 16 CLOSED ...]
REGISTER cells=6 mismatches=0 commit_distinct=6
SUMMARY items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=d892b74f8358
rc= 0
```

Same repo at `c0` (base bytes, no prose):

```
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc= 1
```

**Verdict C1: FAIL §9.** The after-state is reachable by the cheapest work-skipping control: 16
sentences that quote the tokens, on the defective base bytes. The item arm is an assertion of text
presence, not the §9-mandated mismatch count between self-assessment and observed state; 14 of the
16 items point at self-assessment files (`corpus/lessons/*` ×7, `SKILL.md`, `census/round-38/preregistration.txt` ×2,
`SCORECARD.md`, `LOG.md` ×2, `corpus/QUALITY.md`) and the other two at wave record files, and the
counter never re-derives any value those lines state.

## 3. Control 2 — C2 `pass=6` from a tool that always exits 2

Built `/fast/scratch/hyaku/souji-r39/W1CritSizing/repo-c2`:

- `c0 = fde4f821b457345a13c9e8ddc0ab20e08a2ac816` — base bytes of both tools, `corpus/SOURCES.md`,
  `census/round-38/cells.tsv`.
- `c1 = fd0d3d3519560f3462580a40f354b52fdd836739` — `tools/souji-worktree-drift.py` from `2201778`,
  `tools/souji-citation-reconcile.py` replaced by a 4-line stub that writes
  `REFUSAL REV-UNRESOLVED: always-2 stub` to stderr and `sys.exit(2)` unconditionally.
- The six fixture files the counter reads from the worktree were copied from `2201778`.

```
$ python3 -B $L/census/round-39/c2-counter.py --root $S/repo-c2 --rev fd0d3d3519560f3462580a40f354b52fdd836739 \
    --base-rev fde4f821b457345a13c9e8ddc0ab20e08a2ac816 --scratch $S/tmp
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
LEG L6 FAIL r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=0/16(base 16/16) r38-citation-commit=0/14(base 14/14)
SUMMARY legs=6 pass=4 fail=2 harm=2 tool_sha=098da5b2054e/e48ed08e6728 fixture_sha=7ab7c3d85a81
rc= 1
```

**Verdict C2: PASS on the stated attack.** An always-exit-2 tool reaches `pass=4 fail=2 harm=2`,
not `pass=6`; L1/L2/L3 are individually trivial for it, but L5 (the 8-case fixture needs positive
cases) and L6 (the r37/r38 citation consumers need the success path) carry the discrimination and
record `harm=2`. The after-state is not reachable by the cheapest skip.

## 4. Control 3 — C3 `killed=4` from fixtures that always fail

Control 3a, unconditional always-fail fixture
(`$S/c3/alwaysfail.py`, sha256 `8d5b64fb7436…`; prints `SUMMARY cases=6 pass=5 fail=1`, exit 1):

```
$ python3 -B $L/census/round-39/c3-counter.py --root $L --rev 2201778e... --base-rev ed30b7f... \
    --fixture $S/c3/alwaysfail.py --base-fixture $L/tests/fixtures/r38-drift-record.py --scratch $S/tmp
SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=6
rc= 1
```

Blocked by the pristine arm — correct.

Control 3b, byte-identity fixture (`$S/c3/shafail.py`, sha256 `a18aeb6b2e3c…`; green iff
`sha256(--tool bytes) == e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`, the
audited tool's sha256, else `SUMMARY cases=6 pass=0 fail=6` + exit 1 — it asserts **none** of the
four record-file behaviours, only that the file changed):

```
$ python3 -B $L/census/round-39/c3-counter.py --root $L --rev 2201778e... --base-rev ed30b7f... \
    --fixture $S/c3/shafail.py --base-fixture $L/tests/fixtures/r38-drift-record.py --scratch $S/tmp
MUTANT M11 killed=yes base_killed=no rc=1 fails=6 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=6 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=6 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=6 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=6
rc= 0
```

**Verdict C3: FAIL §9.** `killed=4` is reachable by a fixture whose kill criterion is "the tool
bytes differ", so the frozen predicate does not force the claimed coverage surface (the four record
rules). The landed `tests/fixtures/r39-drift-record-rules.py` *is* behavioural (it builds synthetic
fleets and asserts rc/tokens per case; 7 cases), so the claim is true in fact — but the sizing does
not make it true by construction.

## 5. Additional sizing defects found while testing

**D1 — C1's register artifact has no committed producer, and the only producer emits a register the
frozen reconciler rejects.** `census/round-39/cells.tsv` is absent at `2201778` (`git ls-files
census/round-39/cells.tsv` → 0 rows), so `register_cells>=6` is unreachable at the tip. The
untracked `census/round-39/make-cells.py` emits anchored lines that carry their own `stale` token
(`... the stale reading \`legs=2\` belongs to the pre-repair bytes.`), and the frozen reconciler
refuses exactly that (`tools/souji-citation-reconcile.py`, `STALE-PRESENT` arm). Executed on a
scratch repo built from the generator's own row/line format:

```
$ python3 -B $L/tools/souji-citation-reconcile.py --root $S/repo-c1b --rev 34b93b30dcfcb607682efb20c813f13fad11e9c3 \
    --register census/round-39/cells.tsv --register-rev 34b93b30dcfcb607682efb20c813f13fad11e9c3
MISMATCH REG-01 STALE-PRESENT SCORECARD.md stale='legs=2'
MISMATCH REG-02 STALE-PRESENT SCORECARD.md stale='harm=3'
MISMATCH REG-03 STALE-PRESENT SCORECARD.md stale='fail=4'
MISMATCH REG-04 STALE-PRESENT LOG.md stale='killed=1'
MISMATCH REG-05 STALE-PRESENT LOG.md stale='cases=9'
MISMATCH REG-06 STALE-PRESENT corpus/QUALITY.md stale='open=1'
SUMMARY cells=6 mismatches=6
rc= 1
```

The same register through the C1 counter reads `REGISTER cells=6 mismatches=6 ... rc=1`. The
generator was run only to stdout (`make-cells.py --commit 2201778... --late ed30b7f... --freeze
ed30b7f...`, no `--write`), so no lane file was touched.

**D2 — C2's frozen sentence says six consumer fixtures; the counter enumerates five.**
`census/round-39/preregistration.txt:62` — "L6 six consumer fixtures stay green."
`census/round-39/c2-counter.py:19` — "L6 five consumer fixtures stay green"; `CONSUMERS`
(`c2-counter.py:54-59`) has five entries and the SUMMARY's L6 detail prints five. §9 requires the
counting command to enumerate the full set of a numeric/universal clause; here it does not.

**D3 — C3's base fixture is claimed "at `--rev`" but read from the worktree.**
`preregistration.txt:85` — "the base fixture is `tests/fixtures/r38-drift-record.py` at `--rev`";
`c3-counter.py:123-124` — `candidate_src = open(args.fixture, ...)`, `base_src =
open(args.base_fixture, ...)`; the tool bytes come from `git show --rev` but both fixtures are
mutable worktree files. The same is true of the C1 items file (read by path, not at `--rev`) and of
C2's L5/L6 fixtures (disclosed in `c2-counter.py`'s `lane_root_of` docstring). Live divergence for
C3: the frozen command with `--rev ed30b7f --base-rev ed30b7f` prints
`SUMMARY ... killed=4 ... cases=7` today, while the committed before receipt
(`census/round-39/records/c3-before.txt`) prints `killed=0 survived=4 ... cases=10
fixture_sha=ac0be0e7a49e` (that digest is `tests/fixtures/r38-drift-record.py`, i.e. the control ran
the base fixture in the candidate slot). The before-state is therefore not re-derivable from the
landed bytes — a direct violation of "one command over committed bytes". The same gap is live in
C2: `c2-counter.py` hashes and runs `tests/fixtures/r39-citation-rev.py` from the worktree, so my
`--rev 2201778` run read fixture sha `7ab7c3d85a81` while my later `--rev ed30b7f` run read
`e555d8281484` — the fixture changed under the counter when `d4c1755` rewrote three of its lines,
with no `--rev` change on my side.

**D4 — the C3 counter is not the freeze commit's counter.** `git diff b769bfb HEAD --
census/round-39/c3-counter.py` changes only `child_env`/TMPDIR plumbing (`d4c1755`), no scoring
logic; C1/C2 counters and `c1-items.tsv` are byte-unchanged since the freeze. The scoring predicate
is unchanged, but the receipt's `fixture_sha` and the "same counter bytes" provenance are weaker
than the frozen text implies.

**D5 — the frozen control receipts were rewritten after the freeze (`f8ba3f3`, 15:16:01).**
`git diff b769bfb f8ba3f3 -- census/round-39/records/` shows `c1-before.txt` +3, `c2-before.txt`
+8/-2, `c3-before.txt` +4, and a new `prereg-prefix.txt`. The C2 receipt's measured detail changed
after the freeze:

```
-LEG L5 FAIL new=(8, 5, 3, 1) old=(8, 5, 3, 1)
+LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
-SUMMARY ... fixture_sha=c142c1bc28b8
+SUMMARY ... fixture_sha=e555d8281484
```

The commit message is honest ("controls re-measured on final instruments"), and the SUMMARY targets
did not move (`pass=2 fail=4 harm=0` before and after; C1/C3 values unchanged), but the prereg says
these receipts are "committed before any after-data". These bytes are not: the freeze commit
`b769bfb` holds different receipt bytes, and the C2 fixture digest now names the post-data fixture.
The L1 should record this as a control-provenance note (or restore the freeze-commit receipts and
put the re-measurement in a separate after receipt); it must not be presented as the pre-data
control unchanged. This is the R8/R9 class the round's C1 exists to police.

## 6. Smallest safe corrections (advisory; the L1 integrates)

- **C1** (must, before landing): (a) replace the item arm's token-presence assertion with a mismatch
  arm — add a per-row `derive` token/command whose value the counter re-derives from committed bytes
  at `--rev` (e.g. `SOURCES-rows=170` against the `corpus/SOURCES.md` row count; `open=16` against
  `records/c1-before.txt`'s SUMMARY; `killed=4`/`cases=7` against the C3 counter's SUMMARY;
  `measured-revision=fcdecaa` against a resolving ancestor) and keep the row OPEN when the stated
  value disagrees; a prose rewrite then fails because the probes still report the defective state.
  (b) land `census/round-39/cells.tsv` and drop the `stale` clause from `make-cells.py`'s `LINE`
  (D1), otherwise `register_mismatches=0` is unreachable with the lane's own generator.
- **C2** (minor): make the sentence and the counter the same set — either change `preregistration.txt:62`
  to "five" or add the sixth consumer (`tests/fixtures/r38-drift-mutants.py` is already in the tree)
  to `CONSUMERS`. Adding is tighter and safe. No change is needed for the always-exit-2 attack.
- **C3** (must): add a semantics-preserving no-op mutant (comment insertion / local rename) that the
  candidate fixture must leave **alive** and print `survived>=1`; a byte-identity fixture then fails
  the arm (control 3b). Also pin the base fixture with `git show --base-rev` so the before receipt is
  re-derivable (D3), and either re-run and re-commit the C3 before receipt with the landed counter or
  label it non-reproducible.

## 7. Verdict

| Check | Verdict |
|---|---|
| C1 after-state is one concrete value, one command | PASS (value and command are single and exact) |
| C1 do-nothing control cannot reach it | **FAIL** — 16 prose lines + 6 synthetic receipts on base bytes reach `items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=6`, rc 0 |
| C2 after-state is one concrete value, one command | PASS |
| C2 `pass=6` from an always-exit-2 tool | PASS — reaches only `pass=4 fail=2 harm=2` (L5, L6 block) |
| C2 numeric/universal clause enumerated | **FAIL** — "six consumer fixtures" vs five in `CONSUMERS` (D2) |
| C3 after-state is one concrete value, one command | PASS |
| C3 `killed=4` from a fixture that always fails | **PARTIAL/FAIL** — unconditional always-fail is blocked (`pristine=FAIL`); byte-identity fixture reaches `killed=4 survived=0 pristine=ok base_killed=0 cases=6`, rc 0 |
| C3 before receipt re-derivable from committed bytes | **FAIL** — worktree-read base fixture; same frozen command now prints `killed=4` vs receipt `killed=0` (D3) |
| C1 register reachable with the lane's own producer | **FAIL** — `cells.tsv` absent; `make-cells.py` output yields `mismatches=6` (D1) |
| Frozen control receipts are the freeze-commit bytes | **FAIL** — `f8ba3f3` rewrote `c1/c2/c3-before.txt` after the freeze, including C2's `fixture_sha` and L5 detail (D5) |

Impacted axes: calibration (C1 — the claim is an assertion, the §9 class it exists to police), and
coverage (C3 — `killed=4` does not force the named surface). Operability (C2) is sized correctly for
the stated attack; only its consumer count is mis-stated.

Scratch left on disk: `/fast/scratch/hyaku/souji-r39/W1CritSizing` (`repo-c1`, `repo-c1b`,
`repo-c2`, `c3/`, `tmp/`); 2.1 MB. No lane file, no fleet file, no `~/.omp`/`~/.config` file was
written; every scratch git repo asserted `rev-parse --show-toplevel` == its own directory before
the first commit.
