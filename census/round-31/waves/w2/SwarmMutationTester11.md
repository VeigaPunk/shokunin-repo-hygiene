# SwarmMutationTester11 — C2 gate mutation round (souji r31, wave 2)

## Status

STATUS: PASS — all 10 assigned mutants built, committed and run against both detectors in scratch; 8 killed by both, 2 survived both (M4 fence-awareness, M10 digits-prose) with live-behavior demos; pristine bytes restored; lane untouched; scratch removed.

## Evidence

Setup (contract-compliant): `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /fast/scratch/hyaku/souji-r31/w2-MutateGate/c`, origin removed, HEAD = 2c16d018e40db7c23420a2c3bb546b52957bcc25; `TMPDIR=/fast/scratch/hyaku/souji-r31/w2-MutateGate/tmp`; every counter run serial, `--scratch` under my own tmp; no lane writes except this report.

Pristine gate sha256 `577f1387ad51fc554f547a2aa4c40754ad73460db359de3178d40b559f09d8b8` (tip bytes).

Baseline (pristine tip):
- `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` → rc=0, `cases=10 pass=10 control=FALSE-GREEN-REJECTED`.
- `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-31/c2-counter-v3.py --root <clone> --rev 2c16d018… --base 9f17a1ef… --fleet-root /home/vgpnk/Projects/shokunin --scratch <tmp>/ctr-base` → rc=0, `SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok`.

Detectors per mutant (fixture = precision fixture `--tool <mutant working copy>`; counter = c2-counter-v3 with `--rev <mutant commit>`):

| Mutant | Commit | Gate sha256 (16) | Fixture | Counter v3 | Verdict |
|---|---|---|---|---|---|
| M1 drop union (base wave-dir-else-capture) | 4988e49a8c4de0f39a90f0405201104e6ead4e7e | 5a257da0217022bf | G1 FAIL `checked_reports=1 want 2`, rc=1 | `r26=466 fixture=fail`, rc=1 | killed both |
| M2 drop dedupe (both-tree copies counted) | d3115ee574a075fc8c14ed3cd7e57008b805eda5 | e511cdcc4c286f32 | G2 FAIL `reports=2 want 1`, rc=1 | `r26=961 fixture=fail regress=differs`, rc=1 | killed both |
| M3 first-section-only carry | 50252d5e7a686138c9a34bc04a7ddd8e7542e0d8 | ca525952e84a7fd4 | G3 FAIL `uncarried=1 want 0`, rc=1 | `fixture=fail` (LANE leg itself unchanged: fp=0 real=2 r26=495), rc=1 | killed both |
| M4 drop fence awareness | 0a196e67dbe7f6ebad9d86a16ad53a954f116f68 | 7961f68bd398f0c8 | rc=0, 10/10 PASS | rc=0, full target line | **SURVIVED both** |
| M5 drop ASCII ellipsis rule | c354ac7cfb8456a97fb4393fa9bffb61f11cd8ce | fc7398a5e73dbbc6 | G4 FAIL (`census/round-18/...seat-audit...json` dangling), rc=1 | `fp=2 shift=fail`, rc=1 | killed both |
| M6 drop en/em-dash range rule | b2a043cd6a840bf50c8a24b496369480130b3222 | fd976048df13d5e7 | G5 FAIL (`tools/x.py:274–277` dangling), rc=1 | `fp=3 shift=fail`, rc=1 | killed both |
| M7 drop `.captured` mapping | db1ff86e3f488a6a648808a06bacdf1f9f749a55 | 2b7efa12f9619bd9 | G6 FAIL (3 dangling), rc=1 | `fp=1 shift=fail` (random `.gitignore` probe), rc=1 | killed both |
| M8 drop printf templates (base `%s` set) | dc3932de438092a69d34bc3f193af8d4ca56be5b | 6e7d781623bc4fa7 | G7 FAIL (2 dangling), rc=1 | `shift=fail` (printf probes), rc=1 | killed both |
| M9 drop letters-only prose rule | a5584d7a152fc6480a629b89970d7083d238ef22 | 7c2d73f50d7eae6c | G8 FAIL (3 dangling), rc=1 | `fp=7 shift=fail`, rc=1 | killed both |
| M10 over-broad prose (digits count as letters) | 784d5ebfd3d052d016eb39f9412602cc6baa5f5c | c916e1eca68e8089 | rc=0, 10/10 PASS | rc=0, full target line | **SURVIVED both** |

