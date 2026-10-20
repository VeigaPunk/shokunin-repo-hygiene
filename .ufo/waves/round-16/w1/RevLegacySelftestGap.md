# RevLegacySelftestGap — `--selftest` coverage of the five r16 census behaviors

Round 16, W1, reviewer seat. Source inspection at C1 commit
`cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (`tools/souji-census.sh`, 1784 lines); **no
execution** (item: "Review (source inspection; no execution)"). All line numbers below are
that blob's lines (identical to the worktree file).

Axes named: **coverage** (does the legacy gate actually exercise the r16 repair surface it
certifies?) and **calibration** (a green `--selftest` must mean what C1 says it means, and
must mean the same thing on a different host).

Advisory only. I did not edit `tools/souji-census.sh`; the patches below are proposals.

## Verdict in one line

All five named r16 behaviors are **mechanically present** in the tool and **entirely
uncovered** by `run_selftest` (lines 1432-1742); in addition the selftest is **not
hermetic** under r16's own XDG honoring, so two existing assertions (lines 1565-1567,
1571-1575) are host-dependent. No functional defect was found in the five production
mechanisms themselves.

## Coverage matrix (verified by reading `run_selftest`, 1432-1742)

| r16 behavior | mechanism (cbf688a) | selftest check today | finding |
|---|---|---|---|
| un-evaluable config degrades to one `error` row, run exit 0, other repos unaffected | `cfg_soft` 555-558; soft paths 563-568, 582-591, 611-613, 621-623, 628-630, 635-637; soft returns 661-663, 678-680, 741, 773, 789-790, 794, 812, 828-829, 833; row 1086-1091 | **none** (no fixture has un-evaluable config) | F2 |
| filter driver bound to a tracked path skips status for that repo only; driver never runs | `guard_bound_filters` 907-932; skip 939-943 | **none** (no fixture configures a filter) | F3 |
| `<protected>` redaction of a refused path inside a protected root | `protected_fail` 184-191, redaction line 187 | exercised at 1705-1725 but **never asserted** | F6 |
| XDG excludes/attributes default honored when present + boundary-clean, else `/dev/null` | `status_info_file` 874-900 (XDG branch 884-897) | **none**; worse, no invocation pins `HOME`/`XDG_CONFIG_HOME` | F1, F4 |
| `GIT_NO_LAZY_FETCH=1` for every child git (promisor/partialClone inert) | export 147 | **none** | F5 |

Adjacent gaps found while checking those (not named by the item, reported because they bite
the same gate): F7 (inherited-`GIT_*` clearing is untested because the selftest pre-unsets
`GIT_DIR`), F8/F9 (advisory).

## Findings

### F1 — MEDIUM/HIGH (real defect): the selftest is host-dependent under r16's XDG honoring

`status_info_file` now resolves `$XDG_CONFIG_HOME/git/{ignore,attributes}` (884-897) and
passes it to every `git status` (947-949). Every census invocation inside the selftest
inherits the operator's `HOME` and `XDG_CONFIG_HOME`:

- 1520-1523 (`out1`, `out2`), 1631-1632, 1647-1648, 1662-1663, 1684-1685, 1693.
- The two protected tests pin `HOME` (1705, 1716) but not `XDG_CONFIG_HOME`; irrelevant for
  a pre-access refusal, but inconsistent.

Concrete failure modes on a host that has either file (this host currently has neither —
verified `/home/vgpnk/.config/git/ignore` and `.../git/attributes` are absent, and
`XDG_CONFIG_HOME=/home/vgpnk/.config` is exported in the harness environment):

1. `$XDG_CONFIG_HOME/git/ignore` containing any pattern that matches `untracked.txt` or
   `.scratch/` lowers `dirty` below **2** and trips the hard assertion at 1565-1567. Same
   class at 1571-1575 (flags lose `dirty`/`scratch`).
2. `$XDG_CONFIG_HOME/git/attributes` binding `filter=<name>` for a path a fixture tracks,
   where that fixture also configures `filter.<name>.clean`, flips the row to
   `status-unverifiable` via 939-943 (today no fixture configures a driver, so this vector
   needs both files; the ignore vector needs only one).

So the C1 "legacy `--selftest`" evidence is reproducible on this host only. That is an
operability defect in the gate, introduced by the r16 change it is supposed to certify.

Minimal patch: **P1** (pin `HOME`/`XDG_CONFIG_HOME` on every invocation).

### F2 — MEDIUM: the C1 headline behavior has zero selftest coverage

The row that repairs r14's harm is emitted at 1086-1091 and reached only when
`guard_git_surface` returns 1 (soft). No fixture produces un-evaluable config, so a
regression back to r14 semantics (whole-run `exit 2`, or a silently healthy-looking row)
would keep `--selftest` green. Reverting `cfg_soft` → `protected_fail` at e.g. 621-623 or
582-584 would be invisible to the gate.

No defect in the implementation: I traced every `return 1` on the soft path
(563-568, 582-591, 611-613, 621-623, 628-630, 635-637, 661-663, 678-680, 741, 773,
789-790, 794, 812, 828-829, 833) and each one either sets `CFG_SOFT_REASON` or propagates it;
`census_one` emits exactly one row and returns 0; `list_repos` swallows the same soft failure
at 1179/1209 with `|| true` and still appends the repo, so the row is produced (the scan
therefore runs twice per repo — cost only).

Minimal patch: **P2**.

### F3 — MEDIUM: bound-filter skip and "the driver never runs" are untested

`count_dirty` prints `unverifiable` and `status-skipped` at 939-943 when
`guard_bound_filters` (907-932) finds a config-declared driver bound by an attributes
source to a cached path. No fixture configures `filter.*`, so a regression that drops the
call (or inverts the newline test at 917) is invisible. The security-relevant half — the
driver must **not** execute — has no sentinel.

I re-derived 907-932 line by line; it is correct for `git config -z --get-regexp` output
(`key\nvalue\0`, valueless `key\0`): the `case "$rec" in *$'\n')` test at 914 matches only a
record *ending* in newline (explicit empty value), and 915-917 strip at the first newline,
so a driver with a command is collected. No defect found.

Minimal patch: **P3** (includes a canary that proves the driver never runs, plus an unbound
control repo proving a merely-declared driver stays inert).

### F4 — MEDIUM: XDG excludes/attributes resolution and its `/dev/null` fallbacks are untested

`status_info_file` 874-900 has five branches, none exercised: local value (876-883), XDG
absolute (884-889), unset `HOME` (886), relative `XDG_CONFIG_HOME` (890-893),
boundary-hit → `/dev/null` (894-896), missing file → `/dev/null` (897-901). r14's harm was
precisely a wrong branch here (forced `/dev/null` changed dirty counts); nothing pins it.

Minimal patch: **P4** (four runs over one fixture: HOME default honored; `XDG_CONFIG_HOME`
overrides it; unset `HOME`; relative `XDG_CONFIG_HOME`), plus an optional attributes leaf.

### F5 — LOW/MEDIUM: `GIT_NO_LAZY_FETCH` has no check, and cannot get a trace-based one

Line 147 exports `GIT_NO_LAZY_FETCH=1`, which is what makes `remote.*.promisor` /
`extensions.partialClone` inert (doc 102-107, 146). Deleting the export breaks the claim and
no check notices. Note the constraint that shapes the fix: the script clears **every**
inherited `GIT_*` variable at startup (lines 126-133), so a `GIT_TRACE2_EVENT` probe routed
through the census is impossible by design — the env would be dropped before any git runs.
The achievable evidence is therefore (a) the export exists in source and (b) promisor
markers are accepted without degrading the row. Neither proves "no fetch"; both are cheap
and neither can flake.

Minimal patch: **P5** (static export assertion + a promisor-marked repo that must stay
`clean`, with empty stderr).

### F6 — LOW: redaction is exercised but never asserted

`protected_fail` replaces a path inside a protected root with `<protected>` (187). The two
protected tests (1705-1725) already run through that branch (the refused path is
`$ST_TMP/home/.omp/agent[.git]`, which matches `protected_reason_inside`) but assert only
`path-protected`. A regression that echoed the store path would keep the selftest green.
This is the cheapest real gap to close: 4 assertions on existing variables, no new fixture.

Minimal patch: **P6**.

### F7 — LOW (adjacent): inherited-`GIT_*` clearing is untested

Every invocation passes `env -u GIT_DIR` (1520 etc.), which removes exactly the variable the
startup loop (126-133) is supposed to clear. Add one invocation that *sets* `GIT_DIR` to a
bogus path and requires byte-identical output. Patch: **P7**.

### F8 — INFO, no patch: latent divergence between scan (soft) and status (hard)

An unexpandable value is soft in `scan_config_file` (621-623 → `error` row) but hard in
`status_info_file` (878-879 → `protected_fail` → whole-run `exit 2`). Today the scan always
runs first for the same key, so 878-879 is unreachable (I checked every config source git
reads: local `config`, includes, `config.worktree` when enabled — all scanned). Recording it
because it is the exact shape of r14's harm: if a future read source bypasses the scanner,
`core.excludesFile = ~user/...` becomes a whole-run refusal again. No patch recommended
today; if hardened, make 878-879 mirror the scan (degrade that repo), not the boundary
channel.

### F9 — LOW (adjacent): a failing baseline run aborts without a FAIL line

`out1`/`out2` are produced under `set -e` (1518-1523), so a
nonzero census exit kills `run_selftest` at the call site: no `FAIL` line, no summary, only
`exit 2`/`1` and the trap cleanup. Acceptance still sees failure, but the transcript does not
say why. Patch: **P9** (optional, 8 lines).

## Proposed selftest patches (exact code, do not apply to the file from this seat)

Insertion points are "after line N" at `cbf688a`. Each block is plain bash valid inside
`run_selftest` (all locals declared; `st_init`/`st_commit`/`st_row_field` reused as-is).

### P1 — pin `HOME`/`XDG_CONFIG_HOME` (after line 1440, `mkdir -p "$fleet"`)

```bash
  # r16: status_info_file honors $XDG_CONFIG_HOME/git/{ignore,attributes}. Pin
  # both so a host ignore/attributes file cannot change fixture dirty counts
  # (and so the XDG tests below start from a known-empty default).
  local st_home="$ST_TMP/home-base"
  mkdir -p "$st_home/.config"
