# RevD5 — routed defect D5: independent verification and repair judgment

Lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`. Contract read first:
`.ufo/waves/round-23/preregistration.txt` (C1 K2). Source of the claim:
`corpus/lessons/round-22-verifier-spotcheck.md` §6 D5. Read-only seat: no lane file written
except this report; scratch under `/var/tmp/souji-r23-RevD5/`, removed. No tool installed. I did
not execute the lane's instruments (PROTOCOL gate standard); where a statement depends on
`tools/souji-record-agreement.py` behaviour I re-derived its predicate from its source in my own
oracle over the same bytes (§E2), and label anything beyond that `[INFERENCE]`.

## Status

STATUS: PASS — D5 reproduces at the lane base (3 stale scalars in the `Round22 attempt2` LOG entry,
0 corrections) and is open, not overstated; the round's planned repair closes it only after two
wording fixes, because the repair instruction names the superseded tuple as the *correct* one and
the K2 predicate cannot tell a true correction from a false one.

## Evidence

**E1 — one command, defect reproduced (run at `1208bfb`).**

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin; git rev-parse --short HEAD; \
echo '== LOG.md stale scalars =='; grep -nE 'assertions=56 resolved=53|1 present|1 refused' LOG.md; \
echo '== LOG.md "superseded by" count =='; grep -c 'superseded by' LOG.md; \
echo '== last commit touching LOG.md =='; git log -1 --format='%h %ci' -- LOG.md; \
echo '== pinned receipt truth =='; tail -1 census/round-22/attempt2/declared-evidence-before-final.tsv; \
awk -F'\t' 'NF>1{c[$2]++}END{for(k in c)printf "slice %s=%d\n",k,c[k]}' census/round-22/attempt2/slice-verdicts.tsv; \
echo '== earlier receipt (the one LOG cites) =='; tail -1 census/round-22/attempt2/declared-evidence-before.tsv
```

```
1208bfb
== LOG.md stale scalars ==
1484:`--rev 4edb25d --file SCORECARD.md` -> assertions=56 resolved=53
1509:corrected quotes, 1 present, 1 refused (S123 wrong-source
== LOG.md "superseded by" count ==
0
== last commit touching LOG.md ==
70af563 2026-10-25 03:43:30 -0300
== pinned receipt truth ==
assertions=55 resolved=52 skipped=33 mismatches=3

slice accepted=5
slice present=2
slice unverifiable=1
== earlier receipt (the one LOG cites) ==
assertions=56 resolved=53 skipped=33 mismatches=3
```

`slice refused=0` is absent from the tally because no row carries that class; `tally_of` in the
instrument supplies `0` via `.get(cls, 0)`.

**E2 — K2's predicate re-derived independently (transcribed from
`tools/souji-record-agreement.py:45-49,108-130,147-213`, applied by my own script to `LOG.md`,
`census/round-22/attempt2/declared-evidence-before-final.tsv`,
`census/round-22/attempt2/slice-verdicts.tsv`).**

```
want_counts= assertions=55 resolved=52 skipped=33 mismatches=3  want_tally= {'accepted': 5, 'present': 2, 'unverifiable': 1, 'refused': 0}  section_lines= 1471 - 1522
STALE@1478 'assertions=56 resolved=53 skipped=33 mismatches=3' later_correction=False
STALE@1495 '1 present' later_correction=False
STALE@1495 '1 refused' later_correction=False
stale_occurrences= 3
```

The predicate is non-vacuous for D5: it finds exactly the three strings the spot-check names.
Paragraph anchors: the 4-tuple paragraph starts `LOG.md:1478` (literal on 1484-1485); the tally
paragraph starts `LOG.md:1495` (literal on 1508-1510).

**E3 — provenance of the supersession (why the numbers are stale, not wrong when filed).**

- `git log -1 -- LOG.md` → `70af563` 03:43:30. At `70af563`: `declared-evidence-before.tsv` tally =
  `rows=56 resolved=53 mismatch=3`; `slice-verdicts.tsv` tally = 5 accepted / 1 present / 1 refused
  / 1 unverifiable. The LOG entry was **accurate as filed**.
