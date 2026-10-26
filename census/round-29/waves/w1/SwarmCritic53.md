# SwarmCritic53 — assimilation contract check (round 29, item 10)

## Status

STATUS: PARTIAL — the plan satisfies 13 of 23 clauses outright, 6 with a named condition, one is
excluded for this lane (wave-4 quarantine-first lists four other lanes), and 3 are missed (per-entry QUALITY bar never applied; the report carries no place for the two id lists, the
collision count and the renumber map and mis-maps S217-S219; the S118 quarantine verdict says
"not adopted" while S217 adopts the same document). No delivery changes a counter, predicate, kill
rule or target, so the frozen C1/C2/C3 claims survive; every correction below is documentation,
one row cell, one verdict line or one Gate clause.

Lane revision `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`).
Clause-by-clause table: `deliver-assimilation-clause-table.tsv` (23 rows, columns
`clause_id contract clause status satisfied_by minimum_fix evidence`).

## Evidence

Read this run, in this order: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/records/preregistration.txt:8`
(raw, whole line), `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md:449-539`, the ten w1
deliveries named below, `/home/vgpnk/Projects/shokuknow/merge/souji/{MERGE-REPORT.md,SOURCES.append.md,knowledge/corpus/knowledge/}`
(read-only), `corpus/{SOURCES.md,README.md,QUALITY.md}`, `PROVINCE.md`, `tools/souji-gate-check.py`,
`CORPUS.md:120-184`.

Source repo untouched (negative claim, with its sweep):

```
$ find /home/vgpnk/Projects/shokuknow -newermt '2026-10-25 20:00' -type f | wc -l
0
$ find /home/vgpnk/Projects/shokuknow/merge/souji /home/vgpnk/Projects/shokuknow/lanes/souji \
    /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1 -newermt '2026-10-25 00:00'
2026-10-25 07:29 d /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/.qcache
```

No file in the package or the lane's campaign paths changed during the wave (the one hit is the
campaign's own cache directory, seven hours before the wave). Campaign tool mtimes precede the wave:
`renumber-staged.py` 2026-10-23 20:31, `merge-plan.py` 2026-10-23 21:28, `absent-defect-register.py`
2026-10-24 08:36, `absent-defect-register.md` 2026-10-24 08:37, `quote-lint.py` 2026-10-24 21:17;
`SOURCES.append.md` and `MERGE-REPORT.md` 2026-10-24 23:33.

Lane state: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -1` → `b8cb4b3…`;
`status --porcelain=v1 --untracked-files=all` → only the pre-existing
` M .ufo/waves/round-26/w1/ScribeGateDraft.md`. Nothing was committed by a seat.

Guard run, re-read from the delivered artifacts: `reg-ids=139  staged-ids=134  collisions=31`
(`.ufo/waves/round-29/w1/assimilation/`); registry max id S215; adopted ids S216-S219.

Quote check (`python3 -B`, same `squash()` the frozen instrument uses, over
`.ufo/waves/round-29/w1/sources/`): every Gate quote in both entry deliveries is verbatim under
squash, span by span. Two spans elsewhere are not: the append block's Gate-quote table form
`it is impossible to tell which name was the original`, where the served bytes carry `"original"` in
straight quotes, and the package's staged quote `containing only identical documents` (source has
`contained`), which the lane's entry does not use. Byte-exact check of the statx struct comment
(`statx.2.html:97`): `               __u64 stx_ino;         /* Inode number */` — alignment spaces,
so the entry's single-spaced form matches only under squash.

Locator check (`sources/broder97resemblance.txt`): `53-54` holds the cluster sentence, `57` the
mixture clause, `67` the § 2 heading; `deliver-entry-identity.md` cites `54-55`, `58`, `68`.

