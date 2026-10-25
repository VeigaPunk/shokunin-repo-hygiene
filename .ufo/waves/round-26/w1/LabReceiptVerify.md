# LabReceiptVerify — r26 red-before receipt probe

## Status

STATUS: FAIL — 3 of the 4 committed red-before receipts refuse `verify`
(`RECEIPT-COUNTS-ABSENT`): c1-before, c2-before, c3-before. Only c2-k4-base is `verify=ok`.
Each receipt's *payload* is nonetheless byte-identical to a fresh `run` at its recorded rev, so the
measured numbers stand; the frozen prereg's clause "each `verify=ok`" (preregistration.txt:65, :144)
is unearned for those three. Verified against committed blobs at HEAD `ea0bbe66c974062984134bb5b491b21bbb3c17d7`
(and identically at `d6c13b0`, `89e0fce`).

## Evidence

Scratch: `/var/tmp/souji-r26-LabReceiptVerify/` (removed after). All lane reads used absolute paths.
No tool installed or upgraded this run.

### 1. The assigned probe command is not a valid invocation

`verify` has no `--rev` (`tools/souji-receipt-run.py:349-353`: only `--root` + positional receipt;
rev comes from the receipt header) and no `--label` (`run` flags are `--root --rev --tool --out`):

```
$ python3 -B tools/souji-receipt-run.py verify --root . --rev 12fd90bcd9cdfab495e178023eeaa838a977fcbe census/round-26/records/c1-before.tsv
souji-receipt-run.py: error: unrecognized arguments: --rev census/round-26/records/c1-before.tsv
exit=2            # same for c2-before, c3-before, c2-k4-base
```

### 2. verify results, per receipt, on the committed blobs

```
$ for f in c1-before c2-before c3-before c2-k4-base; do git show ea0bbe6:census/round-26/records/$f.tsv > /var/tmp/.../$f.tsv; \
  python3 -B tools/souji-receipt-run.py verify --root . /var/tmp/.../$f.tsv; echo "  exit=$?"; done
c1-before: RECEIPT-COUNTS-ABSENT	no stdout line starts with a counts line      exit=2
c2-before: RECEIPT-COUNTS-ABSENT	no stdout line starts with a counts line      exit=2
c3-before: RECEIPT-COUNTS-ABSENT	no stdout line starts with a counts line      exit=2
c2-k4-base: verify=ok rev=0eca7c8a5d10bcbfdae50d0c390d277deec63bfd tool=tools/souji-coverage-agreement.py tool_sha256=bb506469...12f27f   exit=0
```

Same four verdicts when run against the blobs committed at the amendment-1 commit
`89e0fceeefcf28db313c94120be6d25e03c60094`.

### 3. Byte-consistency with what the runner emits at those revs — CONFIRMED

tool digests (`tool_sha256` == `git show <rev>:<tool> | sha256sum`):

```
git show 12fd90b:census/round-26/c1-counter.sh | sha256sum   c8dbb76cc4495b814ba0ad6bf24298f8d3f3977069e0ce70c319a1130c16bf5a   (= receipt)
git show 89e0fce:census/round-26/c2-counter.sh | sha256sum   e3f7a67703cb9060427cb61de87f4fcb7007da27e7fb1d536cd7c2292251bd9d   (= receipt)
git show 89e0fce:census/round-26/c3-counter.sh | sha256sum   7d40f5d8e32c5c9ab8b5485eaccff408355286c4a1ad1c90dac92b34ef34835d   (= receipt)
git show 0eca7c8:tools/souji-coverage-agreement.py | sha256sum bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f (= receipt)
```

Counter payloads re-run from `git archive <rev> SCORECARD.md corpus census/round-26 tools .ufo/waves/round-26`:

```
markers=2 / headings=17 175 231        (c1-counter @12fd90b, rc=0)
grounded_f1=0 / registry_rows=127      (c2-counter @89e0fce, rc=0)
axis_check_tool=absent                 (c3-counter @89e0fce, rc=0)
```

