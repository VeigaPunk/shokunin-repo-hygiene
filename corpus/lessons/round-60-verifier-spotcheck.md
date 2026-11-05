# Round 60 verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

## Scope and decision

Reviewed base `1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4` → final round tip
`d05a00019835dee5b9bb8fe738add080434c4d67`. Status **ok** (real, committed, lane-authored report),
**admitted=false**, **rejected-harmed**.

Both claims' before→after values re-derive from committed bytes and both beat their do-nothing
controls, so the numeric claims are not the rejection ground. The rejection ground is chronology:
the two bound `Control:` receipts that the frozen preregistration and the report say were committed
"strictly before" the freeze are added **by the freeze commit itself** (`2670e96a`), and the wave
control outputs land after it (`b38c60ee`). The lane's own critic recorded exactly this as
`S60CriticRound` Finding 1 (Q120 VIOLATES) and recommended honest-stop framing; the report and the
lesson surface five other critic limits and not this one, and the report's discernment verdict
asserts "red controls committed before the predicate" — a statement the commit graph contradicts.
Under `AXES.md` calibration ("self-assessment quality … overreach caught"; "SCORECARD entries match
observed repo state") that is a harm, so the round is rejected as harmed rather than as an honest
stop: nothing in the filed record stops honestly on this point.

No lane gate or selftest was executed by closure. All claim evidence below is either re-measured
from committed bytes by plain grep/awk/git/wc over `git show` output, or verified as committed
evidence (receipt text, selftest tallies, frozen-run verdict, revision measured).

## Step-1 conformance

- **Report attribution.** `git log --format='%an <%ae> %H' -- .ufo/reports/round-60/souji.md` →
  `souji-shokunin <souji@shokunin.local> 92b357dced7adcc909009b1e56bd9de48196c1de`. Lane identity,
  pathspec-limited to the report path (1 file, 175 insertions).
- **Landed last.** Report committer time `2026-11-04T21:17:34-03:00` follows the lane tip's
  committer time `2026-11-04T21:17:26-03:00` (`git log -1 --format='author=%ai committer=%ci'` on
  `d05a0001`). Observation, not a defect: the report's *author* date is `21:13:07`, earlier than the
  tip it cites — the fleet repo is jj-colocated (`/home/vgpnk/Projects/shokunin/.jj`), and jj
  preserves the working-copy author date while the committer date is set at commit, so ordering is
  correctly read from committer dates plus content.
- **`SHONEN` heading.** `grep -n '^## SHONEN'` → line 139, exactly one heading; `SHONEN.md` carries
  4 boxes (`grep -c '^- \[' SHONEN.md` → 4) and the report carries 4 mark lines, all `[~]` with
  pointers, zero `[x]`. `SHONEN.md` is unchanged from base.
- **Cited commits.** Every hash in the report (`3b552509`, `2670e96a`, `b38c60ee`, `e51dc9d8`,
  `2ec7f460`, `d05a0001`, plus the four rejected-closure hashes `8c27791a`, `dcbcd05c`, `87430107`,
  `24a07fd8`) returns `commit` from `git cat-file -t` and `0` from
  `git merge-base --is-ancestor <hash> refs/heads/master` (never `@{u}`).
- **Pushed and clean.** `jj-lane.sh state` → `branch=master local=d05a0001… remote=d05a0001…
  ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` prints nothing;
  `git ls-remote origin refs/heads/master` → `d05a00019835dee5b9bb8fe738add080434c4d67`.
- **Prompt fidelity.** `.ufo/prompts/souji-round-60.md` carries all five round-level items
  (mission/axes binding L3–7, L2 ≥8 in one batched swarm L80–84, commit-then-push L133, push scope
  L135–137, L0 side channel L138–140) and all five child-lane items (report path L101,
  commit-before-report L133–134, `SHONEN` L118–119, commit-hash citation L107–108, write scope
  L135–137 and L448–453). An independent seat diffed §1–§5 against `templates/round-prompt.md`
  after `{{LANE}}/{{ROUND}}/{{FLEET_ROOT}}/{{AXES}}` instantiation: empty diff. The addendum's run-15
  route map quotes host aliases (`@m_zfl`/`@m_flash`/…), a different vocabulary from `MISSION.md`'s
  advisory buckets; `MISSION.md` itself declares the bucket grouping advisory and the host route
  table authoritative, so no breach.
- **Frontier step.** Census before/after both EXIT 0, registry rows 211 → 213 (re-measured:
  `git show 1e8bfd8:corpus/SOURCES.md | grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}'` → 211;
  working tree → 213). Round lesson carries `## Gate`, `## Mistakes` (4 rows) and `## Named limits`.
- **Wave.** `census/round-60/wave/w1-results.json` `seats=14`, 14 results, roles executor 5, scout 2,
  reviewer 2, scribe 1, critic 1, mutation-tester 1, sentinel 1, connector 1 → attack share 4/14
  (28.6 %), connector 1, band 8–16, L2 floor met. `sha256sum -c census/round-60/wave-SHA256SUMS` from
  `census/round-60/wave/` → 365/365 OK, 0 failures. Two seats returned 132 and 229 bytes of output
  (`S60ScoutSources`, `S60SentinelRound`), matching the report's own admission that they ended
  mid-narration; their work is not counted as evidence and the report says so.
- **Census.** `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → EXIT 0,
  67 `W04` duplicate-URL warnings, final line `souji ok …/corpus/SOURCES.md`.
- **Driver digest.** `2026-11-04T20:36:11-03:00 launch souji round=60 pgid=1040036 driver=hyaku-inline
  attempt=1`; `2026-11-04T21:18:10-03:00 complete souji round=60; hyaku-inline attempt=1`.

## Claim re-check — C1 calibration (capability acquisition)

**Re-measured from committed bytes (closure's own; no lane instrument executed).**

```sh
git show 1e8bfd8:tools/souji-freeze-check.py | grep -cE 'CONTROL-(INSTRUMENT|REV|COMMAND)'   # 0
git show 2670e96a:tools/souji-freeze-check.py | grep -cE 'CONTROL-(INSTRUMENT|REV|COMMAND)'   # 26
git show 1e8bfd8:tools/souji-freeze-check.py | grep -c 'substance'                            # 0
git show 2670e96a:tools/souji-freeze-check.py | grep -c 'substance'                           # 46
awk -F'\t' 'NR>1&&$2=="accept"' census/round-60/c1-matrix.tsv | wc -l                         # 3
awk -F'\t' 'NR>1&&$2=="refuse"' census/round-60/c1-matrix.tsv | wc -l                         # 5
git diff --stat 1e8bfd8 2670e96a -- tools/souji-freeze-check.py                               # 160+/15-, 415->560 lines
```

**Committed evidence verified (not executed).**

- `census/round-60/controls/c1-do-nothing.txt`: `SUMMARY matrix=8 forgeries_accepted=5
  honest_accepted=3 new_forgeries=5 new_honest=3 stubs=REJECTED`, `EXIT=1`; per-case lines show the
  base tool accepting all five forgery rows and the three honest rows.
- `census/round-60/records/c1-after.txt`: same matrix, `new_forgeries=0 new_honest=3
  stubs=REJECTED`, `EXIT=0`; all five forgery rows `new=refuse`, all three honest rows `new=accept`.
- The two control and after totals reconcile with the matrix: 3 accept-expect + 5 refuse-expect = 8
  cases; `new_forgeries` 5 → 0 is exactly the five refuse-expect rows.
- Bindings: both receipts carry `instrument=`, `instrument_sha256=`, a full-40 `rev=3b552509…` and a
  `command=` naming the counter as an argv token. `git show 3b55250:census/round-60/c1-counter.py |
  sha256sum` → `76f35c2f…106d9b`, matching both receipts; `git merge-base --is-ancestor 3b55250
  2670e96a` → 0.
- Population digests: `git show 2670e96a:census/round-60/c1-matrix.tsv | sha256sum` →
  `7973d520…0132d` and `…/c2-cases.tsv` → `727c5d71…2c7`, exactly the values the prereg pins.
- Default-path byte identity: `census/round-60/wave/w1/S60ExecFreezeArm/byte-identical.txt` records
  `cmp stdout: IDENTICAL` / `cmp stderr: IDENTICAL` for the selftest and three real preregistrations
  (r57/r58/r59), base exit 1,1,1 = candidate exit 1,1,1. Selftest tallies `cases=41 pass=41`
  (default) and `cases=12 pass=12` (`--substance`) committed under the same wave seat.
- The round's own freeze record under the arm it lands is committed as evidence:
  `census/round-60/wave/w1/S60CriticRound/evidence/frozen-state.txt` → `SUMMARY claims=2 findings=0`,
  `EXIT=0` (twice, base checker and `--substance`).

**Verdict: the declared capability and its numbers verify.** What does not verify is the
preregistration's provenance sentence (below).

## Claim re-check — C2 operability

**Re-measured from committed bytes.**

```sh
git show 1e8bfd8:census/round-57/record-receipt.sh | wc -l          # 35 (base recorder, unchanged since r57)
git show 1e8bfd8:census/round-57/record-receipt.sh | grep -cE 'link|fsync'   # 0
git show 2670e96a:tools/souji-receipt-write.py | wc -l             # 694
git show 2670e96a:tools/souji-receipt-write.py | grep -cE 'os\.link|fsync'   # 5
awk -F'\t' 'NR>1&&$2=="accept"' census/round-60/c2-cases.tsv | wc -l   # 2
awk -F'\t' 'NR>1&&$2=="refuse"' census/round-60/c2-cases.tsv | wc -l   # 6
```

**Committed evidence verified.**

- `census/round-60/controls/c2-do-nothing.txt`: `SUMMARY cases=8 pass=4 fail=4
  control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, `EXIT=1`, with the four base passes
  (`atomic-in-flight`, `kill-residue`, `rev-short`, `instrument-absent`) and four base failures.
- `census/round-60/records/c2-after.txt`: `pass=8 fail=0`, same two control rejections, `EXIT=0`.
- The case table has 8 rows (2 accept-expect, 6 refuse-expect) and the fixture's two stubs are both
  rejected, so a do-nothing round cannot pass.
- Writer selftest `cases=12 pass=12` committed at `census/round-60/wave/w1/S60ExecRecorder/selftest.txt`.
- The fixture digest in both receipts (`d5291501…4114`) matches
  `git show 3b55250:tests/fixtures/r60-receipt-write.py | sha256sum`.

**Verdict: the writer's eight refusals verify and the numbers reconcile.** Two limits are named by
the lane and hold: the fixture observes atomicity indirectly (in-flight absence, kill residue), and
the dirty-tree guard is `git status --porcelain` (ignored files do not dirty the tree).

## The rejection ground — control chronology (Q120)

The frozen `census/round-60/preregistration.txt` opens:

> Controls were executed and committed at `3b5525099356e15ff9d17b7fbd2835c2d3512eee`, strictly
> before this freeze commit; both are red there (EXIT=1) and both are written in the bound shape the
> C1 arm requires.

The commit graph contradicts the "committed at 3b552509" clause:

```sh
git cat-file -e 3b55250:census/round-60/controls/c1-do-nothing.txt    # fatal: … not in 3b552509…
git ls-tree -r --name-only 3b55250 census/round-60 | grep controls    # (no output)
git log --format='%h %s' --diff-filter=A -- census/round-60/controls/ # 2670e96a round-60: freeze the two claim predicates…
git log --format='%h %ad %s' --date=iso --diff-filter=A -- \
  census/round-60/wave/w1/S60ExecControls/do-nothing-c1.txt           # b38c60ee (21:10:52, after the freeze)
```

`3b552509` carries the instruments, the counter, the 8-case matrix with its `expected.txt` files,
the fixture, SOURCES, the knowledge entry and the lesson skeleton — no executed control output.
The bound receipts are added by the freeze commit itself; the wave control outputs land later still.
The receipts' `rev=3b552509…` is the revision they were *measured at* (a strict ancestor), not the
commit that adds them, and the `--substance` arm validates the `rev=` line and never asks which
commit added the receipt — so the arm cannot catch this and scores the record `findings=0`.

`QUALITY.md` Q120 requires the executed controls "in a commit strictly preceding predicate freeze"
and states that "a later replay never repairs the chronology". The round's own critic reached the
same verdict (`S60CriticRound` Finding 1) and recommended landing the report as an honest stop naming
`2670e96a`. The filed report instead asserts the opposite twice: "Both claims were frozen only after
their no-work controls were executed and committed" (Work performed, opening) and "red controls
committed before the predicate" (Trend verdicts, discernment). Five other critic findings (matrix
class not pinned, tag substitution for `rev-at-freeze`, indirect atomicity, bytes-not-execution,
dirty-tree vacuity) *are* named as limits in the lesson; Finding 1 is not.

