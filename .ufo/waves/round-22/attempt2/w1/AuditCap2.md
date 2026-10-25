# AuditCap2 — declared-evidence audit of SCORECARD.md capability data rows 6–10

STATUS: PASS

Scope: the five capability-table data rows numbered 6–10 (`maintenance-guard gate`,
`declared-evidence integrity`, `bounded quarantine operations`, `repository structure census`,
`declared-dependency cache eligibility`). Audited against the frozen C1 classes A/B/C of
`.ufo/waves/round-22/attempt2/preregistration.txt`. Read-only; no file outside this report and
the named evidence TSV was written.

## 1. Revision measured and file bytes

Measured revision: **`4edb25dfe262515d0da63224bbba71e02e36cba5`** (frozen base of attempt 2).

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e 4edb25dfe262515d0da63224bbba71e02e36cba5^{commit}
(exit 0)
$ git log --oneline -1 4edb25d
4edb25d round-22 verifier spot-check: strict proof unproven, forward policy boundary held
```

Line numbering. The evidence rows are byte-identical at the base revision and at the current
worktree tip, so the audit applies to both; each row carries its own line number.

```
$ git show 4edb25dfe262515d0da63224bbba71e02e36cba5:SCORECARD.md | awk 'NR>=50 && NR<=54' | sha256sum
559f3ab538608f94d01a9f899b5d2e4ef07c39487120590f3fe4ce125ea1e938  -
$ awk 'NR>=55 && NR<=59' SCORECARD.md | sha256sum
559f3ab538608f94d01a9f899b5d2e4ef07c39487120590f3fe4ce125ea1e938  -
$ diff <(git show 4edb25d:SCORECARD.md | awk 'NR>=50 && NR<=54') <(awk 'NR>=55 && NR<=59' SCORECARD.md)
ROWS-IDENTICAL
$ git status --porcelain -- SCORECARD.md          ->  empty (worktree == HEAD for this file)
```

(An earlier pass of this same diff used two `/tmp` extracts; they were removed, and the
temp-file-free form above reproduces the identical digest. No path other than this report and
`evidence/AuditCap2.tsv` was touched inside the lane.)

The lane tip advanced while this audit ran (`2a130b4` → `3216c19` → `d6a75ba`). Re-checked at the
last of those tips: the five rows are still at lines 55–59 and still byte-identical to base lines
50–54 (`sha256sum` of both extracts = `559f3ab5…`), so nothing in this report is pinned to a moving
line number:

```
$ git rev-parse --short HEAD                      -> d6a75ba
$ grep -n '^| maintenance-guard gate\|^| declared-evidence integrity\|…' SCORECARD.md
55/56/57/58/59
$ awk 'NR>=55 && NR<=59' SCORECARD.md | sha256sum
559f3ab538608f94d01a9f899b5d2e4ef07c39487120590f3fe4ce125ea1e938  -
```

Mapping (identical bytes, different offsets because attempt-2 commits inserted 5 lines above):

| data row | base `4edb25d` line | worktree/HEAD line | row |
|---|---|---|---|
| 6 | 50 | 55 | maintenance-guard gate |
| 7 | 51 | 56 | declared-evidence integrity |
| 8 | 52 | 57 | bounded quarantine operations |
| 9 | 53 | 58 | repository structure census |
| 10 | 54 | 59 | declared-dependency cache eligibility |

The evidence TSV (`evidence/AuditCap2.tsv`) uses the **base-revision** line numbers (the numbers the
frozen counter prints at `--rev 4edb25d`); add 5 for the worktree numbering.

## 2. Exact command per frozen class

- Class A (backticked repo-relative path, optional `:line`, optional glob):
  `git -C <root> cat-file -e 4edb25d:<path>` per token; glob equivalent
  `git -C <root> ls-tree -r 4edb25d --name-only | grep -E '^census/round-14/verification.*\.json$'`.
- Class B (bare 7..40-char hex token in a revision-context cell):
  `git -C <root> cat-file -e <tok>^{commit}` — **zero tokens in this slice**; exercised only to test
  proposed repairs (§5).
- Class C (64-hex digest in a cell with exactly one backticked path):
  `git -C <root> show 4edb25d:<path> | sha256sum` — **zero tokens in this slice**; the same primitive
  was used for the digest-drift finding (§5 F1).

Cross-check with the frozen instrument (reads only; stdout):

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
    --rev 4edb25dfe262515d0da63224bbba71e02e36cba5 --format tsv | awk -F'\t' '$1>=50 && $1<=54'
50  tests/results/r12-maintenance-guard.txt              A  resolved  present at 4edb25d…
51  census/round-13/verification.json                    A  resolved  present at 4edb25d…
52  census/round-13/verification.json                    A  resolved  present at 4edb25d…
53  corpus/knowledge/git-repo-structure-readonly.md      A  resolved  present at 4edb25d…
54  census/round-14/verification*.json                   A  resolved  3 match(es) at 4edb25d…
54  corpus/lessons/round-14-verifier-spotcheck.md        A  resolved  present at 4edb25d…
$ … --format counts
assertions=56 resolved=53 skipped=33 mismatches=3      (exit 1, whole file)
```

