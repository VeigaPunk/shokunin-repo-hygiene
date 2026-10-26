# Deliver — `corpus/lessons/round-29.md` `## Gate` block

Seat `SwarmScribe26`. Paste target: `corpus/lessons/round-29.md`, section `## Gate`
(plus the three stubbed sections below it). Lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`;
frozen preregistration `b8cb4b31ce80e2e3314b88e85d40ea9873180804`.

All four source URLs were opened by this seat on 2026-10-25. Each live fetch returned HTTP 200
and bytes byte-identical to the staged snapshot under `.ufo/waves/round-29/w1/sources/`
(digests below); the Broder PDF's decoded text was regenerated here and matched the staged
decode's sha256. No quote in this block was copied from another seat's report.

`<collisions=N>` and `<verdict>` below are **L1-filled placeholders**; this seat asserts no
number and no verdict for either.

---

## Gate

Sources opened in this lane on 2026-10-25; byte snapshots and SHA256SUMS are in `census/round-29/sources/` (staged at `.ufo/waves/round-29/w1/sources/`, digest-for-digest identical).

| Candidate | Decision | Source reopened | Located quote / evidence | Reason / flip |
|---|---|---|---|---|
| S216 `statx(2)` registry row | ADMIT | https://man7.org/linux/man-pages/man2/statx.2.html — opened 2026-10-25, live HTTP 200, sha256 `2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e`; Linux man-pages 6.19 (2026-02-08) | “The number of hard links on a file.” (§ DESCRIPTION, `stx_nlink`, snapshot line 323; 8 words). Same section, line 335: “The inode number of the file.”; § CONSTANTS line 257: `STATX_MNT_ID_UNIQUE` (since Linux 6.8) | The identity field pair a duplicate verdict must distinguish; used by `duplicate-verdict-identity.md` only. Flip: reject if the row is found to restate S114's origin-record scope (same URL, `corpus/SOURCES.md:135`) instead of answering the duplicate-verdict identity question. |
| S217 Broder 1997 registry row | ADMIT | https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf — opened 2026-10-25, live HTTP 200, 254930 bytes, PDF sha256 `da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b`; decoded text sha256 `3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d` | “their resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of “roughly the same” and “roughly contained.”” (Abstract p.1, decoded text lines 7-9; 24 words) | Vocabulary only: two measures, each a number between 0 and 1, from a web-crawl study — not filesystem verdicts, not a threshold. The DOI `10.1109/SEQUEN.1997.666900` landing page answered HTTP 202 with 0 bytes on 2026-10-25 (re-observed by this seat), so the author-hosted PDF is the locator. Used by both admitted entries. |
| S218 `link(2)` registry row | ADMIT | https://man7.org/linux/man-pages/man2/link.2.html — opened 2026-10-25, live HTTP 200, sha256 `9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9`; page dated 2026-02-11 in man-pages 6.19 | “both names refer to the same file” (§ DESCRIPTION, snapshot line 101; 7 words) | Grounds inode identity over path names; used by both admitted entries. Served bytes continue `(and so have the same permissions and ownership) and it is impossible to tell which name was the "original".` — any quote of the later clause must keep the quotation marks around `original`. |
| S219 `cmp(1)` registry row | ADMIT | https://man7.org/linux/man-pages/man1/cmp.1.html — opened 2026-10-25, live HTTP 200, sha256 `5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3`; diffutils 3.12.26-bbc1, page generated 2026-08-03 | “Exit status is 0 if inputs are the same, 1 if different, 2 if trouble.” (§ DESCRIPTION, snapshot lines 113-114; 15 words) | The three-valued byte-equality oracle, trouble kept distinct from different; used by `duplicate-verdict-byte-equality.md` only. |
| `corpus/knowledge/duplicate-verdict-identity.md` | ADMIT | Cited rows S216, S217, S218 re-opened above; all three carried by the same snapshots | Entry quotes the three rows; its provenance trio and `ground: F3` sit at lines 1-6 | Grounds F3's identity rule (inode, not path) and names the two Broder measures as vocabulary, declaring no receipt class and no threshold. Condition: its S216 Gate quote `stx_ino; /* Inode number */` collapses the served struct-comment spacing (`stx_ino;         /* Inode number */`); replace it with the byte-exact prose quote from the same section, or record the whitespace convention, before this entry lands. |
| `corpus/knowledge/duplicate-verdict-byte-equality.md` | ADMIT | Cited rows S219, S218, S217 re-opened above; all three carried by the same snapshots | Entry quotes the three rows; its provenance trio and `ground: F3` sit at lines 1-6 | Supplies the three-valued oracle plus the identity rule and supersedes nothing; all three of its Gate quotes match the opened bytes after line-break normalisation. |
| `near-duplicate-threshold-r28.md` | REJECT | `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/near-duplicate-threshold-r28.md`, opened 2026-10-25, read-only | line 7: “A near-duplicate threshold has published values, and the measure's own author disclaims the inference” (14 words) | Confirmed: document-similarity ground (ssdeep match score and near-duplicate thresholds), outside PROVINCE F3's byte-identical scope (`PROVINCE.md:69`). Flip: reconsider only if the operator opens a near-duplicate class; then this entry is evidence for the measure's own disclaimer, not a threshold. |
| `near-duplicate-operating-point-r28.md` | REJECT | same package dir, opened 2026-10-25, read-only | line 19: “repository of 8 billion web pages, 64-bit simhash fingerprints and k = 3 are reasonable (S172)” (16 words) | Confirmed: a simhash operating point measured on a web crawl — document similarity, not byte-identical copies. Flip: reconsider only if an operator ruling asks for a precedent on how a threshold is stated; the number is not adoptable on a receipt corpus. |
| `near-duplicate-relations-r29.md` | REJECT | same package dir, opened 2026-10-25, read-only | line 16: “distinct relations over a document pair” (6 words); line 33: “The corpus's `duplicate` class stays byte-equality” | Confirmed: chooses between resemblance and containment and surveys ssdeep/sdhash thresholds, i.e. the near-duplicate relation — outside the byte-identical scope, and its own conclusion keeps the class byte-equality. Flip: reconsider if the operator changes the taxonomy to a near-duplicate class. |
| `near-duplicate-literature-identity-r33.md` | REJECT | same package dir, opened 2026-10-25, read-only | line 5: “the bibliographic identity of the near-duplicate paper the ledger has chased for five rounds without naming it” (17 words) | Confirmed and narrower than the others: a bibliographic identity record (title, authors, DOI, HAL id) for the near-duplicate paper, and its own text records that the paper's full text was not obtained. It states no fact about duplicate verdicts. Flip: reconsider if the lane needs this paper's identity as registry metadata; it still grounds no verdict. |
| `near-duplicate-threshold-source-r34.md` | REJECT | same package dir, opened 2026-10-25, read-only | line 6: “the thresholds the near-duplicate literature actually sets, and how the paper's own text reaches them” (15 words) | Confirmed: ssdeep thresholds t = 60 and t = 40 taken over a 4457-file corpus — document similarity and a threshold choice, outside the byte-identical scope. Flip: reconsider only if the operator adopts ssdeep on a comparable corpus as the class's operating point. |
| `duplicate-receipt-class-decision-r25.md` | REJECT | same package dir, opened 2026-10-25, read-only | line 5: “the lane's OWN receipt taxonomy, and exactly what a `duplicate` class would have to decide” (15 words); evidence cell `r25-receipt-taxonomy.out` | Confirmed: an operator-decision record (own-work evidence, `ground: F3 — duplicate verdicts`), not a fact about the subject; it scopes the ruling the operator has not taken. Flip: never as knowledge ground; it may be cited as a decision record in a lesson or log, not admitted as an entry. |
| `duplicate-receipt-class-decision-r26.md` | REJECT | same package dir, opened 2026-10-25, read-only | line 7: “The `duplicate` receipt class is a ruling the lane has repeatedly deferred, and the deferral is on the record” (19 words); evidence cell `r26-operator-decision-record.out` | Confirmed: records the deferral of the operator decision, not a fact about byte equality. Flip: never as knowledge ground; it stops being relevant when the operator ruling lands, and the ruling itself would be the citable record. |

### Quote check of the two admitted entries (run this task, 2026-10-25)

- `duplicate-verdict-byte-equality.md`: S219, S218 and S217 quotes all match the opened bytes
  after line-break whitespace normalisation, each ≤25 words and free of `|`.
- `duplicate-verdict-identity.md`: S217 and S218 quotes match under the same rule. Its S216
  quote `stx_ino; /* Inode number */` matches only after collapsing internal spaces; the
  served bytes are `stx_ino;         /* Inode number */` (snapshot line 97). Under a strict
  verbatim reading this trips C3's kill rule, so replace it with `The inode number of the
  file.` (§ DESCRIPTION, line 335, byte-exact) or record the whitespace convention before
  landing.
- The seat-owned append block's Gate-quote table quotes S218 as `it is impossible to tell
  which name was the original`; the served bytes are `which name was the "original".`, so that
  quote is not byte-verbatim. This Gate uses `both names refer to the same file` instead.

### Normalization notes (campaign schema → fleet/census schema)

- Registry rows are 11 columns; each of S216–S219 was checked at 11 fields (`NF=13` with the
  outer pipes) with zero escaped or literal `|` in any cell. Anchors and `teaches` cells are in
  the seat's words, not the campaign's.
- `status` `mined`, `opened` `2026-10-25`, `recheck` `365d` for all four rows.
- `used-by` names exactly the admitted entries that cite the row: S216 → identity entry;
  S217, S218 → identity and byte-equality entries; S219 → byte-equality entry only.
- Campaign `recheck` prose was stripped from every row (kept here, not in the registry):

| row | campaign `recheck` cell | normalized |
|---|---|---|
| S216 | `on-release — re-read the man-pages 6.x statx(2) page` | `365d` |
| S217 | `365d — re-resolve the DOI and re-read § 2` | `365d` (DOI re-resolution is unexecutable; the PDF is the locator) |
| S218 | `on-release — re-read the man-pages 6.x link(2) page` | `365d` |
| S219 | `365d — re-fetch the man7 cmp(1) page` | `365d` |

  Replacing `on-release` with `365d` is a tightening: an on-release recheck is never overdue, a
  365d one can be.

### SOURCES touched-row log (old → new)

Transcribed from the C1 repair table `.ufo/waves/round-29/w1/deliver-c1-usedby-changes.tsv`;
the old cells were re-observed at base `b8cb4b3` by this seat. The L1 must reconcile each pair
with the landed row before this log is final. No existing row's `recheck` cell changes.

| row | column | old | new | grounds (from the repair table) |
|---|---|---|---|---|
| S022 | used-by | `corpus/knowledge/trash-spec-restorable-quarantine.md` | `corpus/knowledge/trash-spec-restorable-quarantine.md, corpus/knowledge/quarantine-origin-record-fields-r24.md` | that entry's `source:` line 4 cites S022 (re-checked this run) |
| S024 | status | `queued` | `mined` | status follows a non-empty used-by cell (`../CORPUS.md:103`) |
| S024 | used-by | `—` | `corpus/knowledge/quarantine-same-filesystem-rename.md` | that entry's `source:` line 1 cites S024 and S025 (re-checked this run) |
| S025 | status | `queued` | `mined` | same status rule |
| S025 | used-by | `—` | `corpus/knowledge/quarantine-same-filesystem-rename.md` | same entry, `source:` line 1 |
| S075 | used-by | `corpus/lessons/round-18.md` | `corpus/lessons/round-18.md, corpus/knowledge/process-residue-observations.md` | that entry's `source:` line 1 cites S075 and S076 (re-checked this run) |
| S076 | used-by | `corpus/lessons/round-18.md` | `corpus/lessons/round-18.md, corpus/knowledge/process-residue-observations.md` | same entry, field-22 and exe-suffix uses |
| S215 | status | `mined` | `queued` | used-by becomes `—`, so `mined` would be a false declaration |
| S215 | used-by | `corpus/knowledge/git-auto-maintenance-trigger-set.md` | `—` | that entry does not name S215 (`grep -c S215` → 0, re-checked this run); its `source:` lines may not be edited |

The four new rows S216–S219 add `recheck` `365d` rows; they are new rows, not touched rows.

### Id-collision guard and quarantine

- **Collision guard:** `<collisions=N>` — the L1 fills this from
  `.ufo/waves/round-29/w1/assimilation/collisions` (registry-id and staged-id extracts and the
  guard proof are in the same directory and in `deliver-collision-guard-proof.md`). Renumber is
  by document, never by arithmetic: campaign S117 → S216, S118 → S217, S122 → S218, S136 → S219.
  The four lane ids S216–S219 were unoccupied at base (0 rows each, re-checked this run).
- **Quarantine, campaign register row S118 (the Broder paper):** `<verdict>` — the L1 fills this
  from `.ufo/waves/round-29/w1/deliver-slice-verdicts.tsv` and
  `census/round-29/records/quarantine-slice`; the prior table is
  `census/round-24/records/slice-verdicts.tsv` (S118 `accepted` with a re-cite). This round
  re-checked the row against the author-hosted PDF, which this seat fetched live on 2026-10-25
  (HTTP 200, 254930 bytes, sha256 `da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b`);
  the verdict itself is the L1's to record, not this seat's.

### Spot-check status

No independent non-author spot-check is on record at this point. Wave reviewers, critics,
mutation-testers and scribes are lane-dispatched seats and do not satisfy the independent
closure duty; admit/reject agreement and the counter readings remain unverified pending
outside review.

---

## Findings

- **C1 calibration.** Before at base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`:
  `SUMMARY k1=6 k2=4 mismatches=10` (`census/round-29/records/controls.tsv`, do-nothing control
  identical). K1 is the six registry rows whose declared `used-by` disagreed with committed
  bytes (`S022, S024, S025, S075, S076, S215`; nine cell changes tabled in
  `.ufo/waves/round-29/w1/deliver-c1-usedby-changes.tsv`). K2 is the four stale r26-manifest
  statements still sitting at `LOG.md:1758`, `SCORECARD.md:23`, `corpus/lessons/round-28.md:22`
  and `:40`, pinned in `census/round-29/stale-statements.tsv`; this scribe re-read all four
  lines at base and found each phrase in place. After: the frozen target is
  `mismatches=0`, measured with `python3 -B tools/souji-registry-agreement.py` at the C1
  landing commit and again at the final tip (L1 receipts under `census/round-29/records/`).
