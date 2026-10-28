# W1ExecExitMatrix — exit-code matrix for `tools/souji-citation-reconcile.py` (r39 wave 1)

seat: W1ExecExitMatrix (executor) · round 39 wave 1 · axis judged: operability
lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
base bytes: `ed30b7f5b77939c9073348d810730bc4f355708d` · repaired bytes pinned at lane HEAD `2201778e7736af82e7d8a42dec2494f115bf3923`
(the matrix below is measured on **base** bytes; the `head` column is the pinned repair, measured only to state the delta)
python 3.14.8 · git 2.56.0

Tool bytes actually executed (extracted with `git show`, never a working-tree copy):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-citation-reconcile.py \
  > /fast/scratch/hyaku/souji-r39/W1ExecExitMatrix/reconcile-base.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2201778e7736af82e7d8a42dec2494f115bf3923:tools/souji-citation-reconcile.py \
  > /fast/scratch/hyaku/souji-r39/W1ExecExitMatrix/reconcile-head-2201778.py
```

```
56866ea8f832332c2f69dcba4ddcd9ba5d7894bf9a2e82715962e2fb19bfcbe8  reconcile-base.py
59f1e57d7af02cac675757066fb6fa2629a0153f21c98a62e04b6d3b301d2b73  reconcile-head-2201778.py
```

Every fixture repository was built by a driver that asserts the fixture root first:
`git init -q "$D"`, then `git -C "$D" rev-parse --show-toplevel` compared byte-equal to `$D` before the first commit
(`matrix.py:41-43`, driver aborts otherwise). No git/jj mutation was issued outside a `mktemp`/scratch fixture.

Scratch tree (still on disk when this report was written, deliberately kept as rerunnable evidence):
`/fast/scratch/hyaku/souji-r39/W1ExecExitMatrix/` — `matrix.py`, `matrix2.py`, `boundary.py`,
`matrix.json`, `matrix2.json`, `boundary.json`, the two tool extractions, fixture repos `work/repo`,
`work/shallow`, `notarepo`.

---

## 1. The matrix (base bytes, one synthetic repo, register = 2 rows: row A clean, row B anchor absent)

Driver: `TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecExitMatrix python3 -B matrix.py`
(fixture: commits `rev1`/`rev2`, annotated tag `r39tag`, 12-hex prefix of `rev1`, tree/blob ids of `rev1`,
and a commit reachable only through `refs/jj/keep/<sha>` — branch deleted, `git branch --contains` empty).

`rc` = process exit, `first` = first line starting `MISMATCH` on stdout, `SUMMARY` = whether a `SUMMARY` line was printed.
`head` columns = the pinned repaired bytes on the same input.

| # | `--rev` shape | base rc | base first MISMATCH | base SUMMARY | head rc | head class |
|---|---|---|---|---|---|---|
| 1 | 40-hex, object absent (`1`×40) | **1** | `MISMATCH A FILE-ABSENT cite.txt at 1111…1111` | `SUMMARY cells=2 mismatches=4` | 2 | stderr `REFUSAL REV-UNRESOLVED: --rev 1111…1111 does not resolve to a commit` |
| 2 | 40-hex **blob** id (`cf553eb2…`) | **1** | `MISMATCH A FILE-ABSENT cite.txt at cf553eb2…` | `SUMMARY cells=2 mismatches=4` | 2 | `REFUSAL REV-UNRESOLVED --rev cf553eb2…` |
| 3 | 40-hex **tree** id (`25ad5c35…`) | **1** | `MISMATCH A RECEIPT-REV-NOT-ANCESTOR receipt.txt at 4b93a3b9…` | `SUMMARY cells=2 mismatches=3` | 2 | `REFUSAL REV-UNRESOLVED --rev 25ad5c35…` |
| 4 | 40-hex **annotated tag object** id | 1 | `MISMATCH B ANCHOR-COUNT … anchor='NO-SUCH-ANCHOR' hits=0` | `SUMMARY cells=2 mismatches=1` | 1 | same (peels to its commit — **evaluated**) |
| 5 | **tag name** (`r39tag`) | 2 | — | no | 2 | `REFUSAL USAGE: --rev must be 40-hex` |
| 6 | **12-hex prefix** | 2 | — | no | 2 | `REFUSAL USAGE: --rev must be 40-hex` |
| 7 | 40-hex **commit** | 1 | `MISMATCH B ANCHOR-COUNT … hits=0` | `SUMMARY cells=2 mismatches=1` | 1 | same |
| 8 | `HEAD` | 2 | — | no | 2 | `REFUSAL USAGE: --rev must be 40-hex` |
| 9 | `refs/jj/keep/<sha>` **name** | 2 | — | no | 2 | `REFUSAL USAGE: --rev must be 40-hex` |
| 10 | **keep-only commit by 40-hex** (no branch contains it) | 1 | `MISMATCH B ANCHOR-COUNT … hits=0` | `SUMMARY cells=2 mismatches=1` | 1 | same (resolves by object id) |
| 11 | uppercase 40-hex of a real commit | 2 | — | no | 2 | `REFUSAL USAGE: --rev must be 40-hex` |
| 12 | empty string | 2 | — | no | 2 | `REFUSAL USAGE: --rev must be 40-hex` |
| 13 | `--register-rev` **omitted** (working-tree register) | 1 | `MISMATCH B ANCHOR-COUNT …` | `SUMMARY cells=2 mismatches=1` | 1 | same |
| 14 | `--register-rev` **valid commit** | 1 | `MISMATCH B ANCHOR-COUNT …` | `SUMMARY cells=2 mismatches=1` | 1 | same |
| 15 | `--register-rev` 40-hex **absent** | 2 | — | no | 2 | base `REFUSAL USAGE: register register.tsv is not at 2222…`; head `REFUSAL REV-UNRESOLVED: --register-rev 2222…` |
| 16 | `--register-rev` **blob** id | 2 | — | no | 2 | base `… is not at cf553eb2…`; head `REFUSAL REV-UNRESOLVED` |
| 17 | `--register-rev` **tree** id that does contain the register | **1** | `MISMATCH B ANCHOR-COUNT …` | `SUMMARY cells=2 mismatches=1` | 2 | `REFUSAL REV-UNRESOLVED: --register-rev cd101261…` |
| 18 | `--register-rev` **tag name** | 2 | — | no | 2 | base `… is not at r39tag`; head `REFUSAL REV-UNRESOLVED` |
| 19 | register **path absent** at a resolvable `--register-rev` | 2 | — | no | 2 | `REFUSAL USAGE: register missing.tsv is not at a126f500…` (both) |
| 20 | register **path absent in the working tree** (`--register` only) | 2 | — | no | 2 | `REFUSAL USAGE: unreadable register missing.tsv: [Errno 2] …` (both) |
| 21 | `--root` is **not a repository** | **1** | `MISMATCH C1-1 FILE-ABSENT SCORECARD.md at ed30b7f5…` | `SUMMARY cells=11 mismatches=33` | 2 | `REFUSAL REV-UNRESOLVED: --rev ed30b7f5… does not resolve to a commit` |

Row 21 command (real register, empty root):

```
python3 -B /fast/scratch/hyaku/souji-r39/W1ExecExitMatrix/reconcile-base.py --root /fast/scratch/hyaku/souji-r39/W1ExecExitMatrix/notarepo \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d --register census/round-37/citation-cells.tsv
rc=1 · MISMATCH C1-1 FILE-ABSENT SCORECARD.md at ed30b7f5b77939c9073348d810730bc4f355708d · SUMMARY cells=11 mismatches=33
```

### 1b. Same matrix on the lane's own bytes (`--register census/round-37/citation-cells.tsv`, 11 cells)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
python3 -B <tool> --root . --rev <shape> --register census/round-37/citation-cells.tsv
```

