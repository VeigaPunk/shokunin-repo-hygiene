# deliver-cross-source-patterns — F3 cross-source comparison (round 29, w1)

Seat `SwarmConnector64` (cross-source pattern finder, read-only). Lane base
`691dd29211c53d0ef94fa072394cb9c8a69fe92e`; preregistration
`b8cb4b31ce80e2e3314b88e85d40ea9873180804`. This file is a **comparison note for
the L1**, not a third admitted entry: the preregistration admits exactly two
(`duplicate-verdict-identity.md`, `duplicate-verdict-byte-equality.md`), so this
file adds no `ground: F3` entry and no SOURCES row. It proposes no change to any
frozen counter, predicate, target or case set.

Every quote below is verbatim from bytes opened **this run** (curl 8.23.0,
pdftotext 26.08.0, Python 3.14.8, git 2.56.0 — no tools installed or upgraded
this run) and is at most 25 words with no literal or escaped pipe. Snapshot
paths are relative to the lane root; the four C3 snapshots are committed under
`census/round-29/sources/` and byte-identical copies are in the wave directory
`.ufo/waves/round-29/w1/sources/` (sha256 verified equal this run).

Two source sets are compared: the **four C3 sources** (statx(2) S216, Broder
1997 S217, link(2) S218, cmp(1) S219) and the **lane's existing F3 entry**
`corpus/knowledge/dupe-finders-detect-then-act.md` (held since r12, commit
`d7266c5`), whose own sources are rmlint.1.rst / rmlint cautions / jdupes README
/ fdupes.1 / fclones README (S016–S021).

**Revision note.** The L1 landed C3 at commit
`1dc678500c92164b0b2bea82b934dd03d1dfbf38` *while this seat was running*
(the two entries, the four rows, the snapshots, the slice verdicts). Every
finding below was therefore re-checked against the **committed** bytes, not
only against the staged wave files: the landed
`corpus/knowledge/duplicate-verdict-identity.md` is the
`deliver-entry-identity.md` variant (front matter cites `stx_dev_major`/
`stx_dev_minor` and carries the `[INFERENCE: stat(1) was not opened this run]`
marker at `:31`), and the landed `duplicate-verdict-byte-equality.md` carries
the "does not enumerate what trouble covers" sentence at `:21`. The frozen
counters were re-run on the landed commit: `census/round-29/c3-integrity.py`
reports `legs=9 fail=0`, `gate "entries=2 ok=2 slice_verdicts=8 slice_total=8
fail=0"`, `rows=143`, `coverage "grounded=15 mapped=15 dangling=0 mismatches=0"`.
Findings 1, 2, 4 and 6 are therefore **still open against committed bytes**;
this file is the L1's input for any append-only follow-up, not a retraction.

---

## Pattern 1 — Identity-before-content: the existing guard and statx disagree on the *encoding* of "device"

**Existing entry side.** The entry's rule is stated as "distinct `stat -c '%d:%i'`"
(`corpus/knowledge/dupe-finders-detect-then-act.md:34`), with the pairing
rationale in the same bullet: "`cmp` byte equality (not a hash) between candidate and a designated original".

**New source side.** statx(2) exposes the same two facts as *separate,
split* fields, not one packed number: "The inode number of the file."
(`census/round-29/sources/statx.2.html` § DESCRIPTION, `stx_ino`) and
"The device on which this file (inode) resides."
(`census/round-29/sources/statx.2.html` § DESCRIPTION, `stx_dev_major`/`stx_dev_minor`).

**The contradiction, stated exactly.** A receipt key written from the lane's
existing guard and a receipt key written from statx are **not the same string
for the same file**. `stat(1)` prints "device number in decimal (st_dev)" —
one packed scalar — while statx prints the pair. Measured on one file this run
(scratch `/var/tmp/souji-r29-SwarmConnector64`, `stat -c '%d:%i  %Hd:%Ld:%i'`):
`32:54035245  0:32:54035245`; statx via the same file reported
`0:32:54035245  nlink=1 mnt_id=33`. Same underlying quantity, two different
byte strings.

