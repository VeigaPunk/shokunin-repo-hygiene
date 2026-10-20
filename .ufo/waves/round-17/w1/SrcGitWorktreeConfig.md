STATUS: DONE — both pages state it: `extensions.worktreeConfig` makes `config.worktree` a repository config source read after `.git/config`, `include.path` inserts a foreign file's keys at the directive, and the D1 fix's `-u` override is stated verbatim on git-config; three precision corrections to the claim text.

# SrcGitWorktreeConfig — source opening, git-worktree(1) + git-config(1)

Seat: W1 source opening (round 17). Question: do the two named pages state that
`extensions.worktreeConfig` makes `$GIT_DIR/config.worktree` part of the config and that
`include.path` pulls keys from another file — the D1 arrival variants?

**Verdict: holds, on both counts, plus the D1 override sentence the r16 rows left open.**
The pages say it explicitly, not by implication. Neither page says `not stated` for the
question as asked. The claim text needs three precision fixes (§4) because the pages name a
different locator than the one the claim writes down.

## 1. Located verbatim quotes

All quotes are exact text of the served page with only inline markup stripped
(`<code>`, `<em>`, link wrappers). Word counts are mine; every one is ≤25. Access date
2026-10-20 for every read.

**Q1 — config.worktree is read as config, after `.git/config`.** 13 words.
> "When extensions.worktreeConfig is enabled, the config file .git/worktrees/<id>/config.worktree is read after .git/config is."

Location: git-worktree(1), `§ DETAILS`, served page line 595 (immediately before
`## LIST OUTPUT FORMAT` at :597). Served revision: page header
"git-worktree last updated in 2.56.0", version list entry "2.55.0 no changes" — so this text
is identical for host git 2.55.0.

**Q2 — include.path inserts another file's keys in place.** 22 words.
> "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive."

Location: git-config(1), `§ CONFIGURATION FILE › Includes`, lines 1074-1076; heading
`### Includes` at :1062. Served revision: `/docs/git-config/2.55.0` (page header
"git-config last updated in 2.56.0", selector "Version 2.55.0"); byte-identical wording at
the same lines on the live 2.56.0 page.

**Q3 — the explicit override that D1's fix depends on.** 13 words.
> "This variable can be overridden with the -u|--untracked-files option of git-status[1] and git-commit[1]."

Location: git-config(1), `§ CONFIGURATION FILE › status.showUntrackedFiles`, lines 7965-7966
(entry heading at :7932), `/docs/git-config/2.55.0`. Same wording on live 2.56.0 at
:8169-8170. This is not in the `Includes` or first-paragraph material the question named; it
is later in the same page, in the variable reference.

**Q4 — `normal` is the one-line directory collapse the claim says it keeps.** 14 words.
> "Directories which contain only untracked files, are shown with the directory name only."

Location: git-config(1), `§ status.showUntrackedFiles`, lines 7934-7937 (the sentence spans
:7935-7937), `/docs/git-config/2.55.0`. So `--untracked-files=normal` keeps the collapse and
`all` would break it — the claim's parenthetical is grounded.

**Q5 (locator, secondary).** 15 words.
> "do not make any assumption about whether a path belongs to $GIT_DIR or $GIT_COMMON_DIR"

Location: git-worktree(1), `§ DETAILS`, lines 580-582, completing
"… when you need to directly access something inside `$GIT_DIR`. Use `git` `rev-parse` `--git-path` to get the final path."

**Measured and excluded as over the cap:** the includes *relative-path* sentence
"The variable takes a pathname as its value, and is subject to tilde expansion" (:1070-1072)
is fine, but "If the value of the variable is a relative path, the path is considered to be
relative to the configuration file in which the include directive was found" (:1075-1078) is
30 words — cited as secondary context only, never as the row's grounding quote.

## 2. Draft SOURCES row

Column order per `corpus/SOURCES.md` `## Registry`:
`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`

```markdown
| S051 | git-worktree(1) and git-config(1) — https://git-scm.com/docs/git-worktree, https://git-scm.com/docs/git-config | docs | A | `extensions.worktreeConfig` adding `config.worktree` as a repository config source, and the explicit `-u`/`--untracked-files` override of `status.showUntrackedFiles`; `include.path` insertion is S042's scope and is not re-counted here | web manuals "git-worktree last updated in 2.56.0" ("2.55.0 no changes") and "git-config last updated in 2.56.0"; git-worktree § CONFIGURATION FILE lines 540-548 and § DETAILS lines 580-582, 595; git-config § CONFIGURATION FILE line 991 and § status.showUntrackedFiles lines 7934-7937, 7965-7966 at /docs/git-config/2.55.0; opened 2026-10-20 | `config.worktree` is read after `.git/config` once `extensions.worktreeConfig` is on, and `-u`/`--untracked-files` overrides `status.showUntrackedFiles`, so the census must pass the option explicitly and locate the file with `git rev-parse --git-path config.worktree` instead of assuming `$GIT_DIR` | mined | 2026-10-20 | on-release | corpus/lessons/round-17.md |
```

