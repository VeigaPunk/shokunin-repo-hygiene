# round-12 — non-author verification and spot-check (orchestrator, kaika)

Written by the integrator, not the lane (CORPUS.md: corrections and outside reviews are new
files; the lane owns `round-12.md`). Verifiers were fresh agents dispatched by the orchestrator
after the round landed at `2a363a03d`; full reports are committed in the fleet repo at
`.ufo/waves/kaika-w3/souji-review.md` and `souji-critic.md`.

## Spot-check (LEARNING.md — at least one admit and one reject)

| decision | sample | verifier | result |
|---|---|---|---|
| admit | K1–K4 admissions (git grace periods / `--expire-to`, `git repo structure`, duplicate-finder detection-vs-deletion, FreeDesktop Trash spec) — reviewer re-ran K1–K4 rechecks; agree (K2 after the corrected `MANWIDTH=2000` recheck) | W3ReviewSouji | agree |
| reject | K5 `quarantine-same-filesystem-rename.md` — the reviewer found its Gate claimed a committed fixture that does not exist; the lane moved K5 to HELD in `2a363a0` — agree with the hold | W3ReviewSouji | agree |

## Adjudication

ADMITTED after post-review fixes `2a363a0` (S030 recheck `—`→`365d`; K5 admitted→held; Q16 withdraws the circular Q15; K2 recheck corrected; C1 restated as a rule-coverage count). Per-axis: calibration improved (mistake classes naming an existing rule 28/52→51/53 — a coverage count, not proof of catches; QUALITY.md 15 criteria each citing a lesson), coverage improved (admitted entries 0→4 on 3 frontier areas; capability `sources-registry`, 33 rows, census ok), operability improved (`r12-maintenance-guard.sh --selftest` 6/6: git 2.55 auto-maintenance can prune an unlocked worktree registration on a plain commit; `-c maintenance.auto=false` / `git worktree lock` prevent it). Trends: expansion improved, quality improved, discernment improved (the lane's own post-commit reviewer + critic found 10 defects, fixed pre-commit; outside hold on K5 accepted). Debts: quarantine tool timeout; certification stays OFF.
