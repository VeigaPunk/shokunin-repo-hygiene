STATUS: DONE — jj config page opened at v0.46.0; both snapshot settings located and quoted; SOURCES rows drafted; no page statement contradicts the claim text.

# SrcJjConfigSnapshot — jj `snapshot.auto-track` and `snapshot.max-new-file-size`

Seat: scout, WAVE 1 BUILD. Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Question: exact semantics and defaults of `snapshot.auto-track` and
`snapshot.max-new-file-size`.

## 1. Source opening record

| field | value |
|---|---|
| requested URL | `https://jj-vcs.github.io/jj/latest/config/` |
| redirect chain | `301` → `http://docs.jj-vcs.dev/latest/config/` → `301` → `https://docs.jj-vcs.dev/latest/config/` (observed 2026-10-20) |
| canonical served | `https://docs.jj-vcs.dev/latest/config/` (`<link rel="canonical">`) |
| access date | 2026-10-20; HTTP response `date: Tue, 20 Oct 2026 16:33:51 GMT` |
| version the `latest` alias serves | `v0.46.0` — `curl -fsS https://docs.jj-vcs.dev/versions.json`, entry `{"version":"v0.46.0","aliases":["latest"]}` |
| release date | `v0.46.0` published `2026-10-07T21:28:17Z` — GitHub releases API `tags/v0.46.0` |
| “last updated” line | **none served.** `grep -c -i "last updated"` on the HTML → `0`; the page carries no footer revision stamp. Recorded instead: canonical + mike version selector `latest` = v0.46.0. |
| served HTML sha256 | `4b8047e3309f42d9af06fc8dbd7328e7b37fa61c6e965a9723692a6de7a3bc5b` |
| tagged doc source | `https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/docs/config.md` sha256 `edc5c53c0c90591f92e066106cc4b4cf7423d6bd28a4f4b4e2496cc9c258bc03`; lines 2193–2235 carry the two sections byte-for-byte as served |
| anchors present in HTML | `id="snapshot-settings"`, `id="paths-to-automatically-track"`, `id="maximum-size-for-new-files"` (also `id="default-colocation"`) |

