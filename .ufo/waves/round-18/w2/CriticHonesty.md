STATUS: DONE — overclaim audit of corpus/lessons/round-18.md, SCORECARD.md r18 rows, SKILL.md r18 rows at 5efb519: headline counts verify against records and a read-only replication of the pointer scan, but C2's "after: 0" is asserted with no committed record, and five smaller asserted/imprecise statements found.

# Attacked claims (honesty/calibration)

Corpus lesson §Measurements/§Gate, SCORECARD rows 13–15 + registry rows 52–54, SKILL rows 149/165/167/170–174: every "measured" number should have a record, every count should match its record, every "all/every" should have no exception.

# Method (all read-only on committed data)

- `git show 5efb519:<path>` on the three files under attack and every cited record.
- Parsed `census/round-18/c1-matrix-worktree.json`, `gate-pointers-before-b576341.json`, `gate-replays-r18.json`, `leak-count-live-1721.json`, `proc-census-live-1721.tsv`, `live-fleet-pairs/*.tsv`, `jj-receipts-r18-*.txt`, `leaked-procs-before-1631.txt`.
- Re-implemented the gate's `check_pointers`/`_pointer_paths`/`_round_log_lines`/`_trim_pointer_token`/brace/round-range logic (copied verbatim from `tools/souji-landing-gate.py:644-760` at tip) in a scratch script under /var/tmp; ran it against `git ls-tree`+`git show` at b576341 and 5efb519 with the live `--fleet-root` stat. No souji tool was executed; no process was signaled.
- sha256 comparisons: census `7e6a92d4…` at tip == matrix record `changed` arm; gate `f8a2ebe…` at tip == `gate-replays-r18.json` `gate.sha256`; run-matrix.py + r18-bounded/r15/r17 fixtures byte-identical between 3f822e8 and 5efb519 (records are fresh for tip code).

# What verifies clean (counts that match their records)

- Matrix record `invalid_suites: []`; r18-bounded 6/5/5/0 fails across pre-harm/cc21683/b576341/changed; r17-hygiene 21/14/0/0; r15-config 8/16/0/0; r14-namespace 10/0/0/0; selftest 36/38/49/62 checks, 0 failed; `session_cleanup.killed` empty in every suite; `bash_n`/`shellcheck_warning` rc 0 all arms. b576341 FAIL ids: B1–B4, B8, all `observed_exit=124` — the lesson's "hit the 40 s fixture deadline" is exact, and SKILL row 170's named-failure list matches the record.
- `gate-pointers-before-b576341.json`: exit 2 ("no .md reports under .ufo/waves/round-18/"), 10 findings = 7 ddb7347 citations (SKILL:163,165; README:216; knowledge:2,44,126,148) + 2 non-files + 1 LG-FROZEN-MEASURED; `checked_ptrs=319`, `ptr_fleet=3`. **My independent replication of the tip grammar at b576341 reproduces all 9 pointer findings, exactly 319 tokens and 3 fleet rows** — the record survives the 2fc5f33 comma-fix gate change.
- Tip replication: 445 tokens, 0 dangling, 0 unused exemptions (the r14 `record.json` exemption is consumed by `check_frozen_pins`; r14 placeholder `measured_commit` still present at tip).
- `gate-replays-r18.json`: all five `match: true`, per-replay exit/finding counts match the lesson (1/5, 0/0, 0/0, 0/0, 1/29); gate sha `f8a2ebe` == tip bytes — not stale.
- Live C3: proc-census 65 rows == leak-count 65, **pid sets byte-identical** (diffed). Reason split 58 cwd-deleted + 7 fd-path-gone matches both records.
- `leaked-procs-before-1631.txt` = 58 souji-family orphan lines (44 r15-config + 14 r17-hygiene argv prefixes); leak-count `by_prefix_family` agrees (44+14+7 other=65).
- Fleet pairs: pair1 differs only in tameshi mtime; pair2 differs in mado dirty 10→13 plus mtime — as the lesson says.
- Registry "scout 27 / executor 15 / reviewer 15 / scribe 10 / connector 8 / critic 8 / revenger 4 / sentinel 2 / simplifier 2" == `swarm-registry.json` role counts; 91 `.md` reports in tree.
- ScoutOpenSites.md verifies the lesson's "23 blockable open sites" (25 sites, 23 blockable, line 53).
- Watchdog code (`tools/souji-census.sh:1475-1650`): `set -m` worker in own process group, watchdog kills `-$pgid`; list-phase `guard_repo_candidate` and `census_one` both wrapped — SKILL row 149 "every repository (list-phase guards and census_one) runs in its own process group" is accurate. Timeout parse: integer 1..86400, invalid → exit 2 (`:246-256`). `repo-timeout`/`repo-timeout-unreaped` diagnostics and the `error`-row shape match the claimed contract; `rc=2` propagates to exit 2 (protected refusal preserved).