- **C2 operability.** Before at the same base: `SUMMARY manifests=3 failed=152 uncovered=14
  floor_violations=0`, rc 1 (all 152 failed and all 14 uncovered in round 26; r27 and r28
  clean) — `census/round-29/records/controls.tsv`, measured by
  `python3 -B census/round-29/c2-counter.py --root <lane> --rev <full40>` over `git ls-tree`
  and `cat-file` only. Per-record classes: `.ufo/waves/round-29/w1/deliver-c2-152-classification.tsv`;
  symlink accounting: `deliver-c2-symlinks.tsv`; the improved capture tool and its extended
  fixture: `deliver-souji-wave-evidence-capture.sh`, `deliver-r29-wave-evidence-capture-fixture.sh`.
  After: frozen target `failed=0 uncovered=0 floor_violations=0` at the C2 landing commit and
  the same zeros with `manifests=4` at the final tip (r29 captured by the improved tool).
- **C3 coverage.** Before at base, re-measured by this scribe with the frozen counter shapes:
  `git grep -lE '^ground: F3' HEAD -- corpus/knowledge/ | wc -l` → `0`;
  `git show HEAD:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`
  → `139`; the F3 coverage-map row names one entry (`corpus/README.md:41`). After: target two
  `ground: F3` entries (the two admitted above) and 143 rows; the map row replacement is
  `.ufo/waves/round-29/w1/deliver-readme-f3-row.md`; counters re-run by the L1 —
  `python3 -B tools/souji-coverage-agreement.py` (target `grounded=15 mapped=15 dangling=0
  mismatches=0`), `python3 -B tools/souji-gate-check.py … --entries <the two entries>` (target
  `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`), and `sources-census.sh validate`
  rc 0.
