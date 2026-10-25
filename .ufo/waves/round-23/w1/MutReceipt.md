# MutReceipt — C2 receipt runner: clause enumeration and mutant verdicts

STATUS: PARTIAL — 26 mutants over 20 clauses; 9 killed, **uncovered=17**. The fixture is now a
valid detector (baseline 8/8 against `f8c5d217…`), and on it the "tool digest from the tree at rev"
clause is **not** killed by case 3 and cannot be: case 3 discriminates only the `verify` side. The
stdout/stderr-verbatim clause is uncovered *by the fixture's own concession*, while the shipped
runner demonstrably does not record verbatim bytes.

## Evidence

Bytes tested (read-only copies; both halves were rewritten by the L1 mid-run and I re-baselined
twice — the hashes below are the ones every verdict belongs to):

| artifact | sha256 | note |
|---|---|---|
| `tools/souji-receipt-run.py` | `0d36ce98d1263d4c38a46b97f4654cd2a4242287ddd63161e31bb0e7269a5278` | final bytes; all verdicts below |
| `.ufo/waves/round-23/w1/r23-receipt-run.py` | `f8c5d217e96ab1ea1943f885041c35396184a941c593d33e1366f939c39d7ef2` | the 8-case detector; baseline 8/8 |
| superseded runner | `359cc415…`, `8ba27613…`, `1ec9b2fe…` | 5/8, 6/8, 8/8 baselines; **not** these verdicts |
| superseded fixture | `6ab9ac7b…`, `bef5126d…` | 5/8 and 7/8 baselines; **not** these verdicts |

Both halves were rewritten by the L1 while this seat ran (three runner revisions, two fixture
revisions). The matrix was re-derived from scratch on each; the verdict shape below is the one the
final pair produces, and the earlier pairs produced the same 9 killed / 17 survived split except
where noted in finding 3.

Lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`. Harness under `/var/tmp/souji-r23-MutReceipt`
(scratch only, removed at end; nothing written into the lane, no `git` write, no `pacman`).

Baseline and restoration (printed by the harness on every run):

```
base_sha256=0d36ce98d1263d4c38a46b97f4654cd2a4242287ddd63161e31bb0e7269a5278
fixture_sha256=f8c5d217e96ab1ea1943f885041c35396184a941c593d33e1366f939c39d7ef2
BASELINE rc=0 selftest=8/8
...
restored_sha256=0d36ce98d1263d4c38a46b97f4654cd2a4242287ddd63161e31bb0e7269a5278 identical=True
```

Verdict rule: a mutant is KILLED only when a case that is green at baseline turns red. Every mutant
is a single-clause, single-anchor substitution on a copy; each anchor was asserted to occur exactly
once before the run.

## Findings

### 1. The mutant table (one mutant per clause; `uncovered=17`)

| mutant | clause | killing case | verdict |
|---|---|---|---|
| M01 | rev must be full 40-hex (run side) | — | SURVIVED |
| M02 | rev must be full 40-hex (verify side) | 4 | KILLED |
| M03 | rev reachable from a durable ref | — | SURVIVED |
| M03b | durable roots exclude `refs/jj/*` | — | SURVIVED |
| M04 | measured tree is checked out at rev | — | SURVIVED |
| M05 | tool digest from the tree at rev, not the working tree | — | SURVIVED |
| M07 | `--out` must not be under `/tmp` | 6 | KILLED |
| M08 | `--out` must not be inside the measured repo | — | SURVIVED |
| M09 | runner must not write the target repo (transient write) | — | SURVIVED |
| M09b | same (persistent write, fixed name) | 7 | KILLED |
| M09c | same (persistent write, unique name) | 7 | KILLED |
| M10 | `verify` recomputes the digest at the receipt's rev | 3 | KILLED |
| M11 | `verify` refuses a tool missing at rev | — | SURVIVED |
| M12 | rev shape is exactly 40 lower-hex | — | SURVIVED |
| M13 | receipt header order | 1, 2, 3, 4, 5 | KILLED |
| M13b | receipt header completeness (`utc=`) | 1, 2, 3, 4, 5, 8 | KILLED |
| M14 | `rc` is the command's real exit code | 1 (rc-probe) | KILLED |
| M15 | stdout recorded verbatim (redaction pass removed) | — | SURVIVED |
| M16 | stderr recorded verbatim | — | SURVIVED |
| M17 | stderr fence spelling | 1 | KILLED |
| M18 | refusals write no receipt | — | SURVIVED |
| M19 | `command_refusal` write-side-effect guard | — | SURVIVED |
| M20 | `OUT-PROTECTED` guard | — | SURVIVED |
| M21 | `OUT-SIBLING-LANE` guard | — | SURVIVED |
| M23 | `--tool` is repo-relative (absolute refused) | — | SURVIVED |
| C13 | `verify` requires a counts line (`COUNTS_RE`) | — | SURVIVED |

Killed 9, survived 17. M03/M03b are two mutants of one clause; M09/M09b/M09c are three shapes of one
clause; C13 is a clause the implementation added that the frozen contract does not name.

Observables, verbatim:

```
M02 KILLED by c4 -> short7(rev=15f0186) rc=0 codes=-     # the branch arm alone does NOT kill it
M07 KILLED by c6 -> rc=0 codes=- wrote_under_tmp=True
M09c KILLED by c7 -> after=… ?? .receipt-staging-250566
M10 KILLED by c3 -> immutable rev rejected rc=2 codes=RECEIPT-TOOL-DIGEST-MISMATCH
M13 KILLED by c1 -> line4 key=cmd want=tool_sha256; line5 key=tool_sha256 want=cmd
M13b KILLED by c1 -> header lines=6 want=7; utc=
M14 KILLED by c1 -> rc-probe recorded rc=0 want=3
M17 KILLED by c1 -> no stderr fence
```

### 2. Case 3 does **not** kill "tool digest from the tree at rev" — and cannot

M05 (digest read from the source working tree instead of the checked-out tree at rev) survives all
eight cases. Case 3 moves HEAD forward **after** the receipt exists; at run time (case 1) the working
tree was clean at `rev1`, so the working-tree digest and the rev-blob digest are the *same value* and
the two hypotheses are observationally identical. Case 3 does its real work on the **verify** side —
it kills M10 (`verify` reading HEAD) — and separates nothing about what the run bound.

`verify`'s own re-hash cannot close this either: it computes both sides of its comparison itself, at
the receipt's `rev`, and never observes what the run saw. Only a run performed while the working tree
differs from `--rev` makes the recorded digests diverge. Direct probe (repo at `C1`, working tree
holding `C2`'s bytes via `git reset --soft C1`, `--rev C1`):

```
cur-run.py  run_rc=0 tool_sha256=7bca34089935009299afaf6433de  verify_rc=0 verify=ok
mut-M05.py  run_rc=0 tool_sha256=fb5807941cacecca75e5bc469ad7  verify_rc=2
            RECEIPT-TOOL-DIGEST-MISMATCH  receipt fb5807941cac != tree 7bca34089935 at 1140283c…
```

Minimal fixture re-specification that kills M05: after the case-3 mutation commit, `git reset --soft`
to `rev1` (working tree keeps the newer bytes, `rev=C1`), then `run --rev rev1` and `verify` it — the
receipt must carry `C1`'s blob digest and verify must exit 0. `git reset --hard` afterwards, or
case 7's before/after snapshot is dirtied. This is the case the claim's own kill rule
("a receipt whose verify exits 0 while its tool bytes at rev differ") needs, and no current case
reaches it.

### 3. "stdout/stderr captured verbatim" is uncovered by concession, and the runner is not verbatim

`CTRL_RE` at `tools/souji-receipt-run.py:73` is `[\x00-\x1f\x7f]`, and `redact()` at `:78` replaces
those with a space — `\x0a` included. Both captured streams pass through it (`:204`, `:206`).
Receipt produced this run from the fixture's own counter template (two stdout lines, two stderr
lines):

```
--- stdout ---
assertions=4 resolved=3 skipped=1 mismatches=0 label=two words
--- stderr ---
line-one line-two
```

against the truth `'assertions=4 resolved=3 skipped=1 mismatches=0\nlabel=two words\n'` and
`'line-one\nline-two\n'`. Two lines each became one. M15 and M16 survive because the fixture deliberately stops looking:
`r23-receipt-run.py:305` reads "Presence, not layout: the runner may normalize control characters in
the captured output", and `:308` collapses whitespace before the substring test. So the clause the
task enumerates is not tested at all, and a receipt can no longer be re-parsed line-wise downstream.

Two further violations of the same clause, reproduced on the current bytes: `text=True` (`:190`)
turns `\r\n` into `\n` (true `…  \r\n\n` → recorded `…  \n`), and a non-UTF-8 byte aborts the run with
`UnicodeDecodeError`, `run_rc=1`, and **no receipt** — a counter whose output is not valid UTF-8
cannot be receipted at all.

### 4. Read-only detection is a before/after porcelain snapshot — three blind spots

Case 7 (`r23-receipt-run.py:157-158`) compares `git status --porcelain` around the run. M09b/M09c
(persistent writes) are killed; M09 (a scratch directory created inside `--root` and removed in the
`finally`) is not — a transient write never appears in either snapshot. Measured separately: plain
`--porcelain` does not see ignored paths at all (`''` vs `'!! stray.log'` with `--ignored`), and
writes inside `.git/` are invisible to both. Q4's "runs only under /var/tmp (never /tmp, never a
live fleet path), and cleans up after itself" is enforced for the receipt path and not for the
measured tree.

### 5. Contract drift: `git archive` became `git clone` + `checkout`

The preregistration's C2 kill rule says "The runner is read-only with respect to the lane
(materializes git archive <rev> under /var/tmp; never writes the lane tree, never fetches)." The
shipped runner instead clones into `scratch/repo` and checks out detached at rev
(`tools/souji-receipt-run.py:170-177`). The substitution is defensible — a counter that needs git
plumbing gets a real repository — but it changes the frozen wording, and M04 shows nothing detects a
checkout of the wrong rev. Note also that this `git` invocation is the only one without the
environment scrub and `-c maintenance.auto=false` that every other call site applies (`:106-114`); it
inherits `GIT_*` from the caller. Whether `clone --no-local` can write into the source repo is
[INFERENCE], untested here.

### 6. Clauses with no negative case at all

M01 (run-side rev shape), M03/M03b (durability, `refs/jj/*`), M08 (`--out` inside the repo),
M11 (absent-at-rev precision), M12 (41-hex/uppercase), M15/M16 (verbatim streams), M18 (a refusal
leaving a stub receipt), M19/M20/M21 (the three guards the implementation added), M23 (absolute
`--tool`), C13 (counts-line guard — probe V1 removes it and no case changes).

M11 and M12 are *precision* gaps, not absences: case 5's doctored path is absent everywhere, so a
working-tree fallback is not distinguished; case 4's two values (branch name, 7-hex) never exercise
the 40-hex shape itself. M02 is killed only by case 4's **short7** arm — the branch arm resolves and
passes.

## Attack log

Attack 1: "case 3 is the discriminating case for the digest-at-rev clause." **Refuted.** Case 3 is
green on a verifier that reads HEAD (M10 kills it — that is the verify side) and green on a runner
that reads the working tree (M05 survives); it separates neither from the shipped code at the moment
the receipt is written. The discriminating construction is a *run* at an older rev with newer bytes on
disk (probe in finding 2).

Attack 2: "the 8 cases bind the 12 enumerated clauses." **Refuted for 17 of 26 mutants**, including
three clauses the claim's own kill rule depends on: the digest binding (M05), durability
(M03/M03b) and the read-only property under transient writes (M09).

Attack 3: "a receipt records what ran." **Partially refuted** — `redact()` flattens every newline and
`text=True` re-encodes the streams, so the receipt records a normalized rendering, and non-UTF-8
output produces no receipt at all.

Restoration: `cur-run.py` and `fixture.py` are copies; the lane originals were never opened for
write. The harness re-hashed the tested file after every mutant and printed `identical=True`.

## Cleanup and tooling

`/var/tmp/souji-r23-MutReceipt` removed after this report was written. No tool installed or upgraded
(host `git 2.56.0`, `python 3.14.8` sufficed); no `pacman` transaction attempted.
