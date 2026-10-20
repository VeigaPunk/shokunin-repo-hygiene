STATUS: DONE — S057's primary quote is verbatim, 13 words, at the named anchor; the conditional claim holds as documentation, but the drafted row fails on `id` and `status` at ddb7347 and is imprecise in `source`/`teaches` (corrections below).

# Re-open S057 — `status.showUntrackedFiles` vs `-u|--untracked-files`

Seat ReopenS057-2, wave 2 (falsify). Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Target: `corpus/SOURCES.md` row drafted by wave-1 seat SrcGitShowUntracked
(`.ufo/waves/round-17/w1/SrcGitShowUntracked.md` §5). Question: is the primary quote
verbatim and ≤25 words at the anchor it names, what version line does each page serve today,
and do the drafted `tier`/`status`/`scope`/`teaches` cells claim anything the page does not
state?

Opened independently 2026-10-20. No `ALLOWED-EXEC` item was in this ticket, so no fixture or
repository was executed; every check below is a read, a `git show`/`ls-tree`/`cat-file`, or a
`zcat`/`grep` of a named man page.

## 1. Access record (served today)

| page | URL | version / last-updated line served | opened |
|---|---|---|---|
| git-config(1) | https://git-scm.com/docs/git-config | `git-config last updated in 2.56.0`; version list entry `2.56.0 … *2026-09-28*` | 2026-10-20 |
| git-status(1) | https://git-scm.com/docs/git-status | `git-status last updated in 2.53.0`; first list entry `2.54.0 → 2.56.0 no changes` | 2026-10-20 |

Host mirror: `git --version` → `git version 2.56.0`; installed
`/usr/share/man/man1/git-config.1.gz` and `git-status.1.gz` carry the same sentences at the
lines cited in §4 below. So the web text is not version drift against the installed copy.

Line numbers inside `artifact://70371` / `artifact://70363` in this report are read-tool
coordinates of the served page, not page anchors; the anchor is the section name.

## 2. Primary quote — VERBATIM, 13 words, anchor correct

Served, git-config § `status.showUntrackedFiles`, final paragraph (artifact lines 8151
heading, 8168–8170 sentence; the entry ends there, `status.submoduleSummary` follows):

> All usual spellings for Boolean value `true` are taken as `normal` and `false` as `no`.
> This variable can be overridden with the -u|--untracked-files option
> of [git-status[1]](/docs/git-status) and [git-commit[1]](/docs/git-commit).