- **Quote fidelity.** Two seat-delivered quotes are not byte-verbatim: the identity entry's S216
  struct comment (internal spacing collapsed) and the append block's S218 `original` clause
  (served bytes carry `"original"` in quotation marks). This Gate uses byte-exact alternatives;
  the identity entry's own quote must be replaced or the convention recorded before landing
  (see the quote check above).
- **S216 reuses S114's URL** (`corpus/SOURCES.md:135`) under a different scope. The census
  should report a W04 duplicate-URL warning and no E04; the curation line is that S216 answers
  the duplicate-verdict identity question and must not claim S114's origin-record ground.
- **Read-time observation, outside this seat's write scope:** `git status --porcelain` at the
  lane showed one tracked edit, ` M .ufo/waves/round-26/w1/ScribeGateDraft.md`. It is recorded
  as step 0 of `.ufo/waves/round-29/w1/deliver-landing-checklist.md` and is not touched here.

## Receipts

- Frozen contract and controls: `census/round-29/records/preregistration.txt`, `controls.tsv`,
  `census-start.txt`, `frozen-digests.txt`; counters `tools/souji-registry-agreement.py`,
  `census/round-29/c2-counter.py`, `tools/souji-coverage-agreement.py`,
  `tools/souji-gate-check.py`.
- Source bytes and pins: `census/round-29/sources/{statx.2.html,link.2.html,cmp.1.html,broder97resemblance.pdf,broder97resemblance.txt}`
  with `SHA256SUMS`; located quotes in `.ufo/waves/round-29/w1/deliver-quotes.tsv` and in this
  Gate.
