#!/usr/bin/env python3
"""Build single-edit writer mutants (round-71 C1 writer change) + base-writer 39/40 harness file."""
import os, sys, hashlib

S = os.path.dirname(os.path.abspath(__file__))
CAND = os.path.join(S, "writer-candidate.py")
MUT = os.path.join(S, "mut")

src = open(CAND, "rb").read()
text = src.decode()

def edit(name, old, new, count=1):
    assert text.count(old) == count, (name, text.count(old), count)
    out = text.replace(old, new, 1) if count == 1 else text.replace(old, new)
    p = os.path.join(MUT, name + ".py")
    open(p, "w").write(out)
    return p

EDITS = {}

EDITS["W1"] = ('if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_ATTR_SOURCE") and k not in PATHSPEC_ENV}',
               'if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR") and k not in PATHSPEC_ENV}',
               "drop GIT_ATTR_SOURCE from git() scrub tuple")
EDITS["W2"] = ('"-c", f"core.excludesFile={os.devnull}", "-c", "core.fileMode=true", *args]',
               '"-c", f"core.excludesFile={os.devnull}", *args]',
               "drop -c core.fileMode=true pin")
EDITS["W3"] = ('''    # r71 C1: a configured clean/process filter on any tracked path makes the status witness untrustworthy.
    pre_drivers = _filter_drivers(top)
    if pre_drivers:
        refuse(_filter_refusal(pre_drivers))
''', '', "delete pre-run _filter_drivers refusal (post-run kept)")
EDITS["W4"] = ('''    # r71 C1: a driver configured (or a filter attribute added) by the wrapped command also refuses.
    post_drivers = _filter_drivers(top)
    if post_drivers:
        refuse(_filter_refusal(post_drivers))
''', '', "delete post-run _filter_drivers refusal (pre-run kept)")
EDITS["W5"] = ('        for key in ("clean", "process"):', '        for key in ("clean",):',
               "check only clean, not process")
EDITS["W6"] = ('sorted(values - {b"unspecified", b"unset", b"set"})',
               'sorted(values - {b"unspecified", b"unset"})',
               'treat attribute value "set" as a driver')
EDITS["W7"] = ('''    if ca.returncode != 0:
        refuse(f"cannot read filter attributes of {top}: {ca.stderr.decode('utf-8', 'replace').strip()}")
''', '''    if ca.returncode != 0:
        return []
''', "return [] when check-attr fails over a non-empty ls-files")
EDITS["W8"] = ('ca = git(top, "check-attr", "--stdin", "-z", "filter", input=ls.stdout)',
               'ca = git(top, "check-attr", "--cached", "--stdin", "-z", "filter", input=ls.stdout)',
               "read filter attributes from the index only (check-attr --cached)")

for name in ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"]:
    old, new, desc = EDITS[name]
    p = edit(name, old, new)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"{name}\t{desc}\t{h}")

# ---- base writer + cases 39/40 + CASES entries + FILTER_CLASS ----
base = open(os.path.join(S, "writer-base.py")).read()
cstart = text.index("def case_39_filter_driver_refused")
cend = text.index("\nCASES = (", cstart)
cases_src = text[cstart:cend].rstrip() + "\n"
assert "def case_40_local_filemode_pinned" in cases_src

stub = '''\n\n# r71 C1 constants + case bodies appended by S71MutWriter (base bytes + candidate cases 39/40).
FILTER_CLASS = "RECEIPT-FILTER-DRIVER-SET"


''' + cases_src + "\n"

anchor = 'case_38_pathspec_env_scrubbed),\n)\n'
assert base.count(anchor) == 1
insert_entries = anchor.replace('), \n)', '')  # placeholder, replaced below
entries = ('case_38_pathspec_env_scrubbed),\n'
           '    ("filter-driver: configured clean filter on a tracked path refused (committed, info/attributes); '
           'no-driver attribute accepted; GIT_ATTR_SOURCE filter tree scrubbed (r71 C1)", case_39_filter_driver_refused),\n'
           '    ("filemode-pin: repository-local core.fileMode=false cannot hide a pre-run or in-run mode flip; '
           'clean tree accepted (r71 C1)", case_40_local_filemode_pinned),\n)\n')
base2 = base.replace(anchor, entries, 1)
assert base2 != base
# insert the case bodies + constant before the CASES tuple (functions must precede it)
mark = '\nCASES = (\n'
assert base2.count(mark) == 1
base2 = base2.replace(mark, stub + mark, 1)
p = os.path.join(MUT, "BASE+39+40.py")
open(p, "w").write(base2)
print("BASE+39+40\tsha256=" + hashlib.sha256(base2.encode()).hexdigest() +
      f"\tcases={base2.count('    (\"')}")
