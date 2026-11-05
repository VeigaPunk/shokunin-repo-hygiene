#!/bin/bash
set -u
L=/home/vgpnk/Projects/shokunin/souji-shokunin
S=/fast/scratch/hyaku/souji-r65/S65SentinelScope
P=$S/probe3
trap 'rm -rf -- "$P"' EXIT
rm -rf -- "$P"; mkdir -p "$P/w"
git -C "$L" show 40a371d8232e89e4f50d3ece4ff8779f44c0ee4c:tools/souji-receipt-write.py > "$P/writer.py"
: > "$P/empty.gitconfig"
BASEENV=(env -i PATH="$PATH" HOME="$P/home" GIT_CONFIG_GLOBAL="$P/empty.gitconfig" GIT_CONFIG_NOSYSTEM=1 GIT_OPTIONAL_LOCKS=0)
mkfix() { local d="$P/$1"; mkdir -p "$d/tools"; git -C "$d" init -q
  [ "$(git -C "$d" rev-parse --show-toplevel)" = "$d" ] || { echo "TOPLEVEL MISMATCH $d"; exit 3; }
  printf '#!/bin/sh\necho instrument-ok\n' > "$d/tools/instr.sh"; chmod 755 "$d/tools/instr.sh"; printf 'readme\n' > "$d/README.md"
  git -C "$d" add -A; git -C "$d" -c user.name=ProbeSentinel -c user.email=probe-sentinel@invalid -c commit.gpgsign=false commit -q -m seed
  git -C "$d" rev-parse HEAD > "$P/$1.rev"; }
run() { local name=$1; shift; local d="$P/$name" rev; rev=$(cat "$P/$name.rev"); local out="$P/w/$name.out"; rm -f -- "$out"
  "${BASEENV[@]}" "$@" python3 -B "$P/writer.py" --root "$d" --rev "$rev" --instrument tools/instr.sh --out "$out" --allow-outside --command "/bin/echo hi" >"$P/w/$name.so" 2>"$P/w/$name.se"
  local rc=$?; local v=error; if [ $rc -eq 0 ] && [ -f "$out" ]; then v=accept; elif [ $rc -eq 2 ] && [ ! -e "$out" ]; then v=refuse; fi
  printf '%-22s rc=%s verdict=%-7s stderr=%s\n' "$name" "$rc" "$v" "$(tr '\n' ' ' < "$P/w/$name.se" | cut -c1-120)"; }
# P6b: committed instrument X; refs/replace X->Y; worktree holds Y; --allow-dirty (caller-accepted dirty baseline)
mkfix p6b-replace-allowdirty; R=$P/p6b-replace-allowdirty
X=$(git -C "$R" rev-parse HEAD:tools/instr.sh); printf '#!/bin/sh\necho REPLACED\n' > "$P/y"; Y=$(git -C "$R" hash-object -w "$P/y")
git -C "$R" replace "$X" "$Y"; cp "$P/y" "$R/tools/instr.sh"
out="$P/w/p6b.out"; rm -f "$out"
"${BASEENV[@]}" python3 -B "$P/writer.py" --root "$R" --rev "$(cat "$P/p6b-replace-allowdirty.rev")" --instrument tools/instr.sh --out "$out" --allow-outside --allow-dirty --command "/bin/echo hi" >"$P/w/p6b.so" 2>"$P/w/p6b.se"; rc=$?
echo "P6b replace+allow-dirty rc=$rc out_exists=$([ -f "$out" ] && echo yes || echo no) stderr=$(tr '\n' ' ' < "$P/w/p6b.se" | cut -c1-120)"
[ -f "$out" ] && echo "P6b receipt instrument lines: $(grep -E '^(instrument_sha256|# instrument)' "$out" | head -3 | tr '\n' ' ')"
echo "P6b sha256(committed X)=$(git -C "$R" --no-replace-objects cat-file blob "$X" | sha256sum | cut -c1-16) sha256(replacement Y)=$(printf '#!/bin/sh\necho REPLACED\n' | sha256sum | cut -c1-16)"
# P7: repo-local .git/info/exclude hides an untracked file (not a config key; repo-local write)
mkfix p7-info-exclude; printf 'u\n' > "$P/p7-info-exclude/tools/hidden.txt"; printf 'hidden.txt\n' >> "$P/p7-info-exclude/.git/info/exclude"
run p7-info-exclude
echo "P7 plain status: [$(git -C "$P/p7-info-exclude" status --porcelain | tr '\n' ' ')]"
# P8: status.showUntrackedFiles overridden: confirm -c all beats repo config AND env, but env excludesFile still wins (control for P3 under --allow-dirty)
mkfix p8-env-excludes-allowdirty; printf 'u\n' > "$P/p8-env-excludes-allowdirty/tools/hidden.txt"; printf 'hidden.txt\n' > "$P/p8.excl"
run p8-env-excludes-allowdirty GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0="$P/p8.excl"
