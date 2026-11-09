# souji r97 crash sentinel (census/round-97/c1-survivor-search.py): every crash channel below exits 70
import atexit, os, sys, threading

_SOUJI_EXIT = os._exit
_SOUJI_SEEN = {}
_SOUJI_STATE = {"foreign": None}
_SOUJI_ELIG = {}


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
            os.write(2, ("SOUJI-R97-CRASH " + why + "\n").encode("utf-8", "surrogateescape"))
        except Exception:
            pass
    except Exception:
        pass
    _SOUJI_EXIT(70)


def _souji_excepthook(t, v, tb):
    # r97 (A2): crash FIRST on the raw write, then print — the blocking traceback print cannot hold the exit
    # hostage on a full undrained pipe on either the excepthook or the thread channel.
    _souji_crash("uncaught " + getattr(t, "__name__", "?"))


def _souji_unraisable(u):
    try:
        u.print_exception()
    except Exception:
        pass
    _souji_crash("unraisable " + getattr(u.exc_type, "__name__", "?"))


def _souji_thread(a):
    # r97 (A2): same order as _souji_excepthook above.
    _souji_crash("thread " + getattr(a.exc_type, "__name__", "?"))


def _souji_os_exit(n):
    _souji_crash("os._exit(%r)" % (n,))


def _souji_raise(code, _offset, exc):
    # r97 (A1): LATCH the foreign mark at RAISE-<module> (the unfold point), not at unwind time. The EH leg
    # clears only a latched mark whose exception object is still eligibility-clean (no RERAISE after its first
    # module-level EH). This keeps a terminating module-level finally/explicit-re-raise ERRORed while a
    # caught-at-top-level SystemExit reads declared.
    if not isinstance(exc, SystemExit):
        return
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    seen = _SOUJI_SEEN.get(id(exc))
    if seen is None or seen[0] is not exc:
        seen = _SOUJI_SEEN[id(exc)] = (exc, code.co_filename, code.co_name)
    if main is not None and code.co_filename == main and code.co_name == "<module>":
        _SOUJI_STATE["foreign"] = seen[2] if (seen[1] == main and seen[2] != "<module>") else None
        _SOUJI_STATE["latched"] = True


def _souji_handled(code, _offset, exc):
    # r97 (A1) pending-clear: the module-level EH does NOT clear immediately (EH fires before RERAISE on a
    # finally/explicit-reraise unwind, so an immediate clear would take the terminating mark off in the same
    # ticks that re-list it). It records a pending candidate for THIS exception object; _souji_reraise cancels a
    # pending candidate when the same object re-raises; _souji_atexit flushes a still-pending candidate.
    if not isinstance(exc, SystemExit):
        return
    if code.co_name != "<module>":
        return
    if not _SOUJI_STATE.get("latched"):
        return
    key = id(exc)
    _SOUJI_ELIG.setdefault(key, "pending")
    if _SOUJI_ELIG.get(key) != "pending":
        return
    _SOUJI_STATE["pending_key"] = key





def _souji_reraise(code, _offset, exc):
    # r97 (A1): any RERAISE for a pending candidate spends its eligibility (the finally/explicit-reraise leg).
    if not isinstance(exc, SystemExit):
        return
    key = id(exc)
    if _SOUJI_ELIG.get(key) == "pending":
        _SOUJI_ELIG[key] = "no"
        if _SOUJI_STATE.get("pending_key") == key:
            _SOUJI_STATE["pending_key"] = None


def _souji_atexit():
    # r97 (A1): flush a still-pending module-level EH (a catch that never re-raised) before judging the mark.
    if _SOUJI_STATE.get("pending_key") is not None and _SOUJI_ELIG.get(_SOUJI_STATE["pending_key"]) == "pending":
        seen = _SOUJI_SEEN.pop(_SOUJI_STATE["pending_key"], None)
        if seen is not None and _SOUJI_STATE["foreign"] is not None and seen[2] == _SOUJI_STATE["foreign"]:
            _SOUJI_STATE["foreign"] = None
    if _SOUJI_STATE["foreign"] is not None:
        _souji_crash("SystemExit first raised in " + _SOUJI_STATE["foreign"] + "() of the main script")



atexit.register(_souji_atexit)
sys.excepthook = _souji_excepthook
sys.unraisablehook = _souji_unraisable
threading.excepthook = _souji_thread
os._exit = _souji_os_exit
for _souji_id in range(3, 6):
    try:
        sys.monitoring.use_tool_id(_souji_id, "souji-r97-sentinel")
    except ValueError:
        continue
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.RAISE, _souji_raise)
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.EXCEPTION_HANDLED, _souji_handled)
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.RERAISE, _souji_reraise)
    sys.monitoring.set_events(_souji_id, sys.monitoring.events.RAISE | sys.monitoring.events.EXCEPTION_HANDLED
                              | sys.monitoring.events.RERAISE)
    break
else:
    try:
        os.set_blocking(2, True)  # r97 (A3): restore blocking mode; the r96 fallback left fd 2 non-blocking
        os.write(2, b"SOUJI-R97-SENTINEL no free sys.monitoring tool id\n")
    except Exception:
        pass
