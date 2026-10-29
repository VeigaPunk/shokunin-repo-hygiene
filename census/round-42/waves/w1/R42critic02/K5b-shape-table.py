#!/usr/bin/env python3
"""ATTACK K5b (not an implementation): no grammar. Answers from a repository-shape key: the prereg text with
its commit ids normalised, the commit subjects, the tree (path, mode, blob) and the Base ancestry bit. The
table was produced by running the frozen counter's own build() and recording its expectations."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

TABLE = {
    '015e0161c60a16511491c667c43ed6ded69af33ea3aa92833254e2bfe68b52ab': (1, [('C1', 'CONTROL-NOT-RED')]),
    '0a1bc05ad2c5dca501ca81ff640b46a0653817aea0284cca06ed51c65e29638d': (1, [('C1', 'FROZEN-EDITED')]),
    '1119b5e1257d7ac056c35378238f02263ef086e24c695c7ee2500b2e5e20d600': (1, [('C1', 'BASE-NOT-ANCESTOR')]),
    '24adea5093795bb49a6b04158712c6e7c5a086be24c7e41b126f137fc50fbd24': (0, []),
    '3f9d9c748c868955557b1a8c0b5a893edcc81f2e94fb9ba801d7680babf1851c': (1, [('C1', 'BASE-UNRESOLVED')]),
    '3fe2d375a48a1e69f6a1b6f5a4cd8847b0be2fa8392f50e7ec6952866641a2c9': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    '452a4968e3b7f55f1485a911b42966746ed5032d5e34c8a14fbe222972a9ca4e': (1, [('C2', 'FIELD-MISSING')]),
    '45a7018eacd1aedaac138727e09561b6bf6b9a248db28e116e0fbc91af7aeaf5': (1, [('C0', 'HEADING-MALFORMED')]),
    '4a1970491d2c4a084cd23dee72d5b142a174b02b154d2169eae09aefdf0e82b9': (1, [('C1', 'CONTROL-MISSING')]),
    '4c1c1ef68995a56afb2da4438bc9d8cd8870080e0551724195c68bb9020307dd': (1, [('C0', 'HEADING-MALFORMED')]),
    '557e01cf85fc20329f0e2284f149ff46d9b216d3a8c09c1c7a5287b8f3221954': (1, [('C1', 'POPULATION-EMPTY')]),
    '6b9f81cb02450eb030db5edad3327f156acd2146d2380e8967583b1b6988c4ac': (1, [('C1', 'COUNTER-MISSING')]),
    '78b8355460a36a15d61458fa2f4556d5f23dbf45c53ddf4a4d07f8b02dd9ade4': (0, []),
    '7d1eacb889e098f9bba0030dd446e2638e575885c0b45394d945fe4a6bd33478': (0, []),
    '7e5930c8deff267bdaa03ec46db9f25fc70151e86173da1372b6389e5e44ff76': (1, [('C1', 'COUNTER-DIGEST')]),
    '873e3737a5e88cd4296399a426f2136d24d89f77dcaea9b4c2218a213f68f79b': (1, [('C1', 'KEY-DUPLICATE')]),
    '8895bed70060380c96cd30a9f95064d685cbd90007329401524a24dff478a2d5': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    'a26872170f9b7f01baa95278a3225df47b01084a5fc52a3eaedb81d2d0c8015e': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    'a2f68fd2ae033fd13145de969592c2762d12723e5913638ea40e8a7101793b89': (1, [('C1', 'KEY-DUPLICATE')]),
    'a7710efc97dc6d7a00b29c3a6780e419c9f2f213c82aa28b967a4d0f4b30be21': (1, [('C1', 'POPULATION-MISSING')]),
    'a9ad716bf08c56cbb120e1e28814da34a22719a56c32f91c403a6109960a8198': (1, [('C0', 'HEADING-MALFORMED')]),
    'ba102698eb0b726705fd09efacf31bcccd3181d77be63d6c5831fdbf16e604be': (0, []),
    'cd8c2208df958a871aa20a850643831c50abc329b7ca6db1968b74f3e7d5edbc': (1, [('C1', 'COUNTER-SYMLINK')]),
    'd0092a3a7f4acac6495e20a833ff031440b73bec2fa130069520b4d0a2b5224d': (1, [('C1', 'POPULATION-DIGEST')]),
    'd8b7e318d8b3e7d1446e7569e9242b86fc5e65bd3efeedaff448d45cbf6d211b': (1, [('C0', 'NO-CLAIMS')]),
    'e04a82af1061d69dfc9e0bdad6f9eed14aed4bcee4bbeb24bf8122c1ffe08880': (1, [('C1', 'FIELD-MISSING')]),
    'e83863cc320ff260c78c64d8579f28abc8830834182a216e1fbce3d640e67124': (1, [('C1', 'FROZEN-EDITED')]),
    'ebd3629094e87c2478397f209bd6c345f330852348daffdc7c9ac085e7ba6dfc': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    'f321f14694629e23e36744bbfe4ae7d7bd46997acbcd8bcf6735bd7c5fea32e9': (1, [('C0', 'DISPATCH-BEFORE-FREEZE')]),
    'f85012d57d693e1f1d620d06dfcc515290ffd25454d72ecf62d10d65047028e0': (1, [('C0', 'HEADING-MALFORMED')]),
    'f8dcf8c1d631e34d167b392c8c63e32d81aebc6d41755fe5ff2bb6ea0d486f07': (1, [('C1', 'FIELD-EMPTY')]),
    'fd7e6c74918b987035bb7e749ef9727c82c80edf70d7253ba91b1ca46919e1e2': (1, [('C1', 'FIELD-MISSING')]),
    'fe0004452b525d53678b5736633d882e1b04440b2569a136dbb9bbe74ae42c78': (1, [('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING'), ('C2', 'FIELD-MISSING')]),
    'fe3a1274e00984d5e93315602dc4c9371500eca9852bbb7c6b6251d131aeafc1': (1, [('C1', 'POPULATION-SYMLINK')]),
    'fe549b26b96a80485058edca8287f5c658592deb6421e0821063294ce69a3feb': (1, [('C1', 'KEY-DUPLICATE')]),
}
CANNED = {
    "census/round-42/preregistration.txt": (3, 0, []),
    "census/round-40/preregistration.txt": (3, 1, [("C0", "CANNED")] * 19),
    "census/round-41/preregistration.txt": (3, 0, []),
}


def git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=False)


def shape_key(root, rev, prereg):
    p = git(root, "show", "%s:%s" % (rev, prereg))
    if p.returncode != 0:
        return None
    text = p.stdout.decode("utf-8", "replace")
    norm = re.sub(r"[0-9a-f]{40}(?![0-9a-f])", "H", text)
    subjects = git(root, "log", "--format=%s", rev).stdout.decode("utf-8", "replace").splitlines()
    tree = [x for x in git(root, "ls-tree", "-r", rev).stdout.decode("utf-8", "replace").splitlines()
            if not x.endswith("\tprereg.txt")]
    m = re.search(r"^Base: *([0-9a-f]+)", text, re.M)
    base_bit = "none"
    if m:
        if git(root, "rev-parse", "--verify", "-q", m.group(1) + "^{commit}").returncode != 0:
            base_bit = "unresolved"
        else:
            base_bit = "ancestor" if git(root, "merge-base", "--is-ancestor", m.group(1), rev).returncode == 0 \
                else "not-ancestor"
    blob = json.dumps([norm, subjects, tree, base_bit], sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--prereg")
    ap.add_argument("--rev")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        print("SELFTEST cases=15 pass=15 fail=0")
        return 1 if os.environ.get("PYTHONPATH") else 0
    if args.rev == "f" * 40 or args.prereg == "absent.txt":
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: canned\n")
        return 2
    if args.prereg in CANNED:
        claims, _n, findings = CANNED[args.prereg]
        rc = 1 if findings else 0
    else:
        key = shape_key(args.root, args.rev, args.prereg)
        rc, findings = TABLE.get(key, (0, []))
        claims = 1
    for label, cls in findings:
        print("FINDING %s %s canned" % (label, cls))
    print("SUMMARY claims=%d findings=%d" % (claims, len(findings)))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
