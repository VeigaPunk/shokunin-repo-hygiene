STATUS: DONE — S053 re-opened independently at v0.46.0 (2026-10-20): primary quote verbatim, 17 words, at its named anchor; tier/scope/teaches hold with two precision edits; status/used-by FAIL against the round's own C3 knowledge draft.

# ReopenS053 — jj Configuration: `snapshot.auto-track`, `snapshot.max-new-file-size`

Seat: scout, WAVE 2 FALSIFY. Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Assigned: independently re-open `https://jj-vcs.github.io/jj/latest/config/` on 2026-10-20 and
falsify `.ufo/waves/round-17/w1/SrcJjConfigSnapshot.md` (primary quote, version/last-updated
record, and the drafted tier/status/scope/teaches cells). Read-only; only this report was
written.

## 0. Verdict summary

| check | verdict |
|---|---|
| primary quote VERBATIM (character-exact except inline markup) | HOLDS — Q1, 17 words |
| at the anchor it names | HOLDS — `#paths-to-automatically-track` |
| ≤25 words | HOLDS — Q1 17, Q2 19, Q3 21 (Q3 is a fragment of a 27-word sentence) |
| version recorded | HOLDS — `latest` = v0.46.0; stronger than drafted: `/v0.46.0/config/` is byte-identical |
| “last updated” line recorded | HOLDS — none served |
| tier cell | AGREE (official project docs; the contract text itself was not opened) |
| scope cell | NO OVERCLAIM, but under-scoped for the round's own consumer |
| teaches cell | AGREE on every clause; two precision edits |
| status cell | FAILS — “no declared r17 change is grounded” is false |
| used-by cell | FAILS — must name `corpus/knowledge/jj-colocation-receipts.md` |

The wave-1 conclusion “no page statement contradicts C1, C2 or C3” **holds** under an
independent sweep (§6).

## 1. Independent opening record (2026-10-20, this seat)

| field | value observed now |
|---|---|
| requested URL | `https://jj-vcs.github.io/jj/latest/config/` |
| redirect chain | `301` → `http://docs.jj-vcs.dev/latest/config/` → `301` → `https://docs.jj-vcs.dev/latest/config/` (re-run today: 301, 301, 200) |
| canonical | `https://docs.jj-vcs.dev/latest/config/` (`<link rel="canonical">`) |
| response | HTTP/2 200; `content-type: text/html; charset=UTF-8`; `date: Tue, 20 Oct 2026 17:32:14 GMT`; `etag: "7719b2caa8fb7b4086ae85b6a5cc62a6-ssl"` |
| served HTML sha256 | `4b8047e3309f42d9af06fc8dbd7328e7b37fa61c6e965a9723692a6de7a3bc5b` (269,927 bytes / 269,916 chars) — identical to the wave-1 fetch at 16:33:51 GMT |
| **version, as served** | **no version is printed on the page**: `grep -o 'v0\.46\.0'` → 0 hits. The inline Material config carries `"version": {"alias": true, "provider": "mike"}` (selector is client-side, no `<option>` markup is server-rendered). Alias resolved from `https://docs.jj-vcs.dev/versions.json`: `{"version":"v0.46.0","aliases":["latest"]}` |
| version, cross-checked | `https://docs.jj-vcs.dev/v0.46.0/config/` sha256 `4b8047e3309f42d9af06fc8dbd7328e7b37fa61c6e965a9723692a6de7a3bc5b` — **byte-identical to `/latest/`**, so today's `latest` really is v0.46.0 |
| release date | `v0.46.0` published `2026-10-07T21:28:17Z` (GitHub releases API `tags/v0.46.0`) |
| **“last updated” line** | **none served.** `grep -c -iE 'last[ -]?updated|last modified'` → `0`; `<footer>` text is only “Made with Material for MkDocs”; no revision meta tag |
| anchors present | `id="snapshot-settings"`, `id="paths-to-automatically-track"`, `id="maximum-size-for-new-files"`, `id="default-colocation"` |
| tagged doc source | `https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/docs/config.md` sha256 `edc5c53c0c90591f92e066106cc4b4cf7423d6bd28a4f4b4e2496cc9c258bc03`; Snapshot settings at line 2193, Working copy settings at 2251 |
| built-in defaults (implementation, not the page) | `cli/src/config/misc.toml` at v0.46.0 sha256 `5380373a7943a9b0d04c2b47c01e06d56045150252a9f62858e247d2108643b0`, lines 59–62: `[snapshot]` / `max-new-file-size = "1MiB"` / `auto-track = "all()"` / `auto-update-stale = false` |

