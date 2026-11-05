# S66ReviewerC2 — C2 counter / population / M-ENV attack review

Reviewer seat S66ReviewerC2, souji round 66 (souji-shokunin), post-freeze wave w1.
Read-only attack of the frozen instruments. No mutating command run anywhere; all experiments on
my own scratch bytes under `/fast/scratch/hyaku/souji-r66/S66ReviewerC2/`.

Artifacts read at frozen revisions (`git -C <lane> show <rev>:<path>`):
- `census/round-66/c2-counter.py` @ `4576f101a9200206de00ef00923dd38a7b2dbc7d` — sha256 verified `ac2157e606…5c67` = prereg pin, MATCH.
- `census/round-66/c2-statements.tsv` @ `4576f101…` — sha256 verified `c41b0bc4…2ee4` = prereg pin, MATCH.
- `census/round-66/c2-mutate.py` @ `4576f101…`.
- Base writer `tools/souji-receipt-write.py` @ `045e103478fa4a7eff77db2cab5b9e2f26959a0a` (1374 lines).
- Round-65 counter `census/round-65/c2-counter.py` @ `045e103…` (r65 rule: `EMISSION_TOKENS = ("refuse(", "return")`, bare substring).
- Base `SKILL.md` @ `045e103…`; frozen control `census/round-66/controls/c2-do-nothing.txt` @ `4864c01f112c9f423def430d9b6e01bdc0e21f36`.
- The executor's shape contract read from `.ufo/waves/round-66/w1-spec.json`, item S66ExecWriter.

Baseline reproduction (both read-only counter runs against the lane):
- `python3 -B census/round-66/c2-counter.py --root LANE --tsv census/round-66/c2-statements.tsv --tsv-rev 4576f101… --rev 045e103…` → `FINDING GOVERNED-STATEMENT-UNRESOLVED s5`, `MARKERS flag=1 inrun=1 env=1 unmerged=1 envcfg=0 envred=0`, `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1` — byte-identical to the frozen do-nothing receipt (diff clean).
- `python3 -B census/round-65/c2-counter.py --root LANE --tsv census/round-65/c2-statements.tsv --tsv-rev 2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8 --rev 045e103…` → `rows=4 findings=0 verdict=PASS`, `EXIT=0` (r65 honest green at base).
- Both selftests pass: r66 rc=0 (14 cases), r65 rc=0 (13 cases).

---

## FINDINGS

### MEDIUM-1 (check b) — the M10 regression selftest case is vacuous; the counter's selftest does not guard the repair

`c2-counter.py` selftest case `m10-returncode-line-not-live` (lines 321–326) passes under BOTH the
repaired and the unrepaired emission rule. Proof by experiment — revert the repair
(`RETURN_LITERAL = re.compile(r"return")`, i.e. the exact r65 substring behavior) and run `--selftest`:

```
S=/fast/scratch/hyaku/souji-r66/S66ReviewerC2
python3 -B $S/c2-counter-reverted.py --selftest       # rc=0, all 14 cases PASS, zero MISMATCH
```
All 14 cases — including `m10-returncode-line-not-live: findings=1 want=1 pass` — still pass with the
repair reverted. Root cause: the case's SKILL.md blob is `S2_AFTER` while its row is `_rows4()[2]` (s3,
wordings `S3_BASE`/`S3_AFTER`); neither s3 wording is a substring of `S2_AFTER`, so the row always
resolves `GOVERNED-STATEMENT-UNRESOLVED` — a finding count that is completely independent of the
marker map. The case never exercises the polarity it claims to pin ("a needle on a … `r.returncode`
… line … is not an emission path; the env refusal's deletion … must therefore score findings").
A real regression test would use a row that resolves to `after` (e.g. skill_tip blob) so the finding
count flips only with `env`'s liveness (r66 on M-ENV: 1; r65 rule on M-ENV: 0 — both demonstrated in
check f below).

Impact on THIS round: none — the kill-power predicate itself (check f) validates the repair on the
real mutant. Impact going forward: `--selftest` would stay green if a later round reverted
`RETURN_LITERAL` to the r65 substring rule; the named in-code guard does not exist.

