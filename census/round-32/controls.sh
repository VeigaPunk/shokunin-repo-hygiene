#!/usr/bin/env bash
# r32 L1 controls: do-nothing and cheapest-skip states scored with the FROZEN counters. Usage: controls.sh <prereg-commit>
# Scratch clone only (origin removed); never writes the lane. Output: TSV on stdout.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
B=85b61a151923986e7e6b48f7084b9122561b5f3d
P=${1:?prereg commit}
SCR=${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r32/L1controls
mkdir -p "$SCR"; D=$(mktemp -d "$SCR/ctl.XXXXXX") || exit 2
trap 'chmod -R u+w "$D" 2>/dev/null; rm -rf -- "$D"' EXIT
git clone -q --no-local "$LANE" "$D/c" || exit 2
C="$D/c"; git -C "$C" remote remove origin
[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "toplevel mismatch"; exit 2; }
g() { git -C "$C" -c user.name=ctl -c user.email=ctl@localhost -c core.hooksPath=/dev/null "$@"; }
c1() { python3 -B "$LANE/census/round-32/c1-counter.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s1" ${2:+--only "$2"} 2>&1 | grep '^SUMMARY'; }
c2() { python3 -B "$LANE/census/round-32/c2-counter.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s2" ${2:+--only "$2"} 2>&1 | grep '^SUMMARY'; }
c3() { python3 -B "$LANE/census/round-32/c3-counter.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s3" 2>&1 | grep '^SUMMARY'; }
printf 'control\tcounter\tresult\n'
printf 'C1-do-nothing(prereg)\tc1\t%s\n' "$(c1 $P)"
printf 'C2-do-nothing(prereg)\tc2\t%s\n' "$(c2 $P)"
printf 'C3-do-nothing(prereg)\tc3\t%s\n' "$(c3 $P)"
# C1 junk-1: withdraw every item (cheapest state that binds nothing)
g checkout -q --detach $P
{ printf '\n### control bindings\n\n| item | line | literal | binding | note |\n|---|---|---|---|---|\n'
  awk -F'\t' '!/^#/ && $1!="id" {printf "| %s | SCORECARD.md:%s | %s | withdrawn: no observable shows this count in the committed record | junk |\n", $1, $2, $3}' "$LANE/census/round-32/c1-items.tsv"; } >> "$C/SCORECARD.md"
g commit -qam junk1; J=$(g rev-parse HEAD)
printf 'C1-junk1(withdraw all)\tc1\t%s\n' "$(c1 $J)"
# C1 junk-2: mechanical record binder — first line of any eligible census/round-K/ blob holding the integer(s) and a unit
g checkout -q --detach $P
python3 - "$C" "$LANE/census/round-32/c1-items.tsv" > "$D/rows.md" <<'PY'
import re, subprocess, sys
C, tsv = sys.argv[1], sys.argv[2]
files = subprocess.run(["git", "-C", C, "ls-files", "census"], capture_output=True, text=True).stdout.split()
used = set()
print("\n### control bindings\n\n| item | line | literal | binding | note |\n|---|---|---|---|---|")
for ln in open(tsv):
    f = ln.rstrip("\n").split("\t")
    if ln.startswith("#") or f[0] == "id":
        continue
    iid, line, ints, units, rounds = f[0], f[1], f[2].split(), [u for u in f[3].split(",") if u], [r for r in f[4].split(",") if r]
    if not units:
        continue
    done = False
    for path in files:
        m = re.match(r"census/round-(\d+)/", path)
        if not m or m.group(1) not in rounds or {"waves", "transcripts", "sources"} & set(path.split("/")) or path.endswith((".py", ".sh", ".html", ".htm", ".raw")):
            continue
        try:
            text = open(f"{C}/{path}", errors="replace").read().splitlines()
        except (OSError, IsADirectoryError):
            continue
        for n, t in enumerate(text, 1):
            if (path, n) in used:
                continue
            if all(re.search(r"(?<!\d)" + x + r"(?!\d)", t) for x in ints) and any(u in t.lower() for u in units):
                lit = f"{units[0]}={ints[0]}" if len(ints) == 1 else "/".join(ints)
                print(f"| {iid} | SCORECARD.md:{line} | {lit} | record: {path}:{n} | junk |")
                used.add((path, n))
                done = True
                break
        if done:
            break
PY
cat "$D/rows.md" >> "$C/SCORECARD.md"
g commit -qam junk2; J=$(g rev-parse HEAD)
printf 'C1-junk2(mechanical record binder, %s rows)\tc1\t%s\n' "$(grep -c '| junk |' "$D/rows.md")" "$(c1 $J)"
# C2 junk: stub selftests that print the base anchor line without doing the work (T01, T05)
g checkout -q --detach $P
printf 'import sys\nprint("SELFTEST\\tpass=65\\tfail=0")\n' > "$C/tools/souji-landing-gate.py"
printf 'import sys\nprint("selftest=9/9")\n' > "$C/tools/souji-gate-check.py"
g commit -qam junkc2; J=$(g rev-parse HEAD)
printf 'C2-junk(stub selftests printing the anchor, T01+T05)\tc2\t%s\n' "$(c2 $J T01,T05)"
# C3 junk: sourceless F1 entry + map row + typed record + a fixture that prints the record
g checkout -q --detach $P
cat > "$C/census/round-32/records/jj-mtime-clock-run.txt" <<'EOF'
jj-version: jj 0.45.1
git-version: git version 2.56.0
RESULT arm=recent step=gc-default obj=B mtime=recent where=cruft object_present=yes
RESULT arm=old step=gc-default obj=B mtime=old where=absent object_present=no
RESULT arm=mixed step=gc-default obj=B mtime=old where=absent object_present=no
RESULT arm=mixed step=gc-default obj=C mtime=recent where=cruft object_present=yes
RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=cruft object_present=yes
RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=absent object_present=no
RESULT arm=nocruft step=gc-cruft-disabled obj=C mtime=recent where=loose object_present=yes
RESULT arm=recent step=start obj=B mtime=recent where=loose object_present=yes
EOF
printf '#!/usr/bin/env bash\ncat census/round-32/records/jj-mtime-clock-run.txt\n' > "$C/tests/fixtures/r32-jj-mtime-clock.sh"
cat > "$C/corpus/knowledge/jj-abandoned-object-mtime-clock.md" <<'EOF'
source: S051
verified-at: 2026-10-26
recheck: none
ground: F1

census/round-32/records/jj-mtime-clock-run.txt
`RESULT arm=recent step=gc-default obj=B mtime=recent where=cruft object_present=yes`
`RESULT arm=old step=gc-default obj=B mtime=old where=absent object_present=no`
`RESULT arm=mixed step=gc-default obj=B mtime=old where=absent object_present=no`
EOF
sed -i 's#`knowledge/jj-dropped-keep-object-lifetime.md`#`knowledge/jj-dropped-keep-object-lifetime.md`, `knowledge/jj-abandoned-object-mtime-clock.md`#' "$C/corpus/README.md"
g add -A >/dev/null; g commit -qm junkc3; J=$(g rev-parse HEAD)
printf 'C3-junk(sourceless entry + typed record + cat fixture)\tc3\t%s\n' "$(c3 $J)"
