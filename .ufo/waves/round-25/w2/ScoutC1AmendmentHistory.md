# ScoutC1AmendmentHistory — C1 amendment-vs-scoring chronology audit (W2, round 25)

Seat: L1Souji25.ScoutC1AmendmentHistory (scout, read-only). Lane HEAD `6deb53561aace9aa14a399f88cf8150da4d4f4bd` (amendment 3). Read-only: no lane edits, no git mutations, no scratch writes (no scratch dir needed — nothing was created; removed policy: `/var/tmp/souji-r25-ScoutC1AmendmentHistory/` was never created because no writes were required).

STATUS: PASS

## 1. The question

Does amendment 3 (k5–k7, commit `6deb535`) precede any seat scoring of the C1 fixture? If a seat scored the fixture before the rule changed, the no-rule-change-after-scoring clause would force C1 `unprovable`.

## 2. Exact timeline (all times 2026-10-25, America/Sao_Paulo = UTC−3; Z = UTC)

| Time | Event | Evidence |
|---|---|---|
| 07:07:19 | Round-24 base commit `a6d2d15` (committer stamp) | `git log` |
| 09:24:42 | **Freeze** commit `6e4737e` — `preregistration.txt` + 5 base-control receipts. C1 after-target literal `kill_tested=4`; case target unpinned (`cases=C`) | commit stamp; file mtime 09:24 |
| 09:25:52 | `w1-spec.json` written | mtime |
| 09:26:01 | **Wave 1 dispatched** (`w1-dispatch.json`). ExecC1 prompt pins C1 fixture target: "must print `cases=13 pass=13 …` (or whatever C=13 counts you freeze)" | mtime; dispatch task text |
| 09:29:57 | **Amendment 1** commit `1814de5` (corrects C1 after-target literal to `kill_tested=6 kill_violations=0`; regenerates 5 base receipts). Claim in text: "written before any seat scored — ExecC1-2 and ScoutC2Probe-2 both pre-score" | commit stamp; amendment-1.txt |
| 09:31:47 | **Amendment 2** commit `de736c2` (C2 red-arm blobs; C3 sourcing S124–S126; no C1 change) | commit stamp |
| 09:32:01 | `ScoutPreregAudit.md` written (audit only; flags the 6e4737e receipt anomalies; no C1 fixture run) | mtime |
| 09:32:09 | `ScoutC1KillRule.md` written — ran a *prototype* tool against (a) committed r24 fixture (9/9) and (b) its own 8-case scout harness (k1–k4 + extras k1b/k5/k6/k7). Findings A2/A3/A4 = the attack sources that amendment 3 incorporated. **Not** a run of the C1 r25 fixture (none existed) | report content; mtime |
| 09:33:05 | `ScoutC3Structure-2.md` written (C3; not C1) | mtime |
| 09:34:20 | **Amendment 3** commit `6deb535` — adds C1 k5/k6/k7, pins target `cases=16 pass=16`; regenerates 5 base receipts; C3 red-arms/oracles. Claim in text: "written before any claim was measured; pre-score attack adjudications from ScoutC1KillRule-2, ScoutC3Structure-2 and ScoutPreregAudit-2" | commit stamp; amendment-3.txt; file mtime 09:34 |
| 09:38:08 | Earliest surviving C1 r25 fixture artifact: `w1/r25-coverage-agreement.py` (16 cases incl. k7 veto-less control; sha256 `2a65d8c0…`) | mtime; sha256sum |
| 09:39:16–17 | ExecC1 receipts written — headers `rev=6deb535`, `utc=2026-10-25T12:39:17Z`; green arm `cases=16 pass=16 control=FALSE-GREEN-REJECTED`; red arm `cases=16 pass=9`; real runs `kill_tested=6 kill_violations=0` | receipt headers; mtimes |
| 09:39:25 | `ExecC1.md` written (states fixture implements k5–k7 per amendment 3) | mtime |
| 09:43:40 | `MutCoverageAgreement.md` — 14 mutants scored vs the 16-case fixture | mtime |
| 09:47:41 | `MutCoverageAgreement-2.md` — 37 mutants vs the 16-case fixture | mtime |
| 10:00–10:02 | Wave-1 `assignments.json` / `swarm-registry.json` finalized | mtimes |
| 10:05:37–48 | `w2-spec.json` / `w2-dispatch.json` written; wave 2 dispatch | mtimes |

