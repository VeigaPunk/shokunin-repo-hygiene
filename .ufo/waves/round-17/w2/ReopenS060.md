STATUS: DONE — the S060 primary quote is verbatim (19 words) at the anchor the draft names on a freshly served 2.56.0 page; the row's source/kind/tier/anchor/scope hold, the teaches cell carries one unsourced conclusion and one imprecise prefix rule, and `status: mined` is conditional on co-landing the still-untracked knowledge entry.

# ReopenS060 — independent re-open of git-rev-list(1) `--all`

Re-opened independently (fresh fetch, today 2026-10-20) against the wave-1 seat report
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-17/w1/SrcGitRevAll.md`
(read in full). No wave-1 artifact was trusted; every page fact below was re-derived from the
served HTML and every repo fact from `git show` at `ddb7347` (L1 landing) or `5fa6017` (base).

## 1. What was served (record this exact line)

- URL `https://git-scm.com/docs/git-rev-list`, fetched 2026-10-20, **254766 bytes**,
  sha256 `05282a4426b03e36edc23deef8221a4ad37e30713cf80d4a4c2d09cdcf67ab8c`.
- Title: **`Git - git-rev-list Documentation`**.
- Version/"last updated" line, served in the "Latest version" selector header:
  **`git-rev-list last updated in 2.56.0`**.
  The selector's 2.56.0 entry is dated **2026-09-28** (page render:
  `2.56.0 … *2026-09-28* → /docs/git-rev-list/2.56.0`).
- Host corroboration: `git --version` → `git version 2.56.0`; `pacman -Q git` → `git 2.56.0-1`;
  installed `/usr/share/man/man1/git-rev-list.1.gz` `.TH "GIT\-REV\-LIST" "1" "2026\-09\-27" "Git 2\&.56\&.0"`.
- Draft's stamp claim ("last updated in 2.56.0") **holds**. Two small locational corrections:
  the string sits in the version *selector header*, not a footer; and the served page also gives
  the release date 2026-09-28 (the draft records only 2.56.0 and the man date 2026-09-27).
  Neither changes a cell.

## 2. Primary quote — verbatim, ≤25 words, at the named anchor

Draft quote:
> "Pretend as if all the refs in refs/, along with HEAD, are listed on the command line as <commit>."

Served HTML, `--all` definition block:

```html
<dt class="hdlist1" id="Documentation/git-rev-list.txt-spanclasssynopsiscode--allcodespan"><a id="Documentation/git-rev-list.txt---all" class="anchor" href="#Documentation/git-rev-list.txt---all"></a><span class='synopsis'><code>--all</code></span> </dt>
<dd>
<p>Pretend as if all the refs in <span class='synopsis'><code>refs/</code></span>, along with <span class='synopsis'><code>HEAD</code></span>, are
listed on the command line as <em><span class="hover-term" data-term="commit">&lt;commit&gt;</span></em>.</p>
</dd>
```

- **Verbatim: HOLDS.** Tag-stripped and whitespace-normalized, the draft's string is an exact
  substring of the served text (`primary exact substring: True`). Differences are only inline
  markup (`refs/`, `HEAD` code spans; `<commit>` em/hover-term) — exactly the allowed exception.
- **Word count: HOLDS.** 19 words by `len(q.split())`; ≤25.
- **Anchor: HOLDS.** `id="Documentation/git-rev-list.txt---all"` exists (second occurrence of
  the string is `--all-match`, a different option). HTML line 3574.
- **Section: HOLDS.** `--all` sits between the h3 `_commit_limiting` ("Commit Limiting",
  HTML line 3390) and h3 `_commit_ordering` ("Commit Ordering", line 4462). The draft's
  "§ OPTIONS › Commit Limiting › --all" is accurate.
- **Absence claims: HOLD.** `refs/jj` → 0 hits; `\bjj\b` → 0; `namespace` → 0. The page never
  mentions jj; the `refs/` rule is the whole bridge.
- One nuance in the draft's §1: `refs/stash` appears **twice as a string** in one `%gD`
  reflog-selector example (`refs/stash@{1}` and `refs/stash@{2 minutes ago}`), i.e. one example,
  not one literal occurrence. Cosmetic; does not affect the row.

Supporting table quotes were spot-checked against the served HTML: `--branches`, `--tags`,
`--remotes`, `--glob`, `--exclude`, `--single-worktree` and the `--not` first sentence match
verbatim. Two cosmetic deviations, neither the gate quote: the `--exclude-hidden` excerpt makes
an unmarked elision (the page has "(see git-config[1])" after `transfer.hideRefs`), and the
`--not` excerpt stops at the sentence boundary before the page's two `--stdin` sentences.

