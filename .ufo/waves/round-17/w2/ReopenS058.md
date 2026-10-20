STATUS: DONE — primary quote is verbatim (13 words) in git-worktree § DETAILS, but its cited line 595 is 589 in my fetch; kind/tier/source/opened/recheck agree, while id, scope, anchor, teaches and status need correction (S058 not S051; git-config `extensions.worktreeConfig`, § FILES and `--worktree` are the missing stronger anchors, and § FILES falsifies the draft's off-case inference).

# ReopenS058 — independent re-open of git-worktree(1) CONFIGURATION FILE + git-config(1) Includes

Seat: W2 falsify, source S058. Access date **2026-10-20**. Lane root
`/home/vgpnk/Projects/shokunin/souji-shokunin`. Reading seat: no file was written except this
report, no tool was installed or upgraded, no `git`/`jj` write and no `/var/tmp` directory was
created.

## 0. Served revisions (recorded as asked)

- `https://git-scm.com/docs/git-worktree` — version line **"git-worktree last updated in 2.56.0"**
  (my fetch line 156); version entry 1 is 2.56.0 dated 2026-09-28, entry 2 is
  **"2.55.0 no changes"**.
- `https://git-scm.com/docs/git-config` — version line **"git-config last updated in 2.56.0"**
  (line 155); 2.55.0 is a dated entry (2026-06-29), not "no changes".
- `https://git-scm.com/docs/git-config/2.55.0` — selector **"[Version 2.55.0 ▾]"** under the same
  "git-config last updated in 2.56.0" header; the Includes text and the extensions/FILES text are
  identical to the live page (line numbers in §3).

Line numbers in this report are the ones **my** fetch/reader rendered. The wave-1 numbers are a
consistent **+6** on live pages (§4), so section names, not absolute numbers, are the stable
anchor. This is itself an anchor-cell defect in the draft.

## 1. Primary quote check (draft lines 20-21)

Served git-worktree line 589, with inline markup:

> When `extensions.worktreeConfig` is enabled, the config file
> `.git/worktrees/`*<id>*`/config.worktree` is read after `.git/config` is.

Stripped of inline markup (`<code>`, `<em>`):

> When extensions.worktreeConfig is enabled, the config file
> .git/worktrees/<id>/config.worktree is read after .git/config is.

Draft line 21 is character-identical to the stripped form. Checks:

| criterion | observation | verdict |
|---|---|---|
| verbatim, character-exact modulo inline markup | served and draft strings compare equal after stripping markup; the only markup is the `extensions.worktreeConfig` code span and the `*<id>*` emphasis inside the path | **YES** |
| ≤25 words | 13 words | **YES** |
| anchor it names: `§ DETAILS` | the sentence is the final paragraph of § DETAILS, immediately before `## LIST OUTPUT FORMAT`; my fetch has the sentence at **:589** and the heading at **:591** (draft: 595 / 597, the usual +6) | **section YES; numeric anchor NO** |
| page revision | "git-worktree last updated in 2.56.0", "2.55.0 no changes" | recorded |

Smallest fix: cite "git-worktree § DETAILS, final paragraph before § LIST OUTPUT FORMAT"
instead of `line 595` (or write `:589 in the 2026-10-20 grep rendering`).

**Scope note the reopen prompt makes visible:** the **CONFIGURATION FILE** section does *not*
contain the "read after" sentence. Its own on-scope sentence is at :540:

> "In this mode, specific configuration stays in the path pointed by `git` `rev-parse`
> `--git-path` `config.worktree`."

The ordering sentence lives in DETAILS and is linked-worktree-specific (`.git/worktrees/<id>/…`).
The row therefore needs both anchors; the draft's anchor cell names both, so this is a labeling
nit, not a false quote.

## 2. The other draft quotes (checked independently)

| draft | served location (my fetch) | exact text check | words | under 25 |
|---|---|---|---|---|
| Q2 (28-29) | git-config § CONFIGURATION FILE › Includes, heading :1056, `include.path` named :1064, insertion :1068-1069 (draft 1074-1076 / :1062 = +6) | identical | 22 | yes |
| Q3 (36-37) | git-config `status.showUntrackedFiles`: live :8163-8164, pinned 2.55.0 :7944-7945 (draft pinned 7965-7966 does **not** reproduce; +21) | identical | 13 | yes |
| Q4 (44-45) | git-config pinned 2.55.0 :7929-7931 / live :8148-8150 | identical | **13, draft says 14** | yes |
| Q5 (51-52) | git-worktree § DETAILS :575 (draft 580-582 = +6) | identical | **14, draft says 15** | yes |

Q3/Q4 are the `status.showUntrackedFiles`/`-u` material the round plan assigns to **S057**, not
S058. They are verbatim, but they should not anchor S058.

## 3. What the draft missed — counterexamples that change the row

### (a) The general, all-worktrees statement is in git-config, not only in git-worktree DETAILS

git-config § CONFIGURATION FILE › Variables › `extensions.*` › `worktreeConfig`, live
**:3889-3893**, pinned 2.55.0 **:3813-3815**:

> "If enabled, then worktrees will load config settings from the `$GIT_DIR/config.worktree` file
> in addition to the `$GIT_COMMON_DIR/config` file." — **18 words**

> "The settings in the `config.worktree` file will override settings from any other config
> files." — **14 words**

This is the general statement for main and linked worktrees; the draft's DETAILS quote is the
linked-worktree-specific sentence. For S058 ("config.worktree as a repository config source")
this entry is the stronger primary anchor, and the draft did not cite it.

### (b) The draft's §3(b) `[INFERENCE]` is falsified by git-config § FILES

Draft lines 120-124 say the off-case is an inference: *"the page never writes 'otherwise it is
ignored'"*. But the row has **two** pages, and git-config § FILES, live **:737-739** (pinned
**:739**), states it explicitly:

> `$GIT_DIR/config.worktree`
>
> "This is optional and is only searched when `extensions.worktreeConfig` is present in
> $GIT_DIR/config." — **13 words**

So the inert case **is** documented: no inference flag is needed in the row's `teaches`, and the
diagnostic can say "extension off → file inert" as a page fact. The draft's conclusion
(presence-based refusal is the conservative choice) survives, but its stated basis is incomplete.

### (c) The locator is defined by the page as `$GIT_DIR/config.worktree`

git-config § OPTIONS `--worktree`, live **:493-496**:

> "Similar to `--local` except that `$GIT_DIR/config.worktree` is read from or written to if
> `extensions.worktreeConfig` is enabled." — **16 words**

> "Note that `$GIT_DIR` is equal to `$GIT_COMMON_DIR` for the main working tree, but is of the
> form `$GIT_DIR/worktrees/<id>/` for other working trees."

This sharpens draft §3(a): the page itself names `$GIT_DIR/config.worktree` and defines `$GIT_DIR`
per worktree. A guard that uses git's resolved `$GIT_DIR` is on the documented path; the defect is
hand-assembling `$GIT_DIR` without asking git, and `git rev-parse --git-path config.worktree`
remains the page's rule of thumb (:574-576). The draft's stronger claim that using
`$GIT_DIR/config.worktree` "contradicts the page" is not what the page says.

### (d) Includes is on S058's planned scope

The page states `include.path` insertion (Q2), and the round plan assigns "git-config includes" to
S058. S042 already owns the fact; S058 can corroborate it without re-counting. The draft's scope
cell excludes it entirely ("S042's scope and is not re-counted here"), which leaves the planned
S058 half unrepresented.

## 4. Per-cell verdicts on the draft row (draft line 69)

Registry shape: `corpus/SOURCES.md:13`, last row `S050` at `:64`. Draft row is
`.ufo/waves/round-17/w1/SrcGitWorktreeConfig.md:69`.

### id — DISAGREE
- Draft: `S051`.
- Registry fact: the table ends at S050 (`corpus/SOURCES.md:64`), so S051 is the next free
  *registry* id — the draft's own note is true in isolation.
