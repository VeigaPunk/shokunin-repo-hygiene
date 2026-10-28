# Round 36 verifier spot-check — souji (closure, non-author)

author: hyaku closure (non-author integrator, @m_zfl)
round: souji 36, attempt 1 · base `94b5e96ab72b40622449af2dfe7c5b6d73118176` · tip
`1e771ed59301ed10f68e22d4edf35d5218bacf1a` = `origin/master` (`jj-lane.sh state`: ahead=0
behind=0, tree clean) · report `.ufo/reports/round-36/souji.md` committed `1eb8632a` +
erratum `af0b996e`, both lane-identity, both on fleet `origin/master`.
checked 2026-10-28. Dispatch digest (copied; watchdog.log is mutable):
`2026-10-28T11:09:17-03:00 launch souji round=36 pgid=944615 driver=hyaku-inline attempt=1` /
`2026-10-28T11:50:31-03:00 complete souji round=36; hyaku-inline attempt=1`.

## Step-1 conformance

| check | result |
|---|---|
| report committed by lane identity | ok — `git log -- .ufo/reports/round-36/souji.md`: `souji-shokunin <souji@shokunin.local>` at `1eb8632a`/`af0b996e` (2026-10-28 11:49:31/11:49:50 -03) |
| SHONEN heading, one line per box | ok — report `## SHONEN`, 4 boxes of `SHONEN.md`, 4 `[~]` lines with pointers; `git diff 94b5e96..1e771ed -- SHONEN.md` empty (unchanged, as the report states) |
| cited lane commits exist and are ancestors | ok — `git merge-base --is-ancestor` holds for `42ea92e…`, `af7d51a…`, `007ab53…`, `92a65fa…`, `bc9a3bb…` vs `master`; `1eb8632a` is fleet-repo-only (the erratum names it as the report commit, not a lane hash) |
| no uncommitted round work / pushed | ok — `git status --porcelain` empty; `jj-lane.sh state` ahead=0; `git ls-remote origin refs/heads/master` = `1e771ed…` |
| prompt carries the template contract | ok — `.ufo/prompts/souji-round-36.md`: mission/axes SSOT §1, 1–3 falsifiable claims + lowest axis §2, L2 ≥8 batched §3, report path/sections/SHONEN §4, commit-then-push + push scope + "report lands last and cites the pushed lane hash" + L0 channel §5 (:133–135, :491) |
| marker rule | real report (work, evidence, commit citations), not a marker → not `failed` |

## Per-claim re-check (which were re-measured vs evidence-verified)

- **C1 — RE-MEASURED by this verifier.** I ran the counter at both ends:
  `python3 -B tools/souji-coverage-agreement.py --root . --rev 94b5e96…` →
  `grounded=19 mapped=18 dangling=0 mismatches=1`, rc 1 (MISSING-FROM-MAP
  `corpus/knowledge/fleet-prune-numerator-r35.md`, ground=F1) — matches
  `census/round-36/records/c1-control-base.txt`; with `--rev af7d51a… --base-rev 94b5e96…` →
  `grounded=19 mapped=19 dangling=0 mismatches=0 kill_tested=19 kill_violations=0`, rc 0 —
  matches `c1-after.txt`. Strict arm receipt `c1-strict-paths.txt` (`distinct=27 missing=0
  nested_entries=0`, rc 0) committed. Tree stayed clean through the runs. **VERIFIED.**
- **C2 — EVIDENCE-VERIFIED (gate not executed; PROTOCOL §Gate standard).** Committed receipts
  at tip: `c2-after.txt` = `cases=21 pass=21 fail=0 control=STUB-REJECTED` +
  `control=VACUOUS-CHECKER-REJECTED`; r27 regression `cases=4 pass=4
  control=FALSE-GREEN-REJECTED`; selftest `SUMMARY cases=9 pass=9`; five mutants dead on named
  cases. Control `c2-control-base.txt`: base gate 0/11, STUB-REJECTED; base absence re-verified
  by me (`git cat-file -e 94b5e96…:tools/souji-report-contract.py` → rc 128). Receipt history:
  `c2-after.txt` held 20/20 at `007ab53` and `bc9a3bb`, 21/21 at `1e771ed` — it never held 11
  (w2 SwarmReviewer12-2 confirmed). **VERIFIED under the amended targets** (adjudication below).
- **C3 — EVIDENCE-VERIFIED (gate not executed).** Receipts: `c3-after.txt` = fixture
  `cases=12 pass=12 fail=0 control=STUB-REJECTED` (held 12/12 at both `007ab53` and `5f0dd45` —
  never 9); live run `record_repos=26 record_regs=27 record_prunable=0 live_repos=22 live_regs=23
  live_prunable=1 drift_rows=5 unreachable=0`, ABSENT exactly `ok,research,scripts,templates` +
  `PRUNABLE-CHANGED mado-shokunin`, identical in `c3-live-run.txt`. Base absence re-verified by
  me (rc 128). Capability rows landed (`SCORECARD.md` "Round 36 capability rows"). w2 hand
  recount (SwarmExecutor06) and receipt reproduction (SwarmReviewer12) agree. **VERIFIED under
  the amended targets.**

