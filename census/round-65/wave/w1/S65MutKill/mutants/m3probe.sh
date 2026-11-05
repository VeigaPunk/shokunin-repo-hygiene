#!/bin/bash
# S65MutKill m3 follow-up: same-content symlink retarget inside an untracked dir (outside the frozen matrix).
set -u
S=/fast/scratch/hyaku/souji-r65/S65MutKill
W=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-65/w1/S65MutKill
RETARGET='import os,sys; os.unlink(sys.argv[1]); os.symlink(sys.argv[2], sys.argv[1])'
fix() {
  local r=$S/m3p/$1; rm -rf -- "$r"; mkdir -p "$r/tools/extra"; cd "$r" || exit 2
  git init -q
  [ "$(git rev-parse --show-toplevel)" = "$r" ] || { echo "TOPLEVEL MISMATCH"; exit 2; }
  git config user.name S65 && git config user.email s65@invalid
  printf '#!/bin/sh\necho ok\n' > tools/instr.sh; chmod 755 tools/instr.sh
  printf 'v1\n' > tools/notes.txt; git add -A && git commit -qm seed; REV=$(git rev-parse HEAD)
  printf 'v1\ndirty\n' > tools/notes.txt
  printf 'v1\ndirty\n' > tools/copy.txt          # untracked, byte-identical to notes.txt
  printf 'k\n' > tools/extra/keep.txt
  ln -s ../notes.txt tools/extra/link
}
for tool in landed:"$S/writer-landed.py" m3:"$S/m3-symlink-followed.py"; do
  name=${tool%%:*}; path=${tool#*:}
  fix "$name"
  python3 -B "$path" --root "$PWD" --rev "$REV" --instrument tools/instr.sh --out "$PWD/out-$name.txt" --allow-dirty -- \
     python3 -c "$RETARGET" tools/extra/link ../copy.txt > "$W/m3probe-$name.out" 2>&1
  echo "rc=$? out_exists=$([ -e out-$name.txt ] && echo yes || echo no) link_now=$(readlink tools/extra/link)" >> "$W/m3probe-$name.out"
  cat "$W/m3probe-$name.out"
done
