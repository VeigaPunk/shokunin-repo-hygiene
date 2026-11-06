#!/usr/bin/env python3
"""souji r73: derive census/round-73/c1-counter.py and c1-matrix.tsv from the frozen r72 counter
(census/round-72/c1-counter.py, sha256 7578447d…a912) by exact single-occurrence replacements (count
asserted), the lane's successor pattern (r71/r72 mk-counter.py). The r72 counter is NOT amended (Q131).
The r72 matrix's 75 rows are carried byte for byte; five FX rows are appended (preregistration.txt,
frozen at 23ecd070).
Usage (from the lane root): python3 -B census/round-73/mk-counter.py"""
import hashlib
import sys

src = open("census/round-72/c1-counter.py").read()
assert hashlib.sha256(src.encode()).hexdigest().startswith("7578447d"), "unexpected r72 counter bytes"


def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        sys.exit(f"pattern count {n} != {count}: {old[:80]!r}")
    src = src.replace(old, new)


# 1. docstring head
rep('"""c1-counter.py — souji round-72 C1/C2 counter (L1-built, committed after the r72 freeze 23372f36).\n\n'
    'Round 72 (successor of census/round-71/c1-counter.py; the frozen r71 counter is NOT amended — Q131):\n',
    '''"""c1-counter.py — souji round-73 C1/C2 counter (L1-built, committed after the r73 freeze 23ecd070).

Round 73 (successor of census/round-72/c1-counter.py; the frozen r72 counter is NOT amended — Q131):

  * C2 calibration — forgery witness (r72 routed D4 / S72MutCounter MF: a refuse row was credited as a
    forgery without any check that its fixture forged). For every row and both slots the counter now
    computes the divergence of the fixture worktree from the row's revision (tree_divergence: `git
    ls-tree -r` entries vs the worktree — missing path, wrong type, wrong exec bit, different raw bytes,
    different symlink target — plus worktree files outside the tree, `.git` excluded; no git status, no
    stat cache, no filter), once before the slot runs and once after. A refuse row a slot accepts with no
    divergence at either point is unwitnessed: CASE lines print base_witness= / new_witness=, SUMMARY
    prints base_unwitnessed= and new_unwitnessed=, claim_upheld requires base_unwitnessed=0, and the
    battery classifier counts an accepted refuse row as a forgery only when witnessed (an unwitnessed
    one is `error`). Selftest section (10) exercises the witness.
  * C1 operability rows (r72 routed D3 / S72Sentinel HIGH, index stat-cache forgery; racy-git.adoc S315,
    git-hash-object(1) S316): FX1 in-run forge of tools/counter.py with its index stat entry rewritten,
    FX2 the same before the run, FX3 the same on the instrument in-run — each `refuse
    RECEIPT-WORKTREE-STAT-CONCEALED`, base_expect `accept`; FXh an honest stale-stat file (mtime +10 s,
    bytes unchanged) and FXc an honest core.autocrlf=true CRLF file re-staged by the fixture — `accept`.
  * r72 spot-check D2: the round-72 text below said FWw's "status reads the worktree file, S314"; S314
    states only the fallback order outside checkout. Corrected in this file's copy of that text.

Round 72 text (carried; describes the r72 duties this file still performs):

Round 72 (successor of census/round-71/c1-counter.py; the frozen r71 counter is NOT amended — Q131):
''')

# 2. D2 correction of the carried r72 text
rep("git-check-attr(1) --cached, S312; status reads the worktree file, S314); FWs a driver literally",
    "git-check-attr(1) --cached, S312; outside checkout the worktree .gitattributes is read and the index\n"
    "    copy is only a fall-back, S314 — corrected in r73 from \"status reads the worktree file\"); FWs a driver literally")

# 3. counter identity
rep('COUNTER_REL = "census/round-72/c1-counter.py"', 'COUNTER_REL = "census/round-73/c1-counter.py"')

# 4. case order
rep('              "FWr", "FWi", "FWp", "FWw", "FWs"]\n',
    '              "FWr", "FWi", "FWp", "FWw", "FWs",\n'
    '              "FX1", "FX2", "FX3", "FXh", "FXc"]\n')

