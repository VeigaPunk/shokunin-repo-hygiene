# W1RevExitContract — the citation tool's intended exit contract, reconstructed

seat: W1RevExitContract (revenger, leaf member)
round: 39 wave 1 (hyaku run 11)
lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
audited bytes: `2201778e7736af82e7d8a42dec2494f115bf3923` (HEAD when the tool was extracted; the tool and
`SKILL.md` are byte-identical at the later HEAD `2605bf20b90940f95282cbd6c65e80154ac6b2f2`, see §8)
base bytes: `ed30b7f5b77939c9073348d810730bc4f355708d` (lane base / C2 `--base-rev`)
tool under audit: `tools/souji-citation-reconcile.py` (336 lines at HEAD, 304 at base; `tool_sha=59f1e57d7af0`
as reported by the C2 counter's own digest)
verdict in one line: **the frozen C2 predicate is met at HEAD and the landed three-hunk diff is exactly the
minimal code change that makes it true; two statements remain false and both are prose — `SKILL.md:250`'s
exit-2 cell and its exit-1 class enumeration — plus three sentences that attribute the exit-2 promise to a
registry row that never carried it.**

I did not modify the tool. Every variant I measured is a copy under
`/fast/scratch/hyaku/souji-r39/W1RevExitContract/`.

---

## 1. Method

The contract exists in six kinds of artefact: the module docstring (two revisions of it), the gate-registry
row, the r37 and r38 prereg predicates, the r38 spot-check's R11 finding, the fixtures' literal case tables,
and the r39 frozen predicate plus its two counters. I read all of them, extracted base and HEAD tool bytes
with `git show`, and measured the tool's actual exit surface over fifteen constructed inputs in a private
repository, three times: base bytes, HEAD bytes, and a patched HEAD that closes the one remaining
tool-versus-prose divergence. A statement is "true" only if a command printed the thing it claims.

---

## 2. Every statement of the contract

### S1 — r37 docstring promise (base bytes, `tools/souji-citation-reconcile.py:45-46`)

```
45: Exit: 0 mismatches=0, 1 any mismatch (one MISMATCH line each), 2 usage /
46: malformed register / unresolvable revision. Read-only: git show only, no
```

Binds: three exit codes; "unresolvable revision" is an exit-2 cause. **This is the oldest statement of the
exit-2 arm and it predates the registry row.** It was never implemented (base `run()` resolved nothing).

### S2 — r39 restatement (HEAD bytes, `tools/souji-citation-reconcile.py:45-50`)

```
45: Exit: 0 mismatches=0, 1 any mismatch (one MISMATCH line each), 2 usage /
46: malformed register / unresolvable revision. A revision the counter cannot
47: resolve is a could-not-evaluate input, never a finding (r39 C2, r38 routed
48: defect R11): `--rev` and `--register-rev` must name a commit that resolves
49: (`git cat-file -e <rev>^{commit}`), otherwise the run refuses with
50: `REFUSAL REV-UNRESOLVED` and exits 2 before any row is read.
```

Binds, in order: the mechanism (`cat-file -e <rev>^{commit}`), the class (`REFUSAL REV-UNRESOLVED`), the code
(2), the ordering (before any row is read), and the scope (the two *flags*; the row-level `receipt_rev` arm is
not named).

### S3 — commit-arm class list (HEAD bytes, `tools/souji-citation-reconcile.py:30-36`)

```
33:              `expected` on a SUMMARY line. Mismatch classes: COMMIT-UNRESOLVED,
34:              COMMIT-NOT-ANCESTOR, COMMIT-UNNAMED, COMMIT-RECEIPT-ABSENT,
35:              COMMIT-RECEIPT-DISAGREES. A seven-column row skips the arm
```

Binds a closed enumeration of five commit classes. The tool prints a sixth (`COMMIT-ANCESTOR-ERROR`, line 221).

### S4 — registry row, exit-2 cell (`SKILL.md:250`)

```
… 2 usage / malformed register / non-40-hex rev / non-regular or symlinked register
```

Binds exit 2 to four causes. An unresolvable 40-hex revision is not among them. Byte-identical at base and at
HEAD (measured, §7 C4).

### S5 — registry row, exit-1 enumeration (`SKILL.md:250`)

```
1 any MISMATCH line — citation (`ANCHOR-COUNT`, `EXPECTED-MISSING`, `RECEIPT-UNNAMED`, `STALE-PRESENT`),
receipt (`RECEIPT-REV-UNRESOLVED`, `RECEIPT-REV-NOT-ANCESTOR`, `RECEIPT-ABSENT`, `RECEIPT-DISAGREES`)
or commit (`COMMIT-UNRESOLVED`, `COMMIT-NOT-ANCESTOR`, `COMMIT-UNNAMED`, `COMMIT-RECEIPT-ABSENT`,
`COMMIT-RECEIPT-DISAGREES`)
```

Binds a closed enumeration of thirteen finding classes. The tool prints fifteen (the two extras are
`COMMIT-ANCESTOR-ERROR` and `RECEIPT-REV-ANCESTOR-ERROR`).

### S6 — registry row, invocation cell (`SKILL.md:250`)

```
python3 tools/souji-citation-reconcile.py --root LANE --rev REV --register TSV --register-rev REV
```

Binds the *pinned* form (r37 A2.6 pins `--register-rev` in every command string). `--register-rev` is optional
in `argparse` (`:330`), so the row is the canonical invocation, not a signature. No conflict.

### S7 — r37 prereg predicate (`census/round-37/preregistration.txt:16-21`, `:143-145`)

```
16:   Counter: tools/souji-citation-reconcile.py --root <lane> --rev <landing>
17:            --register census/round-37/citation-cells.tsv
18:   Target (frozen): `SUMMARY cells=9 mismatches=0`, rc 0, …
143:   C1 = "souji-citation-reconcile prints cells=11 mismatches=0 at the landing revision
144:         (register pinned with --register-rev), and every register receipt carries its
145:         expected token" — amended by A1.1 and A1.3;
```

Binds rc 0 for the green run only. **The r37 round states no exit-2 arm.** It does state the correction
convention I rely on in §5 (`:24-25`): "corrections are append-only lines anchored R37-C1-<n> (SCORECARD,
prereg) or **in-place current-registry cells (SKILL, lesson Claims)**".

