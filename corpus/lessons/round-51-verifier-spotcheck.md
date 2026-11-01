author: hyaku closure (non-author integrator, zcode subagent (fresh session, non-author))

# souji round 51 — non-author verifier spot-check

Round: souji 51. Base `d1b8734d835171c7329225fdaab249c5c6799de8` (r50 non-author
spot-check), tip `e004ee1a765df8e1f9d5e14bf13f76539ed133df` (branch `master`,
pushed). This verifier did not author the round; every measurement below was
re-run by this session from committed bytes (`git cat-file`/`git show` only —
index-free git per the host note; nothing inside the repo was written by this
check except this file).

## 1. Step-1 conformance

| check | command (abridged) | observed | verdict |
|---|---|---|---|
| report committed by lane identity | `git -C <fleet> log --format='%an <%ae> %H' -1 -- .ufo/reports/round-51/souji.md` | `souji-shokunin <souji@shokunin.local> 1a2868585c821e47d37568f71030444b091d162c` | pass |
| `SHONEN` heading | read of the report | `## SHONEN` with 4 `[~]` lines, each with a resolvable pointer | pass |
| cited commits exist + ancestry | `cat-file -t` + `merge-base --is-ancestor <c> refs/heads/master` for 851093b, d9aa24f, e004ee1a (and base d1b8734) | all exist; all ancestors of master | pass |
| lane tip pushed | `ls-remote origin refs/heads/master` vs local `rev-parse refs/heads/master` | both `e004ee1a765df8e1f9d5e14bf13f76539ed133df` | pass |
| round work in d1b8734..e004ee1a | `git log` over the range | exactly 3 commits (851093b freeze → d9aa24f content → e004ee1a end receipts), all `souji-shokunin` | pass |
| PROVINCE.md untouched | `diff-tree -r --name-only base tip` | absent from range | pass |
| dispatch/complete digest | contract inputs vs `ls-remote`/HEAD | launch 07:37:12 base=d1b8734, complete 10:18:24 head=e004ee1a pushed=True — matches repo state | pass |
| LOG ties | `show tip:LOG.md` | `## Round 51` (line 2412) + `### Round 51 end-receipts addendum` (line 2498); every landed-changes row ties to it | pass |
| marker rule | report substance | real work, evidence pointers, landed commits — not a marker | pass (status ok) |

Conformance defects: none that change status; two message/annotation defects
are recorded under "Routed defects" below (status-neutral).

## 2. Freeze discipline (one-commit freeze)

`git diff-tree -r --name-status 851093b^ 851093b` — the freeze commit adds
exactly: preregistration.txt, c1/c2 counters, c1/c2 arms (populations), both
do-nothing controls, and the pre-flight receipts (census-before raw + v1
receipt, porcelain-at-base, idx-repair-base, NTFS base, feasibility synth
red/green ×2 + defects note). Counter bytes are identical at freeze, content
tip and final tip (`rev-parse <rev>:<path>`: c1 `134ada59…`, c2 `95f1da86…`).
sha256 of the frozen counter bytes equals the preregistration pins
(c1 `f0db3dcc…91be9`, c2 `ae12203d…33af`). Defect: the freeze commit message
says "S274 captures" but the two `census/round-51/sources/s274-*` files first
land in the content commit d9aa24f (message overclaims; the preregistration
text itself only cites the capture paths, which is fine) — status-neutral,
routed.

## 3. Claim re-checks (re-measured by this verifier)

### C1 — calibration: routed record corrections land append-only + standing suite green at the final tip

Commands run by this verifier (frozen bytes extracted from the freeze commit;
`--root` = lane repo; scratch outside the repo):

```
python -B c1-counter-frozen.py --root LANE --rev d1b8734d835171c7329225fdaab249c5c6799de8 --base-rev d1b8734… --scratch DIR
  → SUMMARY corr=FAIL dup=ok ntfs=FAIL listing=ok corr_lines=0 dup_base=2 dup_tip=2 ; LEG-FAIL corr ; LEG-FAIL ntfs ; EXIT=1
    (byte-equal to the committed control census/round-51/controls/c1-control-donothing.txt)
python -B c1-counter-frozen.py --root LANE --rev d9aa24f4b09efa8c8b69a6035ba1f3a09b6d35dc --base-rev d1b8734… --scratch DIR
  → SUMMARY corr=ok dup=ok ntfs=ok listing=ok corr_lines=1 dup_base=2 dup_tip=2 ; EXIT=0
python -B c1-counter-frozen.py --root LANE --rev e004ee1a765df8e1f9d5e14bf13f76539ed133df --base-rev d1b8734… --scratch DIR
  → SUMMARY corr=ok dup=ok ntfs=ok listing=ok corr_lines=1 dup_base=2 dup_tip=2 ; EXIT=0
```

