# ExecCensusTables — souji round 26, w1 (census before/after tables)

Leaf seat. Lane-read-only: the only writes are this report and
`.ufo/waves/round-26/w1/census-delta.md`; scratch `/var/tmp/souji-r26-ExecCensusTables/`
removed at the end. No `git`/`jj` mutation, no signal, no tool installed or upgraded.
Certification OFF, K5 HELD, F5/NAMESPACE holds untouched.

## Status

STATUS: PASS — the frozen census was run on rev-faithful before and after trees: rows
127→132, tier A 120→125, mined 103→108, and malformed / duplicate / enum / used-by-missing
stay 0 in both states; the maintained validator exits 0 on both files. The table and a
paste-ready block are at `.ufo/waves/round-26/w1/census-delta.md`. The assignment's "before =
the live tree, now" premise is stale — the append is already committed — so BEFORE was
measured at the frozen revision instead of read off the live file (Finding 1).

## Evidence

**Census block.** It is not in a lane `CORPUS.md` (no such path at any revision). It is
`/home/vgpnk/Projects/shokunin/CORPUS.md:131-149`, heading `### Census — run from the lane
root (tested 2026-10-19 on a synthetic table)` (CORPUS.md:131, opened this run). It holds
**seven** commands, not six (Finding 2).

**States.**

```
$ git -C <lane> rev-parse 0eca7c8:corpus 89e0fcee:corpus
a82d8a901d9a8bdd6cfb29378b389a73f9b6cc09   (both — base and freeze share one corpus tree)
$ git show 89e0fcee:corpus/SOURCES.md | sha256sum
8252728f8fde08004b67492c1b9098d688c904149188248bb66cb7f2853d5859   200 lines, S001-S127
$ sha256sum <lane>/corpus/SOURCES.md ; git show HEAD:corpus/SOURCES.md | sha256sum
03bd96c16ed03dabae13993b930324f14345486032f1e922db9425be99692736   (both)  205 lines, S001-S132
$ git rev-parse 0833de9:corpus/SOURCES.md HEAD:corpus/SOURCES.md
35747ad636e1824aef03c5ce4c497f6ccef6814a   (both — append landed in 0833de9)
```

Trees were rebuilt with `git archive <rev> corpus tools` into
`/var/tmp/souji-r26-ExecCensusTables/{before,after}` so every relative `used-by` path in the
frozen CMD7 resolves against that revision, not the live lane. Commands were copied
character-for-character from CORPUS.md:134-149 with only cwd differing.

**Measured (excerpt; full block in `census-delta.md`).**

```
BEFORE 89e0fcee / base 0eca7c8      AFTER HEAD 0c92c2e
CMD1 rows: 127                      CMD1 rows: 132
CMD2 malformed: 0                   CMD2 malformed: 0
CMD3 tier: A=120 B=5 C=2            CMD3 tier: A=125 B=5 C=2
CMD4 status: mined=103 queued=15 rejected=9
                                    CMD4 status: mined=108 queued=15 rejected=9
CMD5 dup: <none>                    CMD5 dup: <none>
CMD6 enum: <none>                   CMD6 enum: <none>
CMD7 used-by-missing: <none>        CMD7 used-by-missing: <none>
ids-contiguous: yes                 ids-contiguous: yes
```

Cross-checks: maintained parser `scripts/sources-census.sh census --file` reports the same
numbers for both files (`rows 127/132`, `tier.A 120/125`, `status.mined 103/108`,
`missing 0`); `validate --file` exits 0 on both with 0 E-lines and the same 34 pre-existing
W04 duplicate-URL warnings; appended rows are 13 fields / 11 cells each, no literal or
escaped `|`, all tier A / status mined / kinds `docs`,`code`,`code`,`own-work`,`own-work`.
Awk's histogram order is hash order and happened to be identical in both states.

**Controls / method corrections.**
- The CMD7 arm fired in an early incomplete mirror (no `tools/` extracted): it printed
  `missing: tools/souji-size-census.py` twice. `tools/souji-size-census.py` is present at
  `0eca7c8`, `89e0fcee` and HEAD, so those two lines were a mirror artefact; the rev-faithful
  archive removed them. That accidental positive control is the only positive control I ran
  for CMD7 — I did not build one for the knowledge-path arm.
- Inferred-not-run: nothing in this report is marked `[INFERENCE]`; every arrow rests on the
  commands above.

## Findings

1. **The BEFORE state no longer exists in the working tree.** `corpus/SOURCES.md` at HEAD and
   in the live tree is already the 132-row after-state (`S128`–`S132` at lines 149–153, file
   205 lines vs 200 at the freeze); the live `git status` for `corpus/` is clean. The append
   is in commit `0833de9`, whose message names only C3 (`round-26 C3: tools/souji-axis-check.py
   + 11-case fixture …`) and which also carries both admitted entries, `corpus/README.md`, the
   snapshots and the C3 tool. Location: `corpus/SOURCES.md:149-153`;
   `git log --oneline -- corpus/SOURCES.md`. Consequence: a seat told to run the census "NOW"
   as the before state would record 132/125/108 as its baseline. I measured BEFORE at
   `89e0fcee` (= base `0eca7c8`, byte-identical `corpus` tree) instead.
2. **The census block has seven commands, not six** — rows, malformed, tier, status,
   duplicate ids, enum/tier-inflation, mined `used-by` existence
   (`/home/vgpnk/Projects/shokunin/CORPUS.md:134-149`). All seven were run; the count in the
   assignment is the only discrepancy.
3. **The assignment's `CORPUS.md` lane path is absent.** `/home/vgpnk/Projects/shokunin/
   souji-shokunin/CORPUS.md` is absent in the working tree and in all refs
   (`git log --all --oneline -- CORPUS.md` prints nothing); the frozen block lives at the
   fleet root (`CORPUS.md:131`). I read that file only; no write.
4. **CMD7 (`used-by` existence) is ordering-dependent and cannot validate the append alone.**
   Applying the five rows to the freeze tree without the two admitted entries prints ten
   `missing: corpus/knowledge/git-auto-maintenance-trigger-set*.md` lines and the validator
   raises E11 ten times (exit 1). Green appears only on the tree where rows and entries land
   together (`0833de9`). Measured: isolated append → 10 missing, validator exit 1 with
   `E11 S132 missing used-by …`; landed tree → 0 missing, exit 0.
5. **The append's arithmetic and the measured after-state agree on every arm**, including the
   line shift (`## Paths` 150→155, `## Search log` 158→163, `## Leads` 188→193) and the +2
   distinct `used-by` targets (25→27). No new validator E/W line appears from the append.
6. **Supplemental, outside the frozen arms:** `used-by`↔citation agreement for the new rows is
   exact in both directions — entry `git-auto-maintenance-trigger-set.md` cites S128/S129/S130,
   `…-r23.md` cites S131/S129/S130/S128/S132, and S128–S132 list precisely those entries; no
   cited id falls outside S128–S132. The frozen CMD7 checks only forward path existence, so
   this is corroboration, not a scored arm (same one-directional limit as LabSourcesCensus A1).

Report path written: `.ufo/waves/round-26/w1/ExecCensusTables.md`; table at
`.ufo/waves/round-26/w1/census-delta.md`. Scratch `/var/tmp/souji-r26-ExecCensusTables/`
removed.
