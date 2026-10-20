#!/usr/bin/env python3
"""Run only r14 owned checks; never a live census or deletion certification."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = "a31642d14006830ec62edf40b0354c3699728c4a"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(TMPDIR="/var/tmp", PYTHONDONTWRITEBYTECODE="1", LC_ALL="C",
           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
           GIT_TERMINAL_PROMPT="0", GIT_AUTHOR_NAME="souji-r14-fixture",
           GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_NAME="souji-r14-fixture",
           GIT_COMMITTER_EMAIL="fixture@example.invalid")

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], env=ENV, text=True).strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(name, command, revision, expected=0, seconds=150):
    started = time.monotonic()
    child = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = child.communicate(timeout=seconds)
        code = child.returncode
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            out, err = child.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            out, err = child.communicate()
        code = 124
        err += "\nROUND14_OUTER_TIMEOUT\n"
    result = dict(name=name, command=command, exit_code=code, expected_exit=expected,
                  matched=code == expected, stdout=out, stderr=err,
                  measured_commit=revision, seconds=round(time.monotonic()-started, 3))
    print(f"{name}: exit={code} expected={expected} matched={result['matched']}", flush=True)
    return result

def main():
    target = ROOT/"census/round-14/verification.json"
    if target.exists():
        raise RuntimeError("Refuse overwriting exercised evidence; use a new attempt filename")
    revision = git("rev-parse", "HEAD")
    paths = ["tools/souji-evidence-cache.py", "tools/souji-census.sh",
             "tests/fixtures/r14-evidence-cache.py", "tests/fixtures/r14-census-boundary.py",
             "census/round-14/cache-demonstration.py", "census/round-13/run-verification.py"]
    before = {p: sha(ROOT/p) for p in paths}
    historical_before = sha(ROOT/"census/round-13/verification.json")
    results = []
    with tempfile.TemporaryDirectory(prefix="souji-r14-verification-", dir="/var/tmp") as temp:
        baseline = Path(temp)/"souji-census.sh"
        baseline.write_bytes(subprocess.check_output(["git", "-C", str(ROOT), "show", BASE+":tools/souji-census.sh"], env=ENV))
        baseline.chmod(0o700)
        commands = [
            ("cache-selftest", ["python3", "-B", "tools/souji-evidence-cache.py", "--selftest"], 0),
            ("cache-fixture", ["python3", "-B", "tests/fixtures/r14-evidence-cache.py"], 0),
            ("cache-frozen", ["python3", "-B", "tools/souji-evidence-cache.py", "--frozen", "tests/fixtures/r14-cache-frozen"], 0),
            ("cache-consumer-red-green", ["python3", "-B", "census/round-14/cache-demonstration.py"], 0),
            ("historical-runner-default-refusal", ["python3", "-B", "census/round-13/run-verification.py"], 2),
            ("census-boundary-red-before", ["python3", "-B", "tests/fixtures/r14-census-boundary.py", "--tool", str(baseline)], 1),
            ("census-boundary", ["python3", "-B", "tests/fixtures/r14-census-boundary.py", "--tool", str(ROOT/"tools/souji-census.sh")], 0),
            ("census-legacy-selftest", ["bash", "tools/souji-census.sh", "--selftest"], 0),
            ("census-shellcheck-warning", ["shellcheck", "-S", "warning", "tools/souji-census.sh"], 0),
            ("source-anchor-red-before", ["python3", "-B", "census/round-14/check-timeout-anchor.py", "S034"], 1),
            ("source-anchor-corrected", ["python3", "-B", "census/round-14/check-timeout-anchor.py", "S038"], 0),
            ("sources-contract", ["/home/vgpnk/Projects/shokunin/scripts/sources-census.sh", "validate", "--root", "/home/vgpnk/Projects/shokunin", "souji"], 0),
        ]
        for name, command, expected in commands:
            results.append(run(name, command, revision, expected))
        baseline_digest = sha(baseline)
    after = {p: sha(ROOT/p) for p in paths}
    historical_after = sha(ROOT/"census/round-13/verification.json")
    data = dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                measured_commit=revision, baseline_commit=BASE, baseline_census_sha256=baseline_digest,
                installed_sha256=after, artifacts_unchanged_during_run=before == after,
                historical_evidence_sha256_before=historical_before,
                historical_evidence_sha256_after=historical_after,
                historical_evidence_unchanged=historical_before == historical_after, results=results,
                scope="All fixtures isolated under /var/tmp; no real credential-store probe or live census. No deletion certification.")
    target.write_text(json.dumps(data, indent=2)+"\n")
    return 0 if before == after and historical_before == historical_after and all(x["matched"] for x in results) else 1

if __name__ == "__main__":
    raise SystemExit(main())
