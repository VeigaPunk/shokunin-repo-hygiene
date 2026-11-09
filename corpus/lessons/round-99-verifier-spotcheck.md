# Round 99 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)
Lane: souji-shokunin. Lane base `c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b`, lane tip at closure `5c47055e30e51f7ecf5ebe0ab7655b3bfd81fd37`.
Report: `.ufo/reports/round-99/souji.md`. Dispatch/complete digest (copied from the closure prompt):
`2026-11-09T11:00:33-03:00 launch souji round=99 pgid=3231865 driver=hyaku-inline attempt=1`;
`2026-11-09T12:15:12-03:00 complete souji round=99; hyaku-inline attempt=1`.

## Conformance (step 1)

- Report committed in the fleet repo by the lane identity: `git log --format='%an %H' -- .ufo/reports/round-99/souji.md` → `souji-shokunin 8e6d857c36b1d571d6d872936e934f1178ae1368 round-99: souji report`. OK.
- `SHONEN` heading present exactly once (`grep -c '^## SHONEN'` = 1, line 83), one line per box (4 × `[~]` with pointers). OK.
- Cited lane commits exist and are ancestors of `master` (`git -C souji-shokunin merge-base --is-ancestor <hash> master`): base `c94d678…` OK, tip `5c47055…` OK; intermediate `d31c07d6`, `183dd640`, `118e5b7d`, `d54b6c1c` listed in the report all present in `c94d678..5c47055` log. OK.
- Lane clean and pushed before spot-check: `jj-lane.sh state` → `ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git -C souji-shokunin status --porcelain` empty; `git ls-remote origin refs/heads/master` = `5c47055e30e51f7ecf5ebe0ab7655b3bfd81fd37` = local tip. OK.
- Prompt carries the template contract (§1 mission/axes, §2 claims, §2b frontier, §3 L2 floor, §4 report contract, §5 commit/push/L0, §6 hyaku addendum). OK.
- Not a marker: the report names real committed work, per-claim evidence pointers, and a checkable lane hash. Status-neutral defects only (below).

## Per-claim re-checks (step 2)

### C1 — calibration 7: shape labels pinned to a frozen file

Re-measured by the verifier against committed bytes (`5c47055…`) with plain commands:

```
sha256sum census/round-99/shapes.tsv
→ 8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14  (matches pinned hash; 18 lines = 1 header + 17 rows)
```

M1 (pinned file, r98 hook):
```
python3 -B census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv \
  --expect-sha256 8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14 \
  --search census/round-98/c1-survivor-search.py --scripts census/round-98/shapes --work /fast/scratch/hyaku/r99-closure/w1
→ SHAPES-SUMMARY shapes=17 mismatched=0, EXIT 0 (identical to committed records/c1-r99.txt M1)
```

M2 (relabelled copy, pin enforced): relabelling q1o/q1q → declared, q1i → crash with the original pin → `SHAPES-FATAL: freeze sha256 004356d7… != pinned 8bc642c4…`, EXIT 2. Verifier's relabel hash `004356d76d94c54158232f250077c6995b5103b16f34ef4111e4933bc6cc330a` matches the committed M2 receipt. Matches.

M3 (same relabelled copy pinned to its own hash): `SHAPES-SUMMARY shapes=17 mismatched=3` (q1o, q1q, q1i named), EXIT 1. Matches committed M3.

Controls on the pinned file: r95 hook `mismatched=3` (t1, t4, q1i), r97 hook `mismatched=3` (q1o, q1q, q1i), both EXIT 1. Verifier re-ran both: identical. Matches.

Population no-harm (evidence-verified, not re-executed): `census/round-99/c1-survivor-search.py` is byte-identical to the r98 search (`sha256 e8ba780a5b8d807ff199c33a679d7d8dd7259fb93e934d123b009e9f9f2649e1` both files, verified by the verifier). The 278-mutant verdicts are unchanged by construction; the population run is the `R99ExecCensus` seat report cited in the wave evidence.

