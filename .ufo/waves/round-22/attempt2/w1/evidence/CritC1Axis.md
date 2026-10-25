# CritC1Axis — executed evidence ledger

Seat `L1Souji22.CritC1Axis`. Read-only against the lane: no git/jj write, no
signal, no install, no mutating cleanup. Base revision
`4edb25dfe262515d0da63224bbba71e02e36cba5` (preregistration). **The lane moved
during review** (`d6a75ba` -> `af73b8b` -> `c9f1fe3`); every number names its
revision, and the timeline is kept rather than overwritten.

All counter runs below use the tool bytes **as committed at the named revision**,
extracted to `/var/tmp` and removed after use. The on-disk `tools/` copy changed
under the review (E1), so "run the tool from disk" was not used for findings.

## E1 — the instrument is unpinned and the on-disk copy was mutating

```
sha256 <committed> af73b8b:tools/souji-declared-evidence.py
58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2
sha256 <committed> c9f1fe3:tools/souji-declared-evidence.py
65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4
sha256 tools/souji-declared-evidence.py  (worktree, 06:53Z)
ac838b4c029a79107bd8…   then   05b53b7d419c2315…   (06:57Z)
```

Three distinct byte states inside five minutes. A `--root .` invocation executes
the **worktree** script but reads the declaration from `--rev`, so the same claim
re-derives differently:

```
06:53:56Z  tools/… --rev af73b8b --format counts -> assertions=59 resolved=58 skipped=37 mismatches=1 (rc 1)
06:57Z     tools/… --rev af73b8b --format counts -> assertions=59 resolved=59 skipped=37 mismatches=0 (rc 0)
committed 58ddbfef at af73b8b                     -> assertions=59 resolved=59 skipped=36 mismatches=0 (rc 0)
```

The single mismatch in the first run was
`census/round-17/jj-receipts-*.txt  A  mismatch:path-absent  glob matches nothing at af73b8b`,
although both targets exist there (`git ls-tree -r --name-only af73b8b census/round-17`
-> `jj-receipts-4f48343.txt`, `jj-receipts-base5fa6017.txt`): a mid-write candidate
with a broken per-segment glob. Recorded as a **reproducibility hazard**, not as a
finding against committed bytes.

## E2 — counter at base and at named tips (committed bytes)

Instrument `58ddbfef` (committed at `a211e4d`..`af73b8b`):

```
--rev 4edb25d   -> assertions=56 resolved=53 skipped=33 mismatches=3   rc 1
--rev 70af563   -> assertions=57 resolved=56 skipped=37 mismatches=1   rc 1
--rev 2a130b4   -> assertions=56 resolved=56 skipped=36 mismatches=0   rc 0
--rev af73b8b   -> assertions=59 resolved=59 skipped=36 mismatches=0   rc 0
```

Instrument `65817d0d` (committed at `c9f1fe3`):

```
--rev 4edb25d              -> assertions=55 resolved=52 skipped=33 mismatches=3  rc 1
--rev 5fdd5d54 (named tip) -> assertions=60 resolved=60 skipped=38 mismatches=0  rc 0
--rev c9f1fe3 (HEAD)       -> assertions=60 resolved=60 skipped=38 mismatches=0  rc 0
selftest                   -> 8/8
```

The three base mismatches are the ones lesson M15 names:

```
3   AXES.md                                              A  mismatch:path-absent
63  reason-after.txt                                     A  mismatch:path-absent
77  .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md A  mismatch:path-absent
```

## E3 — the assertion set is not conserved; the row's set numbers do not re-derive

The committed row at `c9f1fe3` says: "The assertion SET moved with the file
(**5 base tokens retired, 6 added**)". Measured on identical declared bytes:

```
instrument 58ddbfef  base 4edb25d -> tip 5fdd5d54 : retired 7, added 11   (N 56 -> 60)
instrument 65817d0d  base 4edb25d -> tip 5fdd5d54 : retired 6, added 11   (N 55 -> 60)
```

