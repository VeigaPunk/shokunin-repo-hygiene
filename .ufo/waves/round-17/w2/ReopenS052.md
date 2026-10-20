STATUS: DONE — S052 primary quote is verbatim (14 words) at § Introduction; version/last-updated cell holds; 8/11 drafted cells agree, 1 partial (anchor over-lists § Workspaces), 2 disagree (id must be S052, not S051; teaches cell overstates auto-track and drops the "if changed" condition).

# ReopenS052 — independent re-opening of jj "Working copy" (round 17, W2 FALSIFY)

Assigned source: S052, `https://jj-vcs.github.io/jj/latest/working-copy/`, re-opened 2026-10-20.
Wave-1 draft under test: `.ufo/waves/round-17/w1/SrcJjWorkingCopy.md` (untracked file; not in
ddb7347 — `git cat-file -e ddb7347:.ufo/waves/round-17/w1/SrcJjWorkingCopy.md` → fatal, exists on
disk only). Registry target: `corpus/SOURCES.md` at ddb7347 (98 lines; header line 13; last row
S050 at line 64; no S051+ row).

## 1. Access record, independently observed 2026-10-20

| field | observed |
|---|---|
| requested | `https://jj-vcs.github.io/jj/latest/working-copy/` |
| redirect chain | `HTTP/2 301` GitHub.com → `http://docs.jj-vcs.dev/latest/working-copy/` → `HTTP/1.1 301` Netlify → `https://docs.jj-vcs.dev/latest/working-copy/` → `HTTP/2 200` |
| final | `https://docs.jj-vcs.dev/latest/working-copy/`, 47,694 bytes |
| served stamps | `Date: Tue, 20 Oct 2026 17:33:09 GMT`; `ETag: "fe028c3484ada3686843c17d7342d3a5-ssl"`; `Server: Netlify`; **no `Last-Modified` header** |
| body digest | `sha256(served HTML) = 947d0c56c02f9c10b4c14e8aaa8cc3f435f7650536ab9386ef6a52f1d64ff3c7` |
| version / "last updated" line | **none served.** Footer text is exactly `Made with Material for MkDocs`; `md-version` 0 occurrences in the HTML; no `versions.json` reference in the page (0); no `0.x.y` string (`0\.\d+\.\d+` → 0). Generator `mkdocs-1.6.1, mkdocs-material-9.6.23` |
| site versioning (out-of-band) | `https://docs.jj-vcs.dev/versions.json` → HTTP 200, 3,525 bytes, 45 entries; `v0.46.0` carries alias `latest`; `v0.45.1` present without alias |
| release identity | `https://github.com/jj-vcs/jj/releases/latest` → `302 Location: .../releases/tag/v0.46.0` |
| docs source pin | edit link → `docs/working-copy.md` on `main`; API last commit touching it `a497458e49e89a5559f32f3884e1d5294bd77a4f` (2026-09-17T13:26:48Z); `raw.githubusercontent.com/.../main/docs/working-copy.md` is **byte-identical** to the `a497458` blob: both 6,517 bytes, `sha256 = d7c31dd75ba6f9c4a272c50da4cd2973751e95cee2f3dc571ba032da9bec6875` |

Verdict on wave-1's version row (w1:24): **holds**. The page serves no version or
last-updated line. Two refinements: (a) the theme JS carries
`"version": {"alias": true, "provider": "mike"}`, so versioning is configured even though
no selector is rendered (`md-version` 0, `versions.json` unreferenced in the page); (b)
the `latest` channel resolves out-of-band to `v0.46.0` via `versions.json`, so "cannot be
pinned to a release" is true only of the page's own stamp — site metadata does bind it,
subject to the alias moving.

## 2. Primary quote — VERBATIM check

Quote as drafted (w1:33): `Most `jj` commands you run will commit the working-copy changes if they have changed.`

Observed (all independent, this seat):

