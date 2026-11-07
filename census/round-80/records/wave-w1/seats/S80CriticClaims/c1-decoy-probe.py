#!/usr/bin/env python3
"""r80 critic probe 3 (C1): an out-of-population false MOVED row whose decoy copy sits INSIDE the declared
capture root census/round-32/ instead of corpus/round-32/. The successor counter's location rule accepts a
target whose path before round-<N> is "census"; the probe shows the row resolves (accepted), i.e. the NF10
defect shape is still accepted when the byte-equal copy is planted under census/round-<N>/.

Fixture: shared clone of the lane at BASE (never written to), one commit adding the decoy.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "e65538e73c7f1a8f7570bc24a2215da8a90043f3"
COUNTER = os.path.join(LANE, "census/round-80/c1-pointer-counter.py")
S = "/fast/scratch/hyaku/souji-r80/S80CriticClaims"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r80 critic", "GIT_AUTHOR_EMAIL": "critic@r80.invalid",
            "GIT_COMMITTER_NAME": "r80 critic", "GIT_COMMITTER_EMAIL": "critic@r80.invalid",
            "GIT_AUTHOR_DATE": "2026-11-07T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-07T00:00:00Z"})


def git(repo, *args):
    assert os.path.isabs(repo), repo
    return subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV).stdout


def main():
    work = tempfile.mkdtemp(prefix="c1decoy.", dir=S)
    fx = os.path.join(work, "fixture")
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", LANE, fx], check=True, env=ENV)
    top = git(fx, "rev-parse", "--show-toplevel").decode().strip()
    assert os.path.realpath(top) == os.path.realpath(fx), top
    git(fx, "checkout", "-q", "--detach", BASE)
    real = git(fx, "show", f"{BASE}:census/round-32/waves/a2w1/SwarmExecutor08.md")
    decoy = os.path.join(fx, "census/round-32/decoy/SwarmExecutor08.md")
    os.makedirs(os.path.dirname(decoy), exist_ok=True)
    with open(decoy, "wb") as f:
        f.write(real)
    git(fx, "add", "-f", "--", "census/round-32/decoy/SwarmExecutor08.md")
    git(fx, "commit", "-q", "--no-verify", "-m", "r80 critic: byte-equal decoy inside the declared capture root")
    head = git(fx, "rev-parse", "HEAD").decode().strip()
    row = "X1\tP04\tMOVED\tcensus/round-32/decoy/SwarmExecutor08.md\tREFUSED\n"
    forge = os.path.join(work, "forge-X1.tsv")
    with open(forge, "w") as f:
        f.write(row)
    p = subprocess.run([sys.executable, "-B", COUNTER, "--root", fx, "--rev", head, "--fleet-root", FLEET,
                        "--population", os.path.join(LANE, "census/round-77/c2-population.tsv"),
                        "--ledger", os.path.join(LANE, "census/round-77/c2-pointer-ledger.tsv"),
                        "--forge", forge], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, cwd=LANE)
    out = p.stdout.decode("utf-8", "replace")
    lines = [l for l in out.splitlines() if l.startswith(("FORGE ", "FORGE-SUMMARY", "SUMMARY"))]
    print(json.dumps({"decoy_sha256": hashlib.sha256(real).hexdigest(), "fixture_head": head,
                      "decoy": "census/round-32/decoy/SwarmExecutor08.md",
                      "counter_rc": p.returncode, "lines": lines,
                      "stderr": p.stderr.decode()[:300]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
