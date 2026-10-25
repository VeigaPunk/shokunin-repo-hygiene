# CritEntryB — attack on Entry B's strongest claim (round 26, w1)

Reviewed bytes: lane HEAD `9a6e0f13b10cff82c1f6a05059779ed6c06f8a28` (master, 2026-10-25T14:37:35-03:00);
entry `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`, blob `7538d1f9cd0d458173d73c92d1ea8ba2d6427350`.
Campaign bytes were read READ-ONLY and never written or executed:
`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/fixtures/r23-trigger-prune.sh` (206 lines),
`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out`.
Lane worktree was dirty during review (`SCORECARD.md`, `corpus/lessons/round-26.md` modified by sibling seats); all quotes below are from committed bytes.

## Status

STATUS: FAIL — the reviewed entry's strongest claim, "all four commands prune (2->1)", is falsified by the campaign fixture's own case bodies (pull is never invoked; merge and rebase are confounded by a plain `git commit`), and its `verified-at:` does not distinguish "campaign measured" from "this lane measured". The review itself completed on every assigned point.

## Evidence

1. Campaign hashes match the entry's claims (so the byte-identity assertion is true, only its grammatical subject is wrong):
   `sha256sum ...` -> evidence `510722c11a97f6bca8f93e49b8a279f1f109d0222e40f675d001058768e069b4`,
   fixture `11c136aa71066733d50d226d344df9125401780aa81836f8ca9ca68a9997e65a`,
   census `1ac71c4f7199a134c204b45f339aadfc7e90c84b2d640cbed181b3577b9392fd`. All three equal the entry's `11c136aa…` / `510722c1…` / `1ac71c4f…`.
2. Evidence rows (`grep -n` on `r23-trigger-prune.out`): `:1 git_version=git version 2.56.0`, `:2 …case=fetch before=2 after=1…PASS`, `:3 …case=fetch-auto-off before=2 after=2…`, `:4 …case=pull before=2 after=1…`, `:5 …case=merge before=2 after=1…`, `:6 …case=rebase before=2 after=1…`, `:10 # provenance: produced by fixtures/r23-trigger-prune.sh on git 2.56.0`, next line `# (Arch linux x64, 2026-10-23), kernel 7.2.11-arch1-1, run 2026-10-23.`
3. `grep -n "pull" fixtures/r23-trigger-prune.sh` -> `3:`, `12:`, `144:`, `195:` only. Lines 144-147 are the whole pull arm:
   `144:    pull)` / `145:      g "$repo" remote add origin "$rem"` / `146:      g "$repo" fetch -q origin` / `147:      ;;` — no `git pull` anywhere in the 206 lines.
