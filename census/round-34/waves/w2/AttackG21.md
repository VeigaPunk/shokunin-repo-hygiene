# AttackG21 — adversarial falsification of W1's G21 finding (r34 w2, seat SwarmCritic05)

## Status

W1's G21 finding is **CONFIRMED** at source level; every load-bearing link was re-derived from committed bytes
at the pinned revisions, and W1's two counter executions are corroborated by the committed do-nothing control.
One W1 diagnostic sentence is **refined** (root cause is a stale item line number, not a 0-based items file),
with no change to the operational outcome. No honest rule-conforming route exists on the frozen bytes; the
only counter-accepted restatement carries false provenance with a **unique, deterministic** forgery key.
This is evidence review plus bounded read-only probes; no counter run, fixture run, or clone was executed here.

## Evidence

Revisions: base `9c76c7222a8abff027af42e37f0d160d52526bba`; frozen list/counter `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`
(earlier freeze `2b591924f607940febbb99f922cc9bb090508eb6`; G21's `c1-items.tsv` row and all of `c1-counter.py`
are byte-identical between the two freezes — verified by `git show ... | diff`).

- **Frozen item** `census/round-34/c1-items.tsv:38` (at 2b0171e):
  `G21  SKILL.md:245  0  cases=20 pass=20 control=FALSE-GREEN-REJECTED  tests/fixtures/r29-registry-agreement.py,tools/souji-registry-agreement.py  {REV}  python3 -B tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py`.
- **Row location**: at base and at list-rev (SKILL.md identical in both), `git show <rev>:SKILL.md | grep -n "^| souji-registry-agreement |"` → **246**; line 245 is the `souji-pre-report-gate` row. At `4d9bf02^` the registry row was at 245; `4d9bf02` (r33 integration, ancestor of base) inserted lines above → 246. So the enumeration number predates the pinned base, contradicting the TSV header "Line numbers are at base 9c76c72".
- **Counter cause check** `census/round-34/c1-counter.py:293-301` (at 2b0171e): `lineno = int(where.rsplit(":",1)[1])`; `line_text = blob(root, list_rev, "SKILL.md").split("\n")[lineno-1]` → index 244 = 1-based line 245 = the pre-report-gate row; reject when `line_text in before(parent)` or `line_text not in after(cause)`; then require `holds(item's own argv at cause) is False`.
- **Honest cause transition** (content probes, committed bytes): parent of `1dc678500c92164b0b2bea82b934dd03d1dfbf38` (= `b86200714069022954a3b498cf697d894119b45e`) already contains line-245 text (`grep -cF` = 1) → check fires; parent lacks line-246 text (= 0) while the cause has it (= 1) → would pass with the correct line number. `git show 1dc6785 --stat` shows `SKILL.md | 5 +`.
- **Bogus cause transition**: parent of `6cb22dc20c9fdb3c7a49eaa1accabca339054c17` (= `270652720d12572dbc6a464ea938fbd59ad88275`) lacks line-245 text (= 0), cause has it (= 1); `git show 6cb22dc -- SKILL.md` is `-`+`|` replacing a blank line with the pre-report-gate row. `git log -S "<line-245 text>" -- SKILL.md` returns **only** 6cb22dc — the false-accept key is unique and forced, not selected.
- **Fixture cwd**: `tests/fixtures/r29-registry-agreement.py:140-142` at base and at 1dc6785: `subprocess.run([sys.executable, "-B", tool, ...], cwd=BASE)` with `BASE = "/var/tmp/souji-r29-c1-fixture"` (line 18) — a relative `--tool` resolves against BASE → ENOENT. Fixture absent at 6cb22dc (`git cat-file -e` fails).
- **Execution mechanics**: `c1-counter.py` `run_item` runs the (restated) argv via `bash -c` with `cwd=clone`, so W1's corrected argv's `$PWD` expands to the clone root; the absolute tool path exists there.
- **Committed do-nothing control** `census/round-34/records/controls-c1-do-nothing.txt:22`: `ITEM G21 MISMATCH original rc=1 ... stderr=/usr/bin/python3: can't open file '/var/tmp/souji-r29-c1-fixture/tools/souji-registry-agreement.py'`.
- **W1 receipts**: `.ufo/waves/round-34/w1/deliver-c1-G21.md` (honest row → `BAD-CAUSE(cause did not write the row's line)`; bogus cause → `ITEM G21 AGREE restated ... last=cases=20 pass=20 control=FALSE-GREEN-REJECTED`); `.ufo/waves/round-34/w1-results.json` (SwarmExecutor04 and SwarmExecutor01 L1 follow-up record both executions; Executor01 names G21 among 7 base MISMATCHes).
- **Q76 prior-correction scan**: `git show 9c76c72:SCORECARD.md | grep -n G21` → no hits; L36 (SCORECARD.md:401, binding cell SCORECARD.md:313) runs the default-tool form `python3 -B tests/fixtures/r29-registry-agreement.py` and does not bind the SKILL.md:245 row. Preregistration `census/round-34/preregistration.txt:48-53`: argv-correction valid only with a cause that "wrote the row" and whose run already failed the row's argv.

## Findings

