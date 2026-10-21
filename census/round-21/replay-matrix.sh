#!/usr/bin/env bash
set -euo pipefail
exec python3 -B - "$@" <<'PY'
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
p = argparse.ArgumentParser(description='Three-source replay matrix; source repos never modified')
p.add_argument('--runner', required=True)
p.add_argument('--rev', required=True)
p.add_argument('--lane', required=True)
p.add_argument('--work', required=True)
p.add_argument('--expect-replayed', type=int, default=3)
a = p.parse_args()
work = Path(a.work).resolve()
work.mkdir(exist_ok=False)
env = {'PATH':'/usr/bin:/bin', 'LC_ALL':'C', 'PYTHONDONTWRITEBYTECODE':'1',
       'GIT_CONFIG_NOSYSTEM':'1', 'GIT_CONFIG_GLOBAL':'/dev/null', 'GIT_OPTIONAL_LOCKS':'0'}
def git(root, *args):
    r = subprocess.run(['git','-C',str(root),*args],env=env,capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode())
    return r.stdout.decode().strip()
def clone(*args):
    subprocess.run(['git','-c','core.hooksPath=/dev/null','clone','--quiet','--no-local',*args],env=env,check=True)
def state(root):
    bare = git(root, 'rev-parse','--is-bare-repository') == 'true'
    head = git(root, 'rev-parse','HEAD')
    status = '' if bare else git(root,'status','--porcelain','--untracked-files=no')
    refs = git(root,'for-each-ref','--format=%(refname) %(objectname)')
    return {'head':head,'status':status,'refs_sha256':hashlib.sha256(refs.encode()).hexdigest()}
clone(a.lane,str(work/'s1'))
# Intentionally mismatch the caller HEAD and measured revision.
other = git(work/'s1','rev-parse',a.rev+'^')
subprocess.run(['git','-C',str(work/'s1'),'-c','core.hooksPath=/dev/null','checkout','--quiet','--detach',other],env=env,check=True)
clone('--bare',a.lane,str(work/'s2.git'))
records = []
signatures = []
for name, root in [('S1',work/'s1'),('S2',work/'s2.git'),('S3',Path(a.lane).resolve())]:
    before = state(root)
    output = work / ('out-'+name+'.json')
    command = ['python3','-B',str(Path(a.runner).resolve()),'--root',str(root),'--rev',a.rev,'--output',str(output)]
    result = subprocess.run(command,env=env,capture_output=True)
    after = state(root)
    record = {'scenario':name,'command':command,'returncode':result.returncode,'source_before':before,
              'source_after':after,'source_sample_unchanged':before==after,'stdout':result.stdout.decode(),
              'stderr':result.stderr.decode(),'output':str(output)}
    matched, count = False, 0
    if output.exists():
        payload = json.loads(output.read_text())
        matched, count = payload.get('all_matched',False), payload.get('matched_command_count',0)
        record['all_matched'], record['matched_command_count'] = matched, count
        signature = [(r['name'],r['returncode'],r['observed_summary'],r['matched_counts'],r['matched']) for r in payload['commands']]
        signatures.append(signature)
    record['replayed'] = result.returncode == 0 and matched and before==after
    records.append(record)
    print(f'SCENARIO\t{name}\texit={result.returncode}\tmatched={count}/18\tsrc_sample_unchanged={"yes" if before==after else "no"}')
    if result.stderr: print(result.stderr.decode().rstrip())
replayed = sum(r['replayed'] for r in records)
equal = len(signatures)==3 and signatures[0]==signatures[1]==signatures[2]
summary = {'scenarios':3,'replayed':replayed,'summaries_equal':equal,'records':records}
(work/'matrix.json').write_text(json.dumps(summary,indent=2)+'\n')
print(f'MATRIX\tscenarios=3\treplayed={replayed}\tsummaries_equal={equal}')
raise SystemExit(0 if replayed==a.expect_replayed and (a.expect_replayed==0 or equal) else 1)
PY
