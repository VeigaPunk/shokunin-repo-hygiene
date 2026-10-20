#!/usr/bin/env python3
"""Round-13 bounded verification; output is evidence, never deletion certification."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import signal
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = "31984f473ce4bdab61a99b16cca194b28108cb81"
OUTPUT = ROOT / "census/round-13/verification.json"
ENV = os.environ.copy()
ENV.update(TMPDIR="/var/tmp", LC_ALL="C", GIT_CONFIG_NOSYSTEM="1",
           GIT_CONFIG_GLOBAL="/dev/null", GIT_TERMINAL_PROMPT="0",
           SOUJI_CLI_BIN="/bin/false")
for key in list(ENV):
    if key.startswith("GIT_") and key not in {
        "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_TERMINAL_PROMPT"
    }:
        ENV.pop(key)
ENV.update(GIT_AUTHOR_NAME="souji-r13-fixture",
           GIT_AUTHOR_EMAIL="fixture@example.invalid",
           GIT_COMMITTER_NAME="souji-r13-fixture",
           GIT_COMMITTER_EMAIL="fixture@example.invalid")
PREVIOUS = json.loads(OUTPUT.read_text()) if "--retry-failed" in sys.argv else None
PREVIOUS_RESULTS = {item["name"]: item for item in PREVIOUS["results"]} if PREVIOUS else {}
RETRY_NAMES = {name for name, item in PREVIOUS_RESULTS.items() if not item["matched"]}
if "quarantine-bounds" in RETRY_NAMES:
    # The fixture itself changed: repeat the paired baseline with identical new bytes.
    RETRY_NAMES.add("quarantine-red-before")
CURRENT_REV = ""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], env=ENV).decode().strip()


def run(name, command, expected=0, seconds=120):
    if PREVIOUS and name not in RETRY_NAMES:
        retained = dict(PREVIOUS_RESULTS[name])
        retained["measured_commit"] = retained.get("measured_commit", PREVIOUS["measured_commit"])
        retained["retained_from"] = "census/round-13/verification-attempt-1.json"
        print(f"{name}: retaining prior exercised result at {retained['measured_commit']}", flush=True)
        return retained
    start = time.monotonic()
    process = subprocess.Popen(command, cwd=ROOT, env=ENV, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=seconds)
        code = process.returncode
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        code = 124
        stderr += "\nROUND13_OUTER_TIMEOUT\n"
    item = dict(name=name, command=command, exit_code=code, expected_exit=expected,
                matched=code == expected, stdout=stdout, stderr=stderr,
                seconds=round(time.monotonic() - start, 3))
    item["measured_commit"] = CURRENT_REV
    print(f"{name}: exit={code} expected={expected} matched={item['matched']}", flush=True)
    return item


def main():
    revision = git("rev-parse", "HEAD")
    global CURRENT_REV
    CURRENT_REV = revision
    artifacts = [ROOT / "tools" / name for name in (
        "souji-verify.sh", "souji-vault-verify.sh", "souji-quarantine.sh",
        "souji-census.sh", "souji-cert-evidence.py", "souji-repo-structure.sh")]
    before = {str(path.relative_to(ROOT)): digest(path) for path in artifacts}
    results = []
    results.append(run("evidence-selftest", ["python3", "tools/souji-cert-evidence.py", "--selftest"]))
    results.append(run("evidence-frozen", ["python3", "tools/souji-cert-evidence.py", "--frozen", "tests/fixtures/r13-cert-frozen"]))
    results.append(run("evidence-external-fixture", ["python3", "tests/fixtures/r13-cert-evidence.py"]))
    results.append(run("structure-selftest", ["bash", "tests/fixtures/r13-repo-structure.sh", "--selftest", "--probe", "tools/souji-repo-structure.sh"]))
    with tempfile.TemporaryDirectory(prefix="souji-r13-before.", dir="/var/tmp") as scratch:
        baseline = Path(scratch) / "souji-quarantine.sh"
        baseline.write_bytes(subprocess.check_output([
            "git", "-C", str(ROOT), "show", BASE + ":tools/souji-quarantine.sh"], env=ENV))
        results.append(run("quarantine-red-before", ["bash", "tests/fixtures/r13-quarantine-bounds.sh", "--tool", str(baseline)], expected=1))
        results.append(run("quarantine-bounds", ["bash", "tests/fixtures/r13-quarantine-bounds.sh", "--tool", str(ROOT / "tools/souji-quarantine.sh")]))
    for tool in ("souji-verify.sh", "souji-vault-verify.sh", "souji-quarantine.sh", "souji-census.sh"):
        results.append(run(tool + "-selftest", ["bash", "tools/" + tool, "--selftest"], seconds=180))
    results.append(run("shellcheck-warning", ["shellcheck", "-S", "warning", "tools/souji-quarantine.sh", "tools/souji-repo-structure.sh", "tests/fixtures/r13-quarantine-bounds.sh", "tests/fixtures/r13-repo-structure.sh"]))
    results.append(run("sources-contract", ["/home/vgpnk/Projects/shokunin/scripts/sources-census.sh", "validate", "--root", "/home/vgpnk/Projects/shokunin", "souji"]))
    if (ROOT / "census/round-13/replay-wrong-bytes.json").exists():
        for label, finding in (("wrong-bytes", "artifact-digest-mismatch"),
                               ("candidate", "artifact-candidate")):
            replay = run("historical-replay-" + label,
                         ["python3", "tools/souji-cert-evidence.py", "--root", str(ROOT),
                          "--manifest", "census/round-13/replay-" + label + ".json"], expected=2)
            replay["required_finding"] = finding
            replay["matched"] = replay["matched"] and f"finding {finding}:" in replay["stdout"] + replay["stderr"]
            results.append(replay)
    rows = []
    for line in (ROOT / "corpus/SOURCES.md").read_text().splitlines():
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) == 13 and cells[1].startswith("S") and cells[1][1:].isdigit():
            rows.append(cells)
    census = dict(rows=len(rows), tiers=dict(collections.Counter(row[4] for row in rows)),
                  statuses=dict(collections.Counter(row[8] for row in rows)))
    admitted = []
    for entry in (ROOT / "corpus/knowledge").glob("*.md"):
        text = entry.read_text()
        if "## Admission status — HELD" not in text and all(
            text.splitlines()[index].startswith(prefix)
            for index, prefix in enumerate(("source:", "verified-at:", "recheck:"))
        ):
            admitted.append(str(entry.relative_to(ROOT)))
    after = {str(path.relative_to(ROOT)): digest(path) for path in artifacts}
    record = dict(round=13, measured_commit=revision, baseline_commit=BASE,
                  recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  installed_sha256=after, artifacts_unchanged_during_run=before == after,
                  results=results, sources=census, admitted_entries=admitted,
                  prior_attempt="census/round-13/verification-attempt-1.json" if PREVIOUS else None,
                  deletion_certification="OFF", scope="Declared integrity and bounded fixtures; no complete class-suite certification")
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n")
    return 0 if before == after and all(item["matched"] for item in results) else 1


if __name__ == "__main__":
    sys.exit(main())
