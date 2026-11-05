# S68ScoutDeclared — declared-protection inventory (summary)

Seat: `S68ScoutDeclared` (round 68, w1, lane `souji`, repo `/home/vgpnk/Projects/shokunin/souji-shokunin`).
Subject: the writer `tools/souji-receipt-write.py` at blob `f70da577eb1e1624cc63ab8fd0468565927d9b6a`
(sha256 `b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725`).
Method: read-only. No counter was run, no mutant was generated, no frozen file was edited.

## Sources read

- `census/round-68/preregistration.txt` (the freeze) — the C1 declared-protection model: "Each of the 14
  battery mutants removes exactly one of them (census/round-68/battery/SHA256SUMS)".
- `SKILL.md` sections `## Round 61` (line 815), `## Round 62` (833), `## Round 65` (842),
  `## Round 66` (861), `## Round 67` (881) — the lane's own declarations.
- `tools/souji-receipt-write.py` at blob `f70da577` — the docstring (lines 30–67) and the code (97–578).
- `census/round-68/mutate-writer.py` `MUTANTS` table (lines 17–55) — the 14 mutant recipes.
- `census/round-68/battery/SHA256SUMS` — the 14 mutant ids + the candidate sha256.
- `census/round-68/c1-matrix.tsv` (42 rows) and `census/round-68/c1-counter.py` `CASE_SPECS` (line 260) —
  read only to map each protection onto the matrix row that observes it.

## Counts

| quantity | value |
|---|---|
| declared protections **N** | **30** |
| protections with a battery mutant **M** | **16** |
| protections with no battery mutant **U** | **14** |
| distinct battery mutants referenced | 14 / 14 (no orphan mutant, no unnamed mutant) |

## The U rows (declared, but no battery mutant removes them)

| id | protection | matrix row that observes it |
|---|---|---|
| D01 | index-flag refusal `RECEIPT-INDEX-FLAG-CONCEALED` | D, N4 |
| D02 | unmerged class `RECEIPT-INDEX-UNMERGED` | none (no matrix row) |
| D03 | gitlink class `RECEIPT-GITLINK-CONCEALED` | none (no matrix row) |
| D04 | absent class `RECEIPT-INDEX-CONCEALED-ABSENT` | none (no matrix row) |
| D05 | in-run re-read `RECEIPT-STATE-CHANGED-DURING-RUN` | T1, T2, T3, T5, N1, N2, MOD, MOD2, MOD3, SY2, SY3 |
| D06 | `--allow-dirty` content snapshot re-compare | N1, N2, MOD, MOD2, MOD3 |
| D07 | `status.showUntrackedFiles=all` override | V1, V2 |
| D08 | mode recorded beside digest | MOD, MOD2, MOD3 |
| D10 | symlink recorded by name+target, never followed | SY1, SY2, SY3 |
| D18 | `GIT_OPTIONAL_LOCKS=0` | none (no matrix row) |
| D19 | `core.fsmonitor=false` | none (no matrix row) |
| D21 | `GIT_DIR`/`GIT_WORK_TREE` scrubbed from every git call | none (no matrix row) |
| D29 | `:(top)` pathspec (whole-index scope) | N4 |
| D30 | no refusal message prints a caller value | none (no matrix row) |

## Mutant → protection map (the 14 rows that carry a mutant)

K1→D12 · K2→D13 · K3→D15 · K4→D14 · K5→D09 · K6→D17 · K7→D16 · K8→D11 ·
M-CD-CALL→D22 (+D23, D24, D26, D27) · M-CD-EMPTY→D23 · M-CD-NCABS→D26 (+D28) ·
M-CD-NCRAW→D25 (+D26, D28) · M-CD-ROOTREL→D27 · M-CD-SCRUB→D20 (+D22, D25)

Each mutant's recipe is content-anchored and asserts uniqueness against the candidate; all 14 anchor
strings occur exactly once in the candidate bytes (checked).

## Findings

**HIGH — the battery's 14 mutants cover 16 of 30 declared protections; 14 declared
protections have no mutant.** The round-68 C1 target is "each of the 14 battery mutants … exits 1",
i.e. the battery is the calibration instrument and the count is the number of declared-protection
mismatches. But the lane declares 30 protections (30 rows above) and only 16 of them are attacked
by any mutant. Every declared-protection claim the battery cannot test is a claim the round-68
measurement cannot refute. Two of these gaps are structural, not incidental:

**HIGH — D02/D03/D04 (unmerged, gitlink, absent index classes) have no matrix row either.**
`census/round-68/c1-matrix.tsv` expected_class column contains exactly seven distinct refusal
classes (`lane worktree is dirty` on C V1 E3 W4 PK3 PK4 PK6 PK7; `RECEIPT-ENV-COMMONDIR-MISMATCH`
on W1 W2 W5; `RECEIPT-ENV-CONFIG-SET` on E1 E2; `RECEIPT-ENV-REDIRECT-SET` on E4 E5 E6;
`RECEIPT-INDEX-ENV-SET` on N3 P13; `RECEIPT-INDEX-FLAG-CONCEALED` on D N4;
`RECEIPT-STATE-CHANGED-DURING-RUN` on T1 T2 T3 T5 N1 N2 MOD SY2 MOD2 MOD3 SY3) — none of them is
`RECEIPT-INDEX-UNMERGED`,
`RECEIPT-GITLINK-CONCEALED` or `RECEIPT-INDEX-CONCEALED-ABSENT`. `grep -c UNMERGED` on
`census/round-68/c1-counter.py` is 0. So these three refusal classes are declared by the writer
(writer:139, :143, :147) and asserted by the writer's own selftest (writer:1009, :1028, :1043) but are
observed by neither the battery nor the frozen matrix. They are invisible to the round-68 C1
measurement entirely.

**MEDIUM — D30 (no refusal message prints a caller value) has neither a mutant nor a matrix row.**
`RECEIPT-INDEX-ENV-SET` is asserted by matrix rows N3 and P13, but the counter's judge is a
substring check on the refusal class, so a message that printed the value would still pass. The
writer's selftest checks this (writer:1381, :1427 "GIT_COMMON_DIR value echoed"), but the frozen
counter does not. A leak in the refusal text is therefore not detectable by C1.

**MEDIUM — D18 (`GIT_OPTIONAL_LOCKS=0`) and D19 (`core.fsmonitor=false`) are declared in the writer
docstring only, not in SKILL.md.** `grep -n 'OPTIONAL_LOCKS\|core.fsmonitor' SKILL.md` returns only
line 671 (a different tool, the r52 fleet-root census) and line 390. Neither r66 SKILL.md:870 nor any
other round-61/62/65/66/67 SKILL section names them. They are real pins (writer:100, :105) and
`core.fsmonitor=false` is a genuine concealment defence (the writer's own selftest case 16 asserts
it), but they are not lane-declared in the sections under audit, and no mutant and no matrix row
covers them.

**MEDIUM — stale statement in SKILL.md:839.** The round-62 section still says "a permission change is
checked on its permission bits only (setuid, setgid and sticky bits are not)", while SKILL.md:870
(round 66) says "The in-run snapshot mode byte carries setuid, setgid and sticky bits
(`st_mode & 0o7777`)" and the writer implements `st_mode & 0o7777` at writer:183. The round-62
sentence is a superseded statement left un-struck. It contradicts D09 (the `0o7777` protection, K5's
target) inside the same file the round-68 C2 counter reads. The r62 section is the section this seat
was told to read, and it declares a protection (permission bits NOT covered) that the writer no
longer has. This is a documentation defect in a frozen-adjacent surface, not a writer defect.

**LOW — D21 (`GIT_DIR`/`GIT_WORK_TREE` scrub) is untested.** M-CD-SCRUB removes only `GIT_COMMON_DIR`
from the scrub tuple (writer:99) and leaves `GIT_DIR`/`GIT_WORK_TREE` in place, so no mutant in the
battery touches D21 and no matrix row exercises it. The writer's selftest does not cover it either.

**LOW — D07/D08/D10 are declared twice at different granularity.** D07 (`status.showUntrackedFiles=all`)
is declared at SKILL.md:851 and writer:46; D08 (mode beside digest) at SKILL.md:851 and writer:50;
D10 (symlink never followed) at SKILL.md:851 and writer:52. SKILL.md:851 names the matrix row ids
(V1/V2, MOD, SY1/SY2) next to each, so these three are lane-declared and observable — but they have
no mutant, so a round-68 battery run cannot distinguish "the protection holds" from "the battery
never tried".

## Files written

- `.ufo/waves/round-68/w1/S68ScoutDeclared/declared-protections.tsv` (30 rows, 5 columns)
- `.ufo/waves/round-68/w1/S68ScoutDeclared/summary.md` (this file)
- `.ufo/waves/round-68/w1/S68ScoutDeclared.md` (the seat report)

No lane tracked file, no file under `census/round-68/`, and no `.ufo/state/` file was modified.
