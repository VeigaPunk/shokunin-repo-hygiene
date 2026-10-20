# SrcGitNoLazyFetch — git(1) GIT_NO_LAZY_FETCH (round 16, W1 scout)

Seat: `SoujiR16.SrcGitNoLazyFetch`. Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`. Axes: coverage, calibration.
`corpus/SOURCES.md` was read, not edited. No behavioural probe was run (Q24/R5).

## Access record

- Opened `https://git-scm.com/docs/git` on **2026-10-20**. Served version line, verbatim: `git last updated in 2.56.0`; the version selector lists `2.56.0 … 2026-09-28` as the latest entry. Retrieved rendering: 2238 lines.
- Installed copy cross-check: `/usr/share/man/man1/git.1.gz` declares `.\"    Source: Git 2.56.0`, `.\"      Date: 2026-09-27`, `.TH "GIT" "1" "2026-09-27" "Git 2\&.56\&.0"` (roff lines 6, 7, 10). Same header on `git-config.1.gz` and `git-status.1.gz` (roff line 7 each).
- This is a git-scm.com docs page, so the served version is the documentation version; no separate "page last reviewed" stamp exists.

## Located quotes (≤25 words each)

1. **Environment variable** — 21 words, web lines 1992-1996; installed roff 2127-2130:
   > Setting this Boolean environment variable to true tells Git not to lazily fetch missing objects from the promisor remote on demand.
2. **Option** — 11 words, web lines 460-465; installed roff 272-283:
   > Do not fetch missing objects from the promisor remote on demand.
3. **Equivalence** — 11 words, same block:
   > This is equivalent to setting the `GIT_NO_LAZY_FETCH` environment variable to `1`.

Documented use (web lines 462-464, roff 274-279): pairing the switch with `git cat-file -e <object>` "to see if the object is locally available".

## Proposed row (one new row; provisional id)

Numbering: the highest id in `corpus/SOURCES.md` is **S042**; round 15's draft rows S043–S047 were explicitly *not* admitted (`corpus/lessons/round-15.md:27-29`: "research advice, not six admitted registry rows"). So **S043** is the next free id. Every round-16 scout was given the same "S043 onward" instruction, so this id is provisional and will collide; **L1 should allocate a distinct number per scout** (e.g. seat order from S043). I use S043 below.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S043 | git(1) — https://git-scm.com/docs/git | docs | A | GIT_NO_LAZY_FETCH and --no-lazy-fetch: suppression of on-demand promisor fetch only, its Boolean value semantics, and the documented cat-file -e locality idiom; no statement about explicit fetch or completeness | § OPTIONS --no-lazy-fetch (web 460-465); § ENVIRONMENT VARIABLES GIT_NO_LAZY_FETCH (web 1992-1996); installed git(1) /usr/share/man/man1/git.1.gz "Source: Git 2.56.0" dated 2026-09-27, roff 272-283 and 2127-2130; web manual "last updated in 2.56.0", opened 2026-10-20 | a true Boolean GIT_NO_LAZY_FETCH tells Git not to lazily fetch missing objects from a promisor remote on demand; --no-lazy-fetch equals =1 and is documented for testing local availability with cat-file -e; the text is silent on explicit fetch commands and on object completeness, so it bounds lazy fetch, not network I/O generally | queued | 2026-10-20 | on-release | — |