### S8 — r38 prereg predicate and A7 (`census/round-38/preregistration.txt:27-34`, `:206-214`)

```
27: PREDICATE (frozen): … prints `SUMMARY cells=10 mismatches=0`
30: and exits 0; and at the base revision … prints
32: `mismatches>=6` and exits 1.
213: refuses a `receipt_rev` that does not resolve or is not an ancestor (`RECEIPT-REV-UNRESOLVED`,
214: `RECEIPT-REV-NOT-ANCESTOR`), …
```

Binds the **row-level** revision arms as exit-1 findings. This is the boundary against S2: flags refuse, rows
report.

### S9 — r39 frozen predicate (`census/round-39/preregistration.txt:47-62`, amendment `:116-123`)

```
47: Two runnable contracts disagree with their documentation, both reproduced on the base bytes:
48: (a) R11 — `tools/souji-citation-reconcile.py` never resolves `--rev`: a mistyped or non-commit
49: revision collapses to "not an ancestor" and the tool exits 1 with findings instead of the
50: could-not-evaluate exit 2 its SKILL registry row promises; …
56: … Legs: L1
57: unresolvable `--rev` (base: rc 1 with findings; new: rc 2, `REFUSAL REV-UNRESOLVED`), L2 `--rev`
58: naming a blob (same classes), L3 `--register-rev` unresolvable stays rc 2 (harm), …
```

Binds rc 2 + `REFUSAL REV-UNRESOLVED` for an unresolvable `--rev` and for a blob `--rev`; binds `--register-rev`
to stay at rc 2. Amendment A1 (`:116-123`) moves the `register-rev-gone` case's expected class from `not at` to
`REV-UNRESOLVED`, tighter-only.

### S10 — r38 spot-check, R11 (`corpus/lessons/round-38-verifier-spotcheck.md:187-192`)

```
187: 11. **R11 — the citation counter never resolves `--rev`.** `git merge-base --is-ancestor` is read as
188:     "1 = not an ancestor, other non-zero = error" by the arm's own premise (S239/S244), but the code
189:     collapses every non-zero to "not an ancestor": a mistyped audited revision yields `mismatches=20`
190:     and rc 1 instead of a could-not-evaluate exit 2 (`W2RevHarm` F1, reproduced by that seat). `SKILL.md`'s
191:     exit row never declares that case. Resolve `--rev` with `cat-file -e <rev>^{commit}` and split exit
192:     1 from 128.
```

Binds three things: the defect (collapse of every non-zero into "not an ancestor"), the *observation that
SKILL's exit row never declared the case*, and the repair shape (resolve with `cat-file -e <rev>^{commit}`;
distinguish child status 1 from 128).

### S11 — r39 fixture (`tests/fixtures/r39-citation-rev.py:4-19`, `:107-117`)

```
 4: r38 routed defect R11: the counter never resolved `--rev`. …
 7: `mismatches=N` and exit 1 (findings) instead of the could-not-evaluate exit 2 its SKILL registry
 8: row promises.
12:   rev-unknown        a 40-hex revision that does not exist            -> rc 2, REV-UNRESOLVED
13:   rev-blob           a 40-hex blob id                                 -> rc 2, REV-UNRESOLVED
14:   rev-tree           a 40-hex tree id                                 -> rc 2, REV-UNRESOLVED
15:   rev-short          a short hex prefix                               -> rc 2, USAGE
16:   rev-symbolic       a tag-like name                                  -> rc 2, USAGE
17:   clean              the real commit                                  -> rc 0, mismatches=0
18:   register-rev-gone  an unresolvable --register-rev                    -> rc 2, REV-UNRESOLVED
19:   register-absent    a --register absent at a resolvable revision      -> rc 2, "not at"
```

