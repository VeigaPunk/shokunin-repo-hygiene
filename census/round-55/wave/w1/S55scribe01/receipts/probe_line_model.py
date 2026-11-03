# Probe: the language-semantics fact the S278 Gate block rests on.
# Reads the FROZEN counter bytes (read-only) and shows which line breaker each
# version's hidden-line set uses, plus the raw splitlines() vs LF-only divergence.
import re, hashlib, pathlib

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

v3 = LANE/'census/round-54/c1-counter.py'
v4 = LANE/'census/round-55/c1-counter.py'
print("v3 bytes sha256:", sha(v3))
print("v4 bytes sha256:", sha(v4))

for label, p in (("v3", v3), ("v4", v4)):
    src = p.read_text(encoding='utf-8')
    m = re.search(r'def hidden_lines\(text: str\):(.*?)\n\ndef ', src, re.S)
    body = m.group(1)
    nums = re.findall(r"enumerate\(([^,]+), 1\)", body)
    print(f"{label} hidden_lines() numbering expression:", nums)

# the divergence itself
text = "A\x0cB\x0c~~~fence\ncorrection\n"
print("\nfixture text repr:", repr(text))
print("splitlines() ->", len(text.splitlines()), "lines:", text.splitlines())
print("split('\\n') ->", len(text.split('\n')), "lines:", text.split('\n'))
print("diverges:", len(text.splitlines()) != len(text.split('\n')))
