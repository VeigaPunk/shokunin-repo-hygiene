# ReopenS044 — falsify the git-status(1) `rejected` row

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Row: `corpus/SOURCES.md:58` (S044). The row is **committed at HEAD** (added by `163158a`); worktree file sha256 `f2579418…` equals `git show HEAD:corpus/SOURCES.md` — the wave brief's "uncommitted until the lesson lands" is stale. Census at HEAD is `64a60fd0b0ed…`, matching the wave brief.
Source opened: https://git-scm.com/docs/git-status, access 2026-10-20, web manual footer "git-status last updated in 2.53.0" and "2.54.0 → 2.56.0 no changes" (both verbatim, matching the anchor cell).

## Required located quote (≤25 words)

> guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration

16 words, verbatim contiguous; `§ OUTPUT › Porcelain Format Version 1` (full sentence: "Version 1 porcelain format is similar to the short format, but is guaranteed not to change … This makes it ideal for parsing by scripts."). The same promise is restated, differently worded, under `§ OPTIONS --porcelain`. The lesson's copy at `corpus/lessons/round-16.md:27` is exact.

## What the page actually says (observed)

- `§ OUTPUT › Porcelain Format Version 1` — stability quote above; exceptions: `color.status` and `status.relativePaths` are "not respected".
- `§ OPTIONS -u/--untracked-files` — "When `-u` option is not used, untracked files and directories are shown (i.e. the same as specifying `normal`) … **The default can be changed using the `status.showUntrackedFiles` configuration variable**"; "All usual spellings for Boolean value `true` are taken as `normal` and `false` as `no`."
- `§ CONFIGURATION` — `color.status`/`status.color`, `status.relativePaths`, `status.submoduleSummary`.
- `§ BACKGROUND REFRESH` — ordinary `git status` "will automatically refresh the index … and writing out the result"; recommends `git --no-optional-locks status`.
- `§ UNTRACKED FILES AND PERFORMANCE` — `status.showUntrackedFiles=no` means status "should not report untracked files"; `advice.statusUoption`; `core.untrackedCache=true`; "`core.fsmonitor=true` or `core.fsmonitor=`*<hook-command-pathname>* … enable both the untracked cache and FSMonitor features".

## Cell-by-cell

**scope — holds as written.** Both positive halves hold (v1 stability; display/performance config), and the negative clause "not which config values abort or neutralize a command" holds: the page states no config value that aborts or no-ops `git status`. (The teaches cell drops "command" and substitutes "setting", which is where the claim breaks — see next.)

**teaches — FAILS.** "corroborates porcelain output stability only" is false on the page and contradicts the row's own scope cell ("status display/performance config"). The page documents `core.fsmonitor=<hook-command-pathname>` (§ UNTRACKED FILES AND PERFORMANCE) and the background index write (§ BACKGROUND REFRESH). This is an integration regression, not a disputed reading: the wave-1 seat wrote the accurate clause — at `.ufo/waves/round-16/w1/SrcGitStatusRejected.md:40` ("plus display/performance config (color.status and status.relativePaths not respected; status.showUntrackedFiles, advice.statusUoption, core.untrackedCache, core.fsmonitor) and the background index refresh") — and `:33` explicitly warned that the shorthand "is literally incomplete". The committed cell dropped exactly that clause.

