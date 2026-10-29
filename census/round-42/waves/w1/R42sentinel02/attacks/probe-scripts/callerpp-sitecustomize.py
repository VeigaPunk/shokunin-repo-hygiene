import os, sys
with open('/fast/scratch/hyaku/souji-r42/R42sentinel02/callerpp/log.txt', 'a') as h:
    h.write('IMPORTED pid=%d argv0=%s PYTHONPATH-env=%s\n' % (os.getpid(), sys.argv[0], os.environ.get('PYTHONPATH')))
