#!/usr/bin/env bash
# probe-resource.sh — S74Sentinel: hang / memory probes against the stage-W gate.
#   R1 tracked path replaced by a FIFO
#   R2 tracked symlink replaced by a symlink loop (a -> a)
#   R3 tracked 2 GiB sparse regular file (committed, stat-clean)
#   R4 index with 200 000 entries
#   R5 --report is a FIFO            (prediction: grep -c blocks)
#   R6 --report is /dev/zero         (prediction: grep -c never terminates)
#   R7 --prereg is a FIFO            (prediction: [[ -s ]] is false, no read, FAIL)
# Every run is bounded by `timeout`; VERDICT=HANG is exit 124.
# Usage: probe-resource.sh <SCRATCH> <gate-dir>
set -u
S=${1:?scratch}; GATE_DIR=${2:?gate dir}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
MK="$HERE/mkfixture.py"
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"

fresh() { local r=$1; rm -rf "$r"; python3 -B "$MK" --root "$r" >/dev/null
  printf '# Report\n\n## SHONEN\n[~] box `a`\n' > "$r/report.md"; printf 'prereg\n' > "$r/prereg.txt"; }

measure() {  # measure <label> <root> <budget-s> [--report X] [--prereg Y]
  local label=$1 r=$2 bud=$3; shift 3
  local rep="$r/report.md" pre="$r/prereg.txt"
  while [ $# -gt 0 ]; do case "$1" in --report) rep=$2; shift 2;; --prereg) pre=$2; shift 2;; *) shift;; esac; done
  local tf="$r/time.txt"
  ( cd "$r/lane" && /usr/bin/time -f 'wall=%e rss_kb=%M' -o "$tf" \
      timeout "$bud" bash "$GATE_DIR/gate-w.sh" --lane "$r/lane" --branch master \
      --report "$rep" --prereg "$pre" ) > "$r/out.txt" 2>&1
  local rc=$?
  local v=ok; [ "$rc" = 124 ] && v=HANG; [ "$rc" != 0 ] && [ "$rc" != 124 ] && v="exit=$rc"
  printf '%-28s verdict=%-8s %s check-clean=%s\n' "$label" "$v" "$(cat "$tf" 2>/dev/null)" \
    "$(grep -E '^check-clean=' "$r/out.txt" | head -1 || echo '<absent>')"
}

echo "########## R1 tracked path replaced by a FIFO ##########"
R="$S/r1"; fresh "$R"
rm -f "$R/lane/a.txt"; mkfifo "$R/lane/a.txt"
echo "status-lines=$(git -C "$R/lane" status --porcelain=v1 --untracked-files=all | wc -l)"
measure R1-fifo "$R" 30

echo; echo "########## R2 tracked symlink loop (a -> a) ##########"
R="$S/r2"; rm -rf "$R"; python3 -B "$MK" --root "$R" >/dev/null
printf '# Report\n\n## SHONEN\n[~] box `a`\n' > "$R/report.md"; printf 'prereg\n' > "$R/prereg.txt"
ln -s tgt "$R/lane/a.txt" 2>/dev/null; rm -f "$R/lane/a.txt"; ln -s a.txt "$R/lane/a.txt"
echo "status-lines=$(git -C "$R/lane" status --porcelain=v1 --untracked-files=all | wc -l)"
measure R2-symlink-loop "$R" 30

echo; echo "########## R3 tracked 2 GiB sparse regular file ##########"
R="$S/r3"; fresh "$R"
truncate -s 2G "$R/lane/big.bin"
git -C "$R/lane" add big.bin && git -C "$R/lane" -c user.name=fixture -c user.email=f@example.invalid \
  -c commit.gpgsign=false commit -qm big && git -C "$R/lane" push -q origin master
echo "status-lines=$(git -C "$R/lane" status --porcelain=v1 --untracked-files=all | wc -l)"
measure R3-2GiB-sparse "$R" 300

echo; echo "########## R4 index with 200000 entries ##########"
R="$S/r4"; fresh "$R"
python3 - "$R/lane" <<'PY'
import os, sys
lane = sys.argv[1]
for i in range(200000):
    d = os.path.join(lane, "m%02d" % (i // 10000))
    if not os.path.isdir(d):
        os.makedirs(d)
    open(os.path.join(d, "f%06d.txt" % i), "wb").write(b"x")
PY
git -C "$R/lane" add -A
git -C "$R/lane" -c user.name=fixture -c user.email=f@example.invalid -c commit.gpgsign=false commit -qm many
git -C "$R/lane" push -q origin master
echo "index-entries=$(git -C "$R/lane" ls-files | wc -l) status-lines=$(git -C "$R/lane" status --porcelain=v1 --untracked-files=all | wc -l)"
measure R4-200k-index "$R" 600

echo; echo "########## R5 --report is a FIFO ##########"
R="$S/r5"; fresh "$R"; rm -f "$R/report.md"; mkfifo "$R/report.md"
measure R5-report-fifo "$R" 20

echo; echo "########## R6 --report is /dev/zero ##########"
R="$S/r6"; fresh "$R"
measure R6-report-devzero "$R" 20 --report /dev/zero

echo; echo "########## R7 --prereg is a FIFO ##########"
R="$S/r7"; fresh "$R"; rm -f "$R/prereg.txt"; mkfifo "$R/prereg.txt"
measure R7-prereg-fifo "$R" 20