**Frozen-vs-amended adjudication (asked by the orchestrator).** The verdict applies the
**AMENDED targets** (C2 = 21/21 + vacuous control; C3 = 12/12; C1 = counter + strict probe).
Reasons: (1) every in-force target was matched by a receipt committed in the same commit that
set it (A7 at `1e771ed` refreshed receipt + target atomically; A5 changed no target string), so
no receipt ever contradicted a target in force; (2) every amendment is strictly tighter, named
to its producing wave seat in `census/round-36/preregistration.txt`, and re-measured; (3) the
frozen-letter reading would score the round on numbers (`cases=11`/`9`) that never lived in any
committed receipt — scoring against artifacts that do not exist is not a verification reading.
The letter is still broken and is recorded as a defect: the prereg's own "targets are not
rewritten after any after-data" sentence (and its FROZEN PREDICATE SENTENCE, prereg :76–80,
still `cases=11`/`cases=9`/selftest 8) was superseded by amendments without an in-file
correction of the sentence, and `SCORECARD.md` rows :563–:564 + capability rows :575–:576 +
`SKILL.md` gate-registry rows :248–:249 quote those never-true numbers as after-values with a
measured-commit cell (`42ea92e…`, "(instruments)") at which no after receipts exist — dangling
citations, not a two-readings dispute. The supersession table (`SCORECARD.md` :588+,
"rows above stand as written") carries the correct 21/12 readings and the LOG entry (:1839–1844)
carries 21/12; the stale cells are a calibration-signal defect, routed below.

## Per-axis verdicts

- **calibration: improved** — C1 re-measured green at both ends with the base-rev kill arm
  (`kill_violations=0`) and the strict-path probe closing the basename-only false green
  (QUALITY Q80); no axis harmed (`git diff 94b5e96..1e771ed -- SCORECARD.md` touches no axis
  row; scores stay calibration 7 / operability 8 / coverage 8).
- **operability: improved** — C2 receipts verified; checker flags the filed r35 report on
  exactly the four predicates the r35 spot-check recorded (`c2-filed-reports.txt`, r30–r35
  sweep). Routed (do not bar): the gate's contract verdict can be forged by a lying checker
  printing `check-*=PASS` + rc 0 (A5 rejects empty output only — w2 MutationTester01);
  bare WARNING/Traceback lines dropped.
- **coverage: improved** — C3 receipts verified; the drift run reproduces the corrected
  numerator and names the four phantom paths. Routed (do not bar): write-scope escapes in
  `--json`/env scrubbing (below) contradict the tool's "read-only"/docstring claim
  (`tools/souji-worktree-drift.py:14`) and the Gate-standard read-only scope; fixture
  discrimination gaps (survivor mutant `live_repos = len(rows) - unreachable` — only
  `live-repos-non-negative` reads the field; four predicates undiscriminated; HTML-comment
  masking unpinned).

## Discernment spot-check (LEARNING.md; ≥1 admit + ≥1 reject re-opened)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S233 bash conditional expressions | admit | live gnu.org page fetched 2026-10-28 | **agree** | quote verbatim in §6.4: "-s file True if file exists and has a size greater than zero."; the gate's non-empty-report predicate is exactly `-s` |
| S234 GNU grep 3.12 §2.3 Exit Status | admit | live gnu.org manual + committed snapshot (`census/round-36/sources/grep-manual.html`, sha256 `517177d0…` matches lesson) | **agree** | quote present verbatim (1 occurrence); script shells resolve `/usr/bin/grep` printing `grep (GNU grep) 3.12-modified` — I reproduced this myself (`bash -c 'type -a grep; grep --version'`) |
| S235 agent-shell builtin grep (pi-uu-grep 0.2.0) | reject | row basis re-checked in a script shell | **agree** | no located manual, no lane tool executes the builtin; the S234 flip (spec asked reject, lane re-verified and mined) is the discernment highlight of the round |
| S232 correction (r35 routed defect) | re-open | snapshot `git-worktree.html` | **agree, label defect** | quote verbatim at snapshot :2934, but in the LIST OUTPUT FORMAT section (anchor `_list_output_format`, TOC :158), not "§ OPTIONS" as the lesson labels it (w2 Revenger16 confirmed) |

`bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
→ 159 rows (`grep -cE '^\|\s*S[0-9]{3,}\s*\|' corpus/SOURCES.md` = 159), W04 duplicate-URL
warnings only, exit **0**.

## Trend verdicts (closure)

- **expansion: improved** — two mined sources (S233/S234), three QUALITY criteria Q80–Q82, two
  capability rows, F1 numerator recorded held and re-runnable; census 156→159 verified.
- **quality: improved** — seven disclosed amendments A1–A7 each repaired a measured falsifier;
  receipt history shows each repair re-measured in committed receipts; no admitted entry failed
  re-check.
- **discernment: improved** — S234 verdict flip re-verified against the live binary (I
  reproduced it), the counter's false green answered by a second named probe, the r35 Gate
  record repaired; the spot-check agrees with every sampled admit and reject.

## Routed defects (lane owes these in r37; all status-neutral)

1. **Stale/false receipt citations.** `SCORECARD.md:563-564` + capability rows :575–:576,
   `SKILL.md:248-249` (gate registry: r36-report-gate "0 11/11", r36-worktree-drift "0 9/9"),
   `corpus/lessons/round-36.md` ## Claims ("after A1–A3 … cases=20"), prereg :76–80 FROZEN
   PREDICATE SENTENCE: carry 11/9/8/20 vs receipts 21/12/9. Regenerate the cells; the
   measured-commit cells "after `42ea92e…` (instruments)" name a commit holding no receipts.
2. **Prereg discipline.** A7 rewrote the C2 target after after-data existed (letter of prereg
   "not rewritten after any after-data"); mitigate by amending the rule text to allow
   disclosed tighter-only retargeting with an atomic receipt refresh, and correct the frozen
   sentence.
3. **Drift-tool write escapes (w2 Sentinel07 W1–W4 + Reviewer20).** `--json` guard compares
   only `realpath(root)` — a `'../sibling'`/absolute record row plus `--json <sibling>/…`
   overwrites out-of-root files (W1, destructive, live exploit); `GIT_TRACE_REFS` path-valued
   and unscrubbed (W2); scrub deletes `GIT_CONFIG_GLOBAL/SYSTEM/NOSYSTEM` so real config and
   `trace2.*` targets are honoured (W3); guard resolves `target` but writes `open(args.json)`
   — symlink swap mid-run leaks (W4). Docstring :14 "never writes inside the measured tree"
   overstated; Gate-standard read-only scope violated until fixed. Fix the guard or remove
   `--json`; also: name-dedup byte-equality (`alpha`/`./alpha`/`alpha/` triple-count),
   `--root` not a containment boundary, oversized ints exit 1 without SUMMARY (wrong verdict
   class), `--json == --record` rewrite rc 0, `discover()` misses nested repos, prunable
   counts every stderr line, raw record path in SUMMARY, undocumented `#` skipping.
4. **Fixture discrimination.** Survivor mutant `live_repos = len(rows) - unreachable` passes
   12/12 (only `live-repos-non-negative` reads the field — SwarmExecutor23); four predicates
   undiscriminated (Reviewer20); HTML-comment masking mutant unpinned (MutationTester02);
   report-gate verdict forgeable by fabricated `check-*=PASS` + rc 0, bare
   WARNING/Traceback dropped (MutationTester01); residual `--report /dev/zero` unbounded
   read hang (Reviewer31).
5. **Frozen receipt divergence.** `census/round-36/records/c2-filed-reports.txt` predates A3:
   r31/r32 `sections=FAIL` lines no longer reproduce (r31 :18 / r32 :36 quote `##` headings
   mid-line; A3 matches exact `##`-depth headings only). Regenerate with the checker revision
   pinned in the header (lane disclosed; connector's proposed move).
6. **Report prose.** Landed table :106 "wave evidence … committed with the final landing
   commit" is false bytes (erratum supersedes; `.ufo/waves/` is `.gitignore:1`, 0 tracked
   round-36 files vs 3026 legacy incl. round-35: 8); Landed table omits A6/`5f0dd45`;
   counting command carries `<landing>`/`<full40>` placeholders (:16, :112); census command
   cited as `bash scripts/sources-census.sh …` which is rc 127 from the lane cwd (no
   `scripts/`); frontier wording credits the r35 spot-check for the 22/23 numerator (r35
   SCORECARD row records the direct-root replay; seats Reviewer19/Revenger16 disagree on
   provenance — figure itself verified in both places); report wave section says the launcher
   had not taken `w2.ready` at filing — the marker is 11:37:46 -03, before the 11:42:24
   authoring.

## Wave accounting

w1: **39/39** seat reports on disk under `.ufo/waves/round-36/w1/` (incl. the late
SwarmConnector39). w2: 32 spec'd; `w2.ready.dispatched` 11:37:46 -03; **29/32** reports on
disk at spot-check time; no `w1/w2-results.json` handoff exists. Total 71 seats spec'd, in the
64–128 band; §3 L2 floor met inside w1. No claim of this round cites any w2 seat; the w2
findings above are folded as routed defects. The three w2 stragglers' findings, if any, ride
r37's reconciliation.

## Contamination check (kaidoku-class sweep)

**Clean.** All seven round-36 lane commits carry author = committer =
`souji-shokunin <souji@shokunin.local>`; committer times (11:17:50→11:49:01 -03) all fall
inside the dispatch window (11:09:17–11:50:31) and postdate their author times; the freeze
commit's author time (10:43:38) equals its parent's committer time — jj working-copy
inheritance, the same pattern as every prior round, not backdating. Both fleet report commits
are lane-identity and precede the `complete` line. No third-party identity and no
post-completion lane-identity commits touch the lane (tip = remote = `1e771ed…`).

**Verdict: souji r36 admitted — every claim verifies (C1 re-measured, C2/C3 evidence-verified
under amended targets), no owned axis harmed.**