The slice's local reach is 6 class-A assertions, 0 class-B, 0 class-C; the instrument skipped 6
span tokens inside these five rows (commands, flags, prose). The whole-file `mismatches=3` do **not**
come from this slice; they are lines 3 (`AXES.md`, fleet-relative pointer), 63 (`reason-after.txt`,
unnamed receipt) and 77 (`.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`, absent banked file).

## 3. Per-assertion result (executed)

All six class-A assertions re-derived independently of the instrument:

```
$ for p in tests/fixtures/r12-maintenance-guard.sh tests/results/r12-maintenance-guard.txt \
           tools/souji-cert-evidence.py census/round-13/verification.json \
           tests/fixtures/r13-quarantine-bounds.sh tests/fixtures/r13-repo-structure.sh \
           tools/souji-repo-structure.sh corpus/knowledge/git-repo-structure-readonly.md \
           corpus/lessons/round-14-verifier-spotcheck.md; do
    printf '%-55s ' "$p"; git cat-file -e 4edb25d:"$p" 2>/dev/null && echo PRESENT || echo ABSENT; done
tests/fixtures/r12-maintenance-guard.sh                 PRESENT
tests/results/r12-maintenance-guard.txt                 PRESENT
tools/souji-cert-evidence.py                            PRESENT
census/round-13/verification.json                       PRESENT
tests/fixtures/r13-quarantine-bounds.sh                 PRESENT
tests/fixtures/r13-repo-structure.sh                    PRESENT
tools/souji-repo-structure.sh                           PRESENT
corpus/knowledge/git-repo-structure-readonly.md         PRESENT
corpus/lessons/round-14-verifier-spotcheck.md           PRESENT
$ git ls-tree -r 4edb25d --name-only | grep -E '^census/round-14/verification.*\.json$'
census/round-14/verification-attempt-1.json
census/round-14/verification-plan.json
census/round-14/verification.json
$ git ls-tree -r 4edb25d --name-only | grep -xE \
    'tests/results/r12-maintenance-guard\.txt|census/round-13/verification\.json|corpus/knowledge/git-repo-structure-readonly\.md|corpus/lessons/round-14-verifier-spotcheck\.md|tests/fixtures/r12-maintenance-guard\.sh|tools/souji-cert-evidence\.py|tests/fixtures/r13-quarantine-bounds\.sh|tests/fixtures/r13-repo-structure\.sh|tools/souji-repo-structure\.sh'
nine exact-path hits, identical to the loop above
```

Four of those nine back a class-A assertion; the other five sit inside command spans that the frozen
classes skip, so they were checked separately. `tools/souji-evidence-cache.py` (the implementation
`S039` names) was checked the same way and is present.

Content cross-check of the *claims* the rows attach to these paths (executed: `git show` + text/JSON
parse; not re-execution):

| row | claim in cell | committed receipt text observed |
|---|---|---|
| 50 | `6/6 PASS, exit 0` | `tests/results/r12-maintenance-guard.txt`: `selftest=PASS ids=6/6`, `run1=0 run2=0 run3=0 selftest=0` |
| 51 | `36/36`; `external fixture 5/5` | `census/round-13/verification.json`: `selftest: 36/36 passed`; `fixture: 5/5 checks passed` |
| 52 | `5/5`; `same corrected fixture baseline red` | same receipt: `SUMMARY total=5 failed=0 hung=0`; red-before `total=5 failed=4 hung=2` exit 1 |
| 53 | `5/5` | same receipt: `structure-selftest … selftest=PASS ids=5/5` |
| 54 | refusal-only, synthetic-only | `census/round-14/verification.json`: `cache-consumer-red-green` exit 0 matched true |

