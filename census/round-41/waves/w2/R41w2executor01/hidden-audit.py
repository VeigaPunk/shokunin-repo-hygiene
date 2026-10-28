#!/usr/bin/env python3
"""Hidden-case audit for tools/souji-freeze-check.py (round 41, wave 2, seat R41w2executor01).

Builds scenarios the frozen counter (census/round-41/c2-counter.py) does not hold: opaque per-run random
directory / path / commit-message names, fresh salts in every file, CRLF preregistrations, mixed-failure
claims, absent keys, directory-valued paths, spaces, non-ASCII file names, Round absent, merges, renames.
Each scenario is a scratch git repo; the tool under test is run as the documented CLI and its exit code and
(claim, class) multiset are compared with an expectation derived from the GRAMMAR TEXT in
census/round-41/c2-counter.py's docstring, never from the tool. The oracle below shares no code with the tool.

  python3 -B hidden-audit.py [--tool FILE] [--seed N] [--scratch DIR] [--out FILE] [--only SUBSTR] [--keep]

Tiers: strict   = the documented grammar decides the expectation; a mismatch is a FAIL.
       literal  = the documented class text, read literally, decides it; the tool is allowed to read it otherwise.
       ambig    = the grammar is silent; the expectation is the natural reading; a mismatch is a NOTE.
Exit 0 every strict scenario passes; 1 a strict scenario fails; 2 harness error.
"""
import argparse
import collections
import fnmatch
import hashlib
import json
import os
import random
import secrets
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TIP = "1d41c13574db80fdd9a4bde490b712da7ce2a85f"
SCRATCH = "/fast/scratch/hyaku/souji-r41/R41w2executor01"
KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")
GITENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
          "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
IDENT = {"GIT_AUTHOR_NAME": "fx", "GIT_AUTHOR_EMAIL": "fx@example.invalid",
         "GIT_COMMITTER_NAME": "fx", "GIT_COMMITTER_EMAIL": "fx@example.invalid"}
