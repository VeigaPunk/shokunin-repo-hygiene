import re, html, hashlib, sys
p='/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-70/srcs/git-manual.html'
h=open(p,encoding='utf-8',errors='replace').read()
# THE derivation that reproduces BOTH recorded offsets (12133 and 47046):
s=re.sub(r'(?s)<[^>]*>',' ',h); s=html.unescape(s); t=re.sub(r'\s+',' ',s)   # NOTE: <script> content RETAINED
print('text chars',len(t))
g=[m.start() for m in re.finditer('GIT_LITERAL_PATHSPECS',t)]
print('GIT_LITERAL_PATHSPECS char offsets:',g)
print('12133 in set:',12133 in g,' 47046 in set:',47046 in g)
print('dt --literal-pathspecs char offset:',t.find('--literal-pathspecs'))
print('12133 - dt_offset =',12133-t.find('--literal-pathspecs'))
print('context @12133:',repr(t[12133-30:12133+40]))
print('context @47046:',repr(t[47046-30:47046+40]))
