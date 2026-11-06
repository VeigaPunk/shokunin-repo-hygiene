#!/usr/bin/env python3
"""A minimal git filter-process v2 implementation (clean direction): maps 'counter v2' -> 'counter v1'."""
import sys

def pk(data: bytes) -> None:
    sys.stdout.buffer.write(b"%04x" % (len(data) + 4) + data)
    sys.stdout.buffer.flush()

def read_pk():
    h = sys.stdin.buffer.read(4)
    if len(h) < 4:
        return None
    n = int(h, 16)
    if n == 0:
        return b""
    return sys.stdin.buffer.read(n - 4)

# handshake: git-filter-client -> git-filter-server, then version, then capabilities
read_pk()                      # "git-filter-client"
pk(b"git-filter-server\n")
ver = read_pk()                # "version=2"
if ver is not None:
    pk(ver)
caps = []
while True:
    line = read_pk()
    if line is None or line == b"":
        break
    caps.append(line)
for c in caps:
    pk(c)
while True:
    cmd = read_pk()
    if cmd is None:
        sys.exit(0)
    if cmd == b"":
        continue
    fields = {}
    while True:
        line = read_pk()
        if line is None:
            sys.exit(0)
        if line == b"":
            break
        k, _, v = line.partition(b"=")
        fields[k] = v
    content = []
    while True:
        line = read_pk()
        if line is None or line == b"":
            break
        content.append(line)
    body = b"".join(content)
    if fields.get(b"command") == b"clean":
        body = body.replace(b"counter v2", b"counter v1")
    pk(b"command=" + (fields.get(b"command") or b"clean") + b"\n")
    pk(b"status=success\n")
    pk(b"")
    for i in range(0, len(body), 60000):
        pk(body[i:i + 60000])
    pk(b"")
    sys.stdout.buffer.flush()
