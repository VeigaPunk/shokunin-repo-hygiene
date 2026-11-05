# Round 60 — freeze-record substance binding (C1) and atomic receipt writing (C2)

Two claims. C1 calibration/capability: an opt-in `--substance` arm on
`tools/souji-freeze-check.py` binds each claim's `Control:` receipt to the declared Counter bytes and to a
revision strictly before the freeze, measured on a frozen 8-case matrix (3 honest accept, 5 forgery refuse)
against the base tool bytes at 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4. C2 operability: a hardened receipt
writer `tools/souji-receipt-write.py` (atomic temp+rename, refuse overwrite, refuse dirty tree, bounded
output, rev/instrument checks) measured by an 8-case fixture, base recorder
`census/round-57/record-receipt.sh` = 3/8 (the claim text's figure — the committed control receipt prints
`pass=4`; the disagreement is a `## Mistakes` row, and this skeleton asserts neither).

C1 result: do-nothing arm `new_forgeries=TODO-C1-donothing-new-forgeries` with base
`forgeries_accepted=TODO-C1-base-forgeries`; target run `new_forgeries=TODO-C1-new-forgeries
new_honest=TODO-C1-new-honest stubs=TODO-C1-stubs`, runner exit `TODO-C1-exit`. C2 result: base
`pass=TODO-C2-base-pass fail=TODO-C2-base-fail`; target run `pass=TODO-C2-pass fail=TODO-C2-fail
control=TODO-C2-control`, fixture exit `TODO-C2-exit`. Frozen artifacts as read (not re-run by this seat):
preregistration at commit 2670e96a, base 1e8bfd87, controls committed at 3b552509; measured revision
`TODO-MEASURED-REV`. No new score mapping,
coverage or capability acquisition beyond the two named arms; no frontier promotion. These numbers are
placeholders for the L1 to fill from the wave's receipts — this seat ran no measurement and invents none.

## Gate

Registry state committed at 3b552509 (read via `git show HEAD:corpus/SOURCES.md`): the round appends S288
(Python `os.replace` atomic publication, admitted) and S289 (Python `os.replace` cross-filesystem inference,
REJECTED) and re-opens S110, S213, S214 and S251 with unchanged cells. Those two rows are the
round's admit and reject. The `S60ScoutSources` delivery dir held no `SOURCES.append.md` at draft time; its
scratch `opened.txt` (20:51) proposed S288-S292 for rename/fsync/merge-base/os.replace/open, and that
numbering is **superseded** — in the registry S288/S289 are os.replace rows. This seat re-fetched and
re-verified every quote below on 2026-11-04 (curl, HTTP 200; sizes, hashes and the exact substring test in
`.ufo/waves/round-60/w1/S60ScribeEntry/source-fetch.txt`).

- **S288 admit — Python `os.replace`, https://docs.python.org/3/library/os.html#os.replace**, opened
  2026-11-04 by the round-60 L1 (docs.python.org 3.15.2, 791358 bytes, capture
  `census/round-60/sources/s288-python-os-replace.html`). Located quote (14 words): `If successful, the
  renaming will be an atomic operation (this is a POSIX requirement).` Re-verified verbatim by this seat.
  Used by `corpus/knowledge/atomic-receipt-write.md`.
- **S289 reject — Python `os.replace` cross-filesystem inference**, same URL and access date. REJECTED: the
  page states the operation may fail across filesystems, so it does not license renaming a temp created
  under `TMPDIR` onto a receipt path on another device; flip: keep the temp beside the output. This is the
  round's reject row and the reason `atomic-receipt-write.md` forbids a `TMPDIR` temp for the receipt.
- **S213/S214 re-opened (cells unchanged) — POSIX rename() and fsync()**, IEEE Std 1003.1-2024. S213
  grounds atomic publication and the untouched-target-on-failure rule; S214 grounds the data half of
  durability and its null-implementation limit. Both already cited by `atomic-receipt-write.md`.
- **S251 re-opened (cells unchanged) — git-merge-base(1) § OPERATION MODES `--is-ancestor`**, plus S239/S244
  for the exit-status contract. The page sentence this seat verified (25 words): `Check if the first
  <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not.`
  S251's scope carries the reflexivity (a commit is an ancestor of itself) that makes the freeze record's
  revision binding strict. Used by `corpus/knowledge/freeze-record-substance-binding.md`.
