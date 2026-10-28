# R40sentinel59 — C2 operability: the RECORD-MISSING errno catch-all

Seat: sentinel. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Read-only on lane bytes; this
report is the only file written. No commit, no push, no git/jj mutation, no package install (pacman
paused; nothing else was needed). Scratch root `/fast/scratch/hyaku/souji-r40/R40sentinel59`
(removed after this report was written).

## Named edge (item 59)

**The `RECORD-MISSING` errno catch-all, and the "the path exists" clause that only the *joined*
analyzer can read.**

`tools/souji-worktree-drift.py` `parse_record` classifies the record path with one `except
OSError` arm:

```
tools/souji-worktree-drift.py:132-136  (blob 5a2b32941bc5c3da628ee92f75be1c33192ca311)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            raise Refusal("RECORD-MALFORMED: %s is not a regular file" % path)
        raise Refusal("RECORD-MISSING: %s" % exc)
```

`RECORD-MISSING` is therefore the class of **every** non-ENOENT `OSError`, not of the two the
docstring names. The docstring entry for that class is:

```
tools/souji-worktree-drift.py:44-45
  RECORD-MISSING         EACCES or ELOOP opening the record path: the path
                         exists but cannot be opened or read
```

Two things follow, and they are the edge:

1. The class entry enumerates **two** trigger errnos where the code admits an **open** set.
2. The clause **"the path exists but cannot be opened or read"** sits on the **continuation line**
   (`tools/souji-worktree-drift.py:45`). The r39 one-line extractor (`census/round-39/c2-counter.py:133-144`)
   truncates the entry at `...: the path` and never reads it. The r40 joined analyzer **does** read
   it — and at runtime the clause is **false** for `ENOTDIR`, where the path cannot exist at all.

This edge is distinct from the peer r40 attacks on this same claim, which I read before writing:
`R40scout41` (same-indent second continuation; the `TOTAL` token binding), `R40scout53`
(`JSON-UNWRITABLE` symlink clause vs. runtime), `R40executor62` (continuation ownership when the
wrapped prose itself begins with a class-like token), `R40executor38`/`R40executor50` (token-only
continuation detection). None of them attacks the **trigger-set membership** of the catch-all
branch or the existence clause.

## Verdict

**Falsifier, concrete and reproducible.** The r40 C2 predicate has two independent defects that
the committed bytes already expose, plus one measurement-order defect. The r40 leg cannot be
scored yet (`census/round-40/` contains only `preregistration.txt`; no r40 counter, fixture, or
candidate tool bytes exist in the tree), so this is a falsifier of the *predicate as frozen* plus a
bounded measurement plan — not a measured candidate pass/fail.

**F1 (high, operability — the leg has no base-arm failure).** The frozen predicate's control is
"a synthetic wrapped-trigger probe is detected while the r39 one-line analyzer misses it". Measured:
that probe is a property of the **analyzer**, not of the lane bytes. It passes on the pristine base
tool, on the r39 base tool, and on every variant — it never compares base bytes to candidate bytes.
So the L4 leg as described cannot fail on the base arm, and a counter that only lands the joined
analyzer plus the synthetic probe satisfies the predicate with **no change to the tool's
documentation** and no change to the tool at all.

**F2 (high, operability — the frozen pair list is not frozen, and two readings of it disagree).**
The preregistration names "the frozen list" of class/trigger pairs and enumerates none
(`census/round-40/preregistration.txt:8`). The nearest list in the lane is the r39 wave's
seven-trigger enumeration (`census/round-39/waves/w1/W1RevC2Doc.md:213`): *missing, non-regular,
schema, duplicate, TOTAL* under `RECORD-MALFORMED` and *EACCES, ELOOP* under `RECORD-MISSING`.
That list is **docstring-derived** (it is the set of triggers the docstring claims), so an analyzer
that checks the docstring against it is checking the docstring against itself. Measured on the
committed base bytes: with **whole-word** matching the leg **FAILS** (the wave spells the token
`duplicate`; the committed docstring says `duplicated` — `\bduplicate\b` does not match
`a duplicated name`), and with **substring** matching it **PASSES**. The leg's verdict on the
pristine base bytes is therefore decided by an unspecified matching mode, not by the artifact.
Both arms of that simulation were the same bytes (base = candidate tool bytes), so a leg that
PASSes on the base also PASSes on any counter-only candidate.