Correction to the wave-1 record: `.ufo/waves/round-17/w1/SrcJjConfigSnapshot.md:21` says the
tagged `docs/config.md` “lines 2193–2235 carry the two sections byte-for-byte as served”.
The two sections end at line 2231; line 2233 begins `### Automatic update of stale working
copies`. Smallest fix: cite **2193–2231**. The quote text at 2197–2198 and 2213–2214 does
match the served HTML exactly.

## 2. Quote verification (served text, not the tag)

Normalization used: strip tags, HTML-unescape, collapse whitespace (the page wraps lines
inside sentences; rendered text is one space). Each quoted string then appears exactly once
in the section.

**Q1 — the primary quote, `snapshot.auto-track` default. 17 words. Anchor
`#paths-to-automatically-track`. VERBATIM.**

> “All new files in the working copy that don't match the ignore patterns are tracked by default.”

Served raw HTML (no inline markup inside this sentence):
`<p>All new files in the working copy that don't match the ignore patterns are\ntracked by default.`
The sentence sits in the paragraph immediately under `<h3 id="paths-to-automatically-track">`.
Exact-character check: ASCII apostrophe in `don't`; no U+2019, no entity, no link.

**Q2 — `snapshot.auto-track` semantics. 19 words. Same anchor. VERBATIM (one `<code>` span).**

> “You can set the `snapshot.auto-track` to set which paths get automatically tracked when they're added to the working copy.”

Served: `You can set the <code>snapshot.auto-track</code> to set which paths\nget automatically tracked when they're added to the working copy.`
(The ungrammatical double “set” is upstream’s wording, not a transcription error.)

**Q3 — `snapshot.max-new-file-size`. 21 words. Anchor `#maximum-size-for-new-files`.
VERBATIM SUBSTRING, but it is a mid-sentence fragment.**

> “`jj` will refuse to add new files to the snapshot that are larger than a certain size; the default is 1MiB.”

Served full sentence, 27 words:
`By default, as an anti-footgun measure, <code>jj</code> will refuse to add new files to the\nsnapshot that are larger than a certain size; the default is 1MiB.`
The draft omits the lead-in `By default, as an anti-footgun measure, ` without an ellipsis.
The fragment itself is character-exact (modulo the `jj` code span). Because the full sentence
is 27 words, the cut is required by the ≤25-word Gate; the smallest fix is to present it as
`… jj will refuse …` or label it “sentence fragment”.

Also verified verbatim on the same anchors (the wave-1 “additional semantics”):

| quote | words | exact on page |
|---|---|---|
| “Files with paths matching ignore files are never tracked automatically.” | 10 | yes |
| “Files that already exist in the working copy are not subject to this limit.” | 14 | yes |
| “Setting this value to zero will disable the limit entirely.” | 10 | yes |
| “When creating a Git-backed Jujutsu repository, they use "colocated" mode by default, which places the `.git` directory next to the `.jj` directory.” | 22 | yes (`.git`/`.jj` are `<code>`) |
| “Colocation allows some amount of two-way interoperability, but it can perform worse in large repos.” | 15 | yes |

## 3. Per-cell verdicts — primary row (w1:81)

