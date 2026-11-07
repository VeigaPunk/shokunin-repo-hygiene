source: S306 (gitattributes(5), https://git-scm.com/docs/gitattributes, `filter` clean command, sha256 0a1e8015…6aee, accessed 2026-11-06); S307 (git(1) OPTIONS `--attr-source`, equivalent to GIT_ATTR_SOURCE, accessed 2026-11-06); S308 (git-config(1) `core.fileMode`, accessed 2026-11-06); S310 (git-config(1) `attr.tree`, outranked by GIT_ATTR_SOURCE); S311 (gitattributes(5) `ident`); host probes census/round-71/probes/attr-filemode-probe-base.txt, attr-filemode-probe-sizechange.txt, stat-granularity-probe.txt (git 2.56.0); controls census/round-71/controls/c1-*.txt; wave evidence census/round-71/records/wave-w1/ (S71Sentinel, S71CriticClaims, S71Reviewer, S71CriticDiscern); counter census/round-71/c1-counter.py frozen at aa91d1cad89200ec733edd3475461010a372923d; S312 (git-check-attr(1) `--cached`, r72); S313 (gitattributes(5) long running process filter, r72); S314 (gitattributes(5) attribute-file fall-back, r72); S315 (racy-git.adoc v2.56.0, cached stat information, accessed 2026-11-06, r73); S316 (git-hash-object(1) `--no-filters`, accessed 2026-11-06, r73); r72 counter census/round-72/c1-counter.py and r73 counter census/round-73/c1-counter.py (r72 spot-check D1: the header named only the r71 sources); r74: S317 (gitformat-index(5) at v2.56.0, Index entry, sha256 c8aca940…baa93, accessed 2026-11-06)
verified-at: a1db6c8514771c0a0321c29741831606d09cc2a5 (frozen C1 candidate) and f13d575e2e33cc98ae2c2e72e61557cb5a224591 (wave repairs; frozen counter re-run census/round-71/records/c1-at-repair.txt, writer selftest records/writer-selftest-repair.txt); 2026-11-06, git 2.56.0 on this host; r72: counter 06df4f97c531a05ff2139368f70660c3044f71a6, after-arms 2ec8b63dfda8fdf88cd240487c5d1325de13b501 (census/round-72/records/c2-after-battery.txt, c2-honest-writer.txt); r73: writer b84ff90bff05fb057c5a8c4b0661a9ec41d9e4a2, after-arms 312e8f29d42eac0fd91327d65a6b43a0ba9cc64e (census/round-73/records/c1-after.txt, c2-after-D1..D5.txt), 2026-11-06, git 2.56.0; r74: counter ac57303295371f34befc36d34f78c6715f7341a0, gate ec13ba7fac9085005dca2e69ee12a2933d2c22a5, after-arms 8fe48c863d353da8e26140b132afba00de71ba61, 2026-11-06, git 2.56.0
recheck: `python3 -B census/round-71/c1-counter.py --root . --matrix census/round-71/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev <tip> --tool tools/souji-receipt-write.py --work <scratch>` must print `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` and `EXIT=0`; `python3 -B tools/souji-receipt-write.py --selftest --work <scratch>` cases 39-42 pass; on every git release, re-run the three probes and re-fetch S306-S311 against their sha256; r73: `python3 -B census/round-73/c1-counter.py --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev <tip> --tool tools/souji-receipt-write.py --work <scratch>` must print `SUMMARY matrix=80 base_forgeries=15 base_honest=21 base_mismatches=0 base_unwitnessed=0 new_unwitnessed=0 new_forgeries=0 new_honest=21 class_mismatches=0 new_echo=0 errors=0 regress=PASS` and `EXIT=0`; writer selftest cases 43-44 pass; re-fetch S312-S316 against their sha256 on every git release; r74: `python3 -B census/round-74/c1-gate-counter.py --gate tools/souji-pre-report-gate.sh --work <empty scratch>` must print `SUMMARY rows=9 mismatches=0 errors=0` and `EXIT=0`; `python3 -B census/round-74/c1-counter.py --selftest --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --work <scratch>` must print `fail=0`

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

## r73: the index stat cache, and a counter that checks its own forgeries (appended 2026-11-06)

**A clean `git status` is a stat-cache verdict.** git compares each tracked file's `lstat` result with
the stat information cached in its index entry and reads the contents only when they differ; the
technical note says the shortcut means "Git can incorrectly think files in the working tree are
unmodified even though they actually are" (racy-git.adoc at v2.56.0, S315). So anyone who can write
`.git/index` can make forged bytes read clean: write the forged file, rewrite that entry's stat
fields from the new `lstat` (the blob id stays the committed one), recompute the index checksum and
move the index mtime past the entry so git does not treat it as racily clean
(`census/round-73/probes/fx/idxcraft-run.py`, found by r72 seat S72Sentinel). Before this round both
the reference-weak writer (8b9345b1) and the lane-base writer (a789486d) wrote receipts over that state
before the run, during the run, and on the instrument (`census/round-73/probes/fx-index-stat.txt`,
all three routes FORGERY on both).

**What the writer now checks.** Before the run (after its status read) and after it (after the
post-run reads), every stage-0 tracked regular file that `git status --porcelain -z` does not list is
re-hashed with `git hash-object --stdin-paths`, and every tracked symlink's target is hashed as a
blob, and the result is compared with the object id `git ls-files -s` records. `hash-object` without
`--no-filters` hashes after the attribute-selected check-in conversion (git-hash-object(1): `--no-filters`
means "ignoring any input filter that would have been chosen by the attributes mechanism, including
the end-of-line conversion", S316), so an honest `core.autocrlf=true` file whose worktree bytes are CRLF
still matches (row FXc), where a raw byte comparison would refuse it. Clean/process drivers, `ident`
and `working-tree-encoding` are refused before this point (r71), so the conversion left is end-of-line
only. A difference refuses `RECEIPT-WORKTREE-STAT-CONCEALED`; the instrument is also re-compared with
`rev:path` after the run. Measured with the frozen r73 counter (80 rows): the lane-base writer
`new_forgeries=3` EXIT=1 (`census/round-73/controls/c1-K-a-do-nothing.txt`), the r73 writer
`new_forgeries=0 new_honest=21` EXIT=0 (`records/c1-after.txt`). Paths are fed C-quoted (a line
starting with `"` is unquoted), which writer selftest case 44 exercises with a newline in a file name.

**What the counter now checks about itself.** A counter that scores "the base writer accepted a
refuse row" as a forgery trusts its own fixture to forge. Round 72's S72MutCounter showed that trust
was unchecked: with FWi's forged bytes replaced by the committed ones, the row was still counted. The
r73 counter computes, for each row and slot, the divergence of the fixture worktree from the row's
revision — from `git ls-tree -r` and the raw files, not from git status (which the stat cache can
fool) — before and after the slot runs; an accepted refuse row with no divergence is `unwitnessed`,
enters the verdict (`base_unwitnessed`), and in the battery classifies as `error`, never a kill
(QUALITY Q133). Five defanged rows (`census/round-73/c2-defang.json`) pass the r72 counter (EXIT=0) and
each prints `base_unwitnessed=1` under the r73 counter (`records/c2-after-D1..D5.txt`); the unmutated
matrix prints `base_unwitnessed=0`.

The first bullet of "What this does not cover" above (same-second size-preserving edit with mtime
restored, invisible to git status) no longer holds for the writer's clean path: the bytes are
re-hashed regardless of stat. It still holds for git status itself.

Still not covered: gitlinks and paths git status lists are not re-hashed (the `--allow-dirty` content
snapshot covers listed paths); an in-run change restored before the post-run reads (r63 limit); the
witness reads the worktree only (index, config and other `.git` state are not compared) at two points;
git releases other than 2.56.0.

## r74: the lane's own pre-report gate, and a witness scoped to the row (appended 2026-11-06)

**The gate trusted the stat cache too.** `tools/souji-pre-report-gate.sh` check 4 passed `clean` when
`git status --porcelain` printed nothing — the same stat-cache verdict r73 removed from the receipt
writer (S315). An index entry stores stat(2) fields, an object type and the object name side by side
(gitformat-index(5), S317: "this is stat(2) data 32-bit file size This is the on-disk size from stat(2),
truncated to 32-bit. Object name for the represented object"); status compares the stat fields, so rewriting them over forged bytes keeps the
object name and reads clean. Measured with the frozen gate counter (`census/round-74/c1-gate-counter.py`,
9 rows): the lane-base gate passed three forgeries — a same-size file, a retargeted symlink and a
size-changing file in a subdirectory, each with its entry's stat rewritten (`census/round-74/controls/c1-K-a-do-nothing.txt`,
mismatches=3 EXIT=1).

**What the gate now does.** After an empty status it imports the `souji-receipt-write.py` that sits
beside the gate and calls its `_truth_refusal` on the lane: every stage-0 tracked path status did not list
is compared with the object name its entry records (regular files through `git hash-object --stdin-paths`,
which applies check-in conversion, S316; symlink targets hashed as blobs; gitlinks skipped). A mismatch, a
failed read or a missing writer fails `clean`. One implementation serves both tools. Measured:
`census/round-74/records/c1-after.txt` mismatches=0 EXIT=0; a blanket refusal (mismatches=4, the honest
stale-stat, autocrlf and odd-name rows) and a regular-files-only re-hash (mismatches=1, the symlink row)
stay red (`controls/c1-K-b-blanket-refusal.txt`, `controls/c1-K-c-regular-only.txt`).

**The counter's witness now reads the row's own paths.** r73's witness credited a row with any worktree
divergence; FWw, FC1 and FC2 always write `.gitattributes` during set-up, so with their forgery removed
they still read witnessed (r73 S73ExecC2). The r74 counter keeps only divergences on the row's declared
forged paths (`forge_paths`: the row's `target`, else the path its in-run kind, `chmod_notes` or
`index_stat` writes; none declared = unwitnessed). The pre-freeze probe found every one of the 15
base-accepted refuse rows divergent on its forged path and each defanged row divergent only on
`.gitattributes` (`census/round-74/probes/row-scope-*.txt`). Defanged FWw/FC1/FC2: r73 counter 0 of 3
flagged, r74 counter 3 of 3 (`records/c2-after-D6..D8.txt`), D1..D5 still flagged, unmutated
`base_unwitnessed=0 base_forgeries=15` EXIT=0. The four r73 counter survivors (failed witness read counted
as witnessed, symlink target ignored, gitlink skip removed, new-slot witness pre-run only) now each fail
the counter's selftest (`records/c2-after-M08/M14/M15/M17-selftest.txt`).

Still not covered: the forged-path set is the counter's declaration, so a forgery moved to an undeclared
path reads unwitnessed (an under-witness, never a false kill); the gate inherits whatever check-in
conversion `hash-object` applies (a lying clean filter fools it — the writer refuses those, the gate does
not); gitlinks and listed paths are not re-hashed; the lane's other clean-tree tools
(`tools/souji-verify.sh`, `tools/souji-vault-verify.sh`, `tools/cand-*-verify.sh`,
`tools/souji-record-agreement.py`, `tools/souji-guard.r9-s18.sh`) still trust status; git 2.56.0 only.

## r75: what an ignore rule may hide from the gate, and a second detector for the counter's witness (appended 2026-11-06)

**Status reads every exclude source alike.** `git status` leaves out an untracked file that any exclude
source matches, but the three sources are not the same kind of rule. gitignore(5) distributes `.gitignore`
files with the repository and names the other two as "Patterns read from exclude sources that are outside
the working tree, such as $GIT_COMMON_DIR/info/exclude and core.excludesFile" (S318): neither is ever
committed. Only the committed `.gitignore` files are the lane's declared
policy for untracked artifacts (its own `__pycache__/` rule). Measured with the frozen r75 counter
(`census/round-75/c1-evade-counter.py`, 25 rows: the 20 r74 evasion routes plus five ignore-surface rows,
each with a frozen expected verdict in `census/round-75/c1-population.tsv`): the lane-base gate passed an
untracked file hidden by info/exclude and a whole directory hidden the same way
(`census/round-75/controls/c1-K-a-do-nothing.txt`, mismatches=2 EXIT=1).

**What the gate now does.** Inside the same isolated interpreter, after the byte-truth check, it lists
untracked ignored paths twice: under `--exclude-standard` and under `--exclude-per-directory=.gitignore`
alone. git-ls-files(1) defines the first as the second plus those two sources ("give
`--exclude-per-directory=.gitignore`, and then specify: 1. The file specified by the `core.excludesfile`
configuration variable, if exists, or the `$XDG_CONFIG_HOME/git/ignore` file. 2. The
`$GIT_COMMON_DIR/info/exclude` file.", S319), so the set difference is the untracked content hidden only by a local source; a
non-empty difference fails `clean` (count only, no path). Measured: `census/round-75/records/c1-after.txt`
mismatches=0 EXIT=0 at the gate blob of `1ad737b4`. Refusing every ignored file instead
(`controls/c1-K-b-blanket-ignored.txt`) breaks three honest rows — a committed `.gitignore` rule, a
committed `*.pyc` rule and a self-ignoring tool directory — mismatches=3 EXIT=1. On the lane itself the
two listings are equal (difference 0 at every reading; about 26k paths, growing as ignored wave files land, all under committed rules or `.jj/`), so the lane's own
pre-report run stays green.

**Rulings the counter freezes.** The r74 evasion probe labelled routes by worktree bytes alone, which got
two of them wrong (r74 spot-check routed defect 2): an executable-bit change under `core.fileMode=false`
is a lane change git records in the tree (expected FAIL), and an untracked file hidden by a committed
`.gitignore` line is declared policy (expected PASS).

**Stated limit.** An untracked `.gitignore` that ignores itself (`*`) hides its whole directory as
per-directory policy — the shape jj and ruff write (`.jj/.gitignore`, `.ruff_cache/.gitignore`; about half
of the lane's ignored paths sit under these two, S75CriticDiscern), and the shape a forger could copy. The
gate cannot tell the two apart; row f7 freezes the honest label. The limit is wider than a directory: an
untracked root `.gitignore` listing itself and a payload also leaves status and the difference empty
(S75ScoutSources). A broad committed rule likewise hides whatever it matches (S75CriticClaims).

**The witness counter's selftest has a second detector.** S74MutCounter showed two survivors of the r74
counter: X09 (the new slot's divergences not narrowed to the row's forged paths) and X15 (the (9a)
witness-run check without its `new_unwitnessed` term), and that X15 removes the only kill of M17 (new slot
reads its pre-run divergence only). The r75 counter (`census/round-75/c1-counter.py`, selftest only, no
verdict code changed) adds: a witness read that reports only a set-up path outside FM1's forged paths
must leave both slots unwitnessed; and the (9a) run's per-row new-slot witness must be yes for every
forging row. Kills: r74 counter 4 of 6 (X09 and X15∘M17 survive, `controls/c2-K-do-nothing-r74.txt`),
r75 counter 6 of 6 with its own selftest 64/64 (`records/c2-after.txt`). X15 alone still survives by
design: it removes one of two detectors.

**Wave repair: the work tree itself.** A repository-local `core.worktree` makes `git -C <lane>` run status
and both listings against another tree, so the lane's own hidden content never enters the difference;
both the lane-base and the W gate printed `check-clean=PASS` on that fixture (S75ExecEvade HIGH-1,
S75Sentinel F1, S75CriticClaims; `census/round-75/records/wave-repair/coreworktree-W.txt`). The repaired
gate first requires `git rev-parse --show-toplevel` to resolve to the lane directory
(`RECEIPT-WORKTREE-REDIRECTED`, `coreworktree-R.txt`); the frozen counter still reads mismatches=0 at the
repair (`c1-at-repair.txt`). The r36 report-gate fixture hid its own harness symlink with info/exclude and
read 18/21 on the W gate (`regress-r36-original-at-W.txt`); it now declares that symlink in a committed
`.gitignore` and reads 21/21 on the base and the repaired gate.