Byte compare against each receipt's stdout section: `stdout_bytes_equal=True`, `stderr_empty=True`
for all three (30/30, 31/31, 22/22 chars). c2-k4-base payload reproduced by re-running its exact
recorded command at base: `grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, exit 0.

Runner-emitted equivalents (`run` mode, output under /var/tmp):

```
run c1 @12fd90b -> rc=0 counts=none
run c2 @89e0fce -> rc=0 counts=none
run c3 @89e0fce -> rc=0 counts=none
```

`diff <(grep -v '^utc=' committed) <(grep -v '^utc=' emitted)` -> BODY IDENTICAL for all three.

### 4. Revisions / durability

`12fd90b`, `89e0fce`, `0eca7c8` are each reachable from `refs/heads/master` (durable predicate ok).
Receipt blobs unchanged across the tips I sampled: c1-before `7a79f66e…`, c2-before `7a3ff9f3…`,
c3-before `b83501f8…`, c2-k4-base `f9876935…` (same sha256 at `d6c13b0` and `ea0bbe6`).
Runner blob identical across the whole range: `12fd90b:tools/souji-receipt-run.py` == `HEAD:…` ==
`85d5f7bdba897ee16bd34e00e0e592bc0eea5ed7`.

## Findings

1. **`verify=ok` is false for three of the four red-before receipts.**
   c1-before, c2-before, c3-before → `RECEIPT-COUNTS-ABSENT` (exit 2); c2-k4-base → `verify=ok`.
   Location: `census/round-26/records/{c1-before,c2-before,c3-before,c2-k4-base}.tsv` against
   `tools/souji-receipt-run.py` (`cmd_verify`, counts gate) and the frozen assertion at
   `.ufo/waves/round-26/preregistration.txt:65` and `:144`.

2. **Root cause: `run` does not enforce the counts shape that `verify` requires.**
   `COUNTS_RE` (`tools/souji-receipt-run.py:67-75`) admits only 7 literal shapes (`assertions=`,
   `keys=`, `entries=`, `grounded=`, `cases=`, `garbage=`, `selftest=`). The r26 counters print
   `markers=/headings=`, `grounded_f1=/registry_rows=`, `axis_check_tool=`, none of which match.
   `cmd_run` writes the receipt and prints `counts=none`; `cmd_verify` then refuses it. This is a
   run/verify asymmetry, not receipt damage. Prior rounds emitted COUNTS_RE-shaped lines
   (`census/round-25/records/c3-after.tsv`: `selftest=PASS ids=7/7`;
   `census/round-24.md:117` records the same refusal class) — r26 is a regression against that
   convention.

3. **Not a post-hoc tightening.** The runner blob is byte-identical from `12fd90b` to HEAD, and
   running `verify` with the `12fd90b` runner copy gives the same `RECEIPT-COUNTS-ABSENT` on the
   committed c1-before. These receipts cannot have verified at emission time either; the prereg
   line asserts a check that, on this tool, could not pass.

4. **Payload content is sound and reproducible.** Counter stdout, rc, cmd, tool digest and durability
   all reproduce exactly from the recorded revs; the emitted bodies differ from the committed files
   only in `utc=`. The measured red values (C1 `markers=2` `headings=17 175 231`; C2 `grounded_f1=0`
   `registry_rows=127`; C3 `axis_check_tool=absent`; K4 base `grounded=7 …kill_violations=0`) are
   correct as measurements. The defect is the verification-status claim, not the numbers.

5. **The same defect hits the green-side receipts** (observed while checking the set):
   `c1-after.tsv`, `c2-after.tsv`, `c3-after.tsv` all refuse `RECEIPT-COUNTS-ABSENT`; only
   `c2-k4-base.tsv` and `c3-control.tsv` (whose stdout carries `cases=11 pass=4`) verify.
   So 4 of 7 round-26 receipts refuse. C1's kill rule ("any landed SCORECARD number that disagrees
   with its receipt") and C2's "each `verify=ok`" both inherit this gap.

6. **Two of the committed "before" receipts were re-emitted after after-data existed.**
   Current c3-before (`utc=2026-10-25T17:29:28Z`) was committed in `e0f8dcd` (commit time
   17:29:52Z); current c2-before (`utc=2026-10-25T17:29:54Z`) in `d6c13b0` (17:30:04Z). The
   pre-data originals are preserved at `89e0fce` (both `rev=12fd90b`, `utc=17:06:11Z`/`17:06:12Z`).
   No number is gamed — both versions are red and bound to `rev=89e0fce`/`12fd90b`, which precede
   every after-data commit — but the prereg's "committed BEFORE after-data" wording does not describe
   the current committed artifacts. c1-before is untouched (`utc=17:06:10Z`, `rev=12fd90b`).

7. **The prereg's own red-before command is not runnable as frozen.**
   `preregistration.txt` C1 do-nothing control spells
   `python3 -B tools/souji-receipt-run.py run --root . --rev 0eca7c8… --label census/round-26/c1-counter.sh -- bash …`:
   `run` has no `--label` (flag is `--tool`), and
   `git cat-file -e 0eca7c8:census/round-26/c1-counter.sh` fails ("exists on disk, but not in
   '0eca7c8…'", exit 128) — the counters only exist from `12fd90b`. The committed receipts use
   `12fd90b`/`89e0fce`, which is sound; the frozen text is not.

8. **Adjacent (C3 seat's item, reported because the receipts surfaced it):** the committed fixture
   runs 11 cases, not the 12 enumerated in the frozen C3 case set.
   `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py` →
   `cases=11 pass=11`, exit 0, no `control=` token; C3 K2 as frozen requires
   `cases=12 pass=12 control=FALSE-GREEN-REJECTED`. Amendment 1 covers C2-K4 and amendment 2 C1's
   kill rule; no logged amendment covers a 12→11 case-set change, and amendments are stricter-only.

## Attack log

- **A1 (receipt gate is asserted, not executed).** The frozen text claims `verify=ok` on receipts
  that the in-tree runner has always refused. A scorer taking that clause at face value credits a
  gate nobody ran. Counter-move that stays inside the rules: record the refusal verbatim per
  receipt (done here) and let the L1 score the claim on reproducibility + kill rules; do not relax
  `COUNTS_RE` after data (relaxing the counts requirement is strictly weaker, so not an admissible
  amendment).
- **A2 (`verify=ok` does not bind the measured value).** `verify` checks tool digest at `rev`, argv
  membership, durable ref, and that *some* stdout line matches `COUNTS_RE`. A counter that prints a
  decoy COUNTS_RE-shaped line alongside (or instead of) the real key=value could verify while the
  K value is arbitrary; `c3-control.tsv` demonstrates the acceptance path with
  `cases=11 pass=4` (a 4/11 FAIL summary) verifying `ok`. `corpus/lessons/round-22.md:399` (M18)
  already states the counts line is not proof; r26 does not add a binding. This is a counter-design
  attack, not a post-data predicate change.
- **A3 (probe string would launder into a false refusal report).** The assigned command carries
  `--rev`, which `verify` rejects with argparse exit 2 for every receipt, including the good
  c2-k4-base. A seat reading only the exit code would report "all four refused" and misattribute the
  cause to the receipts instead of the invocation. Evidence split above (§1 vs §2) so the L1 can
  separate instruction defect from receipt defect.

## Not done / out of scope

- No build/lint/test/formatter run (wave in flight per lane rules); the only executions are the
  read-only probes quoted above plus the adjacent fixture invocation in finding 8.
- No writes outside this report and `/var/tmp/souji-r26-LabReceiptVerify/` (removed).
- Certification OFF, K5 HELD, F5/NAMESPACE untouched; nothing under `/home/vgpnk/Projects/shokuknow` touched.
