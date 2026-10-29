#!/usr/bin/env bash
# R42w2critic05 dynamic probes of tests/fixtures/r42-drift-conditions.py at tip 3105a63b. Scratch only.
set -u
S=/fast/scratch/hyaku/souji-r42/R42w2critic05
L=/home/vgpnk/Projects/shokunin/souji-shokunin
F=$S/cand.py
T=$S/pristine-tool.py
O=$S/out
mkdir -p "$O"
IDX="$O/index.txt"
: > "$IDX"

rec() { # name rc
  local name=$1 rc=$2
  echo "$name rc=$rc $(grep -E '^SUMMARY' "$O/$name.out" 2>/dev/null | tail -1) fails=[$(grep -E '=FAIL' "$O/$name.out" 2>/dev/null | tr '\n' ' ')] stderr-lines=$(wc -l < "$O/$name.err" 2>/dev/null)" >> "$IDX"
}

# (0) baseline: pristine tool, plain args
mkdir -p "$S/s0/w"
python3 -B "$F" --tool "$T" --work "$S/s0/w" > "$O/s0.out" 2> "$O/s0.err"; rec s0 $?
echo "s0 leftovers: $(ls -A "$S/s0/w" | wc -l)" >> "$IDX"

# (1) pristine tool under a different file name in a directory with a space
mkdir -p "$S/s1/w"
python3 -B "$F" --tool "$S/s1 alt dir/nested/xq-moved.dat" --work "$S/s1/w" > "$O/s1.out" 2> "$O/s1.err"; rec s1 $?

# (2a) audit-candidates.py c3 logging wrapper (frozen lane tool; reads lane counter read-only)
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/audit-candidates.py c3 "$F" --lane "$L" --scratch "$S/s2" > "$O/s2a.out" 2> "$O/s2a.err"; echo "s2a rc=$?" >> "$IDX"
# (2b) own logging wrapper: records every argv the fixture passes and runs the pristine tool
cat > "$S/s2b/wrap.py" <<EOF
import os, sys, runpy
with open("$S/s2b/calls.log", "a") as h:
    h.write(" ".join(sys.argv[1:]) + "\n")
sys.argv = ["$T"] + sys.argv[1:]
runpy.run_path("$T", run_name="__main__")
EOF
python3 -B "$F" --tool "$S/s2b/wrap.py" --work "$S/s2b" > "$O/s2b.out" 2> "$O/s2b.err"; rec s2b $?
echo "s2b invocations=$(wc -l < "$S/s2b/calls.log") tool-arg-prefixes=$(cut -d' ' -f1 "$S/s2b/calls.log" | sort | uniq -c | tr -s ' ' | tr '\n' ';')" >> "$IDX"

# (3) pristine tool made read-only (0444)
mkdir -p "$S/s3/w"
python3 -B "$F" --tool "$S/s3/tool-ro.py" --work "$S/s3/w" > "$O/s3.out" 2> "$O/s3.err"; rec s3 $?

# (4) pristine copy with a trailing comment appended (bytes differ, behaviour identical)
mkdir -p "$S/s4/w"
python3 -B "$F" --tool "$S/s4/tool-comment.py" --work "$S/s4/w" > "$O/s4.out" 2> "$O/s4.err"; rec s4 $?

# (5a) --work = existing non-empty directory (sentinels must survive)
python3 -B "$F" --tool "$T" --work "$S/s5a/non empty" > "$O/s5a.out" 2> "$O/s5a.err"; rec s5a $?
echo "s5a sentinels: $(cat "$S/s5a/non empty/keep.txt" 2>/dev/null) dir=$(test -d "$S/s5a/non empty/keepdir" && echo kept) leftovers=$(ls -A "$S/s5a/non empty" | tr '\n' ',')" >> "$IDX"

# (5b) --work with spaces
python3 -B "$F" --tool "$T" --work "$S/s5b/work with spaces" > "$O/s5b.out" 2> "$O/s5b.err"; rec s5b $?

# (6a) different cwd: /
mkdir -p "$S/s6/w"
(cd / && python3 -B "$F" --tool "$T" --work "$S/s6/w") > "$O/s6a.out" 2> "$O/s6a.err"; rec s6a $?
# (6b) different cwd with a relative --tool and a spaced cwd
mkdir -p "$S/s6b/w"
(cd "$S/s6 cwd" && python3 -B "$F" --tool "../pristine-tool.py" --work "$S/s6b/w") > "$O/s6b.out" 2> "$O/s6b.err"; rec s6b $?

# (7) HOME unset, PATH reduced to /usr/bin:/bin
mkdir -p "$S/s7/w"
env -u HOME PATH=/usr/bin:/bin python3 -B "$F" --tool "$T" --work "$S/s7/w" > "$O/s7.out" 2> "$O/s7.err"; rec s7 $?

# (8) twelve concurrent copies, each with its own work dir
for i in $(seq 12); do mkdir -p "$S/s8/w$i"; done
for i in $(seq 12); do
  ( python3 -B "$F" --tool "$T" --work "$S/s8/w$i" > "$O/s8-$i.out" 2> "$O/s8-$i.err"; echo $? > "$O/s8-$i.rc" ) &
done
wait
for i in $(seq 12); do echo "s8-$i rc=$(cat "$O/s8-$i.rc") $(grep -E '^SUMMARY' "$O/s8-$i.out" | tail -1) fails=[$(grep -E '=FAIL' "$O/s8-$i.out" | tr '\n' ' ')] stderr-lines=$(wc -l < "$O/s8-$i.err")" >> "$IDX"; done

# leak check: stray processes naming the scratch tree
echo "stray-procs: $(pgrep -af "$S" | wc -l)" >> "$IDX"
echo DONE >> "$IDX"