| `--rev` | base rc / first line | head rc / first line |
|---|---|---|
| `ed30b7f5…` (base tip) | 0 · `SUMMARY cells=11 mismatches=0` | 0 · `SUMMARY cells=11 mismatches=0` |
| `5a2b49260be30036b825e7c5e371d7983c18e129` (keep-only; `git branch -a --contains` = 0 lines; only `refs/jj/keep/5a2b4926…`) | 0 · `SUMMARY cells=11 mismatches=0` | 0 · `SUMMARY cells=11 mismatches=0` |
| `$(git rev-parse ed30b7f5…^{tree})` = `856806cd388dcffb2f5f8d14bb9a6f95e83e77b4` | **1** · `MISMATCH C1-1 RECEIPT-REV-NOT-ANCESTOR census/round-36/records/c2-after.txt at 1e771ed5…` · `SUMMARY cells=11 mismatches=11` | 2 · `REFUSAL REV-UNRESOLVED: --rev 856806cd… does not resolve to a commit` |
| `$(git rev-parse ed30b7f5…:SKILL.md)` = `b233c952d59561747bbf4c0d69f55e8d080e547c` (blob) | **1** · `MISMATCH C1-1 FILE-ABSENT SCORECARD.md at b233c952…` · `SUMMARY cells=11 mismatches=22` | 2 · `REFUSAL REV-UNRESOLVED: --rev b233c952…` |
| `1111…1111` (absent) | **1** · `MISMATCH C1-1 FILE-ABSENT SCORECARD.md at 1111…` · `SUMMARY cells=11 mismatches=22` | 2 · `REFUSAL REV-UNRESOLVED` |
| `12hex` | 2 · `REFUSAL USAGE: --rev must be 40-hex` | 2 · same |
| `heads/master` | 2 · `REFUSAL USAGE: --rev must be 40-hex` | 2 · same |
| `refs/jj/keep/002d6a2478b271c7f4c9b5ba1a9d4fe16ab49fe0` | 2 · `REFUSAL USAGE: --rev must be 40-hex` | 2 · same |
| `--rev ed30b7f5… --register-rev 1e771ed59301ed10f68e22d4edf35d5218bacf1a` | 2 · `REFUSAL USAGE: register census/round-37/citation-cells.tsv is not at 1e771ed5…` | 2 · same |

