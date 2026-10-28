# R41w2scribe02 — round-41 frontier update draft and wave-2 re-measurement (scribe)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Tip measured: `1d41c13574db80fdd9a4bde490b712da7ce2a85f`. Freeze: `e2a74312af4233963e44e4dbb38838ece07b8bd2`. Base: `7eebc183f2685d1ea9b004b4de22c09a8a4035a7`.
Scratch: `/fast/scratch/hyaku/souji-r41/R41w2scribe02/` (TMPDIR and --scratch passed explicitly; deleted before yield). No git/jj mutation, no lane file written, `corpus/README.md` not edited. No tool installed or upgraded. No candidate scored.

Deliverable: `.ufo/waves/round-41/w2/R41w2scribe02/readme-r41.md` (the `## Round 41 frontier update` draft). Receipts: `.ufo/waves/round-41/w2/R41w2scribe02/receipts/`.

## Verdict

- **Frozen targets: PASS (re-run).** All four landed counters reproduce their preregistered Target strings at the landed revisions: C1 `items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`; C2 `cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red`; C3 `sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10`; R1 `mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6`. Frozen blobs are byte-identical from freeze to tip.
- **Round narrative: NOT CLEAN — blocking for admission until the L1 appends corrections.** The round lesson makes statements that do not re-derive at the tip (F1: three QUALITY citations; F2: an incomplete N11 command; F3: an overstated "all four routed defects answered" with two open items), and the end census receipt is not committed (F4). No frozen Counter checks any of these, so the targets do not catch them. The calibration axis is harmed by F1 and F3.
- **Coverage map: no ground moved; none promoted to Core.** Assimilation: none. Certification OFF, K5 HELD, NAMESPACE hold unchanged.

## Findings

### F1 — the round lesson cites QUALITY Q98, Q99 and Q100, none of which exists at the tip (calibration; blocking)
- Evidence: `corpus/lessons/round-41.md:35` ("QUALITY Q98 records the rule"), `:106` ("QUALITY Q99"), `:135` and `:143` ("QUALITY Q100 records the rule" / "requires it"). `corpus/QUALITY.md` ends at Q97.
- Commands and output:
  - `grep -c 'Q98\|Q99\|Q100' corpus/QUALITY.md` → `0`
  - `grep -oE '^\| Q[0-9]+' corpus/QUALITY.md | tail -3` → `| Q95`, `| Q96`, `| Q97`
  - `git diff --stat e2a7431 1d41c13 -- corpus/QUALITY.md` → empty; `git diff --stat 7eebc18 1d41c13 -- corpus/QUALITY.md` → empty (no QUALITY change, base to tip).
  - `git grep -n -i 'already held' e2a74312af4233963e44e4dbb38838ece07b8bd2 -- corpus/QUALITY.md | wc -l` → `0` (the R40-D-PRUNE clause-2 criterion was never added).
- Effect: the lesson's R40-D-PRUNE re-decision (`:35`) and its claim-sizing and captured-by statements (`:106`, `:135`, `:143`) cite rules that were never committed. Not covered by any frozen Counter: C1 checks only I1/I3/I4 lines.

