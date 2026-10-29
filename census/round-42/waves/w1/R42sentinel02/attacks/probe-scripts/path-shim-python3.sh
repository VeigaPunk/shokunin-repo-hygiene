#!/bin/sh
echo "SHIM invoked cwd=$(pwd) args=$*" >> /fast/scratch/hyaku/souji-r42/R42sentinel02/shim/log.txt
exec /usr/bin/python3 "$@"
