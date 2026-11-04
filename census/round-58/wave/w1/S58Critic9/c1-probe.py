import csv, hashlib, io, json, subprocess
from pathlib import Path
ROOT='/home/vgpnk/Projects/shokunin/souji-shokunin'
OUT=Path(ROOT)/'.ufo/waves/round-58/w1/S58Critic9'
FROZEN='e7f64f30324e8ddb3f2266302daa9066054cdbb3'
CAND='dccdc469f4c2e0415e1a1dcc317364e1b4d3191e'
receipts=[]
def run(args, data=None):
 p=subprocess.run(args,input=data,capture_output=True)
 receipts.append('$ '+ ' '.join(args)+'\n'+p.stdout.decode()+p.stderr.decode()+'EXIT='+str(p.returncode)+'\n')
 return p

def blob(rev,path):
 p=run(['git','-C',ROOT,'show',rev+':'+path])
 assert p.returncode==0
 return p.stdout
counter=blob(FROZEN,'census/round-58/c1-counter.py')
results={'counter_sha256':hashlib.sha256(counter).hexdigest(),'revisions':{}}
for rev in [FROZEN,CAND]:
 tables=[list(csv.DictReader(io.StringIO(blob(rev,'census/round-57/records/c1-matrix-v'+arm+'.tsv').decode()),delimiter='\t')) for arm in ['5','6']]
 ids=[[r['fixture'] for r in t] for t in tables]
 assert ids[0]==ids[1] and len(set(ids[0]))==len(ids[0])
 identical=sum((a['exit'],a['findings_all'])==(b['exit'],b['findings_all']) for a,b in zip(*tables))
 counts=[sum(r['exit']=='0' for r in t) for t in tables]
 p=run(['python3','-B','-','--root',ROOT,'--rev',rev],counter)
 results['revisions'][rev]={'rows':[len(t) for t in tables],'identical':identical,'exit_zero':counts,'counter_exit':p.returncode,'counter_stdout':p.stdout.decode(),'counter_unchanged':blob(rev,'census/round-58/c1-counter.py')==counter}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'c1-receipts.txt').write_text('\n'.join(receipts))
(OUT/'c1-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
