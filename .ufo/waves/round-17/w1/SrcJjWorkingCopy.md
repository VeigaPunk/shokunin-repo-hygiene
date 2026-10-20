STATUS: DONE — jj working-copy page opened; snapshotting/auto-track/ignored stated, nested-repo and `.git`-directory treatment `not stated`; one registry row drafted plus one optional adjacent-page row.

# SrcJjWorkingCopy — jj working-copy source opening (round 17, W1 BUILD)

Assignment: open `https://jj-vcs.github.io/jj/latest/working-copy/`, record the access
date and the version/"last updated" line the page serves, answer the question
(working-copy snapshotting, auto-track, untracked/ignored files, nested repositories /
`.git` directories), draft a SOURCES row, and quote any page statement that contradicts
the context's claim text.

Verdict: **holds with a stated gap** — the page answers snapshotting, auto-track and
ignored files; it does **not** state how nested repositories or `.git` directories are
treated. No statement on the page contradicts the context.

## 1. Access record (requested URL redirects; no version stamp served)

| field | observed |
|---|---|
| requested | `https://jj-vcs.github.io/jj/latest/working-copy/` |
| final / canonical | `https://docs.jj-vcs.dev/latest/working-copy/` (HTTP 200, 47,694 bytes) |
| canonical link | `<link rel="canonical" href="https://docs.jj-vcs.dev/latest/working-copy/">` |
| access date | 2026-10-20 |
| served at | HTTP `Date: Tue, 20 Oct 2026 16:33:39 GMT`, `Server: Netlify`; **no** `Last-Modified` |
| version / "last updated" line | **none served.** No `Last updated` footer, no version selector (`md-version` 0 hits), no version string anywhere in the HTML (`\b0\.\d+(\.\d+)?\b` → 0). Generator meta: `mkdocs-1.6.1, mkdocs-material-9.6.23` |
| docs source | edit link → `https://github.com/jj-vcs/jj/edit/main/docs/working-copy.md`; last commit touching that file on `main`: `a497458e49e89a5559f32f3884e1d5294bd77a4f` (2026-09-17T13:26:48Z, "workspace remove: remove workspace directory") |
| channel | `latest` is the only channel the root offers: `https://docs.jj-vcs.dev/` is a 336-byte JS/meta redirect to `latest/`; guessed versioned paths `…/0.38.0/working-copy/` and `…/0.37.0/working-copy/` both 404. Latest jj release for an `on-release` recheck: `v0.46.0`, published 2026-10-07 (GitHub API `releases/latest`) |

The jj page therefore cannot be pinned to a release; the row pins the docs source commit
`a497458` and the 2026-10-20 serving date instead.

## 2. Verbatim quote answering the question

Primary (14 words), § Introduction, verbatim in the served text and in
`docs/working-copy.md@a497458` (whitespace-normalized, link text unwrapped):

> Most `jj` commands you run will commit the working-copy changes if they have changed.

Facet quotes, each ≤25 words, same anchors and same verification:

| facet | quote | words | anchor |
|---|---|---|---|
| auto-snapshot | "Jujutsu will automatically create commits from the working-copy contents when they have changed." | 14 | § Introduction |
| replacement | "The resulting revision will replace the previous working-copy revision." | 9 | § Introduction |
| auto-track added files | "Also unlike most other VCSs, added files are implicitly tracked by default." | 12 | § Introduction |
| removal / untracked | "Similarly, if you remove a file from the working copy, it will implicitly be untracked." | 15 | § Introduction |
| ignore match | "Files with paths matching ignore files are never tracked automatically." | 10 | § Introduction |
| ignored vs already tracked | "Ignored files are never tracked automatically (regardless of the value of `snapshot.auto-track`)" | 12 | § Ignored files |
| ignore sources | "`.gitignore` files are supported in any directory in the working copy, as well as in `$XDG_CONFIG_HOME/git/ignore` and `$GIT_DIR/info/exclude`." | 18 | § Ignored files |
| stale workspace | "Snapshot the working copy (which gets recorded as an operation)" | 10 | § Stale working copy |

No quote above is paraphrased; each string was tested with `in` against the pinned
markdown after collapsing whitespace and unwrapping `[text](url)` links (all `True`).

## 3. Nested repositories / `.git` directories — `not stated`

The page does not say how a nested repository or a `.git` directory inside the working
copy is treated. It never mentions a nested repo, a submodule, or a bare `.git`
directory. The only `.git*` strings are ignore-file sources: `.gitignore` (twice) and
`$GIT_DIR/info/exclude` (once); the only `.jj*` strings are the workspace's `.jj/`
directory (three times).

Negative sweep, exact command and output (article body only, so mkdocs nav is excluded):

```sh
python3 - <<'PY'
import urllib.request, re
raw = urllib.request.urlopen("https://docs.jj-vcs.dev/latest/working-copy/").read().decode()
body = raw.split('<article class="md-content__inner md-typeset">',1)[1].split('</article>',1)[0]
for p in [r'nested', r'submodule', r'colocated', r'\.git(?![a-z])', r'\.gitignore', r'GIT_DIR', r'refs/', r'bookmark', r'branch', r'\.jj/']:
    print(p, len(re.findall(p, body, re.I)))
PY
```

