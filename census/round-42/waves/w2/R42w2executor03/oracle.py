#!/usr/bin/env python3
"""R42w2executor03 held-out oracle for tools/souji-freeze-check.py.

Independent re-implementation derived ONLY from the docstring text of census/round-42/c2-counter.py
(lines 1-57) and the docstring of tools/souji-freeze-check.py (lines 2-29).  No tool code was read.
It works on a scenario *spec* (a commit timeline model), never by asking git, so it cannot share a
git-level bug with the tool.

  python3 -B oracle.py --seed 4242 --n 300 --scratch DIR [--tool PATH] [--out results.json]

Scenario = (timeline of commits on main, optional side branch commit, preregistration text).
Oracle(scn) -> (exit, Counter{(claim, CLASS)}, claims_n, details{'HEADING-MALFORMED':[n..], 'KEY-DUPLICATE':[key..]}).

Oracle reading of the docstrings (each choice that the docstrings do not pin is tagged `amb:` in the
scenario and reported separately):
  * lines are split on \\n, a trailing \\r is a line terminator (CRLF files)
  * `Round: <digits>` at column 0 anywhere; missing -> FIELD-MISSING C0
  * a claim opens at `## C<digits>` + (space | EOL); a column-0 `## ` line (not `###`) closes the open claim
    (this includes malformed `## c1`, `## C 1`, but NOT `##C1`, which does not start with `## `)
  * key line: column 0 `Key:` then optional blanks, value, trailing blanks stripped
  * Base: exactly 40 lowercase hex naming a commit that is an ancestor of FREEZE-REV, else BASE-UNRESOLVED /
    BASE-NOT-ANCESTOR (side-branch commit = not ancestor)
  * Counter/Population: `<path> sha256=<64hex>`; FREEZE-REV blob: missing -> *-MISSING, symlink -> *-SYMLINK ALONE,
    digest mismatch -> *-DIGEST, population blank -> POPULATION-EMPTY, blob at --rev differs from blob at
    FREEZE-REV (content, kind, deleted) -> FROZEN-EDITED
  * Control: path; missing at FREEZE-REV -> CONTROL-MISSING; red iff it has >=1 `EXIT=<n>` line and every n != 0
    else CONTROL-NOT-RED; edited at --rev -> FROZEN-EDITED
  * DISPATCH-BEFORE-FREEZE (C0): every file existing at --rev under .ufo/waves/round-<N>/ (any depth) whose
    basename contains `-dispatch` or `.ready` or ends `-spec.json` / `-results.json` and whose first add is
    at FREEZE-REV or earlier on main; one finding per file
  * exits: 0 no findings, 1 findings, 2 refusal (unresolvable --rev, non-40hex --rev, PATH absent at --rev)
Known oracle gaps are listed in the report.
"""
import argparse
import collections
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys

KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")
HEX = "0123456789abcdef"


def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------------------- oracle
def replay(commits, upto):
    st = {}
    for i in range(upto + 1):
        for p, e in commits[i].items():
            if e is None:
                st.pop(p, None)
            else:
                st[p] = e
    return st


def first_add(commits, path):
    for i, c in enumerate(commits):
        if c.get(path) is not None:
            return i
    return None


def heading_like(line):
    if not line.startswith("##") or line.startswith("###"):
        return False
    r = line[2:].lstrip(" ")
    if r[:1] not in ("C", "c") or not r[:1]:
        return False
    r = r[1:].lstrip(" ")
    return r[:1] in tuple("0123456789")


VALID_HEAD = re.compile(r"^## C([0-9]+)(?: |$)")


CFGS = {
    # docstring-literal reading, every undefined point taken in its plainest meaning
    "literal": dict(malformed_closes=False, pop_max_blank_nonblank=0, red_rule="all-exit",
                    dispatch_deleted=False, control_edit=True),
    # literal + three behaviours the docstrings leave open, adopted from the tool's observable output
    "calib": dict(malformed_closes=True, pop_max_blank_nonblank=1, red_rule="last-line",
                  dispatch_deleted=True, control_edit=True),
    # calib + control edits are not FROZEN-EDITED
    "calib-noctl": dict(malformed_closes=True, pop_max_blank_nonblank=1, red_rule="last-line",
                        dispatch_deleted=True, control_edit=False),
    # calib-noctl + malformed Counter/Population values: path = text before ` sha256=`, no digest (=> -DIGEST)
    "calib-full": dict(malformed_closes=True, pop_max_blank_nonblank=1, red_rule="last-line",
                       dispatch_deleted=True, control_edit=False, malformed_value=True),
}


