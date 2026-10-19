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

## 2026-10-18 — round 9 REJECTED (O1 NOT-MET); tools patched but uncertified

**Dispatch.** 24 seats on openai-codex/gpt-6.1-sol-max; 23/24. Red-team +
differential + rubric.

**Findings.** 23 deduplicated defect classes (union across four judges):
false receipts from environment/hostility (disappearing git, tr_TR
locale), authorization forgery (NUL rows, tab-spliced pins, ledger
revocation after capture), stale-sweep blind spots (hidden refs,
directory metadata only), nested-repo deletion via ancestor receipts,
second-check missing default-ref revalidation, git-2.55 linked-worktree
HEAD skew in unique=0, non--shokunin owner names hiding registrations,
index-write contract violation, SCORECARD numeric contradictions
(parent's drift — corrected same-day).

**State.** S17 patches applied (installed tools; selftests 40/51/91,
census 32; S08 universe clean) but fresh replays still reproduce unsafe
deletions: >=16 classes open. Tools are PATCHED-NOT-CERTIFIED: receipts
advisory, deletion authorization OFF. S18 candidates banked for
composition in r10 (not promotable alone). rubric-final.md banked;
scores LEGACY-UNMAPPED/UNRATED. K1 differential MET (bounded); C1 rubric
MET as prospective spec. Dissent preserved.

**Ledger.** r9 = failed. Hardening closure is r10's mission
(operator-rerouted to hyper/deepseek-v4.1-flash).

## 2026-10-18 — operator scheduling amendments 3-4 (session-scoped)

(3) Skip 128-seat xai-grok rounds — r6 already executed; no future grok
rounds remain. (4) sol-6.1 rounds use codex luna-max instead — r9 already
executed; no future sol rounds remain. Remaining schedule unchanged: r10
hyper/deepseek-v4.1-flash, r11 devin/glm-5-3-flash-max, r12
antigravity/gemini-3.8-flash.

## 2026-10-18 — round 10 REJECTED on O1 (3 residual census-contract); merge installed

**Dispatch.** r10 first attempted on hyper/deepseek-v4.1-flash per the
operator's test request: lane functional but ~829s per trivial agent —
functionally unusable for batch work (two interrupted batches, zero
completions; logged as the operator's hyper test result). Completed on
devin/deepseek-v4-1-flash-max (session fallback), 16/16 seats.

**Result.** Seven fix clusters (A-G) patched all three tools; composer
merged; certifier ran 15 corpora/reproducer suites: unsafe outcomes 3,
ALL one class — souji-census --compare accepts empty/near-empty prior
censuses (census-contract; originals preserved; no data loss). 121
conservative refusals. Delta vs r9: >=16 open classes -> 1. Merge
installed (selftests 40/51/91); tools remain NOT certified. r11 fixes
the census contract and re-runs the certifier suites before the
certification flips.

## 2026-10-18 — round 11 closed (operator: finish + push before reboot)

Census contract fix installed (cand-census-02; selftest 36/36; all three
cert-16 shapes refuse) — the last r9 defect class is closed in the tools.
Certification NOT granted: the r11 certifiers compromised evidence
integrity (cert-16 relay overwrites; verdicts on non-installed bytes) —
fail-closed says no certification on compromised evidence. Rubric scores
stay UNRATED. Re-certification under a no-relay protocol is the next
session's first task. Operator cancelled the 12-round goal after this
round; the lane stands at rounds 1-11 closed (1,2,3,5,8 admitted; 6,7,9,
10,11 filed honestly as failed/partial), probation gate already cleared
(>=3 verified rounds), lane repo pushed to origin.

## 2026-10-19 — operator sweep (execution): root-wide receipts + home-wide cache/tmp cleanup

**Directive.** Operator, 2026-10-18 late session: "use this shokunin to clear
stale artifacts and stale cache, look everywhere you can think of", scoped in
three steps: fleet root → `/home/vgpnk/` → `/tmp` (tmpfs, was 80% full).

**Removed — fleet root, receipt `pushed` (96 artifacts).** The r3 approval
list (`census/round-3/operator-approval-list.tsv`, 96 rows: interactive-l1
launch-*.json / prompts / surface / PNG / wave checkouts / conf snapshot /
commit-map) was re-derived at decision time: 96/96 SAFE(pushed) via
tools/souji-verify.sh (evidence: `census/operator-sweep-20261018/approval-list.tsv`,
`resume-verdicts.tsv`). Flow: souji-quarantine.sh staged 3 files then hung
(hit its 20-min driver timeout); completed manually per protocol — 93 staged
via `git mv` into `.ufo-quarantine/2026-10-19/`, hold (>25 min), second check
as hash-vs-origin: 94 copies byte-equal to `origin/master` blobs; 2
(launch-chousa/kagi.json) missing post-timeout, **restored from origin** and
hash-verified (`a75fc635…`, `fd94b883…`). Unpushed-touching=0 throughout;
`ls-remote` tip d6ac1b64 unchanged. Deleted from quarantine; committed at
fleet root as `e20f4fa` (lane identity). Two corrective commits followed
(`9c220bf`, `99819ec`): `git add -A` had swept in 10 live `.scratch/*.out`
(r10 certifier outputs) + the in-flight r11 report + a `.gitignore.tmp`
scaffold — all untracked again, files on disk. **Commits local; publishing
is operator-owned.**

**Removed — caches, quarantine-staged on /home (≈14G).** `~/.cache`: uv 11G
(pure package cache), chromium 1.8G (browser cache only; cookies/config live
in the refused `~/.config`), 14 fleet seat/round dirs (~1.6G; zero open
handles, zero fleet refs except s18 → s18 kept), 11 small stale CLI/seat
caches (deno, bun, gh, devin, hop-tester, adm-ev-r3, anchor-verifier,
bt3-re, d3-r9-review, d24-mirror, empty blender). Staged
`~/.cache/.souji-quarantine/20261018T2331-0300/`, 17-min hold, second check
(0 handles, 0 fresh writes) → deleted. `~/.cache` 28G → 14G.

**Removed — /tmp (tmpfs), age+handle receipts.** Census
(`tmp-census.tsv`): 8,562 items / 13G. OLD>24h band: 1,943 items / 1.1G
staged → 450s hold → second check (0 handles, 0 originals left) → deleted.
Operator then directed "free more": MID 1–24h band 6,443 items / 10.4G
staged the same way (all handles=0; infra/sockets/X11/systemd-private and
live-session FRESH items skipped; this sweep's own evidence files
name-excluded) → `/tmp` 13G → 65M. Process kill (evidence-backed): 3
orphaned r4 `souji-vault-verify.impl-17.sh` judge-fixture processes (~9h,
ppid=systemd, do_wait) each stuck on `sha256sum` of a **FIFO**
(`wait_for_partner`); killed parents+children, freeing their /tmp world
dirs. sqlite3 (3.53.4) checked per operator: live consumers = 1Password
(own `~/.config` DBs, refused zone, untouched) and the /tmp seat DBs
(inside the quarantined seat dirs; holders verified 0).

**NOT-SAFE — kept (the honest majority).** (1) kotodama `.scratch` 42G: the
r6 handoff push-gate is now OPEN (unpushed=0, dirty=0, two-pass delta ~0
B/s) but receipts deny every child — 256 children all have newest-file mtime
<24h (round-32 completion rewrote the tree today); the big three (r28-x58
9.4G, x58 7.8G, x37 3.4G) are additionally `secrets-refusal`
(secret-shaped descendants — kagi's province; never read). Re-sweep when
the tree ages past 24h (≈2026-10-20). A seat-archived COPY of the
interactive-l1 checkpoint tree exists inside `.scratch` — noted, no action.
(2) Engine-SAFE strays denied at the pre-removal reference gate: 107
pushed-receipt files — frozen gate fixtures cited in 8+ round reports,
28 plans/*-record-draft.md cross-referenced 3–7× per lane, research/round-18
logs cited by PREDICTIONS.md/HYGIENE.md (`stay-strays-verdicts.tsv`).
(3) `.tower/comms/log/activity.log` (engine SAFE/stale) treated as
operator-tooling runtime → refused-zone spirit. (4) lore `.scratch` (unpushed
lane), root `.scratch/*.out` + souji `err4.*` (live/too-young), gd2d
fixtures `__pycache__` (not scratch-type).

**Report-only (out-of-province or costly-to-regenerate; operator decides).**
`~/.cache/huggingface` 11G (model weights), `~/.cache/codex-runtimes` 1.7G
(codex daemon live), `~/.cache/ms-playwright` 681M, `~/.local/share/Trash`
694M, cargo `target/` 864M + 289M (ufo-fsd-alpha, modelbench),
`~/Projects/tog/node_modules` 22M.

**Calibration notes.** Pre-removal `git add -A` over live lanes sweeps
untracked work into hygiene commits — scope adds (lesson, two corrective
commits). The quarantine tool's per-target staging loop can hang; the
manual protocol (engine stage-gate → git mv → hash-vs-origin second check)
is an equivalent-or-stronger receipt path and is now exercised end-to-end
on live targets. Evidence: `census/operator-sweep-20261018/`.

## 2026-10-19 — operator decisions on report-only items (huggingface, Trash)

Operator directed deletion of two report-only surfaces from the
2026-10-19 sweep. (1) `~/.cache/huggingface` (11G, 3 models: bge-m3 4.3G,
Unlimited-OCR 6.3G, multilingual-e5-small 471M): 0 open handles (the running
python shims are provider lanes, not ML consumers); staged to
`/home/vgpnk/.souji-quarantine/hf-20261019/` with model manifest, 450s
hold, lsof second check, deleted. Re-downloadable from the hub on demand.
(2) `~/.local/share/Trash` (694M, 3 top-level entries): 0 handles;
already user-staged by definition — manifest captured to the same
quarantine dir, emptied to 0. Both operator-owned surfaces removed under
explicit operator directive; no receipts class applies (never fleet
artifacts).

## 2026-10-19 — round 12 (kaika campaign; steered r12, goal cancelled after r11)

Amendment to the r11 carry: the operator cancelled the 12-round goal after
r11 and the kaika orchestrator steered souji to r12 under the current
directive (grow the corpus, curate sources, learn from mistakes). The r11
carry — no-relay re-certification — is NOT this round's work; it is
Planned r13 and certification stays OFF (SCORECARD correction note).

Claims (evidence `census/round-12/`, gate record `corpus/lessons/round-12.md`):
- C1 calibration (lowest axis): an independent seat mined 52 own-mistake
  classes at dcc8b9e (`census/round-12/mistakes.md`; 28/52 had a rule that
  could catch a recurrence). New `corpus/QUALITY.md` (Q1–Q15, each citing
  its lesson); lesson `## Mistakes` maps 51/53 (M53 added; M27/M39 external).
  Mapped-criteria coverage, not demonstrated catches.
- C2 coverage + capability: `corpus/SOURCES.md` (33 rows opened 2026-10-19,
  A=29 B=3 C=1, 2 rejected with flips; contract census clean) and 5
  knowledge entries on new frontier rows F1, F3, F4 (README coverage map +
  `## Frontier`; PROVINCE Core/Frontier/Adjacent appended). ART candidate
  C3 (size census) rejected/deferred.
- C3 operability: gate `tests/fixtures/r12-maintenance-guard.sh` — on host
  git 2.55.0 a plain `git commit` prunes an expired, unlocked worktree
  registration (2→1, sync and default-detached); `-c maintenance.auto=false`,
  `worktree lock`, a fresh index keep it (2→2); the pruned detached HEAD's
  commit is unreferenced but present until gc prune expiry. Registered in
  SKILL.md; Pre-quarantine checklist gains right-repo, guarded-commit and
  pin rows; new error pattern "Git deletes without a receipt".
Re-verification (freshness): reviewer re-opened the git v2.55.0 sources and
reproduced the prune independently (`census/round-12/reviewer-preflight.md`);
post-integration reviewer + critic re-derived the Gate and every counting
command (`census/round-12/postreview.md`); their defects were fixed before
commit (dispositions in the lesson `## Gate`).
Incident: an L2's silent `cd` failure ran a fixture in the fleet-root main
checkout (4 throwaway commits c095ea1..b21278d on master, ~10 stray files);
reported to the orchestrator, who owns the repair; lesson `## Incident`, M53.
Provider exhaustion: three executor seats (SOURCES, K1/K2, K3–K5) died on a
provider rate limit (resource_exhausted) before writing; re-dispatched as
fresh seats (R12SourcesExec2, R12ExecGit2, R12ExecFs2).
Commit is local only: the standing operator rule "No push" overrides
MISSION.md's commit-then-push (PROTOCOL.md operator-gated hold).

## 2026-10-19 — round 12 closing note (measured commit)

Round-12 work commit: d7266c5e9493a3c78687af68d438c2584f75b3c0 (lane
identity, `-c maintenance.auto=false`, pathspec-limited). After-numbers
measured on it with a clean worktree: `census/round-12/after.txt` — C1
28/52 → 51/53 (mapped criteria), C2 entries 0→5 / frontier rows 0→3 /
SOURCES 33 rows census clean, C3 gate exit 0 with `selftest=PASS ids=6/6`
and guard rows 0→3. SCORECARD measured-commit cells point here. Self-
verdicts only; non-author verification (orchestrator) is pending.

## 2026-10-19 — round 12 post-review fixes (orchestrator adjudication)

Non-author review of d7266c5/de9187e returned HOLD / reject-as-submitted. Fixed in round 12,
append-only (`corpus/lessons/round-12.md` `## Post-review fixes`): S030 recheck `—`→`365d`;
K5 moved admitted→HELD (its Gate claimed a committed fixture that did not exist; its
`/dev/shm` device relied on Q15) with S024/S025 mined→queued; Q15 withdrawn by QUALITY Q16
(circular lesson pointer); K2 recheck corrected (`MANWIDTH=2000`, 6/6 defaults); C1 restated
as a rule-coverage count. After: C2 admitted entries 4 (+1 held), SOURCES mined=16 queued=15,
`TZ=UTC bash .tower/worktrees/kaika/fleet-census/scripts/sources-census.sh validate <worktree>`
→ `souji-shokunin ok`, exit 0. No new claims.
