# R40w2critic05 — attack on the C2 consumer arm (L6), round 40 wave 2

Seat: R40w2critic05 (role critic, leaf, no dispatch). Judged on: operability.
Landed revision attacked: `128e412b0ced3c243dc27c3dd3332054a611bc2e` (round-40 instruments).
Base: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (r39 tip, per `census/round-40/preregistration.txt`).
Lane HEAD at attack time, reported for contrast only: `549d9ec53a1f5932337ff14438fcd22b0621828d`
(`git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline 128e412..HEAD` lists `8a5fbdb`, `6ded124`, `556c24a`, `549d9ec`).

Toolchain used (already present; nothing installed): Python 3.14.8, git 2.56.0. No pacman, no install, no
change to any PATH directory.

## Verdict

| # | Attacked item | Verdict | Where it is shown |
|---|---|---|---|
| A | L6 question: does any of the seven consumer fixtures lose a passing case against base bytes? | **SAFE** | S1 below: `LOST_A_vs_C=[]` and `LOST_A_vs_B=[]` for all seven; the consumer tool and fixture bytes are identical at base and landed |
| B | The C2 counter at the landed revision produces a receipt with legs L1-L6 (the measurement the preregistration names) | **FALSIFIED** | S4: `committed@landed rc=1 ... ModuleNotFoundError: No module named 'docstring_classes'`; with a scratch-only module-name shim, `SUMMARY legs=7 pass=4 fail=3 harm=0` (L1, L2, L5 FAIL) |
| C | L6 is a sound consumer-harm detector (green only when no consumer lost a case) | **FALSIFIED (latent)** | S3: a consumer fixture whose own control is forced red exits rc=1 yet the counter's green predicate is `True` |
| D | L6 harm test is per-case | **FALSIFIED (design)** | `census/round-40/c2-counter.py:321-323` compares pass counts only, although the fixtures print per-case `case-<id>=PASS|FAIL` lines |
| E | Consumer set kills every declared consumer-facing mutant | **FALSIFIED (coverage hole)** | S2: mutant `MC2-ancestor-error-as-no` survives all three citation consumers |

Overall verdict on the attacked question: **FALSIFIED** for the landed instrument (B is a hard failure: the
committed L6-bearing counter cannot run at its own landed revision). The consumer-harm question itself
(A) is **SAFE**: no consumer regresses against base at the landed bytes, measured per case.

## Commands run and their real output

All commands are re-runnable. The whole attack is one script, committed to my seat directory as a
scratch artifact I named (not a lane edit):
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w2/R40w2critic05-consumer-probe.py`

Single invocation used for every number below:

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w2/R40w2critic05-consumer-probe.py \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin \
  --landed 128e412b0ced3c243dc27c3dd3332054a611bc2e \
  --base 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --head 549d9ec53a1f5932337ff14438fcd22b0621828d \
  --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2critic05/run
```

Exit 0, wall time about 30 s. The script exports `tools tests census corpus` from each revision with
`git -C LANE archive REV -- ...`, so the bytes tested are committed bytes, not the working tree.

Preliminary byte identity (run by hand, same exports):

```
sha256sum .../landed/tools/souji-worktree-drift.py .../base/tools/souji-worktree-drift.py \
          .../landed/tools/souji-citation-reconcile.py .../base/tools/souji-citation-reconcile.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  .../landed/tools/souji-worktree-drift.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  .../base/tools/souji-worktree-drift.py
59f1e57d7af02cac675757066fb6fa2629a0153f21c98a62e04b6d3b301d2b73  .../landed/tools/souji-citation-reconcile.py
59f1e57d7af02cac675757066fb6fa2629a0153f21c98a62e04b6d3b301d2b73  .../base/tools/souji-citation-reconcile.py
diff -rq .../landed/tests .../base/tests
Only in .../landed/tests/fixtures: r40-c1-evidence.py
Only in .../landed/tests/fixtures: r40-docstring-joined.py
Only in .../landed/tests/fixtures: r40-drift-record-branches.py
```

