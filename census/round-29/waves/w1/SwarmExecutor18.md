# SwarmExecutor18 — Q60/Q61/Q62 falsifiability proof (souji r29 w1)

## Status

STATUS: PASS — all three proposed quality criteria are falsifiable at base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`: each named checker returns non-clean for the named reason at base and clean after a minimal repair committed on an independent scratch branch. Every checker run was executed against the scratch clone `/var/tmp/souji-r29-QCriteriaRedBefore/c` (toplevel verified); no lane file was written except this report and the delivery TSV.

## Evidence

Setup (clone + toplevel proof):

```
git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r29-QCriteriaRedBefore/c
git -C /var/tmp/souji-r29-QCriteriaRedBefore/c rev-parse --show-toplevel
/var/tmp/souji-r29-QCriteriaRedBefore/c
```

Tool identity — the two named checkers do not exist at base; both are committed at the prereg revision, and the lane file bytes equal the committed blob (sha256, base rev vs lane path):

```
tools/souji-registry-agreement.py  committed@b8cb4b31=51131fe7…  lane=51131fe7…  same=yes
census/round-29/c2-counter.py      committed@b8cb4b31=5ab641c4…  lane=5ab641c4…  same=yes
```

Repairs are separate branches, each parented on the base commit (`git log --oneline -2 <branch>` shows base `691dd29` as parent):

| criterion | repair tip | minimal repair |
|---|---|---|
| Q60 | `69b06858c4f327e443cf03167be01abef6fc78fa` | one `- reading:` bullet appended to the `## Gate` of `corpus/lessons/round-28.md` |
| Q61 | `0e548cb1881ce5599f8da9ce6f36be3637b3bb6f` | r26 manifest rebuilt over committed bytes: `base_records=1382 dropped_absent=152 kept=1230 symlinks=14 new_records=1231`; 14 committed symlinks accounted in `census/round-26/waves/symlinks.tsv`, which is itself recorded |
| Q62 | `c694719f50f7f3972e010a9d8b74dd26c4153e47` | 5 `used-by` cells gain the citing entry, the S215 entry gains a `source: S215 …` line, 4 append-only `R29-CORRECTION` lines appended at EOF (no line shifts) |

### Q60 — excluded-clause reading

Frozen clause, `census/round-28/records/preregistration.txt:7`: "S119 row, if appended, is not counted in this claim".

The lesson's miss ruling, `corpus/lessons/round-28.md:22`: "The frozen registry-row counter is 139 because the separately admitted S119 decision yields S215; the frozen target 138 is missed."

Designed checker (one line; full verbatim command in the delivery TSV, column `checker`):
`python3 -B -c '<scan>' /var/tmp/souji-r29-QCriteriaRedBefore/c <REV> 28` — reads `census/round-28/records/preregistration.txt` and `corpus/lessons/round-28.md` with `git cat-file`, collects every parenthesised `not counted in this claim` clause with its `S###` id and the frozen target from the `N→M` counter pair before it, and requires a `reading:` line before the after-data sections naming both tokens; exit 0 all read, 1 unread, 2 no clause found.

```
base      (691dd29211c53d0ef94fa072394cb9c8a69fe92e)  Q60 clauses=1 readings=0 unread=1 / UNREAD S119 138   rc=1
repaired  (69b06858c4f327e443cf03167be01abef6fc78fa)  Q60 clauses=1 readings=1 unread=0                      rc=0
control   (32c0fe6876335b9d21ef8fc720d9c1d9cc54064f)  Q60 clauses=1 readings=1 unread=1 / UNREAD S119 138   rc=1
round 27  (691dd292…)                                 Q60 clauses=0 readings=0 unread=0                      rc=2
```

The control branch adds a `reading:` line that omits `S119`; round 27 has no such clause, so the checker refuses to call a vacuous scan clean.

Round-27 provenance for the rc 2 path: `census/round-27/records/preregistration.txt` and `corpus/lessons/round-27.md` both exist at base, and `git show 691dd292…:census/round-27/records/preregistration.txt | grep -c "not counted in this claim"` returns `0` — the refusal is a real no-clause evaluation, not a missing file.

### Q61 — receipt/manifest counter over committed bytes

`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/c2-counter.py --root /var/tmp/souji-r29-QCriteriaRedBefore/c --rev <REV>`

```
base (691dd29):
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e    rc=1

repaired (0e548cb):
r26 records=1231 failed=0 uncovered=0 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=0e548cb1881ce5599f8da9ce6f36be3637b3bb6f    rc=0

junk control (d14d3646107b6a8a8ba05b5b32a339abd8513705 — drop the 152 failing records only, no symlink accounting):
r26 records=1230 failed=0 uncovered=14 floor_violation=0
SUMMARY manifests=3 failed=0 uncovered=14 floor_violations=0 rev=d14d3646107b6a8a8ba05b5b32a339abd8513705    rc=1
```

### Q62 — bidirectional used-by/source citation

`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-registry-agreement.py --root /var/tmp/souji-r29-QCriteriaRedBefore/c --rev <REV> --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804`

