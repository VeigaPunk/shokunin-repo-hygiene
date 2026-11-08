# souji round 83 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Lane round 83, base `1e870403c5d806a5cf9ac93b00da7a928359608f`, after
`d5e325b6fa22a5371d2591d6f3c773ad69236c5c` (branch `master`, `local=remote`, `ahead=0`, `head=detached`,
`tracked=0 untracked=0`). Report `.ufo/reports/round-83/souji.md` (fleet repo commit
`1997f0f6ed1f3bdbbad18fd843287ff8226caa1f`, author `souji-shokunin <souji@shokunin.local>`, 02:46:58 −03:00; lane
tip `d5e325b6` committed 02:46:40, so the report lands last). Driver digest (`.ufo/watchdog.log`, mutable — this is
the pointer that resolves at closure):
`2026-11-08T01:28:58-03:00 launch souji round=83 pgid=3657907 driver=hyaku-inline attempt=1`;
`2026-11-08T02:47:31-03:00 complete souji round=83; hyaku-inline attempt=1`.

Outcome: status `ok`, **admitted**. C1 and C2 both verify — I re-measured each before→after myself on the committed
bytes (commands and outputs below), and the frozen kill rules did not fire. No owned axis is harmed. Six defects are
routed (three of them wrong numbers in append-only records, one an undisclosed in-place heading deletion in
`corpus/QUALITY.md`); none changes a status or a verdict.

