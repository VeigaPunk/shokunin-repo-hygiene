#!/usr/bin/env python3
"""Generate C2 mutants (full files) from the pristine receipt-writer bytes.

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

MUTANTS = []


def mutant(name, why, *repls):
    MUTANTS.append((name, why, repls))


# --- M1: non-atomic, streams OUT while the wrapped command runs -------------
mutant(
    "c2-m1-direct-stream",
    "writes OUT directly and opens it before the wrapped command runs "
    "(no temp+rename), so a partial receipt is visible in flight",
    ("    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)",
     "    _live = open(out, \"wb\")\n"
     "    _live.write(b\"instrument=\" + rel.encode() + b\"\\n\")\n"
     "    _live.flush()\n"
     "    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)"),
    ("""    # behaviour 5: atomic write; the temp file exists only from here on
    try:
        fd, tmp = tempfile.mkstemp(prefix=os.path.basename(out) + ".", suffix=".tmp", dir=outdir)
        _TEMP[TEMP_MARK] = tmp
        with os.fdopen(fd, "wb") as f:
            f.write(receipt)
            f.flush()
            os.fsync(f.fileno())
        if os.path.lexists(out):
            refuse(f"out appeared while the command ran ({out})")
        os.replace(tmp, out)
        _TEMP[TEMP_MARK] = None
    finally:
        leftover = _TEMP[TEMP_MARK]
        if leftover:
            _TEMP[TEMP_MARK] = None
            try:
                os.unlink(leftover)
            except OSError:
                pass""",
     """    # MUTANT c2-m1: no temp file; the live handle already owns OUT
    with open(out, "ab") as f:
        f.write(receipt.split(b"\\n", 1)[1])
        f.flush()
        os.fsync(f.fileno())
    _live.close()"""),
)

# --- M2: overwrite check removed (both the pre-check and the in-flight check)
mutant(
    "c2-m2-overwrite-skip",
    "drops the OUT-exists refusal before and after the command, so an "
    "existing receipt is silently replaced",
    ("""    # behaviour 4: OUT must not exist; refuse before any side effect
    if os.path.lexists(out):
        refuse(f"out already exists ({out})")
""", ""),
    ("""        if os.path.lexists(out):
            refuse(f"out appeared while the command ran ({out})")
""", ""),
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