Rendered with inline markup stripped (the draft's declared convention), that is exactly the
draft's quote:

> This variable can be overridden with the -u|--untracked-files option of git-status[1] and git-commit[1].

- Character-exactness: every character matches; the only differences are the anchor link
  `[git-status[1]](/docs/git-status)` → `git-status[1]` and the same for `git-commit[1]`,
  which the convention explicitly allows. The literal `-u|--untracked-files` (no spaces
  around the pipe) is correct.
- Word count: This1 variable2 can3 be4 overridden5 with6 the7 `-u|--untracked-files`8
  option9 of10 `git-status[1]`11 and12 `git-commit[1]`13. **13 ≤ 25.**
- Anchor: § `status.showUntrackedFiles`, last paragraph of the entry, and the draft's extra
  positional claim ("immediately after 'All usual spellings…'") is exact.
- **Verdict: agree.** The quote is admissible as a located quote; it also contains a literal
  `|`, so it must never be pasted into a registry cell (see §3, row-format note).

## 3. Per-cell verdicts on the drafted row

Drafted cell text is taken from `.ufo/waves/round-17/w1/SrcGitShowUntracked.md` line 148
(untruncated), in the registry column order confirmed at `corpus/SOURCES.md:17-18`:
`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.

| cell | drafted | verdict | why (at ddb7347 unless stated) |
|---|---|---|---|
| id | `S0??` (note: "next unused id is S051") | **disagree** | The landed registry does end at S050 (`corpus/SOURCES.md:64`), so "next unused" is true of the file as it stands. But the round's planned numbering reserves S051–S056 for the six jj rows and S057 for this row (wave context, "Planned SOURCES numbering"). The integration note is stale; the id cell must be **S057**. |
| source | `git-config(1) status.showUntrackedFiles — https://git-scm.com/docs/git-config` | **partial** | The row's `teaches` takes its normal-vs-all clause from the **git-status** page, but `source` names only git-config. Corrected source names both pages (list both URLs, or keep the git-config URL and put the git-status URL in `anchor`, which already names the sections). |
| kind | `docs` | **agree** | Official manual page; same kind as S042/S044–S047/S049. |
| tier | `A` | **agree** | Tier definitions live in `SOURCES-CONTRACT-v1` (`corpus/SOURCES.md:3`), which is **not in the tree at ddb7347** (`git ls-tree -r --name-only ddb7347 | grep -i contract` → only `.ufo/waves/round-15/w1/ReportContract.md` and `census/round-4/cli-contract.json`), so the available check is in-registry consistency: every official git-scm manual row is A (S042, S044, S045, S046, S047, S049); B is vendor/community (S014, S017, S029), C is a community article (S030). A holds by that rule. |
| scope | "documented **precedence** of the -u/--untracked-files option over status.showUntrackedFiles for git-status enumeration, and the normal-versus-all mode boundary, not a runtime proof on this host" | **partial** | No overreach in substance: the page says "can be **overridden**", which is exactly the claim, and the disclaimer "not a runtime proof on this host" is correct. Two precision defects: (a) use the page's word *override* rather than *precedence* — the page states no general ordering among config sources, only that this variable is overridden by the option; (b) the mode boundary is stated on **git-status**, not on the git-config page the source cell names, and `teaches` also leans on "no option behaves as normal", which the drafted scope omits. Narrowing to git-status (while the page also names git-commit) does **not** overreach. |
| anchor | version lines, § names, roff 11884/11936 and git-status 90-94, 98-111, 137-140, 1131 | **agree** | Every named location verified (§4). Nothing in the cell exceeds the served text. |
| teaches | "a command-line untracked-files option overrides the config that suppresses untracked enumeration, and **normal keeps one line per untracked directory** while all expands it, so the census can pin normal without changing the collapse" | **partial** | Clause 1 is stated. Clause 3 is stated ("When -u option is not used, untracked files and directories are shown (i.e. the same as specifying normal)"). Clause 2 is **looser than the page**: the page's qualifier is *directories which contain only untracked files* ("Directories which contain only untracked files, are shown with the directory name only"), and git-status's `all` bullet says "individual files in **untracked** directories". A directory that also holds tracked files is not covered by that collapse; "one line per untracked directory" invites that misreading. The landed census comment is already stricter — `tools/souji-census.sh:1112-1115` says "keeps the one-line collapse of a **wholly untracked** directory". Match the page, not the shorthand. |
| status | `mined` | **disagree at ddb7347** | `mined` is a use claim whose `used-by` must exist (every mined row in the registry names an existing file). The drafted used-by `corpus/lessons/round-17.md` **does not exist at ddb7347**: `git cat-file -e ddb7347:corpus/lessons/round-17.md` → `fatal: path … does not exist`, rc 128; `git ls-tree -r --name-only ddb7347 corpus/lessons` lists round-1 … round-16 only. The *code* use is real (census pin at `tools/souji-census.sh:1118`, header notes at `:1-9`, `:36-41`, `:100-103`), but the registry's used-by convention is a corpus note/lesson, so at the landed revision the truthful cell is `queued` + `—`. Correct to `mined` + `corpus/lessons/round-17.md` only if L1 lands that lesson in the same integration. |
| opened | `2026-10-20` | **agree** | Both pages served today; access record in §1. |
| recheck | `on-release` | **agree** | Consistent with the git-scm doc rows (S042, S043, S045–S047, S049) and correct for a page that is versioned per git release. |
| used-by | `corpus/lessons/round-17.md` | **disagree at ddb7347** | Same evidence as `status`: path absent at the landed commit. `—` until the lesson lands. |

Row-format note (carried from the draft, still true): one line, **no `|` inside any cell**.
The primary quote itself contains `-u|--untracked-files`, so it cannot be pasted verbatim
into `teaches`/`scope`; the drafted row correctly paraphrased it, and any correction must keep
doing so.

### Corrected row (single line, cells pipe-free)

```
| S057 | git-config(1) status.showUntrackedFiles and git-status(1) --untracked-files — https://git-scm.com/docs/git-config, https://git-scm.com/docs/git-status | docs | A | documented override of status.showUntrackedFiles by the -u/--untracked-files option (the page names git-status and git-commit), the normal-versus-all boundary for a directory holding only untracked files, and the no-option-equals-normal equivalence, not a runtime proof on this host | web manual "git-config last updated in 2.56.0" (2.56.0 dated 2026-09-28), opened 2026-10-20, § status.showUntrackedFiles final paragraph; companion git-status "last updated in 2.53.0", "2.54.0 → 2.56.0 no changes", § OPTIONS -u and --untracked-files, § OPTIONS default-changed sentence, § UNTRACKED FILES AND PERFORMANCE first bullet; installed git 2.56.0 git-config(1) roff 11884 and 11936-11939, git-status(1) roff 90-94, 98-111, 113-116, 137-140, 1131 | a command-line untracked-files option overrides the config that suppresses untracked enumeration; a directory holding only untracked files is one line under normal while all also lists the files inside it; and status without the option already behaves as normal, so the census can pin normal without changing the collapse | queued | 2026-10-20 | on-release | — |
```

Flip `status`/`used-by` to `mined` / `corpus/lessons/round-17.md` only when that lesson is in
the landed tree. If L1 keeps one URL per row, move the git-status URL into `anchor` and leave
the git-config URL in `source`; do not drop the git-status page from the row while `teaches`
still carries the mode boundary.

## 4. Anchor verification (all named locations)

git-config web, § `status.showUntrackedFiles`, served artifact lines 8151–8170: heading;
"Directories which contain only untracked files, are shown with the directory name only";
`no` / `normal` / `all` bullets; "If this variable is not specified, it defaults to *normal*.";
the boolean sentence; the override sentence. Every anchor the draft names exists and says
what the draft says.

Installed man pages, observed:

- `git-config.1.gz`: `11884:status\&.showUntrackedFiles` (heading);
  `11936` starts `\fBno\fR\&. This variable can be overridden with the \-u|\-\-untracked\-files option of`
  continuing `git-status(1)` / `and` / `git-commit(1)\&.` on 11937–11939. Draft's `11884`,
  `11936-11939` exact.
- `git-status.1.gz`: `90` "It is optional: it defaults to"; `\fBall\fR` on 91; mode bullets
  `no`/`normal`/`all` within 98–111 with the exact wordings the draft quotes; the
  "When -u option is not used … same as specifying normal" paragraph at 113–116;
  `138:\fBstatus\&.showUntrackedFiles\fR` inside the default-changed sentence at 137–140;
  `1131:\fBstatus\&.showUntrackedFiles=no\fR` in the first performance bullet. Draft's
  `90-94`, `98-111`, `137-140`, `1131` exact.

Supporting quote: served first bullet of § UNTRACKED FILES AND PERFORMANCE is
"The --untracked-files=no flag or the status.showUntrackedFiles=no config (see above for
both): indicate that git status should not report untracked files." — the draft's text is
character-exact after markup stripping and joining the line wraps, and is 20 words (≤25).

