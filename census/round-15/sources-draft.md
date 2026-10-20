# sources-draft — round 15 (proposed rows, not admitted)

Lane: `souji`. Seat: `SoujiR15.SourcesDraft`. Opened 2026-10-20. Scope: git-config(1) and git-status(1) primary docs, for C1 operability (value-blind Git config refusals). Not an admission. `corpus/SOURCES.md` is untouched; S001–S040 are unchanged. S041 is reserved by L1 for the reopened non-author round-14 closure row, so this draft starts at S042. L1 integrates these rows after review.

Row shape is the 11-column registry in `corpus/SOURCES.md` (`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`). Kind `docs` and tier `A` are valid per `scripts/sources-census.sh` (kind enum line 655; tier enum `^[ABC]$`). `status` is `queued` on every row: no `corpus/knowledge/` or `corpus/lessons/` path exists yet to name in `used-by`, and `mined` with `—` raises W03.

## Proposed rows

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S042 | git-config(1) — https://git-scm.com/docs/git-config | docs | A | include.path and includeIf.<condition>.path: included contents take effect at the directive; relative paths resolve against the including file | § Includes; installed git 2.55.0 git-config(1) § Includes, rendered text line 642 (man -P cat); web manual served with "last updated in 2.56.0" | "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive." Relative include paths resolve against the file containing the directive. | queued | 2026-10-20 | on-release | — |
| S043 | git-config(1) — https://git-scm.com/docs/git-config | docs | A | --includes and --no-includes default: off for a named file or scope, on for an all-config lookup | § Options, --includes/--no-includes; installed 2.55.0 rendered text lines 278-281 | "Defaults to off when a specific file is given (e.g., using --file, --global, etc) and on when searching all config files." | queued | 2026-10-20 | on-release | — |
| S044 | git-config(1) — https://git-scm.com/docs/git-config | docs | A | core.hooksPath: hook directory is a config value; /dev/null disables all hooks | § core.hooksPath; installed 2.55.0 rendered text lines 2373-2391 | "Set this to different path, e.g. /etc/git/hooks, and Git will try to find your hooks in that directory." Setting core.hooksPath to /dev/null disables all hooks. | queued | 2026-10-20 | on-release | — |
| S045 | git-config(1) — https://git-scm.com/docs/git-config | docs | A | boolean literals and bare-key rule for value parsing | § Values, boolean; installed 2.55.0 rendered text lines 806-814 | "Boolean true literals are yes, on, true, and 1. Also, a variable defined without = <value> is taken as true." False literals are no, off, false, 0 and the empty string; spellings are case-insensitive. | queued | 2026-10-20 | on-release | — |
| S046 | git-config(1) — https://git-scm.com/docs/git-config | docs | A | includeIf hasconfig:remote.*.url: remote URLs in included files cannot satisfy the condition | § Conditional includes, hasconfig; installed 2.55.0 rendered text lines 710-721 | "Files included by this option (directly or indirectly) are not allowed to contain remote URLs." Git breaks the resolution cycle by prohibiting those files from declaring remote URLs. | queued | 2026-10-20 | on-release | — |
| S047 | git-status(1) — https://git-scm.com/docs/git-status | docs | A | porcelain v1 is stable and does not depend on user configuration (color.status and status.relativePaths are not honored) | § --porcelain; § Porcelain Format Version 1; installed 2.55.0 git-status(1) roff lines 60, 670, 682 (zcat man page) | "Version 1 porcelain format ... is guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration." | queued | 2026-10-20 | on-release | — |

## Located quotes (word counts; each ≤ 25 words)

- S042 — "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive." (22 words)
- S043 — "Defaults to off when a specific file is given (e.g., using --file, --global, etc) and on when searching all config files." (21 words)
- S044 — "Set this to different path, e.g. /etc/git/hooks, and Git will try to find your hooks in that directory." (18 words)
- S045 — "Boolean true literals are yes, on, true, and 1. Also, a variable defined without = <value> is taken as true." (20 words)
- S046 — "Files included by this option (directly or indirectly) are not allowed to contain remote URLs." (15 words)
- S047 — "is guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration." (17 words; the subject "Version 1 porcelain format" precedes it in the doc)

## Caveats

- Documentation only. Per the assignment, no probes, runs, or behaviour checks were made. The `teaches` cells state documented behaviour, not behaviour observed on this host (Q2: installed behaviour outranks prose; none was observed here).
- Versions: the web pages served are the 2.56.0 manuals (`last updated in 2.56.0` for git-config; `2.53.0` for git-status). The host runs git 2.55.0; every quote above was also matched in the installed 2.55.0 man page. The version in which `--no-includes`, `hasconfig:`, and `core.hooksPath` were first introduced was not checked (no release notes opened). Q1 needs a verified version; 2.55.0 is the one verified.
- git-status supports S047 only for porcelain v1. The v2 format is out of scope here.
- Tier A is limited to the official Git documentation pages named above. No community or secondary source is proposed.
- These rows teach what a value-blind refusal must model (includes, scope defaults, boolean grammar, hook location). They do not establish what C1 must refuse. That is the refusal lane's decision.
