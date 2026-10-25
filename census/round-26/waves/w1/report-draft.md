# souji — Round 26 report (DRAFT SKELETON)

**This is a skeleton, not the round report.** Every `[EVIDENCE-PENDING: …]` marker is a value the L1
must measure at the landing tip. Values marked "observed" below were read by the drafting seat at the
revision named and are **not** landing-gate evidence; the tip moved during drafting
(`c5949013` → `0c92c2e`) and must be re-derived.

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (repo and workspace hygiene, 掃除).
- Lane base: `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` (master, ahead=0 at freeze).
- Preregistration: `.ufo/waves/round-26/preregistration.txt`, frozen at `12fd90bcd9cdfab495e178023eeaa838a977fcbe`
  (task names `89e0fceeefcf28db313c94120be6d25e03c60094` as the freeze-with-amendment-1 state).
- Amendments: `preregistration-amendment-1.txt` (`89e0fce`, C2 K4 literal corrected to base-derived
  `grounded=7`/`kill_tested=7`), `preregistration-amendment-2.txt` (`965b869`, C1 kill rule read as
  byte-content spans rather than base line positions).
- Axes: calibration 7 (lowest, non-retired), operability 8, coverage 8. No axis may be harmed.
- Structure mirrored from `.ufo/reports/round-25/souji.md` (fleet root; the lane has no `.ufo/reports/`).
- **HARD BOUND:** souji's write scope is its own repo. Nothing outside
  `/home/vgpnk/Projects/shokunin/souji-shokunin/` was deleted, moved, quarantined or classified for
  cleanup this round — including the incident's fleet `.scratch/` tree, `.ufo/state/`,
  `.ufo/watchdog.log`, `MANIFEST.json`, fleet `scripts/`/`templates/`, sibling lanes and
  `/home/vgpnk/Projects/shokuknow` (read-only source; zero bytes written).

## Declared claims

| claim | axis | surface class | frozen counters | declared receipts |
|---|---|---|---|---|
| C1 SCORECARD generation-scaffold census + integration | calibration (7) | bookkeeping-file | K1 `grep -cE '^(Insert the table below directly above\|Optional same-landing correction)' SCORECARD.md` = 2 → 0; K2 `awk '/^### Round (23\|24\|25) measurements/{printf "%s ", NR} END{print ""}' SCORECARD.md` base `17 175 231` → exactly three headings ordered n25 < n24 < n23 | `census/round-26/records/c1-before.tsv`, `c1-after.tsv` (prereg requires each `verify=ok`) |
| C2 F1 auto-maintenance trigger-set assimilation | coverage (8) | knowledge-entry + registry-append | K1 `git grep -l '^ground: F1' 0eca7c8 -- corpus/knowledge/ \| wc -l` 0 → 2; K2 gate `entries=2 ok=2 fail=0` rc 0; K3 `sources-census.sh validate … souji` rc 0, rows 127 → 132; K4 coverage agreement `grounded=7 …` → `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0` | `c2-before.tsv`, `c2-k4-base.tsv`, `c2-after.tsv`, `c2-k4-after.tsv`, `c2-gate.tsv` |
| C3 preregistration axis-of-surface checker | operability (8) | instrument-acquisition | K1 tool absent → present, `claims=3 flags=0` rc 0 on this round's own prereg; K2 fixture `cases=12 pass=12 control=FALSE-GREEN-REJECTED` rc 0 | `c3-before.tsv`, `c3-after.tsv` |

Do-nothing controls: C1 base bytes untouched score K1=2; C2 untouched scores K1=0, K4 `grounded=7`;
C3 base has no tool (`axis_check_tool=absent`) and a stub always-green emitter is rejected by case 12.
Receipt values read from committed bytes during drafting:

- `c1-before.tsv` `rev=12fd90b…` → `markers=2`, `headings=17 175 231`; `c1-after.tsv` `rev=07f83e6…`
  → `markers=0`, `headings=17 44 78`.
