# AttackE14a — w2 adversarial falsification of W1's C1 E14a finding

Seat SwarmCritic13, lane souji-shokunin. Base `9c76c7222a8abff027af42e37f0d160d52526bba`; frozen list `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`.

## Status

W1's E14a finding is **CONFIRMED, with the root cause sharpened**: the frozen argv pins a
**41-hex object name** (`a65fac98964b445758e94c8057280c9a19d302ff8`) — a transcription
defect baked into the frozen list itself — so the mismatch is permanent at every revision
and no honest do-nothing/natural route to AGREE exists. W1's proposed blockage ("reachable
only by appended restatements") is **valid**; I further prove that the only conforming
restatement is an argv-correction of one specific shape, and that the "obvious" hash repair
alone is insufficient. W1's mismatch-class label ("missing/unresolvable pinned revision") is
imprecise but its conclusion is correct a fortiori.

## Evidence

### Frozen item (executed, read-only)

```
$ git show 2b0171e2071fdc9c16a69bed12b0d040e574d8c8:census/round-34/c1-items.tsv | sed -n '54p'
E14a	SCORECARD.md:67	128	path .* does not exist	tests/fixtures/r24-size-census.py	{REV}	bash -c "git cat-file -e a65fac98964b445758e94c8057280c9a19d302ff8:tests/fixtures/r24-size-census.py"
$ git show 2b0171e2071fdc9c16a69bed12b0d040e574d8c8:census/round-34/c1-items.tsv | grep -P '^E14a\t' | grep -o 'a65fac[0-9a-f]*' | awk '{print length($0), $0}'
41 a65fac98964b445758e94c8057280c9a19d302ff8
```

The pinned hash is **41 hex chars** (working tree == list rev: `git diff 2b0171e2… --
census/round-34/c1-items.tsv` is empty; the defect is frozen, not introduced later).

### W1's committed readings (not re-executed by me; treated as evidence)

- `census/round-34/records/controls-c1-do-nothing.txt`: `ITEM	E14a	MISMATCH	original	rc=128 expect_exit=128 predicate fails last=fatal: invalid object name 'a65fac98964b445758e94c8057280c9a19d302ff8'. load=11.20`
- `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:43` — identical line, load 28.47.
- `.ufo/waves/round-34/w1/deliver-q76-honoring.txt:47` — identical line, load 58.11.
- `.ufo/waves/round-34/w1/SwarmExecutor13.md` (finding 5 table): E14a `128; path .* does not exist` vs `128; fatal: invalid object name 'a65fac…'`, class "missing/unresolvable pinned revision"; no prior correction row for `SCORECARD.md:67`.

### My executed probes (main repo, read-only)

```
$ git cat-file -t a65fac98964b445758e94c8057280c9a19d302ff8        # 41-hex, frozen argv hash
fatal: Not a valid object name a65fac98964b445758e94c8057280c9a19d302ff8
$ git rev-parse --disambiguate=a65fac
a65fac98964b445758e94c805728c9a19d302ff8                            # 40-hex, exists
$ git cat-file -t a65fac98964b445758e94c805728c9a19d302ff8
commit                                                              # "a65fac9 round-23 verifier spot-check (integrator, hyaku)"
$ git merge-base --is-ancestor a65fac98964b445758e94c805728c9a19d302ff8 9c76c7222a8abff027af42e37f0d160d52526bba; echo rc=$?
0
$ git merge-base --is-ancestor a65fac98964b445758e94c805728c9a19d302ff8 2b0171e2071fdc9c16a69bed12b0d040e574d8c8; echo rc=$?
0
$ git cat-file -e a65fac98964b445758e94c805728c9a19d302ff8:tests/fixtures/r24-size-census.py
fatal: path 'tests/fixtures/r24-size-census.py' exists on disk, but not in 'a65fac98964b445758e94c805728c9a19d302ff8'   (rc=128)
$ git cat-file -e 9c76c7222a8abff027af42e37f0d160d52526bba:tests/fixtures/r24-size-census.py && echo TRACKED-AT-BASE
TRACKED-AT-BASE
$ git show 9c76c7222a8abff027af42e37f0d160d52526bba:SCORECARD.md | grep -cE "SCORECARD\.md:67([^0-9]|$)"
0                                                                   # no prior Q76 correction pointer
```

