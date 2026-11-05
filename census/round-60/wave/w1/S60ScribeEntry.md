# S60ScribeEntry — round-60 wave-1 scribe report

Scope: draft two knowledge entries and the round lesson skeleton in this seat's delivery dir. Leaf seat:
no subagent dispatch, no production file edited, no git/jj mutation, no install or upgrade attempted, no
measurement run (no counter, fixture, matrix or census executed).

## Delivered (absolute paths, line counts)

| path | lines | S-ids cited |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ScribeEntry/corpus/knowledge/freeze-record-substance-binding.md` | 127 | **no pending id**: S251 (primary) + S239/S244 (exit statuses), corroborating S110, S268, S212, S213, S214 |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ScribeEntry/corpus/knowledge/atomic-receipt-write.md` | 140 | S288 (admitted, os.replace), S289 (rejected, os.replace cross-filesystem), S213, S214, S212, S268, S110; `S-PENDING` ×2 (open(2) O_TRUNC, fsync(2) § NOTES) |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ScribeEntry/corpus/lessons/round-60.md` | 128 | S288, S289, S213, S214, S251, S239, S244, S110; `S-PENDING` ×2; `TODO-*` markers for every number |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ScribeEntry/source-fetch.txt` | 106 | fetch/quote/hash receipts, scout-quote cross-check, registry cross-check, committed-control cross-check, byte-stability probe |

Frontmatter is the corpus four-key form (`source:`, `verified-at:`, `recheck:`, `ground:`) in both entries;
`ground:` names F1 for the freeze record and F4 (restorable quarantine, file-system semantics) for the
atomic write.

## State that changed under the drafts (read, not written, by this seat)

The lane advanced from 1e8bfd87 to HEAD `2670e96a` while this seat worked:

- **3b552509** "substance arm, atomic receipt writer and their frozen fixtures" committed
  `corpus/SOURCES.md` (+4 lines: S288 = Python `os.replace` atomic publication **admitted**, S289 =
  `os.replace` cross-filesystem inference **REJECTED**, plus a provenance note), `tools/souji-freeze-check.py`
  (+175 lines), `tools/souji-receipt-write.py` (new, 694 lines), the C1/C2 fixtures and matrix, **and a
  57-line `corpus/knowledge/freeze-record-substance-binding.md` plus a 42-line `corpus/lessons/round-60.md`
  at this seat's exact filenames**.
- **2670e96a** "freeze the two claim predicates after executed red controls" committed
  `census/round-60/preregistration.txt` and the two control receipts.

Consequences applied to my drafts: entry 2 cites **S288** for os.replace atomicity and **S289** as the
round's reject; the scout's scratch numbering (S288 rename, S289 fsync, S290 merge-base, S291 os.replace,
S292 open — `opened.txt`, 20:51) is **superseded** and appears in no artifact; entry 1 needs no new id at
all (its only external fact is the reflexivity of the ancestry predicate, S251).

## Findings routed to the L1

1. **Conflict, reported verbatim: the base recorder's C2 score is stated three ways.** The wave claim text
   says `census/round-57/record-receipt.sh` = **3/8**; the frozen `census/round-60/preregistration.txt` C2
   Kill rule says the do-nothing arm "prints **pass=4**"; the committed control receipt
   `census/round-60/controls/c2-do-nothing.txt` (3b552509, `EXIT=1`) prints
   `SUMMARY cases=8 pass=4 fail=4` with cases 1, 2, 5, 8 failing and 3, 4, 6, 7 passing (case 5's detail is
   `tool rc=127`). I re-ran neither and assert neither number; the conflict is in the lesson's `## Mistakes`
   table and in entry 2.
2. **My two filenames are already committed with different drafts** (57-line entry, 42-line lesson, both
   added in 3b552509). `diff` against my delivery is non-empty. The committed entry also places `ground:`
   after the title rather than in the four-key header block. I did not edit, move or delete them; the L1
   must choose which draft lands and keep the header convention.
