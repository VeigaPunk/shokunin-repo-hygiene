# SwarmConnector65 — cross-round / cross-lane pattern map (read-only)

STATUS: PASS — pattern map delivered (34 rows, every quote verified against the bytes it cites); Q60–Q62 judged **new, not supersessions**, with two wording defects and one uncovered class reported.

Scope of this seat: read-only pattern finding across the lane's own lessons r23–r28 + the six routed defects, and across sibling lanes' `corpus/lessons` / `corpus/QUALITY.md` (read-only, never written). Lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; the landed tip observed this run is `1dc678500c92164b0b2bea82b934dd03d1dfbf38` (Q60–Q62 already committed there). No file outside `.ufo/waves/round-29/w1/` was written; no `git add/commit`, no `jj`, no signals, no scratch left behind (no `/var/tmp/souji-r29-SwarmConnector65*` was ever created).

## Evidence

Commands run this run (all read-only against the lane):

```
$ python3 -B tools/souji-registry-agreement.py --root <lane> --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md
K1 cited-not-in-used-by S075 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S076 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S022 corpus/knowledge/quarantine-origin-record-fields-r24.md
K1 cited-not-in-used-by S024 corpus/knowledge/quarantine-same-filesystem-rename.md
K1 cited-not-in-used-by S025 corpus/knowledge/quarantine-same-filesystem-rename.md
K2 uncorrected LOG.md:1758 / SCORECARD.md:23 / corpus/lessons/round-28.md:22 / :40
SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e

$ python3 -B census/round-29/c2-counter.py --root <lane> --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0

$ python3 -B tools/souji-registry-agreement.py --root <lane> --rev 1dc678500c92164b0b2bea82b934dd03d1dfbf38 --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
SUMMARY k1=0 k2=0 mismatches=0 rev=1dc678500c92164b0b2bea82b934dd03d1dfbf38

$ git show HEAD:corpus/QUALITY.md | grep -cE '^\| Q[0-9]+ '   -> 62 rows;  Q60|Q61|Q62 present
$ grep -c used-by corpus/QUALITY.md            -> 0   (at base: no in-lane used-by criterion)
$ grep -c wave-evidence corpus/QUALITY.md      -> 0   (at base: no in-lane wave-receipt criterion)
$ grep -c excluded.tsv census/round-29/c2-counter.py     -> 0   (frozen v1 counter)
$ grep -c excluded.tsv census/round-29/c2-counter-v2.py  -> 2   (A3 v2 counter reads it)
```

Every quote in the delivery was checked by substring match against the cited file:line (souji rows against the committed blob at `HEAD` for `census/round-29/c2-counter*.py`, `tools/souji-registry-agreement.py`, `corpus/QUALITY.md`; all other rows against the working-tree bytes; sibling rows against `/home/vgpnk/Projects/shokunin/<lane>/<file>`). 34 rows, 0 mismatches, 0 quotes over 25 words, 0 quotes containing a pipe character.

## Findings

1. **Recurring classes in the lane's own lessons are three, and two already have their criterion.** `number-drift` → Q58 (`corpus/QUALITY.md:142`), `attribution`/axis misreading → Q59 (`:143`), `reference-drift` on registry pointers → Q57 (`:141`). The lane's own lessons name the gaps precisely: `corpus/lessons/round-25.md:54` "number-drift — C1's `kill_tested=4` after-target was copied from a different base" (captured-by *none* at the time → Q58); `corpus/lessons/round-26.md:96` "the round-25 C2 claim declared operability for a change that covered four input edge classes" (captured-by *none* → Q59).

2. **The r28 "reference-drift" class is five rounds old and was never captured.** `corpus/lessons/round-24.md:171` — "registry `used-by` not swept", captured-by "`validate` checks that paths exist, not completeness". The r29 K1 arm is the same class, other direction (`corpus/lessons/round-28-verifier-spotcheck.md:123`, "S215 used-by names `corpus/knowledge/git-auto-maintenance-trigger-set.md`, which does not cite S215"). Q62 is therefore a criterion on a **five-round-old unclosed class**, not a new observation — and R24-M23 should be named as its origin row.

