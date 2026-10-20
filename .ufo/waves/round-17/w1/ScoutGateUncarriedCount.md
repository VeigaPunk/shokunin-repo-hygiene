STATUS: DONE — 29 wave-2 gate markers were uncarried at `79bbe7a` (30 markers total, 1 pre-carried); `LOG.md:902`'s "28" is wrong; pre-harm fails 8 r15-config cases including 03 and 18.

# ScoutGateUncarriedCount — round 17 wave 1

Scope: D3 recount only, static. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `5fa6017`. I did not run `tools/souji-landing-gate.py` (not in the probe allow-list), did not edit LOG, and did not touch any file except this report.

## F1 — true uncarried count is 29 (lesson, closure and gate bytes agree; LOG's 28 fails)

Observed:

1. `corpus/lessons/round-16.md:58-86` holds **29** wave-2 carry bullets, one per line, each `- \`<report>.md:<line>\`` with a disposition. A wider `awk` over `:56-90` yields 30 because line 90 is the first *round-15* bullet (heading at `:88`), not a wave-2 bullet.
2. Each of the 29 named report lines was read at `79bbe7a` (`.ufo/waves/round-16/w2/<file>`, exact line number) and checked against the gate's pinned marker predicate: **29/29 are gate-channel markers** (STATUS prefix, first value word in `FAILURE_STATUS_WORDS`, outside fences, not a table row), e.g. `ConnQuality2.md:206 word=fail`, `MutateGateCarry.md:3 word=partial`. No bullet is a duplicate; all 29 `file:line` pairs are distinct.
3. A static mirror of the gate's carry rule (same `STATUS_PREFIX_RE`, `FAILURE_STATUS_WORDS`, fence toggle on `stripped.startswith("```")`, table-row skip, `norm_line` NFC/backtick/`*`-drop/whitespace-collapse, `CARRY_TOKEN_RE`) was validated against the committed artifact: at `6ff91f5` it reproduces `census/round-16/gate-landing.json` exactly — **141 reports, 30 markers, 0 uncarried**. Same model at `79bbe7a` gives **141 reports, 30 markers, 29 uncarried**. This is real model validation, not an assumption.
4. The 30th (already-carried) marker is identified: `.ufo/waves/round-16/w1/ConnLogConvention.md:385`, byte-exactly `    ## STATUS: INCOMPLETE — file has an unresolved syntax error`. It is outside every fence in that report (fence lines are `204 \`\`\`\`markdown`, `375 \`\`\`\``, `429 \`\`\``, `513 \`\`\``), so it counts; it was already carried at `79bbe7a` by `corpus/lessons/round-16.md:43` with `resolved@0a70bef`. Hence 30 − 1 = 29 uncarried, all wave-2. This closes the open point in `.ufo/waves/round-17/w1/ScribeLogCorrections.md` F1 ("the 30th marker is unidentified").
5. Closure agrees: `corpus/lessons/round-16-verifier-spotcheck.md:66` ("re-derived: 30 markers, 29 uncarried") and `:90` ("lesson :43-93: 12 + 29 + 4 = 45 lines"). Verified at `6ff91f5`: 45 `- \`` bullets, 12 w1 + 29 w2 + 4 r15.

Committed gate output under `census/round-16/` — directory has 9 files; the only gate artifact is `gate-landing.json`:

```json
{"error": null, "exit": 0, "findings": [], "resolved_base": null,
 "resolved_rev": "6ff91f534eece9adde5f667cb7dad400c145351b",
 "summary": {"checked_markers": 30, "checked_pins": 16, "checked_reg": 21,
             "checked_reports": 141, "findings": 0}}
```

It is the **post-carry landing run** (`resolved_rev` 6ff91f5, `findings` 0), not the `79bbe7a` pre-carry run; per D7 it lands at `c46eabf` and measures `6ff91f5` blobs. No committed `--json` exists for the `79bbe7a` run: `28`/`29`/`30` there rest on prose plus re-derivation (D6 gap, unchanged).

Verdict: **LOG.md:902 fails; the lesson and closure hold.** The true number is **29** uncarried wave-2 markers; "30" is the total marker count, not the flagged count. The two numbers are not interchangeable.

