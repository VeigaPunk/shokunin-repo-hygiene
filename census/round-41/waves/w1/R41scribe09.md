# R41scribe09 — scribe: mine one mistake (dead-seat error text)

Seat: R41scribe09 (role scribe, round 41, wave w1). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Frozen revision: `bffcc0f660ff36eb8add3f61582748a7af019a5b`. No commit, push, or mutating git/jj run. No tool installed or upgraded. Scratch `/fast/scratch/hyaku/souji-r41/R41scribe09` removed after the receipt was copied to `.ufo/waves/round-41/w1/R41scribe09/landing-r40.txt`.

## Mistake mined

Candidate: `.ufo/waves/round-41/w1/R41scribe09/mistake-deadtext.md`. It names the unevidenced dead-seat provider error text in `LOG.md:1909`: committed seat results contain no such text. Class: calibration / record-provenance. Fix: the I4 `CORRECTION` line, scored below.

## Commands run and observed output

1. Ground check. The spec's `grep -c` over `census/round-40/waves` at the frozen commit, run as a git grep (zero matches print nothing):

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -c 'flagged as potentially' bffcc0f660ff36eb8add3f61582748a7af019a5b -- census/round-40/waves; echo "exit=$?"
exit=1
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -c 'flagged as potentially' bffcc0f660ff36eb8add3f61582748a7af019a5b -- census/round-40/waves | wc -l
0
```

   Working-tree equivalent: `grep -rc 'flagged as potentially' .../census/round-40/waves | awk -F: '{s+=$NF} END {print "sum="s}'` → `sum=0`.

2. Whole-lane search at the frozen commit:

```
$ git -C .../souji-shokunin grep -n 'flagged as potentially' bffcc0f660ff36eb8add3f61582748a7af019a5b
bffcc0f...:LOG.md:1909:- **Swarm:** ... 2 dead seats (R40w2reviewer01/04, provider error `Codex error event: Invalid prompt: your prompt was flagged as potentially violating our usage policy`) ...
exit=0
```

   The only lane occurrence is the filed claim itself.

3. Other provider-error strings at the frozen commit (`Codex error`, `usage policy`, `Invalid prompt`):

```
.ufo/waves/round-21/provider-error-excerpts.json:6   ... Codex error event: Codex is at capacity ... (code=turn_rate_limit_exceeded)
census/round-20/recovery-seat-outcomes.json:31,38,45,52   same "at capacity" message
corpus/lessons/round-22.md:187   same "at capacity" message
LOG.md:1909   the filed text
```

   None of the committed "at capacity" lines is the filed text.

4. The dead seats' committed results. Parsed `census/round-40/waves/w2-results.json` (64 results):

```
R40w2reviewer01: output len=2310, has 'flagged as potentially': False, 'Codex error': False, 'usage policy': False; ends mid-reasoning, no verdict
R40w2reviewer04: output len=6852, has 'flagged as potentially': False, 'Codex error': False, 'usage policy': False; a <think> block, no verdict
total results: 64
results with 'flagged as potentially' anywhere in JSON text: 0
```

   Report files: `ls census/round-40/waves/w2 | grep -E 'R40w2reviewer0[14]'` → no output (exit 1). No report file exists for either seat.

5. Run record: `wc -c .ufo/waves/round-40/w2-run.err` → `0`; `git cat-file -s bffcc0f...:.ufo/waves/round-40/w2-run.err` → `fatal: path ... exists on disk, but not in 'bffcc0f...'` (untracked, empty).

6. QUALITY sweep (`corpus/QUALITY.md`):
   - Line 8 (fleet floor quoted): "a count carries its command, a negative its sweep, a quote its location, an index row is a claim". This is the captured-by rule for a quote without a located source.
   - Q25(c) and Q68 carry seat failures into `## Seat-reported failures`. `grep -n 'Seat-reported' corpus/lessons/round-40.md corpus/lessons/round-39*.md` → only `corpus/lessons/round-39.md:138`. `grep -n '^## ' corpus/lessons/round-40.md` → lines 7 `## Gate`, 60 `## Mistakes`, 181 `## Frontier`. Round 40 has no seat-failure section.
   - Q55 does not apply (the filed text is a cause, not a count).

7. Landing gate, read-only, at the frozen revision. Receipt copied to `.ufo/waves/round-41/w1/R41scribe09/landing-r40.txt`:

```
$ python3 -B tools/souji-landing-gate.py --root <lane> --rev bffcc0f660ff36eb8add3f61582748a7af019a5b --round 40
rc=1
LG-DANGLING-PTR ../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md  corpus/README.md:217 ...
LG-DANGLING-PTR ../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md  corpus/README.md:217 ...
LG-DANGLING-PTR .ufo/waves/hyaku/jj-w1/reports/  corpus/knowledge/jj-colocation-receipts.md:148 ...
SUMMARY findings=3 checked_reg=100 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=0 status_lines=0 carry_heading=0 checked_reports=117
```

   No finding concerns the dead seats. `status_lines=0` and `carry_heading=0` mean the seat-carry check had nothing to read for round 40. The three `LG-DANGLING-PTR` findings are outside this item and were not investigated. The gate's `--fleet-root` was not supplied.

8. Frozen C1 counter, scored through the supported path (scratch clone, candidate committed in the clone only):

```
$ export TMPDIR=/fast/scratch/hyaku/souji-r41/R41scribe09
$ grep -c '^CORRECTION' .ufo/waves/round-41/w1/R41scribe09/mistake-deadtext.md   → 1
$ bash census/round-41/score-candidate.sh c1 "$TMPDIR" corpus/lessons/round-41.md=.ufo/waves/round-41/w1/R41scribe09/mistake-deadtext.md
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=0 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=0 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=1 uncorrected=2 junk=0 rewritten=0 sourced=0
rc=1
```

   Verbatim SUMMARY: `SUMMARY items=3 mismatched=3 corrected=1 uncorrected=2 junk=0 rewritten=0 sourced=0` (rc=1). The rc is expected: I1 and I3 are not this seat's items. For I4 alone, the line validates: `corrections=1 junk=0`.

## Candidate fix (I4 CORRECTION line)

```
CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-
```

## Verdict

- **Calibration of I4: confirmed by committed bytes.** The filed error text has zero committed occurrences at `bffcc0f` outside its own `LOG.md:1909` claim. The frozen counter derives `occurrences=0` and accepts the candidate line with `corrected=1 junk=0`.
- **Cause of the dead seats: not established.** Committed bytes show no provider failure for R40w2reviewer01/04 (their outputs are unfinished, with no verdict). The filed attribution may be true from an uncommitted transcript, which is not a receipt. [INFERENCE]
- **Routed to L1 (not claimed):** round 40 has no `## Seat-reported failures` section. The gate's seat-carry check reads only `STATUS:` lines, so it cannot see JSON-verdict or result-only seats.
- **Not landed.** The L1 must land the lesson through `jj-lane.sh`. Nothing in the lane was edited.

## Limits

- The round-41 lesson file does not exist at `bffcc0f`; the CORRECTION line is a candidate, not a landed line.
- The landing gate's three `LG-DANGLING-PTR` findings were not investigated.
- The sweep was limited to the QUALITY criteria named above.
