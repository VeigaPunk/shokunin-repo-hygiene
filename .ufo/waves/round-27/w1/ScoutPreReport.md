# ScoutPreReport — failure modes the C3 pre-report gate must catch (souji r27, w1)

Seat: `ScoutPreReport` (scout, read-only, leaf — no subagent dispatch). Lane base `e78ac7c4837b81b634db4a927605a751a7f006ba`, branch `master`, `ahead=0`, remote verified `e78ac7c`. No lane edits, no git/jj mutation, no tool installed. Scratch `/var/tmp/souji-r27-ScoutPreReport` created and removed (see §Cleanup). All checks below were executed this run against the live lane/fleet, read-only.

## Status

STATUS: PASS — the five prereg-named checks are enumerated below with a shell/pipeline, the failure mode each prevents, and the three named incident sources mapped to them; three additional source-derived checks are flagged as stricter-only amendment candidates for the L1 (not applied by me).

## Evidence

- E1 — `grep -n 'lane-dead-no-report souji round=27' /home/vgpnk/Projects/shokunin/.ufo/watchdog.log` → `1377:2026-10-25T14:46:45-03:00 lane-dead-no-report souji round=27; retry same round (hyaku-inline attempt=1: L1 misread inline-spawn handoff`. Neighbouring lines: `1376` = `launch souji round=27 pgid=1728588 driver=hyaku-inline attempt=1`; `1378` = `launch souji round=27 pgid=1952211 driver=hyaku-inline attempt=2`.
- E2 — `sed -n '60p' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-26-verifier-spotcheck.md` → "Trailing wave-seat outputs under `.ufo/waves/round-26/w1/` were still being written past driver completion and remain uncommitted in the lane repo". Same file `:13` records the leftovers as "8 modified + 10 untracked, mtimes 14:36–14:39:37, past driver complete 14:39:08".
- E3 — `sed -n '19p' …/corpus/lessons/round-25.md` → "The first 32-seat batch yielded two duplicate reports (`ScoutGateCensus`, `ScoutToolSHA256Counter`) and 30 seats were cancelled"; `:55` row R25-M2 → "L1 issued the same 32-seat W1 taskCall twice; the duplicate batch created two duplicate completed reports and 30 canceled seat identities".
- E4 — live `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | wc -l` → **40** dirty paths at base: 36 under `.ufo/waves/round-26/w1`, 1 `tools/__pycache__/`, 1 `tests/fixtures/__pycache__`, 1 `census/operator-sweep-20261019/`, 1 `.ufo/waves/round-27/`. `git ls-tree -r --name-only HEAD .ufo/waves/round-26/w1/ | wc -l` → 90 tracked; on-disk → 115; `find .ufo/waves/round-26/w1 -newer <14:39:08> -type f | wc -l` → **115** (every wave file post-dates driver complete).
- E5 — live check results at base: tip `local=e78ac7c… == remote=e78ac7c…` → PASS; report path `/home/vgpnk/Projects/shokunin/.ufo/reports/round-27/souji.md` → **absent** (`ls .ufo/reports/round-27/` shows no `souji.md`); `grep -c '^## SHONEN'` on the r26 report → `1`; `wc -c` r26 report → 8656; prereg `.ufo/waves/round-27/preregistration.txt` → present, 3752 bytes, `MACHINE BLOCK` + 3 `CLAIM` lines.
- E6 — pipeline traps verified in scratch: `git rev-parse refs/heads/master` on a missing branch exits **128 but prints `refs/heads/master` on stdout**; `git rev-parse --verify refs/heads/master` exits 128 and prints **nothing**. `grep -c` on no-match exits **1** and prints `0`. `grep -c '^## SHONEN'` matches `## SHONEN.md` (count 1); `grep -cE '^## SHONEN[[:space:]]*$'` does not.
- E7 — duplicate-dispatch detectors, run on the three wave dirs: r25 → 8 duplicated report basenames (`ExecR17 MutCoverageAgreement readme-patch RevR17 ScoutR17RecordAgreement ScribeReadme ScribeSources sources-rows`) and 32/32 registry `agentId`s carrying a `-2` suffix; r26 → 0 and 0/87; r27 → 0 and 0/79 (`agentId` is `null` for every r26/r27 registry member, so the basename signal is the reliable one).
- E8 — driver acceptance predicate, read from fleet scripts: `scripts/shokunin-watchdog.sh:54` → "MIN_REPORT_BYTES=${MIN_REPORT_BYTES:-400}"; `:193-194` → "a file at the report path completes a lane-round only if it carries the `SHONEN`"; `scripts/hyaku/inline.sh:126` → "WARN lane repo has uncommitted changes"; `scripts/hyaku/inline.sh:136` → "lane-dead-no-report $lane round=$n; retry same round".
- E9 — `/home/vgpnk/Projects/shokunin/PROTOCOL.md:122` → "A lane whose report is still uncommitted when its mission completes has not satisfied this clause."; `:186-187` → "the new lane resolves them (commit-under-its-entry or revert) before it files its own report".
- E10 — an untracked draft of the gate already exists at `.ufo/waves/round-27/w1/souji-pre-report-gate.sh` (4879 B, `?? ` in porcelain, uncommitted); it implements `tip/report/shonen/clean/prereg` with exit 0/1/2 and `check-<name>=PASS|FAIL` on stdout. It is a draft, not the claimed `tools/souji-pre-report-gate.sh`.

