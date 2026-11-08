author: hyaku closure (non-author integrator, @m_zfl)

# Round 91 verifier spot-check — souji (non-author, hyaku closure)

Lane: `souji-shokunin`. Lane base `681f6c72b242d410d0e8654efadb2a1553fb111d` (the r90 verifier spot-check commit);
lane HEAD after the round `9deaefda2853a0b78482f714166523c654b128eb`. `scripts/hyaku/jj-lane.sh state` reads
`branch=master local=9deaefda2853a0b78482f714166523c654b128eb remote=9deaefda2853a0b78482f714166523c654b128eb
ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` is empty and
`git ls-remote origin refs/heads/master` prints the same tip. Report `.ufo/reports/round-91/souji.md` is committed in
the fleet repo by the lane identity (`git log --format='%an %H' -- .ufo/reports/round-91/souji.md` -> `souji-shokunin
4af415c3f80fb104975f5a06d051cac441db2c66`, committed 20:12:17 -0300, contained in `origin/master`).

Dispatch/complete digest copied from this round's closure prompt (mutable `.ufo/watchdog.log`; the four lines are
present at lines 3380, 3400, 3403 and 3407):

`2026-11-08T12:31:50-03:00 launch souji round=91 pgid=2527681 driver=hyaku-inline attempt=1`
`2026-11-08T13:51:17-03:00 lane-dead-no-report souji round=91; retry same round (hyaku-inline attempt=1: L1 ended without a landed report: FAIL report_of (missing, unchanged, no SHONEN heading, or < 400B): .ufo/reports/round-91/souji.md)`
`2026-11-08T19:48:13-03:00 launch souji round=91 pgid=53479 driver=hyaku-inline attempt=2`
`2026-11-08T20:12:32-03:00 complete souji round=91; hyaku-inline attempt=2`

## 1. Step-1 conformance

- **Report identity and path: PASS.** Authored and committed by `souji-shokunin <souji@shokunin.local>`. It is not
  a marker: it names committed instruments, receipts, a population, a tool repair, a source row and a checkable tip.
- **`SHONEN` heading: PASS.** `grep -c '^## SHONEN'` -> 1; four `[~]` lines (`grep -c '^- \[~\]'` -> 4), each with
  a resolvable pointer. `SHONEN.md` is unchanged in the range (`grep -c '\[x\]' SHONEN.md` -> 0).
- **Cited lane commits: PASS.** `git merge-base --is-ancestor <h> master` exits 0 for `7fb865d8`, `d287d3de`,
  `a703bcb7`, `28368806`, `db0a904a`, `9deaefda` and the base; `git log 681f6c72..9deaefda` lists exactly these six
  commits, all by `souji-shokunin`, in the order P1 -> control -> freeze F -> after receipts -> wave -> census-after.
- **Lane state: PASS.** `ahead=0 behind=0`, tracked/untracked 0, clean tree; remote equals local.
- **Report lands last: PASS.** Lane tip committed 20:06:53 -0300; report commit 20:12:17; driver `complete` 20:12:32.
- **Prompt contract: PASS.** `.ufo/prompts/souji-round-91.md` up to `## 6. Campaign addendum` equals
  `templates/round-prompt.md` rendered with `{{LANE}}=souji`, `{{ROUND}}=91`, `{{FLEET_ROOT}}`, `<lane>-repo` ->
  `souji-shokunin` and the 235-character `souji` axes string (prefix and suffix compared byte-for-byte in Python),
  followed by hyaku addendum section 6 and section 8 (pre-file ledger).
- **Retry disclosure: PASS.** Attempt 1 died after landing four commits; attempt 2 re-verified and reused them,
  launched no wave, and says so (report Extras "Inherited state"). The replay `.ufo/waves/round-91/l1a2-replay.txt`
  carries all five predicate/control lines with `EXIT=0`.
