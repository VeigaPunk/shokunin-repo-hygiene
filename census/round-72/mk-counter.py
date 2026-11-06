#!/usr/bin/env python3
"""souji r72: derive census/round-72/c1-counter.py and c1-matrix.tsv from the frozen r71 counter
(census/round-71/c1-counter.py, sha256 7e5a694a…a3cc) by exact single-occurrence replacements
(count asserted), the lane's successor pattern (r71 mk-counter.py). The r71 counter is NOT amended
(Q131). Base expectations for the 70 carried rows are read from the committed r71 receipt
census/round-71/records/c1-after.txt (CASE lines, base slot = writer at 8b9345b1).
Usage (from the lane root): python3 -B census/round-72/mk-counter.py"""
import hashlib
import re
import sys

src = open("census/round-71/c1-counter.py").read()
assert hashlib.sha256(src.encode()).hexdigest().startswith("7e5a694a"), "unexpected r71 counter bytes"


def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        sys.exit(f"pattern count {n} != {count}: {old[:80]!r}")
    src = src.replace(old, new)


# 1. docstring head
rep('"""c1-counter.py — souji round-71 C1/C2 counter (L1-built, pre-freeze).\n\n'
    'Round 71 (successor of census/round-70/c1-counter.py; the frozen r70 counter is NOT amended — Q131):\n',
    '''"""c1-counter.py — souji round-72 C1/C2 counter (L1-built, committed after the r72 freeze 23372f36).

Round 72 (successor of census/round-71/c1-counter.py; the frozen r71 counter is NOT amended — Q131):

  * Base-slot binding (C1, r71 routed D2 / S71MutCounter F1). The matrix gains a fourth column,
    `base_expect`: the frozen verdict of the declared reference-weak base writer (the writer at
    --base-rev; for r72 8b9345b1, the pre-r71 writer). Carried rows take the base verdicts printed
    in census/round-71/records/c1-after.txt; the five FW rows take `accept` (pre-freeze probe
    census/round-72/probes/fw-shapes-probe.txt). Every row whose base verdict differs from its
    base_expect counts in `base_mismatches`; SUMMARY prints it and claim_upheld requires 0, so a
    fixture that stops forging the weak base (S71MutCounter Y4/Y6/Y10: base_forgeries 7 -> 2 or 5
    with EXIT=0 under r71) now fails the verdict. Battery MUTANT lines print it; the battery rc
    does not read it (C2 stays separable).
  * Selftest section (9) (C1): (9a) a base witness — the seven r71 forging rows (AS1 AS2 FC1 FC2 FC3
    FM1 FM2) are rebuilt and run against the base writer, and each base verdict must equal its
    base_expect (kills Y4 Y6 Y10); (9b) claim_upheld is false on one base mismatch; (9c) a member
    name with a path separator alone (`sub/M1`) is refused by the name rule (Y1); (9d) a SHA256SUMS
    line naming a dot-file without a separator is refused as non-plain (Y9); (9e) clean_env scrubs
    every name of its scrub tuple, not only the pathspec variables (Z1, S71CriticClaims).
  * C2 coverage: five rows appended (FWr FWi FWp FWw FWs), each `refuse RECEIPT-FILTER-DRIVER-SET`
    with base_expect `accept`: FWr a pre-run forgery under a configured driver whose wrapped command
    restores the bytes and unsets the driver (only the pre-run witness sees it); FWi an honest tree
    whose wrapped command forges same-size bytes and creates the attribute and driver (only the
    post-run witness sees it); FWp a `filter.<d>.process` long-running driver (gitattributes(5)
    "Long Running Filter Process", S313); FWw a committed empty .gitattributes whose worktree copy
    filters itself back to empty and assigns the forging driver (the index copy carries no filter:
    git-check-attr(1) --cached, S312; status reads the worktree file, S314); FWs a driver literally
    named `set`.

Round 71 text (carried; describes the r71 duties this file still performs):

Round 71 (successor of census/round-70/c1-counter.py; the frozen r70 counter is NOT amended — Q131):
''')

# 2. instrument path
rep('COUNTER_REL = "census/round-71/c1-counter.py"', 'COUNTER_REL = "census/round-72/c1-counter.py"')

