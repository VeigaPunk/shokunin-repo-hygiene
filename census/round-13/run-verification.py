#!/usr/bin/env python3
"""Round-13 bounded verification; output is evidence, never deletion certification.

Every main execution must name a new evidence path:

    python3 census/round-13/run-verification.py --round <N> \
        --output census/round-<N>/<new>.json [--retry-failed --previous PATH]

Invoked without --round and --output it refuses with exit 2 before any check,
and it never overwrites an existing file: output must be a new, lane-contained
census/round-<N>/*.json with a real existing parent, no symlink component, and
no protected or operator-sweep path. `--retry-failed` reads prior evidence
(default census/round-13/verification.json) but keeps its bytes untouched;
the recorded `round` and `prior_attempt` reflect the actual arguments.

With --retry-failed, a prior matched result is retained only when
tools/souji-evidence-cache.py exits 0 for a record built from that result's own
measured_commit and its stored dependency digests. Legacy results without
dependencies, results without their own revision, unstable captures,
non-matched results and external-mutable commands are re-executed instead.
Retention never recomputes digests into a prior record and never inherits a
revision from the top-level record. Historical JSON outputs are read only.
"""
import collections
import datetime
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import signal
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = "31984f473ce4bdab61a99b16cca194b28108cb81"
HISTORICAL_VERIFICATION = ROOT / "census/round-13/verification.json"
GATE = ROOT / "tools/souji-evidence-cache.py"
GATE_TIMEOUT = 120
RUNNER_PATH = str(Path(__file__).resolve().relative_to(ROOT))
GATE_LABEL = str(GATE.relative_to(ROOT))
GATE_FINDING = re.compile(r"(?m)^finding ([a-z0-9_-]+):")
PROTECTED_COMPONENTS = frozenset({
    ".omp", ".ssh", ".gnupg", ".aws", ".kube", ".password-store", ".config", ".git", ".ufo",
})
# External commands and the paired baseline extraction are always re-executed:
# their inputs are neither lane-bound nor captured completely as digests.
REUSE_EXEMPT = {"sources-contract", "shellcheck-warning", "quarantine-red-before"}
ENV = os.environ.copy()
ENV.update(TMPDIR="/var/tmp", LC_ALL="C", GIT_CONFIG_NOSYSTEM="1",
           GIT_CONFIG_GLOBAL="/dev/null", GIT_TERMINAL_PROMPT="0",
           SOUJI_CLI_BIN="/bin/false", PYTHONDONTWRITEBYTECODE="1")
for key in list(ENV):
    if key.startswith("GIT_") and key not in {
        "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_TERMINAL_PROMPT"
    }:
        ENV.pop(key)
ENV.update(GIT_AUTHOR_NAME="souji-r13-fixture",
           GIT_AUTHOR_EMAIL="fixture@example.invalid",
           GIT_COMMITTER_NAME="souji-r13-fixture",
           GIT_COMMITTER_EMAIL="fixture@example.invalid")
PREVIOUS = None
PREVIOUS_RESULTS = {}
RETRY_NAMES = set()
PREVIOUS_SOURCE = None
CURRENT_REV = ""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_or_none(path):
    try:
        return digest(path)
    except OSError:
        return None


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], env=ENV).decode().strip()


def dependency_map(command, name):
    """Bind this observation to the runner plus literal existing lane inputs.

    Only paths named on the command line (or the recursive contents of a named
    fixture directory) are bound. The lane is never scanned wholesale, and
    operator-sweep trees are never entered. External absolute paths are
    excluded; results whose external inputs are mutable are reuse-exempt.
    """
    paths = {RUNNER_PATH}
    if name.endswith(".sh-selftest"):
        helper = ROOT / "tools/souji-round9-selftest.sh"
        if helper.is_file() and not helper.is_symlink():
            paths.add(str(helper.relative_to(ROOT)))
    root_real = Path(os.path.realpath(str(ROOT)))
    for argument in command[1:]:
        if argument.startswith("-"):
            continue
        candidate = Path(argument)
        if not candidate.is_absolute():
            candidate = ROOT / candidate
        if candidate.is_symlink():
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            continue
        if resolved == root_real or root_real not in resolved.parents:
            continue
        relative = resolved.relative_to(root_real)
        parts = relative.parts
        if parts and parts[0] == "census" and len(parts) > 1 and parts[1].startswith("operator-sweep-"):
            continue
        if resolved.is_dir():
            for child in sorted(resolved.rglob("*")):
                if child.is_symlink() or not child.is_file():
                    continue
                paths.add(str(child.relative_to(root_real)))
        elif resolved.is_file():
            paths.add(str(relative))
    return {relative: digest(ROOT / relative) for relative in sorted(paths)}


