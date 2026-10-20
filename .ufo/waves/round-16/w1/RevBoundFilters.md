# RevBoundFilters — source review of `guard_bound_filters` (tools/souji-census.sh @ cbf688a)

Seat: SoujiR16.RevBoundFilters (reviewer, read-only). Asked: review `guard_bound_filters`
(`config -z --get-regexp` record parsing, empty-value skip, dotted filter names,
`ls-files -z --cached | check-attr -z --stdin filter` triple parsing, macro attributes, and
whether status could still run a driver for an untracked or unbound path).

- Target: `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
  (blob `ea05ba722bed6d3dc71003b934ab00b899ea8127`, sha256
  `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`, 1784 lines).
- Method: source inspection only (no execution of the census; no fixture run). Shell checks:
  `bash -n` and `shellcheck -S warning` on a `/var/tmp` copy of the blob.
- Git-side semantics verified against git v2.47 sources (`builtin/config.c`, `config.c`,
  `builtin/check-attr.c`, `convert.c`) rather than from memory; line cites below are v2.47.
- Working-tree state at review time: HEAD is cbf688a and `tools/souji-census.sh` carries an
  uncommitted, still-changing patch — 135 insertions/68 deletions when this seat measured it,
  138/68 when a peer measured it later; treat the count as a snapshot, not a property. It
  contains a config-scan `soft=1` rewrite plus a `pid=$!`/`wait` variant of the D3 fix, and this
  seat did not author it — this seat edits only this report. All line anchors below are committed
  cbf688a bytes; apply any patch by quoted text, not by line number, if the dirty tree is kept.

## Verdict

**Changes requested for D1 and D2.** The function is correct for the mechanisms named in the
brief except two real defects in its own classification, plus one fail-open hardening gap and
one stale comment. Recommend D1/D2 patched before acceptance; D3 is a cheap guard-direction fix.

| id | severity | one line |
|----|----------|----------|
| D1 | MEDIUM | a filter value that ends in a newline is classified "empty value" → driver not registered → status runs it |
| D2 | MEDIUM | `.git/info/attributes` is never type/hardlink-screened although the guard's own `check-attr` and `git status` both read it |
| D3 | LOW | the binding check fails open when `ls-files`/`check-attr` fails (mapfile cannot see the producer status) |
| D4 | LOW (comment) | function comment says "refuse"; behavior is per-repo status skip (header is right) |
| O1 | observation | guard set is not restricted to the status pathspec, so a binding only on an excluded surface over-skips (within the documented contract) |

`STATUS: no check this seat ran failed — bash -n cbf688a rc 0, shellcheck -S warning cbf688a rc 0 (0 findings), b410186 bash -n rc 2 at line 1368 (expected r15 arm, consistent with C1). D1/D2 are unpatched defects in the reviewed revision.`

## D1 — MEDIUM — trailing newline in a filter value is treated as "explicitly empty"

**Where:** `tools/souji-census.sh:913-914` (inside the driver harvest, 910-919).

```
913    # An explicitly empty value (`key\n`) defines no command.
914    case "$rec" in *$'\n') continue ;; esac
```

**Why it is wrong:**

1. `git config -z` prints `key\n<value>\0` per record; the key/value delimiter is `\n` and the
   record terminator is NUL (`builtin/config.c` v2.47:823-825 sets `term='\0'`, `delim='\n'`;
   `show_config` at 244-247 is `printf("%s%c%s%c", key_, delim, value_, term)` when a value is
   present, and `printf("%s%c", key_, term)` only when the value is NULL/bare). So *every*
   record whose value ends in a newline ends in `'\n'` — not only the empty-value records.
2. A config value may legitimately end in a newline: a double-quoted value decodes the `\n`
   escape (`config.c` v2.47 `parse_value`, `case 'n': c = '\n';` at 870-872). Unquoted values
   have trailing whitespace trimmed; a decoded newline inside quotes is preserved.
3. git executes a clean/smudge/process command for any non-empty stored string:
   `convert.c` v2.47 `apply_filter` 1008-1019 — `if (cmd && *cmd) apply_single_file_filter(...)`
   / `else if (drv->process && *drv->process) apply_multi_file_filter(...)`. There is no
   trailing-newline trim.
4. Therefore `[filter "x"] clean = "cmd\n"` yields the record `filter.x.clean\ncmd\n`; line 914
   matches `*$'\n'`, `drivers` stays empty, line 920 returns 0, and `count_dirty`
   (947-953) runs `git status`, which executes `cmd` for a stat-dirty tracked path bound by
   `.gitattributes`. This falsifies the header promise at lines 98-100 ("the driver never runs")
   and the fixture's round-16 safety property (R15CFG-14).
5. It is a regression from the r15 candidate's equivalent test, which classified by the value:
   `b410186:737-742` rejects a valueless key and then does `if [ -n "$v" ]; then
   CFG_DRIVERS+=("$sub"); fi` — a trailing-newline value would have been registered there.
   Two caveats on that precedent: `b410186` does not parse (`bash -n` stops at line 1368), so it
   is source-shape only, not a runnable baseline; and its consumer degraded differently —
   `b410186:1287-1291` maps `unsupported|checkattr-fail` to `dirty=0` plus the `error` flag, a
   per-repository degrade, not a whole-run refusal. r16's silent inert classification is weaker
   than either arm.

Not affected: a value that is exactly empty is correctly inert (record is `key\n`, value part
`${rec#*$'\n'}` = ""), and a bare key (record `key`, no newline) is conservatively kept as a
driver (git prints "missing value" and runs nothing — over-skip only).

**Minimal patch** (replace 913-914; 915-917 and the loop stay):

```bash
    # An explicitly empty value (`key\n`) defines no command; a value that
    # merely ends with a newline is a real command (git runs any non-empty
    # string: convert.c apply_filter only requires `cmd && *cmd`).
    case "$rec" in
      *$'\n'*)
        [ -n "${rec#*$'\n'}" ] || continue
        ;;
    esac
```

**Fixture gap / proposed case:** extend R15CFG-14 with a third repo whose config is written as
`[filter "x"]\n\tclean = "<sentinel>\\n"\n` (literal trailing newline in the value, sentinel
script) and whose `.gitattributes` binds `filter=x` on a tracked, stat-dirty file. Expected:
row `status-unverifiable`, `status-skipped` on stderr, sentinel absent. Today that case would
show the driver ran.

## D2 — MEDIUM — `$GIT_DIR/info/attributes` is read by the guard and by status, but never screened

**Where:** `tools/souji-census.sh:505` (`guard_git_files` fixed-metadata list), against the
documented claim at 501-502 and the consumers at 922-925 (`check-attr`) and 949 (`status`).

```
505    for rel in config HEAD index packed-refs commondir info/exclude objects/info/alternates; do
```

`info/attributes` is missing. It is the highest-precedence attributes source
(`gitattributes(5)`: `$GIT_DIR/info/attributes`, then `.gitattributes`, then
`core.attributesFile`, then the system file) — i.e. exactly the file that decides whether
`filter` is bound, which is the question `guard_bound_filters` is asked.

Current screening coverage for that path:

- symlinks: covered (`guard_git_links` 484-499 refuses a link resolving outside the gitdir);
- FIFO/device/socket: **not covered** — `guard_git_files` only refuses non-regular *existing*
  paths for the names in its list, so a FIFO here is opened by the guard's own `check-attr`
  (922-925) and by `status` (949); open-for-read on a FIFO blocks until a writer appears, so
  the census hangs. This contradicts 501-502 ("a FIFO/device/socket is refused rather than
  opened or waited on");
- hardlink: **not covered** — `nlink > 1` is refused for the listed names (512-514), but a
  hardlinked `info/attributes` is read; hardlink refusal is the documented residual mitigation
  for boundary aliases (header 115-119), so the omission matters for the boundary claim.

**Minimal patch** (one word at 505):

```bash
  for rel in config HEAD index packed-refs commondir info/exclude \
             info/attributes objects/info/alternates; do
```

**Fixture gap:** the fixture covers a FIFO only as an *include target*
(`tests/fixtures/r15-census-config.py:470-471`, `r-inc-fifo`). Proposed case: `.git/info/attributes`
as a FIFO (run under a short timeout) and as a hardlink to a file inside the synthetic store;
both must refuse (`git-metadata-nonregular` / `git-metadata-hardlink`), never open.

## D3 — LOW — the binding check fails open when the producer fails

**Where:** `tools/souji-census.sh:922-925`; consequence at 926-930/931.

```
922    mapfile -d '' -t recs < <(git -C "$wt" -c core.attributesFile="$attrs" \
923        ls-files -z --cached 2>/dev/null \
924      | git -C "$wt" -c core.attributesFile="$attrs" \
925        check-attr -z --stdin filter 2>/dev/null || true)
```

`mapfile` from a process substitution cannot observe the pipeline status, and `2>/dev/null ||
true` discards the errors. If `ls-files` or `check-attr` fails and emits nothing (or stops
mid-record), `recs` is empty/short, the stride loop at 926 finds no match, and the function
returns 0 — status then runs as if no driver were bound. Observed impact is narrow (most of the
same failure modes also make status fail, giving `unverifiable` at 953-955), but this is the only
input to the guard that fails open, and the r15 candidate propagated producer failure
(`b410186:1086-1097`: `if ! bound=$(... | awk ...)` under the global `pipefail` →
`checkattr-fail`).

Note for reviewers who propose dropping the `|| true` tokens: that alone does **not** change
behavior (the status is still unobservable through `mapfile`, and stderr is already redirected).
The producer status must be carried in the stream.

A `pid=$!` + `wait "$pid" || return 1` variant (the BCS process-substitution exit-capture idiom,
BCS-Bash-Ref §5.7) also closes the fail-open when `set -o pipefail` is inside the substitution:
`wait` then returns the producer status, and a legitimately empty index still exits 0. Its one
assumption is that `$!` is the substitution's PID in the target bash. If `$!` is empty or stale,
`wait` fails with 127 and the guard returns 1 for **every** repo that defines any
`filter.<n>.{clean,smudge,process}` key — not only bound ones — converting accurate rows to
`status-unverifiable`. Verify that property in the target bash before relying on it; the
sentinel/parity patch above has no such dependency.

**Minimal patch** (replace 921-926):

```bash
  recs=()
  mapfile -d '' -t recs < <(
    set -o pipefail
    git -C "$wt" -c core.attributesFile="$attrs" ls-files -z --cached 2>/dev/null \
      | git -C "$wt" -c core.attributesFile="$attrs" check-attr -z --stdin filter 2>/dev/null \
      || printf 'guard-check-failed\0'
  )
  # path\0attr\0value\0 triples; a failed producer or a short record is not
  # evidence that no driver is bound.
  if [ $(( ${#recs[@]} % 3 )) -ne 0 ]; then
    return 1
  fi
  for ((i = 2; i < ${#recs[@]}; i += 3)); do
```

The zero-tracked-file case stays `0 % 3 == 0` and still runs status (fixture repos with no
commits depend on that). The sentinel lands in a path slot, so the parity check — not the
membership loop — is what catches it.

## D4 — LOW (comment accuracy) — "refuse" vs per-repo skip

`tools/souji-census.sh:904-905` says the bound driver "could run during status: refuse (round
16)". The behavior, and the accurate header prose, is a per-repository skip: 939-944 print
`status-skipped` and return `unverifiable`, `census_one` turns that into `dirty=0`,
`status-unverifiable`, exit 0 (1134-1136). Independently noted by SoujiR16.SimplifyCensusDiff.

Patch line 905: `# could run during status: skip status for this repository only (round 16).`

## Verified clean (no defect) — the brief's checklist

1. **`config -z --get-regexp` record parsing.** Exact. Records are `key\n<value>\0`
   (`builtin/config.c`:823-825, 244-247). A key can never contain `\n`: `git_config_parse_key`
   rejects a newline in the extended basename (`config.c`:592-595) and every key printed has
   gone through `config_parse_pair` → `git_config_parse_key`. So the first newline is always the
   delimiter, and 915's `${rec%%$'\n'*}` is exact. Values *containing* newlines do not break the
   split; only a value's final character affects the (defective) D1 test.
2. **Empty-value skip (value exactly "").** Semantically right: git runs nothing for an empty
   command string (`convert.c`:1008-1019). `filter.X.process = ""` also disables `clean`; the
   function registers such a driver anyway (over-skip, conservative) — not a defect.
3. **Filter names containing dots.** Correct, and matches git. `parse_config_key` splits at the
   *last* dot (`config.c`:3747-3764, `strrchr`), so a driver name may contain dots; 916-917
   strip the first dot (`filter.`) and the last dot (`.clean|smudge|process`), producing exactly
   the name `read_convert_config` stores (`convert.c`:1034-1044). No missed driver is possible;
   at worst an unreachable dotted name over-skips.
4. **`ls-files -z --cached | check-attr -z --stdin filter` triple parsing.** Correct.
   `check-attr -z` writes `path\0attrname\0attrvalue\0` (`builtin/check-attr.c`:50-55), and `-z`
   also makes `--stdin` input NUL-separated (`check-attr.c`:28-30, 89). The stride-3 loop from
   index 2 reads the value field only. Paths with newlines/spaces are safe under `-z`; a path
   starting with `-` cannot become an option under `--stdin`.
5. **Macro attributes.** No divergence. `check-attr` resolves `[attr]` macros with the same
   attribute engine status uses, so a path bound to `filter=x` through a macro reports `x` and
   matches. Both commands read the same source stack in the same precedence order
   (`$GIT_DIR/info/attributes`, the worktree `.gitattributes` chain, `core.attributesFile` or
   its XDG default, then the system attributes file — the last is read by both because line 140
   unsets every inherited `GIT_*`, including `GIT_ATTR_NOSYSTEM`). Macro definition-placement
   rules are identical too, so the guard cannot see a binding that status would not.
6. **Untracked path.** Cannot run a driver. `git status` converts only index entries whose stat
   data no longer matches (`index_fd` → `convert_to_git`); untracked paths are listed, not
   hashed (`--ignore-submodules=all` removes the submodule recursion as well). The guard's
   `ls-files --cached` set is exactly the set status can hash — the brief's question is
   therefore "no", and no extra untracked enumeration is needed.
7. **Unbound path.** Cannot run a driver. `convert_attrs` yields no driver when the attribute
   value names no `filter.<name>` config, and `apply_filter` returns 0 for `!drv`
   (`convert.c`:1008-1019).
8. **Driver set == what the scan guarded.** `git -C "$wt" config` reads the same includes and
   `config.worktree` that `scan_config_file` (579-650) and `guard_wt_config` (654-665) walk;
   global/system config is `/dev/null` (143-144) and inherited `GIT_*` (including
   `GIT_CONFIG_COUNT`) is unset (140). Includes whose condition does not match are still
   scanned, so the set is a superset — over-skip only, never a miss.
9. **Attributes file identity.** `status_info_file` (874-902) hands the guard the same
   `core.attributesFile` (or XDG default, or `/dev/null`) that status is forced to use via
   `-c core.attributesFile="$at"` (949); the relative-path base is the worktree for both because
   both git calls run with `-C "$wt"`. The guard cannot inspect a different file than status
   reads.

## Residual risk / verification gaps

- D1 and D2 have **no fixture coverage**: R15CFG-13/14 use plain values
  (`tests/fixtures/r15-census-config.py:498-513, 633-643`), and the FIFO case at 470-471 is an
  include target, not `info/attributes`.
- The guard is a point-in-time check: config/attributes can change between `check-attr` and
  `status`; same non-atomic residual the header already states (115-119).
- Worktree `.gitattributes` itself is not boundary-screened: a tracked or untracked attributes
  file that is a symlink out of the repo is opened by `check-attr` and by `status`. Only
  attribute text is consumed and no census field carries it, so I do not count it as a defect,
  but it is a read the header's residual (status "may read or hash tracked content") does not
  name.
- O1 (observation, not a defect): `ls-files` at 923 has no pathspec excludes, unlike status at
  950-953, so a filter bound only on `.ufo/state`, `.ufo/watchdog.log`, or
  `census/operator-sweep-*` skips status although status would never touch those paths (r15 had
  the excludes, `b410186`:1086-1090). This matches the header's wording ("a tracked path"), so
  it is contract-consistent; tightening it would only convert a few false
  `status-unverifiable` rows into accurate counts.
- Not in scope / not executed here: any real-directory census, the fixture matrix, and round
  acceptance (L1).

## Commands

Every shell command this seat ran, verbatim (`R=/home/vgpnk/Projects/shokunin/souji-shokunin`;
the `git show …` selectors are the named revisions/paths only):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | nl -ba | sed -n '1,120p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse cbf688ab2ab28e38103e5a9417ca525b5f2ed423; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -5 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'guard_bound_filters\|config -z\|check-attr\|ls-files\|filter\.'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | nl -ba | sed -n '760,1010p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | nl -ba | sed -n '380,620p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | nl -ba | sed -n '620,762p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | nl -ba | sed -n '1,200p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | nl -ba | sed -n '120,380p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n 'filter\|FILTER'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | nl -ba | sed -n '1400,1620p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | nl -ba | sed -n '1040,1152p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | nl -ba | sed -n '1010,1042p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | nl -ba | sed -n '480,530p;625,672p;1205,1255p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | nl -ba | sed -n '1150,1400p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'status --porcelain\|count_dirty\|ls-files\|check-attr\|git -C' | sed -n '1,80p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n 'mkfifo\|fifo\|info/attributes\|attributesFile\|\.gitattributes' | sed -n '1,40p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | nl -ba | sed -n '500,520p'
for r in cc21683 b410186 cbf688a; do echo "=== $r ==="; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show $r:tools/souji-census.sh | nl -ba | sed -n '/^ *[0-9]*.guard_bound_filters()/,/^ *[0-9]*}/p'; done
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | nl -ba | sed -n '536,575p'
for r in cc21683 b410186; do echo "=== $r ==="; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show $r:tools/souji-census.sh | grep -n 'filter' | sed -n '1,40p'; done
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-census.sh | bash -n; echo "b410186 bash -n rc=$?"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/r16-census-review.sh && bash -n /var/tmp/r16-census-review.sh; echo "cbf688a bash -n rc=$?"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-census.sh | nl -ba | sed -n '1060,1125p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-census.sh | nl -ba | sed -n '725,745p'
bash -n /var/tmp/r16-census-review.sh && echo "parse ok"; shellcheck -S warning /var/tmp/r16-census-review.sh > /var/tmp/r16-shellcheck.out 2>&1; echo "shellcheck rc=$?"; wc -l /var/tmp/r16-shellcheck.out; grep -n 'guard_bound_filters\|SC2[0-9]*\|mapfile\|process substitution' /var/tmp/r16-shellcheck.out | sed -n '1,20p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-census.sh | nl -ba | sed -n '700,724p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse cbf688ab2ab28e38103e5a9417ca525b5f2ed423^{tree} cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh
rm -f /var/tmp/r16-census-review.sh /var/tmp/r16-shellcheck.out && ls /var/tmp/r16-census-review.sh /var/tmp/r16-shellcheck.out 2>&1 | sed -n '1,4p'
grep -n 'Macro attributes' -A 6 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/RevBoundFilters.md
grep -n '273-275\|592-603\|1022-1046\|823-825' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/RevBoundFilters.md
grep -n 'rm -f /var/tmp/r16' -A 3 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/RevBoundFilters.md; tail -5 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/RevBoundFilters.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --numstat -- tools/souji-census.sh; git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff -- tools/souji-census.sh | grep -n 'pid=\$!\|wait \|soft=1\|+.*soft' | sed -n '1,25p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-census.sh | nl -ba | sed -n '1278,1296p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff -- tools/souji-census.sh | grep -n 'pid=\|wait\b\|guard_bound_filters\|check-attr\|mapfile' | sed -n '1,40p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff -- tools/souji-census.sh | grep -c '^+'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat -- tools/souji-census.sh
```

Non-shell source reads (tool-based). Git v2.47 `builtin/config.c`, `builtin/check-attr.c`,
`config.c`, `convert.c` at `https://raw.githubusercontent.com/git/git/v2.47.0/<file>` via
`read`/`grep`, to confirm the `-z` record format, the `\n` value escape, config-key newline
rejection, the last-dot `parse_config_key` split, `check-attr -z` field order, and
`apply_filter`'s non-empty-command rule. For the `$!` note in D3: bash source was not reachable
from this host (`bminor/bash` `bash-5.2/subst.c` and `master/subst.c` → HTTP 404,
`git.savannah.gnu.org` cgit plain → HTTP 502), so the idiom is cited from the Bash Coding
Standard §5.7 (`https://github.com/Open-Technology-Foundation/bash-coding-standard/blob/main/docs/BCS-Bash-Ref/05_Expansions/07_Process-substitution.md`:
"capture the PID via `$!` immediately after the substitution and `wait` on it") and the GNU
Special Parameters page surfaced by `web_search` for "bash process substitution `$!` PID"; the
caveat in D3 is stated as a required verification, not as an observed failure. One further
tool read for integration advice exchanged with SoujiR16.SimplifyCensusDiff (not load-bearing for
any finding here): bash(1) `mapfile` states "If not supplied with an explicit origin, mapfile will
clear array before assigning to it" (man7 bash.1, mapfile section), which settles that seat's A4
deletion; the GNU bash manual page fetched for the same check returned no matching text. No tool
was installed or upgraded for this review.
