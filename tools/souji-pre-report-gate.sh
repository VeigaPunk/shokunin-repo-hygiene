#!/usr/bin/env bash
# Read-only round pre-report checks. Exit: 0 pass, 1 failed check, 2 usage.
set -u
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_COMMON_DIR GIT_NAMESPACE GIT_PREFIX GIT_SHALLOW_FILE GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_CONFIG_GLOBAL GIT_CONFIG_SYSTEM GIT_CONFIG_NOSYSTEM GIT_TERMINAL_PROMPT GIT_ASKPASS GIT_SSH GIT_SSH_COMMAND GIT_EDITOR GIT_PAGER GIT_EXTERNAL_DIFF 2>/dev/null || true
# r74 wave repair (S74ExecEvade HIGH h1/h2): caller-environment config (GIT_CONFIG_COUNT/KEY_n/VALUE_n,
# GIT_CONFIG_PARAMETERS) and GIT_ATTR_SOURCE can install a clean filter that hides edits from status and
# from hash-object alike; none of them may reach the gate's git calls.
unset GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_ATTR_SOURCE 2>/dev/null || true
# r76 wave repair (S76Sentinel MEDIUM-1): a caller GIT_EXEC_PATH made `git ls-remote` run its helper.
unset GIT_EXEC_PATH 2>/dev/null || true
for v in $(compgen -e); do case $v in GIT_CONFIG_KEY_*|GIT_CONFIG_VALUE_*) unset "$v" ;; esac; done
export LC_ALL=C GIT_OPTIONAL_LOCKS=0
usage() { printf '%s\n' 'Usage: bash tools/souji-pre-report-gate.sh --lane ABS --branch NAME --report ABS --prereg ABS [--contract] [--shonen ABS]' >&2; }
usage_error() { usage; exit 2; }
lane= branch= report= prereg= shonen= contract=0
seen_lane=0 seen_branch=0 seen_report=0 seen_prereg=0 seen_shonen=0
while (($#)); do
  case $1 in
    --lane) (( $# >= 2 && !seen_lane )) || usage_error; lane=$2; seen_lane=1; shift 2 ;;
    --branch) (( $# >= 2 && !seen_branch )) || usage_error; branch=$2; seen_branch=1; shift 2 ;;
    --report) (( $# >= 2 && !seen_report )) || usage_error; report=$2; seen_report=1; shift 2 ;;
    --prereg) (( $# >= 2 && !seen_prereg )) || usage_error; prereg=$2; seen_prereg=1; shift 2 ;;
    --shonen) (( $# >= 2 && !seen_shonen )) || usage_error; shonen=$2; seen_shonen=1; shift 2 ;;
    --contract) contract=1; shift ;;
    *) usage_error ;;
  esac
done
(( seen_lane && seen_branch && seen_report && seen_prereg )) || usage_error
[[ $lane = /* && $report = /* && $prereg = /* && -n $branch && $branch != -* && $branch != *..* && $branch != */* ]] || usage_error
fail=0
check() { printf 'check-%s=%s\n' "$1" "$2"; [[ $2 != FAIL ]] || fail=1; }
# 1. Branch name is constrained above; compare full SHA of local branch to remote ref.
local_tip=$(git --no-optional-locks -C "$lane" rev-parse --verify "refs/heads/$branch^{commit}" 2>/dev/null) || local_tip=
remote_data=$(git --no-optional-locks -C "$lane" ls-remote --exit-code origin "refs/heads/$branch" 2>/dev/null) || remote_data=
remote_tip=$(printf '%s\n' "$remote_data" | awk 'NR==1 {print $1}')
if [[ $local_tip =~ ^[0-9a-f]{40,64}$ && $remote_tip == "$local_tip" ]]; then check tip PASS; else check tip FAIL; printf 'detail-tip: local=%s remote=%s\n' "${local_tip:-<none>}" "${remote_tip:-<none>}" >&2; fi
# 2. Report must be a regular file with bytes (r74 wave repair, S74Sentinel MEDIUM-2: a FIFO or a device
#    named as the report made the heading grep below block forever).
if [[ -f $report && -s $report ]]; then check report PASS; else check report FAIL; fi
# 3. Exactly one canonical heading.
shonen_count=0
[[ -f $report ]] && shonen_count=$(grep -c '^## SHONEN' "$report" 2>/dev/null || true)
if [[ $shonen_count == 1 ]]; then check shonen PASS; else check shonen FAIL; printf 'detail-shonen: found %s headings, expected 1\n' "${shonen_count:-0}" >&2; fi
# 4. No lane changes may remain before report filing.
#    r74 C1: an empty `git status` is a stat-cache verdict (racy-git S315): an index entry carries stat(2)
#    data beside the object name (gitformat-index S317), so a rewritten stat entry over changed bytes reads
#    clean. Every tracked path status reports clean is therefore re-hashed against the object id its index
#    entry records, through the receipt writer's own byte-truth check (_truth_refusal in the
#    souji-receipt-write.py beside this gate; hash-object applies check-in conversion, S316). A missing
#    writer, a failed read or any mismatch fails `clean`.
#    r74 wave repairs (after measurement; census/round-74/records/wave-repair/): the writer is resolved
#    beside the gate's real path (S74Reviewer: a symlinked gate could load a stub); it is compiled from its
#    source bytes in an isolated interpreter (`-I`: no caller PYTHON* variables, no CWD on sys.path; no
#    __pycache__ read; S74Sentinel HIGH-1); the writer's own pinned status (core.fsmonitor=false,
#    core.fileMode=true, full stat) must also be empty, because the truth check skips every path that
#    status lists (S74Sentinel HIGH-2, S74ExecEvade n-filemode); its filter/conversion witness
#    (_witness_refusal, r71) runs before the hash, because hash-object applies a configured clean filter
#    (S74ExecEvade HIGH h3); and only the refusal class and count are printed, never a path (D30 no-echo,
#    S74Sentinel MEDIUM-1).
# r77 C1 (S321 git dir.c add_patterns, S064 attr.c, S062 fifo(7)): git opens every exclude and attribute
#    source with a plain blocking open(2) and checks the file type only after it, so a FIFO named as a
#    per-directory .gitignore/.gitattributes, as $GIT_DIR/info/exclude or info/attributes, or as
#    core.excludesFile/core.attributesFile blocked the gate inside `git status` forever (S76Sentinel
#    MEDIUM-2). Every such source that exists must be a regular file (a symlink counts by its target)
#    before any git call below reads it; a work-tree one is refused whatever git would do with it (the gate
#    does not model whether git descends into an ignored directory). Count only, no path echo (D30).
#    Backstop: check 4's git and python calls run under `timeout`; expiry fails clean.
nonreg_sources() {
  local gd f n=0 v
  gd=$(git --no-optional-locks -C "$lane" rev-parse --absolute-git-dir 2>/dev/null) || { echo -1; return; }
  for f in "$gd/info/exclude" "$gd/info/attributes"; do
    [[ -e $f && ! -f $f ]] && n=$((n + 1))
  done
  local xdg=${XDG_CONFIG_HOME:-${HOME:+$HOME/.config}}
  for v in core.excludesFile:ignore core.attributesFile:attributes; do
    f=$(git --no-optional-locks -C "$lane" config --path --get "${v%%:*}" 2>/dev/null) || f=
    # unset: git falls back to $XDG_CONFIG_HOME/git/<name> (or $HOME/.config/git/<name>)
    [[ -z $f && -n $xdg ]] && f=$xdg/git/${v#*:}
    [[ -n $f && $f != /* ]] && f=$lane/$f
    [[ -n $f && -e $f && ! -f $f ]] && n=$((n + 1))
  done
  f=$(find "$lane" -path "$lane/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) \
        ! -type f -print 2>/dev/null | wc -l) || { echo -1; return; }
  echo $((n + f))
}
gate_timeout=300
gate_src=$(readlink -f -- "${BASH_SOURCE[0]}" 2>/dev/null) || gate_src=
gate_dir=
[[ -n $gate_src ]] && gate_dir=$(cd "$(dirname "$gate_src")" && pwd) || gate_dir=
nonreg=$(nonreg_sources)
if [[ $nonreg != 0 ]]; then
  check clean FAIL
  if [[ $nonreg == -1 ]]; then printf 'detail-clean: RECEIPT-NONREGULAR-SOURCE: source scan failed\n' >&2
  else printf 'detail-clean: RECEIPT-NONREGULAR-SOURCE: %s exclude/attribute source(s) are not regular files\n' "$nonreg" >&2; fi
elif status=$(timeout -k 5 "$gate_timeout" git --no-optional-locks -C "$lane" status --porcelain=v1 --untracked-files=all 2>&1); then
  if [[ -n $status ]]; then check clean FAIL; printf 'detail-clean: %s\n' "$status" >&2
  elif truth=$(timeout -k 5 "$gate_timeout" python3 -I -B - "$gate_dir/souji-receipt-write.py" "$lane" 2>&1 <<'PY'
import sys, types
path, lane = sys.argv[1], sys.argv[2]
with open(path, "rb") as f:
    src = f.read()
mod = types.ModuleType("souji_receipt_write")
mod.__file__ = path
sys.modules[mod.__name__] = mod
exec(compile(src, path, "exec"), mod.__dict__)
sz = mod._status_z(lane)
if sz.returncode != 0:
    print("pinned git status failed")
    sys.exit(1)
if sz.stdout:
    print("pinned git status (core.fsmonitor=false, core.fileMode=true) lists %d record(s)"
          % sz.stdout.count(b"\0"))
    sys.exit(1)
for fn in (mod._witness_refusal, mod._truth_refusal):
    msg = fn(lane)
    if msg:
        print(msg.split(" (", 1)[0])
        sys.exit(1)
# r75 C1 (S318 gitignore(5), S319 git-ls-files(1)): status hides untracked files that any exclude source
# matches, but only the per-directory .gitignore files are the lane's declared policy; info/exclude and
# core.excludesFile are local and unversioned. Untracked paths ignored under --exclude-standard but not
# under --exclude-per-directory=.gitignore alone fail clean (count only, no path echo). The r75 stated
# limit (an untracked .gitignore that ignores itself) is closed by the r76 attribution block below.
# r75 wave repair (S75ExecEvade HIGH-1): a repository-local core.worktree points status and both listings
# at another tree, so the difference reads empty while the lane's own tree carries hidden content; the
# work tree git resolves must be the lane itself.
import os, subprocess
top = subprocess.run(["git", "--no-optional-locks", "-C", lane, "rev-parse", "--show-toplevel"],
                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
if top.returncode != 0 or os.path.realpath(top.stdout.rstrip(b"\n")) != os.path.realpath(os.fsencode(lane)):
    print("RECEIPT-WORKTREE-REDIRECTED: git's work tree is not the lane directory")
    sys.exit(1)
def _ignored(*rule):
    p = subprocess.run(["git", "--no-optional-locks", "-C", lane, "-c", "core.fsmonitor=false", "ls-files",
                        "-z", "--others", "--ignored", *rule], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if p.returncode != 0:
        print("ignored-file listing failed")
        sys.exit(1)
    return set(p.stdout.split(b"\0")) - {b""}
hidden = _ignored("--exclude-standard") - _ignored("--exclude-per-directory=.gitignore")
if hidden:
    print("RECEIPT-UNTRACKED-LOCAL-EXCLUDE: %d untracked path(s) are hidden only by info/exclude or "
          "core.excludesFile" % len(hidden))
    sys.exit(1)
# r76 C1 (S320 git-check-ignore(1): -v names each matching pattern's source file): a per-directory
# .gitignore is declared policy only when it is tracked. An untracked .gitignore that ignores itself (the
# r75 stated limit f7) hides content behind an unversioned rule exactly as info/exclude does. Every ignored
# untracked path must be decided by a pattern from a tracked .gitignore in one of its ancestor directories;
# core.excludesFile is attributed away (/dev/null) so a path only it hides reads as unmatched. Count only.
# r76 wave repair (S76Sentinel HIGH-1, LOW-1): the tracked set is read from HEAD's tree, not the index:
# `ls-files --cached` ran a repo-local core.fsmonitor after the byte-truth check (the hook appended a rule
# to the tracked .gitignore and the gate passed), and index membership also admits a staged .gitignore.
_ls = subprocess.run(["git", "--no-optional-locks", "-C", lane, "ls-tree", "-r", "-z", "--name-only",
                      "--full-tree", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
if _ls.returncode != 0:
    print("tracked-file listing failed")
    sys.exit(1)
tracked = set(_ls.stdout.split(b"\0")) - {b""}
ign = sorted(_ignored("--exclude-standard"))
if ign:
    ci = subprocess.run(["git", "--no-optional-locks", "-C", lane, "-c", "core.fsmonitor=false",
                         "-c", "core.excludesFile=/dev/null", "check-ignore", "-v", "-n", "-z", "--stdin"],
                        input=b"\0".join(ign) + b"\0", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    rec = ci.stdout.split(b"\0")
    if ci.returncode not in (0, 1) or len(rec) != 4 * len(ign) + 1 or rec[-1] != b"":
        print("ignore-source attribution failed")
        sys.exit(1)
    undeclared = 0
    for i, path in enumerate(ign):
        src, _ln, pat, echoed = rec[4 * i:4 * i + 4]
        if echoed != path:
            print("ignore-source attribution failed")
            sys.exit(1)
        d = os.path.dirname(src)
        if not (src in tracked and os.path.basename(src) == b".gitignore" and not pat.startswith(b"!")
                and (d == b"" or path.startswith(d + b"/"))):
            undeclared += 1
    if undeclared:
        print("RECEIPT-UNTRACKED-UNDECLARED-IGNORE: %d untracked path(s) are hidden by a rule that is not a "
              "tracked .gitignore" % undeclared)
        sys.exit(1)
PY
  ); then check clean PASS
  else check clean FAIL; printf 'detail-clean: byte truth: %s\n' "$(printf '%s' "${truth:-no output}" | head -c 400 | LC_ALL=C tr -c '[:print:]' '?')" >&2; fi
else check clean FAIL; printf 'detail-clean: git status failed or timed out: %s\n' "$status" >&2; fi
# 5. The preregistration is mandatory; absence is never skipped.
if [[ -s $prereg ]]; then check prereg PASS; else check prereg FAIL; fi
# 6. Report-contract predicates (r36): canonical sections, one SHONEN line per
#    SHONEN.md box, one verdict line per learning trend, the stale-lane line,
#    a measurement row with a counting command and a measured commit, 1-3
#    claim ids, and an evidence pointer. Opt-in via --contract so the r27
#    fixture's predicates 1-5 keep their frozen behaviour; a run that skips it
#    says so, so the evidence can never mistake silence for a pass.
if (( contract )); then
  shonen_path=${shonen:-$lane/SHONEN.md}
  checker=$lane/tools/souji-report-contract.py
  if [[ -f $checker && -s $report ]]; then
    out=$(python3 -B "$checker" --report "$report" --shonen "$shonen_path" 2>&1); rc=$?
    saw_fail=0 saw_check=0
    while IFS= read -r line; do
      case $line in
        check-*) saw_check=$((saw_check + 1)); printf 'contract-%s\n' "$line"; [[ $line != *=FAIL ]] || saw_fail=1 ;;
        SUMMARY*) printf 'contract-%s\n' "$line" ;;
        detail-*|ERROR*) printf 'contract-%s\n' "$line" >&2 ;;
      esac
    done <<< "$out"
    # The verdict binds on the exit code AND the printed lines: a checker that
    # prints FAIL but exits 0 (or a wrapper that swallows a FAIL) is a failure,
    # never a pass (r36 A2, wave seat SwarmCritic19 H3).
    if (( rc == 0 )) && (( saw_fail == 0 )) && (( saw_check > 0 )); then
      check report-contract PASS
    else
      check report-contract FAIL
      (( saw_check > 0 )) || printf 'detail-report-contract: checker printed no check-* line (vacuous success)\n' >&2
    fi
  else
    check report-contract FAIL
    printf 'detail-report-contract: checker missing (%s) or report empty\n' "$checker" >&2
  fi
else
  printf 'check-report-contract=SKIPPED (no --contract)\n'
fi
exit "$fail"
