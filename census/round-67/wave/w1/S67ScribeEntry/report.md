# S67ScribeEntry — round-67 corpus paperwork (scribe seat)

Lane `souji-shokunin` (`/home/vgpnk/Projects/shokunin/souji-shokunin`), wave `round-67/w1`. Seat type:
scribe (leaf member, no dispatch). Scope: drafts only; **no lane file was edited**.

## Headline

**The L1 landed the round-67 corpus paperwork (commit `e41f022f`, 13:48:45 -0300) while this seat was still
gathering evidence.** The three drafted documents the seat was asked for are therefore superseded as *new
content*; what this seat delivers instead is (a) the drafts, marked as such, each carrying the scribe-side
verification of the landed bytes and the gaps the landing left open, and (b) **one actionable defect the
landing introduced**, measured two independent ways.

**The actionable finding:** the round-67 landing added a **new K1 registry finding** — the landed knowledge
entry cites **S298** in its front matter, but S298's `used-by` cell was not extended to name the new entry.
The fix is one cell plus the old→new log the SOURCES contract requires. Details and the controlled measurement
are in §2 and in `sources-rows.md` §3.

---

## Files written (all under this seat's own wave dir)

| path | bytes | what it is |
|---|---|---|
| `.ufo/waves/round-67/w1/S67ScribeEntry/knowledge-common-dir-route.md` | ~26 000 | draft/audit of `corpus/knowledge/common-dir-route-receipt-writer.md`: the landed entry's factual base re-measured independently, the W2 mechanism, the value-aware refusal shape, the scrub tuple, the named limits, and the K1 gap with its fix |
| `.ufo/waves/round-67/w1/S67ScribeEntry/sources-rows.md` | ~14 500 | the S300 row as landed, cell-by-cell against `SOURCES-CONTRACT-v1`; the S298/S299 rows (existing, not re-added); the S298 `used-by` correction with the controlled measurement; the row-count and census evidence |
| `.ufo/waves/round-67/w1/S67ScribeEntry/lesson-round-67.md` | ~13 000 | the `corpus/lessons/round-67.md` skeleton mapped onto the landed lesson, the two known L1 mistakes with re-measured evidence, and the wave-seat placeholders |
| `.ufo/waves/round-67/w1/S67ScribeEntry/log-entry-and-scorecard-rows.md` | ~12 000 | the LOG `## Round 67` entry shape and the SCORECARD Round-67 measurements-table shape, each checked against the landed text, with the placeholders filled from committed receipts and the bookkeeping the landing still owes |
| `.ufo/waves/round-67/w1/S67ScribeEntry/report.md` | this file | this report |

Scratch (removed at yield): `/fast/scratch/hyaku/souji-r67/S67ScribeEntry/` — the upstream captures, a
`--no-hardlinks` clone of the lane, two fixture repos, and the mutant outputs.

---

## 1. What this seat measured (all re-derived, not copied)

### 1.1 The upstream captures are sound

The scout seat delivered 16 files under `.ufo/waves/round-67/w1/S67ScoutSources/`. This seat fetched the same
upstream files independently from `raw.githubusercontent.com/git/git/v2.56.0/` and compared digests:
**all six source captures are byte-identical** (`environment.c` `5b52a5a1…`, `worktree.c` `da5c259a…`,
`setup.c` `8316b1ad…`, `run-command.c` `5cdcbacc…`, `repository.c` `7fb5a64b…`, `environment.h` `6dc06c6a…`).
The scout's `environment.html` (the live git(1) page) is byte-identical to the round-66 capture — the page did
not change between rounds.

### 1.2 All 25 located quotes re-slice; one offset does not reproduce raw

The scout's `quotes.tsv` has 25 rows. Re-sliced with a whitespace-collapsing byte matcher over the captured
bytes: **24/25 EXACT**, every quote ≤25 words (max 25). One row differs:

> `environment.html` @ 189753 → the match is at **189853 (delta +100)**. The 100 bytes before the sentence in
> the raw HTML are the anchor markup; the sentence itself is present exactly once.

The landed lesson's Gate already states the match test is whitespace-normalized ("line breaks and tabs in the
capture defeat the scout's byte offsets; the match is the check") — that is **true and load-bearing**. The gap
is only that the Gate does not name the one row whose stated offset differs raw. A reader running a raw
byte-equality test over all 25 rows sees 24/25 with no note explaining the 25th.

