#!/usr/bin/env bash
# r29 composite-cheat control scored with the AMENDED instruments (scratch clone only). The cheat reaches every FROZEN
# v1 counter with no claimed work (Reviewer44 finding 1); the amended v2/A4 instruments must each reject it.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
PRE=b8cb4b31ce80e2e3314b88e85d40ea9873180804
D=$(mktemp -d /var/tmp/souji-r29-L1ctl2.XXXXXX) || exit 2
git clone -q --no-local "$LANE" "$D/c" || exit 2
C="$D/c"
[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "toplevel mismatch"; exit 2; }
git -C "$C" config user.name ctl; git -C "$C" config user.email ctl@localhost
git -C "$C" checkout -q --detach $PRE
python3 - "$C" <<'PY'
import os,re,subprocess,sys
c=sys.argv[1]
# C1 cheat: hide citation lines below the heading, 4-space-indent S215, marker-only corrections
for f in ['corpus/knowledge/quarantine-same-filesystem-rename.md','corpus/knowledge/process-residue-observations.md','corpus/knowledge/quarantine-origin-record-fields-r24.md']:
    p=f'{c}/{f}'; L=open(p).read().split('\n'); src=[l for l in L if re.match(r'^source:',l)]
    rest=[l for l in L if not re.match(r'^source:',l)]
    i=next(k for k,l in enumerate(rest) if l.startswith('# '))
    open(p,'w').write('\n'.join(rest[:i+1]+['']+src+rest[i+1:]))
p=f'{c}/corpus/SOURCES.md'; L=open(p).read().split('\n')
L=[('    '+l if l.startswith('| S215 ') else l) for l in L]; open(p,'w').write('\n'.join(L))
for f,n in {'LOG.md':[1758],'SCORECARD.md':[23],'corpus/lessons/round-28.md':[22,40]}.items():
    with open(f'{c}/{f}','a') as fh:
        for k in n: fh.write(f'\nR29-CORRECTION {f}:{k} marker only\n')
# C2 cheat: drop the 152 failing records and delete the 14 symlinks, add a one-record r29 manifest
man=f'{c}/census/round-26/waves/manifest.sha256'; tracked=set(subprocess.run(['git','-C',c,'ls-files','-z','census/round-26/waves'],capture_output=True).stdout.decode().split('\0'))
keep=[]
for l in open(man,errors='surrogateescape'):
    m=re.match(r'^\\?[0-9a-f]{64}  \./(.*)$',l.rstrip('\n'))
    if l.startswith('\\') or (m and 'census/round-26/waves/'+m.group(1) in tracked): keep.append(l)
open(man,'w',errors='surrogateescape').writelines(keep)
for t in tracked:
    if t and os.path.islink(f'{c}/{t}'): os.remove(f'{c}/{t}')
os.makedirs(f'{c}/census/round-29/waves',exist_ok=True); open(f'{c}/census/round-29/waves/x.txt','w').write('x\n')
import hashlib; open(f'{c}/census/round-29/waves/manifest.sha256','w').write(hashlib.sha256(b'x\n').hexdigest()+'  ./x.txt\n')
# C3 cheat: two F3 entries, four fabricated rows, tiny snapshots, tiny quotes, fabricated slice
rows=''.join(f'| S21{n} | fake{n} — https://fake{n}.example/x | docs | A | s | anchor | teaches | mined | 2026-10-25 | on-release | corpus/knowledge/junk-f3-{"a" if n<8 else "b"}.md |\n' for n in (6,7,8,9))
s=open(f'{c}/corpus/SOURCES.md').read().split('\n'); i=[k for k,l in enumerate(s) if l.startswith('| S215 ') or l.startswith('    | S215 ')][0]
s[i+1:i+1]=rows.rstrip('\n').split('\n'); open(f'{c}/corpus/SOURCES.md','w').write('\n'.join(s))
os.makedirs(f'{c}/census/round-29/sources',exist_ok=True)
for n,(sid) in (('a',('S216','S217')),('b',('S218','S219'))):
    open(f'{c}/corpus/knowledge/junk-f3-{n}.md','w').write(f'source: {sid[0]}\nsource: {sid[1]}\nverified-at: 2026-10-25\nrecheck: 90d\nground: F3 — junk\n\n# junk\n\n## Gate\nurl: https://fake.example/x\nopened: 2026-10-25\nsnapshot: census/round-29/sources/t{n}.txt\n- "ab cd" — § line 1\n- ADMIT: junk — reason: x\n- REJECT: junk — reason: x\n')
    open(f'{c}/census/round-29/sources/t{n}.txt','w').write('ab cd\n')
r=open(f'{c}/corpus/README.md').read().replace('| F3 duplicate verdicts | frontier, entry held | `knowledge/dupe-finders-detect-then-act.md` |','| F3 duplicate verdicts | frontier, entries held | `knowledge/dupe-finders-detect-then-act.md`, `knowledge/junk-f3-a.md`, `knowledge/junk-f3-b.md` |'); open(f'{c}/corpus/README.md','w').write(r)
PY
git -C "$C" add -A >/dev/null; git -C "$C" commit -q -m composite-cheat; X=$(git -C "$C" rev-parse HEAD)
echo -e "instrument\tfrozen-v1\tamended"
v1="$D/v1.py"; git -C "$LANE" show $PRE:tools/souji-registry-agreement.py > "$v1"
echo -e "C1\t$(python3 -B $v1 --root $C --rev $X --list-rev $PRE | tail -1)\t$(python3 -B $LANE/tools/souji-registry-agreement.py --root $C --rev $X --list-rev $PRE | tail -1)"
echo -e "C2\t$(python3 -B $LANE/census/round-29/c2-counter.py --root $C --rev $X | tail -1)\t$(python3 -B $LANE/census/round-29/c2-counter-v2.py --root $C --rev $X --base-rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e --require-rounds 26,27,28,29 | tail -1)"
echo -e "C3\tF3_entries=$(git -C $C grep -lE '^ground: F3' $X -- corpus/knowledge/ | wc -l) rows=$(git -C $C show $X:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|')\t$(python3 -B $LANE/census/round-29/c3-integrity.py --root $C --rev $X | tail -1)"
rm -rf "$D"