Binds the eight-case table. Its prose at `:7-8` also *attributes* the promise to SKILL.

### S12 — r39 C2 counter (`census/round-39/c2-counter.py:10-12`)

```
10:   L1  an unresolvable `--rev` for `tools/souji-citation-reconcile.py`: base collapses it to "not an
11:       ancestor" and exits 1 with findings; the SKILL registry row promises a could-not-evaluate
12:       exit 2.
```

Same attribution as S11.

### S13 — lane boundary note (`PROVINCE.md:279-281`)

```
279: `tools/souji-citation-reconcile.py` now resolves `--rev` and `--register-rev` (`REFUSAL
280: REV-UNRESOLVED`, exit 2), so a non-commit or absent revision is could-not-evaluate rather than a set
281: of findings; …
```

Binds the repaired behaviour and the class, without claiming a registry cell.

### S14 — r39 lesson (`corpus/lessons/round-39.md:19-20`, `:67`)

```
19: reproduced on the base bytes: R11 (`tools/souji-citation-reconcile.py` never resolved `--rev`, so a
20: blob, tree or absent revision produced findings and exit 1 instead of could-not-evaluate exit 2)
67: | R11 `--rev` never resolved | citation tool resolves both revisions, exit 2 | C2 |
```

Binds the disposition only.

### S15 — the row-level boundary fixture (`tests/fixtures/r38-counter-arms.py:12-13`, `:113`)

```
12:   receipt-rev-not-ancestor a receipt_rev that is not an ancestor of --rev -> RECEIPT-REV-NOT-ANCESTOR
13:   receipt-rev-unresolved   a 40-hex receipt_rev naming no commit -> RECEIPT-REV-UNRESOLVED
117: case("receipt-rev-unresolved", [row("R4", rev="a" * 40)], 1, ["RECEIPT-REV-UNRESOLVED"])
```

Binds a row-level unresolvable revision to **rc 1**, i.e. a finding. This is what stops S2's "never a finding"
from swallowing the row arm.

### S16 — the commit-arm fixture (`tests/fixtures/r38-citation-commit.py:148-167`)

Binds five commit classes at rc 1 (`commit-unresolved`, `commit-not-ancestor`, `commit-unnamed`,
`commit-receipt-absent`, `commit-receipt-disagrees`) and `malformed-commit` at rc 2 `REFUSAL USAGE`. No case
names an ancestry-evaluation error.

---

## 3. Measured exit surface

Private repository per run (`git init -q` in `$S/probe-exit.*`, `rev-parse --show-toplevel` asserted equal to
the repo before the first commit), one citation file, one receipt, one 7-column register row for the clean case
and 8-column rows for the two arm cases. `corrupt-parent` is a commit object written with
`git hash-object -t commit -w --literally` whose parent is `5555…5555`, so `cat-file -e <c>^{commit}` succeeds
and `merge-base --is-ancestor <c> <rev>` dies.

| case | base `ed30b7f5` | HEAD `2201778e` | patched copy |
|---|---|---|---|
| `clean` | rc 0 `SUMMARY cells=1 mismatches=0` | rc 0 same | rc 0 same |
| `rev-absent` (40-hex, no object) | **rc 1**, `MISMATCH K1 FILE-ABSENT …` + `RECEIPT-REV-NOT-ANCESTOR` | **rc 2** `REFUSAL REV-UNRESOLVED` | rc 2 same |
| `rev-blob` | **rc 1** `FILE-ABSENT` | **rc 2** `REV-UNRESOLVED` | rc 2 |
| `rev-tree` | **rc 1** `RECEIPT-REV-NOT-ANCESTOR` | **rc 2** `REV-UNRESOLVED` | rc 2 |
| `rev-short12` | rc 2 `REFUSAL USAGE: --rev must be 40-hex` | rc 2 same | rc 2 same |
| `rev-tag-name` (`v1`) | rc 2 `USAGE` | rc 2 `USAGE` | rc 2 `USAGE` |
| `rev-HEAD` | rc 2 `USAGE` | rc 2 `USAGE` | rc 2 `USAGE` |
| `rev-junk` (`nothex`) | rc 2 `USAGE` | rc 2 `USAGE` | rc 2 `USAGE` |
| `rev-unresolved` + malformed register | rc 2 `REFUSAL USAGE: unreadable register …` | **rc 2 `REFUSAL REV-UNRESOLVED`** | rc 2 same |
| `register-rev-absent` | rc 2 `REFUSAL USAGE: register … is not at …` | rc 2 `REFUSAL REV-UNRESOLVED: --register-rev …` | rc 2 same |
| `register-rev-short` (12-hex) | rc 2 `USAGE … not at` | rc 2 `REFUSAL REV-UNRESOLVED: --register-rev …` | rc 2 same |
| `register-absent-at-rev` | rc 2 `USAGE … not at` | rc 2 `USAGE … not at` | rc 2 same |
| `root-not-repo` | rc 1 (findings) | rc 2 `REFUSAL REV-UNRESOLVED: --rev …` | rc 2 same |
| `commit-arm-corrupt-parent` | rc 1 `COMMIT-NOT-ANCESTOR` | rc 1 `COMMIT-ANCESTOR-ERROR` | **rc 2 `REFUSAL ANCESTRY-UNRESOLVED`** |
| `receipt-arm-corrupt-parent` | rc 1 `RECEIPT-REV-NOT-ANCESTOR` | rc 1 `RECEIPT-REV-ANCESTOR-ERROR` | **rc 2 `REFUSAL ANCESTRY-UNRESOLVED`** |

