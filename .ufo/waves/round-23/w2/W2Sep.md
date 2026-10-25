# W2Sep — C1's separability from C2, against the landed bytes (w2, critic)

STATUS: **PARTIAL** — C1's *instrument* is separable from C2 (survives); C1's *evidence* is not
(falsified as independence: K1's receipt is one of C2's five bound receipts); C2 is separable from
C1 in both its counter and its verifier (survives). The report's separability sentence
(`.ufo/waves/round-23/report-draft.md:120-121`) is wrong as written and needs one clause changed.

Lane tip attacked: `102690017115cb202f292828c90b72705f69bf09` (landings `4765250`, `c0eeaa7`).
Tools as landed: `tools/souji-record-agreement.py` sha256 `617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9`
(350 lines, equals the blob at `4765250` and at the tip), `tools/souji-receipt-run.py` sha256
`6bb623b8e8ce40028aee740ee40d600963d253e494048ce1ef121d5007d63e45`.

Every verdict below is against those two **committed blobs** (`git cat-file blob <tip>:<path>`),
measured in `--no-local` clones of the tip. The live worktree drifted while this seat ran — at
report time `tools/souji-receipt-run.py` hashes `2761290d6bc6e1753d971c33640be925e26f5016f31c7c426f2614019079f5c5`
(`M`) and `corpus/lessons/round-23.md`, `tests/fixtures/r23-record-agreement.py`,
`census/round-23/records/refusal-stale-digest.txt` are also modified by sibling seats. The
`tools/souji-record-agreement.py` worktree bytes still equal the tip blob (`617f4c96…`), so S1-S3
read the same lesson/report text they name only if it has not since been rewritten; re-read those
lines before editing them.

All runs read-only. Scratch `/var/tmp/souji-r23-w2-W2Sep/` (`git clone --no-local` mirrors `mA`-`mD`,
removed at end); no lane write, no `git add/commit/checkout`, no `jj`, no `rm`/`mv` in the lane, no
pacman, no installs. Lane-side runs used `GIT_OPTIONAL_LOCKS=0 python3 -B` so `git status` cannot
refresh the lane index.

## Q1 — does C1 verify with C2's runner never landed?

Mirror `mA` = `--no-local` clone of the lane at the tip, plus an empty placeholder file under
`census/operator-sweep-20261019/` so the mirror reproduces the lane's one exempted `??` row
(operator contents never read). `mB` = `mA` with `tools/souji-receipt-run.py` deleted from the
working tree.

Baseline (mirror reproduces the lane's clean state):

```
$ cd /var/tmp/souji-r23-w2-W2Sep/mA
$ GIT_OPTIONAL_LOCKS=0 python3 -B tools/souji-record-agreement.py \
    --rev 102690017115cb202f292828c90b72705f69bf09 --root /var/tmp/souji-r23-w2-W2Sep/mA
keys=4 records=4 occurrences=17 mismatches=0
EXIT=0
```

The task's literal command (C2's tool deleted from the scratch copy):

```
$ cd /var/tmp/souji-r23-w2-W2Sep/mB
$ GIT_OPTIONAL_LOCKS=0 python3 -B tools/souji-record-agreement.py \
    --rev 102690017115cb202f292828c90b72705f69bf09 --root /var/tmp/souji-r23-w2-W2Sep/mB
MISMATCH	K4	tools/souji-receipt-run.py	uncommitted-path	D
keys=4 records=4 occurrences=17 mismatches=1
EXIT=1
```

Same tree, K4 dropped (`--no-worktree`; K4 is a live-worktree observation by design and the counter
carries the flag for exactly this):

```
$ cd /var/tmp/souji-r23-w2-W2Sep/mB
$ GIT_OPTIONAL_LOCKS=0 python3 -B tools/souji-record-agreement.py \
    --rev 102690017115cb202f292828c90b72705f69bf09 --root /var/tmp/souji-r23-w2-W2Sep/mB --no-worktree
keys=4 records=4 occurrences=17 mismatches=0
EXIT=0
```

**Verdict Q1: survives — instrument-separable, with a confound that must be disclosed.** The single
mismatch the literal command produces is `K4 / uncommitted-path / D`: deleting a tracked file *is*
uncommitted round work, which is precisely what K4 (D1) exists to count. It is not a dependency on
C2's code. Three independent checks agree:

1. No reference exists between the tools: `grep -n "souji-receipt-run\|tool_sha256" tools/souji-record-agreement.py` → no match (rc=1).
2. C1 reads a closed path set — `K1_RECEIPT`, `SCORECARD.md`, `K2_RECEIPT`, `LOG.md`,
   `census/round-22/attempt2/slice-verdicts.tsv`, `corpus/README.md`, `corpus/lessons/round-22.md`,
   `uncommitted-exemptions.tsv` — none of which is either tool, so the tool's presence at `--rev`
   cannot reach K1-K3.
