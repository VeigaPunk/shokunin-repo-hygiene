#!/usr/bin/env python3
"""souji r87 C2 counter: the r86 9-row counter (rows byte-identical) plus three rows that bind the r87 repair:
  KN1 silent-writer  a tool copy whose beside-writer raises AttributeError deep in a traceback: the K4 detail must
                     name the exception line, not the first 200 characters of the traceback           expect=flag(AttributeError)
  KN2 writer-binding the tool's own `# writer path=… sha256=…` header must name the bytes it delegates to, and one
                     appended comment byte in the writer must change the printed digest            expect=header
  KN3 untracked-nl   an untracked path carrying a newline: K4's status arm must record the raw path (C-escaped),
                     not git's own quoted form                                                     expect=flag(exact record)
The other nine rows keep the r85/r86 expectations byte-for-byte.

souji r85 C2 counter: does `tools/souji-record-agreement.py` key K4 (uncommitted round work) still accept a
working tree whose bytes changed under the index stat cache?

r85 claim subject: K4 reads `git status --porcelain` and nothing else, so a tracked path whose bytes were rewritten
and whose index entry stat fields were then rewritten from the forged file's own lstat reads clean and K4 reports no
uncommitted work. That is the class r73/r74 closed in the receipt writer and in the pre-report gate (S315 racy-git,
S316 git-hash-object(1), S317 gitformat-index(5)); record-agreement kept the bare status read (S74Connector, carried
since r74). This counter is the frozen instrument for the repair.

Public path only: every row runs the tool under test as a subprocess,
    python3 -B <tool> --root <clone> --rev <40-hex seed commit>
and parses its `MISMATCH<TAB>K4<TAB>...` rows. K1/K2/K3 also fire on a synthetic repository (no receipts there) and
are ignored: a row is judged on K4 rows alone. A row matches when

  expect=clean   there is no K4 row at all;
  expect=flag    there is at least one K4 row and one of them names the row's forged path (record or detail).

Rows (frozen):
  KH1 clean      the seed tree, nothing changed                                  expect=clean
  KH2 stale      a tracked file's mtime moved +10 s, bytes unchanged            expect=clean
  KU1 edit       a plain edit of a tracked file (status lists it)               expect=flag
  KU2 untracked  an untracked file at the clone root                            expect=flag
  KF1 same-size  same-size byte forge of a.txt, index stat rewritten from it    expect=flag
  KF2 symlink    tracked symlink `ln` retargeted to a same-length target, stat rewritten
                                                                                expect=flag
  KF3 size       size-changing forge of sub/b.txt, index stat rewritten         expect=flag

The fixture is synthetic and hermetic (a bare origin plus one clone; git identity and dates are fixed), so no lane
byte and no fleet path is read or written. `--work` must be absent or empty and must not be under /tmp; the clone
lives under it and is removed on exit unless --keep.

Output: one `ROW <id> expect=<clean|flag> k4=<n> named=<yes|no> rc=<n> match=<yes|no>` line per row, then
`SUMMARY rows=<N> mismatches=<M> errors=<E>` and `EXIT=<0|1>`; exit 2 on usage or a fixture failure.
"""
import argparse
import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys
import time

sys.dont_write_bytecode = True
BASE = "705fa1385c4ccec23811cfa57104046ec6587258"
ROWS = ("KH1", "KH2", "KU1", "KU2", "KF1", "KF2", "KF3", "KG1", "KG2", "KN1", "KN2", "KN3")
# the path each row requires a K4 row to name
FORGED = {"KU1": "a.txt", "KU2": "untracked-scratch.txt", "KF1": "a.txt", "KF2": "ln", "KF3": "sub/b.txt",
          "KG1": "nest", "KG2": "bad\\nname.txt"}
# r87: KN3 requires the record cell to be EXACTLY the C-escaped raw path, the class cell `uncommitted-path` and the
# detail cell the two status characters, so git's own quoted form (`"bad\nname2.txt"`) is a mismatch even though it
# contains the same characters.
EXACT = {"KN3": ("bad\\nname2.txt", "uncommitted-path", "??")}
STUB_WRITER = ("# r87 KN1 stub writer: raises where the delegated byte-truth check would run\n"
               "def git(*args, **kwargs):\n"
               "    raise AttributeError('r87 KN1 stub: no git helper')\n\n\n"
               "def _truth_refusal(root):\n"
               "    raise AttributeError('r87 KN1 stub: no truth helper')\n")