- **S110 re-opened, SCOPE GAP — rename(2), https://man7.org/linux/man-pages/man2/rename.2.html.** The row
  covers `RENAME_NOREPLACE` only; `atomic-receipt-write.md` quotes a different sentence on the same page
  (23 words): `it will be atomically replaced, so that there is no point at which another process
  attempting to access newpath will find it missing`. A widened anchor on S110 or a new row is required;
  the quote, page size (23571 bytes) and sha256
  (8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57) are recorded in `source-fetch.txt`.
- **S-PENDING, NO ROW — open(2) O_TRUNC, https://man7.org/linux/man-pages/man2/open.2.html** (man-pages
  6.19, page dated 2026-09-09, 76506 bytes). The existing open(2) rows (S077/S242/S245) are ENXIO-scope
  only. Located quote (7 words): `it will be truncated to length 0` — conditioned in the page on an
  existing regular file and a write-capable access mode. This is the fact that makes a `>` redirect
  destroy the previous receipt at open; it needs its own row before `atomic-receipt-write.md` can cite it.
- **S-PENDING, NO ROW — fsync(2) § NOTES, https://man7.org/linux/man-pages/man2/fsync.2.html** (man-pages
  6.19, 15152 bytes). No man7 fsync(2) row exists (S214 is the POSIX page). Located quotes: (16 words)
  `so that all changed information can be retrieved even if the system crashes or is rebooted` — the data
  half; (19 words) `Calling fsync() does not necessarily ensure that the entry in the directory containing
  the file has also reached disk` — the directory half that names the writer's missing directory fsync.
