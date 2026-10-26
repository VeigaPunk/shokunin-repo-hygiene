#!/usr/bin/env python3
"""Measure only corrected failures and green checks whose measured bytes changed.

Earlier observations stay in verification-attempt-1.json at their own revision;
this does not reuse or relabel them as new executions.
"""
import datetime
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
# The imported producer is itself a measured input. Verify its bytes before
# importing it so a dirty, syntax-invalid wrapper cannot escape as exit 1.
_BOOT_ENV = {key: value for key, value in os.environ.items()
             if not key.startswith("GIT_")}
_BOOT_ENV.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
                 GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1",
                 GIT_NO_REPLACE_OBJECTS="1", GIT_TERMINAL_PROMPT="0", LC_ALL="C")
_BOOT_GIT = ["git", "-C", str(ROOT), "-c", "maintenance.auto=false",
             "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null"]
_VERIFIER = "census/round-14/run-verification.py"
try:
    verifier = ROOT / _VERIFIER
    if (any(path.is_symlink() for path in
            (ROOT / "census", verifier.parent, verifier)) or not verifier.is_file()):
        raise ValueError("nonregular imported verifier " + _VERIFIER)
    head = subprocess.check_output(_BOOT_GIT + ["rev-parse", "HEAD"],
                                   env=_BOOT_ENV).decode().strip()
    expected = subprocess.check_output(_BOOT_GIT + ["show", head + ":" + _VERIFIER],
                                       env=_BOOT_ENV)
    if verifier.read_bytes() != expected:
        raise ValueError(_VERIFIER + " differs from measured commit")
    spec = importlib.util.spec_from_file_location("r14_verify", verifier)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
except (OSError, ValueError, SyntaxError, ImportError, subprocess.CalledProcessError) as exc:
    print("run-targeted: refused importing %s: %s (no record written)"
          % (_VERIFIER, exc), file=sys.stderr)
    raise SystemExit(2)

def main():
    target = module.output_path()
    prior = ROOT/"census/round-14/verification-attempt-1.json"
    module.MEASURED_PATHS = [*module.MEASURED_PATHS,
                             "census/round-14/verification-attempt-1.json"]
    revision = module.resolve_revision()
    paths = ["tools/souji-evidence-cache.py", "tools/souji-census.sh",
             "tests/fixtures/r14-evidence-cache.py", "tests/fixtures/r14-census-boundary.py",
             "census/round-14/cache-demonstration.py", "census/round-13/run-verification.py"]
    before = {p: module.sha(ROOT/p) for p in paths}
    historical_before = module.sha(ROOT/"census/round-13/verification.json")
    with tempfile.TemporaryDirectory(prefix="souji-r14-targeted-", dir=tempfile.gettempdir()) as temp:
        baseline = Path(temp)/"souji-census.sh"
        baseline.write_bytes(subprocess.check_output(["git", "-C", str(ROOT), "show", module.BASE+":tools/souji-census.sh"], env=module.ENV))
        baseline.chmod(0o700)
        commands = [
            ("cache-consumer-red-green", ["python3", "-B", "census/round-14/cache-demonstration.py"], 0),
            ("historical-runner-default-refusal", ["python3", "-B", "census/round-13/run-verification.py"], 2),
            ("census-boundary-red-before", ["python3", "-B", "tests/fixtures/r14-census-boundary.py", "--tool", str(baseline)], 1),
            ("census-boundary", ["python3", "-B", "tests/fixtures/r14-census-boundary.py", "--tool", str(ROOT/"tools/souji-census.sh")], 0),
            ("census-legacy-selftest", ["bash", "tools/souji-census.sh", "--selftest"], 0),
            ("census-shellcheck-warning", ["shellcheck", "-S", "warning", "tools/souji-census.sh"], 0),
        ]
        results = [module.run(name, command, revision, expected) for name, command, expected in commands]
    after = {p: module.sha(ROOT/p) for p in paths}
    historical_after = module.sha(ROOT/"census/round-13/verification.json")
    inputs_after = module.checked_inputs(revision)
    data = dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                measured_commit=revision, baseline_commit=module.BASE, prior_evidence=str(prior.relative_to(ROOT)),
                prior_evidence_sha256=inputs_after[str(prior.relative_to(ROOT))], installed_sha256=after,
                artifacts_unchanged_during_run=before == after,
                input_sha256=inputs_after, inputs_unchanged_during_run=True,
                input_scope="Owned repository files only; external commands, host state, "
                            "configuration and environment are not attested.",
                historical_evidence_unchanged=historical_before == historical_after,
                historical_evidence_sha256=historical_after, results=results,
                policy="Only failed checks or changed-subject checks re-executed; unchanged green observations remain solely in prior evidence with their original revision; no cache retention or revision backfill.",
                scope="Synthetic /var/tmp inputs only; no real credential-store probe, live census, or deletion certification.")
    with target.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(data, indent=2)+"\n")
    return 0 if before == after and historical_before == historical_after and all(r["matched"] for r in results) else 1

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as exc:
        print("run-targeted: refused: %s (no record written)" % exc, file=sys.stderr)
        raise SystemExit(2)