| cell | drafted | verdict | corrected cell text |
|---|---|---|---|
| source | `Configuration — Jujutsu docs — https://docs.jj-vcs.dev/latest/config/` | **agree** | unchanged |
| kind | `docs` | **agree** | unchanged |
| tier | `A` | **agree** | unchanged. Official project documentation; consistent with every docs row S001–S050. Caveat: `SOURCES-CONTRACT-v1` is external (`corpus/SOURCES.md:3` names kaika’s contract) and was not opened, so this is a convention match, not a contract-text check. |
| scope | `jj v0.46.0 snapshot auto-tracking and new-file size semantics, not ref layout, durability or receipt safety` | **disagree — under-scope (no overclaim)** | `jj v0.46.0 snapshot.auto-track and snapshot.max-new-file-size semantics, plus the config-layer facts the C3 entry uses (repo settings are edited with jj config edit --repo; later-loaded settings override earlier ones); not ref layout, durability, receipt safety, ignore-file syntax or git.colocate` |
| anchor | `§ Snapshot settings › Paths to automatically track and › Maximum size for new files; latest alias = v0.46.0 per versions.json; served 2026-10-20 with no last-updated line` | **agree, precision** | `§ Snapshot settings › Paths to automatically track and › Maximum size for new files; § Config files and TOML (repo settings, load order); latest alias = v0.46.0 per versions.json and byte-identical at /v0.46.0/config/ (sha256 4b8047e3…); served 2026-10-20 with no last-updated line` |
| teaches | `non-ignored new files auto-track by default; ignored paths never auto-track; new files over 1MiB are refused until max-new-file-size is raised, and zero disables the cap` | **agree, precision** | `non-ignored new files auto-track by default; ignore-file paths never auto-track; snapshot.auto-track takes a fileset pattern (page points to the fileset docs for syntax); new files larger than 1MiB are refused until snapshot.max-new-file-size is changed to a different value, zero disables the limit, existing files are exempt; later-loaded repo settings can replace the built-in default` |
| status | `queued` | **disagree** | `queued (pending) → mined when corpus/knowledge/jj-colocation-receipts.md lands; the drafted rationale “no declared r17 change (C1–C3, D3–D7) is grounded by snapshot semantics” is false (§5)` |
| opened | `2026-10-20` | **agree** | unchanged |
| recheck | `on-release` | **agree** | unchanged. `latest` is a mike alias that repoints each release, and the page carries no revision stamp to diff; `on-release` is the only honest cadence. |
| used-by | `—` | **disagree** | `corpus/knowledge/jj-colocation-receipts.md §6 (uncommitted at ddb7347; pending gate)` |

Why the scope/anchor are under-scoped: the round’s C3 knowledge draft cites **the same URL
twice** — line 50 for Q1, and line 54 for “repo settings are editable with `jj config edit
--repo`”. The page supports both (§ Config files and TOML: “The repo settings. These can be
edited with `jj config edit --repo`…”), and the load-order sentence (“the settings from
earlier items in the list are overridden by the settings from later items if they disagree”)
is what makes the entry’s “set `snapshot.auto-track = "none()"`” rule effective over the
built-in `all()`. The drafted row’s scope excludes that fact, so it cannot ground line 54.

Why “raised” → “changed”: the page says the value “can be changed … to a different value”,
not only raised; zero is the disable case (already covered). “Refused until … changed” is
exact.

Why the fileset fact matters: the entry’s rule uses `none()`, a fileset expression. The page
says “See the fileset documentation for the syntax”, so the page supports “takes a fileset
pattern”, **not** the value `none()` itself. Do not attribute `none()` to this page; the
draft correctly keeps `all()` out of the page cells (w1:169).

## 4. Per-cell verdicts — conditional colocation row (w1:89)

