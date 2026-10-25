#!/usr/bin/env python3
"""souji-size-census -- read-only F2 debris census (round 24, claim C1).

CLI: python3 -B tools/souji-size-census.py --repo PATH | --help

PATH may be a work tree (main or linked), any subdirectory of one, or a bare
repository; discovery is `git -C PATH rev-parse`. Every census command runs
against the resolved COMMON git dir (`--git-dir=<common>`), so a linked
worktree reports the common-dir figure: `git -C <linked> count-objects -v`
counts <common>/worktrees/<id>/refs as garbage, `--git-dir=<common>` does not.

Read-only envelope: inherited GIT_* variables (incl. GIT_OBJECT_DIRECTORY,
  GIT_ALTERNATE_OBJECT_DIRECTORIES) are dropped, then
  GIT_OPTIONAL_LOCKS=0 (no optional locks), GIT_NO_LAZY_FETCH=1 (no promisor
  fetch), GIT_TERMINAL_PROMPT=0, GIT_NO_REPLACE_OBJECTS=1, LC_ALL=C;
  -c maintenance.auto=false -c gc.auto=0 -c core.fsmonitor=false;
  never `cd`, never a shell string: argv lists only, stdin is /dev/null.
Commands: `count-objects -v`, `fsck --unreachable --no-reflogs --no-progress`.
`fsck --lost-found` writes .git/lost-found/ and is never run; `--lost-found`
on this tool's argv is refused like any unknown argument.
Promisor/partial-clone repositories are refused (exit 2) before any walk:
`extensions.partialClone` set, any `remote.*.promisor` true, or any
`objects/pack/*.promisor` file (a blobless clone keeps it after its config is
stripped).

Output (stdout, only on success, one key=value per line):
  census.tool=souji-size-census
  census.status=ok
  census.git_version=<verbatim `git --version`>
  census.common_dir=<absolute common git dir>
  census.invoked_from=main|linked|bare
  count.<field>=<value>   every `count-objects -v` line, `-` -> `_` (repeats)
  census.warning=<verbatim `warning: garbage found:` stderr line>
  census.unreachable_scope=includes-alternates            (only if A > 0)
  garbage=G size_garbage=K unreachable=U alternates=A     (always last)
alternates = `alternate: ` lines of `count-objects -v` (git's resolved list,
not the raw objects/info/alternates file); unreachable = fsck stdout lines
starting `unreachable `. fsck follows alternates, so U then includes their
debris; it is not filtered.

Exit codes
  0  census ran
  1  git failure: git missing, non-zero git exit, or any stderr other than
     `warning: garbage found:` lines, e.g. any `error:` line (a missing
     alternate path is such a line; an empty repository's fsck prints
     `notice: No default references` and therefore exits 1)
  2  refused: usage / unknown argv, PATH not a repository (rev-parse exit
     non-zero), promisor or partial-clone repository
"""
import os
import subprocess
import sys

TOOL = "souji-size-census"
CONFIG = ("-c", "maintenance.auto=false", "-c", "gc.auto=0",
          "-c", "core.fsmonitor=false")
GARBAGE_WARNING = "warning: garbage found: "
USAGE = "usage: python3 -B tools/souji-size-census.py --repo PATH\n"


class Refused(Exception):
    pass


class GitFailure(Exception):
    pass


def git_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1",
               GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1",
               LC_ALL="C")
    return env


def git(env, *args):
    argv = ["git", *CONFIG, *args]
    try:
        p = subprocess.run(argv, env=env, stdin=subprocess.DEVNULL,
                           capture_output=True)
    except OSError as e:
        raise GitFailure(f"cannot run git: {e}") from None
    dec = lambda b: b.decode("utf-8", "surrogateescape")
    return p.returncode, dec(p.stdout), dec(p.stderr), argv


def fail_text(argv, rc, err):
    return f"{' '.join(argv)} exited {rc}: {err.strip() or '(no stderr)'}"


def checked(env, *args):
    rc, out, err, argv = git(env, *args)
    if rc != 0 or err:
        raise GitFailure(fail_text(argv, rc, err))
    return out


