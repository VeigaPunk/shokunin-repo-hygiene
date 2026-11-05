#!/usr/bin/env python3
"""Generate C2 mutants (full files) from the production receipt-writer bytes.

Each mutation is an exact single-occurrence replacement; the generator aborts
if any anchor is not found exactly once, so a mutant can never silently be a
copy of the pristine tool.  Writes mutants/c2/<name>.py and prints the sha256
of pristine and each mutant.
"""
import hashlib
import os
import sys

PRISTINE = sys.argv[1]
OUTDIR = sys.argv[2]

ATOMIC = '''    try:
        fd, tmp = tempfile.mkstemp(prefix=os.path.basename(out) + ".", suffix=".tmp", dir=outdir)
        _TEMP[TEMP_MARK] = tmp
        with os.fdopen(fd, "wb") as f:
            f.write(receipt)
            f.flush()
            os.fsync(f.fileno())
        # r60 amendment 3 (S60ReviewerRecorder a1/a2): `os.replace` after an existence check is a
        # TOCTOU that clobbers a file another process created during the run. `os.link` publishes
        # atomically and fails with EEXIST, so the loser of a race never destroys the winner's bytes.
        try:
            os.link(tmp, out)
        except FileExistsError:
            refuse(f"out appeared while the command ran ({out})")
        _TEMP[TEMP_MARK] = None
        try:
            os.unlink(tmp)
        except OSError:
            pass
    finally:
        leftover = _TEMP[TEMP_MARK]
        if leftover:
            _TEMP[TEMP_MARK] = None
            try:
                os.unlink(leftover)
            except OSError:
                pass
'''

MUTANTS = []


def mutant(name, why, *repls):
    MUTANTS.append((name, why, repls))


# --- M1: non-atomic, streams OUT while the wrapped command runs -------------
mutant(
    "c2-m1-direct-stream",
    "writes OUT directly and opens it before the wrapped command runs "
    "(no temp+link publication), so a partial receipt is visible in flight",
    ("    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)",
     "    _live = open(out, \"wb\")\n"
     "    _live.write(b\"instrument=\" + rel.encode() + b\"\\n\")\n"
     "    _live.flush()\n"
     "    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)"),
    (ATOMIC,
     """    with open(out, "ab") as f:
        f.write(receipt.split(b"\\n", 1)[1])
        f.flush()
        os.fsync(f.fileno())
    _live.close()
"""),
)

# --- M2: overwrite check removed (pre-check and in-flight publication check)
mutant(
    "c2-m2-overwrite-skip",
    "drops the OUT-exists refusal before the command and publishes with "
    "os.replace, so an existing receipt is silently replaced",
    ("""    # behaviour 4: OUT must not exist; refuse before any side effect
    if os.path.lexists(out):
        refuse(f"out already exists ({out})")
""", ""),
    ("""        try:
            os.link(tmp, out)
        except FileExistsError:
            refuse(f"out appeared while the command ran ({out})")
""", """        os.replace(tmp, out)
"""),
)

# --- M3: --max-bytes ignored ------------------------------------------------
mutant(
    "c2-m3-bound-ignored",
    "captures without enforcing --max-bytes, so an over-cap command still "
    "produces a receipt",
    ("""            total += len(chunk)
            chunks.append(chunk)
            if total > ns.max_bytes:
                overflow = True
                proc.kill()
                break""",
     """            total += len(chunk)
            chunks.append(chunk)"""),
)

# --- M4: dirty-tree guard removed ------------------------------------------
mutant(
    "c2-m4-dirty-skip",
    "never consults git status, so a dirty lane still yields a receipt",
    ("""    if st.stdout and not ns.allow_dirty:
        refuse("lane worktree is dirty (git status --porcelain non-empty); pass --allow-dirty to override")
""", ""),
)

# --- M5: short rev accepted ------------------------------------------------
mutant(
    "c2-m5-rev-short-accept",
    "accepts a 7..40 hex prefix instead of a full 40-hex commit id",
    ('REV_RE = re.compile(r"^[0-9a-f]{40}$")',
     'REV_RE = re.compile(r"^[0-9a-f]{7,40}$")'),
)

# --- M6: digest read from the worktree, equality check removed --------------
mutant(
    "c2-m6-digest-worktree",
    "binds instrument_sha256 to the worktree bytes rather than the committed "
    "blob at rev (worktree/committed equality check removed)",
    ("    digest = hashlib.sha256(blob.stdout).hexdigest()",
     "    digest = hashlib.sha256(open(os.path.join(root, *rel.split(\"/\")), \"rb\").read()).hexdigest()"),
    ("""    if wt_bytes != blob.stdout:
        refuse(f"worktree {rel} differs from committed bytes at {rev}")
""", ""),
)

# --- M7: command= line omitted from the record ------------------------------
mutant(
    "c2-m7-command-omitted",
    "omits the command= field, so a receipt no longer names the command it "
    "measured",
    ('        ("command=" + shlex.join(argv) + "\\n").encode("utf-8"),\n', ""),
)

# --- M8: publication reverts to os.replace (TOCTOU) -------------------------
mutant(
    "c2-m8-link-to-replace",
    "publishes with os.replace instead of the EEXIST-safe os.link, so a file "
    "created during the run is clobbered",
    ("""        try:
            os.link(tmp, out)
        except FileExistsError:
            refuse(f"out appeared while the command ran ({out})")
""", """        os.replace(tmp, out)
"""),
)

# --- M9: stale-temp sweep removed ------------------------------------------
mutant(
    "c2-m9-no-stale-sweep",
    "no longer sweeps a *.tmp left by an earlier SIGKILL, so residue survives "
    "the next write",
    ("""    for stale in glob.glob(os.path.join(glob.escape(outdir), glob.escape(os.path.basename(out)) + ".*.tmp")):
        try:
            os.unlink(stale)
        except OSError:
            pass
""", ""),
)

# --- M10: OUT-directory confinement removed --------------------------------
mutant(
    "c2-m10-outside-outdir-allowed",
    "never refuses an OUT directory outside the lane root",
    ("""    if (real_outdir != real_root and not real_outdir.startswith(real_root + os.sep)
            and not getattr(ns, "allow_outside", False)):""",
     """    if False:"""),
)


def main():
    with open(PRISTINE, "rb") as f:
        src = f.read().decode("utf-8")
    os.makedirs(OUTDIR, exist_ok=True)
    print("pristine=%s sha256=%s" % (PRISTINE, hashlib.sha256(src.encode()).hexdigest()))
    for name, why, repls in MUTANTS:
        cur = src
        for old, new in repls:
            n = cur.count(old)
            if n != 1:
                sys.exit("ANCHOR %s: %r occurs %d times (want 1)" % (name, old[:60], n))
            cur = cur.replace(old, new)
        if cur == src:
            sys.exit("mutant %s is byte-identical to pristine" % name)
        path = os.path.join(OUTDIR, name + ".py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(cur)
        os.chmod(path, 0o755)
        print("%s sha256=%s why=%s" % (name, hashlib.sha256(cur.encode()).hexdigest(), why))


if __name__ == "__main__":
    main()
