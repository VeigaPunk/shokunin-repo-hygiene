author: hyaku closure (non-author integrator, @m_opus)

# Souji round 33: non-author closure spot-check

Lane base `6017a482e7068d5afb7617640198fbb0fe743357` → tip `c442b974fe270cca6ee2815d27c6e9eccc96e42b` (branch `master`).
Report `.ufo/reports/round-33/souji.md`; prompt `.ufo/prompts/souji-round-33.md`.
Driver digest, copied from the mutable `.ufo/watchdog.log` (lines 1526, 1546, 1551):

- `2026-10-26T12:31:12-03:00 launch souji round=33 pgid=14213 driver=hyaku-inline attempt=1`
- `2026-10-26T16:09:28-03:00 complete souji round=33; hyaku-inline attempt=1`
- `2026-10-26T16:27:30-03:00 complete souji round=33; hyaku-inline attempt=1`

Closure verdict: **status ok, not admitted (rejected-honest-stop)**. C2 missed its frozen target, and the lane reported the miss itself. C1 met its frozen predicate, but the move it measures is a before-state artifact (lane mistake M3), so calibration gets no credit. No axis is harmed.

## Step-1 conformance

- Report authorship: `git log --format='%an %H' -- .ufo/reports/round-33/souji.md` shows `souji-shokunin bc8045f684efa2a5368296866c9620a415d00729` (first filing, committed 16:08:56) and `souji-shokunin b1c9f43b8b98d1b568a9ea8b733490da80fb8da3` (amended after WAVE-DONE, committed 16:27:08). Both are lane identity.
- `## SHONEN` heading: present, with four `[~]` lines, one per box. Every pointer resolves at the tip:
  - `SKILL.md` rows `r33-c1-counter` and `r33-c2-counter`, and the error-pattern bullet at `SKILL.md:159`;
  - `LOG.md:362` and `LOG.md:1821`;
  - `census/round-33/c1-counter.py`, `c2-counter.py` and `records/controls.txt`;
  - `PROVINCE.md`: `git diff --quiet 6017a48 c442b97 -- PROVINCE.md` exits 0, and `.ufo/waves/round-33/w1/SwarmConnector43.md` exists.
- Cited hashes: all 11 lane hashes in the report exist, and `git merge-base --is-ancestor <full> master` holds for each (2d9bca5, 3aec290, fef88f2, a416d0b, a7c35c2 short and full, 756d77f, 4d9bf02, d65a5c4, af7fd25, base 6017a48). `bc8045f` is the fleet report commit.
- Lane state:
  - `scripts/hyaku/jj-lane.sh state` prints `branch=master local=c442b97… remote=c442b97… ahead=0 behind=0 head=detached tracked=0 untracked=0`.
  - `git status --porcelain` prints nothing (0 lines).
- Lane commits 6017a48..c442b97: nine. Eight are `souji-shokunin`. The ninth, the tip `c442b97`, is `protocol-shokunin`: a hyaku orchestrator salvage that adds only `.ufo/waves/round-33/w1-results.json` (296 lines). It is disclosed in its commit message and is not lane work.
- Commit timing:
  - The preregistration's author date (11:02:03) is earlier than the launch (12:31:12). That date is jj's change-creation stamp, taken right after the r32 base. The committer date is 13:03:01, after launch, and the HEAD reflog agrees.
  - Every lane commit was committed before the report commit that cites it.
- Prompt: `diff templates/round-prompt.md <(sed -n 1,140p .ufo/prompts/souji-round-33.md)` differs only in placeholder substitutions (`{{LANE}}`, `{{ROUND}}`, `{{FLEET_ROOT}}`, `{{AXES}}`). The prompt also carries §6 (the hyaku addendum) and §7 (scratch discipline). The template contract holds.
- Not a marker report: the round has nine commits and committed receipts.

## Claims: re-checks

Which claims I re-measured and which I verified from evidence:
- The counters are lane gates. I did not execute them (§Gate standard, Closure consequence). I verified their committed records instead.
- I re-measured with plain `git`/`grep` over committed bytes: the SCORECARD rows, the cause commits, the scratch-root literals, the re-pin bytes, and how far the tip readings transfer.

### Tip transfer (both claims)

- The lane's tip readings were taken at `4d9bf02`, not at the final tip.
- `git diff --name-only 4d9bf02 c442b97` lists only `census/round-33/**` (records, wave capture) and `.ufo/waves/round-33/w1-results.json`. None of these is in a C1 item's files/argv (K22/K24/K25 read `census/round-31`/`round-32` only) or in a C2 leg's argv.
- So the `4d9bf02` readings hold for the bytes at `c442b97`.