def gate_reuse(prior):
    """Ask the installed cache-eligibility gate about a stored record."""
    record = {
        "name": prior["name"],
        "matched": True,
        "measured_commit": prior["measured_commit"],
        "dependencies": dict(prior["dependencies"]),
    }
    handle = tempfile.NamedTemporaryFile(
        "w", prefix="souji-r13-retention.", suffix=".json", dir="/var/tmp",
        delete=False, encoding="utf-8")
    record_path = Path(handle.name)
    try:
        with handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")
        try:
            process = subprocess.run(
                [sys.executable, str(GATE), "--root", str(ROOT),
                 "--record", str(record_path)],
                capture_output=True, text=True, timeout=GATE_TIMEOUT, env=ENV)
            exit_code = process.returncode
            stdout = process.stdout or ""
            stderr = process.stderr or ""
        except subprocess.TimeoutExpired as exc:
            exit_code = 124
            stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = "gate timeout\n"
        except OSError as exc:
            exit_code = 126
            stdout = ""
            stderr = "gate invocation failed: %s\n" % exc
    finally:
        record_path.unlink(missing_ok=True)
    findings = sorted(set(GATE_FINDING.findall(stdout + "\n" + stderr)))
    return {
        "gate": GATE_LABEL,
        "gate_sha256": sha_or_none(GATE),
        "exit_code": exit_code,
        "reusable": exit_code == 0,
        "findings": findings,
        "stdout": stdout[:4096],
        "stderr": stderr[:4096],
    }


def attempt_reuse(name, prior):
    """Return (retained source, evidence). Nothing is reusable on any doubt."""
    if name in REUSE_EXEMPT:
        return None, {"reused": False, "reason": "external-mutable-command"}
    if prior.get("matched") is not True:
        return None, {"reused": False, "reason": "prior-not-matched"}
    commit = prior.get("measured_commit")
    if not isinstance(commit, str) or len(commit) != 40 or any(
            character not in "0123456789abcdef" for character in commit):
        # Never inherit a revision from a top-level or newer field.
        return None, {"reused": False, "reason": "prior-measured-commit-missing"}
    if prior.get("dependencies_stable") is not True:
        return None, {"reused": False, "reason": "prior-dependencies-unstable"}
    dependencies = prior.get("dependencies")
    if not isinstance(dependencies, dict) or not dependencies:
        return None, {"reused": False, "reason": "prior-dependencies-legacy"}
    decision = gate_reuse(prior)
    decision["reused"] = decision["reusable"]
    if not decision["reusable"]:
        # Exit 1/2 never yields a retained source, regardless of the record.
        decision["reason"] = "gate-refused"
        return None, decision
    return prior, decision


def run(name, command, expected=0, seconds=120):
    if PREVIOUS and name not in RETRY_NAMES:
        prior = PREVIOUS_RESULTS.get(name)
        if prior is not None:
            retained_source, reuse = attempt_reuse(name, prior)
            if retained_source is not None:
                retained = dict(retained_source)
                retained["retained_from"] = PREVIOUS_SOURCE
                retained["reuse"] = reuse
                print(f"{name}: retaining prior exercised result at "
                      f"{retained['measured_commit']} (gate exit={reuse['exit_code']})",
                      flush=True)
                return retained
            print(f"{name}: not reused ({reuse['reason']}) -> re-executing", flush=True)
    dependencies_before = dependency_map(command, name)
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
    dependencies_after = dependency_map(command, name)
    item = dict(name=name, command=command, exit_code=code, expected_exit=expected,
                matched=code == expected, stdout=stdout, stderr=stderr,
                seconds=round(time.monotonic() - start, 3),
                dependencies=dependencies_after,
                dependencies_stable=dependencies_before == dependencies_after,
                reuse_eligible=name not in REUSE_EXEMPT)
    item["measured_commit"] = CURRENT_REV
    print(f"{name}: exit={code} expected={expected} matched={item['matched']}", flush=True)
    return item


