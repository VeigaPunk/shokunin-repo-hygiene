# R42scout04 — mistake-mining sweep for the round-42 lesson (souji)

STATUS: DONE — three sweeps executed read-only at the r42 base `bf618f6c5c09d302994871c94903abbea2deb60d`; three mistake candidates found, none captured by a runnable check at the base; scratch deleted.

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. All evidence pointers are lane-relative `path:line` at the base rev `bf618f6` unless a command names another rev. Read sources first: `census/round-42/preregistration.txt`, `corpus/lessons/round-41.md` (M41-1..4, N1-N19, E1-E2), `corpus/lessons/round-41-verifier-spotcheck.md` §5 (`:80-88`), `corpus/lessons/round-38.md:71-133`, `corpus/lessons/round-39.md:74-101`, `corpus/lessons/round-40.md:60-180`, `census/round-42/r1-counter.py:1-22`. Round-tip selection (per assignment): `git -C <lane> log --format=%H%x09%s | grep 'round-<N>'`, first (newest) hit.

## (a) SCORECARD declared-evidence mismatch count over time

Command run at each tip (workdir was my scratch; `TMPDIR` explicit):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-declared-evidence.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <rev> --file SCORECARD.md --format counts
```

| round tip | rev | assertions | resolved | skipped | mismatches | exit |
|---|---|---|---|---|---|---|
| r22 | `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` | 63 | 63 | 40 | **0** | 0 |
| r23 | `d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7` | 82 | 80 | 69 | **2** | 1 |
| r24 | `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe` | 129 | 116 | 155 | **13** | 1 |
| r25 | `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` | 142 | 127 | 173 | **15** | 1 |
| r30 | `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` | 200 | 179 | 310 | **21** | 1 |
| r35 | `94b5e96ab72b40622449af2dfe7c5b6d73118176` | 318 | 288 | 500 | **30** | 1 |
| r38 | `ed30b7f5b77939c9073348d810730bc4f355708d` | 408 | 356 | 653 | **52** | 1 |
| r41/base | `bf618f6c5c09d302994871c94903abbea2deb60d` | 474 | 404 | 780 | **70** | 1 |

Onset: 0 at the r22 tip, first nonzero (2) already at the r23 tip; monotone growth 2 → 13 → 15 → 21 → 30 → 52 → 70 over 19 rounds. The base row reproduces the frozen r42 C1 predicate exactly (`census/round-42/preregistration.txt`: "assertions=474 resolved=404 skipped=780 mismatches=70") — my runs match the frozen derivation.

When was the instrument last run as a records receipt?

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -l 'souji-declared-evidence' bf618f6... -- census/
```

Output (records-scoped): `census/round-23/records/declared-evidence-after.tsv`, `census/round-24/records/c3-after.tsv`, `census/round-24/records/c3-control-base-runner.tsv`, `census/round-24/records/c3-final.tsv` (plus `census/round-22/attempt2/instrument-digests.txt`). Every later mention is wave prose or a scout note (`census/round-39/waves/w1/W1RevHistory.md`, `census/round-41/waves/w1/R41scout02.md`), never a records receipt. So rounds 25-41 each filed SCORECARD-side work without re-running the r22 instrument at their tip, while the mismatch stock grew to 70. Related rules exist for other surfaces (`corpus/QUALITY.md:185` Q75 re-runs capability rows at the round tip; `:129` Q55 binds counts to receipts; `:257` Q101 scopes derived values) — none re-runs the declared-evidence resolution at each round tip.

## (b) r41 N18 claim vs the closure's finding — counts

```
git -C <lane> grep -n -c 'LG-DANGLING' bf618f6... -- corpus/lessons/round-41.md
→ bf618f6...:corpus/lessons/round-41.md:1        (the single hit is N18 itself, :236)
git -C <lane> grep -n -c 'LG-DANGLING' bf618f6... -- corpus/QUALITY.md
→ no output, exit 1                               (0 hits)
```

The lesson's N18 (`corpus/lessons/round-41.md:236-238`) says the gate raised `LG-DANGLING-PTR` "for the lesson's pointer to an untracked round-40 file and for QUALITY pointers into the ignored `.ufo/waves/round-41/`" and that the fix was rewording/repointing "captured at the same commit". The closure (`corpus/lessons/round-41-verifier-spotcheck.md:85`, `census/round-42/r1-counter.py:5-9`) locates three findings at `corpus/README.md:217` (twice) and `corpus/knowledge/jj-colocation-receipts.md:148`, pointers into the fleet repo's `.ufo/waves/hyaku/jj-w1/reports/` that pre-date round 41. Measured at the base:

```
python3 -B tools/souji-landing-gate.py --root <lane> --rev bf618f6... --round 41        (no --fleet-root)
→ LG-DANGLING-PTR  ../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md   corpus/README.md:217 cites path absent at bf618f6c5c09
→ LG-DANGLING-PTR  ../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md   corpus/README.md:217 cites path absent at bf618f6c5c09
→ LG-DANGLING-PTR  .ufo/waves/hyaku/jj-w1/reports/                     corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at bf618f6c5c09
→ SUMMARY findings=3 checked_reg=107 ... exit 1
python3 -B tools/souji-landing-gate.py --root <lane> --rev bf618f6... --round 41 --fleet-root /home/vgpnk/Projects/shokunin
→ SUMMARY findings=0 ... exit 0
```

Count verdict: 1 mention of `LG-DANGLING` in the lesson (the N18 line itself), 0 in QUALITY.md, 3 live findings at the base — and 0 of the 3 sit on the surfaces N18 names. N18's account describes a different run (mode or surface) than the measurement the closure and the frozen R1 rely on: without `--fleet-root` the three r17-era fleet pointers persist; with it they vanish. The lesson records the finding as resolved-by-rewording; the gate was never re-run in the recorded mode with a committed receipt.

## (c) Own sweep — receipts naming scratch paths, repeated r38 → r41

```
for N in 38 39 40 41: git -C <lane> grep -l -E '/var/tmp/|/fast/scratch/' bf618f6... -- census/round-$N/records | wc -l
```

| round | records files naming out-of-lane scratch paths |
|---|---|
| 38 | 12 |
| 39 | 0 |
| 40 | 6 |
| 41 | 4 |

Samples at the base: `census/round-38/records/c2-after.txt:16` (record under `/fast/scratch/hyaku/souji-r38/after/...`), `census/round-40/records/c1-after-d.txt:2` (`--scratch /fast/scratch/hyaku/souji-r40/l1/c1`), `census/round-41/records/c2-after.txt:2`, `c2-after-hardened.txt:2`, `c3-after.txt:2`, `r1-after.txt:2` (all `--scratch /fast/scratch/hyaku/souji-r41/L1`). The class was named and routed forward by r41 ("receipts naming scratch paths (r38-r40)", `corpus/lessons/round-41.md` routed-forward list) — and r41's own records repeat it (4 files) in the same round that routed it, after r39 had shown a clean state is reachable (0). No committed check rejects an out-of-lane absolute path in committed receipt bytes; the gate's SUMMARY scopes (`checked_reg/changed/pins/measured/markers/reports`) do not include receipt-path hygiene.

## Mistake candidates (none captured by a runnable check at the base)

**MC-1 — the calibration instrument was retired from use while its surface drifted (class: stale-instrument / measurement-omission).**
Evidence: sweep (a) table (0 at r22 → 70 at the base; first nonzero at the r23 tip `d3666c3`); last records use `census/round-24/records/c3-final.tsv`; no `census/round-2{5..41}/records` receipt names `souji-declared-evidence` (git grep output above). The frozen instrument exists the whole time and already exits 1 at every sampled tip from r23 on.
Captured-by: none — Q55/Q75/Q101 govern receipts, capability rows and derived-value scope (`corpus/QUALITY.md:129,:185,:257`); no rule re-runs the declared-evidence resolution at each round tip, and no gate finding reads it.
Fix (able to fail): a per-round tip receipt + gate arm `LG-DECLARED-DRIFT`: run `tools/souji-declared-evidence.py --file SCORECARD.md --format counts` at the round tip; `mismatches>0` is a finding. It fails today at every tip from `d3666c3` on (r23: mismatches=2, exit 1), and at the base reads 70. Overlap note: r42's frozen C1 repairs the accumulated stock at the base; this candidate adds the recurrence rule that would have stopped the growth at 2.

**MC-2 — a named limit recorded its finding as resolved without re-running the instrument in the recorded mode (class: resolution-claim-unverified / mode-attribution).**
Evidence: `corpus/lessons/round-41.md:236-238` (N18: findings on "the lesson's pointer to an untracked round-40 file and ... QUALITY pointers", resolved by rewording) vs `corpus/lessons/round-41-verifier-spotcheck.md:85` + gate output at the base: 3 findings on different surfaces (`corpus/README.md:217`, `corpus/knowledge/jj-colocation-receipts.md:148`), findings=3 without `--fleet-root` and findings=0 with it. Counts: lesson `LG-DANGLING` mentions 1 (N18 itself), QUALITY.md 0, live findings 3, of which 0 match N18's named surfaces.
Captured-by: none — the resolution was recorded without a committed re-run receipt in the measuring mode; no check compares a lesson's "fixed" claim against a gate re-run (the landing gate's carry/status checks read `STATUS:` lines only).
Fix (able to fail): the R1 shape — at each round tip run the gate in the measuring mode and require `findings=0` or one append-only `corpus/pointer-exemptions.tsv` row per finding; the frozen `census/round-42/r1-counter.py` demonstrates the catch (target `findings=0 deleted=0 rows_added=3 stale=0`; at the base it reads findings=3 → red until the three rows land). Overlap note: this is the r42 R1 ground seen from the mistake-mining side; the mined delta is N18's mis-attribution, which the R1 counter's docstring (`:5-9`) records but no lesson Mistakes entry yet states.

