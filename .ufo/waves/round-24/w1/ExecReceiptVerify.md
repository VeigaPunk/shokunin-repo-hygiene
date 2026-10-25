# ExecReceiptVerify — round 24 wave 1, C3 (receipt verify/run symmetry)

## Status
STATUS: PASS — the patched copy refuses non-durable revs and labels that are not in argv. All five committed r23 receipts still give verify=ok against the lane root. Every input the base already refused keeps its exact refusal.

## Deliverables
- `.ufo/waves/round-24/w1/souji-receipt-run.py` — copy of `tools/souji-receipt-run.py`. Only `cmd_verify` and the docstring's verify refusal list are edited. sha256 `cbe96d734e54aa6c65707870c2a7ca6cec58fb8bcf07c9820eb27c049e5b543a`. Lane original: sha256 `e13d0c8352c9fbaa95c4dc2560b85d4aa9125c332a4e9240a5c0bc6e96f1121d`.
- `.ufo/waves/round-24/w1/souji-receipt-run.diff` — unified diff against the lane file (`diff -u`, labels `a/tools/souji-receipt-run.py` and `b/.ufo/waves/round-24/w1/souji-receipt-run.py`). sha256 `31026b412c183ce0bc415e4ce4568414f239d2e68b2944a85e0d8a40c952775d`. It has 2 hunks: +3/-1 in the docstring and +9 in `cmd_verify`.

## Behaviour
- (a) `RECEIPT-REV-NOT-DURABLE`, exit 2, when `durable_rev(root, rev)` is false. This is the same function `cmd_run` uses for `REV-NOT-DURABLE`: `for-each-ref --contains <rev> refs/heads refs/tags refs/remotes` must be non-empty, and `refs/jj/*` never counts.
- (b) `RECEIPT-TOOL-NOT-IN-ARGV`, exit 2, when the `tool=` value is not an exact element of `shlex.split(cmd)`.
  - `./tools/x` does NOT count for `tool=tools/x`. Neither does `--tool=tools/x`, nor any other prefix, suffix or path normalisation.
  - If `cmd=` cannot be split (shlex raises `ValueError`, e.g. an unbalanced quote that redaction can produce), the argv is treated as empty, so the receipt is refused with `RECEIPT-TOOL-NOT-IN-ARGV`.
- Ordering: both new checks run AFTER every existing refusal (malformed, rev-malformed, tool-absent, digest-mismatch, counts-absent) and just before `verify=ok`. So any input the base refused gets the same code, detail and exit code. Only inputs the base accepted can now be refused.
  - Consequence for the C3 fixture: case-a and case-b receipts must be valid in every other respect (tool present at rev, matching digest, a counts line). Otherwise an earlier refusal fires first.
  - An absent rev still gives `RECEIPT-TOOL-ABSENT`, not `RECEIPT-REV-NOT-DURABLE`. Unchanged from base.
- `run` and the output format are untouched. The success line is byte-identical.

## Evidence
Lane HEAD `f9db2181647d91470a724a12d626bd6106805076`, git 2.56.0, Python 3.14.8. Every lane read was read-only, and `git status --short` was identical before and after.

Regression (case d). Command: `python3 -B .ufo/waves/round-24/w1/souji-receipt-run.py verify --root /home/vgpnk/Projects/shokunin/souji-shokunin census/round-23/records/<n>.tsv`
```
-- declared-evidence-after
verify=ok rev=9301d98c1c689c79741f0f1ba1f171138d20af07 tool=tools/souji-declared-evidence.py tool_sha256=65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4
rc=0
-- gate-check-at-first-landing
verify=ok rev=a211e4d1bf6ea592670d16269f34e9f67f33e8b3 tool=tools/souji-gate-check.py tool_sha256=d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00
rc=0
-- gate-check-at-lane-base
verify=ok rev=1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd tool=tools/souji-gate-check.py tool_sha256=d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d
rc=0
-- gate-check-c3
verify=ok rev=476525026cdb179f2d49441e1cb6c6f7316f3124 tool=tools/souji-gate-check.py tool_sha256=d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d
rc=0
-- agreement-after
verify=ok rev=eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a tool=tools/souji-record-agreement.py tool_sha256=dd53c228b8cca68cfe6dd51630c4ed3473a7c20db36a0effcf5a18259049bb0f
rc=0
```
The base runner prints the same five lines, each with rc=0. The `tool=` value in every r23 receipt is a bare argv element of its `cmd=` (for example `cmd=python3 -B tools/souji-gate-check.py ...`).

Synthetic falsifiers. These ran in scratch `/var/tmp/souji-r24-ExecReceiptVerify/` (a git-init repo, `tools/t.py` printing `entries=1 ok=1 fail=0`). The scratch has been removed. The clean receipt was produced by the patched `run`. The variants were made by rewriting one header line each.
```
c    (run-produced)                 BASE rc=0 verify=ok   NEW rc=0 verify=ok
a    (commit-tree, no ref)          BASE rc=0 verify=ok   NEW rc=2 RECEIPT-REV-NOT-DURABLE
ajj  (pinned only refs/jj/keep/x)   BASE rc=0 verify=ok   NEW rc=2 RECEIPT-REV-NOT-DURABLE
b    (cmd=python3 -B other.py)      BASE rc=0 verify=ok   NEW rc=2 RECEIPT-TOOL-NOT-IN-ARGV
b2   (cmd=... ./tools/t.py)         BASE rc=0 verify=ok   NEW rc=2 RECEIPT-TOOL-NOT-IN-ARGV
b3   (unbalanced quote in cmd)      BASE rc=0 verify=ok   NEW rc=2 RECEIPT-TOOL-NOT-IN-ARGV
b4   (cmd=... --tool=tools/t.py)    BASE rc=0 verify=ok   NEW rc=2 RECEIPT-TOOL-NOT-IN-ARGV
abs  (rev absent from repo)         BASE rc=2 RECEIPT-TOOL-ABSENT          NEW rc=2 RECEIPT-TOOL-ABSENT
ndmm (non-durable + bad digest)     BASE rc=2 RECEIPT-TOOL-DIGEST-MISMATCH NEW rc=2 RECEIPT-TOOL-DIGEST-MISMATCH
```
On this sample, the base runner gives refusals=0/2 and the patched copy gives refusals=2/2. This is not the frozen counter `tests/fixtures/r24-receipt-verify.py`, which I did not run and which does not exist in my scope.

## Findings
1. No regression receipt was refused. All five r23 receipts give verify=ok under the patched copy (`census/round-23/records/*.tsv` at lane HEAD f9db2181).
2. Durability is evaluated against the lane's refs at verify time, not at receipt time. A receipt that verifies today becomes `RECEIPT-REV-NOT-DURABLE` if the branch, tag or remote ref containing its rev is later deleted or force-moved. `run` has the same time dependence, so this is symmetric by design. `[INFERENCE]` C3's regress=5/5 is only stable while those revs stay on `refs/heads/master` or another durable ref. Location: `.ufo/waves/round-24/w1/souji-receipt-run.py` in `cmd_verify` — "if not durable_rev(root, rev):".
3. The argv binding is lexical only. `tool=tools/x` with `cmd=python3 tools/x` passes even if argv[0] would not actually execute that file (e.g. `cmd=echo tools/x`). C3(b) only asks for "does not occur as an argv element", so this is within contract, but it is a residual the knowledge entry should state. Location: same function — "if tool not in argv:".
4. `./tools/x` is not accepted. Any future receipt recorded with a `./` prefix, or with `--tool=PATH`, will be refused. None of the five r23 receipts use either form.

## Tooling
No tools were installed or updated.
