# SwarmCritic02 — falsify C1 item K02 (SCORECARD.md:153)

Item: K02, SCORECARD.md:153, frozen argv `python3 tools/souji-cert-evidence.py --selftest`, exit `0`, predicate `\b36/36\b`
(census/round-33/c1-items.tsv). Base 6017a482e7068d5afb7617640198fbb0fe743357; measured/list-rev
2d9bca55a9f042a2c9ed60a797a8069e74c41f46.

## Status

STATUS: PASS — K02 reproduces at the base and at 2d9bca5; the run is deterministic across five environments (five
byte-identical outputs, same md5); the frozen predicate is neither laxer nor stricter than the cell's stated outcome
for a behavioural regression (a real regression moves the count to 35/36 and MISMATCHes), and neither of the cell's
two other statements (external fixture 5/5; frozen pins and historical replays in the r13 record) is stale.
**Verdict: HOLDS.** Two residuals are reported below that are outside the item's definition; one of them (evidence
pointer voidable by editing the file it points at) is a real limitation of the C1 surface, not a defect in K02.

## Evidence

All commands run from a private `--no-local` clone with origin removed
(`/fast/scratch/hyaku/souji-r33/AuditK02/c`, `git rev-parse --show-toplevel` → that path), detached at
2d9bca55a9f042a2c9ed60a797a8069e74c41f46, `python3` = system python3, `-B` for lane scripts.

1. Frozen argv, fresh TMPDIR each run, then TMPDIR unset, then `LC_ALL=C`, then cwd elsewhere
   (`cd / && python3 /…/tools/souji-cert-evidence.py --selftest`):

```
$ TMPDIR=$D/tmp/run1 GIT_CONFIG_NOSYSTEM=1 python3 tools/souji-cert-evidence.py --selftest ; echo rc=$?
…
case path-absolute: ok rc=2 status=could-not-evaluate findings=path-absolute
…
selftest: 36/36 passed
rc=0
$ env -u TMPDIR -u TMP -u TEMP python3 tools/souji-cert-evidence.py --selftest ; echo rc=$?
selftest: 36/36 passed
rc=0
md5sum run1..run5 → 5e2fc75d3c4276ad029377ea222b21e7 (all five), 37 lines, 36 `case ` lines,
exactly one occurrence of `36/36`
```

   Deterministic: identical stdout in five runs spanning fresh TMPDIR, no TMPDIR (`/tmp`), `LC_ALL=C`, and a foreign
   cwd. The selftest's scratch is `tempfile.mkdtemp(prefix="souji-r13-cert-selftest.")` (TMPDIR-based); no
   `/var/tmp/souji-r13-cert-selftest.*` or `/tmp/…` leftover remained after any run.

2. Counter, as assigned, twice (list-rev and base):

```
$ python3 -B census/round-33/c1-counter.py --root …/souji-shokunin --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch …/cnt --only K02
ITEM	K02	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest: 36/36 passed
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
rc=0
$ … --rev 6017a482e7068d5afb7617640198fbb0fe743357 --list-rev 2d9bca5…
ITEM	K02	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest: 36/36 passed
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=6017a482e7068d5afb7617640198fbb0fe743357
rc=0
```

   `restated=0`: the item is still carried by the original row at 2d9bca5, and the row is still true there, so K02
   needs no `### Round 33 capability currency` row.

3. Cell text at base (`git show 6017a482e7068d5afb7617640198fbb0fe743357:SCORECARD.md | sed -n 153p`), quoted without
   the table pipes:

   > `python3 tools/souji-cert-evidence.py --selftest` → 36/36; external fixture 5/5; frozen input pins and actual
   > historical replays in `census/round-13/verification.json`

4. Count derivation (tools/souji-cert-evidence.py at 2d9bca5, line 1481):
   `print("selftest: %d/%d passed" % (len(results) - len(failures), len(results)))` and line 1482
   `return EXIT_CLEAN if not failures else EXIT_FAILED`. The total is the dynamic case count, so 36/36 cannot be
   emitted while any case fails (exit would be 1) and a shrunk or grown case list changes the total.

