"""S61CriticRound probe: literal Q120 chronology rule over fixture repos (throwaway identity, fixture dirs only)."""
import os, subprocess, sys, tempfile, shutil, hashlib

S = os.environ["S"]
ENV = dict(os.environ, GIT_AUTHOR_NAME="crit", GIT_AUTHOR_EMAIL="crit@example.invalid",
           GIT_COMMITTER_NAME="crit", GIT_COMMITTER_EMAIL="crit@example.invalid",
           GIT_AUTHOR_DATE="2026-11-05T00:00:00+00:00", GIT_COMMITTER_DATE="2026-11-05T00:00:00+00:00")
ENV.pop("TMPDIR", None)

def g(d, *a, check=True):
    p = subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True, env=ENV)
    if check and p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (a, p.stderr))
    return p.stdout.strip(), p.returncode

def newrepo(name):
    d = os.path.join(S, "fx-" + name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    subprocess.run(["git", "-C", d, "init", "-q"], check=True, env=ENV)
    top, _ = g(d, "rev-parse", "--show-toplevel")
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    return d

def commit(d, files, msg, rm=()):
    for f, body in files.items():
        p = os.path.join(d, f); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(body)
    for f in rm:
        g(d, "rm", "-q", "--cached", f); os.unlink(os.path.join(d, f))
    g(d, "add", "-A")
    g(d, "commit", "-q", "--allow-empty", "-m", msg)
    return g(d, "rev-parse", "HEAD")[0]

REC = "census/x/ctl.txt"
PRE = "census/x/pre.txt"
GREEN = b"instrument=c.py\nrev=%s\nEXIT=0\n"
RED = b"instrument=c.py\nrev=%s\nEXIT=1\n"

def adds(d, rev, path):
    out, rc = g(d, "log", "--format=%H", "--diff-filter=A", "--no-renames", "--full-history", rev, "--", path, check=False)
    return out.split() if rc == 0 else None

def ancestor(d, a, b):
    return g(d, "merge-base", "--is-ancestor", a, b, check=False)[1] == 0

def blob(d, rev, path):
    out, rc = g(d, "rev-parse", "-q", "--verify", "%s:%s" % (rev, path), check=False)
    return out if rc == 0 else None

def literal_rule(d, freeze, rev_walk, path):
    """Spec rule: add commit from git log; refuse unless single/that commit is strict ancestor of freeze."""
    ids = adds(d, rev_walk, path)
    if not ids:
        return "EMPTY-SET (no add found from %s)" % rev_walk[:8]
    cid = ids[0]  # git log default order: newest first (the freeze_rev pattern uses --reverse instead)
    if cid == freeze or not ancestor(d, cid, freeze):
        return "REFUSE CONTROL-ADDED-NOT-BEFORE-FREEZE add=%s" % cid[:8]
    return "ACCEPT add=%s" % cid[:8]


def last_touch(d, freeze, path):
    out, rc = g(d, "log", "-1", "--format=%H", "--no-renames", "--full-history", freeze, "--", path, check=False)
    return out if rc == 0 and out else None

def fixed_rule(d, freeze, path):
    """Candidate F'': the newest commit reachable from freeze that changes PATH must be a strict ancestor of freeze."""
    last = last_touch(d, freeze, path)
    if not last:
        return "REFUSE CONTROL-MISSING-HISTORY (no commit reachable from freeze touches path)"
    if last == freeze or not ancestor(d, last, freeze):
        return "REFUSE CONTROL-ADDED-NOT-BEFORE-FREEZE last=%s" % last[:8]
    return "ACCEPT last=%s" % last[:8]

results = []
def base(d):
    return commit(d, {"c.py": b"print(1)\n"}, "base")

# S1 r60 shape
d = newrepo("s1-born-in-freeze"); x0 = base(d)
freeze = commit(d, {PRE: b"prereg\n", REC: RED % x0.encode()}, "freeze")
results.append(("S1 born in freeze   literal", literal_rule(d, freeze, freeze, REC)))
results.append(("S1 born in freeze   F''", fixed_rule(d, freeze, REC)))

# S2 born green in A, rewritten red in freeze B
d = newrepo("s2-rewrite-at-freeze"); x0 = base(d)
A = commit(d, {REC: GREEN % x0.encode()}, "A: receipt green")
B = commit(d, {PRE: b"prereg\n", REC: RED % x0.encode()}, "B: freeze rewrites receipt red")
results.append(("S2 rewrite-at-freeze literal", literal_rule(d, B, B, REC)))
results.append(("S2 rewrite-at-freeze F''", fixed_rule(d, B, REC)))

# S3 delete in C, re-add in freeze B
d = newrepo("s3-readd-at-freeze"); x0 = base(d)
A = commit(d, {REC: RED % x0.encode()}, "A: receipt added")
C = commit(d, {}, "C: receipt deleted", rm=(REC,))
B = commit(d, {PRE: b"prereg\n", REC: RED % x0.encode()}, "B: freeze re-adds receipt")
oldest = subprocess.run(["git", "-C", d, "log", "--format=%H", "--diff-filter=A", "--no-renames", "--full-history", "--reverse", B, "--", REC], capture_output=True, text=True, env=ENV).stdout.split()
results.append(("S3 readd-at-freeze literal newest", literal_rule(d, B, B, REC)))
results.append(("S3 readd-at-freeze freeze_rev-style oldest", "ACCEPT add=%s" % oldest[0][:8] if oldest and ancestor(d, oldest[0], B) else "?"))
results.append(("S3 readd-at-freeze F''", fixed_rule(d, B, REC)))

# S4 post-freeze delete+re-add on landing branch L; walk from L vs freeze
d = newrepo("s4-postfreeze-readd"); x0 = base(d)
A = commit(d, {REC: RED % x0.encode()}, "A: receipt added")
B = commit(d, {PRE: b"prereg\n"}, "B: freeze (receipt unchanged)")
C = commit(d, {}, "C: receipt deleted post-freeze", rm=(REC,))
L = commit(d, {REC: RED % x0.encode()}, "L: receipt re-added post-freeze (landing)")
oldest = subprocess.run(["git", "-C", d, "log", "--format=%H", "--diff-filter=A", "--no-renames", "--full-history", "--reverse", L, "--", REC], capture_output=True, text=True, env=ENV).stdout.split()
results.append(("S4 walk-from-landing literal newest", literal_rule(d, B, L, REC)))
results.append(("S4 walk-from-landing freeze_rev oldest", "ACCEPT add=%s (oldest)" % oldest[0][:8] if oldest and ancestor(d, oldest[0], B) else "?"))
results.append(("S4 walk-from-freeze literal", literal_rule(d, B, B, REC)))
results.append(("S4 F'' (freeze B)", fixed_rule(d, B, REC)))

# S5 empty set
d = newrepo("s5-empty"); x0 = base(d)
F = commit(d, {PRE: b"prereg\n"}, "F: freeze without receipt")
results.append(("S5 no receipt in history literal (walk x0)", literal_rule(d, F, x0, REC)))
results.append(("S5 no receipt F''", fixed_rule(d, F, REC)))

# H honest: receipt committed at A strictly before freeze B, unchanged
d = newrepo("h-honest"); x0 = base(d)
A = commit(d, {REC: RED % x0.encode()}, "A: receipt red committed")
B = commit(d, {PRE: b"prereg\n"}, "B: freeze")
results.append(("H honest literal", literal_rule(d, B, B, REC)))
results.append(("H honest F''", fixed_rule(d, B, REC)))

# H2 receipt rewritten before freeze (in commit R, strictly before B): should ACCEPT under F''
d = newrepo("h2-prefreeze-rewrite"); x0 = base(d)
A = commit(d, {REC: GREEN % x0.encode()}, "A: green")
R = commit(d, {REC: RED % x0.encode()}, "R: rewritten red before freeze")
B = commit(d, {PRE: b"prereg\n"}, "B: freeze")
results.append(("H2 pre-freeze rewrite literal", literal_rule(d, B, B, REC)))
results.append(("H2 pre-freeze rewrite F''", fixed_rule(d, B, REC)))

for k, v in results:
    print("%-48s %s" % (k, v))
