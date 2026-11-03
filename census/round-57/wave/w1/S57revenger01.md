# S57revenger01 — r56 routed-defect and named-limit disposition against the r57 freeze

Seat: S57revenger01 (revenger, routed-item disposition). Leaf member: no subagent dispatch, no
background job. Read-only to the lane except this report and my seat directory; no git/jj mutation
outside scratch fixture repos I created myself. Scratch:
`/fast/scratch/hyaku/souji-r57/S57revenger01/` (deleted before yield).

Freeze: `d749f7ee081ec1b382b2f92577eb22bfba1c7761`; base `b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd`.
Lane HEAD at audit time: `805482129d022b13db672654f5478952def607a6` (post-freeze frontier commit
"round-57: sources S279/S280 admitted + S281 rejected…"; its diff touches SKILL.md, corpus/QUALITY.md,
corpus/README.md, corpus/SOURCES.md and a knowledge entry — `git diff --stat d749f7ee -- census/round-57
census/round-56` is empty). Frozen bytes unchanged: all **thirteen** prereg pins re-hash to the
pinned values — the nine r57 instrument/fixture/expected/manifest files, the three source captures,
and `census/round-51/records/ws-drift-vs-r46.tsv` at base (`receipts/pins.txt`).

Inputs read: `census/round-57/preregistration.txt`; `corpus/lessons/round-56-verifier-spotcheck.md`
(Routed defects 1–6, Named limits, Per-claim, Sentinel); `corpus/lessons/round-56.md` (Named limits
carried into r57, second Mistakes table); `SCORECARD.md` `### Planned (r57)`; frozen
`census/round-57/{c1-counter.py,c2-counter.py,record-receipt.sh,fixtures/*,records/*,controls/*}`;
post-freeze records as they appeared during the audit (named where read, never presented as my
re-derivation).

Tooling: `uv venv` + `uv pip install markdown-it-py==4.2.0` (with mdurl 0.1.2) into
`<scratch>/venv` from PyPI, for an independent CommonMark render of the comment shapes. Scratch-only;
deleted with the scratch. No pacman transaction, no host service, no permanent install.

## 1. The two required mechanical receipts

### (a) The round-56 `__pycache__` artifact is absent

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files census/round-56/__pycache__
(no output)
[rc=0]
$ find /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-56/__pycache__
find: ‘…/census/round-56/__pycache__’: No such file or directory
[rc=1]
```

Neither tracked nor present on disk. Receipt: `receipts/a-pycache.txt`.
(Lane-wide `git ls-files | grep -c __pycache__` = 5: four `.ufo/waves/round-26/...` paths and
`census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`. Those are pre-existing, not the
routed artifact; see D5 for a **new** r57 artifact.)

### (b) The recorder refuses a non-full40 revision

```
$ TMPDIR=<scratch> bash census/round-57/record-receipt.sh \
    /home/vgpnk/Projects/shokunin/souji-shokunin HEAD x <scratch>/out -- true
