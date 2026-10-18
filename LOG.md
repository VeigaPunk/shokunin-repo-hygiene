# souji-shokunin — LOG (append-only)

## 2026-10-18 — mint (operator directive, orchestrator-minted)

Lane minted by explicit operator directive (2026-10-18): a cleaner shokunin
(掃除) for stale/duplicate/preserved artifacts. Demand evidence, measured at
mint by the orchestrator before scaffolding:

- `b2f2efa` (fleet root) — checkpoint files (15× `launch-*.json`,
  prompts, `prior-owners.json`, `interactive-wall.png`) committed to the
  fleet root; `git merge-base --is-ancestor b2f2efa HEAD` → true at
  2026-10-18. Command: `git show --stat b2f2efa`.
- `shokunin.conf.full-roster-20261015` — operator note claimed byte-identical
  to `shokunin.conf`; measured `cmp` → **DIFFER** (3859 vs 4092 B). Corrected
  fact: it is a superseded snapshot, not a duplicate — still a hygiene
  candidate via the `stale` receipt after diff review.
- lore-shokunin — 19 prunable worktrees of 20 total
  (`git worktree list | wc -l` → 20 lines incl. main; 19 marked `prunable`).
- game-dev-2d-shokunin — 5 prunable worktrees of 6 total.
- kotodama-shokunin — `.scratch/` measures **553M** (`du -sh .scratch`;
  operator note said 1.7G — corrected), with unpushed round-17..22 commits
  (`git log --branches --not --remotes --oneline | wc -l` → ≥10) and a dirty
  tree → NOT-SAFE. This is the r2 `souji-verify` gate's known-false-SAFE
  fixture.

Roster scan (rejected fit) per lane in
`.ufo/scopes/souji-mint-20261018/mint-roster-scan.json`; boundary in
PROVINCE.md; reasoning in MINT.md. Probation: ≥3 verified rounds before any
roster row; recorded as `MANIFEST.json rounds[]` type `mint`.

Corrections to earlier claims are new entries, never rewrites — the two
figure corrections above are the first.

## 2026-10-18 — round 1 admitted (claims: coverage + calibration)

**Claims.** C1 (coverage): dry-run census classifying every mint demand
instance. C2 (calibration): zero false-SAFE in the admitted table under
non-author spot-check.

**Dispatch.** Seat batch 1 of 64 on opencode-go never spawned (user
interrupted; lane switch). Batch 2 of 64 on opencode-go-6/deepseek-v4.1-flash
completed 788s, 64/64 fragments, 246 rows (`census/round-1/seat-*.json`,
`census.tsv`, `census-summary.json`).

**C1 verified.** 109/109 b2f2efa paths classified; parent loop
`git show --name-only --format='' b2f2efa` + per-file introducing commit vs
`origin/master` → 0 NOTPUSHED. 24 worktrees re-derived (19 lore + 2 gd2d
detached: dir absent + unique commits = 0; 3 gd2d named branches hold 1
unpushed commit each → NOT-SAFE). 18 lane recon rows (S48–S53). kotodama
set NOT-SAFE.