`SCORECARD.md:63` heading carries the **correct** 40-hex hash
(`lane base a65fac98964b445758e94c805728c9a19d302ff8`); the frozen argv corrupted it by
inserting `0` after `5728` (`…c805728` + `0` + `c9a19d…`). The `:67` cell text itself
documents the intended probe: "at base the fixture and tool are absent (`git cat-file -e
a65fac9:tests/fixtures/r24-size-census.py` fails)".

### Bounded end-to-end probe (executed; synthetic clone in the counter's exact mechanics)

Lane `.git` is 77 MB (full clone exceeds the 50 MB scratch ceiling), so I reproduced the
counter's execution context at trivial size: a 2-commit repo (commit A without the fixture,
commit B adding it — analogs of the true r23 commit and base), then
`git clone -q --no-local --no-checkout` + `git checkout -qf --detach B` + `/usr/bin/git
cat-file -e …` (git 2.56.0), mirroring `run_item()` in `census/round-34/c1-counter.py:214-232`:

```
FROZEN argv (41-hex):   fatal: invalid object name 'a65fac98964b445758e94c8057280c9a19d302ff8'.   rc=128
CORRECTED argv (40-hex): fatal: path 'tests/fixtures/r24-size-census.py' exists on disk, but not in '<A>'   rc=128
```

Scratch `/fast/scratch/hyaku/souji-r34/E14a/` removed after capture.

## Findings

1. **W1's verdict is real, not a measurement artifact.** Exit agrees (`128 == 128`); the
   predicate `path .* does not exist` fails because the last digit-bearing line is
   `fatal: invalid object name '…'`. Not load-sensitive (identical at load 11.20/28.47/58.11);
   the 41-hex name is unresolvable in any clone and in the main object store alike. The
   synthetic probe reproduces both message forms byte-for-byte in the counter's exact
   clone context, so the clone mechanics are exonerated.

2. **Root cause is stronger than W1's class label.** This is not a "missing/unresolvable
   pinned revision" in the repo sense — the intended commit
   `a65fac98964b445758e94c805728c9a19d302ff8` exists, is an ancestor of both base and the
   list rev, and is documented in the bound cell's own heading (`SCORECARD.md:63`). The
   frozen argv carries a **malformed 41-hex name**; git rejects it syntactically at every
   revision. No repository state can ever make the frozen argv resolve: the do-nothing
   blockage is permanent under `rrun == "same"`.

3. **Counter-evidence against the "obvious" repair (a route that fails).** Simply correcting
   the hash to the true 40-hex commit does **not** restore agreement with the frozen
   `(exit, statement)`: the fixture is tracked at base, so in the counter's checkout it is
   on disk and git prints `exists on disk, but not in '…'` — which does **not** match
   `path .* does not exist` (the identical wording trap W1 recorded for sibling E09a).
   Executed in the main repo and in the synthetic clone probe; [INFERENCE] for the real
   lane clone rests on those two executions plus E09a's recorded W1 output in the real
   counter clone.

4. **Honest-route audit under the frozen judge** (`census/round-34/c1-counter.py:237-312`;
   `census/round-34/preregistration.txt:48-57`):
   - **Value-drift restatement (`rrun == "same"`): impossible.** The judge requires the
     original `(exit, predicate)` to *hold* at the cause's parent; the 41-hex never
     resolves at any commit, so the predicate fails everywhere. No valid cause exists.
   - **Argv-correction restatement: constructible, and the only conforming route.**
     Cause `315422ba9970f03c27f8a9184446783b7fcdf0a7` (round-24 final) satisfies every
     frozen clause, all verified: ancestor of list rev (`rc=0`); parent `d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7`;
     wrote the bound line — the exact list-rev `SCORECARD.md:67` text is present at the
     cause and absent at the parent; the row's own frozen argv provably fails at the cause
     (41-hex, executed); a corrected argv naming the row's file
     (`bash -c "git cat-file -e a65fac98964b445758e94c805728c9a19d302ff8:tests/fixtures/r24-size-census.py"`)
     contains basename `r24-size-census.py`. The restated exit must be `128` and the
     restated statement must be the literal last digit-bearing line of the corrected run:
     `fatal: path 'tests/fixtures/r24-size-census.py' exists on disk, but not in 'a65fac98964b445758e94c805728c9a19d302ff8'`.
     A restatement that fixes the hash but keeps the frozen statement regex fails the
     judge's literal equality (`collapse(last_digit_line) == stmt`, c1-counter.py:308-311).
   - **RESULTS:/ANYLINE:/COUNT: alternatives: unavailable** — the run emits no `RESULT `
     lines, and a restated literal statement must equal the run's last digit-bearing line.
   - **Gaming routes also fail:** a ref named as the 41-hex string would still print
     "exists on disk, but not in" (statement mismatch) or exit 0 (exit mismatch); deleting
     the fixture at the landing rev to force "does not exist in" is a real change that
     breaks sibling E14c (which runs the fixture at `{REV}`) and the item's own files column.

5. **Conclusion.** The alleged defect is real; it is not unreachable under another frozen
   clause and not a measurement artifact. W1's blockage claim stands: E14a cannot AGREE at
   base or any descendant without an appended Q76 restatement, and exactly one restatement
   shape conforms (argv-correction to the true 40-hex hash, restated exit 128, restated
   statement binding the on-disk wording, cause `315422ba…`). What W1 left unspecified —
   the 41-hex malformed-hash root cause, the impossibility of value-drift, and the trap
   that hash-repair alone cannot keep the frozen statement — is supplied here.

Overlap note: the same corrupted 41-hex hash appears in sibling item E15c's frozen argv
(`c1-items.tsv:55`, cell `SCORECARD.md:68`); that item's statement/exit differ and E15c is
another seat's target — cited as corroboration of the transcription-defect family, not a
duplicate finding.

## Attack log

All lane operations read-only (`git show`/`cat-file`/`merge-base`/`rev-parse`/`log`,
`grep`, `sed`, `du` on `/home/vgpnk/Projects/shokunin/souji-shokunin`). No lane file, frozen
item, predicate, commit, or ref was modified; nothing committed or pushed. One bounded
synthetic probe was executed under `/fast/scratch/hyaku/souji-r34/E14a/` (git 2.56.0,
two-commit scratch repo, `--no-local --no-checkout` clone replicating the counter's
`run_item` mechanics) and removed after capture; no lane clone was created (lane `.git` is
77 MB, above the 50 MB scratch ceiling). Counter/W1 artifacts inspected but not executed:
`census/round-34/c1-counter.py` (read at lines 1-333), W1 deliverables listed in Evidence.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE14a.md` — this report.
- `.ufo/waves/round-34/w2/SwarmCritic13.md` — seat summary.
