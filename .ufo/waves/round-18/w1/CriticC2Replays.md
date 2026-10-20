# CriticC2Replays — does LG-DANGLING-PTR break the r18 landing pipeline?

STATUS: DONE — the finding is compatible with the wave/landing pipeline only under a
commit-order contract the current round does not yet enforce; the two failure modes it
creates both have in-tree precedents.

Axes: calibration (primary — PTR is a calibration finding; false findings would *lower*
calibration), operability (landing-order usability), coverage (checked-file set).

## Verdict: holds (conditional)

LG-DANGLING-PTR does **not** flag seat-report or census-record citations in
`corpus/lessons/round-18.md` *provided* the observed r16/r17 landing order is kept —
the gate resolves every token against `git ls-tree REV` (committed bytes only, never
the working copy: `tools/souji-landing-gate.py:20-24`), so resolution is a pure
commit-order question, and the existing carry channel already forces the same
"committed-at-REV" invariant onto `.ufo/waves/round-18/*.md`
(`tools/souji-landing-gate.py:368-375` raises `EvalError` → exit 2 when no `.md`
reports exist under the wave prefix at REV). PTR only *generalizes* that existing
hard requirement from wave reports to every cited path — it introduces no new class
of constraint. The risk is therefore not a design conflict but an *order discipline*
defect that the check itself now makes loud.

## Answered directly

**Would it flag lesson tokens citing `.ufo/waves/round-18/` seat reports committed only
at the end?** Yes — exactly and correctly — if the lesson commit lands before or in a
tree missing the reports commit, or if `--rev` is measured at any such rev. Today
`.ufo/waves/round-18/w1/{ScribeLessonDraft,ScribeProvinceProc,ScribeRowsGit,
ScribeRowsProc,ScribeRowsPy,SrcFifoOpenNonblock}.md` and `w1-spec.json`,
`w1-dispatch.json`, `w1-dispatch-attempts.txt`, `make-w1.py`, `swarm-registry.json`
are all **untracked** (`git ls-files --others`). A gate run at HEAD right now exits 2
(`no .md reports under .ufo/waves/round-18/`) — a correct could-not-evaluate, but it
proves the failure is live, not hypothetical: any rev committed between a
lesson-lands-first order and the reports commit is permanently PTR-red on replay.

**Would it flag `census/round-18/` records written after the measured commit?**
Any `census/round-18/` record cited in a scanned file must be committed at or before
the rev the gate measures. `census/round-18/leaked-procs-before-1631.txt` is untracked
at b576341 and is already named in the round context — if the lesson cites it, it must
be committed in c_records/c_docs below. Records generated *after* the measured tip
(the r16/r17 `gate-landing.json` pattern) can never be cited by round-18 scanned
files; they become citable only from round 19 on.

## Landing order that makes the gate meaningful

