#!/bin/bash
pid=$1
now=""
{ read -r now < "/proc/$pid/stat"; } 2>/dev/null
echo "FIRSTLINE fields-after-strip: $(rest=${now##*) }; set -- $rest; echo $#)"
now2=""
{ IFS= read -r -d '' now2 < "/proc/$pid/stat"; } 2>/dev/null || true
echo "WHOLEFILE status=${?} len=${#now2} fields: $(rest=${now2##*)}; set -- $rest; echo $#)"