Refusals are stderr-only and print no `SUMMARY` (measured, §7 C9). `argparse`'s own missing-argument error is
exit 2 as well (§7 C8).

Fixture scores: `tests/fixtures/r39-citation-rev.py` → HEAD `cases=8 pass=8 fail=0`, base
`cases=8 pass=4 fail=4`; `r37-citation-reconcile.py` → `cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED`;
`r38-citation-commit.py` → `cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED`;
`r38-counter-arms.py` → `cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED`. The frozen counter reads
`SUMMARY legs=6 pass=6 fail=0 harm=0`.

---

## 4. Conflicts and their resolution

**K1 — does anything promise exit 2 for an unresolvable revision?** S4 says no; S1, S2, S9, S11, S12, S13 say
yes. **Resolved: yes, exit 2 is the contract.** Authority order: the frozen predicate (S9) is the claim
contract and is machine-checked; S2 states the mechanism the code implements; S1 shows the promise predates
the registry row, so S4 cannot be its source. S4 is simply stale — it is the same cell at base and at HEAD
(§7 C4), so no one corrected it. This is exactly the defect class R6/R10 police (a registry row that does not
describe the runnable artefact), one round later.

**K2 — the two `ANCESTOR-ERROR` classes.** The tool prints `COMMIT-ANCESTOR-ERROR` (`:221`) and
`RECEIPT-REV-ANCESTOR-ERROR` (`:307`) at exit 1. S5 does not enumerate them, S3 does not enumerate the first,
and `git grep ANCESTOR-ERROR <HEAD> -- tests/ census/` returns nothing, so no fixture pins them either way.
**Resolved: the tool bytes are authoritative for what happens; the prose is authoritative for what is
intended, and the prose is silent.** That silence is the defect: an ancestry the counter could not evaluate is
the same species as a revision it could not resolve, and S2's own principle ("never a finding") plus R11's
"split exit 1 from 128" (S10:191-192) put it on the could-not-evaluate side. Two closures exist and both are
fixture-safe (§5).

**K3 — who promised the exit-2 arm?** S9:50, S11:7-8 and S12:11-12 say "its SKILL registry row promises".
S4's bytes say the row never did. **Resolved: the attribution is wrong; the operative requirement is right.**
Authority: S4 for what the registry says (it is the artefact being described), S1 for where the promise actually
lives. Three sentences are therefore stale claims of provenance — an R13-class defect, not a contract defect.

**K4 — "never a finding" versus `RECEIPT-REV-UNRESOLVED` at rc 1.** S2's first clause is broad; S8 and S15 pin
a row-level unresolvable `receipt_rev` at rc 1. **Resolved: no contradiction.** S2's second sentence names only
`--rev` and `--register-rev`, so the refusal arm is flag-scoped; the row arm keeps the r38 A7 shape. The
boundary is real and both sides are pinned by fixtures. Anyone reading S2's first clause alone will over-read
it; that is a wording risk, not a divergence.

**K5 — S3's closed five-class list versus `:221`.** Same defect as K2, one document earlier. Resolved the same
way: the enumeration must gain the class, or the class must stop existing.

**K6 — non-40-hex asymmetry between the two flags.** `--rev` non-40-hex → `REFUSAL USAGE: --rev must be 40-hex`
(`:243-245`); `--register-rev` non-40-hex → `REFUSAL REV-UNRESOLVED` (`:251-257`, measured). Both exit 2, so S4's
"non-40-hex rev" cell holds at the code level. **Resolved: asymmetry, not conflict.** S2's sentence ("must name
a commit that resolves") covers the `--register-rev` class; S4's cell covers the code. No fixture pins the
`--register-rev` non-40-hex class, so it is free to change later, but it need not.

