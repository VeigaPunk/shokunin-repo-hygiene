source: S219 — cmp(1), GNU diffutils 3.12.26-bbc1 (August 2026), as served by man7.org — https://man7.org/linux/man-pages/man1/cmp.1.html — § DESCRIPTION, byte-by-byte comparison and the exit-status sentence
source: S218 — link(2), Linux man-pages 6.19 (page dated 2026-02-11) — https://man7.org/linux/man-pages/man2/link.2.html — § DESCRIPTION
source: S217 — A. Z. Broder, On the resemblance and containment of documents, SEQUENCES 1997 — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf — Abstract, § 1 Introduction
verified-at: 2026-10-25 — all three opened this run; cmp.1.html sha256 5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3, link.2.html sha256 9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9, Broder PDF sha256 da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b with its plain `pdftotext` decode sha256 3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d
recheck: 365d — re-fetch the two man7 pages and the Broder PDF, compare the four sha256 values above, then re-read § DESCRIPTION and the two named Broder sections; re-read the exit-status sentence on a diffutils release
ground: F3 — duplicate verdicts

# Byte equality has a documented three-valued oracle, and it is not a threshold

## Claim (F3, sourced)

F3's frontier item is the operator decision that would create a `duplicate`
receipt class. This entry supplies the primitive the byte-identical half of that
decision is stated against, and leaves the threshold where it belongs.

1. **The primitive is documented, and it has three outcomes, not two.** `cmp`
   is described as "Compare two files byte by byte." (§ DESCRIPTION, first
   paragraph), and the same section closes with "Exit status is 0 if inputs are
   the same, 1 if different, 2 if trouble." So the lane's byte-equality rule is
   a documented oracle rather than a convention, and *trouble* is a third
   outcome the contract distinguishes from *different*. The page does not
   enumerate what trouble covers — that an unreadable, unopenable or
   I/O-failing input lands in exit 2 is `[INFERENCE]` from the tool's contract,
   not a quoted enumeration. The consequence is not an inference: a verdict
   that recorded exit 2 as "different" would report a non-duplicate the oracle
   never asserted, silently promoting an unreadable file into the removal
   candidates.
2. **The lane already requires that primitive.** The prose rule and the entry it
   points at both demand `cmp` byte equality before a copy is called a
   duplicate (`SKILL.md:85-86`; `corpus/knowledge/dupe-finders-detect-then-act.md:34`).
   That rule was a working convention; with S219 it rests on a primary source.
3. **Byte equality is a predicate over files, not over paths.** `link(2)` says a
   second name for an existing file "may be used exactly as the old one for any
   operation" and that "both names refer to the same file". Two paths can
   therefore be one file, and a byte comparison between them compares a file
   with itself. The companion entry
   (`knowledge/duplicate-verdict-identity.md`) holds the statx(2) fields that
   decide this; this entry does not restate them.
4. **The near-duplicate class is a different object.** Broder defines two
   measures, resemblance and containment, each a number in [0,1], "that seem to
   capture well the informal notions of "roughly the same" and "roughly
   contained."" In his own web-crawl experiment a single chosen threshold — 50%
   resemblance — already produced two populations: clusters that held only
   identical documents, and clusters holding a mixture of exact duplicates and
   similar documents. The threshold is therefore a parameter someone chooses,
   and resemblance/containment stay vocabulary for a later near-duplicate
   class. This entry proposes no value for it.

## What this does NOT establish

- **No threshold and no receipt class.** Neither a resemblance value, an
  admission of containment, nor a `duplicate` receipt class is created, changed
  or implied here. That ruling stays with the operator.
- **No near-duplicate method.** `cmp` compares bytes; it has nothing to say
  about documents that are similar but unequal, which is exactly why the two
  Broder measures exist.
- **No failure taxonomy.** Exit 2 collapses every failure into one value; the
  manual does not say which input failed, or why, and a receipt that needs that
  distinction cannot get it from the exit status alone.
