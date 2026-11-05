#!/usr/bin/env python3
"""C2 probe: score census/round-57/record-receipt.sh against the 8 cases the round's
fixture spec defines, under two natural adapters (positional, flag)."""
import hashlib, os, shutil, signal, subprocess, sys, tempfile, time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = os.path.join(LANE, "census/round-57/record-receipt.sh")
ENV = {"PATH": os.environ["PATH"], "HOME": "/fast/scratch/hyaku/souji-r60/S60CriticRound/home",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
       "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid"}

def git(d, *a):
    return subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=ENV, check=True).stdout.decode().strip()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def siblings(d):
    return [f for f in os.listdir(d) if ".tmp" in f or ".partial" in f]

def main():
    tmp = tempfile.mkdtemp(prefix="c2probe-", dir="/fast/scratch/hyaku/souji-r60/S60CriticRound")
    os.makedirs(os.path.join(os.path.dirname(tmp), "home"), exist_ok=True)
    try:
        d = os.path.join(tmp, "repo"); os.mkdir(d)
        git(d, "init", "-q")
        with open(os.path.join(d, "c.py"), "wb") as fh: fh.write(b"c\n")
        git(d, "add", "-A"); git(d, "commit", "-q", "-m", "c")
        rev = git(d, "rev-parse", "HEAD")
        want_digest = sha(b"c\n")

        def run(case, out, cmd, extra=None, adapter="pos", wait=True):
            if adapter == "pos":
                argv = ["bash", BASE, d, rev, "c.py", out] + (extra or []) + ["--"] + cmd
            else:
                argv = ["bash", BASE, "--root", d, "--rev", rev, "--instrument", "c.py",
                        "--out", out] + (extra or []) + ["--"] + cmd
            p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
            return p.returncode, p.stdout.decode(), p.stderr.decode()

        def text(out):
            try:
                return open(out, "rb").read().decode("utf-8", "replace")
            except FileNotFoundError:
                return None

        results = {}
        # 1 clean
        out = os.path.join(tmp, "c1.out")
        rc, so, se = run("clean", out, ["sh", "-c", "echo hello; exit 0"])
        t = text(out) or ""
        ok = (rc == 0 and "instrument=c.py" in t and "instrument_sha256=" + want_digest in t
              and "rev=" + rev in t and "command=" in t and t.rstrip().endswith("EXIT=0")
              and not siblings(tmp))
        results["clean"] = (ok, rc, "missing-command=" if "command=" not in t else "")
        # 2 overwrite
        out2 = os.path.join(tmp, "c2.out")
        with open(out2, "wb") as fh: fh.write(b"KNOWN\n")
        rc, so, se = run("overwrite", out2, ["sh", "-c", "echo hi; exit 0"])
        results["overwrite"] = (rc == 2 and open(out2, "rb").read() == b"KNOWN\n" and not siblings(tmp), rc, "")
        # 3 atomic-in-flight
        out3 = os.path.join(tmp, "c3.out")
        argv = ["bash", BASE, d, rev, "c.py", out3, "--", "sh", "-c", "sleep 1; echo done; exit 0"]
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
        time.sleep(0.3)
        absent = not os.path.exists(out3)
        p.wait()
        t = text(out3) or ""
        results["atomic"] = (absent and t.rstrip().endswith("EXIT=0"), p.returncode, "absent_at_0.3=%s" % absent)
        # 4 kill-residue
        out4 = os.path.join(tmp, "c4.out")
        argv = ["bash", BASE, d, rev, "c.py", out4, "--", "sh", "-c", "sleep 5; echo done; exit 0"]
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV,
                             start_new_session=True)
        time.sleep(0.4)
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        p.wait()
        time.sleep(0.1)
        results["kill-residue"] = (not os.path.exists(out4) and not siblings(tmp),
                                   p.returncode, "out=%s" % os.path.exists(out4))
        # 5 bound (positional adapter drops --max-bytes; flag adapter passes it)
        out5 = os.path.join(tmp, "c5.out")
        big = ["sh", "-c", "head -c 2097152 /dev/zero | tr '\\0' 'x'; exit 0"]
        rc, so, se = run("bound", out5, big, extra=[] if True else None)
        results["bound(pos,no-flag)"] = (rc == 2 and not os.path.exists(out5), rc,
                                         "out=%s size=%s" % (os.path.exists(out5),
                                                             os.path.getsize(out5) if os.path.exists(out5) else 0))
        out5b = os.path.join(tmp, "c5b.out")
        rc, so, se = run("bound", out5b, big, extra=["--max-bytes", "65536"])
        results["bound(pos,flag-as-pos)"] = (rc == 2 and not os.path.exists(out5b), rc, "out=%s" % os.path.exists(out5b))
        # 6 rev-short
        out6 = os.path.join(tmp, "c6.out")
        p = subprocess.run(["bash", BASE, d, rev[:12], "c.py", out6, "--", "sh", "-c", "echo x; exit 0"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
        results["rev-short"] = (p.returncode == 2 and not os.path.exists(out6), p.returncode, "")
        # 7 instrument-absent
        out7 = os.path.join(tmp, "c7.out")
        p = subprocess.run(["bash", BASE, d, rev, "nope.py", out7, "--", "sh", "-c", "echo x; exit 0"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
        results["instrument-absent"] = (p.returncode == 2 and not os.path.exists(out7), p.returncode, "")
        # 8 dirty-tree
        out8 = os.path.join(tmp, "c8.out")
        with open(os.path.join(d, "untracked.txt"), "wb") as fh: fh.write(b"u\n")
        rc, so, se = run("dirty", out8, ["sh", "-c", "echo x; exit 0"])
        results["dirty-tree"] = (rc == 2 and not os.path.exists(out8), rc, "out=%s" % os.path.exists(out8))
        os.unlink(os.path.join(d, "untracked.txt"))

        # flag adapter over all cases (same argv for both tools)
        flag_pass = 0
        flag_lines = []
        for name, out, cmd in [
            ("clean", os.path.join(tmp, "f1.out"), ["sh", "-c", "echo hello; exit 0"]),
            ("overwrite", os.path.join(tmp, "f2.out"), ["sh", "-c", "echo hi; exit 0"]),
            ("bound", os.path.join(tmp, "f5.out"), big),
            ("rev-short", os.path.join(tmp, "f6.out"), ["sh", "-c", "echo x; exit 0"]),
            ("instrument-absent", os.path.join(tmp, "f7.out"), ["sh", "-c", "echo x; exit 0"]),
            ("dirty", os.path.join(tmp, "f8.out"), ["sh", "-c", "echo x; exit 0"]),
        ]:
            if name == "overwrite":
                with open(out, "wb") as fh: fh.write(b"KNOWN\n")
            p = subprocess.run(["bash", BASE, "--root", d, "--rev", rev, "--instrument", "c.py",
                                "--out", out, "--"] + cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=ENV)
            flag_lines.append("%s rc=%d" % (name, p.returncode))
        print("POSITIONAL-ADAPTER base passes:")
        n = 0
        for k, (ok, rc, note) in results.items():
            n += ok
            print("  %-22s %s rc=%d %s" % (k, "PASS" if ok else "FAIL", rc, note))
        print("POSITIONAL base pass=%d/8" % n)
        print("FLAG-ADAPTER base rc lines: " + ", ".join(flag_lines))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

main()