```

Then every census invocation in the selftest becomes
`env -u GIT_DIR -u XDG_CONFIG_HOME HOME="$st_home" SOUJI_CENSUS_SELFTEST_ACTIVE=1 \`
— lines 1520, 1522, 1631, 1647, 1662, 1684, 1693 — and the two protected invocations
(1705-1707, 1716-1718) gain `-u XDG_CONFIG_HOME` while keeping their own `HOME="$ST_TMP/home"`.
`$st_home` and `$fleet` are siblings under `$ST_TMP`, so no protected-root overlap changes.

### P2 — degrade row (after line 1697, the unknown-flag check; before the protected block)

```bash
  # r16 C1: un-evaluable repo config degrades that repository to one `error`
  # row, leaves the run at exit 0, and leaves sibling repos untouched.
  local DEG="$ST_TMP/r16cfg/degraded-shokunin"
  local OKC="$ST_TMP/r16cfg/healthy-shokunin"
  local CYCO="$ST_TMP/r16cfg/cycle-shokunin"
  st_init "$DEG" master
  printf 'd\n' > "$DEG/d.txt"
  local g1
  g1=$(st_commit "$DEG" "" "deg")
  git -C "$DEG" update-ref refs/heads/master "$g1"
  git -C "$DEG" update-ref refs/remotes/origin/master "$g1"
  # ~user cannot be expanded by expand_config_path -> cfg_soft
  git -C "$DEG" config core.excludesFile '~nobody/ignore'
  st_init "$OKC" master
  printf 'h\n' > "$OKC/h.txt"
  local h1
  h1=$(st_commit "$OKC" "" "healthy")
  git -C "$OKC" update-ref refs/heads/master "$h1"
  git -C "$OKC" update-ref refs/remotes/origin/master "$h1"
  st_init "$CYCO" master
  printf 'c\n' > "$CYCO/c.txt"
  local y1
  y1=$(st_commit "$CYCO" "" "cycle")
  git -C "$CYCO" update-ref refs/heads/master "$y1"
  git -C "$CYCO" update-ref refs/remotes/origin/master "$y1"
  # self-include: written after the refs, so no later git call recurses
  git -C "$CYCO" config include.path "$CYCO/.git/config"
  local deg_rc deg_tsv="$ST_TMP/r16cfg.tsv" deg_err="$ST_TMP/r16cfg.err"
  set +e
  env -u GIT_DIR -u XDG_CONFIG_HOME HOME="$st_home" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$ST_TMP/r16cfg" >"$deg_tsv" 2>"$deg_err"
  deg_rc=$?
  set -e
  if [ "$deg_rc" = 0 ]; then st_ok "degrade: run exit 0"
  else st_bad "degrade: run exit=$deg_rc want 0"; fi
  v=$(st_row_field "$deg_tsv" degraded-shokunin 7)
  if [ "$v" = error ]; then st_ok "degrade: error row (git-config-unsupported)"
  else st_bad "degrade: verdict='$v' want error"; fi
  v=$(st_row_field "$deg_tsv" cycle-shokunin 7)
  if [ "$v" = error ]; then st_ok "degrade: error row (git-include-cycle)"
  else st_bad "degrade: cycle verdict='$v' want error"; fi
  v=$(st_row_field "$deg_tsv" healthy-shokunin 7)
  if [ "$v" = clean ]; then st_ok "degrade: sibling repo unaffected (clean)"
  else st_bad "degrade: sibling verdict='$v' want clean"; fi
  v=$(st_row_field "$deg_tsv" degraded-shokunin 6)
  if [ -z "$v" ]; then st_ok "degrade: mtime field empty"
  else st_bad "degrade: mtime='$v' want empty"; fi
  local dn
  dn=$(grep -c 'config-unsupported: git-config-unsupported' "$deg_err" || true)
  dn=${dn// /}
  if [ "${dn:-0}" = 1 ]; then st_ok "degrade: one config-unsupported line on stderr"
  else st_bad "degrade: $dn config-unsupported lines (want 1)"; fi
  dn=$(grep -c 'config-unsupported: git-include-cycle' "$deg_err" || true)
  dn=${dn// /}
  if [ "${dn:-0}" = 1 ]; then st_ok "degrade: include-cycle reason reported once"
  else st_bad "degrade: $dn include-cycle lines (want 1)"; fi
```

Optional add-on (pins that a degraded row is still `--compare`-loadable, `load_census`
1269-1300 accepts 7 columns with an empty mtime):

```bash
  set +e
  cmp_out=$(env -u GIT_DIR -u XDG_CONFIG_HOME HOME="$st_home" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$ST_TMP/r16cfg" --compare "$deg_tsv" 2>&1)
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 0 ] && [ "$cmp_out" = "$DIFF_HEADER" ]; then
    st_ok "degrade: degraded row compares clean against itself"
  else st_bad "degrade: compare rc=$cmp_st"; fi
```
(`cmp_out`/`cmp_st` are declared at 1629, i.e. before this block.)

### P3 — bound-filter skip (same insertion point, after P2)

```bash
  # r16 C1: a filter driver bound to a tracked path skips status for that
  # repository only, flags status-unverifiable, and never runs the driver.
  local FB="$ST_TMP/r16filt/filter-bound-shokunin"
  local FU="$ST_TMP/r16filt/filter-unbound-shokunin"
  st_init "$FB" master
  printf 'content\n' > "$FB/a.txt"
  printf '*.txt filter=evil\n' > "$FB/.gitattributes"
  local f1
  f1=$(st_commit "$FB" "" "bound")
  git -C "$FB" update-ref refs/heads/master "$f1"
  git -C "$FB" update-ref refs/remotes/origin/master "$f1"
  # configure the driver AFTER the commit: st_commit's `git add -A` would
  # otherwise run clean and trip the canary itself.
  git -C "$FB" config filter.evil.clean "echo ran >> $ST_TMP/filter-canary; cat"
  st_init "$FU" master
  printf 'content\n' > "$FU/u.txt"
  local u3
  u3=$(st_commit "$FU" "" "unbound")
  git -C "$FU" update-ref refs/heads/master "$u3"
  git -C "$FU" update-ref refs/remotes/origin/master "$u3"
  git -C "$FU" config filter.unbound.clean "echo ran >> $ST_TMP/filter-unbound-canary; cat"
  local fil_rc fil_tsv="$ST_TMP/r16filt.tsv" fil_err="$ST_TMP/r16filt.err"
  set +e
  env -u GIT_DIR -u XDG_CONFIG_HOME HOME="$st_home" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$ST_TMP/r16filt" >"$fil_tsv" 2>"$fil_err"
  fil_rc=$?
  set -e
  if [ "$fil_rc" = 0 ]; then st_ok "filter: run exit 0"
  else st_bad "filter: run exit=$fil_rc want 0"; fi
  v=$(st_row_field "$fil_tsv" filter-bound-shokunin 7)
  case "$v" in
    *status-unverifiable*) st_ok "filter: bound driver -> status-unverifiable ($v)" ;;
    *) st_bad "filter: bound verdict='$v'" ;;
  esac
  v=$(st_row_field "$fil_tsv" filter-bound-shokunin 4)
  if [ "$v" = 0 ]; then st_ok "filter: unverifiable dirty coerced to 0"
  else st_bad "filter: dirty='$v' want 0"; fi
  if [ ! -e "$ST_TMP/filter-canary" ]; then st_ok "filter: bound driver never ran"
  else st_bad "filter: bound driver ran (canary present)"; fi
  v=$(st_row_field "$fil_tsv" filter-unbound-shokunin 7)
  if [ "$v" = clean ]; then st_ok "filter: unbound driver inert (clean)"
  else st_bad "filter: unbound verdict='$v' want clean"; fi
  if grep -q 'status-skipped: filter-driver-bound' "$fil_err"; then
    st_ok "filter: status-skipped reported"
  else st_bad "filter: status-skipped missing from stderr"; fi
