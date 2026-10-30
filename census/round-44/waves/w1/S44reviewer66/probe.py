import os, pathlib, subprocess, sys, json
lane='/home/vgpnk/Projects/shokunin/souji-shokunin'
scratch=pathlib.Path('/fast/scratch/hyaku/souji-r44/S44reviewer66')
out=pathlib.Path(lane+'/.ufo/waves/round-44/w1/S44reviewer66')
revs={'base':'55d7af6f5a22340f7a3de1c386e514ababfaa75f','frozen':'d314fd6e85d62565344fa6c4b102f52f62297884'}
receipt=[]
def record(s):
    print(s,flush=True); receipt.append(s)
for label,rev in revs.items():
    p=subprocess.run(['git','-C',lane,'show',rev+':tools/souji-worktree-drift.py'],capture_output=True,check=True)
    (scratch/(label+'.py')).write_bytes(p.stdout)
root=scratch/'empty-fleet'; root.mkdir(exist_ok=True)
rec=scratch/'record.tsv'; rec.write_text('REPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n')
regular=scratch/'parent-file'; regular.write_text('keep\n')
loop=scratch/'loop'; loop.symlink_to(loop)
for label in revs:
    work=scratch/label; work.mkdir(exist_ok=True)
    victim=work/'victim.json'; victim.write_text('keep\n')
    (work/'existing-link').symlink_to(victim)
    (work/'dangling-link').symlink_to(work/'missing.json')
    (work/'directory-link').symlink_to(work)
    parent=work/'parent-link'; parent.symlink_to(work,target_is_directory=True)
    cases={'regular':work/'out.json','existing-link':work/'existing-link','dangling-link':work/'dangling-link','directory-link':work/'directory-link','parent-link':parent/'parent-out.json','not-directory-parent':regular/'out.json','loop-parent':loop/'out.json'}
    for name,target in cases.items():
        cmd=[sys.executable,'-B',str(scratch/(label+'.py')),'--root',str(root),'--record',str(rec),'--json',str(target)]
        p=subprocess.run(cmd,cwd=scratch,capture_output=True,text=True,timeout=10)
        record('COMMAND '+json.dumps(cmd))
        record('CASE %s/%s rc=%d\nstdout=%s\nstderr=%s'%(label,name,p.returncode,p.stdout.rstrip(),p.stderr.rstrip()))
    record('STATE %s victim=%r missing_exists=%r existing_link=%r record=%r'%(label,victim.read_text(),(work/'missing.json').exists(),(work/'existing-link').is_symlink(),rec.read_text()))
(out/'probe-output.txt').write_text('\n'.join(receipt)+'\n')