| cell | verdict | corrected cell text |
|---|---|---|
| source | agree | unchanged |
| kind | agree | unchanged |
| tier | agree | unchanged (same caveat as above) |
| scope | **agree** — no overclaim; `not ref durability` matches the page’s silence | unchanged; optionally add `, not interleaved-command safety` (that warning lives on `git-compatibility`, not this page) |
| anchor | **agree, precision** | `§ Git settings › Default colocation; latest alias = v0.46.0 per versions.json and byte-identical at /v0.46.0/config/; served 2026-10-20` |
| teaches | **agree, precision** | `repositories created by jj git init and jj git clone are colocated by default (.git next to .jj); set git.colocate to false to disable it; the page warns colocation allows some two-way interoperability but can perform worse in large repos` |
| status | **agree** — `queued` | unchanged |
| opened | **agree** | unchanged |
| recheck | **agree** | unchanged |
| used-by | **agree** — `—` | unchanged. The knowledge entry’s body never cites this section; only its “source rows” note (line 114) lists `git.colocate`. Keep this as a separate row (S049/S036 precedent) rather than merging scopes. |

Precision notes on the colocation row: the page’s first sentence uses “they use
"colocated" mode by default” and only the next paragraph names `jj git init` / `jj git
clone`; the drafted attribution is still page-supported. `git.colocate = false` in the
drafted cell renders prose (“Set `git.colocate` to false to disable it.”) as a TOML
assignment; the page shows no such code block, so the corrected wording keeps it prose.

## 5. status / used-by falsification (the substantive disagreement)

The wave-1 rationale (w1:83) is:

> `queued`, not `mined` — no declared r17 change (C1–C3, D3–D7) is grounded by snapshot semantics.

Ground truth against that sentence:

1. `corpus/knowledge/jj-colocation-receipts.md:50` (uncommitted C3 deliverable, named in the
   round context):
   `- **Default tracks new files.** "All new files in the working copy that don't match the ignore patterns are tracked by default." — https://docs.jj-vcs.dev/latest/config/ — `sourced``
   — that is exactly Q1, cited as sourced.
2. Same file `:54`: `Rule: set snapshot.auto-track = "none()" on every colocated lane (repo
   settings are editable with jj config edit --repo, https://docs.jj-vcs.dev/latest/config/).`
   — a second citation of the same URL.
3. Same file `:114`: `S0?? — jj Configuration — https://docs.jj-vcs.dev/latest/config/
   (opened 2026-10-20; scope: snapshot.auto-track default, repo settings, git.colocate)` —
   the entry expects a config row whose scope **includes repo settings**, which the drafted
   row excludes.
4. File ordering: `stat` shows the knowledge draft mtime `2026-10-20 13:35:33 -0300` and the
   wave-1 report mtime `2026-10-20 13:36:20 -0300` — the consumer existed 47 s before the
   rationale was written.
5. The entry is **not in the landed commit**: `git cat-file -e
   ddb7347:corpus/knowledge/jj-colocation-receipts.md` → `fatal: path … exists on disk, but
   not in 'ddb7347'`, rc 128; `git ls-files --error-unmatch …` → `error: pathspec … did not
   match any file(s) known to git`, rc 1. So the `mined` flip is L1’s integration decision;
   the false part is the absolute “no declared r17 change is grounded”.

Smallest fix: keep `queued` only if the row says “pending: cited by the uncommitted C3 entry”,
and set `used-by` to that path with a pending marker; otherwise mark `mined` and name the
entry when it lands. Do not leave `used-by` at `—` with the current rationale.

## 6. Contradiction sweep (independent)

Full served HTML (269,927 bytes), tags stripped, whitespace normalized:

| pattern | hits | reading |
|---|---|---|
| `refs/jj` | 0 | silent on jj’s ref namespace |
| `jj/keep` | 0 | silent on retention refs |
| `refs/stash`, `refs/heads`, `refs/tags` | 0 / 0 / 0 | silent on git ref layout |
| `durab` | 0 | no durability statement |
| `not safe` | 0 | none |
| `nested .git`, `.git/` | 0 / 0 | silent on nested `.git` / empty-dir handling (C3(e) gets no doc support) |
| `concurren` | 2 | nav item “Concurrency”; the `--template` sentence “format many versions of the same file concurrently” — neither is ref durability |
| `colocat` | 9 | TOC + § Git settings › Default colocation only |
| `untracked` | 3 | `untracked_remote_bookmarks()` / `untracked_remote_tags()` revsets and “untracked files can be tracked with jj file track” — none mentions git `status.showUntrackedFiles` |

