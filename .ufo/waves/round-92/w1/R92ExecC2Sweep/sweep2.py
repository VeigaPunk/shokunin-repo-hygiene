#!/usr/bin/env python3
"""R92ExecC2Sweep v2: property-check _one_line_bytes beyond the fixture's finite sweep.

(d) re-derived per the claim's "candidate bytes": a cut moves only across ONE
well-formed UTF-8 sequence straddling the original cut. For a head move
h < head_n, the moved slice raw[h:head_n] is the prefix of a well-formed
sequence raw[h:e] (e > head_n) that strict-decodes to exactly one character.
For a tail move t > t_orig, the moved slice raw[t_orig:t] is the suffix of a
well-formed sequence raw[s:t] (s < t_orig) that strict-decodes to one char.
A non-move is fine (ill-formed bytes keep their raw-byte spelling).
"""
import importlib.util
import json
import random
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
SEAT = LANE / ".ufo/waves/round-92/w1/R92ExecC2Sweep"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

filed = load("filed", LANE / "tools/souji-record-agreement.py")
before = load("before", LANE / "census/round-92/controls/c2-before-tool.py")

SEED = 92092
ASCII = [bytes([b]) for b in range(0x20, 0x7F)]
ASCII += [b"\n", b"\r", b"\t", b"\\", b"\x00", b"\x01", b"\x1f", b"\x7f", b"\x0b", b"\x0c"]
VALID = [
    bytes.fromhex("C282"), bytes.fromhex("C2A0"), bytes.fromhex("C285"),
    bytes.fromhex("DFBF"), bytes.fromhex("E0A080"), bytes.fromhex("E282AC"),
    bytes.fromhex("ED9FBF"), bytes.fromhex("EE8080"), bytes.fromhex("E280A8"),
    bytes.fromhex("F0908080"), bytes.fromhex("F48F8FBF"), bytes.fromhex("F0A08080"),
]
ILL = [
    bytes.fromhex("C0"), bytes.fromhex("C1"), bytes.fromhex("F5"),
    bytes.fromhex("FF"), bytes.fromhex("FE"), bytes.fromhex("80"),
    bytes.fromhex("85"), bytes.fromhex("BF"), bytes.fromhex("E080"),
    bytes.fromhex("E08080"), bytes.fromhex("E09FBF"), bytes.fromhex("EDA080"),
    bytes.fromhex("EDBF80"), bytes.fromhex("F4908080"), bytes.fromhex("F0808080"),
    bytes.fromhex("E2"), bytes.fromhex("F0"), bytes.fromhex("C2"),
    bytes.fromhex("E282"), bytes.fromhex("E280"), bytes.fromhex("A085"),
    bytes.fromhex("A0"), bytes.fromhex("9F"), bytes.fromhex("90"),
    bytes.fromhex("8F"), bytes.fromhex("B0"), b"\xE2\x80", b"\xF0\x90",
    b"\x80\x80", b"\x61\x85",
]
POOL = ASCII * 40 + VALID * 30 + ILL * 20

def gen_payload(rng):
    target = rng.randint(201, 260)
    out = bytearray()
    while len(out) < target:
        tok = rng.choice(POOL)
        remaining = target - len(out)
        out += tok if len(tok) <= remaining else tok[:remaining]
    return bytes(out)

def strict_one(bs):
    try:
        return len(bs.decode("utf-8", "strict")) == 1
    except UnicodeDecodeError:
        return False

def head_move_ok(raw, h, head_n):
    """Moved slice raw[h:head_n] must be the prefix of one well-formed sequence straddling head_n."""
    if h == head_n:
        return True, None
    if h > head_n:
        return False, f"head moved forward h={h} > {head_n}"
    # find e > head_n, e <= h+4 with raw[h:e] strict 1-char
    for e in range(head_n + 1, min(h + 4, len(raw)) + 1):
        if strict_one(raw[h:e]):
            return True, None
    return False, f"head moved {h}->{head_n} moved={raw[h:head_n].hex()} no straddling well-formed seq"

def tail_move_ok(raw, t, t_orig):
    if t == t_orig:
        return True, None
    if t < t_orig:
        return False, f"tail moved back t={t} < {t_orig}"
    for s in range(max(t - 4, 0), t_orig):
        if strict_one(raw[s:t]):
            return True, None
    return False, f"tail moved {t_orig}->{t} moved={raw[t_orig:t].hex()} no straddling well-formed seq"

