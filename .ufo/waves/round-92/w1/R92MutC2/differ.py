#!/usr/bin/env python3
"""Distinguishing payloads: filed vs each survivor, direct _one_line_bytes comparison."""
import importlib.util, sys, pathlib
LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
SCR = pathlib.Path("/fast/scratch/hyaku/souji-r92/R92MutC2")

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

filed = load("filed_tool", LANE / "tools/souji-record-agreement.py")
def show(tag, raw):
    row = [f"### {tag}: len={len(raw)} raw_hex={raw.hex()}"]
    for n in ["A_window3","C_surrogatepass","D_len_ge1","E_head_fwd","H_reprokey"]:
        mod = load("m_" + n, SCR / f"{n}.py")
        a, b = filed._one_line_bytes(raw), mod._one_line_bytes(raw)
        row.append(f"  {n}: differ={a != b}\n    filed : {a!r}\n    forgery: {b!r}")
    print("\n".join(row), flush=True)

# C: ED A0 80 straddling tail cut (t=103 for len 202), then valid U+0085
show("C_tail_surrogate_ED_A0_80",
     b"x"*102 + b"\xed\xa0\x80" + b"\xc2\x85" + b"y"*95)
# C variant: same but cut between A0 and 80
show("C_tail_surrogate_ED_A0__80",
     b"x"*101 + b"\xed\xa0\x80" + b"\xc2\x85" + b"y"*95)
# D: ASCII straddling tail cut (multi-char candidate)
show("D_tail_ascii_aa",
     b"a"*102 + b"b"*200)
# E: U+20AC straddling head cut (h=100)
show("E_head_euro",
     b"x"*99 + b"\xe2\x82\xac" + b"y"*120)
# H: marker text + valid C2 85 straddling tail cut
show("H_marker_plus_valid_nel",
     b"fatal: inv " + b"x"*91 + b"\xc2\x85" + b"y"*95)
# A: 4-byte U+1D11E straddling tail cut (both must agree)
show("A_tail_4byte_U+1D11E",
     b"x"*100 + b"\xf0\x9d\x84\x9e" + b"y"*99)
# stress all survivors vs filed on systematic tokens near both cuts (counts, not prints)
import itertools
TOKS = [b"a", b"\xc2\x85", b"\xe2\x82\xac", b"\xf0\x9d\x84\x9e", b"\x85", b"\xf0\x80", b"\xe0",
        b"\xc0\xaf", b"\xe0\x80\x80", b"\xed\xa0\x80", b"\xf4\x90\x80\x80", b"\xf5\x80", b"\xc1\xbf",
        b"\xe2\x82", b"\xff", b"fatal: inv"]
mods = {n: load("s_" + n, SCR / f"{n}.py") for n in
        ["A_window3","C_surrogatepass","D_len_ge1","E_head_fwd","H_reprokey"]}
counts = {n: 0 for n in mods}
n = 0
for off in (97, 99, 100, 101, 104, 105):
    for a, b in itertools.product(TOKS, repeat=2):
        raw = b"x"*(off-12) + a + b + b"z"*110
        n += 1
        f = filed._one_line_bytes(raw)
        for name, mod in mods.items():
            if mod._one_line_bytes(raw) != f:
                counts[name] += 1
print(f"STRESS payloads={n} differ_counts={counts}")
