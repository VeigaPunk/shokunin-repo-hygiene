# S61ReviewerC1 — C1 attack findings (control-chronology arm)

Seat: reviewer, wave r61-w1. Attacked the r60 base bytes
(`tools/souji-freeze-check.py` @ `c7228424c3919ecf142bab1aec8181722d86467b`,
verified byte-identical to the lane worktree), the wave design in
`.ufo/waves/round-61/w1-spec.json`, and — once it landed — the executor's
delivered candidate `candidate-freeze-check.py` (sha256
`7ef43b8f174fec50717858441822cd83e443bc83be57da8038ef7f3f3bc94828`),
`c1-counter.py`, `c1-matrix.tsv`, `build-matrix.py`, and all 14 receipts.
All fixture repos were hand-built under
`/fast/scratch/hyaku/souji-r61/S61ReviewerC1/` (toplevel asserted, throwaway
identity, every git call `-C <fixture>`); lane access was read-only git plus
the base/candidate tools' own read-only queries. Scratch removed on exit.

## Findings

### HIGH-1 — The arm is structurally blind: freeze-bounded + oldest-add can only ever refuse `add == freeze`

`control_chronology` (candidate lines ~296–315) runs
`git log --diff-filter=A --no-renames --full-history --format=%H <freeze> -- <path>`
and takes `ids[-1]` (oldest). Every commit reachable from `freeze` is an
ancestor-or-self of `freeze`, so `repo.is_ancestor(added, freeze)` is **vacuous**
inside this walk — the only live refusal paths are "no adding commit" and
`added == freeze`. Consequences, all empirically verified against the delivered
candidate bytes (each repo: base+candidate verdicts identical, EXIT=0,
findings=0 unless noted):

- **Post-freeze re-publication is invisible.** Repo `re-add-after`: receipt
  added pre-freeze (bound, red), deleted post-freeze, byte-identically
  re-added post-freeze by a child of the freeze; `--rev` = the re-add tip.
  `blob(freeze)==blob(rev)` so FROZEN-EDITED is silent; the freeze-bounded log
  sees only the pre-freeze add → candidate `SUMMARY claims=1 findings=0`,
  EXIT=0. This is exactly the shape the spec's `chrono-after` row was meant to
  pin (the only build where the *base* accepts a post-freeze receipt); the
  delivered matrix instead pins `chrono-after` as `CONTROL-MISSING` (receipt
  absent at freeze — Reading A), which the base also refuses, so the row
  contributes **zero** new-arm discrimination. Executor deviation D1 is
  honestly documented in `S61ExecChronoArm.md`, and the do-nothing control
  measured `new_forgeries=1` where the spec expected 2 — the spec arithmetic
  was unreachable under the freeze-bounded build.
- **Modify-at-freeze is invisible** (see HIGH-2).
- Q120's "a later replay never repairs the chronology" is not mechanized for
  the replay case: a receipt deleted and re-published after the freeze with
  identical bytes leaves no finding at any `--rev`.

Evidence (candidate, `--substance`):
```
re-add-after:      (0, 'SUMMARY claims=1 findings=0', '')
re-add-at-freeze:  (0, 'SUMMARY claims=1 findings=0', '')
glob:              (0, 'SUMMARY claims=1 findings=0', '')
at-freeze:        (1, 'FINDING C1 CONTROL-ADDED-NOT-BEFORE-FREEZE census/ctl.txt
                        added at 65c498b78850, not a strict ancestor of freeze 65c498b78850 ...')
```

Fix: bound the walk to `--rev` (as `freeze_rev`/`dispatch_findings` do), use
`--diff-filter=AM` (HIGH-2), and refuse when the add/modify set is empty or
**any** listed commit is not a strict ancestor of freeze — order-insensitive,
and it makes the `is_ancestor` check live again (post-freeze commits become
reachable). `git log --diff-filter=AM --no-renames --full-history --format=%H
<rev> -- <path>`; refuse iff any id `== freeze` or `not is_ancestor(id, freeze)`.
Honest rows (single pre-freeze add), `chrono-at-freeze`, and
`chrono-ancestor` keep their verdicts; `chrono-after` should be rebuilt as
Reading B (pre-freeze add + post-freeze identical re-add) and pinned
`CONTROL-ADDED-NOT-BEFORE-FREEZE`.