Survivor liveness demos (mutant vs pristine gate on a scratch world, same rev):
- Fence demo (rev 45b3f0bb13533e897910d68a3ee81dd53f91a496): lesson with a carry section containing a fenced ` ```## Notes``` ` block and the carried entry only after the fence → mutant `LG-SEAT-UNCARRIED … findings=1` rc=1; pristine `findings=0` rc=0. The mutant is live, not a no-op.
- Digit demo (rev 9c9a4717ffcbb88b3fc81195fbb0e3651f7e61da): lesson cites dangling `` `tools/killpg2` `` (letters+digits, no `.`/`-`/`_`/trailing slash) → pristine `LG-DANGLING-PTR tools/killpg2` rc=1; mutant `findings=0` rc=0. The mutant is live, not a no-op.

Restoration: after the last mutant, `git -C <clone> checkout 2c16d018e40db7c23420a2c3bb546b52957bcc25 -- tools/souji-landing-gate.py` → sha256 back to `577f1387…8b8` (verified). Lane read-only checks: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` = 2c16d018… (unchanged); `status --porcelain` = 0 entries. Scratch dir removed after deliveries copied.

## Findings

1. **Fence-awareness rule is uncovered by both detectors** (harms operability). Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py` `failures_section_lines` fence branch (tip lines 417–427), landed as the A3-disclosed SwarmCritic29-finding-7 patch: "a heading quoted inside a fenced block is text, not a section boundary." The precision fixture contains no fenced block at all (`grep -n '\`\`\`' tests/fixtures/r31-landing-gate-precision.py` → 0 matches; every world's lesson is fence-free), counter v3's SHIFT probes are pointer-only, its LANE leg asserts no uncarried count, and the r19-carry-wrap REGRESS worlds are fence-free. Mutant M4 therefore passes the fixture 10/10 and the full v3 target while demonstrably mis-parsing a fenced heading inside a carry section (false LG-SEAT-UNCARRIED, rc=1 vs pristine rc=0). A future regression of the fence rule would ship green.
2. **The digit boundary of the prose rule is uncovered** (harms operability and coverage). Location: `LETTERS_ONLY_RE` at `tools/souji-landing-gate.py:172` — the landed comment says "a trailing `/` or any `.`, `-`, `_` or digit makes it a path again." Fixture G8 exercises only pure-letters tokens (`tools/tests/census/corpus`, `corpus/authority`, `tools/kill/killpg`), and every v3 SHIFT probe contains a `.`, a `-`, a trailing `/` or a hyphenated component, so allowing digits inside components changes no detector outcome. Mutant M10 passes both detectors while silently skipping a real dangling letters+digits token (`tools/killpg2` demo: pristine rc=1, mutant rc=0). This extends the A3-disclosed blind spot ("cannot tell `corpus/authority` from a real dangling `census/waves`") to letters+digits tokens; no detector would notice such a pointer being dropped.
3. **Counter v3's LANE leg cannot see carry-rule mutants** (harms operability of the counter as an oracle). Its docstring defines the leg purely over pointer findings: "fp = LG-DANGLING-PTR lines whose (round, token-path, source) is not in REAL" — no LG-SEAT-UNCARRIED term exists in the SUMMARY, and at BASE content the scanned lessons carry no `## Seat-reported failures` sections to begin with. M3 (first-section-only) left the LANE leg byte-identical (`fp=0 real=2 cne=0 r26=495`); its only counter kill came through the FIXTURE leg. A counter run with the fixture leg removed would green-light every carry-rule regression.

## Attack log

- M1–M3, M5–M9: reproduced kills, outputs excerpted in the table above; each mutant committed in the scratch clone before both detector runs, restored to pristine bytes between mutants (sha256 verified each time).
- M4: survived; live-behavior proven by the fence demo; uncovered rule = fence awareness in `failures_section_lines`.
- M10: survived; live-behavior proven by the digit demo; uncovered rule = the digit boundary of `LETTERS_ONLY_RE`.
- No mutant was judged against the contract; both survivors are coverage findings on the detectors, not gate defects — the landed gate behaves correctly on the demo worlds (pristine outputs above).

## Deliveries

- `.ufo/waves/round-31/w2/SwarmMutationTester11.md` (this report; path relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`).
- Scratch `/fast/scratch/hyaku/souji-r31/w2-MutateGate/` removed after delivery; nothing else written; no lane counters run concurrently; no signals; no lane git/jj mutation.