The predecessor precedent is exact: r58 was rejected with "C2 pre-freeze committed control
prerequisite not met" because the lane disclosed the ordering itself; this round repeats the same
prerequisite failure with the opposite disclosure.

## Axis verdicts and no-harm check

| Owned axis | Verdict | Evidence |
|---|---|---|
| calibration | harmed | C1's instrument and numbers verify, but the round's self-assessment asserts a control chronology the commit graph contradicts (`preregistration.txt` header; report Work performed and Trend verdicts) and leaves its own critic's rejection-ground finding unsurfaced. `AXES.md` calibration is self-assessment quality with overreach caught; r57's "instruments verify but overstate their reach" harm is the same shape |
| operability | unprovable | C2's numbers verify (4/8 → 8/8, two stubs rejected, writer 12/12) but C2 is a declared successor to the rejected r57 C2 whose Q120 prefreeze prerequisite is unmet, so the claim cannot be admitted as a successor; the r58 precedent grades this axis `unprovable` |
| coverage | unchanged | no coverage claim; `PROVINCE.md` unchanged from base; no Core promotion, no package adoption |

**No structural harm.** `git diff --name-status --diff-filter=DM 1e8bfd8 d05a0001` → empty (no
pre-existing file deleted or modified beyond `LOG.md`, `SCORECARD.md`, `SKILL.md`,
`corpus/SOURCES.md`, `tools/souji-freeze-check.py`, all additive or in-place tool extension).
`git diff … -- SCORECARD.md` is append-only (Round 60 measurements, capability rows, Planned r61) with
calibration 7 / operability 8 / coverage 8 numerically unchanged. `PROVINCE.md` and `SHONEN.md`
unchanged. `LOG.md` and `corpus/SOURCES.md` are append-only (0 removed lines; SOURCES +4 lines = two
rows plus one provenance line, with S110/S213/S214/S251 byte-identical to base). The default freeze
checker path is byte-identical to base over four runs, so the pre-existing gate is not regressed.

