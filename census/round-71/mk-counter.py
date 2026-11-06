import sys
src = open("census/round-70/c1-counter.py").read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        sys.exit(f"pattern count {n} != {count}: {old[:80]!r}")
    src = src.replace(old, new)

rep('"""c1-counter.py — souji round-70 C1/C2 counter (L1-built, pre-freeze).\n',
'''"""c1-counter.py — souji round-71 C1/C2 counter (L1-built, pre-freeze).

Round 71 (successor of census/round-70/c1-counter.py; the frozen r70 counter is NOT amended — Q131):

  * C1 operability (writer surface): the 59 r70 rows are carried unchanged and 11 attribute /
    core.fileMode rows are appended (S70Sentinel F1/F2, routed r71). A clean filter driver
    (`filter.<driver>.clean`, gitattributes(5) "filter") that maps size-preserving forged bytes
    back to the committed bytes makes `git status` report a clean tree; the attribute can come from
    a caller-injected GIT_ATTR_SOURCE tree (AS1/AS2), a committed .gitattributes (FC1/FC2) or
    $GIT_DIR/info/attributes (FC3). A repository-local core.fileMode=false hides a mode flip made
    before (FM1) or during (FM2) the run. ASh/FCh/FCh2/FMh are the honest rows: an attribute source
    with no filter, a filter attribute with no configured driver, a configured driver no tracked
    path carries, and core.fileMode=false over an unchanged tree. Forged bytes are size-preserving
    (`counter v2` for the committed `counter v1`): a size change is caught by the stat check before
    any clean filter runs (pre-freeze probe census/round-71/probes/attr-filemode-probe-base.txt).
  * C2 calibration (instrument self-check): the selftest gains section (8), which asserts the
    behaviours the five r70-surviving counter mutants X6-X10 (S70MutCounter, frozen in
    census/round-71/c2-mutants.json) remove: the battery error gate, the ambient pathspec scrub of
    clean_env, the row pathspec_env merge of case_env, and the SHA256SUMS duplicate- and
    malformed-line checks. Battery member names are validated (no path separator, no leading dot;
    S70Sentinel F3/F4) and the SHA256SUMS listing must name the member file exactly.

Round 70 text (carried; describes the r70 duties this file still performs):
''')
rep('COUNTER_REL = "census/round-70/c1-counter.py"', 'COUNTER_REL = "census/round-71/c1-counter.py"')
rep('''              "LA", "LD", "LN4", "LU1", "LG1", "LA9", "GA", "GD", "NGA", "NGD", "ICA", "ICD"]''',
'''              "LA", "LD", "LN4", "LU1", "LG1", "LA9", "GA", "GD", "NGA", "NGD", "ICA", "ICD",
              "AS1", "AS2", "ASh", "FC1", "FC2", "FC3", "FCh", "FCh2", "FM1", "FM2", "FMh"]''')
rep('''LP_ENV = {"GIT_LITERAL_PATHSPECS": "1"}
''', '''LP_ENV = {"GIT_LITERAL_PATHSPECS": "1"}

# r71 C1: size-preserving forged counter bytes and the clean filter that maps them back.
FORGED_SAMESIZE = b"counter v2\\n"
FILTER_CLEAN = "sed s/v2/v1/"
CLASS_FILTER = "RECEIPT-FILTER-DRIVER-SET"
''')
rep('''            "pathspec_env": {"GIT_ICASE_PATHSPECS": "1"}},
}''', '''            "pathspec_env": {"GIT_ICASE_PATHSPECS": "1"}},
    # r71 C1 rows (S70Sentinel F1/F2). AS*: the filter attribute arrives through a caller
    # GIT_ATTR_SOURCE tree (a commit object beside HEAD, read from case-dir/attr-source.txt).
    "AS1":  {"name": "attr-source-filter-forged", "env_kind": "attr-source-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "AS2":  {"name": "attr-source-filter-inrun-edit", "env_kind": "attr-source-filter",
             "inrun": "edit-counter-samesize"},
    "ASh":  {"name": "attr-source-text-honest", "env_kind": "attr-source-text"},
    # FC*: the filter attribute is repository state (committed .gitattributes or info/attributes).
    "FC1":  {"name": "committed-filter-forged", "env_kind": "committed-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "FC2":  {"name": "committed-filter-inrun-edit", "env_kind": "committed-filter",
             "inrun": "edit-counter-samesize"},
    "FC3":  {"name": "info-attributes-filter-forged", "env_kind": "info-attributes-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "FCh":  {"name": "committed-filter-no-driver-honest", "env_kind": "committed-filter-nodriver"},
    "FCh2": {"name": "driver-configured-no-tracked-path-honest", "env_kind": "driver-unused"},
    # FM*: repository-local core.fileMode=false.
    "FM1":  {"name": "local-filemode-false-prerun-chmod", "env_kind": "local-filemode",
             "chmod_notes": True},
    "FM2":  {"name": "local-filemode-false-inrun-chmod", "env_kind": "local-filemode",
             "inrun": "chmod-clean"},
    "FMh":  {"name": "local-filemode-false-honest", "env_kind": "local-filemode"},
}''')
rep('''    raise CaseError(f"unknown in-run kind {kind!r}")''',
'''    if kind == "edit-counter-samesize":
        # AS2/FC2: size-preserving in-run edit of a tracked file a clean filter maps back.
        return [sys.executable, "-c", EDIT_CODE, os.path.join(tools, "counter.py"), "wb",
                _b(FORGED_SAMESIZE)]
    if kind == "chmod-clean":
        # FM2: in-run 644 -> 755 flip of a clean tracked file (no --allow-dirty).
        return [sys.executable, "-c", CHMOD_CODE, os.path.join(tools, "notes.txt")]
    raise CaseError(f"unknown in-run kind {kind!r}")''')
