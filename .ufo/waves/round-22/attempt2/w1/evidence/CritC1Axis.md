# CritC1Axis — executed evidence ledger

Seat `L1Souji22.CritC1Axis`. Read-only against the lane; no git/jj write, no
install, no signal. Base revision `4edb25dfe262515d0da63224bbba71e02e36cba5`
(preregistration). Observations timestamped `2026-10-25T06:53Z`; the lane was
moving during the review (HEAD `d6a75ba` -> `af73b8b`), so every number below
names the revision it was measured at.

## E1 — instrument bytes are not pinned, and the on-disk copy was mutating

```
sha256sum <(git show af73b8b:tools/souji-declared-evidence.py)   # committed
58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2
sha256sum tools/souji-declared-evidence.py                        # worktree
05b53b7d419c2315111b45058bea1fef7474aeb746c0164049cff2b7fb7790d6
```

The worktree digest changed twice inside a four-minute window
(`ac838b4c029a79107bd8…` at 06:53:56Z, `05b53b7d…` at 06:57Z), while the
committed file stayed `58ddbfef…`. A `--root .` invocation executes the
**worktree** script but reads the declaration from `--rev`, so the same claimed
result can be re-derived to a different verdict:

```
06:53:56Z  python3 -B tools/souji-declared-evidence.py --rev af73b8b --format counts
           -> assertions=59 resolved=58 skipped=37 mismatches=1   (rc 1)
           row cell recorded `assertions=59 resolved=59 skipped=36 mismatches=0`
06:57Z     python3 -B tools/souji-declared-evidence.py --rev af73b8b --format counts
           -> assertions=59 resolved=59 skipped=37 mismatches=0   (rc 0)
```

The first run's single mismatch was
`64  census/round-17/jj-receipts-*.txt  A  mismatch:path-absent  glob matches nothing at af73b8b`
although both targets exist at that revision
(`census/round-17/jj-receipts-4f48343.txt`, `census/round-17/jj-receipts-base5fa6017.txt`
from `git ls-tree -r --name-only af73b8b census/round-17`). So that run read a
mid-write candidate with a broken per-segment glob. Recorded as a **reproducibility
hazard**, not as a finding against committed bytes.

All measurements below therefore run the **committed** tool bytes, extracted to
`/var/tmp/de-af73.py` (`sha256 58ddbfef…`) and removed after use.

## E2 — the C1 counter at base and at the committed tip

```
python3 -B /var/tmp/de-af73.py --root . --file SCORECARD.md \
    --rev 4edb25dfe262515d0da63224bbba71e02e36cba5 --format counts
assertions=56 resolved=53 skipped=33 mismatches=3          rc=1

python3 -B /var/tmp/de-af73.py --root . --file SCORECARD.md \
    --rev af73b8ba92fa2783d9f4653bd504233939daa2d6 --format counts
assertions=59 resolved=59 skipped=36 mismatches=0          rc=0
```

Base mismatch rows (`--format tsv`), exactly the three lesson M15 names:

```
3   AXES.md                                            A  mismatch:path-absent
63  reason-after.txt                                  A  mismatch:path-absent
77  .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md  A  mismatch:path-absent
```

Intermediate: `70af563` -> `57 56 37 1` rc 1 (one mismatch remained);
`2a130b4` -> `56 56 36 0` rc 0.

## E3 — the assertion set is not conserved (the row says "the same 56 assertions")

Multiset of `--format tsv` tokens, base `4edb25d` vs committed tip `af73b8b`
(committed tool):

```
REMOVED (7): .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md
             31984f4
             41553adb139d06511dc386bb3ce4326aebfba675
             AXES.md
             b912328d00d19f26918240710d0b5e0f334880ff
             census/round-14/verification*.json
             reason-after.txt
ADDED   (9): 31984f473ce4bdab61a99b16cca194b28108cb81   (same citation, short -> full)
             4edb25dfe262515d0da63224bbba71e02e36cba5   (x3)
             census/round-14/verification.json
             census/round-21/reason-after.txt
             census/round-22/attempt2/declared-evidence-before.tsv  (x2)
             corpus/lessons/round-22-verifier-spotcheck.md
             d7266c5
N: 56 -> 59      S: 33 -> 36      M: 3 -> 0
```

