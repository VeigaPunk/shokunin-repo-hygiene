# ConnSiblings — Sibling-Overlap Scan & Connector Synthesis (Round 26)

## Status
STATUS: PASS — Sibling overlap scan across 21 rostered lanes is clean (zero collision on F1 auto-maintenance, prereg-gating, or SCORECARD surgery); non-obvious connector move unblocks C2 K2 without relaxing frozen predicates or harming any axis.

## Evidence
- Lane HEAD revision: `ba8b54b85814dd980aa96050fe111c7cbfd4956a`; base: `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`.
- Sibling lane scan: 21 `PROVINCE.md` files, 19 `SKILL.md` files (all rostered lanes in `shokunin.conf`).
- Kumitate delegation evidence: `/home/vgpnk/Projects/shokunin/kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:14-17` explicitly delegates:
  > "jj and git substrate internals → souji: `souji-shokunin/corpus/knowledge/jj-colocation-receipts.md` ... and `git-auto-maintenance-prunes-worktrees.md` (linked worktrees pruned by maintenance, which this entry does not cover)"
  and `:195-196`:
  > "Linked-worktree pruning by `git maintenance` (souji) and jj workspaces in colocated repos (M7) are not demonstrated here."
- Kaidoku claim-gate evidence: `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-30/axis-fit-gate.py:1-24` verifies kaidoku's own `.ufo/waves/round-<N>/claims.json` (surface/unmoved_command and pre-data receipts commit order) for M30-1; does not govern fleet or sibling preregistrations.
- C2 K2 live failure command (at HEAD):
  `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts`
  Output: `FAIL ... check1-no-gate` (twice), `entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2`, exit code 1.
- Snapshot quote verification: `census/round-26/sources/git-fetch.1.txt:3197` contains raw-contiguous text `This is enabled by default.`; `census/round-26/sources/git-builtin-fetch.c:2926` contains `run_auto_maintenance(the_repository, verbosity < 0);`.

## Findings

### 1. Surface (a): C2's F1 Trigger-Set Ground (git auto-maintenance, worktree prune, grace periods)
- **tsukuroi-shokunin**: Verdict = `routed` / `report`. References to "maintenance" govern systemd unit states (`state in {offline, maintenance}`) and pacman/ArchWiki system maintenance. "Prune" governs package cache pruning (`/var/cache/pacman/pkg`, `paccache`). Zero git maintenance ground. Host repair routed to tsukuroi.
- **kama-shokunin**: Verdict = `routed`. References to "graceful" govern llama-server SIGTERM teardown; "prune" governs stripping undeclared OpenAI keys from chat payloads. Zero git maintenance ground. Serving issues routed to kama.
- **kumitate-shokunin**: Verdict = `routed`. Kumitate owns live task worktree allocation and locking during dispatch per PROVINCE Adjacency: "kumitate-shokunin locks live task worktrees during dispatch; souji prunes only dead, unlocked registrations and never removes a lock it did not set". Kumitate's `corpus/knowledge/agent-isolation-substrates.md:14-17, 195` explicitly routes git auto-maintenance and linked-worktree pruning to souji.
- **kagi-shokunin**: Verdict = `routed`. Souji refuses secrets; routes credential-bearing history to kagi.
- **mori-shokunin**: Verdict = `routed` / `report`. Mori monitors earlyoom maintenance state and process timeouts; souji lists own-uid process residue without reaping and routes liveness/resource findings to mori.
- **kotodama-shokunin**: Verdict = `report`. Souji previously observed kotodama's unpushed `.scratch/` bloat (40.4 GB), correctly classifying it `NOT-SAFE` and reporting rather than deleting.
- **game-dev-2d-shokunin**: Verdict = `report`. Souji pruned 2 detached registrations in r3 and pinned 3 locked ones; game-dev-2d sentinels explicitly dry-run `git worktree prune` to safeguard custody of unpushed run receipts.
- **lore-shokunin**: Verdict = `report`. Souji pruned 19 dead worktree registrations in r3 with pushed receipts.
- **Remaining lanes** (`chousa`, `kasegi`, `kengaku`, `kake`, `kotoba`, `mado`, `revenger`, `tabi`, `tameshi`, `audio`, `game-dev-3d`): Verdict = `routed`. None holds git maintenance, worktree prune, or git gc grace period ground.
- **Absorb outcome**: Souji absorbs the F1 auto-maintenance trigger set from `/home/vgpnk/Projects/shokuknow/merge/souji/` into its own F1 frontier without colliding with any sibling lane.

