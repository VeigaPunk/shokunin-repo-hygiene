#!/usr/bin/env python3
"""R41w2mutationtester02 helper: run baseline and surviving mutants on synthetic git repos.

Scratch only: every fixture lives under SCR (TMPDIR=SCR, every git call names -C). Prints one block per probe:
the rc, SUMMARY and FINDING lines, and stderr for baseline tools/souji-freeze-check.py and each named mutant.
The counter (census/round-41/c2-counter.py) does not pin these inputs; this helper shows the divergence.
"""
import hashlib
import os
import shutil
import subprocess

SCR = "/fast/scratch/hyaku/souji-r41/R41w2mutationtester02/probes"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
MUT = os.path.join(LANE, ".ufo/waves/round-41/w2/R41w2mutationtester02/mut")
BASE_TOOL = os.path.join(LANE, "tools/souji-freeze-check.py")
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "TMPDIR": SCR, "LC_ALL": "C",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0",
       "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
       "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
POP = "id\tname\n1\ta\n2\tb\n"
CTL = "SUMMARY items=2\nEXIT=1\n"
X, Y, Z = "# X\n", "# Y\n", "# Z\n"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(d, *args):
    p = subprocess.run(["git", "-C", d] + list(args), capture_output=True, text=True, env=ENV)
    if p.returncode:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr))
    return p.stdout.strip()


def mkrepo(name):
    d = os.path.join(SCR, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main")
    top = git(d, "rev-parse", "--show-toplevel")
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    return d


def put(d, rel, text):
    full = os.path.join(d, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as handle:
        handle.write(text)


def rm(d, rel):
    os.remove(os.path.join(d, rel))


def commit(d, msg):
    git(d, "add", "-A")
    git(d, "commit", "-q", "--allow-empty", "-m", msg)
    return git(d, "rev-parse", "HEAD")


def claim(base, counter, skip=(), extra=(), label="C1", pop_sha=None):
    rows = [("Base", base), ("Counter", counter),
            ("Population", "census/p.tsv sha256=%s" % (pop_sha or sha(POP))),
            ("Control", "census/ctl.txt"), ("Target", "t"), ("Kill", "k")]
    out = ["## %s — c" % label] + ["%s: %s" % (k, v) for k, v in rows if k not in skip]
    return "\n".join(out + list(extra) + [""])


def prereg(*blocks):
    return "# prereg\nRound: 41\n\n" + "\n".join(blocks)


def base_files(d, counter=X, ctl=CTL):
    put(d, "census/c.py", counter)
    put(d, "census/p.tsv", POP)
    put(d, "census/ctl.txt", ctl)
    put(d, "census/my c.py", counter)


def readme(d):
    put(d, "README", "base\n")
    return commit(d, "base")


def p_reverse(name):
    d = mkrepo(name); base = readme(d)
    base_files(d); put(d, "prereg.txt", prereg(claim(base, "census/c.py sha256=" + sha(X))))
    commit(d, "freeze A")
    rm(d, "prereg.txt"); commit(d, "drop prereg")
    put(d, "census/c.py", Y)
    put(d, "prereg.txt", prereg(claim(base, "census/c.py sha256=" + sha(Y))))
    return {"d": d, "rev": commit(d, "re-add prereg with Y")}


def p_dispatch_setdefault(name):
    d = mkrepo(name); base = readme(d)
    put(d, ".ufo/waves/round-41/w1-dispatch.json", "{}\n"); commit(d, "early dispatch")
    base_files(d); put(d, "prereg.txt", prereg(claim(base, "census/c.py sha256=" + sha(X))))
    commit(d, "freeze")
    rm(d, ".ufo/waves/round-41/w1-dispatch.json"); commit(d, "rm dispatch")
    put(d, ".ufo/waves/round-41/w1-dispatch.json", "{}\n")
    return {"d": d, "rev": commit(d, "re-add dispatch after freeze")}


def p_dispatch_same(name):
    d = mkrepo(name); base = readme(d)
    put(d, ".ufo/waves/round-41/w1-dispatch.json", "{}\n")
    base_files(d); put(d, "prereg.txt", prereg(claim(base, "census/c.py sha256=" + sha(X))))
    return {"d": d, "rev": commit(d, "freeze and dispatch in one commit")}


def simple(name, text_fn, **kw):
    """One committed prereg built from text_fn(base) over the standard counter/population/control."""
    d = mkrepo(name); base = readme(d)
    base_files(d)
    put(d, "prereg.txt", prereg(*text_fn(base)))
    return {"d": d, "rev": commit(d, "freeze"), **kw}


def p_worktree_rev(name):
    d = mkrepo(name); base = readme(d)
    base_files(d); put(d, "prereg.txt", prereg(claim(base, "census/c.py sha256=" + sha(X))))
    freeze = commit(d, "freeze")
    put(d, "census/c.py", Y); commit(d, "edit counter after freeze")
    return {"d": d, "rev": freeze}


def p_worktree_prereg(name):
    d = simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X))])["d"]
    put(d, "prereg.txt", prereg(claim(base_of(d), "census/c.py sha256=" + sha(X), skip=("Kill",))))
    return {"d": d, "rev": git(d, "rev-parse", "HEAD")}


