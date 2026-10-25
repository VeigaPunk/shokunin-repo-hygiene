# Slice114 — hand-check of absent-defect register row `souji` / S114

STATUS: PASS

Seat: scout, leaf member (no subagent dispatch). Lane `souji`, round 22 attempt 2 (hyaku), wave 1.
Base revision read only; no lane write outside this report and the named evidence file.
Access date for every fetch/read below: **2026-10-25**.

## Row under test (extracted by the id cell, field 4)

Command (read-only; other lanes' rows not re-parsed):

```
awk -F'|' 'NR>1 && $2 ~ /souji/ && $4 ~ /S114/ {print}' \
  /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
```

Observed, verbatim:

```
| `souji` | round1 | S114 | `payload-absent` | https://git-scm.com/docs/git-prune | `Note that unreachable, packed objects will remain. If this is not desired, see git-repack(1).`<br>`Note that unreachable, packed objects will remain. If this is not desired, see git-repack(1).` | cited source, companion URLs and local artifacts were all checked; the quote is in none of them |
```

This is the same row the committed derived slice carries (`census/round-22/attempt2/quarantine-slice:1` →
`` S114   `payload-absent` ``). The quote is duplicated in the cell; both copies are byte-identical, so the
register counted one sentence twice.

## What was actually executed

| # | Action | Result |
|---|---|---|
| 1 | `curl -sS -D headers -o slice114-git-scm-git-prune.html https://git-scm.com/docs/git-prune` | `HTTP/2 200`, `date: Sun, 25 Oct 2026 06:45:27 GMT`, `last-modified: Fri, 23 Oct 2026 13:46:14 GMT`, 27870 bytes / 1656 lines |
| 2 | `man git-prune \| col -b > slice114-man-git-prune.colb.txt` | 1980 bytes / 65 lines; `/usr/share/man/man1/git-prune.1.gz` owned by **git 2.56.0-1**; `\\" Date: 2026-09-27`, `\\" Source: Git 2.56.0`; `git --version` → `git version 2.56.0` |
| 3 | Whitespace-collapsed containment of the claimed quote in each | **man: True**, **page: False** (page: True only with `git-repack[1]`) |
| 4 | Clause probes for the row's teaches-cell | all four clauses `True` on the fetched page |

Both snapshots saved under the named evidence path and hashed (below). Nothing was committed; the
preregistration allows only the report and the item's evidence file.

## Located span and locator

Exact span, 14 words, whitespace-collapsed, **as it appears in the fetched cited source**:

> Note that unreachable, packed objects will remain. If this is not desired, see git-repack[1].

Locators:

- fetched page: **§ DESCRIPTION, third paragraph**, `slice114-git-scm-git-prune.html:1532-1533`
  (raw: `<p>Note that unreachable, packed objects will remain.  If this is` / `not desired, see <a href='/docs/git-repack'>git-repack[1]</a>.</p>`);
  the page's own banner reads “git-prune last updated in 2.43.0” and “2.43.1 → 2.56.0 no changes”, so it is the current text.
- installed manual: **GIT-PRUNE(1), § DESCRIPTION, lines 22-23** of `col -b` output —
  `Note that unreachable, packed objects will remain. If this is not desired,` / `see git-repack(1).`

## Which source holds the sentence verbatim, and how they differ

**Both hold the sentence.** Under whitespace collapse the two sources differ in exactly one token, the
cross-reference rendering:

| source | rendering of the reference | claimed quote matches? |
|---|---|---|
| installed `man git-prune` (git 2.56.0) | `git-repack(1)` | yes, byte-for-byte after collapse |
| `https://git-scm.com/docs/git-prune` (fetched 2026-10-25) | `git-repack[1]` (anchor text inside `<a href='/docs/git-repack'>`) | no — only with `[1]` |

Line wrapping also differs (page wraps after “This is”; the man page wraps after “desired,”); collapse erases that,
so wrapping is not the discrepancy. The *only* discrepancy is `(1)` vs `[1]`, which is asciidoc's `git-repack[1]`
man-reference form versus the rendered man page's `git-repack(1)`. This is a rendering artifact, not a payload gap.

## Which one supports the row's teaches-cell

The teaches-cell is the campaign row's: `lanes/souji/SOURCES-PROPOSED.md:19` —

> prune runs `git fsck --unreachable` over refs and removes unreachable *unpacked* objects; unreachable packed
> objects remain; `--dry-run` reports without removing

Every clause was probed against the fetched page and is present there:

- `runs git fsck --unreachable` → True (§ DESCRIPTION);
- `prunes the unpacked objects that are also found in packs` → True (§ DESCRIPTION);
- `Do not remove anything; just report what it would remove` → True (§ OPTIONS `-n, --dry-run`);
- `Only expire loose objects older than` → True (§ OPTIONS `--expire <time>`).

The quoted sentence itself carries only the second clause (“unreachable packed objects remain”); it is
`git-repack` that the same paragraph names as the remedy. **The fetched page supports the whole teaches-cell;
the installed man page supports it identically.** Note the campaign's own Gate line for S114 already labels the
quote “installed man page git 2.56.0, § DESCRIPTION” while the row's URL cell names the web page — the register's
ABSENT classification is the downstream cost of that mixed provenance: the checker compared a man-page rendering
against a web-page rendering.

## Verdict

**`accepted` — quote corrected.**

Correction (stated exactly): the sentence is present in the cited source; only the cross-reference must be
written in the form the cited source renders.

- claimed: `… If this is not desired, see git-repack(1).`
- corrected against the cited URL: `… If this is not desired, see git-repack[1].`
- if the row instead cites the installed manual as the quoted artifact (which its Gate label says it does),
  the claimed text is already verbatim and needs no correction.

Not `present`: as written, the claimed string is not verbatim in the *cited* source (the URL), only in the
installed manual. Not `refused`: the payload is not absent; the register's `payload-absent` class is
**contradicted** by the fetch. Not `unverifiable`: the source was reachable (HTTP 200) and was read.

## Snapshots and hashes (sha256)

| artifact | bytes | sha256 |
|---|---|---|
| `slice114-git-scm-git-prune.html` (fetched cited source) | 27870 | `5d3dcd3b6588ce51b3cd0afee20f9a17e9f1f071f768e438244e7320fc34de88` |
| `slice114-man-git-prune.colb.txt` (`man git-prune \| col -b`) | 1980 | `6cd032eddb4c6b6c24c02c3ac1e5d12976b5bb2eb7efda4bc4d66e44c0b3db2e` |
| `slice114-http-headers.txt` | 691 | `a500d30a286148cfcbb49c5af49f818aa57891f6974a011051dc998227e0d008` |
| `slice114-git-prune.txt` (the item's named evidence file) | 3214 | `c6505d6d9f1dccd73cf0670684e769c6f2cf20135c03fd58f809771ce100a3d2` |

Independent corroboration, not copied: the sibling reviewer seat's own fetch
`evidence/rev-git-scm.com_docs_git-prune.html` hashes to the **same** `5d3dcd3b…de88`, i.e. two separate fetches
of `https://git-scm.com/docs/git-prune` on 2026-10-25 returned identical bytes.

## Bounded findings

1. **[observed]** The register's `payload-absent` class for this row is wrong; the sentence is in the cited
   source. The register's own legend says a CANDIDATE is “not a verdict”, which this row confirms.
2. **[observed]** The quote field carries the same sentence twice; the defect counter counted one string twice.
   That inflates the row's quote count, not its row count.
3. **[observed]** The lane's committed registry (`corpus/SOURCES.md`) contains **no** `git-prune` row at all
   (`grep -c git-prune corpus/SOURCES.md` → `0`), and its current `S114` is the statx(2) row
   (`corpus/SOURCES.md:134`). The id re-pointing recorded in `LOG.md:1507-1508` (`S117->S114`) means a reader
   who maps this register id `S114` into the lane registry lands on a different source. The git-prune scope and
   teaches-cell currently live only in `lanes/souji/SOURCES-PROPOSED.md:19` (campaign, read-only here).
4. **[observed]** This sentence is documented in **both** the installed manual and the web page, so no
   citation-class defect arises: the artifact really is the cited URL's content. The residual defect is
   provenance labelling inside the campaign row (URL cell + “quoted (installed man page …)” Gate line), not a
   wrong-source citation like S123's.
5. **[inference, labelled]** Any future checker that compares a `git-repack(1)`-style claim against
   `git-scm.com` HTML will keep producing ABSENT on this row until either the claim uses `[1]` or the checker
   normalizes asciidoc man-reference brackets. The frozen eleven folds evidently do not include that
   normalization; I did not inspect the fold implementation.

## Remaining unknowns

- I did not run `absent-defect-register.py`'s fold set, so I cannot say *which* fold would have caught
  `[1]` vs `(1)`; I only measured that the raw fetch contains `[1]` and the man page contains `(1)`.
- Whether the campaign intends the quoted artifact to be the URL or the installed man page is not decidable from
  the row alone; both readings make the sentence present, differing only in whether a correction is needed.
- Tool installs: none. Nothing was upgraded, installed, or restarted for this seat.
