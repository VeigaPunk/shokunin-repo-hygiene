#!/bin/sh
# w2-w3-env-probe.sh — round-66 L1 probes for the two residual routes measured on base and landed candidate.
#   W2: GIT_COMMON_DIR pointing at a copy of .git whose config sets core.fileMode=false hides a tracked
#       755->644 change from the clean-tree check; the writer (no --allow-dirty) should refuse, it accepts.
#   W3: a writer launched with GIT_CONFIG_PARAMETERS set (as git sets for children of `git -c`) is refused by
#       the candidate and accepted by base.
# Usage: sh census/round-66/probes/w2-w3-env-probe.sh LANE BASE_REV LANDED_REV WORK
# Writes only under WORK (must not be under /tmp). Read-only against LANE (git show / git -C reads).
set -eu
LANE=$1; BASE=$2; LAND=$3; WORK=$4
case "$WORK" in /tmp/*|/var/tmp/*) echo "refused: WORK under /tmp" >&2; exit 2;; esac
rm -rf "$WORK"; mkdir -p "$WORK/base" "$WORK/cand"
git -C "$LANE" show "$BASE:tools/souji-receipt-write.py" > "$WORK/base-writer.py"
git -C "$LANE" show "$LAND:tools/souji-receipt-write.py" > "$WORK/cand-writer.py"
D="$WORK/repo"; git init -q "$D"
printf 'tracked\n' > "$D/tool.sh"; chmod 755 "$D/tool.sh"
git -C "$D" -c user.name=L1 -c user.email=l1@example.invalid add tool.sh
git -C "$D" -c user.name=L1 -c user.email=l1@example.invalid commit -q -m seed
R=$(git -C "$D" rev-parse HEAD)
chmod 644 "$D/tool.sh"                      # tracked mode change, uncommitted
cp -r "$D/.git" "$WORK/common"; git config --file "$WORK/common/config" core.fileMode false
echo "W2 status without GIT_COMMON_DIR: $(git -C "$D" status --porcelain | wc -l) line(s)"
echo "W2 status with    GIT_COMMON_DIR: $(GIT_COMMON_DIR="$WORK/common" git -C "$D" status --porcelain | wc -l) line(s)"
for W in base cand; do
  set +e
  GIT_COMMON_DIR="$WORK/common" python3 -B "$WORK/$W-writer.py" --root "$D" --rev "$R" --instrument tool.sh \
     --out "$WORK/$W/w2.out" --allow-outside --command "/bin/echo hi" > "$WORK/$W/w2.log" 2>&1
  echo "W2 $W writer rc=$? ($(head -1 "$WORK/$W/w2.log" | cut -c1-70))"
  set -e
done
# W3: a clean tree, GIT_CONFIG_PARAMETERS set as git sets it for children of `git -c`.
git -C "$D" checkout -q -- tool.sh 2>/dev/null || chmod 755 "$D/tool.sh"
for W in base cand; do
  set +e
  GIT_CONFIG_PARAMETERS="'foo.bar=1'" python3 -B "$WORK/$W-writer.py" --root "$D" --rev "$R" --instrument tool.sh \
     --out "$WORK/$W/w3.out" --allow-outside --command "/bin/echo hi" > "$WORK/$W/w3.log" 2>&1
  echo "W3 $W writer rc=$? ($(head -1 "$WORK/$W/w3.log" | cut -c1-70))"
  set -e
done
