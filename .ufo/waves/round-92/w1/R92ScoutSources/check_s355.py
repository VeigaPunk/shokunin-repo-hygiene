import re, html, itertools, json, sys
ROOT = '/home/vgpnk/Projects/shokunin/souji-shokunin'
raw = open(f'{ROOT}/census/round-92/srcs/unicode-ch3.html', encoding='utf-8').read()
txt = open(f'{ROOT}/census/round-92/srcs/unicode-ch3.txt', encoding='utf-8').read()
def clean(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()
out = {}

# 1. anchor identity: what does id="G7404" wrap, and what does the Table 3-7 caption sit under?
i = raw.find('id="G7404"')
out['G7404_wraps'] = clean(raw[i:i+400])[:120]
c = [m.start() for m in re.finditer(r'Well-Formed UTF-8 Byte Sequences', raw)][-1]
ids = [(m.start(), m.group(1)) for m in re.finditer(r'id="(G\d+)"', raw) if m.start() < c]
out['table37_caption_pos'] = c
out['nearest_id_before_table37'] = ids[-1]
out['G7404_pos'] = i
out['G7404_mentions'] = raw.count('G7404')
out['table37_caption_text'] = clean(raw[c-40:c+80])
# 2. sentence count
n = re.sub(r'\s+', ' ', re.sub(r'<script.*?</script>|<style.*?</style>', '', raw, flags=re.S | re.I))
n = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', n)))
S = 'Ill-formed code unit subsequences do not overlap with minimal well-formed code unit subsequences.'
out['sentence_words'] = len(S.split())
out['sentence_occurrences_normtext'] = n.count(S)
out['sentence_pos_in_D86_paragraph'] = n.find(S) - n.find('D86 Well-formed UTF-8')
# 3. Table 3-7 rows parsed from HTML
t = raw[c:c+12000]
tab = re.search(r'<table.*?</table>', t, flags=re.S).group(0)
rows = []
for r in re.findall(r'<tr.*?</tr>', tab, flags=re.S):
    cells = [clean(x) for x in re.findall(r'<t[dhp][^>]*>(.*?)</t[dhp]>', r, flags=re.S)]
    rows.append(cells)
out['table37_rows'] = rows[1:]
# 4. Decide well-formedness from the TABLE rows and compare to strict Python decoding.
def rng(s):
    lo, hi = s.replace(' ', '').split('..')
    return int(lo, 16), int(hi, 16)
spec = []  # per-position byte ranges for each table row (1..4 bytes)
for r in rows[1:]:
    cp, b1, b2, b3, b4 = r
    cols = [x for x in [b1, b2, b3, b4] if x]
    spec.append([rng(x) if '..' in x else (int(x, 16),)*2 for x in cols])
def table_ok(bs):
    for s in spec:
        if len(s) != len(bs): continue
        if all(lo <= b <= hi for (lo, hi), b in zip(s, bs)):
            return True
    return False
# Exhaustive for 1..3 bytes; for 4 bytes, full lead x byte2 x boundary-sampled byte3/4.
bounds = [0x00, 0x7F, 0x80, 0x8F, 0x90, 0x9F, 0xA0, 0xBF, 0xC0, 0xC1, 0xF4, 0xF5, 0xFF]
mism = []; total = 0
def check(bs):
    global total
    total += 1
    # one candidate sequence is well-formed iff it strictly decodes to exactly one character
    try:
        py = len(bytes(bs).decode('utf-8', 'strict')) == 1
    except UnicodeDecodeError:
        py = False
    tb = table_ok(bs)
    if py != tb: mism.append((bytes(bs).hex(' '), py, tb))
for b1 in range(256):
    check([b1])
for b1 in range(256):
    pass  # single byte: table says 00..7F is well formed alone
for b1, b2 in itertools.product(range(256), repeat=2):
    check([b1, b2])
for b1, b2, b3 in itertools.product(range(256), repeat=3):
    check([b1, b2, b3])
for b1, b2, b3, b4 in itertools.product(range(0xF0, 0x100), range(256), bounds, bounds):
    check([b1, b2, b3, b4])
out['decode_comparison_cases'] = total
out['decode_table_mismatches'] = len(mism)
out['first_mismatches'] = mism[:10]
# 5. Reject sample located quote
q = 'This definition of the maximal subpart is used in describing how far to advance processing when making substitutions'
tn = re.sub(r'\s+', ' ', txt)
out['reject_quote_words'] = len(q.split())
out['reject_quote_occ_txt'] = tn.count(q)
out['reject_quote_pos_txt'] = tn.find(q)
out['reject_quote_occ_html_norm'] = n.count(q)
print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
