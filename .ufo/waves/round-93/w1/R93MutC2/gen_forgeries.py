#!/usr/bin/env python3
"""Generate 9 one-edit forgeries of the FILED C2 tool in scratch. Lane untouched.

Seat R93MutC2 (souji r93 C2). Each forgery is ONE contiguous text edit (applied
exactly once, anchor count asserted == 1) to tools/souji-record-agreement.py
(sha256 fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75).

(a)  A_window3      R92MutC2 A_window3 verbatim: search window 3 instead of 4.
(b1) b1_len230_nomove  len==230 -> no cut moves (r91-style raw cuts); else filed.
(b2) b2_len230_correct len!=230 -> limit 201 (filed at exactly 230); else swap.
(c)  H_reprokey     R92MutC2 H verbatim: if a sequence straddles the tail and the
                    payload contains b"fatal: inv", stay at the raw cut.
(d)  d_headback1    head cut moved one byte too far back when straddling.
(e)  e_tail4byte    tail cut end off by one (seq[1]-1) only for 4-byte sequences.
(f)  f_table_noF4cap range-table decoder missing ONLY the F4 second-byte 8F cap.
(g)  g_table_noEDcap range-table decoder missing ONLY the ED second-byte 9F cap.
(h)  h_filler_a     correct (limit 200) only when filler byte b'a' present.
"""
import hashlib
import pathlib

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
SCR = pathlib.Path("/fast/scratch/hyaku/souji-r93/R93MutC2")
FORG = SCR / "forg"
FORG.mkdir(parents=True, exist_ok=True)
SRC = LANE / "tools/souji-record-agreement.py"
src = SRC.read_text(encoding="utf-8")
assert hashlib.sha256(SRC.read_bytes()).hexdigest().startswith("fc0e35c2"), "filed tool hash drift"

W = "    for start in range(cut - 1, max(cut - 4, 0) - 1, -1):"
D = '                if len(raw[start:end].decode("utf-8", "strict")) == 1:'
HEADCUT = "    seq = _straddling_sequence(raw, h)\n    return seq[0] if seq else h\n"
TAILCUT = "    seq = _straddling_sequence(raw, t)\n    return seq[1] if seq else t\n"
ONE01 = "def _one_line_bytes(raw: bytes, limit: int = 200) -> str:"


def one(name, old, new):
    n = src.count(old)
    assert n == 1, f"{name}: anchor count={n}"
    (FORG / f"{name}.py").write_text(src.replace(old, new, 1), encoding="utf-8")
    h = hashlib.sha256((FORG / f"{name}.py").read_bytes()).hexdigest()
    print(f"{name}: sha256={h}")


# (a) A_window3 — R92MutC2 verbatim anchor.
one("a_window3", W, "    for start in range(cut - 1, max(cut - 3, 0) - 1, -1):")

# (b1) len==230 -> raw cuts (no boundary move); else the filed body below.
one("b1_len230_nomove", ONE01,
    ONE01 + '\n    if len(raw) == 230:  # b1 forgery: raw cuts at the sweep length'
    '\n        return _escape_text(_decode_record(raw[: limit // 2]) + "\\u2026" + _decode_record(raw[limit // 2:]))')

# (b2) len!=230 -> limit 201 (a different boundary-aligned window); filed at 230.
one("b2_len230_correct", ONE01,
    ONE01 + '\n    if len(raw) != 230:  # b2 forgery: only the sweep length is exact'
    '\n        limit = 201')

# (c) H_reprokey — R92MutC2 H verbatim anchor (tail branch; `if seq` guard kept).
one("c_reprokey", TAILCUT,
    "    seq = _straddling_sequence(raw, t)\n"
    '    if seq and b"fatal: inv" in raw:  # c forgery: repro-marker key\n'
    '        return t\n'
    "    return seq[1] if seq else t\n")

# (d) head cut backed one byte too far when a sequence straddles.
one("d_headback1", HEADCUT,
    "    seq = _straddling_sequence(raw, h)\n"
    "    if seq and seq[0] > 0:  # d forgery: one byte too far\n"
    "        return seq[0] - 1\n"
    "    return seq[0] if seq else h\n")

# (e) tail cut end off by one (into the sequence) only for 4-byte sequences.
one("e_tail4byte", TAILCUT,
    "    seq = _straddling_sequence(raw, t)\n"
    "    if seq and seq[1] - seq[0] == 4:  # e forgery: one byte short\n"
    "        return seq[1] - 1\n"
    "    return seq[1] if seq else t\n")

# (f) range table missing ONLY the F4 second-byte upper cap (all other rows exact).
F_F4 = (
    '                cand = raw[start:end]\n'
    '                b0 = cand[0]\n'
    '                if 0xC2 <= b0 <= 0xDF:\n'
    '                    ok = len(cand) == 2 and 0x80 <= cand[1] <= 0xBF\n'
    '                elif 0xE0 <= b0 <= 0xEF:\n'
    '                    ok = len(cand) == 3 and (0xA0 if b0 == 0xE0 else 0x80) <= cand[1] <= 0xBF and 0x80 <= cand[2] <= 0xBF\n'
    '                elif 0xF0 <= b0 <= 0xF4:\n'
    '                    ok = len(cand) == 4 and (0x90 if b0 == 0xF0 else 0x80) <= cand[1] <= 0xBF and 0x80 <= cand[2] <= 0xBF and 0x80 <= cand[3] <= 0xBF\n'
    '                else:\n'
    '                    ok = False\n'
    '                if ok:'
)
one("f_table_noF4cap", D, F_F4)

# (g) range table missing ONLY the ED second-byte upper cap.
G_ED = (
    '                cand = raw[start:end]\n'
    '                b0 = cand[0]\n'
    '                if 0xC2 <= b0 <= 0xDF:\n'
    '                    ok = len(cand) == 2 and 0x80 <= cand[1] <= 0xBF\n'
    '                elif 0xE0 <= b0 <= 0xEF:\n'
    '                    ok = len(cand) == 3 and (0xA0 if b0 == 0xE0 else 0x80) <= cand[1] <= (0xBF if b0 == 0xED else 0xBF) and 0x80 <= cand[2] <= 0xBF\n'
    '                elif 0xF0 <= b0 <= 0xF4:\n'
    '                    ok = len(cand) == 4 and (0x90 if b0 == 0xF0 else 0x80) <= cand[1] <= (0x8F if b0 == 0xF4 else 0xBF) and 0x80 <= cand[2] <= 0xBF and 0x80 <= cand[3] <= 0xBF\n'
    '                else:\n'
    '                    ok = False\n'
    '                if ok:'
)
one("g_table_noEDcap", D, G_ED)

# (h) filed (limit 200) only when the filler byte b'a' is present; else limit 199.
one("h_filler_a", ONE01,
    ONE01 + "\n    if b\"a\" not in raw:  # h forgery: exact only on 'a' filler"
    "\n        limit = 199")

print("OK")
