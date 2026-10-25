# DraftGateLesson — evidence receipts

Seat `L1Souji22.DraftGateLesson` (leaf member, no subagent dispatch).
Lane: `souji-shokunin`. Item: draft the `## Gate — attempt 2` block for
`corpus/lessons/round-22.md` (report only; the lesson file was not edited).
Contract: `.ufo/waves/round-22/attempt2/preregistration.txt` (frozen before
measurement; base revision `4edb25dfe262515d0da63224bbba71e02e36cba5`).
Measured revision: `3216c1998fe04d7e23793ffd4e135bd37c3a11f4` (lane HEAD at
measurement, 2026-10-25T06:47:48Z). Working tree was dirty: two admitted
entries carried uncommitted locator corrections from a concurrent seat
(diff quoted below); no quote span or source id was among the edits.

Nothing was installed or updated: no `pacman`, `uv`, `npx`, `cargo`, no host
transaction. All commands below are read-only (`git log/show/diff/ls-files`,
`sha256sum`, `grep`, `diff`, `awk` over the read-only register, and the two
lane tools invoked without `--write`/`--fix` flags).

## 0. Tool bytes (the counter's instrument)

`tools/souji-gate-check.py` was dirty in the working tree at measurement time
(a concurrent seat's 4-line conformance fix), so both states are pinned:

```
working tree  f2d18e8273d56467a1af29499241348bcfcf90ccac7729bbd424b90d58fd4331
HEAD          d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00
```

The diff removes a `verdict-missing` `fail` entry from `check_slice` and
retargets the `partial-verdicts` selftest fixture to the frozen rule ("a
missing row is a failure and is counted in neither V nor F"). Both counter runs
below were made at `f2d18e82…`; the sha was identical before and after the
runs, so the instrument did not change mid-measurement. The after-state line is
the same under both copies, executed: the committed copy run from stdin through
`git show HEAD:tools/souji-gate-check.py | python3 -B - …` prints
`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, exit 0. Only the
`partial-verdicts` selftest line differs between the two copies.

## 1. Frozen C2 counter — after state

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
EXIT=0
```

## 2. Kill rule — real tool passes the frozen fixtures

```
$ python3 -B tools/souji-gate-check.py --selftest
PASS fixture good -> ok [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture no-date -> fail [... fail=1]
PASS fixture long-quote -> fail [... fail=2]
PASS fixture quote-absent -> fail [... fail=2]
PASS fixture dangling-source -> fail [... fail=1]
PASS fixture no-reject -> fail [... fail=1]
PASS fixture no-gate -> fail [... fail=1]
PASS fixture partial-verdicts -> fail on V!=T with fail=0 [entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=0]
PASS control always-green -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=9/9
SELFTEST_EXIT=0
```

## 3. Before-state — non-destructive substitute only

The frozen before line (`entries=2 ok=0 slice_verdicts=0 slice_total=8`,
exit 1) requires the entries to be absent. Removing them is a mutating
cleanup this lane may not perform, so the exact frozen before line was **not
re-derived by this seat**. Substitute control, executed: point the same
counter at one present and one absent entry.

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r24.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
FAIL corpus/knowledge/quarantine-staging-no-copy-r24.md entry-missing: ...
entries=2 ok=1 slice_verdicts=8 slice_total=8 fail=1
EXIT_ABSENT_ENTRY=1
```

The counter therefore cannot be satisfied by having only one good entry.

## 4. Slice reproduction from the read-only register

```
$ R=/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
$ awk -F'|' -v l='souji' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ \
    {print $4, $5}' "$R" | diff - census/round-22/attempt2/quarantine-slice
SLICE-REPRODUCED-EXACT
```

8 data rows, every line carrying an S-id: campaign `S114 S123 S124 S126 S131
S133 S138` plus the prose-class row `S118`. Register header and `## By lane`
summary are stale, as the round prompt states; only data rows were derived.

## 5. Per-entry frozen predicate re-derivation (executed)

Span test: each double-quoted Gate span, whitespace-collapsed, searched in the
snapshot the same line names (all snapshots git-tracked under
`census/round-22/attempt2/sources/`).

| predicate | r23 staging | r24 origin-record |
|---|---|---|
| 1 file + `## Gate` heading | pass (`corpus/knowledge/quarantine-staging-no-copy-r23.md`) | pass (`corpus/knowledge/quarantine-origin-record-fields-r24.md`) |
| 2 https URL + `opened: YYYY-MM-DD` == round date | 1 URL (`man7.org/.../rename.2.html`), `opened: 2026-10-25` | 1 URL (`man.archlinux.org/man/gio.1.en`), `opened: 2026-10-25` |
| 3 located quote <=25 words with locator token | 3 ADMIT spans, max 14 words, locators `§ DESCRIPTION flags`, `§ DESCRIPTION, option --no-copy` | 6 ADMIT spans, max 23 words, locators `§ COMMANDS trash --list`, `§ COMMANDS trash --restore`, `§ Description`, `§ 6 Contents of a trash directory` (x2), `§ DESCRIPTION struct statx` |
| 4 every span verbatim in the named committed snapshot | 3/3 spans over 2 snapshots (`man7-rename.2.txt`, `man7-mv.1.txt`) | 6/6 spans over 4 snapshots (`arch-gio.1.txt`, `gtk-filetrash.txt`, `freedesktop-trash.txt`, `man7-statx.2.txt`) |
| 5 every `source: S<digits>` resolves to corpus/SOURCES.md | S109, S110, S111 -> rows present | S112, S113, S114, S022 -> rows present |
| 6 >=1 ADMIT and >=1 REJECT each with a reason | 3 ADMIT, 1 REJECT (`staged row campaign-S123`), reason + flip | 6 ADMIT, 1 REJECT (`staged entry quarantine-staging-no-copy-r24`), reason + flip |

Locator truth (outside the predicate, executed): `man7-mv.1.txt` has
`DESCRIPTION top` at line 60 and **no** `OPTIONS` heading, so the working-tree
correction `§ DESCRIPTION, option --no-copy` is true and the committed
`§ OPTIONS --no-copy` located a section that does not exist.
`freedesktop-trash.txt:54` is `6 Contents of a trash directory`, so the
working-tree `§ 6 ...` locator is true and `paragraph, Trash Info key/value
list` was generic.

Uncommitted corrections measured at the tip (quote spans unchanged):

```
corpus/knowledge/quarantine-origin-record-fields-r24.md | 6 +++---
corpus/knowledge/quarantine-staging-no-copy-r23.md      | 4 ++--
 2 files changed, 5 insertions(+), 5 deletions(-)
```

Working-tree sha256: r23 `80a6a89515f96a5455d1ea38a8e428f455b71b627071d5b9b4932d10b22762de`,
r24 `8a21704de532233b68805afc87e29dbed0bd096a42d09df7b1d416998fdea3d0`.
HEAD sha256: r23 `0081e83045a9fb28437902bfa3ba51870646434491f7834fef50c264ae45f394`,
r24 `b92f8118ab9c08a7f1121686da3fa221aeefde4b5cb54ec221db71a99d801eac`.
Gate tool: working tree `f2d18e82…58fd4331`, HEAD `d85c2696…12486b00` (§0).

## 6. Vendored measurement — byte identity

```
$ sha256sum <shokuknow>/lanes/souji/round2/evidence/noreplace-probe.out \
            census/round-22/attempt2/sources/vendor-noreplace-probe.out
1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5  .../noreplace-probe.out
1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5  .../vendor-noreplace-probe.out
$ diff -q ...
BYTE-IDENTICAL
```

`git show HEAD:...vendor-noreplace-probe.out | sha256sum` gives the same
digest, so the vendored copy is committed, not a working-tree artifact. The
file holds 5 device rows (`/var/tmp`, `/home/vgpnk/Projects/shokunin`,
`/home/vgpnk/Projects/shokuknow`, `/dev/shm`, `/tmp`) and `kernel:
7.2.11-arch1-1`. The entry labels it as not re-run in this lane; the lane did
not run it.

Host claim in the entries' frontmatter (`host coreutils 9.12`) — verified
against the real binary, not the session shell's `mv` wrapper, which reports
`0.8.0` and shadows PATH resolution:

```
$ type -a mv
mv is a shell builtin
mv is /usr/bin/mv
$ /usr/bin/mv --version | head -1
mv (GNU coreutils) 9.12
$ /usr/bin/mv --help | grep -i no-copy
      --no-copy
```

## 7. Registry state used by the id-map slot

```
rows: 114  first: S001  last: S114  dupes: 0  min/max: S001 S114
S022 used-by: corpus/knowledge/trash-spec-restorable-quarantine.md   status 2026-10-19
S109..S111 used-by: corpus/knowledge/quarantine-staging-no-copy-r23.md   status 2026-10-25
S112..S114 used-by: corpus/knowledge/quarantine-origin-record-fields-r24.md   status 2026-10-25
```

Collision step (committed `assimilation/collisions`, 0 bytes) plus
`reg-ids` 108 ids / `staged-ids` 134 ids agree with the map below.

## 8. Per-row slice verdict provenance (executed vs carried)

Executed by this seat against primary bytes:

- campaign `S123`: `grep -c "worktree prune \[-n\]"` over
  `<shokuknow>/lanes/souji/round2/evidence/r23-trigger-prune.out` = **0**;
  head of that file is `git_version=git version 2.56.0` then PASS lines;
  the `.sh` named by the TSV does not exist in that directory. The row's
  quote is `git-worktree(1)` SYNOPSIS prose.
- campaign `S126`: the registered quote is present verbatim
  (`grep -c "Sends file to the “Trashcan”, if possible."` over
  `census/round-22/attempt2/sources/gtk-filetrash.txt` = 1).
- campaign `S131`: the registered quote is absent from the cited payload
  (0 matches); the payload's own lines are
  `--- prune census (dry-run only) ---`,
  `default expiry (3.months.ago):      (no output — none prunable)`,
  `--expire=now (most aggressive):      (no output — none prunable)`.
- campaign `S133`: the payload's `SUMMARY: every writable mount implements
  RENAME_NOREPLACE` line exists; the payload sha256 is
  `a53f1e301d0c6969d589f9071b8a3bac9db8f6e1d3ebbb0ace42c300904b0809`, matching
  the staged entry's own frontmatter.
- campaign `S124`: the payload row carries the intervening field
  `NOREPLACE_new=0(ok)` between the path and `NOREPLACE_existing=-1(EEXIST)`,
  i.e. the register quote dropped a field rather than misquoting the page.

Carried from the committed `slice-verdicts.tsv`, not re-derived here:
campaign `S114` (git-scm git-prune reference rendering `git-repack[1]`) and
campaign `S138` (qiita heading `gc.auto (6700)`). Both rows cite public URLs
for which **no snapshot exists** under `census/round-22/attempt2/sources/`
(the directory holds 13 files, all for `rename(2)`, `mv(1)`, `statx(2)`,
`gio(1)`, the GIO `File.trash` page, the Trash spec and the vendored probe),
so those two verdicts cannot be re-derived from committed bytes without a
network fetch. Campaign `S118` (DOI) was not re-fetched; its class is the
register's unchecked prose family.

Note on pointer text: the TSV's evidence pointers paraphrase the payload
(e.g. the S131 pointer renders the em-dash payload line with ASCII hyphens),
so a re-derivation seat must read the bytes, not the pointer.

## 9. Existing lesson heading (conflict, reported verbatim)

`corpus/lessons/round-22.md` at `3216c199` is 370 lines and already carries

```
327:## Gate — attempt 2
```

committed by `70af563 round-22: bookkeeping, lesson gates and LOG for attempt 2`.
Appending another section with the identical heading would duplicate it. The
committed block lacks four required parts: the per-entry frozen criteria, a
register-row rejection with a flip condition, the `G1 RevSliceVerif` seat
name, and the `S-NEW-<slug>` id-map slot with the §10 parameter record.

## Not executed (stated, never claimed)

- the frozen before line for C2 (would require deleting the entries);
- C1's counter and receipts (`tools/souji-declared-evidence.py`,
  `census/round-22/attempt2/declared-evidence-before.tsv`) — another seat's
  axis, not restated here;
- any network fetch this round (no `git fetch`, no URL retrieval);
- any write outside the two assigned files.