## Findings

1. **Check `tip` — lane branch tip equals `git ls-remote origin refs/heads/<branch>`.** Pipeline:
   ```bash
   local_tip=$(git -C "$LANE" rev-parse --verify "refs/heads/$BR" 2>/dev/null) || local_tip=
   remote_tip=$(git -C "$LANE" ls-remote origin "refs/heads/$BR" 2>/dev/null | awk 'NR==1{print $1; exit}')
   [ -n "$local_tip" ] && [ -n "$remote_tip" ] && [ "$local_tip" = "$remote_tip" ]
   ```
   Failure mode prevented: an unpushed round whose report cites a tip that exists only locally — the driver completes the round on report content and the work is never landed. `PROTOCOL.md:122`: "A lane whose report is still uncommitted when its mission completes has not satisfied this clause." Two mandatory guards from E6: use `rev-parse --verify` (plain `rev-parse` echoes the ref name on stdout with rc=128 — E6), and require **both** sides non-empty (empty local vs empty remote must FAIL, not compare equal). Live at base: local == remote == `e78ac7c…` → PASS.
2. **Check `report` — the round report exists at the contract path and is non-trivial.** Pipeline:
   ```bash
   REPORT=/home/vgpnk/Projects/shokunin/.ufo/reports/round-27/souji.md   # fleet repo, not the lane
   [ -s "$REPORT" ] && [ "$(wc -c < "$REPORT")" -ge 400 ]
   ```
   Failure mode prevented: **the exact death of round-27 attempt 1** — `lane-dead-no-report souji round=27` (E1): the L1 returned having produced no report, so the driver killed the round and relaunched the same round (attempt 2). Live at base the path is **absent** (E5), so this check is the one that would have fired before the watchdog did. The `>= 400` clause is the driver's own floor (`MIN_REPORT_BYTES`, E8); a 15-byte stub carrying a `## SHONEN` heading passes a bare existence test and is still rejected by `report_of`.
3. **Check `shonen` — exactly one `^## SHONEN` heading.** Pipeline:
   ```bash
   c=$(grep -c '^## SHONEN' "$REPORT" 2>/dev/null) || c=0
   [ "$c" -eq 1 ]
   ```
   Failure mode prevented: a report the driver's `report_of()` will not accept as content (`scripts/shokunin-watchdog.sh:193-194`): zero headings → the driver logs `lane-report-not-accepted` and relaunches; two headings → a duplicated or concatenated report body, the r25 duplicate-report class (E3) reaching the driver. Two pipeline traps (E6): `grep -c` exits 1 on no-match, so the `|| c=0` guard is mandatory under `set -e`; and the literal `^## SHONEN` also matches `## SHONEN.md` (a heading to a different file) — the anchored `grep -cE '^## SHONEN[[:space:]]*$'` is the stricter form and should be the fixture's discriminator case.
4. **Check `clean` — no uncommitted lane-authored leftovers in the lane worktree.** Pipeline:
   ```bash
   git -C "$LANE" status --porcelain   # must be empty, except aggregator-owned
                                      # corpus/lessons/round-*-aggregator-* (PROTOCOL.md:188)
   ```
   Failure mode prevented: **round-26 verifier defect 1** (E2) — wave-seat outputs written past driver completion and left uncommitted in the lane repo, which then had to be routed back to the lane to commit or sweep. This is not hypothetical at base: the check currently **FAILS with 40 dirty paths** (E4), 36 of them the r26 trailing outputs, plus two unignored `__pycache__` dirs (`git check-ignore -v tools/__pycache__` → rc=1, no root `.gitignore` exists) and `census/operator-sweep-20261019/`. `PROTOCOL.md:186-187`: "the new lane resolves them (commit-under-its-entry or revert) before it files its own report." The driver's own signal is only a WARN (E8), so this lane-side gate is the stricter instrument.
5. **Check `prereg` — the frozen preregistration file is present and intact.** Pipeline:
   ```bash
   PREREG=$LANE/.ufo/waves/round-27/preregistration.txt
   [ -s "$PREREG" ] && grep -q '^MACHINE BLOCK' "$PREREG" && grep -c '^CLAIM ' "$PREREG"   # == 3
   ```
   Failure mode prevented: scoring against a mutated, inherited or absent counter contract — the r25 R25-M1 number-drift class, where the after-target literal was copied from another base without re-deriving. Live at base: present, 3752 B, `MACHINE BLOCK` + 3 `CLAIM` lines (E5).