3. At the base revision the runner does not exist at `--rev` at all and C1 still executes:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e 1208bfb:tools/souji-receipt-run.py
fatal: path 'tools/souji-receipt-run.py' exists on disk, but not in '1208bfb'      # ABSENT at rev
$ cd /var/tmp/souji-r23-w2-W2Sep/mA
$ GIT_OPTIONAL_LOCKS=0 python3 -B tools/souji-record-agreement.py --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --root /var/tmp/souji-r23-w2-W2Sep/mA
MISMATCH	K1	census/round-23/records/declared-evidence-after.tsv	receipt-absent	not in tree at 1208bfb…
MISMATCH	K2	LOG.md:1478	uncorrected	'assertions=56 resolved=53 skipped=33 mismatches=3' has no later 'superseded by' line
MISMATCH	K2	LOG.md:1495	uncorrected	'1 present' has no later 'superseded by' line
MISMATCH	K2	LOG.md:1495	uncorrected	'1 refused' has no later 'superseded by' line
MISMATCH	K3	corpus/README.md:440	tally-disagree	1 present != receipt 2 present
MISMATCH	K3	corpus/README.md:440	tally-disagree	1 refused != receipt 0 refused
MISMATCH	K4	census/operator-sweep-20261019/	uncommitted-path	??
keys=4 records=3 occurrences=13 mismatches=7
EXIT=1
```

`--no-worktree` at the same rev gives `mismatches=6`, byte-identical to the committed control
`census/round-23/records/agreement-control-base.txt` (6 rows, same six). None of the six is
attributable to the runner's absence.

## Q1b — does C1 verify with C2's *artifacts* never landed?

**Verdict Q1b: falsified — C1 is evidence-coupled to C2, by declaration.** The first row of the base
control above is the witness: `K1 … census/round-23/records/declared-evidence-after.tsv
receipt-absent`. That file is not a neutral TSV — it is one of C2's bound receipts:

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
5
  …declared-evidence-after.tsv  gate-check-at-first-landing.tsv  gate-check-at-lane-base.tsv
  …gate-check-c3.tsv            agreement-after.tsv
$ python3 -B tools/souji-receipt-run.py verify --root . census/round-23/records/declared-evidence-after.tsv
verify=ok rev=9301d98c1c689c79741f0f1ba1f171138d20af07 tool=tools/souji-declared-evidence.py tool_sha256=65817d0d…
```

and the preregistration names it as a C2 target artifact (`preregistration.txt`, C2 target:
"declared-evidence before, declared-evidence after, gate-check before, gate-check after"). So at any
rev where C2 never landed, C1's K1 is `receipt-absent` and `M>=1` by construction. This is *not* a
hidden regression: C1's own frozen text requires it ("the receipt must exist in the tree at
`--rev`", "the VALUE is always derived from a receipt"). It must be disclosed, not repaired.

K1 does **not** need C2's binding field. `k1()` in the landed tool requires only a counts tuple plus
a `rev=` header; `tool_sha256=` is never consulted (`grep -n "unbound\|tool_sha256\|digest"
tools/souji-record-agreement.py` → no match, rc=1). Predicate test on the landed module:

```
$ python3 -B -c "…load tools/souji-record-agreement.py…; m.counts_of(<text>)"
1 rev= + counts, NO tool_sha256 : ('assertions=63 resolved=63 skipped=40 mismatches=0', '9301d98c…')
2 rev= + counts, fake tool_sha256: ('assertions=63 resolved=63 skipped=40 mismatches=0', '9301d98c…')
3 counts only, no rev= header    : ('assertions=63 resolved=63 skipped=40 mismatches=0', '')
4 no counts line                 : None
```

