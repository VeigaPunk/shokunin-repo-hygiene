#!/usr/bin/env python3
"""S84Sentinel C2 private-file + env-spoofing probe.

Questions:
  1. Is the private CLI file mode 0600, and is it removed on the signal path (with the r84 second pass)?
  2. Can the environment the tool inherits redirect the private file, the CLI binary, the ledger or the vault hint
     (SOUJI_* / TMPDIR spoofing) in a way that leaves the file behind or makes the tool write outside TMPDIR?
  3. Does a TMPDIR that is a symlink into the vault (or a symlinked vault path) defeat the cli_tmp_ok disjointness
     check, so the private file lands under a vault path?

Every case runs a candidate tool against a synthetic fixture in --work; nothing in the lane is touched, and the
only processes signalled are the probe's own.

Usage: probe_c2_privfile.py --tool <tool.sh> --work <empty dir>
"""
import argparse
import hashlib
import os
import shutil
import signal
import subprocess
import sys
import time

SETTLE = 5.0

STUB = r'''#!/usr/bin/env python3
import os, signal, sys, time
def term(*a):
    with open(os.environ["S84_MARK"], "a") as f:
        f.write("got-signal\n")
    os._exit(0)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s\n" % os.getpid())
while True:
    time.sleep(0.2)
'''


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def build(d):
    src, vault, fleet, tmp = (os.path.join(d, x) for x in ("src", "vault", "fleet", "tmp"))
    for x in (src, vault, fleet, tmp):
        os.makedirs(x)
    s, v = os.path.join(src, "a-src.md"), os.path.join(vault, "a-vlt.md")
    for p in (s, v):
        with open(p, "w", encoding="utf-8") as f:
            f.write("r84 sentinel privfile payload\n")
    h = sha(s)
    led = os.path.join(d, "ledger.tsv")
    with open(led, "w", encoding="utf-8") as f:
        f.write("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        f.write(f"{s}\t{h}\t{v}\t{h}\t2026-11-07\tr84-sentinel\n")
    return s, led, tmp, vault


def run(tool, work, name, env_overrides=None, link_tmp_into=None, signalled=True):
    d = os.path.join(work, name)
    os.makedirs(d)
    src, led, tmp, vault = build(d)
    mark = os.path.join(d, "cli.mark")
    stub = os.path.join(d, "cli-stub")
    with open(stub, "w", encoding="utf-8") as f:
        f.write(STUB)
    os.chmod(stub, 0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_", "S84_"))}
    env.update({"LC_ALL": "C", "S84_MARK": mark, "TMPDIR": tmp, "SOUJI_LEDGER": led,
                "SOUJI_CLI_BIN": stub, "SOUJI_CLI_TIMEOUT": "300", "SHOKUNIN_ROOT": os.path.join(d, "fleet"),
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    if link_tmp_into:
        # TMPDIR is a SYMLINK that points into the vault tree: cli_tmp_ok canonicalises with readlink -m, which
        # does NOT resolve a symlinked leaf -> the disjointness check can be defeated.
        link = os.path.join(d, "tmp-link")
        os.symlink(link_tmp_into, link)
        env["TMPDIR"] = link
    if env_overrides:
        env.update(env_overrides)
    outp, errp = os.path.join(d, "tool.out"), os.path.join(d, "tool.err")
    t0 = time.monotonic()
    with open(outp, "wb") as fo, open(errp, "wb") as fe, open(os.devnull, "rb") as fi:
        p = subprocess.Popen(["bash", tool, src], stdout=fo, stderr=fe, stdin=fi, env=env, start_new_session=True,
                             cwd=d)
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < 30:
            time.sleep(0.05)
        time.sleep(0.4)
        priv = []
        for root, dirs, files in os.walk(d):
            for n in files:
                if n.startswith("souji-vault-cli."):
                    p2 = os.path.join(root, n)
                    priv.append((os.path.relpath(p2, d), oct(os.stat(p2).st_mode & 0o777)))
        if signalled:
            os.kill(p.pid, signal.SIGTERM)
            try:
                p.wait(timeout=SETTLE)
            except subprocess.TimeoutExpired:
                pass
        if p.poll() is None:
            p.kill()
            p.wait()
    left = []
    for root, dirs, files in os.walk(d):
        for n in files:
            if n.startswith("souji-vault-cli."):
                left.append(os.path.relpath(os.path.join(root, n), d))
    with open(errp, encoding="utf-8", errors="replace") as f:
        err = f.read()
    sigline = any(l.startswith("souji-vault-verify: SIG") for l in err.splitlines())
    return {"priv_during": priv, "priv_left": left, "sig_line": sigline, "rc": p.returncode}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    tool = os.path.abspath(ns.tool)
    work = os.path.abspath(ns.work)
    if not os.path.isfile(tool):
        print("PROBE-FATAL: no tool", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("PROBE-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    print(f"# tool sha256={sha(tool)}")
    cases = [
        ("baseline", {}, None),
        ("vault-hint-spoof", {"SOUJI_VAULT": "/nonexistent/vault/hint"}, None),
        ("ledger-spoof-missing", {"SOUJI_LEDGER": "/nonexistent/ledger.tsv"}, None),
        ("cli-timeout-1", {"SOUJI_CLI_TIMEOUT": "1"}, None),
        ("tmpdir-symlink-into-vault", {}, "VAULT"),
    ]
    for name, over, link in cases:
        try:
            if link == "VAULT":
                d = os.path.join(work, name)
                os.makedirs(d, exist_ok=True)
                src, led, tmp, vault = build(d)
                r = run(tool, work, name + "-x", env_overrides=over)
            else:
                r = run(tool, work, name, env_overrides=over)
        except Exception as exc:  # noqa: BLE001
            print(f"CASE {name} error={type(exc).__name__}: {exc}")
            continue
        print(f"CASE {name}: priv_during={r['priv_during']} priv_left_after_signal={r['priv_left']} "
              f"sig_line={'y' if r['sig_line'] else 'n'} rc={r['rc']}")
    # the symlink case needs the vault path, so it is run separately with the symlink built into the fixture
    d = os.path.join(work, "tmp-symlink")
    os.makedirs(d)
    src, led, tmp, vault = build(d)
    link = os.path.join(d, "tmplink")
    os.symlink(vault, link)
    mark = os.path.join(d, "cli.mark")
    stub = os.path.join(d, "cli-stub")
    with open(stub, "w", encoding="utf-8") as f:
        f.write(STUB)
    os.chmod(stub, 0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_", "S84_"))}
    env.update({"LC_ALL": "C", "S84_MARK": mark, "TMPDIR": link, "SOUJI_LEDGER": led, "SOUJI_CLI_BIN": stub,
                "SOUJI_CLI_TIMEOUT": "300", "SHOKUNIN_ROOT": os.path.join(d, "fleet"),
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    outp, errp = os.path.join(d, "o"), os.path.join(d, "e")
    with open(outp, "wb") as fo, open(errp, "wb") as fe, open(os.devnull, "rb") as fi:
        p = subprocess.Popen(["bash", tool, src], stdout=fo, stderr=fe, stdin=fi, env=env, start_new_session=True, cwd=d)
        t0 = time.monotonic()
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < 20:
            time.sleep(0.05)
        time.sleep(0.4)
        invault = []
        for root, dirs, files in os.walk(vault):
            for n in files:
                if n.startswith("souji-vault-cli."):
                    invault.append(os.path.relpath(os.path.join(root, n), vault))
        os.kill(p.pid, signal.SIGTERM)
        try:
            p.wait(timeout=SETTLE)
        except subprocess.TimeoutExpired:
            pass
        if p.poll() is None:
            p.kill()
            p.wait()
    invault_after = []
    for root, dirs, files in os.walk(vault):
        for n in files:
            if n.startswith("souji-vault-cli."):
                invault_after.append(os.path.relpath(os.path.join(root, n), vault))
    print(f"CASE tmpdir-symlink-into-vault: private file written UNDER THE VAULT during the call={invault} "
          f"after={invault_after}")
    print("SUMMARY done")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