Also `git rev-parse 128e412…:tests/fixtures/<f>` and `…0242085…:tests/fixtures/<f>` give equal blobs for
all seven consumer fixtures (`r38-drift-record`, `r36-worktree-drift`, `r38-drift-write-envelope`,
`r39-drift-record-rules`, `r37-citation-reconcile`, `r38-citation-commit`, `r39-citation-rev`); both tools
are byte-identical as well. The only tree differences in `tools`, `tests` and `census` are the r40 additions.

### S1 — seven consumers, four arms (A fixture@landed+tool@landed, B fixture@landed+tool@base, C fixture@base+tool@base, D fixture@base+tool@landed)

```
S1 consumer arms: A=fixture@landed tool@landed, B=fixture@landed tool@base, C=fixture@base tool@base, D=fixture@base tool@landed
r38-drift-record rc=0/0/0/0 cases=10 pass(A)=10 pass(C)=10 LOST_A_vs_C=[] LOST_A_vs_B=[] summary(A)=['SUMMARY cases=10 pass=10 fail=0']
r36-worktree-drift rc=0/0/0/0 cases=12 pass(A)=12 pass(C)=12 LOST_A_vs_C=[] LOST_A_vs_B=[] summary(A)=['SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED']
r38-drift-write-envelope rc=0/0/0/0 cases=12 pass(A)=12 pass(C)=12 LOST_A_vs_C=[] LOST_A_vs_B=[] summary(A)=['SUMMARY cases=12 pass=12 fail=0']
r39-drift-record-rules rc=0/0/0/0 cases=7 pass(A)=7 pass(C)=7 LOST_A_vs_C=[] LOST_A_vs_B=[] summary(A)=['SUMMARY cases=7 pass=7 fail=0']
r37-citation-reconcile rc=0/0/0/0 cases=16 pass(A)=16 pass(C)=16 LOST_A_vs_C=[] LOST_A_vs_B=[] summary(A)=['SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED']
r38-citation-commit rc=0/0/0/0 cases=14 pass(A)=14 pass(C)=14 LOST_A_vs_C=[] LOST_A_vs_B=[] summary(A)=['SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED']
r39-citation-rev rc=0/0/0/0 cases=8 pass(A)=8 pass(C)=8 LOST_A_vs_C=[] LOST_A_vs_B=[] summary(A)=['SUMMARY cases=8 pass=8 fail=0']
```

Per-case identity was checked on the `case-<id>=PASS|FAIL` lines (not just the counts). Result: 79 cases
across the seven consumers (10+12+12+7+16+14+8), all PASS in all four arms, zero lost. The `rc` column is the process exit code
of each fixture run.

This answers A: **SAFE**. It is structural as well as measured: the consumer tools and fixtures are
byte-identical at base and landed, so the round cannot have changed what these consumers observe.

### S2 — mutant tools (scratch copies of the landed tool) against the landed fixtures

Each mutant is a single-line edit in a scratch copy; every edit site matched exactly once (the script asserts
it). `L6 would flag` = the counter's pass-count test `new_r[1] < old_r[1]` (`census/round-40/c2-counter.py:321`)
would fire.

