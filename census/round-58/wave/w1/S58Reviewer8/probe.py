#!/usr/bin/env python3
import argparse, concurrent.futures, hashlib, json, os, pathlib, shlex, subprocess, sys, zlib
P=pathlib.Path
ap=argparse.ArgumentParser(); ap.add_argument('gate'); ap.add_argument('label'); ns=ap.parse_args()
base=P('/fast/scratch/hyaku/souji-r58/S58Reviewer8'); repo=base/'fixture'; repo.mkdir(exist_ok=True)
logs=[]
def cmd(args, timeout=20):
    try:
        p=subprocess.run(args,cwd=base,capture_output=True,text=True,timeout=timeout,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_NOSYSTEM':'1','GIT_NO_REPLACE_OBJECTS':'1','GIT_OPTIONAL_LOCKS':'0'})
        return {'command':shlex.join(args),'stdout':p.stdout,'stderr':p.stderr,'EXIT':p.returncode}
    except subprocess.TimeoutExpired as e:
        return {'command':shlex.join(args),'stdout':str(e.stdout or ''),'stderr':str(e.stderr or ''),'EXIT':'TIMEOUT'}
def git(*args):
    if args[0] != 'init':
        check=cmd(['git','-C',str(repo),'rev-parse','--show-toplevel']); logs.append(check); assert check['stdout'].strip()==str(repo)
    r=cmd(['git','-C',str(repo),*args]); logs.append(r); assert r['EXIT']==0,r
    return r['stdout'].strip()
if not (repo/'.git').exists():
    git('init','-q','-b','main'); git('config','user.name','fixture'); git('config','user.email','fixture@example.invalid')
    (repo/'seed').write_text('fixture\n'); git('add','seed'); git('commit','-q','-m','fixture')
rev=git('rev-parse','HEAD'); body=f'rev={rev}\nEXIT=0\n'; (repo/'receipts').mkdir(exist_ok=True); (repo/'receipts'/'ok').write_text(body)
(base/'outside').mkdir(exist_ok=True); (base/'outside'/'ok').write_text(body)
for name,target in [('parent',base/'outside'),('inside',repo/'receipts'),('final',repo/'receipts'/'ok')]:
    if not (repo/name).is_symlink(): (repo/name).symlink_to(target)
if not (repo/'fifo').exists(): os.mkfifo(repo/'fifo')
(repo/'receipts'/'conflict-a').write_text(body+f'rev={"0"*40}\n')
(repo/'receipts'/'conflict-b').write_text(f'rev={"0"*40}\n'+body)
(repo/'receipts'/'duplicate').write_text(body+f'rev={rev}\n')
cases={'honest':'receipts/ok','absolute':str(repo/'receipts'/'ok'),'traversal':'../outside/ok','normalized-traversal':'receipts/../receipts/ok','dot-normalized':'./receipts/ok','parent-symlink':'parent/ok','inside-parent-symlink':'inside/ok','final-symlink':'final','fifo':'fifo','conflict-valid-first':'receipts/conflict-a','conflict-invalid-first':'receipts/conflict-b','duplicate-identical':'receipts/duplicate'}
assert git('rev-parse','--show-toplevel') == str(repo)
def object_bytes(kind, payload):
    raw=kind.encode()+b' '+str(len(payload)).encode()+b'\0'+payload
    oid=hashlib.sha1(raw).hexdigest(); p=repo/'.git/objects'/oid[:2]/oid[2:]; p.parent.mkdir(exist_ok=True); p.write_bytes(zlib.compress(raw))
    return oid
tree=git('rev-parse','HEAD^{tree}')
def isolated_commit(label):
    payload=f'tree {tree}\nauthor fixture <fixture@example.invalid> 1000000000 +0000\ncommitter fixture <fixture@example.invalid> 1000000000 +0000\n\n{label}\n'.encode()
    return object_bytes('commit',payload)
tag_commit=isolated_commit('tag reachable only'); keep_commit=isolated_commit('keep only'); remote_commit=isolated_commit('remote only')
tag=object_bytes('tag',f'object {tag_commit}\ntype commit\ntag annotated\ntagger fixture <fixture@example.invalid> 1000000000 +0000\n\nannotated fixture\n'.encode())
for ref,oid in [('refs/tags/annotated',tag),('refs/jj/keep/fixture',keep_commit),('refs/remotes/fixture/main',remote_commit)]:
    p=repo/'.git'/ref; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(oid+'\n')
for name,oid in [('tag-object',tag),('tag-commit',tag_commit),('keep-only',keep_commit),('remote-only',remote_commit)]:
    (repo/'receipts'/name).write_text(f'rev={oid}\nEXIT=0\n'); cases[name]='receipts/'+name
logs.append({'fixture_note':'Deterministic loose objects and refs written directly only inside asserted own fixture; no tag/update-ref/reset/git plumbing mutation command used.','tag':tag,'tag_commit':tag_commit,'keep':keep_commit,'remote':remote_commit})
def run(item):
    case,rel=item; mf=base/(case+'.tsv'); mf.write_text('receipt\tinstrument\n'+rel+'\t-\n')
    r=cmd([sys.executable,'-B',str(P(ns.gate).resolve()),'--root',str(repo),'--manifest',str(mf)],10); r['case']=case; return r
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(run,cases.items()))
prod=P('/home/vgpnk/Projects/shokunin/souji-shokunin')
r=cmd([sys.executable,'-B',str(P(ns.gate).resolve()),'--root',str(prod),'--manifest',str(prod/'census/round-57/manifests/after.tsv')],30);r['case']='three-preserved-real'; results.append(r)
result={'axes':['refusal correctness','honest receipt preservation','bounded claim fidelity'],'gate':str(P(ns.gate).resolve()),'sha256':hashlib.sha256(P(ns.gate).read_bytes()).hexdigest(),'fixture_commands':logs,'results':results}
(base/(ns.label+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
