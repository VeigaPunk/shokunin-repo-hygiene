# RevStatusInfoFile — `status_info_file` / effective excludes + attributes

Seat: `SoujiR16.RevStatusInfoFile` (reviewer, leaf). Lane root:
`/home/vgpnk/Projects/shokunin/souji-shokunin`. Source inspection only; nothing executed.

Assigned target: `tools/souji-census.sh` at
`cbf688ab2ab28e38103e5a9417ca525b5f2ed423`. Proof: `git show cbf688a:tools/souji-census.sh`
saved to `/var/tmp/r16-census-cbf688ab.sh`, `sha256sum` = `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`,
`bash -n` clean. **The worktree no longer equals the target**: it is `M` against cbf688a and was
`df4c780e…` when this report was written, moving while reviewed (`fed43c71 → feba44c7 → d9762d55 →
df4c780e` observed). All findings below cite **cbf688a** line numbers; the live-delta section states
which are already addressed there.

## Verified correct (no defect)

- **Relative-path base is git's base for every call site.** `expand_config_path "$val" "$wt"`
  (cbf688a:878) pairs with `git -C "$wt"` at all three consumers — `ls-files`/`check-attr`
  (:922,:924) and `status` (:947-949). git leaves a relative pathname value relative (CWD-relative
  at open; docs carry no base clause for these two keys, unlike `core.worktree`/`include.path`),
  and `-C` makes `$wt` the CWD, so the substitution is exact, not approximate. Only this pairing
  preserves it; a future call site that drops `-C <same dir>` breaks it. (Corroborated by
  `ScoutExcludesRelative.md` F1, whose primary-source citation I did not re-fetch.)
- **No second interpretation.** `status_info_file` prints an absolute, resolved path and it is
  handed to git through `-c`; git cannot re-expand or re-anchor it.
- **Guard before use.** The config read (`git config --get`) precedes the guard; the guard precedes
  every read of the named file (`status_info_file` → `guard_bound_filters`' `ls-files`/`check-attr`
  → `status`). The XDG branch pre-checks `protected_reason_input` on the lexical path (:894) before
  `resolve_guarded` (:897), and a refused walk collapses to `/dev/null`, so no stat/open occurs
  below the store.
- **`~/` uses raw `$HOME`** (:543), matching `interpolate_path(value, 0)`.
- **XDG default construction** (:884-889): non-empty `$XDG_CONFIG_HOME/git/<leaf>`, else
  `$HOME/.config/git/<leaf>` — the documented default and fallback condition.
- **Missing/unreadable files.** XDG default requires `-f` (:897): git also skips a missing default
  silently. A configured value is passed through even if missing (:880): git tries it, warns, and
  continues — same row.
- **`git config --get` semantics**: last value wins for a scalar key, matching git's own
  "last one wins"; includes (`includeIf` conditions included) are resolved because the query runs
  inside the repo, exactly as `status` does.
- **Config-scope clearing is self-consistent.** `GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` (:148-150) apply to the `--get` query and
  to `status` alike, and `-c` overrides any remaining scope, so the reconstructed value cannot
  disagree with the one `status` uses.
- **`-c` value safety**: both values are absolute and tab/CR/newline-free (`guard_config_path`
  :526-528 plus the final `resolve_guarded` walk), so neither option injection nor argument
  splitting is possible.

## Findings

### F1 — MEDIUM — set-but-empty value resurrects the XDG default (row/parity defect)
`cbf688a:876-877` reads the value with `… || true` and then tests `[ -n "$val" ]`. A repo that sets
`[core] excludesFile =` (or `attributesFile =`) yields rc 0 with an empty value from
`git config --get`; the census treats it as **unset** and applies `$XDG_CONFIG_HOME/git/<leaf>`
(:884-897). git treats an explicitly empty pathname as *set*: the XDG default is substituted only
when the variable is NULL, so `excludesFile=""` → no global excludes file and **no fallback**;
`attributesFile=""` behaves the same (`environment.c`/`dir.c`/`attr.c`, per
`ScoutExcludesRelative.md` F3). Effects: (a) dirty count can undercount because the operator's
global ignore hides files this repo asked to track; (b) with `attributesFile=""`, the XDG
attributes file can bind a filter driver, and `guard_bound_filters` (:907-933) then turns a real
row into `dirty 0, status-unverifiable`. Baseline evidence that this is a rewrite regression, not a
pinned choice: the r15 candidate's `_honored_cfg_path` in `b410186` mapped an empty value to
`INERT` → `/dev/null`. Reachable with only repo-local config; no fixture case covers it.

