#!/usr/bin/env python3
"""S87ScoutShapes — TQ1 shape scanner.

For every committed occurrence of a `.ufo/quarantine/...` path in the AUTHORITY scope
(SKILL.md, LOG.md, SCORECARD.md, corpus/ — the counter's AUTHORITY tuple) and in the whole repo, report the
exact bytes that follow the path (so a "sentence-final period" is distinguished from "backtick", "comma", "tab",
"semicolon", "ellipsis").

Also reports the L06 TOKEN shape separately: the counter's `_declared` needs the TOKEN
(tests/vault/vadv54-run/p/p6repo/.git) to be a whole path on the same line, and the m16 clause is `_whole`'s
sentence-ending punctuation disjunct — so the shape that matters is "a path followed by . , ; : then a
non-path byte".

Read-only.
"""
import subprocess, re, os, json, collections

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")
QPAT = re.compile(rb"\.ufo/quarantine/[^\s`\"]*")
TOKPAT = re.compile(rb"tests/vault/vadv54-run/p/p6repo/\.git")


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], capture_output=True)


def scan(paths, label):
    rows = []
    p = git("grep", "-n", "-z", "--no-color", "-I", "-e", ".ufo/quarantine/", "--", *paths)
    # -z output: "<file>\0<line>\0<content>\0" triples
    f = p.stdout.split(b"\0")
    for i in range(0, len(f) - 2, 3):
        fn, ln, content = f[i], f[i + 1], f[i + 2]
        if not fn or not ln:
            continue
        for m in QPAT.finditer(content):
            s, e = m.span()
            nxt = content[e:e + 3]
            rows.append({
                "file": fn.decode(), "line": int(ln),
                "path": m.group(0).decode("utf-8", "replace"),
                "next_bytes": nxt.decode("utf-8", "replace"),
                "next_hex": nxt.hex(),
                "sentence_end_period": bool(nxt[:1] == b"." and (len(nxt) < 2 or nxt[1] not in PATHCH)),
                "punct_disjunct_whole": bool(
                    nxt[:1] in (b".", b",", b";", b":")
                    and (len(nxt) < 2 or nxt[1] not in PATHCH)),
            })
    print(f"=== {label}: {len(rows)} quarantine-path occurrences ===")
    cnt = collections.Counter(r["next_bytes"][:1] for r in rows)
    print("first-byte histogram:", {repr(k): v for k, v in cnt.most_common()})
    for r in rows:
        if r["sentence_end_period"]:
            print("  SENTENCE-END-PERIOD:", r["file"] + ":" + str(r["line"]),
                  "path=" + r["path"], "next=" + repr(r["next_bytes"]))
    return rows


auth = scan(["SKILL.md", "LOG.md", "SCORECARD.md", "corpus"], "AUTHORITY scope (SKILL/LOG/SCORECARD/corpus)")
allr = scan(["."], "WHOLE repo (tracked)")
print()
print("=== summary ===")
print("authority occurrences:", len(auth))
print("authority occurrences with a sentence-final period after the path:",
      sum(1 for r in auth if r["sentence_end_period"]))
print("whole-repo occurrences:", len(allr))
print("whole-repo occurrences with a sentence-final period after the path:",
      sum(1 for r in allr if r["sentence_end_period"]))
print()
print("=== AUTHORITY occurrences in full (for quoting) ===")
for r in auth:
    print(f"  {r['file']}:{r['line']}  path={r['path']}  next={r['next_bytes']!r}  "
          f"punct_whole={r['punct_disjunct_whole']}")

# The L06 TOKEN shape across the authority scope.
print()
print("=== L06 TOKEN (tests/vault/vadv54-run/p/p6repo/.git) occurrences in AUTHORITY scope ===")
p = git("grep", "-n", "-z", "--no-color", "-I", "-e", "tests/vault/vadv54-run/p/p6repo/.git",
        "--", "SKILL.md", "LOG.md", "SCORECARD.md", "corpus")
f = p.stdout.split(b"\0")
for i in range(0, len(f) - 2, 3):
    fn, ln, content = f[i], f[i + 1], f[i + 2]
    if not fn or not ln:
        continue
    for m in TOKPAT.finditer(content):
        nxt = content[m.end():m.end() + 3]
        print(f"  {fn.decode()}:{ln.decode()}  next={nxt.decode('utf-8','replace')!r}  "
              f"hex={nxt.hex()}  punct_whole={bool(nxt[:1] in (b'.', b',', b';', b':') and (len(nxt) < 2 or nxt[1] not in PATHCH))}")

json.dump({"authority": auth, "whole_repo": allr},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tq1_scan.json"), "w"), indent=1)
