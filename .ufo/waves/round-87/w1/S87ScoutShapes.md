# S87ScoutShapes — round 87 shape reconnaissance (TQ1 / NE1 / C2)

Seat: S87ScoutShapes (scout, leaf member, no subagent dispatch). Lane: souji-shokunin.
Scope: are the two new rows' shapes (TQ1, NE1) and the C2 newline-path shape REAL in this lane's
history, or synthetic-only?

All numbers below are measured, not asserted. Every command is read-only against the lane
(`git -C <LANE> …`, `git show`, `git grep`, `git ls-files -z`, `git cat-file --batch`). No fixture
repo was committed to, no lane file was written outside this seat directory and this report.
Scratch lived under `/fast/scratch/hyaku/souji-r87/S87ScoutShapes/` and was deleted before yield
(disclosure below).

Lane tip observed during the scan moved forward under the L1 (`6e502c5c…` → `b0a64c94…`); all
history-wide scans are over `git rev-list --all` and are therefore tip-independent. The base used for
population checks is each population's own PINNED base, taken from the counter's `POPS` table
(`census/round-87/c1-pointer-counter.py:129-148`).

---

## 0. Summary of verdicts

| Shape | What the row needs | Count in the lane's history | Verdict |
|---|---|---|---|
| **TQ1** (m16, `_whole` punctuation disjunct) | a real QUARANTINE TARGET path, or the L06 TOKEN, sitting at a **sentence-final period** inside a line the counter's `_declared` reads (SKILL.md / LOG.md / SCORECARD.md / corpus/) | **0** authority-scope instances over the whole history; **0** load-bearing for any of the **2** real QUARANTINED rows (P14, L06) at both their base and the harness base | **synthetic-only** (as the prereg already states) — but see §1.3, the *general* path-at-sentence-end shape IS real and common (1853 occurrences / 34 distinct paths in the authority scope) |
| **NE1** (m12, R0 token-on-line) | a committed population row whose DECLARED LINE does not carry its TOKEN at the population's base | **1** such row in the pinned pointer populations: `census/round-87/c1-items.tsv` row **I87E** (LOG.md:3166, token on 3165) — this round's own new row | **synthetic-only in the pinned pointer populations** — but **1 real prior instance exists** in a committed CONTROL: `census/round-78/controls/variants/c2-K-d-shifted-population.tsv` row **L01** (LOG.md:28, token on 27) |
| **C2** (K4 `-z` status arm) | a real lane path whose name carries a newline or tab | **6** tracked paths with an embedded newline (0 with a tab), committed since round 4; **1** of them is a **live tracked lane path** (`tests/vault/vadv54-run/r/nl/first\nsecond.md`) | **real-at-least-once** — and the filed K4 tool reproduces the exact defect on the lane's own path (see §3.3) |

---

## 1. TQ1 — the `_whole` punctuation disjunct (m16)

### 1.1 The seat-spec command, verbatim

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
git grep -n -E '\.ufo/quarantine/[^ `]*\.($| )' -- SKILL.md LOG.md SCORECARD.md corpus/
```

**Count: 0** (exit 1) at the tip, and **0** over the whole history of those four paths
(`git rev-list --all -- SKILL.md LOG.md SCORECARD.md corpus/` = 1247 revisions, each grepped; no hit).

Three quoted instances **do not exist** in the authority scope — so I quote the nearest real neighbours
instead, with their exact trailing bytes:

| Where | Path | Byte after the path | Is it a sentence-final period? |
|---|---|---|---|
| `SKILL.md:117` | `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` | `` ` `` (backtick, 0x60) | no |
| `corpus/lessons/round-17-verifier-spotcheck.md:99` | `.ufo/quarantine/round-17/…/dot-git-empty-stub` | `` ` `` (backtick) | no |
| `corpus/pointer-exemptions.tsv:4` | `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` | `\t` (tab, 0x09) | no |
| `LOG.md:946` | `.ufo/quarantine/round-17/…` | `` ` `` (backtick) | no |