### F2 — the N11 command in the lesson is incomplete; the K1 red is real and pre-existing (documentation; the finding stands)
- Evidence: `corpus/lessons/round-41.md:169` gives `python3 -B tools/souji-registry-agreement.py` with no arguments.
- Commands and output:
  - `python3 -B tools/souji-registry-agreement.py` (no args) → argparse error: `the following arguments are required: --root, --rev, --list-rev`, exit 2.
  - `python3 -B tools/souji-registry-agreement.py --root <lane> --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --list-rev e2a74312af4233963e44e4dbb38838ece07b8bd2` → `COULD-NOT-EVALUATE derived facts are trivial`, exit 2 (the freeze commit is not the list revision the tool's K2 facts need; `.ufo/waves/round-41/w1/R41critic07.md:115`).
  - `... --root <lane> --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804` → `K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md`, `SUMMARY k1=1 k2=0 mismatches=1 rev=1d41c13…`, exit 1 (receipt `receipts/regagree-tip.txt`).
  - `... --root <lane> --rev 7eebc183f2685d1ea9b004b4de22c09a8a4035a7 --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804` → the same `K1 cited-no-row S146` line, `mismatches=1`, exit 1 (receipt `receipts/k1-base.txt`). Pre-existing before round 41.
- `grep -c '^| S146 ' corpus/SOURCES.md` → `0` (the row is not in the registry at the tip).

### F3 — the lesson's "all four routed defects answered" and its routed-forward list omit open items (calibration)
- `corpus/lessons/round-41.md:9-10` asserts R40-D-PRUNE, R40-D-C1-BEFORE, R40-D-FREEZE and R40-D-TOTAL are answered. `.ufo/waves/round-41/w1/R41connector02.md` items 1 (R40-D-PRUNE clause 2, see F1) and 3 (R40-D-FREEZE residue) are OPEN.
- Item 3 evidence (re-checked): `grep -n -i 'base' census/round-41/preregistration.txt` returns only the `Base: 7eebc183…` revision lines (`:19`, `:29`, `:39`, `:49`) and the R1 predicate text (`:54`); no C3 or R1 base-fixture path or digest exists. `census/round-41/c2-counter.py:15` defines `Base:` as a full40 revision and has no base-fixture key (agrees with `R41connector02.md` §3).
- The lesson's `## Named limits` "Routed forward (R41connector02)" line lists M40-12, R39-D1/D2, the count pattern, scratch receipts and in-place edits; it omits items 1 and 3.

### F4 — the end census receipt the preregistration asks for is not committed (frontier step)
- `census/round-41/preregistration.txt:57` requires "Census command (start and end)". `census/round-41/records/` holds `census-before.txt` only. `grep -cE '^rows=' census/round-41/records/census-before.txt` → `0`, so the start count is not stated there either.
- Scratch re-run, not committed and not a receipt: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0; `... census --root ... souji` → `souji rows 182`, `tier.A 173`, `tier.B 6`, `tier.C 3`, `status.mined 152`, `status.queued 14`, `status.rejected 16` (receipts `receipts/census-validate-tip.txt`, `receipts/census-tip.txt`). The L1 should commit the end receipt from `1d41c13` or later.

### F5 — N10 reproduced (routed tool defect, unchanged by any landed artifact)
- Setup (scratch): root `n10/root` (empty), record `n10/o/rec` with one row `REPO ghost regs=0 prunable=0`, `--json n10/work/out.json` where `out.json` is a symlink to `n10/outside/victim.json` containing `VICTIM-ORIGINAL`.
- Command: `python3 -B tools/souji-worktree-drift.py --root <root> --record <rec> --json <work>/out.json` → `DRIFT ABSENT ghost recorded regs=0`, rc 1 (a plain `--json` control path gives the same stdout). Afterwards `ls -l` shows `out.json -> .../victim.json` and the victim holds the JSON report (`receipts/n10-victim-after.json`). Confirms `.ufo/waves/round-41/w1/R41sentinel01.md` F1 at the pinned tool (`sha256 b2a603cf…`).

### F6 — S258 and the lesson's CORRECTION lines re-derive (verified; no defect)
- `grep -n -F 'prune missing working trees older than <time>' census/round-41/sources/git-v2.56.0-builtin-worktree.c` → `255: N_("prune missing working trees older than <time>")),`; `sha256sum` of the snapshot → `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc` (matches the S258 row); `git show 1d41c13:census/round-41/sources/git-v2.56.0-builtin-worktree.c | cmp - <snapshot>` → identical.
- I1 at `bffcc0f660ff36eb8add3f61582748a7af019a5b`: `git show bffcc0f…:corpus/SOURCES.md | grep -E '^\| S[0-9]+ ' | grep -c 'worktree\.c'` → `2`; `… | grep -c 'v2\.56\.0/worktree\.c'` → `0`. Matches `rows=2,v2.56.0=0`.
- I3: `git show bffcc0f…:census/round-40/records/c1-before.txt | grep -o 'register_cells=[0-9]*' | head -1` → `register_cells=6`; `c1-after-h.txt` → `register_cells=3`. Matches.
- I4: over the 136 files from `git ls-tree -r --name-only bffcc0f… census/round-40/waves/`, `grep -c 'flagged as potentially'` summed → `occurrences=0`. Matches.

## Commands run (all read-only; exact invocations and the output that matters)

Frozen-target re-measurement (scratch dirs created first; `--scratch` names an existing directory):
1. `python3 -B census/round-41/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 31e4d3e758bb903808a9270018d7e5be99ce38a4` → `ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes`; `ITEM I3 … derived=before=6,after=3 …`; `ITEM I4 … derived=occurrences=0 …`; `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`; `EXIT=0`. (`receipts/c1.out`)
2. `python3 -B census/round-41/c2-counter.py --root <lane> --rev 119c26fa3bbb85e215824de9538bd2eb34e9f874 --scratch <dir>` → 21 `case-…=PASS` lines; `real ok rc=0 findings=0 summary=(3, 0)`; `retro red rc=1 findings=18 summary=(3, 18)`; `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8`; `EXIT=0`. (`receipts/c2.out`)
3. `python3 -B census/round-41/c3-counter.py --root <lane> --rev a1144120611b00091ac4839559d8ebf38aa9a83a --scratch <dir>` → `PRISTINE ok rc=0 probes=21 …`; 19 `SITE Sxx … killed …` lines, none survived; `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2`; `EXIT=0`. (`receipts/c3.out`)
4. `python3 -B census/round-41/r1-counter.py --root <lane> --rev 97eeb01e73a9baa3e4191b9052fed9e505c70215 --scratch <dir>` → 11 `MUTANT M11…M21 … killed=yes`; `SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106`; `EXIT=0`. (`receipts/r1.out`)
5. Controls (committed outputs, `census/round-41/controls/*-control.txt`): c1 `corrected=0 uncorrected=3 junk=3 sourced=0`, rc 1; c2 `pass=2 fail=19 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL`, rc 1; c3 `killed=0 survived=19`, rc 1; r1 `killed=8 survived=3 new_killed=0/3`, rc 1.

Direct tool reads:
6. `python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-41/preregistration.txt --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f` → `SUMMARY claims=3 findings=0`, exit 0. (`receipts/fc-real.txt`)
7. `python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-40/preregistration.txt --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f` → 18 `FINDING …` lines (`grep -c '^FINDING'` → 18; first three `FINDING C3 FIELD-MISSING Kill/Population/Target`); `SUMMARY claims=3 findings=18`; exit 1. (`receipts/fc-retro.txt`)
8. `python3 -B tools/souji-freeze-check.py --help` → usage `--root ROOT --prereg PREREG --rev REV`.
9. Registry: F2 commands (`receipts/regagree-tip.txt`, `receipts/k1-base.txt`).

Frozen-blob and scope checks (receipt `receipts/frozen-and-scope-checks.txt`):
10. `git show e2a7431:<f> | sha256sum` and `git show 1d41c13:<f> | sha256sum` for c1/c2/c3/r1 counters, c1-items.tsv, c2-cases.tsv, c3-sites.tsv, tools/souji-worktree-drift.py → all pairs equal; counters match the preregistration (`8860dc7a…`, `85ffe263…`, `9ef99e8f…`, `8352eed4…`; populations `2d2a548e…`, `4854335a…`, `be363c0d…`); drift tool `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` at e2a7431, 1d41c13 and 6682b98.
11. `git diff --stat e2a7431 1d41c13 -- <frozen paths>` → empty.
12. `git diff --stat 7eebc18 1d41c13` → `32 files changed, 5093 insertions(+), 2 deletions(-)`; `git diff --stat 7eebc18 1d41c13 -- corpus/README.md corpus/knowledge SKILL.md corpus/QUALITY.md tools/souji-cert-evidence.py | wc -l` → `0`.
13. `grep -c '^CORRECTION I' corpus/lessons/round-41.md` → `3`; `grep -cE '^- \*\*N[0-9]+ ' corpus/lessons/round-41.md` → `12`.
14. `git show 1d41c13:corpus/SOURCES.md | grep -cE '^\| *S[0-9]{3,}'` → `182`; `git diff 7eebc18 1d41c13 -- corpus/SOURCES.md` adds one registry row (S258) and one Round-41 provenance paragraph in the search-log section.
15. `git show e9dc38d -- tools/souji-worktree-drift.py` → the R40-D-TOTAL repair (`totals.append(total)`; "every TOTAL row is kept and checked").
16. `grep -cE '^rows=' census/round-41/records/census-before.txt` → `0`; `git grep -n -i 'already held' e2a7431 -- corpus/QUALITY.md | wc -l` → `0`; `grep -c 'Q98\|Q99\|Q100' corpus/QUALITY.md` → `0`; `grep -n -i 'base' census/round-41/preregistration.txt` → lines 19, 29, 39, 49, 54 (F3).
17. `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0; `... census ...` → `souji rows 182` (F4; scratch output, not a receipt).

Attacks and reproductions: N10 (F5). No candidate was written; no `score-candidate.sh` run.

## Evidence pointers

- Lesson: `corpus/lessons/round-41.md` lines 9–10, 35, 106, 135, 143, 169; `## Corrections` block (I1, I3, I4) and `## Named limits` (N1–N12).
- Preregistration: `census/round-41/preregistration.txt` lines 18–60 (targets, kills, frontier step).
- Wave-1 inputs read: `.ufo/waves/round-41/w1/R41connector02.md` (items 1–8), `R41critic07.md` (N11 invocation, lines 115–120), `R41sentinel01.md` (F1, lines 18–25).
- Receipts in seat directory: `.ufo/waves/round-41/w2/R41w2scribe02/receipts/` (c1.out, c2.out, c3.out, r1.out, fc-real.txt, fc-retro.txt, regagree-tip.txt, k1-base.txt, census-tip.txt, census-validate-tip.txt, n10-drift-json-symlink-run.out, n10-victim-after.json, c1/c2/c3/r1-control.txt, frozen-and-scope-checks.txt).
- Draft: `.ufo/waves/round-41/w2/R41w2scribe02/readme-r41.md`.

## Limits of this report

- The counters re-run here are the committed ones at the landed revisions; they do not test whether a different fixture could pass (named limits N1–N9, N12 stand as filed).
- The census end run and the registry check were run from the lane with `-B`, read-only; their outputs are not committed receipts and are reported as observations.
- I did not run the C2 hidden-case audit or the second-seat source re-open the lesson names as wave-2 work (other seats' items).
- The draft README section states F1–F4 as pending corrections; it does not repair the append-only lesson.

## Tools

None installed, upgraded, or removed. Interpreter: system `python3` (`-B`). No pacman transaction.
