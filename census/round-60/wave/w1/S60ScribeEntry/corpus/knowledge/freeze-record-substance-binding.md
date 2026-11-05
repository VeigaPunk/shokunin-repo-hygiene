source: S251 — git-merge-base(1) § OPERATION MODES `--is-ancestor` (strict descendant; the predicate is reflexive, so equality satisfies a bare ancestor test), with S239/S244 for the exit-status contract (0 ancestor, 1 not, other non-zero error). Corroborating admitted rows for the primitives named in passing: S110 rename(2) man-pages 6.19 and S268 renameat2(2) (plain rename replaces atomically; RENAME_NOREPLACE refuses with EEXIST), S212 POSIX open() O_EXCL, S213 POSIX rename() atomicity, S214 POSIX fsync() durability. The receipt grammar and its gaps below are read from the committed tool blob at 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 (sha256 d1ca06fd0fb21d4c7a8452dbbc879f2ecf63ffaaf65378efa3c512e4dbfca364), not from any source page, so this entry binds no pending id and cites only admitted rows. Registry state: rows S288 (Python os.replace, admitted) and S289 (os.replace cross-filesystem inference, rejected) are committed at 3b552509 (read via `git show`); neither is cited by this entry.
verified-at: 2026-11-04 — the four pages fetched from this host with curl (HTTP 200, sizes 23571 / 41397 / 76506 / 15152 bytes) and quoted from the served bytes; the tool grammar below is read from the committed blob at 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4, not from a worktree edit
recheck: 90d — re-open https://man7.org/linux/man-pages/man2/rename.2.html and https://git-scm.com/docs/git-merge-base; re-read tools/souji-freeze-check.py lines 225-239 at the then-current tip and re-run `git cat-file blob <tip>:tools/souji-freeze-check.py | sha256sum`
ground: F1 — git-native housekeeping vs receipts (a freeze record's red control must bind the instrument it names, that instrument's committed bytes at freeze, a revision strictly before the freeze commit, and the command that names it)

# A freeze record's `Control:` receipt is evidence only when it binds instrument, committed digest, pre-freeze revision and command — the base grammar binds none of them

## Claim (F1, sourced; grammar read at one committed blob, no execution claim)

**What this entry is:** the four bindings a `Control:` receipt must carry for its red exit to count as
evidence about the *declared Counter*, and the exact reason the pre-round-60 freeze checker accepted a
receipt that carries none of them. It names a grammar and its gaps. It makes no claim that any
particular round ran its counter, and it certifies no counter's correctness.

### 1. The four bindings

A claim block in a preregistration names a `Counter:` path and a `Control:` receipt path. The receipt is
read as the blob at FREEZE (git object store, never the work tree). For the receipt's red exit to be
evidence *about that counter*, the receipt must carry, as column-0 lines:

| binding | literal line | what it ties together | why the tie is needed |
|---|---|---|---|
| instrument | `instrument=<declared Counter path>` | the receipt names the same path the claim declares | otherwise the red exit may belong to any program, including one that always exits 1 |
| bytes | `instrument_sha256=<64 hex>` equal to sha256 of the declared Counter blob **at FREEZE** | the red exit is attributed to *these* committed bytes | otherwise the counter can be edited after the receipt was produced and the receipt still "explains" the old red |
| revision | `rev=<full40>` resolving to a commit that is a **strict ancestor** of the freeze commit | the bytes existed in the history before the freeze | a commit is an ancestor of itself (S251: the predicate is reflexive, so equality satisfies a bare ancestry test), so "before" must be spelled as strict |
| command | `command=` whose text contains the declared Counter path | the recorded invocation actually named the instrument | a receipt may otherwise record a different tool's red exit while naming the counter in `instrument=` |

The strictness half is the lane's own rule, grounded in the predicate's reflexivity (S251), not stated by
the git documentation as a requirement. The freeze-check arm reads it as
`resolved == freeze or not is_ancestor(resolved, freeze)` for the prereg's `Base:` line
(`tools/souji-freeze-check.py` lines 206-213 at rev 1e8bfd87).

