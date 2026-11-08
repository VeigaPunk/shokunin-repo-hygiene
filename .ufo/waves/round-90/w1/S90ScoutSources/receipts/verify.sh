#!/usr/bin/env bash
# S90ScoutSources — souji r90 scout seat receipts.
# Reproduces every measured fact in .ufo/waves/round-90/w1/S90ScoutSources.md.
# Usage: bash .ufo/waves/round-90/w1/S90ScoutSources/receipts/verify.sh
# Scratch: $S (default /fast/scratch/hyaku/souji-r90/S90ScoutSources). Nothing is written to the lane.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
S=${S:-/fast/scratch/hyaku/souji-r90/S90ScoutSources}
mkdir -p "$S"
cd "$S" || exit 2

echo "===== 1. FETCH TABLE ====="
for u in "https://www.unicode.org/reports/tr14/" \
         "https://www.unicode.org/Public/UCD/latest/ucd/LineBreak.txt" \
         "https://www.unicode.org/reports/tr13/"; do
  out=$(basename "${u%/}")
  curl -sS -L -o "$out" -w "$u http=%{http_code} bytes=%{size_download} effective=%{url_effective}\n" "$u"
done
sha256sum tr14 LineBreak.txt tr13

echo "===== 2. CAPTURE MATCH (cmp against committed lane captures) ====="
cmp tr14       "$LANE/census/round-90/srcs/tr14.html"       && echo "tr14 == census/round-90/srcs/tr14.html"
cmp LineBreak.txt "$LANE/census/round-90/srcs/LineBreak.txt" && echo "LineBreak.txt == census/round-90/srcs/LineBreak.txt"
cmp tr13       "$LANE/census/round-90/srcs/tr13.html"       && echo "tr13 == census/round-90/srcs/tr13.html (UNTRACKED in git)"

echo "===== 3. CAPTURE METADATA (tr14.html) ====="
awk 'NR>=44 && NR<=62' tr14 | sed 's/<[^>]*>//g' | grep -v '^[[:space:]]*$'
grep -n 'Revision 57' tr14
head -2 LineBreak.txt

echo "===== 4. QUOTE: location, word count, occurrence count ====="
python3 - <<'PY'
import re
raw = open('tr14', encoding='utf-8', errors='replace').read()
q = "The NL class acts like BK in all respects (there is a mandatory break after any NEL character)."
t = re.sub(r'<[^>]+>', '', raw).replace('\n\t', ' ')
i = t.find(q)
print("tag-stripped (drop tags, '\\n\\t'->' ') char offset:", i)
print("  byte offset of the quoted sentence 'The NL class ...':",
      len(t[:i].encode('utf-8')))
j = t.find(" NL class acts like BK in all respects (there is a mandatory break after any NEL character).")
print("  byte offset of the same sentence MINUS its first word ('The'), leading space kept:",
      len(t[:j].encode('utf-8')))
print("occurrence count in tag-stripped text:", t.count(q))
print("word count (whitespace split):", len(q.split()))
PY
printf 'The NL class acts like BK in all respects (there is a mandatory break after any NEL character).' | wc -w
grep -n 'The <a class="charclass" href="#NL">NL</a> class acts like' tr14
grep -n 'mandatory break after any NEL character' tr14

echo "===== 5. DATA-FILE LINE FOR 0085 ====="
grep -n '^0085' LineBreak.txt
grep -n '^0080\.\.0084\|^0086\.\.009F' LineBreak.txt

echo "===== 6. REJECT CANDIDATE: UAX #13 ====="
python3 - <<'PY'
import re, html
for f in ('tr13',):
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(f, encoding='utf-8').read())))
    q = ("The material formerly covered by UAX #13: Unicode Newline Guidelines has been "
         "incorporated into the Core Specification of the Unicode Standard, starting with Version 4.0")
    print(f, 'supersession-notice quote count:', t.count(q), 'words:', len(q.split()))
PY
curl -sS -L -o tr13-9.html https://www.unicode.org/reports/tr13/tr13-9.html
sha256sum tr13-9.html
python3 - <<'PY'
import re, html
t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open('tr13-9.html', encoding='utf-8').read())))
for pat in ('NEL is not actually defined in ASCII',
            'on input and in interpretation, treat CR, LF, CRLF, and NEL the same',
            'A readline function should stop at'):
    i = t.find(pat)
    print(f"[{'found' if i>=0 else 'ABSENT'}] {pat!r} @ {i}")
PY

echo "===== 7. SOURCES CENSUS ====="
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji > v.out 2>&1
echo "validate EXIT=$?"
echo "output lines: $(wc -l < v.out)"
echo "E-code lines: $(grep -cE '\bE[0-9]{2}\b' v.out)"
echo "W-code lines: $(grep -cE '\bW[0-9]{2}\b' v.out)"
echo "W04 lines: $(grep -c 'W04' v.out)"
grep -v 'W04' v.out
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji
diff v.out "$LANE/census/round-90/records/sources-census-before.txt" >/dev/null \
  && echo "validate output IDENTICAL to committed pre-freeze receipt census/round-90/records/sources-census-before.txt" \
  || echo "validate output DIFFERS from committed pre-freeze receipt"

echo "===== 8. GIT STATE (read-only) ====="
git -C "$LANE" rev-parse HEAD
git -C "$LANE" ls-files census/round-90/srcs/
git -C "$LANE" status --porcelain corpus/ census/round-90/
