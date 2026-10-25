## Status
STATUS: PARTIAL — agree with ADMIT; independent pin matches, but SHA256SUMS omits the pin and the disposition quote is not an exact transcription.

## Evidence
- `curl -sS --fail --compressed --max-time 60 --max-filesize 5242880 ... https://git-scm.com/docs/git-fetch/zh_HANS-CN` → HTTP 200, final URL unchanged, 156713 bytes. Independent SHA-256 `a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042`; `cmp` against `census/round-28/sources/git-fetch-zh-HANS-CN.html` → identical. Lane snapshot digest and `s119-disposition.tsv` digest match.
- `sha256sum -c census/round-28/sources/SHA256SUMS` (from sources dir) → only `open.html`, `rename.html`, `fsync.html` OK; file has no git-fetch entry.
- Snapshot `census/round-28/sources/git-fetch-zh-HANS-CN.html:3117`, § OPTIONS: `这个功能默认启用。` The same paragraph visibly says `（与 "--[no-]auto-gc" 选项效果一样。）`; preceding synopsis lists `--auto-maintenance` and `--no-auto-maintenance`. Page has `lang="zh_HANS-CN"` and `git-fetch last updated in 2.56.0`.
- Verdict: **AGREE with ADMIT**. The prior rejection reason no longer holds: `corpus/lessons/round-26-verifier-spotcheck.md:47` says `version alignment unprovable, build stamps ambiguous`; today's page is stamped 2.56.0 and decision-time bytes are pinned. The stated flip (later edition drops switch or changes default; recheck on release) is precise. S128 is the English comparator; target `corpus/knowledge/git-auto-maintenance-trigger-set.md` exists.
- Proposed S215 values describe the 11-column schema (docs/A, zh-Hans scope, OPTIONS location, mined, opened 2026-10-25, on-release, prescribed used-by), but the disposition file is a 9-field decision TSV and `corpus/SOURCES.md` has no literal S215 row yet. Current lane HEAD: `0c96332932e66bbaf9cf1c246091d3275a0ab612` (uncommitted wave state). Scratch removed.

## Findings
1. **MEDIUM — missing required checksum receipt.** `census/round-28/sources/SHA256SUMS:1-3` contains only the three POSIX snapshots; its validation emitted three OK lines and no git-fetch line. Although the correct digest is recorded in `s119-disposition.tsv:2`, Exec-C2S119's spec (`.ufo/waves/round-28/w1-spec.json:45`) explicitly requires recording it in SHA256SUMS. L1 should add the pinned snapshot entry before treating the source receipt as complete.
2. **LOW — quote transcription mismatch.** `census/round-28/records/s119-disposition.tsv:2` records `（与 --[no-]auto-gc 选项效果一样。）`, but snapshot line 3117 has `（与 "--[no-]auto-gc" 选项效果一样。）`. The default and switch are supported; correct the quote field so the decision record reproduces the opened visible text.
3. **LOW — no literal S215 registry-row snippet to validate.** The disposition's reason states field values in prose, not an 11-column row; no S215 row is in `corpus/SOURCES.md`. The shape is derivable and the ADMIT rationale is sound, but the executor's requested row snippet remains unmaterialized for L1 integration.

## Attack log
None. No frozen predicate, target, counter, or case set challenged.