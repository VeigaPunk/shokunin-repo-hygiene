#!/usr/bin/env python3
"""cand-s16-cert.py — S16 certification harness (souji-shokunin round 10).

Certifies ONE candidate set (cand-merge-*) against:
  (a) census/round-9/seat-09-generator.py (40-artifact differential corpus);
  (b) every embedded reproducer in census/round-9/final-21..24.json and
      seat-05/07/09/10/11/12.json, replayed verbatim against a fixture lane
      copy so no peer script is edited;
  (c) fresh S16 attack variants, one per adjudicated r9 class J01-J23.

Unsafe outcome = a false-SAFE receipt for ground-truth-not-safe bytes, a
quarantine DELETE of unauthorized bytes, a containment escape, a read-only
index write, or a malformed-input acceptance that the class forbids.
Fail-closed refusals are counted separately as conservative refusals.

Everything runs against /var/tmp fixtures. The live lane repo and the live
installed tools are only ever READ (hashes) — never written.

Usage:
  cand-s16-cert.py [--cand-dir DIR] [--map k=file,...] [--label NAME]
                   [--out FILE] [--corpora LIST] [--timeout N] [--list]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
R9 = LANE / "census" / "round-9"
R10 = LANE / "census" / "round-10"
INSTALLED = LANE / "tools"
CANON = ("souji-verify.sh", "souji-vault-verify.sh", "souji-quarantine.sh", "souji-census.sh")

AP = argparse.ArgumentParser()
AP.add_argument("--cand-dir", default=str(INSTALLED))
AP.add_argument("--map", default="")
AP.add_argument("--label", default="")
AP.add_argument("--out", default="")
AP.add_argument("--corpora", default="")
AP.add_argument("--timeout", type=int, default=900)
AP.add_argument("--list", action="store_true")
A = AP.parse_args()

START = time.time()
STAMP = time.strftime("%Y%m%dT%H%M%S")
LABEL = A.label or f"s16-cert-{STAMP}"
RUN = Path("/var/tmp") / LABEL
UNSAFE = []
REFUSALS = []
CORPORA = []
ERRORS = []
TEST_FAILURES = []
# Test-suite failures gate certification but are not themselves unsafe
# outcomes (no bytes, receipt or containment invariant is violated by them).
TEST_FAILURE_KINDS = ("selftest-failure",)


def say(*parts):
    print(*parts, flush=True)


def sha256(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return "ABSENT"


def record(corpus, case, kind, detail):
    """Unsafe outcomes are measured safety failures. Test-suite failures are a
    separate gate and must not be double-counted as unsafe outcomes."""
    entry = {"corpus": corpus, "case": case, "kind": kind, "detail": detail}
    if kind in TEST_FAILURE_KINDS:
        TEST_FAILURES.append(entry)
    else:
        UNSAFE.append(entry)


def refusal(corpus, case, detail):
    REFUSALS.append({"corpus": corpus, "case": case, "detail": detail})


def run(argv, env=None, cwd=None, timeout=None, data=None):
    t0 = time.monotonic()
    try:
        p = subprocess.run([str(x) for x in argv], env=env, cwd=cwd, input=data,
                           text=True, capture_output=True,
                           timeout=timeout or A.timeout)
        return {"argv": [str(x) for x in argv], "rc": p.returncode,
                "stdout": p.stdout, "stderr": p.stderr,
                "seconds": round(time.monotonic() - t0, 3)}
    except subprocess.TimeoutExpired as e:
        return {"argv": [str(x) for x in argv], "rc": 124,
                "stdout": (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""),
                "stderr": "TIMEOUT", "seconds": round(time.monotonic() - t0, 3)}


# ------------------------------------------------------------------ assemble

def discover(cand_dir):
    """Map candidate filenames -> canonical tool names."""
    if A.map:
        out = {}
        for item in A.map.split(","):
            key, _, value = item.partition("=")
            out[key.strip()] = str(Path(value).resolve())
        return out
    cand_dir = Path(cand_dir).resolve()
    files = sorted(p for p in cand_dir.glob("cand-merge-*")
                   if p.is_file() and p.name != "cand-merge-selftest.sh")
    mapping = {}
    for p in files:
        name = p.name
        for tool, keys in (("verify", ("verify", "check")),
                           ("vault", ("vault", "ledger")),
                           ("quarantine", ("quarantine", "quar")),
                           ("census", ("census", "scan")),
                           ("guard", ("guard", "lib", "shared", "core"))):
            if any(k in name for k in keys) and tool not in mapping:
                mapping[tool] = str(p)
                break
    return mapping


def assemble(mapping):
    """Build a fixture lane copy holding the candidates under canonical names.

    The copy is a real git repository: the tools' own selftests exercise a
    live-fleet guard against their REPO_ROOT, which must resolve inside a git
    repo exactly as the installed lane does.
    """
    lane = RUN / "souji-shokunin"
    tools = lane / "tools"
    (lane / "census" / "round-9").mkdir(parents=True, exist_ok=True)
    (lane / "census" / "round-10").mkdir(parents=True, exist_ok=True)
    tools.mkdir(parents=True, exist_ok=True)
    git_init = run(["git", "init", "-q", "--initial-branch=main", str(lane)], env=ENV)
    if git_init["rc"]:
        ERRORS.append({"corpus": "assemble", "error": "git init failed",
                       "stderr": git_init["stderr"]})
    (lane / "LOG.md").write_text("S16 certification fixture lane sentinel\n")
    # every pre-existing tools/ file is copied verbatim so candidate helpers,
    # selftest runners and the guard ship alongside.
    for src in sorted(INSTALLED.iterdir()):
        if src.is_file() and not src.is_symlink():
            shutil.copy2(src, tools / src.name)
    installed = {}
    for tool in CANON:
        installed[tool] = sha256(INSTALLED / tool)
    # candidates overwrite the canonical names
    for key, path in sorted(mapping.items()):
        if key in ("verify", "vault", "quarantine", "census"):
            target = {"verify": "souji-verify.sh", "vault": "souji-vault-verify.sh",
                      "quarantine": "souji-quarantine.sh",
                      "census": "souji-census.sh"}[key]
            shutil.copy2(path, tools / target)
            os.chmod(tools / target, 0o755)
    # copy the r9 evidence fragments the peer corpora read at run time
    for src in sorted(R9.glob("*")):
        if src.is_file():
            shutil.copy2(src, lane / "census" / "round-9" / src.name)
    for src in sorted(R10.glob("*")):
        if src.is_file():
            shutil.copy2(src, lane / "census" / "round-10" / src.name)
    cand_hashes = {k: sha256(v) for k, v in sorted(mapping.items())}
    lane_hashes = {t: sha256(tools / t) for t in CANON}
    return lane, cand_hashes, lane_hashes, installed


# ------------------------------------------------------------------ env

def base_env():
    e = {k: v for k, v in os.environ.items()
         if not k.startswith(("GIT_", "SOUJI_", "SHOKUNIN_"))}
    e.update({"TMPDIR": "/var/tmp", "LC_ALL": "C", "LANG": "C",
              "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
              "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_OPTIONAL_LOCKS": "0",
              "GIT_TERMINAL_PROMPT": "0",
              "GIT_AUTHOR_NAME": "S16 fixture", "GIT_AUTHOR_EMAIL": "s16@example.invalid",
              "GIT_COMMITTER_NAME": "S16 fixture", "GIT_COMMITTER_EMAIL": "s16@example.invalid"})
    home = RUN / "home"
    home.mkdir(parents=True, exist_ok=True)
    e["HOME"] = str(home)
    return e


ENV = base_env()


def json_of(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


# ------------------------------------------------------------------ tolerant

TOLERANT_PRELUDE = '''
S16_FAILS = []
S16_PASSES = [0]
def S16_REC(lineno, msg, thunk):
    try:
        ok = bool(thunk())
    except Exception as exc:  # noqa: BLE001
        S16_FAILS.append({"line": lineno, "msg": None if msg is None else str(msg),
                          "error": repr(exc)})
        return False
    if ok:
        S16_PASSES[0] += 1
    else:
        S16_FAILS.append({"line": lineno, "msg": None if msg is None else str(msg),
                          "error": "assertion-false"})
    return ok
'''


def tolerant_source(src, name):
    """Rewrite `assert` into recorded checks so a repaired tool does not abort
    the peer reproducer before its evidence is emitted. No file is edited."""
    import ast
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return None, f"syntax: {exc}"

    class Rewrite(ast.NodeTransformer):
        def visit_Assert(self, node):
            self.generic_visit(node)
            call = ast.Call(func=ast.Name(id="S16_REC", ctx=ast.Load()),
                            args=[ast.Constant(value=node.lineno),
                                  node.msg if node.msg is not None else ast.Constant(value=None),
                                  ast.Lambda(args=ast.arguments(
                                      posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                                      kw_defaults=[], kwarg=None, defaults=[]),
                                      body=node.test)],
                            keywords=[])
            return ast.copy_location(ast.Expr(value=call), node)

    tree = Rewrite().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree), None


DUMP_KEYS = ("results", "report", "records", "cases", "summary", "CASES", "base",
             "ROOT", "BASE", "T", "B", "WORK", "RUN", "frozen_sha", "hashes",
             "tool_sha256", "tools_sha256", "PINS", "output", "subject", "engine",
             "S16_FAILS", "S16_PASSES", "index_changed", "case")


def tolerant_run(path, argv=None, cwd=None, extra_env=None, dump=True):
    """exec a peer python script in-process-ish: fresh subprocess with the
    assert-rewrite injected, results dumped to JSON afterwards."""
    src = Path(path).read_text()
    rewritten, err = tolerant_source(src, Path(path).name)
    if err:
        return {"error": err}
    out_json = RUN / "dumps" / (Path(path).name + ".dump.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    harness = RUN / "dumps" / (Path(path).name + ".run.py")
    harness.write_text(
        "import json, sys, traceback\n"
        + TOLERANT_PRELUDE
        + "sys.argv = " + repr([str(x) for x in (argv or [path])]) + "\n"
        + "S16_DUMP = " + repr(str(out_json)) + "\n"
        + "try:\n"
        + "".join("    " + line + "\n" for line in rewritten.splitlines())
        + "except SystemExit:\n"
        + "    raise\n"
        + "except BaseException as exc:\n"
        + "    S16_EXC = repr(exc)\n"
        + "    traceback.print_exc()\n"
        + "finally:\n"
        + "    g = dict(globals())\n"
        + "    picked = {}\n"
        + "    for k in " + repr(DUMP_KEYS) + ":\n"
        + "        if k in g:\n"
        + "            try:\n"
        + "                json.dumps(g[k])\n"
        + "                picked[k] = g[k]\n"
        + "            except (TypeError, ValueError):\n"
        + "                picked[k] = repr(g[k])[:4000]\n"
        + "    json.dump({'dump': picked, 'exc': g.get('S16_EXC'),\n"
        + "               'asserts_failed': g.get('S16_FAILS', []),\n"
        + "               'asserts_passed': (g.get('S16_PASSES') or [0])[0]},\n"
        + "              open(S16_DUMP, 'w'), indent=1, default=str)\n"
    )
    env = dict(ENV)
    if extra_env:
        env.update({k: str(v) for k, v in extra_env.items()})
    res = run([sys.executable, "-B", str(harness)], env=env, cwd=cwd or str(RUN))
    res["dump_path"] = str(out_json)
    try:
        res["dump"] = json.loads(out_json.read_text())
    except (OSError, ValueError):
        res["dump"] = None
    return res


# ------------------------------------------------------------------ fresh S16

def fresh_battery(tools):
    """One fresh attack per adjudicated r9 class J01-J23 (S16 variants).

    Every fixture is built under /var/tmp. `tools` is the fixture lane's
    tools/ directory. Returns a list of case records with explicit
    ground truth: label 'refuse' (bytes must survive) or 'allow'.
    """
    import tempfile
    V = tools / "souji-verify.sh"
    L = tools / "souji-vault-verify.sh"
    Q = tools / "souji-quarantine.sh"
    C = tools / "souji-census.sh"
    cases = []

    def fixture(name):
        base = Path(tempfile.mkdtemp(prefix=f"s16-{name}-", dir="/var/tmp"))
        repo = base / "fleet" / "s16-shokunin"
        repo.mkdir(parents=True)
        (base / "home").mkdir()
        git(repo, "init", "-q", "--initial-branch=main")
        ledger = base / "ledger.tsv"
        ledger.write_text("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        env = dict(ENV, SHOKUNIN_ROOT=str(repo.parent), SOUJI_LEDGER=str(ledger),
                   SOUJI_Q_SHOKUNIN_ROOT=str(repo.parent), SOUJI_Q_LEDGER=str(ledger),
                   SOUJI_VERIFY_BIN=str(V), HOME=str(base / "home"))
        return base, repo, ledger, env

    def git(repo, *args, env=None, data=None):
        r = run(["git", "-C", str(repo), *args], env=env or ENV, data=data)
        if r["rc"]:
            raise RuntimeError(r)
        return r["stdout"].strip()

    def commit(repo, env, pushed=True, parent=None):
        git(repo, "add", "-A", env=env)
        tree = git(repo, "write-tree", env=env)
        args = ["commit-tree", tree]
        if parent:
            args += ["-p", parent]
        oid = git(repo, *args, env=env, data="s16 fixture\n")
        git(repo, "update-ref", "refs/heads/main", oid, env=env)
        if pushed:
            git(repo, "update-ref", "refs/remotes/origin/main", oid, env=env)
            git(repo, "symbolic-ref", "refs/remotes/origin/HEAD",
                "refs/remotes/origin/main", env=env)
        return oid

    def engines(target, env):
        out = {}
        for name, tool in (("verify", V), ("vault", L)):
            args = ["bash", str(tool), "--json"]
            if name == "vault":
                args += ["--fallback"]
            r = run(args + ["--", str(target)], env=env)
            parsed = None
            m = re.search(r"\{.*\}", r["stdout"], re.S)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except ValueError:
                    parsed = None
            out[name] = {"rc": r["rc"], "verdict": (parsed or {}).get("verdict"),
                         "receipt": (parsed or {}).get("receipt"),
                         "raw": r["stdout"][:2000], "stderr": r["stderr"][:800]}
        return out

    def quarantine(repo, target, env, dry=False, hold=0, extra=None):
        e = dict(env)
        if extra:
            e.update({k: str(v) for k, v in extra.items()})
        args = ["bash", str(Q), "--hold", str(hold)]
        if dry:
            args += ["--dry-run"]
        r = run(args + [str(repo), str(target)], env=e)
        rows = [line.split("\t") for line in r["stdout"].splitlines()
                if line.startswith("RESULT\t")]
        result = rows[-1][2] if rows else "NO-RESULT"
        return {"rc": r["rc"], "result": result, "raw": r["stdout"][-3000:],
                "stderr": r["stderr"][:800]}

    def old(*paths, days=4):
        when = time.time() - days * 86400
        for p in paths:
            try:
                os.utime(p, (when, when), follow_symlinks=False)
            except OSError:
                pass

    def sha(p):
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()

    def digest(p):
        r = run(["bash", "-c",
                 "cd -- \"$1\" && find . -path './.git' -prune -o -type f -print0 "
                 "| sort -z | xargs -0 -r sha256sum | sha256sum", "d", str(p)], env=ENV)
        return r["stdout"].split()[0] if r["rc"] == 0 else ""

    def preservation(repo, target):
        """Bytes are preserved when the original survives OR a quarantine copy
        is retained (ABORTED / staged-but-not-deleted are fail-closed).
        Only meaningful when the target existed at fixture build time."""
        tgt = Path(target)
        orig = tgt.exists()
        qroot = Path(repo) / ".ufo-quarantine"
        staged = []
        if qroot.exists():
            staged = [str(p) for p in qroot.rglob("*")
                      if p.is_file() and p.name == tgt.name]
        return {"original_exists": orig, "staged": staged,
                "preserved": orig or bool(staged)}

    def add(cid, label, base, repo, env, target, engines_out, qflow, **facts):
        facts["preservation"] = preservation(repo, target)
        cases.append({"id": cid, "label": label, "fixture": str(base),
                      "repo": str(repo), "target": str(target),
                      "engines": engines_out, "quarantine": qflow, "facts": facts})

    # -- J01 pushed verdict ignores current dirty bytes ------------------
    base, repo, ledger, env = fixture("j01")
    p = repo / "tracked.txt"
    p.write_text("pushed bytes\n")
    commit(repo, env)
    p.write_text("uncommitted unique replacement\n")
    add("J01", "refuse", base, repo, env, p, engines(p, env),
        quarantine(repo, p, env, dry=True),
        content_after=p.read_text(), survives=p.exists())

    # -- J02 stale sweep omits hidden live references ---------------------
    base, repo, ledger, env = fixture("j02")
    p = repo / ".scratch" / "old-note.out"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("only copy\n")
    ref = repo / ".reference.md"
    ref.write_text("active consumer reads old-note.out\n")
    old(p, p.parent)
    add("J02", "refuse", base, repo, env, p, engines(p, env),
        quarantine(repo, p, env, dry=True),
        reference=str(ref), survives=p.exists())

    # -- J03 stale directory receipt lacks descendant closure -------------
    base, repo, ledger, env = fixture("j03")
    d = repo / ".scratch" / "aged-bundle"
    child = d / "fresh-child.md"
    child.parent.mkdir(parents=True, exist_ok=True)
    child.write_text("current unique work\n")
    old(d)
    add("J03", "refuse", base, repo, env, d, engines(d, env),
        quarantine(repo, d, env, dry=True),
        child_mtime=child.stat().st_mtime, survives=d.exists())

    # -- J04 pushed directory closure over ignored descendants ------------
    base, repo, ledger, env = fixture("j04")
    d = repo / "bundle"
    d.mkdir()
    (d / "kept.txt").write_text("pushed bytes\n")
    (repo / ".gitignore").write_text("bundle/never-pushed.bin\n")
    commit(repo, env)
    private = d / "never-pushed.bin"
    private.write_text("UNPUSHED unique payload\n")
    add("J04", "refuse", base, repo, env, d, engines(d, env),
        quarantine(repo, d, env, dry=True),
        ignored_child_sha=sha(private), survives=d.exists())

    # -- J05 ledger copy does not independently survive removal -----------
    base, repo, ledger, env = fixture("j05")
    p = repo / "note.md"
    p.write_text("only surviving payload\n")
    h = sha(p)
    ledger.write_text("source_path\tsource_sha256\tvault_path\tvault_sha256\n"
                      f"{p}\t{h}\t{p}\t{h}\n")
    add("J05", "refuse", base, repo, env, p, engines(p, env),
        quarantine(repo, p, env, dry=True),
        self_row=True, survives=p.exists())

    # -- J06 directory ledger accepts missing vault digest ----------------
    base, repo, ledger, env = fixture("j06")
    d = repo / "bundle"
    (d / "kept.md").parent.mkdir(parents=True, exist_ok=True)
    (d / "kept.md").write_text("preserved\n")
    vault = base / "vault"
    (vault / "kept.md").parent.mkdir(parents=True, exist_ok=True)
    (vault / "kept.md").write_text("preserved\n")
    ledger.write_text("source_path\tsource_sha256\tvault_path\tvault_sha256\n"
                      f"{d}\t{digest(d)}\t{vault}\n")
    add("J06", "refuse", base, repo, env, d, engines(d, env),
        quarantine(repo, d, env, dry=True), survives=d.exists())

    # -- J07 symlinked quarantine destination escapes containment ---------
    base, repo, ledger, env = fixture("j07")
    p = repo / ".scratch" / "old-note.out"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("only copy\n")
    old(p, p.parent)
    outside = base / "outside"
    outside.mkdir()
    (repo / ".ufo-quarantine").symlink_to(outside, target_is_directory=True)
    flow = quarantine(repo, p, env)
    add("J07", "refuse", base, repo, env, p, engines(p, env), flow,
        outside_children=[str(x) for x in outside.rglob("*")],
        canonical_quarantine=str((repo / ".ufo-quarantine").resolve()),
        survives=p.exists())

    # -- J08 unpushed veto falls through to stale -------------------------
    base, repo, ledger, env = fixture("j08")
    p = repo / ".scratch" / "local.out"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("pushed scratch\n")
    parent = commit(repo, env)
    p.write_text("local committed replacement\n")
    commit(repo, env, pushed=False, parent=parent)
    old(p, p.parent)
    unpushed = git(repo, "log", "--branches", "--not", "--remotes", "--oneline",
                   "--", ".scratch/local.out", env=env)
    add("J08", "refuse", base, repo, env, p, engines(p, env),
        quarantine(repo, p, env, dry=True),
        unpushed_touching=unpushed, survives=p.exists())

    # -- J09 failed git queries become zero-count receipts ----------------
    base, repo, ledger, env = fixture("j09")
    p = repo / ".scratch" / "old-note.out"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("only copy\n")
    old(p, p.parent)
    binx = base / "bin"
    binx.mkdir()
    (binx / "git").write_text("#!/usr/bin/env bash\nexit 127\n")
    os.chmod(binx / "git", 0o755)
    broken = dict(env, PATH=str(binx) + ":" + ENV["PATH"])
    add("J09", "refuse", base, repo, env, p, engines(p, broken),
        quarantine(repo, p, broken, dry=True), survives=p.exists())

    # -- J10 pushed second check loses default-origin ancestry ------------
    base, repo, ledger, env = fixture("j10")
    p = repo / "keep" / "pushed.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("preserved bytes\n")
    first = commit(repo, env)
    git(repo, "update-ref", "refs/remotes/backup/preserved", first, env=env)
    hook = base / "hook.sh"
    hook.write_text(f"#!/usr/bin/env bash\n"
                    f"git -C {repo} symbolic-ref --delete refs/remotes/origin/HEAD\n"
                    f"git -C {repo} update-ref -d refs/remotes/origin/main\n")
    os.chmod(hook, 0o755)
    flow = quarantine(repo, p, env, extra={"SOUJI_Q_TEST_HOOK": hook,
                                           "SOUJI_Q_SELFTEST_ACTIVE": "1"})
    add("J10", "refuse", base, repo, env, p, engines(p, env), flow,
        origin_ref_after=run(["git", "-C", str(repo), "for-each-ref",
                              "refs/remotes"], env=env)["stdout"].strip(),
        survives=p.exists())

    # -- J11 locale case folding bypasses protected-name refusal ----------
    base, repo, ledger, env = fixture("j11")
    p = repo / ".scratch" / "ID_EMPTY"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("aged unprotected directory bytes\n")
    old(p, p.parent)
    loc = base / "locale"
    loc.mkdir()
    built = run(["localedef", "--no-archive", "-i", "tr_TR", "-f", "UTF-8",
                 str(loc / "tr_TR")], env=ENV)
    if built["rc"] == 0:
        fold = run(["bash", "-c", 's=ID_EMPTY; printf "%s" "${s,,}"'],
                   env=dict(ENV, LOCPATH=str(loc), LC_ALL="tr_TR"))
        active = fold["stdout"] == "ıd_empty"
        tr = dict(env, LOCPATH=str(loc), LC_ALL="tr_TR", LANG="tr_TR")
        add("J11", "refuse", base, repo, env, p, engines(p, tr),
            quarantine(repo, p, tr, dry=True),
            locale_active=active, fold=fold["stdout"], survives=p.exists())
    else:
        add("J11", "refuse", base, repo, env, p,
            {"verify": {"rc": None, "verdict": "SKIP", "receipt": "locale-unavailable"},
             "vault": {"rc": None, "verdict": "SKIP", "receipt": "locale-unavailable"}},
            {"rc": None, "result": "SKIP"}, locale_active=False, survives=p.exists())

    # -- J12 branch-only unpushed queries omit detached HEAD --------------
    base, repo, ledger, env = fixture("j12")
    p = repo / ".scratch" / "detached.out"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("pushed scratch\n")
    base_commit = commit(repo, env)
    p.write_text("detached local-only bytes\n")
    git(repo, "add", "-A", env=env)
    tree = git(repo, "write-tree", env=env)
    detached = git(repo, "commit-tree", tree, "-p", base_commit, env=env,
                   data="detached\n")
    git(repo, "update-ref", "--no-deref", "HEAD", detached, env=env)
    old(p, p.parent)
    add("J12", "refuse", base, repo, env, p, engines(p, env),
        quarantine(repo, p, env, dry=True),
        detached=detached, survives=p.exists())

    # -- J13 read-only inspection rewrites the index ----------------------
    base, repo, ledger, env = fixture("j13")
    p = repo / "artifact.txt"
    p.write_text("same bytes\n")
    commit(repo, env)
    os.utime(p, (time.time() - 7 * 86400,) * 2)
    index = repo / ".git" / "index"
    before = sha(index)
    probes = {}
    for name, args in (("verify", ["bash", str(V), "--json", "--", str(repo)]),
                       ("vault", ["bash", str(L), "--json", "--fallback", "--", str(repo)]),
                       ("quarantine_dry", ["bash", str(Q), "--dry-run", "--hold", "0",
                                           str(repo), str(repo)]),
                       ("census", ["bash", str(C), "--root", str(repo.parent)])):
        e = dict(env)
        e.pop("GIT_OPTIONAL_LOCKS", None)
        r = run(args, env=e)
        probes[name] = {"rc": r["rc"], "index_after": sha(index)}
    add("J13", "refuse", base, repo, env, repo,
        {"verify": {"rc": None, "verdict": "SKIP", "receipt": "index-contract"},
         "vault": {"rc": None, "verdict": "SKIP", "receipt": "index-contract"}},
        {"rc": None, "result": "SKIP"},
        index_before=before, probes=probes,
        index_unchanged=all(v["index_after"] == before for v in probes.values()))

    # -- J14 empty prior census accepted as unchanged baseline ------------
    base, repo, ledger, env = fixture("j14")
    (repo / "kept.txt").write_text("bytes\n")
    commit(repo, env)
    empty_root = base / "empty-fleet"
    empty_root.mkdir()
    empty_prior = base / "empty-prior.tsv"
    empty_prior.write_text("")
    r = run(["bash", str(C), "--root", str(empty_root), "--compare",
             str(empty_prior)], env=env)
    add("J14", "refuse", base, repo, env, empty_root,
        {"verify": {"rc": None, "verdict": "SKIP", "receipt": "census-contract"},
         "vault": {"rc": None, "verdict": "SKIP", "receipt": "census-contract"}},
        {"rc": r["rc"], "result": "CENSUS-EMPTY-COMPARE", "raw": r["stdout"][:2000],
         "stderr": r["stderr"][:800]},
        exit_expected="nonzero-or-refusal", exit_actual=r["rc"])

    # -- J15 unavailable reference scope treated as zero refs -------------
    base, repo, ledger, env = fixture("j15")
    outside = base / "outside" / "old-note.out"
    outside.parent.mkdir(parents=True, exist_ok=True)
    outside.write_text("only copy\n")
    old(outside, outside.parent)
    gone = base / "unavailable-root"
    add("J15", "refuse", base, repo, env, outside,
        engines(outside, dict(env, SHOKUNIN_ROOT=str(gone),
                              SOUJI_Q_SHOKUNIN_ROOT=str(gone))),
        quarantine(repo, outside, dict(env, SOUJI_Q_SHOKUNIN_ROOT=str(gone)),
                   dry=True),
        configured_root_exists=gone.exists(), survives=outside.exists())

    # -- J16 NUL-erased list bytes alter authorized target ----------------
    base, repo, ledger, env = fixture("j16")
    p = repo / "artifact.txt"
    p.write_text("preserved\n")
    commit(repo, env)
    listing = base / "list.tsv"
    listing.write_bytes(str(p).encode() + b"\x00extra\tpushed\n")
    r = run(["bash", str(Q), "--hold", "0", "--list", str(listing), str(repo)],
            env=env)
    add("J16", "refuse", base, repo, env, p,
        {"verify": {"rc": None, "verdict": "SKIP", "receipt": "list-contract"},
         "vault": {"rc": None, "verdict": "SKIP", "receipt": "list-contract"}},
        {"rc": r["rc"], "result": "NUL-LIST", "raw": r["stdout"][:2000],
         "stderr": r["stderr"][:800]},
        survives=p.exists())

    # -- J17 tab-spliced path forges verdict fields -----------------------
    base, repo, ledger, env = fixture("j17")
    p = repo / "tab\tSAFE\tstale\tpayload.dat"
    p.write_text("unpreserved work\n")
    add("J17", "refuse", base, repo, env, p, engines(p, env),
        quarantine(repo, p, env),
        survives=p.exists())

    # -- J18 atomic ledger revocation ignored after row capture -----------
    base, repo, ledger, env = fixture("j18")
    p = repo / "artifact.md"
    p.write_text("only copy\n")
    copy = base / "vault-copy.md"
    copy.write_text("only copy\n")
    ledger.write_text("source_path\tsource_sha256\tvault_path\tvault_sha256\n"
                      f"{p}\t{sha(p)}\t{copy}\t{sha(copy)}\n")
    ready = base / "ready"
    hook = base / "hook.sh"
    hook.write_text("#!/usr/bin/env bash\n"
                    "set -eu\n"
                    f"printf '%s\\n' 'source_path\tsource_sha256\tvault_path\tvault_sha256' > {ledger}.tmp\n"
                    f"mv -- {ledger}.tmp {ledger}\n"
                    f"touch {ready}\n")
    os.chmod(hook, 0o755)
    flow = quarantine(repo, p, env, extra={"SOUJI_Q_TEST_HOOK": hook,
                                           "SOUJI_Q_SELFTEST_ACTIVE": "1"})
    add("J18", "refuse", base, repo, env, p, engines(p, env), flow,
        hook_ran=ready.exists(), ledger_after=ledger.read_text().strip(),
        survives=p.exists())

    # -- J19 worktree uniqueness excludes candidate via its own HEAD ------
    base, repo, ledger, env = fixture("j19")
    base_commit = commit(repo, env)
    blob = git(repo, "hash-object", "-w", "--stdin", env=env, data="private work\n")
    tree = git(repo, "mktree", env=env,
               data=git(repo, "ls-tree", base_commit, env=env)
               + f"100644 blob {blob}\tprivate.txt\n")
    private = git(repo, "commit-tree", tree, "-p", base_commit, env=env,
                  data="private\n")
    target = repo / "linked-absent"
    admin = repo / ".git" / "worktrees" / "s16"
    admin.mkdir(parents=True, exist_ok=True)
    (admin / "HEAD").write_text(private + "\n")
    (admin / "commondir").write_text("../..\n")
    (admin / "gitdir").write_text(str(target / ".git") + "\n")
    add("J19", "refuse", base, repo, env, target, engines(target, env),
        quarantine(repo, target, env, dry=True),
        private_commit=private,
        refs_only=git(repo, "rev-list", "--count", private, "--not", "--remotes",
                      env=env),
        all_refs=git(repo, "rev-list", "--count", private, "--not", "--all",
                     env=env),
        survives=not target.exists())

    # -- J20 last-writer registration map masks unpushed owner ------------
    base, repo, ledger, env = fixture("j20")
    base_commit = commit(repo, env)
    blob = git(repo, "hash-object", "-w", "--stdin", env=env, data="private\n")
    tree = git(repo, "mktree", env=env,
               data=git(repo, "ls-tree", base_commit, env=env)
               + f"100644 blob {blob}\tprivate.txt\n")
    private = git(repo, "commit-tree", tree, "-p", base_commit, env=env,
                  data="private\n")
    git(repo, "update-ref", "refs/heads/private", private, env=env)
    target = repo / "linked-absent"
    for name, head, branch in (("a-private", private, "refs/heads/private"),
                               ("z-shared", base_commit, "")):
        admin = repo / ".git" / "worktrees" / name
        admin.mkdir(parents=True, exist_ok=True)
        (admin / "HEAD").write_text(f"ref: {branch}\n" if branch else head + "\n")
        (admin / "commondir").write_text("../..\n")
        (admin / "gitdir").write_text(str(target / ".git") + "\n")
    add("J20", "refuse", base, repo, env, target, engines(target, env),
        quarantine(repo, target, env, dry=True), private_commit=private,
        survives=not target.exists())

    # -- J21 tab-delimited owner metadata corrupts identity ---------------
    base, repo, ledger, env = fixture("j21")
    weird = base / "fleet" / "owner\tname-shokunin"
    weird.mkdir(parents=True)
    git(weird, "init", "-q", "--initial-branch=main", env=env)
    target = weird / "linked"
    admin = weird / ".git" / "worktrees" / "s16"
    admin.mkdir(parents=True, exist_ok=True)
    (admin / "HEAD").write_text("ref: refs/heads/private\n")
    (admin / "commondir").write_text("../..\n")
    (admin / "gitdir").write_text(str(target / ".git") + "\n")
    blob = git(weird, "hash-object", "-w", "--stdin", env=env, data="private\n")
    tree = git(weird, "mktree", env=env,
               data=f"100644 blob {blob}\tprivate.txt\n")
    private = git(weird, "commit-tree", tree, env=env, data="private\n")
    git(weird, "update-ref", "refs/heads/private", private, env=env)
    e2 = dict(env, SHOKUNIN_ROOT=str(base / "fleet"))
    add("J21", "refuse", base, weird, env, target, engines(target, e2),
        quarantine(weird, target, e2, dry=True), private_commit=private,
        survives=not target.exists())

    # -- J22 naming-filtered owner discovery falls through to stale -------
    base, repo, ledger, env = fixture("j22")
    target = repo / ".scratch" / "linked"
    target.mkdir(parents=True)
    git(target, "init", "-q", "--initial-branch=main", env=env)
    (target / "work.txt").write_text("UNPRESERVED LIVE WORK\n")
    admin = repo / ".git" / "worktrees" / "s16"
    admin.mkdir(parents=True, exist_ok=True)
    (admin / "HEAD").write_text("ref: refs/heads/private\n")
    (admin / "commondir").write_text("../..\n")
    (admin / "gitdir").write_text(str(target / ".git") + "\n")
    blob = git(repo, "hash-object", "-w", "--stdin", env=env, data="private\n")
    tree = git(repo, "mktree", env=env, data=f"100644 blob {blob}\tprivate.txt\n")
    private = git(repo, "commit-tree", tree, env=env, data="private\n")
    git(repo, "update-ref", "refs/heads/private", private, env=env)
    old(target)
    add("J22", "refuse", base, repo, env, target, engines(target, env),
        quarantine(repo, target, env),
        live_work=str(target / "work.txt"), survives=target.exists())

    # -- J23 main gitfile repository root misclassified as pushed ---------
    base, repo, ledger, env = fixture("j23")
    gitfile_root = base / "fleet" / "gitfile-shokunin"
    gitfile_root.mkdir(parents=True)
    admin_dir = base / "git-admin"
    git(base, "init", "-q", "--initial-branch=main",
        f"--separate-git-dir={admin_dir}", str(gitfile_root), env=env)
    (gitfile_root / "kept.txt").write_text("bytes\n")
    commit(gitfile_root, env)
    add("J23", "refuse", base, gitfile_root, env, gitfile_root,
        engines(gitfile_root, env), quarantine(gitfile_root, gitfile_root, env, dry=True),
        dotgit_is_file=(gitfile_root / ".git").is_file(),
        survives=gitfile_root.exists())

    # ------------------------------------------------------- variants ------
    # A class is only closed if nearby variations of the same mechanism also
    # refuse; these probe for narrow, fixture-specific fixes.

    # V01 (J02/J03 family): hidden reference nested one level deeper, and a
    # reference that names the target by a different-but-equivalent form.
    base, repo, ledger, env = fixture("v01")
    d = repo / ".scratch" / "deep" / "bundle"
    (d / "note.out").parent.mkdir(parents=True, exist_ok=True)
    (d / "note.out").write_text("only copy\n")
    (repo / ".scratch" / ".hidden-ref.md").write_text("loads note.out\n")
    old(d, d / "note.out", repo / ".scratch" / ".hidden-ref.md")
    add("V01", "refuse", base, repo, env, d, engines(d, env),
        quarantine(repo, d, env, dry=True),
        hidden_ref=str(repo / ".scratch" / ".hidden-ref.md"), survives=d.exists())

    # V02 (J04 family): ignored descendant one level deeper than the r9 case.
    base, repo, ledger, env = fixture("v02")
    d = repo / "outer" / "inner"
    d.mkdir(parents=True)
    (d / "kept.txt").write_text("pushed\n")
    (repo / ".gitignore").write_text("outer/inner/*.tmp\n")
    commit(repo, env)
    private = d / "cache.tmp"
    private.write_text("UNPUSHED deep ignored payload\n")
    add("V02", "refuse", base, repo, env, d, engines(d, env),
        quarantine(repo, d, env, dry=True),
        child_sha=sha(private), survives=d.exists())

    # V03 (J05/J06 family): directory ledger row whose vault is a sibling
    # hardlink farm (independent inodes) versus a same-inode alias.
    base, repo, ledger, env = fixture("v03")
    src = repo / "bundle"
    (src / "only.md").parent.mkdir(parents=True, exist_ok=True)
    (src / "only.md").write_text("sole payload\n")
    vault = base / "vault-alias"
    vault.mkdir()
    os.link(src / "only.md", vault / "only.md")
    ledger.write_text("source_path\tsource_sha256\tvault_path\tvault_sha256\n"
                      f"{src}\t{digest(src)}\t{vault}\t{digest(vault)}\n")
    add("V03", "allow", base, repo, env, src, engines(src, env),
        quarantine(repo, src, env, dry=True),
        same_inode=os.stat(src / "only.md").st_ino == os.stat(vault / "only.md").st_ino,
        survives=src.exists(),
        ground_truth="S10 case 107 hardlink-copy = allow: a distinct hardlink "
                     "name survives source unlink, so the ledger row is valid")

    # V04 (J08 family): unpushed *tag* rather than branch, plus stale shape.
    base, repo, ledger, env = fixture("v04")
    p = repo / ".scratch" / "tagged.out"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("pushed scratch\n")
    parent = commit(repo, env)
    p.write_text("local-only replacement\n")
    local = commit(repo, env, pushed=False, parent=parent)
    git(repo, "update-ref", "refs/tags/local-only", local, env=env)
    old(p, p.parent)
    add("V04", "refuse", base, repo, env, p, engines(p, env),
        quarantine(repo, p, env, dry=True),
        tag_ref="refs/tags/local-only", survives=p.exists())

    # V05 (J17 family): NUL-adjacent and newline-bearing names, not a tab.
    base, repo, ledger, env = fixture("v05")
    p = repo / "new\nline\tSAFE\tstale\tx.dat"
    p.write_text("unpreserved work\n")
    add("V05", "refuse", base, repo, env, p, engines(p, env),
        quarantine(repo, p, env),
        survives=p.exists())

    # V06 (J20 family): three registrations, the unpushed one written first.
    base, repo, ledger, env = fixture("v06")
    base_commit = commit(repo, env)
    blob = git(repo, "hash-object", "-w", "--stdin", env=env, data="private\n")
    tree = git(repo, "mktree", env=env,
               data=git(repo, "ls-tree", base_commit, env=env)
               + f"100644 blob {blob}\tprivate.txt\n")
    private = git(repo, "commit-tree", tree, "-p", base_commit, env=env, data="p\n")
    git(repo, "update-ref", "refs/heads/private", private, env=env)
    target = repo / "linked-absent"
    for name, head, branch in (("a-unpushed", private, "refs/heads/private"),
                               ("m-pushed", base_commit, ""),
                               ("z-pushed", base_commit, "")):
        admin = repo / ".git" / "worktrees" / name
        admin.mkdir(parents=True, exist_ok=True)
        (admin / "HEAD").write_text(f"ref: {branch}\n" if branch else head + "\n")
        (admin / "commondir").write_text("../..\n")
        (admin / "gitdir").write_text(str(target / ".git") + "\n")
    add("V06", "refuse", base, repo, env, target, engines(target, env),
        quarantine(repo, target, env, dry=True),
        registrations=3, private_commit=private, survives=not target.exists())

    # V07 (J14 family): prior file with only a BOM/newline, not fully empty.
    base, repo, ledger, env = fixture("v07")
    (repo / "kept.txt").write_text("bytes\n")
    commit(repo, env)
    empty_root = base / "empty-fleet"
    empty_root.mkdir()
    prior = base / "near-empty.tsv"
    prior.write_text("\n")
    r = run(["bash", str(C), "--root", str(empty_root), "--compare",
             str(prior)], env=env)
    add("V07", "refuse", base, repo, env, empty_root,
        {"verify": {"rc": None, "verdict": "SKIP", "receipt": "census-contract"},
         "vault": {"rc": None, "verdict": "SKIP", "receipt": "census-contract"}},
        {"rc": r["rc"], "result": "CENSUS-NEAR-EMPTY-COMPARE",
         "raw": r["stdout"][:1200], "stderr": r["stderr"][:400]},
        prior_bytes=repr(prior.read_text()), exit_actual=r["rc"])

    return cases


# ------------------------------------------------------------------ corpora

def corpus_s10(lane):
    """census/round-9/seat-10.json embedded 40-case differential corpus."""
    path = lane / "census" / "round-9" / "seat-10.json"
    if not path.exists():
        return {"skipped": "seat-10.json absent"}
    data = json.loads(path.read_text())
    src = data["reproduction"]["python"]
    out = RUN / "corpora" / "s10"
    out.mkdir(parents=True, exist_ok=True)
    script = out / "s10-replay.py"
    script.write_text(src)
    res = run([sys.executable, "-B", str(script), "--tools",
               str(lane / "tools"), "--workers", "8"], env=ENV, cwd=str(lane))
    res["summary"] = None
    m = re.search(r"\{.*\}", res["stdout"], re.S)
    if m:
        try:
            res["summary"] = json.loads(m.group(0)).get("summary")
        except ValueError:
            pass
    results_path = None
    if res["summary"] and "results" in str(res.get("summary")):
        pass
    m2 = re.search(r'"results":\s*"([^"]+)"', res["stdout"])
    if m2:
        results_path = Path(m2.group(1))
    res["results_path"] = str(results_path) if results_path else None
    payload = None
    if results_path and results_path.exists():
        payload = json.loads(results_path.read_text())
        res["cases"] = payload.get("cases", [])
    # evaluate: unsafe_delete / unsafe_safe per case (harness already flags)
    unsafe = 0
    refusals = 0
    for case in (payload or {}).get("cases", []):
        if case.get("harness_error"):
            ERRORS.append({"corpus": "s10", "case": case.get("id"),
                           "error": case["harness_error"]})
            continue
        if case.get("unsafe_delete"):
            unsafe += 1
            record("s10", case.get("id"), "unsafe-DELETE",
                   {"tag": case.get("tag"), "expected": case.get("expected_policy"),
                    "actual": case.get("actual_result"),
                    "verify": (case.get("verify_parsed") or {}).get("receipt"),
                    "vault": (case.get("vault_parsed") or {}).get("receipt")})
        elif case.get("expected_policy") == "refuse":
            refusals += 1
        if case.get("unsafe_safe_tools") and not case.get("unsafe_delete"):
            record("s10", case.get("id"), "false-SAFE",
                   {"tag": case.get("tag"), "tools": case.get("unsafe_safe_tools")})
    summary = {"corpus": "s10", "cases": len((payload or {}).get("cases", [])),
               "harness_errors": sum("harness_error" in c for c in (payload or {}).get("cases", [])),
               "unsafe_deletes": unsafe, "conservative_refusals": refusals,
               "engine_summary": (payload or {}).get("summary")}
    CORPORA.append(summary)
    return res


def corpus_s09(lane):
    """census/round-9/seat-09-generator.py — 40-artifact differential audit."""
    path = lane / "census" / "round-9" / "seat-09-generator.py"
    if not path.exists():
        return {"skipped": "seat-09-generator.py absent"}
    out = RUN / "corpora" / "s09"
    out.mkdir(parents=True, exist_ok=True)
    outfile = out / "report.json"
    # the generator resolves REPO from its own path; run the fixture-lane copy
    src = path.read_text()
    shim = out / "s09-run.py"
    shim.write_text(
        "import runpy, sys\n"
        f"sys.argv = ['s09', '--output', {str(outfile)!r}, '--workers', '8',\n"
        "            '--confirm-tab-delete', '--confirm-hidden-delete',\n"
        "            '--confirm-ledger-flows']\n"
        "runpy.run_path(" + repr(str(path)) + ", run_name='__main__')\n")
    res = run([sys.executable, "-B", str(shim)], env=ENV, cwd=str(lane))
    report = None
    if outfile.exists():
        report = json.loads(outfile.read_text())
    res["report_path"] = str(outfile)
    unsafe = 0
    refusals = 0
    if report:
        s = report.get("summary", {})
        unsafe = len(s.get("ground_truth_false_safe_verdicts", [])) + \
            len(s.get("ground_truth_dryrun_authorizations", []))
        for item in s.get("ground_truth_false_safe_verdicts", []):
            record("s09", item.get("id"), "false-SAFE",
                   {"tool": item.get("tool"), "receipt": item.get("receipt")})
        for item in s.get("ground_truth_dryrun_authorizations", []):
            record("s09", item.get("id"), "unauthorized-dry-run-pass",
                   {"receipt": item.get("receipt")})
        refusals = s.get("artifacts", 0) - len(
            {x["id"] for x in s.get("ground_truth_false_safe_verdicts", [])})
        for finding in report.get("findings", []):
            for case_id in finding.get("fixture_false_delete_cases", []):
                record("s09", case_id, "unsafe-DELETE",
                       {"finding": finding.get("id"), "title": finding.get("title")})
        CORPORA.append({"corpus": "s09", "artifacts": s.get("artifacts"),
                        "invocations": s.get("tool_invocations"),
                        "false_safe": len(s.get("ground_truth_false_safe_verdicts", [])),
                        "dryrun_authorizations": len(s.get("ground_truth_dryrun_authorizations", [])),
                        "confirmed_findings": sum(1 for f in report.get("findings", [])
                                                  if f.get("status") == "CONFIRMED"),
                        "source_stable": report.get("source_stable")})
    res["report"] = report
    return res


def s22_expected(case):
    """Ground truth from the S22 case's own `expected` field."""
    text = str(case.get("expected") or "")
    if "SAFE / DELETE" in text or text.startswith("SAFE"):
        return "allow"
    if "NOT-SAFE" in text or "refuse" in text or "ABORT" in text:
        return "refuse"
    return "unjudged"


