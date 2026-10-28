import os, sys, time
time.sleep(float(os.environ.get('SHIM_SLEEP', '1.0')))
os.execv(sys.executable, [sys.executable, '-B', '/fast/scratch/hyaku/souji-r41/R41w2critic04/tool.py'] + sys.argv[1:])