The preregistered target line matches exactly. The dup leg proves the
duplicated "Reject sample" bullet bytes occur exactly twice at BOTH revs
(append-only proven); the R51-CORRECTION line exists at the tip
(`corpus/lessons/round-50.md` line 124) and names the duplication; the ntfs
leg proves exactly one `quoted_d_rows=6` with the six-path listing
byte-identical to base. Suite leg re-measured at the final tip with the r46
frozen counter (souji-owned instrument, read-only + temp-dir writes):

```
python -B r46-c1-counter-frozen.py --root LANE --rev e004ee1a… --work DIR
  → SUMMARY assertions=552 mismatches=70 registered=70 corrected=0 exempted=0 unfiled=0 instrument_sha256=a3324916…9831 ; EXIT=0
```

Matches the committed content-tip receipt (`census/round-51/records/c1-suite-content-tip-51.txt`)
and the report's quoted final-tip receipt; the instrument sha256 equals the
counter's pin. Verdict: **improved** (re-measured, both ends).

### C2 — coverage: live workspace census refresh + derivable drift receipt + per-artifact receipts (sourced on S274)

```
python -B c2-counter-frozen.py --root LANE --rev d1b8734… --base-rev d1b8734… --scratch DIR
  → PRISTINE FAIL WORKSPACE-CENSUS-ABSENT d1b8734…:census/round-51/workspace-census.tsv (rc=128) ; EXIT=1
    (byte-equal to the committed control census/round-51/controls/c2-control-donothing.txt)
python -B c2-counter-frozen.py --root LANE --rev d9aa24f… --base-rev d1b8734… --scratch DIR
  → SUMMARY shape=ok drift=ok receipts=ok limit=ok rows=126 added=79 removed=2 ; EXIT=0
python -B c2-counter-frozen.py --root LANE --rev e004ee1a… --base-rev d1b8734… --scratch DIR
  → SUMMARY shape=ok drift=ok receipts=ok limit=ok rows=126 added=79 removed=2 ; EXIT=0
```

Independent re-derivation of the drift receipt's numbers from the two
committed captures (`git show <rev>:census/round-46/workspace-census.tsv` and
`…/round-51/workspace-census.tsv`): 126 rows, all 4-field; active-foreign-scratch
19 → 89; in-use/pushed 14 → 14; lane-clone (git-repo) surfaces 17 → 17 — all
equal the receipt's COUNT lines; the counter's drift leg additionally
re-derives every COUNT line and the full ADDED/REMOVED key comm (79 + 2, all
3-field) and passed at both tips. Pasteable greps at the final tip:
`grep -c -P "\tin-use/pushed\t" …workspace-census.tsv` → 14 (claimed 14, ok);
`grep -c "^| S274 |" corpus/SOURCES.md` → 1 (claimed 1, ok);
`grep -c "^ADDED" …records/ws-drift-vs-r46.tsv` → **79** (report, SCORECARD
and preregistration annotate **78** — number-drift defect, see Routed
defects; the preregistered SUMMARY target `added=79` is the binding metric
and is met). Verdict: **improved** (re-measured, both ends).

### Axis-harm check

`git diff-tree -r -p d1b8734… e004ee1a… -- SCORECARD.md` is purely additive
(r51 landing section + planned r52). The axis rows for coverage 8,
calibration 7, operability 8 are byte-identical at base and tip
(`git show <rev>:SCORECARD.md` grep). No owned axis harmed.

## 4. Disclosures verified

