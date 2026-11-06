source: S306 (gitattributes(5), https://git-scm.com/docs/gitattributes, `filter` clean command, sha256 0a1e8015…6aee, accessed 2026-11-06); S307 (git(1) OPTIONS `--attr-source`, equivalent to GIT_ATTR_SOURCE, accessed 2026-11-06); S308 (git-config(1) `core.fileMode`, accessed 2026-11-06); S310 (git-config(1) `attr.tree`, outranked by GIT_ATTR_SOURCE); S311 (gitattributes(5) `ident`); host probes census/round-71/probes/attr-filemode-probe-base.txt, attr-filemode-probe-sizechange.txt, stat-granularity-probe.txt (git 2.56.0); controls census/round-71/controls/c1-*.txt; wave evidence census/round-71/records/wave-w1/ (S71Sentinel, S71CriticClaims, S71Reviewer, S71CriticDiscern); counter census/round-71/c1-counter.py frozen at aa91d1cad89200ec733edd3475461010a372923d
verified-at: a1db6c8514771c0a0321c29741831606d09cc2a5 (frozen C1 candidate) and f13d575e2e33cc98ae2c2e72e61557cb5a224591 (wave repairs; frozen counter re-run census/round-71/records/c1-at-repair.txt, writer selftest records/writer-selftest-repair.txt); 2026-11-06, git 2.56.0 on this host
recheck: `python3 -B census/round-71/c1-counter.py --root . --matrix census/round-71/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev <tip> --tool tools/souji-receipt-write.py --work <scratch>` must print `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` and `EXIT=0`; `python3 -B tools/souji-receipt-write.py --selftest --work <scratch>` cases 39-42 pass; on every git release, re-run the three probes and re-fetch S306-S311 against their sha256

# A clean `git status` is not a clean tree when attributes or stat settings say so

A receipt or cleanup tool that decides "the tree is clean" from `git status --porcelain` trusts git's
own comparison of the worktree with the index. Repository-level settings change that comparison
without changing any file the tool looks at.

**Check-in conversions.** gitattributes(5) says "the clean command is used to convert the contents
of worktree file upon checkin" (S306) and that `ident` replaces any `$Id: … $` span with `$Id$`
"upon check-in" (S311). The page does not say that `git status` compares converted bytes; the
probes show that it does (`attr-filemode-probe-base.txt` P3/P4: a size-preserving edit the clean
driver maps back reads as clean, and the round-start writer wrote a receipt). The attribute can come
from a committed `.gitattributes`, from `$GIT_DIR/info/attributes`, from repository-local `attr.tree`
(S310) or `core.attributesFile`, or from a tree the caller names with `GIT_ATTR_SOURCE` (S307:
gitattributes are read "instead of the worktree"; `info/attributes` is still read, measured by
S71CriticDiscern).

**Stat settings.** `core.fileMode=false` (S308: whether "the executable bit … is to be honored")
hides a mode flip. `core.checkStat=minimal` hides a same-second replace by a new inode, and
`core.trustctime=false` hides a later-second in-place edit, when the edit is size-preserving and
restores the mtime (`stat-granularity-probe.txt`).

The size of the edit matters: git's stat check sees a size change before any conversion runs, so a
size-changing edit is reported even under a filter (`attr-filemode-probe-sizechange.txt`), and a CRLF
rewrite under a `text` attribute (P1) is visible. The forgeries need a size-preserving edit, which is
cheap (`v2` for `v1`).

| route | round-start writer | writer now (r71) |
|---|---|---|
| GIT_ATTR_SOURCE tree with `filter=t` + local `filter.t.clean`, forged (P2) or in-run edit (P10) | receipt written | GIT_ATTR_SOURCE scrubbed; the edit is seen (`lane worktree is dirty` / RECEIPT-STATE-CHANGED-DURING-RUN) |
| committed `.gitattributes`, `info/attributes`, `attr.tree` or `core.attributesFile` `filter=t` + local clean or process driver | receipt written | RECEIPT-FILTER-DRIVER-SET before the status read and again after the wrapped command (the post-run check now runs before the post-run status read: an in-run filter that deletes its own attribute while status runs it forged the frozen candidate, S71Sentinel HIGH-1) |
| a driver literally named `set`, `unset` or `unspecified` | receipt written | refused (the frozen candidate exempted these names, S71Reviewer F1) |
| `ident` or a `working-tree-encoding` value on a tracked path | receipt written | RECEIPT-CHECKIN-CONVERSION-SET (S71CriticClaims HIGH) |
| local `core.fileMode=false`, pre-run (P6) or in-run (P7) chmod | receipt written | `-c core.fileMode=true` pinned on every writer git call |
| local `core.checkStat=minimal` / `core.trustctime=false`, size-preserving edit with mtime restored | receipt written | `-c core.checkStat=default -c core.trustctime=true` pinned (S71Sentinel HIGH-2) |
| filter attribute with no configured driver (P5); driver configured but no tracked path carries it (P11); `core.fileMode=false` on an unchanged tree (P8); a `text` attribute | receipt written | still written (a blanket presence refusal over-refuses these: control F1, `new_honest=16` of 19) |

General lesson for this domain: before trusting a clean status as evidence that a tree may be cleaned,
quarantined or receipted, resolve every tracked path's `filter`, `ident` and `working-tree-encoding`
attributes under the tool's own pinned environment, refuse when a conversion can be lossy, pin the
stat settings, and run the attribute check before any status read that would execute a driver.

## What this does not cover

- A size-preserving in-place edit in the same whole second as the last index refresh, mtime
  restored, is invisible to `git status` under any config on this git build (whole-second stat
  comparison, `stat-granularity-probe.txt` rows `*-same-second-inplace`). The writer's clean path
  takes no content snapshot; only `--allow-dirty` fingerprints content.
- Over-refusal: an honest repository with a configured clean driver on a tracked path (an LFS-like
  setup) and a clean tree is refused (S71CriticClaims MEDIUM); no matrix row measures it.
- The frozen r71 matrix measures 7 forgery routes (AS1 AS2 FC1 FC2 FC3 FM1 FM2); the repaired routes in
  the table above are measured by writer selftest cases 41-42 and wave probes, not by the frozen
  counter. AS1/AS2 cannot distinguish a GIT_ATTR_SOURCE scrub from an unfiltered dirty tree
  (S71MutCounter F2).
- Smudge-only drivers (they act on checkout); git releases other than 2.56.0.

## r72: the filter-witness protections as frozen matrix rows (appended 2026-11-06)

The r71 table above lists repairs measured only by writer selftest cases and wave probes. Round 72
puts five of them under the frozen counter (`census/round-72/c1-counter.py`, 75 rows; base slot =
the pre-r71 writer at 8b9345b1, which has no filter witness). Each row forges that base writer and
exactly one single-edit mutant of the current writer, and the current writer refuses all five
with `RECEIPT-FILTER-DRIVER-SET` (`census/round-72/probes/fw-shapes-probe.txt`,
`records/c2-after-battery.txt`; the honest-writer arm `records/c2-honest-writer.txt` shows the
current writer is not over-refused by the 75 rows):

| row | route | which writer check alone sees it | mutant that forges |
|---|---|---|---|
| FWr | forged bytes under a configured driver; the wrapped command restores the committed bytes and unsets the driver | the pre-run witness (post-run there is no driver and a clean tree) | WM3, pre-run refusal deleted |
| FWi | honest tree; the wrapped command forges same-size bytes and creates `info/attributes` plus the clean driver | the post-run witness | WM4, post-run refusal deleted |
| FWp | `filter.p.process` long-running driver, no `clean` key (S313) | the `process` key lookup | WM5, `clean` looked up alone |
| FWw | committed empty `.gitattributes`; the worktree copy filters itself back to empty and assigns the forging driver to a tracked path | a worktree attribute read; the index copy assigns nothing (S312 `--cached` reads the index only; S314 the index copy is a fall-back when the worktree file is missing — outside checkout) | WM8, `check-attr --cached` |
| FWs | a driver literally named `set` | no value exemption | WM6, boolean values exempted |

FWw needs the committed `.gitattributes` to be empty: when the stat data of a size-0 index entry
no longer matches, git checks the content through its filter instead of short-circuiting on the
size (git `read-cache.c` at v2.56.0, located by S72CriticDiscern, not a SOURCES row), so the
self-erasing `filter=e` (`cat >/dev/null`) makes the edited attribute file read as unmodified on
the read that observes the change. Corrected in round 72 after S72CriticDiscern: the first draft
said "on every status read"; a fixture shows filter runs 1/0/0 over three reads 2.2 s apart (later
reads trust the refreshed stat), `census/round-72/records/wave-w1/seats/S72CriticDiscern/size0-receipt.txt`. A non-empty committed copy with a
different-size worktree edit is reported as modified (stat size check, same receipt, shape C) and
needs no attribute witness.

Still not covered by any row: a `check-attr` failure that the writer would treat as fail-open
(no reachable failure was found, r71 S71MutWriter W7); an honest repository with a configured
driver on a tracked path (over-refused); smudge-only drivers; git releases other than 2.56.0.
