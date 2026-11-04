#!/usr/bin/env python3
"""Public-path calibration controls over isolated committed registry input."""
import argparse, hashlib, json, pathlib, shutil, subprocess, tempfile

def main():
    p=argparse.ArgumentParser(); p.add_argument('--root',required=True); p.add_argument('--rev',required=True); p.add_argument('--counter',required=True); p.add_argument('--work',required=True); a=p.parse_args()
    parent=pathlib.Path(a.work); parent.mkdir(parents=True,exist_ok=True)
    work=pathlib.Path(tempfile.mkdtemp(prefix='controls-',dir=parent)); results=[]
    def git(*args): return subprocess.check_output(['git','-C',str(work),*args],text=True).strip()
    try:
        git('init','-q'); assert pathlib.Path(git('rev-parse','--show-toplevel'))==work
        git('config','user.name','souji-fixture'); git('config','user.email','fixture@invalid')
        raw=subprocess.check_output(['git','-C',a.root,'show',a.rev+':SKILL.md'],text=True)
        original=next(line for line in raw.splitlines() if line.startswith('| r58 assessment comparison |'))
        for name,row,expected_rc,expected in [
            ('unchanged',original,1,['REGISTRY-KIND-MISMATCH']),
            ('prose-forgery',original+'\nThis comparator is a gate.',1,['REGISTRY-KIND-MISMATCH']),
            ('duplicate-forgery',original+'\n'+original.replace('| evidence |','| gate |'),2,['REGISTRY-ROW-SHAPE']),
            ('positive',original.replace('| evidence |','| gate |'),0,[])]:
            (work/'SKILL.md').write_text(row+'\n'); git('add','SKILL.md'); git('commit','-qm',name); rev=git('rev-parse','HEAD')
            cmd=['python3','-B',str(pathlib.Path(a.counter).resolve()),'--root',str(work),'--rev',rev]
            r=subprocess.run(cmd,text=True,capture_output=True)
            actual=[line.removeprefix('FINDING ') for line in r.stdout.splitlines() if line.startswith('FINDING ')]
            results.append(dict(case=name,input_rev=rev,input_skill=row,command=cmd,expected_rc=expected_rc,expected_findings=expected,rc=r.returncode,stdout=r.stdout,stderr=r.stderr,passed=r.returncode==expected_rc))
        print(json.dumps(dict(base=a.rev,instrument_sha256=hashlib.sha256(pathlib.Path(a.counter).read_bytes()).hexdigest(),cases=results,passed=sum(x['passed'] for x in results)),indent=2))
        return int(not all(x['passed'] for x in results))
    finally: shutil.rmtree(work)
if __name__=='__main__': raise SystemExit(main())