stderr: refused: rev is not full 40-hex (HEAD)
[rc=2]
out-file-exists=no
```

Exactly the required refusal line, exit 2, and no output file written. Receipt:
`receipts/b-recorder-refusal.txt`.

## 2. Additional re-derivations used by the disposition

All run in my scratch; outputs in `receipts/`.

- **Matrix reproduction.** After
  `python3 -B census/round-57/fixtures/build-fixtures.py --work <scratch>/selftest --manifest <scratch>/selftest/fixture-manifest.tsv`
  (36 C1 fixtures, 16 C2 fixtures), `bash census/round-57/fixtures/run-matrix.sh <scratch> <scratch>/matrix`
  produced both TSVs **byte-identical** to `census/round-57/records/matrix-dryrun/` (`cmp -s`, rc 0 both).
  Exit-0 counts: v5 **10/36**, v6 **8/36**. Row-level join on (fixture, exit, findings_all): exactly
  **2** changed rows, `B4-INLINE-NBSP-OPENER` and `C4-INLINE-CLOSED-COMMENT` (0 → 1, two
  `CORRECTION-IN-FENCE`); the other **34** rows identical. (`receipts/c1-matrix.txt`)
- **Selftests.** C1 v6 `SELFTEST pass cases=36` (rc 0), also on a re-run in the same `--work`.
  C2 `SELFTEST pass cases=8` with `control=FALSE-GREEN-REJECTED stub_meets=1 cases=8` (rc 0, fresh
  `--work`). C2 before manifest: `FINDING RECEIPT-REV-MISSING census/round-56/records/landing-suite-final.txt`
  / `SUMMARY receipts=1 findings=1`, rc 1. (`receipts/selftests.txt`)
- **B4/C4 differential with detail.** v5: rc 0 `filed=2 unfiled=0` on both. v6: rc 1 with two
  `FINDING CORRECTION-IN-FENCE … hidden_by=inline`, `unfiled=2 fenced=2`. F29, C6, F17, F18, F19:
  rc 0 under both arms. (`receipts/b4c4-detail.txt`)
- **M1 re-derivation** (scratch copy of v6 with the secondary `PAIR-FILING-HIDDEN` emission removed;
  frozen bytes untouched): first-finding-only comparison → `SELFTEST pass cases=36`, rc 0 (mutant
  survives); all-findings comparison → `SELFTEST fail cases=36`, rc 1 (mutant killed). Reproduces
  `records/m1-red-before.txt`. (`receipts/m1-arms.txt`)
- **Row-set and summary-field gaps.** Appending `GHOST-C1	0	-` to a scratch expected file still
  prints `SELFTEST pass cases=36` (rc 0); appending `GHOST-C2	RECEIPT-REV-MISSING` to a scratch C2
  expected file still prints `SELFTEST pass cases=8` (rc 0) and never mentions the ghost. A C1
  summary-field mutant (`pairhidden += 3`) also passes 36/36 (rc 0). (`receipts/rowset-ghost.txt`)
- **Independent CommonMark renders** (markdown-it-py 4.2.0, strip `<!--…-->`, count `R52-CORRECTION`):
  B4 0 visible / 1 span; C4 0 visible / 1 span; C6 2 visible / 1 span; F29 2 visible / 0 spans;
  **second opener 0 visible / 2 spans**; code-span shape 2 visible / 0 spans; tab-indent shape
  2 visible / 0 spans. (`receipts/renders.txt`)
- **Recorder binding and overwrite** (scratch repo, clean commit R, then dirty working tree):
  recorder rc 0; receipt carries `instrument_sha256=` of the **clean** blob at R and `rev=R`, while
  its captured output shows the **dirty** bytes; the C2 gate scores it `SUMMARY receipts=1 findings=0`,
  rc 0, with `git status` showing `M tools/i.py`. Re-running the recorder on the same `OUT` replaces
  `EXIT=0` with `EXIT=1` silently. (`receipts/dirty-receipt.txt`)
- **C2 selftest idempotence.** A re-run in an existing `--work` exits 1:
  `fixture build failed: ('git','commit','-q','-m','fixture base')` (nothing to commit). Fresh
  `--work` passes. (`receipts/selftests.txt`)
- **New superlinear inline scan.** A fixture with N unclosed `<!--` prose lines (no `-->` anywhere)
  costs, on this host: 5,000 openers → **0.58 s**; 20,000 openers → **8.70 s** (≈14.9× for 4× the
  openers). Each unclosed opener scans to end of document. The L1 independently probed the same
  shape (`census/round-57/records/probe-scale-unclosed.txt`: 0.85 s / 11.17 s, ≈13×). (`receipts/scale.txt`)

## 3. Disposition table — r56 routed defects

Receipt names in the tables are relative to
`.ufo/waves/round-57/w1/S57revenger01/receipts/`.

Verdicts: **CLOSED** = the routed item's requirement is met on committed bytes and observed;
**NARROWED** = partially met, named residual; **OPEN** = no repair; **DROPPED** = not addressed and
not carried.

| id | item (r56 routed) | claim it threatens | what r57 actually did (committed path / command) | verdict | evidence |
|---|---|---|---|---|---|
| R1 | Standing-suite receipts name no measured revision (Q109) | C2 operability 8; every receipt-based claim | Committed `census/round-57/c2-counter.py` (pin `174d7b8a…`) refuses `RECEIPT-REV-MISSING/SHORT/NOT-FULL40/ABSENT/KEEP-ONLY`, missing `EXIT=`, and an `instrument_sha256=` that differs from the committed blob at the named rev; `record-receipt.sh` (pin `84148011…`) writes `instrument=`, `instrument_sha256=`, `rev=<full40>`, `EXIT=`. Observed: before manifest exit 1 with exactly the r56 finding; recorder refuses `HEAD` (rc 2); post-freeze `c2-before.txt` binds `rev=d749f7ee…`, `c1-tip.txt` binds `rev=d749f7ee…`. | **NARROWED** | `receipts/b-recorder-refusal.txt`, `dirty-receipt.txt`; `census/round-57/records/{c2-before,c1-tip}.txt`; `manifests/before.tsv` |
| R2 | Wave composition: 2 executors vs §3 minimum 3; planner exception must be explicit | §3 conformance of the wave | `.ufo/waves/round-57/w1-spec.json`: **12** items, `executor01/02/03` (3), **no planner**; context states "the canonical planner seat is held by the L1, SoujiR57; the wave validator refuses `planner`". `w1-dispatch.json` `counts.spawn=12`; registry roles = scout 1, connector 1, executor 3, scribe 1, reviewer 2, critic 1, mutation-tester 1, sentinel 1, revenger 1. | **CLOSED** | `.ufo/waves/round-57/{w1-spec.json,w1-dispatch.json,w1/swarm-registry.json}` (live, uncommitted at observation); prereg `## Wave plan` |
| R3 | Ignored `census/round-56/__pycache__/c1-counter.cpython-314.pyc` left behind | "all scratch removed" claim; `.pyc` class | Named artifact removed (receipt (a)); every r57 command in the prereg and `run-matrix.sh` uses `python3 -B`. | **CLOSED** (named artifact) | `receipts/a-pycache.txt`; `fixtures/run-matrix.sh` |
| R4 | C1 B4/C4 hidden-filing over-acceptance (the r56 harm) | C1 calibration; no-harm admission | v6 adds the `inline` class to `hidden_lines` (`c1-counter.py:235-333`); B4/C4/C6 fixtures committed in `fixtures/build-fixtures.py` and `records/c1-selftest-expected.tsv`; observed v5 0 → v6 1 with two `hidden_by=inline`; F29/C6/F17/F18/F19 0 under both; renders hide B4/C4 and show F29/C6. | **CLOSED** (named shapes) | `receipts/b4c4-detail.txt`, `renders.txt`, `c1-matrix.txt` |
| R5 | Selftest kill-power: M1/M7 survive first-finding-only; C2 N3 row-set guard; "assert all findings/summary fields" | C1/C2 kill claims | v6 selftest asserts rc **and the full ordered finding list**; M1 re-derived killed. C2 selftest asserts the full finding list per case. | **NARROWED** | `receipts/m1-arms.txt`, `rowset-ghost.txt`, `selftests.txt` |
| R6 | Sentinel MEDIUM/LOW: quadratic correction-line work; raw terminal control bytes; scratch symlinks; 50 MB memory; `.pyc` without `-B` (F1–F6) | operability 8; sentinel findings | No code-side repair in the freeze: `corr.count('\n', 0, m.start())` per correction remains at `c1-counter.py:420,424` (F1); no escaping of repo-derived strings (F2); no symlink refusal in the C1 builder (F3/F4); no input-size gate (F6); `-B` is command-level only (F5). C2 adds `RECEIPT-SYMLINK` for receipt paths only. | **OPEN** | source lines; `receipts/` (no r57 sentinel report at observation); SCORECARD planned bullet P4 unmet |