```
base (691dd29):
K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md
K1 cited-not-in-used-by S075 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S076 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S022 corpus/knowledge/quarantine-origin-record-fields-r24.md
K1 cited-not-in-used-by S024 corpus/knowledge/quarantine-same-filesystem-rename.md
K1 cited-not-in-used-by S025 corpus/knowledge/quarantine-same-filesystem-rename.md
K2 uncorrected LOG.md:1758
K2 uncorrected SCORECARD.md:23
K2 uncorrected corpus/lessons/round-28.md:22
K2 uncorrected corpus/lessons/round-28.md:40
SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e    rc=1

repaired (c694719):
SUMMARY k1=0 k2=0 mismatches=0 rev=c694719f50f7f3972e010a9d8b74dd26c4153e47    rc=0

committed-bytes check: the same command at the base rev, with the Q62 repairs present only in the scratch
worktree, still printed "SUMMARY … mismatches=10" and rc=1
```

Tooling: no tools installed or upgraded (python3 3.14.8, `python3 -B` throughout). Lane `git status --porcelain` before and after this seat: only `.ufo/waves/round-26/w1/ScribeGateDraft.md` modified (pre-existing, another seat's file; untouched).

## Findings

1. **Q60 fails as proposed at base.** `corpus/lessons/round-28.md` at `691dd29` carries no `reading:` line at all (`readings=0`), so its ruling that the frozen 138 target "is missed" (`corpus/lessons/round-28.md:22`) is recorded without any reading of the clause at `census/round-28/records/preregistration.txt:7` that excluded the appended S215 row. The proposed criterion is falsifiable — but only with a checker that binds a reading to the clause's row id and frozen target; a "any reading line" scan is satisfied by the control at `32c0fe6`.
2. **Q61 fails at base for the named reason, round-scoped.** Only r26 is red (`failed=152 uncovered=14`); r27 (124) and r28 (75) are clean, so the criterion measures per-manifest committed-bytes agreement and per-wave coverage, not a lane-wide property. Location: `census/round-26/waves/manifest.sha256` at `691dd29`.
3. **Q62 fails at base in both directions.** `corpus/SOURCES.md` at `691dd29`: S215's `used-by` names an entry that never cites it, while S022/S024/S025/S075/S076 are cited by entries that their `used-by` cells omit. The S215 half is the r28 defect 5 shape: the row and the entry disagree about the same relationship.
4. **Q62 as proposed is narrower than the checker named for it.** The criterion is the bidirectional citation (k1), but `souji-registry-agreement.py` exits 0 only when the four K2 stale statements are also corrected; a lane that satisfied the citation criterion alone would stay red. Adopting Q62 with this checker silently imports K2 into Q62 (reported as an attack below; no predicate change proposed by this seat).
5. **[INFERENCE] The designed Q60 checker verifies the recording duty, not the arithmetic.** It requires the clause id and the frozen target number before the after-data sections but does not recompute `139 − 1 = 138`; a reading line naming both tokens while stating a wrong application would pass. The arithmetic half remains the frozen C2 counter's job.
6. **Recommended landing for Q60 if adopted:** a committed tool (e.g. `tools/souji-clause-reading-check.py`) plus an r28 regression fixture red at `691dd29` and green at `69b0685`, and the `32c0fe6` negative control. This seat delivered only a command, per the assignment.
7. **Q60 boundary definition [INFERENCE for other rounds].** "Before any after-data" is implemented as the lesson text before the first `## Receipts|Mistakes|Residuals|Wave` heading, matching the schema in `corpus/lessons/round-28.md` (Gate, Findings, Receipts, Mistakes, Residuals, Wave). A round with different headings would need the boundary re-declared; verified only for round 28.

## Attack log

| # | attack | target | result |
|---|---|---|---|
| A1 | satisfy Q60 with any prose about an exclusion | Q60 | refuted by `32c0fe6`: `readings=1` but `unread=1`, rc 1 — the row id binding is what makes the criterion bite |
| A2 | pass Q60 vacuously where the clause phrasing is absent | Q60 | refuted by the round-27 run: `clauses=0` → rc 2, not clean |
| A3 | satisfy Q61 by deleting the failing records | Q61 | refuted by `d14d364`: `failed=0` but `uncovered=14`, rc 1; the green path needs the 14 symlinks plus `symlinks.tsv` recorded |
| A4 | satisfy Q61 with a tool-internal re-verify rather than committed bytes | Q61 | the counter reads only `git ls-tree`/`cat-file` at `--rev` (source read of `census/round-29/c2-counter.py`), so worktree or tool-internal state cannot substitute |
| A5 | satisfy Q62 with uncommitted edits | Q62 | refuted by execution: repairs in the worktree, base rev still `mismatches=10`, rc 1 |
| A6 | satisfy Q62 one-way only (row names entry, entry silent) | Q62 | refuted by the base output carrying both `used-by-no-cite` and `cited-not-in-used-by` lines |
| A7 | read Q62's green as citation-only | Q62 | stands: the named checker couples k1 with K2 (finding 4) — the criterion as written is falsifiable, but it cannot go green on citations alone |
| A8 | read Q60's green as proof the exclusion was applied correctly | Q60 | stands: the checker proves the reading was recorded, not that the count arithmetic is right (finding 5) |

Both standing attacks are limitations of the proposed criteria as checkable, not defects in the counters; the frozen predicates were not changed.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-q60-q62-red-before.tsv` — criterion, checker command, base result, repaired result, delta (sha256 `f9e620afe81608694fc77d466c880358b264a7dc9db23d1f55d236cbf1118cea`)
- `.ufo/waves/round-29/w1/SwarmExecutor18.md` — this report
