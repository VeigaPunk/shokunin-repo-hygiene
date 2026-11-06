#!/usr/bin/env python3
"""souji r74: derive census/round-74/c1-counter.py from the frozen r73 counter (census/round-73/c1-counter.py,
sha256 3809ee7d…eaed3) by exact single-occurrence replacements (count asserted), the lane's successor
pattern (r71/r72/r73 mk-counter.py). The r73 counter is NOT amended (Q131). The matrix is unchanged
(census/round-73/c1-matrix.tsv). The lines the frozen survivor set (census/round-74/c2-survivors.json)
edits are kept byte for byte, so the same edits apply to both counters.
Usage (from the lane root): python3 -B census/round-74/mk-counter.py"""
import hashlib
import sys

src = open("census/round-73/c1-counter.py").read()
assert hashlib.sha256(src.encode()).hexdigest().startswith("3809ee7d"), "unexpected r73 counter bytes"


def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        sys.exit(f"pattern count {n} != {count}: {old[:80]!r}")
    src = src.replace(old, new)


# 1. docstring head
rep('"""c1-counter.py — souji round-73 C1/C2 counter (L1-built, committed after the r73 freeze 23ecd070).\n\n'
    'Round 73 (successor of census/round-72/c1-counter.py; the frozen r72 counter is NOT amended — Q131):\n',
    '''"""c1-counter.py — souji round-74 C2 counter (L1-built, committed after the r74 freeze bcdf2d16).

Round 74 (successor of census/round-73/c1-counter.py; the frozen r73 counter is NOT amended — Q131):

  * C2 calibration — row-specific forgery witness (r73 routed a / S73ExecC2; r73 lesson M2). The r73
    witness credited a row with ANY worktree divergence, and FWw/FC1/FC2 set-up always writes
    `.gitattributes`, so a row whose forgery was removed still read witnessed. The divergence lists are
    now scoped to the row's forged paths (forge_paths: the row's `target`, else the path its in-run kind,
    `chmod_notes` or `index_stat` writes — preregistration.txt C2) before the witness is decided; a row
    with no forged path is unwitnessed (fail closed). base_forgeries now counts witnessed base forgeries
    only (r73 routed e); an unwitnessed one counts in base_unwitnessed alone.
  * claim_upheld also requires new_unwitnessed=0 (S73MutCounter F2 / M17).
  * Selftest section (11) kills the r73 survivors: a failed witness read is unwitnessed in evaluate()
    (M08), a retargeted tracked symlink is a `target` divergence (M14), a gitlink with its directory
    present is no divergence (M15), and the (9a) witness run asserts base/new_unwitnessed=0 (M17); plus
    row_scope/forge_paths checks.

Round 73 text (carried; describes the r73 duties this file still performs):

Round 73 (successor of census/round-72/c1-counter.py; the frozen r72 counter is NOT amended — Q131):
''')

# 2. counter identity
rep('COUNTER_REL = "census/round-73/c1-counter.py"', 'COUNTER_REL = "census/round-74/c1-counter.py"')