Reproduction:
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 4576f101a9200206de00ef00923dd38a7b2dbc7d:census/round-66/c2-counter.py
sed -n '321,326p' <that file>         # the case; blob=S2_AFTER, row=s3, want=1
# reverted-rule copy + selftest shown above
```

### LOW-1 (check a) — RETURN_LITERAL matches non-refusal string-return lines at base (dormant overcount class)

`RETURN_LITERAL = r"\breturn\s*\(?\s*f?[\"']"` (line 95) matches 9 lines in the base writer; 5 of them
are NOT refusal emissions:

| line | text | needle |
|---|---|---|
| 175 | `return "content"` | – |
| 177 | `return "mode"` | – |
| 183 | `return "mode"` | – |
| 186 | `return "content"` | – |
| 853 | `return "python3 -c " + shlex.quote(code)` | – |

The other 4 are genuine refusal emissions: L119 (`return (f"RECEIPT-INDEX-UNMERGED: …"`), L130
(`return (f"RECEIPT-INDEX-FLAG-CONCEALED: …"`), L123 / L127 (refusal strings for classes outside the
6-marker set: `RECEIPT-GITLINK-CONCEALED`, `RECEIPT-INDEX-CONCEALED-ABSENT`). Marker impact at base:
zero — no needle shares those 5 lines. Residual: the lexical read (named limit L4) now also treats
"`return` + string literal" as an emission path; any future needle landing on such a helper line
(e.g. a label builder returning a message string) would count live. Same kin of the r65 `returncode`
overcount, just narrowed.

### PROVEN (check a) — emission-line set delta between r66 and r65 live_markers() on the base writer

Direction 1: new live_markers() counts a line r65 did not — **empty set, for ANY writer** (base
included). `RETURN_LITERAL` begins with the literal `return`, so every r66-emission line contains the
substring `return` and is already an r65 emission line. Verified exhaustively over all 1374 lines
(predicate implication holds for every line).

Direction 2: r65 counts lines r66 does not — **140 lines** (|E65|=182 → |E66|=42). Classes:
`if r.returncode …` selftest/assertion lines and their `raise AssertionError(f"… {r.returncode}…")`
continuations, bare `return` / `return x` value returns, `return subprocess.run(...)` plumbing.
Exactly ONE of the 140 carries a marker needle:

```
L1129: if r.returncode != 2 or os.path.exists(out3) or "RECEIPT-INDEX-ENV-SET" not in r.stderr:
```
(the writer's own selftest assertion in `case_24_git_index_file_env_refused`, the empty-`GIT_INDEX_FILE`
case). That single line is the entire substance of round-65 M10: r65 counted `env` live from a test
assertion inside the writer's selftest.

Marker maps, base writer: r66 `{flag:1, inrun:1, env:1, unmerged:1, envcfg:0, envred:0}`; r65
`{flag:1, inrun:1, env:1, unmerged:1}` — identical for the four shared needles. The repair changes
nothing at base; it changes exactly one bit on the M-ENV mutant (below).

Reproduction (summary):
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 045e103478fa4a7eff77db2cab5b9e2f26959a0a:tools/souji-receipt-write.py > w.py
python3 -c "import re;[print(i,l.rstrip()) for i,l in enumerate(open('w.py'),1) if re.search(r'\breturn\s*\(?\s*f?[\"\']',l) ]"
```

### PROVEN (check c) — DUPLICATE-LIVE-WORDING is unreachable for s5 (and every stable row); second occurrence is invisible and benign

`s5` in the frozen TSV has `base_pattern == after_pattern` (byte-equal) → `stable = True`
(c2-counter.py line 157). The `DUPLICATE-LIVE-WORDING` append sits at line 167–170, inside the
`else:` of `if stable:` (line 160) — statically unreachable for any stable row (s1, s4, s5). So no
stable row can ever be flagged for a stale second copy, and the answer to "is DUPLICATE-LIVE-WORDING
reachable for a stable row" is **no, by construction**.

Second-occurrence risk for the stable s5 wording: matching is presence-only `.encode() in blob`
(line 158–159). A second copy of the s5 sentence anywhere in SKILL.md (quoted lesson, changelog
recap) produces no finding and cannot produce one — benign for this round's green/red, but it also
means the counter cannot tell WHICH occurrence is the governed statement; presence of one copy is
enough, wherever it sits. That is inside the declared lexical-read named limit (L4/round-63 M3
narrowing), not a new defect.

### PROVEN (check d) — an always-zero counter cannot pass the selftest (STUB-ALWAYS-ZERO), double-guarded

Two independent failure paths, both exercised by mutating my scratch copy of the counter only:
1. Stub `live_markers` (returns all-False): honest-tip-green case (want 0) itself MISMATCHES
   (got 4 — every required marker missing), control prints `REJECTED`, `fail=1`, `EXIT=1`.
2. Stub `evaluate` (returns [] always): all 11 non-trivial cases (want ≥ 1 of the 12 non-first
   cases; only `unmerged-clause-green` wants 0) MISMATCH, control prints
   `ACCEPTED-FALSE-GREEN`, but `ok = ok and not stub_zero` (line 339) forces `fail=1`, `EXIT=1`.

The control alone (`stub_zero = all(c == 0 for c in got_counts[1:])`, line 337) is sufficient
because 11 of the 12 non-first expected counts are ≥ 1; the per-case wants make it a second, purely
mechanical guard. Cosmetic only: when the stub- evaluate path fires, the control's message says
"ACCEPTED-FALSE-GREEN" while the run still fails — correct behavior, confusing wording.

Reproduction:
```
python3 -B /fast/scratch/hyaku/souji-r66/S66ReviewerC2/c2-counter-stubM.py --selftest   # EXIT=1
python3 -B /fast/scratch/hyaku/souji-r66/S66ReviewerC2/c2-counter-stubE.py --selftest   # EXIT=1
python3 -B /fast/scratch/hyaku/souji-r66/S66ReviewerC2/c2-counter.py --selftest        # EXIT=0, REJECTED
```

### ANSWERED (check e) — anchor detection cannot silently multi-match; it fails closed; the real fragility is the unconditional 3-line amputation

The anchor test is exact stripped-equality per line: `line.strip() == 'if "GIT_INDEX_FILE" in
os.environ:'`. In the base writer exactly one line matches (L278). In the candidate shape the
executor is told to keep (`w1-spec.json`, S66ExecWriter item 2: keep line 1
``     if "GIT_INDEX_FILE" in os.environ:` then a 2-line `refuse(...)` whose first line starts with
`        refuse(f"RECEIPT-INDEX-ENV-SET:`), there is still exactly one such line — the writer's
selftest references are assignments, comments and assertions, none strip-equal the anchor. If a
second stripped-equal line ever existed, `c2-mutate.py` refuses with exit 2 (`anchor … occurs N times
(need exactly 1)`) — it can never silently match >1; multi-match is fail-closed, and a refused recipe
makes the kill-power target unrunnable (a target failure, not a false pass).

Residual fragility (LOW, named for the L1): the deletion `block = lines[i:i + 3]` is unconditional —
the needle check (`NEEDLE in "".join(block)`) does not verify the block's layout. Under the pinned
3-line shape it amputates guard + 2-line refuse call (base L278–280, following line L281 is blank:
clean). If a future candidate reflows the refuse call to 1 line, the recipe deletes the guard, the
refuse, AND the following line; a deleted comment/blank would still compile (silent unrelated
amputation), while most other deletions strand a continuation and fail the compile check
(fail-closed). The executor's committed contract pins the shape, so this is a watch item, not a
defect of this round's instruments.

### ANSWERED (check f) — the kill-power predicate is falsifiable as written; mechanism validated on base bytes; two named caveats

Predicate (preregistration-attempt2, C2 kill-power target): on the M-ENV mutant of the measured
writer, the r66 counter prints `findings>=1` and exits 1, while the r65 counter (tsv-rev
`2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8`) prints `findings=0` on the same mutant at the same
SKILL.md. It is falsifiable: both halves are single runnable commands over committed artifacts
(frozen recipe, sha-pinned counters/TSV, one measured full40), each printing a deterministic number;
refutation = r66-on-mutant printing `findings=0` (or exit 0), or r65-on-mutant printing
`findings>=1`. The honest C2 target (`findings=0` at the same revision) supplies attribution:
mutant-vs-honest delta isolates the deletion.

Mechanism validated in-memory on the base writer bytes (same `live_markers`/`evaluate` code objects
imported from the committed instrument files):
- M-ENV mutant of base writer: 1374 → 1371 lines (delta 3, matching `removed_lines=3`), anchor gone,
  residual env-needle lines at base L1113 / L1129 / L1272.
- r66 markers on mutant: `env=False` (everything else unchanged) → with a green s1–s5 SKILL.md,
  r66 `findings = 1` (s2 `closed_full` `SCOPE-OVERREACH`, `env` missing; s5 `env_closed` stays green
  because `envcfg`/`envred` are untouched by M-ENV).
- r65 markers on mutant: `env=True` — liveness carried by exactly one line, mutant L1126 (base L1129,
  the `returncode`+needle selftest assertion) → r65 `findings = 0` on the same green SKILL.md.

```
# mechanism reproduction (read-only; instruments imported from committed bytes)
python3 -B /fast/scratch/hyaku/souji-r66/S66ReviewerC2/analyze.py   # sections a5/f1, f2
```

Caveats (not falsity, named for completeness):
1. `findings>=1` does not pin the finding KIND. A spurious finding on the mutant receipt (e.g. a
   typo'd s5 in the landing producing `GOVERNED-STATEMENT-UNRESOLVED`) satisfies the predicate while
   the mutation is unexercised. The exposure is closed only if the honest `findings=0` and the
   mutant `findings>=1` runs read the same rev and the same SKILL.md bytes; as two separately
   receipted targets that linkage is procedural, not enforced by the counter.
2. The r65-blind half silently REQUIRES the candidate to retain a residual `RECEIPT-INDEX-ENV-SET`
   needle on a `return`-substring line OUTSIDE the deleted block (today: base L1129, kept by the
   executor's instruction 6 "keep the selftest passing … without changing existing case results"). If
   the candidate reworded that assertion, r65 would also print `findings>=1` and kill-power would fail
   for a candidate-shape reason, not a counter reason. The executor's contract preserves it this round.
3. Repro needs one scratch-clone commit (mutant bytes at `tools/souji-receipt-write.py`) per the
   prereg's own recipe — permitted for L1, done here only in-memory.

---

## Numeric results measured

| quantity | value |
|---|---|
| instrument sha256 (counter / tsv) | MATCH / MATCH vs prereg pins |
| base writer lines | 1374 |
| RETURN_LITERAL matches at base | 9 (5 non-refusal: L175, L177, L183, L186, L853) |
| emission lines r65 / r66 | 182 / 42; r66∖r65 = 0 (proved for any writer); r65∖r66 = 140, exactly 1 needle-carrying (L1129) |
| base marker maps | r66: flag=1 inrun=1 env=1 unmerged=1 envcfg=0 envred=0; r65: flag=1 inrun=1 env=1 unmerged=1 |
| do-nothing control reproduced | `rows=5 findings=1 verdict=FAIL EXIT=1`, marker line byte-identical to frozen receipt |
| r65 counter at base | `rows=4 findings=0 verdict=PASS EXIT=0` |
| selftests | r66 rc=0 (14 cases); r65 rc=0 (13 cases); reverted-rULE r66 rc=0 (14 cases, all pass ⇒ MEDIUM-1) |
| always-zero stubs | live_markers stub EXIT=1; evaluate stub EXIT=1 (control REJECTED forced) |
| M-ENV mutant of base | 1371 lines, anchor 0 hits, residual env-needle lines 3 (base L1113/L1129/L1272 → mutant L1110/L1126/L1269) |
| mutant markers | r66 env=0 / else unchanged; r65 env=1 (carried by mutant L1126 alone) |
| in-memory kill test (green s1–s5 SKILL.md) | r66 on mutant findings=1 (s2 SCOPE-OVERREACH); r65 on mutant findings=0; honest candidate findings=0 |
| s5 stability | base_pattern == after_pattern ⇒ stable ⇒ DUPLICATE-LIVE-WORDING unreachable |
| anchor hits base writer | exactly 1 (L278) |

Tooling: no installs; only system `python3` and `git` (read-only). Scratch
`/fast/scratch/hyaku/souji-r66/S66ReviewerC2/` holds the extracted blobs, the analysis script
(`analyze.py`), and the three mutation experiment copies (`c2-counter-reverted.py`,
`c2-counter-stubM.py`, `c2-counter-stubE.py`) — all scratch-local, repo untouched.