Two of the three base mismatches left the enumerated set rather than resolving:
`AXES.md` became an absolute host path (uncountable), the obsidian path was
de-backticked (invisible to the span scanner). One resolved: `reason-after.txt`
-> `census/round-21/reason-after.txt`.

## E4 — why the absolute path is the cheapest green

```
PATH_RE.match('AXES.md')                                   -> True
PATH_RE.match('../AXES.md')                                -> True   (would be an assertion)
PATH_RE.match('/home/vgpnk/Projects/shokunin/AXES.md')     -> False  (skipped)
git show HEAD:../AXES.md                     rc=128
git show HEAD:/home/vgpnk/Projects/shokunin/AXES.md  rc=128
```

A *correct* fleet-relative pointer (`../AXES.md`) matches class A and can never
resolve (`git show` refuses an out-of-tree path) — a permanent mismatch. The
absolute host path is skipped and scores green. The frozen enum has no fleet
class, although the lane's own Q31 grammar has one ("fleet-only paths are
listed as `fleet`, never findings").

## E5 — the repaired cells

`git show 70af563 -- SCORECARD.md`:

```
-Axes (fleet `AXES.md`): the lane owns **calibration, ...
+Axes (fleet `/home/vgpnk/Projects/shokunin/AXES.md`): the lane owns ...
```

`git show 2a130b4 -- SCORECARD.md`:

```
-  `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`; that file is absent
+  the operator scope file .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md;
+  that file is absent (checked 2026-10-25, ls -> "No such file or directory"),
+  so the finding is not retrievable from committed bytes and is no longer ...
```

Evidence-column edits base -> tip (capability table):

```
SAME-CLAIM  every row          (column "what it can now do" byte-identical)
            worktree metadata prune        evidence-col changed (+ "measured at d7266c5")
            declared-dependency cache eligibility  evidence-col changed
                                            +`census/round-14/verification.json`
                                            -`census/round-14/verification*.json`
            seat transcript audit          evidence-col changed
            souji-verify                   evidence-col changed
            ledger-verify                  evidence-col changed
            sources registry               evidence-col changed
            process-residue observations   evidence-col changed
NEW ROW     declared-evidence calibration audit (r22 attempt 2)
```

The `census/round-14/verification*.json` glob **resolved at base** (old tool:
"3 match(es) at 4edb25d") and was not a mismatch; the repair pass narrowed it to
one file anyway.

## E6 — the committed row does not reproduce at the committed tip

```
git show af73b8b:SCORECARD.md | grep '^| calibration'
... repaired to 0 mismatches over the same 56 assertions at the final tip ...
... -> `assertions=56 resolved=56 skipped=36 mismatches=0`, exit 0 ...

committed tool at af73b8b -> assertions=59 resolved=59 skipped=36 mismatches=0
```

Prose says 56, the counter cell says 56, the committed instrument measures 59
(three assertions added by `5ff5041`/`d6a75ba`/`af73b8b`). The worktree
SCORECARD already carries 59 (uncommitted at review time).

## E7 — selftest and its scope

`python3 -B /var/tmp/de-af73.py --selftest` -> `selftest=8/8`, fixtures:
all-good 0; absent path; dangling rev; wrong digest; path only at other rev;
correct digest; always-zero control `FALSE-GREEN-REJECTED`; command span
"skipped, not asserted". **No fixture covers a token that is absolutised,
de-backticked or prefix-glued** — the three reclassifications used by the landed
repair are unpunished by construction.

## E8 — the existing landing gate at base does not cover these tokens

```
python3 -B tools/souji-landing-gate.py --root . \
    --rev 4edb25dfe262515d0da63224bbba71e02e36cba5 --round 22
LG-DANGLING-PTR  ../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md   corpus/README.md:217
LG-DANGLING-PTR  ../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md   corpus/README.md:217
LG-DANGLING-PTR  .ufo/waves/hyaku/jj-w1/reports/                     corpus/knowledge/jj-colocation-receipts.md:148
LG-DANGLING-PTR  .ufo/waves/hyaku/parent-closures/souji22/evidence.json  corpus/lessons/round-22-verifier-spotcheck.md:32
SUMMARY  findings=4 checked_reg=50 ... checked_reports=111
```