**F3 (medium, operability — the joined analyzer's extra reading is where the falsehood lives).**
Joining the continuation lines makes the analyzer read `the path exists but cannot be opened or
read`. Measured at runtime, that clause is false for `ENOTDIR`: the path
`<regular-file>/child.tsv` cannot exist, because a path component is a regular file. So the r40
analyzer, on the committed bytes, reads a class entry that **contradicts observed runtime
behaviour** — the exact condition the frozen kill sentence names ("if any observed class mapping
disagrees with runtime behavior"). The r39 one-line analyzer cannot see this defect at all, because
it never reads line 45. This is the one place where the r40 improvement is a strict *regression in
exposure*: joining surfaces a false clause that the old extractor hid.

**F4 (medium, coverage — the catch-all admits triggers no frozen list enumerates).** Measured
runtime classes on the committed bytes, seven triggers:

| trigger | class raised | named in the joined `RECORD-MISSING` entry? |
|---|---|---|
| absent path (ENOENT) | `RECORD-MALFORMED` | (n/a — `ENOENT` is named on the `RECORD-MALFORMED` entry) |
| chmod-000 file (EACCES) | `RECORD-MISSING` | yes |
| self-symlink (ELOOP) | `RECORD-MISSING` | yes |
| parent is a regular file (ENOTDIR) | `RECORD-MISSING` | **no** |
| leaf name > NAME_MAX (ENAMETOOLONG) | `RECORD-MISSING` | **no** |
| FIFO | `RECORD-MALFORMED` | (n/a — `non-regular` is named) |
| directory | `RECORD-MALFORMED` | (n/a — `non-regular` is named) |

`ENOTDIR` and `ENAMETOOLONG` raise `RECORD-MISSING` and are named nowhere in the docstring at any
depth. A raise-site-derived trigger set therefore **cannot** be satisfied by the committed bytes:
the frozen predicate's own kill condition already fires for the base arm.

**F5 (medium, coverage — the trigger set is open, so "all observed pairs" is not a closed
check).** Because the arm is `except OSError`, the trigger set of `RECORD-MISSING` is open: any
errno other than `ENOENT` lands there. No frozen list can enumerate it, so a leg that verifies "all
observed class/trigger pairs in the frozen list" is bounded by whatever the list happens to
contain, and the list's own provenance decides the verdict. The falsifier probe: **M1** (below)
re-classifies `ENOTDIR` from `RECORD-MISSING` to `RECORD-MALFORMED` with the **docstring
byte-identical**; no docstring-vs-runtime check can see it, because the docstring never asserted
anything about `ENOTDIR`.

## Evidence — exact commands and outputs

All commands run from `/home/vgpnk/Projects/shokunin/souji-shokunin` unless stated. Every git call
was `git -C <lane>` or ran with cwd = lane; `git rev-parse --show-toplevel` printed
`/home/vgpnk/Projects/shokunin/souji-shokunin` (asserted before the read-only blob fetches). No
`git init`, no commit, no index write — this seat created no git fixture.

### 0. Identity of the audited bytes

```
$ git rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py
5a2b32941bc5c3da628ee92f75be1c33192ca311
$ git rev-parse HEAD:tools/souji-worktree-drift.py
5a2b32941bc5c3da628ee92f75be1c33192ca311
$ git diff --stat 0242085909fb6a4ee041c5443d76316ac6d59d4b HEAD -- tools/ census/
(no output)
$ git status --porcelain
?? census/round-40/
```

`0242085909fb6a4ee041c5443d76316ac6d59d4b` is the prereg's declared base revision
(`census/round-40/preregistration.txt:2`); `HEAD` at measurement was
`be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`. The tool and census bytes are **identical** at the two
revisions, so the base arm and the candidate arm carry the same tool bytes until a candidate lands.
The only untracked path is `census/round-40/` (the preregistration itself) — pre-existing, not
mine. sha256 of the extracted base blob: `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`
(matches the drift half of `census/round-39/records/c2-after.txt` `tool_sha=59f1e57d7af0/e48ed08e6728`).

### 1. The r39 one-line control vs. a joined analyzer on the committed bytes

Script `/fast/scratch/hyaku/souji-r40/R40sentinel59/analyze_joined.py` (scratch; the r39 half is
the committed `docstring_classes` logic of `census/round-39/c2-counter.py:133-144` transcribed
verbatim; the joined half is header line + every continuation line until the next class header).

```
$ python3 -B analyze_joined.py drift-r40base.py
=== r39 one-line control (committed census/round-39/c2-counter.py logic) ===
  RECORD-MISSING -> 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path'
  RECORD-MALFORMED -> 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'
=== r40 candidate: joined (header + all continuations until next header) ===
  RECORD-MISSING -> 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path exists but cannot be opened or read'
  RECORD-MALFORMED -> 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line that does not match the schema, a duplicated name, or a TOTAL row that disagrees'
  ...
=== token ownership by depth ===
TOKEN            r39-one-line               join-1-cont                join-all
EACCES           RECORD-MISSING             RECORD-MISSING             RECORD-MISSING
ELOOP            RECORD-MISSING             RECORD-MISSING             RECORD-MISSING
ENOENT           RECORD-MALFORMED           RECORD-MALFORMED           RECORD-MALFORMED
ENOTDIR          -                          -                          -
ENAMETOOLONG     -                          -                          -
EISDIR           -                          -                          -
missing          RECORD-MALFORMED           RECORD-MALFORMED           RECORD-MALFORMED
non-regular      RECORD-MALFORMED           RECORD-MALFORMED           RECORD-MALFORMED
schema           -                          RECORD-MALFORMED           RECORD-MALFORMED
duplicated       -                          RECORD-MALFORMED           RECORD-MALFORMED
TOTAL            -                          -                          RECORD-MALFORMED
the path exists  -                          RECORD-MISSING             RECORD-MISSING
```

Two facts this fixes: (a) `the path exists` is invisible to the r39 extractor and visible to every
joined depth; (b) `ENOTDIR`/`ENAMETOOLONG`/`EISDIR` are absent at **every** depth, so no choice of
join depth recovers them.

### 2. Runtime sweep on the committed bytes

Script `probe_errno.py` (scratch). Every case was created and verified to exist with the intended
errno **before** the tool ran, and the file mode was restored afterwards.

```
$ python3 -B probe_errno.py --tool drift-r40base.py --work .../work3
case=ENOENT-absent        class=RECORD-MALFORMED   rc=2 prepared=False(True) out='REFUSAL RECORD-MALFORMED: .../absent.tsv is not a regular file '
case=EACCES-file          class=RECORD-MISSING     rc=2 prepared=True(True)  out="REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '.../locked.tsv' "
case=ELOOP-symlink        class=RECORD-MISSING     rc=2 prepared=True(True)  out="REFUSAL RECORD-MISSING: [Errno 40] Too many levels of symbolic links: '.../loop.tsv' "
case=ENOTDIR-parent-file  class=RECORD-MISSING     rc=2 prepared=False(True) out="REFUSAL RECORD-MISSING: [Errno 20] Not a directory: '.../plain.txt/child.tsv' "
case=EACCES-parent-dir    class=RECORD-MISSING     rc=2 prepared=False(True) out="REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '.../sealed/r.tsv' "
case=ENAMETOOLONG         class=RECORD-MISSING     rc=2 prepared=False(True) out="REFUSAL RECORD-MISSING: [Errno 36] File name too long: '.../xxx' "
```

A second battery (`probe_triggers2.py`) covered the JSON classes with the `--json` target **outside**
`--root` (inside it, `JSON-INSIDE-MEASURED-TREE` masks the others):

```
case=json-not-regular-fifo   class=JSON-NOT-REGULAR   rc=2
case=json-not-regular-dir    class=JSON-NOT-REGULAR   rc=2
case=json-hardlinked         class=JSON-HARDLINKED    rc=2
case=json-symlink-component  class=JSON-UNWRITABLE    rc=2
case=json-is-record          class=JSON-IS-RECORD     rc=2
case=json-inside-root        class=JSON-INSIDE-MEASURED-TREE rc=2
case=usage-root-not-dir      class=USAGE              rc=2
```

**Correction to my own earlier run:** the first version of `probe_triggers2.py` reported
`case=eloop class=RECORD-MALFORMED`, and `probe_runtime.py` reported
`case=json-not-regular class=JSON-INSIDE-MEASURED-TREE`. Both were defects of that script (the
`ELOOP` symlink was never created, so the path was absent; the JSON target sat under `--root`).
The corrected runs above are the ones this report rests on. The defective readings are not cited
as evidence anywhere.

### 3. The synthetic wrapped-trigger probe (the prereg's control) is analyzer-only

Script `item59_harness.py` part A. The synthetic module docstring is:

```
  RECORD-MISSING         opening the record path failed:
                         EACCES or ELOOP
```

Both trigger tokens are absent from the first physical line, as the prereg requires.

```
$ python3 -B item59_harness.py --tool drift-r40base.py --work .../work4
=== A. synthetic wrapped-trigger probe (prereg requirement) ===
  r39 one-line  RECORD-MISSING -> 'RECORD-MISSING         opening the record path failed:'
  r40 joined    RECORD-MISSING -> 'RECORD-MISSING         opening the record path failed: EACCES or ELOOP'
  token=EACCES r39 one-line sees it: False (control: must be False) | r40 joined sees it: True  (candidate: must be True)
  token=ELOOP  r39 one-line sees it: False (control: must be False) | r40 joined sees it: True  (candidate: must be True)
  PART-A RESULT: control_misses=True candidate_detects=True -> True
```

This is exactly the discriminator the prereg asks for — and it is satisfied by the analyzer alone.
It says nothing about the lane bytes, because the probe is a synthetic string. A counter can
therefore satisfy the whole L4 predicate by shipping the joined analyzer and this probe, with the
tool's documentation left exactly as it is.

### 4. The joined analyzer vs. observed runtime — the three disagreements

Script `item59_harness.py` part C, on the committed base bytes:

```
=== C. joined analyzer vs observed runtime ===
  joined RECORD-MISSING entry: 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path exists but cannot be opened or read'
  r39   RECORD-MISSING entry: 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path'
  errno names present in the joined entry: ['EACCES', 'ELOOP']
  clause 'the path exists' in joined entry:      True
  clause 'the path exists' in r39 one-line entry: False
  DISAGREEMENT trigger=ENOTDIR class=RECORD-MISSING: trigger ENOTDIR raises RECORD-MISSING but the joined entry names only ['EACCES', 'ELOOP']
  DISAGREEMENT trigger=ENAMETOOLONG class=RECORD-MISSING: trigger ENAMETOOLONG raises RECORD-MISSING but the joined entry names only ['EACCES', 'ELOOP']
  DISAGREEMENT trigger=ENOTDIR class=RECORD-MISSING: joined entry asserts 'the path exists but cannot be opened or read'; at runtime ENOTDIR means the path does not exist (a parent component is a regular file), so the joined clause is false
  PART-C RESULT: disagreements=3
```

### 5. Falsifier M1 — a code mutant with a byte-identical docstring

Script `make_mutants.py`. M1 changes one branch (`errno.ENOENT` → `errno in (errno.ENOENT,
errno.ENOTDIR)`) and **nothing else**; the script asserts the class-entry block is byte-identical
between M0 and M1.

```
$ python3 -B make_mutants.py --pristine drift-r40base.py --outdir mutants
wrote .../M0-pristine.py sha256=e48ed08e672824e2
wrote .../M1-enotdir-reclassified.py sha256=e9437066d08e7f3b
docstring block identical between M0 and M1: True
```

### 6. The discriminating matrix

Script `matrix_final.py`, over three docstring variants and two code mutants, under two analyzer
families, plus the two committed drift fixtures.

* **AN-1** — join + token presence over the seven wave-documented pairs, r39's two probes
  (absent path, chmod-000 record). This is the shape the prereg literally names.
* **AN-2** — join + trigger set derived from the tool's **raise sites** at runtime.

```
=== DOCSTRING VARIANTS ===
  V0-pristine.py
     AN-1 (join + token presence): PASS
     AN-2 (join + raise-site sweep): FAIL
        - trigger enotdir (ENOTDIR) -> RECORD-MISSING: entry '...EACCES or ELOOP opening the record path: the path exists but cannot be opened or read' does not name it
        - trigger enametoolong (ENAMETOOLONG) -> RECORD-MISSING: entry '...' does not name it
     committed drift fixtures: r38-drift-record.py 10/10, r39-drift-record-rules.py 7/7
  V1-trigger-on-class-line.py        (the r39-lesson M1 style: trigger words onto the class line)
     AN-1: PASS
     AN-2: FAIL   (same two disagreements)
     committed drift fixtures: r38-drift-record.py 10/10, r39-drift-record-rules.py 7/7
  V2-catchall-named.py               (the correct docstring: whole catch-all set named, false existence clause dropped)
     AN-1: PASS
     AN-2: PASS
     committed drift fixtures: r38-drift-record.py 10/10, r39-drift-record-rules.py 7/7
=== CODE MUTANTS (docstring byte-identical) ===
  M0-pristine.py
     AN-1: PASS
     AN-2: FAIL   (same two disagreements)
     committed drift fixtures: r38-drift-record.py 10/10, r39-drift-record-rules.py 7/7
  M1-enotdir-reclassified.py
     AN-1: PASS
     AN-2: FAIL
        - trigger enotdir (ENOTDIR) -> RECORD-MALFORMED: entry 'RECORD-MALFORMED ... a missing (ENOENT) or non-regular record path, ...' does not name it
        - trigger enametoolong (ENAMETOOLONG) -> RECORD-MISSING: entry '...' does not name it
     committed drift fixtures: r38-drift-record.py 10/10, r39-drift-record-rules.py 7/7
```

Readings:

* **AN-1 cannot fail on any of these bytes.** The r39-lesson M1 repair (V1) is indistinguishable
  from pristine (V0) to AN-1, and M1 — a real behavioural change — is invisible to it. AN-1 is a
  token-presence check over a docstring-derived list; it is a tautology on this artifact.
* **AN-2 separates V2 from V0/V1/M0/M1.** It is the only family in this matrix with power, and it
  separates only after the *docstring* is repaired (V2).
* **Both committed drift fixtures pass every mutant**, including M1 (`r38-drift-record.py` 10/10,
  `r39-drift-record-rules.py` 7/7). No existing fixture witnesses the catch-all branch's
  membership, so M1 survives all of them.

### 7. The frozen list is not frozen, and the leg's verdict depends on an unspecified matching mode

Script `simulate_r40_counter.py`, base arm and candidate arm over the **same** tool bytes (base =
candidate tool bytes at `0242085`; no candidate tool exists in the tree).

```
=== frozen list = LIST-W (the r39 wave's seven triggers, W1RevC2Doc.md:213) ===
  base      arm: FAIL
      - RECORD-MALFORMED entry lacks whole-word 'duplicate'
  candidate arm: FAIL
      - RECORD-MALFORMED entry lacks whole-word 'duplicate'

=== frozen list = LIST-R (raise-site derived) ===
  base      arm: FAIL
      - trigger enotdir (ENOTDIR) -> RECORD-MISSING: entry '...' does not name it
      - trigger enametoolong (ENAMETOOLONG) -> RECORD-MISSING: entry '...' does not name it
  candidate arm: FAIL
      - same two

=== synthetic wrapped-trigger probe (the prereg's control) ===
  r39 one-line sees EACCES: False (control requires False)
  r40 joined   sees EACCES: True (candidate requires True)
  -> this control is a property of the ANALYZER, not of the lane bytes:
     it passes on any tool file, including the pristine base.
```

And the matching-mode measurement, on the committed base bytes against LIST-W:

```
LIST-W, whole-word  match -> base arm: FAIL RECORD-MALFORMED lacks 'duplicate'
LIST-W, substring   match -> base arm: PASS
```

The spelling mismatch is real and load-bearing:

```
$ python3 -B  # whole-word vs substring against the joined RECORD-MALFORMED entry
  whole-word \bduplicate\b  match: False | substring match: True
  whole-word \bduplicated\b match: True  | substring match: True
```

The wave's list says `duplicate` (`census/round-39/waves/w1/W1RevC2Doc.md:213`); the committed
docstring says `a duplicated name` (`tools/souji-worktree-drift.py:47`). A leg that uses whole-word
matching therefore fails the base arm over a **spelling** artefact, and one that uses substring
matching passes it. The prereg does not say which.

### 8. The r40 C2 leg is not yet scoreable

```
$ ls -la census/round-40/
-rw-r--r-- 1 vgpnk vgpnk 2299 Oct 28 16:26 preregistration.txt
```

`census/round-40/` holds only the preregistration (untracked). There is no r40 counter, no r40
fixture, no candidate tool bytes, and no `cells.tsv`/`c1-items.tsv` for r40. Every r40 C2 reading
above is therefore a reading of **committed base bytes under a simulated analyzer**, not a
measurement of a candidate. Unrun is not pass: **the r40 C2 claim is NOT MEASURED.**

## Bounded measurement plan (for the L1 / the r40 counter author)

Nothing below changes a frozen claim; it is what a counter must do for the frozen predicate to have
teeth, plus the cases that must be in the receipt.

1. **Freeze the pair list in the lane, as bytes.** A file under `census/round-40/` listing
   `(class, trigger-token)` pairs, committed before any candidate measurement. Freeze the
   **matching mode** with it (whole-word vs substring) and freeze the **token spellings** — the
   wave's `duplicate` does not whole-word-match the docstring's `duplicated`. Without the list in
   bytes, the prereg's "the frozen list" is a placeholder and the leg's verdict is a choice.
2. **Derive the trigger set from the raise sites, not from the docstring.** The catch-all arm
   (`except OSError`, `errno != ENOENT`) makes the docstring-derived list self-referential. Sweep
   the raise sites at runtime (ENOENT, EACCES, ELOOP, ENOTDIR, ENAMETOOLONG, FIFO, directory) and
   require the joined entry for the class each trigger raises to name that trigger. This is AN-2
   in §6, and it is the only family with measured power.
3. **Add the `ENOTDIR` and `ENAMETOOLONG` cases to the counter.** Both raise `RECORD-MISSING` on
   the committed bytes and are named nowhere in the docstring at any depth. Until the class entry
   names the catch-all set (or is rewritten to name the branch, e.g. "any OSError other than
   ENOENT"), the frozen kill sentence fires on the base arm.
4. **Add the existence clause to the check.** After joining, require the entry to make no false
   existence claim: for `ENOTDIR` the path cannot exist. The V2 wording tested in §6
   ("the path may not exist at all") satisfies AN-2; the committed wording does not.
5. **Add M1 to the counter's mutation battery.** `errno in (errno.ENOENT, errno.ENOTDIR)`, docstring
   byte-identical. Both committed drift fixtures pass it (10/10, 7/7); AN-2 kills it. A counter
   that only checks the seven docstring-derived pairs cannot.
6. **Give the leg a real base-arm failure.** The synthetic wrapped-trigger probe (§3) is an
   analyzer self-test. The base arm must fail on the **base bytes** for the leg to discriminate.
   Under LIST-R it does (two ENOTDIR/ENAMETOOLONG disagreements); under LIST-W with substring
   matching it does not. Requirement: the base arm fails for a reason attributable to the base
   **bytes**, and the receipt names that reason.
7. **Keep the r39 one-line control.** It is the right control for the extractor change
   (`census/round-39/c2-counter.py:133-144`), and the synthetic probe correctly shows it misses a
   continuation-only trigger. It must be recorded as an *analyzer* property, not as evidence about
   the lane's documentation.

## Smallest remediation (ordered by cost)

1. Commit the frozen pair list + matching mode + spellings under `census/round-40/` (bytes, before
   candidate measurement). — removes F2.
2. Add the `ENOTDIR`/`ENAMETOOLONG` runtime probes and require the joined `RECORD-MISSING` entry to
   name the whole catch-all set, and drop/qualify the "the path exists" clause. — removes F3, F4.
3. Require the base arm to fail on base bytes for a byte-attributable reason; record the reason in
   the receipt. — removes F1.
4. Add M1 to the counter's mutation battery. — closes F5's blind spot.

## Scope and limits

- Read-only on lane bytes; the only file written is this report.
- No commit, push, `git init`, index write, or jj mutation. `git rev-parse --show-toplevel` was
  asserted (`/home/vgpnk/Projects/shokunin/souji-shokunin`) before the blob reads; no git fixture
  was created, so the fixture-top-level rule was not exercised.
- Tool installs/upgrades: **none**. pacman untouched (paused); no `uv tool`/`npx`/binary install
  was needed. Python 3.14.8, git 2.56.0, both pre-installed.
- Scratch `/fast/scratch/hyaku/souji-r40/R40sentinel59/` (harnesses, variants, mutants, probe
  output, work dirs) removed after this report was written. No `/tmp` file was created.
- **Not claimed:** the r40 C2 claim is not scored (no r40 counter, fixture, or candidate bytes
  exist in the tree). The falsifiers above are readings of committed base bytes under simulated
  analyzers; they bound what a candidate counter can honestly assert, and they do not assert that
  any particular candidate fails.
- Peer r40 reports on this same claim were read first (`R40scout17`, `R40scout41`, `R40scout53`,
  `R40executor38`, `R40executor50`, `R40executor62`); this seat's edge (the errno catch-all and
  the existence clause) is distinct from all of them.