# mutate: env_kind handlers for r71 rows (before the final unknown check)
rep('''        elif kind != "replace-base":
            raise CaseError(f"unknown env_kind {kind!r}")''',
'''        elif kind in ("attr-source-filter", "attr-source-text"):
            # AS1/AS2/ASh: a commit object (not on any ref) whose tree holds only .gitattributes;
            # its id is the caller's GIT_ATTR_SOURCE (read back by _row_env).
            line = (b"tools/counter.py filter=t\\n" if kind == "attr-source-filter" else b"*.md text\\n")
            if kind == "attr-source-filter":
                _cfg(repo, "filter.t.clean", FILTER_CLEAN)
            blob = _git_in(repo, ["hash-object", "-w", "--stdin"], line)
            tree = _git_in(repo, ["mktree"], b"100644 blob %s\\t.gitattributes\\n" % blob.encode())
            commit = _git_in(repo, ["commit-tree", "-m", "r71 attr source", tree], b"",
                             env={"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE})
            with open(os.path.join(case_dir, "attr-source.txt"), "w", encoding="ascii") as f:
                f.write(commit)
        elif kind in ("committed-filter", "committed-filter-nodriver", "driver-unused"):
            # FC1/FC2/FCh/FCh2: a committed .gitattributes; FCh2 names only a path that is not
            # tracked, so its configured driver applies to no tracked path.
            line = b"nosuch.bin filter=t\\n" if kind == "driver-unused" else b"tools/counter.py filter=t\\n"
            with open(os.path.join(repo, ".gitattributes"), "wb") as f:
                f.write(line)
            dates = {"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE}
            for args in (["add", ".gitattributes"], ["commit", "-q", "-m", "r71 attributes"]):
                r = git_run(repo, args, env=dates)
                if r.returncode != 0:
                    raise CaseError(f"attributes {args[0]} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
            if kind != "committed-filter-nodriver":
                _cfg(repo, "filter.t.clean", FILTER_CLEAN)
        elif kind == "info-attributes-filter":
            # FC3: the attribute lives in $GIT_DIR/info/attributes (never committed, never in status).
            os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
            with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
                f.write(b"tools/counter.py filter=t\\n")
            _cfg(repo, "filter.t.clean", FILTER_CLEAN)
        elif kind == "local-filemode":
            # FM1/FM2/FMh: repository-local core.fileMode=false (the r68 PK4/PK7 rows inject it
            # only through caller global/system config files, which the writer already pins).
            _cfg(repo, "core.fileMode", "false")
            if spec.get("chmod_notes"):
                os.chmod(os.path.join(repo, "tools", "notes.txt"), 0o755)
        elif kind != "replace-base":
            raise CaseError(f"unknown env_kind {kind!r}")


def _cfg(repo: str, key: str, val: str) -> None:
    r = git_run(repo, ["config", key, val])
    if r.returncode != 0:
        raise CaseError(f"fixture config {key} failed")


def _git_in(repo: str, args: list[str], data: bytes, env: Optional[dict] = None) -> str:
    r = subprocess.run(["git", "-C", repo, *args], input=data, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=clean_env(env), timeout=120)
    out = r.stdout.decode().strip()
    if r.returncode != 0 or not out:
        raise CaseError(f"git {args[0]} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    return out''')
rep('''    if kind == "replace-ref-head":
        # PK6: repository-state route (refs/replace); no caller env.
        return {}
    return None''', '''    if kind == "replace-ref-head":
        # PK6: repository-state route (refs/replace); no caller env.
        return {}
    if kind in ("attr-source-filter", "attr-source-text"):
        # AS1/AS2/ASh: the caller's GIT_ATTR_SOURCE names the beside-HEAD attributes commit.
        try:
            with open(os.path.join(os.path.dirname(repo), "attr-source.txt"), encoding="ascii") as f:
                return {"GIT_ATTR_SOURCE": f.read().strip()}
        except OSError as exc:
            raise CaseError(f"attr-source.txt unreadable: {exc}")
    if kind in ("committed-filter", "committed-filter-nodriver", "driver-unused",
                "info-attributes-filter", "local-filemode"):
        # FC*/FM*: repository-state routes; no caller env.
        return {}
    return None''')
# verify_members: validate names and sums names (S70Sentinel F3/F4)
rep('''    sums_path = os.path.join(battery_dir, "SHA256SUMS")''',
'''    for name in names:
        # r71 (S70Sentinel F3/F4): a member name is one plain path component.
        if not MEMBER_RE.match(name):
            return None, f"member name {name!r} is not a plain file name"
    sums_path = os.path.join(battery_dir, "SHA256SUMS")''')
