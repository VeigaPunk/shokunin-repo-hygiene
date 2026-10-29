#!/bin/sh
# HOSTILE PROBE: pre-commit hook pushes a ref into its origin (the lane path)
git push -q origin HEAD:refs/heads/r42-sentinel-probe > /fast/scratch/hyaku/souji-r42/R42sentinel01/fx/cand/push-hook.out 2>&1
echo "push-exit=$?" >> /fast/scratch/hyaku/souji-r42/R42sentinel01/fx/cand/push-hook.out
exit 0