- `c2-before.tsv` `rev=89e0fce…` → `grounded_f1=0`, `registry_rows=127`; `c2-after.tsv` `rev=e0f8dcd…`
  → `grounded_f1=2`, `registry_rows=132`; `c2-k4-base.tsv` `rev=0eca7c8…` →
  `grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`.
- `c3-before.tsv` `rev=89e0fce…` → `axis_check_tool=absent`; `c3-after.tsv` `rev=c5949013…` →
  `axis_check_tool=present`, `claims=3 flags=0`, `axis_check_exit=0`, `cases=12 pass=12
  control=FALSE-GREEN-REJECTED`, `fixture_exit=0`.

> **L1 checklist (claims block):** (a) re-run every frozen counter (C1 K1–K2, C2 K1–K4, C3 K1–K2) at
> TIP-40 and replace each "after"
> literal; (b) C1: the `c1-after.tsv` receipt is bound to `07f83e6`, **not** the tip — regenerate it at
> the landing tip per K1's "run at the landing tip in a clean tree"; (c) C2: `c2-k4-after.tsv` and
> `c2-gate.tsv` landed at `9a6e0f1` (bound to rev `33e6807`), so only the tip re-run remains; (d) C3:
> `c3-control.tsv` was deleted at `0c92c2e` (control folded into fixture case 12) and the lesson's
> Receipts block was corrected at `166baa1` — re-check that the corrected text still matches the tree;
> (e) record each receipt's `verify=` state only after running `tools/souji-receipt-run.py verify` at
> the tip.

## Work performed

- **C1 — calibration (7): SCORECARD scaffold census and integration.** The r24 generation scaffold
  (base lines 172–228: instruction, fenced r24 table + two capability rows + two planned bullets, the
  "Optional same-landing correction" paragraph) was removed and its payloads integrated newest-first,
  with an append-only superseded-by mapping note at SCORECARD EOF. Artifacts: `SCORECARD.md`,
  `census/round-26/c1-counter.sh`, `census/round-26/records/{c1-before,c1-after}.tsv`; wave evidence
  `ExecC1Surgery.md`, `ExecC1Verify.md`, `c1-line-map.md`, `c1-verify.md`, `c1-append-note.md`.
  Verdict: `[EVIDENCE-PENDING: K1 = 0 and K2 triple ordered n25<n24<n23 at TIP-40, plus the
  amendment-2 seven-span byte-diff annex (each protected span diff empty)]`.
- **C2 — coverage (8): F1 trigger-set assimilation.** Two entries admitted
  (`corpus/knowledge/git-auto-maintenance-trigger-set.md`, `…-trigger-set-r23.md`) with rows
  S128–S132 renumbered by document from staged S109/S110/S111/S123/S131; staged S119/S120/S121
  language-edition subset refused with reason + flip in the round lesson Gate. Artifacts:
  `corpus/SOURCES.md`, `corpus/README.md` (F1 row `:39` and F1 next-step `:46`, committed `0833de9`),
  `census/round-26/c2-counter.sh`, receipts listed above.
  Verdict: `[EVIDENCE-PENDING: K1=2, K2 rc0 entries=2 ok=2 fail=0, K3 rc0 rows=132 with 0 malformed /
  0 duplicate / 0 enum / 0 tier-inflation / 0 missing used-by, K4 grounded=9 mapped=9 dangling=0
  mismatches=0 kill_tested=7 kill_violations=0 at TIP-40]`.
- **C3 — operability (8): axis-of-surface instrument.** `tools/souji-axis-check.py` (`--prereg`,
  `--scorecard`; `claims=C flags=F`; exit 0/1/2; rules R1–R4) plus
  `tests/fixtures/r26-axis-check.py` (12 frozen cases, in isolated `/var/tmp` worlds) and
  `census/round-26/c3-counter.sh`. Verdict: `[EVIDENCE-PENDING: K1 rc0 flags=0, K2 12/12 with
  FALSE-GREEN-REJECTED and no case bombing on a shared world]`.