Counter receipts already on record and read here: `SwarmExecutor16.md` (rehearsal commit `53264d0`,
`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, rows 143, `grounded=15 mapped=15` over
5797-byte and 4891-byte drafts); `SwarmScribe23.md` (`entries=1 ok=1` over the current
`deliver-entry-identity.md` in a proper scratch root); `SwarmScribe24.md` (`entries=2 ok=2 … fail=0`
with slice 8/8).

Located quotes (each opened this run, ≤25 words, no pipe character):

- `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md:361` — “the cited source could not be fetched, so no quote was checked” (12 words)
- `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/duplicate-verdict-taxonomy-r24.md:1` — “§ DESCRIPTION, exit-status contract” (4 words)
- `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md:460` — “Append only the rows the admitted entries cite” (8 words)
- `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md:488-489` — “every adopted entry's citation is re-pointed” (6 words)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-slice-verdicts.tsv:4` — “This round adopts none of the 8.” (7 words)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-sources-append-block.md:16` — “author-hosted PDF, 9 pages” (4 words)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-report-skeleton.md:48` — “S216 statx, S217 link, S218 cmp” (6 words)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/sources/broder97resemblance.txt:3` — “digital Systems Research Center” (4 words)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md:25` — “the entry's `verified-at:` names a version” (6 words)

## Findings

1. **Package provenance is misstated for the second entry (clauses C06, C05).** Both
   `deliver-collision-guard-proof.md` (finding 3) and `deliver-lesson-gate.md` (Residuals) state that
   `duplicate-verdict-byte-equality.md` is “absent from the package”; the same wave's
   `deliver-f3-scope-table.tsv` names it as `duplicate-verdict-taxonomy-r24.md` renamed, and the
   package file exists at
   `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/duplicate-verdict-taxonomy-r24.md`
   (3099 B) with the cmp ground on line 1. Two artifacts therefore give the L1 opposite provenance
   for one entry, and a later round adopting the package can land the same ground twice. Fix: in
   both artifacts, name the package path and the rename, and mark the package taxonomy entry
   adopted-renamed; the frozen C3 already fixes the lane-side name, so no claim text moves.

2. **The quarantine verdict contradicts the adoption (clause C19).** The file's fourth line says
   “This round adopts none of the 8.” and the S118 row ends “not adopted this round”, while
   `deliver-sources-append-block.md` adopts campaign S118's document as lane S217 (same DOI, same
   PDF, same sha256). The register's own class cell for that row is prose, i.e. the unchecked family,
   and the verdict records `accepted` without that note. Fix: header reads “adopts S118 only”; S118
   becomes `present` with “adopted as lane S217 via the Princeton course-archive copy; cited DOI
   locator unfetchable 202/0 bytes; prose class cell = unchecked family, not a fabrication finding”.
   This is the only slice row the round adopts; the other seven stay unadopted, which is correct.

3. **Quote and locator fidelity is not yet clean (clause C07).** (a) The identity entry's S216 Gate
   quote `stx_ino; /* Inode number */` is not byte-exact — the served line carries alignment spaces —
   and `deliver-lesson-gate.md` already makes replacement-or-convention a landing condition; the
   delivered entry still carries the single-spaced form, so the plan's own condition is unmet. The
   frozen instrument passes it (it squash-compares), so this is a rule-authority conflict, not a
   kill. Replace with the byte-exact `The inode number of the file.` (`statx.2.html:335`, 6 words) or
   record the squash convention once. (b) The append block's Gate-quote table carries the S218 form
   with the quotation marks around `original` dropped, which is not verbatim even under squash; the
   byte-equality entry's frame-span (`This new name may be used exactly as the old one for any
   operation; both names refer to the same file`) is verified and can be reused. (c) Three Broder
   locators are +1: `54-55`→`53-54`, `58`→`57`, `68`→`67` in `deliver-entry-identity.md`.

4. **“Author-hosted” is false and appears eight times in three plan artifacts (clauses C06, C07).** The row's
   anchor cell says “author-hosted PDF, 9 pages”; the bytes name “digital Systems Research Center”
   (`sources/broder97resemblance.txt:3`) and the host path is a Princeton course archive. Same
   wording in `deliver-sources-rows.md:26,45,78,166`, `deliver-lesson-gate.md:102,187` (the last one
   self-contradicts: “author-hosted course-archive PDF”). Fix: “Princeton course-archive copy of the
   author's preliminary version”, the correction `SwarmExecutor16.md` finding 1 already prepared. The
   URL and every counter are unaffected; the frozen prereg's descriptive phrase is not a predicate.

5. **The report duty is unplanned and the skeleton mis-maps the ids (clause C15).** The contract
   requires both id lists, the collision count and the renumber map pasted into the report; the
   `## Sources & frontier` skeleton has no place for them, and its tier line reads “S216 statx, S217
   link, S218 cmp … S219 Broder”, the frozen enumeration order copied positionally, which
   contradicts the append block (S217 Broder, S218 link, S219 cmp). Fix: add the two list paths,
   `collisions=31` and the four-row map, and correct the skeleton line. Counters do not read the
   report, so this is a false record, not a claim break.