**K7 — `root-not-repo` names the revision.** With `--root` pointing at a directory that is not a repository, HEAD
prints `REFUSAL REV-UNRESOLVED: --rev 61bc7048… does not resolve to a commit` although that revision exists in
the lane. Exit code is right (could-not-evaluate); the class misdirects the operator to the revision instead of
the root. **Resolved: precision defect, not a contract violation** — S2's claim is true *relative to that root*.

---

## 5. The minimal code change

### 5a. For the frozen contract: already landed, and it is minimal

The base→HEAD diff is three hunks (35 insertions, 3 deletions):

1. `run()` gains a 40-hex check's successor: `cat-file -e <rev>^{commit}` for `--rev`, then the same for
   `--register-rev`, both writing `REFUSAL REV-UNRESOLVED` and returning 2 **before** `parse_register`
   (`:246-257`).
2. `ancestor_status()` (`:204-211`) splits child status 0 / 1 / other into `yes` / `no` / `error` — R11's
   "split exit 1 from 128".
3. Both arms consume it: `COMMIT-ANCESTOR-ERROR` (`:221`) and `RECEIPT-REV-ANCESTOR-ERROR` (`:307`) instead of
   collapsing into `NOT-ANCESTOR`.

Necessity and sufficiency are both measured: removing it (base bytes) fails four of the eight r39 cases and
legs L1/L2/L5; with it, L1-L6 pass and all four consumer fixtures are green. No fixture had to be relaxed to
accept it — the r39 case table is the only fixture that names the new class, and it was frozen with the
predicate (amendment A1, tighter-only).

### 5b. The one remaining tool-versus-prose divergence, and its two closures

The two `ANCESTOR-ERROR` classes (K2/K5) are the only tool behaviour that no statement declares. Two ways to
make every statement true:

**Option D (documentation only, zero code).** Add to S5 the classes `COMMIT-ANCESTOR-ERROR` and
`RECEIPT-REV-ANCESTOR-ERROR`, and add to S3 the class `COMMIT-ANCESTOR-ERROR`. Cost: two in-place registry
cells and one docstring list. Risk: the registry then documents a finding that is really a could-not-evaluate,
which contradicts S2's principle and leaves R11's "split exit 1 from 128" true only at the child-status level.

**Option C (code, ~10 lines, measured green).** Make an ancestry the counter cannot evaluate a refusal rather
than a finding, exactly as S2 already does for a revision it cannot resolve:

```python
class AncestryError(Exception):
    pass

# commit_checks:
    if status == "error":
        raise AncestryError("%s ancestry of %s could not be evaluated" % (commit, rev))

# receipt arm:
        elif ancestor_status(root, row["receipt_rev"], args.rev) == "error":
            raise AncestryError("%s ancestry of %s could not be evaluated" % (row["receipt_rev"], args.rev))

# run(): the row loop inside
    try:
        for row in rows:
            …
    except AncestryError as exc:
        sys.stderr.write("REFUSAL ANCESTRY-UNRESOLVED: %s\n" % exc)
        return 2
```

plus the docstring's Exit line gains "ancestry could not be evaluated" and S4 gains the same clause and the
resolution clause of K1. I built exactly this copy
(`/fast/scratch/hyaku/souji-r39/W1RevExitContract/patched-cite.py`) and measured it: r39 `8/8`, r37 `16/16`,
r38-citation-commit `14/14`, r38-counter-arms `6/6`, and both corrupt-parent arms move to
`rc 2 REFUSAL ANCESTRY-UNRESOLVED` (§7 C7). **No fixture is relaxed**: none names the two classes, and the
`NOT-ANCESTOR` cases (dangling commit, `rc 1`) are untouched because a dangling commit's ancestry *evaluates*
to "no".

**Recommendation.** Option C plus the two prose amendments (S4's exit-2 cell gains the resolution clause; S3
and S5 need no class additions because the classes disappear). If the round prefers not to touch landed tool
bytes again in wave 1, Option D is the strictly smaller edit and is honest, provided the registry says the
class is an *evaluation failure* and not evidence about the citation. Either way, **S4's exit-2 cell must be
corrected** — that one is not optional: as written, the registry row denies a refusal the tool has performed
since HEAD.

Both edits are legal under the lane's own rule (S7:24-25: registry cells are corrected in place), and neither
touches the sixteen frozen C1 items: the only item anchored in `SKILL.md` is `R39-C1-06`, whose anchor is the
appended paragraph at `SKILL.md:283`, not the r37 row at `:250` (§7 C11).

---

## 6. Verdicts

