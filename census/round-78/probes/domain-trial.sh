#!/usr/bin/env bash
# souji r78 domain trial (C1 conjunct; copy of census/round-77/probes/domain-trial.sh with r77 routed defect 4
# answered: wall time from bash's EPOCHREALTIME, no `bc`; the receipt itself names the C1 candidate blob W and
# whether the gate run is that blob or a later amendment).
# Usage: bash census/round-78/probes/domain-trial.sh REPORT PREREG OUT
# Runs the lane's committed gate over the lane itself and writes OUT outside the lane. The receipt binds:
#   trial_script=<lane-relative path> sha256=<its bytes> and its blob at master;
#   gate sha256 of the bytes run, the gate blob at master, and the candidate blob of commit W
#     (amendment=none when they are equal, else amendment=<W blob> -> <run blob>);
#   report_lines=<N> report_sha256=<sha of the N lines graded> (`head -n N <filed report> | sha256sum`).
set -u
report=$1 prereg=$2 out=$3
W=ed22dc9cb7a6b61a7d0bd150db4a95191b1333aa
lane=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
self="census/round-78/probes/domain-trial.sh"
[[ $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}") == "$lane/$self" ]] \
  || { echo "domain-trial: run the committed script at $lane/$self" >&2; exit 2; }
[[ -e $out ]] && { echo "domain-trial: $out exists" >&2; exit 2; }
case $(realpath -m -- "$out") in "$lane"/*) echo "domain-trial: OUT inside the lane" >&2; exit 2 ;; esac
[[ -f $report && -f $prereg ]] || { echo "domain-trial: report or prereg missing" >&2; exit 2; }
n=$(wc -l < "$report")
run_sha=$(sha256sum -- "$lane/tools/souji-pre-report-gate.sh" | cut -d' ' -f1)
w_sha=$(git -C "$lane" show "$W:tools/souji-pre-report-gate.sh" | sha256sum | cut -d' ' -f1)
{
  printf 'command=bash %s %s %s %s\n' "$self" "$report" "$prereg" "$out"
  printf 'rev=%s\n' "$(git -C "$lane" rev-parse master)"
  printf 'trial_script=%s sha256=%s\n' "$self" "$(sha256sum -- "$lane/$self" | cut -d' ' -f1)"
  printf 'trial_script_blob_at_master_sha256=%s\n' "$(git -C "$lane" show "master:$self" 2>/dev/null | sha256sum | cut -d' ' -f1)"
  printf 'gate=tools/souji-pre-report-gate.sh sha256=%s\n' "$run_sha"
  printf 'gate_blob_at_master_sha256=%s\n' "$(git -C "$lane" show master:tools/souji-pre-report-gate.sh | sha256sum | cut -d' ' -f1)"
  printf 'candidate_W=%s gate_blob_sha256=%s\n' "$W" "$w_sha"
  if [[ $run_sha == "$w_sha" ]]; then printf 'amendment=none\n'; else printf 'amendment=%s -> %s\n' "$w_sha" "$run_sha"; fi
  printf 'writer sha256=%s\n' "$(sha256sum -- "$lane/tools/souji-receipt-write.py" | cut -d' ' -f1)"
  printf 'report=%s report_lines=%s report_sha256=%s\n' "$report" "$n" "$(head -n "$n" -- "$report" | sha256sum | cut -d' ' -f1)"
  printf 'remote_tip=%s\n' "$(git -C "$lane" ls-remote origin refs/heads/master | cut -f1)"
  printf '# host=%s git=%s\n' "$(uname -sr)" "$(git --version | awk '{print $3}')"
  t0=$EPOCHREALTIME
  bash "$lane/tools/souji-pre-report-gate.sh" --lane "$lane" --branch master --report "$report" --prereg "$prereg" 2>&1
  rc=$?
  t1=$EPOCHREALTIME
  us=$(( (${t1%.*} - ${t0%.*}) * 1000000 + 10#${t1#*.} - 10#${t0#*.} ))
  printf 'wall_seconds=%d.%06d\n' $((us / 1000000)) $((us % 1000000))
  printf 'EXIT=%s\n' "$rc"
} > "$out"
cat "$out"
