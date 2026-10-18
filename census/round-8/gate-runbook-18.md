# gate-runbook-18.md — gate-opening runbook for the souji quarantine flow

Seat S18, round 8, 2026-10-18T18:59-03:00. Independent fragment; parent integrates.

Purpose: round 7 closed 0-tickets fail-closed ("the quarantine flow stays
UNEXERCISED … the remaining gates are external", LOG.md r7). This runbook
enumerates every gate standing between the fleet and its first authorized
removal, states each gate's observed condition with command + output, names
the owner of the action that opens it, and fixes the execution procedure to
run once gates open — **proven end-to-end on a mktemp fixture fleet**
(transcript excerpts inline; machine evidence in `results/qrun-18.json`).
Nothing here authorizes a live removal.

Safety envelope of this runbook's own production: read-only over the live
fleet (no fetch/push/commit/branch/prune, no mv/rm outside /tmp mktemp);
both lane tools exercised only via `--selftest` and fixture runs; no
secret-shaped reads; `.ufo/state` and `.ufo/watchdog.log` not opened.

---

## 0. Tool readiness (precondition, verified today)

| Check | Command | Observed |
|---|---|---|
| receipt engine | `tools/souji-verify.sh --selftest` | `selftest: 24 checks, 0 failed`, exit 0 |
| fleet census | `tools/souji-census.sh --selftest` | `selftest: 32 checks, 0 failed`, exit 0 |

A gate check or execution step whose tool selftest is red is VOID — fix the
tool first (that is round work), never waive the check.

## 1. Gate inventory (observed state 2026-10-18 18:53–18:59 -03:00)

| Gate | What it blocks | State | Owner of the opening action |
|---|---|---|---|
| G1 operator sign-off | the 96 fleet-root approval rows | **OPEN pending signature** — receipts healthy, re-verified today | operator |
| G2 souji lane remote | any `pushed` receipt inside souji-shokunin | **CLOSED** — origin 404, 0 remote-tracking refs | operator (remote creation is operator-owned) |
| G3 pair adjudication at execution time | every ticket | **procedural, always required** (S15 rule, r7 plan) | round parent |
| G4 stale clock | stale-class candidates | **CLOSED until ≥ 2026-10-19, and blocked on citations/dirt** | time + lane owners |
| G5 unpushed lanes / locked worktrees | all sibling-lane artifacts | **CLOSED** — every candidate lane unpushed or locked | operator + lane owners |
| G6 fleet-root unpushed backlog | (indirect) receipt re-derivations at execution time | **OPEN with caveat** — 26 unpushed commits exist but none touch the 96 | parent verifies per-ticket |

### G1 — operator sign-off (the only gate between the fleet and its first removal)

Evidence:

```
$ wc -l census/round-3/operator-approval-list.tsv
97                                  # 1 header + 96 rows
$ tools/souji-verify.sh <6 sampled rows, spread 1/20/40/60/80/96>
VERDICT .../launch-chousa.json            SAFE  pushed  intro=b2f2efae7549 ref=refs/remotes/origin/master ancestor=yes
VERDICT .../prompts/kake.md               SAFE  pushed  intro=b2f2efae7549 ref=refs/remotes/origin/master ancestor=yes
VERDICT .../surface/kotoba.txt            SAFE  pushed  intro=b2f2efae7549 ref=refs/remotes/origin/master ancestor=yes
VERDICT .../measure-corpus.mjs            SAFE  pushed  intro=b2f2efae7549 ref=refs/remotes/origin/master ancestor=yes
VERDICT .../registry-home/critic.md       SAFE  pushed  intro=b2f2efae7549 ref=refs/remotes/origin/master ancestor=yes
VERDICT .../registry-home-rerun/scribe.md SAFE  pushed  intro=b2f2efae7549 ref=refs/remotes/origin/master ancestor=yes
```

Fleet origin is live (this is what makes these receipts verifiable at all):

```
$ git ls-remote origin HEAD          # in fleet root
35b17a60bd91ac8710c61ec731da969d7a52ede2	HEAD
```

Open condition: operator signs off (or dispositions) rows of
`census/round-3/operator-approval-list.tsv`. The list has been operator-seen
since r3 ("awaits operator sign-off", LOG r3/r5/r6; dissent-24 §2); the
single remaining prerequisite is the signature itself. On sign-off, the
parent executes §4 below for the signed rows with a fresh author/blind pass
or an explicit operator waiver of the pair requirement (dissent-24,
resolution ¶3).

Operator action (operator-owned; souji never performs it): reply to the
round report marking rows APPROVE / DENY / DEFER. No signature → no
removal, full stop.

### G2 — souji lane remote

Evidence (fresh, 18:56):

```
$ GIT_TERMINAL_PROMPT=0 git ls-remote origin HEAD   # in souji-shokunin
remote: Repository not found.
fatal: repository 'https://github.com/VeigaPunk/shokunin-repo-hygiene.git/' not found
$ git for-each-ref refs/remotes | wc -l
0
$ git log --branches --not --remotes --oneline | wc -l
13
```

Consequence: every `pushed` receipt inside the lane repo is
`pushed-unverifiable` — the r7 finding stands (tools/, tests/, census/
candidates all died on this gate). This gate does NOT block the 96
(fleet-root) tickets; it only blocks lane-internal cleanup.

Open condition: operator creates the GitHub repo `shokunin-repo-hygiene`
under the same account and pushes the lane's 13 local commits. Until then,
souji lane artifacts are quarantine-ineligible; do not re-litigate per
round — this runbook records the gate once.

### G3 — pair adjudication at execution time

Rule (r7 quarantine-plan, `authorization_rule`): a ticket exists only if an
author AND an independent blind seat both emit SAFE with the SAME receipt
class, and all three gates pass and are documented. Receipts age; the r7
verdicts are banked evidence, not standing authorization (dissent-24). At
execution time the parent re-runs §4 step 0 fresh regardless of how recent
the banked verdict is. Not waivable except explicitly by the operator.

### G4 — stale clock

Earliest stale eligibilities from r7 evidence: vault-shard entries
≥ 2026-10-19 ~14:00 -03:00; lore `.scratch/` dir mtime
2026-10-18T00:03:50-03:00 → eligible no earlier than 2026-10-19T00:04-03:00,
AND only if its live citation (lore LOG.md:3530) is retired and the dirty
state resolves (lore unpushed commit 6cec83a edits `.gitignore`, so
ignore-status is not durable). Current lore state: unpushed=3 dirty=1
(fleet census 18:56). Gate opens for a given candidate when `--stale-days`
math passes AND no live reference remains; verify per candidate, never by
clock alone.

### G5 — unpushed lanes and locked worktrees (fleet census 2026-10-18T18:56)

```
kotodama-shokunin   worktrees=1  unpushed=55  dirty=31  scratch=41,698,011,786 B
game-dev-3d         worktrees=1  unpushed=10  dirty=42  secret-shaped
game-dev-2d         worktrees=9  unpushed=10  dirty=3   wt-absent,wt-dirty (locked regs per r7)
audio-shokunin      worktrees=1  unpushed=24
kaidoku-shokunin    worktrees=1  unpushed=20  dirty=1
lore-shokunin       worktrees=1  unpushed=3   dirty=1   scratch=218,489 B
souji-shokunin      worktrees=1  unpushed=13  dirty=10  no-remote
```

Open condition per lane: owner/operator pushes or explicitly abandons the
unpushed work; gd2d's locked registrations additionally need unlock +
unique-commit disposition (r7: each wt branch carries 1 unique commit).
Kotodama additionally needs a settled per-file classification pass before
any number is believed (r6/r7: live-growing 40+ GB tree — do not freeze
counts). Souji does not push, unlock, or abandon on any lane's behalf.

### G6 — fleet-root unpushed backlog

`git log --branches --not --remotes --oneline | wc -l` → 26 at fleet root.
This does NOT invalidate the 96 (their intro commit b2f2efa is an ancestor
of origin/master; none of the 26 touch them — sampled re-verification above
passes with these 26 present). Caveat for execution time: if a future
unpushed commit touches a candidate path, gate1 fails for that path; the
step-0 re-check catches it per ticket.

## 2. Coherence finding — gate2 semantics for untracked artifacts (proposal)

The r7 rule requires gate2 (`git status --porcelain=v1
--untracked-files=all -- <path>` empty). Observed on the fixture and on
lore: an untracked artifact's own `?? <path>` line makes gate2
**permanently unpassable**, yet the installed tool emits `SAFE(stale)` for
the same file (fixture Section 1/3 below; lore in r7 failed exactly this
way). Under the rule as written, no untracked stale candidate can ever be
authorized while the tool classifies it SAFE — a standing tool/rule
contradiction, not a safety feature (gate2's purpose is detecting
*concurrent modification* of tracked content).

Proposal (for parent/judge adjudication, NOT self-applied here): refine
gate2 to "no porcelain line touching `<path>` other than the artifact's own
`?? <path>` entry". Tracked modifications and any third-party path still
fail the gate. Alternative unchanged-rule route: explicit operator waiver
per ticket, the mechanism dissent-24 already recognizes. Until adopted,
untracked stale candidates stay NOT-AUTHORIZED — fail-closed wins ties.

## 3. Second-check semantics — proven subtlety (do not skip)

Fixture Section 6 observed: after staging + commit + push, the tool on the
**quarantined copy** of the pushed file returns
`SAFE pushed intro=024899d…` — but `024899d` is the quarantine commit
itself (it *introduced* the copy). Tool-on-copy proves the copy landed in a
pushed commit; it does NOT re-prove the original receipt. The true second
check re-derives the ORIGINAL receipt without needing a live path:

```
intro=$(git log --diff-filter=A --format=%H -1 -- <original-path>)
git merge-base --is-ancestor "$intro" refs/remotes/origin/master   # must succeed
git log --branches --not --remotes --oneline -- <original-path>    # must print nothing
sha256sum <quarantine-copy>                                        # must equal pre-move hash
```

Fixture observed: `intro=11fe2b529d90…`, `ancestor-of-origin/master: yes`,
unpushed-touching `[0 lines]`, copy sha == pre-move sha. Rule: a second
check that consists only of re-running the tool on the copy is
NECESSARY-BUT-NOT-SUFFICIENT; always append the four-line direct
re-derivation. (Fixture also confirmed the trivially-honest half:
tool on the vacated original path → `NOT-SAFE unreachable` — expected, not
a regression.)

## 4. Execution procedure (fixture-proven; parent runs this when G1..G6 allow)

Proven on `/tmp/qrun18-fleet.737tRI` (mktemp, 2026-10-18 ~18:58): one repo,
bare origin, three artifact classes — A `reports/old-run.json` (tracked,
pushed), B `notes/local.txt` (tracked, unpushed), C `.scratch/junk.log`
(untracked, mtime 3d). Full transcript excerpts below; exit 0 throughout.

- **Step 0 — fresh gates per ticket** (any FAIL → NOT-AUTHORIZED, stop):
  ```
  gate1: git -C <repo> log --branches --not --remotes --oneline -- <path>   # empty
  gate2: git -C <repo> status --porcelain=v1 --untracked-files=all -- <path> # empty (see §2)
  gate3: tools/souji-verify.sh [--json] <path>   # SAFE with the ticket's receipt
  ```
  Observed: A gate1=0 gate2=0 SAFE(pushed) · B gate1=1 line → **never
  staged** (fail-closed exercised) · C SAFE(stale), gate1 vacuous, gate2
  `?? ` per §2.
- **Step 1 — pre-move integrity hash**: `sha256sum <path>` recorded
  (observed A `7ae43323…54f`).
- **Step 2 — stage into `<repo>/.ufo-quarantine/<utc-date>/`**: tracked
  paths `git mv` (path separators → `__`); untracked paths plain `mv`.
  Observed porcelain mid-stage: `R reports/old-run.json ->
  .ufo-quarantine/2026-10-18/reports__old-run.json` +
  `?? .ufo-quarantine/2026-10-18/scratch__junk.log`; copy sha == pre-move.
  Tracked staging MUST be committed before the hold (SKILL: "quarantine is
  a normal commit in the owning repo"); message names receipt class +
  evidence pointer; identity `souji-shokunin <souji@shokunin.local>`
  (fixture commit `024899d`, then pushed to the fixture origin).
- **Step 3 — hold**: ≥ one driver tick (450 s minimum; prefer 24 h for
  anything not `pushed`). Fixture hold = 0 s (mechanics only). During hold:
  quarantine path untouched, no commit, no delete.
- **Step 4 — second check**: tool on quarantined copy (§3: necessary,
  not sufficient) + the four-line direct re-derivation of §3 + copy sha
  equality. All four must hold or the delete is VOID and the move is
  rolled back (§5).
- **Step 5 — delete**: `git rm` the tracked staged copy, `rm` the
  untracked one; commit (same identity/message discipline); never `rm`
  outside `.ufo-quarantine/`. Observed post-state: quarantine dir 0
  entries, survivor B intact (`exists=yes`), `.scratch/junk.log` gone,
  final non-quarantine porcelain **empty**, fixture census verdict
  `clean` (unpushed=0 dirty=0).

Rollback (§5, any step before delete): `git mv` the staged copy back to the
original path (or plain `mv` for untracked), re-run step 0 to confirm
restoration; no other remediation is ever needed — this is why staging
exists.

## 5. What this runbook does NOT authorize

- No live removal, staging directory, mv/rm, commit, push, or remote
  creation. The only writes by this seat are this fragment,
  `results/qrun-18.json`, and mktemp fixture content (removed after
  evidence capture).
- No signature of the 96-row list; no waiver of G3; no gate2 refinement
  adoption (§2 is a proposal for the parent/judges).
- No freezing of live counts (kotodama et al.) — G5 numbers are
  round-8 observations, valid only at their timestamps.

## 6. Re-audit triggers (post-r8 standing list)

1. Operator signs/dispositions the 96 → parent executes §4 on signed rows
   with fresh step-0.
2. Souji lane remote created + pushed → re-open lane-internal receipts
   fleet-wide (G2 clears); re-run gates on tools/, tests/, census/
   archive candidates.
3. Fleet-root history touching b2f2efa lineage changes → all 96 receipts
   re-derived (dissent-24 trigger 3).
4. Stale clock crossings (G4 dates) → re-check citations + dirt per
   candidate before any stale ticket.
5. Any adoption of §2's gate2 refinement → untracked stale candidates
   become authorizeable under otherwise-identical rules; re-adjudicate
   lore `.scratch` first (it is the oldest blocked live candidate).

Evidence manifest: `results/qrun-18.json` (selftest results, live gate
outputs, sampled row verdicts, fixture transcript excerpts, findings).
