# ScoutToolSHA256Counter — r25 w1: tool_sha256 grep counter → verify=ok count

## Status
STATUS: PASS — before numbers measured at both a6d2d15 (lane base) and 6e4737e (current HEAD, the prereg commit); every failure has a cause; replacement wording drafted and executed at both revisions. One attack is reported: the frozen C1 control receipt fails verify.

## Evidence
Revisions: lane base `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`; HEAD `6e4737eab43d8fde1b85eb9f57023d29046705b4` (`git log a6d2d15..HEAD` = one commit "round-25: freeze preregistration + base controls (before-data)"). `git diff --quiet a6d2d15 HEAD -- tools/` → identical. `tools/souji-receipt-run.py` sha256 `279a64739a12f6816392329fe3b9526b0e59cc3ab7b24188b95b1966e065e191` at both revisions. git 2.56.0. `census/` is clean against HEAD (`git diff --quiet HEAD -- census/`); the only untracked census path is `census/operator-sweep-20261019/`.

Commands run this session (all exit 0):
1. Literal r23 counter, run in the working tree at HEAD: `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` → **26**.
2. Base a6d2d15: each `git grep -lE … a6d2d15 -- census/` hit was extracted with `git show` into scratch, then `python3 -B tools/souji-receipt-run.py verify --root <lane> <extracted>` ran on each one, using the base blob of the runner (same sha256 as above). Result: **files=21 verify_ok=19**.
3. HEAD: the loop over the literal grep list runs `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-run.py verify --root /home/vgpnk/Projects/shokunin/souji-shokunin <receipt>`. Result: **files=26 verify_ok=23**.
4. Number of `git grep` hits under `census/` at each revision: 778747e=8, 315422b=15, 2e7efcf=21, a6d2d15=21, HEAD=26. The 315422b figure matches LOG.md:1700-1701: "now lists 15 files under census/, of which 14 verify=ok".

Before numbers:

| revision | grep hits | verify=ok | failing |
|---|---|---|---|
| a6d2d15 (base) | 21 | 19 | `census/round-24/size-census-lane.txt`, `census/round-24/records/r23-agreement-regress.out` |
| 6e4737e (HEAD) | 26 | 23 | the two above + `census/round-25/records/c1-control-base.tsv` |

The 19 files that verify ok at the base are 5 under `census/round-23/records/` (`agreement-after`, `declared-evidence-after`, `gate-check-at-first-landing`, `gate-check-at-lane-base`, `gate-check-c3`) and 14 under `census/round-24/records/` (`c1-after`, `c1-control-stub`, `c1-final`, `c2-after`, `c2-control-base`, `c2-final`, `c2-fixture-after`, `c2-fixture-final`, `c3-after`, `c3-control-base-runner`, `c3-final`, `gate-check-r24-entry`, `gate-final`, `r13-recheck-receipt`), all `.tsv`. HEAD adds 4 that verify ok: `census/round-25/records/{c2-control-base,c3-control-base,coverage-agreement-at-base,record-agreement-at-base}.tsv`, each with `rev=a6d2d15…`.

Verify output for the failures:
- `census/round-24/size-census-lane.txt` gives `rc=2 RECEIPT-MALFORMED header order or fences do not match receipt v1`.
- `census/round-24/records/r23-agreement-regress.out` gives `rc=2 RECEIPT-MALFORMED header order or fences do not match receipt v1`.
- `census/round-25/records/c1-control-base.tsv` (HEAD only) gives `rc=2 RECEIPT-COUNTS-ABSENT no stdout line starts with a counts line`.

