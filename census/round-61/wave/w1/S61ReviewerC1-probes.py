#!/usr/bin/env python3
"""S61ReviewerC1 probe battery - hand-built chrono fixtures + git fact probes.

Every git call names -C <fixture>; toplevel is asserted before first commit;
throwaway identity only. Lane access is read-only (log/cat-file/rev-parse + the
base tool's own read-only queries)."""
import hashlib
import os
import subprocess
import sys

S = "/fast/scratch/hyaku/souji-r61/S61ReviewerC1"
TOOL = os.path.join(S, "base-tool.py")
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
IDENT = {"GIT_AUTHOR_NAME": "rev", "GIT_AUTHOR_EMAIL": "rev@scratch.invalid",
         "GIT_COMMITTER_NAME": "rev", "GIT_COMMITTER_EMAIL": "rev@scratch.invalid",
         "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "HOME": S}
ENV = dict(os.environ, **IDENT)

results = []


def git(d, *a, env=None, check=True):
    p = subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True,
                       env=env or ENV)
    if check and p.returncode:
        raise RuntimeError(("git",) + a, p.returncode, p.stderr.strip())
    return p


def fresh(name):
    d = os.path.join(S, name)
    subprocess.run(["rm", "-rf", d], check=True)
    os.makedirs(d)
    subprocess.run(["git", "init", "-q"], cwd=d, env=ENV, check=True)
    top = git(d, "rev-parse", "--show-toplevel").stdout.strip()
    assert top == os.path.realpath(d), (top, d)
    return d


def commit(d, files=None, delete=(), msg="c"):
    for rel, content in (files or {}).items():
        fp = os.path.join(d, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "wb") as fh:
            fh.write(content.encode())
    for rel in delete:
        os.remove(os.path.join(d, rel))
    git(d, "add", "-A")
    git(d, "commit", "-q", "--allow-empty", "-m", msg)
    return git(d, "rev-parse", "HEAD").stdout.strip()


def sha(b):
    return hashlib.sha256(b.encode()).hexdigest()


def receipt(cpy, rev40):
    return ("instrument=c.py\ninstrument_sha256=%s\nrev=%s\ncommand=python3 c.py\nEXIT=1\n"
            % (sha(cpy), rev40))


def prereg_txt(base40, cpy, pop, control="census/ctl.txt"):
    return ("Round: 61\n\n## C1\nBase: %s\nCounter: c.py sha256=%s\n"
            "Population: p.tsv sha256=%s\nControl: %s\nTarget: t\nKill: k\n"
            % (base40, sha(cpy), sha(pop), control))


def run_tool(root, pre, rev, substance=True):
    cmd = [sys.executable, "-B", TOOL, "--root", root, "--prereg", pre, "--rev", rev]
    if substance:
        cmd.append("--substance")
    p = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def adds(d, rev, path):
    p = git(d, "log", "--diff-filter=A", "--no-renames", "--full-history",
            "--format=%H", rev, "--", path)
    return [x for x in p.stdout.split() if x]


def rec(name, **kw):
    results.append((name, kw))
    print("=== %s" % name)
    for k, v in kw.items():
        print("  %s: %s" % (k, v))
    print()


CPY = "print('counter arm')\n"
POP = "h\nr\n"

# ---- case 1: at-freeze (the r60 rejection shape) --------------------------
d = fresh("at-freeze")
c1 = commit(d, {"c.py": CPY, "p.tsv": POP}, msg="c1 instruments")
c2 = commit(d, {".ufo/waves/round-61/prereg.txt": prereg_txt(c1, CPY, POP),
                "census/ctl.txt": receipt(CPY, c1)}, msg="c2 freeze: prereg+ctl SAME commit")
c3 = commit(d, msg="c3 child")
rc, out, err = run_tool(d, ".ufo/waves/round-61/prereg.txt", c2)
rec("at-freeze rev==freeze", base_exit=rc, stdout=out, stderr=err)
rc, out, err = run_tool(d, ".ufo/waves/round-61/prereg.txt", c3)
rec("at-freeze rev==child", base_exit=rc, stdout=out, stderr=err)
rec("at-freeze adds(ctl) from child", adds=adds(d, c3, "census/ctl.txt"),
    freeze=c2, adds_prereg=adds(d, c3, ".ufo/waves/round-61/prereg.txt"))

