STATUS: PARTIAL

Scope: attack C2's frozen counter and the gate-check predicate in
`.ufo/waves/round-22/attempt2/preregistration.txt` (C2, per-entry checks 1–6 and the slice
predicate). Read-only in the lane; every fixture was executed against the lane's own tool.
Revisions and bytes I measured are pinned below because the lane moved during the review
(HEAD advanced 2a130b4 → 3216c19 → 5ff5041 → d6a75ba while I worked, and
`slice-verdicts.tsv` changed verdict classes at 5ff5041).

PARTIAL, not PASS and not FAIL: the three requested attacks all succeed, and two of the
three succeed in their *strongest* form (an exact-output false-green, and a green counter
over rows that were refused). The frozen predicate therefore does not hold as a
false-green guard. It is not FAIL for honesty: the landed pair's provenance is real — all
six committed `*.raw` snapshots are byte-identical to the pages fetched today, and the
vendored probe's sha256 equals the digest the entry declares. The defect is in what the
counter *can distinguish*, not in what the authors did.

Pinned state
------------
    $ git log --format='%h %s' -1
    d6a75ba round-22: connector and row-draft corrections to registry, entry and README
    $ sha256sum census/round-22/attempt2/slice-verdicts.tsv census/round-22/attempt2/quarantine-slice \
                corpus/knowledge/quarantine-staging-no-copy-r23.md corpus/knowledge/quarantine-origin-record-fields-r24.md \
                tools/souji-gate-check.py
    12cad84e887e6e342c37f6f09001d5f861956791bc2beb7b3f35dd4b22dfca24  census/round-22/attempt2/slice-verdicts.tsv
    12d3c325649ca6026bdb9b98b1edb1ebd2d2dcc61ac519bfa14d7d084c5da7e6  census/round-22/attempt2/quarantine-slice
    80a6a89515f96a5455d1ea38a8e428f455b71b627071d5b9b4932d10b22762de  corpus/knowledge/quarantine-staging-no-copy-r23.md
    46e0afdd435253ebd137141e308d18237e3b40bf4e21c77c904f461e6cde96a7  corpus/knowledge/quarantine-origin-record-fields-r24.md
    d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00  tools/souji-gate-check.py

Second pin, because both the checker and the entries moved while I was attacking them.
The working tree at the end of the review (HEAD still d6a75ba, four paths modified):

    9eb1d40679be0977d456226ed84e8eaf04d143ce09aad1cad55f2047184c4e5b  census/round-22/attempt2/slice-verdicts.tsv
    a60245dc1f0c0d5522da64dab17d72c17440806e9ca7b03acee3d9fa0c60fcf2  corpus/knowledge/quarantine-staging-no-copy-r23.md
    7fd91552fdfd020c07512fc97aee457d68f58d384effff82827edd5bac6b2ba1  corpus/knowledge/quarantine-origin-record-fields-r24.md
    f2d18e8273d56467a1af29499241348bcfcf90ccac7729bbd424b90d58fd4331  tools/souji-gate-check.py   (differs from HEAD)

Every attack below was re-run against this working-tree checker; all verdicts in §B–§E are
unchanged (`attack-log-worktree.json`), and its selftest is still 9/9. The only tool change
is that a missing verdict row no longer emits a `fail` entry, per the frozen rule that such
a row "is counted in neither V nor F" — which produces a new receipt defect, §D(2).

Live counter at that tip:

    $ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
        --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
                  corpus/knowledge/quarantine-origin-record-fields-r24.md \
        --snapshot-dir census/round-22/attempt2/sources \
        --slice census/round-22/attempt2/quarantine-slice \
        --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
    entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
    exit=0

Tool selftest: `--selftest` → `selftest=9/9`, including
`PASS control always-green -> FALSE-GREEN-REJECTED`.

All 24 fixtures, argv, rc and stdout: `w1/evidence/CritC2Counter/attack-log.json`.
Fixture tree and reproduction commands: `w1/evidence/CritC2Counter/INDEX.md`.

--------------------------------------------------------------------------
A. The headline: the frozen "After" line is reproducible with zero real evidence

Fixture `fx/F0` is a fabricated root — fabricated `corpus/SOURCES.md` (rows S109–S114),
two entries whose only quoted evidence lives in a snapshot file I authored, and the real
8-id slice with eight `refused` rows whose evidence pointer is the single character `x`:

    entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0      rc=0

