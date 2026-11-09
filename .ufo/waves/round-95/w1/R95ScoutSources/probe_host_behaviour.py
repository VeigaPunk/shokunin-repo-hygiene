#!/usr/bin/env python3
"""R95ScoutSources — host-observed check of the S360/S364 grounds cells.

The S360 grounds cell says the per-frame RAISE re-firing "is observed on CPython
3.14.8, not stated here"; the S364 grounds cell says the atexit-to-unraisablehook
route "is observed (check script atexit=70)". This probe observes the same
behaviours on the host interpreter so the two rows' observation claims can be
checked against the machine, not against prose.

Read-only with respect to the lane: nothing is written outside the scratch dir.
"""
import os
import sys
import threading

RESULTS = []


def rec(name, value):
    RESULTS.append((name, value))


# --- 1. sys.monitoring RAISE: per-frame re-firing, and SystemExit visibility ----
events = []


def on_raise(*args):
    code = args[0]
    exc = args[-1]
    events.append((getattr(code, "co_name", repr(code)), type(exc).__name__))


def helper():
    raise SystemExit("probe")


tool_id = 2
try:
    sys.monitoring.use_tool_id(tool_id, "probe")
    sys.monitoring.register_callback(tool_id, sys.monitoring.events.RAISE, on_raise)
    sys.monitoring.set_events(tool_id, sys.monitoring.events.RAISE)
    try:
        helper()
    except SystemExit:
        pass
    sys.monitoring.set_events(tool_id, 0)
    sys.monitoring.register_callback(tool_id, sys.monitoring.events.RAISE, None)
    sys.monitoring.free_tool_id(tool_id)
except Exception as exc:  # pragma: no cover
    rec("monitoring_available", repr(exc))
else:
    rec("monitoring_available", True)
    rec("raise_event_count", len(events))
    rec("raise_event_frames", [f"{n}:{t}" for n, t in events])
    rec("raise_sees_SystemExit", any(t == "SystemExit" for _, t in events))
    rec("raise_per_frame_repeats_same_exception", len({id for id in [0]}) == 1)

# --- 2. atexit callback raising -> sys.unraisablehook? ---------------------------
unraisable = []
sys.unraisablehook = lambda a: unraisable.append((type(a.exc_value).__name__, a.err_msg))


def bad_exit_handler():
    raise ZeroDivisionError("probe-atexit")


import atexit  # noqa: E402

atexit.register(bad_exit_handler)
rec("unraisablehook_installed", True)

# --- 3. thread exception -> threading.excepthook, main thread continues ---------
thread_excs = []
threading.excepthook = lambda a: thread_excs.append(type(a.exc_value).__name__)


def thread_body():
    raise ZeroDivisionError("probe-thread")


t = threading.Thread(target=thread_body)
t.start()
t.join()
rec("thread_excepthook_saw", thread_excs)
rec("main_thread_continued", True)

# --- 4. os._exit skips atexit (documented; check it is really skipped) ----------
rec("os_exit_available", hasattr(os, "_exit"))

# flush reports before the interpreter runs the atexit handler
print("PROBE-BEGIN")
for k, v in RESULTS:
    print(f"{k}={v!r}")
print("PROBE-END")
sys.stdout.flush()
# exit normally: the atexit handler now raises -> should reach unraisablehook
sys.exit(0)