# 3. forge_paths / row_scope after tree_divergence
rep('''            if rel not in ents:
                diffs.append((rel.decode("utf-8", "replace"), "untracked"))
    return diffs
''', '''            if rel not in ents:
                diffs.append((rel.decode("utf-8", "replace"), "untracked"))
    return diffs


# r74 C2: the path(s) each in-run kind's forging step writes (preregistration.txt C2, frozen).
INRUN_FORGED = {
    "edit-counter-samesize": "tools/counter.py", "restore-unset-driver": "tools/counter.py",
    "create-driver-forge": "tools/counter.py", "index-stat-counter": "tools/counter.py",
    "flag": "tools/counter.py",
    "chmod-clean": "tools/notes.txt", "chmod-dirty": "tools/notes.txt", "chmod-setuid": "tools/notes.txt",
    "chmod-sticky": "tools/notes.txt", "edit-noninstrument": "tools/notes.txt",
    "transient-restore": "tools/notes.txt", "append-dirty": "tools/notes.txt",
    "edit-instrument": "tools/instr.sh", "index-stat-instrument": "tools/instr.sh",
    "untracked": "tools/extra.txt", "untracked-dir-new": "tools/extra/new.txt",
    "symlink-retarget": "tools/extra/link", "symlink-retarget-same": "tools/extra/link",
}


def forge_paths(spec: dict) -> set:
    """r74 C2: the repo-relative paths the row's forging step writes. Empty = no declared forgery."""
    paths = set()
    if spec.get("target"):
        paths.add(spec["target"])
    elif spec.get("inrun") in INRUN_FORGED:
        paths.add(INRUN_FORGED[spec["inrun"]])
    if spec.get("chmod_notes"):
        paths.add("tools/notes.txt")
    if spec.get("index_stat"):
        paths.add(spec["index_stat"][0])
    return paths


def row_scope(spec: dict, diffs):
    """r74 C2: the divergences on the row's forged paths only; None (a failed read) stays None."""
    if diffs is None:
        return None
    fp = forge_paths(spec)
    return [d for d in diffs if d[0] in fp]
''')

# 4. evaluate: scope the four divergence reads before the witness lines (the witness lines stay verbatim)
rep('''            b_post = n_post = None
        # r73 C2: a witness read that fails is never a witness (fail closed: unwitnessed).
''', '''            b_post = n_post = None
        # r74 C2: the witness reads only the row's forged paths (a set-up divergence elsewhere is not one).
        b_pre, b_post = row_scope(spec, b_pre), row_scope(spec, b_post)
        n_pre, n_post = row_scope(spec, n_pre), row_scope(spec, n_post)
        # r73 C2: a witness read that fails is never a witness (fail closed: unwitnessed).
''')

# 5. base_forgeries counts witnessed base forgeries only
rep('''            if b_v == "accept":
                c["base_forgeries"] += 1
                if not b_wit:
                    c["base_unwitnessed"] += 1
''', '''            if b_v == "accept":
                if b_wit:
                    c["base_forgeries"] += 1
                else:
                    c["base_unwitnessed"] += 1
''')

# 6. claim_upheld gates new_unwitnessed
rep('''            and c.get("base_unwitnessed", 1) == 0)
''', '''            and c.get("base_unwitnessed", 1) == 0
            and c.get("new_unwitnessed", 1) == 0)
''')

# 7. (9a) witness run asserts the witness counts (M17)
rep('''        check("base witness: every r71 forging row forges the base writer as its base_expect says",
              len(wrows) == len(WITNESS_ROWS) and not bad and wres["counts"]["base_mismatches"] == 0,
              f"rows={len(wrows)} mismatches={bad}")
''', '''        check("base witness: every r71 forging row forges the base writer as its base_expect says",
              len(wrows) == len(WITNESS_ROWS) and not bad and wres["counts"]["base_mismatches"] == 0,
              f"rows={len(wrows)} mismatches={bad}")
        # r74 (M17): the same run witnesses every accepted forging row in both slots, including the
        # in-run-only rows (AS2, FC2, FM2) whose divergence exists after the slot only.
        wc = wres["counts"]
        check("witness run: base_unwitnessed=0 and new_unwitnessed=0 over the r71 forging rows",
              wc["base_unwitnessed"] == 0 and wc["new_unwitnessed"] == 0 and wc["base_forgeries"] == len(wrows),
              f"base_unwitnessed={wc['base_unwitnessed']} new_unwitnessed={wc['new_unwitnessed']} "
              f"base_forgeries={wc['base_forgeries']}")
        # r74 (M08): a witness read that fails is unwitnessed in evaluate(), in both slots.
        def _raise(*_a, **_k):
            raise CaseError("selftest: witness read fails")
        saved_td = globals()["tree_divergence"]
        globals()["tree_divergence"] = _raise
        try:
            frows = [r for r in rows if r[0] == "FM1"]
            fres = evaluate(frows, wslot, wslot, os.path.join(st, "witness-fail"), None)
        finally:
            globals()["tree_divergence"] = saved_td
        fc = fres["counts"]
        check("witness: a failed witness read is unwitnessed (FM1, both slots)",
              len(frows) == 1 and fc["base_unwitnessed"] == 1 and fc["new_unwitnessed"] == 1
              and fc["base_forgeries"] == 0 and fres["row_fate"][0]["witness"] is False,
              f"counts={fc}")
''')