Integration notes for L1:

- **Id.** `S051` is the next unused id observed in the registry (rows end at S050; the
  `Path`/`Search log`/`Leads` sections that follow hold no rows). Renumber if integration
  assigns differently; no other cell depends on the number.
- **No `|` in any cell.** `-u|--untracked-files` appears with a pipe in Q3; the row writes it
  as `-u`/`--untracked-files` so `awk -F'|' … NF!=13` stays clean. Do not paste Q3 raw into a cell.
- **Overlap is declared, not re-counted.** `include.path` insertion is already S042
  ("included contents take effect at the directive"). Q2 corroborates S042 for host 2.55.0;
  it is deliberately outside this row's `scope` so the round does not book the same fact
  twice. The new ground is `config.worktree` (absent from S042) and the `-u` override.
- **Status.** `mined` because it grounds the C1/D1 lane change: `count_dirty` passing
  `--untracked-files=normal` rests on Q3, and the arrival-variant guard rests on Q1.
  If the row is inserted before `corpus/lessons/round-17.md` exists, the registry's
  "mined rows whose used-by paths do not exist" census prints `missing:` — until the lesson
  lands, insert as `queued` with `used-by —` and flip to `mined` when the lesson cites it,
  logging old→new in the round Gate (the only in-place changes the contract allows).
- **r16 open item closed.** S044's `teaches` ends "… exposes a repo-local setting the census
  does not pin (open, r17)". This row closes that item. S044 stays `rejected` for its own
  narrower claim (which config values *abort* a command); this is not a supersede, so no
  `supersedes S044 —` prefix.

## 3. Statements that CONTRADICT the context's claim text

Three, all precision defects in the claim wording rather than in its intent. Each quote is
from the served pages at the lines named above.

**(a) The claim writes `$GIT_DIR/config.worktree` as the locator; the page forbids assuming it.**
> "do not make any assumption about whether a path belongs to $GIT_DIR or $GIT_COMMON_DIR … Use git rev-parse --git-path to get the final path."
> (git-worktree § DETAILS :580-582)

and for a linked worktree the file is
> "the config file .git/worktrees/<id>/config.worktree"
> (:595)

Consequence: a guard that assembles `<git-common-dir>/config.worktree` silently misses a
linked worktree's file; one that assembles `$GIT_DIR/config.worktree` by hand contradicts the
page's explicit rule of thumb. The claim's phrase "`$GIT_DIR/config.worktree`" is defensible
only if `$GIT_DIR` is the value git resolves per worktree — say so, or say
"`git rev-parse --git-path config.worktree`".

**(b) The claim treats `config.worktree` as config unconditionally; the page makes it conditional.**
> "In order to have worktree-specific configuration, you can turn on the worktreeConfig extension"
> (§ CONFIGURATION FILE :540)

> "In this mode, specific configuration stays in the path pointed by git rev-parse --git-path config.worktree."
> (:546)

So a `config.worktree` holding `status.showUntrackedFiles=no` has **no effect** while
`extensions.worktreeConfig` is unset. `[INFERENCE]` — the page never writes "otherwise it is
ignored"; it scopes both statements with "In order to have … you can turn on" and "In this
mode", and Q1 opens with "When `extensions.worktreeConfig` is enabled". The inference is
strong but it is not a located quote, and the row's `teaches` must not be read as one. The
claim's "config.worktree … must not yield a false clean row" is therefore true only in the
enabled case, or as a deliberately conservative presence-based refusal. Either way the diagnostic must say which case it is, or the operator
cannot tell a real hazard from an inert file.

**(c) The extension has a version fence the claim does not mention.**
> "Older Git versions will refuse to access repositories with this extension."
> (§ CONFIGURATION FILE :547-548)

Any r17 fixture that turns `extensions.worktreeConfig` on becomes unreadable to old git; a
fixture that asserts the census handles such a repo must state the minimum git it assumes.

**Not a contradiction — disclosure for C3 only.** git-worktree `§ BUGS` :740-742 says
"Multiple checkout in general is still experimental, and the support for submodules is
incomplete." Nothing in the D1 claim text contradicts this; it is a standing caveat on
treating linked worktrees as an ordinary supported domain, and belongs in C3's disclosure,
not in C1's.

**Checked and not found:** neither page says anything that contradicts `include.path`
insertion taking effect at the directive, nor that limits the override to `git status` (Q3
names `git-commit` too, which matters because a census that reads `git commit --porcelain`
would face the same arrival).

## 4. Smallest fix for C1/D1 (advisory)

