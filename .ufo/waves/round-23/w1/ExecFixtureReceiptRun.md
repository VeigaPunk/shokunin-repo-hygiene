## Status
STATUS: PASS — fixture delivered at `.ufo/waves/round-23/w1/r23-receipt-run.py` (549 lines, mode 755, sha256 `f8c5d217e96ab1ea1943f885041c35396184a941c593d33e1366f939c39d7ef2`); `selftest=8/8` against `tools/souji-receipt-run.py` (sha256 `1ec9b2fe851c02a0f881d4eeb07d7a2cc94d1e7e254201fcb57aa7aad9ddfecf`, 11666 B, mtime 05:17) and 12/12 mutants of a compliant reference runner caught, so the 8/8 is not vacuous. No predicate, target or key set was edited.

## Evidence

Lane revision: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (`git rev-parse HEAD`). The fixture is written into that untracked tree; nothing was staged or committed.

Final run (the one run to paste), from `/var/tmp`:

```
$ python3 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-23/w1/r23-receipt-run.py \
    /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-run.py
runner=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-run.py
case=1 expect=<rc=0 + receipt written + v1 header order + rc=0 + stdout present + rc=3 recorded as 3> got=<rc=0 header=v1/7 sha256=a62c58548f91... stdout=assertions=4 resolved=3 skipped=1 mismatches=0 label=two ... rc_probe=3>
case=2 expect=<verify rc=0> got=<rc=0 codes=->
case=3 expect=<old receipt still valid at its own rev after the mutation commit; stale digest at the new rev -> RECEIPT-TOOL-DIGEST-MISMATCH> got=<old_at_rev1=rc0 stale_at_rev2=rc2/RECEIPT-TOOL-DIGEST-MISMATCH>
case=4 expect=<rev=<branch> and rev=<7hex> both refused with RECEIPT-* code, no file written> got=<branch:rc=2/RECEIPT-REV-MALFORMED short7:rc=2/RECEIPT-REV-MALFORMED>
case=5 expect=<tool absent at rev refused with RECEIPT-* code> got=<rc=2 codes=RECEIPT-TOOL-ABSENT>
case=6 expect=<run with --out under /tmp refused (Q4), nothing written there> got=<rc=2 codes=OUT-UNDER-TMP wrote_under_tmp=False>
case=7 expect=<git status --porcelain empty before and after run> got=<before=empty after=empty runner_rc=0>
case=8 expect=<same tool_sha256 + same cmd, different utc> got=<sha_equal=True cmd_equal=True utc_equal=False utc=[2026-10-25T08:22:17Z, 2026-10-25T08:22:18Z]>
selftest=8/8
EXIT=0
```

Repeat run and no-argument discovery (walk up from `__file__`, so the `tests/fixtures/` copy resolves the same runner):

```
$ python3 .ufo/waves/round-23/w1/r23-receipt-run.py          # cwd = lane root, no argv
selftest=8/8
$ python3 .../r23-receipt-run.py <reference-runner>          # portability, not runner-specific
selftest=8/8
```

Control — 12 mutants of a compliant reference runner (each must make the fixture fail):

```
mutant=M1 verify-always-ok        caught=True rc=1 selftest=7/8 targets=3 (digest never checked)
mutant=M2 verify-reads-worktree   caught=True rc=1 selftest=6/8 targets=3a (bound rev not immutable)
mutant=M3 no-rev-guard-at-all     caught=True rc=1 selftest=7/8 targets=4 (branch/7-char accepted)
mutant=M4 no-tmp-out-guard        caught=True rc=1 selftest=7/8 targets=6 (writes under /tmp)
mutant=M5 run-writes-into-repo    caught=True rc=1 selftest=7/8 targets=7 (target repo modified)
mutant=M6 fixed-utc               caught=True rc=1 selftest=7/8 targets=8 (utc constant)
mutant=M7 drops-stdout            caught=True rc=1 selftest=7/8 targets=1 (stdout missing)
mutant=M8 header-order-swap       caught=True rc=1 selftest=7/8 targets=1 (header order)
mutant=M9 cmd-unquoted            caught=True rc=1 selftest=7/8 targets=1 (cmd not shell-quoted)
mutant=M10 no-tool-absent-code    caught=True rc=1 selftest=7/8 targets=5 (refusal without code)
mutant=M11 verify-writes-sidecar  caught=True rc=1 selftest=7/8 targets=4 (verify wrote an output file)
mutant=M12 run-ignores-rc         caught=True rc=1 selftest=7/8 targets=1 (rc not the real exit code)
mutation-control=caught 12/12
```

Hygiene: `/var/tmp/souji-r23-ExecFixtureReceiptRun/` (reference runner, mutation harness, probes) removed; no `/var/tmp/souji-r23-receipt-*`, `/var/tmp/souji-receipt-*` or `/tmp/souji-r23-should-not-exist-*` left behind; `git status --porcelain` in the lane shows no path this seat created beyond the untracked wave dir. No tool installed or upgraded (stdlib only: `hashlib`, `shlex`, `subprocess`, `tempfile`).

## Findings

1. **Case 3 as worded is unsatisfiable for a correct verifier, and the fixture splits it (ATTACK, §Attack log).** The fixture implements 3a + 3b instead of the literal "old receipt fails after a new commit": `old_at_rev1=rc0` and `stale_at_rev2=rc2/RECEIPT-TOOL-DIGEST-MISMATCH`. Location: fixture `case3()` (`.ufo/waves/round-23/w1/r23-receipt-run.py:340-376`) against the runner's verify body (`tools/souji-receipt-run.py:176-197`).

