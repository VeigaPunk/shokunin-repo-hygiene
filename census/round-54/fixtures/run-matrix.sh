#!/usr/bin/env bash
# round-54 matrix receipt taker (L1): runs the frozen v2 counters (r53) and
# the v3 counters (r54) over the committed fixture set and writes the matrix
# TSVs. The v2 arm is the acceptance control for the r53 routed surfaces.
# Usage: bash census/round-54/fixtures/run-matrix.sh <scratch> <outdir>
set -u
S=${1:?scratch}; OUT=${2:?outdir}
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
M="$S/selftest/fixture-manifest.tsv"
[ -f "$M" ] || { echo "manifest missing: $M" >&2; exit 2; }

c1_arm() { # $1 = counter label, $2 = counter path (relative to LANE)
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C1 ] || continue
    case "$n" in F5-REWRITE|F6-RECORD-DRIFT) bb="$b";; *) bb="$t";; esac
    out=$(cd "$LANE" && TMPDIR="$S" python3 -B "$2" --root "$d" --rev "$t" --base "$bb" \
      --record-sha256 "$r" --sources-rev-before "$t" --sources-rev-after "$t" --scratch "$S" 2>&1); rc=$?
    fin=$(printf '%s\n' "$out" | grep -oE '^FINDING [A-Z-]+' | head -1 | cut -d' ' -f2)
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$n" "$1" "${t:0:12}" "${bb:0:12}" "$rc" "${fin:--}" "$sum"
  done
}

c1_v2() { # the frozen r53 counter takes no --sources-rev args
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C1 ] || continue
    case "$n" in F5-REWRITE|F6-RECORD-DRIFT) bb="$b";; *) bb="$t";; esac
    out=$(cd "$LANE" && TMPDIR="$S" python3 -B census/round-53/c1-counter.py --root "$d" --rev "$t" \
      --base "$bb" --record-sha256 "$r" --scratch "$S" 2>&1); rc=$?
    fin=$(printf '%s\n' "$out" | grep -oE '^FINDING [A-Z-]+' | head -1 | cut -d' ' -f2)
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\tv2-r53\t%s\t%s\t%s\t%s\t%s\n' "$n" "${t:0:12}" "${bb:0:12}" "$rc" "${fin:--}" "$sum"
  done
}

c2_arm() { # $1 = counter label, $2 = counter path
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C2 ] || continue
    out=$(cd "$LANE" && TMPDIR="$S" python3 -B "$2" --root "$d" --rev "$t" \
      --capture census/round-52/records/fleet-root-census.tsv \
      --receipt census/round-53/records/fleet-root-census-run.txt --scratch "$S" 2>&1); rc=$?
    fin=$(printf '%s\n' "$out" | grep -oE '^FINDING [A-Z-]+' | head -1 | cut -d' ' -f2)
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\t%s\t%s\t-\t%s\t%s\t%s\n' "$n" "$1" "${t:0:12}" "$rc" "${fin:--}" "$sum"
  done
}

c1_v2 > "$OUT/c1-matrix-v2.tsv"; echo "c1-v2 rc=$?"
c1_arm v3-r54 census/round-54/c1-counter.py > "$OUT/c1-matrix-v3.tsv"; echo "c1-v3 rc=$?"
c2_arm v2-r53 census/round-53/c2-counter.py > "$OUT/c2-matrix-v2.tsv"; echo "c2-v2 rc=$?"
c2_arm v3-r54 census/round-54/c2-counter.py > "$OUT/c2-matrix-v3.tsv"; echo "c2-v3 rc=$?"