## 1. Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by the lane identity | `git log --format='%an %H %ci' -- .ufo/reports/round-83/souji.md` | `souji-shokunin 1997f0f6…`, one path, 18 s after the lane tip | pass |
| `## SHONEN` heading, one line per box | `grep -c '^## SHONEN' <report>`; `grep -c '^- \`\[[x~ ]\]\`'` | 1 heading, 4 lines, all `[~]` with resolvable pointers; `SHONEN.md` holds the same 4 boxes, each `[~]` + one indented evidence line (`LOG.md:362`, `census/round-21/run-acceptance.py` + `accepted-matrix.json`, `PROVINCE.md` "Round21 privacy boundary", SKILL gate registry) — all resolve | pass |
| cited commits exist and are ancestors of `master` | `git merge-base --is-ancestor <h> master` over 12 hashes (P `1014143d`, F `fbf0ae5e`, A0 `51b50c94`, W1 `bbffe6a0`, W2 `9994af61`, `802a41e7`, `523e372d`, A10 `9d927f80`, tip `d5e325b6`, r82 `51a5e7fa`, base `1e870403`, landing-gate tip `9d927f80`) | 12/12 ancestor; every round commit authored `souji-shokunin <souji@shokunin.local>` | pass |
| lane pushed, nothing uncommitted | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain` | `branch=master local=d5e325b6 remote=d5e325b6 ahead=0 behind=0 head=detached tracked=0 untracked=0`; empty | pass |
| prompt carries the template contract | read `.ufo/prompts/souji-round-83.md` (987 lines) | §1 MISSION/AXES binding; §2 1–3 claims + lowest non-retired axis + causal separability + capability/exploratory; §2b frontier step + frozen census command; §3 L2 floor ≥8 + role split + godspeed lead; §4 report contract + marker rule + `## SHONEN` + commit-hash citation; §5 commit-then-push + push scope + L0; §6 hyaku addendum (run 15 binding: 8–16 seats, ≥25 % attack, ≤2 connectors, routing, "never pass `model`") — matches `templates/round-prompt.md` + addendum | pass |
| marker vs report | report names 9 round commits, receipts and before→after tables | real report, not a marker | pass |
| L2 floor and attack share | `.ufo/waves/round-83/w1-spec.json`, `w1-results.json` | 12 seats (policy band 8–16) in one wave: executor×3, scribe, scout×2, reviewer, critic, mutation-tester×2, sentinel, connector; attack = 4/12 = 33 % on the run-15 map (reviewer/critic/mutation-tester; 6/12 = 50 % if sentinel+connector count, the report's label), connectors 1 ≤ 2; 12/12 seats returned substantive output (1306–20000 bytes) | pass |
| planner seat (r82 routed defect 4) | `python3 -c "… ufo-wave-policy.json"` → `lanes[]` ids | `scout, reviewer, labrat, critic, connector, executor, mutation-tester, revenger, simplifier, scribe` — no `planner`; `nativeProfiles.omp-native-v1.planner` is a profile slot, not a dispatchable lane, so the lesson's resolution is correct and the r82 defect is answered | pass |

Status-neutral defects (named, not status predicates):

- **D1 — stale SOURCES count.** Report "Sources & frontier" and `LOG.md` say rows `252 → 255`. Re-derived:
  `git show <rev>:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → base `1e870403` = 252,
  `802a41e7` = 255, `523e372d`/`9d927f80`/tip `d5e325b6` = **256**; the diff adds exactly 4 rows (S330–S333, 0 removed).
  The 255 was measured before S333 landed at `523e372d` and never re-derived at filing.
- **D2 — undisclosed in-place deletion in `corpus/QUALITY.md`.** `git log -S'## Round 23 criteria' 1e870403..d5e325b6`
  → deleted at `802a41e7`; `grep '^## Round 2[0-9] criteria'` shows `## Round 23 criteria` gone from both revisions
  after it, so Q54/Q55 now sit under `## Round 21 criteria`. No report/LOG/lesson sentence mentions it.
- **D3 — wrong digest bound to a cited receipt.** `LOG.md` (twice: the C2 bullet and the "regenerated receipts"
  bullet) and `corpus/lessons/round-83.md` "Measured" bind `census/round-83/records/c2-after.txt` to tool sha256
  `b0a5b662…`. That receipt's own header says `sha256=72a405f2…`, and
  `git show d5e325b6:tools/souji-vault-verify.sh | sha256sum` = `72a405f2…`. `b0a5b662…` is the earlier
  `802a41e7` arity-guarded bytes (the A10 whole-file read changed them).
- **D4 — seat-delivery sentence contradicts the wave.** `LOG.md` "9 seats delivered substantive reports, 3 left a
  skeleton only". `w1-results.json` holds 12 substantive outputs (min 1306 B), and the report itself says all twelve
  delivered (three after a first-read skeleton). The LOG wording is wrong, the report's is right.
- **D5 — "read each stat whole" is true of the map pass only.** `plans/round-83.md` A10 says "every
  `/proc/<pid>/stat` is read WHOLE"; the filed tool reads whole at `tools/souji-vault-verify.sh:244` (the map pass)
  but first-line at `:263` (TERM re-read) and `:276` (KILL re-read). See §2 for the probe: no frozen row fails.
- **D6 — wave seat reports are not durable.** `.ufo/waves/` is gitignored (`.gitignore:1`); only 8 files under
  `.ufo/waves/round-83/` are tracked (spec/dispatch/results/ready + the ledger), while the falsification ledger cites
  nine seat reports under `.ufo/waves/round-83/w1/`. Those pointers resolve on this host's working tree only. Same
  pattern as r82 (2 tracked files), so a standing durability defect, not a new one.

## 2. Claims

Both claims rest on lane-owned instruments. Per PROTOCOL §Gate standard (Closure consequence) I executed no sibling
gate: **re-measured** means I ran the committed counter bytes myself from the lane root against scratch dirs under
`/home/vgpnk/Projects/shokunin/.scratch/` (the instruments refuse `/tmp`); **evidence-verified** means I re-read
committed receipts and re-hashed the bytes they bind.

| object | at base `1e870403` | at the commit that introduced it | at tip `d5e325b6` | receipt binding | result |
|---|---|---|---|---|---|
| `census/round-83/c1-false-row-harness.py` | absent | `0b76936d…c14b` (P `1014143d`) | same | `0b76936d…` | frozen |
| `census/round-83/c1-false-rows.tsv` | absent | `c9a6d58c…eb` (P) | same | pinned by the harness (`POP_PIN`) | frozen |
| `census/round-83/c1-pointer-counter.py` | absent | `2d163a6e…90e0` (W1 `bbffe6a0`) | `052c4f3f…1d79` | `052c4f3f…` | candidate; the W1→tip delta is the disclosed cleanup (dead alternates/disjunct, comment) |
| `census/round-82/c1-pointer-counter.py` (control K-a) | `cbfdc07c…875a` | — | same | `cbfdc07c…` | frozen do-nothing control |
| `census/round-83/c2-tree-walk-counter.py` | absent | — | `d3fe851d…fc92` | `d3fe851d…` | frozen |
| `census/round-83/c2-population.tsv` | absent | — | `25904ded…958e` | `25904ded…` | frozen; equals the counter's `ROUTES` |
| `tools/souji-vault-verify.sh` | `dd6d440e…5e1a` | `9994af61` = `d4826cce…`, `802a41e7` = `b0a5b662…`, A10 = `72a405f2…` | `72a405f2…8a18` | receipts `c2-after*.txt` bind `72a405f2…` | tip = A10 bytes |
| `census/round-83/controls/c2-K-a-r82-tool.sh` | — | `dd6d440e…5e1a` | same | `dd6d440e…` | byte-identical to the base tool, i.e. a true do-nothing control |

### C1 — calibration (the lane's lowest owned non-retired axis, 7): **verified** (re-measured, both ends, plus a mutant)

```
python3 -B census/round-83/c1-false-row-harness.py \
  --counter census/round-83/c1-pointer-counter.py \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin \
  --work /home/vgpnk/Projects/shokunin/.scratch/closure-r83-c1a
```

Observed: `SUMMARY rows=36 mismatches=0 accepted=0 refused_true=0 errors=0`, `EXIT=0` (70.1 s). Every row `match=yes`;
`TF6` (`w2/`) and `TF7` (`w1/`) `got=MOVED`; `NF-J` (duplicated middle dir) and `NF-K` (flattened round-root copy)
`got=REFUSED`. Header digests match the receipt: harness `0b76936d…`, population `c9a6d58c…`, counter `052c4f3f…`.

Before, same harness, the r82 counter (`census/round-82/c1-pointer-counter.py`, `cbfdc07c…`):

```
SUMMARY rows=36 mismatches=2 accepted=0 refused_true=2 errors=0        EXIT=1   (65.0 s)
ROW TF6 … expect=MOVED/- got=REFUSED rc=1 match=no
ROW TF7 … expect=MOVED/- got=REFUSED rc=1 match=no
```

Delta delivered by the new rule, reproduced exactly (same two refusals the report and `controls/c1-K-a-r82-counter.txt`
name). Implementation checked at `census/round-83/c1-pointer-counter.py:321`
(`OWNTREE_WAVE = re.compile(r"^(?:w[0-9]+|a2w1|assimilation)/")`) plus the kept `_capture_ok` fallback, i.e. the
per-branch remainder the claim states.

Mutation probe of the round's own wording (the ledger's C1/`S83CriticClaims` row: "the six-shape enumeration is
over-specified"). I copied the counter into scratch and reduced only the regex to `^(?:w[0-9]+)/`:

```
python3 -B census/round-83/c1-false-row-harness.py --counter /home/vgpnk/Projects/shokunin/.scratch/mut/c1-w-only.py …
SUMMARY rows=36 mismatches=0 accepted=0 refused_true=0 errors=0        EXIT=0   (43.5 s)
```

So the row is real: a one-alternation mutant keeps all 36 rows, `a2w1/`/`assimilation/` carry no row. It is
**reconciled**, not unreconciled: the filed claim states the shapes as the rule's real vocabulary and carries the
over-specification as a stated limit, and Q152 records the criterion. Nothing in the filed wording claims the
population discriminates the six-shape list.

Regression evidence-verified only: `c1-regress-r82-harness.txt` `rows=32 mismatches=0`, `r81 25/0`, `r80 18/0`,
`r79 9/0`, `r78` `items=22 resolved=22` + `forged=12 matched=12 accepted=0`, `r77` `items=35 resolved=35` +
`forged=7 matched=7 accepted=0`.

### C2 — operability (8): **verified** (re-measured, both ends)

After, the filed bytes (`tools/souji-vault-verify.sh` `72a405f2…`), at load1 ≈ 145:

```
python3 -B census/round-83/c2-tree-walk-counter.py --tool tools/souji-vault-verify.sh \
  --work /home/vgpnk/Projects/shokunin/.scratch/closure-r83-c2a
```

Observed: `SUMMARY rows=20 mismatches=0 errors=0 orphans=0`, `EXIT=0` (102.8 s); deep rows `d12-term-pid` 1.0 s,
`d12-term-group` 0.8 s, `d24-term-pid` 1.0 s, `d24-monitor-group` 0.8 s, each `survivors=0 tmpleft=0`, both launches
(`default` and `monitor`); the four positive controls (`p1-honest`, `p2-hang-bounded`, `p3-stdin`, `p4-fallback`)
`match=yes`.

Before, the do-nothing control (`c2-K-a-r82-tool.sh`, byte-identical to `git show 1e870403:tools/souji-vault-verify.sh`,
`dd6d440e…`), at load1 ≈ 86:

```
python3 -B census/round-83/c2-tree-walk-counter.py --tool census/round-83/controls/c2-K-a-r82-tool.sh …
SUMMARY rows=20 mismatches=2 errors=0 orphans=2        EXIT=1   (94.4 s)
ROW d12-term-pid     … secs=4.6 match=yes
ROW d12-term-group   … secs=3.8 match=yes
ROW d24-term-pid     … exited=n survivors=29 tmpleft=1 secs=5.0 match=no
ROW d24-monitor-group… exited=n survivors=29 tmpleft=1 secs=5.0 match=no
```

That is the reported load-dependent character reproduced (the round saw 4, 1 and 0/2/2/2/4; I see 2): the N=24 rows
exceed the 5 s settle with 29 survivors and a leftover private file, while the N=12 rows straddle it at 3.8–4.6 s. The
load-independent discriminators I re-derived myself: **pgrep invocations** — the candidate contains none
(`grep -n pgrep tools/souji-vault-verify.sh` → one comment line; the walk is one `for d in /proc/[0-9]*` pass, an
associative ppid map and a kill-as-discovered DFS) and the control calls `kids=$(pgrep -P "$child")` once per tree
node (`census/round-83/controls/c2-K-a-r82-tool.sh:236`), N+2 nodes per tree; and **deep-row seconds** 3.8–5.0 →
0.8–1.0.

Adversarial probe of the A10 repair (D5). I ran the filed tool against a stub whose own comm carries a newline
(`prctl(PR_SET_NAME, "x\ny")`, then `sleep 600`), asserting the hang point `prog=cli parent=timeout` and signalling
the tool by pid after 2 s. At signal time the stub's stat began `2639659 (x\ny`. Result: `exited=y rc=143
sig_line=y survivors=0` — the truncated TERM re-read (`:263`) skips the pid, but `cli_on_signal:292`
(`kill -TERM -- "-$pid"`) still ends the in-group stub. So the map pass's whole-file read is load-bearing only for
pids that also leave timeout's process group, which is already a stated limit. The residual hazard is narrow, the
claim's frozen population does not fail, and A10's "every read is whole" sentence is still an overstatement (routed).

Evidence-verified only (not executed — the lane's gate): `selftest: 57 checks, 0 failed` (`c2-regress-selftest.txt`),
r17 `SUMMARY total=37 failed=0 skipped=0` (binds `72a405f2…`), probe D `SUMMARY arms=4 failed=0` (binds `72a405f2…`).

### SCORECARD and axes

`git diff 1e870403 d5e325b6 -- SCORECARD.md`: appends only (the Round 83 measurements table, the capability row, the
r84 planned list); no axis score changed (calibration 7, coverage 8, operability 8 at both ends, each carrying a
verdict and counting command instead of a number, as the lane has done since r79). `git diff --quiet 1e870403
d5e325b6 -- PROVINCE.md` is true. `git diff … -- tools/souji-vault-verify.sh` is confined to `cli_kill_tree` (+ the
comment block); no other safety path moved.

| axis | verdict | reason |
|---|---|---|
| calibration | improved | C1 re-measured: the r82 counter REFUSES two true rows (`TF6` `w2/`, `TF7` `w1/`, `refused_true=2`, `EXIT=1`); the filed counter keeps them and still refuses `NF-J`/`NF-K` (`mismatches=0 accepted=0 refused_true=0`, `EXIT=0`), with the r82 32-row regression green. The rule now agrees with the lane's real layouts (`census/round-83/records/wave-dirs.txt`), which is exactly the r82 A2 limit and spot-check route 5 |
| operability | improved | C2 re-measured: the base bytes leave both N=24 rows red (29 survivors each, 5.0 s, private file left) and both N=12 rows at 3.8–4.6 s of a 5 s settle; the filed tool is 0/0/0 with deep rows 0.8–1.0 s and zero per-node `pgrep` forks. The A10 whole-file map read is in the bytes and the frozen population passes on both launches |
| coverage | unchanged | no coverage claim; `PROVINCE.md` unchanged; four SOURCES rows appended but no `## Frontier` row advanced (`corpus/README.md` no diff) |

The other three axes carry no claim and show no harm: `depth` gains `corpus/knowledge/own-tree-pointer-binding.md` and
an r83 section inside `gate-signal-handling.md`; `freshness` is exercised in passing (r77–r82 regressions re-run, r82
spot-check defects 1/2/3/5/8/9 answered — see the lesson `## Inherited`); `adjacency` is unchanged (the connector seat
records `tools/souji-proc-census.sh:136-160` as the lane's own overlap, nothing absorbed).

## 3. Discernment spot-check

`corpus/lessons/round-83.md` `## Gate` logs four decisions: three admits (S332, S331, S333) and one reject (S330).

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S332 — Linux kernel `fs/proc/array.c` at tag v6.17, `do_task_stat()` | admit (`code`, tier A; cited by C2's knowledge section) | `curl -sS https://raw.githubusercontent.com/torvalds/linux/v6.17/fs/proc/array.c` → `HTTP 200 bytes=23233`, sha256 `17f2318d…a938` = the committed capture `census/round-83/srcs/linux-array.c-v6.17`; `sed -n '590,594p'` → the quoted five lines verbatim; `proc_task_name(m, task, false)` at 591; `start_time` at 612 | agree | quote is verbatim, located, ≤25 words; emission order and the unescaped-comm branch are precisely what the tool parses, and S075 (`proc_pid_stat(5)`) governs field meaning — the scope split is real, so this is not the r23 "duplicate of an existing ground" failure |
| S330 — procps-ng `pgrep(1)`, `-P/--parent` | reject (row exists as `rejected` with reason + flip) | `sha256sum /usr/share/man/man1/pgrep.1.gz` = `04b59b01…a916`; `zcat … \| sed -n '166,167p'` → "\-P, \-\-parent ppid… Only match processes whose parent process ID is listed."; `zcat … \| grep -ic nspid` → 0; `zcat … \| grep -cE 'list-full\|oldest\|newest\|--full'` → 4 | agree | the only new proposition is the `-P` parent lookup, which the tool demonstrates by running, and S075 already governs process identity, so a second row adds no expansion; the flip is grounded in tokens the page does contain and the draft's ungrounded `NSpid` token is absent (0 hits) |
| S331 — the lane's own wave-directory census (`census/round-83/records/wave-dirs.txt`) | admit (`own-work`, tier A, `mined`) | re-ran the file's header command in the lane at the tip working tree: `for d in .ufo/waves/round-*/*/; … uniq -c` → `w1/ 66, w2/ 19, assimilation/ 4, records/ 3, residual/ 2, w3/ 1, a2w1/ 1` (+ the singleton dirs); the committed file says `w1/ 65` at `1e870403`; `grep -n waves .gitignore` → `1:.ufo/waves/` | agree | the census is reproducible from the working tree and its single drift (`w1/ 65 → 66`, the r83 wave dir created after the census) is disclosed by S333; it is the only row that speaks to the C1 shape list, which is why C1 is a sourced claim |
| newly written `corpus/SOURCES.md` row — S332's quote cell | ≤25-word located quote | as above (`sed -n '590,594p'` of the capture; quoted text 24 words) | agree | the cell quotes the file, names the line range and the capture path, and the citation resolves; S333's cell paraphrases its own header command (no quotation marks) — acceptable for an `own-work` provenance row, noted as form only |

Sources census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, 87 pre-existing `W04` cross-scope duplicate-URL
lines, `EXIT=0`. Rows `252 → 256` (`grep -cE` above); the report's `255` is D1.

## 4. Trend verdicts

- **expansion: unchanged** — I agree. The registry gains four rows (S330 rejected, S331/S333 own-work, S332 code) and
  the corpus gains one knowledge file plus one section inside an existing entry, all on ground the coverage map
  already holds; `git diff --quiet 1e870403 d5e325b6 -- corpus/README.md` is true, so no `## Frontier` row advanced
  and no new kind of source entered. The round's gain is instrument depth (a rule that matches the real layouts, a
  walk that costs one pass), not breadth, and the report says exactly that.
- **quality: improved** — I agree. The pointer rule now binds the lane's real wave shapes instead of a plausible
  fixture (my re-measurement: 2 refused true rows → 0); the vault tool's signal path drops from one `/proc` scan per
  node to one pass, deep-row cost 3.8–5.0 s → 0.8–1.0 s with 0 survivors and 0 pgrep forks; the two repair-grade
  defects the wave found are on the filed bytes (the `${20}` arity abort, the whole-file map read) and the
  receipts bind those bytes; Q152/Q153 add two criteria with evidence pointers. Nothing admitted was found false and
  no entry was left stale (the new entry's `recheck:` command is the one I ran).
- **discernment: improved** — I agree. The pre-file ledger carries 12 rows over 2 claims and all 6 attack seats,
  every `falsifies-wording`/`falsifies-number` row names a narrowing (A1–A10), and my own mutant probe confirms the
  over-specification row is real rather than defensive; the wave falsified eight sentences of the round's own
  wording and all eight were narrowed before filing; the three Gate decisions I re-opened all agree; the S330
  rejection was re-adjudicated with a grounded flip. The defects I file below are record-form and durability, not
  taste disagreements.

## 5. Routed defects (lane fixes next round)

1. **D1 — SOURCES count.** Append a correction naming `252 → 256` (counting command
   `git show d5e325b6:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`) for the report's and
   `LOG.md`'s `255`; the report itself is filed and is never rewritten.
2. **D2 — `corpus/QUALITY.md` heading.** `## Round 23 criteria` was deleted at `802a41e7` with no record, leaving
   Q54/Q55 under `## Round 21 criteria`. Restore the heading in a new commit and name the deletion in the round entry
   (criteria rows themselves are untouched).
3. **D3 — digest binding.** `LOG.md` (two places) and `corpus/lessons/round-83.md` bind `records/c2-after.txt` to tool
   sha256 `b0a5b662…`; that receipt and the filed tool are `72a405f2…`. Append a `superseded by` line naming the
   superseded digest (Q55's own rule), not a rewrite.
4. **D4 — seat-delivery sentence.** `LOG.md`'s "9 seats delivered substantive reports, 3 left a skeleton only"
   contradicts `w1-results.json` (12 substantive outputs) and the report; append the correction.
5. **D5 — A10 scope.** Apply the whole-file/last-`)` stat read to the TERM and KILL re-reads
   (`tools/souji-vault-verify.sh:263`, `:276`), and row a setsid'd newline-comm CLI (discovered by the map pass,
   skipped by the truncated re-read, missed by the group kill). No frozen row fails today; the sentence is what is
   wrong.
6. **D6 — wave evidence durability.** The seat reports the ledger cites (`.ufo/waves/round-83/w1/*.md`) are gitignored
   and untracked; commit the seat reports (force-add) with the round that cites them, as the spec/ledger/ready files
   already are.
7. **Carried unchanged** — the r83 lesson's own r84 list (C1 deep-token pair + `NF-L`/`NF-L2`/`NF-M`/`NF-L3`, the
   census-in-tree branch, C2 pid-reuse/parent-before-child/`termign-fork`/`p5-late-term`/`strace` settle, the prereg
   key-line form) and the r81 list (`_regular` pathspec framing, quarantine intro-blob digest row, fork-tail row, r79
   gate re-measurement, check-4 300 s backstop, r76 K03/K04, status-trusting lane tools, r17 240 s runners).

SHONEN: all four boxes stay `[~]` with resolvable pointers (SKILL gate registry rows `SKILL.md:956-957`, the r83
receipts, `LOG.md:362` for the historical end-to-end sweep, `PROVINCE.md` unchanged). Boxes 1–4 look checkable by a
non-author from those pointers; promotion is operator-owned and I write no `[x]`.