# Findings

## F1 — C2's after-verdict has no committed record (calibration; the sharpest finding)

- `corpus/lessons/round-18.md:7`: "After: the same command at the round tip — see Gate." §Gate (`:27`) contains **no command, no output, no count, no record path** — only "candidate admit."
- `SCORECARD.md:14` states "after: 0 at the round tip (Gate in `corpus/lessons/round-18.md`)". The pointer it gives (lesson §Gate) contains no such measurement.
- `git ls-tree -r 5efb519 census/round-18/` has no `gate-pointers-after-*.json`; only the b576341 *before* record exists. The claimed `souji ok`-style end-state is asserted, not evidenced.
- This is self-referentially bad: the round's own calibration claim is "authority files must not cite evidence that does not exist" — and the SCORECARD row cites §Gate for a measurement §Gate does not contain. An admission reviewer cannot verify "0" without re-running the gate themselves.
- I replicated it read-only: tip scan → 445 ptr tokens, 0 dangling findings, 0 stale exemptions, 3 fleet (README:217 ×2, knowledge:148). So the *number* is right; the *evidence* is missing. On the axis this seat is judged on: the claim is currently an assertion that happens to be true.
- Smallest fix: run the same `--rev 5efb519 --round 18 --fleet-root` command, commit `census/round-18/gate-pointers-after-5efb519.json`, cite it from lesson §Gate and SCORECARD:14. One command, one file.

## F2 — SCORECARD:15 flattens a caveat the records contradict

- Claim: "live fleet pair identical on 21 repositories (`census/round-18/live-fleet-pairs/`)".
- Record reality: pair1 is identical *excluding mtime* (diff shows only `2026-10-20T17:29:36` → `:48` on tameshi); pair2 differs in mado-shokunin `dirty 10 → 13` (a lane writing mid-run) *and* mtime. The lesson (`round-18.md:6`) says this correctly; the SCORECARD row drops both qualifiers and says "identical" flatly — inside a parenthesis that still says "(author: improved, outside admission pending)" the word "identical" is exactly the kind of thing a verifier must catch.
- Smallest fix: "pair 1 identical excluding mtime; pair 2 differs only in mado-shokunin dirty 10→13 (lane writing during the run)" — copy the lesson's wording.

## F3 — asserted-not-recorded cluster (low; each is plausible but unverifiable from the tree)

- `round-18.md:26` "the whole live fleet takes about 11 s" — `git grep` across the entire tip tree finds this string only in this sentence; no record carries a fleet-run wall time. Asserted.
- `round-18.md:6` "Leak count … before the matrix 65 … after 66 — the one new pid is another lane's live omp runner" and "the 25-minute matrix" — no leak-count record exists after the matrix (only `leak-count-live-1721.json` at 20:21Z) and the matrix record carries no timing field. The before-65 and the orphan attributions check out; "66" and "25-minute" do not.
- `round-18.md:9` quarantine "selftest 101 → 105" — no committed record carries 105; the wave-1 executor (`QuarantineRecipe.md:8`) predicted **104**, a one-off discrepancy nobody reconciled. Counting `st_check` call sites in the tool is inconclusive (65 sites, some in loops).
- Fixtures `r18-proc-census.sh` 11/0, `r18-landing-pointers.py` 11/0, "r16 fixture 15/0" (lesson :7–8, SCORECARD:13–14) — no committed run output for any of the three. The pointer fixture's 11 emit sites exist and its `historical-b576341-round-18` case asserts the real-lane replay, so the shape is right; the numbers are asserted.

## F4 — SKILL row 167 capability text vs the actual record

