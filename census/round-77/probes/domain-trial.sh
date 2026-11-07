#!/usr/bin/env bash
# souji r77 domain trial (C1 conjunct; answers r76 routed defects 1 and 2).
# Usage: bash census/round-77/probes/domain-trial.sh REPORT PREREG OUT
# Runs the lane's committed gate (tools/souji-pre-report-gate.sh at the lane's current files) over the lane
# itself and writes OUT outside the lane (OUT must not exist and must not be inside the lane, so the
# receipt cannot dirty the tree it grades). The receipt binds:
#   trial_script=<lane-relative path of this script> sha256=<its bytes>  (defect 1: the trial is the
#     committed script, not a scratch copy)
#   gate=tools/souji-pre-report-gate.sh sha256=<bytes run>, writer sha256, and the gate blob at master
#   report_lines=<N> report_sha256=<sha of the N lines graded>  (defect 2: a verifier re-derives the
#     graded bytes as `head -n N <filed report> | sha256sum`; lines appended after the trial are visible)
set -u
report=$1 prereg=$2 out=$3
lane=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
self="census/round-77/probes/domain-trial.sh"
[[ $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}") == "$lane/$self" ]] \
  || { echo "domain-trial: run the committed script at $lane/$self" >&2; exit 2; }
[[ -e $out ]] && { echo "domain-trial: $out exists" >&2; exit 2; }
case $(realpath -m -- "$out") in "$lane"/*) echo "domain-trial: OUT inside the lane" >&2; exit 2 ;; esac
[[ -f $report && -f $prereg ]] || { echo "domain-trial: report or prereg missing" >&2; exit 2; }
n=$(wc -l < "$report")
{
  printf 'command=bash %s %s %s %s\n' "$self" "$report" "$prereg" "$out"
  printf 'rev=%s\n' "$(git -C "$lane" rev-parse master)"
  printf 'trial_script=%s sha256=%s\n' "$self" "$(sha256sum -- "$lane/$self" | cut -d' ' -f1)"
  printf 'trial_script_blob_at_master_sha256=%s\n' "$(git -C "$lane" show "master:$self" 2>/dev/null | sha256sum | cut -d' ' -f1)"
  printf 'gate=tools/souji-pre-report-gate.sh sha256=%s\n' "$(sha256sum -- "$lane/tools/souji-pre-report-gate.sh" | cut -d' ' -f1)"
  printf 'gate_blob_at_master_sha256=%s\n' "$(git -C "$lane" show master:tools/souji-pre-report-gate.sh | sha256sum | cut -d' ' -f1)"
  printf 'writer sha256=%s\n' "$(sha256sum -- "$lane/tools/souji-receipt-write.py" | cut -d' ' -f1)"
  printf 'report=%s report_lines=%s report_sha256=%s\n' "$report" "$n" "$(head -n "$n" -- "$report" | sha256sum | cut -d' ' -f1)"
  printf 'remote_tip=%s\n' "$(git -C "$lane" ls-remote origin refs/heads/master | cut -f1)"
  printf '# host=%s git=%s\n' "$(uname -sr)" "$(git --version | awk '{print $3}')"
  t0=$(date +%s.%N)
  bash "$lane/tools/souji-pre-report-gate.sh" --lane "$lane" --branch master --report "$report" --prereg "$prereg" 2>&1
  rc=$?
  printf 'wall_seconds=%s\n' "$(echo "$(date +%s.%N) - $t0" | bc)"
  printf 'EXIT=%s\n' "$rc"
} > "$out"
cat "$out"
