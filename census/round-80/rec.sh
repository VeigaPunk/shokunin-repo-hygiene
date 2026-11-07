#!/usr/bin/env bash
# souji r80 receipt helper (copy of census/round-79/rec.sh, plus the launch line routed by the r79 spot-check,
# defect 1: the disposition this helper and so CMD inherited): rec.sh OUT BIND1[,BIND2...] -- CMD ARGS...
# Runs CMD from the lane root, writes a header (command, cwd, lane master, host, git, sha256 of every
# lane-relative BIND path), the combined stdout+stderr, and a final EXIT=<rc>. Refuses an existing OUT.
set -u
out=$1 binds=$2; shift 2
[[ ${1:-} == -- ]] || { echo 'usage: rec.sh OUT BINDS -- CMD...' >&2; exit 2; }
shift
lane=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
[[ -e $out ]] && { echo "rec.sh: $out exists" >&2; exit 2; }
# r76 lesson M1: a BIND path that is not a regular file wrote an empty instrument_sha256= (census-before,
# first attempt); refuse before writing anything.
IFS=, read -r -a _bl <<< "$binds"
(( ${#_bl[@]} )) || { echo "rec.sh: no BIND path" >&2; exit 2; }
for _b in "${_bl[@]}"; do [[ -n $_b && -f $lane/$_b ]] || { echo "rec.sh: BIND path not a file: $_b" >&2; exit 2; }; done
mkdir -p "$(dirname "$out")"
{
  first=${binds%%,*}
  printf 'command=%s\n' "$*"
  printf 'rev=%s\n' "$(git -C "$lane" rev-parse master)"
  printf 'instrument=%s\n' "$first"
  printf 'instrument_sha256=%s\n' "$(sha256sum -- "$lane/$first" | cut -d' ' -f1)"
  printf '# cwd=lane root; host=%s; git=%s\n' "$(uname -sr)" "$(git --version | awk '{print $3}')"
  printf 'launch=pid=%s pgid=%s sid=%s sigign=%s sigblk=%s stdin_tty=%s\n' "$$" "$(ps -o pgid= -p $$ | tr -d ' ')" \
    "$(ps -o sid= -p $$ | tr -d ' ')" "$(awk '/^SigIgn:/{print $2}' /proc/$$/status)" \
    "$(awk '/^SigBlk:/{print $2}' /proc/$$/status)" "$([[ -t 0 ]] && echo y || echo n)"
  IFS=, read -r -a bl <<< "$binds"
  for b in "${bl[@]}"; do [[ -n $b ]] && printf '# bind %s sha256=%s\n' "$b" "$(sha256sum -- "$lane/$b" | cut -d' ' -f1)"; done
} > "$out"
(cd "$lane" && "$@") >> "$out" 2>&1
rc=$?
printf 'EXIT=%s\n' "$rc" >> "$out"
exit 0