1. Keep `count_dirty`'s explicit `--untracked-files=normal`: Q3 states the override verbatim,
   Q4 states that `normal` is the directory-collapse mode. No inference needed.
2. In `guard_git_files`, resolve the worktree config through
   `git rev-parse --git-path config.worktree` (Q5), not a hand-built `$GIT_DIR` or common-dir
   path; that single change covers main and linked worktrees and is the page's own rule.
3. Emit the `error` row on the file's **presence** (conservative, satisfies "never a false
   clean row"), and put the extension state in the diagnostic: `git-metadata-unsupported
   config.worktree <path> extensions.worktreeConfig=on|off`. Off means the file is inert
   today but live the moment the extension is turned on; on means the row would have been
   falsely clean. Same stderr shape as the D2 diagnostic, so the two stay parseable together.
4. Included files need no new probe: Q2 makes an included key indistinguishable from a
   directive-local one, so guarding the repository config file already covers
   `include.path` arrivals. Only `--file`-less config reads of *other* scopes (global,
   system) remain out of reach, and those are not repo-local controls.

## 5. Exact commands run and their outputs

No lane file was written except this report. No `git`, `jj`, shell script, tool, fixture, or
`/var/tmp` directory was created or run — this was a reading seat.

| action | target | output observed |
|---|---|---|
| `read` | `https://git-scm.com/docs/git-worktree` | served; header "git-worktree last updated in 2.56.0"; version list "2.55.0 no changes" |
| `read` | `https://git-scm.com/docs/git-config` | served; header "git-config last updated in 2.56.0" |
| `read` | `https://git-scm.com/docs/git-config/2.55.0` | served; selector "Version 2.55.0"; Includes and § status.showUntrackedFiles text identical to live page |
| `read` | `https://git-scm.com/docs/git-status/2.55.0` | HTTP redirect stub to `https://git-scm.com/docs/git-status/2.53.0` ("Redirecting…") |
| `read` | `https://git-scm.com/docs/git-status/2.53.0` | served; "git-status last updated in 2.53.0"; "2.54.0 → 2.56.0 no changes" |
| `grep` | reader artifacts for the two pinned pages | located § Includes :1062, § CONFIGURATION FILE :988/:533, § DETAILS :564, § BUGS :738, § status.showUntrackedFiles :7932/:8151 |

Tool installs: **none** — nothing was installed or upgraded, so there is no tool/version/
channel record to add.

The git-status read is recorded because it settles a neighbouring question (below) and it
confirms the redirect target S044 used; it grounds no row of its own.

## 6. Remaining unknowns

1. **`git commit` arrival.** Q3 names `git-commit[1]` alongside `git-status[1]`, so an
   explicit `-u` is required there too. I did not open git-commit(1); if `count_dirty` ever
   reads commit output, that page needs the same check. One grep, unopened.
2. **Extension state in non-repo configs.** Whether a global `extensions.worktreeConfig=true`
   enables the file for every repository is not stated on either page. I did not open
   gitrepository-layout(5) (S033) for it; it affects only the diagnostic wording in fix (3).
3. **Command-line `--no-optional-locks` interaction** with a worktree config read is not
   stated on these pages; S036's scope already excludes it, so no new row is implied.
4. **Runtime proof.** Every statement above is documentation, not an exercised gate run.
   Nothing here shows that a specific census revision actually emits the error row.

## 7. Copy-ready Gate and Search-log records

`## Gate` row material (contract rule 1: URL, access date, ≤25-word quote with location):

- S051 — `https://git-scm.com/docs/git-worktree` and `https://git-scm.com/docs/git-config`
  (pinned `/docs/git-config/2.55.0`), opened **2026-10-20**. Quote: "When
  extensions.worktreeConfig is enabled, the config file .git/worktrees/<id>/config.worktree
  is read after .git/config is." — § DETAILS :595. Corroborating quote: "This variable can be
  overridden with the -u|--untracked-files option of git-status[1] and git-commit[1]." —
  § status.showUntrackedFiles :7965-7966. Includes overlap with S042 recorded, not re-counted.

`## Search log` bullet (rule 5 shape: question, where, date, counts, exclusions, stop):

- **Round-17 config arrival variants (2026-10-20).** Question: do git's own docs make
  `config.worktree` and `include.path` repository config sources, and do they state that `-u`
  overrides `status.showUntrackedFiles`? Where: the live git-worktree and git-config web
  manuals, the 2.55.0-pinned git-config manual (host version), and git-status 2.55.0 →
  2.53.0 canonical to settle the redirect revision. Identified 3 documents, screened 3;
  included 2 in one new row S051; excluded 0 from rows (git-status contributes the redirect
  revision check only). Stop: both arrival variants and the override sentence were located
  with verbatim anchors; no runtime census behaviour was claimed.
