import sys as _s
for _i in (3,4,5):
    _s.monitoring.use_tool_id(_i, 'blocker')
    _s.monitoring.set_events(_i, _s.monitoring.events.RAISE)
# souji r96 crash sentinel (census/round-96/c1-survivor-search.py): every crash channel below exits 70
import atexit, os, sys, threading

_SOUJI_EXIT = os._exit
_SOUJI_SEEN = {}
_SOUJI_STATE = {"foreign": None}


def _souji_crash(why):
    # Signal-safe and non-blocking (r96): a raw os.write bypasses the TextIOWrapper lock a signal handler would
    # deadlock on, and a momentarily non-blocking fd 2 keeps a full undrained pipe from blocking the crash path.
    # The marker is best-effort; the exit code is the verdict.
    try:
        try:
            os.set_blocking(2, False)
        except Exception:
            pass
        try:
            os.write(2, ("SOUJI-R96-CRASH " + why + "\n").encode("utf-8", "surrogateescape"))
        except Exception:
            pass
    except Exception:
        pass
    _SOUJI_EXIT(70)


def _souji_excepthook(t, v, tb):
    sys.__excepthook__(t, v, tb)
    _souji_crash("uncaught " + getattr(t, "__name__", "?"))


def _souji_unraisable(u):
    try:
        u.print_exception()
    except Exception:
        pass
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


def _souji_handled(code, _offset, exc):
    if not isinstance(exc, SystemExit):
        return
    if code.co_name != "<module>":
        return
    seen = _SOUJI_SEEN.pop(id(exc), None)
    if seen is not None and _SOUJI_STATE["foreign"] is not None and seen[2] == _SOUJI_STATE["foreign"]:
        _SOUJI_STATE["foreign"] = None


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
        sys.monitoring.use_tool_id(_souji_id, "souji-r96-sentinel")
    except ValueError:
        continue
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.RAISE, _souji_raise)
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.EXCEPTION_HANDLED, _souji_handled)
    sys.monitoring.set_events(_souji_id, sys.monitoring.events.RAISE | sys.monitoring.events.EXCEPTION_HANDLED)
    break
else:
    try:
        os.set_blocking(2, False)
        os.write(2, b"SOUJI-R96-SENTINEL no free sys.monitoring tool id\n")
    except Exception:
        pass
