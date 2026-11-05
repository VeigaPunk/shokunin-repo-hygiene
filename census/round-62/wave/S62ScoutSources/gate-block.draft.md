# S62ScoutSources — Gate block draft (round 62)

Paste-ready `## Gate` content for `corpus/lessons/round-62.md`. Format follows the lane's
round-61 Gate (`corpus/lessons/round-61.md:13-26`): source, URL, anchor, access date, located
quote with word count, scope, and the caveat the row's `teaches` cell carries.

```
Sources opened 2026-11-05 by the wave's scout seat (`S62ScoutSources`); captures and digests in
`census/round-62/sources/` (`SHA256SUMS`).

- **S292 admit** — git-ls-files(1), https://git-scm.com/docs/git-ls-files, OPTIONS `-v`,
  anchor `Documentation/git-ls-files.txt--v`.
  Located quote (17 words): `Similar to -t, but use lowercase letters for files that are marked as assume unchanged (see git-update-index[1]).`
  Scope: the status tags `git ls-files -v` prints for each tracked path. With `-t`, `H` is a
  tracked file that is not either unmerged or skip-worktree and `S` is a tracked file that is
  skip-worktree; `-v` additionally lowercases the tag of a path marked assume unchanged. So a
  tracked path carrying either index bit is not tagged `H`, and `git ls-files -v -z` is the read
  that names it. The row does not document that `git status --porcelain` stays silent for such a
  path; that silence is a round probe on git 2.56.0, not a manual fact.
  Used by `corpus/knowledge/skip-worktree-concealment.md`.

- **S291 re-open (caveat row, unchanged except the recheck cell)** — git-update-index(1),
  https://git-scm.com/docs/git-update-index, NOTES anchor
  `Documentation/git-update-index.txt---notes`.
  Located quote (21 words): `This does not work as expected, since Git may still check working tree files against the index when performing certain operations.`
  Scope: the skip-worktree bit's own limit. The manual gives no guarantee that status stays
  silent for a flagged path; the concealment effect measured this round is a probe on git 2.56.0.
  Re-opened 2026-11-05: the quote reproduces verbatim in a fresh re-fetch, and that re-fetch is
  byte-identical to the stored capture `census/round-61/sources/s291-git-update-index.html`
  (sha256 ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8, 84442 bytes).
  Registry change: recheck `180d` → `2026-11-05`; status `mined` and used-by
  `corpus/knowledge/skip-worktree-concealment.md` unchanged.

- **Rejected inference (carried from round 61): "a silent `git status --porcelain` certifies a
  flagged path's worktree bytes".** The S291 NOTES passage undermines it directly: Git "may still
  check working tree files against the index when performing certain operations". The flip — a
  manual statement that the bit is honoured on every status read — is the falsifier, and it is
  absent from the page. The concealment itself is the round's probe, not a documented guarantee.
```

Access record, per source (both fetched 2026-11-05, `curl -sL`, HTTP 200):

| id | URL | bytes | sha256 | capture |
|---|---|---|---|---|
| S292 | https://git-scm.com/docs/git-ls-files | 69017 | `39bbbe6af002214f7ee3075ab4915fc7af05943869a469b89e3393c8cd6f5f08` | `captures/ls-files.html` |
| S291 | https://git-scm.com/docs/git-update-index | 84442 | `ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8` | `captures/update-index.html` |

Web manual revision strings read from the pages: git-ls-files "last updated in 2.55.0";
git-update-index "last updated in 2.52.0".