- `dd8a6b7` 04:07:55 ("pinned-instrument before receipt, digest file cleanup, verdicts id-space
  header") is the first revision carrying
  `census/round-22/attempt2/declared-evidence-before-final.tsv` (`assertions=55 resolved=52
  skipped=33 mismatches=3`, line 56), and it flipped `S123 refused → accepted` and
  `S138 accepted → present` (`git diff 70af563 HEAD -- …/slice-verdicts.tsv`).
- `70af563` is an ancestor of `dd8a6b7`, which is an ancestor of the base. So the round itself
  superseded its own LOG entry and left no later LOG line: `grep -c 'superseded by' LOG.md` = 0 and
  `70af563` is the newest commit touching `LOG.md`.

**E4 — the lane already holds the truth in another record** —
`corpus/lessons/round-22.md:314`: "the pinned instrument scores `55/52/33/3` at the same revision —
both kept, neither overwritten".

**E5 — the planned repair, from `.ufo/waves/round-23/w1-spec.json` item `ScribeLog`, block (1):**
"it names the superseded tuple (`assertions=56 resolved=53`), the correct tuple the committed
receipt `census/round-22/attempt2/declared-evidence-before.tsv` holds". That receipt's counts line
(`…-before.tsv:57`) is `assertions=56 resolved=53 skipped=33 mismatches=3` — the superseded tuple.

**E6 — K2 probes on the same predicate (simulated on `/var/tmp` copies; the lane's `LOG.md` was
never written).**

| probe | appended lines | K2 result |
|---|---|---|
| correction drafted per `ScribeLog` (calls 56/53 "correct") | +10 | all 3 `later_correction=True` → K2 green |
| correction naming 55/52 as replacement | +10 | identical → K2 green |
| marker inserted **inline** into the filed paragraph, nothing appended | 0 | `later_correction=True` → K2 green |
| filed 4-tuple **deleted**, tally corrected later | -1 | `stale_occurrences=2`, all corrected → K2 green |

## Findings

1. **D5 is real and open at the lane base** (`LOG.md:1484-1485`, `LOG.md:1508-1510`; zero
   `superseded by` lines; newest `LOG.md` commit `70af563` predates the superseding `dd8a6b7`).
   Not overstated: the entry's numbers genuinely disagree with the receipts the round ended on.
   Understated in two respects the spot-check omits: (a) the LOG was accurate when filed, so the
   defect is the missing append-only correction, not fabrication; (b) the slice half is a *two-class*
   error — `S123 refused → accepted` **and** `S138 accepted → present` — so the correction must not
   say only "S123 was accepted".

2. **The repair instruction targets the wrong receipt.** `ScribeLog` block (1) names
   `declared-evidence-before.tsv` as the source of the correct tuple; that file holds 56/53/33/3 —
   the value the same sentence calls superseded. Drafted literally, the LOG correction asserts
   "`assertions=56 resolved=53 skipped=33 mismatches=3` … superseded by `assertions=56 resolved=53
   skipped=33 mismatches=3`", which contradicts `corpus/lessons/round-22.md:314` and the frozen
   K2 receipt. The correct tuple is `assertions=55 resolved=52 skipped=33 mismatches=3`
   (`declared-evidence-before-final.tsv:56`, landed `dd8a6b7`, pinned instrument
   `65817d0d…` in `census/round-22/attempt2/instrument-digests.txt`).

3. **K2 cannot distinguish a true correction from a false one** (E6 rows 1-2 are identical). It
   requires only that the stale string and the literal `superseded by` co-occur in a later 6-line
   window; it never checks that the named replacement equals the receipt. A self-contradictory
   correction therefore yields `M=0` for K2. Finding 2 would not be caught by the instrument.

4. **K2 does not enforce "LATER LOG.md line"** as the prereg words it: the search window starts at
   the stale paragraph's own first line (`range(start_line, …)`,
   `tools/souji-record-agreement.py:203-207`), so an in-place edit of the filed paragraph that adds
   `superseded by` satisfies K2 with zero appended lines (E6 row 3) — filed-bytes tampering the
   counter would bless.

5. **K2's append-only guard is aggregate, not per-occurrence.** The prereg promises "the filed
   historical occurrence must still exist (its deletion is itself a mismatch)". In code the guard
   is `if found == 0` over the whole section, so deleting the filed 4-tuple while the tally
   paragraph survives is invisible (E6 row 4: `stale_occurrences` drops 3 → 2, no mismatch class
   raised). Only deleting *every* scalar trips `filed-occurrence-missing`.

6. **Prereg prose vs instrument constant disagree on K2** (see Attack A1). Resolution I recommend
   as the reading, not as an edit: the code governs — the prereg itself says "the tool is the frozen
   contract", the constant `K2_RECEIPT = "…/declared-evidence-before-final.tsv"` is the only choice
   that detects D5, and the docstring records the tally extension as "extended pre-data to tallies".
   The prose's version of K2 (compare against `declared-evidence-before.tsv`, 4-tuples only) is
   vacuous: the LOG agrees with that receipt exactly, so it would demand no correction and leave the
   slice half untouched.

7. **Exact minimal repair that closes D5** — append only to
   `/home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md`, after line 1522 (current EOF, last line
   `deleted.`), in a new section. Wording constraints, each load-bearing:

   - **c1** contain verbatim, each within 6 physical lines of the literal marker `superseded by`:
     `assertions=56 resolved=53 skipped=33 mismatches=3`, `1 present`, `1 refused`
     (K2 matches substrings; `1 refused (S123 wrong-source citation)` supplies `1 refused`).
   - **c2** name the replacement as exactly `assertions=55 resolved=52 skipped=33 mismatches=3`,
     attributed to `census/round-22/attempt2/declared-evidence-before-final.tsv` (`dd8a6b7`,
     pinned instrument) — **not** `declared-evidence-before.tsv` and **not** 56/53.
   - **c3** name the replacement tally `2 present` and `0 refused`, with both flips: `S123`
     accepted (corrected quote, `git-worktree(1):12`) and `S138` present (qiita `gc.auto` fold false
     positive), per `census/round-22/attempt2/slice-verdicts.tsv`.
   - **c4** leave `LOG.md:1478-1522` byte-identical; no deletion (finding 5) and no in-place marker
     (finding 4).
   - **c5** put the block after a `^=====` underline of its own heading, so K2's scan — which ends at
     the first `^=====` after line 1470 — stops before it; wrap only at spaces, never mid-token, or
     the joined-paragraph match in K2 breaks.
   - **c6** write no other `assertions=`/`<n> <class>` scalar in the block whose value is not the
     receipt's own.

   **Closure command (frozen counter; for the lane or closure to run, not me):**

   ```
   cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tools/souji-record-agreement.py \
     --rev "$(git rev-parse master)" --root /home/vgpnk/Projects/shokunin/souji-shokunin --no-worktree \
     | grep -E '^MISMATCH	K2|^keys='
   ```

   Because of finding 3, K2 green is necessary but not sufficient. Substantive proof (does the
   correction name the pinned tuple, after the filed entry, without moving it):

   ```
   cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show "$(git rev-parse master):LOG.md" \
     | awk '/superseded by/{m=NR} /assertions=55 resolved=52 skipped=33 mismatches=3/{c=NR} \
            END{printf "marker=%d corrected=%d\n",m,c; exit !(m>1522 && c>m)}'
   ```

8. **Achievability.** The repair needs no filed-evidence edit and no operator file: `LOG.md` is
   lane-owned and the change is a pure append, which is exactly what PROTOCOL requires. The only
   non-append-only route — editing lines 1478/1509 or the r22 receipts — is unnecessary and would
   itself violate the append-only rule the claim rests on. If the round cannot land the append, the
   honest disposition is a residual: D5 stays open and C1's K2 must be reported as an uncorrected
   mismatch, not narrowed out of the key set.

## Attack log

- **A1 — prereg C1 K2 prose is the wrong predicate.** `.ufo/waves/round-23/preregistration.txt`
  C1 K2 compares against `census/round-22/attempt2/declared-evidence-before.tsv` and covers only
  4-tuples; `tools/souji-record-agreement.py:48` sets
  `K2_RECEIPT = "census/round-22/attempt2/declared-evidence-before-final.tsv"` and its docstring
  extends the key to `<n> <class>` tallies. Read literally, the prose is vacuous for D5 (LOG agrees
  with that receipt: 56/53 vs 56/53) and blind to the slice half. Not proposing an edit; the round
  must record which text governs, since a reviewer holding only the prereg would certify a green
  counter that proves nothing.
- **A2 — `ScribeLog` block (1) is self-contradictory.** The prompt names the superseded tuple as
  the correct one (E5, finding 2). As written it produces a LOG correction that asserts a value is
  superseded by itself; K2 would still pass (finding 3), so the defect would ship green.
- **A3 — K2 accepts same-paragraph "corrections".** The `later` search starts at the stale
  paragraph's own start line (`tools/souji-record-agreement.py:203-207`), so the frozen prose's
  "named by a LATER LOG.md line" is not what the code tests; an in-place marker edit passes with no
  appended line (E6 row 3).
- **A4 — K2's deletion guard is section-aggregate.** `if found == 0` cannot see one filed scalar
  disappear; deleting the 4-tuple plus correcting the tallies yields `M=0` while bytes were removed
  (E6 row 4), contradicting the prose's "its deletion is itself a mismatch".

## Residual risk and verification gaps

- K2's runtime output was not executed by me; E2 is my transcription of its predicate, and its
  agreement with the instrument's own run is `[INFERENCE]` until the lane/closure runs the closure
  command. The bytes it reads are the same bytes, and the predicate constants were copied verbatim.
- Findings 3-5 are properties of the committed-in-working-tree instrument, which is **untracked**
  (`git status`: `?? tools/souji-record-agreement.py`, `?? tools/souji-receipt-run.py`). Until the
  lane commits them, "the tool is the frozen contract" binds a working-tree file, not a revision —
  C2's blob-binding requirement is what makes that difference visible, and it is not yet met.
- Not in my scope but visible in the tree: `corpus/README.md` is currently modified-uncommitted
  (D4 repair in flight) and `census/round-23/` is untracked; K4 will count both at the tip unless
  the exemption file names them.
- D5's closure is a one-line-record property; no axis is harmed by the append, and calibration is
  the axis it serves.
