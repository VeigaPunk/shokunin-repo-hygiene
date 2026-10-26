# SwarmMutationTester20 — C3 fixture × c3-counter-v3 mutation round (souji r31, wave 2)

## Status

STATUS: PASS — 8 mutants of tests/fixtures/r31-jj-object-clock.sh committed one-per-commit in a scratch clone at 2c16d018e40db7c23420a2c3bb546b52957bcc25 and each measured with census/round-31/c3-counter-v3.py; 6 killed, 2 survived (coverage findings, not contract changes); baseline and restored bytes both green; lane untouched.

## Evidence

Scratch: /fast/scratch/hyaku/souji-r31/w2-MutateFixture (removed after deliveries). Clone: `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D/c"` + `git -C "$D/c" remote remove origin`; `rev-parse HEAD` = 2c16d018e40db7c23420a2c3bb546b52957bcc25; `rev-parse --show-toplevel` verified before every commit; remotes=0. Pristine fixture sha256 780a68233e10ce1268ad9fea7bdb6b3eea89955346fe45918125962c352b4266.

Detector (serial, one run at a time):
`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-31/c3-counter-v3.py --root $D/c --rev <commit> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --scratch $D/counterscratch`

- Pristine 2c16d018e40db7c23420a2c3bb546b52957bcc25: `SUMMARY legs=13 fail=0 f1_entries=4` (L1-L13 all PASS; L13 detail `M1:...no=0<4=True M2:...no=0<4=True`).
- Each mutant: commit, run, then `git checkout 2c16d018e40db7c23420a2c3bb546b52957bcc25 -- tests/fixtures/r31-jj-object-clock.sh`; sha256 re-verified equal to pristine after every restore (8/8).
- Restored bytes committed as ce26654826cae2454927a160fb790f66977a3ee5 and re-run: `SUMMARY legs=13 fail=0 f1_entries=4`, fixture sha256 equal to pristine.
- Per-mutant delta vs pristine: every commit is `1 file changed` on tests/fixtures/r31-jj-object-clock.sh only (MF4 28+/28- block move; MF5 28-; MF7 3+/3-; others 1+/1-).
- Lane repo `git status --porcelain` before my delivery write: 0 entries.

Record baseline for kill analysis: census/round-31/records/jj-object-clock-run.txt has 17 `RESULT ` lines, 4 with `object_present=no` (lines 8, 14, 15, 19).

## Findings