- **Round shape: PASS with a status-neutral note.** One v1 wave, 13 seats (band 8–16); planned attack share 4/13 =
  30.8 % under the addendum's four roles. Four seats died on provider errors (R91Critic, R91Revenger 429;
  R91Sentinel 429; R91MutCounter 400 then `permission_denied`), each with a committed dead-seat record under
  `.ufo/waves/round-91/w1/dead-seats/`. The settled attack share is 2/13 = 15 %, below the 25 % floor, but the
  addendum forbids replacing a dead seat and the report states both figures; the practical cost is that C1's
  alternative-edit survivor search (the mutation-tester's job) never ran — routed below.
- **r90 routed defects: ANSWERED.** Claims path now cited as `.ufo/waves/round-91/claims.json` (exists); one
  attack-share definition with the broader `ATTACK_ROLES` figure labelled separately; the r89 design-only capability
  row is annotated `SUPERSEDED r90` in `SCORECARD.md` (seen in the diff); the narrowed r90 instrument work is this
  round's C2.

## 2. Pre-file falsification ledger (addendum section 8, Amendment 59)

```
python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 91
PREFILE-FALSIFICATION: pass claims=2 rows=18 attack_seats=7 findings=0
EXIT=0
```

Both claims in the frozen `claims.json` are covered; the four dead attack seats each have a `neutral` row pointing
at their dead-seat record (the lane's negative control `prefile-negative-control.txt` shows the gate fails with
`findings=4` without them). Eight rows are `falsifies-wording`, every one names `plans/round-91.md`. Adjudication:

| row | real? | reconciled? |
|---|---|---|
| C1 `R91ReviewerC1` / `R91ExecC1Harness` / `R91ExecC1Battery` — STATED LIMITS (iii)'s premise ("base run is not all-resolved … exit 1 is expected") is false: LD4's base run is 35/35 resolved, rc 0 | real (three seats agree; the limit sentence is a rationale, not a number) | yes: A1 narrows the sentence, routes an `rc=0` assertion to r92; no C1 number moves — my re-run reproduces every C1 number |
| C2 `R91ExecC2Tool` repro + `R91Scribe` cut-edge probe — `_cut_tail` over-advances on a truncated/invalid lead, re-creating the byte/character collision | real: I rebuilt payloads A and B from the repro (sha256 `f639d877…`, `b53080a7…`, identical to the receipt) and the committed tool prints equal cells for both (`CELLS_EQUAL=True`, one `\x85`) | yes: A2(a) narrows C2 to valid UTF-8 payloads and routes the fix |
| C2 `R91Connector` §6 — "valid" is structural, not RFC validity (overlong/surrogate/F5–F7 leads pass the lead test) | real | yes: A2(a) states the lead test is structural |
| C2 `R91ReviewerC2` / `R91ExecC2Fixture` — KFF13 is a literal-substring scan; a spaced `def _one_line (` scores 15/15, a docstring mention false-fails | real | yes: A2(b) narrows the KFF13 clause; `ast`-based check routed |

No row is spurious and none is unreconciled. C2 therefore verifies only under its A2 narrowings, which the report
states; C1's narrowing touches a limit sentence, not the claim.

## 3. Per-claim re-check

Re-measured on an exported tree (`git -C souji-shokunin archive 9deaefda… | tar -x` into
`/fast/scratch/hyaku/souji-r91-close/tree`), work roots empty directories beside it, never `/tmp`. These are the
claim's counting instruments, not a registered lane gate; the lane repo was not written (`status --porcelain` stays
empty). Every pinned sha256 re-derives: counter `fd0a8e24…`, harness `5c6a1cf9…`, battery `5f717a1b…`, mutants
`3c26051e…`, r91 population `fdc3d238…`, r90 population `d64d7695…`, tool `21e5c740…`, before-arm `d095b52f…`,
fixture `f815abbc…`, variant probe `0610c5d2…`.

### C1 — calibration 7 (re-measured; VERIFIES)

```
python3 -B census/round-91/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --mutants census/round-91/c1-mutants.json --work ../c1a --only r90,r91 --expect-killed 38
MUTANT-PAIR ld1c-class-keyed     pop=r90 killed=no ... | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR ld1d-conflict-keyed  pop=r90 killed=no ... | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR nf6i2-last-occurrence pop=r90 killed=no ... | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR nf6j-pathch-narrow   pop=r90 killed=no ... | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR s1-exact-width       pop=r90 killed=no ... | pop=r91 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR s3-equal-two         pop=r90 killed=no ... | pop=r91 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=22 sets=r90,r91 pristine_r90=ok pristine_r91=ok killed_r90=16 killed_r91=22 killed_total=38
C1 EXIT=0
```

