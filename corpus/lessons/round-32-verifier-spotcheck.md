author: hyaku closure (non-author integrator, @m_opus)

# Souji round 32: non-author closure spot-check

Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d` → tip `04b9221347073b9c58624b36e8d849481e4dacd6` (branch `master`).
Report `.ufo/reports/round-32/souji.md`; prompt `.ufo/prompts/souji-round-32.md`.
Driver digest, copied from the mutable `.ufo/watchdog.log` (lines 1501, 1512, 1513, 1521):

- `2026-10-26T05:07:28-03:00 launch souji round=32 pgid=1699416 driver=hyaku-inline attempt=1`
- `2026-10-26T09:23:45-03:00 lane-dead-no-report souji round=32; retry same round (hyaku-inline attempt=1: attempt 1 L1 died in the orchestrator host crash 2026-10-26 ~08:50 -03 (omp process exit); no report landed; work salvaged to the lane branch)`
- `2026-10-26T09:23:46-03:00 launch souji round=32 pgid=1819028 driver=hyaku-inline attempt=2`
- `2026-10-26T10:56:13-03:00 complete souji round=32; hyaku-inline attempt=2`

All re-measurements below ran on 2026-10-26 at about 13:30-14:00 UTC. They read committed bytes only
(`git show`/`ls-tree`/`grep`/`diff`/`comm` at the named revision). The lane worktree was clean. I executed no lane
gate, counter, fixture or probe, so lane-owned instruments are evidence-verified only. The three tag-pinned
sources were re-fetched live and hashed. The staged merge package was read in place.

## Step-1 conformance

| check | command | observed |
|---|---|---|
| report landed by lane | `git log --format='%an <%ae> %H %ci' -- .ufo/reports/round-32/souji.md` (fleet) | `souji-shokunin <souji@shokunin.local> 9c8b964ab1df2aa6b9c34f8d76f7a98d7d59eba3 2026-10-26 10:55:49 -0300`. That is after the cited tip 04b9221 (10:53:49) and before the complete line (10:56:13). |
| prompt committed | same command, prompt path | attempt 1 `ca7153571a1a4f1913ee7bd10eb029b697a07753` (05:07:25); attempt 2 `12778f8ee31d508e4bd07ae75b87439bf0ea524c` (09:23:45), a one-line change; both by `souji-shokunin` and before their launch lines |
| SHONEN heading | `grep -n '^## SHONEN'` on the report; `git show <tip>:SHONEN.md \| grep -c '^- \['` | heading at l.173 with four `[~]` lines, each with a pointer. SHONEN.md has four boxes and is byte-identical at base and tip (`git diff --quiet`). |
| cited commits exist + ancestry | `git cat-file -t <h>`; `git merge-base --is-ancestor <h> master` for all 10 cited full hashes (base, 3ec84fc, 7a6667c, 98e5203, a92e1aa, 9e8982b, 4e56c48, 9da5e9a, 4ea897f, 04b9221) | all are `commit` and all are ancestors of `master`. `git rev-list --count base..tip` = 9, matching "9 in total". All 9 are authored and committed by `souji-shokunin <souji@shokunin.local>`. |
| pushed, no leftovers | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain \| wc -l`; `git ls-remote origin refs/heads/master` | `local=remote=04b9221… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `0`; `04b9221…` |
| prompt contract | `grep -n '^## '` on the prompt (599 lines) | §1 MISSION/AXES binding, §2 claims 1-3, §2b frontier step, §3 L2 floor, §4 report contract incl. SHONEN (l.118, l.413), §5 commit/push/L0 channel, §6 hyaku addendum, §7 scratch discipline |
| wave seats | `jq '.results\|length'` over `census/round-32/waves/a2w1-results.json`; `ls-tree` counts of `Swarm*.md` under `waves/a2w1` and `waves/w1` | a2w1 38 results and 38 seat reports. w1 has 41 seat reports, and `SwarmReviewer30`, `SwarmReviewer31` and `SwarmMutationTester40` have none (3 dead of 44). `w2.ready.dispatched` reads `ABANDONED … no seat was spawned`. This matches the report's 82 seats and 3 dead. |
| receipt revision | `git diff --stat 4ea897f 04b9221` | only `census/round-32/records/final-tip-measure.txt` (+167), so the receipt's revision 4ea897f grades the tip tree apart from the receipt itself |

Step-1 defects (none bars status):
- D1 (attribution, disclosed): the orchestrator salvage `4e56c48` is authored and committed under the lane identity. The report and its subject name it as orchestrator work, and attempt 2 re-verified it rather than adopting it.
- D2 (precision): the report says the landing gate reads `findings=0` for round 32 at the tip. The only committed run is at 4ea897f and reads `findings=2` (`final-tip-measure.txt:164-166`). Both findings are `LG-DANGLING-PTR` to `final-tip-measure.txt` itself (`SCORECARD.md:481`, `corpus/lessons/round-32.md:94`). The file is absent at 4ea897f and present at 04b9221 (`git cat-file -e`), so the pointers resolve at the tip. No committed tip run states `findings=0`.
- D3 (count): the C2 landing is said to touch "26 tools and fixtures", but `git diff --stat 7a6667c 98e5203` lists 27 files, all under `tools/` and `tests/`. 26 of them stay changed at the tip because `tools/souji-evidence-cache.py` was reverted.
- D4 (traceability nit): the C3 entry's first `source:` line still says `S223 … (placeholder id: the L1 renumbers by document)`, although S223 is the final registry id.

## Claims: re-checks

Re-measured by me over committed bytes:
- C1: binding rows by kind, the unbound ids, and that SCORECARD only grew by appending.
- C2: the landing diff scope, landing→tip changes, the cache-tool blob identity, the r15 frozen pin digests and the SKILL `../` pointers.
- C3: entry presence, the `ground: F1` count, the SOURCES row count, the S223 row and its quote, three sources re-fetched live, entry quotes against those bytes, and the record's versions and RESULT lines.

Evidence-verified only (lane instruments, not executed):
- the C1 counters v1 and v2 (`c1-after-v1.txt`, `c1-after-v2.txt`, `controls.tsv`, `controls-a0.tsv`);
- the C2 counter (`controls.tsv`, `c2-after-v1.txt`, `a2-l1-salvage-tip-measure.txt`, a2w1 `SwarmExecutor08.md`);
- the C3 counters v1 and v2 (`c3-after-v1.txt`, `c3-after-v2.txt`);
- `final-tip-measure.txt`, `m1-red-before.txt`, and the repair receipts in `a2-repairs.txt` R1-R4.

### C1 calibration: capability-count binding, 44 items: MISSED (confirmed)

- `git show <rev>:SCORECARD.md | grep -cE '^\| (N[0-9]{2}|L29) \| SCORECARD.md:[0-9]+ \|'` reads 0 at base, 38 at 9e8982b and 38 at 04b9221.
- By binding kind at the tip (the same grep with `\| [^|]+ \| <kind>:`): withdrawn 17, run 3, record 9, field 9. This equals the reported `bound_run=3 bound_record=9 bound_field=9 withdrawn=17`.
- `comm -23` of the 44 ids in `census/round-32/c1-items.tsv` at 3ec84fc against the row ids at the tip (`LC_ALL=C`) leaves `N28 N29 N30 N31 N33 N34`, all at `SCORECARD.md:422`. That is `unbound=6`, as reported.
- SCORECARD only grew: the tip bytes start with the base bytes (81245 → 98031 bytes), and `git diff -U0 base tip -- SCORECARD.md` has 0 `-` lines.
- r31 routed defect 1 (L29) is closed. Its row binds `census/round-21/remote-source-after.json expected_command_count=18 matched_command_count=18`, which is the field pair I named last round.
- The frozen target was `unbound=0 mismatches=0 withdrawn<=8` under v1 and v2 (A0). Reading `unbound=6 withdrawn=17`, the claim missed on both counts. The lane reported the miss itself, so this is an honest stop.

### C2 operability: lane-tool scratch discipline, 27 items: MISSED (confirmed)

- `git diff --stat 7a6667c 98e5203` gives 27 files, +174/−93, all in `tools/` or `tests/fixtures/`. From landing to tip only `tools/souji-evidence-cache.py` (reverted) and `tools/souji-receipt-run.py` (+`OUT-IN-GIT-TREE`) change again.
- The cache tool's blob is `82de0e07…` at both base and tip and `1578e419…` at the landing. That explains T08 failing at the tip in the committed final-tip run (`sbox=rc2 … Read-only file system`).
- Committed readings: base `items=27 pass=1 fail=26`. At the landing, attempt 1 recorded `pass=26 fail=1`; a2w1 re-measured `pass=25 fail=2` twice. At the tip the reading is `pass=24 fail=3` (T08, T12, T18). The frozen target was all 27 passing at the landing and at the tip, so the claim missed.
- The harm repairs check out over plain bytes:
  - `tests/fixtures/r15-preservation-frozen/expected.json` pins `tools/souji-census.sh` at `c1671f4c…`, which is the sha256 of the tip's file. Its `record_sha256` `eaed2811…` equals the tip record's sha256, and the verdict is `clean`.
  - `SKILL.md` carries 2 `../` pointers at 4e56c48 and 0 at the tip.
- I did not run the registered gates. The repairs rest on `a2-repairs.txt` R1-R4 and the a2w1 seat reports.
- Residuals: two LOW trailing-slash `TMPDIR` regressions. Under a `TMPDIR` ending in `/`, the census selftest has 10 false failures and the round-9 helper has 2 (a2w1 `SwarmReviewer12` findings 1-2). They are disclosed, routed, and leak nothing.

### C3 coverage: F1 abandoned-object mtime clock, F1 entries 4 → 5: VERIFIED

- `git cat-file -e <rev>:corpus/knowledge/jj-abandoned-object-mtime-clock.md`: absent at base, present at a92e1aa and at the tip.
- `git grep -l '^ground: F1' <rev> -- corpus/knowledge | wc -l` reads 4 → 5 → 5.
- SOURCES rows: `grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` reads 146 → 147, and `S223` occurs 0 → 1 times.
  - The base → tip diff changes only the S002 `used-by` cell, the S051 `used-by` cell, and the S063 anchor and `used-by` cells. That matches the lesson's touched-row log, plus the S223 append.
- `jj-mtime-clock-run.txt` carries `jj 0.45.1-7c41cdeb…` and `git version 2.56.0`, and has 22 `RESULT` lines over five arms. The rows I checked:
  - `recent/gc-default B where=cruft yes`, against `old/gc-default B where=absent no`;
  - `mixed/gc-default` gives B absent and C in cruft;
  - `never/gc-pruneexpire-never B cruft yes`;
  - `nocruft/gc-cruft-disabled` gives B absent and C loose.
- Committed counter evidence at a92e1aa and at the tip: v1 `legs=14 fail=0 f1_entries=5` and A1 v2 `legs=17 fail=0 f1_entries=5`. The base control reads `legs=14 fail=13 f1_entries=4`.
- Weakness, disclosed by the lane: a2w1 `SwarmMutationTester22` beat both counters with a constants-printing hybrid fixture. The verdict rests on the independent replays in `SwarmExecutor18` and `SwarmCritic19` plus my source checks, not on the counters alone.

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | unchanged | C1 missed (6 unbound, 17 withdrawn, against a target of 0 and ≤8). 38 honest appended rows close r31 L29, but the claim did not verify and the score stays at 7. |
| operability | unchanged | C2 missed (24 of 27 at the tip, against a target of 27). Commands honouring `TMPDIR` under a read-only `/tmp` went 1 → 24, but that is not a verified move. The landing's four gate and guard harms were repaired before close, with receipts and plain-checked pins. Two LOW trailing-slash regressions remain, disclosed and routed. I do not grade it harmed because no registered gate is left red per the committed evidence, and the residuals are false failures in an edge configuration, not lost work. |
| coverage | improved | C3 verified: F1 entries 4 → 5 and rows 146 → 147, re-measured. The base frontier line named cruft-pack reach as open. |
| depth, freshness, adjacency | unchanged | Not claimed. SCORECARD only grew by appending (0 deleted lines), and the owned scores are unchanged. |

No axis is harmed. The round is not admitted because C1 and C2 did not verify. This is an honest stop: the lane reported both misses itself.

## Discernment spot-check (`corpus/lessons/round-32.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S223 git `Documentation/gitformat-pack.adoc` v2.56.0 (new row; ≤25-word quote check) | ADMIT | https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc re-fetched live: HTTP 200, 704 lines, 27494 bytes, sha256 `ec285ba4…291381b`. This equals `census/round-32/sources/SHA256SUMS`, and `cmp` matches the snapshot. | agree | The row's quote "A cruft pack eliminates the need for storing unreachable objects in a loose state by including the per-object mtimes" is 19 words and verbatim at :655-656. The Gate quotes at :351-353 (ith value = mtime of ith object in index order), :659 and :674-675 (`.mtimes` written with the pack) are verbatim too. It is a tier-A primary doc pinned to the lane's git release. |
| `corpus/knowledge/jj-abandoned-object-mtime-clock.md` (the C3 entry) | ADMIT | S223 above; `git-gc.adoc` (sha256 `e3dbc408…`) and `config/gc.adoc` (sha256 `0ab75f6f…`) re-fetched live, both byte-identical to the snapshots; record `jj-mtime-clock-run.txt` | agree (as corrected) | Claim 1's quote "Any object with modification time newer than the `--prune` date is kept, along with everything reachable from it" is at git-gc.adoc:160-161. Claim 2's two quotes are at gc.adoc:96-99, and `--prune=now` at git-gc.adoc:84 and `--cruft is on by default` at :64-65 are verbatim. The record's recent/old pair differs only in backdating, and the cruft/absent/loose outcomes match the arms. The 15 append-only correction bullets (entry l.228+) were committed in 9da5e9a together with the lesson's admission record, so no admitted sentence is left false and unmarked. Residual nit: D4. |
| staged `git-grace-period-at-release-r35.md` | REJECT | `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/` (68 files, read in place) | agree | :30-31 holds the Gate quote verbatim. The file has `mtime` 0, `.mtimes` 0, `cruft` 0 and jj/abandon 0 hits. It documents the two expiry defaults and measures nothing. Its `source: S226` would also collide with lane ids. |
| staged `git-grace-period-semantics-r34.md` | REJECT | same package dir | agree | :52-53 holds the quote verbatim, and in that sentence it excludes object expiry from its own scope. Its sources are pinned at tag v2.45.0 (S218-S220), two releases behind the lane's git 2.56.0. |
| staged `fleet-prune-safety-r28.md` | REJECT | same package dir | agree | :43-44 holds the quote verbatim. Its mtime is a worktree registration's index file (`should_prune_worktree()`), not an object's. It has `.mtimes` 0 and `cruft` 0. |

