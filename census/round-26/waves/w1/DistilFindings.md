# DistilFindings — round 26 w1 findings distillation

## Status

STATUS: PASS — 87 deduplicated findings distilled from 84 STATUS-bearing seat reports (107 `.md`
files) in `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/`, each with its
strongest seat pointer and a severity (attack / finding / observation); 13 pairs of seats that
disagree on the same fact are flagged with the bytes that settle each; 30 findings were re-verified
against the lane at tip `e78ac7c`. Delivery: `.ufo/waves/round-26/w1/distill-findings.md`.

## Evidence

Lane tip when distilled: `e78ac7c4837b81b634db4a927605a751a7f006ba` (`round-26 verifier spot-check
(integrator, hyaku): non-author admit/reject`); earlier tips observed during the run:
`0eca7c8` (base) → `89e0fce` → `a529c76` → `07f83e6` → `33e6807` → `c594901` → `9a6e0f1` →
`166baa1` → `e78ac7c`.

Report census (read-only, `ls`/`grep` only):

```
$ ls .ufo/waves/round-26/w1/*.md | wc -l
107
$ grep -l 'STATUS: ' .ufo/waves/round-26/w1/*.md | wc -l
84
```

Frozen contract read first: `.ufo/waves/round-26/preregistration.txt` (claims C1/C2/C3, K1–K4
counters, kill rules), plus `preregistration-amendment-1.txt` and `-2.txt`.

Re-verifications run by this seat against the lane at tip (all read-only):

```
$ bash census/round-26/c1-counter.sh
markers=0
headings=17 44 78
$ bash census/round-26/c3-counter.sh
axis_check_tool=present
claims=3 flags=0
axis_check_exit=0
cases=12 pass=12 control=FALSE-GREEN-REJECTED
fixture_exit=0
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/git-auto-maintenance-trigger-set.md \
             corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
    --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice \
    --slice-verdicts census/round-26/records/empty-verdicts
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0
$ python3 -B tools/souji-coverage-agreement.py --root . --rev $(git rev-parse HEAD) \
    --base-rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0
$ python3 -B tests/fixtures/r23-locator-heading.py --entries \
    corpus/knowledge/git-auto-maintenance-trigger-set.md \
    corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
    --snapshot-dir census/round-26/sources
entries=2 locators=0 locators_bad=0
$ for r in c1-before c1-after c2-before c2-after c2-k4-base c2-k4-after c2-gate c3-before c3-after; do
    python3 -B tools/souji-receipt-run.py verify --root . census/round-26/records/$r.tsv; done
c1-before    RECEIPT-COUNTS-ABSENT      c2-k4-base  verify=ok
c1-after     RECEIPT-COUNTS-ABSENT      c2-k4-after verify=ok
c2-before    RECEIPT-COUNTS-ABSENT      c2-gate     verify=ok
c2-after     RECEIPT-COUNTS-ABSENT      c3-before   RECEIPT-COUNTS-ABSENT
                                       c3-after    verify=ok
$ grep -n '^### Round 2[3-6] measurements' SCORECARD.md
17:### Round 25 measurements …
44:### Round 24 measurements …
78:### Round 23 measurements …
264:### Round 26 measurements …
$ grep -c 'Quote (' corpus/lessons/round-25.md corpus/lessons/round-26.md
corpus/lessons/round-25.md:3
corpus/lessons/round-26.md:0
$ git show HEAD:.ufo/waves/round-26/w1/verify-loop.sh | bash -n
bash: line 320: unexpected EOF while looking for matching `"'
```

Attack re-verifications this seat ran independently (scratch under `/var/tmp/souji-r26-DistilFindings*`,
removed):

- R2 vocabulary hole: `surface-class: garbage-typo` → `claims=1 flags=0`, rc 0.
- R2 last-wins hole: `surface-class: bookkeeping-file` then `surface-class: receipt-binding` →
  `claims=1 flags=0`, rc 0.
- Fixture case-body audit (read-only): `pull)` body is `git remote add origin "$rem"` +
  `git fetch -q origin` (no `git pull` anywhere in the file); `merge)`/`rebase)` bodies run
  `git commit -qm topic` before the named command; a plain `git commit --allow-empty` alone moves the
  registration count 2→1 (measured `before=2`, `after_plain_commit=1`); the fixture's merge topology
  replays as `Fast-forward`, contradicting its own comment "A real, non-fast-forward merge".
- Fleet census currency: `git worktree list --porcelain | grep -c '^worktree '` → 5, and
  `git worktree prune --dry-run --expire=now` lists 4 removable registrations, against the landed
  row S132's "0 prunable".

Bounds held: no `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no `rm`/`mv` outside my
own scratch, no signals, no `agent://all`, nothing read under `/home/vgpnk/Projects/shokuknow` beyond
the read-only staged package already cited by the wave, no fleet `.scratch/`, `.ufo/state/`,
`watchdog.log`, `MANIFEST.json`, `census/operator-sweep-*` or sibling-lane content touched. No tool
installed or upgraded.