Residual detail for the NARROWED/OPEN rows is in §6.

### 3a. The six sentinel findings behind R6, one verdict each

Source: `census/round-56/wave/w1/S56sentinel01/` (F1–F6). None of these is repaired in the r57
freeze; the r57 code paths are the same lines the r56 report cited.

| id | r56 finding | r57 state (observed) | verdict |
|---|---|---|---|
| F1 (MEDIUM) | Unbounded quadratic CPU on committed correction lines | `corr.count('\n', 0, m.start())` still runs per correction (`c1-counter.py:420,424`); **and v6 adds a new superlinear path** — every unclosed inline opener scans to end of document (5k → 0.58 s, 20k → 8.70 s; D7); no benchmark re-run of the r56 shape by me | **OPEN** (worse on a new shape) |
| F2 (MEDIUM) | Committed text printed verbatim: terminal control-sequence injection (C1 and C2) | No escaping/`repr` added anywhere in either counter; finding details still interpolate repo-derived strings | **OPEN** |
| F3 (LOW) | Symlinked `<work>/c1-fixtures` can create a `.git` skeleton outside `--work` | Builder keeps only the toplevel assertion (`build-fixtures.py:273-275`); no `is_symlink` refusal; not re-run by me | **OPEN** |
| F4 (LOW) | A symlinked `--work` falsely fails the honest selftest | Same code path; unchanged | **OPEN** |
| F5 (LOW) | `.pyc` written outside `--work` when `-B` is omitted | Every r57 prereg command and `run-matrix.sh` uses `python3 -B`; the r56 artifact is gone (R3), but a new r57 artifact exists (D5) | **NARROWED** |
| F6 (LOW) | No input-size gate; memory amplification 6× (C1) / 22.6× (C2) | Whole-blob reads and `split` unchanged; no size gate | **OPEN** |