## Discernment spot-check

Re-opened `https://docs.python.org/3/library/os.html#os.replace` on 2026-11-04 (`curl -sSL`,
`HTTP=200 BYTES=791358`, matching the committed capture `census/round-60/sources/s288-python-os-replace.html`
byte-length; the capture hashes to the recorded `ece1ab71…8079` — the live page differs by two bytes
in its "Last updated on … (23:57 UTC)" footer). Quotes were checked in the tag-stripped text, where
the page's line wrapping splits them.

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S288 `os.replace` atomic publication admissible | admit | `docs.python.org/3/library/os.html#os.replace`, anchor `id="os.replace"` | **agree** | 14-word quote present verbatim after unwrapping ("If successful, the renaming will be an atomic operation (this is a POSIX requirement)."); official stdlib docs are tier A for the primitive, and the row's scope is the primitive the writer publishes with, not the writer's own atomicity |
| S289 cross-filesystem rename inference rejected | reject | same page, same anchor | **agree** | 16-word quote present verbatim after unwrapping ("The operation may fail on some Unix flavors if src and dst are on different filesystems."); the rejected item is the inference that a `$TMPDIR` temp can be renamed onto a receipt on another device, and the flip ("place the temp beside the output") is the correct repair. The document is kept, the inference is rejected — the right shape |

