# W2 C1 control attack — round 23

Seat: L1Souji23.W2C1Ctl. Target: C1's before-value (6 revision-scoped mismatches at the base
revision). Lane tip at attack: `102690017115cb202f292828c90b72705f69bf09`. Read-only.

**Verdict on the control: `survives`.** The before-value is 6, reproduced from tip bytes, and every
one of the 6 is a defect the round repaired. None of the 6 would be 0 on a do-nothing tree.

**Verdict on C1's report layer: `falsified`.** Four records describing this control disagree with
the control's own committed receipt (F1-F4 below). The number is right; the sentences around it are
not.

---

## 1. The counter, re-run from tip bytes

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
python3 tools/souji-record-agreement.py --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --no-worktree
```

```
MISMATCH	K1	census/round-23/records/declared-evidence-after.tsv	receipt-absent	not in tree at 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd
MISMATCH	K2	LOG.md:1478	uncorrected	'assertions=56 resolved=53 skipped=33 mismatches=3' has no later 'superseded by' line
MISMATCH	K2	LOG.md:1495	uncorrected	'1 present' has no later 'superseded by' line
MISMATCH	K2	LOG.md:1495	uncorrected	'1 refused' has no later 'superseded by' line
MISMATCH	K3	corpus/README.md:440	tally-disagree	1 present != receipt 2 present
MISMATCH	K3	corpus/README.md:440	tally-disagree	1 refused != receipt 0 refused
keys=4 records=3 occurrences=13 mismatches=6
RC=1
```

Ran twice, identical. The tool blob at tip, `4765250`, `c0eeaa7` is one blob —
`617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9`, 350 lines — so this is not a
tool-drift reading (the D3 shape). The tool does not exist at `1208bfb` (`git show` empty), so the
control is necessarily "tip bytes, base revision", as the receipt
`census/round-23/records/agreement-control-base.txt:4` states.

At the tip the same command reports `keys=4 records=4 occurrences=17 mismatches=0`, rc 0. Target met.

---

## 2. Row-by-row: defect or do-nothing artifact?

| # | key / class | record:line at base | genuine pre-existing defect? | repair landed at tip | row verdict |
|---|---|---|---|---|---|
| 1 | K1 `receipt-absent` | `census/round-23/records/declared-evidence-after.tsv` | **yes — D2**, and independently confirmed: at `1208bfb` the after tuple `assertions=63 resolved=63 skipped=40 mismatches=0` exists **only** in `SCORECARD.md:14`, and the only receipts in that tree are the two *before* receipts (`declared-evidence-before.tsv` = 56/53/33/3, `-final.tsv` = 55/52/33/3). Nothing binds `9301d98`'s after-state. | receipt created at `4765250`: `census/round-23/records/declared-evidence-after.tsv` (`rev=9301d98c…`, `tool_sha256=65817d0d…`, stdout `assertions=63 resolved=63 skipped=40 mismatches=0`). Re-derived independently — see §3. Plus `c0eeaa7` names `4edb25dfe…` beside the before tuple in `SCORECARD.md:14`, clearing the value-disagree that the receipt exposes (§4). | repaired |
| 2 | K2 `uncorrected` | `LOG.md:1478` (paragraph opens at 1478; the tuple is on 1484) | **yes — D5**; spot-check D5 names exactly `assertions=56 resolved=53` as the superseded value, and `-final.tsv` holds 55/52 | `LOG.md:1529-1535` — "1. C1 base tuple … The authoritative before receipt is … `declared-evidence-before-final.tsv`: assertions=55 resolved=52 skipped=33 mismatches=3 (the earlier receipt is superseded by it…)". Filed occurrence still present at 1484. | repaired |
| 3 | K2 `uncorrected` | `LOG.md:1495` (`1 present`) | **yes — D5/D4**; `slice-verdicts.tsv` tallies 5 accepted / 2 present / 1 unverifiable / 0 refused | `LOG.md:1537-1541` — "2. Register-slice tally … The pairs "1 present" and "1 refused" are superseded by 2 present and 0 refused". | repaired |
| 4 | K2 `uncorrected` | `LOG.md:1495` (`1 refused`) | **yes — same receipt** (0 refused) | same lines, `LOG.md:1541` | repaired |
| 5 | K3 `tally-disagree` | `corpus/README.md:440` (`1 present != 2`) | **yes — D4** | `corpus/README.md:440` now reads "5 accepted with corrected quotes, 2 present, 0 refused, 1 unverifiable", with the sweep note at `README.md:495` | repaired |
| 6 | K3 `tally-disagree` | `corpus/README.md:440` (`1 refused != 0`) | **yes — D4** | same line | repaired |

**Would any be 0 on a do-nothing tree?** No. The do-nothing tree is exactly what §1 ran (base bytes,
no repairs, instrument present): all 6 fire. Rows 2-6 fire on unchanged base bytes by construction.
Row 1 fires on *any* tree that lacks the round's own artifact — including a do-nothing tree.

That last property is the one honest qualification, and it is a disclosure, not a falsification:
row 1 is **construction-guaranteed**. `tools/souji-record-agreement.py:139-142` returns from K1 on
`receipt-absent` before it ever reads `SCORECARD.md`, so the control's K1 row cannot distinguish
"D2 present" from "D2 absent" — it only asserts that the round has not happened. D2's substance is
nevertheless real (§3) and the round repaired it, so the row is a faithful (if uninformative)
measurement of D2, not a false positive. The claim-sizing statement the round should carry is:
**of the 6, five measure r22 record defects; the sixth measures the absence of a round-23 receipt,
which is guaranteed at base.** Do not present 6 as "six r22 defects".

---

## 3. Is row 1's repair real, or a transcription of the claim?

A receipt the round authors can always agree with the record the round authors. Test: re-derive the
receipt's own numbers with the pinned instrument.

```
python3 tools/souji-declared-evidence.py --rev 9301d98c1c689c79741f0f1ba1f171138d20af07 --file SCORECARD.md
→ assertions=63 resolved=63 skipped=40 mismatches=0   RC=0
```

Byte-identical to `declared-evidence-after.tsv`'s stdout block, and the recorded
`tool_sha256=65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4` equals the pin in
`census/round-22/attempt2/instrument-digests.txt:1`. The receipt is genuinely derived, not copied.
Row 1's repair holds on its merits, not on the control.

---

## 4. Counterfactual: base bytes + the round's receipt injected

Scratch clone at `/var/tmp/souji-r23-w2-C1Ctl/repo`, detached at `1208bfb`, the tip receipt committed
there, tip tool run against it:

```
MISMATCH	K1	SCORECARD.md:14	value-disagree	assertions=55 resolved=52 skipped=33 mismatches=3 != receipt assertions=63 resolved=63 skipped=40 mismatches=0 at 9301d98c…
keys=4 records=4 occurrences=16 mismatches=6
```

Two results, both load-bearing:

1. The base tree carries **content behind the receipt-absence**. `SCORECARD.md:14` quotes the
   before-value 55/52 twice; the second occurrence follows the tip token, so the proximity rule
   (`tools/souji-record-agreement.py:163-165`) binds it to `9301d98` and reports a value-disagree.
   A human reads it as the before receipt's number, so this is an *ambiguity of the record*, not a
   wrong number — and `c0eeaa7` removed it the only way it can be removed, by naming
   `4edb25dfe262515d0da63224bbba71e02e36cba5` beside the before receipt. That is substantive
   provenance hardening, not predicate appeasement.
2. The control's 6 and the counterfactual's 6 are the **same count with different composition**
   (row 1 changes class from `receipt-absent` to `value-disagree`). A future edit that removes one
   genuine defect and re-introduces a construction row would still read `6`. The control is a
   threshold, not a discriminator — disclose, don't fix.

---

## 5. Findings — C1's report layer, all reproducible from the tip

### F1 (fix) — the control value is stated as 20 in two records and 6 in a third
- `LOG.md:1576`: `nothing) = the same tool bytes at base: keys=4 records=3 occurrences=13` / `mismatches=20, rc 1`
- `corpus/README.md:456`: "`mismatches=20` at the base revision → `0` at the landing tip"
- `SCORECARD.md:21` and `census/round-23/records/agreement-control-base.txt`: `mismatches=6`
- LOG's `20` is the **333-line pre-hardening blob** `e41db304…e596` (`.ufo/waves/round-23/w1/CritPrereg.md:35`), which exists in **no commit**: `1208bfb` has no tool file, and `4765250`/`c0eeaa7`/`1026900` all hash to `617f4c96…`. The discriminator is on LOG's own line — it pairs `records=3 occurrences=13` (the revision-scoped base arm) with 20, while the 333-line measurement was `records=3 occurrences=13 mismatches=20`; the committed tool at base gives `records=3 occurrences=13 mismatches=6`. So no committed blob and no revision-scoped arm yields 20. This is the exact D3 shape C2 claims to close, reproduced inside C1's own report.
- Coincidence trap for whoever fixes this: the frozen command at the tip **right now** also prints `mismatches=20`, but with `records=4 occurrences=17` (§F3). Fixing LOG to "20" by copying today's tip run would make the number look right and the row still wrong.
- **Do:** set `LOG.md:1576` and `corpus/README.md:456` to `mismatches=6` and cite `agreement-control-base.txt`.

### F2 (fix) — the after receipt cited twice does not exist, and the receipt that does exist says 1
- `SCORECARD.md:21` and `LOG.md:1578` cite `census/round-23/records/agreement-after.txt`.
- `test -e census/round-23/records/agreement-after.txt` → ABSENT. The file is `agreement-after.tsv`, and it records `rev=476525026cdb179f2d49441e1cb6c6f7316f3124`, `rc=1`, `keys=4 records=4 occurrences=18 mismatches=1`.
- So the only committed after-receipt binds the **first landing**, where the target was *not* met, and `LOG.md:1577` ("After: mismatches=0 at the landing tip") is contradicted by the receipt it cites in the next line. The 0 I measured at `1026900` is currently **unbound by any receipt** — which is the K1/D2 defect this round is supposed to have closed, applied to itself.
- **Do:** cite `agreement-after.tsv` and describe it as the `4765250` run (rc=1), then commit a receipt for the tip run (`--rev 1026900… --no-worktree` → `mismatches=0`) and cite that for the after-value.

### F3 (fix) — the documented counting command does not reproduce either number
- `SCORECARD.md:21` and `corpus/README.md:456` both document `python3 -B tools/souji-record-agreement.py --rev <full40>`. That command's result depends on which seat is writing at the moment: at the same revision `1026900` it gave `mismatches=1` (`K4 .ufo/waves/round-23/report-draft.md`) at 05:4x and `mismatches=20` at 05:47 as nine `w2/W2*.md` seat reports and `tools/__pycache__/` appeared — same `keys=4 records=4 occurrences=17`, only K4 moved. At base it gives `mismatches=8` today, not 6.
- The 6 and the 0 are only obtainable with `--no-worktree`, which the preregistration's frozen counter (`preregistration.txt:22-23`) never mentions. K4 is a live-worktree observation and cannot be replayed at base — that must be said in the record, not left to the receipt's `note=`.
- **Do:** put `--no-worktree` in both counting-command cells, and state the live-K4 arm separately as a snapshot (`mismatches=29` at base per `agreement-control-base-worktree.txt`; `20` at tip at 05:47 and moving with every seat report).

### F4 (fix) — fixture case count disagrees with itself
- `LOG.md:1579-1580`: "kills an always-zero emitter on eight cases"; `SCORECARD.md:21`: "9/9". Ran `python3 tests/fixtures/r23-record-agreement.py --tool tools/souji-record-agreement.py` → `selftest=9/9`, `control=FALSE-GREEN-REJECTED`, nine cases, including case 9 (exempted operator path is not a mismatch). SCORECARD is right, LOG is wrong.
- **Do:** `eight` → `nine` at `LOG.md:1579`.

### F5 (disclose) — the frozen K2 prose names the wrong receipt
- `preregistration.txt:33` says K2 compares against `census/round-22/attempt2/declared-evidence-before.tsv`. That file's counts line **is** `assertions=56 resolved=53 skipped=33 mismatches=3` — the very tuple the base control flags. Read literally, the prereg's K2 makes row 2 **agree** and the before-value becomes **5**, not 6.
- The code (`tools/souji-record-agreement.py:50`) reads `declared-evidence-before-final.tsv` (55/52), which is correct: `-final.tsv` was committed at `dd8a6b7` as the pinned before-receipt, `instrument-digests.txt` pins the tool, spot-check D5 names 56/53 as superseded, and `LOG.md:1529-1535` documents the supersession.
- **Do:** correct `preregistration.txt:33` to `declared-evidence-before-final.tsv` with a one-line note that the superseded receipt still exists; do not leave a frozen predicate that contradicts its own code by one mismatch.

### F6 (accept, note) — the K2 correction check is satisfiable by restating the stale value
- `tools/souji-record-agreement.py` accepts a correction when a line within 6 lines contains both `superseded by` and the stale token; it never requires the superseding value to be correct or present. `"1 present superseded by 1 present"` would pass. The round's actual repairs do state the correct values (`LOG.md:1532`, `1541`), so nothing is currently wrong — but the predicate is weaker than "re-derives".
- **Do:** accept for this round; harden next round to require the superseding value.

### F7 (disclose) — the prereg's control receipt path is `.tsv`; the artifact is `.txt`
- `preregistration.txt:57` names `census/round-23/records/agreement-control-base.tsv`; only `agreement-control-base.txt` exists. Same class as F2, one line of prose.

---

## 6. Axis impact

- **Calibration (7):** the control value itself is correct and the four routed defects D2/D4/D5 are genuinely repaired with real receipts — no axis regression from the control. F1/F2 are record-agreement defects on the axis whose entire claim is record agreement, so they cap any *move*: calibration stays 7 until the report rows match the receipt.
- **Operability (8):** untouched by this seat; note only that F2's absent after receipt is the C2 kill-rule shape (`verify` on a path that does not exist).
- **Coverage (8):** untouched.

---

## 7. What I ran / limits

Ran: the counter at base ×2 (`--no-worktree`), at tip (`--no-worktree` and K4-on, the latter twice
~4 minutes apart to measure K4 drift); base K4-on; blob
hashes of `tools/souji-record-agreement.py` at `1208bfb`/`4765250`/`c0eeaa7`/`1026900`;
`tools/souji-declared-evidence.py` at `9301d98`; `tests/fixtures/r23-record-agreement.py` 9/9;
`git show`/`git grep`/`git diff --word-diff` on `SCORECARD.md`, `LOG.md`, `corpus/README.md`, the
r22 receipts; one counterfactual clone at `/var/tmp/souji-r23-w2-C1Ctl/repo` (scratch, removed).

Not run: nothing outside the lane was read or written; no installs, no git/jj mutation in the lane,
no writes to `.ufo/state/`, `MANIFEST.json`, fleet `scripts/`/`templates/`. `[INFERENCE]` appears
nowhere in the findings above — every figure is a quoted command output, except the 333-line→20
attribution, which is taken from `.ufo/waves/round-23/w1/CritPrereg.md:35` rather than re-run.
