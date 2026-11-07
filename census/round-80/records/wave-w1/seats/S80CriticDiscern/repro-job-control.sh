#!/bin/bash
# S80CriticDiscern r80: F1 reproducer — tools/souji-quarantine.sh under a job-control launch.
# Usage: bash repro-job-control.sh [scratch-root]
# Runs the W2 candidate (836dac3e) twice on the same hang engine: one as committed, one with `set +m`
# inserted after the shebang. Prints the front's exit code, output lines and the surviving worker.
set -u
S=${1:-/fast/scratch/hyaku/souji-r80/S80CriticDiscern/repro}
L=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p "$S/tools" "$S/tmp"
git -C "$L" show 836dac3e336863c57d9d7125837ed22b22d8d044:tools/souji-quarantine.sh > "$S/tools/cand.sh"
sed '1a set +m' "$S/tools/cand.sh" > "$S/tools/fixed.sh"
chmod 0755 "$S/tools/cand.sh" "$S/tools/fixed.sh"
printf '#!/bin/bash\nexec sleep 600\n' > "$S/engine.sh"; chmod 0755 "$S/engine.sh"

cleanup() {
  python3 - "$S/tools/cand.sh" "$S/tools/fixed.sh" "$S/engine.sh" <<'PY'
import os, sys
pats, me = set(sys.argv[1:]), os.getpid()
left = []
for p in os.listdir('/proc'):
    if not p.isdigit() or int(p) == me:
        continue
    try:
        argv = [a.decode('utf8','replace') for a in open(f'/proc/{p}/cmdline','rb').read().split(b'\0')]
    except OSError:
        continue
    if any(a in pats for a in argv):
        left.append(p)
        try: os.kill(int(p), 9)
        except OSError: pass
print('cleanup_killed=%s' % (left or 'none'))
PY
}
trap cleanup EXIT

arm() {
  local tool=$1 label=$2 front
  : > "$S/out.$label"
  TMPDIR=$S/tmp SOUJI_VERIFY_BIN=$S/engine.sh \
    SOUJI_Q_LEDGER=$L/corpus/knowledge/obsidian-ledger.tsv \
    env SHELLOPTS=monitor "$tool" --dry-run "$L" "$L/PROVINCE.md" > "$S/out.$label" 2>&1 &
  front=$!
  sleep 1
  echo "--- $label front_alive_after_1s=$(ps -p "$front" -o pid= | wc -l) out_lines=$(wc -l < "$S/out.$label")"
  if ps -p "$front" >/dev/null 2>&1; then
    kill -TERM "$front" 2>/dev/null
  fi
  wait "$front"; echo "--- $label front_rc=$?"
  sed -n '1,4p' "$S/out.$label"
}
arm "$S/tools/cand.sh" nofix
arm "$S/tools/fixed.sh" setplusm
