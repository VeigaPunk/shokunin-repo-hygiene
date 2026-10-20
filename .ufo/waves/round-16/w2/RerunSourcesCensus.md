# RerunSourcesCensus — wave-2 falsification of the round-16 SOURCES census

Seat: `SoujiR16.RerunSourcesCensus-4`. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Assignment: run the ALLOWED-EXEC validator, report every line and exit code, and name the
E11 rows the validator would emit until `corpus/lessons/round-16.md` exists.

## Binding and the moving target

- Review started at lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae` with
  `corpus/SOURCES.md` modified (S042 used-by edit + rows S043–S050) and
  `corpus/lessons/round-16.md` untracked.
- L1 landed `163158a706352f1c0ee3521c4da2e5289970db57` mid-review
  ("round-16: lesson, sources S043-S050, Q25/Q26, …"). That commit contains both files.
- The bytes I validated are byte-identical to the landed commit, so the result below binds
  to `163158a` as well as to the pre-landing worktree:
  - `corpus/SOURCES.md` = `f257941874ffce9d0837b942b2b07282a0e317bdf3b6bd932ede070975413319`
    (worktree and `163158a:corpus/SOURCES.md`);
  - `corpus/lessons/round-16.md` = `33058396af5246c0a21326d9b155c65b693ee027ad8e48bc89039060f946d5a9`
    (worktree and `163158a:corpus/lessons/round-16.md`; `git cat-file -e` rc 0).
- Pre-landing HEAD bytes: `a6ec781:corpus/SOURCES.md` =
  `5185720f8dfd1a9a5e69143e61d1dfe99c3116adc058c7c6768a1217999662d`, which is the
  `5185720f…` "Start" hash recorded in `corpus/lessons/round-16.md` Gate.

## Validator runs (every line, verbatim)

Command (both runs):
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`

Run 1 — pre-landing worktree (`a6ec781` + uncommitted rows):

```
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S049 duplicate url git-scm.com/docs/git across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```

Run 2 — after `163158a`, working tree clean for that file:

```
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S049 duplicate url git-scm.com/docs/git across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```

There is no E-coded line in either run. Verdict: **holds** — the validator is clean at both
snapshots. W04 is warning-only by construction: only `\tE[0-9]+\t` sets `findings`
(`scripts/sources-census.sh:739-741`); all `[EW]` lines are printed (`:742-744`); `ok` is
emitted when no E line was seen (`:745`); exit 1 follows only from `findings`
(`:805`), and exit 2 only from a missing SOURCES in a non-census mode (`:804`).

## E11 — none, and the rows it would name

E11 is `used-by path missing on disk` for `status=mined` rows
(`scripts/sources-census.sh:538-570`; emit at `:567`, test `[ ! -e "$dir/$path" ]` at `:566`;
invoked only in `validate` at `:721`). It checks the filesystem, not git.

- No E11 line appeared because `corpus/lessons/round-16.md` exists on disk: untracked at
  run 1, tracked at run 2. The assignment's expected E11 window closes the moment that file
  exists, and it existed for the whole review.
- If the lesson file were absent, the validator would emit seven E11 lines (and exit 1,
  `:739-741`, `:805`), naming exactly these rows from `corpus/SOURCES.md`:

```
souji	E11	S042 missing used-by corpus/lessons/round-16.md
souji	E11	S043 missing used-by corpus/lessons/round-16.md
souji	E11	S045 missing used-by corpus/lessons/round-16.md
souji	E11	S046 missing used-by corpus/lessons/round-16.md
souji	E11	S047 missing used-by corpus/lessons/round-16.md
souji	E11	S049 missing used-by corpus/lessons/round-16.md
souji	E11	S050 missing used-by corpus/lessons/round-16.md
```

  Rows: S042 `corpus/SOURCES.md:56`, S043 `:57`, S045 `:59`, S046 `:60`, S047 `:61`,
  S049 `:63`, S050 `:64`. S044 `:58` and S048 `:62` are `rejected`, so E11 skips them.
  S042 is included because its used-by cell now carries two paths, one of them the r16
  lesson (`:56`).

Verdict: **holds** — no E11 in either run; the hypothetical set is derived from the
validator's own loop and the registry, not by deleting the file (lane mutation is forbidden).

## W04 — four warnings, all justified

| line | duplicate of | scope difference | supersession marker |
|---|---|---|---|
| S035 `:49` | S005 `:19` (git-repo) | S005 "output and format stability" vs S035 "documented structure formats, not a universal read-only guarantee" | S035 teaches "supersedes S005" (`:49`) |
| S036 `:50` | S006 `:20` (git) | S006 "GIT_OPTIONAL_LOCKS" vs S036 "optional lock suppression only, not mandatory writes or lazy fetching" | S036 teaches "supersedes S006" (`:50`) |
| S038 `:52` | S034 `:48` (timeout) | S034 "exit codes and secondary kill" vs S038 "corrected installed-vendor timeout quote and exit-status locations" | S038 teaches "supersedes S034" (`:52`) |
| S049 `:63` | S036 `:50` (git) | S036 excludes lazy fetching; S049 is exactly `GIT_NO_LAZY_FETCH` suppression | documented in the provenance note (`:9`) and lesson Gate (`corpus/lessons/round-16.md:32`) |