### HIGH-2 — `--diff-filter=A` cannot see content authored by the freeze commit via modify

Repo `re-add-at-freeze`: receipt added pre-freeze with unbound content, then
the **freeze commit itself** rewrites it to the full bound shape
(`instrument=`, `instrument_sha256=`, `rev=`, `command=`, `EXIT=1`). The
rewrite is an `M`, invisible to `--diff-filter=A`; `adds(ctl)=[c1]` (ancestor)
→ candidate accepts, EXIT=0 findings=0. Every substance check reads the
freeze *blob*, which is the evil content — so the entire bound receipt was
authored at the freeze commit and the arm sees nothing. No adding-commit rule
(oldest or newest) fixes this; the filter must include `M`.

Fix: folded into HIGH-1's `--diff-filter=AM` recommendation. Add a matrix case
`chrono-modify-at-freeze` (pre-freeze unbound add, freeze-commit rewrite to
bound shape) pinned `CONTROL-ADDED-NOT-BEFORE-FREEZE`.

### MEDIUM-1 — Raw pathspec globbing lets an innocent older path satisfy the oldest-add rule

The declared `Control:` path is passed unmodified as a git pathspec. Default
pathspec magic globs `*?[`: repo `glob` declares `Control: census/ctl*.txt`,
contains the literal file `census/ctl*.txt` (added **by the freeze commit**,
bound red receipt — `cat-file blob` lookups are exact, so all base checks
pass) plus an innocent `census/ctl-old.txt` added pre-freeze.
`git log -- census/ctl*.txt` matches **both** adds:
```
matches: ['1071d83b…', '304827a…']   # literal-file add at freeze + ctl-old add pre-freeze
```
oldest = the innocent pre-freeze add → candidate accepts (verified EXIT=0).
The same exposure pre-exists in `freeze_rev`/`dispatch_findings` (route as a
follow-up). A forged prereg can simply name a glob-metachar path.

Fix: prefix every repo path fed to `git log` with `:(literal)` in the new arm
(and ideally the pre-existing queries): `-- ":(literal)<path>"`.

### MEDIUM-2 — Merge-resolution content is invisible to A and AM without `-m`

Verified with a real conflicting merge whose resolution authored the receipt
content at the merge commit: `--diff-filter=A` and `--diff-filter=AM` (both
with `--full-history --no-renames`) list only the two branch adds — the merge
commit itself produces **no** file event. Content smuggled into the freeze
tree via conflict resolution at the freeze commit is therefore invisible to
even the recommended AM rule. (`-m` would surface it, at the cost of flagging
benign post-freeze merges that touch the receipt — a fail-closed trade-off the
L1 should choose deliberately.)

Fix: either run the chronology query with `-m` (documenting that post-freeze
merges touching the receipt refuse) or name the merge-resolution blind spot in
the matrix docs and add a merge-shaped matrix case pinning the chosen
semantics. Lane history is linear, so naming the limit is defensible.

### MEDIUM-3 — The matrix + stubs + real-record arm cannot catch an argv-keyed mutant

Every counter argv is deterministic: `--root work/<case-name>`,
`--prereg pre.txt`, `--rev <freeze sha>` where the freeze shas are pinned in
each case's `expected.txt` (delivered bytes); the real-record argv is fixed
lane bytes. A mutant that keys verdicts on literal argv strings passes the
11-case matrix, both stubs, and the real-record arm mechanically. The counter
*does* rebuild each case and verify pinned ancestor/freeze/orphan hashes
(`c1-counter.py` ~line 275) — good integrity pinning — but the pins are public
in the delivery. The only defense today is procedural (bytes review +
S61MutationCounter with fresh repos).