- C1: `.ufo/waves/round-29/w1/deliver-c1-usedby-changes.tsv`, `deliver-c1-history.tsv`,
  `deliver-stale-sweep.tsv`, `census/round-29/stale-statements.tsv`.
- C2: `census/round-29/c2-counter.py`, `deliver-c2-152-classification.tsv`,
  `deliver-c2-symlinks.tsv`, `deliver-c2-history.tsv`, `deliver-souji-wave-evidence-capture.sh`,
  `deliver-r29-wave-evidence-capture-fixture.sh`, `census/round-{26,27,28,29}/waves/`.
- C3: `deliver-sources-append-block.md`, `deliver-duplicate-verdict-identity.md`,
  `deliver-duplicate-verdict-byte-equality.md`, `deliver-readme-f3-row.md`,
  `deliver-collision-guard-proof.md`, `assimilation/{reg-ids,staged-ids,collisions}`,
  `deliver-slice-verdicts.tsv`, `assimilation/quarantine-slice`,
  `census/round-24/records/slice-verdicts.tsv`, `deliver-mirror-validate.txt`.
- Census before/after: `census/round-29/records/census-start.txt` and `census-end.txt` (L1 run).

## Residuals

- `<collisions=N>` and the S118 quarantine `<verdict>` are unfilled by design; only the L1 fills
  them, from the files named above.
