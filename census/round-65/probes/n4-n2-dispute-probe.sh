#!/bin/sh
# census/round-65/probes/n4-n2-dispute-probe.sh — souji round 65, M1/M5 probe duty (r63 lesson).
# Resolves, mechanically and against BOTH writer bytes, the two fixture disputes round 64 routed:
#   M1 (N4): the round-64 design reviewer reported base=refuse on a subdirectory-root fixture,
#       while the round-64 counter's frozen N4 fixture gives base=accept. The difference is the
#       root-level dual seed copy. Shape R (reviewer, no dual seed): base must fail to resolve its
#       instrument blob. Shape C (counter, dual seed): base must accept the out-of-subtree forge.
#   M5 (N2): an EMPTY pre-run untracked directory vs the frozen NON-EMPTY fixture.
# Every run binds the writer bytes by sha256. Writes only under $WORK and the receipt paths given.
set -eu
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
BASE_REV=4a43a4d919c5b51ae9be859a1266ce4b11337b0b
WORK=${1:?usage: n4-n2-dispute-probe.sh WORK}
BASE_W=${2:-$LANE/.ufo/waves/round-65/build/base-writer.py}
NEW_W=${3:-$LANE/.ufo/waves/round-65/build/souji-receipt-write.py}
mkdir -p "$WORK"
git -C "$LANE" show "$BASE_REV:tools/souji-receipt-write.py" > "$BASE_W"
E() { printf '%s\n' "$*" >&2; exit 2; }
run_writer() { # slot repo rev out rootsub [wrapped-python-code] -> rc on stdout
    slot=$1; repo=$2; rev=$3; out=$4; rootsub=$5; code=${6:-}
    instrument="tools/instr.sh"; [ -n "$rootsub" ] && { instrument="instr.sh"; root="$repo/$rootsub"; } || root="$repo"
    if [ -n "$code" ]; then
        python3 -B "$slot" --root "$root" --rev "$rev" --instrument "$instrument" --out "$out" \
            --allow-outside --allow-dirty -- python3 -c "$code" >/dev/null 2>"$WORK/err-$$.txt" && rc=0 || rc=$?
    else
        python3 -B "$slot" --root "$root" --rev "$rev" --instrument "$instrument" --out "$out" \
            --allow-outside --allow-dirty -- /bin/echo hi >/dev/null 2>"$WORK/err-$$.txt" && rc=0 || rc=$?
    fi
    cp "$WORK/err-$$.txt" "$out.err" 2>/dev/null || :; printf '%s' "$rc"
}
sha() { sha256sum "$1" | cut -c1-16; }
mk() { # dir -> creates seeded fixture repo, echoes rev  (no dual copies unless 2nd arg = dual)
    d=$1; dual=${2:-}; rm -rf "$d"; mkdir -p "$d/repo/tools"
    git -C "$d/repo" init -q
    git -C "$d/repo" config user.name P65; git -C "$d/repo" config user.email p65@invalid
    printf '#!/bin/sh\necho instrument-ok\n' > "$d/repo/tools/instr.sh"
    chmod +x "$d/repo/tools/instr.sh"
    printf 'notes v1\n' > "$d/repo/tools/notes.txt"
    printf 'readme v1\n' > "$d/repo/README.md"
    [ "$dual" = dual ] && cp "$d/repo/tools/instr.sh" "$d/repo/instr.sh"
    GIT_AUTHOR_DATE=2026-11-05T12:00:00Z GIT_COMMITTER_DATE=2026-11-05T12:00:00Z \
        git -C "$d/repo" add -A && git -C "$d/repo" commit -q -m seed
    git -C "$d/repo" rev-parse HEAD
}
echo "# n4-n2-dispute-probe base=$(sha "$BASE_W") new=$(sha "$NEW_W") base_rev=$BASE_REV"

# --- M1 shape R (reviewer's fixture: --root tools, NO root-level dual copy) ---
for slotname in base new; do
    d="$WORK/n4-R-$slotname"; rev=$(mk "$d")
    [ "$slotname" = base ] && slot=$BASE_W || slot=$NEW_W
    rc=$(run_writer "$slot" "$d/repo" "$rev" "$d/out.txt" tools)
    echo "N4-R $slotname rc=$rc out_exists=$([ -e "$d/out.txt" ] && echo yes || echo no) stderr=$(head -c 160 "$d/out.err" | tr '\n' ' ')"
done

# --- M1 shape C (counter fixture: dual seed copy) ---
for slotname in base new; do
    d="$WORK/n4-C-$slotname"; rev=$(mk "$d" dual)
    [ "$slotname" = base ] && slot=$BASE_W || slot=$NEW_W
    git -C "$d/repo" update-index --skip-worktree README.md
    printf 'readme FORGED\n' > "$d/repo/README.md"
    rc=$(run_writer "$slot" "$d/repo" "$rev" "$d/out.txt" tools)
    echo "N4-C $slotname rc=$rc out_exists=$([ -e "$d/out.txt" ] && echo yes || echo no) stderr=$(head -c 160 "$d/out.err" | tr '\n' ' ')"
done

# --- M5 shape E (EMPTY pre-run untracked dir, in-run file) vs shape N (non-empty, the frozen
#     fixture shape), each also with a pre-existing-file polarity arm (expect accept both slots) ---
for shape in E N; do
    for slotname in base new; do
        d="$WORK/n2-$shape-$slotname"; rev=$(mk "$d")
        [ "$slotname" = base ] && slot=$BASE_W || slot=$NEW_W
        mkdir -p "$d/repo/tools/extra"
        [ "$shape" = N ] && printf 'k\n' > "$d/repo/tools/extra/keep.txt"
        rc=$(python3 -B "$slot" --root "$d/repo" --rev "$rev" --instrument tools/instr.sh \
            --out "$d/out.txt" --allow-outside --allow-dirty -- \
            python3 -c "import sys
open(sys.argv[1], 'wb').write(b'new\n')" "$d/repo/tools/extra/new.txt" >/dev/null 2>"$d/out.err" && echo 0 || echo $?)
        echo "N2-$shape-inrun $slotname rc=$rc out_exists=$([ -e "$d/out.txt" ] && echo yes || echo no) stderr=$(head -c 160 "$d/out.err" | tr '\n' ' ')"
        # polarity arm: the file pre-exists the run (honest allow-dirty baseline) -> accept
        d2="$WORK/n2-$shape-pre-$slotname"; rev2=$(mk "$d2")
        mkdir -p "$d2/repo/tools/extra"
        [ "$shape" = N ] && printf 'k\n' > "$d2/repo/tools/extra/keep.txt"
        python3 -c "import sys; open(sys.argv[1],'wb').write(b'new\n')" "$d2/repo/tools/extra/new.txt"
        [ "$slotname" = base ] && slot2=$BASE_W || slot2=$NEW_W
        rc2=$(python3 -B "$slot2" --root "$d2/repo" --rev "$rev2" --instrument tools/instr.sh \
            --out "$d2/out.txt" --allow-outside --allow-dirty -- /bin/echo hi >/dev/null 2>"$d2/out.err" && echo 0 || echo $?)
        echo "N2-$shape-prerun $slotname rc=$rc2 out_exists=$([ -e "$d2/out.txt" ] && echo yes || echo no) stderr=$(head -c 160 "$d2/out.err" | tr '\n' ' ')"
    done
done
echo "PROBE-COMPLETE"