### 2. What the base grammar actually tests (rev 1e8bfd87, blob sha256 d1ca06fd0fb21d4c7a8452dbbc879f2ecf63ffaaf65378efa3c512e4dbfca364)

The committed blob is byte-identical to the worktree copy at the lane tip when this entry was drafted
(`git cat-file blob 1e8bfd87…:tools/souji-freeze-check.py | sha256sum` equals
`sha256sum tools/souji-freeze-check.py`). The whole `Control:` branch is lines 225-239:

1. **Existence at freeze** — `repo.blob(freeze, path)` is None → `CONTROL-MISSING` (228-229).
2. **Symlink refusal at freeze** — `CONTROL-SYMLINK` (230-231), without reading the link text as a control.
3. **The only content test** — for a non-symlink blob, the tool splits the bytes into non-blank lines and
   matches **the last one** against `^EXIT=(\d+)$` (`EXIT_LINE`, line 53); a match with a non-zero value is
   the whole of "red" (233-237). Any earlier line is never parsed.
4. **Immutability** — the blob at `--rev` must equal the blob at freeze, else `FROZEN-EDITED` (238-239).
   This compares blob identity, not content semantics.

Two consequences follow directly from that code, not from a measurement:

- The receipt file is opaque bytes apart from its last non-blank line. The prereg parser's key grammar
  (`KEYLINE`, only `Base|Counter|Population|Control|Target|Kill` at column 0) applies to the
  preregistration, never to the receipt, so `instrument=`, `instrument_sha256=`, `rev=` and `command=`
  inside a receipt are unread text.
- The Counter's own digest check (`check_path_sha`, 160-184) hashes the Counter blob at freeze and compares
  it to the **preregistration's** `Counter: <path> sha256=<hex>` value. It never reads the receipt to
  compare the receipt's `instrument_sha256=` against the Counter it names. The two digests live in
  different files and are never cross-checked.

### 3. Decision table — the five forgery classes, and why the base grammar accepts each

Each row is a receipt that ends `EXIT=1` (so `CONTROL-NOT-RED` does not fire) and differs from an honest
receipt in exactly one binding. The finding id is the class the round-60 `--substance` arm must raise
(ids frozen in the wave spec before data).

| forgery class (matrix row) | finding the substance arm must raise | why the base grammar accepts it |
|---|---|---|
| kind-only: receipt is the single line `EXIT=1` | `CONTROL-INSTRUMENT-MISSING` | lines 233-237 read `lines[-1]` only; `EXIT=1` matches `EXIT_LINE` with a non-zero value, so nothing fires. No line-count, no required-line, and no `instrument=` check exists anywhere in the branch. |
| digest: `instrument_sha256=` is the sha256 of a different blob | `CONTROL-INSTRUMENT-MISMATCH` | the receipt is never hashed against anything. `check_path_sha` (160-184) compares the **Counter** blob to the **prereg's** digest; the receipt's own digest line is bytes the tool never interprets. |
| rev-at-freeze: `rev=` equals the freeze commit itself | `CONTROL-REV-NOT-BEFORE-FREEZE` | no revision inside a receipt is resolved. The only ancestry test (206-213) reads the prereg's `Base:` value. A receipt `rev=` naming the freeze commit is indistinguishable from any other opaque line, and its last line is still `EXIT=1`. |
| rev-missing: no `rev=` line at all | `CONTROL-REV-MISSING` | absence of a line is not a finding: the grammar has no notion of required receipt lines. Only `lines[-1]` participates in the verdict. |
| command-other: `command=` names another tool | `CONTROL-COMMAND-MISMATCH` | `command=` is never read, and the tool contains no path-containment or argv test anywhere. The `Control:` value is used for exactly four things: existence, symlink refusal, the last-line exit match, and freeze/rev blob equality (225-239). |