- No independent non-author spot-check exists yet; lane seats do not count. Admit/reject
  agreement and every after-counter remain unverified pending outside review.
- The two admitted entries' landed quotes need the fix named in the quote check, or an explicit
  whitespace-normalisation convention in the lesson.
- S217's locator is an author-hosted course-archive PDF; the registered DOI is unusable
  (HTTP 202, 0 bytes). The 365d recheck can re-hash the PDF and cannot re-resolve the DOI. If
  the course-archive path moves, the committed snapshot plus its digest is the only authority.
- Campaign ids are not portable: the package already uses S216–S219 for four different
  documents (Breitinger chapter, Unpaywall record, `config/gc.txt`, `git-worktree.txt`). Any
  later adoption must re-point by document again.
- S216 and S114 share a URL; the round's census output is expected to carry one more W04 and
  must carry no E03/E04.
- `duplicate-verdict-byte-equality.md` is new in this lane and absent from the package; its only
  ground is the frozen preregistration's declaration plus the S219 bytes quoted above.
- The tracked edit `M .ufo/waves/round-26/w1/ScribeGateDraft.md` observed at read time must be
  resolved by the L1 before the clean-tree gate can pass.
- The `## Mistakes` section is outside this delivery: the frozen mistake (r28's exclusion-clause
  misreading and the disk-verified receipt, fix shown red-before by C1/C2 counters at base)
  belongs in the L1's own `## Mistakes` draft.
