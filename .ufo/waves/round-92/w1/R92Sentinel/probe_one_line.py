#!/usr/bin/env python3
"""R92Sentinel: adversarial probe of tools/souji-record-agreement.py `_one_line_bytes` (copy in scratch)."""
import importlib.util
import os
import random
import sys
import time

sys.dont_write_bytecode = True
SCR = "/fast/scratch/hyaku/souji-r92/R92Sentinel"
spec = importlib.util.spec_from_file_location("tool_copy", os.path.join(SCR, "src/tools/souji-record-agreement.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
OLB = mod._one_line_bytes

BAD = {"\n", "\r", "\t", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029", "\x7f"}


def one_line_ok(cell):
    return (len(cell.splitlines()) <= 1 and "\n" not in cell and not any(c in BAD for c in cell)
            and not any(ord(c) < 0x20 for c in cell) and not any(0xDC80 <= ord(c) <= 0xDCFF for c in cell))


def expect_prefix_suffix(raw, cell):
    """Independent of the cut helpers: head is a prefix of the whole rendering, tail a suffix."""
    full = mod._escape_text(mod._decode_record(raw))
    if "\u2026" in full:
        return None
    if "\u2026" not in cell:
        return cell == full
    head, tail = cell.split("\u2026", 1)
    return full.startswith(head) and full.endswith(tail)


def run_big(name, raw):
    t0 = time.perf_counter()
    try:
        cell = OLB(raw)
        err = None
    except Exception as e:  # report, do not hide
        cell, err = None, f"{type(e).__name__}: {e}"
    dt = time.perf_counter() - t0
    if cell is None:
        print(f"BIG {name} bytes={len(raw)} EXC={err} t={dt:.3f}s")
        return
    ok1 = one_line_ok(cell)
    head_len = mod._cut_head(raw, 100)
    t = mod._cut_tail(raw, len(raw) - 99)
    print(f"BIG {name} bytes={len(raw)} t={dt:.3f}s cell_chars={len(cell)} cell_utf8={len(cell.encode('utf-8', 'surrogatepass'))} "
          f"one_line={ok1} raw_kept={head_len + (len(raw) - t)} raw_window_le_199={head_len + (len(raw) - t) <= 199} "
          f"ellipsis={cell.count(chr(0x2026))}")
    print(f"    head120={cell[:120]!r}")
    print(f"    tail120={cell[-120:]!r}")


def length_cases():
    fails = 0
    count = 0
    tokens = [b"\xe2\x82\xac", b"\xc2\x85", b"\xe2\x80\xa8", b"\xf0\x9f\x98\x80", b"\xf0\x80\x61", b"\xe0\x80\x80",
              b"\xed\xa0\x80", b"\x80", b"\xc2", b"\xe2\x82", b"\xff", b"\x00", b"\x1b", b"\x09", b"a", b"\\",
              b"\xf4\x8f\xbf\xbf", b"\xf4\x90\x80\x80", b"\xf0\x9d\x84\x9e", b"\xc0\xaf", b"\xf5\x80\x80\x80", b"\xef\xbf\xbf",
              b"\xe0\xa0\x80", b"\xed\x9f\xbf", b"\x85", b"\xa0", b"\xf0\x90\x80", b"\xf0\x90"]
    for n in (200, 201, 202, 203):
        for X in tokens:
            for p in range(max(0, 92), 110):
                if p + len(X) > n:
                    continue
                raw = b"A" * p + X + b"B" * (n - p - len(X))
                count += 1
                if not check(raw):
                    fails += 1
        # deterministic A/B-style and head/tail-straddling payloads
        for raw in (b"x" * (n - 5) + b"\xf0\x80\x61\xc2\x85", b"x" * (n - 6) + b"\xf0\x80\x61\x62\x85",
                    b"\x01" * 25 + b"AttributeError: boom" + b"y" * (n - 45)):
            count += 1
            if not check(raw):
                fails += 1
    print(f"LENGTH-CASES n_cases={count} fails={fails}")


def check(raw):
    cell = OLB(raw)
    ok = one_line_ok(cell)
    ps = expect_prefix_suffix(raw, cell)
    if len(raw) <= 200:
        ps = cell == mod._escape_text(mod._decode_record(raw))
    if not ok or ps is False:
        print(f"  FAIL len={len(raw)} one_line={ok} prefix_suffix={ps} raw={raw[:40]!r}..{raw[-20:]!r} cell={cell[:160]!r}")
        return False
    return True


def fuzz(seed, n_iter, lo, hi):
    rnd = random.Random(seed)
    tokens = [b"\xe2\x82\xac", b"\xc2\x85", b"\xe2\x80\xa8", b"\xf0\x9f\x98\x80", b"\xf0\x80", b"\xf0\x80\x61", b"\xe0\x80\x80",
              b"\xed\xa0\x80", b"\x80", b"\xbf", b"\xc2", b"\xe2\x82", b"\xf0\x9d", b"\xff", b"\x00", b"\x1b", b"\x09",
              b"\x0a", b"\x0d", b"\xf4\x8f\xbf\xbf", b"\xf4\x90\x80\x80", b"\xc0\xaf", b"\xf5\x80", b"\xe0\xa0\x80",
              b"\xed\x9f\xbf", b"\x85", b"\xa0", b"\x90", b"a", b"b", b"\\", b" ", b"Error: x"]
    fails = 0
    for _ in range(n_iter):
        target = rnd.randint(lo, hi)
        buf = bytearray()
        while len(buf) < target:
            buf += rnd.choice(tokens)
        raw = bytes(buf[:target]) if rnd.random() < 0.5 else bytes(buf)
        if not check(raw):
            fails += 1
            if fails > 5:
                break
    print(f"FUZZ seed={seed} iters={n_iter} lens={lo}-{hi} fails={fails}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "len"):
        length_cases()
    if which in ("all", "fuzz"):
        fuzz(92, 30000, 196, 260)
        fuzz(93, 3000, 260, 3000)
    if which in ("all", "big"):
        MB = 1_000_000
        run_big("cont-80x10MB", b"\x80" * (10 * MB))
        run_big("F4-8F-BF-BF x10MB", b"\xf4\x8f\xbf\xbf" * (10 * MB // 4))
        run_big("NUL x10MB", b"\x00" * (10 * MB))
        run_big("surrogate-enc ED-A0-80 x10MB", b"\xed\xa0\x80" * (10 * MB // 3))
        run_big("NEL char C2-85 x10MB", b"\xc2\x85" * (10 * MB // 2))
        run_big("LS E2-80-A8 x10MB", b"\xe2\x80\xa8" * (10 * MB // 3))
        run_big("truncated E2-82 x10MB", b"\xe2\x82" * (10 * MB // 2))
        run_big("ASCII 10MB", b"x" * (10 * MB))
        rnd = random.Random(7)
        run_big("random-bytes 10MB", bytes(rnd.getrandbits(8) for _ in range(0)) or bytes(rnd.randrange(256) for _ in range(10 * MB)))
        run_big("mixed-tokens 10MB", (b"\xe2\x82\xac\xc2\x85\x00\xf0\x80a\xed\xa0\x80" * (10 * MB // 14 + 1))[:10 * MB])
        run_big("payload-201 AttributeError", b"AttributeError: " + b"\x01" * 185)
        run_big("payload-202 NEL straddle", b"f" * 100 + b"\xc2\x85" + b"g" * 100)
