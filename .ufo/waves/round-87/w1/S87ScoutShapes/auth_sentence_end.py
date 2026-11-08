#!/usr/bin/env python3
"""S87ScoutShapes — refined: REAL paths (containing '/') immediately before a sentence-final period,
in the AUTHORITY scope the counter's `_declared` actually reads, at every revision in the lane's history.

The m16 clause is load-bearing exactly when a path is followed by '.' + a non-path byte.
This answers: has the lane ever put a PATH (not an English word) at a sentence end in an authority file?
"""
import subprocess, re, os, json, collections

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")
# a path-like run that contains at least one '/' and at least one '.', ending right before a sentence-final period
RE = re.compile(rb"[A-Za-z0-9._/@+~-]{4,}/[A-Za-z0-9._/@+~-]*\.(?![A-Za-z0-9._/@+~-])")
AUTH = ("SKILL.md", "LOG.md", "SCORECARD.md", "corpus/")

env = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
       "PATH": os.environ["PATH"], "HOME": os.environ.get("HOME", "/tmp")}

# Walk every revision that touches the authority scope, and grep its authority files.
revs = subprocess.run(["git", "-C", LANE, "rev-list", "--all", "--", *AUTH],
                      capture_output=True, env=env).stdout.decode().split()
print(f"# revisions touching the authority scope: {len(revs)}")

hits = collections.Counter()
examples = {}
checked = 0
for r in revs:
    p = subprocess.run(["git", "-C", LANE, "grep", "-I", "-n", "-E",
                        r"[A-Za-z0-9._/@+~-]{4,}/[A-Za-z0-9._/@+~-]*\\.([^A-Za-z0-9._/@+~-]|$)",
                        r, "--", *AUTH], capture_output=True, env=env)
    checked += 1
    for line in p.stdout.split(b"\n"):
        if not line.strip():
            continue
        try:
            meta, content = line.split(b"\t", 1)
        except ValueError:
            continue
        fn, ln = meta.split(b":", 1)
        for m in RE.finditer(content):
            g = m.group(0)
            hits[g] += 1
            key = g
            if key not in examples:
                examples[key] = (r[:12], fn.decode() + ":" + ln.decode(),
                                 content.decode("utf-8", "replace").strip()[:220])

print(f"# revisions grepped: {checked}")
print(f"# distinct path-at-sentence-end runs in the authority scope: {len(hits)}")
print(f"# total occurrences: {sum(hits.values())}")
print()
print("=== top 40 by frequency ===")
for g, c in hits.most_common(40):
    ex = examples[g]
    print(f"  {c:6d}  {g.decode()!r}")
    print(f"          first seen {ex[0]} at {ex[1]}")
    print(f"          ...{ex[2][:190]}...")

json.dump({"distinct": len(hits), "total": sum(hits.values()),
           "top": [[g.decode(), c] for g, c in hits.most_common(200)],
           "examples": {g.decode(): v for g, v in examples.items()}},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth_sentence_end.json"), "w"), indent=1)