# 5. constants (after WITNESS_ROWS)
rep('WITNESS_ROWS = ("AS1", "AS2", "FC1", "FC2", "FC3", "FM1", "FM2")\n',
    '''WITNESS_ROWS = ("AS1", "AS2", "FC1", "FC2", "FC3", "FM1", "FM2")
# r73 C1: index stat-cache forgery (S72Sentinel; racy-git.adoc S315). Writes the forged bytes, then
# rewrites that path's index entry stat fields from the forged file's lstat (blob OID and flags kept),
# recomputes the index checksum and moves the index mtime 5 s past the entry so git does not treat the
# entry as racily clean. argv: repo, repo-relative path, forged bytes (latin-1).
CLASS_TRUTH = "RECEIPT-WORKTREE-STAT-CONCEALED"
INDEX_STAT_CODE = r\'\'\'import hashlib, os, struct, sys
repo, rel, forged = sys.argv[1], sys.argv[2], sys.argv[3].encode("latin-1")
full = os.path.join(repo, rel)
with open(full, "wb") as f:
    f.write(forged)
st = os.lstat(full)
p = os.path.join(repo, ".git", "index")
data = open(p, "rb").read()
if data[:4] != b"DIRC":
    sys.exit("bad index signature")
ver, n = struct.unpack(">II", data[4:12])
if ver not in (2, 3):
    sys.exit(f"index version {ver} unsupported")
off, out, target, hit = 12, bytearray(data[:12]), rel.encode(), False
for _ in range(n):
    start = off
    fixed = data[off:off + 62]
    sha, flags = fixed[40:60], fixed[60:62]
    ns = off + 62
    z = data.index(b"\\0", ns)
    name = data[ns:z]
    tail_end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
    if name == target:
        hit = True
        fixed = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                            int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                            st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF, st.st_mode,
                            st.st_uid, st.st_gid, st.st_size & 0xFFFFFFFF) + sha + flags
        out += fixed + data[ns:tail_end]
    else:
        out += data[start:tail_end]
    off = tail_end
if not hit:
    sys.exit(f"{rel} not in index")
out += data[off:-20]
out += hashlib.sha1(bytes(out)).digest()
with open(p, "wb") as f:
    f.write(bytes(out))
t = st.st_mtime + 5
os.utime(p, (t, t))
\'\'\'
''')

# 6. case specs (after FWs)
rep('''    "FWs":  {"name": "driver-named-set-forged", "env_kind": "info-filter-named-set",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
}
''', '''    "FWs":  {"name": "driver-named-set-forged", "env_kind": "info-filter-named-set",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    # r73 C1 rows (S72Sentinel index stat-cache routes; pre-freeze probes fx-index-stat.txt, fx-honest.txt).
    "FX1":  {"name": "inrun-forge-index-stat-rewritten", "inrun": "index-stat-counter"},
    "FX2":  {"name": "prerun-forge-index-stat-rewritten", "index_stat": ("tools/counter.py", FORGED_SAMESIZE)},
    "FX3":  {"name": "inrun-instrument-forge-index-stat-rewritten", "inrun": "index-stat-instrument"},
    "FXh":  {"name": "honest-stale-stat-bytes-unchanged", "stale_stat": "tools/notes.txt"},
    "FXc":  {"name": "honest-autocrlf-crlf-restaged", "autocrlf_crlf": "tools/notes.txt"},
}
''')

# 7. in-run kinds
rep('''    raise CaseError(f"unknown in-run kind {kind!r}")
''', '''    if kind == "index-stat-counter":
        # FX1: forge same-size counter bytes and rewrite the entry's stat cache in-run.
        return [sys.executable, "-c", INDEX_STAT_CODE, repo, "tools/counter.py", _b(FORGED_SAMESIZE)]
    if kind == "index-stat-instrument":
        # FX3: forge the instrument and rewrite its stat cache in-run (the writer compared it pre-run only).
        return [sys.executable, "-c", INDEX_STAT_CODE, repo, "tools/instr.sh", _b(FORGED_INSTR)]
    raise CaseError(f"unknown in-run kind {kind!r}")
''')

