import sys
sys.path.insert(0, sys.argv[1])
src = open(sys.argv[2], encoding="utf-8").read()
import importlib.util
spec = importlib.util.spec_from_file_location("cm", sys.argv[3])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for mid, _d, old, new in m.MUTANTS + m.EQUIV:
    if mid in sys.argv[4:]:
        assert src.count(old) == 1, mid
        open("mut-%s.py" % mid, "w", encoding="utf-8").write(src.replace(old, new))
        print("wrote", mid)
