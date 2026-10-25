# ExecCensusAfter — round 26 census-after recipe

## Status
STATUS: PASS — `census-after-recipe.md` written with the exact validate command, the frozen §Census checks, paste-ready after values, and the expected-delta table; the planning hint's "A-tier +3" is corrected to +5 from the append block and the committed rows.

## Evidence

1. Contract read first: `.ufo/waves/round-26/preregistration.txt` (C2 K3: rows 127 → 132, malformed 0, duplicate ids none, enum none, used-by missing 0) plus amendments 1 and 2. Frozen manual block read at `/home/vgpnk/Projects/shokunin/CORPUS.md:131-151` (7 shell commands: 6 table-integrity checks + the used-by existence loop).
2. Revisions: base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`, HEAD `c5949013f89fe0b8289bdb7050ab64a47e08c911`; registry blobs `f3cffccdb15be2b8ead6cf19fda8c8a8adc145d7` (base) and `35747ad636e1824aef03c5ce4c497f6ccef6814a` (tip). The append is already committed: `git log -S'S128' -- corpus/SOURCES.md` → `0833de9`; S128–S132 sit at `corpus/SOURCES.md:149-153`.
3. Base census (`git show 0eca7c8:corpus/SOURCES.md` through the frozen commands): rows `127`; malformed `0`; tiers `A=120 B=5 C=2`; statuses `mined=103 queued=15 rejected=9`; dup ids empty; enum empty; used-by missing empty.
4. Tip census (same frozen commands on `corpus/SOURCES.md`): rows `132`; malformed `0`; tiers `A=125 B=5 C=2`; statuses `mined=108 queued=15 rejected=9`; dup ids empty; enum empty; used-by missing empty (27 distinct mined used-by paths).
5. Validate at tip: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → rc `0`, 34 `W04` lines, 0 `E` lines, final line `souji	ok	…/corpus/SOURCES.md`. `diff` against `.ufo/waves/round-26/census-before.txt` is empty (before output byte-identical).
6. Optional parser corroboration: `sources-census.sh census --root /home/vgpnk/Projects/shokunin souji` → `rows 132`, `tier.A 125`, `tier.B 5`, `tier.C 2`, `mined 108`, `queued 15`, `rejected 9`, `missing 0`, rc 0.
7. Indentation guard: `grep -cE '^ {1,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `0`, so the frozen column-zero regexes and the 0–3-space parser agree on 132.

## Findings

1. **Expected-delta table** (in `.ufo/waves/round-26/w1/census-after-recipe.md` §3): rows 127→132 (+5); tier A 120→125 (+5); B 5→5; C 2→2; mined 103→108 (+5); queued 15→15; rejected 9→9; malformed 0→0; dup ids none→none; enum none→none; used-by missing none→none; validate rc 0→0, W04 34→34, E 0→0. Location: `corpus/SOURCES.md`, `CORPUS.md:131-151`.
2. **A-tier correction:** the assignment's "A-tier +3?" is unsupported. All five appended rows are tier A and mined — S128 docs/A, S129 code/A, S130 code/A, S131 own-work/A, S132 own-work/A (`corpus/SOURCES.md:149-153`; draft cells in `.ufo/waves/round-26/w1/sources-append-block.md`). A rises by 5 exactly; B/C/queued/rejected are unchanged, so no existing row was re-tiered. Sums balance: 125+5+2 = 132.
3. **W04 unchanged:** 34→34 because the five new rows add no duplicate URL+scope pair (two new github tag URLs; S131/S132 own-work with no URL). W04 is warning-only per `scripts/sources-census.sh:33` ("W04 same URL across scopes (warnings do not affect clean lanes)"). [INFERENCE on the cause of the constant count; the counts are observed.]
4. **"Six greps" vs seven commands:** `CORPUS.md:131-151` contains seven shell commands. The recipe numbers the six greps/awks as checks 1–6 and the block's seventh command (mined used-by existence loop) as check 7; all seven are required by K3's used-by arm, so none were dropped.
5. **Tip stability:** HEAD already carries the append; the working tree's only modifications are `census/round-26/records/c3-{before,after}.tsv` and untracked wave files, and `git status --porcelain corpus/SOURCES.md` is empty, so the after-values are reproducible at this tip. A later tip that leaves `corpus/SOURCES.md` unchanged keeps them [INFERENCE].
6. **Recipe location:** `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/census-after-recipe.md`. No lane edits beyond that file and this report; no tools installed; scratch `/var/tmp/souji-r26-ExecCensusAfter/` removed.

## Attack log

- No attack on a predicate, target or case set; no amendment proposed. The census counters are honest and non-gameable here: row count, tier/status sums and the validate output all agree, and the before/after validate bytes are identical.
- Two contract-text observations are recorded instead: (a) the planning hint "A-tier +3" contradicts the frozen append block (all five rows tier A → +5), which the recipe corrects; (b) the task phrase "six manual census greps" undercounts the frozen block's seven commands, so the recipe includes the seventh (used-by loop) explicitly. Both are planning-text defects, not counter defects — no post-data change to any predicate is implied.
