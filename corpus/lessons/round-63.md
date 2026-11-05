# Round 63 — honest stop: in-run receipt refusal and concealment classes (C1), statement agreement (C2)

Base `728ab685617e412172a8e5cb6260f7098b486aec`. Pre-freeze controls commit `d7bd4ff2`. No preregistration was
frozen and no production writer or SKILL bytes changed this round. Outcome: **both declared claims are not
admitted** (see `## Claim`). The wave (11 seats, one v1 wave, `.ufo/waves/round-63/w1/`) produced the candidate
writer, counters, and an attack set that this lesson records.

## Claim

Declared intent (wave context, dispatched before any seat ran): two claims on distinct axes.

- **C1, operability.** The receipt writer refuses a change made by the wrapped command while it runs (flag set,
  tracked edit, untracked creation), and classes unmerged, gitlink and absent index entries under their own
  refusal tokens. Candidate: `eba4f7e0d1218d88158459426de3ad505e7401201af7ad006415daed31f9586f`
  (`.ufo/waves/round-63/w1/S63ExecWriter/souji-receipt-write.py`).
- **C2, calibration (lowest owned axis, score 7).** Three SKILL.md statements about the writer's enforced scope
  agree with the writer bytes in both directions (overreach and stale-open).

Diagnostic measurements (not frozen, scored before any preregistration existed; see Mistakes M2):

| check | base (do-nothing) | candidate `eba4f7e0` |
|---|---|---|
| C1 counter, 9-row matrix | `new_forgeries=4 class_mismatches=4`, EXIT 1 (`census/round-63/controls/c1-do-nothing.txt`) | `new_forgeries=0 new_honest=3 class_mismatches=0 regress=PASS`, EXIT 0 (`census/round-63/records/c1-after-candidate-eba4f7e0.txt`) |
| C2-edge classes, 5-row matrix (P1 P2 H1 H2 H3) | `base_class_mismatches=3`, EXIT 1 (`census/round-63/controls/c2-do-nothing.txt`) | `new_class_mismatches=0`, EXIT 0 (`census/round-63/records/c2-after-candidate-eba4f7e0.txt`) |
| C2-statements (SKILL-only population, 3 rows) | `findings=1` (`s2` overreach), EXIT 1 (`census/round-63/controls/c3-do-nothing.txt`) | not measured (no after-wording landed) |
| kind-only forgery: after-wording, base writer | `findings=4`, EXIT 1 (`census/round-63/controls/c3-kind-only-forgery.txt`) | — |

## Why neither claim is admitted

1. **Chronology (Q120).** The candidate was scored before any predicate was frozen. The seats' counters and mine ran
   on `eba4f7e0` before the preregistration existed. The predicate text existed in the wave context, but the
   instruments and the matrix did not.
2. **Declared rule changed after scoring.** The C1 matrix as first drafted had an H4 row (sparse-excluded forged
   file, expected `RECEIPT-INDEX-FLAG-CONCEALED`). The sentinel measured it failing on the delivered candidate
   (F6: a present sparse-excluded file is `H` and is refused as dirty, so no writer can produce the class). H4 was
   removed from the frozen matrix after that measurement. The lane rule forbids this for the same claim; it can
   only be re-declared with a fixture proven realizable before declaration.
3. **Population changed after scoring.** The C2 population was first a mix of SKILL.md and
   `corpus/knowledge/skip-worktree-concealment.md`. The critic showed the knowledge entry maps to coverage
   (`SURFACE_AXIS`), so the population was narrowed to SKILL.md. The sentinel had already run the counter with the
   base wordings (F10), so the narrowing post-dates a scored run.

Consequence: C1 and C2 are **unprovable as declared**; the diagnostic numbers above show the candidate beats the
do-nothing control on the stated counters, which is exactly the situation the honest-stop rule names. No axis is
harmed by this round (no production bytes changed). Score cells stay calibration 7, coverage 8, operability 8.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | Frozen matrix row not realizable: H4 (sparse-excluded forged) could not produce its expected class on git 2.56.0; the design declared it without a pre-declaration probe | `.ufo/waves/round-63/w1/S63SentinelScope.md` F6; `.ufo/waves/round-63/w1/S63ExecCounterC2/c2-counter.py` `--h4` variants | none (the sentinel found it after dispatch; no rule requires each fixture row to be probed before declaration) | H4 removed from `census/round-63/c2-matrix.tsv` and `c2-counter.py`. Fix not yet shown able to fail: a freeze-time check that runs each row's fixture and matches its class is routed to round 64 |
| M2 | Chronology: candidate writer scored before the preregistration froze (Q120 requires controls and freeze before scoring; this round scored first) | `census/round-63/records/c1-after-candidate-eba4f7e0.txt`, `census/round-63/records/c2-after-candidate-eba4f7e0.txt`, created before any `preregistration*.txt` | none (no mechanical check in `tools/souji-freeze-check.py` binds candidate-measurement time to freeze time) | Not claimed. Routed: round 64 freezes first, then scores; the freeze-check arm must refuse a receipt whose rev post-dates the freeze commit |
| M3 | Population changed after a scored run: the C2 population was narrowed to SKILL.md after the sentinel's counter run on the wider population | `.ufo/waves/round-63/w1/S63SentinelScope.md` F10; `census/round-63/c3-statements.tsv` (3 rows) | critic `S63CriticClaims` (C3 surface finding) | narrowed before freeze; the post-scoring narrowing is disclosed here, not hidden |
| M4 | Round-62 spot-check R2 defect: the round-62 lesson claimed the S292 quote was "verbatim in the raw capture (offset 8351)"; the quote is located only after markup stripping | `corpus/lessons/round-62-verifier-spotcheck.md` §1 CD3 and §6 R2; `corpus/lessons/round-62.md` `## Gate` | closure spot-check (not captured inside the round) | appended correction in `corpus/lessons/round-62.md` (this round); the earlier entry is not rewritten |

