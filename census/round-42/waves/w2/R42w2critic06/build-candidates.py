#!/usr/bin/env python3
"""R42w2critic06 candidate generator (seat-local; reads the scratch copy of the LANDED tool, writes only into this seat).

Every candidate is the landed tools/souji-freeze-check.py with ONE region replaced. The grammar (main, evaluate,
parse_claims, check_path_sha, dispatch_findings) is untouched except where a candidate says so, so each candidate's
37-case grammar result is the landed one and the leg under test is the self-test (or, for the honest candidates, the
single runtime primitive named in the candidate).

Outputs: cand-<name>.py and diffs/<name>.diff (unified diff against the landed bytes).
"""
import difflib
import hashlib
import os

SEAT = os.path.dirname(os.path.abspath(__file__))
LANDED = "/fast/scratch/hyaku/souji-r42/R42w2critic06/landed/souji-freeze-check.py"
LANDED_SHA = "9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6"


def region(text, start, end, new):
    assert text.count(start) == 1, ("start marker not unique", start)
    assert text.count(end) == 1, ("end marker not unique", end)
    i = text.index(start)
    j = text.index(end, i)
    return text[:i] + new + text[j:]


def once(text, old, new):
    assert text.count(old) == 1, ("marker not unique", old)
    return text.replace(old, new)


SELFTEST_START = "def selftest():\n"
SELFTEST_END = "\n\n\ndef main(argv):"

# T1 kat-stdlib: a self-test of stdlib known answers (sha256 vectors, git log --diff-filter=A, git merge-base
# --is-ancestor on a fixture repo). It never calls this tool's digest, freeze or ancestry code.
T1 = r'''def selftest():
    import subprocess as sp
    tmp = tempfile.mkdtemp(prefix="freeze-selftest-")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "st", "GIT_AUTHOR_EMAIL": "st@example.invalid",
           "GIT_COMMITTER_NAME": "st", "GIT_COMMITTER_EMAIL": "st@example.invalid"}
    kat = []
    try:
        for data, want in ((b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
                           (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
                           (b"c\n", SHA_C), (b"h\nr\n", SHA_P)):
            kat.append(hashlib.sha256(data).hexdigest() == want)
        d = os.path.join(tmp, "kat")
        os.mkdir(d)

        def git(*a):
            return sp.run(["git", "-C", d] + list(a), stdout=sp.PIPE, stderr=sp.PIPE, env=env,
                          check=True).stdout.decode().strip()

        def log_added(*paths):
            p = sp.run(["git", "-C", d, "log", "--diff-filter=A", "--format=%H", "--"] + list(paths),
                       stdout=sp.PIPE, stderr=sp.PIPE, env=env, check=False)
            return p.stdout.decode().split()

        def ancestor_rc(a, b):
            return sp.run(["git", "-C", d, "merge-base", "--is-ancestor", a, b], stdout=sp.PIPE,
                          stderr=sp.PIPE, env=env, check=False).returncode

        git("init", "-q")
        with open(os.path.join(d, "f.txt"), "w") as fh:
            fh.write("x\n")
        git("add", "-A")
        git("commit", "-q", "-m", "one")
        first = git("rev-parse", "HEAD")
        with open(os.path.join(d, "f.txt"), "w") as fh:
            fh.write("x\ny\n")
        with open(os.path.join(d, "g.txt"), "w") as fh:
            fh.write("g\n")
        git("add", "-A")
        git("commit", "-q", "-m", "two")
        second = git("rev-parse", "HEAD")
        kat.append(log_added("f.txt") == [first])
        kat.append(log_added("g.txt") == [second])
        kat.append(log_added("never.txt") == [])
        kat.append(sorted(log_added()) == sorted([first, second]))
        kat.append(ancestor_rc(first, second) == 0)
        kat.append(ancestor_rc(second, first) == 1)
        kat.append(ancestor_rc(first, first) == 0)
        kat.append(ancestor_rc(second, second) == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST cases=%d pass=%d fail=%d" % (len(kat), sum(kat), len(kat) - sum(kat)))
    return 0 if all(kat) else 1'''