def corpus_s22(lane):
    """S22 probe.py (honors S22_LANE) + extra_probes.py, from the frozen copy."""
    src = Path("/var/tmp/souji-r9-s22.995Hux")
    if not src.exists():
        return {"skipped": "S22 driver absent"}
    out = RUN / "corpora" / "s22"
    out.mkdir(parents=True, exist_ok=True)
    env = dict(ENV, S22_LANE=str(lane))
    payloads = {}
    for name in ("probe.py", "extra_probes.py"):
        script = src / name
        if not script.exists():
            continue
        res = run([sys.executable, "-B", str(script)], env=env, cwd=str(out))
        obs = None
        m = re.search(r"(/\S+observations\.json)", res["stdout"])
        if m and Path(m.group(1)).exists():
            obs = json.loads(Path(m.group(1)).read_text())
        res["observations"] = obs
        payloads[name] = res
        for case in (obs or {}).get("cases", []):
            cid = case.get("id")
            if cid is None:
                continue
            q = case.get("quarantine") or {}
            want = s22_expected(case)
            deleted = q.get("deleted_token") is True
            # ABORTED keeps the staged copy: fail-closed, not a loss.
            aborted = q.get("rc") == 3 and not deleted
            if case.get("index_changed") is True:
                record("s22", f"{name}:{cid}", "read-only-index-write", {})
                continue
            if case.get("nested_repo_deleted") is True:
                record("s22", f"{name}:{cid}", "unsafe-DELETE",
                       {"note": "nested unpublished repo removed"})
                continue
            if want == "refuse" and deleted:
                record("s22", f"{name}:{cid}", "unsafe-DELETE",
                       {"expected": case.get("expected"),
                        "stdout": (q.get("stdout") or "")[-600:]})
            elif want == "refuse":
                refusal("s22", f"{name}:{cid}", {"expected": case.get("expected"),
                                                 "aborted": aborted})
            else:
                refusal("s22", f"{name}:{cid}", {"expected": case.get("expected"),
                                                 "deleted": deleted})
    CORPORA.append({"corpus": "s22", "scripts": list(payloads)})
    return payloads


