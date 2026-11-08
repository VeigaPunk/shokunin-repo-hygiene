#!/usr/bin/env python3
"""R91ReviewerC2: byte-level derivation of C2's boundary claim, on the frozen bytes.

Reads the lane read-only; writes only under --work (its own scratch) and prints receipts. Importing the two tools
is used only for the INTERNAL cut arithmetic the claim names (`_cut_head`/`_cut_tail`/`_one_line_bytes`); the
public path is measured separately by importing the frozen r91 fixture and reading its K4 cell.
"""
import importlib.util
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv):
    work = os.path.abspath(argv[0])
    if os.path.exists(work) and os.listdir(work):
        print(f"WORK-NOT-EMPTY {work}")
        return 2
    os.makedirs(work, exist_ok=True)
    after = load(os.path.join(LANE, "tools/souji-record-agreement.py"), "r91tool")
    before = load(os.path.join(LANE, "census/round-91/controls/c2-before-tool.py"), "r90tool")
    fixture = load(os.path.join(LANE, "tests/fixtures/r91-k4-flagfail.py"), "r91fixture")

    # --- 1. the payload, byte for byte, exactly as the fixture's FAKE_WRITER "nelcut" mode builds it
    payload = b"fatal: nel " + b"x" * 90 + b"\xc2\x85" + b"s" * 98
    print(f"PAYLOAD len={len(payload)} sha256_sha={__import__('hashlib').sha256(payload).hexdigest()}")
    print(f"INDEX 0xc2={payload.index(b'\xc2')} 0x85={payload.index(b'\x85')} "
          f"first_s={payload.index(b's', 103)}")
    print(f"BYTES[99:104]={payload[99:104]!r}")

    # --- 2. the r90 window arithmetic (the before tool's own expression)
    limit = 200
    head = limit // 2
    keep = limit - head - 1
    h90, t90 = head, len(payload) - keep
    win90 = payload[:h90] + "\u2026".encode("utf-8") + payload[-keep:]
    cell90 = before._one_line_bytes(payload)
    print(f"R90 head={h90} keep={keep} tail_start={t90} window_len={len(win90)}")
    print(f"R90 window_tail_first={win90[h90 + 3:h90 + 4].hex()} "
          f"tail_is_continuation={0x80 <= win90[h90 + 3] <= 0xBF}")
    print(f"R90 decoded_tail0=U+{ord(chr(0xDC00 + win90[h90 + 3])):04X} (surrogate)")
    print(f"R90 CELL={cell90!r}")
    print(f"R90 CELL_HAS_\\x85={'\\x85' in cell90} CELL_HAS_\\u0085={'\\u0085' in cell90}")

    # --- 3. the filed cut arithmetic
    hf = after._cut_head(payload, head)
    t0 = len(payload) - keep
    tf = after._cut_tail(payload, t0)
    cellf = after._one_line_bytes(payload)
    winf_len = hf + 3 + (len(payload) - tf)
    print(f"AFTER _cut_head(payload,{head})={hf}  _cut_tail(payload,{t0})={tf} "
          f"(t0-1={payload[t0 - 1]:#04x} at0={payload[t0]:#04x} at1={payload[t0 + 1]:#04x})")
    print(f"AFTER head_end={payload[hf - 1]:#04x} head_is_lead={0xC0 <= payload[hf - 1] <= 0xF7} "
          f"head_is_cont={0x80 <= payload[hf - 1] <= 0xBF}")
    print(f"AFTER elided_middle={payload[hf:tf]!r} len={tf - hf}")
    print(f"AFTER window_len={winf_len}")
    print(f"AFTER CELL={cellf!r}")
    print(f"AFTER CELL_HAS_\\x85={'\\x85' in cellf} CELL_HAS_\\u0085={'\\u0085' in cellf}")

    # --- 4. the public path: the frozen fixture's own K4 cell for the nelcut mode
    for label, tool in (("r90", os.path.join(LANE, "census/round-91/controls/c2-before-tool.py")),
                        ("r91", os.path.join(LANE, "tools/souji-record-agreement.py"))):
        kit = fixture.make_kit(os.path.join(work, "kit-" + label), tool)
        out, rows = fixture.run_case(kit, "nelcut")
        print(f"PUBLIC {label} rows={len(rows)} cell={rows[0]!r}")
        print(f"PUBLIC {label} cell_has_\\x85={'\\x85' in rows[0]} cell_has_\\u0085={'\\u0085' in rows[0]}")
        # the same tool on the raw-byte mode, for the "share a cell" pair question
        _o, rows_b = fixture.run_case(kit, "nelbyte")
        print(f"PUBLIC {label} nelbyte cell={rows_b[0]!r}")

    # --- 5. "two materially different delegated failures share a cell" under the r90 tool only.
    # A: valid UTF-8 U+0085 at the tail straddle (fixture mode nelcut).  D: the INVALID raw 0x85 at the same
    # position, same head, same tail suffix.
    d = b"fatal: nel " + b"x" * 89 + b"AB" + b"\x85" + b"s" * 98
    assert len(d) == 201
    d90, df = before._one_line_bytes(d), after._one_line_bytes(d)
    print(f"PAIR D len={len(d)} r90_identical_to_nelcut={d90 == cell90} r91_identical={df == cellf}")
    print(f"PAIR D r90_cell={d90!r}")
    print(f"PAIR D r91_cell={df!r}")

    # --- 6. orphan continuation with NO lead at the tail start must keep its \xNN spelling
    orphan = bytearray(b"fatal: nel " + b"y" * 190)  # 201 bytes, so t0 = 102
    assert len(orphan) == 201
    orphan[102] = 0x85
    orphan = bytes(orphan)
    t_o = len(orphan) - keep
    print(f"ORPHAN t0={t_o} at={orphan[t_o]:#04x} prev={orphan[t_o - 1]:#04x} "
          f"_cut_tail={after._cut_tail(orphan, t_o)} cell={after._one_line_bytes(orphan)!r}")

    # --- 7. sweep: every valid-UTF-8 payload must yield no raw-byte spelling anywhere in the cell
    seqs = {"nel2": "\u0085".encode("utf-8"), "eacute2": "\u00e9".encode("utf-8"),
            "ls2028": "\u2028".encode("utf-8"), "emoji4": "\U0001f600".encode("utf-8")}
    bad = []
    checked = 0
    head_moved = tail_moved = 0
    for name, seq in seqs.items():
        for total in range(201, 207):
            for pos in list(range(95, 106)) + list(range(total - 106, total - 97)):
                if pos < 11 or pos + len(seq) > total:
                    continue
                p = b"fatal: nel " + b"x" * (pos - 11) + seq + b"z" * (total - pos - len(seq))
                assert len(p) == total and p.find(seq) == pos
                cell = after._one_line_bytes(p)
                checked += 1
                if after._cut_head(p, 100) != 100:
                    head_moved += 1
                if after._cut_tail(p, len(p) - 99) != len(p) - 99:
                    tail_moved += 1
                if re.search(r"\\x[0-9a-f]{2}", cell):
                    bad.append((name, total, pos, cell))
                if "\u2026" not in cell:
                    bad.append(("no-ellipsis", name, total, pos, cell))
    print(f"SWEEP checked={checked} head_moved={head_moved} tail_moved={tail_moved} "
          f"raw_byte_spellings_or_bad={len(bad)}")
    for b in bad[:10]:
        print(f"SWEEP-BAD {b!r}")

    # --- 8. the before tool on the same sweep: count boundary violations (control for sentence 1)
    before_bad = 0
    for name, seq in seqs.items():
        for total in range(201, 207):
            for pos in list(range(95, 106)) + list(range(total - 106, total - 97)):
                if pos < 11 or pos + len(seq) > total:
                    continue
                p = b"fatal: nel " + b"x" * (pos - 11) + seq + b"z" * (total - pos - len(seq))
                if re.search(r"\\x[0-9a-f]{2}", before._one_line_bytes(p)):
                    before_bad += 1
    print(f"SWEEP r90_arm_raw_byte_spellings={before_bad}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    finally:
        pass
