# RevRedaction — r16 W1: `<protected>` redaction and every stderr/stdout print site

- Target: `tools/souji-census.sh` @ `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
  (blob sha256 `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`, 1784 lines).
  **Every line number below is against that commit**, read via
  `git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh`.
- Method: source inspection only. No census/fixture execution, no `/var/tmp` world,
  no read of `~/.omp` or `census/operator-sweep-*`.
- Axes: (A1) no store path / canary reaches stdout or stderr; (A2) diagnostics remain
  sufficient for the operator and for both fixture oracles; (A3) no over-redaction.

> **Environment note (added during review).** The worktree is now dirty:
> `M tools/souji-census.sh`, blob sha256 `feba44c7a598888844debb84efe4d29d90869f0dd640ea3f0229969eacd1aa88`
> (+55/−34 vs the commit). That revision changes `scan_config_file` (soft findings now
> `continue` instead of returning, so a later protected include still refuses),
> `expand_config_path` (`:(optional)` stripping), `guard_git_config`,
> `status_info_file` (rc 3 for unmodellable values), `guard_bound_filters` (fail-closed
> pipe/modulo checks) and `count_dirty` (rc-3 → `unverifiable`). It does **not** touch
> `protected_fail`, `resolve_guarded`, `guard_config_path` or `load_census`, so F1, F3 and
> the relabel in F2 apply to both trees. My citations stay on the pinned commit.

## Answers to the two posed questions

**Can any store path or canary still be printed?** The canary cannot: no print site emits
file *contents*, and no config *value* is ever printed — `scan_config_file:579-650` uses
`$val` only as input to `expand_config_path`; `protected_fail:184-192` prints reason + label
+ path; `status_info_file:874-902` passes the key name `core.excludesFile|core.attributesFile`,
never the value. Git's own stderr, which does echo config paths and values, is suppressed at
every call (`count_worktrees:850-854`, `count_unpushed:856-868`, `status_info_file:876`,
`guard_bound_filters:910-925`, `count_dirty:947-953`, `scan_config_file:589,592,635`,
`worktree_extra_flags:1076`, `census_one:1104`).

A **store path string** can still reach output through two narrow channels: the
`ambiguous-path` refusal echoes raw, un-normalized input while the redaction predicate is
lexical-normalizing (F1), and `--compare` echoes operator-supplied baseline fields
unfiltered (F3). Everything else — every guarded row field, every refusal produced by
`guard_target`/`guard_path`/`guard_config_path`, and all four diagnostics
(`status-skipped` `:940-941`, `config-unsupported` `:1088-1090`, `census failed` `:1232`,
`root is not a directory` `:1221,1332`) — prints only already-resolved, already-guarded
paths.

**Does redaction hide information the r14 fixture needs?** No. The r14 oracle reads only:
exit code (`r14:484`), substring `path-protected` in stderr (`r14:486`), canary absence from
out+err (`r14:488`), empty stdout (`r14:490`), `str(AGENT)` absence from **stdout**
(`r14:492`), and the spy/strace access logs (`r14:494-501`). It never parses the third
`protected_fail` field. The r15 oracle parses only finding+reason with
`FINDING_RE = r"souji-census:\s*([a-z0-9-]+):\s*([a-z0-9-]+)"` (`r15:235`) and rejects any
`str(AGENT) in res.out + res.err` (`r15:831`); redaction touches only the text after the
reason, so neither oracle is weakened or broken. Redaction is strictly additive: r14-harm
`cc21683:160-164` and r15-baseline `b410186:202-206` printed `$3` raw, and both fixtures'
pass criteria are unchanged by the new `<protected>` value.

## Findings

### F1 — Low/Medium: `ambiguous-path` echoes raw input, so a `..`-bearing path prints the protected path text

`protected_fail:184-192` redacts `$3` only when `protected_reason_inside` matches (`:186`).
That predicate normalizes lexically first (`protected_reason_inside:330-332` calls
`lexical_abs:197-212`, whose `..` branch is `:209`). `resolve_guarded` refuses a `..`
component *before* any normalization and echoes the raw string (`:369-371`; same for
control characters at `:378-380`):

    souji-census.sh --root "$HOME/.omp/agent/.."
    → souji-census: path-protected: ambiguous-path (input: /home/<u>/.omp/agent/..)

`lexical_abs("/home/<u>/.omp/agent/..")` = `/home/<u>/.omp`, which is neither under the root
nor a `.omp/agent` pair, so `:186` is false and `$raw` is printed verbatim: the store path
string (not content) reaches stderr. The same applies to
`--compare "$AGENT/../records.tsv"`. Not reachable through config values:
`guard_config_path:526-534` always prints `$cfg`, never the raw target. No current fixture
hits this (r14:556-566 uses `<scratch>/root-alias/..`; r15 case_19 at `r15:1298-1303` uses
only `AGENT` and `HOME`), but it violates the header's promise at `:110-111` in spirit and
would trip r15's `access_problems` (`:831`) if a case used `"$AGENT/.."`.

Minimal patch — add a textual predicate and OR it into the redaction test:

```bash
# after protected_reason_input (line 357): raw, unnormalized text may carry `..`
protected_text_reaches() { # $1 raw text from the diagnostic
  local text=$1 root
  for root in "${PROTECTED_HOME_ROOTS[@]+"${PROTECTED_HOME_ROOTS[@]}"}"; do
    [ -n "$root" ] || continue
    case "/$text/" in *"/${root#/}/"*) return 0 ;; esac
  done
  case "/$text/" in
    *"/.omp/agent/"*|*"/census/operator-sweep-"*|*"/.ufo/state/"*|*"/.ufo/watchdog.log/"*)
      return 0 ;;
  esac
  return 1
}
```

```diff
@@ protected_fail:186
-  if [ -n "$shown" ] && protected_reason_inside "$shown" >/dev/null 2>&1; then
+  if [ -n "$shown" ] && { protected_reason_inside "$shown" >/dev/null 2>&1 \
+       || protected_text_reaches "$shown"; }; then
     shown='<protected>'
