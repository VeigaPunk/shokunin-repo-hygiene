import os
with open(os.environ['PREMISE_LOG'], 'a') as h:
    h.write('IMPORTED sitecustomize flags_isolated=%s no_site=%s\n' % (__import__('sys').flags.isolated, __import__('sys').flags.no_site))
