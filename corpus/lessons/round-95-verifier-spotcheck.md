# Round 95 — non-author verifier spot-check (integrator, hyaku)

author: hyaku closure (non-author integrator, @m_zfl)
Lane base `93c3ef13a9eb9678483518562f3692124db714c2`, lane HEAD `71a1ae0951c605e4d539cd25db3a5aad150c003e`. Date 2026-11-09. Reviewer ≠ author. Claims re-measured on committed bytes; no fleet-wide gate executed (PROTOCOL §Gate standard, Closure consequence).

## 1. Conformance

- Report `.ufo/reports/round-95/souji.md` in fleet repo: `git log --format='%an %H' -- <report>` → `souji-shokunin 9e442e1e09cf3e1be4d84452c61e266aaa07ce40` — lane identity, landed. Heading `## SHONEN` with one `[~]` line per box (4 boxes). No marker: 6 commits cited, all present in lane history, `merge-base --is-ancestor 71a1ae09 master` holds. Lane repo clean (`git status --porcelain` empty), pushed (`ahead=0`, `ls-remote origin refs/heads/master` = `71a1ae0951c605e4d539cd25db3a5aad150c003e`).
- Prompt `.ufo/prompts/souji-round-95.md` carries mission/axes binding, 1–3 falsifiable claims, lowest-axis rule, L2 floor (≥8 batched), report contract, commit/push scope, L0 side channel, hyaku addendum §6 — template contract present.
- Dispatch/complete digest (watchdog.log, mutable — copied verbatim): `2026-11-09T02:20:07-03:00 launch souji round=95 pgid=2804766 driver=hyaku-inline attempt=1`; `2026-11-09T03:30:59-03:00 complete souji round=95; hyaku-inline attempt=1`.
- Status: `ok` (real report, checkable work, pushed lane). No defect bars admission.

## 2. Pre-file falsification ledger (addendum §8, Amendment 59)

`python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 95` → `PREFILE-FALSIFICATION: pass claims=2 rows=27 attack_seats=8 findings=0`, exit 0. Matches lane's own receipt (`.ufo/waves/round-95/prefile-gate.txt`). All 14 `falsifies-wording` rows name a narrowing in `plans/round-95.md` (A1–A3/A5–A7); every claim is covered; all eight attack-role seats read. Ledger committed at `.ufo/waves/round-95/claim-falsification.tsv`. No hidden falsification — PASS.

## 3. Per-claim re-check

**C1 — calibration 7 (lowest owned non-retired axis). Before→after 5 → 0 mis-scored crash-channel fixtures.** Re-measured, not evidence-verified.
- Before (frozen r94 rule): `census/round-95/controls/c1-control-r94-rule.txt` `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=2 killed=5 survived=3` — h-sysexit/killed=yes, h-atexit/no, h-thread/no, h-osexit/yes, h-sigkill/yes. Mis-scored = 5 − 0 = 5 under `grep -cE '^SEARCH h-(sysexit|atexit|thread|osexit|sigkill) ' − grep -cE '^SEARCH h-(sysexit|atexit|thread|osexit|sigkill) .*killed=errored'`.
- After (committed `dd520684`): `census/round-95/records/c1-after.txt` `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`, `SEARCH-SUMMARY ... errored=7 killed=2 survived=1` — all five crash fixtures `killed=errored`, five r94 targets unchanged (two pre-existing errored, one killed, one survived + h-crash pair).
- Closure re-run on committed bytes (no sibling gate executed; plain measurement only): `python3 -B census/round-95/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py ... --jobs 5 --ids census/round-95/c1-targets.json` → same check line, same `errored=7 killed=2 survived=1`, exit 0. Verifies.
- Forgeries: FA/FB/FC refused 3/3 (`controls/c1-forgery-controls.txt` `C1-FORGERY-CTL-SUMMARY`).
- Reported narrowings honored: SystemExit leg scores declared `sys.exit` inside `main` as errored (mismatched=6 in `records/declared-shapes.txt`); `os._exit(0)` → 70. These narrow scope, not the predication.

