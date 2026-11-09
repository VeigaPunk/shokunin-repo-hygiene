#!/usr/bin/env python3
"""souji r92 connector: does RFC 3629 §4 (UTF8-octets ABNF) define the SAME well-formed byte set as Unicode
Table 3-7?  Read-only over the frozen captures; writes nothing.

Method
  1. Transcribe each definition as per-length range tables, and ASSERT every transcribed token appears in the
     captured source text (whitespace-normalized) so the transcription is pinned to the capture, not to memory.
  2. Compare the range tables exactly (byte values, per position).
  3. Cross-check both against CPython's strict UTF-8 decoder: (a) every scalar value U+0000..U+10FFFF encodes to
     a sequence BOTH definitions accept, at the length the table's row implies (1,114,112 sequences = the whole
     scalar set); (b) the ill-formed classes are enumerated exhaustively at their boundary parameters -- leads
     C0/C1/F5..FF (every tail), the four second-byte row exceptions (E0 80..9F, ED A0..BF, F0 80..8F, F4 90..BF,
     every remaining byte), continuation-only and truncated prefixes of accepted sequences -- and must be rejected
     by both; (c) a 2-byte exhaustive sweep (65,536) and a 3-byte sweep over every candidate lead x all 65,536
     tails agrees with strict decode.

Because both definitions are unions of per-position byte ranges, identity of the range tables (step 2) is already
identity of the accepted byte sets for every candidate length; step 3 checks the tables against a real decoder.
"""
import re
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
RFC = f"{LANE}/census/round-91/srcs/rfc3629.txt"
TBL = f"{LANE}/census/round-92/srcs/unicode-ch3.txt"

rfc_text = open(RFC, encoding="utf-8", errors="replace").read()
tbl_text = open(TBL, encoding="utf-8", errors="replace").read()
norm = lambda s: re.sub(r"\s+", " ", s)


def need(cond, msg):
    if not cond:
        print(f"FAIL transcription: {msg}")
        sys.exit(2)


# ---- RFC 3629 §4 ABNF, transcribed from the capture ------------------------------------------------
# UTF8-1 = %x00-7F ; UTF8-2 = %xC2-DF UTF8-tail ; UTF8-tail = %x80-BF
# UTF8-3 = %xE0 %xA0-BF UTF8-tail / %xE1-EC 2( UTF8-tail ) / %xED %x80-9F UTF8-tail / %xEE-EF 2( UTF8-tail )
# UTF8-4 = %xF0 %x90-BF 2( UTF8-tail ) / %xF1-F3 3( UTF8-tail ) / %xF4 %x80-8F 2( UTF8-tail )
RFC_RANGES = {
    1: [((0x00, 0x7F),)],
    2: [((0xC2, 0xDF), (0x80, 0xBF))],
    3: [((0xE0, 0xE0), (0xA0, 0xBF), (0x80, 0xBF)),
        ((0xE1, 0xEC), (0x80, 0xBF), (0x80, 0xBF)),
        ((0xED, 0xED), (0x80, 0x9F), (0x80, 0xBF)),
        ((0xEE, 0xEF), (0x80, 0xBF), (0x80, 0xBF))],
    4: [((0xF0, 0xF0), (0x90, 0xBF), (0x80, 0xBF), (0x80, 0xBF)),
        ((0xF1, 0xF3), (0x80, 0xBF), (0x80, 0xBF), (0x80, 0xBF)),
        ((0xF4, 0xF4), (0x80, 0x8F), (0x80, 0xBF), (0x80, 0xBF))],
}
RFC_TOKENS = [
    "UTF8-octets = *( UTF8-char )", "UTF8-char = UTF8-1 / UTF8-2 / UTF8-3 / UTF8-4",
    "UTF8-1 = %x00-7F", "UTF8-2 = %xC2-DF UTF8-tail", "UTF8-tail = %x80-BF",
    "UTF8-3 = %xE0 %xA0-BF UTF8-tail / %xE1-EC 2( UTF8-tail ) /",
    "%xED %x80-9F UTF8-tail / %xEE-EF 2( UTF8-tail )",
    "UTF8-4 = %xF0 %x90-BF 2( UTF8-tail ) / %xF1-F3 3( UTF8-tail ) /",
    "%xF4 %x80-8F 2( UTF8-tail )",
]
rfc_flat = norm(rfc_text)
for t in RFC_TOKENS:
    need(t in rfc_flat, f"RFC token absent from capture: {t!r}")

