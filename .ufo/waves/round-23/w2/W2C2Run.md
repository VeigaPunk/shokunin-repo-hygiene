# W2C2Run — C2 run-path falsification (round 23, wave 2)

seat: L1Souji23.W2C2Run (leaf, no dispatch)
date: 2026-10-25
target: C2 run path, `tools/souji-receipt-run.py run`
bytes attacked: lane tip `102690017115cb202f292828c90b72705f69bf09`
  (`git cat-file blob 1026900:tools/souji-receipt-run.py | sha256sum` =
   `6bb623b8e8ce40028aee740ee40d600963d253e494048ce1ef121d5007d63e45`,
   equal to the working-tree `sha256sum` of the same file)
method: scratch clone of the lane at the tip under `/var/tmp/souji-r23-w2-C2Run/lane`
  (`git clone --no-local`), runner invoked with `--root` = that clone. The lane repo was
  never the `--root` of a run.

## Verdict

**survives** — all six required shapes refuse with exit 2 and the documented code, no receipt
is written for any of them, and the lane/measured clone stays clean. Four defects found around
the run path (two evadable guards, one over-fire, one harness gap); none of them lets a run
write to the lane or produce a receipt it should have refused *for the six shapes under test*.
They are `disclose`/`fix` items for the round's claim text, not falsifiers of the run path as
scoped.

## The six required cases — command and output

Runner path used in every case: `tools/souji-receipt-run.py` (relative, run from the clone).
`REV=102690017115cb202f292828c90b72705f69bf09`.

### (a) rev that is a branch name

```
python3 tools/souji-receipt-run.py run --root /var/tmp/souji-r23-w2-C2Run/lane \
  --rev master --tool tools/souji-receipt-run.py \
  --out /var/tmp/souji-r23-w2-C2Run/out/a.receipt -- python3 tools/souji-gate-check.py --help
```
```
REV-MALFORMED	--rev must be a full 40-hex commit id
EXIT=2
ls: cannot access '/var/tmp/souji-r23-w2-C2Run/out/a.receipt': No such file or directory
```

### (b) 39-char rev (`102690017115cb202f292828c90b72705f69bf0`, `${#R39}` = 39)

```
python3 tools/souji-receipt-run.py run --root /var/tmp/souji-r23-w2-C2Run/lane \
  --rev 102690017115cb202f292828c90b72705f69bf0 --tool tools/souji-receipt-run.py \
  --out /var/tmp/souji-r23-w2-C2Run/out/b.receipt -- python3 tools/souji-gate-check.py --help
```
```
REV-MALFORMED	--rev must be a full 40-hex commit id
EXIT=2
ls: cannot access '/var/tmp/souji-r23-w2-C2Run/out/b.receipt': No such file or directory
```

### (c) `--out` under /tmp

```
python3 tools/souji-receipt-run.py run --root /var/tmp/souji-r23-w2-C2Run/lane \
  --rev 102690017115cb202f292828c90b72705f69bf09 --tool tools/souji-receipt-run.py \
  --out /tmp/c.receipt -- python3 tools/souji-gate-check.py --help
```
```
OUT-UNDER-TMP	receipts go outside /tmp (Q4)
EXIT=2
ls: cannot access '/tmp/c.receipt': No such file or directory
```

### (d) `--out` inside the repo

```
python3 tools/souji-receipt-run.py run --root /var/tmp/souji-r23-w2-C2Run/lane \
  --rev 102690017115cb202f292828c90b72705f69bf09 --tool tools/souji-receipt-run.py \
  --out /var/tmp/souji-r23-w2-C2Run/lane/d.receipt -- python3 tools/souji-gate-check.py --help
```
```
OUT-IN-REPO	the receipt must not be written inside the measured repo
EXIT=2
ls: cannot access '/var/tmp/souji-r23-w2-C2Run/lane/d.receipt': No such file or directory
git -C /var/tmp/souji-r23-w2-C2Run/lane status --porcelain   ->  (empty)
```

### (e) `git -C <elsewhere> fsck --lost-found`

