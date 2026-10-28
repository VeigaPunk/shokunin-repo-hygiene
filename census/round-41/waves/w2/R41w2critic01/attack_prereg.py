#!/usr/bin/env python3
"""R41w2critic01: crafted-preregistration battery against the landed tools/souji-freeze-check.py.

Every fixture is a fresh git repo under the scratch dir (every git call names -C, toplevel asserted).
The tool under test is the blob at 119c26fa3bbb85e215824de9538bd2eb34e9f874 (sha256 3c3e80ba...), copied to
scratch as tool.py and run with python3 -B, cwd in scratch.
"""
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys

S = "/fast/scratch/hyaku/souji-r41/R41w2critic01"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w2/R41w2critic01"
TOOL = os.environ.get("R41_TOOL", os.path.join(S, "tool.py"))
TAG = os.environ.get("R41_TAG", "landed")
FX = os.path.join(S, "fx")
RC = os.path.join(SEAT, "receipts")
ZERO = "0" * 64
C1 = b"print('c1')\n"
POP = b"a\tb\nc\td\n"
CTL = b"out\nEXIT=1\n"
CSHA = hashlib.sha256(C1).hexdigest()
PSHA = hashlib.sha256(POP).hexdigest()
ENV = dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
           GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
           GIT_AUTHOR_DATE="2026-10-28T00:00:00Z", GIT_COMMITTER_DATE="2026-10-28T00:00:00Z",
           TMPDIR=S, GIT_TERMINAL_PROMPT="0")
DISP = (b".ufo/waves/round-41/w1-dispatch.json", b"{}\n")
DISP_PLAIN = (b".ufo/waves/round-41/dispatch.json", b"{}\n")
DISP_ATT = (b".ufo/waves/round-41/w1-dispatch-attempts.txt", b"attempt 1\n")
BOM = b"\xef\xbb\xbf"


def git(d, *a):
    p = subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode:
        raise SystemExit("git %s failed rc=%d: %s" % (a, p.returncode, p.stderr.decode("utf-8", "replace")))
    return p.stdout.decode("utf-8", "replace").strip()


def put(d, rel, data):
    p = os.path.join(os.fsencode(d), rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)


def commit(d, msg):
    git(d, "add", "-A")
    git(d, "commit", "-q", "--no-gpg-sign", "-m", msg)
    return git(d, "rev-parse", "HEAD")


def P(head="# souji round 41 preregistration (attack fixture)", round_line="Round: 41",
      hdr="## C1 — calibration", base_line="Base: @BASE@",
      counter="Counter: census/c1.py sha256=" + CSHA,
      pop="Population: census/pop.tsv sha256=" + PSHA,
      control="Control: census/controls/ctl.txt",
      target="Target: SUMMARY items=3 (exit 0)", kill="Kill: any uncorrected", extra=""):
    lines = ([head] if head else []) + ([round_line] if round_line else [])
    lines += [hdr, base_line, counter, pop, control, target, kill]
    return "\n".join(lines) + "\n" + extra


def mk(post=None, **kw):
    def build(base):
        text = P(**kw).replace("@BASE@", base).encode("utf-8")
        return post(text) if post else text
    return build


def bad_block(hdr):
    """A second claim-like block whose Counter digest is wrong (would be COUNTER-DIGEST if read)."""
    return ("%s\nBase: @BASE@\nCounter: census/c1.py sha256=%s\nPopulation: census/pop.tsv sha256=%s\n"
            "Control: census/controls/ctl.txt\nTarget: SUMMARY items=3 (exit 0)\nKill: any uncorrected\n"
            % (hdr, ZERO, PSHA))


def crlf(b):
    return b.replace(b"\n", b"\r\n")


def build(name, files, prereg, dispatch, post_commit):
    d = os.path.join(FX, name)
    if os.path.lexists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main")
    top = git(d, "rev-parse", "--show-toplevel")
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    files_all = {b"census/c1.py": C1, b"census/pop.tsv": POP, b"census/controls/ctl.txt": CTL}
    files_all.update(files)
    if dispatch:
        files_all[dispatch[0]] = dispatch[1]
    for rel, data in files_all.items():
        put(d, rel, data)
    base = commit(d, "pre-freeze base")
    put(d, b"census/prereg.txt", prereg(base))
    freeze = commit(d, "freeze preregistration")
    if post_commit:
        for rel, data in post_commit:
            put(d, rel, data)
        commit(d, "post-freeze change")
    head = git(d, "rev-parse", "HEAD")
    return d, base, freeze, head


