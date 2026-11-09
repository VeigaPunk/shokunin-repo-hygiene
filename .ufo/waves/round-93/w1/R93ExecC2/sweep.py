import importlib.util, random, sys, tempfile, os
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

L = "/home/vgpnk/Projects/shokunin/souji-shokunin/"
fix = load("fix", L+"tests/fixtures/r93-k4-flagfail.py")
ref_cuts = fix.ref_cuts

def load_from_text(name, text):
    name = "tool_" + name
    fd, p = tempfile.mkstemp(suffix=".py"); os.write(fd, text.encode()); os.close(fd)
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); os.unlink(p)
    return mod

tool_src = open(L+"tools/souji-record-agreement.py").read()
tool = load_from_text("filed", tool_src)

edits = {
 "F5": ('                if len(raw[start:end].decode("utf-8", "strict")) == 1:\n',
        '                if len(raw[start:end].decode("utf-8", "surrogatepass")) == 1:  # F5 forgery\n'),
 "F6": ('                if len(raw[start:end].decode("utf-8", "strict")) == 1:\n',
        '                if len(raw[start:end].decode("utf-8", "strict")) >= 1:  # F6 forgery\n'),
 "F7": ("    seq = _straddling_sequence(raw, h)\n    return seq[0] if seq else h\n",
        "    seq = _straddling_sequence(raw, h)\n    return seq[1] if seq else h  # F7 forgery\n"),
}
forgeries = {}
for fid,(old,new) in edits.items():
    assert tool_src.count(old)==1, (fid, tool_src.count(old))
    forgeries[fid] = load_from_text(fid, tool_src.replace(old,new,1))

ALPHABET = []
ALPHABET += [bytes([i]) for i in range(0x00,0x80)]
ALPHABET += [b"\xc2\x80", b"\xc2\xbf", b"\xdf\x80", b"\xdf\xbf",
             b"\xe0\xa0\x80", b"\xe0\xbf\xbf", b"\xe1\x80\x80", b"\xe1\xbf\xbf", b"\xec\x80\x80", b"\xec\xbf\xbf",
             b"\xed\x80\x80", b"\xed\x9f\xbf", b"\xee\x80\x80", b"\xee\xbf\xbf", b"\xef\x80\x80", b"\xef\xbf\xbf",
             b"\xf0\x90\x80\x80", b"\xf0\xbf\xbf\xbf", b"\xf1\x80\x80\x80", b"\xf1\xbf\xbf\xbf",
             b"\xf3\x80\x80\x80", b"\xf3\xbf\xbf\xbf", b"\xf4\x80\x80\x80", b"\xf4\x8f\xbf\xbf"]
ALPHABET += [b"\xc0\x80", b"\xc0\xbf", b"\xc1\x80", b"\xc1\xbf", b"\xe0\x80\x80", b"\xe0\x9f\xbf",
             b"\xed\xa0\x80", b"\xed\xbf\xbf", b"\xf0\x80\x80\x80", b"\xf0\x8f\xbf\xbf", b"\xf4\x90\x80\x80",
             b"\xf4\xbf\xbf\xbf", b"\xf5\x80\x80\x80", b"\xf5\xbf\xbf\xbf", b"\xf6\x80\x80\x80", b"\xf7\xbf\xbf\xbf",
             b"\xf8\x80\x80\x80\x80", b"\xfb\xbf\xbf\xbf\xbf", b"\xfc\x80\x80\x80\x80\x80", b"\xfd\xbf\xbf\xbf\xbf\xbf",
             b"\xfe", b"\xff", b"\x80", b"\x9f", b"\xa0", b"\xbf"]
ALPHABET += [b"\xe2\x82", b"\xf0\x9d\x84", b"\xf0\x9d", b"\xc2", b"\xe1\x80", b"\xf1\x80\x80", b"\xf4\x8f", b"\xed\x9f", b"\xe0\xa0", b"\xf0\x90"]
rng = random.Random(20261109)
for _ in range(200):
    n = rng.randint(2,6)
    ALPHABET.append(bytes(rng.getrandbits(8) for _ in range(n)))

print(f"alphabet tokens={len(ALPHABET)}", flush=True)

def gen_payload(rng):
    L = rng.randint(201,400)
    parts = []; n=0
    while n < L:
        t = ALPHABET[rng.randrange(len(ALPHABET))]
        parts.append(t); n += len(t)
    return b"".join(parts)[:L]

def expected_cell(mod, raw):
    h,t = ref_cuts(raw)
    return mod._escape_text(mod._decode_record(raw[:h]) + "\u2026" + mod._decode_record(raw[t:]))

N = 300000
dis_filed = []; dis_filed_n = 0; counts = {"F5":0,"F6":0,"F7":0}
for i in range(N):
    raw = gen_payload(rng)
    want = expected_cell(tool, raw)
    if tool._one_line_bytes(raw) != want:
        dis_filed_n += 1
        if len(dis_filed) < 5: dis_filed.append((i, raw.hex()))
    for fid, m in forgeries.items():
        if m._one_line_bytes(raw) != want: counts[fid]+=1
print(f"filed disagreements total={dis_filed_n}")
for row in dis_filed: print(row)
print("forgery disagreement counts:", counts)
