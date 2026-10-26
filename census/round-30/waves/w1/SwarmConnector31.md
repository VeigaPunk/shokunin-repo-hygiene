# SwarmConnector31 — sibling-overlap scan, souji round 30 w1

## Status

STATUS: PASS — all three of this round's surfaces (jj keep-ref/gc/abandon, landing-gate/report discovery over committed captures, capability-table literal agreement) scanned read-only across 952 sibling files plus `scripts/hyaku/jj-lane.sh`; zero contested-scope claims found; `jj-lane.sh` never runs `jj util gc` or `jj op abandon`.

## Evidence

- Scan (sweep inventory: 21 `*/PROVINCE.md`, 19 `*/SKILL.md`, 21 `*/corpus/README.md`, 890 `*/corpus/knowledge/*.md`, `scripts/hyaku/jj-lane.sh`; souji files filtered):
  `cd /home/vgpnk/Projects/shokunin && grep -rnF '<pattern>' */PROVINCE.md */SKILL.md */corpus/README.md */corpus/knowledge/*.md scripts/hyaku/jj-lane.sh` for patterns `refs/jj/keep`, `util gc`, `op abandon`, `keep ref`, `census/round-`, `capability`; supplemental regex passes for `landing|\.ufo/waves/round-`, `keep[- ]ref`, `souji-landing-gate|souji-capability|SHONEN`.
- Scan reference revision: fleet working tree at fleet HEAD `a7c6d0f1828099828a6ca0e01c2f6eb2b3f8c59c` (sibling files read from the fleet worktree; lane HEAD observed `df6afe817d096e4ad71ba2b9cc21a83f126eb658`, wave-1 landings in progress). Full receipts: `.ufo/waves/round-30/w1/deliver-sibling-overlap.md`; raw scans in seat scratch (removed after the run per scratch discipline).
- `jj-lane.sh` empty sweep: `grep -nE 'util gc|op abandon' scripts/hyaku/jj-lane.sh` → exit 1 (zero matches over 841 lines).

## Findings

1. Surface 1 (keep refs / gc / op abandon; souji C3): three sibling hits, none contested. kumitate-shokunin/corpus/knowledge/jj-workspace-seat-containment.md:102 (verbatim, 16 words): "only `jj op abandon` + `jj util gc` or a separate clone excludes them from storage" — states the op-log GC mechanism for abandoned *commits'* storage, not `refs/jj/keep/*` expiry. kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:57 (verbatim): "one keep-ref, rewrites `.git/index`" and mado-shokunin/corpus/knowledge/tripwire-precision-r20.md:70 (verbatim): "measured: +1 op, `refs/jj/keep`" are creation-side observations only. Souji's F1 keep-ref-expiry entry ground is uncontested.
2. Surface 2 (landing gates / discovery over committed captures; souji C2): two sibling hits, both consumption not contest — tsukuroi-shokunin/corpus/knowledge/adjacency-anchors-r19.md:185-186 cite `souji:census/round-12/connector.md:29` and `souji:census/round-16/transcripts/w1/SiblingOverlap.txt:52` as operative adjacency anchors (IN-090, IN-091). No sibling references `souji-landing-gate` or `souji-capability` (zero hits). Nearest sibling instrument family is kumitate-internal (report-receipt-diff, round-close gate) and does not discover reports from committed census captures. Souji's C2 surface is uncontested; tsukuroi's anchors are demand-side evidence that siblings read souji's committed census paths.
3. Surface 3 (capability-table literal agreement; souji C1): sibling `capability` hits are generic vocabulary; the calibration idiom is practiced lane-internally by kaidoku (SKILL.md:1263, verbatim 11 words: "gate — R36-C2 calibration, self-assessment surfaces vs observed repo state"), kama (corpus/knowledge/self-assessment-at-writing.md:7, verbatim 16 words: "Round 29 C1 checks only the statement forms extracted from lines of `SCORECARD.md` and `SHONEN.md`"; frozen counter `.ufo/waves/round-29/count-c1.py`), and revenger (SKILL.md:295, `corpus/self_assessment_check.py`) — each over its own SCORECARD/SHONEN, none over souji's rows R01–R18 at base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`. Uncontested.
4. `scripts/hyaku/jj-lane.sh` (841 lines) never runs `jj util gc` or `jj op abandon` (empty sweep, exit 1). Its `"$JJ_BIN"` surface is: `config get/set/list`, `log --no-graph`, `bookmark list/set`, `git fetch`, `git push --bookmark`, `status`, `git init --colocate` — no GC or op-log mutation in the fleet helper.
5. Tool defect (reported at `xd://report_issue`): the harness `grep` tool returned "No matches found" for absolute-path globs (`/home/vgpnk/Projects/shokunin/*/corpus/README.md`) where a literal path over the same bytes matched; scan was run with shell `grep` instead. No tools installed this seat.

## Deliveries

- `.ufo/waves/round-30/w1/deliver-sibling-overlap.md` — the sibling-overlap scan deliverable (hit tables, verbatim quotes, contested-scope verdicts, jj-lane.sh sweep).
- `.ufo/waves/round-30/w1/SwarmConnector31.md` — this report.