# 8. pre-run r73 set-up, run after mutate() in build_case
rep('''    repo, rev = build_repo_at(os.path.join(case_dir, repo_name))
    mutate(repo, spec)
''', '''    repo, rev = build_repo_at(os.path.join(case_dir, repo_name))
    mutate(repo, spec)
    _r73_prerun(repo, spec)
''')
rep('''def case_env(spec: dict, repo: str) -> Optional[dict]:
''', '''def _r73_prerun(repo: str, spec: dict) -> None:
    """r73 pre-run set-up for the FX rows (after mutate())."""
    if spec.get("index_stat"):
        rel, forged = spec["index_stat"]
        r = subprocess.run([sys.executable, "-c", INDEX_STAT_CODE, repo, rel, _b(forged)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=clean_env(), timeout=120)
        if r.returncode != 0:
            raise CaseError(f"index-stat forge failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    if spec.get("stale_stat"):
        p = os.path.join(repo, spec["stale_stat"])
        s = os.stat(p)
        os.utime(p, ns=(s.st_atime_ns, s.st_mtime_ns + 10_000_000_000))
    if spec.get("autocrlf_crlf"):
        rel = spec["autocrlf_crlf"]
        _cfg(repo, "core.autocrlf", "true")
        with open(os.path.join(repo, rel), "rb") as f:
            data = f.read()
        with open(os.path.join(repo, rel), "wb") as f:
            f.write(data.replace(b"\\n", b"\\r\\n"))
        r = git_run(repo, ["add", "--", rel])
        if r.returncode != 0:
            raise CaseError("autocrlf re-stage failed")


def tree_divergence(repo: str, rev: str) -> list[tuple[str, str]]:
    """r73 C2 forgery witness: (path, kind) for every way the worktree differs from rev's tree, read
    without git status, the index stat cache or any filter. Kinds: missing, type, mode (exec bit),
    bytes, target (symlink), untracked (a worktree file or symlink outside the tree; `.git` excluded).
    Gitlinks are skipped. Raises CaseError when the tree cannot be read."""
    r = git_run(repo, ["ls-tree", "-r", "-z", "--full-tree", rev])
    if r.returncode != 0:
        raise CaseError(f"witness ls-tree failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    ents: dict[bytes, tuple[bytes, bytes]] = {}
    for rec in r.stdout.split(b"\\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\\t")
        mode, _typ, oid = meta.split()
        ents[path] = (mode, oid)
    top = os.fsencode(repo)
    diffs: list[tuple[str, str]] = []

    def blob(oid: bytes) -> bytes:
        b = git_run(repo, ["cat-file", "blob", oid.decode()])
        if b.returncode != 0:
            raise CaseError("witness cat-file failed")
        return b.stdout

    for path, (mode, oid) in sorted(ents.items()):
        name = path.decode("utf-8", "replace")
        full = os.path.join(top, path)
        try:
            s = os.lstat(full)
        except FileNotFoundError:
            diffs.append((name, "missing"))
            continue
        if mode == b"160000":
            continue
        if mode == b"120000":
            if not stat.S_ISLNK(s.st_mode):
                diffs.append((name, "type"))
            elif os.readlink(full) != blob(oid):
                diffs.append((name, "target"))
            continue
        if not stat.S_ISREG(s.st_mode):
            diffs.append((name, "type"))
            continue
        if bool(s.st_mode & 0o111) != (mode == b"100755"):
            diffs.append((name, "mode"))
        with open(full, "rb") as f:
            if f.read() != blob(oid):
                diffs.append((name, "bytes"))
    for dirpath, dirnames, filenames in os.walk(top):
        rel_dir = os.path.relpath(dirpath, top)
        rel_dir = b"" if rel_dir == b"." else rel_dir
        if rel_dir == b"":
            dirnames[:] = [d for d in dirnames if d != b".git"]
        links = [d for d in dirnames if os.path.islink(os.path.join(dirpath, d))]
        for leaf in filenames + links:
            rel = rel_dir + b"/" + leaf if rel_dir else leaf
            if rel not in ents:
                diffs.append((rel.decode("utf-8", "replace"), "untracked"))
    return diffs


def case_env(spec: dict, repo: str) -> Optional[dict]:
''')

# 9. evaluate: witness both slots, before and after
rep('''        b_out = os.path.join(work, letter, "base", "out", "receipt.txt")
        n_out = os.path.join(work, letter, "new", "out", "receipt.txt")
        b_rc, _, b_se = run_slot(''', '''        b_out = os.path.join(work, letter, "base", "out", "receipt.txt")
        n_out = os.path.join(work, letter, "new", "out", "receipt.txt")
        try:
            b_pre, n_pre = tree_divergence(b_repo, b_rev), tree_divergence(n_repo, n_rev)
        except CaseError:
            b_pre = n_pre = None
        b_rc, _, b_se = run_slot(''')
