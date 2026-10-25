# MutC3Control — C3 committed baseline / extended fixture vs old probe, two C3 mutants, always-success stubs (souji r25 w2)

Seat: L1Souji25.MutC3Control (mutation-tester, leaf). Written 2026-10-25. No edits to any lane/fleet file; scratch `/var/tmp/souji-r25-MutC3Control/` removed before finish. Host git 2.56.0. No installs/updates.

STATUS: PASS. All five probes run; verdicts below.

## Method (all in /var/tmp scratch, byte-exact extractions)

- **Old probe (a6d2d15):** `git show a6d2d15:tools/souji-repo-structure.sh` → sha256 `80025137b20d5a61` = tool_sha256 in committed receipt `census/round-25/records/c3-control-base.tsv` (blob 0f42ebf5…).
- **Committed baseline fixture (a6d2d15):** `git show a6d2d15:tests/fixtures/r13-repo-structure.sh` → sha256 `b6bf52056d037b22` = receipt tool_sha256 (blob 39b488a6…).
- **Extended fixture:** working-tree `tests/fixtures/r13-repo-structure.sh` → sha256 `eabc5f0ac56ea3db` = W1 draft `.ufo/waves/round-25/w1/r13-repo-structure.sh` (ExecC3 blob c369546e…), 34 788 bytes.
- Counter invoked exactly as frozen: `bash <fixture> --selftest --probe <probe>`.

## Table (one table; all runs on this host, exact old probe = a6d2d15 blob)

| probe (CSI) | fixture | final line | rc | failing case(s) / detail |
|---|---|---|---|---|
| old probe a6d2d15 (`80025137…`) | committed base a6d2d15 | `selftest=PASS ids=5/5` | 0 | — (matches c3-control-base.tsv: 41 manifest entries, checks=29) |
| old probe a6d2d15 | extended draft | `selftest=PASS ids=7/7` | 0 | — (linked: rc=0 common_entries=53 private_entries=9 checks=8 control=PASS; colocated: others_plain=0 others_colocated=2 commits 1→2 differing_keys=8) |
| **mut-a-misreport** (linked: prints private gitdir as `probe.git_common_dir`) | extended draft | `selftest=FAIL ids=7/7 missing=[] extra=[] failed_verdicts=1` | 1 | only `linked-common-dir`: `probe.git_common_dir=<priv> want=<common>; probe.git_dir==probe.git_common_dir` |
| **mut-b-commonwrite** (linked: appends to `$common/description`) | extended draft | `selftest=FAIL ids=7/7 missing=[] extra=[] failed_verdicts=1` | 1 | only `linked-common-dir`: `common-dir-manifest-delta` |
| stub-noop (always `exit 0`, no output) | extended draft | `selftest=FAIL ids=7/7 failed_verdicts=1` | 1 | promisor/bogus rc=0 want=2 (markers missing); linked metric checks empty; colocated no-metrics + metrics-identical + others unparsed |
| stub-canned (always-success canned transcript, never adapts) | extended draft | `selftest=FAIL ids=7/7 failed_verdicts=1` | 1 | promisor/bogus rc=0 want=2 (+ refusal-emitted-structure); linked `probe.git_common_dir=/canned/.git want=<literal common>` + repo_root/git_dir mismatches; colocated metrics-identical + `others.count colocated=0 not> plain=0` |
| mut-a-misreport | committed base | `selftest=PASS ids=5/5` | 0 | **false green** (committed fixture blind: no linked case) |
| mut-b-commonwrite | committed base | `selftest=PASS ids=5/5` | 0 | **false green** (same) |
| stub-noop | committed base | `selftest=FAIL ids=5/5` | 1 | write-free/object-metrics/bogus/promisor fail |
| stub-canned | committed base | `selftest=FAIL ids=5/5` | 1 | object-metrics (real oid keys want real values), bogus/promisor rc |

## Findings

1. **Baseline 5/5 confirmed** — committed fixture + exact old probe: `selftest=PASS ids=5/5`, rc 0; identical to the committed c3-control-base.tsv receipt (same id lines, manifest_entries=41, checks=29).
2. **Extended 7/7 confirmed** — exact old probe passes the two new pinned cases: linked-common-dir (rc=0, common manifest 53 entries, private 9, checks=8, control=PASS) and colocated-vs-plain (plain/colo rc=0, `references.others.count` 0→2, commits 1→2, differing_keys=8, precondition=colocated-not-interchangeable…). No probe change was needed (matches ExecC3 + ScoutC3Structure-2).
3. **Both C3 mutants red (amendment 3 §2 exactly):** each fails the extended fixture with `failed_verdicts=1`, the sole failure being `SOUJI-R13-STRUCT-linked-common-dir`; missing=[] extra=[] confirms no id-set gaming. (a) misreport: caught by the literal `$A/.git` oracle + `probe.git_dir==probe.git_common_dir` guard. (b) common-dir write: caught by the common-dir manifest delta (private manifest alone cannot see it).
4. **Always-success stubs are rejected by the extended fixture** (both variants, rc 1): a noop fails structure checks; even a canned success-shaped transcript cannot reach PASS because bogus/promisor demand rc=2, the linked case uses the literal common-dir oracle, and the colocated case demands `others(colo)>others(plain)` with non-identical metrics. The do-nothing emit cannot reach `PASS`, so the counter is not vacuously satisfiable by a trivial emitter.
5. **Committed fixture blind to the mutants (false green):** both C3 mutants score `PASS ids=5/5` on the committed fixture — the regression gap amendment 3 §2 exists to close; the extended fixture closes it.

## Attack log

- A1 (amendment 3 §2 red arm): receipts above — mut-a (private-gitdir-as-common-dir) and mut-b (common-dir write) both red on extended, both false-green on committed.
- A2 (vacuity probe): two always-success emitters (noop and canned transcript) — both rejected by extended; canned variant shows the case-level checks (rc=2 refusals, literal oracle, others-ordering) are what defends 7/7, not the id tally.
- A3 (no edits): probe/fixture/stub variants all live in scratch only; lane tree untouched. Scratch removed.
