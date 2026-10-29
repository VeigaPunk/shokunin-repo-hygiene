# R42w2scout01 — history sweep: declared-evidence mismatch count of SCORECARD.md at every round tip r22–r41

STATUS: DONE — 22 instrument runs over 20 round tips plus 2 context revisions; onset and every material jump attributed to a named commit; scratch deleted.

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, landed tip `3105a63b23481fccf7df58e74d14a6681e0ea0c8` (working tree equal, no sibling seen writing). All numbers below are verbatim outputs of my runs. Instrument: the tip's committed blob `tools/souji-declared-evidence.py`, sha256 `a332491607129195f59d289b431cc29fb4c8dc21e10859d552700697a3b09831` before and after the sweep (unchanged mid-run). Read-only throughout: no lane file written except this report and `R42w2scout01/receipts/` (both under my seat directory).

## Tip-selection rule (stated, and verified under both enumerations)

Rule A: the newest commit whose subject begins `round-<N>` (`git log --format='%H %s'` scanned top-down, anchored `^<hash> round-<N>[: ]`).
Rule B: the parent of the chronologically first (oldest) `round-<N+1>` commit.
Both computed programmatically over the full 409-line log (`R42w2scout01/receipts/log-all.txt`): **SAME for every N in 22..41** — the per-round subject blocks are contiguous and each round ends in its "round-N verifier spot-check" commit (which is exactly how r42's own base `bf618f6…` is described in the preregistration). A naive unanchored `grep 'round-<N>'` is defective here: e.g. `d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7` ("round-24: inherited late round-23 seat updates …") is a round-24 commit that matches `round-23`; wave-1's R42scout04 cited it as the "r23 tip".

## Command (run at each revision; `TMPDIR` pointed into my scratch per run)

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-declared-evidence.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <rev> --file SCORECARD.md --format counts
```

## Table — round | rev | counts (assertions / resolved / skipped / mismatches, exit)

| round | rev (tip) | counts | exit |
|---|---|---|---|
| r22 | `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` | assertions=63 resolved=63 skipped=40 mismatches=0 | 0 |
| r23 | `a65fac98964b445758e94c805728c9a19d302ff8` | assertions=82 resolved=80 skipped=69 **mismatches=2** | 1 |
| r24 | `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe` | assertions=129 resolved=116 skipped=155 mismatches=13 | 1 |
| r25 | `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` | assertions=142 resolved=127 skipped=173 mismatches=15 | 1 |
| r26 | `270652720d12572dbc6a464ea938fbd59ad88275` | assertions=148 resolved=133 skipped=186 mismatches=15 | 1 |
| r27 | `3a2a80d0d18940a5e352ebc526da22a57dad83c4` | assertions=155 resolved=139 skipped=201 mismatches=16 | 1 |
| r28 | `691dd29211c53d0ef94fa072394cb9c8a69fe92e` | assertions=164 resolved=145 skipped=223 mismatches=19 | 1 |
| r29 | `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` | assertions=175 resolved=154 skipped=278 mismatches=21 | 1 |
| r30 | `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` | assertions=200 resolved=179 skipped=310 mismatches=21 | 1 |
| r31 | `85b61a151923986e7e6b48f7084b9122561b5f3d` | assertions=252 resolved=229 skipped=401 mismatches=23 | 1 |
| r32 | `6017a482e7068d5afb7617640198fbb0fe743357` | assertions=291 resolved=265 skipped=444 mismatches=26 | 1 |
| r33 | `9c76c7222a8abff027af42e37f0d160d52526bba` | assertions=312 resolved=283 skipped=474 mismatches=29 | 1 |
| r34 | `2cdea6845caae072ead9ffaf0e14395cc1760d42` | assertions=317 resolved=287 skipped=495 mismatches=30 | 1 |
| r35 | `94b5e96ab72b40622449af2dfe7c5b6d73118176` | assertions=318 resolved=288 skipped=500 mismatches=30 | 1 |
| r36 | `0d974ffcb7dfb70617947531cab2d7e96cd8f9fd` | assertions=336 resolved=306 skipped=545 mismatches=30 | 1 |
| r37 | `ca4369a9296011644636711a624da6a8074e8e2a` | assertions=365 resolved=335 skipped=574 mismatches=30 | 1 |
| r38 | `ed30b7f5b77939c9073348d810730bc4f355708d` | assertions=408 resolved=356 skipped=653 mismatches=52 | 1 |
| r39 | `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e` | assertions=438 resolved=379 skipped=705 mismatches=59 | 1 |
| r40 | `7eebc183f2685d1ea9b004b4de22c09a8a4035a7` | assertions=466 resolved=400 skipped=756 mismatches=66 | 1 |
| r41 | `bf618f6c5c09d302994871c94903abbea2deb60d` | assertions=474 resolved=404 skipped=780 mismatches=70 | 1 |
| r42 (context) | `3105a63b23481fccf7df58e74d14a6681e0ea0c8` | assertions=490 resolved=420 skipped=810 mismatches=70 | 1 |

Raw: `R42w2scout01/receipts/sweep.tsv`. The r41 row reproduces the frozen C1 predicate exactly (`assertions=474 resolved=404 skipped=780 mismatches=70`, `census/round-42/preregistration.txt`), and the r22 row reproduces the lesson's recorded receipt (`assertions=63 resolved=63 mismatches=0`) — no instrument-version skew at either anchor.

## First round with mismatches > 0, and the onset commit

r23 is the first nonzero tip: 0 at the r22 tip → 2 at the r23 tip `a65fac98…`. Attribution scan (tool run at every SCORECARD-touching commit of the interval, chronological):

- `476525026cdb179f2d49441e1cb6c6f7316f3124` "round-23: record-agreement and blob-bound-receipt instruments, F2 read-side entries, D1-D7 repairs" → **mismatches=3** (82/79/67): introduced all three (SCORECARD was clean at its parent-side state).
- `1dd8b1e30a971e662480b49bedf1000667fbddea` "round-23: wave-2 falsification fixes, final instruments and records" → repaired one (3→2); r23 tip stays 2.
- The two surviving r23 tokens (`--format tsv` at `a65fac98…`): SCORECARD line 14 token `65817d0d` (class B, rev-unresolved — the truncated sha256 prefix of a `tools/souji-declared-evidence.py` blob; the same token r42's C1 corrects at line 14 today) and line 23 `git-repo-structure-readonly.md` (class A, path-absent). So the stock's first deposit is still on the books at the base.

## Biggest jumps and their causing commits (tool-scan over each interval's SCORECARD-touching commits; `git log <lo>..<hi> -- SCORECARD.md` enumerates them)

| jump | interval | causing commit(s) | step |
|---|---|---|---|
| **+11** (2→13) | r23→r24 | `315422ba9970f03c27f8a9184446783b7fcdf0a7` "round-24: final — post-wave-2 repairs …" — the only SCORECARD commit in the interval; it appended the Round 24 measurements block including a fenced ```markdown draft whose cells carry truncated digests (`e13d0c83…`, `09bb8e0d…`) and many new path assertions | single step 2→13 at that commit |
| **+22** (30→52) | r37→r38 | distributed over five receipt commits: `7b542e22dca0098c5c743b586ce0e0fda67a856b` **+8** (30→38, Round 38 measurements block), `f10a3a8e5b3692bbc7c75613cfe4d6820b8667b9` +5, `9b9e2f807597696b9eb91d853e8d448ced0d30f7` +3, `be668863f4a93fd70f7194037402c9047e6a5e6b` +3, `8093c70a8e7f4105945b0cfaf53bab409b12e6f5` +3 (`cb80d0d0…` +0). Largest single contributor: `7b542e22…` | no single cause; five receipts |
| +7 (52→59) | r38→r39 | `544104503a3ad70687ba399fcafd12bd30648169` "round-39: measurements — SCORECARD rows/capabilities/planned …" (the three earlier r39 commits read 52 each) | single step |
| +7 (59→66) | r39→r40 | largest step `994de3b447e9a7bea2abfbd80c4736f6215d3e47` +8 (59→67); `42e18ed7…` +3 (67→70); **`4280fedba7ae3297182ae023422dc03c10bd356b` −4 (70→66)** — the only count decrease in the whole history, an intra-round repair | net +7 |
| +4 (66→70) | r40→r41 | `0c9581a44a2eaa7350b4699e64dcdfbe07fec0d5` "round-41: LOG, SCORECARD, README, final census and tip re-measurement" (only SCORECARD commit; reads 474/404/780/70) | single step |

Between r25 and r37 the stock grows slowly (+0 to +3 per round, 15→30) with no round re-running the instrument (below).

## Does M42-1's sentence hold?

**Holds.** M42-1 (`corpus/lessons/round-42.md`): r22 attempt 2 recorded `assertions=63 resolved=63 mismatches=0` — my run at the r22 tip reproduces it exactly; the sweep puts the first nonzero count at the r23 tip — confirmed (2 at `a65fac98…`, 0 at `1208bfb…`); "the count rising after it with no round re-running the instrument" — confirmed at tip granularity: strictly rising r23→r41 except one intra-r40 −4 repair, and no round filed a declared-evidence-at-tip calibration receipt after r24 (evidence below).

Three wave-1 evidence defects found while confirming it (the lesson's sentence survives all three; they attack the w1 report's supporting lines, not the round claim):

1. **R42scout04's r23 rev is mislabeled.** `census/round-42/waves/w1/R42scout04.md` sweep (a) lists r23 tip = `d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7`, which is a round-24-tagged commit ("round-24: inherited late round-23 seat updates …"); its stated rule ("`grep 'round-<N>'`, first (newest) hit") matches `round-23` inside that round-24 subject. The true r23 tip under both clean rules is `a65fac98…`. Counts coincide (both 2) only because `d3666c3…` does not touch SCORECARD (`git log a65fac98..a6d2d15 -- SCORECARD.md` names only `315422ba…`) — verified by running the instrument at `a65fac98…` (82/80/69/2) and `d3666c3…` (82/80/69/2).
2. **R42scout04's "no records receipt names the instrument" grep sentence is false in the letter.** MC-1 states "no `census/round-2{5..41}/records` receipt names `souji-declared-evidence`". At `bf618f6…`: `git grep -n souji-declared-evidence bf618f6… -- census/round-31/records census/round-32/records` returns 4 hits (`c1-after-a4.txt:31`, `c1-after-v1.txt:31`, `c1-before.txt:31` — r31 C1 run-binding lines executing `python3 tools/souji-declared-evidence.py --selftest rc=0 observed=selftest=8/8`; `round-32/records/preregistration.txt:15` — a C2 counter arm described as reading SCORECARD "through souji-declared-evidence at the fixed base"). None of these is a SCORECARD-at-tip audit, so the lesson's "re-running the instrument" sentence stands under its natural reading; the w1 supporting sentence does not.
3. **Even r23's own receipt did not measure the r23 tip.** `census/round-23/records/declared-evidence-after.tsv:5` reads `cmd=python3 tools/souji-declared-evidence.py --rev 9301d98c1c689c79741f0f1ba1f171138d20af07 --file SCORECARD.md` — `9301d98c…` is the r22 final tip. The instrument has never been filed against any r23+ tip before this sweep; the only later r24 mentions are receipt-run `verify=ok` re-checks of that r22-tip receipt (`census/round-24/records/c3-{after,control-base-runner,final}.tsv:13`, `tool_sha256=65817d0d…` — itself the truncated-digest token of finding M42-1/C1 line 14).

Context note, not a defect: the instrument still reads `mismatches=70` at the r42 tip (`3105a63…`, assertions 490 / resolved 420 / skipped 810). That is C1 working as designed — base lines stay byte-identical, the 70 are accounted by `census/round-42/c1-register.tsv` + five CORRECTION-DE lines, and the counter's `new_mismatches` leg (not the instrument's total) is the landed gate. The instrument's total will read 70 until a future round retires the tokens.