### 2. Surface (b): C3's Prereg-Gate Surface (preregistration / claim-gating)
- **protocol / aggregator**: Verdict = `routed`. Protocol/aggregator owns fleet-wide protocol standards for preregistration/replay gates (referenced in `kengaku-shokunin/PROVINCE.md:139`).
- **kaidoku-shokunin**: Verdict = `routed`. Kaidoku built `axis-fit-gate.py` (M30-1) to check surface and unmoved_command on `coverage`/`depth` claims, and `freeze-integrity.py` for its own `.ufo/waves/round-<N>/claims.json`. Kaidoku does NOT own fleet preregistration or claim-gating for other lanes.
- **kasegi-shokunin**: Verdict = `routed`. Kasegi owns vulnerability/bounty report claim gates (`claim-gates.md`), not UFO wave claim preregistration.
- **souji-shokunin**: `tools/souji-axis-check.py` is lane-local, checking souji's own `.ufo/waves/round-26/preregistration.txt` format (`surface-class`, `enumerate:`, and lowest-axis rule against `SCORECARD.md`).
- Verdict across all siblings = `routed`. No sibling owns or contests souji's prereg-gate surface.

### 3. Surface (c): SCORECARD-Surgery Surface
- Every lane maintains its own internal self-assessment `SCORECARD.md`.
- Fleet root `SCORECARD.md` is owned by protocol / aggregator / operator.
- Souji's C1 claim operates strictly on `souji-shokunin/SCORECARD.md` to remove unintegrated scaffold fences and enforce newest-first ordering.
- Verdict across all siblings = `routed`. Zero cross-lane overlap.

### 4. Per-Lane Overlap Matrix (Rostered Lanes)
| Lane | Surface (a) F1 Auto-Maintenance | Surface (b) Prereg-Gate | Surface (c) SCORECARD Surgery | Primary Action / Routing |
|---|---|---|---|---|
| protocol | routed | routed | routed | Fleet protocol standards |
| aggregator | routed | routed | routed | Cross-lane quality reviews |
| kumitate | routed | routed | routed | Live worktree locking during dispatch; delegates git maintenance to souji |
| tsukuroi | routed / report | routed | routed | Host systemd services, pacman cache prune |
| kama | routed | routed | routed | Llama-server teardown, chat body key pruning |
| kaidoku | routed | routed | routed | Shipped artifact REA; lane-local M30-1 axis-fit-gate |
| kagi | routed | routed | routed | Secret/credential hygiene; souji refuses secrets |
| mori | routed / report | routed | routed | Fleet/host liveness, earlyoom monitoring; souji reports proc residue |
| chousa | routed | routed | routed | Deep research method and source hierarchy |
| kasegi | routed | routed | routed | Bounty mission state, vulnerability claim gates |
| kengaku | routed | routed | routed | LLM evaluation, benchmark horizon maintenance |
| kake | routed | routed | routed | Web properties, Projects dead slot prune |
| kotoba | routed | routed | routed | Prompt/skill craft verifiers |
| kotodama | report | routed | routed | Unpushed scratch bloat reported, not deleted |
| lore | report | routed | routed | Dead worktree registrations pruned with receipt |
| mado | routed | routed | routed | Desktop compositor and window management |
| revenger | routed | routed | routed | RE evidence-ledger discipline |
| tabi | routed | routed | routed | Browser and web-interaction craft |
| tameshi | routed | routed | routed | Verification fixtures, bwrap envelopes |
| audio | routed | routed | routed | Audio pipeline craft |
| game-dev-2d | report | routed | routed | Worktree custody monitored against prune |
| game-dev-3d | routed | routed | routed | 3D game dev pipelines |

