source: S210 — GLib 2.84.0 `gio/glocalfile.c`, `g_local_file_trash()` — https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c
source: S211 — GLib 2.84.0 `glib/gfileutils.c`, file-content writer — https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c
verified-at: 2026-10-25 — fetched snapshots SHA-256 `66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f` and `5161ae435ee57448c280323de064e1d6d62dc1ba3ba2771c5982b913888dfad5`; tag tree blobs verified
recheck: 365d
ground: F4 — restorable quarantine (the distinct roles of reservation, content write, and publication in this reference implementation)

# Three mechanisms in GLib's reference writer

GLib 2.84.0 separates reservation of the trash-info pathname from writing its content, then moves the payload only after that content write. Its general file-content helper separately writes through a temporary file and publishes by rename. These are implementation observations, not a specification; they do not determine Souji's receipt format or establish pairwise atomicity.

## Gate

url: https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c
url: https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c
snapshot: census/round-27/sources/glocalfile.c
snapshot: census/round-27/sources/gfileutils.c
opened: 2026-10-25

- ADMIT: "O_EXCL" — gio/glocalfile.c line 2261 — reason: reservation creation uses an exclusive-open flag — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "(void) g_close (fd, NULL);" — gio/glocalfile.c line 2281 — reason: the reservation descriptor is closed before the later content write — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "if (g_rename (old_name, new_name) == -1)" — glib/gfileutils.c line 1041 — reason: temporary content is published by rename — snapshot: census/round-27/sources/gfileutils.c
- ADMIT: "if (!rename_file (tmp_filename, filename, do_fsync, &rename_error))" — glib/gfileutils.c line 1390 — reason: consistent-write mode uses the rename path — snapshot: census/round-27/sources/gfileutils.c
- REJECT: staged S119 zh-Hans git-fetch page — reason: unrelated to GLib record mechanisms and its decision-time version state lacks a pinned snapshot; flip: only reconsider if a pinned, located edition is relevant to this F4 question.
