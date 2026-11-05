#!/bin/bash
L=/home/vgpnk/Projects/shokunin/souji-shokunin; D=$L/.ufo/waves/round-65/w1/S65SentinelScope; S=/fast/scratch/hyaku/souji-r65/S65SentinelScope
Q=$S/secprobe; rm -rf -- "$Q"; mkdir -p "$Q/w" "$Q/repo/tools" "$Q/h"
trap 'rm -rf -- "$Q"' EXIT
git -C "$Q/repo" init -q
[ "$(git -C "$Q/repo" rev-parse --show-toplevel)" = "$Q/repo" ] || { echo TOP-MISMATCH; exit 3; }
printf '#!/bin/sh\necho ok\n' > "$Q/repo/tools/instr.sh"; chmod 755 "$Q/repo/tools/instr.sh"
git -C "$Q/repo" add -A
git -C "$Q/repo" -c user.name=SecProbe -c user.email=secprobe@invalid -c commit.gpgsign=false commit -q -m s || { echo COMMIT-FAIL; exit 4; }
REV=$(git -C "$Q/repo" rev-parse HEAD)
git -C "$L" show 40a371d8232e89e4f50d3ece4ff8779f44c0ee4c:tools/souji-receipt-write.py > "$Q/writer.py"
PAD=$(printf 'a%.0s' $(seq 1 300))
LONG="$Q/keys/id_rsa_secret_credential_${PAD}.idx"
env -i PATH="$PATH" HOME="$Q/h" GIT_INDEX_FILE="$LONG" python3 -B "$Q/writer.py" --root "$Q/repo" --rev "$REV" --instrument tools/instr.sh --out "$Q/w/o.txt" --allow-outside --command "/bin/echo hi" 2> "$Q/se.txt"; echo "envset rc=$?"
echo "writer stderr bytes=$(wc -c < "$Q/se.txt")"
echo "writer stderr head: $(head -c 150 "$Q/se.txt")"
env -i PATH="$PATH" HOME="$Q/h" python3 -B "$Q/writer.py" --root "$Q/repo" --rev "$REV" --instrument tools/instr.sh --out "$Q/w/o2.txt" --allow-outside --command 'echo "SECRET-ARGV-TOKEN-xyz' 2> "$Q/se2.txt"; echo "parse rc=$?"; echo "parse stderr: $(cat "$Q/se2.txt")"
