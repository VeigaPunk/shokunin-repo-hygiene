import importlib.util,sys,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('gate',sys.argv[1]);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
work=Path('/fast/scratch/hyaku/souji-r58/S58Sentinel11/cleanup-probe');work.mkdir()
old=work/'c2-fixtures';old.mkdir();marker=old/'synthetic-marker';marker.write_text('preserve synthetic caller data\n')
created=[]
def builder(base):
    created.append(str(base));(base/'owned-marker').write_text('owned')
    return base/'repo',base,{}
def scorer(*args):return 0
g.build_fixtures=builder;g.score_selftest=scorer
rc=g.run_selftest(work,work/'unused-expected',[])
print(json.dumps({'case':'cleanup-success','EXIT':rc,'caller_marker':marker.read_text(),'created':created,'created_dirs_remain':[p for p in created if Path(p).exists()]}))
def failing(base):
    created.append(str(base));(base/'owned-marker').write_text('owned');raise RuntimeError('synthetic builder failure')
g.build_fixtures=failing
try:g.run_selftest(work,work/'unused-expected',[])
except RuntimeError as e:print(json.dumps({'case':'cleanup-exception','exception':str(e),'caller_marker':marker.read_text(),'created_dirs_remain':[p for p in created if Path(p).exists()]}))
