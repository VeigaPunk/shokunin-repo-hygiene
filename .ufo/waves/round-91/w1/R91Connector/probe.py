import importlib.util, sys, hashlib
L='/home/vgpnk/Projects/shokunin/souji-shokunin'
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
tool=load(L+'/tools/souji-record-agreement.py','tool91')
before=load(L+'/census/round-91/controls/c2-before-tool.py','tool90')
print("tool sha256", hashlib.sha256(open(L+'/tools/souji-record-agreement.py','rb').read()).hexdigest())
print("before sha256", hashlib.sha256(open(L+'/census/round-91/controls/c2-before-tool.py','rb').read()).hexdigest())
print("_utf8_seq_need table:", {hex(b):tool._utf8_seq_need(b) for b in (0xC0,0xC1,0xC2,0xDF,0xE0,0xED,0xF0,0xF4,0xF5,0xF7,0xF8,0x80,0x41)})

def mk(seq, at):
    n=201
    body=bytes(range(0x41,0x41+1))  # unused
    pre=b'x'*at
    post=b'y'*(n-at-len(seq))
    return pre+bytes(seq)+post

cases={
 'valid-2 C2 85 head':      (0xC2,0x85),
 'overlong-2 C0 80 head':   (0xC0,0x80),
 'overlong-2 C1 BF head':   (0xC1,0xBF),
 'overlong-3 E0 80 80':     (0xE0,0x80,0x80),
 'surrogate-3 ED A0 80':    (0xED,0xA0,0x80),
 'overlong-4 F0 80 80 80':  (0xF0,0x80,0x80,0x80),
 'outofrange F4 90 80 80':  (0xF4,0x90,0x80,0x80),
}
for name,seq in cases.items():
    at=101-len(seq)          # straddles the head cut h=100
    raw=mk(seq,at)
    h91=tool._cut_head(raw,100); h90=100
    print(f"{name:26s} at={at:3d} cut_head91={h91:3d} moved={h91<100} | r91 head tail-spell={tool._one_line_bytes(raw)[:14]!r} | r90 head tail-spell={before._one_line_bytes(raw)[:14]!r}")

print()
for name,seq in cases.items():
    at=101-len(seq)
    raw=mk(seq,at)
    t91=tool._cut_tail(raw,102)
    print(f"TAIL {name:26s} cut_tail91={t91:3d} moved={t91>102}")