- **Rows added: TODO-SOURCES-ROWS (admit TODO-SOURCES-ADMIT, reject TODO-SOURCES-REJECT).** No existing
  row's status, recheck or used-by cell changed. `sources-census.sh validate --root
  /home/vgpnk/Projects/shokunin souji` exit `TODO-SOURCES-CENSUS-EXIT`, W04 duplicate-URL warnings
  before=66 (observed in `.ufo/waves/round-60/w1/S60ScoutSources/census-before.txt`: 67 lines, 66 `W04`
  plus one `ok` line for corpus/SOURCES.md), after=`TODO-SOURCES-W04`. The census-before receipt shows the
  open(2) and git-merge-base URLs are already in the registry under other scopes (S077/S242/S245 and
  S244/S251), so a new row on either URL will read as a W04 duplicate by design.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| vacuous: a control receipt that binds nothing is red-identical to a fully bound one | `tools/souji-freeze-check.py` lines 225-239 at 1e8bfd87 (blob sha256 d1ca06fd0fb21d4c7a8452dbbc879f2ecf63ffaaf65378efa3c512e4dbfca364): the only content test is `lines[-1]` against `^EXIT=(\d+)$` with a non-zero value; `instrument=`, `instrument_sha256=`, `rev=` and `command=` inside the receipt are never parsed, and the Counter digest check (160-184) compares the Counter blob to the PREREG's digest, never to the receipt's | S60ScribeEntry source read (this file's decision table) | C1 `--substance` arm with the seven frozen finding classes; the 8-case matrix measures the five classes it covers. Unrun here: `TODO-C1` |
| unsafe: an in-place `>` redirect truncates the previous receipt at open, with no error and no fsync | `census/round-57/record-receipt.sh` lines 26-33 (blob fae325df3fadd0aab1390afd226b199785395379): `OUTPUT=$("$@" 2>&1)` buffers unbounded, then `} > "$OUT"` opens with O_TRUNC before the block runs; no temp file, no fsync, no bound, no dirty-tree check | S60ScribeEntry source read; open(2) O_TRUNC clause and rename(2)/os.replace quotes above | C2 writer: temp beside OUT, fsync, `os.replace`, pre-check existence, `--max-bytes`, dirty-tree refusal. Unrun here: `TODO-C2` |
| provenance: the SOURCES draft was absent when the entries were drafted, so the entries cite `S-PENDING` | `ls .ufo/waves/round-60/w1/S60ScoutSources` empty at draft time; this file's Gate ids | S60ScribeEntry | L1 binds the ids from the scout's `SOURCES.append.md` and replaces `S-PENDING` before integration; no id is guessed after S287 |
| conflict: the round claim text says the base recorder is 3/8, the frozen preregistration's kill rule says `pass=4`, and the committed control receipt says 4 | `census/round-60/controls/c2-do-nothing.txt` (committed 3b552509, `EXIT=1`) prints `SUMMARY cases=8 pass=4 fail=4` with cases 1/2/5/8 failing; `census/round-60/preregistration.txt` C2 Kill names `pass=4`; the wave claim text states 3/8 | S60ScribeEntry read of both committed artifacts; neither re-run | L1 resolves by stating the receipt's number and correcting the claim text or the prereg — not by averaging, and not by a silent pick. This seat asserts neither number |
| vacuous (inherited, not repaired): the freeze record's `EXIT=` line is validated as text, not as an observed process status | `freeze-record-substance-binding.md` § What this does NOT prove; the base tool never spawns the counter | S60ScribeEntry | not repairable inside the freeze checker; execution evidence must come from executed controls (the round's own selftest/matrix receipts). Named, not fixed |

## Named limits

- **The substance arm discriminates five forgery classes; it does not authenticate execution.** A receipt
  that truthfully names the instrument, its digest, a real pre-freeze revision and a command string
  containing the counter path still passes if no such command ever ran. `command=` is substring
  containment, so a mention of the counter path satisfies it. `TODO-C1` for the measured counts.
- **Two of the seven finding classes have no matrix row.** `CONTROL-REV-INVALID` (a `rev=` that does not
  resolve) and `CONTROL-COMMAND-MISSING` (no `command=` line) exist in the arm but are outside the frozen
  8-case matrix; an unexercised branch is unproved.
- **Byte-identity of the unflagged path is a separate receipt, not an assumption.** The claim that the
  default output stays byte-identical rests on `TODO-C1-IDENTITY` (the three-revision diff receipts);
  this seat did not run it.
- **The writer's overwrite refusal is check-then-replace, not an atomic no-clobber.** Two writers racing
  one destination can both pass the pre-check and the later `os.replace` wins silently; `RENAME_NOREPLACE`
  (S110/S268) would close it and is not used. The dirty-tree refusal cannot see ignored-but-modified
  instruments (`status --porcelain` without `--ignored`) or a dirty nested repository.
- **No crash test is claimed.** Atomic publication rests on POSIX rename/fsync semantics (S213/S214 and the
  pages above); S214 records that a null `fsync` implementation is permitted, and the specified writer
  does not fsync the containing directory, so a crash between replace and directory flush can lose the
  name. Nothing here was run under a power-cut or `fsfreeze` harness.
- **`instrument_sha256=` binds committed bytes at a revision, never execution**, in both the freeze record
  and the receipt; an uncommitted worktree edit is invisible by construction.
- **Two ids remain unbound and one anchor is too narrow.** `S-PENDING` marks the two facts with no
  registry row (open(2) O_TRUNC, fsync(2) § NOTES directory entry); S110's scope covers
  `RENAME_NOREPLACE` only and not the plain-replace sentence `atomic-receipt-write.md` quotes. Those are
  rows the L1 must open or widen; this seat opened pages and recorded quotes/hashes, and invented no id.
  The round's reject row exists in the worktree registry (S289) and is cited as the registry's, not as this
  seat's opening.
- **Live documentation is not byte-stable within a day.** docs.python.org served 791358 bytes at 20:47 with
  sha256 `ece1ab71f281f72bbaaa318f6e376adeceed40466f086861eb1edfbb79f68079` (matching the scout's
  `opened.txt`) and the same 791358 bytes at 21:0x with sha256
  `cdf486e8533a8d88649acae57a03b6df89f048ffb78d6df744937cce1b394f51`; three consecutive later fetches were
  identical to each other, and every quoted sentence is present in both. The quoted text is stable, the
  page bytes are not, so the capture path — not a remembered hash — is the pin, and S288's row records a
  size without a sha256.
- **The two committed control receipts are cited as evidence, never re-run.** `c1-do-nothing.txt` and
  `c2-do-nothing.txt` were read from commit 3b552509; every number attributed to them is quoted from their
  own SUMMARY lines, and the `TODO-*` markers are for the target-run values the L1 measures.
- **No measurement is stated by this skeleton.** Every `TODO-<claim>` marker is a number the L1 fills from
  wave receipts (C1 matrix base/new, C2 fixture base/new, stub verdicts, freeze and measured revisions,
  SOURCES census counts). This seat ran no counter, no fixture and no census, and reports no exit code it
  did not observe.
- **Scope:** leaf seat, no subagent dispatch, no production file edited, no git/jj mutation, no install or
  upgrade attempted. The two knowledge entries and this skeleton are candidates delivered under
  `.ufo/waves/round-60/w1/S60ScribeEntry/` for the L1 to copy into `corpus/`.