3. **Two facts still have no registry row.** (a) open(2) **O_TRUNC** — `it will be truncated to length 0`
   (7 words, page sha256 `d665489c…91c789`); existing open(2) rows S077/S242/S245 are ENXIO-scope only.
   (b) fsync(2) **§ NOTES directory entry** — `Calling fsync() does not necessarily ensure that the entry in
   the directory containing the file has also reached disk` (19 words, page sha256 `f0a986d2…5d91f5`); no
   man7 fsync(2) row exists (S214 is the POSIX page). Both are `S-PENDING` in entry 2 and the lesson Gate.
4. **S110's anchor is too narrow for entry 2.** The row covers `RENAME_NOREPLACE`; entry 2 quotes the
   plain-replace sentence (`it will be atomically replaced, so that there is no point at which another
   process attempting to access newpath will find it missing`, 23 words). Widened anchor or new row needed.
5. **Live documentation is not byte-stable within a day.** docs.python.org served 791358 bytes at 20:47 with
   sha256 `ece1ab71…f68079` (the scout's hash) and the same 791358 bytes at 21:0x with sha256
   `cdf486e8…b394f51`; three later fetches were identical to each other and every quoted sentence is present
   in both. S288's row records a size and a capture path but no sha256, so the capture path is the pin.
6. **The base Control grammar reads one line.** At 1e8bfd87 the `Control:` branch (lines 225-239) tests only
   existence at freeze, symlink refusal, `lines[-1]` against `^EXIT=(\d+)$` with a non-zero value, and
   freeze/rev blob equality. `instrument=`, `instrument_sha256=`, `rev=`, `command=` inside a receipt are
   unread bytes; the Counter digest check (160-184) never compares the receipt's digest to the Counter blob.
   Source-read, not measured — the justification for the C1 arm.
7. **The base recorder destroys the old receipt at open.** `census/round-57/record-receipt.sh` line 26
   captures unbounded output into a variable and line 33 opens `$OUT` with O_TRUNC before the block runs;
   no temp file, no fsync, no byte bound, no dirty-tree check, no `command=` line. The C2 gap.
8. **The committed C1 control confirms the table.** `census/round-60/controls/c1-do-nothing.txt` (3b552509,
   `EXIT=1`) is written in exactly the four-binding shape entry 1 specifies and records `base=accept` for
   all five forgery cases (`forgeries_accepted=5`; `--new-arm plain` gives `new_forgeries=5`). Cited in
   entry 1 as evidence, not re-run.

## Content of the three artifacts

- **Entry 1** decision table has exactly the five frozen forgery classes with finding id and line-level
  reason the base grammar accepts each: `kind-only → CONTROL-INSTRUMENT-MISSING`,
  `digest → CONTROL-INSTRUMENT-MISMATCH`, `rev-at-freeze → CONTROL-REV-NOT-BEFORE-FREEZE`,
  `rev-missing → CONTROL-REV-MISSING`, `command-other → CONTROL-COMMAND-MISMATCH`. It names the two arm
  classes outside the frozen matrix (`CONTROL-REV-INVALID`, `CONTROL-COMMAND-MISSING`) and what the bindings
  do NOT prove (bytes not execution; a truthful forgery of the same bytes passes; `command=` is substring
  containment; ancestry is a graph property; `EXIT=` is validated as text).
- **Entry 2** grounds temp-beside-output + file fsync + `os.replace` on S288/S213/S214, sources the
  directory-fsync gap on the fsync(2) NOTES sentence, explains `>` truncation at open via O_TRUNC, and gives
  a refusal table naming the TOCTOU gap in check-then-replace (RENAME_NOREPLACE, S110/S268, unused).
- **Lesson** has `## Gate` (S288 admit, S289 reject, S213/S214/S251 re-opened, S110 scope gap, two
  `S-PENDING` facts, each with URL, access date 2026-11-04, version, ≤25-word quote and word count),
  `## Mistakes` (5 rows: vacuous control grammar, unsafe `>` recorder, unbound provenance, the 3-vs-4
  conflict, inherited unobserved `EXIT=`), `## Named limits`. Every claim number is a `TODO-<claim>` marker
  in the frozen summary vocabulary (`new_forgeries`, `new_honest`, `stubs`, `pass`, `fail`, `control`); the
  only filled number is the W04 before-count, observed in the scout's own receipt.

## Exact commands and observed outputs

Read-only git (cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`):

```
git rev-parse --verify -q 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4^{commit}
  -> 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4        rev_verify_rc=0
git cat-file blob 1e8bfd87…:tools/souji-freeze-check.py | sha256sum
  -> d1ca06fd0fb21d4c7a8452dbbc879f2ecf63ffaaf65378efa3c512e4dbfca364
sha256sum tools/souji-freeze-check.py
  -> d1ca06fd0fb21d4c7a8452dbbc879f2ecf63ffaaf65378efa3c512e4dbfca364   (blob == worktree at read time, rc=0)
git rev-parse 1e8bfd87…:census/round-57/record-receipt.sh
  -> fae325df3fadd0aab1390afd226b199785395379        recorder_blob_rc=0
git cat-file blob 1e8bfd87…:tools/souji-freeze-check.py | awk 'NR>=176 && NR<=242'
  -> numbered dump; Control branch = lines 225-239, EXIT_LINE = line 53, ancestry test = 206-213
awk '{printf "%d: %s\n", NR, $0}' census/round-57/record-receipt.sh | sed -n '18,35p'
  -> unbounded capture at line 26, `} > "$OUT"` at line 33
ls -A .ufo/waves/round-60/w1/S60ScoutSources | wc -l      -> 2 (census-before.txt, census-before.stderr.txt)
wc -l …/census-before.txt ; grep -c W04 …                -> 67 lines, 66 W04 + one `ok` line
git status --porcelain                                    -> at first read 7 lines (M corpus/SOURCES.md;
  M tools/souji-freeze-check.py; ?? census/round-60/; ?? corpus/knowledge/freeze-record-substance-binding.md;
  ?? corpus/lessons/round-60.md; ?? tests/fixtures/r60-receipt-write.py; ?? tools/souji-receipt-write.py);
  at the final read 1 line (?? census/round-60/records/) after the L1 committed 3b552509 and 2670e96a
git check-ignore -v .ufo/waves/round-60/w1/S60ScribeEntry.md  -> .gitignore:1:.ufo/waves/   (ignore_rc=0)
git log --oneline -3                                      -> 2670e96a, 3b552509, 1e8bfd87
git show --stat --format='%h %s' 3b552509                 -> SOURCES.md +4, knowledge entry 57+, lesson 42+,
  freeze-check +175, receipt-writer 694+, fixtures/matrix
git show HEAD:corpus/SOURCES.md | grep -c '^| S288 \|^| S289 '  -> 2
cat census/round-60/c1-matrix.tsv                         -> header + 8 cases (3 honest, 5 forgery)
cat census/round-60/preregistration.txt                   -> C1/C2 predicates, base 1e8bfd87, controls 3b552509
cat census/round-60/controls/c1-do-nothing.txt            -> bound receipt, base=accept ×5, EXIT=1
cat census/round-60/controls/c2-do-nothing.txt            -> pass=4 fail=4, EXIT=1
```

Fetches (scratch cwd `/fast/scratch/hyaku/souji-r60/S60ScribeEntry`, `curl -sSL --max-time 40`, 2026-11-04):

```
https://man7.org/linux/man-pages/man2/rename.2.html   -> 200 23571 bytes   sha256 8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57
https://man7.org/linux/man-pages/man2/fsync.2.html    -> 200 15152 bytes   sha256 f0a986d21500222ecb69580fc7a910f346c6b1ff1005ca515501fb05bb5d91f5
https://man7.org/linux/man-pages/man2/open.2.html     -> 200 76506 bytes   sha256 d665489cadb85624d98fae03a8d8d06209030f32735cff8aeba949ad8491c789
https://git-scm.com/docs/git-merge-base               -> HTTP=200 SIZE=41397 sha256 46d106b777754f7ec3072813ace57d2c5385d110181b8db1c56b7136cfb49644
https://docs.python.org/3/library/os.html             -> rc=0, 791358 bytes; sha256 ece1ab71…f68079 at 20:47, cdf486e8…b394f51 at 21:0x
```

Document versions from the served bytes: man-pages 6.19 (page dated 2026-09-09) for the three man pages;
git-scm web manual "last updated in 2.43.0"; docs.python.org serving Python 3.15.2.

Located-quote verification (tags stripped, whitespace normalised, exact substring test + `len(split())`),
copied verbatim into `source-fetch.txt`:

```
man2-rename.2.html     FOUND   words=23 | it will be atomically replaced, so that there is no point at which another process attempting to access newpath will find it missing
man2-open.2.html       FOUND   words= 7 | it will be truncated to length 0
man2-fsync.2.html      FOUND   words=16 | so that all changed information can be retrieved even if the system crashes or is rebooted
man2-fsync.2.html      FOUND   words=19 | Calling fsync() does not necessarily ensure that the entry in the directory containing the file has also reached disk
git-merge-base.html    FOUND   words=25 | Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not.
os.html                FOUND   words=14 | If successful, the renaming will be an atomic operation (this is a POSIX requirement).
os.html                FOUND   words=17 | If dst exists and is a file, it will be replaced silently if the user has permission.
os.html                FOUND   words=12 | The operation may fail if src and dst are on different filesystems.
open.html              FOUND   words=17 | Write operations on the file will complete according to the requirements of synchronized I/O data integrity completion.
```

Exit codes: every command above completed with status 0; the deliberate rc captures printed
`rev_verify_rc=0`, `tool_blob_eq_worktree_rc=0`, `recorder_blob_rc=0`, `ignore_rc=0`. No command was run
against the C1 arm, the C2 writer, the matrix, the fixture or the census, so no measurement exit code is
reported; the two control receipts' `EXIT=1` lines are quoted from their committed bytes.

## Named limits

- No measurement, no fixture, no counter, no census run by this seat; every number in the lesson skeleton is
  a `TODO-<claim>` marker for the L1, in the frozen summary vocabulary.
- The entries assert only source-read facts about committed blobs at 1e8bfd87 and about the pages quoted;
  they make no claim about the C1 arm's or C2 writer's behaviour (committed in 3b552509, unrun by me).
- No execution-authenticity claim: both entries state that `instrument_sha256=` binds bytes, that a
  truthful forgery of the same bytes passes, and that `EXIT=` is validated as text.
- No crash/durability claim: atomic publication rests on POSIX rename/fsync semantics and the quoted pages;
  S214's null-implementation limit and the missing directory fsync are named, not repaired.
- Page bodies are not copied into the lane (only sha256, size, version, quotes in `source-fetch.txt`);
  full-page snapshots remain the scout's and the L1's capture under `census/round-60/sources/`.
- Scratch `/fast/scratch/hyaku/souji-r60/S60ScribeEntry` was created by this seat and removed
  (`scratch_removed_rc=0`) after the receipts were copied into the delivery dir.
- Writes were confined to `.ufo/waves/round-60/w1/S60ScribeEntry/` and this report; both are under the
  gitignored `.ufo/waves/`. No production file, fleet-root file, `~/.local/bin` entry, git index or jj state
  was touched.
- Tooling: no install and no upgrade was attempted or needed (curl, python3, git, awk, sha256sum all
  pre-installed); therefore no tool/version/channel record is due.
