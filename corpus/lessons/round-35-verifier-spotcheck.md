# Round 35 — non-author verifier spot-check

author: hyaku closure (non-author integrator, @m_opus)

## Closure decision

The lane report is a substantive partial report tied to committed work, not a marker: it names work, receipts, and pushed lane commit `01dc784134ac03bf04db280383d0c70c39ac4837`. Status is therefore `ok` under the marker rule, despite contract defects. Admission is **rejected-honest-stop**: frozen C1 and C2 targets remain unresolved, so the round does not qualify as admitted. The lane's claim/evidence omissions are not converted into fabricated passes.

## Step-1 conformance

- Report `.ufo/reports/round-35/souji.md` is committed by `souji-shokunin` (`git log --format='%an %H' -- .ufo/reports/round-35/souji.md`: `souji-shokunin fca0f3f0ea81a9a28041ce76d50a761602ea093f`). It has `## SHONEN` and correctly reports no checklist mutation; the heading explicitly says unchanged, but does not provide one line per checklist box as the contract requires (defect).
- Every lane commit cited in the report exists and is an ancestor of `refs/heads/master`: `1e9cad0b553891c41fe5b7ad1686decc147d76d4`, `d1c940414087b606503662e4d115f51cb0fba40c`, `4e9c295e9339cc2b13f7a0dd5ec9fc8213a9e18e`, `8788d5565f9e1cbc8cd6e4fe84222b5d6483612c`, `fedfa4068801164ac2e189029137ebe87a1d94d3`, and `01dc784134ac03bf04db280383d0c70c39ac4837`. Command: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e <hash>^{commit}` and `git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor <hash> refs/heads/master`; all six returned 0.
- The report commit is by the lane identity (`01dc784...`: author/committer `souji-shokunin <souji@shokunin.local>`). Its report-path commit is `fca0f3f0ea81a9a28041ce76d50a761602ea093f`, also by the lane identity.
- `jj-lane.sh state ...`: `branch=master local=01dc784... remote=01dc784... ahead=0 behind=0 head=detached tracked=1 untracked=1`; `ls-remote origin refs/heads/master` returned the same `01dc784...`. However `git status --porcelain` shows post-tip leftovers ` M SCORECARD.md` and `?? census/round-35/records/prune-census-corrected.tsv`. Left untouched; they are not part of the pushed round. Required clean-worktree condition fails (status-neutral conformance defect; origin/HEAD remains synchronized).
- The dispatched prompt contains the core claims/frontier/report/SHONEN/commit/write-scope contract. Its campaign addendum is internally stale: it contains the 32–128/64–128 policy and an older run-7 recipe, while the current run-10 directive requires 64–128 total seats; the report records a 40-seat W1 and no W2. Record as a dispatch/report conformance defect, not a basis to erase the real report.
- Report defects: missing required ordered `Work performed`, `Landed changes`, `Before → after measurements`, `Sources & frontier`, `Trend verdicts`, and `Stale-lane` sections; its `SHONEN` heading has no checklist line per box. It is nevertheless substantive, with resolvable committed round work and evidence, hence not a marker. Round shape is incomplete (40-seat W1 only; no W2/results handoff), disclosed honestly. Dispatch/complete digest: `2026-10-28T07:41:58-03:00 launch souji round=35 pgid=3255231 driver=hyaku-inline attempt=1`; `2026-10-28T09:56:56-03:00 complete souji round=35; hyaku-inline attempt=1`.

## Claim re-checks and axis verdicts

All directly measurable claims below were independently re-measured from committed receipts or evidence; gate conclusions were evidence-verified from the committed counter receipt and its pinned revision, not by running the lane gate.

| Claim | Independent re-check | Axis verdict |
|---|---|---|
| C1 calibration, frozen 60-item agreement target | `census/round-35/records/controls-c1-do-nothing.txt` and report show only the red do-nothing instrument result `SUMMARY items=60 agree=37 unresolved=23 mismatches=23 withdrawn=0 restated=5`, rc 1. No final target result or measurement revision exists; lane explicitly says pending. | **unprovable** — no final after-state to compare. |
| C2 operability, frozen 13-leg target | `census/round-35/preregistration.txt` freezes `SUMMARY legs=13 pass=13 fail=0 harm_measured=0`; report/lesson retain only feasibility receipts: N3 `cases=12 pinned=True summary=False`, W2 `CASE=20 ... failed=1`, W3/W4 unmeasured, and no full counter run. | **unprovable** — no final 13-leg measurement. Red feasibility legs are not a measured axis regression. |
| C3 coverage, F1 fleet numerator | Recounted `census/round-35/records/prune-census.tsv` with `awk -F '\t' '$1=="REPO" {n++; split($3,a,"="); regs+=a[2]; split($4,b,"="); prunable+=b[2]} $1=="TOTAL" {print "recorded_total=" $0} END {printf "REPO_rows=%d regs=%d prunable=%d\n",n,regs,prunable}'`: `REPO_rows=26 regs=27 prunable=0`, `TOTAL repos=26 regs=27 prunable=0`; `sha256sum` matches S231 `8b37041ac1a954263c6f4e665a8105d37ac342c802fb11f596aadb69ec257177`. The committed C3 receipt says six legs all pass at `fedfa406...`; its revision is an ancestor of lane tip. The new knowledge entry repeats the receipt and cites mined S231/S232. But `corpus/README.md` still lists the exact F1 numerator as an open frontier item, so the claimed frontier-to-core coverage movement was not reflected in the coverage map; the fixed claim cannot be credited as a completed coverage-axis move. | **unprovable** — factual numerator and entry are supported, but claimed coverage transition is not established by the stale map. |

Overall owned axes: calibration **unprovable**; operability **unprovable**; coverage **unprovable**. No axis is evidenced harmed; all three axis claims remain unverified, so admission fails the all-claims rule. No score increase is justified. The SOURCES validator was independently run as required: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` printed only W04 duplicate-URL warnings and ended `souji ok` (exit 0); warnings are not a clean warning-free census.