def red(content, rule):
    ls = content.replace("\r\n", "\n").split("\n")
    if rule == "last-line":
        ne = [x for x in ls if x.strip() != ""]
        m = re.fullmatch(r"EXIT=([0-9]+)", ne[-1]) if ne else None
        return bool(m) and int(m.group(1)) != 0
    codes = [int(m.group(1)) for m in (re.fullmatch(r"EXIT=([0-9]+)", ln) for ln in ls) if m]
    return bool(codes) and all(c != 0 for c in codes)


def oracle(scn, cfg):
    kout = collections.Counter()
    if scn["refusal"]:
        return 2, collections.Counter(), None, {}, False, kout
    commits, f, t = scn["commits"], scn["f"], scn["t"]
    S, T = replay(commits, f), replay(commits, scn["rev_idx"])
    text = scn["text"]
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    out = collections.Counter()
    det = {"HEADING-MALFORMED": [], "KEY-DUPLICATE": []}
    undet = False

    def add(label, cls, key=""):
        out[(label, cls)] += 1
        kout[(cls, key)] += 1

    rnd = None
    for ln in lines:
        m = re.fullmatch(r"Round:[ \t]*([0-9]+)[ \t]*", ln)
        if m:
            rnd = m.group(1)
            break
    if rnd is None:
        add("C0", "FIELD-MISSING", "Round")
    claims, cur = [], None
    for i, ln in enumerate(lines):
        if heading_like(ln):
            m = VALID_HEAD.match(ln)
            if m:
                cur = ("C" + m.group(1), [])
                claims.append(cur)
                continue
            add("C0", "HEADING-MALFORMED")
            det["HEADING-MALFORMED"].append(i + 1)
            if cfg["malformed_closes"] or ln.startswith("## "):
                cur = None
            continue
        if ln.startswith("## "):
            cur = None
            continue
        if cur is not None:
            cur[1].append(ln)
    if not claims:
        add("C0", "NO-CLAIMS")
    for label, block in claims:
        for key in KEYS:
            vals = []
            for ln in block:
                m = re.fullmatch(key + r":[ \t]*(.*?)[ \t]*", ln)
                if m:
                    vals.append(m.group(1))
            if not vals:
                add(label, "FIELD-MISSING", key)
                continue
            if len(vals) > 1:
                add(label, "KEY-DUPLICATE", key)
                det["KEY-DUPLICATE"].append(key)
                continue
            v = vals[0]
            if v == "":
                add(label, "FIELD-EMPTY", key)
                continue
            if key == "Base":
                if not re.fullmatch("[0-9a-f]{40}", v) or v not in scn["shas"]:
                    add(label, "BASE-UNRESOLVED")
                else:
                    br, idx = scn["shas"][v]
                    if br != "main" or idx >= f:
                        add(label, "BASE-NOT-ANCESTOR")
            elif key in ("Counter", "Population"):
                m = re.fullmatch(r"(.+?)[ \t]+sha256=([0-9a-f]{64})", v)
                up = key.upper()
                if not m:
                    if not cfg.get("malformed_value"):
                        undet = True
                        continue
                    m2 = re.match(r"(.+?)[ \t]+sha256=", v)
                    path, dg = (m2.group(1) if m2 else v), None
                else:
                    path, dg = m.group(1), m.group(2)
                e = S.get(path)
                if e is None:
                    add(label, up + "-MISSING")
                    continue
                if e[0] == "l":
                    add(label, up + "-SYMLINK")
                    continue
                if dg is None or sha256(e[1]) != dg:
                    add(label, up + "-DIGEST")
                if key == "Population" and len([x for x in e[1].split("\n") if x.strip()]) <= cfg["pop_max_blank_nonblank"] \
                        and (e[1].strip() == "" or cfg["pop_max_blank_nonblank"] >= 1):
                    add(label, "POPULATION-EMPTY")
                if T.get(path) != e:
                    add(label, "FROZEN-EDITED", key.lower())
            elif key == "Control":
                e = S.get(v)
                if e is None:
                    add(label, "CONTROL-MISSING")
                    continue
                if e[0] == "l" or not red(e[1], cfg["red_rule"]):
                    add(label, "CONTROL-NOT-RED")
                if cfg["control_edit"] and T.get(v) != e:
                    add(label, "FROZEN-EDITED", "control")
    if rnd is not None:
        pre = ".ufo/waves/round-%s/" % rnd
        universe = set(p for c in commits[:scn["rev_idx"] + 1] for p in c) if cfg["dispatch_deleted"] else set(T)
        for path in universe:
            if not path.startswith(pre):
                continue
            b = path.rsplit("/", 1)[-1]
            if "-dispatch" in b or ".ready" in b or b.endswith("-spec.json") or b.endswith("-results.json"):
                fa = first_add(commits, path)
                if fa is not None and fa <= f:
                    add("C0", "DISPATCH-BEFORE-FREEZE")
    rc = 1 if sum(out.values()) else 0
    return rc, out, len(claims), det, undet, kout


