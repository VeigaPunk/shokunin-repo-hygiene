#!/usr/bin/env python3
"""R45 external fixture: honest register and single-property corruptions.
Caller supplies external --scratch. No repository mutations or fixture commits.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

ap=argparse.ArgumentParser()
ap.add_argument('--root',required=True)
ap.add_argument('--rev',required=True)
ap.add_argument('--scratch',required=True)
ap.add_argument('--tool')
a=ap.parse_args()
root=Path(a.root).resolve(); scratch=Path(a.scratch).resolve()
if not scratch.is_dir() or scratch==root or root in scratch.parents:
    sys.exit('external scratch directory required')
tool=Path(a.tool).resolve() if a.tool else root/'census/round-45/c1-counter.py'
reg=subprocess.check_output(['git','-C',str(root),'show',a.rev+':corpus/lessons/round-44.md']).decode()
lines=reg.splitlines(); correction=next(x for x in lines if x.startswith('CORRECTION-R44 '))
wrong=reg.replace('derived=UNRESOLVED','derived=FALSE-TOKEN',1)
cases=[('honest',None,0,'registered=66'),('wrong-derived',wrong,1,'derived_mismatches=1'),
       ('absent','# empty\n',1,'missing=66'),
       ('missing',reg.replace(correction+'\n','',1),1,'missing=1'),
       ('duplicate',reg+'\n'+correction+'\n',1,'duplicate=2'),
       ('fenced','```\n'+reg+'\n```\n',1,'fenced=66'),
       ('tilde-fenced','~~~~\n'+reg+'\n~~~~\n',1,'fenced=66'),
       ('indented','\n'.join(' '+x if x.startswith('CORRECTION-R44 ') else x for x in lines),1,'fenced=66'),
       ('retracted',reg+'\nRETRACTED-R44 id=R44-01\n',1,'retracted=1'),
       ('wrong-rev',reg.replace('rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f','rev=BAD',1),1,'junk=1'),
       ('wrong-file',reg.replace('file=SCORECARD.md','file=OTHER.md',1),1,'junk=1'),
       ('unknown-field',reg.replace(correction,correction+' unexpected=yes',1),1,'junk=1')]
passed=0
with tempfile.TemporaryDirectory(dir=scratch,prefix='r45-fixture-') as td:
    for name,text,want,token in cases:
        cmd=[sys.executable,'-B',str(tool),'--root',str(root),'--rev',a.rev,'--scratch',td]
        if text is not None:
            p=Path(td)/'register.txt'; p.write_text(text); cmd+=['--register-file',str(p)]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
        ok=result.returncode==want and token in result.stdout and not result.stderr
        passed+=ok
        print('CASE '+name+' '+('PASS' if ok else 'FAIL')+' rc='+str(result.returncode)+' '+result.stdout.strip())
print('SUMMARY cases=%d pass=%d fail=%d'%(len(cases),passed,len(cases)-passed))
sys.exit(0 if passed==len(cases) else 1)