## F2 — pre-harm failure set: 8 of 20, including 03 (degrade) and 18 (preserve)

`census/round-16/c1-matrix-final.json`, `.arms["pre-harm"]` (`rev a31642d…`, `r15-config.rc 1`, `failed 8`), cases with `verdict != "PASS"`:

```
R15CFG-02, R15CFG-03, R15CFG-08, R15CFG-11, R15CFG-14, R15CFG-17, R15CFG-18, R15CFG-19
```

This matches `corpus/lessons/round-16.md:20` and the wave-2 LOG correction at `LOG.md:892-894`. Calibration note on the closure: `round-16-verifier-spotcheck.md:44`'s "Pre-harm fails 03 only" is scoped to the r14-closure repair predicate's three cases (03/04/16, stated in the same cell), not the 20-case suite; it does not contradict row `:41`. It should not be cited as a closure error.

## F3 — exact quotes and corrected wording (append-only)

`LOG.md:858-859` verbatim:

```
ShellCheck clean; r14-harm fails every HARM_CASES id; pre-harm fails only
refusal/safety cases; r15 baseline fails `bash -n` and all cases
```

`LOG.md:902-903` verbatim (line 902 is the sentence in question):

```
`fb23b12` (15/15 re-run). The landing gate flagged 28 uncarried wave-2
STATUS lines; they are carried in `corpus/lessons/round-16.md`. S044 and
```

Proposed append-only correction entry (exact text; earlier entries stand as written; consistent with, and safe to merge with, `ScribeLogCorrections.md`):

```
## 2026-10-20 — round 16 corrections to the C1 and wave-2 correction entries (appended; both stand as written)

Two sentences in the round-16 entries above are corrected here, from the
round-16 non-author closure (`corpus/lessons/round-16-verifier-spotcheck.md`,
routed defects D3) and a static re-derivation of the gate's carry rule at the
named revisions. No earlier text is edited.

`LOG.md:858-859` reads "pre-harm fails only refusal/safety cases". Corrected:
pre-harm `a31642d` fails eight r15-config cases — 02, 03, 08, 11, 14, 17, 18,
19 — of which 03 (per-repository degrade) and 18 (benign-config preservation)
are not refusal/safety cases (`census/round-16/c1-matrix-final.json`,
`.arms["pre-harm"]`); `corpus/lessons/round-16.md:20` and the wave-2
correction above at `LOG.md:892-894` already state this list.

`LOG.md:902` reads "The landing gate flagged 28 uncarried wave-2 STATUS
lines". Corrected: the gate flagged 29. At `79bbe7a` the report set
(`.ufo/waves/round-16/`, 141 reports) holds 30 gate-channel markers, of which
29 were uncarried and all 29 are carried at `corpus/lessons/round-16.md:58-86`
(bullets 58-86, one per line); the 30th, `.ufo/waves/round-16/w1/
ConnLogConvention.md:385`, was already carried at `corpus/lessons/round-16.md:43`
(`resolved@0a70bef`). The round-end committed run, `census/round-16/
gate-landing.json`, records the same 30 markers over 141 reports with 0
findings at `6ff91f5`. The figure 28 is withdrawn; 30 is the marker total,
not the uncarried count.
```

## Commands run (read-only) and outputs

