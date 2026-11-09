import re, html, sys, hashlib, json
ROOT = "/home/vgpnk/Projects/shokunin/souji-shokunin"
src = open(f"{ROOT}/census/round-93/srcs/encoding.html", encoding="utf-8").read()
sha = hashlib.sha256(src.encode()).hexdigest()
print("capture sha256", sha)
# locate section 8.1.1 by id
m = re.search(r'<h4[^>]*id="utf-8-decoder"', src)
print("id utf-8-decoder occurrences:", len(re.findall(r'id="utf-8-decoder"', src)))
start = m.start()
# next h4/h3/h2 heading after start
nxt = re.search(r'<h[1-4][^>]*class="[^"]*heading', src[m.end():])
end = m.end() + nxt.start() if nxt else len(src)
sec = src[start:end]
def norm(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()
sec_text = norm(sec)
print("SECTION LEN", len(sec_text))
print(sec_text[:3000])
open("/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-93/w1/R93ScoutSources/s818_section_811.txt","w").write(sec_text+"\n")
full = norm(src)
open("/fast/scratch/hyaku/souji-r93/R93ScoutSources/full.txt","w").write(full)
q = "If byte is 0xE0, then set UTF-8 lower boundary to 0xA0"
print("full-text occurrences of quote prefix:", full.count(q))
# row
lines = open(f"{ROOT}/corpus/SOURCES.md", encoding="utf-8").read().split("\n")
rows = [l for l in lines if l.startswith("| S356 |")]
print("S356 rows:", len(rows))
row = rows[0]
print("row chars", len(row), "pipes", row.count("|"))
# cell split: naive by " | "? use split on '|' and strip edges
cells = row.strip().strip("|").split("|")
print("naive cells:", len(cells))
for i,c in enumerate(cells): print(i, repr(c.strip()[:160]))
open("/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-93/w1/R93ScoutSources/s356_row.txt","w").write(row+"\n")
