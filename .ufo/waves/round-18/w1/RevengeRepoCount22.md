STATUS: DONE — the paired census contains 21 repository rows; its 22-entry `rows` arrays include the header.

# RevengeRepoCount22 — r17 “22 repos” provenance

Axis examined: **calibration**. No census/runtime was run.

## Reconstructed finding

`SCORECARD.md:15` says “live fleet paired rows identical (22 repos).” The phrase was introduced on that line by commit `d98065d` (the round-17 lesson/scorecard commit). The paired-run artifact does **not** contain 22 repository rows: in `census/round-17/live-fleet.json:11-21`, `rows` begins with a seven-field header array (`"repo"`, `"worktrees"`, …), followed by repository records. A JSON projection of both arm lengths gives 22 entries; removing the first/header entry gives 21 data rows. The 21 repo paths in the r16 array are immediate `*-shokunin` children and do not include the root `/home/vgpnk/Projects/shokunin`.

The live artifact records its root and command at `census/round-17/live-fleet.json:2-4`: root `/home/vgpnk/Projects/shokunin`, command `TMPDIR=/var/tmp bash <arm>.sh --root /home/vgpnk/Projects/shokunin`. Its row shape therefore explains an exact “22” if array entries were counted, but that count includes the header, not 22 repos.

The r17 seat report with a separate explicit 22 is `.ufo/waves/round-17/w1/ScoutFleetInfoAttrs.md:18,20-24,81`. Its inventory lists the fleet-root repo (`:28`) plus 21 child repos (`:29-50`), for 22 main gitdirs. That is a filesystem/gitdir inventory including the root, not the paired census's 21 output rows. The report itself says at `:18` that `INCLUDE_ROOT=1` is required and defaults to 0, then says the fleet-root census covers its 22 measured repos; that sentence does not match the default census row set. Thus the evidence supports two possible routes to the scorecard's number—counting the JSON header or reusing the scout's root-inclusive inventory—but does not record which the scorecard author used. The scorecard wording specifically describes paired rows, for which the header-inclusive array length is the direct match.

`RerunMatrixLanded.md:23-31,43-45,77-79` is not the source of this number: it reruns the fixture matrix and reports 232 case verdicts, not fleet repository rows.

**Verdict: fails as a repository count.** There are 21 repository data rows; “22 repos” counts either the paired artifact's header or the extra fleet-root gitdir in the separate scout inventory. Confidence: high on the 21-row result and header; medium on which source the scorecard author used, because the scorecard commit does not bind the number to a source.

**Smallest fix:** change `SCORECARD.md:15` to “live fleet paired rows identical (21 repos; header excluded).” If retaining the scout inventory's separate count, describe it as 22 main gitdirs including the fleet root, not 22 paired census rows.

## Evidence commands and outputs

Command:
```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %s' -S '22 repos' -- SCORECARD.md
```
Output:
```text
d98065d round-17: lesson, knowledge entry jj-colocation-receipts, SOURCES S051-S063, QUALITY Q27/Q28, SKILL/PROVINCE/README jj rules + registry rows, SCORECARD, LOG (D3 corrections + round entry), verify selftest locals
```
The unscoped history command was also run:
```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -S '22 repos' --oneline
```
Output:
```text
b576341 round-17 verifier spot-check (integrator, hyaku): non-author admit/reject
d98065d round-17: lesson, knowledge entry jj-colocation-receipts, SOURCES S051-S063, QUALITY Q27/Q28, SKILL/PROVINCE/README jj rules + registry rows, SCORECARD, LOG (D3 corrections + round entry), verify selftest locals
95519a7 round-17: wave specs/dispatch/registries and seat reports (w1 78, w2 71), landed-rev evidence (matrix, replays, jj fixture, live fleet), stub quarantine receipt
58ace9f round-15 verifier spot-check (integrator, hyaku): non-author admit/reject
d7266c5 round-12: QUALITY bar + mistakes ledger (C1), SOURCES registry + 5 frontier entries (C2), maintenance-guard gate + guarded commit checklist (C3)
43d5754 round-11: closed — census contract fixed (36/36, last r9 class closed); certification NOT granted (certifier evidence-integrity defects)
ad8b670 sweep: commit seat-result fragments; drop embedded fixture fleet (regenerable junk)
b5db5cf round-6: REJECTED as a round (2/3 claims) — parent completed C1/O1 (unpushed-touching fix, census tool, docs reconcile), K1 honest stop; dissent preserved
```

`git show --format=fuller --no-ext-diff d98065d -- SCORECARD.md` shows the added operability row containing “live fleet paired rows identical (22 repos)” (`SCORECARD.md:15`). The scoped history output above identifies the commit introducing the phrase.

Read-only JSON projection of `census/round-17/live-fleet.json`:
```text
Filter: `{r16:(.arms.r16.rows|length),changed:(.arms.changed.rows|length),first:(.arms.r16.rows[0]),repo_rows:(.arms.r16.rows[1:]|length)}`
Output: `{"r16":22,"changed":22,"first":["repo","worktrees","unpushed","dirty","scratch_bytes","mtime_iso","verdict_flags"],"repo_rows":21}`
```
The repo identities projection of `r16.rows[1:]` returns 21 paths, from `audio-shokunin` through `tsukuroi-shokunin`; no root-repository path is present.

No tools installed or upgraded.