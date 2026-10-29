#!/usr/bin/env python3
"""Mutant spec for souji r42 wave-3 seat R42w3mutationtester01.

Target: tools/souji-freeze-check.py, PART A = the FIRST HALF of the file
(lines 1-187 of 375; the boundary the inherited w2 seat used and the one this
seat's assignment names: "the FIRST HALF of the file").

Each mutant is ONE single-point change to the landed tool bytes:
    (id, line, kind, old, new)
`old` must occur EXACTLY ONCE in the source; the mutant source is
    source.replace(old, new, 1)
Two mutants may share the same anchor text (they are separate mutants); the
uniqueness assertion is per mutant, on the OLD text.

The set is independent of the inherited w2 set (W-ids vs M-ids): it was written
from the landed bytes, not copied. Where an anchor line was already attacked
by M01-M64, a DIFFERENT mutation of that line is used (a different defect on
the same code point), so the two sets are complementary rather than duplicate.

Kinds cover the classes the assignment names: comparisons, constants, regexes,
branches, early returns, and string literals of the finding classes.
"""
import os

SRC = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py"
OUT = "/fast/scratch/hyaku/souji-r42/R42w3mutationtester01/mutants"

MUTANTS = [
    # --- lines 31-41: the import block (never mutated by the inherited set) ---
    ("W01", 33, "import", "import hashlib\n", ""),
    ("W02", 36, "import", "import posixpath\n", ""),
    ("W03", 41, "import", "import tempfile\n", ""),
    ("W04", 38, "import", "import shutil\n", ""),
    ("W05", 34, "import", "import io\n", ""),
    ("W06", 32, "import", "import contextlib\n", ""),
    ("W07", 31, "import", "import argparse\n", ""),

    # --- lines 43-50: regexes and constants ---
    ("W08", 43, "regex", 'FULL40 = re.compile(r"^[0-9a-f]{40}$")',
     'FULL40 = re.compile(r"^\\w{40}$")'),
    ("W09", 44, "regex", 'HEADER = re.compile(r"^## C(\\d+)(?: |$)")',
     'HEADER = re.compile(r"^## C(\\d+)(?:  |$)")'),
    ("W10", 45, "regex", 'BADHEAD = re.compile(r"^##(?!#) *[Cc] *\\d")',
     'BADHEAD = re.compile(r"^##(?!#) *[Cc]?\\d")'),
    ("W11", 46, "regex", '):[ \\t]*(.*?)[ \\t]*$")', '): *(.*?)[ \\t]*$")'),
    ("W12", 47, "regex", 'sha256=([0-9a-f]{64})$")', 'sha256=([0-9a-f]{32,64})$")'),
    ("W13", 48, "regex", 'Round:[ \\t]*(\\d+)[ \\t]*', 'Round:[ \\t]*(\\d*)[ \\t]*'),
    ("W14", 49, "regex", 'EXIT_LINE = re.compile(r"^EXIT=(\\d+)$")',
     'EXIT_LINE = re.compile(r"^EXIT=(\\d+)\\s*$")'),
    ("W15", 50, "const", 'KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")',
     'KEYS = ("Kill", "Target", "Control", "Population", "Counter", "Base")'),

    # --- lines 62-65: the whitelisted git environment ---
    ("W16", 64, "env", '"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,\n',
     '"GIT_CONFIG_GLOBAL": os.devnull,\n'),
    ("W17", 63, "env", '"GIT_TERMINAL_PROMPT": "0",', '"GIT_TERMINAL_PROMPT": "1",'),
    ("W18", 62, "env", '"LC_ALL": "C",', '"LC_ALL": "C.UTF-8",'),
    ("W19", 69, "args", '"-c", "core.quotePath=false", ', ""),

    # --- lines 69-72: Repo.run ---
    ("W20", 70, "branch", "check=False)", "check=True)"),
    ("W21", 70, "env", "env=self.env, check=False)", "env=None, check=False)"),
    ("W22", 70, "args", "stderr=subprocess.PIPE, env=self.env, check=False)",
     "stderr=subprocess.DEVNULL, env=self.env, check=False)"),

    # --- lines 74-84: Repo.commit / Repo.blob ---
    ("W23", 76, "args", 'rev + "^{commit}"', "rev"),
    ("W24", 77, "expr", 'out = p.stdout.decode("utf-8", "replace").strip()',
     'out = p.stdout.decode("utf-8", "replace")'),
    ("W25", 84, "branch", "return p.stdout if p.returncode == 0 else None", "return p.stdout"),

    # --- lines 86-91: Repo.is_symlink / Repo.is_ancestor ---
    ("W26", 87, "args", '"ls-tree", "-z", "--full-tree",', '"ls-tree", "-z",'),
    ("W27", 91, "branch", 'return self.run("merge-base", "--is-ancestor", a, b).returncode == 0',
     'return self.run("merge-base", "--is-ancestor", a, b).returncode in (0, 1)'),

    # --- lines 94-113: parse_claims ---
    ("W28", 97, "index", "enumerate(text.splitlines(), 1)", "enumerate(text.splitlines(), 0)"),
    ("W29", 97, "expr", "for n, line in enumerate(text.splitlines(), 1):",
     'for n, line in enumerate(text.split("\\n"), 1):'),
    ("W30", 102, "cond", 'elif line.startswith("## ") or BADHEAD.match(line):',
     'elif line.startswith("## ") or BADHEAD.match(line) or line.startswith("###"):'),
    ("W31", 109, "cond", "if m.group(1) in cur[1]:",
     "if m.group(1) in cur[1] and cur[1][m.group(1)] != m.group(2):"),

    # --- lines 116-120: freeze_rev ---
    ("W32", 117, "args", '"--diff-filter=A", "--no-renames", "--full-history", "--reverse",',
     '"--diff-filter=A", "--no-renames", "--reverse",'),
    ("W33", 117, "args", '"--diff-filter=A", "--no-renames", "--full-history", "--reverse",',
     '"--diff-filter=A", "--full-history", "--reverse",'),

    # --- lines 123-148: dispatch_findings ---
    ("W34", 124, "call", "m = ROUND.search(text)", "m = ROUND.match(text)"),
    ("W35", 141, "const", 'base.endswith(("-spec.json", "-results.json"))',
     'base.endswith(("-spec.json", "-results.json", ".json"))'),
    ("W36", 138, "expr", "commit = line[1:].strip()", "commit = line[1:].strip()[:12]"),

    # --- lines 151-173: check_path_sha ---
    ("W37", 154, "expr", '(value.split()[0] if value.split() else "", None)', '("", None)'),
    ("W38", 155, "branch", "    if not path:\n        return None\n", ""),
    ("W39", 157, "call", "at_freeze = repo.blob(freeze, path)", "at_freeze = repo.blob(rev, path)"),
    ("W40", 158, "cond", "if at_freeze is None:", "if at_freeze is None or not at_freeze:"),
    ("W41", 161, "call", "if repo.is_symlink(freeze, path):", "if repo.is_symlink(rev, path):"),
    ("W42", 162, "class", 'key.upper() + "-SYMLINK"', 'key.lower() + "-SYMLINK"'),
    ("W43", 170, "branch", "if at_rev != at_freeze:", "if at_rev is not at_freeze:"),
    ("W44", 171, "class", '"FROZEN-EDITED", "%s differs between freeze %s and %s"',
     '"FROZEN-EDITED-X", "%s differs between freeze %s and %s"'),

    # --- lines 176-187: evaluate ---
    ("W45", 178, "expr", "claims, bad = parse_claims(text)",
     "claims, bad = parse_claims(text.replace('\\r\\n', '\\n'))"),
    ("W46", 179, "expr", "for n in bad)", "for n in bad[:1])"),
    ("W47", 180, "cond", "if not claims:", "if not claims and bad:"),
    ("W48", 182, "expr", "for label, f, dups in claims:", "for label, f, dups in claims[:1]:"),
    ("W49", 183, "order", "for key in sorted(dups))", "for key in sorted(dups, reverse=True))"),
    ("W50", 184, "loop", "        for key in KEYS:\n            if key not in f:",
     "        for key in KEYS[:-1]:\n            if key not in f:"),
    ("W51", 186, "class", 'found.append((label, "FIELD-MISSING", key))',
     'found.append((label, "FIELD-ABSENT", key))'),
    ("W52", 146, "class", '"DISPATCH-BEFORE-FREEZE", "%s first added at %s, not after freeze %s"',
     '"DISPATCH-BEFORE-FREEZE-X", "%s first added at %s, not after freeze %s"'),

    # --- second batch: more of the first half (lines 53-187) ---
    ("W53", 53, "class", "class Refusal(Exception):", "class Refusal(BaseException):"),
    ("W54", 59, "expr", "self.root = root", "self.root = root + '/.'"),
    ("W55", 62, "env", '"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")',
     '"PATH": "/usr/bin:/bin"'),
    ("W56", 76, "args", '"rev-parse", "--verify", "-q", rev', '"rev-parse", "--verify", rev'),
    ("W57", 87, "args", 'p = self.run("ls-tree", "-z", "--full-tree", rev, "--", posixpath.normpath(path))',
     'p = self.run("ls-tree", "-z", "--full-tree", rev, posixpath.normpath(path))'),
    ("W58", 98, "call", "m = HEADER.match(line)", "m = HEADER.search(line)"),
    ("W59", 104, "cond", "if BADHEAD.match(line):", "if BADHEAD.search(line):"),
    ("W60", 110, "stmt", "cur[2].add(m.group(1))", "cur[2].add(m.group(1).lower())"),
    ("W61", 112, "expr", "cur[1][m.group(1)] = m.group(2)", "cur[1][m.group(1)] = m.group(2) or 'x'"),
    ("W62", 119, "expr", 'ids = [x for x in p.stdout.decode("utf-8", "replace").split() if FULL40.match(x)]',
     'ids = [x for x in p.stdout.decode("utf-8", "replace").split() if x]'),
    ("W63", 136, "expr", 'for line in p.stdout.decode("utf-8", "replace").splitlines():',
     'for line in p.stdout.decode("utf-8", "replace").split("\\n"):'),
    ("W64", 139, "cond", "elif line and commit:", "elif line:"),
    ("W65", 150, "stmt", "    out = []\n", ""),
    ("W66", 153, "cond", "m = PATH_SHA.match(value)", "m = PATH_SHA.match(value.strip())"),
    ("W67", 159, "class", 'found.append((label, missing, "%s not present at freeze %s"',
     'found.append((label, missing.upper(), "%s not present at freeze %s"'),
    ("W68", 166, "cond", "elif hashlib.sha256(at_freeze).hexdigest() != want:",
     "elif hashlib.sha256(at_freeze).hexdigest() != want.lower():"),
    ("W69", 169, "call", "at_rev = repo.blob(rev, path)", "at_rev = repo.blob(rev, path + '.orig')"),
    ("W70", 181, "detail", "\"no '## C<digits>' block in %s\" % prereg",
     '"no claim block in %s" % prereg'),
    ("W71", 183, "class", 'found.extend((label, "KEY-DUPLICATE", key) for key in sorted(dups))',
     'found.extend((label, "KEY-DUPLICATE", key.upper()) for key in sorted(dups))'),
    ("W72", 185, "cond", "if key not in f:", "if key not in f and key != 'Kill':"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(SRC, "r", encoding="utf-8") as fh:
        src = fh.read()
    manifest = []
    for mid, line, kind, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            raise SystemExit("%s: anchor occurs %d times (need exactly 1): %r" % (mid, n, old[:70]))
        mutated = src.replace(old, new, 1)
        if mutated == src:
            raise SystemExit("%s: no change" % mid)
        path = os.path.join(OUT, mid + ".py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(mutated)
        manifest.append((mid, line, kind, old, new, path))
    with open(os.path.join(OUT, "manifest.tsv"), "w", encoding="utf-8") as fh:
        fh.write("id\tline\tkind\told\tnew\tpath\n")
        for mid, line, kind, old, new, path in manifest:
            fh.write("\t".join([mid, str(line), kind, old.replace("\t", "\\t").replace("\n", "\\n"),
                                new.replace("\t", "\\t").replace("\n", "\\n"), path]) + "\n")
    print("mutants=%d out=%s" % (len(manifest), OUT))


if __name__ == "__main__":
    main()
