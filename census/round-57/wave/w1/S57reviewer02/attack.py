import os, subprocess, hashlib, json, shutil
from pathlib import Path
S=Path('/fast/scratch/hyaku/souji-r57/S57reviewer02')
O=Path('/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57reviewer02')
G=Path('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/c2-counter.py')
os.environ['TMPDIR']=str(S)
R=S/'repo'
R.mkdir()
env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_AUTHOR_NAME='review',GIT_AUTHOR_EMAIL='review@example.invalid',GIT_COMMITTER_NAME='review',GIT_COMMITTER_EMAIL='review@example.invalid')
log=[]
def git(*args):
    cmd=['git','-C',str(R),'-c','core.hooksPath=/dev/null',*args]
    p=subprocess.run(cmd,capture_output=True,text=True,env=env,check=True)
    log.append({'cmd':cmd,'stdout':p.stdout,'stderr':p.stderr,'exit':p.returncode})
    return p.stdout.strip()
try:
    git('init','-q','-b','main')
    assert git('rev-parse','--show-toplevel')==str(R)
    (R/'tool.py').write_text("print('v1')\n")
    git('add','tool.py'); git('commit','-q','-m','v1')
    a=git('rev-parse','HEAD'); pin_a=hashlib.sha256((R/'tool.py').read_bytes()).hexdigest()
    (R/'tool.py').write_text("print('v2')\n")
    git('add','tool.py'); git('commit','-q','-m','v2')
    b=git('rev-parse','HEAD'); pin_b=hashlib.sha256((R/'tool.py').read_bytes()).hexdigest()
    git('tag','-a','durable','-m','annotated durable tag',b)
    tag=git('rev-parse','refs/tags/durable'); tag_type=git('cat-file','-t',tag)
    git('update-ref','refs/heads/main',a,b)
    assert git('merge-base','--is-ancestor',b,'refs/tags/durable')==''
    # b is not reachable from main; its only durable ref is the annotated tag.
    refs_b=git('for-each-ref','--contains='+b,'--format=%(refname)')
    def body(rev=a,pin=pin_a):
        return f'rev={rev}\ninstrument=tool.py\ninstrument_sha256={pin}\nEXIT=0\n'
    honest=body()
    cases=[
        ('honest',honest,'tool.py'),
        ('duplicate-good-bad',honest+'rev=HEAD\n','tool.py'),
        ('duplicate-bad-good','rev=HEAD\n'+honest,'tool.py'),
        ('trailing-punctuation',honest.replace('rev='+a,'rev='+a+','),'tool.py'),
        ('spaces',honest.replace('rev='+a,'rev = '+a),'tool.py'),
        ('fenced-only',honest.replace('rev='+a+'\n','```example\nrev='+a+'\n```\n'),'tool.py'),
        ('crlf',honest.replace('\n','\r\n'),'tool.py'),
        ('different-revision-pin',body(a,pin_b),'tool.py'),
        ('tag-only-commit',body(b,pin_b),'tool.py'),
        ('annotated-tag-object',body(tag,pin_b),'tool.py'),
        ('no-execution-forgery',honest,'tool.py'),
        ('missing-pin',honest.replace('instrument_sha256='+pin_a+'\n',''),'tool.py'),
        ('missing-exit',honest.replace('EXIT=0\n',''),'tool.py'),
        ('manifest-instrument-dash','rev='+a+'\nEXIT=0\n','-'),
    ]
    results=[]
    def run(name,rows):
        mf=S/(name+'.tsv'); mf.write_text('receipt\tinstrument\n'+rows+'\n')
        cmd=['python3','-B',str(G),'--root',str(R),'--manifest',str(mf),'--scratch',str(S)]
        p=subprocess.run(cmd,capture_output=True,text=True,env=env)
        results.append({'case':name,'command':cmd,'manifest':mf.read_text(),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    for name,text,instrument in cases:
        (R/(name+'.txt')).write_bytes(text.encode())
        run(name,name+'.txt\t'+instrument)
    (R/'symlink.txt').symlink_to(R/'honest.txt')
    run('symlink','symlink.txt\ttool.py')
    run('manifest-three-columns','honest.txt\ttool.py\textra')
    run('manifest-missing-file','absent.txt\ttool.py')
    outside=S/'outside.txt'; outside.write_text(honest)
    run('manifest-absolute',str(outside)+'\ttool.py')
    run('manifest-escape','../outside.txt\ttool.py')
    result={'gate_sha256':hashlib.sha256(G.read_bytes()).hexdigest(),'fixture':{'a':a,'b':b,'tag':tag,'tag_type':tag_type,'refs_containing_b':refs_b,'pin_a':pin_a,'pin_b':pin_b},'git_setup':log,'results':results}
    (O/'observed.json').write_text(json.dumps(result,indent=2)+'\n')
    for x in results:
        print(x['case'], 'EXIT='+str(x['exit']), x['stdout'].strip().replace('\n',' | '))
finally:
    shutil.rmtree(S)