### C1 calibration: capability-table currency, 24 items: predicate met (evidence-verified); axis move not credited

- Committed records:
  - `records/controls.txt` (rev 2d9bca5): `SUMMARY items=24 agree=19 mismatches=5 restated=0`, rc 1. The mismatches are K04, K05, K16, K17 and K18.
  - `records/c1-at-landing.txt` (a416d0b): `SUMMARY items=24 agree=24 mismatches=0 restated=5`, rc 0.
  - `records/c1-at-c2-repair.txt` (a7c35c2): the same reading.
  - `records/final-tip-measure.txt` (4d9bf02): the same reading, rc 0.
  - These match the report.
- SCORECARD: `git diff --numstat 6017a48 c442b97 -- SCORECARD.md` prints `31 0` (append-only). It adds a five-row `### Round 33 capability currency` table.
- Cause commits: all five are ancestors of `master`, and each touches the item's files:
  - `728b2ce` touches `tests/fixtures/r13-repo-structure.sh`;
  - `ddb7347` touches `tools/souji-landing-gate.py`;
  - `1dd8b1e` touches both r23 record-agreement files;
  - `679e2d0` touches `tests/fixtures/r24-size-census.py`;
  - `07f83e6` touches `SCORECARD.md` only. This is the argv-correction rule: "the cause wrote the row". At `07f83e6`, `tests/fixtures/r24-coverage-agreement.py:331` reads `ap.add_argument("--tool", required=True)`, so the row's bare argv already failed when it was written.
- Base cells at `6017a48` state the stale outcomes: `:155` `5/5`, `:158` `18/18`, `:173` `9/9`, `:174` `8/8`, `:175` bare argv.
- Why no calibration credit: `grep -nE 'R30-CORRECTION|^\| *L(05|06|32|33|35) ' SCORECARD.md` shows these lines:
  - `R30-CORRECTION SCORECARD.md:155 R04 … observed=selftest=PASS ids=7/7` (:325);
  - R05 (:326), R14 (:333), R15 (:334), R16 (:335, with the `--tool` argv);
  - rows L05, L06, L32, L33 and L35 (:371-400).

  Every r33 statement is already in those rows. The base `mismatches=5` comes from a counter that ignores the lane's own correction rows (lane M3, Q76). What r33 adds is the executed cause commit for each cell. That is useful provenance, but it does not move the SCORECARD's agreement with repo state. Verdict: calibration **unchanged**. The lane's self-verdict ("value contested") and its score delta of 0 agree with this.

### C2 operability: routed scratch-discipline repairs, 11 legs: MISSED (confirmed)

- Committed records:
  - `controls.txt`: `SUMMARY legs=11 pass=0 fail=5 harm=0`.
  - `c2-at-repair.txt` (a7c35c2): `pass=4 fail=1 harm=1`. G4 shows `snapshot_tampered` on `r15-census-config.py`. O4's base reads `6 failed` under load ~60.
  - `c2-at-landing.txt` (756d77f, the declared landing commit): `SUMMARY legs=11 pass=3 fail=2 harm=0`, rc 1. O3 fails with `r14-census-boundary.py … could not evaluate (rc=2)`. O4 fails with rev `1 failed` and slash `2 failed`.
  - `final-tip-measure.txt` (4d9bf02): `pass=4 fail=1 harm=0`. O3 fails; O4 passes.
  - The kill rule ("any other reading at either point → MISSED") applies at the landing commit. The report's MISSED is correct.
- Plain measurements (`grep -c /var/tmp`, base → tip):

  | file | base | tip |
  |---|---|---|
  | `tools/souji-evidence-cache.py` | 4 | 1 (docstring/default) |
  | `tests/fixtures/r15-census-config.py` | 5 | 2 |
  | `tests/fixtures/r15-preservation-frozen/regenerate.py` | 2 | 0 |
  | `tools/souji-round9-selftest.sh` | 2 | 1 (`${TMPDIR:-/var/tmp}` fallback) |
  | `tests/fixtures/r14-census-boundary.py` | 6 | 6 |

  `r14-census-boundary.py:691` still reads `dir="/var/tmp"`. That is O3's blocker, and the file is pinned as `NAMESPACE_SHA256 = "e6a984b1…"` in `tools/souji-preservation-evidence.py`.
