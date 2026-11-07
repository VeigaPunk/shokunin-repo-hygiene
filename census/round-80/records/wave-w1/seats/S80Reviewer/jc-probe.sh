#!/bin/bash
# S80Reviewer: independent minimal signal checks of tools/souji-quarantine.sh (not via the r80 C2 counter).
# The tool is extracted from the frozen W2 blob (836dac3e), so the probe measures the landed bytes.
# A: TERM at the receipt-engine hang, plain bash -> expect rc=143, SIGNAL line, 0 survivors.
# B: `bash -m` with no tty: bash reports "no job control", setsid execs in place; `timeout 8` TERMs the front
#    at the bound -> expect the SIGNAL path, 0 survivors.
# C: the caller exports SOUJI_Q_SESSION=<its own sid> -> the tool takes the inline nested branch (landed block
#    line 216): expect TERM to kill the shell, no SIGNAL line, children left running (reproducer, not a control).
set -u
S=/fast/scratch/hyaku/souji-r80/S80Reviewer
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p "$S/tools/cand"
[ -f "$S/tools/cand/souji-quarantine.sh" ] || git -C "$LANE" show 836dac3e336863c57d9d7125837ed22b22d8d044:tools/souji-quarantine.sh > "$S/tools/cand/souji-quarantine.sh"
chmod 0755 "$S/tools/cand/souji-quarantine.sh"
TOOL=$S/tools/cand/souji-quarantine.sh
[ "$(sha256sum < "$TOOL" | cut -d' ' -f1)" = 67ec160b97b4fea7e93fdf74afcf1bd904171cf25062fef1a602fe28de3a7181 ] || { echo "tool blob is not 67ec160b"; exit 1; }
D=$(mktemp -d -p "$S" fx.XXXXXX) || { echo "mktemp failed"; exit 1; }
[ -n "$D" ] && [ -d "$D" ] || { echo "bad D"; exit 1; }
cleanup() { local p; for p in /proc/[0-9]*; do p=${p#/proc/}; grep -qa "SOUJI_R80_JC=$D" "/proc/$p/environ" 2>/dev/null && kill -9 "$p" 2>/dev/null; done; rm -rf -- "$D"; }
trap cleanup EXIT
mkdir -p "$D/fleet/repo/.scratch" "$D/tmp"
git -C "$D/fleet/repo" init -q || exit 1
[ "$(git -C "$D/fleet/repo" rev-parse --show-toplevel)" = "$D/fleet/repo" ] || exit 1
printf 'payload\n' > "$D/fleet/repo/.scratch/aged.dat"
touch -d '3 days ago' "$D/fleet/repo/.scratch/aged.dat" "$D/fleet/repo/.scratch"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$D/ledger.tsv"
printf '#!/bin/bash\nprintf "%%s\\n" "$@" > "%s"\nexec sleep 600\n' "$D/engine.mark" > "$D/engine-hang.sh"
chmod 0755 "$D/engine-hang.sh"
common=(env "SOUJI_VERIFY_BIN=$D/engine-hang.sh" "SOUJI_Q_SHOKUNIN_ROOT=$D/fleet" "SOUJI_Q_LEDGER=$D/ledger.tsv"
        "TMPDIR=$D/tmp" "SOUJI_R80_JC=$D" "LC_ALL=C")
survivors() { local n=0 p; for p in /proc/[0-9]*; do p=${p#/proc/}; grep -qa "SOUJI_R80_JC=$D" "/proc/$p/environ" 2>/dev/null && n=$((n+1)); done; echo "$n"; }
tg="$D/fleet/repo/.scratch/aged.dat"
echo "== A: TERM at the engine hang, plain bash =="
"${common[@]}" bash "$TOOL" --dry-run "$D/fleet/repo" "$tg" > "$D/a.out" 2>&1 &
apid=$!
for i in $(seq 1 200); do [ -f "$D/engine.mark" ] && break; sleep 0.05; done
[ -f "$D/engine.mark" ] && echo "A mark=yes" || echo "A mark=no"
kill -TERM "$apid" 2>/dev/null
wait "$apid"; arc=$?
printf 'A rc=%s signal_line=%s survivors=%s\n' "$arc" "$(grep -c $'^SIGNAL\t' "$D/a.out")" "$(survivors)"
echo "== B: bash -m (no tty) with an outer timeout 8 =="
rm -f "$D/engine.mark"
t0=$(date +%s%N)
"${common[@]}" timeout 8 bash -m "$TOOL" --dry-run "$D/fleet/repo" "$tg" > "$D/b.out" 2>&1
brc=$?
t1=$(date +%s%N)
printf 'B rc=%s elapsed_ms=%s signal_line=%s survivors=%s stderr_jobctl=%s\n' "$brc" "$(( (t1 - t0) / 1000000 ))" \
  "$(grep -c $'^SIGNAL\t' "$D/b.out")" "$(survivors)" "$(grep -c 'no job control' "$D/b.out")"
echo "== C: caller exports SOUJI_Q_SESSION=<its own sid> (landed line 216 inline branch) =="
rm -f "$D/engine.mark"
mysid=$(ps -o sid= -p $$ | tr -d ' ')
"${common[@]}" SOUJI_Q_SESSION="$mysid" bash "$TOOL" --dry-run "$D/fleet/repo" "$tg" > "$D/c.out" 2>&1 &
cpid=$!
for i in $(seq 1 200); do [ -f "$D/engine.mark" ] && break; sleep 0.05; done
[ -f "$D/engine.mark" ] && echo "C mark=yes" || echo "C mark=no"
kill -TERM "$cpid" 2>/dev/null
wait "$cpid"; crc=$?
sleep 1
printf 'C rc=%s tool_alive_after_term=%s signal_line=%s survivors=%s\n' "$crc" \
  "$(kill -0 "$cpid" 2>/dev/null && echo y || echo n)" "$(grep -c $'^SIGNAL\t' "$D/c.out")" "$(survivors)"
