# SwarmExecutor28 — r33 w1, C2 leg O1 (evidence-cache selftest scratch root)

## Status
STATUS: PASS — Q71 repair of `tools/souji-evidence-cache.py` plus the Q73-justified correction of its one committed
byte-pin consumer; frozen counter at the candidate reads `legs=4 pass=1 fail=0 harm=0` with O1 PASS and G1/G2/G3 PASS,
against `pass=0 fail=1` (O1 FAIL) at 2d9bca55a9f042a2c9ed60a797a8069e74c41f46. Full C2 target (11 legs) is the L1's;
not claimed here. Not an attack item, so no attack log.

## Evidence

Revisions: base 6017a482e7068d5afb7617640198fbb0fe743357, list-rev/prereg 2d9bca55a9f042a2c9ed60a797a8069e74c41f46,
candidate (scratch) 1595c203cc34083bc67c0edb28c131bcb01cb3f6. Everything ran in
`/fast/scratch/hyaku/souji-r33/FixO1/c` (clone, origin removed; throwaway identity; deleted after this report).

Frozen counter, `--only O1,G1,G2,G3`, both points (`python3 -B …/census/round-33/c2-counter.py … --scratch <scratch>`):

```
2d9bca5  LEG O1 sandbox FAIL base=rc0:W302:selftest: 48/48 passed  sbox=rc2:W0:selftest-unavailable: [Errno 30] Read-only file system: '<TMP>'
2d9bca5  LEG G1/G2/G3 PASS; SUMMARY legs=4 pass=0 fail=1 harm=0 partial=1
1595c20  LEG O1 sandbox PASS base=rc0:W302:selftest: 48/48 passed  sbox=rc0:W303:selftest: 48/48 passed
1595c20  LEG G1 guard PASS base=rc0:"total": 258      rev=rc0:"total": 258
1595c20  LEG G2 guard PASS base=rc0:"survived": 7     rev=rc0:"survived": 7
1595c20  LEG G3 guard PASS base=rc0:fixture: 22/22 checks passed  rev=rc0:fixture: 22/22 checks passed
1595c20  SUMMARY legs=4 pass=1 fail=0 harm=0 partial=1
```

Mechanism falsifier (tool repaired, runner untouched at 2d9bca5):
`r22-result-oracle.py` rc 1 `total 258 pass 256 fail 2` (`positive/clean-cache-demonstration`,
`positive/cache-transient-path-and-time`); `mutation-adequacy.py` rc 1 `"survived": 0`. With the runner correction:
oracle rc 0 258/258; mutation-adequacy rc 0, 59 mutants, 52 killed, 7 survived, `disagreeing_with_expect: []`, and
`gate-sha` still killed by `adequacy/cache/gate-sha-mismatch`, `adequacy/residual/cache/gate-both-slots-wrong`,
`adequacy/residual2/r3/cache/gate-empty`.

Scratch root moved, measured not grepped: with `TMPDIR=<scratch>`, `strace -e trace=mkdir,mkdirat` over
`--selftest` records 209 scratch-path mentions rooted `/var/tmp` at base and 209 rooted `<scratch>` at the candidate;
`ls -d /var/tmp/souji-r14-cache-selftest.*` = 0 afterwards, `<scratch>` empty; `selftest: 48/48 passed` rc 0 at both.

Refusals (Q74), base vs candidate identical rc + finding line: `--root /var/tmp/token-audit` rc2
`root-protected: --root is secret-shaped name 'token-audit'`; `--root /etc` rc2 `root-protected`; record declaring
`.ssh/id_ed25519` rc2 `path-protected`; `--root <symlink>` rc2 `root-symlink`; `--root /var/tmp` still evaluated
(rc1 stale), not refused. No-writable-root refusal still fires at both (bwrap, `/tmp`,`/var/tmp`,`/dev/shm` read-only,
cwd read-only): rc2 `selftest-unavailable`. `/var/tmp` mentions in the tool: base 4 (33/144/1295/1311), candidate 1
(144, the name-pattern example).

