# W2C3Rerun — C3 after-state rerun + all-receipt tip/base verify table

## Status
STATUS: PARTIAL. C3's frozen counter and kill rule both hold, but one new run/verify asymmetry is falsified outside the frozen cases.

- The frozen counter and the kill rule survive. The tip runner scores `cases=8 pass=8 refusals=2/2 regress=5/5` (exit 0); the base runner scores `refusals=0/2`.
- Every `receipt=v1` file in the lane was checked. None is refused by the tip but accepted by the base.
- The amendment-1 symmetry clause is FALSIFIED outside the frozen cases. The tip `run` exits 0 and writes receipts that the tip `verify` refuses as RECEIPT-MALFORMED. The trigger is any argv element `--token=X` or `password=X`, which the base `run` wrote as a parseable `cmd=`. See Finding 1.

## Evidence
Environment:
- Clone: `/var/tmp/souji-r24-W2C3Rerun/lane` (`git clone --no-hardlinks` of the lane, detached at `ca7fc1cb6dd1333096c6f3bdbad304686691d126`).
- Lane master has since moved to `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`. That commit only adds `.ufo/waves/round-24/w1/*` and no new receipt.
- Versions: git 2.56.0, Python 3.14.8.
- Base runner: `git show a65fac98…:tools/souji-receipt-run.py`, sha256 `e13d0c83…`. Tip runner sha256 `9df0738c…`.

Commands and results:

1. Tip runner. Command: `python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py --lane-root .`
   - Result: `cases=8 pass=8 refusals=2/2 regress=5/5`, exit 0.
   - Case a returned RECEIPT-REV-NOT-DURABLE for both the no-ref commit and the commit held only by `refs/jj/keep/r24-fixture`.
   - Case b returned RECEIPT-TOOL-NOT-IN-ARGV for both the absent path and the substring-only path.
2. Base runner. Command: `python3 -B tests/fixtures/r24-receipt-verify.py --tool /var/tmp/souji-r24-W2C3Rerun/base-runner.py --lane-root .`
   - Result: `cases=8 pass=6 refusals=0/2 regress=5/5`, exit 1.
   - Cases a and b returned `verify=ok`. This matches the control claim.
3. All-receipt table. The receipt list comes from `grep -rl '^receipt=v1' census/` at ca7fc1c (14 files).
   - Each receipt was verified with `<runner> verify --root <R> <receipt>` for both runners.
   - R was the clone, and also the live lane root (verify only reads, via `for-each-ref`/`cat-file`).
   - The durable ref sets are equivalent: the lane has heads master, hyaku/s3-ready66-souji and souji-r20-* plus origin/master; the clone holds the same tips under refs/remotes/origin.

| receipt | rev | tool | tip@clone | base@clone | tip@lane | base@lane |
|---|---|---|---|---|---|---|
| census/round-23/records/agreement-after.tsv | eb1aa49783ae | tools/souji-record-agreement.py | ok | ok | ok | ok |
| census/round-23/records/declared-evidence-after.tsv | 9301d98c1c68 | tools/souji-declared-evidence.py | ok | ok | ok | ok |
| census/round-23/records/gate-check-at-first-landing.tsv | a211e4d1bf6e | tools/souji-gate-check.py | ok | ok | ok | ok |
| census/round-23/records/gate-check-at-lane-base.tsv | 1208bfb4924d | tools/souji-gate-check.py | ok | ok | ok | ok |
| census/round-23/records/gate-check-c3.tsv | 476525026cdb | tools/souji-gate-check.py | ok | ok | ok | ok |
| census/round-24/records/c1-after.tsv | 778747eb671f | tests/fixtures/r24-size-census.py | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT |
| census/round-24/records/c1-control-stub.tsv | 1efe406e7f39 | tests/fixtures/r24-size-census.py | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT |
| census/round-24/records/c2-after.tsv | 778747eb671f | tools/souji-coverage-agreement.py | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT |
| census/round-24/records/c2-control-base.tsv | 1efe406e7f39 | tools/souji-coverage-agreement.py | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT |
| census/round-24/records/c2-fixture-after.tsv | 778747eb671f | tests/fixtures/r24-coverage-agreement.py | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT |
| census/round-24/records/c3-after.tsv | 778747eb671f | tests/fixtures/r24-receipt-verify.py | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT |
| census/round-24/records/c3-control-base-runner.tsv | 1efe406e7f39 | tests/fixtures/r24-receipt-verify.py | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT |
| census/round-24/records/gate-check-r24-entry.tsv | 778747eb671f | tools/souji-gate-check.py | ok | ok | ok | ok |
| census/round-24/records/r13-recheck-receipt.tsv | 778747eb671f | tests/fixtures/r13-repo-structure.sh | ok | rc=2 RECEIPT-COUNTS-ABSENT | ok | rc=2 RECEIPT-COUNTS-ABSENT |

