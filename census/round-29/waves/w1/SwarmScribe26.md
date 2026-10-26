# SwarmScribe26 — round-29 lesson `## Gate` draft (souji, lane fleet hygiene)

## Status

STATUS: PASS — `## Gate` block drafted at `.ufo/waves/round-29/w1/deliver-lesson-gate.md` with all four S216–S219 sources opened live on 2026-10-25 (bytes byte-identical to the staged snapshots), both entry ADMITs, seven REJECTs with flip conditions confirmed from each staged file's text, normalization notes, the C1 touched-row log, the two L1-filled placeholders kept visibly marked, and the pending non-author spot-check stated; `## Findings`, `## Receipts` and `## Residuals` drafted with the preregistration's evidence pointers. Two delivered quotes are not byte-verbatim and are flagged as a landing condition.

## Evidence

Base `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (preregistration commit; branch `master`). All commands read-only; scratch `/var/tmp/souji-r29-SwarmScribe26.*`, removed at the end. No tool installed or upgraded.

1. Staged snapshots verify against their own pin file:

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/sources && sha256sum -c SHA256SUMS
broder97resemblance.pdf: OK
broder97resemblance.txt: OK
cmp.1.html: OK
link.2.html: OK
statx.2.html: OK
```

2. Live re-open of all four URLs (this run, 2026-10-25), to scratch, then hashed — byte-identical to the staged snapshots:

```
statx.2.html 200 33125      sha256 2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e
link.2.html  200 19883      sha256 9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9
cmp.1.html   200 9791       sha256 5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3
broder.pdf   200 254930     sha256 da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b
```

3. Broder decode reproduced here: `pdftotext broder.pdf broder-default.txt` → sha256 `3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d`, equal to the staged decode hash; the Abstract sentence is present at decoded lines 7-9.

4. DOI locator claim re-observed, not taken from another seat:

```
$ curl -sS -o /dev/null -w '%{http_code} %{size_download}\n' -L 'https://doi.org/10.1109/SEQUEN.1997.666900'
202 0
```

5. Page identity lines inside the opened bytes: `Linux man-pages 6.19  2026-02-08  statx(2)` (statx.2.html:587), `Linux man-pages 6.19  2026-02-11  link(2)` (link.2.html:310), `diffutils 3.12.26-bbc1  August 2026  CMP(1)` with generation date 2026-08-03 (cmp.1.html:147,156).

6. Quote fidelity measured against the opened bytes (whitespace-normalised for line wraps, which is the convention the r28 Gate used):

```
S216_struct_inline  exact_ws=True  bytes=False  words=5   (served: "stx_ino;         /* Inode number */")
S216_prose_ino      exact_ws=True  bytes=True   words=6
S217_abstract       exact_ws=True (decoded) words=24
S218_original       exact_ws=False bytes=False  words=10  (served: was the "original".)
S218_samefile       exact_ws=True  bytes=True   words=7
S218_newname_op     exact_ws=True  bytes=False  words=14  (line break only)
S219_exit           exact_ws=True  bytes=False  words=15  (line break only)
```

7. Reject grounds verified by substring search in each staged file (all True, all ≤25 words, none containing `|`): threshold-r28:7, operating-point-r28:19, relations-r29:16 and :33, literature-identity-r33:5, threshold-source-r34:6, decision-r25:5, decision-r26:7.

8. Base state re-measured for the drafted Findings (not copied from `controls.tsv`):

```
$ git grep -lE '^ground: F3' HEAD -- corpus/knowledge/ | wc -l                 -> 0
$ git show HEAD:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'  -> 139
$ grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S21[6-9][[:space:]]*\|' corpus/SOURCES.md  -> 0 0 0 0
```

The four stale phrases are still at `LOG.md:1758`, `SCORECARD.md:23`, `corpus/lessons/round-28.md:22` and `:40` at base. Touched-row old cells re-observed at base: S022 `mined` / one used-by; S024 and S025 `queued` / `—`; S075 and S076 `mined` / `corpus/lessons/round-18.md`; S215 `mined` / `corpus/knowledge/git-auto-maintenance-trigger-set.md`. Citation directions of the repair table re-checked: `quarantine-origin-record-fields-r24.md:4` cites S022; `quarantine-same-filesystem-rename.md:1` cites S024 and S025; `process-residue-observations.md:1` cites S075 and S076; `grep -c S215 corpus/knowledge/git-auto-maintenance-trigger-set.md` → `0`.

