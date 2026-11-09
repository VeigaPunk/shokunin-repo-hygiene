# souji r95 crash sentinel (census/round-95/c1-survivor-search.py): every crash channel below exits 70
import atexit, os, sys, threading

_SOUJI_EXIT = os._exit
_SOUJI_SEEN = {}
_SOUJI_STATE = {"foreign": None}


def _souji_crash(why):
    try:
        sys.stderr.write("SOUJI-R95-CRASH " + why + "\\n")
    except Exception:
        pass
    for s in (sys.stdout, sys.stderr):
        try:
            s.flush()
        except Exception:
            pass
    _SOUJI_EXIT(70)


def _souji_excepthook(t, v, tb):
    sys.__excepthook__(t, v, tb)
    _souji_crash("uncaught " + getattr(t, "__name__", "?"))


def _souji_unraisable(u):
    sys.__unraisablehook__(u)
    _souji_crash("unraisable " + getattr(u.exc_type, "__name__", "?"))


def _souji_thread(a):
    threading.__excepthook__(a)
    _souji_crash("thread " + getattr(a.exc_type, "__name__", "?"))


def _souji_os_exit(n):
    _souji_crash("os._exit(%r)" % (n,))


def _souji_raise(code, _offset, exc):
    if not isinstance(exc, SystemExit):
        return
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    seen = _SOUJI_SEEN.get(id(exc))
    if seen is None or seen[0] is not exc:
        seen = _SOUJI_SEEN[id(exc)] = (exc, code.co_filename, code.co_name)
    if main is not None and code.co_filename == main and code.co_name == "<module>":
        _SOUJI_STATE["foreign"] = seen[2] if (seen[1] == main and seen[2] != "<module>") else None


def _souji_atexit():
    if _SOUJI_STATE["foreign"] is not None:
        _souji_crash("SystemExit first raised in " + _SOUJI_STATE["foreign"] + "() of the main script")


atexit.register(_souji_atexit)
sys.excepthook = _souji_excepthook
sys.unraisablehook = _souji_unraisable
threading.excepthook = _souji_thread
os._exit = _souji_os_exit
for _souji_id in range(3, 6):
    try:
        sys.monitoring.use_tool_id(_souji_id, "souji-r95-sentinel")
    except ValueError:
        continue
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.RAISE, _souji_raise)
    sys.monitoring.set_events(_souji_id, sys.monitoring.events.RAISE)
    break
else:
    sys.stderr.write("SOUJI-R95-SENTINEL no free sys.monitoring tool id\\n")
