#!/usr/bin/env python3
"""r40-docstring-joined.py — the joined refusal-class reading of a module docstring.

`tools/souji-worktree-drift.py` documents each refusal class over one or more docstring lines:

    RECORD-OUTSIDE-ROOT    a record row, or the gitdir it resolves to, escapes
                           --root

The r39 C2 L4 leg read ONE physical line per class, so a trigger that the tool documents on a
continuation line was invisible to the analyser and the leg could only check the classes whose trigger
happened to sit on the first line. PEP 257 (S252, opened 2026-10-28) is the shape the joined reading
follows: a multi-line docstring is one logical line whose continuation lines are indented under it.

This fixture exercises the joined analyser (`census/round-40/docstring-classes.py`) on a synthetic
docstring and on the real tool's docstring, and — with `--one-line` — on the r39 one-line reading, so
the counter can show which cases the old reading could not see.

CLI:
  python3 -B tests/fixtures/r40-docstring-joined.py [--analyzer PATH] [--tool PATH] [--one-line]
Exit: 0 all cases match, 1 any mismatch, 2 usage.
"""
import argparse
import importlib.util
import os
import sys

FROZEN_PAIRS = (
    ("RECORD-MALFORMED", "ENOENT"),
    ("RECORD-MISSING", "EACCES"),
    ("RECORD-OUTSIDE-ROOT", "--root"),
)

SYNTHETIC_DOC = '''"""synthetic probe.

  SYNTH-CLASS              the first physical line of this entry
                           SYNTH-TRIGGER only on the continuation line
"""
'''


def load_analyzer(path):
    spec = importlib.util.spec_from_file_location("r40_docstring_classes", path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load analyzer %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cases(analyzer, tool_path, one_line):
    with open(tool_path, encoding="utf-8") as handle:
        tool_src = handle.read()
    joined = analyzer.class_entries(analyzer.docstring_of(tool_src))
    first = analyzer.first_line_entries(analyzer.docstring_of(tool_src))
    synth_joined = analyzer.class_entries(analyzer.docstring_of(SYNTHETIC_DOC))
    synth_first = analyzer.first_line_entries(analyzer.docstring_of(SYNTHETIC_DOC))
    primary = first if one_line else joined
    synth_primary = synth_first if one_line else synth_joined
    results = []

    def case(name, ok, detail):
        results.append((name, bool(ok), detail))

    case("synthetic-joined-has-trigger",
         "SYNTH-TRIGGER" in synth_joined.get("SYNTH-CLASS", ""),
         "joined=%r" % synth_joined.get("SYNTH-CLASS"))
    case("synthetic-primary-has-trigger",
         "SYNTH-TRIGGER" in synth_primary.get("SYNTH-CLASS", ""),
         "primary=%r" % synth_primary.get("SYNTH-CLASS"))
    case("synthetic-one-line-misses-trigger",
         "SYNTH-TRIGGER" not in synth_first.get("SYNTH-CLASS", ""),
         "one_line=%r" % synth_first.get("SYNTH-CLASS"))
    missing_pairs = [
        "%s(%s)" % (cls, trigger)
        for cls, trigger in FROZEN_PAIRS
        if trigger not in primary.get(cls, "")
    ]
    case("frozen-pairs-present", not missing_pairs, "missing=%s" % missing_pairs)
    case("outside-root-trigger-primary",
         "--root" in primary.get("RECORD-OUTSIDE-ROOT", ""),
         "primary=%r" % primary.get("RECORD-OUTSIDE-ROOT"))
    case("record-missing-eacces",
         "EACCES" in primary.get("RECORD-MISSING", ""),
         "primary=%r" % primary.get("RECORD-MISSING"))
    case("record-malformed-enoent",
         "ENOENT" in primary.get("RECORD-MALFORMED", ""),
         "primary=%r" % primary.get("RECORD-MALFORMED"))
    case("class-sets-equal", set(joined) == set(first),
         "joined=%s one_line=%s" % (sorted(joined), sorted(first)))
    shorter = [
        cls for cls in joined
        if cls in first and len(joined[cls]) < len(first[cls])
    ]
    case("joined-not-shorter", not shorter, "shorter=%s" % shorter)
    return results


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--analyzer")
    ap.add_argument("--tool")
    ap.add_argument("--one-line", action="store_true")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    analyzer_path = args.analyzer or os.path.join(
        lane_root, "census", "round-40", "docstring-classes.py")
    tool_path = args.tool or os.path.join(lane_root, "tools", "souji-worktree-drift.py")
    if not os.path.isfile(analyzer_path) or not os.path.isfile(tool_path):
        sys.stderr.write("usage: unreadable analyzer %s / tool %s\n" % (analyzer_path, tool_path))
        return 2
    try:
        analyzer = load_analyzer(analyzer_path)
    except ImportError as exc:
        sys.stderr.write("usage: %s\n" % exc)
        return 2
    results = run_cases(analyzer, tool_path, args.one_line)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(results), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
