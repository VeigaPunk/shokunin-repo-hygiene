#!/usr/bin/env bash
# S77Sentinel probe 6: linked-worktree lane — does --absolute-git-dir point at the dir git actually reads
# info/exclude from? If not, the guard misses the real source (fail-open of the guard).
set -u
S=/fast/scratch/hyaku/souji-r77/S77Sentinel
mkdir -p "$S" || exit 1
D=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] || exit 1
trap 'rm -rf -- "$D"' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 1; }
printf 'x\n' > "$D/f"; git -C "$D" add f
git -C "$D" -c user.name=p -c user.email=p@x commit -q -m base || exit 1
git -C "$D" worktree add -q "$D/wt" -b wtb || exit 1
[ "$(git -C "$D/wt" rev-parse --show-toplevel)" = "$D/wt" ] || { echo "WORKTREE TOPLEVEL MISMATCH"; exit 1; }
echo "worktree: $D/wt"
echo "--absolute-git-dir      : $(git -C "$D/wt" rev-parse --absolute-git-dir)"
echo "--git-path info/exclude : $(git -C "$D/wt" rev-parse --git-path info/exclude)"
echo "--git-path info/attributes: $(git -C "$D/wt" rev-parse --git-path info/attributes)"
echo "--git-common-dir        : $(git -C "$D/wt" rev-parse --git-common-dir)"
echo
echo "=== place a FIFO at the path git ACTUALLY reads (the --git-path answer) ==="
COMMON=$(cd "$D" && git rev-parse --git-common-dir)
case $COMMON in /*) ;; *) COMMON=$D/$COMMON ;; esac
EXC="$COMMON/info/exclude"
rm -f "$EXC"
mkfifo "$EXC" || exit 1
echo "FIFO at: $EXC"
echo "gate-style check path (wd/info/exclude under --absolute-git-dir): $(git -C "$D/wt" rev-parse --absolute-git-dir)/info/exclude"
if [ -e "$(git -C "$D/wt" rev-parse --absolute-git-dir)/info/exclude" ]; then
  echo "gate-style path EXISTS -> guard sees it"
else
  echo "gate-style path MISSING -> guard does not see the FIFO"
fi
echo
echo "=== does the guard's own expression count it? (find over the worktree cannot see the common dir) ==="
lane="$D/wt"
find "$lane" -path "$lane/.git" -prune -o \( -name .gitignore -o -name .gitattributes \) ! -type f -print 2>/dev/null | wc -l
echo "=== does git status actually read the FIFO (i.e. would it block)? ==="
out=$(setsid timeout -k 5 5 git -C "$D/wt" --no-optional-locks status --porcelain 2>&1); rc=$?
echo "git status rc=$rc out=$(printf '%q' "$out")"
echo "=== and via the receipt writer's -C? same repo, same answer ==="