def lane_relative(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def lexical_path(argument):
    candidate = Path(argument)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return Path(os.path.abspath(str(candidate)))


def protected_parts(relative):
    return any(
        part.startswith("operator-sweep-") or part in PROTECTED_COMPONENTS
        for part in relative.parts
    )


def closed_round_floor():
    """Highest existing census/round-<N> number; earlier rounds are closed."""
    census_dir = ROOT / "census"
    floor = 0
    if not census_dir.is_dir():
        return floor
    for entry in census_dir.iterdir():
        if entry.is_symlink() or not entry.is_dir():
            continue
        match = re.fullmatch(r"round-(\d+)", entry.name)
        if match is not None:
            floor = max(floor, int(match.group(1)))
    return floor


def validate_output(round_number, output_argument):
    """Return (new output path, None) or (None, refusal reason).

    The evidence path must be an explicitly new, lane-contained
    census/round-<N>/*.json file with a real existing parent directory. An
    existing file, symlink, historical evidence path, protected path, operator
    sweep path, or a round below the closed-round floor is refused before any
    check runs.
    """
    if not isinstance(round_number, int) or isinstance(round_number, bool) or round_number < 1:
        return None, "round-invalid"
    if round_number < closed_round_floor():
        return None, "round-closed"
    output = lexical_path(output_argument)
    root_abs = Path(os.path.abspath(str(ROOT)))
    if output == root_abs or root_abs not in output.parents:
        return None, "output-not-lane-contained"
    if output.parent != root_abs / "census" / ("round-%d" % round_number):
        return None, "output-not-round-directory"
    if not output.name.endswith(".json"):
        return None, "output-name-invalid"
    relative = output.relative_to(root_abs)
    if protected_parts(relative):
        return None, "output-protected-path"
    if output.is_symlink():
        return None, "output-symlink"
    if output.exists():
        return None, "output-exists"
    if output.resolve(strict=False) != output:
        return None, "output-symlink-ancestor"
    if output.parent.is_symlink() or not output.parent.is_dir():
        return None, "output-parent-invalid"
    current = root_abs
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            return None, "output-symlink-ancestor"
    if output == Path(os.path.abspath(str(HISTORICAL_VERIFICATION))):
        return None, "output-historical-evidence"
    return output, None


def validate_previous(previous_argument):
    """Return (readable prior evidence path, None) or (None, refusal reason)."""
    previous = lexical_path(previous_argument)
    root_abs = Path(os.path.abspath(str(ROOT)))
    if previous == root_abs or root_abs not in previous.parents:
        return None, "previous-not-lane-contained"
    if protected_parts(previous.relative_to(root_abs)):
        return None, "previous-protected-path"
    if previous.is_symlink():
        return None, "previous-symlink"
    if not previous.is_file():
        return None, "previous-not-regular"
    try:
        resolved = previous.resolve(strict=True)
    except OSError:
        return None, "previous-unreadable"
    if resolved != previous:
        return None, "previous-symlink-ancestor"
    return previous, None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Bounded verification runner; every main execution must name a new explicit evidence path.")
    parser.add_argument("--round", type=int, help="round number recorded in the new evidence file")
    parser.add_argument("--output", help="new evidence path: census/round-<N>/<new>.json")
    parser.add_argument("--retry-failed", action="store_true",
                        help="read prior evidence for retention decisions; never overwrite it")
    parser.add_argument("--previous", default=str(HISTORICAL_VERIFICATION),
                        help="prior evidence file to read with --retry-failed (default: %(default)s)")
    args = parser.parse_args(argv)

    if args.round is None or args.output is None:
        print("run-verification: refusing: --round N and --output census/round-N/<new>.json "
              "are required; no default output exists", file=sys.stderr)
        return 2

    output, reason = validate_output(args.round, args.output)
    if reason is not None:
        print("run-verification: refusing output %r: %s" % (args.output, reason), file=sys.stderr)
        return 2

    previous = None
    if args.retry_failed:
        previous, reason = validate_previous(args.previous)
        if reason is not None:
            print("run-verification: refusing previous %r: %s" % (args.previous, reason), file=sys.stderr)
            return 2

    try:
        return execute(args.round, output, previous)
    except FileExistsError:
        print("run-verification: refusing to overwrite existing evidence %s" % output,
              file=sys.stderr)
        return 2
    except Exception as exc:
        print("run-verification: could-not-evaluate: %s: %s" % (type(exc).__name__, exc),
              file=sys.stderr)
        return 2


def execute(round_number, output, previous):
    global CURRENT_REV, PREVIOUS, PREVIOUS_RESULTS, RETRY_NAMES, PREVIOUS_SOURCE
    revision = git("rev-parse", "HEAD")
    CURRENT_REV = revision
    PREVIOUS = json.loads(previous.read_text()) if previous is not None else None
    PREVIOUS_RESULTS = {item["name"]: item for item in PREVIOUS["results"]} if PREVIOUS else {}
    RETRY_NAMES = {name for name, item in PREVIOUS_RESULTS.items() if not item["matched"]}
    PREVIOUS_SOURCE = lane_relative(previous) if previous is not None else None
    artifacts = [ROOT / "tools" / name for name in (
        "souji-verify.sh", "souji-vault-verify.sh", "souji-quarantine.sh",
        "souji-census.sh", "souji-cert-evidence.py", "souji-repo-structure.sh",
        "souji-evidence-cache.py")]
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
    record = dict(round=round_number, measured_commit=revision, baseline_commit=BASE,
                  recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  installed_sha256=after, artifacts_unchanged_during_run=before == after,
                  retention_gate=dict(
                      path=GATE_LABEL, sha256=sha_or_none(GATE),
                      policy="reuse a prior matched result only when the gate exits 0; "
                             "legacy, unstable, missing-revision, non-matched and "
                             "external-mutable results re-execute"),
                  results=results, sources=census, admitted_entries=admitted,
                  prior_attempt=PREVIOUS_SOURCE,
                  deletion_certification="OFF", scope="Declared integrity and bounded fixtures; no complete class-suite certification")
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(record, indent=2) + "\n")
    return 0 if before == after and all(item["matched"] for item in results) else 1


if __name__ == "__main__":
    sys.exit(main())