rep('''        b_v, n_v = judge(b_rc, b_out), judge(n_rc, n_out)
''', '''        b_v, n_v = judge(b_rc, b_out), judge(n_rc, n_out)
        try:
            b_post, n_post = tree_divergence(b_repo, b_rev), tree_divergence(n_repo, n_rev)
        except CaseError:
            b_post = n_post = None
        # r73 C2: a witness read that fails is never a witness (fail closed: unwitnessed).
        b_wit = bool(b_pre is not None and b_post is not None and (b_pre or b_post))
        n_wit = bool(n_pre is not None and n_post is not None and (n_pre or n_post))
''')
rep('''                     f"base_expect={base_expect}")
''', '''                     f"base_expect={base_expect} base_witness={'yes' if b_wit else 'no'} "
                     f"new_witness={'yes' if n_wit else 'no'}")
''')
rep('''        if expect == "refuse":
            if b_v == "accept":
                c["base_forgeries"] += 1
            if n_v == "accept":
                c["new_forgeries"] += 1
''', '''        if expect == "refuse":
            if b_v == "accept":
                c["base_forgeries"] += 1
                if not b_wit:
                    c["base_unwitnessed"] += 1
            if n_v == "accept":
                c["new_forgeries"] += 1
                if not n_wit:
                    c["new_unwitnessed"] += 1
''')
rep('''        "class_mismatches": 0, "new_echo": 0, "errors": 0, "base_mismatches": 0}
    all_new_match = True''', '''        "class_mismatches": 0, "new_echo": 0, "errors": 0, "base_mismatches": 0,
         "base_unwitnessed": 0, "new_unwitnessed": 0}
    all_new_match = True''')
rep('''            row_fate.append({"letter": letter, "expect": expect, "verdict": "error",
                             "class_ok": False, "echo": False, "base": "error"})''',
    '''            row_fate.append({"letter": letter, "expect": expect, "verdict": "error",
                             "class_ok": False, "echo": False, "base": "error", "witness": False})''')
rep('''                         "echo": n_echo, "base": b_v})''',
    '''                         "echo": n_echo, "base": b_v, "witness": n_wit})''')

# 10. verdict, summary, classifier
rep('''            and c.get("base_mismatches", 1) == 0)''',
    '''            and c.get("base_mismatches", 1) == 0
            and c.get("base_unwitnessed", 1) == 0)''')
rep('''            f"base_honest={c['base_honest']} base_mismatches={c['base_mismatches']} "
            f"new_forgeries={c['new_forgeries']} "''',
    '''            f"base_honest={c['base_honest']} base_mismatches={c['base_mismatches']} "
            f"base_unwitnessed={c['base_unwitnessed']} new_unwitnessed={c['new_unwitnessed']} "
            f"new_forgeries={c['new_forgeries']} "''')
rep('''    fates = res["row_fate"]
    errors = sum(1 for f in fates if f["verdict"] == "error")
    forgeries = sum(1 for f in fates if f["expect"] == "refuse" and f["verdict"] == "accept")''',
    '''    fates = res["row_fate"]
    # r73 C2: an accepted refuse row is a forgery kill only when its fixture's divergence was observed;
    # an unwitnessed one is an invalid fixture and classifies as error.
    errors = sum(1 for f in fates if f["verdict"] == "error"
                 or (f["expect"] == "refuse" and f["verdict"] == "accept" and not f["witness"]))
    forgeries = sum(1 for f in fates if f["expect"] == "refuse" and f["verdict"] == "accept"
                    and f["witness"])''')
rep('''        "forgeries": sum(1 for f in fates if f["expect"] == "refuse" and f["verdict"] == "accept"),''',
    '''        "forgeries": sum(1 for f in fates if f["expect"] == "refuse" and f["verdict"] == "accept"
                         and f["witness"]),''')
rep('''        "errors": sum(1 for f in fates if f["verdict"] == "error"),''',
    '''        "errors": sum(1 for f in fates if f["verdict"] == "error"
                      or (f["expect"] == "refuse" and f["verdict"] == "accept" and not f["witness"])),''')

# 11. selftest: synthetic fates carry a witness; (9b) zero dict; section (10)
rep('''    def fate(letter, expect, verdict, class_ok=True, echo=False):
        return {"letter": letter, "expect": expect, "verdict": verdict,
                "class_ok": class_ok, "echo": echo}''',
    '''    def fate(letter, expect, verdict, class_ok=True, echo=False, witness=True):
        return {"letter": letter, "expect": expect, "verdict": verdict,
                "class_ok": class_ok, "echo": echo, "witness": witness}''')