The three closest statements, and why none contradicts the r17 claim text:

1. **Default colocation** (“When creating a Git-backed Jujutsu repository, they use
   "colocated" mode by default…”): **qualifies** C3’s framing — colocation is jj’s own
   default for Git-backed repos and `git.colocate` opts out — it does not contradict it.
2. **“For security reasons, they are not located inside the repo.”** — this governs jj’s own
   *repo settings*, not `$GIT_DIR/config`, `config.worktree` or `info/attributes` (C1/D2).
   Reading it as a C1 contradiction is a category error. The same section is **usable** for
   the C3 entry: repo settings are editable with `jj config edit --repo` (see §3).
3. **`immutable_heads()` default** (`trunk() | tags() | untracked_remote_bookmarks() |
   untracked_remote_tags()`): revision immutability, not commit retention by `refs/jj/keep`;
   do not cite it as corroboration for C3(a).

Conclusion: the wave-1 “none found” verdict **holds**; the page is silent on refs,
durability and nested `.git`, so it can neither support nor refute C3(a)/(b)/(e).

## 7. Commands run (exact; no tool installed or upgraded)

```
curl -fsS https://docs.jj-vcs.dev/latest/config/ | sha256sum
→ 4b8047e3309f42d9af06fc8dbd7328e7b37fa61c6e965a9723692a6de7a3bc5b  -
curl -fsSI https://docs.jj-vcs.dev/latest/config/ | grep -iE '^(HTTP|date|etag|last-modified|content-type)'
→ HTTP/2 200; content-type: text/html; charset=UTF-8; date: Tue, 20 Oct 2026 17:32:14 GMT; etag: "7719b2caa8fb7b4086ae85b6a5cc62a6-ssl"
curl -fsS https://docs.jj-vcs.dev/versions.json | python3 -c '…aliases contains latest…'
→ [{'version': 'v0.46.0', 'title': 'v0.46.0', 'aliases': ['latest']}]
curl -sS -o /dev/null -w '%{http_code} %{redirect_url}\n' https://jj-vcs.github.io/jj/latest/config/
→ 301 http://docs.jj-vcs.dev/latest/config/
curl -sS -o /dev/null -w '%{http_code} %{redirect_url}\n' http://docs.jj-vcs.dev/latest/config/
→ 301 https://docs.jj-vcs.dev/latest/config/
curl -sS -o /dev/null -w '%{http_code} %{redirect_url}\n' https://docs.jj-vcs.dev/latest/config/
→ 200
curl -fsS https://docs.jj-vcs.dev/v0.46.0/config/ | sha256sum
→ 4b8047e3309f42d9af06fc8dbd7328e7b37fa61c6e965a9723692a6de7a3bc5b  -   (byte-identical to /latest/)
grep -c -iE 'last[ -]?updated|last modified' config.html
→ 0
grep -o 'v0\.46\.0' config.html | sort | uniq -c
→ (no output)   # page prints no version string
grep -oE 'id="[^"]*(snapshot|automatically|maximum-size|colocation)[^"]*"' config.html
→ id="snapshot-settings" id="paths-to-automatically-track" id="maximum-size-for-new-files" id="default-colocation"
python3 heredoc (tags stripped, whitespace collapsed): count of each drafted sentence in its section
→ Q1 1 (17 words), Q2 1 (19 words), Q3 1 (21 words), full Q3 sentence 1 (27 words)
python3 heredoc: count of 'last updated|last modified' in the HTML → 0; footer = "Made with Material for MkDocs"
python3 heredoc, pattern order and results: refs/jj 0, jj/keep 0, refs/stash 0, refs/heads 0, refs/tags 0,
durab 0, concurren 2, \block\b 0, "not safe" 0, "nested \.git" 0, "\.git/" 0, untracked 3, colocat 9 (contexts in §6)
curl -fsS https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/docs/config.md | sha256sum
→ edc5c53c0c90591f92e066106cc4b4cf7423d6bd28a4f4b4e2496cc9c258bc03
grep -n '^## Snapshot settings\|^## Working copy settings\|^### Automatic update' config-v046.md
→ 2193, 2251, 2233
curl -fsS https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/cli/src/config/misc.toml | sha256sum
→ 5380373a7943a9b0d04c2b47c01e06d56045150252a9f62858e247d2108643b0
grep -n -A4 '^\[snapshot\]' misc.toml
→ 59:[snapshot] 60:max-new-file-size = "1MiB" 61:auto-track = "all()" 62:auto-update-stale = false
curl -fsS https://api.github.com/repos/jj-vcs/jj/releases/tags/v0.46.0
→ tag_name v0.46.0, published_at 2026-10-07T21:28:17Z
git show ddb7347:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
→ 50   (S051 is the next free id; context plans S053 for this source)
git cat-file -e ddb7347:corpus/knowledge/jj-colocation-receipts.md
→ fatal: path … exists on disk, but not in 'ddb7347'; rc 128
git ls-files --error-unmatch corpus/knowledge/jj-colocation-receipts.md
→ error: pathspec … did not match any file(s) known to git; rc 1
stat -c '%y %n' .ufo/waves/round-17/w1/SrcJjConfigSnapshot.md corpus/knowledge/jj-colocation-receipts.md
→ 2026-10-20 13:36:20 -0300 w1/SrcJjConfigSnapshot.md; 2026-10-20 13:35:33 -0300 corpus/knowledge/jj-colocation-receipts.md
```

