# W2FixReceipt — mutation probe of the C2 fixture (`tests/fixtures/r23-receipt-run.py`)

**Verdict: the fixture is not decorative — the assigned mutant is KILLED by case 3 (7/8, exit 1).
Coverage limit: two clauses the runner's own docstring names are unbound — `RECEIPT-REV-NOT-DURABLE`
(Q37) and `RECEIPT-COUNTS-ABSENT` — each provable by a mutant that passes 8/8.**

Bytes under test (lane tip, read-only; nothing in the lane was written or moved):

```
$ sha256sum tools/souji-receipt-run.py tests/fixtures/r23-receipt-run.py
6bb623b8e8ce40028aee740ee40d600963d253e494048ce1ef121d5007d63e45  tools/souji-receipt-run.py
f8c5d217e96ab1ea1943f885041c35396184a941c593d33e1366f939c39d7ef2  tests/fixtures/r23-receipt-run.py
$ git rev-parse HEAD
102690017115cb202f292828c90b72705f69bf09
```

`HEAD` is `1026900`, one commit past the round's landed `4765250`/`c0eeaa7`; the only change it makes
to this artifact is `errors="replace"` on the measured `subprocess.run` (`git diff c0eeaa7 HEAD --
tools/souji-receipt-run.py`, 4 added/2 removed lines). The probe below runs against `1026900`'s bytes.

## Baseline (pristine, exact bytes)

```
$ python3 tests/fixtures/r23-receipt-run.py
case=1 ... got=<rc=0 header=v1/7 sha256=a62c58548f91... stdout=assertions=4 resolved=3 skipped=1 mismatches=0 label=two ... rc_probe=3>
case=2 expect=<verify rc=0> got=<rc=0 codes=->
case=3 ... got=<old_at_rev1=rc0 stale_at_rev2=rc2/RECEIPT-TOOL-DIGEST-MISMATCH>
case=4 ... got=<branch:rc=2/RECEIPT-REV-MALFORMED short7:rc=2/RECEIPT-REV-MALFORMED>
case=5 ... got=<rc=2 codes=RECEIPT-TOOL-ABSENT>
case=6 ... got=<rc=2 codes=OUT-UNDER-TMP wrote_under_tmp=False>
case=7 ... got=<before=empty after=empty runner_rc=0>
case=8 ... got=<sha_equal=True cmd_equal=True utc_equal=False utc=[2026-10-25T08:37:55Z, 2026-10-25T08:37:57Z]>
selftest=8/8
EXIT=0   (1.68 s)
```

## Mutant A (assigned) — `verify` compares against HEAD, not the receipt's rev

Mirror `/var/tmp/souji-r23-w2-W2FixReceipt/tool-mutant-A.py`, one edit at
`tools/souji-receipt-run.py:252`:

```diff
-    actual = blob_sha_bytes(root, rev, tool)
+    head = git(root, "rev-parse", "HEAD").stdout.strip()
+    actual = blob_sha_bytes(root, head, tool)
```

sha256 of the mutant: `0d85af77f073a41a0e1071f629db8e3e4b56f394e5c5d6c4857f65a0fe1c49c5`
(pristine `6bb623b8…63e45`).

```
$ python3 tests/fixtures/r23-receipt-run.py /var/tmp/souji-r23-w2-W2FixReceipt/tool-mutant-A.py
case=1 ... rc_probe=3>
case=2 expect=<verify rc=0> got=<rc=0 codes=->
case=3 expect=<old receipt still valid at its own rev after the mutation commit; stale digest at the new rev -> RECEIPT-TOOL-DIGEST-MISMATCH>
       got=<immutable rev rejected rc=2 codes=RECEIPT-TOOL-DIGEST-MISMATCH>
case=4 ... got=<branch:rc=2/RECEIPT-REV-MALFORMED short7:rc=2/RECEIPT-REV-MALFORMED>
case=5 ... got=<rc=2 codes=RECEIPT-TOOL-ABSENT>
case=6 ... got=<rc=2 codes=OUT-UNDER-TMP wrote_under_tmp=False>
case=7 ... got=<before=empty after=empty runner_rc=0>
case=8 ... got=<sha_equal=True cmd_equal=True utc_equal=False ...>
selftest=7/8
EXIT=1
```

