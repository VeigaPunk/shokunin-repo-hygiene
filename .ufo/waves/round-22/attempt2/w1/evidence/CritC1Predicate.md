# CritC1Predicate — executed transcript (read-only)

Instrument under test: `tools/souji-declared-evidence.py`, 14845 B,
sha256 `58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2`
(matches the digest pinned by peers MutPath/MutDigest).

Base rev `4edb25dfe262515d0da63224bbba71e02e36cba5`. The lane tip **moved during
this review**: `2a130b4` → `3216c19` ("round-22: record the measured declared-evidence
counts", 1 file, 1 line). All counts below are invariant across the two: 56/56/0/36.

Files written by me: this file and `../CritC1Predicate.md` only. Synthetic probe
declarations were written to `/tmp/c1crit/` (outside the lane) and never into the lane.
No lane file was edited; no git/jj write was run.

## E1 — counters (the frozen command)

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev 4edb25d --format counts
assertions=56 resolved=53 skipped=33 mismatches=3        rc=1
$ ... --rev 2a130b4 --format counts
assertions=56 resolved=56 skipped=36 mismatches=0        rc=0
$ ... --rev 3216c19 --format counts
assertions=56 resolved=56 skipped=36 mismatches=0        rc=0
```

Base mismatch rows (from `--format tsv`):

```
3   AXES.md                                                A mismatch:path-absent  not in tree at 4edb25d
63  reason-after.txt                                       A mismatch:path-absent  not in tree at 4edb25d
77  .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md  A mismatch:path-absent  not in tree at 4edb25d
```

All three targets are genuinely absent at base:

```
$ for p in AXES.md reason-after.txt .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md; do
    git cat-file -e 4edb25d:$p && echo PRESENT || echo ABSENT; done
ABSENT  AXES.md
ABSENT  reason-after.txt
ABSENT  .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md
$ git log --all --oneline -- AXES.md      # empty: never tracked in this lane
```

## E2 — selftest (kill-rule fixtures)

```
$ python3 -B tools/souji-declared-evidence.py --selftest
PASS fixture1 all-good -> 0
PASS fixture2 absent path -> mismatch
PASS fixture3 dangling rev -> mismatch
PASS fixture4 wrong digest -> mismatch
PASS fixture5 path only at other rev -> mismatch
PASS fixture6 correct digest -> resolved
PASS control always-zero -> FALSE-GREEN-REJECTED
PASS fixture7 command span -> skipped, not asserted
selftest=8/8   rc=0
```
No fixture covers: de-backticked token, absolute path, letter-prefixed hex,
digest with two paths, class-B on a non-table line, or N/set conservation.

## E3 — assertion SET is not conserved while N is

```
base (4edb25d) N 56 S 33   head (3216c19) N 56 S 36
REMOVED at head (were asserted at base):
  - A AXES.md
  - B 41553adb139d06511dc386bb3ce4326aebfba675
  - B b912328d00d19f26918240710d0b5e0f334880ff
  - A reason-after.txt
  - A .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md
ADDED at head:
  + A census/round-22/attempt2/declared-evidence-before.tsv   x2
  + B 4edb25dfe262515d0da63224bbba71e02e36cba5
  + A corpus/lessons/round-22-verifier-spotcheck.md
  + A census/round-21/reason-after.txt
base class counts Counter({'A': 50, 'B': 6})
head class counts Counter({'A': 51, 'B': 5})
```
Head SCORECARD L14 asserts "repaired to 0 mismatches over **the same 56
assertions**". Five base tokens were removed and six added; the sentence is false
and the counter cannot see it, because it prints only N.

Repaired forms, verbatim:

* head L3 `Axes (fleet `/home/vgpnk/Projects/shokunin/AXES.md`)` — still presents a
  path as the axes authority; names no revision; supplies no receipt. Host file
  exists (`/home/vgpnk/Projects/shokunin/AXES.md`, 5160 B) but is not in any lane
  revision. Satisfies **none** of the prereg's three permitted branches.
* head L83 `the operator scope file .ufo/scopes/.../obsidian-cli-probe.md;` — the
  path is still in the document, unbackticked. Target still absent:
  `ls` → no such file; `git cat-file -e HEAD:...` → ABSENT.
* head L68 `census/round-21/reason-after.txt` resolved — the only genuine repair.

## E4 — six dodge probes (real base bytes, synthetic copies at /tmp/c1crit/d)

```
00-baseline                       rc=1 N=56 R=53 S=33 M=3
01-dangling-prefixed-token        rc=1 N=56 R=53 S=33 M=3   # 473e98a... -> deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
02-debacktick-mismatch            rc=1 N=55 R=53 S=33 M=2   # `reason-after.txt` -> reason-after.txt
03-hyphenate-resolved-hex         rc=1 N=55 R=52 S=33 M=3   # b912328d... -> rev-b912328d...
04-absolute-path                  rc=1 N=55 R=53 S=34 M=2   # `AXES.md` -> `/home/.../AXES.md`  (M->S)
05-truncate-short-token           rc=1 N=56 R=53 S=33 M=3   # b912328d... -> b912328 (7-hex floor holds)
21-false-measurement-real-commit  rc=1 N=56 R=53 S=33 M=3   # base60/214 -> base999/999
22-false-positive-count           rc=1 N=56 R=53 S=33 M=3   # positive20/20 -> positive0/0
```
01 proves a 40-hex revision token presented as evidence can be replaced by a
dangling sha with **no** change to any counter field. 02/03/04 prove three
rewrites that lose no information and remove the assertion. 21/22 prove that
class B checks only `cat-file -e ^{commit}`, never the measurement attributed to
it.

## E5 — class B beyond the enum (real lines)

```
HEAD L38  pipes=0 table=NO   (base L33) `reproduced at its named measured revision `6f8ee0f``
HEAD L114 pipes=0 table=NO   `Preregistration `29c1f7e8df849be8ee1b2d62d2351e17ec9d21a8``
```
Both are counted as class B (base TSV row 33, head TSV row 114) although the
frozen enum confines class B to a token "inside a table cell". L114 has no
revision-context word at all; it matches on the word "measured" in prose.

## E6 — invisible revision tokens (real line, base L14 final cell)

```
changed runner4f83fd222ffbd8825340221a8c426550ef891191 (unchanged bytes);
oracle214 at b912328d00d19f26918240710d0b5e0f334880ff;
final oracle258 at473e98a498dbdb7315604251ab5a19a0823e7818
```
`HEX_B_RE` lookbehind `(?<![A-Za-z0-9_.-])` blocks `runner4f83…` and `at473e98a…`:
neither is in N and neither is added to S. Both resolve today
(`git cat-file -e <sha>^{commit}` → commit), so the miss is latent — but probe 01
shows it is unreported if one does not resolve.

## E7 — class C is structurally empty

Zero 64-hex tokens exist in SCORECARD at base or head (`grep -c` → 0/0), and
`classify` requires digest and path in the **same** cell while SCORECARD puts
paths in the left cells and measurements in the right. Probes:

```
10-C-paired-with-wrong-path  rc=1 assertions=3 resolved=2 skipped=0 mismatches=1
   | `tools/souji-verify.sh` | measured sha256 000...000 of `census/round-13/verification.json` |
   -> the digest is asserted against tools/souji-verify.sh (false coupling, spurious mismatch)
11-C-two-paths-skipped       rc=0 assertions=2 resolved=2 skipped=1 mismatches=0
   | `census/round-13/verification.json` `tools/souji-verify.sh` | measured sha256 000...000 |
   -> a WRONG digest escapes entirely, exit 0
12-C-true-target-wrong-digest rc=0 assertions=1 resolved=1 skipped=1 mismatches=0
   | `census/round-13/verification.json` | measured sha256 000...000 |
   -> path and digest in different cells: digest skipped, exit 0
```

## E8 — provenance fallback

```
$ python3 -B tools/souji-declared-evidence.py --root . --rev 4edb25d \
    --file census/round-22/attempt2/declared-evidence-before.tsv --format counts
assertions=56 resolved=56 skipped=0 mismatches=0
```
That file does not exist at `4edb25d` (`git cat-file -e` → ABSENT); the tool read
the worktree copy and still reported the run at the named revision.

## E9 — skipped tokens are never itemised

`run()` writes TSV rows for classified assertions only; `skipped` is a bare
integer. Unclassified spans observed at base (33 of them) include
`git show 41553adb…:census/round-21/run-acceptance.py` (a real path, present, never
asserted), `corpus/lessons/round-{6..11}.md` (brace range outside `GLOB_RE`; all
six exist, latent miss), and `## Post-review fixes`, `--round N …`, `HEAD`, `/tmp`.

## E10 — the quoted counter is itself an unscanned assertion, and it has drifted

The lane advanced again during review: `3216c19` → `5ff5041` → `d6a75ba`.

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev d6a75ba --format counts
assertions=58 resolved=58 skipped=36 mismatches=0        rc=0
class counts Counter({'A': 51, 'B': 7})   skipped 36
  B 6f8ee0f line 38 pipes 0        <- still class B on a prose line (enum says table cell)
  B 29c1f7e8df84 line 114 pipes 0  <- still class B on a bullet
```

SCORECARD L14 at `d6a75ba` still reads

```
... repaired to 0 mismatches over the same 56 assertions at the final tip ...
  `assertions=56 resolved=56 skipped=36 mismatches=0`, exit 0
```

`grep -c 'same 56 assertions'` at HEAD → 1; L3 still
``Axes (fleet `/home/vgpnk/Projects/shokunin/AXES.md`)``; L83 still
`the operator scope file .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.`
(target ABSENT on disk and in tree).

The quoted output `assertions=56 resolved=56 skipped=36 mismatches=0` sits in a
backticked span that is neither a path nor a bare hex, so it is counted in
`skipped` and never checked — while the file now measures **58**. The C1 row's
own headline number is therefore a declared-evidence assertion the instrument
cannot see, and it is already stale by 2 at the current tip. It was accurate at
`2a130b4`/`3216c19` (measured 56/56/36/0 at both), so this is drift, not a false
statement at commit time; but the row is keyed to "`--rev <final tip>`", and the
final tip moved.
