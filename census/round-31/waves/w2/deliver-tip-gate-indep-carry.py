#!/usr/bin/env python3
"""Independent re-derivation of the per-round seat-failure carry census.

Different implementation from tools/souji-landing-gate.py:
 - bytes read through one `git cat-file --batch` stream over ls-tree oids;
 - failure detection uses its own regex and also records fenced/table STATUS
   lines the gate excludes, as hidden-failure candidates;
 - carry region = first `## Seat-reported failures` heading to EOF (all later
   headings kept, unlike the gate which stops at each heading);
 - match rule = FULL normalized paragraph must occur in the carry region
   (no ellipsis allowance) AND the containing bullet must hold a carry token.
Stricter than the gate on both axes, so every gate-pass it fails is a case
to inspect, not an automatic defect.
"""
import json
import re
import subprocess
import sys
import unicodedata

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "2c16d018e40db7c23420a2c3bb546b52957bcc25"
ROUNDS = range(13, 31)

ST = re.compile(r"^[#*\s]*STATUS[*]*\s*[:\u2014]\s*(.*)$", re.I)
FAILWORDS = {
    "incomplete", "fail", "failed", "fails", "failing", "failure",
    "blocked", "broken", "partial", "harmed", "red", "unrun", "error",
    "regression", "known",
}
HEAD = re.compile(r"^##\s+Seat-reported failures\b", re.I)
TOKEN = re.compile(r"(?i)\bopen\b|resolved@[0-9a-f]{7,}")
ANYH = re.compile(r"^#{1,6}\s")
LIST = re.compile(r"^([-*+]|\d+\.)\s+")
CONT = re.compile(r"^(\s*$|\s*(```|\||>|<|#{1,6}\s|[-*+]\s|\d+\.\s)|STATUS[*]*\s*[:\u2014])", re.I)


def norm(t):
    t = unicodedata.normalize("NFC", t)
    t = t.replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", t).strip()


def ls_tree():
    out = subprocess.run(
        ["git", "-C", LANE, "ls-tree", "-r", "-z", "--full-tree", REV],
        capture_output=True, check=True).stdout
    tree = {}
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, oid = meta.split()
        tree[path.decode()] = oid.decode()
    return tree


def read_blobs(oids):
    p = subprocess.run(
        ["git", "-C", LANE, "cat-file", "--batch"],
        input="".join(o + "\n" for o in oids).encode(),
        capture_output=True, check=True).stdout
    blobs, i, n = {}, 0, len(oids)
    idx = 0
    while i < len(p):
        nl = p.index(b"\n", i)
        hdr = p[i:nl].split()
        size = int(hdr[2])
        body = p[nl + 1: nl + 1 + size]
        blobs[oids[idx]] = body.decode("utf-8", "replace")
        idx += 1
        i = nl + 1 + size + 1
    return blobs


def reports(tree, n):
    wp = ".ufo/waves/round-%d/" % n
    cp = "census/round-%d/waves/" % n
    chosen = {}
    for pref in (cp, wp):
        for path in tree:
            if path.startswith(pref) and path.endswith(".md"):
                suf = path[len(pref):]
                chosen[suf] = path if pref == wp else chosen.get(suf, path)
    return sorted(chosen.values()), len(chosen)


def failure_lines(text):
    """(lineno, raw, where) where = free|fence|table."""
    out, fence = [], False
    for no, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        m = ST.match(s)
        if not m:
            continue
        w = re.match(r"[*:\u2014\s]*(\S+)", m.group(1))
        word = w.group(1).strip("*:\u2014").lower() if w else ""
        if word not in FAILWORDS:
            continue
        where = "fence" if fence else ("table" if s.startswith("|") else "free")
        out.append((no, raw, where))
    return out


def status_count(text):
    return sum(1 for l in text.splitlines() if ST.match(l.strip()))


def para(lines, i):
    blk = [lines[i]]
    j = i + 1
    while j < len(lines) and lines[j].strip() and not CONT.match(lines[j]):
        blk.append(lines[j])
        j += 1
    return blk


def carry_region(lesson):
    nog = re.sub(r"<!--.*?-->", "", lesson, flags=re.S)
    lines, inside, out, fence = nog.splitlines(), False, [], False
    for l in lines:
        s = l.strip()
        if s.startswith("```"):
            fence = not fence
        if not fence and HEAD.match(s):
            inside = True
            continue
        if inside:
            out.append(l)
    return out


def bullets(region):
    ents = []
    for l in region:
        if ents and l.strip() and not LIST.match(l.strip()):
            ents[-1] += " " + l
        else:
            ents.append(l)
    return [norm(e) for e in ents]


def main():
    tree = ls_tree()
    oids = []
    plan = {}
    for n in ROUNDS:
        reps, nrep = reports(tree, n)
        plan[n] = (reps, nrep)
        for r in reps:
            oids.append(tree[r])
        lp = "corpus/lessons/round-%d.md" % n
        if lp in tree:
            oids.append(tree[lp])
    blobs = read_blobs(oids)
    out = {"rev": REV, "rounds": {}}
    for n in ROUNDS:
        reps, nrep = plan[n]
        lp = "corpus/lessons/round-%d.md" % n
        lesson = blobs[tree[lp]] if lp in tree else ""
        region = carry_region(lesson)
        ents = bullets(region)
        tok_ents = [e for e in ents if TOKEN.search(e)]
        marks = hidden = 0
        uncarried, hidden_unc, stat = [], [], 0
        for r in reps:
            text = blobs[tree[r]]
            stat += status_count(text)
            rl = text.splitlines()
            for no, raw, where in failure_lines(text):
                marks += 1
                blk = para(rl, no - 1)
                full = norm(" ".join(blk))
                hit = any(full and full in e and TOKEN.search(e) for e in tok_ents)
                if where != "free":
                    hidden += 1
                    if not hit:
                        hidden_unc.append({"report": r, "line": no, "where": where,
                                           "text": norm(raw)[:120]})
                    continue
                if not hit:
                    uncarried.append({"report": r, "line": no,
                                      "text": norm(raw)[:160]})
        out["rounds"][n] = {
            "reports": nrep, "checked_reports_paths": reps,
            "status_lines": stat, "markers_all": marks,
            "markers_fenced_or_table": hidden,
            "carry_headings": sum(1 for l in re.sub(r"<!--.*?-->", "", lesson, flags=re.S).splitlines()
                                  if HEAD.match(l.strip())),
            "carry_bullets": len(ents), "carry_bullets_with_token": len(tok_ents),
            "uncarried_strict": uncarried,
            "hidden_uncarried": hidden_unc,
        }
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