3. **Q60–Q62 are new rows, not supersessions.** Closest existing rows, with quotes: Q60 ↔ **Q57** "re-derive it from the named authoritative file at a named revision" (`corpus/QUALITY.md:141`) and **Q58** "A preregistered numeric target is derived at the named base revision, not copied from a prior round's different base." (`:142`) — Q60 governs whether a frozen *clause* was read as written, a different subject from Q58's number and from Q57's slice-tally citations (Q57 states it "is not an omission-discovery claim"). Q61 ↔ **Q55** "A count quoted in a lane record must name a receipt that binds the revision and the sha256 of the bytes that produced it." (`:129`) and **Q37** "A stamped revision is durable and binds the measured bytes." (`:91`) — Q55 binds the producing tool's bytes, Q61 binds the receipt *content set* to the committed tree. Q62 ↔ **Q56** "Every `corpus/knowledge/*.md` entry that declares `ground: F<k>` in its front matter must be named" (`:135`), the lane's own declared-vs-files counter precedent. Each of the three adds a binding dimension the closest row cannot see; none replaces one. Verified at `HEAD`: all five predecessor rows remain in force alongside Q60–Q62.

4. **Q55 is provably insufficient, from the lane's own lesson.** `corpus/lessons/round-24.md:155` — "Q55 cannot see a quoted value disagreeing with its receipt", captured-by "Q55 in name only". Q61 is the response; Q55 must stay.

5. **Q62's third sentence restates a shape Q57 already owns.** Q62 requires an `R29-CORRECTION <file:line>` line for a stale statement; Q57 already states "if a citation is superseded, append a note naming that exact `file:line`, the authority file and the recomputed value". Name Q57 rather than restating the append-a-note shape — otherwise the lane carries two append-only dialects.

6. **Sibling lanes already hold the two halves of Q62, separately.** audio-shokunin Q20 (`corpus/QUALITY.md:28`): "Each source row's `used-by` lists every knowledge entry and lesson that cites it" (row→entry). kaidoku-shokunin criterion 29 (`corpus/QUALITY.md:39`): "the entry's source line cites an opened, mined row whose used-by names that entry" (entry→row). chousa-shokunin ships the mechanical check: `tools/research-gate.sh:3451` "used-by does not name entry" (`META_SOURCE_USEDBY_MISSING`, fixture case `metadata-registry-used-by-path` at `:7228`). audio's own lesson names the root cause: `corpus/lessons/round-101.md:28` — "the SOURCES path census only proved listed paths existed", fix "validate completeness as well as existence". Q62's novelty is the *union* plus a committed-bytes counter; its halves are prior art and the criterion should cite them.

7. **The fleet already has a two-way-agreement idiom to copy the wording from.** kotodama-shokunin `corpus/lessons/round-20.md:97` — "\"Every index row names an existing file\" is a two-way check"; kumitate-shokunin `corpus/lessons/round-4-aggregator-audit.md:48` — "Index row is a claim — in both directions." Use this idiom for Q62 instead of inventing new phrasing.

8. **Sibling lanes already solved ignored-evidence capture two different ways.** kotodama-shokunin `corpus/lessons/round-67.md:52` — "scratch clone trees named excluded with reasons": its R66-D1 disposition is a committed manifest that dispositions every wave path with a reason (the same shape Q61 wants as `excluded.tsv`/`renames.tsv`). chousa-shokunin fixed the identical defect class twice: `round-44-verifier-spotcheck.md:154` "The RFC/WARP/E2867 captures are untracked, gitignored files in the campaign tree" → `round-45.md:118` "located spans committed under `corpus/evidence/round45/spans/` with the capture sha256 and offset". kaidoku-shokunin `round-25.md:138` already published the exact ignore probe the r29 capture tool uses: "git check-ignore --no-index --verbose --non-matching" (`deliver-souji-wave-evidence-capture.sh:206`). Two sibling criteria state the same discipline in general terms: mori-shokunin `corpus/QUALITY.md:356` "A counting command reads every input from committed bytes at a named revision." and kumitate-shokunin `corpus/QUALITY.md:406` "no untracked wave report at report filing, checked by a command". Q61 should name these rather than present the fleet practice as new.