| # | check | verdict |
|---|---|---|
| V1 | Exit contract reconstructed from all six artefact families, with file:line | **DONE** — S1-S16 |
| V2 | Frozen C2 predicate at HEAD (`legs=6 pass=6 fail=0 harm=0`) | **PASS** — measured (§7 C5) |
| V3 | R11's exit-2 arm implemented at HEAD (absent / blob / tree / register-rev) | **PASS** — rc 2 `REV-UNRESOLVED` for all four (§7 C2, C3) |
| V4 | R11's base arm still red (the repair is discriminating) | **PASS** — base rc 1 with findings; r39 fixture base `pass=4 fail=4` (§7 C3) |
| V5 | `SKILL.md:250` describes the tool it registers | **FAIL** — exit-2 cell omits the resolution refusal; exit-1 enumeration omits two reachable classes (K1, K2) |
| V6 | The promise's provenance as three artefacts state it ("its SKILL registry row promises") | **FAIL** — the promise is the r37 docstring (S1); the row never carried it (K3) |
| V7 | Ordering claim "refuses … before any row is read" | **PASS** — an unresolvable `--rev` beats a malformed register at HEAD; base inverts it (§7 C2) |
| V8 | No fixture relaxed by the repair | **PASS** — 8/8, 16/16, 14/14, 6/6, controls rejected (§7 C6) |
| V9 | Row-level versus flag-level revision boundary | **PASS** — row arm stays rc 1 per r38 A7 and `r38-counter-arms` (§7 C6); S2 scopes it |
| V10 | `--root` not a repository | **FAIL (precision)** — exit 2 is right, the class names the revision (K7) |
| V11 | Minimal code change stated and measured | **DONE** — §5a landed diff; §5b Option C measured green, Option D named |
| V12 | Tool left unmodified by this seat | **PASS** — `git status` shows no change to `tools/souji-citation-reconcile.py` (§7 C1) |

Two of these (V5, V6) are routing items for the L1: they are C1-class calibration defects in the registry row
and in two docstrings, they are not covered by any of the sixteen frozen C1 items, and they cannot be closed by
changing the tool alone.

---

## 7. Commands run, with observed output

All from `/home/vgpnk/Projects/shokunin/souji-shokunin` unless stated. `S=/fast/scratch/hyaku/souji-r39/W1RevExitContract`.

**C1 — lane state and tool identity**

```
$ git status --porcelain=v1
 M census/round-39/c3-counter.py
 M tests/fixtures/r39-citation-rev.py
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
$ git rev-parse HEAD
2201778e7736af82e7d8a42dec2494f115bf3923
$ git diff --stat ed30b7f5..HEAD -- tools/souji-citation-reconcile.py
 tools/souji-citation-reconcile.py | 38 +++++++++++++++++++++++++++++++++++---
 1 file changed, 35 insertions(+), 3 deletions(-)
```

`tools/souji-citation-reconcile.py` is **not** in the dirty list: the tool at HEAD is committed, and I changed
nothing in it.

**C2 — base and HEAD tool bytes extracted, then probed**

```
$ git show ed30b7f5…:tools/souji-citation-reconcile.py > "$S/base-cite.py"   # 304 lines
$ git show 2201778e…:tools/souji-citation-reconcile.py > "$S/head-cite.py"   # 336 lines
$ python3 -B "$S/probe_exit.py" "$S/head-cite.py"
clean                              rc=0   | SUMMARY cells=1 mismatches=0
rev-absent                         rc=2   classes=REV-UNRESOLVED | REFUSAL REV-UNRESOLVED: --rev 1111… does not resolve to a commit
rev-blob                           rc=2   classes=REV-UNRESOLVED | REFUSAL REV-UNRESOLVED: --rev cdfb3eb0… does not resolve to a commit
rev-tree                           rc=2   classes=REV-UNRESOLVED | REFUSAL REV-UNRESOLVED: --rev 3e1aa6fa… does not resolve to a commit
rev-short12                        rc=2   classes=USAGE | REFUSAL USAGE: --rev must be 40-hex
rev-tag-name                       rc=2   classes=USAGE | REFUSAL USAGE: --rev must be 40-hex
rev-HEAD                           rc=2   classes=USAGE | REFUSAL USAGE: --rev must be 40-hex
rev-junk                           rc=2   classes=USAGE | REFUSAL USAGE: --rev must be 40-hex
rev-unresolved+malformed-register  rc=2   classes=REV-UNRESOLVED | REFUSAL REV-UNRESOLVED: --rev 1111… does not resolve to a commit
register-rev-absent                rc=2   classes=REV-UNRESOLVED | REFUSAL REV-UNRESOLVED: --register-rev 1111… does not resolve to a commit
register-rev-short                 rc=2   classes=REV-UNRESOLVED | REFUSAL REV-UNRESOLVED: --register-rev 440fe1efc8f5 does not resolve to a commit
register-absent-at-rev             rc=2   classes=USAGE,not at | REFUSAL USAGE: register …/nope.tsv is not at …
root-not-repo                      rc=2   classes=REV-UNRESOLVED | REFUSAL REV-UNRESOLVED: --rev 440fe1ef… does not resolve to a commit
commit-arm-corrupt-parent          rc=1   classes=COMMIT-ANCESTOR-ERROR | MISMATCH K1 COMMIT-ANCESTOR-ERROR 7c551824… ancestry of 440fe1ef…
receipt-arm-corrupt-parent         rc=1   classes=RECEIPT-REV-ANCESTOR-ERROR | MISMATCH K1 RECEIPT-REV-ANCESTOR-ERROR receipt.txt at 7c551824…
```