- Plan fact: the round-17 brief reserves **S051 for jj git-compatibility** and **S058 for
  git-worktree config.worktree + git-config includes**. Inserting S051 double-books the plan.
- **Corrected cell: `S058`.**

### source — AGREE
- Draft: `git-worktree(1) and git-config(1) — https://git-scm.com/docs/git-worktree, https://git-scm.com/docs/git-config`.
- Both pages served today; exactly the two documents S058 needs. **Unchanged.**

### kind — AGREE
- Draft: `docs`. Both are vendor manuals. **Unchanged.**

### tier — AGREE
- Draft: `A`. Official git-scm.com manuals; every git-scm docs row in the registry is tier A
  (S001-S004, S035/S036, S042, S045-S047, S049). The frozen `SOURCES-CONTRACT-v1` file is not
  present in `corpus/` (directory holds README.md, SOURCES.md, QUALITY.md, knowledge/, lessons/),
  so this is precedent-based, not a re-read contract. **Unchanged: `A`.**

### scope — DISAGREE
- Draft: `extensions.worktreeConfig` adding `config.worktree` as a repository config source, and
  the explicit `-u`/`--untracked-files` override of `status.showUntrackedFiles`; `include.path`
  insertion is S042's scope and is not re-counted here.
- Defects: (i) the `-u`/`status.showUntrackedFiles` half belongs to **S057** per the plan, so
  keeping it here leaves S057 empty and makes S058 cover two planned rows; (ii) the
  `include.path` half that the plan assigns to S058 is omitted. Neither is a page overclaim; it
  is a plan-fit/scope-split defect. The page statements themselves are accurate.
- **Corrected cell:**
  `` `extensions.worktreeConfig` making `$GIT_DIR/config.worktree` a repository config source
  loaded in addition to `$GIT_COMMON_DIR/config` and overriding other config files; `include.path`
  insertion (already S042's fact, corroborated here and not re-counted). The
  `-u`/`--untracked-files` override of `status.showUntrackedFiles` belongs to S057. ``

### anchor — DISAGREE
- Draft: `web manuals "git-worktree last updated in 2.56.0" ("2.55.0 no changes") and
  "git-config last updated in 2.56.0"; git-worktree § CONFIGURATION FILE lines 540-548 and
  § DETAILS lines 580-582, 595; git-config § CONFIGURATION FILE line 991 and
  § status.showUntrackedFiles lines 7934-7937, 7965-7966 at /docs/git-config/2.55.0;
  opened 2026-10-20`.
- Defects: (i) the absolute line numbers do not reproduce: worktree ordering :589 (not :595),
  LIST OUTPUT FORMAT :591 (not :597), rule of thumb :574-576 (not :580-582), CONFIGURATION FILE
  quotes :534/:540-542 (not :540-548); git-config Includes heading :1056 (not :1062), insertion
  :1068-1069 (not :1074-1076), CONFIGURATION FILE intro :985 (not :991); pinned status override
  :7944-7945 (not :7965-7966). The live-page offset is a consistent +6; the pinned status
  citations are +5/+6 for Q4 and +21 for Q3, so these are renderer-relative numbers, not page
  coordinates. (ii) The strongest
  on-scope anchors are missing: git-config § FILES :737-739, § OPTIONS `--worktree` :493-496,
  § CONFIGURATION FILE › `extensions.*` › `worktreeConfig` :3889-3893. (iii) The pinned location
  is only named for the status quotes; the FILES/extensions text should be pinned too (it is at
  pinned :739 and :3813-3815).
- **Corrected cell:**
  ``git-worktree § CONFIGURATION FILE (534 "In order to have worktree-specific configuration…";
  540-542 "In this mode, specific configuration stays in the path pointed by git rev-parse
  --git-path config.worktree… Older Git versions will refuse…"), § DETAILS (574-576 rule of
  thumb; 589 ".git/worktrees/<id>/config.worktree is read after .git/config"); git-config
  § FILES `$GIT_DIR/config.worktree` (737-739: optional, "only searched when
  extensions.worktreeConfig is present"), § OPTIONS `--worktree` (493-496: read from or written
  to if enabled; `$GIT_DIR` = `$GIT_COMMON_DIR` for the main tree,
  `$GIT_COMMON_DIR/worktrees/<id>/` for others), § CONFIGURATION FILE › `extensions.*` ›
  `worktreeConfig` (3889-3893: load in addition to `$GIT_COMMON_DIR/config`, settings override
  other config files), § Includes (1056, 1064, 1068-1069); web manuals "git-worktree last updated
  in 2.56.0" with "2.55.0 no changes" and "git-config last updated in 2.56.0" (the pinned 2.55.0
  page repeats the FILES and extensions text at 739 and 3813-3815); opened 2026-10-20``.