```

### P4 — XDG excludes (same insertion point, after P3)

```bash
  # r16 C1: the XDG default excludes file is honored when present and
  # boundary-clean; a different, relative, or absent XDG/HOME default is not.
  local XR="$ST_TMP/r16xdg/xdg-shokunin"
  st_init "$XR" master
  printf 'base\n' > "$XR/base.txt"
  local x1
  x1=$(st_commit "$XR" "" "xdg")
  git -C "$XR" update-ref refs/heads/master "$x1"
  git -C "$XR" update-ref refs/remotes/origin/master "$x1"
  printf 'noise\n' > "$XR/ignored.log"
  local xh="$ST_TMP/home-xdg"
  mkdir -p "$xh/.config/git" "$ST_TMP/xdg-empty"
  printf '*.log\n' > "$xh/.config/git/ignore"
  local xdg_rc xdg_tsv="$ST_TMP/r16xdg.tsv"
  set +e
  env -u GIT_DIR -u XDG_CONFIG_HOME HOME="$xh" SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$ST_TMP/r16xdg" >"$xdg_tsv" 2>/dev/null
  xdg_rc=$?
  set -e
  if [ "$xdg_rc" = 0 ]; then st_ok "xdg: run exit 0"; else st_bad "xdg: exit=$xdg_rc"; fi
  v=$(st_row_field "$xdg_tsv" xdg-shokunin 4)
  if [ "$v" = 0 ]; then st_ok "xdg: \$HOME/.config/git/ignore honored (dirty=0)"
  else st_bad "xdg: HOME ignore not honored (dirty=$v)"; fi
  set +e
  env -u GIT_DIR HOME="$xh" XDG_CONFIG_HOME="$ST_TMP/xdg-empty" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$ST_TMP/r16xdg" >"$xdg_tsv" 2>/dev/null
  xdg_rc=$?
  set -e
  v=$(st_row_field "$xdg_tsv" xdg-shokunin 4)
  if [ "$xdg_rc" = 0 ] && [ "$v" = 1 ]; then
    st_ok "xdg: XDG_CONFIG_HOME overrides \$HOME (dirty=1)"
  else st_bad "xdg: XDG override rc=$xdg_rc dirty=$v want 1"; fi
  set +e
  env -u GIT_DIR -u HOME -u XDG_CONFIG_HOME SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$ST_TMP/r16xdg" >"$xdg_tsv" 2>/dev/null
  xdg_rc=$?
  set -e
  v=$(st_row_field "$xdg_tsv" xdg-shokunin 4)
  if [ "$xdg_rc" = 0 ] && [ "$v" = 1 ]; then
    st_ok "xdg: unset HOME/XDG -> /dev/null (dirty=1)"
  else st_bad "xdg: unset HOME rc=$xdg_rc dirty=$v want 1"; fi
  set +e
  env -u GIT_DIR -u HOME XDG_CONFIG_HOME=relcfg SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$ST_TMP/r16xdg" >"$xdg_tsv" 2>/dev/null
  xdg_rc=$?
  set -e
  v=$(st_row_field "$xdg_tsv" xdg-shokunin 4)
  if [ "$xdg_rc" = 0 ] && [ "$v" = 1 ]; then
    st_ok "xdg: relative XDG_CONFIG_HOME -> /dev/null (dirty=1)"
  else st_bad "xdg: relative XDG rc=$xdg_rc dirty=$v want 1"; fi