- **Round shape.** One v2 wave, build + attack together: `.ufo/waves/round-26/w1-spec.json` =
  **87 items** (executor 31, reviewer 15, scribe 11, scout 10, critic 9, mutation-tester 6,
  connector 2, simplifier 2, sentinel 1); `w1-dispatch.json` `counts.spawn=87`, policy
  `waveMinLanes=64`, `waveMaxLanes=128`, `hardCeiling=256`. The L1 holds the planner seat and is the
  only integrator.
  `[EVIDENCE-PENDING: returned / failed / cancelled seat counts and their last errors; this drafting
  seat is a leaf member and dispatched nothing]`.
- **Seat isolation.** This seat ran read-only against the lane and wrote only its own two files under
  `.ufo/waves/round-26/w1/`; no `git add/commit/push/stash/checkout/reset`, no `jj`, no `rm`/`mv`, no
  signals, no `agent://all`. Scratch (none needed beyond reads) — `[EVIDENCE-PENDING: L1's statement
  that every wave seat stayed in `/var/tmp/souji-r26-*` and that all such scratch was removed]`.
- **L1 checklist (this section):** one bullet per claim carrying the measured verdict, the round-shape
  counts, the L1-planner statement, and the seat-isolation/HARD-BOUND statement with the lane's own
  read-only sweep. Replace `[EVIDENCE-PENDING]` blocks; do not claim a seat ran a command it did not.

## Landed changes

Commits observed in `0eca7c8..HEAD` during drafting (oldest first; **the L1 must append later commits
and name the final landing commit**):

| lane commit | landed change |
|---|---|
| `12fd90bcd9cdfab495e178023eeaa838a977fcbe` | preregistration freeze (C1/C2/C3) + frozen counters |
| `89e0fceeefcf28db313c94120be6d25e03c60094` | amendment 1 (C2 K4 literal → base-derived `grounded=7`/`kill_tested=7`) + red-before receipts |
| `bd6588c74ebfe86057b80035fdbc33aded8d7666` | wave evidence (`make-spec.py`, w1 spec + dispatch + registry 87 seats, validate) |
| `965b8699d480702828062a5e739fbd2a203b4fb8` | amendment 2 (C1 kill rule read as content spans) + r26 slice verdicts |
| `a529c762c81272d398727e6a623c801a230ac157` | C1 integration (scaffold removed, newest-first order, R3 dated note, r24 planned bullets) |
| `44531281914ddd200432cdc7dae8ad958c5447e3` | C1 green receipt at `a529c76` |
| `0833de9591a7db81cdfa4efda2cdad2e75606f58` | C3 tool + first fixture (11 cases) + self-host `flags=0`; README F1 row/next-step |
| `d2e62533bc485bc68fae2c8ef083af0c36a1e1e3` | C3 counter gains `--stub` control arm |
| `e0f8dcd12b1df1c53f213dc3a71def77d8ddf3f3` | C3 before/after receipts |
| `d6c13b0f00066cbb342fdc50167849a5f1c726e5` | C2 before/after receipts + real gate rc=0 |
| `ea0bbe66c974062984134bb5b491b21bbb3c17d7` | `corpus/lessons/round-26.md` (Gate, findings, residuals) + Entry B enriched citations |
| `d6fe8a1125a9723e7593df7b8b90ee6c05cdf9ff` | SCORECARD EOF append-only mapping note (five superseded-by targets) |
| `07f83e69979b1032f9de4fe876739a8dccc7242b` | C1 fix: two r24 capability rows appended (wave `ExecC1Surgery` found the omission) |
| `ba8b54b85814dd980aa96050fe111c7cbfd4956a` | C1 `c1-after` regenerated at `07f83e6` |
| `c5949013f89fe0b8289bdb7050ab64a47e08c911` | C3 R4 per frozen contract; wave 12-case fixture adopted; counter adds fixture arm |
| `0c92c2e6fbe18f2f3009504d87240b6a22ad3d5b` | C3 receipts re-run; `c3-control.tsv` removed (control is fixture case 12) |
| `33e6807ea54ad5fa295d9138067a9a78f3b0f7ec` | C2 Gate sections on both entries (opened/ADMIT/REJECT/located snapshot quotes); gate `entries=2 ok=2 fail=0` |
| `9a6e0f1` (`pending full-40 in the final report`) | C2 receipts at tip `33e6807`: `c2-gate.tsv` (`entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`), `c2-k4-after.tsv` (`grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`) |
| `166baa1` (`pending full-40 in the final report`) | SCORECARD r26 measurements block + r26 planned bullet, lessons updates, `corpus/QUALITY.md` Q59 + R26-M1 mistakes row, wave w1 seat record; **this draft committed here** |
| `FINAL-LANDING-COMMIT-40` | `[EVIDENCE-PENDING: final wave-2 fixes, LOG.md Round 26 entry, README Round 26 section]` |