- Served article text, tags stripped and whitespace collapsed, contains the quote with inline
  code rendered as bare `jj`: `True`. Raw HTML at served line 2005 is
  `Most <code>jj</code> commands you run will\ncommit the working-copy changes if they have changed.`
  — character-exact after unwrapping the one inline `<code>` element and the source line wrap.
- Word count: **14** (≤25). Sentence boundary matches: the quote is a complete sentence ending U+002E.
- Anchor: **§ Introduction**. Heading offsets in the normalized article:
  Introduction 14, Conflicts 1403, Ignored files 3038, Workspaces 3740, Stale working copy 5079;
  quote offset 386 → last heading before it is Introduction.
- Pinned markdown source `docs/working-copy.md@a497458`, whitespace-normalized, contains the
  same literal quote: `True` (backticks present in the source). Headings in the source:
  `## Introduction`, `## Conflicts`, `## Ignored files`, `## Workspaces`, `## Stale working copy`.

Verdict: **holds, exactly**. No correction to the primary quote, word count, or anchor.

Non-material error in the facet table only: w1:42 counts the "auto-snapshot" quote
("Jujutsu will automatically create commits from the working-copy contents when they have
changed.") as **14** words; it is **13**. The quote itself is present at § Introduction.
All other facets re-verified present at their named anchors (auto-snapshot 13,
replacement 9, auto-track added 12, removal 15, ignore match 10, ignored-vs-tracked 12 at
§ Ignored files, ignore sources 18 at § Ignored files, stale 10 at § Stale working copy).

## 3. Silence claim (nested repos / `.git`)

Wave-1 §3: **holds.** Independent counts, article body only (markup-aware):
`nested 0`, `submodule 0`, `colocated 0`, `\.git(?![a-z]) 0`, `refs/ 0`, `bookmark 0`,
`branch 0`; `.jj/ 3`, `.gitignore 2`, `GIT_DIR 1`. Same counts in
`docs/working-copy.md@a497458` (`nested 0`, `submodule 0`, `colocated 0`,
`.git` non-ignore 0). The only "last updated" string in the article is the body phrase
"last updated to" (§ Stale working copy), not a stamp.

## 4. Per-cell verdict on the drafted S052 row (w1:88, 11 cells confirmed)

| # | cell | drafted | verdict | corrected cell text |
|---|---|---|---|---|
| 1 | id | `S0??`, with prose "next unused numeral is **S051**" (w1:91) | **DISAGREE** | `S052`. L1's planned numbering reserves S051 for jj git-compatibility (the same draft's §4b page); SOURCES at ddb7347 ends at S050 (line 64), so both are free, but the working-copy row is S052. Change the prose recommendation at w1:188 from "Allocate **S051**" to "Allocate **S052**". |
| 2 | source | `Jujutsu docs, Working copy — https://docs.jj-vcs.dev/latest/working-copy/` | **AGREE** | optional precision: append the observed redirect (`jj-vcs.github.io` 301 → `docs.jj-vcs.dev` 301 → https 200) if the registry wants the requested URL recorded; the canonical is correct as written. |
| 3 | kind | `docs` | **AGREE** | — |
| 4 | tier | `A` | **AGREE** | — official jj documentation; versionless official-docs pages already hold tier A (S048 at SOURCES.md:62, S049 at :63). Keep wave-1's caveat that A scopes to this page as served, not to jj 0.45.1 behavior. |
| 5 | scope | "jj working-copy snapshotting, auto-track and ignore-file handling on the docs `latest` channel, which serves no release version" | **AGREE** | optionally add `(mike alias latest → v0.46.0, 2026-10-07)` — true as written, but "serves no release version" describes the page stamp only; the channel identity is resolvable from `versions.json`. |
| 6 | anchor | `§ Introduction; § Ignored files; § Workspaces; § Stale working copy — canonical ...; docs/working-copy.md on main at a497458 (2026-09-17); opened 2026-10-20, no version or last-updated line (HTTP Date 2026-10-20 16:33 GMT)` | **PARTIAL** | drop `§ Workspaces` (no quote or claim in the row rests on it; it is scope-adjacent padding) **or** add a workspace claim. Add the byte receipt: `ETag "fe028c3484ada3686843c17d7342d3a5-ssl", 47,694 bytes; docs pin a497458 verified still current (main byte-identical, sha256 d7c31dd7…)`. Keep `§ Stale working copy`: the stale quote ("Snapshot the working copy (which gets recorded as an operation)") does support the snapshot mechanism. |
| 7 | teaches | "most jj commands snapshot the working copy into a revision replacing the previous working-copy revision: a removed file is implicitly untracked, an added file is tracked unless an ignore file (including `$GIT_DIR/info/exclude`) matches" | **DISAGREE — overstates** | "when the working copy has changed, most jj commands snapshot it and the resulting revision replaces the previous working-copy revision; added files are auto-tracked by default unless `snapshot.auto-track` excludes them or an ignore file (including `$GIT_DIR/info/exclude`) matches; a removed file becomes implicitly untracked" |
| 8 | status | `queued` | **AGREE at ddb7347; flip imminent** | at the landed rev the cited file is absent: `git cat-file -e ddb7347:corpus/knowledge/jj-colocation-receipts.md` → `fatal: ... exists on disk, but not in ddb7347`; the worktree file is untracked (`git ls-files --error-unmatch` → pathspec error). But the reason text in w1:98 ("does not exist as of this write") is stale: the draft now exists and references this URL (`corpus/knowledge/jj-colocation-receipts.md:51` marks it `sourced`; `:112` lists it under "Source rows to number" as `S0??`). Keep `queued` at ddb7347; when the draft lands numbered, set `mined` and `used-by corpus/knowledge/jj-colocation-receipts.md`. |
| 9 | opened | `2026-10-20` | **AGREE** | — |
| 10 | recheck | `on-release` | **AGREE** | — `v0.46.0` confirmed as the release behind `latest` (302 + versions.json). |
| 11 | used-by | `—` | **AGREE** while queued | becomes `corpus/knowledge/jj-colocation-receipts.md` on the status flip. |

