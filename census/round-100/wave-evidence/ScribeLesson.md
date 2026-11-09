# ScribeLesson — round-100 lesson skeleton (souji, wave w1)

Seat: ScribeLesson (godspeed). Lane: `souji-shokunin` @ `a662bb0d7e033cc5ceccd70b52eb234404300845`.
Scratch: `/fast/scratch/hyaku/souji-r100/ScribeLesson/` (deleted before yield).
Wave dir (owned): `.ufo/waves/round-100/w1/ScribeLesson/`.

**Deliverable:** the round-100 lesson **skeleton**, with every heading of the frozen shape and every
L1-owned value left as a named `{{PLACEHOLDER}}`. Two byte-identical copies (sha256
`79fb9f12c349ef9542f8215be51d969194e091e8a4715eb839682881ddd7ba5d`):

| path | role |
|---|---|
| `corpus/lessons/round-100.md` | the canonical lesson path the Target names (uncommitted; the L1 lands it) |
| `.ufo/waves/round-100/w1/ScribeLesson/round-100-skeleton.md` | the byte-identical copy inside this seat's owned dir |

`cmp` reports the two files identical. **This seat did not commit, push, or mutate git/jj state.**
The L1 remains the sole integration owner of the lesson file.

---

## 1. Headings the skeleton carries

The file contains every heading of the frozen shape, in the r99 lesson's order and naming:

| # | heading (exact text in the file) | line |
|---|---|---|
| 1 | `# Round 100 — {{TITLE_C1_CLAIM}} (C1 {{C1_VERDICT_WORD}}); {{TITLE_C2_CLAIM}} (C2 {{C2_VERDICT_WORD}})` (title line; names which claim is admitted-candidate and which is not, with the verdict word) | 1 |
| 2 | `## Claims and verdicts` | 7 |
| 3 | `## Gate` | 18 |
| 4 | `## Mistakes` | 44 |
| 5 | `## Wave findings (summary; full verdicts in \`census/round-100/wave-evidence/\`)` | 49 |
| 6 | `## Trend verdicts (lane)` | 53 |
| 7 | `## Frontier` | 59 |

Verified: `grep -n '^#'` on the skeleton → 7 heading lines (1 title + 6 sections), 61 lines total.

Structural notes the L1 should keep when filling:
- **Title line** carries both claim clauses *and* both verdict words, so the admitted-candidate claim and the
  non-admitted claim are named in one line as the Target requires.
- **Claims and verdicts** — one bullet per claim (C1, C2). Each bullet carries the **measured number**
  (`{{C1_NUMBER}}` / `{{C2_NUMBER}}`), the **receipt path** (`{{C1_RECEIPT_PATH}}` / `{{C2_RECEIPT_PATH}}`)
  and the **commit it was measured at** (`{{C1_COMMIT}}` / `{{C2_COMMIT}}`), plus the control lines
  (`{{C1_CONTROL_R99}}`, `{{C1_CONTROL_CM8}}`, `{{C1_CONTROL_MNOPPID}}`) and the C2 bidirectional legs
  (`{{C2_LEG1}}`, `{{C2_LEG2}}`).
- **Gate** — the source-rows-re-opened table names all three required rows (**S075, S332, S368**) with
  URL / access / located quote / location cells left for the scout's live re-open; then the assimilation
  `none` line and the considerthese `none` line.
- **Mistakes** — exactly **one row**, with the class / evidence pointer / captured-by / fix /
  "shown able to fail" line all left blank for the L1.
- **Trend verdicts** — exactly three lines (expansion / quality / discernment), each with a placeholder
  verdict word and a placeholder note.
- **Frontier** — one line.

## 2. Every placeholder, by name

**48 distinct placeholders.** All are unfilled by design — the L1 fills them. Grouped:

**Title (2)** — `{{TITLE_C1_CLAIM}}`, `{{TITLE_C2_CLAIM}}`

**C1 (8)** — `{{C1_CLAIM_SENTENCE}}`, `{{C1_VERDICT_WORD}}`, `{{C1_NUMBER}}`, `{{C1_RECEIPT_PATH}}`,
`{{C1_COMMIT}}`, `{{C1_CONTROL_R99}}`, `{{C1_CONTROL_CM8}}`, `{{C1_CONTROL_MNOPPID}}`

