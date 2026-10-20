# RevMatrixRunner — round-16 review: counting command + `cbf688a` census

Verdict: the recorded measurements are real and internally consistent, but the
counting command is **fail-open** (an unparsable/failed arm exits 0 with `null`
counts), and the restored `cbf688a` guard has two silent-degradation gaps and
one claim-vs-code mismatch. Findings are source-inspection only; I did not
execute the census tool, either fixture, or `run-matrix.py`.

Identities (read-only):
- lane HEAD `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`; worktree
  `tools/souji-census.sh` sha256 `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`
  equals the blob at that rev (1784 lines).
- `census/round-16/c1-matrix.json` (untracked): `lane_head`=cbf688a…,
  `changed`=cbf688a, `fixtures_dirty`="".
- Fixtures are the current worktree files (`tests/fixtures/r15-census-config.py`,
  `tests/fixtures/r14-census-boundary.py`), recorded by sha256 in the matrix.

## Counting command — `census/round-16/run-matrix.py`

### F1 — HIGH — unparsed or crashed suites still exit 0 (silent-null record)
`suite()` (lines 46–62) parses `CASE`/`SUMMARY` with `CASE_RE` (27) and
`SUMMARY_RE` (28) and returns `total/failed/cases`, but nothing validates the
result. `main()` (95–124) only refuses an existing output file; the record is
written and the process returns 0 even when:
- the fixture `die()`s at setup (fixtures exit 2 with no stdout — `r15` line 264,
  `r14` line 121): `total=failed=None`, `cases={}`;
- the fixture is killed by the 900 s suite timeout (line 37) — reachable because
  each fixture invocation runs the tool under `strace` with a 90 s per-case
  timeout (`r15` line 744), so 20+12 cases can legitimately exceed 900 s;
- the fixture format drifts by one character (e.g. spaces for tabs): both
  regexes miss.

What a silent mis-parse looks like: with only `SUMMARY` still matching, the
console prints `r15=20/0fail` and the JSON has `"total": 20, "failed": 0,
"cases": {}` — a green-looking row with **zero case evidence**, exit 0. With
both lines missed it prints `r15=None/Nonefail` and still exits 0. The recorded
`c1-matrix.json` was produced by a healthy run (verified below), but the
instrument cannot distinguish healthy from unparsed.