Substantive overreach detail for cell 7, with page text:

- Page: "Most `jj` commands you run will commit the working-copy changes **if they have
  changed**." The draft drops the condition, implying unconditional snapshotting.
- Page: "added files are implicitly tracked **by default**"; "The `snapshot.auto-track`
  config option controls which paths get automatically tracked when they're added to the
  working copy"; ignore files then "are never tracked automatically". The draft's "tracked
  unless an ignore file matches" makes ignore the only exception and silently promotes the
  default to a rule. The knowledge draft itself records `snapshot.auto-track="none()"`
  behavior (`jj-colocation-receipts.md:52-54`), so the omission is not academic.

Cell 6 is a list-precision defect, not a page-content overclaim: every listed section exists,
but § Workspaces carries no claim in this row.

The §4b git-compatibility row is a different source and was **not** re-opened or verified by
this seat; its five quotes remain unverified here.

## 5. Commands run (exact; outputs abbreviated only where quoted above)

1. `read https://jj-vcs.github.io/jj/latest/working-copy/` → final `https://docs.jj-vcs.dev/latest/working-copy/`, 47,694 bytes, canonical meta `https://docs.jj-vcs.dev/latest/working-copy/`.
2. `python3` urllib fetch of the requested URL → `status 200`, `Date Tue, 20 Oct 2026 17:32:27 GMT`, `Etag "fe028c3484ada3686843c17d7342d3a5-ssl"`, no `last-modified`; article 6,344 chars plain / 6,412 markup-aware.
3. Markup-aware extraction (`<code>`→backticks, `<a>`→text, tags stripped, whitespace collapsed): primary quote `in` → `True`; 14 words; heading offsets `Introduction 14 … Stale working copy 5079`; quote at 386 → anchor Introduction. All 8 facet quotes found at the anchors tabulated in §4.
4. Full-HTML regex sweep: `Last updated` 0 (footer has no stamp); `md-version` 0; `versions.json` 0; `0\.\d+\.\d+` 0; footer text `Made with Material for MkDocs`; JS config `"version": {"alias": true, "provider": "mike"}`.
5. `curl -sSIL https://jj-vcs.github.io/jj/latest/working-copy/` → `301` GitHub → `http://docs.jj-vcs.dev/...`; `301` Netlify → `https://docs.jj-vcs.dev/...`; `200`, `content-length: 47694`, ETag as above, no `Last-Modified`.
6. `curl -sS https://docs.jj-vcs.dev/versions.json` → HTTP 200, 3,525 bytes, 45 entries; `v0.46.0` aliases `["latest"]`.
7. `curl -sSI https://github.com/jj-vcs/jj/releases/latest` → `302 location: .../releases/tag/v0.46.0`.
8. GitHub API `repos/jj-vcs/jj/commits?path=docs/working-copy.md&per_page=1` → `a497458e49e89a5559f32f3884e1d5294bd77a4f`, `2026-09-17T13:26:48Z`. (A later API call hit the unauthenticated rate limit; releases/tags were resolved via the HTML redirect and versions.json instead.)
9. `curl` raw `docs/working-copy.md` at `a497458` and at `main` → both 6,517 bytes, `cmp` equal, sha256 `d7c31dd7…`; headings as listed; quote literals present; `nested|submodule|colocated|.git(non-ignore) = 0`.
10. `grep -Fn` on the raw markdown → the primary/facet quotes are line-wrapped in source, hence normalized comparison used (literal single-line grep is not a valid absence test here).
11. Registry/repo reads: `git show ddb7347:corpus/SOURCES.md | grep -nE '^\| S05[0-9]'` → only S050 (line 64); header line 13; file 98 lines. `git cat-file -e ddb7347:corpus/knowledge/jj-colocation-receipts.md` → fatal (absent); `git ls-files --error-unmatch` → untracked; draft lines 51, 112-114 read.
12. Row parse: `row.split('|')[1:-1]` → **11** cells for S052, matching the 11-column header at SOURCES.md:13.

