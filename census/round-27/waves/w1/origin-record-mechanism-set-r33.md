
source: S210 — https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c
source: S211 — https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c
verified-at: 2026-10-25 — GLib tag 2.84.0; snapshots fetched this round (sha256 in census/round-27/sources/)
recheck: 365d
ground: F4 — restorable quarantine (whether a per-item origin record needs O_EXCL uniqueness, rollback, or a different scheme)

# Three complementary mechanisms in GLib's origin-record writer

GLib's local trash implementation separates exclusive name reservation from content writing and payload movement. The three operations serve complementary purposes; this is evidence about one implementation, not a general specification.

## Exclusive create reserves a unique record name

At `gio/glocalfile.c:2261`, the writer opens the candidate info file with `O_CREAT | O_EXCL | O_CLOEXEC`; on `EEXIST` it retries with another generated name (`:2264-2267`). It closes that descriptor immediately (`:2281`), so this exclusive create reserves the destination name rather than writing the final record through that descriptor. The reservation is removed if the subsequent info write fails (`:2287-2288`).

## Temporary-file content write

At `glib/gfileutils.c:1366-1369`, the consistent-write path constructs a `filename.XXXXXX` temporary name and calls `g_mkstemp_full`. That helper passes `O_CREAT | O_EXCL` (`:1691-1697`), giving the temporary file a unique name. `write_to_file` writes the content to the temporary descriptor (`:1382-1385`); this is distinct from the earlier `.trashinfo` reservation.

## Atomic publication by rename

After the temporary content write succeeds, `glib/gfileutils.c:1390-1395` calls `rename_file` for the temporary and destination names, and removes the temporary on failure. `rename_file` invokes `g_rename` (`:1040-1042`). Separately, the payload is moved only after the info content write succeeds (`gio/glocalfile.c:2359-2363`, `:2383-2388`); a payload-rename failure removes the record reservation. The reservation rollback and temp-file cleanup address different failure paths; neither makes the record-and-payload pair atomic as a pair.

**Limits:** this describes GLib's implementation, not a specification; no receipt-format decision follows. In particular, it does not establish that a Souji receipt should use this format or that the record-plus-payload operation is one atomic transaction.

## Gate

opened: 2026-10-25
- ADMIT: staged S210 and S211 as direct implementation evidence for the three-mechanism distinction; reason: this entry cites and re-grounds both pinned GLib files; flip: the snapshots or quoted implementation lines fail recheck.
- REJECT: staged S152 as an additional source row for this entry; reason: S152 is already the companion writer entry's source and is not one of the two sources grounding this mechanism comparison; flip: the re-grounded comparison directly relies on a distinct S152 claim not present in S210/S211.
- ADMIT: the mechanism comparison only; reason: the reservation, temporary write, and rename claims each have located source quotes below; flip: any cited line fails the pinned-source comparison.
- REJECT: treating this implementation as a normative specification or as a receipt-format decision; reason: the source is implementation code and cannot decide Souji's receipt contract; flip: a normative receipt specification explicitly adopts these semantics.

url: https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c
opened: 2026-10-25
- ADMIT: `gio/glocalfile.c:2261` "fd = g_open (infofile, O_CREAT | O_EXCL | O_CLOEXEC, 0666);"; reason: source confirms exclusive reservation; flip: pinned bytes differ; snapshot: census/round-27/sources/glocalfile.c
- ADMIT: `gio/glocalfile.c:2281` "(void) g_close (fd, NULL);"; reason: source confirms reservation descriptor closes before content write; flip: pinned bytes differ; snapshot: census/round-27/sources/glocalfile.c

url: https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c
opened: 2026-10-25
- ADMIT: `glib/gfileutils.c:1366-1369` "tmp_filename = g_strdup_printf (\"%s.XXXXXX\", filename);"; reason: source confirms temporary content path; flip: pinned bytes differ; snapshot: census/round-27/sources/gfileutils.c
- ADMIT: `glib/gfileutils.c:1691-1697` "flags | O_CREAT | O_EXCL, mode);"; reason: source confirms exclusive temporary creation; flip: pinned bytes differ; snapshot: census/round-27/sources/gfileutils.c
- ADMIT: `glib/gfileutils.c:1390-1394` "if (!rename_file (tmp_filename, filename, do_fsync, &rename_error))"; reason: source confirms rename publication path; flip: pinned bytes differ; snapshot: census/round-27/sources/gfileutils.c
