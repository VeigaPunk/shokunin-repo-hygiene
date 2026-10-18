# MINT — souji-shokunin (2026-10-18)

**Name:** souji (掃除, "sweeping"). Rejected alternatives recorded per
operator note: harai (祓 — too ritual), sarae (浚え — too obscure).

**Cause:** explicit operator directive (2026-10-18): "minting a new
shokunin responsible for cleaning and pruning stale artifacts, logs,
anything that's bloat from previous runs." The directive itself clears the
mint bar (`PROTOCOL.md` §Lifecycle, branch (b)); the demand instances below
are measured confirmations, two of which corrected the operator's figures at
mint time.

**Demand instances (evidence, measured 2026-10-18):**

1. **Fleet-root checkpoint bloat** — `b2f2efa` (2026-10-15) committed 15×
   `launch-*.json` checkpoint files, round prompts, `prior-owners.json`,
   and a 675 KB `interactive-wall.png` to the fleet root; still an ancestor
   of HEAD. (`git show --stat b2f2efa`; `git merge-base --is-ancestor
   b2f2efa HEAD` → true.)
2. **Superseded config snapshot** — `shokunin.conf.full-roster-20261015`
   claimed byte-identical to `shokunin.conf`; `cmp` measured **DIFFER**
   (3859 vs 4092 B). Corrected: a stale snapshot, unique among hygiene
   candidates because its receipt class differs (stale, not duplicate).
3. **Dead worktree metadata** — lore-shokunin: 19 prunable worktrees;
   game-dev-2d-shokunin: 5 (`git worktree list` both repos). 24 total.
4. **Scratch bloat beside live work** — kotodama-shokunin `.scratch/` =
   553M (`du -sh`), with ≥10 unpushed round-17..22 commits and a dirty
   tree → a false-SAFE here is the lane's worst failure and the r2 gate's
   known trap. (Operator note said 1.7G; measured 553M — corrected.)
5. **No existing lane removes anything** — tsukuroi "never installs,
   upgrades, or removes packages"; mori/kama/mado are detect-and-report;
   kagi owns credential hygiene only. See roster scan.

**Roster scan (rejected fit):** 22 lanes scanned 2026-10-18; per-lane
province sha256 + one-line rejection in
`.ufo/scopes/souji-mint-20261018/mint-roster-scan.json` (main repo).
Headline rejections: tsukuroi refuses removals (host repair); mori is
observation-only; kagi is credential hygiene; kumitate owns tooling code,
not artifact lifecycle; protocol/aggregator are integrator roles.

**Domain boundary:** fleet repository & workspace hygiene — receipt-gated
removal of stale, duplicate, and already-preserved artifacts; dry-run by
default; quarantine before delete; receipts: pushed /
moved-to-obsidian (ledger row) / stale. Refuses: history rewrite,
credentials, operator config, driver runtime, dirty/unpushed lane work,
publishing.

**Obsidian ledger:** `corpus/knowledge/obsidian-ledger.tsv` — source path +
sha256, vault path + sha256. Without a matching row nothing qualifies as
moved-to-obsidian. The ledger exists from mint; rows enter only when the
operator records an export (nothing records exports today — operator
statement, 2026-10-18).

**Probation:** ≥3 verified rounds before a roster row; recorded as fleet
`MANIFEST.json rounds[]` type `"mint"`. Planned r1–r3 (operator-approved):
r1 dry-run census of the demand evidence with zero false-SAFE verdicts
under non-author spot-check; r2 `souji-verify` tool that must return
NOT-SAFE on kotodama's unpushed state; r3 prune the 24 dead worktree
entries (metadata only) + a root-scratch removal list for operator
approval.

**Risk noted by operator:** rounds may hit the same MISSING_BINDING
routing block as other lanes — recorded in the fleet scope and the training
goal's stop rule.