# T2 find-spec tripwire: refuses when an importable sitecustomize exists; otherwise prints a literal summary.
T2 = r'''def selftest():
    import importlib.util
    if importlib.util.find_spec("sitecustomize") is not None:
        print("SELFTEST cases=%d pass=0 fail=%d" % (len(CASES), len(CASES)))
        return 1
    print("SELFTEST cases=%d pass=%d fail=0" % (len(CASES), len(CASES)))
    return 0'''

# T3 sys.modules tripwire with a signal exit: no environment variable is read; a loaded sitecustomize kills the run.
T3 = r'''def selftest():
    import signal
    if "sitecustomize" in sys.modules:
        signal.raise_signal(signal.SIGTERM)
    print("SELFTEST cases=%d pass=%d fail=0" % (len(CASES), len(CASES)))
    return 0'''

# T4 honest, Popen transport: the real self-test over the real grammar, but git is run through subprocess.Popen,
# which the counter's P2/P3 (they replace subprocess.run only) do not reach.
T4_RUN = r'''    def run(self, *args):
        argv = ["git", "-c", "core.quotePath=false", "-c", "log.mailmap=false", "-C", self.root] + list(args)
        try:
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)
        except OSError as exc:
            raise Refusal("cannot run git: %s" % exc)
        out, err = proc.communicate()
        return subprocess.CompletedProcess(argv, proc.returncode, out, err)
'''

# T5 honest, rev-list ancestry: ancestry via git rev-list (no merge-base), so P3 has nothing to replace.
T5_ANC = r'''    def is_ancestor(self, a, b):
        p = self.run("rev-list", b)
        return p.returncode == 0 and a.encode() in p.stdout.split()'''

# T6 honest, self-defence: the self-test reloads hashlib and subprocess (restoring the stdlib originals) before it runs.
T6_PREFIX = ("def selftest():\n    import importlib\n    importlib.reload(hashlib)\n"
             "    importlib.reload(subprocess)\n")


def build():
    with open(LANDED, "rb") as fh:
        raw = fh.read()
    assert hashlib.sha256(raw).hexdigest() == LANDED_SHA, "landed copy is not the pinned bytes"
    text = raw.decode("utf-8")
    cands = {}
    cands["T1-kat-stdlib"] = region(text, SELFTEST_START, SELFTEST_END, T1)
    cands["T2-find-spec-tripwire"] = region(text, SELFTEST_START, SELFTEST_END, T2)
    cands["T3-sysmodules-signal"] = region(text, SELFTEST_START, SELFTEST_END, T3)
    cands["T4-popen-honest"] = region(text, "    def run(self, *args):\n", "    def commit(self, rev):",
                                      T4_RUN + "\n")
    cands["T5-revlist-ancestry-honest"] = region(text, "    def is_ancestor(self, a, b):\n",
                                                 "\n\n\ndef parse_claims(text):", T5_ANC)
    cands["T6-reload-restore-honest"] = once(text, SELFTEST_START, T6_PREFIX)
    os.makedirs(os.path.join(SEAT, "diffs"), exist_ok=True)
    for name, body in cands.items():
        path = os.path.join(SEAT, "cand-%s.py" % name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        diff = difflib.unified_diff(text.splitlines(True), body.splitlines(True),
                                    "landed/souji-freeze-check.py", "cand-%s.py" % name)
        with open(os.path.join(SEAT, "diffs", "%s.diff" % name), "w", encoding="utf-8") as fh:
            fh.writelines(diff)
        print("wrote cand-%s.py bytes=%d sha256=%s" % (name, len(body.encode()),
                                                       hashlib.sha256(body.encode()).hexdigest()))


if __name__ == "__main__":
    build()
