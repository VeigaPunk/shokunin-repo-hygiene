STATUS: DONE — S051 independently re-opened (docs.jj-vcs.dev/latest/git-compatibility/, `latest` = v0.46.0, no last-updated line served); primary quote is verbatim, 25 words, at the anchor it names; tier agree, status agree only if the used-by entry is committed with the row, scope disagree on two phrases, teaches agree with one precision fix; wave-1's "0 `index` matches in the whole HTML" is false (1 match, an href).

# Re-open S051 — jj docs, Git compatibility

Wave-1 draft audited: `.ufo/waves/round-17/w1/SrcJjGitCompat.md`, sha256 `80b1bad0dc8b66757252852dff9e17ad80694692b4e830190c5709c94cbe92c4`, 13,274 bytes. That file is **not in the landed tree** (`git cat-file -e ddb7347:.ufo/waves/round-17/w1/SrcJjGitCompat.md` → `fatal: path ... exists on disk, but not in 'ddb7347'`), so the `:N` references below are to the working-tree file at that hash.

Registry state at the landed rev: `git show ddb7347:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → **50**; `grep -c S051 corpus/SOURCES.md` → **0**. The row exists only as the wave-1 draft; L1 assigns the number and lands it.

## 1. Access record (fresh fetch, 2026-10-20, this seat)

| fact | measured value |
|---|---|
| URL chain | `https://jj-vcs.github.io/jj/latest/git-compatibility/` → **301**, `location: http://docs.jj-vcs.dev/latest/git-compatibility/` → **301**, `Location: https://docs.jj-vcs.dev/latest/git-compatibility/` → **200** |
| body | 61,334 bytes; sha256 **`db9c9a760810386858e6b1bad4a7a334c56bd48c77692dbc1c343657ae0ca254`** — byte-identical to wave-1's copy; a second https fetch re-hashes to the same value |
| version served | `https://docs.jj-vcs.dev/versions.json` 200: `{"version":"v0.46.0","aliases":["latest"]}` is element 2, so **`latest` = v0.46.0**. The page HTML itself contains **0** occurrences of `v0.46.0`; `latest` occurs once, in `<link rel="canonical" href="https://docs.jj-vcs.dev/latest/git-compatibility/">` |
| last-updated line | **none served.** No `Last-Modified` header (`date: Tue, 20 Oct 2026 17:32:11 GMT`, `etag: "02aec1f4984867c2018ec2e52d542385-ssl"`, `server: Netlify`, `content-length: 61334`). 0 matches for `last[ -]updated|git_revision|revision-date` in the HTML; 0 visible `updated|modified|generated|built`; 0 date-like strings in the rendered article |
| only version string in content | exactly 1 visible `version` occurrence: `since version 0.30.0`, in § Format mapping details (change-id header paragraph) — as wave-1 recorded |

One correction to wave-1's access record: the redirect is **two** 301s (github.io → `http://` docs → `https://` docs), not one. Wave-1 line 7 collapses the intermediate `http://` Location. Cosmetic; final body identical.

## 2. Primary quote — HOLDS

Quote as it appears in the draft's blockquote (extracted mechanically from the file, not retyped):

> "jj commands will usually put the Git repo in a "detached HEAD" state, since in jj there is not concept of a "currently tracked branch"."

- **Character-exact**: present as an exact substring of the rendered `<article>` text (whole-article text index 6213, space on both boundaries). 135 chars, 25 words. Straight ASCII double quotes; the `there is not concept` (sic) slip is preserved. The only inline markup inside the span is `<code>jj</code>` twice — the contract's permitted inline-markup exception.
- **≤25 words**: exactly 25. Holds.
- **Anchor**: inside `<h2 id="colocated-jujutsugit-workspaces">` (§ Colocated Jujutsu/Git workspaces), in the paragraph beginning `It is allowed to mix jj and git commands in such a workspace in any order.` — the third paragraph of that section in document order, exactly as the draft says (`:16-18`). The next sentence in the same paragraph, `Before doing mutating Git commands, you may need to tell Git what the current branch should be with a git switch command.`, also holds verbatim (22 words).

## 3. Second quote (index half) — HOLDS