**C2 verified with the full process told.** Author-stage SAFE proposals: 6;
critic seat (S63, non-author) falsified 6/6 — 5 launch-*.json stale receipts
self-polluted by reference sweeps hitting the census's own fragments
(seat-01's own out shows hits only in seat-01.json/seat-54.json); seat-21
r87-C5 SAFE(pushed) conflicted with its own unreachable evidence. Parent
then re-derived the final table: 132 unique SAFE proposals (109 pushed +
21 metadata-prune + 2 root strays), 0 false-SAFE survive. Blind seats S54–61
(21 targets) all independently NOT-SAFE; their disagreement with final
SAFE(pushed) rows is traced to defect D1 below, not to missed evidence.

**Defects (lessons, corpus/lessons/round-1.md):** D1 fleet default branch is
`origin/master`, not origin/main — the receipt procedure must resolve the
default branch (blind seats stopped at pushed-unverifiable). D2 the
unreachable→NOT-SAFE rule misfires on worktree metadata seats; absent dir
IS the prune condition. D3 reference sweeps must exclude
`souji-shokunin/census/**`.

**Cross-domain (reported, not absorbed):** game-dev-2d-shokunin branches
wt-r98/99/100 each carry 1 unpushed commit — the 3 NOT-SAFE worktree
registrations stay until that lane pushes. kotodama `.scratch` measured
553M at mint (11:45) and 1.9G at 12:35 — live writes by its in-flight
round-22 work; the operator's "1.7G" figure is this time variance.

**Verdicts:** coverage improved (C1), calibration improved (C2), no axis
harmed. Nothing was removed — dry run throughout.

## 2026-10-18 — obsidian-cli probe (deferred integration task, pre-round evidence)

Per operator: Obsidian integration is a later task inside the training
(goal), not mint work. Probe results banked at
`../.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` (main repo):
official CLI bundled since Obsidian 1.12; host on 1.14.4 with `"cli":true`
in `~/.config/obsidian/obsidian.json`; one vault registered at
`/home/vgpnk/Documents/shokoknowledge`. `/usr/bin/obsidian` is the GUI
launcher — launching it as a probe spawns the app; the registered CLI shim
was not in `~/.local/bin` or `/usr/local/bin` at probe time (to-verify:
`obsidian-cli-inspector`, and the real entry point — first claim of the
integration task). Until then, vault-side receipt checks fall back to
read-only `sha256sum` under the vault path.

## 2026-10-18 — round 2 admitted (claim: operability)

**Claim O1.** tools/souji-verify.sh per spec tools/souji-verify.spec.md
(D1–D3 fixes), NOT-SAFE on kotodama, fixture self-test. Verified; no axis
harmed.

**Dispatch.** 64 seats on opencode-go-6 (8 fixture authors, 8 implementors,
16 runners, 8 reviewers, 8 adversarial, 8 compliance, 8 final judges); 49
completed / 15 failed on staggered waits — redundancy covered all critical
roles. ~40 min.

**Measurement.** Runner matrices: impl-11..16 at 11/11; impl-09/10 at 9/11.
Review probes (36/impl): 11 false-SAFE on unpushed-branch worktrees, 15
false-SAFE on stale-live, 10 selftest exit≠0 — all disqualified. impl-09
also failed F7/F8 in runners despite a 60/60 review. Parent harness:
selftest exit 0 + 5/5 live targets (kotodama NOT-SAFE unpushed=42
dirty=14–15; launch-tsukuroi.json SAFE/pushed; /tmp/r87-B1
SAFE/metadata-prune; conf snapshot SAFE/pushed; app.env NOT-SAFE
secrets-refusal) + F1 fixture spot probe. Winner **impl-12**, installed
byte-identical (sha256 7efda63bd760…, tests/results/INSTALL.json); tie with
13/16 broken by judge consensus (final-57).

**Defects recorded** (corpus/lessons/round-2.md): seat write-scope overstep
(a synthesized tools/souji-verify.sh installed by a seat — deleted);
fixture interface chaos (2/10 contracted protocol); compliance grep
over-strictness; signal hierarchy = runners > reviews.

**Operability:** 0 → 7 — a runnable, self-tested, live-verified verdict
tool. Capability row added.

## 2026-10-18 — round 3 admitted (claims: coverage + calibration) — PROBATION GATE CLEARED

**Claims.** C1 (coverage): prune the 21 SAFE(metadata-prune) worktree
registrations (metadata only). C2 (calibration): operator approval list
with zero false-SAFE. Both verified.

**Dispatch.** 64 seats on devin/deepseek-v4-1-flash-high (operator devin
test; the operator then directed devin/deepseek-v4-1-flash-max for all
future devin dispatches — recorded here). 64/64 completed, 404s.

**Execution (parent, serialized).** Gate re-check: lore + gd2d unpushed = 0
at act time (artifact-scoped reading of the dirty/unpushed rule; both
readings satisfied). Lore: dry-run listed exactly the 19 → pruned →
worktree list 20→1. gd2d: locked the 3 pinned named-branch registrations,
pruned (2 detached removed) → list 6→4, unlocked; main sha unchanged
(05a72899), wt-r98/99/100 branches intact with 1 unpushed commit each,
.git/worktrees holds exactly the 3 preserved admin dirs. Blind pairs 21/21
agreed (S57); gate seats S58–S64 all GO with 3 blockers handled: (B1) no
bare gd2d prune — lock mechanism used; (B2) wording — both readings
satisfied at execution; (B3) the 111-row contract re-cut to 96
approve-remove + 15 already-removed (fleet commit a1b44b1 had already
deleted the 15 shell strays; blobs survive in origin/master).

**Artifacts.** census/round-3/{seat-01..64.json, approvals-*.tsv,
operator-approval-list.tsv (96 rows), approval-summary.json}. The list
awaits operator sign-off; no file deletions this round.

**Verdicts:** coverage improved, calibration improved; no axis harmed.
Nothing deleted except the 21 authorized metadata registrations.
**Rounds 1–3 verified → probation gate satisfied; the roster row remains
the operator's decision.**

## 2026-10-18 — operator routing directive (session-scoped, post-r3)

Future deepseek-v4.1-flash dispatches in this session use **devin as the
provider at max effort**: model `devin/deepseek-v4-1-flash-max`. This
supersedes the training schedule's hyper lane for r4 (and r10). Rounds
scheduled on other families (luna-max, grok-4.7, glm-5.3, gemini-3.8,
gpt-6.1-sol-max) are unchanged.

## 2026-10-18 — round 4 admitted AMENDED (operator withdrew the obsidian claim)

**Claims as dispatched:** O1 obsidian-CLI capability + C1 calibration.
**Operator directive mid-round:** "forget the obsidian integration for
now" — O1 withdrawn; replaced by O1': standalone ledger-backed
moved-to-obsidian verification (the receipt machinery, Obsidian-free).
Completion-criterion obsidian-row requirement waived by the operator.

**Dispatch.** 64 seats on devin/deepseek-v4-1-flash-max (operator devin
test); 63/64 completed, ~72 min.

**Finding (banked for the operator).** The official Obsidian CLI has NO
usable entry point on this host: it is the app as a socket client to
$XDG_RUNTIME_DIR/.obsidian-cli.sock; registration is refused by an argv0
gate under the pacman wrapper; bounded socket probes returned 0 bytes.
Details: ../.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md (updated).

**Measurement.** 7 impls; runner matrices + 8 judges: majority converged on
impl-20 (selftest 35/35; refuses self-referential ledger rows — a false-SAFE
class rivals accepted; 4/8 judges dissented NO-CLEAN-CANDIDATE over fixture
rot, recorded). Parent battery: 4/4 decisive cases + real-vault live probe
(SAFE/moved-to-obsidian against
/home/vgpnk/Documents/shokoknowledge/Home.md with a temp ledger; cli=
unavailable; live ledger still header-only). Winner installed byte-identical
as tools/souji-vault-verify.sh (sha256 d312263a…).

**Verdicts:** operability improved (second tool live), calibration improved
(judge-dissent adjudicated by parent re-derivation, not by majority vote).
No axis harmed.

## 2026-10-18 — round 5 admitted (verification round; 3 material defects found and fixed)

**Dispatch.** 64 seats on openai-codex/gpt-6-luna-max; 64/64 in ~29 min.
Claims: V1 calibration (verdict audit of r1–r4), V2 coverage
(missed-items sweep), V3 operability (regression battery).

**Findings (non-author judges, material).**
(1) Symlink false-SAFE class in both tools — dir_digest dropped `-type l`;
fixed fail-closed (`symlink-present`); reproduction probe refuses;
selftests 24/24 + 35/35 green. (2) Local-master pushed fallback — both
tools could emit SAFE(pushed) from refs/heads/master alone; fixed to
`pushed-unverifiable`; spec amended. (3) r1 logs_tier.txt false-SAFE
(already deleted pre-census; no operational impact; procedure fix:
pushed corrections re-verify existence). Pin risk: 3 gd2d registrations
re-locked durably.

**Process findings** (lessons/round-5.md): r1 LOG mid-file insertion
(append-only violation, historical); r4 read-only claim vs a seat's
GUI-launch incident (disclosed, verdicts unaffected); SKILL.md doc drift
routed to r6.

**Correction discipline:** every finding carries a named finder, an
in-round fix with re-run evidence, or an explicit disposition. 0
unresolved contradictions at closure. Calibration improved; coverage
improved (gap table in census/round-5/seat-51.json); operability improved
(tools hardened, all batteries green). No axis harmed.

## 2026-10-18 — round 6 REJECTED as a round; deliverables completed by parent

**Dispatch.** 128 seats on xai-oauth/grok-4.7-fast; 96 completed / 32
failed. Claims: C1 docs drift→0, O1 tools/souji-census.sh, K1 kotodama
.scratch fully classified + handoff. 15/17 final judges: NOT-MET at their
measurement time (drift never applied; no census winner installed; live-tree
counts diverged). Per protocol the round files as REJECTED (claims not all
verified); the parent completed C1/O1 before filing and banked K1's
artifacts — judges' dissent preserved, never re-rolled.

**Parent completion.** (a) Both verdict tools fixed: pushed receipt now
also requires zero unpushed commits touching the path
(--branches --not --remotes; bare --not --remotes silently returns nothing
on git 2.55 — pitfall recorded). Probes: dirty+local-commit file →
NOT-SAFE(unpushed-commits-touching); clean file → SAFE(pushed); selftests
24/24 + 35/35 green. (b) tools/souji-census.sh installed (impl-33,
sha 11bf9cdf, selftest 32/32); two fleet runs byte-stable except live
deltas — kotodama .scratch = 40.4G and growing ~2.3MB/s. (c) SKILL.md
reconciled to installed behavior; AGENTS.md gained the seat-harness clause.
(d) K1 honest stop: full 388-child classification NOT achieved (seat
failures + live tree); parent snapshot + parent-signed handoff delivered
instead; kotodama stays NOT-SAFE/hands-off.

**Ledger.** r6 = failed (2/3 claims); the schedule continues at r7 — the
completion criterion's "12 admitted" is now unattainable verbatim; flagged
for the final completion audit.

## 2026-10-18 — round 7 REJECTED as a round (2/3); receipts deny every candidate

**Dispatch.** 24 seats on zai-coding-plan/glm-5.3-flash; 24/24. Claims:
C1 blind-pair receipts, O1 first quarantine exercise, K1 fleet delta.

**Findings.** Receipts denied everything: lore .scratch fails 3 gates
(untracked, live LOG reference, mtime too young); souji's own tracked
files are unpushed-tangled (its bookkeeping commits touch tools/, tests/,
census/); **the lane's remote does not exist (origin 404 — creation is
operator-owned), so every pushed receipt inside the lane repo is
unverifiable**. Calibration win: S02 caught the parent's column misread
(lore worktrees=3 was unpushed=3; registrations=0). Blind pairs agreed
everywhere; no candidate manufactured. K1: delta census run; live deltas
only; no new dead registrations.

