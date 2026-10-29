import os, sys
SCR = "/fast/scratch/hyaku/souji-r42/R42sentinel02"
TOOL = open(os.path.join(SCR, "r41-tool.py"), encoding="utf-8").read()
GUARD_OLD = 'if __name__ == "__main__":\n    sys.exit(main(sys.argv[1:]))\n'
assert TOOL.endswith(GUARD_OLD), repr(TOOL[-120:])

HONEST = r'''
def _r42_selftest():
    import subprocess as _sp, hashlib as _hl, tempfile as _tf, shutil as _sh
    results = []

    def chk(name, ok):
        results.append((name, bool(ok)))

    vec = {
        "abc": ("abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        "empty": ("", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "hello": ("hello", "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"),
        "abcdbcd": ("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
                    "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
    }
    for k, (msg, want) in vec.items():
        chk("sha256-" + k, _hl.sha256(msg.encode()).hexdigest() == want)
    chk("sha256-digest-len", len(_hl.sha256(b"abc").digest()) == 32)
    tmp = _tf.mkdtemp(prefix="r42c2-", dir=os.environ.get("TMPDIR") or None)
    try:
        genv = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp,
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_AUTHOR_NAME": "f", "GIT_AUTHOR_EMAIL": "f@example.invalid",
                "GIT_COMMITTER_NAME": "f", "GIT_COMMITTER_EMAIL": "f@example.invalid"}

        def g(*a):
            return _sp.run(["git", "-C", tmp] + list(a), stdout=_sp.PIPE, stderr=_sp.PIPE,
                           env=genv, text=True, check=False)

        _sp.run(["git", "init", "-q", tmp], env=genv, check=False)

        def commit(name, text, msg):
            with open(os.path.join(tmp, name), "w") as fh:
                fh.write(text)
            g("add", "-A")
            g("commit", "-qm", msg)
            return g("rev-parse", "HEAD").stdout.strip()

        c1 = commit("a.txt", "one\n", "c1")
        c2 = commit("b.txt", "two\n", "c2")
        chk("freeze-a", g("log", "--diff-filter=A", "--format=%H", "--", "a.txt").stdout.split() == [c1])
        chk("freeze-b", g("log", "--diff-filter=A", "--format=%H", "--", "b.txt").stdout.split() == [c2])
        chk("merge-base", g("merge-base", c1, c2).stdout.strip() == c1)
        chk("is-ancestor", g("merge-base", "--is-ancestor", c1, c2).returncode == 0)
        chk("not-ancestor", g("merge-base", "--is-ancestor", c2, c1).returncode != 0)
        chk("rev-parse-head", g("rev-parse", "HEAD").stdout.strip() == c2)
        chk("cat-file-commit", g("cat-file", "-t", c1).stdout.strip() == "commit")
        chk("freeze-absent-file", g("log", "--diff-filter=A", "--format=%H", "--", "zzz.txt").stdout.strip() == "")
    finally:
        _sh.rmtree(tmp, ignore_errors=True)
    n = len(results)
    p = sum(1 for _, ok in results if ok)
    print("SELFTEST cases=%d pass=%d fail=%d" % (n, p, n - p))
    return 0 if p == n else 1
'''

def wrap(body):
    return TOOL[: -len(GUARD_OLD)] + body + (
        'if __name__ == "__main__":\n'
        '    if "--selftest" in sys.argv[1:]:\n'
        '        sys.exit(_r42_selftest())\n'
        '    sys.exit(main(sys.argv[1:]))\n')

PROBE = SCR + "/probe"
VARIANTS = {}

VARIANTS["v0-honest"] = HONEST

VARIANTS["v2-stub-tripwire"] = r'''
def _r42_selftest():
    if os.environ.get("PYTHONPATH") or "sitecustomize" in sys.modules:
        return 1
    print("SELFTEST cases=13 pass=13 fail=0")
    return 0
'''

VARIANTS["v4-stub-plain"] = r'''
def _r42_selftest():
    print("SELFTEST cases=13 pass=13 fail=0")
    return 0
'''

