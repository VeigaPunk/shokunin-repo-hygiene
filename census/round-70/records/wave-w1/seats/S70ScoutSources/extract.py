import re, html, sys, hashlib

def raw_tagstrip(s):
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?s)<!--.*?-->', ' ', s)
    s = re.sub(r'(?s)<[^>]*>', '', s)
    s = html.unescape(s)
    return s

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out=[]; self.skip=0
    def handle_starttag(self,t,a):
        if t in ('script','style'): self.skip+=1
    def handle_endtag(self,t):
        if t in ('script','style') and self.skip: self.skip-=1
    def handle_data(self,d):
        if not self.skip: self.out.append(d)

def htmlparser_text(s):
    p=P(); p.feed(s); return ''.join(p.out)

for path in ('git-manual.html','gitglossary.html'):
    b = open('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-70/srcs/'+path,'rb').read()
    s = b.decode('utf-8','replace')
    variants = {}
    variants['regex_norm'] = norm(raw_tagstrip(s))
    variants['parser_norm'] = norm(htmlparser_text(s))
    for name,t in variants.items():
        print('==',path,name,'len',len(t))
        for q in ['Treat pathspecs literally','GIT_LITERAL_PATHSPECS environment variable to 1',
                  'will cause Git to treat all pathspecs literally, rather than as glob patterns']:
            i=t.find(q)
            if i>=0: print('   found', repr(q[:40]), 'offset', i)
