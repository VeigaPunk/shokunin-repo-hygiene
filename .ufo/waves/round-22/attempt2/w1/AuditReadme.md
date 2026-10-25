STATUS: PASS

Seat: `L1Souji22.AuditReadme` (leaf, read-only). Scope: declared-evidence audit of
`corpus/README.md` under the frozen classes A/B/C of
`.ufo/waves/round-22/attempt2/preregistration.txt`, with the CORPUS.md rule
"an index row is a claim" (rule 46 of `/home/vgpnk/Projects/shokunin/CORPUS.md`)
and "a count carries its command" (rule 34 of the same file) as the index rules.

Artifacts written (only these two paths):

- `.ufo/waves/round-22/attempt2/w1/evidence/AuditReadme.tsv` — 109 rows
  (`file/line/token/class/observed`): 94 class A, 15 class B, 0 class C.
- this report.

Nothing under `corpus/`, `census/`, `tools/`, or any sibling repo was written.
No tool was installed; `git`, `python3`, `grep`, `ls`, `wc` were already present.

## Pin

| item | value |
|---|---|
| lane repo | `/home/vgpnk/Projects/shokunin/souji-shokunin` |
| measured revision | `3216c1998fe04d7e23793ffd4e135bd37c3a11f4` |
| `corpus/README.md` blob | `5ee593e411f4403b5be542773faba236e8c315de` (446 lines) |
| worktree state of that file | clean (`git status --porcelain corpus/README.md` → empty) |

`git rev-parse HEAD` returned `70af563c` at my first call and `3216c19` a few
calls later: siblings landed commits during the seat. I pinned the audit to
`3216c19` and verified the README bytes I read equal that revision's blob
(`git hash-object corpus/README.md` = `5ee593e…`), so no token was graded
against stale prose.

## Method

Class rules are the preregistration's, used verbatim: A = backticked path ending
`.py/.sh/.json/.tsv/.md/.txt`, optional `:<line>`, optional glob, must be present
at `--rev`; B = 7..40-char hex in a cell naming a revision context, must pass
`git cat-file -e <tok>^{commit}`; C = 64-hex in a cell with exactly one
backticked path, must equal `sha256` of that path at `--rev`.

Cross-check with the frozen C1 scanner (read-only, no writes except its own
`/var/tmp` scratch):

```
$ python3 -B tools/souji-declared-evidence.py --root . --file corpus/README.md \
      --rev 3216c19 --format tsv
assertions=108 resolved=18 skipped=79 mismatches=90      (rc=1)
```

Independently I resolved each span against the two bases the file actually
uses — repo-root and `corpus/` (the file lives in `corpus/`, and `../tools/…`
can only mean repo-root) — plus a bare-basename rule for names carried by a
section heading. Result, and the difference from the scanner:

| class | rows | resolved | unresolved |
|---|---|---|---|
| A, literal repo-relative (scanner rule) | 93 | 3 | 90 |
| A, base-aware (repo-root / corpus-base / bare) | 94 | 88 | 6 |
| B, commit resolution | 15 | 15 | 0 |
| C, digest | 0 | — | — |

18 = 15 B + 3 A in the scanner line, so the two runs agree on B and on the
repo-relative reading; the divergence is entirely the base question in F3.
I added one hand-classified class-A row (line 344,
`6ff3413bba9c…:tools/souji-proc-census.sh`) that the scanner skips because the
span carries a `git show ` prefix. Total rows differ by that one row (108 → 109).

## Findings

### F1 HIGH — the `QUALITY.md` index row states an admission-bar range that is false at the measured revision

`corpus/README.md:31`: "the admission bar (Q1–Q15 at r12; Q1–Q26 since r16;
Q1–Q28 since r17, see the Round 16 and Round 17 sections)".

```
$ grep -cE '^\| Q[0-9]+ \|' corpus/QUALITY.md
53
$ grep -oE '^\| Q[0-9]+ ' corpus/QUALITY.md | grep -oE '[0-9]+' | sort -n | tail -1
53
```

The bar is Q1–Q53 at the measured revision. The row is not merely stale: the
same file cites `Q36`, `Q37`, `Q38` (lines 275–277) and `Q47–Q50` (line 366),
so README contradicts its own index row, and no later section carries the
correction (the only other range statements, lines 62 and 200, are earlier and
also stale). Under "an index row is a claim" this row asserts the wrong size
for the only file it points at. The row also carries no command and no date for
any of the three ranges (see F4, row L31).

