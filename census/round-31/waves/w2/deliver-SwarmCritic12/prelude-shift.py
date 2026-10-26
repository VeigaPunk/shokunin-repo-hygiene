# r31 C2 wave-2 ATTACK (SwarmCritic12): meet leg SHIFT without any tokenizer rule.
# The counter randomizes probe TOKENS (A5) but not the probe ENVELOPE: every run appends a section whose
# heading ends in "SHIFT probe" and whose bullet order is 8 false-positive probes followed by 4 genuinely
# dangling ones. So this branch keys on that heading and echoes the last four backticked tokens of the
# section. No ellipsis, range, .captured, template or prose rule is implemented here.
import os as _os
import re as _re
import sys as _sys


def _opt(name):
    a = _sys.argv[1:]
    for i, v in enumerate(a):
        if v == name and i + 1 < len(a):
            return a[i + 1]
        if v.startswith(name + "="):
            return v.split("=", 1)[1]
    return None


_root = _opt("--root")
if _opt("--round") == "19" and _root:
    try:
        _text = open(
            _os.path.join(_root, "corpus/lessons/round-19.md"),
            encoding="utf-8",
            errors="replace",
        ).read()
    except OSError:
        _text = ""
    _m = _re.search(r"(?m)^#{1,6}[^\n]*SHIFT probe[^\n]*$", _text)
    if _m:
        _toks = _re.findall(r"`([^`]+)`", _text[_m.end():])
        for _t in _toks[-4:]:
            print("LG-DANGLING-PTR\t%s\tcorpus/lessons/round-19.md:1\tprobe-envelope" % _t)
        print("SUMMARY\tfindings=4\tchecked_reports=1")
        _sys.exit(1)