Fix (cheap, counter-side): rebuild each case under a randomized directory name
per run (rewrite the row's `control_receipt` prefix consistently), and add a
synthetic twin of the real-record shape at a randomized path requiring the
same `CONTROL-ADDED-NOT-BEFORE-FREEZE` pair. Otherwise name the limit.

### LOW-1 — Every matrix row is audited AT its freeze commit

`run_arm` is always invoked with `--rev exp["freeze"]` (`c1-counter.py` ~line
280), so `FROZEN-EDITED` and every post-freeze surface are vacuous inside the
matrix; the only rev>freeze coverage is the real-record arm on clean data.
Pre-existing r60 counter property, not introduced by r61 — worth a named
limit; optionally add one case audited at a post-freeze rev with an edited
receipt.

### LOW-2 — Verified non-issues (pinned for the record)

- **Shallow clones fail closed.** `git clone --depth 1|2 file://<at-freeze>`:
  the graft makes the shallow tip the attributed adder of every tree path;
  observed verdicts exit 1 with `BASE-UNRESOLVED` + `CONTROL-REV-INVALID`
  (findings=2). Under the recommended rev-bound rule the add set would resolve
  to non-ancestors → refuse. Fail-closed either way.
- **Replace refs cannot alter verdicts**: `Repo.env` hardcodes
  `GIT_NO_REPLACE_OBJECTS=1`; a planted `git replace` on the freeze commit
  left the verdict byte-identical (0/0).
- **Case-folding filesystems**: git tree/blob lookups are exact-byte; a
  case-mismatched declared path yields `CONTROL-MISSING` (fail-closed).
- **`--follow` absence is fine**: with `--no-renames` a rename registers as
  `A(new)+D(old)` — verified the rename commit is reported as the ADD of the
  new path, so a pre-freeze rename accepts and an at-freeze rename refuses.
- **`chrono-ancestor` positive control** is built at commit index 1 (after
  base) — a mutant requiring the add to be an ancestor of *Base* would still
  be caught via the honest rows; optionally rebuild it with the receipt added
  by the root commit to pin "chronology binds to freeze, not base".

## Assigned questions answered

**Q2 — r60 bytes over a hand-built chrono-at-freeze repo: PROVEN.** Base tool
`--substance` exits 0 `findings=0` both at `--rev=<freeze>` and
`--rev=<child>`; `git log --diff-filter=A --no-renames --full-history
--format=%H <rev> -- census/ctl.txt` resolves to the freeze commit
(`65c498b78850082928b0b80ace8aa7638916a1ca`, the same commit that adds
`pre.txt`). On the real record: lane adds for
`census/round-60/controls/c{1,2}-do-nothing.txt` and
`census/round-60/preregistration.txt` are all
`2670e96af1b81c7aa793acc34d40361b4beecff8`; base `--substance` at
`d05a00019835dee5b9bb8fe738add080434c4d67` → EXIT=0 findings=0 (reproduced);
candidate → EXIT=1 with exactly two
`CONTROL-ADDED-NOT-BEFORE-FREEZE` findings (C1 and C2), matching the C1 claim.
Default-path runs are clean (EXIT=0 both bytes).

**Q3 — counter falsification.** `new_honest=4` is correct for the delivered
11-row matrix (honest-1..3 + chrono-ancestor). The stubs still discriminate:
receipts show stub-accept → `new_forgeries=7 class_mismatches=7` EXIT=1 and
stub-refuse → `new_honest=0 class_mismatches=7` EXIT=1, `stubs=REJECTED`.
However the matrix **cannot** distinguish rule families: the real record has a
single add at freeze (every rule agrees), and no matrix row separates
oldest/any/newest or sees modify/merge events — the three bypass repos above
are precisely the missing discriminating shapes. An argv-keyed mutant passes
all arms mechanically (MEDIUM-3).

**Replacement-case check**: `forgery-rev-orphan` is constructible
(`git commit-tree` with no parent) and base-refused with
`CONTROL-REV-NOT-BEFORE-FREEZE` — verified on my own orphan-rev fixture
(EXIT=1, that class), so it correctly does not inflate `new_forgeries`.

## Verification gaps / residual risk

- I did not re-run the executor's counter end-to-end; I verified its receipts,
  the counter's comparison/rebuild logic by reading, and ran the *candidate
  tool* directly over my bypass repos (the decisive evidence).
- The `-m` merge trade-off and the rev-bound+AM rule change the finding
  surface; the L1 must re-pin `chrono-after`'s expected class and the
  do-nothing `new_forgeries` expectation (spec says 2; only reachable under
  the Reading-B rebuild).
- No tools installed or updated.