Gate consideration: C1's witness is L1-measured with committed receipts, not a lane-owned gate verdict, so no gate-evidence rule binds it; the verifier re-ran the measurement directly. The post-scoring pin amendment A99.1 (filed after seats scored, disclosed in plan and lesson) is the mechanism that answers reviewer R99Reviewer1's duplicate/missing-row attack (`shapes=18`/`shapes=16` reaching a clean count on the unpinned runner). The verifier confirmed the amended runner refuses both wrong row counts (17 distinct names checked, rc 2 on mismatch — see declared-shapes.py; M2 demonstrates the refusal path).

**C1 verdict: improved (verifies).** Before: r98 hard-coded labels, relabelling reached `mismatched=0` (movable count). After: pinned file refuses the relabel (EXIT 2) and the unpinned count moves to 3. Do-nothing controls stay red.

### C2 — operability 8: spawn-chain-only reap

Re-derived from committed bytes (no live re-execution of the arms counter; the destructive live-run is evidence-verified):

- Code: r99 `_reap_owned` (`census/round-99/c2-setup-arms.py:164-200`) kills only (a) the spawn pid starttime-verified or (b) ppid-chain descendants of the spawn pid. Branch (c) — `elif _is_descendant(pid, os.getpid())` in r98 (`census/round-98/c2-setup-arms.py:189`) — is absent in r99. Verified by grep on both committed files.
- Decoy receipts (committed): r99 `verdict=spared`, dead 0 / alive 83; r98 `verdict=spared`, 0/83; r97 `verdict=killed`, 60/23; CM8 `verdict=killed`, 82/1. Verifier grepped all four committed receipts: values match the report.
- Escapee receipts (committed): `census/round-99/records/c2-escapee-r99.txt` — r99 `ESCAPEE-ALIVE alive=1`, r98 `alive=0`, r97 `alive=0`. Verifier read the file: values match the report. The superseded `c2-counter-*.txt` lines are correctly disclaimed via `c2-escapee-NOTE.txt` (M12 doubled-path bug).
- Cross-arm claim rests on a seat run (`R99ExecC2b`), not a committed L1 receipt; MutC2's pristine 30/30 spare is cited instead. Not independently re-executed (evidence-verified).

No axis harm beyond C2's own: `git diff c94d678… 5c47055… -- SCORECARD.md` shows only the round-99 measurement rows; no owned score moved (calibration 7, operability 8, coverage 8 unchanged, legacy-unmapped numeric rows); coverage untouched (no registry row added/changed — `corpus/SOURCES.md` diff empty).

**C2 verdict: harmed (self-reported by the lane, confirmed by re-derivation).** The decoy spare adds no discrimination over r98 (already spared); the only new effect is the escapee leak (`alive=1` vs r98 `alive=0`). An axis trade is not an improvement; C2 does not verify.

### Prefile falsification ledger (step 2b)

`python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 99` → `PREFILE-FALSIFICATION: pass claims=2 rows=11 attack_seats=7 findings=0`, exit 0. Ledger `claims.json` covers both claims; all 7 attack seats (reviewer ×2, critic, mutation-tester ×2, sentinel, connector) appear; every `falsifies-wording` row names a narrowing (A99.1 for C1's unpinned-runner rows; A99.2 for C2's escapee rows). The C1 falsifies-wording rows are reconciled by the A99.1 pin (verified above); the C2 rows are reconciled by the lane's own harmed verdict (the narrowing records the harm, it does not hide it). No unreconciled failing row. PASS.

## Discernment spot-check (step 3, LEARNING.md)

From `corpus/lessons/round-99.md` `## Gate`: sampled the C1 admit and the C2 reject.

