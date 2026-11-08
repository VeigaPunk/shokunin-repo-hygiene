#!/usr/bin/env python3
"""S87ScoutShapes — C2 shape scan.

Question: does the lane contain a REAL path whose NAME carries a newline or a tab (the KN3 shape), and does
`git status` quote any real path right now?

Uses `git ls-files -z` (raw NUL-separated, NO quoting) so the answer is about real bytes, not git's C-quoted
spelling. Read-only.
"""
import subprocess, os, json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"


def git(*args):
    return subprocess.run(["git", "-C", LANE, *args], capture_output=True)


out = {}

# 1. TRACKED paths with control characters in the name, read raw (-z disables quoting).
p = git("ls-files", "-z")
tracked = p.stdout.split(b"\0")
bad_tracked = [t for t in tracked if t and any(c in t for c in (b"\t", b"\n", b"\r"))]
out["tracked_total"] = len([t for t in tracked if t])
out["tracked_with_control"] = len(bad_tracked)

# 2. The same paths as git's OWN quoted spelling (what the K4 line-form arm would record).
out["tracked_control_quoted"] = []
for t in bad_tracked:
    q = git("ls-files", "--", t.decode("utf-8", "surrogateescape")).stdout
    out["tracked_control_quoted"].append({"raw": t.decode("utf-8", "surrogateescape"),
                                          "ls-files-line": q.decode("utf-8", "replace").strip("\n")})

# 3. UNTRACKED-but-not-ignored paths with control characters, from the RAW -z status stream.
p = git("status", "--porcelain", "-z", "--untracked-files=all")
fields = p.stdout.split(b"\0")
out["status_raw_fields"] = len([f for f in fields if f])
out["status_quoted_paths"] = []
for f in fields:
    if f and b'"' in f:
        out["status_quoted_paths"].append(f.decode("utf-8", "replace"))
    if f and any(c in f for c in (b"\t", b"\n")):
        out["status_quoted_paths"].append("RAW-CTRL:" + f.decode("utf-8", "replace"))

# 4. Does the line-form (non -z) status quote anything today?
p = git("status", "--porcelain", "--untracked-files=all")
out["status_line_form_quoted_lines"] = [l for l in p.stdout.decode("utf-8", "replace").split("\n") if '"' in l]

# 5. On-disk (untracked, including ignored) paths whose name carries a control character.
disk = []
for root, dirs, files in os.walk(LANE):
    if ".git" in dirs:
        dirs.remove(".git")
    for n in files + dirs:
        if any(c in n for c in ("\t", "\n", "\r")):
            disk.append(os.path.relpath(os.path.join(root, n), LANE))
out["ondisk_control_names"] = sorted(disk)

print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "c2_paths_scan.json"), "w"), indent=1)
