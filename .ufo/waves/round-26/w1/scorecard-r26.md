# Round 26 SCORECARD draft (paste-ready) — C1/C2/C3

Read at lane tip `ba8b54b` (tip was still moving while this draft was written; every cell
names the revision its number came from). Frozen base `0eca7c8`, prereg freeze `89e0fce`,
amendments 1 and 2. Nothing here is landed by this seat; every unfilled number is a
`RECEIPT-PENDING` line the L1 must replace with a receipt path, not with a recollection.

---

## 1. Insertion — `### Round 26 measurements`

**Place directly above `### Round 25 measurements` (currently `SCORECARD.md:17`), followed by
the already-landed `### Round 26 append-only corrections` block (currently `:239-261`).**
That block is appended at EOF today; moving it (bytes unchanged) next to the measurements
section restores the file's own newest-first contract that C1 enforces.

```markdown
### Round 26 measurements (2026-10-25; lane base 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 SCORECARD generation-scaffold census and integration | calibration 7 | At base `0eca7c8` the r24 payload exists only as a fenced scaffold copy: `markers=2`, headings `17 175 231` (the Round 24 heading sits inside the fence). The red receipt ran at `12fd90b`, the freeze commit, whose `SCORECARD.md` blob `4b564bc6…` is byte-identical to the base. The do-nothing control is that same run: untouched bytes score `markers=2`. | At fix tip `07f83e6`: `markers=0`, headings `17 44 78`, i.e. Round 25 (17) before Round 24 (44) before Round 23 (78), newest first; 254 to 261 lines; payloads integrated exactly once (Round 24 table, the two r24 capability rows at `:155-:156`, the two planned bullets, one dated R3 note on the `blob-bound receipts (r23)` row, and the append-only mapping note at `:239`). Re-read live at `ba8b54b`: same `markers=0` and `17 44 78`. **RECEIPT-PENDING: a fresh `c1-after` at the final tip after the Round 26 measurements section is inserted above `:17`** — that insertion shifts the three heading line numbers and the current receipt literal would no longer describe the tip. | `bash census/round-26/c1-counter.sh`; protected spans by byte-diff per amendment 2 | `census/round-26/records/c1-after.tsv` (`rev=07f83e6…`, tool sha256 `c8dbb76c…`, `verify` RECEIPT-PENDING at the final tip); red `census/round-26/records/c1-before.tsv` (`rev=12fd90b…`) |
| C2 F1 auto-maintenance trigger-set assimilation (2 entries, S128-S132) | coverage 8 | `grounded_f1=0`, `registry_rows=127` (`c2-before.tsv`, rev `12fd90b`, same freeze-commit caveat as C1). K4 at the named base `0eca7c8`: `grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0` (`c2-k4-base.tsv`). | At `e0f8dcd`: `grounded_f1=2`, `registry_rows=132` (`c2-after.tsv`). This seat's live runs at `d6fe8a1`, not receipts: K3 `sources-census.sh validate` rc 0 with duplicate-url W04 warnings only; K4 `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0` rc 0. **K2 is red at the tip**: `entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2`, both entries `check1-no-gate`. The wave drafts `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set{,-r23}.md` carry the `## Gate` blocks and the identical command passes `entries=2 ok=2 fail=0` rc 0 against them in a `/var/tmp` mirror. **RECEIPT-PENDING: `c2-gate.tsv` (K2) and `c2-k4-after.tsv` (K4) after the Gate blocks land at the final tip.** | `bash census/round-26/c2-counter.sh`; `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts`; `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`; `python3 -B tools/souji-coverage-agreement.py --root . --rev <tip-full40> --base-rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` | `census/round-26/records/c2-before.tsv`, `c2-after.tsv`, `c2-k4-base.tsv`; K3/K4 live at `d6fe8a1`; entries `corpus/knowledge/git-auto-maintenance-trigger-set{,-r23}.md`, registry tail S128-S132; snapshots `census/round-26/sources/*` bound by `SHA256SUMS` |
| C3 preregistration axis-of-surface checker | operability 8 | At `89e0fce`: `axis_check_tool=absent` (`c3-before.tsv`). The tool is absent at the named base `0eca7c8` as well (`git cat-file -e 0eca7c8:tools/souji-axis-check.py` rc 128). | At `d2e6253`: `axis_check_tool=present`, `claims=3 flags=0`, `axis_check_exit=0` (`c3-after.tsv`, counter sha256 `b60bcede…`); this seat's live run at `ba8b54b` prints the same `claims=3 flags=0` rc 0 on the frozen prereg. Control arm `cases=11 pass=4 control=FALSE-GREEN-REJECTED` rc 1 (`c3-control.tsv`). **K2 is not met from committed bytes**: `tests/fixtures/r26-axis-check.py` is the 11-case fixture (`cases=11 pass=11`, no r25-C2 replica case) while C3 K2 freezes 12 cases; the wave delivery `.ufo/waves/round-26/w1/r26-axis-check.py` (sha256 `220eed2e…`) reports `cases=12 pass=12 control=FALSE-GREEN-REJECTED` against `tools/souji-axis-check.py` (sha256 `14bc9632…`) in the ExecAxisFixture report, which this seat did not run. **RECEIPT-PENDING: land the 12-case fixture over the committed 11-case bytes, then run it and regenerate `c3-after` and the control receipt at the final tip.** | `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md`; `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py` | `census/round-26/records/c3-before.tsv` (rev `89e0fce`), `c3-after.tsv` and `c3-control.tsv` (rev `d2e6253`); tool `tools/souji-axis-check.py` |