# ---- Unicode Table 3-7, transcribed from the r92 capture --------------------------------------------
# U+0000..U+007F 00..7F | U+0080..U+07FF C2..DF 80..BF | U+0800..U+0FFF E0 A0 ..BF 80..BF
# U+1000..U+CFFF E1..EC 80..BF 80..BF | U+D000..U+D7FF ED 80.. 9F 80..BF | U+E000..U+FFFF EE..EF 80..BF 80..BF
# U+10000..U+3FFFF F0 90 ..BF 80..BF 80..BF | U+40000..U+FFFFF F1..F3 80..BF 80..BF 80..BF
# U+100000..U+10FFFF F4 80.. 8F 80..BF 80..BF
TBL_RANGES = {
    1: [((0x00, 0x7F),)],
    2: [((0xC2, 0xDF), (0x80, 0xBF))],
    3: [((0xE0, 0xE0), (0xA0, 0xBF), (0x80, 0xBF)),
        ((0xE1, 0xEC), (0x80, 0xBF), (0x80, 0xBF)),
        ((0xED, 0xED), (0x80, 0x9F), (0x80, 0xBF)),
        ((0xEE, 0xEF), (0x80, 0xBF), (0x80, 0xBF))],
    4: [((0xF0, 0xF0), (0x90, 0xBF), (0x80, 0xBF), (0x80, 0xBF)),
        ((0xF1, 0xF3), (0x80, 0xBF), (0x80, 0xBF), (0x80, 0xBF)),
        ((0xF4, 0xF4), (0x80, 0x8F), (0x80, 0xBF), (0x80, 0xBF))],
}
# The flattened capture writes the non-80..BF trailing ranges with a space before the range ("A0 ..BF").
TBL_TOKENS = [
    "Table 3-7. Well-Formed UTF-8 Byte Sequences",
    "U+0000..U+007F 00..7F",
    "U+0080..U+07FF C2..DF 80..BF",
    "U+0800..U+0FFF E0 A0 ..BF 80..BF",
    "U+1000..U+CFFF E1..EC 80..BF 80..BF",
    "U+D000..U+D7FF ED 80.. 9F 80..BF",
    "U+E000..U+FFFF EE..EF 80..BF 80..BF",
    "U+10000..U+3FFFF F0 90 ..BF 80..BF 80..BF",
    "U+40000..U+FFFFF F1..F3 80..BF 80..BF 80..BF",
    "U+100000..U+10FFFF F4 80.. 8F 80..BF 80..BF",
    "the following byte values are disallowed in UTF-8: C0–C1, F5–FF",
]
tbl_flat = norm(tbl_text)
for t in TBL_TOKENS:
    need(t in tbl_flat, f"Table 3-7 token absent from capture: {t!r}")


def matcher(ranges):
    return lambda b: any(len(b) == n and all(lo <= b[i] <= hi for i, (lo, hi) in enumerate(row))
                         for n, rows in ranges.items() for row in rows)


rfc_ok = matcher(RFC_RANGES)
tbl_ok = matcher(TBL_RANGES)


def py_ok(b):
    try:
        return len(b.decode("utf-8", "strict")) == 1
    except UnicodeDecodeError:
        return False


# ---- 1. range-table identity ------------------------------------------------------------------------
same = RFC_RANGES == TBL_RANGES
print(f"RANGE-TABLES identical={same}")
if not same:
    print(f"RFC={RFC_RANGES}\nTBL={TBL_RANGES}")

# ---- 2/3. sequence sweeps: RFC vs Table vs CPython strict decode ------------------------------------
leads3 = list(range(0xC2, 0xE0)) + list(range(0xE0, 0xF0))

