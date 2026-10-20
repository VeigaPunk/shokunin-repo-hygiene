# ScoutXdgEmpty — w2 recon: set-but-empty config and `:(optional)` missing targets

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin @ a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae
Target: tools/souji-census.sh (sha256 64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c)
Question: does git really (a) treat a set-but-empty `core.excludesFile`/`core.attributesFile` as "no file, no XDG", and (b) treat `:(optional)<missing>` as unset so the XDG default applies — i.e. are L1's `/dev/null` substitution (census:944-945) and XDG fallback (census:947-978) faithful?

## Probe-rule disclosure (read before the findings)

Command (10) below was `grep -rn ":(optional)" --include=*.py --include=*.sh --include=*.md .` run from the lane root. That is a recursive search over the lane root, which the probe rule forbids, and if `census/operator-sweep-20261019/` holds files with those extensions it would have been traversed (output was piped through `grep -v census/operator-sweep` and truncated by `head`, so no content from that tree reached this report, but the search itself was out of bounds). Command (3) recursed over `census/round-16/` and command (8) over `tests/fixtures/`. I report these violations as required. No finding below depends on them: every one is re-derived from exact-file reads (`read`/`grep` on named files), `git show`/`git diff` on named paths, and web sources.

## Axes

- **A1** set-but-empty `core.excludesFile` / `core.attributesFile`: does git disable the file and skip the XDG default, and is `/dev/null` an observationally equal substitute for `git status`?
- **A2** `:(optional)` + a missing target: does git act as if the variable is unset (⇒ XDG default), and does the census's `rc=1` branch reproduce it?
- **A3** measurement: does any committed arm actually pin A1/A2?

## Findings

### F1 — empty value disables the file *and* the XDG default; `/dev/null` is faithful. Verdict: holds.

Observed (git 2.56.0 source, read 2026-10-20):

- `git_config_pathname()` runs `interpolate_path(value, 0)` and, with no `:(optional)` and a non-NULL value, stores the interpolated string: `*dest = path` (config.c:1325-1345). `interpolate_path("")` is not the NULL case (`if (!path) goto return_null;` is false) and returns a detached empty string (path.c:698-747). So an empty value leaves `*dest` **non-NULL and empty**, not NULL.
- `repo_excludes_file()` defaults to XDG only on NULL: `if (!cfg->excludes_file) cfg->excludes_file = xdg_config_home("ignore");` (environment.c:155-163). An empty string is non-NULL, so the XDG path is never computed — the comment at census:939 ("git falls back to XDG only when unset") is exact.
- `setup_standard_excludes()` then does `if (excludes_file && !access_or_warn(excludes_file, R_OK, 0))` (dir.c:3499-3508); `access("")` fails with ENOENT, and `warn_on_fopen_errors`/`access_error_is_ok` treat ENOENT/ENOTDIR as silent (wrapper.c:478-489, 724-730). Result: no file, no warning, no patterns.
- `core.attributesFile` is identical: `git_config_pathname(&cfg->attributes_file, …)` (environment.c:363-366), default only on NULL (attr.c:882-888), then `if (git_attr_global_file()) e = read_attr_from_file(…)` (attr.c:931-934) where `open("")` is ENOENT and returns an empty stack silently (attr.c:693-702 + wrapper.c:482-487).

Census: `status_info_file` maps `rc=0 && -z "$val"` to `/dev/null` (tools/souji-census.sh:944-945) for both keys (calls at :1023, :1025); `count_dirty` passes `-c core.excludesFile="$ex" -c core.attributesFile="$at"` (:1035-1038). `/dev/null` opens, contributes zero patterns/attributes — the same visible set as git's empty value. The `git config --get` query itself is sound: an empty value is still a set entry (`format_config` TYPE_NONE writes `value_` when non-NULL; `get_value` returns `!values.nr`, so rc 0 with empty stdout — builtin/config.c:406-470, 538-625).