Lane branch state at landing: `[EVIDENCE-PENDING: master ahead=/behind= and the ls-remote origin
refs/heads/master match, or an explicit statement that the fleet report is pushed separately]`.

**L1 checklist (this section):** map each commit/change to its `LOG.md` entry (currently the LOG's
last entry is `## 2026-10-25 — Round 25 honest stop …`, `LOG.md:1723` — **there is no Round 26 entry
yet**), append the final landing commit, and state branch/push state. Do not list a commit as
"landed" if its only existence is an untracked wave file.

## Before → after measurements

| claim | axis | before → after | counting command | measured commit |
|---|---|---|---|---|
| C1 | calibration (7) | K1 `2` → `[EVIDENCE-PENDING: 0]`; K2 `17 175 231` → `[EVIDENCE-PENDING: n25 n24 n23 with n25<n24<n23]`; amendment-2 span diffs `[EVIDENCE-PENDING: 7/7 empty]` | `bash census/round-26/c1-counter.sh`; span annex per amendment 2 | before `12fd90b…`, after `TIP-40`; **`c1-after.tsv` currently bound to `07f83e6`, not the tip** |
| C2 | coverage (8) | K1 `0` → `[EVIDENCE-PENDING at TIP-40: 2]`; K2 gate `[EVIDENCE-PENDING at TIP-40]` (bound at `33e6807`: `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`, rc 0); K3 rows `127` → `[EVIDENCE-PENDING at TIP-40: 132], rc 0`; K4 `grounded=7 mapped=7 … kill_tested=7` → `[EVIDENCE-PENDING at TIP-40]` (bound at `33e6807`: `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`) | `bash census/round-26/c2-counter.sh`; gate command as frozen (K2); `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` (K3); `python3 -B tools/souji-coverage-agreement.py --root . --rev TIP-40 --base-rev 0eca7c8…` (K4) | before `89e0fce…` / `0eca7c8…`; both after-receipts present since `9a6e0f1`, bound to `33e6807` — re-bind at `TIP-40` |
| C3 | operability (8) | K1 `axis_check_tool=absent` → `[EVIDENCE-PENDING: present, claims=3 flags=0, rc 0]`; K2 fixture `[EVIDENCE-PENDING: cases=12 pass=12 control=FALSE-GREEN-REJECTED, rc 0]` | `bash census/round-26/c3-counter.sh` | before `89e0fce…`, after `TIP-40`; last bound after-receipt: `c5949013…` |

Controls and separability:

- C1 control: base bytes untouched score K1=2 (receipt `c1-before.tsv`, `rev=12fd90b…`, `markers=2`).
- C2 control: untouched base scores K1=0 and K4 `grounded=7` (`c2-before.tsv`, `c2-k4-base.tsv`).
- C3 control: no tool at base (`axis_check_tool=absent`); a stub that always prints `claims=1 flags=0`
  must be rejected (fixture case 12).
- `[EVIDENCE-PENDING: separability statement — that C1's predicate reads only SCORECARD bytes +
  its own receipts, C2's only entries/registry/map, C3's only the tool/fixture; and that no counter
  moved after any seat scored (Q58 / amendment rule).]`
- Draft-time observations (this seat, at HEAD `c5949013`, **not** the landing gate): K1 `0`; K2
  `17 44 78`; registry rows `132`; `grep -l '^ground: F1'` `2`. `[INFERENCE]` these should still hold
  at the tip unless a later commit changes SCORECARD/SOURCES/entries.

**L1 checklist (this section):** fill every "after" cell from a tip run, name the receipt and its
`verify=` state, add the C1 byte-diff annex (amendment 2 spans 1–7), and state that no 0–10 axis score
changed (no re-derivable mapping exists; SCORECARD axis-table bytes are a C1-protected region).

## Sources & frontier

- Registry: rows **127 → 132** (`S128`–`S132`, 5 net new), `validate` exit `[EVIDENCE-PENDING: 0]`,
  malformed `0`, duplicate ids `none`, enum/tier-inflation `none`, mined `used-by` missing `0`.
  `[EVIDENCE-PENDING: tier histogram and status histogram before → after]`.
- Rows added: S128 `git-fetch(1)` OPTIONS switches; S129 five v2.56.0 `run_auto_maintenance` call
  sites; S130 `builtin/pull.c` child-spawn; S131 own-work measured prune fixture; S132 own-work fleet
  worktree census (5 registrations, 0 prunable, 0 locked). Renumber map old→new: staged S109→S128,
  S110→S129, S111→S130, S123→S131, S131→S132.
- `[EVIDENCE-PENDING: confirmed tier/status per added row and "existing rows touched: none" — verify no
  pre-existing row's status/recheck/used-by cell changed vs `0eca7c8`]`.
- Gate: two entries admitted (both `ground: F1`); staged S119/S120/S121 language-edition subset and the
  vendor page refused with reason + flip, recorded in `corpus/lessons/round-26.md` `## Gate`. Each
  admitted source re-opened this round with a new access date and a ≤25-word located quote; snapshots
  under `census/round-26/sources/` bound by `SHA256SUMS`.
  `[EVIDENCE-PENDING: the two verbatim quotes (containing no literal or escaped pipe) with file:line locators, and the Q54 per-snapshot
  heading resolution result]`.
- Frontier: F1 stays **frontier, entries held** (`corpus/README.md:39`, four entries; next-step
  `:46` names the two r26 entries and S128–S132). No frontier→Core move.
  `[EVIDENCE-PENDING: expansion/coverage verdict sentence and any further F-row movement; F2/F3/F4/F5
  unchanged]`.
- `considerthese/` is **absent** in this lane (verified `ls -d considerthese` → No such file).
- Assimilation theme = C2 (the §10 theme and the round's §2b sourced claim). `[EVIDENCE-PENDING: one
  line naming the theme, the two admitted entries and the refusal count]`.
- **L1 checklist (this section):** fill the before/after census numbers from a tip run, list added rows
  by tier/status, state "existing rows touched: none" only after a diff, carry the two located quotes,
  and state the frontier verdict without promoting F1.

## Trend verdicts

- **expansion — `[EVIDENCE-PENDING: improved / unchanged (bounded)]`.** Draft-time basis: two admitted
  F1 entries and five registry rows on an already-held ground; F1 remains frontier (no SKILL rule, no
  tool). Bound: `git maintenance run` strategy/task scope and keep-ref expiry stay unmeasured
  (`corpus/lessons/round-26.md` `## Residuals` R-r26-1, R-r26-3).