**C2 — operability 8. Before→after 12/16 → 16/16.** Re-measured.
- Before (r94 probe): `census/round-95/controls/c2-control-r94-probe.txt` `ARMS-SUMMARY arms=16 conform=12` (S9–S11 exit 1, S12 hung), EXIT 1.
- After: `census/round-95/records/c2-after.txt` `ARMS-SUMMARY arms=16 conform=16`, EXIT 0; forgeries GA/GB/GC conform 15/14/15, `refused 3/3` (`controls/c2-forgery-controls.txt`). Closure census re-ran the sixteen-arm counter on committed bytes; summary matched (arm detail in receipt).
- Narrowing honored (A6): a `setsid` grandchild holding pipes hangs the probe past `--timeout`; routed to r96. The four refusal shapes (decode/create/write/timeout) all exit 2 with `C2-FORGERY-FATAL:`.

No owned axis harmed: `git diff 93c3ef13 71a1ae09 -- SCORECARD.md` shows scores unchanged (calibration 7, operability 8, coverage 8; "no reproducible 0–10 mapping" carried, verdicts do the work); capabilities table +2 rows, each backed by re-measured commands.

## 4. Per-axis verdicts

| axis | verdict |
|---|---|
| calibration | **improved** (C1 5 → 0) |
| operability | **improved** (C2 12 → 16) |
| coverage | **unchanged** (no score change; C2's TOCTOU/unix-surface concerns not re-scored) |

## 5. Discernment spot-check (LEARNING.md)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S360 `sys.monitoring` RAISE | ADMIT | docs.python.org/3/library/sys.monitoring.html (§ Events, `sys.monitoring.events.RAISE`) via committed capture `census/round-95/srcs/monitoring.html`/`.txt` | **agree** | Quote "An exception is raised, except those that cause a STOP_ITERATION event." (11w) found at occurrence 1 in whitespace-normalized tag-stripped text; sha256 `cd85fa73159a...` matches row; A7-corrected scope cell discloses page does not name SystemExit. |
| S362 `os._exit` | ADMIT | docs.python.org/3/library/os.html#os._exit | **agree** | Quote "Exit the process with status n , without calling cleanup handlers, flushing stdio buffers, etc." (15w) occurrence 1; sha256 `078e69b12c66...` matches. |
| `faulthandler` docs | REJECT | docs.python.org/3/library/faulthandler.html | **agree** | No exit-status statement; SIGKILL omitted from its list — reject reason accurate; flip (claim needing fatal-signal-vs-verdict separation) is stated and testable. |
| S361 `threading.excepthook` (new row) | ADMIT | docs.python.org/3/library/threading.html#threading.excepthook | **agree** | Quote "Handle uncaught exception raised by Thread.run() ." (7w) occurrence 1; sha256 `d6f8ca655ef4...`; A7 correction verifiably applied (no `Functions` heading). |

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok` (W04 duplicate-URL warnings only), exit 0. Census 281 → 286; `git diff --numstat 93c3ef13 -- corpus/SOURCES.md` → `5 0` (no pre-existing row touched). All new rows `mined`, `used-by` = knowledge entry.

## 6. Trend verdicts

- **expansion: improved** — five tier-A `mined` rows (S360–S364) + `corpus/knowledge/crash-channels-beyond-excepthook.md` on crash channels the lane did not hold before; capability rows backed by running commands.
- **quality: improved** — C1 5→0 and C2 12→16 re-measured by non-author seats on committed bytes; forgery controls refuse 3/3 each; full-population census (R95ExecCensus, 263 ids) shows no verdict change beyond the five new fixtures.
- **discernment: improved** — five wording falsifications were narrowed before filing (A1–A3/A5/A6), the lane's own new rows were corrected (A7), the labrat's finding was re-measured on exact bytes (Q172, mismatched=6 shown able to fail), and M1's recurrence class was mined into a criterion with a failing test.

## 7. Routed defects (lane must fix next round)

None blocking. Carried by the lane into `### Planned (r96)`: SystemExit-leg rewrite for declared `sys.exit` in `main` (Q172 precondition, mismatched=0); signal-safe crash path (`os.write(2,...)` + real `os._exit(70)`); hook scope to the counter (ids 3–4); per-channel `SOUJI-R95-CRASH` CHECK; finalization `__del__` fixture; harness-side crash target; C2 FATAL-reason-text arms (S13), pipe-holder reaping, write-failure/TOCTOU arms. SHONEN boxes look assessable as asserted (`[~]`) — promotion is operator-owned; noted here for the operator, not acted on.
