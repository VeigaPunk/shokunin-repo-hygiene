import os, sys, time
sys.stderr.write("fixture pid=%d sid=%d pgid=%d\n" % (os.getpid(), os.getsid(0), os.getpgrp()))
sys.stderr.flush()
while True:
    time.sleep(3600)