That is byte-identical to C2's frozen After line (`entries=2 ok=2 slice_verdicts=8/8
fail=0`, exit 0). Checks 1–6 all pass on bytes that cite a real URL, quote a sentence
that exists in no document, and attest nothing. The root contains no `.git` at all, so
"committed" is not even representable, and nothing in the tool consults git: the only
`subprocess` call in the file is `rm -rf` for the selftest tempdir (`:275`); there is no
network client anywhere.

--------------------------------------------------------------------------
B. Question 1 — authored snapshot + real URL: which frozen check catches it? None.

Fixture `fx/Q1`: Gate `url: https://man7.org/linux/man-pages/man2/rename.2.html`,
`opened: 2026-10-25`, ADMIT quoting

    RENAME_NOREPLACE refuses to overwrite an existing destination and returns EEXIST,
    verified on every device the fleet uses.

with `— § DESCRIPTION — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt`,
where that snapshot is a one-line file I wrote. Observed:

    entries=1 ok=1 slice_verdicts=1 slice_total=1 fail=0    rc=0

    fabricated quote present in LIVE rename.2 html?           False
    fabricated quote present in COMMITTED .raw?               False
    fabricated quote present in COMMITTED .txt?               False

Per frozen check: check 1 → the file exists and has `## Gate` (pass); check 2 → one https
token and one `opened:` literal with the round date (pass, and it never dereferences the
URL); check 3 → a ≤25-word quote with `§` on the line (pass); check 4 → the quote is in
the file the line names, which is under `--snapshot-dir` (pass); check 5 → the cited
`S109` row exists in the fabricated registry (pass); check 6 → ADMIT and REJECT present
(pass).

**No frozen check compares the snapshot's bytes with the cited URL, and no frozen check
requires the snapshot to have been fetched.** The decisive corroboration is inside the
tool: its own positive fixture (`_gate`, `:214`) cites `https://example.invalid/doc`.
An address guaranteed not to resolve is the tool's definition of a good Gate, so check 2
is a string obligation, not an access record. `fx/Q8` confirms the same with
`url: https://example.invalid/never-opened` and `opened: 2026-10-25` inside an HTML
comment: `entries=1 ok=1 … fail=0`, rc=0.

Related, and stronger than a fixture: check 4's containment test is
`spath.startswith(snap_root + os.sep)` on a `normpath`ed string (`:99`), with no
`realpath`. `fx/Q5` puts `sources/alias.txt` as a symlink to
`…/CritC2Counter/injected-uncommitted.txt` — outside the snapshot dir, outside the repo,
uncommitted bytes. Observed `entries=1 ok=1 … fail=0`, rc=0. So "the committed snapshot
file" can be a link to bytes that were never committed.

--------------------------------------------------------------------------
C. Question 2 — whitespace-collapsed splice: yes, but only at whitespace-only seams

`fx/Q2`: snapshot = the committed `man7-mv.1.txt` bytes + `\n` + the committed
`man7-rename.2.txt` bytes (both files are tracked, unmodified). Quote:

    Hosting by jambit GmbH. rename(2) - Linux manual page

(9 words; mv's last line + rename's first line). Observed:

    entries=1 ok=1 slice_verdicts=1 slice_total=1 fail=0     rc=0
    seam quote in mv.1.txt alone?     False
    seam quote in rename.2.txt alone? False

`fx/Q2c` is the semantic version with real bytes only: `excerpt.txt` is one real line of
`man7-mv.1.txt` followed by one real sentence of `man7-rename.2.txt`, and the entry quotes
the joined span (13 words):

    do not copy if renaming fails RENAME_NOREPLACE requires support from the underlying filesystem.

    entries=1 ok=1 slice_verdicts=1 slice_total=1 fail=0     rc=0

The discriminating control `fx/Q2c_punct` is the same span with one appended `.`:

    FAIL … check4-quote-absent-from-snapshot-line-7
    entries=1 ok=0 … fail=2    rc=1

So the collapse is exactly a whitespace-only join: it erases line wraps, paragraph breaks,
and the seam between two documents or two excerpts, but it cannot join spans with any
non-whitespace between them, and one character of invented punctuation breaks the match.
That is the honest bound: **a "quote assembled from two distant places" passes only if the
named file makes those two places adjacent modulo whitespace** — which is trivially
arranged, because nothing forbids a snapshot from being a concatenation or an excerpt.
Check 4 catches the punctuation variant; no frozen check catches the seam variant, because
check 4 asks only "is this string in this file", never "is this one document, and is it the
document the URL and locator name".