def check_tool(mod, raw, ces):
    bad = []
    out = mod._one_line_bytes(raw)
    whole = mod._escape_text(mod._decode_record(raw))
    head_n, keep_n = 100, 99
    h = mod._cut_head(raw, head_n)
    t = mod._cut_tail(raw, len(raw) - keep_n)
    if t < h:
        t = h
    window_len = h + 3 + (len(raw) - t) if len(raw) > 200 else len(raw)
    if window_len > 202:
        bad.append("a")
        ces.append(("a", raw.hex(), out, whole, f"window_len={window_len} h={h} t={t}"))
    if len(raw) > 200:
        head_part = mod._escape_text(mod._decode_record(raw[:h]))
        tail_part = mod._escape_text(mod._decode_record(raw[t:]))
        if not whole.startswith(head_part) or not whole.endswith(tail_part):
            bad.append("b")
            ces.append(("b", raw.hex(), out, whole, f"head={head_part!r} tail={tail_part!r} h={h} t={t}"))
        expect = head_part + "\u2026" + tail_part
        if out != expect:
            bad.append("b-text")
            ces.append(("b-text", raw.hex(), out, whole, f"expect={expect!r}"))
    elif out != whole:
        bad.append("b-short")
        ces.append(("b-short", raw.hex(), out, whole, "short mismatch"))
    if "\n" in out or "\r" in out:
        bad.append("c-raw")
        ces.append(("c-raw", raw.hex(), out, whole, "raw NL/CR"))
    parts = out.splitlines()
    lines = out.splitlines()
    if len(lines) != 1:
        bad.append("c-split")
        ces.append(("c-split", raw.hex(), out, whole, f"splitlines={len(lines)} parts={[repr(l) for l in lines]}"))
    ok_h, why_h = head_move_ok(raw, h, head_n)
    if not ok_h:
        bad.append("d-head")
        ces.append(("d-head", raw.hex(), out, whole, why_h))
    ok_t, why_t = tail_move_ok(raw, t, len(raw) - keep_n)
    if not ok_t:
        bad.append("d-tail")
        ces.append(("d-tail", raw.hex(), out, whole, why_t))
    # completeness: any well-formed straddle must be moved (else (b) would fail, belt+braces)
    # (already covered by (b); record misses separately if (b) passes)
    return bad

def main():
    N = 200000
    results = {}
    for label, mod in (("filed", filed), ("before", before)):
        violations = {}
        ces = []
        rng = random.Random(SEED)
        t0 = time.perf_counter()
        for i in range(N):
            raw = gen_payload(rng)
            bad = check_tool(mod, raw, ces)
            for b in bad:
                violations[b] = violations.get(b, 0) + 1
        dt = time.perf_counter() - t0
        results[label] = violations
        print(f"{label}: n={N} elapsed={dt:.2f}s violations={violations} n_counter={len(ces)}")
        outp = SEAT / f"counterexamples-{label}-v2.jsonl"
        with open(outp, "w") as f:
            for prop, hx, o, w, extra in ces[:1000]:
                f.write(json.dumps({"prop": prop, "raw_hex": hx, "out": o, "whole": w, "extra": extra}) + "\n")
        print(f"{label}: wrote {len(ces)} -> {outp}")
        for c in ces[:4]:
            print(f"  {c[0]} len={len(c[1])//2} extra={c[4]}")
    # timing
    print("--- timing ---")
    big = bytes.fromhex("41") * (1024 * 1024)  # 1 MB of 'A'
    # 1 MB mixed: repeat a mixed block
    block = b"A" + bytes.fromhex("E282AC") + bytes.fromhex("C285") + bytes.fromhex("61") + bytes.fromhex("F0908080")
    big_mixed = (block * ((1024 * 1024) // len(block) + 1))[: 1024 * 1024]
    for label, mod in (("filed", filed), ("before", before)):
        for name, payload in (("1MB_ascii", big), ("1MB_mixed", big_mixed)):
            reps = 5
            t0 = time.perf_counter()
            for _ in range(reps):
                mod._one_line_bytes(payload)
            dt = (time.perf_counter() - t0) / reps
            print(f"{label} {name}: {dt*1000:.2f} ms/call")
    # 10,000 payload batch
    rng = random.Random(SEED + 1)
    batch = [gen_payload(rng) for _ in range(10000)]
    for label, mod in (("filed", filed), ("before", before)):
        t0 = time.perf_counter()
        for raw in batch:
            mod._one_line_bytes(raw)
        dt = time.perf_counter() - t0
        print(f"{label} 10k_payloads: {dt:.2f}s total, {dt/10000*1000:.3f} ms/payload")
    print("SUMMARY " + json.dumps(results))

if __name__ == "__main__":
    main()
