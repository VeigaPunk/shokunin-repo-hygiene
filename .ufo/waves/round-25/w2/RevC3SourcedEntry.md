# RevC3SourcedEntry — review of `corpus/knowledge/git-repo-structure-common-dir.md` (W2, read-only)

Reviewed 2026-10-25 against SOURCES S124/S125/S126/S127, the round-25 source snapshots,
the committed blobs at HEAD (a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe), and independent
re-runs. Lane: souji-shokunin; leaf seat, no subagent dispatch.

## STATUS: PASS with 2 findings (1 evidence-hygiene gate failure on S127; 1 minor quote-glyph deviation)

Gate check list:

| Check | Result | Evidence |
|---|---|---|
| Provenance trio first (`source:`/`verified-at:`/`recheck:`) | PASS | entry lines 1–5, in order |
| Front matter `ground: F2` | PASS | entry line 6 |
| S124 quote exact, ≤25 words | PASS | 23 tokens; verbatim vs snapshot `gitrepository-layout.5.txt:2302-2304` |
| S125 quote exact, ≤25 words | PASS | 6 tokens; verbatim vs snapshot `git-rev-parse.1.txt:2917` under `--git-common-dir` heading (line 2915) |
| S126 quote exact, ≤25 words | **FINDING 2 (minor)** | 11 tokens; sentence verified in snapshot `git-worktree.1.txt:2860` (DETAILS section, line 2845), but source glyph is U+2019 `worktree’s`; entry/SOURCES-row quote uses ASCII `worktree's` |
| S127 rejection located (reason + flip) | PASS | entry line 70; SOURCES row S127 status=rejected, teaches=REJECTED:…; flip: |
| S127 sweep evidence reproducible | **FINDING 1 (gate)** | cited snapshot `census/round-25/sources/gitglossary.7.txt` does not exist (tree, git, SHA256SUMS); documented `grep -ciE 'common\|COMMON_DIR' …` exits rc=2 with no output — “yielded 0” not reproducible from that path. Conclusion itself independently confirmed (below) |
| Recheck cadence allowed | PASS | rows `on-release`; entry `on-release` + `180d`; contract allows `90d`/`180d`/`on-release` (CORPUS.md § SOURCES.md line 105–106) |
| Sources opened this round | PASS | S124–S127 `opened: 2026-10-25`; snapshots dated Oct 25 09:42; `sha256sum -c SHA256SUMS` OK for S124/S125/S126 |
| `used-by` paths exist | PASS | all 4 rows → `corpus/knowledge/git-repo-structure-common-dir.md` exists |
| No unsupported claim | PASS | see attack log |
| No literal pipe outside tables | PASS | pipe chars only inside decision table (lines 38–43) and inside inline-code regex (line 70) |
| README coverage map F2 row (Q56) | PASS | `corpus/README.md:544` entries column lists `knowledge/git-repo-structure-common-dir.md` (SOURCES S124–S126) |

## Numbered findings

1. **[gate] S127 rejection evidence path missing.** `census/round-25/sources/gitglossary.7.txt`
   does not exist: not in the working tree (only `gitrepository-layout.5.txt`,
   `git-rev-parse.1.txt`, `git-worktree.1.txt` + `SHA256SUMS`, which lists only those three),
   not tracked (`git ls-files census/round-25/sources/` empty), no history. The entry line 70
   and SOURCES row S127 cite the `grep -ciE 'common|COMMON_DIR' census/round-25/sources/gitglossary.7.txt`
   sweep; re-running it now returns `grep: …: No such file or directory` rc=2 (no stdout), so the
   claimed “yielded 0” is not reproducible as documented. Independent confirmation of the rejection
   conclusion: installed `gitglossary(7)` 2.56.0-1 man page `grep -ciE 'common|COMMON_DIR'` → 0
   matches (rc=1), and the live page (git-scm.com/docs/gitglossary) contains no common-directory
   definition; the quoted sentence “most of which are shared among other worktrees of a single
   repository” is verbatim in the live § worktree definition and in the installed man page. Fix:
   re-add the gitglossary snapshot (with SHA256SUMS entry) or re-anchor the sweep to the installed
   man page / live page and record the actual exit code.
2. **[minor] S126 quote glyph deviation.** Source text (web snapshot `git-worktree.1.txt:2860`
   and installed `git-worktree(1)` man page) reads `…the main worktree’s $GIT_DIR` with U+2019
   right single quote; the entry Gate line 66 and SOURCES row S126 render `worktree's` with ASCII
   apostrophe. Same sentence, 11 words, semantics identical — typographic not verbatim. Under a
   strict exact-quote standard this is a deviation; consider quoting the U+2019 form.

## Attack log (independent probes, all read-only)

- `git --version` → `git version 2.56.0` (entry line 4/48 host claim OK).
- Probe call claim: `tools/souji-repo-structure.sh:181` uses `rev-parse --path-format=absolute --absolute-git-dir`;
  `:193` uses `rev-parse --path-format=absolute --git-common-dir` → “S125 § --git-common-dir is the
  exact probe call” and the r13 `--absolute-git-dir` envelope statement hold.
- Probe-blob claim: `git rev-parse HEAD:tools/souji-repo-structure.sh` = `0f42ebf5afac31e8dbddfc67de6b30ef96e4806c`
  = working-tree `git hash-object` → “unchanged probe blob 0f42ebf5afac” is a git blob OID, exact and unchanged.
- Selftest re-run (scratch): `TMPDIR=/var/tmp/souji-r25-RevC3 bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`
  → `selftest=PASS ids=7/7`, `selftest rc=0`. Linked case: `linked-common-dir … rc=0 common_entries=53 private_entries=9 checks=8 control=PASS verdict=PASS`;
  colocated case: `colocated-vs-plain … others_plain=0 others_colocated=2 commits_plain=1 commits_colocated=2 differing_keys=8 precondition=colocated-not-interchangeable-with-plain-baseline verdict=PASS`.
  Matches entry lines 15–34 and the C3 after-target. Base receipt `census/round-25/records/c3-control-base.tsv` (5/5, `tool_sha256=b6bf52056d…`, rc=0) is the pre-data control.
- Installed man pages confirm provenance: `gitrepository-layout(5)` contains the commondir sentence;
  `git-rev-parse(1)` contains `--git-common-dir` (line 354) and `$GIT_COMMON_DIR` (357);
  `git-worktree(1)` line 505 contains the within-linked-worktree `$GIT_COMMON_DIR` sentence.
- Web snapshot footers: `gitrepository-layout last updated in 2.49.0`, `git-rev-parse last updated in 2.56.0`,
  `git-worktree last updated in 2.56.0` → entry lines 1–3 “last updated” claims OK. The interval claim
  “2.49.1 → 2.56.0 no changes” has no local changelog snapshot — verification gap, not contradicted.
- Frozen census checks for rows S124–S127 (NF=13, tier/status/kind/recheck enums) — no violations; all used-by paths exist.

## Residual risk / verification gaps

- S127 sweep evidence as written is unreproducible (FINDING 1); rejection verdict rests on my
  independent 0-match checks, not on the documented snapshot.
- “2.49.1 → 2.56.0 no changes” not locally evidenced (web page only shows latest-updated).
- Entry and sources are W1 uncommitted drafts (expected pre-landing); no committed snapshot of the
  entry itself exists to diff against.