9. **ATTACK-class wording defect in Q61's check column.** The frozen counter reads only `symlinks.tsv` — `census/round-29/c2-counter.py:73` "lt = d + 'symlinks.tsv'" and `grep -c excluded.tsv` on that blob = 0. Q61's criterion text names `renames.tsv` and `excluded.tsv` as files "the counter can check", but the counter named first in the check cell cannot check them; only the A3 `c2-counter-v2.py` has that arm (`c2-counter-v2.py:103` "acct = set(tsv_col(a.root, ents, d + 'excluded.tsv'))"). Recommend the check cell name the v2 counter for the accounting clause (no predicate change; the frozen bytes stay frozen).

10. **Scope note on Q62, not a defect.** The amended registry tool still couples the two arms in one exit code (`tools/souji-registry-agreement.py:193` "return 1 if f1 or f2 else 0"), so Q62 cannot go green on its citation half alone. That is acceptable only because Q62's own text also carries the stale-statement rule; if the L1 ever splits the stale-statement clause out of Q62, the check cell must be split with it. The citation arm *is* separately expressible without touching the frozen tool: at base the amended tool prints 6 lines starting `K1 ` and 4 starting `K2 `, at `HEAD` both are 0.

11. **One class is covered by nothing in Q60–Q62.** `corpus/lessons/round-28.md:35` — captured-by "none — no existing criterion required agreement between the checker and pointer gate" (the Q57 checker printed `q57=PASS` while the landing gate independently found 2). No proposed criterion forces *two instruments over the same tree* to agree. Q56–Q62 are all instance-scoped (one counter, one registry, one receipt). The uncovered class is a class-scoped agreement rule, and it is the cheapest addition that would prevent the r28 stale-premise class from recurring.

12. **A second, partly-uncovered class: the unevaluable gate.** `corpus/lessons/round-28-verifier-spotcheck.md:119` — "`souji-landing-gate.py`'s report check can never evaluate committed round reports" (routed defect 3). Q61 covers *receipts* over committed bytes; this is a *gate* whose input path is gitignored (`.gitignore:1` = `.ufo/waves/`). Q61's text should say which, or defect 3 stays uncovered.

## Attack log

Not an attack seat; no counter predicate, target or case set is proposed for change. Two wording-level attacks on the *proposed criteria* are reported as findings 9 and 10, both narrower-only and both compatible with the frozen instruments (finding 9 names the A3 v2 counter that already exists; finding 10 asks that any future split of Q62 also split its check cell).

## Deliveries

- `.ufo/waves/round-29/w1/deliver-pattern-map.tsv` — 34 rows, columns `pattern_id, scope, class, lane, file, line, evidence_quote, captured_by, closest_existing_row, proposed, verdict, recommendation`. Rows P1–P10 (lane-internal recurring classes and the six routed defects), C1–C7 (closest existing souji QUALITY rows for each proposed criterion), S1–S12 (cross-lane prior art), V1–V5 (landed-state and scope observations). Every quote re-verified against its cited bytes at write time.

Recommendation carried in the TSV's `verdict`/`recommendation` columns: **Q60, Q61, Q62 should stand as new rows that extend and cross-reference Q57/Q58, Q55/Q37, Q56 respectively — not as supersessions of Q55, Q57 or Q58.** All three are already committed at `HEAD` as new rows, which matches this finding. Add the class-scoped agreement rule (finding 11) as the next criterion rather than a fourth instance-scoped row.

## Tools

No tool was installed or upgraded this run; every command used Python 3 from the host (`python3 -B`, no `__pycache__` written) plus read-only `git` plumbing (`git show`, `git ls-tree`, `git rev-parse`, `git cat-file`, `git check-ignore`, `git status`). No pacman transaction was attempted (host-wide pacman guard). No scratch repository was needed: every measurement ran against the lane repo read-only, so no `/var/tmp/souji-r29-SwarmConnector65*` directory was created and none remains.