The second half of the same row does hold: every one of the 53 criteria rows
has a non-empty lesson cell (`53 rows, 0 without lesson citation`, script check
over `| Q<n> | ... |` rows).

### F2 MEDIUM — "admitted" has two incompatible counting rules, and the r22a2 rows show no command

- Line 285 fixes the authority: "The lane's own counter
  (`python3 census/round-13/count-claims.py b576341…`) reports **6**". That
  counter's predicate is frontmatter-shaped — first three lines must be
  `source:`, `verified-at:`, `recheck:` in that order, and the text must not
  contain `## Admission status — HELD`.
- At the measured revision that command returns
  `{"admitted_entries": 7, "evidence_gate": 1, "F2_entry": 1, "measured_commit": "3216c19…", "sources": 114, ...}`.
- The two entries the r22a2 section adopts are **not** counted by it: both have
  3–5 `source:` lines before `verified-at:`, so the three-line predicate fails.

```
$ python3 -c "... same predicate per file at 3216c19 ..."
not  corpus/knowledge/quarantine-origin-record-fields-r24.md  | fm3= False
not  corpus/knowledge/quarantine-staging-no-copy-r23.md       | fm3= False
```

- Line 286 states a third rule — "eight files under `knowledge/` minus the
  `.tsv` ledger and the single HELD entry" — which at the measured revision
  (`11` files) yields **9**, not 7.
- Lines 427–437 then call the two entries "adopted" / "entries admitted" on the
  gate-check predicate. That predicate is satisfied (see below), but the README
  states only the tool path, never the invocation or round date, unlike the r13,
  r14 and r19 counter rows which print the full command.

So the index now contains three different answers (7, 8-implicit, 9) to "how
many entries are admitted", each under an unnamed predicate. A reader cannot
reconcile coverage from the index alone. This is a live, not historical,
inconsistency: it is created by the r22a2 rows themselves.

### F3 MEDIUM — only 3 of 93 declared paths are literally repo-relative; 6 are not dereferenceable as written

`corpus/README.md` never states a path base, yet mixes four conventions:

| convention | spans | outcome |
|---|---|---|
| repo-root literal | 3 | resolve (e.g. `census/round-1/census.tsv`, `tools/souji-verify.sh`) |
| `../…` (corpus parent = repo root) | 50 | 48 resolve in repo root; 2 point outside the lane repo |
| corpus-relative, unprefixed | 29 | resolve only against an unstated `corpus/` base |
| bare basename (section supplies the dir) | 11 | 7 recoverable from the section, 4 ambiguous |

(93 scanner spans; the hand-added rev-pinned row at line 344 makes 94 class-A
rows in the TSV.)

Under the frozen class-A text ("must be present in the repository at `--rev`")
the literal reading scores 3/93 and produces 90 mismatches — the scanner's
`mismatches=90`. That number is real but it grades notation, not truth: 87 of
the 93 name files that exist. The actionable defects are the 6 that no base
recovers:

| line | token | bytes actually at | dereferenceable as written |
|---|---|---|---|
| 92 | `counts.json` | `census/round-13/counts.json` | no |
| 311 | `counts.json` | `census/round-13/` or `census/round-14/` (both exist) | no, and ambiguous between two |
| 383 | `remote-source-after.json` | `census/round-21/remote-source-after.json` | no |
| 383 | `final-code-verification.json` | `census/round-21/final-code-verification.json` | no |
| 217 | `../../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` | `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/` (verified with `ls`) | outside the lane repo |
| 217 | `../../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` | same | outside the lane repo |

Consequence for calibration: any literal declared-evidence counter run over
this file reports ~90 false mismatches, so this index cannot be graded by that
counter until the base is stated (or the paths rooted). That is a property of
the index, not of the files it names.

### F4 MEDIUM — 21 numeric claims do not carry the `<number> — <command> <date>` form CORPUS.md requires

Rule 34 (`/home/vgpnk/Projects/shokunin/CORPUS.md:34`): "Any number in a corpus
entry (rows, files, lines, packages) is written as `<number> — <command>
<date>`." Rows that comply: L32, L55, L91–92, L140–142, L221–223, L285,
L351–355 (command + revision). Rows that do not:

| line | count claim | form present |
|---|---|---|
| 31 | `Q1–Q15` / `Q1–Q26` / `Q1–Q28` | none (also stale, F1) |
| 46 | `0 prunable, 3 locked today` | file pointer only, no date |
| 94–97 | `36/36`, `5/5`, `5/5`, `1/5 PASS`, `40/51/91/36` | file pointer only |
| 134–136 | `48/48`, `22/22`, `33/33`, `2/12→12/12`, `38/38` | file pointer only |
| 216 | `changed arm 0 failed` | none |
| 217 | `15`, `55 vs 44` | two report pointers |
| 248 | `58 souji fixture orphans` | none, undated |
| 254–255 | `9 failed → 0`, `49→69`, `0 failures` | file pointer only |
| 258–260 | `61/0`, `11/0`, `Seven` | none |
| 261–264 | `19/0`, `66=66`, `65=65` | file pointer only |
| 295 | `18/18` | revision only |
| 330 | `historical58-orphan` | none (marked historical) |
| 340–341 | `27-case`, `old6/27`, `19 leaks`, `changed27/27`, `454→160` | fixture command on L346 covers a different entry point |
| 362 | `32/32`, `base18/32`, `14` | none |
| 365 | `0→2 new flags` | file pointer only |
| 371–377 | `192`, `3539`, `2372`, `tp3/fp0/fn0/missing0/extra0`, `3`, `2`, `401`, `1942`, `430`, `seven`, `one` | one JSON pointer, no command |
| 383 | `exit2` | none |
| 387–388 | `32/32`, `4/4`, `27/27`, `8/8`, `3/3` | file pointer only |
| 427 | `2/2 entries`, `8/8 register-slice verdicts` | tool path, no invocation, no date |
| 430 | `five-device measurement` | none |
| 439–441 | `8 rows`, `5`, `1`, `1`, `1` | TSV pointer only |

Sixteen of those values are nonetheless **true** against committed JSON, which
I re-derived: L372's `192`/`3539`/`2372` and L373's five oracle fields match
`census/round-21/oracle-acceptance.json` (`files: 192`, `calls: 3539`,
`oracle: {tp: 3, fp: 0, fn: 0, missing: 0, extra: 0}`, `labelled: 2372`), and
L387–388's five totals match the `SUMMARY` lines inside
`census/round-21/final-code-verification.json`
(`read32 total=32 pass=32 … base_discriminating=14`; `render4 4/4`;
`reason27 27/27 leaks=0 base_leaks=19 max_reason_bytes=160`; `output8 8/8`;
`head3 3/3`). The defect is form, not arithmetic — and it matters, because the
rule exists precisely so a reader does not have to guess which JSON produced a
number.

### F5 LOW — the lessons/ shape claim fails for six rounds, and its only command covers half the range

Line 17: "per-round training lessons, one file per round, each with a `## Gate`
section (candidates / admitted / rejected / spot-check) — held from r12 only".

```
round-12  Gate=1 candidates=6 admitted=5 rejected=10 spot-check=2
round-13  Gate=1  6  9 17  2
round-14  Gate=1  2  4  6  0
round-15  Gate=1  3  4  6  0
round-16  Gate=1  4  2  6  0
round-17  Gate=1  3  1  4  0
round-18  Gate=1  3  3  2  0
round-19  Gate=1  1  3  2  0
round-20  Gate=2  3 10 25  0
round-21  Gate=1  2  3  7  3
round-22  Gate=2  2  7 18  4
```

The `## Gate` half is true and is what line 55's command actually tests
(`grep -c '^## Gate' corpus/lessons/round-{1..11}.md` → 0 each, verified). The
four-part parenthetical is false for r14–r19, which contain no `spot-check`
section at all, and no command supports it for r12+. The parenthetical should
either drop `spot-check` or name the rounds that carry it.

### F6 LOW — a dated sweep in a live index has already rotted

Line 40's F2 row: sweep `ls corpus/knowledge | grep -ciE 'size|structure|sizer'`
→ 0, 2026-10-19. Today the same command returns `1`
(`git-repo-structure-readonly.md`). The row is dated and superseded at line 64
("supersedes the r12 F2 row"), so it is rule-compliant, but it demonstrates the
failure mode F1 and F4 share: a dated count left in place without a successor
row reading the same index.

### F7 LOW — `ddb7347` is described as "never committed" while resolving as a commit

Line 216: "(changed arm 0 failed; r18 correction: was a `ddb7347` record name
never committed)". The token resolves:

```
$ git log -1 --format='%H %s' ddb7347
ddb73474433977ff54b015ac3e77669ff2537353 round-17: C1 census D1/D2, C2 seat-audit precision + r16 transcripts bundle, …
$ git ls-tree -r --name-only 3216c19 | grep -i ddb7347
.ufo/waves/round-18/w1/RevengeDdb7347Pointers.md
census/round-18/transcripts/w1/RevengeDdb7347Pointers.txt
```