Contradiction check, both pages: nothing contradicts "the config suppresses enumeration" or
"the option overrides the variable". The three adjacent bounds the draft reports are real and
quoted accurately: bare `-u` defaults to `all`; `--porcelain` promises format stability
"across Git versions and regardless of user configuration" (not enumeration stability); and
`extensions.worktreeConfig`/'config.worktree' says "The settings in the `config.worktree`
file will override settings from any other config files." (served lines 3898–3899) — verbatim.

## 5. Falsifier beyond the row: wave-1 line numbers are base-relative, and the §4.1 gap is live

The wave-1 report's §4.1 finding survives at the landed revision, with shifted line numbers
and one broader exposure:

- `git show ddb7347:tools/souji-census.sh | grep -n 'untracked-files'` → `6`, `38`, `100`
  (comments) and **`1118`** (the `--untracked-files=normal` token). The report's `:1037` is
  the base-revision line.
- `git show ddb7347:tools/souji-census.sh | grep -n 'GIT_CONFIG_GLOBAL|SYSTEM|NOSYSTEM'`
  → `171:export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null`,
  `172:export GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0`. Report's `:153-154` is
  base-relative. `GIT_CONFIG_COUNT=2`, `GIT_CONFIG_KEY_0/1` at `180-181` — the draft's
  "two GIT_CONFIG_KEY_* entries" claim is confirmed.
- `git show ddb7347:tools/souji-verify.sh | grep -n 'status --porcelain|untracked-files'`
  → `361`, `405`, `865` with **no** untracked mode, and `697` with
  `--untracked-files=all`. The report's `:322`, `:366`, `:820`, `:658` are base-relative.
- Stronger than the report: `git show ddb7347:tools/souji-verify.sh | grep -n 'GIT_CONFIG'`
  → **no output**. `souji-verify.sh` neutralises neither the global nor the system layer, so
  its three unpinned dirty probes are exposed to a *global or system*
  `status.showUntrackedFiles=no` as well as a repo-local one; the census is exposed only to
  the repo-local/included/`config.worktree` layers because it pins `GIT_CONFIG_GLOBAL`,
  `GIT_CONFIG_SYSTEM` and `GIT_CONFIG_NOSYSTEM`. At `evaluate_repo_root`
  (`souji-verify.sh:361`) an empty status sets `dirty=0` and `R_RECEIPT=none`, so the receipt
  path can certify a dirty repository as clean — the w1 finding stands and widens.
- Consequence for the census header: `tools/souji-census.sh:38-39` reads "explicit
  --untracked-files=normal: a wholly untracked directory is one line, **matching
  souji-verify**". That is true only while no config suppresses enumeration; under
  `status.showUntrackedFiles=no` the two tools diverge and the comment misleads. This is the
  same divergence the wave-1 report predicted, now evidenced at the landed lines.

