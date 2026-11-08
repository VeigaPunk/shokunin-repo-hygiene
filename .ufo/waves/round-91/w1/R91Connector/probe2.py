import importlib.util
L='/home/vgpnk/Projects/shokunin/souji-shokunin'
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
tool=load(L+'/tools/souji-record-agreement.py','t91')
before=load(L+'/census/round-91/controls/c2-before-tool.py','t90')
def mk(seq, at, n=201, fill=b'x', post=b'y'):
    return fill*at+bytes(seq)+post*(n-at-len(seq))
def show(name,raw):
    a=tool._one_line_bytes(raw); b=before._one_line_bytes(raw)
    i=a.find('\u2026')
    print(f"--- {name}")
    print(f"    r91 : head={a[:i][-12:]!r} tail={a[i+1:i+13]!r} len={len(a)}")
    j=b.find('\u2026')
    print(f"    r90 : head={b[:j][-12:]!r} tail={b[j+1:j+13]!r}")
cases={
 'VALID 2-octet C2 85 at 99':      (0xC2,0x85),
 'INVALID overlong C0 80 at 99':   (0xC0,0x80),
 'INVALID overlong C1 BF at 99':   (0xC1,0xBF),
 'INVALID overlong-3 E0 80 80':    (0xE0,0x80,0x80),
 'INVALID surrogate ED A0 80':     (0xED,0xA0,0x80),
 'INVALID overlong-4 F0 80 80 80': (0xF0,0x80,0x80,0x80),
 'INVALID >10FFFF F4 90 80 80':    (0xF4,0x90,0x80,0x80),
 'INVALID lead F5 80 80 80':       (0xF5,0x80,0x80,0x80),
}
for n,s in cases.items():
    show(n, mk(s,101-len(s)))
print()
print("=== TAIL-side: pair straddles the tail cut at index 102 (lead 101, cont 102) ===")
for n,s in cases.items():
    raw=mk(s,101)
    t=tool._cut_tail(raw,102); t90=102
    a=tool._one_line_bytes(raw); i=a.find('\u2026')
    print(f"{n:32s} cut_tail91={t:3d} moved={t>102} tail_head_of_window={a[i+1:i+15]!r}")
