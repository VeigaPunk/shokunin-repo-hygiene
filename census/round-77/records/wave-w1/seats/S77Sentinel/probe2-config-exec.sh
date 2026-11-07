#!/usr/bin/env bash
# S77Sentinel probe 2: can repo-local config make the W pre-check calls EXECUTE code?
# Vectors: core.fsmonitor, core.hooksPath + hook, alias shadowing, core.pager, filter.*, include.path exec?
set -u
S=/fast/scratch/hyaku/souji-r77/S77Sentinel
mkdir -p "$S" || exit 1
D=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
M=$(mktemp -d -p "$S" mk.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] && [ -n "$M" ] && [ -d "$M" ] || exit 1
trap 'rm -rf -- "$D" "$M"' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }
git -C "$D" -c user.name=p -c user.email=p@x commit -q --allow-empty -m base || exit 1

cat > "$M/hook.sh" <<'EOF'
#!/bin/sh
printf 'RAN %s\n' "$0" >> "$MARKER"
exit 0
EOF
chmod +x "$M/hook.sh"
printf '%s\n' "$M/hook.sh" > "$M/hookpath"

git -C "$D" config core.fsmonitor "$M/hook.sh"
git -C "$D" config core.hooksPath "$M"
git -C "$D" config alias.rev-parse '!echo ALIAS-RAN'
git -C "$D" config core.pager "$M/hook.sh"
git -C "$D" config diff.external "$M/hook.sh"

export MARKER="$M/marker"
: > "$MARKER"
probe() {
  local name=$1; shift
  local rc out
  out=$(setsid timeout -k 5 10 "$@" 2>&1); rc=$?
  printf '%-45s rc=%-3s out=%q\n' "$name" "$rc" "$out"
}
probe "rev-parse --absolute-git-dir" git -C "$D" rev-parse --absolute-git-dir
echo "marker after rev-parse: [$(cat "$MARKER")]"
probe "config --path --get core.excludesFile" git -C "$D" config --path --get core.excludesFile
echo "marker after config: [$(cat "$MARKER")]"
probe "status --porcelain" git -C "$D" --no-optional-locks status --porcelain
echo "marker after status: [$(cat "$MARKER")]"
: > "$MARKER"
echo "--- marker reset; second status run ---"
probe "status #2" git -C "$D" --no-optional-locks status --porcelain
echo "marker after status#2: [$(cat "$MARKER")]"
echo "--- log path resolved or not ---"
git -C "$D" config --get core.fsmonitor