The five acceptances are not only inferred from the code: the round's committed control receipt
`census/round-60/controls/c1-do-nothing.txt` (added at commit 3b552509, last line `EXIT=1`; read by this
seat, not re-run) records `base=accept` for all five forgery cases and
`SUMMARY matrix=8 forgeries_accepted=5 honest_accepted=3 new_forgeries=5 new_honest=3 stubs=REJECTED` for the
do-nothing arm. That receipt is the measured form of this table's right-hand column.

The one thing the base grammar does enforce is that the last non-blank line is a non-zero `EXIT=`. Every
forgery above therefore keeps `EXIT=1`; a receipt ending `EXIT=0` is refused (`CONTROL-NOT-RED`), which is
why the base tool's own selftest has a `control-not-red` case and no other control case.

## What this does NOT prove

- **Bytes, not execution.** `instrument_sha256=` binds the Counter blob's bytes at freeze. It does not show
  that the recorded command ran those bytes, at that revision, on this host, or at all. Nothing in the
  receipt is signed, and nothing in the checker observes a process.
- **A truthful forgery of the same bytes still passes.** A receipt that names the right instrument, the
  right digest, a genuinely pre-freeze revision and a command string containing the counter path is
  accepted even if no such command was ever executed. The four bindings raise the *cost* of a forgery
  from "write `EXIT=1`" to "know the counter's path, digest and a pre-freeze commit", which is knowledge a
  forger with repository read access has. This is a discrimination gain against the five named classes,
  not authenticity.
- **`command=` is containment, not equality.** The frozen rule is that the command text *contains* the
  declared Counter path. `python3 tools/counter.py --help` or a comment mentioning the path satisfies it
  without invoking the counter as a counter. Substring containment cannot distinguish invocation from
  mention.
- **Revision ordering is a graph property.** A strict ancestor proves the commit exists and precedes the
  freeze in the commit graph. It says nothing about when the command ran, or whether the receipt's author
  had that commit checked out.
- **The digest is the blob at freeze from the object store**, so an uncommitted or post-freeze worktree
  edit is invisible by construction — that is the intended reading, and it also means the receipt cannot
  describe a worktree run.
- **`EXIT=` remains an unobserved claim.** The checker validates the receipt's *last line*, not the
  process's exit status. A hand-written `EXIT=1` is indistinguishable from a recorded one.
- **Two of the seven finding classes are not exercised by the frozen 8-case matrix.** The matrix covers
  `CONTROL-INSTRUMENT-MISSING`, `CONTROL-INSTRUMENT-MISMATCH`, `CONTROL-REV-NOT-BEFORE-FREEZE`,
  `CONTROL-REV-MISSING` and `CONTROL-COMMAND-MISMATCH`. `CONTROL-REV-INVALID` (a `rev=` that does not
  resolve) and `CONTROL-COMMAND-MISSING` (no `command=` line) exist in the arm but have no matrix row; an
  unexercised branch is unproved.
- **The counter's own correctness is out of scope.** This entry says the red exit is attributable to the
  declared bytes. Whether those bytes measure the declared target is the counter's claim, not this one.
- **No tool change is authorized here.** The `--substance` arm is round 60's C1 candidate; this entry
  records the contract it must satisfy and the grammar it must replace, nothing more.

## Lane link and consequence

Before round 60, a claim's red control was reproducible from a one-line file. The freeze record's purpose
is to make "this counter was red at this revision" checkable by a later reader from the committed objects
alone; the base grammar checks that *a file with a red last line* existed at freeze. The four bindings
close the five cheapest forgeries at the price of four lines per receipt, and the honest cost is that the
preregistration must be frozen *after* the counter's blob digest and a pre-freeze revision are known —
which is exactly the chronology the receipt records.

The residual gap is deliberate and must be stated wherever the arm is cited: **the arm discriminates five
forgery classes; it does not authenticate execution.** Where a round needs execution evidence, it needs
an executed control observed by an independent process (the round's own selftest and matrix receipts), not
a stronger reading of this receipt.