```
MD1-empty-off r38-drift-record landed rc=0 pass=10/10 | mutant rc=1 pass=9/9 | LOST=['case-empty-record'] GAINED=[] | L6 would flag=True
MD1-empty-off r36-worktree-drift landed rc=0 pass=12/12 | mutant rc=1 pass=11/11 | LOST=['case-empty'] GAINED=[] | L6 would flag=True
MD1-empty-off r38-drift-write-envelope landed rc=0 pass=12/12 | mutant rc=0 pass=12/12 | LOST=[] GAINED=[] | L6 would flag=False
MD1-empty-off r39-drift-record-rules landed rc=0 pass=7/7 | mutant rc=1 pass=6/6 | LOST=['case-comments-total-only'] GAINED=[] | L6 would flag=True
MD2-total-repos-off r38-drift-record landed rc=0 pass=10/10 | mutant rc=1 pass=9/9 | LOST=['case-total-repos-mismatch'] GAINED=[] | L6 would flag=True
MD2-total-repos-off r36-worktree-drift landed rc=0 pass=12/12 | mutant rc=1 pass=11/11 | LOST=['case-total-mismatch'] GAINED=[] | L6 would flag=True
MD2-total-repos-off r38-drift-write-envelope landed rc=0 pass=12/12 | mutant rc=0 pass=12/12 | LOST=[] GAINED=[] | L6 would flag=False
MD2-total-repos-off r39-drift-record-rules landed rc=0 pass=7/7 | mutant rc=0 pass=7/7 | LOST=[] GAINED=[] | L6 would flag=False
MD3-outside-root-off r38-drift-record landed rc=0 pass=10/10 | mutant rc=0 pass=10/10 | LOST=[] GAINED=[] | L6 would flag=False
MD3-outside-root-off r36-worktree-drift landed rc=0 pass=12/12 | mutant rc=0 pass=12/12 | LOST=[] GAINED=[] | L6 would flag=False
MD3-outside-root-off r38-drift-write-envelope landed rc=0 pass=12/12 | mutant rc=1 pass=11/11 | LOST=['case-record-outside-root'] GAINED=[] | L6 would flag=True
MD3-outside-root-off r39-drift-record-rules landed rc=0 pass=7/7 | mutant rc=1 pass=6/6 | LOST=['case-outside-root'] GAINED=[] | L6 would flag=True
MC1-rev-unresolved-off r37-citation-reconcile landed rc=0 pass=16/16 | mutant rc=0 pass=16/16 | LOST=[] GAINED=[] | L6 would flag=False
MC1-rev-unresolved-off r38-citation-commit landed rc=0 pass=14/14 | mutant rc=0 pass=14/14 | LOST=[] GAINED=[] | L6 would flag=False
MC1-rev-unresolved-off r39-citation-rev landed rc=0 pass=8/8 | mutant rc=1 pass=5/5 | LOST=['case-rev-blob', 'case-rev-tree', 'case-rev-unknown'] GAINED=[] | L6 would flag=True
MC2-ancestor-error-as-no r37-citation-reconcile landed rc=0 pass=16/16 | mutant rc=0 pass=16/16 | LOST=[] GAINED=[] | L6 would flag=False
MC2-ancestor-error-as-no r38-citation-commit landed rc=0 pass=14/14 | mutant rc=0 pass=14/14 | LOST=[] GAINED=[] | L6 would flag=False
MC2-ancestor-error-as-no r39-citation-rev landed rc=0 pass=8/8 | mutant rc=0 pass=8/8 | LOST=[] GAINED=[] | L6 would flag=False
```

Reading: 8 of 18 mutant-consumer pairs are caught. At mutant level the consumer arm kills 4 of 5 mutants
(MD1, MD2, MD3, MC1). **MC2 survives all consumers** (E). The mutants are scratch copies only; no lane byte
changed.

### S3 — control blindness: consumer fixture with its own control forced red

Scratch copies of two consumers have their control predicate forced to `False`
(`tests/fixtures/r36-worktree-drift.py:286` `control_ok = not replicated` → `False`;
`tests/fixtures/r37-citation-reconcile.py:264` `control_ok = not control_replicated` → `False`).

```
r36-worktree-drift fixture rc=1 ['SUMMARY cases=12 pass=12 fail=0 control=STUB-NOT-REJECTED'] | counter L6 green predicate=True
r37-citation-reconcile fixture rc=1 ['SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-NOT-REJECTED'] | counter L6 green predicate=True
```

