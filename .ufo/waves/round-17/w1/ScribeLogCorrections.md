STATUS: DONE — two append-only LOG correction drafts written and checked against committed bytes; LOG.md not edited.

# ScribeLogCorrections — round 17 wave 1

Scope: draft (report only) two append-only correction entries for `LOG.md`, named after the round-16 non-author closure `corpus/lessons/round-16-verifier-spotcheck.md`, routed defect D3. No product file, no LOG edit, no commit, no jj, no git write, no gate or census run.

## Findings

### F1 — LOG.md:902 says "28" uncarried; the count is 29 (confirmed)

- `LOG.md:902`: "The landing gate flagged 28 uncarried wave-2 STATUS lines; they are carried in `corpus/lessons/round-16.md`."
- `corpus/lessons/round-16.md:56-86`: the wave-2 carry list has 29 bullets (lines 58-86 inclusive, one bullet per line, each `- \`<report>.md:<line>\``). Each is "quoted verbatim" and carries a disposition.
- The closure re-derived `79bbe7a` as 30 markers, 29 uncarried (`round-16-verifier-spotcheck.md` table row "`79bbe7a` → 29 uncarried"; routed D3 item 3).
- Corroboration: `census/round-16/gate-landing.json` (at `6ff91f5`) records `checked_markers: 30`, `findings: 0`.
- Commit `79bbe7a62199260694943ec7186fef6ebff9d41a` ("round-16: final wave-2 seat reports") exists (`git log -1`, `git cat-file -t` → commit).
- Open detail: the closure says 30 markers but 29 uncarried, so one marker was not uncarried at `79bbe7a`. I did not identify that marker; I did not run the gate (not in the probe allow-list). Left as an open point for the L1 integrator.

### F2 — LOG.md:858-859 says "pre-harm fails only refusal/safety cases"; it also fails R15CFG-03 and R15CFG-18 (confirmed)

- `LOG.md:858-859`: "r14-harm fails every HARM_CASES id; pre-harm fails only refusal/safety cases".
- `census/round-16/c1-matrix-final.json`, `.arms["pre-harm"]["r15-config"].cases` filtered to `verdict != PASS`: `R15CFG-02, R15CFG-03, R15CFG-08, R15CFG-11, R15CFG-14, R15CFG-17, R15CFG-18, R15CFG-19` (8 of 20; `failed: 8`).
- R15CFG-03 detail: `r-inc-cycle: finding config-unsupported missing from stderr` and similar, i.e. the per-repo degrade class.
- R15CFG-18 detail: `a-benign`, `m-safe-config`, `z-benign` each `worktrees=0 want 1`, `verdict_flags=error want clean`, i.e. the benign-preservation class.
- R15CFG-14 detail: filter-driver case (`verdict_flags=dirty,unpushed want unpushed,status-unverifiable`); I read this as a safety case [INFERENCE: its oracle is "driver must not run / status-unverifiable"], so the "refusal/safety" label still covers it. 03 and 18 are the exceptions.
- `corpus/lessons/round-16.md:20` states the correct list: "pre-harm (`a31642d`) fails 02, 03, 08, 11, 14, 17, 18, 19 — refusal/safety cases plus 03 (degrade) and 18 (preserve …)".
- The LOG already carries the correct statement at `LOG.md:892-894` (wave-2 corrections: "pre-harm fails 02, 03, 08, 11, 14, 17, 18, 19 — refusal/safety plus 03 (degrade) and 18 (preserve), not 'only refusal/safety'"). So entry 2 is a same-sentence cross-correction to the original line, not new information.
- Warning against the closure: `round-16-verifier-spotcheck.md:44` says "Pre-harm fails 03 only". That contradicts the same file's line 41 and the matrix above. Do not cite line 44.

## Draft LOG entries (append-only; paste at the end of LOG.md, after the wave-2 corrections block)

```
## 2026-10-20 — round 16 correction: the uncarried wave-2 count is 29, not 28

Correction to "The landing gate flagged 28 uncarried wave-2 STATUS lines" (LOG.md:902, round-16 wave-2 corrections above; that entry stands as written). Found by the round-16 non-author closure, `corpus/lessons/round-16-verifier-spotcheck.md` (routed defect D3, item 3; its table row "`79bbe7a` → 29 uncarried"). Re-derived at `79bbe7a` (`round-16: final wave-2 seat reports`): 30 gate markers, 29 uncarried. The carry list `corpus/lessons/round-16.md:58-86` holds 29 wave-2 bullets, one per uncarried line. The 30-marker count matches `census/round-16/gate-landing.json` (`checked_markers` 30, `findings` 0, at `6ff91f5`). The figure 28 is withdrawn.

## 2026-10-20 — round 16 correction: pre-harm fails R15CFG-03 and R15CFG-18, not only refusal/safety cases

Correction to "pre-harm fails only refusal/safety cases" (LOG.md:858-859, round-16 C1 entry above; the wave-2 corrections at LOG.md:892-894 already state the right list). Found by the round-16 non-author closure, `corpus/lessons/round-16-verifier-spotcheck.md` (routed defect D3, item 3). Pre-harm `a31642d` fails eight r15-config cases: 02, 03, 08, 11, 14, 17, 18, 19 (`census/round-16/c1-matrix-final.json`, `.arms["pre-harm"]["r15-config"]`). R15CFG-03 is the per-repository degrade class and R15CFG-18 is benign-config preservation; neither is refusal/safety. This matches `corpus/lessons/round-16.md:20`.
```

## Checks run (all read-only)

| # | command / read | result |
|---|---|---|
| 1 | read `LOG.md:810-906` | correction style (dated `## 2026-10-20 — round 16 …` headings, prose), 858-859 and 902 confirmed verbatim |
| 2 | read `corpus/lessons/round-16-verifier-spotcheck.md` (full) | D3 names LOG:902 and LOG:858-859; table row "79bbe7a → 29 uncarried"; line 44 says "Pre-harm fails 03 only" (contradicted by line 41) |
| 3 | read `corpus/lessons/round-16.md:1-93` | line 20 pre-harm list correct; wave-2 carry list = 29 bullets at 58-86 |
| 4 | read `census/round-16/gate-landing.json` | `checked_markers` 30, `findings` 0, `resolved_rev` 6ff91f5 |
| 5 | `git -C …/souji-shokunin log -1 79bbe7a`; `cat-file -t 79bbe7a` | `79bbe7a62199… round-16: final wave-2 seat reports`; `commit` |
| 6 | jq queries on `census/round-16/c1-matrix-final.json` (`.arms|keys`; `["pre-harm"]["r15-config"]` keys; failing `verdict != PASS` ids; details of 03/14/18) | 8 failing ids as listed in F2 |
| 7 | grep `uncarried|only refusal|fails only` in `LOG.md` | hits at 858, 902 (the two lines to correct); no existing "29 uncarried" |

## Not verified / limits

- Did not run `tools/souji-landing-gate.py` (not on the probe allow-list); the 30-markers / 29-uncarried figures rest on the closure's re-derivation plus `gate-landing.json` at `6ff91f5`. The 30th marker is unidentified (see F1).
- `.ufo/reports/round-16/souji.md` is not at the lane root (read returned not found); the closure's "report:45" pointer was not checked.
- Did not open `census/operator-sweep-20261019/` (operator-owned).
- Closure's "pre-harm fails 03 only" (`round-16-verifier-spotcheck.md:44`) is an error in the closure itself; the draft does not cite it.

## Tool installs/updates

None.

## Touched surfaces

This report only: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-17/w1/ScribeLogCorrections.md`. No other file was written.
