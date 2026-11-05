source: S288 — Python os.replace atomic publication (https://docs.python.org/3/library/os.html#os.replace; admitted, r60: `If successful, the renaming will be an atomic operation (this is a POSIX requirement).` 14 words, and the cross-filesystem failure its scope names). S289 — Python os.replace cross-filesystem inference (REJECTED r60: the page does not license renaming a TMPDIR temp onto another device; this entry states the opposite, that the temp must sit beside the output). Corroborating admitted rows: S213 POSIX rename() (atomic publication; a failed rename leaves the target untouched), S214 POSIX fsync() (durability, and the null-implementation limit that makes atomicity not durability), S212 POSIX open() O_EXCL, S268 renameat2(2) (RENAME_NOREPLACE refuses with EEXIST). S110 rename(2) man-pages 6.19 covers the no-overwrite flag; its scope does NOT cover the plain-replace sentence this entry quotes, so that sentence needs a widened anchor on S110 or its own row. S-PENDING, two facts with no registry row: (1) open(2) O_TRUNC `it will be truncated to length 0` (7 words, page sha256 d665489cadb85624d98fae03a8d8d06209030f32735cff8aeba949ad8491c789; existing open(2) rows S077/S242/S245 are ENXIO-scope only); (2) fsync(2) NOTES `Calling fsync() does not necessarily ensure that the entry in the directory containing the file has also reached disk` (19 words, page sha256 f0a986d21500222ecb69580fc7a910f346c6b1ff1005ca515501fb05bb5d91f5; no man7 fsync(2) row exists, S214 is the POSIX page). Quotes, sizes and hashes: `.ufo/waves/round-60/w1/S60ScribeEntry/source-fetch.txt`. Registry state: S288/S289 are committed at 3b552509 (read via `git show`).
verified-at: 2026-11-04 — pages fetched from this host with curl (HTTP 200; man-pages 6.19 dated 2026-09-09; docs.python.org serving 3.15.2) and quoted from the served bytes; the base recorder below is read from blob fae325df3fadd0aab1390afd226b199785395379 (census/round-57/record-receipt.sh at 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4), not executed
recheck: 90d — re-open https://man7.org/linux/man-pages/man2/rename.2.html and https://docs.python.org/3/library/os.html; re-read census/round-57/record-receipt.sh lines 25-33 and the candidate tools/souji-receipt-write.py write path
ground: F4 — restorable quarantine, file-system semantics (publishing a per-item receipt so that a reader never observes a partial record and a crash never leaves one)

# A receipt is published by temp-file-in-the-destination-directory, fsync, then rename — an in-place `>` redirect truncates the old receipt before the new one exists

## Claim (F4, sourced; file-system semantics and one read of the base recorder)

**What this entry is:** the publication sequence a receipt writer must use, the two failure modes an
in-place redirect has, and the three refusal rules that turn "write a receipt" into "write a receipt or
write nothing". It grounds the round-60 C2 writer (`tools/souji-receipt-write.py`, candidate). It claims
nothing about any host's crash behaviour and runs no crash test.

### 1. The sequence, and why each step is there

1. **Create the temp file in the destination's own directory.** `rename(2)` is atomic within a
   filesystem, and Python's `os.replace` inherits the constraint: "The operation may fail if src and dst
   are on different filesystems" and "the renaming will be an atomic operation (this is a POSIX
   requirement)" (os.replace, docs.python.org 3.15.2, § `os.replace`). A temp file created under
   `TMPDIR` or `/tmp` is frequently on another filesystem; the rename then fails, and a writer that
   "falls back" to copy-then-delete has silently given up atomicity. `TMPDIR` may govern *other* scratch,
   never the receipt's temp sibling.
2. **Write the full receipt to the temp file.** Nothing about the destination name exists yet, so no
   reader can observe a half-written record under the final name.
3. **`fsync` the file, then `os.replace(temp, out)`.** Atomicity of the *name* is not durability of the
   *contents*: POSIX requires the rename action to be atomic and to leave the target untouched on failure
   (S213), while `fsync()` is what makes data survive a crash, and even that is bounded — a null
   implementation is permitted, so fsync is not a guarantee about any particular device (S214). Without
   the file fsync, a crash after the replace can leave a complete-looking name with zero-length or
   partial contents, which is strictly worse than a visibly truncated file because the name now claims
   the record is finished.
4. **On any exception or SIGTERM/SIGINT, remove the temp file and leave the destination absent.** The
   invariant is: the destination either does not exist, or holds a complete receipt.

Rename's replacement semantics are what make step 3 work and what makes a pre-check mandatory: "If
newpath already exists, it will be atomically replaced, so that there is no point at which another
process attempting to access newpath will find it missing" (rename(2), man-pages 6.19, § DESCRIPTION).
The same sentence in the Python wrapper: "If dst exists and is a file, it will be replaced silently if
the user has permission" (os.replace, § `os.replace`). Atomic replacement is not a refusal; it is a
silent overwrite, and it is the reason the writer must check existence *before* the replace.

### 2. Why an in-place `>` redirect is not atomic

The base recorder (`census/round-57/record-receipt.sh`, blob
`fae325df3fadd0aab1390afd226b199785395379`) captures the command's output into a shell variable and then
redirects a brace group into the destination:

```
26: OUTPUT=$("$@" 2>&1); RC=$?
27: {
...
32:   echo "EXIT=$RC"
33: } > "$OUT"
```

A shell redirection opens the target **before** the block runs, with `O_WRONLY|O_CREAT|O_TRUNC`, so:

- **The old receipt is destroyed at open, not at success.** `O_TRUNC` — "If the file already exists and is
  a regular file" and the mode allows writing, "it will be truncated to length 0" (open(2), man-pages
  6.19, § DESCRIPTION, flags) — fires at line 33's open. A writer that then dies mid-block leaves an
  empty or partial file where a valid earlier receipt used to be. There is no error and no window in
  which the old bytes are still readable.