### teaches — DISAGREE (in part)
- Draft: `` `config.worktree` is read after `.git/config` once `extensions.worktreeConfig` is on,
  and `-u`/`--untracked-files` overrides `status.showUntrackedFiles`, so the census must pass the
  option explicitly and locate the file with `git rev-parse --git-path config.worktree` instead
  of assuming `$GIT_DIR` ``.
- Defects: (i) **"must pass the option explicitly" is a design inference**, not a page statement;
  the page says the variable *can be overridden* (Q3), not that a reader must override it.
  Registry precedent hedges such consequences (S045: "a defensive choice, since this page does
  not state…"). (ii) **"config.worktree is read after `.git/config`" is stated for the
  linked-worktree path** `.git/worktrees/<id>/config.worktree`; the general load/override
  statement is git-config's `extensions.worktreeConfig` entry. (iii) **"instead of assuming
  `$GIT_DIR`" is too strong**: git-config § OPTIONS defines the path as `$GIT_DIR/config.worktree`
  with `$GIT_DIR` per worktree; the page's rule of thumb is to use
  `git rev-parse --git-path`, not to avoid the variable. (iv) Includes is omitted.
- **Corrected cell:**
  ``when `extensions.worktreeConfig` is enabled, worktrees load config from
  `$GIT_DIR/config.worktree` in addition to `$GIT_COMMON_DIR/config`, and those settings override
  other config files; the file is optional and only searched when the extension is present; the
  linked-worktree file `.git/worktrees/<id>/config.worktree` is read after `.git/config`; the
  rule of thumb is to resolve the path with `git rev-parse --git-path` instead of assuming which
  of `$GIT_DIR`/`$GIT_COMMON_DIR` it belongs to; included files insert their contents at the
  directive``.

### status — DISAGREE as drafted
- Draft: `mined`, `used-by corpus/lessons/round-17.md`.
- `corpus/lessons/round-17.md` does **not** exist (glob: missing), so `mined` plus that used-by
  would trip the registry's missing-used-by census. The draft's own integration note (lines
  83-88) says to insert as `queued` with `used-by —` and flip when the lesson cites it; the row
  cell was not written that way.
- **Corrected cell: `queued`**, with `used-by —`; flip to `mined` and add the lesson path only
  when `corpus/lessons/round-17.md` exists and cites S058.

### opened — AGREE
- Draft: `2026-10-20`. I re-opened both pages today. **Unchanged.**

### recheck — AGREE
- Draft: `on-release`. Both pages carry a 2.56.0 "last updated" line, which is the registry
  convention for versioned git-scm pages (S001-S004, S042, S045-S047, S049). **Unchanged.**

### used-by — CONDITIONAL
- Draft: `corpus/lessons/round-17.md`. Correct once that lesson lands and cites S058; today the
  path is absent, so the insertable value is `—`. **Corrected cell: `—`** (flip with `status`).

## 5. Corrected row (copy-ready, 11 cells, no `|` inside a cell)

```markdown
| S058 | git-worktree(1) and git-config(1) — https://git-scm.com/docs/git-worktree, https://git-scm.com/docs/git-config | docs | A | `extensions.worktreeConfig` making `$GIT_DIR/config.worktree` a repository config source loaded in addition to `$GIT_COMMON_DIR/config` and overriding other config files; `include.path` insertion (already S042's fact, corroborated here and not re-counted). The `-u`/`--untracked-files` override of `status.showUntrackedFiles` belongs to S057. | git-worktree § CONFIGURATION FILE (534 "In order to have worktree-specific configuration…"; 540-542 "In this mode, specific configuration stays in the path pointed by git rev-parse --git-path config.worktree… Older Git versions will refuse…"), § DETAILS (574-576 rule of thumb; 589 ".git/worktrees/<id>/config.worktree is read after .git/config"); git-config § FILES `$GIT_DIR/config.worktree` (737-739: optional, "only searched when extensions.worktreeConfig is present"), § OPTIONS `--worktree` (493-496: read from or written to if enabled; `$GIT_DIR` = `$GIT_COMMON_DIR` for the main tree, `$GIT_COMMON_DIR/worktrees/<id>/` for others), § CONFIGURATION FILE › `extensions.*` › `worktreeConfig` (3889-3893: load in addition to `$GIT_COMMON_DIR/config`, settings override other config files), § Includes (1056, 1064, 1068-1069); web manuals "git-worktree last updated in 2.56.0" with "2.55.0 no changes" and "git-config last updated in 2.56.0" (the pinned 2.55.0 page repeats the FILES and extensions text at 739 and 3813-3815); opened 2026-10-20 | when `extensions.worktreeConfig` is enabled, worktrees load config from `$GIT_DIR/config.worktree` in addition to `$GIT_COMMON_DIR/config`, and those settings override other config files; the file is optional and only searched when the extension is present; the linked-worktree file `.git/worktrees/<id>/config.worktree` is read after `.git/config`; the rule of thumb is to resolve the path with `git rev-parse --git-path` instead of assuming which of `$GIT_DIR`/`$GIT_COMMON_DIR` it belongs to; included files insert their contents at the directive | queued | 2026-10-20 | on-release | — |
```

Insertion notes for L1:

- If rows are inserted strictly in id order, S058 waits for S051-S057; if L1 inserts out of order,
  the gap is harmless because the plan reserves the numbers.
- The S057 row needs the Q3/Q4 material this draft verified: git-config `status.showUntrackedFiles`
  (live :8145/:8163-8164, pinned :7926/:7944-7945) and the git-status(1) page (S044 was rejected
  for a narrower claim; a fresh S057 row should cite git-config plus the git-status page under its
  own scope). Do not drop the verified Q3/Q4 text with the renumbering.
- If L1 prefers `mined` immediately, it must land `corpus/lessons/round-17.md` in the same
  integration and make it cite S058; otherwise the census prints the row as missing-used-by.

## 6. Commands run and outputs (reading seat; no bash command executed)

| tool | target / pattern | observed output |
|---|---|---|
| `read` | `https://git-scm.com/docs/git-worktree` | served; "git-worktree last updated in 2.56.0"; version entry "2.55.0 no changes"; § CONFIGURATION FILE heading and quotes; § DETAILS and § BUGS |
| `grep` | worktree URL: `read after\|LIST OUTPUT FORMAT\|last updated in` | version :156; sentence :589; `## LIST OUTPUT FORMAT` :591 |
| `grep` | worktree URL: `^## CONFIGURATION FILE\|^## DETAILS\|^## BUGS\|In order to have worktree-specific configuration\|In this mode, specific configuration\|Older Git versions will refuse\|do not make any assumption` | headings :527, :558, :732; quotes :534, :540-542; rule of thumb :575 |
| `grep` | worktree URL: `config\.worktree\|worktreeConfig` | all occurrences; confirms the ordering sentence is the only "read after" statement and is linked-worktree-scoped |
| `read` | `https://git-scm.com/docs/git-config` § CONFIGURATION FILE intro :982-990 | "The files `.git/config` and optionally `config.worktree` … are used to store the configuration for that repository" |
| `grep` | git-config URL: `contents of the included file are inserted\|last updated in 2\.56\.0\|^### Includes\|status.showUntrackedFiles` | header :155; `### Includes` :1056; insertion :1068-1069; `status.showUntrackedFiles` :8145 |
| `read` | git-config URL :488-499 | `--worktree`: "Similar to `--local` except that `$GIT_DIR/config.worktree` is read from or written to if `extensions.worktreeConfig` is enabled…"; `$GIT_DIR` = `$GIT_COMMON_DIR` for the main tree, `$GIT_COMMON_DIR/worktrees/<id>/` otherwise |
| `read` | git-config URL :728-746 | § FILES `$GIT_DIR/config.worktree`; "This is optional and is only searched when `extensions.worktreeConfig` is present in $GIT_DIR/config." |
| `read` | git-config URL :3884-3904 | `extensions.*` › `worktreeConfig`: load in addition to `$GIT_COMMON_DIR/config`; settings override other config files |
| `grep` | git-config URL: `^## ` and `^extensions\|^### extensions` | `## CONFIGURATION FILE` :982; no separate extensions top-level; `extensions.*` :3774; `worktreeConfig` :3889 |
| `grep` | git-config URL: `worktreeConfig\|config\.worktree` | `--worktree` :493-496; FILES :737-739; intro :985; `includeIf worktree` note :1148-1149; extensions entry :3889-3893 |
| `grep` | `https://git-scm.com/docs/git-config/2.55.0`: `contents of the included file are inserted\|can be overridden with the\|last updated in` | header "Version 2.55.0 / git-config last updated in 2.56.0" :155; insertion :1068-1069; override :7944-7945 |
| `grep` | pinned git-config URL: `worktrees will load config settings\|only searched when` | FILES :739; extensions entry :3813-3815 |
| `grep` | pinned git-config URL: `^status\.showUntrackedFiles\|Directories which\|contain only untracked files\|can be overridden with the` | heading :7926; "Directories…" :7929-7931; override :7944-7945 |
| `glob` | `corpus/SOURCES-CONTRACT*; corpus/lessons/round-17.md` | no contract file; `corpus/lessons/round-17.md` missing |
| `read` | `corpus/` | README.md, SOURCES.md, QUALITY.md, knowledge/, lessons/ (no contract file) |
| `grep` | `corpus/SOURCES.md`: `^\| S050 \|` / `^\| id \|` | header :13; last row S050 :64 |
| `grep` | draft `.ufo/waves/round-17/w1/SrcGitWorktreeConfig.md`: quote/row/inference patterns | Q1 :20-21; Q2 :28-29; Q3 :36-37; Q4 :44-45; Q5 :51-52; row :69; §3(b) inference :120-124; Gate :203-206 |

Tool installs: **none** — nothing was installed or upgraded, so there is no tool/version/channel
record to add.

## 7. Remaining unknowns

1. **Frozen tier contract.** `SOURCES-CONTRACT-v1` is not a lane file (`corpus/` has no such
   file), so tier A is judged from registry precedent (all git-scm docs rows are A), not from
   contract text. If L1 has the frozen contract elsewhere, re-check the A definition against it.
2. **Host binary.** I did not run `git --version`; the version claims rest on the served page
   stamps ("2.55.0 no changes" for worktree; the pinned 2.55.0 git-config page repeats the same
   text). The context states host git 2.55.0.
3. **Line numbers.** All numbers above are my 2026-10-20 fetch rendering. The wave-1 numbers are
   +6 on live pages, so they came from a renderer with six extra header lines; the sections are
   right, the absolute numbers are not portable. The corrected anchor cell leads with section
   names for this reason.
4. **git-status(1) for S057.** I did not re-open the git-status page; S057's git-status half is
   outside this seat. The Q3/Q4 git-config quotes are verified and should move to S057.
5. **Runtime proof.** None. Nothing here shows a census or fixture emits the diagnostic; this
   seat only checked documentation text and the draft's cells.
