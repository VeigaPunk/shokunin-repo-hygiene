#!/usr/bin/env bash
# round-57 matrix receipt taker (L1): runs the v5 counter (census/round-56/
# c1-counter.py, the before arm, frozen bytes never edited) and the v6 counter
# (census/round-57/c1-counter.py) over the round-57 fixture set (36 C1
# fixtures: the 33 r56 rows plus B4/C4/C6) and writes the two matrix TSVs.
# Finding extraction keeps the r54 verifier spot-check §5.2 rule for the first
# column and adds the FULL ordered finding list (the r57 all-findings rule).
# Usage: bash census/round-57/fixtures/run-matrix.sh <scratch> <outdir>
#   (run the builder first: python3 -B census/round-57/fixtures/build-fixtures.py
#    --work <scratch>/selftest --manifest <scratch>/selftest/fixture-manifest.tsv)
set -u
S=${1:?scratch}; OUT=${2:?outdir}
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
M="$S/selftest/fixture-manifest.tsv"
[ -f "$M" ] || { echo "manifest missing: $M" >&2; exit 2; }
mkdir -p "$OUT"

c1_arm() { # $1 = counter label, $2 = counter path (relative to LANE)
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tfindings_all\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C1 ] || continue
    case "$n" in F5-REWRITE|F6-RECORD-DRIFT|F27-BINARY-NUMSTAT) bb="$b";; *) bb="$t";; esac
    out=$(cd "$LANE" && TMPDIR="$S" python3 -B "$2" --root "$d" --rev "$t" --base "$bb" \
      --record-sha256 "$r" --sources-rev-before "$t" --sources-rev-after "$t" --scratch "$S" 2>&1); rc=$?
    f=$(printf '%s\n' "$out" | awk '/^FINDING /{print $2; exit}')
    all=$(printf '%s\n' "$out" | awk '/^FINDING /{printf "%s,",$2}' | sed 's/,$//')
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$n" "$1" "${t:0:12}" "${bb:0:12}" \
      "$rc" "${f:--}" "${all:--}" "$sum"
  done
}

c1_arm v5-r56 census/round-56/c1-counter.py > "$OUT/c1-matrix-v5.tsv"; echo "c1-v5 arm written"
c1_arm v6-r57 census/round-57/c1-counter.py > "$OUT/c1-matrix-v6.tsv"; echo "c1-v6 arm written"