Retired (current instrument): `.ufo/scopes/…/obsidian-cli-probe.md`, `31984f4`,
`AXES.md`, `b912328d00d…`, `census/round-14/verification*.json`, `reason-after.txt`.
Added (current instrument): `31984f473ce4…`, `4edb25dfe…` ×3,
`af73b8ba92fa…`, `census/round-14/verification.json`,
`census/round-21/reason-after.txt`,
`census/round-22/attempt2/declared-evidence-before.tsv` ×2,
`corpus/lessons/round-22-verifier-spotcheck.md`, `d7266c5`.

Earlier state, for the timeline: at `af73b8b` the row said "over **the same 56
assertions**" while the committed instrument measured 59 at that tip and the row's
counter cell still read `assertions=56 resolved=56 skipped=36` (stale by 3).
`ee1aef2`/`4a6ee90`/`c9f1fe3` replaced that sentence and re-derived the cell.

Two of the three base mismatches left the enumerated set rather than resolving
(`skipped` 33 -> 36 at `af73b8b`, 33 -> 38 at `c9f1fe3`), one resolved.

## E4 — why the absolute path is the cheapest green

```
PATH_RE.match('AXES.md')                                -> True
PATH_RE.match('../AXES.md')                             -> True    (assertion; can never resolve)
PATH_RE.match('/home/vgpnk/Projects/shokunin/AXES.md')  -> False   (skip)
git show HEAD:../AXES.md                     rc=128
git show HEAD:/home/vgpnk/Projects/shokunin/AXES.md  rc=128
```

A *correct* fleet-relative pointer matches class A and is a permanent mismatch;
the absolute host path is skipped and green. The frozen enum has no fleet class,
though the lane's own Q31 grammar does ("fleet-only paths are listed as `fleet`,
never findings"). The committed row at `c9f1fe3` now concedes this:
"1 of the 3 repairs names a fleet file absolutely and therefore leaves class A
rather than resolving inside it."

## E5 — the repaired cells and what changed in the verdict cells

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

Capability table, base `4edb25d` vs `c9f1fe3` (column 2 = "what it can now do"):

```
claim-column same=24 changed=0 new=1   (new = "declared-evidence calibration audit (r22 attempt 2)")
axis scores: coverage 8, calibration 7, operability 8   (base and tip identical)
evidence-column changes: souji-verify, worktree metadata prune (+ "measured at d7266c5"),
  ledger-verify, sources registry, seat transcript audit, process-residue observations,
  declared-dependency cache eligibility
```

The `census/round-14/verification*.json` glob **resolved at base** ("3 match(es)")
and was not a mismatch; the repair pass narrowed it to one file anyway. It is still
narrowed at `c9f1fe3` (`grep -c 'verification\*\.json' SCORECARD.md` -> 0).

## E6 — the committed row vs the committed instrument

At `c9f1fe3`:

```
row: "Base 4edb25d: assertions=56 resolved=53 skipped=33 mismatches=3; tip 5fdd5d54…: mismatches=0"
     counter cell: assertions=60 resolved=60 skipped=38 mismatches=0
     "Score 7 unchanged; CritC1Predicate dissent on record"
instrument 65817d0d at tip 5fdd5d54 -> 60/60/38/0   (reproduces)
instrument 65817d0d at base 4edb25d -> 55/52/33/3   (the row's 56 came from the older instrument)
no instrument digest appears in SCORECARD (`grep -c` for 65817d0d/58ddbfef -> 0)
```

So the after-state is pinned by revision and reproduces; the before-state is a
number without its instrument, and the set numbers in the prose do not re-derive
under either committed instrument (E3).

## E7 — selftest and its scope

`--selftest` -> `selftest=8/8` at both `58ddbfef` and `65817d0d`. Fixtures:
all-good 0; absent path; dangling rev; wrong digest; path only at other rev;
correct digest; always-zero control `FALSE-GREEN-REJECTED`; command span
"skipped, not asserted". **No fixture covers a token that is absolutised,
de-backticked or prefix-glued**, and the TSV emits no per-token skip ledger
(`skipped` is a bare integer) — so the reclassifications used by the landed
repair are unpunished by construction.

## E8 — the existing landing gate at base does not cover these tokens

