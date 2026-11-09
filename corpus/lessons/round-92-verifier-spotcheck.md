author: hyaku closure (non-author integrator, @m_zfl)

# Round 92 verifier spot-check — souji (non-author, hyaku closure)

Lane: `souji-shokunin`, branch `master`. Lane base `5339b2ac79f81aa446f6a2cd4700321cf4982fd3` (r91 closed); lane
HEAD after the round `e112cc73756d480dc2699fcaa202cab88c38cfbc`. Report `.ufo/reports/round-92/souji.md`.

Dispatch/complete digest copied from this round's closure prompt (mutable `.ufo/watchdog.log`):

`2026-11-08T20:31:45-03:00 launch souji round=92 pgid=78373 driver=hyaku-inline attempt=1`
`2026-11-08T21:09:26-03:00 lane-dead-no-report souji round=92; retry same round (hyaku-inline attempt=1: L1 ended without a landed report: FAIL report_of (missing, unchanged, no SHONEN heading, or < 400B): .ufo/reports/round-92/souji.md)`
`2026-11-08T21:09:28-03:00 launch souji round=92 pgid=3725876 driver=hyaku-inline attempt=2`
`2026-11-09T00:25:30-03:00 complete souji round=92; hyaku-inline attempt=2`

## 1. Step-1 conformance

- **Report identity: PASS.** `git log --format='%an <%ae> %H %ci' -- .ufo/reports/round-92/souji.md` ->
  `souji-shokunin <souji@shokunin.local> 652ef9adea424872ae86762c4588b3383a074fdf 2026-11-09 00:25:04 -0300`. Not a
  marker: it names committed instruments, a population, a tool repair, receipts, a source row and a checkable tip.
- **`SHONEN` heading: PASS.** One `## SHONEN` heading, four `[~]` lines each with a pointer; `grep -c '\[x\]'
  SHONEN.md` -> 0; `SHONEN.md` unchanged in the range.
- **Cited lane commits: PASS.** `git cat-file -e` and `git merge-base --is-ancestor <h> master` exit 0 for
  `44d45b44`, `1d015a2d`, `e8d31f06`, `e5059168`, `d64c0260`, `a3bcd9d6`, `e112cc73` and the base; `git log
  5339b2ac..e112cc73` lists exactly these seven commits, all by `souji-shokunin`, in the order P1 -> P2 -> F ->
  after receipts -> wave/ledger -> misroot sweep -> ledger format fix. F (`e8d31f06`) contains only the
  preregistration.
- **Lane state: PASS.** `scripts/hyaku/jj-lane.sh state` -> `branch=master local=e112cc73… remote=e112cc73…
  ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` empty (also after every re-run
  below); `git ls-remote origin refs/heads/master` -> `e112cc73756d480dc2699fcaa202cab88c38cfbc`.
- **Report lands last: PASS.** Lane tip 00:24:50 -0300, report commit 00:25:04, driver `complete` 00:25:30.
- **Prompt contract: PASS.** Every one of the 105 non-placeholder lines of `templates/round-prompt.md` occurs in
  `.ufo/prompts/souji-round-92.md` (Python line-containment check, 0 missing), followed by hyaku addendum §6, §7
  and §8 (pre-file ledger).
- **Retry disclosure: PASS.** Attempt 1 died before any wave and left uncommitted instruments; attempt 2 re-ran and
  adopted them (preregistration INHERITED paragraph; report Extras). r92 is attempt 2's single round.
- **r91 routed defects: ANSWERED.** (1) invalid-lead collision -> C2 repair, KFF14/15/16; (2) KFF13 by `ast` with a
  both-directions self-check; (3) the alternative-edit survivor search ran (270 mutants) -> C1; (4) RFC 3629
  re-gate -> the rule is grounded on S355 (Table 3-7), RFC 3629 §4 compared (lesson Gate); (5) the r92 population's
  comment line names the r90/r91/r92 rows.
- **Status-neutral conformance notes.** (a) S355's `anchor` cell was edited in place (`id="G7404"` ->
  `id="G27506"`, `git diff e5059168 d64c0260 -- corpus/SOURCES.md` shows one `-`/`+` S355 pair); CORPUS.md
  SOURCES rule 2 lets only `status`/`recheck`/`used-by` change in place. Mitigation: the row was born this round,
  the correction precedes filing and is logged old->new in the lesson Gate, and the new anchor is correct (section
  5). (b) One seat report (`R92ScoutSources.md`) was written to the fleet root and swept into the lane byte-exact
  (lesson M5); the fleet root holds no souji r92 leftover now. (c) The pre-file ledger first ran FAIL (format) and was
  fixed before filing (`e112cc73`).

## 2. Pre-file falsification ledger (addendum §8, Amendment 59)

```
python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 92
PREFILE-FALSIFICATION: pass claims=2 rows=21 attack_seats=7 findings=0
EXIT=0
```

Both claims of `.ufo/waves/round-92/claims.json` are covered; 13 seat artifacts exist under `w1/` (13 `*.md`,
`w1-results.json` present). Five rows are `falsifies-wording`, each naming `plans/round-92.md`:

| row | real? | reconciled? |
|---|---|---|
| C1 `R92MutC1.md` + `harness-E1-ok-relaxed-r92.txt` — the kill rule scores crashes as kills; an alternative line-552 edit (E1) survives both populations | real (the kill rule is "non-zero exit", and binding 47 edits is not binding their clauses) | yes: A3 narrows "kills" to the 47 listed edits, none a crash; every C1 number re-derives below |
| C2 `R92MutC2.md` + `fixture_D_len_ge1.txt` — surrogatepass / multi-character span / forward-head forgeries pass the frozen fixture 20/20 | real (KFF18's prefix/suffix property tolerates an over-eager cut) | yes: A1 narrows the one-sequence sentence to source reading + sweep; my independent sweep (section 3) supports the property of the filed tool |
| C2 `R92ScoutSources.md` — S355 anchor `G7404` is the §3.9 heading | real (re-opened: `G7404` wraps "3.9 Unicode Encoding Forms", `G27506` wraps "Table 3-7. Well-Formed UTF-8 Byte Sequences") | yes: A4 corrects the cell (see note 1(a)) |

No row is spurious and none is unreconciled.

## 3. Per-claim re-check

Re-measured by me on the committed lane tree at `e112cc73` (clean, detached at the tip), work roots under
`/fast/scratch/hyaku/souji-r92-close/` (never `/tmp`). These are the claims' counting instruments, not a registered
lane gate. Pins re-derive: counter `fd0a8e24…`, r92 population `f66341fc…`, targets `5a8f6087…`, tool `fc0e35c2…`,
fixture `2c9bd76c…`, r91 before-tool `21e5c740…`.

### C1 — calibration 7 (re-measured; VERIFIES as narrowed A3)

```
c1-survivor-search.py ... --population census/round-92/c1-false-rows.tsv --jobs 8 --ids census/round-92/c1-targets.json
SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=47 survived=0          EXIT=0
control, same command with --population census/round-91/c1-false-rows.tsv
SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=0 survived=47          EXIT=0
pristine c1-false-row-harness.py --population census/round-92/c1-false-rows.tsv
ROW LD4r where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/0 got=MOVED rc=0 match=yes
SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0                                    EXIT=0
```

Structure: `cmp -n <size r91>` -> the r92 population is the r91 file byte-for-byte; `diff` -> `65a66,67` (one comment
line, LD4r). Targets 47 ⊂ r91 survivors 124; targets ∪ `records/c1-residual-survivors.json` (77) = the 124, disjoint.
The full census receipt reads `generated=270 ambiguous=9 uncompiled=0 hung=1 scored=260 killed=136 survived=124`
(evidence-verified, not re-run: 270 harness runs). The 47 are by construction what LD4r kills (stated limit vi);
the committed control and R92ExecC1Cause's 14/14 per-target attribution are what make it more than its
construction. **Verdict: C1 verifies as narrowed; calibration `improved`.**

### C2 — operability 8 (re-measured; VERIFIES as narrowed A1)

```
r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before controls/c2-before-tool.py
  CASE KFF14/15/16/18 tool=pass before=fail ; SUMMARY cases=20 tool_pass=20 before_pass=16          EXIT=0
control, r91 tool as both arms: KFF14/15/16/18 tool=fail ; SUMMARY cases=20 tool_pass=16 before_pass=16 EXIT=1
c2-forgery-probe.py: F1 18/20 F2 19/20 F3 18/20 F4 18/20 N0 16/20 ; FORGERY-SUMMARY forgeries=5 rejected=5 positive=pass EXIT=0
round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py : SUMMARY rows=12 mismatches=0 errors=0 EXIT=0
```

Independent probes (my scripts, importing each tool by path):
- **A/B pair rebuilt** (`p*100 + q*6 + F0 80 61 {C2|62} 85 + s*95`, 206 bytes, F0 just before the tail cut): r91
  tool `equal=True`, both tails `…\x85sssssss` (the collision); filed tool `equal=False`, A `…\x80a\u0085`, B
  `…\x80ab\x85s`.
- **Random sweep**, 60,000 payloads (seed 92, 201–240 bytes over 15 well-formed and ill-formed tokens incl.
  surrogate, overlong, F4 90, F5 leads): checks (i) head is a prefix and tail a suffix of
  `_escape_text(_decode_record(raw))`, (ii) a moved cut spans exactly one strictly-decodable character straddling
  the cut (computed without the tool's helper). Filed tool: `prefix_suffix_violations=0 move_violations=0`. r91
  tool: `238` and `27781`. Check (ii) is the over-move direction A1 says the frozen fixture misses; it holds for the
  filed tool on this sweep, which supports the narrowed sentence (source reading + sweep), not the frozen predicate.
**Verdict: C2 verifies as narrowed; operability `improved`.**

### Axis-harm check

`git diff 5339b2ac e112cc73 -- SCORECARD.md` is purely additive (Round 92 measurements, two capability rows,
`### Planned (r93)`); no axis score changed. `git diff --numstat` over `SKILL.md PROVINCE.md SHONEN.md` prints
nothing; `corpus/QUALITY.md` +7/−0 (Q167, Q168, each with a lesson and an able-to-fail test);
`tools/souji-record-agreement.py` +33/−37 (the cut helpers only); `corpus/SOURCES.md` one appended row (S355).
No sibling lane touched. No owned axis harmed.

## 4. Axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | improved | 47 previously surviving single-token counter edits now exit 1 with a row mismatch (47/0 vs control 0/47, re-measured), pristine 64/0 with LD4r rc=0; narrowed to the edits (A3) |
| operability | improved | the A/B invalid-lead collision is repaired (reproduced on the r91 tool, absent on the filed tool), fixture 20/20 vs 16/20, forgeries 5/5, K4 12/0/0, independent 60k sweep 0/0 vs 238/27781; narrowed A1 |
| depth | unchanged | `SKILL.md` untouched |
| coverage | unchanged | `PROVINCE.md` untouched |
| freshness | unchanged | no drift re-verification claim |
| adjacency | unchanged | R92Connector §1: no sibling owns the surface |

## 5. Discernment spot-check (`corpus/lessons/round-92.md` `## Gate`)

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
-> `souji ok`, `EXIT=0` (W04 only). Rows (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`):
276 at `5339b2ac`, 277 at `e112cc73`.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S355 Unicode 18.0.0 ch. 3 §3.9 D84a–D86 / Table 3-7 (admit) | admit, tier A `docs`, `mined` | live `https://www.unicode.org/versions/latest/core-spec/chapter-3/` -> HTTP 200, redirect to `…/Unicode18.0.0/core-spec/chapter-3/`, 428,731 bytes, sha256 `f9e158a6…`, `cmp`-identical to `census/round-92/srcs/unicode-ch3.html` | agree | primary standard; Table 3-7 is exactly the well-formedness set the strict-decode helper implements; scope excludes U+FFFD practice; used-by `corpus/knowledge/utf8-window-well-formed-cut.md` exists and opens `source: S355` |
| §3.9 D93b maximal subpart (reject sample, not filed) | reject with flip condition | same live page: quote found once (18 words, normalized offset 145946) | agree | D93b governs how far U+FFFD substitution advances; the filed tool never substitutes (`grep -E 'FFFD|"replace"'` on the tool -> nothing) and no r92 sentence uses U+FFFD; flip condition is concrete |
| S355 registry quote (`corpus/SOURCES.md` S355 anchor cell) | ≤25 words? location? | live page, tag-stripped whitespace-normalized | agree | "Ill-formed code unit subsequences do not overlap with minimal well-formed code unit subsequences." — 13 words, occurrence 1, at offset 133443, inside D86's body (D86 at 132318, next D-number at 133541); the corrected `id="G27506"` wraps the Table 3-7 caption, `G7404` the §3.9 heading |

Both sampled gate decisions agree. `## Mistakes` M1–M5 carry evidence and fixes (M1/M2 shown able to fail; Q167/Q168
ground in them).

## 6. Trend verdicts

- **expansion: improved.** S355 (tier A, `mined`, re-opened live byte-identical) grounds a new knowledge entry on
  ground the lane did not hold (well-formedness vs the S354 sequence unit); a new capability (bounded single-token
  mutation census) and a well-formed-cut capability, both with passing demonstrations I re-ran.
- **quality: improved.** The r91 residual is repaired and measured (re-measured 20/20 vs 16/20; my 60k sweep 0 vs
  27,781 move violations); 47 surviving counter edits bound; Q167/Q168 land; residuals (over-move forgeries, 77
  survivors, E1, search robustness) named and routed; no admitted entry fails its re-check.
- **discernment: improved.** Three wave falsifications narrowed in `plans/round-92.md` before filing (A1, A3, A4),
  the target-selection construction disclosed as limit (vi) with a committed control; my sampled admit and reject
  both agree.

## 7. Routed defects for r93

1. **C2 maximality case** (A1): a fixture row that turns surrogatepass / multi-character span / forward-head
   forgeries red (e.g., the excerpt equals the exact one-sequence window on boundary payloads). Lane-planned.
2. **C1 E1 binding row** (A3): a ledger-resolve run with exactly one unresolved item asserting rc 1; classify or
   bind the 77 residual survivors and name equivalent mutants.
3. **Survivor-search robustness** (R92Sentinel M1/L1/L2): cleanup on SIGKILL/SIGINT, bare-`/tmp` guard.
4. **SOURCES rule 2** (note 1(a)): an anchor correction is a new row (`supersedes S0NN —`) or the lane states, in
   the lesson, why a same-round unfiled row is corrected in place; do not edit non-mutable cells silently.
5. **Seat write scope** (M5): seats must write wave artifacts under the lane, never the fleet root.

## 8. Closure verdict

Both declared claims verify under their recorded narrowings (C1 A3, C2 A1), all predicate and control numbers
re-measured by me; no owned axis harmed; the three learning trends `improved`. Conformance notes are status-neutral.
The four `SHONEN` boxes carry pointers a non-author can check; promotion stays operator-owned.
