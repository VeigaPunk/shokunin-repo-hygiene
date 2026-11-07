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
# r79 C1 (S325 bash 5.3 manual "Signals"; S326 coreutils timeout.c): every git, find and python child runs under
#    `timeout`, which moves itself and the command into a NEW process group (S326: `if (!foreground) setpgid
#    (0, 0);`). A caller's TERM/HUP to the gate killed the shell and left that group running (the blocked child
#    outlived the gate by up to the 300 s bound), and bash defers a trapped signal while it waits for a
#    foreground command (S325: "it will not execute the trap until the command completes"), so a trap alone
#    cannot act. Children therefore run as asynchronous jobs through gate_run, which `wait`s on them: S325
#    "the `wait` builtin will return immediately with an exit status greater than 128, immediately after which
#    the shell executes the trap". The trap kills the running child's process group (and the child itself, in
#    case it has not yet called setpgid), removes the gate's private scratch dir, prints check-signal=FAIL and
#    the class RECEIPT-GATE-SIGNALED, and exits 128 + the signal number. Output reaches the shell through files
#    in that scratch dir (mktemp -d under $TMPDIR), never through `$(...)` or `<(...)`, which bash also waits
#    for in the foreground.
gate_tmp= gate_child=
gate_cleanup() { [[ -n $gate_tmp ]] && rm -rf -- "$gate_tmp"; gate_tmp=; }
gate_on_signal() {  # $1 name, $2 number
  trap '' TERM INT HUP
  if [[ -n $gate_child ]]; then
    : # r79 control K-c: the running child group is NOT killed
  fi
  gate_cleanup
  printf 'check-signal=FAIL\n'
  printf 'detail-signal: RECEIPT-GATE-SIGNALED: SIG%s received; the running child group was killed\n' "$1" >&2
  exit $((128 + $2))
}
trap 'gate_on_signal TERM 15' TERM
trap 'gate_on_signal INT 2' INT
trap 'gate_on_signal HUP 1' HUP
trap gate_cleanup EXIT
gate_tmp=$(mktemp -d -t souji-gate.XXXXXXXX) || { printf 'gate: mktemp failed\n' >&2; exit 2; }
gate_run_file() {  # [-c] SECS CMD...: stdout (and stderr with -c) in $gate_tmp/o; returns the command's status
  local merge=0 rc
  [[ $1 == -c ]] && { merge=1; shift; }
  local secs=$1; shift
  if (( merge )); then timeout -k 5 "$secs" "$@" <&0 >"$gate_tmp/o" 2>&1 &
  else timeout -k 5 "$secs" "$@" <&0 >"$gate_tmp/o" 2>/dev/null &
  fi
  gate_child=$!
  wait "$gate_child"; rc=$?
  gate_child=
  return "$rc"
}
gate_run() {  # [-c] VAR SECS CMD...: like `VAR=$(CMD)` (trailing newlines stripped), bounded and interruptible
  local merge=() var rc data=
  [[ $1 == -c ]] && { merge=(-c); shift; }
  var=$1; shift
  gate_run_file "${merge[@]}" "$@"; rc=$?
  IFS= read -r -d '' data < "$gate_tmp/o"
  while [[ $data == *$'\n' ]]; do data=${data%$'\n'}; done
  printf -v "$var" '%s' "$data"
  return "$rc"
}
# 0. r78 C1 (S324 git setup.c get_common_dir_noenv; S323 git config.adoc "Includes"; S062 fifo(7)): every git
#    command first discovers the repository — it reads $GIT_DIR/HEAD and $GIT_DIR/commondir with a plain
#    blocking open, then the system, global ($HOME/.gitconfig, $XDG_CONFIG_HOME/git/config), repository and
#    worktree config files and every file their include.path / includeIf.*.path names. A FIFO at any of those
#    paths blocked the gate's FIRST git call (check 1) forever, before check 4's r77 source pre-check could
#    run (S77ExecEvade, S77Sentinel MEDIUM-2). Each such source that exists must be a regular file (a symlink
#    counts by its target) before any git call that discovers the lane; include targets are followed
#    (relative to the including file, `~/` expanded, at most 10 deep, the depth git itself allows) with
#    `git config --file` run from `/`, which reads only the named, already-checked file. An include whose
#    condition git would not meet is held to the same rule (the gate does not evaluate conditions). On
#    refusal checks 1 and 4, which run git in the lane, are skipped as FAIL. Count only, no path echo (D30).
#    Check 1's git calls (rev-parse, and ls-remote, which runs upload-pack in the remote repository whose
#    config the gate cannot pre-check) run under `timeout`; expiry fails tip with RECEIPT-GIT-TIMEOUT.
#    r78 wave repair (after measurement; census/round-78/records/wave-repair/): include records are read
#    NUL-delimited (`-z`: key, newline, value) so a subsection with a space or a value with a newline cannot
#    split a record (S78Reviewer HIGH, S78Sentinel MEDIUM-1); values go through `--type=path`, so git's own
#    `~/`, `~user/` and `%(prefix)/` expansion decides the path (S78Reviewer, S78CriticDiscern); the seen-set
#    keys on the canonical path (an associative array, not a `|`-joined string) and the walk stops at 64
#    config files, so a fan-out tree cannot fork without bound (S78Sentinel HIGH-1, LOW-2); a depth or count
#    overrun, an unreadable config or a failed read is its own class, RECEIPT-GITSOURCE-SCAN, never counted as
#    a non-regular file (S78Sentinel MEDIUM-2); the gitfile and commondir are read under a timeout (S78Reviewer
#    LOW TOCTOU); the branch's loose ref is held to the same rule (S78CriticClaims evidence 6).
gate_git_timeout=45
gitsrc_n=0 gitsrc_err=0 gitsrc_nodes=0 gitsrc_line=
declare -A gitsrc_seen=()
gitsrc_one() {  # $1 path, $2 depth (config files only; -1 = not a config file)
  local p=$1 depth=$2 rc canon rec v
  local -a recs=()
  [[ -e $p || -L $p ]] || return 0
  if [[ ! -f $p ]]; then gitsrc_n=$((gitsrc_n + 1)); return 0; fi
  (( depth >= 0 )) || return 0
  canon=$(realpath -m -- "$p" 2>/dev/null) || { gitsrc_err=1; return 0; }
  [[ -n ${gitsrc_seen[$canon]+x} ]] && return 0
  gitsrc_seen[$canon]=1
  gitsrc_nodes=$((gitsrc_nodes + 1))
  (( depth <= 10 && gitsrc_nodes <= 64 )) || { gitsrc_err=1; return 0; }
  gate_run_file "$gate_git_timeout" env -C / GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
          git --no-optional-locks config -z --no-includes --type=path --file "$p" \
          --get-regexp '^include(if\..*)?\.path$'
  rc=$?
  case $rc in 0|1) ;; *) gitsrc_err=1; return 0 ;; esac
  mapfile -d '' recs < "$gate_tmp/o"
  for rec in "${recs[@]}"; do
    [[ $rec == *$'\n'* ]] || { gitsrc_err=1; continue; }
    v=${rec#*$'\n'}
    [[ -n $v ]] || continue
    [[ $v == /* ]] || v=$(dirname -- "$p")/$v
    gitsrc_one "$v" $((depth + 1))
  done
}
gitsrc_read1() {  # first line of a small regular file into $gitsrc_line, bounded in time (the -f test races a swap)
  gate_run gitsrc_line 5 head -n 1 -c 4096 -- "$1"
}
gitsrc_scan() {
  local gd cd v
  if [[ -e $lane/.git && ! -d $lane/.git && ! -f $lane/.git ]]; then gitsrc_n=$((gitsrc_n + 1)); return; fi
  if [[ -d $lane/.git ]]; then gd=$lane/.git
  elif [[ -f $lane/.git ]]; then
    gitsrc_read1 "$lane/.git" || { gitsrc_err=1; return; }
    v=$gitsrc_line
    v=${v#gitdir: }
    [[ $v == /* ]] || v=$lane/$v
    gd=$v
  else return
  fi
  cd=$gd
  gitsrc_one "$gd/commondir" -1
  if [[ -f $gd/commondir ]]; then
    gitsrc_read1 "$gd/commondir" || { gitsrc_err=1; return; }
    v=$gitsrc_line
    [[ $v == /* ]] || v=$gd/$v
    cd=$v
  fi
  gitsrc_one "$gd/HEAD" -1
  gitsrc_one "$cd/packed-refs" -1
  gitsrc_one "$cd/refs/heads/$branch" -1
  gitsrc_one "/etc/gitconfig" 0
  [[ -n ${HOME:-} ]] && gitsrc_one "$HOME/.gitconfig" 0
  local xdg=${XDG_CONFIG_HOME:-${HOME:+$HOME/.config}}
  [[ -n $xdg ]] && gitsrc_one "$xdg/git/config" 0
  gitsrc_one "$cd/config" 0
  gitsrc_one "$gd/config.worktree" 0
}
gitsrc_scan
if (( gitsrc_n || gitsrc_err )); then
  check gitsource FAIL
  (( gitsrc_n )) && printf 'detail-gitsource: RECEIPT-NONREGULAR-GITSOURCE: %s git configuration/ref source(s) are not regular files\n' "$gitsrc_n" >&2
  (( gitsrc_err )) && printf 'detail-gitsource: RECEIPT-GITSOURCE-SCAN: the discovery-source scan failed or exceeded its bound (depth 10, 64 config files)\n' >&2
else
  check gitsource PASS
fi
# 1. Branch name is constrained above; compare full SHA of local branch to remote ref.
if (( gitsrc_n || gitsrc_err )); then
  check tip FAIL; printf 'detail-tip: skipped: discovery-source refusal\n' >&2
else
  local_rc=0 remote_rc=0
  gate_run local_tip "$gate_git_timeout" git --no-optional-locks -C "$lane" rev-parse --verify "refs/heads/$branch^{commit}" || { local_rc=$?; local_tip=; }
  gate_run remote_data "$gate_git_timeout" git --no-optional-locks -C "$lane" ls-remote --exit-code origin "refs/heads/$branch" || { remote_rc=$?; remote_data=; }
  remote_tip=$(printf '%s\n' "$remote_data" | awk 'NR==1 {print $1}')
  if [[ $local_tip =~ ^[0-9a-f]{40,64}$ && $remote_tip == "$local_tip" ]]; then check tip PASS; else check tip FAIL; printf 'detail-tip: local=%s remote=%s\n' "${local_tip:-<none>}" "${remote_tip:-<none>}" >&2; fi
  if (( local_rc == 124 || local_rc == 137 || remote_rc == 124 || remote_rc == 137 )); then
    printf 'detail-tip: RECEIPT-GIT-TIMEOUT: a check-1 git call exceeded %ss\n' "$gate_git_timeout" >&2
  fi
fi
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
#    r77 wave repair (after measurement; census/round-77/records/wave-repair/): git reads info/exclude and
#    info/attributes from the COMMON dir in a linked worktree, so every git-dir path is resolved with
#    `rev-parse --git-path` (S77Reviewer MEDIUM-1, S77Sentinel MEDIUM-1); the index and info/sparse-checkout,
#    which `git status` also opens, are held to the same rule (S77ExecEvade f3/sp1); the work-tree scan
#    follows a symlink to its target (`-xtype f`, the stated rule; S77CriticClaims) and starts at the
#    work-tree top; a failed scan fails closed (`find` status, not `wc`'s; S77MutGate F5, S77Sentinel LOW-2);
#    /dev/null as core.excludesFile/core.attributesFile is the documented way to disable them and passes
#    (S77Reviewer LOW-3); the pre-check's own git calls run under the same timeout (S77Sentinel MEDIUM-2).
gate_timeout=300
nonreg_sources() {  # sets $nonreg: the count of non-regular sources, -1 when the scan failed
  local f n=0 v top hits
  nonreg=-1
  gate_run top "$gate_timeout" git --no-optional-locks -C "$lane" rev-parse --show-toplevel || return
  for v in info/exclude info/attributes index info/sparse-checkout; do
    gate_run f "$gate_timeout" git --no-optional-locks -C "$lane" rev-parse --path-format=absolute \
          --git-path "$v" || return
    [[ -e $f && ! -f $f ]] && n=$((n + 1))
  done
  local xdg=${XDG_CONFIG_HOME:-${HOME:+$HOME/.config}}
  for v in core.excludesFile:ignore core.attributesFile:attributes; do
    gate_run f "$gate_timeout" git --no-optional-locks -C "$lane" config --path --get "${v%%:*}"
    case $? in 0|1) ;; *) return ;; esac
    # unset: git falls back to $XDG_CONFIG_HOME/git/<name> (or $HOME/.config/git/<name>)
    [[ -z $f && -n $xdg ]] && f=$xdg/git/${v#*:}
    [[ -n $f && $f != /* ]] && f=$lane/$f
    [[ $f == /dev/null ]] && continue
    [[ -n $f && -e $f && ! -f $f ]] && n=$((n + 1))
  done
  gate_run hits "$gate_timeout" find "$top" -path "$top/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) \
           ! -xtype f -printf x || return
  nonreg=$((n + ${#hits}))
}
gate_src=$(readlink -f -- "${BASH_SOURCE[0]}" 2>/dev/null) || gate_src=
gate_dir=
[[ -n $gate_src ]] && gate_dir=$(cd "$(dirname "$gate_src")" && pwd) || gate_dir=
if (( gitsrc_n || gitsrc_err )); then
  check clean FAIL; printf 'detail-clean: skipped: discovery-source refusal\n' >&2
elif nonreg_sources; [[ $nonreg != 0 ]]; then
  check clean FAIL
  if [[ $nonreg == -1 ]]; then printf 'detail-clean: RECEIPT-NONREGULAR-SOURCE: source scan failed\n' >&2
  else printf 'detail-clean: RECEIPT-NONREGULAR-SOURCE: %s exclude/attribute source(s) are not regular files\n' "$nonreg" >&2; fi
elif gate_run -c status "$gate_timeout" git --no-optional-locks -C "$lane" -c core.fsmonitor=false status --porcelain=v1 --untracked-files=all; then
  if [[ -n $status ]]; then check clean FAIL; printf 'detail-clean: %s\n' "$status" >&2
  elif gate_run -c truth "$gate_timeout" python3 -I -B - "$gate_dir/souji-receipt-write.py" "$lane" <<'PY'
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
  then check clean PASS
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
    gate_run -c out "$gate_timeout" python3 -B "$checker" --report "$report" --shonen "$shonen_path"; rc=$?
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