**C2 (8)** — `{{C2_CLAIM_SENTENCE}}`, `{{C2_VERDICT_WORD}}`, `{{C2_NUMBER}}`, `{{C2_RECEIPT_PATH}}`,
`{{C2_COMMIT}}`, `{{C2_LEG1}}`, `{{C2_LEG2}}`, `{{C2_ROW_COUNT}}`

**Gate (15)** — `{{SCOUT_SEAT}}`, `{{S075_URL}}`, `{{S075_ACCESS}}`, `{{S075_QUOTE}}`, `{{S075_LOCATION}}`,
`{{S332_URL}}`, `{{S332_ACCESS}}`, `{{S332_QUOTE}}`, `{{S332_LOCATION}}`, `{{S368_URL}}`, `{{S368_ACCESS}}`,
`{{S368_QUOTE}}`, `{{S368_LOCATION}}`, `{{GATE_SOURCES_CENSUS_LINE}}`, `{{GATE_NON_AUTHOR_LINE}}`

**Mistakes (7)** — `{{MISTAKE_NUMBER}}`, `{{MISTAKE_TITLE}}`, `{{MISTAKE_CLASS}}`, `{{MISTAKE_EVIDENCE}}`,
`{{MISTAKE_CAPTURED_BY}}`, `{{MISTAKE_FIX}}`, `{{MISTAKE_SHOWN_ABLE_TO_FAIL}}`

**Wave findings (1)** — `{{WAVE_FINDINGS_SUMMARY}}`

**Trend verdicts (6)** — `{{TREND_EXPANSION_VERDICT}}`, `{{TREND_EXPANSION_NOTE}}`,
`{{TREND_QUALITY_VERDICT}}`, `{{TREND_QUALITY_NOTE}}`, `{{TREND_DISCERNMENT_VERDICT}}`,
`{{TREND_DISCERNMENT_NOTE}}`

**Frontier (1)** — `{{FRONTIER_LINE}}`

Verified by `grep -o '{{[A-Z0-9_]*}}' … | sort -u | wc -l` → **48**.

> **The L1 must fill or the lesson is defective.** Every one of the 48 is currently unfilled, by the
> seat's instruction ("never invent a number"). The only non-`{{…}}` content in the file is the
> fixed scaffolding plus the **capture-verified quote cross-check note** under the Gate table (see §4),
> which is measured on committed captures and is labelled as *not* a live re-open.

---

## 3. Finding (with reproducer) — the r100 session key cannot own the T1 escapee

This is a **finding for the L1, not an edit**: predicates are L1-frozen, and this seat changed no
predicate. It bears directly on the C1 frozen target and on the Mistakes row.

**F1 (operability, HIGH) — the frozen session key misses the escapee it exists to reap; the r100
counter degenerates to the r99 do-nothing on the escapee leg.**

Reproducer: `.ufo/waves/round-100/w1/ScribeLesson/repro/repro_session_key.py`
(output: `.ufo/waves/round-100/w1/ScribeLesson/repro/out-session-key.txt`)

