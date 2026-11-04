import sys, os, json, importlib.util, pathlib, subprocess, signal, hashlib
P=pathlib.Path
base=P('/fast/scratch/hyaku/souji-r58/S58Sentinel11')
source=P(sys.argv[1]); label=sys.argv[2]
spec=importlib.util.spec_from_file_location('gate', source); gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
root=base/label/'root'; root.mkdir(parents=True,exist_ok=True)
outside=root.parent/'outside'; outside.mkdir(exist_ok=True)
(outside/'synthetic.txt').write_text('synthetic-data-only\nEXIT=0\n')
(root/'inside.txt').write_text('synthetic-data-only\nEXIT=0\n')
(root/'escape').symlink_to(outside, target_is_directory=True)
(root/'leaf.txt').symlink_to(outside/'synthetic.txt')
os.mkfifo(root/'fifo')
(root/'directory').mkdir()
read_events=[]
original=P.read_bytes
def observed(self):
    read_events.append(str(self))
    return original(self)
P.read_bytes=observed
cases={'absolute':str(outside/'synthetic.txt'),'traversal':'../outside/synthetic.txt','intermediate-symlink':'escape/synthetic.txt','leaf-symlink':'leaf.txt','fifo':'fifo','directory':'directory','ordinary':'inside.txt'}
for name,rel in cases.items():
    read_events.clear()
    try: result=gate.check_receipt(root if label == 'frozen-r57' else str(root),rel,'-')
    except Exception as exc: result={'exception':type(exc).__name__,'detail':str(exc)}
    print(json.dumps({'case':name,'findings':result,'read_bytes_calls':list(read_events)},sort_keys=True),flush=True)
P.read_bytes=original
trace=base/label/'git-trace-must-not-exist'
os.environ['GIT_TRACE']=str(trace)
os.environ['GIT_CONFIG_COUNT']='1';os.environ['GIT_CONFIG_KEY_0']='core.hooksPath';os.environ['GIT_CONFIG_VALUE_0']=str(outside)
env=gate.git_env()
print(json.dumps({'case':'git-env','forwarded_write_env':sorted(k for k in env if k in {'GIT_TRACE','GIT_CONFIG_COUNT','GIT_CONFIG_KEY_0','GIT_CONFIG_VALUE_0','GIT_DIR','GIT_WORK_TREE'}),'optional_locks':env.get('GIT_OPTIONAL_LOCKS'),'lazy_fetch':env.get('GIT_NO_LAZY_FETCH')}),flush=True)
p=gate.git(root,'--version')
print(json.dumps({'case':'git-readonly','stdout':p.stdout.decode(),'stderr':p.stderr.decode(),'EXIT':p.returncode,'trace_created':trace.exists()}),flush=True)
print(json.dumps({'case':'bytecode','dont_write_bytecode':sys.dont_write_bytecode,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'own_pyc':list(map(str,base.rglob('*.pyc')))}),flush=True)