**Verdict for the slice: 6/6 resolved, 0 mismatches, 0 skipped-under-A/B/C beyond the frozen skip
set.** No `mismatch:*` row exists, so no repair is owed under the frozen class definition. The
findings below are calibration/operability defects the frozen enum cannot see, each with the
minimal truth-preserving repair — none proposes deleting a capability claim.

## 4. Hex-adjacent tokens deliberately reported as skipped

Frozen-class candidates a reader might mistake for evidence: `6/6`, `36/36`, `5/5` ×3 (counts);
`S035/S036/S037`, `S039` (source ids: `S`-prefixed, ≤4 chars, outside `[0-9a-f]{7,40}`); `C1` (claim
label); `r12`/`r13`/`r14` (round labels, `r` is not a hex digit). The independent scan used

```
$ awk 'NR>=55 && NR<=59' SCORECARD.md | grep -oE '(^|[^A-Za-z0-9_.-])[0-9a-f]{7,40}([^A-Za-z0-9_.-]|$)'
NO 7-40 HEX TOKEN
$ awk 'NR>=55 && NR<=59' SCORECARD.md | grep -oE '[0-9a-f]{64}'
NO 64-HEX DIGEST
```

so the slice genuinely contains no class-B or class-C candidate. No year-like token occurs in it.

## 5. Findings

**F1 (medium, calibration/operability) — row 8's receipt is revision-drifted; the 5/5 is true only
at `6f8ee0f`.**
`census/round-13/verification.json` declares `measured_commit 6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6`
and pins `tools/souji-quarantine.sh` at `df4075112c36bae804b98766c4eb66b0e5b2b80b76d7333475ede27b06b168c4`.
At the measured revision the same path hashes to
`e2f2d083d679f1da165866c6190af1a948c43e080d7ae629e5b08a7199849e4d`:

```
$ git show 6f8ee0f:tools/souji-quarantine.sh | sha256sum   -> df407511…
$ git show 4edb25d:tools/souji-quarantine.sh | sha256sum   -> e2f2d083…
$ git log --oneline 6f8ee0f..4edb25d -- tools/souji-quarantine.sh
4f48343 … / 3f822e8 … / 4800fd7 …     (270 insertions after r13)
```

No committed receipt re-runs `tests/fixtures/r13-quarantine-bounds.sh` against the newer bytes:

```
$ for f in census/round-20/final-acceptance-b7b606b.json census/round-20/final-acceptance-4f30f23.json \
           census/round-20/final-acceptance-5ff7565.json census/round-21/acceptance-c2-first.json \
           census/round-21/final-out-S1.json census/round-21/final-out-S2.json \
           census/round-21/final-out-S3.json; do printf '%s: ' "$f"; \
    git show 4edb25d:$f | python3 -c 'import json,sys
d=json.load(sys.stdin); cs=d.get("commands") or []
print("commands=%d quarantine-bounds-runs=%d" % (len(cs), len([c for c in cs if "quarantine-bounds" in json.dumps(c.get("argv") or c.get("command") or "")])))'
  done
census/round-20/final-acceptance-b7b606b.json: commands=18 quarantine-bounds-runs=0
census/round-20/final-acceptance-4f30f23.json: commands=18 quarantine-bounds-runs=0
census/round-20/final-acceptance-5ff7565.json: commands=18 quarantine-bounds-runs=0
census/round-21/acceptance-c2-first.json: commands=18 quarantine-bounds-runs=0
census/round-21/final-out-S1.json: commands=18 quarantine-bounds-runs=0
census/round-21/final-out-S2.json: commands=18 quarantine-bounds-runs=0
census/round-21/final-out-S3.json: commands=18 quarantine-bounds-runs=0
```

In those later files the fixture appears only inside `input_sha256_*` inventories as
`23b2b879352b3a3ef2f3fe4297ab2818643c8d45db3a75dda2d5dd9c18b07f5e`-class entries (identical to the
base bytes), never as an executed argv. The drifted **tool** does have one post-drift exercise —
`census/round-18/final-verification-4800fd7.json` pins it at `e2f2d083…` and its `checks[7]`
`quarantine-selftest` exits 0 — but that is the tool's own selftest, not the fixture that carries
the bounded move/digest/refusal cases the row claims. The cell therefore presents an r13 measurement
as if it were current.
Repair (truth-preserving, cheapest first):
(a) append `measured at 6f8ee0f` to the cell — `git cat-file -e 6f8ee0f^{commit}` exits 0
(executed), so the added class-B token resolves (the cell already carries a `census/round-13/`
context, so the frozen class-B rule is the one that will police it); class A is unchanged and the
next counter run simply reports one more resolved assertion (N 56→57, M stays 0); or
(b) supply the missing committed receipt: run the fixture at `e2f2d083…` bytes and commit its
output as `tests/results/r13-quarantine-bounds.txt` (the path promised in
`census/round-13/registry-draft.md`, which git does not contain today) or under
`census/round-22/…`, and cite it. I did not run it: this audit is read-only and the fixture spawns
timeout/process cases (it produced the r13 red-before/green pair).
Keep the capability claim; only the revision binding is wrong.

