# Overlap — Sibling-Boundary & Province Overlap Scan (Round 13, Wave 1)

**Seat**: `SoujiR13.Overlap` (Connector, Leaf)  
**Lane Root**: `/home/vgpnk/Projects/shokunin/souji-shokunin`  
**Fleet Root**: `/home/vgpnk/Projects/shokunin`  
**Target Path**: `.ufo/waves/round-13/w1/Overlap.md` (`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-13/w1/Overlap.md`)  
**Baseline HEAD**: `31984f473ce4bdab61a99b16cca194b28108cb81`  
**Posture**: Godspeed subagent (`calibration`, `operability`, `coverage`). Leaf member — no subagent dispatch; read-only inspection; no commits; zero scans of operator sweep contents.

---

## 1. Axes & Posture

- **Calibration**: Empirically verify boundary definitions against live sibling `PROVINCE.md` declarations, current `SKILL.md` boundaries, and the fleet `MANIFEST.json`; never infer uncontested scope without exhaustive path/symbol sweeps.
- **Operability**: Provide checkable commands, exact file paths, and verifiable hand-off interfaces that L1 and non-author verifiers can independently execute without oral context.
- **Coverage**: Exhaustively scan the three round-13 souji focus areas (Frontier F2 size-census, tool-certification evidence validator, and restorable quarantine bounds) across candidate sibling provinces (`kumitate`, `tsukuroi`, `kagi`).

---

## 2. Fleet MANIFEST Scan (Read-Only)

### 2.1 Manifest Structure & Roster Alignment
- **Path**: `/home/vgpnk/Projects/shokunin/MANIFEST.json`
- **Total Rounds Recorded**: 329 entries (`.rounds | length = 329`).
- **Fleet Roster**: 13 rostered lanes (`kasegi`, `kengaku`, `kake`, `kumitate`, `kotoba`, `kagi`, `kama`, `audio`, `game-dev-2d`, `game-dev-3d`, `lore`, `revenger`, `kaidoku`).
- **Souji Closure Entries**:
  - Exactly 1 closure entry: Round 12 (`entry 325`, `commit: souji-shokunin@31984f473`, `closed_at: 2026-10-19T22:37:14Z`, verdict `admitted`).
  - Capabilities added in r12: `sources-registry` (33 rows) and `r12-maintenance-guard` (git auto-maintenance worktree-prune guard).
  - Notes explicitly record: *"Work d7266c5 + de9187e, post-review 2a363a0, integrator spot-check. One L2's failed cd produced 4 stray fleet-root commits + strays — repaired by the integrator (reset --keep 31baf5c, quarantine). No push (standing rule)."*
- **Sibling Closures Scanned**:
  - `kumitate` (Round 34, `commit: kumitate-shokunin@a5683a96c`, closed `2026-10-19T23:49:24Z`, verdict `admitted`): Capabilities added: `sources-registry` over 20 opened rows. Confined strictly to orchestration, OMP task/hub, and runtime scripts.
  - `kagi` (Round 21, `closed_at: 2026-10-19T23:07:14Z`, verdict `rejected-honest-stop`): Evaluated secret scanning, SOPS/age, OpenBao/Vault lifecycle. Confined strictly to vault ops and credential custody.
  - `tsukuroi` (Round 12, `commit: tsukuroi-shokunin@9574a189a758251da5957eee8ff0f38ba2d03c7f`, closed `2026-10-20T04:12:43Z`, verdict `rejected-harmed`): Added capability `root-metadata-observer` for OS root DAC/ACL and unit inspection. Refused package removal, host mutation, or workspace deletions.

### 2.2 MANIFEST Search for Contested Ground
A bounded query across all 329 MANIFEST rounds for terms `quarantine`, `size-census`, `size census`, and `souji` confirms:
1. No sibling lane claims or registers tools for `souji` size census, repository object metrics (`git repo structure`), or workspace quarantine staging.
2. Historical quarantine references in MANIFEST pertain exclusively to orchestrator triage of broken runs (e.g. Round 2 in 2026-10-15 and Round 12 integrator repairs), never to a sibling lane's capability or active province.

---

## 3. Contested Scope Scan vs Relevant Provinces