```

`$text` is the `case` *subject*, never a pattern, so glob characters in the path cannot
change matching. The only over-redaction is a path that contains a root/component pair
textually — the intended fail-closed direction.

### F2 — Low (adjacent to scope): `guard_config_path` relabels every resolve failure as a namespace reach

`guard_config_path:532-534` suppresses `resolve_guarded`'s stderr and re-emits the caller's
namespace reason. Every `resolve_guarded` failure is a `protected_fail`, so a *structural*
failure — `unresolved-path` (`:416`), `ambiguous-path` on a symlink target (`:420`),
`symlink-loop` (`:426`) — becomes `souji-census: path-protected: include-protected (...)` and
aborts the whole run. That contradicts the documented shape at `:90-97` (“only a
protected-namespace reach keeps the whole-run exit-2 refusal”; an unreadable or looping
include is could-not-evaluate and belongs in the per-repo `error` row via
`config-unsupported`). No fixture covers it: r15's `r-inc-cycle` (`r15:466`) is a *value*
cycle caught by `CFG_STACK` (`:583-585`), not a symlink loop. Fail-closed, not fail-open:
no store access either way.

Patch sketch (change `guard_config_path:532` and `status_info_file:880` together):

```diff
@@ guard_config_path:531-534
-  if ! resolved=$(resolve_guarded "$raw" 1 1 2>/dev/null); then
-    protected_fail "$reason" "$dir" "$cfg"
-  fi
+  local rc=0
+  resolved=$(resolve_guarded "$raw" 1 1 1 2>/dev/null) || rc=$?
+  if [ "$rc" = 1 ]; then cfg_soft "${resolved:-git-config-unresolved}"; return 1; fi
+  if [ "$rc" = 2 ]; then protected_fail "$reason" "$dir" "$cfg"; fi
```

with `resolve_guarded` taking a 4th `soft-structural` flag that makes `:416,:420,:426`
print the reason to stdout and `return 1` instead of `protected_fail`; and
`status_info_file:880` changing `|| exit 2` to `|| return 1`, with `count_dirty:937-938`
degrading to `unverifiable` on rc 1 and still `exit 2` on rc 2. Preserves r15 case_02
(`r-inc-symlink`, `r15:472-473` → still `credential-store`, exit 2).

### F3 — Low: `--compare` echoes baseline content unfiltered (store path, arbitrary text)

`load_census:1286-1298` validates column count and numerics for columns 2-5 only; the repo
field is checked for emptiness only (`:1288`), and `mtime_iso`/`verdict_flags` (columns 6-7)
are not validated at all. Those values are printed verbatim: `:1357`, `:1362` (repo field of
added/removed rows) and `:1378-1380` (`before_v`/`after_v`). The tool can never *produce* a
row inside the store (`census_one:1086` guards the repo; `list_repos:1193-1195` refuses
protected children), but a pre-r14 or hand-edited baseline can carry
`/home/<u>/.omp/agent` — or any canary-shaped string in the last two columns — and
`--compare` echoes it to stdout; `usage_err "…duplicate repo $repo"` at `:1296` echoes it to
stderr. No fixture exercises a baseline *outside* the store that names one.

Minimal patch (after `repo=${line%%$'\t'*}`; add `reason` to the `local` list at `:1269`):

```diff
@@ load_census:1286-1288
     repo=${line%%$'\t'*}
     rest=${line#*$'\t'}
     [ -n "$repo" ] || usage_err "compare file: empty repo on line $n"
+    if reason=$(protected_reason_input "$(lexical_abs "$repo")"); then
+      protected_fail "$reason" compare "$file"
+    fi
```

`$file` is already `guard_path`-resolved (`:1252`), so the diagnostic itself is safe.
Optional hardening in the same place: validate `mtime_iso` and `verdict_flags` against the
shapes the tool itself emits (`newest_mtime:1028`, ordered vocabulary at `census_one:1154`),
which makes “corrupt previous census” detection consistent with the header's stance.

### F4 — Informational: the label `$2` is not redacted, though at 14 call sites it is a path

`protected_fail:189-190` prints `$2` verbatim. The label is a path at
`:459,464,471` (`$objdir`), `:487,490,496,510,513,516,658,673` (`$dir`), `:804` (`$repo`),
`:879` (`$wt`), `:1049` (`$repo`). Today every one is either a `guard_target`-derived value
(`:463,475,493,700,719,731,735,744,753,766,770,777,786,809,816,825,1051,1058,1174,1201`)
or a repo path already admitted by `protected_reason_input` (`list_repos:1193-1195`,
`census_one:1086`), so none can be inside a protected root and no leak is reachable. The
invariant is implicit; if a future call passes a less-trusted label, the store path appears
in the label while `$3` shows `<protected>`. Optional: apply the same redaction test to `$2`.

## Positively verified (no defect)

- Redaction cannot over-redact the refusal the r14 fixture needs: the finding token
  (`:181,189`) and the reason (`$1`) are outside the substitution; r14:486 and
  r15:981-988 read only those.
- No print site emits file contents: `newest_mtime`'s awk (`:986-1016`) emits only
  `epoch<TAB>flag`; `scratch_bytes` (`:961-974`) emits a number; `du`/`find` stderr is
  suppressed.
- All four stderr diagnostics carry only guarded repo paths: `status-skipped`
  (`:940-941`), `config-unsupported` (`:1088-1090`, reason is a literal),
  `census failed` (`:1232`), `root is not a directory` (`:1221,1332`).
  `hardlinked-compare` (`:1265`) prints the `guard_path`-resolved baseline name, not the
  hardlink's other name.
- `resolve_guarded` is only ever invoked inside `$( )`, and every protective caller maps its
  rc to `exit 2` (`guard_path:443`, `guard_target:452`, `guard_alternates_file:475`,
  `guard_git_links:493`, `census_one:1086,1115`, `emit_census:1220`), so no refusal is
  swallowed and no row is printed before a refusal (rows buffer until after the loop,
  `emit_census:1225-1239`).
- The selftest's boundary probes (`:1707,:1718`) run with a synthetic
  `$ST_TMP/home/.omp/agent`, and its only stderr echo (`:1713,:1724`) is a first-line
  `st_bad` diagnostic on a failing fixture — not a production print site.

## Residual risk / verification gap

- F1 and F3 are *path-string* leaks only; neither can emit store content. Both are outside
  the current fixture matrix, so no arm (pre-harm `a31642d`, r14-harm `cc21683`,
  r15-baseline `b410186`, changed) turns red for them.
- The r14 fixture's refusal oracle checks `str(AGENT)` on **stdout only** (`r14:492`) while
  its positive oracle checks out+err (`r14:533`). A future regression that prints the store
  path on stderr during a *refusal* would pass r14 and only be caught by r15:831 (which
  applies to every invocation). Relevant when reading the 38/38 claim.
- I executed no fixture, so the declared 12/12 and 38/38 counts are taken as given, not
  re-derived here.
- The uncommitted worktree revision (see Environment note) fixes one instance of F2's class
  (soft include findings no longer abort the scan before a later protected reach) but leaves
  `guard_config_path`'s structural-failure relabel, F1, F3 and F4 untouched.

STATUS: no defect found that breaks either fixture oracle; three real but narrow issues
(F1 store-path echo on `..` input, F2 namespace mislabel/whole-run abort for structural
include failures, F3 unredacted `--compare` baseline echo), one informational (F4).
Worktree is dirty (`M tools/souji-census.sh`, not mine); commit cbf688a is clean.

## Commands

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git cat-file -t cbf688ab2ab28e38103e5a9417ca525b5f2ed423 && wc -l tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum && sha256sum tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'printf\|echo\|>&2\|redact\|protected' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tests/fixtures/r14-census-boundary.py tests/fixtures/r15-census-config.py census/round-16/run-matrix.py 2>/dev/null; grep -n 'canary\|<protected>\|path-protected\|stderr\|err' tests/fixtures/r14-census-boundary.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "include-protected\|core-worktree-protected\|<protected>\|credential-store" tests/ tools/ corpus/ --include=*.py --include=*.sh --include=*.md | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "err\b\|stderr\|reason\|FINDING\|config-unsupported\|status-skipped\|hardlinked" tests/fixtures/r15-census-config.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat a31642d cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh && git diff cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | grep -n 'protected_fail\|<protected>\|shown'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in a31642d cc21683 b410186; do echo "=== $r ==="; git show $r:tools/souji-census.sh 2>/dev/null | grep -n -A12 '^protected_fail()' || echo "(absent)"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
p='.ufo/waves/round-16/w1-spec.json'
d=json.load(open(p))
def walk(o,path=""):
    if isinstance(o,dict):
        for k,v in o.items(): walk(v,path+"/"+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+f"[{i}]")
    else:
        if isinstance(o,str) and 'Redaction' in o or (isinstance(o,str) and 'redaction' in o):
            print(path,"::",o[:3000])
walk(d)
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'protected_fail ' tools/souji-census.sh | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'printf' tools/souji-census.sh | grep -v 'printf .%s.\|printf .%s\\n.\|printf .%d'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | grep -nE '^[-+].*(printf|>&2|sanitize_field|status-skipped|config-unsupported|census failed|hardlinked)' | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/ .ufo/waves/round-16/w1/ 2>/dev/null | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '180,360p' tests/fixtures/r14-census-boundary.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '130,180p' tests/fixtures/r14-census-boundary.py; echo ---; grep -n 'scratch' tests/fixtures/r14-census-boundary.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | grep -n -B3 -A8 'status_info_file\|XDG_CONFIG_HOME' | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1064,1506p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "STORE\s*=\|AGENT\s*=\|HOME\s*=\|SESSIONS\s*=\|LEAK\s*=\|GD\s*=\|RECORDS\s*=" tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'r-inc-cycle\|r-inc-symlink\|r-inc-nested\|r-inc-tildeuser\|r-inc-fifo' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '470,700p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'local shown=\|protected_reason_inside "\$shown"\|ambiguous-path\|if ! resolved=\|repo=\${line%%\|usage_err "compare file: duplicate\|printf .%s\\trepo\\t\|printf .%s\\t%s\\t%s\\t%s\\t%s\\n.$\|set -x\|2>&1\|> "\$CENSUS_TMP"' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'def refusal_problems\|def positive_problems\|FINDING not in res.err\|CANARY in res.out\|str(AGENT) in res.out\|def access_problems\|FINDING_RE = \|def case_19\|def case_05' tests/fixtures/r14-census-boundary.py tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=478 && NR<=545 {printf "%d: %s\n", NR, $0}' tests/fixtures/r14-census-boundary.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=180 && NR<=196 || NR>=366 && NR<=372 || NR>=524 && NR<=537 {printf "%d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'guard_config_path \|guard_target gitdir\|guard_target worktree\|guard_target git-metadata\|guard_target alternates' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'protected_reason_inside() {\|protected_reason_input() {\|lexical_abs() {\|^guard_path() \|^guard_target() \|^scan_config_file() \|^status_info_file() \|^guard_bound_filters() \|^count_dirty() \|^worktree_extra_flags() \|^census_one() \|^emit_census() \|^newest_mtime() \|^scratch_bytes() \|^guard_config_path() ' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=108 && NR<=112 || NR>=86 && NR<=101 || NR>=1136 && NR<=1152 || NR>=1027 && NR<=1035 || NR>=1076 && NR<=1082 || NR>=934 && NR<=942 || NR>=924 && NR<=932 || NR>=878 && NR<=888 {printf "%d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain -- tools/souji-census.sh && sha256sum tools/souji-census.sh && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum && git log --oneline -5 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat -- tools/souji-census.sh && git diff -U2 -- tools/souji-census.sh | head -160
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff -U2 -- tools/souji-census.sh | sed -n '160,320p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n '^[a-z_]*() {\|^protected_fail()\|^lexical_abs()\|^protected_reason_inside()\|^protected_reason_input()\|^guard_path()\|^guard_target()\|^guard_config_path()\|^scan_config_file()\|^status_info_file()\|^guard_bound_filters()\|^count_dirty()\|^scratch_bytes()\|^newest_mtime()\|^worktree_extra_flags()\|^census_one()\|^emit_census()\|^load_census()\|^emit_compare()\|^list_repos()'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=203 && NR<=212 || NR>=438 && NR<=455 || NR>=470 && NR<=500 || NR>=580 && NR<=600 || NR>=605 && NR<=618 || NR>=640 && NR<=655 {printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=618 && NR<=640 || NR>=874 && NR<=960 || NR>=980 && NR<=1060 {printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=1060 && NR<=1170 || NR>=1218 && NR<=1262 || NR>=1328 && NR<=1400 {printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=330 && NR<=336 || NR>=1180 && NR<=1200 {printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'def case_0[1-9]\|def case_1[0-2]' tests/fixtures/r14-census-boundary.py; echo ---; grep -n 'def refusal_problems\|def case_19\|def soft_problems\|FINDING_RE = ' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'guard_target \|protected_fail "unresolved-path"\|protected_fail "git-metadata-symlink"\|protected_fail "ambiguous-path" "\$repo"'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'protected_fail '
```

Tool installs/updates: none.