The first three are pre-existing and unchanged; only the S049 warning is new, and the lane
declared it in `corpus/SOURCES.md:9` before the run. Verdict: **holds** — four W04 lines,
zero E lines, exit 0.

## S043–S050 Gate provenance — every quote located

All eight Gate bullets (`corpus/lessons/round-16.md:26-33`) were checked against a primary
copy; word count 6–22 each, all ≤25. Verdict: **holds** for all eight.

| row | claimed anchor | verified location (verbatim match) |
|---|---|---|
| S043 `:57` | installed `bash(1)` GNU Bash 5.3 roff 11466-11469 | `/usr/share/man/man1/bash.1.gz` member `bash.1` roff 11466-11469: `.B \-n` / "Read commands but do not execute them." / "This may be used to check a shell script for syntax errors." / "This is ignored by interactive shells."; installed `bash-5.3.20-1` (`/var/lib/pacman/local/bash-5.3.20-1`) |
| S044 `:58` | web manual "last updated in 2.53.0"; § OUTPUT Porcelain Format Version 1 | live `git-scm.com/docs/git-status`: version line at rendered 157, "2.54.0 → 2.56.0 no changes" at 159, quote at 534-536 |
| S045 `:59` | web manual "last updated in 2.56.0"; § Effects, filter | live `gitattributes`: version at 150, quote at 847-849; installed `gitattributes.5` roff 826 |
| S046 `:60` | web manual "last updated in 2.52.0", "2.53.0 → 2.56.0 no changes"; § OUTPUT, § OPTIONS -z | live `git-check-attr` version lines 186, 189; installed `git-check-attr.1` roff 85 (`<path> NUL <attribute> NUL <info> NUL`) |
| S047 `:61` | web manual "last updated in 2.55.0", "2.56.0 no changes"; § DESCRIPTION core.excludesFile | live `gitignore` version lines 157, 159; installed `gitignore.5` roff 132 |
| S048 `:62` | served without version line | live `shellcheck.net/wiki/SC1046` title line 3 and heading line 14 |
| S049 `:63` | web manual "last updated in 2.56.0"; § ENVIRONMENT VARIABLES GIT_NO_LAZY_FETCH; installed git(1) 2.56.0 | live `git` version at 157; installed `git.1` roff 2129; installed package `git-2.56.0-1` |
| S050 `:64` | Python 3.15.0 docs; § Built-in Functions compile | live `docs.python.org/3/library/functions.html` lines 278-279; page carries "Changed in version 3.15" at 314 |

Minor precision note (low): the S045 anchor says "§ Effects, filter", but the quoted
sentence is one subsection later — "§ EFFECTS › Checking-out and checking-in › Interaction
between checkin/checkout attributes" (live 845-849; installed roff 823-828). The `filter`
subsection independently supports the teaches cell ("the `clean` command is used to convert
the contents of worktree file upon checkin", live 585-586; installed roff 545), so the
substance holds. Smallest fix: widen the cell to `§ Effects, filter / Interaction between
checkin/checkout attributes`.

## Registry delta and Start hash

- Pre-landing diff (HEAD `a6ec781` → worktree) touched only: the round-16 provenance
  paragraph + blank line (`corpus/SOURCES.md:9`), the S042 row's used-by cell
  (`corpus/lessons/round-15.md` → `corpus/lessons/round-15.md, corpus/lessons/round-16.md`),
  the eight S043–S050 rows, and one Search-log entry (round-16). No other status, recheck or
  used-by cell changed, matching the lesson's claim at `corpus/lessons/round-16.md:35`.
- The lesson's Start hash `5185720f…` equals `a6ec781:corpus/SOURCES.md`; the S049 W04 is the
  only warning added by the edit (3 → 4). Verdict: **holds**.

## Context check: the installed git manual moved today

The apparent S036 ("installed 2.55.0") vs S049 ("installed git(1) 2.56.0") conflict is a host
upgrade, not a registry error: `/var/lib/pacman/local/git-2.56.0-1/desc` gives INSTALLDATE
`1792498597` = 2026-10-20 12:16:37 UTC, and `/usr/share/man/man1/git.1.gz` is `Git 2.56.0`.
S036's cited ranges still resolve on the 2.56.0 page (`--no-optional-locks` 285-291;
`GIT_OPTIONAL_LOCKS` header at 2200), so the historical row is internally consistent; its
version label is host-state dependent. No r16 action; noted so a later audit does not
"correct" S036 by today's package state.