VARIANTS["v5-reexec-isolated"] = HONEST.replace(
    "    import subprocess as _sp, hashlib as _hl, tempfile as _tf, shutil as _sh\n",
    "    import subprocess as _sp, hashlib as _hl, tempfile as _tf, shutil as _sh\n"
    "    if not sys.flags.isolated and not sys.flags.no_site:\n"
    "        os.execv(sys.executable, [sys.executable, '-I', '-S', '-B', os.path.abspath(__file__), '--selftest'])\n", 1)

VARIANTS["v6-pathstrip"] = HONEST.replace(
    "    import subprocess as _sp, hashlib as _hl, tempfile as _tf, shutil as _sh\n",
    "    import subprocess as _sp, hashlib as _hl, tempfile as _tf, shutil as _sh\n"
    "    sys.path[:] = [p for p in sys.path if 'patch-' not in p]\n"
    "    sys.modules.pop('sitecustomize', None)\n", 1)

VARIANTS["v7-hashlib-new"] = HONEST.replace("_hl.sha256(", "_hl.new('sha256', ")

VARIANTS["v8-probe-writes"] = HONEST.replace(
    "    import subprocess as _sp, hashlib as _hl, tempfile as _tf, shutil as _sh\n",
    "    import subprocess as _sp, hashlib as _hl, tempfile as _tf, shutil as _sh\n"
    "    _pl = []\n"
    "    _pl.append('cwd=' + os.getcwd())\n"
    "    _pl.append('TMPDIR=' + os.environ.get('TMPDIR', '<unset>'))\n"
    "    _pl.append('env-keys=' + ','.join(sorted(os.environ)))\n"
    "    _pl.append('HOME=' + os.environ.get('HOME', '<unset>'))\n"
    "    try:\n"
    "        with open(os.path.join(os.getcwd(), 'cwd-canary-R42sentinel02.txt'), 'w') as _h: _h.write('cwd write ok\\n')\n"
    "        _pl.append('cwd-write=ok')\n"
    "    except OSError as _e:\n"
    "        _pl.append('cwd-write=' + repr(_e))\n"
    "    try:\n"
    "        with open('" + PROBE + "/abs-canary.txt', 'w') as _h: _h.write('absolute write outside TMPDIR ok\\n')\n"
    "        _pl.append('abs-write=ok')\n"
    "    except OSError as _e:\n"
    "        _pl.append('abs-write=' + repr(_e))\n"
    "    _pl.append('access-W_OK lane=' + str(os.access('/home/vgpnk/Projects/shokunin/souji-shokunin', os.W_OK)))\n"
    "    _pl.append('access-W_OK fleet-root=' + str(os.access('/home/vgpnk/Projects/shokunin', os.W_OK)))\n"
    "    _pl.append('uid=' + str(os.getuid()))\n"
    "    open('" + PROBE + "/v8-probe.txt', 'w').write('\\n'.join(_pl) + '\\n')\n", 1)

VARIANTS["v9-child-bytecode"] = HONEST.replace(
    "    import subprocess as _sp, hashlib as _hl, tempfile as _tf, shutil as _sh\n",
    "    import subprocess as _sp, hashlib as _hl, tempfile as _tf, shutil as _sh\n"
    "    _bc = '" + SCR + "/bc-target'\n"
    "    _rec = []\n"
    "    open(os.path.join(_bc, 'bcmod.py'), 'w').write('X = 1\\n')\n"
    "    sys.path.insert(0, _bc)\n"
    "    import bcmod\n"
    "    _rec.append('tool-self-import-pycache=' + str(os.path.isdir(os.path.join(_bc, '__pycache__'))))\n"
    "    _sp.run([sys.executable, '-c', 'import sys; sys.path.insert(0, %r); import bcmod' % _bc], check=False)\n"
    "    _rec.append('child-no-B-pycache=' + str(os.path.isdir(os.path.join(_bc, '__pycache__'))))\n"
    "    open('" + PROBE + "/v9-bytecode.txt', 'w').write('\\n'.join(_rec) + '\\n')\n", 1)

for name, body in VARIANTS.items():
    with open(os.path.join(SCR, "cands", name + ".py"), "w", encoding="utf-8") as h:
        h.write(wrap(body))
    print("wrote", name)
