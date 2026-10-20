# RerunCheckerFixture — r16 W2 (falsify)

Seat: `SoujiR16.RerunCheckerFixture-4` · Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`
Lane HEAD at review: `163158a706352f1c0ee3521c4da2e5289970db57` (context said `a6ec781`; `163158a` adds the
lesson/SOURCES commit and is a descendant of the landing capture `7a79dc2`).

## Item

1. ALLOWED-EXEC: `python3 .../tests/fixtures/r15-preservation-evidence.py` — confirm 8/8.
2. Attack the r16 literal sets (`BENIGN`/`REFUSAL`/`SAFETY`/`PRESERVE`/`TOKEN`/`NS`) against
   `census/round-16/c1-matrix-final.json` per-arm statuses.

Axis under judgment: calibration (does the pinned universe equal the measured behavior, and does the
harness actually fail when a pin is wrong).

## Result — 8/8 confirmed

```
ok selftest
ok external-clean
ok external-green-only
ok external-weakened-red
ok external-no-ns
ok external-changed-is-baseline
ok frozen-lane
ok frozen-tampered
fixture: 8/8 checks passed
RC=0
```

The run is against tool bytes `tools/souji-preservation-evidence.py` at HEAD; the fixture file is
unchanged from HEAD (`git diff` empty for it).

## Literal-set attack — statuses hold exactly

Mechanically compared the fixture's pinned classes with the matrix (all assertions exited 0/`true`):

| Fixture class | ids | changed | pre-harm (`a31642d`) | r14-harm (`cc21683`) |
|---|---|---|---|---|
| `BENIGN` (11) | 01,04,06,07,09,10,12,13,15,16,20 | PASS | PASS | FAIL |
| `REFUSAL` (3) | 02,11,17 | PASS | FAIL | PASS |
| `SAFETY` (5) | 03,08,14,18,19 | PASS | FAIL | FAIL |
| `PRESERVE` (1) | 05 | PASS | PASS | PASS |

- changed: `total=20 failed=0`, every verdict `PASS`
  (`tests/fixtures/r15-preservation-evidence.py:49-61` vs matrix `.arms.changed["r15-config"]`).
- pre-harm: `failed=8`, FAIL ids = `02,03,08,11,14,17,18,19` = `REFUSAL ∪ SAFETY`
  (`PREHARM_FAILS`, fixture:60). Exact set equality asserted.
- r14-harm: `failed=16`, FAIL ids = `01,03,04,06,07,08,09,10,12,13,14,15,16,18,19,20`
  = `BENIGN ∪ SAFETY` (`HARM_FAILS`, fixture:61); PASS ids = `02,05,11,17`. Exact set equality on
  both directions.
- r15-baseline: not part of the pinned universe; the arm is unparseable by construction
  (`bash -n` rc 2, syntax error at `tools/souji-census.sh:1368` in `.arms["r15-baseline"].bash_n`),
  and its config arm is 20/20 FAIL (rc 1). Nothing in the checker represents that arm.
- `TOKEN` (6 ids) equals the checker's `CONFIG_TOKEN_IDS`
  (`tools/souji-preservation-evidence.py:361-363`) and every TOKEN id carries a non-`none`
  `observed_finding` in the changed arm; every other changed PASS carries `none` — verified row by row.
- The four class sets (`BENIGN`/`REFUSAL`/`SAFETY`/`PRESERVE`) are disjoint and cover `01..20`
  exactly once; `TOKEN` is exactly `REFUSAL ∪ {03,14,19}` (a subset of `REFUSAL ∪ SAFETY`), and `NS`
  is 12 ids disjoint from all classes; the changed namespace arm is 12/12 PASS.

Verdict: **holds**. The r16 status literals are correct for every arm the harness pins.

### Provenance drift (informational, not a failure)

The fixture comment cites `c1-matrix-final.json`, but that matrix measured `r15-census-config.py`
at sha `85de2a43…` (commit `0a70bef`), while current/HEAD bytes are `27474396…` (R4 commit `c6207bd`
capped the human-readable CASE detail at 400 chars). `c1-matrix-landing.json` measured the current
bytes. Statuses are identical across both matrices for all arms; changed-arm and namespace details
are byte-identical, and pre-harm details differ only by that 400-char cap. So the literals are valid
for both revisions — but the comment should cite the landing matrix (or both digests) since
`git show HEAD:` no longer matches `c1-matrix-final.json`'s `fixtures_sha256["r15-config"]`.

## Findings

### F1 (medium) — literal *statuses* are pinned; detail *values* are not, and the harness's clean record contradicts the shipped record

`detail()` (`tests/fixtures/r15-preservation-evidence.py:104-110`) synthesises
`observed_exit=2 observed_finding=path-protected` for **every** `TOKEN` id and
`observed_exit=0 observed_finding=none` for every non-`TOKEN` id. The matrix and the shipped frozen
record both say otherwise for three ids:

| id | matrix / `record.json` changed-row | harness `detail()` |
|---|---|---|
| R15CFG-03 | `exit=0`, `config-unsupported:git-include-cycle` | `exit=2`, `path-protected` |
| R15CFG-14 | `exit=0`, `status-skipped:filter-driver-bound` | `exit=2`, `path-protected` |
| R15CFG-20 | `exit=2`, `finding=none` | `exit=0`, `finding=none` |

The checker reads only the finding token (`tools/souji-preservation-evidence.py:1493-1503`) and never
parses `observed_exit` — its only occurrence is as a substring in `REASON_TOKENS` (`:371`). So a
record claiming a protected-path refusal at whole-run `exit=0` (impossible under C1: protected path
⇒ exit 2) certifies `clean`, and `baseline-reason-weak` (`:1507-1519`) accepts a FAIL row whose
"concrete reason" is `observed_exit=0`. No external arm constructs either contradiction
(arms are `:205-292`).

Verdict: **partial** — the pins are calibrated for statuses and for token presence; the exit-code
axis is unexercised and the harness's template record is not the shipped record.
Smallest fix: replace the three fixed strings with a pinned per-id `(observed_exit, observed_finding)`
table copied from the matrix (03→`(0, config-unsupported:…)`, 14→`(0, status-skipped:…)`,
20→`(2, none)`), and add one negative arm `external-exit-contradiction` (R15CFG-02 PASS with
`observed_exit=0`) requiring a rejection. If the checker is to reject it, add the corresponding
finding id rather than changing only the fixture.

### F2 (medium) — the checker's own stated oracle table is the r15 one and contradicts its r16 constants

Module docstring (`tools/souji-preservation-evidence.py:109-116`) still documents:

```
benign   (01,04,06,09,10,12,13,15,16)
refusal  (02,03,07,11,14,17,19)
safety   (08)
preserve (05 pass / 18,20 fail preharm; all pass baseline + changed)
```

The implemented r16 universe (`:323-347`, `:350-353`, `:357`) is
benign `01,04,06,07,09,10,12,13,15,16,20`, refusal `02,11,17`, safety `03,08,14,18,19`,
preserve `05`. The docstring mispredicts **6 of 20 ids** (03, 07, 14, 18, 19, 20) against the
measured matrix — e.g. it calls 19 a refusal (harm pass) while the matrix records 19 FAIL on r14-harm.
`_expected_status` implements the constants, not the docstring (`:1302-1317`), so behavior is right;
the human-readable contract is stale and would mislead a maintainer "fixing" code to match it.

Verdict: **fails** (documentation contract). Smallest fix: regenerate `:109-116` from the
`CONFIG_*` constants, or replace the table with a pointer to them.

### F3 (low-medium) — `frozen-lane` cannot distinguish a clean frozen verdict from a failed one

The frozen check accepts `rc ∈ {0,1,2}` and requires only the `souji-preservation-evidence:` and
`frozen_files:` banners (`tests/fixtures/r15-preservation-evidence.py:277-280`; rc guard immediately
above). `frozen_files` is emitted on every path because it is set before the pin loop
(`tools/souji-preservation-evidence.py:1693`). Therefore the 8/8 green is unchanged whether
`--frozen` reports `clean`, `failed`, or `could-not-evaluate` — and the only `--frozen` evidence in
the lane (a `clean` claim) is not exercised by this harness. The justification comment says this is
deliberate for a pre-integration snapshot, but the snapshot has since been regenerated.

Verdict: **partial** — the harness under-covers the one claim it is adjacent to.
Smallest fix: require `souji-preservation-evidence: clean` in the frozen-lane needles now that
`expected.json` pins `verdict: clean` and the record binds current bytes.

### F4 (low) — frozen README is stale

`tests/fixtures/r15-preservation-frozen/README.md:6-10` says the shipped pins describe a
pre-integration snapshot and "correctly yield `snapshot_tampered` (exit 2) until the integrator
refreshes". They have been refreshed: `record.json` has `measured_commit=c6207bd…`, tool sha
`64a60fd0…` (= live), fixture sha `27474396…` (= live), ns fixture `e6a984b1…` (= live);
`record_sha256=173db777…` matches the file bytes; `expected.json` pins `verdict: clean`.
`--frozen` on the lane therefore evaluates `clean`, contradicting the README paragraph.

Verdict: **fails** (doc). Smallest fix: rewrite that paragraph to state the record is pinned at
`c6207bd` against the current digests and that `clean` is the expected verdict.

### F5 (low) — the checker's selftest count is unpinned (floor is 1)

`tests/fixtures/r15-preservation-evidence.py:211-217` requires `N/N passed` with `N ≥ 1`
(`int(match.group(2)) < 1`). The external harness therefore cannot detect erosion of the checker's
own selftest (24/47 → repaired 47/47) down to one case. The census selftest (38/38) is measured only
by the matrix runner and is likewise not floor-asserted by this fixture.

Verdict: **partial**. Smallest fix: pin `47` (or a documented floor) in the external fixture.

### F6 (low) — `HARM_CASES` omits R15CFG-19 though the matrix records it FAIL on r14-harm

`tests/fixtures/r15-census-config.py:161-165` lists 15 harm-fail ids; the matrix's r14-harm arm fails
16 (adds `R15CFG-19`, detail "store: contract: synthetic store path in output"). The table is
metadata only (emitted at `:1555`; the case functions carry the oracle), and the checker's
`HARM_FAILS` correctly includes 19 via `CONFIG_SAFETY_IDS`, so nothing misbehaves. But the
wave-1 phrase "r14-harm fails every `HARM_CASES` id" is strictly weaker than observation, and the
table is the readable source a future re-pin would copy.

Verdict: **holds** functionally; documentation drift. Smallest fix: add `R15CFG-19` to `HARM_CASES`
(or note the different failure reason).

## Residual risk

- **Triple correlation is not independence.** The harness's literals, the checker's literals, and the
  matrix are three copies of the same measurement; the measurement itself is the fixture-under-test's
  case oracles. A misclassified case intent propagates to all three and no artifact in this set can
  detect it. The only independent leg is the hand-written expectations inside
  `tests/fixtures/r15-census-config.py`'s `case_*` functions, which I read for 03/05/08/14/18/19/20
  but did not exhaustively audit (another seat's scope).
- **Exit-value blindness** (F1) means a dishonest record can pair a refusal token with `exit=0` and
  still admit. The shipped record is honest; the format does not force it.
- The external harness exercises 6 of the checker's finding ids (`run-missing`, `baseline-not-red`,
  `case-status-unexpected`, `pinned-mismatch`, `snapshot_tampered`, plus the clean banner); the other
  ~14 rely on the checker's own selftest, which the harness only checks is fully green at some count.
- `want_status()` (`tests/fixtures/r15-preservation-evidence.py:139-146`) falls through to `PASS` for
  any arm name other than `baseline`/`baseline_preharm`; adding an arm without updating it would
  silently expect all-green. No current arm is affected.

## Verification gaps

- I did not execute `tools/souji-preservation-evidence.py --frozen` directly (outside ALLOWED-EXEC).
  `clean` is inferred from byte binding (record/expected digests, live file digests), the record's
  own arm counts (changed 0 fail, preharm 8, harm 16, ns 0/12), and the max harm detail length
  471 ≤ `MAX_DETAIL_CHARS` 512 (`tools/souji-preservation-evidence.py:296`, `:1514`).
- I did not mutate a copy of the fixture. Sensitivity of `external-clean` to each literal set is
  derived from `_expected_status`/`CONFIG_TOKEN_IDS`/`CONFIG_HARM_FAILS` code paths, not exercised.
- One probe (`jq -e` PASS-set assertion) returned `false` from a probe-side `.cases[]` vs
  `.cases | to_entries[]` indexing error; re-run correctly it returned `true`. It is not a lane
  finding, and the verbatim command is retained below.
- The census `--selftest` 38/38 and `bash -n`/shellcheck results were not re-run (matrix territory).

STATUS: ok

No tool installs or upgrades were performed; no files outside this report were written.

## Commands

Shell commands, in order (file reads used the `read` tool, not shell). `cd` prefixes are verbatim.

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '.arms | to_entries[] | .key as $a | .value | to_entries[] | select(.value|type=="object") | "\($a)\t\(.key)\trc=\(.value.rc // .value.exit // "?")\t\(.value.status // "")"' census/round-16/c1-matrix-final.json | head -60
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-preservation-evidence.py; echo "RC=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '.arms | to_entries[] | .key as $a | (.value["r15-config"].cases // .value.cases // {}) | to_entries[] | "\($a)\t\(.key)\t\(.value.verdict)\t\(.value.detail)"' census/round-16/c1-matrix-final.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat -- tests/fixtures/r15-preservation-evidence.py tools/souji-preservation-evidence.py census/round-16/ && echo "---HEAD---" && git show HEAD:tests/fixtures/r15-preservation-evidence.py | sed -n '30,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '.arms["changed"]["r15-config"] | keys' census/round-16/c1-matrix-final.json && echo "---" && jq -r '.arms["changed"]["r15-config"]' census/round-16/c1-matrix-final.json | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '.arms | to_entries[] | "ARM=\(.key) valid=\(.value.valid) rc=\(.value.rc) total=\(.value.total // "?") failed=\(.value.failed // "?") stderr_tail=\(.value.stderr_tail // "")"' census/round-16/c1-matrix-final.json && echo "=== r14-harm cases ===" && jq -r '.arms["r14-harm"].cases // {} | to_entries[] | "\(.key)\t\(.value.verdict)\t\(.value.detail)"' census/round-16/c1-matrix-final.json && echo "=== r15-baseline ===" && jq -r '.arms["r15-baseline"]' census/round-16/c1-matrix-final.json | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '.arms["changed"]["r14-namespace"], .arms["changed"]["selftest"], .arms["changed"]["bash_n"], .arms["changed"]["shellcheck_warning"]' census/round-16/c1-matrix-final.json | head -70
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '.arms["r14-harm"] | keys' census/round-16/c1-matrix-final.json && echo "=== r14-harm r15-config ===" && jq -r '.arms["r14-harm"]["r15-config"] | {valid,rc,total,failed,stderr_tail}' census/round-16/c1-matrix-final.json && jq -r '.arms["r14-harm"]["r15-config"].cases | to_entries[] | "\(.key)\t\(.value.verdict)\t\(.value.detail)"' census/round-16/c1-matrix-final.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '.arms["pre-harm"]["r15-config"] | {valid,rc,total,failed,stderr_tail}' census/round-16/c1-matrix-final.json && echo "=== r15-baseline arms ===" && jq -r '.arms["r15-baseline"] | {r15_config: .["r15-config"], selftest, shellcheck_warning}' census/round-16/c1-matrix-final.json | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-preservation-evidence.py census/round-16/c1-matrix-final.json census/round-16/c1-matrix-landing.json && echo "--- landing fixture digests ---" && jq -r '.fixtures_sha256, .lane_head, .fixtures_dirty' census/round-16/c1-matrix-landing.json 2>/dev/null | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "observed_finding\|observed_exit\|TOKEN\|detail\|finding" tools/souji-preservation-evidence.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tools/souji-preservation-evidence.py tests/fixtures/r15-census-config.py tests/fixtures/r15-preservation-frozen/regenerate.py 2>/dev/null && ls tests/fixtures/r15-preservation-frozen/ 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "HEAD fixture:" && git show HEAD:tests/fixtures/r15-census-config.py | sha256sum && git log --oneline -3 -- tests/fixtures/r15-census-config.py && echo "--- final top ---" && jq -r '{lane_head, changed, fixtures_dirty, fixtures_sha256}' census/round-16/c1-matrix-final.json && echo "--- landing top ---" && jq -r '{lane_head, changed, fixtures_dirty, fixtures_sha256}' census/round-16/c1-matrix-landing.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "LANDING changed:" && jq -r '.arms["changed"]["r15-config"].cases | to_entries[] | "\(.key)\t\(.value.verdict)\t\(.value.detail)"' census/round-16/c1-matrix-landing.json && echo "LANDING pre-harm fails:" && jq -r '[.arms["pre-harm"]["r15-config"].cases | to_entries[] | select(.value.verdict=="FAIL") | .key] | join(",")' census/round-16/c1-matrix-landing.json && echo "LANDING r14-harm fails:" && jq -r '[.arms["r14-harm"]["r15-config"].cases | to_entries[] | select(.value.verdict=="FAIL") | .key] | join(",")' census/round-16/c1-matrix-landing.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "R15CFG-20\|R15CFG-03\|R15CFG-14\|R15CFG-05\|R15CFG-08\|R15CFG-18" tests/fixtures/r15-census-config.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "HARM_EXPECT\|PREHARM\|CLASSES\|cls\b\|expected" tests/fixtures/r15-census-config.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "case-status-unexpected\|case-finding-mismatch\|baseline-not-red\|REASON_TOKENS\|CONFIG_TOKEN_IDS\|CONFIG_HARM_FAILS\|CONFIG_PRESERVE_PREHARM" tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "HARM_CASES" tests/fixtures/r15-census-config.py && echo "--- diff 0a70bef..c6207bd fixture ---" && git diff 0a70bef c6207bd -- tests/fixtures/r15-census-config.py | head -40 && echo "--- sha at 0a70bef ---" && git show 0a70bef:tests/fixtures/r15-census-config.py | sha256sum && echo "--- sha at c6207bd ---" && git show c6207bd:tests/fixtures/r15-census-config.py | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "observed_exit" tools/souji-preservation-evidence.py; echo "--- tool digest ---"; sha256sum tools/souji-census.sh; jq -r '.arms["changed"].sha256, .arms["pre-harm"].sha256, .arms["r14-harm"].sha256' census/round-16/c1-matrix-final.json; echo "--- fixture frozen block lines ---"; grep -n "frozen-lane\|frozen_files\|frozen-tampered\|match.group(2) < 1\|selftest: " tests/fixtures/r15-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && cat tests/fixtures/r15-preservation-frozen/README.md; echo "=== expected.json ==="; jq -r '.' tests/fixtures/r15-preservation-frozen/expected.json | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "selftest\|checks" census/round-16/run-matrix.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tests/fixtures/r15-preservation-frozen/record.json && jq -r '{measured_commit, changed_tool: .runs.changed.tool, ns_tool: .namespace_controls.tool, fixture: .fixture, ns_fixture: .namespace_fixture}' tests/fixtures/r15-preservation-frozen/record.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '.arms["r15-baseline"] | {bash_n, r15_config: .["r15-config"]} | {bash_n_rc: .bash_n.rc, valid: .r15_config.valid, rc: .r15_config.rc, total: .r15_config.total, failed: .r15_config.failed, stderr_tail: .r15_config.stderr_tail}' census/round-16/c1-matrix-final.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '{changed: ([.runs.changed.cases[] | select(.status=="fail")] | length), preharm: ([.runs.baseline_preharm.cases[] | select(.status=="fail")] | length), harm: ([.runs.baseline.cases[] | select(.status=="fail")] | length), ns: ([.namespace_controls.cases[] | select(.status=="fail")] | length), ns_total: (.namespace_controls.cases|length)}' tests/fixtures/r15-preservation-frozen/record.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -e --argjson pre '["R15CFG-02","R15CFG-11","R15CFG-17","R15CFG-03","R15CFG-08","R15CFG-14","R15CFG-18","R15CFG-19"]' '([.arms["pre-harm"]["r15-config"].cases | to_entries[] | select(.value.verdict=="FAIL") | .key] | sort) == ($pre | sort)' census/round-16/c1-matrix-final.json && jq -e --argjson harm '["R15CFG-01","R15CFG-04","R15CFG-06","R15CFG-07","R15CFG-09","R15CFG-10","R15CFG-12","R15CFG-13","R15CFG-15","R15CFG-16","R15CFG-20","R15CFG-03","R15CFG-08","R15CFG-14","R15CFG-18","R15CFG-19"]' '([.arms["r14-harm"]["r15-config"].cases | to_entries[] | select(.value.verdict=="FAIL") | .key] | sort) == ($harm | sort)' census/round-16/c1-matrix-final.json && jq -e '[.arms["changed"]["r15-config"].cases[] | .verdict] | unique == ["PASS"]' census/round-16/c1-matrix-final.json && jq -e '.arms["changed"]["r15-config"].total == 20 and .arms["changed"]["r15-config"].failed == 0' census/round-16/c1-matrix-final.json && jq -e '([.arms["r14-harm"]["r15-config"].cases[] | select(.verdict=="PASS") | .key] | sort) == (["R15CFG-02","R15CFG-05","R15CFG-11","R15CFG-17"] | sort)' census/round-16/c1-matrix-final.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -3 && echo "--- landing ancestor? ---" && git merge-base --is-ancestor 7a79dc2d6e282654b9379c391c4c6be985ccf92c HEAD && echo "7a79dc2 is ancestor of HEAD" || echo "NOT ancestor"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -r '[.arms["r14-harm"]["r15-config"].cases | to_entries[] | select(.value.verdict=="PASS") | .key] | join(",")' census/round-16/c1-matrix-final.json && echo "--- counts ---" && jq -r '.arms["r14-harm"]["r15-config"] | {total, failed, ncases: (.cases|length)}' census/round-16/c1-matrix-final.json && jq -r '[.arms["r14-harm"]["r15-config"].cases | to_entries[] | .value.verdict] | group_by(.) | map({verdict: .[0], n: length})' census/round-16/c1-matrix-final.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -c '[.arms["r14-harm"]["r15-config"].cases | to_entries[] | select(.value.verdict=="PASS") | .key] | sort' census/round-16/c1-matrix-final.json && jq -c '["R15CFG-02","R15CFG-05","R15CFG-11","R15CFG-17"] | sort' --null-input && jq -n -c '[["R15CFG-02","R15CFG-05","R15CFG-11","R15CFG-17"] | sort]'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -e '([.arms["r14-harm"]["r15-config"].cases | to_entries[] | select(.value.verdict=="PASS") | .key] | sort) == (["R15CFG-02","R15CFG-05","R15CFG-11","R15CFG-17"] | sort)' census/round-16/c1-matrix-final.json && jq -e '([.arms["pre-harm"]["r15-config"].cases | to_entries[] | select(.value.verdict=="PASS") | .key] | sort) == (["R15CFG-01","R15CFG-04","R15CFG-05","R15CFG-06","R15CFG-07","R15CFG-09","R15CFG-10","R15CFG-12","R15CFG-13","R15CFG-15","R15CFG-16","R15CFG-20"] | sort)' census/round-16/c1-matrix-final.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "selftest:" tools/souji-census.sh | head -10; echo "--- fixture anchors ---"; grep -n "^BENIGN\|^REFUSAL\|^SAFETY\|^PRESERVE\|^TOKEN\|^NS =\|^IDS =\|^PREHARM_FAILS\|^HARM_FAILS\|^def detail\|^def arm\|^def want_status\|^def build_record" tests/fixtures/r15-preservation-evidence.py; echo "--- README anchors ---"; grep -n "snapshot_tampered\|pre-integration\|clean" tests/fixtures/r15-preservation-frozen/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "passed" tools/souji-census.sh | head; echo "---"; sed -n '1826,1846p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '104,116p;139,160p;205,225p' tests/fixtures/r15-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "benign   (01\|refusal  (02\|safety   (08\|preserve (05\|Expected per-case status\|CONFIG_BENIGN_IDS / CONFIG_REFUSAL_IDS" tools/souji-preservation-evidence.py; echo "--- impl anchors ---"; grep -n "def _expected_status\|def _eval_arm\|token = re.search\|if cid in refusal_ids\|REASON_TOKENS = " tools/souji-preservation-evidence.py; echo "--- readonly lines ---"; sed -n '6,13p' tests/fixtures/r15-preservation-frozen/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && jq -n --slurpfile f census/round-16/c1-matrix-final.json --slurpfile l census/round-16/c1-matrix-landing.json '{changed_cases_equal: (($f[0].arms.changed["r15-config"].cases|tostring)==($l[0].arms.changed["r15-config"].cases|tostring)), preharm_cases_equal: (($f[0].arms["pre-harm"]["r15-config"].cases|tostring)==($l[0].arms["pre-harm"]["r15-config"].cases|tostring)), harm_cases_equal: (($f[0].arms["r14-harm"]["r15-config"].cases|tostring)==($l[0].arms["r14-harm"]["r15-config"].cases|tostring)), ns_cases_equal: (($f[0].arms.changed["r14-namespace"].cases|tostring)==($l[0].arms.changed["r14-namespace"].cases|tostring))}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "MAX_DETAIL_CHARS" tools/souji-preservation-evidence.py && jq -r '[.runs.baseline.cases[] | {id, n: (.detail|length)}] | (max_by(.n)), (map(.n)|max)' tests/fixtures/r15-preservation-frozen/record.json && jq -r '[.runs.changed.cases[] | select(.id=="R15CFG-03" or .id=="R15CFG-14" or .id=="R15CFG-20" or .id=="R15CFG-02") | {id, status, detail}]' tests/fixtures/r15-preservation-frozen/record.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "CONFIG_BENIGN_IDS = \|CONFIG_REFUSAL_IDS = \|CONFIG_SAFETY_IDS = \|CONFIG_PRESERVE_PREHARM = \|CONFIG_HARM_FAILS = \|CONFIG_TOKEN_IDS = \|Round-16 L1 re-pin" tools/souji-preservation-evidence.py && wc -l tools/souji-preservation-evidence.py && jq -r '.runs.baseline_preharm.cases | map(select(.status=="fail")) | length' tests/fixtures/r15-preservation-frozen/record.json
```