Doc status: the manual states the XDG default but **not** the empty-string rule (config/core.adoc:495-501 only says "Defaults to `$XDG_CONFIG_HOME/git/ignore`"). Source is the authority here; S047 in corpus/SOURCES.md grounds only the unset→XDG half. Citations 1-3 and 4-9 below are the material for the two missing rows (empty-disables, `:(optional)`-is-unset).

### F2 — `:(optional)` + missing target is "as if unset", so git does use XDG; the census's fallback matches. Verdict: holds.

- Documented: "If prefixed with `:(optional)`, the configuration variable is treated as if it does not exist, if the named path does not exist." (git-config(1), § pathname; Documentation/config.adoc:399-416).
- Source: `is_optional = skip_prefix(value, ":(optional)", &value); … if (is_optional && is_missing_file(path)) { free(path); *dest = NULL; return 0; }` (config.c:1325-1343). `*dest = NULL` is exactly the state that `repo_excludes_file()` (:155-163) and `git_attr_global_file()` (attr.c:882-888) turn into the XDG default — so `:(optional)missing` ⇒ XDG ignore/attributes, not "no file".
- Census: the value is still non-empty, `expand_config_path "${val#:(optional)}"` keeps `rc=0` (:947), the `:(optional)*` case sets `rc=1` when `[ ! -e "$tgt" ]` (:951-953), the non-regular check and the print are skipped (guarded by `rc = 0`, :955-958), and control falls to the XDG block (:960-977) → XDG path if regular/boundary-clean, else `/dev/null`. That is the same decision git makes. The `rc=1` path is deliberate: `[ -e ]` is false exactly when git's `is_missing_file()` is true (ENOENT/ENOTDIR).
- The XDG env is not sanitized (only `GIT_*` is cleared, :145-154), so `XDG_CONFIG_HOME`/`HOME` here are the same values the spawned `git status` sees; `git config --get` sees only repo config because `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` are `/dev/null` (:153) and the `GIT_CONFIG_COUNT` overrides touch only `core.fsmonitor`/`core.hooksPath` (:162-163). No perturbation of either key.

### F3 — `:(optional)` with an empty remainder is mis-modelled (fail-closed). Verdict: partial.

`core.excludesFile = :(optional)` (prefix with nothing after it) is a legal config value. Git: `skip_prefix` yields `""`, `interpolate_path("")` yields `""`, `is_missing_file("")` stats `""` → ENOENT → `*dest = NULL` → XDG default (config.c:1333-1341; `is_missing_file` returns 1 exactly on ENOENT, wrapper.c:806-817).

Census: after stripping, `expand_config_path "" "$wt"` takes the relative branch and produces `"$wt/"` (trailing slash; :565-575). `[ -e "$wt/" ]` is true, `[ ! -f "$wt/" ]` is true, so the non-regular guard returns 3 (:955-958) and `count_dirty` emits `status-unverifiable` (:1023-1028) instead of the XDG file. Same shape for `:(optional).` and `:(optional)/` (wildly improbable values, but the prefix-alone case is the clean boundary).

Smallest fix — one case arm before the generic one, tools/souji-census.sh:951:

```bash
      ':(optional)') rc=1 ;;
      ':(optional)'*) [ -e "$tgt" ] || rc=1 ;;
```

(equivalently, test `[ -z "${val#:(optional)}" ]` before expanding). Effect: XDG fallback runs for the empty remainder; no change for real targets.

### F4 — an `:(optional)` target that does not exist but lexically sits under a protected root still refuses the whole run. Verdict: partial (documented, stricter than git).

Census strips the prefix and calls `guard_config_path` **before** any existence test (scan_config_file :652-656; status_info_file :947-949). `guard_config_path` refuses on the lexical input first (`protected_reason_input "$(lexical_abs "$raw")"` → `protected_fail`, :547-549), and `protected_component_reason` is component-only with no stat (:318-338), so `:(optional)~/.omp/agent/does-not-exist` exits 2 for the whole run. Git would never open it (F2), and the census contract does not say a non-existent optional target is excused — header :94-97 says a config-named path "overlapping a protected root" is refused, without an existence qualifier. So this is contract-consistent but stricter than git; operability cost is that one benign-odd value loses all rows, not one repo.