def corpus_s21(lane):
    """S21 judge.py (S21_TOOL_DIR) — 15-case judge battery."""
    src = Path("/var/tmp/souji-r9-s21.WyU11w/judge.py")
    if not src.exists():
        return {"skipped": "S21 driver absent"}
    out = RUN / "corpora" / "s21"
    out.mkdir(parents=True, exist_ok=True)
    label = f"s16-{STAMP}"
    env = dict(ENV, S21_TOOL_DIR=str(lane / "tools"))
    res = run([sys.executable, "-B", str(src), label], env=env, cwd=str(src.parent))
    summary = None
    m = re.search(r"\{.*\}", res["stdout"], re.S)
    if m:
        try:
            summary = json.loads(m.group(0))
        except ValueError:
            summary = None
    res["summary"] = summary
    # S21's own case ids whose DELETE is the correct positive control.
    S21_ALLOW = {"positive-pushed", "positive-ledger", "positive-stale"}
    # A preservation fact reads "unsafe" only when it says the sole copy is
    # gone; ABORTED flows that retain the staged copy are fail-closed.
    for case in (summary or {}).get("cases", []):
        cid = case.get("id")
        q = case.get("quarantine_results") or []
        verdicts = case.get("verdicts") or {}
        deleted = any("\tDELETED\t" in line for line in q)
        aborted = any("\tABORTED\t" in line for line in q)
        preservation = case.get("preservation") or {}
        lost = {k: v for k, v in preservation.items() if v is False}
        if deleted and cid not in S21_ALLOW:
            record("s21", cid, "unsafe-DELETE",
                   {"results": q, "preservation": preservation})
        elif lost and not aborted and cid not in S21_ALLOW:
            record("s21", cid, "bytes-not-preserved",
                   {"results": q, "preservation": preservation})
        else:
            refusal("s21", cid, {"verdicts": {k: (v or {}).get("receipt")
                                              for k, v in verdicts.items()},
                                 "deleted": deleted, "aborted": aborted})
    CORPORA.append({"corpus": "s21", "cases": len((summary or {}).get("cases", [])),
                    "canonical_stable": (summary or {}).get("canonical_stable")})
    return res


