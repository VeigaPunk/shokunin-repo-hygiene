#!/usr/bin/env python3
"""S90Labrat r90 probe: exhaustive byte/character spelling map for _escape_text(_decode_record(x)).

Arms: `after` = filed tools/souji-record-agreement.py (r90), `before` = census/round-90/controls/c2-before-tool.py
(the r89 filed bytes). Imports scratch copies; never touches the lane.
"""
import hashlib
import importlib.util
import inspect
import json
import os
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCRATCH = "/fast/scratch/hyaku/souji-r90/S90Labrat"
FILES = {
    "after": os.path.join(LANE, "tools/souji-record-agreement.py"),
    "before": os.path.join(LANE, "census/round-90/controls/c2-before-tool.py"),
}


def load(name, path):
    spec = importlib.util.spec_from_file_location("arm_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    arms = {}
    meta = {}
    for name, path in FILES.items():
        copy = os.path.join(SCRATCH, "copy-" + name + ".py")
        data = open(path, "rb").read()
        with open(copy, "wb") as f:
            f.write(data)
        assert sha256_file(copy) == sha256_file(path)
        mod = load(name, copy)
        src_esc = inspect.getsource(mod._escape_text).encode()
        src_dec = inspect.getsource(mod._decode_record).encode()
        src_one = inspect.getsource(mod._one_line_bytes).encode()
        meta[name] = {
            "file": path,
            "file_sha256": sha256_file(path),
            "escape_text_src_sha256": hashlib.sha256(src_esc).hexdigest(),
            "decode_record_src_sha256": hashlib.sha256(src_dec).hexdigest(),
            "one_line_bytes_src_sha256": hashlib.sha256(src_one).hexdigest(),
            "has_one_line": hasattr(mod, "_one_line"),
        }
        arms[name] = mod

    print("ARMS", json.dumps(meta, indent=2, sort_keys=True))

    results = {}
    for name, mod in arms.items():
        byte_rows = {}
        char_rows = {}
        for b in range(0x80, 0x100):
            raw = bytes([b])
            dec = mod._decode_record(raw)
            esc = mod._escape_text(dec)
            byte_rows[b] = {
                "raw": raw.hex(),
                "decoded": " ".join("U+%04X" % ord(c) for c in dec),
                "spelling": esc,
                "len": len(esc),
            }
        for c in range(0x80, 0x100):
            raw = chr(c).encode("utf-8")
            dec = mod._decode_record(raw)
            esc = mod._escape_text(dec)
            char_rows[c] = {
                "raw": raw.hex(),
                "decoded": " ".join("U+%04X" % ord(x) for x in dec),
                "spelling": esc,
                "len": len(esc),
            }
        # cross-domain pairs: byte b vs character c render identically
        pairs = []
        for b, br in byte_rows.items():
            for c, cr in char_rows.items():
                if br["spelling"] == cr["spelling"]:
                    pairs.append({"byte": "0x%02x" % b, "char": "U+%04X" % c, "spelling": br["spelling"]})
        # intra-arm: any spelling shared by two distinct sources (bytes+chars together)
        groups = {}
        for b, br in byte_rows.items():
            groups.setdefault(br["spelling"], []).append("byte:0x%02x" % b)
        for c, cr in char_rows.items():
            groups.setdefault(cr["spelling"], []).append("char:U+%04X" % c)
        shared = {k: v for k, v in groups.items() if len(v) > 1}
        results[name] = {
            "byte_rows": byte_rows,
            "char_rows": char_rows,
            "cross_pairs": pairs,
            "shared_spellings": shared,
            "distinct_spellings": len(groups),
            "nonprintable_escaped_chars": {("U+%04X" % c): char_rows[c]["spelling"]
                                           for c in char_rows if char_rows[c]["spelling"] != chr(c)},
        }
        print("ARM %s n_bytes=128 n_chars=128 cross_pairs=%d shared_spellings=%d distinct=%d"
              % (name, len(pairs), len(shared), len(groups)))
        for p in pairs:
            print("  PAIR %-6s %-8s -> %r" % (p["byte"], p["char"], p["spelling"]))
        for k, v in shared.items():
            print("  SHARED %r <- %s" % (k, ",".join(v)))

    # delta: per source spelling change between arms
    changed = []
    for b in range(0x80, 0x100):
        a = results["before"]["byte_rows"][b]["spelling"]
        z = results["after"]["byte_rows"][b]["spelling"]
        if a != z:
            changed.append({"source": "byte:0x%02x" % b, "before": a, "after": z})
    for c in range(0x80, 0x100):
        a = results["before"]["char_rows"][c]["spelling"]
        z = results["after"]["char_rows"][c]["spelling"]
        if a != z:
            changed.append({"source": "char:U+%04X" % c, "before": a, "after": z})
    print("DELTA changed_sources=%d" % len(changed))
    for ch in changed:
        print("  CHANGED %-12s before=%r after=%r" % (ch["source"], ch["before"], ch["after"]))

    pairs_before = {tuple(sorted([p["byte"], p["char"]])) for p in results["before"]["cross_pairs"]}
    pairs_after = {tuple(sorted([p["byte"], p["char"]])) for p in results["after"]["cross_pairs"]}
    flipped = sorted(pairs_before - pairs_after)
    new = sorted(pairs_after - pairs_before)
    print("PAIR-DELTA before=%d after=%d flipped_to_distinct=%d new_collisions=%d"
          % (len(pairs_before), len(pairs_after), len(flipped), len(new)))
    for f in flipped:
        print("  FLIPPED %s %s" % f)
    for f in new:
        print("  NEW-COLLISION %s %s" % f)

    # ---- boundary cases ----
    boundary = {}
    for name, mod in arms.items():
        rows = {}
        cases = {
            "utf8_above_07ff_U+0800": chr(0x0800).encode("utf-8"),
            "utf8_above_07ff_U+2028": chr(0x2028).encode("utf-8"),
            "utf8_above_07ff_U+4E2D": chr(0x4E2D).encode("utf-8"),
            "utf8_4byte_U+1F600": chr(0x1F600).encode("utf-8"),
            "lone_continuation_0x85": b"\x85",
            "lone_continuation_0x80": b"\x80",
            "truncated_3byte_e2_80": b"\xe2\x80",
            "empty": b"",
        }
        for cid, raw in cases.items():
            rows[cid] = {
                "raw": raw.hex(),
                "spelling": mod._escape_text(mod._decode_record(raw)),
                "one_line_bytes": mod._one_line_bytes(raw),
            }
        # surrogate ALREADY in the input as text (not produced by surrogateescape)
        rows["surrogate_text_U+DC85"] = {
            "raw": "(str) \\udc85",
            "spelling": mod._escape_text("\udc85"),
            "one_line_bytes": None,
        }
        rows["surrogate_text_U+DC85_x2"] = {
            "raw": "(str) \\udc85\\udc85",
            "spelling": mod._escape_text("\udc85\udc85"),
            "one_line_bytes": None,
        }
        # literal backslash-x spelling (control for the doubling)
        rows["literal_backslash_x85"] = {
            "raw": "5c783835",
            "spelling": mod._escape_text(mod._decode_record(b"\\x85")),
            "one_line_bytes": mod._one_line_bytes(b"\\x85"),
        }
        boundary[name] = rows
    print("BOUNDARY", json.dumps(boundary, indent=2, sort_keys=True))

    # exact compare of boundary spellings across arms
    print("BOUNDARY-DELTA")
    for cid in sorted(boundary["before"]):
        a = boundary["before"][cid]["spelling"]
        z = boundary["after"][cid]["spelling"]
        flag = "SAME" if a == z else "DIFF"
        print("  %-28s %s before=%r after=%r" % (cid, flag, a, z))

    with open(os.path.join(SCRATCH, "probe-results.json"), "w") as f:
        json.dump({"meta": meta, "results": results, "changed": changed,
                   "pairs_before": sorted(pairs_before), "pairs_after": sorted(pairs_after),
                   "flipped": flipped, "new": new, "boundary": boundary}, f, indent=1)
    print("WROTE", os.path.join(SCRATCH, "probe-results.json"))


if __name__ == "__main__":
    main()
