#!/usr/bin/env bash
# round-53 matrix receipt taker (L1): runs the frozen v1 counters and the v2
# counters over the committed fixture set and writes the matrix TSVs.
# Usage: bash census/round-53/fixtures/run-matrix.sh <scratch> <outdir>
set -u
S=${1:?scratch}; OUT=${2:?outdir}
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
M="$S/selftest/fixture-manifest.tsv"
[ -f "$M" ] || { echo "manifest missing: $M" >&2; exit 2; }

hdr() { printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'; }

c1_v1() {
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C1 ] || continue
    out=$(TMPDIR="$S" python3 -B census/round-52/c1-counter.py --root "$d" --rev "$t" --scratch "$S" 2>&1); rc=$?
    fin=$(printf '%s\n' "$out" | grep -oE '^FINDING [A-Z-]+' | head -1 | cut -d' ' -f2)
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\tv1-r52\t%s\t-\t%s\t%s\t%s\n' "$n" "${t:0:12}" "$rc" "${fin:--}" "$sum"
  done
}

c1_v2() {
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C1 ] || continue
    case "$n" in F5-REWRITE|F6-RECORD-DRIFT) bb="$b";; *) bb="$t";; esac
    out=$(TMPDIR="$S" python3 -B census/round-53/c1-counter.py --root "$d" --rev "$t" --base "$bb" --record-sha256 "$r" --scratch "$S" 2>&1); rc=$?
    fin=$(printf '%s\n' "$out" | grep -oE '^FINDING [A-Z-]+' | head -1 | cut -d' ' -f2)
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\tv2-r53\t%s\t%s\t%s\t%s\t%s\n' "$n" "${t:0:12}" "${bb:0:12}" "$rc" "${fin:--}" "$sum"
  done
}

c2_v1() {
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C2 ] || continue
    out=$(TMPDIR="$S" python3 -B census/round-52/c2-counter.py --root "$d" --rev "$t" --scratch "$S" 2>&1); rc=$?
    fin=$(printf '%s\n' "$out" | grep -oE '^FINDING [A-Z-]+' | head -1 | cut -d' ' -f2)
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\tv1-r52\t%s\t-\t%s\t%s\t%s\n' "$n" "${t:0:12}" "$rc" "${fin:--}" "$sum"
  done
}

c2_v2() {
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C2 ] || continue
    out=$(TMPDIR="$S" python3 -B census/round-53/c2-counter.py --root "$d" --rev "$t" \
      --capture census/round-52/records/fleet-root-census.tsv \
      --receipt census/round-53/records/fleet-root-census-run.txt --scratch "$S" 2>&1); rc=$?
    fin=$(printf '%s\n' "$out" | grep -oE '^FINDING [A-Z-]+' | head -1 | cut -d' ' -f2)
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\tv2-r53\t%s\t-\t%s\t%s\t%s\n' "$n" "${t:0:12}" "$rc" "${fin:--}" "$sum"
  done
}

c1_v1 > "$OUT/c1-matrix-v1.tsv"; echo "c1-v1 rc=$?"
c1_v2 > "$OUT/c1-matrix-v2.tsv"; echo "c1-v2 rc=$?"
c2_v1 > "$OUT/c2-matrix-v1.tsv"; echo "c2-v1 rc=$?"
c2_v2 > "$OUT/c2-matrix-v2.tsv"; echo "c2-v2 rc=$?"
