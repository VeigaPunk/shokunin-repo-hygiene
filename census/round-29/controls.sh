#!/usr/bin/env bash
# r29 L1 controls: do-nothing and junk states scored with the FROZEN counters. Scratch clone only.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
B=691dd29211c53d0ef94fa072394cb9c8a69fe92e
D=$(mktemp -d /var/tmp/souji-r29-L1ctl.XXXXXX) || exit 2
git clone -q --no-local "$LANE" "$D/c" || exit 2
C="$D/c"
[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "toplevel mismatch"; exit 2; }
git -C "$C" config user.name ctl; git -C "$C" config user.email ctl@localhost
mkdir -p "$C/census/round-29" "$C/tools"
cp "$LANE/tools/souji-registry-agreement.py" "$C/tools/"; cp "$LANE/census/round-29/stale-statements.tsv" "$LANE/census/round-29/c2-counter.py" "$C/census/round-29/"
git -C "$C" add -A >/dev/null; git -C "$C" commit -q -m frozen-counters; X=$(git -C "$C" rev-parse HEAD)
c1() { python3 -B "$LANE/tools/souji-registry-agreement.py" --root "$C" --rev "$1" --list-rev "$X" 2>&1 | tail -1; }
c2() { python3 -B "$LANE/census/round-29/c2-counter.py" --root "$C" --rev "$1" 2>&1 | tail -1; }
echo -e "control\tcounter\tresult"
echo -e "C1-do-nothing(base)\tc1\t$(c1 $B)"
echo -e "C2-do-nothing(base)\tc2\t$(c2 $B)"
echo -e "C3-do-nothing(base)\tc3\tF3_entries=$(git -C "$C" grep -lE '^ground: F3' $B -- corpus/knowledge/ | wc -l) rows=$(git -C "$C" show $B:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|')"
# C1 junk-1: correction markers only (registry untouched)
git -C "$C" checkout -q --detach $B
python3 - "$C" <<'PY'
import sys
c=sys.argv[1]
tag={'LOG.md':[1758],'SCORECARD.md':[23],'corpus/lessons/round-28.md':[22,40]}
for f,ns in tag.items():
    with open(f'{c}/{f}','a') as fh:
        for n in ns: fh.write(f'\nR29-CORRECTION {f}:{n} junk marker\n')
PY
git -C "$C" add -A >/dev/null; git -C "$C" commit -q -m junk1; J1=$(git -C "$C" rev-parse HEAD)
echo -e "C1-junk1(markers only)\tc1\t$(c1 $J1)"
# C1 junk-2: markers + stale phrases edited away in place
python3 - "$C" <<'PY'
import sys
c=sys.argv[1]
for f,ph in [('LOG.md','improperly formatted'),('SCORECARD.md','malformed newline-path'),('corpus/lessons/round-28.md','improperly formatted'),('corpus/lessons/round-28.md','malformed newline-path')]:
    p=f'{c}/{f}'; t=open(p).read().replace(ph,'REDACTED'); open(p,'w').write(t)
PY
git -C "$C" add -A >/dev/null; git -C "$C" commit -q -m junk2; J2=$(git -C "$C" rev-parse HEAD)
echo -e "C1-junk2(markers+in-place edit)\tc1\t$(c1 $J2)"
# C1 junk-3: blank every used-by cell (registry made vacuously consistent forward)
git -C "$C" checkout -q --detach $B
python3 - "$C" <<'PY'
import re,sys
p=sys.argv[1]+'/corpus/SOURCES.md'; out=[]
for l in open(p):
    if re.match(r'^ {0,3}\|\s*S\d{3,}\s*\|',l):
        c=l.rstrip('\n').split('|'); c[11]=' — '; l='|'.join(c)+'\n'
    out.append(l)
open(p,'w').writelines(out)
PY
git -C "$C" add -A >/dev/null; git -C "$C" commit -q -m junk3; J3=$(git -C "$C" rev-parse HEAD)
echo -e "C1-junk3(blank used-by)\tc1\t$(c1 $J3)"
# C2 junk-1: r26 manifest keeps only verifying records (drop the 152 absent ones); symlinks unaccounted
git -C "$C" checkout -q --detach $B
python3 - "$C" <<'PY'
import subprocess,sys,re
c=sys.argv[1]; m=c+'/census/round-26/waves/manifest.sha256'
tracked=set(subprocess.run(['git','-C',c,'ls-files','-z','census/round-26/waves'],capture_output=True).stdout.decode().split('\0'))
keep=[]
for l in open(m,errors='surrogateescape'):
    mm=re.match(r'^\\?[0-9a-f]{64}  \./(.*)$',l.rstrip('\n'))
    if mm and 'census/round-26/waves/'+mm.group(1) in tracked and not l.startswith('\\'): keep.append(l)
    elif l.startswith('\\'): keep.append(l)
open(m,'w',errors='surrogateescape').writelines(keep)
PY
git -C "$C" add -A >/dev/null; git -C "$C" commit -q -m junk-c2a; K1=$(git -C "$C" rev-parse HEAD)
echo -e "C2-junk1(drop failing records)\tc2\t$(c2 $K1)"
# C2 junk-2: empty all three manifests and delete the other captured files
git -C "$C" checkout -q --detach $B
for r in 26 27 28; do : > "$C/census/round-$r/waves/manifest.sha256"; find "$C/census/round-$r/waves" -mindepth 1 ! -name manifest.sha256 -delete 2>/dev/null; done
git -C "$C" add -A >/dev/null; git -C "$C" commit -q -m junk-c2b; K2=$(git -C "$C" rev-parse HEAD)
echo -e "C2-junk2(empty manifests, files deleted)\tc2\t$(c2 $K2)"
# C3 junk: two ground:F3 entries citing existing rows only, no snapshots, no new rows
git -C "$C" checkout -q --detach $B
for n in a b; do printf 'source: S212 — junk\nverified-at: 2026-10-25\nrecheck: 90d\nground: F3 — junk\n\n# junk %s\n' $n > "$C/corpus/knowledge/junk-f3-$n.md"; done
git -C "$C" add -A >/dev/null; git -C "$C" commit -q -m junk-c3; K3=$(git -C "$C" rev-parse HEAD)
echo -e "C3-junk(2 sourceless-by-row F3 entries)\tc3\tF3_entries=$(git -C "$C" grep -lE '^ground: F3' $K3 -- corpus/knowledge/ | wc -l) rows=$(git -C "$C" show $K3:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|') c1=$(c1 $K3)"
git -C "$C" checkout -q --detach $K3
(cd "$C" && python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/junk-f3-a.md corpus/knowledge/junk-f3-b.md 2>&1 | tail -2 | tr '\n' ' '; echo)
rm -rf "$D"