Q73 consumers (`git -C <clone> grep -l tools/souji-evidence-cache.py -- tests/fixtures census` = 79 files, identical
listing at both revisions; 9 live executables, plus the oracle and mutation-adequacy which reach the tool through the
runner), rc + last digit-bearing line base -> candidate:
oracle 258 -> 258; mutation-adequacy `"survived": 7` -> `"survived": 7`; r14-evidence-cache 22/22 -> 22/22;
r20-input-binding `total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=31` ->
same but `baseline_mismatches=32`; cache-demonstration status ok 33/33 checks residue [] -> same;
count-claims rc0 with byte-identical output after rev normalization; r13 run-verification, r14 run-verification,
r14 run-targeted rc2 with the same refusal lines; r20 run-acceptance rc2 (refuses outside the literal lane path).

## Findings
1. The r32 red was a false pin, not a tool property: `census/round-21/run-acceptance.py:503` compared the pinned r21
   payload digest (`census/round-21/final-out-S1.json`, tool sha `dd279ba9…`) with the **live** tool, while
   `tests/fixtures/r22-result-oracle.py:17,96-103` re-grades that payload with `root = ROOT` (the lane checkout) at
   revision `ff425ab8…`. Any tool byte change failed two literal positives, and
   `census/round-22/mutation-adequacy.py` requires the pristine runner green, so it followed.
2. Repair is two files: the tool's selftest scratch root from `TMPDIR` (`tempfile.mkdtemp` without `dir=`, caller
   `TMPDIR` passed to children, docstring line 33) and the consumer reading the gate digest at the graded revision.
   Q71 (`corpus/QUALITY.md:176`): "takes its scratch root from the caller's `TMPDIR`"; Q73 (`:178`): "is either
   regenerated with its own committed script at the candidate, or the tool edit is reverted"; Q74 (`:179`):
   "every base refusal code still fires for its base input".
   Justified, not a weakening: real runs already bind the tree to the revision
   (`census/round-21/run-acceptance.py:246-256` `combined_snapshot` via `pin.input_snapshot`, plus
   `pin.resolve_durable(..., tree_check=True)`, which also keeps the symlink/non-regular refusals), and the pinned
   payload is a historical record of revision `ff425ab`, never rewritten by hand.
3. No re-pin is needed: `tests/fixtures/r15-preservation-frozen/{expected,record}.json` pin neither
   `tools/souji-evidence-cache.py` nor `census/round-21/run-acceptance.py` (grep count 0 in both files), so G4/G5 are
   untouched by this patch.
4. `SKILL.md:208` (gate registry, `souji-evidence-cache` write-scope cell) still claims "isolated selftest
   `/var/tmp`", now false; L1 restatement, out of this leg's patch scope (C1 measures SCORECARD.md rows only).
5. `tests/fixtures/r20-input-binding.py` SUMMARY moves `baseline_mismatches=31 -> 32` because the tool is in its
   measured closure: a revision-drift data count on a still-green gate (rc0, `fail=0`, `inventory=exact`), the same
   class as the r32 T18 anchor.
6. `census/round-20/run-acceptance.py:458` carries the identical live read but refuses in any clone
   ("root must be the lane path used by the bounded r16/r18 fixtures"), so it is unmeasurable from scratch and green by
   construction when it runs (clone at `--rev`); left unchanged and reported.
7. `tempfile.gettempdir()` keeps Python's documented fallback when `TMPDIR` is unset or unusable (measured: `TMPDIR`
   nonexistent -> rc0 via the default root; `TMPDIR=/proc` -> rc0). Q71 names exactly this form as compliant.
8. Lane config sets `diff.mnemonicPrefix=true`; a delivery diff must be generated with
   `git -c diff.mnemonicPrefix=false diff <rev>` (the shipped patch uses `a/…` `b/…` and reverse-applies).

## Deliveries
- `.ufo/waves/round-33/w1/deliver-c2-O1.patch` — `git diff 2d9bca55a9f042a2c9ed60a797a8069e74c41f46` of the scratch
  commit `1595c203cc34083bc67c0edb28c131bcb01cb3f6` (2 files, +13/-6; `tools/souji-evidence-cache.py` and the Q73
  consumer `census/round-21/run-acceptance.py`).
- `.ufo/waves/round-33/w1/deliver-c2-O1.md` — full receipts: mechanism, both counter runs, strace counts, the 8-consumer
  Q73 table, the Q74 refusal matrix, and the residual list for the L1.
- `.ufo/waves/round-33/w1/SwarmExecutor28.md` — this report.
