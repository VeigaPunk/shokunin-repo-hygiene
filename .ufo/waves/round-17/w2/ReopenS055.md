STATUS: DONE — the primary quote is verbatim (22 words, at #mapping-to-git-branches) and `latest` = v0.46.0 holds. Four cells need changes: id collides (S051→S055); teaches overclaims with two "only"s; scope and anchor leave out § Bookmark updates, which the citing knowledge entry uses; status `mined` holds only if used-by lands.

# ReopenS055 — independent re-open of jj Bookmarks (r17 W2 FALSIFY)

Attacks: `.ufo/waves/round-17/w1/SrcJjBookmarks.md` (seat SrcJjBookmarks). The file is untracked worktree content and is not in ddb7347: `git show ddb7347:.ufo/waves/round-17/w1/SrcJjBookmarks.md` → `fatal: path ... exists on disk, but not in 'ddb7347'`. Lines below are worktree lines (sha256 `2246217b28db5743b7da13be03d182a006c5819d71fc75509c7873b2ed21b380`). Source re-opened 2026-10-20 by this seat.

## 1. Access record (as served 2026-10-20)

- Requested `https://jj-vcs.github.io/jj/latest/bookmarks/` → `HTTP/2 301` `location: http://docs.jj-vcs.dev/latest/bookmarks/` → `HTTP/1.1 301` `Location: https://docs.jj-vcs.dev/latest/bookmarks/` → `HTTP/2 200`. This matches draft :10. The first hop downgrades to http.
- Final page: title `Bookmarks - Jujutsu docs`, canonical `https://docs.jj-vcs.dev/latest/bookmarks/`, generator `mkdocs-1.6.1, mkdocs-material-9.6.23`. 59,728 bytes, sha256 `3679e5b859ad66e054cbe8a40e0cddbbd0b78ac31c0219922d4245f8b5ce2b57`. Headers: `Server: Netlify`, `Etag: "4515b3dc1d342144a300b4720cca19ea-ssl"`, **no `Last-Modified`**, `Date: Tue, 20 Oct 2026 17:37:00 GMT`.
- **Version / "last updated" line served: NONE.** The HTML has 0 matches for `v?0\.\d+\.\d+` and 0 for `last\s+updated` (case-insensitive). It has no `md-version`, `version-selector` or `data-md-component="version"` markup. The only version signal is the mike config `"version": {"alias": true, "provider": "mike"}`, so the selector is rendered client-side. The visible header topic is just `Jujutsu docs`, and the footer is only `Made with Material for MkDocs`. Draft :12 **holds**.
- Revision, resolved outside the page:
  - `https://docs.jj-vcs.dev/versions.json` has 45 entries; `{'version': 'v0.46.0', 'title': 'v0.46.0', 'aliases': ['latest']}`.
  - `/v0.46.0/bookmarks/` is **byte-identical** to `/latest/` (same sha256, same ETag). That is stronger than the draft's "text identical".
  - Tag `v0.46.0` → commit `7d382314f942`, release published `2026-10-07T21:28:17Z`.
  - Last commit touching `docs/bookmarks.md` at the tag: `d91f81a8b2ed` (2026-10-06T17:42:20Z, "docs: explain converting an existing Git repo with jj git init").
- Cross-version check (relevant because the lane observed jj 0.45.1: knowledge draft :21, :38):
  - `/v0.45.0/` and `/v0.45.1/bookmarks/` (59,723 B, sha256 `3c450526dc7869c1…`) render **identical text** to v0.46.0.
  - The only HTML delta is one link target: `#colocated-jujutsugit-repos` → `#colocated-jujutsugit-workspaces`, which is md:233 in the raw diff.
  - Every versioned page's canonical points at `/latest/` (mike behaviour), so the version must come from versions.json, never from the canonical link.

## 2. Primary quote — HOLDS

Draft :18–20: § *Mapping to Git branches* (`#mapping-to-git-branches`), 22 words:
`if you create a `bar` branch in the backing Git repo, then a subsequent `jj git import` will create a `bar` bookmark`

- **Verbatim:** yes.
  - Served raw HTML: `Similarly, if you create a <code>bar</code> branch\nin the backing Git repo, then a subsequent <code>jj git import</code> will create a <code>bar</code>\nbookmark (reminder: …`.
  - I read draft line 20's bytes, stripped the backticks, and found the result as an exact substring of the rendered, whitespace-normalised page text (`True`). The only differences are `<code>` markup and source newlines rendered as spaces. The quote has no non-ASCII characters.
- **≤25 words:** 22.
- **At the named anchor:** yes. The nearest preceding `<h2 id=` in the served HTML is `mapping-to-git-branches`, and the next is `remotes-and-tracked-bookmarks`. In the tagged source it is `docs/bookmarks.md:18-20` under `## Mapping to Git branches` (:14), before `## Remotes and tracked bookmarks` (:23).
- The quote is also present at `/v0.45.0/` and `/v0.45.1/`.
- Caveat: it is a mid-sentence excerpt. It drops the leading "Similarly, " and stops before the parenthetical, so on its own it does **not** carry "automatic in colocated workspaces". That clause needs the 8-word reminder quote `(reminder: that import happens automatically in colocated workspaces)`, verified at md:20-21 (link text = "colocated workspaces"). The two cannot share one ≤25-word span without losing either "backing Git repo" or "colocated" (the joined span is 30 words).

Other quotes the draft or the knowledge entry rely on, each an exact substring of the rendered page:

| quote | words | section (served h2 id) | md line @v0.46.0 |
|---|---|---|---|
| "This record is updated on every `jj git fetch` and `jj git push` of the bookmark." | 16 | remotes-and-tracked-bookmarks | 26-27 |
| "`jj` does not provide a way to manually edit these recorded positions." | 12 | remotes-and-tracked-bookmarks | 28-29 |
| "Jujutsu maps its bookmarks to Git branches when interacting with Git repos." | 12 | **mapping-to-git-branches** | 16 |
| "Bookmarks automatically move when revisions are rewritten (e.g. by `jj rebase`)." | 11 | introduction | 6-7 |
| "There is currently no concept of an active/current/checked-out bookmark." | 9 | introduction | 11-12 |
| "When a commit has been abandoned, all associated bookmarks will be deleted." | 12 | **bookmark-updates** | 160 |

**Draft error (minor):** :30 labels both supporting quotes "§ *Introduction* (`#introduction`)". The :32 quote ("Jujutsu maps its bookmarks …") is the first sentence of **§ Mapping to Git branches** (md:16), not the Introduction. Only :34 is in § Introduction.

## 3. Cell-by-cell verdict (drafted row = draft :48)

Contract: `/home/vgpnk/Projects/shokunin/CORPUS.md`:93-97 (tier scoped to scope; A = official docs), :98 scope, :99-100 anchor, :101 teaches, :103 `mined` = "cited by ≥1 path in `used-by`", :112-115 Rule 1, :146-147 `missing:` census.

| cell | drafted | verdict | corrected text |
|---|---|---|---|
| id | `S051` | **disagree** | `S055`. S051 is also drafted by SrcJjGitCompat.md:47 (its :44 asks that "no other seat may take S051 first"). L1's planned numbering puts jj bookmarks at S055. `corpus/SOURCES.md` at ddb7347 ends at S050 (S05[1-9] count 0). |
| source | `Jujutsu docs, Bookmarks — https://docs.jj-vcs.dev/latest/bookmarks/` | agree | unchanged. It is the served canonical URL; the assigned jj-vcs.github.io URL 301s to it. |
| kind | `docs` | agree | unchanged |
| tier | `A` | agree | unchanged. Official project docs are primary for jj's *documented* bookmark behaviour. They are not observed behaviour, and this seat ran no jj. |
| scope | `jj 0.46.0 bookmark-to-Git-branch mapping and remote-tracking records; not the refs/heads namespace, colocated import/export timing, refs/jj/* storage, or prune safety` | **partial** | `jj 0.45.0–0.46.0 documented bookmark behaviour: mapping to Git branches, a backing-repo branch imported as a bookmark, per-remote last-seen records, moves on rewrite, deletion on abandon, no current bookmark; not the refs/heads or refs/remotes namespace, when colocated import/export runs, refs/jj/* storage, or prune safety`. Everything drafted is on the page and the exclusions are honest (refs/heads, refs/remotes, refs/jj, export, prune: 0 hits each). But the row's own used-by entry, the knowledge draft, cites this page for **abandon → bookmarks deleted** (:37, § Bookmark updates) and **no current bookmark** (:20). Both are outside the drafted scope, while CORPUS.md:98 says the tier applies only to `scope`. The 0.45.x widening rests on the identical-text check in §1. Keep `jj 0.46.0` if L1 prefers the narrower range. |
| anchor | `§ Mapping to Git branches, § Remotes and tracked bookmarks, § Introduction; mike alias … v0.46.0 …, text identical to /v0.46.0/bookmarks/; opened 2026-10-20; served HTML has no version or last-updated line` | **partial** | `§ Introduction, § Mapping to Git branches, § Remotes and tracked bookmarks, § Bookmark updates; docs/bookmarks.md at tag v0.46.0 (7d38231) lines 5-12, 16-21, 25-29, 153-160; mike alias latest = v0.46.0 per https://docs.jj-vcs.dev/versions.json, byte-identical to /v0.46.0/bookmarks/; rendered text identical at /v0.45.0/ and /v0.45.1/; served HTML has no version or last-updated line; opened 2026-10-20`. Every drafted fact was re-verified: the section ids exist, versions.json maps latest to v0.46.0, the text is identical, and no stamp is served. The anchor is still missing § Bookmark updates (see scope), and a line plus commit pin is available (CORPUS.md:99-100). |
| teaches | `bookmarks are jj's branch-equivalent named pointers: a Git branch becomes a bookmark **only** on import (automatic in colocated workspaces) and a remote position updates **only** on fetch or push of that bookmark` | **disagree** | `jj maps bookmarks to Git branches: a branch created in the backing Git repo becomes a bookmark on a subsequent jj git import (automatic in colocated workspaces); bookmarks move with rewritten commits and are deleted when their commit is abandoned; a bookmark's last-seen position on each remote is updated on every jj git fetch and jj git push of the bookmark`. The page states neither "only". (a) It gives import as one route ("a subsequent `jj git import` will create a `bar` bookmark") without saying it is the only one, and the same page names others: pulling a tracked remote bookmark updates "the corresponding local bookmark, which will be created if it doesn't exist already" (§ Remotes and tracked bookmarks), and `jj git clone` tracks the default remote bookmark (§ Automatic tracking). (b) The record is updated "on **every** `jj git fetch` and `jj git push`" — the page does not say these are the only triggers. The page's linked Design Doc, `design/tracking-branches/` md:173-183 at v0.46.0, says `jj git import` "Copies `git_refs` from the backing Git repo", diffs `git_refs["refs/remotes/{remote}"] - remotes[remote]` and "Updates `remotes` reflecting the import". That doc labels itself "a plan" (md:3), and the behaviour was not exercised here (no jj run). |
| status | `mined` | **agree — conditional** | `mined` only if L1 lands `corpus/knowledge/jj-colocation-receipts.md` with :113 `S0??` → `S055`, and the round-17 lesson `## Gate` records the quote. Otherwise `queued`. At ddb7347 neither used-by path is in the tree (`git ls-tree ddb7347 -- <both>` → empty). In the worktree the knowledge entry is untracked (`?? corpus/knowledge/jj-colocation-receipts.md`, 16,253 B) and the lesson is absent (`ls: cannot access … round-17.md`), so the CORPUS.md:146-147 census run now would print `missing: corpus/lessons/round-17.md`. Draft :51's "both paths are absent today" is stale for the knowledge entry. |
| opened | `2026-10-20` | agree | unchanged (re-opened the same day) |
| recheck | `on-release` | agree | unchanged. `latest` moves on every release; the last move was v0.46.0 on 2026-10-07. |
| used-by | `corpus/knowledge/jj-colocation-receipts.md, corpus/lessons/round-17.md` | **agree — conditional** | keep each path only if it lands and cites the row; `—` if neither lands (same evidence as status) |

Corrected row, validated as NF=13 with 11 cells and no `|` inside any cell:

| S055 | Jujutsu docs, Bookmarks — https://docs.jj-vcs.dev/latest/bookmarks/ | docs | A | jj 0.45.0–0.46.0 documented bookmark behaviour: mapping to Git branches, a backing-repo branch imported as a bookmark, per-remote last-seen records, moves on rewrite, deletion on abandon, no current bookmark; not the refs/heads or refs/remotes namespace, when colocated import/export runs, refs/jj/* storage, or prune safety | § Introduction, § Mapping to Git branches, § Remotes and tracked bookmarks, § Bookmark updates; docs/bookmarks.md at tag v0.46.0 (7d38231) lines 5-12, 16-21, 25-29, 153-160; mike alias latest = v0.46.0 per https://docs.jj-vcs.dev/versions.json, byte-identical to /v0.46.0/bookmarks/; rendered text identical at /v0.45.0/ and /v0.45.1/; served HTML has no version or last-updated line; opened 2026-10-20 | jj maps bookmarks to Git branches: a branch created in the backing Git repo becomes a bookmark on a subsequent jj git import (automatic in colocated workspaces); bookmarks move with rewritten commits and are deleted when their commit is abandoned; a bookmark's last-seen position on each remote is updated on every jj git fetch and jj git push of the bookmark | mined | 2026-10-20 | on-release | corpus/knowledge/jj-colocation-receipts.md, corpus/lessons/round-17.md |

## 4. Adjacent findings (advisory, outside the row cells)

- **Draft :51 status rationale overreaches:** "so refs/heads and refs/remotes carry them" is [INFERENCE]. The page never names either ref namespace (0 hits), and the draft's own :52 and its scope cell disclaim this. The Gate should not record it as page-stated.
- **Knowledge draft :36** bolds "Bookmarks map to branches only." The quoted sentence has no "only" — the same overclaim as the teaches cell. Suggested text: "Bookmarks map to Git branches." Its :113 scope ("branch mapping, abandoned bookmarks, no current bookmark") matches the corrected row, not the drafted one.
- **Contradiction check vs C3:** none found. The abandon sentence (md:160) supports the premise that an abandoned commit loses its branch refs, which C3(b′) handles through refs/jj/keep. The keep-ref claim itself is not on this page.

## 5. Verdict and smallest fix

- Primary quote: **holds** (verbatim apart from markup, 22 words, correct anchor). Version line: **holds** (none served; v0.46.0 via versions.json).
- Row: **partial**. Must-fix: id `S051` → `S055`, and remove both "only"s from teaches (corrected text above). Also fix if the knowledge entry keeps its abandon citation: add § Bookmark updates (md:153-160) to scope and anchor. Status and used-by stay `mined` only if the used-by files land and cite S055. Also fix draft :30's section label for the "Jujutsu maps…" quote.

## 6. Commands run (exact) and outputs

1. `read .ufo/waves/round-17/w1/SrcJjBookmarks.md` and `:raw:48-48` → draft and row text (quoted above).
2. `read https://jj-vcs.github.io/jj/latest/bookmarks/` → `URL: https://docs.jj-vcs.dev/latest/bookmarks/`, title and generator as in §1, full page text.
3. `curl -sSIL --max-time 30 https://jj-vcs.github.io/jj/latest/bookmarks/ | grep -iE '^(HTTP/|location)'` → `HTTP/2 301` / `location: http://docs.jj-vcs.dev/latest/bookmarks/` / `HTTP/1.1 301 Moved Permanently` / `Location: https://docs.jj-vcs.dev/latest/bookmarks/` / `HTTP/2 200`.
4. Python urllib (eval) fetch of `/latest/bookmarks/` → `bytes: 59728 sha256: 3679e5b8…`, version strings `[]`, last-updated count `0`, `id="mapping-to-git-branches"` `True`, quote at char 2654, `wordcount: 22`. versions.json → `count: 45`, `latest entry: [{'version': 'v0.46.0', 'title': 'v0.46.0', 'aliases': ['latest']}]`.
5. Python: `/v0.46.0/bookmarks/` → `text identical latest vs v0.46.0: True`, `len 12760 12760`. Term sweep, raw case-sensitive: `refs/jj 0, refs/stash 0, refs/heads 0, refs/remotes 0, export 0, @{u} 0, HEAD 0, last updated 0, checked-out 1, refs/ 0`. No version/date meta tags.
6. Python: mike snippet `"version": {"alias": true, "provider": "mike"}`; `md-version 0`, `version-selector 0`, `data-md-component="version" 0`; header topic `Jujutsu docs`.
7. Python headers: both URLs `Etag: "4515b3dc1d342144a300b4720cca19ea-ssl"`, `Server: Netlify`, no `Last-Modified`.
8. Python byte check of draft line 20 → `repr` as quoted, `non-ascii []`, substring `True`, `words: 22`. Other quotes all `True`; abandon quote's nearest h2 `bookmark-updates`; "Jujutsu maps…" nearest h2 `mapping-to-git-branches`; "Bookmarks automatically move…" nearest h2 `introduction`.
9. Python v0.45.x: `v0.45.1 … bytes 59723 sha256 3c450526dc7869c1`, same for v0.45.0; `text v0.45.1 == v0.46.0: True`, `text v0.45.0 == v0.46.0: True`; primary quote present in both.
10. Python `difflib` HTML v0.45.1→v0.46.0 → a single changed line (`#colocated-jujutsugit-repos` → `#colocated-jujutsugit-workspaces`). Raw `docs/bookmarks.md` diff → only line 233.
11. GitHub API (read): `releases/tags/v0.46.0` → `published_at 2026-10-07T21:28:17Z`; v0.45.1 → `2026-09-03T16:24:38Z`; `commits?path=docs/bookmarks.md&sha=v0.46.0` → `d91f81a8b2ed 2026-10-06T17:42:20Z …`; `git/refs/tags/v0.46.0` → `commit 7d382314f942`.
12. raw `docs/bookmarks.md` at v0.46.0 printed lines 1-30, 150-162 and 233 (line numbers in §2/§3).
13. `/v0.46.0/git-compatibility/` sentence search → "Jujutsu will import and export from and to the Git repo on every jj command automatically."
14. `/v0.46.0/design/tracking-branches/` plus raw `docs/design/tracking-branches.md` at v0.46.0 → md:3 "This is a plan to implement more Git-like remote tracking branch UX."; md:173-183 import steps as quoted.
15. In the lane root: `git ls-tree ddb7347 -- .ufo/waves/round-17/w1/SrcJjBookmarks.md .ufo/waves/round-17/w1/SrcJjGitCompat.md corpus/SOURCES.md` → only `100644 blob ca6672bd… corpus/SOURCES.md`. `sha256sum <draft>` → `2246217b…`. `git show ddb7347:<draft>` → `fatal: … exists on disk, but not in 'ddb7347'`.
16. `git show ddb7347:corpus/SOURCES.md | grep -oE '^\|[[:space:]]*S[0-9]{3,}' | tr -d '| ' | tail -3` → `S048 S049 S050`; `… | grep -cE '^\|[[:space:]]*S05[1-9]'` → `0`.
17. `ls -l corpus/knowledge/jj-colocation-receipts.md corpus/lessons/round-17.md` → lesson `No such file or directory`; knowledge `16253 Oct 20 13:35`. `git ls-tree ddb7347 -- <both>` → empty, rc 0. `git status --porcelain -- <both>` → `?? corpus/knowledge/jj-colocation-receipts.md`.
18. grep `SrcJjGitCompat.md` → `S051` at :1, :44, :47. grep the knowledge draft → bookmarks-page citations at :20, :36, :37 and `S0?? — jj Bookmarks` at :113.
19. read/grep `/home/vgpnk/Projects/shokunin/CORPUS.md` → contract lines as cited in §3.
20. `awk 'NR==48{print "pipes="gsub(/\|/,"|")}' <draft>` → `pipes=12` (drafted row shape OK).

## 7. Probe-rule disclosure

Deviations from the allowed list, all read-only in intent:

- `git status --porcelain -- <2 paths>` is not on the allowed git list, and I did not set GIT_OPTIONAL_LOCKS=0. Evidence it did not write: `stat` shows `.git/index` mtime `2026-10-20 14:24:44.216 -0300`, earlier than this seat's eval-kernel start `14:32:26 -0300` (from `/proc/self/stat`), which preceded the call. `date` at check time: `14:37:00 -0300`.
- `git check-ignore -v <draft>` → rc 1 (not on the list; read-only).
- Non-recursive listings beyond exact-file reads: `ls .ufo/waves/round-17/w1/`, `ls .ufo/waves/round-17/w2/`, `ls corpus/`, and a `read` of `tools/`. None was a recursive search.
- `awk` on one exact file, `date`, and reads of `/proc/stat` and `/proc/self/stat`.

I did not run jj, any census/verify/vault/quarantine tool, or any git write. No /var/tmp scratch was created. The only file written is this report.

Tooling installs/updates: none.
