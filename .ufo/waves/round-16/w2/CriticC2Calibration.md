# CriticC2Calibration — round 16 w2 (critic, calibration)

Seat: SoujiR16.CriticC2Calibration (leaf critic). I own only this report.
Target: C2 as a **calibration** claim. AXES.md:15 defines calibration as "Self-assessment quality: gaps named honestly, confidence graded, overreach caught", with the signal that SHONEN/SCORECARD entries match observed repo state.
Reviewed bytes:
- `tools/souji-landing-gate.py` and `tests/fixtures/r16-landing-gate.py` at a6ec781. `git diff --stat a6ec781 163158a` shows neither file changed.
- The lesson, SCORECARD and QUALITY at 163158a. HEAD moved from a6ec781 to 163158a while I was reviewing.
- `corpus/lessons/round-15-verifier-spotcheck.md`.

Method:
- Static review.
- In-memory replication. I copied the gate's channel and carry logic verbatim (gate:71-85 and 239-356) into a Python cell and fed it committed bytes read with `git show` / `git ls-tree`.
- **I did not execute the gate, its selftest or its fixture** (no ALLOWED-EXEC on this item). Every gate-output statement below is either quoted from a named report or derived by that replication. Derived statements are marked [REPLICATED].

## Verdict

**Partial.** The parse check is a real mechanism with informative negatives, and the lesson scopes C2 honestly in places: it rejects the "disclosure enforcement" label, and it says r14 was "rejected for behavior, not landing claims". The headline before→after, however, is mostly tautological:

- "before 0 of 3 → after 3 of 3 on b410186" is **true by construction**. The gate was written from those three defects (gate:4-14). The replay is its training instance, and "before 0" is the gate's own absence. The real before is 3/3, found by hand by the outside closure.
- "0 false findings on r13/r14" is **honest but vacuous** for two of the three check families:
  - Carry check: 0 markers exist on either replay.
  - Pin check: every r13/r14 pin is self-referential, and the only `measured_commit` is dangling, so LG-FROZEN-MEASURED contributes 0 checks.
  - Both rates were tuned on these same replays.
- "15 held-out fixture cases" **overstates**. The 15 are:
  - 1 training replay;
  - 1 meta-check of the fixture itself;
  - 13 synthetic spec-conformance cases. Their spec is the W1 critic's acceptance list, and one case's assertions were flipped in the same commit that narrowed the gate.
- On the one round with STATUS discipline that the gate was not designed from (the r16 w1 seats), recall on defect-reporting STATUS lines is **0/11** [REPLICATED]. The only marker it raises there is a quotation.
- Q25(b), Q25(c) and the SCORECARD capability row promise checks the gate does not perform: dangling `measured_commit` and the `resolved@<rev>` provenance. That is self-assessment overreach on the calibration axis itself.

Operability is not harmed: the gate is additive and read-only. The defects are fixable. The only one the judge must treat as a tradeoff, not a fix, is that no substring check can prove disclosure quality.

## Counterexamples

### CX1 — The 3/3 replay is the training set (tautology)

- `tools/souji-landing-gate.py:4-14` (docstring): "Mechanically re-derives the three round-15 landing defects the non-author closure found by hand". The replay case `tests/fixtures/r16-landing-gate.py:229-235` asserts exactly those three ids on exactly that revision.
- "Before: no lane mechanism detected any of the three" (`corpus/lessons/round-16.md`, C2 decision) holds because the gate did not exist. It is not a measured baseline of a competing mechanism.
- What was actually detected before was 3/3, by hand, by the closure (`round-15-verifier-spotcheck.md:41-42,56,30`). The calibration gain is that this detection moves from outside to inside the lane. That is a capability. It is not a measured calibration improvement until the gate catches something on a landing it was not written from.

### CX2 — The false-positive rate was tuned in-sample, twice, including on the author's own landing