**Verdict: killed.** Case 3a (`tests/fixtures/r23-receipt-run.py:352-357`) is the killer: it re-verifies
the old receipt *after* the mutation commit, so `rev1 != HEAD` and a HEAD-bound verifier rejects an
immutable receipt — reported as `immutable rev rejected rc=2`. Case 3b alone would **not** have killed
it: at 3b's verify time `HEAD == rev2`, so the stale digest still mismatches at HEAD and the mutant
produces the required `RECEIPT-TOOL-DIGEST-MISMATCH` for the wrong reason. The 3a/3b pair is what makes
the mutation detectable, and it is the only place in the fixture where `rev != HEAD` at verify time.
Reproduced twice (identical `7/8`, exit 1), so the kill is deterministic, not a race.

**Restoration:** the pristine bytes were copied back into the mirror slot
(`tool-restored.py`, sha256 `6bb623b8…63e45`, byte-identical to the lane file) and the same detector
returned `selftest=8/8`, `EXIT=0`. The lane file itself was never edited — pre- and post-run
`sha256sum` agree and `git status --porcelain -- tools/souji-receipt-run.py
tests/fixtures/r23-receipt-run.py` is empty (`status_rc=0`).

## Coverage limit — two mutants that survive 8/8

Both are single, plausible deletions of a guard the runner's docstring advertises (lines 28-31:
"`verify` exits 2 with one of: RECEIPT-MALFORMED, RECEIPT-TOOL-DIGEST-MISMATCH, RECEIPT-TOOL-ABSENT,
RECEIPT-REV-MALFORMED, RECEIPT-COUNTS-ABSENT"; lines 20-21: "`--rev` not reachable from refs/heads,
refs/tags or refs/remotes (refs/jj/* never counts — Q37)").

**B — durability gate stubbed** (`tools/souji-receipt-run.py:123-128` → `return True`,
sha256 `ceab04a0…`):

```
$ python3 tests/fixtures/r23-receipt-run.py .../tool-mutant-B.py
selftest=8/8   EXIT=0
```

Differential proving the mutation is behaviour-bearing (scratch repo, `revB` reachable only from
`refs/jj/keep`; `for-each-ref --contains revB refs/heads refs/tags refs/remotes` → empty,
`... refs/jj` → `refs/jj/keep`):

```
pristine : rc=2  REV-NOT-DURABLE  ec41a15b… is not reachable from refs/heads|tags|remotes
mutant B : rc=2  CHECKOUT-FAILED  fatal: unable to read tree (ec41a15b…)
```

The mutant walks straight through the Q37 gate; it fails only later, incidentally, because the
`--no-local` clone cannot fetch `refs/jj/*`. A stronger clone would have run a non-durable rev.

**C — counts guard deleted** (`tools/souji-receipt-run.py:258-259` removed, sha256 `bf17f2ce…`):

```
$ python3 tests/fixtures/r23-receipt-run.py .../tool-mutant-C.py
selftest=8/8   EXIT=0
```

Differential on a receipt produced by the pristine runner with a command that emits no counts line
(`-- /bin/echo hello`, body `--- stdout --- hello`):

```
pristine : rc=2  RECEIPT-COUNTS-ABSENT  no counts line in the recorded output
mutant C : rc=0  verify=ok rev=b4391e3f… tool_sha256=d60cdf61…
```

A receipt carrying no measurement verifies green under the mutant.

### Why the fixture misses them

- `refs/jj` and `durable` appear **0 times** in the fixture (`grep -c`); case 4 (`:379`) tests only
  the two *malformed* rev shapes (branch name, 7-hex) which fail `REV_RE` at `:249` before the
  durability gate at `:145` is ever reached. No case presents a full-40 rev that is unreachable from
  durable refs, so `REV-NOT-DURABLE` is never exercised.
- The only receipts the fixture feeds to `verify` are produced by its own counter, which always prints
  `assertions=4 …`, and the three `doctored()` call sites (`:364`, `:389`, `:413`) rewrite `rev` and
  `tool` only — never the body. `RECEIPT-COUNTS-ABSENT` is therefore unexercised.
- The same static gap covers these refusals, which have **0 occurrences** in the fixture and no case
  that can reach them: `OUT-IN-REPO` (`:154`), `OUT-PROTECTED` (`:162`), `OUT-SIBLING-LANE` (`:164`),
  `command_refusal`/`GIT-DIRECTED-COMMAND`/`MUTATING-SUBCOMMAND` (`:91-113`), `REV-ABSENT` (`:147`),
  `TOOL-UNREADABLE` (`:191`), `CLONE-FAILED` (`:172`), `CHECKOUT-FAILED`, `RECEIPT-UNREADABLE`
  (`:241`), `RECEIPT-MALFORMED` (`:246`, no case reorders or corrupts the header), and `redact`
  (`:77`, no case emits secret-shaped output). Case 6 (`:419`) binds only the `/tmp` guard.
  `[INFERENCE]` these are read, not mutated: only B and C were run, per the one-mutant budget plus two
  probes for the limit claim.

## What the round must do

- **Accept** the fixture's coverage of the headline C2 clause. `verify` is bound to *the receipt's
  rev*, not to HEAD, and that binding is enforced by a case that would otherwise look redundant
  (3a). No change owed for mutant A.
- **Fix (or explicitly disclose as out of scope)** the durability gap: `tests/fixtures/r23-receipt-run.py`
  has no case for a full-40 rev reachable only from `refs/jj/*`, so the Q37 refusal the runner's
  docstring promises is unverified. A ninth case — create an extra commit, `update-ref refs/jj/keep`
  it, `reset --hard` the branch back, then `run --rev <that commit>` expecting a refusal code and no
  receipt — costs one commit and closes it. Until it exists, any sentence in the round report that
  rests on "the runner refuses non-durable revisions" is a claim about unexercised code.
- **Fix (or disclose)** the counts gap: no case feeds `verify` a receipt whose body lacks a counts
  line, so `RECEIPT-COUNTS-ABSENT` is unverified; one `doctored`-style body edit plus a refusal
  assertion closes it. This one touches C2's evidence value directly — a counts-free receipt is
  exactly the "receipt that records nothing measurable" the guard exists to reject.
- Do **not** read `selftest=8/8` as coverage of the runner's whole refusal surface: 10 of the 13
  `refuse()` codes in the tool are unreachable from the fixture (static list above).

## Method limits

- Read-only in the lane: only `sha256sum`, `git rev-parse/log/diff/status`, `grep`, `cp` into
  `/var/tmp/souji-r23-w2-W2FixReceipt/`, and `python3` on the fixture and its mirrors. No git/jj
  mutation, no `rm`/`mv`, no signals, no installs.
- All mutations live in `/var/tmp/souji-r23-w2-W2FixReceipt/` and are removed at the end of this
  seat; the lane file was never a mutation target. The scratch probe repo
  (`/var/tmp/souji-r23-w2-W2FixReceipt/probe-repo`) was created by this seat only, for the B/C
  differentials.
- The fixture creates and trap-cleans its own `/var/tmp/souji-r23-receipt-*` trees; it wrote nothing
  under `/tmp` (case 6 asserts `wrote_under_tmp=False`).
- `[INFERENCE]` The "stronger clone would have run a non-durable rev" reading of mutant B's
  `CHECKOUT-FAILED` is reasoning about git clone's ref selection, not an executed alternative.