1. SURVIVOR — reflog_hits provenance is unmeasured (axis: coverage). Mutant MF2 (11a3a71260ebf3b5a9c14472bff32ec3140ca76c) replaces `G reflog --all --format='%H'` with `G reflog --format='%H'` (HEAD reflog only) at tests/fixtures/r31-jj-object-clock.sh:105; detector `fail=0`, all 17 replayed lines byte-equal to the record. L9/L12 only pin fixture output to the committed record — census/round-31/c3-counter-v3.py:34-35: "their `RESULT ` lines equal RUN's `RESULT ` lines exactly (same lines, same order)" — and no leg re-derives reflog_hits from reality; amendments.txt:15 discloses exactly this: "reflog_hits is a fixture report, no leg re-derives it". Here HEAD-only happens to agree with `--all` (the one reflog entry naming B lives in the HEAD reflog), so the counter cannot distinguish an honest `--all` count from a HEAD-only count. A leg that re-derives reflog_hits independently (its own `git reflog --all` count compared to the fixture's) would close this.
2. SURVIVOR — keep_count pattern is unmeasured (axis: coverage). Mutant MF8 (e0044f1c23952435df78b1c49abebed61b457106) drops the `'refs/jj/keep/*'` pattern from keep_count at tests/fixtures/r31-jj-object-clock.sh:95, counting every ref; detector `fail=0`, byte-equal output. In these fresh colocated repos the ref namespace holds only keep refs, so the unpatterned count agrees empirically; same record-pinning blind spot as finding 1 (L9/L12 compare outputs, not computation). Any counter leg that re-derives keep_refs (or a scenario with a non-keep ref present) would close this.
3. L13 alone cannot catch a constant object_present (axis: operability of the leg, coverage of the cheat class). Mutant MF1 (53ef937ca76af0c1505c1252292cc80fc392d2da) prints `object_present` from a constant `yes` (fixture line 108); L13 PASSES because a constant-yes output satisfies its heuristic — census/round-31/c3-counter-v3.py:225: "ok = mrc == 0 and len(ml) == len(rl) and ml != rl and mno < nno" — the mutant runs differ from the record and carry fewer no-lines trivially. MF1 is killed only by L9 (lines differ from record) and L12 (`missing=['git cat-file -e']`, results_equal=False). The A1 rule "differ from it and carry strictly fewer object_present=no lines" (amendments.txt:13) is therefore satisfiable by a fixture that never measures anything, as long as the constant differs from the record; L9/L12 carry the kill.
4. Leg complementarity confirmed (no defect): L9 pins values, line count and ORDER (MF4 arms-swapped and MF7 reordered-execution die on L9's ordered equality; MF5 dies on 13≠17 lines); L12 pins tool provenance through PATH (MF6 `/usr/bin/git` keeps L9 green but loses `git reflog expire` and `git cat-file -e` from the shim log and freezes M1 at `differs=False`); L13 pins remover sensitivity (MF3 constant-no dies at `no=17<4=False`; MF6's M1 dies at `differs=False`). L8 is record-only by design and no fixture mutant can flip it (observed: L8 PASS on all 8 mutants).

## Attack log

Detector: census/round-31/c3-counter-v3.py, `--root $D/c --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --scratch $D/counterscratch`, `--rev` per row. Baseline pristine 2c16d018e40db7c23420a2c3bb546b52957bcc25 = PASS (legs=13 fail=0); restored ce26654826cae2454927a160fb790f66977a3ee5 = PASS (legs=13 fail=0). A baseline failure would have made every verdict inconclusive; baseline was green.

| mutant | commit (scratch clone) | delta vs pristine | failing legs | verdict |
|---|---|---|---|---|
| MF1 object_present constant `yes` | 53ef937ca76af0c1505c1252292cc80fc392d2da | 1+/1- | L9, L12 | KILLED |
| MF2 reflog_hits from HEAD reflog only | 11a3a71260ebf3b5a9c14472bff32ec3140ca76c | 1+/1- | none | SURVIVED |
| MF3 cat-file skipped, constant `no` | d2e643d34d7c7090f55eccdaa31ca1102efa25cd | 1+/1- | L9, L12, L13 | KILLED |
| MF4 reflog-only arm run before solo arm | 85b7e0ef69ab8f14600bd625d042719123da672b | 28+/28- | L9, L12 | KILLED |
| MF5 reflog-only arm dropped | d61d43554917c79f5f86b2d94ca30ceaf1b58d78 | 28- | L9, L12, L13 | KILLED |
| MF6 git by absolute /usr/bin/git path | ed5d9d568f08370d7262b4b752193bdd928bcd03 | 1+/1- | L12, L13 | KILLED |
| MF7 assigned steps reordered, labels printed in old order | 2fb327844ce9aa969dfdf60fd0a86e756659ba62 | 3+/3- | L9, L12 | KILLED |
| MF8 keep_count counts all refs | e0044f1c23952435df78b1c49abebed61b457106 | 1+/1- | none | SURVIVED |

Representative detector lines:
- MF1: `L9 FAIL replays=[(0, 17, False), (0, 17, False)]` / `L12 FAIL ... missing=['git cat-file -e']` / `L13 PASS M1:...no=0<4=True M2:...no=0<4=True` → `fail=2`
- MF2: `L9 PASS replays=[(0, 17, True), (0, 17, True)]` / `L12 PASS ... missing=[]` / `L13 PASS` → `fail=0`
- MF3: `L13 FAIL M1:...no=17<4=False M2:...no=17<4=False` → `fail=3`
- MF5: `L9 FAIL replays=[(0, 13, False), (0, 13, False)]` / `L13 FAIL M1:rc=0,lines=13,...` → `fail=3`
- MF6: `L12 FAIL rc=0 results_equal=True jj_calls=26 git_calls=6 missing=['git reflog expire', 'git cat-file -e']` / `L13 FAIL M1:rc=0,lines=17,differs=False,no=4<4=False M2:...no=3<4=True` → `fail=2`
- MF7: `L9 FAIL replays=[(0, 17, False), (0, 17, False)]` / `L12 FAIL ... results_equal=False` → `fail=2`

Restoration evidence: after each mutant run the fixture was restored from 2c16d018e40db7c23420a2c3bb546b52957bcc25 and sha256-verified 780a68233e10ce1268ad9fea7bdb6b3eea89955346fe45918125962c352b4266 (8/8 matches); a final restored-bytes commit ce26654826cae2454927a160fb790f66977a3ee5 re-passed the detector. The two survivors are coverage findings against the counter, not evidence about the landed entry; no contract change is proposed.

## Deliveries

- .ufo/waves/round-31/w2/SwarmMutationTester20.md (this report)
- Scratch /fast/scratch/hyaku/souji-r31/w2-MutateFixture removed after delivery; nothing written outside it and this report.
