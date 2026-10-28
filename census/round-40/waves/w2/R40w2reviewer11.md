# R40w2reviewer11 — LG-SEAT-UNCARRIED attack

## Scope and verdict

Attacked the round's use of wave-1 seat reports: whether concrete findings reported there are answered in landed commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Frozen claims were read first from `census/round-40/preregistration.txt`; no edits to them. **Verdict: FALSIFIED (LG-SEAT-UNCARRIED).** At least one concrete, actionable W1 defect remains unanswered: the C3 invalid-byte fixture decodes child output in text mode and its tested mutant set avoids the raw-byte failure that W1 specifically demonstrated.

## Commands and real output

Commands actually run (all repo paths absolute):

```sh
# read /home/vgpnk/.omp/agent/RULES.md
# read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
# read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w1/R40reviewer06.md
# read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w1/R40reviewer18.md
# read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w1/R40critic07.md
# read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w1/R40reviewer30.md
# read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w1/R40reviewer42.md
# read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w2/R40w2reviewer05.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat 128e412b0ced3c243dc27c3dd3332054a611bc2e
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/c3-counter.py | nl -ba | grep -E 'M15|M16|M17|M18|cases>=|crash =|failing|SUMMARY'
# read /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r40-drift-record-branches.py:1-150
```

Commit summary output:

```text
commit 128e412b0ced3c243dc27c3dd3332054a611bc2e
Author: souji-shokunin <souji@shokunin.local>
Date:   Wed Oct 28 15:52:14 2026 -0300

    round-40: instruments, sources, knowledge — C1 evidence-bound counter, C2 joined docstring classes, C3 record-branch battery

 census/round-40/c1-counter.py                      |  362 +++
 census/round-40/c2-counter.py                      |  341 +++
 census/round-40/c3-counter.py                      |  211 ++
 ...
 tests/fixtures/r40-drift-record-branches.py        |  150 ++
```

Relevant counter output from source inspection:

```text
9  M15 the parser assigns the LAST TOTAL row it reads; the mutant keeps the FIRST
11 M16 --skip-unrecorded ... mutant always scans
12 M17 ... decode ... replace ... mutant uses ignore
14 M18 a TOTAL row whose repos disagrees ... mutant accepts it
62 (M15, ...)
66 (M16, ...)
67 (M17, ... decode(..., "ignore"))
68 (M18, ...)
115 crash = "Traceback (most recent call last)" in proc.stderr
116 failing = [ ... case names ... ]
118 killed = proc.returncode == 1 and fails > 0 and not crash
202 SUMMARY mutants=%d killed=%d survived=%d pristine=ok base_killed=%d cases=%d
```

The fixture source read returned these decisive lines:

```text
49 subprocess.run(... stdout=PIPE, stderr=PIPE, text=True, ...)
82 subprocess.run(tool, ... stdout=PIPE, stderr=PIPE, text=True, ...)
85 env=ENV, stdout=PIPE, stderr=PIPE, text=True
87 out = proc.stdout + proc.stderr
102 run_record(... "total-duplicate-identical" ...)
104-106 total-conflicting-second
110-113 skip-unrecorded-suppresses / unrecorded-without-flag
114-120 invalid-utf8-in-repo-name, invalid-utf8-in-comment
```

## Findings: concrete W1 defects still unanswered

1. **F5 / F4 raw undecodable child-output crash (HIGH, LG-SEAT-UNCARRIED).** W1 `R40reviewer06.md:361-388` (M52, decode `surrogateescape`) and `R40reviewer18.md:122-131` (ME1) report that the fixture's `text=True` subprocess decoding raises `UnicodeDecodeError` when the mutant emits raw `0xff`; this produces no fixture SUMMARY and is a harness defect, not a semantic kill. Landed `tests/fixtures/r40-drift-record-branches.py:82-86` still uses `text=True` for the tool subprocess. Landed `census/round-40/c3-counter.py:62-68` declares M17 as `replace`→`ignore`, not the reported `surrogateescape` mutant; thus its battery does not exercise the failure. This is a concrete unchanged vulnerable path, not an inference that a particular command was run. The direct line evidence is the fixture mode and the absence of a raw-byte mutant from the declared set.

2. **F4/F6 accounting and unreachable coverage (MEDIUM, LG-SEAT-UNCARRIED).** W1 `R40reviewer06.md:319-359` reports that asserting the `UNRECORDED` row alone misses M51 changing `live_regs/live_prunable` in SUMMARY, and that `unreachable` needs an unrecorded `.git` file pointing to a missing gitdir (M50). Landed fixture `tests/fixtures/r40-drift-record-branches.py:110-113` only checks `SUMMARY` for the skip-on row and `UNRECORDED` for skip-off; it creates three ordinary repos at lines 62-69, not the `.git`-file/missing-gitdir condition. The counter battery at `census/round-40/c3-counter.py:62-68` contains no M50/M51 accounting mutants. Those reported observable surfaces are therefore not addressed by this fixture/battery.

3. **F1 scoring defect is answered.** W1 `R40reviewer18.md:28-87` reports tool traceback echoed into fixture stdout falsely setting crash. Landed C3 counter `census/round-40/c3-counter.py:115-118` checks only fixture stderr and captures failing case names; this is a direct remedy. W2 reviewer05 also exercised the landed counter successfully (its report lines 13-27).

4. **F2 identical TOTAL case is answered for the mutant identified.** W1 `R40reviewer06.md:235-259` and `R40reviewer42.md:247-281` warn that identical rows do not discriminate first-wins. Landed fixture includes `total-conflicting-second` at `tests/fixtures/r40-drift-record-branches.py:104-106`, and the declared M15 first-wins mutant at `census/round-40/c3-counter.py:62`; so the actionable first-wins edge is represented. The identical case at fixture lines 102-103 is not alone.

## Limits / reproducibility

This assigned attack is review of wave-1 reports against landed bytes, not a rerun of counter mutations. No scratch directory was created; therefore scratch removal is **not applicable**. No tool installed. No semantic lsp device was available in this seat's tool inventory; cited evidence is direct line inspection of the committed revision, not grep presented as semantic proof. The W1 reports identify the exact mutant and behavioral outputs for the remaining harness/accounting gaps, and the landed source lines show those cases are absent or still use the warned-about mode.