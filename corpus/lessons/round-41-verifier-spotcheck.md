# Round 41 — non-author verifier spot-check (souji)

author: hyaku closure (non-author integrator, @m_zfl)

Measured revision: lane tip `0c9581a44a2eaa7350b4699e64dcdfbe07fec0d5` (base `7eebc183f2685d1ea9b004b4de22c09a8a4035a7`).
Inputs: fleet report `.ufo/reports/round-41/souji.md` (fleet commit `a1f0c405fc62ccb2d6daaa7c77de46331805337f`), prompt
`.ufo/prompts/souji-round-41.md`. Driver digest (`.ufo/watchdog.log`, mutable):
`2026-10-28T18:37:47-03:00 launch souji round=41 pgid=3244729 driver=hyaku-inline attempt=1` /
`2026-10-28T20:36:51-03:00 complete souji round=41; hyaku-inline attempt=1`.
Everything below was run by the integrator against committed bytes; scratch lived under `/tmp/closure-s41.*` (no lane write).

## 1. Conformance (step 1)

| check | command / observation | result |
|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-41/souji.md` (fleet) -> `souji-shokunin a1f0c405…` | ok |
| `SHONEN` heading, one line per box | report § SHONEN: four boxes, each `[~]` with a pointer | ok (no `[x]`) |
| cited lane commits exist and are ancestors of `master` | 16 distinct 40-hex hashes in the report; `git merge-base --is-ancestor <h> master` -> 15 ok; the 16th (`9bcf1f95…`) is the cited fleet commit for the L0 line, present in the fleet repo | ok |
| lane pushed, nothing uncommitted | `jj-lane.sh state` -> `ahead=0 behind=0 tracked=0 untracked=0`; `git status --porcelain` empty; `git ls-remote origin refs/heads/master` -> `0c9581a4…` | ok |
| prompt carries the template contract | prompt has the 1–3 claims / lowest-axis clause (l.11-15), report contract incl. SHONEN + hash rule (l.106-118), write scope (l.430), commit order and push scope (l.131-137, 444+), L0 channel (l.138), L2 minimum (l.82) | ok |
| freeze order | freeze commit `e2a74312…` (committer 18:54:12) precedes `w1-spec.json` (18:57:58) and `w1-dispatch.json` (18:58:04); `a114412` (C3) was landed at 20:07:59 committer time, after the freeze | ok |
| frozen instruments unchanged | sha256 of `c1/c2/c3/r1-counter.py`, `c1-items.tsv`, `c2-cases.tsv`, `c3-sites.tsv` at the tip equal the digests in `census/round-41/preregistration.txt`; `git diff 6682b98 0c9581a -- census/round-41/*.py census/round-41/*.tsv tools/souji-worktree-drift.py` is empty; drift tool sha256 `b2a603cf…4dc6` as pinned | ok |

Defects (status-neutral): (a) the C2 tool was changed after landing (three hardening commits; lesson E1) — disclosed by the lane, counter and
population untouched; (b) `tools/souji-freeze-check.py` has no `--selftest` flag; its registry row (SKILL.md:282) names the committed
counter `c2-counter.py`/row `r41-freeze-check-cases` as the self-test arm, which satisfies §Gate standard "Self-test" only through the lane-owned
counter, not a self-invocation flag — note, not a failure; (c) `tools/souji-landing-gate.py --round 41` at the tip prints 3 `LG-DANGLING-PTR`
(`corpus/README.md:217` ×2, `corpus/knowledge/jj-colocation-receipts.md:148`, all pointing into `.ufo/waves/hyaku/jj-w1/…`); the same three findings
print at base `7eebc18` with `--round 40`, so they are pre-existing, not round-41 harm.

## 2. Claim re-checks (step 2)

Method: `python3 -B census/round-41/<c>-counter.py --root . --rev 0c9581a44a2eaa7350b4699e64dcdfbe07fec0d5 [--scratch DIR]` run by the integrator over
committed bytes (these are the lane's frozen claim counters over a committed revision, not a gate of a sibling lane). "Re-measured" = I ran the
counting command and compared; "evidence-verified" = I read the committed receipt only.

| claim | before (re-derived) | after (observed at tip) | status |
|---|---|---|---|
| C1 calibration | `c1-counter.py --rev 7eebc18…` -> `REFUSAL COULD-NOT-EVALUATE: items table absent` (artifact absent at base); lane's do-nothing control `corrected=0 uncorrected=3`, junk lesson `junk=3` (`controls/c1-control.txt`, evidence-verified) | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` rc 0 | **re-measured**, matches report |
| C2 operability | `c2-counter.py --rev 7eebc18…` -> `PRISTINE FAIL TOOL-ABSENT … SUMMARY cases=21 pass=0 fail=21` | `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=8131847bcfc5` | **re-measured**, matches |
| C3 coverage | `c3-counter.py --rev 7eebc18…` -> `REFUSAL COULD-NOT-EVALUATE: tool or sites table absent` (fixture absent); always-PASS stub `survived 19/19` (`controls/c3-control.txt`, evidence-verified) | `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok` | **re-measured**, matches |
| R1 (residual, not a claim) | base drift tool sha256 `e48ed08e…` differs from the pin `b2a603cf…` (TOTAL repair absent) | `SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12` | **re-measured**, matches |

Substance probes I ran beyond the counters (the lane itself names these as limits N1-N16; I record what a non-author sees):

* **C1 values re-derived by hand at `bffcc0f660ff36eb8add3f61582748a7af019a5b`:** I1 `grep -E '^\| S[0-9]+ ' corpus/SOURCES.md | grep -c 'worktree\.c'` -> 2 (S009, S033), `grep -c 'v2\.56\.0/worktree\.c'` -> 0, 181 rows; I3 `register_cells=6` (`c1-before.txt`) vs `register_cells=3` (`c1-after-h.txt`); I4 zero occurrences of `flagged as potentially` in the 136 files under `census/round-40/waves/`, while `LOG.md:1909` at `bffcc0f` does carry the "Invalid prompt" text (so the lane's scope prose is correct, and the line alone would mislead — the lane says so in M41-4). All three CORRECTION lines carry values that I reproduced. The I1 prose "wrong by any reading" was retracted in E2 by the lane.
* **C2 tool attacked in a scratch clone:** (i) real prereg at tip -> `SUMMARY claims=3 findings=0`, rc 0; r40 prereg -> red (`FIELD-MISSING Round/Base/…`); (ii) flipped one hex digit in a stated Population digest and a Counter digest -> `POPULATION-DIGEST` and `COUNTER-DIGEST` findings, rc 1; (iii) appended a byte to the frozen `c3-counter.py` after freeze -> `FROZEN-EDITED`, rc 1. The tool really reads digests and the freeze order; it is a runnable replacement for the prose rule.
* **C3 fixture mutated by me (condition level, not label):** `st_nlink > 1` -> `> 2` kills P17; `total["regs"] != sum` -> `<` kills P08; `total["repos"] != len(rows)` -> `>` **survives** the 21 probes (passes 21/21). This confirms lesson N14: the battery is class-level; the claim's own predicate (label rewrite turns exactly the mapped probes red) holds and is re-measured.
* **SCORECARD diff** (`git diff 7eebc18 0c9581a -- SCORECARD.md`): append-only, 24 added lines, scores unchanged (calibration 7, operability 8, coverage 8), no prior row edited; four capability rows appended, each with a pointer to a committed receipt that exists. Registry diff `corpus/SOURCES.md`: 4 insertions, 0 deletions (pure append).
* **Gate evidence:** registry rows for `souji-freeze-check`, `r41-freeze-check-cases`, `r41-refusal-sites`, `r41-drift-record-order`, `r41-c1-corrections` exist at SKILL.md:282-286 with exit-code maps; frozen-run receipts `census/round-41/records/tip-remeasure.txt` (measured at `716eaa9`, docs-only difference to the tip) all rc=0 and equal my own tip run (evidence-verified + re-measured).

Axis verdicts (every claim verified on its frozen counter; no owned axis harmed; lane's disclosed substance caveats kept):

| axis | claim | verdict | reason |
|---|---|---|---|
| calibration | C1 | **improved** | three filed r40 statements shown false/overstated by independent re-derivation; append-only CORRECTION lines carry values I reproduced; the lane then corrected nine misstatements in its own lesson (E2) append-only |
| operability | C2 | **improved** | a runnable tool replaces a prose rule; absent at base, 21/21 at tip, and my three scratch attacks are detected. First-landing receipt (`119c26f`) and hardened final (`72e8a0b`) both 21/21; the post-landing hardening is disclosed (E1) and the final bytes are the measured ones |
| coverage | C3 | **improved** | fixture absent at base; 19 sites / 21 probes re-measured killed-by-label; caveat N14: a condition-level mutant of mine survives, so coverage is of refusal classes, not conditions |
| (owned axes depth, freshness, adjacency) | — | **unchanged** | no scorecard score or surface changed; no harm found (59/61 gate rows identical per N19; landing-gate findings identical at base and tip) |

## 3. Discernment spot-check (step 3)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S258 git v2.56.0 `builtin/worktree.c` | admit (tier A, mined) | `curl https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c` -> HTTP 200, 1541 lines, sha256 `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc` (equals `census/round-41/sources/SHA256SUMS`); `grep -n -F 'prune missing working trees older than <time>'` -> line 255; line 229 `should_prune_worktree(the_repository, …)`, line 259 `expire = TIME_MAX;` | **agree** | primary upstream source, bytes pinned, the quote (7 words) is verbatim at the cited line; the row is a pure append; a v2.56.0 pin of the builtin half was not held before (S009 is at v2.55.0) |
| staged `fleet-prune-safety-r28.md` (staged S160) not adopted; r40 reject reason "worktree.c appears in 9 rows" re-decided | reject (outcome) / reason replaced | `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/fleet-prune-safety-r28.md` (header: 26 prunable registrations, run 2026-10-24) vs lane `corpus/knowledge/fleet-prune-numerator-r35.md` (27 registrations, 0 prunable, run 2026-10-28); `git grep` count at `bffcc0f` -> 2 rows contain `worktree.c`, 0 at v2.56.0 | **agree with the outcome; disagree that the lesson states the reason** | the r40 "9 rows" ground is falsified (I reproduced 2 and 0). Not adopting is right on other ground the lesson does not name: the staged entry's fleet figure (26 prunable, 2026-10-24) is superseded by the lane's own newer census (0 prunable, 2026-10-28). The lesson's "admit-by-reopening, staged item stays unadopted" is correct in outcome but leaves no positive reject reason |
| F1 frontier promotion (not promoted) | reject | lesson § Gate (S009 library `worktree.c` recheck still open) | agree | consistent with S258's own scope note (`should_prune_worktree()` library half not read) |

Newly written `corpus/SOURCES.md` row re-opened: **S258** (above). Quote ≤25 words and verbatim at `:255`; snapshot sha256 and the v2.55.0 diff claim (:171-266 differ only at :229) stand as stated by the lane (I re-fetched v2.56.0 only; the v2.55.0 hash is recorded in `SHA256SUMS`, evidence-verified).
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` -> `souji ok`, rc 0, 52 W04 duplicate-url warnings (report: 52 -> 52).

## 4. Trend verdicts (LEARNING.md)

| trend | verdict | evidence |
|---|---|---|
| expansion | **unchanged** | one tier-A row (S258) on held F1 ground; no new `knowledge/` entry; no coverage-map ground promoted; one capability set (4 rows) entered SCORECARD with receipts — instrument capability, not domain ground |
| quality | **improved** | falsified filed claims (I1/I3/I4) corrected append-only with reproducible values; nine lesson misstatements and a transposed S258 hash caught and corrected; Q98-Q102 added each citing a lesson; no admitted entry found failing its re-check |
| discernment | **improved** | my spot-check agrees with the gate on the admit (S258) and on the not-adopt outcome; the r40 spot-check's disagreement (R40-D-PRUNE) became lesson M41/Q98 with a reproducible-count criterion. Lane graded this `unprovable-but-better` pending a non-author check; the non-author check is now on record |

## 5. Routed defects (the lane fixes next round)

* **R41-D-REJECT-REASON:** state the positive ground for leaving staged `fleet-prune-safety-r28.md` unadopted (staged 2026-10-24 26-prunable figure superseded by `fleet-prune-numerator-r35.md`), appended to the round-41 gate, not rewritten.
* **R41-D-C3-CONDITION:** N14 stands; the survivor `total["repos"] != len(rows)` -> `>` (my mutant) joins the r42 condition-level mutant set; confirm which older drift fixture kills it.
* **R41-D-C2-SELFTEST:** give `tools/souji-freeze-check.py` a self-invocation mode or record in the registry row that the counter arm is the self-test (Gate standard "Self-test"); status-neutral.
* **R41-D-LG-DANGLING:** the three `LG-DANGLING-PTR` findings (`corpus/README.md:217`, `corpus/knowledge/jj-colocation-receipts.md:148`) pre-date round 41; repoint or mark them.
* **Carried from lane (N1-N19, N10 `--json` leaf symlink, N11 `K1 cited-no-row S146`):** accepted as the lane's own routed items; none narrows a claim.
* SHONEN boxes: all four are `[~]` with pointers; none is fully checkable by a non-author from this round alone (instrument work only, no end-to-end domain task with deletion authority). Operator note: nothing to promote.

## 6. Verdict

Every claim re-measured on the frozen counters at the tip (C1, C2, C3 plus residual R1), no owned axis harmed, substance caveats are disclosed and reproduced
by me (C3 class-level; C2 hardened after landing). Round 41: **admitted**.
