import os,sys,re,json,hashlib,subprocess,importlib.util,shutil
from pathlib import Path
from markdown_it import MarkdownIt
S=Path('/fast/scratch/hyaku/souji-r57/S57reviewer01')
O=Path('/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57reviewer01')
L=Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
os.environ['TMPDIR']=str(S)
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def run(cmd):
 p=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,env=os.environ,timeout=120)
 return p
spec=importlib.util.spec_from_file_location('builder',L/'census/round-57/fixtures/build-fixtures.py'); b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
A='R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79'
B='R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79'
C=A+'\n'+B+'\n'
cases={
 '01-block': '<!--\n'+C+'-->\n',
 '02-block-three-spaces':'   <!--\n'+C+'-->\n',
 '03-inline':'prose <!--\n'+C+'-->\n',
 '04-two-inline-openers':'prose <!-- one --> <!-- two\n'+C+'-->\n',
 '05-two-block-openers':'<!-- one --> <!-- two\n'+C+'-->\n',
 '06-opener-in-fence':'```\n<!--\n```\n'+C+'-->\n',
 '07-closer-following-correction':'prose <!--\n--> '+A+'\n'+B+'\n',
 '08-abrupt-block-bang':'<!-->\n'+C,
 '09-abrupt-block-dash':'<!--->\n'+C,
 '10-abrupt-inline-bang':'prose <!-->\n'+C,
 '11-abrupt-inline-dash':'prose <!--->\n'+C,
 '12-unclosed-block':'<!--\n'+C,
 '13-unclosed-inline':'prose <!--\n'+C,
 '14-lazy-indent4':'paragraph\n    <!--\n'+C+'-->\n',
 '15-indent4-after-blank':'\n    <!--\n'+C+'-->\n',
 '16-crlf-inline':('prose <!--\n'+C+'-->\n').replace('\n','\r\n'),
 '17-nested-block':'<!-- outer\ninside <!-- inner\n'+C+'-->\n',
 '18-closer-before-opener':'prose --> <!--\n'+C+'-->\n',
 '19-bang-closer-block':'<!--\n--!>\n'+C,
 '20-bang-closer-inline':'prose <!--\n--!>\n'+C,
 '21-split-token':'R52-COR<!-- hidden -->RECTION SCORECARD.md:5 stale=78 recomputed=79\n'+B+'\n',
 '22-inline-code-opener':'prose `<!--`\n'+C+'-->\n',
 '23-escaped-opener':'prose \\<!--\n'+C+'-->\n',
 '24-link-destination':'[link](https://example.invalid/<!--)\n'+C+'-->\n',
 '25-list-container':'- prose <!--\n  '+A+'\n  '+B+'\n  -->\n',
 '26-tab-lazy':'paragraph\n\t<!--\n'+C+'-->\n',
 '27-fence':'~~~\n'+C+'~~~\n',
 '28-fence-vt-closer':'~~~\n~~~\x0b\n'+C,
 '29-one-line-wrapper':'<!-- '+A+' -->\n'+B+'\n',
 '30-empty-comment-then-block':'prose <!----> <!--\n'+C+'-->\n',
 '31-second-opener-closer-line':'prose <!-- first\n--> <!-- second\n'+C+'-->\n',
 '32-block-then-inline-code':'<!-- first -->\n`<!--`\n'+C+'-->\n',
}
md=MarkdownIt('commonmark')
# HTML comment tokenizer: abrupt empty forms, standard/bang close, or EOF.
comments=re.compile(r'<!--(?:>|->|[\s\S]*?(?:--!?>|\Z))')
rows=[]
for name,body in cases.items():
 d=S/name; d.mkdir()
 assert run(['git','-C',d,'init','-q']).returncode==0
 assert run(['git','-C',d,'rev-parse','--show-toplevel']).stdout.strip()==str(d)
 for k,v in [('user.name','fixture'),('user.email','fixture@invalid'),('commit.gpgsign','false')]:
  assert run(['git','-C',d,'config',k,v]).returncode==0
 sc='\n'.join(b.sc_base_lines(name))+'\n\n'+body
 files={'SCORECARD.md':sc,'census/round-51/preregistration.txt':'\n'.join(b.pre_base_lines(name))+'\n','census/round-51/records/ws-drift-vs-r46.tsv':'\n'.join(b.RECORD_BODY)+'\n','corpus/SOURCES.md':b.REGISTRY_3ROWS,'LOG.md':'# log\n','corpus/README.md':'# corpus\n'}
 for path,data in files.items():
  p=d/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data.encode())
 assert run(['git','-C',d,'add','-A']).returncode==0
 assert run(['git','-C',d,'-c','core.hooksPath=/dev/null','commit','-qm','attack']).returncode==0
 rev=run(['git','-C',d,'rev-parse','HEAD']).stdout.strip()
 sha=hashlib.sha256(files['census/round-51/records/ws-drift-vs-r46.tsv'].encode()).hexdigest()
 cmd=[sys.executable,'-B',L/'census/round-57/c1-counter.py','--root',d,'--rev',rev,'--base',rev,'--record-sha256',sha,'--sources-rev-before',rev,'--sources-rev-after',rev,'--scratch',S]
 p=run(cmd);render=md.render(sc);visible=comments.sub('',render)
 tokens=[]
 for token in [A,B]:
  # Literal tokens in code are rendered, but correctly nonfiling: kept separate below.
  shown=token in visible
  target=token.split(' stale=')[0].replace('R52-CORRECTION ','')
  refused=any(line.startswith('FINDING ') and ('site '+target+')') in line for line in p.stdout.splitlines())
  if token not in sc: outcome='NO-LITERAL-TOKEN'
  elif not shown and not refused and p.returncode==0:outcome='HARM'
  elif shown and refused:outcome='OVER-HIDE'
  else:outcome='AGREE'
  tokens.append(dict(token=token,shown=shown,refused=refused,outcome=outcome))
 out=O/name;out.mkdir(exist_ok=True)
 (out/'SCORECARD.md').write_bytes(sc.encode());(out/'render.html').write_text(render);(out/'visible.html').write_text(visible)
 (out/'v6.txt').write_text('COMMAND '+ ' '.join(map(str,cmd))+'\n'+p.stdout+p.stderr+'EXIT='+str(p.returncode)+'\n')
 row=dict(name=name,rev=rev,exit=p.returncode,tokens=tokens,stdout=p.stdout)
 (out/'result.json').write_text(json.dumps(row,indent=2));rows.append(row)
