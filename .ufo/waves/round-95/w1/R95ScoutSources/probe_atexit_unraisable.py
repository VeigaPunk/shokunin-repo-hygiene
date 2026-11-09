#!/usr/bin/env python3
"""R95ScoutSources — does an exception raised in an atexit handler reach
sys.unraisablehook on the host interpreter (CPython 3.14.8)?

This is the route the S364 grounds cell attributes to observation, not to the
quoted atexit page (the page names no sys.unraisablehook; verified: the word
"unraisable" does not occur in census/round-95/srcs/atexit.txt).

Writes nothing. Prints one line.
"""
import atexit
import sys

seen = []


def hook(unraisable):
    seen.append((type(unraisable.exc_value).__name__, unraisable.err_msg))
    sys.stderr.write("UNRAISABLEHOOK-CALLED exc=%s err=%r\n"
                     % (type(unraisable.exc_value).__name__, unraisable.err_msg))
    sys.stderr.flush()


sys.unraisablehook = hook


def boom():
    raise ZeroDivisionError("atexit-route-probe")


atexit.register(boom)
sys.stdout.write("PRE-EXIT\n")
sys.stdout.flush()
sys.exit(0)
