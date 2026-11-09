#!/usr/bin/env python3
"""Generate 8 one-edit forgeries of the FILED C2 tool in scratch. Lane untouched."""
import hashlib, shutil, sys, pathlib

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
SCR = pathlib.Path("/fast/scratch/hyaku/souji-r92/R92MutC2")
SRC = LANE / "tools/souji-record-agreement.py"
src = SRC.read_text(encoding="utf-8")
assert hashlib.sha256(SRC.read_bytes()).hexdigest().startswith("fc0e35c2"), "filed tool hash drift"

def one(name, old, new):
    n = src.count(old)
    assert n == 1, f"{name}: anchor count={n}"
    (SCR / f"{name}.py").write_text(src.replace(old, new), encoding="utf-8")
    print(f"{name}: sha256={hashlib.sha256((SCR/f'{name}.py').read_bytes()).hexdigest()[:12]}")

# (a) _straddling_sequence search window 3 instead of 4 bytes back
one("A_window3",
    "    for start in range(cut - 1, max(cut - 4, 0) - 1, -1):",
    "    for start in range(cut - 1, max(cut - 3, 0) - 1, -1):")

# (b) strict decode replaced by a lead-byte range table missing E0/ED/F0/F4 second-byte restrictions

# Build replacement carefully on decoded line
old_decode = "                if len(raw[start:end].decode(\"utf-8\", \"strict\")) == 1:"
assert src.count(old_decode) == 1
replacement = """                cand = raw[start:end]
                ok = bool(cand) and ((0xC2 <= cand[0] <= 0xDF and len(cand) == 2) or (0xE0 <= cand[0] <= 0xEF and len(cand) == 3) or (0xF0 <= cand[0] <= 0xF7 and len(cand) == 4)) and all(0x80 <= b <= 0xBF for b in cand[1:])
                if ok:"""
one("B_leadtable", old_decode, replacement)

# (c) decode with surrogatepass: strict->surrogatepass in _straddling_sequence only
one("C_surrogatepass",
    "                if len(raw[start:end].decode(\"utf-8\", \"strict\")) == 1:",
    "                if len(raw[start:end].decode(\"utf-8\", \"surrogatepass\")) == 1:")

# (d) len(...) == 1 relaxed to >= 1
one("D_len_ge1",
    "                if len(raw[start:end].decode(\"utf-8\", \"strict\")) == 1:",
    "                if len(raw[start:end].decode(\"utf-8\", \"strict\")) >= 1:")

# (e) head cut moved forward instead of back: seq[0] -> seq[1]
one("E_head_fwd",
    "    seq = _straddling_sequence(raw, h)\n    return seq[0] if seq else h\n",
    "    seq = _straddling_sequence(raw, h)\n    return seq[1] if seq else h\n")

# (f) tail cut moved back instead of forward: seq[1] -> seq[0]
one("F_tail_back",
    "    seq = _straddling_sequence(raw, t)\n    return seq[1] if seq else t\n",
    "    seq = _straddling_sequence(raw, t)\n    return seq[0] if seq else t\n")

# (g) end range off by one (min(start + 3, ...) instead of +4)
one("G_end_minus1",
    "        for end in range(cut + 1, min(start + 4, len(raw)) + 1):",
    "        for end in range(cut + 1, min(start + 3, len(raw)) + 1):")

# (h) repro-pair special case keyed on the cell text (KFF14/KFF15 payloads): if tail text == "\u2026" + "fatal: inv" marker... key on exact repro marker text
old_cut = """    seq = _straddling_sequence(raw, t)
    return seq[1] if seq else t"""
new_cut = """    seq = _straddling_sequence(raw, t)
    if seq and b"fatal: inv" in raw:
        return t
    return seq[1] if seq else t"""
one("H_reprokey", old_cut, new_cut)
print("OK")
