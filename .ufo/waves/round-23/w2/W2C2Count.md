# W2C2Count — attack on C2's counting command (round 23, wave 2)

Seat: L1Souji23.W2C2Count (critic, falsify). Read-only. Lane tip
`102690017115cb202f292828c90b72705f69bf09` (= `refs/heads/master`).
Artifact attacked: the C2 counter `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l`,
the five receipts it counts under `census/round-23/records/`, and
`tools/souji-receipt-run.py` **at the tip blob**, sha256
`6bb623b8e8ce40028aee740ee40d600963d253e494048ce1ef121d5007d63e45`
(extracted to scratch and run there; the worktree copy was being edited by a concurrent seat
during this review, see §6 — every verify result below is from the tip blob).
Frozen contract: `.ufo/waves/round-23/preregistration.txt` §C2.
Scratch: `/var/tmp/souji-r23-w2-C2Count/` (removed at end).

## Verdict

**`falsified` as worded**, and **`survives` in its narrow enforced part.**

- Falsified: the predicate is a *worktree file count*, not a count of bound receipts, and
  `verify` does not enforce three of the six fields the claim says the receipt "binds"
  (`command`, `rc`, `stdout`). Both questions in the assignment answer **YES**: the number can be
  inflated without a run, and a receipt verifies while its recorded `rc` and `stdout` are wrong.
  The report's pairing (`count` then `verify` each) does **not** close either.
- Survives: (a) the number 5 reproduces under both a worktree count and a revision-scoped count;
  (b) 5/5 receipts `verify=ok` against the tip blob; (c) the before arm is 0 at the base rev;
  (d) the stale-digest refusal fires with the documented code. C2's kill rule ("a receipt whose
  verify exits 0 while its tool bytes at rev differ from the recorded digest") **does not fire** —
  I found no such receipt. The digest binding is real; the *evidence that a run happened* is not,
  and the claim's wording implies it is.

## 1. The counter, re-run (three ways)

```
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
5
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/
census/round-23/records/agreement-after.tsv
census/round-23/records/declared-evidence-after.tsv
census/round-23/records/gate-check-at-first-landing.tsv
census/round-23/records/gate-check-at-lane-base.tsv
census/round-23/records/gate-check-c3.tsv

$ git grep -lE '^tool_sha256=[0-9a-f]{64}$' 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd -- census/ | wc -l
0                                  # before arm reproduces
$ git grep -lE '^tool_sha256=[0-9a-f]{64}$' 1026900 -- census/ | wc -l
5                                  # after arm, revision-scoped, also 5
```

So the landed number is correct *today*. The defect is the predicate, not the count.

Note the asymmetry: the **before** arm is revision-scoped (`git grep <base>`), the **after** arm is
worktree-scoped (`grep -r`). `census/` currently holds **152 untracked files**
(`git ls-files --others --exclude-standard census/ | wc -l`), so the after arm's domain is not the
tip tree.

## 2. Inflation — YES, without any run and still `verify=ok`

Mirror of the five receipts at `/var/tmp/souji-r23-w2-C2Count/mirror2/census/round-23/records/`,
then one hand-written file with a header I typed (never produced by `run`; `rev` real, `tool`
real, digest copied from a real receipt, `cmd`/`rc`/stdout invented):

```
before (5 real receipts):            5
after 1 hand-written never-run file: 6
$ python3 <tip-blob> verify --root <lane> .../forged-never-run.tsv
verify=ok rev=1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd tool=tools/souji-gate-check.py tool_sha256=d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d
exit=0
```

Those bytes exist in **no commit** of the lane; `verify` accepts them. A second forged file makes
the point sharper — the `tool` need not be a counter and the `cmd` need not invoke it:

```
tool=corpus/README.md  tool_sha256=7e0fe5450a810d50b9f31c51ed2eae4386f8a11ab2deb8f08c4a62a1c14b5279
cmd=/bin/true
--- stdout ---
keys=4 records=4 occurrences=18 mismatches=0
$ verify --root <lane> ...
verify=ok ... tool=corpus/README.md ...
exit=0
```