The draft's corroborating EXAMPLES sentence is also verbatim on the page
("Print the list of commits authored by you in the past year, on any branch, tag, or other ref.")
but is **19 words, not 20** as the draft's table says (`Print`=1 … `ref.`=19). The gate quote
itself is the 19-word primary and is correct.

## 3. Cell-by-cell verdicts (registry order, `CORPUS.md:86`)

Column order at `CORPUS.md:86`:
`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.
Drafted row is `.ufo/waves/round-17/w1/SrcGitRevAll.md:167`, 889 bytes, split gives **13 fields
→ 11 columns: HOLDS** (no stray `|`; edge empties present).

| cell | drafted | verdict | corrected text |
|---|---|---|---|
| `source` | `git-rev-list(1), ref-selection pseudo-options — https://git-scm.com/docs/git-rev-list` | **agree** | unchanged |
| `kind` | `docs` | **agree** | unchanged (official rendered manual) |
| `tier` | `A` | **agree** | unchanged. `CORPUS.md:93-95`: A = "primary or authoritative for that scope (spec, official docs, …)". Same-host precedent at `ddb7347:corpus/SOURCES.md`: S036 git(1) A, S044 git-status A, S049 git(1) A |
| `scope` | `which refs --all and the durable-ref options root, and how --glob/--exclude narrow them, on Git 2.56.0; not for-each-ref pattern semantics` | **agree, tighten** | `which refs --all, --branches, --tags, --remotes and --glob root, and how --exclude (and --exclude-hidden) prune them, on the served Git 2.56.0 manual; not for-each-ref pattern or exclude semantics` — "durable-ref options" is lane jargon the page never uses; name the options. "on Git 2.56.0" holds (served manual is 2.56.0). The negative bound holds: the page is rev-list and says nothing about for-each-ref |
| `anchor` | `web manual "git-rev-list last updated in 2.56.0", opened 2026-10-20; installed git 2.56.0-1 roff (Date: 2026-09-27) agrees verbatim; § OPTIONS › Commit Limiting: --all, --branches, --tags, --remotes, --glob, --exclude, --exclude-hidden, --single-worktree, --not; § EXAMPLES (--all)` | **agree** | add the served release date: `… "last updated in 2.56.0" (2.56.0 entry dated 2026-09-28), opened 2026-10-20; installed git 2.56.0-1 roff (Date: 2026-09-27)…`. Every listed section/option was located; the roff wording checked: roff lines 284-287 read `Pretend as if all the refs in refs/, along with HEAD, are listed on the command line as <commit>.` |
| `teaches` | `--all roots every ref under refs/ plus HEAD, so refs/jj/keep/* are roots; --branches, --tags, --remotes root exactly refs/heads, refs/tags, refs/remotes; --glob prepends refs/; --exclude prunes only refs/ names, only for the next pseudo-option, and cannot drop HEAD` | **partial** | see §4: two clauses claim more than the page states |
| `status` | `mined` | **conditional** | `mined` only if the knowledge entry lands in the same commit; otherwise `queued` with `used-by —` |
| `opened` | `2026-10-20` | **agree** | unchanged (I re-opened today) |
| `recheck` | `on-release` | **agree** | unchanged (docs precedent, S001-S036) |
| `used-by` | `corpus/knowledge/jj-colocation-receipts.md` | **conditional** | same condition as `status`; also the entry must cite **S051** (it currently says `S0?? — git-rev-list(1) …`) |

## 4. `teaches` — what the page states vs what the cell asserts

Verified page text (all § OPTIONS › Commit Limiting, served 2026-10-20):