- Gate comment `tools/souji-landing-gate.py:66-70`: the first draft "flagged 10 benign lines on each admitted round-13/14 replay". The second "matched 42 lines at the round-16 landing". Both were dropped.
- `.ufo/waves/round-16/w1/LandingGate.md:62,81` records the pre-narrowing replays: b410186 `findings=34` and cc21683 `findings=10`. After two narrowings the claim reads 5 and 0.
- The "0 false findings on r13/r14" figure is therefore the objective the vocabulary was fitted to, not a held-out measurement.
- The second narrowing (`git diff 7a79dc2 a6ec781`: `PHRASE_MARKER_RE` deleted) was made when the gate was red on the round being graded. Moving the threshold of your own gate at that moment is the pattern calibration exists to catch. The rationale (quotations are noise) may be right, but the correction should have been quotation exclusion, which CriticGateVacuity F2 had proposed. Instead the whole prose channel was deleted, and the surviving channel still flags a quotation (see CX4).

### CX3 — The r13/r14 negatives are vacuous for carry and pins [REPLICATED]

| rev / round | wave reports | STATUS lines (outside fences/tables) | gate markers | pin files | measured checks |
|---|---|---|---|---|---|
| a31642d / 13 | 32 | 1 (`authored`) | **0** | `r13-cert-frozen`: 7 keys, all frozen-dir-local | 0 (no record) |
| cc21683 / 14 | 32 | 0 | **0** | `r13-cert-frozen` + `r14-cache-frozen` (`dependency.txt`, `record.json`), all frozen-dir-local | 0: `measured_commit` `0123456789abcdef…` is dangling and skipped silently (gate:467-476) |
| b410186 / 15 | 64 | 16 (14 `design-only`, 1 `scout`, 1 `incomplete`) | 1: `ConfigRepair.md:7` | | |
| 163158a / 16 | 63 | 56 | 1: `ConnLogConvention.md:385` | | |

- **Carry:** 0 markers on r13 and r14, so "0 false findings" exercises nothing. The STATUS convention barely existed before r15.
- **Pins:** self-contained pins can fail only by in-place edit (CriticGateVacuity F5 already noted this).
- **Parse:** the only informative negative family. About 15 SKILL-cited scripts parse (LandingGate.md:124, `checked_reg=15` at cc21683).

The claim should say which family the zero comes from.

### CX4 — Recall 0/11 on the r16 seat round; the one hit is a quotation [REPLICATED]

- Under its own `## Seat-reported failures` heading, L1 carried by hand 11 r16 w1 STATUS lines that report defects or open items. The heading's own wording: "every failure-channel STATUS line and every non-ok STATUS line that reports a defect".
- The gate's channel marks none of them. First words: `residual`, `survived`, `probe`, `f1`, `source`, `` `b5187351…` ``, `r16`, `live`, `gate`, `skeleton`, `findings`. Examples:
  - `MutateDirtyFilters.md:5` (a surviving mutant);
  - `SentinelCommandExec.md:91` ("F1 is open … does not hold");
  - `CriticNamespaceWeakening.md:5` ("definite soft-refusal precedence defect");
  - `SrcGitCheckAttr.md:113` (a PROBE RULE breach).
- The **only** r16 marker is `ConnLogConvention.md:385`, `    ## STATUS: INCOMPLETE — file has an unresolved syntax error`. It is a 4-space-indented (markdown code block) quotation of r15's line, which is the very false-positive class used to justify narrowing.
- Precision 0/1, recall 0/11.
- Across all four revisions, the carry check has fired on exactly one string: r15's heading line, once as the original and once as its quotation.

### CX5 — The vocabulary is attributed to a contract that did not require it

- `tools/souji-landing-gate.py:62-66` says the first word must be "in the pinned failure vocabulary the wave contract requires seats to use". It is not.
- The r16 **w1** contract (`.ufo/waves/round-16/w1-spec.json`) says "any known failure on a line starting `STATUS:`", which is free vocabulary.
- A fixed vocabulary (`STATUS: FAIL — …` or INCOMPLETE/BLOCKED/PARTIAL) appears only in `w2-spec.json`. No r13/r14/r15 contract had it.
- Every replay corpus was therefore measured against a rule its authors were never given. The gate's set also differs from the w2 contract: it adds `known`, `harmed`, `red`, `unrun`, `regression` and `error` (gate:72-78).

### CX6 — The r15 replay hit rests on one exact line format [REPLICATED]

- After narrowing, `ConfigRepair.md` yields one marker (line 7). Before narrowing it yielded several (LandingGate.md:69-71: lines 7, 9, 11 and 124).
- One-token variants of line 7 are all **silent** under the copied logic. Each states the same failure:

```text
## STATUS: `INCOMPLETE` — …        (backticked word; norm_line is not applied before the vocabulary test)
## STATUS: INCOMPLETE, …           (trailing comma)
## STATUS: INCOMPLETE. …           (trailing period)
## STATUS: (INCOMPLETE) …
## STATUS - INCOMPLETE — …         (hyphen; en-dash also silent)
- STATUS: INCOMPLETE — …           (list item)
> STATUS: INCOMPLETE — …           (blockquote)
STATUS: NOT OK — census does not parse
STATUS: unverified candidate — bash -n fails   (r15's own understatement wording)
STATUS: does not parse
```

- The 3/3 therefore measures whether the r15 seat happened to type `## STATUS: INCOMPLETE —`, not whether the lane detects uncarried known failures.

### CX7 — `resolved@<hex>` is accepted without provenance (false provenance)

- The carry token is `(?i)\bopen\b|resolved@[0-9a-f]{7,}` (gate:83), tested by regex only (gate:338). The hex is never resolved and never checked as an ancestor of REV. `git rev-parse --verify deadbeef^{commit}` → unresolved, yet `… — resolved@deadbeef` satisfies carry [REPLICATED].
- The gate's own selftest certifies this. `carried-resolved` (gate:903-912) writes `resolved@cbf688ab2ab2` into a fresh synthetic repo where that commit cannot exist, and asserts exit 0.
- Fixture case 8's comment (`tests/fixtures/r16-landing-gate.py:370-372`, "a resolved@ disposition pointing at a real ancestor commit") implies a property the gate does not check.
- The token is searched on the whole lesson line, needle included. A seat line containing the word "open" (e.g. `STATUS: BLOCKED — open question …`) therefore satisfies carry when pasted verbatim, with no disposition at all [REPLICATED].
- Q25(c) says "`resolved@<rev>`", which reads as a revision. The gate accepts any hex.

### CX8 — Dangling or absent `measured_commit` passes silently; Q25(b) overclaims

- gate:464-476: a non-hex or unresolvable `measured_commit` sets `measured_ok = False` and "contributes no checks". An absent `measured_commit` or absent `record` does the same. No finding is emitted either way.
- The selftest green world uses exactly that. `_frozen_world` sets `"measured_commit": "0" * 40` (gate:725), and `clean-pass` (gate:784) asserts exit 0.
- The real corpus has a live instance: cc21683 `r14-cache-frozen/record.json` `measured_commit` `0123456789abcdef…`.
- Q25(b) (QUALITY.md, r16) states "a record's `measured_commit` must hold the bytes the record pins". The gate enforces that only when the record cooperates.
- The record's own run digests (`runs.*.tool.sha256`, the `TOOL … sha256=` stdout line) are never compared with the pins. CriticGateVacuity F5/A9 asked for this and it is not implemented. A re-hash plus re-pointing `measured_commit` at REV therefore passes with no run.
- Today's r15 record is coherent: at 163158a, `runs.changed.tool.sha256` equals the pin `64a60fd0…` and `measured_commit` c6207bd resolves. That coherence is not what the gate proves.

### CX9 — LG-OPEN-ADMITTED is dodged by markdown, and the lesson is not the admission authority [REPLICATED]

- `ADMITTED_TRUE_RE` (gate:84) runs on raw lesson text. It returns False for `**admitted:** true`, `admitted: **true**`, `` `admitted`: true `` and `admitted: yes`, so bold, which this lane commonly uses, silences it.
- The r16 lesson records admission as "candidate admit". Admission actually lives in the closure and SCORECARD, so on real lessons this id effectively cannot fire.

### CX10 — Stale self-descriptions, and a fixture that co-evolved with the gate

- Fixture docstring `tests/fixtures/r16-landing-gate.py:21-25` still specifies "first word … outside the benign allowlist, plus parse/do-not-ship/snapshot_tampered phrase markers". That contradicts the gate and the fixture's own case 9.
- Selftest comment gate:883 ("STATUS failure + phrase") and gate docstring :13 ("STATUS/failure lines") are stale in the same way.
- In a6ec781, case 9 moved SeatC/SeatD from `need` to `absent` in the same commit that deleted `PHRASE_MARKER_RE`. The fixture was edited to agree with the changed gate.
- The only committed 15/15 transcript (`LandingGateFixture.md:29-45`) is from the **pre-flip** fixture: "5 rows (SeatA–E flagged)", line 63. The post-flip 15/15 claimed in SCORECARD has no committed transcript.