Minimal patch (exactly what the live worktree now has at `:911-912`):
```sh
-  local wt=$1 key=$2 leaf=$3 val tgt base
-  val=$(git -C "$wt" config --get "$key" 2>/dev/null || true)
-  if [ -n "$val" ]; then
+  local wt=$1 key=$2 leaf=$3 val tgt base rc=0
+  val=$(git -C "$wt" config --get "$key" 2>/dev/null) || rc=$?
+  if [ "$rc" = 0 ] && [ -z "$val" ]; then printf '/dev/null'; return 0; fi
+  if [ "$rc" = 0 ]; then
```

### F2 — MEDIUM — non-protected, unresolvable/ambiguous config values abort the whole run
The header contract (`cbf688a:90-97`, fixture header line 14) says whole-run exit 2 is kept **only**
for a protected-namespace reach; everything else that cannot be evaluated is one `error` row. But
the excludes/attributes branch of `scan_config_file` does `guard_config_path … || exit 2` (:624),
and `guard_config_path` refuses with `protected_fail` (→ exit 2) not only for a protected reach but
also for `tab`/`CR`/`LF` in the value (:526-528) and for an unresolved/dangling/looping walk
(:532-534). A quoted multi-line value (`excludesFile = "a\nb"`) or a self-referential symlink named
by the value therefore kills the entire census, though git only warns and continues (ELOOP/ENOENT →
"cannot use … as an exclude file"). Reachable with repo-local config. The same class is latent in
`status_info_file` (:878-880: `expand_config_path` failure and `guard_config_path` failure are both
whole-run there); it is currently unreachable because the scan refuses those values first.

Minimal patch: let `guard_config_path` return 3 for the non-protected failures and degrade at the
call sites (this is what the live worktree now does — `guard_config_path` classifies a protected
reach from the finding text and returns 3 otherwise; callers `{ rc=$?; [ "$rc" = 3 ] || exit 2;
cfg_soft …; }`, live `:627-629`, `:639-640`, `:647-648`, `:915-916`), **plus** a fixture case —
none exists for a multi-line/looping excludes value, so the current "20/20" does not exercise it.

### F3 — LOW — per-occurrence refusal ignores git's last-wins value (value-blind, r14-harm class)
`scan_config_file` evaluates every occurrence (:622-627) and its own comment says "last-wins
settings track git's own reading order" (:591), but the refusal decision is per occurrence, not per
effective value. Two concrete inversions: (a) `$GIT_DIR/config` sets `excludesFile = <store>/ignore`
and then `excludesFile = /dev/null` — git's effective value is `/dev/null` and it never opens the
store path, yet the census exits 2 for the whole run; (b) an earlier `~user/x` shadowed by a later
clean absolute path yields an `error` row although the effective config is evaluable. This is the
value-blind whole-run harm r14 was rejected for, narrowed to shadowed occurrences.

Minimal patch shape: record the last raw value per key during the scan (`CFG_VAL["$sec:$var"]=$val`
inside the recursion, which already follows includes in place), then evaluate protection/softness
once for the final entry in `guard_git_config`. If fail-closed-on-any-occurrence is preferred, say
so in the header and drop the last-wins sentence — currently code and comment disagree.

### F4 — LOW — scan's base for these two keys is not git's base (linked worktrees/submodules)
The scan expands with `${dir%/*}` (:624), where `dir` is the admin gitdir (`…/.git/worktrees/<n>`,
`…/.git/modules/<m>`) or the common gitdir — not the worktree root the row is about. git resolves
the value against its CWD (the worktree root via `-C`), and `status_info_file` correctly uses `$wt`
(:878), so the *use-time* guard is right and no store read can slip past; the only consequence is a
possible **false-positive whole-run exit 2** when the admin-relative resolution happens to contain a
protected component while the worktree-relative one does not.

Minimal patch: for these two keys make the scan check textual only —
`protected_reason_input "$(lexical_abs "$tgt")" >/dev/null && protected_fail …` — and leave the
base-dependent walk to `status_info_file`, which runs before the only read of the file. (The
commands that precede it — `worktree list`, `rev-list`, `rev-parse` — never open excludes/attributes,
so guarding there loses nothing.) Alternative: thread the worktree root into `guard_git_config` as a
fourth argument and use it here.