- **No separate EXIT STATUS section.** This page's sections are NAME, SYNOPSIS,
  DESCRIPTION, AUTHOR, REPORTING BUGS, COPYRIGHT, SEE ALSO and COLOPHON; the
  exit contract lives in one § DESCRIPTION sentence. A citation to an
  `EXIT STATUS` section of `cmp(1)` would name a section that does not exist.
- **No act-time guarantee.** The oracle is a single comparison; it says nothing
  about a file changing between comparison and removal. The act-time re-check
  required by `dupe-finders-detect-then-act.md` is untouched.
- **Nothing superseded.** No existing entry, row or tool statement is replaced.

## Lane link

- `SKILL.md:85-86` (§ Error patterns, "Superseded-snapshot drift") already makes
  `cmp` the discriminator between a duplicate and a stale snapshot: a config
  copy "claimed "byte-identical"" that "`cmp` shows differing from the live
  file" is a stale *snapshot*, not a duplicate. S219 is the primary source for
  the word that paragraph leans on.
- `corpus/knowledge/dupe-finders-detect-then-act.md:34` requires, for any future
  duplicate verdict, "`cmp` byte equality (not a hash) between candidate and a
  designated original" plus "a second `cmp` at act time". This entry grounds the
  first clause only; the identity guard, the designated original and the
  act-time re-check stand unchanged.
- `knowledge/duplicate-verdict-identity.md` is the companion entry: it holds the
  inode / link-count rule (S216, S218) and the same two-axis vocabulary (S217).
  The two entries are one ruling — identity decides *what* is compared, this
  entry decides *how*.
- Coverage map: the `corpus/README.md` F3 row names this entry. F3 remains a
  frontier row; the class is still an operator decision, not a delivered
  capability.

## Gate

url: https://man7.org/linux/man-pages/man1/cmp.1.html
url: https://man7.org/linux/man-pages/man2/link.2.html
url: https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf
snapshot: census/round-29/sources/cmp.1.html
snapshot: census/round-29/sources/link.2.html
snapshot: census/round-29/sources/broder97resemblance.pdf
snapshot: census/round-29/sources/broder97resemblance.txt
opened: 2026-10-25

- S219, cmp(1) § DESCRIPTION first paragraph — "Compare two files byte by byte." — reason: the comparison's unit is the byte, not a digest — snapshot: census/round-29/sources/cmp.1.html
- S219, cmp(1) § DESCRIPTION closing paragraph — "Exit status is 0 if inputs are the same, 1 if different, 2 if trouble." — reason: three outcomes, with trouble distinguished from different — snapshot: census/round-29/sources/cmp.1.html
- S218, link(2) § DESCRIPTION hard-link paragraph — "This new name may be used exactly as the old one for any operation; both names refer to the same file" — reason: two names can name one file, so equality is predicated on files — snapshot: census/round-29/sources/link.2.html
- S217, Broder § Abstract — "resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of “roughly the same” and “roughly contained.”" — reason: the near-duplicate vocabulary is two named measures, not one label — snapshot: census/round-29/sources/broder97resemblance.txt
- S217, Broder § 1 Introduction, Alta Vista clustering paragraph — "2.1 million clusters contained only identical documents (5.3 million documents). The remaining 1.5 million clusters contained 7 million documents" — reason: one chosen threshold already yields two populations, so the value is a parameter — snapshot: census/round-29/sources/broder97resemblance.txt

- ADMIT: `duplicate-verdict-byte-equality.md` (this entry) — reason: grounds the byte-equality half of F3 in the documented three-valued oracle and the link(2) identity sentence, both quoted verbatim from committed snapshots, and supersedes nothing.
- ADMIT: `duplicate-verdict-identity.md` (companion) — reason: holds the inode/link-count rule this oracle is applied to; the two are admitted as one ruling and neither supersedes an entry.
- REJECT: `near-duplicate-relations-r29.md` (staged) — reason: document-similarity relations and the question whether a threshold exists, which this round keeps as vocabulary only; it grounds no byte-equality fact.
- REJECT: `duplicate-receipt-class-decision-r25.md` (staged) — reason: records the lane's own receipt taxonomy and what an operator ruling would have to touch, a decision record rather than a fact about the subject.
