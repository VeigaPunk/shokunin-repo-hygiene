import collections, concurrent.futures, hashlib, os, pathlib, re, subprocess
L='/home/vgpnk/Projects/shokunin/souji-shokunin'
O=pathlib.Path(L+'/.ufo/waves/round-44/w1/S44reviewer61')
S=pathlib.Path('/fast/scratch/hyaku/souji-r44/S44reviewer61')
F='d314fd6e85d62565344fa6c4b102f52f62297884'
B='55d7af6f5a22340f7a3de1c386e514ababfaa75f'
def blob(p):
    return subprocess.check_output(['git','-C',L,'show',F+':'+p])
def rows(p):
    return [x.split('\t') for x in blob(p).decode().splitlines()[1:] if x]
pop=rows('census/round-44/c1-population.tsv')
old=rows('census/round-42/c1-items.tsv')
reg=rows('census/round-42/c1-register.tsv')
prior=collections.Counter((r[0],r[1],r[3]) for r in old)
now=collections.Counter(tuple(r[:3]) for r in pop)
lookup={(r[0],r[1]):r[2:] for r in reg}
lesson=blob('corpus/lessons/round-42.md').decode()
corr={(m[0],m[1]):m[2] for m in re.findall(r'^CORRECTION-DE line=(\d+) token=(\S+) derived=(\S+) rev=bf618f6c5c09d302994871c94903abbea2deb60d$',lesson,re.M)}
summary=['AXES calibration/operability/coverage; scoped axis calibration',f'FROZEN {F}',f'population_occurrences={len(pop)} unique_keys={len(now)} duplicate_excess={len(pop)-len(now)}',f'prior_population_identical_keys_and_multiplicity={now==prior}',f'new_population_occurrences={sum((now-prior).values())}']
counts=collections.Counter()
lines=['population_row\tline\ttoken\tclass\tq76_disposition\tprior_evidence']
for i,r in enumerate(pop,1):
    line,tok,cls=r[:3]
    kind,path=lookup[(line,tok)]
    if kind=='resolved':
        status='already-accounted-path'; evidence='census/round-42/c1-register.tsv:'+str(i+1)+' resolved_to='+path
    elif (line,tok) in corr:
        status='already-corrected-scoped'; evidence='corpus/lessons/round-42.md CORRECTION-DE derived='+corr[(line,tok)]
    else:
        status='remaining-unaccounted'; evidence='NONE'
    counts[status]+=1
    lines.append('\t'.join([str(i),line,tok,cls,status,evidence]))
summary += [f'{k}={v}' for k,v in sorted(counts.items())]
summary += ['remaining_new_self_assessment_mismatches_under_Q76='+str(counts['remaining-unaccounted'])]
(O/'classification.tsv').write_text('\n'.join(lines)+'\n')
for name,p in [('r42-counter.py','census/round-42/c1-counter.py'),('r44-counter.py','census/round-44/c1-counter.py')]:
    data=blob(p); (S/name).write_bytes(data)
    summary.append('SHA256 '+p+' '+hashlib.sha256(data).hexdigest())
summary.append('SHA256 census/round-44/c1-population.tsv '+hashlib.sha256(blob('census/round-44/c1-population.tsv')).hexdigest())
def run(name):
    cmd=['python3','-B',str(S/name),'--root',L,'--rev',F,'--scratch',str(S)]
    p=subprocess.run(cmd,cwd=S,capture_output=True,text=True,timeout=600,env={**os.environ,'TMPDIR':str(S),'PYTHONDONTWRITEBYTECODE':'1'})
    text='$ '+' '.join(cmd)+'\n'+p.stdout+p.stderr+'EXIT='+str(p.returncode)+'\n'
    (O/(name+'.txt')).write_text(text)
    return text
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    for text in pool.map(run,['r42-counter.py','r44-counter.py']): summary.append(text)
text='\n'.join(summary)+'\n'
(O/'audit.txt').write_text(text)
print(text)