- **A concurrent reader can observe a partial record.** The name exists throughout the block; the file
  grows line by line. Nothing marks it incomplete, and the `EXIT=` line — the only line the freeze
  checker reads — is written last, so the observable states are "no EXIT line" (unreadable) and "complete";
  an in-flight read can still see a receipt with some instrument lines and no exit line and mistake it for
  a malformed record.
- **The capture itself is unbounded.** `OUTPUT=$(...)` buffers the whole command output in memory before
  anything is written (line 26), so a runaway instrument is a memory event, and the eventual write is one
  shell builtin sequence, not a transaction. A byte bound must be enforced *while* capturing, and a
  refusal must happen before the destination is touched.
- **No fsync anywhere.** The base recorder relies on the page cache for both the receipt and the
  directory entry.

The committed C2 control receipt `census/round-60/controls/c2-do-nothing.txt` (added at commit 3b552509,
last line `EXIT=1`; read by this seat, not re-run) scores this recorder `SUMMARY cases=8 pass=4 fail=4
control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, failing cases 1 (clean-write), 2 (overwrite), 5
(bound) and 8 (dirty-tree) and passing 3 (atomic-in-flight), 4 (kill-residue), 6 (rev-short) and 7
(instrument-absent). Case 5's detail is `tool rc=127` — the shell recorder fails the byte-bound case by not
recognising the invocation at all, not by writing too much. **Conflict to be resolved by the L1:** the round's
claim text states the base recorder is 3/8, while the frozen preregistration's C2 kill rule states `pass=4`;
the committed receipt says 4. This seat re-ran neither and asserts neither number.

None of this makes the base recorder wrong about what it records: its `instrument=`, `instrument_sha256=`
and `rev=` lines are the shape the hardened writer keeps, and its own header states the limit that the
digest binds BYTES, not execution (census/round-57 preregistration C2 named limits). It is the
publication step, not the record shape, that this entry replaces.

### 3. The refusal rules, and what each one costs

| rule | trigger | effect | what it does NOT cover |
|---|---|---|---|
| overwrite | destination already exists | exit 2, destination byte-identical, no temp file created | it is a pre-check, not an atomic no-clobber: two writers racing the same destination can both pass the check and the later `os.replace` wins silently. Closing that race needs `RENAME_NOREPLACE` (S110/S268: "returns an error instead of overwriting newpath", needs per-filesystem support), which the specified writer does not use |
| dirty tree | `git status --porcelain` non-empty, unless `--allow-dirty` | exit 2, nothing written | porcelain hides ignored paths unless `--ignored` is passed, so a receipt measured over an ignored-but-modified instrument is not caught; a dirty nested repository or submodule is not a change to this worktree's own index |
| bound | captured output exceeds `--max-bytes` | exit 2, nothing written | the bound is on the instrument's output, not on the receipt's total size; it does not bound the instrument's runtime or memory |
| instrument presence | instrument absent at the given rev, or a symlink there | exit 2, nothing written | it proves the bytes are in the commit, not that they are the bytes the command executed |
| revision form | `--rev` not a full 40-hex id | exit 2, nothing written | a full id is not a guarantee of a commit (the writer must resolve `^{commit}` separately), and a branch or tag would make the receipt non-replayable later |

The receipt keeps the base shape (`instrument=`, `instrument_sha256=`, `rev=`, then the command's output,
then `EXIT=<rc>`) and adds `command=`. The writer's own exit status is the wrapped command's status, and
the receipt is still written when that status is non-zero — a refusal (exit 2) is the only path that
leaves no receipt, which is what makes "no receipt" mean "the measurement did not happen" rather than
"the measurement was red".

## What this does NOT prove

- **No crash test is claimed.** The sequence is the one POSIX/rename and fsync ground; whether a given
  filesystem honours it through power loss is a device property, and S214 records that a null `fsync`
  implementation is permitted. Nothing here was run under `dm-flakey`, a VM kill, or `fsfreeze`.
- **The directory is not fsynced by the specified writer.** Durability of the rename itself needs an
  `fsync` of the containing directory after the replace, and fsync(2) says so directly: "Calling fsync()
  does not necessarily ensure that the entry in the directory containing the file has also reached disk"
  (fsync(2), man-pages 6.19, § NOTES, 19 words; S-PENDING — no registry row covers this sentence, and
  S289 is a rejected os.replace inference, not this fact). The frozen C2 behaviour list
  requires the file fsync only, so a crash between the replace and the directory flush can lose the name.
  This entry states the gap; it does not repair it.
- **The overwrite refusal is not atomic.** As in the table: check-then-replace is a TOCTOU window. The
  primitive that closes it (`RENAME_NOREPLACE`) is grounded in S110/S268 and is not used by the specified
  writer.
- **`instrument_sha256=` still binds bytes, not execution** — the same limit as
  `freeze-record-substance-binding.md`. The writer records what the instrument blob was at `rev`; it does
  not observe which bytes the shell executed, and it does not prove the instrument is the counter the
  claim declares.
- **`EXIT=<rc>` is the writer's observation of a child process**, so it is stronger than a hand-written
  receipt but still not authenticated: any process with write access to the destination directory can
  produce a byte-identical file.
- **Atomicity is per name, not per set.** A round that publishes several receipts has no cross-file
  transaction; a reader can see receipt A from the new run and receipt B from the old one.
- **The base recorder's measured score is not restated here.** The 8-case fixture's counts are round-60
  measurements and live in the round's lesson and receipts (`TODO-C2`), not in this entry.

## Lane link and consequence

F4's staging rule is "quarantine before delete, no copy". The receipt writer is the same discipline
pointed at the audit record: **publish or write nothing**. An audit trail that can be truncated by a
killed writer is not a trail — the previous receipt is the only evidence that the earlier measurement
happened, and `>` destroys it at open. The three refusals are the cheap half of the fix (they cost one
`os.path.lexists`, one `git status --porcelain`, one counter); the atomic publish is the half that makes
the surviving bytes trustworthy.