The fixtures' own exit code is 1 (r36 `tests/fixtures/r36-worktree-drift.py:295`, r37 control at
`:264-275`), but the counter reads only the `SUMMARY` counts. `census/round-40/c2-counter.py:318`
(`green = new_r[0] == new_r[1] and new_r[2] == 0`) and the `run_fixture` return at `:185` (which includes
the rc, unused in L6) mean L6 stays green while a consumer's control is red. The control is currently green
at landed (S1 summaries show `STUB-REJECTED` / `FALSE-GREEN-REJECTED`), so this is latent, not a present
harm. A future control regression would not reach L6. **FALSIFIED (latent)** for C.

### S4 — the C2 counter

```
S4 the C2 counter
committed@landed rc=1 stdout='' stderr_last=["ModuleNotFoundError: No module named 'docstring_classes'"]
landed+module-shim rc=1
LEG L1 FAIL new rc=2 class=True old rc=2 class=True
LEG L2 FAIL new rc=2 class=True old rc=2 class=True
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 FAIL new=None old(one-line)=None
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=4 fail=3 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
committed@head rc=0
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
```

The committed landed counter (run from `git archive` bytes of `128e412`, `census/round-40/c2-counter.py`)
dies on import before any leg runs:

- `census/round-40/c2-counter.py:45-46` — `sys.path.insert(...)` then `import docstring_classes as dc`.
- The committed file is `census/round-40/docstring-classes.py` (hyphen, blob sha256 prefix `bc418a58e751`). The
  name the counter imports does not exist at the landed revision. This is a hard failure, not a finding:
  no L-leg line is printed, exit 1.

Three further landed-counter defects are visible once the import is shimmed (scratch copy only):

- **L1/L2 cannot pass at the declared base.** `census/round-40/c2-counter.py:221` runs the "old" arm on
  `args.base_rev` = `0242085`, where the unresolved-`--rev` defect is already repaired (the base refuses
  it with `REFUSAL REV-UNRESOLVED`, rc 2, as the probe showed). So `old_has` is True and `new_ok and not
  old_has` is always False. HEAD fixes this by adding `--defect-base-rev` (`ed30b7f5…`), where the defect
  is live: HEAD L1 `old rc=1 class=False`.
- **L5 cannot run.** `census/round-40/c2-counter.py:178-179` `run_fixture` always appends `--work`, but
  `tests/fixtures/r40-docstring-joined.py:100-102` accepts only `--analyzer`, `--tool`, `--one-line`, so
  argparse exits 2 (`unrecognized arguments: --work …`), no `SUMMARY` line, `run_fixture` returns `None`
  (`:184`). HEAD fixes this with `with_work=False`.
- **L6 is not measured against the base fixture.** At landed the consumer source is read once at
  `args.rev` (`census/round-40/c2-counter.py:302`) and written to one `fixp` (`:307`) that both arms run
  (`:312-313`). The counter therefore compares the candidate fixture against two tools; it never runs the
  base fixture bytes. Harmless today (S1 shows the fixture bytes are equal), but not what the leg's text says.

HEAD's counter (`549d9ec`) runs 7/7 with the same tools and fixtures. HEAD therefore has a green L6, but
that receipt is not the landed revision's receipt. The round's landed evidence for C2 is a crash.

### Other probes run (not in the script)

- Envelope fixture base control: `python3 -B …/tests/fixtures/r38-drift-write-envelope.py --tool <landed> --base-tool <base>`
  prints `BASE-BEHAVIORAL failed=0 cases=` and `SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=0 behavioral_fail=0`
  (rc 0). The counter never passes `--base-tool` (`census/round-40/c2-counter.py` CONSUMERS row at landed line 65,
  and the L6 loop passes only `--tool`). So the envelope's base control, which exists to show the
  base fails behaviourally (`tests/fixtures/r38-drift-write-envelope.py:297-305`), is not in L6 and would
  show nothing at this base pair anyway (the escapes were repaired before `0242085`).