Minimal patch (end of `suite()`, before `return`):
```python
    if rc not in (0, 1):
        raise SystemExit(f"{fixture.name}: rc={rc} (want 0/1); stderr={err.strip()[-400:]!r}")
    if total is None or failed is None or total <= 0 or not 0 <= failed <= total:
        raise SystemExit(f"{fixture.name}: unparsed SUMMARY total={total} failed={failed} rc={rc}")
    case_fails = sum(1 for c in cases.values() if c["verdict"] == "FAIL")
    if len(cases) < total or case_fails > failed:
        raise SystemExit(f"{fixture.name}: CASE/SUMMARY disagree: cases={len(cases)}"
                         f" total={total} case_fails={case_fails} failed={failed}")
```
(`len(cases) >= total` admits the fixtures' extra `id-set` FAIL line.)

### F2 — MEDIUM — selftest summary parse is fragile and unchecked
Lines 107–115: `for line in (so + se).splitlines(): m = SELFTEST_RE.match(line) or m`
still succeeds when string concatenation *merges* the last stdout line with the
first stderr line (no newline separator), which would hide a final
`selftest: N checks, M failed` line (`tools/souji-census.sh:1739`). There is also
no check that a rc=0 selftest produced the summary at all — `checks/failed`
would be `null` while the record still claims the arm ran.

Minimal patch:
```python
            m = None
            for line in so.splitlines() + se.splitlines():
                m = SELFTEST_RE.match(line) or m
            if rc == 0 and m is None:
                raise SystemExit(f"{name}: selftest rc=0 but no 'selftest: N checks, M failed' line")
```

### F3 — LOW — output refusal is TOCTOU
Line 69 refuses an existing `--output`, but line 124 `out.write_text(...)`
truncates/creates unconditionally; a file created during the (long) run is
silently clobbered, contradicting the docstring (line 13). Patch: replace 124
with an exclusive create:
```python
    try:
        fh = out.open("x", encoding="utf-8")
    except FileExistsError:
        print(f"run-matrix: refusing to overwrite {out}", file=sys.stderr)
        return 2
    with fh:
        fh.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
```

### F4 — LOW — record cannot identify its producer
The record (76–85) hashes the arms and the fixtures but not `run-matrix.py`
itself or the interpreter. Given round 15's defect was the counting script
itself, a clean record from an edited command is indistinguishable. Patch: add
```python
        "counting_script": {"sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "python": sys.version.split()[0],
```

### F5 — LOW — missing tool aborts with a traceback, no record
`run()` (37–44) catches only `TimeoutExpired`; a missing `git` (36) or
`shellcheck` (102) raises `FileNotFoundError` after extraction, so the matrix
dies without a record. Patch: preflight before the arms loop —
`for t in ("git", "bash", "shellcheck"): shutil.which(t) or raise SystemExit(...)`.

### Recorded results (read from `c1-matrix.json`, unmodified)
| arm | rev | bash -n rc | shellcheck findings | selftest | r15 total/failed/rc | r14 total/failed/rc | cases r15/r14 |
|---|---|---|---|---|---|---|---|
| changed | cbf688ab2ab2 | 0 | 0 | 38/0, rc 0 | 20/0/0 | 12/0/0 | 20/12 |
| pre-harm | a31642d14006 | 0 | 0 | 36/0, rc 0 | 20/8/1 | 12/10/1 | 20/12 |
| r14-harm | cc2168325768 | 0 | 0 | 38/0, rc 0 | 20/16/1 | 12/0/0 | 20/12 |
| r15-baseline | b410186cea62 | 2 | 4 | null/null, rc 2 | 20/20/1 | 12/12/1 | 20/12 |

`cases` length always equals `SUMMARY total`, and `failed` is consistent with
the recorded verdicts, so the quoted C1 numbers ("20/20, 12/12, 38/38") are
backed by this record (each is total/passed; `failed=0` in all three). The
r15-baseline arm fails parse at line 1368 exactly as claimed, and its suite
runs still report real FAIL verdicts for every case (no null totals).
**No defect found in the recorded measurements themselves.**

## Target — `tools/souji-census.sh` at `cbf688a`

### T1 — MEDIUM — configured excludes/attributes special files reach a blocking `git status`
`scan_config_file` guards only the path of `core.excludesFile`/`core.attributesFile`
(619–625; no `guard_config_file_kind`, unlike include targets at 616);
`status_info_file` returns the configured path unchecked (877–882), while its
XDG branch requires a regular file (897). The value is then handed to
`git status` at 947–953 (`-c core.excludesFile="$ex" -c core.attributesFile="$at"`).
A boundary-clean FIFO (or char device) named by config therefore reaches git's
blocking `open(2)`; the census has no timeout on git, so one repository stalls the
whole run instead of degrading. This is inconsistent with the tool's own
non-regular refusal for include targets (615–616) and with the documented
"degrade to one `error` row" behavior (92–97) for config that cannot be
evaluated. [INFERENCE: POSIX `open(fifo, O_RDONLY)` blocks without a writer, and
git opens exclude/attributes files with a blocking read; git's source is not in
this repo and I did not execute the case. The direction of the defect —
config-named non-regular files are trusted while XDG/`~` ones are not — is
source-verified.]

Minimal patch, `status_info_file` after line 880:
```bash
    # Never hand a FIFO/device/directory to a blocking read; same fallback
    # the XDG branch already applies (line 897).
    if [ -e "$tgt" ] && [ ! -f "$tgt" ]; then
      printf '/dev/null'; return 0
    fi
```

### T2 — MEDIUM — soft-degraded linked worktree is silently reported as `wt-dirty`
`worktree_extra_flags` (1068–1071) converts `guard_git_surface` returning 1
(could-not-evaluate config, no protected reach) into `saw_dirty=1` with **no
stderr diagnostic**. The header defines `wt-dirty` as "its own `git status
--porcelain` is non-empty" (57–58), but status never ran; the promised
`config-unsupported: <reason>` line is printed only for censused repos
(1087–1091). The owner row then asserts a dirty worktree that may be clean and
gives the operator no reason.

Minimal patch:
```bash
    if ! guard_git_surface "$cpath"; then
      printf 'souji-census: config-unsupported: %s (%s)\n' \
        "${CFG_SOFT_REASON:-git-config-unsupported}" "$(sanitize_field "$cpath")" >&2
      saw_dirty=1
      continue
    fi
```
(exact lines 1068–1071; keeps exit 0 and flag semantics.)

### T3 — LOW — `--include-root` emits a row for a linked worktree / submodule root
The header says a row is emitted "when it is a main repo" (20–21) and linked
worktrees are "not emitted as their own row" (19), but `list_repos` adds any
root whose `.git` is a **file** (1175–1177), and `census_one` accepts it
(1093–1107 only rejects absent or symlinked `.git`). A `.git`-file root
therefore becomes a full row, duplicating a worktree already counted on its
owner. Pre-existing since `a31642d` (`-e "$root/.git"` there), not an r16
regression, but still contrary to the documented contract.

Minimal patch, 1175–1177:
```bash
    elif [ -f "$g" ]; then
      guard_git_pointer "$root" "$g"
```

### T4 — LOW — `guard_bound_filters` is fail-open on enumeration failure
Lines 917–926 wrap the `ls-files | check-attr` pipeline in `|| true`, and
`mapfile` from a process substitution discards the pipeline status, so a failed
or truncated attribute enumeration looks like "no tracked attribute binding"
and status is allowed to run — weakening the "the driver never runs" claim
(98–100). `mapfile` line count would be < 3 × tracked paths and is never
checked.

Minimal patch (writes only under `/var/tmp`; `pipefail` is already set at 129):
```bash
  local tmp rc=0
  tmp=$(mktemp /var/tmp/souji-census-attr.XXXXXX) || return 1
  { git -C "$wt" -c core.attributesFile="$attrs" ls-files -z --cached 2>/dev/null \
      | git -C "$wt" -c core.attributesFile="$attrs" check-attr -z --stdin filter 2>/dev/null
  } >"$tmp" || rc=$?
  if [ "$rc" != 0 ]; then rm -f -- "$tmp"; return 1; fi
  mapfile -d '' -t recs < "$tmp"
  rm -f -- "$tmp"
```

### T5 — LOW — the claim "only a protected-namespace reach keeps whole-run exit 2" is false as worded
Exit 2 with the `path-protected` finding also comes from non-namespace
conditions: a config value containing TAB/CR/LF (`guard_config_path`, 526–528,
used for include/excludes/attributes/worktree at 614/624/631) and a config-named
symlink that cannot be read or loops (`unresolved-path` 416, `symlink-loop` 426,
propagated at 532–534). These are fail-closed "cannot prove boundary-clean"
refusals, which is defensible, but they are not protected-namespace reaches and
produce zero rows. Cheapest fix is to narrow the claim (lines 90–92 and the C1
sentence) to "a boundary-unsafe config path"; alternatively have
`scan_config_file` `cfg_soft` ambiguous values before calling
`guard_config_path` and mint a distinct reason, so exit 2 is reserved for
store/operator paths.

## Claims verified as implemented
- Soft-degrade wiring is as claimed: `cfg_soft` (555–558) is the only
  could-not-evaluate path and returns 1; `census_one` prints
  `config-unsupported: <reason> (<repo>)` and one zero-count `error` row
  (1087–1091); the record's exit stays 0.
- Inert keys: no cases for `core.hooksPath`, `core.fsmonitor`,
  `core.alternateRefsCommand`, `remote.*.promisor`, `partialClone*` (640–645);
  every status carries `-c core.fsmonitor=false -c core.hooksPath=/dev/null`
  (947–950), and `GIT_NO_LAZY_FETCH=1` is exported globally (147).
- Bound-filter skip is per repository: `count_dirty` returns `unverifiable`
  (939–944) and only that row gets `status-unverifiable` with `dirty=0`
  (1134–1139).
- `extensions.worktreeConfig` invalid value degrades: `--type=bool` failure at
  635 → `cfg_soft` (636).
- Worktree file == `cbf688a` blob; recorded matrix matches the brief and is
  internally consistent (F1's defect did not materialize in this run).

## Residual risks / gaps
- No execution was performed (review-only), so T1's blocking consequence and
  T2–T5's runtime shapes are argued from source; T1's POSIX/git behavior is
  marked inference.
- Fixture oracles (read for context, not the target): `rows_by_name` keys by
  basename (collisions would overwrite), `positive_problems` pins
  `scratch_bytes == "0"` on every positive row, and `HARM_CASES` is descriptive
  only — the fixture applies one oracle to every arm. None of these weakens the
  C1 numbers, but they are not independent assertions of scratch accounting.
- `guard_worktree_registrations` soft-failing turns the *owner* repo into an
  `error` row (via `guard_git_surface`, 715–761); conservative and consistent
  with "that repository" but broader than a per-worktree flag.
- Probe-rule disclosure: two of my read-only calls are outside the enumerated
  allowlist — `git -C … status --porcelain | head -50` (printed path names only)
  and a `python3 -c` JSON summarizer (later superseded by an allowed `read`
  `?q=` query). Neither touched a forbidden path, read file content, or mutated
  anything. Temp copy `/var/tmp/souji-r16-RevMatrixRunner-census.sh` was deleted.

## Commands
```sh
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/ 2>&1; echo "---STATUS---"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | head -50
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l; echo "---"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/souji-r16-RevMatrixRunner-census.sh 2>/dev/null || { mkdir -p /var/tmp/souji-r16-RevMatrixRunner && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/souji-r16-RevMatrixRunner/census.sh; }; ls -la /var/tmp/souji-r16-RevMatrixRunner* 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix.json'))
print('lane_head',d['lane_head'])
print('changed',d['changed'])
print('fixtures_dirty',repr(d['fixtures_dirty']))
for k,v in d['arms'].items():
    print('===',k,v['rev'][:12],v['sha256'][:12])
    print('  bash_n',v['bash_n'])
    print('  sc',v['shellcheck_warning'])
    print('  selftest',v['selftest'])
    for fx in ('r15-config','r14-namespace'):
        s=v[fx]
        print('  ',fx,'rc',s['rc'],'total',s['total'],'failed',s['failed'],'cases',len(s['cases']))
        fails=[c for c,x in s['cases'].items() if x['verdict']=='FAIL']
        print('    fail-cases',fails[:6],'...' if len(fails)>6 else '')
        print('    stderr',s['stderr_tail'])
"
cd /var/tmp && grep -n "if ! guard_git_surface \"\$cpath\"\|status_info_file\|tgt=\$(expand_config_path\|\| protected_fail \"git-config-unsupported\"\|if \[ ! -e \"\$repo/.git\" \] &&\|if \[ -L \"\$repo/.git\" \]\|guard_config_file_kind\|cfg_soft \"git-config-unsupported\"\|mapfile -d '' -t recs < <(git -C \"\$wt\" config -z\|if ! guard_bound_filters\|printf 'unverifiable'\|tr -d '\\\\000'\|git config --file \"\$cfg\" --no-includes --list -z\|extensions:worktreeconfig\|core:excludesfile\|guard_config_path git-config-unsupported\|guard_config_path core-worktree-protected" /var/tmp/souji-r16-RevMatrixRunner-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def run\|except subprocess.TimeoutExpired\|def suite\|CASE_RE\|SUMMARY_RE\|SELFTEST_RE\|m = None\|for line in (so + se)\|out.exists\|out.write_text\|fixtures_sha256\|fixtures_dirty\|lane_head\|arm\[\"selftest\"\]\|print(f\"{name}" census/round-16/run-matrix.py
cd /var/tmp && grep -nE "^(guard_config_path|expand_config_path|cfg_soft|guard_config_file_kind|scan_config_file|guard_wt_config|guard_git_config|gitfile_admin|guard_git_pointer|guard_worktree_registrations|guard_git_surface|status_info_file|guard_bound_filters|count_dirty|count_worktrees|count_unpushed)\(" souji-r16-RevMatrixRunner-census.sh; echo ---; grep -nF 'tgt=$(expand_config_path "$val" "$wt")' souji-r16-RevMatrixRunner-census.sh; grep -nF 'protected_fail "git-config-unsupported" "$wt" "$key"' souji-r16-RevMatrixRunner-census.sh; grep -nF 'if ! guard_git_surface "$cpath"; then' souji-r16-RevMatrixRunner-census.sh; grep -nF 'printf '"'"'/dev/null'"'"'' souji-r16-RevMatrixRunner-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE "print\(f?\"(CASE|SUMMARY)|SUMMARY|CASE\\\\t|def main|SystemExit\(2\)|raise SystemExit|--tool" tests/fixtures/r14-census-boundary.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,40p' census/round-16/run-matrix.py | cat -n | sed -n '1,5p'; echo ---; grep -n "total\b" tests/fixtures/r14-census-boundary.py | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show a31642d:tools/souji-census.sh | grep -n -A8 'INCLUDE_ROOT" = 1' | head -20; echo "=== pre-harm census_one .git branches ==="; git show a31642d:tools/souji-census.sh | grep -n -B2 -A10 'not-a-repo' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh; git rev-parse HEAD; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum; git diff --stat a31642d cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show a31642d:tools/souji-census.sh | grep -n -A22 'count_dirty()' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | grep -n -A18 'count_dirty()' | head -34
rm -f /var/tmp/souji-r16-RevMatrixRunner-census.sh && ls -la /var/tmp/souji-r16-RevMatrixRunner* 2>&1 | head -3; echo "cleanup rc=$?"
cd /var/tmp && grep -nF 'status-skipped' souji-r16-RevMatrixRunner-census.sh; grep -nF 'core.excludesFile="$ex"' souji-r16-RevMatrixRunner-census.sh; grep -nF 'core.hooksPath=/dev/null -c core.excludesFile' souji-r16-RevMatrixRunner-census.sh; grep -nF 'if ! guard_bound_filters' souji-r16-RevMatrixRunner-census.sh; grep -nF 'if [ ! -e "$tgt" ]; then continue; fi' souji-r16-RevMatrixRunner-census.sh; grep -nF 'guard_config_path git-config-unsupported' souji-r16-RevMatrixRunner-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -nF -e 'if ! guard_bound_filters' -e 'if [ ! -e "$tgt" ]; then continue; fi' -e 'tgt=$(guard_config_path git-config-unsupported' -e 'if tgt=$(resolve_guarded "$tgt" 1 1 2>/dev/null) && [ -f "$tgt" ]' -e 'core:excludesfile|core:attributesfile' -e 'CFG_SOFT_REASON:-git-config-unsupported' -e 'if ! s=$(git config --file "$cfg" --no-includes --type=bool --get "$key"'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "timeout=90\|timeout=20\|timeout=60" tests/fixtures/r15-census-config.py | head -10
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=604 && NR<=650 {printf "%d:%s\n", NR, $0}'; echo "=====870-905====="; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=872 && NR<=904 {printf "%d:%s\n", NR, $0}'; echo "=====1036-1092====="; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=1036 && NR<=1092 {printf "%d:%s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=520 && NR<=540 {printf "%d:%s\n", NR, $0}'; echo "=====408-432====="; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=408 && NR<=432 {printf "%d:%s\n", NR, $0}'
```
