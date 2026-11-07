#!/usr/bin/env bash
# souji r82 receipt helper (successor of census/round-80/rec.sh): rec.sh OUT BIND1[,BIND2...] -- CMD ARGS...
# Runs CMD from the lane root, writes a header (command, cwd, lane master, host, git, launch dispositions,
# sha256 AND mode of every BIND path), the combined stdout+stderr, and a final EXIT=<rc>. Refuses an existing OUT.
# r81 changes (r80 spot-check routed defects 2 and 5): a BIND path may be absolute (a scratch copy the command
# executes, or a fleet script such as scripts/sources-census.sh), so a receipt binds the bytes it actually ran,
# never a lane file of the same name; every bind line also records the file's octal mode.
set -u
out=$1 binds=$2; shift 2
[[ ${1:-} == -- ]] || { echo 'usage: rec.sh OUT BINDS -- CMD...' >&2; exit 2; }
shift
lane=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
[[ -e $out ]] && { echo "rec.sh: $out exists" >&2; exit 2; }
_abs() { case $1 in /*) printf '%s' "$1" ;; *) printf '%s/%s' "$lane" "$1" ;; esac; }
IFS=, read -r -a _bl <<< "$binds"
(( ${#_bl[@]} )) || { echo "rec.sh: no BIND path" >&2; exit 2; }
for _b in "${_bl[@]}"; do [[ -n $_b && -f $(_abs "$_b") ]] || { echo "rec.sh: BIND path not a file: $_b" >&2; exit 2; }; done
mkdir -p "$(dirname "$out")"
{
  first=${binds%%,*}
  printf 'command=%s\n' "$*"
  printf 'rev=%s\n' "$(git -C "$lane" rev-parse master)"
  printf 'instrument=%s\n' "$first"
  printf 'instrument_sha256=%s\n' "$(sha256sum -- "$(_abs "$first")" | cut -d' ' -f1)"
  printf '# cwd=lane root; host=%s; git=%s\n' "$(uname -sr)" "$(git --version | awk '{print $3}')"
  printf 'launch=pid=%s pgid=%s sid=%s sigign=%s sigblk=%s stdin_tty=%s\n' "$$" "$(ps -o pgid= -p $$ | tr -d ' ')" \
    "$(ps -o sid= -p $$ | tr -d ' ')" "$(awk '/^SigIgn:/{print $2}' /proc/$$/status)" \
    "$(awk '/^SigBlk:/{print $2}' /proc/$$/status)" "$([[ -t 0 ]] && echo y || echo n)"
  for b in "${_bl[@]}"; do
    printf '# bind %s sha256=%s mode=%s\n' "$b" "$(sha256sum -- "$(_abs "$b")" | cut -d' ' -f1)" "$(stat -c %a -- "$(_abs "$b")")"
  done
} > "$out"
(cd "$lane" && "$@") >> "$out" 2>&1
rc=$?
printf 'EXIT=%s\n' "$rc" >> "$out"
exit 0
