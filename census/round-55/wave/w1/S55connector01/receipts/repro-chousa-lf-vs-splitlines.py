import importlib.util
spec = importlib.util.spec_from_file_location("csc", "/fast/scratch/hyaku/souji-r55/S55connector01/repro/chousa-stale-count-check.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
RECEIPT_ROWS = 7
# The stale count is on LF-line 1; a human/editor/grep -n cites it as "line 1".
prose = "\x0cQUOTES=9 stale count\ncorrection: this entry is superseded by line 1\n"
lf, sl = prose.split('\n'), prose.splitlines()
print("LF  (editor / grep -n) numbering:", [(i, repr(l)) for i,l in enumerate(lf,1)])
print("splitlines() numbering         :", [(i, repr(l)) for i,l in enumerate(sl,1)])
print()
for name, lines in (("splitlines (chousa today)", sl), ("LF-only (one line model)", lf)):
    hits = m.scan(lines, RECEIPT_ROWS)
    unresolved = sum(1 for _,_,ok in hits if not ok)
    print("%-28s hits=%s unresolved=%d -> %s" % (name, hits, unresolved, "FAIL" if unresolved else "PASS"))
print()
print("LF numbering is the one a human cites (grep -n / editor): the stale count is line 1,")
print("the correction names line 1 -> correctly resolved (PASS).")
print("splitlines() invents a phantom line, so the citation no longer names the stale")
print("line -> the tool reports a stale count that does not exist (FAIL).")
