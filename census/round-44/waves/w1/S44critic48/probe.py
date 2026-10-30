import pathlib, subprocess, json, hashlib, shutil
OUT=pathlib.Path(__file__).resolve().parent
SCR=pathlib.Path('/fast/scratch/hyaku/souji-r44/S44critic48')
ROOT=SCR/'fixture'
LANE=pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
FREEZE='d314fd6e85d62565344fa6c4b102f52f62297884'
BASE='55d7af6f5a22340f7a3de1c386e514ababfaa75f'
COUNTER=LANE/'census/round-44/c1-counter.py'
def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args],text=True)
assert git('rev-parse','--show-toplevel').strip()==str(ROOT)
# Only this private fixture is mutated; no lane refs/index changes.
git('checkout','--detach',FREEZE)
cmd=['python3','-B',str(COUNTER),'--root',str(ROOT),'--rev',FREEZE,'--scratch',str(SCR/'counter'),'--emit']
p=subprocess.run(cmd,capture_output=True,text=True,cwd=SCR)
(OUT/'emit.tsv').write_text(p.stdout)
(OUT/'emit.stderr').write_text(p.stderr)
assert p.returncode==0
rows=[]
for ln in p.stdout.splitlines():
    fs=ln.split('\t'); rows.append((fs[0],dict(x.split('=',1) for x in fs[1:])))
assert len(rows)==66
receipts=[]
for kind in ('natural','wrong-derived','swapped'):
    lines=[]
    for cid,orig in rows:
        f=orig.copy()
        if kind=='wrong-derived' and cid=='R44-09': f['derived']='UNHELD'
        if kind=='swapped': f['class'],f['stale']=f['stale'],f['class']
        lines.append('CORRECTION-R44 id='+cid+' file=SCORECARD.md '+' '.join(k+'='+f[k] for k in ('line','class','stale','derived'))+' rev='+BASE+' scope=historical-registration')
    lesson='\n'.join(lines)+'\n'
    (OUT/(kind+'.md')).write_text(lesson)
    (ROOT/'corpus/lessons/round-44.md').write_text(lesson)
    assert git('rev-parse','--show-toplevel').strip()==str(ROOT)
    git('add','corpus/lessons/round-44.md')
    git('-c','user.name=S44critic48','-c','user.email=critic48@example.invalid','-c','core.hooksPath=/dev/null','commit','-m','isolated c1 '+kind)
    rev=git('rev-parse','HEAD').strip()
    cmd=['python3','-B',str(COUNTER),'--root',str(ROOT),'--rev',rev,'--scratch',str(SCR/'counter')]
    p=subprocess.run(cmd,capture_output=True,text=True,cwd=SCR)
    (OUT/(kind+'.stdout')).write_text(p.stdout)
    (OUT/(kind+'.stderr')).write_text(p.stderr)
    r={'fixture':kind,'rev':rev,'command':cmd,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    receipts.append(r); print(json.dumps(r))
# Exact frozen historical bytes, not live worktree evidence.
for name,path in [('q76-round42','corpus/lessons/round-42.md'),('base-scorecard','SCORECARD.md')]:
    (OUT/(name+'.txt')).write_text(git('show',BASE+':'+path))
(OUT/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
(OUT/'pins.json').write_text(json.dumps({str(p.relative_to(LANE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [COUNTER,LANE/'census/round-44/c1-population.tsv']},indent=2)+'\n')
print('Artifacts preserved:',OUT)