The r56 report's A17 (unhandled git timeout/absence, INFERENCE) and A18 (two `git show` per flagged
pair line) are also unchanged; they were not in the routed defect-6 list.

## 4. Disposition table — r56 named limits carried into r57

| id | named limit (r56) | what r57 did | verdict | evidence |
|---|---|---|---|---|
| L1 | Counters read two annotation sites; pair annotations only in `LOG.md` / `corpus/README.md` | Unchanged: `SITES = ['SCORECARD.md','census/round-51/preregistration.txt']`, `PAIR_SITES = ['LOG.md','corpus/README.md']` | **OPEN** | `c1-counter.py:193-201` |
| L2 | HTML comment rule is line-level; CommonMark HTML block types other than 2 not modelled | v6 adds inline comment spans (multi-line, first `-->`), but still models only block type 2 plus inline comments; no `<script>/<pre>/<style>/<div>/<table>` handling | **NARROWED** | `hidden_lines` docstring; grep finds no other block type |
| L3 | Fence closers rstripped, so exotic separators still close a fence | Unchanged: `body = ln.rstrip().rstrip(' ')` | **OPEN** | `c1-counter.py:281` |
| L4 | A visible correction in a prose paragraph is judged by line only | Unchanged: `is_filed = bool(corr_nos) and all(n not in hidden …)` | **OPEN** | `c1-counter.py:596-599` |
| L5 | F27 pins the finding name, not a silent pass; no silent shape beyond F28 | Unchanged; F27 expected row is still `DELETIONS-UNREADABLE-BINARY` | **OPEN** (carry-over by design) | expected TSV; numstat branch |
| L6 | Receipt grammar reports only the FIRST unknown key | r56 `census/round-56/c2-counter.py` untouched (last touch `cce21b55`); r57's C2 is a different gate, not that grammar | **OPEN** | `git log -- census/round-56/c2-counter.py` |
| L7 | Numstat parse is LF-only | Unchanged: `p.stdout.decode(...).split('\n')` | **OPEN** | `c1-counter.py:364-384` |

