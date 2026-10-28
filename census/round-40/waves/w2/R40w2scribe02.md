# R40w2scribe02 — Sources & frontier evidence

## Verdict: SAFE (sources/frontier reporting slice)

### Draft `## Sources & frontier`

> **Registry count:** At the frozen round-40 base `0242085909fb6a4ee041c5443d76316ac6d59d4b`, `corpus/SOURCES.md` had **174 rows**; at landed instrument commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`, it had **178 rows** (**+4**). The counting command was `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`; at the final recorded census it reported `SUMMARY rows=178 W04=49 rc=0 measured_at=8a5fbdbddaab24c5ba43fc6a133499efb405f214 registry=corpus/SOURCES.md`, followed by `# census exit: 0`. The actual run returned exit 0. For the before/after revision count: `for rev in 0242085909fb6a4ee041c5443d76316ac6d59d4b 128e412b0ced3c243dc27c3dd3332054a611bc2e; do printf '%s ' "$rev"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show "$rev:corpus/SOURCES.md" | grep -Ec '^\\| S[0-9]{3,} \\|'; done` returned respectively `174` and `178`. Both registry snapshots contain tier A/B/C counts **165/6/3 → 169/6/3**.
>
> **Added/touched rows:** Four rows were added, all tier A: **S251, S252, S253, S254**. S251–S253 are `mined` sources for the C1 strict-descendant, C2 continuation-line, and C3 invalid-UTF-8 claims; S254 is a `mined` GVFS reference implementation adopted for the F4 origin-record-format surface. The `corpus/SOURCES.md` revision diff is `9 +++++++++` (9 insertions, 0 deletions); it adds a provenance paragraph and those four rows. **Touched old rows: none.** No `SOURCES: unchanged` claim applies.
>
> **Frontier/assimilation:** `corpus/README.md` adds a Round 40 frontier update and maps three C1–C3 knowledge entries onto F1 and the GVFS entry onto F4; both remain frontier and **no ground is promoted to Core**. Assimilation: one theme was adopted from `/home/vgpnk/Projects/shokuknow/merge/souji/`—the per-item origin record's GVFS read-side reference implementation, recorded as S254 and `knowledge/origin-record-format-gvfs-r40.md`; the package's 58 colliding ids are noted as an L0 question, and nothing else was adopted.

### Evidence commands and real outputs

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat 128e412b0ced3c243dc27c3dd3332054a611bc2e`

```text
commit 128e412b0ced3c243dc27c3dd3332054a611bc2e
Author: souji-shokunin <souji@shokunin.local>
Date:   Wed Oct 28 15:52:14 2026 -0300

    round-40: instruments, sources, knowledge — C1 evidence-bound counter, C2 joined docstring classes, C3 record-branch battery

 census/round-40/assimilation/collisions            |   58 +
 census/round-40/assimilation/reg-ids               |  177 ++
 census/round-40/assimilation/staged-ids            |  134 +
 census/round-40/c1-counter.py                      |  362 +++
 census/round-40/c2-counter.py                      |  341 +++
 census/round-40/c3-counter.py                      |  211 +++
 census/round-40/docstring-classes.py               |   96 +
 census/round-40/preregistration.txt                |   13 +
 census/round-40/sources/SHA256SUMS                 |    5 +
 census/round-40/sources/codecs.html                | 2312 +++++++++++++++++
 census/round-40/sources/git-merge-base.1.txt       |  191 ++
 census/round-40/sources/gvfs-trashitem-1.62.0.c    |  560 ++++
 census/round-40/sources/inspect-cleandoc.txt       |    5 +
 census/round-40/sources/inspect.html               | 2654 +++++++++++++++++++
 corpus/README.md                                   |   24 +-
 corpus/SOURCES.md                                  |    9 +
 .../docstring-class-continuation-lines-r40.md      |   50 +
 corpus/knowledge/drift-record-invalid-utf8-r40.md  |   49 +
 .../git-strict-descendant-relation-r40.md          |   43 +
 corpus/knowledge/origin-record-format-gvfs-r40.md  |   54 +
 corpus/lessons/round-40.md                         |  102 +
 tests/fixtures/r40-c1-evidence.py                  |  235 +++
 tests/fixtures/r40-docstring-joined.py             |  126 ++
 tests/fixtures/r40-drift-record-branches.py        |  150 ++
 24 files changed, 7959 insertions(+), 2 deletions(-)
