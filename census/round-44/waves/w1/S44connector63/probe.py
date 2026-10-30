import ast, hashlib, json, os, subprocess, sys
ROOT='/home/vgpnk/Projects/shokunin/souji-shokunin'
OUT=ROOT+'/.ufo/waves/round-44/w1/S44connector63'
SCR='/fast/scratch/hyaku/souji-r44/S44connector63'
BASE='55d7af6f5a22340f7a3de1c386e514ababfaa75f'
INHERITED='4641e14671e60bf6cdc62ba8045c02a387a0d72c'
FREEZE='d314fd6e85d62565344fa6c4b102f52f62297884'
lines=[]
def run(args):
 p=subprocess.run(args,cwd=SCR,capture_output=True,text=True,timeout=180)
 lines.extend(['COMMAND='+repr(args),p.stdout.rstrip(), 'STDERR='+p.stderr.rstrip(),'EXIT='+str(p.returncode)])
 return p
def blob(rev,path):
 p=subprocess.run(['git','-C',ROOT,'show',rev+':'+path],capture_output=True)
 return p.stdout if p.returncode==0 else None
paths=['census/round-44/c1-counter.py','census/round-44/c2-counter.py','census/round-44/c3-counter.py','census/round-44/c2-hidden-audit.py','corpus/lessons/round-44.md','tools/souji-freeze-check.py','tools/souji-worktree-drift.py','tests/fixtures/r38-drift-write-envelope.py','tests/fixtures/r44-drift-symlink-refusal.py']
for path in paths:
 lines.append('BLOB '+path+' '+json.dumps({r:(hashlib.sha256(b).hexdigest() if (b:=blob(r,path)) is not None else 'ABSENT') for r in [BASE,INHERITED,FREEZE]}))
run(['git','-C',ROOT,'log','-4','--format=%H %aI %s',FREEZE,'--']+paths)
for rev in [INHERITED,FREEZE]:
 counter=blob(FREEZE,'census/round-44/c1-counter.py')
 cp=OUT+'/frozen-c1-counter.py'
 with open(cp,'wb') as f:f.write(counter)
 run([sys.executable,'-B',cp,'--root',ROOT,'--rev',rev,'--scratch',SCR+'/c1-'+rev[:8]])
# AST-only: prove scenario construction equivalence without executing fixture git mutations.
a=ast.parse(blob(BASE,'census/round-43/c2-hidden-audit.py'))
b=ast.parse(blob(FREEZE,'census/round-44/c2-hidden-audit.py'))
for name in ['build','classes','run','git']:
 x=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==name)
 y=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==name)
 lines.append('AST_FUNCTION_EQUAL '+name+'='+str(ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False)))
for path in ['census/round-44/controls/c1-donothing.txt','census/round-44/controls/c2-donothing.txt','census/round-44/controls/c3-donothing.txt']:
 lines.append('FROZEN_CONTROL '+path+'\n'+blob(FREEZE,path).decode())
with open(OUT+'/probe-output.txt','w') as f:f.write('\n'.join(lines)+'\n')
print('\n'.join(lines))