## 5. Disposition table — r56 second Mistakes table and r57 planned bullets

| id | item | what r57 did | verdict | evidence |
|---|---|---|---|---|
| X1 | Block-start condition mistaken for complete visibility semantics | v6 inline class; B4/C4 refused, F29/C6 visible; independent render agrees on all four | **CLOSED** | `receipts/b4c4-detail.txt`, `renders.txt` |
| X2 | Measurement receipt overwritten after landing | Recorder writes `> "$OUT"` (a second run silently replaced `EXIT=0` with `EXIT=1`); no dirty-tree binding (green receipt from a dirty tree demonstrated) | **OPEN** | `receipts/dirty-receipt.txt`; `record-receipt.sh` line 30 |
| X3 | Context forbade all git mutation while seats build fixtures | r57 dispatch context authorizes scratch fixture repos (`mktemp -d`, `git -C "$D"`) and keeps lane/fleet/sibling mutations forbidden | **CLOSED** | `.ufo/waves/round-57/w1-spec.json` context; seat bounds |
| P1 | Calibration first: distinguish inline comments from HTML-block starts; pin B4/C4 and benign F29 before data | v6 inline class; fixtures/expected/matrices committed in the freeze | **CLOSED** | freeze `d749f7ee`; `records/c1-selftest-expected.tsv`; matrix |
| P2 | Retain every r55/r56 accepted/refused shape as a differential, including the five narrowing rows; do not relax the r56 predicate | 36-row differential; 34 carry rows identical (exit + full finding list); only B4/C4 tightened; the five r56 narrowing rows unchanged: F24 `1 UNFILED-SOURCES-ANNOTATION,PAIR-FILING-HIDDEN`, F26 `1 UNFILED-SOURCES-ANNOTATION`, F27 `1 DELETIONS-UNREADABLE-BINARY`, F28 `1 CORRECTION-FILE-BINARY`, F29 `0` | **CLOSED** | `receipts/c1-matrix.txt`; my matrix join |
| P3 | Selftest coverage: assert all finding ids **or summary fields**, not only the first (M1); mutation-test the row-set assertion (N3) | All finding ids asserted; M1 killed. No summary-field assertion; no row-set meta-test (ghost expected row silently ignored in both gates); the finding detail `hidden_by=` is not asserted by selftest or matrix; the C2 control line is derived from the expected file, not by running `controls/c2-stub.py` | **NARROWED** | `receipts/m1-arms.txt`, `rowset-ghost.txt`, `selftests.txt` |
| P4 | Operability/security: linear line-number calculation, escaped diagnostic strings, symlink-safe scratch roots; finite reproductions in the sentinel report | No implementation in the freeze (same code paths as R6); the sentinel seat held only `receipts/` at observation (no report file) | **OPEN** | source lines; `.ufo/waves/round-57/w1/S57sentinel01/` |
| P5 | Carry the revenger's 41-row disposition table; unresolved items remain explicit | This report; every item carries a verdict and §6 names every non-closure | **CLOSED** | this file; r56 table `census/round-56/wave/w1/S56revenger01.md` |

## 6. New divergences found against the r57 freeze (not r56 items)