Authority-scope quarantine-path occurrences at the tip: **3** distinct paths
(`tq1_scan.py` → `tq1_scan.json`), and the first-byte histogram of what follows is
`` ` `` ×2, `\t` ×1 — **no period anywhere**.

### 1.2 Over the WHOLE history, all tracked files (blob-level, one pass)

Every blob that ever existed in the lane (17 621 blobs, via `git rev-list --all --objects` +
`git cat-file --batch`) scanned with the EXACT seat-spec regex:

**4 hits, in 4 distinct files** (`exact_scan.py` → `exact_scan.json`):

1. `census/round-77/records/wave-w1/mk-spec.py` — match `.ufo/quarantine/. `
   (a bare directory reference followed by a period and a space — the "any path under .ufo/quarantine/." phrasing,
   not a leaf)
2. `census/round-77/records/wave-w1/w1-dispatch.json` — same string, inside a JSON task prompt
3. `census/round-77/records/wave-w1/w1-spec.json` — same string, inside a JSON task prompt
4. `census/round-78/records/wave-w1/seats/S78MutCounter/repro.txt:44` —
   `.ufo/quarantine/round-17/.ufo/NOT-THE-L0. rev ecc6ec0d (1-7), then 6f44938f (8). No lane file was written.`

Only #4 is a genuine **leaf** at a sentence end, and it is a *seat repro note*, not an authority file
the counter's `_declared` reads. The other three are the bare directory `.ufo/quarantine/` itself.

**Verdict for the TQ1 shape as the seat spec words it: synthetic-only.** The lane has never carried a
quarantine leaf at a sentence end in SKILL.md / LOG.md / SCORECARD.md / corpus/.

### 1.3 The mechanism check (what m16 actually gates) — the sharper measurement

m16 is not about quarantine paths. m16 drops the PUNCTUATION DISJUNCT of `_whole`
(`census/round-87/c1-pointer-counter.py:260-275`):

```python
after_ok = (not after or after[0] not in PATHCH
            or (after[:1] in (b".", b",", b";", b":") and (len(after) < 2 or after[1] not in PATHCH)))