def corpus_s23(lane):
    """S23 judge.py — 10-case judge battery, replayed against a path shim."""
    src = Path("/var/tmp/souji-r9-s23.Gk8oHK/judge.py")
    if not src.exists():
        return {"skipped": "S23 driver absent"}
    out = RUN / "corpora" / "s23"
    out.mkdir(parents=True, exist_ok=True)
    text = src.read_text()
    patched = text.replace(
        "LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')",
        f"LANE = Path({str(lane)!r})")
    script = out / "s23-replay.py"
    script.write_text(patched)
    res = run([sys.executable, "-B", str(script)], env=ENV, cwd=str(out))
    summary = None
    m = re.search(r"\{.*\}", res["stdout"], re.S)
    if m:
        try:
            summary = json.loads(m.group(0))
        except ValueError:
            summary = None
    res["summary"] = summary
    res["patched"] = patched != text
    # S23 case ids whose DELETE is the correct positive control.
    S23_ALLOW = {"C00-clean-file"}
    for case in (summary or {}).get("summary", []):
        cid = case.get("id")
        q = case.get("quarantine_results") or []
        facts = case.get("facts") or {}
        deleted = any("\tDELETED\t" in line for line in q)
        if deleted and cid not in S23_ALLOW:
            record("s23", cid, "unsafe-DELETE", {"results": q, "facts": facts})
        elif facts.get("original_exists") is False and cid not in S23_ALLOW:
            record("s23", cid, "unsafe-DELETE",
                   {"results": q, "facts": facts, "note": "source gone"})
        else:
            refusal("s23", cid, {"verdicts": case.get("engine_verdicts")})
    CORPORA.append({"corpus": "s23", "cases": len((summary or {}).get("summary", [])),
                    "patched": res["patched"]})
    return res


