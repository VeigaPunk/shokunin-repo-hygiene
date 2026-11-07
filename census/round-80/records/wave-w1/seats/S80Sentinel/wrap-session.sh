#!/bin/bash
# caller wrapper: export the tool's own session id as SOUJI_Q_SESSION, then exec it
sid=$(awk '{r=$0; sub(/^[^)]*\) /,"",r); split(r,a," "); print a[4]}' "/proc/$$/stat")
export SOUJI_Q_SESSION=$sid
exec bash /fast/scratch/hyaku/souji-r80/S80Sentinel/tool.sh "$@"