```

Optional attributes leaf (pins `status_info_file`'s second key and its interaction with
P3's guard; add `xdg-attr-shokunin` with tracked `x.dat`, repo-local `filter.evil.clean`,
and `*.dat filter=evil` in `$xh/.config/git/attributes`; expect `status-unverifiable` in run
1 and `clean` in run 2):

```bash
  local XA="$ST_TMP/r16xdg/xdg-attr-shokunin"
  st_init "$XA" master
  printf 'dat\n' > "$XA/x.dat"
  printf '*.dat filter=evil\n' > "$xh/.config/git/attributes"
  local a2
  a2=$(st_commit "$XA" "" "xdg-attr")
  git -C "$XA" update-ref refs/heads/master "$a2"
  git -C "$XA" update-ref refs/remotes/origin/master "$a2"
  git -C "$XA" config filter.evil.clean "echo ran >> $ST_TMP/filter-canary; cat"
```
and assert, in run 1, `st_row_field ... xdg-attr-shokunin 7` contains `status-unverifiable`
and `[ ! -e "$ST_TMP/filter-canary" ]`; in run 2, verdict `clean`.

### P5 — `GIT_NO_LAZY_FETCH` (static half after line 1732; fixture half with P2-P4)

```bash
  # r16 C1: every child git sees GIT_NO_LAZY_FETCH=1, so promisor/partialClone
  # markers stay inert. A trace probe is impossible by design (startup clears
  # every inherited GIT_*), so assert the export and the accepted-marker row.
  if grep -q '^export GIT_NO_LAZY_FETCH=1$' "$SELF"; then
    st_ok "GIT_NO_LAZY_FETCH=1 exported"
  else
    st_bad "GIT_NO_LAZY_FETCH export missing"
  fi
  local PR="$ST_TMP/r16prom/promisor-shokunin"
  st_init "$PR" master
  printf 'p\n' > "$PR/p.txt"
  local p1
  p1=$(st_commit "$PR" "" "promisor")
  git -C "$PR" update-ref refs/heads/master "$p1"
  git -C "$PR" update-ref refs/remotes/origin/master "$p1"
  git -C "$PR" config remote.origin.promisor true
  git -C "$PR" config remote.origin.partialCloneFilter blob:none
  local prom_tsv="$ST_TMP/r16prom.tsv" prom_err="$ST_TMP/r16prom.err" prom_rc
  set +e
  env -u GIT_DIR -u XDG_CONFIG_HOME HOME="$st_home" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$ST_TMP/r16prom" >"$prom_tsv" 2>"$prom_err"
  prom_rc=$?
  set -e
  v=$(st_row_field "$prom_tsv" promisor-shokunin 7)
  if [ "$prom_rc" = 0 ] && [ "$v" = clean ]; then
    st_ok "promisor markers inert (exit 0, clean)"
  else st_bad "promisor: rc=$prom_rc verdict='$v'"; fi
  if [ ! -s "$prom_err" ]; then st_ok "promisor: no stderr diagnostics"
  else st_bad "promisor: stderr $(head -1 "$prom_err")"; fi