rep('''            "class_mismatches": 0, "new_echo": 0, "errors": 0, "base_mismatches": 0}
    good_res =''', '''            "class_mismatches": 0, "new_echo": 0, "errors": 0, "base_mismatches": 0,
            "base_unwitnessed": 0, "new_unwitnessed": 0}
    good_res =''')
rep('''    check("clean_env: every scrub-tuple name is removed from the ambient environment",
          kept_amb == [], f"kept={kept_amb}")
''', '''    check("clean_env: every scrub-tuple name is removed from the ambient environment",
          kept_amb == [], f"kept={kept_amb}")

    # (10) r73 C2 forgery witness.
    wdir = os.path.join(st, "witness-r73")
    try:
        wrepo, wrev = build_repo_at(os.path.join(wdir, "repo"))
        clean0 = tree_divergence(wrepo, wrev)
        notes = os.path.join(wrepo, "tools", "notes.txt")
        os.chmod(notes, 0o755)
        d_mode = tree_divergence(wrepo, wrev)
        os.chmod(notes, 0o644)
        with open(os.path.join(wrepo, "tools", "extra.txt"), "wb") as f:
            f.write(UNTRACKED)
        d_untr = tree_divergence(wrepo, wrev)
        os.unlink(os.path.join(wrepo, "tools", "extra.txt"))
        os.unlink(os.path.join(wrepo, "README.md"))
        d_miss = tree_divergence(wrepo, wrev)
        with open(os.path.join(wrepo, "README.md"), "wb") as f:
            f.write(SEED_README)
        r10 = subprocess.run([sys.executable, "-c", INDEX_STAT_CODE, wrepo, "tools/counter.py",
                              _b(FORGED_SAMESIZE)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=clean_env(), timeout=120)
        st10 = git_run(wrepo, ["status", "--porcelain"]).stdout
        d_stat = tree_divergence(wrepo, wrev)
        check("witness: a clean fixture has no divergence", clean0 == [], f"{clean0}")
        check("witness: an exec-bit flip is a mode divergence", d_mode == [("tools/notes.txt", "mode")], f"{d_mode}")
        check("witness: a new worktree file is an untracked divergence",
              d_untr == [("tools/extra.txt", "untracked")], f"{d_untr}")
        check("witness: a deleted tracked file is a missing divergence",
              d_miss == [("README.md", "missing")], f"{d_miss}")
        check("witness: a stat-concealed forgery (git status clean) is a bytes divergence",
              r10.returncode == 0 and st10 == b"" and d_stat == [("tools/counter.py", "bytes")],
              f"rc={r10.returncode} status={st10!r} {d_stat}")
    except (CaseError, OSError) as exc:
        check("witness: fixture set-up", False, f"{exc}")
    unw = {"counts": dict(zero, base_unwitnessed=1), "n_accept": 0, "regress": "PASS", "all_new_match": True}
    check("claim verdict: one unwitnessed base forgery fails the claim", claim_upheld(unw) is False)
    synth = {"row_fate": [fate("FWi", "refuse", "accept", witness=False)]}
    check("classifier: an accepted refuse row without a witness is error, not a forgery",
          classify_outcome(synth) == "error" and outcome_counts(synth)["forgeries"] == 0)
    synth = {"row_fate": [fate("FWi", "refuse", "accept", witness=True)]}
    check("classifier: an accepted refuse row with a witness is a forgery", classify_outcome(synth) == "forgery")
''')

# 12. imports: stat module
rep("\nimport subprocess\n", "\nimport stat\nimport subprocess\n")

open("census/round-73/c1-counter.py", "w").write(src)

m = open("census/round-72/c1-matrix.tsv").read()
assert hashlib.sha256(m.encode()).hexdigest().startswith("cd8490b4"), "unexpected r72 matrix bytes"
m += ("FX1\trefuse\tRECEIPT-WORKTREE-STAT-CONCEALED\taccept\n"
      "FX2\trefuse\tRECEIPT-WORKTREE-STAT-CONCEALED\taccept\n"
      "FX3\trefuse\tRECEIPT-WORKTREE-STAT-CONCEALED\taccept\n"
      "FXh\taccept\t-\taccept\n"
      "FXc\taccept\t-\taccept\n")
open("census/round-73/c1-matrix.tsv", "w").write(m)
print("wrote census/round-73/c1-counter.py sha256",
      hashlib.sha256(src.encode()).hexdigest(), "and c1-matrix.tsv sha256",
      hashlib.sha256(m.encode()).hexdigest())
