#!/usr/bin/env python3
"""Verify the filed R44 register against its declared historical referents.
This repairs measurement, not historical facts. No new correction credit.
Exit 0 exact complete agreement, 1 findings, 2 unavailable/malformed input.
--register-file selects a caller-owned discrimination fixture, never claim evidence.
"""
import argparse
import collections
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

BASE = '55d7af6f5a22340f7a3de1c386e514ababfaa75f'
POP = 'census/round-44/c1-population.tsv'
POP_SHA = '422875449468ae146ef029a4622d8f521f05f570a9b79f90286be03b7b0c1e2c'
REGISTER = 'corpus/lessons/round-44.md'

def git(root, *args):
    e = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL':'C',
         'GIT_CONFIG_NOSYSTEM':'1', 'GIT_CONFIG_GLOBAL':os.devnull,
         'GIT_CONFIG_SYSTEM':os.devnull, 'GIT_NO_REPLACE_OBJECTS':'1',
         'GIT_OPTIONAL_LOCKS':'0', 'GIT_NO_LAZY_FETCH':'1'}
    p = subprocess.run(['git','-C',str(root),*args], capture_output=True, env=e, timeout=60)
    if p.returncode:
        raise ValueError('git input unavailable')
    return p.stdout

def verify(root, rev, register, scratch):
    raw = git(root,'show',rev+':'+POP)
    if hashlib.sha256(raw).hexdigest() != POP_SHA:
        raise ValueError('population digest')
    rows = [x.split('\t') for x in raw.decode().splitlines()[1:]]
    if len(rows)!=70 or any(len(x)!=4 for x in rows):
        raise ValueError('population shape')
    keys = {(int(n),t,c) for n,t,c,_ in rows}
    source = git(root,'show',BASE+':tools/souji-declared-evidence.py')
    with tempfile.TemporaryDirectory(dir=scratch, prefix='r45-instrument-') as td:
        tool=Path(td)/'instrument.py'; tool.write_bytes(source)
        p=subprocess.run([sys.executable,'-B',str(tool),'--root',str(root),'--rev',BASE,
                          '--file','SCORECARD.md','--format','tsv'],capture_output=True,
                         env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'TMPDIR':td},timeout=120)
        if p.returncode not in (0,1):
            raise ValueError('derivation instrument unavailable')
    facts={}
    for line in p.stdout.decode().splitlines():
        f=line.split('\t')
        if len(f)>=5 and f[3].startswith('mismatch:'):
            facts[(int(f[0]),f[1],f[3])]=f[4]
    if set(facts)!=keys:
        raise ValueError('population differs from historical instrument')
    files=git(root,'ls-tree','-rz','--name-only',BASE).decode().split('\0')[:-1]
    sc=git(root,'show',BASE+':SCORECARD.md').decode().splitlines()
    expected={}
    for n,t,c in keys:
        if c=='mismatch:path-absent':
            candidates=sorted(x for x in files if (x.endswith(t) if '/' in t else x.rsplit('/',1)[-1]==t))
            v=candidates[0] if len(candidates)==1 else ('multi:'+';'.join(candidates) if candidates else 'UNHELD')
        elif c=='mismatch:rev-unresolved':
            ds=[x for x in re.findall(r'[0-9a-f]{64}',sc[n-1]) if x.startswith(t)]
            v='sha256prefix:'+ds[0] if ds else 'UNRESOLVED'
        elif c=='mismatch:digest':
            m=re.fullmatch(r'sha256 is ([0-9a-f]{64})',facts[(n,t,c)])
            if not m: raise ValueError('digest derivation')
            v='sha256:'+m[1]
        else: raise ValueError('unknown class')
        expected[(n,t,c)]=v
    found=collections.defaultdict(list); ids=set(); junk=fenced=duplicate=retracted=0
    fence=None
    for line in register.splitlines():
        fm=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',line)
        if fm:
            run=fm[1]
            if fence is None: fence=(run[0],len(run))
            elif run[0]==fence[0] and len(run)>=fence[1] and not fm[2].strip(): fence=None
            continue
        if line.startswith('RETRACTED-R44 '): retracted+=1; continue
        if not line.lstrip().startswith('CORRECTION-R44 '): continue
        if fence or line[:1].isspace(): fenced+=1; continue
        fs=line.split(); fields={}
        for item in fs[1:]:
            k,sep,v=item.partition('=')
            if not sep or k in fields: junk+=1; break
            fields[k]=v
        else:
            required={'id','file','line','class','stale','derived','rev','scope'}
            if set(fields)!=required or fields['file']!='SCORECARD.md' or fields['rev']!=BASE or not fields['scope'] or not re.fullmatch(r'R44-\d{2,}',fields['id']) or not fields['line'].isdigit():
                junk+=1; continue
            if fields['id'] in ids: duplicate+=1
            ids.add(fields['id'])
            key=(int(fields['line']),fields['stale'],fields['class'])
            if key not in keys: junk+=1; continue
            found[key].append(fields['derived'])
    missing=sum(k not in found for k in keys)
    duplicate+=sum(len(v)-1 for v in found.values())
    mismatches=sum(any(v!=expected[k] for v in vs) for k,vs in found.items())
    matched=sum(len(found.get(k,[]))==1 and found[k][0]==expected[k] for k in keys)
    print('SUMMARY population=70 unique=66 registered=%d missing=%d derived_mismatches=%d junk=%d fenced=%d duplicate=%d retracted=%d historical_credit=0' %
          (matched,missing,mismatches,junk,fenced,duplicate,retracted))
    return int(not (matched==66 and missing==mismatches==junk==fenced==duplicate==retracted==0))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',required=True); ap.add_argument('--rev',required=True)
    ap.add_argument('--scratch',required=True); ap.add_argument('--register-file')
    ns=ap.parse_args()
    try:
        if not re.fullmatch('[0-9a-f]{40}',ns.rev): raise ValueError('full revision required')
        root=Path(ns.root).resolve(); scratch=Path(ns.scratch).resolve()
        if not scratch.is_dir() or root==scratch or root in scratch.parents:
            raise ValueError('external scratch directory required')
        git(root,'rev-parse','--verify',ns.rev+'^{commit}')
        text=Path(ns.register_file).read_text() if ns.register_file else git(root,'show',ns.rev+':'+REGISTER).decode()
        return verify(root,ns.rev,text,str(scratch))
    except (OSError,ValueError,subprocess.SubprocessError,UnicodeError) as ex:
        print('REFUSAL '+str(ex),file=sys.stderr); return 2

if __name__=='__main__': sys.exit(main())
