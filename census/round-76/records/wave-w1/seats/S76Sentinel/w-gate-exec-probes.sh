#!/usr/bin/env bash
# S76Sentinel: config-driven code-execution probes against the W gate's check 4.
# Each route installs a repo-local config that git might honour, points it at a marker script,
# and reports whether the marker fired and what the gate's clean verdict was.
set -u
S=${S:-/fast/scratch/hyaku/souji-r76/S76Sentinel}
G=$S/G
REP=$S/report.md
PRE=$S/prereg.txt
printf '## SHONEN\nx\n' >"$REP"
printf 'prereg body\n' >"$PRE"

mkfx() {
  local d
  d=$(mktemp -d -p "$S" fx.XXXXXX) || return 1
  [ -n "$d" ] && [ -d "$d" ] || { echo "EMPTY-FIXTURE-PATH" >&2; exit 1; }
  git -C "$d" init -q || exit 1
  [ "$(git -C "$d" rev-parse --show-toplevel)" = "$d" ] || { echo "FIXTURE-TOPLEVEL-MISMATCH" >&2; exit 1; }
  printf 'base\n' >"$d/README.md"
  printf '__pycache__/\n' >"$d/.gitignore"
  git -C "$d" -c user.name=fx -c user.email=fx@fx add -A || exit 1
  git -C "$d" -c user.name=fx -c user.email=fx@fx commit -q -m base || exit 1
  echo "$d"
}
marker() { # $1 = fixture ; prints marker path ; the hook script writes to it
  local m="$S/fired.$$.$(basename "$1")"
  rm -f "$m"
  cat >"$S/evil.sh" <<EOF
#!/bin/sh
printf 'EXEC-RAN %s\n' "\$*" >>"$m"
printf '[]\n' 2>/dev/null
exit 0
EOF
  chmod +x "$S/evil.sh"
  echo "$m"
}
run_gate() {
  local lane=$1 out rc
  out=$(bash "$G/souji-pre-report-gate.sh" --lane "$lane" --branch main \
        --report "$REP" --prereg "$PRE" 2>&1); rc=$?
  printf '%s\n' "$out" | grep -E '^check-(clean)=|^detail-clean:' | sed 's/^/    /'
  printf '    gate-rc=%s\n' "$rc"
}

case ${1:-} in
fsmonitor) # repo-local core.fsmonitor = evil.sh  (should be pinned false by the gate)
  d=$(mkfx); m=$(marker "$d"); git -C "$d" config core.fsmonitor "$S/evil.sh"
  echo "ROUTE fsmonitor fixture=$d marker=$m"; run_gate "$d"
  [ -e "$m" ] && { echo "    MARKER FIRED:"; sed 's/^/      /' "$m"; } || echo "    marker absent (no exec)" ;;
fsmonitor-nogateopt) # same but through a plain status, to show the vector exists when unpinned
  d=$(mkfx); m=$(marker "$d"); git -C "$d" config core.fsmonitor "$S/evil.sh"
  echo "ROUTE fsmonitor-nogateopt fixture=$d"
  git -C "$d" -c core.fsmonitor="$S/evil.sh" status --porcelain >/dev/null 2>&1
  git -C "$d" -c core.fsmonitor="$S/evil.sh" --no-optional-locks status --porcelain >/dev/null 2>&1
  [ -e "$m" ] && { echo "    MARKER FIRED:"; sed 's/^/      /' "$m"; } || echo "    marker absent (no exec)" ;;
alias-shadow) # alias.check-ignore must not shadow the builtin
  d=$(mkfx); m=$(marker "$d"); git -C "$d" config alias.check-ignore "!$S/evil.sh"
  git -C "$d" config alias.ls-files "!$S/evil.sh"
  echo "ROUTE alias-shadow fixture=$d"; run_gate "$d"
  [ -e "$m" ] && { echo "    MARKER FIRED:"; sed 's/^/      /' "$m"; } || echo "    marker absent (no exec)" ;;
hooks-path) # core.hooksPath: no hook is run by status/ls-files/check-ignore
  d=$(mkfx); m=$(marker "$d"); mkdir -p "$S/hooks"
  for h in pre-commit post-index-change reference-transaction fsmonitor-watchman; do
    printf '#!/bin/sh\nprintf "EXEC-RAN %s\\n" >>"%s"\nexit 0\n' "$h" "$m" >"$S/hooks/$h"; chmod +x "$S/hooks/$h"
  done
  git -C "$d" config core.hooksPath "$S/hooks"
  echo "ROUTE hooks-path fixture=$d"; run_gate "$d"
  [ -e "$m" ] && { echo "    MARKER FIRED:"; sed 's/^/      /' "$m"; } || echo "    marker absent (no exec)" ;;
pager) # core.pager must not be spawned by check-ignore/ls-files
  d=$(mkfx); m=$(marker "$d"); git -C "$d" config core.pager "$S/evil.sh"
  git -C "$d" config pager.check-ignore "$S/evil.sh"
  echo "ROUTE pager fixture=$d"; run_gate "$d"
  [ -e "$m" ] && { echo "    MARKER FIRED:"; sed 's/^/      /' "$m"; } || echo "    marker absent (no exec)" ;;
excludesfile-outside) # repo-local core.excludesFile outside the tree hides a payload
  d=$(mkfx); printf 'hidden.bin\n' >"$S/excl-outside"
  git -C "$d" config core.excludesFile "$S/excl-outside"; printf 'h\n' >"$d/hidden.bin"
  echo "ROUTE excludesfile-outside fixture=$d"; run_gate "$d" ;;
git-execpath) # caller GIT_EXEC_PATH reaches git ls-remote's remote helper (check 1)
  d=$(mkfx); m="$S/fired.execepath"; rm -f "$m"; mkdir -p "$S/fakeexec"
  printf '#!/bin/sh\nprintf "EXEC-RAN remote-helper %%s\\n" "$*" >>"%s"\nexit 1\n' "$m" >"$S/fakeexec/git-remote-https"
  chmod +x "$S/fakeexec/git-remote-https"
  git -C "$d" remote add origin https://127.0.0.1:1/x.git
  echo "ROUTE git-execpath fixture=$d"
  GIT_EXEC_PATH="$S/fakeexec" timeout 20 git -C "$d" ls-remote --exit-code origin refs/heads/master 2>&1 | sed 's/^/    /'
  [ -e "$m" ] && { echo "    MARKER FIRED:"; sed 's/^/      /' "$m"; } || echo "    marker absent (no exec)" ;;

*) echo "unknown route ${1:-}" >&2; exit 2 ;;
esac
