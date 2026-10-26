# SwarmCritic50 — scope critic, both planned F3 entries (round 29, w1)

## Status

STATUS: PASS — scope disposition delivered as a 42-row keep/cut table over both planned
entries and their three staged variants. No scope fault in the core identity or cmp-oracle
claims; 12 rows are OUT (10 plain, plus one entry-level and one not-verbatim quote) — F4
origin-field ground, operator-decision prescriptions, a nonexistent lane file, an out-of-lane
ledger citation, one inverted risk statement — and 8 are BORDERLINE with a named rewrite.

## Evidence

Revision: lane `HEAD` = `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (preregistration commit; lane
base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`). `git status --porcelain` over
`PROVINCE.md SKILL.md corpus/SOURCES.md corpus/QUALITY.md corpus/README.md
corpus/knowledge/dupe-finders-detect-then-act.md` printed nothing, so the line numbers below are
the committed bytes. Entry drafts and snapshots are uncommitted files under
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/`.

```
$ sed -n '5,9p' census/round-29/records/preregistration.txt   # C3 admit set, condensed: line breaks rejoined
... Admit exactly two re-grounded entries: ... duplicate-verdict-identity.md (statx(2)
inode/link-count identity fields, link(2) two names one file, Broder resemblance/containment
as vocabulary only) and ... duplicate-verdict-byte-equality.md (cmp(1) three-valued exit
contract plus the same identity rule; supersedes nothing).
... The Gate records the admit set (two entries, four rows) and at least one reject from the
staged F3-adjacent set (near-duplicate-* entries are document-similarity ground outside
PROVINCE F3's byte-identical scope; duplicate-receipt-class-decision-r25.md records an
operator decision, not a fact).

$ grep -n 'stx_ino\|stx_nlink\|stx_btime\|stx_mnt_id;' .ufo/waves/round-29/w1/sources/statx.2.html
93:               __u32 stx_nlink;       /* Number of hard links */
97:               __u64 stx_ino;         /* Inode number */
106:              struct statx_timestamp stx_btime;  /* Creation */
120:              __u64 stx_mnt_id;      /* Mount ID */

$ grep -n 'new link (also known\|exactly as the old one' .../sources/link.2.html
95:       <b>link</b>() creates a new link (also known as a hard link) to an
100:       This new name may be used exactly as the old one for any

$ grep -n -i 'exit\|trouble' .../sources/cmp.1.html
113:       If a FILE is '-' or missing, read standard input.  Exit status is
114:       0 if inputs are the same, 1 if different, 2 if trouble.
$ grep -n '<h1\|<h2\|NAME\|SYNOPSIS\|COLOPHON' .../sources/cmp.1.html   # section ids, trimmed
NAME SYNOPSIS DESCRIPTION AUTHOR REPORTING_BUGS COPYRIGHT SEE_ALSO COLOPHON   -> no EXIT STATUS

$ sha256sum .../sources/{statx.2.html,link.2.html,cmp.1.html,broder97resemblance.pdf,broder97resemblance.txt}
2a47fe31… 9cb197a7… 5c68e8d8… da122799… 3ba1e117…   (equal to the digests both entries declare)

$ grep -n 'Definitions as set intersection\|50% resemblance\|mixture of exact' .../broder97resemblance.txt
54:a 50% resemblance. We found 3.6 million clusters containing a total of 12.3 million
57:(a mixture of exact duplicates and similar). For further details see [5].
67:Definitions as set intersection problems
$ awk 'NR==53||NR==54||NR==57{print NR": "$0}' .../broder97resemblance.txt
53: engine. The total input data was over 150 Gbytes. We calculated our clusters based on
54: a 50% resemblance. We found 3.6 million clusters containing a total of 12.3 million
57: (a mixture of exact duplicates and similar). For further details see [5].

$ grep -nE '^\s{0,3}\| *S(114|117|118|122|136) *\|' corpus/SOURCES.md   # trimmed to S114
135:| S114 | statx(2), man-pages 6.19 — https://man7.org/linux/man-pages/man2/statx.2.html | docs | A |
 the identity fields a per-item origin record can carry (inode, link count, creation time, mount id) ...
$ sed -n '1,8p' corpus/knowledge/quarantine-origin-record-fields-r24.md
source: S114 — https://man7.org/linux/man-pages/man2/statx.2.html
ground: F4 — restorable quarantine (the read side of a per-item origin record)

$ grep -n 'used-by' tools/souji-registry-agreement.py
56: out.append(f'K1 used-by-missing {i} {p}')
58: out.append(f'K1 used-by-no-cite {i} {p}')

