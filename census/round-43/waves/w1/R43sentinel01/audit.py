import contextlib, hashlib, importlib.util, io, json, os, pathlib, shutil, subprocess, sys, tempfile
L='/home/vgpnk/Projects/shokunin/souji-shokunin'
A=L+'/.ufo/waves/round-43/w1/R43sentinel01'
S='/fast/scratch/hyaku/souji-r43/R43sentinel01'
F='f8c805dbfa7f45814cf9a7270fa8bbffb41a8373'
BASE='13de0e84b45efd1113f077d58fc1e89bc586a013'
os.makedirs(S,exist_ok=True)
os.chdir(S)
os.environ['TMPDIR']=S
os.environ['HOME']=S+'/home'
os.makedirs(os.environ['HOME'],exist_ok=True)
realrun=subprocess.run

def run(argv, **kw):
    if argv[0]=='git' and any(x in argv for x in ('commit','checkout','branch','add','update-ref')):
        assert '-C' in argv, argv
        d=argv[argv.index('-C')+1]
        top=realrun(['git','-C',d,'rev-parse','--show-toplevel'],capture_output=True,text=True,check=True).stdout.strip()
        assert os.path.realpath(top)==os.path.realpath(d),(top,d)
    return realrun(argv,**kw)
subprocess.run=run

def cmd(argv,**kw):
    p=run(argv,capture_output=True,text=True,**kw)
    print('$ '+json.dumps(argv)+'\nrc='+str(p.returncode)+'\n'+p.stdout+p.stderr,flush=True)
    return p

def load(name):
    spec=importlib.util.spec_from_file_location(name,A+'/'+name+'.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

try:
    print('AXES: operability; coverage; write-envelope containment; provenance',flush=True)
    print('uid='+str(os.getuid())+' frozen='+F+' base='+BASE,flush=True)
    # Pin a scratch-only source repository so score-candidate resolves its own LANE safely.
    R=S+'/harness-repo'
    cmd(['git','clone','-q','--shared',L,R])
    cmd(['git','-C',R,'checkout','-q','--detach',BASE])
    cmd(['git','-C',R,'branch','-f','master',BASE])
    frozen=run(['git','-C',R,'show','master:census/round-43/score-candidate.sh'],capture_output=True,check=True).stdout
    assert frozen==pathlib.Path(A+'/score-candidate.sh').read_bytes()
    os.makedirs(S+'/scores')
    for dest in ['census/round-43/c2-counter.py','census/round-43/c3-survivors.tsv','census/round-43/preregistration.txt','../escape','/absolute']:
        cmd(['bash',R+'/census/round-43/score-candidate.sh','c2',S+'/scores',dest+'='+A+'/c2-counter.py'])
    # Symlinked allowlisted leaf in a scratch clone only.
    leaf=R+'/tools/souji-freeze-check.py'
    os.unlink(leaf);os.symlink(S+'/symlink-victim',leaf)
    pathlib.Path(S+'/symlink-victim').write_text('CANARY\n')
    cmd(['git','-C',R,'add','tools/souji-freeze-check.py'])
    ident=dict(os.environ,GIT_AUTHOR_NAME='fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_NAME='fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
    cmd(['git','-C',R,'commit','-qm','scratch symlink guard'],env=ident)
    cmd(['git','-C',R,'branch','-f','master','HEAD'])
    cmd(['bash',R+'/census/round-43/score-candidate.sh','c2',S+'/scores','tools/souji-freeze-check.py='+A+'/c2-counter.py'])
    print('symlink-victim='+repr(pathlib.Path(S+'/symlink-victim').read_text()),flush=True)
    c2=load('c2-counter')
    c2s=S+'/c2';os.makedirs(c2s)
    print('C2 env='+json.dumps(c2.env(c2s),sort_keys=True),flush=True)
    for name,mut in c2.CASE_BUILDERS.items():
        d,tip,_=c2.build(c2s,name,mut)
        print('C2 built '+d+' tip='+tip,flush=True)
    print('HOME files='+json.dumps([str(p.relative_to(S)) for p in pathlib.Path(S+'/home').rglob('*')]),flush=True)
    # Ordinary relative-write fixture: use the canonical c3 runner, never a lane cwd.
    c3=load('c3-counter')
    c3s=S+'/c3';os.makedirs(c3s)
    fx=b'import os, pathlib\npathlib.Path("cwd-canary").write_text(os.getcwd())\nprint("cwd="+os.getcwd())\nprint("SUMMARY cases=1 pass=1 fail=0")\n'
    p,elapsed,to,fxpath=c3.run_fixture(fx,A+'/c3-counter.py',c3s+'/fixture',c3s)
    print('C3 run_fixture rc='+str(p.returncode)+' timeout='+str(to)+' fixture='+fxpath+' stdout='+p.stdout.decode(),flush=True)
    print('C3 cwd-canary='+str(pathlib.Path(c3s+'/cwd-canary'))+' value='+pathlib.Path(c3s+'/cwd-canary').read_text(),flush=True)
    # Verify the selftest's mkdtemp honors ambient TMPDIR instead of explicit --scratch.
    ambient=S+'/ambient-temp';os.makedirs(ambient)
    tempfile.tempdir=ambient
    created=[]
    def hook(event,args):
        if event=='tempfile.mkdtemp': created.append(args[0])
    sys.addaudithook(hook)
    print('C3 stderr_discrimination='+str(c3.stderr_discrimination_selftest())+' created='+json.dumps(created)+' explicit_scratch='+c3s,flush=True)
    tempfile.tempdir=S
    # Hidden audit under ambient global config canary; runtime wrapper asserts all fixture commits.
    canary=S+'/global.gitconfig';pathlib.Path(canary).write_text('[sentinel]\n\tvalue = untouched\n')
    before=pathlib.Path(canary).read_bytes();os.environ['GIT_CONFIG_GLOBAL']=canary
    tool=run(['git','-C',L,'show',BASE+':tools/souji-freeze-check.py'],capture_output=True,check=True).stdout
    toolpath=S+'/freeze-tool.py';pathlib.Path(toolpath).write_bytes(tool)
    hidden=load('c2-hidden-audit')
    rc=hidden.main(['--tool',toolpath,'--work',S+'/hidden'])
    print('HIDDEN rc='+str(rc)+' global_canary_unchanged='+str(before==pathlib.Path(canary).read_bytes())+' sha256='+hashlib.sha256(before).hexdigest(),flush=True)
    # Re-derive required kinds directly, recording exact plumbing commands.
    c1=load('c1-counter')
    req=run(['git','-C',L,'show',F+':census/round-43/c1-required.tsv'],capture_output=True,text=True,check=True).stdout.splitlines()
    original=c1.git
    def recorded(root,scratch,*args):
        print('C1 plumbing '+json.dumps(['git','-C',root]+list(args)),flush=True)
        return original(root,scratch,*args)
    c1.git=recorded
    keys=req[0].split('\t')
    for line in req[1:]:
        row=dict(zip(keys,line.split('\t')))
        print('C1 rederive '+row['kind']+' '+repr(c1.rederive(row['kind'],row,S,L)),flush=True)
finally:
    shutil.rmtree(S,ignore_errors=True)
    print('scratch_removed='+str(not os.path.exists(S)),flush=True)
