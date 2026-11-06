SEAT=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-70/w1/S70ScoutSources
S=/fast/scratch/hyaku/souji-r70/S70ScoutSources
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
{
echo "# S70ScoutSources — quote location, reject-reason, teaches-cell and row-shape receipts"
echo
echo "## 1. S304 located quote: verbatim, contiguous, section, word count"
python3 - <<'PY'
import re
S='/fast/scratch/hyaku/souji-r70/S70ScoutSources/'
q304="Treat pathspecs literally (i.e. no globbing, no pathspec magic). This is equivalent to setting the GIT_LITERAL_PATHSPECS environment variable to 1"
q305="will cause Git to treat all pathspecs literally, rather than as glob patterns"
print('S304 quote words:',len(q304.split()),'(<=25 required) ->',len(q304.split())<=25)
print('S305 quote words:',len(q305.split()))
for name,f in (('round-66 recipe.py output',"r70-stripped.txt"),('round-65 s297-tagstrip.py output','house-stripped.txt')):
    t=open(S+f,encoding='utf-8').read()
    c=re.sub(r'\s+',' ',t)
    print(f'  {name}:')
    print(f'     S304 quote  whitespace-normalized contiguous={q304 in c} offset={c.find(q304)}')
    print(f'     S305 quote  whitespace-normalized contiguous={q305 in c} offset={c.find(q305)}')
t=open(S+'r70-stripped.txt',encoding='utf-8').read()
c=re.sub(r'\s+',' ',t)
prev=[(m.start(),m.group(0)) for m in re.finditer(r'(?m)^(OPTIONS|Environment Variables)$',t)]
def sect(o):
    b=[x for x in prev if x[0]<o]; return b[-1] if b else None
print('  section of S304 quote (canonical recipe):',sect(c.find(q304)))
print('  section of S305 quote (canonical recipe):',sect(c.find(q305)))
PY
echo
echo "## 2. S305 reject reason: does the ENVIRONMENT VARIABLES dt GIT_LITERAL_PATHSPECS name 'magic'?"
python3 - <<'PY'
import re
h=open('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-70/srcs/git-manual.html',encoding='utf-8',errors='replace').read()
def block(anchor):
    i=h.find(anchor); i=h.rfind('<dt',0,i); j=h.find('</dd>',i); return h[i:j]
blk=block('spanclasssynopsiscodeGITLITERALPATHSPECScodespan')
print('  ENV dt GIT_LITERAL_PATHSPECS dt+dd contains "magic":', 'magic' in blk)
print('  ENV dt GIT_LITERAL_PATHSPECS dt+dd contains "glob" :', 'glob' in blk)
print('  text:', re.sub(r'\s+',' ',re.sub(r'<[^>]*>','',blk))[:230])
for v in ('GITGLOB','GITNOGLOB','GITICASE'):
    b=block('spanclasssynopsiscode'+v+'PATHSPECS')
    print('  sibling',v,'->', re.sub(r'\s+',' ',re.sub(r'<[^>]*>','',b))[:135])
opt=block('id="Documentation/git.txt---literal-pathspecs"')
print('  OPTIONS dt --literal-pathspecs dd:', re.sub(r'\s+',' ',re.sub(r'<[^>]*>','',opt))[:240])
print('  git(1) occurrences of ":(top)":', len(re.findall(re.escape(':(top)'),h)))
print('  OPTIONS sibling dd sentences:')
for opt_name in ('glob-pathspecs','noglob-pathspecs','icase-pathspecs'):
    b=block('id="Documentation/git.txt---'+opt_name+'"')
    print('   ', opt_name, '->', re.sub(r'\s+',' ',re.sub(r'<[^>]*>','',b))[:150])
PY
echo
echo "## 3. Registry row shape and used-by at tip"
python3 - <<'PY'
lines=open('/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md',encoding='utf-8').read().split('\n')
for n in (263,264):
    c=[x.strip() for x in lines[n-1].strip().strip('|').split('|')]
    print(f'  line {n}: id={c[0]} kind={c[2]} tier={c[3]} status={c[7]} recheck={c[9]} used-by={c[10]}  columns={len(c)}')
PY
echo "  used-by path at tip feb283ee:"
git -C "$LANE" ls-tree feb283eea6d03656864d9dcba43e178b127681ee corpus/knowledge/pathspec-env-scrub.md
echo "  lane sources census validator (run from lane root):"
cd "$LANE" && bash census/round-12/sources-census.sh; echo "  EXIT=$?"
} > "$SEAT/rows-receipt.txt" 2>&1
