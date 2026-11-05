import os, threading, time, tempfile, sys
S = os.environ["S"]
REC = b"x" * 700
FULL = len(REC)

def publish_chunked(out, pause):
    h = FULL // 2
    with open(out, "wb") as f:
        f.write(REC[:h]); f.flush()
        if pause: time.sleep(pause)
        f.write(REC[h:]); f.flush()

def publish_honest(out, _pause):
    d = os.path.dirname(out)
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(out) + ".", suffix=".tmp", dir=d)
    with os.fdopen(fd, "wb") as f:
        f.write(REC); f.flush(); os.fsync(f.fileno())
    os.link(tmp, out); os.unlink(tmp)

def trial(fn, pause, n_trials, polls_pre_sleep=0.0):
    seen_partial = 0; seen_full = 0
    d = tempfile.mkdtemp(dir=S)
    for i in range(n_trials):
        out = os.path.join(d, "OUT.%d" % i)
        stop = threading.Event(); obs = []
        def reader():
            while not stop.is_set():
                try:
                    with open(out, "rb") as f:
                        obs.append(len(f.read()))
                except FileNotFoundError:
                    pass
        t = threading.Thread(target=reader); t.start()
        time.sleep(0.005)
        fn(out, pause)
        time.sleep(0.005)
        stop.set(); t.join()
        if any(0 < s < FULL for s in obs): seen_partial += 1
        if any(s == FULL for s in obs): seen_full += 1
    return seen_partial, seen_full

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
print("N=%d per arm" % N)
print("chunked, no pause      partial-trials=%d/%d full-seen=%d" % (*trial(publish_chunked, 0, N), N))
print("chunked, 50ms pause    partial-trials=%d/%d full-seen=%d" % (*trial(publish_chunked, 0.05, N), N))
print("honest temp+link       partial-trials=%d/%d full-seen=%d" % (*trial(publish_honest, 0, N), N))