# ------------------------------------------------------------------------------------- generator
CTRL_BODIES = {
    "red": "SUMMARY items=2 corrected=0\nEXIT=1\n",
    "green": "SUMMARY items=2 corrected=2\nEXIT=0\n",
    "none": "SUMMARY items=2\n",
    "red3": "SUMMARY x\nEXIT=3\n",
}
DISPATCH_NAMES = [
    ("w1-dispatch-attempts.txt", 1), ("w1.ready.dispatched", 1), ("w1-spec.json", 1), ("w1-results.json", 1),
    ("notes.md", 0), ("sub/dir/w2-dispatch.md", 1), ("w1.ready", 1), ("w1-dispatches.txt", 1), ("x.ready", 1),
    ("dispatch.txt", 0), ("w1-spec.json.bak", 0), ("spec.json", 0), ("w1-ready", 0), ("results.json", 0),
    ("a-results.jsonl", 0), ("deep/er/w3-results.json", 1), ("w1-dispatch", 1),
]
MALFORMED = ["##C%d", "## c%d", "## C %d", "## C%dx", "## C%d:", "##  C%d", "## C%d\tx", "##C %d", "## c %d tail",
             "## C%d\u2014title"]  # last one is *valid-ish*? ("C<d>" followed by an em dash => malformed)
SPECIAL_STYLES = [
    ("census/\u00fcn\u00ef/c%d counter.py", "census/\u00fcn\u00ef/c%d pop.tsv", "census/\u00fcn\u00ef/c%d control.txt"),
    ("census/c[%d]-counter.py", "census/c[%d]-pop.tsv", "census/c[%d]-control.txt"),
    ("census/c%d*counter.py", "census/c%d*pop.tsv", "census/c%d*control.txt"),
    ("census/c%d's counter.py", "census/c%d's pop.tsv", "census/c%d's control.txt"),
    ('census/c%d"q counter.py', 'census/c%d"q pop.tsv', 'census/c%d"q control.txt'),
    ("-lead/c%d counter.py", "-lead/c%d pop.tsv", "-lead/c%d control.txt"),
    ("census/c%d  dbl counter.py", "census/c%d  dbl pop.tsv", "census/c%d  dbl control.txt"),
    ("census/c%d?.py", "census/c%d?.tsv", "census/c%d?.txt"),
    ("census/sub dir/c%d counter.py", "census/sub dir/c%d pop.tsv", "census/sub dir/c%d control.txt"),
]


def mk_key(rng, key, value, tags):
    r = rng.random()
    if r < 0.72:
        return "%s: %s" % (key, value)
    if r < 0.84:
        return "%s:   %s   " % (key, value)
    if r < 0.92:
        return "%s: %s\t" % (key, value)
    if r < 0.96:
        return "%s:\t%s" % (key, value)
    tags.add("amb:nospace")
    return "%s:%s" % (key, value)


PROSE = ["Predicate: reads the thing.", "Do-nothing control: controls/x.txt (x).", "Sourced: S259.", "",
         "Note: free text.", "### Sub heading C1", "Baseline: not a key", "Counters: not a key", "- Base: bullet",
         " Base: indented", "#C1", "Round: still prose? no", "Kill-switch: no"]


