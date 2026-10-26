# SwarmScribe17 — DocsF1 (round 31, wave 1)

## Status

STATUS: PASS — the five documentation edits that land with C3 are drafted as exact replacement
text in `deliver-docs-f1.md`; no lane file was edited (L1 is the integration owner), and every
run-derived sentence is traced to a record I opened this run plus the fixture seat's message, with
the one unresolved pointer (the two delivered file names) named for the L1.

## Evidence

Read first: `census/round-31/records/preregistration.txt` (lines 1-41, incl. the C3 paragraph at
:20, the fixture row contract, and the MACHINE BLOCK). Base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`
(`git cat-file -t` → commit; `git log --oneline -1 9f17a1e` → `round-30 verifier spot-check`);
preregistration `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` and controls
`ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc` both type `commit`. Lane HEAD at my run:
`1b811368461785040e955f41f9c97e62f61fd67c`; `git status --porcelain --untracked-files=all` →
empty; `.gitignore:1:.ufo/waves/` covers my delivery path (same as earlier rounds' wave files).

Targets read this run (all at the tip above, lane-relative):

- `awk 'NR==39' corpus/README.md` → the F1 map row, 308 bytes with the newline, 4 pipes (3
  cells): ground cell `F1 git-native housekeeping vs receipts`, status cell `frontier, entries
  held`, entries cell naming five knowledge paths. `awk 'NR==46'` → the frontier bullet
  still saying "remaining: keep-ref expiry unmeasured, fleet exposure numerator re-census".
- `grep -n 'a keep ref is removed by jj' SKILL.md` → `115` (single match); the bullet is 1005
  bytes, 0 pipes. Line 113 is the r17 keep-root bullet, 114 the keep-only-visibility bullet, 116
  the nested-`.git` bullet — so the r31 bullet inserts at 116.
- `wc -l` → `corpus/README.md` 641, `PROVINCE.md` 211, `SKILL.md` 399.
- `grep -n '^## Round 30 boundary note' PROVINCE.md` → `195`, ending at 211.
- `corpus/QUALITY.md:135` → Q56, the same-commit map-row rule the delivery relies on.
- `cat census/round-30/records/jj-keep-expiry-run.txt` → step 4 `keep_refs=6`, step 5
  `RESULT step=5-op-abandon-util-gc-expire-now keep_refs=2 object_present=yes note=target_keep=no`.
- `corpus/knowledge/jj-keep-ref-expiry.md:122-133` (wave-2 corrections): :128 the packed arm,
  :133 "the measured lever at steps 4 and 8 is packedness".
- `grep -rn 'pack-refs' census/round-30/waves/w2/*.md` → `SwarmCritic21.md:22`, which records
  "a keep ref packed seconds earlier is deleted by plain `jj util gc` under the 14-day default".
- `corpus/lessons/round-30-verifier-spotcheck.md:131-133` → routed defect 1 (packed-ref caveat and
  the `leaves two keep refs where eight stood` misalignment).
- `census/round-31/c3-counter.py` docstring, legs L1-L11: L2 requires exactly
  `grounded=17 mapped=17 dangling=0 mismatches=0` (base 16/16), L10 requires the entry's backticked
  `RESULT ` spans to be whole record lines — so my README/PROVINCE/SKILL text deliberately carries
  no backticked `RESULT ` span.
- Run record for the prose: the fixture seat `SwarmExecutor08` messaged me the final arms/steps and
  17 `RESULT` lines; I read the same bytes at
  `/fast/scratch/hyaku/souji-r31/SwarmExecutor08/frun{1,2,3}.txt` (`md5sum` →
  `3bf8e6a533627b113f7a7acff21f559d` on all three; `jj-version: jj
  0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`, `git-version: git version 2.56.0`) and the
  step list at `final-fixture.sh:2-35`. The names the seat reports as delivered
  (`deliver-r31-jj-object-clock.sh`, `deliver-jj-object-clock-run.txt`) were **not on disk** in
  `.ufo/waves/round-31/w1/` at `03:30`; the earlier candidate `run{1,2,3}.txt`
  (`md5 df51be942fbeca2d2ca63d8b8491e9d9`, 13 lines, two arms) is stale and was discarded.
- Coverage instrument rule: `tools/souji-coverage-agreement.py:1-15` — a map row carries F1 when
  its ground cell starts with the `F1` token and a backticked entries span ends
  `knowledge/<name>`; a status-cell or prose mention does not map.

## Findings

1. `SKILL.md:115` states the r30 ref count wrongly: "`jj op abandon ..@-` before a second
   `jj util gc` leaves two keep refs where eight stood", while the committed record it cites goes
   6 → 2 at step 5 (`census/round-30/records/jj-keep-expiry-run.txt` steps 4 and 5; the surviving
   correction is `corpus/knowledge/jj-keep-ref-expiry.md:127`). The `eight` is step 3's count, not
   the count the step began from. Fix drafted (delivery item 4).
2. `SKILL.md:115` never names packedness. The entry's wave-2 corrections already say a packed keep
   ref has no loose file for the age gate, so packedness is the measured lever and `--expire=now`
   is sourced (`corpus/knowledge/jj-keep-ref-expiry.md:128`, `:133`; ground
   `census/round-30/waves/w2/SwarmCritic21.md:22`). This is the routed r30-closure defect 1
   (`corpus/lessons/round-30-verifier-spotcheck.md:131-133`) and is unfixed at the tip.
3. `corpus/README.md:39` does not name the C3 entry, so C3's L2 (coverage agreement) cannot reach
   `grounded=17 mapped=17` until the in-place row edit lands; status cell needs no change and the
   row still matches once (delivery item 1, verified byte-equal to the current line).
4. `corpus/README.md:46` and the r30 `### Frontier (r30)` bullet still carry the object clock as
   unmeasured, and `PROVINCE.md:208` says "the object-prune clock that follows a dropped keep ref
   is unmeasured here". Both are history and stay unrewritten; the r31 corrections bullet and the
   r31 boundary note record the closure instead (delivery items 2-3).
5. The run record changed shape mid-wave: the first candidate had 2 arms / 13 `RESULT` lines, the
   final has 3 arms (`solo`, `descendant`, `reflog-only`) / 17. The `reflog-only` arm is what makes
   the reflog a *measured* holder; in the other two arms expiring every reflog entry naming B left
   the object present, so any docs prose written from the 13-line candidate would have overstated
   the reflog and omitted the isolation. My drafts state the arm caveat explicitly (delivery items
   2, 3, 5 plus the sentence-to-record map).
6. The mtime keeper (object age against `gc.pruneExpire`) is **sourced, not measured**: every prune
   in the record uses `--prune=now`. Drafted text labels it as sourced in all three places.
7. Unresolved pointer for the L1: the two delivered fixture/record files named by the fixture seat
   were absent from `.ufo/waves/round-31/w1/` at my last look, so the delivery's provenance block
   names the scratch bytes I read and flags the L1 reconciliation against the landed record. This
   blocks nothing in the drafts themselves, which cite only the landing paths
   (`tests/fixtures/r31-jj-object-clock.sh`, `census/round-31/records/jj-object-clock-run.txt`).

No attack log: this item is a drafting seat, not an attack; no counter, predicate or case set was
proposed for change.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-docs-f1.md` — the five edits as exact text: (1) in-place
  `corpus/README.md:39` row replacement adding `knowledge/jj-dropped-keep-object-lifetime.md`;
  (2) appended `## Round 31 — F1 object lifetime behind a dropped keep ref` with
  `### Frontier (r31)` and `### Round 31 corrections`; (3) one-paragraph
  `## Round 31 boundary note (F1 object lifetime)` for `PROVINCE.md`; (4) exact replacement for
  the `SKILL.md:115` keep-ref bullet (packed-ref caveat, 6 → 2, `--expire=now` sourced) with its
  ground per clause; (5) one new `SKILL.md` error-pattern bullet citing the r31 entry, with a
  sentence-to-record map.
- `.ufo/waves/round-31/w1/SwarmScribe17.md` — this report.

Untouched by me: every lane file (no edit, no `git add`/`commit`/`jj`), every fleet path outside
the lane, and every peer's scratch. Tooling: no installs, no upgrades (nothing needed; `python3
-B`, `md5sum`, `grep`/`awk` only). Scratch: none created — this item ran no clone, fixture or
download, so there is no `/fast/scratch/hyaku/souji-r31/DocsF1/` to remove; peer scratch was read
only.
