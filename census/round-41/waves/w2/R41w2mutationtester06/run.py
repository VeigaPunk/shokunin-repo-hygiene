#!/usr/bin/env python3
"""R41w2mutationtester06 driver: scores every mutant in mutants/manifest.tsv.

For each mutant: (a) allowlisted dests run through the committed harness
census/round-41/score-candidate.sh c1 (SUMMARY verbatim); (b) every mutant also runs in a private
clone made by the same procedure (git clone --shared of the lane, copy bytes, commit in the CLONE only,
counter at that commit, plus landing gate at round 41). Clone is removed afterwards.
Outputs: mutants/out/<id>.score.txt and mutants/out/<id>.clone.txt. Never writes the lane.
"""
import os, shutil, subprocess, sys, tempfile

SEAT = os.path.dirname(os.path.abspath(__file__))
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCR = "/fast/scratch/hyaku/souji-r41/R41w2mutationtester06"
ALLOW = {"corpus/lessons/round-41.md", "corpus/SOURCES.md"}
ENV = dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
           GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
os.makedirs(SCR, exist_ok=True)
os.makedirs(os.path.join(SEAT, "mutants", "out"), exist_ok=True)

rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(SEAT, "mutants", "manifest.tsv"), encoding="utf-8")][1:]
summary = []
for mid, dest, name, desc, exp in rows:
    src = os.path.join(SEAT, "mutants", name)
    outdir = os.path.join(SEAT, "mutants", "out")
    # (a) official harness, allowlisted dests only
    if dest in ALLOW:
        p = subprocess.run(["bash", os.path.join(LANE, "census/round-41/score-candidate.sh"), "c1", SCR, "%s=%s" % (dest, src)],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=SCR, env=ENV)
        with open(os.path.join(outdir, mid + ".score.txt"), "w", encoding="utf-8") as f:
            f.write("$ bash census/round-41/score-candidate.sh c1 %s %s=mutants/%s\n" % (SCR, dest, name))
            f.write(p.stdout.decode("utf-8", "replace"))
            f.write("EXIT=%d\n" % p.returncode)
        score_summary = [l for l in p.stdout.decode("utf-8", "replace").splitlines() if l.startswith("SUMMARY")]
        score_exit = p.returncode
    else:
        score_summary, score_exit = ["(not allowlisted: harness not run)"], None
    # (b) private clone, same procedure, plus landing gate
    D = tempfile.mkdtemp(prefix="mut-", dir=SCR)
    try:
        C = os.path.join(D, "clone")
        subprocess.run(["git", "clone", "-q", "--shared", LANE, C], check=True, env=ENV)
        assert subprocess.run(["git", "-C", C, "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE, check=True,
                              env=ENV).stdout.decode().strip() == C
        dst = os.path.join(C, dest)
        shutil.copyfile(src, dst)
        subprocess.run(["git", "-C", C, "add", "-A"], check=True, env=ENV)
        subprocess.run(["git", "-C", C, "commit", "-q", "--allow-empty", "-m", "mutant " + mid], check=True, env=ENV)
        rev = subprocess.run(["git", "-C", C, "rev-parse", "HEAD"], stdout=subprocess.PIPE, check=True, env=ENV).stdout.decode().strip()
        cnt = subprocess.run(["python3", "-B", os.path.join(C, "census/round-41/c1-counter.py"), "--root", C, "--rev", rev, "--scratch", D],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=ENV)
        gate = subprocess.run(["python3", "-B", os.path.join(C, "tools/souji-landing-gate.py"), "--root", C, "--rev", rev, "--round", "41"],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=ENV, cwd=D)
        with open(os.path.join(outdir, mid + ".clone.txt"), "w", encoding="utf-8") as f:
            f.write("mutant=%s dest=%s rev=%s\n" % (mid, dest, rev))
            f.write("--- c1-counter\n" + cnt.stdout.decode("utf-8", "replace") + "EXIT=%d\n" % cnt.returncode)
            f.write("--- landing-gate round 41 (tail)\n" + "\n".join(gate.stdout.decode("utf-8", "replace").splitlines()[-6:]) + "\nEXIT=%d\n" % gate.returncode)
        cs = [l for l in cnt.stdout.decode("utf-8", "replace").splitlines() if l.startswith("SUMMARY")]
        summary.append((mid, dest, desc, exp, score_exit, score_summary[0] if score_summary else "(no SUMMARY)",
                        cnt.returncode, cs[0] if cs else "(no SUMMARY)", gate.returncode))
    finally:
        shutil.rmtree(D, ignore_errors=True)

with open(os.path.join(outdir, "SUMMARY.tsv"), "w", encoding="utf-8") as f:
    f.write("id\tdest\tdescription\texpected\tscore_exit\tscore_summary\tclone_counter_exit\tclone_summary\tlanding_gate_exit\n")
    for r in summary:
        f.write("\t".join(str(x) for x in r) + "\n")
print("done", len(summary))
