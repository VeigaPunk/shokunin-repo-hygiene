#!/usr/bin/env bash
# S79ExecEvade probe sweep: fixed signal-timing cases, escapees, env cases,
# payload cases, random-offset hammer. Writes one JSON line per case to
# $S/probes.jsonl. Run from anywhere; all state under the seat scratch.
set -u
SEAT="/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-79/w1/S79ExecEvade"
S="/fast/scratch/hyaku/souji-r79/S79ExecEvade"
D="$S/D/souji-pre-report-gate.sh"
ROSTER="$S/probes.jsonl"
export SHIM_LOG=/dev/null
run() { python3 "$SEAT/probes/run_one.py" "$S/cases/$1" "$2" "$3" "$4" "$5" >>"$ROSTER" 2>>"$S/cases/err.log"; }
SHIMS="$SEAT/probes/shims"

# --- 1. smoke: no shims, no signal, default env
run smoke "" "$D" - "$S/fx"

# --- 2. slow-git children: TERM/INT/HUP during a child; doubles; TERM-then-INT
export SHIM_PRE_SLEEP=0.8
run term-child  "TERM@1.2"       "$D" "$SEAT/probes/shims" "$S/fx"
run int-child   "INT@1.2"        "$D" "$SEAT/probes/shims" "$S/fx"
run hup-child   "HUP@1.2"        "$D" "$SEAT/probes/shims" "$S/fx"
run term-term   "TERM@1.2,TERM@1.22"  "$D" "$SEAT/probes/shims" "$S/fx"
run term-int    "TERM@1.2,INT@1.24"   "$D" "$SEAT/probes/shims" "$S/fx"
run term-early  "TERM@0.005"     "$D" "$SEAT/probes/shims" "$S/fx"
run term-early2 "TERM@0.05"      "$D" "$SEAT/probes/shims" "$S/fx"

# --- 3. signal during a short $(...) fork (stated limit: deferred, then acted on)
export SHIM_REALPATH_SLEEP=1.5
export SHIM_AWK_SLEEP=1.0
export SHIM_PRE_SLEEP=0.3
run term-realpath "TERM@0.6"     "$D" "$SEAT/probes/shims" "$S/fx"
run term-awk      "TERM@1.4"     "$D" "$SEAT/probes/shims" "$S/fx"
unset SHIM_REALPATH_SLEEP SHIM_AWK_SLEEP

# --- 4. escaping children
export SHIM_PRE_SLEEP=0.8
export SHIM_ESCAPE=setsid;     run esc-setsid     "TERM@1.2" "$D" "$SEAT/probes/shims" "$S/fx"
export SHIM_ESCAPE=dfork;      run esc-dfork      "TERM@1.2" "$D" "$SEAT/probes/shims" "$S/fx"
export SHIM_ESCAPE=dforkplain; run esc-dforkplain "TERM@1.2" "$D" "$SEAT/probes/shims" "$S/fx"
unset SHIM_ESCAPE SHIM_PRE_SLEEP

# --- 5. environment cases (no shims, no signals)
R79_TMPDIR=UNSET                     run tmpdir-unset    "" "$D" - "$S/fx"
mkdir -p "$S/tmp-ro" && chmod 500 "$S/tmp-ro"
R79_TMPDIR="$S/tmp-ro"               run tmpdir-ro       "" "$D" - "$S/fx"
mkdir -p "$S/tmp with spaces"
R79_TMPDIR="$S/tmp with spaces"      run tmpdir-spaces   "" "$D" - "$S/fx"
mkdir -p "$S/tmp-real" && ln -sfn "$S/tmp-real" "$S/tmp-link"
R79_TMPDIR="$S/tmp-link"             run tmpdir-symlink  "" "$D" - "$S/fx"
R79_HOME=UNSET                       run home-unset      "" "$D" - "$S/fx"
R79_ULIMIT=60                        run ulimit60        "" "$D" - "$S/fx"

# --- 6. huge child output (100 MB) with and without NUL bytes; dirty fixture
cp -a "$S/fx" "$S/fx-big"; touch "$S/fx-big/repo/untracked.txt"
export SHIM_PAYLOAD=x
run big-x   "" "$D" "$SEAT/probes/shims" "$S/fx-big"
export SHIM_PAYLOAD=nul
run big-nul "" "$D" "$SEAT/probes/shims" "$S/fx-big"
unset SHIM_PAYLOAD

# --- 7. hammer: TERM at a uniform random offset in [0.02,0.65] s, fast fixture
for i in $(seq 1 150); do
  T="$(awk "BEGIN{srand($i);printf \"%.3f\", 0.02+rand()*0.63}")"
  run "hammer-$i" "TERM@$T" "$D" - "$S/fx"
done
echo "sweep complete: $(wc -l <"$ROSTER") cases"