| id | shape / observation | command and observed output | class | verdict |
|---|---|---|---|---|
| D1 | **Second inline opener after the first closer on the same line.** A line `… <!-- a --> <!-- second opener` followed by two `R52-CORRECTION` lines and a later `-->`: v6 hides only the opener line and files both corrections; markdown-it 4.2.0 puts both corrections inside the **second** comment. | v6 `rc=0`, `SUMMARY … filed=2 unfiled=0`; render `tokens_visible=0 comment_spans=2`. Fixture built from the committed C4 tree in scratch. | **over-accept of a hidden filing — the same harm class as the r56 B4/C4 defect** | **OPEN** |
| D2 | **Inline code span precedence.** A prose line reading `a code span` followed by the token `<!--` inside backticks and `is literal`, with a later `-->` line: CommonMark treats the token as a code span (no comment), but v6 opens an inline span and hides the corrections. | v6 `rc=1`, two `FINDING CORRECTION-IN-FENCE … hidden_by=inline`; render `tokens_visible=2 comment_spans=0`. | **over-hide (false refusal of honest filings)** | **OPEN** |
| D3 | **Tab-indented opener.** `\t<!-- tab-indented opener` + later `-->`: v6 counts only ASCII spaces, so `indent=0` and the line is treated as an inline opener; CommonMark expands the tab to 4 spaces → indented code → literal. | v6 `rc=1`, two `hidden_by=inline`; render `tokens_visible=2 comment_spans=0`. | **over-hide** | **OPEN** |
| D4 | **C2 receipt binds committed bytes, not execution.** The recorder takes `rev` as an argument and computes the pin from the committed blob; it never checks the tree the command ran against. | Dirty-tree scratch repo: recorder rc 0; receipt `instrument_sha256=<clean blob at R>`, `rev=R`, captured output `RAN-ON: # instrument DIRTY v2`; gate `SUMMARY receipts=1 findings=0`, rc 0; `git status` `M tools/i.py`. Also: the recorder header cites "census/round-57/preregistration.txt, C2 named limits", but the prereg has no such section. | **disclosed limit** (recorder header) but the citation is wrong and no dirty-tree refusal exists | **OPEN** |
| D5 | **r57 ignored build artifact.** `census/round-57/__pycache__/c1-counter.cpython-314.pyc`, 44,686 B, mtime 2026-11-03 20:31:17; `git check-ignore` matches `.gitignore:3:__pycache__/`. The routed-3 class has already recurred in r57. Not deleted by me (lane write ban; may be a live seat's). | `ls -l`; `git check-ignore -v`; `git status --porcelain --ignored census/round-57` shows `!! census/round-57/__pycache__/`. | **class recurrence of R3** | **OPEN** |
| D6 | **C2 selftest is not idempotent.** A re-run in an existing `--work` fails before scoring. | `python3 -B c2-counter.py --selftest --work <existing>` → rc 1, `fixture build failed: ('git','commit','-q','-m','fixture base')`. Fresh `--work`: `SELFTEST pass cases=8`, rc 0. C1's selftest re-runs cleanly (rc 0). | **operability (LOW)** | **OPEN** |
| D7 | **Superlinear inline scan on unclosed openers.** Every `<!--` with no closer scans to end of document, so N unclosed openers cost O(N × lines); a hostile or malformed correction file stalls the counter. | N=5,000 openers → **0.58 s**; N=20,000 → **8.70 s** (≈14.9× for 4×), rc 0 both. The L1's independent probe (`records/probe-scale-unclosed.txt`) measured 0.85 s / 11.17 s (≈13×) and routed it to r58. | **operability (amplification, new in v6)** | **OPEN** |

D1 was also probed by the L1 in `census/round-57/records/probe-second-opener-harm.txt` (post-freeze;
reviewer01 case 04/31), D2 in `records/probe-code-span-overhide.txt` (reviewer01 case 22), and D3 in
`records/probe-tab-indent-overhide.txt` (labelled "revenger D3"). I reproduced the counter side and
the render for all three independently; the fixtures and render counts above are mine. D4–D7 are my
own receipts.

## 7. Items the round does NOT close (explicit, so silence is not read as repair)

- **R1 NARROWED.** The gate/recorder mechanism is committed and observed refusing unrevisioned
  receipts, but (i) the canonical after half is **not green at observation**: `manifests/after.tsv`
  appeared at 20:37 with three rows, and at 20:37–20:43 only `c1-tip.txt` existed — the gate exits 1
  with `FINDING RECEIPT-MISSING census/round-57/records/c2-tip.txt` and `… standing.txt` (the
  executor02 report says Main instructed a two-row manifest and owns finalization), so C2
  T2/T4/T5-after are unverified; (ii) the pin binds committed bytes, not the tree the command ran
  against (D4); (iii) the recorder overwrites an existing `OUT` without refusal (X2). The L1's
  pre-wave probe (`census/round-57/records/probe-rev-shapes.txt`, post-freeze) records
  annotated-tag-object acceptance and stash-only-commit refusal; I did not re-run that probe.
- **R5 NARROWED.** M1 is killed; **M7 (LF-only numstat) is still unasserted and unchanged**; no
  summary-field assertion (a `pairhidden += 3` mutant passes 36/36); no row-set meta-test (a ghost
  expected row is silently ignored in both gates); the `hidden_by=` detail is not asserted by the
  selftest or the matrix; the C2 "control" is a paper count derived from the expected file, not an
  execution of `controls/c2-stub.py`.
- **R6 OPEN.** None of F1–F6 is repaired in the freeze; the r57 SCORECARD bullet P4 is unmet and no
  r57 sentinel report file existed at observation (its seat held only a `receipts/` directory created
  at 20:42).
- **L1–L7 all remain open** (L2 narrowed): two-site scope, unmodelled HTML block types, rstripped
  fence closers, line-only prose judging, F27 carry-over, r56 receipt-key grammar, LF-only numstat.
- **X2 OPEN.** Receipt overwrite after landing is still possible, and a dirty-tree receipt is accepted.
- **P3 NARROWED, P4 OPEN.**
- **D1–D7 OPEN.** D1 is the r56 harm class on an adjacent shape (over-accept); D2/D3 are over-hide
  harms (honest filings refused); D4/D6 are operability limits; D5 is the routed-3 class recurring;
  D7 is a new superlinear path in the v6 inline scan.

## 8. Claim-predicate status at observation (not a closure verdict)

- **C1:** T1 observed (B4/C4 v5 0 → v6 1, both details `hidden_by=inline`); T2 observed
  (C6/F29/F17/F18/F19 rc 0 both arms); T3 observed (34 rows identical exit + full finding list);
  T4 observed (v5 10/36, v6 8/36); T5 observed (`SELFTEST pass cases=36`, rc 0); T6 read from the
  post-freeze `records/c1-tip.txt` (`rev=d749f7ee…`, `unfiled=0 fenced=0`, `EXIT=0`) — not re-run by
  me; T7 observed on the receipts I read (`c1-tip`, `c2-before`, `c1-selftest`, `c2-selftest`,
  `c1-hidden-class`, `c1-targets`, `c1-matrix-run` all carry `EXIT=` lines; the matrices are TSV data,
  the r56 errata reading).
- **C2:** T1 observed (exit 1, exactly one finding); T3 observed (`cases=8`,
  `control=FALSE-GREEN-REJECTED`); T5-before observed (`grep -cE '^rev=[0-9a-f]{40}$'` = 0 on the r56
  receipt). **T2/T4/T5-after not met at observation**: `manifests/after.tsv` exists (20:37, three
  rows) but `census/round-57/records/c2-tip.txt` and `census/round-57/records/standing.txt` are absent,
  so the gate exits 1 with two `RECEIPT-MISSING` findings; only the `c1-tip.txt` row is clean
  (`rev=d749f7ee…`, pin `e18872d6…`, `EXIT=0`). The executor02 report states Main owns the final
  two-row after manifest.

## 9. Boundary and cleanup

No lane, fleet or sibling write outside this report and
`.ufo/waves/round-57/w1/S57revenger01/`; no git/jj mutation outside scratch fixture repos created by
me (each asserted `git rev-parse --show-toplevel == $D` before the first commit). Scratch deleted
before yield. No subagent dispatched; no background job started.