9. Staged registry rows: each of S216–S219 has 11 fields (13 split parts with the outer pipes) and no escaped or literal pipe in any cell.

10. Read-time tree state: `git status --porcelain` → ` M .ufo/waves/round-26/w1/ScribeGateDraft.md`; not touched (outside this seat's write scope).

## Findings

1. **Gate block delivered** at `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-lesson-gate.md`, shaped like `corpus/lessons/round-28.md` `## Gate`: four row ADMITs (S216 statx(2), S217 Broder PDF, S218 link(2), S219 cmp(1)) each with URL, access date 2026-10-25, snapshot digest and a located byte-verbatim quote of ≤25 words (§ S216 statx.2.html:323; S217 decoded text 7-9; S218 link.2.html:101; S219 cmp.1.html:113-114).
2. **Entry ADMITs recorded** for `duplicate-verdict-identity.md` and `duplicate-verdict-byte-equality.md`, both with `ground: F3` and the provenance trio present in the delivered entry files; neither supersedes an entry, and neither creates a class or threshold.
3. **Two delivered quotes are not byte-verbatim.** (a) `deliver-duplicate-verdict-identity.md` Gate quotes S216 as `stx_ino; /* Inode number */`; the served bytes are `stx_ino;         /* Inode number */` (statx.2.html:97). (b) `deliver-sources-append-block.md` Gate-quote table quotes S218 as `it is impossible to tell which name was the original`; the served bytes are `which name was the "original".` (link.2.html:102-103). Both are flagged in the Gate with byte-exact replacements (`The inode number of the file.`, `both names refer to the same file`); under the frozen kill rule the first must be replaced or the whitespace convention recorded before the identity entry lands.
4. **Seven REJECTs confirmed from the staged text**, each with reason and flip: the five `near-duplicate-*` entries are document-similarity ground outside PROVINCE F3's byte-identical scope (`PROVINCE.md:69`); `near-duplicate-literature-identity-r33.md` is narrower still — a bibliographic identity record that itself records the paper's full text was not obtained; `duplicate-receipt-class-decision-r25.md` and `-r26.md` are operator-decision records (own-work evidence `r25-receipt-taxonomy.out`, `r26-operator-decision-record.out`), not facts.
5. **Normalization notes recorded**: 11-column rows with 11 fields, zero pipes; `status mined`, `opened 2026-10-25`, `recheck 365d`; campaign recheck prose stripped for all four rows (two `on-release` cadences replaced by `365d`, recorded as a tightening); `used-by` exactly the citing admitted entries; anchors and `teaches` cells rewritten in the seat's words.
6. **Touched-row log tabled** (9 cell changes over 6 rows, old → new, plus the explicit statement that no existing row's `recheck` cell changes), transcribed from the C1 repair table and marked for L1 reconciliation against the landed rows.
7. **Placeholders kept visibly unfilled**: `<collisions=N>` (source `.ufo/waves/round-29/w1/assimilation/collisions`, guard proof in `deliver-collision-guard-proof.md`) and the campaign-register-row-S118 quarantine `<verdict>` (sources `deliver-slice-verdicts.tsv`, `assimilation/quarantine-slice`, prior `census/round-24/records/slice-verdicts.tsv`). No number or verdict was invented.
8. **Spot-check note included**: no independent non-author spot-check is on record; lane-dispatched seats do not satisfy the closure duty.
9. **S216 reuses S114's URL** (`corpus/SOURCES.md:135`) under a different scope. Expected census effect is one more W04 duplicate-URL warning and no E04; the curation line is that S216 must not claim S114's origin-record ground.
10. **Read-time tracked edit** `M .ufo/waves/round-26/w1/ScribeGateDraft.md` observed at base; recorded in the Gate and left untouched.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-lesson-gate.md` — the `## Gate` block plus the `## Findings`, `## Receipts`, `## Residuals` drafts for `corpus/lessons/round-29.md`.
- `.ufo/waves/round-29/w1/SwarmScribe26.md` — this report.