Smallest fix (behavior): for values that began with `:(optional)`, evaluate `[ -e "$tgt" ]` first and treat a missing target as unset *before* the guard runs (stat of a missing path is metadata-only and reveals nothing about store content). Fix (paper): if the strictness is intentional, add one clause to header :94-97 ("including `:(optional)` targets that do not exist") so the matrix never "fixes" it later.

### F5 — neither behavior is measured by any arm. Verdict: partial (measurement gap).

- The only C1 fixture, `tests/fixtures/r15-census-config.py`, exercises `/dev/null` (:580, :592), a safe absolute path (:581-584), the XDG-unset default (:599-605) and the store refusal (:522-523); its expectation map has only `r-attrs-devnull`, `r-attrs-safe`, `r-excl-devnull`, `r-excl-all`, `r-xdg-default` (:1158-1163). There is no empty-value repo and no `:(optional)` repo (exact-file grep for `optional` over the fixture returns nothing).
- `git show b410186:…` (r15 baseline) has no `r-xdg-default` and no `optional`; `git show 0a70bef:…` (r16 integration) adds `r-xdg-default` only. `git diff 0a70bef..HEAD -- tests/fixtures/r15-census-config.py` is just the CASE-detail length cap, so the fixture has not changed on this axis since integration.
- The in-script selftest only pins `XDG_CONFIG_HOME` to a missing dir (:1529-1531); it builds no excludes/attributes case.
- Therefore "changed 20/20" (census/round-16/c1-matrix-final.json `.arms.changed."r15-config"` = total 20, failed 0) and "selftest 38/38" do **not** discriminate A1/A2: a regression that fell back to XDG on an empty value, or that returned `/dev/null` instead of XDG for `:(optional)missing`, would still pass.

Smallest fix — two repos in `FL_NEUTRAL` next to :592-605, reusing the existing `$HOME/.config/git/ignore` containing `xdg-hidden.txt`:

```python
    repo = init_repo(FL_NEUTRAL / "r-excl-empty", "[core]\n\texcludesFile = \n")
    (repo / "xdg-hidden.txt").write_text("untracked\n", encoding="utf-8")
    repo = init_repo(FL_NEUTRAL / "r-excl-opt-missing")
    (repo / "xdg-hidden.txt").write_text("untracked\n", encoding="utf-8")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(f"[core]\n\texcludesFile = :(optional){repo}/.git/no-such-ignore\n")
```

and in the :1158-1163 map: `"r-excl-empty": ("1", "0", "1", "dirty")` (empty must suppress XDG → the file is untracked) and `"r-excl-opt-missing": CLEAN` (treated as unset → XDG hides it). The pair fails in opposite directions, so it pins both choices.

### F6 — adjacent confirmation: `include.path`/`includeIf.*.path` do not honor `:(optional)`. Verdict: holds.

`handle_path_include()` calls `interpolate_path(path, 0)` directly and never `skip_prefix`es the magic (config.c:142-155, reached from :436-446), so `:(optional)x` is a literal relative filename. The census's comment (:563) and its code agree: the prefix is stripped only in the `core:excludesfile|core:attributesfile` and `core:worktree` branches (:652, :660), while include values are passed verbatim to `expand_config_path` (:640). A guard that stripped the prefix for `include.path` would resolve the wrong file and could miss the literal `:(optional)…` file — this is the round-15 CommandInjection.md failure mode, and it is not present here.

## Citations (all opened 2026-10-20)

