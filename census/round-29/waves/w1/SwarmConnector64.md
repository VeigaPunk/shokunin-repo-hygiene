# SwarmConnector64 — cross-source pattern finder (round 29, w1)

## Status

STATUS: PASS — all four C3 sources and the lane's existing F3 entry were opened
this run and compared; seven patterns delivered with both sides cited
(`.ufo/waves/round-29/w1/deliver-cross-source-patterns.md`). No lane file was
edited, no frozen counter/predicate/target/case set touched, no third entry or
SOURCES row proposed.

**Mid-run landing.** The L1 landed C3 at commit
`1dc678500c92164b0b2bea82b934dd03d1dfbf38` while this seat was running. Every
finding was therefore re-checked against the **committed** bytes, not only the
staged wave files, and the frozen counters were re-run at that commit
(`census/round-29/c3-integrity.py --root . --rev 1dc6785…` → `legs=9 fail=0`;
gate `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`; `rows=143`;
coverage `grounded=15 mapped=15 dangling=0 mismatches=0`). Findings 1, 2, 4
and 6 are still open against committed bytes and are input for an append-only
follow-up; this seat did not and could not edit the landed entries.

## Evidence

Lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, branch master. This seat
read the preregistration at `b8cb4b31ce80e2e3314b88e85d40ea9873180804`; the L1
landed C1, C2 and C3 during the run, so the lane tip moved to
`1dc678500c92164b0b2bea82b934dd03d1dfbf38`. The two files this seat wrote are
both under `.ufo/waves/`, which `.gitignore:1` excludes, so they do not appear
in `git status --porcelain`. The working-tree changes that *are* visible at
the end (`census/round-29/c3-integrity.py` modified;
`census/round-29/controls-amended.sh` and
`census/round-29/records/controls-amended.tsv` untracked) are **not mine** —
they appeared at 22:41–22:42, after this seat's last write, and this seat
wrote nothing under `census/`.

Sources fetched live this run into `/var/tmp/souji-r29-SwarmConnector64/`
(scratch, removed at seat end). sha256 of each, compared with the sha256 the
staged entries record:

```
statx.2.html            2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e
link.2.html             9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9
cmp.1.html              5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3
broder97resemblance.pdf da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b
broder97resemblance.txt 3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d
```

All five equal the values recorded in `deliver-duplicate-verdict-identity.md:4`
and `deliver-duplicate-verdict-byte-equality.md:4`, and the four committed
copies under `.ufo/waves/round-29/w1/sources/` hash identically to my fetches.
Toolchain used (no install or upgrade performed this run): curl 8.23.0,
pdftotext 26.08.0, Python 3.14.8 (all lane scripts run as `python3 -B`),
git 2.56.0 read-only (`log`/`show`/`ls-tree`/`status`/`rev-parse` only).

