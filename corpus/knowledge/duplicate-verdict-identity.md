source: S216 — statx(2) — https://man7.org/linux/man-pages/man2/statx.2.html — § DESCRIPTION struct statx (stx_ino, stx_nlink, stx_btime, stx_mnt_id, stx_dev_major/stx_dev_minor); § CONSTANTS STATX_MNT_ID_UNIQUE; § DESCRIPTION stx_mask — Linux man-pages 6.19 (2026-02-08)
source: S217 — A. Z. Broder, "On the resemblance and containment of documents" — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf — Abstract; § 1 clustering experiment; § 2 Definitions as set intersection problems — IEEE SEQUENCES 1997; the registered DOI answers 202 with a zero-byte body (probed 2026-10-25), so the Princeton course mirror is the edition opened here
source: S218 — link(2) — https://man7.org/linux/man-pages/man2/link.2.html — § DESCRIPTION — Linux man-pages 6.19 (2026-02-11)
verified-at: 2026-10-25 — all three opened live this run: statx.2.html sha256 2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e, link.2.html sha256 9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9, Broder PDF sha256 da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b and its plain pdftotext decode sha256 3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d; the DOI probe returned 202 with 0 bytes
recheck: 365d — bash -c 'd=$(mktemp -d /var/tmp/souji-r29-recheck.XXXXXX); curl -fsSL -o $d/statx.2.html https://man7.org/linux/man-pages/man2/statx.2.html; curl -fsSL -o $d/link.2.html https://man7.org/linux/man-pages/man2/link.2.html; curl -fsSL -o $d/broder.pdf https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf; pdftotext $d/broder.pdf $d/broder97resemblance.txt; sha256sum $d/statx.2.html $d/link.2.html $d/broder.pdf $d/broder97resemblance.txt; curl -sS -o /dev/null -w "doi %{http_code} %{size_download}\n" -L https://doi.org/10.1109/SEQUEN.1997.666900; rm -r $d'   # expect 2a47fe31… 9cb197a7… da122799… 3ba1e117…, then doi 202 0
ground: F3 — duplicate verdicts

# Two paths are not two files, and "duplicate" names a family of verdicts

## Claim (F3: duplicate verdicts)

F3's frontier asks what a `duplicate` receipt class would have to record. Three
opened sources fix the identity half of that question and supply vocabulary for
the non-identical half; none of them chooses the class, a threshold or an
original-designation rule.

1. **Path multiplicity is not file multiplicity.** link(2) states that a new name
   for an existing file "may be used exactly as the old one for any operation",
   that both names refer to the same file with the same permissions and
   ownership, and that it is impossible to tell which name was the original
   [S218]. A verdict built on path strings therefore reports two items where the
   filesystem holds one. The comparison has to be made on inode identity, and
   which name is the original cannot be recovered from the inode: it is a policy
   choice the verdict has to declare separately.