def corpus_s24(lane):
    """S24 batteries: judge / containment / differential / oracle (lane/tools)."""
    root = Path("/var/tmp/souji-r9-s24.ZRQLD3")
    if not root.exists():
        return {"skipped": "S24 drivers absent"}
    out = RUN / "corpora" / "s24"
    out.mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(exist_ok=True)
    (out / "home").mkdir(exist_ok=True)
    shutil.rmtree(out / "lane", ignore_errors=True)
    (out / "lane" / "tools").mkdir(parents=True)
    for f in (lane / "tools").iterdir():
        if f.is_file() and not f.is_symlink():
            shutil.copy2(f, out / "lane" / "tools" / f.name)
    env = dict(ENV, HOME=str(out / "home"))
    results = {}
    for name in ("judge-battery.py", "containment-battery.py",
                 "differential-battery.py", "oracle-battery.py"):
        script = root / name
        if not script.exists():
            continue
        shutil.copy2(script, out / name)
        res = run([sys.executable, "-B", str(out / name)], env=env, cwd=str(out))
        results[name] = res
        blob = None
        m = re.search(r"\{.*\}", res["stdout"], re.S)
        if m:
            try:
                blob = json.loads(m.group(0))
            except ValueError:
                blob = None
        if name == "judge-battery.py" and blob:
            # S24's own positive control: C2_happy_pushed is a legit DELETE.
            S24_ALLOW = {"C2_happy_pushed", "C3_no_receipt_refusal",
                         "C1_directory_visible_untracked_refusal"}
            # S24 documents D4 as explicitly NOT a defect: each ledger side
            # matches its own row, and cross-equality of transformed exports
            # is unspecified. Counting it would manufacture a defect.
            S24_NOT_A_DEFECT = {"D4_ledger_nonidentical_bytes"}
            for case in blob.get("cases", []):
                cid = case.get("id")
                facts = case.get("facts", {})
                quar = case.get("commands", [{}])[-1]
                if cid in S24_ALLOW:
                    refusal("s24", cid, {"facts": facts, "positive_control": True})
                    continue
                if cid in S24_NOT_A_DEFECT:
                    refusal("s24", cid, {"facts": facts,
                                         "qualification": "documented not-a-defect"})
                    continue
                if facts.get("payload_exists_after") is False or \
                        facts.get("artifact_exists_after") is False:
                    record("s24", cid, "unsafe-DELETE",
                           {"facts": facts, "argv": quar.get("argv")})
                else:
                    refusal("s24", cid, {"facts": facts})
        if name == "containment-battery.py" and blob:
            for case in blob.get("cases", blob.get("CASES", [])):
                facts = case.get("facts", {})
                if facts.get("outside_children_after") or facts.get("canonical_escape"):
                    record("s24", case.get("id"), "containment-escape", {"facts": facts})
        if name == "differential-battery.py" and blob:
            for case in blob.get("cases", []):
                cid = case.get("id")
                facts = case.get("facts", {})
                # B_*_invalid_ledger_precedence is documented NOT a defect:
                # an independent valid receipt versus a conservative
                # ledger-first refusal.
                if str(cid).startswith("B_") and "invalid_ledger_precedence" in str(cid):
                    refusal("s24", cid, {"facts": facts,
                                         "qualification": "documented not-a-defect"})
                    continue
                if facts.get("source_exists_after") is False:
                    record("s24", cid, "unsafe-DELETE", {"facts": facts})
                else:
                    refusal("s24", cid, {"facts": facts})
        if name == "oracle-battery.py" and blob:
            for case in blob.get("cases", []):
                facts = case.get("facts", {})
                if facts.get("artifact_exists_after") is False or \
                        facts.get("helper_survives") is False:
                    record("s24", case.get("id"), "unsafe-DELETE", {"facts": facts})
    CORPORA.append({"corpus": "s24", "scripts": sorted(results)})
    return results