## Findings

The full deduplicated list — 87 findings, each with its strongest seat pointer and severity, plus
the disagreement flags and the residual unknowns — is at
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/distill-findings.md`.

Highest-severity clusters (severity `attack`; full list with all pointers in the delivery file):

1. **Entry B's headline measurement is falsified by the fixture's own case bodies** — the `pull` case
   never runs `git pull`, the `merge`/`rebase` cases are confounded by a plain `git commit` that alone
   prunes 2→1, and the merge is a fast-forward contradicting the fixture's comment.
   (CritEntryB F1–F3, corroborated by ScoutRegroundDocs F6–F8; re-verified by this seat.)
2. **S132's "0 prunable" fleet figure is stale** — 4 of 5 live registrations are prunable.
   (ScoutRegroundOwnwork F3, LabGitVersion F6; re-verified.)
3. **The frozen K2 suite is forgeable** — static case worlds, `tail -n 1` reduction, control arm
   detached from the submitted tool. (CritKillRules F6–F7, MutC3Fixture F2–F6.)
4. **R2 has three live bypasses** — unbounded class vocabulary, last-wins duplicate `surface-class`,
   decoy MACHINE BLOCK shadowing. (RevC3Design F2–F4, CritClaims F4; two re-verified at tip.)
5. **The Q54 heading-resolution clause of the C2 kill rule is vacuous** — no entry Gate carries a
   `§` locator (`locators=0`, re-verified). (ScoutRegroundDocs F3, CritQ54Gate F1–F6.)
6. **Five of nine receipts refuse `verify`** while the prereg and lesson assert "each `verify=ok`".
   (LabReceiptVerify F1/F5, ExecVerifyLoop F2; re-verified.)
7. **The prereg's own frozen red-before command cannot run** (`--label` is not an option; the
   counters do not exist at the named base). (LabReceiptVerify F7, CritClaims F7.)
8. **C1's K1/K2 counters measure nothing about payload** — the omission of both r24 capability rows
   scored green. (ExecC1Surgery A3, ExecC1Verify F3; the omission happened and was repaired at
   `07f83e6`.)
9. **The prereg's red-before/green-after ordering rule is prose only** — no predicate consumes a
   receipt's `utc` or `rev`. (MutFreezeOrder F2.)
10. **`verify=ok` is byte-binding, not truth.** (MutCounterStub F1.)

Thirteen seat-disagreement flags are recorded in the delivery file (D1–D13), each with the bytes that
settle it. The three that remain live and consequential: the closure verdict's "expansion — improved"
against the base F1 row's "frontier, entries held" (D11); the spot-check's `§ OPTIONS` reading against
the entries' `locators=0` (D12); and the three different rationales for one staged refusal across the
prereg, the landed lesson and the spot-check (D13).

## Attack log

Not an attack seat: this item distils, it does not challenge a frozen predicate, target or case set,
and it proposes no amendment. Two findings above are recorded as attacks on the *round's own landed
work* (entry B's measurement, S132's currency) rather than on the preregistration — those are
first-party defects a later round must repair, and their freeze-relevant framing is preserved as
reported by their originating seats.