Tool installs/updates: none. Temporary work under `/var/tmp/souji-r17-ReopenS052/` (served HTML + both markdown copies) deleted after use.

## 6. Smallest fix for L1

1. Land the row as **S052**, not S051; fix the prose at w1:188. Leave S051 to the §4b
   git-compatibility row.
2. Replace the teaches cell with the corrected text in §4 cell 7 (restore "when changed";
   restore `snapshot.auto-track` as an exception before ignore files).
3. In the anchor cell, delete `§ Workspaces` (or attach a workspace claim) and add the
   ETag/byte receipt; keep § Introduction, § Ignored files, § Stale working copy.
4. Keep `status queued` at ddb7347; on landing the existing untracked knowledge draft with
   its `S0??` placeholders numbered, flip to `mined` / `used-by corpus/knowledge/jj-colocation-receipts.md`.
5. Correct w1:42's facet count 14 → 13 (record-only; no registry impact).

## 7. Verdict and remaining unknowns

**Primary quote: holds** (verbatim, 14 words, § Introduction, served page and pinned source).
**Version/last-updated cell: holds** (none served; footer only).
**Cells: 8 agree, 1 partial (anchor), 2 disagree (id → S052; teaches overstates).**

Remaining unknowns (none block the row):
- L1's planned S051/S052 split is taken from the round context; confirm against the
  ScribeSourcesRows draft before committing (a sibling may have renumbered).
- Whether the knowledge draft lands citing S052 verbatim (it currently uses `S0??`); the
  status flip is conditional on that.
- How nested repositories / `.git` directories are treated is still absent from this page,
  `git-compatibility` and `faq` (wave-1's 0-hit claims), so it remains a lead, not a row.