Four findings, **none in SCORECARD.md**: its grammar is limited to
`census/ tests/ tools/ corpus/ .ufo/waves/`, so a root-level name, a bare
basename and a `.ufo/scopes/` path are outside it. The new instrument does cover
a class the lane's gate missed — this is the fair part of C1.

## E9 — calibration score history (what earned a move)

`git log --format=%h -- SCORECARD.md`, first calibration row per commit:

```
ccbb132  | calibration | 0 | no false-SAFE rate measured yet
97f22c9  | calibration | 5 | improved (C2, r1): author first-pass SAFE precision
3674633  | calibration | 6 | improved (C2, r3): 0/21 blind-pair disagreements;
                         96-row approval list re-verified, 0 false-SAFE
455b1de  | calibration | 7 | improved (V1, r5): verification round found 3 material
                         defects (symlink false-SAFE class; local-master pushed
                         fallback; r1 logs_tier row) — all corrected in-round
then 7 through r21 (commit 4eb2fda) and r22 attempt 1 (fe7590b)
```

Every r13–r21 calibration row is an instrument acquisition recorded as
`improved ... numeric delta 0` (r13 declared-evidence validator, r14 cache
eligibility, r16 landing gate, r17 seat audit, r18 pointer gate, r19 carry gate,
r20/r21 auditor oracles). The two moves (5->6, 6->7) both rest on verdict
accuracy (blind-pair re-derivation; false-SAFE defects), never on pointer
resolvability.

## E10 — the lane's own criteria and corrections

```
corpus/QUALITY.md:34  Q10  "At the closing commit the bookkeeping matches the repo:
                           SCORECARD prose equals its table numbers, `## Planned` ...
corpus/QUALITY.md:41  Q17  "A claimed committed fixture or evidence fragment must
                           resolve to a contained regular, non-symlink file at the
                           measured revision; prose naming a fixture is not a
                           substitute for the file."
SCORECARD.md:31-33    "Correction (r12 post-review ...): ... calibration C1's
                           28/52 -> 51/53 is a rule-coverage count, not calibration
                           proof."
corpus/lessons/round-22.md:306-320 (M15)  "... *Captured-by:* QUALITY Q10
                           (bookkeeping matches the repo) — stated, never
                           machine-checked. *Fix:* tools/souji-declared-evidence.py"
```

Q17 already states the rule the audit enforces; SCORECARD was outside Q17's
declared `applies-to` ("knowledge, round evidence"). The lesson's `captured-by`
names Q10, the bookkeeping criterion.

## E11 — kengaku round-24 precedent (read, not re-executed)

`.ufo/waves/kaika-w3/kengaku-critic.md` (C2):

> "The claim's own scorecard rubric requires a scored probe ... and C2 holds the
> score at 8: mistake inventory, late r23 closeout and ledger repairs are useful
> bookkeeping, but do not verify the registered calibration axis-move."

`.ufo/reports/round-24/kengaku.md:203-205` records the same ruling as "fails as
registered" under rubric clause (d), score held; the later orchestration note
(post-review) upgrades C2 to "a real calibration move" only after the outside
spot-check disagreements became lessons M21/M22 and grounded criteria Q9/Q10 —
i.e. a judgment change, not the state repair.

## E12 — peer cross-checks (source-read, not re-executed)

- `w1/evidence/AuditReadme.tsv`: 9 same-class mismatches in `corpus/README.md`
  (bare `counts.json`, `obsidian-ledger.tsv`, `quarantine-same-filesystem-rename.md`,
  `../../.ufo/...`), none repaired, all outside C1's declared file.
- `w1/CritC1Predicate.md`: independently reaches the set-conservation and
  skip-escape findings (Q2/Q3/Q4) from the same bytes; its Q3 rewrite table and
  my E3 token diff agree.

## E13 — scratch and cleanup

One scratch extraction (`/var/tmp/de-af73.py`, committed tool bytes) and three
token lists (`/var/tmp/b2`, `/var/tmp/t2b`, `/var/tmp/tip73.tok`) plus two TSVs
were written under `/var/tmp` for byte-exact A/B work; all removed after use.
No lane file was modified; no tool installed.
