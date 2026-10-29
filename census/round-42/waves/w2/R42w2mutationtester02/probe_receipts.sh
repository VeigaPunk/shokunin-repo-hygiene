#!/usr/bin/env bash
# R42w2mutationtester02 - re-run the probes the report cites that had no saved receipt.
# Writes receipts/probe_extra.txt (stdout of every probe). Scratch only under SCRATCH.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
SEAT="$LANE/.ufo/waves/round-42/w2/R42w2mutationtester02"
REV=3105a63b23481fccf7df58e74d14a6681e0ea0c8
SCRATCH=/fast/scratch/hyaku/souji-r42/R42w2mutationtester02/receipts
rm -rf "$SCRATCH"; mkdir -p "$SCRATCH" "$SEAT/receipts"
export TMPDIR="$SCRATCH/tmp"; mkdir -p "$TMPDIR"
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null LC_ALL=C
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
PRISTINE="$SCRATCH/pristine.py"
git -C "$LANE" show "$REV:tools/souji-freeze-check.py" > "$PRISTINE"
M="$SEAT/mutants"
SHA_C=a3a5e715f0cc574a73c3f9bebb6bc24f32ffd5b67b387244c2c909da779a1478
SHA_P=bc0405cffdbb957b8790ce8d5ced0091b4d0b2f32bee8f8a5ffc143032bda4f8
OUT="$SEAT/receipts/probe_extra.txt"
: > "$OUT"

mkrepo() { # $1 = name -> prints repo dir, base sha in $SCRATCH/$1.base
  d="$SCRATCH/$1"; rm -rf "$d"; mkdir -p "$d"
  git -C "$d" init -q -b main
  echo seed > "$d/seed.txt"; git -C "$d" add -A; git -C "$d" commit -qm seed
  git -C "$d" rev-parse HEAD > "$SCRATCH/$1.base"
  echo "$d"
}
run_tool() { # $1 tool  $2 dir  $3 rev  $4 prereg
  out=$(python3 -B "$1" --root "$2" --prereg "$4" --rev "$3" 2>"$SCRATCH/err.txt"); rc=$?
  printf '  %-34s rc=%d out=%s err=%s\n' "$(basename "$1")" "$rc" "$(echo "$out" | tr '\n' '|')" "$(tr '\n' '|' < "$SCRATCH/err.txt")"
}

{
echo "## N30 finding order: two findings, discovery order != sorted order"
d=$(mkrepo n30); b0=$(cat "$SCRATCH/n30.base")
echo c > "$d/c.py"; printf 'h\nr\n' > "$d/p.tsv"; echo 'x
EXIT=1' > "$d/ctl.txt"
printf 'Round: 7\n## C1\nBase: %s\nCounter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n' "$b0" "$SHA_C" "$SHA_P" > "$d/prereg.txt"
git -C "$d" add -A; git -C "$d" commit -qm c
printf 'Round: 7\n## C1\nBase: %s\nCounter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nKill: k\n' "$b0" "0000000000000000000000000000000000000000000000000000000000000000" "$SHA_P" > "$d/prereg.txt"
git -C "$d" add -A; git -C "$d" commit -qm c2; rev=$(git -C "$d" rev-parse HEAD)
run_tool "$PRISTINE" "$d" "$rev" prereg.txt
run_tool "$M/N30-main-findings-unsorted.py" "$d" "$rev" prereg.txt

echo "## N33 --rev not 40-hex (symbolic HEAD)"
run_tool "$PRISTINE" "$d" HEAD prereg.txt
run_tool "$M/N33-main-rev-format-not-checked.py" "$d" HEAD prereg.txt

echo "## M22 dispatch pathspec: sibling directory round-421 must NOT match round-42"
d=$(mkrepo m22); b0=$(cat "$SCRATCH/m22.base")
mkdir -p "$d/.ufo/waves/round-421"; echo '{}' > "$d/.ufo/waves/round-421/w1-spec.json"
echo c > "$d/c.py"; printf 'h\nr\n' > "$d/p.tsv"; echo 'x
EXIT=1' > "$d/ctl.txt"
printf 'Round: 7\n## C1\nBase: %s\nCounter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n' "$b0" "$SHA_C" "$SHA_P" > "$d/prereg.txt"
git -C "$d" add -A; git -C "$d" commit -qm c; rev=$(git -C "$d" rev-parse HEAD)
run_tool "$PRISTINE" "$d" "$rev" prereg.txt
run_tool "$M/M22-dispatch-tree-no-slash.py" "$d" "$rev" prereg.txt

echo "## patch P-raise: digest function raises at runtime (exception path of --selftest)"
PP="$SCRATCH/patch-raise"; mkdir -p "$PP"
cat > "$PP/sitecustomize.py" <<'PY'
import hashlib
class _Raise(object):
    def __init__(self, *a, **k):
        raise RuntimeError("injected digest failure")
hashlib.sha256 = _Raise
PY
for t in "$PRISTINE" "$M/M51-selftest-exception-passes.py" "$M/M54-selftest-expectation-ignored.py"; do
  o=$(PYTHONPATH="$PP" python3 -B "$t" --selftest 2>/dev/null); rc=$?
  printf '  %-34s rc=%d out=%s\n' "$(basename "$t")" "$rc" "$o"
done

echo "## patch P4: finding class renamed in printed output, exit code unchanged"
PQ="$SCRATCH/patch-p4"; mkdir -p "$PQ"
cat > "$PQ/sitecustomize.py" <<'PY'
import builtins
_print = builtins.print
def _p(*a, **k):
    a = tuple(str(x).replace("COUNTER-DIGEST", "DIGEST-MISMATCH") for x in a)
    return _print(*a, **k)
builtins.print = _p
PY
for t in "$PRISTINE" "$M/M51-selftest-exception-passes.py" "$M/M54-selftest-expectation-ignored.py"; do
  o=$(PYTHONPATH="$PQ" python3 -B "$t" --selftest 2>/dev/null | tail -1); rc=$?
  printf '  %-34s out=%s\n' "$(basename "$t")" "$o"
done
} >> "$OUT" 2>&1
echo "wrote $OUT"
rm -rf "$SCRATCH"