### F5 — LOW — relative `$XDG_CONFIG_HOME` and set-but-empty `$HOME`
`cbf688a:884-893`: a non-absolute XDG base is replaced by `/dev/null`, and an empty `$HOME` short-circuits
to `/dev/null`. git accepts any non-empty `$XDG_CONFIG_HOME` (concatenates and opens from its CWD,
i.e. `$wt` under `-C`), and its `$HOME` test is pointer-based, so `HOME=""` still yields
`/.config/git/<leaf>`. The result is a silent drop of patterns/attributes git would apply — same
direction as F1, much narrower (invalid environment).

Minimal patch:
```sh
-    if [ -z "${HOME:-}" ]; then printf '/dev/null'; return 0; fi
+    if [ -z "${HOME+x}" ]; then printf '/dev/null'; return 0; fi
     base="$HOME/.config"
   fi
   tgt="$base/git/$leaf"
   case "$tgt" in
-    /*) ;;
-    *) printf '/dev/null'; return 0 ;;
+    /*) ;;
+    *) tgt="$wt/$tgt" ;;   # git opens it from its cwd; -C made that $wt
   esac
```

### F6 — LOW — `:(optional)` is mis-passed (corroborated by ScoutExcludesRelative F4)
`expand_config_path` (:540-549) has no `:(optional)` case, so `core.excludesFile = :(optional)<rel>`
becomes `"$wt/:(optional)<rel>"` and is passed as an absolute `-c` value, where git can no longer
strip the prefix. git strips it and, when the stripped target is missing, sets the pointer to NULL —
which re-enables the XDG default. Both branches diverge: existing target → census reads a literal
`:(optional)…` path git does not; missing target → git falls back to XDG, census suppresses it.
Obscure value, but a deterministic parity break. **Already fixed in the live worktree** (:548-551
strip, :917-919 missing → XDG).

Minimal patch: as live, but see the cross-caller risk in the addendum — the strip sits in the shared
expander, so `include.path` and `core.worktree` now strip too.

## Parity with pre-harm a31642d

For the **local-value** path the reconstruction is exact (relative, absolute, `~/`, unset), except
F1/F6. Blanket parity is not true, and the round should not claim it: pre-harm `a31642d` cleared
only `GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE` (`:71`) and exported `GIT_OPTIONAL_LOCKS`
(`:73`) — it did **not** touch `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM`/`GIT_CONFIG_NOSYSTEM`, so its
`status` honored the operator's global/system `core.excludesFile` and `core.attributesFile`, while
cbf688a disables them (documented at :121-123). A repo that relies on a global value (repo has no
local value, operator's `~/.gitconfig` sets one) gets the XDG default instead of the pre-harm file.
The fixture pins `GIT_CONFIG_GLOBAL=/dev/null` and a synthetic `HOME` (`r15-census-config.py:719-727,
367`), so it cannot observe this. Recommend the lesson/report state this residual explicitly.

## Verification gaps (fixture)

`tests/fixtures/r15-census-config.py` has cases only for absolute local values (`:543-561`) and for
store-reaching values (`:496-497`). It has **no** case for: set-but-empty value (F1), relative value
(neither main nor linked worktree), a present XDG default file, `~user`/`%(prefix)` **on these two
keys** (the `~user` degrade case is `include.path` only, `:469`), shadowed/repeated occurrences (F3),
multi-line/looping values (F2), or the linked-worktree scan base (F4). The claimed 20/20 therefore
says nothing about F1-F6.

## Live worktree addendum (uncommitted; `7746d865…` at finalization)

(The file moved four times during this review: `fed43c71 → feba44c7 → d9762d55 → df4c780e → 7746d865`.
Line numbers in this section are from `d9762d55`; the constructs, re-checked at `7746d865`, are
unchanged: F3 has no last-wins store, F4's base is still `${dir%/*}` (:642), F5 is still
`${HOME:-}` (:936) with a non-absolute XDG base forced to `/dev/null`.)

- Fixes F1 (`:911-912`), F2 (`guard_config_path` → rc 3 + degrade blocks at `:627-629`, `:639-640`,
  `:647-648`, `:915-916`), F6 (`:548-551`, `:917-919`), and adds a non-regular-target degrade
  (`:921`) that is strictly safer than pre-harm (git would open a FIFO named by the value and block).
- **Still live: F3, F4, F5.** F4's base is still `${dir%/*}` at `:636`.
- Not a defect: `pid=$!; wait "$pid"` in `guard_bound_filters` (`:934-935` in `d9762d55`) is
  documented bash behaviour, not an accident — bash ≥5.0's NEWS: "The `wait' builtin can now wait
  for the last process substitution created" and "Bash now allows waiting for the most recent
  process substitution, since it appears as `$!`" (installed bash 5.3 per `/usr/share/doc/bash/NEWS`
  header). `set -o pipefail` inside the substitution makes the reaped status the pipeline's.
