# SrcJjBookmarks — jj bookmarks vs Git branches (r17 W1)

STATUS: DONE — jj Bookmarks page opened at v0.46.0; mapping and remote-tracking claims grounded, Git-branch-move timing not stated on this page; row drafted, no contradiction to C3 found.

Assignment: source opening for `corpus/SOURCES.md`; question = bookmarks vs git branches in a colocated repo, when a git branch moves, tracking remote bookmarks. Read only: `CORPUS.md` § SOURCES.md, `corpus/SOURCES.md` header/rows/tail, directory listings to check used-by paths. No lane script run, no repo mutated.

## Access record (as served)

- Requested: `https://jj-vcs.github.io/jj/latest/bookmarks/`
- Redirect chain (`curl -sSIL`): `301` → `http://docs.jj-vcs.dev/latest/bookmarks/` → `301` → `https://docs.jj-vcs.dev/latest/bookmarks/` → `200`.
- Canonical link in served HTML: `https://docs.jj-vcs.dev/latest/bookmarks/`; title `Bookmarks - Jujutsu docs`; generator `mkdocs-1.6.1, mkdocs-material-9.6.23`; footer text is only `Made with Material for MkDocs`.
- **Version line:** the page serves **no version string and no "last updated" line** — `last updated` occurs 0 times and no `0.46`/`v0.x` string appears in the page HTML. The site is mike-versioned (`"version": {"alias": true, "provider": "mike"}`); `https://docs.jj-vcs.dev/versions.json` resolves `latest` → **`v0.46.0`** (`{"version": "v0.46.0", "title": "v0.46.0", "aliases": ["latest"]}`).
- Verified the alias is byte-equivalent in text to the pinned page: flattened text of `/latest/bookmarks/` == `/v0.46.0/bookmarks/` → `True`. All quotes below were also re-verified against `/v0.46.0/bookmarks/`.
- Access date: **2026-10-20**.

## (1) Answering quotes (verbatim, ≤25 words each)

Primary quote (bookmarks vs Git branches, colocated import), § *Mapping to Git branches* (`#mapping-to-git-branches`), 22 words:

> if you create a `bar` branch in the backing Git repo, then a subsequent `jj git import` will create a `bar` bookmark

Colocated trigger, same section, 8 words:

> (reminder: that import happens automatically in colocated workspaces)

Tracking remote bookmarks, § *Remotes and tracked bookmarks* (`#remotes-and-tracked-bookmarks`), 16 words:

> This record is updated on every `jj git fetch` and `jj git push` of the bookmark.

Supporting: what a bookmark is and when it moves, § *Introduction* (`#introduction`), 12 + 11 words:

> Jujutsu maps its bookmarks to Git branches when interacting with Git repos.

> Bookmarks automatically move when revisions are rewritten (e.g. by `jj rebase`).

**When a git branch moves: `not stated`.** The page states creation (`create a bar branch … a subsequent jj git import will create a bar bookmark`) and that import is automatic in colocated workspaces; it does **not** state update-on-move for an existing branch, the moment import is triggered, or the reverse direction (`jj git export` occurs 0 times on the page). The timing lives behind the page's own link to `../git-compatibility/#colocated-jujutsugit-workspaces`, which this seat did not open (not named in the assignment).

Other located statements relevant to the lane:
- "Jujutsu records the last seen position of a bookmark on each remote (just like Git's remote-tracking branches)." (§ Remotes and tracked bookmarks)
- "A remote bookmark can be associated with a local bookmark of the same name. This is called a **tracked remote bookmark** (which maps to a Git remote branch when using the Git backend)." (same section)
- "There is currently no concept of an active/current/checked-out bookmark." (§ Introduction)
- "The notion of tracked bookmarks serves a similar function to the Git notion of an 'upstream branch'." (§ Terminology summary)

## (2) Drafted SOURCES row — exact column order, next unused id

`S051` is the next unused id (`grep -oE '^\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | tr -d '| ' | sort | tail -5` → `S046 S047 S048 S049 S050`; no jj row exists: `grep -in 'jujutsu|jj-vcs|refs/jj' corpus/SOURCES.md` → no output). L1 numbers/renumbers.

| S051 | Jujutsu docs, Bookmarks — https://docs.jj-vcs.dev/latest/bookmarks/ | docs | A | jj 0.46.0 bookmark-to-Git-branch mapping and remote-tracking records; not the refs/heads namespace, colocated import/export timing, refs/jj/* storage, or prune safety | § Mapping to Git branches, § Remotes and tracked bookmarks, § Introduction; mike alias `latest` resolved v0.46.0 via https://docs.jj-vcs.dev/versions.json, text identical to /v0.46.0/bookmarks/; opened 2026-10-20; served HTML has no version or last-updated line | bookmarks are jj's branch-equivalent named pointers: a Git branch becomes a bookmark only on import (automatic in colocated workspaces) and a remote position updates only on fetch or push of that bookmark | mined | 2026-10-20 | on-release | corpus/knowledge/jj-colocation-receipts.md, corpus/lessons/round-17.md |