# 3. matrix order
rep('"FCh", "FCh2", "FM1", "FM2", "FMh"]\n',
    '"FCh", "FCh2", "FM1", "FM2", "FMh",\n              "FWr", "FWi", "FWp", "FWw", "FWs"]\n')

# 4. row specs
rep('    "FMh":  {"name": "local-filemode-false-honest", "env_kind": "local-filemode"},\n}\n',
    '''    "FMh":  {"name": "local-filemode-false-honest", "env_kind": "local-filemode"},
    # r72 C2 rows (S71MutWriter W3/W4/W5/W6/W8 routes; pre-freeze probe fw-shapes-probe.txt).
    "FWr":  {"name": "prerun-forged-driver-restored-and-unset-inrun", "env_kind": "info-attributes-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE, "inrun": "restore-unset-driver"},
    "FWi":  {"name": "inrun-forge-and-driver-creation", "inrun": "create-driver-forge"},
    "FWp":  {"name": "process-driver-forged", "env_kind": "info-process-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "FWw":  {"name": "worktree-only-attributes-forged", "env_kind": "worktree-only-attributes",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "FWs":  {"name": "driver-named-set-forged", "env_kind": "info-filter-named-set",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
}
''')

# 5. helper code for the FW rows (after the r71 filter class constant)
rep('CLASS_FILTER = "RECEIPT-FILTER-DRIVER-SET"\n',
    '''CLASS_FILTER = "RECEIPT-FILTER-DRIVER-SET"
# r72 C2: wrapped-command helpers and the long-running process driver for the FW rows.
RESTORE_UNSET_CODE = ("import subprocess, sys\\n"
                      "open(sys.argv[1], 'wb').write(sys.argv[2].encode('latin-1'))\\n"
                      "subprocess.run(['git', '-C', sys.argv[3], 'config', '--unset', 'filter.t.clean'], check=True)\\n")
CREATE_FORGE_CODE = ("import os, subprocess, sys\\n"
                     "repo = sys.argv[1]\\n"
                     "open(os.path.join(repo, 'tools', 'counter.py'), 'wb').write(sys.argv[2].encode('latin-1'))\\n"
                     "os.makedirs(os.path.join(repo, '.git', 'info'), exist_ok=True)\\n"
                     "open(os.path.join(repo, '.git', 'info', 'attributes'), 'wb').write(b'tools/counter.py filter=t\\\\n')\\n"
                     "subprocess.run(['git', '-C', repo, 'config', 'filter.t.clean', sys.argv[3]], check=True)\\n")
# pkt-line v2 long-running filter (gitattributes(5) "Long Running Filter Process"); clean maps v2 -> v1.
PROC_FILTER_CODE = r\'\'\'import sys
i, o = sys.stdin.buffer, sys.stdout.buffer
def rd():
    h = i.read(4)
    if not h:
        sys.exit(0)
    n = int(h, 16)
    return None if n == 0 else i.read(n - 4)
def wr(b):
    o.write(b"%04x" % (len(b) + 4) + b)
def fl():
    o.write(b"0000"); o.flush()
def lst():
    out = []
    while True:
        p = rd()
        if p is None:
            return out
        out.append(p)
lst(); wr(b"git-filter-server\\n"); wr(b"version=2\\n"); fl()
lst(); wr(b"capability=clean\\n"); fl()
while True:
    hdr = lst()
    data = b"".join(lst())
    cmd = [h for h in hdr if h.startswith(b"command=")]
    if cmd and cmd[0] == b"command=clean\\n":
        data = data.replace(b"v2", b"v1")
    wr(b"status=success\\n"); fl()
    if data:
        wr(data)
    fl(); fl()
\'\'\'
WITNESS_ROWS = ("AS1", "AS2", "FC1", "FC2", "FC3", "FM1", "FM2")
''')

# 6. in-run kinds
rep('    raise CaseError(f"unknown in-run kind {kind!r}")\n',
    '''    if kind == "restore-unset-driver":
        # FWr: restore the committed bytes and unset the driver; only the pre-run witness saw both.
        return [sys.executable, "-c", RESTORE_UNSET_CODE, os.path.join(tools, "counter.py"),
                _b(SEED_COUNTER), repo]
    if kind == "create-driver-forge":
        # FWi: forge same-size bytes and create info/attributes + the clean driver in-run.
        return [sys.executable, "-c", CREATE_FORGE_CODE, repo, _b(FORGED_SAMESIZE), FILTER_CLEAN]
    raise CaseError(f"unknown in-run kind {kind!r}")
''')

