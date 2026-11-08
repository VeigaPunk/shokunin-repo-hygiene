#!/usr/bin/env bash
# S84Sentinel C2 reproducer: a CLI whose /proc/<pid>/stat comm holds a NEWLINE and ')' is never frozen by the
# candidate tool, so its TERM trap fires and the setsid'd child it forks survives the abort path.
#
# The frozen 22-row C2 population cannot see this: none of its 22 stubs has a newline in its comm.
#
# Usage: repro_c2_newline_comm.sh <candidate-tool.sh>
set -u
TOOL=${1:?usage: repro_c2_newline_comm.sh <candidate-tool.sh>}
TOOL=$(readlink -m -- "$TOOL")
W=$(mktemp -d /fast/scratch/hyaku/souji-r84/S84Sentinel/repro-newline.XXXXXX)
trap 'rm -rf -- "$W"' EXIT
mkdir -p "$W/src" "$W/vault" "$W/fleet" "$W/tmp"
printf 'r84 sentinel newline-comm repro\n' > "$W/src/a-src.md"
cp "$W/src/a-src.md" "$W/vault/a-vlt.md"
H=$(sha256sum -- "$W/src/a-src.md" | cut -d' ' -f1)
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$W/ledger.tsv"
printf '%s\t%s\t%s\t%s\t2026-11-08\tr84-sentinel\n' "$W/src/a-src.md" "$H" "$W/vault/a-vlt.md" "$H" >> "$W/ledger.tsv"

# the CLI: its OWN comm holds a newline and ')'; on the first TERM it forks a setsid'd child and keeps running.
cat > "$W/cli" <<'PYEOF'
#!/usr/bin/env python3
import ctypes, os, signal, sys, time
libc = ctypes.CDLL("libc.so.6", use_errno=True)
libc.prctl(15, b"a\nb)c", 0, 0, 0)          # comm = "a\nb)c": a NEWLINE and a ')'
def term(*a):
    pid = os.fork()
    if pid == 0:
        os.setsid()                          # leave the tool's process group
        while True:
            time.sleep(0.3)
    os._exit(0)
signal.signal(signal.SIGTERM, term)
signal.signal(signal.SIGINT, term)
signal.signal(signal.SIGHUP, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s\n" % os.getpid())
while True:
    time.sleep(0.2)
PYEOF
chmod +x "$W/cli"

NONCE=r84sentinel$$
export S84_MARK="$W/mark" S84_NONCE="$NONCE"
env -i PATH="$PATH" HOME="$HOME" LC_ALL=C \
    TMPDIR="$W/tmp" S84_MARK="$W/mark" S84_NONCE="$NONCE" \
    SOUJI_LEDGER="$W/ledger.tsv" SOUJI_CLI_BIN="$W/cli" SOUJI_CLI_TIMEOUT=300 \
    SHOKUNIN_ROOT="$W/fleet" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null \
    setsid bash "$TOOL" "$W/src/a-src.md" > "$W/out" 2> "$W/err" &
TOOL_PID=$!
for _ in $(seq 1 100); do [ -f "$W/mark" ] && break; sleep 0.1; done
CLI_PID=$(sed -n 's/.*pid=\([0-9]*\).*/\1/p' "$W/mark")
echo "# tool        : $TOOL"
echo "# cli pid     : $CLI_PID"
echo "# cli comm    : $(tr '\n' '?' < /proc/$CLI_PID/comm 2>/dev/null)"
kill -TERM "$TOOL_PID" 2>/dev/null
for _ in $(seq 1 60); do kill -0 "$TOOL_PID" 2>/dev/null || break; sleep 0.1; done
SURV=0
for p in /proc/[0-9]*; do
    [ -r "$p/environ" ] || continue
    if tr '\0' '\n' < "$p/environ" 2>/dev/null | grep -qx "S84_NONCE=$NONCE"; then
        st=$(awk '{print $3}' "$p/stat" 2>/dev/null)
        [ "$st" = "Z" ] && continue
        echo "# SURVIVOR pid=${p#/proc/} state=$st comm=$(tr '\n' '?' < "$p/comm" 2>/dev/null)"
        SURV=$((SURV+1))
    fi
done
grep -q 'souji-vault-verify: SIGTERM' "$W/err" && echo "# tool printed the SIGTERM line" || echo "# tool printed NO SIGTERM line"
echo "# survivors   : $SURV"
[ "$SURV" -gt 0 ] && echo "RESULT: LEAK (a setsid'd child of the CLI survived the abort path)" \
                  || echo "RESULT: no leak"
exit 0
