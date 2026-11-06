# S73Scribe — r73 draft for `corpus/knowledge/filter-filemode-witness.md` (L1 integrates)

Two parts: (A) replacement header lines 1–3, (B) the r73 section to append. Every number below was
re-read from the committed receipt named beside it; no number is copied from the L1's report.

## A. Header lines (corrected per the r72 verifier spot-check D1)

```
source: S306 (gitattributes(5), https://git-scm.com/docs/gitattributes, `filter` clean command, sha256 0a1e8015…6aee, accessed 2026-11-06); S307 (git(1) OPTIONS `--attr-source`, equivalent to GIT_ATTR_SOURCE, accessed 2026-11-06); S308 (git-config(1) `core.fileMode`, accessed 2026-11-06); S310 (git-config(1) `attr.tree`, outranked by GIT_ATTR_SOURCE); S311 (gitattributes(5) `ident`); S312 (git-check-attr(1) `--cached`, index-only attribute read, r72); S313 (gitattributes(5) long running process filter, r72); S314 (gitattributes(5) attribute-file fall-back order, r72); S315 (git technical documentation racy-git.adoc at tag v2.56.0, cached stat information, accessed 2026-11-06, r73); S316 (git-hash-object(1) DESCRIPTION, object id of a named file's contents, accessed 2026-11-06, r73); host probes census/round-71/probes/attr-filemode-probe-base.txt, attr-filemode-probe-sizechange.txt, stat-granularity-probe.txt (git 2.56.0); controls census/round-71/controls/c1-*.txt; wave evidence census/round-71/records/wave-w1/ (S71Sentinel, S71CriticClaims, S71Reviewer, S71CriticDiscern); counters census/round-71/c1-counter.py frozen at aa91d1cad89200ec733edd3475461010a372923d, census/round-72/c1-counter.py (r72), census/round-73/c1-counter.py (r73); r72 probes census/round-72/probes/fw-shapes-probe.txt, receipts census/round-72/records/c2-after-battery.txt, c2-honest-writer.txt; r73 probes census/round-73/probes/ (witness-weak-base.txt, witness-defang-D1..D5.txt, fx-index-stat.txt, fx-honest.txt), controls census/round-73/controls/c1-K-*.txt and c2-before-r72-D1..D5.txt, receipts census/round-73/records/ (c1-after.txt, c2-after-D1..D5.txt, writer-selftest.txt, counter-selftest.txt) (r72 spot-check D1: the header named only the r71 sources)
verified-at: a1db6c8514771c0a0321c29741831606d09cc2a5 (frozen C1 candidate) and f13d575e2e33cc98ae2c2e72e61557cb5a224591 (wave repairs; frozen counter re-run census/round-71/records/c1-at-repair.txt, writer selftest records/writer-selftest-repair.txt); 2026-11-06, git 2.56.0 on this host; r72: counter 06df4f97c531a05ff2139368f70660c3044f71a6, after-arms 2ec8b63dfda8fdf88cd240487c5d1325de13b501 (census/round-72/records/c2-after-battery.txt, c2-honest-writer.txt); r73: freeze 23ecd0700be05a78b71ad88ae6fca2d2d8f5468b, counter 1eac307f7cc8d1e30df009eabb693875ace97976, controls aaacba3378d8b8160f4c86c142182c0ddbcad81a, writer b84ff90bff05fb057c5a8c4b0661a9ec41d9e4a2, after-arms 312e8f29d42eac0fd91327d65a6b43a0ba9cc64e (census/round-73/records/c1-after.txt, c2-after-D1..D5.txt, writer-selftest.txt, counter-selftest.txt); 2026-11-06, git 2.56.0
recheck: `python3 -B census/round-71/c1-counter.py --root . --matrix census/round-71/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev <tip> --tool tools/souji-receipt-write.py --work <scratch>` must print `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` and `EXIT=0`; `python3 -B tools/souji-receipt-write.py --selftest --work <scratch>` cases 39-42 pass; on every git release, re-run the three probes and re-fetch S306-S316 against their sha256; r72: `python3 -B census/round-72/c1-counter.py --root . --matrix census/round-72/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev <tip> --tool tools/souji-receipt-write.py --work <scratch>` must print `SUMMARY matrix=75 base_forgeries=12 base_honest=19 base_mismatches=0 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` and `EXIT=0` (census/round-72/records/c2-honest-writer.txt); r73: `python3 -B census/round-73/c1-counter.py --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev <tip> --tool tools/souji-receipt-write.py --work <scratch>` must print `SUMMARY matrix=80 base_forgeries=15 base_honest=21 base_mismatches=0 base_unwitnessed=0 new_unwitnessed=0 new_forgeries=0 new_honest=21 class_mismatches=0 new_echo=0 errors=0 regress=PASS` and `EXIT=0`; writer selftest cases 43-44 pass; counter selftest 52/52
```

## B. Section to append

### r73: the index stat-cache forgery, the writer's byte truth, and the counter's forgery witness (appended 2026-11-06)

The r71/r72 protections all assume `git status` is a truthful witness of the worktree. It is not: the
index also caches the `lstat(2)` fields of every entry, and git skips the content read when they
match — "If some of these "cached stat information" fields do not match, Git can tell that the files
are modified without even looking at their contents" (S315, offset 1435 of
`census/round-73/srcs/racy-git.txt`), and the page states the failure itself: "Git can incorrectly
think files in the working tree are unmodified even though they actually are" (offset 3539).

