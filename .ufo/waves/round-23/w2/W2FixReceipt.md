# W2FixReceipt — mutation probe of the C2 fixture (`tests/fixtures/r23-receipt-run.py`)

**Verdict: the fixture is not decorative — the assigned mutant (verify re-pinned to HEAD instead of
the receipt's rev) is KILLED by case 3, `selftest=7/8` exit 1, deterministically. Coverage limit:
three further one-point mutations — stubbed durability gate (Q37 / `RECEIPT-REV-NOT-DURABLE`),
deleted counts guard (`RECEIPT-COUNTS-ABSENT`), and a revert of the `realpath` `--out` hardening —
each pass `8/8`, with live differentials proving the mutated code is reachable and the killed
behaviour is real.**

## Bytes pinned

The lane was under concurrent sibling edits during this seat; the final pinned pair is the lane's
committed state at HEAD `5378018` ("round-23: r22 section ends at the correction header (K2)",
two commits past `1026900`):

```
$ sha256sum tools/souji-receipt-run.py tests/fixtures/r23-receipt-run.py
d6e7e32f38c1bee7a72d8f2f567f8579896153cc4411361b34ef1923b7d65e5b  tools/souji-receipt-run.py
18f4da110e0cdb176826cb14b5967e899875d4b31fadb289679e6b3e39f996b4  tests/fixtures/r23-receipt-run.py
$ git status --porcelain -- tools/souji-receipt-run.py tests/fixtures/r23-receipt-run.py
(empty — both committed at 5378018)
```

Every verdict below was also reproduced at the seat's start on the `1026900` bytes
(`6bb623b8…63e45` tool, `f8c5d217…7ef2` fixture) — identical outcomes. The tip drifted twice
mid-seat; all probes were re-run and re-pinned rather than inherited (see Drift section).

## Baseline (pinned pristine, lane's own bytes via copy `s3.py`)

```
$ python3 tests/fixtures/r23-receipt-run.py <s3.py>
selftest=8/8    exit=0   (~1.7 s)
```

All eight cases pass; case 3 reports `old_at_rev1=rc0 stale_at_rev2=rc2/RECEIPT-TOOL-DIGEST-MISMATCH`.

## Mutant A (assigned) — verify binds HEAD, not the receipt's rev

One-point edit at `tools/souji-receipt-run.py:255` (on the pinned copy, mirror `s3-A.py`,
sha256 `49cd430573efc6239645a799d566193e9dc76a442652c2ca458a9d3a3f066629`):

```diff
-    actual = blob_sha_bytes(root, rev, tool)
+    head = git(root, "rev-parse", "HEAD").stdout.strip()
+    actual = blob_sha_bytes(root, head, tool)
```

```
$ python3 tests/fixtures/r23-receipt-run.py <s3-A.py>
case=3 expect=<old receipt still valid at its own rev after the mutation commit; stale digest at
  the new rev -> RECEIPT-TOOL-DIGEST-MISMATCH>
       got=<immutable rev rejected rc=2 codes=RECEIPT-TOOL-DIGEST-MISMATCH>
selftest=7/8    exit=1
```

**Killed.** The killer is case 3a (`tests/fixtures/r23-receipt-run.py:354-362`): after the
mutation commit lands, the fixture re-verifies the old receipt, whose `rev=` is `rev1 != HEAD`, and
a HEAD-bound verifier must reject an immutable receipt — `immutable rev rejected rc=2`. The
companion sub-case 3b (`:366` writes a receipt doctored to `rev=rev2` while `HEAD == rev2`) would
**not** have caught this mutant alone: at that moment comparing against HEAD still mismatches the
stale digest, so the mutant emits the required code for the wrong reason. The 3a/3b pairing is
what makes the rev-vs-HEAD distinction observable, and it is the only place in the fixture where a
verify runs at `rev != HEAD`. Killed twice (deterministic, not a race).

## Surviving mutants (the coverage limit, demonstrated)

### B — durability gate stubbed (`return True`, Q37)

`tools/souji-receipt-run.py:126-130` (`s3-B.py`, sha256 `28825be366bdebe86c4d40e305576502b312e3e365e9f9fd0fdcc15cd7d783de`):

```
$ python3 tests/fixtures/r23-receipt-run.py <s3-B.py>
selftest=8/8    exit=0        ← survives
```

Differential proving the gate is live and the mutant reaches it (scratch repo: `revB` reachable
only from `refs/jj/keep`; `for-each-ref --contains revB refs/heads refs/tags refs/remotes` →
empty, `... refs/jj` → `refs/jj/keep`):

```
pristine : rc=2  REV-NOT-DURABLE   d81f66d25d… is not reachable from refs/heads|tags|remotes
mutant B : rc=2  CHECKOUT-FAILED   fatal: unable to read tree (d81f66d25d…)
```

The mutant walks straight through the Q37 refusal; it only trips later on an incidental checkout
(a `--no-local` clone cannot fetch `refs/jj/*`). The fixture never presents a full-40 rev that is
unreachable from durable refs: `refs/jj` and `durable` occur **0 times** in the fixture file, and
case 4 (`:381`) feeds only the malformed shapes (branch name, 7-hex) that die at `REV_RE` before
`:148`'s durability call.

### C — counts guard deleted

`tools/souji-receipt-run.py:261-262` removed (`s3-C.py`, sha256
`9ab8e39c425d4681056ad9ab15f5e0d3f3624beb7a0a6e0050fb0ee0f3578ac8`):

```
$ python3 tests/fixtures/r23-receipt-run.py <s3-C.py>
selftest=8/8    exit=0        ← survives
```

Differential on a receipt produced by the *pristine* runner with a no-counts command
(`-- /bin/echo hello`):

```
pristine : rc=2  RECEIPT-COUNTS-ABSENT  no counts line in the recorded output
mutant C : rc=0  verify=ok rev=dc868388… tool_sha256=d60cdf61…   ← counts-free receipt verifies green
```

Every receipt the fixture feeds `verify` is either produced by its own counter (always prints
`assertions=4 …`) or a `doctored()` rewrite that touches only `rev`/`tool` (`:366`, `:391`, `:415`)
— never the body. `RECEIPT-COUNTS-ABSENT` is unexercised.

### D — `realpath` → `abspath` on `--out` (revert of the mid-seat hardening)

`tools/souji-receipt-run.py:153` (`s3-D.py`, sha256
`9305204cdac040ac1c9643b9cc662bb1c35086c3eb51b1d1c84e841b9782e7eb`):

```
$ python3 tests/fixtures/r23-receipt-run.py <s3-D.py>
selftest=8/8    exit=0        ← survives — while the mutant demonstrably does this:
pristine : rc=2 OUT-UNDER-TMP, wrote=False        (--out = symlink-dir/receipt)
mutant D : rc=0 receipt=…/linkdir/d-s3-D.py.receipt   wrote real path /tmp/d-s3-D.py.receipt
```

A sibling hardened `--out` with `os.path.realpath` at 05:44 mid-seat. The revert survives because
case 6 (`:421-430`) probes only the literal path `/tmp/souji-r23-should-not-exist-…` — it has no
symlink case, so the Q4 hardening added today is unverified. (The stray `/tmp` receipt from the
differential was removed.)

### Still-unbound, statically established (not run — one-mutant budget plus three probes)

`OUT-IN-REPO` (`:156`), `OUT-PROTECTED` (`:164`), `OUT-SIBLING-LANE` (`:166`), the
`command_refusal` shapes `GIT-DIRECTED-COMMAND`/`WRITE-SIDE-EFFECT`/`MUTATING-SUBCOMMAND`
(`:93-113`; the new every-token `DENY_SUBCOMMANDS` loop at `:104` — another mid-seat sibling
hardening — is likewise unexercised: `counter_cmd` at `:215` never runs a `git` command),
`REV-ABSENT`, `TOOL-UNREADABLE`, `CLONE-FAILED`, `CHECKOUT-FAILED`, `RECEIPT-UNREADABLE`,
`RECEIPT-MALFORMED` (no case reorders/corrupts the header), and `redact` (no case emits
secret-shaped output). Each token occurs 0 times in the fixture (`grep -c` = 0 for all listed
names). Of the tool's 13 `refuse()` sites the fixture reaches about three on the run path and
four on the verify path.

## Drift disclosure (concurrent sibling edits mid-seat)

| Time (-03:00) | Event | Effect on this probe |
|---|---|---|
| 05:38–05:51 | All baseline + mutant verdicts first run on `1026900` bytes (`6bb623b8`/`f8c5d217`) | Identical outcomes to the pinned set |
| 05:44:32 | `tools/souji-receipt-run.py` modified in-tree: `command_refusal` every-token DENY loop, `out = os.path.realpath(...)` | Probes re-applied and re-run on `2761290d` bytes; identical verdicts; mutant D added to cover the new guard |
| 05:50:42 | Both files modified again: `sys.dont_write_bytecode = True` added to each (no case/logic change) | Re-pinned as `d6e7e32f`/`18f4da11`; full probe set + all differentials re-run on these bytes — the verdicts above are those runs |
| ~05:52–05:56 | Lane commits `1dd8b1e`, `5378018` | `5378018`'s tool blob `git show` hashes to exactly `d6e7e32f` — the pinned tool IS the committed tip |

The probe verdicts hold on three consecutive byte sets; the surviving-mutant findings are
byte-stable.

## What the round must do

- **Accept** that the headline C2 clause is bound by the fixture: `verify` is pinned to the
  receipt's named rev, and the 3a/3b case pair demonstrably detects a HEAD-bound verifier. No
  change owed for mutant A.
- **Fix (or explicitly disclose as unverified)** the durability gap: add a case that commits a rev
  reachable only from `refs/jj/*` and asserts a refusal on `run --rev <it>` — the Q37 contract the
  tool's docstring advertises (`tools/souji-receipt-run.py:20-21`, `:126`) is currently unbound.
- **Fix (or disclose)** the counts gap: one `doctored`-style body rewrite that deletes the counts
  line, asserting `verify` refuses, closes `RECEIPT-COUNTS-ABSENT`. This matters because a
  counts-free receipt is precisely "evidence that records nothing measurable."
- **Fix (or disclose)** the `--out` coverage gap: case 6's literal-path probe does not exercise
  `realpath`, and 10 of 13 `refuse()` sites are unreachable from the fixture (list above). The
  mid-seat hardenings (`realpath`, every-token DENY loop) landed *while this seat was running* and
  are each unverified; `selftest=8/8` must not be read as coverage of the runner's whole refusal
  surface.

## Method limits

- Read-only in the lane: `sha256sum`, `git rev-parse/log/diff/show/status`, `grep`, `cp` into
  `/var/tmp/souji-r23-w2-W2FixReceipt/`, `python3` on the fixture and mirrors. No git/jj mutation,
  no `rm`/`mv` in the lane, no signals, no installs.
- Scratch repo + symlink differential lived only under `/var/tmp/souji-r23-w2-W2FixReceipt/`
  (removed at seat end); the two receipts the mutants tricked into `/tmp` were deleted immediately.
  The lane tool was never a mutation target — `git status --porcelain` on both files is empty and
  tip bytes are committed.
- The fixture cleans its own `/var/tmp/souji-r23-receipt-*` trees via trap; case 6's
  `wrote_under_tmp=False` confirms no `/tmp` writes on the pristine path.
- `[INFERENCE]` Mutant B's `CHECKOUT-FAILED` rests on `refs/jj/*` not being cloned by
  `--no-local`; a differently-configured clone could carry the ref — the gate's absence, not the
  downstream failure, is the demonstrated part.
- `[INFERENCE]` The "still-unbound" list is static (zero occurrence + no constructing case);
  those deletions were not each run.