(O/'attacks.json').write_text(json.dumps(rows,indent=2))
# Differential over the complete frozen 36-fixture population, both arms use identical repos.
work=S/'committed';work.mkdir()
diff=[]
for name in b.C1_FIXTURES:
 info=b.build_one(name,work);r=info['tip'];base=info['base'] if name in ('F5-REWRITE','F6-RECORD-DRIFT','F27-BINARY-NUMSTAT') else r
 arms=[]
 for rnd in (56,57):
  cmd=[sys.executable,'-B',L/f'census/round-{rnd}/c1-counter.py','--root',info['dir'],'--rev',r,'--base',base,'--record-sha256',info['record_sha256'],'--sources-rev-before',r,'--sources-rev-after',r,'--scratch',S]
  p=run(cmd);findings=[x.split()[1] for x in p.stdout.splitlines() if x.startswith('FINDING ')]
  arms.append({'round':rnd,'exit':p.returncode,'findings':findings,'stdout':p.stdout,'command':' '.join(map(str,cmd))})
 diff.append({'name':name,'arms':arms,'moved':(arms[0]['exit'],arms[0]['findings'])!=(arms[1]['exit'],arms[1]['findings'])})
(O/'differential.json').write_text(json.dumps(diff,indent=2))
print(json.dumps({'shapes':len(rows),'token_counts':{x:sum(t['outcome']==x for r in rows for t in r['tokens']) for x in ('HARM','OVER-HIDE','AGREE','NO-LITERAL-TOKEN')},'moved':[r['name'] for r in diff if r['moved']],'green_v5':sum(r['arms'][0]['exit']==0 for r in diff),'green_v6':sum(r['arms'][1]['exit']==0 for r in diff)},indent=2))