2. **The identity fields are separate and countable.** `struct statx` carries the
   inode number (`stx_ino`), the hard-link count (`stx_nlink`), creation time
   (`stx_btime`), the mount id (`stx_mnt_id`) and the device the inode resides on
   (`stx_dev_major`/`stx_dev_minor`) [S216]. The device matters because an inode
   number is only meaningful on its device; the lane's existing guard `stat -c
   '%d:%i'` (`dupe-finders-detect-then-act.md`) is that (device, inode) pair
   [INFERENCE: stat(1) was not opened this run, so the `%d` = device-number
   mapping is not quote-backed here]. The link count turns the duplicate
   question into a count question: one inode with a link count of two is one
   file under two names, not two copies.
3. **Resemblance and containment are vocabulary, not equality.** Broder defines
   two measures, resemblance r(A, B) and containment c(A, B), each a number
   between 0 and 1, offered as capturing "roughly the same" and "roughly
   contained" [S217]. That gives the non-identical half two named axes instead of
   one label: a `duplicate` verdict must say which measure it applies and at what
   threshold. Broder's own clustering at a 50% resemblance produced two
   populations — clusters holding only identical documents, and clusters mixing
   exact duplicates with similar ones — so a single threshold does not yield a
   single kind of verdict.

## What this does NOT establish

- **`stx_btime` is availability-dependent, not guaranteed.** statx clears the
  mask bit for a requested field when the backing filesystem does not support it
  (or the value is unrepresentable) and may fill a dummy value, so
  `STATX_BTIME` can be unset; no claim is made that creation time exists on every
  filesystem this lane touches [S216 § DESCRIPTION stx_mask].
- **`stx_mnt_id` identifies the mount, not the file.** The uniqueness promise
  belongs to `STATX_MNT_ID_UNIQUE`, available only since Linux 6.8, and it is a
  no-reuse guarantee while the system runs — not a stable identity across
  reboots [S216 § CONSTANTS, § DESCRIPTION stx_mnt_id]. A receipt keyed on it
  must record the kernel version it assumed.
- **Broder is document similarity, not byte equality.** The measures are defined
  over documents reduced to token sets in a World Wide Web crawl study;
  resemblance is stated there to be non-transitive. The paper is vocabulary for
  the near-duplicate half and tier-B evidence for it; it says nothing about
  filesystem byte comparison.
- **No receipt class is chosen here.** This entry records what three sources say
  about identity and vocabulary; it does not add a class, a threshold, a
  comparison algorithm or an original-designation rule.

## Lane link

- `corpus/knowledge/dupe-finders-detect-then-act.md` already requires, for any
  duplicate verdict, distinct `stat -c '%d:%i'` (no symlink component), `cmp`
  byte equality against a designated original, and a second `cmp` at act time.
  This entry grounds the identity leg of that requirement in S216/S218 and leaves
  the byte-equality leg to the companion entry `duplicate-verdict-byte-equality.md`
  (S219, admitted by the same ruling). It supersedes no existing entry.
- `PROVINCE.md`:12 puts "duplicate configs" in this lane's scope.
- `SKILL.md`:26 names the receipt taxonomy ("every removal needs exactly one")
  and its table (:35-:37) defines `pushed`, `moved-to-obsidian` and `stale`. No
  `duplicate` class exists, and adding one changes the taxonomy and
  `tools/souji-verify.sh`: PROVINCE F3 therefore stays an OPERATOR decision. This
  entry supplies that decision's vocabulary and identity rule; it does not take
  the decision.

## Gate

opened: 2026-10-25 — the three sources were fetched and opened this run; every
quote below is copied from the bytes named on its own line, is at most 25 words,
and contains no pipe character. Snapshot paths are the round's capture paths
under `census/round-29/sources/`.

- S216 statx(2) § DESCRIPTION, stx_ino and stx_nlink definitions — "The inode number of the file." and "The number of hard links on a file." — https://man7.org/linux/man-pages/man2/statx.2.html — snapshot: census/round-29/sources/statx.2.html
- S216 statx(2) § DESCRIPTION, stx_btime definition and stx_mnt_id paragraph — "The file's creation timestamp." and "If using STATX_MNT_ID_UNIQUE, this is the unique mount ID of the mount containing the file." — https://man7.org/linux/man-pages/man2/statx.2.html — snapshot: census/round-29/sources/statx.2.html
- S216 statx(2) § DESCRIPTION stx_dev_major, line 366 — "The device on which this file (inode) resides." — https://man7.org/linux/man-pages/man2/statx.2.html — snapshot: census/round-29/sources/statx.2.html
- S216 statx(2) § CONSTANTS, line 257 — "Want unique stx_mnt_id (since Linux 6.8)" — https://man7.org/linux/man-pages/man2/statx.2.html — snapshot: census/round-29/sources/statx.2.html
- S216 statx(2) § DESCRIPTION stx_mask, lines 289-290 — "If a filesystem does not support a field or if it has an unrepresentable value" — https://man7.org/linux/man-pages/man2/statx.2.html — snapshot: census/round-29/sources/statx.2.html
- S216 statx(2) § DESCRIPTION stx_mnt_id, lines 382-383 — "It is guaranteed to not be reused while the system is running." — https://man7.org/linux/man-pages/man2/statx.2.html — snapshot: census/round-29/sources/statx.2.html
- S218 link(2) § DESCRIPTION, line 95 — "creates a new link (also known as a hard link) to an existing file." — https://man7.org/linux/man-pages/man2/link.2.html — snapshot: census/round-29/sources/link.2.html
- S218 link(2) § DESCRIPTION, lines 100-101 — "This new name may be used exactly as the old one for any operation" — https://man7.org/linux/man-pages/man2/link.2.html — snapshot: census/round-29/sources/link.2.html
- S217 Broder § Abstract, lines 8-9 — "resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of “roughly the same” and “roughly contained.”" — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf — snapshot: census/round-29/sources/broder97resemblance.txt
- S217 Broder § 1, lines 53-54 — "We calculated our clusters based on a 50% resemblance." — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf — snapshot: census/round-29/sources/broder97resemblance.txt
- S217 Broder § 1, line 57 — "a mixture of exact duplicates and similar" — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf — snapshot: census/round-29/sources/broder97resemblance.txt
- S217 Broder § 2, line 67 — "Definitions as set intersection problems" — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf — snapshot: census/round-29/sources/broder97resemblance.txt

- ADMIT: `corpus/knowledge/duplicate-verdict-identity.md` — reason: grounds the F3 identity rule (inode identity, not path identity) in statx(2) and link(2), and uses Broder only to name the two similarity measures as vocabulary that bounds the byte-identical class — no similarity method, threshold or operating point is adopted, which is why the staged near-duplicate threshold entries below are rejected as document-similarity ground outside F3's byte-identical scope; sources opened, quoted and hash-pinned this round.
- REJECT: the staged package's closing sentence, which points the operator decision at `CANNOT-ANSWER.md` — reason: no such file exists in this lane (`ls CANNOT-ANSWER.md` → No such file or directory at b8cb4b3), so the wording cites a decision record that cannot be located; the operator-decision fact is stated here without that reference.
