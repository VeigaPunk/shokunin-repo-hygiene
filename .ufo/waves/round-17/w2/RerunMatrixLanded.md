STATUS: DONE — rerun of the C1 counting command at ddb7347 reproduces every context number and every L1 c1-matrix.json verdict; zero differences; one minor ungated-surface observation on the runner itself.

# RerunMatrixLanded — C1 counting-command attack (round 17, wave 2)

Seat: SoujiR17-3.RerunMatrixLanded-2 (leaf, no subagents). All commands read-only except the
single ALLOWED-EXEC matrix run writing under /var/tmp/souji-r17-RerunMatrixLanded/ (deleted afterwards;
report is the only lane write). No `jj`, no git writes, no census/verify/vault/quarantine run against
any real directory.

## Precondition checks (identity of the rerun vs L1's landed-rev record)

- `sha256sum census/round-17/run-matrix.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-census-config.py tests/fixtures/r17-census-hygiene.py`
  → `2a46ae127ea8…` / `e6a984b1…` / `27474396…` / `136b0e49…` — byte-identical to `runner_sha256` and
  `fixtures_sha256` recorded in census/round-17/c1-matrix.json. `git status --porcelain` over those four
  paths: empty. So my rerun executed the exact bytes L1's record was produced from.
- Both records: `lane_head` = `git_head` = `d7e648d5a193…`, `changed_rev` = `ddb73474433…`,
  `fixtures_dirty` = `""`, `allow_dirty_fixtures` = false, `fixture_dir` = null, `invalid_suites` = [],
  env identical (git 2.56.0, bash 5.3.20(1), python 3.14.8, shellcheck 0.11.0).

## The ALLOWED-EXEC run

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 census/round-17/run-matrix.py \
  --changed ddb73474433977ff54b015ac3e77669ff2537353 --output /var/tmp/souji-r17-RerunMatrixLanded/m.json
```
rc=0, wall 616.6 s. Runner's own tally (verbatim):
```
pre-harm	6a000c59fe74	bash-n=0	sc=0	selftest=36/0fail	r17-hygiene=26/20fail	r15-config=20/8fail	r14-namespace=12/10fail
r14-harm	fcff8b057b3e	bash-n=0	sc=0	selftest=38/0fail	r17-hygiene=26/13fail	r15-config=20/16fail	r14-namespace=12/0fail
r16	64a60fd0b0ed	bash-n=0	sc=0	selftest=38/0fail	r17-hygiene=26/13fail	r15-config=20/0fail	r14-namespace=12/0fail
changed	688ff8ad684b	bash-n=0	sc=0	selftest=49/0fail	r17-hygiene=26/0fail	r15-config=20/0fail	r14-namespace=12/0fail
```

## Comparison 1 — rerun vs context claim: HOLDS (zero diffs)

Context numbers (pre-harm hygiene 26/20, r15-config 20/8, ns 12/10, selftest 36/0; r14-harm 26/13,
20/16, 12/0, 38/0; r16 26/13, 20/0, 12/0, 38/0; changed 26/0, 20/0, 12/0, 49/0; bash -n and
shellcheck -S warning clean every arm) — all reproduced exactly, including `bash_n.rc=0`,
`shellcheck_warning.rc=0 findings=0`, `selftest.failed=0` in every arm.

## Comparison 2 — rerun vs L1 census/round-17/c1-matrix.json: HOLDS (zero diffs)

- Per-arm totals, failed, rc, `valid`, selftest (checks/failed), bash_n, shellcheck: identical, all 4 arms × 3 suites.
- All 232 per-case verdicts (26+20+12 cases × 4 arms) identical, case-id sets identical.
- Extracted census bytes per arm: sha256 identical (changed arm `688ff8ad684b970d…` = c1-matrix's value).

## Comparison 3 — L1 c1-matrix.json vs context (run before the rerun): HOLDS (zero diffs)

Same comparator, m.json absent → no DIFF lines.

## Observed nondeterminism (not a verdict difference; informational)

24 of 232 case `detail` strings differ between the two records; every one is run-local randomness
inside fixture free text: wall-clock timestamps the hygiene fixture stamps into rows
(e.g. `2026-10-20T14:25:00-03:00` → `15:02:54-03:00`) and the fixture's own `mkdtemp` scratch name
echoed in census error text (`/var/tmp/r17-census-hygiene.2w8_88ty` → `.ge3cvtqn`). Timestamp- and
scratch-normalized details are equal (truncation-aware check at 250 chars). `stderr_tail` identical
in 12/12 suites. So the JSON records are verdict/summary-reproducible, not byte-reproducible —
expected fixture behavior, no action needed.

## Finding 1 (minor, runner hardening — not a landed-claim defect)

`census/round-17/run-matrix.py:233-235` (at ddb7347): `invalid_suites` is computed over `suite_keys`
only (line 189), so `bash_n`, `shellcheck_warning` and `selftest` are recorded as data with no
validity gate — e.g. a `--selftest` crash (rc=1) or an unparseable selftest line
(`checks: null`, possible per lines 216-218) would still exit 0 with `invalid_suites: []`. The
docstring's exit-code contract ("0 … every suite valid") is not violated, and both landed records
happen to be clean (selftest rc=0 everywhere, checks are ints), so no landed evidence is wrong.
Smallest fix: extend the invalid list with arm entries when `arm["bash_n"]["rc"] != 0`,
`arm["shellcheck_warning"]["findings"] != 0`, or `arm["selftest"]["rc"] != 0 or
arm["selftest"]["checks"] is None` (one extra comprehension term each; keeps schema 2 additive or
bumps to 3 if L1 wants the distinction recorded).
Verdict: holds-as-landed, partial-as-contract — advisory only.

## Verdict

C1's counting command is reproducible at ddb7347: every arm total, every one of the 232 per-case
verdicts, and every runner meta field match both the context numbers and L1's
census/round-17/c1-matrix.json. No counterexample found. Scratch dir /var/tmp/souji-r17-RerunMatrixLanded/
removed after the report was written. No tools installed (none needed; pacman guard respected).