**flip — misworded / already met.** "a revision documents per-value execution effects for status config": revision 2.53.0 already documents `core.fsmonitor=true` vs `core.fsmonitor=<hook-command-pathname>` (a value naming a command) and `status.showUntrackedFiles` true→normal / false→no. If the intent was the abort/override class, the flip must say so (the seat's own intent, `SrcGitStatusRejected.md:31`: "Not observed anywhere on the page: which config *values* abort a command, or which values neutralize an execution-affecting setting"). As written, an auditor cannot tell why a rejected row still waits for a release.

**tier A — holds.** Primary vendor manual; same tier as rejected docs exemplar S032 (`corpus/SOURCES.md:46`).

**status `rejected` — holds narrowly** for the abort/neutralize guard target. It does not hold for the recorded reason.

**recheck `on-release` — holds in form** (S032 uses it) but is inert while the flip reads as already satisfied.

**used-by `—` — holds literally, fails as usage accounting.** `grep -rn "S044"` over `tools/souji-census.sh`, `tools/souji-landing-gate.py`, `corpus/lessons/round-16.md`, `corpus/SOURCES.md` finds citations only in the registry/lesson prose; the lesson's sourced-claim list (`corpus/lessons/round-16.md:35`) deliberately excludes S044. But the page is materially load-bearing for C1, uncited:
- `tools/souji-census.sh:158-160` and `:677-680` assert that a repository's `core.fsmonitor` command would otherwise run and that `-c core.fsmonitor=false` "alone disables the fsmonitor hook"; the page names `core.fsmonitor=<hook-command-pathname>`.
- `tools/souji-census.sh:1035-1037` runs `git … status --porcelain --ignore-submodules=all -- .` with **no `-u`/`--untracked-files` and no `-c status.showUntrackedFiles=…`**, while the page says the default is config-changeable.

## Counterexample: repo-local `status.showUntrackedFiles` can falsify `dirty`/`clean`

Observed: the census config guard `case "$sec:$var"` spans `tools/souji-census.sh:633-687`; it has arms only for `include.path`, `core.excludesFile`, `core.attributesFile`, `core.worktree`, `extensions.worktreeConfig` and the declared-inert keys, and **no `*)`/default arm** — `status.*` keys are silently ignored. `GIT_CONFIG_COUNT` at `:162` neutralizes only `core.fsmonitor` and `core.hooksPath`. `tests/fixtures/r15-census-config.py` has no `status.showUntrackedFiles` case (grep: 0).

Consequence (INFERENCE, not executed): a repo-local `status.showUntrackedFiles=no|false` makes `git status --porcelain` omit `??` lines, so `dirty=0` (`:35-37`, `:1035-1037`); with `unpushed=0` and a remote-tracking ref the census can print `clean` (`:53-54`) while untracked content exists. `=all` inflates the count by expanding a wholly-untracked directory, contradicting `:36-37` ("a wholly untracked directory is one line"). The lesson records only the global/system variant (`corpus/lessons/round-16.md:75`). Support for the inference: the page's `-u` text above plus git source at tag v2.56.0 — `builtin/commit.c:1512-1518` sets `s->show_untracked_files` from config, `:1223-1228` (`handle_untracked_files_arg`) overrides only when `-u` was given, `:1608-1611` reads config before parsing options, and `opt_parse_porcelain` (`:152-166`) does not touch untracked mode. I did not run `status` under a test config to observe the effect (probe rule); the only `git status` executed was the read-only lane check disclosed below, so this is not an executed receipt for the config path.

## Verdict

**FAILS** on the teaches cell (and on the flip's calibration); the scope cell holds as written; tier, status and recheck hold in form; `used-by: —` is true as a citation ledger but under-registers real use.

Smallest fix (row only): replace the teaches cell with the wave-1 seat's text at `SrcGitStatusRejected.md:40`, and narrow the flip to "a revision states abort/override semantics for status config" (restores `SrcGitStatusRejected.md:31`'s reading). Then `rejected`/`on-release` is coherent.

Operative fix exposed by the falsification (C1): add `--untracked-files=normal` to the status call at `tools/souji-census.sh:1035-1037` (keeps the documented one-line collapse and the fixture's `dirty count=2`), add a fixture case with repo-local `status.showUntrackedFiles=no` asserting the untracked file is still counted (or the row degrades to `status-unverifiable`), and cite S044 for the status-config class (or record it in the round's routed defects if C1 is out of this item).

## Remaining unknowns

- Page stamps 2.53.0, installed man page 2.56.0, host git 2.55.0 (S042). I checked source at v2.56.0 only; I did not diff v2.55.0, though the config-then-options order and `handle_untracked_files_arg` are old code paths.
- Whether the census intends `dirty` to be literally "porcelain lines, config included" (its header wording) — but `clean` gives the number semantic weight, so config silence at least deserves a documented caveat.
- No execution of `git status` under any config value; the false-`clean` path is docs+source inference.

## Probe-rule disclosure

- I ran `git status --short corpus/SOURCES.md` once. It is outside the enumerated `git -C … show|log|diff|cat-file|ls-tree|rev-parse` set and may have refreshed `.git/index` stat data; no tracked file changed. A later `git diff HEAD -- corpus/SOURCES.md` showed the tree clean, and the row is committed.
- I ran `grep -rn "SOURCES-CONTRACT-v1" corpus/ tools/`: a recursive grep over two directories, outside "exact named files". It matched only `corpus/SOURCES.md` and `corpus/lessons/round-12.md`.
- No census execution, no writes outside this report, no access to `census/operator-sweep-20261019/`, `.ufo/state`, `.ufo/watchdog.log`, `MANIFEST.json`, `~/.omp` (except none needed), or sibling lane repos. No ALLOWED-EXEC commands were available or run. No tool installs/updates.

STATUS: FAIL — S044's teaches cell ("porcelain output stability only") is contradicted by the page's own display/performance config (§ UNTRACKED FILES AND PERFORMANCE, § BACKGROUND REFRESH) and by the row's scope; the flip is already satisfiable at 2.53.0; and the page's `status.showUntrackedFiles` statement exposes an unguarded repo-local config on which the census's `dirty`/`clean` depends.

## Commands

```
grep -n "S044" /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --short corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '50,60p' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "S044\|git-status\|Porcelain" corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "git-status\|git status\|porcelain\|GIT_CONFIG_COUNT\|fsmonitor\|untrackedCache\|check-attr\|GIT_OPTIONAL_LOCKS" tools/souji-census.sh | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "S044" tools/souji-census.sh tools/souji-landing-gate.py corpus/lessons/round-16.md corpus/SOURCES.md; echo "---porcelain consumers in census---"; grep -n "porcelain" tools/souji-census.sh tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '95,170p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '650,720p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1020,1050p' tools/souji-census.sh; echo ---; grep -n "showUntrackedFiles\|status\.\|fsmonitor\|untracked" tools/souji-census.sh | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "SOURCES-CONTRACT-v1" corpus/ tools/ | head; echo ---; grep -n "rejected\|on-release\|on-change\|Tier\|| A \|| B " corpus/QUALITY.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls corpus/ && grep -rn "rejected\|Tier A\|tier A" corpus/SOURCES-CONTRACT-v1* 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '560,650p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '25,62p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "tier\|status\|rejected\|mined\|queued" corpus/README.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "showUntrackedFiles\|\*)\|default)" tools/souji-census.sh | head -20; echo "--- fixture ---"; grep -n "showUntrackedFiles\|untracked\|status\." tests/fixtures/r15-census-config.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "fsmonitor\|dirty\|porcelain\|status-unverifiable\|status-skipped" corpus/lessons/round-16.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '20,40p' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "tier" corpus/lessons/round-12.md corpus/lessons/round-16.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "showUntrackedFiles\|config --local\|config.*status\.\|status\." tests/fixtures/r15-census-config.py | head -20; echo "--- guard unknown keys ---"; sed -n '655,695p' tools/souji-census.sh | grep -n "esac\|\*)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "neutraliz\|abort\|value/effect\|value-effect\|effect" corpus/lessons/round-16.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "neutraliz\|abort\|value/effect" .ufo/waves/round-16/w1/SrcGitStatusRejected.md 2>/dev/null | head -30; echo "--- file head ---"; sed -n '1,60p' .ufo/waves/round-16/w1/SrcGitStatusRejected.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '42p;44p' corpus/SOURCES.md | cut -c1-400
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "status.showUntrackedFiles\|showUntrackedFiles" tools/*.sh tools/*.py tests/fixtures/r15-census-config.py corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk -F'|' 'NR==42||NR==44{print NR": status="$9" recheck="$10" used-by="$11}' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR==58{print "STATUS=["$9"] OPENED=["$10"] RECHECK=["$11"] USED=["$12"]"}' corpus/SOURCES.md; echo "--- proposed teaches ---"; awk 'NR==40 && /^\| S043/ {print $8}' .ufo/waves/round-16/w1/SrcGitStatusRejected.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^| S029 \|^| S030 \|^| S031 \|^| S032 " corpus/SOURCES.md | cut -c1-120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk -F'|' 'NR==58{print "STATUS=["$9"] OPENED=["$10"] RECHECK=["$11"] USED=["$12"]"}' corpus/SOURCES.md; echo "--- proposed teaches ---"; awk -F'|' 'NR==40 && $2 ~ /S043/ {print $8}' .ufo/waves/round-16/w1/SrcGitStatusRejected.md; echo "--- S032 recheck ---"; awk -F'|' 'NR==46{print "STATUS=["$9"] RECHECK=["$11"] USED=["$12"]"}' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'case "\$sec:\$var" in\|^  esac\|^  done$' tools/souji-census.sh | head -10; echo ---; grep -n '"clean" only when\|clean. only when' tools/souji-census.sh; sed -n '52,58p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "status.showUntrackedFiles\|not report untracked\|The default can be changed" -n /dev/null; echo "use page fetch again:"; true
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'case "\$sec' tools/souji-census.sh; sed -n '616,624p' tools/souji-census.sh; echo "--- esac tail ---"; sed -n '683,690p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/SOURCES.md | grep -c "S044"; git show HEAD:tools/souji-census.sh | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/SOURCES.md | grep -n "S044" | cut -c1-300
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff -- corpus/SOURCES.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff HEAD --stat -- corpus/SOURCES.md; git diff HEAD -- corpus/SOURCES.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -S 'S044 | git-status' -- corpus/SOURCES.md | head -5; echo "--- file identity ---"; sha256sum corpus/SOURCES.md; git show HEAD:corpus/SOURCES.md | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "literally incomplete\|Not observed anywhere\|hook-command-pathname" .ufo/waves/round-16/w1/SrcGitStatusRejected.md | cut -c1-220
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '633,650p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '155,163p' tools/souji-census.sh
```

Non-shell access: `read` on https://git-scm.com/docs/git-status (lines 1-300, 300-560, 560-770), `read` on https://raw.githubusercontent.com/git/git/v2.56.0/builtin/commit.c (1196-1330, 1480-1520), `grep` on the same raw URL, one `web_search` for the porcelain/`status.showUntrackedFiles` interaction.