**O1 NOT-MET** — the quarantine flow stays UNEXERCISED: no authorized
target exists in scope (the 96 approval rows await the operator; other
lanes are unpushed). Reported as such; nothing forced. Rounds r6-r7 are
the lane discovering its true boundary: the remaining gates are external
(operator sign-off, lane pushes, remote creation).

## 2026-10-18 — round 8 admitted (all 3 claims)

**Dispatch.** 24 seats on zai-coding-plan/glm-5.3-flash; 22/24 (2 failures
traced to host /tmp DISK QUOTA corrupting fixture runs — escalated).

**O1.** tools/souji-quarantine.sh = impl-01 (sha 5780ad75…) — the receipt-
gated quarantine flow as a fail-closed tool: engine-authorized stage 1 with
receipt pinning, git-mv/mv staging, hold, class-aware second check, delete
on PASS only. Selftest 63/63 (TMPDIR=/var/tmp); full flow exercised on
fixtures (DELETED/ABORTED/NOT-AUTHORIZED/SKIPPED/dry-run both outcomes);
96-row approval dry-run: 96/96 PASS, zero mutations. Live mutations
refused without env override.

**C1.** Pointer sweep: 111 tokens across reports r1-r7 + SCORECARD/LOG —
95 alive, 1 dead (confirms the r7 correction), 1 drift recorded.

**K1.** Gate-opening runbook (census/round-8/gate-runbook.md): exact
command sequences per blocked class, including the one-line quarantine
command for the signed 96 and the simulated post-push prune-ticket
regeneration for the gd2d pins.

**Notes.** r7's gate2 contradiction dissolved (untracked stale flows
clean); parent awk bug caught by the tool's fail-closed refusal; /tmp
quota is now host-critical. Operability +1 capability row.

## 2026-10-18 — operator routing amendment 2 (session-scoped)

Round 10 (the remaining deepseek-v4.1-flash round of the schedule) uses
the **hyper provider** (`hyper/deepseek-v4.1-flash`) instead of devin, per
operator request. All other routing stands.