# 7. fixture kinds
rep('        elif kind != "replace-base":\n            raise CaseError(f"unknown env_kind {kind!r}")\n',
    '''        elif kind == "info-process-filter":
            # FWp: a long-running process driver (no clean key) named by info/attributes.
            pf = os.path.join(case_dir, "proc-filter.py")
            with open(pf, "w", encoding="utf-8") as f:
                f.write(PROC_FILTER_CODE)
            os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
            with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
                f.write(b"tools/counter.py filter=p\\n")
            _cfg(repo, "filter.p.process", f"{sys.executable} -B {pf}")
        elif kind == "worktree-only-attributes":
            # FWw: commit an EMPTY .gitattributes (index size 0, so git re-hashes it through its
            # filter), then give the worktree copy a self-erasing filter and the forging driver.
            with open(os.path.join(repo, ".gitattributes"), "wb") as f:
                f.write(b"")
            dates = {"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE}
            for args in (["add", ".gitattributes"], ["commit", "-q", "-m", "r72 empty attributes"]):
                r = git_run(repo, args, env=dates)
                if r.returncode != 0:
                    raise CaseError(f"attributes {args[0]} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
            with open(os.path.join(repo, ".gitattributes"), "wb") as f:
                f.write(b".gitattributes filter=e\\ntools/counter.py filter=t\\n")
            _cfg(repo, "filter.e.clean", "cat >/dev/null")
            _cfg(repo, "filter.t.clean", FILTER_CLEAN)
        elif kind == "info-filter-named-set":
            # FWs: a driver literally named `set` (check-attr prints the same text as the boolean state).
            os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
            with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
                f.write(b"tools/counter.py filter=set\\n")
            _cfg(repo, "filter.set.clean", FILTER_CLEAN)
        elif kind != "replace-base":
            raise CaseError(f"unknown env_kind {kind!r}")
''')

# 8. row env: repository-state kinds
rep('                "info-attributes-filter", "local-filemode"):\n',
    '                "info-attributes-filter", "local-filemode", "info-process-filter",\n'
    '                "worktree-only-attributes", "info-filter-named-set"):\n')

# 9. matrix loader: fourth column base_expect
rep('''def load_matrix(path: str) -> tuple[Optional[list[tuple[str, str, str]]], str]:''',
    '''def load_matrix(path: str) -> tuple[Optional[list[tuple[str, str, str, str]]], str]:''')
rep('''    if lines[0].split("\\t") != ["case", "expect", "expected_class"]:
        return None, f"bad header: {lines[0]!r}"
    rows: list[tuple[str, str, str]] = []
    for i, line in enumerate(lines[1:], 2):
        parts = line.split("\\t")
        if len(parts) != 3:
            return None, f"line {i}: expected 3 tab-separated fields, got {len(parts)}"
        case, expect, klass = parts
''', '''    if lines[0].split("\\t") != ["case", "expect", "expected_class", "base_expect"]:
        return None, f"bad header: {lines[0]!r}"
    rows: list[tuple[str, str, str, str]] = []
    for i, line in enumerate(lines[1:], 2):
        parts = line.split("\\t")
        if len(parts) != 4:
            return None, f"line {i}: expected 4 tab-separated fields, got {len(parts)}"
        case, expect, klass, base_expect = parts
        if base_expect not in ("accept", "refuse"):
            return None, f"line {i}: base_expect must be accept|refuse, got {base_expect!r}"
''')
rep('        rows.append((case, expect, klass))\n', '        rows.append((case, expect, klass, base_expect))\n')

# 10. evaluate: base binding
rep('''    c = {"base_forgeries": 0, "base_honest": 0, "new_forgeries": 0, "new_honest": 0,
         "class_mismatches": 0, "new_echo": 0, "errors": 0}''',
    '''    c = {"base_forgeries": 0, "base_honest": 0, "new_forgeries": 0, "new_honest": 0,
         "class_mismatches": 0, "new_echo": 0, "errors": 0, "base_mismatches": 0}''')
rep('    for letter, expect, klass in rows:\n        spec = CASE_SPECS[letter]\n',
    '    for letter, expect, klass, base_expect in rows:\n        spec = CASE_SPECS[letter]\n')
