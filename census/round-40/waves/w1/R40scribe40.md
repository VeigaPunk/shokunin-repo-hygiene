# R40scribe40 — C1 strict-descendant calibration attack

- Seat: scribe, leaf (no dispatch).
- Distinct item 40: **register ordering / equal-revision edge case**, based on the committed r39 adversarial register fixture, not another token-only-line replay.
- Frozen contract read first: `census/round-40/preregistration.txt:5`.
- Tools installed/upgraded: none; pacman untouched.

## Evidence examined

Commands actually run (read-only):

```text
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
read /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-39-verifier-spotcheck.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/records/c1-after.txt
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/waves/w1/W1RevC1Register.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/waves/w1/W1MutC1.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-39/w1/W1RevC1Forge.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-39/w1/W1ExecC1Items.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/records/c1-before.txt
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b^{commit}
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- .ufo/waves/round-40/w1/R40scribe40.md
```

The `rev-parse` output was `0242085909fb6a4ee041c5443d76316ac6d59d4b`, confirming the frozen base resolves. The scoped report path had no preexisting status output. No counter or fixture was executed in this seat.

R39's committed `census/round-39/waves/w1/W1RevC1Register.md:136-150` records an equal-revision attack: six register rows all set `receipt_rev=A, commit=A`; the reconciler gave `cells=6 mismatches=0 commit_distinct=0`, while the counter exited 1 solely on its distinct-row floor. The same report at `:177-206` records the complementary backwards-order case: all rows `receipt_rev=B, commit=A` where A is B's parent; receipt blobs were byte-identical and the counter returned rc 0 with zero mismatches. Thus r39's checks did not enforce the chronology rationale. Its final independent spot-check, `corpus/lessons/round-39-verifier-spotcheck.md:44-49`, rederived r39's actual rows as strict descendants, showing the real landing happened to satisfy ordering but the old acceptance path itself was not a measurement of ordering.

The frozen r40 predicate at `census/round-40/preregistration.txt:5` explicitly adds strict-descendant ordering and says equal/backwards commit passing is a kill condition. The r39 examples form bounded challenge cases for that new arm; they are provenance for tests, not evidence about the r40 candidate.

## Verdict

**Concrete falsifier of the r39 instrument; r40 status NOT MEASURED.** The equal-revision case shows why the new r40 comparison must reject equality (not merely require resolvable revisions or unequal strings); the backwards-parent case shows the old reconciler can green a chronologically reversed register even when receipt content is identical. I did not run r40 candidate bytes or claim that r40 fails. Required bounded measurement to establish the r40 clause: feed its register checker (a) `commit=receipt_rev`, (b) parent `commit` with child `receipt_rev`, and (c) valid strict-descendant control rows; require the first two to fail specifically the ordering predicate and the control to pass. Separately preserve the frozen forged token-only item as OPEN as required by the C1 line-5 contract; that is not tested here.

## Gates, surfaces, limits

- Behavior: legacy r39 accepts backwards commit ordering (rc 0) and rejects equal ordering only due to a generic distinct floor, per the committed fixture report; r40 behavior unobserved.
- Gates: no tests/build/linter or candidate counter run; no git/jj/index mutation.
- Touched surface: this assigned report only, `.ufo/waves/round-40/w1/R40scribe40.md`.
- Out of scope: frozen claims, production files, other C1 evidence-pointer/forgery behavior, C2/C3, lane state.
- Scratch: none. Installs: none.