import hashlib,json,os,pathlib,shutil,subprocess,textwrap
L=pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin'); P=L/'.ufo/waves/round-43/w1/R43critic01'; S=pathlib.Path('/fast/scratch/hyaku/souji-r43/R43critic01'); F='f8c805dbfa7f45814cf9a7270fa8bbffb41a8373'
S.mkdir(parents=True,exist_ok=True); E=dict(os.environ,TMPDIR=str(S),PYTHONDONTWRITEBYTECODE='1')
def show(rev,p): return subprocess.check_output(['git','-C',str(L),'show',rev+':'+p],env=E)
try:
    master=subprocess.check_output(['git','-C',str(L),'rev-parse','refs/heads/master'],env=E,text=True).strip()
    out={'master_at_probe':master,'declared_master':'13de0e84b45efd1113f077d58fc1e89bc586a013','frozen':F,'hashes':{}}
    for p in ['census/round-43/c1-counter.py','census/round-43/c1-required.tsv','census/round-43/score-candidate.sh','census/round-43/c2-counter.py','census/round-43/c2-cases.tsv','census/round-43/c3-counter.py','census/round-43/c3-survivors.tsv','tools/souji-worktree-drift.py']:
        out['hashes'][p]={r:hashlib.sha256(show(r,p)).hexdigest() for r in [F,master]}
    src=show(F,'census/round-43/c2-counter.py').decode()
    block=textwrap.dedent(src[src.index('    mem_lines = ['):src.index('    with open(os.path.join(work, "memorizer.py")')])
    prereg=S/'prereg.txt'; prereg.write_text('# prereg\nRound: 42\n')
    key=hashlib.sha256(prereg.read_bytes()).hexdigest()
    ns={'answers':{key:(1,['FINDING C1 KEY-DUPLICATE memorized'])}}
    exec(block,ns); mem=S/'memorizer.py'; mem.write_bytes(ns['mem_b']); (P/'c2-memorizer-extracted.py').write_bytes(ns['mem_b'])
    cmd=['python3','-B',str(mem),'--root',str(S),'--prereg',str(prereg),'--rev','0'*40]
    p=subprocess.run(cmd,env=E,cwd=S,capture_output=True,text=True)
    out['memorizer']={'command':cmd,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'expected_visible_answer':'FINDING C1 KEY-DUPLICATE memorized; exit 1'}
    (P/'control-probe.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
finally: shutil.rmtree(S,ignore_errors=True)