def gen(seed, i):
    rng = random.Random("%s:%d" % (seed, i))
    tags = set()
    scn = {"i": i, "seed": seed}
    n_pre, n_post = rng.choice([0, 0, 1, 2]), rng.choice([0, 1, 1, 2, 3])
    f = n_pre + 1
    t = f + n_post
    commits = [dict() for _ in range(t + 1)]
    commits[0]["README.md"] = ("f", "readme\n")
    paths = collections.defaultdict(list)

    def mut(c, s):
        return s + c if c.count("EXIT=") else c + s

    def lifecycle(path, content, allow_sym, tagname):
        r = rng.random()
        if r < 0.40:
            a = 0
        elif r < 0.55 and n_pre:
            a = rng.randint(1, n_pre)
        elif r < 0.90 or t == f:
            a = f
        else:
            a = rng.randint(f + 1, t)
            tags.add("late-add:" + tagname)
        if allow_sym and rng.random() < 0.09:
            commits[a][path] = ("l", rng.choice(["README.md", "../elsewhere.py", "nonexistent-target"]))
            tags.add("symlink:" + tagname)
        else:
            commits[a][path] = ("f", content)
        lo = a + 1
        if lo <= f and rng.random() < 0.2:
            j = rng.randint(lo, f)
            commits[j][path] = ("f", mut(content, "pre-edit %d\n" % j))
        if t > max(a, f) and rng.random() < 0.28:
            j = rng.randint(max(a, f) + 1, t)
            r2 = rng.random()
            if r2 < 0.14:
                commits[j][path] = None
                tags.add("deleted-at-tip:" + tagname)
            elif r2 < 0.22:
                commits[j][path] = ("l", "README.md")
                tags.add("amb:file-to-symlink")
            elif r2 < 0.30 and j < t:
                prev_e = replay(commits, j - 1).get(path)
                commits[j][path] = ("f", mut(content, "temp\n"))
                commits[t][path] = prev_e
                tags.add("edit-revert")
            else:
                commits[j][path] = ("f", mut(content, "post-edit %d\n" % j))
                tags.add("edited:" + tagname)

    nclaims = 0 if rng.random() < 0.06 else rng.randint(1, 4)
    nums = rng.sample(range(1, 13), max(nclaims, 1))
    if nclaims >= 2 and rng.random() < 0.03:
        nums[1] = nums[0]
        tags.add("amb:dup-label")
    cl = []
    prev = None
    for n in nums[:nclaims]:
        sp = rng.random() < 0.3
        c = {"n": n}
        if prev and rng.random() < 0.05:
            c.update({k: prev[k] for k in ("counter", "pop", "control")})
            tags.add("shared-paths")
        else:
            if rng.random() < 0.13:
                st = rng.choice(SPECIAL_STYLES)
                tags.add("special-path")
                c["counter"], c["pop"], c["control"] = [s % n for s in st]
            else:
                c["counter"] = ("census/r9/c%d counter.py" if sp else "census/round-9/c%d-counter.py") % n
                c["pop"] = ("census/r9/c%d pop.tsv" if sp else "census/round-9/c%d-pop.tsv") % n
                c["control"] = ("census/r9/controls/c%d control.txt" if sp else "census/round-9/controls/c%d-control.txt") % n
            if rng.random() < 0.04:
                c["counter"] = "census/ld%d/counter.py" % n
                commits[0]["census/ld%d" % n] = ("l", "../real")
                tags.add("symlink-dir-component")
            else:
                lifecycle(c["counter"], "# counter %d\nprint(1)\n" % n, True, "counter")
            pk = rng.choice(["normal", "normal", "normal", "empty", "empty", "ws", "hdr"])
            body = {"normal": "id\tname\n1\ta\n2\tb\n", "empty": "", "ws": "\n", "hdr": "id\tname\n"}[pk]
            if pk in ("ws", "hdr"):
                tags.add("amb:pop-" + pk)
            lifecycle(c["pop"], body, True, "pop")
            ck = rng.choice(["red", "red", "red", "green", "none", "red3", "multi", "crlf"])
            if ck == "multi":
                body = rng.choice(["EXIT=1\nEXIT=0\n", "EXIT=0\nEXIT=1\n"])
                tags.add("amb:control-multi-exit")
            elif ck == "crlf":
                body = "SUMMARY a\r\nEXIT=1\r\n"
                tags.add("amb:control-crlf")
            else:
                body = CTRL_BODIES[ck]
            lifecycle(c["control"], body, False, "control")
        bk = rng.random()
        c["base"] = ("ok" if bk < 0.78 else "unknown" if bk < 0.84 else "side" if bk < 0.90 else
                     "nonhex" if bk < 0.94 else "abbrev")
        if c["base"] in ("nonhex", "abbrev"):
            tags.add("amb:base-" + c["base"])
        cl.append(c)
        prev = c
    side = any(c["base"] == "side" for c in cl)

    # dispatch files
    rnd = rng.choice([42, 7, 41])
    missing_round = rng.random() < 0.08
    rn = rnd
    dd = []
    for name, _red in DISPATCH_NAMES:
        if rng.random() < 0.28:
            d = rng.choice(["round-%d" % rn] * 6 + ["round-%d" % (rn + 1), "round-%d0" % rn, "round-%dx" % rn])
            if rng.random() < 0.04:
                name = name.replace("dispatch", "Dispatch").replace("ready", "READY")
                tags.add("amb:case")
            path = ".ufo/waves/%s/%s" % (d, name)
            a = rng.randint(0, t)
            if a == 0 and rng.random() < 0.7:
                a = f
            if rng.random() < 0.04:
                commits[a][path] = ("l", "README.md")
                tags.add("amb:dispatch-symlink")
            else:
                commits[a][path] = ("f", "dispatch data %s\n" % path)
            if rng.random() < 0.04 and a < t:
                commits[rng.randint(a + 1, t)][path] = None
                tags.add("amb:dispatch-deleted")
            dd.append(path)
    merged_list = []
    if t >= 2 and rng.random() < 0.18:
        for _k in range(rng.randint(1, 2)):
            name = rng.choice([n for n, red_ in DISPATCH_NAMES if red_ and "/" not in n])
            b = rng.randint(0, t - 1)
            m = rng.randint(b + 1, t)
            if m == f:
                continue
            path = ".ufo/waves/round-%d/%s" % (rn, name)
            if any(path in c for c in commits):
                continue
            commits[m][path] = ("f", "merged dispatch data %s\n" % path)
            merged_list.append((b, m, path))
            tags.add("merged-dispatch:" + ("pre" if m < f else "post") + ("-branched-pre" if b < f else ""))

    # prereg text
    eol = "\r\n" if rng.random() < 0.3 else "\n"
    L = ["# prereg", "Written by tests."]
    if not missing_round:
        if rng.random() < 0.9:
            L.append("Round: %d" % rnd)
        else:
            L.append("Round:%d" % rnd)
            tags.add("amb:nospace")
        if rng.random() < 0.04:
            L.append("Round: %d" % (rnd + 1))
            tags.add("amb:two-rounds")
    else:
        tags.add("round-missing")
        if rng.random() < 0.5:
            L.append("round: %d" % rnd)
        if rng.random() < 0.3:
            L.append("Round: abc")
            tags.add("amb:round-nondigit")
    if rng.random() < 0.1:
        L += ["Base: %s" % ("0" * 40), "Counter: decoy sha256=" + "0" * 64]
        tags.add("preamble-decoy")
    L.append("")
    blocks = []
    for c in cl:
        B = []
        if rng.random() < 0.15:
            h = rng.choice(MALFORMED) % c["n"]
            B.append(h)
            tags.add("malformed-heading")
        else:
            B.append(rng.choice(["## C%d", "## C%d", "## C%d - title", "## C%d ", "## C%d \u2014 calibration"]) % c["n"])
        body = []
        order = list(KEYS)
        rng.shuffle(order)
        for key in order:
            r = rng.random()
            if key == "Base":
                bk = c["base"]
                if bk == "ok":
                    val = "@@BASE@@"
                elif bk == "side":
                    val = "@@SIDE@@"
                elif bk == "unknown":
                    val = "".join(rng.choice(HEX) for _ in range(40))
                elif bk == "nonhex":
                    val = rng.choice(["main", "HEAD~1", "master"])
                else:
                    val = "@@ABBREV@@"
            elif key in ("Counter", "Population"):
                val = "@@%s:%s@@" % (key, c["counter" if key == "Counter" else "pop"])
            elif key == "Control":
                val = c["control"]
            else:
                val = {"Target": "SUMMARY ok=1 (exit 0)", "Kill": "any finding"}[key]
            if r < 0.06:
                tags.add("key-missing")
                if rng.random() < 0.5:
                    body.append(rng.choice(["Baseline: x", "- %s: %s" % (key, val), " %s: %s" % (key, val),
                                            "%s : %s" % (key, val), "%s: %s" % (key.lower(), val)]) if key == "Base"
                                else rng.choice(["- %s: %s" % (key, val), " %s: %s" % (key, val)]))
                continue
            if r < 0.10:
                tags.add("key-empty")
                body.append(rng.choice(["%s:", "%s:   ", "%s:\t"]) % key)
                continue
            if r < 0.17:
                tags.add("key-dup")
                body.append(mk_key(rng, key, val, tags))
                body.append(rng.choice(PROSE))
                if rng.random() < 0.5:
                    body.append(mk_key(rng, key, val, tags))
                else:
                    body.append(mk_key(rng, key, "other-" + val, tags))
                continue
            body.append(mk_key(rng, key, val, tags))
            if rng.random() < 0.35:
                body.append(rng.choice(PROSE))
        B += body
        B.append("")
        blocks.append(B)
    for B in blocks:
        L += B
        if rng.random() < 0.12:
            L.append(rng.choice(MALFORMED) % rng.randint(20, 29))
            L.append("")
            tags.add("stray-malformed")
    if rng.random() < 0.4:
        L += ["## Frontier step (not a claim)", "Base: %s" % ("1" * 40), "Counter: z sha256=" + "1" * 64, ""]
        tags.add("tail-section")
    text = eol.join(L)
    if rng.random() < 0.85:
        text += eol
    if eol == "\r\n":
        tags.add("crlf")

    # refusal / args
    refusal, prereg_arg, rev_mode = None, None, "tip"
    pp = rng.random()
    if pp < 0.10:
        prereg_path, decoy = rng.choice([("census/pre[ab].txt", "census/prea.txt"), ("census/pre*.txt", "census/pre-x.txt"),
                                         ("census/pre?.txt", "census/pre1.txt"), ("census/pr\u00e9 reg.txt", None),
                                         ("census/pre[ab].txt", "census/preb.txt")])
        tags.add("special-prereg-path")
        if decoy:
            commits[0][decoy] = ("f", "decoy prereg\n")
            tags.add("prereg-glob-decoy")
    else:
        prereg_path = rng.choice(["census/round-9/preregistration.txt", "census/r9/pre reg.txt"])
    r = rng.random()
    if r < 0.02:
        refusal, rev_mode = "rev-unknown", "zeros"
    elif r < 0.035:
        refusal, rev_mode = "rev-short", "short"
    elif r < 0.05:
        refusal, prereg_arg = "prereg-absent", "census/nope/absent.txt"
    if refusal:
        tags.add("refusal:" + refusal)
    commits[f][prereg_path] = ("f", "@@TEXT@@")
    rev_idx = t
    pe = rng.random()
    if t >= f + 1 and pe < 0.08:
        commits[rng.randint(f + 1, t)][prereg_path] = ("f", "@@TEXT2@@")
        tags.add("prereg-edited-post")
    elif t >= f + 2 and pe < 0.12:
        j = rng.randint(f + 1, t - 1)
        commits[j][prereg_path] = None
        commits[rng.randint(j + 1, t)][prereg_path] = ("f", "@@TEXT@@")
        tags.add("prereg-deleted-readded")
    elif t > f and pe < 0.35:
        rev_idx = rng.randint(f, t)
        if rev_idx != t:
            tags.add("rev-mid")
    scn.update(dict(commits=commits, f=f, t=t, text=text, side=side, tags=sorted(tags), refusal=bool(refusal),
                    refusal_kind=refusal, prereg_path=prereg_path, prereg_arg=prereg_arg or prereg_path,
                    rev_mode=rev_mode, claims=cl, rev_idx=rev_idx, merged=merged_list))
    scn["_rng"] = rng
    return scn


