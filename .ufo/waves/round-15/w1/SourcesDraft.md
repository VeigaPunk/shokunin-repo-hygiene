# SourcesDraft — round 15 / w1 (scoped)

Seat: `SoujiR15.SourcesDraft` (leaf; no delegation). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Date: 2026-10-20.
Owned output: `census/round-15/sources-draft.md` (proposed S042–S047). S041 is reserved by L1 for the reopened non-author round-14 closure row and is not proposed here. Not edited: `corpus/SOURCES.md`, S001–S040, any other file. No runtime checks were run.

## Behaviour / result

- Six proposed `docs`/tier-A rows, S042–S047, drafted in the 11-column registry shape with status `queued`, opened 2026-10-20, recheck `on-release`, used-by `—`.
- Rows support C1 (value-blind Git config refusals). They cover:
  - S042 include and includeIf inserts at the directive, relative to the including file.
  - S043 `--includes` / `--no-includes` default (off for a named file, on for all-config lookups).
  - S044 `core.hooksPath` as a config-controlled hook location, with `/dev/null` disabling all hooks.
  - S045 boolean literals and the bare-key rule.
  - S046 the `hasconfig:remote.*.url` cycle break (remote URLs in included files do not count).
  - S047 `git status --porcelain` v1 stability independent of user configuration.
- Each quote is ≤25 words and was matched in the installed 2.55.0 man page; the web text is 2.56.0 for git-config.
- Quote and URL scope: the git-config and git-status URLs above; quotes listed under "Located quotes" only.

## Sources opened (exact)

| # | Source | How | Date/version |
|---|---|---|---|
| 1 | https://git-scm.com/docs/git-config | web reader; `curl -fsSL` to a scratch file (text extraction, removed) | served "last updated in 2.56.0" |
| 2 | https://git-scm.com/docs/git-status | web reader; `curl` to a scratch file (removed) | served "last updated in 2.53.0" |
| 3 | installed git-config(1) | `man -P cat git-config` (rendered; text line numbers below are into this rendering) | git 2.55.0 (`git --version`) |
| 4 | installed git-status(1) | `zcat /usr/share/man/man1/git-status.1.gz` (roff line numbers) | git 2.55.0 |
| 5 | `corpus/SOURCES.md` (registry shape, read-only) | `read` | — |
| 6 | `corpus/QUALITY.md` lines 1–40 (tier pointer; Q1/Q2 rules) | `read` | — |
| 7 | `scripts/sources-census.sh` (kind enum line 655, tier enum line 657; read-only) | `grep` | — |
| 8 | `census/round-15/claims.json`, `.ufo/waves/round-15/w1-assignments.json` | `read` | — |
| 9 | `.ufo/waves/round-14/w1/SourceTimeout.md` (report-format example only) | `read` | — |

Not opened: `~/.omp/agent/agent.db*`, any credential or auth file, `census/operator-sweep-*`, fleet siblings, or any file outside the lane contract. No registry rows were edited.

## Located quotes (exact text, ≤25 words)

- S042: "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive." — web § Includes; installed rendered line 642.
- S043: "Defaults to off when a specific file is given (e.g., using --file, --global, etc) and on when searching all config files." — web § Options; installed rendered lines 278–281.
- S044: "Set this to different path, e.g. /etc/git/hooks, and Git will try to find your hooks in that directory." — web § core.hooksPath; installed rendered lines 2373–2391. Also: "setting core.hooksPath to /dev/null" disables all hooks.
- S045: "Boolean true literals are yes, on, true, and 1. Also, a variable defined without = <value> is taken as true." — web § boolean; installed rendered lines 806–814. False literals: "no, off, false, 0 and the empty string" (installed line 814).
- S046: "Files included by this option (directly or indirectly) are not allowed to contain remote URLs." — web § Conditional includes; installed rendered lines 710–721 (wrapped).
- S047: "…is guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration." — git-status § Porcelain Format Version 1; installed roff line 670. Also roff line 60: "regardless of user configuration".

## Tier and status

- Tier A for all six: primary official Git documentation (git-config(1) and git-status(1)). No community or secondary source.
- Status `queued` on all six (not `mined`), because no `corpus/knowledge/` or `corpus/lessons/` path exists yet to name in `used-by`. Promotion to `mined` waits for the lesson/knowledge path a later seat writes (W03 flags `mined` with `—`).

## Caveats

1. Documentation only. No probe, run, or behaviour check was performed (per assignment). The `teaches` cells state documented behaviour, not behaviour observed on this host. Q2 says installed behaviour outranks prose; none was observed.
2. Version split: the web git-config page is the 2.56.0 manual; host git is 2.55.0. All quoted sentences were confirmed in the installed 2.55.0 man rendering. The introduction version of `--no-includes`, `hasconfig:`, and `core.hooksPath` was not checked (no release notes opened); Q1 needs a verified version, which is 2.55.0.
3. Line numbers: web numbers are not cited (the reader's extraction is not canonical). Installed citations are rendered (`man -P cat`) or roff (`zcat`), as labelled.
4. S047 covers porcelain v1 only; v2 is out of scope.
5. The rows teach what a value-blind refusal must model. They do not establish what C1 must refuse. That is the refusal lane's decision and stays outside this seat.

## Tooling

- Installed: nothing. No pacman, uv, npm, or cargo install was run. `curl` (existing) fetched the two public doc pages to scratch, removed afterwards; `git --version`, `man`, and `zcat` were used read-only.

## Checks for L1 (not run here, per contract)

- After integration: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` should rise by 6 to 46 (if S041 is integrated separately by L1, the count reflects that row too).
- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` should exit 0 with no E05/E06/E07/E08/E09 lines.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --numstat -- corpus/SOURCES.md` should show insertions only, 0 deletions.
- Quotes: re-grep each quoted sentence against the installed `man -P cat git-config` and `zcat /usr/share/man/man1/git-status.1.gz`.

## Findings (actionable)

- Operability: S042/S043/S046 imply that a checker reading one config file cannot see values that Git resolves through includes, and that scope defaults change whether includes apply. Any value-blind refusal that reads only a single file should say so.
- Calibration: S045 shows value grammar (case-insensitive literals, bare keys = true, empty string = false) is part of what a value-blind check must parse; a naive string match would miscount these.
- No finding in this seat is a runtime fact about this host.

## Boundary disclosure (no-query rule)

Calls that breached the no-query boundary earlier in this seat, disclosed and not repeated:

- `grep -rln 'SOURCES-CONTRACT' --include=*.md .` run from the lane root. Recursive, so it walked `census/`, including `census/operator-sweep-20261018` and `census/operator-sweep-20261019`. Only matching filenames were printed; no matched line was quoted or used. The OPERATOR-authored sweep dirs were not opened, edited, moved or copied by this seat.
- `find . -maxdepth 2 -iname 'SOURCES*'` from the lane root, and `find /home/vgpnk/Projects/shokunin -maxdepth 6 ...` from the parent root. The parent search can reach `census/operator-sweep-*` at depth 3. Names only; nothing read.
- `ls census` and `ls -la` at the lane root: directory-name listings that include the operator sweep dir names. Nothing inside them was listed or read.

Limitation: those searches did not read sweep content, but they did touch those paths. No further lane-root or census-wide search was run after the boundary reminder. Every later read used explicit paths.