```
python3 tools/souji-receipt-run.py run --root /var/tmp/souji-r23-w2-C2Run/lane \
  --rev 102690017115cb202f292828c90b72705f69bf09 --tool tools/souji-receipt-run.py \
  --out /var/tmp/souji-r23-w2-C2Run/out/e.receipt -- \
  git -C /var/tmp/souji-r23-w2-C2Run/elsewhere fsck --lost-found
```
```
GIT-DIRECTED-COMMAND	a -C/--git-dir/--work-tree command escapes the measured tree
EXIT=2
ls: cannot access '/var/tmp/souji-r23-w2-C2Run/out/e.receipt': No such file or directory
```
Note on code precedence: `-C` is tested (`tools/souji-receipt-run.py:97`) before the
`--lost-found` test (`:100`), so this shape reports `GIT-DIRECTED-COMMAND`, not
`WRITE-SIDE-EFFECT`. Both are documented exit-2 refusals and both are correct for this shape
(the command escapes the measured tree *and* writes); the precedence is stable, not flaky.
The pure form without `-C` does hit the write-side code:

```
... --out /var/tmp/souji-r23-w2-C2Run/out/ep.receipt -- git fsck --lost-found
WRITE-SIDE-EFFECT	git fsck --lost-found writes into the repository      EXIT=2
```

### (f) `git gc`

```
python3 tools/souji-receipt-run.py run --root /var/tmp/souji-r23-w2-C2Run/lane \
  --rev 102690017115cb202f292828c90b72705f69bf09 --tool tools/souji-receipt-run.py \
  --out /var/tmp/souji-r23-w2-C2Run/out/f.receipt -- git gc
```
```
MUTATING-SUBCOMMAND	git gc is not a counter
EXIT=2
ls: cannot access '/var/tmp/souji-r23-w2-C2Run/out/f.receipt': No such file or directory
```
Neighbour check: `--out .../fp.receipt -- git prune` ->
`MUTATING-SUBCOMMAND	git prune is not a counter`, EXIT=2.

Positive control (the refusals are not "refuse everything"): `-- git count-objects -v`
-> `receipt=... rc=0 counts=none`, EXIT=0, receipt written with
`tool_sha256=6bb623b8e8ce...`. No `/var/tmp/souji-receipt-*` scratch dir survived any run
(`ls -d /var/tmp/souji-receipt-*` -> "No such file or directory").

## Findings

### F1 — deny list is evadable by a global git option before the subcommand — disclose (or fix)

`tools/souji-receipt-run.py:99`
```
sub = next((a for a in argv[1:] if not a.startswith("-")), "")
```
The "subcommand" is the first token that does not start with `-`, so any global option that
takes a *separate* value hides the real subcommand. Measured:

```
-- git -c maintenance.auto=false gc --quiet
receipt=/var/tmp/souji-r23-w2-C2Run/out/p1.receipt rev=102690017115... rc=0 counts=none   EXIT=0
cmd=git -c maintenance.auto=false gc --quiet
```
Same with a wrapper: `-- env git gc --quiet` -> EXIT=0, receipt written;
`-- sh -c 'git gc --quiet'` -> EXIT=0, receipt written.