Notes for L1:
- Status `mined` is claimed because the row grounds C3(a)'s premise (bookmarks are Git branches / remote branches, so refs/heads and refs/remotes carry them) and C3(b)'s premise (bookmarks move on rewrite, so a rewritten predecessor is not branch-reachable) and feeds the C3(c) knowledge entry. **Flip to `queued`, used-by `—`, if neither `corpus/knowledge/jj-colocation-receipts.md` nor `corpus/lessons/round-17.md` lands this round** — both paths are absent today (`ls -l` → No such file; lessons end at `round-16-verifier-spotcheck.md`), and the census's `missing:` sweep would flag the row. If only the lesson lands, keep `corpus/lessons/round-17.md` and drop the knowledge path.
- Do not widen `scope`: the page never names `refs/heads`/`refs/remotes` (0 occurrences each) and never mentions `refs/jj`, `refs/stash`, `HEAD`, `export`, `@{u}` — so it cannot ground the namespace list or the NOT-SAFE verdict by itself.

## (3) Contradiction check against the context claim text

**No statement on this page contradicts C1/C3 claim text.** Negative sweep on the served v0.46.0 text (case-sensitive): `refs/jj`=0, `refs/stash`=0, `refs/heads`=0, `refs/remotes`=0, `export`=0, `@{u}`=0, `\bHEAD\b`=0, `last updated`=0; `checked-out`=1 (the "no concept of an active/current/checked-out bookmark" sentence).

Closest statements, and why they are not contradictions:
- "Jujutsu maps its bookmarks to Git branches when interacting with Git repos." — supports C3(a)'s use of branch refs as roots; it does not say every revision is bookmarked, so it does not contradict a commit being held only by `refs/jj/keep`.
- "Bookmarks automatically move when revisions are rewritten (e.g. by `jj rebase`)." — supports C3(b)'s hidden-predecessor premise (a rewritten commit loses its branch name); it does not claim the predecessor is deleted or prunable.
- "There is currently no concept of an active/current/checked-out bookmark." — consistent with C3(d) "detached HEAD" and "no `@{u}`"; the page offers `name@remote`, not Git upstream syntax. Worth flagging to the helper author: "similar function to … 'upstream branch'" is analogy only.
- The page is silent on `refs/jj/*`, `refs/stash`, `HEAD`, and `jj git export`, so it neither supports nor refutes the "absent worktree head held only by refs/jj/keep is NOT-SAFE" verdict; that verdict needs jj's keep-ref/colocated docs.

## Verdict

- Mapping (bookmarks ↔ Git branches, colocated auto-import) and remote-tracking records: **holds**, tier A, scoped as above.
- "When a git branch moves": **partial / not stated on this page** — only branch *creation* + automatic import in colocated workspaces is stated; move-update, trigger moment and export direction are absent.
- C3 claim text: **no contradiction found**; the page's move-on-rewrite sentence leans with C3(b), not against it.

Smallest fix: keep S051 scoped to mapping/tracking as drafted; if the lane needs the branch-move trigger or write-back, open `../git-compatibility/#colocated-jujutsugit-workspaces` (linked from S051's page) as a separate row and cite it for the timing instead of stretching S051.

## Commands run (all read-only)

1. `read` on `CORPUS.md` and `corpus/SOURCES.md:1-40,43-98` (contract + column shape).
2. `python3` (urllib) fetch of `/latest/bookmarks/` → canonical, generator, footer, version-selector JSON; regex for `[Ll]ast updated`/`Version`/`0.x.y` → zero version/last-updated hits.
3. `curl -sSIL --max-time 30 https://jj-vcs.github.io/jj/latest/bookmarks/ | grep -iE '^(HTTP|location)'` → `301`→docs.jj-vcs.dev (`http`) `301`→`https` `200`.
4. `python3` fetch of `https://docs.jj-vcs.dev/versions.json` → `latest` alias on `v0.46.0`, 45 versions listed.
5. `python3` flatten + equality of `/latest/` vs `/v0.46.0/` text → `latest==v046 text: True`; substring checks for the five quotes → all `FOUND`; term counts as in § 3.
6. `grep -oE '^\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | tr -d '| ' | sort | tail -5` → `S046…S050`; `grep -in 'jujutsu\|jj-vcs\|refs/jj' corpus/SOURCES.md` → empty.
7. `ls -l corpus/knowledge/jj-colocation-receipts.md corpus/lessons/round-17.md` → both absent; `ls corpus/lessons | sort -V | tail` → ends `round-16-verifier-spotcheck.md`.

Tooling installs/updates: none.