> "The staging area will be ignored. For example, jj diff will show a diff from the Git HEAD to the working copy."

Verbatim in the `Staging area: Kind of.` bullet of `#supported-features`, 22 words (exact substring at rendered-text index 2307). The bullet continues `There are ways of fulfilling your use cases without a staging area.` (link target `../git-comparison/#the-index`); the draft presents only the first two sentences, so it does not overstate the bullet.

## 4. Cell audit — verdicts against `SOURCES-CONTRACT-v1` (fleet path `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`)

| cell | verdict | reasoning | corrected cell text |
|---|---|---|---|
| **tier** | **AGREE** | `docs` + **A** matches the contract definition (`tier` "primary or authoritative for that scope (spec, official docs, source code ...)", contract:26-28). The page is the jj project's own documentation; `kind=docs`, no `community` inflation. | unchanged: `A` |
| **status** | **AGREE IN FORM, CONDITIONAL IN FACT** | `mined` means "cited by ≥1 path in `used-by`" (contract:36). The cited path `corpus/knowledge/jj-colocation-receipts.md` exists on disk (16,253 B, sha256 `2e4ea04…`) and cites this page at `:11-43`; but it is **untracked at HEAD and absent from ddb7347** (`git ls-files --error-unmatch` rc 1; `git cat-file -e HEAD:corpus/knowledge/jj-colocation-receipts.md` → `fatal: ... not in 'HEAD'`). The census E11 check is `[ -e "$dir/$path" ]` on disk (`scripts/sources-census.sh:566`), so a worktree census passes while the landed tree references a path that does not exist in the commit — the gap is **silent**. Wave-1's "not yet present" (`:52`) is now precise: present untracked, not committed. | keep `mined` **only if** the entry is committed in the same landing rev (and its `## Source rows to number` `:111` says `S0??` — replace with `S051`); otherwise `queued` with used-by `—`. |
| **scope** | **DISAGREE — two phrases claim more than the page states; the rest holds** | (a) `refs/jj/ keep refs`: the page says `Commits created by jj have a ref starting with refs/jj/ to prevent GC.` — `refs/jj/keep` occurs **0** times and `keep` appears only in `keep track of what is going on`. Since C3(b) uses `--glob=refs/jj/keep/*`, the cell as drafted reads as if the `keep` sub-namespace were documented; it is observed only (knowledge entry `:29`). (b) `the ignored git index`: the page says **staging area**; visible text has 0 `index`; `index` occurs once in HTML, as `href="../git-comparison/#the-index"`. The not-stated item is that the page never says jj resets/rewrites it — so the scope should not name the index as documented. `jj 0.46.0` and "colocated … workspaces" hold. | `jj 0.46.0 colocated Jujutsu/Git workspaces: usually-detached git HEAD with no currently tracked branch; refs beginning refs/jj/ that prevent GC (no refs/jj/keep sub-namespace stated); the ignored git staging area (no index reset/rewrite stated)` |
| **teaches** | **AGREE with one precision fix** | Clause check: `usually leaves git in detached HEAD (no currently tracked branch)` holds; `the git staging area is ignored` holds; `jj-created commits carry a refs/jj/ ref to prevent GC` holds (`a ref starting with refs/jj/ to prevent GC` — prefer "beginning"). The one overreach: `imports and exports git refs on every command` — the page's sentence is `Jujutsu will import and export from and to the Git repo on every jj command automatically.` "refs" is explicit only for git→jj (`"import git refs" operation`, ¶4) and for `branches or other refs` slowness, not as the verbatim object of both directions. One grounded learner benefit otherwise holds (contract:38-39, style of peer rows). | `Jujutsu imports and exports from and to the Git repo on every jj command and usually leaves git in a detached-HEAD state (jj has no currently tracked branch); the git staging area is ignored, and commits created by jj carry a ref beginning refs/jj/ to prevent GC` |

