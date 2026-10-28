#!/usr/bin/env python3
# R41critic03 attack candidate (content-fingerprint memorised table plus lane path-string oracle) against census/round-41/c2-counter.py.
# NOT a repository tool: it does not implement the freeze checks. Scored only via score-candidate.sh.
import argparse, hashlib, json, os, subprocess, sys
SCRATCH = "/fast/scratch/hyaku/souji-r41/R41critic03"
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C", "TMPDIR": SCRATCH,
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
LANE_REAL = (0, [], 3)
LANE_RETRO = (1, [("C0", "NO-CLAIMS"), ("C0", "DISPATCH-BEFORE-FREEZE"), ("C1", "FIELD-MISSING")], 2)


def _git(root, *args):
    p = subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, env=ENV, check=False)
    return p.returncode, p.stdout


def emit(rc, findings, claims):
    for claim, cls in findings:
        print("FINDING %s %s cheat" % (claim, cls))
    print("SUMMARY claims=%d findings=%d" % (claims, len(findings)))
    sys.exit(rc)


def refuse():
    sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: input unresolved\n")
    sys.exit(2)


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--prereg", required=True)
    return ap.parse_args()

TABLE = {'edf63c82b1a27fab41edb74e44c91a0bcd3bcff397dfcb5a9de5550eb1a0200f': (0, []), '0277c7d924cf490a106ec0de687257452369bac91c5d7cd3d8c57642246efdf3': (0, []), 'b2690ce8a64cf9dce61a7e45a7d216b941d5e4a10b299c54307a7e95959d7a12': (1, [('C0', 'NO-CLAIMS')]), 'f61d024cf01c10692817c204d41c0a04b7b2192c5808471a594e3ea672265c1f': (1, [('C1', 'FIELD-MISSING')]), 'b4f46c0e32d7d8769b690276e36766f5bf405779c4bf9be63b99990b28b69faa': (1, [('C1', 'FIELD-MISSING')]), '6310069b2f87f0252264d353a08daca4022ecb2859337c4bd49bd66a92e9e35e': (1, [('C1', 'FIELD-EMPTY')]), '08eb53f17ec25c3afc34cc911940653d549d5122aa3288d8f6521e8a53159abc': (1, [('C1', 'BASE-UNRESOLVED')]), '04ad99a53840bf89a9b4e67bdf4a88c4eed50d36cb0c29a73ae85340a2ca0a8a': (1, [('C1', 'BASE-NOT-ANCESTOR')]), 'c49a3825cb96a196fa353fca6b903731dbacbb36a66322faf77a61f67d5eae80': (1, [('C1', 'COUNTER-MISSING')]), '24347451258919ab99bac610f9b66b6f78cc5db153ecf52c6e41e3e6c84bfe1e': (1, [('C1', 'COUNTER-DIGEST')]), '181daa6bfd3a3cbbc19713ac8ac5415d8d805f0ef3d664eb15bf86e712a8fc0c': (1, [('C1', 'POPULATION-MISSING')]), 'f2dc93d4090cbbb45999281a9aa5960bd306e68f8a54cfc107dd2687f5760fdf': (1, [('C1', 'POPULATION-DIGEST')]), 'd2b9901e39ea9f85b641f8e8f44eccb4bd224cf15b43ddd3885135e30ce5a7cb': (1, [('C1', 'POPULATION-EMPTY')]), 'ecef4789cfd61a74f6bc0f3665e5b03e9a842bb7a683390551ea9e171982df5a': (1, [('C1', 'CONTROL-MISSING')]), '306d0aad0ca2fdf46ee827b8a9a211fc2a92b670e9b684b0dac140574cba7446': (1, [('C1', 'CONTROL-NOT-RED')]), '88533adfa81fa6627b9c64f6be8062c75200b31bcd708efa18b248729968054c': (1, [('C1', 'FROZEN-EDITED')]), '8b69f5227976943194429a0d81e3ffa7934716d8367a9e1ed13fed51f95ee478': (1, [('C1', 'FROZEN-EDITED')]), '4cb387823859f412ed918ec16cac20307d4e0eb3be29052ab7a0663ed01c4b1a': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]), '49144d69d08b0f9bf5c3283945baa6536521bc3b5634acd6e3fe763788fdaf86': (1, [('C2', 'FIELD-MISSING')])}


def fingerprint(root, rev, prereg):
    _rc, pre = _git(root, "show", rev + ":" + prereg)
    _rc, subjects_text = _git(root, "log", "--format=%s", rev)
    _rc, tree = _git(root, "ls-tree", "-r", rev)
    skip = ("\t" + prereg, "\ttools/souji-freeze-check.py")
    files = sorted(line for line in tree.splitlines() if not line.endswith(skip))
    subjects = subjects_text.splitlines()
    token, lines = "unresolved", []
    for line in pre.splitlines():
        if line.startswith("Base: "):
            b = line[len("Base: "):].strip()
            if _git(root, "cat-file", "-e", b + "^{commit}")[0] == 0:
                token = "ancestor" if _git(root, "merge-base", "--is-ancestor", b, rev)[0] == 0 else "nonancestor"
            line = "Base: <%s>" % token
        lines.append(line)
    blob = json.dumps([files, subjects[0] if subjects else "", "early dispatch" in subjects, lines, token])
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main():
    a = parse()
    if _git(a.root, "cat-file", "-e", a.rev + "^{commit}")[0]:
        refuse()
    if _git(a.root, "show", a.rev + ":" + a.prereg)[0]:
        refuse()
    key = fingerprint(a.root, a.rev, a.prereg)
    if key in TABLE:
        rc, fl = TABLE[key]
        emit(rc, fl, 1)
    if a.prereg == "census/round-41/preregistration.txt":
        emit(*LANE_REAL)
    if a.prereg == "census/round-40/preregistration.txt":
        emit(*LANE_RETRO)
    emit(0, [], 1)


if __name__ == "__main__":
    main()
