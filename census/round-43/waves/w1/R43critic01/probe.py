#!/usr/bin/env python3
import concurrent.futures, hashlib, importlib.util, json, os, pathlib, shutil, subprocess, sys
L=pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
P=L/'.ufo/waves/round-43/w1/R43critic01'
S=pathlib.Path('/fast/scratch/hyaku/souji-r43/R43critic01')
REV='f8c805dbfa7f45814cf9a7270fa8bbffb41a8373'
E=dict(os.environ,TMPDIR=str(S),PYTHONDONTWRITEBYTECODE='1')
def committed(rel):
    return subprocess.check_output(['git','-C',str(L),'show',REV+':'+rel],env=E)
def load(rel,name):
    # Execute only the frozen instrument module, never candidate edits.
    src=committed(rel); m=type(sys)(name); m.__file__=str(L/rel); exec(compile(src,m.__file__,'exec'),m.__dict__); return m

def score(name,lesson,reg=None):
    f=P/(name+'.md'); f.write_text(lesson)
    work=S/name; work.mkdir()
    cmd=['bash',str(L/'census/round-43/score-candidate.sh'),'c1',str(work),'corpus/lessons/round-43.md='+str(f)]
    if reg is not None:
        r=P/(name+'.tsv'); r.write_text(reg); cmd+=['census/round-43/c1-required.tsv='+str(r)]
    p=subprocess.run(cmd,env=E,cwd=S,text=True,capture_output=True)
    result={'command':cmd,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    (P/(name+'.json')).write_text(json.dumps(result,indent=2)); return name,result

def c1():
    reg=committed('census/round-43/c1-required.tsv').decode(); rows=[x.split('\t') for x in reg.splitlines()[1:]]
    def lesson(rows):
        return '# Instrument attack only\n'+''.join('CORRECTION-R39 id=%s file=%s field=%s stale=%s derived=%s rev=%s\n'%tuple(r[:6]) for r in rows)
    good=lesson(rows)
    wrong=[r.copy() for r in rows]
    wrong[0][4]='rows=999999'; wrong[1][4]='W04=999999'; wrong[2][4]='0'*40
    # A duplicated required ID can overwrite a preceding false register row.
    badfirst=rows[0].copy(); badfirst[4]='rows=999999'
    dupe=reg.splitlines()[0]+'\n'+'\t'.join(badfirst)+'\n'+'\n'.join('\t'.join(r) for r in rows)+'\n'
    jobs=[('c1-good',good,None),('c1-derived-wrong',lesson(wrong),None),('c1-register-duplicate',good,dupe)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        return dict(ex.map(lambda x:score(*x),jobs))

def c2():
    m=load('census/round-43/c2-counter.py','c2'); out=[]
    for name,mut in m.CASE_BUILDERS.items():
        d,tip,ptext=m.build(str(S),'inspect-'+name,mut)
        mode=m.git(d,str(S),'ls-tree',tip,'census/control.txt')
        hist=m.git(d,str(S),'log','--format=%s').splitlines()
        prereg=m.git(d,str(S),'show',tip+':prereg.txt')
        freeze=m.git(d,str(S),'log','--all','--format=%H','--grep=^freeze$')
        changes=m.git(d,str(S),'diff','--name-only',freeze,tip)
        out.append({'case':name,'control_tree':mode,'commits':hist,'freeze_to_tip':changes,'prereg':prereg})
    (P/'c2-builders.json').write_text(json.dumps(out,indent=2)); return out

def c3():
    m=load('census/round-43/c3-counter.py','c3')
    tool=committed('tools/souji-worktree-drift.py').decode(); out={}
    # The named empty-regs mutant genuinely flips the parser to an uncaught ValueError.
    rec=S/'empty-regs.tsv'; rec.write_text('REPO\tr\tregs=\tprunable=0\nTOTAL\trepos=1\tregs=0\tprunable=0\n')
    for name,src in [('pristine',tool),('S13',tool.replace(*next((o,n) for mid,o,n in m.MUTANTS if mid=='S13')))]:
        mod=type(sys)(name); mod.__file__=str(S/(name+'.py')); exec(compile(src,mod.__file__,'exec'),mod.__dict__)
        try: result=repr(mod.parse_record(str(rec)))
        except Exception as e: result=type(e).__name__+': '+str(e)
        out[name]=result
    # Apply the exact execution-count leg to a fixture that never opens/runs --tool.
    fx=b"import os\nfor i in range(17): print('case-never-runs-%d=PASS' % i)\nif 'SHIM_LOG' in os.environ:\n    with open(os.environ['SHIM_LOG'],'w') as f: f.write('invoke forged\\n'*17)\nprint('SUMMARY cases=17 pass=17 fail=0')\n"
    (P/'c3-no-tool-fixture.py').write_bytes(fx)
    shim=S/'shim'; shim.mkdir(); wrapper=shim/'wrapper.py'; wrapper.write_text(m.WRAPPER)
    fxpath=m.write_fixture(str(shim),fx); env=m.env(str(shim)); env['SHIM_LOG']=str(shim/'shim.log')
    p=subprocess.run(['python3','-B',fxpath,'--tool',str(wrapper),'--work',str(shim)],cwd=S,env=env,capture_output=True,text=True)
    invocations=len((shim/'shim.log').read_text().splitlines()); passed=17
    out['shim']={'rc':p.returncode,'stdout':p.stdout,'logged_invocations':invocations,'shim_ok':invocations>=passed and passed>0,'actual_tool_invocations':0}
    # n10_before does not appear in the target predicate, and a changed tool sets it to base-receipt.
    source=committed('census/round-43/c3-counter.py').decode()
    target=source[source.index('    target = ('):source.index('    print("SUMMARY mutants=')]
    out['n10_gate']={'target_predicate':target,'tests_n10_before':'n10_before' in target,'changed_tool_label':'base-receipt'}
    out['tool_sha256']=hashlib.sha256(tool.encode()).hexdigest()
    (P/'c3-probes.json').write_text(json.dumps(out,indent=2)); return out

try:
    S.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        tasks={name:ex.submit(fn) for name,fn in [('c1',c1),('c2',c2),('c3',c3)]}
        for name,f in tasks.items():
            try: print(name,json.dumps(f.result(),sort_keys=True))
            except Exception as exc: print(name,'ERROR',repr(exc)); raise
finally:
    shutil.rmtree(S,ignore_errors=True)