| # | command | output |
|---|---|---|
| 1 | `awk 'NR>=896&&NR<=906{printf "%d|%s\n",NR,$0}' LOG.md` | `902|`fb23b12` (15/15 re-run). The landing gate flagged 28 uncarried wave-2` |
| 2 | `awk 'NR>=855&&NR<=862{...}' LOG.md` | `858|…pre-harm fails only` / `859|refusal/safety cases; r15 baseline fails \`bash -n\` and all cases` |
| 3 | `awk 'NR>=56&&NR<=90' corpus/lessons/round-16.md \| grep -c '^- \`'` | `30`; explaining line 90 = first round-15 bullet, so wave-2 (`58-86`) = **29** |
| 4 | `git show 79bbe7a:corpus/lessons/round-16.md \| awk '/^Round 16 wave 2/{f=1} f&&/^- `/{c++} END{print c}'` | empty (`w2bullets=`): no wave-2 carry existed at `79bbe7a` |
| 5 | per-bullet `git show 79bbe7a:.ufo/waves/round-16/w2/$f \| awk -v n=$ln 'NR==n'` + predicate | 29 `MARKER` lines, one per distinct `file:line`; 0 non-marker |
| 6 | same loop over wave-1 bullets (`43-54`) | 1 `MARKER`: `ConnLogConvention.md:385 word=incomplete`; the other 11 are non-vocabulary (`residual`, `survived`, `probe`, `f1`, `source`, quoted hash, `r16`, `probe`, `live`, `gate`, `skeleton`) |
| 7 | `git show 79bbe7a:.ufo/waves/round-16/w1/ConnLogConvention.md \| awk '/^[[:space:]]*```/{print NR}'` | fences at `204`, `375`, `429`, `513` → line 385 is outside any fence, inside prose |
| 8 | `git show 79bbe7a:…ConnLogConvention.md \| awk 'NR==385'` | `    ## STATUS: INCOMPLETE — file has an unresolved syntax error` |
| 9 | `git ls-tree -r --name-only 79bbe7a -- .ufo/waves/round-16 \| grep -c '\.md$'` | `141` |
| 10 | static mirror of the gate predicate over the 141 report blobs + lesson carry lines | `79bbe7a reports=141 markers=30 uncarried=29`; `6ff91f5 reports=141 markers=30 uncarried=0` |
| 11 | `read census/round-16/gate-landing.json` | exit 0, findings 0, `checked_markers` 30, `checked_reports` 141, `resolved_rev` 6ff91f5 |
| 12 | `git cat-file -t 79bbe7a` / `git log -1 --format='%H %ci %s' 79bbe7a` | `commit`; `79bbe7a62199260694943ec7186fef6ebff9d41a 2026-10-20 12:25:28 -0300 round-16: final wave-2 seat reports` |
| 13 | `python3` read of `census/round-16/c1-matrix-final.json` (`.arms[arm]["r15-config"].cases`, `verdict != PASS`) | pre-harm `rc 1 failed 8` → `02,03,08,11,14,17,18,19`; changed `rc 0 failed 0`; r14-harm `failed 16`; r15-baseline `failed 20` |

## Verdict and smallest fix

- Claim "gate flagged 29 uncarried at 79bbe7a": **holds** (independently re-derived; 29/29 lines verified in the report blobs).
- Claim "30 markers": **holds and is a different quantity** — total markers checked, one already carried at `79bbe7a`, 30 checked / 0 uncarried at `6ff91f5`.
- `LOG.md:902` "28": **fails** (off by one, undercount).
- `LOG.md:858-859` "pre-harm fails only refusal/safety cases": **fails** (8 failures; 03 degrade and 18 preserve are outside refusal/safety).
- Smallest fix: append the single correction entry in F3. Do not edit lines 858-859 or 902; do not restate "30 uncarried".

## Remaining unknowns / limits

- No committed `--json` output exists for the `79bbe7a` run; the 29 is a static re-derivation against the gate's pinned predicates, validated by an exact byte-level reproduction of `gate-landing.json` at `6ff91f5`. D6's ask (commit `--json` replays with expected verdicts) stays open.
- I did not execute `tools/souji-landing-gate.py`, the census, or any gate/selftest/fixture (no `ALLOWED-EXEC` item in this ticket); no harness output was regenerated.
- The four `MutateGate*`/`MutateSeatAudit` bullets are marker `PARTIAL` lines by vocabulary; their content dispositions are not re-judged here (D5/D6 territory).
- `corpus/lessons/round-16-verifier-spotcheck.md:44`'s "Pre-harm fails 03 only" is scoped to its three-case repair predicate; flagged above so it is not mistaken for a contradictory re-derivation. [INFERENCE on the scope: same-cell cases "03/04/16" and "all three FAIL (04 observed_exit=2)".]

## Tool installs/updates

None.

## Touched surfaces

This report only: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-17/w1/ScoutGateUncarriedCount.md`. No commits, no jj, no git writes, no other lane file written.
