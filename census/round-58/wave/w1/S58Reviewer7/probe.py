import csv, io, json, os, pathlib, shlex, subprocess, sys, hashlib
ROOT='/home/vgpnk/Projects/shokunin/souji-shokunin'
BASE='e7f64f30324e8ddb3f2266302daa9066054cdbb3'
SCR=pathlib.Path('/fast/scratch/hyaku/souji-r58/S58Reviewer7')
OUT=pathlib.Path(ROOT+'/.ufo/waves/round-58/w1/S58Reviewer7')
OUT.mkdir(parents=True,exist_ok=True)
log=[]
def run(args, **kw):
 p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,**kw)
 log.append('$ '+shlex.join(map(str,args))+'\n'+p.stdout+'EXIT='+str(p.returncode)+'\n')
 return p
head=run(['git','-C',ROOT,'rev-parse','HEAD']).stdout.strip()
def blob(rev,path):
 p=run(['git','-C',ROOT,'show',rev+':'+path]); assert p.returncode==0; return p.stdout
counter=blob(BASE,'census/round-58/c1-counter.py'); (SCR/'counter.py').write_text(counter)
paths=['census/round-57/records/c1-matrix-v5.tsv','census/round-57/records/c1-matrix-v6.tsv']
mats=[blob(BASE,p) for p in paths]
old=blob(BASE,'SCORECARD.md'); landed=blob(head,'SCORECARD.md')
run(['git','-C',ROOT,'diff',BASE,head,'--','SCORECARD.md','census/round-58/c1-counter.py',*paths])
for rev in [BASE,head]: run([sys.executable,'-B',str(SCR/'counter.py'),'--root',ROOT,'--rev',rev])
rows=[list(csv.DictReader(io.StringIO(t),delimiter='\t')) for t in mats]
keys=[[r['fixture'] for r in rs] for rs in rows]
independent={'rows':list(map(len,rows)),'unique_fixture_ids':list(map(lambda k:len(set(k)),keys)),'same_order':keys[0]==keys[1],'exit_zero':[sum(r['exit']=='0' for r in rs) for rs in rows],'identical_by_fixture':sum(a['exit']==b['exit'] and a['findings_all']==b['findings_all'] for a,b in zip(*rows))}
notes=[line for line in landed.splitlines() if line.startswith('R58-CALIBRATION ')]
assert len(notes)==2
cases=[]
def case(name,card=landed,tables=mats): cases.append((name,card,list(tables)))
case('honest')
case('omit-carry-note',landed.replace(notes[0],''))
case('omit-exit-note',landed.replace(notes[1],''))
case('junk-only','R58-CALIBRATION carry_identical=999\nR58-CALIBRATION exit_zero=999,999\n')
case('wrong-numeric-notes',landed.replace('R58-CALIBRATION carry_identical=34','R58-CALIBRATION carry_identical=33').replace('R58-CALIBRATION exit_zero=10,8','R58-CALIBRATION exit_zero=18,18'))
case('notes-without-original-assertion','\n'.join(notes)+'\n')
case('contradictory-prose',landed+'\nThe two R58-CALIBRATION notes above are false; the original r57 assertions remain authoritative.\n')
lines=[m.splitlines(keepends=True) for m in mats]
changed=list(lines[0]); fields=changed[1].split('\t'); fields[4]='1'; changed[1]='\t'.join(fields)
case('matrix-exit-byte',tables=[''.join(changed),mats[1]])
changed=list(lines[0]); fields=changed[1].split('\t'); fields[0]='X'+fields[0][1:]; changed[1]='\t'.join(fields)
case('matrix-identity-byte',tables=[''.join(changed),mats[1]])
# Drop an already nonidentical nonzero row: counts and identical total stay unchanged.
idx=next(i for i,(a,b) in enumerate(zip(*rows),1) if a['exit']!='0' and b['exit']!='0' and (a['exit']!=b['exit'] or a['findings_all']!=b['findings_all'])) if any(a['exit']!='0' and b['exit']!='0' and (a['exit']!=b['exit'] or a['findings_all']!=b['findings_all']) for a,b in zip(*rows)) else None
# Omit the final nonzero row from only v6: zip truncation changes carry count.
case('omit-final-v6-row',tables=[mats[0],''.join(lines[1][:-1])])
# Append a duplicate nonzero row beyond zip's shorter arm: all reported metrics remain unchanged.
dup=next(line for line in lines[0][1:] if line.split('\t')[4]!='0')
case('duplicate-v5-nonzero-row',tables=[mats[0]+dup,mats[1]])
case('duplicate-notes',landed+'\n'+'\n'.join(notes)+'\n')
repo=SCR/'fixture'; repo.mkdir()
p=run(['git','-C',str(repo),'init']); assert p.returncode==0
actual=run(['git','-C',str(repo),'rev-parse','--show-toplevel']); assert actual.stdout.strip()==str(repo)
env=os.environ.copy(); env.update(GIT_AUTHOR_NAME='Scratch Fixture',GIT_AUTHOR_EMAIL='scratch@example.invalid',GIT_COMMITTER_NAME='Scratch Fixture',GIT_COMMITTER_EMAIL='scratch@example.invalid')
results=[]
for name,card,tables in cases:
 for path,text in zip(paths,tables):
  dest=repo/path; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(text)
 (repo/'SCORECARD.md').write_text(card)
 assert run(['git','-C',str(repo),'rev-parse','--show-toplevel']).stdout.strip()==str(repo)
 assert run(['git','-C',str(repo),'add','--','SCORECARD.md',*paths]).returncode==0
 assert run(['git','-C',str(repo),'rev-parse','--show-toplevel']).stdout.strip()==str(repo)
 assert run(['git','-C',str(repo),'commit','--allow-empty','-m',name],env=env).returncode==0
 rev=run(['git','-C',str(repo),'rev-parse','HEAD']).stdout.strip()
 p=run([sys.executable,'-B',str(SCR/'counter.py'),'--root',str(repo),'--rev',rev])
 results.append({'case':name,'exit':p.returncode,'output':p.stdout,'revision':rev})
(OUT/'receipts.txt').write_text('\n'.join(log))
(OUT/'results.json').write_text(json.dumps({'production_revision':head,'frozen_predicate':BASE,'counter_sha256':hashlib.sha256(counter.encode()).hexdigest(),'independent':independent,'cases':results},indent=2)+'\n')
(OUT/'probe.py').write_text((SCR/'probe.py').read_text())
print(json.dumps({'production_revision':head,'independent':independent,'cases':results},indent=2))