---

## Connector Synthesis & Non-Obvious Move

### Evidence
1. `python3 -B tools/souji-gate-check.py ...` fails at HEAD with exit code 1 (`check1-no-gate`), because `gate_section()` requires `\n## Gate` inside each target entry, but both admitted entries placed the Gate rationale solely in `corpus/lessons/round-26.md`.
2. `tools/souji-gate-check.py:110-118` (check4) verifies quote spans against `squash(snapshot)` without stripping HTML tags. The git-fetch snapshot `census/round-26/sources/git-fetch.1.txt` is raw HTML.
3. Kumitate's `corpus/knowledge/agent-isolation-substrates.md:14-17` explicitly acknowledges souji's ownership of `git-auto-maintenance-prunes-worktrees.md`, confirming that F1 trigger-set knowledge is souji's canonical domain.

### Affected Axes
- **Coverage (8)**: Primary improvement. Unblocks C2 from failing its frozen K2 kill rule (`ok=2 fail=0`, exit 0), enabling the admission of the two F1 knowledge entries and 5 net new registry rows (S128–S132).
- **Calibration (7)**: Reconciles the disconnect between the gate verification instrument and the knowledge entries, eliminating phantom test failures and ungrounded receipts.
- **Operability (8)**: Harm = 0. Preserves all frozen commands, counters, and kill rules without requiring any predicate relaxation or tool modification.

### Proposed Move: "In-Entry Gate Header Contract with Raw-Contiguous Snapshot Anchoring"
Synthesizing the sibling boundary separation (kumitate ceding git maintenance to souji) with C2's gate-check failure:
1. Append an exact, compliant 5-line `## Gate` block to `corpus/knowledge/git-auto-maintenance-trigger-set.md` citing:
   - S128 URL (`https://git-scm.com/docs/git-fetch`), date `2026-10-25`, and the raw-contiguous snapshot quote `This is enabled by default.` from HTML line 3197 (which passes check4 without HTML tag stripping).
   - S129 URL (`https://github.com/git/git/blob/v2.56.0/builtin/fetch.c`), date `2026-10-25`, and quote `run_auto_maintenance(the_repository, verbosity < 0);` from line 2926.
2. Append a matching `## Gate` block to `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` citing:
   - S131 own-work fixture path, date `2026-10-25`, and quote `PASS requires before==2 exactly AND after==expect; anything else is FAIL.` (line 29).
   - S132 own-work census path, date `2026-10-25`, and quote `today: 0 prunable, 0 locked, 5 registrations` (lines 28-29).
3. Keep the broad curation narrative, search log, and S119–S121 language-edition refusal rationale in `corpus/lessons/round-26.md`.

### Risks
- If the quote in the entry's `## Gate` differs from the committed snapshot bytes, check4 fails. Mitigated by using the raw-contiguous span from line 3197 (`This is enabled by default.`) rather than the multi-line rendered sentence that contains HTML tags.
- The move requires no changes to predicates, targets, or case sets, adhering strictly to the pre-data amendment rules.

### Verification
Run the frozen K2 command:
```bash
python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
  --entries corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
  --snapshot-dir census/round-26/sources \
  --slice census/round-26/records/empty-slice \
  --slice-verdicts census/round-26/records/empty-verdicts
```
Expected output: `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`, exit code 0.

## Attack Log
No attack on frozen predicates or case sets. The connector proposal identifies a structural verification disconnect (missing `## Gate` in admitted entries causing K2 exit 1) and provides a fully compatible, non-relaxing synthesis that unblocks C2 coverage while maintaining complete boundary isolation across all sibling lanes.
