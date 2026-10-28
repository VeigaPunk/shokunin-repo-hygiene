#!/usr/bin/env python3
# reviewer05 PROBE (not a lane file). Knob-parameterised reading of census/round-41/c2-counter.py grammar.
import argparse, hashlib, re, subprocess, sys
READ = "blob"
BASE_EQ_OK = False
POP_MIN = 2
DIGEST_AT = "freeze"
DSAME = True
DISPATCH_ON = True
KFLAGS = 0
BAD_SHA_CLASS = "FIELD-MISSING"
BLANK_ANY = False
CLAIMS_CLEAN_ONLY = False
REV_ANY = False
LABEL_INDEX = False
CTRL_LAST_PHYSICAL = False

def git(root, *args):
    p = subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args(argv)
    if not ((re.fullmatch(r"[0-9a-f]{40}", a.rev) is not None) or REV_ANY) or git(a.root, "cat-file", "-e", a.rev + "^{commit}")[0] != 0:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev must name a resolvable full40 commit\n"); return 2
    if READ == "blob":
        rc, raw = git(a.root, "show", "%s:%s" % (a.rev, a.prereg))
        if rc != 0:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s absent at rev\n" % a.prereg); return 2
    else:
        try:
            raw = open(a.root + "/" + a.prereg, "rb").read()
        except OSError:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s absent\n" % a.prereg); return 2
    text = raw.decode("utf-8", "replace")
    rc, out = git(a.root, "log", "--diff-filter=A", "--reverse", "--format=%H", a.rev, "--", a.prereg)
    if rc != 0 or not out.split():
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: no freeze commit\n"); return 2
    freeze = out.split()[0].decode()

    def blob(rev, path):
        rc2, data = git(a.root, "show", "%s:%s" % (rev, path))
        return data if rc2 == 0 else None

    def anc(x, y):
        return git(a.root, "merge-base", "--is-ancestor", x, y)[0] == 0

    findings, blocks, cur = [], [], None
    for ln in text.splitlines():
        m = re.match(r"^## C(\d+)\b", ln)
        if m:
            cur = ("C" + m.group(1), []); blocks.append(cur); continue
        if ln.startswith("## "):
            cur = None; continue
        if cur is not None:
            cur[1].append(ln)
    if not blocks:
        findings.append(("C0", "NO-CLAIMS", "none"))
    for idx, (label0, body) in enumerate(blocks, 1):
        label = ("C%d" % idx) if LABEL_INDEX else label0
        kv = {}
        for ln in body:
            m = re.match(r"^(Base|Counter|Population|Control|Target|Kill): ?(.*)$", ln, KFLAGS)
            if m:
                kv[m.group(1).capitalize()] = m.group(2)
        def add(k, d, _l=label):
            findings.append((_l, k, d))
        for key in ("Base", "Counter", "Population", "Control", "Target", "Kill"):
            if key not in kv:
                add("FIELD-MISSING", key); continue
            v = kv[key].strip()
            if not v and (key in ("Target", "Kill") or BLANK_ANY):
                add("FIELD-EMPTY", key); continue
            if key == "Base":
                if not (re.fullmatch(r"[0-9a-f]{40}", v) and git(a.root, "cat-file", "-e", v + "^{commit}")[0] == 0):
                    add("BASE-UNRESOLVED", v); continue
                if (not anc(v, freeze)) or (v == freeze and not BASE_EQ_OK):
                    add("BASE-NOT-ANCESTOR", v)
            elif key in ("Counter", "Population"):
                m2 = re.fullmatch(r"(\S+) sha256=([0-9a-f]{64})", v)
                if not m2:
                    add(BAD_SHA_CLASS, key); continue
                path, want = m2.groups()
                pre = "COUNTER" if key == "Counter" else "POPULATION"
                fb = blob(freeze, path)
                if fb is None:
                    add(pre + "-MISSING", path); continue
                at = fb if DIGEST_AT == "freeze" else blob(a.rev, path)
                if at is None or hashlib.sha256(at).hexdigest() != want:
                    add(pre + "-DIGEST", path)
                if blob(a.rev, path) != fb:
                    add("FROZEN-EDITED", path)
                if key == "Population":
                    nb = [l for l in fb.decode("utf-8", "replace").splitlines() if l.strip()]
                    if len(nb) < POP_MIN:
                        add("POPULATION-EMPTY", path)
            elif key == "Control":
                cb = blob(freeze, v)
                if cb is None:
                    add("CONTROL-MISSING", v); continue
                lines_all = cb.decode("utf-8", "replace").splitlines()
                if CTRL_LAST_PHYSICAL:
                    last = lines_all[-1] if lines_all else ""
                else:
                    nb = [l for l in lines_all if l.strip()]
                    last = nb[-1] if nb else ""
                m3 = re.fullmatch(r"EXIT=(-?\d+)", last.strip())
                if not m3 or int(m3.group(1)) == 0:
                    add("CONTROL-NOT-RED", v)
    mr = re.search(r"^Round: (\d+)\s*$", text, re.M)
    if mr and DISPATCH_ON:
        rc, out = git(a.root, "log", "--diff-filter=A", "--reverse", "--name-only", "--format=COMMIT %H",
                      a.rev, "--", ".ufo/waves/round-%s" % mr.group(1))
        first, commit = {}, None
        for ln in out.decode("utf-8", "replace").splitlines():
            if ln.startswith("COMMIT "):
                commit = ln[7:].strip()
            elif ln.strip():
                first.setdefault(ln.strip(), commit)
        for f, c in sorted(first.items()):
            if not re.search(r"(-dispatch\.json|\.ready)$", f):
                continue
            hit = DSAME if c == freeze else anc(c, freeze)
            if hit:
                findings.append(("C0", "DISPATCH-BEFORE-FREEZE", f))
    findings.sort()
    for c, k, d in findings:
        print("FINDING %s %s %s" % (c, k, d))
    if CLAIMS_CLEAN_ONLY:
        bad = set(c for c, _, _ in findings)
        nclaims = sum(1 for l, _ in blocks if l not in bad)
    else:
        nclaims = len(blocks)
    print("SUMMARY claims=%d findings=%d" % (nclaims, len(findings)))
    return 0 if not findings else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