6. **Amendment candidate A — duplicate-dispatch detector** (derived from E3/E7; **not** one of the four frozen checks). Pipelines:
   ```bash
   # (a) duplicated seat report basenames in the wave report dir
   find "$WAVE" -maxdepth 1 -name '*.md' -printf '%f\n' | sed 's/\.md$//' \
     | sed -E 's/-[0-9]+$//' | sort | uniq -d
   # (b) respawn-suffixed agent identities in the wave registry
   python3 -B -c "import json,re,sys; m=json.load(open(sys.argv[1]))['members']; \
     print(sum(1 for v in m.values() if re.search(r'-[2-9][0-9]*$', v.get('agentId') or '')))" \
     "$WAVE/swarm-registry.json"
   ```
   Failure mode prevented: the L1 issuing the same batched task call twice — 30 cancelled seat identities, two duplicate completed reports counted as distinct attack work (r25 R25-M2). Measured: r25 fires on both signals (8 duplicated basenames, 32/32 suffixed ids); r26 and r27 are clean (0, 0). Note (b) is unreliable for r26/r27 because their registries record `agentId: null` — signal (a) is the portable one. A `-N` suffix alone is suggestive, not proof; the discriminator must be "same seat base name, two files, both completed".
7. **Amendment candidate B — wave outputs must not post-date driver completion.** Pipeline: compare the mtime of every `.ufo/waves/round-<N>/w1/**` file against the driver's `complete <lane> round=<N>` timestamp in `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log`. Failure mode prevented: the second half of r26 defect 1 (E2) — seat files still being written after the driver logged complete. Measured at r26: 115/115 wave files are newer than the 14:39:08 complete line (E4). This is a lane-readable, read-only comparison (the watchdog log is append-only and fleet-owned; no write needed).
8. **Amendment candidate C — the report's cited lane commits must be ancestors of the lane HEAD.** Pipeline: `git -C "$LANE" merge-base --is-ancestor <cited-sha> refs/heads/master`. Failure mode prevented: a report citing a hash the lane repo does not contain, or one that is not an ancestor at closure — `PROTOCOL.md:119-121` names `git merge-base --is-ancestor <hash> HEAD` as the check. This is what makes check `tip` meaningful (a tip that exists but is not the cited/ancestor tip is still a defect).
9. **Gap the L1 must adjudicate — the frozen C3 case budget cannot cover five checks plus a control.** The frozen counter is `cases=4 pass=4 control=FALSE-GREEN-REJECTED` (preregistration, MACHINE BLOCK C3), i.e. 3 real cases + 1 false-green control. The four frozen checks (tip/report/shonen/clean/prereg) already exceed three; candidates A/B/C would exceed them further. Either the fixture combines several violations into one case (a case that breaks tip+clean together), or the case count is raised — the latter changes a frozen counter and is an L1 amendment (stricter-only), not a seat decision. I did not change it.
10. **Observation on the existing draft gate** (E10): `.ufo/waves/round-27/w1/souji-pre-report-gate.sh` already implements tip/report/shonen/clean/prereg with exit 0/1/2 and `check-<name>=PASS|FAIL` stdout lines — but it (a) is not the claimed path `tools/souji-pre-report-gate.sh` and is uncommitted, (b) uses the literal `grep -c '^## SHONEN'` (Finding 3 trap), (c) has no byte floor on the report (Finding 2), (d) has no duplicate-dispatch detector (Finding 6), (e) has no `--allow`-style exclusion for aggregator-owned `corpus/lessons/round-*-aggregator-*` paths (PROTOCOL.md:188) and no handling for unignored `__pycache__` (Finding 4). It is also currently doomed to FAIL check `clean` at base (40 dirty paths, E4). This is a draft for the executor seat and the L1 to reconcile; the L1 installs the fixture at `tests/fixtures/r27-pre-report-gate.sh` and the tool at `tools/souji-pre-report-gate.sh`.
11. **Naming the failure modes in one line each** (for the tool's help text and the fixture's case names): `tip` → unpushed round / local-only tip; `report` → no report at the contract path (attempt-1 death) or a sub-400-byte stub; `shonen` → no SHONEN section (driver rejects the marker) or a duplicated one; `clean` → trailing or uncommitted lane-authored work in the lane worktree; `prereg` → missing or mutated frozen counter contract; `dup-dispatch` → the same batched task call issued twice; `wave-late` → seat output written past driver completion.

## Attack log

Not an attack seat; no claim/counter was attacked. Findings 9 and 10 are counter-shaped observations routed to the L1, not amendments applied here.

## Cleanup

`/var/tmp/souji-r27-ScoutPreReport` (scratch git repos + fixture probe files) removed before finishing; verified absent. No file was written outside this report; the lane's 40 pre-existing dirty paths (E4) were left untouched, `HEAD` still `e78ac7c4837b81b634db4a927605a751a7f006ba`, index unmodified.
