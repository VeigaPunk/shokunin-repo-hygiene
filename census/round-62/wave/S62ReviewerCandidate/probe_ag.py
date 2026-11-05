#!/usr/bin/env python3
"""S62ReviewerCandidate: A-G matrix probe for the r62 C1 index-flag rule.

Builds one fixture repo per row per the frozen matrix, runs the candidate
and the base tool over each, and checks enforcement ordering with a
corrupt-index failure probe. Prints one compact JSON blob at the end.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

CAND = os.path.abspath(sys.argv[1])
BASE = os.path.abspath(sys.argv[2])
WORK = os.path.abspath(sys.argv[3])
os.makedirs(WORK, exist_ok=True)
shutil.rmtree(WORK)
os.makedirs(WORK)

ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}


def git(repo, *args, **kw):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, env=ENV, **kw)


def git_clean(repo, *args, **kw):
    p = git(repo, *args, **kw)
    assert p.returncode == 0, (args, p.stdout[-400:], p.stderr[-400:])
    return p


def new_repo(work_name):
    d = os.path.join(WORK, work_name)
    os.makedirs(d)
    assert git(d, "init", "-q").returncode == 0
    tl = git_clean(d, "rev-parse", "--show-toplevel").stdout.decode().strip()
    assert tl == os.path.realpath(d), (tl, d)
    return d


def commit_instr(repo, rel, body):
    p = os.path.join(repo, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(body)
    with open(os.path.join(repo, "notes.txt"), "w") as f:
        f.write("notes\n")
    git_clean(repo, "add", ".")
    git_clean(repo, "-c", "user.name=cand", "-c", "user.email=cand@x", "commit", "-q", "-m", "seed")
    return git_clean(repo, "rev-parse", "HEAD").stdout.decode().strip()


def run_tool(tool, repo, rev, out, allow_dirty=False):
    argv = ["python3", tool, "--root", repo, "--rev", rev,
            "--instrument", "tools/counter.py", "--out", out,
            "--", "echo", "ran"]
    if allow_dirty:
        argv.insert(-5, "--allow-dirty")
        i = argv.index("--allow-dirty")
        # keep it a flag, not part of the positional argv: it must sit before `--`
        del argv[i]
        argv.insert(argv.index("--"), "--allow-dirty")
    return subprocess.run(argv, capture_output=True, env=ENV, cwd=WORK)


def tag_of(repo, path):
    out = git_clean(repo, "ls-files", "-v", "--", path).stdout.decode().strip()
    return out[:1]


def expected_class(outline):
    if "RECEIPT-INDEX-FLAG-CONCEALED" in outline:
        return "indexFlag"
    if "lane worktree is dirty" in outline:
        return "dirty"
    if "differs from committed bytes" in outline:
        return "differs"
    if outline.startswith("accepted"):
        return "ACCEPT"
    return "OTHER"


def lastline(r):
    txt = (r.stdout + r.stderr).decode("utf-8", "replace").strip()
    return txt.splitlines()[-1][:220] if txt else "<no output>"


rows = [
    ("A", "honest-clean", False, False, False),
    ("B", "honest-allow-dirty", True, False, False),
    ("C", "dirty-visible", True, False, False),
    ("D", "skip-worktree-forged", False, True, "S"),
    ("E", "assume-unchanged-forged", False, True, "h"),
    ("F", "skip-worktree-unmodified", False, False, "S"),
    ("G", "instrument-skip-worktree-forged", False, False, "S"),
]

EXPECT = {"A": "ACCEPT", "B": "ACCEPT", "C": "dirty", "D": "indexFlag",
          "E": "indexFlag", "F": "indexFlag", "G": "DIFFERS-OR-FLAG"}

results = {}
for row_id, _name, dirty, forged, flag in rows:
    repo = new_repo("m-" + row_id)
    rev = commit_instr(repo, "tools/counter.py",
                       "#!/bin/sh\necho counter-ok\n")
    commit_instr(repo, "tools/instr.sh", "#!/bin/sh\necho instr-ok\n")
    if dirty:
        with open(os.path.join(repo, "notes.txt"), "a") as f:
            f.write("edit\n")
    if flag:
        if row_id == "G":
            subprocess.run(["git", "-C", repo, "update-index", "--skip-worktree",
                            "tools/instr.sh"], capture_output=True, env=ENV)
            assert tag_of(repo, "tools/instr.sh") == "S", tag_of(repo, "tools/instr.sh")
            p = os.path.join(repo, "tools", "instr.sh")
        else:
            subprocess.run(["git", "-C", repo, "update-index", "--" +
                            ("skip-worktree" if flag == "S" else "assume-unchanged"),
                            "tools/counter.py"], capture_output=True, env=ENV)
            assert tag_of(repo, "tools/counter.py") == flag, tag_of(repo, "tools/counter.py")
            p = os.path.join(repo, "tools", "counter.py")
        if forged:
            with open(p, "a") as f:
                f.write("\necho FORGED\n")
    out = os.path.join(repo, "receipt.out")
    # snapshot worktree state so the base run sees the same bytes as the cand run
    snap = {}
    for root_, dirs_, files_ in os.walk(repo):
        if ".git" in dirs_:
            dirs_.remove(".git")
        for fn in files_:
            fp_ = os.path.join(root_, fn)
            snap[fp_] = open(fp_, "rb").read()
    for toolname, tool in (("cand", CAND), ("base", "/dev/null")):
        r = run_tool(tool if toolname == "cand" else BASE if os.path.isfile(BASE) else "/dev/null", repo, rev, out,
                     allow_dirty=(row_id == "B"))
        cl = expected_class((r.stdout + r.stderr).decode("utf-8", "replace").strip())
        results.setdefault(row_id, {})[toolname] = {
            "rc": r.returncode, "class": cl,
            "line": lastline(r),
        }
        if os.path.exists(out):
            results[row_id][toolname]["outSize"] = os.path.getsize(out)
            os.unlink(out)
        else:
            results[row_id][toolname]["outSize"] = 0

order = {}
cr = new_repo("order")
rev = commit_instr(cr, "tools/counter.py", "#!/bin/sh\necho counter-ok\n")
subprocess.run(["git", "-C", cr, "update-index", "--skip-worktree", "tools/counter.py"], capture_output=True, env=ENV)
with open(os.path.join(cr, "notes.txt"), "a") as f:
    f.write("edit\n")
out = os.path.join(cr, "receipt.out")
r = run_tool(CAND, cr, rev, out, allow_dirty=True)
order["dirty+flagged allow-dirty"] = {"rc": r.returncode,
                                      "line": lastline(r)}
r = run_tool(CAND, cr, rev, out, allow_dirty=False)
order["dirty+flagged no-flag"] = {"rc": r.returncode,
                                  "line": lastline(r)}

cn = new_repo("corrupt")
sha = git_clean(cn, "hash-object", "-w", "-t", "blob", "--stdin",
                input=b"corrupt index bytes").stdout.decode().strip()
git_clean(cn, "update-index", "--add", "--cacheinfo", "100644," + sha + ",tools/counter.py")
git_clean(cn, "-c", "user.name=cand", "-c", "user.email=cand@x", "commit", "-q", "-m", "c")
idx = os.path.join(cn, ".git", "index")
with open(idx, "r+b") as f:
    f.seek(2048)
    f.write(b"\xde\xad\xbe\xef")
out = os.path.join(cn, "receipt.out")
r = run_tool(CAND, cn, git_clean(cn, "rev-parse", "HEAD").stdout.decode().strip(), out)
order["corrupt-index"] = {"rc": r.returncode,
                          "line": lastline(r),
                          "outExists": os.path.exists(out)}

print(json.dumps({"rows": results, "order": order}, indent=1, sort_keys=True))
