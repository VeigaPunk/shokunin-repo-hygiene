#!/bin/bash
# Measure the two stat-read shapes for a given pid.
pid=$1
if [ ! -r "/proc/$pid/stat" ]; then echo "pid $pid unreadable"; exit 1; fi
now=""
{ read -r now < "/proc/$pid/stat"; } 2>/dev/null
st1=$?
rest=${now##*)}
set -- $rest
echo "FIRSTLINE status=$st1 bytes=${#now} fields_after_strip=$#"
now2=""
{ IFS= read -r -d '' now2 < "/proc/$pid/stat"; } 2>/dev/null
st2=$?
rest2=${now2##*)}
set -- $rest2
echo "WHOLEFILE status=$st2 bytes=${#now2} fields_after_strip=$#"
