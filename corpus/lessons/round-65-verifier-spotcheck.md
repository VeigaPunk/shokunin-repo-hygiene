author: hyaku closure (non-author integrator, @m_zfl)
round: 65 (souji) — non-author closure spot-check
date: 2026-11-05
report: .ufo/reports/round-65/souji.md (fleet repo, commit c0ba37cc by souji-shokunin <souji@shokunin.local>)
lane HEAD before → after: 4a43a4d919c5b51ae9be859a1266ce4b11337b0b → f6358d2cc28e8fefa28ab343f561e38e0867d791

## Conformance results

| check | result | evidence |
|---|---|---|
| report committed by lane identity | PASS | `git log --format='%an <%ae> %H' -- .ufo/reports/round-65/souji.md` → `souji-shokunin <souji@shokunin.local> c0ba37cc5c68a74a848611e363ff330377c2934b` |
| `SHONEN` heading, one line per box | PASS | report lines 83–88: `## SHONEN` + four `[~]` lines (4 boxes) |
| all cited lane commits exist and are ancestors of the branch ref | PASS | 14/14 hashes (`2761f0aa`, `3c5bfdc0`, `d2850b3e`, `022cf979`, `40a371d8`, `16da2445`, `af81553f`, `a3f98054`, `0f2fefb1`, `ef00ac57`, `a46e0749`, `494c00df`, `6147f025`, `f6358d2c`) pass `git cat-file -e <h>^{commit}` and `git merge-base --is-ancestor <h> refs/heads/master` (jj-colocated repo; ancestry tested against the branch ref, not `@{u}`) |
| no uncommitted round work; pushed | PASS | `git status --porcelain` empty; `scripts/hyaku/jj-lane.sh state` → `branch=master local=f6358d2c… remote=f6358d2c… ahead=0 behind=0` |
| prompt carries the template contract | PASS | `.ufo/prompts/souji-round-65.md` renders `templates/round-prompt.md` sections 1–5 verbatim (mission/axes binding; 1–3 claims incl. lowest-axis rule; frontier step 2b with the census command; L2 floor; report contract incl. SHONEN; commit-then-push, push scope, L0 channel) + hyaku addendum §6 |
| dispatch evidence digest | PASS | watchdog.log: `2026-11-05T09:59:23-03:00 launch souji round=65 pgid=2895289 driver=hyaku-inline attempt=1` / `2026-11-05T11:16:49-03:00 complete souji round=65; hyaku-inline attempt=1` — matches the closure digest |
| marker check | PASS — real report, not a marker | many checkable commits cited; receipts and instruments committed |
| misroot sweep re-run at closure | PASS | `git -C /home/vgpnk/Projects/shokunin status --porcelain` → only ` M .scratch/run15-state.json` and `?? .ufo/closure-kaidoku-r92.json` (orchestrator-owned; another lane's closure temp). No souji-authored file at the fleet root |

## Per-claim re-check

Both claims rest on lane-owned counters (`census/round-65/c1-counter.py`, `c2-counter.py` = gates under
PROTOCOL §Gate standard). Per the closure consequence I verified their committed evidence and did NOT
execute a sibling's gate; the plain measurements below are my own greps/wc/sha256/diff over committed bytes.

### C1 — operability (writer refuses 4 concealment classes; frozen 19-row matrix)

Evidence-verified (frozen-run verdicts + revision pin), corroborated by plain measurement:

- Before (do-nothing control, base bytes): `census/round-65/controls/c1-do-nothing.txt` →
  `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=12 new_honest=5 class_mismatches=12 regress=PASS`, `EXIT=1`.
- After: `census/round-65/records/c1-after-494c00df.txt` →
  `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`, rev bound `494c00df…`.
- Matrix size: `wc -l census/round-65/c1-matrix.tsv` → 20 (header + 19 rows). Control and after receipts both record the same matrix sha256 `a521170c…` — the frozen matrix did not move.
- Instrument pin: `sha256sum census/round-65/c1-counter.py` → `6401b35d…` — equals the pin recorded in both receipts and the report's stale-state note.
- Writer bytes: `git diff af81553f 494c00df -- tools/souji-receipt-write.py` → empty (identical); `git diff 40a371d8 494c00df` shows the docstring-only key-scope correction at `af81553f` (wording, no behaviour) — matches "no writer behaviour changed after `40a371d8` except the docstring".
- Mechanism greps in writer bytes @`494c00df` (my own, over committed bytes): `-c status.showUntrackedFiles=all` on every status read (2 sites); snapshot records `oct(os.stat(full).st_mode & 0o777)` beside the digest with `mode <path>` diff rows; symlinks recorded by name + target bytes (`symlink:` + `os.readlink`), never followed; `GIT_INDEX_FILE` env refusal (`RECEIPT-INDEX-ENV-SET`) before any git call. All four claimed refusal classes are present in the bytes, and the after-receipt shows each matrix row refusing with the expected finding class (V1, MOD, SY2, P13, N3).
- Honest accepts preserved: rows A, B, T4, SY1, V2 all `new=accept` in the after receipt — 5/5, matching `new_honest=5`.
- Independent reproduction corroborated in the committed wave mirror: `census/round-65/wave/w1/S65ExecScore.md` → repro C1 `matrix=19 … new_forgeries=0 … regress=PASS` EXIT=0, writer selftest `cases=30 pass=30`, c1 selftest `cases=8 pass=8`, c2 selftest `cases=13 pass=13`.
- Selftest tallies cited by the receipts: `census/round-65/records/writer-selftest.txt` (`SELFTEST cases=30 pass=30 fail=0`), `freeze-check-selftest-chronology.txt` (`cases=52 pass=52`), `freeze-check-substance-at-freeze.txt` (`SUMMARY claims=2 findings=0`).

Verdict C1: verifies. Before→after re-derived from committed receipts and byte-level greps; reported values match exactly.

### C2 — calibration (4 SKILL statements agree with writer bytes under live-marker read)

Evidence-verified, corroborated by plain measurement:

- Before: `census/round-65/controls/c2-do-nothing.txt` → `findings=2 verdict=FAIL` (s2 SCOPE-OVERREACH, s4 GOVERNED-STATEMENT-UNRESOLVED), `EXIT=1`.
- After: `census/round-65/records/c2-after-494c00df.txt` → `MARKERS flag=1 inrun=1 env=1 unmerged=1`, `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0`, instrument sha `afd4cb54…` — `sha256sum census/round-65/c2-counter.py` matches the pin.
- Statement rows: `wc -l census/round-65/c2-statements.tsv` → 5 (header + 4 statements s1–s4); TSV rev pinned `2761f0aa…` in both runs.
- SKILL.md @`494c00df` grep (my own): the after-wordings are present with their live markers — the round-65 writer-rule sentence carries `RECEIPT-INDEX-FLAG-CONCEALED`, `RECEIPT-STATE-CHANGED-DURING-RUN`, `RECEIPT-INDEX-UNMERGED` and the in-run scope qualification; the round-65 deltas line names `status.showUntrackedFiles=all`, the mode column, the symlink rule and the `GIT_INDEX_FILE`/P13 refusal, with the named limits (GIT_CONFIG_*, ignore routes, lexical C2 read) stated. Statements agree with the writer bytes I grepped above.

Verdict C2: verifies. Reported values match exactly.

### No owned axis harmed

`git diff 4a43a4d9 f6358d2c -- SCORECARD.md` shows only additions: the Round-65 measurements table, the capabilities row (freeze chronology binding, selftest 52/52 receipt committed), the R65-ERRATUM-PREREG and R65-KILL-POWER dispositions. Owned score rows unchanged (calibration 7, coverage 8, operability 8 — no reproducible 0–10 mapping; numeric deltas 0, disclosed). Spot reads: LOG.md Round 65 entry present (line 2854); the honest-shape harm check holds — every probed honest row (A, B, T4, SY1, V2) still accepts at the measured revision.

## Per-axis verdicts (this closure, non-author)

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 verified: forgeries 12 → 0 on the frozen 19-row matrix, honest accepts 5/5 preserved, regress PASS; HIGH kill-power gaps (M11 symlink read-through, M12 mode masking) are named and open, not counted as improvement |
| calibration | improved | C2 verified: findings 2 → 0; SKILL statements corrected then qualified to measured scope (M9/M12); the `return`-token kill-power gap (M10) is named and open, not counted |
| coverage | unchanged | no claim moved coverage; SCORECARD row 8 unchanged; no coverage-map ground newly held (`corpus/README.md` unchanged) |

## Discernment spot-check (LEARNING.md — checked from outside)

Re-open performed by this closure judge, 2026-11-05: `curl https://git-scm.com/docs/git-config` → HTTP 200,
830605 bytes, sha256 `37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226` — byte-identical to
the committed capture `census/round-65/sources/s297-git-config.html`. Re-ran the committed tag-strip recipe
(`s297-tagstrip.py`) on the live bytes → sha256 `a692dbcb…` identical to the committed text capture. Slice
assertions re-run over UTF-8 byte offsets (not codepoint offsets — the first naive codepoint slice misses; the
committed `s297-located-quote.txt` offsets are byte offsets):

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| ADMIT S297 quote `no - Show no untracked files.` | admit | live git-config(1) page (git-scm.com), byte-identical to capture | agree | slice assertion PASS at byte offset 299360; 6 words ≤ 25; the sentence states exactly what the `no` value displays, grounding the V1 row |
| ADMIT S297 quote `all - Show also individual files in untracked directories.` | admit | same live page | agree | PASS at byte offset 299437; 9 words; grounds the V2 polarity and the `all` scope as measured |
| ADMIT S297 primary quote `So, this variable controls how the commands display the untracked files.` | admit | same live page | agree | PASS at byte offset 299266; 11 words; correctly recorded in the registry row as not byte-contiguous in raw HTML |
| REJECT "a receipt writer must override `status.showUntrackedFiles`" | reject | same live page | agree | the page contains zero occurrences of "receipt"/"writer" and assigns no duty to any consumer; the override is the lane's own design, and citing the page for it would be scope overreach |
| REJECT "`status.showUntrackedFiles=all` makes every untracked file visible" | reject | same live page | agree | the § status.showUntrackedFiles section never mentions ignored paths; `all` is scoped to "individual files in untracked directories"; the measured `core.excludesFile` arm (sentinel F1) shows ignored paths stay hidden — the page cannot support the general claim |
| REJECT (routed) `:(top)` code-kind registry row | reject (routed, not adopted) | n/a — operator L0 open | agree | routing, not adoption, is the right disposition while the operator L0 question is open |

Registry row re-opened: S297 (`corpus/SOURCES.md` line 256) — anchor (accessed 2026-11-05, HTTP 200, byte
count + sha256 prefix, capture paths), tier A/docs scoped to the untracked-visibility switch, `teaches`
grounded by the ≤25-word quotes verified above, `status: mined` with `used-by` = the knowledge entry. Quote
word counts 6/9/11 — within the ≤25-word limit. Knowledge entry `corpus/knowledge/untracked-visibility-concealment.md`
carries the provenance trio (`source: S297` + S291, `verified-at: af81553f…`, `recheck:` = the C1 command with
its expected SUMMARY line). S291 `used-by` change matches the lesson's old→new record exactly.
Census at closure: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0,
final line `ok …/corpus/SOURCES.md`; 220 rows (`grep -cE '^\|\s*S[0-9]{3,}\s*\|'` = 220, matching 219 → 220).
The validator's ~70 `W04 duplicate url … across scopes` lines are pre-existing warnings (rows share URLs at
different scopes, permitted by contract v1), not round-65 defects.

