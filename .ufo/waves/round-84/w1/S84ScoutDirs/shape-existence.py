#!/usr/bin/env python3
"""S84ScoutDirs probe v3: for every r84 population row, is the SHAPE it uses (the directory-name class)
present in the lane's REAL tree, and at the EXACT path the row names?

Read-only on the lane. Prints a table; writes nothing.

Usage: shape-existence.py
"""
import os
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
POP = os.path.join(LANE, "census/round-84/c1-false-rows.tsv")

# the real shape census of the lane's own tree (working tree; .ufo/waves/ is gitignored)
own = {}
for d in os.listdir(os.path.join(LANE, ".ufo/waves")):
    if not d.startswith("round-"):
        continue
    base = os.path.join(LANE, ".ufo/waves", d)
    if not os.path.isdir(base):
        continue
    for k in os.listdir(base):
        if os.path.isdir(os.path.join(base, k)):
            own.setdefault(k, []).append(f".ufo/waves/{d}/{k}")

# census-side capture shapes under census/round-N/
cen_waves, cen_wave, cen_recwave = [], [], []
for d in sorted(os.listdir(os.path.join(LANE, "census"))):
    if not d.startswith("round-"):
        continue
    base = os.path.join(LANE, "census", d)
    if os.path.isdir(os.path.join(base, "waves")):
        cen_waves.append(d)
    if os.path.isdir(os.path.join(base, "wave")):
        cen_wave.append(d)
    rd = os.path.join(base, "records")
    if os.path.isdir(rd):
        for k in os.listdir(rd):
            if os.path.isdir(os.path.join(rd, k)) and k.startswith("wave-"):
                cen_recwave.append(f"census/{d}/records/{k}")


def shape_of(path):
    """The directory-name class the path uses."""
    parts = path.split("/")
    for i, p in enumerate(parts):
        if p.startswith("round-"):
            rest = parts[i + 1:]
            return (rest[0] if rest else "-", "/".join(parts[:i + 1]))
    return ("-", "/".join(parts[:-1]))


def real_shape_exists(path):
    """Does the EXACT directory path (the part before the file name) exist in the real tree?"""
    d = os.path.dirname(path)
    return os.path.isdir(os.path.join(LANE, d))


def shape_present_somewhere(cls):
    if cls in own:
        return f"own-tree/{cls} x{len(own[cls])}"
    if cls == "waves" and cen_waves:
        return f"census/waves/ x{len(cen_waves)}"
    if cls == "wave" and cen_wave:
        return f"census/wave/ x{len(cen_wave)}"
    if cls.startswith("wave-") and cen_recwave:
        return f"census/records/wave-*/ x{len(cen_recwave)}"
    return "NOT PRESENT IN REAL TREE"


def main():
    rows = [l.rstrip("\n").split("\t") for l in open(POP, encoding="utf-8")
            if l.strip() and not l.startswith("#")]
    print("ROW   EXPECTED   TARGET")
    print("                 shape-class | shape exists in real tree (somewhere) | EXACT dir path exists in real tree")
    for rid, where, rlabel, popl, item, cls, target, exp, rc, src in rows:
        if cls != "MOVED":
            continue
        shape, parent = shape_of(target)
        tag = "T" if exp == "MOVED" else "F"
        print(f"{tag} {rid:6s} {exp:9s} {target}")
        print(f"                 class={shape!r} | {shape_present_somewhere(shape)} | "
              f"exact dir {parent}/ -> {'PRESENT' if real_shape_exists(target) else 'ABSENT'}")


if __name__ == "__main__":
    sys.exit(main())