The true part — the record *file name* `jj-receipts-ddb7347.txt` was never
committed — holds (no such path in the tree). But the cell attaches "never
committed" to a token that is a commit, and class B resolves it, so the cell
survives the counter while reading as a false denial. One clause ("record name
`jj-receipts-ddb7347.txt` was never committed") would remove the collision.

## Second table — index rows whose named file does not exist

**None.** Every declared path in the file resolves to an existing file or
directory: 88 of 94 class-A rows resolve in-tree, 2 resolve outside the lane
repo at the fleet-root path they spell, and the 4 bare basenames that no base
recovers map to files that exist in the round directory named by the same
section (F3 table). Supporting checks beyond paths:

| claim | evidence |
|---|---|
| `SOURCES.md` … `## Paths`, `## Search log` | `grep -nE '^## (Paths\|Search log)'` → lines 136, 143 |
| all cited source ids exist | 41/41 `OK` for S022, S034–S040, S064–S070, S072–S078, S082–S085, S089, S091–S093, S100/S101, S103–S106, S109–S114 |
| `obsidian-ledger.tsv` is header-only | `wc -l` → 1 |
| `SKILL.md`, `tools/` exist (line 38) | `ls SKILL.md` → present at repo root |
| `../census/round-15/end-sources.json` = 42-row inventory | JSON `source_rows: 42` |
| `MANIFEST rounds[402]` = CloseSouji20 | `rounds[402]` = `{"round": 20, "lane": "souji", "type": "closure", "admitted": true, "verdict": "admitted", …}` |
| r22a2 snapshots committed | `git ls-files census/round-22/attempt2/` lists all 13 source files incl. `vendor-noreplace-probe.out` |
| `slice-verdicts.tsv` 8 rows, distribution as claimed | `cut -f2 \| sort \| uniq -c` → 5 accepted, 1 present, 1 refused, 1 unverifiable |
| gate-check counts in line 427 | `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, rc=0 |
| adoption package path (line 425) | `/home/vgpnk/Projects/shokuknow/merge/souji` exists (listed only; not read) |

## Counts re-derived true (positive evidence, so the audit is not only negative)

| README row | command run | observed |
|---|---|---|
| L32 "33 rows" (2026-10-19) | same `grep -cE` at `d7266c5` and `31984f4` | 33, 33 |
| L55 "0 each, rounds 1–11" | `grep -c '^## Gate' corpus/lessons/round-{1..11}.md` | 0 ×11 |
| L91–92 "4→5" | `count-claims.py` at `31984f4`, `6f8ee0f` | admitted 4, 5 |
| L140–142 "5→5, rows 37→40" | `count-claims.py` at `a31642d`, `552cae4` | 5/5, 37/40 |
| L285 "reports 6" | `count-claims.py b576341` | `admitted_entries: 6` |
| L353–355 "3-source matrix 0/3→3/3, each 18/18 at 4b826a5" | `head -5 census/round-21/replay-integrated.txt` | `S1..S3 matched=18/18`, `scenarios=3 replayed=3 summaries_equal=True` |
| L380 "3/3 source shapes" | `accepted-matrix.json` | `scenarios: 3, replayed: 3` |
| L427 "2/2, 8/8" | frozen gate-check invocation | `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0` |

## Residual risk and verification gaps

- Historical acceptance at L295 (`bbeb73bd…`, 18/18) and L353 (`4b826a5…`) was
  read from its receipts, not re-executed; re-running acceptance is the C1/round
  receipt job, not this item's.
- Class C has **zero** coverage here: the file contains no 64-hex digest, so
  nothing in the index asserts a byte digest that could be wrong. That is a
  finding about the index's evidence density, not a pass I can claim beyond
  "0 assertions".
- `base18/32` (L362) is not in `final-code-verification.json`'s `read32`
  summary, which reports `base_discriminating=14` instead; that value is
  unverified from the records I read.
- The two `../../.ufo/...` targets were verified to exist on disk; I did not
  check whether they are tracked in the fleet root's repository, so
  "cross-repo pointer" is a statement about location, not about tracking.
- Numbers in the attempt-1/attempt-2 result-contract sections that need a
  fixture re-run (`five-device measurement`, `454→160`) were not re-derived;
  nothing is asserted about them either way.
- `census/operator-sweep-20261019/` was not opened (contract); only its name
  appears in the index and it is disclosed there as untracked/operator-owned.