For every scanned file S (SKILL.md, SCORECARD.md, PROVINCE.md, corpus/QUALITY.md,
corpus/README.md, corpus/knowledge/*.md, corpus/lessons/round-18.md, LOG.md's
round-18 section) citing token P: `commit(S) ≥ commit(P)`, and the measured tip T
must contain both. Concretely:

1. `c_reports` — every `.ufo/waves/round-18/` artifact seat reports plus wave
   specs/dispatch/registries (r17 precedent: `95519a7`, which also carried the
   landed-rev census records).
2. `c_records` — every `census/round-18/` record the round's prose will cite, plus
   `corpus/pointer-exemptions.tsv` rows covering deliberate non-file tokens
   (quarantine stub, `.ufo/state`, `.ufo/watchdog.log`-shaped deliberate paths).
   Same-commit-with-citer is legal: r16 `163158a` committed
   `census/round-16/c1-matrix-landing.json` **in the same commit** as the lesson
   citing it (`git show 163158a --stat`) and resolved at measured rev `6ff91f5`.
3. `c_docs` — lesson, LOG round-18 section, SKILL/SCORECARD/PROVINCE/QUALITY/README.
4. `python3 tools/souji-landing-gate.py --root lane --rev T --round 18` where T is
   the tip after step 3 and every cited path ∈ tree(T). The gate measures the tip
   that carries every cited file — never an earlier rev, never the working copy.
5. `c_evidence` — landing evidence for *this* run (r16 `c46eabf` "gate evidence at
   6ff91f5", r17 `2cfc6c0` "evidence at d98065d"; in both cases resolved_rev is the
   parent, not self). **Must not be cited by any round-18 scanned file.**

## Failure modes when a record is cited before it is committed

- **F1 — dangling at the measured rev (loud, intended).** Any scanned file citing a
  path absent from tree(T) → exit 1 with `LG-DANGLING-PTR`. Includes same-name
  files that exist only in the working copy: untracked `w1/*.md` bytes resolve
  nowhere for the gate.
- **F2 — permanent replay residue.** A rev committed between a cite-first commit
  and the cited file's commit carries the finding forever; history cannot be
  amended. This is worse than F1: it pollutes every future `--round 18` replay of
  that rev even when the tip lands green. Order must be enforced per-commit, not
  "eventually."
- **F3 — name drift on regeneration (precedent exists).** LOG.md:916 cites
  `census/round-17/gate-replays-ddb7347.json`; the committed record is
  `gate-replays-4f48343.json` (added `95519a7`; `git ls-files census/round-17`
  shows no `-ddb7347` file ever landed). The citation was drafted against the
  pre-landing rev-suffixed name and landed stale. Any rev-suffixed record that is
  regenerated under a new name breaks every existing citation — PTR finds it, but
  only as damage already done.
- **F4 — self-citation of landing evidence (unsatisfiable).** A lesson citing the
  gate-evidence commit's own record can never resolve at the measured rev (the
  record postdates T by construction). Both r16 and r17 avoided this only by
  discipline; nothing enforces it.
- **F5 — frozen-record interior check.** A `census/round-18/` frozen record citing
  itself or post-measure blobs in `files[*]` hits `LG-FROZEN-MEASURED`
  (`tools/souji-landing-gate.py:538-593`) even when its *name* resolves — the
  pin-vs-measured-commit check runs inside the record, orthogonal to PTR.
- **F6 — fleet masking (low likelihood, high precision cost).** A token missing in
  the lane but present in the fleet is classified `fleet`, not a finding. Verified
  the class is load-bearing: `.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`,
  `.ufo/reports/round-17/souji.md`, `.ufo/prompts/souji-round-17.md`,
  `.ufo/l0-questions.md`, `.ufo/state/*`, `.ufo/watchdog.log` are fleet-only paths
  already cited by lane docs. But a lane filename *typo'd into* a fleet-existent
  path is silently masked — the fleet repo currently carries no `.ufo/waves/round-*`
  paths (fleet `git ls-files .ufo/waves` → `aggregator-r11/`, `hyaku/` only), so
  wave-report citations cannot be masked today; the risk attaches to generic
  `tests/`, `corpus/`, `.ufo/` shapes if the fleet later adds colliding paths.

## Smallest safe corrections

1. **Commit-order contract**: enforce `commit(S) ≥ commit(P)` by keeping the
   reports→records→docs→gate→evidence order; treat any cite-first intermediate rev
   as a landing defect even if the tip is green (F2). Merge reports into the docs
   commit when atomicity is cheaper (r16 precedent).
2. **Stable citation names**: cite records by their committed name; when a
   rev-suffixed record is regenerated, update every citation in the same commit
   (F3 — the only unresolved r17 dangler outside routed items is exactly this).
3. **Gate evidence exemption discipline**: scanned files for round N never cite
   round-N's own `gate-landing`-class record (F4); nothing in the gate enforces it,
   so it needs a checklist line in PROVINCE or the integrator recipe.
4. **Exemptions committed before/at the citing commit**: `corpus/pointer-exemptions.tsv`
   rows for deliberate non-files (nested `.git` fixture dirs like
   `tests/vault/vadv54-run/p/p6repo/.git`, quarantine stub) must land in step 2,
   not after the gate has already gone red.
5. **Directory resolution**: the checker must count tree *directories* as resolving
   (`census/round-16/transcripts`, `corpus/knowledge/` are cited as dirs); a
   blob-only lookup would false-positive on legitimate dir citations — worth a
   selftest case.
6. **Spotcheck naming note**: `corpus/lessons/round-N-verifier-spotcheck.md` does
   not match the `round-N.md` scan target, so its citations (it already cites the
   dangling `gate-replays-ddb7347.json` at :150) sit outside the check — acceptable
   (it is post-gate outside closure) but worth recording as a deliberate gap.

## Commands run (all read-only; no installs, no mutations)

- `git ls-files .ufo census corpus/lessons`; `git ls-files --others --exclude-standard census/round-18 .ufo/waves/round-18` → round-18 artifacts untracked.
- `git log --format='%h %ad %s'` → landing order `95519a7`(reports+records) → `d98065d`(docs) → `2cfc6c0`(gate evidence at d98065d) → `b576341`(spotcheck).
- `git ls-tree 6ff91f5 -- census/round-16/*` + `git log --diff-filter=A` → r16 `final`/`landing` records resolve at measured rev; `c1-matrix-landing.json` added in the same commit `163158a` as the citing lesson (atomic landing).
- `git show d98065d:LOG.md` → `gate-replays-ddb7347.json` cited at :916, name never committed (F3).
- Fleet `git ls-files .ufo` → fleet-only targets for the `fleet` class; no fleet `.ufo/waves/round-*` collision (F6).
- Reads: `tools/souji-landing-gate.py:20-58,368-433,538-702` (committed-tree basis, carry EvalError, measured-commit check, evaluate order).
