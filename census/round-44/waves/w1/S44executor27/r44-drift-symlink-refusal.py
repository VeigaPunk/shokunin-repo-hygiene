#!/usr/bin/env python3
"""Behavioral contract battery for refusing --json leaf symlinks.

Every case creates an isolated synthetic git fleet, invokes the supplied tool,
and checks its observable status, refusal output, and filesystem effects.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

TOKEN = "JSON-TARGET-SYMLINK"
ENV = dict(os.environ, LC_ALL="C", GIT_AUTHOR_NAME="fixture",
           GIT_COMMITTER_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
           GIT_COMMITTER_EMAIL="fixture@example.invalid")


def write(path, data):
    with open(path, "w", encoding="utf-8") as stream:
        stream.write(data)


def make_fleet(base):
    repo = os.path.join(base, "fleet", "alpha")
    os.makedirs(repo)
    def run(args):
        return subprocess.run(args, env=ENV, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, check=False)
    init = run(["git", "init", "-q", "-b", "main", repo])
    if init.returncode:
        raise RuntimeError("git init failed: %r" % init.stderr)
    write(os.path.join(repo, "file.txt"), "base\n")
    for args in (["git", "-C", repo, "add", "file.txt"],
                 ["git", "-C", repo, "commit", "-qm", "base"]):
        proc = run(args)
        if proc.returncode:
            raise RuntimeError("git setup failed: %r" % proc.stderr)
    record = os.path.join(base, "record.tsv")
    write(record, "REPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return os.path.join(base, "fleet"), record


def invoke(tool, root, record, target):
    try:
        p = subprocess.run([sys.executable, "-B", tool, "--root", root,
                            "--record", record, "--timeout", "30", "--json", target],
                           env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, timeout=15, check=False)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"


def test(tool, scratch, name, setup):
    base = os.path.join(scratch, name)
    os.makedirs(base)
    root, record = make_fleet(base)
    target, expected = setup(base)
    rc, output = invoke(tool, root, record, target)
    ok = expected(rc, output)
    return name, ok, "rc=%r output=%r" % (rc, output.splitlines()[:2])


def cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="r44-symlink-", dir=work)
    results = []
    try:
        def dangling(base):
            target, victim = os.path.join(base, "link.json"), os.path.join(base, "missing.json")
            os.symlink(victim, target)
            return target, lambda rc, out: rc == 2 and TOKEN in out and not os.path.lexists(victim)
        def existing(base):
            victim, target = os.path.join(base, "victim.json"), os.path.join(base, "link.json")
            write(victim, "keep\n")
            os.symlink(victim, target)
            return target, lambda rc, out: rc == 2 and TOKEN in out and open(victim, encoding="utf-8").read() == "keep\n"
        def nested(base):
            folder = os.path.join(base, "nested")
            os.mkdir(folder)
            target = os.path.join(folder, "link.json")
            os.symlink(os.path.join(folder, "missing.json"), target)
            return target, lambda rc, out: rc == 2 and TOKEN in out and not os.path.lexists(os.path.join(folder, "missing.json"))
        def directory(base):
            victim, target = os.path.join(base, "directory"), os.path.join(base, "link.json")
            os.mkdir(victim)
            return (os.symlink(victim, target) or target), lambda rc, out: rc == 2 and TOKEN in out and os.path.isdir(victim) and not os.path.isfile(os.path.join(victim, "record.tsv"))
        def regular(base):
            target = os.path.join(base, "normal", "out.json")
            os.mkdir(os.path.dirname(target))
            def expected(rc, out):
                try:
                    with open(target, encoding="utf-8") as stream:
                        json.load(stream)
                    return rc in (0, 1)
                except (OSError, ValueError):
                    return False
            return target, expected
        def parent_link(base):
            real = os.path.join(base, "real")
            os.mkdir(real)
            link = os.path.join(base, "parent")
            os.symlink(real, link)
            target = os.path.join(link, "out.json")
            return target, lambda rc, out: rc in (0, 1) and os.path.isfile(os.path.join(real, "out.json"))
        for name, setup in (("dangling-leaf-refused", dangling),
                            ("existing-file-leaf-refused", existing),
                            ("nested-leaf-refused", nested),
                            ("directory-target-refused", directory),
                            ("ordinary-output-written", regular),
                            ("symlinked-parent-allowed", parent_link)):
            try:
                results.append(test(tool, scratch, name, setup))
            except (OSError, RuntimeError) as exc:
                results.append((name, False, "setup/invocation error: %s" % exc))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return results


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", required=True)
    parser.add_argument("--work", required=True)
    args = parser.parse_args(argv)
    if not os.path.isdir(args.work):
        print("usage: --work must name an existing directory", file=sys.stderr)
        return 2
    results = cases(args.tool, os.path.abspath(args.work))
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    passed = sum(ok for _, ok, _ in results)
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(results), passed, len(results) - passed))
    return 0 if results and passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
