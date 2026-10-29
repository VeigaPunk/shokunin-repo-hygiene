#!/bin/sh
# HOSTILE PROBE: pre-commit hook dropped via dest .git/hooks/pre-commit
echo "HOOK-RAN pid=$$ uid=$(id -u) home=${HOME-unset} pwd=$(pwd)" > /fast/scratch/hyaku/souji-r42/R42sentinel01/fx/cand/hook-ran.txt
env | sort > /fast/scratch/hyaku/souji-r42/R42sentinel01/fx/cand/hook-env.txt
exit 0