The lane carries **no tags** (`git tag` empty), so the tag-name row is exercised on the synthetic fixture only (row 5) — stated, not inferred.

---

## 2. Which shapes a "could-not-evaluate exit 2" contract must cover

Rule derived from the matrix: **exit 2 belongs to every input the tool cannot evaluate, and to nothing else.**
Concretely, a revision-bearing CLI input must exit 2 with **no** `MISMATCH` and **no** `SUMMARY` line when:

1. **`--rev` is syntactically not a 40-hex object id** — tag name, branch name, `HEAD`, 12-hex prefix,
   `refs/jj/keep/<sha>` name, uppercase hex, empty string. Base already does this (`REFUSAL USAGE`, rc 2, empty stdout);
   this must not regress into findings. Note these are *resolvable* revisions that the tool deliberately refuses:
   the contract is "40-hex or could-not-evaluate", not "anything git resolves".
2. **`--rev` is 40-hex but does not resolve to a commit** — absent object, blob id, tree id. **This is the base hole**
   (rows 1-3, 1b): base reads `tree:path` / `path` bytes out of objects that are not revisions and prints
   `FILE-ABSENT` / `RECEIPT-REV-NOT-ANCESTOR` findings with `SUMMARY` and rc 1. The tree case is the sharpest: the
   citation arm *passes* (git happily serves `tree:file`) and the tool then accuses the register of an ancestry
   failure that no revision was ever checked against.
3. **`--register-rev` names anything that is not a resolvable commit** — absent object, blob, tree, tag name.
   Base is already rc 2 for absent/blob/tag (message `... is not at <rev>`), but **accepts a tree id and evaluates
   the register out of that tree** (row 17: base rc 1 with `SUMMARY`, then head rc 2). Whatever the class name,
   the exit code for a non-commit `--register-rev` must be 2 and it must be 2 for the tree shape too.
4. **`--root` is not a git work tree** (row 21): base prints 33 findings and rc 1 for a directory that is not a
   repository. This must be exit 2. The repaired bytes do exit 2 but attribute the cause to `--rev`
   (`REFUSAL REV-UNRESOLVED`), which is a *different* lie: the revision was never the problem.
5. Register-as-input failures already at exit 2 and must stay: register path absent at the pinned revision
   (`... is not at <rev>`), unreadable working-tree register, malformed register, non-regular/symlinked register.

**Must stay exit 1 (findings), and only when `--rev` resolved to a commit.** Verified at a resolved commit,
both tool revisions, identical strings (`matrix.py` kinds run):