`verify` checks that the named path's blob at the named rev hashes to the recorded digest; it never
checks that the path is a tool, that `cmd` runs it, or that the counts line came from anything.

## 3. `rc` / `stdout` falsification — YES

Copy of the real `census/round-23/records/agreement-after.tsv` (`rc=1`,
`MISMATCH K1 … mismatches=1`) with two edits — `rc=1` → `rc=0`, stdout replaced by a clean counts
line — then verified against the lane's git:

```
$ verify --root <lane> /var/tmp/souji-r23-w2-C2Count/tampered.tsv
verify=ok rev=476525026cdb179f2d49441e1cb6c6f7316f3124 tool=tools/souji-record-agreement.py tool_sha256=617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9
exit=0
```

And a receipt whose `rc` is not even an integer, whose `utc` is not a date, whose stdout is empty
and whose counts line sits in the **stderr** fence:

```
rc=banana
utc=not-a-date
--- stdout ---
--- stderr ---
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
$ verify → verify=ok ... exit=0
```

Root cause, from the tip blob: `cmd_verify` (L238-260) reads only `rev`, `tool`, `tool_sha256` and
`_body`; `_body` is `"\n".join(lines[idx:])` starting at the `--- stdout ---` line and running to
EOF (L234), so a counts-shaped line anywhere after that fence passes (L258). `rc` (written at
L204) and `utc` (L205) are never read back. `run`'s own fixture proves the *runner* records `rc`
faithfully (`tests/fixtures/r23-receipt-run.py:311-323`, rc-probe wants `3`), but no case binds
`verify` to a re-run; the fixture's three `doctored()` sites touch only `rev` (L364, L389) and
`tool` (L413). So 8/8 does not cover this vector.

## 4. Already in-tree: a red receipt inside the counted set, and a citation that does not exist

`census/round-23/records/agreement-after.tsv` records `rc=1` and
`keys=4 records=4 occurrences=18 mismatches=1` at `4765250`. It `verify=ok`. So "every one
`verify=ok`" (SCORECARD.md:22) is literally true *of a failing run*.

The report then pairs that green with a C1 after-state that no file supports:

- `SCORECARD.md:21` after cell: ``mismatches=0`` at the landing tip
  (``census/round-23/records/agreement-after.txt``).
- `LOG.md:1577-1578`: `After: mismatches=0 at the landing tip (receipt
  census/round-23/records/agreement-after.txt)`.

`agreement-after.txt` exists in **no commit** (`git log --all --diff-filter=AD --
census/round-23/records/agreement-after.txt` → empty) and is absent from the tip tree
(`git ls-tree --name-only 1026900 census/round-23/records/` lists only `agreement-after.tsv`).
The existing `.tsv` says `mismatches=1`, not 0. Measured now: the C1 instrument at tip `1026900`
emits `mismatches=4`, all K4 live-worktree (wave-2 seat reports in flight), K1 resolved; the only
C1 after-receipt in the tree binds the red `4765250` state. So the C2 "5 bound receipts" set
contains **no receipt binding the tip's C1 state**, and the report's pairing is being used as a
truth halo over a receipt that says the opposite of the row that cites it.

## 5. Durability asymmetry: `verify` accepts what `run` refuses

A receipt naming `00eceb01d4f7f393511511d9bf212e909521ab0a` (reachable only from `refs/jj/keep`;
0 refs among heads/tags/remotes) with the correct blob digest there:

```
$ verify --root <lane> .../nondurable.tsv
verify=ok rev=00eceb01d4f7f393511511d9bf212e909521ab0a tool=tools/souji-gate-check.py tool_sha256=d5ed0805...
exit=0
$ run --root <lane> --rev 00eceb01... --tool tools/souji-gate-check.py --out ... -- /bin/true
REV-NOT-DURABLE	00eceb01d4f7f393511511d9bf212e909521ab0a is not reachable from refs/heads|tags|remotes
exit=2
```