- Base citation tool on an unresolvable revision: `python3 -B <base>/tools/souji-citation-reconcile.py --root <lane> --rev 0000…0 --register census/round-38/cells.tsv --register-rev 0242085…` → rc 2, `REFUSAL REV-UNRESOLVED: --rev 000… does not resolve to a commit`. Confirms that the base already refuses, which is why L1's old arm is always refused at base (see above).

## File:line of everything attacked

Landed bytes (`git show 128e412:<path>`):

- `census/round-40/c2-counter.py:45-46` — import of `docstring_classes` (missing module): **crash**.
- `census/round-40/c2-counter.py:62-70` — `CONSUMERS` table (seven consumers).
- `census/round-40/c2-counter.py:178-185` — `run_fixture`: always appends `--work` (`:179`); `SUMMARY` regex (`:182`); returns `None` without a SUMMARY (`:184`); returns rc (`:185`), rc unused by L6.
- `census/round-40/c2-counter.py:219-227` — L1 (old arm = base revision, `:221`).
- `census/round-40/c2-counter.py:292-296` — L5 (`run_fixture` calls without `with_work`).
- `census/round-40/c2-counter.py:299-325` — L6: `src` from `args.rev` (`:302`), `fixp` (`:307`), `new_r`/`old_r` (`:312-313`), `green` (`:318`) ignores rc, pass-count harm `:321-323`, leg `:325`.
- `census/round-40/docstring-classes.py` — analyser the counter cannot import (sha256 prefix `bc418a58e751`).
- `tests/fixtures/r40-docstring-joined.py:100-102` — no `--work` argument.
- `tests/fixtures/r36-worktree-drift.py:286-295` — control and exit; forced red in S3.
- `tests/fixtures/r37-citation-reconcile.py:264-275` — control and exit; forced red in S3.
- `tests/fixtures/r38-citation-commit.py:185-200` — vacuity control; `control_tag` `:199` (not forced; control `SUMMARY` only, rc not probed).
- `tests/fixtures/r38-drift-write-envelope.py:297-305` — `--base-tool` control, not passed by the counter.
- `tools/souji-worktree-drift.py:167-168` (RECORD-EMPTY), `:170-171` (TOTAL repos), `:292-293` (RECORD-OUTSIDE-ROOT) — mutant sites MD1-MD3.
- `tools/souji-citation-reconcile.py:248-251` (REV-UNRESOLVED) — mutant site MC1; `:204-212` `ancestor_status` — mutant site MC2 (`"error"` → `"no"`, `:211` region).

HEAD bytes (`549d9ec`, contrast only): `census/round-40/c2-counter.py` L6 block at `:328-354` (green `:347`, harm `:350-352`), `run_fixture` with `with_work` (`:178-204`).

## What I could not establish

- L6 cannot detect a regression that is both a lost case and a gained case in the same consumer (pass-count
  arithmetic cancels). I did not construct such a mutant; the claim is [INFERENCE] from `c2-counter.py:321-323`.
- The consumer set has no case that pins the `error` class of `ancestor_status` (MC2). Whether that behaviour
  is supposed to be a refusal is not stated anywhere in the consumer fixtures I read.
- `r38-citation-commit`'s rc under a forced control was not probed; only the SUMMARY tag is read there.

## Scratch

Scratch dir: `/fast/scratch/hyaku/souji-r40/w2/R40w2critic05/` (exports `landed/`, `base/`, `head/`, `run/`, `shim/`, mutants, work dirs). It is removed at the end of this seat; see the line below.

Scratch removed: yes. `rm -rf -- /fast/scratch/hyaku/souji-r40/w2/R40w2critic05` ran and the path no longer exists.
The re-runnable probe above lives in the lane's w2 directory as a named scratch artifact, and it writes only under the `--scratch` path it is given.