- **quality — `[EVIDENCE-PENDING]`.** Draft-time basis: C3 adds a runnable axis-of-surface gate with a
  FALSE-GREEN control; C1 removes a scaffold that made the self-assessment disagree with its observed
  layout. Bound: no non-author re-grade occurred this round.
- **discernment — `[EVIDENCE-PENDING]`.** Draft-time basis: the round's own wave found and fixed two
  omissions (missing r24 capability rows, `ExecC1Surgery`; fixture case count 11 → frozen 12), and the
  Gate records a refusal with a flip.
- **Axis harm:** the axis-harm guard says no owned-axis score changes; `[EVIDENCE-PENDING: explicit
  statement that calibration/operability/coverage scores are unchanged and that SCORECARD's axes table
  bytes are byte-identical to base]`.
- **L1 checklist (this section):** one honest verdict per trend with its bound and the artifact that
  supports it; no verdict without a pointer; disclose any wave-1 correction that was needed.

## SHONEN

- `[~]` SKILL.md decision tables, error patterns, checklist — pointer carried from r25 as
  `SKILL.md:245-265`; `[EVIDENCE-PENDING: re-resolve the pointer at TIP-40 and record what changed]`.
- `[~]` At least one end-to-end domain task executed and logged in LOG.md — **blocked on the missing
  Round 26 LOG entry** (`LOG.md` currently ends at the Round 25 entry, `LOG.md:1723`).
  `[EVIDENCE-PENDING: LOG entry heading + line]`.
- `[~]` Instructions executable without oral context — `tests/fixtures/r26-axis-check.py`,
  `census/round-26/{c1,c2,c3}-counter.sh`; `[EVIDENCE-PENDING: runnable-without-context statement and
  named limits]`.
- `[~]` No cross-domain bleed — `PROVINCE.md:48-57`; `[EVIDENCE-PENDING: confirm PROVINCE.md unchanged
  vs base and that no sibling source tree or `/home/vgpnk/Projects/shokuknow` byte was written]`.
- No box is `[x]`: promotion is operator-owned and this round has no non-author verifier on record.
- **L1 checklist (this section):** keep every box `[~]` unless a non-author verifier exists; each box
  needs a resolving pointer at the tip.

## Stale-lane

- `[EVIDENCE-PENDING: whether the mission exceeded the driver tick budget and whether it was
  progressing (lane commits + round artifacts landed) rather than silent; open L0 questions: none /
  list]`.
- **L1 checklist:** one line on driver ticks, one on open L0 questions, and nothing claiming operator
  contact that did not happen.

## Tool installs

- This drafting seat installed or updated **nothing**: no `pacman` (transactions are paused host-wide),
  no `uv tool`, `npx`, `cargo` or `npm`, no binary downloaded. Python ran as `python3 -B` only
  (no `__pycache__` written by this seat).
- Round total: `[EVIDENCE-PENDING: per-seat installs/upgrades with tool, version, channel and reason,
  or "none"]`.