STATE = {}
K4 = re.compile(r"^MISMATCH\tK4\t([^\t]*)\t([^\t]*)\t(.*)$", re.M)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r85 fixture", "GIT_AUTHOR_EMAIL": "fixture@r85.invalid",
            "GIT_COMMITTER_NAME": "r85 fixture", "GIT_COMMITTER_EMAIL": "fixture@r85.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})


class FixtureError(Exception):
    pass


def git(repo, *args, check=True):
    if not repo or not os.path.isabs(repo):
        raise FixtureError(f"refusing git -C with {repo!r}")
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=ENV, timeout=120)
    if check and p.returncode != 0:
        raise FixtureError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.decode('utf-8', 'replace').strip()}")
    return p


def forge_index_stat(repo, rel):
    """Rewrite rel's index entry stat fields from the worktree path's lstat (object id and flags kept), re-checksum
    the index and move its mtime 5 s past the entry (so git cannot call it racily clean). Index v2/v3, SHA-1.
    Byte-for-byte the r74 C1 helper: the same forgery the gate and the writer already refuse."""
    st = os.lstat(os.path.join(repo, rel))
    p = os.path.join(repo, ".git", "index")
    data = open(p, "rb").read()
    if data[:4] != b"DIRC":
        raise FixtureError("bad index signature")
    ver, n = struct.unpack(">II", data[4:12])
    if ver not in (2, 3):
        raise FixtureError(f"index version {ver}")
    off, out, target, hit = 12, bytearray(data[:12]), rel.encode(), False
    for _ in range(n):
        start = off
        fixed = data[off:off + 62]
        sha, flags = fixed[40:60], fixed[60:62]
        mode = struct.unpack(">I", fixed[24:28])[0]
        ns = off + 62
        z = data.index(b"\0", ns)
        name = data[ns:z]
        tail_end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
        if name == target:
            hit = True
            fixed = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                                int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                                st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF, mode,
                                st.st_uid, st.st_gid, st.st_size & 0xFFFFFFFF) + sha + flags
            out += fixed + data[ns:tail_end]
        else:
            out += data[start:tail_end]
        off = tail_end
    if not hit:
        raise FixtureError(f"{rel} not in index")
    out += data[off:-20]
    out += hashlib.sha1(bytes(out)).digest()
    with open(p, "wb") as f:
        f.write(bytes(out))
    t = st.st_mtime + 5
    os.utime(p, (t, t))


def build(work):
    origin = os.path.join(work, "origin.git")
    clone = os.path.join(work, "clone")
    git(work, "init", "-q", "--bare", "-b", "master", origin)
    git(work, "init", "-q", "-b", "master", clone)
    if os.path.realpath(git(clone, "rev-parse", "--show-toplevel").stdout.decode().strip()) \
            != os.path.realpath(clone):
        raise FixtureError("fixture toplevel is not the clone dir")
    files = {"a.txt": b"alpha v1\n", "sub/b.txt": b"bravo\n", "run.sh": b"#!/bin/sh\necho hi\n",
             "tgt-one": b"one\n", "tgt-two": b"two\n", "bad\nname.txt": b"newline v1\n"}
    for rel, data in files.items():
        p = os.path.join(clone, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)
    os.chmod(os.path.join(clone, "run.sh"), 0o755)
    os.symlink("tgt-one", os.path.join(clone, "ln"))
    # r86 (S85ExecK4 §2d): a nested repository bound as a gitlink, so a commit change can be concealed by an
    # index flag the writer's status read cannot see. No .gitmodules: the index entry is the whole binding.
    nest = os.path.join(clone, "nest")
    os.makedirs(nest, exist_ok=True)
    git(nest, "init", "-q", "-b", "master")
    with open(os.path.join(nest, "n.txt"), "wb") as f:
        f.write(b"nest v1\n")
    git(nest, "add", "-A")
    git(nest, "commit", "-q", "--no-verify", "-m", "nest seed")
    nest1 = git(nest, "rev-parse", "HEAD").stdout.decode().strip()
    STATE["nest"] = nest
    STATE["nest1"] = nest1
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "--no-verify", "-m", "r85 C2 fixture seed")
    if git(clone, "ls-files", "-s", "-z", ":(top)").stdout.find(b"160000") < 0:
        raise FixtureError("the seeded tree carries no gitlink entry (nest was not staged as 160000)")
    git(clone, "remote", "add", "origin", origin)
    git(clone, "push", "-q", "origin", "master")
    git(clone, "update-index", "--refresh", check=False)
    old = time.time() - 30
    for rel in list(files) + ["ln"]:
        os.utime(os.path.join(clone, rel), (old, old), follow_symlinks=False)
    git(clone, "update-index", "--really-refresh", check=False)
    return clone, git(clone, "rev-parse", "HEAD").stdout.decode().strip()


