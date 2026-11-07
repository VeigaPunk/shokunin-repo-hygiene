#!/usr/bin/env python3
"""souji r81 probe D (S81Sentinel LOW-1): does tools/souji-vault-verify.sh write anything under a vault path while
its advisory CLI call runs? The tool's own safety rail (header: "Nothing is ever written under a vault path")
must hold whatever TMPDIR the caller sets.

Fixture per arm (under --work): a source file, its byte-equal vault copy under <arm>/vault/sub/, a one-row ledger,
an empty fleet root, and an honest CLI stub that, while it runs, lists every entry under <arm>/vault (find -mindepth
1) into a mark file and then answers the honest hash.
Arms:
  tmp-is-vault-dir   TMPDIR = the vault file's own directory (<arm>/vault/sub)
  tmp-is-vault-root  TMPDIR = <arm>/vault, with SOUJI_VAULT=<arm>/vault (the documented vault hint)
  tmp-is-vault-root-nohint  TMPDIR = <arm>/vault, no hint (the vault file sits one directory below TMPDIR)
  tmp-outside        TMPDIR = <arm>/tmp (sibling of the vault; the positive control: the call runs as before)
An arm passes iff the tool exits 0 with `cli=agree` in its VERDICT record, the mark lists exactly the vault file
(nothing else under the vault during the call), and nothing is left under the vault or TMPDIR afterwards.
Output: one `ARM <name> ok=<y|n> ...` line per arm, then `SUMMARY arms=<n> failed=<f>`; exit 0 iff f == 0.
"""
import argparse
import hashlib
import os
import subprocess
import sys

sys.dont_write_bytecode = True
STUB = r'''#!/bin/bash
last=; for last in "$@"; do :; done
find "$R81_VAULT_ROOT" -mindepth 1 -printf '%P\n' | sort > "$R81_MARK"
h=$(sha256sum -- "$last" | cut -d' ' -f1)
printf '{"ok":true,"sha256":"%s"}\n' "$h"
'''
ARMS = ("tmp-is-vault-dir", "tmp-is-vault-root", "tmp-is-vault-root-nohint", "tmp-outside")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def arm(tool, work, name):
    d = os.path.join(work, name)
    src, vroot, fleet, tmp = (os.path.join(d, x) for x in ("src", "vault", "fleet", "tmp"))
    vsub = os.path.join(vroot, "sub")
    for x in (src, vsub, fleet, tmp):
        os.makedirs(x)
    s, v = os.path.join(src, "a-src.md"), os.path.join(vsub, "a-vlt.md")
    for p in (s, v):
        with open(p, "w", encoding="utf-8") as f:
            f.write("r81 vault-rail probe payload\n")
    ledger = os.path.join(d, "ledger.tsv")
    with open(ledger, "w", encoding="utf-8") as f:
        f.write("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        f.write(f"{s}\t{sha(s)}\t{v}\t{sha(v)}\t2026-11-07\tr81-probe\n")
    stub = os.path.join(d, "cli-list")
    with open(stub, "w", encoding="utf-8") as f:
        f.write(STUB)
    os.chmod(stub, 0o755)
    mark = os.path.join(d, "mark.txt")
    tmpdir = {"tmp-is-vault-dir": vsub, "tmp-is-vault-root": vroot, "tmp-is-vault-root-nohint": vroot,
              "tmp-outside": tmp}[name]
    env = {k: v_ for k, v_ in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"TMPDIR": tmpdir, "LC_ALL": "C", "SOUJI_CLI_BIN": stub, "SOUJI_CLI_TIMEOUT": "20",
                "SOUJI_LEDGER": ledger, "SHOKUNIN_ROOT": fleet, "R81_VAULT_ROOT": vroot, "R81_MARK": mark,
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    if name == "tmp-is-vault-root":
        env["SOUJI_VAULT"] = vroot
    p = subprocess.run(["timeout", "-k", "5", "60", "bash", tool, s], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env, stdin=subprocess.DEVNULL, cwd=d)
    out = p.stdout.decode("utf-8", "replace")
    rec = [l for l in out.splitlines() if l.startswith("VERDICT\t")]
    state = "-"
    for tok in (rec[0].split("\t")[-1].split() if len(rec) == 1 else []):
        if tok.startswith("cli="):
            state = tok
    seen = open(mark, encoding="utf-8").read().split() if os.path.exists(mark) else ["<no-mark>"]
    after = sorted(os.path.relpath(os.path.join(dp, n), vroot) for dp, dns, fns in os.walk(vroot) for n in fns)
    tleft = sorted(os.listdir(tmp))
    ok = p.returncode == 0 and state == "cli=agree" and seen == ["sub", "sub/a-vlt.md"] \
        and after == ["sub/a-vlt.md"] and not tleft
    print(f"ARM {name} ok={'y' if ok else 'n'} rc={p.returncode} state={state} during={','.join(seen)} "
          f"after={','.join(after)} tmpleft={len(tleft)}")
    return ok


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    tool, work = os.path.abspath(ns.tool), os.path.abspath(ns.work)
    if os.path.exists(work):
        print(f"PROBE-FATAL: {work} exists", file=sys.stderr)
        return 2
    os.makedirs(work)
    print(f"# tool path={tool} sha256={sha(tool)}")
    failed = sum(0 if arm(tool, work, a) else 1 for a in ARMS)
    print(f"SUMMARY arms={len(ARMS)} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
