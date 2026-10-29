# Round 42 — verifier spot-check (souji)

author: hyaku closure (non-author integrator, @m_zfl)

Round: souji 42 (two dispatch attempts: run 11 honest-stop, run 12 resume completion).
Lane base `bf618f6c5c09d302994871c94903abbea2deb60d` (r41 spotcheck commit) → tip
`34343a39ffab8029b06e8e6c9ac699ebcbd65f8a` (pushed `refs/heads/master`). The closure
assignment names `6a3f7594…` as "HEAD before the round"; that is the run-12 resume base —
the run-11 landed work (`410316c9…`–`6a3f7594…`) sits between. Axis-harm was therefore
checked over the full span `bf618f6c…`→`34343a39…` and over the assignment's range.

## 1. Step-1 conformance — all pass, defects none blocking

- Report committed in the fleet repo by the lane identity:
  `git log --format='%an <%ae> %H' -- .ufo/reports/round-42/souji.md` →
  `souji-shokunin <souji@shokunin.local> 5ada10c884520fa7d02338cd03b9bfaab72d6bdd` (honest stop)
  and `8fd7b8f15ed41f7cd1a31e28a45d1afa72e2a721` (resume). Path per contract. Real report, not a
  marker: work performed, landed changes with hashes, before→after table, Sources & frontier,
  trend verdicts, SHONEN all present.
- `## SHONEN` heading exactly 1 (`grep -c '^## SHONEN'` → 1) with four `[~]` lines — one per
  SHONEN.md box, pointers resolvable. No `[x]` written by the lane.
- All 13 cited lane commits exist and are ancestors of `refs/heads/master`
  (`git merge-base --is-ancestor <hash> refs/heads/master`): 410316c9, b7408095, afe17f41,
  13320670, 5ad7046d, e95b13be, 51f204fb, 34e33a66, 3105a63b, d39e3453, 6a3f7594, 17a6d0b5,
  34343a39 — ANCESTOR for every one.
- Pushed, no leftovers: `jj-lane.sh state` → `branch=master local=34343a39… remote=34343a39…
  ahead=0 behind=0`; `git status --porcelain` in the lane → empty;
  `git ls-remote origin refs/heads/master` → `34343a39…`.
- Dispatch evidence digest (copied from `.ufo/watchdog.log`, verified byte-identical at lines
  1919/1932/1934/1940):
  `2026-10-28T20:44:09-03:00 launch souji round=42 pgid=1394300 driver=hyaku-inline attempt=1`
  `2026-10-28T23:45:14-03:00 complete souji round=42; hyaku-inline attempt=1`
  `2026-10-29T17:09:52-03:00 launch souji round=42 pgid=3365367 driver=hyaku-inline attempt=1`
  `2026-10-29T19:57:29-03:00 complete souji round=42; hyaku-inline attempt=1`
