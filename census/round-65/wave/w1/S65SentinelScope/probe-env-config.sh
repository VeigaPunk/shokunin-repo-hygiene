#!/bin/bash
set -u
L=/home/vgpnk/Projects/shokunin/souji-shokunin
S=/fast/scratch/hyaku/souji-r65/S65SentinelScope
P=$S/probe2
trap 'rm -rf -- "$P"' EXIT
rm -rf -- "$P"; mkdir -p "$P/w"
git -C "$L" show 40a371d8232e89e4f50d3ece4ff8779f44c0ee4c:tools/souji-receipt-write.py > "$P/writer.py"
: > "$P/empty.gitconfig"
BASEENV=(env -i PATH="$PATH" HOME="$P/home" GIT_CONFIG_GLOBAL="$P/empty.gitconfig" GIT_CONFIG_NOSYSTEM=1 GIT_OPTIONAL_LOCKS=0)
mkfix() {
  local d="$P/$1"; mkdir -p "$d/tools"
  git -C "$d" init -q
  [ "$(git -C "$d" rev-parse --show-toplevel)" = "$d" ] || { echo "TOPLEVEL MISMATCH $d"; exit 3; }
  printf '#!/bin/sh\necho instrument-ok\n' > "$d/tools/instr.sh"; chmod 755 "$d/tools/instr.sh"
  printf 'readme\n' > "$d/README.md"
  git -C "$d" add -A
  git -C "$d" -c user.name=ProbeSentinel -c user.email=probe-sentinel@invalid -c commit.gpgsign=false commit -q -m seed
  git -C "$d" rev-parse HEAD > "$P/$1.rev"
}
# run NAME [ENV=VAL ...] : writer invoked under env -i with the given assignments
run() {
  local name=$1; shift; local d="$P/$name" rev; rev=$(cat "$P/$name.rev")
  local out="$P/w/$name.out"; rm -f -- "$out"
  "${BASEENV[@]}" "$@" python3 -B "$P/writer.py" --root "$d" --rev "$rev" --instrument tools/instr.sh --out "$out" --allow-outside --command "/bin/echo hi" >"$P/w/$name.so" 2>"$P/w/$name.se"
  local rc=$?
  local v=error; if [ $rc -eq 0 ] && [ -f "$out" ]; then v=accept; elif [ $rc -eq 2 ] && [ ! -e "$out" ]; then v=refuse; fi
  printf '%-22s rc=%s verdict=%-7s stderr=%s\n' "$name" "$rc" "$v" "$(tr '\n' ' ' < "$P/w/$name.se" | cut -c1-120)"
}
# liveness: does the injection change a plain git status (no writer -c override)?
live() { # live NAME [ENV=VAL...]
  local name=$1; shift; local d="$P/$name"
  printf '%-22s plain-status-under-injection=[%s]\n' "$name" "$("${BASEENV[@]}" "$@" git -C "$d" status --porcelain | tr '\n' ' ')"
}
mkfix ctl-clean;               run ctl-clean
mkfix ctl-untracked;           printf 'u\n' > "$P/ctl-untracked/tools/extra.txt"; run ctl-untracked
mkfix ctl-repo-cfg;            printf 'u\n' > "$P/ctl-repo-cfg/tools/extra.txt"; git -C "$P/ctl-repo-cfg" config status.showUntrackedFiles no; run ctl-repo-cfg
mkfix p1-count-showuntracked;  printf 'u\n' > "$P/p1-count-showuntracked/tools/extra.txt"
E1=(GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=status.showUntrackedFiles GIT_CONFIG_VALUE_0=no)
live p1-count-showuntracked "${E1[@]}"; run p1-count-showuntracked "${E1[@]}"
mkfix p2-params-showuntracked; printf 'u\n' > "$P/p2-params-showuntracked/tools/extra.txt"
E2=("GIT_CONFIG_PARAMETERS='status.showUntrackedFiles'='no'")
live p2-params-showuntracked "${E2[@]}"; run p2-params-showuntracked "${E2[@]}"
mkfix p3-excludesfile-clean;   printf 'hidden.txt\n' > "$P/p3.excludes"
printf 'u\n' > "$P/p3-excludesfile-clean/tools/hidden.txt"
E3=(GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0="$P/p3.excludes")
live p3-excludesfile-clean "${E3[@]}"; run p3-excludesfile-clean "${E3[@]}"
mkfix p3c-noinjection;         printf 'u\n' > "$P/p3c-noinjection/tools/hidden.txt"
run p3c-noinjection
mkfix p4-fsmonitor;            printf 'u\n' > "$P/p4-fsmonitor/tools/extra.txt"
E4=(GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=true)
run p4-fsmonitor "${E4[@]}"
mkfix p6-replace
R=$P/p6-replace
blob=$(git -C "$R" rev-parse "HEAD:tools/instr.sh")
printf '#!/bin/sh\necho REPLACED\n' > "$P/p6.replacement"
rblob=$(git -C "$R" hash-object -w "$P/p6.replacement")
git -C "$R" replace "$blob" "$rblob"
cp "$P/p6.replacement" "$R/tools/instr.sh"
run p6-replace
echo "P6 cat-file (replace honoured): $(git -C "$R" cat-file blob "HEAD:tools/instr.sh" | tr '\n' ' ')"
echo "P6 cat-file --no-replace-objects: $(git -C "$R" --no-replace-objects cat-file blob "HEAD:tools/instr.sh" | tr '\n' ' ')"
echo "P6 worktree instrument: $(tr '\n' ' ' < "$R/tools/instr.sh")"