def parse_argv(argv):
    if argv in (["--help"], ["-h"]):
        sys.stdout.write(__doc__)
        sys.exit(0)
    if len(argv) != 2 or argv[0] != "--repo" or not argv[1]:
        raise Refused("unknown or missing arguments: " + " ".join(argv))
    return argv[1]


def resolve(env, path):
    rc, out, err, argv = git(env, "-C", path, "rev-parse",
                             "--path-format=absolute", "--git-common-dir",
                             "--git-dir", "--is-bare-repository")
    if rc != 0:
        raise Refused("not a repository: " + fail_text(argv, rc, err))
    lines = out.split("\n")
    if err or len(lines) < 3:
        raise GitFailure(fail_text(argv, rc, err))
    common, gitdir, bare = lines[0], lines[1], lines[2]
    if bare == "true":
        return common, "bare"
    return common, ("main" if os.path.realpath(gitdir) ==
                    os.path.realpath(common) else "linked")


def refuse_promisor(env, path, common):
    rc, out, err, argv = git(env, "-C", path, "config", "--get",
                             "extensions.partialClone")
    if rc == 0:
        raise Refused("partial-clone repository (extensions.partialClone="
                      + out.strip() + ")")
    if rc != 1 or err:
        raise GitFailure(fail_text(argv, rc, err))
    rc, out, err, argv = git(env, "-C", path, "config", "--type=bool",
                             "--get-regexp", r"^remote\..*\.promisor$")
    if rc not in (0, 1) or err:
        raise GitFailure(fail_text(argv, rc, err))
    for line in out.splitlines():
        if line.rsplit(" ", 1)[-1] == "true":
            raise Refused("promisor remote (" + line + ")")
    pack = os.path.join(common, "objects", "pack")
    if os.path.isdir(pack):
        for name in sorted(os.listdir(pack)):
            if name.endswith(".promisor"):
                raise Refused("promisor pack (objects/pack/" + name + ")")


def count_objects(env, common):
    rc, out, err, argv = git(env, "--git-dir=" + common, "count-objects", "-v")
    warnings = err.splitlines()
    if rc != 0 or any(not w.startswith(GARBAGE_WARNING) for w in warnings):
        raise GitFailure(fail_text(argv, rc, err))
    fields = []
    for line in out.splitlines():
        key, sep, value = line.partition(": ")
        if not sep or not key:
            raise GitFailure("unparsable count-objects line: " + line)
        fields.append((key.replace("-", "_"), value))
    if not {"garbage", "size_garbage"} <= {k for k, _ in fields}:
        raise GitFailure("count-objects -v lacks garbage/size-garbage")
    return fields, warnings


def unreachable(env, common):
    out = checked(env, "--git-dir=" + common, "fsck", "--unreachable",
                  "--no-reflogs", "--no-progress")
    return sum(1 for line in out.splitlines() if line.startswith("unreachable "))


def census(path):
    env = git_env()
    version = checked(env, "--version").strip()
    common, invoked_from = resolve(env, path)
    refuse_promisor(env, path, common)
    fields, warnings = count_objects(env, common)
    u = unreachable(env, common)
    a = sum(1 for k, _ in fields if k == "alternate")
    value = dict(fields)
    out = [f"census.tool={TOOL}", "census.status=ok",
           f"census.git_version={version}", f"census.common_dir={common}",
           f"census.invoked_from={invoked_from}"]
    out += [f"count.{k}={v}" for k, v in fields]
    out += [f"census.warning={w}" for w in warnings]
    if a:
        out.append("census.unreachable_scope=includes-alternates")
    out.append(f"garbage={value['garbage']} size_garbage={value['size_garbage']}"
               f" unreachable={u} alternates={a}")
    return "".join(line + "\n" for line in out)


def main(argv):
    try:
        text = census(parse_argv(argv))
    except Refused as e:
        sys.stderr.write(f"{TOOL}: refused: {e}\n{USAGE}")
        return 2
    except GitFailure as e:
        sys.stderr.write(f"{TOOL}: git failure: {e}\n")
        return 1
    sys.stdout.buffer.write(text.encode("utf-8", "surrogateescape"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
