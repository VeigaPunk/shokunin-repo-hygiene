#!/usr/bin/env bash
# S77Sentinel probe 5: route table of the real W gate blob against each non-regular-source vector.
# Also: does the refusal echo a path (D30)? How long does a refusal take?
set -u
S=/fast/scratch/hyaku/souji-r77/S77Sentinel
R=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-77/w1/S77Sentinel
mkdir -p "$S" || exit 1
GATE="$S/gateW/souji-pre-report-gate.sh"
[ -f "$GATE" ] || { echo "missing gate copy"; exit 1; }
M=$(mktemp -d -p "$S" mk.XXXXXX) || exit 1
[ -n "$M" ] && [ -d "$M" ] || exit 1
printf '## SHONEN\n' > "$M/report.md"
printf 'x\n' > "$M/prereg.txt"
X=$(mktemp -d -p "$S" xdg.XXXXXX) || exit 1
export XDG_CONFIG_HOME="$X"

run_case() { # name, mutation-callback
  local name=$1 mut=$2
  local D; D=$(mktemp -d -p "$S" fx.XXXXXX) || return 1
  [ -n "$D" ] && [ -d "$D" ] || return 1
  git -C "$D" init -q || return 1
  [ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; return 1; }
  git -C "$D" -c user.name=p -c user.email=p@x commit -q --allow-empty -m base || return 1
  "$mut" "$D" || { echo "$name: MUTATION FAILED"; return 1; }
  local t0 t1 out rc
  t0=$(date +%s%N)
  out=$(setsid timeout -k 5 20 bash "$GATE" --lane "$D" --branch nosuch --report "$M/report.md" --prereg "$M/prereg.txt" 2>&1); rc=$?
  t1=$(date +%s%N)
  local ms=$(( (t1 - t0) / 1000000 ))
  local clean detail
  clean=$(printf '%s\n' "$out" | grep '^check-clean=' || true)
  detail=$(printf '%s\n' "$out" | grep '^detail-clean:' | head -2)
  # scrub the fixture path to prove no path echo
  local leaked=no
  printf '%s\n%s\n' "$clean" "$detail" | grep -qF "$D" && leaked=YES
  printf '%-26s %-16s rc=%-3s %sms leaked_path=%s\n' "$name" "${clean:-<none>}" "$rc" "$ms" "$leaked"
  [[ -n $detail ]] && printf '    %s\n' "$(printf '%s\n' "$detail" | sed "s|$D|<FIXTURE>|g" | cut -c1-150 | tr '\n' ' ')"
  # kill anything left
  for pid in $(ps -eo pid,args | grep -F "$D" | grep -v grep | awk '{print $1}'); do kill -KILL "$pid" 2>/dev/null; done
  rm -rf -- "$D"
  return 0
}

m_none() { :; }
m_wt_fifo_gitignore() { mkfifo "$1/.gitignore"; }
m_wt_fifo_gitattributes() { mkdir -p "$1/sub"; mkfifo "$1/sub/.gitattributes"; }
m_info_exclude_fifo() { mkfifo "$1/.git/info/exclude.tmp"; rm -f "$1/.git/info/exclude"; mv "$1/.git/info/exclude.tmp" "$1/.git/info/exclude"; }
m_info_attributes_fifo() { rm -f "$1/.git/info/attributes"; mkfifo "$1/.git/info/attributes"; }
m_excludesfile_fifo() { mkfifo "$1/fx.excl"; git -C "$1" config core.excludesFile "$1/fx.excl"; }
m_excludesfile_dir() { mkdir "$1/excldir"; git -C "$1" config core.excludesFile "$1/excldir"; }
m_attributesfile_fifo() { mkfifo "$1/fx.attr"; git -C "$1" config core.attributesFile "$1/fx.attr"; }
m_xdg_default_fifo() { mkdir -p "$XDG_CONFIG_HOME/git"; mkfifo "$XDG_CONFIG_HOME/git/ignore"; }
m_xdg_default_regular() { mkdir -p "$XDG_CONFIG_HOME/git"; : > "$XDG_CONFIG_HOME/git/ignore"; }
m_symlink_to_regular() { : > "$1/real-ignore"; ln -s real-ignore "$1/.gitignore"; }
m_symlink_dangling() { ln -s /nonexistent-target "$1/.gitignore"; }
m_dir_named_gitignore() { mkdir "$1/.gitignore"; }
m_fifo_in_ignored_dir() { printf 'sub/\n' > "$1/.gitignore"; mkdir "$1/sub"; mkfifo "$1/sub/.gitignore"; }
m_socket_gitignore() { python3 -c 'import socket,sys; s=socket.socket(socket.AF_UNIX); s.bind(sys.argv[1])' "$1/.gitignore"; }
m_regular_gitignore() { printf 'x\n' > "$1/.gitignore"; }
m_include_path_fifo() { mkfifo "$1/inc.cfg"; git -C "$1" config include.path "$1/inc.cfg"; }

echo "gate sha256: $(sha256sum "$GATE" | cut -d' ' -f1)"
for c in none:1 wt_fifo_gitignore:2 wt_fifo_gitattributes:3 info_exclude_fifo:4 info_attributes_fifo:5 \
         excludesfile_fifo:6 excludesfile_dir:7 attributesfile_fifo:8 xdg_default_fifo:9 xdg_default_regular:10 \
         symlink_to_regular:11 symlink_dangling:12 dir_named_gitignore:13 fifo_in_ignored_dir:14 \
         socket_gitignore:15 regular_gitignore:16 include_path_fifo:17; do
  name=${c%%:*}; f=$(printf '%s' "$c#*" | cut -d: -f2)
  run_case "$name" "m_$name"
  rm -f "$X/git/ignore" 2>/dev/null
done
echo "--- leftover processes referencing scratch fixtures ---"
ps -eo pid,args | grep -F "$S/fx." | grep -v grep | cut -c1-120 || echo none
