#!/usr/bin/env python3
"""R20 caller-level input-binding oracle for the R19 C2 rejection.

The fixture copies only each entrypoint's statically declared measured input
closure from --root into isolated synthetic Git repositories under /var/tmp.
It then commits that closure and changes one owned input at a time with an
inert comment/whitespace mutation (or one valid added knowledge record). The
four production callers must refuse each applicable dirty input with exit 2
before suite output or a measurement record is produced.

This fixture is an oracle, not a gate by wiring inspection: it invokes the
actual r13 runner, r14 runner, r14 targeted runner and cache demonstration.
It also probes the revision helper API and runs four historical counter arms
with full commit IDs. With --baseline REV it runs seven bounded old-vs-current
entrypoint pairs, replacing suite producers with a named tripwire; no suite runs.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
TMP_ROOT = Path("/var/tmp")
ROUND13 = "census/round-13/run-verification.py"
ROUND14 = "census/round-14/run-verification.py"
TARGETED = "census/round-14/run-targeted.py"
DEMO = "census/round-14/cache-demonstration.py"
HELPER = "tools/souji-rev-pin.py"
R13_PRIOR = "census/round-13/verification.json"
R14_PRIOR = "census/round-14/verification-attempt-1.json"
R13_FROZEN = "tests/fixtures/r13-cert-frozen/expected.json"
R14_FROZEN = "tests/fixtures/r14-cache-frozen/expected.json"
R13_FROZEN_DIR = "tests/fixtures/r13-cert-frozen"
NEW_KNOWLEDGE = "corpus/knowledge/r20-input-binding-added.md"

# Deliberately minimal: do not inherit credentials, Git repository selectors,
# user config, service settings or other operator environment values.
CLEAN_ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/var/tmp",
    "TMPDIR": "/var/tmp",
    "LC_ALL": "C",
    "PYTHONDONTWRITEBYTECODE": "1",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_NO_LAZY_FETCH": "1",
}
GIT_CONFIG_ARGS = [
    "-c", "maintenance.auto=false",
    "-c", "gc.auto=0",
    "-c", "core.fsmonitor=false",
    "-c", "core.hooksPath=/dev/null",
]
IDENTITY_ARGS = [
    "-c", "user.name=Souji R20 isolated fixture",
    "-c", "user.email=souji-r20-fixture@example.invalid",
    "-c", "commit.gpgsign=false",
]


class FixturePrerequisite(Exception):
    """A required public input or local Git capability is unavailable."""


class Cases:
    def __init__(self):
        self.results: list[tuple[str, bool]] = []
        self.baseline_mismatches = 0
        self.baseline_requested = False

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        clean = " ".join(str(detail).replace("\t", " ").split())
        status = "pass" if ok else "FAIL"
        print("CASE\t%s\t%s\t%s" % (status, name, clean))
        self.results.append((name, ok))

    def baseline(self, path: str, current: str, expected: str) -> None:
        self.baseline_mismatches += 1
        print("BASELINE_MISMATCH\t%s\tcurrent=%s\tbaseline=%s" %
              (path, current, expected))

    def summary(self, blocked: bool = False) -> int:
        failed = sum(not ok for _, ok in self.results)
        passed = len(self.results) - failed
        names = [name for name, _ok in self.results]
        expected = expected_case_ids(self.baseline_requested)
        observed = set(names)
        missing = sorted(expected - observed)
        unexpected = sorted(observed - expected)
        duplicates = len(names) - len(observed)
        inventory_ok = not missing and not unexpected and duplicates == 0
        print("INVENTORY\t%s\texpected=%d observed=%d missing=%s unexpected=%s duplicates=%d" %
              ("exact" if inventory_ok else "FAIL", len(expected), len(names),
               ",".join(missing) or "-", ",".join(unexpected) or "-", duplicates))
        print("SUMMARY\ttotal=%d\tpass=%d\tfail=%d\tblocked=%d\tinventory=%s\tbaseline_mismatches=%s" %
              (len(self.results), passed, failed, int(blocked),
               "exact" if inventory_ok else "mismatch",
               self.baseline_mismatches if self.baseline_requested else "not-requested"))
        return 2 if blocked else (1 if failed or not inventory_ok else 0)
BASELINE_PAIR_CASE_IDS = (
    "baseline-r13-helper",
    "baseline-r13-sources",
    "baseline-r13-new-knowledge",
    "baseline-r14-helper",
    "baseline-r14-frozen",
    "baseline-targeted-wrapper",
    "baseline-demo-helper",
)


def expected_case_ids(include_baseline: bool = False) -> set[str]:
    names = {
        "helper-input-snapshot-clean", "helper-resolve-clean", "helper-head-refuse",
        "helper-branch-refuse", "helper-short-refuse", "helper-keep-only-refuse",
        "helper-walk-error-refuse", "helper-protected-census-ancestor-no-walk",
        "helper-ambient-GIT_DIR-redirection",
        "r13-helper-dirty", "r13-helper-syntax-invalid", "r13-wrapper-dirty",
        "r13-frozen-dirty", "r13-sources-dirty", "r13-admitted-knowledge-dirty",
        "r13-counted-knowledge-added", "r13-optional-prior-dirty",
        "r14-helper-dirty", "r14-helper-syntax-invalid", "r14-wrapper-dirty",
        "r14-frozen-dirty", "r14-sources-dirty",
        "targeted-helper-dirty", "targeted-helper-syntax-invalid", "targeted-wrapper-dirty",
        "targeted-verifier-syntax-invalid", "targeted-frozen-dirty", "targeted-sources-dirty",
        "targeted-prior-attempt-dirty",
        "demo-helper-dirty", "demo-helper-syntax-invalid", "demo-wrapper-dirty",
        "demo-historical-input-dirty",
        "historical-r13-31984f473ce4bdab61a99b16cca194b28108cb81",
        "historical-r13-6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6",
        "historical-r14-a31642d14006830ec62edf40b0354c3699728c4a",
        "historical-r14-552cae4204b3ab818419ad8adbfef3a4da29a3e0",
        "writer-r13-clean", "writer-r14-clean", "writer-targeted-clean",
        "writer-demo-clean", "drift-r13", "drift-r14", "drift-targeted", "drift-demo",
    }
    if include_baseline:
        names.update(BASELINE_PAIR_CASE_IDS)
    return names


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise FixturePrerequisite("measured path is empty or not text")
    raw_parts = value.split("/")
    if value.startswith("/") or any(part in ("", ".", "..") for part in raw_parts):
        raise FixturePrerequisite("measured path is not a canonical repository-relative path")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise FixturePrerequisite("measured path is not a canonical repository-relative path")
    if path.parts[0] in (".git", ".jj"):
        raise FixturePrerequisite("measured path enters repository metadata")
    if path.as_posix() == "census":
        raise FixturePrerequisite("unbounded census ancestor refused")
    if (len(path.parts) > 1 and path.parts[0] == "census"
            and path.parts[1].startswith("operator-sweep-")):
        raise FixturePrerequisite("measured path enters held operator-sweep material")
    return path.as_posix()


def parse_path_list(root: Path, source_path: str, variable: str) -> list[str]:
    source = root / source_path
    if source.is_symlink() or not source.is_file():
        raise FixturePrerequisite("required caller source is absent or non-regular: " + source_path)
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=source_path)
    except (OSError, UnicodeError, SyntaxError) as exc:
        raise FixturePrerequisite("cannot statically read caller source: " + source_path) from exc
    for node in tree.body:
        value = None
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        if any(isinstance(target, ast.Name) and target.id == variable for target in targets):
            try:
                paths = ast.literal_eval(value)
            except (ValueError, TypeError) as exc:
                raise FixturePrerequisite("caller path inventory is not a literal: " + variable) from exc
            if (not isinstance(paths, list) or not paths
                    or any(not isinstance(path, str) for path in paths)):
                raise FixturePrerequisite("caller path inventory has an unsupported shape: " + variable)
            normalized = [safe_relative(path) for path in paths]
            if len(set(normalized)) != len(normalized):
                raise FixturePrerequisite("caller path inventory contains duplicate entries: " + variable)
            return normalized
    raise FixturePrerequisite("caller path inventory is unavailable: " + variable)


def checked_components(root: Path, relative: str) -> Path:
    relative = safe_relative(relative)
    current = root
    try:
        for component in PurePosixPath(relative).parts:
            current = current / component
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise FixturePrerequisite("symlink in bounded input closure: " + relative)
    except OSError as exc:
        raise FixturePrerequisite("missing bounded input path: " + relative) from exc
    return current


def expand_closure(root: Path, paths: list[str]) -> tuple[dict[str, tuple[bytes, int]], set[str]]:
    files: dict[str, tuple[bytes, int]] = {}
    directories: set[str] = set()
    for raw in paths:
        relative = safe_relative(raw)
        source = checked_components(root, relative)
        mode = source.lstat().st_mode
        if stat.S_ISREG(mode):
            files[relative] = (source.read_bytes(), stat.S_IMODE(mode))
            continue
        if not stat.S_ISDIR(mode):
            raise FixturePrerequisite("bounded input is not a regular file or directory: " + relative)
        directories.add(relative)
        def walk_error(exc: OSError) -> None:
            raise FixturePrerequisite("cannot enumerate bounded input directory: " + relative) from exc
        for parent, dirnames, filenames in os.walk(
                source, topdown=True, followlinks=False, onerror=walk_error):
            dirnames.sort()
            filenames.sort()
            parent_path = Path(parent)
            for name in list(dirnames):
                child = parent_path / name
                if child.is_symlink():
                    raise FixturePrerequisite("symlink in bounded input directory: " + relative)
                if not child.is_dir():
                    raise FixturePrerequisite("non-directory in bounded input tree: " + relative)
                directories.add(child.relative_to(root).as_posix())
            for name in filenames:
                child = parent_path / name
                if child.is_symlink():
                    raise FixturePrerequisite("symlink in bounded input directory: " + relative)
                child_mode = child.lstat().st_mode
                if not stat.S_ISREG(child_mode):
                    raise FixturePrerequisite("non-regular file in bounded input tree: " + relative)
                child_relative = child.relative_to(root).as_posix()
                files[child_relative] = (child.read_bytes(), stat.S_IMODE(child_mode))
    return dict(sorted(files.items())), directories


def git_env(**overrides: str) -> dict[str, str]:
    result = dict(CLEAN_ENV)
    result.update(overrides)
    return result


def run_git(root: Path | None, *args: str, env: dict[str, str] | None = None,
            check: bool = True) -> subprocess.CompletedProcess[bytes]:
    command = ["git"]
    if root is not None:
        command.extend(["-C", str(root)])
    command.extend(GIT_CONFIG_ARGS)
    command.extend(args)
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=env or CLEAN_ENV, timeout=60)
    if check and proc.returncode != 0:
        raise FixturePrerequisite("local Git operation unavailable: " + args[0])
    return proc


def make_repo(path: Path) -> None:
    path.mkdir(parents=True)
    proc = subprocess.run(
        ["git", *GIT_CONFIG_ARGS, "init", "--quiet", "--initial-branch=main", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=CLEAN_ENV, timeout=60)
    if proc.returncode != 0:
        raise FixturePrerequisite("cannot initialize isolated synthetic Git repository")


def commit_all(repo: Path, message: str) -> str:
    run_git(repo, "add", "--all")
    proc = subprocess.run(
        ["git", "-C", str(repo), *GIT_CONFIG_ARGS, *IDENTITY_ARGS,
         "commit", "--quiet", "-m", message],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=CLEAN_ENV, timeout=60)
    if proc.returncode != 0:
        raise FixturePrerequisite("cannot commit bounded synthetic input closure")
    return run_git(repo, "rev-parse", "HEAD").stdout.decode("ascii").strip()


def make_sandbox(top: Path, name: str, root: Path, measured: list[str],
                 extras: list[str]) -> tuple[Path, dict[str, tuple[bytes, int]], list[str]]:
    all_paths = list(dict.fromkeys([*measured, *extras]))
    files, directories = expand_closure(root, all_paths)
    repo = top / name
    make_repo(repo)
    for relative in sorted(directories):
        (repo / relative).mkdir(parents=True, exist_ok=True)
    for relative, (data, mode) in files.items():
        destination = repo / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        destination.chmod(mode)
    commit_all(repo, name + " bounded input closure")
    # The fresh output directory is intentionally outside every measured input.
    (repo / "census" / "round-20").mkdir(parents=True, exist_ok=True)
    return repo, files, all_paths


def path_list_at_revision(root: Path, revision: str, source_path: str,
                          variable: str) -> list[str]:
    source = run_git(root, "show", revision + ":" + source_path).stdout.decode("utf-8")
    try:
        tree = ast.parse(source, filename=source_path)
    except SyntaxError as exc:
        raise FixturePrerequisite("baseline caller source is not parseable: " + source_path) from exc
    for node in tree.body:
        value = None
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        if any(isinstance(target, ast.Name) and target.id == variable for target in targets):
            try:
                paths = ast.literal_eval(value)
            except (ValueError, TypeError) as exc:
                raise FixturePrerequisite("baseline path inventory is not a literal: " + variable) from exc
            if not isinstance(paths, list) or not paths or any(not isinstance(path, str) for path in paths):
                raise FixturePrerequisite("baseline path inventory has an unsupported shape: " + variable)
            return [safe_relative(path) for path in paths]
    raise FixturePrerequisite("baseline path inventory is unavailable: " + variable)


def expand_git_closure(root: Path, revision: str, paths: list[str]
                       ) -> tuple[dict[str, tuple[bytes, int]], set[str]]:
    selected = [safe_relative(path) for path in paths]
    tree = run_git(root, "ls-tree", "-r", "-z", revision, "--", *selected)
    files: dict[str, tuple[bytes, int]] = {}
    directories: set[str] = set()
    for row in tree.stdout.split(b"\0"):
        if not row:
            continue
        metadata, encoded_name = row.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        relative = safe_relative(os.fsdecode(encoded_name))
        if kind != b"blob" or mode not in (b"100644", b"100755"):
            raise FixturePrerequisite("baseline closure contains a non-regular input: " + relative)
        data = run_git(root, "cat-file", "blob", oid.decode("ascii")).stdout
        files[relative] = (data, 0o755 if mode == b"100755" else 0o644)
        parent = PurePosixPath(relative).parent
        while parent.parts:
            directories.add(parent.as_posix())
            parent = parent.parent
    return dict(sorted(files.items())), directories


def make_git_sandbox(top: Path, name: str, root: Path, revision: str,
                     measured: list[str], extras: list[str]
                     ) -> tuple[Path, dict[str, tuple[bytes, int]], list[str]]:
    all_paths = list(dict.fromkeys([*measured, *extras]))
    files, directories = expand_git_closure(root, revision, all_paths)
    repo = top / name
    make_repo(repo)
    for relative in sorted(directories):
        (repo / relative).mkdir(parents=True, exist_ok=True)
    for relative, (data, mode) in files.items():
        destination = repo / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        destination.chmod(mode)
    commit_all(repo, name + " baseline bounded input closure")
    (repo / "census" / "round-20").mkdir(parents=True, exist_ok=True)
    return repo, files, all_paths


def make_overlay_sandbox(top: Path, name: str, root: Path, revision: str,
                         paths: list[str], overlay_paths: list[str]
                         ) -> tuple[Path, dict[str, tuple[bytes, int]], list[str]]:
    all_paths = list(dict.fromkeys(safe_relative(path) for path in paths))
    files, directories = expand_git_closure(root, revision, all_paths)
    for relative in all_paths:
        if relative not in files and not any(path.startswith(relative.rstrip("/") + "/")
                                             for path in files):
            raise FixturePrerequisite("baseline lacks shared pair input: " + relative)
    for relative in overlay_paths:
        source = checked_components(root, relative)
        mode = source.lstat().st_mode
        if not stat.S_ISREG(mode):
            raise FixturePrerequisite("current implementation overlay is not regular: " + relative)
        files[relative] = (source.read_bytes(), stat.S_IMODE(mode))
        parent = PurePosixPath(relative).parent
        while parent.parts:
            directories.add(parent.as_posix())
            parent = parent.parent
    files = dict(sorted(files.items()))
    repo = top / name
    make_repo(repo)
    for relative in sorted(directories):
        (repo / relative).mkdir(parents=True, exist_ok=True)
    for relative, (data, mode) in files.items():
        destination = repo / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        destination.chmod(mode)
    commit_all(repo, name + " same-corpus changed implementation")
    (repo / "census" / "round-20").mkdir(parents=True, exist_ok=True)
    return repo, files, all_paths


def current_snapshot(files: dict[str, tuple[bytes, int]], paths: list[str]) -> dict[str, str]:
    selected: dict[str, str] = {}
    for relative, (data, _mode) in files.items():
        if any(relative == path or relative.startswith(path.rstrip("/") + "/")
               for path in paths):
            selected[relative] = sha256(data)
    return dict(sorted(selected.items()))


def make_keep_only_commit(repo: Path, files: dict[str, tuple[bytes, int]]) -> str:
    candidates = [path for path in sorted(files) if path != HELPER]
    if not candidates:
        raise FixturePrerequisite("no regular measured leaf available for keep-only control")
    relative = candidates[0]
    run_git(repo, "switch", "--detach", "HEAD")
    target = repo / relative
    original = target.read_bytes()
    target.write_bytes(original + b"\n<!-- inert refs/jj control -->\n")
    run_git(repo, "add", "--", relative)
    proc = subprocess.run(
        ["git", "-C", str(repo), *GIT_CONFIG_ARGS, *IDENTITY_ARGS,
         "commit", "--quiet", "--only", "-m", "keep-only control", "--", relative],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=CLEAN_ENV, timeout=60)
    if proc.returncode != 0:
        raise FixturePrerequisite("cannot create detached synthetic keep-only commit")
    commit = run_git(repo, "rev-parse", "HEAD").stdout.decode("ascii").strip()
    run_git(repo, "update-ref", "refs/jj/keep/r20-input-binding", commit)
    run_git(repo, "switch", "main")
    if target.read_bytes() != original:
        raise FixturePrerequisite("synthetic worktree did not return to its clean branch")
    return commit


HELPER_DRIVER = r'''import importlib.util, json, sys
helper_path, root, clean, paths_json, expected_json, keep_only, walk_directory = sys.argv[1:]
paths = json.loads(paths_json)
expected = json.loads(expected_json)
spec = importlib.util.spec_from_file_location("r20_pin", helper_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
results = []
def record(name, ok):
    results.append({"name": name, "ok": bool(ok)})
def refusal(name, revision, needle):
    try:
        module.resolve_durable(root, revision, paths)
    except module.Refusal as exc:
        record(name, needle in str(exc))
    except Exception:
        record(name, False)
    else:
        record(name, False)
try:
    observed = module.input_snapshot(root, clean, paths)
    record("input-snapshot-clean", observed == expected and bool(observed))
except Exception:
    record("input-snapshot-clean", False)
try:
    record("resolve-clean", module.resolve_durable(root, clean, paths) == clean)
except Exception:
    record("resolve-clean", False)
refusal("head-refuse", "HEAD", "40-hex")
refusal("branch-refuse", "main", "40-hex")
refusal("short-refuse", clean[:12], "40-hex")
refusal("keep-only-refuse", keep_only, "not reachable")
original_walk = module.os.walk
walk_calls = {"walk": 0, "onerror": 0}
def synthetic_walk_error(path, topdown=True, onerror=None, followlinks=False):
    walk_calls["walk"] += 1
    if onerror is not None:
        walk_calls["onerror"] += 1
        onerror(OSError("synthetic directory-walk failure"))
    return iter(())
try:
    module.os.walk = synthetic_walk_error
    try:
        module.input_snapshot(root, clean, [walk_directory])
    except module.Refusal:
        record("walk-error-refuse", walk_calls == {"walk": 1, "onerror": 1})
    except Exception:
        record("walk-error-refuse", False)
    else:
        record("walk-error-refuse", False)
finally:
    module.os.walk = original_walk
original_git = module._git
walk_calls = {"git": 0, "walk": 0}
def forbidden_git(*args, **kwargs):
    walk_calls["git"] += 1
    raise AssertionError("protected path reached Git")
def forbidden_walk(*args, **kwargs):
    walk_calls["walk"] += 1
    raise AssertionError("protected path reached filesystem walk")
try:
    module._git = forbidden_git
    module.os.walk = forbidden_walk
    try:
        module.input_snapshot(
            root, clean, ["census"])
    except module.Refusal as exc:
        record("protected-census-ancestor-no-walk",
               "protected measured path" in str(exc)
               and walk_calls == {"git": 0, "walk": 0})
    except Exception:
        record("protected-census-ancestor-no-walk", False)
    else:
        record("protected-census-ancestor-no-walk", False)
finally:
    module._git = original_git
    module.os.walk = original_walk
print(json.dumps({"cases": results}, sort_keys=True))
'''
TRIPWIRE_DRIVER = r'''import contextlib, importlib.util, io, json, sys
from pathlib import Path
repo, kind, script, output, commit, changed_path, witness = sys.argv[1:]
stdout = io.StringIO()
stderr = io.StringIO()
module = None
status = "exception"
exit_code = None
observed_witness = ""
def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, Path(repo) / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError("entrypoint loader unavailable")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded
class ProducerReached(BaseException):
    def __init__(self, name):
        self.name = name
def producer(*args, **kwargs):
    raise ProducerReached(witness)
try:
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        if kind == "r13":
            module = load(script, "r20_tripwire_r13")
            module.BASE = commit
            module.run = producer
            result = module.main(["--round", "20", "--output", output])
        elif kind == "r14":
            module = load(script, "r20_tripwire_r14")
            module.BASE = commit
            module.run = producer
            sys.argv = [script, "--output", output]
            result = module.main()
        elif kind == "targeted":
            module = load(script, "r20_tripwire_targeted")
            module.module.BASE = commit
            module.module.run = producer
            sys.argv = [script, "--output", output]
            result = module.main()
        elif kind == "demo":
            module = load(script, "r20_tripwire_demo")
            module.BASELINE_COMMIT = commit
            module.run_demonstration = producer
            result = module.main(["--gate", str(Path(repo) / "tools/souji-evidence-cache.py")])
        else:
            raise RuntimeError("unknown caller kind")
    status = "return"
    exit_code = result if isinstance(result, int) else 0
except ProducerReached as exc:
    status = "producer"
    observed_witness = exc.name
except SystemExit as exc:
    status = "exit"
    exit_code = exc.code if isinstance(exc.code, int) else 0
except BaseException as exc:
    status = "exception"
    observed_witness = type(exc).__name__
output_exists = bool(output) and (Path(repo) / output).exists()
print(json.dumps({
    "status": status,
    "exit_code": exit_code,
    "witness": observed_witness,
    "changed_path_named": changed_path in stderr.getvalue(),
    "stdout_empty": stdout.getvalue() == "",
    "output_absent": not output_exists,
}, sort_keys=True))
'''

WRITER_DRIVER = r'''import contextlib, hashlib, importlib.util, io, json, sys
from pathlib import Path
repo, kind, script, output, commit, drift_path, expected_snapshot_json = sys.argv[1:]
expected_snapshot = json.loads(expected_snapshot_json)
stdout = io.StringIO()
stderr = io.StringIO()
module = None
state = {"producer_stubbed": False, "producer_calls": 0, "drift_written": False}
status = "exception"
exit_code = None
exception_type = ""
exception_message = ""
def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, Path(repo) / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError("entrypoint loader unavailable")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded
def mutate_drift():
    if not drift_path or state["drift_written"]:
        return
    target = Path(repo) / drift_path
    suffix = b" \n" if target.suffix.lower() == ".json" else b"\n<!-- inert writer drift -->\n"
    target.write_bytes(target.read_bytes() + suffix)
    state["drift_written"] = True
def marked_result(name, command, expected, revision):
    return {
        "name": name, "command": command, "exit_code": expected,
        "expected_exit": expected, "matched": True,
        "stdout": "finding artifact-digest-mismatch:\nfinding artifact-candidate:\n",
        "stderr": "", "seconds": 0.0, "measured_commit": revision,
        "dependencies": {}, "dependencies_stable": True,
        "reuse_eligible": True,
    }
def r13_producer(name, command, expected=0, seconds=120):
    state["producer_stubbed"] = True
    state["producer_calls"] += 1
    mutate_drift()
    return marked_result(name, command, expected, module.CURRENT_REV)
def r14_producer(name, command, revision, expected=0, seconds=150):
    state["producer_stubbed"] = True
    state["producer_calls"] += 1
    mutate_drift()
    return marked_result(name, command, expected, revision)
def demo_producer(gate, gate_state, base, initial_commit):
    state["producer_stubbed"] = True
    state["producer_calls"] += 1
    mutate_drift()
    return {
        "schema": "souji-r14-cache-demonstration-v1",
        "demonstration": "digest-bound-retention",
        "status": "ok",
        "measured_commit": initial_commit,
        "harness_revision": initial_commit,
        "gate": dict(gate_state),
        "checks": {},
        "failed_checks": [],
    }
try:
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        if kind == "r13":
            module = load(script, "r20_writer_r13")
            module.BASE = commit
            module.run = r13_producer
            result = module.main(["--round", "20", "--output", output])
        elif kind == "r14":
            module = load(script, "r20_writer_r14")
            module.BASE = commit
            module.run = r14_producer
            sys.argv = [script, "--output", output]
            result = module.main()
        elif kind == "targeted":
            module = load(script, "r20_writer_targeted")
            module.module.BASE = commit
            module.module.run = r14_producer
            sys.argv = [script, "--output", output]
            result = module.main()
        elif kind == "demo":
            module = load(script, "r20_writer_demo")
            module.BASELINE_COMMIT = commit
            module.run_demonstration = demo_producer
            result = module.main(["--gate", str(Path(repo) / "tools/souji-evidence-cache.py")])
        else:
            raise RuntimeError("unknown writer caller kind")
    status = "return"
    exit_code = result if isinstance(result, int) else 0
except SystemExit as exc:
    status = "exit"
    exit_code = exc.code if isinstance(exc.code, int) else 0
except BaseException as exc:
    status = "exception"
    exception_type = type(exc).__name__
    exception_message = str(exc)
first_refusal = next((line for line in stderr.getvalue().splitlines() if line.strip()), "")
reason = first_refusal or exception_message
record = None
output_path = Path(repo) / output if output else None
if output_path is not None and output_path.is_file():
    try:
        record = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        record = None
elif kind == "demo" and status == "return" and exit_code == 0:
    try:
        record = json.loads(stdout.getvalue())
    except ValueError:
        record = None
input_hashes = record.get("input_sha256") if isinstance(record, dict) else None
def valid_hash(value):
    return (isinstance(value, str) and len(value) == 64
            and all(character in "0123456789abcdef" for character in value))
input_sha256_valid = (
    isinstance(input_hashes, dict)
    and input_hashes == expected_snapshot
    and all(valid_hash(value) for value in input_hashes.values())
)
revision_valid = (isinstance(record, dict)
                  and record.get("measured_commit") == commit)
record_absent = (not output_path.exists() if output_path is not None
                 else record is None and stdout.getvalue() == "")
print(json.dumps({
    "status": status,
    "exit_code": exit_code,
    "exception_type": exception_type,
    "reason": reason,
    "producer_stubbed": state["producer_stubbed"],
    "producer_calls": state["producer_calls"],
    "drift_written": state["drift_written"],
    "record_exists": record is not None,
    "record_absent": record_absent,
    "input_sha256_valid": input_sha256_valid,
    "inputs_unchanged_during_run": (
        isinstance(record, dict) and record.get("inputs_unchanged_during_run") is True),
    "measured_revision_valid": revision_valid,
    "stdout_empty": stdout.getvalue() == "",
}, sort_keys=True))
'''


def helper_controls(repo: Path, measured: list[str], files: dict[str, tuple[bytes, int]],
                    decoy: Path, top: Path, cases: Cases) -> None:
    helper_path = repo / HELPER
    if not helper_path.is_file():
        raise FixturePrerequisite("revision helper is not in r13 bounded closure")
    keep_only = make_keep_only_commit(repo, files)
    clean = run_git(repo, "rev-parse", "HEAD").stdout.decode("ascii").strip()
    expected = current_snapshot(files, measured)
    env = git_env(
        GIT_DIR=str(decoy / ".git"),
        GIT_WORK_TREE=str(decoy),
        GIT_INDEX_FILE=str(decoy / ".git" / "index"),
    )
    walk_directory = R13_FROZEN_DIR
    proc = subprocess.run(
        [sys.executable, "-B", "-c", HELPER_DRIVER, str(helper_path), str(repo), clean,
         json.dumps(measured), json.dumps(expected, sort_keys=True), keep_only, walk_directory],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=top,
        env=env, timeout=60)
    parsed = None
    if proc.returncode == 0:
        try:
            parsed = json.loads(proc.stdout)
        except ValueError:
            parsed = None
    expected_names = {
        "input-snapshot-clean", "resolve-clean", "head-refuse", "branch-refuse",
        "short-refuse", "keep-only-refuse", "walk-error-refuse",
        "protected-census-ancestor-no-walk",
    }
    observed = {item.get("name"): item.get("ok") for item in (parsed or {}).get("cases", [])}
    for name in sorted(expected_names):
        cases.add("helper-" + name, observed.get(name) is True,
                  "actual helper API; ambient GIT_DIR points at a different synthetic repository")
    cases.add("helper-ambient-GIT_DIR-redirection", observed.get("input-snapshot-clean") is True
              and observed.get("resolve-clean") is True,
              "clean root snapshot and durable resolution survive foreign GIT_DIR/GIT_WORK_TREE/INDEX")


def choose_existing_admitted(root: Path) -> str:
    knowledge = root / "corpus" / "knowledge"
    if knowledge.is_symlink() or not knowledge.is_dir():
        raise FixturePrerequisite("r13 admission corpus directory is unavailable")
    for candidate in sorted(knowledge.glob("*.md")):
        if candidate.is_symlink() or not candidate.is_file():
            continue
        text = candidate.read_text(encoding="utf-8")
        lines = text.splitlines()
        if (len(lines) >= 3 and "## Admission status — HELD" not in text
                and lines[0].startswith("source:")
                and lines[1].startswith("verified-at:")
                and lines[2].startswith("recheck:")):
            return candidate.relative_to(root).as_posix()
    raise FixturePrerequisite("r13 admission corpus has no admitted markdown input")


def inert_suffix(relative: str) -> bytes:
    suffix = PurePosixPath(relative).suffix.lower()
    if suffix == ".json":
        return b" \n"
    if suffix in (".py", ".sh", ".txt"):
        return b"\n# inert r20 input-binding mutation\n"
    return b"\n<!-- inert r20 input-binding mutation -->\n"


def caller_command(repo: Path, name: str, kind: str, script: str,
                   case_name: str) -> tuple[list[str], str | None]:
    output = "census/round-20/r20-%s-%s.json" % (name, case_name)
    if kind == "r13":
        return [sys.executable, "-B", script, "--round", "20", "--output", output,
                "--retry-failed", "--previous", R13_PRIOR], output
    if kind in ("r14", "targeted"):
        return [sys.executable, "-B", script, "--output", output], output
    if kind == "demo":
        return [sys.executable, "-B", script], None
    raise FixturePrerequisite("unknown caller kind")


def expected_refusal_fragment(case_name: str, changed_path: str) -> str:
    if case_name in ("helper-dirty", "helper-syntax-invalid"):
        return HELPER + " differs from measured commit"
    if case_name == "verifier-syntax-invalid":
        return ROUND14 + " differs from measured commit"
    if case_name == "counted-knowledge-added":
        return "missing=[] added=%r changed=[]" % [changed_path]
    return "missing=[] added=[] changed=%r" % [changed_path]


def caller_refusal(repo: Path, name: str, kind: str, script: str,
                   case_name: str, changed_path: str, decoy: Path) -> tuple[bool, str]:
    command, output_relative = caller_command(repo, name, kind, script, case_name)
    env = git_env(
        GIT_DIR=str(decoy / ".git"),
        GIT_WORK_TREE=str(decoy),
        GIT_INDEX_FILE=str(decoy / ".git" / "index"),
    )
    try:
        proc = subprocess.run(command, cwd=repo, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, "caller invocation failed before an observed refusal: " + type(exc).__name__
    combined = proc.stdout + proc.stderr
    first_refusal = next((line for line in proc.stderr.splitlines() if line.strip()), "")
    reason_fragment = expected_refusal_fragment(case_name, changed_path)
    reason_ok = reason_fragment in first_refusal
    specific = changed_path in combined
    if kind == "demo":
        stdout_empty = proc.stdout == ""
        return (proc.returncode == 2 and specific and reason_ok and stdout_empty,
                "exit=%d changed_path_named=%d reason_family=%d stdout_empty=%d "
                "first_refusal=%s" %
                (proc.returncode, int(specific), int(reason_ok), int(stdout_empty), first_refusal))
    output_absent = output_relative is not None and not (repo / output_relative).exists()
    no_suite_output = proc.stdout == ""
    return (proc.returncode == 2 and specific and reason_ok and output_absent and no_suite_output,
            "exit=%d changed_path_named=%d reason_family=%d output_absent=%d "
            "suite_stdout_absent=%d first_refusal=%s" %
            (proc.returncode, int(specific), int(reason_ok), int(output_absent),
             int(no_suite_output), first_refusal))


def mutate_and_call(repo: Path, name: str, kind: str, script: str,
                    case_name: str, relative: str, decoy: Path, cases: Cases,
                    add_file: bool = False, invalid_syntax: bool = False) -> None:
    target = repo / relative
    if add_file:
        if target.exists() or target.is_symlink():
            raise FixturePrerequisite("new-knowledge test path already exists in sandbox")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "source: fixture-local\nverified-at: 2026-10-21\n"
            "recheck: r20-input-binding\n\n"
            "# inert counted-input fixture; no external source claim\n",
            encoding="utf-8")
        original = None
    else:
        if target.is_symlink() or not target.is_file():
            raise FixturePrerequisite("dirty-input target is not a regular synthetic file: " + relative)
        original = target.read_bytes()
        if invalid_syntax:
            target.write_bytes(original + b"\ndef r20_invalid(:\n")
        else:
            target.write_bytes(original + inert_suffix(relative))
    try:
        ok, detail = caller_refusal(repo, name, kind, script, case_name, relative, decoy)
        cases.add(name + "-" + case_name, ok,
                  "changed=%s; %s" % (relative, detail))
    finally:
        if add_file:
            target.unlink(missing_ok=True)
        elif original is not None:
            target.write_bytes(original)


def covered_by_measured(path: str, measured: list[str]) -> bool:
    return any(path == item or path.startswith(item.rstrip("/") + "/")
               for item in measured)


def mutation_plan(name: str, kind: str, script: str, measured: list[str],
                  existing_knowledge: str | None) -> list[tuple[str, str, bool]]:
    plan: list[tuple[str, str, bool]] = [
        ("helper-dirty", HELPER, False),
        ("helper-syntax-invalid", HELPER, False),
        ("wrapper-dirty", script, False),
    ]
    if name == "r13":
        plan.extend([
            ("frozen-dirty", R13_FROZEN, False),
            ("sources-dirty", "corpus/SOURCES.md", False),
            ("admitted-knowledge-dirty", existing_knowledge or "", False),
            ("counted-knowledge-added", NEW_KNOWLEDGE, True),
            ("optional-prior-dirty", R13_PRIOR, False),
        ])
    elif name in ("r14", "targeted"):
        plan.extend([
            ("frozen-dirty", R14_FROZEN, False),
            ("sources-dirty", "corpus/SOURCES.md", False),
        ])
        if name == "targeted":
            plan.extend([
                ("verifier-syntax-invalid", ROUND14, False),
                ("prior-attempt-dirty", R14_PRIOR, False),
            ])
    elif name == "demo":
        plan.append(("historical-input-dirty", R13_PRIOR, False))
    for label, path, _add in plan:
        if not path or not covered_by_measured(path, measured):
            raise FixturePrerequisite("expected actual caller input is absent from its measured closure: " + label)
    return plan


def run_caller_matrix(top: Path, root: Path, caller_specs: list[dict[str, object]],
                      existing_knowledge: str, decoy: Path, cases: Cases) -> None:
    for spec in caller_specs:
        name = str(spec["name"])
        measured = list(spec["measured"])
        extras = list(spec["extras"])
        script = str(spec["script"])
        kind = str(spec["kind"])
        repo, _files, all_paths = make_sandbox(top, name, root, measured, extras)
        plan = mutation_plan(name, kind, script, all_paths, existing_knowledge)
        for case_name, relative, add_file in plan:
            mutate_and_call(repo, name, kind, script, case_name, relative,
                            decoy, cases, add_file=add_file,
                            invalid_syntax=case_name in (
                                "helper-syntax-invalid", "verifier-syntax-invalid"))




def invoke_writer(repo: Path, kind: str, script: str, output: str,
                  commit: str, drift_path: str,
                  expected_snapshot: dict[str, str]) -> dict[str, object]:
    try:
        proc = subprocess.run(
            [sys.executable, "-B", "-c", WRITER_DRIVER, str(repo), kind, script,
             output, commit, drift_path, json.dumps(expected_snapshot, sort_keys=True)],
            cwd=repo, env=CLEAN_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "invocation-failed", "exception_type": type(exc).__name__}
    try:
        return json.loads(proc.stdout) if proc.returncode == 0 else {
            "status": "driver-failed", "exception_type": "driver-exit-%d" % proc.returncode}
    except ValueError:
        return {"status": "driver-failed", "exception_type": "invalid-driver-json"}


def run_writer_controls(top: Path, root: Path, caller_specs: list[dict[str, object]],
                        cases: Cases) -> None:
    drift_paths = {
        "r13": "corpus/SOURCES.md",
        "r14": "corpus/SOURCES.md",
        "targeted": "corpus/SOURCES.md",
        "demo": R13_PRIOR,
    }
    for spec in caller_specs:
        name = str(spec["name"])
        kind = str(spec["kind"])
        script = str(spec["script"])
        measured = list(spec["measured"])
        extras = list(spec["extras"])
        drift_path = drift_paths[name]
        if not covered_by_measured(drift_path, list(dict.fromkeys([*measured, *extras]))):
            raise FixturePrerequisite("writer-drift input is absent from measured closure: " + drift_path)
        for phase in ("clean", "drift"):
            repo, input_files, _paths = make_sandbox(
                top, "writer-%s-%s" % (name, phase), root, measured, extras)
            expected_snapshot = current_snapshot(input_files, measured)
            commit = run_git(repo, "rev-parse", "HEAD").stdout.decode("ascii").strip()
            output = "" if kind == "demo" else (
                "census/round-20/writer-%s-%s.json" % (name, phase))
            changed = drift_path if phase == "drift" else ""
            observed = invoke_writer(
                repo, kind, script, output, commit, changed, expected_snapshot)
            stubbed = observed.get("producer_stubbed") is True and int(
                observed.get("producer_calls", 0) or 0) > 0
            if phase == "clean":
                good = (observed.get("status") == "return"
                        and observed.get("exit_code") == 0
                        and stubbed
                        and observed.get("record_exists") is True
                        and observed.get("input_sha256_valid") is True
                        and observed.get("inputs_unchanged_during_run") is True
                        and observed.get("measured_revision_valid") is True)
                cases.add("writer-%s-clean" % name, good,
                          "producer_stubbed=%s calls=%s top_level_input_sha256=%d "
                          "measured_revision=%d record_exists=%d" %
                          ("True" if stubbed else "False", observed.get("producer_calls", 0),
                           int(observed.get("input_sha256_valid") is True),
                           int(observed.get("measured_revision_valid") is True),
                           int(observed.get("record_exists") is True)))
                continue
            reason = str(observed.get("reason", ""))
            expected_change = "missing=[] added=[] changed=%r" % [drift_path]
            reason_family = ("measured inputs differ from" in reason
                             and expected_change in reason)
            status = observed.get("status")
            typed_refusal = (status == "exception"
                             and observed.get("exception_type") == "Refusal")
            returned_refusal = (status in ("return", "exit")
                                and observed.get("exit_code") == 2)
            no_record = (observed.get("record_absent") is True
                         and observed.get("record_exists") is False)
            good = (stubbed and observed.get("drift_written") is True
                    and (typed_refusal or returned_refusal)
                    and reason_family and no_record
                    and observed.get("stdout_empty") is True)
            cases.add("drift-%s" % name, good,
                      "producer_stubbed=%s calls=%s drift_written=%d typed_refusal=%d "
                      "returned_refusal=%d reason_family=%d no_record=%d stdout_empty=%d "
                      "first_refusal=%s" %
                      ("True" if stubbed else "False", observed.get("producer_calls", 0),
                       int(observed.get("drift_written") is True), int(typed_refusal),
                       int(returned_refusal), int(reason_family), int(no_record),
                       int(observed.get("stdout_empty") is True), reason))
def invoke_tripwire(repo: Path, kind: str, script: str, output: str,
                    commit: str, changed_path: str, witness: str) -> dict[str, object]:
    try:
        proc = subprocess.run(
            [sys.executable, "-B", "-c", TRIPWIRE_DRIVER, str(repo), kind, script,
             output, commit, changed_path, witness],
            cwd=repo, env=CLEAN_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "invocation-failed", "error": type(exc).__name__}
    try:
        result = json.loads(proc.stdout) if proc.returncode == 0 else {}
    except ValueError:
        result = {}
    return result


def apply_pair_mutation(repo: Path, relative: str, add_file: bool) -> None:
    target = repo / relative
    if add_file:
        if target.exists() or target.is_symlink():
            raise FixturePrerequisite("baseline pair knowledge path already exists in synthetic tree")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "source: fixture-local\nverified-at: 2026-10-21\n"
            "recheck: r20-input-binding\n\n"
            "# inert counted-input fixture; no external source claim\n",
            encoding="utf-8")
        return
    if target.is_symlink() or not target.is_file():
        raise FixturePrerequisite("baseline pair input is not a regular synthetic file: " + relative)
    target.write_bytes(target.read_bytes() + inert_suffix(relative))


def run_baseline_pairs(top: Path, root: Path, revision: str,
                       caller_specs: list[dict[str, object]], cases: Cases) -> None:
    specs = {str(item["name"]): item for item in caller_specs}
    old_r13 = path_list_at_revision(root, revision, ROUND13, "MEASURED_PATHS")
    old_r14 = path_list_at_revision(root, revision, ROUND14, "MEASURED_PATHS")
    old_demo = path_list_at_revision(root, revision, DEMO, "DEMO_MEASURED_PATHS")
    pairs = [
        ("baseline-r13-helper", "r13", ROUND13, old_r13, [HELPER], "r13", HELPER, False),
        ("baseline-r13-sources", "r13", ROUND13, old_r13, ["corpus/SOURCES.md"],
         "r13", "corpus/SOURCES.md", False),
        ("baseline-r13-new-knowledge", "r13", ROUND13, old_r13, [],
         "r13", NEW_KNOWLEDGE, True),
        ("baseline-r14-helper", "r14", ROUND14, old_r14,
         [HELPER, R13_PRIOR], "r14", HELPER, False),
        ("baseline-r14-frozen", "r14", ROUND14, old_r14,
         [R14_FROZEN, R13_PRIOR], "r14", R14_FROZEN, False),
        ("baseline-targeted-wrapper", "targeted", TARGETED,
         list(dict.fromkeys([*old_r14, R14_PRIOR])),
         [TARGETED, R13_PRIOR], "targeted", TARGETED, False),
        ("baseline-demo-helper", "demo", DEMO, old_demo, [HELPER],
         "demo", HELPER, False),
    ]
    for case_id, kind, script, old_paths, old_extras, changed_name, changed_path, add_file in pairs:
        changed_spec = specs[changed_name]
        changed_paths = list(dict.fromkeys([
            *list(changed_spec["measured"]), *list(changed_spec["extras"]),
        ]))
        common_paths = list(dict.fromkeys([*old_paths, *old_extras, *changed_paths]))
        overlay_paths = list(dict.fromkeys([script, HELPER]
                                           + ([ROUND14] if kind == "targeted" else [])))
        baseline_repo, baseline_files, _ = make_git_sandbox(
            top, case_id + "-baseline", root, revision, common_paths, [])
        changed_repo, changed_files, _ = make_overlay_sandbox(
            top, case_id + "-changed", root, revision, common_paths, overlay_paths)
        overlay_set = set(overlay_paths)
        if any(baseline_files.get(path) != changed_files.get(path)
               for path in set(baseline_files) | set(changed_files)
               if path not in overlay_set):
            raise FixturePrerequisite("baseline and changed pair input corpora differ")
        apply_pair_mutation(baseline_repo, changed_path, add_file)
        apply_pair_mutation(changed_repo, changed_path, add_file)
        baseline_commit = run_git(baseline_repo, "rev-parse", "HEAD").stdout.decode("ascii").strip()
        changed_commit = run_git(changed_repo, "rev-parse", "HEAD").stdout.decode("ascii").strip()
        baseline_output = "census/round-20/%s-baseline.json" % case_id
        changed_output = "census/round-20/%s-changed.json" % case_id
        old_result = invoke_tripwire(
            baseline_repo, kind, script, baseline_output, baseline_commit, changed_path, case_id)
        new_result = invoke_tripwire(
            changed_repo, kind, script, changed_output, changed_commit, changed_path, case_id)
        baseline_reached = (old_result.get("status") == "producer"
                            and old_result.get("witness") == case_id
                            and old_result.get("output_absent") is True)
        changed_refused = (new_result.get("status") in ("exit", "return")
                           and new_result.get("exit_code") == 2
                           and new_result.get("changed_path_named") is True
                           and new_result.get("stdout_empty") is True
                           and new_result.get("output_absent") is True)
        cases.add(case_id, baseline_reached and changed_refused,
                  "baseline_tripwire=%d changed_exit2=%d changed_path_named=%d "
                  "stdout_empty=%d output_absent=%d" %
                  (int(baseline_reached), int(changed_refused),
                   int(new_result.get("changed_path_named") is True),
                   int(new_result.get("stdout_empty") is True),
                   int(new_result.get("output_absent") is True)))


def compare_baseline(root: Path, closure_files: dict[str, tuple[bytes, int]],
                     paths: list[str], revision: str, cases: Cases) -> None:
    cases.baseline_requested = True
    resolved = run_git(root, "rev-parse", "--verify", "--quiet", revision + "^{commit}",
                       check=False)
    if resolved.returncode != 0:
        raise FixturePrerequisite("requested baseline does not resolve locally")
    baseline = resolved.stdout.decode("ascii").strip()
    tree = run_git(root, "ls-tree", "-r", "-z", "--name-only", baseline,
                   "--", *paths)
    baseline_paths = {os.fsdecode(item) for item in tree.stdout.split(b"\0") if item}
    baseline_files: dict[str, bytes] = {}
    for relative in sorted(baseline_paths):
        item = run_git(root, "show", baseline + ":" + relative)
        baseline_files[relative] = item.stdout
    current_files = {relative: item[0] for relative, item in closure_files.items()}
    differences = sorted(set(current_files) | set(baseline_files))
    for relative in differences:
        current = current_files.get(relative)
        expected = baseline_files.get(relative)
        current_hash = sha256(current) if current is not None else "missing"
        expected_hash = sha256(expected) if expected is not None else "missing"
        if current_hash != expected_hash:
            cases.baseline(relative, current_hash, expected_hash)
    if cases.baseline_mismatches == 0:
        print("BASELINE_MATCH\tcommit=%s\tfiles=%d" % (baseline, len(current_files)))
    else:
        print("BASELINE_SUMMARY\tcommit=%s\tfiles=%d\tmismatches=%d" %
              (baseline, len(current_files), cases.baseline_mismatches))


def expected_counter_inventories() -> list[tuple[str, str, str, dict[str, object]]]:
    return [
        ("r13", "census/round-13/count-claims.py",
         "31984f473ce4bdab61a99b16cca194b28108cb81",
         {"F2_entry": 0, "admitted_entries": 4, "evidence_gate": 0,
          "measured_commit": "31984f473ce4bdab61a99b16cca194b28108cb81",
          "sources": 33, "tiers": {"A": 29, "B": 3, "C": 1},
          "statuses": {"mined": 16, "queued": 15, "rejected": 2}}),
        ("r13", "census/round-13/count-claims.py",
         "6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6",
         {"F2_entry": 1, "admitted_entries": 5, "evidence_gate": 1,
          "measured_commit": "6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6",
          "sources": 37, "tiers": {"A": 33, "B": 3, "C": 1},
          "statuses": {"mined": 20, "queued": 15, "rejected": 2}}),
        ("r14", "census/round-14/count-claims.py",
         "a31642d14006830ec62edf40b0354c3699728c4a",
         {"measured_commit": "a31642d14006830ec62edf40b0354c3699728c4a",
          "cache_gate": 0, "cache_fixture": 0, "boundary_fixture": 0,
          "source_rows": 37, "tiers": {"A": 33, "B": 3, "C": 1},
          "statuses": {"mined": 20, "queued": 15, "rejected": 2},
          "admitted_knowledge": 5, "held_knowledge": 1}),
        ("r14", "census/round-14/count-claims.py",
         "552cae4204b3ab818419ad8adbfef3a4da29a3e0",
         {"measured_commit": "552cae4204b3ab818419ad8adbfef3a4da29a3e0",
          "cache_gate": 1, "cache_fixture": 1, "boundary_fixture": 1,
          "source_rows": 40, "tiers": {"A": 36, "B": 3, "C": 1},
          "statuses": {"mined": 23, "queued": 15, "rejected": 2},
          "admitted_knowledge": 5, "held_knowledge": 1}),
    ]


def run_historical_counters(root: Path, cases: Cases) -> None:
    for round_name, script, revision, expected in expected_counter_inventories():
        try:
            proc = subprocess.run(
                [sys.executable, "-B", str(root / script), revision], cwd=root,
                env=CLEAN_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=90)
        except (OSError, subprocess.TimeoutExpired) as exc:
            cases.add("historical-%s-%s" % (round_name, revision), False,
                      "full-ID counter invocation failed: " + type(exc).__name__)
            continue
        try:
            observed = json.loads(proc.stdout) if proc.returncode == 0 else None
        except ValueError:
            observed = None
        cases.add("historical-%s-%s" % (round_name, revision),
                  proc.returncode == 0 and observed == expected,
                  "full 40-hex ID; exit=%d inventory_match=%d" %
                  (proc.returncode, int(observed == expected)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT),
                        help="installed source root (default: fixture's repository root)")
    parser.add_argument("--baseline", metavar="REV",
                        help="compare bounded source bytes and run seven actual red-before tripwire pairs")
    args = parser.parse_args(argv)
    cases = Cases()
    root = Path(args.root)
    if root.is_symlink() or not root.is_dir():
        cases.add("source-root", False, "--root must name an existing non-symlink directory")
        return cases.summary(blocked=True)
    root = Path(os.path.abspath(root))

    try:
        r13_paths = parse_path_list(root, ROUND13, "MEASURED_PATHS")
        r14_paths = parse_path_list(root, ROUND14, "MEASURED_PATHS")
        demo_paths = parse_path_list(root, DEMO, "DEMO_MEASURED_PATHS")
        # The targeted caller adds its exact prior-attempt input before asking
        # the r14 resolver to snapshot the complete set.
        targeted_paths = list(dict.fromkeys([*r14_paths, R14_PRIOR]))
        r13_extras = [R13_PRIOR]
        existing_knowledge = choose_existing_admitted(root)
        closure_by_caller = [
            ("r13", r13_paths, r13_extras),
            ("r14", r14_paths, []),
            ("targeted", targeted_paths, []),
            ("demo", demo_paths, []),
        ]
        closure_files: dict[str, tuple[bytes, int]] = {}
        for _name, paths, extras in closure_by_caller:
            expanded, _dirs = expand_closure(root, [*paths, *extras])
            closure_files.update(expanded)
        if args.baseline:
            compare_baseline(root, closure_files,
                             list(dict.fromkeys(path for _name, paths, extras in closure_by_caller
                                                for path in [*paths, *extras])),
                             args.baseline, cases)
        with tempfile.TemporaryDirectory(prefix="souji-r20-input-binding-", dir=TMP_ROOT) as temp:
            top = Path(temp)
            r13_repo, _r13_files, _ = make_sandbox(
                top, "helper-controls", root, r13_paths, r13_extras)
            decoy = top / "ambient-decoy"
            make_repo(decoy)
            (decoy / "decoy-only.txt").write_text("other synthetic repository\n", encoding="utf-8")
            commit_all(decoy, "ambient repository selector control")
            helper_controls(r13_repo, r13_paths + r13_extras,
                            expand_closure(root, r13_paths + r13_extras)[0],
                            decoy, top, cases)

            caller_specs: list[dict[str, object]] = [
                {"name": "r13", "script": ROUND13, "kind": "r13",
                 "measured": r13_paths, "extras": r13_extras},
                {"name": "r14", "script": ROUND14, "kind": "r14",
                 "measured": r14_paths, "extras": []},
                {"name": "targeted", "script": TARGETED, "kind": "targeted",
                 "measured": targeted_paths, "extras": []},
                {"name": "demo", "script": DEMO, "kind": "demo",
                 "measured": demo_paths, "extras": []},
            ]
            run_caller_matrix(top, root, caller_specs, existing_knowledge, decoy, cases)
            run_writer_controls(top, root, caller_specs, cases)
            if args.baseline:
                run_baseline_pairs(top, root, args.baseline, caller_specs, cases)
        run_historical_counters(root, cases)
    except FixturePrerequisite as exc:
        cases.add("prerequisite", False, str(exc))
        return cases.summary(blocked=True)
    return cases.summary()



def _private_var_tmp() -> None:
    """Scratch discipline (r32 C2): run this fixture inside a private /var/tmp backed by the caller's TMPDIR.

    Its synthetic worlds and the pinned historical entrypoints it executes create scratch under a literal /var/tmp;
    bwrap binds a fresh directory under TMPDIR over /var/tmp for the whole process tree, so nothing lands in the
    host's /var/tmp. Without bwrap the fixture runs as before.
    """
    import os, shutil, subprocess, sys, tempfile
    if os.environ.get("SOUJI_PRIVATE_VARTMP") or shutil.which("bwrap") is None:
        return
    private = tempfile.mkdtemp(prefix="souji-private-vartmp.")
    try:
        argv = [sys.executable] + (["-B"] if sys.flags.dont_write_bytecode else []) + sys.argv
        rc = subprocess.call(["bwrap", "--dev-bind", "/", "/", "--bind", private, "/var/tmp", "--chdir", os.getcwd(), *argv],
                             env=dict(os.environ, SOUJI_PRIVATE_VARTMP=private))
    finally:
        shutil.rmtree(private, ignore_errors=True)
    sys.exit(rc)


if __name__ == "__main__":
    _private_var_tmp()
    raise SystemExit(main())
