import os, sys, runpy
with open("/fast/scratch/hyaku/souji-r42/R42w2critic05/s2b/calls.log", "a") as h:
    h.write(" ".join(sys.argv[1:]) + "\n")
sys.argv = ["/fast/scratch/hyaku/souji-r42/R42w2critic05/pristine-tool.py"] + sys.argv[1:]
runpy.run_path("/fast/scratch/hyaku/souji-r42/R42w2critic05/pristine-tool.py", run_name="__main__")
