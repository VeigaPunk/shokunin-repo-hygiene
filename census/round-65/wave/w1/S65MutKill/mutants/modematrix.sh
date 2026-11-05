#!/bin/bash
# S65MutKill mode-polarity driver: landed writer, --allow-dirty, in-run chmod/chown of a dirty tracked file.
set -u
S=/fast/scratch/hyaku/souji-r65/S65MutKill
W=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-65/w1/S65MutKill
WR=$S/writer-landed.py
CHM='import os,sys; os.chmod(sys.argv[1], int(sys.argv[2],8))'
mkfix() { # $1 name, $2 start mode for notes.txt, $3 extra untracked file flag
  local r=$S/mm/$1
  rm -rf -- "$r"; mkdir -p "$r/tools"; cd "$r" || exit 2
  git init -q
  [ "$(git rev-parse --show-toplevel)" = "$r" ] || { echo "TOPLEVEL MISMATCH $r"; exit 2; }
  git config user.name S65 && git config user.email s65@invalid
  printf '#!/bin/sh\necho ok\n' > tools/instr.sh; chmod 755 tools/instr.sh
  printf 'v1\n' > tools/notes.txt; printf 'clean\n' > tools/clean.txt
  chmod 644 tools/notes.txt tools/clean.txt
  git add -A && git commit -qm seed
  REV=$(git rev-parse HEAD)
  printf 'dirty\n' >> tools/notes.txt; chmod "$2" tools/notes.txt
  MODE_START=$(stat -c %a tools/notes.txt)
}
runw() { # $1 label; rest = writer argv (after --)
  local label=$1; shift
  local out=$W/mode-$label.out
  python3 -B "$WR" --root "$PWD" --rev "$REV" --instrument tools/instr.sh --out "$PWD/out-$label.txt" --allow-dirty -- "$@" > "$out.stdout" 2> "$out.stderr"
  local rc=$?
  { echo "label=$label start_mode=$MODE_START rc=$rc out_exists=$([ -e out-$label.txt ] && echo yes || echo no)"; echo "--- stderr:"; cat "$out.stderr"; echo "--- stdout:"; cat "$out.stdout"; echo "--- final notes mode: $(stat -c %a tools/notes.txt)"; } > "$out"
  cat "$out"
  rm -f "$out.stdout" "$out.stderr"
}
mkdir -p "$S/mm" "$W"
for target in 600 444 755 4755; do
  mkfix "t$target-from644" 644
  runw "t$target-from644" python3 -c "$CHM" tools/notes.txt "$target"
done
# setuid-only arm: start 755, flip to 4755 (low 9 bits unchanged)
mkfix setuid-from755 755
runw setuid-from755-to4755 python3 -c "$CHM" tools/notes.txt 4755
# setuid-only arm on 644 base
mkfix setuid-from644 644
runw setuid-from644-to4644 python3 -c "$CHM" tools/notes.txt 4644
# in-run chown of dirty tracked file (non-root, no sudo): record
mkfix chown-dirty 644
runw chown-dirty-to-root python3 -c 'import os,sys; os.chown(sys.argv[1], 0, 0)' tools/notes.txt
# boundary: clean tracked file, not snapshotted, chmod in-run (no --allow-dirty and --allow-dirty variants)
mkfix clean-chmod-600 644
r=$PWD
python3 -B "$WR" --root "$r" --rev "$REV" --instrument tools/instr.sh --out "$r/out-clean600-noallow.txt" -- python3 -c "$CHM" tools/clean.txt 600 > "$W/mode-boundary-clean600-noallow.out" 2>&1; echo "boundary-clean600-noallow rc=$?" >> "$W/mode-boundary-clean600-noallow.out"
mkfix clean-chmod-755 644
r=$PWD
python3 -B "$WR" --root "$r" --rev "$REV" --instrument tools/instr.sh --out "$r/out-clean755-noallow.txt" -- python3 -c "$CHM" tools/clean.txt 755 > "$W/mode-boundary-clean755-noallow.out" 2>&1; echo "boundary-clean755-noallow rc=$?" >> "$W/mode-boundary-clean755-noallow.out"
mkfix clean-chmod-600-allow 644
r=$PWD
python3 -B "$WR" --root "$r" --rev "$REV" --instrument tools/instr.sh --out "$r/out-clean600-allow.txt" --allow-dirty -- python3 -c "$CHM" tools/clean.txt 600 > "$W/mode-boundary-clean600-allowdirty.out" 2>&1; echo "boundary-clean600-allowdirty rc=$?" >> "$W/mode-boundary-clean600-allowdirty.out"
mkfix clean-chmod-755-allow 644
r=$PWD
python3 -B "$WR" --root "$r" --rev "$REV" --instrument tools/instr.sh --out "$r/out-clean755-allow.txt" --allow-dirty -- python3 -c "$CHM" tools/clean.txt 755 > "$W/mode-boundary-clean755-allowdirty.out" 2>&1; echo "boundary-clean755-allowdirty rc=$?" >> "$W/mode-boundary-clean755-allowdirty.out"
echo "id -u=$(id -u)"