| item | lane decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| C1 freeze-file binding (admit) | admitted-candidate; pinned file refuses the relabel attack | `census/round-99/shapes.tsv` (sha256 `8bc642c4…`) + M2/M3 re-run by verifier (above) | **agree** | The pin converts a movable count into a refused attack: M2 EXIT 2 on the relabelled copy, M3 `mismatched=3` without the pin, controls red. The admit rests on a re-runnable measurement, not on the sentence. |
| C2 spawn-chain reap (reject) | harmed (trade); not admitted | `census/round-99/records/c2-escapee-r99.txt` (`alive=1` vs r98 `alive=0`) + r98/r99 `_reap_owned` diff; seat `R99ScoutSources` FINDING 1 (no-op mutant byte-identical arm output) | **agree** | The decoy leg is a wash against r98 and the escapee leg is a measured regression; no honest reading admits it. The lane's self-reported harm matches the committed bytes. |
| S372 quote `\u201cAn exception is re-raised, for example at the end of a finally block.\u201d` (≤25-word quote, re-opened) | row re-verified, no registry row written | Live fetch `https://docs.python.org/3/library/sys.monitoring.html` (verifier, HTTP 200) vs committed capture `census/round-97/srcs/monitoring.html`: byte-identical; quote occurs exactly once in the normalized text of the capture | **agree** | Quote located and counted; the byte quote only appears split across HTML tags in the raw bytes, so the checkable form is the normalized text, which the verifier confirms. |
| S075/S368 quotes | re-verified live, byte-identical to committed captures | Seat `R99ScoutSources` §3 fetch table (live sha256 vs capture sha256) | **agree** | Both live fetches byte-identical to committed captures; the verifier spot-confirmed the S075 capture path. |

Registry: no `corpus/SOURCES.md` row added or touched this round (294 → 294, `grep -c` verified; diff empty). Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0 (`ok …corpus/SOURCES.md`; W04 duplicate-URL warnings are pre-existing and scoped).

## Per-axis verdicts

| axis | verdict |
|---|---|
| calibration | improved |
| operability | harmed |
| coverage | unchanged |

## Trend verdicts (with evidence)

- **expansion: unchanged.** No knowledge entry admitted on new ground; no registry row (294 → 294 verified). The frontier work (F5 escapee) is measurement, not an entry.
- **quality: improved.** C1 turns the calibration input into a pinned, refusal-enforcing file (M2 EXIT 2) — a weaker movable count superseded by a stronger binding, with the C2 regression recorded as a harm rather than hidden. No admitted entry fails its re-check.
- **discernment: harmed.** Two faults the pre-freeze gate missed and attack seats caught: the unpinned freeze hash (M9, Reviewer1) and the spawn-chain escapee assumption (M10, Sentinel/Reviewer2/MutC2). The lane's own verdict agrees; the learning is recorded (M9 fix shown able to fail; M10 routed to r100), but the in-round catch still required attack seats, which is the harmed grade. The verifier agrees with both gate decisions (admit C1, reject C2), so the disagreement history is grounded, not left unlearned.

## Routed defects (lane must fix next round; status-neutral)

1. **C2 escapee successor (r100, operability):** an ownership key that is not the ppid chain (candidate: fixture session id recorded at spawn, starttime-verified), with a positive escapee-reap predicate (`ESCAPEE-ALIVE alive=0`; r99 `alive=1` is the do-nothing). The `m_noppid` mutant must FAIL it. Carried in SCORECARD `Planned (r100)`.
2. **Stale source attribution (from seat R99ScoutSources FINDING 3):** `census/round-99/c2-setup-arms.py` docstrings (lines 96, 128, 330) and `corpus/knowledge/deadline-owned-reaping.md` still attribute the field-4 ppid wording to S075, which the r98 lesson withdrew (S332 is the kernel emission-order attribution). Also S075's `used-by` does not list `deadline-owned-reaping.md` (FINDING 4). Correct by new entry/row, never in-place rewrite.
3. **Sentinel FINDINGS 2–5 (carried):** escapee holds fixture pipes after counter exit; `_reap_by_identity` dead with stale docstring; the /tmp guard is prefix-only (r97 carry).
4. **M11 quiet-host gate:** cross-arm runs need a quiet-host rule so a concurrent decoy storm cannot confound them (not shown able to fail as a frozen rule).

## Conformance defects (status-neutral)

- None material. The report's `Sources & frontier` section records the census before→after with the counting command and exit codes (before 294, after 294, census `ok`); verified here. The plan misroot (M13) was repaired in-round and committed (`118e5b7d`); the fleet-root copy was deleted.