- **New risk to check before landing:** `v=${v#:(optional)}` sits in the shared
  `expand_config_path`, so `include.path` (`:624`) and `core.worktree` (`:644`) now strip the
  prefix as well. The primary-source grounding places the strip in `git_config_pathname` (pathname
  config values); `include.path` is resolved relative to the file git actually opens. If git does
  not strip there, the census now scans a *different* file than git reads — false `error` rows or a
  missed guard. Scope the strip to the two pathname callers (e.g. a fourth parameter) unless the
  scout confirms include.path strips too.
- Wording drift: live `status_info_file` returns 3 for `~user`/`%(prefix)` and `count_dirty` maps it
  to `unverifiable` (`:976-979`), while the header (:94-96) still lists those as the `error`-row
  class. For local config the scan soft-fails first, so rc 3 is defensive-only; reconcile the
  header (or the mapping) so the contract matches the code.

## Residual risk

- Guard and open are not atomic (documented). A component swapped to a store symlink between
  `resolve_guarded` and git's `open` is detectable only by that documented window.
- An XDG default that resolves into the protected namespace is silently replaced by `/dev/null`
  (safe, not diagnosed). No row/flag tells the operator patterns were dropped.
- Pre-existing, out of scope here: hardlinked store aliases; `GIT_ATTR_NOSYSTEM` is not cleared, so
  system attributes affect `check-attr` exactly as they affect `status` (parity preserved).