| case at resolved commit | rc | first line |
|---|---|---|
| clean register | 0 | `SUMMARY cells=1 mismatches=0` |
| cited file absent at that commit | 1 | `MISMATCH A FILE-ABSENT absent.txt at a9d374df…` |
| anchor not found | 1 | `MISMATCH A ANCHOR-COUNT cite.txt anchor='NOPE' hits=0` |
| expected token missing on the line | 1 | `MISMATCH A EXPECTED-MISSING cite.txt expected='cases=8'` |
| citation line does not name its receipt | 1 | `MISMATCH A RECEIPT-UNNAMED cite.txt receipt='other.txt'` |
| stale token still present | 1 | `MISMATCH A STALE-PRESENT cite.txt stale='cases=7'` |
| receipt SUMMARY lacks the expected token | 1 | `MISMATCH A RECEIPT-DISAGREES receipt2.txt expected='cases=7' (no SUMMARY line carries it)` |

The boundary that keeps this coherent — and the one sentence the repair must not blur:

> **A revision the CLI was told to audit is an input: unresolved ⇒ exit 2. A revision written inside a register
> row (`receipt_rev`, `commit`) is data being audited: unresolved ⇒ finding, exit 1.**

Measured on both revisions (unchanged behaviour, correct):

```
row receipt_rev = blob cf553eb2…    -> rc 1  MISMATCH A RECEIPT-REV-UNRESOLVED receipt.txt at cf553eb2…
row receipt_rev = tree 25ad5c35…    -> rc 1  MISMATCH A RECEIPT-REV-UNRESOLVED receipt.txt at 25ad5c35…
row receipt_rev = absent 4444…      -> rc 1  MISMATCH A RECEIPT-REV-UNRESOLVED receipt.txt at 4444…
row receipt_rev = non-ancestor      -> rc 1  MISMATCH A RECEIPT-REV-NOT-ANCESTOR receipt.txt at 6fb366e2…
row commit cell  = blob cf553eb2…   -> rc 1  MISMATCH A COMMIT-UNRESOLVED cf553eb2… does not resolve to a commit
```

A resolved commit that is reachable **only** through `refs/jj/keep/…` must keep evaluating (rows 10, 1b: rc 0/1,
not a refusal) — the repair's `cat-file -e <rev>^{commit}` preserves this, and the lane's 1142 `refs/jj/keep` refs
make it a live shape, not a hypothetical.

---

## 3. Findings (residues at the repaired HEAD `2201778e`)

**F1 — `SKILL.md:250` still misdescribes the exit-2 cell (documented class ≠ produced class).**
The row reads `2 usage / malformed register / non-40-hex rev / non-regular or symlinked register`. At HEAD the tool
also exits 2 for a **40-hex revision that does not resolve to a commit** (absent object, blob, tree, and either
flag), whose stderr class is `REFUSAL REV-UNRESOLVED`. Confirmed unchanged at HEAD:

```
git show 2201778e:SKILL.md | grep -n r37-citation-reconcile   # identical exit-2 cell to base ed30b7f5
```

**F2 — `SKILL.md:250` omits two finding classes the repaired bytes can print.** `tools/souji-citation-reconcile.py`
at HEAD emits `COMMIT-ANCESTOR-ERROR` (line 221) and `RECEIPT-REV-ANCESTOR-ERROR` (line 307); the row's exit-1
enumeration lists neither, and no fixture case exercises them (`git grep ANCESTOR-ERROR` at HEAD matches only the
tool). They are reachable — a commit object whose parent is missing (corrupt/partial clone) makes
`merge-base --is-ancestor` exit 128 while `cat-file -e <c>^{commit}` succeeds:

```
hash-object -t commit -w --literally  -> c641f389b64ae1686572fa4427dc288425b8a637
cat-file -e c641f389^{commit}         -> rc 0
merge-base --is-ancestor c641f389 <rev> -> rc 128  "Could not read 5555…5555"
base: rc 1  MISMATCH A RECEIPT-REV-NOT-ANCESTOR receipt.txt at c641f389…
head: rc 1  MISMATCH A RECEIPT-REV-ANCESTOR-ERROR receipt.txt at c641f389…
base: rc 1  MISMATCH A COMMIT-NOT-ANCESTOR c641f389… is not an ancestor of f1b77b63…
head: rc 1  MISMATCH A COMMIT-ANCESTOR-ERROR c641f389… ancestry of f1b77b63… could not be evaluated
```

So the base mislabelled a git *error* as "not an ancestor" (the same collapse R11 named, one arm deeper); the repair
is right to distinguish it, but the class is undocumented. In a shallow clone the analogous shape degrades to
`RECEIPT-REV-UNRESOLVED` (finding), measured: `cat-file -e <side>^{commit}` rc 128 in the depth-1 clone, both tools
`rc 1  MISMATCH A RECEIPT-REV-UNRESOLVED receipt.txt at b1ee7128…  SUMMARY cells=2 mismatches=5`.