```

`PATHCH` = `A-Za-z0-9 . _ / @ + ~ -`. So `,` `;` `:` are **not** path bytes and are already accepted by
the FIRST clause — the disjunct is **load-bearing only for a period** (`.` IS a path byte). This
distinction matters and is easy to get wrong: a naive "path followed by `;`" search over-reports by
several orders of magnitude.

Corrected measurement over every blob in the lane's history (`m16_scan.py` → `m16_scan.json`):

* **L06 TOKEN** `tests/vault/vadv54-run/p/p6repo/.git` immediately before a sentence-final period:
  **1** occurrence in the whole history, and it is
  `census/round-87/c1-false-row-harness.py` — **this round's own harness** writing
  ``f.write(f"\n- quarantine slot `{q6}lemma-stub` keeps tests/vault/vadv54-run/p/p6repo/.git.\n")``.
  (A second near-miss exists at `census/round-79/records/wave-w1/seats/S79MutCounter/fixture.txt`
  where the token is followed by `; ` — that is accepted by the FIRST clause, so m16 is NOT load-bearing
  there. Only 2 hits in 405 token occurrences have the disjunct firing at all, and only 1 of those is a
  period.)
* **QUARANTINE TARGET path** immediately before a sentence-final period: **0** in the whole history.
* **ANY real FILE PATH** at a sentence end, authority scope, whole history (`auth_realpaths.py`):
  **1853 occurrences / 34 distinct paths** — e.g. `census/round-18/seat-audit-adjudication.json.`
  (LOG.md), `corpus/lessons/round-25.md.` (SCORECARD.md), `tools/souji-size-census.py.` (LOG.md).
  So the *general* shape "a path at a sentence end" is common and real in the lane's prose.

### 1.4 Is m16 load-bearing on any REAL population row? — the number that matters

`_whole` is called from exactly one place, `_declared` (`:254`):

```python
return any(_whole(target.encode(), l) and _whole(token.encode(), l) for l in lines)
```

and `_declared` runs only for the `QUARANTINED` class (`:464`). The pinned populations contain exactly
**2** QUARANTINED rows — `P14` (r77) and `L06` (r78), both with target
`.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub`.

`m16_declared.py` re-implements `_whole` with and without the disjunct and runs the real `_declared`
git grep (SKILL.md, LOG.md, SCORECARD.md, corpus/) at BOTH the population's pinned base
(`d4f51563…` / `a8558d41…`) and the harness base `e65538e7…`:

> **QUARANTINED rows in the pinned populations: 2
> (population, revision) pairs where the m16 disjunct is LOAD-BEARING for the token or target: 0**

A second, independent measurement over ALL 69 rows of the five pinned populations
(`m16_real_rows.py` → `m16_real_rows.json`) — token and ledger-target occurrences on each item's
declared base line:

> rows where the m16 disjunct is LOAD-BEARING for the token or the target: **0**
> rows where the m16 disjunct fires at all (load-bearing or not): **1**
> — `r77 P01 SCORECARD.md:202` token `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`
> (fires on a `,`/`;`-style boundary already covered by the first clause; **not** load-bearing).

**Verdict: TQ1 is synthetic-only, and the prereg's stated limit is correct and correctly scoped.**
Nothing in the lane's own history makes m16 load-bearing; only the r87 fixture's R10 declaration does.
The row is a *new* clause binding, not a re-derivation of a historical instance — which is precisely
what the frozen wording says ("TQ1's declaration is synthetic fixture text written for this round").

**Caveat worth passing to the L1 (not a falsification):** the row is a genuine clause binding, but the
shape it binds — *a path at a sentence end* — is real and common in the lane's prose (1853 occurrences,
34 distinct paths, §1.3). What is synthetic is only the specific **quarantine-leaf** instantiation and
the fixture rev R10. The frozen wording already says this ("proves only that `_whole` accepts a token
at a sentence end, not that every declaration shape in the lane's history is read"). My measurement
confirms the wording is not widened by this wave: no artifact produced by r87 falsifies it.

---

## 2. NE1 — the R0 token-on-line guard (m12)

### 2.1 The command

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
python3 -B .ufo/waves/round-87/w1/S87ScoutShapes/ne1_scan.py
```