STATUS: review complete. F1 (MEDIUM, row accuracy) and F6 are fixed in the live worktree; F2 (MEDIUM, whole-run abort on non-protected unresolvable values) is fixed in the live worktree but untested by the fixture; F3/F4/F5 remain live in both cbf688a and the worktree. No execution was possible under the probe rule, so every git-behaviour claim above is source/doc-grounded, not observed.

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -6 && git status --porcelain=v1 -uno | head -20 && git rev-parse HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/r16-census-cbf688ab.sh; wc -l /var/tmp/r16-census-cbf688ab.sh; git show a31642d:tools/souji-census.sh > /var/tmp/r16-census-a31642d.sh; wc -l /var/tmp/r16-census-a31642d.sh; git show b410186:tools/souji-census.sh > /var/tmp/r16-census-b410186.sh 2>&1; wc -l /var/tmp/r16-census-b410186.sh
cd /var/tmp && grep -n "status_info_file\|excludesFile\|attributesFile\|statusInfo\|status_info" r16-census-cbf688ab.sh
cd /var/tmp && grep -n "status_info_file\|excludesFile\|attributesFile\|statusInfo\|status_info" r16-census-a31642d.sh r16-census-b410186.sh
cd /var/tmp && grep -n "excludesFile\|attributesFile\|XDG_CONFIG_HOME\|hooksPath\|fsmonitor" r16-census-a31642d.sh
cd /var/tmp && grep -n "expand_config_path\|guard_config_path\|lexical_abs\|resolve_guarded\|protected_reason_input\|protected_fail\|canon_home" r16-census-cbf688ab.sh
cd /var/tmp && grep -n "^[a-zA-Z_][a-zA-Z0-9_]*() *#\|^[a-zA-Z_][a-zA-Z0-9_]*() {\|^[a-zA-Z_][a-zA-Z0-9_]*()$" r16-census-cbf688ab.sh
cd /var/tmp && sed -n '1030,1170p' r16-census-cbf688ab.sh
cd /var/tmp && grep -n "count_dirty\|status --porcelain\|--no-optional-locks" r16-census-a31642d.sh; echo ---; sed -n '/^count_dirty()/,/^}/p' r16-census-a31642d.sh
ls /usr/share/man/man5/ 2>/dev/null | grep -i "git" | head -40; ls /usr/share/man/man1/ 2>/dev/null | grep -i "^git" | head -20
cd /var/tmp && sed -n '1218,1305p' r16-census-cbf688ab.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,70p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "relative\|~user\|tilde\|prefix\|\%(" tests/fixtures/r15-census-config.py | head -40
cd /var/tmp && sed -n '560,700p' r16-census-cbf688ab.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tests/fixtures/ | head -30; wc -l tests/fixtures/r15-census-config.py 2>/dev/null; git cat-file -t cbf688ab2ab28e38103e5a9417ca525b5f2ed423 && git show --stat --oneline cbf688ab2ab28e38103e5a9417ca525b5f2ed423 | head -20
ls /usr/share/doc/git/ 2>/dev/null | head; ls /usr/share/doc/git-doc 2>/dev/null | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "excludesFile\|attributesFile\|XDG_CONFIG_HOME\|status_info_file" tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | grep -n "^[+-].*\(excludesFile\|attributesFile\|XDG\|status_info_file\)" | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '470,600p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "oracle\|def expected\|status --porcelain\|pre-harm\|baseline" tests/fixtures/r15-census-config.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "HOME\|environ\|subprocess.run\|def run_tool\|env=" tests/fixtures/r15-census-config.py | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1060,1145p' tests/fixtures/r15-census-config.py
cd /var/tmp && sed -n '60,165p' r16-census-cbf688ab.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '680,760p' tests/fixtures/r15-census-config.py
cd /var/tmp && sed -n '700,840p' r16-census-cbf688ab.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh /var/tmp/r16-census-cbf688ab.sh && bash -n tools/souji-census.sh && echo PARSE_OK && ls -la .ufo/waves/round-16/w1/ 2>&1 | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tools/souji-census.sh | sed -n '872,906p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tools/souji-census.sh | sed -n '515,560p'; echo ===; grep -n "" tools/souji-census.sh | sed -n '600,632p'
cd /var/tmp && sed -n '1035,1085p' r16-census-b410186.sh
cd /var/tmp && sed -n '/^_honored_cfg_path()/,/^}/p' r16-census-b410186.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tools/souji-census.sh | sed -n '84,110p'; echo ===; grep -n "" tools/souji-census.sh | sed -n '1224,1240p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/w1/ | sed -n '20,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,45p' .ufo/waves/round-16/w1/RevSoftPropagation.md 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,120p' .ufo/waves/round-16/w1/ScoutExcludesRelative.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,120p' .ufo/waves/round-16/w1/SrcGitignoreXdg.md
cd /var/tmp && grep -n "GIT_\|env -i\|export " r16-census-a31642d.sh | head -30; echo ===; sed -n '60,110p' r16-census-a31642d.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n ":(\|optional" tools/souji-census.sh | head; echo ===; grep -n "expand_config_path" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh; git status --porcelain -- tools/souji-census.sh; git rev-parse HEAD; git diff --stat cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | head -120
ls /usr/share/doc/bash/ 2>/dev/null; ls /usr/share/doc/bash/NEWS 2>/dev/null /usr/share/doc/bash/CHANGES 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tools/souji-census.sh | sed -n '870,955p'
grep -n -i "process substitution" /usr/share/doc/bash/NEWS | head -40
grep -n '\$!' /usr/share/doc/bash/NEWS | head -30
sed -n '1,12p' /usr/share/doc/bash/NEWS; echo ...; sed -n '110,128p' /usr/share/doc/bash/NEWS; echo ...; sed -n '560,570p' /usr/share/doc/bash/NEWS; echo ...; sed -n '803,815p' /usr/share/doc/bash/NEWS
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tools/souji-census.sh | sed -n '618,634p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh; git diff --stat cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh; git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | sed -n '120,320p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | sed -n '1,120p'
cd /var/tmp && grep -n "" r16-census-cbf688ab.sh | sed -n '935,960p'; echo ===; cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh && grep -n "" tools/souji-census.sh | sed -n '610,618p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "guard_config_path\|expand_config_path\|status_info_file\|rc = 3\|\"3\"" tools/souji-census.sh | head -25; echo ===; sha256sum tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tools/souji-census.sh | sed -n '596,665p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tools/souji-census.sh | sed -n '900,925p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "" tools/souji-census.sh | sed -n '924,945p'; echo ===; grep -n "" tools/souji-census.sh | sed -n '583,596p'
```

Notes: `read` was used for ranged reads of `/var/tmp/r16-census-cbf688ab.sh` and for the compressed
man pages (which the reader returned as a bare stub, so the man pages contributed nothing). `sed -n`
and `grep -n "" | sed -n` were used only to page exact named files/results; no file was modified.
Three blob copies were written under `/var/tmp` (read-only use, no repository file touched); no
census run, no fixture run, no network, no package-manager action, and nothing under
`census/operator-sweep-20261019/`, `~/.omp`, `.ufo/state`, `.ufo/watchdog.log`, `MANIFEST.json`, or a
sibling lane was opened.
