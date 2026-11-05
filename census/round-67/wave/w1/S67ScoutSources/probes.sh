#!/bin/sh
# S67ScoutSources behavioural probe receipt (round 67 C1 GIT_COMMON_DIR).
# Read-only against the lane; all fixtures live under the scratch root passed as $1.
# Usage: probes.sh <scratch-dir>
set -u
S="${1:?scratch dir required}"
mkdir -p "$S"
D=$(mktemp -d -p "$S" probe.XXXXXX)
trap 'rm -rf -- "$D"' EXIT
cd "$D" || exit 2

echo "# git version"
git --version

echo
echo "# fixture: repo $D/main, tracked file mode 644 in the index, worktree 755"
git init -q "$D/main" || exit 2
cd "$D/main" || exit 2
git config user.email a@b.c
git config user.name a
echo x > f
git add f
git commit -qm c
chmod 755 f

echo
echo "# A) baseline (no injection): the 755->644 tracked mode change IS reported"
git status --porcelain; echo "   rc=$?"

echo
echo "# B) injected GIT_COMMON_DIR = a copy of .git whose config sets core.fileMode=false"
cp -a .git "$D/copygit"
printf '[core]\n\tfileMode = false\n' >> "$D/copygit/config"
GIT_COMMON_DIR="$D/copygit" git status --porcelain; echo "   rc=$? (empty output above = mode change hidden)"

echo
echo "# C) empty GIT_COMMON_DIR: git takes the env branch and then finds no repository"
GIT_COMMON_DIR= git rev-parse --git-common-dir 2>&1; echo "   rc=$?"
GIT_COMMON_DIR= git ls-files 2>&1 | head -2; echo "   rc=$?"

echo
echo "# D) mismatching GIT_COMMON_DIR with no config: git reports not a git repository"
mkdir -p "$D/alt"
GIT_COMMON_DIR="$D/alt" git rev-parse --git-common-dir 2>&1; echo "   rc=$?"

echo
echo "# E) the injected value is what git reports as the common dir (no canonicalization of the text)"
GIT_COMMON_DIR="$D/copygit" git rev-parse --git-common-dir 2>&1
ln -s "$D/main/.git" "$D/gitlink"
GIT_COMMON_DIR="$D/gitlink" git rev-parse --git-common-dir 2>&1
GIT_COMMON_DIR="$D/gitlink" git rev-parse --path-format=absolute --git-common-dir 2>&1

echo
echo "# F) relative env value is interpreted from the worktree top level, not the writer cwd"
mkdir -p sub
cd sub || exit 2
GIT_COMMON_DIR=../.git git -C "$D/main/sub" rev-parse --path-format=absolute --git-common-dir 2>&1
echo "   (expected base: $D/main -> ../.git == $D/.git ; writer-cwd base would be $PWD/../.git)"

echo
echo "# G) worktree child env: git exports GIT_DIR and GIT_WORK_TREE, never GIT_COMMON_DIR"
cd "$D/main" || exit 2
mkdir -p .git/hooks
printf '#!/bin/sh\nenv | grep -E "^GIT_(COMMON_DIR|DIR|WORK_TREE)=" | sort > %s/hookenv.txt\n' "$D" > .git/hooks/post-checkout
chmod +x .git/hooks/post-checkout
rm -f "$D/hookenv.txt"
git worktree add -q "$D/wt" -b wtb >/dev/null 2>&1
# the post-checkout hook fires on a checkout inside the linked worktree
( cd "$D/wt" && git checkout -q wtb ) >/dev/null 2>&1
echo "   hook env inside the new worktree (no GIT_COMMON_DIR line expected):"
cat "$D/hookenv.txt" 2>/dev/null || echo "   (no hook output)"
echo "   with GIT_COMMON_DIR exported in the parent, the child inherits it verbatim:"
rm -f "$D/hookenv.txt"
GIT_COMMON_DIR="$D/main/.git" git -C "$D/wt" checkout -q wtb >/dev/null 2>&1
cat "$D/hookenv.txt" 2>/dev/null || echo "   (no hook output)"

echo
echo "# H) submodule path in git's own source bypasses the env (worktree.c:553-556)"
echo "   (source evidence; see quotes.tsv rows for worktree.txt offsets 14166)"