6. **The QUALITY.md bar is never applied per entry (clause C11).** No artifact evaluates the two
   admitted entries against `corpus/QUALITY.md`; `deliver-f3-scope-table.tsv` covers PROVINCE only
   and `deliver-quality-skill.md` proposes new criteria. Fix: one PASS block per entry for the
   applicable bar — Q1 (`verified-at` names the version), Q4 (recheck under `/var/tmp`, self-cleaning:
   both entries' recheck lines comply), Q17 (cited snapshot resolves to a regular non-symlink file at
   the landing rev), Q25 (landing claims checked at the landing commit).

7. **Two identity-entry candidates; the green rehearsal is over stale bytes (clauses C07, C17).**
   `deliver-duplicate-verdict-identity.md` (5797 B) is the file `SwarmExecutor16.md` rehearsed; the
   assigned deliverable is `deliver-entry-identity.md` (10418 B), and the byte-equality entry grew
   from 4891 B to 9018 B. The schema receipt transfers, the byte receipt does not. Fix: the landing
   step names `deliver-entry-identity.md` and `deliver-duplicate-verdict-byte-equality.md`, cites
   Scribe23/Scribe24's green runs over those bytes, and the L1 re-runs the frozen gate-check at the
   landing commit (C3 already requires the tip reading).

8. **The Gate uses one reason to admit and to reject similarity material (clause C10).** Broder is
   admitted as F3 ground while `near-duplicate-*` entries are rejected as “document-similarity ground
   outside PROVINCE F3's byte-identical scope”. The distinction the plan actually applies is
   method/threshold vs bounded naming vocabulary; the Gate never says so. Fix: one clause in the S217
   ADMIT reason — vocabulary for naming the measure, no method and no threshold adopted — so the two
   decisions cannot be read as the same rule applied two ways.

9. **The mirror proves paths, not the delivered files; the frozen gate's inputs are not landed
   (clause C17).** `deliver-mirror-validate.txt` used two placeholder knowledge files and
   `census/round-29/records/quarantine-slice` plus `slice-verdicts.tsv` do not exist, so the frozen
   gate-check exits 1 (`FAIL slice slice-missing`) with the base tree. Fix: land both real entries,
   both records files and the five snapshots in the same commit as the rows; the rehearsal's second
   commit is the shape, a single commit is the safe one.

10. **Clauses satisfied but resting on explicit L1 steps (C04, C14).** The §4 helper owns the C3
    commit and no delivery assigns it; the collision evidence files exist as wave deliverables and
    must be carried by the L1. Both are conditions in the table, not gaps.

## Attack log

- **A1 — false provenance is the strongest counterexample available, and it is real.** Test: grep
  the package for the byte-equality ground. Result: present under a renamed file, so “absent from the
  package” is falsified by bytes (`duplicate-verdict-taxonomy-r24.md:1`). Impacted axes: coverage
  (re-adoption hazard, not this round's count) and calibration (a declared record contradicting
  bytes). Smallest safe correction: Finding 1.
- **A2 — a green guard is not append safety.** `S216` shares `S114`'s URL and S114's scope cell
  already names inode, link count, creation time and mount id, so the census cannot fire E04 on
  URL+scope; the guard proves only that no id was reused (guard proof finding 1 says so). The
  coverage increment therefore rests on S217/S218/S219, and F3 must stay `frontier`. The plan does
  keep it frontier; no correction needed, one Gate sentence recommended (C12).
- **A3 — do not apply Critic49's E9 correction as a claim change.** It removes Broder from the
  identity entry and sets S217's `used-by` to `—`; the row would then be `mined` with no citing
  entry and the entry would no longer be the one the frozen C3 sentence declares. Tested against the
  frozen line 8; the frozen claim wins. Record the attack, land the frozen sentence (C22).
- **A4 — the frozen enumeration order (statx, link, cmp, Broder) differs from the landed id order.**
  Checked, not a defect: the target is count-based and ids were assigned by document (URL + anchor),
  which is the contract's own rule. A positional reader will see a mismatch; the report should say
  the order is not part of the predicate.
- **A5 — “verbatim” is instrument-defined.** The S216 struct-comment quote passes the frozen
  gate-check (`squash()` containment) and fails a byte-exact reading; the plan contains a condition
  written to the byte-exact reading. Both cannot govern. Choose one (replacement or convention) at
  landing; do not carry an unmet condition into the Gate.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-assimilation-clause-table.tsv` (23 clauses, 13 satisfied, 6 satisfied-condition, 3 gap, 1 n/a)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/SwarmCritic53.md` (this report)

No installs or upgrades were needed; no pacman call was made. Scratch: none created — every check was
a read-only `grep`/`find`/`git` read or an in-memory `python3 -B` comparison against the delivered
snapshots.