```

Honest scope note: this does **not** prove a lazy fetch is suppressed. `extensions.partialClone`
is deliberately omitted (it requires `core.repositoryformatversion=1`; adding it is only safe
if the local git accepts v1 + that extension — verify by execution before adopting). A true
fetch probe (missing object + reachable `file://` promisor) is possible but needs
`clone --filter` and object surgery inside a packfile; it is **not** proposed here because it
is fragile in a selftest and I could not execute it.

### P6 — redaction assertions (edit the existing blocks)

After line 1714 (`protected root` PASS/FAIL) and after line 1725 (`protected compare alias`):

```bash
  case "$prot_err" in
    *'(<protected>)'*) st_ok "protected root: path redacted" ;;
    *) st_bad "protected root: path not redacted" ;;
  esac
  if printf '%s' "$prot_err" | grep -qF "$ST_TMP/home/.omp"; then
    st_bad "protected root: store path leaked in stderr"
  else
    st_ok "protected root: no store path in stderr"
  fi
```

and, for the compare block, the same two checks with the label `protected compare alias`.
(Both refusals already take the redaction branch: `protected_fail` 185-188 sees
`$ST_TMP/home/.omp/agent[...]`, which `protected_reason_inside` (330-343) matches at the
`.omp`/`agent` component pair defined in `protected_component_reason` 314-316.)