Score delta: 0 on every owned score value; no reproducible 0-10 mapping moved, and the axes table
is a C1 kill-rule protected span. C1 is a record-consistency repair, not a calibration score move.
C2 adds two entries on ground F1 already held frontier, so the expansion predicate reads
**unchanged** and no F1/Core promotion is claimed. C3 lands an operability instrument whose frozen
case set is not yet the committed case set. No axis was relabelled to fit its surface — the r25
failure mode this instrument exists to catch. Certification OFF, K5 HELD.
```

---

## 2. Insertion — capability row

Append inside `## Capabilities`, after the `coverage-map agreement (r24)` row (currently
`SCORECARD.md:156`).

```markdown
| prereg axis-check (r26) | read a round's frozen `## MACHINE BLOCK` and flag axis ownership (R1), axis/surface-class misattribution (R2: fixture-expansion or knowledge-entry/registry-append off coverage, bookkeeping-file off calibration, instrument-acquisition off operability), a round with no claim on the lowest-scoring non-retired axis (R3), and a universal clause with no same-claim `enumerate:` line (R4); exit 0 clean, 1 any flag, 2 on a malformed block, and never pass a block it could not parse. Limits: the surface-class map is a whitelist, so an unknown class is neutral rather than flagged, and R3 reads only the Axes table window before `## Retired` | `tools/souji-axis-check.py` sha256 `14bc9632e88ef58f18108011f6645bd970cd825d0ffc1664369dc60b0d579332`; `--prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` gives `claims=3 flags=0` rc 0; control arm `FALSE-GREEN-REJECTED` (`census/round-26/records/c3-control.tsv`); the frozen 12-case fixture is `.ufo/waves/round-26/w1/r26-axis-check.py` 12/12 `control=FALSE-GREEN-REJECTED` (ExecAxisFixture arm B); the committed `tests/fixtures/r26-axis-check.py` is still the 11-case bytes | r26 |
```

---

## 3. Planned edits — r26 done, r27 drafted

**Landing constraint.** C1 amendment 2 protects the `## Planned` section as "the base `## Planned`
section (95-137) with exactly the two fenced r24/r25 planned bullets appended". A third and fourth
bullet inside `## Planned` makes that span's byte-diff non-empty, which is a C1 kill-rule failure.
Land the two bullets below in an appended `### Round 26 planned-roll` block at EOF (after the
existing `### Round 26 append-only corrections`), or land them only after the C1 landing-gate run
at the tip it certifies. Leave `## Planned` byte-identical to base plus the two fenced bullets.

