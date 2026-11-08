#!/usr/bin/env python3
"""R91ExecC2Tool reproducer: the filed tool's `_cut_tail` can land INSIDE a valid sequence.

Run:  python3 -B .ufo/waves/round-91/w1/R91ExecC2Tool/repro-cut-tail-split.py
Reads the lane read-only; imports the filed tool from tools/ (no bytecode written).
"""
import hashlib
import importlib.util
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FILED = LANE + "/tools/souji-record-agreement.py"

spec = importlib.util.spec_from_file_location("filed", FILED)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

# A: an invalid 4-octet lead (F0 80) closes the continuation run before the cut, so `_cut_tail` advances by the
#    DECLARED length (4) instead of to the end of the run; index 114 is U+0085's continuation, lead C2 at 113.
A = b"a" * 110 + b"\xf0" + b"\x80" + b"a" + b"\xc2\x85" + b"b" * 95
# B: the same excerpt with a RAW 0x85 at the same place (no lead octet anywhere before it).
B = b"a" * 110 + b"\xf0" + b"\x80" + b"a" + b"b" + b"\x85" + b"b" * 95


def run(raw):
    h = tool._cut_head(raw, 100)
    t = tool._cut_tail(raw, len(raw) - 99)
    cell = tool._one_line_bytes(raw)
    return h, t, cell


for name, raw in (("A", A), ("B", B)):
    h, t, cell = run(raw)
    print(f"{name} len={len(raw)} sha256={hashlib.sha256(raw).hexdigest()}")
    print(f"   bytes[108:116]={raw[108:116].hex(' ')}  head_cut={h} tail_cut={t} "
          f"raw[tail_cut]=0x{raw[t]:02x}  window_octets={h + 3 + (len(raw) - t)}")
    print(f"   cell={cell!r}")

ca, cb = run(A)[2], run(B)[2]
print(f"CELLS_EQUAL={ca == cb}  (A's 0x85 belongs to a valid U+0085; B's 0x85 is a lone raw byte)")
print(f"A_x85_spellings={ca.count(chr(92) + 'x85')} A_u0085_spellings={ca.count(chr(92) + 'u0085')}")