## Discernment spot-check

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S231 / `fleet-prune-numerator-r35.md` | Admit | Committed own-work record `census/round-35/records/prune-census.tsv`; re-count above; registry row cites the row hash and totals. | agree | The 26 REPO records sum to 27 registrations and zero prunable, matching TOTAL and the dated entry. The separate lesson Gate does not give the required URL/access-date/≤25-word located quote for either new source; this is a curation-record defect, not a falsification of the receipt. |
| S229 | Reject | Re-opened https://docs.python.org/3.15/library/tempfile.html; page identifies itself as “Python 3.15.2 documentation.” | agree | The lane runs Python 3.14.8 per the row's stated rationale, so this page is not its interpreter-version source and the duplicate teaching adds no grounded fact over S226. The rejection has an explicit reason and flip condition. |

The spot-check agrees on the sampled admit and reject, so the outside check supports improved recognition of the gate's decisions. The missing quote/access record is a curation-evidence defect routed below; it does not change the independently re-opened admit/reject judgments.

## Trend verdicts

- **expansion: improved** — new `fleet-prune-numerator-r35.md` records a dated F1 re-census, cites mined S231/S232, and the frozen C3 receipt verifies its six checks; it adds a grounded current numerator, although README frontier maintenance is stale.
- **quality: unchanged** — no existing knowledge entry is re-verified, deepened, or superseded by stronger evidence; the old 2026-10-24 numerator is explicitly treated as historical rather than false.
- **discernment: improved** — the outside sample agrees with one admit and one reject; the incomplete Gate quote/access records remain a separate conformance defect.

## Routed defects for next round

1. Update `corpus/README.md` F1 coverage/frontier row when the re-census entry is held; the present map still says this exact re-census remains open.
2. Record each new SOURCES row's source URL, access date, and ≤25-word located quote in `corpus/lessons/round-35.md` `## Gate` (the current Gate is only a summary).
3. Resolve and document the post-tip `SCORECARD.md` modification and untracked `prune-census-corrected.tsv`; do not silently leave round work outside the pushed tip.
4. Next report must include the canonical section order, per-box SHONEN assessment, all three trend verdicts, stale-lane line, and actual before/after per claim; never report a 40-seat partial W1 as satisfying the run-10 64-seat floor or imply an unreceived wave result.
