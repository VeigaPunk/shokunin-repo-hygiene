#!/usr/bin/env python3
"""R42w2mutationtester06 — differential oracle: is a surviving mutant behaviour-equivalent?

For each surviving mutant the oracle builds the SAME scenario twice (once for the pristine
tool, once for the mutant), runs the tool in both, and compares the observable surface:
exit code, stdout, stderr and the --json document. A scenario pair that differs proves the
mutant is NOT equivalent; a mutant that differs nowhere across the whole battery is
reported as equivalent *for this battery* (the battery is enumerated in the report).

Nothing is written inside the lane: everything lives under --scratch.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
SCENARIOS = []


def scenario(fn):
    SCENARIOS.append(fn)
    return fn


def env(work):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": work,
         "HOME": work, "LC_ALL": "C"}
    e.update(GIT_ENV)
    return e


def sh(cmd, cwd=None, e=None, check=False):
    return subprocess.run(cmd, cwd=cwd, env=e, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=check)


def init_repo(path, bare=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cmd = ["git", "init", "-q"] + (["--bare"] if bare else []) + [path]
    sh(cmd, check=True)


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as h:
        h.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def run_tool(tool, work, args, timeout=60, env_extra=None):
    e = env(work)
    if env_extra:
        e.update(env_extra)
    try:
        p = subprocess.run([sys.executable, "-B", tool] + args, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=e, timeout=timeout, cwd=work)
        return {"rc": p.returncode, "out": p.stdout.decode("utf-8", "replace"),
                "err": p.stderr.decode("utf-8", "replace")}
    except subprocess.TimeoutExpired:
        return {"rc": "TIMEOUT", "out": "", "err": ""}


def normalise(text, work, tool=None):
    """Erase the per-run absolute paths so the two runs are comparable."""
    if tool:
        # argparse prints the script path in its usage message; the mutant blob has a
        # different file name, so erase it or every mutant looks different.
        text = text.replace(os.path.abspath(tool), "<TOOL>")
        text = text.replace(os.path.basename(tool), "<TOOL>")
    text = text.replace(work, "<W>")
    text = re.sub(r"/tmp/[A-Za-z0-9_.\-]+", "<T>", text)
    text = re.sub(r"in \d+\.\d+s", "in <T>s", text)
    return text


def build(work, name):
    """Return a callable that materialises the scenario and returns the tool argv."""
    root = os.path.join(work, "root")
    rec_dir = os.path.join(work, "rec")
    os.makedirs(root)
    os.makedirs(rec_dir)

    def repo(sub, bare=False):
        init_repo(os.path.join(root, sub), bare=bare)
        return os.path.join(root, sub)

    def record(text, fname="record.tsv"):
        return write(os.path.join(rec_dir, fname), text)

    return root, rec_dir, repo, record


# --- scenarios ---------------------------------------------------------------

@scenario
def s_match(w, root, repo, record):
    repo("alpha")
    repo("beta")
    rec = record("REPO\talpha\tregs=1\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\n"
                 "TOTAL\trepos=2\tregs=2\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_regs_changed(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=2\tprunable=0\nTOTAL\trepos=1\tregs=2\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_absent(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\nREPO\tgone\tregs=1\tprunable=0\n"
                 "TOTAL\trepos=2\tregs=2\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_unrecorded(w, root, repo, record):
    repo("alpha")
    repo("gamma")
    rec = record("REPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_unrecorded_skipped(w, root, repo, record):
    repo("alpha")
    repo("gamma")
    rec = record("REPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec, "--skip-unrecorded"], None


@scenario
def s_root_is_repo(w, root, repo, record):
    init_repo(root)
    init_repo(os.path.join(root, "alpha"))
    rec = record("REPO\t%s\tregs=1\tprunable=0\n" % os.path.basename(root))
    return ["--root", root, "--record", rec], None


@scenario
def s_root_is_repo_trailing_slash(w, root, repo, record):
    init_repo(root)
    init_repo(os.path.join(root, "alpha"))
    rec = record("REPO\t%s\tregs=1\tprunable=0\n" % os.path.basename(root))
    return ["--root", root + "/", "--record", rec], None


@scenario
def s_total_mismatch(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=2\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_empty(w, root, repo, record):
    rec = record("TOTAL\trepos=0\tregs=0\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_duplicate_name(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_comments_blanks(w, root, repo, record):
    repo("alpha")
    rec = record("# comment\n\nREPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_malformed_line(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\njunk row\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_two_totals(w, root, repo, record):
    repo("alpha")
    rec = record("TOTAL\trepos=1\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n"
                 "TOTAL\trepos=1\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_two_totals_second_disagrees(w, root, repo, record):
    repo("alpha")
    rec = record("TOTAL\trepos=1\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n"
                 "TOTAL\trepos=9\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_missing_record(w, root, repo, record):
    repo("alpha")
    return ["--root", root, "--record", os.path.join(root, "nope.tsv")], None


@scenario
def s_record_outside_root(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\t../outside\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_record_is_dir(w, root, repo, record):
    repo("alpha")
    d = os.path.join(root, "adir")
    os.makedirs(d)
    return ["--root", root, "--record", d], None


@scenario
def s_root_not_a_dir(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", os.path.join(root, "alpha"), "--record", rec], None


@scenario
def s_timeout_zero(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec, "--timeout", "0"], None


@scenario
def s_timeout_one(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec, "--timeout", "1"], None


@scenario
def s_missing_root_option(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--record", rec], None


@scenario
def s_missing_record_option(w, root, repo, record):
    repo("alpha")
    return ["--root", root], None


@scenario
def s_json_plain(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    out = os.path.join(w, "out.json")
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_json_with_drift(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=9\tprunable=0\n")
    out = os.path.join(w, "out.json")
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_json_overwrites_longer_file(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    out = os.path.join(w, "out.json")
    write(out, "X" * 5000)
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_json_inside_root(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    out = os.path.join(root, "out.json")
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_json_inside_measured_repo(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    out = os.path.join(root, "alpha", "out.json")
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_json_is_record(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec, "--json", rec], rec


@scenario
def s_json_symlink_leaf(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    target = os.path.join(w, "target.json")
    write(target, "OLD")
    link = os.path.join(w, "link.json")
    os.symlink(target, link)
    return ["--root", root, "--record", rec, "--json", link], target


@scenario
def s_json_symlink_parent(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    real = os.path.join(w, "real")
    os.makedirs(real)
    link = os.path.join(w, "link")
    os.symlink(real, link)
    out = os.path.join(link, "out.json")
    return ["--root", root, "--record", rec, "--json", out], os.path.join(real, "out.json")


@scenario
def s_json_is_dir(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    out = os.path.join(w, "adir")
    os.makedirs(out)
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_json_hardlink_to_record(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    link = os.path.join(w, "alias.tsv")
    os.link(rec, link)
    return ["--root", root, "--record", rec, "--json", link], None


@scenario
def s_json_hardlink_other(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    other = write(os.path.join(w, "other.json"), "OLD")
    link = os.path.join(w, "alias.json")
    os.link(other, link)
    return ["--root", root, "--record", rec, "--json", link], other


@scenario
def s_json_unwritable_dir(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    d = os.path.join(w, "ro")
    os.makedirs(d)
    os.chmod(d, 0o555)
    out = os.path.join(d, "out.json")
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_symlinked_child_not_discovered(w, root, repo, record):
    repo("alpha")
    repo("beta")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    os.symlink(os.path.join(root, "beta"), os.path.join(root, "lnk"))
    return ["--root", root, "--record", rec], None


@scenario
def s_gitfile_child(w, root, repo, record):
    """A child whose .git is a FILE (a linked worktree) is a repository too."""
    repo("alpha")
    other = os.path.join(w, "other")
    init_repo(other)
    os.makedirs(os.path.join(root, "linked"))
    write(os.path.join(root, "linked", ".git"), "gitdir: %s/.git\n" % other)
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_record_gitfile_child(w, root, repo, record):
    repo("alpha")
    other = os.path.join(w, "other")
    init_repo(other)
    os.makedirs(os.path.join(root, "linked"))
    write(os.path.join(root, "linked", ".git"), "gitdir: %s/.git\n" % other)
    rec = record("REPO\tlinked\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_invalid_utf8_name(w, root, repo, record):
    repo("alpha")
    rec = record(b"REPO\ta\xffb\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_invalid_utf8_comment(w, root, repo, record):
    repo("alpha")
    rec = record(b"# c\xff\nREPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_prunable_changed(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=1\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_two_digit_regs(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=10\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_root_basename_row(w, root, repo, record):
    repo("alpha")
    init_repo(root)
    rec = record("REPO\t%s\tregs=1\tprunable=0\n" % os.path.basename(root))
    return ["--root", root, "--record", rec], None


@scenario
def s_root_basename_row_other(w, root, repo, record):
    """The record names the root's basename but --root is not a repository."""
    repo("alpha")
    rec = record("REPO\t%s\tregs=1\tprunable=0\n" % os.path.basename(root))
    return ["--root", root, "--record", rec], None


