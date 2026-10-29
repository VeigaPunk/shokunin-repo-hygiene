#!/usr/bin/env python3
"""R42w2mutationtester02 - generate single-point mutants of tools/souji-freeze-check.py (part B).

Reads the pristine tool bytes from the lane tip (git show), applies exactly one
string replacement per mutant, and writes each mutant under the seat's mutants/ dir.
The number of substitutions is asserted to be exactly 1 for every mutant.
"""
import os
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mutants")

# (name, description, old, new)
MUTANTS = [
    # ---- new grammar: HEADING-MALFORMED / KEY-DUPLICATE regexes and detectors
    ("M01-header-no-boundary",
     "HEADER regex drops the 'space or EOL' boundary: '## C2x' becomes a valid claim",
     'HEADER = re.compile(r"^## C(\\d+)(?: |$)")',
     'HEADER = re.compile(r"^## C(\\d+)")'),
    ("M02-badhead-never",
     "BADHEAD regex can never match: HEADING-MALFORMED is never reported",
     'BADHEAD = re.compile(r"^##(?!#) *[Cc] *\\d")',
     'BADHEAD = re.compile(r"^###(?!#) *[Cc] *\\d")'),
    ("M03-badhead-digit-optional",
     "BADHEAD digit made optional: every '## C<n>' heading is also malformed",
     'BADHEAD = re.compile(r"^##(?!#) *[Cc] *\\d")',
     'BADHEAD = re.compile(r"^##(?!#) *[Cc] *\\d*")'),
    ("M04-keyline-drop-kill",
     "KEYLINE no longer recognises the Kill key",
     'KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \\t]*(.*?)[ \\t]*$")',
     'KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target):[ \\t]*(.*?)[ \\t]*$")'),
    ("M05-keyline-allow-indent",
     "KEYLINE accepts indented key lines (grammar widening)",
     'KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \\t]*(.*?)[ \\t]*$")',
     'KEYLINE = re.compile(r"^[ \\t]*(Base|Counter|Population|Control|Target|Kill):[ \\t]*(.*?)[ \\t]*$")'),
    ("M06-dup-never-recorded",
     "a repeated key is never added to the duplicate set: KEY-DUPLICATE never fires",
     '                if m.group(1) in cur[1]:\n'
     '                    cur[2].add(m.group(1))\n',
     '                if m.group(1) in cur[1]:\n'
     '                    pass\n'),
    ("M07-dup-class-renamed",
     "KEY-DUPLICATE is reported under a different class name",
     'found.extend((label, "KEY-DUPLICATE", key) for key in sorted(dups))',
     'found.extend((label, "KEY-DUPLICATED", key) for key in sorted(dups))'),
    ("M08-dup-key-still-evaluated",
     "the duplicated key is no longer removed before evaluation (docstring says it is not evaluated)",
     '        for key in dups:\n'
     '            del f[key]  # ambiguous: reported above, not evaluated\n',
     '        for key in dups:\n'
     '            pass\n'),
    ("M09-dup-unsorted",
     "duplicates are reported in set order rather than sorted order",
     'found.extend((label, "KEY-DUPLICATE", key) for key in sorted(dups))',
     'found.extend((label, "KEY-DUPLICATE", key) for key in dups)'),
    # ---- symlink mode test
    ("M10-symlink-mode-no-space",
     "symlink mode test drops the trailing space (equivalent?)",
     'return p.returncode == 0 and p.stdout.startswith(b"120000 ")',
     'return p.returncode == 0 and p.stdout.startswith(b"120000")'),
    ("M11-symlink-mode-wrong",
     "symlink mode test uses the wrong mode string: symlinks are not detected",
     'return p.returncode == 0 and p.stdout.startswith(b"120000 ")',
     'return p.returncode == 0 and p.stdout.startswith(b"12000 ")'),
    ("M12-symlink-at-rev-not-freeze",
     "symlink is tested at REV instead of FREEZE-REV",
     '    if repo.is_symlink(freeze, path):\n',
     '    if repo.is_symlink(rev, path):\n'),
    ("M13-symlink-class-renamed",
     "the symlink finding class is renamed",
     'found.append((label, key.upper() + "-SYMLINK", "%s is a symlink at freeze %s" % (path, freeze[:12])))',
     'found.append((label, key.upper() + "-LINK", "%s is a symlink at freeze %s" % (path, freeze[:12])))'),
    ("M14-symlink-any-type",
     "is_symlink accepts any tree entry type, not only mode 120000",
     'return p.returncode == 0 and p.stdout.startswith(b"120000 ")',
     'return p.returncode == 0'),
    # ---- widened dispatch-name test
    ("M15-dispatch-drop-dispatch",
     "dispatch name test drops the '-dispatch' substring",
     'if "-dispatch" in base or ".ready" in base or base.endswith(("-spec.json", "-results.json")):',
     'if ".ready" in base or base.endswith(("-spec.json", "-results.json")):'),
    ("M16-dispatch-drop-ready",
     "dispatch name test drops the '.ready' substring",
     'if "-dispatch" in base or ".ready" in base or base.endswith(("-spec.json", "-results.json")):',
     'if "-dispatch" in base or base.endswith(("-spec.json", "-results.json")):'),
    ("M17-dispatch-drop-json",
     "dispatch name test drops the '-spec.json'/'-results.json' suffixes",
     'if "-dispatch" in base or ".ready" in base or base.endswith(("-spec.json", "-results.json")):',
     'if "-dispatch" in base or ".ready" in base:'),
    ("M18-dispatch-name-is-full-path",
     "dispatch name test uses the full path instead of the basename",
     'base = line.rsplit("/", 1)[-1]',
     'base = line'),
    ("M19-dispatch-ancestor-only-freeze",
     "dispatch check drops the ancestor test: only the freeze commit itself counts",
     'if c == freeze or repo.is_ancestor(c, freeze):',
     'if c == freeze:'),
    ("M20-dispatch-ancestor-only",
     "dispatch check drops the c == freeze shortcut",
     'if c == freeze or repo.is_ancestor(c, freeze):',
     'if repo.is_ancestor(c, freeze):'),
    ("M21-dispatch-first-setdefault",
     "the oldest adding commit is no longer kept (newest wins)",
     'first[line] = commit',
     'first.setdefault(line, commit)'),
    ("M22-dispatch-tree-no-slash",
     "the dispatch tree pathspec loses its trailing slash",
     'tree = ".ufo/waves/round-%s/" % m.group(1)',
     'tree = ".ufo/waves/round-%s" % m.group(1)'),
    ("M23-dispatch-missing-round-silent",
     "a missing Round line no longer yields FIELD-MISSING C0 Round",
     'return [("C0", "FIELD-MISSING", "Round")]',
     'return []'),
    # ---- claim / field evaluation
    ("M24-no-claims-removed",
     "the NO-CLAIMS finding is never raised",
     '        found.append(("C0", "NO-CLAIMS", "no \'## C<digits>\' block in %s" % prereg))\n',
     '        pass\n'),
    ("M25-keys-drop-kill",
     "the KEYS tuple drops Kill: a missing Kill key is not reported",
     'KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")',
     'KEYS = ("Base", "Counter", "Population", "Control", "Target")'),
    ("M26-field-empty-never",
     "an empty key value is never reported as FIELD-EMPTY",
     'if key in f and not f[key]:',
     'if key in f and f[key] is None:'),
    ("M27-heading-label-c1",
     "HEADING-MALFORMED findings are labelled C1 instead of C0",
     'found.extend(("C0", "HEADING-MALFORMED", "line=%d" % n) for n in bad)',
     'found.extend(("C1", "HEADING-MALFORMED", "line=%d" % n) for n in bad)'),
    ("M28-claim-label-shifted",
     "claim labels are off by one",
     'cur = ("C" + m.group(1), {}, set())',
     'cur = ("C" + str(int(m.group(1)) + 1), {}, set())'),
    ("M29-base-commit-no-full40",
     "the Base value is resolved even when it is not a full 40-hex id",
     'resolved = repo.commit(base) if FULL40.match(base) else None',
     'resolved = repo.commit(base)'),
    ("M30-base-not-ancestor-drop",
     "the BASE-NOT-ANCESTOR test loses the ancestor comparison",
     'elif resolved == freeze or not repo.is_ancestor(resolved, freeze):',
     'elif resolved == freeze:'),
    ("M31-base-ancestor-inverted",
     "the ancestor comparison is inverted",
     'elif resolved == freeze or not repo.is_ancestor(resolved, freeze):',
     'elif resolved == freeze or repo.is_ancestor(resolved, freeze):'),
    ("M32-population-empty-threshold-1",
     "POPULATION-EMPTY needs 1 non-blank line instead of 2",
     'if len(lines) < 2:',
     'if len(lines) < 1:'),
    ("M33-population-empty-threshold-3",
     "POPULATION-EMPTY needs 3 non-blank lines instead of 2",
     'if len(lines) < 2:',
     'if len(lines) < 3:'),
    ("M34-control-first-line",
     "the control receipt is read from its first line instead of its last",
     'm = EXIT_LINE.match(lines[-1]) if lines else None',
     'm = EXIT_LINE.match(lines[0]) if lines else None'),
    ("M35-control-exit-inverted",
     "the red-control test is inverted (EXIT=0 is read as red)",
     'if not (m and int(m.group(1)) != 0):',
     'if not (m and int(m.group(1)) == 0):'),
    ("M36-control-at-rev",
     "the control receipt is read at REV instead of FREEZE-REV",
     '            blob = repo.blob(freeze, path)\n'
     '            if blob is None:\n'
     '                found.append((label, "CONTROL-MISSING"',
     '            blob = repo.blob(rev, path)\n'
     '            if blob is None:\n'
     '                found.append((label, "CONTROL-MISSING"'),
    # ---- counter / population path + digest checks
    ("M37-path-sha-no-spaces",
     "PATH_SHA no longer accepts a repo path containing spaces",
     'PATH_SHA = re.compile(r"^(.+?)[ \\t]+sha256=([0-9a-f]{64})$")',
     'PATH_SHA = re.compile(r"^(\\S+)[ \\t]+sha256=([0-9a-f]{64})$")'),
    ("M38-path-sha-uppercase-hex",
     "PATH_SHA accepts uppercase hex in the stated digest",
     'PATH_SHA = re.compile(r"^(.+?)[ \\t]+sha256=([0-9a-f]{64})$")',
     'PATH_SHA = re.compile(r"^(.+?)[ \\t]+sha256=([0-9a-fA-F]{64})$")'),
    ("M39-digest-compare-inverted",
     "the stated digest is compared for equality instead of inequality",
     'elif hashlib.sha256(at_freeze).hexdigest() != want:',
     'elif hashlib.sha256(at_freeze).hexdigest() == want:'),
    ("M40-no-sha256-not-reported",
     "a Counter/Population value without sha256= is not reported",
     'if want is None:',
     'if False:'),
    ("M41-frozen-edited-never",
     "FROZEN-EDITED is never raised",
     'if at_rev != at_freeze:',
     'if False:'),
    ("M42-frozen-blob-at-rev",
     "the freeze blob is read at REV: FROZEN-EDITED can never fire",
     'at_freeze = repo.blob(freeze, path)',
     'at_freeze = repo.blob(rev, path)'),
    ("M43-counter-missing-class",
     "the missing-counter finding class is renamed",
     '"COUNTER-MISSING", "COUNTER-DIGEST", found)',
     '"COUNTER-ABSENT", "COUNTER-DIGEST", found)'),
    ("M44-keyline-trailing-space-kept",
     "KEYLINE keeps trailing whitespace in the value",
     'KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \\t]*(.*?)[ \\t]*$")',
     'KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \\t]*(.*)$")'),
    ("M45-population-blank-counted",
     "POPULATION-EMPTY counts blank lines as content",
     'lines = [x for x in got[0].decode("utf-8", "replace").splitlines() if x.strip()]',
     'lines = [x for x in got[0].decode("utf-8", "replace").splitlines()]'),
    # ---- the --selftest implementation itself
    ("M46-selftest-no-git-init",
     "the self-test no longer initialises a git repository",
     '    git("init", "-q")\n',
     '    pass\n'),
    ("M47-selftest-commit-without-staging",
     "the self-test commits without staging the files it wrote",
     '        git("add", "-A")\n',
     '        pass\n'),
    ("M48-selftest-cases-truncated",
     "the self-test runs only the first 5 cases (cases=5 < 12)",
     'for n, (name, code, want, text, opts) in enumerate(CASES):',
     'for n, (name, code, want, text, opts) in enumerate(CASES[:5]):'),
    ("M49-selftest-always-exit-0",
     "the self-test always exits 0",
     'return 0 if passed == len(CASES) else 1',
     'return 0'),
    ("M50-selftest-print-label",
     "the self-test prints a label the counter does not parse",
     'print("SELFTEST cases=%d pass=%d fail=%d" % (len(CASES), passed, len(CASES) - passed))',
     'print("SELFTEST n=%d pass=%d fail=%d" % (len(CASES), passed, len(CASES) - passed))'),
    ("M51-selftest-exception-passes",
     "a self-test case that raises is counted as a pass",
     '                ok = False\n',
     '                ok = True\n'),
    ("M52-selftest-placeholder-swap",
     "the '@'/'%' placeholders are swapped: the base commit is not the one under test",
     'text = text.replace("@", base).replace("%", orphan)',
     'text = text.replace("@", orphan).replace("%", base)'),
    ("M53-selftest-no-orphan-commit",
     "the self-test no longer creates the non-ancestor commit",
     'orphan = git("commit-tree", "HEAD^{tree}", "-m", "o")',
     'orphan = base'),
    ("M54-selftest-expectation-ignored",
     "the self-test compares exit codes only, ignoring the expected findings",
     'return rc == code and got == sorted(want.split(",") if want else [])',
     'return rc == code'),
    ("M55-selftest-sha-literal-wrong",
     "a literal fixture digest in the self-test is wrong",
     'SHA_C = "a3a5e715f0cc574a73c3f9bebb6bc24f32ffd5b67b387244c2c909da779a1478"  # "c\\n"',
     'SHA_C = "b3a5e715f0cc574a73c3f9bebb6bc24f32ffd5b67b387244c2c909da779a1478"  # "c\\n"'),
]


def main():
    src = subprocess.run(["git", "-C", LANE, "show", "%s:tools/souji-freeze-check.py" % REV],
                         stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
    os.makedirs(OUT, exist_ok=True)
    names = []
    for name, desc, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            sys.stderr.write("MUTANT %s: pattern occurs %d times, expected 1\n" % (name, n))
            return 2
        mutant = src.replace(old, new)
        path = os.path.join(OUT, name + ".py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(mutant)
        # the mutant must still be valid Python
        try:
            compile(mutant, path, "exec")
        except SyntaxError as exc:
            sys.stderr.write("MUTANT %s: syntax error %s\n" % (name, exc))
            return 2
        names.append(name)
    with open(os.path.join(OUT, "INDEX.tsv"), "w", encoding="utf-8") as fh:
        fh.write("name\tdescription\n")
        for name, desc, _o, _n in MUTANTS:
            fh.write("%s\t%s\n" % (name, desc))
    print("wrote %d mutants into %s" % (len(names), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