Observed: `nested 0`, `submodule 0`, `colocated 0`, `\.git(?![a-z]) 0`, `\.gitignore 2`,
`GIT_DIR 1`, `refs/ 0`, `bookmark 0`, `branch 0`, `\.jj/ 3`.

Full-page `nested` hits: 8, all inside mkdocs navigation markup
(`class="md-nav__item md-nav__item--nested"`), 0 in the article. Counting the raw HTML
without that split would overstate presence; the article-body count is the statement
test.

Adjacent pages, opened only to place the gap (not the assigned page; bounded sweep):
`docs/git-compatibility/` — `nested` 0 in its article; `docs/faq/` — `nested` 0.

## 4. Drafted SOURCES row (registry column order, 11 cells)

```md
| S0?? | Jujutsu docs, Working copy — https://docs.jj-vcs.dev/latest/working-copy/ | docs | A | jj working-copy snapshotting, auto-track and ignore-file handling on the docs `latest` channel, which serves no release version | § Introduction; § Ignored files; § Workspaces; § Stale working copy — canonical of https://jj-vcs.github.io/jj/latest/working-copy/; docs/working-copy.md on main at a497458 (2026-09-17); opened 2026-10-20, no version or last-updated line (HTTP Date 2026-10-20 16:33 GMT) | most jj commands snapshot the working copy into a revision replacing the previous working-copy revision: a removed file is implicitly untracked, an added file is tracked unless an ignore file (including `$GIT_DIR/info/exclude`) matches | queued | 2026-10-20 | on-release | — |
```

- `id` — left as `S0??`; next unused numeral is **S051** (S050 is the last row). Before
  assigning, check `ScribeSourcesRows.md` / `SrcJjBookmarks.md` in this directory for a
  jj row drafted by a sibling; dedupe rather than allocate twice.
- Column shape validated by substituting `S051`: `awk -F'|'` NF = 13, no stray `|`
  inside any cell (checked programmatically on the literal row text).
- `kind` docs, `tier` A scoped to that page's own statement (official jj docs, section
  anchors above). Tier is not a truth claim about jj behavior at other revisions.
- `status` **queued** — reason: it grounds the snapshot/untracked mechanism but no
  knowledge entry cites it yet (`corpus/knowledge/jj-colocation-receipts.md` does not
  exist as of this write: read returned not found). It cannot ground C3(a)/(b): the page
  contains no `refs/`, `bookmark` or `branch` statement.
  Flip (logged old→new, per SOURCES rule 2): if
  `corpus/knowledge/jj-colocation-receipts.md` cites this row, set `status mined` and
  `used-by corpus/knowledge/jj-colocation-receipts.md`.
- `recheck` `on-release` — docs are the `latest` channel; the next jj release is the
  trigger (current `v0.46.0`, 2026-10-07).
- `used-by` `—` while queued.

### 4b. Optional adjacent-page row (not the assigned page; L1 decides/merges)

The assigned page says nothing about `.git` coexistence; `git-compatibility` does, and it
also carries the detached-HEAD statement the context's C3(d) recipe claim needs. Opened
and pinned this round, so a row is permissible; drop it if a sibling already drafted it.

```md
| S0?? | Jujutsu docs, Git compatibility — https://docs.jj-vcs.dev/latest/git-compatibility/ | docs | A | documented jj/Git coexistence: colocated workspaces, ref import/export, detached HEAD, submodules, ignore sources; not nested-repository treatment | § Colocated Jujutsu/Git workspaces; § Supported features (Submodules, .gitignore) — canonical of https://jj-vcs.github.io/jj/latest/git-compatibility/; docs/git-compatibility.md on main at d91f81a (2026-10-06); opened 2026-10-20, no version or last-updated line | jj imports and exports with the Git repo on every command and usually leaves Git in a detached HEAD state with no currently tracked branch; submodules never show up in the working copy | queued | 2026-10-20 | on-release | — |
```

Grounding quotes (verified against `docs/git-compatibility.md@d91f81a`, bold/link
markers stripped):

- "Jujutsu will import and export from and to the Git repo on every `jj` command automatically." — 16 words, § Colocated Jujutsu/Git workspaces.
- "`jj` commands will usually put the Git repo in a \"detached HEAD\" state" — 13 words, same section; the full sentence adds "since in `jj` there is not concept of a \"currently tracked branch\"" (25 words total if the entire sentence is wanted).
- "A colocated Jujutsu workspace is a hybrid Jujutsu/Git workspace." — 9 words, same section.
- "Submodules: No. They will not show up in the working copy, but they will not be lost either." — 18 words, § Supported features.
- "This creates a colocated Jujutsu workspace, there will be a `.jj` directory and a `.git` directory." — 16 words, § Creating an empty repo.