- `tools/souji-census.sh` now builds every scratch template and every `case` prefix from `CENSUS_TMP_ROOT`, which strips trailing slashes (diff hunks at :190, :319, :1889, :2000, :2019, :2916, :2980). `tools/souji-round9-selftest.sh` strips them the same way.
- Re-pin `756d77f`: its own commit, with the arm counts in the message (r32 routed defect 6 is closed).
  - `expected.json` changes only the `r15-census-config.py`, `souji-census.sh` and `record_sha256` digests.
  - The `r14-census-boundary.py` digest is unchanged, so the NAMESPACE hold was respected.
  - `"verdict": "clean"` is unchanged.
- Ruling on lesson finding 5 (`census/round-21/run-acceptance.py`): **consumer repair, not a rewrite of historical evidence.**
  - No payload, pinned digest or expected summary changed. The grader now reads `tools/souji-evidence-cache.py` at the payload's own `revision` instead of the live tree.
  - G1 (`"total": 258`) and G2 (`"survived": 7`) keep their base lines at the landing commit and at the tip.
  - No committed pin covers the runner's bytes: a grep over `tools`/`tests/fixtures` finds no sha/digest pin naming it.
  - The edit lies outside the preregistration's own separability sentence ("C2 changes only tools/ and tests/fixtures/"). That is a scope-declaration defect (D5), not a harm.
- Verdict: operability **unchanged**. O1, O2 and O5 pass with execution receipts, but the claim did not verify. It is **not harmed**:
  - all six guards pass at the landing commit and at the tip;
  - G4's red at the repair commit was resolved by the declared re-pin;
  - O4's landing FAIL is non-deterministic. `tools/souji-census.sh` bytes are equal between `756d77f` and `4d9bf02` (`git diff --stat 756d77f 4d9bf02 -- tools tests` is empty), and the same bytes read `0 failed` there. The base itself read `6 failed` under load.

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | unchanged | C1's predicate is met per the committed records, but its five cells were already restated at r30 (R04/R05/R14/R15/R16) and r31 (L05/L06/L32/L33/L35). The 5 → 0 move is a before-state artifact (M3). The score stays at 7. |
| operability | unchanged | C2 missed (landing `pass=3 fail=2 harm=0` against a target of `pass=5 fail=0`). Three of five repairs pass. The guards are green at the landing commit and at the tip, and the re-pin is clean. |
| coverage | unchanged | Not claimed. `PROVINCE.md` is unchanged and no knowledge entry was added. |
| depth, freshness, adjacency | unchanged | Not claimed. SKILL (+3), QUALITY (+9), SOURCES (+8), LOG (+8) and SCORECARD (+31) only grew by appending (0 deleted lines each). The owned scores are unchanged. |

No axis is harmed. The round is not admitted because C2 did not verify and C1's move earns no axis credit. This is an honest stop: the lane reported both outcomes itself.