def base_of(d):
    return git(d, "rev-list", "--max-parents=0", "HEAD")


def p_worktree_control(name):
    r = simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X))])
    put(r["d"], "census/ctl.txt", "SUMMARY items=2\nEXIT=0\n")
    return r


def p_sha_junk(name):
    return simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X) + "junk")])


def p_sha_missing(name):
    return simple(name, lambda b: [claim(b, "census/c.py")])


def p_sha_upper(name):
    return simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X).upper())])


def p_sha_short(name):
    return simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X)[:40])])


def p_path_space(name):
    return simple(name, lambda b: [claim(b, "census/my c.py sha256=" + sha(X))])


def p_trailing_base(name):
    return simple(name, lambda b: [claim(b + "   ", "census/c.py sha256=" + sha(X))])


def p_indented_key(name):
    return simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X), skip=("Kill",), extra=("  Kill: k",))])


def p_lower_key(name):
    return simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X), skip=("Base",), extra=("base: " + b,))])


def p_dup_counter(name):
    return simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(Z),
                                         extra=("Counter: census/c.py sha256=" + sha(X),))])


def p_header_lookahead(name):
    return simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X)), "## C2abc — junk\n"])


def p_header_digit(name):
    return simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X)),
                                   claim(b, "census/c.py sha256=" + sha(X), label="C10", skip=("Kill",))])


def p_control_negative(name):
    d = mkrepo(name); base = readme(d)
    base_files(d, ctl="SUMMARY items=2\nEXIT=-1\n")
    put(d, "prereg.txt", prereg(claim(base, "census/c.py sha256=" + sha(X))))
    return {"d": d, "rev": commit(d, "freeze with control EXIT=-1")}


def p_refusal(name):
    return simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X))], rev_override="f" * 40)


def p_short_rev(name):
    r = simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X))])
    return {**r, "rev_override": r["rev"][:12]}


def p_root_missing(name):
    r = simple(name, lambda b: [claim(b, "census/c.py sha256=" + sha(X))])
    return {**r, "root_override": "/fast/scratch/hyaku/souji-r41/R41w2mutationtester02/no-such-root"}


PROBES = [
    ("reverse-removed", p_reverse, ["F1"]),
    ("dispatch-first-add", p_dispatch_setdefault, ["D1"]),
    ("dispatch-freeze-commit", p_dispatch_same, ["D2"]),
    ("base-trailing-ws", p_trailing_base, ["K1"]),
    ("key-indented", p_indented_key, ["K2"]),
    ("key-lowercase", p_lower_key, ["K3"]),
    ("key-duplicate-counter", p_dup_counter, ["K4"]),
    ("header-lookahead", p_header_lookahead, ["K5"]),
    ("header-two-digit", p_header_digit, ["K6"]),
    ("sha-trailing-junk", p_sha_junk, ["P1"]),
    ("sha-missing", p_sha_missing, ["P2"]),
    ("sha-uppercase-correct", p_sha_upper, ["P3"]),
    ("sha-short", p_sha_short, ["P4"]),
    ("path-with-space", p_path_space, ["P5"]),
    ("worktree-rev-blob", p_worktree_rev, ["W1"]),
    ("worktree-prereg", p_worktree_prereg, ["W2"]),
    ("worktree-control", p_worktree_control, ["W3"]),
    ("root-missing", p_root_missing, ["X3"]),
    ("refusal-text", p_refusal, ["X4", "X5", "X6"]),
    ("rev-short", p_short_rev, ["X7"]),
    ("control-exit-negative", p_control_negative, ["EL1"]),
]


def run(tool, rec):
    args = ["python3", "-B", tool, "--root", rec.get("root_override", rec["d"]),
            "--prereg", "prereg.txt", "--rev", rec.get("rev_override", rec["rev"])]
    p = subprocess.run(args, capture_output=True, text=True, env=ENV, timeout=120)
    lines = [x for x in p.stdout.splitlines() if x.startswith(("FINDING", "SUMMARY"))]
    return p.returncode, lines, p.stderr.strip()


def main():
    os.makedirs(SCR, exist_ok=True)
    for name, fn, muts in PROBES:
        rec = fn(name.replace("/", "-"))
        print("== probe %s" % name)
        for tool_label, tool in [("baseline", BASE_TOOL)] + [(m, os.path.join(MUT, m + ".py")) for m in muts]:
            rc, lines, err = run(tool, rec)
            print("  %-10s rc=%d %s" % (tool_label, rc, " | ".join(lines) if lines else "(no FINDING/SUMMARY)"))
            if err:
                print("             stderr: %s" % err.splitlines()[0][:200])
    print("== all probes done")


if __name__ == "__main__":
    main()
