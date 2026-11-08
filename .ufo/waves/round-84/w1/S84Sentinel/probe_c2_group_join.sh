#!/usr/bin/env bash
# S84Sentinel C2 group-join probe: the tool's abort path ends with a PROCESS-GROUP kill
# (`kill -TERM -- -$CLI_PID` / `kill -KILL -- -$CLI_PID`). This probe asks the seat's CRITICAL question directly:
# can a pid OUTSIDE the CLI's descendant set receive a signal from that kill?
#
# The canary is a pre-existing process in the SAME SESSION as the tool; the (untrusted) CLI publishes its own
# process-group id, and the canary joins that group with setpgid(). The canary logs every signal it receives.
# A canary hit is a signal to a non-descendant.
#
# Only processes this script creates are ever signalled. Writes only under --work.
#
# Usage: probe_c2_group_join.sh <candidate-tool.sh> [work-dir]
set -u
TOOL=$(readlink -m -- "${1:?usage: probe_c2_group_join.sh <tool.sh> [work-dir]}")
WORK=${2:-$(mktemp -d /fast/scratch/hyaku/souji-r84/S84Sentinel/gj.XXXXXX)}
mkdir -p "$WORK"
D="$WORK/gj"
rm -rf "$D"; mkdir -p "$D"/{src,vault,fleet,tmp}
printf 'r84 sentinel group-join payload\n' > "$D/src/a-src.md"
cp "$D/src/a-src.md" "$D/vault/a-vlt.md"
H=$(sha256sum -- "$D/src/a-src.md" | cut -d' ' -f1)
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$D/ledger.tsv"
printf '%s\t%s\t%s\t%s\t2026-11-08\tr84-sentinel\n' "$D/src/a-src.md" "$H" "$D/vault/a-vlt.md" "$H" >> "$D/ledger.tsv"

# the CLI: publishes its pgid, then hangs (the tool's abort path then runs)
cat > "$D/cli" <<'PYEOF'
#!/usr/bin/env python3
import os, signal, time
def term(*a):
    os._exit(0)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s pgid=%s\n" % (os.getpid(), os.getpgrp()))
while True:
    time.sleep(0.2)
PYEOF
chmod +x "$D/cli"

# the canary: waits for the CLI's pgid, joins that group, then logs every signal it receives
cat > "$D/canary" <<'PYEOF'
#!/usr/bin/env python3
import os, signal, time
log = os.environ["S84_CANARY_LOG"]
def note(s):
    with open(log, "a") as f:
        f.write(s + "\n")
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT):
    try:
        signal.signal(s, lambda n, f: note("sig%d" % n))
    except (OSError, ValueError):
        pass
note("start")
deadline = time.time() + 25
joined = False
while time.time() < deadline:
    try:
        with open(os.environ["S84_CLI_PGID"], encoding="utf-8") as f:
            pgid = int(f.read().strip())
        os.setpgid(0, pgid)
        note("joined-pgid-%d" % pgid)
        joined = True
        break
    except (OSError, ValueError):
        time.sleep(0.05)
note("joined" if joined else "not-joined")
open(os.environ["S84_CANARY_READY"], "w").write("ready\n")
while True:
    time.sleep(0.1)
PYEOF
chmod +x "$D/canary"

cat > "$D/run.sh" <<EOF
#!/bin/bash
cd "$D"
export S84_MARK="$D/cli.mark" S84_CLI_PGID="$D/cli.pgid" S84_CANARY_LOG="$D/canary.log" \\
       S84_CANARY_READY="$D/canary.ready" TMPDIR="$D/tmp" SOUJI_LEDGER="$D/ledger.tsv" \\
       SOUJI_CLI_BIN="$D/cli" SOUJI_CLI_TIMEOUT=300 SHOKUNIN_ROOT="$D/fleet" \\
       GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
"$D/canary" &
exec bash "$TOOL" "$D/src/a-src.md"
EOF
chmod +x "$D/run.sh"

# ONE session for both the tool and the canary, so the canary may join the CLI's group.
setsid bash "$D/run.sh" > "$D/out" 2> "$D/err" &
RUN=$!
for _ in $(seq 1 200); do [ -f "$D/cli.mark" ] && break; sleep 0.1; done
CLI_PGID=""
if [ -f "$D/cli.mark" ]; then
    CLI_PGID=$(sed -n 's/.*pgid=\([0-9]*\).*/\1/p' "$D/cli.mark")
    [ -n "$CLI_PGID" ] && printf '%s\n' "$CLI_PGID" > "$D/cli.pgid"
fi
for _ in $(seq 1 100); do grep -q '^joined' "$D/canary.log" 2>/dev/null && break; sleep 0.1; done
sleep 0.4
TOOL_PID=$(pgrep -f "^bash $TOOL " | head -1)
echo "# tool        : $TOOL"
echo "# cli pgid    : ${CLI_PGID:-<none>}"
echo "# tool pid    : ${TOOL_PID:-<none>}"
grep -q '^joined' "$D/canary.log" 2>/dev/null && echo "# canary joined the CLI's process group" || echo "# canary did NOT join"
[ -n "$TOOL_PID" ] && kill -TERM "$TOOL_PID" 2>/dev/null
for _ in $(seq 1 60); do [ -n "$TOOL_PID" ] && kill -0 "$TOOL_PID" 2>/dev/null || break; sleep 0.1; done
sleep 0.3
echo "# canary log  : $(tr '\n' ' ' < "$D/canary.log" 2>/dev/null)"
HITS=$(grep -c '^sig' "$D/canary.log" 2>/dev/null || echo 0)
echo "# canary signals received: $HITS"
if [ "$HITS" -gt 0 ]; then echo "RESULT: SIGNAL TO A NON-DESCENDANT (CRITICAL)"; else echo "RESULT: no signal outside the descendant set"; fi
pkill -f "$D/canary" 2>/dev/null
pkill -f "$D/cli" 2>/dev/null
exit 0