**C3 — base tool on the same worlds (the defect, reproduced)**

```
$ python3 -B "$S/probe_exit.py" "$S/base-cite.py"
clean                              rc=0   | SUMMARY cells=1 mismatches=0
rev-absent                         rc=1   classes=RECEIPT-REV-NOT-ANCESTOR | MISMATCH K1 FILE-ABSENT doc.md at 1111…
rev-blob                           rc=1   classes=RECEIPT-REV-NOT-ANCESTOR | MISMATCH K1 FILE-ABSENT doc.md at cdfb3eb0…
rev-tree                           rc=1   classes=RECEIPT-REV-NOT-ANCESTOR | MISMATCH K1 RECEIPT-REV-NOT-ANCESTOR receipt.txt at 440fe1ef…
rev-unresolved+malformed-register  rc=2   classes=USAGE | REFUSAL USAGE: unreadable register …/missing.tsv …
register-rev-absent                rc=2   classes=USAGE,not at | REFUSAL USAGE: register …/reg.tsv is not at 1111…
root-not-repo                      rc=1   | MISMATCH K1 FILE-ABSENT doc.md at 440fe1ef…
commit-arm-corrupt-parent          rc=1   classes=COMMIT-NOT-ANCESTOR | MISMATCH K1 COMMIT-NOT-ANCESTOR 7c551824… is not an ancestor of 440fe1ef…
receipt-arm-corrupt-parent         rc=1   classes=RECEIPT-REV-NOT-ANCESTOR | MISMATCH K1 RECEIPT-REV-NOT-ANCESTOR receipt.txt at 7c551824…
```

Base collapses absent/blob/tree into findings (R11, reproduced) and mislabels a git error as "not an ancestor"
(the deeper collapse R11 names).

**C4 — the registry row is byte-identical at base and HEAD**

```
$ diff <(awk 'NR==250' "$S/SKILL-base.md") <(awk 'NR==250' "$S/SKILL-head.md")
IDENTICAL
$ awk 'NR==250' "$S/SKILL-base.md" | awk -F'|' '{print $5}'
 0 `mismatches=0`; 1 any MISMATCH line — citation (…), receipt (…), commit (…); 2 usage / malformed register / non-40-hex rev / non-regular or symlinked register
```

**C5 — the frozen C2 predicate at HEAD**

```
$ python3 -B census/round-39/c2-counter.py --root "$PWD" --rev 2201778e… --base-rev ed30b7f5… --scratch "$S"
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
rc=0
```

**C6 — consumer fixtures against HEAD bytes**

```
$ TMPDIR="$S" python3 -B tests/fixtures/r39-citation-rev.py --tool tools/souji-citation-reconcile.py --work "$S"
SUMMARY cases=8 pass=8 fail=0                      (rc=0)
$ TMPDIR="$S" python3 -B tests/fixtures/r39-citation-rev.py --tool "$S/base-cite.py" --work "$S"
SUMMARY cases=8 pass=4 fail=4                      (rc=1; FAIL: rev-unknown, rev-blob, rev-tree, register-rev-gone)
$ TMPDIR="$S" python3 -B tests/fixtures/r37-citation-reconcile.py --tool tools/souji-citation-reconcile.py --work "$S"
SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED
$ TMPDIR="$S" python3 -B tests/fixtures/r38-citation-commit.py --tool tools/souji-citation-reconcile.py --work "$S"
SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED
$ TMPDIR="$S" python3 -B tests/fixtures/r38-counter-arms.py --tool tools/souji-citation-reconcile.py --work "$S"
SUMMARY cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED
```

**C7 — the §5b Option C patch, measured (scratch copy only)**