# 8. section (11): symlink target, gitlink skip, row_scope/forge_paths
rep('''    synth = {"row_fate": [fate("FWi", "refuse", "accept", witness=True)]}
    check("classifier: an accepted refuse row with a witness is a forgery", classify_outcome(synth) == "forgery")
''', '''    synth = {"row_fate": [fate("FWi", "refuse", "accept", witness=True)]}
    check("classifier: an accepted refuse row with a witness is a forgery", classify_outcome(synth) == "forgery")

    # (11) r74 C2: row-specific witness and the r73 survivors (S73MutCounter M14, M15).
    xdir = os.path.join(st, "witness-r74")
    try:
        xrepo, _ = build_repo_at(os.path.join(xdir, "repo"))
        os.symlink("notes.txt", os.path.join(xrepo, "tools", "lnk"))
        r_add = git_run(xrepo, ["add", "--", "tools/lnk"])
        sub_oid = git_run(xrepo, ["rev-parse", "HEAD"]).stdout.decode().strip()
        r_gl = git_run(xrepo, ["update-index", "--add", "--cacheinfo", f"160000,{sub_oid},tools/sub"])
        r_ci = git_run(xrepo, ["commit", "-q", "-m", "r74 selftest: symlink + gitlink"])
        xrev = git_run(xrepo, ["rev-parse", "HEAD"]).stdout.decode().strip()
        if r_add.returncode or r_gl.returncode or r_ci.returncode or not xrev:
            raise CaseError(f"r74 witness fixture: add={r_add.returncode} gitlink={r_gl.returncode} "
                            f"commit={r_ci.returncode}")
        os.makedirs(os.path.join(xrepo, "tools", "sub"))
        x_clean = tree_divergence(xrepo, xrev)
        os.unlink(os.path.join(xrepo, "tools", "lnk"))
        os.symlink("counter.py", os.path.join(xrepo, "tools", "lnk"))
        x_tgt = tree_divergence(xrepo, xrev)
        check("witness: a gitlink whose directory is present is no divergence", x_clean == [], f"{x_clean}")
        check("witness: a retargeted tracked symlink is a target divergence",
              x_tgt == [("tools/lnk", "target")], f"{x_tgt}")
    except (CaseError, OSError) as exc:
        check("witness r74: fixture set-up", False, f"{exc}")
    setup_only = [(".gitattributes", "untracked")]
    check("row scope: a set-up-only divergence is not the row's (FWw, FC1, FC2)",
          all(row_scope(CASE_SPECS[k], setup_only) == [] for k in ("FWw", "FC1", "FC2")))
    check("row scope: a divergence on the row's forged path is kept",
          row_scope(CASE_SPECS["FC2"], [("tools/counter.py", "bytes")] + setup_only)
          == [("tools/counter.py", "bytes")])
    check("row scope: a failed read stays a failed read", row_scope(CASE_SPECS["FWw"], None) is None)
    check("row scope: a row with no declared forged path keeps nothing (fail closed)",
          row_scope({"name": "synthetic"}, [("tools/counter.py", "bytes")]) == [])
    acc = [r[0] for r in rows if r[1] == "refuse" and r[3] == "accept"]
    nofp = [k for k in acc if not forge_paths(CASE_SPECS[k])]
    check("forge paths: every base-accepted refuse row declares a forged path", acc and not nofp, f"{nofp}")
    unw2 = {"counts": dict(zero, new_unwitnessed=1), "n_accept": 0, "regress": "PASS", "all_new_match": True}
    check("claim verdict: one unwitnessed new-slot forgery fails the claim", claim_upheld(unw2) is False)
''')

open("census/round-74/c1-counter.py", "w").write(src)
print("wrote census/round-74/c1-counter.py sha256", hashlib.sha256(src.encode()).hexdigest())