## Residual risk and verification gaps

- I did not run `curl`; the S043 "live page unreachable (curl exit 28)" claim is unverified.
  The quote itself is verified against the installed `bash(1)` 5.3.20 (the L1 anchor).
- The Wayback capture `20260930073822` was not opened.
- Live pages were read at review time, not at the seats' opening instant; the version stamps
  (2.52.0/2.53.0/2.55.0/2.56.0) bound drift but do not exclude same-day edits.
- "host Python 3.14" (S050 anchor) is unverified: the probe whitelist allows only
  `python3 -m py_compile`, which does not report the version.
- The E11 hypothetical set is code-derived; I did not delete or rename the lesson to exercise
  it (lane writes are forbidden outside this report).
- The Start run (3 W04, exit 0) is inferred from the HEAD hash plus the absence of S049 in
  `a6ec781`; I did not materialize `a6ec781` bytes to rerun it.

STATUS: ok

## Commands

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji; echo "EXIT=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain | head -50 && echo "---SOURCES S043-S050---" && grep -n "S04[3-9]\|S050" corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin && wc -l scripts/sources-census.sh && grep -n "E11\|E1[0-9]\|W04\|lessons" scripts/sources-census.sh | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l corpus/SOURCES.md corpus/lessons/round-16.md && echo "---GATE HEADINGS---" && grep -n "^#\|^##" corpus/lessons/round-16.md | head -40 && echo "---GIT DIRTY CHECK---" && git log --oneline -3 && git show --stat HEAD | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "---HEAD S042/S043---" && git show HEAD:corpus/SOURCES.md | grep -n "^| S04[0-9]" | cut -c1-260 && echo "---HEAD round-16 provenance---" && git show HEAD:corpus/SOURCES.md | grep -cn "round-16" ; echo "---worktree refs to round-16.md---" && grep -n "round-16.md" corpus/SOURCES.md | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat -- corpus/SOURCES.md && git diff -U0 -- corpus/SOURCES.md | grep -E "^[-+]" | grep -vE "^[-+][-+]" | cut -c1-220
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "HEAD_HASH:" && git show HEAD:corpus/SOURCES.md | sha256sum && echo "WT_HASH:" && sha256sum corpus/SOURCES.md corpus/lessons/round-16.md && echo "S042_HEAD:" && git show HEAD:corpus/SOURCES.md | grep "^| S042" | awk -F'|' '{print "usedby=[" $13 "] status=[" $10 "] recheck=[" $12 "]"}' && echo "S042_WT:" && grep "^| S042" corpus/SOURCES.md | awk -F'|' '{print "usedby=[" $13 "] status=[" $10 "] recheck=[" $12 "]"}' 
ls -l /usr/share/man/man1/bash.1.gz /usr/share/man/man1/git.1.gz 2>&1; file /usr/share/man/man1/bash.1.gz /usr/share/man/man1/git.1.gz 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff -U0 -- corpus/SOURCES.md | grep -nE "^@@|Round-16 parse|Round-16 provenance" && echo "---NUMSTAT---" && git diff --numstat -- corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain | head -20 && echo "---DIFFSTAT---" && git diff --stat -- corpus/SOURCES.md && echo "---LOG---" && git log --oneline -2
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "---STAT---" && git show --stat --oneline 163158a | head -30 && echo "---COMMITTED LESSON---" && git cat-file -e 163158a:corpus/lessons/round-16.md; echo "lesson_rc=$?" && echo "---HASHES---" && git show 163158a:corpus/SOURCES.md | sha256sum && git show 163158a:corpus/lessons/round-16.md | sha256sum && sha256sum corpus/SOURCES.md corpus/lessons/round-16.md
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji; echo "EXIT=$?"
cd /home/vgpnk/Projects/shokunin && grep -n "usedby_out=\$(usedby_findings\|lane_errors=0\|E\[0-9\]\|lane_errors\" = 1\|findings\" = 1\|missing_error\" = 1" scripts/sources-census.sh
cd /home/vgpnk/Projects/shokunin && grep -n "usedby_findings()\|! -e \"\$dir/\$path\"\|status\" = mined\|status\" != mined" scripts/sources-census.sh
```

Tool-only reads (no shell): `read`/`grep`/`glob` on `corpus/SOURCES.md`,
`corpus/lessons/round-16.md`, `scripts/sources-census.sh`, `tools/souji-seat-audit.py`,
`/usr/share/man/man1/{bash,git}.1.gz`, `/usr/share/man/man{1,5}/git-{check-attr,ignore,attributes}.*.gz`,
`/var/lib/pacman/local/git-2.56.0-1/desc`, and the live pages
`git-scm.com/docs/{gitattributes,git-check-attr,gitignore,git-status,git}`,
`docs.python.org/3/library/functions.html`, `shellcheck.net/wiki/SC1046`.
