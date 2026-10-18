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