Ancillary cells, checked for completeness (not in the assignment's four, but they carry the row):

- **source** — AGREE. `docs.jj-vcs.dev/latest/git-compatibility/` is the canonical host (canonical link + final 200); the github.io URL is a two-hop alias. Draft's advice to cite docs.jj-vcs.dev is right.
- **anchor** — AGREE. Sections and revision are present per contract:32-34: § Colocated ¶1 (share/import-export) and ¶3 (the quote), § Supported features › Staging area, Detached HEAD, Garbage collection, § Branches, § Format mapping details ¶2 (refs/jj), § Converting (HEAD comment); revision `latest` = v0.46.0 attributed to versions.json, and "page serves no last-updated stamp" is true. It does not claim the page states a version.
- **opened / recheck** — AGREE. Opened 2026-10-20 (today; this seat re-opened it today). `on-release` is an allowed cadence (contract:38-39) and is the right one: the row is pinned to the `latest` alias, which moves on every jj release (v0.46.0 now).

## 5. Disagreements with wave-1's own measurements (the falsification part)

1. **Line 28 is false as written.** `The word index does not occur anywhere on the page (0 case-insensitive \bindex\b matches across the whole HTML)` — the HTML has **1** match: `href="../git-comparison/#the-index"` inside the Staging-area bullet. Rendered text has 0. Corrected sentence: *the word does not occur in rendered text; it occurs once as an href to git-comparison#the-index, and the page never describes jj resetting/rewriting/refreshing an index.* The substantive conclusion (no support for a "jj leaves the index stale"/"jj rewrites the index" claim) **still holds** — the page only says the staging area is ignored and cross-links to `git-comparison#the-index` for `ways of fulfilling your use cases without a staging area`.
2. **Line 56's honesty bound** repeats the same overstatement (`page never uses the word`). Correct to *never uses it in rendered text*.
3. **Line 7's redirect chain** omits the intermediate `http://` hop (two 301s, see §1).
4. **Line 52's landing condition** is directionally right but under-stated: "not yet present" is wrong at HEAD (the file exists on disk) and the real condition is *committed in the same rev*, because E11's disk check cannot see the difference.
5. Everything else in the access record and the five quoted sentences checked out verbatim, including `refs/jj/keep` = 0, `TODO: Describe how branches are mapped` exact, `branch@git` present, the `# Convince jj to update .git/HEAD to point to the working-copy commit's parent` / `jj new && jj undo` fenced comment, and the `import git refs` op-log sentence.

## 6. Page absences re-verified (they support the draft's `not stated` items)

- **Index reset/rewrite**: not stated anywhere; `index` only in the cross-link href (see §5.1).
- **Bookmark ↔ git-ref mapping**: `#branches` contains exactly `TODO: Describe how branches are mapped` and nothing else.
- **`refs/jj/keep`**: 0 occurrences; the page's only refs-namespace statement is `a ref starting with refs/jj/`.
- **HEAD's target**: stated only in the fenced shell comment in § Converting (`# Convince jj to update .git/HEAD to point to the working-copy commit's parent`, then `jj new && jj undo`) — not as a normative sentence, as the draft says.
- **Last-updated**: none (see §1).

## 7. Exact commands run (with the outputs that decide the findings)

```
$ curl -sSL -o page.html -w 'HTTP %{http_code} size %{size_download} final %{url_effective}\n' \
    https://jj-vcs.github.io/jj/latest/git-compatibility/
HTTP 200 size 61334 final https://docs.jj-vcs.dev/latest/git-compatibility/

$ curl -sSIL https://jj-vcs.github.io/jj/latest/git-compatibility/ | grep -iE '^HTTP|^location'
HTTP/2 301
location: http://docs.jj-vcs.dev/latest/git-compatibility/
HTTP/1.1 301 Moved Permanently
Location: https://docs.jj-vcs.dev/latest/git-compatibility/
HTTP/2 200

$ curl -sSI https://docs.jj-vcs.dev/latest/git-compatibility/ | grep -iE 'last-modified|^etag|^date|^server|content-length'
date: Tue, 20 Oct 2026 17:32:11 GMT
etag: "02aec1f4984867c2018ec2e52d542385-ssl"
server: Netlify
content-length: 61334          # no last-modified

$ curl -sS https://docs.jj-vcs.dev/versions.json -w '\nHTTP %{http_code}\n'
HTTP 200                       # element 2: {"version":"v0.46.0","aliases":["latest"]}

$ sha256sum page.html   # and: curl -sSL https://docs.jj-vcs.dev/... | sha256sum
db9c9a760810386858e6b1bad4a7a334c56bd48c77692dbc1c343657ae0ca254  page.html

$ python3  # tag-strip <article>, collapse whitespace, substring test
VISIBLE TEXT 'index' matches: 0
q in textn: True | words: 25 | chars: 135 | boundaries: ' ... ' | ASCII quotes only: True | sic 'is not concept': True
q2 in textn: True | words: 22
'branch@git present: True'; 'TODO: Describe how branches are mapped' present: True
refs/jj/keep: 0 matches in HTML; '\bkeep\b': 1 match ('keep track of what is going on')
last[ -]updated / git_revision / revision-date: 0 matches in HTML
visible 'version' occurrences: 1 ("since version 0.30.0")
$ grep -o 'href="[^"]*the-index[^"]*"' page.html
href="../git-comparison/#the-index"

$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ git rev-parse HEAD
d7e648d5a1931e6dbacfd5be0587547afee15de3
$ git cat-file -e ddb7347:corpus/knowledge/jj-colocation-receipts.md
fatal: path 'corpus/knowledge/jj-colocation-receipts.md' exists on disk, but not in 'ddb73474433977ff54b015ac3e77669ff2537353'
$ git ls-files --error-unmatch corpus/knowledge/jj-colocation-receipts.md
error: pathspec ... did not match any file(s) known to git      (rc=1)
$ git show ddb7347:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
50
$ grep -c 'S051' corpus/SOURCES.md
0
```

Contract/census lines used: `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:26-28` (tier A), `:32-34` (anchor revision), `:36-40` (status `mined`, recheck cadence, used-by), `:45` (a row is a claim); E11 implementation `scripts/sources-census.sh:538-575`, disk test at `:566`.

**Probe-rule self-disclosure (read this before using the seat).** One forbidden shape was run: `grep -rn 'SOURCES-CONTRACT' --include='*.md' corpus/ .ufo/waves/round-16/` — a recursive grep over two directory trees, which the probe rule disallows ("never recursive search over ... a whole directory tree"). It did not traverse the lane root or the fleet root, output contained nothing from `census/operator-sweep-20261019/`, and no line from that path was opened or quoted. The contract path it surfaced (`.ufo/waves/round-16/w1/SrcGitCheckAttr.md:129` → `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`) was then read as an exact named file, and every finding above was independently re-derived from the fresh page fetch and exact-file reads. L1 should treat the search-log accounting as disclosed and, if the round voids breached seats, re-derive the four cell verdicts — they do not depend on that grep.

Tooling: nothing installed or upgraded (no pacman/uv/npx/cargo); `/var/tmp/souji-r17-ReopenS051/` removed after the run (page.html + versions.json only).

## 8. Verdict and smallest fix

**Source row: landable. Quote and provenance hold; two cell texts and one landing condition need edits.**

- Quote: verbatim, 25 words, at `#colocated-jujutsugit-workspaces` ¶3 — as drafted. No change.
- Version record: `latest` = v0.46.0 per versions.json; page serves no last-updated line; content's only version string is `since version 0.30.0`. As drafted (fix the redirect hop count if the access record is quoted).
- `tier` A: agree, no change.
- `status` mined: agree **only** if `corpus/knowledge/jj-colocation-receipts.md` is committed in the same landing rev (currently untracked, absent from ddb7347; the disk-based E11 check will not catch it). Also replace `S0??` with `S051` in that entry's `## Source rows to number` (`:111`) when the id is assigned.
- `scope`: replace with `jj 0.46.0 colocated Jujutsu/Git workspaces: usually-detached git HEAD with no currently tracked branch; refs beginning refs/jj/ that prevent GC (no refs/jj/keep sub-namespace stated); the ignored git staging area (no index reset/rewrite stated)`.
- `teaches`: replace with `Jujutsu imports and exports from and to the Git repo on every jj command and usually leaves git in a detached-HEAD state (jj has no currently tracked branch); the git staging area is ignored, and commits created by jj carry a ref beginning refs/jj/ to prevent GC`.
- Correct the false `index` measurement (`SrcJjGitCompat.md:28`, `:56`) before any lesson quotes it: 0 in rendered text, 1 href `../git-comparison/#the-index` in the HTML.