### P7 — inherited `GIT_*` clear (after line 1655, before the mutation block)

```bash
  # The startup loop clears every inherited GIT_*; a bogus GIT_DIR must not
  # change the census. (out1 is still the pristine baseline here.)
  set +e
  env -u XDG_CONFIG_HOME HOME="$st_home" GIT_DIR="$ST_TMP/not-a-gitdir" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" >"$ST_TMP/gitdir-leak.tsv" 2>/dev/null
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 0 ] && cmp -s "$ST_TMP/gitdir-leak.tsv" "$out1"; then
    st_ok "inherited GIT_DIR cleared (identical output)"
  else
    st_bad "inherited GIT_DIR leaked (rc=$cmp_st)"
  fi
```

### P9 — optional: surface a failing baseline as a FAIL line

Replace the bare `out1`/`out2` invocations (source order 1518-1523) with:

```bash
  local base_rc
  set +e
  env -u GIT_DIR -u XDG_CONFIG_HOME HOME="$st_home" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" > "$out1" 2>"$ST_TMP/c1.err"
  base_rc=$?
  set -e
  if [ "$base_rc" = 0 ]; then st_ok "baseline run exit 0"
  else st_bad "baseline run exit=$base_rc"; head -3 "$ST_TMP/c1.err"; fi
```

