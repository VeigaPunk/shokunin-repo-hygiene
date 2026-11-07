# S68ScoutDeclared — declared-protection inventory for the round-68 C1 writer

**Verdict:** the lane declares **30** protections on the round-68 candidate writer
(`tools/souji-receipt-write.py`, blob `f70da577eb1e1624cc63ab8fd0468565927d9b6a`, sha256
`b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725`). **16** are removed by a battery
mutant, **14** are not (`U`). All 14 battery mutants are referenced by exactly one protection each;
there is no orphan mutant and no unnamed mutant.

Files written (all under my seat dir):
- `.ufo/waves/round-68/w1/S68ScoutDeclared/declared-protections.tsv` — 30 rows, columns
  `id, protection, declared-in (file:line), writer-anchor (file:line at f70da577), battery-mutant or none`
- `.ufo/waves/round-68/w1/S68ScoutDeclared/summary.md` — N/M/U, the U names, the full mutant map, findings
- `.ufo/waves/round-68/w1/S68ScoutDeclared.md` — this report

Read-only: no counter run, no mutant generated, no file under `census/round-68/` touched, no lane
tracked file edited, no git mutation. Scratch dir `/fast/scratch/hyaku/souji-r68/S68ScoutDeclared/`
removed on exit.

## Commands run (evidence)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f70da577eb1e1624cc63ab8fd0468565927d9b6a:tools/souji-receipt-write.py
grep -n '^## \|^### ' SKILL.md            # 815 Round 61, 833 Round 62, 842 Round 65, 861 Round 66, 881 Round 67
cat census/round-68/battery/SHA256SUMS   # 14 mutant ids + candidate sha256
cat census/round-68/mutate-writer.py     # MUTANTS table, lines 17-55
cat census/round-68/c1-matrix.tsv        # 42 rows
sed -n '260,330p' census/round-68/c1-counter.py   # CASE_SPECS
```

Deciding observed lines:

- `grep -c UNMERGED census/round-68/c1-counter.py` → `0`; `grep -c GITLINK` → `0`;
  `grep -c CONCEALED-ABSENT` → `0`.
- `awk -F'\t' 'NR>1 && $3!="-"{a[$3]=a[$3]" "$1}' census/round-68/c1-matrix.tsv` → exactly seven
  refusal classes; none is `RECEIPT-INDEX-UNMERGED` / `-GITLINK-CONCEALED` / `-CONCEALED-ABSENT`.
- `grep -n 'OPTIONAL_LOCKS\|core.fsmonitor' SKILL.md` → only line 671 (the r52 census tool) and 390;
  neither r66 SKILL.md:870 nor any round-61/62/65/66/67 section names them.
- Writer:100 `env["GIT_OPTIONAL_LOCKS"] = "0"`, writer:105 `"core.fsmonitor=false"`.
- Writer:183 `mode = oct(os.stat(full).st_mode & 0o7777).encode("ascii") + b":"`.
- SKILL.md:839 ends "a permission change is checked on its permission bits only (setuid, setgid and
  sticky bits are not)"; SKILL.md:870 says "The in-run snapshot mode byte carries setuid, setgid and
  sticky bits (`st_mode & 0o7777`)".
- All 14 mutant anchor strings occur exactly once in the candidate bytes (checked by script).
- Every `file:line` in the TSV resolves inside the cited file (checked by script; SKILL.md 896 lines,
  writer 1591 lines).

## Findings

**HIGH — 14 of 30 declared protections have no battery mutant.** The round-68 C1 target is "each of the
14 battery mutants … exits 1"; the count is declared-protection mismatches. Only 16 of the 30 declared
protections are attacked. U rows (named in `summary.md`): D01 index-flag refusal, D02 unmerged class,
D03 gitlink class, D04 absent class, D05 in-run re-read, D06 `--allow-dirty` content snapshot,
D07 `status.showUntrackedFiles=all` override, D08 mode beside digest, D10 symlink-never-followed,
D18 `GIT_OPTIONAL_LOCKS=0`, D19 `core.fsmonitor=false`, D21 `GIT_DIR`/`GIT_WORK_TREE` scrub,
D29 `:(top)` pathspec, D30 no-caller-value-in-messages.

**HIGH — D02/D03/D04 (`RECEIPT-INDEX-UNMERGED`, `RECEIPT-GITLINK-CONCEALED`,
`RECEIPT-INDEX-CONCEALED-ABSENT`) are invisible to the whole round-68 C1 measurement.** No battery
mutant removes them and no matrix row observes them (`grep -c UNMERGED`=0 in the counter; the seven
matrix refusal classes exclude all three). The writer declares them (writer:139, :143, :147) and its
own selftest asserts them (writer:1009, :1028, :1043), but C1 can neither refute nor confirm them.

**MEDIUM — D30 (a refusal message must not print the caller value) is unobservable by C1.** The
counter's judge is a substring check on the refusal class (`findings_for(n_v, n_se, klass)`), so a
message that echoed `GIT_INDEX_FILE`/`GIT_COMMON_DIR` would still pass N3/P13/W1-W6. The writer's
selftest does check it (writer:1381, :1427).

**MEDIUM — D18 and D19 are writer-docstring-only declarations.** `GIT_OPTIONAL_LOCKS=0` (writer:100)
and `core.fsmonitor=false` (writer:105) are real pins; `core.fsmonitor=false` is a genuine concealment
defence the writer's selftest case 16 asserts, but neither is named in the SKILL.md rounds under audit,
and no mutant or matrix row covers either.

**MEDIUM — stale statement at SKILL.md:839.** The round-62 section still claims setuid/setgid/sticky
bits are not checked; SKILL.md:870 (round 66) and writer:183 both carry `0o7777`. The round-62
sentence contradicts the very protection K5 removes (D09) inside the file C2 reads.

**LOW — D21 (`GIT_DIR`/`GIT_WORK_TREE` scrub) untested.** M-CD-SCRUB removes only `GIT_COMMON_DIR`
from the tuple (writer:99); no mutant or matrix row exercises D21.

**LOW — D07/D08/D10 are declared at two granularities** (SKILL.md:851 with matrix ids V1/V2, MOD,
SY1/SY2 alongside; writer:46, :50, :52). Observed by the matrix but not by any mutant, so a round-68
battery run cannot separate "the protection holds" from "the battery never tried".

## Note for the integrator (L1)

The round-68 C1 measurement is a **battery** measurement: its power is bounded by the 14 mutants.
This inventory shows the lane's declared surface is 30 protections, so a green C1 run
(`class_mismatches=0`) refutes nothing about the 14 unmutated rows, and 7 of those 14 (D02, D03, D04,
D18, D19, D21, D30) have no matrix row either — they are entirely outside the round-68 instrument.
That is a scope fact about the frozen instrument, not a defect in the candidate writer, and it is
consistent with the preregistration's own named limit (L3): "`GIT_NAMESPACE` and
`GIT_CEILING_DIRECTORIES` have no writer row". The same shape applies one level up to
`GIT_NAMESPACE`/`GIT_CEILING_DIRECTORIES` (neither refused nor pinned, SKILL.md:888) — they are
declared as absent, not as protected, and correctly carry no row.

## Tooling

No tool was installed or upgraded for this seat (read-only inventory; `python3` from the base image
was sufficient). No pacman transaction was run, so the paused-pacman ruling was not engaged.