No other W1 seat report references a run of the C1 r25 fixture (checked all `w1/*.md`; `RevC1` produced no report; the only `15-case` mentions in the wave are the unrelated R17 record-agreement fixture). C1 after/red receipts are only the uncommitted ExecC1 set above; `census/round-25/records/` holds only the five base controls (confirmed by ScoutC1Receipts, W2).

## 3. Did a 15-case C1 fixture ever exist?

**No.** No committed or draft version of the r25 fixture has 15 cases:
- Pre-amendment-3 target: `13` (9 r24 + k1–k4; k0 control separate) — pinned in the wave-1 ExecC1 prompt; ScoutC1KillRule A5 notes the after-target was unpinned `cases=C`, "r24's 9 + k1–k4 = 13".
- Post-amendment-3 target and artifact: `16` (9 r24 + k1–k6 + k7 control) — amendment 3 text; all three W1 fixture-scoring reports (ExecC1, Mut#1, Mut#2) and all receipts show `cases=16`.
- `git log -S'cases=15' --all` across the repo: zero hits. Grep of the working tree: no `cases=15` in C1 context.
- The "15-case C1 fixture" in the task statement matches no artifact; if it denotes 9 + k1..k6 excluding the k7 control, that state likewise never existed as a separate artifact — the draft added k1–k7 atomically (first artifact 09:38:08).

## 4. Verdict: amendment 3 preceded every C1 fixture scoring

- Amendment 3 committed at **09:34:20** (6deb535).
- The earliest C1 fixture scoring artifact is ExecC1's **09:39:16** receipts (headers pin `rev=6deb535`), followed by 09:39:25 (ExecC1.md), 09:43:40 and 09:47:41 (mutation testers). All post-date amendment 3.
- The only pre-09:34:20 "scoring"-adjacent work is ScoutC1KillRule-2's prototype runs, which targeted the committed r24 fixture (9/9) and its own ad-hoc 8-case harness — not the C1 r25 fixture (which did not exist). Those runs are precisely what amendment 3 adjudicated and absorbed.
- The amendments' own claims hold: amendment 1 "written before any seat scored" (first fixture scoring 09:39+), amendment 3 "written before any claim was measured" (first measurement 09:39:17).

**Conclusion: C1 is NOT rendered `unprovable` by the no-rule-change-after-scoring clause on chronology grounds.** Amendment 3 only *added* cases k5–k7 (stricter) before the fixture existed or was scored; it dropped/re-specified no frozen case. The kill rule "no case is dropped/re-specified after any seat has scored" is satisfied.

## 5. C1 claims and case targets before/after each amendment

**C1 claim (unchanged through all amendments):** calibration (7, lowest non-retired) — kill-rule tool row. Tool CLI (frozen): `python3 -B tools/souji-coverage-agreement.py --root <lane> --rev <full40> [--base-rev <full40>]`; with `--base-rev`, read base knowledge tree, require every `ground: F<k>` front-matter entry to still exist at `--rev` with the same F<k>; violations print `MISMATCH\tKILL-RULE\tcorpus/knowledge/<name>\t<detail>`; counts line gains `kill_tested=N kill_violations=V`; exit 0 iff mismatches==0 AND kill_violations==0. Kill rule: any KILL-RULE violation or mismatches>0 at tip → C1 not verified; **no case dropped/re-specified after any seat has scored**. Before (do-nothing control): current tool at base rejects `--base-rev` (rc 2; `c1-control-base.tsv`). Red-arm: OLD tool blob run against the extended fixture must fail k1–k4; receipt committed before any after-data.

| State | C1 fixture case set | Target line |
|---|---|---|
| Frozen (`preregistration.txt` @ 6e4737e, 09:24:42) | r24 fixture (9 cases) + k1 deleted, k2 regrounded, k3 clean, k4 multi + k0 always-zero control | `cases=C pass=C control=FALSE-GREEN-REJECTED` (C unpinned; wave-1 prompt pins 13); after-run literal `kill_tested=4 kill_violations=0` (fact error) |
| After amendment 1 (1814de5, 09:29:57) | unchanged | literal corrected to `kill_tested=6 kill_violations=0` (6 base-grounded entries: 4×F2 + 2×F4); separability note "stays 4"→6; no predicate/case/kill-rule change |
| After amendment 2 (de736c2, 09:31:47) | unchanged (amendment is C2/C3-only) | unchanged |
| After amendment 3 (6deb535, 09:34:20) | + k5 partial-removal (base F2+F3 → tip F2 only ⇒ one KILL-RULE row, rc 1), k6 extra-ground-allowed (base F2 → tip F2+F4, both map rows list E ⇒ rc 0, kill_violations=0), k7 veto-less-tool control (accepts `--base-rev`, prints `kill_tested=N kill_violations=0` without checking ⇒ must FAIL k1/k2). Definitions pinned: kill_tested counts base-grounded entries; kill_violations counts entries with ≥1 violation (not per-line); `--base-rev` refuses non-full-40-hex | `cases=16 pass=16 (r24's nine + k1..k6 + k7 control), control=FALSE-GREEN-REJECTED`; r24 nine + k1..k4 remain frozen; "no frozen predicate, target, kill rule or r24 case changes — only adds cases, red arms and oracles" |

`preregistration.txt` itself is byte-unchanged across the amendments (`git diff 6e4737e 6deb535` on it is empty; only the amendment files and base receipts were added/replaced). Amendment commits are append-only, monotonic (author=committer of predecessor, committer=wall clock matching file mtimes; no backdating).

## 6. Findings

1. Amendment 3 (`6deb535`, 09:34:20) preceded *every* seat scoring of the C1 r25 fixture (earliest scoring artifact 09:39:16, receipt headers `rev=6deb535`). The no-rule-change-after-scoring clause is not violated; C1 need not be `unprovable` on chronology grounds. `[OBSERVED]`
2. The "15-case C1 fixture" exists in no artifact: pre-amendment-3 target was 13; post-amendment-3 target/artifact is 16. The phrase is best read as a mis-count (or as 9 + k1..k6 excluding the k7 control, which also never existed as a separate artifact). `[OBSERVED]`
3. The only pre-amendment-3 C1-touching "scoring" was ScoutC1KillRule-2's prototype runs (r24 fixture 9/9; own 8-case scout harness) — not the C1 fixture. Amendment 3's text explicitly credits those pre-score adjudications. `[OBSERVED]`
4. Amendment 1's and 3's own "written before any seat scored / any claim was measured" claims are true against artifact evidence (earliest fixture scoring 09:39+). `[OBSERVED]`
5. Process wrinkles (not rule changes, reported for completeness): (a) amendments 1 and 3 replaced the five committed base-control receipts *after* wave-1 dispatch (09:26:01); the 6e4737e receipts had impossible `utc` stamps predating their bound rev (ScoutPreregAudit finding 4) — amendment 3 §5 discloses only the c1 refusal-receipt status; (b) ExecC1's prose says "current HEAD de736c2" while its own receipts pin `rev=6deb535` — the receipt header governs: measurement happened after amendment 3. `[OBSERVED]`
6. `[INFERENCE]` No rejected-predicate or narrowed-target attack is found: amendment 3 enlarged the case set before any scoring, a stricter (not narrower) contract.

## 7. Attack log

- ATTACK (chronology): "did amendment 3 land after a seat scored a 15-case fixture?" → FALSIFIED: no 15-case fixture exists in any artifact; all fixture scoring (09:39+) postdates amendment 3 (09:34:20).
- ATTACK (receipt integrity): receipt headers (`rev=6deb535`, `utc=12:39:17Z`) independently confirm post-amendment-3 execution, so uncommitted draft mtimes are not the only evidence.
- No production writes; no lane/git mutations; no tools installed; no scratch used.

## 8. Remaining unknowns

- Whether an earlier (pre-09:38) draft of the r25 fixture with 13 or 15 cases existed and was overwritten: no evidence either way; uncommitted drafts leave no audit trail. It would not change the verdict: any such state was still *targeted at 13 and never scored* (no receipts/reports reference it).
- RevC1 (assigned to falsify C1 at frozen bytes) produced no report; its absence does not affect the chronology (it would be a falsifier, not a scorer).