- Prompt fidelity: `.ufo/prompts/souji-round-42.md` is the canonical `templates/round-prompt.md`
  rendering (sections 1–5 byte-faithful modulo lane/round/fleet/axes substitution) plus the hyaku
  addendum §6 and §7 scratch discipline. Round-level items (i) mission/axes binding, (ii) L2 ≥8 in
  one batched call, (iii) commit-then-push, (iv) push scope, (v) L0 channel — all present; five
  child-lane items (report path/filename, commit-before-report ordering ["The report lands last and
  cites the pushed lane hash"], SHONEN heading, commit-hash citation, write scope) — all present.
  Route map quoted (run-11 map + m_auto amendment) defers to the host table; MISSION.md carries no
  conflicting per-alias bucket. No conflict.
- Round shape evidence: w1 39/40 seat reports, w2 32/34, w3 4/4 in `census/round-42/waves/`,
  `w3-results.json` carries 4 seats, all settled. Run-11 waves have no results file (disclosed in
  the report; seat counts rest on report files) — conformance note, status-neutral.

## 2. Claims — re-check per claim

The three counters and r1-counter are lane-owned gates (SKILL.md registry rows `r42-*-counter` at
the lane's registry home, each with verdict map, selftest, pinned values, owner). Per PROTOCOL
§Gate standard (Closure consequence) they were **not executed** by this reviewer; their committed
evidence was verified and the numeric claims re-derived with plain grep/awk/git over committed
bytes. No owned axis was harmed: `git diff bf618f6c… 34343a39… -- SCORECARD.md` is append-only
(+41 lines, honest-stop errata + resume section; scores calibration 7 / operability 8 / coverage 8
unchanged); the assignment's range `6a3f7594…`→`34343a39…` adds the resume section only.

Frozen-instrument integrity (preregistration rule 1): at tip `34343a39…`, sha256 of c1-counter.py
`0ab07cd3…`, c2-counter.py `fa44392d…`, c3-counter.py `bf0ebf4f…`, r1-counter.py `f2dcbd06…`,
c1-items.tsv `b2601340…`, c2-cases.tsv `148b7b87…`, c3-mutants.tsv `2f6f8df3…`,
tools/souji-worktree-drift.py `b2a603cf…` — all MATCH the preregistration; every frozen file is
blob-identical between freeze commit `afe17f41…` and tip.

### C1 — calibration (lowest non-retired axis, 7) — verdict: improved (evidence-verified + re-measured plainly)

- Population real: all 70 `c1-items.tsv` tokens (70 data rows) grep in SCORECARD.md at base
  `bf618f6c…` — sweep found 0 absent.
- Register honest: `c1-register.tsv` awk by class column → `resolved=65 unresolved=5` (= 70).
- Corrections bound: `corpus/lessons/round-42.md` carries exactly 5 `CORRECTION-DE` lines whose
  tokens equal the register's 5 unresolved tokens (65817d0d, 42259756…, 71b89eb3…, 09bb8e0d,
  c2-after.tsv), each with the counter's derived value and rev.
- Sampled 5 of the 65 `resolved_to` paths — all exist at tip (`git cat-file -e`).
- Controls red (receipt `controls/c1-control.txt` at instruments commit `b7408095…`): do-nothing
  `registered=0` rc=1; forged all-resolved register `class_ok=42` rc=1.
- Committed measurement: `records/c1-after.txt` at `34e33a66…` and the resume re-run
  (`records/resume-remeasure-l1.txt`, first attempts rc=2 refusal honestly recorded) both print
  `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0
  rewritten=0 new_mismatches=0` rc=0 — identical to the report.

### C2 — operability — verdict: improved (evidence-verified + re-measured plainly)

- 37 case rows in `c2-cases.tsv` (38 lines − header) = the counter's `cases=37`.
- Committed receipts (`records/c2-after.txt` at `5ad7046d…`; tip re-run identical): 37/37 cases
  PASS, `real=ok`, `retro=red`, `retro_clean=ok`, `selftest=ok`, `patches=3/3`, `tool_sha=9ddd596b98fb`,
  rc=0 — identical to the report. Self-test tally committed; registry row present.
- Controls red (`controls/c2-control.txt`): r41 tool `pass=24 fail=13 selftest=FAIL patches=0/3`
  rc=1; always-green selftest stub `selftest=ok` but `patches=0/3` rc=1.
- Tool landed at `1332067…`; the new grammar classes (KEY-DUPLICATE, HEADING-MALFORMED,
  COUNTER-/POPULATION-SYMLINK, widened DISPATCH-BEFORE-FREEZE names) grep in the landed tool bytes.
- Sourced leg: S259 (below) — the `sitecustomize`/PYTHONPATH injection the patches leg uses.
- Wave-3 corroboration: `waves/w3/R42w3mutationtester01.md` — 136 part-A mutants, 67 survivors all
  re-verified and classified (35 equivalent + 30 gaps + 2 real-leg-only); the frozen target is
  untouched and still reads 37/37 on the honest tool.

### C3 — coverage — verdict: improved, with the load-sensitivity limit standing (evidence-verified + re-measured plainly)

- 13 mutant rows in `c3-mutants.tsv` (14 lines − header) = `mutants=13`; preregistration names the
  same 13 ids and the 6 behaviour-equivalent ids.
- Canonical idle receipt `records/c3-after.txt` at `5ad7046d…`: 13 × `candidate=killed`,
  6 × EQUIV `survived`, `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0
  equiv=6 equiv_killed=0 anchors=ok` rc=0. Tip re-run at load 40.21 also 13/13 rc=0.
- The load flake is disclosed, never narrowed: SCORECARD errata + lesson E-1 (1 of 3 tip runs
  `killed=9`, one loaded run `killed=5`); the idle-host reading stays canonical.
- Controls red (`controls/c3-control.txt`): absent fixture `survived=13` pristine=FAIL rc=1;
  always-pass stub `survived=13` rc=1; byte-sniffing stub `equiv_killed=6` rc=1 — the fixture is
  shown to read behaviour, not bytes.
- Pinned tool byte-identical (`b2a603cf…` at freeze and tip). Fixture exists at tip
  (`tests/fixtures/r42-drift-conditions.py`).
- Wave-3 corroboration: `waves/w3/R42w3mutationtester02.md` — 1050-cell fixture-mutation grid, 0
  disagreements with the wave-2 partial grid over 634 shared cells, harness verdicts match the
  frozen counter exactly, G3 kill reproduced serially under load.

### R1 — residual (not a claim) — status-neutral, honestly red-by-its-letter

The frozen r1-counter predicate (`rows_added=3`) is unsatisfiable: the gate's exemption grammar
cannot name `../` pointers and the frozen counter ignores the gate exit (lesson E-2/M42-2) —
disclosed in the report as deviation, never narrowed. Plain re-check of the landed repair: base
gate receipt (`records/gate-both-modes.txt`) shows `findings=3` (3 × LG-DANGLING-PTR) at
`bf618f6c…` and `findings=0` both modes at `51f204fb…`; tip receipts `findings=0` both modes with
`--round 42`. My own read of the tip bytes: `corpus/README.md` now cites
`../census/round-42/jj-w1-reports/JjTrialSouji.md` / `JjAuditSouji.md`, and
`corpus/knowledge/jj-colocation-receipts.md` cites the same lane copies — the files exist
in-repo with `SHA256SUMS`. The repair is real; the counter reads it red by its letter.

## 3. Discernment spot-check (LEARNING.md) — non-author re-open

| item | decision | re-opened source (by this reviewer) | agree/disagree | reason |
|---|---|---|---|---|
| S259 — Python `site` docs (admit, tier A, mined) | admitted for C2's `patches` leg | committed snapshot `census/round-42/sources/python-3-library-site.html`: sha256 `620581fe…5d546a` matches `SHA256SUMS`; quote "an attempt is made to import a module named sitecustomize, which can perform arbitrary site-specific customizations" found across lines 415–421 with tags stripped (splits across served-HTML lines exactly as the lesson's location note says); served marker "Python 3.15.2 documentation" matches the anchor; 16 words ≤ 25; registry row cells well-formed, scope caveat (not `-I`/`-E`/`-S`, not `-I`) recorded as Q105 | **agree** | the C2 patches leg genuinely injects through a `sitecustomize` module on PYTHONPATH; the page documents exactly that import and the `-S` suppression; the tier-A scope is honest about what the page does not say |
| staged `fleet-prune-safety-r28.md` (reject; shokuknow `merge/souji/knowledge/corpus/knowledge/`) | rejected, not adopted | re-opened the staged entry ("Every prunable registration is safe to prune…", recheck expecting `registrations=26 safe=26`, measured 2026-10-24) and the lane's counter-evidence `corpus/knowledge/fleet-prune-numerator-r35.md` + `census/round-35/records/prune-census.tsv` (`TOTAL repos=26 regs=27 prunable=0`, run 2026-10-28) | **agree** | the staged conclusion is about a population the newer measurement shows empty (0 prunable); adopting would reintroduce a superseded numerator; rejection carries a positive ground, as the r41 spotcheck demanded |

Sample = the round's full Gate set (1 admit + 1 reject). Census validator re-run by this reviewer:
`sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok`, rc=0, 52 W04
warnings (pre-existing duplicate-URL class, unchanged 182→183), rows 182→183 with the single new
row S259 — matches the receipts.

## 4. Trend verdicts (closure's own, with evidence)

- **expansion — unchanged.** One tier-A row (S259) on held ground (the C2 patches leg's own
  mechanism); no `knowledge/` entry added (full-round diff: SOURCES +1, no knowledge/ additions);
  corpus/README F1 stays frontier; 17 new drift survivors are r43 population, not ground.
- **quality — unprovable-but-better.** Nothing regressed: two false SCORECARD sentences corrected
  append-only with named scope (CORRECTION-SC), C1's five unresolved tokens corrected with
  derived-value scope, Q103–Q105 added each citing its lesson, and the artifacts survived wave-3
  attack (136 tool mutants, 1050 fixture cells, axis-harm audit) with no defect finding. But no
  corpus `knowledge/` entry was re-verified or superseded this round and the C3 reading stays
  load-fragile, so the trend's `improved` observable is not met.
- **discernment — improved.** This closure is the named outside spot-check: the sampled admit and
  reject both AGREE (sample = the round's full Gate set); additionally the round caught its own
  wrong diagnosis (E-2) and flaky reading (E-1) and landed them as lesson content with criteria.

## 5. Per-axis verdicts

| axis | claim | verdict |
|---|---|---|
| calibration | C1 | improved |
| operability | C2 | improved |
| coverage | C3 | improved (load-sensitivity limit stands, disclosed) |

No axis harmed. All three claims verify → admission criteria met.

## 6. Routed defects / items the lane owes r43 (status-neutral)

1. r1-counter.py's frozen predicate is unsatisfiable as written (ignores gate exit; exemption
   grammar cannot express `../` repairs) — amend as a new instrument version or retire with
   reason next round; the landed repair itself is verified green in both gate modes.
2. Load-stable C3 reading: timeouts read as survivors; `killed()`/`old_killed` timing (lesson
   N-list) — the canonical idle-host receipt stands, but a load-robust counter is owed.
3. C1 counter defects (blank-line sentinel, `> 840` threshold, extra register rows, fences,
   marker-in-prose junk) and a counter that reads correction prose (N1–N4) — already routed to r43.
4. C2 named gaps: 30 part-A mutation survivors (R42w3mutationtester01) extend the coverage-limit
   note; expectation readings and the unclosed holes list (zero-padded/fullwidth `Round:`,
   Control symlink text, FROZEN-EDITED reach, malformed-heading block boundary).
5. S259 scope narrowing (`using/cmdline` page) per R42w2reviewer07 E-5; no superseding row landed.
6. Run-11 waves produced no results.json; w2 seat-count evidence is report files only — disclosed;
   no action owed beyond the note.

## 7. Operator note (promotion is operator-owned)

The four SHONEN boxes carry resolvable `[~]` pointers and every cited surface checked here
resolves (SKILL decision tables/gate rows with committed receipts; end-to-end LOG entries; the
frozen preregistration + four counters executable as written; cross-domain evidence reported, not
absorbed — `waves/w1/R42connector01.md`). A non-author could check all four boxes; this reviewer
writes no `[x]` — SHONEN.md marks are out of closure scope per the protocol.