Command run (cwd `/fast/scratch/hyaku/souji-r100/ScribeLesson`, exit code observed):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-100/w1/ScribeLesson/repro/repro_session_key.py /fast/scratch/hyaku/souji-r100/ScribeLesson/rerun
```
exit **1**; observed lines:
```
COUNTER-SHA256 f71b2155cb9f68cd75d5f56c9a50a0b941f4ed7b26aece7489486e8bed777abe
RECORDED-SPAWN spawn_pid=3515311 spawn_starttime=7880339 spawn_sid=3515311
ESCAPEE pid=3515315 ppid=1525 pgrp=3515315 sid=3515315 starttime=7880341
ESCAPEE argv_carries_token=True
SESSION-MEMBERS spawn_sid(3515311) -> [3515311]
SESSION-MEMBERS escapee_sid(3515315) -> [3515315]
SID-ALIASING escapee_sid==own_pid: True  spawn_sid==spawn_pid: True
PREDICATE branch(a) pid==spawn_pid AND starttime match : owned=False
PREDICATE branch(b) sid==spawn_sid AND starttime>=spawn : owned=False  (sid_escapee=3515315 vs spawn_sid=3515311)
OWNED_BY_SESSION_KEY = False
STRUCTURAL escapee_sid != spawn_sid is forced by setsid(2) creating a NEW session (S368): True
VERDICT escapee_owned=False  (r100 rule reaps it? NO -> ESCAPEE LEAKS, alive=1)
```

**What was measured.** The reproducer imports the *committed* r100 counter's own helpers
(`_proc_stat`, `_proc_sid`, `_proc_starttime` from `census/round-100/c2-setup-arms.py`, sha256
`f71b2155…`) and applies the *exact* `_reap_owned` ownership predicate written at
`census/round-100/c2-setup-arms.py:197-206` to a live chain built with the counter's own T1 spawn
shape:

```
counter --(Popen start_new_session=True)--> probe(pid=P)   <- the counter's recorded spawn pid
probe   --(Popen start_new_session=True)--> fixture(pid=F)
fixture --fork--> E, E calls setsid()                      <- the T1 escapee
```

Nothing was signalled: the reproducer evaluates the predicate only; the escapee child exits on its own.
No kill run on any process the counter did not plant in this round's fixture.

**Why it is structural, not a tuning miss.** `SESSION-MEMBERS` shows **both** sessions are
**singletons**: the recorded spawn session contains only the spawn pid, and the escapee's session
contains only the escapee. Because `setsid(2)` *always* creates a **new** session (S368), a process
that called `setsid()` can never share the session id of a pid recorded before it — the two ids are
equal only in the degenerate case where the escapee *is* the recorded spawn pid. Recorded
`spawn_sid == spawn_pid` is `True` (the probe is its own session leader, because `one()` spawns the
arm probe with `start_new_session=True`), and the escapee's `sid == own_pid` is `True` (it leads its
own fresh session). **No value the counter could have recorded at spawn can match the escapee's
session id.** The session key is therefore structurally incapable of satisfying the frozen leg
`ESCAPEE-ALIVE alive=0` (`plans/round-100.md:17-19`), and `m_noppid` (session key removed) cannot
make that leg fail — the two mutants are indistinguishable on it, so the experiment is **vacuous on
the escapee leg** exactly as Q175's clause (`plans/round-100.md:27-31`) was written to catch.

**Consequence for the C1 triple and the decoy leg.**
- Leg (1) `alive=0` is unreachable via this key ⇒ C1's primary target cannot be met by this
  implementation ⇒ the expected verdict is the r99 do-nothing outcome (`alive=1`), and the claim
  must be withdrawn to an honest stop or re-scoped.
- Leg (1)'s decoy half (`verdict=spared`) is satisfied **for free**: a key that matches nothing
  kills nothing. It therefore carries **no discrimination** over the r99 counter (which already
  spared, `census/round-99/records/c2-decoy-r99.txt`: `DECOY-PLANTED n=83 dead=0 alive=83`,
  `DECOY-SUMMARY verdict=spared`). The CM8 leg stays non-vacuous (`census/round-99/records/c2-decoy-cm8.txt`:
  `dead=82 alive=1`, `verdict=killed`), because argv-only does reach the decoy.
- The shipped decoy test cannot falsify branch (b): `census/round-100/c2-decoy-test.py` is
  **byte-identical** to `census/round-99/c2-decoy-test.py` (`diff -u` → no output) and plants every
  decoy with `start_new_session=True` (`census/round-100/c2-decoy-test.py:101-105`), i.e. a
  fresh-session decoy — the one shape the session key trivially spares.

**Captured-by.** Independently reported by the peer attack seats before this seat's reproducer was
written: `ReviewerC1Predicate` (attack (a), "the session-key branch misses the escapee it exists to
reap"; attack (b), a forked non-`setsid` decoy inherits the spawn session and is over-killed), and
`ConnectorOverlap/session-key.txt` (`KEY … spawn_sid=3397888 sid==spawn_sid:False sid==own_pid:True`
for both the fixture and the escapee). This seat's contribution is the **predicate-level proof
against the committed counter bytes** (importing the counter's own helpers and applying its own
`_reap_owned` branch), plus the singleton-session measurement that shows the mismatch is forced by
`setsid(2)` rather than by a wrong recorded value.

**Suggested Mistakes row (for the L1 to accept or rewrite; this seat did not edit the lesson):**
class *ownership key that cannot reach its own target*; evidence pointer
`.ufo/waves/round-100/w1/ScribeLesson/repro/out-session-key.txt`; captured-by *Q177's positive-reap
clause and Q175's vacuity clause — the pre-freeze gate froze a session key whose target had left the
session by construction (S368)*; fix *an ownership key must be shown to reach the process it exists
to reap on the fixture it runs on, before it is frozen — the only in-lineage mechanism that reaches
the orphaned escapee is the r98 counter-child/subreaper net (`census/round-98/c2-setup-arms.py:189`,
`:206-221`), not a session id*; shown able to fail *the reproducer exits 1 with
`OWNED_BY_SESSION_KEY = False` and `ESCAPEE LEAKS, alive=1`*.

---

## 4. Gate-table cross-check (measured on committed captures only)

The skeleton leaves the Gate's live-fetch cells for the scout seat. To help the L1 cross-check, this
seat verified the three rows' located quotes **against the committed captures** (NOT a live re-open):

```
python3 - <<'EOF'  # tag-stripped, whitespace-normalized text of each capture
… S075 capture census/round-98/srcs/proc_pid_stat.5.html (sha256 0f04d78946538fd8…)
… S075 field 6  "The session ID of the process."                 occurrences=1
… S075 field 22 "The time the process started after system boot." occurrences=1
… S075 field 4  "The PID of the parent of this process."         occurrences=1
… S368 capture census/round-96/srcs/setsid.2.html (sha256 52cbc1904742df69…)
… S368 "The calling process also becomes the process group leader of a new process group in the session"  occurrences=1
… S332 capture census/round-83/srcs/linux-array.c-v6.17 (sha256 17f2318d5b29740c…)
… S332 do_task_stat() lines 590-594 = seq_puts(m," (") / proc_task_name(m,task,false) / seq_puts(m,") ") /
      seq_putc(m,state) / seq_put_decimal_ll(m," ",ppid)   — each fragment occurrences=1