DECOYS = ["freeze", "prereg", "early dispatch", "fix", "wip", "instruments", "dispatch", "Round 41 freeze",
          "merge", "oops", "ready"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rhex(rnd, n=8):
    return "".join(rnd.choice("0123456789abcdef") for _ in range(n))


def msg(rnd):
    return "%s %s" % (rnd.choice(DECOYS), rhex(rnd, 6))


class Fx:
    def __init__(self, scratch, dirname):
        self.d = os.path.join(scratch, dirname)
        os.makedirs(self.d)
        self.main = "m" + secrets.token_hex(3)
        self.git("init", "-q", "-b", self.main, ".")
        top = self.git("rev-parse", "--show-toplevel")
        if os.path.realpath(top) != os.path.realpath(self.d):
            raise RuntimeError("fixture root mismatch %s != %s" % (top, self.d))

    def env(self, ident=True):
        e = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "TMPDIR": os.path.dirname(self.d)}
        e.update(GITENV)
        if ident:
            e.update(IDENT)
        return e

    def git(self, *args):
        p = subprocess.run(["git", "-C", self.d] + list(args), stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=self.env(), text=True)
        if p.returncode != 0:
            raise RuntimeError("git %s: %s" % (" ".join(args), p.stderr))
        return p.stdout.strip()

    def write(self, rel, data):
        full = os.path.join(self.d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as h:
            h.write(data if isinstance(data, bytes) else data.encode("utf-8"))

    def rm(self, rel):
        os.remove(os.path.join(self.d, rel))

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")


# ---------------------------------------------------------------- specs
def C(num, **kw):
    s = dict(num=num, base="ok", counter="ok", cwrong=False, cedit=None, pop="ok", popc="ok", pwrong=False,
             pedit=None, control="red", target="ok", kill="ok")
    s.update(kw)
    return s


def D(name, when="before", tree=None, sub="w1"):
    return dict(name=name, when=when, tree=tree, sub=sub)


OPTS = dict(eol="\n", round="auto", dfiles=[], root="plain", ppath="plain", raw=None, prereg_edit=False,
            rev_at_freeze=False, rename=False, side_freeze=False, trailer=[], subheader=False, preamble=[],
            rev_override=None, prereg_override=None, root_override=None, expect_exit_override=None)

POP = {"ok": "id\tname\n1\t{s}\n2\t{s}b\n", "header": "id\tname\n", "zero": "", "hblank": "id\tname\n\n \n\t\n",
       "nonl": "id\tname\n1\t{s}"}
CONTROL = {"red": "SUMMARY items=2 corrected=0 {s}\nEXIT={n}\n", "green": "SUMMARY ok {s}\nEXIT=0\n",
           "notlast": "EXIT=1\nSUMMARY after {s}\n", "empty": "", "garbage": "SUMMARY {s}\nEXIT=x\n",
           "crlfred": "SUMMARY {s}\r\nEXIT=3\r\n\r\n", "trailblank": "SUMMARY {s}\nEXIT=2\n\n\n  \n",
           "zeros": "SUMMARY {s}\nEXIT=00\n"}
CONTROL_RED = {"red", "crlfred", "trailblank"}


def fmt_key(k, v, indented=False):
    return ("  " if indented else "") + "%s: %s" % (k, v)


# ---------------------------------------------------------------- oracle (grammar text only)
def oracle(claims, o):
    """-> (exit, [(claim, class)], n_claims). Written from the grammar docstring; shares no code with the tool."""
    f = []
    if o["raw"] is not None:
        return o["raw_expect"]
    if o["rev_override"] or o["prereg_override"] or o["root_override"]:
        return 2, [], len(claims)
    if not claims:
        f.append(("C0", "NO-CLAIMS"))
    for c in claims:
        L = "C%d" % c["num"]
        if o["rev_at_freeze"]:  # the blobs as of the freeze commit: later edits and the v2 text are not visible
            c = dict(c, cedit=None, pedit=None, base="ok" if c["base"] in ("freeze", "desc") else c["base"])
        for key, st in (("Base", c["base"]), ("Counter", c["counter"]), ("Population", c["pop"]),
                        ("Control", c["control"]), ("Target", c["target"]), ("Kill", c["kill"])):
            if st in ("absent", "indented"):
                f.append((L, "FIELD-MISSING"))
        for key, st in (("Target", c["target"]), ("Kill", c["kill"])):
            if st in ("empty", "tabempty"):
                f.append((L, "FIELD-EMPTY"))
        b = c["base"]
        if b in ("unresolved-abbrev", "zero", "tree", "blob", "blank"):
            f.append((L, "BASE-UNRESOLVED"))
        elif b in ("side", "freeze", "desc"):
            f.append((L, "BASE-NOT-ANCESTOR"))
        for kind, st, wrong, edit, prefix in (("Counter", c["counter"], c["cwrong"], c["cedit"], "COUNTER"),
                                              ("Population", c["pop"], c["pwrong"], c["pedit"], "POPULATION")):
            if st in ("missing", "dir", "blank", "late"):
                f.append((L, prefix + "-MISSING"))
            elif st in ("ok", "nosha", "upper", "spaced"):
                if wrong or st == "nosha":
                    f.append((L, prefix + "-DIGEST"))
                if edit in ("modify", "delete"):
                    f.append((L, "FROZEN-EDITED"))
                if kind == "Population":
                    nonblank = [x for x in POP[c["popc"]].replace("\r", "").split("\n") if x.strip()]
                    if len(nonblank) < 2:
                        f.append((L, "POPULATION-EMPTY"))
        cs = c["control"]
        if cs in ("missing", "dir", "blank"):
            f.append((L, "CONTROL-MISSING"))
        elif cs in ("notlast", "empty", "garbage", "green", "zeros"):
            f.append((L, "CONTROL-NOT-RED"))
    if o["round"] not in (None, "auto"):
        for d in o["dfiles"]:
            if d["tree"] is not None and d["tree"] != o["round"]:
                continue
            if not (fnmatch.fnmatchcase(d["name"], "*-dispatch.json") or fnmatch.fnmatchcase(d["name"], "*.ready")):
                continue
            if d["when"] in ("before", "same", "readd", "sideearly") or (d["when"] == "after" and o["rename"]):
                f.append(("C0", "DISPATCH-BEFORE-FREEZE"))
    return (1 if f else 0), f, len(claims)


# ---------------------------------------------------------------- builder
def build(scratch, name, rnd, claims, opts):
    o = dict(OPTS)
    o.update(opts)
    if o["round"] == "auto":
        o["round"] = rnd.randint(10, 99)
    h = rhex(rnd)
    dirname = {"spaces": "fx dir %s" % h}.get(o["root"], "fx-%s" % h)
    fx = Fx(scratch, dirname)
    rn = rnd.randint(10, 99)
    ppath = {"plain": "census/round-%d/prereg-%s.txt" % (rn, rhex(rnd)),
             "spaces": "census/rnd %d/pre reg %s.txt" % (rn, rhex(rnd)),
             "glob": "census/r[%d]/pre*reg-%s.txt" % (rn, rhex(rnd))}[o["ppath"]]
    salt = lambda: rhex(rnd, 14)
    fx.write("README", "base " + salt() + "\n")
    c0 = fx.commit(msg(rnd))
    tree = lambda r: ".ufo/waves/round-%s/" % r
    dtree = lambda d: tree(d["tree"] if d["tree"] is not None else (o["round"] if o["round"] is not None else 7))

    def dpath(d):
        return dtree(d) + d["sub"] + "/" + d["name"]

    side = None
    if any(c["base"] == "side" for c in claims):
        fx.git("checkout", "-q", "-b", "s" + secrets.token_hex(3))
        fx.write("side-%s.txt" % rhex(rnd), salt())
        side = fx.commit(msg(rnd))
        fx.git("checkout", "-q", fx.main)
    if o["side_freeze"]:
        fx.git("checkout", "-q", "-b", "sf" + secrets.token_hex(3))
        sidebranch = fx.git("rev-parse", "--abbrev-ref", "HEAD")
        fx.git("checkout", "-q", fx.main)
        for d in o["dfiles"]:
            if d["when"] == "mainparallel":
                fx.write(dpath(d), salt())
                fx.commit(msg(rnd))
        fx.git("checkout", "-q", sidebranch)
    else:
        for _ in range(rnd.randint(1, 3)):
            fx.write("src/%s.txt" % rhex(rnd), salt())
            fx.commit(msg(rnd))
    for d in o["dfiles"]:
        if d["when"] in ("before", "readd", "sideearly"):
            fx.write(dpath(d), salt())
            fx.commit(msg(rnd))
        if d["when"] == "readd":
            fx.rm(dpath(d))
            fx.commit(msg(rnd))

    # instruments and the preregistration text
    info = []
    for c in claims:
        cd = "census/r%s/" % rhex(rnd, 6)
        if "spaced" in (c["counter"], c["pop"]):
            cd = "census/sp ace %s/" % rhex(rnd, 4)
        i = dict(c=c, cpath=cd + "counter-%s.py" % rhex(rnd, 5), ppath=cd + "pop-%s.tsv" % rhex(rnd, 5),
                 kpath="census/controls/ctl-%s.txt" % rhex(rnd, 6))
        s = salt()
        i["cbytes"] = ("# counter %s\nprint(%r)\n" % (s, s)).encode()
        i["pbytes"] = POP[c["popc"]].format(s=s).encode()
        i["kbytes"] = CONTROL[c["control"] if c["control"] in CONTROL else "red"].format(s=s, n=rnd.randint(1, 9)).encode()
        for st, path, data in ((c["counter"], i["cpath"], i["cbytes"]), (c["pop"], i["ppath"], i["pbytes"]),
                               (c["control"], i["kpath"], i["kbytes"])):
            if st == "dir":
                fx.write(path + "/inner-%s.txt" % rhex(rnd, 4), salt())
            elif st in ("missing", "absent", "blank", "late"):
                pass
            else:
                fx.write(path, data)
        info.append(i)
    eol = o["eol"]

    def stated(data, wrong, upper=False, none=False):
        if none:
            return None
        v = sha(data + (b"x" + salt().encode() if wrong else b""))
        return v.upper() if upper else v

    def text(final, base_map):
        out = ["# prereg %s" % salt()]
        if o["round"] is not None:
            out.append("Round: %s" % o["round"])
        out.append("Lane: /x/%s" % rhex(rnd))
        out.extend(o["preamble"])
        out.append("")
        for k, i in enumerate(info):
            c = i["c"]
            out.append("## C%d — claim %s" % (c["num"], i["tag"]))
            lines = {}
            b = c["base"]
            bv = {"ok": c0, "unresolved-abbrev": c0[:12], "zero": "0" * 40, "tree": i["treeid"], "blob": i["blobid"],
                  "side": side, "freeze": base_map.get("freeze", c0), "desc": base_map.get("desc", c0), "blank": ""}.get(b)
            if b != "absent":
                lines["Base"] = bv
            cs = c["counter"]
            if cs != "absent":
                lines["Counter"] = "" if cs == "blank" else (i["cpath"] if cs == "nosha" else
                                   "%s sha256=%s" % (i["cpath"], i["cstated"]))
            ps = c["pop"]
            if ps != "absent":
                lines["Population"] = "" if ps == "blank" else "%s sha256=%s" % (i["ppath"], i["pstated"])
            if c["control"] != "absent":
                lines["Control"] = "" if c["control"] == "blank" else i["kpath"]
            lines["_t"], lines["_k"] = None, None
            for key, st in (("Target", c["target"]), ("Kill", c["kill"])):
                if st == "absent":
                    continue
                v = {"ok": "text %s" % rhex(rnd, 4), "empty": "", "tabempty": "\t", "indented": "x"}[st]
                lines["_" + key[0].lower()] = fmt_key(key, v, st == "indented")
            body = [fmt_key(k2, lines[k2]) for k2 in ("Base", "Counter", "Population", "Control") if k2 in lines]
            if lines.get("_t"):
                body.append(lines["_t"])
            if o["subheader"] and k == 0:
                body.append("### Notes")
                body.append("prose line without a key")
            if lines.get("_k"):
                body.append(lines["_k"])
            out.extend(body)
            out.append("")
        out.extend(o["trailer"])
        return eol.join(out) + eol

    for i in info:
        c = i["c"]
        i["tag"] = rhex(rnd, 4)
        i["treeid"] = fx.git("rev-parse", c0 + "^{tree}")
        i["blobid"] = fx.git("rev-parse", c0 + ":README")
        i["cstated"] = stated(i["cbytes"], c["cwrong"], upper=c["counter"] == "upper")
        i["pstated"] = stated(i["pbytes"], c["pwrong"])
        if c["counter"] == "late":
            i["cstated"] = sha(i["cbytes"])
    if o["raw"] is not None:
        v1 = o["raw"]
    else:
        v1 = text(False, {}).encode("utf-8", "surrogateescape")
    for d in o["dfiles"]:
        if d["when"] == "same":
            fx.write(dpath(d), salt())
    fx.write(ppath, v1)
    fz = fx.commit(msg(rnd))
    if o["side_freeze"]:
        fx.git("checkout", "-q", fx.main)
        fx.git("merge", "-q", "--no-ff", "-m", msg(rnd), sidebranch)
    for d in o["dfiles"]:
        if d["when"] in ("after", "readd"):
            fx.write(dpath(d), salt())
            fx.commit(msg(rnd))
    if o["rename"]:
        newp = "census/round-%d/moved-%s.txt" % (rn, rhex(rnd))
        fx.git("mv", ppath, newp)
        fx.commit(msg(rnd))
        ppath = newp
    for i in info:
        c = i["c"]
        for edit, path, key in ((c["cedit"], i["cpath"], c["counter"]), (c["pedit"], i["ppath"], c["pop"])):
            if key not in ("ok", "upper", "nosha", "spaced"):
                continue
            if edit in ("modify", "revert"):
                orig = open(os.path.join(fx.d, path), "rb").read()
                fx.write(path, orig + b"\n# edit " + salt().encode() + b"\n")
                fx.commit(msg(rnd))
                if edit == "revert":
                    fx.write(path, orig)
                    fx.commit(msg(rnd))
            elif edit == "delete":
                fx.rm(path)
                fx.commit(msg(rnd))
        if c["counter"] == "late":
            fx.write(i["cpath"], i["cbytes"])
            fx.commit(msg(rnd))
    fx.write("post/%s.txt" % rhex(rnd), salt())
    desc = fx.commit(msg(rnd))
    needs_v2 = any(i["c"]["base"] in ("freeze", "desc") for i in info)
    if (needs_v2 or o["prereg_edit"]) and o["raw"] is None:
        v2 = text(True, {"freeze": fz, "desc": desc})
        if o["prereg_edit"]:
            v2 = v2 + "# edited after freeze %s%s" % (salt(), eol)
        fx.write(ppath, v2.encode("utf-8", "surrogateescape"))
        fx.commit(msg(rnd))
    rev = fz if o["rev_at_freeze"] else fx.git("rev-parse", "HEAD")
    root = fx.d
    cwd = scratch
    if o["root"] == "symlink":
        root = fx.d + "-link"
        os.symlink(fx.d, root)
    elif o["root"] == "slash":
        root = fx.d + "/"
    elif o["root"] == "relative":
        root = "./" + os.path.basename(fx.d)
    exit_, finds, n = oracle([i["c"] for i in info], o)
    return dict(fx=fx, root=root, cwd=cwd, rev=rev, prereg=ppath, expect=(exit_, collections.Counter(finds), n),
                fz=fz, c0=c0)


# ---------------------------------------------------------------- scenarios
def scenarios(rnd):
    S = []

    def add(name, tier, claims, expect=None, **opts):
        S.append(dict(name=name, tier=tier, claims=claims, opts=opts, explicit=expect))

    E = lambda ex, *f, n=None: (ex, collections.Counter(f), n)
    add("clean-1-claim", "strict", [C(1)], E(0))
    add("clean-claims-1-9-10-11", "strict", [C(1), C(9), C(10), C(11)], E(0))
    add("crlf-clean", "strict", [C(1), C(2)], E(0), eol="\r\n")
    add("crlf-defects-and-early-dispatch", "strict", [C(1, cwrong=True), C(2, pop="ok", popc="header")],
        E(1, ("C1", "COUNTER-DIGEST"), ("C2", "POPULATION-EMPTY"), ("C0", "DISPATCH-BEFORE-FREEZE")),
        eol="\r\n", dfiles=[D("a-%s-dispatch.json" % rhex(rnd), "before")])
    add("two-claims-different-failures", "strict",
        [C(1, cwrong=True), C(2, control="notlast", popc="header")],
        E(1, ("C1", "COUNTER-DIGEST"), ("C2", "CONTROL-NOT-RED"), ("C2", "POPULATION-EMPTY")))
    add("claim-without-control", "strict", [C(1), C(2, control="absent")], E(1, ("C2", "FIELD-MISSING")))
    add("population-header-only", "strict", [C(1, popc="header")], E(1, ("C1", "POPULATION-EMPTY")))
    add("population-zero-bytes", "strict", [C(1, popc="zero")], E(1, ("C1", "POPULATION-EMPTY")))
    add("population-header-plus-blank-lines", "strict", [C(1, popc="hblank")], E(1, ("C1", "POPULATION-EMPTY")))
    add("population-two-lines-no-final-newline", "strict", [C(1, popc="nonl")], E(0))
    add("counter-path-is-directory", "strict", [C(1, counter="dir")], E(1, ("C1", "COUNTER-MISSING")))
    add("population-path-is-directory", "strict", [C(1, pop="dir")], E(1, ("C1", "POPULATION-MISSING")))
    add("control-path-is-directory", "strict", [C(1, control="dir")], E(1, ("C1", "CONTROL-MISSING")))
    add("root-with-spaces", "strict", [C(1), C(2)], E(0), root="spaces")
    add("prereg-path-with-spaces", "strict", [C(1)], E(0), ppath="spaces")
    add("root-symlink", "strict", [C(1)], E(0), root="symlink")
    add("root-trailing-slash", "strict", [C(1)], E(0), root="slash")
    add("root-relative-cwd", "strict", [C(1, cwrong=True)], E(1, ("C1", "COUNTER-DIGEST")), root="relative")
    add("round-absent-early-dispatch-silent", "strict", [C(1)], E(0), round=None,
        dfiles=[D("z-%s-dispatch.json" % rhex(rnd), "before"), D("%s.ready" % rhex(rnd), "same")])
    add("dispatch-before-freeze", "strict", [C(1)], E(1, ("C0", "DISPATCH-BEFORE-FREEZE")),
        dfiles=[D("%s-dispatch.json" % rhex(rnd), "before")])
    add("ready-before-freeze", "strict", [C(1)], E(1, ("C0", "DISPATCH-BEFORE-FREEZE")),
        dfiles=[D("%s.ready" % rhex(rnd), "before", sub="w2/deep")])
    add("dispatch-in-freeze-commit", "strict", [C(1)], E(1, ("C0", "DISPATCH-BEFORE-FREEZE")),
        dfiles=[D("%s-dispatch.json" % rhex(rnd), "same")])
    add("dispatch-after-freeze-clean", "strict", [C(1)], E(0), dfiles=[D("%s-dispatch.json" % rhex(rnd), "after")])
    add("dispatch-other-round-silent", "strict", [C(1)], E(0), round=41,
        dfiles=[D("%s-dispatch.json" % rhex(rnd), "before", tree=40)])
    add("two-dispatch-files-before", "strict", [C(1)],
        E(1, ("C0", "DISPATCH-BEFORE-FREEZE"), ("C0", "DISPATCH-BEFORE-FREEZE")),
        dfiles=[D("%s-dispatch.json" % rhex(rnd), "before"), D("%s.ready" % rhex(rnd), "before", sub="w9")])
    add("dispatch-deleted-and-readded-after-freeze", "strict", [C(1)], E(1, ("C0", "DISPATCH-BEFORE-FREEZE")),
        dfiles=[D("%s-dispatch.json" % rhex(rnd), "readd")])
    add("dispatch-lookalike-names-silent", "strict", [C(1)], E(0),
        dfiles=[D(n, "before") for n in ("dispatch.json", "x-dispatch.json.bak", "ready", "x.readyy",
                                          "a-dispatch.jsonl", "%s-dispatch.JSON" % rhex(rnd))])
    add("dispatch-non-ascii-file-name", "strict", [C(1)], E(1, ("C0", "DISPATCH-BEFORE-FREEZE")),
        dfiles=[D("\u00e9%s-dispatch.json" % rhex(rnd, 4), "before")])
    add("dispatch-non-ascii-directory", "strict", [C(1)], E(1, ("C0", "DISPATCH-BEFORE-FREEZE")),
        dfiles=[D("%s.ready" % rhex(rnd), "before", sub="w\u00fc1")])
    add("dispatch-in-spaced-directory", "strict", [C(1)], E(1, ("C0", "DISPATCH-BEFORE-FREEZE")),
        dfiles=[D("%s-dispatch.json" % rhex(rnd), "before", sub="w 1")])
    add("counter-edited-after-freeze", "strict", [C(1, cedit="modify")], E(1, ("C1", "FROZEN-EDITED")))
    add("counter-deleted-after-freeze", "strict", [C(1, cedit="delete")], E(1, ("C1", "FROZEN-EDITED")))
    add("counter-edited-then-reverted-clean", "strict", [C(1, cedit="revert")], E(0))
    add("population-edited-after-freeze", "strict", [C(1, pedit="modify")], E(1, ("C1", "FROZEN-EDITED")))
    add("counter-wrong-digest-and-edited", "strict", [C(1, cwrong=True, cedit="modify")],
        E(1, ("C1", "COUNTER-DIGEST"), ("C1", "FROZEN-EDITED")))
    add("population-wrong-digest", "strict", [C(1, pwrong=True)], E(1, ("C1", "POPULATION-DIGEST")))
    add("population-header-only-and-wrong-digest", "strict", [C(1, pwrong=True, popc="header")],
        E(1, ("C1", "POPULATION-DIGEST"), ("C1", "POPULATION-EMPTY")))
    add("counter-missing-everywhere", "strict", [C(1, counter="missing")], E(1, ("C1", "COUNTER-MISSING")))
    add("population-missing-no-empty-finding", "strict", [C(1, pop="missing")], E(1, ("C1", "POPULATION-MISSING")))
    add("base-abbreviated", "strict", [C(1, base="unresolved-abbrev")], E(1, ("C1", "BASE-UNRESOLVED")))
    add("base-zero-sha", "strict", [C(1, base="zero")], E(1, ("C1", "BASE-UNRESOLVED")))
    add("base-is-tree-id", "strict", [C(1, base="tree")], E(1, ("C1", "BASE-UNRESOLVED")))
    add("base-is-blob-id", "strict", [C(1, base="blob")], E(1, ("C1", "BASE-UNRESOLVED")))
    add("base-on-side-branch", "strict", [C(1, base="side")], E(1, ("C1", "BASE-NOT-ANCESTOR")))
    add("base-is-freeze-itself", "strict", [C(1, base="freeze")], E(1, ("C1", "BASE-NOT-ANCESTOR")))
    add("base-is-descendant-of-freeze", "strict", [C(1, base="desc")], E(1, ("C1", "BASE-NOT-ANCESTOR")))
    add("kill-key-indented", "strict", [C(1, kill="indented")], E(1, ("C1", "FIELD-MISSING")))
    add("target-tab-only-empty", "strict", [C(1, target="tabempty")], E(1, ("C1", "FIELD-EMPTY")))
    add("all-keys-absent", "strict", [C(1, base="absent", counter="absent", pop="absent", control="absent",
                                        target="absent", kill="absent")], E(1, *[("C1", "FIELD-MISSING")] * 6))
    add("subheader-keeps-block", "strict", [C(1), C(2)], E(0), subheader=True)
    add("later-section-keys-not-credited", "strict", [C(1, kill="absent")], E(1, ("C1", "FIELD-MISSING")),
        trailer=["## Appendix", "Kill: not part of any claim", "Base: nor this"])
    add("preamble-key-lines-ignored", "strict", [C(1)], E(0),
        preamble=["Target: a", "Kill: b", "Base: " + "1" * 40, "Counter: nope sha256=" + "0" * 64])
    add("control-exit-zero", "strict", [C(1, control="green")], E(1, ("C1", "CONTROL-NOT-RED")))
    add("control-exit-not-last-line", "strict", [C(1, control="notlast")], E(1, ("C1", "CONTROL-NOT-RED")))
    add("control-empty-file", "strict", [C(1, control="empty")], E(1, ("C1", "CONTROL-NOT-RED")))
    add("control-exit-garbage", "strict", [C(1, control="garbage")], E(1, ("C1", "CONTROL-NOT-RED")))
    add("control-exit-00", "strict", [C(1, control="zeros")], E(1, ("C1", "CONTROL-NOT-RED")))
    add("control-crlf-red-clean", "strict", [C(1, control="crlfred")], E(0))
    add("control-trailing-blank-lines-clean", "strict", [C(1, control="trailblank")], E(0))
    add("control-missing", "strict", [C(1, control="missing")], E(1, ("C1", "CONTROL-MISSING")))
    add("non-utf8-bytes-in-preamble", "strict", [C(1)], E(0), preamble=["Note: caf\udce9 \udcff\udcfe"])
    add("prereg-edited-after-freeze-silent", "strict", [C(1)], E(0), prereg_edit=True)
    add("rev-at-freeze-not-tip", "strict", [C(1, cedit="modify")], E(0), rev_at_freeze=True)
    add("prereg-renamed-freeze-is-rename-commit", "strict", [C(1)], E(1, ("C0", "DISPATCH-BEFORE-FREEZE")),
        rename=True, dfiles=[D("%s-dispatch.json" % rhex(rnd), "after")])
    add("freeze-on-side-branch-merged-clean", "strict", [C(1)], E(0), side_freeze=True,
        dfiles=[D("%s-dispatch.json" % rhex(rnd), "mainparallel")])
    add("freeze-on-side-branch-early-dispatch", "strict", [C(1)], E(1, ("C0", "DISPATCH-BEFORE-FREEZE")),
        side_freeze=True, dfiles=[D("%s.ready" % rhex(rnd), "before"), D("%s-dispatch.json" % rhex(rnd), "mainparallel")])
    # raw preregistrations
    for nm, raw, ex in (("no-claims-empty-file", b"", E(1, ("C0", "NO-CLAIMS"), n=0)),
                        ("no-claims-header-variants", ("# x\n##C1\n## c2\n## C\n# C3\n#### C4\nBase: " + "a" * 40 + "\n").encode(),
                         E(1, ("C0", "NO-CLAIMS"), n=0)),
                        ("no-claims-crlf-only", b"Round: 5\r\nnothing\r\n", E(1, ("C0", "NO-CLAIMS"), n=0))):
        add(nm, "strict", [], ex, raw=raw, raw_expect=(ex[0], ex[1], 0))
    # refusals
    add("refuse-abbreviated-rev", "strict", [C(1)], E(2), rev_override="abbrev")
    add("refuse-unknown-full40-rev", "strict", [C(1)], E(2), rev_override="unknown")
    add("refuse-prereg-absent-at-rev", "strict", [C(1)], E(2), prereg_override="absent")
    add("refuse-prereg-is-directory", "strict", [C(1)], E(2), prereg_override="dir")
    add("refuse-root-not-a-repo", "strict", [C(1)], E(2), root_override="notrepo")
    add("refuse-root-missing", "strict", [C(1)], E(2), root_override="missing")
    # literal reading of the class text: blank value of a present key
    add("literal-base-blank", "literal", [C(1, base="blank")], E(1, ("C1", "BASE-UNRESOLVED")))
    add("literal-counter-blank", "literal", [C(1, counter="blank")], E(1, ("C1", "COUNTER-MISSING")))
    add("literal-population-blank", "literal", [C(1, pop="blank")], E(1, ("C1", "POPULATION-MISSING")))
    add("literal-control-blank", "literal", [C(1, control="blank")], E(1, ("C1", "CONTROL-MISSING")))
    # grammar silent
    add("ambig-counter-path-with-space", "ambig", [C(1, counter="spaced", pop="spaced")], E(0))
    add("ambig-counter-without-sha256", "ambig", [C(1, counter="nosha")], E(1, ("C1", "COUNTER-DIGEST")))
    add("ambig-sha256-uppercase-hex", "ambig", [C(1, counter="upper")], E(0))
    add("ambig-counter-added-after-freeze", "ambig", [C(1, counter="late")], E(1, ("C1", "COUNTER-MISSING")))
    add("ambig-prereg-path-has-glob-chars", "ambig", [C(1)], E(0), ppath="glob")
    # fuzz: independent per-claim defect choice, oracle-derived expectation
    for k in range(8):
        n = rnd.randint(5, 9)
        claims = []
        for num in rnd.sample(range(1, 15), n):
            claims.append(C(num,
                            base=rnd.choice(["ok"] * 5 + ["unresolved-abbrev", "zero", "tree", "blob", "side", "freeze", "desc", "absent"]),
                            counter=rnd.choice(["ok"] * 5 + ["missing", "dir", "absent"]), cwrong=rnd.random() < .25,
                            cedit=rnd.choice([None] * 3 + ["modify", "delete", "revert"]),
                            pop=rnd.choice(["ok"] * 5 + ["missing", "dir", "absent"]),
                            popc=rnd.choice(["ok"] * 3 + ["header", "zero", "hblank", "nonl"]), pwrong=rnd.random() < .25,
                            pedit=rnd.choice([None] * 3 + ["modify", "delete", "revert"]),
                            control=rnd.choice(["red"] * 3 + ["green", "notlast", "empty", "garbage", "crlfred", "trailblank",
                                                              "zeros", "missing", "dir", "absent"]),
                            target=rnd.choice(["ok"] * 4 + ["empty", "absent", "indented", "tabempty"]),
                            kill=rnd.choice(["ok"] * 4 + ["empty", "absent", "indented", "tabempty"])))
        dfiles = [D("%s-dispatch.json" % rhex(rnd), rnd.choice(["before", "same", "after", "readd"]))
                  for _ in range(rnd.randint(0, 3))]
        eol = rnd.choice(["\n", "\r\n"])
        add("fuzz-%d-%dclaims-%s" % (k, n, "crlf" if eol == "\r\n" else "lf"), "strict", claims, None, eol=eol,
            dfiles=dfiles, subheader=rnd.random() < .5)
    return S


# ---------------------------------------------------------------- runner
def run_case(tool, scratch, sc, rnd):
    b = build(scratch, "c%03d-%s" % (sc["idx"], rhex(rnd, 4)), rnd, sc["claims"], sc["opts"])
    o = sc["opts"]
    root, rev, prereg = b["root"], b["rev"], b["prereg"]
    if o.get("rev_override") == "abbrev":
        rev = rev[:12]
    elif o.get("rev_override") == "unknown":
        rev = secrets.token_hex(20)
    if o.get("prereg_override") == "absent":
        prereg = "census/never-%s.txt" % rhex(rnd)
    elif o.get("prereg_override") == "dir":
        prereg = os.path.dirname(prereg)
    if o.get("root_override") == "notrepo":
        root = os.path.join(scratch, "plain-" + rhex(rnd))
        os.makedirs(root)
    elif o.get("root_override") == "missing":
        root = os.path.join(scratch, "missing-" + rhex(rnd))
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "TMPDIR": scratch}
    env.update(GITENV)
    cmd = [sys.executable, "-B", tool, "--root", root, "--prereg", prereg, "--rev", rev]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=b["cwd"], env=env, timeout=120)
        rc, out, err = p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        rc, out, err = -9, "", "TIMEOUT"
    exp_rc, exp_f, exp_n = b["expect"]
    if sc["explicit"] is not None:
        xr, xf, xn = sc["explicit"]
        if sc["opts"].get("raw") is None and (xr, xf) != (exp_rc, exp_f):
            raise RuntimeError("HARNESS INCONSISTENT %s: explicit %r vs oracle %r" % (sc["name"], (xr, dict(xf)), (exp_rc, dict(exp_f))))
    got = collections.Counter()
    notes = []
    lines = [x for x in out.splitlines()]
    finds = [x for x in lines if x.startswith("FINDING ")]
    summ = [x for x in lines if x.startswith("SUMMARY ")]
    for x in finds:
        t = x.split(None, 3)
        if len(t) < 3:
            notes.append("malformed:" + x)
        else:
            got[(t[1], t[2])] += 1
    if "Traceback" in err:
        notes.append("traceback")
    if exp_rc == 2:
        if finds or summ:
            notes.append("stdout-not-empty-on-refusal")
        if not err.startswith("REFUSAL COULD-NOT-EVALUATE"):
            notes.append("no-REFUSAL-line")
    else:
        if finds != sorted(finds):
            notes.append("findings-unsorted")
        if len(summ) != 1 or not lines or lines[-1] != summ[0]:
            notes.append("summary-missing-or-not-last")
        else:
            want = "SUMMARY claims=%d findings=%d" % (exp_n, sum(exp_f.values()))
            if summ[0] != want:
                notes.append("summary=%r want %r" % (summ[0], want))
    ok = rc == exp_rc and got == exp_f and not notes
    return dict(name=sc["name"], tier=sc["tier"], ok=ok, rc=rc, want_rc=exp_rc, got=sorted(got.elements()),
                want=sorted(exp_f.elements()), notes=notes, stderr=err.strip()[:300])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool")
    ap.add_argument("--lane", default=LANE)
    ap.add_argument("--tip", default=TIP)
    ap.add_argument("--scratch", default=SCRATCH)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out")
    ap.add_argument("--only")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args(argv)
    seed = a.seed if a.seed is not None else secrets.randbelow(2 ** 31)
    run = os.path.join(a.scratch, "run-%s" % secrets.token_hex(4))
    os.makedirs(run)
    try:
        tool = a.tool
        if not tool:
            tool = os.path.join(run, "souji-freeze-check.py")
            p = subprocess.run(["git", "-C", a.lane, "show", "%s:tools/souji-freeze-check.py" % a.tip],
                               stdout=subprocess.PIPE, check=True)
            with open(tool, "wb") as h:
                h.write(p.stdout)
        tool = os.path.abspath(tool)
        tsha = sha(open(tool, "rb").read())
        print("tool=%s sha256=%s seed=%d" % (tool, tsha, seed))
        work = os.path.join(run, "w")
        os.makedirs(work)
        rnd = random.Random(seed)
        scs = scenarios(rnd)
        for i, s in enumerate(scs):
            s["idx"] = i
        res = []
        for s in scs:
            if a.only and a.only not in s["name"]:
                continue
            res.append(run_case(tool, work, s, rnd))
        print("%-4s %-8s %-48s %-7s %s" % ("RES", "TIER", "SCENARIO", "EXIT", "DETAIL"))
        for r in res:
            detail = ""
            if not r["ok"]:
                w, g = collections.Counter(r["want"]), collections.Counter(r["got"])
                detail = "missing=%s extra=%s notes=%s %s" % (sorted((w - g).elements()), sorted((g - w).elements()),
                                                             [n for n in r["notes"] if not n.startswith("summary=")],
                                                             r["stderr"] if r["rc"] != r["want_rc"] else "")
            print("%-4s %-8s %-48s %-7s %s" % ("PASS" if r["ok"] else "FAIL", r["tier"], r["name"],
                                              "%s/%s" % (r["rc"], r["want_rc"]), detail))
        agg = {}
        for t in ("strict", "literal", "ambig"):
            tr = [r for r in res if r["tier"] == t]
            agg[t] = (sum(1 for r in tr if r["ok"]), len(tr))
        print("SUMMARY scenarios=%d strict=%d/%d literal=%d/%d ambig=%d/%d seed=%d tool_sha256=%s" % (
            len(res), agg["strict"][0], agg["strict"][1], agg["literal"][0], agg["literal"][1],
            agg["ambig"][0], agg["ambig"][1], seed, tsha))
        if a.out:
            with open(a.out, "w") as h:
                json.dump(dict(seed=seed, tool=tool, tool_sha256=tsha, results=res), h, indent=1)
        return 0 if agg["strict"][0] == agg["strict"][1] else 1
    finally:
        if not a.keep:
            shutil.rmtree(run, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