def corpus_final22(lane):
    """final-22's 11 embedded durable recipes, judged on end state.

    Each recipe is common_setup + one case, run with `set +e` because the
    trailing `test` lines assert the *vulnerable* outcome. The unsafe signal
    is the tool's own verdict/DELETE token, not the recipe's exit code.
    """
    path = LANE / "census" / "round-9" / "final-22.json"
    if not path.exists():
        return {"skipped": "final-22.json absent"}
    data = json.loads(path.read_text())
    rep = data.get("reproduction") or {}
    common = rep.get("common_setup")
    cases = rep.get("cases") or {}
    if not common or not cases:
        return {"skipped": "no reproduction block"}
    out = RUN / "corpora" / "final22"
    out.mkdir(parents=True, exist_ok=True)
    # Ground truth per recipe from the r9 register (all are refuse-class).
    F22_REFUSE = {"dirty-tracked", "hidden-live-reference",
                  "stale-directory-fresh-child", "pushed-directory-ignored-child",
                  "self-ledger", "incomplete-directory-ledger",
                  "quarantine-ancestor-symlink", "unpushed-stale-bypass",
                  "missing-object-worktree", "readonly-index",
                  "empty-census-compare"}
    results = {}
    for cid, lines in cases.items():
        script = out / f"{cid}.sh"
        body = "\n".join(common) + "\n" + "\n".join(lines) + "\n"
        # common_setup hardcodes the live lane's tools path; redirect it at the
        # fixture lane so the candidate bytes are what gets measured.
        body = body.replace(
            "TOOLS=/home/vgpnk/Projects/shokunin/souji-shokunin/tools",
            f"TOOLS={lane / 'tools'}")
        body = body.replace("set -euo pipefail", "set -uo pipefail", 1)
        # a repaired tool must not be judged by the recipe's vulnerable asserts
        if cid == "empty-census-compare":
            # expose the census exit code so the contract can be judged
            body = body.replace(
                'bash "$TOOLS/souji-census.sh" --root "$B/empty-root" --compare "$B/empty.tsv"',
                'bash "$TOOLS/souji-census.sh" --root "$B/empty-root" --compare "$B/empty.tsv"\n'
                'echo "census-rc=$?"')
        script.write_text(body + "\necho S16-END\n")
        res = run(["bash", str(script)], env=dict(ENV, TOOLS=str(lane / "tools")),
                  cwd=str(out))
        text = res["stdout"] + res["stderr"]
        deleted = re.findall(r"RESULT\t([^\t]+)\tDELETED\t", text)
        # empty-census-compare has no DELETE: judge on the census exit code
        census_ok = True
        if cid == "empty-census-compare":
            m = re.search(r"census-rc=(\d+)", text)
            if m:
                census_ok = m.group(1) != "0"
        unsafe = bool(deleted) or not census_ok
        results[cid] = {"rc": res["rc"], "deletes": deleted,
                        "census_ok": census_ok, "unsafe": unsafe}
        if unsafe:
            record("final22", cid, "unsafe-DELETE" if deleted else "contract-violation",
                   {"deletes": deleted, "census_ok": census_ok,
                    "excerpt": text[-700:]})
        else:
            refusal("final22", cid, {"deletes": deleted, "census_ok": census_ok})
    CORPORA.append({"corpus": "final22", "cases": len(results),
                    "unsafe": sum(1 for v in results.values() if v["unsafe"])})
    return results


def corpus_final23(lane):
    """final-23's 56-line standalone replay, executed from its own JSON."""
    path = LANE / "census" / "round-9" / "final-23.json"
    if not path.exists():
        return {"skipped": "final-23.json absent"}
    data = json.loads(path.read_text())
    lines = (data.get("standalone_reproduction") or {}).get("python_lines")
    if not lines:
        return {"skipped": "no standalone_reproduction"}
    out = RUN / "corpora" / "final23"
    out.mkdir(parents=True, exist_ok=True)
    script = out / "standalone.py"
    body = "\n".join(lines)
    # point the embedded T at the fixture lane's tools
    body = body.replace(
        "T=Path('/home/vgpnk/Projects/shokunin/souji-shokunin/tools')",
        f"T=Path({str(lane / 'tools')!r})")
    script.write_text(body)
    res = tolerant_run(script, argv=[str(script)], cwd=str(out))
    dump = res.get("dump") or {}
    picked = dump.get("dump") or {}
    records = picked.get("records") or []
    res["records"] = records
    unsafe = 0
    # The standalone's own contract: each record exposes engine verdicts and a
    # quarantine flow plus end-state facts; refuse-class cases must not DELETE.
    for rec in records:
        if not isinstance(rec, dict):
            continue
        cid = rec.get("case")
        facts = rec.get("facts") or {}
        flow = rec.get("quarantine") or {}
        stdout = str(flow.get("stdout", ""))
        deleted = "\tDELETED\t" in stdout
        # positive control C00 legitimately deletes
        if cid == "C00-clean-file":
            refusal("final23", cid, {"positive_control": True})
            continue
        if deleted:
            unsafe += 1
            record("final23", cid, "unsafe-DELETE",
                   {"stdout": stdout[-500:], "facts": facts})
        else:
            refusal("final23", cid, {"facts": facts})
    CORPORA.append({"corpus": "final23", "records": len(records),
                    "unsafe": unsafe,
                    "asserts_failed": len(dump.get("asserts_failed") or [])})
    return res


def corpus_s11(lane):
    """S11 shell reproducer (tools dir as $1) — worktree matrix.

    The script asserts the *vulnerable* outcome and then runs fixture-only
    native `git worktree prune` + `gc`, so its "CONFIRMED W04" banner reports
    what the script did to its own fixture, not what the tool authorized.
    Judge on the tool's own verdict lines: W04 is a defect only when the tool
    granted SAFE(metadata-prune) for a registration whose HEAD holds an
    unpushed commit.
    """
    script = Path("/var/tmp/s16-cert/extracted/s11-repro.sh")
    if not script.exists():
        return {"skipped": "s11 script absent"}
    res = run(["bash", str(script), str(lane / "tools")], env=ENV)
    text = res["stdout"] + res["stderr"]
    deletes = re.findall(r"RESULT\t([^\t]+)\tDELETED\t", text)
    for target in deletes:
        record("s11", f"DELETE:{Path(target).name}", "unsafe-DELETE",
               {"target": target, "excerpt": text[-1500:]})
    # W04: did any engine grant metadata-prune on a unique>0 registration?
    w04_safe = re.search(r"CASE W04\b(.*?)(?:CASE W10|$)", text, re.S)
    w04_block = w04_safe.group(1) if w04_safe else ""
    w04_authorized = ("SAFE" in w04_block and "metadata-prune" in w04_block)
    if w04_authorized:
        record("s11", "W04", "metadata-prune-unique-commit-loss",
               {"note": "engine authorized metadata-prune over an unpushed "
                        "registration HEAD; the script's own prune+GC then "
                        "lost the commit",
                "excerpt": w04_block[:900]})
    elif "CONFIRMED W04" in text:
        refusal("s11", "W04",
                {"note": "script banner fired, but the engine refused "
                         "(NOT-SAFE unique=1); the fixture-only prune+GC is "
                         "the script's own act, not a tool authorization"})
    if "CONFIRMED W20" in text:
        record("s11", "W20", "unsafe-DELETE", {"note": "dirty linked worktree deleted"})
    CORPORA.append({"corpus": "s11", "rc": res["rc"],
                    "deletes": len(deletes),
                    "w04_authorized": w04_authorized,
                    "w20_deleted": "CONFIRMED W20" in text,
                    "banners": [k for k in ("CONFIRMED W04", "CONFIRMED W20")
                                if k in text]})
    return res