# ---- case 2: re-add-after (chrono-after, Reading B) -----------------------
d = fresh("re-add-after")
c1 = commit(d, {"c.py": CPY, "p.tsv": POP, "census/ctl.txt": receipt(CPY, c1 := "PENDING")},
            msg="placeholder")
# rebuild properly: receipt needs c1's id, so build instruments first
d = fresh("re-add-after")
c0 = commit(d, {"c.py": CPY, "p.tsv": POP}, msg="c0 instruments")
ctl_bytes = receipt(CPY, c0)
c1 = commit(d, {"census/ctl.txt": ctl_bytes}, msg="c1 add ctl")
c2 = commit(d, {".ufo/waves/round-61/prereg.txt": prereg_txt(c0, CPY, POP)},
            msg="c2 freeze: prereg only")
c3 = commit(d, delete=("census/ctl.txt",), msg="c3 delete ctl")
c4 = commit(d, {"census/ctl.txt": ctl_bytes}, msg="c4 re-add IDENTICAL ctl")
rc, out, err = run_tool(d, ".ufo/waves/round-61/prereg.txt", c4)
rec("re-add-after base verdict", base_exit=rc, stdout=out, stderr=err,
    note="blob(c4,ctl)==blob(c2,ctl): %s" % (ctl_bytes == open(os.path.join(d, "census/ctl.txt")).read()))
rec("re-add-after adds(ctl)", adds=adds(d, c4, "census/ctl.txt"),
    oldest=c1, newest=c4, freeze=c2)

# ---- case 3: re-add-at-freeze (content authored by freeze commit) --------
d = fresh("re-add-at-freeze")
c0 = commit(d, {"c.py": CPY, "p.tsv": POP}, msg="c0 instruments")
v1 = "unbound legacy run\nEXIT=1\n"
c1 = commit(d, {"census/ctl.txt": v1}, msg="c1 add unbound ctl")
bound = receipt(CPY, c0)
c2 = commit(d, {".ufo/waves/round-61/prereg.txt": prereg_txt(c0, CPY, POP),
                "census/ctl.txt": bound}, msg="c2 freeze: REWRITES ctl content")
c3 = commit(d, msg="c3 child")
rc, out, err = run_tool(d, ".ufo/waves/round-61/prereg.txt", c3)
rec("re-add-at-freeze base verdict", base_exit=rc, stdout=out, stderr=err)
rec("re-add-at-freeze adds(ctl)", adds=adds(d, c3, "census/ctl.txt"),
    oldest=c1, newest=c2 + " (== freeze)", freeze=c2)

# ---- case 4: glob pathspec ------------------------------------------------
d = fresh("glob")
c0 = commit(d, {"c.py": CPY, "p.tsv": POP}, msg="c0")
c1 = commit(d, {"census/ctl-old.txt": "old run\nEXIT=1\n"}, msg="c1 add innocent ctl-old")
g = prereg_txt(c0, CPY, POP, control="census/ctl*.txt")
c2 = commit(d, {".ufo/waves/round-61/prereg.txt": g,
                "census/ctl*.txt": receipt(CPY, c0)}, msg="c2 freeze literal glob-name receipt")
c3 = commit(d, msg="c3 child")
rc, out, err = run_tool(d, ".ufo/waves/round-61/prereg.txt", c3)
p = git(d, "log", "--diff-filter=A", "--no-renames", "--full-history", "--format=%H", c3,
        "--", "census/ctl*.txt")
rec("glob base verdict", base_exit=rc, stdout=out, stderr=err)
rec("glob log pathspec matches", matches=p.stdout.split(),
    note="oldest add is c1 (innocent census/ctl-old.txt) -> oldest-rule accepts")

# ---- case 5: orphan rev= (replacement for r60 tag case) -------------------
d = fresh("orphan-rev")
c0 = commit(d, {"c.py": CPY, "p.tsv": POP}, msg="c0")
orphan = git(d, "commit-tree", "HEAD^{tree}", "-m", "o").stdout.strip()
c2 = commit(d, {".ufo/waves/round-61/prereg.txt": prereg_txt(c0, CPY, POP),
                "census/ctl.txt": receipt(CPY, orphan)}, msg="c2 freeze, rev=orphan")
c3 = commit(d, msg="c3 child")
rc, out, err = run_tool(d, ".ufo/waves/round-61/prereg.txt", c3)
rec("orphan-rev base verdict", base_exit=rc, stdout=out, stderr=err,
    orphan=orphan, expect_class="CONTROL-REV-NOT-BEFORE-FREEZE")

