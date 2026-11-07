source: S152 — https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c — GLib tag 2.84.0, `gio/glocalfile.c:2256`, `:2261`, `:2281`, `:2288`, `:2331-2333`, `:2340`, `:2354-2355`, `:2359-2361`, `:2363`, `:2383`, `:2387` — opened 2026-10-25
verified-at: 2026-10-25 — GLib tag 2.84.0; snapshot fetched this round (sha256 66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f, at census/round-27/sources/glocalfile.c)
recheck: 365d — re-fetch `gio/glocalfile.c` at tag 2.84.0; the normative format remains the FreeDesktop trash specification (lane row S022)
ground: F4 — restorable quarantine (who WRITES a per-item origin record, and with what guarantees)

# GLib writes the record, and its writer's guarantees are exactly the ones a receipt needs

## Claim (F4, re-grounded at a pinned tag)

The round-5 ledger asked who writes a per-item origin record. The
writer is **GLib's** local-file trash (`g_local_file_trash()` in
`gio/glocalfile.c`), and the code states its guarantees at the pinned
tag 2.84.0.

1. **The record is created exclusively; an existing record blocks the create.**
   `fd = g_open (infofile, O_CREAT | O_EXCL | O_CLOEXEC, 0666);`
   (`gio/glocalfile.c:2261`). `O_EXCL` makes an existing `.trashinfo`
   a failure (`EEXIST`), and the enclosing loop retries under a new
   unique name: `trashname = get_unique_filename (basename, i++);`
   (`:2256`). A trash operation therefore cannot overwrite a previous
   item's record.
2. **The record's content is fixed, and the path is escaped.**
   `original_name_escaped = g_uri_escape_string (original_name, "/", FALSE);`
   (`:2340`), then `data = g_strdup_printf ("[Trash Info]\nPath=%s\nDeletionDate=%s\n", original_name_escaped, delete_time);`
   (`:2354-2355`). The group is `Trash Info`, the keys are `Path` and
   `DeletionDate`, and `Path` is URI-escaped with `/` left unescaped.
3. **The record is written before the payload moves.** The create is a
   reservation: the descriptor is closed unwritten —
   `(void) g_close (fd, NULL);` (`:2281`) — and the content is put in
   place afterwards by path: `if (!g_file_set_contents_full (infofile, data, -1, G_FILE_SET_CONTENTS_CONSISTENT | G_FILE_SET_CONTENTS_ONLY_EXISTING, 0600, error))`
   (`:2359-2361`). The ordering intent is stated beside the code: "Write the full content of the info file before trashing to make sure someone doesn't read an empty file."
   (`:2331-2333`). Only then does the payload move:
   `if (g_rename (local->filename, trashfile) == -1)` (`:2383`).
4. **Every failure path removes the record it just created.** Three
   `g_unlink (infofile);` sites — after the reservation fails
   (`:2288`), after the content write fails (`:2363`), and after the
   rename fails (`:2387`) — mean a half-made trash entry is not left
   behind: if the payload cannot move, the record is deleted, and if
   the record cannot be written, the payload is not moved.

## What this does NOT establish

- **This is GLib's implementation, not the specification.** The
  normative format remains the FreeDesktop trash specification (lane
  row S022); this row shows how the guarantees are realised in code.
- **The `DeletionDate` format is not quoted here.** The value is
  produced at `gio/glocalfile.c:2348` (`g_date_time_format (now,
  "%Y-%m-%dT%H:%M:%S")`); the quotes above are limited to the writer's
  create/content/ordering/rollback lines.
- **The writer is not a souji tool.** Nothing here says a souji
  receipt must reuse GLib's format — only that a reference
  implementation exists whose ordering and rollback a souji design can
  be measured against.
- **No durability claim is made from this file.** The content write
  uses `CONSISTENT | ONLY_EXISTING`, not `DURABLE`; crash-safety is a
  separate question.

## Amendment note

This entry re-grounds, at the round's own access date, the write side
of the F4 theme: it complements the lane's held specification entry
`corpus/knowledge/trash-spec-restorable-quarantine.md` (S022) and the
staged read-side entry `corpus/knowledge/origin-record-format-gvfs-r26.md`
(S146), and answers the "who writes one" question with a named,
pinned implementation. It replaces none of them.

## Gate

url: https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c
snapshot: census/round-27/sources/glocalfile.c (sha256 66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f)
opened: 2026-10-25

- ADMIT: "fd = g_open (infofile, O_CREAT | O_EXCL | O_CLOEXEC, 0666);" — gio/glocalfile.c:2261 — reason: an existing record makes the create fail rather than overwrite — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "trashname = get_unique_filename (basename, i++);" — gio/glocalfile.c:2256 — reason: a name collision retries under a new unique name — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "original_name_escaped = g_uri_escape_string (original_name, "/", FALSE);" — gio/glocalfile.c:2340 — reason: the record's path field is escaped, with `/` left unescaped — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "data = g_strdup_printf ("[Trash Info]\nPath=%s\nDeletionDate=%s\n", original_name_escaped, delete_time);" — gio/glocalfile.c:2354-2355 — reason: the record's group and keys are fixed — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "Write the full content of the info file before trashing to make sure someone doesn't read an empty file." — gio/glocalfile.c:2331-2333 — reason: the record is completed before the payload moves — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "if (g_rename (local->filename, trashfile) == -1)" — gio/glocalfile.c:2383 — reason: the payload move follows the record write — snapshot: census/round-27/sources/glocalfile.c
- ADMIT: "g_unlink (infofile);" — gio/glocalfile.c:2288, :2363, :2387 — reason: every failure path removes the just-created record — snapshot: census/round-27/sources/glocalfile.c
- REJECT: staged row S119 (git-fetch(1) zh-Hans edition, merged/souji/SOURCES.append.md:17) — reason: re-staged as mined with no sha256-pinned snapshot and no decision-time fetch quote; the routed round-26 lesson (corpus/lessons/round-26-verifier-spotcheck.md:47, round-26.md item 2) requires such a pin on re-adoption, and decision-time mirror state is unrecoverable; the row is corroboration-only ("adds no rule beyond S109"), so its claim surface is already carried by S109 — flip: admissibility requires a pinned snapshot and sha256 with the locate quote recorded at decision time — accessed: 2026-10-25