(`ne1_scan.py` / `ne1_wide_scan.py` / `pop_survey.py` — read-only; the logic is: for every row of a
population with the `(id, file, line, token, digest)` shape, read the item's file blob at the
population's PINNED base and assert `token in blob[int(line)-1]`.)

### 2.2 The count

`pop_survey.py` sweeps **every** committed census TSV whose columns match the pointer-population shape
(`id, file, numeric-line, token`) — 8 files — and checks each at its pinned base:

```
census/round-77/c2-population.tsv  @ d4f515637884:  rows=35  off-line=0
census/round-78/c2-population.tsv  @ a8558d410e98:  rows=22  off-line=0
census/round-78/controls/variants/c2-K-d-shifted-population.tsv @ a8558d410e98: rows=22 off-line=1
    OFF-LINE ('L01', 'LOG.md', '28', '.ufo/scopes/souji-mint-20261018/mint-roster-scan.json',
              'token-not-on-declared-line (on [27])')
census/round-85/c1-items.tsv        @ 705fa1385c4c:  rows=3   off-line=0
census/round-86/c1-items.tsv        @ 705fa1385c4c:  rows=4   off-line=0
census/round-87/c1-items.tsv        @ 705fa1385c4c:  rows=5   off-line=1
    OFF-LINE ('I87E', 'LOG.md', '3166', 'census/round-84/records/c1-after.txt',
              'token-not-on-declared-line (on [3165])')
=== TOTAL: rows=91 off-line=2 ===
```

Two further populations checked for the same shape (different column layouts, so handled separately):

* `census/round-44/c1-population.tsv` — columns `line, token, class, reason`, file = `SCORECARD.md` at
  the r44 base `55d7af6f…`: **rows=70 off-line=0** (`r44_scan.py`).
* `census/round-32/c1-items.tsv` and `census/round-33/c1-items.tsv` — columns
  `id, line, integer, units, rounds, context`; the `context` is a 40-byte excerpt around the integer
  and must sit on the declared line. At their pinned bases
  (`85b61a15…` / `6017a482…`, from each round's own enumerate script and header):
  * r32: **rows=44 off-line=1** — `L29`, line 170, context `remote-source-after.json18/18 (r31 L29)`.
    The excerpt is not on SCORECARD.md:170 at the r32 base; the *underlying* text
    `remote-source-after.json18/18` IS on that line, but the row's context cell carries an added
    `(r31 L29)` annotation, so the excerpt as written does not match.
  * r33: **rows=24 off-line=9** — K11, K12, K13, K15, K16, K18, K22, K24, K25. Their contexts are found
    at *other* lines (e.g. K11's context is on line 387, the row declares 166) or nowhere (K18, K22,
    K24, K25). Note the r33 counter treats the `line` column as the SCORECARD row the item came from
    (`census/round-33/c1-counter.py:199` binds `SCORECARD.md:<line>`), and the *command* in the context
    column is a separate field — so this is a partly different shape from the r87 pointer population's
    "the declared line carries the token". Recorded as a distinct observation, not folded into the count.

### 2.3 Three quoted instances

The two rows that ARE off-line in the pinned pointer populations:

1. `census/round-87/c1-items.tsv` line 6 —
   `I87E	LOG.md	3166	census/round-84/records/c1-after.txt	f:6d432ba4731e81e98758512eee30af0f3bc469827bfc8100173dfcaa94cd54bc`
   — declares LOG.md:3166; the token `census/round-84/records/c1-after.txt` is on **3165**.
   (This is the r87 row itself.)
2. `census/round-78/controls/variants/c2-K-d-shifted-population.tsv` line 2 —
   `L01	LOG.md	28	.ufo/scopes/souji-mint-20261018/mint-roster-scan.json	-`
   — the r78 population's L01 declares LOG.md:27; the shifted control declares **28**, so the token is
   NOT on the declared line. `diff` against the real population shows this is the ONLY difference
   (one line, `27` → `28`). It is a **committed** file, and the r78 control receipt
   `census/round-78/controls/c2-K-d-shifted-population.txt` records that the counter refuses it with
   `C2-COUNTER-FATAL: population sha256 7c3194b9… is not pinned`, EXIT=2.
3. `census/round-32/c1-items.tsv` line 45 —
   `L29	170	18 18	after,json,remote,source	20,21	remote-source-after.json18/18 (r31 L29)`
   — the context excerpt as written is not on SCORECARD.md:170 at the r32 base.

### 2.4 Verdict

**NE1 is synthetic-only in the pinned pointer populations, but the SHAPE has one real committed prior
instance elsewhere in the lane.**

* In the five pinned populations the only off-line row is `I87E` — this round's own row. So the row is
  a *new* clause binding, exactly as the frozen wording says ("NE1 is a deliberately malformed item, so
  it binds a diagnostic class, never a resolution rule").
* But the SHAPE is not synthetic-only: `census/round-78/controls/variants/c2-K-d-shifted-population.tsv`
  L01 is a **committed, real** row whose declared line does not carry its token. It was built as a
  *negative control* (an unpinned-population guard), so it does not exercise m12's R0 guard — it is
  refused earlier by the population-pin check. Still, it is a real committed off-line row, and it shows
  the lane has produced the shape before (r78), even if in a control rather than a measurement.
* Same for the r32/r33 populations (1 and 9 off-line rows) — but those are a different column shape
  ("context excerpt", not "token"), so I do not fold them into the pointer-population count.

**Falsification check against the frozen wording:** the wording says NE1 "declares a line its token is
NOT on (the token is on 3165)". My measurement reproduces that exactly (token on 3165, declared 3166,
verified at the pinned base `705fa138…`). Nothing produced by this wave falsifies it.

---

## 3. C2 — the K4 `-z` status arm and a newline path

### 3.1 The command (and a trap in the seat-spec form)

The seat spec offered `git ls-files -z | tr '\0' '\n' | grep -c $'\n'`-style checks. **That form gives a
false answer**, because `tr '\0' '\n'` destroys the NUL separator that keeps a path with an embedded
newline as ONE record — the newline inside the name becomes indistinguishable from the record separator:

```
$ git ls-files -z | tr '\0' '\n' | grep -c $'\n'
21364          # WRONG: this counts LINES, and grep -c $'\n' matches every line
$ git ls-files -z | tr '\0' '\n' | grep -cP '[\x09\x0a\x0d]'
0              # ALSO WRONG: the tr split the embedded newline into a line break, so no line contains one
```

The correct command splits on the raw NUL only:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files -z | python3 -B -c '
import sys
p=[x for x in sys.stdin.buffer.read().split(b"\0") if x]
print("total", len(p))
print("with tab/nl/CR:", sum(1 for x in p if any(c in x for c in (9,10,13))))'
total 21358
with tab/nl/CR: 6
```

(`c2_paths_scan.py` → `c2_paths_scan.json`; it also cross-checks `git ls-tree -r -z --name-only HEAD`,
which gives the same 6.)

### 3.2 The count — 6 tracked paths with an embedded newline, 0 with a tab

All six, byte-exact (`\n` = 0x0A), each in three copies across the tree:

```
.ufo/waves/round-26/assimilation/validate/tests/vault/vadv54-run/r/nl/first\nsecond.md
.ufo/waves/round-26/assimilation/validate/tests/vault/vadv54-run/r/scratch/.scratch/old\nname.log
census/round-26/waves/assimilation/validate/tests/vault/vadv54-run/r/nl/first\nsecond.md
census/round-26/waves/assimilation/validate/tests/vault/vadv54-run/r/scratch/.scratch/old\nname.log
tests/vault/vadv54-run/r/nl/first\nsecond.md
tests/vault/vadv54-run/r/scratch/.scratch/old\nname.log
```

Quoted instance: `git ls-files` prints the lane's own path in git's C-quoted spelling —
`"tests/vault/vadv54-run/r/nl/first\nsecond.md"`.

Provenance: the lane-root pair (`tests/vault/…`) was committed at `48a64d87` ("round-4 (amended): obsidian
claim withdrawn by operator; ledger-verify tool installed (impl-20, d312263a), CLI findings banked"); the
`census/round-26/…` copies at `765fe8bd` ("round-28: repair pointers, curate F4 primitives, capture wave
evidence"). The `.ufo/waves/round-26/…` copies are the wave-tree mirrors. The files are still on disk
(`ls -la tests/vault/vadv54-run/r/nl/` → `first\nsecond.md`, 23 bytes).

So the shape is **real-at-least-once**, and it is the lane's OWN live tracked path — not a synthetic
fixture. The r87 counter's KN3 row creates a *fresh* untracked `bad\nname2.txt` in a clone; the lane
already carries two real newline-named tracked paths.

### 3.3 A real reproducer: the filed K4 tool on the lane's OWN path

Scratch clone of the lane (`git clone --no-local`, `git rev-parse --show-toplevel` asserted equal to the
clone dir before any commit), with the lane's own tracked newline path modified in the worktree:

```
$ git status --porcelain                 # LINE form: what the r86 tool read
 M "tests/vault/vadv54-run/r/nl/first\nsecond.md"

$ git status --porcelain -z | od -c       # -z form: what the r87 tool reads
0000000       M       t   e   s   t   s   /   v   a   u   l   t   /   v
0000020   a   d   v   5   4   -   r   u   n   /   r   /   n   l   /   f
0000040   i   r   s   t  \n   s   e   c   o   n   d   .   m   d  \0
```

**Filed r87 tool** (`tools/souji-record-agreement.py`, byte-identical to the filed bytes) on that clone:

```
MISMATCH	K4	tests/vault/vadv54-run/r/nl/first\nsecond.md	uncommitted-path	M
```

**r86 base tool** (`census/round-87/controls/c2-before-base-tool.py`) on the same clone:

```
MISMATCH	K4	"tests/vault/vadv54-run/r/nl/first\nsecond.md"	uncommitted-path	M
```

The before arm records git's **quoted spelling** (`"…first\nsecond.md"`, with the literal backslash-n inside
the quotes); the filed tool records the **raw, C-escaped path** (`…first\nsecond.md`) with the record
staying one physical line. That is exactly the §2e defect the r87 K4 arm closes, reproduced on a REAL
lane path rather than a fixture.

And with an **untracked** path carrying the lane's own newline shape, the filed tool gives the KN3
shape verbatim:

```
$ git status --porcelain
?? "census/round-87/records/bad\nname2.txt"
$ python3 -B tools/souji-record-agreement.py --root <clone>
MISMATCH	K4	census/round-87/records/bad\nsecond.md	uncommitted-path	??
```

(record cell = the C-escaped raw path, class `uncommitted-path`, detail `??` — the KN3 exact shape.)

### 3.4 Untracked paths git status quotes in the lane RIGHT NOW — none

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain --untracked-files=all
 M LOG.md
 M PROVINCE.md
 M SCORECARD.md
 M census/round-87/c2-byte-arm.py
 M census/round-87/records/c1-c8-measured.txt
 M corpus/QUALITY.md
 M corpus/SOURCES.md
 M corpus/knowledge/own-tree-pointer-binding.md
?? census/round-87/controls/prefreeze/c1-after-prefreeze.txt
?? census/round-87/controls/prefreeze/c2-after-prefreeze.txt
?? census/round-87/records/c1-after.txt
?? census/round-87/records/c1-prefix-audit.txt
?? census/round-87/records/c2-real-lane.txt
?? census/round-87/records/c2-regression-fixtures.txt
?? census/round-87/records/source-capture-check.txt
?? census/round-87/records/sources-census-after.txt
?? census/round-87/records/sources-census-before.txt
?? corpus/knowledge/machine-parsed-path-spelling.md
?? corpus/lessons/round-87.md
?? plans/round-87.md
```

Quoted paths in that output: **0**. Raw `-z` records: **20**, of which **0** carry a tab or newline.
So no lane path is quoted *right now* — but the newline-named paths are TRACKED, so they never appear in
`git status` unless modified (which is when the C-quoted spelling bites, §3.3).

**Verdict: the C2 newline-path shape is REAL-at-least-once** — the lane carries two real newline-named
tracked paths (committed since round 4), and the filed K4 tool's `-z` arm is load-bearing on them. The
KN3 counter row's `bad\nname2.txt` is a synthetic *name*, but the *shape* it exercises is the lane's own.
Nothing in this wave falsifies the C2 wording.

---

## 4. Instrument-hash re-measurement (the assignment asks for it; a mismatch is a finding)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
sha256sum census/round-87/c1-false-rows.tsv census/round-87/c1-items.tsv census/round-87/c1-mutants.json \
          census/round-87/c1-pointer-counter.py census/round-87/c1-false-row-harness.py \
          census/round-87/c1-clause-battery.py census/round-87/c2-k4-counter.py \
          census/round-87/controls/c2-before-base-tool.py census/round-87/controls/souji-receipt-write.py
```

**No mismatch found.** Every one of the nine instrument hashes equals the frozen value in the
assignment. (See §5 for the exact output.)

---

## 5. Exact instrument-hash output

```
b066fa0fc686efdf96c8ebf21a32764070661796c3b4d6e5e99f8aad18669220  census/round-87/c1-false-rows.tsv
ce80195de8b978e5ed00a03c22c3f9911d841c9f277a2a736c730c455178d2e9  census/round-87/c1-items.tsv
9368b34234bf3f56f6c5f3913979ad891a35ac048a54e4ec749895900338d132  census/round-87/c1-mutants.json
fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b  census/round-87/c1-pointer-counter.py
d6f4e612f08fe2aaf2b789e4fe3a2a8a965318161bab2a4dae39363c86fabaef  census/round-87/c1-false-row-harness.py
b0c1472be3d0d957b5b88a92d6d622d895cdd693de5ce491329a6cf3d3c1aaeb  census/round-87/c1-clause-battery.py
4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e  census/round-87/c2-k4-counter.py
cf8753673b566da1e9a634d790dda70e93efef396f33bb3e42d4fad1425cbddc  census/round-87/controls/c2-before-base-tool.py
70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa  census/round-87/controls/souji-receipt-write.py
```

## 6. Files this seat wrote

All under the seat's own scope, `souji-shokunin/.ufo/waves/round-87/w1/S87ScoutShapes/`:

| File | What it does |
|---|---|
| `ne1_scan.py`, `ne1_wide_scan.py` | NE1 off-line scan over the (file, line, token) populations, at pinned bases and at the harness base |
| `pop_survey.py` | NE1 scan over every committed census TSV with the pointer-population column shape |
| `r44_scan.py`, `r32_scan.py`, `r32_base_pinned.py` | NE1 scan over the r44 / r32 / r33 populations (different column shapes) |
| `tq1_scan.py` | TQ1 quarantine-path occurrences with the exact trailing bytes, authority scope and whole repo |
| `exact_scan.py` | the EXACT seat-spec regex over every blob in the lane's history + the L06-token load-bearing contexts |
| `m16_scan.py` | the CORRECTED m16 load-bearing scan (period only) over every blob |
| `m16_real_rows.py` | m16 load-bearing over the 69 rows of the five pinned populations |
| `m16_declared.py` | m16 load-bearing at the point of use (`_declared` over authority lines) for the 2 QUARANTINED rows |
| `auth_sentence_end.py`, `auth_refined.py`, `auth_realpaths.py` | authority-scope path-at-sentence-end measurements over the whole history |
| `c2_paths_scan.py` | tracked/untracked/on-disk paths carrying a control character; git's quoted spelling |
| `*.json` | the raw outputs of the above |

## 7. Scratch disclosure

Scratch root `/fast/scratch/hyaku/souji-r87/S87ScoutShapes/` held: the two throwaway git repos
(`nlpath-fixture/`, `lane-nl/`, `lane-real-nl/`, `lane-clone/` — the lane clone used for the §3.3
reproducer) and the measurement outputs. **The scratch directory was deleted before yield.** Nothing was
left behind in `/tmp` (the one `/tmp/x` byte-copy in the §3.3 walkthrough was removed in the same step).
No lane file was modified; no commit, no push, no `git fetch`; the lane's git/jj state was only read.

## 8. Open questions for the L1 (no action taken)

1. **TQ1's shape is synthetic but the general shape is real.** If the L1 wants the C1 wording to claim
   the shape is *real*, the honest route would be a row bound to a real authority line where a path sits
   at a sentence end (34 such paths exist in the authority scope, e.g.
   `census/round-18/seat-audit-adjudication.json.` in LOG.md) — but that is a DIFFERENT clause-binding
   exercise and would need its own row and its own mutant. The frozen wording does not claim this, and
   I did not propose it.
2. **The r78 shifted-population control (L01, off-line) is a real committed instance of NE1's shape**
   but is refused by the population-pin guard before R0 is reached, so it cannot serve as a non-synthetic
   m12 row. If the L1 wants a NON-synthetic m12 row, this control file is the closest real artifact in
   the lane — but it would need a counter that reaches R0 on it, which the pinned-population guard
   prevents. Not added, not proposed as a row.
3. **The r32/r33 populations carry 1 and 9 off-line rows** under a "context excerpt" column shape. They
   are a different shape from the r87 pointer population's "token", and the r32/r33 counters do not use
   the context column as an on-line token check. I recorded them as observations; I did not classify them
   as NE1 instances. If the L1 wants them counted, the counting rule needs to be stated first.