Pair tally from my log: 16 r90 kills, 22 r91 kills. Structural checks: `cmp -n <size r90>` shows the r91 population
is the r90 file byte-for-byte, then exactly the five appended rows LD1c, LD3, LD4, NF6i2, NF6j (`diff` -> `60a61,65`);
the r91 mutant `members[:16]` equal the r90 list and the six additions are the six named edits; the counter is the
frozen r87 bytes. The separate `--only r90 --expect-killed 16` control re-run was cut by my own 900 s command
deadline before it printed; it is subsumed by the r90 arm above (same counter, mutants and population) and its
committed receipt `census/round-91/controls/c1-control-r90.txt` reads `SUMMARY mutants=22 sets=r90 pristine_r90=ok
killed_r90=16 killed_total=16` with the six `killed=no` — evidence-verified. **Verdict: C1 verifies; calibration
`improved`.**

### C2 — operability 8 (re-measured; VERIFIES as narrowed)

```
(a) r91-k4-flagfail.py --tool tools/souji-record-agreement.py --before controls/c2-before-tool.py
    CASE KFF11 tool=pass before=fail ; SUMMARY cases=15 tool_pass=15 before_pass=14      EXIT=0
    control, r90 tool as both arms:  CASE KFF11 tool=fail before=fail ;
                                     SUMMARY cases=15 tool_pass=14 before_pass=14        EXIT=1
(b) c2-variant-probe.py --fixture r91 : SUMMARY variants=3 fixture=r91 detected=3        EXIT=0
    control --fixture r90             : SUMMARY variants=3 fixture=r90 detected=0        EXIT=0
(c) round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py
                                      : SUMMARY rows=12 mismatches=0 errors=0            EXIT=0
```

