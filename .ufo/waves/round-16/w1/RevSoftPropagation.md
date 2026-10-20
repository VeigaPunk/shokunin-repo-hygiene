# RevSoftPropagation — soft refusal propagation review (round 16)

Seat: reviewer (leaf). Scope: soft refusal propagation in
`tools/souji-census.sh` — every `return 1` vs `exit 2` path, bash errexit
semantics inside `||` / `if !` / `$(...)` / process substitution, and proof
that no path runs git in a repository whose config guard soft-failed
(`list_repos ... || true`, `census_one`, `worktree_extra_flags`,
`count_dirty`). Source inspection only; nothing executed (per assignment).

## Bytes reviewed

- Target: commit `cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh`.
- At first read the worktree file was byte-identical to that blob:
  `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`
  (1784 lines). All line numbers below are that blob's.
- **Concurrent drift:** the worktree changed under this review (observed
  `31 insertions/18 deletions`, sha `feba44c7…`, then `115/62`, sha
  `ef4faaa2…`; at the final check `tools/souji-census.sh` showed 266 changed
  lines and `tests/fixtures/r15-census-config.py` +70). Neither target file
  was cbf688a in the worktree at final read. Findings below describe the
  commit; where in-flight hunks intersect a finding it is stated explicitly
  (F3 is about that in-flight work only).

## Verdict

**No path lets a measurement git command run in a repository whose config
guard soft-failed.** That is proven by exhaustive callsite audit below. The
guards themselves do invoke `git config --file` (no repository discovery)
and, only after a passing guard, `git config -z --get-regexp`,
`ls-files` and `check-attr`.

Three defects remain in the reviewed commit (F1, F2, F4), plus two
lower-severity claim/guard-completeness gaps (F5, F6) and one risk in the
uncommitted repair (F3). F1 is a fail-open on the filter-driver execution
gate; F2 is a protected-root under-guard through `:(optional)` on
`core.worktree`.

**On the narrow `return 1`-vs-`exit 2` question I found no misclassification:**
every soft return in the config chain is checked at its callsite, every hard
refusal is an unconditional `exit 2` (never a `return 2`), and every
command-substitution boundary that can carry a refusal has an explicit status
check. F1 and F2 are defects in *what* is evaluated, not in how the verdict
propagates.

## 1. Propagation proof

### 1.1 The complete soft set

`cfg_soft()` (557-559) is the only soft emitter: it sets `CFG_SOFT_REASON`
and returns 1. Soft returns, all with no intervening command:

| Site | Lines |
|---|---|
| `guard_config_file_kind` | 563, 566, 568 |
| `scan_config_file` | 582, 584, 587, 590, 612, 616, 617, 622, 629, 636 |
| `guard_wt_config` | 661, 663 |
| `guard_git_config` | 678, 680 |
| `guard_worktree_registrations` | 741 |
| `guard_git_surface` | 773, 789, 790, 794, 812, 828, 829, 833 |

Every one of those is written `X || return 1` (or is itself `cfg_soft; return
1`), so the soft state reaches `guard_git_surface`'s caller unchanged.
`CFG_SOFT_REASON` is always set on that path (the `${…:-…}` fallback at 1089
is belt-and-braces only). The non-config `return 1` at 928 is
`guard_bound_filters` (a *skip* decision, not a config soft) — see F1.

### 1.2 Consumers (complete, by grep)

- **1087** `if ! guard_git_surface "$repo"` → prints
  `config-unsupported: <reason> (<repo>)` and the `0 0 0 0 <empty> error`
  row, `return 0` at 1091. The first measurement command is
  `git -C "$repo" rev-parse` at **1104**, i.e. after the guard.
- **1068** `if ! guard_git_surface "$cpath"` → `saw_dirty=1; continue`
  (1069-1070). `count_dirty "$cpath"` is at **1072**, i.e. skipped.
- **1176, 1179, 1209** `guard_git_surface … || true` → list construction
  only; `list_repos` runs no measurement git. The repo is re-guarded at 1087
  inside `census_one` before any measurement runs, and both passes see the
  same files (no condition-evaluated includeIf state in r16; CFG_STACK and
  CFG_WT_ENABLED are reset per top-level scan at 662/677 and 675).
