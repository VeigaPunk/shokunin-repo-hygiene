import os,subprocess,sys,tempfile,shutil
sys.path.insert(0,'/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42')
import importlib.util
spec=importlib.util.spec_from_file_location("c2c","/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
scratch="/fast/scratch/hyaku/souji-r42/R42w2mutationtester07/probe-sc"
os.makedirs(scratch,exist_ok=True)
tool="/fast/scratch/hyaku/souji-r42/R42w2mutationtester07/clone-tip/tools/souji-freeze-check.py"
for art,label in ((tool,"landed"),("/fast/scratch/hyaku/souji-r42/R42w2mutationtester07/clone-tip/census/round-42/controls/c2-stub-tool.py","control")):
    print(label,"plain:",m.run_selftest(art,scratch))
    for p in ("P1","P2","P3"):
        print(label,p,m.run_selftest(art,scratch,p))
