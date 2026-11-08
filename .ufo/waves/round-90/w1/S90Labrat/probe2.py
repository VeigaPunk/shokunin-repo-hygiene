#!/usr/bin/env python3
"""S90Labrat r90 probe, part 2: domain-complete cross table, KFF9/KFF10 replication, token-composition
collisions, surrogate-as-text identities, splitlines census. Imports the same scratch copies as probe.py.
"""
import hashlib
import importlib.util
import json
import os
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCRATCH = "/fast/scratch/hyaku/souji-r90/S90Labrat"
FILES = {
    "after": os.path.join(SCRATCH, "copy-after.py"),
    "before": os.path.join(SCRATCH, "copy-before.py"),
}


def load(name, path):
    spec = importlib.util.spec_from_file_location("arm2_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    arms = {n: load(n, p) for n, p in FILES.items()}
    print("PY", sys.version.split()[0], "fsenc=%s" % sys.getfilesystemencoding())
    for n, p in FILES.items():
        print("ARM %s copy=%s sha256=%s" % (n, p, hashlib.sha256(open(p, "rb").read()).hexdigest()))

    def esc(mod, raw):
        return mod._escape_text(mod._decode_record(raw))

    # --- A. domain-complete cross table: ALL bytes 0x00..0xFF vs chars U+0080..U+00FF ---
    for name, mod in arms.items():
        pairs = []
        for b in range(0x00, 0x100):
            eb = esc(mod, bytes([b]))
            for c in range(0x80, 0x100):
                if eb == esc(mod, chr(c).encode("utf-8")):
                    pairs.append({"byte": "0x%02x" % b, "char": "U+%04X" % c, "spelling": eb})
        print("CROSS-ALL %s pairs=%d %s" % (name, len(pairs),
              "; ".join("%s/%s=%r" % (p["byte"], p["char"], p["spelling"]) for p in pairs)))

    # --- B. KFF9/KFF10 payloads exactly as the frozen fixture frames them (lines 69-70) ---
    payloads = {"KFF9": b"fatal: nel \xc2\x85 marker\n", "KFF10": b"fatal: nel \x85 marker\n"}
    bs = chr(92)
    for name, mod in arms.items():
        cells = {k: mod._one_line_bytes(v) for k, v in payloads.items()}
        rows = {}
        for k, cell in cells.items():
            rows[k] = {
                "cell": cell,
                "count_u0085": cell.count(bs + "u0085"),
                "count_x85": cell.count(bs + "x85"),
                "physical_lines": len(cell.splitlines()),
                "has_raw_nel": "\x85" in cell,
            }
        pair_ok = cells["KFF9"] != cells["KFF10"] and len(cells["KFF9"].splitlines()) == 1 and len(cells["KFF10"].splitlines()) == 1
        k9 = (rows["KFF9"]["count_u0085"] == 1 and rows["KFF9"]["count_x85"] == 0
              and "fatal: nel" in cells["KFF9"] and "marker" in cells["KFF9"] and not rows["KFF9"]["has_raw_nel"])
        k10 = (rows["KFF10"]["count_x85"] == 1 and rows["KFF10"]["count_u0085"] == 0
               and "fatal: nel" in cells["KFF10"] and "marker" in cells["KFF10"] and not rows["KFF10"]["has_raw_nel"])
        print("KFF %s KFF9=%s KFF10=%s pair_ok=%s" % (name, k9, k10, pair_ok))
        print("   KFF9  cell=%r" % cells["KFF9"])
        print("   KFF10 cell=%r" % cells["KFF10"])

    # --- C. splitlines census over U+0080..U+00FF and over raw bytes 0x80..0xFF ---
    split_chars = ["U+%04X" % c for c in range(0x80, 0x100) if len(chr(c).splitlines()) != 1]
    print("SPLITLINES char_splitters_in_range=%s" % (",".join(split_chars) or "(none)"))
    print("SPLITLINES raw_byte_strings_with_LF_or_split=%s"
          % [("0x%02x" % b) for b in range(0x80, 0x100)
             if b in (0x0A, 0x0D) or len(bytes([b]).splitlines()) != 1])

    # --- D. token composition collisions: any 2-token output equal to a 1-token output or to another 2-token output ---
    for name, mod in arms.items():
        toks = {}       # source -> spelling
        for b in range(0x80, 0x100):
            toks["byte:0x%02x" % b] = esc(mod, bytes([b]))
        for c in range(0x80, 0x100):
            toks["char:U+%04X" % c] = esc(mod, chr(c).encode("utf-8"))
        single = {}
        for src, sp in toks.items():
            single.setdefault(sp, []).append(src)
        comp = {}
        items = list(toks.items())
        for s1, p1 in items:
            for s2, p2 in items:
                comp.setdefault(p1 + p2, []).append(s1 + "+" + s2)
        bad = {k: v for k, v in comp.items() if len(v) > 1}
        cross = {k: (single[k], comp[k]) for k in comp if k in single}
        print("COMPOSE %s pairs=%d two_token_collisions=%d one_vs_two=%d" % (name, len(comp), len(bad), len(cross)))
        for k, v in list(cross.items())[:5]:
            print("   ONE-VS-TWO %r one=%s two=%s" % (k, v[0][:3], v[1][:3]))

    # --- E. surrogate-as-text identities (U+DC80..U+DCFF as str) vs raw bytes 0x80..0xFF, per arm ---
    for name, mod in arms.items():
        ident = []
        for b in range(0x80, 0x100):
            st = chr(0xDC00 + b)
            if mod._escape_text(st) == esc(mod, bytes([b])):
                ident.append("0x%02x" % b)
        print("SURROGATE-TEXT %s identities=%d all_identical=%s first=%s last=%s"
              % (name, len(ident), len(ident) == 128, ident[0] if ident else None, ident[-1] if ident else None))

    # --- F. empty-cell uniqueness: no non-empty swept input escapes to "" ---
    for name, mod in arms.items():
        empty_hits = [s for s in sys.argv if False]  # placeholder for clarity
        hits = []
        for b in range(0x80, 0x100):
            if esc(mod, bytes([b])) == "":
                hits.append("byte:0x%02x" % b)
        for c in range(0x80, 0x100):
            if esc(mod, chr(c).encode("utf-8")) == "":
                hits.append("char:U+%04X" % c)
        print("EMPTY %s nonempty_inputs_escaping_to_empty=%d empty_input_escape=%r one_line_bytes_empty=%r"
              % (name, len(hits), mod._escape_text(mod._decode_record(b"")), mod._one_line_bytes(b"")))


if __name__ == "__main__":
    main()