### CX11 — What "held-out" means here

- Cases 2–13 are CriticGateVacuity's acceptance list A3–A12 (`.ufo/waves/round-16/w1/CriticGateVacuity.md:113-127`), adopted as L1 steers and written into the gate spec. They are held out from the gate's *selftest*, not from its *specification*. They test conformance to the spec, not calibration on unseen data.
- The fixture contains no r13/r14 replay and no known-miss assertion (CriticGateVacuity A1/A2). The "0 on r13/r14" result is pinned nowhere, so a regression would be silent.

### CX12 — No committed run evidence for C2

- `git ls-tree 163158a census/round-16/` holds C1's `c1-matrix*.json`, `live-fleet*.json` and `seat-audit-w1.json`. There is no C2 artifact: no replay TSV/JSON, selftest transcript or fixture transcript.
- The replay counts (5 / 0 / 0), the 18/18 and the 15/15 exist only as lesson and SCORECARD prose ("replays in `corpus/lessons/round-16.md` Gate"). The gate has a `--json` writer (gate:594-636) and it was not used for evidence.
- A closure can verify these numbers only by rerunning.

## What holds

- **LG-PARSE-REG / LG-MISSING-REG / LG-PARSE-CHANGED** are real mechanisms:
  - stderr-as-finding catches the truncated here-doc (gate:205-209);
  - `compile()` replaces `ast.parse` (gate:213-221);
  - blob reads use `ls-tree` + `cat-file`, never `git archive`.
  W1 findings F6.2/F6.3 and F4 (exit 2 on a missing wave dir, `checked_reports`) are implemented. The parse negatives on r13/r14 are informative.
- **b410186 replay [REPLICATED for carry]:** under the copied logic, `ConfigRepair.md:7` is the single uncarried marker. At 163158a/round 16 the single marker is carried, so carry is green.
- **The lesson's scoping is calibrated** where it rejects "disclosure enforcement" and frames r14 as behavior-rejected. The Q25 text "A gate pass is consistency, not behavior" is accurate.
- **No other axis is harmed.**

## Impacted axes

- **calibration:** the claim. As worded, the before→after is tautological and the r13/r14 zeros are vacuous in two of three families. SCORECARD's capability row, Q25(b)/(c) and the fixture/selftest comments overstate what the gate checks, which is an overreach of exactly the kind AXES.md:15 says calibration must catch. Measured r16 recall on defect-reporting STATUS lines is 0/11.
- **operability:** unchanged. The gate is additive and read-only (it never executes repository code: gate:16-18, 192-231). I did not run `py_compile` on it. Parse status comes from the lane's own reports, not from this seat.

## Smallest safe corrections

1. **Reword the C2 claim (SCORECARD row 23, capability row 34, lesson C2 decision).** Suggested: "new landing-consistency gate; red on its training instance b410186; parse negatives on r13/r14 over N cited scripts; carry and pin families unexercised on r13/r14 (0 markers; self-contained pins; dangling measured_commit); 13 synthetic spec-conformance cases + 1 replay + 1 vacuity meta-check; r16 w1 STATUS-line recall 0/11 (vocabulary introduced in w2)". Do not call this "held-out", and do not count 3/3 as an improvement over a measured before.
2. **Gate, about 15 lines in total:**
   - (a) In LG-FROZEN-MEASURED, emit a finding when `record_sha256`/`record` is present but `measured_commit` is absent, dangling, or not an ancestor of REV (`git merge-base --is-ancestor`).
   - (b) Resolve every `resolved@<hex>` with `rev-parse --verify` plus an ancestor check; anything else counts as uncarried.
   - (c) Search the carry token only in the lesson line with the needle removed.
   - (d) Apply `norm_line` and strip `.,()` before the first-word test. Accept `-` and `–` separators and list/blockquote prefixes, or document that they are excluded.
   - (e) Treat 4-space-indented lines as code.
   - (f) Run `ADMITTED_TRUE_RE` on `norm_line(lesson)`.
   - (g) Print an advisory `STATUS_OTHER=k` count of STATUS lines whose first word is neither in the failure vocabulary nor benign, so the recall gap stays visible instead of silent.
