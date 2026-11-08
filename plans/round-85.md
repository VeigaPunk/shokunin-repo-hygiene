# Round 85 — amendments to the frozen claims (pre-file falsification)

Written before the round report was filed. The frozen wording lives in `census/round-85/preregistration.txt`
(commit `43c630eb3983f5b5b51f8b46dd9e64899427378b`, F) and is not edited here: each amendment records what the
round's own artifacts falsified in that wording, and the narrower sentence the round now puts its name to. Numbers
are re-derived on committed bytes by non-author seats and by the L1; records under `census/round-85/records/` and the
wave's reports under `.ufo/waves/round-85/w1/`.

Wave evidence root: `.ufo/waves/round-85/w1/`.

## A0 — instrument corrections, before any claim score (not amendments to a claim)

- **A0.1 — the C2 counter leaked the previous row's forgery.** The first C2 run read `k4=1 named=no` on KF2/KF3 (the
  counter's own comment said `detail=''`): a forged index entry SURVIVES `git reset --hard` (reset does not rewrite
  an entry whose stat fields already match the checked-out path), so row N's forgery made row N+1 read dirty. Fix
  before any claim score: `reset()` deletes `.git/index` before the reset, so every tracked path is checked out
  again and gets fresh stat fields. Re-run: `census/round-85/controls/c2-before-base-tool.txt` reads
  `mismatches=3` with KF1/KF2/KF3 `k4=0 match=no` and the four honest/dirty rows clean, which is the frozen before.
  No after-arm byte existed at the time of the change.
- **A0.2 — the r85 population pin was off by one.** The first pin declared 48 rows for a 48-line file (one line is
  the header comment); the harness counts rows, so the pin was corrected to 47 before any battery ran with it. The
  pinned sha256 never changed.
- **A0.3 — the first C1 target (bind the census-in-tree clause) was not bindable.** See A1; the frozen target moved
  to the class-enum guard *before* F (the counter's pin table, the population and the mutants were all in P, and no
  after receipt existed when m11 was replaced). The wrong first target and its measurement are kept in A1 as the
  round's finding, not deleted.

## A1 — C1: the census-in-tree branch is REACHABLE and UNBOUND (first reading withdrawn; S85Scribe F1)

- **Artifact:** `.ufo/waves/round-85/w1/S85Scribe.md` § F1 and its reproducer
  `.ufo/waves/round-85/w1/S85Scribe/probe-census-in-tree-reachable.py`, run through the counter's own public
  `--forge` path on the committed bytes (`91b4ffde…`): for item I85R with a target under `census/round-84/w1/`, the
  pristine counter refuses with `why=census-in-tree target is not a wave capture keeping the token's full path
  suffix`, while the mutant that drops that branch resolves the same row as MOVED. The Scribe then added the missing
  row (NF-W, target `census/round-84/w1/c1-after.txt`) to a scratch copy of the harness and a 48-row population: the
  pristine counter scores `rows=48 mismatches=0` and the c7 mutant goes red on NF-W alone. One row binds the clause.
