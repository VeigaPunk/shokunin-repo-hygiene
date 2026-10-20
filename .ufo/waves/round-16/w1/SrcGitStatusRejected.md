# SrcGitStatusRejected — R7: curate git-status(1) as a `rejected` registry row

Round 16, W1, scout seat. Axes named: **coverage** (the r15 reject exists only as search-log prose; R7 asks for a registry row) and **calibration** (curated reason must state what the page actually grounds, not a slogan).
Advisory only; SOURCES.md was **not edited** (item forbids it). L1 integrates and renumbers.

## Source record

- URL: https://git-scm.com/docs/git-status
- Access date: **2026-10-20**
- Served version / last-updated line, verbatim from the page header (top of page, "Latest version" selector):
  `git-status last updated in 2.53.0`
  and its own changelog list: `1. 2.54.0 → 2.56.0 no changes`, then `2.53.0 … 2026-02-02`.
- Installed rendering cross-check: `/usr/share/man/man1/git-status.1.gz` (member `git-status.1`) roff header reads `Date: 2026-09-27`, `Source: Git 2.56.0`; `.TH "GIT\-STATUS" "1" "2026\-09\-27" "Git 2\&.56\&.0" "Git Manual"`.
- Cross-check result: the two stability sentences quoted below are **text-identical** in the web rendering (2.53.0 stamp) and the installed 2.56.0 rendering — the promise text did not change 2.53.0 → 2.56.0, matching the page's "no changes" list.

## Quote (porcelain stability, 16 words, verbatim)

> guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration

It is the predicate of: `Version 1 porcelain format is similar to the short format, but is guaranteed not to change … This makes it ideal for parsing by scripts.` (`§ OUTPUT › Porcelain Format Version 1`; installed roff line **670**, section header roff **668**.)
The same promise also appears as `--porcelain`: `This is similar to the short output, but will remain stable across Git versions and regardless of user configuration.` (`§ OPTIONS --porcelain`; installed roff line **60**.)

## What the page does and does not ground (observed)

Observed in the same page (`/usr/share/man/man1/git-status.1.gz:git-status.1`, web page as served 2026-10-20):