**F2 (low-medium, calibration) — row 6's receipt is revision-unbound.**
`tests/results/r12-maintenance-guard.txt` is present and its text matches the claim, but it names
the fixture only through a host-local path (`/home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/
souji-shokunin/tests/fixtures/r12-maintenance-guard.sh`) and records no digest and no commit, and
the SCORECARD cell names no revision either — so class B never applies and the "6/6" cannot be tied
to committed bytes from the declaration alone. Mitigating fact (executed): receipt and fixture were
each introduced in `d7266c5e9493a3c78687af68d438c2584f75b3c0` and never modified since
(`git log --format=… -- <path>` returns exactly that one commit for both), and the fixture at
`4edb25d` hashes to `a359070a66706ad2570eb92f0ce87f5ba840136f02f3cf987adb57272e95a0f9`.
Repair: append `at d7266c5` to the cell (`git cat-file -e d7266c5^{commit}` exits 0, executed), or
record in the receipt (next commit) the fixture sha256 above plus the revision measured. Claim stays.

**F3 (low, calibration) — row 10's pointer is a glob that spans a non-receipt.**
`census/round-14/verification*.json` expands to three files: `verification.json` (6 results,
including the `cache-consumer-red-green` run the row's claim rests on), `verification-attempt-1.json`
(12 results, superseded first attempt) and `verification-plan.json` (`results=0`, a plan). The
assertion resolves under class A, but a reader cannot tell which file is the receipt.
Repair: name `census/round-14/verification.json` explicitly (class A presence verified) and keep
`corpus/lessons/round-14-verifier-spotcheck.md` as the outside-judgment pointer; optionally add
`census/round-14/cache-demonstration.py`, the script the receipt actually ran. No claim changes.

**F4 (informational, calibration scope) — the frozen classes do not defend the numbers in this
slice.** All five numeric claims and all four command spans are instrument-skipped, so a green C1
count over these rows attests only that receipt files exist. I verified the numbers out-of-class and
all five match the committed receipt text (§3). No action is possible inside this preregistration;
widening class A to command spans or adding a "receipt contains <claim>" class would require a new
preregistration, not an edit to this frozen enum.

**F5 (informational, coverage) — out-of-class registry citations resolve.**
`S035`/`S036`/`S037` are rows 55–57 of `corpus/SOURCES.md` (git-repo, git, repo.c) and the cited
knowledge file names all three on line 1; its body backs "refuses partial/promisor" (line 40) and
"reports the common Git directory" (line 11). `S039` is row 59 and its recorded source digest
`dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6` equals
`sha256(git show 4edb25d:tools/souji-evidence-cache.py)` exactly (executed); the implementation file
is present. No defect.

## 6. Residual risk and verification gaps

- Content checks are **text-level**: a receipt contains the claimed string; it is not proof the
  command was executed on the committed bytes. F1 is exactly that gap made concrete.
- No repository fixture was executed (read-only mandate): `5/5` at `e2f2d083…` and "stable
  special-file refusals" are unmeasured at the base revision. Stated as unmeasured, not as passed.
- The whole-file C1 counter still reports 3 mismatches at `4edb25d` (lines 3/63/77); they are
  outside this slice and untouched here. At `3216c19` (the tip when that run was made; the tip has
  since advanced to `d6a75ba`) the same counter printed
  `assertions=56 resolved=56 skipped=36 mismatches=0` (rc 0) — context only, not this audit's verdict.
- Instrument/`git` agreement was total for the slice: the 6 class-A tokens and their line numbers
  match between my manual `cat-file`/`ls-tree` pass and the frozen tool.
- No tool was installed or upgraded for this audit; no network access was used.

## Evidence

- `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap2.tsv` — 25 rows: 6 `class A` assertions (all
  `resolved`) plus every skipped candidate token with its explicit reason.