Additional sources opened for the "existing entry" side of the comparison
(S016–S021, the entry's own registry rows), all hash-matched to the entry's
recorded digests: `rmlint.1.rst` `8e09de1c95c72498…`, `fdupes.1`
`5398cf7cc8e34956…`, `fclones-README.md` `c345ffd9b6c616c4…`,
`jdupes-README.md` `33b6b8d1c9e87b21…`, plus `rmlint-cautions.html`,
`fclones-dedupe.rs` `040f78e35e25f559…` (byte-equal to the entry's recorded
`040f78e3…`), `fclones-file.rs`, and `stat.1.html`.

Measured behaviour (GNU diffutils 3.12 `cmp`, GNU coreutils `stat`, statx via
libc `statx(2)`, scratch dir only):

```
### stat -c '%d' vs statx dev pair — same file, two encodings
stat -c '%d:%i  %Hd:%Ld:%i' a.txt  ->  32:54035245  0:32:54035245
statx (same file)                  ->  0:32:54035245  nlink=1 mnt_id=33

### cmp exit values
cmp a.txt missing      -> rc=2   (No such file or directory)
cmp a.txt .            -> rc=2   (Is a directory)
cmp a.txt unreadable   -> rc=2   (Permission denied)
cmp a.txt c.txt        -> rc=1   (differ: byte 6)
cmp -n 5 a.txt c.txt   -> rc=0   <-- bounded compare reports "same"

### cmp operand contract
printf 'hello\n' | cmp a.txt  -> rc=0   (second operand missing -> reads stdin)

### symlink semantics diverge across the three tools
stat   -c '%d:%i' l1 -> 32:54035725  (the LINK's inode; %F = symbolic link)
stat -L -c '%d:%i' l1 -> 32:54035245  (the TARGET's inode)
statx default       -> l1 ino=54035245 mode=100644   (follows)
statx NOFOLLOW      -> l1 ino=54035725 mode=120777   (does not follow)
cmp l1 l2 (targets differ at byte 6) -> rc=1
```

Frozen gate tool, first run read-only against the two staged entries in a
scratch root (not the lane), to establish the shape of the C3 gate counter's
remaining work at the time this seat read them:

```
$ python3 -B tools/souji-gate-check.py --root <scratch> --round-date 2026-10-25 \
    --entries corpus/knowledge/duplicate-verdict-identity.md \
              corpus/knowledge/duplicate-verdict-byte-equality.md \
    --snapshot-dir census/round-29/sources \
    --slice census/round-29/records/quarantine-slice \
    --slice-verdicts census/round-29/records/slice-verdicts.tsv
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=7
```

The 7 failures were all `check5-dangling-source: S216/S217/S218/S219` plus
`slice slice-missing` — expected in a scratch root carrying neither the
appended SOURCES rows nor the slice files. **Every quote/snapshot check
(3/4) passed** once the snapshot dir was placed at `census/round-29/sources/`;
the two entries' Gate quotes are verbatim in the snapshots.

Re-run after the L1's C3 landing, over an exported copy of the committed tree
(per amendment A4, since the gate tool reads the working tree):

```
$ D=$(mktemp -d /var/tmp/souji-r29-verify.XXXXXX) && git archive HEAD | tar -x -C "$D"
$ python3 -B "$D/tools/souji-gate-check.py" --root "$D" --round-date 2026-10-25 \
    --entries corpus/knowledge/duplicate-verdict-identity.md \
              corpus/knowledge/duplicate-verdict-byte-equality.md \
    --snapshot-dir census/round-29/sources \
    --slice census/round-29/records/quarantine-slice \
    --slice-verdicts census/round-29/records/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0

$ python3 -B census/round-29/c3-integrity.py --root . --rev 1dc678500c92164b0b2bea82b934dd03d1dfbf38
L1 PASS f3_entries=2
L2 PASS rows=143 coverage="grounded=15 mapped=15 dangling=0 mismatches=0"
L3 PASS gate="entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0" rc=0
L4 PASS bad=[]   L5 PASS bad=[]   L6 PASS bad=[]   L7 PASS bad=[]
L8 PASS identity_has=['stx_nlink', 'stx_ino'] bytes_has=True held_has=[]
L9 PASS
SUMMARY legs=9 fail=0 rev=1dc678500c92164b0b2bea82b934dd03d1dfbf38
```

So the C3 counters all pass at the landed commit. The findings below are
therefore **not** counter defects — they are statements in the committed prose
that a later reader could over-read, plus two gaps the landed entries leave
open.

## Findings

1. **The existing identity guard and statx encode "device" differently.**
   `corpus/knowledge/dupe-finders-detect-then-act.md:34` guards on
   "distinct `stat -c '%d:%i'`"; statx(2) exposes `stx_ino` ("The inode
   number of the file.") and `stx_dev_major`/`stx_dev_minor` ("The device on
   which this file (inode) resides." — § DESCRIPTION of
   `census/round-29/sources/statx.2.html`). `stat(1)` prints "device number in
   decimal (st_dev)", one packed scalar. Measured on one file: `32:54035245`
   vs `0:32:54035245` — same quantity, different bytes. The **landed**
   `corpus/knowledge/duplicate-verdict-identity.md:30-31` calls the lane's guard
   "that (device, inode) pair" and marks the mapping `[INFERENCE: stat(1) was
   not opened this run]`; this run opened stat(1), so the inference can be
   closed — but with a **correction**, not a confirmation: `%Hd:%Ld:%i`, not
   `%d:%i`, is the statx-comparable form. (The landed entry's front matter
   names `stx_dev_major`/`stx_dev_minor`, so the fields are cited; only the
   *encoding* the lane actually uses is unbacked.)

2. **A hard-link pair is "duplicate" in one cited tool's default and not in
   the others' — and the existing entry never says so.**
   rmlint: "Hardlinked files are treated as duplicates by default"
   (`rmlint.1.rst:327`). fdupes: "Normally, when two or more files point to
   the same disk area they are treated as non-duplicates" (`fdupes.1:33`).
   jdupes: "linked files are treated as non-duplicates for safety"
   (jdupes `README:118`). fclones: "In each group, remove duplicate files with
   the same inode id." (`fclones/README.md:403`) — collapses rather than
   duplicates. `cmp` (S219) reports "same" for such a pair; link(2) (S218) says
   "both names refer to the same file"; statx (S216) says "The number of hard
   links on a file." The existing entry's own guard resolves this for souji in
   line with the majority, but `grep -c 'hardlinked' corpus/knowledge/dupe-finders-detect-then-act.md`
   → `0`: rmlint's default is undocumented in the lane.

3. **Both halves of a verdict are three-valued; the existing rule is
   two-valued on both.** cmp(1): "Exit status is 0 if inputs are the same, 1 if
   different, 2 if trouble." The existing rule at `:34` is "`cmp` byte
   equality (not a hash)"; the lane's live use at `SKILL.md:86` is "`cmp` shows
   differing from the live file". `cmp` exit 1 and exit 2 are the same non-zero
   value to a shell; exit 2 is reachable (missing / directory / unreadable
   operand, all measured rc=2). On the identity side statx has its own
   cannot-tell: "it simply informs the caller which values are supported by
   this kernel and filesystem via the statx.stx_mask field", and "the kernel
   may return fields that weren't requested and may fail to return fields that
   were requested". The lane's `stat -c '%d:%i'` guard has no third state at
   all: on failure the substitution is the **empty string** (measured), so two
   failed stats compare equal.

4. **`cmp`'s operand contract is the unrecorded half of the existing rule.**
   cmp(1): "If a FILE is '-' or missing, read standard input." — `cmp "$A"`
   with `$B` unset does not fail, it compares against stdin (measured rc=0 on
   matching stdin). And "The optional SKIP1 and SKIP2 specify the number of
   bytes to skip" / "compare at most LIMIT bytes" — `cmp -n 5` on files
   differing at byte 6 returns rc=0 (measured). Neither the existing entry nor
   the **landed** `duplicate-verdict-byte-equality.md` records this (its
   `:21` says the page "does not enumerate what trouble covers" and stops
   there); it is where the existing rule is silently satisfiable by a wrong
   comparison.

5. **The corpus holds three verdict families; the existing entry names two.**
   Exact byte predicate (cmp, S219: "Compare two files byte by byte."); graded
   and thresholded (Broder, S217: "resemblance r(A, B) and their containment
   c(A, B)", "a number between 0 and 1", and one threshold already splitting
   his corpus — "2.1 million clusters contained only identical documents");
   hash-gated and probabilistic (the entry's own tools: rmlint's "Use ``-p``
   if you want byte-by-byte comparison without any hashing.", `rmlint.1.rst:194`).
   The graded family is absent from the existing entry.

6. **The three tools disagree about what a symlink path names — and statx's
   default silently changes the lane's existing guard.** `stat -c '%d:%i'` does
   not dereference (it yields the link's own inode); statx's default does
   (`AT_STATX_SYNC_AS_STAT` — "Do whatever stat(2) does. This is the default");
   `cmp` follows. The non-following behaviour is opt-in on statx:
   "If path is a symbolic link, do not dereference it: instead return
   information about the link itself" (`AT_SYMLINK_NOFOLLOW`). link(2) goes
   the other way from statx: "does not dereference oldpath if it is a
   symbolic link" (the `AT_SYMLINK_FOLLOW` paragraph) — the two new kernel
   sources disagree with each other on the default. This breaks the existing
   entry's own "no symlink component" clause (`:34`) if the guard is
   re-implemented on statx's default flags. The **landed**
   `duplicate-verdict-identity.md:69` quotes that clause in its Lane link
   ("distinct `stat -c '%d:%i'` (no symlink component)") while grounding the
   identity leg in S216/S218 — the two sources it cites disagree on the
   default, and statx's default is the dereferencing one. Still open.

7. **Two staged identity variants existed; the collision is now resolved.**
   Both `deliver-duplicate-verdict-identity.md` and `deliver-entry-identity.md`
   targeted `corpus/knowledge/duplicate-verdict-identity.md`, with different
   front matter and different claim wording. The L1 landed the
   `deliver-entry-identity.md` variant (its front matter names
   `stx_dev_major`/`stx_dev_minor` and its `:31` carries the `[INFERENCE: ...]`
   marker that Finding 1 addresses). The comparison in the delivery was
   written against the union of their claims; Finding 1's correction applies
   to what landed.

**Which existing-entry statements the new sources better ground** (the
append-only link-note candidates, in the L1's terms — the delivery proposes
the note, it does not land it):

- `:34` "distinct `stat -c '%d:%i'`" — grounded by statx's split fields and
  link(2)'s "both names refer to the same file", **corrected** by Finding 1.
- `:34` "no symlink component" — grounded by a named kernel flag
  (`AT_SYMLINK_NOFOLLOW`) instead of a prohibition, and shown to conflict with
  statx's default. Strongest single link-note candidate.
- `:34` "`cmp` byte equality (not a hash)" — grounded as a primary source
  instead of a convention, and extended by the third exit value and the
  operand contract.
- `:34` "a recorded original that is never the removal target" — grounded by
  link(2), which says it is "impossible to tell which name" was the original
  (`census/round-29/sources/link.2.html:102-103`), so *original* is a declared
  policy choice, not a filesystem fact.
- `:26` (fdupes `-H` failure case) — grounded further by rmlint's own caution
  that the check "automatically filters out path doubles".
- `:9` (hash default) — better grounded as the middle of the three-family
  ladder (Finding 5).

**One statement the new sources do NOT ground:** `:34` "a second `cmp` at act
time". Neither cmp(1), link(2) nor statx(2) speaks to act-time re-checking;
the landed byte-equality entry says so correctly ("No act-time guarantee").
That requirement stays grounded where it is today, in the dupe-finder sources.
A link note should say so rather than let the new sources appear to cover it.

## Attack log

Not an attack seat; no counter, predicate, target or case set is proposed for
change, so no amendment is requested. The C3 counters were re-run at the
landed commit and all pass (`legs=9 fail=0`, gate `entries=2 ok=2
slice_verdicts=8 slice_total=8 fail=0`, `rows=143`, coverage `grounded=15
mapped=15 dangling=0 mismatches=0`), so nothing here is a counter defect.

One point of record for the L1, on the landed `used-by` mapping rather than
on any counter: the C1 counter's `used-by` symmetry rule means each S-row must
name exactly the entries that cite it. At the landed commit the mapping is
S216 → identity entry; **S217 → identity entry only**; S218 → both entries;
S219 → byte-equality entry. That matches the landed entries' front matter
(the byte-equality entry cites S219 and S218 only) and the L1's own amendment
A4 note, which records the S217 narrowing as a response to the Critic49 /
Critic53 attacks. No counter semantics are touched by this note, and no
amendment is requested on the basis of it.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-cross-source-patterns.md`
  — seven cross-source patterns, each with both sides quoted (<=25 words,
  verbatim, located, no pipe character), the append-only link-note candidates,
  the explicit statement of what the new sources do *not* ground, a
  mid-run-landing revision note, and a priority list for the L1's follow-up.
  Contains no third entry, no `ground: F3` line and no SOURCES row, so the C3
  counters' targets are unaffected by it (the landed commit already has
  F3-grounded entries = 2 and rows = 143; this file changes neither).
- This report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/SwarmConnector64.md`.

**Checks the L1 should run** (not run by this seat, which is read-only for the
lane):

- `python3 -B census/round-29/c3-integrity.py --root . --rev <tip>` — expected
  `SUMMARY legs=9 fail=0` at the landed commit `1dc6785…` (measured this run,
  unchanged by my delivery).
- `python3 -B tools/souji-registry-agreement.py --root . --rev <tip>
  --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804` — expected
  `mismatches=0`; my delivery adds no registry row and no `source:` line, so
  it cannot move this counter.
- If the L1 acts on Finding 6 (the symlink-dereference divergence) or
  Finding 1 (the `%d` vs `stx_dev_major`/`stx_dev_minor` encoding), those are
  **prose edits to already-admitted entries** and would need their own
  append-only receipt; they are not covered by any counter in the frozen
  preregistration, so this seat has not made them and does not request an
  amendment for them.

Scratch `/var/tmp/souji-r29-SwarmConnector64/` removed at seat end; no file
outside the lane repo and the wave delivery directory was written. Nothing in
`/home/vgpnk/Projects/shokunin/` outside the lane repo, and nothing at all in
`/home/vgpnk/Projects/shokuknow`, was written, moved, deleted or committed.