- `--branches[=<pattern>]`: "Pretend as if all the refs in refs/heads are listed on the command
  line as <commit>. If <pattern> is given, limit branches to ones matching given shell glob.
  If <pattern> lacks ?, *, or [, /* at the end is implied." → the cell's "root exactly
  refs/heads" **holds**; same for tags/remotes (`--tags` says "If **pattern** lacks" without
  "the", as the draft notes — reproduced exactly).
- `--glob`: "… Leading refs/, is automatically prepended if missing. If pattern lacks ?, *, or
  [, /* at the end is implied." → "prepends refs/" **holds** (stray comma is the page's). The
  cell omits the implied `/*` — under-claim only.
- `--exclude`: "Do not include refs matching <glob-pattern> that the next --all, --branches,
  --tags, --remotes, or --glob would otherwise consider. Repetitions … accumulate … up to the
  next … option"; and "The patterns given should not begin with refs/heads, refs/tags, or
  refs/remotes when applied to --branches, --tags, or --remotes, respectively, and they must
  begin with refs/ when applied to --glob or --all. If a trailing /* is intended, it must be
  given explicitly."

Against that, the cell's last clause is **not all page text**:

1. "prunes only refs/ names" is **imprecise**: the prefix rule is option-relative. Patterns for
   `--glob`/`--all` must begin with `refs/`; patterns for `--branches`/`--tags`/`--remotes` must
   **not** begin with `refs/heads`/`refs/tags`/`refs/remotes` (they are namespace-relative).
2. "and cannot drop HEAD" is **not stated on the page** — it is a two-step inference (the
   `--all` sentence adds HEAD separately, and valid `--all` patterns must start with `refs/`),
   corroborated by the draft's own measurement (`--exclude=HEAD --all` → 58, from 58). The page
   never says `--exclude` cannot drop HEAD. Do not present it as sourced in the row.
3. "so refs/jj/keep/* are roots" is a one-step substitution the page does not make
   (`refs/jj` appears 0 times). It is sound, but the cell should carry it as inference, or
   phrase it as the substitution it is.

Corrected `teaches` (all sourced clauses are the page's words; the jj step is marked):

> `--all` lists all the refs in `refs/` along with `HEAD` as `<commit>`, so any ref under
> `refs/` — `refs/jj/keep/*` when present [inference; the page names no jj ref] — is a root;
> `--branches`, `--tags`, `--remotes` list exactly `refs/heads`, `refs/tags`, `refs/remotes`;
> `--glob` prepends `refs/` and implies a trailing `/*` when the pattern lacks `?*[`;
> `--exclude` prunes only the next `--all`/`--branches`/`--tags`/`--remotes`/`--glob`
> (accumulating), takes `refs/`-prefixed patterns for `--glob`/`--all` and
> `refs/heads`/`refs/tags`/`refs/remotes`-free patterns for the trio, and does not imply a
> trailing `/*`

(`--all --exclude=HEAD` → `58` and the positional `--exclude` behaviour belong in the lesson /
verification, not in the sourced cell; or keep them with an explicit `[measured]` tag.)

## 5. Landed-rev reality checks (what the row's cells now depend on)

- **`used-by` path absent at the landed rev**: `git -C <lane> cat-file -e
  ddb7347:corpus/knowledge/jj-colocation-receipts.md` →
  `fatal: path 'corpus/knowledge/jj-colocation-receipts.md' exists on disk, but not in 'ddb7347'`
  (rc 128). In the worktree it exists untracked: `-rw-r--r-- 16253 Oct 20 13:35`.
  The frozen-census check is `CORPUS.md:146-147`: for each `mined` row's `used-by` paths it runs
  `[ -e "$p" ]` from the repo root. So the row **passes in this worktree** and **fails in any
  checkout of ddb7347**. The draft's landing precondition text ("does not exist yet; `ls -l` →
  No such file or directory") is now stale — the file exists on disk, untracked. The correct
  gate is co-landing, not "append once C3(c) lands".
  Also `git show ddb7347:corpus/knowledge/jj-colocation-receipts.md` line 117 still reads
  `S0?? — git-rev-list(1) …`; replace with S051 for `mined` ("cited by ≥1 path", `CORPUS.md:103`)
  to be a citation of the row, not just the URL.
- **Numbering holds**: `ddb7347:corpus/SOURCES.md` has 50 rows, last S050; `^| S051 ` count 0 →
  next unused id is S051.
- **Draft's measurements are base-dated, not current.** At base 5fa6017 the draft reports
  all=58 / trio=52 / keep-only=6 / keep refs=8. Measured now in the lane worktree (read-only
  `rev-list`): `all=67`, `trio=54`, `heads=54`, `jjglob=67`, `head=54`, `all∖trio=13`,
  `keeprefs=17`. The qualitative claim survives and the decisive pair is unchanged:
  `0254661… --not --all` → `0`; `… --not --branches --tags --remotes` → `1`. If L1 quotes
  58/52, date them to 5fa6017 or use 67/54.
- **Fix-site line numbers moved at ddb7347.** The draft's base-rev citations are correct:
  `git show 5fa6017:tools/souji-verify.sh` line 351 is
  `uniq=$(git -C "$owner" log --oneline "$head" --not --all …)`, and lines 809-813 are the
  unfiltered `for-each-ref --format='%(objectname)'` roots array + `rev-list … --not "${roots[@]}"`.
  At ddb7347 the same `--not --all` query is at `tools/souji-verify.sh:390` and
  `tools/souji-vault-verify.sh:568`; the roots site is now
  `for-each-ref --exclude='refs/jj/'` at `tools/souji-verify.sh:854`,
  `tools/souji-vault-verify.sh:1061`, `tools/souji-quarantine.sh:1155`; the new jj guard is
  `rev-list --glob=refs/jj/keep/* --not --branches --tags --remotes` at verify:247, vault:439,
  quarantine:983. So fix #2 as drafted (replace the roots array with pseudo-options) was **not**
  taken — the landed code keeps `for-each-ref` and narrows with `--exclude`, whose pattern
  semantics this row explicitly excludes and nobody has opened (`git-for-each-ref(1)` remains
  unopened). That is consistent with the row's scope, but the landed fix rests on an unopened
  source; route it.

## 6. Commands run and what they returned

```
curl -fsS --max-time 60 -o /var/tmp/souji-r17-ReopenS060/rev-list.html https://git-scm.com/docs/git-rev-list
  → 254766 bytes; sha256 05282a44…67ab8c
grep -o 'git-rev-list last updated in [0-9.]*' rev-list.html
  → git-rev-list last updated in 2.56.0
python3 (strip tags; normalise whitespace; exact-substring test)
  → primary exact substring: True ; primary words: 19
  → example exact substring: True ; example words: 19            (draft says 20)
grep -n 'id="Documentation/git-rev-list.txt---all"' rev-list.html
  → 3574 (plus 3469 for --all-match, a different option)
h3 scan → 3390 _commit_limiting "Commit Limiting"; 4462 _commit_ordering "Commit Ordering"
regex over tag-stripped page → refs/jj: 0 ; \bjj\b: 0 ; namespace: 0
regex refs/stash → two hits, both in the one %gD reflog-selector example
title → Git - git-rev-list Documentation ; selector 2.56.0 → 2026-09-28
git --version → git version 2.56.0 ; pacman -Q git → git 2.56.0-1
zcat /usr/share/man/man1/git-rev-list.1.gz → .TH "GIT-REV-LIST" "1" "2026-09-27" "Git 2.56.0";
  roff 284-287 = the same --all sentence
git show 5fa6017:tools/souji-verify.sh | sed -n '345,356p;805,816p'
  → :351 log --not --all ; :809 for-each-ref --format='%(objectname)' ; :813 rev-list --not "${roots[@]}"
git show ddb7347:tools/souji-verify.sh | grep -- '--not --all' → :390
git show ddb7347:tools/souji-vault-verify.sh | grep -- '--not --all' → :568
grep for-each-ref --exclude at ddb7347 → verify:854, vault:1061, quarantine:1155
rev-list (lane worktree): all=67 trio=54 heads=54 jjglob=67 head=54 all∖trio=13 keeprefs=17
  0254661… --not --all → 0 ; --not --branches --tags --remotes → 1
git cat-file -e ddb7347:corpus/knowledge/jj-colocation-receipts.md → fatal … not in 'ddb7347' (rc 128)
ls -l corpus/knowledge/jj-colocation-receipts.md → 16253 bytes, Oct 20 13:35 (untracked)
git show ddb7347:corpus/SOURCES.md → rows=50 last=S050; ^| S051 → 0
CORPUS.md:93-95 tier A ; :99 anchor ; :103 status ; :107 used-by ; :114 ≤25-word quote ;
  :146-147 census awk, used-by existence via [ -e "$p" ]
```

No tool was installed or upgraded; no pacman transaction; no `jj`; no git write; the only files
written were under `/var/tmp/souji-r17-ReopenS060/` (removed after) and this report.

## 7. Verdict

- **Quote and its location: HOLDS** (verbatim modulo inline markup, 19 words, anchor
  `#Documentation/git-rev-list.txt---all` inside § OPTIONS › Commit Limiting).
- **Version line: HOLDS** ("git-rev-list last updated in 2.56.0"; add served date 2026-09-28).
- **Row as a whole: PARTIAL.** `source`, `kind`, `tier`, `anchor`, `opened`, `recheck`, NF=13
  agree. `scope` agrees after naming the options. `teaches` must stop presenting
  "cannot drop HEAD" and "prunes only refs/ names" as page statements, and should mark the
  `refs/jj` step as inference. `status: mined` + `used-by` are valid only if the untracked
  knowledge entry is committed in the same landing and updated from `S0??` to `S051`.

**Smallest fix (one line):** append S051 with the corrected `teaches` and `scope` text above;
either co-commit `corpus/knowledge/jj-colocation-receipts.md` (with S051 substituted for
`S0??`) or set `status: queued` / `used-by: —`. Keep the gate quote as-is; it is exact.
Do not cite the base-rev line numbers as current: use verify:390 / vault:568 today, and either
date the 58/52 counts to 5fa6017 or use 67/54.

## 8. Remaining unknowns

1. `git-for-each-ref(1)` pattern and `--exclude` semantics — still unopened, and the landed
   roots narrowing (`for-each-ref --exclude='refs/jj/'`) depends on them. Route to the row that
   covers for-each-ref, or land the pseudo-option form the draft recommends.
2. Whether L1 intends to quote the base-rev measurements (58/52/6/8) or re-measure at ddb7347
   (67/54/13/17). Both are internally consistent; mixing them would not be.
3. I did not read the sibling w2 files (`ReopenS051/052/057/061.md`) per the probe rule; if one
   of them fixes the same row, keep one and fold this quote in.