3. **Fix the comment at gate:62-66.** The vocabulary is a w2 contract rule, applied retroactively to r13–r16w1.
4. **Fixture additions:**
   - pin the r13/r14 replays (exit 0, `checked_markers=0` asserted as such);
   - add a known-miss case using one r16 w1 line (e.g. `MutateDirtyFilters.md:5`);
   - add `resolved@deadbeef` → LG-SEAT-UNCARRIED;
   - add a dangling `measured_commit` → finding.
   Rewrite docstring :21-25 and selftest comment :883. Change selftest `_frozen_world` to use a real commit and stop asserting green on `0`×40.
5. **Commit C2 run evidence:** `--json` for each replay, plus selftest and fixture transcripts under `census/round-16/`.

STATUS: ok — the review is complete. The gate, selftest and fixture were not executed (item has no ALLOWED-EXEC); results marked [REPLICATED] come from an in-memory verbatim copy of the gate's channel/carry logic over `git show` bytes, not from the tool.

Tool installs/updates: none.

## Commands

Shell, verbatim:
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %ad %s' --date=iso -- tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py && git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only HEAD census/round-16/ && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/ConfigRepair.md`
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff 7a79dc2 a6ec781 --stat && git diff 7a79dc2 a6ec781 -- tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py && git ls-tree -r --name-only HEAD .ufo/waves/round-16/ && git ls-tree -r --name-only a31642d .ufo/waves/round-13/ && git ls-tree -r --name-only cc21683 .ufo/waves/round-14/`
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:AXES.md && …` (failed at the first command: rc 128, path absent; nothing after it ran)
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree --name-only HEAD && git ls-tree --name-only HEAD corpus/lessons/round-16.md corpus/lessons/round-15.md && git ls-tree --name-only HEAD tests/fixtures/r15-preservation-frozen/ && git show HEAD:tests/fixtures/r15-preservation-frozen/expected.json`
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-preservation-frozen/record.json && git show HEAD:corpus/lessons/round-16.md`
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --format='%h %ad %s' --date=iso -8 && git log --format=%h -1 -- corpus/lessons/round-16.md && for h in 0a70bef c6207bd a6ec781 cbf688a deadbeef; do git rev-parse --verify --quiet "$h^{commit}" || echo "$h unresolved"; done`
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat a6ec781 163158a && git diff 58ace9f 163158a -- SCORECARD.md && git show 163158a:corpus/QUALITY.md`
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 163158a:.ufo/waves/round-16/w1-spec.json | python3 -c "<regex excerpt of STATUS text>" && git show 163158a:.ufo/waves/round-16/w2-spec.json | python3 -c "<regex excerpt of 'STATUS: FAIL' text>" && git ls-tree --name-only 163158a census/round-16/` (the inline python3 only extracted text from JSON on stdin)

In-process Python (eval kernel): `subprocess.run(["git","-C",LANE,"show",f"{rev}:{path}"])` and `git -C LANE ls-tree -r --name-only <rev> <prefix>` for a31642d/.ufo/waves/round-13/, cc21683/.ufo/waves/round-14/, b410186/.ufo/waves/round-15/, HEAD/.ufo/waves/round-16/, a31642d|cc21683 tests/fixtures/, and the named frozen expected/record files. Verbatim copies of the gate regexes and logic were applied to those bytes and to the literal probe strings in CX6, CX7 and CX9. No lane code was imported or executed, and no /var/tmp scratch was created.

Non-shell reads (exact files): `skill://godspeed`; `corpus/lessons/round-15-verifier-spotcheck.md`; `tools/souji-landing-gate.py` (1-113, 179-603, 639-1005); `tests/fixtures/r16-landing-gate.py` (1-63, 196-530); `.ufo/waves/round-16/w1/{LandingGate,LandingGateFixture,CriticFixtureOverfit,CriticGateVacuity}.md`; `/home/vgpnk/Projects/shokunin/AXES.md`; grep over spilled tool-output artifacts only.