## Acceptance-shape note

`run-matrix.py` parses `^selftest: (\d+) checks, (\d+) failed` (line 29; consumed at 106-112)
and records `selftest=<checks>/<failed>fail` (118). It does **not** hardcode a count, so
P1-P7 need no runner change — but they add 26 assertions (P2 7, P3 6, P4 5 (+1 optional),
P5 3, P6 4, P7 1), so C1's recorded `selftest=38/...` must be re-measured after integration;
the receipt will legitimately read a larger `checks` value. `bash -n`/`shellcheck` remain the
syntax gate (the selftest does not self-parse).

## What the selftest already covers (so the gap is not overstated)

Header contract, four-repo row set, dot-dir/plain-dir/linked-worktree exclusion, clean/dirty/
unpushed/no-remote/wt-absent/wt-dirty flags, scratch bytes, secret-shaped exclusion, secret
and `.ufo` content non-leakage, mtime ISO shape and forbidden-surface pruning, byte-identical
repeat runs, `--compare` self/mutation/trailing-blank/malformed baselines, unknown flag exit
2, protected `--root` and `--compare` alias exit 2 (both before access), and the
forbidden-git-subcommand source audit (1727-1732). The five r16 behaviors above are the
entire remainder of C1's contract and none is touched.

## Residual risk / verification gaps (stated, not hidden)

- **Every proposed block is unexecuted.** This seat was "source inspection; no execution";
  I did not create fixtures or run the census (allowed commands only). Each block was traced
  against the exact function it drives: P2 → 555-558/579-585/619-625/1086-1091; P3 →
  907-943; P4 → 874-900; P5 → 147 + 1184-1211; P6 → 184-191/302-325/330-343; P7 → 126-133.
- P2's include-cycle repo relies on `git config include.path` accepting a self-reference at
  write time (the cycle is created by the write). If a target git refuses to write it, use
  `printf '[include]\n\tpath = %s\n' "$CYCO/.git/config" >> "$CYCO/.git/config"` instead.
- P3's canary ordering is load-bearing: configuring `filter.evil.clean` before `st_commit`
  would let `git add -A` execute it and create the canary from the fixture, not the census.
- P4 run 3 (`-u HOME`) exercises 886; run 4 (`XDG_CONFIG_HOME=relcfg`) exercises 890-893.
  Both expect `dirty=1`; if git's own `HOME` handling changes, the assertion still holds
  because the census neutralizes global config (`GIT_CONFIG_GLOBAL=/dev/null`, 143-145).
- P5 cannot prove fetch suppression; it proves the export and marker inertness only (see the
  note in P5). The existing forbidden-subcommand audit already forbids an explicit `git fetch`.
- F1's fix (P1) changes fixture `HOME`; the protected tests keep their own `HOME` and must not
  inherit `$st_home` (their refusal depends on `$ST_TMP/home/.omp/agent`).
- Not investigated here (out of item scope): the four arm fixtures
  `tests/fixtures/r15-census-config.py`, `tests/fixtures/r14-census-boundary.py`, the matrix
  runner's arm accounting, and the new `tools/souji-landing-gate.py` (C2). No claim is made
  about them.

STATUS: none — no failing check; this seat executed no census, no fixture, and no test, so
no run result is asserted. The gate weakness reported here is source-read evidence.

## Compliance

- Read only `tools/souji-census.sh` at `cbf688a` via `git show`, plus
  `census/round-16/run-matrix.py` (grep) and two sibling reports in this wave directory.
- No census run, no copy of the tool executed, no fixture created, no `/var/tmp` git repo,
  nothing under `census/operator-sweep-20261019/`, `~/.omp`, `.ufo/state`,
  `.ufo/watchdog.log`, `MANIFEST.json` or sibling lanes was opened.
- One scratch copy of the blob was written to `/var/tmp/r16lss-census.sh` for line-numbered
  reading and has been deleted (see Commands); no lane path was touched.