```markdown
### Round 26 planned-roll

- **r26 (planned r25) — done, see `corpus/lessons/round-26.md`:** C1 removed the r24 generation
  scaffold and integrated its payloads once (markers 2 to 0; headings Round 25 17 before Round 24
  44 before Round 23 78, newest first; 254 to 261 lines; the two r24 capability rows at
  `SCORECARD.md:155-:156` and the append-only mapping note at `:239`). C2 admitted 2 F1 entries and
  5 registry rows (S128-S132, rows 127 to 132; K4 grounded and mapped 7 to 9) and refused the
  staged zh/ja and vendor subset; its K2 gate is red at the tip because the committed entries do
  not carry the drafts' `## Gate` blocks. C3 landed `tools/souji-axis-check.py` (`claims=3 flags=0`
  on the frozen prereg, `FALSE-GREEN-REJECTED` control) but the committed fixture is still the
  11-case bytes, not the frozen 12. No owned-axis score change; calibration is neither harmed nor
  credited. RECEIPT-PENDING: final-tip receipts, this round's admission verdict. Certification OFF,
  K5 HELD.
- **r27 — planned:** (a) coverage/F1: measure keep-ref expiry (R-r26-3 — the trigger set covers
  `gc.worktreePruneExpire`, not the keep-ref guarantee); re-run the fleet exposure census numerator
  (S132 is a 2026-10-23 point-in-time: 5 registrations, 0 prunable, 0 locked, and
  `corpus/README.md:46` still names the numerator as open); `git maintenance run`
  strategy/task scope (R-r26-1); hold the zh/ja and vendor staged rows refused (R-r26-2) until an
  edition's version stamp is provable and quoted, not paraphrased. (b) calibration: land the two
  entries' `## Gate` blocks so C2 K2 goes green; land the frozen 12-case fixture over the committed
  11-case bytes; receipt K2, K4, `c1-after` and `c3-after` at the final tip; correct
  `corpus/lessons/round-26.md` `## Receipts`, which names `89e0fce` and `d6c13b0` where the receipts
  record `12fd90b` and `e0f8dcd`, and says "11-case" where the contract freezes 12; record the
  absent `.ufo/waves/round-26/assimilation/validate/` mirror gate. (c) operability: the C3 tool has
  no `--selftest` (ExecAxisSelftest F1); the frozen red-before command names a revision where the
  counter file does not exist, so the red receipt can only bind the freeze commit — either keep that
  and record it as a contract defect, or add a rev-scoped counter variant. Fleet route: the
  LEARNING.md expansion predicate stays unresolved. Certification OFF, K5 HELD; F5 reap and
  NAMESPACE holds unchanged.
```

---

## 4. Two verdict sentences (quality / discernment)

**Quality.** The r26 instruments discriminate rather than merely pass — the C1 counter moves
`markers` 2 to 0 while every protected span stays byte-equal, and the C3 control arm rejects an
always-green stub (`FALSE-GREEN-REJECTED`, `census/round-26/records/c3-control.tsv`) — but the gain
is proven on delivered bytes only: the frozen 12-case fixture and the entries' `## Gate` blocks
exist today as wave drafts, so quality on the lane's committed bytes is RECEIPT-PENDING.

**Discernment.** Discernment held where it was pointed at a decision — amendment 1 re-derived C2's
stale K4 literal at the named base before any seat scored (the R25-M1 class, caught by Q58), and
the round refused the unprovable zh/ja and vendor pages instead of paraphrasing them into the claim
(`corpus/lessons/round-26.md` `## Gate`) — and did not hold at the record layer, where the round
lesson and two commit messages report a green gate and a 12-case contract that the committed bytes
do not reproduce, which is the same record-versus-measurement drift C1 exists to repair.

Authoritative wording for the trend verdicts belongs to the `RevTrendWording` seat; these two
sentences are this scribe's reading of the same evidence and should be replaced, not merged, if
that report lands.

---

## 5. Checks after landing

1. `bash census/round-26/c1-counter.sh` at the final tip prints `markers=0` and a strictly
   increasing heading triple; regenerate `c1-after.tsv` and confirm `verify=ok`.
2. Gate: the frozen K2 command prints `entries=2 ok=2 fail=0` rc 0; save it as
   `census/round-26/records/c2-gate.tsv` and `verify=ok`.
3. `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py` on the landed
   12-case bytes prints `cases=12 pass=12 control=FALSE-GREEN-REJECTED` rc 0; receipt it as
   `c3-control.tsv`/`c3-after.tsv` at the final tip.
4. `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt
   --scorecard SCORECARD.md` still prints `claims=3 flags=0` after the table insertion (the
   insertion adds a second axes-like table, so re-run it).
5. Byte-diff each of the seven amendment-2 spans; span 6 (`## Planned` plus two fenced bullets)
   must show an empty diff after this draft's section 3 is applied at EOF.
