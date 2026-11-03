#!/usr/bin/env bash
# round-55 matrix receipt taker (L1): runs the frozen v3 counters (r54) and
# the v4 counters (r55) over the committed round-55 fixture set and writes
# the matrix TSVs. The v3 arm is the acceptance control for the r54 routed
# surfaces. Finding extraction fixed per the r54 verifier spot-check §5.2:
# the second whitespace token of the first FINDING line (any case), so every
# counted kill row names its finding.
# Usage: bash census/round-55/fixtures/run-matrix.sh <scratch> <outdir>
set -u
S=${1:?scratch}; OUT=${2:?outdir}
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
M="$S/selftest/fixture-manifest.tsv"
[ -f "$M" ] || { echo "manifest missing: $M" >&2; exit 2; }

finof() { # first FINDING line's id token, or -
  printf '%s\n' "$1" | awk '/^FINDING /{print $2; exit}' | { read -r f; printf '%s' "${f:--}"; }
}

c1_arm() { # $1 = counter label, $2 = counter path (relative to LANE)
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C1 ] || continue
    case "$n" in F5-REWRITE|F6-RECORD-DRIFT) bb="$b";; *) bb="$t";; esac
    out=$(cd "$LANE" && TMPDIR="$S" python3 -B "$2" --root "$d" --rev "$t" --base "$bb" \
      --record-sha256 "$r" --sources-rev-before "$t" --sources-rev-after "$t" --scratch "$S" 2>&1); rc=$?
    f=$(finof "$out")
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$n" "$1" "${t:0:12}" "${bb:0:12}" "$rc" "$f" "$sum"
  done
}

c2_arm() { # $1 = counter label, $2 = counter path
  printf 'fixture\tcounter\trev\tbase\texit\tfinding\tSUMMARY\n'
  tail -n +2 "$M" | while IFS=$'\t' read -r n k d b t r; do
    [ "$k" = C2 ] || continue
    out=$(cd "$LANE" && TMPDIR="$S" python3 -B "$2" --root "$d" --rev "$t" \
      --capture census/round-52/records/fleet-root-census.tsv \
      --receipt census/round-53/records/fleet-root-census-run.txt --scratch "$S" 2>&1); rc=$?
    f=$(finof "$out")
    sum=$(printf '%s\n' "$out" | grep '^SUMMARY')
    printf '%s\t%s\t%s\t-\t%s\t%s\t%s\n' "$n" "$1" "${t:0:12}" "$rc" "$f" "$sum"
  done
}

c1_arm v3-r54 census/round-54/c1-counter.py > "$OUT/c1-matrix-v3.tsv"; echo "c1-v3 rc=$?"
c1_arm v4-r55 census/round-55/c1-counter.py > "$OUT/c1-matrix-v4.tsv"; echo "c1-v4 rc=$?"
c2_arm v3-r54 census/round-54/c2-counter.py > "$OUT/c2-matrix-v3.tsv"; echo "c2-v3 rc=$?"
c2_arm v4-r55 census/round-55/c2-counter.py > "$OUT/c2-matrix-v4.tsv"; echo "c2-v4 rc=$?"
