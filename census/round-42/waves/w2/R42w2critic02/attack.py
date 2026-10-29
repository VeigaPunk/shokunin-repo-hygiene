#!/usr/bin/env python3
"""R42w2critic02 attack harness over the landed C2 tool (tip 3105a63b).

Expectations (`rc`, `exp`) were written from the docstring of census/round-42/c2-counter.py
(exit codes, finding classes, grammar, FREEZE-REV and DISPATCH rules) BEFORE any scenario ran.
Where that docstring is silent, the expectation is the literal reading and the row carries a
`contested` note. Classes: ok | false green | false finding | crash | hang.

Scratch: /fast/scratch/hyaku/souji-r42/R42w2critic02 (fixture repos under repos/, tool copy under tool/).
Results: results.tsv and raw/ next to this file (seat directory).
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter

SCR = "/fast/scratch/hyaku/souji-r42/R42w2critic02"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2critic02"
REPOS = SCR + "/repos"
TMP = SCR + "/tmp"
TOOL = SCR + "/tool/souji-freeze-check.py"  # `git show 3105a63b:tools/souji-freeze-check.py`
GENV = {"PATH": os.environ["PATH"], "HOME": SCR + "/home", "TMPDIR": TMP, "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "critic", "GIT_AUTHOR_EMAIL": "critic@example.invalid",
        "GIT_COMMITTER_NAME": "critic", "GIT_COMMITTER_EMAIL": "critic@example.invalid"}
RUN_ENV = {"PATH": os.environ["PATH"], "HOME": SCR + "/home", "TMPDIR": TMP, "LC_ALL": "C"}

COUNTER = b"# counter\nprint('counter')\n"
COUNTER_EDIT = b"# counter\nprint('edited')\n"
POP = b"id\tname\n1\talpha\n2\tbeta\n"
CTL_RED = b"SUMMARY items=2 corrected=0\nEXIT=1\n"
DEFAULT_BASE = {"README": b"base\n", "census/c1.py": COUNTER, "census/pop.tsv": POP,
                "census/control.txt": CTL_RED}
R = ".ufo/waves/round-42/"


def h(b):
    return hashlib.sha256(b).hexdigest()


def git(d, *args, env=None, check=True):
    e = dict(GENV)
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", d] + list(args), capture_output=True, env=e)
    if check and p.returncode != 0:
        raise RuntimeError("git %s in %s: %s" % (" ".join(args), d, p.stderr.decode("utf-8", "replace")))
    return p.stdout.decode("utf-8", "replace").strip()


def assert_top(d):
    top = git(d, "rev-parse", "--show-toplevel")
    if os.path.realpath(top) != os.path.realpath(d):
        raise RuntimeError("toplevel mismatch: %s != %s" % (top, d))


# ---- ops --------------------------------------------------------------------------------------
def W(path, val):
    return ("w", path, val)


def CM(msg, **opts):
    return ("c", msg, opts)


def MV(a, b):
    return ("mv", a, b)


def FZ(text=None, path="prereg.txt"):
    return [W(path, PRE if text is None else text), CM("freeze")]


def put(d, path, v, subs):
    full = os.path.join(d, path)
    if v is None:
        if os.path.islink(full) or os.path.isfile(full):
            os.remove(full)
        elif os.path.isdir(full):
            shutil.rmtree(full)
        return
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if os.path.islink(full) or os.path.isfile(full):
        os.remove(full)
    elif os.path.isdir(full):
        shutil.rmtree(full)
    if isinstance(v, tuple):
        os.symlink(v[1], full)
        return
    if isinstance(v, str):
        v = v.encode("utf-8")
    for k in sorted(subs, key=len, reverse=True):
        v = v.replace(("{%s}" % k).encode("utf-8"), subs[k].encode("utf-8"))
    with open(full, "wb") as fh:
        fh.write(v)


def head(d):
    return git(d, "rev-parse", "HEAD")


def run_ops(d, ops, subs):
    for op in ops:
        k = op[0]
        if k == "w":
            put(d, op[1], op[2], subs)
        elif k == "mv":
            os.makedirs(os.path.dirname(os.path.join(d, op[2])) or d, exist_ok=True)
            os.rename(os.path.join(d, op[1]), os.path.join(d, op[2]))
        elif k == "x":
            os.chmod(os.path.join(d, op[1]), 0o755)
        elif k == "c":
            opts = op[2]
            env = {}
            if "date" in opts:
                env = {"GIT_AUTHOR_DATE": opts["date"], "GIT_COMMITTER_DATE": opts["date"]}
            git(d, "add", "-A")
            git(d, "commit", "-q", "--allow-empty", "-m", op[1], env=env)
            if opts.get("tag"):
                subs[opts["tag"]] = head(d)
        elif k == "gl":  # gitlink (submodule) entry at path, pointing at subs[op[2]]
            git(d, "update-index", "--add", "--cacheinfo", "160000,%s,%s" % (subs[op[2]], op[1]))
            git(d, "commit", "-q", "--allow-empty", "-m", "gitlink")
        elif k == "br":
            git(d, "checkout", "-q", "-b", op[1])
        elif k == "co":
            git(d, "checkout", "-q", op[1])
        elif k == "mg":
            git(d, "merge", "-q", "--no-ff", "--no-edit", "-m", "merge " + op[1], op[1])
        elif k == "ann":  # annotated tag at HEAD; subs[UPPER] = tag object id
            git(d, "tag", "-a", op[1], "-m", "tag " + op[1])
            subs[op[1].upper()] = git(d, "rev-parse", "refs/tags/" + op[1])
        elif k == "orph":  # commit with HEAD's tree but not an ancestor of HEAD
            subs[op[1]] = git(d, "commit-tree", "HEAD^{tree}", "-m", "orphan")
        else:
            raise RuntimeError("unknown op %r" % (op,))


# ---- prereg text ------------------------------------------------------------------------------
G = ["Base: {BASE}", "Counter: census/c1.py sha256={CS}", "Population: census/pop.tsv sha256={PS}",
     "Control: census/control.txt", "Target: items=2 corrected=2", "Kill: any uncorrected"]


def claim(head="## C1 — claim", rep=None, drop=(), add=(), body=None):
    out = [head]
    for ln in (G if body is None else body):
        k = ln.split(":", 1)[0]
        if rep and k in rep:
            if rep[k] is not None:
                out.append(rep[k])
            continue
        if k in drop:
            continue
        out.append(ln)
    out.extend(add)
    return out


def doc(*blocks, round_="Round: 42", eol="\n", pre=()):
    lines = list(pre)
    if round_ is not None:
        lines.append(round_)
    lines.append("")
    for b in blocks:
        lines.extend(b)
        lines.append("")
    return eol.join(lines) + eol


PRE = doc(claim())
PRE_EDIT = doc(claim(rep={"Counter": "Counter: census/c1.py sha256={CS_EDIT}"}))  # digest of edited counter
PRE_DRAFT_CSE = PRE_EDIT  # draft whose digest names the counter edited before the rename


def scenarios():
    S = []

    def add(name, attack, rc, exp, steps=(), base=None, full=False, sub=None, rev=None,
            prereg="prereg.txt", contested=None, special=None):
        S.append(dict(name=name, attack=attack, rc=rc, exp=list(exp), steps=list(steps), base=base,
                      full=full, sub=sub, rev=rev, prereg=prereg, contested=contested, special=special))

    # ---- A: dispatch-before-freeze (any depth, basename rule, round scoping)
    add("A01", "dispatch-named file after freeze at depth 3 stays clean", 0, [],
        FZ() + [W(R + "a/b/c-dispatch.json", "{}\n"), CM("post")])
    add("A02", "dispatch file before freeze at depth 2", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "a/w1-dispatch.json", "{}\n"), CM("pre")] + FZ())
    add("A03", "w1-spec.json before freeze at depth 3", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "a/b/w1-spec.json", "{}"), CM("pre")] + FZ())
    add("A04", ".ready.partial before freeze (basename contains .ready)", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "w1.ready.partial", "x"), CM("pre")] + FZ())
    add("A05", "*-dispatch-attempts.txt after freeze", 0, [],
        FZ() + [W(R + "w1-dispatch-attempts.txt", "x"), CM("post")])
    add("A06", "*-dispatch-attempts.txt before freeze", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "w1-dispatch-attempts.txt", "x"), CM("pre")] + FZ())
    add("A07", "spec.json (no hyphen before spec) is not a dispatch name", 0, [],
        [W(R + "spec.json", "{}"), CM("pre")] + FZ())
    add("A08", "w1-results.json.bak does not end -results.json", 0, [],
        [W(R + "w1-results.json.bak", "x"), CM("pre")] + FZ())
    add("A09", "dispatch file of round-41 is out of scope for round-42", 0, [],
        [W(".ufo/waves/round-41/w1-dispatch.json", "{}"), CM("pre")] + FZ())
    add("A10", "round-420 directory is not round-42 (prefix trap)", 0, [],
        [W(".ufo/waves/round-420/w1-dispatch.json", "{}"), CM("pre")] + FZ())
    add("A11", "dispatch basename with a space", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "w1-dispatch file.json", "{}"), CM("pre")] + FZ())
    add("A12", "dispatch basename with unicode", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "w1-dispatché.json", "{}"), CM("pre")] + FZ())
    add("A13", "dispatch basename with a double quote (git-quoted in log output)", 1,
        ["C0 DISPATCH-BEFORE-FREEZE"], [W(R + 'w1-dispatch"x.json', "{}"), CM("pre")] + FZ())
    add("A14", "dispatch basename with a newline (git-quoted in log output)", 1,
        ["C0 DISPATCH-BEFORE-FREEZE"], [W(R + "w1-dispatch\nx.json", "{}"), CM("pre")] + FZ())
    add("A15", "dispatch name that is a symlink, before freeze", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "w1-dispatch.json", ("link", "notes.md")), CM("pre")] + FZ())
    add("A16", "-dispatch in a directory name only; file basename clean", 0, [],
        [W(R + "x-dispatch/notes.md", "n"), CM("pre")] + FZ())
    add("A17", "dispatch added before freeze and deleted after", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "w1-dispatch.json", "{}"), CM("pre")] + FZ() + [W(R + "w1-dispatch.json", None), CM("rm")])
    add("A18", "dispatch added before freeze and renamed after", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "w1-dispatch.json", "{}"), CM("pre")] + FZ() + [MV(R + "w1-dispatch.json", R + "w1-dispatch.old"),
                                                                 CM("mv")])
    add("A19", "dispatch on a side branch merged before the freeze commit", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [("br", "side"), W(R + "w1-dispatch.json", "{}"), CM("side"), ("co", "main"), ("mg", "side")] + FZ())
    add("A20", "dispatch on a side branch merged AFTER freeze (graph-order reading)", 0, [],
        [("br", "side"), W(R + "w1-dispatch.json", "{}"), CM("side"), ("co", "main")] + FZ() + [("mg", "side")],
        contested="docstring defines 'ancestor of FREEZE-REV'; wall-clock order not in scope")
    add("A21", "Round: 042 (zero-padded) with round-42 dispatch before freeze", 1, ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "w1-dispatch.json", "{}"), CM("pre")] + FZ(doc(claim(), round_="Round: 042")),
        contested="round number 42 written 042; docstring says round-<N>")
    add("A22", "Round: ４２ (fullwidth digits) with round-42 dispatch before freeze", 1,
        ["C0 DISPATCH-BEFORE-FREEZE"],
        [W(R + "w1-dispatch.json", "{}"), CM("pre")] + FZ(doc(claim(), round_="Round: ４２")),
        contested="Unicode digits; round is 42")
    add("A23", "lowercase 'round:' key", 1, ["C0 FIELD-MISSING"], FZ(doc(claim(), round_="round: 42")),
        contested="Round check is tool-side (r41 hardening); docstring lists FIELD-MISSING, not the Round field")
    add("A24", "two Round lines, both 42", 0, [], FZ(doc(claim(), round_="Round: 42\nRound: 42")),
        contested="duplicate Round line has no class in the docstring")
    add("A25", "no Round line at all", 1, ["C0 FIELD-MISSING"], FZ(doc(claim(), round_=None)),
        contested="missing Round is prereg-wide FIELD-MISSING C0 (docstring names the class, not the field)")
    add("A26", "draft at other path, dispatch between draft and rename-in to prereg.txt", 1,
        ["C0 DISPATCH-BEFORE-FREEZE"],
        [W("draft.txt", PRE), CM("draft"), W(R + "w1-dispatch.json", "{}"), CM("disp"),
         MV("draft.txt", "prereg.txt"), CM("rename")])
    add("A27", "draft names the counter's EDITED digest; counter edited between draft and rename-in", 0, [],
        [W("draft.txt", PRE_DRAFT_CSE), CM("draft"), W("census/c1.py", COUNTER_EDIT), CM("edit"),
         MV("draft.txt", "prereg.txt"), CM("rename")],
        contested="FREEZE-REV is the oldest ADDING commit: the rename-in is the freeze (limit)")

    # ---- B: key grammar
    add("B01", "same claim keys in two claims (not a duplicate)", 0, [], FZ(doc(claim(), claim("## C2 — b"))))
    add("B02", "Base key twice, differing", 1, ["C1 KEY-DUPLICATE"],
        FZ(doc(claim(add=["Base: 0000000000000000000000000000000000000000"]))))
    add("B03", "Base key three times", 1, ["C1 KEY-DUPLICATE"],
        FZ(doc(claim(add=["Base: x", "Base: y"]))))
    add("B04", "Counter key twice, identical value", 1, ["C1 KEY-DUPLICATE"],
        FZ(doc(claim(add=["Counter: census/c1.py sha256={CS}"]))))
    add("B05", "Target key twice, second empty", 1, ["C1 KEY-DUPLICATE"], FZ(doc(claim(add=["Target:"]))))
    add("B06", "duplicate Base plus missing Kill", 1, ["C1 KEY-DUPLICATE", "C1 FIELD-MISSING"],
        FZ(doc(claim(drop=("Kill",), add=["Base: {BASE}"]))))
    add("B07", "every key tab-indented", 1, ["C1 FIELD-MISSING"] * 6,
        FZ(doc(claim(body=["\t" + x for x in G]))))
    add("B08", "Target key with leading space", 1, ["C1 FIELD-MISSING"],
        FZ(doc(claim(rep={"Target": " Target: items=2 corrected=2"}))))
    add("B09", "key with space before colon ('Target :')", 1, ["C1 FIELD-MISSING"],
        FZ(doc(claim(rep={"Target": "Target : items=2 corrected=2"}))))
    add("B10", "lowercase key 'target:'", 1, ["C1 FIELD-MISSING"],
        FZ(doc(claim(rep={"Target": "target: items=2 corrected=2"}))))
    add("B11", "trailing spaces on a value", 0, [], FZ(doc(claim(rep={"Target": "Target: items=2 corrected=2   "}))))
    add("B12", "no space after colon ('Target:x')", 0, [],
        FZ(doc(claim(rep={"Target": "Target:items=2 corrected=2"}))),
        contested="docstring writes `Key: value`; lenient reading is clean")
    add("B13", "tab after colon", 0, [], FZ(doc(claim(rep={"Target": "Target:\titems=2 corrected=2"}))))
    add("B14", "whole prereg CRLF", 0, [], FZ(doc(claim(), eol="\r\n")))
    add("B15", "BOM in front of the first key of a claim", 1, ["C1 FIELD-MISSING"],
        FZ(doc(claim(rep={"Base": "\ufeffBase: {BASE}"}))),
        contested="docstring silent on BOM; literal column-0 key rule")
    add("B16", "BOM in front of the Round line", 0, [], FZ(doc(claim(), round_="\ufeffRound: 42")))
    add("B17", "empty value after whitespace", 1, ["C1 FIELD-EMPTY"],
        FZ(doc(claim(rep={"Target": "Target:    "}))))
    add("B18", "Kill key in the preamble, not in the claim", 1, ["C1 FIELD-MISSING"],
        FZ(doc(claim(drop=("Kill",)), pre=["Kill: any uncorrected"])))
    add("B19", "Kill after a '## Notes' heading inside the claim", 1, ["C1 FIELD-MISSING"],
        FZ(doc(claim(drop=("Kill",), add=["## Notes", "Kill: any uncorrected"]))),
        contested="block end at any '## ' line is the r41 grammar (tool docstring), not counter text")
    add("B20", "Kill after a '### ' sub-heading inside the claim", 0, [],
        FZ(doc(claim(drop=("Kill",), add=["### sub", "Kill: any uncorrected"]))))
    add("B21", "Kill as a bullet '- Kill: ...'", 1, ["C1 FIELD-MISSING"],
        FZ(doc(claim(rep={"Kill": "- Kill: any uncorrected"}))))
    add("B22", "near-duplicate 'Target : other' next to Target", 0, [],
        FZ(doc(claim(add=["Target : other"]))),
        contested="near-duplicate is not a key line; silent by grammar")
    add("B23", "Target example repeated inside a fenced block in the claim", 1, ["C1 KEY-DUPLICATE"],
        FZ(doc(claim(add=["```", "Target: example", "```"]))))

    # ---- C: headings
    add("C01", "'## C1: claim' colon form", 1, ["C0 HEADING-MALFORMED", "C0 NO-CLAIMS"],
        FZ(doc(claim(head="## C1: claim"))))
    add("C02", "'## C01 — claim' zero-padded number is a valid heading", 0, [],
        FZ(doc(claim(head="## C01 — claim"))))
    add("C03", "'## C1.' trailing dot", 1, ["C0 HEADING-MALFORMED", "C0 NO-CLAIMS"],
        FZ(doc(claim(head="## C1."))))
    add("C04", "'## C1.' followed by valid C2: claim C1 silently dropped", 1, ["C0 HEADING-MALFORMED"],
        FZ(doc(claim(head="## C1."), claim("## C2 — b"))))
    add("C05", "'##  C2' double space", 1, ["C0 HEADING-MALFORMED"], FZ(doc(claim(), claim("##  C2 — b"))))
    add("C06", "'##\\tC2' tab after ## with a full C2 body", 1, ["C1 KEY-DUPLICATE"] * 6,
        FZ(doc(claim(), claim("##\tC2 — b"))),
        contested="tab is not 'optional spaces'; C2 absorbed into C1 (six duplicate keys)")
    add("C07", "'##\\u00a0C2' no-break space with a full C2 body", 1, ["C1 KEY-DUPLICATE"] * 6,
        FZ(doc(claim(), claim("##\u00a0C2 — b"))), contested="NBSP is not 'optional spaces'")
    add("C08", "' ## C2' leading space (not column 0)", 1, ["C1 KEY-DUPLICATE"] * 6,
        FZ(doc(claim(), claim(" ## C2 — b"))), contested="column-0 rule; not malformed by grammar")
    add("C09", "'## C — b' has no digit: silent block end, C2 body dropped", 0, [],
        FZ(doc(claim(), claim("## C — b"))), contested="literal grammar: no digit means not a claim heading")
    add("C10", "'### C2' is a sub-heading: body keys fall into C1", 1, ["C1 KEY-DUPLICATE"] * 6,
        FZ(doc(claim(), claim("### C2 — b"))))
    add("C11", "two complete claims both numbered C1", 0, [], FZ(doc(claim(), claim("## C1 — again"))),
        contested="duplicate claim number has no class in the docstring")
    add("C12", "'## C1' followed by a tab", 1, ["C0 HEADING-MALFORMED", "C0 NO-CLAIMS"], FZ(doc(claim(head="## C1\t"))),
        contested="trailing tab after a valid heading; grammar says space or EOL")
    add("C13", "'## C1' followed by spaces", 0, [], FZ(doc(claim(head="## C1   "))))
    add("C14", "'## C1' example inside a fence, Base 0x40, then the real claim", 1,
        ["C1 BASE-UNRESOLVED"] + ["C1 FIELD-MISSING"] * 5,
        FZ("```\n## C1 — example\nBase: " + "0" * 40 + "\n```\n\n" + doc(claim())),
        contested="docstring has no fence rule; the fenced example is parsed as a claim")
    add("C15", "malformed '##C9' inside a fence", 1, ["C0 HEADING-MALFORMED"],
        FZ(doc(claim(), pre=["```", "##C9 example", "```"])), contested="fence-unaware, per docstring")
    add("C16", "two claims, CRLF", 0, [], FZ(doc(claim(), claim("## C2 — b"), eol="\r\n")))
    add("C17", "only a '## C — b' heading with keys: no claim", 1, ["C0 NO-CLAIMS"],
        FZ(doc(["## C — b"] + G)))
    add("C18", "heading text contains '## C2' mid-line", 0, [], FZ(doc(claim(head="## C1 — claim with ## C2 inside"))))
    add("C19", "'## C１' fullwidth digit one", 0, [], FZ(doc(claim(head="## C１ — x"))),
        contested="Unicode digit; docstring says 'a digit'")

    # ---- D: digests and paths
    add("D01", "Counter digest in upper case, correct bytes", 0, [],
        FZ(doc(claim(rep={"Counter": "Counter: census/c1.py sha256={CSU}"}))),
        contested="same digest value in another case; docstring says <64 hex>")
    add("D02", "Population digest in upper case, correct bytes", 0, [],
        FZ(doc(claim(rep={"Population": "Population: census/pop.tsv sha256={PSU}"}))),
        contested="same digest value in another case")
    add("D03", "Counter digest of 63 hex digits", 1, ["C1 COUNTER-DIGEST"],
        FZ(doc(claim(rep={"Counter": "Counter: census/c1.py sha256={CS63}"}))))
    add("D04", "Counter digest of 65 hex digits", 1, ["C1 COUNTER-DIGEST"],
        FZ(doc(claim(rep={"Counter": "Counter: census/c1.py sha256={CS65}"}))))
    add("D05", "Counter path without sha256= at all", 1, ["C1 COUNTER-DIGEST"],
        FZ(doc(claim(rep={"Counter": "Counter: census/c1.py"}))))
    add("D06", "Counter path with spaces", 0, [],
        FZ(doc(claim(rep={"Counter": "Counter: census/my counter.py sha256={CS}"}))),
        base={"census/my counter.py": COUNTER, "census/c1.py": None})
    add("D07", "Counter path with quotes", 0, [],
        FZ(doc(claim(rep={"Counter": 'Counter: census/"c1".py sha256={CS}'}))),
        base={'census/"c1".py': COUNTER, "census/c1.py": None})
    add("D08", "Counter path with unicode", 0, [],
        FZ(doc(claim(rep={"Counter": "Counter: census/çounter.py sha256={CS}"}))),
        base={"census/çounter.py": COUNTER, "census/c1.py": None})
    add("D09", "Counter path absolute '/census/c1.py'", 1, ["C1 COUNTER-MISSING"],
        FZ(doc(claim(rep={"Counter": "Counter: /census/c1.py sha256={CS}"}))))
    add("D10", "Counter path 'census/../census/c1.py'", 1, ["C1 COUNTER-MISSING"],
        FZ(doc(claim(rep={"Counter": "Counter: census/../census/c1.py sha256={CS}"}))),
        contested="same file by normalisation; docstring says repo path")
    add("D11", "Counter path './census/c1.py'", 0, [],
        FZ(doc(claim(rep={"Counter": "Counter: ./census/c1.py sha256={CS}"}))),
        contested="same file; git resolves ./ relative to cwd")
    add("D12", "Counter path with trailing slash 'census/c1.py/'", 1, ["C1 COUNTER-MISSING"],
        FZ(doc(claim(rep={"Counter": "Counter: census/c1.py/ sha256={CS}"}))))
    add("D13", "Counter path is a directory", 1, ["C1 COUNTER-MISSING"],
        FZ(doc(claim())), base={"census/c1.py": None, "census/c1.py/inner.py": COUNTER})
    add("D14", "census is a symlink to a directory: Counter, Population and Control all behind it", 1,
        ["C1 COUNTER-MISSING", "C1 POPULATION-MISSING", "C1 CONTROL-MISSING"], FZ(),
        full=True, base={"README": b"base\n", "census": ("link", "census-real"),
                         "census-real/c1.py": COUNTER, "census-real/pop.tsv": POP,
                         "census-real/control.txt": CTL_RED})
    add("D15", "Counter is a symlink, digest of the link text", 1, ["C1 COUNTER-SYMLINK"],
        FZ(doc(claim(rep={"Counter": "Counter: census/c1.py sha256={LSHA}"}))),
        base={"census/c1.py": ("link", "real-c1.py"), "census/real-c1.py": COUNTER})
    add("D16", "Counter is a symlink to an absolute path", 1, ["C1 COUNTER-SYMLINK"],
        FZ(), base={"census/c1.py": ("link", "/etc/passwd")})
    add("D17", "Counter is a gitlink (submodule entry)", 1, ["C1 COUNTER-MISSING"],
        [("gl", "census/c1.py", "BASE")] + FZ(), base={"census/c1.py": None})
    add("D18", "Counter regular at freeze, symlink after freeze", 1, ["C1 FROZEN-EDITED"],
        FZ() + [W("census/c1.py", ("link", "real-c1.py")), CM("link")])
    add("D19", "Counter symlink at freeze, regular after (COUNTER-SYMLINK alone by docstring)", 1,
        ["C1 COUNTER-SYMLINK"],
        FZ(), base={"census/c1.py": ("link", "real-c1.py"), "census/real-c1.py": COUNTER},
        contested=None)
    add("D20", "Population is a symlink", 1, ["C1 POPULATION-SYMLINK"],
        FZ(), base={"census/pop.tsv": ("link", "real-pop.tsv"), "census/real-pop.tsv": POP})
    add("D21", "Population with header and one data line (2 non-blank lines)", 0, [],
        FZ(doc(claim())), base={"census/pop.tsv": b"id\n1\n"}, sub={"PS": h(b"id\n1\n")})
    add("D22", "Population header only", 1, ["C1 POPULATION-EMPTY"], FZ(),
        base={"census/pop.tsv": b"id\tname\n"}, sub={"PS": h(b"id\tname\n")})
    add("D23", "Population whitespace-only data lines", 1, ["C1 POPULATION-EMPTY"], FZ(),
        base={"census/pop.tsv": b"id\n   \n\t\n"}, sub={"PS": h(b"id\n   \n\t\n")})
    add("D24", "Population with invalid UTF-8 and NUL, two lines", 0, [], FZ(),
        base={"census/pop.tsv": b"id\n\xff\x00\n"}, sub={"PS": h(b"id\n\xff\x00\n")})
    add("D25", "Population with CR-only line endings", 0, [], FZ(),
        base={"census/pop.tsv": b"id\r1\ralpha\r"}, sub={"PS": h(b"id\r1\ralpha\r")})
    add("D26", "Population whose only line is 'id' plus U+2028", 1, ["C1 POPULATION-EMPTY"], FZ(),
        base={"census/pop.tsv": "id\u2028".encode("utf-8")}, sub={"PS": h("id\u2028".encode("utf-8"))})

    # ---- E: control receipts
    add("E01", "Control path is a directory", 1, ["C1 CONTROL-MISSING"], FZ(),
        base={"census/control.txt": None, "census/control.txt/inner": CTL_RED})
    add("E02", "Control is a symlink to a red receipt file", 1, ["C1 CONTROL-NOT-RED"], FZ(),
        base={"census/control.txt": ("link", "real-ctl.txt"), "census/real-ctl.txt": CTL_RED},
        contested="no Control-symlink class in docstring; COUNTER-SYMLINK rationale applied by analogy")
    add("E03", "Control is a symlink whose LINK TEXT is 'EXIT=1' (no receipt file exists)", 1,
        ["C1 CONTROL-NOT-RED"], FZ(), base={"census/control.txt": ("link", "EXIT=1")},
        contested="by analogy with COUNTER-SYMLINK rationale: link text is not the receipt")
    add("E04", "Control last line EXIT=0 after an EXIT=1 line", 1, ["C1 CONTROL-NOT-RED"], FZ(),
        base={"census/control.txt": b"EXIT=1\nEXIT=0\n"})
    add("E05", "Control with trailing blank lines after EXIT=1", 0, [], FZ(),
        base={"census/control.txt": b"SUMMARY\nEXIT=1\n\n\n"})
    add("E06", "Control last line EXIT=-1", 1, ["C1 CONTROL-NOT-RED"], FZ(),
        base={"census/control.txt": b"EXIT=-1\n"}, contested="'-1' is nonzero but not digits")
    add("E07", "Control last line EXIT=01", 0, [], FZ(), base={"census/control.txt": b"EXIT=01\n"})
    add("E08", "Control empty", 1, ["C1 CONTROL-NOT-RED"], FZ(), base={"census/control.txt": b""})
    add("E09", "Control CRLF with EXIT=1", 0, [], FZ(), base={"census/control.txt": b"x\r\nEXIT=1\r\n"})
    add("E10", "Control absent", 1, ["C1 CONTROL-MISSING"], FZ(), base={"census/control.txt": None})
    add("E11", "Control lower-case 'exit=1'", 1, ["C1 CONTROL-NOT-RED"], FZ(),
        base={"census/control.txt": b"exit=1\n"})
    add("E12", "Control EXIT with a 26-digit code", 0, [], FZ(),
        base={"census/control.txt": b"EXIT=99999999999999999999999999\n"})
    add("E13", "Control path with a space", 0, [],
        FZ(doc(claim(rep={"Control": "Control: census/control file.txt"}))),
        base={"census/control.txt": None, "census/control file.txt": CTL_RED})

    # ---- F: freeze, rev, prereg location, Base resolution
    add("F01", "prereg renamed after freeze: absent at rev", 2, [], FZ() + [MV("prereg.txt", "old-prereg.txt"),
                                                                              CM("rename")])
    add("F02", "counter edited after freeze, prereg deleted and re-added naming the edited digest", 1,
        ["C1 COUNTER-DIGEST", "C1 FROZEN-EDITED"],
        FZ() + [W("census/c1.py", COUNTER_EDIT), CM("edit"), W("prereg.txt", None), CM("rm prereg"),
                W("prereg.txt", PRE_EDIT), CM("re-add")])
    add("F03", "same as F02 with a forged older committer date on the re-add (linear history)", 1,
        ["C1 COUNTER-DIGEST", "C1 FROZEN-EDITED"],
        FZ() + [W("census/c1.py", COUNTER_EDIT), CM("edit"), W("prereg.txt", None), CM("rm prereg"),
                W("prereg.txt", PRE_EDIT), CM("re-add", date="2001-01-01T00:00:00Z")])
    add("F04", "prereg added, removed, re-added byte-identical after freeze", 0, [],
        FZ() + [W("prereg.txt", None), CM("rm"), W("prereg.txt", PRE), CM("re-add")])
    add("F05", "counter edited, prereg re-added with the ORIGINAL digest", 1, ["C1 FROZEN-EDITED"],
        FZ() + [W("census/c1.py", COUNTER_EDIT), CM("edit"), W("prereg.txt", None), CM("rm"),
                W("prereg.txt", PRE), CM("re-add")])
    add("F06", "counter added after the prereg (not present at freeze)", 1, ["C1 COUNTER-MISSING"],
        FZ() + [W("census/c1.py", COUNTER), CM("late counter")], base={"census/c1.py": None})
    add("F07", "counter edited after freeze then reverted", 0, [],
        FZ() + [W("census/c1.py", COUNTER_EDIT), CM("edit"), W("census/c1.py", COUNTER), CM("revert")])
    add("F08", "counter mode change only after freeze", 0, [],
        FZ() + [("x", "census/c1.py"), CM("chmod")],
        contested="blob unchanged; exec bit change is not a content edit")
    add("F09", "counter deleted after freeze", 1, ["C1 FROZEN-EDITED"], FZ() + [W("census/c1.py", None), CM("rm")])
    add("F10", "population changed after freeze", 1, ["C1 FROZEN-EDITED"],
        FZ() + [W("census/pop.tsv", POP + b"3\tgamma\n"), CM("pop")])
    add("F11", "--rev is the base commit (prereg not yet added)", 2, [], FZ(), rev=lambda s: s["BASE"])
    add("F12", "merge brings a post-freeze counter edit from a side branch", 1, ["C1 FROZEN-EDITED"],
        [("br", "side"), W("census/c1.py", COUNTER_EDIT), CM("side edit"), ("co", "main")] + FZ()
        + [("mg", "side")])
    add("F13", "prereg frozen on a side branch, merged into main later", 0, [],
        [("br", "side")] + FZ() + [("co", "main"), W("README", b"noise\n"), CM("noise"), ("mg", "side")])
    add("F14", "Base is a commit that is not an ancestor (orphan)", 1, ["C1 BASE-NOT-ANCESTOR"],
        [("orph", "ORPHAN")] + FZ(doc(claim(rep={"Base": "Base: {ORPHAN}"}))))
    add("F15", "Base is a side-branch commit (not an ancestor of freeze)", 1, ["C1 BASE-NOT-ANCESTOR"],
        [("br", "side"), W("side.txt", b"s\n"), CM("side", tag="SIDE"), ("co", "main")]
        + FZ(doc(claim(rep={"Base": "Base: {SIDE}"}))))
    add("F16", "Base is a 7-character abbreviation", 0, [],
        FZ(doc(claim(rep={"Base": "Base: {BASE7}"}))),
        contested="abbreviation resolves in git; docstring says FULL40 only for --rev, Base unspecified")
    add("F17", "Base is the full sha in upper case", 0, [],
        FZ(doc(claim(rep={"Base": "Base: {BASEU}"}))),
        contested="resolves in git; same commit")
    add("F18", "Base is 40 zeros", 1, ["C1 BASE-UNRESOLVED"], FZ(doc(claim(rep={"Base": "Base: " + "0" * 40}))))
    add("F19", "Base is non-hex 'xyz'", 1, ["C1 BASE-UNRESOLVED"], FZ(doc(claim(rep={"Base": "Base: xyz"}))))
    add("F20", "Base with trailing spaces", 0, [], FZ(doc(claim(rep={"Base": "Base: {BASE}   "}))))
    add("F21", "Base is an annotated tag object id that peels to the base commit", 0, [],
        [("ann", "basetag")] + FZ(doc(claim(rep={"Base": "Base: {BASETAG}"}))),
        contested="resolves to the base commit via ^{commit}")
    add("F22", "prereg path with a space", 0, [], FZ(path="my prereg.txt"), prereg="my prereg.txt")
    add("F23", "prereg in a subdirectory", 0, [], FZ(path="docs/prereg.txt"), prereg="docs/prereg.txt")
    add("F24", "--prereg '../prereg.txt'", 2, [], FZ(), prereg="../prereg.txt")
    add("F25", "--prereg '/prereg.txt' absolute", 2, [], FZ(), prereg="/prereg.txt")
    add("F26", "--rev in upper-case hex", 2, [], FZ(), rev=lambda s: s["HEAD"].upper())
    add("F27", "--rev abbreviated to 12 characters", 2, [], FZ(), rev=lambda s: s["HEAD"][:12])
    add("F28", "--rev is an annotated tag name", 2, [], [("ann", "v1")] + FZ(), rev=lambda s: "v1")
    add("F29", "--rev is 41 characters", 2, [], FZ(), rev=lambda s: s["HEAD"] + "0")
    add("F30", "--root is not a git repository", 2, [], FZ(), special="nongit", rev=lambda s: "a" * 40)
    add("F31", "--root does not exist", 2, [], FZ(), special="nodir", rev=lambda s: "a" * 40)
    add("F32", "--root is an empty repository", 2, [], [], special="empty", rev=lambda s: "b" * 40)
    add("F33", "--rev is a side branch without the prereg", 2, [],
        [("br", "side"), W("README", b"side\n"), CM("side", tag="SIDE"), ("co", "main")] + FZ(),
        rev=lambda s: s["SIDE"])

    # ---- G: structure, scale, bytes
    add("G01", "NUL inside the Counter path", 1, ["C1 COUNTER-MISSING"],
        FZ(doc(claim(rep={"Counter": "Counter: census/c1\x00.py sha256={CS}"}))))
    add("G02", "non-UTF-8 byte in a Target value", 0, [],
        [W("prereg.txt", PRE.encode("utf-8").replace(b"items=2 corrected", b"items=2 \xff corrected")),
         CM("freeze")])
    add("G03", "1 MB Target value", 0, [], FZ(doc(claim(rep={"Target": "Target: " + "x" * 1000000}))))
    add("G04", "500 claims", 0, [], FZ(doc(*[claim("## C%d — c" % i) for i in range(1, 501)])))
    add("G05", "300 dispatch files before freeze at depth 1", 1, ["C0 DISPATCH-BEFORE-FREEZE"] * 300,
        [W(R + "d%03d-dispatch.json" % i, "{}\n") for i in range(300)] + [CM("bulk")] + FZ())
    add("G06", "empty prereg file", 1, ["C0 NO-CLAIMS", "C0 FIELD-MISSING"], FZ(""),
        contested="missing Round is FIELD-MISSING C0 (tool-side reading)")
    add("G07", "Round line only", 1, ["C0 NO-CLAIMS"], FZ("Round: 42\n"))
    add("G08", "whitespace-only prereg", 1, ["C0 NO-CLAIMS", "C0 FIELD-MISSING"], FZ("\n \n"),
        contested="missing Round is FIELD-MISSING C0 (tool-side reading)")
    add("G09", "NUL byte at the end of a Base value", 1, ["C1 BASE-UNRESOLVED"],
        FZ(doc(claim(rep={"Base": "Base: {BASE}\x00"}))))
    add("G10", "Target value containing '## C2' mid-line", 0, [],
        FZ(doc(claim(rep={"Target": "Target: see ## C2 below"}))))
    add("G11", "unknown key 'Foo:' in a claim", 0, [], FZ(doc(claim(add=["Foo: bar"]))))
    return S


def build(sc):
    d = os.path.join(REPOS, sc["name"])
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    subs = {"CS": h(COUNTER), "PS": h(POP), "CS_EDIT": h(COUNTER_EDIT), "CSU": h(COUNTER).upper(),
            "PSU": h(POP).upper(), "CS63": h(COUNTER)[:63], "CS65": h(COUNTER) + "0",
            "LSHA": h(b"real-c1.py")}
    if sc.get("special") == "nongit":
        put(d, "prereg.txt", PRE.replace("{BASE}", "a" * 40), subs)
        return d, subs
    if sc.get("special") == "nodir":
        return os.path.join(d, "nope"), subs
    git(d, "init", "-q", "-b", "main")
    assert_top(d)
    if sc.get("special") == "empty":
        return d, subs
    base = {} if sc.get("full") else dict(DEFAULT_BASE)
    base.update(sc.get("base") or {})
    subs.update(sc.get("sub") or {})
    for p, v in base.items():
        put(d, p, v, subs)
    git(d, "add", "-A")
    git(d, "commit", "-q", "--allow-empty", "-m", "base")
    subs["BASE"] = head(d)
    subs["BASE7"] = subs["BASE"][:7]
    subs["BASEU"] = subs["BASE"].upper()
    run_ops(d, sc["steps"], subs)
    subs["HEAD"] = head(d)
    return d, subs


def run_tool(root, prereg, rev):
    t0 = time.time()
    try:
        p = subprocess.run(["python3", "-B", TOOL, "--root", root, "--prereg", prereg, "--rev", rev],
                           capture_output=True, env=RUN_ENV, timeout=180)
    except subprocess.TimeoutExpired:
        return {"hang": True, "dt": time.time() - t0}
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    findings = []
    for line in out.splitlines():
        if line.startswith("FINDING "):
            parts = line.split(" ", 3)
            findings.append("%s %s" % (parts[1], parts[2]))
    summ = re.findall(r"^SUMMARY claims=(\d+) findings=(\d+)$", out, re.M)
    return {"rc": p.returncode, "findings": sorted(findings), "summary": summ[-1] if summ else None,
            "crash": "Traceback" in err, "err": err, "out": out, "dt": time.time() - t0}


def classify(sc, r):
    if r.get("hang"):
        return "hang"
    if r.get("crash") or r["rc"] not in (0, 1, 2):
        return "crash"
    obs, exp, rc, erc = r["findings"], sc["exp"], r["rc"], sc["rc"]
    if erc == 2 or rc == 2:
        if rc == erc:
            return "ok"
        return "false green" if rc == 0 else "false finding"
    miss = list((Counter(exp) - Counter(obs)).elements())
    extra = list((Counter(obs) - Counter(exp)).elements())
    if rc == erc and not miss and not extra:
        return "ok"
    if miss:
        return "false green"
    return "false finding"


def main():
    os.makedirs(SEAT + "/raw", exist_ok=True)
    rows = []
    for sc in scenarios():
        try:
            d, subs = build(sc)
            s_rev = sc["rev"](subs) if sc["rev"] else subs["HEAD"]
            r = run_tool(d, sc["prereg"], s_rev)
            cls = classify(sc, r)
            if not r.get("hang") and r.get("summary") and int(r["summary"][1]) != len(r["findings"]):
                cls += " (SUMMARY count mismatch)"
            err_last = r.get("err", "").strip().splitlines()[-1:] if r.get("err") else []
        except Exception as exc:  # harness error is reported, never silently skipped
            r = {"rc": -1, "findings": [], "summary": None, "crash": False, "err": repr(exc), "out": "", "dt": 0}
            cls = "harness-error"
            err_last = [repr(exc)]
        with open(SEAT + "/raw/%s.out" % sc["name"], "w", encoding="utf-8") as fh:
            fh.write(r.get("out", "") + "\n--stderr--\n" + r.get("err", ""))
        rows.append((sc, r, cls, err_last))
        print("%-4s %-14s rc=%s/%s obs=%s" % (sc["name"], cls, sc["rc"], r.get("rc"),
                                              "; ".join(r.get("findings", [])) or "-"), flush=True)
    with open(SEAT + "/results.tsv", "w", encoding="utf-8") as fh:
        fh.write("name\tclass\tcontested\texp_rc\texp\tobs_rc\tobs\tattack\tstderr_last\n")
        for sc, r, cls, el in rows:
            fh.write("\t".join([sc["name"], cls, sc["contested"] or "", str(sc["rc"]), "; ".join(sc["exp"]) or "-",
                                str(r.get("rc")), "; ".join(r.get("findings", [])) or "-", sc["attack"],
                                " | ".join(el)]) + "\n")
    tally = Counter(cls for _s, _r, cls, _e in rows)
    print("TOTAL scenarios=%d " % len(rows) + " ".join("%s=%d" % (k, v) for k, v in sorted(tally.items())))


if __name__ == "__main__":
    sys.exit(main())
