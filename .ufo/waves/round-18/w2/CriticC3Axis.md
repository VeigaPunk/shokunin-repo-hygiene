# CriticC3Axis — attack on C3 (coverage): `tools/souji-proc-census.sh`, residue classes 0 → 3

Scope: the declared C3 claim as written in `corpus/lessons/round-18.md:8`,
`SCORECARD.md:13`, `SCORECARD.md:54`, `PROVINCE.md` (Work-surface bullet, F5
row, Refuses bullet), `corpus/QUALITY.md` Q32, `corpus/README.md:236-246`, and
the SKILL registry rows `souji-proc-census` / `r18-proc-census` /
`r18-leak-count` (`SKILL.md:172-174`). Read-only probes only; committed bytes at
`5efb519f` via `git show`, `git diff`, `git grep` on named paths, plus
sha/sort/comm arithmetic on the two committed live records. No installs made
(pacman guard honored; nothing needed).

## Claim under attack

"Process residue becomes an observed, list-only surface (F5):
`tools/souji-proc-census.sh` lists 3 residue classes (cwd-deleted,
argv-path-gone, fd-path-gone; 0 before); fixture 11/0; header-only stub fails
P1/P2; live 65 = blind counter 65, symmetric pid difference 0."

## Findings

### F1 — MODERATE (coverage): "governed" overclaims an observed surface; the lane's own authority files say "observed"

- `corpus/lessons/round-18.md:8` — "residue classes **governed** 0 → 3".
- `SCORECARD.md:13` — "`tools/souji-proc-census.sh` **governs** 3 residue classes".
- The same round's criterion Q32 (`corpus/QUALITY.md`, round-18 table): "Process
  residue is an **observed** surface, **list-only** ... a row is a nomination,
  not a removal receipt." `PROVINCE.md` work-surface bullet: "(r18, **observed**
  surface, F5) ... a row is a nomination, never a removal receipt." F5 row:
  "own-uid scratch residue is **listed** ... reaping ... outside it."
  `corpus/README.md:242`: "frontier ... listed, never signalled".

The tool cannot make a residue class go away, bound it, or authorize anything
about it — it reads `/proc` and prints rows. "Governs" is the verb the lane uses
elsewhere for surfaces under receipt authority (e.g. r17 "jj-colocated
repositories governed", `LOG.md:946`, where refusal rules actually bind). A
reader comparing the r17 row ("governed" = enforced receipt roots) to the r18
row ("governed" = prints a list) gets a false equivalence — exactly the
premature-saturation pattern the coverage axis guards against. **Smallest fix:**
s/governs/lists/ in SCORECARD :13 and s/classes governed/classes observed/ in
lesson :8. One word each; no structural change.

### F2 — MODERATE (coverage): F5 is filed under `## Work surfaces`, which PROVINCE's own Core/Frontier section defines as Core — while F5 itself says frontier

- `PROVINCE.md` adds the process-residue bullet under `## Work surfaces
  (resolve and re-verify each round)` (diff hunk at old :28).
- The same file's `## Core / Frontier / Adjacent` states: "**Core** — the
  surfaces under `## Owns` and `## Work surfaces` above." By that definition
  the new bullet *is* Core.
- The same file's F5 row says: "F5 process residue (r18) — own-uid scratch
  residue is listed (tool + gate, no knowledge entry yet, so it **stays
  frontier**)". `corpus/README.md:242` agrees (frontier table). The round-18
  lesson :28 agrees ("candidate admit, frontier only").
- The frontier promotion rule itself requires an admitted `corpus/knowledge/`
  entry *and* a SKILL rule; the SKILL rows exist (`SKILL.md:172-174`) but the
  knowledge entry does not (lesson :75, "no knowledge entry (F5 frontier)" —
  self-consistent).

So process residue is simultaneously Core (by structural placement) and
Frontier (by every explicit label). The fix is not a tradeoff — it is a
placement defect: the bullet's *content* is correct (it even says "(r18,
observed surface, F5)"), it just sits in a section whose own definition makes
it Core. **Smallest fix:** move the process-residue bullet out of
`## Work surfaces` into the F5 frontier row (it already duplicates the same
facts), or relabel the section so frontier surfaces are excluded from Core.

### F3 — MODERATE (coverage): the live 65 = 65 agreement never exercises `argv-path-gone`, the one class where the two implementations' predicates diverge

Verified arithmetic on the committed records:

```
git show 5efb519:census/round-18/proc-census-live-1721.tsv | tail -n +3 | wc -l     → 65
git show 5efb519:census/round-18/leak-count-live-1721.json (pids)                    → 65
LC_ALL=C comm -3 <(tool pids, sorted) <(leak pids, sorted) | wc -l                   → 0
tool reasons: 58 cwd-deleted, 7 fd-path-gone, 0 argv-path-gone
leak reasons: 58 cwd-deleted, 7 fd-path-gone, 0 argv-path-gone
```

The "symmetric pid difference 0" claim is **true on the recorded data**. But
both counters saw zero `argv-path-gone` rows, so live agreement validates only
2 of 3 claimed classes. The third class is exactly where the two
implementations encode different predicates:

- `tools/souji-proc-census.sh` `read_process_argv` (:196-214 region): a
  candidate is an argv element that is either `/*` or `--*=/*` (assignment
  after a `--flag`), and it must additionally satisfy `! -e $candidate` and a
  gone top-level scratch dir.
- `census/round-18/leak-count.py` `PATH_RE` + `_argv_missing_scratch_family`:
  a regex finds `/var/tmp|/dev/shm|/tmp` substrings **anywhere inside an argv
  element** (skipped only when the match is preceded by `/`), requiring only
  the top-level scratch dir gone — it does not require the matched path
  itself to be missing.

Concrete divergent input (constructively derived, not executed): a process
with argv element `NOTE=/var/tmp/gone-top/x` — leak-count counts it
(regex match, top-level gone), the tool does not (`NOTE=` is neither `/*` nor
`--*=`). Also `--json /var/tmp/<absent-top>/out.json` makes **leak-count count
its own invocation** (it never excludes its own pid tree; the tool's
`is_self_tree` does — :126-137), inflating its total by 1 vs the tool on the
same world; the committed run happened to write to a non-scratch path so this
did not fire. Live "blind agreement" is therefore demonstrated only on the two
classes whose predicates the two implementations share shape. **Smallest fix:**
either (a) seed one argv-path-gone specimen on the host before the next live
pair, or (b) disclose in the lesson/SCORECARD row that live agreement covers
cwd-deleted + fd-path-gone and the argv class is fixture-verified only —
one sentence. Also add a self-exclusion to leak-count or disclose the
`--json`-in-scratch self-count (latent, unexercised).

### F4 — MODERATE (coverage/calibration): souji text contradicts the watchdog signal exception in three places

The r18 boundary text, `PROVINCE.md` `## Refuses`: "**Signalling any process
except the process group the census itself forked for one repository** (the
r18 repo-timeout watchdog)." Q32 last sentence: "The census watchdog's signal
to the group it forked is **the only signal souji tools send**."

Counter-evidence in the same landing:

1. `tools/souji-proc-census.sh` header line 3: "It never signals a process
   **outside its selftest**." — i.e. it *does* signal inside its selftest:
   `cleanup_selftest` runs `kill -KILL -- "-$pid"` on the five
   `setsid`-spawned worker groups. Q32's "only signal souji tools send" is
   falsified by the very tool the criterion owns, on its own documented
   selftest path. SKILL row `souji-proc-census` (:172) repeats the flat
   "never signals" in the write-scope column while its verdict cell names
   `--selftest` — the same flattening.
2. `tests/fixtures/r18-proc-census.sh` `cleanup_children` →
   `os.killpg(pid, SIGKILL)` on every spawned worker; `run_tool` →
   `os.killpg(SIGKILL)` on a timed-out census. The SKILL row itself says it
   plainly (:173): "kills exactly the processes it started". Those are not
   "the process group the census itself forked for one repository".
3. `census/round-18/run-matrix.py` `kill_session` (:87-140) SIGKILLs every pid
   whose `/proc/<pid>/stat` field 6 equals the suite's session id —
   session-wide, explicitly *not* the census-forked group (header :8-9:
   "killed by session ID"). The r15/r17 fixtures mandate the same
   session-wide kill (`r15-census-config.py` :269-292,
   `r17-census-hygiene.py` :149-168) — Q30 *requires* it.