**Why it matters here.** The landed
`corpus/knowledge/duplicate-verdict-identity.md:30-31` claims the lane's guard
"is that (device, inode) pair" and marks it
`[INFERENCE: stat(1) was not opened this run, so the `%d` = device-number
mapping is not quote-backed here]`. This run opened stat(1), so the inference
can be closed — but with a correction, not a confirmation: stat(1) also offers
`%Hd`/`%Ld` for major/minor (its § DESCRIPTION format list: "major device number in decimal"
and "minor device number in decimal"), and it is `%Hd:%Ld:%i`, not `%d:%i`,
that is byte-comparable with a statx-derived key. The F3 identity entry should
quote the *fields*, not assert the *strings* are interchangeable.

**Status against the landed commit.** Still open. The landed entry carries the
`[INFERENCE: ...]` marker verbatim at `:31` and its Lane link (`:67-71`) says
the entry "grounds the identity leg of that requirement in S216/S218" — but
the identity leg it grounds is the *field set*, and the *encoding* the lane
actually uses (`%d:%i`) is still unbacked. The landed commit's own
`c3-integrity.py` L8 novelty leg passes on this entry
(`identity_has=['stx_nlink', 'stx_ino']`), so this finding is not a counter
defect — it is a statement in the committed prose that a later reader could
take for a quote-backed claim when it is explicitly marked as an inference.

**Pattern verdict.** Complementary gap with a contradiction inside it: the new
source grounds the *pair*; it does not ground the existing *encoding*.

---

## Pattern 2 — Is a hard-link pair a "duplicate"? Four sources answer four different ways

This is the sharpest disagreement across the whole corpus, and it is the one the
existing entry does not record.