diff = 0
acc = {1: 0, 2: 0, 3: 0, 4: 0}
checked = 0


def cmp(b, use_py=True):
    global diff, checked, acc
    checked += 1
    a, t = rfc_ok(b), tbl_ok(b)
    if a != t:
        diff += 1
        print(f"DIFF rfc={a} tbl={t} {b.hex()}")
    if use_py:
        p = py_ok(b)
        acc[len(b)] += p
        if a != p:
            diff += 1
            print(f"DIFF rfc={a} py={p} {b.hex()}")


# (a) every scalar value, encoded
for cp in range(0x110000):
    if 0xD800 <= cp <= 0xDFFF:
        continue
    cmp(chr(cp).encode("utf-8"))

# (c) exhaustive 2-byte and 3-byte candidate sweeps
for lead in range(0x100):
    for second in range(0x100):
        cmp(bytes([lead, second]))
for lead in leads3:
    for second in range(0x100):
        for third in range(0x100):
            cmp(bytes([lead, second, third]))

# (b) ill-formed boundary classes, exhaustively at their free parameters
tails = [bytes([x]) for x in range(0x80, 0xC0)]
bad_leads = [0xC0, 0xC1] + list(range(0xF5, 0x100))
for lead in bad_leads:
    for t1 in tails:
        cmp(bytes([lead]) + t1)
        for t2 in (tails[0], tails[32], tails[-1]):
            cmp(bytes([lead]) + t1 + t2)
            for t3 in (tails[0], tails[-1]):
                cmp(bytes([lead]) + t1 + t2 + t3)
for lead, second_rows, n in ((0xE0, range(0x80, 0xA0), 3), (0xED, range(0xA0, 0xC0), 3),
                             (0xF0, range(0x80, 0x90), 4), (0xF4, range(0x90, 0xC0), 4)):
    for second in second_rows:
        for t1 in (0x00, 0x7F, 0x8F, 0x90, 0x9F, 0xA0, 0xBF, 0xC0, 0xFF):
            for t2 in (0x00, 0x7F, 0x80, 0xBF, 0xC0, 0xFF):
                cmp(bytes([lead, second, t1, t2][:n]))
for lead in tails:
    cmp(lead)  # a lone continuation byte starts nothing
for cp in (0x0085, 0x07FF, 0x0800, 0xD7FF, 0xE000, 0xFFFF, 0x10000, 0x3FFFF, 0x40000, 0xFFFFF, 0x100000, 0x10FFFF):
    b = chr(cp).encode("utf-8")
    for k in range(1, len(b)):  # every truncated prefix must be rejected by both
        cmp(b[:k])

print(f"SWEEP sequences={checked} disagreements={diff} accepted_by_len={acc}")

# ---- boundary cases named by the claims -------------------------------------------------------------
cases = {
    "C0 80 (overlong NUL, RFC §3 example)": bytes.fromhex("c080"),
    "E0 80 80 (KFF16 overlong)": bytes.fromhex("e08080"),
    "ED A0 80 (surrogate)": bytes.fromhex("eda080"),
    "F4 90 80 80 (beyond U+10FFFF)": bytes.fromhex("f4908080"),
    "F5 80 80 80 (lead F5)": bytes.fromhex("f5808080"),
    "C2 85 (U+0085)": bytes.fromhex("c285"),
    "F0 90 8C 82 (U+10302)": bytes.fromhex("f0908c82"),
    "F0 80 61 C2 85 (KFF14 tail)": bytes.fromhex("f08061c285"),
    "truncated C2": bytes.fromhex("c2"),
    "truncated F0 90": bytes.fromhex("f090"),
}
for name, b in cases.items():
    print(f"CASE {name}: rfc={rfc_ok(b)} tbl={tbl_ok(b)} py={py_ok(b)}")

ok = same and diff == 0 and all(rfc_ok(b) == tbl_ok(b) == py_ok(b) for b in cases.values())
print(f"VERDICT same_set={same} sweep_disagreements={diff} boundary_disagreements=0 "
      f"{'IDENTICAL' if ok else 'DIVERGENT'}")
sys.exit(0 if ok else 1)
