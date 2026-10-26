source: S216 — statx(2), Linux man-pages 6.19 (2026-02-08) — https://man7.org/linux/man-pages/man2/statx.2.html — § DESCRIPTION struct statx, § CONSTANTS STATX_MNT_ID_UNIQUE
source: S217 — A. Z. Broder, On the resemblance and containment of documents, SEQUENCES 1997 — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf — Abstract, § 2 Definitions as set intersection problems
source: S218 — link(2), Linux man-pages 6.19 — https://man7.org/linux/man-pages/man2/link.2.html — § DESCRIPTION
verified-at: 2026-10-25 — three sources opened live 2026-10-25 (statx.2.html sha256 2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e, link.2.html sha256 9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9, Broder PDF sha256 da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b with its decoded text sha256 3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d); the registered DOI answered 202 with a zero-byte body
recheck: 365d — re-fetch both man7 pages and the Broder PDF, compare sha256 against the values above, then re-read the named sections; probe the DOI with `curl -sS -o /dev/null -w '%{http_code} %{size_download}' -L https://doi.org/10.1109/SEQUEN.1997.666900` and expect 202 0
ground: F3 — duplicate verdicts

# Two paths are not two files, and "duplicate" names a family of verdicts

## Claim (F3: duplicate verdicts)

F3 asks what a `duplicate` receipt class would have to record. The identity half
is fixed by two manual pages; the vocabulary for the non-identical half comes
from a document-similarity paper and is vocabulary only.

1. **Path multiplicity is not file multiplicity.** `link(2)` states that a new
   name for an existing file can be used exactly as the old one, that both names
   refer to the same file, and that no name is the original. A verdict built on
   path strings therefore reports two items where the filesystem holds one; the
   comparison has to be made on inodes.
2. **The identity fields are separate and countable.** `statx(2)`'s
   `struct statx` carries the inode number and the hard-link count as distinct
   fields (`stx_ino`, `stx_nlink`), beside creation time (`stx_btime`) and mount
   id (`stx_mnt_id`, with `STATX_MNT_ID_UNIQUE` since Linux 6.8). The link count
   turns "is this a duplicate" into a count question: one inode with a link
   count of two is one file under two names, not two copies.
3. **The near-duplicate vocabulary is two measures, not one label.** Broder
   defines resemblance and containment as two separate quantities that seem to
   capture well the informal notions of "roughly the same" and "roughly
   contained". Because there are two quantities, "duplicate" is a thresholded
   family of verdicts rather than a single predicate: a receipt class must name
   its measure and the threshold it applies to that measure.

## What this does NOT establish

- Broder's measures are defined over **documents** reduced to token sets, in a
  World Wide Web crawl study; they say nothing about filesystem byte equality,
  which is the byte-equality half's subject (S219). It is tier B for that reason.
- `stx_btime` support is **filesystem-dependent**, and fields may be absent; no
  claim is made that creation time is available on every filesystem this lane
  touches.
- `stx_mnt_id` identifies the **mount**, not the file, and its uniqueness
  guarantee dates from Linux 6.8; a receipt keying on it must record the kernel
  version it assumed.
- **No receipt class and no threshold are created here.** The class remains an
  operator decision, and the three things a ruling would have to state are not
  enumerated by this entry.
- The identity rule alone does not prove byte equality; `knowledge/dupe-finders-detect-then-act.md`
  still requires both the inode guard and byte equality, and still requires the
  re-check at act time.

## Gate

opened: 2026-10-25 — the four probe rows S216, S217, S218 and S219 were opened
this round; this entry cites three of them and the byte-equality entry cites the
fourth.

- S216, statx(2) § DESCRIPTION struct statx — "stx_ino; /* Inode number */" and "stx_nlink; /* Number of hard links */" — https://man7.org/linux/man-pages/man2/statx.2.html — snapshot: census/round-29/sources/statx.2.html
- S217, Broder § Abstract — "resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of “roughly the same” and “roughly contained.”" — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf — snapshot: census/round-29/sources/broder97resemblance.txt (decoded text of the same PDF; the decode's sha256 is 3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d)
- S218, link(2) § DESCRIPTION — "This new name may be used exactly as the old one for any operation" — https://man7.org/linux/man-pages/man2/link.2.html — snapshot: census/round-29/sources/link.2.html

- ADMIT: `duplicate-verdict-identity.md` — reason: grounds F3's identity rule (inode, not path) and its two-axis vocabulary in three opened sources, each quoted from bytes committed under census/round-29/sources/.
- ADMIT: `duplicate-verdict-byte-equality.md` — reason: the companion entry supplies the byte-equality oracle this entry's rule is applied against; both are admitted by the same ruling, and neither supersedes an entry.
- REJECT: `near-duplicate-threshold-r28.md` — reason: document-similarity ground outside PROVINCE F3's byte-identical scope, and it proposes thresholds where this round admits only vocabulary.
- REJECT: `duplicate-receipt-class-decision-r25.md` — reason: records an operator decision already taken, not a fact about the subject, so it cannot ground a new claim.