`run` enforces durability (L145); `verify` does not call `durable_rev` at all, and it checks only
that `rev` is 40 hex (L249). The blob at that jj-only rev hashes to the *same* `d5ed0805…` as
`1208bfb`, so the digest field cannot distinguish the two. A receipt bound to a jj-keep commit is
one `jj forget` + gc away from `RECEIPT-TOOL-ABSENT`, i.e. the evidence evaporates without any
commit changing.

## 6. The chain has no root: the verifier itself is not bound

No receipt and no record under `census/` binds `tools/souji-receipt-run.py`
(`grep -rn '6bb623b8\|2761290d' census/` → no hits; the only mention is
`agreement-control-base-worktree.txt:30` listing it as `uncommitted-path ??`). The verifier is the
trust root of the whole C2 claim and it is pinned by nothing. During this review the worktree copy
was modified by a concurrent seat (`sha256 2761290d…` worktree vs `6bb623b8…` at tip) while the
five receipts were being verified. Today's diff is confined to `run`'s `command_refusal` token scan
and `out = realpath`, so `verify`'s logic is unchanged — but nothing in the artifact set would have
told a reader that, and a changed `cmd_verify` would silently re-bless any receipt set.

## 7. No receipt is committed at its own named rev; the domain races

```
declared-evidence-after.tsv      @ 9301d98c -> ABSENT
agreement-after.tsv              @ 47652502 -> ABSENT
gate-check-at-first-landing.tsv  @ a211e4d1 -> ABSENT
gate-check-at-lane-base.tsv      @ 1208bfb4 -> ABSENT
gate-check-c3.tsv                @ 47652502 -> ABSENT
```

So only `rev → tool blob` is bound; the receipt bytes themselves are bound to nothing, which is
exactly why §2's forgery is indistinguishable. And because the counter's domain is the worktree,
the number is not revision-reproducible: mid-review I observed `?? census/round-23/records/stale-digest-demo.tsv`
(a concurrent seat's scratch, created and removed between two of my calls — I did not read its
bytes, so I cannot say whether it matched the anchored regex) and
`M census/round-23/records/refusal-stale-digest.txt`. The count stayed 5 on every one of my runs,
but the predicate admits any file another seat drops under `census/`.

## Honest predicate

> `C2_honest`: `verify` exits 0 iff the receipt header parses in v1 order, `rev` is 40 lowercase
> hex, `rev:tool` resolves to a blob, `sha256(blob) == tool_sha256`, and a counts-shaped line
> appears anywhere between the `--- stdout ---` fence and EOF. It establishes **no** fact about
> `cmd`, `rc`, `utc`, the stdout body, the durability of `rev`, whether `tool` is a counter, or
> whether the receipt was produced by `run`. The counter counts **files under the worktree**
> `census/` whose bytes contain that anchored line, regardless of whether any of the above holds.
> Five such files exist at the tip and all five pass `verify`; that is the whole claim.

What the claim/report says and what is enforced:

| field | claim (prereg C2) | enforced by `verify` |
|---|---|---|
| rev | bound | syntax only (40 hex); no durability, no commit check |
| tool path | bound | must exist at rev; may be any file |
| tool_sha256 | bound | **enforced** (L252-256) |
| command | bound | never read |
| rc | bound | never read |
| stdout | bound | only a counts-shaped line anywhere in stdout+stderr |

## Does the pairing close it?

