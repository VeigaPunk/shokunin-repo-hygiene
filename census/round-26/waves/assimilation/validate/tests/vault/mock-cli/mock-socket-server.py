#!/usr/bin/env python3
"""mock obsidian CLI socket server — seat S53 (vadv-53) adversarial probe.

The official Obsidian CLI is a *client of the running app* over a unix socket
at $XDG_RUNTIME_DIR/.obsidian-cli.sock (read out of obsidian.asar by seat S06).
This server fakes the *server* side so the harness can force the degraded
transports a `--cli` code path must survive:

  noreply   accept the connection, read the request, never write a reply
  garbage   reply with unparseable bytes
  close     accept then close immediately (no reply)
  eof       accept, read the request, send a bare newline
  honest    reply with the real sha256 of $MOCK_VAULT_FILE as JSON + text

Env: MOCK_SOCK_DIR (default /tmp), MOCK_MODE, MOCK_VAULT_FILE, MOCK_LOG
It only ever listens on a path inside MOCK_SOCK_DIR; it never touches the
real vault and never launches the desktop app.
"""
import hashlib
import json
import os
import socket
import sys
import time

sock_dir = os.environ.get("MOCK_SOCK_DIR", "/tmp")
mode = os.environ.get("MOCK_MODE", "noreply")
vault_file = os.environ.get("MOCK_VAULT_FILE", "")
log_path = os.environ.get("MOCK_LOG", "")
path = os.path.join(sock_dir, ".obsidian-cli.sock")

try:
    os.unlink(path)
except OSError:
    pass

srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
srv.bind(path)
srv.listen(8)
# Announce readiness so the harness never races the bind.
ready = path + ".ready"
with open(ready, "w") as fh:
    fh.write(str(os.getpid()))

deadline = time.time() + float(os.environ.get("MOCK_LIFETIME", "120"))

def log(line):
    if not log_path:
        return
    with open(log_path, "a") as fh:
        fh.write("%.6f\t%s\t%s\n" % (time.time(), mode, line))

while time.time() < deadline:
    srv.settimeout(max(1.0, deadline - time.time()))
    try:
        conn, _ = srv.accept()
    except socket.timeout:
        break
    except OSError:
        break
    try:
        conn.settimeout(5.0)
        try:
            req = conn.recv(65536)
        except socket.timeout:
            req = b""
        log("request=%r" % (req[:200],))
        if mode == "noreply":
            # Hold the connection open without answering: a client with no
            # own timeout blocks here forever.
            time.sleep(60)
        elif mode == "garbage":
            conn.sendall(b"\x00\x01not-json-not-a-hash\n")
        elif mode == "close":
            pass
        elif mode == "eof":
            conn.sendall(b"\n")
        elif mode == "honest":
            digest = ""
            size = 0
            if vault_file and os.path.isfile(vault_file):
                h = hashlib.sha256()
                with open(vault_file, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
                digest = h.hexdigest()
                size = os.path.getsize(vault_file)
            conn.sendall((json.dumps({"ok": True, "path": vault_file,
                                      "sha256": digest, "size": size}) + "\n").encode())
        else:
            conn.sendall(b"unknown-mode\n")
    finally:
        try:
            conn.close()
        except OSError:
            pass

try:
    srv.close()
except OSError:
    pass
try:
    os.unlink(path)
    os.unlink(ready)
except OSError:
    pass
sys.exit(0)