@scenario
def s_json_relative_path(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec, "--json", "rel.json"], "rel.json"


@scenario
def s_json_dot_component(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    out = os.path.join(w, ".", "out.json")
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_list_rc_nonzero(w, root, repo, record):
    """A child whose .git is a FILE pointing at a missing gitdir: git fails."""
    os.makedirs(os.path.join(root, "broken"))
    write(os.path.join(root, "broken", ".git"), "gitdir: /nonexistent/gitdir\n")
    rec = record("REPO\tbroken\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_json_root_slash(w, root, repo, record):
    """--json "/" : the only absolute path whose component list is empty."""
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec, "--json", "/"], None


@scenario
def s_json_relative_subdir(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec, "--json", "sub/out.json"], None


@scenario
def s_json_missing_parent(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    out = os.path.join(w, "nope", "out.json")
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_json_double_slash(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    out = os.path.join(w, "out.json")
    return ["--root", root, "--record", rec, "--json", out.replace("/", "//", 1)], out


@scenario
def s_record_trailing_slash(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec + "/"], None


@scenario
def s_root_dot_slash(w, root, repo, record):
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", "./" + os.path.basename(root), "--record", rec], None


def fake_git_dir(work, mode):
    """A directory holding a `git` shim that proxies the real git but replaces the
    `worktree prune` call according to `mode`:
      hang  -> the prune call blocks forever
      rc3   -> the prune call exits 3 after writing one candidate line
      blank -> the prune call writes blank lines around one candidate line
    Every other git call (including `worktree list` and `rev-parse`) is the real git.
    """
    d = os.path.join(work, "fakebin")
    os.makedirs(d, exist_ok=True)
    real = shutil.which("git") or "/usr/bin/git"
    path = os.path.join(d, "git")
    with open(path, "w") as h:
        h.write("#!/usr/bin/env python3\n"
                "import os, subprocess, sys\n"
                "REAL = %r\n"
                "MODE = %r\n"
                "args = sys.argv[1:]\n"
                "is_prune = 'prune' in args and 'worktree' in args\n"
                "if is_prune and MODE == 'hang':\n"
                "    import time; time.sleep(30)\n"
                "if is_prune and MODE == 'rc3':\n"
                "    sys.stderr.write('Removing worktrees/x: gitdir file points to non-existent location\\n')\n"
                "    sys.exit(3)\n"
                "if is_prune and MODE == 'blank':\n"
                "    sys.stderr.write('\\n\\nRemoving worktrees/x: gitdir file points to non-existent location\\n\\n')\n"
                "    sys.exit(0)\n"
                "if is_prune and MODE == 'ws':\n"
                "    sys.stderr.write('   \\nRemoving worktrees/x: gitdir file points to non-existent location\\n')\n"
                "    sys.exit(0)\n"
                "if MODE == 'badutf8' and 'list' in args:\n"
                "    sys.stdout.buffer.write(b'worktree /root/\\xff\\xfe\\nHEAD 1234\\n')\n"
                "    sys.exit(0)\n"
                "os.execv(REAL, [REAL] + args)\n"
                % (real, mode))
    os.chmod(path, 0o755)
    return d


@scenario
def s_prune_hangs(w, root, repo, record):
    """The prune call blocks until the tool's --timeout fires."""
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    d = fake_git_dir(w, "hang")
    return (["--root", root, "--record", rec, "--timeout", "2"], None,
            {"PATH": d + ":" + os.environ.get("PATH", "")})


@scenario
def s_prune_rc_nonzero(w, root, repo, record):
    """The prune call exits nonzero (git worktree prune failed)."""
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    d = fake_git_dir(w, "rc3")
    return (["--root", root, "--record", rec], None,
            {"PATH": d + ":" + os.environ.get("PATH", "")})


@scenario
def s_prune_blank_lines(w, root, repo, record):
    """The prune call writes blank lines around its one candidate line."""
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=1\n")
    d = fake_git_dir(w, "blank")
    return (["--root", root, "--record", rec], None,
            {"PATH": d + ":" + os.environ.get("PATH", "")})


@scenario
def s_prune_whitespace_line(w, root, repo, record):
    """The prune call writes a whitespace-only stderr line beside its candidate line."""
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=1\n")
    d = fake_git_dir(w, "ws")
    return (["--root", root, "--record", rec], None,
            {"PATH": d + ":" + os.environ.get("PATH", "")})


@scenario
def s_list_output_invalid_utf8(w, root, repo, record):
    """`git worktree list --porcelain` prints bytes that are not valid UTF-8."""
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    d = fake_git_dir(w, "badutf8")
    return (["--root", root, "--record", rec], None,
            {"PATH": d + ":" + os.environ.get("PATH", "")})


@scenario
def s_invalid_utf8_worktree_path(w, root, repo, record):
    """A linked worktree whose path is not valid UTF-8: the list output carries raw bytes."""
    repo("alpha")
    bad = os.path.join(root, "wt\udcff")
    try:
        os.mkdir(bad)
    except OSError:
        return ["--root", root, "--record", record("REPO\talpha\tregs=1\tprunable=0\n")], None
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_unreadable_root(w, root, repo, record):
    """--root cannot be listed (mode 000): the listing raises OSError."""
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    os.chmod(root, 0o000)
    return ["--root", root, "--record", rec], None


@scenario
def s_root_is_repo_trailing_slash_unrecorded(w, root, repo, record):
    """--root is itself a repository and is written with a trailing slash; the record
    names only a child, so the root's own repository is an UNRECORDED candidate."""
    init_repo(root)
    init_repo(os.path.join(root, "alpha"))
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root + "/", "--record", rec], None


@scenario
def s_two_drift_rows(w, root, repo, record):
    """Two drift rows whose sorted order differs from the record order."""
    repo("alpha")
    rec = record("REPO\tzulu\tregs=1\tprunable=0\nREPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_root_git_is_a_file(w, root, repo, record):
    """--root's .git is a FILE (a linked worktree's gitdir pointer)."""
    repo("alpha")
    other = os.path.join(w, "other")
    init_repo(other)
    write(os.path.join(root, ".git"), "gitdir: %s/.git\n" % other)
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_root_git_is_a_file_self_named(w, root, repo, record):
    """--root's .git is a FILE and the record names the root's own basename."""
    repo("alpha")
    other = os.path.join(w, "other")
    init_repo(other)
    write(os.path.join(root, ".git"), "gitdir: %s/.git\n" % other)
    rec = record("REPO\t%s\tregs=1\tprunable=0\n" % os.path.basename(root))
    return ["--root", root, "--record", rec], None


@scenario
def s_two_drift_rows_reversed(w, root, repo, record):
    """Two REGS-CHANGED rows whose record order (zulu, alpha) differs from their sorted order."""
    repo("zulu")
    repo("alpha")
    rec = record("REPO\tzulu\tregs=2\tprunable=0\nREPO\talpha\tregs=2\tprunable=0\n"
                 "TOTAL\trepos=2\tregs=4\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_json_many_unrecorded(w, root, repo, record):
    """Twelve unrecorded repositories: the --json drift array order follows discover() order."""
    for n in ["kilo", "echo", "quebec", "alpha", "zulu", "mike", "bravo", "oscar", "tango", "hotel", "xray", "golf"]:
        repo(n)
    repo("anchor")
    rec = record("REPO\tanchor\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    out = os.path.join(w, "out.json")
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_json_root_repo_unrecorded_child(w, root, repo, record):
    """--root is itself a repository (unrecorded) next to an unrecorded child; --json writes the drift array."""
    init_repo(root)
    repo("beta")
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    out = os.path.join(w, "out.json")
    return ["--root", root, "--record", rec, "--json", out], out


@scenario
def s_root_gitfile_child_same_name(w, root, repo, record):
    """--root is a linked worktree (.git FILE) whose basename names a child repository: discover lists it twice."""
    other = os.path.join(w, "other")
    init_repo(other)
    write(os.path.join(root, ".git"), "gitdir: %s/.git\n" % other)
    repo("root")
    rec = record("REPO\tzz\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec], None


@scenario
def s_json_root_slash_only(w, root, repo, record):
    """--json "/" alone: the empty-component absolute path (the one target that reaches open_nofollow's parts guard)."""
    repo("alpha")
    rec = record("REPO\talpha\tregs=1\tprunable=0\n")
    return ["--root", root, "--record", rec, "--json", "/"], None


def run_one(tool, work, fn):
    root, rec_dir, repo, record = build(work, fn.__name__)
    if fn.__name__ == "s_unreadable_root":
        try:
            os.chmod(root, 0o700)
        except OSError:
            pass
    ret = fn(work, root, repo, record)
    argv, artifact = ret[0], ret[1]
    env_extra = ret[2] if len(ret) > 2 else None
    res = run_tool(tool, work, argv, env_extra=env_extra)
    res["out"] = normalise(res["out"], work, tool)
    res["err"] = normalise(res["err"], work, tool)
    art = None
    mode = None
    if artifact:
        path = artifact if os.path.isabs(artifact) else os.path.join(work, artifact)
        try:
            with open(path, "rb") as h:
                art = h.read().decode("utf-8", "replace")
            art = normalise(art, work, tool)
            mode = oct(os.stat(path).st_mode & 0o777)
        except OSError as exc:
            art = "<%s>" % exc.__class__.__name__
    res["artifact"] = art
    res["artifact_mode"] = mode
    return res


def classes(err):
    """The REFUSAL class tokens in stderr (the lane's refusal contract), plus a traceback flag."""
    found = re.findall(r"REFUSAL ([A-Z][A-Z0-9-]*)", err)
    return found, "Traceback (most recent call last)" in err


def compare(pristine, mutant):
    """Return (byte_diffs, sem_diffs).

    byte_diffs: any difference in rc, stdout, stderr text, the --json bytes or the --json mode.
    sem_diffs : any difference in rc, stdout (the DRIFT rows and SUMMARY), the refusal CLASS tokens,
                the traceback flag, the --json document as parsed JSON, or the --json mode.
                Message wording after the class token and JSON key order / whitespace are not semantic.
    """
    byte, sem = [], []
    if pristine["rc"] != mutant["rc"]:
        byte.append("rc %s != %s" % (pristine["rc"], mutant["rc"]))
        sem.append("rc %s != %s" % (pristine["rc"], mutant["rc"]))
    if pristine["out"] != mutant["out"]:
        byte.append("stdout differs")
        sem.append("stdout differs")
    if pristine["err"] != mutant["err"]:
        byte.append("stderr differs")
        pc, pt = classes(pristine["err"])
        mc, mt = classes(mutant["err"])
        if (pc, pt) != (mc, mt):
            sem.append("stderr class %s/tb=%s != %s/tb=%s" % (pc, pt, mc, mt))
    if pristine["artifact"] != mutant["artifact"]:
        byte.append("--json artifact bytes differ")
        try:
            same = json.loads(pristine["artifact"]) == json.loads(mutant["artifact"])
        except (ValueError, TypeError):
            same = False
        if not same:
            sem.append("--json document differs (parsed)")
    if pristine.get("artifact_mode") != mutant.get("artifact_mode"):
        byte.append("--json artifact mode differs (%s != %s)" % (pristine.get("artifact_mode"), mutant.get("artifact_mode")))
        sem.append("--json artifact mode differs (%s != %s)" % (pristine.get("artifact_mode"), mutant.get("artifact_mode")))
    return byte, sem


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--pristine", default=None)
    ap.add_argument("--mutants", nargs="*", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    scratch = a.scratch
    os.makedirs(scratch, exist_ok=True)
    pristine = a.pristine or os.path.join(scratch, "pristine.py")
    base = {}
    base_dir = os.path.join(scratch, "diff-base")
    os.makedirs(base_dir, exist_ok=True)
    for fn in SCENARIOS:
        work = tempfile.mkdtemp(prefix="b-", dir=base_dir)
        try:
            base[fn.__name__] = run_one(pristine, work, fn)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    result = {"baseline": base, "mutants": {}}
    for mid in (a.mutants or []):
        tool = os.path.join(scratch, "mut", "mut-%s.py" % mid)
        if not os.path.exists(tool):
            continue
        byte_hits, sem_hits = [], []
        mdir = os.path.join(scratch, "diff-" + mid)
        os.makedirs(mdir, exist_ok=True)
        for fn in SCENARIOS:
            work = tempfile.mkdtemp(prefix="m-", dir=mdir)
            try:
                got = run_one(tool, work, fn)
            finally:
                shutil.rmtree(work, ignore_errors=True)
            b, sm = compare(base[fn.__name__], got)
            if b:
                byte_hits.append({"scenario": fn.__name__, "diffs": b})
            if sm:
                sem_hits.append({"scenario": fn.__name__, "diffs": sm,
                                 "pristine": base[fn.__name__], "mutant": got})
        result["mutants"][mid] = {"byte": byte_hits, "sem": sem_hits, "n_scenarios": len(SCENARIOS)}
        verdict = ("SEMANTIC:" + "; ".join("%s:%s" % (x["scenario"], ",".join(x["diffs"])) for x in sem_hits)) if sem_hits else (
            "BYTE-ONLY:" + ",".join(x["scenario"] for x in byte_hits) if byte_hits else "EQUIVALENT")
        print("DIFF %-6s %s" % (mid, verdict[:400]))
    with open(a.out, "w") as h:
        json.dump(result, h, indent=1, sort_keys=True)
    print("WROTE %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