4. Confound: fixture `:135 before="$(count_worktrees "$repo")"` is taken before the case body; the merge body runs `:153 g "$repo" commit -qm topic` before `:155 … merge -q --no-edit topic`, and the rebase body runs `:161` (same commit) before `:163 … rebase -q topic`; `:179 after=…`. The lane's own SKILL.md:95 says that commit path prunes: "a plain `git commit` spawns `git maintenance run --auto`, whose default geometric strategy runs `worktree prune --expire 3.months.ago`".
5. Executed probe, own scratch `/var/tmp/souji-r26-CritEntryB/probe.sh` (faithful copy of the fixture's setup: init, base commit, `worktree add --detach`, commit in worktree, `rm -rf` worktree, `touch -d '4 months ago' …/worktrees/wt-N/index`; `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, `maintenance.autoDetach=false`):
   - merge body minus the merge: `before=2` -> `after-commit=1` (`worktree prune --dry-run` then empty);
   - rebase body minus the rebase: `before=2` -> `after-body-commit=1`;
   - fetch-only arm: `before=2` -> `after-fetch=1` (the one clean arm);
   - the fixture's merge shape, replayed exactly: `git merge` prints `Fast-forward` — it is a fast-forward, not a non-fast-forward merge.
6. Locators in the entry: `evidence/r23-trigger-prune.out:2-6` (entry line 26) includes `:3` (fetch-auto-off, `after=2`), which is not one of the four claimed rows; the four are `:2,:4,:5,:6`. `fixture line 149` (entry line 24) is the comment `# A real, non-fast-forward merge so the merge actually updates HEAD.` — the merge command is `:155`, and the comment is factually wrong. PROVINCE quote cited `PROVINCE.md:3` but the quoted phrase starts on `:2` (spans `:2-3`).
7. Registry/arithmetic: S129 (`corpus/SOURCES.md:150`) claim cell is "fetch, merge, rebase, am and commit each call `run_auto_maintenance`", and the Gate draft records "none in `builtin/pull.c`". Entry line 84-86 then says "five trigger commands at v2.56.0 (S129), of which four reach the prune path (S131) and one — `git pull` — … (S130)". `git pull` is not one of S129's five, and `am`/`commit` are not in S131's fixture, so no reading of that sentence is true.
8. No round-26 record of the campaign re-read exists under `census/round-26/records/` (only c1/c2/c3/c2-k4 tsvs). The "verified byte-for-byte this round" clause is attested only in prose (entry line 6, entry line 97, w1 seat reports). The only lane bytes carrying these digests outside round 26 are `census/round-24/records/slice-verdicts.tsv:5,8` and `.ufo/waves/round-22/attempt2/w1/…`; neither is "this round".

## Findings

1. **Falsified: `git pull` is never measured.** `fixtures/r23-trigger-prune.sh:144-147` runs `git fetch -q origin` under the case name `pull`; the evidence row `:4 case=pull … PASS` is therefore a second fetch run. Entry line 20-27 attributes a `2 -> 1` to `git pull` and cites that row as measurement. The only true statement available is the entry's *second* sentence (line 26-28): pull's trigger is inherited from fetch by S130's child spawn — an inference, not this evidence.
2. **Falsified: the merge and rebase rows cannot be attributed to merge/rebase.** Both case bodies run a plain `git commit` (fixture `:153`, `:161`) after the `before` count (`:135`) and before the named command. Probe item 5 shows that commit alone takes the count `2 -> 1` under this exact expiry aging, and the lane's own SKILL.md:95 says commit runs `worktree prune --expire 3.months.ago`. The PASS rows are consistent with commit-only pruning; they do not isolate the merge or rebase trigger.
3. **The merge shape is a fast-forward.** Entry line 24 says "under a real non-fast-forward `git merge` (fixture line 149)". Replaying the fixture's exact branch construction prints `Fast-forward` (probe item 5), and `:149` is a comment, not the merge (`:155`). `census/round-26/sources/git-builtin-merge.c:1690` confirms the ff path calls `finish()` (which owns the `:509` call site), so the ff/real distinction does not rescue the entry's description; the description is simply false.
4. **`verified-at:` does not honestly distinguish the two acts.** Entry line 6 reads `verified-at: 2026-10-25 — git 2.56.0; campaign evidence re-grounded by this lane (… — all verified byte-for-byte this round)`. What is verified is the *identity of the bytes*; what a front-matter scanner (QUALITY Q1's test) reads is a verification *date and version of the behavioural claim*. The campaign run date is 2026-10-23 (evidence `:10-11`), not 2026-10-25. The entry is honest only at line 61 ("The fixture was the campaign's run; this lane re-grounded it by reading the evidence bytes, not by re-executing the fixture") and at line 7 (`recheck: …` "not this lane's run"), i.e. 55 and 1 lines away from the field and the claim they qualify. Placement, not intent, is the defect: the one sentence that must be first is the one that is nearly last.
5. **The Gate is the weakest link.** Entry `## Gate` line 97 (`- ADMIT: the measured prune fixture entry; reason: fixture … re-grounded byte-for-byte this round …`) carries no location and no verbatim quote for the measured evidence, and no "campaign, not this lane" clause. The lesson Gate (`corpus/lessons/round-26.md:24-28`) says "S131 (the campaign's measured prune fixture, re-grounded byte-for-byte by sha256)" and then "S131/S132 … the lane's re-runnable gate output" — the second phrase actively misattributes ownership of the campaign's output to this lane. Neither Gate carries the located <=25-word quote the prereg requires for a cited source.
6. **Denominator sentence is internally false** (item 7): S129's five commands and S131's four cases are different sets, and pull is in neither S129 nor any clean S131 arm.
7. **Minor locator drift:** evidence `:2-6` includes the `after=2` control row `:3`; `fixture line 149` is a comment; PROVINCE quote starts at `:2`. Individually cosmetic; collectively they are why the pull/merge defects survived review — every defective statement points at a locator that does not say what the entry says.

Impacted axes: **calibration (7, lowest)** — self-report vs observed evidence, and the specific field a calibration reader scans is the dishonest one (F4/F5); **coverage (8)** — the headline is the round's coverage substance, and as written it claims four measured commands where one was never invoked and two are confounded (F1/F2); **operability (8)** — untouched by this item (no tool/test change); the entry's `recheck:` remains a runnable campaign-checkout command.

Smallest safe correction: the four text edits below, plus (L1's call) either narrowing the headline to the one isolated arm or recording this disproof as a round mistake. No counter, target, case set, or axis changes; C2's frozen counters (K1-K4) read none of the headline text, so a narrowing is stricter-only and cannot relax the claim.

## Attack log

### A. Direct answer: where the entry must say it

The entry must say, in these four places, that the run is the campaign's and the lane only read it —
(1) `verified-at:` (line 6), because that field is what a consumer/Q1 scan reads first and it currently puts a 2.56.0 verification date (2026-10-25) on a claim measured 2026-10-23;
(2) the claim paragraph itself (lines 20-28), next to the four-command sentence and its evidence pointer, not 40 lines below it;
(3) the entry's `## Gate` ADMIT bullet (line 97), with the located quote;
(4) the lesson Gate (lines 24-28), where "the lane's re-runnable gate output" must become the campaign lane's output.
It must NOT be left to line 66 or line 7 alone; those stay as corroboration.

### B. Exact wording — `verified-at:` (provenance honest, claim text otherwise unchanged)

```
verified-at: 2026-10-25 — host git 2.56.0; MEASURED IN THE CAMPAIGN, NOT BY THIS LANE: the 2 -> 1 result is the campaign's own run recorded in lanes/souji/round2/evidence/r23-trigger-prune.out (fixture lanes/souji/round2/fixtures/r23-trigger-prune.sh, git 2.56.0, kernel 7.2.11-arch1-1, run 2026-10-23); this lane verified only that those bytes are unchanged, by reading them this round (fixture sha256 11c136aa…, evidence sha256 510722c1…, census sha256 1ac71c4f…), and did not run the fixture
```

### C. Exact wording — `verified-at:` if the claim is narrowed to what the evidence supports (recommended)

```
verified-at: 2026-10-25 — host git 2.56.0; MEASURED IN THE CAMPAIGN, NOT BY THIS LANE: only the fetch 2 -> 1 arm is isolated, in lanes/souji/round2/evidence/r23-trigger-prune.out:2 (run 2026-10-23, git 2.56.0, kernel 7.2.11-arch1-1); the rows named pull (:4), merge (:5) and rebase (:6) do not measure those commands — the pull case runs git fetch (fixture :146) and the merge and rebase cases run a plain git commit after the before-count (fixture :153, :161); this lane read those bytes on 2026-10-25 (sha256 510722c1…, fixture 11c136aa…) and did not execute the fixture
```

### D. Exact wording — entry `## Gate` (replace line 97; the quote is 6 words, raw, no pipe)

```
- ADMIT — "id=SOUJI-R23-TRIGGER-fetch case=fetch before=2 after=1 expect=1 verdict=PASS" (6 words) at lanes/souji/round2/evidence/r23-trigger-prune.out:2; the campaign ran the fixture 2026-10-23 on git 2.56.0, kernel 7.2.11-arch1-1; this lane re-opened the file 2026-10-25, verified sha256 510722c1…, and did not run the fixture.
- Same-run caveat: the pull row (:4) is a git fetch (fixture :146), and the merge and rebase rows (:5-6) are preceded by a plain git commit (fixture :153, :161) that alone takes the count 2 -> 1 — so those three rows are not attributions to pull, merge or rebase.
```

### E. Exact wording — lesson Gate `corpus/lessons/round-26.md:24-28`

Replace "S131 (the campaign's measured prune fixture, re-grounded byte-for-byte by sha256)" and "S131/S132 are own-work tier A per the source registry contract: the lane's re-runnable gate output, re-run in r26 by sha256 verification rather than by re-executing the campaign fixture" with:

```
S131 (the campaign's own run, 2026-10-23 on git 2.56.0 — not this lane's execution:
lanes/souji/round2/evidence/r23-trigger-prune.out:2 — "id=SOUJI-R23-TRIGGER-fetch
case=fetch before=2 after=1 expect=1 verdict=PASS", 6 words) and S132 (...). S131/S132
are the campaign lane's own-work tier A output; this lane re-grounded them in r26 by
reading the bytes (sha256 510722c1…, 1ac71c4f…) and did not re-execute the campaign
fixture.
```

### F. Residual notes for L1 (no action taken by this seat)

- The pull, merge and rebase defects are in the campaign fixture's design, not introduced by this lane. They cannot be repaired here (campaign is read-only; the fixture must not be run from this lane). If a future round wants the claim, it needs a campaign-side re-run that (a) invokes `git pull`, and (b) removes the in-case `git commit` from the merge/rebase arms.
- The lane's S131 registry row (`corpus/SOURCES.md:152`) repeats the same defect in its scope and claim cells ("whether `git fetch`/`merge`/`rebase`/`pull` … actually prunes" / "fetch, pull, merge and rebase each take a stale worktree registration 2 to 1"). `used-by` rows are not counterpart of the entry's claim; correcting only the entry would leave the registry asserting the falsified version.
- If the headline is narrowed, the F1 README row (`corpus/README.md:39`) and the residual at `corpus/lessons/round-26.md` R-r26-1 should state that merge/rebase remain call-site-only, so F1 does not silently graduate on an unmeasured row.
- No tool was installed or upgraded for this review; no file outside this report was written; scratch `/var/tmp/souji-r26-CritEntryB` was removed after the probe (probe output is quoted above).