def resolve_text(scn, shas_by_idx, side_sha):
    """Fill @@..@@ tokens at build time (needs real commit ids and the model's freeze state)."""
    rng = scn["_rng"]
    S = replay(scn["commits"], scn["f"])
    text = scn["text"]
    base = shas_by_idx[rng.randint(0, scn["f"] - 1)]
    text = text.replace("@@BASE@@", base)
    text = text.replace("@@SIDE@@", side_sha or ("0" * 40))
    text = text.replace("@@ABBREV@@", base[:12])

    def rep(m):
        key, path = m.group(1), m.group(2)
        e = S.get(path)
        mode = rng.random()
        if e is None:
            dg = "".join(rng.choice(HEX) for _ in range(64))
        elif e[0] == "l":
            dg = rng.choice([sha256(e[1]), sha256("readme\n"), "".join(rng.choice(HEX) for _ in range(64))])
        elif mode < 0.76:
            dg = sha256(e[1])
        else:
            dg = "".join(rng.choice(HEX) for _ in range(64))
        sep = " " if rng.random() < 0.97 else "\t"
        if sep == "\t":
            scn["tags"].append("amb:tabsep")
        odd = rng.random()
        if odd < 0.025:
            kind = rng.choice(["nodigest", "upper", "short", "trail"])
            scn["tags"].append("amb:value-" + kind)
            return {"nodigest": path, "upper": "%s%ssha256=%s" % (path, sep, dg.upper()),
                    "short": "%s%ssha256=%s" % (path, sep, dg[:63]),
                    "trail": "%s%ssha256=%s extra" % (path, sep, dg)}[kind]
        return "%s%ssha256=%s" % (path, sep, dg)
    text = re.sub(r"@@(Counter|Population):([^@]*)@@", rep, text)
    return text