## Gate

Sources opened 2026-11-05 (scout seat `S63ScoutSources`; captures and probes under
`.ufo/waves/round-63/w1/S63ScoutSources/`):

- **S294 admit** — git-fast-import(1), file mode 160000 is a gitlink, https://git-scm.com/docs/git-fast-import,
  § OPTIONS `filemodify`; accessed 2026-11-05 (HTTP 200; sha256 `4830e69c…d72e9`; capture
  `census/round-63/sources/s294-git-fast-import.html`). Located quote (13 words, offset 31053 of the tag-stripped
  text, raw offset 109019, contiguous in raw bytes): `A gitlink, SHA-1 of the object refers to a commit in another repository.`
  Scope: the mode fact only. The 15-word form with the mode number is not contiguous in raw bytes and is not cited.
- **S292 used-by widened (no new row for the unmerged tag)** — git-ls-files(1) `-t`/`-v` tag table, already
  opened 2026-11-05 in round 62. The `M` letter (`tracked file that is unmerged`) is re-located in the committed
  capture `census/round-62/sources/s292-git-ls-files.html` at tag-stripped offset 7840 (line 345), raw offset
  53257 (line 2376), contiguous.
- **Rejected inference (discernment sample, recorded not admitted).** "A gitlink with a clean `git status` is a
  gitlink with an unchanged worktree." Rejected by the scout's probe: a committed gitlink whose worktree path is
  absent shows as ` D` in `git status --porcelain` (a deletion), not silence; `git ls-files -u -z` is empty.
  Flip: a manual statement that status is silent for absent gitlinks.
- **Assimilation: none.** `considerthese/` does not exist in this lane. The connector seat `S63ConnectorOverlap`
  read `/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md` read-only; its findings are in
  `.ufo/waves/round-63/w1/S63ConnectorOverlap.md` (no theme adopted this round).
- **Non-author spot-check:** pending for S294 and for this lesson's diagnostic numbers.

## Named limits (carried as observed; none claimed)

- **Allow-dirty content-blindness (HIGH, sentinel F1, reviewer H1).** With `--allow-dirty`, an in-run append to an
  already-dirty tracked file, and an in-run new file inside an already-untracked directory, are accepted; porcelain
  bytes do not change. The candidate does not close this. A content-bearing snapshot (sentinel
  `mitigation/cand-mit.py`, not run against the r60/r62 fixtures) is the routed fix.
- **Transient restore accepted (F5, reviewer H2).** A forge-then-restore inside the run is invisible to any porcelain
  or flag snapshot. The receipt binds the committed blob digest, not the executed bytes.
- **Detached child (F2).** A child that outlives the wrapped command and edits a tracked file after exit is accepted
  by base and candidate; the post-read runs at the wrapped process's exit.
- **Subdirectory root (reviewer H4).** `ls-files -v -z` under a subdirectory root without `:(top)` is a reachable
  bypass; not covered by any frozen row.
- **GIT_INDEX_FILE (reviewer H5, critical).** A caller-set index file is not recorded and not scrubbed.
- **Overflow ordering (reviewer H3, critical).** The `--max-bytes` refusal precedes the post-read. An overflowing run
  refuses anyway, so no receipt is forged; the refusal class differs.
- **fsmonitor-valid bit (sentinel F3).** `ls-files -v` renders it as `H`; the candidate refuses only because the status
  re-read runs with `core.fsmonitor=false`.
- **Gitlink with `H` tag (reviewer C2.2).** A gitlink whose tag is `H` (no flag) is never read by the flag loop; the
  class applies only when a flag is also set. Gitlink class must read the `-s` mode, never the `-v` tag (scout).
- **Sparse-induced `S` (scout; sentinel F7).** A sparse-excluded absent file is tagged `S` and survives
  `core.sparseCheckout` unset; it is indistinguishable from a manual skip-worktree deletion and takes the ABSENT class.
  The earlier sentence "sparse-checkout-induced S tags keep the generic class" is false for absent files.
- **Class check is a stderr substring; marker tokens are byte needles.** A comment-only marker in the writer would
  satisfy the C2 counter's marker check (reviewer C3.2, critic). The counter is text-and-marker agreement, not semantics.
- **C2 population of three SKILL.md rows is thin** (critic). A kind-only forger editing only the knowledge entry is
  outside it by design (the knowledge entry is coverage-mapped).
- **Axis tie-break unresolved.** Edge-class refusals: operability by Q59 and round-62 F1; coverage by round-25 C2
  (`SCORECARD.md` r25 row). Both precedents are in the lane record. Routed to the operator (L0 line this round).

## Routed to round 64

1. Freeze before scoring: preregistration first, then the candidate commit, then measurement; the freeze check must refuse
   a receipt whose rev post-dates the freeze (M2).
2. Probe each frozen matrix row's fixture against the base and candidate writers before declaration (M1).
3. Content-bearing snapshot for `--allow-dirty` and a matrix row for the F1 shape (sentinel F9); `:(top)` pathspec and
   GIT_INDEX_FILE scrub (reviewer H4, H5).
4. SKILL.md:830 overreach sentence (round-62 spot-check R1, calibration) — routed, not edited this round.
5. Knowledge-entry `verified-at` refresh (round-62 spot-check R3) — routed.
6. Operator decisions still open: `## MACHINE BLOCK` for preregistrations and numeric axis mapping (`.ufo/l0-questions.md`
   lines 324–325, round 62); the edge-class axis tie-break (new L0 line this round).