Note what is *not* a contradiction: the `## Adjacency` mori wording was
correctly rewritten in this diff ("souji acts on artifacts and never on
processes" → "lists only its own uid's scratch residue"), and the census
watchdog really does signal only the worker group it forked
(`tools/souji-census.sh` :1478-1500, `set -m` worker group, watchdog
`kill -TERM/-KILL -- -$pgid`). The defect is that the Refuses exception and
Q32's "only signal" sentence are scoped to exactly that one site while three
other sanctioned souji signalers (selftest, fixture cleanup, runner session
kill) exist in the same tree. **Smallest fix:** widen the exception once, in
both places: "…except the process group the census forked for one repository
and any process group or session a souji tool, selftest or fixture itself
spawned" — which is the invariant every implementation already satisfies.

### F5 — MINOR (calibration): the header-only stub arm is meaningful but mislabeled as "the b576341 state"

- The stub arm exists and is recorded: `.ufo/waves/round-18/w1/
  ProcCensusFixture.md:31-47` captures a run against a header-only stub →
  fixture exit 1, P1 and P2 FAIL. That is a real vacuity falsifier — it proves
  the gate is not satisfied by a tool that emits only schema (`# boot_id` +
  TSV header), the exact degenerate case `CriticC3Measure.md:7` warned would
  satisfy a surface-existence claim. Meaningful, keep it.
- But `corpus/lessons/round-18.md:8` calls it "(no capability, the b576341
  state)" and `SCORECARD.md:13` echoes "(the no-capability state)". At the
  true baseline the fixture cannot even start: `r18-proc-census.sh:57-60`
  exits 2 "tool not readable" when `--tool` is absent — which is what
  b576341 has (no `tools/souji-proc-census.sh`; `git ls-tree` empty, per
  `ConnClaimSeparability.md:113`). So the stub arm is a *degenerate-tool
  probe*, not a replay of the baseline; the "before" capability count rests
  on file absence, not on the stub run.
- Additional bound on its power: it tests only "header with no detection".
  A stub echoing the header plus canned rows `1 1 1 1 0 0 R - cwd-deleted x`
  would fail differently (malformed pids caught, but a stub emitting
  plausible-looking rows for nonexistent pids is only rejected because P1/P2
  pin *this fixture's* real pids — good enough, but the arm is one mutant,
  not a mutation suite). **Smallest fix:** drop the parenthetical "(no
  capability, the b576341 state)" or reword to "(degenerate tool emitting
  only the output schema)".

## What holds

- The tool is genuinely list-only in census mode: no `kill`, `rm`, or write
  outside its selftest paths in `census()`; `is_self_tree` self-exclusion;
  uid filter via `/proc/<pid>/status`; never environ. Reads
  `stat,status,cmdline,cwd,fd,wchan` only — matches Q32's read set.
- Reason precedence `cwd-deleted` > `argv-path-gone` > `fd-path-gone` is
  implemented in the tool (:300-313), asserted by P1/P2/P9 in the fixture,
  and matches leak-count's `_primary_reason_and_family` ordering.
- `# boot_id` first line + (pid, starttime) identity binder present; P11 pins
  starttime to `/proc/<pid>/stat` field 22 — the pid-reuse binder Q32 asks
  for is real.
- Fixture P1–P11 covers all three classes plus boundary case P10 (deleted
  nested dir under a *live* top → absent) — a real negative control for the
  top-level-gone rule.
- Live 65 = 65 with symmetric pid difference **0** — recomputed from the two
  committed records; claim verified, not just plausible.
- No stray "never terminates processes" text survives: the old Adjacency
  sentence was rewritten in this diff; `git grep` on authority files shows
  no remaining instance of the pre-r18 absolute.

## Verdict: PARTIAL

The substrate is sound — real tool, real fixture with negative controls, real
blind counter, verified live equality — but the claim's *wording* and
*placement* overclaim on the coverage axis in four fixable ways:

- F2 (frontier filed as Core) is the sharpest: the same file contradicts
  itself structurally; a judge reading `## Core` gets a different answer than
  F5's own row.
- F4 ("only signal souji tools send") is falsified by three sanctioned
  signalers in the same commit, including the tool's own selftest.
- F3 is a coverage-strength limit, not a lie: 65=65 is true and verified, but
  the class where the two predicates provably diverge was never exercised
  live.
- F1 ("governed") and F5 (stub-as-baseline label) are one-line
  recalibrations each.

None requires rejecting the approach; all are smallest-correction wording or
a one-specimen evidence gap. Recommended fixes (priority order): move the
PROVINCE process-residue bullet out of `## Work surfaces` (F2); widen the
signal exception in PROVINCE Refuses + Q32 + SKILL :172 (F4); "governs" →
"lists" in SCORECARD/lesson (F1); restate the stub arm as a degenerate-tool
probe (F5); seed or disclose the argv-class live gap + leak-count
self-exclusion (F3).

Report: .ufo/waves/round-18/w2/CriticC3Axis.md
Tooling: none installed or upgraded (pacman paused; reads sufficed).