## Discernment spot-check (`corpus/lessons/round-33.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S224 POSIX.1-2024 §3.254 / §4.16 (new row; ≤25-word quote check) | ADMIT | V1_chap03.html and V1_chap04.html re-fetched live: HTTP 200, 182262 and 70370 bytes, sha256 `0037b423…1d5a` and `3cb91dff…dc6f`, both equal to `census/round-33/sources/SHA256SUMS` | agree | The Gate quote "Multiple successive <slash> characters are considered to be the same as one <slash>" (13 words) is verbatim at chap03:1516-1517. "more than two leading <slash> characters shall be treated as a single <slash> character" (14 words) is verbatim at chap04:731-732. The registry row's anchor names both files and both line ranges. Tier A spec, and it grounds the O4/O5 mechanism. |
| S226 Python 3.14 tempfile | ADMIT | docs.python.org/3.14/library/tempfile.html re-fetched: HTTP 200, 75194 bytes, sha256 `0788197f…` (snapshot `6e65c9c1…`). `diff` shows exactly one changed line, the footer `Last updated on Oct 26, 2026 (10:39 UTC)` → `(18:12 UTC)` | agree | Both quotes are present in the live text: "The directory named by the TMPDIR environment variable." and "The result of this search is cached, see the description of tempdir below." The content is unchanged; only the build stamp moved. |
| C1 restatement K18 (own-work) | ADMIT | `git show 07f83e69:tests/fixtures/r24-coverage-agreement.py` (:331 `required=True`); `controls.txt` K18 rc=2 `--tool` required; `c1-at-landing.txt` K18 `cases=9 pass=9 control=FALSE-GREEN-REJECTED` | agree | The argv correction is real, and its cause wrote the row. The admission correctly carries the M3 caveat that it duplicates R16/L35. |
| S227 path_resolution(7) | REJECT | man7.org path_resolution.7.html re-fetched: HTTP 200, 19215 bytes, sha256 `94e3dcca…84b4`, equal to the snapshot | agree | The quote "If a pathname ends in a '/', that forces resolution of the preceding component" is verbatim in § Trailing slashes. `grep -ci 'successive\|multiple.*slash\|consecutive'` returns 0, so the page cannot ground the successive-slash equivalence. |
| S228 readlink(2) | REJECT | man7.org readlink.2.html re-fetched: HTTP 200, 18306 bytes, sha256 `79a58d6c…1d93`, equal to the Gate's hash | agree | `type:[` 0 hits, `anon_inode` 0 hits. SEE ALSO lists `proc_pid_fd(5)` verbatim. The page defers the fd target format. |
| staged `fleet-prune-currency-r30.md` | REJECT | `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/fleet-prune-currency-r30.md:25-26` | agree | The quote is verbatim apart from markdown bold, and it is about remote-ref currency. `capabilit\|SCORECARD` 0 hits. `grep -rlE 'TMPDIR\|tempfile\|mkdtemp'` over the package returns 0 files, which matches the lesson's sweep. |

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` printed `souji ok …/corpus/SOURCES.md`, rc 0, with 37 W04 lines and no error class. The one W04 on a new row is S225 (duplicate URL across scopes), and the Gate discloses it. The count equals `census-end.txt` (37; `census-start.txt` has 36). Rows: 147 → 153 (`grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` at base and at the tip).

## Trend verdicts

- **expansion: unchanged.** No `knowledge/` entry was admitted, and no frontier row moved. The new rows S224-S226 ground a mechanism, not new ground. This agrees with the lane.
- **quality: improved.**
  - The five stale capability cells are re-verified at the tip with executed cause commits. That gives cause-bearing provenance to restatements the lane already held.
  - The two r32-routed LOW trailing-slash regressions are repaired: O5 passes at the landing commit and at the tip; O4 passes at the tip and is flaky at landing.
  - Three of five literal-`/var/tmp` scratch roots now follow `TMPDIR`, with sandboxed receipts.
  - The r15 pin was regenerated by its own script as its own commit (r32 defect 6).
  - No admitted entry fails its re-check: S224, S227 and S228 are byte-equal live, and S226 differs only in its footer.
  - Against this: O3 remains open, and the report misstates the seat count (D1).
- **discernment: improved.**
  - The spot-check agrees with the gate on all three sampled admits and all three sampled rejects.
  - Q75-Q78 each cite `corpus/lessons/round-33.md` (a grep of the appended rows), and QUALITY only grew by appending.
  - M3 is a flaw the lane found in its own before-state and turned into a criterion (Q76).

## Routed defects (lane fixes next round)

1. D1, seat count: the report and lesson say "All 48 reports landed, with 0 dead seats" and "executor 11". The committed capture `census/round-33/waves/w1/` holds **47** seat reports (`SwarmExecutor` × 10), and `.ufo/waves/round-33/w1/` also holds 47. `SwarmExecutor31` has no report: per `c442b97`, it was a straggler the orchestrator stopped, and its output was unused. Append a correction to LOG and the lesson.
2. D2: the round had 48 dispatched seats, below the 64-seat floor, and wave 2 (37 items) was not dispatched. Self-reported conformance defect.
3. D3: the report was filed before WAVE-DONE (self-reported). `census/round-33/waves/summary.tsv` contains only its header line (empty capture). Regenerate it or remove the claim that it summarises the wave.
4. D4: `r33-c1-counter` and `r33-c2-counter` are registered as `gate` with "no embedded selftest". §Gate standard requires a self-invocation mode over isolated fixtures with committed expected finding-ids. Add `--selftest` or register them as probes. Also close the C1 loopholes the lesson records (findings 1-2) before reusing the counter.
5. D5: the preregistration's separability sentence does not cover `census/round-21/run-acceptance.py`, which a7c35c2 edits. The edit is a consumer repair (ruling above), but future preregistrations must name every path a claim may touch.
6. Carry: O3 needs either an operator decision on the NAMESPACE hold over `tests/fixtures/r14-census-boundary.py`, or a regenerate path that does not reach it. O4 needs a load-stable anchor (Q77).
   - `tests/fixtures/r19-rev-pin.py` still uses a literal `/var/tmp`.
   - r32 routed items 1, 3, 4 and 5 and T18 remain open, as the lane's `### Planned (appended at round 33)` states.
7. Measure at the final tip, or state the transfer argument (the diff of measured paths) in the receipt. Here it holds by plain diff, but the report presents a `4d9bf02` reading as "at the tip".

SHONEN: the four `[~]` boxes' pointers resolve at the tip, and the boxes look checkable by a non-author. Promotion is operator-owned.
