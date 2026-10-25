# Census delta — `corpus/SOURCES.md`, round 26 (C2 / K3 support table)

Measured with the frozen census block at `/home/vgpnk/Projects/shokunin/CORPUS.md:131-149`
("### Census — run from the lane root (tested 2026-10-19 on a synthetic table)", CORPUS.md:131).
That file is at the **fleet root**; the lane carries no `CORPUS.md`.

## States measured

| | Revision | `corpus/SOURCES.md` sha256 | Lines | Rows |
|---|---|---|---|---|
| BEFORE | `89e0fceeefcf28db313c94120be6d25e03c60094` (= base `0eca7c8a…`, same `corpus` tree `a82d8a90…`) | `8252728f8fde08004b67492c1b9098d688c904149188248bb66cb7f2853d5859` | 200 | S001–S127 |
| AFTER | `0c92c2e6fbe18f2f3009504d87240b6a22ad3d5b` (HEAD; file unchanged since `0833de9`) | `03bd96c16ed03dabae13993b930324f14345486032f1e922db9425be99692736` | 205 | S001–S132 |

Both trees reconstructed rev-faithfully under `/var/tmp` with `git archive <rev> corpus tools`
(so the `used-by` arm's `[ -e ]` resolves against that revision, not the live lane).
The AFTER bytes are byte-identical to the live working tree and to `0833de9:corpus/SOURCES.md`.

## Delta table

| Arm (frozen command) | Before `0eca7c8`/`89e0fcee` | After HEAD `0c92c2e` | Δ |
|---|---|---|---|
| rows | 127 | 132 | **+5** |
| malformed rows (NF≠13) | 0 | 0 | 0 |
| tier A | 120 | 125 | **+5** |
| tier B | 5 | 5 | 0 |
| tier C | 2 | 2 | 0 |
| status mined | 103 | 108 | **+5** |
| status queued | 15 | 15 | 0 |
| status rejected | 9 | 9 | 0 |
| duplicate ids | none | none | — |
| enum / tier-inflation findings | 0 | 0 | 0 |
| mined `used-by` paths missing | 0 | 0 | 0 |
| distinct mined `used-by` paths | 25 | 27 | **+2** |
| ids contiguous S001..Sn | yes | yes | — |
| validator (`--file`) | exit 0, 0 E / 34 W04 | exit 0, 0 E / 34 W04 | unchanged |

Expected after-state from the append block agrees exactly: 5 rows, every one tier A / status
mined, kinds `docs`×1 `code`×2 `own-work`×2 (all in enum, no `community`), 11 cells / 13 fields
each, no literal or escaped `|`, `used-by` naming only the two admitted entries; sections after
the registry shift by +5 (`## Paths` 150→155, `## Search log` 158→163, `## Leads` 188→193);
`S127` stays at line 148 and `S128`–`S132` occupy lines 149–153.

Supplemental reverse check (beyond the frozen arms): entry `git-auto-maintenance-trigger-set.md`
cites S128/S129/S130; `…-r23.md` cites S131/S129/S130/S128/S132; every appended `used-by` cell
lists exactly those entries — no omission in either direction, no cited row outside S128–S132.

## Paste-ready block for the report's Sources & frontier section

```text
Census delta, corpus/SOURCES.md (frozen commands, /home/vgpnk/Projects/shokunin/CORPUS.md:131-149)

    arm                              before 0eca7c8/89e0fcee   after HEAD 0c92c2e
    rows                             127                       132        (+5)
    malformed rows                   0                         0
    tier A / B / C                   120 / 5 / 2               125 / 5 / 2 (+5 A)
    status mined / queued / rejected 103 / 15 / 9              108 / 15 / 9 (+5 mined)
    duplicate ids                    none                      none
    enum / tier-inflation findings   0                         0
    mined used-by paths missing      0                         0
    distinct mined used-by targets   25                        27         (+2)
    validator --file                 exit 0, 0 E / 34 W04       exit 0, 0 E / 34 W04

  before: 89e0fceeefcf28db313c94120be6d25e03c60094, SOURCES.md sha256 8252728f…, 200 lines
          (identical corpus tree and file bytes at lane base 0eca7c8a…)
  after:  0c92c2e6fbe18f2f3009504d87240b6a22ad3d5b, SOURCES.md sha256 03bd96c1…, 205 lines
          (identical to 0833de9 and to the live working tree)
  append: 5 rows S128-S132, all tier A / status mined, kinds docs 1, code 2, own-work 2;
          11 cells each, no literal or escaped pipe; used-by names only the admitted entries.

  Raw outputs (before; after differs only as shown in the table):
    CMD1 rows: 127
    CMD2 malformed: 0
    CMD3 tier: A=120 B=5 C=2
    CMD4 status: mined=103 queued=15 rejected=9
    CMD5 dup: (no output)
    CMD6 enum: (no output)
    CMD7 used-by-missing: (no output)

  Ordering caveat: CMD7 is tree-relative. Appending the five rows to the freeze tree WITHOUT
  the two admitted entries prints 10 `missing:` lines (both entries, five rows) and the
  validator raises E11 x10; the counter is green only on the commit that lands rows and
  entries together (0833de9), which is the measured AFTER state.
```
