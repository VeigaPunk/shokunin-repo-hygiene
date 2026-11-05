#!/usr/bin/env bash
# S68ScoutReplace: git replace-ref fact experiment (read-only to the lane; scratch-only).
set -u
SEAT="${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r68/S68ScoutReplace"
D=$(mktemp -d -p "$SEAT" replaceexp.XXXXXX)
echo "FIXTURE_DIR=$D"
git -C "$D" init -q
TOP=$(git -C "$D" rev-parse --show-toplevel)
if [ "$TOP" != "$D" ]; then echo "ABORT: toplevel $TOP != $D"; exit 9; fi
echo "TOPLEVEL_OK=$TOP"
# scratch identity, inside this repo only
git -C "$D" config user.name "S68 Scratch Fixture"
git -C "$D" config user.email "s68-scratch@invalid"
git -C "$D" config core.fileMode false

mkdir -p "$D/tools"
printf 'REAL-BYTES\n' > "$D/tools/instr.sh"
chmod 0755 "$D/tools/instr.sh"
git -C "$D" add tools/instr.sh
git -C "$D" commit -q -m "real tree"
HEAD1=$(git -C "$D" rev-parse HEAD)
echo "HEAD1=$HEAD1"

# second commit (two trees in history)
printf 'REAL-BYTES-2\n' > "$D/tools/instr.sh"
git -C "$D" add tools/instr.sh
git -C "$D" commit -q -m "second real tree"
HEAD=$(git -C "$D" rev-parse HEAD)
echo "HEAD=$HEAD"
git -C "$D" log --oneline

# forged commit: same parent as HEAD, tree carrying FORGED instrument bytes
printf 'FORGED-BYTES\n' > "$SEAT/forged-instr.sh"
chmod 0755 "$SEAT/forged-instr.sh"
BLOB=$(git -C "$D" hash-object -w "$SEAT/forged-instr.sh")
echo "FORGED_BLOB=$BLOB"
IDX="$SEAT/forge-idx"
GIT_INDEX_FILE="$IDX" git -C "$D" read-tree "$HEAD"
GIT_INDEX_FILE="$IDX" git -C "$D" update-index --add --cacheinfo "100755,$BLOB,tools/instr.sh"
TREE=$(GIT_INDEX_FILE="$IDX" git -C "$D" write-tree)
echo "FORGED_TREE=$TREE"
export GIT_AUTHOR_DATE="2026-11-05T00:00:00Z" GIT_COMMITTER_DATE="2026-11-05T00:00:00Z"
export GIT_AUTHOR_NAME="R68 Fixture" GIT_AUTHOR_EMAIL="r68-fixture@invalid"
export GIT_COMMITTER_NAME="R68 Fixture" GIT_COMMITTER_EMAIL="r68-fixture@invalid"
REP=$(git -C "$D" commit-tree "$TREE" -p "$HEAD" -m "r68 forged replacement")
echo "REPLACEMENT_COMMIT=$REP"
unset GIT_AUTHOR_DATE GIT_COMMITTER_DATE GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL
git -C "$D" update-ref "refs/replace/$HEAD" "$REP"
echo "REPLACE_REF_LIST:"; git -C "$D" for-each-ref refs/replace/

# worktree + real index carry the forged bytes (as in the PK6 fixture)
printf 'FORGED-BYTES\n' > "$D/tools/instr.sh"
chmod 0755 "$D/tools/instr.sh"
git -C "$D" update-index --cacheinfo "100755,$BLOB,tools/instr.sh"

echo "===== A: replacement-honouring (no GIT_NO_REPLACE_OBJECTS) ====="
echo "-- git show HEAD:tools/instr.sh"
git -C "$D" show "HEAD:tools/instr.sh"; echo "rc=$?"
echo "-- git cat-file -p HEAD (tree line)"
git -C "$D" cat-file -p HEAD; echo "rc=$?"
echo "-- git status --porcelain"
git -C "$D" status --porcelain; echo "rc=$?"
echo "-- git ls-files -v"
git -C "$D" ls-files -v; echo "rc=$?"
echo "-- git rev-parse HEAD"
git -C "$D" rev-parse HEAD
echo "-- git show --stat --oneline HEAD"
git -C "$D" show --stat --oneline HEAD | head -5

echo "===== B: GIT_NO_REPLACE_OBJECTS=1 ====="
echo "-- git show HEAD:tools/instr.sh"
GIT_NO_REPLACE_OBJECTS=1 git -C "$D" show "HEAD:tools/instr.sh"; echo "rc=$?"
echo "-- git cat-file -p HEAD (tree line)"
GIT_NO_REPLACE_OBJECTS=1 git -C "$D" cat-file -p HEAD; echo "rc=$?"
echo "-- git status --porcelain"
GIT_NO_REPLACE_OBJECTS=1 git -C "$D" status --porcelain; echo "rc=$?"
echo "-- git ls-files -v"
GIT_NO_REPLACE_OBJECTS=1 git -C "$D" ls-files -v; echo "rc=$?"
echo "-- git rev-parse HEAD"
GIT_NO_REPLACE_OBJECTS=1 git -C "$D" rev-parse HEAD

echo "===== C: --no-replace-objects option (doc cross-check) ====="
git -C "$D" --no-replace-objects show "HEAD:tools/instr.sh"; echo "rc=$?"
git -C "$D" --no-replace-objects status --porcelain; echo "rc=$?"

echo "===== D: does a plain `git show <HEAD>:<path>` (not HEAD) differ? ====="
echo "-- show $HEAD1:tools/instr.sh (honouring)"
git -C "$D" show "$HEAD1:tools/instr.sh"
echo "-- show $HEAD1:tools/instr.sh (no-replace)"
GIT_NO_REPLACE_OBJECTS=1 git -C "$D" show "$HEAD1:tools/instr.sh"

echo "FIXTURE_DIR_FINAL=$D"
