import re, html, hashlib, sys
P='census/round-90/srcs/tr14.html'
raw=open(P,'rb').read()
print('capture bytes=%d sha256=%s' % (len(raw), hashlib.sha256(raw).hexdigest()))
text=raw.decode('utf-8')
stripped=re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', text)
stripped=re.sub(r'<[^>]+>', '', stripped)
stripped=html.unescape(stripped)
Q='The NL class acts like BK in all respects (there is a mandatory break after any NEL character).'
pat=re.compile(r'\s+'.join(re.escape(w) for w in Q.split()))
m=pat.search(stripped)
print('quote_whitespace_tolerant_match:', bool(m))
print('occurrence_count:', len(re.findall(r'\s+'.join(re.escape(w) for w in Q.split()), stripped)))
print('tag_stripped_char_offset:', m.start())
print('tag_stripped_line:', stripped.count('\n',0,m.start())+1)
print('words:', len(Q.split()))
print('contiguous_in_raw_html:', Q in text)
print('class_table_row:', '0085' in stripped and 'NEXT LINE (NEL)' in stripped)