2. **`redact()` destroys the receipt's line structure, contradicting the runner's own `<verbatim>` contract.** `CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")` matches `\n` and `\t`, so `redact()` replaces every newline with a space before the body is written. Location: `tools/souji-receipt-run.py:73` (regex), `:76-81` (`redact`), `:203-206` (applied to stdout/stderr) versus the docstring's `<verbatim>` at `:23` and `:25`. Observed: a two-line counter output lands in the receipt as one physical line — `assertions=4 resolved=3 skipped=1 mismatches=0 label=two words`. Operability consequence: a multi-line output whose last line is a counts line is byte-indistinguishable from a single fabricated counts line, so the receipt cannot be used to show *which* line carried the counts. The fixture therefore matches stdout by presence with whitespace collapsed (`.ufo/waves/round-23/w1/r23-receipt-run.py:305-310`) rather than requiring layout, and still fails a runner that drops the output (M7).

3. **`COUNTS_RE` rejects the C1 instrument's own counts line.** The guard accepts `assertions=/resolved=/skipped=/mismatches=` or `entries=/ok=/fail=` only (`tools/souji-receipt-run.py:36-40`, enforced at `:193-194`), so a receipt for `tools/souji-record-agreement.py`, whose frozen counts line is `keys=K records=R occurrences=O mismatches=M`, would be refused with `RECEIPT-COUNTS-ABSENT`. The four C2 target receipts (declared-evidence before/after, gate-check before/after) are covered by the two accepted alternatives, so the C2 target is reachable — but the round's own C1 instrument cannot be receipt-bound. Not fixed here (runner is the L1's file); reported for the L1 to decide.

4. **First fixture draft was vacuous on case 7 and the control caught it.** The fixture's own `git add -A` swept a repo-dirtying runner's droppings into the next commit, so case 7 saw a clean tree (mutant M5 survived at 8/8). Fixed: commits now stage explicit pathspecs (`Ctx.commit(..., paths=...)`, `.ufo/waves/round-23/w1/r23-receipt-run.py:170-178`), and M5 is caught.

5. **A hard-coded `rc=0` was invisible to the specified case 1** (mutant M12 survived). Closed by an rc-fidelity probe inside case 1: the same rev is also run through the counter with `--fail 3`, and the receipt must record `rc=3` (`.ufo/waves/round-23/w1/r23-receipt-run.py:311-322`). Case count stays 8. Coupling note: a future runner that refuses to *write* a receipt for a non-zero exit code will fail this probe — that is intended, since the v1 header requires `rc=<int>`.

6. **Runner discovery is path-based, not cwd-based**, so the copy the L1 places at `tests/fixtures/r23-receipt-run.py` needs no argument and no env (`find_runner()`, `.ufo/waves/round-23/w1/r23-receipt-run.py:491-509`; verified from the lane root and from `/var/tmp`). `SOUJI_RECEIPT_RUN` overrides; an explicit argv[1] wins.

7. **Refusal codes are matched generically** (`[A-Z][A-Z0-9]*-[A-Z0-9][A-Z0-9-]*`, fixture `:66-70`) except case 3, which requires the literal `RECEIPT-TOOL-DIGEST-MISMATCH`. Observed runner spellings: run-side `REV-MALFORMED`, `OUT-UNDER-TMP` (no `RECEIPT-` prefix), verify-side `RECEIPT-REV-MALFORMED`, `RECEIPT-TOOL-ABSENT`, `RECEIPT-TOOL-DIGEST-MISMATCH`. The fixture therefore binds behaviour, not the runner's spelling — and would still fail a refusal with no code at all (M10).

## Attack log

**Attack: the ticket's case-3 predicate is false for any verifier the C2 claim allows.** Case 3 asks that after the tool is mutated in a NEW commit, `verify` on the OLD receipt (whose `rev=` names the pre-mutation commit) exit nonzero. A commit is immutable: the blob at the named rev is unchanged by a later commit, so a blob-bound verifier must still exit 0. Measured directly in a throw-away repo:

```
A=97ac9057... B=cc2b2081...
blob@A=98752ee28d5484bd blob@B=7b519d327803fabd   # A's blob identical before and after B
```

The only way to make the literal case fire is to have `verify` compare the recorded digest against the working tree or `HEAD` instead of the named revision — which is precisely what C2's kill rule forbids ("a receipt whose verify exits 0 while its tool bytes at rev differ from the recorded digest kills the claim") and what the C2 counter target breaks: the four receipts committed under `census/` must stay verifiable after the round's later commits. So the literal predicate would force a wrong runner.

The fixture keeps the *defect* case 3 exists for (spot-check D3: the digest was recorded out of band and the tool blob moved) by splitting into two sub-checks that a correct verifier passes and a worktree-comparing one fails: **3a** the old receipt still verifies at its own rev after the mutation commit (immutability — fails the worktree mutant M2), **3b** the same old digest re-filed against the NEW rev is refused with `RECEIPT-TOOL-DIGEST-MISMATCH` (the stale-digest shape — fails M1). No preregistration predicate was edited; if the L1 wants the literal wording instead, the runner must stop being blob-bound and C2 dies with it.

Second, smaller attack, on finding 3: `COUNTS_RE` is narrower than the lane's own counters, so the guard admits the census and gate-check receipts but silently excludes `tools/souji-record-agreement.py`. That is an operability limit of the runner, not of the fixture.