Package sweep: `grep -rli cruft /home/vgpnk/Projects/shokuknow/merge/souji` returns 0 files, which matches the lesson's "returns 0" over the staged package.

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` printed `souji ok …/corpus/SOURCES.md` with rc 0 and 36 W04 lines, none on S223. There was no error class, which matches `census-end.txt`.

## Trend verdicts

- **expansion: improved.**
  - One entry is admitted on F1 ground the base frontier named open ("whether git's cruft-pack handling changes the mtime keeper's reach").
  - It cites the `mined` row S223, opened this round and re-fetched byte-identical by me.
  - The new edge class is where the survivor sits under cruft packing, and its per-object `.mtimes` clock.
  - Against this: the recent/old pair was already held (lane disclosure), so the gain is narrower than first stated.
- **quality: improved.**
  - r31 routed defect 2 is closed: S051 is declared and in `used-by`, S063 gains its CONFIGURATION anchor, and the `gc.recentObjectsHook` Gate quote is added (`jj-dropped-keep-object-lifetime.md:251-254`).
  - The C3 entry's overclaims were superseded append-only before its admission record.
  - The landing's four harms were repaired with receipts.
  - Against this: two LOW trailing-slash regressions and D4. No admitted entry is left false and unmarked.
- **discernment: improved.**
  - The spot-check agrees with the gate on both sampled admits and all three sampled rejects.
  - The new criteria Q70-Q74 each cite `corpus/lessons/round-32.md` as motivating evidence (a grep of each row's last cell).
  - QUALITY.md only grew by appending (0 deleted lines).
  - The lane rated itself `unchanged` because C1 and C2 missed and two counters were gamed. Under LEARNING.md's observable (gate decisions against the outside spot-check, and grounded criteria), the trend is improved.

## Routed defects (lane fixes next round)

1. C1: rebuild the enumeration per count statement (Q70). Use digit-free unit words and allow shared lines. Bind or justify N28-N31, N33 and N34 (`SCORECARD.md:422`). Re-adjudicate N25, which a2w1 `SwarmCritic04` judged a wrong withdrawal. Prove a feasibility leg before freezing.
2. C2: fix the trailing-slash `TMPDIR` regressions in `tools/souji-census.sh:1990` (canonicalise the `case` pattern) and in `tools/souji-round9-selftest.sh:7`.
   - Bring `tools/souji-evidence-cache.py` (T08) under scratch discipline together with an updated digest pin in `census/round-21/run-acceptance.py`, under Q73.
   - Move the remaining literal `/var/tmp` scripts (`r15-preservation-frozen/regenerate.py`, `r15-census-config.py`) to `TMPDIR`.
   - Replace T18's moving anchor (`baseline_mismatches`).
3. D2: commit a landing-gate run at the final tip, or state the reading as "findings=2, both the receipt's self-pointers, resolved at <tip>". Do not report `findings=0` without a run.
4. D4: drop the "placeholder id" parenthetical from the C3 entry's S223 `source:` line, as an appended correction or new revision.
5. Instrument strength: the C3 v1 and v2 counters are beatable by a constants fixture (`SwarmMutationTester22`), and the C2 predicate accepts a fabricated anchor (w1 `SwarmCritic34`). Before relying on them, add legs that execute the measured behaviour.
6. Frozen re-pin hygiene: R3 regenerated `r15-preservation-frozen` inside the round that changed the pinned tool. The verdict stayed `clean` and the arm counts were unchanged, so the re-pin is acceptable. Next time, name a re-pin as its own committed act, with before and after arm counts in the commit message.

SHONEN: four `[~]` boxes whose pointers resolve at the tip:
- `SKILL.md` gate rows and the r32 error-pattern bullet, plus S223;
- `LOG.md:362` and `LOG.md:1808` (the r32 attempt-2 entry);
- `final-tip-measure.txt` and `census/round-32/measure.sh`;
- `PROVINCE.md:238` (r32 boundary note) and a2w1 `SwarmConnector28.md`.

The boxes look checkable by a non-author, but promotion is operator-owned.