```

Note for the L1's Gate row for S332: the SOURCES-row quote is a **space-joined concatenation** of
five source lines, so it does not occur literally in the capture (`occurrences=0` for the joined
string); each fragment occurs exactly once and the emission order is ppid-as-field-4 at capture lines
590-594. The skeleton says so in the Gate's capture-verified note so the L1 does not record a
verbatim quote it cannot locate.

**C2's two legs, measured on this lane's bytes** (the L1 re-measures at the landing tip):
```
grep -c 'S332' corpus/knowledge/deadline-owned-reaping.md                    -> 1   (worktree); 0 at HEAD
awk -F'|' '/^\|[[:space:]]*S075[[:space:]]*\|/ {print $12}' corpus/SOURCES.md \
  | grep -c 'deadline-owned-reaping.md'                                       -> 1   (worktree); 0 at HEAD
grep -c '^| S[0-9]' corpus/SOURCES.md                                         -> 294 (no new row)
```
(exit 0 each; `git show HEAD:…` for the committed baseline prints 0/0 — the pre-repair state, as the
plan's "Before at base" line predicts.)

---

## 5. Commands run, exit codes, observed summary lines

All read-only git; no `add`/`commit`/`stash`/`checkout`/`reset`/`pull`/`push`, no mutating jj.

| command | exit | observed summary |
|---|---|---|
| `git -C … rev-parse --show-toplevel` | 0 | `/home/vgpnk/Projects/shokunin/souji-shokunin` |
| `git -C … rev-parse HEAD` | 0 | `bf990609bfc621e7175bc10e42472d07112cac39` (r100 plan commit; base `a662bb0d…`) |
| `git -C … status --porcelain` | 0 | ` M corpus/SOURCES.md`, ` M corpus/knowledge/deadline-owned-reaping.md`, `?? census/round-100/`, `?? corpus/lessons/round-100.md` (last = this seat's skeleton; uncommitted) |
| `sha256sum census/round-100/c2-setup-arms.py` | 0 | `f71b2155cb9f68cd75d5f56c9a50a0b941f4ed7b26aece7489486e8bed777abe` (bytes stable across my two reads, 12:24:40 → 12:31) |
| `diff -u census/round-99/c2-setup-arms.py census/round-100/c2-setup-arms.py` | 1 (differences) | only the `_proc_sid` helper + the `_reap_owned` branch (b) + `spawn = (p.pid, _proc_starttime(p.pid), _proc_sid(p.pid))` |
| `diff -u census/round-99/c2-decoy-test.py census/round-100/c2-decoy-test.py` | 0 (identical) | the r100 decoy test is byte-identical to r99's; it plants only `start_new_session=True` decoys |
| `python3 -B …/ScribeLesson/repro/repro_session_key.py <scratch>` | **1** | `OWNED_BY_SESSION_KEY = False`; `VERDICT escapee_owned=False (… NO -> ESCAPEE LEAKS, alive=1)` |
| `grep -o '{{[A-Z0-9_]*}}' …/round-100-skeleton.md \| sort -u \| wc -l` | 0 | `48` |
| `grep -n '^#' …/round-100-skeleton.md` | 0 | 7 heading lines (1 title + 6 sections) |
| `cmp corpus/lessons/round-100.md …/ScribeLesson/round-100-skeleton.md` | 0 | identical (sha256 `79fb9f12…`) |

**Tooling:** system `python3` only. Nothing installed or upgraded (no tool was needed); no pacman
transaction (all pacman transactions are PAUSED host-wide); no sysctl mutated; no host-mutation need
found. Read `/home/vgpnk/.omp/agent/RULES.md` first, as required.

**Paths touched by this seat:** `corpus/lessons/round-100.md` (new, uncommitted skeleton),
`.ufo/waves/round-100/w1/ScribeLesson.md` (this report), `.ufo/waves/round-100/w1/ScribeLesson/`
(skeleton copy + `repro/`). Nothing else. No `census/round-99/*` file was edited; no `MANIFEST.json`,
`.ufo/state/*`, `.scratch/*`, `.ufo/watchdog.log`; no fleet-root or sibling-lane file; `considerthese`
and `shokuknow` untouched (both absent from this lane).

---

## 6. Out of scope for this seat

- Landing/filling the lesson — the L1's job (the skeleton's 48 placeholders are the L1's to fill).
- Editing any predicate (the plan's A0.1, the counter, the decoy test, the probe) — L1-frozen.
- The live r100 counter run and the `m_noppid` / CM8 mutant runs — the executor and mutation-tester
  seats' measurements; this seat did not duplicate them, and did not run any kill.
- The C2 committed-byte re-measurement at the landing tip — the L1's.

## 7. Known limits of this seat's own work

- The Gate's three rows are **not** live-re-opened by this seat; only committed captures were checked.
  The live fetch, HTTP status and access date are the scout seat's cells, left as placeholders.
- The finding in §3 is a **predicate-level proof against the committed counter bytes**, not a live
  r100 counter run: no `ESCAPEE-ALIVE alive=` line exists yet for the r100 successor. The L1's live
  run is what turns it into the frozen measurement; this seat's reproducer shows the branch cannot
  fire on the escapee in the counter's own spawn shape.
- The 48-placeholder count and the heading list are properties of the skeleton **as written**; the L1's
  edits may add cells, which is expected.

---

## Artifact paths

| path | contents |
|---|---|
| `.ufo/waves/round-100/w1/ScribeLesson.md` | this report |
| `corpus/lessons/round-100.md` | the lesson skeleton (canonical path; uncommitted; L1 fills the 48 placeholders) |
| `.ufo/waves/round-100/w1/ScribeLesson/round-100-skeleton.md` | byte-identical copy of the skeleton (sha256 `79fb9f12…`) |
| `.ufo/waves/round-100/w1/ScribeLesson/repro/repro_session_key.py` | F1 reproducer (signals nothing; exit 1 = escapee not owned) |
| `.ufo/waves/round-100/w1/ScribeLesson/repro/out-session-key.txt` | F1 measured output (verbatim) |

Report: .ufo/waves/round-100/w1/ScribeLesson.md