```
$ python3 -B "$S/probe_exit.py" "$S/patched-cite.py"
commit-arm-corrupt-parent          rc=2   | REFUSAL ANCESTRY-UNRESOLVED: 7c551824… ancestry of 61bc7048… could not be evaluated
receipt-arm-corrupt-parent         rc=2   | REFUSAL ANCESTRY-UNRESOLVED: 7c551824… ancestry of 61bc7048… could not be evaluated
(all other rows identical to C2)
$ TMPDIR="$S" python3 -B tests/fixtures/r39-citation-rev.py     --tool "$S/patched-cite.py" --work "$S"
SUMMARY cases=8 pass=8 fail=0
$ TMPDIR="$S" python3 -B tests/fixtures/r37-citation-reconcile.py --tool "$S/patched-cite.py" --work "$S"
SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED
$ TMPDIR="$S" python3 -B tests/fixtures/r38-citation-commit.py  --tool "$S/patched-cite.py" --work "$S"
SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED
$ TMPDIR="$S" python3 -B tests/fixtures/r38-counter-arms.py     --tool "$S/patched-cite.py" --work "$S"
SUMMARY cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED
```

**C8 — usage exit and stream discipline**

```
$ python3 -B "$S/head-cite.py" --root . --rev 2201778e…
head-cite.py: error: the following arguments are required: --register
rc=2
$ python3 -B "$S/head-cite.py" --root . --rev 1111… --register census/round-38/cells.tsv 2>/dev/null
(no stdout)
$ python3 -B "$S/head-cite.py" --root . --rev 1111… --register census/round-38/cells.tsv 2>&1 >/dev/null
STDERR: REFUSAL REV-UNRESOLVED: --rev 1111111111111111111111111111111111111111 does not resolve to a commit
```

**C9 — no fixture names the two error classes**

```
$ git grep -n "ANCESTOR-ERROR" 2201778e… -- tests/ census/
(no match; rc=1)
```

**C10 — statement extraction**

```
$ awk 'NR>=41 && NR<=53' "$S/head-cite.py"     # S2, quoted verbatim in §2
$ awk 'NR>=25 && NR<=40' tools/souji-citation-reconcile.py   # S3
$ awk 'NR==250' SKILL.md                        # S4/S5/S6
$ awk 'NR>=10 && NR<=25' census/round-37/preregistration.txt ; awk 'NR>=138 && NR<=150' …
$ awk 'NR>=18 && NR<=48' census/round-38/preregistration.txt
$ awk 'NR>=44 && NR<=70' census/round-39/preregistration.txt
$ awk 'NR>=183 && NR<=196' corpus/lessons/round-38-verifier-spotcheck.md
$ awk 'NR>=270 && NR<=290' PROVINCE.md
$ awk 'NR>=14 && NR<=24' corpus/lessons/round-39.md ; awk 'NR>=62 && NR<=72' …
```

**C11 — the frozen C1 item list is not disturbed by a `SKILL.md:250` edit**

```
$ awk -F'\t' 'NR==1 || $2 ~ /SKILL/' census/round-39/c1-items.tsv
R39-C1-06	SKILL.md	R39-C1-06	r38-citation-commit,r38-drift-write-envelope,r38-drift-record,r38-drift-mutants	-
$ grep -n "R39-C1-06" SKILL.md
283:R39-C1-06 — four r38 counters had no registry row …
```

The only item anchored in `SKILL.md` anchors the appended paragraph at `:283`; the r37 row at `:250` is outside
every frozen item.

---

## 8. Housekeeping

- **Concurrent lane movement (disclosed, not measured by me).** The lane advanced from `2201778e` to
  `2605bf20b90940f95282cbd6c65e80154ac6b2f2` while this seat ran (`d4c1755`, `f8ba3f3`, `e9958ee`,
  `2605bf2`). `git diff --stat 2201778e..HEAD -- tools/souji-citation-reconcile.py SKILL.md` prints nothing, so
  the audited tool bytes and the registry row are identical at both revisions and every measurement in §3 and §7
  holds at HEAD. The worktree carries uncommitted `SKILL.md` edits by another seat (8 insertions, 8 deletions);
  I checked that row 250 is byte-identical to HEAD (`diff … && echo ROW-250-UNCHANGED` → `ROW-250-UNCHANGED`), so
  V5 still stands against the live worktree as well.
- Scratch: `/fast/scratch/hyaku/souji-r39/W1RevExitContract/` (base-cite.py, head-cite.py, patched-cite.py,
  SKILL-base.md, SKILL-head.md, probe_exit.py). Every fixture was passed `--work "$S"` and `TMPDIR="$S"`; the
  probe creates and removes its own `$S/probe-exit.*` repositories. **The directory is still on disk** (kept so
  the L1 can re-run C7 without rebuilding the patch); remove it with
  `rm -rf /fast/scratch/hyaku/souji-r39/W1RevExitContract`.
- No git or jj mutation was run anywhere: read-only `log`, `show`, `diff`, `status`, `rev-parse`, `grep` only.
  The only repositories created are the probe's private ones under `$S`, each asserted with
  `git -C "$D" rev-parse --show-toplevel` before its first commit.
- No tool installed or upgraded; no PATH directory, fleet-root file, frozen receipt, prereg or items TSV was
  touched. The only lane write is this report.
