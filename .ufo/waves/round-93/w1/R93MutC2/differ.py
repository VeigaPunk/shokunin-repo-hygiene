#!/usr/bin/env python3
"""Behavioural differ: filed tool vs each forgery, on the decoder-equivalence
proof (window-3), the KFF19 sweep payloads, the KFF18 sweep payloads, and
survivor-distinguishing payload shapes. Lane untouched."""
import importlib.util
import itertools
import pathlib
import sys

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
SCR = pathlib.Path("/fast/scratch/hyaku/souji-r93/R93MutC2")
FORG = SCR / "forg"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


filed = load("filed", LANE / "tools/souji-record-agreement.py")
forgeries = {p.stem: load(p.stem, p) for p in sorted(FORG.glob("*.py"))}


def differ(fm, raw):
    return fm._one_line_bytes(raw) != filed._one_line_bytes(raw)


# ── 1. window-3 equivalence proof ──────────────────────────────────────────────
def proof_window3():
    fm = forgeries["a_window3"]
    # Every 4-byte UTF-8 sequence (lead F0..F4, first continuation 90..BF
    # appropriately bounded, later continuations 80..BF) at every start that can
    # straddle either cut of the limit-200 window, filler 'a' and DEL (7F).
    cases = []
    for cut in (100, 114):  # head 100; for a 215-byte payload the tail cut is 215-99=116
        pass
    stops = []
    for L in (215, 230):
        for cut in (100, L - 99):
            for lead, lo, hi in ((0xF0, 0x90, 0xBF), (0xF4, 0x80, 0x8F)):
                for second in (lo, hi, 0x80, 0xBF):
                    for filler in (b"a", b"\x7f"):
                        for start in range(cut - 3, cut):
                            seqbytes = bytes([lead, second, 0x80, 0x80])
                            raw = filler * start + seqbytes + filler * (L - start - 4)
                            if len(raw) != L:
                                continue
                            cases.append((_name(L, cut, start, lead), raw))
    diff = [n for n, raw in cases if differ(fm, raw)]
    # Boundary cut==start+3 exactly: the 4-byte straddle window-3 cannot see.
    boundary = [n for n, raw in cases
                if len(raw) > 200 and differ(fm, raw)]
    n_exact = [n for n, raw in cases if n.startswith("L215-c100") or n.startswith("L215-c116")]
    print(f"window3 proof: 4-byte straddles tested={len(cases)} differs={len(diff)} "
          f"(sample {diff[:3]})")
    return len(diff) == 0


def _name(L, cut, start, lead):
    return f"L{L}-c{cut}-s{start}-F{lead:02X}"


