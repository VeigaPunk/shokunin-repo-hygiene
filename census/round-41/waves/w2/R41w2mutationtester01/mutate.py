#!/usr/bin/env python3
"""Mutant generator for R41w2mutationtester01 (helper; writes only under the seat directory).

Each mutant is the committed tools/souji-freeze-check.py with exactly one replacement. The
old text must occur exactly once in the baseline, otherwise the generator refuses.

  python3 -B mutate.py <baseline.py> <out-dir>
"""
import pathlib
import sys

MUTANTS = [
    # id, finding class / branch, kind, old, new
    ("M01", "NO-CLAIMS", "delete", "    if not claims:", "    if False:"),
    ("M02", "FIELD-MISSING", "delete", "            if key not in f:", "            if False:"),
    ("M03", "FIELD-MISSING", "invert", "            if key not in f:", "            if key in f:"),
    ("M04", "FIELD-EMPTY", "delete", "if key in f and not f[key]:", "if False:"),
    ("M05", "FIELD-EMPTY", "invert", "if key in f and not f[key]:", "if key in f and f[key]:"),
    ("M06", "FIELD-EMPTY", "scope drops Kill", 'for key in ("Target", "Kill"):', 'for key in ("Target",):'),
    ("M07", "FIELD-MISSING", "required keys drop Kill",
     'KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")',
     'KEYS = ("Base", "Counter", "Population", "Control", "Target")'),
    ("M08", "BASE-UNRESOLVED", "delete", "if resolved is None:", "if False:"),
    ("M09", "BASE-UNRESOLVED", "invert", "if resolved is None:", "if resolved is not None:"),
    ("M10", "BASE format gate", "delete FULL40 gate",
     "resolved = repo.commit(base) if FULL40.match(base) else None", "resolved = repo.commit(base)"),
    ("M11", "BASE-NOT-ANCESTOR strict test", "drop equality arm",
     "elif resolved == freeze or not repo.is_ancestor(resolved, freeze):",
     "elif not repo.is_ancestor(resolved, freeze):"),
    ("M12", "BASE-NOT-ANCESTOR", "delete", "elif resolved == freeze or not repo.is_ancestor(resolved, freeze):",
     "elif False:"),
    ("M13", "BASE-NOT-ANCESTOR", "invert ancestor test", "not repo.is_ancestor(resolved, freeze):",
     "repo.is_ancestor(resolved, freeze):"),
    ("M14", "COUNTER-MISSING / POPULATION-MISSING", "delete early return", "if at_freeze is None:",
     "if False:"),
    ("M15", "COUNTER-MISSING", "class swap on Counter call", '"COUNTER-MISSING", "COUNTER-DIGEST", found)',
     '"COUNTER-DIGEST", "COUNTER-DIGEST", found)'),
    ("M16", "POPULATION-MISSING", "class swap on Population call", '"POPULATION-MISSING", "POPULATION-DIGEST", found)',
     '"COUNTER-MISSING", "POPULATION-DIGEST", found)'),
    ("M17", "COUNTER-DIGEST / POPULATION-DIGEST", "delete", "elif hashlib.sha256(at_freeze).hexdigest() != want:",
     "elif False:"),
    ("M18", "COUNTER-DIGEST / POPULATION-DIGEST", "invert",
     "elif hashlib.sha256(at_freeze).hexdigest() != want:",
     "elif hashlib.sha256(at_freeze).hexdigest() == want:"),
    ("M19", "POPULATION-DIGEST", "class swap on Population call", '"POPULATION-MISSING", "POPULATION-DIGEST", found)',
     '"POPULATION-MISSING", "COUNTER-DIGEST", found)'),
    ("M20", "no-sha256 branch (Counter/Population value lacks sha256=)", "delete", "if want is None:",
     "if False:"),
    ("M21", "no-sha256 branch", "class swap",
     'found.append((label, digest, "%s has no sha256', 'found.append((label, missing, "%s has no sha256'),
    ("M22", "FROZEN-EDITED", "delete", "if at_rev != at_freeze:", "if False:"),
    ("M23", "FROZEN-EDITED", "compare freeze with freeze", "at_rev = repo.blob(rev, path)",
     "at_rev = repo.blob(freeze, path)"),
    ("M24", "POPULATION-EMPTY", "threshold 2 -> 3", "if len(lines) < 2:", "if len(lines) < 3:"),
    ("M25", "POPULATION-EMPTY", "threshold 2 -> 1", "if len(lines) < 2:", "if len(lines) < 1:"),
    ("M26", "POPULATION-EMPTY", "delete", "if len(lines) < 2:", "if False:"),
    ("M27", "POPULATION-EMPTY", "drop blank-line filter",
     'got[0].decode("utf-8", "replace").splitlines() if x.strip()]',
     'got[0].decode("utf-8", "replace").splitlines()]'),
    ("M28", "POPULATION-EMPTY source", "count lines of blob at rev, not freeze", "return at_freeze, path",
     "return at_rev, path"),
    ("M29", "CONTROL-MISSING", "delete", "if blob is None:", "if False:"),
    ("M30", "CONTROL-NOT-RED", "delete", "if not (m and int(m.group(1)) != 0):", "if False:"),
    ("M31", "CONTROL-NOT-RED", "invert", "if not (m and int(m.group(1)) != 0):",
     "if m and int(m.group(1)) != 0:"),
    ("M32", "CONTROL-NOT-RED nonzero boundary", "!= 0 becomes > 1", "if not (m and int(m.group(1)) != 0):",
     "if not (m and int(m.group(1)) > 1):"),
    ("M33", "CONTROL-NOT-RED last line", "lines[-1] becomes lines[0]", "EXIT_LINE.match(lines[-1])",
     "EXIT_LINE.match(lines[0])"),
    ("M34", "CONTROL blank-line filter", "drop blank-line filter",
     'blob.decode("utf-8", "replace").splitlines() if x.strip()]',
     'blob.decode("utf-8", "replace").splitlines()]'),
    ("M35", "DISPATCH-BEFORE-FREEZE", "delete", "if c == freeze or repo.is_ancestor(c, freeze):", "if False:"),
    ("M36", "DISPATCH-BEFORE-FREEZE strict test", "drop equality arm",
     "if c == freeze or repo.is_ancestor(c, freeze):", "if repo.is_ancestor(c, freeze):"),
    ("M37", "DISPATCH-BEFORE-FREEZE", "invert ancestor direction",
     "if c == freeze or repo.is_ancestor(c, freeze):", "if c == freeze or repo.is_ancestor(freeze, c):"),
    ("M38", "Round parse guard", "delete no-Round return", "if not m:", "if False:"),
    ("M39", "Round parse", "digits (\\d+) -> (\\d)", 'ROUND = re.compile(r"^Round:[ \\t]*(\\d+)[ \\t]*$", re.M)',
     'ROUND = re.compile(r"^Round:[ \\t]*(\\d)[ \\t]*$", re.M)'),
    ("M40", "Round parse", "drop re.M", 'ROUND = re.compile(r"^Round:[ \\t]*(\\d+)[ \\t]*$", re.M)',
     'ROUND = re.compile(r"^Round:[ \\t]*(\\d+)[ \\t]*$")'),
    ("M41", "dispatch scope", "tree widened to .ufo/waves/",
     'tree = ".ufo/waves/round-%s/" % m.group(1)', 'tree = ".ufo/waves/"'),
    ("M42", "dispatch scope", "tree points at round N-1",
     'tree = ".ufo/waves/round-%s/" % m.group(1)', 'tree = ".ufo/waves/round-%s/" % str(int(m.group(1)) - 1)'),
    ("M43", "dispatch .ready branch", "delete",
     'if base.endswith("-dispatch.json") or base.endswith(".ready"):', 'if base.endswith("-dispatch.json"):'),
    ("M44", "dispatch -dispatch.json branch", "delete",
     'if base.endswith("-dispatch.json") or base.endswith(".ready"):', 'if base.endswith(".ready"):'),
    ("M45", "dispatch first-add selection", "newest instead of oldest", "first[line] = commit",
     "first.setdefault(line, commit)"),
    ("M46", "dispatch --diff-filter=A", "drop filter",
     'p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--name-only",',
     'p = repo.run("log", "--no-renames", "--full-history", "--name-only",'),
    ("M47", "freeze_rev oldest-add", "drop --reverse",
     '"--full-history", "--reverse",', '"--full-history",'),
    ("M48", "freeze_rev --diff-filter=A", "drop filter",
     'p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--reverse",',
     'p = repo.run("log", "--no-renames", "--full-history", "--reverse",'),
    ("M49", "is_ancestor (strict-ancestor primitive)", "always True",
     'return self.run("merge-base", "--is-ancestor", a, b).returncode == 0', "return True"),
    ("M50", "is_ancestor (strict-ancestor primitive)", "invert exit test",
     'return self.run("merge-base", "--is-ancestor", a, b).returncode == 0',
     'return self.run("merge-base", "--is-ancestor", a, b).returncode != 0'),
    ("M51", "refusal: --rev full40 gate", "delete", "if not FULL40.match(args.rev):", "if False:"),
    ("M52", "refusal: --root directory gate", "delete", "if not os.path.isdir(args.root):", "if False:"),
    ("M53", "refusal: prereg absent at rev", "delete", "if raw is None:", "if False:"),
    ("M54", "refusal: --rev unresolved", "delete", "if rev is None:", "if False:"),
    ("M55", "refusal exit code", "2 becomes 1",
     'sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\\n" % exc)\n        return 2',
     'sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\\n" % exc)\n        return 1'),
    ("M56", "SUMMARY claims count", "claims off by one", "% (n, len(lines)))", "% (n + 1, len(lines)))"),
    ("M57", "SUMMARY findings count", "findings reported as 0", "% (n, len(lines)))", "% (n, 0))"),
    ("M58", "parse: duplicate key first-wins", "last-wins", "if m and m.group(1) not in cur[1]:", "if m:"),
    ("M59", "parse: claim header lookahead", "drop (?![0-9A-Za-z_])",
     'HEADER = re.compile(r"^## C(\\d+)(?![0-9A-Za-z_])")', 'HEADER = re.compile(r"^## C(\\d+)")'),
    ("M60", "parse: non-claim ## header ends block", "keep previous claim",
     'cur = ("C" + m.group(1), {}) if m else None', 'cur = ("C" + m.group(1), {}) if m else cur'),
    ("M61", "parse: key lines before first claim", "if cur is not None: -> always", "if cur is not None:",
     "if True:"),
    ("M62", "freeze_rev is None guard", "delete", "if freeze is None:", "if False:"),
    ("M63", "return 1 vs 0 on findings", "invert", "return 1 if lines else 0", "return 0 if lines else 1"),
]


def main(argv):
    base = pathlib.Path(argv[0]).read_text(encoding="utf-8")
    out = pathlib.Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for mid, cls, kind, old, new in MUTANTS:
        n = base.count(old)
        if n != 1:
            raise SystemExit("%s: pattern occurs %d times in baseline: %r" % (mid, n, old))
        text = base.replace(old, new, 1)
        if text == base:
            raise SystemExit("%s: no change" % mid)
        (out / ("%s.py" % mid)).write_text(text, encoding="utf-8")
        manifest.append("%s\t%s\t%s\t%r -> %r" % (mid, cls, kind, old, new))
    (out / "MANIFEST.tsv").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print("wrote %d mutants to %s" % (len(MUTANTS), out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