Status/recheck reasoning: `queued` + `—` because no `corpus/knowledge/` or `corpus/lessons/` file cites this id yet (`mined` with `—` raises W03, per the round-15 draft's note). **Flip condition:** if L1 adds S043 to `corpus/knowledge/git-repo-structure-readonly.md:1` while making the doc edits in F2 below, set status `mined` and used-by `corpus/knowledge/git-repo-structure-readonly.md`. `on-release` matches S036/S042 (docs page version is release-coupled; served version did not move this round).

## Scope: why this is not a duplicate of S036

S036's own scope cell reads "optional lock suppression only, **not mandatory writes or lazy fetching**". The new evidence is the mechanism S036 disclaims: a different variable (`GIT_NO_LAZY_FETCH`), a different option (`--no-lazy-fetch`), and a different consumer line (`tools/souji-census.sh:147` for the env var vs `:142` for `GIT_OPTIONAL_LOCKS`). A new row is therefore warranted under the item's own carve-out ("unless scope differs"), and it is what makes the existing knowledge-doc claim sourceable (F2).

## S036 recheck/used-by update proposal

| cell | current | proposed |
|---|---|---|
| scope | optional lock suppression only, not mandatory writes or lazy fetching | **unchanged** — still correct and still the reason S043 is separate |
| anchor | "Git 2.56.0 web manual as opened 2026-10-20; installed 2.55.0 git(1) OPTIONS no-optional-locks, ENVIRONMENT VARIABLES GIT_OPTIONAL_LOCKS, roff 285-291,2195-2201" | **version label is wrong today**: the installed `/usr/share/man/man1/git.1.gz` declares `Source: Git 2.56.0` (roff 6-7, `.TH` roff 10). Locators: `--no-optional-locks` begins at roff 285, matching S036's 285-291 exactly; the `GIT_OPTIONAL_LOCKS` heading sits at roff 2200, inside S036's 2195-2201 span but with the span start ~5 lines early. So the `2.55.0` label is the substantive error; the env locator is imprecise but contains the heading |
| teaches | suppresses optional lock-taking suboperations … does not forbid mandatory writes or object fetching | **unchanged** — the installed 2.56.0 text still says "without performing any optional sub-operations that require taking a lock" (roff ~2202) and defaults to `1` |
| status | mined | **unchanged** |
| recheck | on-release | **unchanged** — no release drift: served page is 2.56.0, the same version S036 already cites |
| used-by | corpus/knowledge/git-repo-structure-readonly.md | **unchanged** — the path is valid. Do not add S043 here; the lazy-fetch claim belongs to S043 |

Recording method: use a **Round-16 provenance paragraph** at the top of `corpus/SOURCES.md` (the pattern at lines 5-7 for rounds 13/14), not an in-place rewrite of a mined row. Suggested text:

> Round-16 provenance: S043 is opened this round on 2026-10-20 (git(1) GIT_NO_LAZY_FETCH). S036's anchor label "installed 2.55.0" is corrected to 2.56.0: the installed git(1) at /usr/share/man/man1/git.1.gz declares Source: Git 2.56.0 (2026-09-27), and the cited option locator matches that page. S036's scope, teaches, status and used-by are unchanged; no other historical cell was rewritten.

A correction *row* (the r14 S038 pattern) is not recommended here: no claim changed, only a version label, and `corpus/lessons/round-15.md:29` warns that "source rows alone are not knowledge growth".

## Calibration findings

- **F1 (high) — host documentation version is 2.56.0, not 2.55.0.** Three installed pages sampled (`git.1.gz`, `git-config.1.gz`, `git-status.1.gz`) all declare `Source: Git 2.56.0`, `.TH` date 2026-09-27. Yet `S036.anchor` says "installed 2.55.0", and `corpus/knowledge/git-repo-structure-readonly.md:2` says `host Git 2.55.0 (package 2.55.0-1), web docs 2.56.0`; `corpus/lessons/round-15.md:22` also claims a "corresponding installed Git 2.55.0 manual" for S042. Under Q1 every affected claim must name the host version it was re-run on, so those labels are unreproducible as written. Not established here: whether the package was upgraded within the last hours or the labels were assumed from earlier rounds; the git **binary** version was not probed (probe rule), and `/usr/local/share/man/man1/git.1.gz` does not exist, so no shadow copy explains it. `[INFERENCE]` On Arch the man pages ship in the `git` package, so the package is likely 2.56.0 — this is inference, not observed.
- **F2 (high) — existing knowledge claim is over-attributed; S043 closes it.** `corpus/knowledge/git-repo-structure-readonly.md:1` lists sources `S035, S036, S037` for a body that at line 11 says the probe "suppresses optional locks **and lazy fetching**" and at lines 33-34 relies on "lazy fetch disabled". S036's scope explicitly excludes lazy fetching and no row covered it before this proposal. L1 edit: append S043 to the doc's `source:` line and keep the sentence; the doc's `verified-at` host-version label also needs F1's correction.
- **F3 (medium) — the guard's phrase is stronger than the doc's promise.** `tools/souji-census.sh:644` says `remote.*.promisor`, `remote.*.partialCloneFilter` and `extensions.partialClone` "cannot fetch under GIT_NO_LAZY_FETCH=1"; git(1) says the variable tells Git "not to lazily fetch missing objects … on demand". Documented policy ("will not lazily fetch") is not a proof of impossibility for every fetch path. C1's "promisor/partialClone are inert" should be carried by the gate's measured behaviour plus the existing status skip, not by this comment's wording. Advisory, not a claim that the guard is wrong.
- **F4 (medium) — the documented idiom is narrower than the census use.** git(1) recommends the switch specifically with `git cat-file -e <object>` to test *local* availability (web 462-464). The census never runs `cat-file -e`; it runs `status`/`rev-parse`/`config` under the exported variable. The row therefore supports "no lazy fetch by census commands", not "the census tests object locality". Do not cite S043 for a locality test.
- **F5 (low) — no release drift this round.** Served page is 2.56.0, identical to S036's existing web anchor, so `on-release` needs no interval change and S043 joins the existing duplicate-URL pair (S006, S036) with a different scope (validator W04 watches duplicate URLs across scopes).
- **F6 (low) — version evidence is man-page headers only.** `/usr/share/doc/git/RelNotes/2.56.0.txt` and `.../2.55.0.txt` are both absent on this host, so the introduction release of `GIT_NO_LAZY_FETCH` was not determined; the row's scope does not claim one.

## Remaining unknowns

- Installed git **binary** version (not probed; the probe rule permits reads, `bash -n`, `shellcheck`, `py_compile`, `git -C … show|log|diff|cat-file|ls-tree|rev-parse`, not `git --version`). Only documentation version is observed.
- Release that introduced `GIT_NO_LAZY_FETCH` / `--no-lazy-fetch` (no RelNotes on the host; not opened upstream).
- Whether S036's `2.55.0` label is upgrade drift or a transcription assumption; unreachable without a host-history probe this seat may not run.

STATUS: no behavioural probe was executed (Q24/R5-compliant); the git binary version is unverified and the 2.55.0→2.56.0 installed-docs discrepancy is reported, not resolved.

## Commands

none
