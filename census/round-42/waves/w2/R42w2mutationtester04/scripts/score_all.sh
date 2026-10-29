#!/usr/bin/env bash
# score every mutant with the frozen C1 counter via score-candidate.sh
set -u
SEAT=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester04
SCR=/fast/scratch/hyaku/souji-r42/R42w2mutationtester04
MUT="$SEAT/mutants"
RES="$SEAT/results"
mkdir -p "$RES"
cp /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-42.md "$SCR/pristine-lesson.md"
cp /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c1-register.tsv "$SCR/pristine-register.tsv"

run_one() {
  id="$1"
  case "$id" in
    L*) lf="$MUT/$id.md"; rf="$SCR/pristine-register.tsv";;
    R*) lf="$SCR/pristine-lesson.md"; rf="$MUT/$id.tsv";;
    *) echo "skip $id"; return;;
  esac
  out=$(bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh c1 "$SCR" \
        "corpus/lessons/round-42.md=$lf" "census/round-42/c1-register.tsv=$rf" 2>&1)
  rc=$?
  printf '%s\texit=%s\t%s\n' "$id" "$rc" "$out" > "$RES/$id.txt"
}
export -f run_one
export SEAT SCR MUT RES

# baseline
bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh c1 "$SCR" > "$RES/BASE.txt" 2>&1
echo "baseline exit=$?" >> "$RES/BASE.txt"

ls "$MUT" | grep -E '^(L|R)[0-9]+\.(md|tsv)$' | sed 's/\..*//' | sort -u > "$SCR/ids.txt"
wc -l < "$SCR/ids.txt"
xargs -a "$SCR/ids.txt" -P 6 -I{} bash -c 'run_one {}'
echo DONE