- Four mined mistakes: `corpus/lessons/round-51.md` `## Mistakes` carries
  exactly 4 rows, each with evidence pointer, captured-by and fix —
  (1) header-row drift artifact, (2) unpinned new-top-level-candidates
  definition, (3) CRLF-vs-LF vacuous listing leg (all three named in the
  committed `records/feasibility-defects-note.txt` and fixed before the
  freeze), (4) the E12 SOURCES-append-outside-Registry catch. Note for the
  record: the lane's artifacts name exactly THREE pre-freeze counter defects
  (prereg, feasibility note, lesson rows 1–3); the fourth mined row is E12,
  caught post-freeze by the round-end census gate.
- E12 first take committed, not deleted:
  `census/round-51/records/census-after-first-take-disclosed.txt` ends
  `E12	S274 row outside Registry section`; the passing re-take
  (`census-after.txt`) reads `CENSUS-RUN lane=souji conf_rc=2 dir_rc=0` with
  59 W04 rows and `verify` ok over every check
  (`census-after-verify.txt`); S274 sits inside the Registry directly after
  S273 (SOURCES.md line 234, Registry starts line 32).
- NTFS tolerance stayed at 6: base receipt and tip re-check
  (`ntfs-exclusion-check-base.txt`, `ntfs-exclusion-check-tip-51.txt`) each
  list exactly the six pinned control-character paths with
  `quoted_d_rows=6` / `count=6`; idx-repair-base receipt reads BEFORE rows=8
  → AFTER rows=6 unexpected=0 EXIT=0 (tolerance not widened).