--------------------------------------------------------------------------
D. Question 3 — V==T with refused rows and no verification: yes, in three ways

    fx/Q6a  real 8-id slice, 8 `refused` rows, evidence `x`   → entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0  rc=0
    fx/Q6b  4-id slice, 4 `refused` rows, evidence `x`        → slice_verdicts=4 slice_total=4 fail=0                 rc=0
    fx/Q6c  empty slice + empty verdicts                      → slice_verdicts=0 slice_total=0 fail=0                 rc=0

Q6b is the literal four-refused question, and Q6c shows there is no floor at all: T is
whatever the slice file parses to, and with no ids every predicate over ids is vacuously
true. Two further slice holes:

    fx/Q6d  slice line " S114 S999   `payload-absent` " plus a verdict for S114 only
            → slice_verdicts=1 slice_total=1 fail=0           rc=0   (the second id on a line is never required)
    fx/Q6e  the real 8 rows plus an invented S999 row
            → slice_verdicts=8 slice_total=8 fail=0           rc=0   (unknown rows are silently ignored)

Only two guards exist, and both fire: a blank evidence pointer (`verdict-no-evidence`,
Q6f) and a class outside the four frozen names (`verdict-bad-class`, Q6g). Nothing checks
that the pointer resolves to anything. `refused` is a frozen class, so counting it in V is
permitted by the predicate — but it means `slice_verdicts=8` reports "eight rows carry a
class", not "eight verdicts are verified".

Two measurements make that concrete rather than hypothetical.

(1) At sha 12cad84e (commit 5ff5041) the landed file contained **two `refused` rows**
(S123, S131, each stating the cited payload does *not* support the claim) and the counter
still printed `slice_verdicts=8 slice_total=8 fail=0`, exit 0. A quarter of the slice was a
refusal and the green line was unchanged. Then both rows were re-graded to `accepted`
between 5ff5041 and the working tree, with no artifact added to the wave — the correction
re-cites `git-worktree(1)`, which has no snapshot in the wave:

    -S123  refused   quote absent from cited fixture r23-trigger-prune.sh and its .out (0 matches) …
    +S123  accepted  span verbatim in git-worktree(1) SYNOPSIS line 12 and the docs page; 0 matches in the cited fixture output …

    -S131  refused   quote absent from the cited payload (0 literal and 0 normalized matches) …
    +S131  accepted  span verbatim in git-worktree(1) OPTIONS -n,--dry-run; payload own line prune --dry-run …

`slice_verdicts=8 slice_total=8 fail=0` is identical before and after. The counter cannot
distinguish "the row was refused" from "the row was re-cited"; only the class string moved.

(2) The working-tree tool drops the per-row `fail` entry for a missing verdict. Result:

    fx/Q6h  7 of 8 verdict rows, real slice
            → entries=1 ok=1 slice_verdicts=7 slice_total=8 fail=0      exit 1
            with no FAIL line at all

