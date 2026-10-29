#!/usr/bin/env bash
# R42w2mutationtester02 - score every mutant with the frozen r42 C2 counter and the tool's own --selftest.
# Usage: bash run_mutants.sh [parallelism]
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
SEAT="$LANE/.ufo/waves/round-42/w2/R42w2mutationtester02"
SCRATCH=/fast/scratch/hyaku/souji-r42/R42w2mutationtester02
PAR="${1:-6}"
mkdir -p "$SCRATCH/logs" "$SEAT/results"
export TMPDIR="$SCRATCH/tmp"
mkdir -p "$TMPDIR"

score_one() {
  name="${1%.py}"
  mutant="$SEAT/mutants/$name.py"
  work="$SCRATCH/work/$name"
  mkdir -p "$work"
  # --- 1. the tool's own --selftest, run directly on the mutant bytes
  st_out="$SCRATCH/logs/$name.selftest.txt"
  ( cd "$work" && TMPDIR="$work/tmp" mkdir -p "$work/tmp" && \
    TMPDIR="$work/tmp" timeout 600 python3 -B "$mutant" --selftest ) >"$st_out" 2>&1
  st_rc=$?
  # --- 2. the frozen C2 counter over the committed tip plus this mutant
  sc_out="$SCRATCH/logs/$name.counter.txt"
  ( cd "$work" && TMPDIR="$work/tmp" timeout 1800 bash "$LANE/census/round-42/score-candidate.sh" c2 "$work" \
      "tools/souji-freeze-check.py=$mutant" ) >"$sc_out" 2>&1
  sc_rc=$?
  # --- 3. record
  {
    printf 'mutant\t%s\n' "$name"
    printf 'selftest_exit\t%s\n' "$st_rc"
    printf 'selftest_out\t%s\n' "$(tr '\n' '|' < "$st_out" | cut -c1-400)"
    printf 'counter_exit\t%s\n' "$sc_rc"
    printf 'counter_summary\t%s\n' "$(grep -E '^SUMMARY ' "$sc_out" | tail -1)"
    printf 'counter_cases_failed\t%s\n' "$(grep -c '=FAIL' "$sc_out")"
    printf 'counter_failed_names\t%s\n' "$(grep -o 'case-[a-z0-9-]*=FAIL' "$sc_out" | tr '\n' ',' )"
    printf 'counter_legs\t%s\n' "$(grep -E '^(real|retro|retro_clean|selftest) ' "$sc_out" | tr '\n' '|')"
  } > "$SEAT/results/$name.tsv"
  rm -rf "$work"
}

export -f score_one
export LANE SEAT SCRATCH

ls "$SEAT/mutants" | grep -E '^M[0-9]+-' | \
  xargs -P "$PAR" -I{} bash -c 'score_one "$@"' _ {}
echo "DONE"