### 3.1 Frontier F2: Repository Size Census (`git repo structure` / `count-objects`)
- **Souji Target**: Read-only probe `tools/souji-repo-structure.sh` executing `GIT_OPTIONAL_LOCKS=0 git -C <repo> -c maintenance.auto=false repo structure --format=lines`. Governed by `corpus/knowledge/git-repo-structure-readonly.md` (sourced S005/S006).
- **Scan vs `kumitate-shokunin`** (`kumitate-shokunin/PROVINCE.md:3-34`):
  - *Kumitate Owns*: Orchestration & tooling across OMP task/hub and `ufo-fsd-alpha` runtime scripts.
  - *Finding*: Kumitate inspects agent dispatch worktrees (`git worktree list/lock`), but does **not** measure git object store sizing, disk pack distribution, or inflated commit/blob metrics.
  - *Bleed Risk*: None. Souji measures static object structures without dispatching tasks, acquiring agent locks, or modifying runtime contracts.
- **Scan vs `tsukuroi-shokunin`** (`tsukuroi-shokunin/PROVINCE.md:3-48`):
  - *Tsukuroi Owns*: Host OS substrate, pacman package states, kernel/driver health, systemd units, root DAC, and snapper rollback nets.
  - *Finding*: Tsukuroi diagnoses disk storage via host filesystem metrics (`df`, snapper subvolumes), never git-level object-store metrics (`git repo structure`).
  - *Bleed Risk*: None. Tsukuroi measures host/subvolume disk consumption; Souji executes git-internal structure probes on workspace repositories and explicitly refuses host OS filesystems (`/var/lib/pacman`, system root).
- **Scan vs `kagi-shokunin`** (`kagi-shokunin/PROVINCE.md:3-38`):
  - *Kagi Owns*: Secrets, vault ops, credential hygiene, and shape-only secret scanning.
  - *Finding*: Kagi monitors secret presence and large files only in the context of credential leak prevention (S015/S012 `git-filter-repo` recommendations), refusing git history rewrites.
  - *Bleed Risk*: None. Souji measures topological counts and inflated bytes without inspecting blob content or resolving secret references.

### 3.2 Tool-Certification Evidence Validator (`tools/souji-cert-evidence.py`)
- **Souji Target**: Machine-checkable gate verifying receipt and certification fragment evidence consistency (author uniqueness, hash matching of installed tool bytes `tools/souji-*.sh`, evidence non-emptiness, deterministic exit codes `0/1/2`). Certification stays strictly OFF.
- **Scan vs `kumitate-shokunin`**:
  - *Kumitate Owns*: Gate registries for multi-agent execution (`claims-check.mjs`, `proxy-check.mjs`).
  - *Finding*: Kumitate gates check runner options and protocol equivalence for task runners. They do not validate souji removal receipts (`pushed`, `moved-to-obsidian`, `stale`) or installed hygiene tool fragments.
  - *Bleed Risk*: None. Souji's validator checks fragments strictly within `souji-shokunin/census/` and `tools/`.
- **Scan vs `tsukuroi-shokunin`**:
  - *Finding*: Tsukuroi verifies package signatures (`.pkg.tar.zst` discipline) and system unit integrity; it has zero overlap with repo tool certification.
  - *Bleed Risk*: None.
- **Scan vs `kagi-shokunin`**:
  - *Finding*: Kagi operates `corpus/claim-ledger.sh` and `corpus/checklist-run.sh` for vault operations. Kagi does not certify file hygiene tools.
  - *Bleed Risk*: None.

### 3.3 Quarantine Boundaries & Bounded Staging (`tools/souji-quarantine.sh`)
- **Souji Target**: Receipt-gated staging of unreferenced workspace debris into `.ufo-quarantine/` (or designated quarantine path). Enforces Q8: timeout bounds on per-target `mv`/`git mv` and `sha256sum`, rejection of FIFOs/devices/sockets, fail-closed handling on timeout.
- **Scan vs `kumitate-shokunin`**:
  - *Boundary*: Kumitate holds `git worktree lock` during live tasks. Souji only touches dead worktree metadata or stale scratch after verifying no locks exist (`git worktree list --porcelain`).
  - *Bleed Risk*: None. Souji never unlocks a worktree it did not lock, nor does it stage active execution directories.
- **Scan vs `tsukuroi-shokunin`**:
  - *Boundary*: Tsukuroi investigates system failures and reports remediation to the operator; Tsukuroi explicitly refuses deleting files or removing packages (`PROVINCE.md:24`: *"Never installs, upgrades, or removes packages; never restarts services"*).
  - *Bleed Risk*: None. Souji handles workspace repo artifact quarantine and never stages system files, packages, or host unit configurations.
