author: hyaku closure (non-author integrator, zcode subagent (fresh session, non-author))

# Round 49 verifier spot-check — souji (C1 freeze-check binary-fixture repair, calibration)

Verifier: hyaku closure, round 49, 2026-11-01. Fresh session, did not author
this round. Dispatch/complete digest (orchestrator watchdog): launch
2026-11-01T01:22:08-08:00 base=5a26fbfd5b0f; complete 2026-11-01T03:13:09-08:00
head=7836df3e5053 pushed=True. Round base `5a26fbfd5b0f94b0d8283908a0f4b876b2857bfc`,
tip `7836df3e50538598f245ce3823d979de2992eb73` (branch master, pushed).

## 1. Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git -C <fleet> log --format='%an %H' -1 -- .ufo/reports/round-49/souji.md` | `souji-shokunin 573e949976dbc194b7a82a25c57c8a4584aba8f0` | pass |
| report timestamp vs complete digest | `git log --format='%ad' -1 573e9499` | `2026-11-01 03:13:10 -0800` (digest says 03:13:09 -08:00) | pass |
| SHONEN heading | read of `.ufo/reports/round-49/souji.md` | `## SHONEN` present; 4 boxes, all `[~]` with resolvable pointers; no `[x]` | pass |
| cited lane commits exist + ancestry | `git cat-file -e <h>^{commit}` + `git merge-base --is-ancestor <h> refs/heads/master` for 5a26fbfd, ebebc44c, 445321aa, f86a5103, 7836df3e | all exist, all ANCESTOR | pass |
| branch tip pushed | `git ls-remote origin refs/heads/master` vs local `rev-parse refs/heads/master` | both `7836df3e50538598f245ce3823d979de2992eb73` | pass |
| cited work reachable in range | `git log 5a26fbfd..7836df3e` | exactly 4 commits (ebebc44c, 445321aa, f86a5103, 7836df3e), all authored `souji-shokunin`, matching the report's Landed-changes table one-for-one | pass |
| report marker rule | read | content-rich report with counting commands and checkable hashes; not a marker | pass |
| report sections in order | read | Work performed / Landed changes / Before→after measurements / Sources & frontier / Trend verdicts / SHONEN — all present, in contract order | pass |

Index-free git only (`rev-parse`, `cat-file`, `ls-tree`, `diff-tree`,
`merge-base --is-ancestor`, `show`, `log`, `ls-remote`); no `git status`, no
mutating command, no checkout. PROVINCE.md untouched this round (absent from
the range diff) as the report claims.

## 2. Claim C1 — re-check (calibration; instrument repair, not a capability acquisition)

The round's one declared claim. Re-derived end-to-end with my own runs — not
from the lane's receipts alone. All scratch under a verifier-only scratch dir;
the repo was never written to.

**2a. The repair diff is exactly the claimed 2 hunks, verdict code
byte-identical.** I extracted the tool bytes at base and tip from the object
store and hashed/diffed them myself:

- `git show 5a26fbfd…:tools/souji-freeze-check.py | sha256sum` →
  `f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999` — equals
  TOOL-BASE-SHA256 in `census/round-49/records/tool-diff-base-to-fix.txt`.
- `git show 7836df3e…:tools/souji-freeze-check.py | sha256sum` →
  `d1ca06fd0fb21d4c7a8452dbbc879f2ecf63ffaaf65378efa3c512e4dbfca364` — equals
  TOOL-FIXED-SHA256 in the same receipt.
- My own `diff -u base tip`: exactly 2 hunks (`grep -c '^@@'` → 2), byte-identical
  in content to the committed receipt: hunk 1 = docstring lines only; hunk 2 =
  the fixture writer `open(fp, "w")` + `fh.write(c)` → `open(fp, "wb")` +
  `fh.write(c.encode("utf-8"))` plus its comment lines, inside
  `selftest_case`. No verdict/digest/freeze-detection/ancestry code is touched —
  "verdict code byte-identical" holds by construction of the diff.