### 1.3 The W2 mechanism, re-measured on the host (git 2.56.0)

Fixture repo under this seat's scratch; `git rev-parse --show-toplevel` asserted equal to the fixture dir before
the first commit. With `GIT_COMMON_DIR` pointing at a copy of `.git` whose config carries `[core] fileMode =
false`:

* `rev-parse --git-common-dir` → the copy (the value is consumed as the repository's common dir);
* `config --get core.fileMode` → **`false`** under the redirect, **`true`** without it (config reads follow);
* `status --porcelain` → the tracked ` M f.txt` **disappears** under the redirect (the mode change is hidden);
* `cat-file -p <blob>` succeeds against the copy's object store and fails once the copy's `objects/` is removed
  (the object store follows too).

The upstream code agrees: `setup.c:310-319 get_common_dir()` returns the env value verbatim when set;
`repository.c:153-167 repo_set_commondir()` stores it as `repo->commondir` with `different_commondir = 1`.

### 1.4 The frozen predicates verify, re-run

* **C1** — the frozen counter re-run against the **landed candidate** in a scratch clone:
  `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0
  regress=PASS`, `EXIT=0`. The frozen target, met. W1/W2 refuse `RECEIPT-ENV-COMMONDIR-MISMATCH`; W3 (equal
  value) accepts — the Q22 value-aware shape, not a presence refusal.
* **C2** — the r67 counter at the pinned state `c13fbb4e`: `FINDING SCOPE-OVERREACH s5`; `SUMMARY rows=5
  findings=1 verdict=FAIL`; `EXIT=1`. Exactly one finding, the frozen kind.
* **Kill power** — both mutants rebuilt by the frozen recipe: `reverted-rule --selftest` →
  `m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`, `cases=17 fail=1`, `EXIT=1`; `enum-weakened` at
  the pinned state → `findings=0 verdict=PASS`, `EXIT=0`. Both frozen kill-power targets hold.

### 1.5 The preregistration digest transcriptions, re-measured

| attempt | commit | C1 Population digest length | relation to the true 64-hex digest |
|---|---|---|---|
| 1 | `832a4d43` | **63** | truth minus the `f` at index 39 |
| 2 | `b3aa70fe` | **63** | same string as attempt 1 |
| 3 | `d874bf0d` | **62** | truth minus `1f` at index 40 |
| 4 | `4c61efcb` | **64** | = the measured `sha256sum` of the committed matrix blob |

Freeze-checker reproductions (in a scratch clone): attempt 2 and attempt 3 each → `FINDING C1 POPULATION-DIGEST
… has no sha256=<64 hex>` + `SUMMARY claims=2 findings=1`, `EXIT=1`; attempt 4 → `SUMMARY claims=2 findings=0`,
`EXIT=0`. At attempt 1 the checker prints **two** findings — the digest **and**
`C2 CONTROL-ADDED-NOT-BEFORE-FREEZE`.

**Discrepancy worth recording.** The landed lesson's M1 row states the attempt-2 length as **63 hex** and the
attempt-3 length as **62 hex** — both confirmed correct here. But the **frozen, never-edited** prereg
headers say something different:

> attempt-3 header: "…a transcribed extra character (**65 hex**, rejected by the freeze checker POPULATION-DIGEST)"
> attempt-4 header: "attempt 2 transcribed **65 hex** and attempt 3 transcribed 62 hex by hand"

The committed attempt-2 blob carries **63** hex, and both transcriptions are **deletions** of truth characters,
not an "extra character". So the frozen narrative of the defect mis-states the length by two hex digits and
mis-states its direction, while the lesson's own numbers are right. The record does not reconcile the two. The
fix is a lesson note, **not** a prereg edit (the prereg is frozen).

---

## 2. The actionable finding — the landing introduced a new K1 registry finding

### 2.1 What the check says

`tools/souji-registry-agreement.py` (registered at `SKILL.md:265` as the lane gate `souji-registry-agreement`)
has a K1 arm that enforces QUALITY **Q62**'s bidirectional binding: *"every S### cited in the front-matter
`source:` lines of a corpus/knowledge/*.md entry must be a row whose `used-by` lists that entry."*

The landed entry's front matter cites **S298 and S300**:

```
$ git show HEAD:corpus/knowledge/common-dir-route-receipt-writer.md | grep -o "S[0-9]\{3\}" | sort -u
S298
S300
```

`S300`'s `used-by` names the new entry. **`S298`'s does not** — the landing commit changed exactly one line of
`corpus/SOURCES.md` (the appended `| S300 | …` row) and left S298's `used-by` cell untouched:

```
$ git diff 4c61efcb… 11a96e07… -- corpus/SOURCES.md | grep -E "^[+-]\| S(298|299|300)"
+| S300 | git setup.c common-dir resolution and git(1) § ENVIRONMENT VARIABLES at tag v2.56.0 — …
```

### 2.2 The measurement

Calling the K1 arm at three revisions of the lane:

| revision | K1 findings |
|---|---|
| freeze `4c61efcb` (before any r67 paperwork) | **4** — all pre-existing (S251 ×2, S146, S110) |
| landing `11a96e07` | **5** — the four plus **`K1 cited-not-in-used-by S298 corpus/knowledge/common-dir-route-receipt-writer.md`** |
| current tip `36200ad8` | **5** — unchanged |

**The r67 landing added the fifth, and it is the round's own entry.**

### 2.3 The fix, and two controlled measurements that establish it

`SOURCES-CONTRACT-v1` rule 2 permits exactly one in-place edit to an existing row: *"Only `status`, `recheck`
and `used-by` change in place, and each change is logged old→new in the round lesson."* So the correction is a
one-cell edit to S298's `used-by` plus the old→new log. Nothing else changes:

```
-| S298 | … | mined | 2026-11-05 | on-release | corpus/knowledge/caller-env-routes-receipt-writer.md |
+| S298 | … | mined | 2026-11-05 | on-release | corpus/knowledge/caller-env-routes-receipt-writer.md, corpus/knowledge/common-dir-route-receipt-writer.md |
```

**Measurement 1 — a fixture built from the ACTUAL landed lane bytes** (`corpus/SOURCES.md` + the three relevant
entries at `36200ad8`, committed in a fixture repo under this seat's scratch):

| fixture state | K1 findings for S298/S299/S300/common-dir |
|---|---|
| as landed | **`K1 cited-not-in-used-by S298 corpus/knowledge/common-dir-route-receipt-writer.md`** — the defect reproduces on the real bytes |
| after the one-cell S298 `used-by` edit | **0** — the finding is cleared |

**Measurement 2 — a second, independent fixture** built from the freeze revision's `SOURCES.md` plus the r66
entry, the r67 entry and the S300 row, run through the same two states: the defect reproduces in state A and
clears in state B, identically.

**Two constraints on the fix, both measured:**

1. **Extend S298 only.** The r67 entry does **not** cite S299. A fixture state with S299's `used-by` extended
   and S299 uncited produces the mirror finding `K1 used-by-no-cite S299
   corpus/knowledge/common-dir-route-receipt-writer.md`. Extending S299 as well would trade one finding for
   another.
2. **The old→new must be logged in the round lesson** (contract rule 2). The landed LOG entry already has a
   **"Corrections (append-only; the frozen files are not edited)"** bullet — the natural home. And the sentence
   the correction makes false is in **`corpus/README.md:990`**: *"S300 added (…, rc 0, 223 rows). **S298/S299
   unchanged.**"* — which must be updated too.

### 2.4 Why neither gate that ran at landing saw it

* `tools/souji-landing-gate.py` does **not** invoke the registry-agreement arm — `grep -n "registry-agreement"`
  in that tool returns nothing. The arm is registered in `SKILL.md:265` as a separately invoked gate.
* `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` passes at the landed revision
  (rc 0, `ok`, 223 rows) because its `E11` check only verifies that a **`mined`** row's `used-by` paths **exist
  on disk**. It does not check the reverse direction.

So only the K1 arm sees this; running it before the round closes is what catches it.

### 2.5 A second, independent consideration — is S298 the scope-correct citation?

S298's scope cell enumerates six variables: `GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES,
GIT_NO_REPLACE_OBJECTS, GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM and GIT_CONFIG_NOSYSTEM` — **`GIT_COMMON_DIR` is
not among them.** The row whose scope is *exactly* "what GIT_COMMON_DIR redirects to when explicitly set" is the
pre-existing **S125** (`git(1) § ENVIRONMENT VARIABLES, GIT_COMMON_DIR`; `used-by`
`corpus/knowledge/git-repo-structure-common-dir.md`), and this seat confirmed the sentence the entry quotes is
present in S125's own capture (`census/round-25/sources/git.1.txt`, sha256 `da58bd50…`, at byte 71550).

This matters because the entry cites S298 for the git(1) GIT_COMMON_DIR contract sentence — a claim outside
S298's recorded scope. Two viable corrections, both leaving the K1 finding resolved:

* **(a) extend S298's `used-by`** (the measurement above) — smallest change, but the entry keeps a citation
  outside S298's scope;
* **(b) re-point the git(1) sentence to S125** and extend S125's `used-by` instead — scope-correct, and the
  K1 finding clears the same way (measured in a fixture: with the entry citing S300 + S125 and S125's `used-by`
  extended, the S298/S125/S300 hits are 0).

S300's own `teaches` cell already carries the git(1) contract sentence as part of its grounded line, so the
entry's S298 citation is not the only carrier of that fact.

---

## 3. Two smaller record gaps (both measured)

1. **One located-quote offset does not reproduce raw** — `environment.html` @ 189753 → 189853 (delta 100); the
   other 24 rows are EXACT (§1.2). The Gate's whitespace-normalization sentence is true; naming the one row
   closes the disclosure.
2. **A dangling pre-landing commit.** `git log --all -- census/round-67/preregistration-attempt2.txt` returns
   the landed `b3aa70fe` **and** `5b57138076b7de3410aa9bce1ce83959e60eb94e` (parent `832a4d43`, 13:28:31
   -0300), which is **not an ancestor of `master`** and is in no branch. Its attempt-2 blob also carries 63 hex
   (not a different digest variant) — it is a stray pre-landing commit. Unreachable from any ref, so it cannot
   affect the freeze, but it is unreferenced history that the lesson's chronology sweep does not mention.

---

## 4. The landed paperwork, checked against its contract

| item | verdict |
|---|---|
| S300 row shape | **conforms.** 11 columns (NF=13), `kind=code`, `tier=A`, `status=mined`, `opened=2026-11-05`, `recheck=on-release`, `used-by` names the entry; the anchor names the file, function, tag and capture digests; the scope states its own exclusion. No `|` inside any cell. |
| S300 `teaches` | one grounded benefit, two quoted spans (the `setup.c` line + the git(1) contract) — both halves teach the same fact, and the Gate separates them by capture. |
| S300 capture digests | `setup.txt` `8316b1ad…` and `doc-git.txt` `050c5330…` — **both confirmed byte-identical** to this seat's independent fetch. |
| S298 / S299 | correctly **not** re-added; unchanged. |
| registry census | 222 → 223 rows; malformed-row count 0; `scripts/sources-census.sh validate … souji` → rc 0, `ok`. |
| coverage map | `tools/souji-coverage-agreement.py` at the tip → `grounded=27 mapped=27 dangling=0 mismatches=0`. |
| knowledge entry | the landed entry declares `ground: F4-adjacent` **after** the H1 (line 7), the same placement as its three F4-adjacent siblings, so the coverage-agreement instrument does not count it as grounded and no map row is required — consistent with the lane's existing pattern. |
| LOG `## Round 67` | shape satisfied: claims, freeze chronology, wave w1, landed, measured, named trade, corrections, sources, assimilation, tools, scratch. The "Named trade (C1, operator ruling needed)" bullet keeps the relative-value trade out of the verdict — the r66 precedent. |
| SCORECARD Round-67 table | shape satisfied: six columns, two rows, closing sentence naming the trade and no score change. **Every number in the table was reproduced by this seat** from committed receipts or by re-running the frozen instruments (§1.4). |
| lesson `corpus/lessons/round-67.md` | `## Gate` (sources, admitted, rejected-inside-the-entry, sourced claim, census, assimilation, probes), `## Claims`, `## Mistakes` M1–M10, named limits, sweep, verdicts. |

---

## 5. Findings, ranked

1. **[actionable] The landing introduced a new K1 registry finding** — the landed entry cites S298; S298's
   `used-by` was not extended to name the entry. One cell + the contract's old→new log fixes it; **measured to
   clear** on the actual landed bytes. See §2.
2. **[actionable] A frozen-header / lesson mismatch** — the frozen attempt-3 and attempt-4 headers say "65 hex"
   for attempt 2; the committed attempt-2 blob carries 63 hex, and both transcriptions are deletions, not an
   "extra character". The lesson's M1 numbers are right; the record does not reconcile them. A lesson note (not a
   prereg edit) closes it. See §1.5.
3. **[disclosure] One located-quote offset does not reproduce raw** — `environment.html` @ 189753 → 189853
   (delta 100), 24/25 exact. The Gate's whitespace-normalization note is true; naming the row closes it. §3.1.
4. **[hygiene] A dangling pre-landing commit** `5b571380` (attempt-2 file, not an ancestor of `master`, in no
   branch). Unreachable, so harmless to the freeze; worth one line in the chronology sweep. §3.2.
5. **[curation, for the L1's judgement] Is S298 the scope-correct citation** for the git(1) GIT_COMMON_DIR
   sentence, or is the pre-existing S125? S298's scope enumerates six other variables; S125's scope is exactly
   this claim. Both routes clear the K1 finding; §2.5 gives the measurements.

**None of these is a claim change.** C1 and C2 keep their frozen predicates and their landed measurements; the
defects are in the corpus bookkeeping that sits beside them.

---

## 6. Out of scope / not done by this seat

* **No lane file was edited.** `tools/`, `census/`, `corpus/`, `SKILL.md`, `QUALITY.md`, `SCORECARD.md`,
  `LOG.md`, `MANIFEST.json`, `.ufo/state/` and every sibling repo are untouched by this seat.
* **No commit, push, or mutating git/jj command** was run against the lane, a sibling repo, or anywhere else.
  The only commits this seat made were inside its own scratch fixture repos (identity `-c
  user.email=t@t -c user.name=t`), each created by `mktemp -d -p /fast/scratch/hyaku/souji-r67/S67ScribeEntry`
  with `git init -q` and `git rev-parse --show-toplevel` asserted equal to the fixture dir before the first
  commit. The lane was read with read-only plumbing only (`git show`, `git log`, `git status`, `git rev-parse`,
  `git ls-tree`, `git merge-base`, `git diff`).
* **No counter, gate, selftest or formatter was run against the live lane tree.** The frozen C1/C2 counters and
  the frozen mutant recipe were run in a `--no-hardlinks` clone of the lane under this seat's scratch, reading
  committed bytes; the lane working tree was never written. `tools/souji-freeze-check.py` was run the same way.
  `tools/souji-coverage-agreement.py` and the K1 arm of `tools/souji-registry-agreement.py` read committed bytes
  at named revisions.
* **No tool was installed or upgraded** this round — no `pacman`, `uv`, `npx` or binary install, so there is no
  tool/version/channel entry to record. The host's git 2.56.0 was used as found. `pacman` remains PAUSED
  host-wide; no pacman transaction, no service restart, no sysctl read or write, no sudo use.
* **No network probe against a provider API.** The only network fetches were to
  `raw.githubusercontent.com/git/git/v2.56.0/` (upstream git source, the same URLs the S300 row names) and
  `git-scm.com` via the scout's committed capture.
* **No credential material** appears in any delivered file.
* **The wave's sibling seats' findings are not restated.** This seat did not read the other seats' reports
  except the scout's captures (the source bytes the S300 row is bound to) and the executor's candidate bytes via
  the lane's committed candidate; every measurement reported here is this seat's own re-derivation.

## 7. Recommendation to the L1

1. Apply the one-cell **S298 `used-by`** correction and log the old→new in the lesson (contract rule 2);
   update `corpus/README.md:990` ("S298/S299 unchanged"), which the correction makes false. Run the K1 arm
   before closing: `python3 -B tools/souji-registry-agreement.py --root . --rev <tip> --list-rev <prereg>` —
   it should print `mismatches=0` with the four pre-existing findings gone from the r67 delta.
2. Add the M1 addendum (§1.5) and the one-row quote-offset disclosure (§3.1) to the lesson.
3. Consider whether the git(1) GIT_COMMON_DIR sentence should be cited from **S125** rather than S298 (§2.5).

The scratch root `/fast/scratch/hyaku/souji-r67/S67ScribeEntry/` was removed at yield, per the wave contract.
