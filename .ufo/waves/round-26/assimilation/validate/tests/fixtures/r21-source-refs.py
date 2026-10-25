#!/usr/bin/env python3
"""Replay from a remote-ref-only source; never promote a jj-only source."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--runner', required=True)
p.add_argument('--root', required=True)
p.add_argument('--rev', required=True)
p.add_argument('--work', required=True)
p.add_argument('--keep-only', action='store_true')
a = p.parse_args()
if not re.fullmatch('[0-9a-f]{40}', a.rev): p.error('--rev must be full40')
work = Path(a.work).resolve()
work.mkdir(exist_ok=False)
source = work / 'source.git'
env = {'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1',
       'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_OPTIONAL_LOCKS':'0'}
subprocess.run(['git','init','--quiet','--bare',str(source)],env=env,check=True)
ref = 'refs/jj/keep/synthetic' if a.keep_only else 'refs/remotes/synthetic/main'
subprocess.run(['git','-C',str(source),'-c','core.hooksPath=/dev/null','fetch','--quiet','--no-tags','--',
                str(Path(a.root).resolve()),a.rev+':'+ref],env=env,check=True)
output = work / 'result.json'
command = ['python3','-B',str(Path(a.runner).resolve()),'--root',str(source),'--rev',a.rev,'--output',str(output)]
result = subprocess.run(command,env=env,capture_output=True,text=True)
payload = json.loads(output.read_text()) if output.exists() else None
if a.keep_only:
    ok = result.returncode == 2 and payload is None
else:
    ok = (result.returncode == 0 and payload is not None and payload['all_matched']
          and payload['matched_command_count'] == 18 and payload['source_state_before']['head'] is None)
record = {'argv':command,'source_ref':ref,'runner_exit':result.returncode,'stdout':result.stdout,
          'stderr':result.stderr,'output_created':output.exists(),'pass':bool(ok),
          'matched':payload.get('matched_command_count') if payload else None}
(work/'fixture.json').write_text(json.dumps(record,indent=2)+'\n')
print('CASE\t%s\t%s\trunner_exit=%d\tmatched=%s' % ('pass' if ok else 'FAIL',ref,result.returncode,record['matched']))
print('SUMMARY\ttotal=1\tpass=%d\tfail=%d' % (int(ok),int(not ok)))
raise SystemExit(0 if ok else 1)