# --------------------------------------------------------------------------------------- driver
def genv(scratch):
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "TMPDIR": scratch, "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "HOME": scratch,
            "GIT_AUTHOR_NAME": "fx", "GIT_AUTHOR_EMAIL": "fx@example.invalid",
            "GIT_COMMITTER_NAME": "fx", "GIT_COMMITTER_EMAIL": "fx@example.invalid",
            "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}


def g(D, scratch, *args, check=True):
    p = subprocess.run(["git", "-C", D] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, env=genv(scratch))
    if check and p.returncode:
        raise RuntimeError("git %s: %s" % (args, p.stderr))
    return p.stdout.strip()


def build(scn, scratch):
    D = os.path.join(scratch, "s%04d" % scn["i"])
    os.makedirs(D)
    g(D, scratch, "init", "-q", "-b", "main")
    top = g(D, scratch, "rev-parse", "--show-toplevel")
    assert os.path.realpath(top) == os.path.realpath(D), (top, D)
    shas, side_sha = [], None
    merged = scn.get("merged", [])  # (branch_point b, merge_after m, path)
    skip = collections.defaultdict(set)
    for b, m, path in merged:
        skip[m].add(path)
    texts = {}
    for i, ch in enumerate(scn["commits"]):
        for path, e in ch.items():
            if path in skip[i]:
                continue
            full = os.path.join(D, path)
            if e is None:
                if os.path.lexists(full):
                    os.remove(full)
                continue
            if os.path.lexists(full):
                os.remove(full)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            if e[0] == "l":
                os.symlink(e[1], full)
            else:
                body = e[1]
                if body in ("@@TEXT@@", "@@TEXT2@@"):
                    if "final_text" not in scn:
                        scn["final_text"] = resolve_text(scn, shas, side_sha)
                    body = scn["final_text"]
                    if e[1] == "@@TEXT2@@":
                        eol = "\r\n" if "\r\n" in body else "\n"
                        body = body + eol + "Postscript: edited after freeze" + eol
                    texts[i] = body
                with open(full, "wb") as fh:
                    fh.write(body.encode("utf-8"))
        g(D, scratch, "add", "-A")
        g(D, scratch, "commit", "-q", "--allow-empty", "-m", "c%d" % i)
        shas.append(g(D, scratch, "rev-parse", "HEAD"))
        if i == 0 and scn["side"]:
            g(D, scratch, "checkout", "-q", "-b", "side")
            with open(os.path.join(D, "side.txt"), "w") as fh:
                fh.write("side\n")
            g(D, scratch, "add", "-A")
            g(D, scratch, "commit", "-q", "-m", "side")
            side_sha = g(D, scratch, "rev-parse", "HEAD")
            g(D, scratch, "checkout", "-q", "main")
        for k, (b, m, path) in enumerate(merged):
            if b == i:
                g(D, scratch, "checkout", "-q", "-b", "mb%d" % k)
                full = os.path.join(D, path)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "wb") as fh:
                    fh.write(scn["commits"][m][path][1].encode("utf-8"))
                g(D, scratch, "add", "-A")
                g(D, scratch, "commit", "-q", "-m", "branch %d" % k)
                g(D, scratch, "checkout", "-q", "main")
        merged_now = [k for k, (b, m, path) in enumerate(merged) if m == i]
        for k in merged_now:
            g(D, scratch, "merge", "-q", "--no-ff", "-m", "merge %d" % k, "mb%d" % k)
        if merged_now:
            shas[-1] = g(D, scratch, "rev-parse", "HEAD")
    scn["text"] = texts[max(k for k in texts if k <= scn["rev_idx"])]
    scn["shas"] = {s: ("main", k) for k, s in enumerate(shas)}
    if side_sha:
        scn["shas"][side_sha] = ("side", 0)
    scn["rev_sha"] = shas[scn["rev_idx"]]
    return D, shas[scn["rev_idx"]]