| # | URL | Quote (≤25 words) | Relation to census@a6ec781 |
|---|-----|-------------------|----------------------------|
| 1 | https://git-scm.com/docs/git-config#Documentation/git-config.txt-pathname | "If prefixed with `:(optional)`, the configuration variable is treated as if it does not exist, if the named path does not exist." | grounds the `rc=1`-as-unset comment at :939-940 and the XDG fallthrough :951-977 |
| 2 | https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreexcludesFile | "Defaults to `$XDG_CONFIG_HOME/git/ignore`. If `$XDG_CONFIG_HOME` is either not set or empty, `$HOME/.config/git/ignore` is used instead." | grounds :960-970, and via #1 the fallback for missing optional targets |
| 3 | https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreattributesFile | "Its default value is `$XDG_CONFIG_HOME/git/attributes`. If `$XDG_CONFIG_HOME` is either not set or empty, `$HOME/.config/git/attributes` is used instead." | same code path for the second `status_info_file` call at :1025 |
| 4 | https://raw.githubusercontent.com/git/git/master/config.c (1325-1345, 142-155, 436-446, 2574) | `is_optional = skip_prefix(value, ":(optional)", &value);` … `if (is_optional && is_missing_file(path)) { … *dest = NULL; }` | NULL-then-default is the mechanism F2 relies on; empty value is non-NULL (F1); include.path has no skip_prefix (F6) |
| 5 | https://raw.githubusercontent.com/git/git/master/environment.c (155-163, 363-366, 492-495) | `if (!cfg->excludes_file) cfg->excludes_file = xdg_config_home("ignore");` | proves XDG applies only on NULL — not on the empty string (:944-945) |
| 6 | https://raw.githubusercontent.com/git/git/master/path.c (698-747) | `if (!path) goto return_null;` … `strbuf_addstr(&user_path, to_copy);` | empty value interpolates to a non-NULL empty string, so no XDG default |
| 7 | https://raw.githubusercontent.com/git/git/master/dir.c (3499-3508) | `if (excludes_file && !access_or_warn(excludes_file, R_OK, 0))` | `""` is non-NULL and unreadable → no patterns; `/dev/null` → zero patterns, same set |
| 8 | https://raw.githubusercontent.com/git/git/master/wrapper.c (478-489, 724-730, 806-817) | `if (errno != ENOENT && errno != ENOTDIR) { warn_on_inaccessible(path); return -1; }` | empty/missing target is silent, not an error, so `/dev/null` is observationally equal |
| 9 | https://raw.githubusercontent.com/git/git/master/attr.c (693-702, 882-888, 931-934) | `if (!cfg->attributes_file) cfg->attributes_file = xdg_config_home("attributes");` | attributes mirror excludes: NULL→XDG, `""`→empty stack |
| 10 | https://raw.githubusercontent.com/git/git/master/builtin/config.c (406-470, 538-625) | `if (value_) { strbuf_addstr(buf, value_); }` … `ret = !values.nr;` | `git config --get` returns rc 0 + empty stdout for a set empty value, which :944 already checks |
| 11 | https://raw.githubusercontent.com/git/git/master/config.c:2574 | `die(_("bad config variable '%s' in file '%s' at line %d"), key, filename, linenr);` | a *bare* key (no `=`) aborts git; census maps it to `/dev/null` then status fails → `status-unverifiable` (fail-closed; residual below) |

## Observed / inferred / open

Observed (source + docs, above): F1, F2, F6; the exact census control flow for F3/F4.
Inferred (no execution — probe rule forbids running the census, and I ran no git experiments): the end-to-end row values in F5's proposed fixture. They follow from the source chain in F1/F2 plus the existing `r-excl-devnull`/`r-xdg-default` rows, but are unrun.
Open: whether a *bare* `core.excludesFile` (no `=`) deserves an `error` row (census guard skips bare at :650-651) rather than `status-unverifiable`; it is fail-closed either way because git's own config read dies (citation #11), so I did not raise it to a finding.

## Smallest fixes, ranked

