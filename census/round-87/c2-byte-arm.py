#!/usr/bin/env python3
"""souji r87 C2 byte-arm probe: the three shapes the frozen 12-row counter does not carry, measured against a given
tool build. Written after S87ExecC2's HIGH finding (a non-UTF-8 status path crashed the first -z implementation and
emitted no K4 row at all).

Rows (each on a fresh clone of a hermetic seed repository):
  KB1 non-utf8   an untracked path whose name carries a raw 0xff byte: one K4 row must name it (backslashreplace
                 spelling `\\xff-name.txt`), and the tool must print a counts line
  KB2 cr         an untracked path whose name carries a CR: one K4 row, its record naming `\\r` (not `\\n`)
  KB3 rename     a staged rename whose SOURCE name starts `ab ` (two characters and a space): one row naming the
                 destination (the change) and NO row for the source (the second NUL field is a name, not a status
                 record; a content test for "status pair" reads `ab src.txt` as status `ab`)

Output: `ROW <id> expect=<one|escaped> k4=<n> named=<yes|no> counts=<yes|no> rc=<n> match=<yes|no>` then
`SUMMARY rows=3 mismatches=<M>` and `EXIT=<0|1>`. Exit 2 on usage or a fixture failure. `--work` must be absent or
empty and never under /tmp.
"""
import argparse
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
K4 = b"MISMATCH\tK4\t"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r87 fixture", "GIT_AUTHOR_EMAIL": "fixture@r87.invalid",
            "GIT_COMMITTER_NAME": "r87 fixture", "GIT_COMMITTER_EMAIL": "fixture@r87.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})
ROWS = ("KB1", "KB2", "KB3")


class FixtureError(Exception):
    pass


def git(repo, *args, check=True):
    if not repo or not os.path.isabs(repo):
        raise FixtureError(f"refusing git -C with {repo!r}")
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, timeout=120)
    if check and p.returncode != 0:
        raise FixtureError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr[:200]!r}")
    return p


def build(work):
    clone = os.path.join(work, "clone")
    os.makedirs(clone)
    git(clone, "init", "-q", "-b", "master")
    with open(os.path.join(clone, "a.txt"), "wb") as f:
        f.write(b"alpha\n")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "--no-verify", "-m", "r87 KB seed")
    return clone, git(clone, "rev-parse", "HEAD").stdout.decode().strip()


def apply_row(clone, row):
    git(clone, "reset", "-q", "--hard", "HEAD")
    git(clone, "clean", "-q", "-fdx")
    # reset() cannot remove a name that is not valid UTF-8 through a text-mode call; both KB1/KB2 create untracked
    # files, so `clean -fdx` is enough and the loop re-creates exactly one per row.
    if row == "KB1":
        with open(os.path.join(clone.encode(), b"\xff-name.txt"), "wb") as f:
            f.write(b"not utf-8\n")
    elif row == "KB2":
        with open(os.path.join(clone, "cr\rname.txt"), "wb") as f:
            f.write(b"carriage return\n")
    elif row == "KB3":
        with open(os.path.join(clone, "ab src.txt"), "wb") as f:
            f.write(b"source\n")
        git(clone, "add", "-A")
        git(clone, "commit", "-q", "--no-verify", "-m", "src")
        git(clone, "mv", "ab src.txt", "dst.txt")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--keep", action="store_true")
    ns = ap.parse_args(argv)
    tool, work = os.path.abspath(ns.tool), os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C2-BYTE-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if not os.path.isfile(tool):
        print(f"C2-BYTE-FATAL: --tool {tool} is not a file", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C2-BYTE-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    print(f"# tool path={tool}")
    try:
        clone, rev = build(work)
    except (FixtureError, OSError) as exc:
        print(f"C2-BYTE-FATAL: fixture: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    mism = 0
    for row in ROWS:
        try:
            apply_row(clone, row)
        except (FixtureError, OSError) as exc:
            mism += 1
            print(f"ROW {row} expect=- k4=- named=- counts=- rc=- match=error detail={type(exc).__name__}: {exc}")
            continue
        p = subprocess.run([sys.executable, "-B", tool, "--root", clone, "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, timeout=600)
        out, err = p.stdout, p.stderr
        lines = [l.split(b"\t") for l in out.split(b"\n") if l.startswith(K4)]
        records = [(c[0], c[1] if len(c) > 1 else b"") for c in (l[2:] for l in lines)]
        counts = b"keys=" in out
        if row == "KB1":
            expect = b"\\xff-name.txt"
            named = any(expect in a or expect in b for a, b in records)
            detail = f"records={[a[:40] for a, _ in records]} stderr={err[:80]!r}"
        elif row == "KB2":
            expect = b"cr\\rname.txt"
            named = any(expect in a or expect in b for a, b in records)
            detail = f"records={[a[:40] for a, _ in records]}"
        else:
            expect = b"dst.txt"
            named = (any(a == b"dst.txt" for a, _ in records)
                     and not any(a == b"src.txt" for a, _ in records))
            detail = f"records={[a[:40] for a, _ in records]}"
        ok = bool(counts) and named
        mism += 0 if ok else 1
        print(f"ROW {row} expect={expect.decode('utf-8', 'replace')} k4={len(lines)} named={'yes' if named else 'no'} "
              f"counts={'yes' if counts else 'no'} rc={p.returncode} match={'yes' if ok else 'no'} {detail}")
    git(clone, "reset", "-q", "--hard", "HEAD", check=False)
    print(f"SUMMARY rows={len(ROWS)} mismatches={mism}")
    print(f"EXIT={0 if mism == 0 else 1}")
    if not ns.keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0 if mism == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