1. **The alleged defect is real and reachable — not an artifact.** The frozen argv is broken by construction
   (fixture forces `cwd=/var/tmp/souji-r29-c1-fixture`; the control record at `controls-c1-do-nothing.txt:22`
   shows the exact ENOENT), and the counter's cause check tests the wrong line because the item pins
   `SKILL.md:245` while the registry row sits at 246. The honest cause `1dc6785` provably wrote the registry
   row (`SKILL.md | 5 +`; parent lacks the row text, cause has it) yet is rejected; W1's execution receipts
   match the deterministic code path exactly.
2. **The gate is inverted, with a unique forgery key.** `git log -S` shows 6cb22dc is the only commit whose
   parent→cause transition introduces the current line-245 text; the fixture's absence there makes the
   second check (`row's argv failed at the cause`) pass vacuously (rc=2); the corrected argv then AGREEs at
   the measured rev. No other commit can pass the line check, so the counter-accepted restatement is forced
   to cite an r27 commit that predates the r29 fixture and tool — false provenance, deterministic.
3. **Refinement of W1's diagnosis (no operational change).** W1 wrote "the r34 items file numbers lines 0-based
   while the counter's argv-correction path indexes 1-based". Committed history shows the items file is not
   0-based: 245 was the row's correct 1-based number at `4d9bf02^`; the r33 integration commit 4d9bf02
   (ancestor of base) moved the row to 246, and the frozen number was never updated to the pinned base the
   TSV header claims. Net effect is identical to W1's — the counter reads the pre-report-gate row — but the
   smallest safe correction targets the stale item line (renumber G21 to `SKILL.md:246`), not the counter's
   indexing; a counter "tolerance" change would touch frozen trust-boundary code. Any fix is an L1 ruling
   (frozen-list amendment), matching W1's routed "stricter-only amendment vs routed defect" framing.
4. **No honest rule-conforming route exists (alternate routes checked and closed).**
   - `same` restatement: requires the row's own argv to hold at the cause's parent — it fails at every
     revision (broken by construction) → `BAD-CAUSE`. Closed.
   - argv-correction with the true cause: rejected on the line-content check (finding 1). Closed.
   - Renumbering via the restated row's `where` cell: `c1-counter.py` requires `where == item["where"]`
     (`BAD-ROW(where or kind)`), and the items TSV is frozen at list-rev — a restater cannot amend it. Closed.
   - Q76/L36 prior-correction route: no SCORECARD row binds G21 (grep = 0 hits at base); L36 binds the
     SCORECARD.md:313 cell with the default-tool invocation and, even if invoked as G21's correction, the
     cause-line arithmetic is unchanged. Closed.
   - Reachability proof for the fix: with the item line at 246, W1's exact proposed row passes every frozen
     check (line-content transition verified; `holds(original argv at 1dc6785)` = False since the fixture
     already had `cwd=BASE` there; statement equals the run's last digit-bearing line under `bash -c` `$PWD`
     expansion). So the blockage is purely the stale line number.
5. **Inter-seat tension resolved.** SwarmExecutor13's note (G21 mismatch "caused by a hardcoded /var/tmp ...
   path ... not a committed-bytes cause") classifies the do-nothing mismatch as environment-conditioned;
   that is compatible with W1: the mismatch mechanism is host-path-conditioned, but the restatement cause
   (1dc6785) is commit-derivable and the counter blockage is deterministic committed code + frozen bytes.
   Nothing in Executor13's reading falsifies W1's attack.

## Attack log

- Read W1 deliverable `deliver-c1-G21.md`, `w1-results.json` (Executor01/04/13/Scribe35 G21 lines), frozen TSV row, frozen counter source, preregistration contract, Q75–Q78, committed do-nothing control, base SCORECARD cells 313/401.
- Bounded read-only probes (all `git show`/`grep -n`/`grep -cF`/`git log -S` against pinned revisions; no execution): row line numbers at 9c76c72, 2b0171e, 4d9bf02, 4d9bf02^, 1dc6785; cause/parent content transitions for 1dc6785 (b862007) and 6cb22dc (2706527); uniqueness pickaxe for the line-245 text; fixture `cwd=BASE` presence at base and 1dc6785, absence at 6cb22dc; freeze-drift diff of `c1-items.tsv` G21 row and `c1-counter.py` between 2b591924 and 2b0171e (both identical).
- Adversarial attempts that failed to falsify W1: (a) alternate numbering convention — disproven by 4d9bf02 drift; (b) honest-route search — all four routes closed above; (c) measurement-artifact theory for the bogus acceptance — disproven by the `-S` uniqueness and deterministic code path; (d) freeze-revision drift — disproven by byte-identical diffs.
- Probes deliberately NOT run: live counter do-nothing or scratch restatement clones (lane `.git` is 77 MB > the 50 MB scratch ceiling) and live fixture execution (fixture uses the shared fixed path `/var/tmp/souji-r29-c1-fixture`; ~80 live peers make a Q77 race likely). All execution claims above are W1's committed receipts; everything else is derived from committed bytes and labeled as such.
- No lane files, frozen artifacts, or other repositories touched; no commits; nothing written outside the two report paths.

## Deliveries

- `.ufo/waves/round-34/w2/AttackG21.md` (this file)
- `.ufo/waves/round-34/w2/SwarmCritic05.md` (seat report, same content)
