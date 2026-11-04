# Round 58 verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

## Scope and decision

Reviewed base `83d3813257648e99fb4ab2ddef217124f39cf324` → final round tip `8743010706b399dbc4121c09985d4ebfb85fb797`. Status **ok** (real committed report), **admitted=false**, **rejected-honest-stop**. Finite C1 and C2 results are reproducible/evidence-verified, but C2 lacks the binding pre-freeze committed control prerequisite. This is not a fabricated-result finding or a new-harm finding. Read-only independent reviewer seats: CloseSoujiR58.Souji58C1Review (critic) and CloseSoujiR58.Souji58GateReview (reviewer). Neither authored the round; no lane gate/selftest was executed by closure.

## Step-1 conformance

- `git log --format='%an %H' -- .ufo/reports/round-58/souji.md` returned `souji-shokunin 65addc1febd28002bd831600a749698ab8871e9f`. Report has SHONEN heading and four `[~]` evidence lines, actual work, LOG ties and full commit hashes; it is not a marker. Report commit time 12:07:46 -03:00 follows final lane commit 12:06:53.
- `jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin` returned `branch=master local=8743010706b399dbc4121c09985d4ebfb85fb797 remote=8743010706b399dbc4121c09985d4ebfb85fb797 ahead=0 behind=0 head=detached tracked=0 untracked=0`. `git ... status --porcelain` printed nothing. This is the pre-verifier state.
- For each cited hash, `git -C LANE cat-file -t HASH` returned `commit` and `git -C LANE merge-base --is-ancestor HASH refs/heads/master` returned 0: e7f64f30324e8ddb3f2266302daa9066054cdbb3, dccdc469f4c2e0415e1a1dcc317364e1b4d3191e, 1880343ed04337379c5478f91408c30c8fbd4b77, b1c2bb9f762baa8142eaeaa5d4f472765b09dd32, 5e4b8f14572d7051537b167dece4541bed7d2bab, 81d556e7f94569ae5f24b38458f157b153188191, final tip, and cited prior-closure hashes fafe371694fea41c5d23f63083865d5ccf3f1d36, b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd and base.
- Dispatched prompt carries mission/axes, distinct 1–3 claims, L2 floor, report path/SHONEN/hash/commit ordering, own-lane scope, push scope and L0 channel; campaign amendments explicitly supersede routing/seat requirements. Prompt is committed (`git log -1 --format='%an %H' -- .ufo/prompts/souji-round-58.md`: souji-shokunin 5d337908fbfc1b3b48b77923ab93d2df13ff6623).
- Durable driver digest: `2026-11-04T11:37:51-03:00 launch souji round=58 pgid=2680205 driver=hyaku-inline attempt=1`; `2026-11-04T12:08:03-03:00 complete souji round=58; hyaku-inline attempt=1`.

## Claim re-checks

### C1 calibration — independently re-measured

Read committed files using `git -C LANE show REV:census/round-57/records/c1-matrix-v5.tsv`, corresponding v6 path, and `REV:SCORECARD.md`, for both base and final tip. Independent Python `csv.DictReader(io.StringIO(blob), delimiter='\t')` parsing gave 36 rows per matrix, identical fixture order, `sum((a['exit'],a['findings_all']) == (b['exit'],b['findings_all']) for a,b in zip(v5,v6)) = 34`, and `sum(r['exit']=='0' for r in matrix) = 10,8`. The two exact R58-CALIBRATION correction notes are absent at base and present at final tip: **assertions=2 mismatches=2→0**. Matrices are unchanged. This validates two enumerated record corrections, not discovery completeness or Markdown visibility. SCORECARD diff is append-only and scores remain 7/8/8.

### C2 operability — committed evidence verified, prerequisite unprovable

Plain JSON extraction: `json.loads(json.loads(git_show(REV + ':' + PATH))['stdout'])['target']['cases']`, then `sum(case['passed'] for case in cases)` gave **3/8** in `census/round-58/before-arm.json` and **8/8** in `census/round-58/c2-after.json`. Before: abs, ../, parent-symlink-escape, annotated-tag-OBJECT, conflicting-rev all incorrectly EXIT0; real-1/2/3 clean. After: first three have RECEIPT-PATH-UNCONFINED, tag has RECEIPT-REV-ABSENT, conflict has RECEIPT-REV-CONFLICT (all EXIT1); three real receipts remain EXIT0. Always-clean and always-refuse controls are both rejected.

Committed `c2-selftest.txt` reports exact case set 17/17, rc/full normalized finding comparisons, false-green control rejected, EXIT0; committed expected TSV has 17 data rows. Registry exists in SKILL.md Round 58 current receipt interface. `sha256(git show FINAL:census/round-58/c2-gate.py)` = `56f2a31163035726f1190db3e6b827fc121602377e187d16a54a6ae8f15af543`; oracle digest = `55b5e063fa57a02d7fcf186c9d8e9b719b0ecb76b08001ad0988ad76aa3fc82e`. Both match recorded bindings. Measured revision is `5e4b8f14572d7051537b167dece4541bed7d2bab`, not an inferred execution at the bookkeeping tip. These are evidence verification and receipt counts, not gate re-execution.

