#!/usr/bin/env bash
# r71 pre-freeze probe: which attribute / core.fileMode routes hide a change from `git status`
# and from the base writer (tools/souji-receipt-write.py at the lane base). Scratch-only.
# Forged bytes are SIZE-PRESERVING ('counter v2' vs committed 'counter v1'): a size change is seen
# by the stat check before any clean filter runs (first run of this probe; see census/round-71/preregistration.txt).
# Usage: attr-filemode-probe.sh <writer.py> <scratch-dir>
set -u
W=$1; S=$2
mkdir -p "$S"; S=$(cd "$S" && pwd)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_DATE=2026-11-06T12:00:00Z GIT_COMMITTER_DATE=2026-11-06T12:00:00Z
unset GIT_DIR GIT_WORK_TREE GIT_ATTR_SOURCE
mk() {  # mk <name> -> fresh repo with tools/counter.py, tools/notes.txt, tools/instr.sh
  local D="$S/$1"; rm -rf "$D"; mkdir -p "$D/tools"
  git -C "$D" init -q
  [ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "toplevel mismatch $D"; exit 9; }
  git -C "$D" config user.name probe; git -C "$D" config user.email probe@invalid
  printf 'counter v1\n' > "$D/tools/counter.py"; printf 'notes v1\n' > "$D/tools/notes.txt"
  printf '#!/bin/sh\necho ok\n' > "$D/tools/instr.sh"; chmod 755 "$D/tools/instr.sh"
  git -C "$D" add -A; git -C "$D" commit -qm seed
  echo "$D"
}
runw() {  # runw <repo> [env...] -- argv : run the writer, print rc and refusal line
  local D=$1; shift; local envs=(); while [ "$1" != "--" ]; do envs+=("$1"); shift; done; shift
  local rev; rev=$(git -C "$D" rev-parse HEAD); rm -rf "$D.out"; mkdir -p "$D/out"
  env "${envs[@]}" python3 -B "$W" --root "$D" --rev "$rev" --instrument tools/instr.sh \
     --out "$D/out/r.txt" -- "$@" >"$D.wout" 2>"$D.werr"; local rc=$?
  echo "  writer rc=$rc receipt=$([ -f "$D/out/r.txt" ] && echo written || echo none) err=$(head -c 160 "$D.werr" | tr '\n' ' ')"
  rm -rf "$D/out"
}
st() { echo "  status=[$(env "$@" git -C "$D" status --porcelain | tr '\n' ' ')]"; }

echo "## P1 GIT_ATTR_SOURCE=<commit: tools/counter.py text> + CRLF worktree bytes, no config"
D=$(mk p1)
blob=$(printf 'tools/counter.py text\n' | git -C "$D" hash-object -w --stdin)
tree=$(printf '100644 blob %s\t.gitattributes\n' "$blob" | git -C "$D" mktree)
asrc=$(git -C "$D" commit-tree -m attrs "$tree")
printf 'counter v1\r\n' > "$D/tools/counter.py"
st; st GIT_ATTR_SOURCE=$asrc
runw "$D" GIT_ATTR_SOURCE=$asrc -- /bin/echo hi

echo "## P2 GIT_ATTR_SOURCE=<commit: tools/counter.py filter=t> + local filter.t.clean, forged bytes"
D=$(mk p2)
git -C "$D" config filter.t.clean "sed s/v2/v1/"
blob=$(printf 'tools/counter.py filter=t\n' | git -C "$D" hash-object -w --stdin)
tree=$(printf '100644 blob %s\t.gitattributes\n' "$blob" | git -C "$D" mktree)
asrc=$(git -C "$D" commit-tree -m attrs "$tree")
printf 'counter v2\n' > "$D/tools/counter.py"
st; st GIT_ATTR_SOURCE=$asrc
runw "$D" GIT_ATTR_SOURCE=$asrc -- /bin/echo hi

echo "## P3 committed .gitattributes filter=t + local filter.t.clean, forged pre-run bytes"
D=$(mk p3)
printf 'tools/counter.py filter=t\n' > "$D/.gitattributes"; git -C "$D" add .gitattributes; git -C "$D" commit -qm attrs
git -C "$D" config filter.t.clean "sed s/v2/v1/"
printf 'counter v2\n' > "$D/tools/counter.py"
st
runw "$D" -- /bin/echo hi

echo "## P4 committed .gitattributes filter=t + local filter.t.clean, IN-RUN edit"
D=$(mk p4)
printf 'tools/counter.py filter=t\n' > "$D/.gitattributes"; git -C "$D" add .gitattributes; git -C "$D" commit -qm attrs
git -C "$D" config filter.t.clean "sed s/v2/v1/"
st
runw "$D" -- python3 -c "open('$D/tools/counter.py','w').write('counter v2\n')"

echo "## P5 committed .gitattributes filter=t, NO driver configured, clean tree (honest)"
D=$(mk p5)
printf 'tools/counter.py filter=t\n' > "$D/.gitattributes"; git -C "$D" add .gitattributes; git -C "$D" commit -qm attrs
st
runw "$D" -- /bin/echo hi

echo "## P6 local core.fileMode=false, pre-run chmod 755 tools/notes.txt"
D=$(mk p6); git -C "$D" config core.fileMode false; chmod 755 "$D/tools/notes.txt"
st; st GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fileMode GIT_CONFIG_VALUE_0=true
runw "$D" -- /bin/echo hi

echo "## P7 local core.fileMode=false, IN-RUN chmod 755 tools/notes.txt"
D=$(mk p7); git -C "$D" config core.fileMode false
runw "$D" -- python3 -c "import os; os.chmod('$D/tools/notes.txt', 0o755)"

echo "## P8 local core.fileMode=false, clean (honest)"
D=$(mk p8); git -C "$D" config core.fileMode false
runw "$D" -- /bin/echo hi

echo "## P9 local filter.t.process only (no clean), committed attr, forged"
D=$(mk p9)
printf 'tools/counter.py filter=t\n' > "$D/.gitattributes"; git -C "$D" add .gitattributes; git -C "$D" commit -qm attrs
git -C "$D" config filter.t.process "false"; git -C "$D" config filter.t.required false
printf 'counter v2\n' > "$D/tools/counter.py"
st
runw "$D" -- /bin/echo hi
echo "## git $(git --version)"

echo "## P10 GIT_ATTR_SOURCE=<commit: tools/counter.py filter=t> + local clean, IN-RUN edit"
D=$(mk p10)
git -C "$D" config filter.t.clean "sed s/v2/v1/"
blob=$(printf 'tools/counter.py filter=t\n' | git -C "$D" hash-object -w --stdin)
tree=$(printf '100644 blob %s\t.gitattributes\n' "$blob" | git -C "$D" mktree)
asrc=$(git -C "$D" commit-tree -m attrs "$tree")
runw "$D" GIT_ATTR_SOURCE=$asrc -- python3 -c "open('$D/tools/counter.py','w').write('counter v2\n')"
echo "## P11 filter driver configured, attribute names a non-existent path only (honest)"
D=$(mk p11)
printf 'nosuch.bin filter=t\n' > "$D/.gitattributes"; git -C "$D" add .gitattributes; git -C "$D" commit -qm attrs
git -C "$D" config filter.t.clean "sed s/v2/v1/"
st
runw "$D" -- /bin/echo hi
