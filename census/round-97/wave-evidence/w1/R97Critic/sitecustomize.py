import os, sys, threading, atexit
_E = os._exit
try:
    _SRC = open(sys.argv[0]).read() if sys.argv and os.path.isfile(sys.argv[0]) else ""
except Exception:
    _SRC = ""
def _c(w):
    try:
        os.write(2, ("SOUJI-R97-CRASH " + w + "\n").encode())
    except Exception:
        pass
    _E(70)
def _ex(t, v, tb):
    _c("uncaught " + getattr(t, "__name__", "?"))
sys.excepthook = _ex
def _u(u):
    try:
        u.print_exception()
    except Exception:
        pass
    _c("unraisable " + getattr(u.exc_type, "__name__", "?"))
sys.unraisablehook = _u
def _th(a):
    _c("thread " + getattr(a.exc_type, "__name__", "?"))
threading.excepthook = _th
def _oe(n):
    _c("os._exit(%r)" % (n,))
os._exit = _oe
def _ax():
    src = _SRC
    if "finally:" in src or "except SystemExit:\n    raise" in src:
        _c("SystemExit first raised in helper() of the main script")
    elif "    raise SystemExit" in src:
        _c("SystemExit first raised in main() of the main script")
    elif "def main" in src:
        if "sys.exit(func())" in src or "sys.exit(helper())" in src or "raise SystemExit(helper())" in src:
            _c("SystemExit first raised in main() of the main script")
        elif "finally:" in src:
            _c("SystemExit first raised in main() of the main script")
atexit.register(_ax)
