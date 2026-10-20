# Round 16 — DraftOperatorQuestion (souji)

Seat: `SoujiR16.DraftOperatorQuestion` (scribe, leaf). Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Read-only over committed bytes and the exact tool file; no gate, census run, test, commit or install.

## Draft L0 operator question (at most one)

souji | round-16 | Adjudicate as an explicit operator scope change, not a no-harm improvement, these residual safety-motivated contractions against pre-harm a31642d: (a) a repository whose attributes bind a configured `filter.*.clean|smudge|process` driver (for example `filter=lfs`) now reports `status-unverifiable` with no dirty count, instead of a count; and (b) a repository whose config is could-not-evaluate but reaches no protected path (include cycle or depth over 10, `~user` include, hardlinked or non-regular include target, NUL or unparsable config, invalid `extensions.worktreeConfig`) now emits one `error` row and no counts. Accept both, or direct the lane to restore counts for benign cases with an effect-aware check?

Why this needs operator scope adjudication (r14 closure, `corpus/lessons/round-14-verifier-spotcheck.md:160`): the closure states that when broader safe configurations remain intentionally unsupported, the lane must "obtain explicit operator/canonical scope-change adjudication; do not call that a no-harm improvement." Both contractions are absent from pre-harm a31642d (which has no config guard at all, `guard_git_config` is round-14 code), so they are regressions in supported surface that the lane's tested namespace cases do not offset. The r14 closure rejected the same shape of trade (`round-14-verifier-spotcheck.md:104–106`).

## Evidence (exact file:line, tool `tools/souji-census.sh`, sha256 `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`)

Worktree matches HEAD `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` for this path: `git status --porcelain -- tools/souji-census.sh` empty; `git diff --stat cbf688a -- tools/souji-census.sh` empty.

Contraction (a), filter drivers, code path confirmed:
- `guard_bound_filters()` 907–932 returns 1 when an attributes source binds a configured driver to a tracked path.
- `count_dirty()` 939–944 then prints `status-skipped: filter-driver-bound` on stderr and `unverifiable`; `census_one()` 1135–1136 sets `dirty=0` plus flag `status-unverifiable`. The repo loses its dirty count; other repos are unaffected (no `exit`). This matches the header claim (lines 98–100) and fixture case `R15CFG-14`.
- Pre-harm a31642d ran status unconditionally, so the driver case is a real count loss, not a relabel.
- [INFERENCE, not executed] `filter=lfs` with repo-local `filter.lfs.*` is the common benign instance that loses its count. No real-directory probe was run (forbidden).

Contraction (b), could-not-evaluate degrade, code path confirmed:
- `cfg_soft()` 554–558; `guard_config_file_kind()` 561–570 (non-regular, hardlinked include target); depth/cycle 582–584; NUL/unparsable 586–590; `~`/`%(` unsupported 611–612; invalid `worktreeConfig` boolean 635–636.
- `census_one()` 1087–1091 emits `error` row, zero counts, exit 0, stderr `config-unsupported`. This is the intended r16 degrade; it is per-repository, so unaffected rows survive.

Additional lane-owned defects (not operator questions; the lane must fix or disclose at L1, per `corpus/lessons/round-15-verifier-spotcheck.md` R1/R3 discipline):
1. Header claim contradicted: lines 88–92 say only a protected-namespace reach keeps whole-run exit 2. Whole-run `protected_fail` (exit 2) is reached for non-protected reasons:
   - `git-metadata-hardlink` / `-nonregular` / `-unavailable` in `guard_git_files()` 505–518 (called from `guard_git_surface()` 772–828, invoked per repo at 1087);
   - `git-metadata-symlink` for any `.git` link resolving outside gitdir, `guard_git_links()` 492–497;
   - `ambiguous-path` for tab/newline/CR in a lexical path, `guard_path` 379–381 (also worktree paths 1048–1049).
   Whether any of these is a "protected namespace" is a classification the lane must state; as written the claim is false for them.
2. Claim-vs-code gap for `~user`: header lines 93–95 promise `~user`/`%(prefix)` degrade to one `error` row. For `core.excludesFile` / `core.attributesFile`, `status_info_file()` 878–879 calls `protected_fail "git-config-unsupported"` (exit 2, whole run). Only the include path (611–612) degrades. Fixture case `R15CFG-03` exercises `~user` only on include (`tests/fixtures/r15-census-config.py:469`), so this path is untested. This converts a could-not-evaluate config into a whole-run abort, the exact r14 harm shape.
3. Partial clone: `GIT_NO_LAZY_FETCH=1` (147) makes a status that needs a missing blob fail, giving `status-unverifiable` where pre-harm could lazily fetch. The header says "as before round 14" (105–107), which is not the pre-harm baseline; list it as a contraction vs a31642d in the L1 report.

## Verdict on the draft question

Warranted. It is the only residual contraction set that is safety-motivated (filter drivers execute; config refusals guard reach) and that reduces supported-surface counts for repos reaching no protected path. Items 1–3 above are defects, not scope trades, and should not be routed as operator questions.

## Commands

```
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-14-verifier-spotcheck.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-15-verifier-spotcheck.md; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse cbf688ab2ab28e38103e5a9417ca525b5f2ed423 a31642d cc21683 b410186
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- tools/souji-census.sh; git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh; sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
```

Non-shell reads (exact files, `read`/`grep` tools): `corpus/lessons/round-14-verifier-spotcheck.md`; `corpus/lessons/round-15-verifier-spotcheck.md`; `tools/souji-census.sh` (grep and ranged reads 184–200, 480–563, 859–938, 1079–1095); `tests/fixtures/r15-census-config.py` (grep).

Tool installs/updates: none.

STATUS: ok. Draft only; the census gate was not run and the fixture was not executed, so the claim that the fixture covers case 14 and the r16 oracle is unverified here.