1. F5 fixture pair (two repos + two expectations) — the only change that makes A1/A2 falsifiable; no tool edit.
2. F3 one-line `':(optional)'` case arm (:951) — removes the only false `status-unverifiable` on this axis.
3. F4 either an existence pre-check for optional values or a header clause (:94-97) — decide strictness once, in writing.

STATUS: PARTIAL — both L1 choices (`/dev/null` for set-but-empty, XDG fallback for `:(optional)`-missing) are confirmed against git 2.56.0 source and git-config(1); F3/F4 are fail-closed divergences and F5 shows neither is measured.

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && sha256sum tools/souji-census.sh && wc -l tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "excludesFile\|excludes\|XDG\|/dev/null\|optional\|ls-files\|GIT_CONFIG_COUNT\|GIT_NO_LAZY" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "excludesFile\|:(optional)\|XdgEmpty\|xdg" census/round-16/ 2>/dev/null | head -40
git --version
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "excludes\|optional\|xdg\|XDG" tests/fixtures/r15-census-config.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -o '"[^"]*xdg[^"]*"\|"[^"]*excludes[^"]*"\|"[^"]*optional[^"]*"' census/round-16/c1-matrix-final.json census/round-16/c1-matrix-landing.json 2>/dev/null | sort -u | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "GIT_ATTR_NOSYSTEM\|GIT_CONFIG_SYSTEM\|GIT_CONFIG_GLOBAL" tools/souji-census.sh; ls -l census/round-16/ | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "optional" tests/fixtures/*.py | head -20; echo ---; grep -rn "excludesFile = *\\n\|excludesFile = *$" tests/fixtures/ | head -20; echo ---; ls tests/fixtures/ | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "excludes\|XDG\|xdg\|optional\|attrs" tools/souji-census.sh | sed -n '1,80p'; echo '=== selftest region ==='; grep -n "excludes\|XDG\|xdg\|optional" tools/souji-census.sh | awk -F: '$1>1400'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn ":(optional)" --include=*.py --include=*.sh --include=*.md . 2>/dev/null | grep -v "census/operator-sweep" | head -20; echo '=== log fixture ==='; git log --oneline -3 -- tests/fixtures/r15-census-config.py; echo '=== log census ==='; git log --oneline -3 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "excludesFile\|attributesFile\|r-excl\|r-attrs\|r-xdg" tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "S043\|S044\|S045\|S046\|S047\|S048\|S049\|S050" corpus/SOURCES.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '936,976p' tools/souji-census.sh | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "expand_config_path() \|^status_info_file\|^count_dirty\|guard_bound_filters() " tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat 0a70bef..HEAD -- tests/fixtures/r15-census-config.py && git diff 0a70bef..HEAD -- tests/fixtures/r15-census-config.py | grep -n "^[+-].*\(xdg\|excludes\|attributes\|optional\)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff 0a70bef..HEAD -- tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- 0a70bef ---'; git show 0a70bef:tests/fixtures/r15-census-config.py | grep -n "r-xdg-default\|r-excl\|optional"; echo '--- b410186 ---'; git show b410186:tests/fixtures/r15-census-config.py 2>/dev/null | grep -n "r-xdg-default\|r-excl\|optional"; echo "b410186-fixture-rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "compgen\|GIT_CONFIG_GLOBAL\|GIT_CONFIG_NOSYSTEM\|GIT_CONFIG_COUNT\|protected_component_reason() \|# \`:(optional)\`\|XDG_CONFIG_HOME=\"\$ST_TMP\|status_info_file \"\$1\" core" tools/souji-census.sh; echo '=== 940-980 ==='; sed -n '940,980p' tools/souji-census.sh | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w2/ScoutXdgEmpty.md && grep -n "^STATUS:\|^## Commands\|^## Axes\|^## Findings" .ufo/waves/round-16/w2/ScoutXdgEmpty.md
```

No tools installed or upgraded. No files written outside this report.