- `tools/souji-census.sh` was **not** edited; this report is the only file written.

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'run_selftest\|^selftest\|--selftest'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'XDG\|GIT_NO_LAZY_FETCH\|fsmonitor\|hooksPath\|alternateRefsCommand\|promisor\|partialClone\|redact\|REDACT\|degrade\|could-not-evaluate\|error'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/r16lss-census.sh && sed -n '1420,1700p' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '860,1000p' /var/tmp/r16lss-census.sh 2>/dev/null || git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '860,1000p'
cd /home/vgpnk/Projects/shokunin && sed -n '1700,1784p' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin && sed -n '1,160p' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin && sed -n '500,700p' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin && sed -n '1040,1160p' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin && grep -n 'protected>\|protected_fail()\|protected_reason_input()\|guard_git_surface()\|sanitize_field()\|st_init()\|st_commit()\|st_ok()\|st_bad()\|st_note()\|ST_PASS\|ST_FAIL' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin && sed -n '380,500p' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin && sed -n '755,860p;1391,1432p' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin && sed -n '176,205p;340,380p' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin && awk 'NR>=1432 && NR<=1745' /var/tmp/r16lss-census.sh | grep -n 'config-unsupported\|status-skipped\|status-unverifiable\|<protected>\|XDG\|GIT_NO_LAZY_FETCH\|filter\|promisor\|partialClone\|excludesFile\|attributesFile\|core.worktree\|worktreeConfig' ; echo "---exact anchors---"; grep -n 'count_dirty()\|guard_bound_filters()\|status_info_file()\|census_one()\|^run_selftest()\|source audit\|no forbidden git subcommand\|protected root refused\|protected compare alias' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin && grep -n 'XDG_CONFIG_HOME\|HOME=' /var/tmp/r16lss-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'config-unsupported: %s\|status-skipped: filter\|env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1\|export GIT_NO_LAZY_FETCH\|shown=<\|shown=.protected\|tgt="$base/git\|guard_bound_filters "\$1"\|printf .unverifiable.\|CFG_SOFT_REASON:-git-config\|flat\|readonly'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '1084,1100p;1727,1735p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '995,1045p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '250,346p'
for f in /home/vgpnk/.config/git/ignore /home/vgpnk/.config/git/attributes; do if [ -e "$f" ]; then printf '%s: EXISTS\n' "$f"; else printf '%s: absent\n' "$f"; fi; done; printf 'HOME=%s XDG_CONFIG_HOME=%s\n' "$HOME" "${XDG_CONFIG_HOME:-unset}"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'guard_worktree_registrations()\|^build_protected_roots\|build_protected_roots()\|homes='
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '241,256p;715,760p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -8 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '874,900p;935,960p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '1690,1745p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '1160,1250p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '1600,1665p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '1432,1450p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '1250,1330p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '1556,1585p;1416,1432p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '555,640p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'selftest\|checks\|38\|failed' census/round-16/run-matrix.py | head -40
rm -f /var/tmp/r16lss-census.sh; ls -l /var/tmp/r16lss-census.sh 2>&1; ls -l /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/RevLegacySelftestGap.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'passwd_home()' -A 14
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '300,345p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | cat -n | sed -n '905,935p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n '|| return 1\|guard_wt_config()\|guard_git_config()\|guard_alternates()\|guard_worktree_registrations "\$dir"'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '1618-1623\|578-585\|1520-1523' .ufo/waves/round-16/w1/RevLegacySelftestGap.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '907-933\|907-943' .ufo/waves/round-16/w1/RevLegacySelftestGap.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -i 's/`guard_bound_filters` 907-933;/`guard_bound_filters` 907-932;/; s/`guard_bound_filters` (907-933) finds/`guard_bound_filters` (907-932) finds/' .ufo/waves/round-16/w1/RevLegacySelftestGap.md && grep -n '907-932\|907-933\|907-943' .ufo/waves/round-16/w1/RevLegacySelftestGap.md
```

Two disclosures on method:

- The single `sed -i` above was the one shell-based in-place edit of this report (normalizing
  a line-number citation); every other report change used the `edit` tool, and the result was
  re-grepped immediately (same command). It touched only this report, never the tool.
- The `/var/tmp/r16lss-census.sh` scratch copy of the blob was created in my third command for
  line-numbered reading and removed by the `rm -f` above; no lane file, fixture, or census
  run was involved.

Other evidence came from `read`/`grep`/`glob`-class tool calls on exact named files
(`tools/souji-census.sh` at `cbf688a`, `census/round-16/run-matrix.py`,
`.ufo/waves/round-16/w1/` directory listing, `SrcGitignoreXdg.md`, `SrcGitStatusRejected.md`)
and from this seat's writes to this report; no further shell commands were run, and no
verification command was executed against `tools/souji-census.sh`.