- Disclosed-not-mined items present in the lesson prose: the discarded first
  census take (`.zcode` hidden-dir scope, 124 vs 126 rows), the 86 → 89
  foreign-scratch growth between takes, and the two discarded suite-receipt
  takes (named in the committed suite receipt's header).
- SOURCES.md diff base→tip is +2 lines / −0 lines (S274 row + provenance
  paragraph): append-only; no existing row's status/recheck/used-by cell
  changed. `corpus/knowledge/` untouched (expansion stays unchanged).
- Census before/after both disclosed with the conf-form rc-2 host state
  verbatim (`CONF-RC=2` inside both v1 receipts); DIR-RC=0, DIR-RESULT=ok,
  DIR-WARN-W04=59 at both ends. Item stays operator-owned (r48/r50 L0),
  routed around, nothing assumed answered.

## 5. Discernment spot-check table (re-opened by this non-author)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S274 admit (git-cherry(1)) | admitted, tier A docs, scope = patch-equivalence ground for the pushed-receipt limit | live re-open `curl -sSL https://git-scm.com/docs/git-cherry` → HTTP 200, no redirect, 27219 bytes, sha256 `abe22306…9ab73e3` — byte-identical to the committed capture; quote re-counted by re-running the pasted command against the committed capture: substring True, **15 words** | agree | the quote is verbatim in the DESCRIPTION, the tier-A scope is precise (equivalence semantics only; classification labels stay S270's), and the grounding claim (sha comparison cannot see copied history) is exactly what the sentence states |
| Reject sample | zero new reject rows, one fetch bound | `ls-tree tip:census/round-51/sources/` → only the two S274 files; the Gate's sweep names the round-start/end census runs as local metadata reads, not fetches | agree | the bounding sweep is checkable and holds; a zero-reject round with an explicit sweep is honest taste evidence, not a skipped duty |
| NOT-SAFE per-artifact receipt (helpers-r74) | NOT-SAFE, reason `none`, advisory | re-ran the frozen `tools/souji-verify.sh` bytes (blob sha256 `e6cb3f93…691f` = the receipt's tool sha) on the target → `VERDICT … NOT-SAFE	none	obsidian=ledger-unverifiable; stale=not-scratch-type`, exit 0 | agree | verdict and stale evidence reproduce; the obsidian evidence field wording differs from the receipt (`ledger-unverifiable` vs `no-matching-ledger-row`) because this re-run executes the tool from scratch, where the repo-relative ledger does not resolve — a cwd artifact of the re-check method, not a verdict change. The scratch-r80v row (NOT-SAFE, secrets-refusal) was NOT re-executed by design: the tool refuses secret-shaped descendants and this verifier leaves that surface untouched |
| Census validate (round-end gate) | conf form rc 2 disclosed; adapter/DIR form exit 0 | re-ran the contract's literal command → `souji	missing	…` exit 2 (the documented L0-open host state, disclosed verbatim in every receipt); re-ran the DIR form over the lane repo → verdict `ok`, 59 W04, exit 0 | agree | the rc-2 is a real host state correctly disclosed and routed around, and the working DIR-form census independently reproduces the committed receipts' verdict |

## 6. Trend verdicts (with this verifier's evidence)

- **expansion: unchanged** — `corpus/knowledge/` absent from the range
  diff-tree; PROVINCE.md absent; SOURCES +1 (S274, from the standing Leads
  list); the workspace census refresh covers already-owned census ground
  with current data (coverage stays 8, no new surface claimed).
- **quality: improved** — the two routed record-accuracy repairs verified
  append-only by the frozen counter at both revs (this verifier re-ran it);
  the standing suite receipt is green at the tip again under the directed
  ordering (re-measured at the final tip, exit 0, unfiled=0); the drift
  receipt's every number re-derives from the two committed captures
  (counter drift leg + this verifier's independent spot re-derivation).
- **discernment: improved** — four mistakes mined with same-round executed
  fixes; three caught pre-freeze by feasibility/review before they could
  become frozen instruments, one by the round-end census gate doing its job;
  both do-nothing controls are red at the base and this verifier re-derived
  both greens from committed bytes; the E12 failure is disclosed with the
  first take committed; the S274 admission names its scope precisely; the
  fresh-start ruling-out table (r43/r44/r45) is re-derived in the lesson and
  matches the structural facts this verifier checked (one-commit freeze;
  targets derived from base-honest states; same instrument bytes on both
  arms).

## 7. Per-axis verdicts (this verifier)

| axis | verdict | basis |
|---|---|---|
| calibration | improved | C1 re-measured red→green at both ends; append-only proven; suite restored green at the tip (re-measured); routed items addressed exactly as directed |
| coverage | improved | C2 re-measured red→green at both ends; drift re-derivation verified; per-artifact receipts verified incl. tool-sha pin; sourced on S274 (re-opened live) |
| operability | unchanged | no operability claim; axis rows byte-identical; no harm |

## 8. Routed defects (the lane must fix next round; all status-neutral)

1. **Number-drift (78 vs 79).** The pasteable grep
   `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` is
   annotated **78** in the round report (Sources & frontier and the C2
   measurement row), the SCORECARD r51 C2 row, and the preregistration's
   counting-commands line. The actual committed count is **79** at both the
   content tip and the final tip (and the counter's own preregistered
   SUMMARY metric `added=79` is met — the binding target). Fix in r52: an
   appended erratum/correction line (report + lesson; SCORECARD via a new
   appended correction row per append-only discipline) naming 79 and
   superseding the 78 annotations. The preregistration file itself is frozen
   — correct by naming, never by editing.
2. **Freeze-commit message overclaims "S274 captures".** The two
   `census/round-51/sources/s274-*` files first land in the content commit
   d9aa24f, not the freeze commit 851093b whose message names them. No
   substance is affected (the preregistration only cites the paths; the
   captures exist and verify). Fix: name the message inaccuracy in the r52
   lesson (commit messages are immutable).
3. **Prereg mining plan vs executed lesson (non-claim item).** The
   preregistration's mistake-mining plan named "the three counter defects
   plus the discarded first census take" as the rows; the executed lesson
   mines E12 as the fourth row and discloses the census take (plus the
   86→89 growth and two suite takes) in prose. This verifier grades the
   executed choice better (E12 is an executed-fix mistake; the census-take
   scope slip is disclosed with its scope rule) — recorded so the prereg-plan
   drift is on the record, nothing to fix beyond this note.
4. **SHONEN for the operator (unchanged from r50).** All four boxes remain
   author-asserted `[~]`; no non-author verifier has written `[x]`. This
   verifier's checks (boxes 1–3 evidence resolves; box 4 PROVINCE absent
   from the range) look satisfiable by a non-author, but per protocol the
   `[x]` writer must be a non-author reviewer arranged by the operator —
   this closure does not write `[x]`.

## 9. Verdict

Both claims verify (re-measured from committed bytes at named revisions); no
owned axis is harmed; conformance holds with the status-neutral defects
above; the report is a real report, not a marker. Lane-round souji 51:
**ok / admitted**.