rep('''            c["errors"] += 1
            row_fate.append({"letter": letter, "expect": expect, "verdict": "error",
                             "class_ok": False, "echo": False})''',
    '''            c["errors"] += 1
            c["base_mismatches"] += 1
            row_fate.append({"letter": letter, "expect": expect, "verdict": "error",
                             "class_ok": False, "echo": False, "base": "error"})''')
rep('''        lines.append(f"CASE {letter} expect={expect} base={b_v} base_findings={b_f} "
                     f"new={n_v} new_findings={n_f} new_echo={str(n_echo).lower()}")''',
    '''        if b_v != base_expect:
            c["base_mismatches"] += 1
        lines.append(f"CASE {letter} expect={expect} base={b_v} base_findings={b_f} "
                     f"new={n_v} new_findings={n_f} new_echo={str(n_echo).lower()} "
                     f"base_expect={base_expect}")''')
rep('''                         "class_ok": bool(n_v == "refuse" and klass and klass in n_se),
                         "echo": n_echo})''',
    '''                         "class_ok": bool(n_v == "refuse" and klass and klass in n_se),
                         "echo": n_echo, "base": b_v})''')
rep('''            and c["class_mismatches"] == 0 and c["new_echo"] == 0
            and res["regress"] == "PASS" and res["all_new_match"])''',
    '''            and c["class_mismatches"] == 0 and c["new_echo"] == 0
            and res["regress"] == "PASS" and res["all_new_match"]
            and c.get("base_mismatches", 1) == 0)''')
rep('''            f"base_honest={c['base_honest']} new_forgeries={c['new_forgeries']} "''',
    '''            f"base_honest={c['base_honest']} base_mismatches={c['base_mismatches']} "
            f"new_forgeries={c['new_forgeries']} "''')
rep('''                 f"label={oc['label']} errors={oc['errors']} regress={res['regress']} "''',
    '''                 f"label={oc['label']} errors={oc['errors']} regress={res['regress']} "
                 f"base_mismatches={res['counts']['base_mismatches']} "''')

# 11. selftest synthetic TSVs carry the fourth column
rep('        f.write("case\\texpect\\texpected_class\\n")\n',
    '        f.write("case\\texpect\\texpected_class\\tbase_expect\\n")\n', count=3)
rep('''        for letter, expect, klass in rows:
            if letter != "T5":
                f.write(f"{letter}\\t{expect}\\t{klass}\\n")''',
    '''        for letter, expect, klass, bexp in rows:
            if letter != "T5":
                f.write(f"{letter}\\t{expect}\\t{klass}\\t{bexp}\\n")''')
rep('''        for letter, expect, klass in rows:
            f.write(f"{letter}\\t{expect}\\t{klass}\\n")
        f.write("T6\\trefuse\\tRECEIPT-STATE-CHANGED-DURING-RUN\\n")''',
    '''        for letter, expect, klass, bexp in rows:
            f.write(f"{letter}\\t{expect}\\t{klass}\\t{bexp}\\n")
        f.write("T6\\trefuse\\tRECEIPT-STATE-CHANGED-DURING-RUN\\trefuse\\n")''')
rep('''        for letter, expect, klass in rows[:2]:
            f.write(f"{letter}\\t{expect}\\t{klass}\\n")''',
    '''        for letter, expect, klass, bexp in rows[:2]:
            f.write(f"{letter}\\t{expect}\\t{klass}\\t{bexp}\\n")''')

