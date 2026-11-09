import importlib.util, itertools, random, sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("fx", "tests/fixtures/r93-k4-flagfail.py")
fx = importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)
def codec_straddle(raw, cut):
    # independent oracle: Python strict codec, minimal well-formed sequence crossing cut
    for s in range(cut - 1, max(cut - 4, -1), -1):
        for e in range(cut + 1, min(s + 4, len(raw)) + 1):
            try:
                if len(raw[s:e].decode("utf-8", "strict")) == 1:
                    return (s, e)
            except UnicodeDecodeError:
                pass
    return None
def ref_straddle(raw, cut):
    return fx._ref_straddle(raw, cut)
mism = n = 0
ex = []
# exhaustive lengths 2 and 3 over all bytes, cut inside at every position
for L in (2, 3):
    for tup in itertools.product(range(256), repeat=L):
        raw = bytes(b"a" + bytes(tup) + b"a")
        for cut in range(1, len(raw)):
            n += 1
            a = codec_straddle(raw, cut); b = ref_straddle(raw, cut)
            if a != b:
                mism += 1
                if len(ex) < 5: ex.append((raw, cut, a, b))
# random length-4 sample
random.seed(93)
for _ in range(2_000_000):
    tup = bytes(random.choice((random.randrange(256), 0x80, 0xBF, 0xA0, 0x9F, 0x90, 0x8F, 0xC0, 0xF4, 0xF5)) for _ in range(4))
    raw = b"a" + tup + b"a"
    for cut in range(1, len(raw)):
        n += 1
        a = codec_straddle(raw, cut); b = ref_straddle(raw, cut)
        if a != b:
            mism += 1
            if len(ex) < 5: ex.append((raw, cut, a, b))
print(f"REFCHECK compared={n} mismatches={mism}")
for e in ex: print("EX", e)