Reading the table:
- The tip refuses 0 receipts that the base accepted.
- The base refuses 8 receipts. Each has a round-24 counts line that the base `COUNTS_RE` lacks; the amendment-1 widening adds them (intended). These are base-only refusals, not C3 harms.
- History scan: `git rev-list --all` × `git grep -l '^receipt=v1' -- census` finds exactly these 14 paths. No receipt was ever deleted.
- One `receipt=v1` file sits outside `census/`: `.ufo/waves/round-23/records/stale-digest-demo.tsv`. It is an intentional negative demo. Tip and base both return rc=2 RECEIPT-TOOL-DIGEST-MISMATCH, so its result is unchanged.

4. Synthetic argv-shape probe. Script: `/var/tmp/souji-r24-W2C3Rerun/probe.sh`, run against a scratch repo.
   - The tool prints an r23 counts line, `assertions=1 resolved=1 skipped=0 mismatches=0`, so both verifiers can accept it.
   - Each runner's `run` wrote a receipt for each shape. Both verifiers then checked every receipt.

| shape (argv after `--`) | writer | run rc | recorded `cmd=` | tip verify | base verify |
|---|---|---|---|---|---|
| `python3 tools/c.py` | tip / base | 0 / 0 | `python3 tools/c.py` | ok / ok | ok / ok |
| `python3 ./tools/c.py` | tip | 2 TOOL-NOT-IN-ARGV | — | — | — |
| `python3 ./tools/c.py` | base | 0 | `python3 ./tools/c.py` | rc=2 RECEIPT-TOOL-NOT-IN-ARGV | ok |
| `sh -c 'python3 tools/c.py'` | tip | 2 TOOL-NOT-IN-ARGV | — | — | — |
| `sh -c 'python3 tools/c.py'` | base | 0 | `sh -c 'python3 tools/c.py'` | rc=2 RECEIPT-TOOL-NOT-IN-ARGV | ok |
| `python3 tools/c.py --token=abc` | **tip** | **0** | `python3 tools/c.py '--token=[REDACTED]` | **rc=2 RECEIPT-MALFORMED** | ok |
| `python3 tools/c.py --token=abc` | base | 0 | `python3 tools/c.py --token=[REDACTED]` | ok | ok |
| `python3 tools/c.py password=abc` | **tip** | **0** | `python3 tools/c.py 'password=[REDACTED]` | **rc=2 RECEIPT-MALFORMED** | ok |
| `python3 tools/c.py password=abc` | base | 0 | `python3 tools/c.py password=[REDACTED]` | ok | ok |
| `python3 tools/c.py 'Authorization: Bearer abc'` | tip / base | 0 / 0 | `… 'Authorization: Bearer [REDACTED]` (both) | rc=2 RECEIPT-MALFORMED (both) | ok (both) |
| `python3 tools/c.py Authorization: Bearer abc` | tip / base | 0 / 0 | `… Authorization: Bearer [REDACTED]` | ok / ok | ok / ok |
| `python3 tools/c.py ghp_abcdef` | tip / base | 0 / 0 | tip `'[REDACTED]'`, base `[REDACTED]` | ok / ok | ok / ok |
| `python3 tools/c.py https://u:p@h/x` | tip / base | 0 / 0 | tip `'https://[REDACTED]@h/x'` | ok / ok | ok / ok |
| `python3 tools/c.py 'a b'` / `"it's"` | tip / base | 0 / 0 | quoted correctly | ok / ok | ok / ok |