# 12. selftest section (9)
rep('''    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:''',
    '''    # (9) r72 C1: the defects the r71 wave found in this instrument (S71MutCounter Y1 Y4 Y6 Y9 Y10,
    # S71CriticClaims Z1) and the base-slot binding (r71 routed D2).
    # (9a) base witness: each r71 forging row still forges the reference-weak base writer.
    wbytes, werr = git_show(root, f"{base_rev}:{BASE_REL}")
    if wbytes is None:
        check("base witness: base bytes readable", False, werr)
    else:
        wslot = os.path.join(st, "witness-base.py")
        write_exec(wslot, wbytes)
        wrows = [r for r in rows if r[0] in WITNESS_ROWS]
        wres = evaluate(wrows, wslot, wslot, os.path.join(st, "witness"), None)
        got = {f["letter"]: f.get("base") for f in wres["row_fate"]}
        bad = [f"{r[0]}:{got.get(r[0])}!={r[3]}" for r in wrows if got.get(r[0]) != r[3]]
        check("base witness: every r71 forging row forges the base writer as its base_expect says",
              len(wrows) == len(WITNESS_ROWS) and not bad and wres["counts"]["base_mismatches"] == 0,
              f"rows={len(wrows)} mismatches={bad}")
    # (9b) the verdict reads the base slot.
    zero = {"base_forgeries": 0, "base_honest": 0, "new_forgeries": 0, "new_honest": 0,
            "class_mismatches": 0, "new_echo": 0, "errors": 0, "base_mismatches": 0}
    good_res = {"counts": dict(zero), "n_accept": 0, "regress": "PASS", "all_new_match": True}
    bad_res = {"counts": dict(zero, base_mismatches=1), "n_accept": 0, "regress": "PASS",
               "all_new_match": True}
    check("claim verdict: one base mismatch fails the claim; none passes it",
          claim_upheld(good_res) is True and claim_upheld(bad_res) is False)
    # (9c) Y1: a separator alone (no traversal) fails the NAME rule, not the listing rule.
    sep, e_sep = verify_members(bdir, ["sub/M1"])
    check("member binding: a member name with a path separator is refused as not plain",
          sep is None and "plain" in e_sep, e_sep)
    # (9d) Y9: a leading-dot SHA256SUMS name without a separator is refused as non-plain.
    hdir = os.path.join(st, "battery-dotname")
    os.makedirs(hdir)
    with open(os.path.join(hdir, "M1.py"), "wb") as f:
        f.write(b"print('m1')\\n")
    with open(os.path.join(hdir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  M1.py\\n{good}  .hidden.py\\n")
    dot, e_dot = verify_members(hdir, ["M1"])
    check("member binding: a SHA256SUMS line naming a dot-file is refused as non-plain",
          dot is None and "non-plain" in e_dot, e_dot)
    # (9e) Z1: clean_env scrubs every name of its tuple from the ambient environment.
    scrub = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
             "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_CONFIG_COUNT",
             "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_SYSTEM",
             "GIT_NO_REPLACE_OBJECTS", "GIT_COMMON_DIR", "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES",
             "HOME", "XDG_CONFIG_HOME", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0", "GIT_TRACE",
             "GIT_TRACE2_EVENT", "GIT_TEMPLATE_DIR", "GIT_ATTR_SOURCE", "GIT_EXEC_PATH",
             "GIT_DEFAULT_HASH")
    sentinel = "/nonexistent-r72-ambient-probe"
    saved_amb = {k: os.environ.get(k) for k in scrub}
    try:
        for k in scrub:
            os.environ[k] = sentinel
        amb = clean_env()
    finally:
        for k, v in saved_amb.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    kept_amb = sorted(k for k in scrub if amb.get(k) == sentinel)
    check("clean_env: every scrub-tuple name is removed from the ambient environment",
          kept_amb == [], f"kept={kept_amb}")

    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:''')

open("census/round-72/c1-counter.py", "w").write(src)

# matrix
base = {}
for line in open("census/round-71/records/c1-after.txt"):
    m = re.match(r"^CASE (\S+) expect=\S+ base=(\S+) ", line)
    if m:
        base[m.group(1)] = m.group(2)
old = [l.rstrip("\n") for l in open("census/round-71/c1-matrix.tsv") if l.strip()]
assert old[0] == "case\texpect\texpected_class"
out = ["case\texpect\texpected_class\tbase_expect"]
for l in old[1:]:
    case = l.split("\t")[0]
    assert base.get(case) in ("accept", "refuse"), (case, base.get(case))
    out.append(f"{l}\t{base[case]}")
for case in ("FWr", "FWi", "FWp", "FWw", "FWs"):
    out.append(f"{case}\trefuse\tRECEIPT-FILTER-DRIVER-SET\taccept")
open("census/round-72/c1-matrix.tsv", "w").write("\n".join(out) + "\n")
print(f"counter sha256={hashlib.sha256(src.encode()).hexdigest()} rows={len(out) - 1} "
      f"base_accept={sum(1 for l in out[1:] if l.endswith('accept') and l.split(chr(9))[3] == 'accept')}")