- **What the first reading got wrong (this file's own A1 text before this amendment):** it said the prefix-equal
  own-tree belt refuses every pair that could reach the branch. It does not: `_owntree_ok` returns True when the
  target sits under a real wave directory (`OWNTREE_WAVE`, `^(?:w[0-9]+|a2w1|assimilation)/`), so for a
  census-rooted token whose target is `census/round-<N>/w1/…` the belt is satisfied and control reaches the
  census-in-tree branch. The shadow probe's `killed_r84=0 killed_r85=0` (`records/a1-c7-shadow.txt`) is explained by
  the POPULATION, not by unreachability: no pinned row carries that shape — NF-R's `records/copy/` target is refused
  by the belt first, TF11's `waves/` target is accepted as a capture.
- **Same bytes, two more clauses measured (S85Scribe F4):** dropping the last-component basename check
  (`c1-pointer-counter.py:387`) makes every row error on both populations — it is bound, and it is the only clause
  between the population and an exception; dropping the own-tree belt (`:391`) is killed 7 of 7 rows on both
  populations — bound, and it is what refuses NF-R. Neither is shadowed.
- **Frozen wording falsified:** the preregistration's round non-claim ("the branch is shadowed by the prefix-equal
  own-tree belt … the routed decision … is answered as 'delete'") and the r85 knowledge section's shadow
  paragraph — both were written from the first reading. The two frozen CLAIMS are untouched: C1 is about the
  class-enum guard and its kill, C2 about K4.
- **Amended sentence:** *the census-in-tree branch is reachable and discriminating and has no row; a MOVED row whose
  census-rooted token lands in a wave directory under its own round (`census/round-<N>/w1/<basename>`) is refused by
  that branch alone. The r85 population is one row short of binding it. r84's routed "ground it or delete it"
  therefore answers "ground it", and the row (NF-W) with the 48-row population — plus the Scribe's c7 kill — is
  routed to r86. Nothing is deleted, and Q156's test stands: it asked for the measurement, and the measurement said
  the opposite of the first reading.*

## A2 — C2: a gitlink concealed by skip-worktree passes K4 (wording narrowed; the repair does not carry the flag sweep)

- **Artifact:** `.ufo/waves/round-85/w1/S85ExecK4.md` §§ (d) and "probe-d2b" (`out-probe2.txt`): a submodule whose
  checked-out commit changed, with `skip-worktree` on the gitlink entry, leaves `git status --porcelain` empty; K4
  emits **zero** rows and the tool exits 0 on an otherwise clean tree. Mechanism, quoted from the seat and checked
  against the writer: `_truth_refusal` skips `mode == b"160000"` (`tools/souji-receipt-write.py:283`), and the
  writer's `RECEIPT-GITLINK-CONCEALED` refusal lives in its *flag sweep* (`git ls-files -v`), a code path inside
  `write_receipt` that K4 does not run. K4's own status loop does not cover it either, because the flag hides the
  change from porcelain.
- **Frozen wording falsified:** the preregistration's "every status-clean stage-0 tracked path and symlink is
  re-hashed" reads "tracked path" as everything `ls-files` records; the instrument re-hashes regular files and
  symlinks only.
- **Amended sentence:** *K4 re-hashes every status-clean stage-0 tracked REGULAR FILE and SYMLINK against the object
  id its index entry records — the class the seven frozen rows measure. It does not carry the writer's flag sweep, so
  a gitlink (mode 160000) whose commit moved under `skip-worktree`, or any path concealed by a non-zero stage, passes
  K4 unmeasured; that is a routed defect (S85ExecK4 (d2b)), not coverage, and the next repair carries the flag sweep
  K4 currently omits.*

## A3 — C1: the stage-0 filter clause is shadowed (m4 survives; measured by the wave)

- **Artifact:** `.ufo/waves/round-85/w1/S85MutK4.md` m4: widening the writer-side stage-0 filter (`stage != b"0" or
  ...` → `mode == b"160000" or ...`) scores `rows=7 mismatches=0`, EXIT 0 — the clause has no row. This is a C2-side
  shadow (the counter's population has no non-zero-stage row), not a C1 clause; the claim's guard (m11) is unaffected.
  Routed: a stage-2 row and an intent-to-add row are r86 items; S85ExecK4 showed both states are listed by porcelain
  today, so they cannot be written as concealment rows without the flag sweep.

## A0.4 — C2 instrument correction after two seats had scored (disclosed)

- `.ufo/waves/round-85/w1/S85MutK4.md` § m5: the mutant that compares `hash-object` to the wrong field made the
  counter die with `KeyError: 'KH1'` — the counter's `named` predicate indexed `FORGED` for honest rows, so any
  mutant that over-refuses an honest row crashed the instrument instead of printing `ROW … match=no`. Fixed before
  filing (`census/round-85/c2-k4-counter.py` sha256 `ae482f07…` → `0a7b801d…`): `named` is computed only for `flag`
  rows. Both arms were re-run on the filed counter (`census/round-85/records/c2-after.txt` 7/0,
  `census/round-85/controls/c2-before-base-tool.txt` 3). Seat findings scored against `ae482f07…` are recorded as
  findings about those bytes; the class the m5 mutant belongs to is now killed by a row, not by a crash.

## A4 — C1: five more guards are unbound (measured by the wave); the claim covers only the six it names

- **Artifact:** `.ufo/waves/round-85/w1/S85MutCounter.md` (table at its §3, receipts `receipts/ext-*`): six new
  single-edit mutants scored on BOTH pinned populations — `m12-r0-line` (R0's token-on-base-line half) survives
  44/0 and 47/0; `m14-short-shape` (`len(want) < 2 or len(got) < 2`) survives both; `m15-empty-want` (`bool(want)`
  in `_capture_ok`) survives both and the seat shows **0 of 32 inputs flip** (dead clause); `m16-nf6b-punct` (the
  sentence-end punctuation disjunct in `_whole`) survives both; `m17-dup-id` (duplicate-id refusal in `_ledger`)
  survives both and silently overwrites. `m13-no-round-guard` is killed by NF3 on both — already bound, not new
  coverage.
- **Frozen wording falsified:** none. The preregistration claims "kills all six frozen single-edit mutants" and
  says the population "does not certify the counter's whole rule". The seat's survivors are exactly that limit, and
  the C1 claim's stated limits already say the population proves discrimination on its own rows only.
- **Disposition:** `neutral` in the ledger with this pointer; the five unbound guards and the dead clause are
  routed to r86 (a row each, or a deletion for m15). Q156 now requires the shadow-vs-unbound test before a clause is
  named, so m15 (dead) is filed as dead rather than "unbound".