- Observed hygiene note for the L1 (not this seat's to remove): untracked `tests/fixtures/__pycache__/`
  and `tools/__pycache__/` exist at `166baa1` (`git status --porcelain` `??` entries).
- **L1 checklist:** record the round's install ledger honestly; do not claim "none" if a wave seat
  installed anything.

## Draft findings handed to the L1 (defects found while drafting, not claim verdicts)

Status as of `166baa1` (the commit that landed this draft); each item names the revision where observed.

1. **C2 declared receipts — CLOSED at `9a6e0f1`.** `c2-k4-after.tsv` and `c2-gate.tsv` were absent at
   `0c92c2e`; both are present at `166baa1`, bound to rev `33e6807` (`c2-gate`: `entries=2 ok=2
   slice_verdicts=0 slice_total=0 fail=0`; `c2-k4-after`: `grounded=9 mapped=9 dangling=0
   mismatches=0 kill_tested=7 kill_violations=0`). Only the tip re-bind remains (checklist (c)).
2. **C1 after-receipt rev ≠ landing tip — OPEN.** `c1-after.tsv` is still `rev=07f83e6` at `166baa1`;
   the prereg requires the K1 after value "run at the landing tip in a clean tree", and `166baa1`
   itself edited SCORECARD (r26 measurements block). Regenerate at the tip.
3. **Lesson named a deleted receipt — CLOSED at `166baa1`.** `corpus/lessons/round-26.md` `## Receipts`
   no longer names `c3-control.tsv` (removed at `0c92c2e`; the control is fixture case 12). Re-check
   the corrected bytes against the tree at the tip.
4. **QUALITY Q59 — CLOSED at `166baa1`.** `corpus/QUALITY.md:143` now carries Q59 (axis/surface-class
   consistency, instrument-checked), and the R26-M1 mistakes row landed in the same commit.
5. **Round 26 documentation tail — OPEN (README/LOG).** At `166baa1` the SCORECARD r26 measurements
   block exists (`SCORECARD.md:264`) and Q59 landed, but `corpus/README.md` still has no Round 26
   section and `LOG.md` still ends at `1723:## 2026-10-25 — Round 25 honest stop…`.
6. **This draft was committed mid-draft at `166baa1`.** The working-tree delta after that commit is the
   drafting seat's wording-only fix (claims-table `verify=ok` phrasing; checklist item (a) names the
   counters explicitly) — take it as-is, do not revert it, and do not treat the committed skeleton as
   final.
7. **Fixture case-count history.** The frozen set is 12 cases; the first landed fixture (`0833de9`) was
   11 cases and `c5949013` adopted the 12-case wave fixture. Any wave seat that scored 11/11 before
   that commit scored a narrower set; state this chronology rather than reporting only 12/12.
8. **Pre-drafted edge case for this document.** The drafting seat's own scratch discipline holds; the
   lane's `jj` state and git index were not touched, and no fleet path was written.

## Attack log

- **ATTACK A1 (frozen red-before rev is unsatisfiable as written) — substantiated by bytes.**
  C1's do-nothing control names `--rev 0eca7c8a… --label census/round-26/c1-counter.sh`, but
  `git ls-tree 0eca7c8 census/round-26/` is **empty**: the counter first exists at `12fd90b`. The
  executed receipt (`c1-before.tsv`) is bound to `rev=12fd90b…`, one commit after base. C2/C3 before
  receipts likewise ran at `89e0fce…`, not at base. This is the Q58/R25-M1 class (a literal copied to a
  revision where its artifact is absent). It is **not** a predicate violation: `SCORECARD.md` blob
  `4b564bc628d40328d276476c4171c30817cd6e75` is identical at `0eca7c8` and `12fd90b`, and
  `corpus/SOURCES.md` blob `f3cffccdb15be2b8ead6cf19fda8c8a8adc145d7` is identical at `0eca7c8` and
  `89e0fce`, so each red reading is semantically at base. Required: the L1 records the executed rev and
  the blob-identity justification in the report (or a stricter-only attachment), and does not phrase the
  C1 red arm as "run at 0eca7c8".
- **ATTACK A2 (claim C1's protection is position-worded) — already amended, re-checked.** Amendment 2
  replaced positional kill-rule regions with seven byte-content spans; the report must carry the
  span-diff annex, otherwise K2 alone (heading order) is satisfiable while protected bytes drift.
- **ATTACK A3 (C3 can self-satisfy).** K1 is the checker running on the round's own prereg, so a
  checker weakened to accept its author's prereg passes trivially; the fixture's case 1 (r25-C2 replica
  flagged on its frozen operability axis) and case 12 (always-green stub rejected) are the only
  discriminators. The report must show both were run at the tip; `c3-after.tsv` at `c5949013` does.