**2b. Raw selftest, my own runs (the round's before→after).**

- Base bytes: `python -B <base extraction> --selftest` →
  `SELFTEST cases=41 pass=4 fail=37`, exit 1 — matches
  `controls/freeze-selftest-base-red.txt` (4/37 red, as briefed).
- Tip bytes: `python -B <tip extraction> --selftest` →
  `SELFTEST cases=41 pass=41 fail=0`, exit 0 — matches
  `records/freeze-selftest-fixed-green.txt`.

**2c. The r49 counter at BOTH revisions, my own runs ("same instrument both
ends").** Counter digest check first: `git show 445321aa…:census/round-49/c1-counter.py`
and `git show 7836df3e…:census/round-49/c1-counter.py` both sha256 to
`194df28cfc02288f0fa82eaef223ed30dc0d158ffc6d80a8be670fb5c5a0b94e` — the value
pinned in `preregistration-r2.txt`. The instrument's bytes are identical in
both arms; only the world (the tool's committed bytes) moves. This is the
structural answer to the r45 different-instrument limit, and I verified it at
the byte level, not by trusting the claim.

- Counter at base (rev=5a26fbfd…), my run →
  `selftest FAIL rc=1 summary=(41, 4, 37)` / `real ok` / `retro red findings=4` /
  `retro_clean ok` / `SUMMARY selftest=FAIL patches=0/3 real=ok retro=red
  retro_clean=ok tool_sha=f7f54e8f0a71`, exit 1 — byte-equal to the committed
  do-nothing control `controls/c1-control-donothing-r2.txt`.
- Counter at tip (rev=7836df3e…), my run →
  `selftest ok rc=0 summary=(41, 41, 0)` / `real ok findings=0 summary=(2, 0)` /
  `retro red findings=4` / `retro_clean ok summary=(3, 0)` /
  `SUMMARY selftest=ok patches=3/3 real=ok retro=red retro_clean=ok
  tool_sha=d1ca06fd0fb2`, exit 0 — byte-equal to the committed
  `records/c1-tip-49.txt`, and every leg matches the prereg population table's
  expected-at-tip column. `patches=3/3` (P1 reversed digests, P2 empty
  `--diff-filter=A`, P3 failing merge-base each flip the selftest non-zero)
  re-derived in my runs: the repaired selftest still discriminates.
- Verdict-path-unchanged check: `real`/`retro`/`retro_clean` are identical at
  base and tip in my runs (ok/red/ok, same finding counts), while
  selftest/patches flip exactly as the prereg's population table predicts. No
  verdict-path regression.
- Both counter arms exit exactly 0-could-not-evaluate free (no REFUSAL lines).

**2d. Freeze-check verdicts, my own runs.**

- Base tool bytes over `preregistration.txt` at ebebc44c →
  `FINDING C1 CONTROL-NOT-RED census/round-49/controls/c1-control-donothing.txt
  last line 'COUNTER-EXIT=1' is not EXIT=<nonzero>` / `SUMMARY claims=1
  findings=1`, exit 1 — byte-equal to `records/freeze-check-at-freeze-attempt1.txt`.
- Tip tool bytes over `preregistration-r2.txt` at 7836df3e →
  `SUMMARY claims=1 findings=0`, exit 0 — byte-equal to
  `records/freeze-check-at-tip.txt`.

**2e. Freeze discipline (attempt 1 ebebc44c superseded by attempt 2
445321aa).**

- Ordering: attempt-2 commit `git diff-tree -r ebebc44c 445321aa` adds exactly
  two files (`preregistration-r2.txt`, `controls/c1-control-donothing-r2.txt`)
  and modifies/deletes nothing. Every after-data receipt
  (`freeze-selftest-fixed-green.txt`, `tool-diff-base-to-fix.txt`,
  `c1-tip-49.txt`, the S272/S267 receipts) first appears in the content commit
  f86a5103 (10:47:03 UTC), after attempt 2 (10:31:04 UTC; attempt 1 at
  10:17:15 UTC). The supersede landed before any after-data existed — the
  checkable form of the r48 Amendment-1 ordering holds.
- Attempt 1 preserved: all six attempt-1 frozen files byte-identical (same
  blob ids) at 445321aa and at the tip.
- CONTROL-NOT-RED mined: `corpus/lessons/round-49.md` `## Mistakes` row 2
  records the class ("a receipt destined for a grammar-parsing field must meet
  that grammar") with the attempt-1 freeze-check receipt as evidence, the
  freeze-check named as captured-by, and the r2 re-take as fix, including the
  standing rule (run the freeze-check verdict against a freeze commit BEFORE
  building on it). Verified.
- No post-freeze edits: `preregistration-r2.txt`, `c1-counter.py`,
  `c1-arms.tsv`, both control receipts byte-identical (same blob ids) between
  the freeze commit and the tip. Population digest re-hashed:
  `c1-arms.tsv` → `2e4bc72703defd11fd6c4d8d8eb77aa274546e48cd7bde7287a0f8326b0d9f22`,
  equal to the prereg's pin.

Claim C1 verdict: **verified — calibration improved**. Every value in the
report's before→after section reproduced by my own runs. The r45 limit does
not apply (same instrument bytes both arms, verified). The repair direction is
the r48 non-author closure's own routed fix (r48 spotcheck defect item 1),
not a new instrument invented to flip a verdict.

## 3. No axis harmed

- `git diff-tree -r -p 5a26fbfd 7836df3e -- SCORECARD.md`: purely additive —
  one new r49 landing section + planned r50; no axis row, score, or
  last-change cell edited. Numeric scores stay 7/8/8 (calibration/operability/
  coverage), honestly unchanged; the lane does not claim saturation from one
  repair.
- PROVINCE.md: absent from the range diff (untouched).
- LOG.md, SOURCES.md, lessons: append-only diffs (LOG: one appended round-49
  entry; SOURCES: one provenance line + one appended row S272, no existing
  row's cells changed — verified in the diff).
- operability: no command surface added or removed; the sweep's named limits
  are documentation, not edits. coverage: no province surface change.
  Verdicts: calibration improved, operability unchanged, coverage unchanged.

## 4. Discernment spot-check (Gate sample, re-opened by this verifier)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S272 admit (the Gate's only new row, the round's sourced ground) | admitted | live fetch `https://docs.python.org/3/library/functions.html` (served `/3/builtins/functions.html` after one 301), this session: HTTP 200, 330862 bytes, sha256 `ece1c4b3c9c266377b26b6907b44d8c1470c587696c2dacce52fedef9e00701a` — identical to the capture receipt | agree | located quote found verbatim on the live page (tag-stripped, whitespace-flattened): "When writing output to the stream, if newline is None, any '\n' characters written are translated to the system default line separator, os.linesep." — 23 words by my own count (≤25); the supporting encoding sentence is present; the tier-A docs source grounds exactly the text-mode translation mechanism behind the repaired defect; scope limit honestly stated (interpreter behavior only) |
| S267 standing rejection re-open (the Gate's stated reject sample) | stays rejected | live fetch `https://docs.python.org/3/builtins/stdtypes.html`, this session: HTTP 200, 814236 bytes, sha256 `0a9474e3b83b8fb3cb862d51fdfa3e0fca65e83eab531b44b28b00a881c8f5d3` — identical to the re-open receipt | agree (with a wording nit) | the comparison sentence is verbatim on the live page ("Sequences of the same type also support comparisons. In particular, tuples and lists are compared lexicographically by comparing corresponding elements."); zero occurrences of "factual"; the rejection reason (tuple equality cannot establish historical correction truth) holds — the page documents comparison semantics only. Nit: the receipt's "zero occurrences of histor*" is exact for the page content but the raw bytes carry one footer occurrence ("History and License" link) — the decision is unaffected; name the counting method next time |
| S271 word-count erratum (r48 carry-in item 2) | erratum recorded, history not rewritten | recount by command this session: `len(s.split())` over the verbatim quote → 16 | agree | the r48 "17 words" label was wrong; verbatim count is 16; ≤25-word bound held either way; the r48 lesson stays as filed (append-only discipline respected) |

New SOURCES row re-opened: S272 (the only new row) — URL, byte count, sha256,
located quote, and 23-word count all reproduced above against live bytes.

Census commands this session:

- Contract command `sources-census.sh validate --root <fleet> souji` → rc 2,
  `souji missing` — the known, disclosed conf-name-vs-host mismatch (the
  lane's registry lives at `fleet/shokunin-repo-hygiene`, not
  `<fleet>/souji-shokunin/`), routed to the operator at L0 round-48 and
  disclosed verbatim in the report; carried defect, status-neutral.
- Explicit-directory form over the lane repo → exit 0, `shokunin-repo-hygiene
  ok`, 59 W04 warnings (W-codes never change status), the last one being
  `S272 duplicate url docs.python.org/3/library/functions.html across scopes`
  — identical to the committed `records/census-after.txt` (ADAPTER-EXIT=0).
  Round-end exit-0 claim: held through the documented adapter path, as the
  r48 closure also ruled (agree with that precedent).

## 5. Trend verdicts (this verifier's, with evidence)

- **expansion: unchanged** — no `knowledge/` entry added, no Core promotion,
  no PROVINCE change, no capability row; SOURCES 195 → 196 (my count with the
  report's command: `grep -cE '^\|\s*S[0-9]{3,}\s*\|'` → 195 at base, 196 at
  tip) on a docs host the coverage map already held; the +1 W04 is S272's
  shared URL, disclosed. Agree with the lane.
- **quality: improved** — the registered r42 gate `r42-freeze-check-selftest`
  had no obtainable green on this host at base (37/41 false failures from
  platform-dependent fixture bytes) and re-derives green end-to-end from
  committed bytes at the tip (my runs: raw 41/41; counter green with
  patches=3/3; verdict legs unchanged); the fixture rule is a committed SKILL
  contract with a schema-complete registry row (name/kind/entry/verdict
  map/self-test/pinned-value/write scope/owner — verified in the SKILL.md
  diff); the hazard sweep bounds the class across the inventory with frozen
  counters documented as named limits, not edited. Agree with the lane.
- **discernment: improved** — three mistakes mined with receipts and
  same-round executed fixes; the freeze instrument caught the round's own
  formatting defect at the attempt-1 freeze (receipt reproduced by me) and
  the supersede landed before any after-data (verified structurally from
  commit contents); the first flawed red receipt (exit-after-pipe) was caught
  in pre-landing review; fresh-start rulings re-derived against r43/r44/r45,
  and the r45 limit is structurally avoided (byte-identical counter both
  arms — verified); the Gate states its reject sample explicitly. Agree with
  the lane.

## 6. Standing-practice receipts (spot reads, consistent)

`c1-suite-tip-49.txt` (assertions=548, registered=70, unfiled=0, exit 0),
`ntfs-exclusion-check-tip.txt` (count=6, tolerance not widened),
`idx-repair-base-49.txt` (repairable→AFTER rows=6 unexpected=0, exit 0),
`idx-repair-freeze2-49.txt` (fail-closed REFUSAL on the in-progress tool
edit, nothing repaired, exit 1 — disclosed in the report), `census-before.txt`
(58 W04, rows 195, conf rc-2 verdict recorded inside). All match the report.

## 7. Routed defects / notes for the lane and operator (status-neutral)

1. **S267 re-open receipt wording** (this round's artifact, no row changed):
   "zero occurrences of 'histor*'" is exact for page content but not for the
   raw page bytes (one footer boilerplate occurrence: "History and License").
   Fix next round if the receipt class is reused: name the counting method
   (content area, tag-stripped) or paste the command, per the round's own
   quote-counting practice. Decision unaffected; S267 stays rejected.
2. **Census conf-form rc 2 on this host** — carried, operator-owned (L0
   round-48); the round handled it exactly as its r48 precedent documents.
   Nothing new for the lane.
3. **SHONEN boxes for the operator:** all four boxes carry `[~]` with
   resolvable evidence pointers, and this verifier finds them checkable by a
   non-author from the committed artifacts (SKILL decision tables + registry,
   LOG + receipts, self-contained prereg/counter/controls re-derived this
   session, PROVINCE untouched). Per duty this verifier writes no `[x]`;
   flagging for the operator's promotion review that the boxes look
   non-author-verifiable.

## 8. Closure decision

One declared claim (C1, calibration), re-measured end-to-end by this
verifier with independent runs at both revisions; no axis harmed; trends
agree with the lane's; conformance clean (minor notes above). Verdict:
**souji round 49 — ok, admitted**.
