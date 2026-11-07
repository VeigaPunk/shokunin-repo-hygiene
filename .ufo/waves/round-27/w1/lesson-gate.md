## Gate

| Candidate | Decision | Reason / flip condition |
|---|---|---|
| S152 — GLib `g_local_file_trash()` writer (`gio/glocalfile.c`, tag 2.84.0), staged `SOURCES.append.md:50` | ADMIT to `origin-record-writer-r27.md` | Re-grounded pinned writer sequence, distinct from reader-side S146. |
| S210 — GLib trash writer's exclusive-create/content-write/rollback ordering, staged `SOURCES.append.md:108` | ADMIT to `origin-record-mechanism-set-r33.md` | Extends S152 by establishing the exclusively created descriptor is closed rather than used for content. |
| S211 — GLib `g_file_set_contents_full()` temp-file publication mechanism, staged `SOURCES.append.md:109` | ADMIT to `origin-record-mechanism-set-r33.md` | Complementary content-writer mechanism; `O_EXCL` applies to temp creation and rename publishes it. |
| S119 — git-fetch(1) zh-Hans edition, staged `SOURCES.append.md:17` | REJECT | Re-staged without pinned snapshot sha256 or decision-time quote, and duplicates S109. Flip: pin a snapshot with sha256 and record the locate quote at decision time; because the historical mirror state is unrecoverable, do not retroactively admit this instance. |

Admitted rows, re-grounded 2026-10-25:

- S152 — `https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c`, `gio/glocalfile.c:2261`: “fd = g_open (infofile, O_CREAT | O_EXCL | O_CLOEXEC, 0666);” (opened snapshot `census/round-27/sources/glocalfile.c`; SHA256 `66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f`).
- S210 — same GLib URL, `gio/glocalfile.c:2281-2285`: “(void) g_close (fd, NULL);” (same pinned snapshot; demonstrates reservation descriptor closed, then content writer invoked).
- S211 — `https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c`, `glib/gfileutils.c:1696-1697`: “flags | O_CREAT | O_EXCL, mode);” (opened snapshot `census/round-27/sources/gfileutils.c`; see round-27 GLib re-grounding receipt for its sha256).

Rejected rows: S119 as above; no other staged candidates admitted/rejected by this scoped decision.

Spot-check: <non-lane verifier records independent spot-check of S152/S210/S211 source locations and quotes in `round-27-verifier-spotcheck.md`; verifier duty, not completed by this scribe>.