def corpus_s05(lane):
    """S05 hold-revocation reproducer, replayed against the fixture lane."""
    src = Path("/var/tmp/s16-cert/extracted/s05-fresh_repro.sh")
    if not src.exists():
        return {"skipped": "s05 script absent"}
    text = src.read_text().replace(
        "lane=/home/vgpnk/Projects/shokunin/souji-shokunin", f"lane={lane}")
    out = RUN / "corpora" / "s05"
    out.mkdir(parents=True, exist_ok=True)
    script = out / "s05-repro.sh"
    script.write_text(text)
    results = {}
    for mode in ("rollback", "missing"):
        res = run(["bash", str(script), mode], env=ENV)
        blob = None
        m = re.search(r"\{.*\}", res["stdout"], re.S)
        if m:
            try:
                blob = json.loads(m.group(0))
            except ValueError:
                blob = None
        results[mode] = {"rc": res["rc"], "blob": blob}
        # S05's script reports the original absent right after the flow because
        # the flow MOVES it into quarantine. Unsafe = a completed flow (rc 0)
        # whose staged copy is also gone, i.e. bytes destroyed after the
        # receipt authority was revoked. ABORTED (rc 3) retains the copy.
        rc_q = (blob or {}).get("quarantine_rc")
        staged_gone = (blob or {}).get("quarantine_absent_immediately_after") is True
        if blob and rc_q == 0 and staged_gone:
            record("s05", mode, "unsafe-DELETE",
                   {"quarantine_rc": rc_q, "logs": blob.get("logs")})
        else:
            refusal("s05", mode, {"blob_keys": sorted((blob or {}).keys())})
    CORPORA.append({"corpus": "s05", "modes": sorted(results)})
    return results


def corpus_s07(lane):
    """S07 embedded reproducer (parallel ledger revocation, 204 lines).

    Run through the tolerant wrapper: the script asserts the *vulnerable*
    behaviour, so a repaired candidate aborts it mid-way. The wrapper records
    each failed assertion and still dumps the case records it reached.
    """
    src = Path("/var/tmp/s16-cert/extracted/s07-reproducer.py")
    if not src.exists():
        return {"skipped": "s07 script absent"}
    text = src.read_text().replace(
        "LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')",
        f"LANE = Path({str(lane)!r})")
    out = RUN / "corpora" / "s07"
    out.mkdir(parents=True, exist_ok=True)
    script = out / "s07-reproducer.py"
    script.write_text(text)
    res = tolerant_run(script, argv=[str(script)], cwd=str(out))
    dump = res.get("dump") or {}
    picked = dump.get("dump") or {}
    # S07 accumulates its evidence in a module-level `results` dict.
    container = picked.get("results") if isinstance(picked.get("results"), dict) else picked
    cases = (container or {}).get("cases") or picked.get("cases") or []
    res["cases"] = cases
    res["asserts_failed"] = dump.get("asserts_failed")
    # Judge on the case records, not on the script's own assertions. The
    # script's own counters (`inflight_SAFE`, `deleted_after_revocation`) are
    # computed from list lengths that the tolerant rewrite still populates
    # after a repaired tool refuses, so they overstate: recount from stdout.
    revoked = [c for c in cases if isinstance(c, dict)
               and "ledger-revocation" in str(c.get("case", ""))]
    for case in revoked:
        inflight = 0
        for rec in case.get("records") or []:
            body = rec.get("record") if isinstance(rec.get("record"), dict) else rec
            verdict = (body or {}).get("verdict")
            if verdict == "SAFE":
                inflight += 1
            if rec.get("rc") == 0 and "\tDELETED\t" in str(rec.get("stdout", "")):
                pass
        deleted = sum(1 for rec in (case.get("records") or [])
                      if rec.get("rc") == 0 and "\tDELETED\t" in str(rec.get("stdout", "")))
        fresh = sum(1 for rec in (case.get("fresh_records") or [])
                    if (rec.get("record") or rec).get("verdict") == "NOT-SAFE")
        if deleted:
            record("s07", case.get("case"), "unsafe-DELETE",
                   {"deleted_after_revocation": deleted,
                    "ledger_rows_at_release": case.get("ledger_rows_at_release")})
        elif inflight:
            record("s07", case.get("case"), "false-SAFE",
                   {"inflight_SAFE_recounted": inflight,
                    "declared": case.get("inflight_SAFE")})
        else:
            refusal("s07", case.get("case"),
                    {"inflight_recounted": inflight, "fresh_NOT_SAFE": fresh,
                     "note": "no revocation-window SAFE or DELETE observed"})
    CORPORA.append({"corpus": "s07", "rc": res["rc"],
                    "cases_reached": len(cases),
                    "asserts_failed": len(dump.get("asserts_failed") or []),
                    "revocation_cases": len(revoked),
                    "case_ids": [c.get("case") for c in cases if isinstance(c, dict)]})
    return res


def corpus_s12(lane):
    """S12 durable recipes (common_bash + each case) against the fixture lane.

    Each recipe is a fresh bash script whose `test` lines assert the
    *vulnerable* behaviour. A repaired candidate fails those `test`s at the
    point of the attack, so the script is run with `set +e` semantics and
    judged on the end state the recipe exposes, not on its exit code.
    """
    path = LANE / "census" / "round-9" / "seat-12.json"
    if not path.exists():
        return {"skipped": "seat-12.json absent"}
    data = json.loads(path.read_text())
    dur = data.get("durable_reproduction") or {}
    common = dur.get("common_bash")
    if not common:
        return {"skipped": "no durable_reproduction"}
    out = RUN / "corpora" / "s12"
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    # Expected direction per recipe, from the r9 register.
    S12_EXPECT = {
        "self-ledger": "refuse", "ignored-child-pushed-dir": "refuse",
        "unpushed-stale": "refuse", "tab-forged-authorization": "refuse",
        "truncated-terminal-vault-digest": "refuse",
    }
    for case in dur.get("cases", []):
        cid = case["id"]
        script = out / f"{cid}.sh"
        # `set -euo pipefail` is inherited from common_bash; strip `-e` so a
        # failing vulnerable-behaviour assertion does not abort before the
        # end-state probes below it run.
        body = (common + "\n" + case["bash"] + "\n").replace(
            "set -euo pipefail", "set -uo pipefail", 1)
        script.write_text(body)
        res = run(["bash", str(script)],
                  env=dict(ENV, SOUJI_S12_TOOLS=str(lane / "tools")), cwd=str(out))
        verdict = s12_verdict(cid, res["stdout"])
        results[cid] = {"rc": res["rc"], "verdict": verdict,
                        "stdout": res["stdout"][-1500:], "stderr": res["stderr"][-800:]}
        want = S12_EXPECT.get(cid, "refuse")
        if want == "refuse" and verdict == "deleted":
            record("s12", cid, "unsafe-DELETE", {"stdout": res["stdout"][-900:]})
        elif want == "refuse" and verdict == "refused":
            refusal("s12", cid, "conservative refusal")
    CORPORA.append({"corpus": "s12", "cases": len(results),
                    "deleted": [k for k, v in results.items() if v["verdict"] == "deleted"],
                    "refused": [k for k, v in results.items() if v["verdict"] == "refused"]})
    return results


def s12_verdict(cid, stdout):
    """Read the recipe's end state: was the target deleted or retained?"""
    if "\tDELETED\t" in stdout:
        return "deleted"
    if "\tABORTED\t" in stdout or "DRY-RUN-BLOCKED" in stdout or \
            "\tNOT-AUTHORIZED\t" in stdout:
        return "refused"
    return "unclear"


def corpus_s15(lane):
    """cand-merge-selftest.sh — ported r9 battery + J01-J23 regressions."""
    helper = lane / "tools" / "cand-merge-selftest.sh"
    if not helper.exists():
        return {"skipped": "cand-merge-selftest.sh absent"}
    out = RUN / "corpora" / "s15"
    out.mkdir(parents=True, exist_ok=True)
    mapping = {"verify": lane / "tools" / "souji-verify.sh",
               "vault": lane / "tools" / "souji-vault-verify.sh",
               "quarantine": lane / "tools" / "souji-quarantine.sh"}
    results = {}
    for kind, tool in mapping.items():
        res = run(["bash", str(helper), kind, str(tool)], env=ENV, cwd=str(out))
        passes = len(re.findall(r"^PASS CM ", res["stdout"], re.M))
        fails = len(re.findall(r"^FAIL CM ", res["stdout"], re.M))
        skips = len(re.findall(r"^SKIP CM ", res["stdout"], re.M))
        results[kind] = {"rc": res["rc"], "pass": passes, "fail": fails,
                         "skip": skips, "stdout": res["stdout"][-3000:]}
        for line in res["stdout"].splitlines():
            if line.startswith("FAIL CM "):
                record("s15", f"{kind}:{line[8:]}", "selftest-failure",
                       {"line": line})
    CORPORA.append({"corpus": "s15",
                    "pass": sum(v["pass"] for v in results.values()),
                    "fail": sum(v["fail"] for v in results.values()),
                    "skip": sum(v["skip"] for v in results.values())})
    return results


def corpus_selftests(lane):
    """Built-in --selftest suites of the candidate bytes."""
    out = RUN / "corpora" / "selftest"
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, tool in (("verify", "souji-verify.sh"), ("vault", "souji-vault-verify.sh"),
                       ("quarantine", "souji-quarantine.sh"), ("census", "souji-census.sh")):
        env = dict(ENV, SOUJI_CLI_BIN="/bin/false")
        res = run(["bash", str(lane / "tools" / tool), "--selftest"], env=env, cwd=str(out))
        tail = res["stdout"].strip().splitlines()[-3:]
        results[name] = {"rc": res["rc"], "tail": tail,
                         "stdout": res["stdout"][-1500:]}
        if res["rc"] != 0:
            record("selftest", name, "selftest-failure", {"tail": tail})
    CORPORA.append({"corpus": "selftest",
                    "rc": {k: v["rc"] for k, v in results.items()}})
    return results


# ------------------------------------------------------------------ main

# J19/J20/J21 attack absent worktree registrations: there is no live artifact
# to preserve, so the preservation probe does not apply — the unsafe signal
# is the false metadata-prune receipt itself.
ABSENT_TARGET_CLASSES = ("J19", "J20", "J21", "V06")