- Tip SKILL.md:167 r17-gate-replays row: "the gate's own `--selftest` tail recorded". Both committed replay records — `census/round-17/gate-replays-4f48343.json` and `census/round-18/gate-replays-r18.json` — carry `"selftest": null` (`gate-replays.py:239,261`: only populated under the never-used `--selftest` flag). The registry describes a behavior the produced record does not exhibit.
- Smallest fix: either drop "the gate's own `--selftest` tail recorded" from the row or pass `--selftest` when generating the r18 record.

## F5 — prose imprecisions (very low)

- `round-18.md:45` "`expected_sha_match` false by design" — the record's field is `gate_sha256_match` (inside `expected`); misnamed field.
- `round-18.md:60` R2 correction lists knowledge line `:3` among lines "re-pointed from never-committed `ddb7347` record names" — line 3 at b576341 contains no ddb7347 token; what changed there was the recheck expectation `total=20 failed=0 skipped=0` → `total=35 failed=0 skipped=2` (visible in the tip file's own "(r18 correction)" parenthetical). Minor over-attribution inside a corrections section that is supposed to be exact.
- `round-18.md:7` truncates the finding detail: "2 deliberate non-files (`census/operator-sweep-20261019/`, the removed nested `.git`)" — the actual cited path is `tests/vault/vadv54-run/p/p6repo/.git` (SKILL.md:110). Harmless paraphrase, still names the wrong file shape for a gate that exists to police path citations.
- The 8th never-committed citation (`SKILL.md:166`'s elided `-ddb7347.json` → `seat-audit-r16-replay-ddb7347.json`, also absent at b576341 — verified: no such blob in the tree) is correctly disclosed as a grammar blind spot in §Gate; counted here only as confirmation that "7 citations" is *gate-visible* citations, not total dangling citations. The lesson says this; fine.

## F6 — "never signals" is selftest-scoped, slightly loose phrasing (very low)

- `SKILL.md:174` r18-leak-count row: "reads /proc of the current uid; never signals" — `census/round-18/leak-count.py:228,235` sends `os.killpg(process.pid, signal.SIGKILL)` and `process.kill()` inside `run_selftest()` (on a process it spawned; `souji-proc-census.sh:3` discloses "never signals a process outside its selftest" but the registry row omits the qualifier).
- Smallest fix: "never signals outside `--selftest`" (one qualifier, same pattern as proc-census's own header).

# Counterexample summary for the judge

The strongest counterexample is F1: a calibration claim ("authority files must not cite evidence that does not exist") whose own headline after-verdict cites a section containing no evidence. It is fixable with one command + one committed JSON; it is not a reason to reject C2's mechanism (the gate demonstrably reproduces 0/10 under independent re-implementation of its grammar) — it is a reason the round's own standard currently fails on the round's own scorecard row.

Everything else: F2 is a count-precision defect against its own record (tradeoff vs. the lesson's full wording — reject-able if SCORECARD compression is tolerated by convention; the r17 "22 repos" precedent says this fleet does not tolerate it). F3/F4/F5/F6 are fixable wording/record gaps, none requiring design change.

# Verdict

- C2 after-claim: **partial** — numerically verified by independent replication, but asserted-as-measured in both files under attack (F1).
- Count claims vs records: **holds** for every committed record checked (matrix, gate-before, replays, leak/proc live pairs, jj-receipts, swarm registry); **fails** for SCORECARD:15's "identical" (F2) and the SKILL:167 selftest-tail sentence (F4).
- "All/every" claims: **holds** — `session_cleanup.killed` empty in all 16 suite-arm cells; watchdog coverage of list-phase guards + census_one verified in code; every named b576341 failure is the claimed deadline.
- Smallest safe correction set: (a) commit `census/round-18/gate-pointers-after-5efb519.json` and cite it in lesson §Gate + SCORECARD:14; (b) copy the lesson's pair wording into SCORECARD:15; (c) one-word fixes: "never signals" → "never signals outside --selftest" (SKILL:174), drop "the gate's own --selftest tail recorded" or record it (SKILL:167), `expected_sha_match` → `gate_sha256_match` (lesson:45), move `:3` out of the re-pointed list (lesson:60).

# Tooling installs

None. All checks used git read-only plumbing, python3 on committed blobs, and stat() replication of the fleet-path check — no souji census/gate tool was executed.

Report: .ufo/waves/round-18/w2/CriticHonesty.md