A hand-made receipt with `rev=` and the counts line satisfies K1 (case 1). Therefore
`w1/CritPrereg.md:186-192` (F17: "350-line `k1()` rejects a receipt without a `tool_sha256=` header
(`receipt-unbound`) … **not separable at the current bytes**") and its table row at
`w1/CritPrereg.md:199` are **stale against the landed bytes**: the `receipt-unbound` clause is gone,
the repair landed, and F17's present-tense claim is falsified. F17 may appear in wave-2 text only in
the past tense, as the report draft already does.

## Q2 — does C2 verify without C1?

Mirror `mC` = `mA` with `tools/souji-record-agreement.py` deleted from the working tree; `mD` = `mC`
with C1's only receipt (`agreement-after.tsv`) removed.

```
$ cd /var/tmp/souji-r23-w2-W2Sep/mC
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
5
$ for r in census/round-23/records/*.tsv; do python3 -B tools/souji-receipt-run.py verify --root . "$r"; done
agreement-after.tsv            verify=ok rev=476525026cdb179f2d49441e1cb6c6f7316f3124 tool=tools/souji-record-agreement.py tool_sha256=617f4c96…   rc=0
declared-evidence-after.tsv    verify=ok rev=9301d98c1c689c79741f0f1ba1f171138d20af07 tool=tools/souji-declared-evidence.py  tool_sha256=65817d0d…   rc=0
gate-check-at-first-landing.tsv verify=ok rev=a211e4d1bf6ea592670d16269f34e9f67f33e8b3 tool=tools/souji-gate-check.py      tool_sha256=d85c2696…   rc=0
gate-check-at-lane-base.tsv    verify=ok rev=1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd tool=tools/souji-gate-check.py      tool_sha256=d5ed0805…   rc=0
gate-check-c3.tsv              verify=ok rev=476525026cdb179f2d49441e1cb6c6f7316f3124 tool=tools/souji-gate-check.py      tool_sha256=d5ed0805…   rc=0

$ cd /var/tmp/souji-r23-w2-W2Sep/mD
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
4
```

**Verdict Q2: survives, in both directions.** The counter is unchanged at 5 with C1's tool deleted
(it is a plain file count), every receipt still verifies because `blob_sha_bytes()` reads the tool
blob from git objects at the receipt's `rev`, never the worktree — so `agreement-after.tsv` verifies
even though the tool it names is gone from disk — and C2's `>=4` target survives losing C1's only
receipt (4 remains: the three gate-check/declared-evidence receipts plus `gate-check-c3`). No
reference exists in the other direction either: `grep -n "record-agreement\|souji-record"
tools/souji-receipt-run.py` → no match (rc=1).

## Findings

| # | where | class | required action |
|---|---|---|---|
| S1 | `.ufo/waves/round-23/report-draft.md:120-121` — "The three claims were also checked for separability: C1's predicate reads only its own receipts and the records" | false as landed: C1's K1 receipt `census/round-23/records/declared-evidence-after.tsv` **is** one of C2's five bound receipts (C2's own counter lists it; `verify=ok`; prereg C2 names it as a target artifact) | **fix** (one clause): "C2 is separable from C1 in counter and verifier; C1 needs no C2 code, but its K1 evidence file is one of C2's bound receipts, so C1 is instrument-separable and receipt-coupled" |
| S2 | same row's C1 command (`.ufo/waves/round-23/report-draft.md:112`) | the separability probe as written is confounded: deleting a tracked file makes K4 fire (`uncommitted-path D`), so `mismatches=1` there is D1 semantics, not a C2 dependency | **disclose**: state that the separability probe must be `--no-worktree` (or rev-based); the literal run's `M=1` must not be quoted as C1 needing C2 |
| S3 | `corpus/lessons/round-23.md:130` — "the C2 coupling (receipt-unbound) was removed for separability" | accurate about the clause, silent about the surviving file coupling | **fix** (qualifier): append "clause removal restored predicate separability; the shared receipt file keeps C1 evidence-coupled to C2 by declaration (prereg C1 K1)" |
| S4 | `.ufo/waves/round-23/w1/CritPrereg.md:186-192, 199` (F17 / A7) | stale at landed bytes: no `receipt-unbound` clause exists (`grep` rc=1; a receipt with no `tool_sha256=` parses), so "not separable at the current bytes" is falsified | **fix in wave-2 text only**: never carry F17 in the present tense; the report draft's past-tense form is already correct |

No predicate change is proposed for any of these; every action is text. A predicate change
(e.g. dropping K1's receipt-existence clause) would be **would-invalidate** — after-data.

## Impacted axes

- **calibration (C1, lowest non-retired = 7)**: impacted. C1's K1 evidence is a C2 artifact, so a C2
  rollback moves C1 from 0 to 1 silently (`K1 receipt-absent`) — the claim's evidence is not
  self-contained. Declared in the frozen contract, so no target moves; the report text must not
  claim independence.
- **operability (C2)**: unaffected. Separable from C1 in counter, verifier and target threshold.
- **coverage (C3)**: untouched by this seat.

## Named limits (not repaired)

- No committed-deletion revision was synthesized: the contract forbids git/jj mutation, so "the C2
  tool never existed at `--rev`" is evidenced by (a) the base rev, where it is genuinely absent and
  C1 runs, and (b) `--no-worktree` on the deleted-worktree mirror — not by a new commit.
- K4 was exercised only in its live-worktree form; its non-reproducibility across seats is already a
  disclosed limit and was observed live: at the tip with the worktree as it stands,
  `python3 -B tools/souji-record-agreement.py --rev 1026900…` returns
  `MISMATCH K4 .ufo/waves/round-23/report-draft.md uncommitted-path ??` / `mismatches=1` — a sibling
  seat's in-flight draft, not a C1 defect. The `M=0` verdicts above are revision-scoped or taken in
  a mirror with a controlled worktree.
- The mirror's `census/operator-sweep-20261019/` entry is an empty placeholder file, never operator
  contents.
- Context, outside this seat's verdict: `census/round-23/records/agreement-after.tsv` records C1's
  own run at `4765250` with `rc=1` and one `K1 value-disagree` (SCORECARD quoted
  `assertions=55 resolved=52 skipped=33 mismatches=3` against the receipt's `63/63/40/0`); the tip
  now agrees. That is C1's after-state history, not separability.