**No.** `count` + `verify` each closes exactly one class: a receipt whose digest is stale or
mistyped at its named rev (the D3 shape) — reproduced:
`tool_sha256=5b8025a8…` → `RECEIPT-TOOL-DIGEST-MISMATCH … exit=2`, matching
`census/round-23/records/refusal-stale-digest.txt`. It leaves open, each demonstrated above:
inflation by a file that was never run (§2), `rc`/`stdout` falsification (§3), a red receipt read
as green (§4), non-durable revs (§5), non-counter tools (§2), and an unbound verifier (§6).
The disclosure in `corpus/lessons/round-23.md:40` ("Receipts bind bytes, not execution — a typed
receipt passes `verify`") is honest and covers §3; it does **not** cover §2 — "a typed receipt
passes verify" says the digest proves nothing about execution, not that the *counter* is
satisfiable by a file that no runner produced. The SentinelScope disposition at
`corpus/lessons/round-23.md:136` ("the 'grep counter counts files, not verified receipts' attack
is disclosed and paired with a verify-per-receipt command") claims the pairing as the mitigation;
§2 shows the pairing does not mitigate it.

## Smallest safe correction

1. **FIX the counter (one line, no new authority).** Make both arms revision-scoped:
   `git grep -lE '^tool_sha256=[0-9a-f]{64}$' <full40 tip> -- census/ | wc -l` → measured `5`.
   This removes the untracked-file vector and the worktree race in §7 outright. Update
   `SCORECARD.md:22`, `LOG.md:1582-1592`, `corpus/lessons/round-23.md:29-30`.
2. **FIX the root (cheap, closes §2/§6).** Commit `census/round-23/records/receipts.tsv` with one
   `path<TAB>sha256(receipt bytes)<TAB>rev` row for the five receipts plus
   `tools/souji-receipt-run.py<TAB>6bb623b8…<TAB>1026900`, and have `verify` check the receipt's own
   sha256 against that row. A forged or edited receipt then fails, and the verifier is pinned.
3. **FIX the wording, or add `--rerun`.** Either strike `command, rc, stdout` from "binding" in
   `preregistration.txt` §C2, `SCORECARD.md:22` and `LOG.md:1582-1592` (and say "records"), or add
   `verify --rerun` that re-executes the recorded `cmd` at `rev` and compares `rc` + stdout (the
   runner already has the clone+checkout path at L166-178). The prereg's named limit already declines
   execution proof, so the wording fix is the safe one; `--rerun` is optional.
4. **FIX the citation (§4).** `SCORECARD.md:21` and `LOG.md:1577-1578` must name
   `census/round-23/records/agreement-after.tsv` and state `rc=1, mismatches=1 at 4765250` — or bind
   a fresh tip receipt. This is C1 scope; it is reported here because it sits inside the C2
   counted set and is the concrete instance of "green verify, red counter".
5. **DISCLOSE the enumerated-set substitution.** The prereg target names four receipts
   (`declared-evidence before, declared-evidence after, gate-check before, gate-check after`); the
   landed five are `declared-evidence-after, gate-check-at-first-landing, gate-check-at-lane-base,
   gate-check-c3, agreement-after`. The missing one is producible-but-degenerate, measured: the
   tool is absent at the r22 base `4edb25d` (`git cat-file -e 4edb25d:tools/souji-declared-evidence.py`
   → `fatal: … exists on disk, but not in '4edb25d…'`), and at `1208bfb` the runner produces
   `assertions=63 resolved=63 skipped=40 mismatches=0` — byte-identical to the "after" at `9301d98`
   (same tool digest `65817d0d…`), so the before/after pair proves nothing. I produced that receipt
   in scratch (`verify=ok`) and did not commit it. The report must state this, not leave the
   enumeration unmatched.
6. **ACCEPT** the rc/stdout limit (prereg named it) — but repeat it in the `SCORECARD.md:22` row,
   not only in the lesson Boundary, and drop the word "bound" for those three fields.

## Impacted axes

- **operability 8** (the axis this claim moves): the instrument is sound for what it enforces
  (digest binding + stale-digest refusal + read-only run), but the claim overstates its own measure
  and the counting predicate is inflatable. The axis move stands only after correction 1-3.
- **calibration 7**: §4 is a false citation in the report plus a red receipt counted as green; that
  is the axis's own defect class (D2/D5) reappearing in the round that claims to close it.

## Bounds

Read-only. Writes: this report and `/var/tmp/souji-r23-w2-C2Count/` (removed). No git/jj mutation,
no `rm`/`mv`, no signals, no installs, nothing touched under `.ufo/state/`, `MANIFEST.json`, the
fleet `scripts/`/`templates/`, sibling lanes, or the lane's index. The frozen counter scans
`census/`, which includes 152 untracked operator-sweep files; I ran the frozen command as specified
and did not open any operator-sweep file. Certification OFF, K5 HELD. This report is untracked under
`.ufo/waves/round-23/w2/` and will be flagged by C1's K4 until committed or exempted.
