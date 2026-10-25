#!/usr/bin/env bash
# Read-only round pre-report checks. Exit: 0 pass, 1 failed check, 2 usage.
set -u
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_COMMON_DIR GIT_NAMESPACE GIT_PREFIX GIT_SHALLOW_FILE GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_CONFIG_GLOBAL GIT_CONFIG_SYSTEM GIT_CONFIG_NOSYSTEM GIT_TERMINAL_PROMPT GIT_ASKPASS GIT_SSH GIT_SSH_COMMAND GIT_EDITOR GIT_PAGER GIT_EXTERNAL_DIFF 2>/dev/null || true
export LC_ALL=C GIT_OPTIONAL_LOCKS=0
usage() { printf '%s\n' 'Usage: bash tools/souji-pre-report-gate.sh --lane ABS --branch NAME --report ABS --prereg ABS' >&2; }
usage_error() { usage; exit 2; }
lane= branch= report= prereg=
seen_lane=0 seen_branch=0 seen_report=0 seen_prereg=0
while (($#)); do
  case $1 in
    --lane) (( $# >= 2 && !seen_lane )) || usage_error; lane=$2; seen_lane=1; shift 2 ;;
    --branch) (( $# >= 2 && !seen_branch )) || usage_error; branch=$2; seen_branch=1; shift 2 ;;
    --report) (( $# >= 2 && !seen_report )) || usage_error; report=$2; seen_report=1; shift 2 ;;
    --prereg) (( $# >= 2 && !seen_prereg )) || usage_error; prereg=$2; seen_prereg=1; shift 2 ;;
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
# 2. Report must exist and contain bytes.
if [[ -s $report ]]; then check report PASS; else check report FAIL; fi
# 3. Exactly one canonical heading.
shonen_count=$(grep -c '^## SHONEN' "$report" 2>/dev/null || true)
if [[ $shonen_count == 1 ]]; then check shonen PASS; else check shonen FAIL; printf 'detail-shonen: found %s headings, expected 1\n' "${shonen_count:-0}" >&2; fi
# 4. No lane changes may remain before report filing.
if status=$(git --no-optional-locks -C "$lane" status --porcelain=v1 --untracked-files=all 2>&1); then
  if [[ -z $status ]]; then check clean PASS; else check clean FAIL; printf 'detail-clean: %s\n' "$status" >&2; fi
else check clean FAIL; printf 'detail-clean: git status failed: %s\n' "$status" >&2; fi
# 5. The preregistration is mandatory; absence is never skipped.
if [[ -s $prereg ]]; then check prereg PASS; else check prereg FAIL; fi
exit "$fail"