Under the C3 counts line (`cases=1 pass=1`), the base verifier refuses every receipt with RECEIPT-COUNTS-ABSENT. That is why the table above uses the r23 counts line instead.

## Findings
1. **HIGH — the tip `run` writes receipts that the tip `verify` refuses. This is a new run-to-verify asymmetry for `--token=`/`password=` arguments.**
   - Location: `tools/souji-receipt-run.py:239`, which reads `f"cmd={redact(shlex.join([redact(a) for a in args.command]))}",`.
   - The redaction patterns involved are at `:79` (`(re.compile(r"(?i)(--token=)\S+"), r"\1[REDACTED]"),`) and `:82` (the same shape for `password=`).
   - Mechanism:
     1. Per-element redaction turns `--token=abc` into `--token=[REDACTED]`.
     2. `shlex.quote` must quote the `[` and `]`, giving `'--token=[REDACTED]'`.
     3. The second, whole-line `redact` matches `\S+` on `[REDACTED]'` and removes the closing quote.
     4. `verify` (`:300` `argv = shlex.split(header["cmd"])`, then `:302`) refuses the result as RECEIPT-MALFORMED.
   - The base `run` joined first, so `abc` stayed unquoted, and wrote a parseable `--token=[REDACTED]`. Both verifiers accept that.
   - So this is a regression created by the per-element remedy, not just the latent issue `w1/CritC3Value.md` finding 5 described. That finding concerns already-quoted arguments.
   - It contradicts amendment 1 line 39: "Symmetry made literal (the claim's title): `run` refuses TOOL-NOT-IN-ARGV and TOOL-PATH-REDACTED;". No `run` refusal guards this path; `run` exits 0.
   - The frozen counter cannot see it. Case c (`r24-receipt-verify.py:186`) runs one shape with no secret-shaped arguments.
   - No lane receipt is affected today: none of the 14 `cmd=` lines carries a secret-shaped argument.
   - Fix direction [INFERENCE, not run]: drop the outer `redact()` once elements are redacted, or have `run` self-check `shlex.split(cmd)` and refuse before writing.
2. **LOW, intended narrowing: the tip `verify` refuses base-written `./tools/x` and `sh -c '…'` receipts with RECEIPT-TOOL-NOT-IN-ARGV.**
   - These are the shapes `w1/CritC3Value.md` finding 4 named.
   - The tip `run` now refuses the same shapes, so run and verify are symmetric at the tip.
   - The docstring documents the narrowing (`./tools/x` does not match `tools/x`).
   - No lane receipt uses either shape, so the kill rule is not triggered.
3. **INFO: the single-element `'Authorization: Bearer X'` form is unparsable in both versions.**
   - Base `verify` never split `cmd=`, so it accepted the receipt; the tip refuses it as RECEIPT-MALFORMED.
   - This is the pre-existing latent issue that w1 named. The tip only makes it visible.
   - No lane receipt has this shape.
4. **INFO: the C3 kill rule is not triggered.**
   - All 5 r23 regression receipts and all 9 r24 receipts verify ok at the tip, against both the clone and the live lane root.

## Attack log
- Attack A: find a lane receipt that the tip refuses but the base accepted. Ran it on 14 census receipts plus 1 `.ufo` receipt, × 2 runners × 2 roots. Result: **survives** (0 cases).
- Attack B: check for receipts deleted from history that might hide a regression. Scanned `rev-list --all`. Result: **survives** (the path set is identical).
- Attack C: write receipts with the tip `run`, then verify them with the tip `verify`, over 11 argv shapes. Result: **falsified** for `--token=X`, `password=X` and `'Authorization: Bearer X'` (Finding 1).
- Attack D: verify base-written receipts with the tip, to separate intended from unintended refusals.
  - Refusals of `./` and `sh -c` are intended and symmetric (Finding 2).
  - The Bearer refusal is a pre-existing malformation (Finding 3).
- Writes: only this report. Scratch `/var/tmp/souji-r24-W2C3Rerun/` was removed before finishing. No tool installs.