**The forgery.** A caller (before the run) or the wrapped command (in-run) writes forged bytes to a
tracked file and rewrites that entry's stat fields in `.git/index` — blob OID kept, index checksum
recomputed, index mtime moved past the entry. `git status` reads clean over bytes that differ from
the revision. Both the pre-r71 writer (8b9345b1) and the lane-base writer (a789486d) wrote a receipt
over them: `census/round-73/probes/fx-index-stat.txt` prints `verdict=FORGERY` for
`route=index-stat-inrun`, `index-stat-prerun` and `index-stat-instrument-inrun` on both slots (3 of 3,
`pre_status=<clean>` and `post_status=<clean>` each time).

**What the writer now checks** (stage W, b84ff90b). For every stage-0 tracked regular file and
symlink that `git status` reports clean, the object id of the worktree content (`git hash-object
--stdin-paths` with C-quoted paths for regular files; the link target hashed as a blob for symlinks)
is compared with the object id the index records — before the run, after the status read
(`tools/souji-receipt-write.py:610`), and after the run, after the post-run reads (`:735`). Any
difference refuses `RECEIPT-WORKTREE-STAT-CONCEALED` (`:262`). The instrument's worktree bytes are
re-compared with `rev:path` after the run (`:742-744`). Selftest cases 43–44 cover it:
`stat-cache-forgery` (pre-run, in-run including `--allow-dirty`, and the instrument) and
`byte-truth-honest` (stale stat over unchanged bytes, autocrlf CRLF re-staged, tracked symlink, a
newline file name).

**What the counter's witness is** (stage I, 1eac307f). `tree_divergence`
(`census/round-73/c1-counter.py:1063`) compares `git ls-tree -r` entries with the worktree — missing
path, wrong type, wrong exec bit, different raw bytes, different symlink target, plus worktree files
outside the tree (`.git` excluded) — with no `git status`, no stat cache and no filter, once before
and once after each slot. A refuse row a slot accepts with no divergence at either point is
unwitnessed: `CASE` lines print `base_witness=no`, `SUMMARY` prints `base_unwitnessed=`, and
`claim_upheld` requires `base_unwitnessed=0` (`:1483`). The battery classifier counts an unwitnessed
acceptance as `error`, not a forgery (`:1503`); a witness read that fails is unwitnessed, never
witnessed (`:1414`). The five defang edits (D1 FWr, D2 FWi, D3 FWp, D4 FWs, D5 FC3) replace a row's
forged bytes with the committed bytes while the driver set-up stays, so the weak base still accepts
the row and nothing diverges.

Rows added (matrix 80 rows, 21 accept):

| row | route | which check alone sees it |
|---|---|---|
| FX1 | in-run forge of `tools/counter.py` plus that entry's stat rewrite | the post-run byte truth |
| FX2 | the same forge before the run | the pre-run byte truth |
| FX3 | in-run forge of the instrument plus its stat rewrite | the post-run byte truth, then the instrument re-compare |
| FXh | honest: `tools/notes.txt` mtime +10 s, bytes unchanged | accepted (a stat-only difference is not a divergence) |
| FXc | honest: `core.autocrlf=true`, CRLF notes, re-staged | accepted (raw worktree bytes differ from the blob, `probes/fx-honest.txt` `raw_equal=false`) |

Measured, re-read from the committed receipts:

- C1 after, r73 counter over the stage-W writer: `SUMMARY matrix=80 base_forgeries=15 base_honest=21
  base_mismatches=0 base_unwitnessed=0 new_unwitnessed=0 new_forgeries=0 new_honest=21
  class_mismatches=0 new_echo=0 errors=0 regress=PASS`, `EXIT=0`
  (`census/round-73/records/c1-after.txt`). Index stat-cache forgeries accepted 3 -> 0 of 3; honest
  rows 21 of 21 kept; EXIT 1 -> 0.
- C1 controls (stage K, before any writer byte changed): do-nothing with the lane-base writer prints
  `new_forgeries=3` and `EXIT=1` (`controls/c1-K-a-do-nothing.txt`); the always-refuse stub prints
  `new_honest=0` and `EXIT=1` (`controls/c1-K-b-blanket-refusal.txt`); the weak base writer as the
  new slot prints `new_forgeries=15` and `EXIT=1` (`controls/c1-K-c-forger.txt`).
- Writer selftest: `SELFTEST cases=44 pass=44 fail=0` (`records/writer-selftest.txt`).
- C2 after: each of D1..D5 prints `base_unwitnessed=1` with `base_witness=no` on its own defanged row
  (FWr, FWi, FWp, FWs, FC3 in turn) — `records/c2-after-D1..D5.txt`; the unmutated counter prints
  `base_unwitnessed=0 base_forgeries=15` (`controls/c1-K-a-do-nothing.txt`); counter selftest
  `SELFTEST cases=52 pass=52 fail=0` (`records/counter-selftest.txt`).
- C2 before: the r72 counter with each edit prints `base_forgeries=12` and `EXIT=0`, crediting the
  defanged row — detected 0 of 5 (`controls/c2-before-r72-D1..D5.txt`). Target 0 of 5 -> 5 of 5.

**Named limits** (declared in the preregistration before data). The witness sees the worktree only
(index, config and `.git` state are not compared), at two points, with raw bytes — a conversion-only
difference counts as divergence and matters only for refuse rows. The defang set covers five rows.
The writer trusts `git hash-object` to apply the same check-in conversion `git status` applies (S316),
skips gitlinks and paths status reports dirty, and runs at two points, so an in-run forgery restored
before the post-run read stays invisible (carried from r63). git 2.56.0 only. FXc is the converse
trap: on an honest tree the raw worktree bytes differ from the blob (`raw_equal=false`), so a
raw-byte comparison would over-refuse it.