def run_tool(tool, D, rev, prereg, scratch):
    p = subprocess.run(["python3", "-B", tool, "--root", D, "--prereg", prereg, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=genv(scratch), timeout=120)
    fnd = []
    for ln in p.stdout.splitlines():
        m = re.match(r"^FINDING (\S+) (\S+)(?: (.*))?$", ln)
        if m:
            fnd.append((m.group(1), m.group(2), m.group(3) or ""))
    sm = re.findall(r"^SUMMARY claims=(\d+) findings=(\d+)\s*$", p.stdout, re.M)
    return p.returncode, fnd, (tuple(map(int, sm[-1])) if sm else None), "Traceback" in p.stderr, p.stderr


def tkey(cls, detail):
    d = detail.strip()
    if cls in ("FIELD-MISSING", "FIELD-EMPTY", "KEY-DUPLICATE"):
        return d.split()[0] if d else ""
    if cls == "FROZEN-EDITED":
        low = d.lower()
        for w in ("control", "pop", "counter"):
            if w in low:
                return {"pop": "population"}.get(w, w)
    return ""


def compare(scn, cfg, rc, fnd, summ):
    erc, eout, ecl, edet, undet, kout = oracle(scn, cfg)
    tmul = collections.Counter((c, k) for c, k, _d in fnd)
    tk = collections.Counter((k, tkey(k, d)) for c, k, d in fnd)
    tdet = {"HEADING-MALFORMED": sorted(int(re.search(r"line=(\d+)", d).group(1)) for c, k, d in fnd
                                        if k == "HEADING-MALFORMED" and re.search(r"line=(\d+)", d)),
            "KEY-DUPLICATE": sorted(d.strip() for c, k, d in fnd if k == "KEY-DUPLICATE")}
    odet = {k: sorted(v) for k, v in edet.items()}
    ok_rc = rc == erc
    ok_f = tmul == eout
    ok_sum = (summ is None) if erc == 2 else (summ == (ecl, sum(eout.values())))
    ok_det = (tdet == odet) if erc != 2 else True
    atoms = sorted(["tool+%s/%s" % x for x in (tk - kout).elements()] + ["tool-%s/%s" % x for x in (kout - tk).elements()])
    # (claim,class) multiset diffs are authoritative for ok_f; keyed atoms give the cause label
    return dict(undet=undet, erc=erc, ok_rc=ok_rc, ok_f=ok_f, ok_sum=ok_sum, ok_det=ok_det, atoms=atoms,
                extra=sorted((tmul - eout).elements()), missing=sorted((eout - tmul).elements()),
                esumm=[ecl, sum(eout.values())], odet=odet, tdet=tdet,
                oracle=sorted([list(k) + [v] for k, v in eout.items()]),
                agree=ok_rc and ok_f and ok_sum and ok_det)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="4242")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--tool", default="/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py")
    ap.add_argument("--out", default=None)
    ap.add_argument("--only", default=None, help="comma list of scenario indexes")
    a = ap.parse_args(argv)
    print("SEED %s N %d TOOL %s" % (a.seed, a.n, a.tool))
    os.makedirs(a.scratch, exist_ok=True)
    res = []
    only = set(int(x) for x in a.only.split(",")) if a.only else None
    for i in range(a.n):
        if only is not None and i not in only:
            continue
        scn = gen(a.seed, i)
        D, tip = build(scn, a.scratch)
        rev = {"tip": tip, "zeros": "0" * 40, "short": tip[:10]}[scn["rev_mode"]]
        rc, fnd, summ, crash, err = run_tool(a.tool, D, rev, scn["prereg_arg"], a.scratch)
        r = dict(i=i, tags=scn["tags"], rc=rc, crash=crash, summ=summ, tool_findings=[list(x) for x in fnd],
                 stderr=err[-300:] if rc == 2 or crash else "", prereg=scn["prereg_arg"], f=scn["f"], t=scn["t"],
                 cfg={})
        for name, cfg in CFGS.items():
            r["cfg"][name] = compare(scn, cfg, rc, fnd, summ)
        res.append(r)
        shutil.rmtree(D, ignore_errors=True)
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(res, fh, indent=1)
    for name in CFGS:
        tot = len(res)
        und = [r for r in res if r["cfg"][name]["undet"]]
        dis = [r for r in res if not r["cfg"][name]["agree"] and not r["cfg"][name]["undet"]]
        print("CFG %-12s SCENARIOS %d agree %d disagree %d undetermined %d" %
              (name, tot, tot - len(dis) - len(und), len(dis), len(und)))
        groups = collections.defaultdict(list)
        for r in dis:
            c = r["cfg"][name]
            sig = (("rc %d!=%d" % (r["rc"], c["erc"])) if not c["ok_rc"] else "", tuple(c["atoms"]),
                   "sum" if not c["ok_sum"] else "", "det" if not c["ok_det"] else "")
            groups[sig].append(r["i"])
        for sig, ids in sorted(groups.items(), key=lambda x: -len(x[1]))[:25]:
            print("  GROUP n=%d %s  ex=%s" % (len(ids), sig, ids[:6]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