## Verdict

The lesson's M42-1 history claim is TRUE as stated: first nonzero at the r23 tip (`a65fac98…`, mismatches=2; onset deposit `47652502…`, +3, one repaired in-round), monotone rise to 70 at the r41 base, no round re-running the instrument at its tip after r24. Biggest jumps: +11 r23→r24 (`315422ba…`), +22 r37→r38 (five receipt commits, largest `7b542e22…` +8), +7 r38→r39 (`544104503…`), +7 r39→r40 (largest `994de3b4…`; one −4 intra-round repair `4280fedb…`), +4 r40→r41 (`0c9581a4…`). Two cosmetic falsifications in wave-1's supporting evidence (r23 rev mislabel; "no records receipt names the tool" grep sentence), neither of which breaks the lesson's sentence.

## Receipts (committed under my seat directory)

- `R42w2scout01/receipts/sweep.tsv` — 21 rows: round, rev, exit, verbatim counts line (r22–r41 tips + r42 tip; plus r23 true-tip re-run recorded in this report body).
- `R42w2scout01/receipts/log-all.txt` — full `git log --format='%H %s'` (409 commits) used for both tip rules.
- `R42w2scout01/receipts/r23-tip.tsv` — `--format tsv` at `a65fac98…` (the two mismatch rows with classes).
- `R42w2scout01/receipts/bisect-*.txt` — per-commit counts for the onset, r23→r24, r37→r38, r38→r39, r39→r40, r40→r41 intervals.
