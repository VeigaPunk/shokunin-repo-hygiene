#!/usr/bin/env python3
"""r37-drift-escapes.py — fixture for the r37 C2 drift-tool write-escape repair.

The r36 non-author spot-check (routed defect 3) found `tools/souji-worktree-drift.py`
writes outside its documented read-only envelope: a record row plus `--json`
can overwrite a file in a repository the record names (W1); `GIT_TRACE_REFS`
is scrubbed nowhere (W2); the env scrub *removes* `GIT_CONFIG_NOSYSTEM` and
`GIT_CONFIG_GLOBAL/SYSTEM` so trace2 targets from real config are honoured
(W3); and the `--json` guard resolves one path while the writer opens another
(W4). The r36 capability row claims the tool never writes inside the measured
tree.

Each case builds a synthetic fleet in scratch (under `--work` / `TMPDIR`, never
a hard-coded /tmp or /var/tmp), invokes the candidate tool, and checks the
refusal and the absence of the escape file. The same cases then run against
`--base-tool` (the r36 blob: `git show <r36-tip>:tools/souji-worktree-drift.py`)
so the fixture proves it discriminates: `base_fail` must be >= 8 and `escapes` >= 6 and the
control must print `ESCAPE-REPRODUCED`.

Cases:
  record-escape      record names `../sibling` (outside --root)          -> rc 2 RECORD-OUTSIDE-ROOT
  json-write-escape  the same row plus `--json <sibling>/pwned.json`     -> rc 2, pwned absent
  trace-refs         GIT_TRACE_REFS=<scratch>/trace                       -> trace absent
  env-witness        child git env carries GIT_CONFIG_NOSYSTEM=1 and
                     GIT_CONFIG_GLOBAL/SYSTEM=/dev/null, no config injection
  json-inside        --json inside the measured root (r36 A2 regression)  -> rc 2, file absent
  trace2-event       GIT_TRACE2_EVENT=<scratch>/trace (r36 A2 regression) -> trace absent
  json-hardlink      --json names an out-of-root hardlink to an in-root
                     file                                                -> rc 2, victim unchanged
  record-fifo        a FIFO record                                         -> rc 2, not a hang
  json-gitfile-write a row whose .git file points outside --root           -> rc 2, victim unchanged
  json-symlink-child an unrecorded symlinked child is not measured          -> victim unchanged
  record-symlink     a record row that is a symlink out of --root          -> rc 2, no file
  measured           a record that disagrees with the live tree            -> rc 1 REGS-CHANGED
                                                                             drift_rows=1 (a fixed-
                                                                             summary stub fails)

CLI:
  python3 -B tests/fixtures/r37-drift-escapes.py [--tool PATH] [--base-tool PATH] [--work DIR]

Exit: 0 candidate fail=0, base_fail >= 8 and escapes >= 6, 1 otherwise, 2 usage.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C",
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}


def sh(cmd, cwd=None, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env or ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def make_repo(path):
    os.makedirs(path)
    sh(["git", "init", "-q", "-b", "main", path])
    write(os.path.join(path, "file.txt"), "base\n")
    sh(["git", "-C", path, "add", "file.txt"])
    sh(["git", "-C", path, "commit", "-qm", "base"])
    return path


def build(scratch, name):
    root = os.path.join(scratch, name)
    os.makedirs(root)
    fleet = os.path.join(root, "fleet")
    os.makedirs(fleet)
    make_repo(os.path.join(fleet, "alpha"))
    make_repo(os.path.join(fleet, "beta"))
    sibling = make_repo(os.path.join(root, "sibling"))
    return root, fleet, sibling


def record(root, rows, total):
    path = os.path.join(root, "record.tsv")
    lines = ["REPO\t%s\tregs=%d\tprunable=%d" % (n, r, p) for n, r, p in rows]
    lines.append("TOTAL\trepos=%d\tregs=%d\tprunable=%d" % total)
    write(path, "\n".join(lines) + "\n")
    return path


def invoke(tool, fleet, rec, extra=None, env_extra=None):
    env = dict(ENV)
    if env_extra:
        env.update(env_extra)
    cmd = ["python3", "-B", tool, "--root", fleet, "--record", rec, "--timeout", "30"] + list(extra or [])
    proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=20)
    return proc.returncode, proc.stdout + proc.stderr


def cases(tool, scratch):
    out = {}
    escaped = {}

    # record-escape: a record row resolving outside --root must be refused.
    root, fleet, sibling = build(scratch, "record-escape")
    rec = record(root, [("../sibling", 1, 0)], (1, 1, 0))
    rc, text = invoke(tool, fleet, rec)
    out["record-escape"] = rc == 2 and "RECORD-OUTSIDE-ROOT" in text
    escaped["record"] = rc != 2

    # json-write-escape: the same row plus --json aimed into the sibling repo.
    target = os.path.join(sibling, "pwned.json")
    rc, text = invoke(tool, fleet, rec, extra=["--json", target])
    out["json-write-escape"] = rc == 2 and not os.path.exists(target)
    escaped["json-write"] = os.path.exists(target)

    # trace-refs: a path-valued GIT_TRACE_REFS must not be honoured.
    root, fleet, sibling = build(scratch, "trace-refs")
    rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], (2, 2, 0))
    trace = os.path.join(root, "trace-refs.log")
    rc, text = invoke(tool, fleet, rec, env_extra={"GIT_TRACE_REFS": trace})
    out["trace-refs"] = not os.path.exists(trace)
    escaped["trace-refs"] = os.path.exists(trace)

    # env-witness: the child git process must see a config-neutralised
    # environment. A PATH shim git records its own env, so the observation is
    # bound to the executable the tool selected (r36 W3: the scrub removed
    # GIT_CONFIG_NOSYSTEM / GIT_CONFIG_GLOBAL / GIT_CONFIG_SYSTEM and inherited
    # GIT_CONFIG_COUNT / GIT_CONFIG_PARAMETERS, so trace2 targets from real or
    # injected config were honoured).
    root, fleet, sibling = build(scratch, "env-witness")
    rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], (2, 2, 0))
    witness = os.path.join(root, "child-env")
    shim = os.path.join(root, "shim")
    os.makedirs(shim)
    shim_git = os.path.join(shim, "git")
    write(shim_git, "#!/bin/sh\n{ env | sort; } > %s\necho 'worktree /x'\nexit 0\n" % witness)
    os.chmod(shim_git, 0o755)
    shim_path = shim + ":" + ENV["PATH"]
    rc, text = invoke(
        tool,
        fleet,
        rec,
        env_extra={
            "PATH": shim_path,
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "trace2.eventTarget",
            "GIT_CONFIG_VALUE_0": os.path.join(root, "trace2-count"),
            "GIT_CONFIG_PARAMETERS": "'trace2.eventTarget=%s'" % os.path.join(root, "trace2-parameters"),
        },
    )
    seen = ""
    if os.path.exists(witness):
        seen = open(witness, encoding="utf-8", errors="replace").read()
    # r37 A2 (wave seat W1CritC2): four literal conjuncts let a blacklist built
    # from exactly those four names pass. The witness now asserts the property:
    # no GIT_* key outside the declared allowlist, and the three config keys at
    # their neutral values.
    allowed = {
        "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM",
        "GIT_ATTR_NOSYSTEM", "GIT_OPTIONAL_LOCKS", "GIT_TERMINAL_PROMPT",
    }
    pairs = {}
    for line in seen.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            pairs[key] = value
    stray = sorted(k for k in pairs if k.startswith("GIT_") and k not in allowed)
    escaped["env"] = bool(stray)
    out["env-witness"] = (
        not stray
        and pairs.get("GIT_CONFIG_NOSYSTEM") == "1"
        and pairs.get("GIT_CONFIG_GLOBAL") == "/dev/null"
        and pairs.get("GIT_CONFIG_SYSTEM") == "/dev/null"
        and not os.path.exists(os.path.join(root, "trace2-count"))
        and not os.path.exists(os.path.join(root, "trace2-parameters"))
    )

    # json-inside: the r36 A2 containment regression (both ends must refuse).
    root, fleet, sibling = build(scratch, "json-inside")
    rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], (2, 2, 0))
    leak = os.path.join(fleet, "alpha", "leak.json")
    rc, text = invoke(tool, fleet, rec, extra=["--json", leak])
    out["json-inside"] = rc == 2 and not os.path.exists(leak)

    # trace2-event: the r36 A2 scrub regression (both ends must scrub).
    root, fleet, sibling = build(scratch, "trace2-event")
    rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], (2, 2, 0))
    trace = os.path.join(root, "trace2-event.log")
    rc, text = invoke(tool, fleet, rec, env_extra={"GIT_TRACE2_EVENT": trace})
    out["trace2-event"] = not os.path.exists(trace)

    # json-hardlink: realpath cannot resolve a hardlink; a multi-link target is
    # an inode inside a measured repository.
    root, fleet, sibling = build(scratch, "json-hardlink")
    rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], (2, 2, 0))
    outdir = os.path.join(root, "out")
    os.makedirs(outdir)
    link = os.path.join(outdir, "pwned.json")
    victim = os.path.join(fleet, "alpha", "file.txt")
    before_bytes = open(victim, "rb").read()
    os.link(victim, link)
    rc, text = invoke(tool, fleet, rec, extra=["--json", link])
    out["json-hardlink"] = (
        rc == 2 and "JSON-HARDLINKED" in text
        and open(victim, "rb").read() == before_bytes
    )
    escaped["hardlink"] = open(victim, "rb").read() != before_bytes

    # record-fifo: a FIFO record must be refused, not block.
    root, fleet, sibling = build(scratch, "record-fifo")
    fifo = os.path.join(root, "record.fifo")
    os.mkfifo(fifo)
    try:
        rc, text = invoke(tool, fleet, fifo)
    except subprocess.TimeoutExpired:
        rc, text = 124, "timeout"
    out["record-fifo"] = rc == 2 and "not a regular file" in text
    escaped["fifo"] = rc != 2

    # json-gitfile-write: a record row whose .git FILE points outside --root is
    # measured there, so --json into that gitdir must be refused.
    root, fleet, sibling = build(scratch, "json-gitfile")
    outside = make_repo(os.path.join(root, "outside-repo"))
    victim = os.path.join(outside, "file.txt")
    before_bytes = open(victim, "rb").read()
    alpha = os.path.join(fleet, "alpha")
    shutil.rmtree(alpha)
    os.makedirs(alpha)
    write(os.path.join(alpha, ".git"), "gitdir: %s\n" % os.path.join(outside, ".git"))
    rec = record(root, [("alpha", 1, 0)], (1, 1, 0))
    rc, text = invoke(tool, fleet, rec, extra=["--json", victim])
    out["json-gitfile-write"] = (
        rc == 2 and "RECORD-OUTSIDE-ROOT" in text
        and open(victim, "rb").read() == before_bytes
    )
    escaped["gitfile"] = open(victim, "rb").read() != before_bytes

    # json-symlink-child: an unrecorded symlinked child must not be measured, so
    # --json into its target is outside every measured repository.
    root, fleet, sibling = build(scratch, "json-symlink-child")
    target_repo = make_repo(os.path.join(root, "target-repo"))
    victim = os.path.join(target_repo, "file.txt")
    before_bytes = open(victim, "rb").read()
    os.symlink(target_repo, os.path.join(fleet, "zlink"))
    rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], (2, 2, 0))
    rc, text = invoke(tool, fleet, rec, extra=["--json", victim])
    # the point is that zlink is not *measured* (so the --json target is outside
    # every measured repository); the explicit outside path is allowed by design.
    out["json-symlink-child"] = "zlink" not in text
    escaped["symlink-child"] = "zlink" in text

    # record-symlink: a record row that is a symlink to an out-of-root repository
    # must be refused (abspath-only containment re-opens the r36 W1 write).
    root, fleet, sibling = build(scratch, "record-symlink")
    os.symlink(sibling, os.path.join(fleet, "gamma"))
    target = os.path.join(sibling, "pwned2.json")
    rec = record(root, [("gamma", 1, 0)], (1, 1, 0))
    rc, text = invoke(tool, fleet, rec, extra=["--json", target])
    out["record-symlink"] = rc == 2 and "RECORD-OUTSIDE-ROOT" in text and not os.path.exists(target)
    escaped["row-symlink"] = os.path.exists(target)

    # measured: a fixed-summary stub must fail the required measured drift.
    root, fleet, sibling = build(scratch, "measured")
    rec = record(root, [("alpha", 2, 0), ("beta", 1, 0)], (2, 3, 0))
    rc, text = invoke(tool, fleet, rec)
    out["measured"] = rc == 1 and "REGS-CHANGED\talpha" in text and "drift_rows=1" in text
    return out, escaped


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool")
    ap.add_argument("--base-tool")
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tool = args.tool or os.path.join(lane_root, "tools", "souji-worktree-drift.py")
    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
    if not os.path.isdir(work):
        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
        return 2
    scratch = tempfile.mkdtemp(prefix="souji-r37-escapes.", dir=work)
    try:
        cand_scratch = os.path.join(scratch, "candidate")
        os.makedirs(cand_scratch)
        candidate, _ = cases(tool, cand_scratch)
        if args.base_tool:
            base_scratch = os.path.join(scratch, "base")
            os.makedirs(base_scratch)
            base, base_escaped = cases(args.base_tool, base_scratch)
        else:
            base = None
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    for name, ok in candidate.items():
        print("case-%s=%s" % (name, "PASS" if ok else "FAIL"))
    failed = sum(1 for ok in candidate.values() if not ok)
    if base is None:
        print("SUMMARY cases=%d pass=%d fail=%d base_fail=0 control=NO-BASE-TOOL" % (len(candidate), len(candidate) - failed, failed))
        # r37 A2 (wave seat W1ExecEscapes F2): the exit contract requires a
        # reproduced control; a control-free run is not a pass.
        return 1
    base_fail = sum(1 for ok in base.values() if not ok)
    escapes = sum(1 for v in base_escaped.values() if v)
    # r37 A2.5 (wave seat W2RevRerunC2): a fail count also rises when the base
    # tool merely errors. The control requires the base to be observed writing
    # the escapes themselves (>=4 of 6 artifacts), plus the case floor.
    control_ok = base_fail >= 8 and escapes >= 6
    print("SUMMARY cases=%d pass=%d fail=%d base_fail=%d escapes=%d control=%s" % (
        len(candidate), len(candidate) - failed, failed, base_fail, escapes,
        "ESCAPE-REPRODUCED" if control_ok else "ESCAPE-NOT-REPRODUCED"))
    return 0 if failed == 0 and control_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
