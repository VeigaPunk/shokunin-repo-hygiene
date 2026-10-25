# SwarmScout55 — POSIX.1-2024 anchor recon (souji round 28 w1)

Scoped item: recon of the three POSIX.1-2024 (IEEE Std 1003.1-2024, Issue 8) function
pages for precise citation anchors. Read-only: no lane writes beyond this report.

## Status
STATUS: PASS — all three pages fetched from the live Open Group onlinepubs site; exact
section headings and target sentences extracted with line anchors; no unresolved gaps.

## Evidence
- Command: `read` on
  - https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html (615 lines, full)
  - https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html (345 lines; lines 301-345 = CHANGE HISTORY tail, not needed)
  - https://pubs.opengroup.org/onlinepubs/9799919799/functions/fsync.html (full)
  followed by `grep` on the same URLs for target phrases.
- All three pages carry the header "The Open Group Base Specifications Issue 8 / IEEE Std 1003.1-2024 / Copyright (c) 2001-2024 The IEEE and The Open Group". Revision = live onlinepubs (no local git revision applies; fetched 2026-10-25).
- grep hits (reader-text line numbers, URL line format `<line>|> <text>`):
  - open.html 100: "creation of the file if it does not exist shall be atomic with respect to other threads executing *open*() naming the same" (O_EXCL paragraph spans reader-text lines 99-102)
  - rename.html 42-43: "a directory entry named *new* shall remain visible to other threads throughout the renaming operation and refer either to the file referred to by *new* or *old* before the operation began."
  - rename.html 62: "If the *rename*() function fails for any reason other than [EIO], any file named by *new* shall be unaffected."
  - rename.html 226: "already exists. That specification requires that the action of the function be atomic."
  - fsync.html 72: "system crash or other failure that all data up to the time of the *fsync*() call is recorded on the disk."
  - fsync.html 77: "expected from the system. It is explicitly intended that a null implementation is permitted."

## Findings
1. open.html — section headings present: NAME, SYNOPSIS, DESCRIPTION, RETURN VALUE, ERRORS; informative: EXAMPLES, APPLICATION USAGE, RATIONALE, FUTURE DIRECTIONS, SEE ALSO, CHANGE HISTORY.
   - O_EXCL exact sentence (DESCRIPTION, O_EXCL paragraph, reader-text lines 99-102): "If O_CREAT and O_EXCL are set, open() shall fail if the file exists. The check for the existence of the file and the creation of the file if it does not exist shall be atomic with respect to other threads executing open() naming the same filename in the same directory with O_EXCL and O_CREAT set."
   - 22-word verbatim excerpt: "The check for the existence of the file and the creation of the file if it does not exist shall be atomic"
   - ERRORS [EEXIST]: "O_CREAT and O_EXCL are set, and the named file exists." (line 158 area; grep-verified phrase at 100)
   - RATIONALE (symlink atomicity, paragraph after "In general, the open() function follows the symbolic link..."): "The test for a symbolic link which refers to a nonexisting file must be atomic with the creation of a new file." — no line anchor captured; cite as RATIONALE paragraph.
2. rename.html — section headings present: NAME, SYNOPSIS, DESCRIPTION, RETURN VALUE, ERRORS; informative: EXAMPLES, APPLICATION USAGE, RATIONALE, FUTURE DIRECTIONS, SEE ALSO, CHANGE HISTORY.
   - Failure clause exact sentence (DESCRIPTION, reader-text lines 42-43): "If the old argument names a file that is not a directory and the new argument names a directory, or old names a directory and new names a file that is not a directory, or new names a directory that is not empty, rename() shall fail."
   - Atomicity exact sentence (same paragraph, lines 42-43): "Otherwise, if the directory entry named by new exists, it shall be removed and old renamed to new. In this case, a directory entry named new shall remain visible to other threads throughout the renaming operation and refer either to the file referred to by new or old before the operation began."
   - Post-failure guarantee (line 62): "If the rename() function fails for any reason other than [EIO], any file named by new shall be unaffected." (19-word excerpt: "If the rename() function fails for any reason other than [EIO], any file named by new shall be unaffected." — 19 words, no pipe)
   - RATIONALE atomicity (line 226): "That specification requires that the action of the function be atomic."
3. fsync.html — section headings present: NAME, SYNOPSIS, DESCRIPTION, RETURN VALUE, ERRORS; informative: EXAMPLES, APPLICATION USAGE, RATIONALE, FUTURE DIRECTIONS, SEE ALSO, CHANGE HISTORY (Issue 8 note: Austin Group Defect 672 applied to APPLICATION USAGE).
   - DESCRIPTION exact sentence: "The fsync() function shall request that all data for the open file descriptor named by fildes is to be transferred to the storage device associated with the file described by fildes. The nature of the transfer is implementation-defined. The fsync() function shall not return until the system has completed that action or until an error is detected."
   - RATIONALE "recorded on the disk" (line 72): "The fsync() function is intended to force a physical write of data from the buffer cache, and to assure that after a system crash or other failure that all data up to the time of the fsync() call is recorded on the disk." (15-word excerpt: "all data up to the time of the fsync() call is recorded on the disk")
   - Null-implementation allowance (line 77): "It is explicitly intended that a null implementation is permitted." (10 words)
4. Confidence: high — quotes copied from bytes opened this run via `read`/`grep` on the canonical URLs; line anchors refer to reader-extracted text numbering, not raw HTML byte offsets. No other POSIX documents consulted.

## Attack log
None — recon item only; no predicate/target/counter concerns to report.

Remaining unknowns: none material.