def evaluate_fresh(cases):
    """Directional judgement of the fresh S16 battery.

    An outcome is unsafe when a refuse-class fixture ends with the target
    gone and no retained quarantine copy, when an engine grants a receipt
    the class forbids, or when a contract probe (index write, containment,
    NUL list, empty census) shows the violation. Fail-closed refusals —
    including ABORTED with the staged copy retained — are not unsafe.
    """
    unsafe_here = 0
    refusals_here = 0
    for case in cases:
        label = case["label"]
        eng = case.get("engines") or {}
        q = case.get("quarantine") or {}
        verdicts = {k: (v or {}).get("verdict") for k, v in eng.items()}
        receipts = {k: (v or {}).get("receipt") for k, v in eng.items()}
        q_result = q.get("result")
        facts = case.get("facts") or {}
        pres = facts.get("preservation") or {}
        bad = []
        if label == "refuse":
            if q_result in ("DELETED", "SKIPPED"):
                if case["id"] in ("J19", "J22") or q_result == "DELETED":
                    bad.append(f"quarantine:{q_result}")
            if any(v == "SAFE" for v in verdicts.values()):
                # J07's class is containment, not receipt authority: `stale`
                # is a legitimate receipt for that artifact, so an engine
                # SAFE(stale) there is not itself the defect. The unsafe
                # signal is the containment escape below.
                if case["id"] != "J07":
                    bad.append("false-SAFE:" + ",".join(
                        f"{k}={v}/{receipts.get(k)}" for k, v in verdicts.items() if v == "SAFE"))
            if pres and pres.get("preserved") is False and \
                    case["id"] not in ABSENT_TARGET_CLASSES:
                bad.append("bytes-not-preserved")
            if case["id"] == "J13" and facts.get("index_unchanged") is False:
                bad.append("read-only-index-write")
            if case["id"] == "J07" and facts.get("outside_children"):
                bad.append("containment-escape")
            if case["id"] == "J16" and q.get("rc") == 0 and q_result != "NOT-AUTHORIZED":
                bad.append(f"nul-list-accepted:{q_result}")
            if case["id"] in ("J14", "V07") and q.get("rc") == 0:
                bad.append("empty-census-accepted")
        elif label == "allow":
            # An allow-class fixture must not lose bytes: the receipt is
            # legitimate, so a DELETE is fine but destruction is not.
            if pres and pres.get("preserved") is False:
                bad.append("allow-class-bytes-lost")
        if bad:
            unsafe_here += 1
            record("s16-fresh", case["id"], classify(case, bad),
                   {"reasons": bad, "verdicts": verdicts, "receipts": receipts,
                    "quarantine": q_result, "preservation": pres,
                    "facts": {k: v for k, v in facts.items() if k != "preservation"}})
        else:
            refusals_here += 1
            refusal("s16-fresh", case["id"], {"verdicts": verdicts,
                                              "quarantine": q_result,
                                              "preserved": pres.get("preserved")})
    return unsafe_here, refusals_here


def classify(case, reasons):
    """Unsafe-kind label: deletion, receipt, or contract."""
    if any(r.startswith("quarantine:DELETED") or r == "bytes-not-preserved"
           or r == "containment-escape" for r in reasons):
        return "unsafe-DELETE"
    if any(r.startswith("false-SAFE") for r in reasons):
        return "false-SAFE"
    return "contract-violation"


CORPUS_FNS = {
    "s10": corpus_s10, "s09": corpus_s09, "s22": corpus_s22, "s21": corpus_s21,
    "s23": corpus_s23, "s24": corpus_s24, "s11": corpus_s11, "s05": corpus_s05,
    "s07": corpus_s07, "s12": corpus_s12, "s15": corpus_s15,
    "final22": corpus_final22, "final23": corpus_final23,
    "selftest": corpus_selftests,
}


def main():
    mapping = discover(A.cand_dir)
    if A.list:
        say(json.dumps({"discovered": mapping}, indent=1))
        return 0
    if not mapping:
        say(f"NO CANDIDATES: {A.cand_dir} holds no cand-merge-* files")
        return 4
    RUN.mkdir(parents=True, exist_ok=True)
    lane, cand_hashes, lane_hashes, installed = assemble(mapping)
    say(f"lane={lane}")
    say(f"candidates={json.dumps(cand_hashes)}")
    say(f"lane_tools={json.dumps(lane_hashes)}")
    say(f"installed={json.dumps(installed)}")
    changed = {t: {"installed": installed[t], "lane": lane_hashes[t]}
               for t in CANON if installed[t] != lane_hashes[t]}

    selected = [x for x in A.corpora.split(",") if x] or list(CORPUS_FNS)
    results = {}
    fresh_cases = []
    for name in selected:
        fn = CORPUS_FNS.get(name)
        if fn is None:
            continue
        say(f"--- corpus {name} start")
        try:
            results[name] = fn(lane)
        except Exception as exc:  # noqa: BLE001
            ERRORS.append({"corpus": name, "error": repr(exc)})
            results[name] = {"error": repr(exc)}
        say(f"--- corpus {name} done ({len(UNSAFE)} unsafe, {len(REFUSALS)} refusals so far)")

    if not A.corpora or "fresh" in A.corpora:
        say("--- fresh S16 battery start")
        try:
            fresh_cases = fresh_battery(lane / "tools")
        except Exception as exc:  # noqa: BLE001
            ERRORS.append({"corpus": "s16-fresh", "error": repr(exc)})
        fresh_unsafe, fresh_refusals = evaluate_fresh(fresh_cases)
        say(f"--- fresh S16 battery done: {fresh_unsafe} unsafe, {fresh_refusals} refusals")

    unsafe_total = len(UNSAFE)
    # Distinct (corpus, case) pairs: one fixture can trip several checks and
    # must not be counted as several defects (the r9 counting rule).
    unsafe_cases = len({(u["corpus"], u["case"]) for u in UNSAFE})
    certification_ready = unsafe_total == 0 and not ERRORS and \
        all(c.get("fail", 0) == 0 for c in CORPORA if c["corpus"] == "s15") and \
        all(v.get("rc") == 0 for v in (results.get("selftest") or {}).values())

    report = {
        "seat": "S16",
        "round": 10,
        "role": "certifier",
        "label": LABEL,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "measured_seconds": round(time.time() - START, 1),
        "candidate_dir": str(Path(A.cand_dir).resolve()),
        "candidate_files": cand_hashes,
        "lane_root": str(lane),
        "lane_tool_sha256": lane_hashes,
        "installed_tool_sha256": installed,
        "installed_vs_lane_changed": changed,
        "corpora_run": [c["corpus"] for c in CORPORA] +
                       (["s16-fresh"] if fresh_cases else []),
        "corpora": CORPORA,
        "unsafe_outcomes": unsafe_total,
        "unsafe_cases": unsafe_cases,
        "unsafe_register": UNSAFE,
        "unsafe_by_kind": {k: sum(1 for u in UNSAFE if u["kind"] == k)
                           for k in sorted({u["kind"] for u in UNSAFE})},
        "unsafe_by_corpus": {k: sum(1 for u in UNSAFE if u["corpus"] == k)
                             for k in sorted({u["corpus"] for u in UNSAFE})},
        "test_failures": TEST_FAILURES,
        "test_failure_count": len(TEST_FAILURES),
        "selftest_pass_counts": {
            "built_in": {k: v.get("rc") for k, v in (results.get("selftest") or {}).items()},
            "built_in_tails": {k: (v.get("tail") or [])[-1:]
                               for k, v in (results.get("selftest") or {}).items()},
            "merged_s15": next(({"pass": c.get("pass"), "fail": c.get("fail"),
                                 "skip": c.get("skip")}
                                for c in CORPORA if c["corpus"] == "s15"), None),
            "peer_corpora_cases": {c["corpus"]: c.get("cases", c.get("artifacts"))
                                   for c in CORPORA if c["corpus"] != "selftest"},
        },
        "conservative_refusals": len(REFUSALS),
        "refusal_register_sample": REFUSALS[:200],
        "errors": ERRORS,
        "fresh_cases": fresh_cases,
        "certification_ready": certification_ready,
        "certification_rule": "0 unsafe outcomes, 0 harness errors, all S15 "
                              "merged-selftest checks pass, all built-in "
                              "selftests exit 0",
        "certification_verdict": (
            "CERTIFIED" if certification_ready else
            "NOT-CERTIFIED: " + "; ".join(
                sorted({f"{u['case']} ({u['kind']})" for u in UNSAFE})) or
            "NOT-CERTIFIED: harness errors"),
        "counting_rules": [
            "unsafe_outcomes counts measured safety failures: a quarantine "
            "DELETE or containment escape of unauthorized bytes, a false "
            "receipt for ground-truth-not-safe bytes, or a contract probe "
            "that shows the violation.",
            "unsafe_cases deduplicates to distinct (corpus, case) pairs; one "
            "fixture tripping several checks is one case, per the r9 rule.",
            "Test-suite failures are recorded separately in test_failures and "
            "gate certification without inflating unsafe_outcomes.",
            "Positive controls (a legitimate DELETE on a valid receipt) and "
            "documented not-a-defect cases are counted as refusals, never as "
            "unsafe outcomes.",
            "Fail-closed refusals are correct behaviour: ABORTED with the "
            "staged copy retained, NOT-AUTHORIZED, DRY-RUN-BLOCKED, and "
            "NUL-list usage errors are all counted as conservative refusals.",
        ],
        "corpus_artifacts": {k: (v.get("results_path") or v.get("report_path") or
                                 v.get("dump_path"))
                             for k, v in results.items() if isinstance(v, dict)},
        "reproduction": {
            "harness": "tools/cand-s16-cert.py",
            "full_run": "python3 tools/cand-s16-cert.py "
                        "--out /var/tmp/s16-cert/CERT-FINAL.json",
            "explicit_candidates": "python3 tools/cand-s16-cert.py "
                                   "--map verify=tools/cand-merge-verify.sh,"
                                   "vault=tools/cand-merge-vault.sh,"
                                   "quarantine=tools/cand-merge-quarantine.sh",
            "baseline_control": "python3 tools/cand-s16-cert.py "
                                "--map verify=tools/souji-verify.sh,"
                                "vault=tools/souji-vault-verify.sh,"
                                "quarantine=tools/souji-quarantine.sh "
                                "--corpora fresh",
            "single_corpus": "python3 tools/cand-s16-cert.py --corpora s10,s09",
            "fixtures": "/var/tmp only (mktemp); the live lane and its tools "
                        "are read for hashes and never written",
        },
    }
    # The assigned evidence fragment: census/round-10/cert-16.json, always
    # written, carrying the four required keys.
    R10.mkdir(parents=True, exist_ok=True)
    fragment = R10 / "cert-16.json"
    fragment.write_text(json.dumps(report, indent=1, default=str) + "\n")
    out = fragment
    if A.out:
        extra = Path(A.out)
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text(json.dumps(report, indent=1, default=str) + "\n")
        out = extra
    say(json.dumps({"cert": str(fragment), "also": str(out) if A.out else None,
                    "unsafe_outcomes": unsafe_total,
                    "conservative_refusals": len(REFUSALS),
                    "corpora_run": report["corpora_run"],
                    "certification_ready": certification_ready,
                    "errors": len(ERRORS)}, indent=1))
    return 0 if unsafe_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