```
python3 -B tools/souji-landing-gate.py --root . --rev 4edb25d --round 22
LG-DANGLING-PTR  ../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md   corpus/README.md:217
LG-DANGLING-PTR  ../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md   corpus/README.md:217
LG-DANGLING-PTR  .ufo/waves/hyaku/jj-w1/reports/                     corpus/knowledge/jj-colocation-receipts.md:148
LG-DANGLING-PTR  .ufo/waves/hyaku/parent-closures/souji22/evidence.json  corpus/lessons/round-22-verifier-spotcheck.md:32
SUMMARY  findings=4 checked_reg=50 ... checked_reports=111
```

Four findings, **none in SCORECARD.md**: the gate's grammar covers only
`census/ tests/ tools/ corpus/ .ufo/waves/`. The new instrument does cover a class
the gate missed — the fair part of C1.

## E9 — calibration score history (what earned a move)

```
ccbb132  | calibration | 0 | no false-SAFE rate measured yet
97f22c9  | calibration | 5 | improved (C2, r1): author first-pass SAFE precision
3674633  | calibration | 6 | improved (C2, r3): 0/21 blind-pair disagreements;
                         96-row approval list re-verified, 0 false-SAFE
455b1de  | calibration | 7 | improved (V1, r5): verification round found 3 material
                         defects (symlink false-SAFE class; local-master pushed
                         fallback; r1 logs_tier row) — all corrected in-round
...       | calibration | 7 | r6..r21 unchanged; every r13–r21 claim is an instrument
                         acquisition recorded "improved ... numeric delta 0"
c9f1fe3  | calibration | 7 | r22 attempt 2 C1; "Score 7 unchanged"
```

Both moves rest on verdict accuracy (blind-pair re-derivation; false-SAFE
defects), never on pointer resolvability.

## E10 — the lane's own criteria and corrections

```
corpus/QUALITY.md:34  Q10  "At the closing commit the bookkeeping matches the repo:
                           SCORECARD prose equals its table numbers, ..."
corpus/QUALITY.md:41  Q17  "A claimed committed fixture or evidence fragment must
                           resolve to a contained regular, non-symlink file at the
                           measured revision; prose naming a fixture is not a
                           substitute for the file."
SCORECARD.md:31-33    "Correction (r12 post-review ...): ... calibration C1's
                           28/52 -> 51/53 is a rule-coverage count, not calibration
                           proof."
corpus/lessons/round-22.md:306-320 (M15, still current): "*Captured-by:* QUALITY
                           Q10 (bookkeeping matches the repo) — stated, never
                           machine-checked. *Fix:* tools/souji-declared-evidence.py"
```

Q17 already states the rule the audit enforces; SCORECARD sat outside Q17's
declared `applies-to` ("knowledge, round evidence"). M15's `captured-by` names
Q10, the bookkeeping criterion.

## E11 — kengaku round-24 precedent (read, not re-executed)

`.ufo/waves/kaika-w3/kengaku-critic.md` (C2):

> "The claim's own scorecard rubric requires a scored probe ... and C2 holds the
> score at 8: mistake inventory, late r23 closeout and ledger repairs are useful
> bookkeeping, but do not verify the registered calibration axis-move."

`.ufo/reports/round-24/kengaku.md:203-205` records the ruling as "fails as
registered" under rubric clause (d), score held; the post-review note upgrades C2
to "a real calibration move" only after the outside spot-check disagreements
became lessons M21/M22 and grounded criteria Q9/Q10 — a judgment change, not the
state repair.

## E12 — peer cross-checks (source-read, not re-executed)

- `w1/evidence/AuditReadme.tsv`: 9 same-class mismatches in `corpus/README.md`
  (bare `counts.json`, `obsidian-ledger.tsv`, `quarantine-same-filesystem-rename.md`,
  `../../.ufo/...`), none repaired, outside C1's declared file.
- `w1/CritC1Predicate.md`: independently reaches the set-conservation and
  skip-escape findings; its Q3 rewrite table and my E3 token diff agree.

## E13 — scratch and cleanup

Scratch under `/var/tmp` only: committed tool extractions (`de-af73.py`,
`de-c9.py`, `de-old.py`), token lists and two TSVs for byte-exact A/B work; all
removed after use. No lane file written; no tool installed; no signal sent.