```

2. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat 0242085909fb6a4ee041c5443d76316ac6d59d4b 128e412b0ced3c243dc27c3dd3332054a611bc2e -- corpus/SOURCES.md`

```text
 corpus/SOURCES.md | 9 +++++++++
 1 file changed, 9 insertions(+)
```

3. Census invocation and process exit capture:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji; printf 'command_exit=%s\\n' "$?"
```

The census emitted 49 W04 lines. Its exact summary and tail were:

```text
souji\tok\t/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
# census exit: 0
command_exit=0
```

The corresponding committed census receipt is `census/round-40/records/census-after.txt:2-4,54-55`; line 4 records `rows=178 W04=49 rc=0` and its `measured_at` revision. The runner was executed against the lane's registry at invocation time; that receipt's measured revision is later than the instrument commit, so it is not misrepresented as a census run at `128e412`.

4. Row/tier counting over those two named git revisions:

```sh
for rev in 0242085909fb6a4ee041c5443d76316ac6d59d4b 128e412b0ced3c243dc27c3dd3332054a611bc2e; do printf '%s ' "$rev"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show "$rev:corpus/SOURCES.md" | grep -Ec '^\\| S[0-9]{3,} \\|'; done
```

```text
0242085909fb6a4ee041c5443d76316ac6d59d4b 174
128e412b0ced3c243dc27c3dd3332054a611bc2e 178
```

```sh
for rev in 0242085909fb6a4ee041c5443d76316ac6d59d4b 128e412b0ced3c243dc27c3dd3332054a611bc2e; do printf '%s ' "$rev"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show "$rev:corpus/SOURCES.md" | awk -F'|' '/^\\| S[0-9][0-9][0-9] \\|/ {gsub(/[[:space:]]/,"",$5); t[$5]++; rows++} END {printf "rows=%d tier.A=%d tier.B=%d tier.C=%d\\n",rows,t["A"],t["B"],t["C"]}'; done
```

```text
0242085909fb6a4ee041c5443d76316ac6d59d4b rows=174 tier.A=165 tier.B=6 tier.C=3
128e412b0ced3c243dc27c3dd3332054a611bc2e rows=178 tier.A=169 tier.B=6 tier.C=3
```

5. Frontier diff command: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat 0242085909fb6a4ee041c5443d76316ac6d59d4b 128e412b0ced3c243dc27c3dd3332054a611bc2e -- corpus/README.md corpus/knowledge && git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --unified=0 0242085909fb6a4ee041c5443d76316ac6d59d4b 128e412b0ced3c243dc27c3dd3332054a611bc2e -- corpus/README.md`.

Output established `corpus/README.md | 24 +++++++++-`, plus four new knowledge entries (50, 49, 43, 54 lines); the README diff adds `## Round 40 frontier update`. Relevant exact claims are at `corpus/README.md:781-800`: all four entries are mapped; three F1 entries are the three claims' S251–S253; S254 belongs to F4; F1/F4 remain frontier and no ground is promoted to Core; one theme was assimilated and nothing else. The output states the package collision is 58 ids and the adopted row was pointed to S254.

### Loci attacked / limits

- Frozen base is named in `census/round-40/preregistration.txt:1`; its claims and measurements are frozen at lines 3-11. No frozen file was edited.
- Round-40 provenance and source scope are documented at `corpus/SOURCES.md:22`; the added registry rows are `corpus/SOURCES.md:203-206`. They identify S251–S254 respectively as tier-A sources, and distinguish S251's scope from S239/S244.
- Frontier mapping and no-Core-promotion statement: `corpus/README.md:781-800`.
- Source census output is preserved at `census/round-40/records/census-after.txt:2-4,54-55`.
- The count at the frozen base (174) is measured directly from its committed registry snapshot; no historical census runner was executed against a checked-out base. Current census output is from `8a5fbdb...`, later than landed `128e412...`; treat it as the final recorded census, not the landed-revision census. This scope reports the sources/frontier section only, not the C1/C2/C3 behavioral verdicts.
- Scratch directory: none created, therefore no scratch cleanup required. No tools installed; no mutation, commit, or push performed.
