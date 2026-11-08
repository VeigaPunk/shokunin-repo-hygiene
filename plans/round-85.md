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

## A1 — C1: the census-in-tree branch is SHADOWED, not unbound (the routed r84 A10 item)

- **Artifact:** `census/round-85/records/a1-c7-shadow.txt` — the single-edit mutant `c7-census-in-tree-drop`
  (drops only the branch at `census/round-85/c1-pointer-counter.py` `judge()`, `elif kr and target[:tr.start(0)] ==
  "census" and token[:kr.start(0)] == "census"`) is **not killed** by either pinned population: both pristine arms
  green (44/0 and 47/0), `killed_r84=0 killed_r85=0`, EXIT 0. The same mutant also survived the r83 population in
  r84. Rows NF-R/TF11 (the census-token move, non-capture and capture) do not change that.
- **Why (branch order, read directly):** for the branch to be reached, `target[:tr.start(0)] == "census"` and
  `token[:kr.start(0)] == "census"`; but the branch immediately above it is
  `elif kr and target[:tr.start(0)] == token[:kr.start(0)] and not _owntree_ok(...)`, and those two conditions make
  its guard TRUE, so the own-tree belt refuses first. When the token's root is NOT `census`, the branch's second
  condition is false and the `token[:kr.start(0)] != "census"` belt above it applies instead. So the branch cannot
  be the first refusing branch for any (token, target) pair.
- **Frozen wording falsified:** r84's A10 sentence and the r84 knowledge section's framing that the
  "census-in-census clause" was *unbound by the population* — an unbound clause is one a row could bind; this one is
  shadowed, and no row can bind it. r84's own routed item asked to "ground it or delete it"; the measurement answers:
  it cannot be grounded.
- **Amended sentence:** *the r85 round measures that the census-in-tree branch is unreachable behind the own-tree and
  cross-root belts (a single-edit drop survives both pinned populations, 0/2), and adopts the routed decision
  "delete"; the deletion lands as the r86 item rather than this round's claim, because the claim slot this round is
  the class-enum guard (P's m11) and a claim's rule is not changed after any seat has scored.* This is a finding,
  not a claim; the pre-file ledger records it as `falsifies-wording` with this pointer.

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