**F3 — `--root` not a repository is refused under the wrong class.** Head rc 2 is correct; the message
`REFUSAL REV-UNRESOLVED: --rev ed30b7f5… does not resolve to a commit` names the revision although the revision
exists in the lane and the *root* is not a work tree. A `REFUSAL ROOT-NOT-REPO` (or a `rev-parse --git-dir`
precheck) would keep the exit code and stop misdirecting the operator.

**F4 — two `merge-base` subprocesses per register row.** Head lines 306 and 309 each call
`ancestor_status(root, row["receipt_rev"], args.rev)`; the `elif` chain re-runs the same git command for every row
whose status is not `error`. One call bound to a local variable halves the git process count of the receipt arm
(11 rows in `census/round-37/citation-cells.tsv` → 11 avoidable subprocesses per run).

**F5 (imprecision, not a defect) — "unresolvable revision" in the docstring.** The Exit line says
`2 usage / malformed register / unresolvable revision`, but a tag name, `HEAD` or a `refs/jj/keep/…` name *is*
resolvable and is still refused (`REFUSAL USAGE`). The tool's contract is "40-hex object id naming a commit or
refuse"; the docstring wording should say so.

---

## 4. Verdicts

| check | verdict |
|---|---|
| Base builds a complete exit-code matrix over the requested shapes (40-hex absent, blob, tree, tag name, 12-hex, 40-hex commit, `HEAD`, keep-only commit, `--register-rev` absent/valid, plus uppercase, empty, `--register-rev` blob/tree/tag, register-path-absent, non-repo root) | **PASS** — 21 synthetic rows + 9 lane-byte rows, each with rc, first MISMATCH, SUMMARY presence |
| Base defect reproduced (R11): findings + `SUMMARY` + rc 1 for a revision that never resolved to a commit | **PASS (defect confirmed)** — absent/blob/tree on synthetic and lane bytes; rc 1, `mismatches=22/11/4/3` |
| Non-40-hex shapes (`tag`, `HEAD`, 12-hex, `refs/jj/keep` name, uppercase, empty) already refused with rc 2 and no findings at base | **PASS** — `REFUSAL USAGE: --rev must be 40-hex`, empty stdout |
| `--register-rev` unresolvable is rc 2 at base (harm leg L3) and stays rc 2 at head | **PASS** — absent/blob/tag rc 2 both; class tightens `USAGE`→`REV-UNRESOLVED`; **tree** flips 1→2 (row 17) |
| Keep-only (`refs/jj/keep`) commits still evaluate after the repair | **PASS** — lane `5a2b4926…` rc 0 `SUMMARY cells=11 mismatches=0` on both revisions |
| Findings still exit 1 for every finding class at a resolved commit | **PASS** — six classes + clean rc 0, identical strings on both revisions |
| The repaired bytes satisfy the "must be exit 2" set of §2 | **PASS for absent/blob/tree/non-40-hex/`--register-rev`; PARTIAL for `--root`-not-a-repo** (rc 2, wrong class — F3) |
| Registry row (`SKILL.md:250`) matches the bytes it describes at `2201778e` | **FAIL** — F1 (exit-2 cell omits the resolution refusal) and F2 (two finding classes unlisted, reachable but unfixtured) |
| Base was able to print findings for a revision it never resolved, which the contract must forbid | **CONFIRMED** — 4 baselines: `40hex-absent rc1/4 findings`, `blob rc1/4`, `tree rc1/3`, lane blob `rc1/22`, lane tree `rc1/11`, non-repo root `rc1/33` |

No byte of the lane was changed by this seat: the two tool revisions were extracted with `git show` into scratch and
executed there; `census/round-39/preregistration.txt`, `c1-items.tsv`, the `*-counter.py` specs and every frozen
receipt were read-only. No commit, push, add, stash or jj command was issued. No tool was installed or upgraded.
Only file written outside scratch: this report.

**Blockers:** none. **Risk carried to the L1:** F1/F2 are documentation-vs-bytes mismatches of the same species C1's
R10/R11 items police; if `SKILL.md:250` is not corrected in this round, C2's L4-style "docstring matches the classes
it raises" reading is true for `souji-worktree-drift.py` and false for `souji-citation-reconcile.py`.