Status stays `queued` under the same rule: `jj-colocation-receipts.md` does not yet exist
to cite it. Same flip applies.

## 5. Contradictions with the context's claim text

**None.** No statement on the assigned page contradicts C1, C2 or C3. Checked per claim
with the sweep in §3 (article-body counts in brackets):

- C3(a) durable roots `refs/heads`, `refs/tags`, `refs/remotes` only, never `refs/jj/*`:
  page has no ref statement (`refs/` 0, `bookmark` 0, `branch` 0) — silence, not
  contradiction. The page's "automatically create commits from the working-copy
  contents" does not say where the resulting revision is referenced, so it must not be
  quoted as support for "the head is not on a branch".
- C3(b) `--glob=refs/jj/keep/*` in unpushed checks: no statement (`refs/` 0).
- C3(d) detached HEAD / no `@{u}`: not on this page (`branch` 0); the adjacent
  git-compatibility page states detached HEAD **supporting**, not contradicting, the
  recipe claim.
- C3(e) empty untracked `…/p6repo/.git` stub causes phantom deletions: page says nothing
  about a `.git` directory (`\.git(?![a-z])` 0). Its removal sentence is consistent with
  the observed mechanism — a tracked file absent from the working copy is implicitly
  untracked by the snapshot — but the page does not state the `.git`-stub cause, so it is
  mechanism context, not a contradiction and not proof of the fixture observation.
- C3's "colocated" edge class: page has 0 "colocated" hits; silent.
- C1 (`status.showUntrackedFiles=no` false-clean) and C2 (seat-audit precision): unrelated
  git/python surfaces; nothing on the page touches them. The page's "added files are
  implicitly tracked by default" is jj behavior and must not be transferred to git status.

No contradictory quote to report.

## 6. Commands run (exact, with observed output)

1. Web read of `https://jj-vcs.github.io/jj/latest/working-copy/` → final
   `https://docs.jj-vcs.dev/latest/working-copy/`, 200, 47,694 bytes.
2. `python3` (urllib) fetch of the same URL: `final https://docs.jj-vcs.dev/latest/working-copy/`,
   `server Netlify`, `last-modified None`, `date Tue, 20 Oct 2026 16:33:39 GMT`.
3. Regex sweep on the raw HTML: `md-version` 0, `colocat` 0, `\b0\.\d+` 0,
   `Last updated` 1 (the body phrase "last updated to", § Stale working copy) — i.e. no
   footer stamp.
4. Article-body sweep (§3 command): counts as listed; `nested`/`submodule`/`colocated`/
   `.git`(non-ignore) all 0 in the article.
5. Pinned source fetch `https://raw.githubusercontent.com/jj-vcs/jj/a497458e49e89a5559f32f3884e1d5294bd77a4f/docs/working-copy.md`
   → 6,517 bytes; headings `## Introduction`, `## Conflicts`, `## Ignored files`,
   `## Workspaces`, `## Stale working copy`; every quote above `in` the normalized text
   (`True`); `nested` 0, `submodule` 0, `colocated` 0.
6. GitHub API `repos/jj-vcs/jj/commits?path=docs/working-copy.md&per_page=1` →
   `a497458e49e89a5559f32f3884e1d5294bd77a4f`, `2026-09-17T13:26:48Z`.
7. GitHub API `repos/jj-vcs/jj/releases/latest` → `v0.46.0`, `2026-10-07T21:28:17Z`.
8. `https://docs.jj-vcs.dev/` → 336-byte redirect page to `latest/`;
   `…/0.38.0/working-copy/` and `…/0.37.0/working-copy/` → HTTP 404.
9. Adjacent pages opened for the gap placement and the optional row:
   `…/latest/git-compatibility/` (11,957 chars of article text) and `…/latest/faq/`
   (24,897 chars) — `nested` 0 in both; pinned `docs/git-compatibility.md@d91f81a`
   (2026-10-06) and verified the five quotes above (`True`).
10. Registry checks: `grep -i 'jujutsu|\bjj\b|jj-vcs' corpus/SOURCES.md` → no matches
    (no existing jj row); `corpus/knowledge/jj-colocation-receipts.md` read → not found.

Tool installs/updates: none.

## 7. Smallest fix / recommendation for L1

1. Allocate **S051** (check sibling drafts first) with the §4 row, keep `status queued`,
   and schedule the status flip the moment `corpus/knowledge/jj-colocation-receipts.md`
   lands and cites it.
2. Do **not** cite this page for C3(a)/(b) ref roots or for the `.git`-stub phantom
   deletions; it is silent on all three. For the colocated `.git`/detached-HEAD premises
   use the §4b row (or a sibling's equivalent), not this page.
3. If the lane needs a citable answer to "how are nested repositories or `.git`
   directories treated", it is still unopened ground: neither the working-copy page nor
   the git-compatibility or FAQ pages say `nested` (0 hits each). Open the jj design docs
   or the jj source before making that claim; until then the honest registry state is a
   lead, not a row.