5. Mutation M1 (real regression, covered behaviour) — in the scratch clone only, `_classify_rel` changed so absolute
   paths are accepted (`return value.lstrip("/"), None`), committed with the throwaway identity
   (`scratch@invalid`, scratch commit `8b03182`):

```
$ python3 tools/souji-cert-evidence.py --selftest
case path-absolute: FAIL findings=artifact-missing want exactly=path-absolute
selftest: 35/36 passed
rc=1
$ c1-counter.py --root <scratch clone> --rev 8b03182… --only K02
ITEM	K02	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=selftest: 35/36 passed
rc=1
```

6. Mutation M2 (evidence-pointer voiding) — in the scratch clone only, `selftest()` replaced by a body that prints
   `selftest: 36/36 passed` and returns `EXIT_CLEAN`, scratch commit `e80f9ef`:

```
$ python3 tools/souji-cert-evidence.py --selftest ; echo rc=$?
selftest: 36/36 passed
rc=0
$ python3 -B tests/fixtures/r13-cert-evidence.py      # the cell's own sibling clause
ok selftest / ok external-clean / ok external-digest-mismatch / ok frozen-clean / ok frozen-tampered
fixture: 5/5 checks passed
$ c1-counter.py --root <scratch clone> --rev e80f9ef… --only K02
ITEM	K02	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest: 36/36 passed
```

7. Re-derivation of the cell's other statements at 2d9bca5:

```
$ python3 -B tests/fixtures/r13-cert-evidence.py
ok selftest / ok external-clean / ok external-digest-mismatch / ok frozen-clean / ok frozen-tampered
fixture: 5/5 checks passed
rc=0
$ python3 tools/souji-cert-evidence.py --frozen tests/fixtures/r13-cert-frozen
souji-cert-evidence: clean
summary fragments=2 assessed=2 pass=2 fail=0 findings=0 frozen_files=7
rc=0
$ python3 tools/souji-cert-evidence.py --root <clone> --manifest census/round-13/replay-wrong-bytes.json
finding artifact-digest-mismatch: fragments[0] artifact=tools/souji-census.sh …
rc=2        # record: exit 2, matched true
$ python3 tools/souji-cert-evidence.py --root <clone> --manifest census/round-13/replay-candidate.json
finding artifact-candidate: fragments[0] artifact=tools/cand-census-03.sh is a candidate file, …
rc=2        # record: exit 2, matched true
```

   The r13 record's own `evidence-selftest` entry holds 37 stdout lines whose last is `selftest: 36/36 passed`, so the
   row's stated count is backed by the record it cites, not copied from a later run.

8. Cited-record digests vs committed bytes at 2d9bca5 (`git show <rev>:<path> | sha256sum`): the record's
   `installed_sha256` for `tools/souji-cert-evidence.py` is `943d664c5df4e795c23821892a1691847772e95ef36752d532f5cbeff0e544d4`;
   committed bytes at 2d9bca5 are `816e85558a2fb829d55cf5fc11a1383b01b501468c59bba9ec700f048cafb921`. All six pinned tools
   differ (`souji-verify.sh` f88fed23…, `souji-census.sh` c1671f4c…, …), as expected for a historical record.

Tool installs/updates this seat: none (no tooling change was needed; pacman untouched).

## Findings

1. **K02 reproduces deterministically at both measured revisions.** Five runs, byte-identical
   (md5 `5e2fc75d3c4276ad029377ea222b21e7`), including once with TMPDIR unset and once from a foreign cwd; counter
   AGREE at base 6017a48 and at 2d9bca5. Location: `tools/souji-cert-evidence.py:1151-1482`, `census/round-33/c1-items.tsv:18`.

2. **The frozen predicate is faithful to the cell's stated outcome for this command, and it is not laxer for
   behavioural regressions.** `\b36/36\b` plus exit 0 is exactly `selftest: 36/36 passed` under the dynamic-total
   print, so a covered regression cannot pass it (M1 → 35/36 → MISMATCH). It is not stricter either: it does not
   demand the trailing word `passed` or the full line, but exit 0 supplies that guarantee because
   `selftest()` returns `EXIT_CLEAN` only when no case fails. Location: `tools/souji-cert-evidence.py:1481-1482`,
   `census/round-33/c1-items.tsv:18`.

