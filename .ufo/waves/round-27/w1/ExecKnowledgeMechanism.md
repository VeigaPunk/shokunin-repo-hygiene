## Status
STATUS: PARTIAL — mechanism-entry draft delivered; source snapshots are not present in the lane census, and required assimilation checks remain unrun.

## Evidence
- `cat /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt` — opened frozen C2 contract first; it requires S210/S211, two Gate outcomes, 132→135 source rows and gate/census checks. Revision: `e78ac7c4837b81b634db4a927605a751a7f006ba` (read-only `git rev-parse HEAD`).
- Fetched pinned source bytes on 2026-10-25 with `curl -fsSL` from `https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c` and `.../glib/gfileutils.c`; `sha256sum` returned `66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f` and `5161ae435ee57448c280323de064e1d6d62dc1ba3ba2771c5982b913888dfad5`, respectively. Bytes are in `/var/tmp/souji-r27-ExecKnowledgeMechanism/`.
- Opened source excerpts: `gio/glocalfile.c:2261` “fd = g_open (infofile, O_CREAT | O_EXCL | O_CLOEXEC, 0666);”; `:2281` “(void) g_close (fd, NULL);”; `glib/gfileutils.c:1366-1369` temporary-name construction and `g_mkstemp_full`; `:1691-1697` “flags | O_CREAT | O_EXCL, mode);”; `:1390-1394` rename publication/failure cleanup. Each is a verbatim quote of at most 25 words.
- `glob /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-27/sources/**` — no files found. No snapshot bytes were written to that census path because the seat permits writing only the draft and its own report in `w1/`.
- `grep` on lane `corpus/SOURCES.md` found no S210/S211 entries; no SOURCES registry or knowledge registry changes were made.

## Findings
1. Draft entry delivered at `.ufo/waves/round-27/w1/origin-record-mechanism-set-r33.md`. It describes exclusive reservation, temp content write and rename, states the implementation/specification and receipt-format limits, and includes admit/reject reasons plus located source quotes.
2. The fetched source snapshots currently exist only in the permitted scratch directory. The draft Gate references the expected `census/round-27/sources/{glocalfile.c,gfileutils.c}` paths, which are absent; it is therefore not yet grounded to census files for the gate checker.
3. C2 registration/counters, collision proof, gate check and sources-census validation were not executed. The expected S210/S211 registry rows and knowledge-registry admission are outside this seat's write scope.

## Attack log
None.