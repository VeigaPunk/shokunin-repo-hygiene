# SwarmExecutor27 — round 31 wave 2, no-harm sweep (lane base → tip)

## Status

STATUS: PASS for the assigned scope (base→`2c16d01`: no harm) — one post-tip regression is flagged
after the lane advanced to `f950267`. 62 lane commands (every runnable registry self-test plus every
runnable
`tests/fixtures/*`) were run at base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` and at tip
`2c16d018e40db7c23420a2c3bb546b52957bcc25`, each in its own `git clone --no-local` with `origin`
removed: 57 return the same rc and the same last digit-bearing line, 5 differ for content-driven
reasons that are all benign, none flips green→red. `souji-registry-agreement` 0/0 and
`souji-coverage-agreement` 0/0 at both revs; the round-30 capability counter is
`k1=0 k2=0 mismatches=0` at the tip. Findings below are gaps or pre-existing defects, not
base→tip regressions, with one exception: the lane advanced during the sweep (`76bb697`, `f950267`)
and the harm-relevant readings were re-checked there — exactly one new defect appears,
finding 8 (declared-evidence 21→23 mismatches at `f950267`).

## Evidence

Scratch: `/fast/scratch/hyaku/souji-r31/w2-SwarmExecutor27/{base,tip,head}`, `TMPDIR` set explicitly,
`rev-parse --show-toplevel` verified per clone, base blobs extracted with `git -C <clone> show`.

Post-tip re-check (the lane advanced during the sweep; `git -C lane log --oneline 2c16d01..HEAD`
= `76bb697` wave-2 capture/entry corrections, `f950267` lesson + Q67-Q69 + SKILL gate rows +
SCORECARD r31 measurements + LOG + end census). At a fresh clone of `f950267`
(worktree was dirty with the L1's in-flight edits, so only the commit is read):

- `souji-registry-agreement` `k1=0 k2=0 mismatches=0`; `souji-coverage-agreement`
  `grounded=17 mapped=17 dangling=0 mismatches=0`; `souji-capability-agreement`
  `k1=0 k2=0 mismatches=0 rows=18`; `tools/souji-capability-cells.py`
  `items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` (L29 still unbound).
- `souji-declared-evidence` `assertions=252 resolved=229 skipped=401 mismatches=23` — two MORE
  than at base or at `2c16d01`, see finding 8.
- landing gate over rounds 19/24/26/27/28/29/30/31 = `6/20/3/3/3/3/3/3` findings; round 31's seven
  uncarried wave-1 reports are gone once `corpus/lessons/round-31.md` exists at `f950267`.
- `tests/fixtures/r31-landing-gate-precision.py` still `cases=10 pass=10
  control=FALSE-GREEN-REJECTED`; `tests/fixtures/r31-jj-object-clock.sh` still replays the committed
  record byte-identically.

Base→tip change set (`git -C tip diff --name-status 9f17a1e 2c16d01`, no deletions):

```
M PROVINCE.md M SCORECARD.md M SKILL.md M corpus/README.md M corpus/SOURCES.md
A corpus/knowledge/jj-dropped-keep-object-lifetime.md
M corpus/lessons/round-26.md M corpus/lessons/round-27.md M corpus/lessons/round-28.md
A tests/fixtures/r31-jj-object-clock.sh A tests/fixtures/r31-landing-gate-precision.py
A tools/souji-capability-cells.py M tools/souji-landing-gate.py   (+ census/round-31/**)
```

Sweep (full table in `deliver-no-harm.tsv`); the five differing rows, all benign:

| item | base | tip | why not harm |
|---|---|---|---|
| r20_input_binding | `baseline_mismatches=25` | `=26` | the only new baseline-drift entry is `corpus/knowledge/jj-dropped-keep-object-lifetime.md` (`baseline=missing`); 52/52 pass at both |
| tool_registry_agreement | `k1=0 k2=0 mismatches=0 rev=9f17a1e…` | same with `rev=2c16d01…` | only the rev token moves |
| tool_coverage_agreement | `grounded=16 mapped=16 dangling=0 mismatches=0` | `grounded=17 mapped=17 …=0` | the new F1 entry is mapped in `corpus/README.md:39` |
| tool_declared_evidence | `assertions=200 … mismatches=21` | `assertions=219 … mismatches=21` | `--format tsv` mismatch sets are byte-identical (diff empty); the 21 rows are SCORECARD lines 14–314, none of the appended 361–406 block |
| gate_replay_r29_counter | `manifests=5 failed=0 uncovered=0 floor_violations=0` | `manifests=6 … 0 0` | the sixth manifest is `census/round-31/waves/manifest.sha256` |

Red at both revs, unchanged: `souji-quarantine --selftest` (36 FAIL, identical line set,
N1/N2/N3 `got=4 want=3`), `tests/fixtures/r18-proc-census.sh` (same case P7 `rc=124` timeout under
host load), `souji-declared-evidence` (21 mismatches both ends). `tests/fixtures/r29-registry-agreement.py`
is red at both revs only with the registry's relative `--tool` (see finding 5).

Landing gate (`tools/souji-landing-gate.py`, the only changed tool; base blob vs tip blob, the same
committed content at `9f17a1e`), per-round `findings=` totals:

```
gate@9f17a1e over content 9f17a1e: r13 0 r16 0 r19 10 r20 9 r24 21 r26 21 r27 32 r28 24 r29 3 r30 3
gate@2c16d01 over content 9f17a1e: r13 0 r16 0 r19  6 r20 3 r24 20 r26 29 r27 32 r28 22 r29 3 r30 3
```

Every decrease is a base false positive the tip gate frees (`corpus/authority`, `tools/kill/killpg`,
`corpus/helper`, `corpus/source/QUALITY`, `:274–277` and `:395–396` line specs, `LOG.md:1106`/`:1123`).
The single increase, round 26 `21→29`, is the union discovery on the same bytes:
`checked_reports=466→495`, and the 8 new lines are exactly the capture-only reports whose
`.ufo/waves/round-26/w1/<name>.md` is absent at that rev (`git cat-file -e` = 8× absent/present pair),
each a genuine seat STATUS failure or partial line orphaned by the base gate. Full gate status at the tip:
rounds 13/16 clean; 26/27/28/29/30 carry-only clean (only the 3 residual pre-existing dangling
pointers each); round 19 = 3 dangling + 3 uncarried and round 24 = 3 dangling + 17 uncarried (both
pre-existing, their base-gate counts were 10 and 21); round 31 shows 7 wave-1 reports uncarried
(the round-31 lesson is not written yet).

Round-31 instruments, run by this seat at the tip:

- `bash tests/fixtures/r31-jj-object-clock.sh` → rc 0, 17 `RESULT` lines, and
  `diff` of its `RESULT`/version lines against `census/round-31/records/jj-object-clock-run.txt`
  is empty (replay identical).
- `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` →
  `cases=10 pass=10 control=FALSE-GREEN-REJECTED`; the same fixture with the base gate blob →
  `cases=10 pass=3`, failing exactly G1 G3 G4 G5 G6 G7 G8 and passing G2 G9 G10, i.e. the frozen
  REDARM set.
- `tools/souji-capability-cells.py --root <lane> --rev 2c16d01 --base 9f17a1e --list-rev 1d45496`
  → `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`, the item is `L29`
  `base-cell binding=- UNBOUND`. Independent check of the enumeration: all 41 `c1-cells.tsv`
  literals occur on the base SCORECARD line they name (41/41, 0 bad).

M1 receipts reproduced at the real lane with `--fleet-root` (read-only `git cat-file`): base gate at
`1d45496` gives r26 18 / r27 29 / r28 21 findings, where r28's 21 = 19 uncarried + 2 dangling; base
gate at `c610830` gives r26 0 / r27 0 / r28 2, and the tip gate at `c610830` gives 0 / 0 / 0 — the
same numbers as `m1-red-before.txt` and `m1-after.txt`. All `resolved@<40hex>` dispositions
(9 in r26, 16 in r27, 13 in r28) resolve to real commits; bullets 26/29/19.

Landing-gate precision at the tip is unchanged for the pre-existing residual set:
`corpus/README.md:217` ×2 and `corpus/knowledge/jj-colocation-receipts.md:148` cite
`.ufo/waves/hyaku/jj-w1/reports/`, absent at both revs (verified `git cat-file -e`), so they are
real pointers, not r31 artefacts.

## Findings

1. `SKILL.md:115` — calibration. The rewritten r30 bullet says "packedness, not the threshold, is
   what the record discriminates". The pinned record `census/round-30/records/jj-keep-expiry-run.txt`
   holds no packed/loose pair; its own last two steps differ only in the threshold
   (`step=7-default-expire-control keep_refs=8` vs `step=8-control-expire-now keep_refs=6`), and the
   fixture's header states the opposite intent: "followed by --expire=now on the same repository
   (step 8) to show the threshold is the lever"
   (`tests/fixtures/r30-jj-keep-expiry.sh:18-20`). The packed arm the sentence relies on lives in a
   wave-2 critic receipt (`census/round-30/waves/w2/SwarmCritic21-receipts.txt:62-63`), not in the
   cited record. Fix: name the receipt the packed arm comes from, or drop the "record discriminates"
   clause.
2. `SKILL.md` `## Gate registry` — operability. At the assigned tip the table has 63 lines, the same
   as base: no row for `tools/souji-capability-cells.py`, `tests/fixtures/r31-landing-gate-precision.py`,
   `tests/fixtures/r31-jj-object-clock.sh` or the c2/c3 counters, although wave 1 delivered five rows
   (`census/round-31/waves/w1/deliver-quality-q67-q69.md:25` "Block B — append to SKILL.md
   `## Gate registry`"). At `f950267` three of those rows landed (`souji-capability-cells`,
   `r31-landing-gate-precision`, `r31-jj-object-clock`, table now 66 lines); the two counter rows
   `r31-c2-counter` and `r31-c3-counter` are still absent, so the frozen C2/C3 instruments remain
   undiscoverable from the gate map while their fixtures are registered. Block A (Q67-Q69) landed at
   `f950267` (`corpus/QUALITY.md` is modified there).
3. `census/round-31/apply-c3.py` — hygiene/operability. A committed one-shot integration script that
   reads the wave directory by absolute path
   (`W = '/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1'`), rewrites four
   tracked files in place (`rw(...)` → `open(p,'w').write(s2)`) and `shutil.copyfile`s six delivery
   files. It is the only `apply/patch` script and the only census script with a hardcoded lane path
   (`git ls-tree -r 2c16d01 census/` scan), it is not reproducible from committed bytes alone
   (its input `.ufo/waves/round-31/w1/*` is untracked), and it bypasses the append-only discipline
   the round claims. This is dead weight in a cleanup lane; it should be deleted or replaced by a
   receipt that names the deliveries it applied.
4. `corpus/lessons/round-26.md:98,105` — calibration (cosmetic). Two adjacent
   `## Seat-reported failures` headings; the first carries only the intro paragraph
   ("Append-only carry of the round-26 committed seat STATUS failure lines (26 across the 466
   reports…") and zero bullets, the 26 bullets sit under the second. No instrument is misled (the
   tip gate reads both, the base gate merges adjacent carry headings — verified: base gate at
   `c610830` returns r26 0), but a reader of the append sees a carry section that claims 26 entries
   and carries none. Same commit; one heading and one paragraph are redundant.
5. Pre-existing, unchanged base→tip, reported because this sweep is the lane's hygiene reading:
   the registry's own command for `souji-registry-agreement`
   (`python3 -B tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py`)
   prints `cases=20 pass=0` because the fixture resolves the relative tool under
   `/var/tmp/souji-r29-c1-fixture`; with an absolute `--tool` it is
   `cases=20 pass=20 control=FALSE-GREEN-REJECTED` rc 0 at both revs. Also unchanged:
   `souji-quarantine --selftest` 36 FAIL, `r18-proc-census` P7 timeout, `souji-declared-evidence`
   21 mismatches, and the three residual dangling pointers listed under Evidence.
6. `corpus/knowledge/jj-dropped-keep-object-lifetime.md:1` — coverage/hygiene nit. The landed entry's
   first source line still reads "S222 — git-reflog(1) at tag v2.56.0 (placeholder id: the L1
   renumbers by document)" although `corpus/SOURCES.md:167` carries S222 and
   `souji-registry-agreement` is `k1=0`. At `f950267` a later bullet in the same entry
   ("Supersedes the source line's `(placeholder id: the L1 renumbers by document)`…") discloses the
   resolution, so the defect is now cosmetic; the source line itself should still lose the note.
7. C1 target, measured independently: `unbound=1 mismatches=1` at the tip (L29), so the frozen
   `unbound=0 mismatches=0` is not met on the calibration axis. This matches the L1's pre-landing
   A4 disclosure and `census/round-31/records/c1-after-a4.txt`; it is the claim's own miss, not a
   regression introduced by wave 2. It still reads `unbound=1` at `f950267`.
8. `SCORECARD.md:424` (landed in `f950267`) — calibration, NEW after the assigned tip. The jj
   object-clock measurement row cites its sibling records inconsistently: v1 is cited with its
   directory (`census/round-31/records/c3-after-c3-counter.txt`) while v2 and v3 are cited as bare
   basenames (`c3-after-c3-counter-v2.txt`, `c3-after-c3-counter-v3.txt`). `souji-declared-evidence
   --root . --file SCORECARD.md --rev f950267 --format counts` therefore returns
   `mismatches=23` against `21` at base and at `2c16d01`, and the two new rows are exactly
   `424 c3-after-c3-counter-v2.txt A mismatch:path-absent` and
   `424 c3-after-c3-counter-v3.txt A mismatch:path-absent` (the files exist under
   `census/round-31/records/`). Fix: prefix both tokens with `census/round-31/records/`; that would
   return the instrument to its pre-existing 21.

## Attack log

- Union discovery could be a false-positive farm: re-ran base and tip gates on the SAME committed
  content and enumerated every added line — all 8 additions are capture-only reports absent from the
  `.ufo` tree at that rev; `checked_reports` 466→495 matches the prereg's "29 capture-only" claim.
- Gate loosening (letters-only prose rule, `.captured` mapping, `:text` suffix, ellipsis, line
  ranges): ran the frozen G1–G10 fixture at the tip (10/10) and against the base gate (3/10) — the
  discarding rules are held by a red arm that fails exactly the seven required cases, and each of the
  six removed r20 findings is a real non-path (`corpus/authority`, `tools/kill/killpg`, …).
- Appended SCORECARD block could carry wrong line numbers or invented literals: parsed all 40 rows and
  checked the 41 `c1-cells.tsv` base literals against the base blob — 41/41 present, all line numbers
  ≤ 359 (base length), none in the append pointing at itself.
- Append-only carry could hide unresolved work: every `resolved@` hash in the three lessons exists as
  a commit (`git cat-file -e <h>^{commit}`), 26/29/19 bullets, and the base gate at the pre-append rev
  reproduces 18/29/19 uncarried.
- Instruments could be gamed: ran the new C1 counter and the round-30 capability counter myself; both
  reproduce the recorded readings (`items=41 … unbound=1`; `rows=18 mismatches=0`), and the 3
  agreement tools show no regression across the change.
- Re-ran the two red fixtures and the r29 fixture in isolation to separate lane defects from my own
  invocation error (finding 5) — the r29 red is an invocation artifact at both revs, not a
  regression; quarantine/proc-census reds are identical at both revs.
- The lane moved under the sweep: cloned `f950267` and re-ran every instrument that reads the files
  the two new commits touched (SKILL, QUALITY, SCORECARD, LOG, lesson, README, entry). Registry,
  coverage and capability agreements stay 0; the landing gate's round 31 goes 7 uncarried → 3
  pre-existing dangling; the two r31 fixtures stay green and replay-identical; only
  `souji-declared-evidence` moves, 21 → 23, and the two new rows are the citation defect of
  finding 8.

Not run, with reason: `census/round-18/leak-count.py --selftest` (whole-host live `/proc` census,
excluded per seat instruction); `tools/souji-proc-census.sh --selftest` and
`tests/fixtures/r18-proc-census.sh` WERE run because both are bounded to fixture-owned workers; no
network-dependent fixture exists in the lane. `tests/fixtures/case-F*`, `*-frozen` and
`q54-mutant-entry.md` / `r22-result-oracle.json` are inputs, not runnable gates.

## Deliveries

- `.ufo/waves/round-31/w2/SwarmExecutor27.md` (this report).
- `.ufo/waves/round-31/w2/deliver-no-harm.tsv` — 65 rows: `item, base_rc, base_last_digit_line,
  tip_rc, tip_last_digit_line, delta, note` for the 62 commands compared base→tip `2c16d01` plus the
  3 new-at-tip instruments. The post-`2c16d01` readings live in this report's Evidence block and
  finding 8, not in the TSV.
- Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmExecutor27/` removed after the copies. Nothing was
  written in `/home/vgpnk/Projects/shokunin/souji-shokunin` or anywhere else outside the two paths
  above; no `git`/`jj` mutation ran in the lane; no package transaction ran (no tool installed,
  upgraded or removed this seat).