# ── 2. sweep differs (counts only) ─────────────────────────────────────────────
def sweep_counts():
    for nm in ("a_window3", "c_reprokey", "h_filler_a"):
        n19 = bad19 = n18 = bad18 = 0
        # KFF19 exact_payloads reconstruction
        EXACT_TOKENS = (
            b"a", b"\x7f", b"\xc2\x80", b"\xdf\xbf", b"\xe0\xa0\x80", b"\xe0\xbf\xbf", b"\xe1\x80\x80",
            b"\xec\xbf\xbf", b"\xed\x80\x80", b"\xed\x9f\xbf", b"\xee\x80\x80", b"\xef\xbf\xbf",
            b"\xf0\x90\x80\x80", b"\xf0\xbf\xbf\xbf", b"\xf1\x80\x80\x80", b"\xf3\xbf\xbf\xbf",
            b"\xf4\x80\x80\x80", b"\xf4\x8f\xbf\xbf", b"\xc0\x80", b"\xc1\xbf", b"\xe0\x80\x80",
            b"\xe0\x9f\xbf", b"\xed\xa0\x80", b"\xed\xbf\xbf", b"\xf0\x80\x80\x80", b"\xf0\x8f\xbf\xbf",
            b"\xf4\x90\x80\x80", b"\xf5\x80\x80\x80", b"\xff", b"\x80", b"\xbf", b"\xe2\x82",
            b"\xf0\x9d\x84")
        for cut in (100, 131):
            for a, b in itertools.product(EXACT_TOKENS, repeat=2):
                pair = a + b
                for s in range(cut - len(pair), cut + 1):
                    n19 += 1
                    sel = b"a" * s + pair + b"a" * (230 - s - len(pair))
                    if differ(forgeries[nm], sel):
                        bad19 += 1
        print(f"{nm}: KFF19-payload differs={bad19}/{n19}")
    # KFF18 sweep payloads reconstruction (counts only, prefix/suffix check live in fixture)
    TOKENS = (b"a", b"\xc2\x85", b"\xe2\x82\xac", b"\xf0\x9d\x84\x9e", b"\x85", b"\xf0\x80", b"\xe0",
              b"\xc0\xaf", b"\xe0\x80\x80", b"\xed\xa0\x80", b"\xf4\x90\x80\x80", b"\xf5\x80", b"\xc1\xbf",
              b"\xe2\x82", b"\xff")
    for nm in ("a_window3", "c_reprokey"):
        n = bad = 0
        for off in range(96, 118):
            for a, b in itertools.product(TOKENS, repeat=2):
                for total in (205, 210, 214):
                    tail = b"x" * off + a + b
                    for raw in (tail + b"y" * max(0, total - len(tail)),
                                b"x" * (off - 12) + a + b + b"z" * (total - (off - 12) - len(a) - len(b))):
                        n += 1
                        if differ(forgeries[nm], raw):
                            bad += 1
        print(f"{nm}: KFF18-payload differs={bad}/{n}")

    # Tail cut for a 214-byte payload is 214-99 = 115; U+0085 at 114..116 straddles it.
    M = b"fatal: inv " + b"a" * 103 + b"\xc2\x85" + b"b" * 98
    assert len(M) == 214 and M[114:116] == b"\xc2\x85"
    assert differ(forgeries['c_reprokey'], M)
    Q = b"f" + b"q" * 113 + b"\xc2\x85" + b"w" * 98
    assert len(Q) == 214 and b"a" not in Q and differ(forgeries['h_filler_a'], Q)
    QA = b"a" + b"q" * 113 + b"\xc2\x85" + b"w" * 98
    assert not differ(forgeries['h_filler_a'], QA)

# ── 3. survivor distinguishing payloads ───────────────────────────────────────
def detail():
    out = []
    out.append("== c_reprokey: need a valid-sequence tail-straddle + fatal: inv marker ==")
    raw = b"fatal: inv " + b"a" * 91 + b"\xe2\x82\xac" + b"b" * 95  # tail cut at 201
    out.append(f"rawlen={len(raw)} raw_hex={raw[:20].hex()}...")
    out.append(f"differs={differ(forgeries['c_reprokey'], raw)}")
    out.append(f"filed  head={filed._one_line_bytes(raw)[:60]!r} tail={filed._one_line_bytes(raw)[-60:]!r}")
    out.append(f"forg   head={forgeries['c_reprokey']._one_line_bytes(raw)[:60]!r} tail={forgeries['c_reprokey']._one_line_bytes(raw)[-60:]!r}")

    out.append("== h_filler_a: a non-'a'-filler payload with a straddling sequence ==")
    raw2 = b"fatal: inv " + b"x" * 93 + b"\xc2\x85" + b"b" * 95  # tail cut at 201
    out.append(f"rawlen={len(raw2)} raw_hex={raw2[:20].hex()}...")
    out.append(f"differs={differ(forgeries['h_filler_a'], raw2)}")
    out.append(f"filed  head={filed._one_line_bytes(raw2)[:80]!r} tail={filed._one_line_bytes(raw2)[-80:]!r}")
    out.append(f"forg   head={forgeries['h_filler_a']._one_line_bytes(raw2)[:80]!r} tail={forgeries['h_filler_a']._one_line_bytes(raw2)[-80:]!r}")
    # the same payload with 'a' filler -> identical (key condition)
    raw3 = raw2.replace(b"x" * 93, b"a" * 93).replace(b"b" * 95, b"c" * 95)
    out.append(f"with 'a'-filler variant differs={differ(forgeries['h_filler_a'], raw3)}")

    for line in out:
        print(line)
    return out


if __name__ == "__main__":
    ok = proof_window3()
    sweep_counts()
    detail()
    print(f"window3-equivalence={ok}")
    sys.exit(0 if ok else 1)