Independent probe (my own script importing the committed tool's `_one_line_bytes`): the claim's boundary payload
`p*101 + C2 85 + s*98` (201 bytes) renders neither `\x85` nor `\u0085`; a sweep of five valid multi-octet
characters (U+0085, é, €, U+1D11E, U+2028) at head offsets 90–114 and total lengths 195–214 (2,500 payloads)
prints zero `\x8N`–`\xFN` escapes, i.e. no valid sequence is split — consistent with the lane's 1137-row sweep.
The invalid-lead residual reproduces (section 2), which is exactly what A2(a) narrows. **Verdict: C2 verifies under
A2; operability `improved`.**

### Axis-harm check

`git diff 681f6c72 9deaefda -- SCORECARD.md` is additive (r91 measurement block, two capability rows, `### Planned
(r92)`) plus one in-place relabel of the r89 design-only row to `SUPERSEDED r90` (the r90 spot-check's routed item 4);
no axis score changed. `git diff --numstat` over `SKILL.md PROVINCE.md SHONEN.md` prints nothing; `corpus/SOURCES.md`
+1/−0; `corpus/QUALITY.md` +6/−0 (Q166); `tools/souji-record-agreement.py` is the only code change (the two cut
helpers). No file outside the lane changed; no sibling lane was touched. No owned axis was harmed.

## 4. Axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | improved | six previously surviving mutant edits are now killed by five load-bearing rows; 16 -> 22 kills re-measured with pristine arms green |
| operability | improved | the filed tool's cuts land on sequence boundaries for valid UTF-8 (15/15 vs 14/14, re-measured), the fixture now detects all three r90-falsified wording variants (3/3 vs 0/3), K4 regression green; invalid-lead residual narrowed and routed |
| depth | unchanged | `SKILL.md` untouched |
| coverage | unchanged | `PROVINCE.md` untouched; the knowledge entry deepens an existing surface |
| freshness | unchanged | no drift re-verification claim; S354 is new, not stale-held |
| adjacency | unchanged | R91Connector §2: no sibling owns the surface; no cross-domain absorption |

## 5. Discernment spot-check (`corpus/lessons/round-91.md` `## Gate`)

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
-> `souji ok`, `EXIT=0` (W04 warnings only). Rows `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
corpus/SOURCES.md` -> 275 at `681f6c72`, 276 at `9deaefda`; the SOURCES diff is one inserted row (S354).

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S354 RFC 3629 §3 UTF-8 definition (the round's admit) | admit, tier A `docs`, `mined` | live `https://www.rfc-editor.org/rfc/rfc3629.txt` -> HTTP 200, 33,856 bytes, sha256 `a2a3a394…`, `cmp`-identical to `census/round-91/srcs/rfc3629.txt`; quote at LF lines 183–185, whitespace-joined occurrence count 1 | agree | the sentence defines the initial octet of an n-octet sequence — exactly the sequence-unit rule both cut helpers implement; the row scopes itself to §3 and excludes §10/MIME/BOM; it is the primary IETF standard |
| RFC 3629 §10 Security Considerations (the round's reject sample, not filed) | reject, with flip condition | same live capture: header at line 523, quoted sentence at 525–526, occurrence 1; the overlong `C0 80` and `2F C0 AE 2E 2F` examples are at lines 536/539 | agree, with a forward note | §10 states hazards of handling illegal sequences, not an octet-role rule, and the narrowed C2 explicitly disclaims RFC validity (A2(a)), so it grounds nothing the round claims. But `### Planned (r92)` adds C0/C1/F5–F7 range checks to `_cut_tail` — a validity obligation that meets the lane's own flip condition; r92 must re-gate RFC 3629 §4 (syntax) / §10 before relying on S354's §3-only scope |
| S354's registry quote (`corpus/SOURCES.md:293`) | ≤25 words? | the row's quoted sentence against the live capture | agree | `wc -w` -> 25, occurrence 1, locator "LF capture lines 183-185 (splitlines 186-188)" is correct (`sed -n 183,185p` shows the sentence across those three LF lines); `used-by` `corpus/knowledge/utf8-window-sequence-boundary.md` exists and opens with `source: S354` |

Both sampled gate decisions agree. `## Mistakes` M1–M4 each carry evidence and a fix (M1/M2 answer the r90 routed
defects; M3 is the `_cut_tail` instrument-vs-sentence gap; M4 the spawned-vs-settled attack share).

## 6. Trend verdicts

- **expansion: improved.** `SOURCES.md` 275 -> 276 (S354, tier A, `mined`, quote re-opened live and byte-identical);
  a new admitted knowledge entry citing it; the C1 population grows by five rows on ground the r90 population did
  not hold; two capability rows with passing demonstrations.
- **quality: improved.** The filed tool fixes the r90 boundary collision for valid UTF-8 (re-measured 15/15 vs 14/14,
  plus my 2,500-payload sweep), the fixture now discriminates the three r90-falsified variants (3/3 vs 0/3), K4 stays
  green, Q166 lands; the residuals the wave found are named, reproduced and routed, not hidden.
- **discernment: improved.** The wave falsified one C1 limit sentence and three C2 clause readings; the lane narrowed
  each in `plans/round-91.md` before filing rather than defending them, reported dead attack seats as non-attacks
  with the settled share beside the planned one, corrected its own S354 locator line model in-round, and answered
  all five r90 routed defects. My sampled admit and reject both agree.

## 7. Routed defects for r92

1. **Invalid-lead collision (C2 residual, reproduced here).** `_cut_tail` must validate the whole declared sequence
   before moving the cut; add head-cut and invalid-lead fixture rows (payloads A/B of
   `w1/R91ExecC2Tool/repro-cut-tail-split.txt` as a case pair). Already in `### Planned (r92)`.
2. **KFF13 by `ast`, both directions as cases** (spaced name must fail, docstring mention must pass).
3. **C1 alternative-edit survivor search never ran** (R91MutCounter dead; settled attack share 2/13). Run it, and
   add LD4's `rc=0` assertion (A1).
4. **Re-gate RFC 3629 before any validity claim** (section 5 forward note): range checks make the §10 reject's flip
   condition fire; ground them on §4 syntax, not on S354's §3-only scope.
5. **Population header hygiene** (R91Connector F3): the r91 population's inherited comment lines should name the
   r90/r91 rows.

## 8. Closure verdict

Both declared claims verify (C1 fully re-measured; C2 re-measured under its recorded A2 narrowings, with the residual
independently reproduced); no owned axis is harmed; the three learning trends are `improved`. The settled
attack-share shortfall and the routed items are status-neutral. The four `SHONEN` boxes carry pointers a non-author
can check; promotion stays operator-owned.
