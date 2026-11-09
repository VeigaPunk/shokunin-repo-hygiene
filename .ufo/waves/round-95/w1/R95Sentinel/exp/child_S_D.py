import os, sys
pid = os.fork()
if pid == 0:
    os._exit(0)
print("child status:", os.waitpid(pid, 0)[1])