Both quotes are ≤25 words and ground their scoped `teaches` cells; the new rows are additive (S288
mined, S289 rejected, both tier A, no old cell rewritten). Required census executed here: EXIT 0,
registry rows 211 → 213, 67 `W04` duplicate-URL warnings (`S289` shares the S288 URL by design).

## Learning trends

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | unchanged | `corpus/knowledge/` 41 → 42 files (`git ls-tree -r --name-only … corpus/knowledge \| wc -l`) and the new entry cites the mined `S288`, but `corpus/README.md` was **not** updated (`git diff --stat 1e8bfd8 d05a0001 -- corpus/README.md` empty; `grep -c freeze-record-substance-binding corpus/README.md` → 0) while every other recent entry is indexed, so no coverage-map row holds the ground and LEARNING's expansion criterion is not met; no province move, no Core promotion, no package adoption |
| quality | improved | the weaker label-only freeze grammar is superseded by a substance arm that refuses five forgery states it accepted at base (5 → 0 on frozen bytes), and the r57 recorder's 4/8 is superseded by a writer at 8/8; four held rows re-verified with cells left byte-identical; no admitted entry found false |
| discernment | improved | this outside spot-check agrees with both gate decisions (S288 admit, S289 reject); the round also took its C2 base from the instrument (4/8) against the prompt's 3/8. Caveat recorded, not a trend reversal: the critic's Finding 1 is left unlearned, which is charged to calibration above |

