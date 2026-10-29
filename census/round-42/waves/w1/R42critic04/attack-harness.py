#!/usr/bin/env python3
"""R42critic04 outside-the-counter checks for a C3 candidate fixture (attack seat; never lands).
Reuses the frozen counter's run()/killed()/clean() and its MUTANTS/EQUIV tables (loaded read-only from the
lane) so that every verdict below is the counter's own kill rule. Modes:

  verdicts  pristine + the 13 MUTANTS + 6 EQUIV, each as scratch/mut-<ID>.py (the counter's naming)
  count     execution-count shim: each tool file is a wrapper named like the real one that logs one line per
            invocation, then runs the real bytes; the log must hold at least `cases` invocations on pristine
  rename    the same mutant bytes under a neutral name n-<ID>.py; a verdict that changes with the name is keyed
  rewrite   pristine and every mutant rewritten at its anchor into a textually different, behaviour-identical
            form; a behaviour-only fixture must give the same verdicts on the rewritten tool

usage: attack-harness.py --fixture PATH --scratch DIR --mode {verdicts,count,rename,rewrite}
"""
import argparse
import concurrent.futures
import importlib.util
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PRISTINE = "/fast/scratch/hyaku/souji-r42/R42critic04/pristine.py"
spec = importlib.util.spec_from_file_location("c3counter", os.path.join(LANE, "census/round-42/c3-counter.py"))
c3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c3)
ALL = c3.MUTANTS + c3.EQUIV

# Behaviour-identical rewrites of the anchor text (old -> equivalent). Each old occurs exactly once.
REWRITE = {
    "B1": ("fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)", "fd = os.open(path, os.O_NONBLOCK | os.O_RDONLY)"),
    "E2": ("inside = os.path.commonpath([resolved, root_real]) == root_real",
           "inside = root_real == os.path.commonpath([resolved, root_real])"),
    "E4": ("gitdir_inside = os.path.commonpath([gitdir, root_real]) == root_real",
           "gitdir_inside = root_real == os.path.commonpath([gitdir, root_real])"),
    "G2": ("if args.timeout < 1:", "if 1 > args.timeout:"),
    "G3": ("default=20", "default=(20)"),
    "G4": ('return None, None, "UNREACHABLE:list-timeout"', 'return (None), None, "UNREACHABLE:list-timeout"'),
    "G5": ("if listed.returncode != 0:", "if 0 != listed.returncode:"),
    "H1": ('ap.add_argument("--root", required=True)', 'ap.add_argument("--root", required=True,)'),
    "H2": ('ap.add_argument("--record", required=True)', 'ap.add_argument("--record", required=True,)'),
    "I1": ("if os.path.islink(path):", "if (os.path.islink(path)):"),
    "J9": (r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d+)", r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d{1,})"),
    "M1": ("os.ftruncate(fd, 0)", "os.ftruncate(fd, int(0))"),
    "D4": ('raw = b"".join(chunks).decode("utf-8", "replace")',
           'raw = b"".join(chunks).decode(encoding="utf-8", errors="replace")'),
    "B3": ("os.set_blocking(fd, True)\n        chunks = []", "os.set_blocking(fd, True)\n        chunks = list()"),
    "B4": ("os.set_blocking(fd, True)\n        return fd", "os.set_blocking(fd, True)\n        return (fd)"),
    "E5": ("for base in measured:", "for base in (measured):"),
    "E7": ("measured.append(gitdir)", "measured.append((gitdir))"),
    "E9": ("measured.append(resolved)", "measured.append((resolved))"),
    "H4": ('ap.add_argument("--json")', 'ap.add_argument("--json",)'),
}


