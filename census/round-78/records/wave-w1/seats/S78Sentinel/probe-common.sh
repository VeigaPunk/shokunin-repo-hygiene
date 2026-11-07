# probe-common.sh — shared fixture factory for S78Sentinel probes (r78 W gate).
# Writes only under /fast/scratch/hyaku/souji-r78/S78Sentinel/.
H=/fast/scratch/hyaku/souji-r78/S78Sentinel
mkdir -p "$H" || exit 1
GATE=$H/D/souji-pre-report-gate.sh
prep() { mkdir -p "$H/D"
  git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ed22dc9c:tools/souji-pre-report-gate.sh > "$GATE"
  git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ed22dc9c:tools/souji-receipt-write.py > "$H/D/souji-receipt-write.py"
  sha256sum "$GATE"; }
mkfix() { D=$(mktemp -d -p "$H" fx.XXXXXX) || exit 1
  [ -n "$D" ] && [ -d "$D" ] || exit 1
  git -C "$D" init -q || exit 1
  [ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo TOPLEVEL-MISMATCH >&2; exit 1; }
  printf '## SHONEN\nx\n' > "$D/report.md"; echo x > "$D/prereg.txt"; echo "$D"; }
rungate() { timeout -k 5 "${T:-120}" bash "$GATE" --lane "$D" --branch master --report "$D/report.md" --prereg "$D/prereg.txt"; }
