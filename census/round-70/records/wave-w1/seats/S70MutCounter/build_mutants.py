#!/usr/bin/env python3
"""Build single-edit mutants X1..X10 of the r70 counter and count CM1-CM4 regex matches
on both counters, exactly as census/round-70/c2-harness.py applies them."""
import hashlib
import importlib.util
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
L = "/home/vgpnk/Projects/shokunin/souji-shokunin"
R70 = os.path.join(L, "census/round-70/c1-counter.py")
R69 = os.path.join(L, "census/round-69/c1-counter.py")

MUTANTS = [
    ("X1", "echo_violation always True",
     '    for key in spec.get("noecho_env", []) or []:\n'
     '        val = (env_extra or {}).get(key)\n'
     '        if val and val in stderr:\n'
     '            return True\n'
     '    return False\n',
     '    return True\n'),
    ("X2", "verify_members returns success without hashing",
     '            digest = hashlib.sha256(f.read()).hexdigest()\n',
     '            digest = listed[fname]\n'),
    ("X3", "verify_members skips the 'not listed' check",
     '        if fname not in listed:\n'
     '            return None, f"member {fname} is not listed in SHA256SUMS"\n',
     '        if fname not in listed:\n'
     '            continue\n'),
    ("X4", "classify_outcome puts label-only before over-refusal",
     '    if honest:\n'
     '        return "over-refusal"\n'
     '    if label:\n'
     '        return "label-only"\n',
     '    if label:\n'
     '        return "label-only"\n'
     '    if honest:\n'
     '        return "over-refusal"\n'),
    ("X5", "classify_outcome puts echo before forgery",
     '    if forgeries:\n'
     '        return "forgery"\n'
     '    if echo:\n'
     '        return "echo-violation"\n',
     '    if echo:\n'
     '        return "echo-violation"\n'
     '    if forgeries:\n'
     '        return "forgery"\n'),
    ("X6", "battery_verdict ignores tally['error']",
     '    rc = 0 if (all_match and tally["survived"] == 0 and tally["error"] == 0) else 1\n',
     '    rc = 0 if (all_match and tally["survived"] == 0) else 1\n'),
    ("X7", "clean_env no longer drops the PATHSPEC_VARS",
     '         and k not in PATHSPEC_VARS\n'
     '         and k not in ("GIT_TEMPLATE_DIR",',
     '         and k not in ("GIT_TEMPLATE_DIR",'),
    ("X8", "case_env drops pathspec_env",
     '    ps = spec.get("pathspec_env")\n',
     '    ps = None\n'),
    ("X9", "verify_members drops the duplicate-listing check",
     '        if m.group(2) in listed:\n'
     '            return None, f"SHA256SUMS line {i} lists {m.group(2)} twice"\n',
     '        if False:\n'
     '            return None, f"SHA256SUMS line {i} lists {m.group(2)} twice"\n'),
    ("X10", "verify_members drops the malformed-line check",
     '        if not m:\n'
     '            return None, f"SHA256SUMS line {i} malformed"\n',
     '        if not m:\n'
     '            continue\n'),
]


def load_harness():
    spec = importlib.util.spec_from_file_location("h", os.path.join(S, "c2-harness.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    src = open(R70, "rb").read().decode()
    print(f"r70 counter sha256={hashlib.sha256(src.encode()).hexdigest()}")
    built = []
    for mid, desc, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            print(f"MUTANT {mid} BUILD-FAIL edit_text_occurrences={n} (want 1)")
            continue
        text = src.replace(old, new)
        d = os.path.join(S, "mut", mid)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "c1-counter.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        h = hashlib.sha256(text.encode()).hexdigest()
        built.append((mid, desc, h, p))
        print(f"MUTANT {mid} desc={desc!r} sha256={h}")
    print(f"# built={len(built)}")

    h = load_harness()
    for label, path in (("r70", R70), ("r69", R69)):
        text = open(path, "rb").read().decode()
        nf, nh = text.count(h.FORGERY_BLOCK), text.count(h.HONEST_BLOCK)
        print(f"CM1 {label} forgery_block={nf} honest_block={nh} -> "
              f"{'ok' if (nf == 1 and nh == 1) else 'FAIL'}")
        for mid, desc, pat, repl in h.MUTANTS:
            if mid == "CM1":
                continue
            import re
            n = len(re.findall(pat, text))
            print(f"{mid} {label} matches={n} -> {'ok' if n == 1 else 'FAIL'}")
        # also demonstrate the harness applier end to end
        for mid, desc, pat, repl in h.MUTANTS:
            mt, why = h.apply_mutant(text, mid, pat, repl)
            print(f"APPLY {mid} {label} result={'applied' if mt is not None else 'refused'} why={why} "
                  f"sha256={hashlib.sha256(mt.encode()).hexdigest()[:16] if mt else '-'}")


if __name__ == "__main__":
    main()