**MC-3 — committed receipts cite scratch paths outside the lane that are deleted after the round (class: evidence-pointer-outside-lane; repeated r38, r40, r41 after a clean r39).**
Evidence: sweep (c) table (12/0/6/4 files); samples `census/round-38/records/c2-after.txt:16`, `census/round-40/records/c1-after-d.txt:2`, `census/round-41/records/c2-after.txt:2`. A receipt whose command header names `/fast/scratch/hyaku/souji-r41/L1` cannot be re-derived once that directory is removed — the receipt's own provenance ground is outside the lane and ephemeral.
Captured-by: none — routed forward in prose only (`corpus/lessons/round-41.md` routed-forward list); no gate finding or counter inspects receipt bytes for out-of-lane absolute paths.
Fix (able to fail): a counter/gate rule over committed `census/round-N/**` bytes: any command-header or receipt line carrying an absolute path outside the lane root is a finding (or must carry a `scratch-deleted` marker). Red at the base: 22 files across r38/r40/r41. Nuance a frozen rule must decide: r38's hits are tool stdout quotes inside FAIL-case lines (e.g. `record=/fast/scratch/...`), so a byte-level regex over-flags unless scoped to `# command:`/`$ ` receipt headers.

## Ranking (how cleanly a frozen counter could have caught them)

1. **MC-1** — cleanest: the frozen instrument already prints the verdict (`mismatches=`); a counter is run+read, deterministic, red from r23 onward, largest surface (70 tokens).
2. **MC-2** — deterministic in a fixed gate mode and already proven catchable by the frozen R1 counter (findings=3 at the base); one notch below MC-1 only because binding the lesson's prose claim to the receipt needs the R1 append-only discipline.
3. **MC-3** — trivially detectable (byte regex, 22 files red at the base) but the normative rule is new and needs a header-scoped definition to avoid flagging tool stdout quotes; the check is easy, the rule is the judgment.

## Verdict

All three required sweeps ran; outputs above are verbatim-quoted from my runs at the stated revisions. The preregistration's "Mistake to mine" sentence is confirmed by measurement: the 70 unresolvable tokens accumulated from a first nonzero at the r23 tip with no instrument re-run at any later tip, and the N18/closure disagreement is a real mode disagreement (3 vs 0 findings, different files), not a wording quibble. Three mined mistakes are filed as MC-1..MC-3 with ranked fixes. No frozen file was read-modified; no candidate files were written; no tooling was installed (pacman paused host-wide; none needed). Scratch `/fast/scratch/hyaku/souji-r42/R42scout04` left no files (`find` printed nothing) and is removed before yield.

| rank | class | evidence pointer (at base bf618f6) | captured-by | fix |
|---|---|---|---|---|
| 1 | stale-instrument / measurement-omission (declared-evidence drift 0→70, r23→r41) | sweep (a) table; `census/round-24/records/c3-final.tsv` (last records use); `tools/souji-declared-evidence.py:1`; base counts 474/404/780/70 | none (Q55/Q75/Q101 cover other surfaces; no per-round re-run rule) | `LG-DECLARED-DRIFT`: run the instrument at each round tip; mismatches>0 = finding (red at r23 `d3666c3` mismatches=2; red at base mismatches=70) |
| 2 | resolution-claim-unverified / mode-attribution (N18 vs closure) | `corpus/lessons/round-41.md:236-238`; `corpus/lessons/round-41-verifier-spotcheck.md:85`; gate at base findings=3 (`corpus/README.md:217` ×2, `corpus/knowledge/jj-colocation-receipts.md:148`) vs findings=0 with `--fleet-root`; `census/round-42/r1-counter.py:5-9` | none (no committed re-run receipt in the measuring mode; R1 lands only in r42) | R1 shape: gate at tip in measuring mode; findings=0 or one append-only `corpus/pointer-exemptions.tsv` row per finding (red at base: 3 findings, 0 exemption rows) |
| 3 | evidence-pointer-outside-lane (receipts naming scratch paths; repeats r38/r40/r41 after clean r39) | `census/round-38/records/c2-after.txt:16`; `census/round-40/records/c1-after-d.txt:2`; `census/round-41/records/c2-after.txt:2`; sweep (c) counts 12/0/6/4 | none (routed forward in prose only; no check reads receipt bytes for out-of-lane paths) | counter/gate rule: receipt command-header lines carrying absolute out-of-lane paths = finding (red at base: 22 files across r38/r40/r41) |
