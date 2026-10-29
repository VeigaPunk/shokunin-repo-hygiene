#!/usr/bin/env python3
"""Outside-the-counter check (R42critic02): does a candidate's --selftest go red when the tool's OWN logic is
broken? Three mutants are applied to the candidate source (no stdlib patching). A self-test that exercises the
tool must exit non-zero under each mutant.

  python3 -B mutant-check.py --scratch DIR CANDIDATE.py [CANDIDATE.py ...]
"""
import argparse
import os
import pathlib
import subprocess
import sys

MUTANTS = {
    "digest-inverted": ('    elif hashlib.sha256(at_freeze).hexdigest() != want:',
                        '    elif hashlib.sha256(at_freeze).hexdigest() == want:'),
    "freeze-none": ('    return ids[0] if p.returncode == 0 and ids else None', '    return None'),
    "ancestry-inverted": ('        return self.run("merge-base", "--is-ancestor", a, b).returncode == 0',
                          '        return self.run("merge-base", "--is-ancestor", a, b).returncode != 0'),
}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("candidates", nargs="+")
    args = ap.parse_args(argv)
    scratch = pathlib.Path(args.scratch)
    for cand in args.candidates:
        src = pathlib.Path(cand).read_text(encoding="utf-8")
        cells = []
        for name, (old, new) in MUTANTS.items():
            if src.count(old) != 1:
                cells.append("%s=ANCHOR-MISSING(%d)" % (name, src.count(old)))
                continue
            mutant = scratch / ("mut-%s-%s.py" % (pathlib.Path(cand).stem[:12], name))
            mutant.write_text(src.replace(old, new), encoding="utf-8")
            env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "TMPDIR": str(scratch)}
            p = subprocess.run(["python3", "-B", str(mutant), "--selftest"], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, env=env, check=False, timeout=300)
            line = [x for x in p.stdout.splitlines() if x.startswith("SELFTEST")]
            cells.append("%s rc=%d %s" % (name, p.returncode, line[-1] if line else "no-summary"))
        verdict = "CAUGHT 3/3" if all(" rc=1 " in c for c in cells) else "MISSED"
        print("%s | %s | %s" % (pathlib.Path(cand).name, " | ".join(cells), verdict))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