def verdict(res):
    if c3.killed(res):
        return "killed"
    if c3.clean(res):
        return "clean"
    return "other"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--mode", required=True, choices=("verdicts", "count", "rename", "rewrite"))
    args = ap.parse_args(argv)
    scratch = os.path.realpath(args.scratch)
    fixture = os.path.realpath(args.fixture)
    if os.geteuid() == 0:
        print("refusing root")
        return 2
    base_src = open(PRISTINE, "rb").read().decode("utf-8")
    work = tempfile.mkdtemp(prefix="harness.", dir=scratch)
    try:
        if args.mode == "rewrite":
            src = base_src
            for mid, (old, new) in REWRITE.items():
                n = src.count(old)
                if n != 1:
                    print("REWRITE-ANCHOR %s occurs %d times" % (mid, n))
                    return 2
                src = src.replace(old, new)
            compile(src, "rewritten", "exec")
            base_src = src
        pristine_path = os.path.join(work, "pristine.py")
        open(pristine_path, "w", encoding="utf-8").write(base_src)
        os.chmod(pristine_path, 0o755)
        mutants = {}
        for mid, _d, old, new in ALL:
            if args.mode == "rewrite":
                ro = REWRITE[mid][1]
                if base_src.count(ro) != 1:
                    print("REWRITE-ANCHOR-MISSING %s" % mid)
                    return 2
                body = base_src.replace(ro, new)
            else:
                body = base_src.replace(old, new)
            d = os.path.join(work, "m-%s" % mid)
            os.makedirs(d)
            p = os.path.join(d, "mut-%s.py" % mid)
            open(p, "w", encoding="utf-8").write(body)
            os.chmod(p, 0o755)
            mutants[mid] = p
        if args.mode == "rename":
            for mid, p in list(mutants.items()):
                d = os.path.join(work, "n-%s" % mid)
                os.makedirs(d)
                q = os.path.join(d, "n-%s.py" % mid)
                shutil.copyfile(p, q)
                os.chmod(q, 0o755)
                mutants[mid] = q
        if args.mode == "count":
            for mid, p in list(mutants.items()):
                d = os.path.join(work, "shim-%s" % mid)
                os.makedirs(d)
                log = os.path.join(d, "log.txt")
                wrap = os.path.join(d, os.path.basename(p))
                open(wrap, "w", encoding="utf-8").write(
                    "import runpy, sys\nopen(%r, 'a').write('invoke\\n')\n"
                    "sys.argv = [%r] + sys.argv[1:]\nrunpy.run_path(%r, run_name='__main__')\n" % (log, wrap, p))
                os.chmod(wrap, 0o755)
                mutants[mid] = wrap
                mutants[mid + "#log"] = log
            pristine_wrap_dir = os.path.join(work, "shim-pristine")
            os.makedirs(pristine_wrap_dir)
            plog = os.path.join(pristine_wrap_dir, "log.txt")
            pwrap = os.path.join(pristine_wrap_dir, "pristine.py")
            open(pwrap, "w", encoding="utf-8").write(
                "import runpy, sys\nopen(%r, 'a').write('invoke\\n')\n"
                "sys.argv = [%r] + sys.argv[1:]\nrunpy.run_path(%r, run_name='__main__')\n"
                % (plog, pwrap, pristine_path))
            os.chmod(pwrap, 0o755)
            pristine_path = pwrap
            mutants["pristine#log"] = plog
        jobs = {"pristine": pristine_path}
        jobs.update({k: v for k, v in mutants.items() if "#" not in k})
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            futs = {k: pool.submit(c3.run, fixture, p, scratch, "h-" + k) for k, p in jobs.items()}
            res = {k: f.result() for k, f in futs.items()}
        pres = res["pristine"]
        print("PRISTINE %s rc=%s cases=%s pass=%s fail=%s crash=%s" % (
            verdict(pres), pres[0], pres[1], pres[2], pres[3], pres[4]))
        for mid, _d, _o, _n in ALL:
            kind = "MUTANT" if (mid, _d, _o, _n) in c3.MUTANTS else "EQUIV"
            r = res[mid]
            line = "%s %s %s rc=%s cases=%s fail=%s crash=%s" % (kind, mid, verdict(r), r[0], r[1], r[3], r[4])
            if args.mode == "count":
                log = mutants[mid + "#log"]
                n = open(log).read().count("invoke") if os.path.exists(log) else 0
                line += " invocations=%d" % n
            print(line)
        if args.mode == "count":
            n = open(plog).read().count("invoke") if os.path.exists(plog) else 0
            print("PRISTINE-INVOCATIONS %d (cases=%s)" % (n, pres[1]))
        killed_ids = [mid for mid, _d, _o, _n in c3.MUTANTS if c3.killed(res[mid])]
        equiv_ids = [mid for mid, _d, _o, _n in c3.EQUIV if c3.killed(res[mid])]
        print("TALLY killed=%d/%d equiv_killed=%d/%d pristine_clean=%s" % (
            len(killed_ids), len(c3.MUTANTS), len(equiv_ids), len(c3.EQUIV), c3.clean(pres)))
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
