#!/bin/bash
# caller wrapper: claim the worker role from a session leader, then exec the tool
exec bash /fast/scratch/hyaku/souji-r80/S80Sentinel/tool.sh "$@"
