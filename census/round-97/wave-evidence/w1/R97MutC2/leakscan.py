#!/usr/bin/env python3
"""Exact-token /proc scan: print processes (pid, executable, argv) carrying any of the given tokens.
Usage: leakscan.py <token> [<token>...]  (exit 0 always; prints lines, 'none' if clean)"""
import os, sys

def scan(tokens):
    found = []
    for name in sorted(os.listdir("/proc")):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid == os.getpid():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                argv = f.read().split(b"\x00")
        except OSError:
            continue
        hits = [t for t in tokens if t.encode() in argv]
        if hits:
            try:
                exe = os.readlink(f"/proc/{pid}/exe")
            except OSError:
                exe = "?"
            found.append((pid, exe, hits))
    return found

toks = sys.argv[1:]
res = scan(toks)
if not res:
    print("none")
else:
    for pid, exe, hits in res:
        print(f"pid={pid} exe={exe} tokens={hits}")