Impact is bounded: the mutating command runs with `cwd` = the private `--no-local` clone under
`/var/tmp`, which is deleted in the `finally` (`:186`), so the **lane** is not written — the
read-only-with-respect-to-the-lane half of C2 still holds. What fails is the *stated* guard:
`MUTATING-SUBCOMMAND` is presented as a refusal the runner performs, and `git -c k=v gc` walks
past it and yields a receipt with `rc=0`. The `env`/`sh -c` forms are arguably covered by the
docstring's "not a sandbox" limit, but the `-c` form is a plain parsing miss.
Round must: either (i) skip known global-option/value pairs when locating the subcommand
(`-c`, `--config-env`, `--exec-path`, `--namespace`, `--super-prefix`, `--attr-source`), or
(ii) add one sentence to the docstring naming the exact limit ("the deny list reads the first
non-option token; a global option with a separate value defeats it"). Silent omission is the
one thing the round may not do, because C2's control narrative reads the deny list as a guard.

### F2 — Q4 (`/tmp`) and OUT-IN-REPO guards are string-prefix, not realpath — disclose

`tools/souji-receipt-run.py:150-154` uses `os.path.abspath` (no symlink resolution) and then
`out.startswith("/tmp/")` / `out.startswith(root + os.sep)`. Measured:

```
ln -sfn /tmp /var/tmp/souji-r23-w2-C2Run/tmplink
... --out /var/tmp/souji-r23-w2-C2Run/tmplink/p4.receipt -- python3 -c 'print("keys=1 ...")'
receipt=/var/tmp/souji-r23-w2-C2Run/tmplink/p4.receipt ... counts=keys=1 records=1 occurrences=1 mismatches=0   EXIT=0
ls -l /tmp/p4.receipt  ->  -rw-r--r-- 1 vgpnk vgpnk 340 Oct 25 05:39 /tmp/p4.receipt
```
A receipt landed in `/tmp` with exit 0. The same trick inverts OUT-IN-REPO (a symlink inside
`--root` pointing outward, or an outside path reaching in). Q4 is a *house rule* (receipts must
survive the tmp cleaner), so a symlinked bypass is a real operability hole, not cosmetics.
Round must: use `os.path.realpath` on both `out` and `root` before the two prefix tests
(one-line change, no behaviour change for the six required shapes — verified: cases (c)/(d)
refuse on the literal paths as well, so the fix is additive), or disclose that the guards are
lexical. `fix` is cheap; prefer it.

### F3 — `-C` test over-fires on legitimate git copy-detection flags — accept (over-refusal)

`tools/souji-receipt-run.py:97` tests `"-C" in argv` positionally-blind, so
`git log -C --oneline -1` and `git diff -C --stat HEAD~1 HEAD` are refused
`GIT-DIRECTED-COMMAND` (both measured, EXIT=2). These are legitimate read-only counters that
`-C`-as-a-flag never escapes the tree with. Direction is safe (refuse, don't run), and no
round-23 receipt uses `-C` copy detection (`grep -rhE '^cmd=' census/` shows only `python3`
counters), so nothing landed is affected. Accept, with the over-fire named here so a later
round does not "discover" it as a regression.

### F4 — the committed fixture does not exercise four of the six run-path refusals — disclose

`tests/fixtures/r23-receipt-run.py:479-487` (`CASES = (1..8)`); its own docstring lists:
case 4 = *receipt* whose `rev=` is a branch name/7-char id (verify side), case 6 = `--out`
under `/tmp`. Not covered anywhere: `run` with a branch-name `--rev`, `run` with a 39-char
`--rev`, `OUT-IN-REPO`, and the three command-refusal codes
(`GIT-DIRECTED-COMMAND`/`MUTATING-SUBCOMMAND`/`WRITE-SIDE-EFFECT`). So the six shapes this
seat verified by hand have no committed harness behind them — the round's evidence for them is
this report, not a re-runnable selftest.
Round must: add cases for those four shapes to the fixture (each is ~6 lines reusing `case6`'s
shape), or state in the C2 row that the command-refusal path is demonstrated only in
`.ufo/waves/round-23/w2/W2C2Run.md`.

## Adjacent observations (not this seat's verdict — for W2C2Verify / main)

1. C2's claim text names four receipts: "declared-evidence before, declared-evidence after,
   gate-check before, gate-check after". On disk there is **no declared-evidence before**
   receipt: `grep -rln '^tool=.*souji-declared-evidence.py' census/` returns only
   `census/round-23/records/declared-evidence-after.tsv`. The numeric counter still passes —
   `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` = **5** (>= 4: agreement-after,
   declared-evidence-after, gate-check-at-first-landing, gate-check-at-lane-base,
   gate-check-c3), and all five verify clean:
   `verify=ok` for each, exit 0. But the parenthetical set and the disk set differ; the claim
   text must be corrected to the set that exists, or the missing before-receipt supplied.
2. `census/round-23/records/refusal-stale-digest.txt` is a hand-written transcript, not a
   receipt: it carries `command: ... <receipt with the r22 stale digest 5b8025a8...>` (an
   ellipsis placeholder) and `verify` on the file itself returns
   `RECEIPT-MALFORMED ... EXIT=2`. The refusal *behaviour* it claims was not re-derived by this
   seat (no receipt bytes for the stale digest exist to feed `verify`); the verify-side seat
   should either commit the fixture receipt or downgrade the artifact to a narrative.

## Residual risk / gaps

- Not attacked (out of assignment): `verify`'s own refusal paths, `durable_rev` against
  `refs/jj/*`-only commits, receipt overwrite semantics at an existing `--out`, and the
  non-UTF-8 `errors="replace"` claim. `durable_rev` was only exercised indirectly (a full-40
  rev reachable from `refs/heads/master` and `refs/remotes/origin/master` returned
  `refs/heads/master`, so the run path reached the command stage).
- F1/F2 evasions were measured only inside a throw-away clone; the lane was never the measured
  tree, so "the lane is read-only" is confirmed for these shapes by construction, not by a
  before/after object-count diff on the lane.
- Scratch `/var/tmp/souji-r23-w2-C2Run/` and `/tmp/p4.receipt` removed after the report was
  written; no lane file was touched by this seat.
