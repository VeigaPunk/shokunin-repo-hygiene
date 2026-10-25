source: S152 — GLib 2.84.0 `gio/glocalfile.c`, `g_local_file_trash()` — https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c
verified-at: 2026-10-25 — fetched snapshot SHA-256 `66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f`; tag tree blob `03a793716358234c4e6b2ed02362b0f84e34de04`
recheck: 365d
ground: F4 — restorable quarantine (the reference writer's per-item origin-record sequence)

# GLib's per-item origin-record writer sequence

GLib's `g_local_file_trash()` implementation gives a concrete reference for a per-item origin record. It creates a unique info filename, writes the record before moving the payload, and removes the info file on relevant failures. This describes GLib 2.84.0 only; it does not specify Souji's receipt format or guarantee that the record and payload move form one transaction.

## Gate

url: https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c
snapshot: census/round-27/sources/glocalfile.c
opened: 2026-10-25

- ADMIT: "O_EXCL" — gio/glocalfile.c line 2261 — reason: the info-file name is opened exclusively — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "trashname = get_unique_filename (basename, i++);" — gio/glocalfile.c line 2256 — reason: a collision retries with another generated filename — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "if (g_rename (local->filename, trashfile) == -1)" — gio/glocalfile.c line 2383 — reason: the payload move is a later operation — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "g_unlink (infofile);" — gio/glocalfile.c line 2387 — reason: a failed payload move removes the info file — snapshot: census/round-27/sources/glocalfile.c
- REJECT: staged S119 zh-Hans git-fetch page — reason: decision-time version state is unrecoverable without a pinned snapshot and quote; flip: a decision-time snapshot and sha256 make its version alignment checkable.