## Routed defects — souji next round

1. **Q120 chronology (blocking for these claims).** Do not re-freeze or edit `preregistration.txt`
   (pushed bytes). Append an erratum to the next round's report naming `2670e96a` as the commit that
   adds both `Control:` receipts, and correct the "committed at 3b552509" provenance. Any successor
   claim must commit its executed controls strictly before its freeze commit.
2. **Mechanise the rule the round is about.** In `--substance`, resolve the commit that *adds* the
   `Control:` receipt (`git log --diff-filter=A -- <receipt>`) and require it to be a strict ancestor
   of the freeze commit; the frozen r60 record would then be red, which is the honest reading.
3. **Surface the critic's surviving finding.** `S60CriticRound` Finding 1 belongs in the round
   lesson's `## Named limits` or `## Mistakes`; five other findings are already there.
4. **Coverage map.** `corpus/README.md` holds no row for `knowledge/freeze-record-substance-binding.md`
   although every other recent entry is indexed and the report says F1 gains it. Index it.
5. **Broken evidence pointer.** `SKILL.md` r60 section cites
   `census/round-60/w1/S60ExecFreezeArm/byte-identical.txt`; the file is at
   `census/round-60/wave/w1/S60ExecFreezeArm/byte-identical.txt`
   (`ls census/round-60/w1/…` → No such file or directory). Correct the path.
6. **Keep open** the r56–r59 debts and this round's own named limits: matrix finding class not
   pinned, `forgery-rev-at-freeze` is a tag rather than a constructible non-ancestor, C2 atomicity
   observed indirectly, Q102 hidden-case audit not run, 5 of 15 mutants surviving, and C2's successor
   framing absent from the frozen prereg.

SHONEN promotion remains operator-owned: the four boxes are lane-asserted `[~]` with pointers, and
closure writes no `[x]`.

Closure self-evaluation: accuracy 4 (committed-byte re-measurement, no sibling gate executed),
completeness 4 (attribution, ancestry, prompt, wave, receipts, sources, trends), clarity 4 (numeric
claims separated from the chronology failure), actionability 4 (six specific routed repairs),
conciseness 4. Highest-impact improvement: the freeze record must be able to see which commit added
its own control receipts. No tools installed or updated.
