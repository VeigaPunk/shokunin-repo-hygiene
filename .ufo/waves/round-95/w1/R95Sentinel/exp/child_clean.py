import os, sys
sys.stdout.write('PARENT-BUFFERED-TEXT')
pid = os.fork()
if pid == 0:
    os._exit(0)
os.waitpid(pid, 0)
sys.stdout.write('|PARENT-AFTER')
sys.stdout.flush()
