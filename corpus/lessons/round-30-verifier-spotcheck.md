author: hyaku closure (non-author integrator, @m_opus)

# Souji round 30: non-author closure spot-check

Lane base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` → tip `2726c3d819a025dd2c193a5c780645d7fb71319a` (branch `master`).
Report `.ufo/reports/round-30/souji.md`; prompt `.ufo/prompts/souji-round-30.md`.
Driver digest (copied from mutable `.ufo/watchdog.log`):

- `2026-10-26T01:12:04-03:00 launch souji round=30 pgid=115880 driver=hyaku-inline attempt=1`
- `2026-10-26T02:49:22-03:00 complete souji round=30; hyaku-inline attempt=1`

All re-measurements below ran on 2026-10-26 at about 05:50 UTC. They read committed bytes only (`git show`/`cat-file`/`ls-tree`/`grep` at the
named revision). The lane worktree was clean (`tracked=0 untracked=0`). I executed no lane gate, counter, fixture or probe, so
lane-owned instruments are evidence-verified only. External sources were re-fetched live with `urllib` (HTTP 200) and hashed.

## Step-1 conformance

| check | command | observed |
|---|---|---|
| report landed by lane | `git log --format='%an <%ae> %H %cI' -- .ufo/reports/round-30/souji.md` (fleet) | `souji-shokunin <souji@shokunin.local> 3c361e87917bc6582fe508705554eab2e90a883f 2026-10-26T02:48:56-03:00`. This is after the cited lane HEAD 2726c3d (02:47:24) and before the complete line. The commit touches only the report (+142). |
| prompt committed | same command, prompt path | `souji-shokunin 1cb652056562c40f2a2dd864e81ee210fc0c427b` (01:12:03, before launch) |
| SHONEN heading | `grep -n '^## SHONEN'` on the report; `git show 2726c3d:SHONEN.md \| grep -c '^- \['` | heading at l.119. SHONEN.md has four boxes and the report has four `[~]` lines, each with a pointer. SHONEN.md is byte-identical at base and tip. |
| cited commits exist + ancestry | `git cat-file -t <h>`; `git merge-base --is-ancestor <h> refs/heads/master` for all 14 cited full hashes (9420341, d4928ec, bae103c, df6afe8, 02aea48, 7b16731, 68447af, aea0525, 76c94eb, 936efc8, 9dcd367, f732978, 393b011, 2726c3d) | all are `commit` and all are ancestors of `master`. The 13 commits in `9420341..2726c3d` are all authored `souji-shokunin <souji@shokunin.local>`. |
| pushed, no leftovers | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `local=remote=2726c3d… ahead=0 behind=0 head=detached tracked=0 untracked=0`; empty; `2726c3d…` |
| prompt contract | read prompt §1–§5 | MISSION/AXES binding (l.3–7); 1–3 claims plus the lowest axis (l.9–40); frontier step §2b (l.42–78); L2 batched floor of 8 (l.80–97); report path and required sections incl. SHONEN (l.99–129); commit-then-push, push scope and L0 channel (l.131–140); write scope and report-lands-last (§6 l.341–414) |
| wave seats | `jq` over `census/round-30/waves/w{1,2}-results.json` at tip | w1 35 seats / 35 results / 35 non-empty `output`; w2 34/34/34. That makes 69 seats and 0 dead, matching the report. `manifest.sha256` has 425 lines. |

Step-1 defects: none found. Every routed r29 item the round could close was closed. D1: the cited final-tip receipt (2726c3d) landed before the
report. D2: a cross-domain line is present (report l.128). D3 landed at df6afe8. D4 landed at 936efc8. Item 4 (landing gate) was the C2 subject.

## Claims: re-checks

Re-measured by me over committed bytes:
- C1: the correction-line count, the append-only prefix, and the row-id cross-match.
- C3: entry presence, the `ground: F1` count, row counts and rows, the run-record shape, and the README map row at the landing commit.
- C2: the kill-rule fact (landing-commit pointer and capture absence).

Evidence-verified only (lane instruments, not executed):
- The C1 counter's rc/observed values (`c1-before.txt`, `c1-after-v1.txt`, `c1-after-a3.txt`, `final-tip-measure.txt`).
- The C2 gate, fixture, red-arm and regress legs (`c2-after-v1.txt`, `c2-after-v2.txt`, `final-tip-measure.txt`).
- The C3 counter legs and the jj fixture replay (`c3-after-v{1,2}.txt`).
- The M1 red-before receipt.

`git diff --stat 393b011 2726c3d` adds only `census/round-30/records/final-tip-measure.txt` (+38), so the receipt's revision 393b011 grades the
same tree as the tip apart from that receipt.

### C1 calibration: capability-row literals 13 → 0: VERIFIED

- `git show <rev>:SCORECARD.md | grep -c 'R30-CORRECTION SCORECARD.md:'` reads 0 at 9420341, 13 at 7b16731 and 13 at 2726c3d.
- `SCORECARD.md` at tip begins with its base bytes: `startswith(base)=True`, 54403 → 61956 bytes. `git diff -U0 9420341 2726c3d -- SCORECARD.md` has no `-` line.
- The 13 correction row ids (R03 R04 R05 R06 R07 R08 R09 R10 R11 R14 R15 R16 R18) are exactly the 13 `MISMATCH` rows of `c1-before.txt`
  (`SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10`). Each correction's `rc`/`observed` equals that row's base observation.
  The one exception is R16, which carries `cmd=` with the row's own script plus the required `--tool`; the prereg K1 grammar allows that.
- Committed after-records: `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10` at 7b16731 under v1 and A3, and at 393b011 (final-tip receipt).
  The prereg target held at the landing commit and at the tip.
- Caveats, all disclosed by the lane:
  - R18's correction records a v1 stdout+stderr usage banner. `SCORECARD.md:338` marks it, and A3 reads R18 as `MATCH` on stdout.
  - The capability cells themselves still carry the old literals, with the observed state appended beside them.

### C2 operability: committed-capture report discovery: MISSED (confirmed)

- The prereg kill rule needs `dangling=0` at the C2 landing commit **and** at the tip. `c2-after-v1.txt` at 68447af reads
  `SUMMARY reports=86 cne=0 dangling=1 other=7 fixture=ok redarm=ok regress=same`, rc=1.
- Plain re-derivation of the cause: `git grep deliver-c1-literal-history 68447af -- SCORECARD.md` hits `SCORECARD.md:322`, while
  `git ls-tree -r --name-only 68447af | grep -c '^census/round-30/waves/'` is 0. The pointer could not resolve at that commit.
- The 86 matches `git ls-tree -r --name-only 9420341 census/round-29/waves | grep -c '\.md$'` = 86.
- At the tip, the receipt reads `dangling=0 other=0`, fixture `cases=7 pass=7`, and redarm base `pass=3`. Under the frozen rule the claim is still missed.
- No harm: `--selftest` and `tests/fixtures/r16-landing-gate.py` keep identical (rc, last line) for the base and revised gate. A1's
  `regress_full=differs` comes from A1's own regex expecting a tab where the selftest prints a space (lesson Mistakes, stale-premise row).
- `git diff --stat 9420341 68447af -- tools/ tests/` shows that C2 touched only `tools/souji-landing-gate.py` (+58/−5) and added its fixture.

### C3 coverage: F1 keep-ref expiry entry, F1 entries 2 → 3: VERIFIED

- `git cat-file -e <rev>:corpus/knowledge/jj-keep-ref-expiry.md` gives rc 128 at base and 0 at tip.
- `git grep -l '^ground: F1' <rev> -- corpus/knowledge | wc -l` reads 2 → 3.
- SOURCES rows: `grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` reads 143 → 145 (S220, S221 new, `mined`, opened 2026-10-26).
  S054 and S063 changed only `used-by`, matching the lesson's touched-row log.
- The entry opens with `source:` (S220/S054/S221/S063), then `verified-at:`, `recheck:` and `ground: F1`.
- `jj-keep-expiry-run.txt` carries `jj-version: jj 0.45.1-7c41cdeb…` and 8 `RESULT` lines (the prereg asks for ≥3).
- The README F1 map row (`:39`) names the entry at the landing commit 76c94eb.
- Correction sweep: the five wave-2-refuted phrasings (`later prune can drop`, `Steps 4, 5 and 8`, `precondition`, `not of git`,
  `no lane action requests`) occur only inside the entry, each with its appended `supersedes` line. No sibling file repeats them.

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | improved | C1: 13 → 0 re-measured; the stale literals now carry the observed state, append-only |
| operability | unchanged | C2 missed by its frozen kill rule at the landing commit. The gate change harms no fixture (selftest 65/65 and r16 15/15 identical). The score stays 8. |
| coverage | improved | C3: F1 entries 2 → 3 and rows 143 → 145, re-measured |
| depth, freshness, adjacency | unchanged | Not claimed. The SCORECARD diff is append-only (+41 −0) and the owned scores 7/8/8 are unchanged. The only deletion in README/SKILL/QUALITY/SOURCES is the in-place F1 map row plus the two `used-by` cells. |

No axis is harmed. The round is not admitted because C2 did not verify (honest stop: the lane reported the miss itself).

## Discernment spot-check (`corpus/lessons/round-30.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S220 jj CLI reference v0.45.1 (new row) | ADMIT | https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap, 154561 bytes, sha256 `b3306943…9a7333554` (= `SHA256SUMS` pin) | agree | Every quote is verbatim at its line: :2415 "To discard old operation history, use `jj op abandon ..<operation ID>`."; :3791; :3801 "By default, only obsolete objects and operations older than 2 weeks are pruned."; :3803 "Only the string "now" can be passed to this parameter." (each ≤25 words). Tier A docs at the pinned tag is right, and the scope cell keeps the code path in S054. |
| S221 jj docs/operation-log.md v0.45.1 (new row; ≤25-word quote check) | ADMIT | https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/operation-log.md, 3334 bytes, sha256 `2a48dab8…209ce18` (= pin) | agree | :8-9 "The view contains information about where each bookmark, tag, and Git ref (in Git-backed repos) pointed" is verbatim and 17 words. The row's claim that `abandon` does not occur is true (count 0). The entry's original range "lines 5-8" was corrected append-only to 5-9. |
| `corpus/knowledge/jj-keep-ref-expiry.md` | ADMIT | S054 `lib/src/git_backend.rs` at v0.45.1 sha256 `95147270…13d86c69` (= pin), :99-100, :900-901, :929-944, :977, :1558-1564; record `jj-keep-expiry-run.txt` | agree (as corrected) | The headline holds: step 3 `git gc --prune=now` leaves the target keep ref in place (8, yes), and step 4 `jj util gc --expire=now` removes it (6, no). `recreate_no_gc_refs` (:900-901) is the only remover. At its landing commit 76c94eb the entry carried five sentences stronger than its record. They were superseded in-file at f732978, before the lesson's admission record (393b011), so the admitted text is no longer false and unmarked. The SKILL headline still omits the packed-ref caveat (routed below). |
| staged `prune-expiry-behaviour-r29.md` | REJECT | `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/prune-expiry-behaviour-r29.md` (read-only) | agree | :11-12 quote verbatim ("Round 8 read the levers out of git's manuals: `gc.worktreePruneExpire` sets the grace period"). `grep -iE 'jj\|keep'` hits only the `ground:` line. The entry is about worktree-registration expiry, not keep refs. |
| staged `git-grace-period-at-release-r35.md` | REJECT | same package dir | agree | :30-31 quote verbatim (`gc.pruneExpire` defaults to **2 weeks**, unreachable loose objects). There is no jj mention (`grep -iE 'jj\|refs/jj'` returns 0 lines). Reading git's 2-week object default as jj's threshold is exactly the conflation the entry guards against. |
| loose-ref mtime check as an expiry guarantee (entry `## Gate`) | REJECT | S054 git_backend.rs :929-944 | agree | The source comment reads "Check timestamp of loose ref, but this is still racy on re-import" and "existing packed ref won't be demoted to loose ref". The mtime gate applies only when `loose_ref_path.metadata()` succeeds. |

