#!/usr/bin/env python3
"""S90Labrat r90 probe, part 3: line-splitting census (EOF-aware), valid-chars-containing-0x85, truncation,
prefix-freeness, exact 2-token collision counts."""
import hashlib
import importlib.util
import json
import os
import sys

SCRATCH = "/fast/scratch/hyaku/souji-r90/S90Labrat"
FILES = {"after": os.path.join(SCRATCH, "copy-after.py"),
         "before": os.path.join(SCRATCH, "copy-before.py")}


def load(name, path):
    spec = importlib.util.spec_from_file_location("arm3_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    arms = {n: load(n, p) for n, p in FILES.items()}

    def esc(mod, raw):
        return mod._escape_text(mod._decode_record(raw))

    # --- 1. EOF-AWARE line-splitting census: does an EMBEDDED character tear a line? ---
    splits = []
    for cp in range(0x0000, 0x110000):
        if 0xD800 <= cp <= 0xDFFF:
            continue
        if len(("a" + chr(cp) + "b").splitlines()) != 1:
            splits.append(cp)
    print("SPLITLINES-V2 embedded_splitters=%d %s" % (len(splits), " ".join("U+%04X" % c for c in splits)))
    in_range = [c for c in splits if 0x80 <= c <= 0xFF]
    print("SPLITLINES-V2 in_U+0080..U+00FF=%s" % (" ".join("U+%04X" % c for c in in_range) or "(none)"))
    # The single-char form is not a boundary signal (a trailing break yields one element).
    for c in (0x0A, 0x0B, 0x85, 0x2028):
        print("SINGLE U+%04X splitlines=%r" % (c, chr(c).splitlines()))

    # --- 2. valid UTF-8 chars whose encoding CONTAINS byte 0x85: decoded first, so no surrogate forms ---
    contain = []
    for cp in range(0x80, 0x10000):
        if 0xD800 <= cp <= 0xDFFF:
            continue
        try:
            raw = chr(cp).encode("utf-8")
        except UnicodeEncodeError:
            continue
        if b"\x85" in raw:
            contain.append((cp, raw))
    print("CHARS-CONTAINING-0x85 count=%d" % len(contain))
    for name, mod in arms.items():
        bad = []
        for cp, raw in contain:
            sp = esc(mod, raw)
            if sp != chr(cp):
                bad.append((cp, raw.hex(), sp))
        print("  ARM %s passthrough_all=%s deviations=%s" % (name, not bad, bad[:5]))

    # truncated prefixes of those encodings: each surviving byte must escape separately
    trunc_report = {}
    for cp, raw in contain:
        for cut in range(1, len(raw)):
            pre = raw[:cut]
            trunc_report[pre.hex()] = esc(arms["after"], pre)
    print("TRUNCATED 0x85-bearing prefixes=%d all_per_byte_escaped=%s"
          % (len(trunc_report), all(v.count("\\x") == len(bytes.fromhex(k)) for k, v in trunc_report.items())))
    for k in sorted(trunc_report)[:6]:
        print("   prefix=%s -> %r" % (k, trunc_report[k]))

    # --- 3. prefix-freeness + exact collision counts on the 256-token set ---
    for name, mod in arms.items():
        toks = {}
        for b in range(0x80, 0x100):
            toks["byte:0x%02x" % b] = esc(mod, bytes([b]))
        for c in range(0x80, 0x100):
            toks["char:U+%04X" % c] = esc(mod, chr(c).encode("utf-8"))
        spellings = list(toks.values())
        not_prefix_free = [(a, b) for a in spellings for b in spellings if a != b and b.startswith(a)]
        groups1 = {}
        for s, sp in toks.items():
            groups1.setdefault(sp, set()).add(s)
        comp = {}
        items = list(toks.items())
        for s1, p1 in items:
            for s2, p2 in items:
                comp.setdefault(p1 + p2, set()).add(s1 + "+" + s2)
        groups2 = {k: v for k, v in comp.items() if len(v) > 1}
        pairs2 = sum(len(v) * (len(v) - 1) // 2 for v in groups2.values())
        print("TOKENS %s n=256 distinct_len1=%d distinct_len2=%d prefix_violations=%d len2_colliding_outputs=%d len2_colliding_pairs=%d"
              % (name, len(groups1), len(comp), len(not_prefix_free), len(groups2), pairs2))
        for k, v in list(groups2.items())[:3]:
            print("   LEN2 %r <- %s" % (k, sorted(v)[:6]))

    # --- 4. the four boundary cases with the seat's exact framing, both arms, machine-readable ---
    boundary = {}
    for name, mod in arms.items():
        boundary[name] = {
            "utf8_above_07ff": {
                "U+0800": esc(mod, chr(0x0800).encode("utf-8")),
                "U+0105": esc(mod, chr(0x0105).encode("utf-8")),
                "U+4E2D": esc(mod, chr(0x4E2D).encode("utf-8")),
                "U+2028": esc(mod, chr(0x2028).encode("utf-8")),
                "U+1F600": esc(mod, chr(0x1F600).encode("utf-8")),
            },
            "lone_continuation": {
                "0x80": esc(mod, b"\x80"),
                "0x85": esc(mod, b"\x85"),
                "0xbf": esc(mod, b"\xbf"),
                "truncated_c2": esc(mod, b"\xc2"),
                "c2_then_ascii": esc(mod, b"\xc2A"),
            },
            "surrogate_text": {
                "U+DC85": mod._escape_text(chr(0xDC85)),
                "U+DC80": mod._escape_text(chr(0xDC80)),
                "U+DCFF": mod._escape_text(chr(0xDCFF)),
                "U+DC85 x2": mod._escape_text(chr(0xDC85) * 2),
                "raw 0x85 via pipeline": esc(mod, b"\x85"),
            },
            "empty_cell": {
                "escape(decode(b''))": mod._escape_text(mod._decode_record(b"")),
                "one_line_bytes(b'')": mod._one_line_bytes(b""),
            },
        }
    print("BOUNDARY-V2 " + json.dumps(boundary, indent=1, sort_keys=True))

    with open(os.path.join(SCRATCH, "probe3-results.json"), "w") as f:
        json.dump({"splitters": ["U+%04X" % c for c in splits],
                   "contain_0x85": [[cp, raw.hex()] for cp, raw in contain],
                   "truncated": trunc_report, "boundary": boundary}, f, indent=1)
    print("WROTE", os.path.join(SCRATCH, "probe3-results.json"))


if __name__ == "__main__":
    main()
