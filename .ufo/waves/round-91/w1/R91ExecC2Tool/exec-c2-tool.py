#!/usr/bin/env python3
"""R91ExecC2Tool: unit-level validation of the r91 C2 boundary repair in tools/souji-record-agreement.py.

Imports the FILED tool (read-only, no bytecode) and the before-arm control, then
  1. sweeps payloads of 201..260 bytes carrying 1-, 2-, 3- and 4-octet characters at every
     cut position (head 100 / tail L-99) and records cell, raw window octets, cell UTF-8
     bytes and the orphan check;
  2. quotes the before/after cell for 101p+C285+98s;
  3. checks raw-byte spelling preservation (lone 0x85, invalid lead at a cut);
  4. echoes the boundary-helper returns for the same payloads.

Writes matrix.tsv + matrix.json into the seat dir; writes nothing into the lane.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-91/w1/R91ExecC2Tool")
FILED = os.path.join(LANE, "tools/souji-record-agreement.py")
BEFORE = os.path.join(LANE, "census/round-91/controls/c2-before-tool.py")
ELL = "\u2026"


def sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # module body has no side effects (main() is __main__-gated)
    return mod


# ---- payload builders -------------------------------------------------------
CHARS = {1: b"A", 2: b"\xc2\x85", 3: b"\xe2\x82\xac", 4: b"\xf0\x9d\x84\x9e"}
FILL = b"#"


def build(length: int, seqs: list[tuple[int, bytes]]) -> bytes:
    buf = bytearray(FILL * length)
    for pos, seq in seqs:
        if pos < 0 or pos + len(seq) > length:
            raise AssertionError(f"placement {pos}+{len(seq)} outside 0..{length}")
        buf[pos:pos + len(seq)] = seq
    return bytes(buf)


def spans_overlap(a: tuple[int, bytes], b: tuple[int, bytes]) -> bool:
    (pa, sa), (pb, sb) = a, b
    return pa < pb + len(sb) and pb < pa + len(sa)


def window_bytes(raw: bytes, h: int, t: int) -> bytes:
    return raw[:h] + ELL.encode("utf-8") + raw[t:]


def classify_cut(mod, raw: bytes, idx: int) -> str:
    """What the byte at `idx` (the first byte the window excludes / the first byte the tail keeps) is:
    boundary          not a continuation octet (a legitimate cut point)
    orphan-beyond     a continuation octet past the end of the lead's declared sequence (invalid data)
    orphan-no-lead    a continuation octet with no lead octet before it in the run
    SPLIT             a continuation octet of a declared sequence whose lead sits on the other side of the cut
    """
    if idx <= 0 or idx >= len(raw) or not 0x80 <= raw[idx] <= 0xBF:
        return "boundary"
    i = idx
    while i > 0 and 0x80 <= raw[i - 1] <= 0xBF:
        i -= 1
    if i == 0:
        return "orphan-no-lead"
    lead = raw[i - 1]
    need = mod._utf8_seq_need(lead) if hasattr(mod, "_utf8_seq_need") else 0
    if not need:
        return "orphan-no-lead"
    return "SPLIT" if idx < i - 1 + need else "orphan-beyond"


def cut_state(mod, raw: bytes):
    head, keep = 100, 99
    cut_head = getattr(mod, "_cut_head", lambda _raw, h: h)      # r90 control has no boundary helpers
    cut_tail = getattr(mod, "_cut_tail", lambda _raw, t: t)
    h = cut_head(raw, head)
    t = cut_tail(raw, len(raw) - keep)
    if t < h:
        t = h
    return h, t


def analyse(mod, raw: bytes) -> dict:
    h, t = cut_state(mod, raw)
    cell = mod._one_line_bytes(raw)
    recon = mod._escape_text(mod._decode_record(raw[:h]) + ELL + mod._decode_record(raw[t:]))
    win = window_bytes(raw, h, t)
    decoded = mod._decode_record(raw[:h]) + ELL + mod._decode_record(raw[t:])
    surrogates = [f"U+{ord(c):04X}" for c in decoded if 0xDC80 <= ord(c) <= 0xDCFF]
    return {
        "head_cut": h,
        "tail_cut": t,
        "head_moved": h != 100,
        "tail_moved": t != len(raw) - 99,
        "head_boundary": classify_cut(mod, raw, h),
        "tail_boundary": classify_cut(mod, raw, t),
        "window_octets": len(win),
        "cell_utf8_bytes": len(cell.encode("utf-8")),
        "cell_chars": len(cell),
        "cell": cell,
        "x85_spellings": cell.count("\\x85"),
        "u0085_spellings": cell.count("\\u0085"),
        "surrogate_bytes": surrogates,
        "reconstruction_exact": cell == recon,
    }


def main() -> int:
    filed, before = load(FILED, "c2_filed_tool"), load(BEFORE, "c2_before_tool")
    rows: list[dict] = []

    def add(family: str, length: int, width: int, align: str, raw: bytes, note: str = "") -> None:
        a = analyse(filed, raw)
        rows.append({
            "family": family, "length": length, "width": width, "align": align,
            "payload_sha256": hashlib.sha256(raw).hexdigest(),
            "payload_hex": raw.hex() if family in ("preserve", "whole", "attack") else "",
            "payload_head_hex": raw[:120].hex(), "note": note, **a,
        })

    # Family A: a wide character straddles the HEAD cut (h=100); tail region untouched.
    for length in range(201, 261):
        for width in (1, 2, 3, 4):
            seq = CHARS[width]
            if width == 1:
                # a one-octet character cannot straddle: put it as the last head byte and at each elided side
                add("head-adjacent", length, 1, "head:last-kept=99", build(length, [(99, seq)]))
                add("head-adjacent", length, 1, "head:first-elided=100", build(length, [(100, seq)]))
                continue
            for hs in range(1, width):                     # hs bytes of the sequence lie before the cut
                s = 100 - hs
                add("head-straddle", length, width, f"head:lead={s}:split={hs}", build(length, [(s, seq)]))
    # Family B: a wide character straddles the TAIL cut (t=L-99); head region untouched (t-w >= 98).
    for length in range(201, 261):
        for width in (1, 2, 3, 4):
            seq = CHARS[width]
            t = length - 99
            if width == 1:
                add("tail-adjacent", length, 1, "tail:last-elided", build(length, [(t - 1, seq)]))
                add("tail-adjacent", length, 1, "tail:first-kept", build(length, [(t, seq)]))
                continue
            for ts in range(1, width):                     # ts bytes lie before the tail start
                s = t - ts
                add("tail-straddle", length, width, f"tail:lead={s}:split={ts}", build(length, [(s, seq)]))
    # Family C: head U+0085 straddle (split 1) plus tail 4-octet straddle, when the spans do not overlap.
    for length in range(201, 261):
        t = length - 99
        for ts in (1, 2, 3):
            sh, st = 99, t - ts
            if spans_overlap((sh, CHARS[2]), (st, CHARS[4])):
                continue
            add("both-straddle", length, 2, f"head:lead={sh}:split=1|tail:lead={st}:split={ts}",
                build(length, [(sh, CHARS[2]), (st, CHARS[4])]))

    # Family D: raw-byte preservation and whole-sequence rendering (hand-built).
    cases = [
        ("preserve", 210, b"a" * 111 + b"\x85" + b"b" * 98,
         "lone 0x85 at tail cut (belongs to no lead) -> must print \\x85"),
        ("preserve", 201, b"a" * 99 + b"\x85" + b"b" * 101,
         "lone 0x85 as last head byte (belongs to no lead) -> must print \\x85"),
        ("preserve", 201, b"a" * 99 + b"\xc2" + b"z" * 101,
         "0xC2 at head cut whose next byte is not a continuation -> must print \\xc2"),
        ("preserve", 201, b"a" * 98 + b"\xe2\x82" + b"z" * 101,
         "truncated 3-octet lead at head cut -> must print \\xe2\\x82"),
        ("preserve", 210, b"a" * 111 + b"\xff" + b"b" * 98,
         "0xFF at tail cut -> must print \\xff"),
        ("preserve", 210, b"a" * 108 + b"\xc2\x85\x85\x85" + b"b" * 98,
         "valid C2 85 then orphans at tail cut: head of sequence elided, orphan keeps \\x85"),
        ("whole", 210, b"a" * 111 + b"\xc2\x85" + b"b" * 97,
         "whole C2 85 inside the tail -> \\u0085, no \\x85"),
        ("whole", 201, b"a" * 99 + b"\xc2\x85" + b"b" * 100,
         "C2 85 straddling head cut -> whole sequence elided, neither spelling"),
        ("whole", 202, b"a" * 100 + b"\xc2\x85" + b"b" * 100,
         "C2 85 starting at index 100 -> wholly in the elided middle, neither spelling"),
    ]
    for family, length, raw, note in cases:
        assert len(raw) == length, (len(raw), length)
        add(family, length, 2, "hand", raw, note)

    # Family E (attack, prereg STATED LIMIT (iii)): an INVALID 4-octet lead immediately before the tail cut whose
    # declared length reaches past the continuation run, so `_cut_tail` advances by the declared length rather than
    # to the end of the run and can land INSIDE a later, valid sequence.
    att = [
        ("attack", 210,
         b"a" * 110 + b"\xf0" + b"\x80" + b"a" + b"\xc2\x85" + b"b" * 95,
         "F0 80 before the cut (truncated 4-octet lead); C2 85 follows -> does the tail keep 0x85 alone?"),
        ("attack", 210,
         b"a" * 110 + b"\xf0" + b"\x80" + b"a" + b"b" + b"\x85" + b"b" * 95,
         "collision partner: same cell, but the 0x85 here is a RAW byte (no lead at all)"),
        ("attack", 210,
         b"a" * 110 + b"\xf0" + b"\x80" + b"a" + b"\xe2\x82\xac" + b"b" * 94,
         "F0 80 before the cut; 3-octet EUR follows -> tail cut inside E2 82 AC?"),
        ("attack", 210,
         b"a" * 110 + b"\xf0" + b"\x80" + b"a" + b"\xf0\x9d\x84\x9e" + b"b" * 93,
         "F0 80 before the cut; 4-octet U+1D11E follows -> tail cut inside it?"),
        ("attack", 210,
         b"a" * 110 + b"\xe2" + b"\x80" + b"\xc2\x85" + b"b" * 96,
         "E2 80 before the cut (truncated 3-octet lead); C2 85 follows"),
        ("attack", 210,
         b"a" * 111 + b"\xc2\x85" + b"b" * 97,
         "positive control: the same C2 85 with the cut on its LEAD keeps the whole pair"),
    ]
    for family, length, raw, note in att:
        assert len(raw) == length, (len(raw), length)
        add(family, length, 2, "hand", raw, note)

    # ---- family summaries ---------------------------------------------------
    summary = {}
    for r in rows:
        f = r["family"]
        s = summary.setdefault(f, {"rows": 0, "max_window_octets": 0, "max_cell_utf8_bytes": 0,
                                   "window_over_202": 0, "surrogate_rows": 0, "x85_rows": 0,
                                   "u0085_rows": 0, "recon_mismatch": 0, "head_SPLIT": 0,
                                   "tail_SPLIT": 0, "tail_orphan_beyond": 0})
        s["rows"] += 1
        s["max_window_octets"] = max(s["max_window_octets"], r["window_octets"])
        s["max_cell_utf8_bytes"] = max(s["max_cell_utf8_bytes"], r["cell_utf8_bytes"])
        s["window_over_202"] += r["window_octets"] > 202
        s["surrogate_rows"] += bool(r["surrogate_bytes"])
        s["x85_rows"] += bool(r["x85_spellings"])
        s["u0085_rows"] += bool(r["u0085_spellings"])
        s["recon_mismatch"] += not r["reconstruction_exact"]
        s["head_SPLIT"] += r["head_boundary"] == "SPLIT"
        s["tail_SPLIT"] += r["tail_boundary"] == "SPLIT"
        s["tail_orphan_beyond"] += r["tail_boundary"] == "orphan-beyond"

    # ---- the named before/after payload ------------------------------------
    named = b"p" * 101 + b"\xc2\x85" + b"s" * 98
    assert len(named) == 201
    after = analyse(filed, named)
    bef = analyse(before, named)
    before_cell = before._one_line_bytes(named)

    out = {
        "filed": {"path": FILED, "sha256": sha(FILED)},
        "before": {"path": BEFORE, "sha256": sha(BEFORE)},
        "named_payload": {"sha256": hashlib.sha256(named).hexdigest(), "length": len(named),
                          "after": after, "before": bef, "before_cell": before_cell},
        "summary": summary,
        "rows": rows,
    }
    with open(os.path.join(SEAT, "matrix.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    cols = ["family", "length", "width", "align", "head_cut", "tail_cut", "head_moved", "tail_moved",
            "head_boundary", "tail_boundary", "window_octets", "cell_utf8_bytes", "cell_chars",
            "x85_spellings", "u0085_spellings", "surrogate_bytes", "reconstruction_exact",
            "payload_sha256", "note", "cell"]
    with open(os.path.join(SEAT, "matrix.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]).replace("\t", " ") for c in cols) + "\n")
    # durable reproducer: the hand-built payloads in full (they are what the attack rows rest on)
    with open(os.path.join(SEAT, "hand-payloads.txt"), "w") as f:
        for r in rows:
            if r["family"] in ("preserve", "whole", "attack"):
                f.write(f"{r['family']}\tlen={r['length']}\tsha256={r['payload_sha256']}\n")
                f.write(f"  note={r['note']}\n")
                f.write(f"  payload_hex={r['payload_hex']}\n")
                f.write(f"  h={r['head_cut']} t={r['tail_cut']} head_boundary={r['head_boundary']} "
                        f"tail_boundary={r['tail_boundary']} window_octets={r['window_octets']}\n")
                f.write(f"  cell={r['cell']}\n")

    print(f"TOOL sha256={out['filed']['sha256']}")
    print(f"BEFORE sha256={out['before']['sha256']}")
    print(f"ROWS total={len(rows)}")
    for f, s in sorted(summary.items()):
        print(f"FAMILY {f} rows={s['rows']} max_window_octets={s['max_window_octets']} "
              f"max_cell_utf8_bytes={s['max_cell_utf8_bytes']} window_over_202={s['window_over_202']} "
              f"surrogate_rows={s['surrogate_rows']} x85_rows={s['x85_rows']} u0085_rows={s['u0085_rows']} "
              f"recon_mismatch={s['recon_mismatch']} head_SPLIT={s['head_SPLIT']} tail_SPLIT={s['tail_SPLIT']} "
              f"tail_orphan_beyond={s['tail_orphan_beyond']}")
    print(f"NAMED payload_sha256={out['named_payload']['sha256']} len={len(named)}")
    print(f"AFTER  cell={after['cell']!r}")
    print(f"AFTER  head_cut={after['head_cut']} tail_cut={after['tail_cut']} window_octets={after['window_octets']} "
          f"x85={after['x85_spellings']} u0085={after['u0085_spellings']} surrogates={after['surrogate_bytes']}")
    print(f"BEFORE cell={before_cell!r}")
    print(f"BEFORE head_cut={bef['head_cut']} tail_cut={bef['tail_cut']} window_octets={bef['window_octets']} "
          f"x85={bef['x85_spellings']} u0085={bef['u0085_spellings']} surrogates={bef['surrogate_bytes']}")
    print("PRESERVE/WHOLE cases:")
    for r in rows:
        if r["family"] in ("preserve", "whole"):
            print(f"  {r['family']:<9} len={r['length']} h={r['head_cut']} t={r['tail_cut']} "
                  f"win={r['window_octets']} x85={r['x85_spellings']} u0085={r['u0085_spellings']} "
                  f"cell={r['cell']!r}")
    print("ATTACK cases:")
    for r in rows:
        if r["family"] == "attack":
            print(f"  len={r['length']} h={r['head_cut']} t={r['tail_cut']} "
                  f"head_boundary={r['head_boundary']} tail_boundary={r['tail_boundary']} "
                  f"win={r['window_octets']} x85={r['x85_spellings']} u0085={r['u0085_spellings']} "
                  f"surrogates={r['surrogate_bytes']}")
            print(f"    note={r['note']}")
            print(f"    cell={r['cell']!r}")
    # collision demonstration: the two payloads that differ only inside the elided middle
    atk = [r for r in rows if r["family"] == "attack"]
    if len(atk) >= 2:
        print(f"COLLISION cells_equal={atk[0]['cell'] == atk[1]['cell']} "
              f"A={atk[0]['payload_sha256'][:16]} B={atk[1]['payload_sha256'][:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
