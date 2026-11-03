import re, html, sys, hashlib
p = sys.argv[1]
raw = open(p, encoding='utf-8', errors='replace').read()
t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', raw)
t = re.sub(r'<[^>]+>', '', t)
t = html.unescape(t)
t = re.sub(r'\s+', ' ', t)
quotes = [
 ("This method splits on the following line boundaries. In particular, the boundaries are a superset of universal newlines", 18),
 ("Line breaks are not included in the resulting list unless keepends is given and true.", 15),
 (r"\v or \x0b Line Tabulation \f or \x0c Form Feed \x1c File Separator \x1d Group Separator \x1e Record Separator \x85 Next Line (C1 Control Code)", 25),
 (r"Changed in version 3.2: \v and \f added to list of line boundaries", 13),
]
for i,(q,exp) in enumerate(quotes,1):
    sub = q in t
    w = len(q.split())
    print(f"q{i} substring: {sub} words: {w} expected_words: {exp} match: {w==exp}")
    j = t.find(q)
    print(f"   ctx_before: {t[max(0,j-90):j]!r}")
    print(f"   ctx_after : {t[j+len(q):j+len(q)+90]!r}")
print("--- heading ---")
print("'Python 3.12.' present:", 'Python 3.12.' in t)
for m in re.finditer(r'Python 3\.12\.[0-9]+[^ ]* documentation', t):
    print("heading_hit:", repr(m.group(0)))
    break