$ find /home/vgpnk/Projects/shokunin/souji-shokunin -maxdepth 2 -name 'CANNOT-ANSWER*'   -> no output
$ ls /home/vgpnk/Projects/shokuknow/lanes/souji/CANNOT-ANSWER.md                          -> exists, outside the lane
$ grep -rn 'operator ruling, not a fact' /home/vgpnk/Projects/shokuknow/lanes/souji/round2
round2/DOMAIN.md:37 | 8 | what are the operator's thresholds for a `duplicate` receipt class |
 **NOT CLOSED** — it is an operator ruling, not a fact ...
round2/CANNOT-ANSWER.md:16  an operator ruling, not a fact to be looked up.**

$ grep -n 'Superseded-snapshot\|Receipt | Qualifies\|`pushed` |\|`stale` |' SKILL.md   # bodies elided
26:## Receipt taxonomy — every removal needs exactly one
33:| Receipt | Qualifies when (as the tool checks it, r6) |
35:| `pushed` | ...   36:| `moved-to-obsidian` | ...   37:| `stale` | ...
85:- **Superseded-snapshot drift**: a config copy claimed "byte-identical" that
```

## Findings

1. **F4 origin-field trespass in the expanded identity draft.** `deliver-entry-identity.md:1`
   (front matter S216 locator), `:25-31` (btime, mnt_id, dev pair, the labelled `%d:%i`
   inference), `:47-56` (btime availability, mnt_id uniqueness and "must record the kernel
   version"), `:90-94` (six extra Gate quotes) import creation-time, mount-id, device and mask
   fields. That ground is
   already held: `corpus/SOURCES.md:135` scopes lane S114 to "the identity fields a per-item
   origin record can carry (inode, link count, creation time, mount id)", and the F4 entry
   `corpus/knowledge/quarantine-origin-record-fields-r24.md:7` reads `ground: F4`. The
   delivered S216 row explicitly excludes that list. Two rows on one URL with overlapping
   scope plus an entry that re-imports the excluded half is duplicate authority.
   Table rows: IDN-FM2, IDN-C2x, IDN-C2y, IDN-WN2, IDN-WN3, IDN-GATE2.
2. **Operator-owned decisions stated as requirements.** `deliver-duplicate-verdict-identity.md:31-32`
   ("a receipt class must name its measure and the threshold it applies to that measure"),
   `:43` ("a receipt keying on it must record the kernel version it assumed"),
   `deliver-entry-identity.md:39-40` ("a `duplicate` verdict must say which measure it applies
   and at what threshold"), `:56`; merge `duplicate-verdict-taxonomy-r24.md:38` ("the three
   things the ruling must state"), `:42` ("a souji receipt would have to record that third
   outcome"). A receipt class is an operator decision (`PROVINCE.md` F3), so prescribing the
   ruling's required content crosses the line. Table rows: IDN-C3x, IDN-WN3, BEQ-WN0, BEQ-WN1.
3. **Nonexistent file cited.** Merge `duplicate-verdict-identity.md:65` ("recorded in
   `CANNOT-ANSWER.md`") and merge `duplicate-verdict-taxonomy-r24.md:38` ("listed in
   `CANNOT-ANSWER.md`"). No such file exists in the lane (sweep above); it exists only at
   `/home/vgpnk/Projects/shokuknow/lanes/souji/CANNOT-ANSWER.md`, a read-only source outside
   the lane. Table rows: IDN-CLOSE, BEQ-WN0, IDN-WN4x.
4. **Out-of-lane ledger citation.** Merge `duplicate-verdict-taxonomy-r24.md:12` cites "the
   round-2 ledger"; the only resolution is
   `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/DOMAIN.md:37` and its
   `CANNOT-ANSWER.md:16`. Not a lane artifact and not opened by any seat this round. Table
   row: BEQ-TITLE0.
5. **One vocabulary claim, two owners.** S217 (Broder) is cited by both entries and the
   axes claim is asserted in both, while prereg C3 gives vocabulary to the identity entry and
   scopes the other to "cmp(1) three-valued exit contract plus the same identity rule". If the
   byte-equality entry drops the Broder claim but the S217 row keeps it in `used-by`, C1 fires
   `K1 used-by-no-cite` (`tools/souji-registry-agreement.py:58`); if it keeps the citation it
   keeps the duplicate claim. The pair must be edited together. Table rows: IDN-C3y, BEQ-C2,
   BEQ-GATE2.
6. **Inverted risk direction.** `deliver-duplicate-verdict-byte-equality.md:26-27` says a
   verdict recording exit 2 as "different" would end in "silently promoting an unreadable file
   into the removal candidates". It would not: "different" yields a non-duplicate, so nothing
   is removed. The false-SAFE hazard is the opposite mapping (2 read as "same"). Table row:
   BEQ-C1x.
7. **Quote-location drift.** Merge `duplicate-verdict-identity.md:24` quotes "containing only
   identical documents"; the snapshot reads "contained only identical documents"
   (`broder97resemblance.txt:55`). `deliver-entry-identity.md:98-100` locators are each one line
   high: the 50 percent sentence spans `:53-54` (cited 54-55), "a mixture of exact duplicates
   and similar" is `:57` (cited 58), "Definitions as set intersection problems" is `:67`
   (cited 68). Table rows: IDN-QUOTE1, plus the locator note inside BEQ-GATE2 and IDN-GATE1.
8. **Landing-order condition.** `deliver-duplicate-verdict-identity.md:62` admits the entries
   because they are "quoted from bytes committed under census/round-29/sources/"; those
   snapshot files are uncommitted today in `.ufo/waves/round-29/w1/sources/` (six files: the
   statx, link and cmp pages, the Broder PDF, its decoded text, and a SHA256SUMS). The reason is
   true only if entries and snapshots land in one commit. Table row: IDN-GATE4.
9. **Verified sound, do not disturb.** cmp quotes verbatim at `cmp.1.html:75` and `:113-114`;
   the page has no EXIT STATUS section (section ids listed above), so the entry's bound is
   correct; link(2) and statx(2) quotes verbatim; all five snapshot digests equal the declared
   values; `SKILL.md:85-86`, `SKILL.md:26`, `SKILL.md:35-37` and
   `dupe-finders-detect-then-act.md:34` resolve as cited. Table rows marked KEEP.

## Attack log

- **Counterexample 1 — risk direction (strongest available).** Take the staged sentence at
  `deliver-duplicate-verdict-byte-equality.md:26-27` and the oracle at `cmp.1.html:113-114`:
  exit 2 means trouble, 1 means different. A verdict that folds 2 into 1 reports
  "non-duplicate", which removes nothing; a verdict that folds 2 into 0 reports "duplicate",
  which is the false-SAFE removal the lane treats as its worst failure. The sentence names the
  safe error as the dangerous one, and it does so inside the entry that exists to pin the
  oracle. Impacted axes: coverage (a false consequence in an admitted entry), calibration (an
  admitted record that does not agree with its own source). Smallest safe correction: state
  both directions or cut the consequence clause (BEQ-C1x).
- **Counterexample 2 — duplicate authority inside the admit set.** Two entries both quoting
  Broder's axes and both listing S217 produce either a doubled claim (scope) or a C1
  `used-by-no-cite` mismatch (calibration) depending on which half is trimmed. Impacted axes:
  coverage, calibration. Correction: vocabulary in the identity entry only; byte-equality
  points at it; S217 `used-by` loses the byte-equality path in the same commit (BEQ-C2).
- **Counterexample 3 — frontier-row collision.** With the expanded identity draft landed, the
  lane would hold S114 and S216 on the same statx(2) URL, an F4 entry citing S114 for origin
  fields, and an F3 entry quoting those same fields. The scope cell of the new row excludes the
  list the new entry uses, so the record contradicts itself. Impacted axes: coverage (map and
  registry agreement), operability none. Correction: cut the fields (IDN-FM2, IDN-C2x).
- **Tradeoff that is not a defect.** Broder's resemblance/containment vocabulary inside the
  identity entry is expressly sanctioned by prereg C3; it should stay bounded, not be cut.
  Cutting it would shrink the declared claim set, which is not mine to do.

## Unrun

No counter was executed by this seat (read-only scope review by contract). The L1 must still
run `tools/souji-gate-check.py`, `tools/souji-coverage-agreement.py`, the C1 agreement counter
and `sources-census.sh validate` at the landing commit, and re-check S217 `used-by` against the
final front matter if BEQ-C2 is applied.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-scope-keep-cut.tsv` — 42 rows, columns
  `entry pid section drafts paragraph class ground action reason correction`; `drafts` codes
  A0 = merge `duplicate-verdict-identity.md`, A1 = `deliver-duplicate-verdict-identity.md`,
  A2 = `deliver-entry-identity.md`, B0 = merge `duplicate-verdict-taxonomy-r24.md`,
  B1 = `deliver-duplicate-verdict-byte-equality.md`. Distribution: IN 22, BORDERLINE 8,
  OUT 12; actions KEEP 22, CUT 13, REWRITE 4, conditional KEEP forms 3.