3. **No stale out-of-set residual on line 153.** The cell's two non-item statements re-derive at 2d9bca5: external
   fixture `fixture: 5/5 checks passed` rc=0, and the r13 record's frozen pins and historical replays behave as
   recorded (`--frozen` → `frozen_files=7` clean; both replay manifests → rc=2 with the recorded finding ids).
   Location: `SCORECARD.md:153`, `census/round-13/verification.json` (`results[1]`, `results[10]`, `results[11]`).

4. **Residual (outside K02's definition, not a K02 defect): the item's surface cannot detect a tool that voids its
   own evidence pointer.** M2 — `selftest()` replaced by a hardcoded print of the frozen line — still AGREE, and the
   cell's sibling clause (`external fixture 5/5`) still passes, because that fixture only asserts the selftest's exit
   code and its result line. The row's statement stays literally true in M2, so nothing here is a C1 mismatch; what
   dies is the value of the pointer. Location: `tools/souji-cert-evidence.py:1151`, `tests/fixtures/r13-cert-evidence.py`
   (`selftest` check), reproduced in Evidence 6.

5. **Residual for the L1 (target sentence, not my item): a `--only` run prints the frozen `SUMMARY`.** Both of my
   `--only K02` runs printed `mismatches=0` with exit 0, which is the preregistration's literal C1 predicate
   ("the counter prints `mismatches=0`"), while `partial=1` records that only one item was evaluated. Nothing forbids
   `--only` in the frozen sentence, so the target is saddleable by a narrowed run; the counter's own full run is what
   carries the claim. Location: `census/round-33/c1-counter.py:307-308`, `census/round-33/preregistration.txt` C1
   predicate sentence.

6. **Observation (factual, not false): the cited r13 record's tool digests no longer bind current bytes, and row 153
   carries no `superseded:` annotation** unlike rows :148 and :150, which do. The cell only asserts the pins are *in*
   the record, which is true; I report the drift (`943d664c…` → `816e8555…` for this tool) so the L1 can decide whether
   the annotation gap matters. Location: `SCORECARD.md:148`, `:150`, `:153`; `census/round-13/verification.json`
   `installed_sha256`.

## Attack log

**Verdict: HOLDS** (not LAX-PREDICATE, not STRICT-PREDICATE, not NONDETERMINISTIC).

- *Counterexample tried (determinism)*: three independent environments (two fresh TMPDIRs, TMPDIR unset) plus
  `LC_ALL=C` and a foreign cwd. Result: identical 37-line output in all five, rc=0. No nondeterminism found; the
  tool's only external dependency is TMPDIR writability, and it honours it in both directions.
- *Counterexample tried (lax predicate)*: M1, a genuine capability regression in a covered path. Result: 35/36, exit 1,
  counter MISMATCH. The predicate discriminates.
- *Counterexample tried (stricter predicate)*: none found; the predicate accepts the exact nominal line and the
  dynamic-total construction makes the count exact (36 cases printed, one `36/36` token in the output; `\b` blocks
  `136/36` and `36/360`).
- *Counterexample that survives (reported, not scored against K02)*: M2 shows the C1 surface accepts a tool that
  deleted its own assertions, and the cell's external fixture does not close that hole. This is a limitation of
  pairing one command with one stated outcome — the item's frozen definition — not an over-lax reading of *this* cell.
- *Smallest safe correction*: none available inside this round's rules. K02's predicate, exit and item row are
  frozen, amendments are stricter-only and the L1's alone, and a rule changed after a seat has scored is not the
  claim's rule; I propose no change to K02 and no amendment. The durable fix is a future, differently-defined item
  that binds the 36 case names (the r13 record already holds them: `census/round-13/verification.json`
  `results[0].stdout`, 36 `case ` lines) rather than only the summary token — and that is a next-round design
  decision for the L1, not a repair to this round's frozen item.

## Deliveries

- `.ufo/waves/round-33/w1/SwarmCritic02.md` (this report).

Scratch removed: `/fast/scratch/hyaku/souji-r33/AuditK02` (clone, four TMPDIR trees, mutants `8b03182` and `e80f9ef`
existed only there and are gone; `/var/tmp` and `/tmp` hold no selftest residue; the lane working tree is clean —
`git -C …/souji-shokunin status --porcelain` printed nothing).