- Porcelain v1 exceptions are **display-only** config neutralization: `color.status` is `not respected; color will always be off`, and `status.relativePaths` is `not respected; paths shown will always be relative to the repository root` (`§ OUTPUT › Porcelain Format Version 1`, numbered exceptions 1-2).
- `§ CONFIGURATION` documents `color.status`/`status.color`, `status.relativePaths`, `status.submoduleSummary` — all output shaping.
- `§ UNTRACKED FILES AND PERFORMANCE` documents `status.showUntrackedFiles`, `advice.statusUoption`, `core.untrackedCache`, and `core.fsmonitor` (including a `hook-command-pathname`, pointing at git-update-index(1)) — caching/performance.
- `§ BACKGROUND REFRESH` documents an index write on ordinary `git status` and points at `git --no-optional-locks` — already grounded by S006→S036.
- **Not observed anywhere on the page:** which config *values* abort a command, or which values neutralize an execution-affecting setting (the r16 guard's question). The page documents effects on output and on caching, never abort/neutralize semantics.

Calibration consequence: the closure's shorthand "corroborates output format only" is right about the *grounding use* but is literally incomplete — the page also documents performance config (`core.fsmonitor`, untracked cache) and the background index write. The drafted row below keeps the reject and states that precisely, so the curated reason survives a reader who greps the page for `fsmonitor`.

## Proposed registry row (next free number: **S043**; L1 renumbers)

`S042` (corpus/SOURCES.md:54) is the highest committed id; the header at corpus/SOURCES.md:11 fixes the 11 columns; rejected exemplars are corpus/SOURCES.md:42 (S030) and :44 (S032). Proposed S043; `SoujiR16.SrcBashSetN` has since stated the same S043 for GNU Bash Reference Manual § The Set Builtin, so L1 renumbers per the wave contract — this row is position-independent and its cells do not change.

```markdown
| S043 | git-status(1) — https://git-scm.com/docs/git-status | docs | A | porcelain output stability and status display/performance config, not which config values abort or neutralize a command | § OPTIONS --porcelain (installed roff :60); § OUTPUT › Porcelain Format Version 1 (installed roff :668-670); web manual served 2026-10-20, page states "git-status last updated in 2.53.0" and "2.54.0 → 2.56.0 no changes" (2.53.0 dated 2026-02-02); installed /usr/share/man/man1/git-status.1.gz header "Source: Git 2.56.0", Date 2026-09-27 | REJECTED: corroborates porcelain output stability only ("guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration") plus display/performance config (color.status and status.relativePaths not respected; status.showUntrackedFiles, advice.statusUoption, core.untrackedCache, core.fsmonitor) and the background index refresh; it does not say which config values abort a command or neutralize a setting, so it cannot ground the r16 value/effect guard. flip: a revision states per-value execution effects for status config | rejected | 2026-10-20 | on-release | — |
```

Tier rationale: primary git documentation, so tier `A` like the other rejected docs row S032; status `rejected` with `used-by: —` follows S030 (:42) and S032 (:44), which consume no knowledge file. `recheck: on-release` follows S032 — the page is release-versioned and the page itself tracks changes per release.

## Proposed search-log line (round-16 bullet, existing style at corpus/SOURCES.md:63-73)

```markdown
- **Round-16 R7 curation: git-status(1) rejection (2026-10-20).** Question: should the source opened and excluded in round 15 be curated in the registry rather than only in search-log prose? Where: the live page https://git-scm.com/docs/git-status (served "git-status last updated in 2.53.0"; its version list records "2.54.0 → 2.56.0 no changes") and the installed /usr/share/man/man1/git-status.1.gz (roff header "Source: Git 2.56.0", Date 2026-09-27; v1 promise at roff 670, --porcelain sentence at roff 60). Identified 1 document in 2 renderings, screened 1, included 1 rejected row (S043 proposed), excluded 0 new admissions. Stop: the page grounds output stability and display/performance config only; the abort/neutralize value semantics the r16 guard needs are absent, so a rejected row is the correct disposition and no knowledge row is admitted.
```

Search accounting for that bounded set: identified 1 distinct document, screened 1, included 1 registry row (rejected), excluded 0 admissions. Two renderings of one manual page are one row, consistent with the r15 rejection of splitting one document's subsections into separate rows.

## Registry arithmetic (derived, integration remeasures)

From the r15 closure census (corpus/lessons/round-15-verifier-spotcheck.md:87-88): 42 rows, `{'A': 38, 'B': 3, 'C': 1}`, `{'mined': 25, 'queued': 15, 'rejected': 2}`. Adding this one rejected A row gives **43 rows, A39/B3/C1, mined 25 / queued 15 / rejected 3** (my row only; the confirmed `SoujiR16.SrcBashSetN` row shifts these counts again and is L1's remeasure). These are registry counts only, not knowledge expansion — R7 itself is curation, so the expansion trend stays `unchanged`.

## Remaining unknowns

- The web page's last-updated stamp is 2.53.0 while the installed man page renders 2.56.0; both carry identical stability sentences, so the reject does not depend on resolving which build served the page. Unresolved: whether the host `git` binary is also 2.56.0 — S042 (:54) records 2.55.0, this installed man page says 2.56.0. Out of scope for R7; flagged in STATUS for L1.
- The page does not document abort/neutralize semantics at all, so no revision currently exists to flip the reject on this page alone; the flip condition is a future revision that adds them.

## Verdict

R7 is dischargeable by pasting the one row above (plus the search-log line). The draft uses the exact 11-column shape of corpus/SOURCES.md:11, the next free id S043, access date 2026-10-20, served version line, a 16-word stability quote, and tier/status/recheck/used-by cells consistent with the two existing rejected rows.

STATUS: ok; draft complete; SOURCES.md unmodified and no edit attempted; one observation outside this item: installed `/usr/share/man/man1/git-status.1.gz` header says `Source: Git 2.56.0` (+ `Date: 2026-09-27`) while S042's row cites installed 2.55.0 — L1 may want to record the host git version at round end.

Tool installs/updates by this seat: none.

## Commands

none