**Admission prerequisite:** prompt §9 requires building/scoring/committing the do-nothing control before freezing. `git show -s --format='%H %cI' HASH` gives predicate freeze e7f64f3 at 11:44:19 -03:00, C1 correction dccdc46 at 11:46:25, executable C2 oracle/control first retained 1880343 at 11:50:15, bound C1 replay b1c2bb9 at 11:55:37, final candidate 5e4b8f1 at 12:01:56. Preregistration explicitly says C2 oracle is “to be built.” The later committed control beats do-nothing, but cannot retrospectively satisfy the pre-freeze commitment. The final disclosure honestly preserves this and leaves first development-selftest/control generation order unknown. No predicate changed; no stronger accusation follows. Full C2 claim therefore remains **unprovable** under its operative prerequisite.

## Axis verdicts and no-harm check

| Owned axis | Verdict | Evidence |
|---|---|---|
| calibration | improved | independently reproduced two bounded assessment mismatches 2→0; scores unchanged; late C1 bound receipt disclosed |
| operability | unprovable | finite 3/8→8/8 evidence verifies, but pre-freeze committed control absent; no new harm established |
| coverage | unchanged | no new knowledge/capability/frontier promotion; PROVINCE unchanged |

`git diff BASE FINAL -- SCORECARD.md` contains appended corrections/measurements/plan only. Spot-read SKILL current-interface registry, QUALITY Q117/Q118, lesson residuals and README frontier; they preserve certification OFF, K5 HELD, old rejected parser/recorder harms and bounded pathname/resource limitations. Existing harms are not retroactively repaired or re-admitted. No axis newly harmed was established on this bounded review. SHONEN assertions are not a full independently executable promotion proof here; no boxes checked and no promotion recommended.

## Discernment spot-check

Reopened both official URLs on 2026-11-04; manual version shown 2.56.0. Sample drawn from round-58 lesson Gate continuation and new SOURCES rows S284/S285.

| Item | Decision | Re-opened source | Judgment | Reason |
|---|---|---|---|---|
| S284 raw type observation | admit | https://git-scm.com/docs/git-cat-file, OPTIONS `-t` | agree | exact located 11-word quote: “Instead of the content, show the object type identified by <object>.” Supports type observation, not execution authentication |
| S285 peeling-as-raw-identity inference | reject | https://git-scm.com/docs/gitrevisions, SPECIFYING REVISIONS `<rev>^{<type>}` | agree | exact located 14-word excerpt: “dereference the object at <rev> recursively until an object of type <type> is found”; recursive peeling does not establish original raw object type. Document itself is not rejected |

Both quotes meet ≤25 words and ground their scoped teaches. SOURCES row regex `^ {0,3}\|\s*S[0-9]{3,}\s*\|` over committed blobs independently gives **207→209**. Required `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` executed here: EXIT0, 64 W04 duplicate-URL-across-scopes warnings and final `souji ok .../corpus/SOURCES.md`; no error. These scoped duplicates are not concealed or expansion credit.

## Learning trends

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | unchanged | two source rows only, no admitted knowledge on uncovered ground or repertoire addition |
| quality | improved | finite five repaired refusal cases with three honest receipts preserved; bounded correction accuracy; residual limitations explicitly marked |
| discernment | improved | outside check agrees on admit and reject; lesson-backed Q117/Q118 capture prior outside disagreement and pre-landing safety mistakes |

Trend improvement does not waive the C2 admission prerequisite. No exploratory claim is judged.

## Routed defects — souji next round

1. Preserve this honest-stop: pre-freeze control commitment failed for C2. Next new claim must retain a revision/instrument-bound do-nothing control before predicate freeze and any scoring; later replays must never backdate it. C1's original freeze receipt lacked command/revision/digest headers; later bound replay is useful evidence, not original binding proof.
2. C1 comparator is registered as `evidence` but reads/compares persisted expectations and returns a verdict, meeting PROTOCOL's gate definition. Correct registry classification and provide isolated self-invocation rc/finding tests; external discrimination fixtures do not replace the required gate selftest. Status-neutral conformance defect, independent of the reproduced two-note result.
3. Keep inherited visibility-parser, recorder dirty-tree/overwrite, capture row-set meta-test, historical receipt bindings, atomic-read/resource and diagnostic debts OPEN; no new finding here closes them.

Closure self-evaluation: accuracy4 (gate execution deliberately excluded), completeness4 (bounded review, not universal safety audit), clarity4 (finite success separated from prerequisite failure), actionability4 (specific routed controls/classification), conciseness4 (long receipt history summarized); average4.0. Highest-impact improvement: a compact pre-freeze bound control would remove the central ambiguity in future rounds. No tools installed or updated.
