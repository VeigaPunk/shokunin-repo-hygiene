#!/usr/bin/env bash
# S55executor01: four-row re-run of the frozen round-55 matrix, identical logic
# to census/round-55/fixtures/run-matrix.sh c1_arm, filtered to four fixtures.
set -u
S=${1:?scratch}; OUT=${2:?outdir}
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
M="$S/manifest.tsv"
[ -f "$M" ] || { echo "manifest missing: $M" >&2; exit 2; }
FILTER='F7-FF|F13-DUAL-ANCHOR|F17-INDENT4-FENCE|F23-SOURCES-RECOMP'

finof() {
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
  done | grep -E "^(fixture|($FILTER)	)"
}

mkdir -p "$OUT"
c1_arm v3-r54 census/round-54/c1-counter.py > "$OUT/c1-matrix-v3.tsv"
c1_arm v4-r55 census/round-55/c1-counter.py > "$OUT/c1-matrix-v4.tsv"
echo "rows-v3=$(($(wc -l < "$OUT/c1-matrix-v3.tsv")-1)) rows-v4=$(($(wc -l < "$OUT/c1-matrix-v4.tsv")-1))"