## 6. Verdict summary

- Primary quote: **holds** — verbatim, 13 words, at the named anchor; pages served
  git-config 2.56.0 (2026-09-28) and git-status 2.53.0 ("2.54.0 → 2.56.0 no changes") today.
- Row cells: `kind`, `tier`, `anchor`, `opened`, `recheck` **agree**; `id` and `status`
  (+ `used-by`) **disagree at ddb7347**; `source`, `scope`, `teaches` **partial** with the
  corrected text in §3. No cell claims runtime behavior; the "not a runtime proof" disclaimer
  is present and correct.
- Smallest fix for L1: take the §3 corrected row, assign **S057**, leave `status: queued`
  until `corpus/lessons/round-17.md` lands, and keep the git-status URL reachable from the row.

## 7. Remaining unknowns

- Tier definitions are not readable in-tree at ddb7347 (`SOURCES-CONTRACT-v1` absent); the A
  verdict rests on in-registry consistency, not on the frozen contract text. [limitation]
- Whether L1 lands `corpus/lessons/round-17.md` in the same integration determines
  `mined` vs `queued`; I can only observe that it is absent at ddb7347. [open]
- The page states no precedence between `-c`/`GIT_CONFIG_COUNT` and `config.worktree`, so the
  census's existing `-c`-style pins are not documented as overriding a worktree config; the
  row correctly does not claim that. [open, unchanged from wave 1]
- Runtime confirmation that `--untracked-files=normal` restores untracked lines under a
  repo-local `showUntrackedFiles=no` remains the fixture's job (`tests/fixtures/
  r17-census-hygiene.py`); I ran no repository, per the probe rule. [not exercised]

## 8. Commands run and observed output

- `read https://git-scm.com/docs/git-config` → served; header `git-config last updated in
  2.56.0`; list entry `2.56.0 … *2026-09-28*`.
- `read https://git-scm.com/docs/git-status` → served; `git-status last updated in 2.53.0`;
  first entry `2.54.0 → 2.56.0 no changes`.
- `grep 'showUntrackedFiles|overridden with the -u' artifact://70371` → 8151 heading,
  8168–8170 boolean + override sentences.
- `grep 'UNTRACKED FILES AND PERFORMANCE|should not report untracked|default can be changed'
  artifact://70363` → 709 heading, 719–723 first bullet, 306 default-changed sentence.
- `read artifact://70371:8145-8172:raw` and `artifact://70363:700-735:raw` → full entry and
  first-bullet text quoted in §2/§4.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb7347…:tools/souji-census.sh |
  grep -n 'untracked-files|default untracked'` → 6, 38, 100, 1118.
- `… show ddb7347…:tools/souji-verify.sh | grep -n 'status --porcelain|untracked-files'` →
  361, 405, 697, 865.
- `zcat /usr/share/man/man1/git-config.1.gz | grep -n 'can be overridden with the|
  status.showUntrackedFiles'` → 11936; `grep -n 'status\&\.showUntrackedFiles'` → 11884.
- `zcat /usr/share/man/man1/git-status.1.gz | sed -n '88,116p'` → the mode paragraph and
  bullets; `grep -n 'showUntrackedFiles|defaults to |It is optional'` → 90, 138, 1131.
- `git --version` → `git version 2.56.0`.
- `git … cat-file -e ddb7347…:corpus/lessons/round-17.md` → `fatal: path … does not exist`,
  rc=128.
- `git … ls-tree -r --name-only ddb7347… corpus | grep -i 'sources|lesson'` → `corpus/SOURCES.md`
  and `corpus/lessons/round-1.md … round-16-verifier-spotcheck.md`, no round-17.
- `git … ls-tree -r --name-only ddb7347… | grep -iE 'contract|QUALITY.md|PROVINCE'` → no
  SOURCES contract file.
- `git … show ddb7347…:tools/souji-census.sh | grep -n 'GIT_CONFIG'` → 129, 171–172, 180–181;
  same grep on `souji-verify.sh` → empty.
- `git … show ddb7347…:tools/souji-census.sh | sed -n '1100,1125p'` → the dirty-count call
  with `--untracked-files=normal` at 1118 and the round-17 comment above it.
- Lane reads: `corpus/SOURCES.md:1-70,74-98`; `corpus/QUALITY.md:1-25`; `corpus/README.md`;
  wave-1 report `SrcGitShowUntracked.md` (whole, with line 148 re-read raw).

## 9. Tooling record

No install or upgrade performed. `pacman` stays paused host-wide; nothing was needed — the two
pages are reachable through the web reader and the installed git 2.56.0 man pages cover the
mirror checks. Nothing was written outside this report.
