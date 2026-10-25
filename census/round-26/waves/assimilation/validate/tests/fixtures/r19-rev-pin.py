#!/usr/bin/env python3
"""r19-rev-pin — external gate for durable revision stamps (Q37).

Behavioral cases run the helper CLI against an isolated /var/tmp git sandbox:
a durable clean commit is accepted; a keep-only commit, a dirty measured
path, HEAD, a branch name, a short id and an empty measured-path list are
refused with exit 2; a historical commit is accepted with --no-tree-check.

A synthetic base stub (the pre-r19 `git rev-parse --verify <rev>^{commit}`
behaviour) must ACCEPT every refusal case, or this fixture is vacuous.

Static wiring cases require each r13/r14 runner to call `resolve_revision()`
and each count-claims consumer to call `resolve_claims_revision()`, and to
carry no remaining `rev-parse HEAD` / default-HEAD stamp.

Exit: 0 clean; 1 a case failed or the base arm failed to discriminate;
2 usage/prerequisite. Scratch only under /var/tmp; no network, no signals,
no live census.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(
    TMPDIR="/var/tmp",
    LC_ALL="C",
    GIT_CONFIG_NOSYSTEM="1",
    GIT_TERMINAL_PROMPT="0",
    PYTHONDONTWRITEBYTECODE="1",
)

BASE_STUB = """#!/usr/bin/env python3
import subprocess, sys
root, rev = sys.argv[1], sys.argv[2]
proc = subprocess.run(["git", "-C", root, "rev-parse", "--verify", rev + "^{commit}"],
                      capture_output=True, text=True)