def reset(clone, rev):
    # A forged index entry survives `reset --hard` (the stat fields are not rewritten), so the index is deleted
    # first: the reset then checks out every tracked path again and writes fresh stat entries. Without this the
    # previous row's forgery leaks into the next row.
    # r86: the nested repository behind the gitlink is reset too, so a row that moved its HEAD cannot leave the
    # next row with a dirty gitlink (which would look like a KU-class flag on an honest row).
    nest = STATE.get("nest")
    if nest and os.path.isdir(os.path.join(nest, ".git")):
        git(nest, "reset", "-q", "--hard", STATE["nest1"])
        git(nest, "clean", "-q", "-fdx")
    idx = os.path.join(clone, ".git", "index")
    if os.path.exists(idx):
        os.unlink(idx)
    git(clone, "reset", "-q", "--hard", rev)
    git(clone, "clean", "-q", "-fdx")
    git(clone, "update-index", "--refresh", check=False)


def apply_row(clone, row):
    if row == "KH2":
        p = os.path.join(clone, "a.txt")
        st = os.stat(p)
        os.utime(p, (st.st_atime + 10, st.st_mtime + 10))
    elif row == "KU1":
        with open(os.path.join(clone, "a.txt"), "wb") as f:
            f.write(b"alpha v2 (edited)\n")
    elif row == "KU2":
        with open(os.path.join(clone, "untracked-scratch.txt"), "wb") as f:
            f.write(b"not committed\n")
    elif row == "KF1":
        with open(os.path.join(clone, "a.txt"), "wb") as f:
            f.write(b"alpha X1\n")          # same length, different bytes
        forge_index_stat(clone, "a.txt")
    elif row == "KF2":
        os.unlink(os.path.join(clone, "ln"))
        os.symlink("tgt-two", os.path.join(clone, "ln"))
        forge_index_stat(clone, "ln")
    elif row == "KF3":
        with open(os.path.join(clone, "sub/b.txt"), "wb") as f:
            f.write(b"bravo but longer\n")
        forge_index_stat(clone, "sub/b.txt")
    elif row == "KG1":
        # S85ExecK4 §2d probe-d2b: the nested repository's HEAD moves, then the gitlink entry is marked
        # skip-worktree. `git status --porcelain` is empty (the flag hides the change) and the index still
        # records a 160000 entry, so only an index-flag sweep can see it.
        nest = STATE["nest"]
        with open(os.path.join(nest, "n.txt"), "ab") as f:
            f.write(b"nest v2\n")
        git(nest, "add", "-A")
        git(nest, "commit", "-q", "--no-verify", "-m", "nest second")
        git(clone, "update-index", "--skip-worktree", "nest")
    elif row == "KN3":
        # r87: an UNTRACKED path whose name carries a newline. `git status --porcelain` quotes it; the -z arm does not.
        with open(os.path.join(clone, "bad\nname2.txt"), "wb") as f:
            f.write(b"newline untracked\n")
    elif row == "KG2":
        # S85ExecK4 §2e: a path whose name carries a newline, forged under the index stat cache.
        with open(os.path.join(clone, "bad\nname.txt"), "wb") as f:
            f.write(b"newline X1\n")
        forge_index_stat(clone, "bad\nname.txt")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True, help="tools/souji-record-agreement.py under test")
    ap.add_argument("--work", required=True, help="absent or empty scratch dir, never under /tmp")
    ap.add_argument("--rows", default=",".join(ROWS), help="comma list of row ids")
    ap.add_argument("--keep", action="store_true")
    ns = ap.parse_args(argv)
    tool, work = os.path.abspath(ns.tool), os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C2-COUNTER-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if not os.path.isfile(tool):
        print(f"C2-COUNTER-FATAL: --tool {tool} is not a file", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C2-COUNTER-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    rows = [r for r in ns.rows.split(",") if r]
    if not rows or any(r not in ROWS for r in rows):
        print(f"C2-COUNTER-FATAL: --rows {ns.rows!r} is not a subset of {list(ROWS)}", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    print(f"# tool path={tool} sha256={hashlib.sha256(open(tool, 'rb').read()).hexdigest()}")
    wr = os.path.join(os.path.dirname(os.path.realpath(tool)), "souji-receipt-write.py")
    print(f"# writer path={wr} sha256="
          + (hashlib.sha256(open(wr, 'rb').read()).hexdigest() if os.path.isfile(wr) else "absent"))
    print(f"# counter sha256={hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest()}")
    try:
        clone, rev = build(work)
    except (FixtureError, OSError, subprocess.SubprocessError) as exc:
        print(f"C2-COUNTER-FATAL: fixture: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(f"# fixture clone={clone} rev={rev}")
    mism = errs = 0
    for row in rows:
        try:
            reset(clone, rev)
            apply_row(clone, row)
        except (FixtureError, OSError) as exc:
            errs += 1
            print(f"ROW {row} expect=- k4=- named=- rc=- match=error detail={type(exc).__name__}: {exc}")
            continue
        tool_row = tool
        if row in ("KN1", "KN2"):
            kit = os.path.join(work, "kits", row)
            os.makedirs(kit, exist_ok=True)
            shutil.copyfile(tool, os.path.join(kit, "souji-record-agreement.py"))
            wpath = os.path.join(kit, "souji-receipt-write.py")
            if row == "KN1":
                with open(wpath, "w", encoding="utf-8") as f:
                    f.write(STUB_WRITER)
            elif os.path.isfile(wr):
                shutil.copyfile(wr, wpath)
            tool_row = os.path.join(kit, "souji-record-agreement.py")
        p = subprocess.run([sys.executable, "-B", tool_row, "--root", clone, "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work, env=ENV, timeout=600)
        out = p.stdout.decode("utf-8", "replace")
        hits = K4.findall(out)
        expect = "clean" if row in ("KH1", "KH2") else "flag"
        extra = ""
        if expect == "clean":
            ok = not hits
            named = "-"
        elif row == "KN2":
            # r87: the tool binds its delegation by naming the writer's path and sha256 in its own output, and the
            # name must track the bytes: one appended comment line changes the printed digest.
            expect = "header"
            m = re.search(r"^# writer path=(\S+) sha256=([0-9a-f]{64})$", out, re.M)
            ok = False
            named = "no"
            if m and os.path.isfile(m.group(1)):
                live = hashlib.sha256(open(m.group(1), "rb").read()).hexdigest()
                first = m.group(2)
                with open(m.group(1), "ab") as f:
                    f.write(b"# r87 KN2: one appended comment byte changes the digest\n")
                p2 = subprocess.run([sys.executable, "-B", tool_row, "--root", clone, "--rev", rev],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work, env=ENV, timeout=600)
                m2 = re.search(r"^# writer path=(\S+) sha256=([0-9a-f]{64})$",
                               p2.stdout.decode("utf-8", "replace"), re.M)
                second = m2.group(2) if m2 else "-"
                ok = first == live and second not in ("-", first)
                named = "yes" if ok else "no"
                extra = f" writer_sha={first[:12]} appended_sha={second[:12]}"
        elif row == "KN1":
            named_ok = any("AttributeError" in c for _a, _b, c in hits)
            ok = bool(hits) and named_ok
            named = "yes" if named_ok else "no"
        elif row in EXACT:
            want_rec, want_cls, want_detail = EXACT[row]
            named_ok = any(a == want_rec and b == want_cls and c == want_detail for a, b, c in hits)
            ok = bool(hits) and named_ok
            named = "yes" if named_ok else "no"
        else:
            named_ok = any(FORGED[row] in (a + "\t" + b + "\t" + c) for a, b, c in hits)
            ok = bool(hits) and named_ok
            named = "yes" if named_ok else "no"
        mism += 0 if ok else 1
        print(f"ROW {row} expect={expect} k4={len(hits)} named={named} rc={p.returncode} "
              f"match={'yes' if ok else 'no'}"
              + (f" k4rows={[a + '|' + b for a, b, c in hits]}" if hits else "")
              + extra
              + ("" if ok else f" detail={p.stderr.decode('utf-8', 'replace')[:160]!r}"))
    reset(clone, rev)
    print(f"SUMMARY rows={len(rows)} mismatches={mism} errors={errs}")
    print(f"EXIT={0 if mism == 0 and errs == 0 else 1}")
    if not ns.keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
