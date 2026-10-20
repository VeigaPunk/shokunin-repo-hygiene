STATUS: DONE — jj git-compatibility page opened 2026-10-20 (`latest` = v0.46.0); located 25-word quote answers HEAD/detached; index reset and bookmark mapping are `not stated`; SOURCES row drafted as S051 (mined).

# Source opening — jj "Git compatibility"

## Access record

- Requested `https://jj-vcs.github.io/jj/latest/git-compatibility/` → **301** → `https://docs.jj-vcs.dev/latest/git-compatibility/` (canonical per `<link rel="canonical" href="https://docs.jj-vcs.dev/latest/git-compatibility/">`). Final response 200, 61,334 bytes, fetched **2026-10-20** (response `date: Tue, 20 Oct 2026 16:33:42 GMT`, `server: Netlify`). Local copy sha256 `db9c9a760810386858e6b1bad4a7a334c56bd48c77692dbc1c343657ae0ca254`.
- Version the page serves: **`latest` alias = v0.46.0**, confirmed from `https://docs.jj-vcs.dev/versions.json` (200): `[prerelease, {v0.46.0, aliases:[latest]}, v0.45.1, v0.45.0, v0.44.0, …]`.
- "Last updated" line: **the page serves none.** 0 matches for `last[ -]updated|git_revision|revision-date` in the HTML, and no `Last-Modified` response header (only `cache-control: public,max-age=0,must-revalidate`, `etag: "02aec1f4984867c2018ec2e52d542385-ssl"`). The only in-content version stamp is `since version 0.30.0` (§ Format mapping details, change-id header paragraph) and the `git.write-change-id-header` setting.
- Curation note for the row: cite **docs.jj-vcs.dev**, not the github.io URL (the github.io path is a redirecting alias).

## (1) Answer

**Primary located quote (25 words exactly, verbatim):**

> "jj commands will usually put the Git repo in a "detached HEAD" state, since in jj there is not concept of a "currently tracked branch"."

Location: **§ Colocated Jujutsu/Git workspaces**, paragraph 3 (the paragraph beginning `It is allowed to mix jj and git commands in such a workspace in any order.`), anchor `#colocated-jujutsugit-workspaces`. Verbatim quirks preserved: straight double quotes; `there is not concept` (sic).

**Second located quote for the index half (22 words, verbatim):**

> "The staging area will be ignored. For example, jj diff will show a diff from the Git HEAD to the working copy."

Location: **§ Supported features**, bullet `Staging area: Kind of.` (anchor `#supported-features`). Restated as a colocation disadvantage: `Jujutsu will ignore Git's staging area. It will not understand merge conflicts as Git represents them, unfinished git rebase states, as well as other less common states a Git repository can be in.` (§ Colocated Jujutsu/Git workspaces, disadvantages list).

**Explicitly `not stated` on this page:**

1. **Whether jj resets/rewrites/refreshes the git index.** The word `index` does **not occur anywhere** on the page (0 case-insensitive `\bindex\b` matches across the whole HTML). The page says only that the staging area is *ignored*; ignoring is not resetting, so a "jj leaves the git index stale" or "jj rewrites the index" claim has no support here.
2. **How branches/bookmarks map onto git refs.** § Branches (anchor `#branches`) contains exactly: `TODO: Describe how branches are mapped`. The only mapping statements are indirect: conflicted jj branches disagree with the git-side position and are labelled `branch@git` (disadvantage bullet); non-colocated workspaces may have `no branches at all (not even a main branch) or … branches that are out of date with jj's bookmarks` unless `jj git import`/`jj git export` are run.
3. **HEAD's exact target in prose.** It appears only as a fenced-shell comment in § Converting a workspace into a colocated workspace: `# Convince jj to update .git/HEAD to point to the working-copy commit's parent` followed by `jj new && jj undo`. `[INFERENCE]` This is consistent with HEAD = `parent(working-copy commit)`, which is rewritten by ordinary jj operations — the operational reason a receipt must not root on HEAD — but the page states the mechanism only in that comment, not as a normative sentence.

**Other page statements bearing on C3 (each verbatim):**

- `The Git repo and the Jujutsu workspace then share the same working copy. Jujutsu will import and export from and to the Git repo on every jj command automatically.` (§ Colocated, ¶1) — git-side refs are refreshed by **every** jj command, so git-side reads of a colocated repo see post-jj state.
- `It is allowed to mix jj and git commands in such a workspace in any order.` (§ Colocated, ¶3) — with the qualification that read-only git is preferred and `Before doing mutating Git commands, you may need to tell Git what the current branch should be with a git switch command.` (this is the detached-HEAD recipe C3(d) needs).
- `You can undo the results of mutating git commands using jj undo and jj op restore. Inside jj op log, changes by git will be represented as an "import git refs" operation.` (§ Colocated, ¶4).
- `Commits created by jj have a ref starting with refs/jj/ to prevent GC.` (§ Format mapping details, ¶2, anchor `#format-mapping-details`) — the only refs-namespace statement on the page; note it says `refs/jj/`, **not** `refs/jj/keep/` (`refs/jj/keep` does not occur).
- `It should be safe to run git gc in the Git repo, but it's not tested, so it's probably a good idea to make a backup of the whole workspace first.` (§ Supported features, bullet `Garbage collection: Yes.`).
- `Detached HEAD: Yes. Jujutsu supports anonymous branches, so this is a natural state.` (§ Supported features).
- In colocated workspaces with many refs, `jj commands can get noticeably slower because of the automatic jj git import executed on each command`; mitigated by `jj util gc` `(that command includes packing the Git refs)`.

