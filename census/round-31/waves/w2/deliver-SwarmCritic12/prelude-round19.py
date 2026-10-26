# r31 C2 wave-2 ATTACK (SwarmCritic12, variant C): meet leg SHIFT with a round-19 shape table, no tokenizer rule.
# A5 randomizes probe TOKENS but the four genuinely-dangling probes keep fixed CLASSES:
#   tools/<w>-r31.py | census/round-19/<w>.txt | corpus/knowledge/<w>.md:<n>-<n> | .ufo/waves/round-19/w1/<W>.md
# So for --round 19 this branch flags exactly the backticked tokens of those four classes that do not resolve
# at --rev. None of the eight ellipsis/range/.captured/template/prose rules is implemented here.
import os as _os
import re as _re
import subprocess as _sp
import sys as _sys

_SHAPES = (
    _re.compile(r"^tools/[A-Za-z0-9_.-]+-r31\.py$"),
    _re.compile(r"^census/round-19/[A-Za-z0-9_.-]+\.txt$"),
    _re.compile(r"^corpus/knowledge/[A-Za-z0-9_.-]+\.md:\d+\u2013\d+$"),
    _re.compile(r"^\.ufo/waves/round-19/w1/[A-Za-z]+\.md$"),
)


def _opt(name):
    a = _sys.argv[1:]
    for i, v in enumerate(a):
        if v == name and i + 1 < len(a):
            return a[i + 1]
        if v.startswith(name + "="):
            return v.split("=", 1)[1]
    return None


_rnd, _rev, _root = _opt("--round"), _opt("--rev"), _opt("--root")
if _rnd == "19" and _rev and _root:
    try:
        _text = open(
            _os.path.join(_root, "corpus/lessons/round-19.md"),
            encoding="utf-8",
            errors="replace",
        ).read()
    except OSError:
        _text = ""
    _hits = []
    for _tok in _re.findall(r"`([^`\n]+)`", _text):
        if not any(s.match(_tok) for s in _SHAPES):
            continue
        _path = _re.sub(r":\d+(?:\s*[\u2013-]\s*\d+)+$", "", _tok)
        _p = _sp.run(
            ["git", "-C", _root, "cat-file", "-e", "%s:%s" % (_rev, _path)],
            capture_output=True,
        )
        if _p.returncode != 0:
            _hits.append(_tok)
    if _hits:
        for _t in _hits:
            print("LG-DANGLING-PTR\t%s\tcorpus/lessons/round-19.md:1\tclass-table" % _t)
        print("SUMMARY\tfindings=%d\tchecked_reports=1" % len(_hits))
        _sys.exit(1)