## Findings
1. **size-census-lane.txt is a hand-shaped record, not a v1 receipt.** Line 1 is a `# lane-bound C1 measurement: …` comment, not `receipt=v1`. The file has no `receipt=` key. `rc=0` comes after the stdout block instead of between `cmd=` and `utc=`. There is no `--- stderr ---` fence. `parse_receipt` (`tools/souji-receipt-run.py:285-304`) requires all of these and returns None, which gives MALFORMED. The binding inside the file is still true: `git show 778747e:tools/souji-size-census.py | sha256sum` = `09bb8e0d…ed6d`, which equals the file's `tool_sha256=`, and 778747e is an ancestor of HEAD. Its stdout ends with a line that the counts regex accepts (`garbage=0 size_garbage=0 unreachable=1093 alternates=0`). It fails only on form. Re-receipting or relabelling it is SCORECARD.md:225 item "turn `census/round-24/size-census-lane.txt` into a v1 receipt or relabel it".
2. **r23-agreement-regress.out is not a receipt at all.** It is fixture selftest output (`selftest=12/12`, `control=FALSE-GREEN-REJECTED`) that begins `tool=/home/vgpnk/…/tools/souji-record-agreement.py` then `tool_sha256=41db9ca8…`. It has no `receipt=v1`, `rev=`, `cmd=` or fences, and the tool path is absolute. It matches the r23 grep only because its second line starts with `tool_sha256=` and has 64 hex characters. This is a false positive of the grep counter, and it shows directly why the grep count should be replaced. It was added by 2e7efcf, after the LOG.md:1700 "15/14" figure, which is why the base shows 21/19 rather than 15/14 + 6.
3. **c1-control-base.tsv (HEAD only) is a well-formed v1 receipt that verify refuses.** It is the C1 do-nothing control, and the prereg says "the current tool bytes at a6d2d15 reject --base-rev (rc 2; receipt census/round-25/records/c1-control-base.tsv)". Its stdout is empty, so `counts_line` returns None (`tools/souji-receipt-run.py:327-328`). See the Attack log.
4. **verify does not check `rc=`.** Three r24 controls with `rc=1` verify ok (`c1-control-stub`, `c2-control-base`, `c3-control-base-runner`). A verify=ok count therefore counts bound receipts, not passing runs. The wording below says this so the number is not read as "N green runs".
5. **The literal r23 counter reads untracked operator-sweep content.** `grep -r … census/` walks `census/operator-sweep-20261019/` (untracked; it returned 0 hits this run). The seat contract forbids "`census/operator-sweep-*` contents". The replacement uses `git grep`, which reads tracked files only, so the operator-sweep files are never read and the count is pinned to a revision.

## Proposed SCORECARD counter wording (draft; the L1 integrates)
Counter column, rev-pinned form: this is the one to use for before/after, and it was executed here at a6d2d15 (19/21) and 6e4737e (23/26):

> `receipts_verify_ok` at `<rev>`: for each path in `git grep -lE '^tool_sha256=[0-9a-f]{64}$' <rev> -- census/` (tracked files only), extract `git show <rev>:<path>` to /var/tmp scratch and run `python3 -B tools/souji-receipt-run.py verify --root . <extracted>`; counter = number of `verify=ok ` stdout lines; report alongside `grep_hits` (the denominator). A verify=ok receipt is blob-bound and well-formed; it says nothing about the recorded `rc=`.

Shell form for a clean tree at the tip (precondition: `git diff --quiet HEAD -- census/`). Executed at HEAD → `receipts_verify_ok=23 grep_hits=26`:

```bash
M=$(git grep -lE '^tool_sha256=[0-9a-f]{64}$' -- census/ | wc -l)
N=$(git grep -lzE '^tool_sha256=[0-9a-f]{64}$' -- census/ | xargs -0 -n1 python3 -B tools/souji-receipt-run.py verify --root . 2>/dev/null | grep -c '^verify=ok ')
echo "receipts_verify_ok=$N grep_hits=$M"
```

Before cell: `receipts_verify_ok=19 grep_hits=21` at a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe. The failures are size-census-lane.txt and r23-agreement-regress.out, both RECEIPT-MALFORMED. For reference, the value at 6e4737e is `23 of 26`; the third failure there is c1-control-base.tsv, RECEIPT-COUNTS-ABSENT.

## Attack log
- **A1 (calibration; run/verify asymmetry; the frozen C1 control receipt is unverifiable).** `cmd_run` writes a receipt whatever the stdout is (`tools/souji-receipt-run.py:263-282`), and prints `counts=none` when there is no counts line. `cmd_verify` refuses that same receipt with RECEIPT-COUNTS-ABSENT (`:327-328`). Docstring `:35-36` says "so every receipt `run` writes parses under `verify`". That holds for parsing only, not for verifying ok. As a result, `census/round-25/records/c1-control-base.tsv`, the receipt the prereg names for C1's before-control, does not reach verify=ok, and any receipt counter excludes it. It has the receipt v1 header order of `run` output, so it was written by `run` [INFERENCE]. This is not a request to change C1. It is a run/verify symmetry shape for D1's "remaining run/verify symmetry shapes as future counter cases" list, and a disclosure for the counter: refusal controls with empty stdout can never be counted.
- **A2 (gameability of the old counter).** Any file with a line `tool_sha256=<64 hex>` raises the r23 grep count. `r23-agreement-regress.out` is a live example. The verify=ok count closes that gap only for files that also bind rev, tool blob, counts line, durable ref and argv. Replacing the counter is warranted.

## Tooling / scratch
No installs. Scratch: `/var/tmp/souji-r25-ScoutToolSHA256Counter/`, removed at finish. No lane writes except this report; no git or jj mutation.