Gate-agreement outcome: the non-author spot-check agrees with the round gate on every sampled admit and
reject → per LEARNING.md the discernment `improved` condition is met this round.

## Trend verdicts (this closure)

- **expansion: unchanged.** One admitted knowledge entry citing the newly mined row S297 (`status: mined`, cited by `used-by`), but the ground is adjacent to F1/F4 which the coverage map already holds (`corpus/README.md` unchanged at `f6358d2c`); no new coverage-map ground, no frontier area entered, no new source kind. Matches the lane's own verdict.
- **quality: improved.** C1 forgeries 12 → 0 with 5/5 honest accepts preserved on the frozen matrix; C2 findings 2 → 0 with statements corrected and then qualified to measured scope; no admitted entry fails its bar at closure (census exit 0; the one erratum is a preregistration sentence, disclosed as R65-ERRATUM-PREREG with frozen bytes untouched). HIGH kill-power gaps are named and routed, not counted as improvement.
- **discernment: improved.** The lane held this at unchanged pending the closure spot-check; this spot-check (non-author) agrees with the gate on all sampled admits and rejects (table above). Additionally the five outside-check disagreements from the wave (M5/M7/M9/M10/M12) each became a mined lesson row, a narrowed QUALITY criterion (Q126/Q127), or a routed item — the "disagreement becomes a grounded criterion" condition is met in substance, verified against `corpus/lessons/round-65.md` `## Mistakes` and the SCORECARD corrections block.

