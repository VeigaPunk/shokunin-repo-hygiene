# SwarmExecutor17 — no-harm sweep, half B (round 32, attempt 2, wave a2w1)

## Status

STATUS: PARTIAL — the assigned sweep is complete: 41 executed comparisons (the 27 C2 argv plus 14 of
my 15 half-B rows, the fifteenth unrun for a stated contract reason) each ran at both revisions
(base `85b61a151923986e7e6b48f7084b9122561b5f3d`, tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`),
40 identical on (rc, last digit-bearing line), 1 benign difference, every difference classified below.
The sweep's own claim holds; the lane tip does not hold the same conclusion outside the enumerated set:
three committed gate surfaces are red at the tip, in one shared class — consumers keyed to the bytes C2
edited — namely `souji-preservation-evidence --frozen` rc 2, `r22-result-oracle` rc 1 (2 of 258 cases)
with `r22-mutation-adequacy` rc 1 cascading from it, plus two classes of dangling pointer in
`souji-landing-gate`. The two pinned-byte surfaces and the `../` pointers are being repaired in the L1
worktree; none is in my write scope. 14 of 15 half-B rows executed; row 16 was not executed under the
lane's "no live /proc census" clause.

## Evidence

Runner: private `git clone -q --no-local --no-checkout <lane> <scratch>/<tag>`, `remote remove origin`,
`git -C <clone> rev-parse --show-toplevel` asserted equal to the clone, then per item
`checkout -qf --detach <rev>` + `clean -fdxq`, cwd = clone root, `TMPDIR` a fresh scratch directory,
no sandbox (bwrap/strace not used), `env -u GIT_DIR -u GIT_WORK_TREE`. Comparator is the frozen C2
counter's S: the last digit-bearing line of normalized stdout (stderr when stdout has none), with
scratch and tmp paths → `<TMP>`, 12+ hex → `<HEX>`, `N.Ns` → `<DUR>`.
Scratch `/fast/scratch/hyaku/souji-r32/NoHarmB` (199 MB peak, removed after this report was written).

### Enumeration (partition agreed with the half-A seat, SwarmExecutor16-3)

Rule (both halves, so the split is disjoint): backticked spans in the SKILL.md gate registry
(self-test command column) and the SCORECARD.md capability rows that start with `bash`/`python3`
after stripping leading `TMPDIR=<v> `/`SOUJI_CLI_BIN=<v> ` prefixes; drop spans carrying `<...>`,
`…` or ALL-CAPS placeholder tokens and `--output`/`--work`/`--json`/`--base-tool`/`--base` or an
external base blob; reduce `[--opt ...]`-only spans to the bare default invocation; dedupe;
`LC_ALL=C` sort. Universe 30 rows, halves 1–15 (half A, not mine) and 16–30 (mine).

| row | command | half | my run |
|---|---|---|---|
| 1 | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` | A | not mine |
| 2 | `bash tests/fixtures/r13-quarantine-bounds.sh` | A | not mine |
| 3 | `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` | A | not mine |
| 4 | `bash tests/fixtures/r30-jj-keep-expiry.sh` | A | not mine |
| 5 | `bash tests/fixtures/r31-jj-object-clock.sh` | A | not mine |
| 6 | `bash tests/fixtures/r32-jj-mtime-clock.sh` | A | not mine |
| 7 | `bash tools/souji-proc-census.sh --selftest` | A | not mine (half-A lists it unexecuted) |
| 8 | `bash tools/souji-quarantine.sh --selftest` | A | not mine |
| 9 | `bash tools/souji-vault-verify.sh --selftest` | A | not mine |
| 10 | `python3 -B census/round-22/mutation-adequacy.py` | A | not mine |
| 11 | `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py` | A | not mine |
| 12 | `python3 -B tests/fixtures/r29-registry-agreement.py` | A | not mine |
| 13 | `python3 -B tools/souji-record-contract.py --record census/round-31/records/jj-object-clock-run.txt --contract census/round-32/m1-r31-contract.txt` | A | not mine |
| 14 | `python3 -m py_compile census/round-17/run-matrix.py` | A | not mine |
| 15 | `python3 census/round-17/transcript-manifest.py --check census/round-16/transcripts` | A | not mine |
| 16 | `python3 census/round-18/leak-count.py --selftest` | B | NOT executed: reads live `/proc` of its own children (`census/round-18/leak-count.py:241`, `:266`) and hard-codes `/var/tmp` at `:327`; declined under the lane contract's "no live /proc census" clause, the same reading the half-A seat took for `souji-proc-census.sh --selftest` |
| 17 | `python3 census/round-19/probe-carry-invariants.py` | B | ran |
| 18 | `python3 census/round-19/verify-agreement-pin.py --selftest` | B | ran |
| 19 | `python3 tests/fixtures/r13-cert-evidence.py` | B | ran |
| 20 | `python3 tests/fixtures/r14-census-boundary.py` | B | ran |
| 21 | `python3 tests/fixtures/r14-evidence-cache.py` | B | ran |
| 22 | `python3 tests/fixtures/r15-census-config.py` | B | ran |
| 23 | `python3 tests/fixtures/r15-preservation-evidence.py` | B | ran |
| 24 | `python3 tests/fixtures/r16-landing-gate.py` | B | ran |
| 25 | `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` | B | ran |
| 26 | `python3 tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` | B | ran |
| 27 | `python3 tests/fixtures/r19-carry-wrap.py` | B | ran |
| 28 | `python3 tests/fixtures/r19-rev-pin.py` | B | ran |
| 29 | `python3 tests/fixtures/r19-seat-audit-shapes.py` | B | ran |
| 30 | `python3 tests/fixtures/r21-read-render-edges.py --tool tools/souji-seat-audit.py` | B | ran |

Out of the universe by the rule (each dropped for a placeholder/optional-only span, an external base
blob or C2 membership): the 27 C2 items themselves (run separately below), `souji-verify`,
`souji-vault-verify`, `souji-quarantine --dry-run`, `souji-census --root DIR`, `souji-repo-structure`,
`souji-rev-pin --root`, `souji-seat-audit --spec`, `souji-preservation-evidence --root/--record`,
`souji-cert-evidence --root/--manifest`, `souji-evidence-cache --root/--record`,
`souji-record-contract --record/--contract`, `souji-registry-agreement --root`,
`souji-capability-agreement`, `souji-capability-cells`, `souji-pre-report-gate`,
`souji-wave-evidence-capture`, `souji-landing-gate --root/--rev/--round`, `r17-jj-receipts --tool-dir DIR`,
`r18-proc-census --tool`, `r18-census-bounded --census`, `r17-census-hygiene --census PATH`,
`r21-read-root`/`r21-reason-canary`/`r21-replay-boundaries`/`r21-source-head`/`r21-source-refs`
(external base blobs), `r19-carry-wrap --base-rev`, `r20-input-binding` (its `--baseline` form is C2
item T18), `r22-mutation-adequacy --oracle`, `round-17/18/21` runners, `transcript-manifest --check DIR`,
`census/round-29/c2-counter`, `census/round-32/c2-counter`.

### Half B, 14 executed rows — base vs tip, run normally

Command: `python3 -B runner.py --rev-a 85b61a1… --rev-b 4e56c48… --set halfB-set.tsv --out halfB.json`
(last line `SUMMARY items=14 same=14 diff=0`, 262 s).

| id | base rc:line | tip rc:line | verdict |
|---|---|---|---|
| B17 | rc0 `SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0` | same | same |
| B18 | rc0 `SUMMARY total=5 failed=0` | same | same |
| B19 | rc0 `fixture: 5/5 checks passed` | same | same |
| B20 | rc0 `SUMMARY total=12 failed=0` | same | same |
| B21 | rc0 `fixture: 22/22 checks passed` | same | same |
| B22 | rc0 `SUMMARY total=20 failed=0` | same | same |
| B23 | rc0 `fixture: 8/8 checks passed` | same | same; does not cover finding 1 (see F5) |
| B24 | rc0 `SUMMARY total=15 failed=0` | same | same |
| B25 | rc0 `SUMMARY total=29 failed=0` | same | same |
| B26 | rc0 `SUMMARY total=11 failed=0` | same | same |
| B27 | rc0 `SUMMARY total=4 failed=0 base_discriminating=2` | same | same |
| B28 | rc0 `SUMMARY total=13 failed=0 base_discriminating=6` | same | same |
| B29 | rc0 `SUMMARY total=17 failed=0 base_discriminating=12` | same | same |
| B30 | rc0 `SUMMARY total=4 pass=4 fail=0` | same | same |

### The 27 C2 items, run normally (no bwrap, no strace)

Command: `python3 -B runner.py … --set c2-set.tsv --out c2-all.json` over
`census/round-32/c2-items.tsv` argv verbatim (last line `SUMMARY items=27 same=26 diff=1`, 144 s).

| id | base rc:line | tip rc:line | verdict |
|---|---|---|---|
| T01 | rc0 `SELFTEST pass=65 fail=0` | same | same |
| T02 | rc0 `SUMMARY findings=0 checked_reg=65 … checked_reports=114` | same | same |
| T03 | rc1 `assertions=252 resolved=229 skipped=401 mismatches=23` | rc1 `assertions=252 resolved=229 skipped=401 mismatches=23` | same |
| T04 | rc0 `selftest=8/8` | same | same |
| T05 | rc0 `selftest=9/9` | same | same |
| T06 | rc0 `SUMMARY total=11 failed=0` | same | same |
| T07 | rc0 `selftest: 36/36 passed` | same | same |
| T08 | rc0 `selftest: 48/48 passed` | same | same |
| T09 | rc0 `selftest: 47/47 passed` | same | same |
| T10 | rc0 `SELFTEST pass=118 fail=0` | same | same |
| T11 | rc0 `selftest=PASS ids=7/7` | same | same |
| T12 | rc0 `selftest: 69 checks, 0 failed` | same | same |
| T15 | rc0 `selftest: 49 checks, 0 failed` | same | same |
| T16 | rc0 `selftest=8/8` | same | same |
| T17 | rc0 `SUMMARY total=66 pass=66 fail=0 base_discriminating=0` | same | same |
| T18 | rc0 `SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=26` | rc0 `… baseline_mismatches=32` | DIFF — benign, F4 |
| T19 | rc0 `cases=8 pass=8 refusals=2/2 regress=5/5` | same | same |
| T20 | rc0 `selftest=15/15` | same | same |
| T21 | rc0 `cases=9 pass=9 control=FALSE-GREEN-REJECTED` | same | same |
| T22 | rc0 `cases=16 pass=16 control=FALSE-GREEN-REJECTED` | same | same |
| T23 | rc0 `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | same | same |
| T24 | rc0 `cases=1 pass=1` | same | same |
| T25 | rc0 `cases=12 pass=12 control=FALSE-GREEN-REJECTED` | same | same |
| T26 | rc0 `cases=4 pass=4 control=FALSE-GREEN-REJECTED` | same | same |
| T27 | rc0 `cases=15 pass=15 control=TAMPER-REJECTED` | same | same |
| T29 | rc0 `cases=7 pass=7 control=FALSE-GREEN-REJECTED` | same | same |
| T30 | rc0 `cases=10 pass=10 control=FALSE-GREEN-REJECTED` | same | same |

T18 drift, attributed (one clone, `checkout --detach` per commit, same argv):
`85b61a1 → baseline_mismatches=26`, `98e5203 (C2) → 31`, `a92e1aa (C3) → 32`,
`9e8982b (C1) → 32`, `4e56c48 (tip) → 32`; rc 0 at every commit.

### Required command 1 — declared evidence at the tip

`python3 -B tools/souji-declared-evidence.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 4e56c48b8fc828f9aba2746e324dc46aa538bdbf`
→ `assertions=259 resolved=236 skipped=404 mismatches=23`, rc 1.
Base control (`--rev 85b61a1…`): `assertions=252 resolved=229 skipped=401 mismatches=23`, rc 1.
Verdict histogram, identical both ends (`--format tsv`, awk column 4): `229 resolved`,
`19 mismatch:path-absent`, `2 mismatch:rev-unresolved`, `2 mismatch:digest` at base;
`236 resolved`, same 19/2/2 at tip. No delta: the 23 mismatches are pre-existing, not a regression.

### Required command 2 — landing gate at the tip

`python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 4e56c48b8fc828f9aba2746e324dc46aa538bdbf --round 32 --fleet-root /home/vgpnk/Projects/shokunin`

```
LG-DANGLING-PTR	../census/round-32/records/jj-mtime-clock-run.txt	SKILL.md:155 cites path absent at 4e56c48b8fc8
LG-DANGLING-PTR	../tests/fixtures/r32-jj-mtime-clock.sh	SKILL.md:156 cites path absent at 4e56c48b8fc8
LG-DANGLING-PTR	.ufo/waves/round-32/w1/deliver-jj-mtime-clock-run.txt	corpus/knowledge/jj-abandoned-object-mtime-clock.md:4 cites path absent at 4e56c48b8fc8
LG-FROZEN-PIN	tests/fixtures/r15-preservation-frozen/expected.json	files[tools/souji-census.sh] pinned 21c19ff620ad92c2 but tools/souji-census.sh hashes c1671f4c5ef9d45c
SUMMARY	findings=4	checked_reg=68	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-32/ or census/round-32/waves/ at 4e56c48b8fc828f9aba2746e324dc46aa538bdbf
```
rc 2 (the rc 2 comes from the COULD-NOT-EVALUATE; the four findings would otherwise make it 1).
Base control on the same tool, round 31 (C2 item T02): `findings=0` at both base and tip.

### Frozen pin, directly probed (the discriminating measurement)

`python3 -B tools/souji-preservation-evidence.py --root . --frozen tests/fixtures/r15-preservation-frozen`
in a clone at each revision with `TMPDIR` under scratch:
base `85b61a1` → `measured_commit: 005f3d376e…`, `frozen_files: 3`, rc 0;
tip `4e56c48` → `souji-preservation-evidence: could-not-evaluate`,
`finding snapshot_tampered: 'tools/souji-census.sh': pinned=21c19ff620ad92c2… observed=c1671f4c5ef9d45c…`, rc 2.

### The two r22 surfaces keyed to `tools/souji-evidence-cache.py` (reproduced here, same root cause)

Both commands run in one clone at the base, at `98e5203` and at the tip, then at the tip with only
`tools/souji-evidence-cache.py` restored to its base bytes.

`python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py`:
base rc 0, `results total 258 fail 0`; `98e5203` rc 1; tip rc 1, `results total 258 fail 2`, failing
`positive/clean-cache-demonstration` and `positive/cache-transient-path-and-time`
(`observed: false`); tip with base tool bytes restored: rc 0.

`python3 -B census/round-22/mutation-adequacy.py`:
base rc 0, `killed=52 survived=7` `disagreeing_with_expect: []`, `pristine {'exit': 0, 'fail': 0, 'pass': 258}`;
tip rc 1, `killed=59 survived=0`, `pristine {'exit': 1, 'fail': 2, 'pass': 256}`,
`disagreeing_with_expect: ['nonexact-keyin-get','failed-checks-to-eq','names-len-constant','phases-len-constant','baseline-guard-pass','checks-len-drop','caserows-len-drop']`,
each of those seven `expect equivalent observed killed oracle_exit 1`; tip with base tool bytes
restored: rc 0 and the base summary exactly.

Mechanism: the r21 summarizer recomputes the live digest
`gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))`
(`census/round-21/run-acceptance.py:503`) and requires the frozen cache-demonstration payload's
`gate.sha256` to equal it (`:522`), so the frozen public receipt carries the base digest and C2's edit
breaks it; the mutation arm then reads every mutant's `oracle_exit` as 1 against the red pristine.
Attribution: `git log --oneline 85b61a1..4e56c48 -- tools/souji-evidence-cache.py` prints `98e5203` alone.
This is the half-A seat's H1/H2, independently reproduced here.

## Findings

1. **HARM (committed gate red at the tip): C2's `tools/souji-census.sh` edit left the r15 preservation
   frozen pin stale.** `tests/fixtures/r15-preservation-frozen/expected.json` still pins
   `21c19ff620ad92c26df15550f473158d887a1bba0967e9e2686cf1b5d0f21629` (base bytes) while the tip
   tool hashes `c1671f4c5ef9d45cf483cf12787103ecb60aae8a5f4059425dc4da1feb79b114`; the same old digest
   appears 4× in `tests/fixtures/r15-preservation-frozen/record.json`. Cause is commit `98e5203`
   (C2), the only commit in `85b61a1..4e56c48` touching the tool: `git log --oneline 85b61a1..4e56c48 --
   tools/souji-census.sh` prints it alone, and its diff replaces
   `CENSUS_TMP=$(mktemp -d /var/tmp/souji-census-now.XXXXXX)` with the `${TMPDIR:-/tmp}` form at
   `tools/souji-census.sh:306` and `:1876`. Consequences measured: the gate
   `souji-preservation-evidence --frozen` goes rc 0 → rc 2 (`snapshot_tampered`) and the landing gate
   at round 32 adds `LG-FROZEN-PIN` (evidence above). The L1 already has `expected.json` and
   `record.json` modified in the worktree with the new digest (4 × `c1671f4c…` in `record.json`,
   1 × in `expected.json`); that repair is uncommitted and is not evidence.
2. **HARM (durable dangling pointer): the C3 knowledge entry cites a gitignored path.**
   `corpus/knowledge/jj-abandoned-object-mtime-clock.md:4` says the run record "is the fixture seat's
   delivery `.ufo/waves/round-32/w1/deliver-jj-mtime-clock-run.txt`". `.gitignore:1` is `.ufo/waves/`,
   so `git check-ignore -v` confirms the path is ignored and it is absent at every revision — the
   landing gate's `LG-DANGLING-PTR` for it can never clear, capture or no capture. The committed
   record `census/round-32/records/jj-mtime-clock-run.txt` (present at the tip) is the citable path;
   SKILL.md already uses it.
3. **HARM (doc pointer prefix): two `../`-prefixed pointers in the gate registry.** At the tip,
   `SKILL.md:155` reads `record ../census/round-32/records/jj-mtime-clock-run.txt, fixture` and
   `SKILL.md:156` reads `../tests/fixtures/r32-jj-mtime-clock.sh`. Both targets exist repo-root-relative
   at the tip, so this is a prefix defect, not a missing file: the gate resolves the `../` form outside
   the lane and reports two `LG-DANGLING-PTR`. Introduced by `a92e1aa`:
   `git log -S'../census/round-32/records/jj-mtime-clock-run.txt' 85b61a1..4e56c48 -- SKILL.md`
   returns that commit alone. The L1 worktree already drops both prefixes (uncommitted).
4. **BENIGN (instrument drift, already disclosed): C2 item T18.** `r20-input-binding.py --baseline
   12516f7d…` keeps rc 0 and `total=52 pass=52 fail=0`; only its `baseline_mismatches` counter moves
   26 → 31 at `98e5203`, 32 at `a92e1aa`, 32 at the tip. The counter counts closure files that differ
   from the pinned 2026-10-21 revision, so any landing in the round moves it; the frozen C2 predicate
   requires exact equality and therefore cannot hold (recorded in
   `census/round-32/records/amendments.txt`: "C2 reads 26 of 27 PASS"). Lane behaviour is unchanged:
   the tool's own verdict and exit code are identical.
5. **Observation (why the enumerated sweep alone would have missed finding 1).** The committed fixture
   `tests/fixtures/r15-preservation-evidence.py` accepts any of rc 0/1/2 for its shipped-pin arm
   (`if proc.returncode not in (0, 1, 2): problems.append(...)`), so its `8/8` at the tip is a
   shape check, not a pin check; and the registry's `--frozen DIR` entry form is excluded from the
   enumerated universe by the placeholder rule. The discriminating command is the tool's `--frozen`
   mode directly (measured above). Any no-harm claim built only on the enumerated set is therefore
   blind to this class.
6. **Observation: the declared-evidence exit 1 is pre-existing.** rc 1 and `mismatches=23` at both
   revisions with an identical class histogram (19 path-absent, 2 rev-unresolved, 2 digest); the
   growth `252→259` assertions and `229→236` resolved is SCORECARD rows added this round, not a
   regression. Not attributable to C2/C3 by this measurement.
7. **Observation: process residue in `/var/tmp` is not mine.** At 10:06 -03 four directories existed
   (`souji-census-now.eNCN3t`, `souji-census-selftest.Tsmc5B`, `souji-r29-c1-fixture`,
   `souji-r29-wave-capture-fixture`), empty and mtime-current while concurrent seats ran the same
   fixtures; my runs cleaned up and I removed nothing I did not create.
8. **HARM (same class as F1, second edited file): C2's `tools/souji-evidence-cache.py` edit turns two
   committed r22 gates red at the tip, and neither is refreshed.** Cause is `98e5203` alone
   (`git log --oneline 85b61a1..4e56c48 -- tools/souji-evidence-cache.py`), whose diff only moves the
   selftest scratch to `tempfile.mkdtemp(prefix=…)` and stops forcing the child `TMPDIR=/var/tmp`.
   Measured: `r22-result-oracle` rc 0 → rc 1 with exactly two failing cases
   (`positive/clean-cache-demonstration`, `positive/cache-transient-path-and-time`), and
   `r22-mutation-adequacy` rc 0 `killed=52 survived=7` → rc 1 `killed=59 survived=0` whose seven
   `disagreeing_with_expect` entries are all `expect equivalent observed killed oracle_exit 1` — a
   cascade of the red pristine arm (`pass: 256`, `fail: 2`), not seven independent findings. Location
   of the coupling: `census/round-21/run-acceptance.py:503` recomputes the live digest of
   `tools/souji-evidence-cache.py` and `:522` requires the frozen payload's `gate.sha256` to equal it —
   byte identity of the whole file, so any edit to that tool breaks those two positives
   deterministically, not only a TMPDIR change. The frozen 27-item C2 set cannot see it: C2 item T08
   (`souji-evidence-cache.py --selftest`) is `selftest: 48/48 passed` on both sides (table above).
   Counterfactual at the tip: restoring only that file's base bytes returns both commands to their
   base summaries (rc 0, `fail 0`; rc 0, `killed=52 survived=7`, `disagreeing_with_expect: []`).
   With F1 this fixes the class: every red surface at the tip is a consumer keyed to bytes C2 edited,
   so the C2 landing is not verdict-neutral and its repair must be a re-pin/re-capture decision by the
   L1, not a re-run. The half-A seat reached the same result independently; both measurements agree.

## Attack log

Premise attacked: "C2's 26-file TMPDIR edit changed no committed gate verdict, and the lane's
committed self-test/fixture commands behave identically at base and at the tip". Attacks executed:

- A1 — every self-contained, non-C2 command in the two named doc surfaces (half B, 14 executed, plus
  row 16 declined under the `/proc` clause), run at both revisions in throwaway clones: 14/14
  identical on (rc, last digit-bearing line). No counterexample inside the set.
- A2 — the 27 frozen C2 argv themselves, run unsandboxed at both revisions: 26/27 identical; the one
  difference (T18) is a drift-prone anchor line, not behaviour (F4).
- A3 — outside the set, aimed at the gate that consumes the files C2 edited:
  `souji-preservation-evidence --frozen` at both revisions. COUNTEREXAMPLE: rc 0 → rc 2, pinned
  21c19ff6… vs observed c1671f4c… (F1). The premise is false; the C2 landing is not verdict-neutral.
- A4 — pointer resolution of every path the C3 landing cites at the tip: three `LG-DANGLING-PTR`
  (F2, F3). One is structurally unresolvable because `.ufo/waves/` is gitignored.
- A5 — SCORECARD assertion re-derivation at both ends (`souji-declared-evidence`): same 23 mismatches,
  same classes. No counterexample.
- A6 — the two r22 surfaces that read the edited tool's live bytes, at the base, at `98e5203` and at
  the tip, with a restore-only counterfactual at the tip: COUNTEREXAMPLE twice. `r22-result-oracle`
  rc 0 → rc 1 (2/258 cases) and `r22-mutation-adequacy` rc 0 → rc 1 (`killed=59 survived=0`, seven
  `expect equivalent` mutants reading killed off a red pristine); restoring
  `tools/souji-evidence-cache.py`'s base bytes alone returns both to green (F8). This is the half-A
  seat's H1/H2 reproduced independently.

No claim, predicate or counter was proposed for change. The three red surfaces at the tip are
consumers keyed to bytes C2 edited (values the frozen predicates of C1/C2/C3 do not read), not counter
defects: the C2 counter's own item set is green on 26 of 27 because it compares summaries, and the
r15 fixture's shipped-pin arm tolerates rc 2 by design (F5).

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmExecutor17.md` (this report). No delivery files; no lane writes
  other than this report; no git/jj mutation; no subagents. Tooling: nothing installed or upgraded
  (no pacman, no `uv`/`npx`); scratch `/fast/scratch/hyaku/souji-r32/NoHarmB` removed after writing.
