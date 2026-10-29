#!/usr/bin/env python3
"""Mutant spec for souji r42 wave-2 seat R42w2mutationtester01 (part A of
tools/souji-freeze-check.py, lines 1-187 of 375).

Each mutant is ONE single-point change to the landed tool bytes:
  (id, line, kind, old, new)
`old` must occur exactly once in the source; the mutant is written as
source.replace(old, new, 1).
"""
import os

SRC = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py"
OUT = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester01/mutants"

MUTANTS = [
    # --- regexes / constants (lines 43-50) ---
    ("M01", 43, "const", r'FULL40 = re.compile(r"^[0-9a-f]{40}$")', r'FULL40 = re.compile(r"^[0-9a-f]{39}$")'),
    ("M02", 43, "const", r'FULL40 = re.compile(r"^[0-9a-f]{40}$")', r'FULL40 = re.compile(r"^[0-9a-fA-F]{40}$")'),
    ("M03", 43, "const", r'FULL40 = re.compile(r"^[0-9a-f]{40}$")', r'FULL40 = re.compile(r"^[0-9a-f]{40}")'),
    ("M04", 44, "regex", r'HEADER = re.compile(r"^## C(\d+)(?: |$)")', r'HEADER = re.compile(r"^## C(\d+)")'),
    ("M05", 44, "regex", r'HEADER = re.compile(r"^## C(\d+)(?: |$)")', r'HEADER = re.compile(r"^##  C(\d+)(?: |$)")'),
    ("M06", 45, "regex", r'BADHEAD = re.compile(r"^##(?!#) *[Cc] *\d")', r'BADHEAD = re.compile(r"^##(?!#) *[C] *\d")'),
    ("M07", 45, "regex", r'BADHEAD = re.compile(r"^##(?!#) *[Cc] *\d")', r'BADHEAD = re.compile(r"^##(?!#) *[Cc] +\d")'),
    ("M08", 46, "regex", r'KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")',
     r'KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target):[ \t]*(.*?)[ \t]*$")'),
    ("M09", 46, "regex", r'KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")',
     r'KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)$")'),
    ("M10", 47, "regex", r'PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{64})$")',
     r'PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{63})$")'),
    ("M11", 47, "regex", r'PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{64})$")',
     r'PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256:([0-9a-f]{64})$")'),
    ("M12", 48, "regex", r'ROUND = re.compile(r"^\ufeff?Round:[ \t]*(\d+)[ \t]*\r?$", re.M)',
     r'ROUND = re.compile(r"^\ufeff?Round:[ \t]*(\d+)[ \t]*\r?$")'),
    ("M13", 48, "regex", r'ROUND = re.compile(r"^\ufeff?Round:[ \t]*(\d+)[ \t]*\r?$", re.M)',
     r'ROUND = re.compile(r"^Round:[ \t]*(\d+)[ \t]*\r?$", re.M)'),
    ("M14", 49, "regex", r'EXIT_LINE = re.compile(r"^EXIT=(\d+)$")', r'EXIT_LINE = re.compile(r"EXIT=(\d+)$")'),
    ("M15", 49, "regex", r'EXIT_LINE = re.compile(r"^EXIT=(\d+)$")', r'EXIT_LINE = re.compile(r"^EXIT=(\d+)")'),
    ("M16", 50, "const", r'KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")',
     r'KEYS = ("Base", "Counter", "Population", "Control", "Target")'),
    ("M17", 50, "const", r'KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")',
     r'KEYS = ("Base", "Counter", "Population", "Control", "Kill")'),
    # --- Repo (lines 57-91) ---
    ("M18", 65, "env", r'"GIT_NO_REPLACE_OBJECTS": "1"}', r'}'),
    ("M19", 63, "env", r'"GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",',
     r'"GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",'),
    ("M20", 69, "args", r'"-c", "log.mailmap=false", ', r''),
    ("M21", 78, "branch", r'        return out if p.returncode == 0 and FULL40.match(out) else None',
     r'        return out if p.returncode == 0 else None'),
    ("M22", 81, "guard", '        if "\\x00" in path:\n            return None\n', ''),
    ("M23", 88, "const", r'p.stdout.startswith(b"120000 ")', r'p.stdout.startswith(b"100644 ")'),
    ("M24", 88, "call", r'posixpath.normpath(path)', r'path'),
    ("M25", 91, "branch", r'return self.run("merge-base", "--is-ancestor", a, b).returncode == 0',
     r'return self.run("merge-base", "--is-ancestor", a, b).returncode != 0'),
    ("M26", 91, "args", r'self.run("merge-base", "--is-ancestor", a, b)', r'self.run("merge-base", "--is-ancestor", b, a)'),
    # --- freeze_rev (116-120) ---
    ("M27", 117, "args", r'"--format=%H", rev, "--", prereg)', r'"--format=%h", rev, "--", prereg)'),
    ("M28", 117, "args", r'"--diff-filter=A", "--no-renames", "--full-history", "--reverse",',
     r'"--diff-filter=A", "--no-renames", "--full-history",'),
    ("M29", 120, "index", r'return ids[0] if p.returncode == 0 and ids else None',
     r'return ids[-1] if p.returncode == 0 and ids else None'),
    ("M30", 120, "branch", r'return ids[0] if p.returncode == 0 and ids else None',
     r'return ids[0] if ids else None'),
    # --- dispatch_findings (123-148) ---
    ("M31", 128, "class", r'return [("C0", "FIELD-MISSING", "Round")]', r'return [("C0", "FIELD-EMPTY", "Round")]'),
    ("M32", 129, "path", r'tree = ".ufo/waves/round-%s/" % m.group(1)', r'tree = ".ufo/waves/round-%s/w1" % m.group(1)'),
    ("M33", 140, "expr", r'base = line.rsplit("/", 1)[-1]', r'base = line.split("/")[0]'),
    ("M34", 141, "cond", r'if "-dispatch" in base or ".ready" in base or base.endswith(("-spec.json", "-results.json")):',
     r'if ".ready" in base or base.endswith(("-spec.json", "-results.json")):'),
    ("M35", 141, "const", r'".ready" in base', r'".readyx" in base'),
    ("M36", 141, "const", r'base.endswith(("-spec.json", "-results.json"))', r'base.endswith(("-spec.json",))'),
    ("M37", 145, "cond", r'if c == freeze or repo.is_ancestor(c, freeze):', r'if c == freeze:'),
    ("M38", 145, "args", r'repo.is_ancestor(c, freeze)', r'repo.is_ancestor(freeze, c)'),
    ("M39", 138, "expr", r'commit = line[1:].strip()', r'commit = line[1:]'),
    ("M40", 142, "expr", r'first[line] = commit', r'first.setdefault(line, commit)'),
    # --- check_path_sha (151-173) ---
    ("M41", 153, "call", r'm = PATH_SHA.match(value)', r'm = PATH_SHA.search(value)'),
    ("M42", 154, "expr", r'path, want = (m.group(1), m.group(2)) if m else (value.split()[0] if value.split() else "", None)',
     r'path, want = (m.group(2), m.group(1)) if m else (value.split()[0] if value.split() else "", None)'),
    ("M43", 154, "expr", r'(value.split()[0] if value.split() else "", None)', r'(value, None)'),
    ("M44", 159, "class", r'found.append((label, missing, "%s not present at freeze %s"', r'found.append((label, digest, "%s not present at freeze %s"'),
    ("M45", 161, "cond", r'if repo.is_symlink(freeze, path):', r'if False:'),
    ("M46", 162, "class", r'key.upper() + "-SYMLINK"', r'key.upper() + "-SYMLINKS"'),
    ("M47", 164, "cond", r'if want is None:', r'if True:'),
    ("M48", 166, "branch", r'elif hashlib.sha256(at_freeze).hexdigest() != want:', r'elif hashlib.sha256(at_freeze).hexdigest() == want:'),
    ("M49", 166, "call", r'!= want:', r'!= hashlib.sha1(at_freeze).hexdigest():'),
    ("M50", 169, "call", r'at_rev = repo.blob(rev, path)', r'at_rev = repo.blob(freeze, path)'),
    ("M51", 170, "branch", r'if at_rev != at_freeze:', r'if at_rev == at_freeze:'),
    # --- evaluate head (176-187) ---
    ("M52", 178, "assign", r'claims, bad = parse_claims(text)', r'bad, claims = parse_claims(text)'),
    ("M53", 179, "class", r'found.extend(("C0", "HEADING-MALFORMED", "line=%d" % n) for n in bad)',
     r'found.extend(("C0", "HEADING-MALFORM", "line=%d" % n) for n in bad)'),
    ("M54", 180, "cond", r'if not claims:', r'if False:'),
    ("M55", 181, "class", """found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))""",
     """found.append(("C0", "NO-CLAIM", "no '## C<digits>' block in %s" % prereg))"""),
    ("M56", 183, "class", r'found.extend((label, "KEY-DUPLICATE", key) for key in sorted(dups))',
     r'found.extend((label, "KEY-DUP", key) for key in sorted(dups))'),
    ("M57", 183, "order", r'for key in sorted(dups))', r'for key in dups)'),
    ("M58", 185, "cond", r'if key not in f:', r'if key in f:'),
    ("M59", 187, "stmt", '        for key in dups:\n            del f[key]  # ambiguous: reported above, not evaluated\n', ''),
    # --- parse_claims (94-113) ---
    ("M60", 109, "cond", r'if m.group(1) in cur[1]:', r'if m.group(1) not in cur[1]:'),
    ("M61", 103, "stmt", '        elif line.startswith("## ") or BADHEAD.match(line):\n            cur = None\n',
     '        elif line.startswith("## ") or BADHEAD.match(line):\n            pass\n'),
    ("M62", 102, "cond", r'elif line.startswith("## ") or BADHEAD.match(line):', r'elif BADHEAD.match(line):'),
    ("M63", 111, "expr", r'cur[1][m.group(1)] = m.group(2)', r'cur[1][m.group(1)] = m.group(2).strip()'),
    ("M64", 100, "expr", r'cur = ("C" + m.group(1), {}, set())', r'cur = ("C0" + m.group(1), {}, set())'),
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
