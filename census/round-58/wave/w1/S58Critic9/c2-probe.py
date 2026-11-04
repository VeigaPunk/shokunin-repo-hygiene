import hashlib,json,runpy,subprocess,sys
from pathlib import Path
ROOT=Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
OUT=ROOT/'.ufo/waves/round-58/w1/S58Critic9'
WORK=Path('/fast/scratch/hyaku/souji-r58/S58Critic9')
DRIVER=ROOT/'.ufo/waves/round-58/w1/S58Executor4/c2-acceptance.py'
assert hashlib.sha256(DRIVER.read_bytes()).hexdigest()=='55b5e063fa57a02d7fcf186c9d8e9b719b0ecb76b08001ad0988ad76aa3fc82e'
d=runpy.run_path(str(DRIVER))
WORK.mkdir(parents=True,exist_ok=True)
env=d['environment'](WORK)
report={'command':sys.argv,'driver_sha256':hashlib.sha256(DRIVER.read_bytes()).hexdigest(),'fixture_commands':[],'arms':{}}
base,cases,details=d['fixture'](WORK,env,report['fixture_commands'])
report['fixture']=details
for i,(receipt,instrument) in enumerate(d['REAL_ROWS']):
 mf=base/('real-%d.tsv'%i)
 mf.write_text('receipt\tinstrument\n%s\t%s\n'%(receipt,instrument))
 cases.append(('real-%d'%(i+1),ROOT,mf,0,[]))
report['real_sha256']={r:hashlib.sha256((ROOT/r).read_bytes()).hexdigest() for r,_ in d['REAL_ROWS']}
frozen=subprocess.run(['git','-C',str(ROOT),'show','e7f64f30324e8ddb3f2266302daa9066054cdbb3:census/round-57/c2-counter.py'],capture_output=True)
assert frozen.returncode==0
old=base/'frozen-r57.py';old.write_bytes(frozen.stdout)
for label,tool in [('r57-control',old),('changed',Path(sys.argv[1]))]:
 before=hashlib.sha256(tool.read_bytes()).hexdigest()
 scored=d['score'](tool,cases,env,base)
 after=hashlib.sha256(tool.read_bytes()).hexdigest()
 assert before==after
 report['arms'][label]={'tool':str(tool),'sha256_before':before,'sha256_after':after,**scored}
report['driver_sha256_after']=hashlib.sha256(DRIVER.read_bytes()).hexdigest()
(OUT/'c2-results.json').write_text(json.dumps(report,indent=2)+'\n')
for label,arm in report['arms'].items():
 print(label,arm['sha256_before'],'target_met='+str(arm['passed']))
 for row in arm['cases']:
  print(row['case'],'EXIT='+str(row['EXIT']),'findings='+str(row['findings']),'expected='+str(row['expected_findings']))
print('Evidence:',OUT/'c2-results.json')