so `fail=0` no longer means "no failures": a failing run now reports `fail=0` and the only
discriminator is `V != T` plus the exit code. That follows the frozen wording ("a missing
row … is counted in neither V nor F") but it removes the diagnostic that named the missing
id, and it makes the counter line unreadable in isolation — the very failure mode §H
records for calibration.

--------------------------------------------------------------------------
E. Smaller predicate holes, each executed

| fixture | what it exploits | frozen check | verdict |
|---|---|---|---|
| `fx/Q3` | locator token `section` occurs **inside the quoted text**; no locator outside it | 3 | `ok=1 rc=0` — the locator need not locate |
| `fx/Q4` | one `ADMIT:` with no quote, no locator, no snapshot **and no reason**, plus `- REJECT: —` | 6 | `ok=1 rc=0` — `REASON_RE` matches a bare em dash |
| `fx/Q9` | entry at an absolute path **outside** `--root`, quoting committed `gtk-filetrash.txt` under the `gio(1)` URL, scored against the lane's real slice | 1 | `ok=1 slice_verdicts=8 slice_total=8 fail=0 rc=0` |

Q4 is a divergence where the implementation is weaker than the frozen wording: frozen
check 6 requires ">=1 ADMIT and >=1 REJECT **with a reason string each**"; the code
(`:126-133`) checks a reason only on REJECT, and only for the first offending line. Q9 is
the same shape for check 1: frozen says "the file exists at the lane root", but
`path = rel if os.path.isabs(rel) else os.path.join(root, rel)` (`:65`) accepts any absolute path,
so the committed-entry requirement is unverified. The C2 counter contains no git call at
all, so "committed" is nowhere tested.

--------------------------------------------------------------------------
F. The landed wave: what the green line does not establish

Anchor audit of the eight verdict rows at the current sha 9eb1d406 (walk of
`census/round-22/attempt2/**`, matching each pointer against the sixteen artifact names in
the wave):

    S114 accepted      no wave artifact named   "snapshot git-scm git-prune"
    S118 unverifiable  no wave artifact named   "DOI resolves 202 with an empty body"
    S123 accepted      no wave artifact named   "git-worktree(1) SYNOPSIS line 12 and the docs page"
    S124 accepted      no path named            "payload line 2"
    S126 present       gtk-filetrash.txt        resolves
    S131 accepted      no wave artifact named   "git-worktree(1) OPTIONS -n,--dry-run"
    S133 accepted      no wave artifact named   "payload line 11 'SUMMARY: every writable mount implements RENAME_NOREPLACE'"
    S138 present       no wave artifact named   "qiita page and its API markdown"

Seven of eight pointers are prose, not references; one resolves. The wave holds sixteen
files: the six documents (`.raw`+`.txt`), the vendored probe, the slice, the verdicts and
the C1 TSV — there is no `git-worktree` snapshot, no `qiita` snapshot and no
`r23-trigger-prune` fixture, so those pointers cannot be re-derived from lane bytes at all.
S133's is the sharpest: its quoted payload line does not exist anywhere in the wave —

    $ grep -rl "SUMMARY: every writable mount" census/ corpus/ tools/
    census/round-22/attempt2/slice-verdicts.tsv      # only the verdict row itself
    $ wc -l census/round-22/attempt2/sources/vendor-noreplace-probe.out
    6 census/round-22/attempt2/sources/vendor-noreplace-probe.out

— the only probe artifact in the wave has six lines, so "line 11" of it cannot exist. The
counter counts that row as verified. This is the executed form of §D: the slice half of
the counter reports rows, not anchors.

Two positive receipts, so the record is balanced: (i) `cmp` returned IDENTICAL for all six
committed `*.raw` snapshots against the pages fetched today (HTTP 200, byte-identical to all six committed `.raw`, sizes
19401/11693/26697…); (ii) `vendor-noreplace-probe.out` hashes to
`1634d206…024be8bb5`, matching the digest the r23 entry declares, and its five device
lines carry the `NOREPLACE_existing=-1(EEXIST)` field the entry attributes to them. The
pair's *quoted* evidence is real; it is the verdict slice that is unanchored.

--------------------------------------------------------------------------
G. Operability: the counter is easy to satisfy by writing less

`fx/Q7` is an entry that is greener the less it says. A REJECT reason that honestly quotes
a term —

    - REJECT: staged row S1 — the "Path" key is a heading in the spec, reason: wrong artifact …

— is red, because `QUOTE_RE` picks up `"Path"` and `LOCATOR_RE` picks up `heading`, so the
line is treated as a located quote with no `snapshot:` token:

    FAIL … check4-no-snapshot-named-line-8 ; entries=1 ok=0 fail=1 ; rc=1

The cheap way to green is to delete the quotes — i.e. the predicate rewards prose over
quotation in exactly the field (reject reasons) that should be most explicit. Same family:
`gate_section` searches for `"\n## Gate"`, so a Gate heading at byte 0 is rejected;
`SNAPSHOT_RE.search(line)` takes only the first of two `snapshot:` tokens on a line;
`QUOTE_RE` ignores spans shorter than 2 chars, so a one-character quote is invisible.

Kill-rule fidelity: the frozen fixture 6 is "a byte-exact copy of the staged package
entry". The selftest substitutes a synthesized `"# fixture entry without a gate"` string.
I ran the real bytes instead —

    $ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
        --entries /home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md …
    FAIL … check1-no-gate: …
    entries=1 ok=0 … fail=1   exit=1

— so the kill rule's *effect* holds (the staged entry has zero `## Gate` headings), but the
selftest never exercises the case it names. Recommend embedding the staged bytes
(sha256 `f13fb769c418d7e4575ddfebaedae2c8199e47afbd08477ded8fd7ee4efa7e48` at this read).

And the "Before" line reproduces: with two absent entry paths the counter prints
`entries=2 ok=0 … fail=2`, exit 1.

**Where the predicate does hold.** The negative sweep, all executed, twelve cases:

| negative | result |
|---|---|
| quote of 26 words | `check3-quote-26-words`, rc=1 |
| `opened:` ≠ round date | `check2-opened-date`, rc=1 |
| Gate with no REJECT | `check6-no-reject`, rc=1 |
| `source: S999` absent from the registry | `check5-dangling-source: S999`, rc=1 |
| quote not in the named snapshot | `check4-quote-absent-from-snapshot`, rc=1 |
| verbatim quote + one appended `.` (Q2c_punct) | `check4-quote-absent`, rc=1 |
| blank verdict evidence pointer | `verdict-no-evidence`, rc=1 |
| verdict class outside the four frozen names | `verdict-bad-class`, rc=1 |
| 7 of 8 verdict rows | `slice_verdicts=7 slice_total=8`, rc=1 |
| byte-exact staged entry (kill fixture 6, real bytes) | `check1-no-gate`, rc=1 |
| entries absent (`Before`) | `ok=0`, rc=1 |
| always-green control | `FALSE-GREEN-REJECTED` (selftest) |

So each frozen check can fail on its own stated fixture, and the counter is not vacuous.
The defect is narrower and worse: the predicate has no positive-evidence floor — it can be
satisfied completely with bytes that prove nothing (§A), and its slice half cannot tell a
verified row from a refused one (§D).

--------------------------------------------------------------------------
H. Impacted axes

- **coverage (C2's own axis)**: `slice_verdicts=8/8` is not a coverage measurement. It is
  compatible with 8/8 refused (§D), with 7/8 unanchored pointers (§F), and with an empty
  slice. Quoting the After line as coverage overstates it by up to 8/8.
- **calibration**: a receipt whose output line is identical for "verified", "refused" and
  "re-cited" cannot calibrate anything — §D(1) shows the same line before and after two
  verdicts moved from `refused` to `accepted`. And after the working-tree change, `fail=0`
  coexists with exit 1 (§D(2)), so the field that reads as "no failures" is not one. This
  is the same defect class C1 is repairing in SCORECARD: a printable green that is not a
  function of the state it claims to report.
- **operability**: §G — the shortest path to green is to remove quotable prose from reject
  reasons and to write evidence pointers as free text; and the wave moved under the
  command (HEAD advanced four times, verdict classes changed at 5ff5041), so a report must
  cite the sha of `slice-verdicts.tsv` beside the counter line or the run is not
  reproducible.
- No axis harmed by this review: read-only in the lane, no git/jj writes, nothing written
  outside `w1/evidence/CritC2Counter/` and this report, no deletion authority created, no
  process signalled, `shokuknow` only read.

--------------------------------------------------------------------------
I. Smallest safe correction (additive only — the predicate may not be redefined)

1. Keep the four frozen classes and `V`/`T` semantics untouched this round. Beside the
   counter, emit two receipts in the round report:
   (a) **provenance receipt** — for each Gate `url:` fetch the page and byte-compare it to
       the snapshot the Gate names. Executed here: 6/6 committed `*.raw` are identical,
       which is the only check that rejects `fx/Q1`/`fx/F0`. Record the fetch date and the
       sha256 of each snapshot.
   (b) **anchor receipt** — resolve every verdict pointer to an existing wave-relative
       artifact. Today that is 1 of 8 (S126); the rest cite `git-worktree(1)`, `qiita`, a
       `r23-trigger-prune` fixture and a bare "payload", none of which is in the wave. The
       coverage sentence must read "8 rows carry a class (1 resolving pointer, 7 prose
       pointers, refused count disclosed)", never "8/8 verified".
2. Re-state the slice claim in the DOCUMENT rather than editing frozen text: C2's target
   becomes "exit 0 **and** every verdict pointer resolves **and** the refused count is
   disclosed" — the counter line alone is not the claim.
3. For the *next* freeze (explicitly not this round, because adding checks to the counter
   now would change what `ok`/`V`/`T` mean): give the counter checks 7–10 with their own
   failing fixtures — snapshot must be `realpath`-contained and git-tracked at the measured
   rev; entry path must be inside `--root`; ADMIT must carry a reason; verdict pointer must
   resolve to a file; `slice_total` must be > 0 and every id must be first on its own line.
   Fixtures `fx/Q1`, `fx/Q5`, `fx/Q9`, `fx/Q4`, `fx/Q2c`, `fx/Q6a`–`fx/Q6e` are ready to
   serve as their negatives.
4. Add the real staged entry (sha `f13fb769…`) as kill fixture 6 instead of a synthesized
   no-gate string, so the selftest exercises the case the frozen rule names.

Tooling: nothing installed or upgraded; no pacman/uv/npx transaction was run. Network use
was limited to six public `https` GETs (man7.org ×3, man.archlinux.org, docs.gtk.org,
specifications.freedesktop.org) and their bytes are kept under `w1/evidence/CritC2Counter/`
so every comparison is re-runnable offline.
