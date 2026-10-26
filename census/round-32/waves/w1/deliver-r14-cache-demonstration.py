#!/usr/bin/env python3
"""Round-14 C1 consumer demonstration: digest-bound retention, never retained green.

This is an isolated synthetic demonstration of evidence-collection decisions,
not a production evidence consumer. It exercises the historical and migrated
attempt_reuse decision functions separately; it does not run the full migrated
dispatch or demonstrate positive production retention. Historical JSON outputs
are never rewritten.

The demonstration builds a synthetic observation under /var/tmp only:

  1. initial-fresh        producer execution 1 supplies a green result and the
                          record written from it carries that result's actual
                          measured_commit and dependency digests;
  2. unchanged            reuse(record) asks the installed gate; only exit 0
                          returns a retained result, and no producer runs;
  3. dependency-modified  one dependency byte changes; reuse(record) must not
                          return exit 0, so the policy executes a fresh
                          producer (execution 2) instead of retaining green;
  4. legacy-no-deps       a matched record without dependencies is refused by
                          the gate (exit 2) and also re-executes (execution 3).

The unsafe control re-applies the old policy (retain whenever record.matched
is true) to the same stale and legacy records and reports that it would have
retained a green whose dependency bytes drifted. The authentic red-before then
loads census/round-13/run-verification.py at baseline commit
a31642d14006830ec62edf40b0354c3699728c4a with `git show`, isolates its actual
top-level run() FunctionDef with ast.parse, compiles it against synthetic
module globals, and executes it on the same stale matched-green record with a
harmless producer command. The baseline retention branch returns the stale
green without invoking that command; the new caller refuses the same record
and re-executes. The migrated runner is then imported read-only and its
attempt_reuse decision is executed directly on unchanged, stale, legacy,
missing-revision, unstable and external-mutable in-memory records.

Every gate decision is retained with its exit code and any `finding <id>:`
lines parsed from the gate's own output. The stale and legacy cases also
assert the exact ids `dependency-digest-mismatch` and `dependencies-legacy`.
The installed gate path and its sha256 are recorded before and after
invocation.

Output: one JSON document on stdout.

Exit codes: 0 demonstration agrees with the gate and all checks pass,
1 a check failed (red), 2 prerequisite or environment blocked the run.

No production data, no credentials, no historical evidence is read or
written. Certification remains OFF; this is not deletion authorization.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import datetime
import hashlib
import io
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

LANE = Path(__file__).resolve().parents[2]
DEFAULT_GATE = LANE / "tools" / "souji-evidence-cache.py"
BASELINE_COMMIT = "a31642d14006830ec62edf40b0354c3699728c4a"
BASELINE_RUNNER = "census/round-13/run-verification.py"
# r19 C2: tracked subjects this demonstration executes or reads as measured
# bytes. The harness revision is stamped only when it is durable and these
# paths equal the working tree (the synthetic dependency bytes live under
# /var/tmp and are never claimed to be contained in the commit).
DEMO_MEASURED_PATHS = [
    "tools/souji-evidence-cache.py",
    "tools/souji-census.sh",
    "tests/fixtures/r14-evidence-cache.py",
    "tests/fixtures/r14-census-boundary.py",
    "census/round-14/cache-demonstration.py",
    "census/round-13/run-verification.py",
    "tools/souji-rev-pin.py",
    "census/round-13/verification.json",
]
DEMO_INPUT_SHA256 = None
DEMO_PINNED_REV = None
SYNTHETIC_NAME = "synthetic-matched-green"
NAME = "r14-cache-demonstration"
EXPECTED_STALE_FINDINGS = ("dependency-digest-mismatch",)
EXPECTED_LEGACY_FINDINGS = ("dependencies-legacy",)
REUSABLE_STATUS = "souji-evidence-cache: reusable"
STALE_STATUS = "souji-evidence-cache: stale"
COULD_NOT_EVALUATE_STATUS = "souji-evidence-cache: could-not-evaluate"
TMP_BASE = tempfile.gettempdir()
OUTPUT_LIMIT = 16384
GATE_TIMEOUT = 120
FINDING_PATTERN = re.compile(r"(?m)^finding ([a-z0-9_-]+):")
HEX40 = re.compile(r"[0-9a-f]{40}")
GATE_ENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "LC_ALL": "C",
    "TMPDIR": TMP_BASE,
    "PYTHONDONTWRITEBYTECODE": "1",
}
GIT_ENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_OPTIONAL_LOCKS": "0",
}
FIXTURE = {
    "observations/alpha.txt": b"alpha observation for the r14 cache demonstration\n",
    "observations/beta.txt": b"beta observation for the r14 cache demonstration\n",
}
DEPENDENCY_ORDER = tuple(FIXTURE)
MUTATION_MARKER = b"# mutated after the retained green\n"
PRODUCER_CODE = (
    "import hashlib, pathlib, sys\n"
    "root = pathlib.Path(sys.argv[1])\n"
    "parts = []\n"
    "for rel in sys.argv[2:]:\n"
    "    parts.append(rel + '=' + hashlib.sha256((root / rel).read_bytes()).hexdigest())\n"
    "sys.stdout.write('r14-producer ' + ' '.join(parts) + '\\n')\n"
)


class DemoBlocked(Exception):
    """A prerequisite or environment condition made the demonstration unevaluable."""

    def __init__(self, reason, detail=None):
        super().__init__(reason)
        self.reason = reason
        self.detail = detail or {}


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 256), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def trim(text):
    text = text or ""
    if len(text) <= OUTPUT_LIMIT:
        return text, False
    return text[:OUTPUT_LIMIT], True


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return value


def within(base_real, path):
    resolved = Path(os.path.realpath(str(path)))
    return resolved == base_real or base_real in resolved.parents


def git_head():
    global DEMO_INPUT_SHA256, DEMO_PINNED_REV
    try:
        proc = subprocess.run(
            ["git", "-C", str(LANE), "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            env=GIT_ENV,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, "git rev-parse unavailable: %s" % exc
    value = proc.stdout.strip()
    if proc.returncode != 0 or HEX40.fullmatch(value) is None:
        return None, "git rev-parse exit=%d output=%r" % (proc.returncode, value)
    helper = LANE / "tools/souji-rev-pin.py"
    try:
        if helper.parent.is_symlink() or helper.is_symlink() or not helper.is_file():
            raise ValueError("nonregular revision helper tools/souji-rev-pin.py")
        committed = subprocess.check_output(
            ["git", "-C", str(LANE), "show", value + ":tools/souji-rev-pin.py"],
            env=GIT_ENV)
        if helper.read_bytes() != committed:
            raise ValueError("tools/souji-rev-pin.py differs from measured commit")
        spec = importlib.util.spec_from_file_location("souji_rev_pin", helper)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        revision = module.resolve_durable(str(LANE), value, DEMO_MEASURED_PATHS)
        observed = module.input_snapshot(str(LANE), revision, DEMO_MEASURED_PATHS)
        if DEMO_INPUT_SHA256 is None:
            DEMO_INPUT_SHA256, DEMO_PINNED_REV = observed, revision
        elif observed != DEMO_INPUT_SHA256 or revision != DEMO_PINNED_REV:
            raise module.Refusal("owned inputs or measured revision changed during run")
        return revision, None
    except (OSError, ValueError, SyntaxError, ImportError, subprocess.CalledProcessError) as exc:
        return None, "durable revision refused: %s" % exc


def stat_file(path):
    state = {
        "path": str(path),
        "exists": path.exists(),
        "symlink": path.is_symlink(),
        "regular": path.is_file() and not path.is_symlink(),
        "size_bytes": None,
        "sha256": None,
    }
    if state["regular"]:
        try:
            state["size_bytes"] = path.stat().st_size
            state["sha256"] = sha256_file(path)
        except OSError as exc:
            state["regular"] = False
            state["error"] = str(exc)
    return state


def tracked_at(commit, relative):
    try:
        proc = subprocess.run(
            ["git", "-C", str(LANE), "cat-file", "-e", "%s:%s" % (commit, relative)],
            capture_output=True,
            text=True,
            timeout=30,
            env=GIT_ENV,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def inspect_gate(gate):
    state = stat_file(gate)
    state["installed_default"] = stat_file(DEFAULT_GATE)
    state["installed_default"]["tracked_at_baseline_commit"] = tracked_at(
        BASELINE_COMMIT, "tools/souji-evidence-cache.py"
    )
    state["matches_installed_default"] = os.path.realpath(str(gate)) == os.path.realpath(str(DEFAULT_GATE))
    state["reason"] = None
    if not gate.is_absolute():
        state["reason"] = "gate-path-not-absolute"
    elif state["symlink"]:
        state["reason"] = "gate-symlink-refused"
    elif not state["exists"]:
        state["reason"] = "gate-missing"
    elif not state["regular"]:
        state["reason"] = "gate-not-regular"
    elif state["sha256"] is None:
        state["reason"] = "gate-unreadable"
    return state


def invoke_gate(gate, root, record_path):
    command = [sys.executable, str(gate), "--root", str(root), "--record", str(record_path)]
    started = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            command,
            cwd=str(LANE),
            capture_output=True,
            text=True,
            timeout=GATE_TIMEOUT,
            env=GATE_ENV,
        )
        code = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
    except subprocess.TimeoutExpired as exc:
        code = 124
        timed_out = True
        stdout = as_text(exc.stdout)
        stderr = as_text(exc.stderr) + "\nR14_GATE_TIMEOUT\n"
    except OSError as exc:
        code = 126
        stdout = ""
        stderr = "invocation failed: %s\n" % exc
    combined = stdout + "\n" + stderr
    finding_ids = sorted(set(FINDING_PATTERN.findall(combined)))
    finding_lines = [line for line in combined.splitlines() if line.startswith("finding ")]
    trimmed_out, out_cut = trim(stdout)
    trimmed_err, err_cut = trim(stderr)
    commit, commit_error = git_head()
    return {
        "command": command,
        "exit_code": code,
        "timed_out": timed_out,
        "findings": finding_ids,
        "finding_lines": finding_lines,
        "stdout": trimmed_out,
        "stdout_truncated": out_cut,
        "stderr": trimmed_err,
        "stderr_truncated": err_cut,
        "seconds": round(time.monotonic() - started, 3),
        "measured_commit": commit,
        "measured_commit_error": commit_error,
    }


def load_baseline_run(commit):
    """Extract the named baseline runner and compile only its top-level run()."""
    try:
        source_proc = subprocess.run(
            ["git", "-C", str(LANE), "show", "%s:%s" % (commit, BASELINE_RUNNER)],
            capture_output=True,
            text=True,
            timeout=60,
            env=GIT_ENV,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DemoBlocked("baseline-unavailable", {"commit": commit, "error": str(exc)})
    if source_proc.returncode != 0:
        raise DemoBlocked(
            "baseline-unavailable",
            {
                "commit": commit,
                "path": BASELINE_RUNNER,
                "exit_code": source_proc.returncode,
                "stderr": (source_proc.stderr or "").strip()[:2048],
            },
        )
    source = source_proc.stdout
    try:
        tree = ast.parse(source, filename="%s@%s" % (BASELINE_RUNNER, commit))
    except SyntaxError as exc:
        raise DemoBlocked("baseline-unparseable", {"commit": commit, "error": str(exc)})
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run"]
    if len(definitions) != 1:
        raise DemoBlocked("baseline-run-definition-ambiguous", {"commit": commit, "count": len(definitions)})
    module = ast.Module(body=[definitions[0]], type_ignores=[])
    ast.fix_missing_locations(module)
    return source, compile(module, "%s@%s" % (BASELINE_RUNNER, commit), "exec")


class ForbiddenSubprocess:
    """Tripwire: the baseline retention branch must never reach a subprocess."""

    PIPE = -1

    class TimeoutExpired(Exception):
        pass

    @staticmethod
    def Popen(*args, **kwargs):
        raise AssertionError("baseline retention branch executed a subprocess")


def load_migrated_caller():
    """Import the migrated runner read-only and return its module.

    The import runs with argv reset to the module path so no caller flag is
    parsed; module import defines functions and constants only, writes
    nothing, and does not run the runner's suite. Its retention decision
    function is then called directly with in-memory records.
    """
    module_path = LANE / BASELINE_RUNNER
    spec = importlib.util.spec_from_file_location("souji_r13_runner_r14", str(module_path))
    if spec is None or spec.loader is None:
        raise DemoBlocked("migrated-caller-unavailable", {"path": str(module_path)})
    module = importlib.util.module_from_spec(spec)
    previous_argv = list(sys.argv)
    try:
        # Import must never see the demonstration's own flags.
        sys.argv = [str(module_path)]
        spec.loader.exec_module(module)
    except Exception as exc:
        raise DemoBlocked(
            "migrated-caller-unloadable",
            {"path": str(module_path), "error": "%s: %s" % (type(exc).__name__, exc)},
        )
    finally:
        sys.argv = previous_argv
    return module


def summarize_reuse(outcome):
    retained, evidence = outcome
    return {
        "retained": retained is not None,
        "gate_exit": evidence.get("exit_code"),
        "reusable": evidence.get("reusable"),
        "findings": evidence.get("findings"),
        "reason": evidence.get("reason"),
    }


def run_demonstration(gate, gate_state, base, initial_commit):
    base_real = Path(os.path.realpath(str(base)))
    var_tmp_real = Path(os.path.realpath(TMP_BASE))
    root = base / "root"
    results_dir = base / "results"
    records_dir = base / "records"
    try:
        for directory in (root, results_dir, records_dir):
            directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise DemoBlocked("isolation-directory-unavailable", {"error": str(exc)})
    root_real = Path(os.path.realpath(str(root)))
    baseline_source, baseline_code = load_baseline_run(BASELINE_COMMIT)
    migrated_module = load_migrated_caller()
    # gate_reuse resolves records against the module's ROOT; rebind it to the
    # isolated fixture so the same synthetic record is evaluated authentically.
    # GATE stays the absolute installed gate path.
    migrated_module.ROOT = root

    for relative, contents in FIXTURE.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(contents)

    executions = []
    cases = []

    def inspect_dependencies():
        observed = {}
        for relative in DEPENDENCY_ORDER:
            path = root / relative
            if path.is_symlink():
                raise DemoBlocked("dependency-symlink-refused", {"path": relative})
            resolved = Path(os.path.realpath(str(path)))
            if resolved == root_real or not within(root_real, resolved):
                raise DemoBlocked("dependency-escape-refused", {"path": relative, "resolved": str(resolved)})
            if not resolved.is_file():
                raise DemoBlocked("dependency-not-regular", {"path": relative})
            observed[relative] = sha256_file(resolved)
        return observed

    def producer(phase):
        commit_now, commit_error = git_head()
        if commit_now is None:
            raise DemoBlocked("measured-commit-unavailable", {"phase": phase, "error": commit_error})
        observed = inspect_dependencies()
        command = [sys.executable, "-c", PRODUCER_CODE, str(root), *DEPENDENCY_ORDER]
        expected_stdout = "r14-producer " + " ".join(
            "%s=%s" % (relative, observed[relative]) for relative in DEPENDENCY_ORDER
        ) + "\n"
        started = time.monotonic()
        timed_out = False
        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                env=GATE_ENV,
            )
            exit_code = proc.returncode
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
        except subprocess.TimeoutExpired as exc:
            exit_code = 124
            timed_out = True
            stdout = as_text(exc.stdout)
            stderr = as_text(exc.stderr) + "\nR14_PRODUCER_TIMEOUT\n"
        except OSError as exc:
            exit_code = 126
            stdout = ""
            stderr = "producer invocation failed: %s\n" % exc
        seconds = round(time.monotonic() - started, 3)
        observed_after = inspect_dependencies()
        dependencies_stable = observed == observed_after
        stdout_stable = stdout == expected_stdout
        matched = exit_code == 0 and stdout_stable
        producer_evidence = {
            "command": command,
            "exit_code": exit_code,
            "expected_stdout": expected_stdout,
            "stdout": stdout,
            "stderr": stderr,
            "stdout_stable": stdout_stable,
            "dependencies_stable": dependencies_stable,
            "timed_out": timed_out,
            "seconds": seconds,
        }
        execution = {
            "execution_index": len(executions) + 1,
            "phase": phase,
            "measured_commit": commit_now,
            "harness_revision": commit_now,
            "dependencies": observed_after,
            "dependencies_stable": dependencies_stable,
            "producer": producer_evidence,
            "produced_at": utc_now(),
        }
        executions.append(execution)
        result = {
            "name": NAME,
            "matched": matched,
            "measured_commit": commit_now,
            "harness_revision": commit_now,
            "dependencies": dict(observed_after),
            "dependencies_stable": dependencies_stable,
            "result_origin": "fresh-execution",
            "producer_executed": True,
            "producer_kind": "harmless isolated subprocess; matched from actual exit 0 and exact expected stdout",
            "measured_commit_scope": "harness revision only; the /var/tmp synthetic dependency bytes are not tracked at that commit",
            "producer": producer_evidence,
        }
        write_json(
            results_dir / ("%02d-%s.json" % (execution["execution_index"], phase)),
            {"result": result, "execution": execution},
        )
        return result, execution

    def reuse(record_path):
        evidence = invoke_gate(gate, root, record_path)
        decision = {
            "record": str(record_path),
            "record_sha256": sha256_file(record_path),
            "gate_exit": evidence["exit_code"],
            "reusable": evidence["exit_code"] == 0,
            "findings": evidence["findings"],
            "evidence": evidence,
        }
        return decision

    def apply_policy(phase, decision, record, prior_result):
        if (decision["reusable"] and prior_result is not None
                and prior_result.get("dependencies_stable") is True):
            retained = dict(prior_result)
            retained.update(
                {
                    "result_origin": "retained-from-record",
                    "producer_executed": False,
                    "measured_commit": record["measured_commit"],
                    "measured_commit_source": "record",
                    "measured_commit_scope": "preserved from the record's original observation; the declared dependency bytes are not contained in that lane commit",
                    "dependencies": dict(record.get("dependencies") or {}),
                    "eligibility": {
                        "gate_exit": decision["gate_exit"],
                        "findings": decision["findings"],
                    },
                }
            )
            return retained, None
        return producer(phase)

    def make_case(phase, record_path, declared, observed, decision, result, execution):
        match = isinstance(declared.get("dependencies"), dict) and declared["dependencies"] == observed
        return {
            "phase": phase,
            "record": str(record_path),
            "record_sha256": sha256_file(record_path),
            "declared": declared,
            "observed_dependencies": observed,
            "declared_dependency_digests_match": match,
            "gate": None if decision is None else decision["evidence"],
            "gate_exit": None if decision is None else decision["gate_exit"],
            "reusable": None if decision is None else decision["reusable"],
            "result": result,
            "retained": result.get("result_origin") == "retained-from-record",
            "producer_execution": execution,
            "executions_after": len(executions),
        }

    def build_record(result, include_dependencies=True):
        record = {
            "name": result["name"],
            "matched": result["matched"],
            "measured_commit": result["measured_commit"],
        }
        if include_dependencies:
            record["dependencies"] = dict(result["dependencies"])
        return record

    def old_policy_reuse(record, prior_result):
        return record.get("matched") is True and prior_result is not None

    initial_result, initial_execution = producer("initial-fresh")
    record_one = build_record(initial_result)
    record_path = records_dir / "record.json"
    write_json(record_path, record_one)
    record_sha_initial = sha256_file(record_path)
    observed_initial = initial_result["dependencies"]
    declared_initial = json.loads(record_path.read_text(encoding="utf-8"))
    cases.append(
        make_case(
            "initial-fresh",
            record_path,
            declared_initial,
            observed_initial,
            None,
            initial_result,
            initial_execution,
        )
    )

    observed_unchanged = inspect_dependencies()
    declaration_unchanged = json.loads(record_path.read_text(encoding="utf-8"))
    decision_unchanged = reuse(record_path)
    result_unchanged, execution_unchanged = apply_policy(
        "unchanged-recheck", decision_unchanged, declaration_unchanged, initial_result
    )
    cases.append(
        make_case(
            "unchanged",
            record_path,
            declaration_unchanged,
            observed_unchanged,
            decision_unchanged,
            result_unchanged,
            execution_unchanged,
        )
    )

    migrated_unchanged = summarize_reuse(migrated_module.attempt_reuse(NAME, dict(initial_result)))

    mutation = {
        "path": "observations/beta.txt",
        "marker": MUTATION_MARKER.decode("utf-8"),
        "before": None,
        "after": None,
    }
    mutation["before"] = {
        "sha256": sha256_file(root / "observations/beta.txt"),
        "size_bytes": (root / "observations/beta.txt").stat().st_size,
    }
    with (root / "observations/beta.txt").open("ab") as handle:
        handle.write(MUTATION_MARKER)
    mutation["after"] = {
        "sha256": sha256_file(root / "observations/beta.txt"),
        "size_bytes": (root / "observations/beta.txt").stat().st_size,
    }
    observed_modified = inspect_dependencies()
    declaration_modified = json.loads(record_path.read_text(encoding="utf-8"))
    gate_sha_after_first = sha256_file(gate)
    record_sha_before_modified = sha256_file(record_path)
    alpha_unchanged = observed_modified["observations/alpha.txt"] == observed_initial["observations/alpha.txt"]
    record_unchanged = record_sha_before_modified == record_sha_initial
    gate_unchanged = gate_sha_after_first == gate_state["sha256"]
    decision_modified = reuse(record_path)
    result_modified, execution_modified = apply_policy(
        "dependency-modified", decision_modified, declaration_modified, result_unchanged
    )
    cases.append(
        make_case(
            "dependency-modified",
            record_path,
            declaration_modified,
            observed_modified,
            decision_modified,
            result_modified,
            execution_modified,
        )
    )

    migrated_stale = summarize_reuse(migrated_module.attempt_reuse(NAME, dict(initial_result)))
    migrated_legacy = summarize_reuse(migrated_module.attempt_reuse(NAME, {
        "name": NAME,
        "matched": True,
        "measured_commit": declaration_modified["measured_commit"],
        "dependencies_stable": True,
    }))
    migrated_missing_revision = summarize_reuse(migrated_module.attempt_reuse(NAME, {
        "name": NAME,
        "matched": True,
        "dependencies_stable": True,
        "dependencies": dict(declaration_modified["dependencies"]),
    }))
    migrated_unstable = summarize_reuse(migrated_module.attempt_reuse(NAME, dict(
        initial_result, dependencies_stable=False)))
    migrated_external = summarize_reuse(migrated_module.attempt_reuse(
        "sources-contract", dict(initial_result)))
    migrated_caller = {
        "module": BASELINE_RUNNER,
        "entry": "attempt_reuse(name, prior) executed from the migrated module; run()'s full command suite is not invoked",
        "historical_outputs_read_only": True,
        "gate": str(migrated_module.GATE),
        "root": str(migrated_module.ROOT),
        "root_rebound_to_fixture": migrated_module.ROOT == root,
        "gate_label_decoupled": True,
        "unchanged": migrated_unchanged,
        "stale": migrated_stale,
        "legacy": migrated_legacy,
        "missing_revision": migrated_missing_revision,
        "unstable_capture": migrated_unstable,
        "external_mutable": migrated_external,
    }

    baseline_marker = base / "baseline-producer-marker.txt"
    baseline_command = [
        sys.executable,
        "-c",
        "import pathlib, sys; pathlib.Path(sys.argv[1]).write_text('baseline producer ran')\n",
        str(baseline_marker),
    ]
    baseline_namespace = {
        "PREVIOUS": {"measured_commit": declaration_modified["measured_commit"]},
        "PREVIOUS_RESULTS": {SYNTHETIC_NAME: dict(result_unchanged)},
        "RETRY_NAMES": set(),
        "CURRENT_REV": initial_commit,
        "ROOT": LANE,
        "ENV": GATE_ENV,
        "subprocess": ForbiddenSubprocess,
        "os": os,
        "signal": signal,
        "sys": sys,
        "time": time,
    }
    exec(baseline_code, baseline_namespace)
    baseline_run = baseline_namespace["run"]
    baseline_stream = io.StringIO()
    baseline_result = None
    baseline_error = None
    try:
        with contextlib.redirect_stdout(baseline_stream):
            baseline_result = baseline_run(SYNTHETIC_NAME, baseline_command, expected=0)
    except Exception as exc:
        baseline_error = "%s: %s" % (type(exc).__name__, exc)
    baseline_marker_exists = baseline_marker.exists()
    baseline_retained = isinstance(baseline_result, dict) and bool(baseline_result.get("retained_from"))
    baseline_no_producer = (
        baseline_error is None
        and isinstance(baseline_result, dict)
        and not baseline_marker_exists
        and "exit_code" not in baseline_result
    )
    baseline_commit_preserved = (
        isinstance(baseline_result, dict)
        and baseline_result.get("measured_commit") == declaration_modified["measured_commit"]
    )
    baseline_stdout, baseline_stdout_truncated = trim(baseline_stream.getvalue())
    baseline_stale = observed_modified != declaration_modified["dependencies"]
    baseline_control = {
        "commit": BASELINE_COMMIT,
        "path": BASELINE_RUNNER,
        "source_sha256": hashlib.sha256(baseline_source.encode("utf-8")).hexdigest(),
        "extraction": "git show <commit>:<path>; ast.parse; top-level run() FunctionDef compiled and executed against synthetic module globals",
        "synthetic_record": {
            "name": SYNTHETIC_NAME,
            "record": str(record_path),
            "record_sha256": sha256_file(record_path),
            "declared_dependencies": declaration_modified["dependencies"],
            "observed_dependencies": observed_modified,
            "declared_dependency_digests_match": observed_modified == declaration_modified["dependencies"],
        },
        "command_not_allowed_to_run": baseline_command,
        "producer_marker": str(baseline_marker),
        "producer_marker_exists": baseline_marker_exists,
        "subprocess_tripwire": "subprocess.Popen raises if the baseline retention branch attempts execution",
        "error": baseline_error,
        "stdout": baseline_stdout,
        "stdout_truncated": baseline_stdout_truncated,
        "returned": baseline_result,
        "retained": baseline_retained,
        "retained_from": baseline_result.get("retained_from") if isinstance(baseline_result, dict) else None,
        "preserved_measured_commit": baseline_commit_preserved,
        "no_producer_execution": baseline_no_producer,
        "stale_declared_dependency_mismatch": baseline_stale,
        "new_caller": {
            "record": str(record_path),
            "record_sha256": sha256_file(record_path),
            "gate_exit": decision_modified["gate_exit"],
            "findings": decision_modified["findings"],
            "reused": decision_modified["reusable"],
            "executed_producer": execution_modified is not None,
            "execution_index": execution_modified["execution_index"] if execution_modified else None,
            "fresh_measured_commit": result_modified["measured_commit"],
        },
    }

    legacy_record = {
        "name": NAME,
        "matched": result_modified["matched"],
        "measured_commit": result_modified["measured_commit"],
    }
    legacy_path = records_dir / "record-legacy.json"
    write_json(legacy_path, legacy_record)
    observed_legacy = inspect_dependencies()
    declaration_legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    decision_legacy = reuse(legacy_path)
    result_legacy, execution_legacy = apply_policy(
        "legacy-no-dependencies", decision_legacy, declaration_legacy, result_modified
    )
    cases.append(
        make_case(
            "legacy-no-dependencies",
            legacy_path,
            declaration_legacy,
            observed_legacy,
            decision_legacy,
            result_legacy,
            execution_legacy,
        )
    )

    verification_path = LANE / "census/round-13/verification.json"
    historical_entries = []
    if verification_path.is_file() and not verification_path.is_symlink():
        historical = json.loads(verification_path.read_text(encoding="utf-8"))
        for index, prior in enumerate(historical.get("results", [])):
            if "retained_from" not in prior:
                continue
            historical_record = {
                "name": "round-13:%s" % prior.get("name", "unknown"),
                "matched": prior.get("matched") is True,
                "measured_commit": prior.get("measured_commit"),
            }
            historical_path = records_dir / ("historical-legacy-%02d.json" % index)
            write_json(historical_path, historical_record)
            historical_decision = reuse(historical_path)
            historical_entries.append(
                {
                    "source": str(verification_path.relative_to(LANE)),
                    "source_result": prior.get("name"),
                    "source_retained_from": prior.get("retained_from"),
                    "source_measured_commit": prior.get("measured_commit"),
                    "source_dependencies_absent": "dependencies" not in prior,
                    "record": str(historical_path),
                    "record_sha256": sha256_file(historical_path),
                    "gate_exit": historical_decision["gate_exit"],
                    "findings": historical_decision["findings"],
                    "reusable": historical_decision["reusable"],
                }
            )
    historical_legacy = {
        "policy": "historical retained greens are read and refused, never rewritten",
        "source": str(verification_path.relative_to(LANE)) if verification_path.is_file() else None,
        "records": historical_entries,
        "all_refused": bool(historical_entries) and all(
            item["gate_exit"] == 2 and tuple(item["findings"]) == EXPECTED_LEGACY_FINDINGS
            for item in historical_entries
        ),
    }

    gate_sha_final = sha256_file(gate)
    record_sha_final = sha256_file(record_path)
    disk_executions = sorted(path.name for path in results_dir.glob("*.json"))
    stale_declared_mismatch = observed_modified != declaration_modified["dependencies"]
    stale_would_retain = old_policy_reuse(declaration_unchanged, result_unchanged)
    legacy_would_retain = old_policy_reuse(declaration_legacy, result_modified)
    new_policy_executions = len(executions)
    old_policy_executions = 1

    control = {
        "policy": "retain when record.matched is true; no dependency-digest recheck",
        "hypothetical": True,
        "stale_case": {
            "record": str(record_path),
            "record_matched": declaration_unchanged["matched"],
            "gate_exit": decision_modified["gate_exit"],
            "gate_reusable": decision_modified["reusable"],
            "would_retain": stale_would_retain,
            "retained_measured_commit": result_unchanged["measured_commit"],
            "observed_declared_dependency_mismatch": stale_declared_mismatch,
            "new_policy_producer_executions": new_policy_executions,
            "old_policy_producer_executions": old_policy_executions,
        },
        "legacy_case": {
            "record": str(legacy_path),
            "record_matched": declaration_legacy["matched"],
            "gate_exit": decision_legacy["gate_exit"],
            "gate_reusable": decision_legacy["reusable"],
            "would_retain": legacy_would_retain,
            "digest_basis": "absent",
            "new_policy_producer_executions": new_policy_executions,
            "old_policy_producer_executions": old_policy_executions,
        },
    }

    checks = {
        "initial_fresh_once": cases[0]["executions_after"] == 1,
        "producer_actual_subprocess_green": (
            initial_result["matched"] is True
            and initial_result["producer"]["exit_code"] == 0
            and initial_result["producer"]["stdout_stable"] is True
        ),
        "unchanged_gate_exit_zero": decision_unchanged["gate_exit"] == 0,
        "unchanged_gate_status_reusable": (
            decision_unchanged["findings"] == []
            and REUSABLE_STATUS in decision_unchanged["evidence"]["stdout"]
            and ("measured_commit: " + declaration_unchanged["measured_commit"])
            in decision_unchanged["evidence"]["stdout"]
        ),
        "changed_dependency_exact_finding": (
            tuple(decision_modified["findings"]) == EXPECTED_STALE_FINDINGS
            and STALE_STATUS in decision_modified["evidence"]["stdout"]
        ),
        "legacy_exact_finding": (
            tuple(decision_legacy["findings"]) == EXPECTED_LEGACY_FINDINGS
            and COULD_NOT_EVALUATE_STATUS in decision_legacy["evidence"]["stdout"]
        ),
        "unchanged_reused_without_producer": (
            decision_unchanged["reusable"]
            and execution_unchanged is None
            and cases[1]["executions_after"] == 1
        ),
        "unchanged_retained_measured_commit": (
            cases[1]["retained"]
            and result_unchanged["measured_commit"] == declaration_unchanged["measured_commit"]
            and result_unchanged.get("measured_commit_source") == "record"
        ),
        "changed_dependency_gate_exit_one": decision_modified["gate_exit"] == 1,
        "changed_dependency_not_reused": (
            not decision_modified["reusable"] and result_modified["result_origin"] == "fresh-execution"
        ),
        "changed_dependency_producer_executed": execution_modified is not None and cases[2]["executions_after"] == 2,
        "changed_dependency_fresh_digests": (
            result_modified["dependencies"]["observations/beta.txt"] == mutation["after"]["sha256"]
            and observed_modified == result_modified["dependencies"]
        ),
        "legacy_gate_exit_two": decision_legacy["gate_exit"] == 2,
        "legacy_not_reused": (
            not decision_legacy["reusable"] and result_legacy["result_origin"] == "fresh-execution"
        ),
        "legacy_producer_executed": execution_legacy is not None and cases[3]["executions_after"] == 3,
        "legacy_fresh_digests": result_legacy["dependencies"] == observed_legacy,
        "only_declared_dependency_changed": (
            alpha_unchanged
            and record_unchanged
            and gate_unchanged
            and mutation["before"]["sha256"] != mutation["after"]["sha256"]
        ),
        "record_bytes_unchanged": record_sha_final == record_sha_initial,
        "gate_digest_recorded_and_unchanged": (
            bool(gate_state["sha256"]) and gate_sha_final == gate_state["sha256"]
        ),
        "execution_log_matches_disk": len(disk_executions) == new_policy_executions,
        "isolation_confined": (
            base_real.parent == var_tmp_real
            and root_real.parent == base_real
            and not any(path.is_symlink() for path in base.rglob("*"))
        ),
        "unsafe_control_would_retain_stale_green": (
            stale_would_retain
            and not decision_modified["reusable"]
            and stale_declared_mismatch
        ),
        "unsafe_control_would_retain_legacy_green": legacy_would_retain and not decision_legacy["reusable"],
        "baseline_authentic_retention": (
            baseline_retained
            and baseline_no_producer
            and baseline_commit_preserved
            and baseline_error is None
        ),
        "baseline_stale_green_reused": (
            baseline_retained and baseline_stale and not baseline_marker_exists
        ),
        "new_caller_refused_same_record_and_reexecuted": (
            decision_modified["gate_exit"] == 1
            and not decision_modified["reusable"]
            and execution_modified is not None
        ),
        "historical_legacy_records_refused": historical_legacy["all_refused"],
        "migrated_caller_reuses_unchanged": (
            migrated_unchanged["retained"] and migrated_unchanged["gate_exit"] == 0
        ),
        "migrated_caller_refuses_stale": (
            not migrated_stale["retained"]
            and migrated_stale["gate_exit"] == 1
            and tuple(migrated_stale["findings"]) == EXPECTED_STALE_FINDINGS
        ),
        "migrated_caller_refuses_legacy": migrated_legacy["reason"] == "prior-dependencies-legacy",
        "migrated_caller_refuses_missing_revision": (
            migrated_missing_revision["reason"] == "prior-measured-commit-missing"
        ),
        "migrated_caller_refuses_unstable": migrated_unstable["reason"] == "prior-dependencies-unstable",
        "migrated_caller_reruns_external_mutable": (
            migrated_external["reason"] == "external-mutable-command"
        ),
    }

    advisories = []
    if decision_modified["gate_exit"] == 1 and not decision_modified["findings"]:
        advisories.append("stale-exit-without-named-finding")
    if decision_legacy["gate_exit"] == 2 and not decision_legacy["findings"]:
        advisories.append("legacy-exit-without-named-finding")
    if decision_unchanged["gate_exit"] == 0 and decision_unchanged["findings"]:
        advisories.append("reusable-with-findings")
    invocation_commits = {
        decision["evidence"]["measured_commit"] for decision in (decision_unchanged, decision_modified, decision_legacy)
    }
    if len(invocation_commits) > 1:
        advisories.append("head-changed-between-gate-invocations")

    return {
        "schema": "souji-r14-cache-demonstration-v1",
        "demonstration": "digest-bound-retention",
        "status": "ok" if all(checks.values()) else "red",
        "measured_commit": initial_commit,
        "measured_commit_basis": "git -C lane rev-parse --verify HEAD at demonstration start",
        "observed_at": utc_now(),
        "consumer": {
            "role": "C1 digest-bound retention consumer for current-round evidence collection",
            "supported_current_round_consumer": True,
            "historical_runner": "census/round-13/run-verification.py",
            "historical_runner_code_migration": "its --retry-failed retention branch consults this gate; historical JSON outputs are not rewritten",
            "historical_json_outputs_rewritten": False,
            "old_policy_precondition": "retained-green selected without comparing dependency digests",
        },
        "producer_kind": "harmless isolated subprocess; green derived from actual exit 0 and stable stdout",
        "harness_revision": initial_commit,
        "measured_commit_scope": "lane HEAD is recorded as harness_revision only; synthetic /var/tmp dependency bytes and the gate file are not contained in that commit",
        "baseline_control": baseline_control,
        "historical_legacy": historical_legacy,
        "migrated_caller": migrated_caller,
        "retention_policy": {
            "reuse": "only when the installed gate exits 0",
            "reexecute": "gate exit 1 (stale), 2 (malformed/legacy/could-not-evaluate), or any other non-zero",
            "measured_commit": "every producer result keeps its own measured_commit; a retained result preserves the record's measured_commit and is marked result_origin=retained-from-record",
        },
        "gate": gate_state,
        "gate_sha256_after": gate_sha_final,
        "isolation": {
            "base": str(base),
            "root": str(root),
            "results": str(results_dir),
            "records": str(records_dir),
            "under_var_tmp": base_real.parent == var_tmp_real,
            "fixture_files": sorted(FIXTURE),
        },
        "record": {
            "path": str(record_path),
            "sha256_initial": record_sha_initial,
            "sha256_final": record_sha_final,
            "unchanged": record_sha_final == record_sha_initial,
            "declared": declaration_unchanged,
        },
        "dependency_mutation": {
            "path": mutation["path"],
            "marker": mutation["marker"],
            "before": mutation["before"],
            "after": mutation["after"],
            "alpha_unchanged": alpha_unchanged,
            "record_unchanged": record_unchanged,
            "gate_unchanged": gate_unchanged,
        },
        "cases": cases,
        "unsafe_policy_control": control,
        "executions": executions,
        "producer_executions_new_policy": new_policy_executions,
        "producer_executions_old_policy": old_policy_executions,
        "checks": checks,
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "advisories": advisories,
        "limitations": [
            "Synthetic bytes under /var/tmp only; no production evidence is read, moved, or deleted.",
            "The producer is an actual harmless subprocess reading only the isolated fixture; its matched flag comes from exit 0 plus exact stdout equality. It proves the fixture observation, not production work.",
            "Lane HEAD is labelled harness_revision; synthetic dependency bytes and the gate file are not contained in that commit, and no historical execution is proven or re-executed.",
            "Demonstrates the consumer policy and the gate's eligibility decisions on this fixture; it does not prove historical runner execution or historical result provenance.",
            "The baseline control executes only the actual retention branch of run() from the pinned baseline commit; it does not execute that runner's commands.",
            "The migrated runner is imported read-only and its attempt_reuse decision is executed directly; its full command suite is not run and no historical JSON output is rewritten.",
            "Historical retained greens are read from census/round-13/verification.json and refused; those files are not rewritten.",
            "Finding ids are parsed from gate output and the stale/legacy cases assert the exact ids; only documented exit codes 0/1/2 drive reuse.",
            "Certification is OFF; this is not deletion authorization and not a complete-class-suite recertification.",
        ],
        "deletion_certification": "OFF",
    }


def blocked_payload(reason, detail, gate_state, cases, observed_at):
    payload = {
        "schema": "souji-r14-cache-demonstration-v1",
        "demonstration": "digest-bound-retention",
        "status": "blocked",
        "reason": reason,
        "detail": detail,
        "observed_at": observed_at,
        "gate": gate_state,
        "cases_observed": cases,
        "deletion_certification": "OFF",
    }
    return payload


def cleanup(base, keep):
    if keep:
        return {
            "kept": True,
            "cleaned": False,
            "residue": [str(base)],
        }
    shutil.rmtree(base, ignore_errors=True)
    cleaned = not base.exists()
    residue = []
    if base.exists():
        try:
            residue = sorted(str(path) for path in base.rglob("*"))[:64]
        except OSError:
            residue = [str(base)]
    return {
        "kept": False,
        "cleaned": cleaned,
        "residue": residue,
    }


def emit(payload, code):
    print(json.dumps(payload, indent=2, sort_keys=True))
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--gate",
        default=str(DEFAULT_GATE),
        help="installed gate path to consume (default: %(default)s)",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="keep the isolated /var/tmp tree for inspection instead of removing it",
    )
    args = parser.parse_args(argv)

    observed_at = utc_now()
    gate = Path(args.gate)
    gate_state = inspect_gate(gate)
    if gate_state["reason"] is not None:
        return emit(
            blocked_payload(
                gate_state["reason"],
                {
                    "gate": str(gate),
                    "installed_default": str(DEFAULT_GATE),
                    "note": "the installed C1 gate must exist as a regular non-symlink file",
                },
                gate_state,
                [],
                observed_at,
            ),
            2,
        )

    initial_commit, commit_error = git_head()
    if initial_commit is None:
        print("cache-demonstration: refused: %s (no record written)" % commit_error,
              file=sys.stderr)
        return 2

    try:
        base = Path(tempfile.mkdtemp(prefix="souji-r14-cache-demo.", dir=TMP_BASE))
    except OSError as exc:
        return emit(
            blocked_payload(
                "isolation-unavailable",
                {"error": str(exc), "tmp_base": TMP_BASE},
                gate_state,
                [],
                observed_at,
            ),
            2,
        )

    base_real = Path(os.path.realpath(str(base)))
    var_tmp_real = Path(os.path.realpath(TMP_BASE))
    if base_real.parent != var_tmp_real:
        cleanup(base, keep=False)
        return emit(
            blocked_payload(
                "isolation-not-under-var-tmp",
                {"base": str(base), "resolved": str(base_real)},
                gate_state,
                [],
                observed_at,
            ),
            2,
        )

    payload = None
    code = 2
    try:
        try:
            payload = run_demonstration(gate, gate_state, base, initial_commit)
            code = 0 if payload["status"] == "ok" else 1
        except DemoBlocked as exc:
            payload = blocked_payload(exc.reason, exc.detail, gate_state, [], observed_at)
            code = 2
        except Exception:
            payload = blocked_payload(
                "unexpected-error",
                {"traceback": traceback.format_exc(limit=4)},
                gate_state,
                [],
                observed_at,
            )
            code = 2
    finally:
        state = cleanup(base, keep=args.keep)

    payload.setdefault("isolation", {})
    payload["isolation"].update(state)
    if payload["status"] == "ok" and not state["cleaned"]:
        payload["status"] = "red"
        payload.setdefault("checks", {})["isolation_cleaned"] = False
        payload.setdefault("failed_checks", []).append("isolation_cleaned")
        code = 1
    payload["gate"]["sha256_after"] = (
        sha256_file(gate) if gate.is_file() and not gate.is_symlink() else None
    )
    final_commit, final_error = git_head()
    if final_commit != initial_commit or final_error is not None:
        print("cache-demonstration: refused measured input drift: %s (no record written)"
              % final_error, file=sys.stderr)
        return 2
    payload["input_sha256"] = DEMO_INPUT_SHA256
    payload["inputs_unchanged_during_run"] = True
    payload["input_scope"] = ("Owned repository files only; external commands, host state, "
                              "configuration and environment are not attested.")
    return emit(payload, code)


if __name__ == "__main__":
    sys.exit(main())