The page's own statement of where built-in defaults live: “The built-in settings. These cannot be edited. They can be viewed in the
[`cli/src/config/`](https://github.com/jj-vcs/jj/blob/main/cli/src/config/) directory in `jj`'s source repo.”

## 2. (1) Located verbatim quotes

Three quotes, each ≤25 words, because the page answers one key per sentence; stated verbatim from the served page and the v0.46.0 tag.

**Q1 — `snapshot.auto-track`, default behaviour.** 17 words.
Anchor: § Snapshot settings › Paths to automatically track (`#paths-to-automatically-track`).

> All new files in the working copy that don't match the ignore patterns are tracked by default.

**Q2 — `snapshot.auto-track`, semantics.** 19 words.
Anchor: same section (`#paths-to-automatically-track`).

> You can set the `snapshot.auto-track` to set which paths get automatically tracked when they're added to the working copy.

**Q3 — `snapshot.max-new-file-size`, semantics and default.** 21 words.
Anchor: § Snapshot settings › Maximum size for new files (`#maximum-size-for-new-files`).

> `jj` will refuse to add new files to the snapshot that are larger than a certain size; the default is 1MiB.

### Additional page-stated semantics (verbatim, same anchors; not the headline quote)

- `#paths-to-automatically-track`: “Files with paths matching ignore files are never tracked automatically.”
- `#paths-to-automatically-track`: “If you set `snapshot.auto-track` to a non-default value, untracked files can be tracked with `jj file track`.” — so the key is a fileset pattern, not a boolean; a non-default value can leave additions untracked until explicitly tracked.
- `#paths-to-automatically-track`: untracking with `jj file untrack` is undone immediately unless the path is ignored or removed from the `snapshot.auto-track` patterns.
- `#maximum-size-for-new-files`: “Files that already exist in the working copy are not subject to this limit.”
- `#maximum-size-for-new-files`: “Setting this value to zero will disable the limit entirely.”
- `#maximum-size-for-new-files`: human-readable suffixes `B`, `MiB`, `GB`, etc.; no suffix or raw integer means bytes.

### Not stated on the page (explicit gap)

The page states the *behavioural* default of `snapshot.auto-track` (“tracked by default”) but does **not** state the literal built-in value. For the exact value I opened the built-in config the page points to:
`https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/cli/src/config/misc.toml` sha256
`5380373a7943a9b0d04c2b47c01e06d56045150252a9f62858e247d2108643b0`, lines 59–62:

```
[snapshot]
max-new-file-size = "1MiB"
auto-track = "all()"
auto-update-stale = false
```

This is same-tag implementation source, not the page; it confirms `max-new-file-size = "1MiB"` and supplies the literal `auto-track = "all()"` that the page only describes behaviourally. Do not attribute `all()` to the docs page.

## 3. (2) Drafted SOURCES row

Registry shape confirmed from `corpus/SOURCES.md` header and rows S001/S050: 11 columns,
`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`.
Current registry count 50 — `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` →
`50`; next unused id is **S051**, L1 numbers it.

Primary row (snapshot question):

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S0?? | Configuration — Jujutsu docs — https://docs.jj-vcs.dev/latest/config/ | docs | A | jj v0.46.0 snapshot auto-tracking and new-file size semantics, not ref layout, durability or receipt safety | § Snapshot settings › Paths to automatically track and › Maximum size for new files; latest alias = v0.46.0 per versions.json; served 2026-10-20 with no last-updated line | non-ignored new files auto-track by default; ignored paths never auto-track; new files over 1MiB are refused until max-new-file-size is raised, and zero disables the cap | queued | 2026-10-20 | on-release | — |

Status rationale: `queued`, not `mined` — no declared r17 change (C1–C3, D3–D7) is grounded by snapshot semantics. If L1 instead uses this page for C3(c)'s colocation entry, the colocation fact needs its own scope (below); do not stretch this row's scope to cover refs claims.

Conditional second row, only if L1 admits the colocation fact as a separate entry (different scope from the row above; S049/S036 already show one URL can carry two scopes):

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S0?? | Configuration — Jujutsu docs — https://docs.jj-vcs.dev/latest/config/ | docs | A | jj v0.46.0 default colocation for new Git-backed repositories, not ref durability | § Git settings › Default colocation; latest alias = v0.46.0; served 2026-10-20 | jj git init and jj git clone create colocated workspaces by default, git.colocate = false opts out, and the page warns colocation can perform worse in large repos | queued | 2026-10-20 | on-release | — |

Verbatim grounding for that second row — two sentences, 22 and 15 words, so either fits the Gate's ≤25 cap:
“When creating a Git-backed Jujutsu repository, they use "colocated" mode by default, which places the `.git` directory next to the `.jj` directory.”
“Colocation allows some amount of two-way interoperability, but it can perform worse in large repos.”

Why it matters to C3: the context frames colocation as the operator's 2026-10-20 lane fact; this page shows colocation is jj's own default for git-backed repos, with an opt-out. That supports C3's framing but also warns it is the common case, not an exotic edge.

## 4. (3) Contradictions with the context's claim text

**None found on this page.** No statement on `https://docs.jj-vcs.dev/latest/config/` (v0.46.0) contradicts C1, C2, or C3.

Sweep performed on the full served text (2486 extracted lines) and the raw HTML:

- `grep -n -iE "refs/|jj/keep|export|concurrent|simultaneous|lock|not safe"` over the page text → no `refs/heads`, `refs/tags`, `refs/remotes`, `refs/jj`, `refs/stash`, `jj/keep`, HEAD-durability, or concurrency statement. The page is **silent** on the storage/durability of jj or git refs, so it can neither support nor contradict C3(a)/(b).
- `grep -n -iE "colocat|refs/jj|jj/keep|git backend|\bgit\b"` → colocation appears only under § Git settings › Default colocation; `git` elsewhere means diff formatting, config, signing, hash format, fetch remotes. No statement about the git backend's ref layout.
- `grep -n -iE "ignored|\.gitignore|\.git/|untracked|jj file track"` → snapshot/ignore statements only; no statement about nested `.git` directories, empty `.git` stubs, or phantom deletions, so C3(e) is neither corroborated nor contradicted here.
- `grep -c -i "last updated"` → `0`; no revision claim to contradict.

Closest statements, with why they are not contradictions:

1. `#default-colocation`: “When creating a Git-backed Jujutsu repository, they use "colocated" mode by default …” — **qualifies, does not contradict.** C3 says lanes use jj, colocated; the page says that is jj's default and `git.colocate = false` opts out. The context's “operator 2026-10-20: lanes use jj, colocated” remains true; it is just not a non-default configuration.
2. § Config files and TOML, repo settings: “For security reasons, they are not located inside the repo.” — **not about git config.** This governs jj's own repo-level settings, not `$GIT_DIR/config`, `config.worktree` or `info/attributes` that C1/D2 handle. Reading it as a contradiction with C1 would be a category error.
3. § Revsets, `immutable_heads()` default (`trunk() | tags() | untracked_remote_bookmarks() | untracked_remote_tags()`) — **not receipt durability.** Immutability of revisions is unrelated to whether a commit is held by `refs/jj/keep`; do not cite it as corroboration for C3(a).
4. `snapshot.auto-track` default (`all()` in the built-in config) — **not about `.git` tracking.** An empty directory is not snapshot content; the page says nothing that would explain or refute the C3(e) phantom-deletion observation.

## 5. Search log (PRISMA-inspired, for the SOURCES.md Gate)

Question: exact `snapshot.auto-track` / `snapshot.max-new-file-size` semantics and defaults in jj, and any contradiction with the r17 claim text.
Where searched: the assigned `jj-vcs.github.io` URL (redirected to `docs.jj-vcs.dev`), `versions.json`, the v0.46.0 tagged `docs/config.md`, and the built-in `cli/src/config/misc.toml` at the same tag; GitHub releases API for the tag date. No recursive repo search; no lane files beyond the named contract/registry files.
Identified 1 page (+1 built-in config file consulted only for the literal default, not a second row), screened 1, included 1 row (snapshot scope) + 1 conditional row draft (colocation scope), excluded 0.
Stop rationale: both keys, their behavioural defaults, the literal `1MiB` default, the `all()` built-in value and the zero-disable / existing-file exemptions are located at a named release; further jj pages (working-copy, filesets) were not opened because the assigned page resolves the question and opening them would widen scope beyond the ticket.

## 6. Commands run (exact, with relevant output)

```
curl -fsSI https://jj-vcs.github.io/jj/latest/config/ | grep -iE '^(HTTP|location|content-type)'
→ HTTP/2 301 ; location: http://docs.jj-vcs.dev/latest/config/

curl -fsSI http://docs.jj-vcs.dev/latest/config/ | grep -iE '^(HTTP|location)'
→ HTTP/1.1 301 Moved Permanently ; Location: https://docs.jj-vcs.dev/latest/config/

curl -fsS https://docs.jj-vcs.dev/versions.json
→ [{"version":"prerelease",...},{"version":"v0.46.0","title":"v0.46.0","aliases":["latest"]},...]

curl -fsSI https://docs.jj-vcs.dev/latest/config/ | grep -iE '^(HTTP|content-type|etag|last-modified|date)'
→ HTTP/2 200 ; content-type: text/html; charset=UTF-8 ; date: Tue, 20 Oct 2026 16:33:51 GMT ; etag: "7719b2ca…"

curl -fsS https://docs.jj-vcs.dev/latest/config/ | sha256sum
→ 4b8047e3309f42d9af06fc8dbd7328e7b37fa61c6e965a9723692a6de7a3bc5b

grep -c -i "last updated" jj-config.html
→ 0

for p in "All new files in the working copy that don't match the ignore patterns are" \
         "never tracked automatically" "the default is 1MiB" \
         "Setting this value to zero will disable the limit entirely" \
         "Files that already exist in the working copy are not subject to this limit"; do grep -c -F "$p" jj-config.html; done
→ 1 1 1 1 1

grep -oE 'id="(paths-to-automatically-track|maximum-size-for-new-files|snapshot-settings|default-colocation)"' jj-config.html
→ id="default-colocation" / id="maximum-size-for-new-files" / id="paths-to-automatically-track" / id="snapshot-settings"

curl -fsS https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/docs/config.md | sha256sum
→ edc5c53c0c90591f92e066106cc4b4cf7423d6bd28a4f4b4e2496cc9c258bc03

sed -n '2195,2235p' config.md (v0.46.0)
→ both snapshot sections as quoted above

curl -fsS https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/cli/src/config/misc.toml | grep -n -A4 -B2 -E 'auto-track|max-new-file-size|\[snapshot\]'
→ 59:[snapshot] / 60:max-new-file-size = "1MiB" / 61:auto-track = "all()" / 62:auto-update-stale = false

grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
→ 50   (next unused id S051)
```

No files under `corpus/` or `census/` were touched; only this report was written. No tool installed or upgraded (nothing needed).

## 7. Residual unknowns

- Literal default expression for `snapshot.auto-track` is not on the docs page; `all()` is read from the v0.46.0 built-in config. If L1 wants the page alone to carry both rows, the row's `teaches` must not claim `all()`.
- Whether the `latest` alias advanced since the 2026-10-20 16:33:51 GMT fetch cannot be known from this snapshot; `recheck: on-release` is the right cadence because mike repoints `latest` at each release.
- The page does not say whether `snapshot.auto-track` applies to paths added by a checkout/rewrite as well as working-copy additions; the wording is “when they're added to the working copy,” and no stronger claim should be made.
- Effect of these settings on the C3(e) fixture was not tested (probe rule forbids running jj); the report only notes that the page does not address nested `.git` stubs.