# ---- case 6: rename probe (pre-freeze rename of the receipt) --------------
d = fresh("rename")
c0 = commit(d, {"c.py": CPY, "p.tsv": POP, "old.txt": receipt(CPY, "x" * 40)},
            msg="c0")
# fix receipt binding: receipt rev must be an ancestor; rebuild with c0
d = fresh("rename")
c0 = commit(d, {"c.py": CPY, "p.tsv": POP}, msg="c0")
c1 = commit(d, {"old.txt": receipt(CPY, c0)}, msg="c1 add old.txt")
git(d, "mv", "old.txt", "census/ctl.txt")
c2 = commit(d, msg="c2 rename (pre-freeze)")
c3 = commit(d, {".ufo/waves/round-61/prereg.txt": prereg_txt(c0, CPY, POP)},
            msg="c3 freeze")
c4 = commit(d, msg="c4 child")
rec("rename adds(ctl) --no-renames", adds=adds(d, c4, "census/ctl.txt"),
    note="rename commit c2 counts as the ADD of census/ctl.txt; rename at freeze would refuse")

# ---- case 7: shallow clone ------------------------------------------------
dst = os.path.join(S, "shallow-1")
subprocess.run(["rm", "-rf", dst], check=True)
p = subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + os.path.join(S, "at-freeze"), dst],
                   env=ENV, capture_output=True, text=True)
top = git(dst, "rev-parse", "--show-toplevel").stdout.strip()
assert top == os.path.realpath(dst)
rc, out, err = run_tool(dst, ".ufo/waves/round-61/prereg.txt", c3)
rec("shallow depth=1 (at-freeze)", clone_rc=p.returncode, base_exit=rc, stdout=out, stderr=err)
dst2 = os.path.join(S, "shallow-2")
subprocess.run(["rm", "-rf", dst2], check=True)
subprocess.run(["git", "clone", "-q", "--depth", "2", "file://" + os.path.join(S, "at-freeze"), dst2],
               env=ENV, check=True)
rc, out, err = run_tool(dst2, ".ufo/waves/round-61/prereg.txt", c3)
rec("shallow depth=2 (at-freeze)", base_exit=rc, stdout=out, stderr=err)

# ---- case 8: replace refs --------------------------------------------------
d = os.path.join(S, "at-freeze")
c2_tree = git(d, "rev-parse", c2 + "^{tree}").stdout.strip()
alt = git(d, "commit-tree", c2_tree, "-p", c1, "-m", "REPLACED freeze message").stdout.strip()
git(d, "replace", c2, alt)
rc, out, err = run_tool(d, ".ufo/waves/round-61/prereg.txt", c3)
p_vis = git(d, "log", "--diff-filter=A", "--no-renames", "--full-history", "--format=%H",
            c3, "--", "census/ctl.txt", env=dict(ENV, GIT_NO_REPLACE_OBJECTS="0"))
p_tool = adds(d, c3, "census/ctl.txt")
git(d, "replace", "-d", c2)
rec("replace-ref ignored by tool env", base_exit=rc, stdout=out,
    adds_with_replace_visible=p_vis.stdout.split(), adds_under_tool_env=p_tool,
    replaced_with=alt)

# ---- lane real-record probes (read-only) ----------------------------------
for path in ("census/round-60/controls/c1-do-nothing.txt",
             "census/round-60/controls/c2-do-nothing.txt",
             "census/round-60/preregistration.txt"):
    rec("lane adds %s" % path, adds=git(LANE, "log", "--diff-filter=A", "--no-renames",
        "--full-history", "--format=%H", "d05a00019835dee5b9bb8fe738add080434c4d67",
        "--", path).stdout.split())
rc, out, err = run_tool(LANE, "census/round-60/preregistration.txt",
                        "d05a00019835dee5b9bb8fe738add080434c4d67", substance=True)
rec("lane real record --substance (base bytes)", base_exit=rc, stdout=out, stderr=err)
rc, out, err = run_tool(LANE, "census/round-60/preregistration.txt",
                        "d05a00019835dee5b9bb8fe738add080434c4d67", substance=False)
rec("lane real record default (base bytes)", base_exit=rc, stdout=out, stderr=err)

print("PROBES COMPLETE")
