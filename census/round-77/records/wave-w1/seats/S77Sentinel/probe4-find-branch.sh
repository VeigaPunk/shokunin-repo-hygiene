#!/usr/bin/env bash
# S77Sentinel probe 4: the find branch of nonreg_sources — cost, newline names, unreadable dirs,
# glob metacharacters in the lane path (prune failure), and the swallowed-error fail-open.
set -u
S=/fast/scratch/hyaku/souji-r77/S77Sentinel
mkdir -p "$S" || exit 1
D=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] || exit 1
trap 'chmod -R u+rwX "$D" 2>/dev/null; rm -rf -- "$D"' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }

scan() { # exactly the gate's find expression
  local lane=$1
  find "$lane" -path "$lane/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print 2>/dev/null | wc -l
}

echo "=== A. cost on the real lane (same expression) ==="
L=/home/vgpnk/Projects/shokunin/souji-shokunin
/usr/bin/time -f 'lane find: %e s, maxrss %M KiB' bash -c 'find "$1" -path "$1/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print 2>/dev/null | wc -l' _ "$L"

echo "=== B. 200k-entry ignored tree ==="
mkdir -p "$D/big"
python3 - "$D/big" <<'PY'
import os, sys
root = sys.argv[1]
for i in range(200000):
    d = os.path.join(root, f"d{i//1000:03d}")
    if i % 1000 == 0: os.makedirs(d, exist_ok=True)
    open(os.path.join(d, f"f{i:06d}.bin"), "wb").close()
PY
/usr/bin/time -f '200k find: %e s, maxrss %M KiB' bash -c 'find "$1" -path "$1/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print 2>/dev/null | wc -l' _ "$D"
rm -rf "$D/big"
echo "entries removed"

echo "=== C. newline in a directory name: count inflation, never deflation ==="
mkdir -p "$D/plain" "$D/$(printf 'a\nb')"
mkfifo "$D/plain/.gitignore"
echo "one FIFO .gitignore, plain dirs: count=$(scan "$D")"
rm -f "$D/plain/.gitignore"; rmdir "$D/plain"
mkfifo "$D/$(printf 'a\nb')/.gitignore"
echo "one FIFO .gitignore, newline dir: count=$(scan "$D")"
rm -f "$D/$(printf 'a\nb')/.gitignore"; rmdir "$D/$(printf 'a\nb')"

echo "=== D. unreadable directory: find errors, pipeline rc=0, count=0 ==="
mkdir -p "$D/locked"; mkfifo "$D/locked/.gitignore"; chmod 000 "$D/locked"
f=$(find "$D" -path "$D/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print 2>/dev/null | wc -l); rc=$?
echo "pipeline rc=$rc count=$f   (FIFO exists inside mode-000 dir)"
find "$D" -path "$D/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print > /dev/null 2>&1; echo "find FOREGROUND rc=$?"
chmod 755 "$D/locked"; rm -f "$D/locked/.gitignore"; rmdir "$D/locked"

echo "=== E. glob metacharacter in the lane path defeats -path prune ==="
G="$S/lane[1].XXXXXX"
G=$(mktemp -d -p "$S" 'lane[1].XXXXXX') || exit 1
[ -n "$G" ] && [ -d "$G" ] || exit 1
git -C "$G" init -q || exit 1
[ "$(git -C "$G" rev-parse --show-toplevel)" = "$G" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }
mkfifo "$G/.git/info/nonreg-marker.gitignore"
echo "lane path: $G"
echo "with the real prune expression, .git reached? "
find "$G" -path "$G/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print 2>/dev/null | sed "s|^$G|<LANE>|" | head -3
echo "prune -path literal would be: $G/.git"
echo "count=$(scan "$G")"
rm -rf -- "$G"
