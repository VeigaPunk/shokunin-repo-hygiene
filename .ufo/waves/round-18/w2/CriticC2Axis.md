# CriticC2Axis — C2 calibration attack (wave 2)

Attacked claim: C2 calibration — `LG-DANGLING-PTR` / `LG-DANGLING-PTR-EXEMPT-STALE`
at `--round` ≥ 18, unresolvable `measured_commit` as `LG-FROZEN-MEASURED`,
`corpus/pointer-exemptions.tsv`, `--fleet-root`, `checked_measured` totality fix.
Claimed: 10 findings at b576341 → 0 at tip 5efb519; selftest 33 → 53;
fixture `r18-landing-pointers.py` 11/0; r17 replays unchanged.

Seat bounds respected: no exec of any souji tool (item has no ALLOWED-EXEC);
all checks are `git show/ls-tree/diff` on the named revisions, static reads,
and one independent re-parse of pointer tokens (plain Python over extracted
blobs, not the gate). No clone needed — nothing executed.

## Verdict: claim HOLDS, with two calibration notes and one latent sink defect

### 1. The 10 → 0 is real but mixed-composition — and the lane discloses it (pass)

Decomposition of the committed before-record
`census/round-18/gate-pointers-before-b576341.json` (read at tip):

- 7 × `LG-DANGLING-PTR` — citations of never-committed `ddb7347` record names
  (`gate-replays-ddb7347.json` ×2 in SKILL.md, `jj-receipts-ddb7347.txt` ×5 in
  corpus/README.md + jj-colocation-receipts.md). **Fixed by repointing, not
  deletion.** `git diff b576341..5efb519` on the three named files shows every
  citation retargeted to `*-4f48343.*`; `git ls-tree b576341 census/round-17/`
  confirms `gate-replays-4f48343.json`, `jj-receipts-4f48343.txt` and
  `seat-audit-r16-replay-4f48343.json` all exist — the pointers now name real,
  committed evidence. This is a genuine repair of a genuine defect (R18-M1).
- 1 × `census/operator-sweep-20261019/` — exempted ("operator-owned, never
  committed"). Cited at corpus/README.md:81 at tip; still absent from tree.
  Legitimate: the path is deliberately absent, the citation is a provenance
  name, not evidence.
- 1 × `tests/vault/vadv54-run/p/p6repo/.git` — exempted ("absent by design").
  Cited at SKILL.md:110 as the hazard's location; still absent. Legitimate.
- 1 × `LG-FROZEN-MEASURED` on `tests/fixtures/r14-cache-frozen/expected.json` —
  the record `tests/fixtures/r14-cache-frozen/record.json` is exempted
  (synthetic placeholder `measured_commit`). Exemption keying is correct:
  `check_frozen_pins` matches `record_repo` (gate L596), not the finding path.

So the truthful composition is **7 repaired + 3 exempted = 10 → 0**, and the
SCORECARD row (line 14) and lesson (round-18.md §Measurements C2) both say
exactly that: "7 citations… 2 deliberate non-files and 1 synthetic placeholder
(now committed exemptions with reasons)". No inflation in the prose. No
finding was fixed by deleting a pointer; every deleted-name citation was
repointed, and the three exempted citations were retained with reasons.

### 2. The "0 at tip" reproduces — I re-derived it statically (pass)

The lane committed no after-run JSON, so I rebuilt the check: extracted
SKILL.md, SHONEN.md, SCORECARD.md, PROVINCE.md, corpus/QUALITY.md,
corpus/README.md, corpus/lessons/round-18.md (+ spotcheck, absent at tip),
all `corpus/knowledge/*.md`, and LOG.md's round-18 section at 5efb519;
applied the gate's exact grammar (`POINTER_PATH_RE`, trim `:<lines>`, braces,
`round-{a..b}` ranges, `round-N` placeholder skip, `../` normalization,
existence vs. `git ls-tree`, fleet check against `/home/vgpnk/Projects/shokunin`,
the 3 committed exemptions).

Result: **445 pointer tokens → 0 dangling, 3 fleet, 3 exempt** — the claimed
0 is correct at the claimed tip, and all 3 committed exemptions were used
(no stale rows). Every `.ufo/waves/round-18/w1/*.md` path cited in the lesson
resolves in-tree (`.ufo` is tracked — 530 paths). This also refutes the
"inflated by deliberate non-files" hypothesis beyond the 3 disclosed rows.

### 3. Defect found: path-keyed exemption silently masks a *new* dangling pointer of a different kind (minor, real)