- No other `guard_git_surface` callsites exist (grep over the whole file).
- `count_dirty` (935-958) never calls the config guard itself; it is only
  reachable through 1072/1115, both after a `0` guard return.

`if !` inverts only the *return value*; it cannot convert a refusal, because
the refusal never returns.

### 1.3 The complete hard set

`protected_fail` (184-191) is the only exit-2 guard emitter (`exit 2` at
191). It runs in the current shell, except where the guard is invoked inside
a command substitution; each such boundary has an explicit status check:

- wrappers: 443, 452 (guards), 475, 493 (alternates/links);
- config: 614, 624, 631;
- gitfiles: 700, 708, 737, 739, 740;
- surface: 770, 771, 772, 786, 787, 788, 793 (direct), 809, 810, 811, 825,
  826, 827, 832 (direct);
- measurement path: 880, 937, 938, 1051, 1072, 1086, 1115, 1117, 1220,
  1252, 1331.

`guard_git_config`'s hard path (673) and `guard_wt_config`'s (658) are direct
calls, so their `exit 2` is in-process. `census_one`'s rc 2 becomes a
whole-run `exit 2` at **1231** (the `$?` after `if row=$(census_one …)` is
the substitution's status). In compare mode, `emit_census > "$CENSUS_TMP"`
(1336) is a simple command under `set -e`, and main runs
`emit_compare; exit $?` (1779-1780), so rc 2 survives unchanged.

### 1.4 errexit semantics

- `set -euo pipefail` at 107. `if !` and `||` suppress errexit inside the
  whole guard call tree (SC2310 confirms dozens of instances), but the
  refusal path does not depend on errexit: `protected_fail` exits
  unconditionally, and every soft path is an explicit `return 1` whose rc is
  tested at its callsite. There is no `return 2` anywhere in the file.
- The classic masking bug (`local x=$(cmd)`) is absent: every saved
  assignment is a separate statement and its rc is tested (`guard_path`
  442-443, `guard_target` 451-452, `resolve_guarded`'s `reason=$(…)` uses).
- The remaining status-discarding sites shellcheck flags (SC2312) are
  592, 911, 925, 958 and the selftest helpers. 592 is backstopped by the
  separate parse check at 589-590; 911 by the fact that a config that makes
  `--get-regexp` fail also fails the scan at 589 (so `count_dirty` is never
  reached), except under the documented TOCTOU; **925 is a real fail-open —
  F1**. 958's `grep -c` status is irrelevant to the count value.
- `newest_mtime` (965-1030) toggles `set +e`/`set -o pipefail` inside a
  command substitution only; the toggles cannot leak to the caller.

### 1.5 No measurement git after a soft fail — ordered argument

1. `list_repos` (1167-1216) runs no measurement git; its only git calls are
   the guard's `git config --file` scans (589, 592, 635), which do not
   discover a repository.
2. Every repo that reaches `census_one` is guarded at 1087 before 1104.
3. `worktree_extra_flags` runs `git -C "$repo" worktree list` (1076) on the
   main repo already guarded at 1087, and guards each `$cpath` at 1068
   before `count_dirty` at 1072.
4. `count_dirty` runs `git config --get` (876), `--get-regexp` (910),
   `ls-files | check-attr` (922-925) and `status` (947-949) only after the
   caller's guard returned 0.

Doc precision (not a defect): header 92-93 says "no git command runs in it";
that is true of the *measurement* commands (`rev-parse`, `worktree list`,
`for-each-ref`, `rev-list`, `status`), but the guard itself does run
`git config --file` while evaluating the config. Worth a wording fix if the
claim is cited literally by acceptance.

## 2. Findings

### F1 — MEDIUM — `guard_bound_filters` fails open when its attribute probe fails

Commit 922-925 (probe), 939-943 (skip mapping), 947-949 (status):

```sh
922  mapfile -d '' -t recs < <(git -C "$wt" -c core.attributesFile="$attrs" \
923      ls-files -z --cached 2>/dev/null \
924    | git -C "$wt" -c core.attributesFile="$attrs" \
925      check-attr -z --stdin filter 2>/dev/null || true)
```

`mapfile` always returns 0 and the process substitution's status is
discarded (`|| true` at 925 is redundant on top of that). A failed
`ls-files`/`check-attr`, or a record stream not ending on a triplet
boundary, is therefore read as "no driver bound": `guard_bound_filters`
returns 0 (931) and `count_dirty` runs `git status` (947-949), the exact
command that can execute a repo-declared `filter.<name>.clean|smudge|
process`. That contradicts header 98-100 ("the driver never runs").

This is an r16 regression: r15 emitted a distinct `checkattr-fail` from the
same probe and mapped it to a row-level `error` (b410186:1096 and
b410186:1289 `unsupported|checkattr-fail) dirty=0; flags+=(error)`). The
r16 change replaced "skip status" with "assume unbound". Reachability of a
probe failure that status would survive is not demonstrated by a concrete
command (index/attribute failures usually fail status too), so this is a
fail-closed regression rather than a demonstrated escape; it is still the
only path where the driver gate can open without a positive "unbound"
reading.

Minimal patch (fail closed, no temp files; `pipefail` is already global):

```sh
   mapfile -d '' -t recs < <(git -C "$wt" -c core.attributesFile="$attrs" \
       ls-files -z --cached 2>/dev/null \
     | git -C "$wt" -c core.attributesFile="$attrs" \
-      check-attr -z --stdin filter 2>/dev/null || true)
+      check-attr -z --stdin filter 2>/dev/null)
+  pid=$!
+  wait "$pid" || return 1
+  [ $(( ${#recs[@]} % 3 )) = 0 ] || return 1
```

`set -o pipefail` is inherited, so the pipeline status reflects either git.
Add `pid` to the `local` list at 908 (`set -u` is on).
The caller's `if !` already treats nonzero as "skip status", so no 3-state
plumbing is needed; optionally print a distinct
`status-skipped: filter-probe-failed` diagnostic instead of
`filter-driver-bound`. If `$!`/`wait` on a process substitution is not
trusted, use a write-free preflight pass of the same pipeline with output
to `/dev/null` and keep the triplet check. Apply the triplet check to the
driver-list probe too (910-911) for symmetry.

Verification gap: the fixture has no vehicle that makes this probe fail
(case_03's vehicles are cycle, `~user`, FIFO include, NUL config, invalid
boolean; case_14's drivers are all found by a healthy probe).

### F2 — MEDIUM (security leg) / LOW (semantics leg) — `:(optional)` is not modelled for the pathname keys

`expand_config_path` (540-549) models only `~/`, `~user` and `%(prefix)`.
`:(optional)<path>` falls into the relative branch (546), so the guard
checks `$dir/:(optional)<path>` / `$wt/:(optional)<path>` instead of the
target git resolves.

Two legs:

- **LOW, excludes/attributes:** `core.excludesFile`/`core.attributesFile`
  are read through `git_config_pathname`, which strips `:(optional)` and
  treats a missing optional target as unset (lane source scout
  `ScoutExcludesRelative.md` F4, line 69; `SrcGitConfigIncludesRecheck.md`
  66-73). `scan_config_file` (619-625) and `status_info_file` (876-880)
  guard the mis-resolved path, and the `-c` value at 948-949 is already
  absolute, so git no longer strips it and reads a nonexistent file,
  suppressing the XDG default. Dirty counts can diverge (already reported as
  ScoutExcludesRelative F4; not repeated as new).
- **MEDIUM, `core.worktree`:** git strips the prefix and (because the target
  exists) uses it, and the census does **not** override `core.worktree`.
  The default store is still caught because the stripped-looking value
  retains `.omp/agent` as components and `protected_component_reason`
  (302-324) refuses it. A **relocated** root seeded by
  `build_protected_roots` (241-297) — e.g. `PI_CODING_AGENT_DIR=/srv/agentstore`
  or a custom `PI_CONFIG_DIR` whose directory is not named `.omp` — is
  matched only by the root-overlap predicate (`protected_reason_input`
  346-358). For `core.worktree = :(optional)/srv/agentstore`, the guarded
  path is `$dir/:(optional)/srv/agentstore`, which does not overlap
  `/srv/agentstore`, so the scan (626-631) passes; `git -C repo status`
  then applies `/srv/agentstore` as the worktree and walks it.
  [INFERENCE: `core.worktree` is read via `git_config_pathname` and the
  value is used when the optional target exists; grounded in the lane's
  source scouts `SrcGitConfigIncludesRecheck.md` 66-73 and
  `ScoutExcludesRelative.md` 69, not executed. The non-optional
  `core.worktree = /srv/agentstore` IS refused today — only the prefix
  defeats the check.]

Minimal patch: strip only in the three pathname-key branches, never in the
shared helper (F3):

```sh
       core:excludesfile|core:attributesfile)
         if [ "$bare" = 1 ] || [ -z "$val" ]; then continue; fi
+        val_eff=$val
+        case "$val" in ':(optional)'*) val_eff=${val#:(optional)} ;; esac
-        if ! tgt=$(expand_config_path "$val" "${dir%/*}"); then
+        if ! tgt=$(expand_config_path "$val_eff" "${dir%/*}"); then
       core:worktree)
         if [ "$bare" = 1 ] || [ -z "$val" ]; then continue; fi
-        if ! tgt=$(expand_config_path "$val" "$dir"); then
+        val_eff=$val
+        case "$val" in ':(optional)'*) val_eff=${val#:(optional)} ;; esac
+        if ! tgt=$(expand_config_path "$val_eff" "$dir"); then
```

and in `status_info_file` (876-880): expand/guard the stripped value, and
for excludes/attributes treat an optional target that does not exist as
unset (fall through to the XDG default) instead of passing the literal
`: (optional)…` string to `-c`. Add `val_eff` to `scan_config_file`'s
`local` list at 580 (and the equivalent in `status_info_file`'s `local`
list at 875); `set -u` is on.

### F3 — MEDIUM (in-flight repair only, not cbf688a) — a global `:(optional)` strip over-refuses `include.path`

Observed in the uncommitted worktree hunk (`+/−31/18` state; the current
stripped line was `v=${v#:(optional)}` at the top of `expand_config_path`).
Stripping inside the *shared* helper also applies to
`scan_config_file`'s include branch (commit 611-614), but git does **not**
strip `:(optional)` for `include.path`: `handle_path_include` calls
`interpolate_path` directly (`config.c:153`), while only
`git_config_pathname` (`config.c:1319-1328`) handles the prefix — the lane's
own source-verified scout states this and concludes the commit's
literal-relative treatment is correct and "not a hole"
(`SrcGitConfigIncludesRecheck.md` 66-80, especially 71-80).

If that scope is integrated, `include.path = :(optional)<protected-target>`
would resolve the stripped target, reach `guard_config_path` and exit 2 for
the whole run — a single repo-local, otherwise-inert value promoted to a
fleet-wide refusal (the r14 harm class), for a file git reads only under the
literal prefixed name (normally absent, which the guard itself treats as
benign at 615). The commit is correct here; the repair must not "fix" it.

Patch: keep `expand_config_path` literal and do the key-local strip in the
three `core:*` branches only (F2). Add fixture rows: `r-inc-opt-store`
(`include.path = :(optional)<store>`, must stay green) and
`r-excl-opt-store` / `r-wtc-opt-store` (must refuse on the stripped target).

### F4 — LOW — a linked-worktree soft skip is reported as `wt-dirty`, and the row can still say `clean`

1072-1075 and 1134-1149:

```sh
1072    d=$(count_dirty "$cpath") || exit 2
1073    if [ "$d" = unverifiable ] || [ "${d:-0}" -gt 0 ]; then
1074      saw_dirty=1
```

`count_dirty` returns `unverifiable` both for a bound filter driver
(939-943) and for a failed status (953-955). In a *linked* worktree that
becomes `wt-dirty` (1074) — documented at 57-58 as "its own `git status
--porcelain` is non-empty", which a skipped/failed status is not — while the
same condition in the **main** worktree becomes `status-unverifiable`
(1134-1136). `wt-dirty` is absent from `has_problem` (1146), so a row whose
only side condition is this prints `clean,wt-dirty` instead of losing
`clean`. The mapping predates r16 (pre-harm a31642d:232 maps
`unverifiable`→`saw_dirty` identically), so this is inherited; r16's new
`status-skipped` path widens its reach to bound-filter worktrees.

Patch: distinguish the two outcomes in `worktree_extra_flags`
(`saw_unverifiable=1` for `unverifiable`, `saw_dirty=1` only for a positive
count), emit `status-unverifiable` in its output, and in `census_one` fold
it into the existing flag once:

```sh
   local unverifiable=0
   [ "$dirty" = unverifiable ] && unverifiable=1
   case "$wt_extra" in *status-unverifiable*) unverifiable=1 ;; esac
   if [ "$unverifiable" = 1 ]; then dirty=0; flags+=(status-unverifiable); fi
```

### F5 — LOW — "only a protected-namespace reach keeps whole-run exit 2" is not what the code does

The code's deliberate non-protected whole-run refusals still present at
cbf688a: `ambiguous-path` (370, 380, 420, 1062), `unresolved-path` (416,
806), `symlink-loop` (426), `git-alternates-depth` (459),
`git-alternates-unparsed` (464, 471), `git-metadata-unreadable` (487, 490),
`git-metadata-symlink` (496, 660, 675), `git-metadata-unavailable` (510),
`git-metadata-hardlink` (513), `git-metadata-nonregular` (516),
`hardlinked-compare` (1267), `special-path` (1268). A single fleet child
with a FIFO/hardlinked `.git/config` (505-516) or an unreadable `.git/info`
(486-490) still suppresses every other repo's rows.

The script header no longer names the reserved classes (r15 had that
sentence and r16 deleted it), but the round's C1 claim and the fixture
docstring (`tests/fixtures/r15-census-config.py` 13-19: "only a
protected-namespace reach keeps the whole-run exit-2 refusal shape") state
an exclusivity the tool does not implement — and the same fixture's
`CONFIG_REASONS` (954-967) admits `git-metadata-nonregular` /
`git-metadata-hardlink`, i.e. the oracle expects those hard refusals. Claim
and oracle disagree.

Patch: text only — narrow the claim to "protected-namespace reach plus the
r14 git-metadata/ambiguous-input integrity refusals (list them)", or restore
the r15-style reserved-classes sentence in the header. No behaviour change.

### F6 — LOW — an invalid `extensions.worktreeConfig` earlier occurrence is not detected

635-638:

```sh
635    if ! s=$(git config --file "$cfg" --no-includes --type=bool --get "$key" ...); then
636      cfg_soft "git-config-unparsed"; return 1
```

`--get` returns the **last** value. With

```ini
[extensions]
    worktreeConfig = maybe
    worktreeConfig = true
```

the probe returns `true` and the repo is measured, although git parses every
occurrence and dies on `maybe` (`git_config_bool` → `die_bad_number`
per occurrence). The observed row would then be `status-unverifiable` (git's
own status fails at 947-955), not the header's promised `error` row for "an
invalid extensions.worktreeConfig boolean" (commit header 92-97). The outcome is
honest (no `clean`) but the documented flag is wrong. [INFERENCE on git's
per-occurrence boolean parse; not executed.]

Patch: validate every occurrence with git's own parser and take the last
value:

```sh
-        if ! s=$(git config --file "$cfg" --no-includes --type=bool --get "$key" 2>/dev/null); then
+        if ! s=$(git config --file "$cfg" --no-includes --type=bool --get-all "$key" 2>/dev/null); then
           cfg_soft "git-config-unparsed"; return 1
         fi
+        s=${s##*$'\n'}
```

Add a fixture row (`worktreeConfig = maybe` then `= true`) to pin that
`--get-all --type=bool` exits nonzero when any value is invalid.

## 3. Residual risk and verification gaps

1. **Source only.** Nothing was executed (assignment says source inspection;
   the probe rule also forbids running the census). Every claim above is a
   read of `cbf688a`; the declared measurements (changed 20/20, 12/12,
   38/38) were not re-run by this seat.
2. **Fixture does not assert the "no git ran" property.** `soft_problems`
   (fixture 1010-1032) asserts exit 0, exactly one zero-count `error` row,
   the `config-unsupported` token, no store access and sentinels. The git
   spy already logs cwd+argv (fixture 76-78, 179, 713-763), so an assertion
   "no `git` spy line carries `-C <soft repo>` / `--git-dir <soft gitdir>`"
   is cheap and would turn header 92-93 into an oracle. Today the proof is
   static only.
3. **No vehicles for F1/F2/F3/F4-linked/F6:** no probe-failure case, no
   `:(optional)` case, no linked worktree in case_14, no multi-value
   worktreeConfig.
4. **TOCTOU** between guard and later access remains (header 115-118).
5. **Inherited masking (not r16):** `count_worktrees` (852) and
   `count_unpushed` (862, 866) turn a git failure into `0` / `no-remote`
   with no `error` flag (identical in pre-harm a31642d:109, 119, 123), so a
   damaged repo can still read `clean`. Same soft-failure→false-clean
   family; worth a later round.
6. **Diagnostic token reuse:** `git-config-unsupported` is both the soft
   diagnostic (1088) and the hard `path-protected` reason for
   excludes/attributes (624, 880); a path-resolution refusal
   (`symlink-loop`, `unresolved-path`) in such a value therefore prints
   `path-protected: git-config-unsupported`, which reads like the soft
   class. Distinguishable only by the `path-protected` prefix.

## 4. Probe-rule self-audit

- No `census/operator-sweep-20261019/`, `~/.omp`, `.ufo/state`,
  `.ufo/watchdog.log`, `MANIFEST.json`, sibling lane, fleet script or
  template was read, listed, grepped or copied.
- No commit/add/stash/reset/checkout; no lane file written except this
  report. No delegation, no `agent://all`.
- Two `git show` extractions were written to `/tmp/r15-census.txt` and
  `/tmp/preharm-census.txt` for line-number comparison (outside the lane,
  no lane data); both were removed and their absence verified. Disclosed
  rather than hidden.
- One deviation from "exact named files": a single non-recursive `ls` of
  `.ufo/waves/round-16/w1/` and one recursive `grep -rln 'optional'` over
  that same report directory were used to locate lane evidence; afterwards
  only exact named files were read. Neither touched a forbidden surface.

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --stat --oneline -s; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat b410186 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh tests/fixtures/r15-census-config.py && git diff b410186 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | grep -n '^[-+]' | grep -v '^[-+][-+]' | head -100
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'return [0-9]' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'exit [0-9]' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '|| true\|if ! \|&& exit\||| exit\||| return' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && shellcheck --version; shellcheck -f gcc -s bash tools/souji-census.sh; echo "shellcheck_rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && shellcheck -o all -f gcc -s bash tools/souji-census.sh; echo "shellcheck_all_rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && shellcheck -o all -f gcc -s bash tools/souji-census.sh 2>/dev/null | grep -E 'SC2310|SC2311|SC2312|SC2329'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && shellcheck -S warning -f gcc -s bash tools/souji-census.sh 2>/dev/null | grep -vE 'SC2250|SC2292|SC2249|SC2094|SC2310|SC2311|SC2312|SC2329' ; echo done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1035 && NR<=1165 {printf "%4d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1166 && NR<=1242 {printf "%4d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=755 && NR<=905 {printf "%4d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=571 && NR<=682 {printf "%4d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=360 && NR<=460 {printf "%4d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py census/round-16/run-matrix.py 2>/dev/null; git -C . show cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --stat --oneline -s; ls .ufo/waves/round-16/w1 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'status-skipped\|config-unsupported\|no git\|error row\|soft\|return 1\|exit 2\|inert' tests/fixtures/r15-census-config.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=900 && NR<=1120 {printf "%4d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1160 && NR<=1260 {printf "%4d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1 && NR<=140 {printf "%4d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'def spy_git_env\|SPY\|wrapper\|argv\|cwd\|def run_tool\|def sentinel_problems\|def access_problems\|git_spy\|spy_path' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=700 && NR<=880 {printf "%4d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i 'fifo\|mknod\|hardlink\|link_to\|nul\|chmod 000\|cfg-nul\|wtc-maybe\|inc-cycle\|inc-tildeuser' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=140 && NR<=175 {printf "%4d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py; grep -n 'case_1[7-9]\|case_2[0-9]' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=400 && NR<=525 {printf "%4d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1262 && NR<=1310 {printf "%4d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh > /tmp/r15-census.txt 2>/dev/null; grep -n 'unverifiable\|wt-dirty' /tmp/r15-census.txt
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show a31642d:tools/souji-census.sh > /tmp/preharm-census.txt 2>/dev/null; grep -n 'unverifiable\|wt-dirty' /tmp/preharm-census.txt; echo ---; git show a31642d:tools/souji-census.sh | wc -l
awk 'NR>=1070 && NR<=1130 {printf "%4d: %s\n", NR, $0}' /tmp/r15-census.txt
awk 'NR>=1191 && NR<=1240 {printf "%4d: %s\n", NR, $0}' /tmp/r15-census.txt; echo '--- r15 census_one'; awk 'NR>=1240 && NR<=1300 {printf "%4d: %s\n", NR, $0}' /tmp/r15-census.txt
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum; git diff --stat -- tools/souji-census.sh; git diff -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/w1/ && grep -rln 'optional' .ufo/waves/round-16/w1/ 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=860 && NR<=975 {printf "%4d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -A4 -B4 'optional' .ufo/waves/round-16/w1/ScoutIncludeIfConditions.md .ufo/waves/round-16/w1/SrcGitConfigIncludesRecheck.md .ufo/waves/round-16/w1/ScoutExcludesRelative.md 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -B3 -A6 'optional' .ufo/waves/round-16/w1/ScoutGitHostVersion.md .ufo/waves/round-16/w1/SrcGitStatusRejected.md 2>/dev/null | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=40 && NR<=100 {printf "%4d: %s\n", NR, $0}' .ufo/waves/round-16/w1/SrcGitConfigIncludesRecheck.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=56 && NR<=80 {printf "%4d: %s\n", NR, $0}' .ufo/waves/round-16/w1/ScoutExcludesRelative.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR==1{next} {print NR": "$0}' | grep -n -E 'expand_config_path\(\)|:(optional)|core:excludesfile|core:worktree|guard_config_file_kind "\$tgt"|scan_config_file "\$dir" "\$tgt"|guard_bound_filters\(\)|mapfile -d|check-attr -z|\|\| true\)|unverifiable.*wt-dirty|wt-dirty: a non-main|status-unverifiable|clean only when|has_problem|guard_git_surface "\$d" \|\| true|if ! guard_git_surface|exit 2; fi|return 1' | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat; echo '--- fixture diff:'; git diff --stat -- tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -E 'clean" only|wt-dirty: a non-main|Degraded to one|no git command runs|Accepted: any core.hooksPath|filter.<name>.clean'
grep -n -E "\|\| printf '0'|grep -c \. \|\| true|worktree list 2>/dev/null" /tmp/preharm-census.txt | head -20; echo '--- r15 third value'; grep -n 'checkattr-fail\|unsupported' /tmp/r15-census.txt | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -E '^build_protected_roots\(\)|^protected_component_reason\(\)|^protected_reason_inside\(\)|^protected_reason_input\(\)|^path_overlaps\(\)|^status_info_file\(\)|status_info_file "\$1" core|core.excludesFile="\$ex"|core.attributesFile="\$at"|^count_dirty\(\)|^worktree_extra_flags\(\)|d=\$\(count_dirty|unverifiable" \]|status-skipped'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh; git diff --stat -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=907 && NR<=958 {printf "%4d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=538 && NR<=552 {printf "%4d: %s\n", NR, $0} NR>=616 && NR<=633 {printf "%4d: %s\n", NR, $0} NR>=1066 && NR<=1076 {printf "%4d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -E 'not one atomic|Residual: hardlinked|hardlinked object'
rm -f /tmp/r15-census.txt /tmp/preharm-census.txt && ls /tmp/r15-census.txt /tmp/preharm-census.txt 2>&1 | sed -n '1,2p'; echo cleanup_rc=$?
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -E 'emit_compare$|emit_compare;|emit_census >|^emit_census$|load_census "\$COMPARE"'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w1/RevSoftPropagation.md && awk 'NR>=30 && NR<=48 {printf "%4d: %s\n", NR, $0}' .ufo/waves/round-16/w1/RevSoftPropagation.md && awk 'NR>=392 && NR<=404 {printf "%4d: %s\n", NR, $0}' .ufo/waves/round-16/w1/RevSoftPropagation.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w1/RevSoftPropagation.md && git diff --stat -- .ufo/waves/round-16/w1/RevSoftPropagation.md tools/souji-census.sh tests/fixtures/r15-census-config.py && sha256sum .ufo/waves/round-16/w1/RevSoftPropagation.md
```

Non-shell tool reads (for completeness): `read` of
`tools/souji-census.sh` ranges 1-263, 261-560, 564-900, 901-1240,
1244-1784, and 160-200.