## (2) Drafted SOURCES row (registry's parameter order: id · source · kind · tier · scope · anchor · teaches · status · opened · recheck · used-by)

Id note: highest existing id is `S050`; next unused is **S051** — **L1 assigns the final number** (the row's id cell must not be reused, and no other seat may take S051 first).

```
| S051 | jj docs, Git compatibility — https://docs.jj-vcs.dev/latest/git-compatibility/ | docs | A | jj 0.46.0 colocated Jujutsu/Git workspaces: git HEAD, refs/jj/ keep refs and the ignored git index | § Colocated Jujutsu/Git workspaces ¶1, ¶3; § Supported features › Staging area, Detached HEAD, Garbage collection; § Branches; § Format mapping details ¶2; § Converting a workspace into a colocated workspace; docs.jj-vcs.dev `latest` = v0.46.0 per versions.json 2026-10-20; page serves no last-updated stamp | jj imports and exports git refs on every command and usually leaves git in detached HEAD (no currently tracked branch); the git staging area is ignored, and jj-created commits carry a refs/jj/ ref to prevent GC | mined | 2026-10-20 | on-release | corpus/knowledge/jj-colocation-receipts.md |
```

Cell checks against `SOURCES-CONTRACT-v1`: 11 columns, no `|` inside any cell; `kind=docs`; `tier=A` scoped to official jj docs for jj 0.46.0 documented behaviour (not observed behaviour — this seat ran no `jj`); `status=mined` because it grounds C3(a) (refs/jj/ refs are GC keep refs, so they are not receipt roots) and C3(d) (detached HEAD, `git switch` before mutating git) this round.

**Landing condition (census rule 7: mined rows' `used-by` paths must exist):** `corpus/knowledge/jj-colocation-receipts.md` is a round-17 deliverable (C3c), not yet present. Land this row **with or after** that entry, otherwise the "mined rows whose used-by paths do not exist" census prints `missing:` and the row fails. If C3c is dropped, flip the two cells to `queued` / `—` and keep `teaches` as is.

**`recheck` rationale:** `on-release`, because the row is anchored to the `latest` alias, which moves at every jj release (v0.46.0 at time of opening); `90d` would be a fallback if L1 prefers a date.

**`teaches` honesty bound:** it deliberately does *not* claim bookmark↔ref mapping (page says `TODO`) and does not claim jj resets the index (page never uses the word). Both omissions are the `not stated` items above.

## (3) Contradictions with the context's claim text

**None found.** No sentence on the page contradicts the C1/C2/C3 claim text. Four statements are near enough to misread as one, so they are quoted with the reading that keeps them consistent:

1. `It should be safe to run git gc in the Git repo, but it's not tested, so it's probably a good idea to make a backup of the whole workspace first.` (§ Supported features › Garbage collection). Does **not** rescue `SAFE(metadata-prune)`: it speaks about object GC, not about whether a worktree head is durable. Paired with `Commits created by jj have a ref starting with refs/jj/ to prevent GC.`, it actually confirms C3(a)'s direction — a commit held only by a `refs/jj/` ref is invisible to a roots list restricted to refs/heads, refs/tags, refs/remotes, so the receipt must be NOT-SAFE rather than SAFE(metadata-prune).
2. `Moreover, unless you explicitly use jj git import and jj git export commands, that Git repository will either have no branches at all (not even a main branch) or will have branches that are out of date with jj's bookmarks.` (§ Colocated, ¶5). Scoped to `--no-colocate` workspaces; the lane's repos are colocated (C3 opening premise), so it narrows scope but contradicts nothing.
3. `When a jj branch is conflicted, the position of the branch in the Git repo will disagree with one or more of the conflicted positions.` (§ Colocated, disadvantages). This *does* undercut any receipt that treats `refs/heads` read from git as authoritative inside a colocated repo — but the claim text already demotes refs/jj/* and HEAD, and nothing in it asserts git-side refs are always in agreement. Flag as a scope caveat for the knowledge entry, not a contradiction.
4. Scope gap, not a contradiction: the page grounds only `refs/jj/` (`Commits created by jj have a ref starting with refs/jj/`), never `refs/jj/keep/*`. C3(b)'s exact glob `--glob=refs/jj/keep/*` is **not** grounded here; the `keep` sub-namespace needs its own source (or must be described as jj-internal in the knowledge entry). `[INFERENCE]` Because the page says *every* jj-created commit carries a `refs/jj/` ref, a `keep`-only glob is a narrower selector than "all jj-created commits" — the two statements are compatible only if `keep` is where jj parks hidden predecessors, which this page does not state.

**Verdict per facet of the question:** holds — jj leaves git in detached HEAD and has no tracked-branch concept; every jj command imports/exports git refs; the git staging area is ignored; refs/jj/ exists to prevent GC. `not stated` — whether jj resets the index (word absent), and how branches/bookmarks map to git refs (§ Branches is a TODO). Partial — `refs/jj/keep/*` specificity.

## Commands run (exact, with outputs)

```
$ curl -sS -o jj-gitcompat.html -w '%{http_code} %{size_download}\n' https://jj-vcs.github.io/jj/latest/git-compatibility/
301 162
$ curl -sSL -o jj-gitcompat.html -w '%{http_code} %{size_download} %{url_effective}\n' https://jj-vcs.github.io/jj/latest/git-compatibility/
200 61334 https://docs.jj-vcs.dev/latest/git-compatibility/
$ curl -sS -o jj-versions.json -w '%{http_code}\n' https://docs.jj-vcs.dev/versions.json
200        # -> {"version":"v0.46.0","aliases":["latest"]} is element 2 of the list
$ curl -sSI https://docs.jj-vcs.dev/latest/git-compatibility/ | grep -iE 'last-modified|etag|date|server'
cache-control: public,max-age=0,must-revalidate
date: Tue, 20 Oct 2026 16:33:42 GMT
etag: "02aec1f4984867c2018ec2e52d542385-ssl"
server: Netlify      # no last-modified
$ grep -oE '<h[1-6] id="[^"]*"' jj-gitcompat.html
# h2: supported-features, creating-an-empty-repo, creating-a-repo-backed-by-an-existing-git-repo,
#     creating-a-repo-by-cloning-a-git-repo, colocated-jujutsugit-workspaces, branches, format-mapping-details
# h3: in-the-same-working-copy-colocated, in-a-separate-working-copy,
#     converting-a-workspace-into-a-colocated-workspace
$ python3 (HTML→text; strip tags; unescape)
occurrences of "index" (case-insens): 0
25 words | present verbatim in page text: True     # detached-HEAD quote
22 words | present verbatim in page text: True     # staging-area quote
13 words | present verbatim in page text: True     # refs/jj/ quote
"TODO: Describe how branches are mapped" present: True
"keep" in refs/jj context: False                   # refs/jj/keep absent
"last updated"/revision-date markers: 0
$ sha256sum jj-gitcompat.html
db9c9a760810386858e6b1bad4a7a334c56bd48c77692dbc1c343657ae0ca254  jj-gitcompat.html
```

Tooling: nothing installed or upgraded (no pacman/uv/npx/cargo use). No lane file read beyond `/home/vgpnk/Projects/shokunin/CORPUS.md` § SOURCES.md and `corpus/SOURCES.md` (header, existing rows, id census); no `jj` and no git write was run.

Search log (one line, contract rule 5): question = jj↔git colocation semantics for HEAD/bookmarks/index, searched only the canonical jj docs page + its versions.json on 2026-10-20; identified 1 page, screened 7 sections, included 6 section anchors, excluded 0; stop rationale = authoritative source hit on first query, remaining gaps (`index` reset, bookmark mapping) are documented TODOs/absences on that source, not search misses.