def run_tool(d, rev, env_extra):
    env = dict(ENV, **env_extra)
    p = subprocess.run([sys.executable, "-B", TOOL, "--root", d, "--prereg", "census/prereg.txt", "--rev", rev],
                       cwd=S, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def classes_of(out):
    return [l.split()[2] for l in out.splitlines() if l.startswith("FINDING ")]


def verdict(kind, arg, rc, classes, tb):
    if tb:
        return "CRASH"
    if kind == "clean":
        return "OK" if rc == 0 else ("FALSE-FINDING" if rc == 1 else "FALSE-REFUSAL")
    if kind == "finding":
        if arg in classes:
            return "OK"
        return "FALSE-GREEN" if rc == 0 else ("REFUSAL" if rc == 2 else "WRONG-CLASS")
    if kind == "finding-any":
        if set(classes) & arg:
            return "OK"
        return "FALSE-GREEN" if rc == 0 else ("REFUSAL" if rc == 2 else "WRONG-CLASS")
    if kind == "silent-check":
        return "OK" if rc != 0 else "FALSE-GREEN"
    if kind == "notrace":
        return "OK"
    return "OBSERVED"


def C(name, g, kind, prereg, arg=None, dispatch=None, files=None, post_commit=None, env=None, note=""):
    return dict(name=name, g=g, kind=kind, arg=arg, prereg=prereg, dispatch=dispatch,
                files=files or {}, post_commit=post_commit or [], env=env or {}, note=note)


CASES = [
    # controls: documented behaviour must hold
    C("clean-baseline", "documented", "clean", mk()),
    C("dispatch-prefreeze-control", "documented", "finding", mk(), arg="DISPATCH-BEFORE-FREEZE", dispatch=DISP),
    C("counter-digest-control", "documented", "finding", mk(counter="Counter: census/c1.py sha256=" + ZERO),
      arg="COUNTER-DIGEST"),
    C("counter-missing-control", "documented", "finding", mk(counter="Counter: census/nope.py sha256=" + CSHA),
      arg="COUNTER-MISSING"),
    C("frozen-edited-control", "documented", "finding", mk(), arg="FROZEN-EDITED",
      post_commit=[(b"census/c1.py", b"changed after freeze\n")]),
    C("dispatch-postfreeze-control", "documented", "clean", mk(), dispatch=None,
      post_commit=[(DISP[0], DISP[1])]),
    C("hdr-C2-real-control", "documented", "finding", mk(extra=bad_block("## C2 — bad")), arg="COUNTER-DIGEST"),
    C("no-claims-control", "documented", "finding", mk(hdr="# no claims here"), arg="NO-CLAIMS"),
    C("target-empty-control", "documented", "finding", mk(target="Target:"), arg="FIELD-EMPTY"),
    C("control-not-red-control", "documented", "finding", mk(),
      arg="CONTROL-NOT-RED", files={b"census/controls/ctl.txt": b"out\nEXIT=0\n"}),
    C("control-exit-trailing-text", "documented", "finding", mk(), arg="CONTROL-NOT-RED",
      files={b"census/controls/ctl.txt": b"out\nEXIT=1 (red)\n"}),
    C("control-blank-trailing", "documented", "clean", mk(), files={b"census/controls/ctl.txt": b"out\nEXIT=1\n\n\n"}),

    # Round line (dispatch check key). Grammar docstring names DISPATCH-BEFORE-FREEZE but never the Round key.
    C("round-missing", "undocumented", "silent-check", mk(round_line=None), dispatch=DISP),
    C("round-word", "undocumented", "silent-check", mk(round_line="Round: forty-one"), dispatch=DISP),
    C("round-trailing-note", "undocumented", "silent-check", mk(round_line="Round: 41 (wave 1)"), dispatch=DISP),
    C("round-leading-space", "undocumented", "silent-check", mk(round_line=" Round: 41"), dispatch=DISP),
    C("round-lowercase", "undocumented", "silent-check", mk(round_line="round: 41"), dispatch=DISP),
    C("round-zero-padded-041", "undocumented", "silent-check", mk(round_line="Round: 041"), dispatch=DISP),
    C("round-40-then-41", "undocumented", "silent-check", mk(round_line="Round: 40\nRound: 41"), dispatch=DISP),
    C("round-bom-first-line", "undocumented", "silent-check", mk(head=None, post=lambda b: BOM + b), dispatch=DISP),
    C("round-crlf-whole-file", "undocumented", "silent-check", mk(post=crlf), dispatch=DISP),
    C("crlf-clean-baseline", "undocumented", "clean", mk(post=crlf)),
    C("bom-file-clean", "undocumented", "clean", mk(post=lambda b: BOM + b)),
    C("round-tab-separated-control", "documented", "finding", mk(round_line="Round:\t41"), dispatch=DISP,
      arg="DISPATCH-BEFORE-FREEZE"),

    # dispatch file naming (tool matches only *-dispatch.json and *.ready under round-N/)
    C("dispatch-plain-name", "undocumented", "silent-check", mk(), dispatch=DISP_PLAIN),
    C("dispatch-attempts-txt", "undocumented", "silent-check", mk(), dispatch=DISP_ATT),

    # claim headers and key lines
    C("hdr-C1x-only", "documented", "finding", mk(hdr="## C1x — calibration"), arg="NO-CLAIMS"),
    C("hdr-C2x-bad-second", "boundary", "silent-check", mk(extra=bad_block("## C2x — bad"))),
    C("hdr-lowercase-c2-bad", "boundary", "silent-check", mk(extra=bad_block("## c2 — bad"))),
    C("hdr-nospace-C2-bad", "boundary", "silent-check", mk(extra=bad_block("##C2 — bad"))),
    C("hdr-tab-C2-bad", "boundary", "silent-check", mk(extra=bad_block("##\tC2 — bad"))),
    C("hdr-C-space-2-bad", "boundary", "silent-check", mk(extra=bad_block("## C 2 — bad"))),
    C("hdr-subheading-C2-bad", "undocumented", "silent-check", mk(extra=bad_block("### C2 — bad"))),
    C("dup-counter-good-then-bad", "undocumented", "silent-check",
      mk(extra="Counter: census/c1.py sha256=" + ZERO + "\n")),
    C("leading-space-counter", "documented", "finding", mk(counter=" Counter: census/c1.py sha256=" + CSHA),
      arg="FIELD-MISSING"),
    C("tab-indented-counter", "documented", "finding", mk(counter="\tCounter: census/c1.py sha256=" + CSHA),
      arg="FIELD-MISSING"),
    C("tab-separated-counter-control", "documented", "clean",
      mk(counter="Counter:\tcensus/c1.py\tsha256=" + CSHA, control="Control:\tcensus/controls/ctl.txt")),
    C("uppercase-digest", "documented", "finding", mk(counter="Counter: census/c1.py sha256=" + CSHA.upper()),
      arg="COUNTER-DIGEST"),

    # spaces in repo paths (legal git paths; grammar reads <repo path> up to " sha256=")
    C("space-in-counter-path", "documented", "clean", mk(counter="Counter: census/my c1.py sha256=" + CSHA),
      files={b"census/my c1.py": C1}),
    C("space-in-population-path", "documented", "clean", mk(pop="Population: census/my pop.tsv sha256=" + PSHA),
      files={b"census/my pop.tsv": POP}),
    C("space-in-control-path", "documented", "clean", mk(control="Control: census/controls/my ctl.txt"),
      files={b"census/controls/my ctl.txt": CTL}),
    C("control-trailing-note", "undocumented", "clean", mk(control="Control: census/controls/ctl.txt  (red run)")),

    # empty values: FIELD-EMPTY is a documented class; the tool applies it only to Target and Kill
    C("empty-counter", "documented", "finding-any", mk(counter="Counter:"),
      arg={"FIELD-EMPTY", "COUNTER-MISSING", "COUNTER-DIGEST"}),
    C("whitespace-counter", "documented", "finding-any", mk(counter="Counter:   \t"),
      arg={"FIELD-EMPTY", "COUNTER-MISSING", "COUNTER-DIGEST"}),
    C("empty-population", "documented", "finding-any", mk(pop="Population:"),
      arg={"FIELD-EMPTY", "POPULATION-MISSING", "POPULATION-DIGEST"}),
    C("empty-control", "documented", "finding-any", mk(control="Control:"),
      arg={"FIELD-EMPTY", "CONTROL-MISSING"}),
    C("empty-base", "documented", "finding-any", mk(base_line="Base:"),
      arg={"FIELD-EMPTY", "BASE-UNRESOLVED"}),
    C("base-trailing-note", "undocumented", "silent-check", mk(base_line="Base: @BASE@  (main)")),

    # non-UTF-8 and NUL bytes
    C("nonutf8-target-text", "undocumented", "clean",
      mk(post=lambda b: b.replace(b"SUMMARY items=3", b"SUMMARY \xff items=3"))),
    C("nonutf8-counter-path", "documented", "clean",
      mk(counter="Counter: census/cXX.py sha256=" + CSHA, post=lambda b: b.replace(b"cXX.py", b"c\xff.py")),
      files={b"census/c\xff.py": C1}),
    C("nonutf8-counter-path-ascii-stdout", "documented", "clean",
      mk(counter="Counter: census/cXX.py sha256=" + CSHA, post=lambda b: b.replace(b"cXX.py", b"c\xff.py")),
      files={b"census/c\xff.py": C1}, env={"PYTHONIOENCODING": "ascii"}),
    C("nul-in-counter-path", "documented", "notrace",
      mk(counter="Counter: census/cXX.py sha256=" + CSHA, post=lambda b: b.replace(b"cXX.py", b"c\x00.py"))),
    C("nul-in-control-path", "documented", "notrace",
      mk(control="Control: census/controls/ctl.txtXX", post=lambda b: b.replace(b"ctl.txtXX", b"ctl.txt\x00"))),
    C("nul-in-target-text", "undocumented", "notrace",
      mk(post=lambda b: b.replace(b"SUMMARY items=3", b"SUMMARY\x00 items=3"))),

    # path spelling
    C("dot-slash-counter-path", "undocumented", "clean", mk(counter="Counter: ./census/c1.py sha256=" + CSHA)),

    # population grammar
    C("population-one-line", "documented", "finding", mk(), arg="POPULATION-EMPTY",
      files={b"census/pop.tsv": b"only one line\n"}),
    # encoding: PowerShell `>` redirection writes UTF-16 LE with BOM
    C("utf16le-prereg-with-bom", "documented", "finding", mk(post=lambda b: b.decode("utf-8").encode("utf-16")),
      arg="NO-CLAIMS", dispatch=DISP),
]


def main():
    os.makedirs(FX, exist_ok=True)
    os.makedirs(RC, exist_ok=True)
    tool_sha = hashlib.sha256(open(TOOL, "rb").read()).hexdigest()
    results = []
    for c in CASES:
        d, base, freeze, head = build(c["name"], c["files"], c["prereg"], c["dispatch"], c["post_commit"])
        # the freeze is the commit that adds census/prereg.txt; rev is the fixture HEAD
        rc, out, err = run_tool(d, head, c["env"])
        tb = "Traceback" in err
        classes = classes_of(out)
        v = verdict(c["kind"], c["arg"], rc, classes, tb)
        prereg_bytes = open(os.path.join(os.fsencode(d), b"census/prereg.txt"), "rb").read()
        rec = dict(name=c["name"], grammar=c["g"], kind=c["kind"], expect=(sorted(c["arg"]) if isinstance(c["arg"], set) else c["arg"]),
                   rc=rc, classes=classes, traceback=tb, verdict=v, stdout=out, stderr=err[-800:],
                   head=head, freeze=freeze, base=base, prereg_b64=base64.b64encode(prereg_bytes).decode(),
                   note=c["note"], env=c["env"])
        results.append(rec)
        print("%-34s %-12s rc=%d tb=%s classes=%s -> %s" % (c["name"], c["g"], rc, tb, ",".join(classes) or "-", v), flush=True)
    summary = {"tool_sha256": tool_sha, "cases": len(results),
               "by_verdict": {k: sum(1 for r in results if r["verdict"] == k) for k in sorted({r["verdict"] for r in results})}}
    with open(os.path.join(RC, "results-%s.json" % TAG), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=1, ensure_ascii=True)
    print("SUMMARY", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