- **Scan vs `kagi-shokunin`**:
  - *Boundary*: Kagi identifies credential-bearing files and routes them to the operator/kagi workflows. Souji explicitly refuses credential handling (`PROVINCE.md:29`: *"Credentials, secrets, tokens, vault refs — kagi-shokunin's province. Souji cites paths/modes only and never reads secret content"*).
  - *Bleed Risk*: None. Quarantine staging checks shape, rejects special files, and aborts if secret paths are contested.

---

## 4. Cross-Domain Adjacency Matrix

| Domain Boundary | `souji-shokunin` | Sibling Owner | Adjacency Contract & Why No Bleed |
|---|---|---|---|
| **Git Object & Size Census** | Owns read-only repo structure probe (`git repo structure --format=lines`, reachable objects/sizes). Does not grant deletion. | *None* (Uncontested) | No sibling measures git topological structure or object pack inflation. Sibling telemetry is limited to system disk runway (`mori`/`tsukuroi`) or worktree lists (`kumitate`). |
| **Worktree Lifecycle** | Prunes dead worktree registrations (`git worktree prune`) after checking receipt (pushed/empty) and unlocked status. | `kumitate-shokunin` (`PROVINCE.md:3-6`) | Kumitate locks active worktrees (`git worktree lock`) during task runs. Souji respects existing locks and never prunes locked trees. |
| **Host vs Workspace Hygiene** | Stages/removes unreferenced repo files under verified receipts (`.scratch/`, dead metadata). Never touches OS packages or root. | `tsukuroi-shokunin` (`PROVINCE.md:3-24`) | Tsukuroi repairs host OS substrate (`/var/lib/pacman`, systemd, boot), refusing file removal. Souji operates only on workspace paths under `$SHOKUNIN_ROOT` and refuses OS substrate. |
| **Credential & Secret Scrutiny** | Detects unreferenced debris; routes credential-bearing paths to kagi without reading secret content. | `kagi-shokunin` (`PROVINCE.md:3-6`) | Kagi owns credential hygiene, vault ops, and secret classification. Souji refuses credentials, tokens, and history rewrites (`git-filter-repo`). |
| **Observability vs Action** | Acts on workspace artifacts under receipt discipline; never terminates processes. | `mori-shokunin` (`PROVINCE.md:3-16`) | Mori observes host/fleet resource runway, memory pressure, and watchdog liveness. Souji acts only on disk artifacts, never on processes. |

---

## 5. Verification Checks for L1

1. **Absence Sweep Verification**:
   Verify zero sibling claims over souji's frontier terms (F1 git maintenance, F2 size census, F3 duplicate files, F4 restorable quarantine):
   ```bash
   grep -EIn "git[ -]maintenance|maintenance\.auto|expire-to|gc\.(pruneExpire|worktreePruneExpire)|git\s+repo\s+structure|rmlint|fclones|jdupes|fdupes|trash-cli|freedesktop.*trash" \
     /home/vgpnk/Projects/shokunin/*-shokunin/{PROVINCE.md,SKILL.md} 2>/dev/null \
     | grep -v "/souji-shokunin/" | wc -l
   ```
   *Expected*: `0`

2. **MANIFEST Integrity Check**:
   Ensure no sibling closure entry in `MANIFEST.json` registers `souji` capabilities:
   ```bash
   node -e '
     const fs = require("fs");
     const m = JSON.parse(fs.readFileSync("/home/vgpnk/Projects/shokunin/MANIFEST.json", "utf8"));
     const hits = m.rounds.filter(r => r.lane !== "souji" && JSON.stringify(r).match(/souji-(verify|quarantine|census|cert|repo)/));
     console.log("Contested sibling capability entries:", hits.length);
     process.exit(hits.length === 0 ? 0 : 1);
   '
   ```
   *Expected Exit*: `0`

3. **Province Scope Fence Verification**:
   Confirm that `souji-shokunin/PROVINCE.md` explicitly preserves the refusals for OS files, secrets, and history rewrites:
   ```bash
   grep -nE "Refuses|Git history rewrite|Credentials, secrets|Operator config" /home/vgpnk/Projects/shokunin/souji-shokunin/PROVINCE.md
   ```
   *Expected*: Resolves lines 26–32 with explicit refusals.

---

## 6. Limitations & Tooling Record

- **Tooling Directive Record**: No tools were installed or updated during this seat execution. All inspections utilized existing host tools (`git`, `node`, `grep`).
- **Read-Only Scope Boundedness**: Operator sweep paths (`census/operator-sweep-20261018/`, `census/operator-sweep-20261019/`) were strictly excluded from scanning.
- **Seat Independence**: This seat is an advisory leaf connector seat (`SoujiR13.Overlap`); this report does not constitute an independent non-author verification or promotion endorsement.