| source | verdict on a hard-link pair | quote |
|---|---|---|
| rmlint (existing entry's S016) | **duplicate by default** | "Hardlinked files are treated as duplicates by default" (`rmlint.1.rst:327`) |
| fdupes (S019) | **not** a duplicate by default | "Normally, when two or more files point to the same disk area they are treated as non-duplicates" (`fdupes.1:33`) |
| jdupes (S018) | **not** a duplicate by default | "linked files are treated as non-duplicates for safety" (jdupes `README:118`) |
| fclones (S020/S021) | **collapsed, not duplicated** | "In each group, remove duplicate files with the same inode id." (`fclones/README.md:403`) |
| cmp(1) (S219, new) | **"same"** — exit 0 | "Exit status is 0 if inputs are the same, 1 if different, 2 if trouble." (`census/round-29/sources/cmp.1.html` § DESCRIPTION) |
| link(2) (S218, new) | **one file, two names** | "both names refer to the same file" (`census/round-29/sources/link.2.html` § DESCRIPTION) |
| statx(2) (S216, new) | **one file, nlink counts the names** | "The number of hard links on a file." (`census/round-29/sources/statx.2.html` § DESCRIPTION, `stx_nlink`) |

**Contradiction, not a scalar.** rmlint's *default* says a hard-link pair is a
duplicate; fdupes and jdupes' *defaults* say it is not; fclones removes the
pair from the group rather than calling it a duplicate; `cmp` reports "same"
(byte-identical) without any notion of file multiplicity; link(2) and statx(2)
say there is only one file. These are not degrees of one answer — the
"duplicate" word denotes different objects in each column.

**What the lane already decided.** The existing entry's own guard settles it
for souji, and agrees with the fdupes/jdupes/fclones majority and with
link(2)/statx(2): "distinct `stat -c '%d:%i'`"
(`corpus/knowledge/dupe-finders-detect-then-act.md:34`) — a hard-link pair is
*not* two candidates. rmlint's default is the outlier and the entry does not
say so.

**Complementary gap in the existing entry.** It never mentions rmlint's
`--hardlinked` default at all — `grep -c 'hardlinked\|--keep-hardlinked' corpus/knowledge/dupe-finders-detect-then-act.md` → `0`
(run at lane base). A reader of the existing entry would conclude that
hard-link handling is settled, when the maintained tool it cites most heavily
defaults the other way.

---

## Pattern 3 — Three-valued verdicts: `cmp`'s third outcome, and statx's third outcome, are both missing from the existing rule

**New source side.** cmp(1): "Exit status is 0 if inputs are the same, 1 if different, 2 if trouble."
(`census/round-29/sources/cmp.1.html` § DESCRIPTION).

**Existing entry side.** The entry's rule reads "`cmp` byte equality (not a hash) between candidate and a designated original"
(`corpus/knowledge/dupe-finders-detect-then-act.md:34`) — a **two-valued**
predicate — and the lane's own live use of it is two-valued: "`cmp` shows differing from the live file"
(`SKILL.md:86`, in the `Superseded-snapshot drift` error pattern).

**The consequence, concretely.** `cmp` exit 1 ("different") and exit 2
("trouble") are the same non-zero value to a shell. A receipt that records
*not equal* from a non-zero exit cannot tell *the copy differs* from *the copy
could not be read*. Measured this run, GNU diffutils 3.12: missing operand →
rc=2; directory operand → rc=2; unreadable operand → rc=2; differing bytes →
rc=1. `trouble` is reachable, not hypothetical — and the manual does not
enumerate it, so the lane must classify it deliberately.

**The parallel third state on the identity side.** statx(2) has its own
*cannot-tell*: the kernel "simply informs the caller which values are supported by this kernel and filesystem via the statx.stx_mask field"
(`census/round-29/sources/statx.2.html` § DESCRIPTION, `stx_mask`), and
"the kernel may return fields that weren't requested and may fail to return fields that were requested"
(same section). So the identity half is three-valued too — present / mask-bit
absent / syscall error — and the existing entry's "distinct `stat -c '%d:%i'`"
has no third state at all: when `stat` fails the shell substitution is the
**empty string** (measured: `stat -c '%d:%i' /nonexistent/path` → empty), so
two failed stats compare *equal*.

**Pattern verdict.** The new sources make the lane's rule three-valued on both
halves; the existing rule is two-valued on both, and the lane's live SKILL.md
use is two-valued.

---

## Pattern 4 — `cmp`'s operand and option contract is the un-recorded half of the existing rule

The existing entry requires "`cmp` byte equality (not a hash) between candidate and a designated original"
(`corpus/knowledge/dupe-finders-detect-then-act.md:34`). Neither the existing
entry nor either staged new entry records what `cmp` does with the operands it
is handed. From the new source, cmp(1) § DESCRIPTION:

- "If a FILE is '-' or missing, read standard input." — so `cmp "$A"` with
  the second argument unset **does not fail**; it compares `$A` against stdin.
  Measured this run: `printf 'hello\n' | cmp a.txt` → **rc=0** ("same"), and
  `cmp a.txt < /dev/null` → rc=1 with the diagnostic `EOF on '-' which is
  empty`. A receipt that shells out with an unset variable can certify
  equality against whatever was on stdin.
- "The optional SKIP1 and SKIP2 specify the number of bytes to skip" and
  "compare at most LIMIT bytes" (`-n`/`--bytes`) — a *bounded* comparison is
  not file equality. Measured this run: files differing at byte 6 give
  `cmp a.txt c.txt` → rc=1, but `cmp -n 5 a.txt c.txt` → **rc=0**. The exit
  contract is identical; the verdict is not whole-file equality.

**Pattern verdict.** Complementary gap, both halves. The staged
`duplicate-verdict-byte-equality.md` correctly records the three exit values
and correctly says the page "does not enumerate what trouble covers" (that
sentence is in `deliver-duplicate-verdict-byte-equality.md:21-22`), but it
does not record the operand contract — and the operand contract is where the
existing rule is silently satisfiable by a wrong comparison.

---

## Pattern 5 — Thresholded vs exact: the corpus has three verdict families and the existing entry names two

- **Exact byte predicate** (new): cmp(1) "Compare two files byte by byte."
  (`census/round-29/sources/cmp.1.html` § DESCRIPTION). No threshold, no
  tolerance — one bit of difference is a difference.
- **Graded, thresholded** (new): Broder defines two measures, "resemblance r(A, B) and their containment c(A, B)"
  (`census/round-29/sources/broder97resemblance.txt` § Abstract), each "a number between 0 and 1"
  (same file § 2) — and one threshold already split his corpus in two:
  "2.1 million clusters contained only identical documents"
  (`census/round-29/sources/broder97resemblance.txt` § 1).
- **Probabilistic, hash-gated** (existing entry's tools, S016–S021): rmlint's
  default matching is a hash — "Use ``-p`` if you want byte-by-byte comparison without any hashing."
  (`rmlint.1.rst:194`); jdupes' byte-for-byte failsafe is the thing `-Q` skips,
  so hash-only comparison is a *documented, selectable* weaker verdict.

**Existing entry side.** It names two of the three: hash-vs-byte
("Default matching is a hash (blake2b); byte-by-byte only with `-p`",
`corpus/knowledge/dupe-finders-detect-then-act.md:9`) and the exact
("`cmp` byte equality (not a hash)", `:34`). The graded family is absent.

**Pattern verdict.** Complementary gap. The new sources complete the ladder
from hash-equal (probabilistic) through byte-equal (exact) to
similarity-at-a-threshold (graded). Note the honesty constraint the staged
byte-equality entry already states correctly: the graded family is document
similarity over token sets and is **not** filesystem byte equality — it is
vocabulary for a different class, and its threshold is a parameter the operator
chooses.

---

## Pattern 6 — The symlink semantics of the identity guard: `stat -c`, statx and `cmp` answer three different questions

**This is the most consequential disagreement, and it is invisible in prose.**

**Existing entry side.** The guard is "distinct `stat -c '%d:%i'`" and it
carries a second, separate clause: "no symlink component"
(`corpus/knowledge/dupe-finders-detect-then-act.md:34`).

**Measured this run** (GNU coreutils `stat` 9.x on this host, GNU diffutils
3.12 `cmp`, statx via libc):

| tool | symlink path `l1` → regular file `a.txt` |
|---|---|
| `stat -c '%d:%i' l1` | `32:54035725` — the **link's own** inode (`%F` = `symbolic link`) |
| `stat -L -c '%d:%i' l1` | `32:54035245` — the **target's** inode |
| statx, default flags | `l1 ino=54035245 mode=100644` — the **target's** inode (follows) |
| statx, `AT_SYMLINK_NOFOLLOW` | `l1 ino=54035725 mode=120777` — the **link's own** inode |

statx's default is `AT_STATX_SYNC_AS_STAT` — "Do whatever stat(2) does. This is the default"
(`census/round-29/sources/statx.2.html` § DESCRIPTION), and stat(2) follows
symlinks; the non-following behaviour is opt-in:
"If path is a symbolic link, do not dereference it: instead return information about the link itself"
(same section, `AT_SYMLINK_NOFOLLOW`). The lane's existing `stat -c '%d:%i'`
behaves like `AT_SYMLINK_NOFOLLOW`, **not** like statx's default.

**And `cmp` follows too.** Measured: `cmp l1 l2` where `l1`→`a.txt` and
`l2`→`c.txt` and the two *targets* differ at byte 6 → rc=1 ("differ"), while
`cmp` on two symlinks to equal-content targets → rc=0. So the byte oracle and
the identity guard can disagree about whether two paths name the same thing.

**Contradiction with link(2).** link(2) goes the *other* way from statx: for
`linkat`, "does not dereference oldpath if it is a symbolic link"
(`census/round-29/sources/link.2.html` § DESCRIPTION, `AT_SYMLINK_FOLLOW`
paragraph) — so the two new kernel sources disagree with each other on the
default. statx follows by default; linkat does not.

**Pattern verdict.** Contradiction across the new pair plus a hidden one
against the existing entry. A re-implementation of the lane's existing
`stat -c '%d:%i'` guard on statx's **default** flags silently changes the
guard's answer on every symlinked path. The identity entry's own "no symlink
component" clause — the one the existing entry states and the staged entry
does not restate — is exactly the clause this breaks.

**Status against the landed commit.** Still open, and now slightly sharper.
The landed `corpus/knowledge/duplicate-verdict-identity.md:69` *does* restate
the clause in its Lane link — "distinct `stat -c '%d:%i'` (no symlink component)" —
so the clause is present in committed bytes. But the landed entry grounds the
identity leg in S216/S218 without recording that the two kernel sources it
cites disagree on dereferencing by default, and without recording that
statx's default is the *dereferencing* one. A reader who implements the
landed entry's identity rule on statx's default flags gets a guard that
follows symlinks — the opposite of the clause the same entry quotes.

---

## Pattern 7 — Which existing-entry statements the new sources better ground (append-only link-note candidates)

The L1 asked for the statements that become better grounded by the new sources.
Ordered by how much the grounding changes them:

1. **`corpus/knowledge/dupe-finders-detect-then-act.md:34` — "distinct `stat -c '%d:%i'`"**.
   Better grounded by statx's split fields (`stx_ino`; `stx_dev_major`/`stx_dev_minor`)
   and by link(2)'s "both names refer to the same file" — *and corrected* by
   Pattern 1: the lane's `%d` is the packed `st_dev`, not the statx pair.
   Pattern 6 adds the condition the entry states in prose ("no symlink
   component") that the field set does not enforce.
2. **`:34` — "no symlink component"**. Now grounded by a *named flag*
   (`AT_SYMLINK_NOFOLLOW`) rather than a prohibition, and shown to conflict
   with statx's default. This is the strongest append-only link-note candidate:
   one clause, one kernel flag, one measured divergence.
3. **`:34` — "`cmp` byte equality (not a hash)"**. Now grounded as a primary
   source instead of a convention ("Compare two files byte by byte.",
   cmp(1)), and *extended* by the third exit value (Pattern 3) and the operand
   contract (Pattern 4) that the two-valued phrasing hides.
4. **`:34` — "a recorded original that is never the removal target"**. Now
   grounded by link(2): "it is impossible to tell which name was the "original""
   (`census/round-29/sources/link.2.html` § DESCRIPTION) — so "original" is a
   *declared policy choice*, not a fact recoverable from the filesystem. The
   staged identity entry says this ("which name is the original cannot be
   recovered from the inode"); the existing entry asserts the requirement
   without the reason.
5. **`:26` (failure case) — fdupes `-H` turns the inode check off**. Grounded
   further by rmlint's own caution that the check "automatically filters out path doubles"
   (rmlint cautions, § Path Doubles) and by Pattern 2: the check being turned
   off is exactly what turns one file into two candidate duplicates under
   rmlint's default semantics.
6. **`:9` — "Default matching is a hash (blake2b); byte-by-byte only with `-p`"**.
   Better grounded by Pattern 5 as the *middle* of a three-family ladder, not
   the only alternative to byte-equality.

**One statement the new sources do NOT ground.** `:34` — "a second `cmp` at act time".
Neither cmp(1) nor link(2) nor statx(2) says anything about act-time
re-checking; the staged byte-equality entry states this correctly ("No act-time
guarantee"). The act-time requirement stays grounded, as it is today, in the
dupe-finder sources (jdupes' change checks, fclones' `modified_before`). Any
link note should say so rather than let the new sources appear to cover it.

---

## Not proposed (scope discipline)

- No third knowledge entry, no `ground: F3` line, no SOURCES row — the
  preregistration admits exactly two entries and four rows (S216–S219). The
  landed commit already has `ground: F3` entries = 2 and rows = 143; this note
  changes neither.
- No change to any frozen counter, predicate, target, control or case set.
- No edit to `corpus/knowledge/dupe-finders-detect-then-act.md`: the
  append-only link note is a *recommendation to the L1*, not a landed edit.
- **Two staged identity variants existed**
  (`deliver-duplicate-verdict-identity.md` and `deliver-entry-identity.md`)
  with different `source:`/front-matter and different claim wording. The L1
  landed the `deliver-entry-identity.md` variant (it is the one whose
  front matter names `stx_dev_major`/`stx_dev_minor` and whose `:31` carries
  the `[INFERENCE: ...]` marker this note addresses in Pattern 1). The
  collision is resolved; Pattern 1's correction applies to what landed.

## What the L1 can act on, in priority order

1. **Pattern 6** — the symlink-dereference divergence. One clause
   (`duplicate-verdict-identity.md:69`'s "no symlink component"), one kernel
   flag (`AT_SYMLINK_NOFOLLOW`), one measured divergence. Highest value per
   byte: the entry's own quoted clause is not enforced by the field set it
   grounds.
2. **Pattern 1** — the `%d` vs `stx_dev_major`/`stx_dev_minor` encoding. The
   landed entry already marks this as an inference, so closing it is additive,
   not a rewrite.
3. **Pattern 4** — `cmp`'s operand contract. The landed byte-equality entry
   records the three exit values but not the operand contract; the contract is
   where the existing rule is satisfiable by a wrong comparison.
4. **Pattern 2** — rmlint's `--hardlinked` default versus the other three
   tools' defaults, and its absence from the held entry.
