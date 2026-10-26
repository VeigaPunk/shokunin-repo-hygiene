author: hyaku closure (non-author integrator, @m_opus)

# Souji round 31: non-author closure spot-check

Lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` → tip `d999c596d389dbc710e939b340066297046f3204` (branch `master`).
Report `.ufo/reports/round-31/souji.md`; prompt `.ufo/prompts/souji-round-31.md`.
Driver digest (copied from mutable `.ufo/watchdog.log`):

- `2026-10-26T02:55:57-03:00 launch souji round=31 pgid=297674 driver=hyaku-inline attempt=1`
- `2026-10-26T04:58:50-03:00 complete souji round=31; hyaku-inline attempt=1`

All re-measurements below ran on 2026-10-26 at about 08:00 UTC. They read committed bytes only
(`git show`/`ls-tree -z`/`grep`/`diff` at the named revision). The lane worktree was clean. I executed no lane
gate, counter, fixture or probe, so lane-owned instruments are evidence-verified only. The one external
source (S222) was re-fetched live from its tag and hashed. The staged merge package was read in place.

## Step-1 conformance

| check | command | observed |
|---|---|---|
| report landed by lane | `git log --format='%an <%ae> %H %ci' -- .ufo/reports/round-31/souji.md` (fleet) | `souji-shokunin <souji@shokunin.local> 3322a5456356c747c74f3c73553dd3cf1876a29f 2026-10-26 04:58:17 -0300`. This is after the cited tip d999c59 (04:57:01) and before the complete line (04:58:50). |
| prompt committed | same command, prompt path | `souji-shokunin 8f9997059e7d8b41d6d9fd6f2b0422c983b3f4b1` (02:55:55), 2 s before launch |
| SHONEN heading | `grep -n '^## SHONEN'` on the report; `git show d999c59:SHONEN.md \| grep -c '^- \['` | heading at l.164 with four `[~]` lines, each with a pointer. SHONEN.md has four boxes and is byte-identical at base and tip. |
| cited commits exist + ancestry | `git cat-file -t <h>`; `git merge-base --is-ancestor <h> master` for all 15 cited full hashes (base plus 1d45496, ed17ff6, 1b81136, 26153a4, 6fdd696, 52ebd48, 8024b54, 1baf4da, 24f343c, c610830, 2c16d01, 76bb697, f950267, d999c59) | all are `commit` and all are ancestors of `master`. `git rev-list --count base..tip` = 14, matching "14 lane commits". All 14 are authored `souji-shokunin <souji@shokunin.local>`. |
| pushed, no leftovers | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `local=remote=d999c59… ahead=0 behind=0 head=detached tracked=0 untracked=0`; empty; `d999c59…` |
| prompt contract | `grep -n '^## '` on the prompt (599 lines) | §1 MISSION/AXES binding, §2 claims 1–3, §2b frontier step, §3 L2 floor, §4 report contract incl. SHONEN, §5 commit/push/L0 channel, §6 hyaku addendum, §7 scratch discipline |
| wave seats | `jq '.results\|length'` and non-empty `output` over `census/round-31/waves/w1-results.json`; `ls-tree` count of `census/round-31/waves/w2/Swarm*.md` | w1 38/38 with output (38 `Swarm*.md` captured); w2 36 seat reports. That makes 74 seats and 0 dead, matching the report. |
| receipt revision | `git diff --stat f950267 d999c59` | only `census/round-31/records/final-tip-measure.txt` (+24), so the receipt's revision f950267 grades the tip tree apart from the receipt itself |

Step-1 defects: none that bar status.
- D1 (disclosed by the lane): the C3 record prints four `arm=reflog-only` lines, outside the frozen fixture contract's `arm=<solo|descendant>` (preregistration l.20). It is recorded in `amendments.txt` as a deviation.
- Amendment A5 (C2 v3) landed at 2c16d01, after the C2 landing 8024b54. It is stricter-only and was re-measured at the landing revision, so this is a timing note only.

## Claims: re-checks

Re-measured by me over committed bytes:
- C1: the appended binding-row count, the missing id, the append-only prefix, three sampled record bindings, and the L29 record's shape.
- C2: the round-26 report union (r26 466 → 495) and the C2 diff scope.
- C3: entry presence, the `ground: F1` count, SOURCES row count, the S222 row and live source, the record's versions and RESULT count, and the correction sweep.

Evidence-verified only (lane instruments, not executed):
- the C1 counter (`c1-before.txt`, `c1-after-v1.txt`, `c1-after-a4.txt`);
- the C2 counter v1–v3, fixture G1–G10, REDARM, REGRESS and SHIFT legs (`c2-after-v{1,2,3}.txt`, `c2-fixture-red-before.txt`, `controls.tsv`);
- the C3 counter v1–v3, including the fixture replay, PATH shim and remover mutants (`c3-after-c3-counter*.txt`);
- `final-tip-measure.txt`, the M1 receipts, and the W2 SwarmExecutor27 no-harm sweep.

### C1 calibration: capability-cell literal binding, mismatches 34 → 1: MISSED (confirmed)

- `git show <rev>:SCORECARD.md | grep -cE '^\| L[0-9]{2} \| SCORECARD.md:[0-9]+ \|'` reads 0 at base, 40 at 24f343c and 40 at d999c59. There are 40 distinct ids: 20 `run:` and 20 `record:`.
- `comm` of `c1-cells.tsv` ids against the SCORECARD row ids leaves exactly `L29`.
- SCORECARD is append-only: the tip bytes start with the base bytes (`startswith=True`, 61956 → 81245 bytes), and `git diff -U0 base tip -- SCORECARD.md` has 0 `-` lines.
- Sampled record bindings L03, L08 and L09 checked out:
  - each cited record contains its literal (`5/5 checks passed`, `total=32\tpass=32`, `total=32\tpass=18`; 1 hit each);
  - each record is unchanged between base and tip.
- L29 (`SCORECARD.md:170`, `remote-source-after.json18/18`): `census/round-21/remote-source-after.json` contains no `18/18` string. Its count lives in the scalar fields `expected_command_count`, `matched_command_count` and `observed_command_count` (= 18), plus an 18-element `commands` list.
- The frozen record rule (literal in the record) therefore cannot bind L29. I agree that no honest binding exists under the frozen rule.
- Committed readings: base `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` rc=1. At the landing commit and in the final-tip receipt the reading is `items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` rc=1, under both v1 and A2+A4.
- The kill rule `mismatches>0 at the C1 landing commit or at the tip -> missed` applies. This is an honest stop, reported by the lane itself.

### C2 operability: landing-gate reading precision: VERIFIED

- Plain re-derivation of `r26` (NUL-safe, `git ls-tree -r -z --name-only <rev>`):
  - base: `.ufo/waves/round-26/*.md` = 466 and `census/round-26/waves/*.md` = 495. The union of relative suffixes is 495, and every wave-dir suffix is also in the capture.
  - So the base gate (wave dir only) read 466 and hid 29, and the union reads 495, matching `r26=466 → 495`.
  - (A non-`-z` ls-tree undercounts by one here: six paths in this tree are C-quoted.)
- `git diff --stat base 8024b54 -- tools tests` touches only `tools/souji-landing-gate.py` (+136/−24), the new fixture `tests/fixtures/r31-landing-gate-precision.py` and C1's new `tools/souji-capability-cells.py`.
- Committed evidence at the landing commit 8024b54, under v1, v2 and two v3 random-probe runs: `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same`, plus `shift=ok` under v2/v3.
  - Fixture line: `cases=10 pass=10 control=FALSE-GREEN-REJECTED`.
  - REDARM: the base tool fails exactly G1 G3 G4 G5 G6 G7 G8 and passes G2 G9 G10, as frozen.
  - REGRESS keeps (rc, last line) identical for `--selftest` (`SELFTEST pass=65 fail=0`), r16 (15/15), r30 (7/7) and r19 (4/4).
- The final-tip receipt reads the same. Base control: `fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same`.

### C3 coverage: F1 dropped-keep-ref object lifetime entry, F1 entries 3 → 4: VERIFIED

- `git cat-file -e <rev>:corpus/knowledge/jj-dropped-keep-object-lifetime.md`: absent at base, present at tip. `git grep -l '^ground: F1' <rev> -- corpus/knowledge | wc -l` reads 3 → 4.
- SOURCES rows: `grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` reads 145 → 146, and `S222` occurs 0 → 1 times.
  - The base → tip diff of `corpus/SOURCES.md` changes only the `used-by` cells of S002/S054/S063/S117/S220, matching the lesson's touched-row log, plus the S222 append.
- `jj-object-clock-run.txt` carries `jj-version: jj 0.45.1-7c41cdeb…` and `git-version: git version 2.56.0`, and has 17 `RESULT` lines in three arms.
  - Both outcomes are present: `object_present=no` at `solo/delete-descendant-keep-refs-and-prune`, `descendant/abandon-descendant-and-op-abandon-and-util-gc` and `reflog-only/reflog-expire-then-prune`.
- Committed counter evidence at 1baf4da and the tip: v1 `legs=11 fail=0 f1_entries=4`, v2 `legs=12 fail=0` (PATH shim: jj_calls=26 git_calls=111), v3 `legs=13 fail=0` (both remover mutants change the record). The base control is `legs=11 fail=10 f1_entries=3`.
- Correction sweep: eleven superseded phrasings each occur only inside the entry together with their appended correction bullet. I checked `does not restate`, `survives only when`, `measures the separation`, `absence is cheap`, `independent keepers`, `as the only root`, `reads the same except`, `outranks reflog expiry`, `placeholder id` and `measures the independence`, across SKILL/PROVINCE/README/QUALITY/LOG/SCORECARD/knowledge.
  - The one outside hit, `PROVINCE.md:83` "does not restate it", is an unrelated chousa boundary sentence.
- The routed r30 defect 1 is closed: the SKILL keep-ref bullet now says that packedness, not the threshold, is what the record discriminates, and it reads `keep_refs` 6 to 2 at step 5.

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | unchanged | C1 missed its frozen target by one item (L29). 40 of 41 cell literals now carry an honest appended binding (34 → 1 mismatches), but the claim did not verify and the lane left the score at 7. |
| operability | improved | C2 verified: the gate reads the union (466 → 495, re-derived) and all carry sections, and drops 13 false dangling pointers while keeping both real ones. The fixture is 10/10 with a rejected false-green control, and REGRESS is identical. |
| coverage | improved | C3 verified: F1 entries 3 → 4 and rows 145 → 146, re-measured. The object-removal side was named unmeasured at base (`PROVINCE.md:208`, `jj-keep-ref-expiry.md:126`). |
| depth, freshness, adjacency | unchanged | Not claimed. The SCORECARD diff is append-only (0 deleted lines), and the owned scores 7/8/8 are unchanged. The only in-place deletions in docs are the SKILL keep-ref bullet (routed r30 fix), the README F1 map row (adds the entry) and five `used-by` cells. |

No axis is harmed. The round is not admitted because C1 did not verify. This is an honest stop: the lane reported the miss itself.

## Discernment spot-check (`corpus/lessons/round-31.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S222 git `Documentation/git-reflog.adoc` v2.56.0 (new row; ≤25-word quote check) | ADMIT | https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc re-fetched live: 161 lines, 5657 bytes, sha256 `59e7f0f1…d6bf54` (= `census/round-31/sources/SHA256SUMS` and the committed snapshot) | agree | Lines 66-68 contain the Gate quote verbatim: "Entries older than `expire` time, or entries older than `expire-unreachable` time and not reachable from the current tip, are removed from the reflog." That is 23 words. Lines 114-115 give "`gc.reflogExpire`, which in turn defaults to 90 days", and lines 123-124 give `gc.reflogExpireUnreachable` "defaults to 30 days". So the row's `teaches` cell (90/30 days, `all`/`never`) is grounded. The row's scope disclaims S063/S117 correctly, and tier A docs at a pinned tag is right. |
| `corpus/knowledge/jj-dropped-keep-object-lifetime.md` (the C3 entry) | ADMIT | record `census/round-31/records/jj-object-clock-run.txt`; S222 above; base `PROVINCE.md:208`, `jj-keep-ref-expiry.md:126` | agree (as corrected) | The measured core holds. In `reflog-only`, once the keep refs reaching B are gone, `git gc --prune=now` leaves B present with `reflog_hits=1`, and only `reflog-expire-then-prune` reaches `object_present=no`. Each other arm has its own release step. The entry shipped at 1baf4da with statements stronger than its record or sources, and 18 append-only correction bullets (l.230-247) superseded them in-file at 76bb697. That was before the lesson's admission record (f950267), so no admitted sentence is false and unmarked. Residual traceability gaps are routed below: S051 is quoted but not cited, the S063 cell lacks the CONFIGURATION anchor, and `gc.recentObjectsHook` has no Gate quote. |
| staged `git-grace-period-at-release-r35.md` | REJECT | `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/git-grace-period-at-release-r35.md` (read-only, 68-file package) | agree | :30-31 has the quote verbatim ("`gc.pruneExpire` defaults to **2 weeks** and governs unreachable loose **objects**"). `grep -ciE 'refs/jj\|jj util\|keep ref'` = 0 and `reflog` = 1. The entry is about separating the object window from the worktree-registration window, and its S226-S230 ids would collide. The entry already sources the 2-week window from the gc.adoc bytes it opened itself. |
| staged `prune-expiry-behaviour-r29.md` | REJECT | same package dir | agree | :11-12 has the quote verbatim ("`gc.worktreePruneExpire` sets the grace period, with `now` disabling it and `never` suppressing pruning"). It has 0 jj/keep hits and 0 `reflog` hits. Its measured object is a worktree registration, not a git object. |
| staged `repo-size-census-readonly.md` (older revision) | REJECT | same package dir | agree | :31-32 has the quote verbatim ("Do not consider commits that are referenced only by an entry in a reflog to be reachable."). Its front matter cites S112-S114 at 2026-10-23, so it is an older revision of an admitted lane entry (a re-point, not an admission). Reflog-as-root is not the reflog window. |

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` printed `souji ok …/corpus/SOURCES.md` with rc 0 and 36 W04 lines (duplicate URL across scopes, none on S222). There was no error class, which matches `census-end.txt`.

## Trend verdicts

- **expansion: improved.**
  - One entry is admitted on F1 ground the base named unmeasured in three places: `PROVINCE.md:208` "the object-prune clock that follows a dropped keep ref is unmeasured here", `corpus/README.md:625-627`, and `jj-keep-ref-expiry.md:126` "Ref removal is measured; object removal is not".
  - It cites the `mined` row S222, opened this round, and the F1 map row names it.
  - Two capability rows are demonstrated running in `final-tip-measure.txt` (C2 fixture 10/10; C3 record replay). The third, C1's audit, runs but reports its one refusal.
- Against expansion: W2 SwarmCritic21 judges the move depth on held ground. Its own evidence lists the held propositions, and the entry's corrections now cite them as held. What is new and measured is the removal side: three releases and the reflog-only isolation. That is net new coverage of a gap the map named, so I rule above the lane's own `unprovable-but-better`.
- **quality: improved.**
  - The landing gate reads 29 hidden round-26 reports and every carry section, and drops 13 false dangling pointers.
  - The SKILL keep-ref bullet is corrected (routed r30 defect 1).
  - 74 seat failures from r26-r28 are carried. The wave-2 audit found 18 wrong dispositions, and those were corrected append-only at 76bb697.
  - The entry's overstatements were superseded before admission.
- Against quality: no admitted entry is left false and unmarked. The pre-existing `souji-declared-evidence` reads 21 mismatches at both base and tip (SwarmExecutor27), so this round introduced no regression there.
- **discernment: improved.**
  - The spot-check agrees with the gate on both sampled admits and all three sampled rejects.
  - The three new criteria Q67-Q69 each cite `corpus/lessons/round-31.md` plus committed records as motivating evidence.
  - The lane rated itself `unchanged` because C1 missed and wave-1 gamed v1 counters. Under LEARNING.md's observable (gate decisions vs the outside spot-check, and grounded criteria), the trend is improved.

## Routed defects (lane fixes next round)

1. L29 (`SCORECARD.md:170`, `remote-source-after.json18/18`): bind it with an appended dated row that names the record's scalar fields (`expected_command_count`/`matched_command_count` = 18). Alternatively, widen the record rule, stricter-only, to accept a named field pair. Do not leave the cell literal unbound.
2. C3 entry traceability:
   - add S051 to the entry's `source:` lines and the S051 `used-by` cell, or drop the quote (lesson Gate l.19);
   - add the CONFIGURATION/`config/gc.adoc` anchor to S063's cell, or open a dedicated row;
   - give `gc.recentObjectsHook` a Gate quote (entry correction l.247).
3. D1 recurrence guard: a preregistered fixture contract with an enumerated field (`arm=<solo|descendant>`) must be amended, stricter-only, before a record prints a value outside it. Do not disclose the deviation after landing.
4. Landing-text discipline (Q65/Q69 class): after wave 2 the C3 entry needed 18 append-only correction bullets (entry l.230-247), and M1 needed 18 disposition corrections (10/26, 3/29, 5/19). Before the landing commit, run the correction sweep and a sentence-to-record check over every claim sentence, not only the backticked RESULT spans.
5. Lane residuals to carry, as listed in SCORECARD `### Planned (appended at round 31)`:
   - the C1 enumeration gap (count statements outside the notation);
   - the file-granular record rule;
   - the C2 oracle envelope and the letters-only prose blind spot;
   - surviving gate mutants M4/M10;
   - uncarried seat failures of r15/r19/r23/r24/r25;
   - `/var/tmp` snapshots in the gate (§7 item 4).

SHONEN: four `[~]` boxes whose pointers resolve at the tip:
- `SKILL.md` gate rows `souji-capability-cells`, `r31-landing-gate-precision`, `r31-jj-object-clock`, the r31 error-pattern bullet, and S222;
- `LOG.md:362` (2026-10-19 operator sweep) and `LOG.md:1796` (the r31 entry);
- `final-tip-measure.txt`;
- `PROVINCE.md:213` (r31 boundary note) and `census/round-31/waves/w2/SwarmConnector28.md` ("STATUS: PASS — 20 sibling lanes scanned").

The boxes look checkable by a non-author, but promotion is operator-owned.