rep('''        if m.group(2) in listed:''', '''        if "/" in m.group(2) or m.group(2).startswith("."):
            return None, f"SHA256SUMS line {i} names a non-plain file"
        if m.group(2) in listed:''')
rep('''        path = os.path.join(battery_dir, fname)
        if fname not in listed:''', '''        path = os.path.join(battery_dir, fname)
        if os.path.islink(path):
            return None, f"member {fname} is a symlink"
        if fname not in listed:''')
rep('''def verify_members(''', '''MEMBER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def verify_members(''')
# selftest section (8)
rep('''    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        print(f"selftest {'ok' if ok else 'FAIL'}: {name}" + (f" | {detail}" if detail else ""))''',
'''    # (8) r71 C2: the behaviours the five r70-surviving mutants X6-X10 remove (S70MutCounter).
    # (8a) X6: an errored member fails the battery even when error was its expectation.
    _, x6_ok, x6_rc = battery_verdict([("E", "error", "error")])
    check("battery verdict: an errored member makes rc 1 even when expected", x6_rc == 1,
          f"all_match={x6_ok} rc={x6_rc}")
    # (8b) X7: clean_env drops every ambient pathspec variable.
    saved_env = {k: os.environ.get(k) for k in PATHSPEC_VARS}
    try:
        for k in PATHSPEC_VARS:
            os.environ[k] = "1"
        leaked = sorted(k for k in PATHSPEC_VARS if k in clean_env())
        kept = clean_env({"GIT_LITERAL_PATHSPECS": "1"}).get("GIT_LITERAL_PATHSPECS")
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    check("clean_env: ambient pathspec variables are scrubbed", leaked == [], f"leaked={leaked}")
    check("clean_env: a row's own caller env is applied after the scrub", kept == "1", f"kept={kept}")
    # (8c) X8: case_env merges each row's pathspec_env, on its own and over a row env.
    la = case_env(CASE_SPECS["LA"], os.path.join(st, "nonexistent-repo"))
    check("case_env: LA carries GIT_LITERAL_PATHSPECS=1", (la or {}).get("GIT_LITERAL_PATHSPECS") == "1",
          f"env={la}")
    merged = case_env({"env_kind": "global-filemode", "pathspec_env": {"GIT_ICASE_PATHSPECS": "1"}},
                      os.path.join(st, "nonexistent-repo"))
    check("case_env: pathspec_env merges over a row env",
          (merged or {}).get("GIT_ICASE_PATHSPECS") == "1" and "GIT_CONFIG_GLOBAL" in (merged or {}),
          f"env={merged}")
    # (8d) X9/X10: duplicate and malformed SHA256SUMS lines are refused beside a valid line.
    ddir = os.path.join(st, "battery-dup")
    os.makedirs(ddir)
    with open(os.path.join(ddir, "M1.py"), "wb") as f:
        f.write(b"print('m1')\\n")
    with open(os.path.join(ddir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  M1.py\\n{good} *M1.py\\n")
    dup, e_dup = verify_members(ddir, ["M1"])
    check("member binding: a member listed twice is refused", dup is None and "twice" in e_dup, e_dup)
    mdir = os.path.join(st, "battery-malformed")
    os.makedirs(mdir)
    with open(os.path.join(mdir, "M1.py"), "wb") as f:
        f.write(b"print('m1')\\n")
    with open(os.path.join(mdir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  M1.py\\nGARBAGE-LINE-NOT-A-DIGEST\\n")
    mal, e_mal = verify_members(mdir, ["M1"])
    check("member binding: a malformed line beside a valid one is refused",
          mal is None and "malformed" in e_mal, e_mal)
    # (8e) S70Sentinel F3/F4: traversal names and symlinked members are refused.
    trav, e_trav = verify_members(bdir, ["../M1"])
    check("member binding: a traversal member name is refused", trav is None and "plain" in e_trav, e_trav)
    sdir = os.path.join(st, "battery-sumsname")
    os.makedirs(sdir)
    with open(os.path.join(sdir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  ../M1.py\\n")
    sn, e_sn = verify_members(sdir, ["M1"])
    check("member binding: a SHA256SUMS line naming a non-plain file is refused",
          sn is None and "non-plain" in e_sn, e_sn)
    ldir = os.path.join(st, "battery-link")
    os.makedirs(ldir)
    with open(os.path.join(st, "outside-m1.py"), "wb") as f:
        f.write(b"print('m1')\\n")
    os.symlink(os.path.join(st, "outside-m1.py"), os.path.join(ldir, "M1.py"))
    with open(os.path.join(ldir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  M1.py\\n")
    lk, e_lk = verify_members(ldir, ["M1"])
    check("member binding: a symlinked member is refused", lk is None and "symlink" in e_lk, e_lk)

    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        print(f"selftest {'ok' if ok else 'FAIL'}: {name}" + (f" | {detail}" if detail else ""))''')
open("census/round-71/c1-counter.py", "w").write(src)
print("ok")