## Routed defects the lane must fix next round (round 66)

Confirmed from the lane's own routing and this closure's reads; carried so they stay on the durable queue:

1. **F1 behaviour (HIGH):** `GIT_CONFIG_*` env passthrough and ignore routes (`core.excludesFile`, `.git/info/exclude`, tracked `.gitignore`) still defeat the dirty check for non-status keys. Writer docstring corrected at `af81553f` (wording); behaviour fix owed.
2. **M10 C2 kill-power (HIGH):** emission token `return` matches `returncode`; deleting the env refusal yields `findings=0`. Fix the emission token.
3. **M11 C1 kill-power (HIGH):** a same-content symlink retarget survives a read-through mutant; add the matrix row.
4. **M12 mode scope (HIGH):** permission bits only (`& 0o777`); setuid/setgid/sticky invisible. Q126 already narrowed; behaviour fix owed.
5. **MEDIUM routed:** N4 dual-seed fixture masks instrument-resolution behaviour; the TSV pin is not anti-launder; env-value echo in `RECEIPT-INDEX-ENV-SET` (sentinel F4); counter excerpt bound (F5).
6. **M8/Q59:** preregistrations still lack a MACHINE BLOCK (instrument refused the prereg gate; hand-judged axis) — operator L0 open.
7. **R65-ERRATUM-PREREG:** the frozen prereg's false chronology sentence stands corrected only by erratum; keep the prereg bytes frozen.

## Conformance defects (status-neutral, recorded in notes)

- Commit `6147f025`'s subject says "drop reviewer selftest temp residue from the wave mirror" but its diff only adds the receipts; the deletions actually landed in `f6358d2c`. Message/content mismatch, cosmetic; the report's landed-changes table describes the diffs correctly.
- SHONEN boxes are all `[~]` (asserted-by-author). This closure verified each box's evidence pointer resolves (SKILL.md round-65 writer-rule table + S297; LOG.md Round 65 entry + measured C1/C2 receipts; committed selftest receipts and `--selftest` modes on both counters; connector overlap scan in the wave mirror) — the boxes look fully checkable by a non-author; promotion is operator-owned, so this is a note for the operator, not a box mark.
- The dispatch log's launch and complete lines carry no report-filing timestamp between them beyond the watchdog's own; the report cites the final push check (`ls-remote` → `f6358d2c…`) consistent with the state check above.

## Closure ruling

Both claims verify (C1 and C2 evidence-verified with plain corroborating measurement; no axis harmed). Status
`ok`, admitted. Wave seats 9/9 settled with output (committed mirror); no dead seats; attack share 5/9 ≥ 25%.