Package sweep: `grep -rlE 'refs/jj|jj util|jj op' …/merge/souji/knowledge/corpus/knowledge/` returns only `fleet-prune-safety-r28.md`, which is not an F1
keep-ref candidate. No staged keep-ref entry was missed.

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` printed `souji ok …/corpus/SOURCES.md` with rc 0 and 36 W04
(duplicate URL across scopes; S220/S221 add none). There was no error class, which matches `census-end.txt`.

## Trend verdicts

- **expansion: improved.** One admitted entry lands on F1 ground that the map listed as unmeasured (`corpus/README.md:46` at base). Its `source:`
  cites the `mined` rows S220/S221 opened this round. Two capability rows are demonstrated running at the tip (`final-tip-measure.txt`
  C1 A3, C2 v1 fixture 7/7).
- Against expansion: the entry shipped five overstated sentences at 76c94eb, and SwarmCritic18 found that 10 of 18 propositions restate held text.
  The corrections landed before the admission record, and the measured removal lever is new.
- **quality: improved.**
  - 13 stale capability literals now carry their observed output, append-only.
  - The seven uncarried r29 seat failures are carried, shown able to fail by the M1 receipt: `findings=7` rc 1 → `findings=0` rc 0.
  - The r29 D3/D4 corrections landed.
  - The refuted entry sentences are superseded in-file.
- Against quality: the SKILL keep-ref bullet still says "jj's own gc threshold" without the packed-ref caveat. This is an imprecision, not a false
  unmarked entry.
- **discernment: improved.** The spot-check agrees with the gate on all three admits and on all three sampled rejects. Q63–Q66 each
  cite lesson evidence (Findings/Mistakes).

## Routed defects (lane fixes next round)

1. SKILL.md:115 keep-ref bullet: add the packed-ref caveat recorded in the entry's wave-2 corrections. A keep ref packed by `git gc`/`pack-refs` is removed by
   a default-threshold `jj util gc`, so the threshold is not what the fixture discriminates. Also align "leaves two keep refs where eight stood" with
   the record (step 5 goes 6 → 2).
2. Capability cells R03–R18 still state the old literals. If calibration is to read from the cells alone, supersede them in a dated row rather than
   leaving correctness only in the R30-CORRECTION block (lane-planned r31 enumeration widening covers SCORECARD.md:164/:168).
3. A1 `c2-counter-v2.py:69` regex expects `\terr=` while the selftest prints ` err=`, so REGRESS-FULL cannot pass as committed. Fix the regex or retire the leg
   (lane residual).
4. Landing-gate discovery precedence: a force-added `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv` is now tracked in the lane repo.
   Pin that a non-`.md` force-add under `.ufo/waves/round-N/` never hides the committed capture (lane residual "discovery precedence").
5. Q65 recurrence: the round re-committed r29's D1 class (citing a wave path before its capture landed), and that is what sank C2. Run the landing
   gate at every record-landing commit before the next commit, not only at the tip.

SHONEN: four `[~]` boxes whose pointers resolve at tip. LOG.md:362 is the 2026-10-19 operator-sweep entry, PROVINCE.md:195 is the r30 boundary note,
and w2 SwarmConnector31 reads "zero contested-scope findings". Box 3 now has committed green fixture output (D3 closed). The boxes look checkable by
a non-author, but promotion is operator-owned.