Not run (probe rule): `tools/souji-census.sh`, `souji-verify.sh`, `souji-vault-verify.sh`,
`souji-quarantine.sh`, any `jj` command, any lane mutating command. Working files lived only
under `/var/tmp/souji-r17-ReopenS053-2/` and were deleted afterwards.

## 8. Verdict

- **Primary quote: HOLDS** — Q1 verbatim, 17 words, at `#paths-to-automatically-track`; Q2
  and Q3 verbatim (Q3 a marked fragment of a 27-word sentence).
- **Version/last-updated record: HOLDS** — no last-updated line; `latest` = v0.46.0, now
  proven by byte-identical `/v0.46.0/config/`, not only by `versions.json`.
- **Tier: AGREE; scope: under-scoped; teaches: AGREE with two precision edits.**
- **Status/used-by: FAIL** — the round’s own uncommitted C3 knowledge entry cites this page
  twice; the drafted rationale says the opposite.
- **Contradictions: none; wave-1 sweep confirmed.**

Smallest fix (one row, five cells): apply the corrected `scope`, `anchor`, `teaches`,
`status` and `used-by` texts in §3; do not merge the colocation row into it (§4).

## 9. Residual unknowns

- `SOURCES-CONTRACT-v1` tier/status definitions were not opened (named as external, kaika);
  tier A and the status vocabulary are matched by registry convention, not contract text.
- The knowledge entry is uncommitted and `candidate — pending round-17 gate`, so whether the
  row is `mined` or `queued` belongs to L1’s integration commit; what is already false is the
  absolute rationale, not the status token itself.
- The page does not state the literal `auto-track` default (`all()` is implementation source
  at v0.46.0), does not mention `none()`, and does not say whether auto-track applies to
  paths introduced by checkout/rewrite rather than working-copy addition. No stronger claim
  should be added to the row.
- The page says nothing about nested `.git` stubs or empty directories, so C3(e) remains
  observation-only; this page cannot be cited for it.