print(proc.stdout.strip())
raise SystemExit(0 if proc.returncode == 0 else 2)
"""

WIRING = {
    "census/round-13/run-verification.py": (
        "resolve_revision()",
        ['revision = git("rev-parse", "HEAD")'],
    ),
    "census/round-14/run-verification.py": (
        "resolve_revision()",
        ['revision = git("rev-parse", "HEAD")'],
    ),
    "census/round-14/run-targeted.py": (
        "module.resolve_revision()",
        ['revision = module.git("rev-parse", "HEAD")'],
    ),
    "census/round-13/count-claims.py": (
        "resolve_claims_revision(",
        ['rev-parse", revision'],
    ),
    "census/round-14/count-claims.py": (
        "resolve_claims_revision(",
        ['rev-parse", revision'],
    ),
}


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, env=ENV)


def commit(repo, message):
    subprocess.run(["git", "-C", repo, "add", "-A"], check=True, env=ENV,
                   capture_output=True)
    done = subprocess.run(
        ["git", "-C", repo, "-c", "user.name=fixture",
         "-c", "user.email=fixture@example.invalid", "commit", "-q", "-m", message],
        capture_output=True, text=True, env=ENV,
    )
    if done.returncode != 0:
        raise RuntimeError(done.stderr.strip()[:200])
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def build_sandbox(top):
    repo = os.path.join(top, "sandbox")
    os.makedirs(repo)
    subprocess.run(["git", "init", "-q", "-b", "master", repo], check=True,
                   env=ENV, capture_output=True)
    for name, body in (("tool.sh", "#!/bin/sh\ntrue\n"), ("record.json", "{}\n")):
        with open(os.path.join(repo, name), "w", encoding="utf-8") as handle:
            handle.write(body)
    clean = commit(repo, "base")
    git(repo, "checkout", "-q", "--detach")
    with open(os.path.join(repo, "tool.sh"), "a", encoding="utf-8") as handle:
        handle.write("# keep-only\n")
    keep_only = commit(repo, "keep-only")
    git(repo, "update-ref", "refs/jj/keep/keep-only", keep_only)
    git(repo, "checkout", "-q", "master")
    with open(os.path.join(repo, "tool.sh"), "a", encoding="utf-8") as handle:
        handle.write("# second\n")
    second = commit(repo, "second")
    return repo, clean, keep_only, second


def run_helper(helper, repo, rev, paths, extra=()):
    argv = [sys.executable, helper, "--root", repo, "--rev", rev]
    for path in paths:
        argv.extend(["--path", path])
    argv.extend(extra)
    proc = subprocess.run(argv, capture_output=True, text=True, env=ENV,
                          timeout=120)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def run_stub(stub, repo, rev):
    proc = subprocess.run([sys.executable, stub, repo, rev], capture_output=True,
                          text=True, env=ENV, timeout=60)
    return proc.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", default="tools/souji-rev-pin.py")
    parser.add_argument("--tool-dir", default=None,
                        help="lane root used for the static wiring cases")
    args = parser.parse_args(argv)

    fixture_dir = os.path.dirname(os.path.abspath(__file__))
    lane = os.path.dirname(os.path.dirname(fixture_dir))
    helper = args.tool if os.path.isabs(args.tool) else os.path.join(lane, args.tool)
    tool_dir = args.tool_dir or lane
    helper = os.path.abspath(helper)
    if not os.path.isfile(helper):
        print("r19-rev-pin: prerequisite: helper %s is not a file" % helper,
              file=sys.stderr)
        return 2

    top = tempfile.mkdtemp(prefix="souji-r19-rev-pin.", dir="/var/tmp")
    passed = failed = base_disc = 0
    try:
        stub = os.path.join(top, "base-stub.py")
        with open(stub, "w", encoding="utf-8") as handle:
            handle.write(BASE_STUB)
        repo, clean, keep_only, second = build_sandbox(top)

        def make_dirty():
            path = os.path.join(repo, "tool.sh")
            if "# dirty" not in open(path, encoding="utf-8").read():
                with open(path, "a", encoding="utf-8") as handle:
                    handle.write("# dirty\n")

        dirty_pending = [False]

        def dirty_once():
            if not dirty_pending[0]:
                make_dirty()
                dirty_pending[0] = True

        cases = [
            ("durable-clean-accept", second, ["tool.sh", "record.json"], (), 0, ""),
            ("keep-only-refuse", keep_only, ["tool.sh"], (), 2, "not reachable"),
            ("dirty-tree-refuse", second, ["tool.sh"], (), 2, "differ from"),
            ("head-refuse", "HEAD", ["tool.sh"], (), 2, "40-hex"),
            ("branch-refuse", "master", ["tool.sh"], (), 2, "40-hex"),
            ("short-id-refuse", second[:12], ["tool.sh"], (), 2, "40-hex"),
            ("no-paths-refuse", second, [], (), 2, "no measured paths"),
            ("historical-no-tree-check", clean, [],
             ("--no-tree-check",), 0, ""),
        ]
        for name, rev, paths, extra, want_code, want_text in cases:
            if name == "dirty-tree-refuse":
                dirty_once()
            code, text = run_helper(helper, repo, rev, paths, extra)
            ok = code == want_code and (want_text == "" or want_text in text)
            if ok:
                passed += 1
                print("CASE\tpass\t%s\texit=%d" % (name, code))
            else:
                failed += 1
                print("CASE\tFAIL\t%s\texit=%d want=%d text=%r"
                      % (name, code, want_code, text[:160]))
            if want_code == 2:
                stub_code = run_stub(stub, repo, rev)
                if stub_code == 0:
                    base_disc += 1
                print("CASE\t%s\tbase/%s\texit=%d"
                      % ("discriminates" if stub_code == 0 else "accepts-refusal",
                         name, stub_code))

        # Static wiring: each consumer must route through the helper.
        for rel, (marker, forbidden) in WIRING.items():
            path = os.path.join(tool_dir, rel)
            try:
                with open(path, encoding="utf-8") as handle:
                    text = handle.read()
            except OSError as exc:
                failed += 1
                print("CASE\tFAIL\twiring/%s\tunreadable: %s" % (rel, exc))
                continue
            missing = marker not in text
            leftovers = [token for token in forbidden if token in text]
            if missing or leftovers:
                failed += 1
                print("CASE\tFAIL\twiring/%s\tmissing=%s leftovers=%s"
                      % (rel, missing, leftovers))
            else:
                passed += 1
                print("CASE\tpass\twiring/%s" % rel)

        if base_disc < sum(1 for case in cases if case[4] == 2):
            failed += 1
            print("CASE\tFAIL\tbase-vacuity\tonly %d/%d refusal cases accepted "
                  "by the pre-fix stub" % (base_disc,
                                           sum(1 for c in cases if c[4] == 2)))
        print("SUMMARY total=%d failed=%d base_discriminating=%d"
              % (passed + failed, failed, base_disc))
        return 0 if failed == 0 else 1
    finally:
        shutil.rmtree(top, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