`check_pointers` L865 suppresses when `path in exemptions` — keyed on the
path alone, source and reason unchecked. Same key reused for
`LG-FROZEN-MEASURED` via `record_repo in exemptions` (L596). Counterexample:
`tests/fixtures/r14-cache-frozen/record.json` is now exempt "for the r14
synthetic placeholder". If a future commit edits that record's
`measured_commit` to a *different* unresolvable value (e.g. a real SHA
typo'd in an honest re-measure), the gate stays silent forever — the
exemption suppresses by record path, not by placeholder value, and it can
never go STALE because it keeps "being used". The STALE guard fires only
when an exemption suppresses *nothing*; a permanently-masking exemption is
invisible. Same for `tests/vault/vadv54-run/p/p6repo/.git`: any later citation
of that absent path — for an unrelated reason — is silently absorbed.
Impacted axis: **calibration** (a self-assessment instrument with an
unbounded, unobservable silence window). Smallest fix: make the TSV
third-column or the reason machine-checked (e.g. match the finding's detail
substring, or for measured_commit pin the exempt value
`0123…4567` in the row); or scope pointer exemptions to `(source-file, path)`
pairs. Cheap alternative: emit exempted hits in `findings` with a distinct
`LG-DANGLING-PTR-EXEMPTED` info id that does not count against exit 1, so
masking is observable in the JSON without breaking the 0-exit contract.

### 4. Latent ordering defect: STALE can false-positive when a citation moves to fleet (latent only)

Fleet classification (L850-863) runs *before* the exemption check; fleet hits
`continue` without marking the exemption used. If an exempted path's citation
is ever re-pointed to a `../`-normalized fleet path that resolves under
`--fleet-root`, the exemption flips to unused → `LG-DANGLING-PTR-EXEMPT-STALE`
fires on a row that was correct when committed. Worse, the verdict then
differs by invocation: without `--fleet-root` the same revision yields
`LG-DANGLING-PTR` (fleet pre-check skipped), with it yields `EXEMPT-STALE`.
Not triggered by current content (no exempted path is cited as `../`), but
the grammar fully permits it. Fix: mark `used_exemptions` when the fleet
match consumed the same underlying path, or exempt by citation occurrence.

### 5. Evidence asymmetry on the before→after pair (calibration note, not a defect)

`gate-pointers-before-b576341.json` is committed; the after run at 5efb519
has no committed JSON — the "0" rests on the SCORECARD/lesson prose and my
static re-derivation. Also, lesson line 5 says measurements were on "the
integrated worktree whose code is committed at `3f822e8`" while the claim
says "0 at the round tip" (5efb519 = 3 commits later, touching SKILL.md,
SCORECARD.md, LOG.md, README — all scanned files). My sweep proves the 0
still holds at tip, so the claim survives, but an asymmetric record
(before pinned to JSON, after to prose) is exactly the R18-M1 class this
claim exists to kill. Smallest fix: commit
`census/round-18/gate-pointers-after-5efb519.json` (or a `--rev` + `--round`
replay record like `gate-replays-r18.json`) so the claim's after-side is
re-derivable without trusting prose.

### 6. Checks that passed against falsification

- Exemption file is *not* a blanket sink: `load_pointer_exemptions` (L763-789)
  validates rows (2 fields, path under `POINTER_ROOTS`, no whitespace/< > *,
  unique) → malformed = exit 2, tested by `malformed-exemption-exit2`.
- `LG-DANGLING-PTR-EXEMPT-STALE` exists (L991-999) and selftest
  `pointer-stale-exemptions` covers unused + resolvable-but-exempted rows
  (selftest ~L1367-1379). Fixture `r18-landing-pointers.py` covers
  exemption-honored + malformed-exit2 (does not cover the §3/§4 cases above).
- Exemptions are only loaded at `round_no >= 18` (L913-914), so r17 replays
  are unaffected; `gate-replays-r18.json` shows `match: true` on r13/r14/r15
  pinned replays including the r15 5-finding multiset.
- The `checked_measured` totality fix is real (result dict L899 initialized;
  selftest `cli-unknown-rev-exit2`, `cli-bad-exemption-exit2`).
- Exempted paths are still *cited* at tip (README.md:81, SKILL.md:110,
  exemptions TSV self-cite) and still *absent* from the tree — exemptions are
  doing exactly the work described, not hiding removals.
- Scope: scanned sources = SKILL/SHONEN/SCORECARD/PROVINCE/QUALITY/README/
  knowledge/*.md/round-18 lesson+spotcheck + LOG round-18 section only —
  consistent with LOG being append-only (historical sections legitimately
  cite since-removed records, e.g. LOG.md:916 `ddb7347`).

## Impact on admission

C2 is admittable: the calibration claim is honestly graded, the 10→0
decomposes correctly, and my independent reproduction confirms the after
state. The §3 exemption-masking defect and §5 missing after-record are
fixable defects, not judge-level rejections — they describe how a *future*
silent regression could hide inside the new mechanism, not that the landed
one is wrong. Recommend routing: (a) exemption masking observability (§3),
(b) commit the after-record (§5).
