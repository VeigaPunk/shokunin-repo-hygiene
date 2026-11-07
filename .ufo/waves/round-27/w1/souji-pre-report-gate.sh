#!/usr/bin/env bash
# souji-pre-report-gate.sh — round-27 C3 pre-report gate (draft).
#
# Frozen CLI (round-27 preregistration, claim C3):
#   bash tools/souji-pre-report-gate.sh --lane <abs-lane> --branch <branch> \
#        --report <abs-report> [--prereg <abs-file>] [--allow <rel-path>]...
#
# Checks (each prints `check-<name>=PASS|FAIL|SKIP` on stdout):
#   tip     `git -C <lane> rev-parse refs/heads/<branch>` equals the first line
#            (SHA field) of `git -C <lane> ls-remote origin refs/heads/<branch>`
#   report  report file exists and is nonempty
#   shonen  report carries exactly one `^## SHONEN` heading
#   clean   `git -C <lane> status --porcelain` shows no untracked/modified
#            paths outside the optional --allow list
#   prereg  prereg file exists (SKIP when --prereg is not supplied)
#
# Details go to stderr as `detail-<name>: ...`; machine-readable check lines
# stay on stdout. Exit status: 0 iff no check FAILs (SKIP tolerated),
# 1 if any check FAILs, 2 on usage error.

set -u

# Scrubbed environment: ignore ambient git dir/env config and locale.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_COMMON_DIR \
  GIT_NAMESPACE GIT_PREFIX GIT_SHALLOW_FILE GIT_ALTERNATE_OBJECT_DIRECTORIES \
  GIT_CONFIG_GLOBAL GIT_CONFIG_SYSTEM GIT_CONFIG_NOSYSTEM GIT_TERMINAL_PROMPT \
  GIT_ASKPASS GIT_SSH GIT_SSH_COMMAND GIT_EDITOR GIT_PAGER GIT_EXTERNAL_DIFF \
  2>/dev/null || true
export LC_ALL=C

usage() {
  cat <<'USAGE'
Usage: souji-pre-report-gate.sh --lane <abs-lane> --branch <branch> \
       --report <abs-report> [--prereg <abs-file>] [--allow <rel-path>]...
  --lane ABS      absolute path to the lane git worktree (required)
  --branch NAME   branch name; compared to origin refs/heads/NAME (required)
  --report ABS    absolute path to the round report file (required)
  --prereg ABS    absolute path to the frozen preregistration file
  --allow REL     repo-relative path exempt from the clean check (repeatable)

Checks (stdout): check-tip, check-report, check-shonen, check-clean,
check-prereg = PASS|FAIL|SKIP. Exit 0 iff no check FAILs, 1 otherwise, 2 usage.
USAGE
}

usage_error() { usage >&2; exit 2; }

is_abs() { [ "${1#/}" != "$1" ]; }

lane= branch= report= prereg=
allows=()

while [ $# -gt 0 ]; do
  case $1 in
    --lane)   [ $# -ge 2 ] || usage_error; lane=$2; shift 2 ;;
    --branch) [ $# -ge 2 ] || usage_error; branch=$2; shift 2 ;;
    --report) [ $# -ge 2 ] || usage_error; report=$2; shift 2 ;;
    --prereg) [ $# -ge 2 ] || usage_error; prereg=$2; shift 2 ;;
    --allow)  [ $# -ge 2 ] || usage_error; allows+=("$2"); shift 2 ;;
    *) usage_error ;;
  esac
done

[ -n "$lane" ] && [ -n "$branch" ] && [ -n "$report" ] || usage_error
is_abs "$lane" || usage_error
is_abs "$report" || usage_error
if [ -n "$prereg" ]; then is_abs "$prereg" || usage_error; fi

fail=0

check() { # name verdict [detail...]
  local name=$1 verdict=$2
  shift 2
  printf 'check-%s=%s\n' "$name" "$verdict"
  if [ "$verdict" = FAIL ]; then fail=1; fi
  if [ $# -gt 0 ]; then printf 'detail-%s: %s\n' "$name" "$*" >&2; fi
}

# 1. tip — local branch tip == first line of origin ls-remote for the branch.
local_tip=$(git -C "$lane" rev-parse "refs/heads/$branch" 2>/dev/null) || local_tip=
remote_tip=$(git -C "$lane" ls-remote origin "refs/heads/$branch" 2>/dev/null \
  | awk 'NR==1{print $1; exit}')
if [ -n "$local_tip" ] && [ -n "$remote_tip" ] && [ "$local_tip" = "$remote_tip" ]; then
  check tip PASS
else
  check tip FAIL "local=${local_tip:-<none>} remote=${remote_tip:-<none>}"
fi

# 2. report — exists and nonempty.
if [ -s "$report" ]; then
  check report PASS
else
  check report FAIL "missing or empty: $report"
fi

# 3. shonen — exactly one `^## SHONEN` heading.
shonen_cnt=$(grep -c '^## SHONEN' "$report" 2>/dev/null) || shonen_cnt=0
if [ "$shonen_cnt" -eq 1 ]; then
  check shonen PASS
else
  check shonen FAIL "found $shonen_cnt '^## SHONEN' headings (want exactly 1)"
fi

# 4. clean — no porcelain entries outside the allow list.
cleaned=1
status_out=$(git -C "$lane" status --porcelain 2>/dev/null) || {
  check clean FAIL "git status failed: $lane"
  cleaned=0
  status_out=
}
while IFS= read -r line; do
  [ -z "$line" ] && continue
  p=${line:3}
  [ -n "$p" ] || continue
  ok=0
  for a in "${allows[@]}"; do
    a=${a%/}
    if [ "$p" = "$a" ] || [ "${p#"$a"/}" != "$p" ]; then
      ok=1
      break
    fi
  done
  if [ "$ok" = 0 ]; then
    check clean FAIL "unallowed dirty path: $p"
    cleaned=0
    break
  fi
done <<<"$status_out"
if [ "$cleaned" = 1 ]; then check clean PASS; fi

# 5. prereg — exists when supplied; otherwise not applicable.
if [ -n "$prereg" ]; then
  if [ -f "$prereg" ]; then
    check prereg PASS
  else
    check prereg FAIL "missing: $prereg"
  fi
else
  check prereg SKIP "--prereg not supplied"
fi

if [ "$fail" = 1 ]; then exit 1; fi
exit 0
