# SiblingOverlap — Round 15 W1 Connector Report

**Seat:** `SoujiR15.SiblingOverlap` (connector, leaf)
**Lane:** `souji-shokunin` (`/home/vgpnk/Projects/shokunin/souji-shokunin`)
**Axes:** operability (primary, C1), calibration (C2 paired controls)
**Source state:** round-14 tool present (`tools/souji-census.sh` sha256 `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`, mtime 2026-10-20 04:56). No round-15 repair is landed. Every statement about a repair is **design-only**.

---

## 1. Tooling Directive & Execution Class

- **Installed or upgraded tools:** none.
- **Exercised evidence:** none. Source inspection only, per the leaf contract. No tests, builds, linters, selftests, probes, or census runs. No real `~/.omp/agent`, credential, or auth file was opened. `census/operator-sweep-20261019/` was not opened.
- **External source:** one web search excerpt of `https://git-scm.com/docs/git-config` (`--worktree` / `config.worktree`). The page itself was not opened in full. Cited as search-excerpt evidence only.

---

## 2. Named Axes and Boundary Verdict

| Axis | Role in this seat | Verdict |
|---|---|---|
| operability (C1) | Round-14 value-blind refusal of benign repo-local Git config | Repair is in-province. Concrete overreach found in the current tool (§3). |
| calibration (C2) | Paired preservation evidence for the repair | Needs red/green pairs with poisoned values and benign mixed fleets (§6). |
| coverage / depth / adjacency | Not scored by this seat | Unchanged; no province absorption found (§4). |

**Bottom line:** the config-refusal repair is a souji-internal, read-scope decision over Git metadata of lane repos. It is not credential hygiene, not orchestration, and not fleet observability. It is **not absorbed** by kagi, kumitate, or mori, provided the four guardrails in §5 hold.

---

## 3. Source Evidence: Value-Blind Refusal and Its Blast Radius

### 3.1 The predicate is key-name only
- `tools/souji-census.sh:500` — `git config --file "$cfg" --no-includes --name-only --list` (names only; values never read).
- `tools/souji-census.sh:505–506` — glob predicate over the lowercased key list. Refuses on key presence, with no value test:
  `*include.*|*includeif.*|*filter.*.clean*|*filter.*.smudge*|*filter.*.process*|*core.hookspath*|*core.attributesfile*|*core.excludesfile*|*core.alternaterefscommand*|*remote.*.promisor*|*extensions.partialclone*|*extensions.worktreeconfig*`
- `tools/souji-census.sh:511–515` — `core.worktree` is boundary-checked, not refused. Only a `~` value is refused.
- Call sites of `guard_git_config`: lines 581, 613, 628, 650, 665.

### 3.2 Neutralization already exists for some refused keys
- `tools/souji-census.sh:710–712` — the only `status` invocation (`count_dirty`) forces `-c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null`.
- Grep of the tool: no other `status` call. `rev-list`, `for-each-ref`, `worktree list`, `rev-parse`, `symbolic-ref` (lines 688–702, 836, 859) do not read excludes or attributes. Git does not run `core.hooksPath` hooks for read-only commands.
- The `add -A` at line 1157 is in the selftest fixture builder, not the census path.
- **Result:** `core.hookspath`, `core.attributesfile`, and `core.excludesfile` are refused for keys whose effect is already neutralized at every census read. This matches the round-14 verifier's stated case (`corpus/lessons/round-14-verifier-spotcheck.md:104`: a harmless `core.hooksPath=/dev/null` meets the refusal predicate).

### 3.3 Whole-census abort (mixed-fleet harm)
- `tools/souji-census.sh:931–964` — `list_repos` calls `guard_git_surface` per repo.
- `tools/souji-census.sh:973–991` — `emit_census` calls `list_repos` before the header is printed at line 991.
- `tools/souji-census.sh:160–164` — `protected_fail` exits 2.
- **Result:** one repo with a refused key aborts the whole census with no TSV, including unaffected peers. The round-14 verifier rejected this as operability harm (`corpus/lessons/round-14-verifier-spotcheck.md:104`, `:148`, `:160`).
- Current line numbers differ slightly from the verifier's citations (`emit_census` 973 versus 979). The mechanism is unchanged.

### 3.4 No benign-config control exists
- `tests/fixtures/r14-census-boundary.py`: positive controls `case_07` (`NORMAL`), `case_08` (`SCRATCH_REPO`), and `case_12` (`NORMAL2`) use `init_repo` only. No local config key is written into any positive repo. The only config written is the synthetic store `GD/config` at lines 221–223, which is not a repo.
- **Result:** the round-14 C2 "12/12" claim has zero benign-local-config preservation evidence (`corpus/lessons/round-14-verifier-spotcheck.md:104` says the same).

### 3.5 Worktree config is not guarded (critical precondition)
- The guard reads only `$dir/config` (line 495, `cfg="$dir/config"`).
- `grep -n config.worktree tools/souji-census.sh` returns no code hits (only the header comment at line 88 and the key-list at 505).
- git-config docs (search excerpt, `https://git-scm.com/docs/git-config`, `--worktree`): with `extensions.worktreeConfig` enabled, Git reads `$GIT_DIR/config.worktree`. For the main worktree that is `$GIT_COMMON_DIR/config.worktree`.
- **Result:** today the `extensions.worktreeconfig` refusal is the only thing preventing an unguarded `config.worktree` read. Relaxing that refusal for `true` without a `config.worktree` guard would open a new unchecked config surface that can carry `include.path` or `filter.*`.
- [INFERENCE, not exercised] With `extensions.worktreeConfig=false`, Git ignores `config.worktree`. A `false`/absent value is therefore inert and safe to admit.

### 3.6 Includes are read by every Git command
- The `-c` overrides in `count_dirty` do not neutralize `include.path` / `includeIf`. Read-only commands (`worktree list`, `for-each-ref`, `rev-list`) also process includes from repo config.
- [INFERENCE from git-config semantics; not exercised] This is why `include.*` must stay refused, or be value-checked (§6 option B).

---

## 4. Province Boundary Check (no absorption)

### 4.1 Kagi-shokunin — config refusal is not credential hygiene
- Kagi's PROVINCE owns credential custody, 1Password, the-janitor, and credential-hygiene evidence. It refuses anything outside that domain.
- Souji's PROVINCE `## Refuses`: "Credentials, secrets, tokens, vault refs — kagi-shokunin's province. Souji cites paths/modes only and never reads secret content."
- The `~/.omp/agent` fence (round-14 C2) is a path-refusal before any read. It is not a content scan, and it does not classify credentials.
- **Absorption risk:** a value-aware repair would start reading config values. Keys such as `remote.*.url` (embedded credentials), `http.*.extraheader` (bearer tokens), `credential.*`, and `url.*.insteadOf` carry secret-shaped material. Reading or emitting them would be credential hygiene, which is kagi's domain.
- **Verdict:** no absorption, provided the repair reads only an enumerated set of semantic keys (booleans, plus the path-resolution checks already present), never emits values, and never runs secret-shape detection. Any secret-shaped value encountered is routed to kagi, not reported as a souji finding.

### 4.2 Kumitate-shokunin — worktree locks are orchestration, not config
- Souji PROVINCE `## Adjacent`: "kumitate-shokunin locks live task worktrees during dispatch; souji prunes only dead, unlocked registrations and never removes a lock it did not set."
- Kumitate's PROVINCE owns dispatch and worktree allocation/locks. Souji's worktree handling is read-only (`worktree list`, registration guard at lines 831–836 and 844–847).
- **Absorption risk:** admitting `extensions.worktreeConfig=true` changes what Git reads for linked worktrees. A repair that also starts inferring lock state, or that prunes or removes registrations, would take over kumitate's lifecycle authority.
- **Verdict:** no absorption, provided the repair adds no `git worktree prune`/`remove`, no lock inference, and no change to the registration guard.

### 4.3 Mori-shokunin — observability only
- Mori reads `.ufo/waves/*` settlement, watchdog liveness, journal/OOM classes, and disk/cgroup runway. It refuses dispatch (→ kumitate), OS state (→ tsukuroi), and credentials (→ kagi). It never remediates.
- Souji PROVINCE adjacency: "mori-shokunin observes fleet health and reports; souji acts on artifacts and never on processes."
- **Verdict:** no overlap. The config repair is a census read-scope change, not a process or host-state change. No mori surface depends on the census verdict.

### 4.4 Operator config — the trap in "preserve benign configurations"
- Souji PROVINCE `## Refuses`: operator config (`~/.config/**`, driver `scripts/`, `.ufo/state/`, `.ufo/watchdog.log`).
- `tools/souji-census.sh:121–123` disables global and system Git config (`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`).
- **Absorption risk:** "preserve benign configurations" could be misread as re-enabling the operator's `~/.gitconfig` or `includeIf` chain. That would read operator config, which souji refuses.
- **Verdict:** the repair must keep global and system config disabled. Benign means repo-local, not operator-global.

---

## 5. Guardrails the Repair Must Keep

1. **No value reads beyond the whitelist.** Values are read only for: `extensions.worktreeconfig`, `remote.*.promisor`, and `core.worktree` (existing path check). Use `--type=bool` where applicable. Never emit values. Non-boolean or unparsable → fail closed (refuse).
2. **No secret-shape detection** in the census. Routed to kagi.
3. **No orchestration authority.** No prune, remove, lock inference, or registration change.
4. **Global and system git config stay disabled.**

---

## 6. Proposed Move (one bounded proposal)

Replace the key-presence predicate in `guard_git_config` (`tools/souji-census.sh:505–506`) with **three effect tiers**. Admit only what the tool already neutralizes or can boundary-check, and keep every effect-bearing refusal.

| Tier | Keys | Repair | Justification |
|---|---|---|---|
| **A — effect-neutralized (admit)** | `core.hookspath`, `core.excludesfile`, `core.attributesfile` | Drop from refusal, conditional on the invariant that every `status` call keeps its `-c` override (`count_dirty` 710–712). Add a guard that fails selftest if a `status` call lacks the override. | No read-only census command runs hooks. Only `status` reads excludes/attributes, and it is overridden. |
| **B — value-aware (admit false/absent only)** | `extensions.worktreeconfig`, `remote.*.promisor` | Refuse only when the effective boolean is `true`, or the value is non-boolean. `extensions.partialclone` presence stays refused. | `false` is inert [INFERENCE]. `promisor=true` can lazily fetch from a remote, so it stays refused. |
| **C — keep refused (effect-bearing)** | `include.*`, `includeif.*`, `filter.*.clean|smudge|process`, `core.alternaterefscommand`, `core.worktree` with `~` | Unchanged. | Read on every command (include), or executes a command (filter, alternateRefsCommand). Value-checking include is a separate scope decision (option B below). |

**Precondition for any future `worktreeConfig=true` admission:** boundary-guard `config.worktree` in both `$admin` and `$GIT_COMMON_DIR` with the same predicates. Not part of this repair. Until then `true` stays refused.

**Option B (not proposed here, requires operator/canonical scope decision):** admit `include.path` only when relative, `~`-free, and boundary-resolves inside the repo. Refuse `includeIf`, and refuse nested includes.

**Mixed-fleet behavior:** keep `exit 2` for the genuinely refused keys (C tier). Do not change the output contract. The round-14 verifier's requirement that "a harmless local setting cannot suppress unaffected rows" is met by Tier A/B. A genuinely unsupported repo still aborts the census, and that remains an operator scope decision.

---

## 7. Affected Axes

| Axis | Effect of proposed move | Mechanism |
|---|---|---|
| operability (C1) | **Improved** | Benign `core.hooksPath` / `excludesFile` / `attributesFile` / `worktreeConfig=false` / `promisor=false` repos produce rows. Mixed fleets keep their unaffected rows. |
| calibration (C2) | **Improved, if** paired controls land (§8) | Red/green pairs prove the poisoned-value case is still safe. |
| namespace protection | **Harm-free** | Tier C and the path fence (`path-protected`) are unchanged. Tier A is safe only because `status` overrides the keys. |
| credential hygiene (kagi) | **Harm-free** | Whitelist-only value reads; no secret-shape detection. |
| orchestration (kumitate) | **Harm-free** | No lock or prune change. |

---

## 8. Calibration Acceptance (for the C2 checker and L1)

Design-only. Nothing below was run.

Required paired cases, all with synthetic canary values only (no real credentials):

- **Red/green poisoned value (Tier A):** `core.excludesFile=<store>/auth.json` and `core.hooksPath=<store>/hooks`. Baseline must refuse with exit 2. Changed tool must succeed (rows emitted) with zero store access (strace/EACCES, mode-000 store), and no store canary in output.
- **Red/green (Tier B):** `extensions.worktreeConfig=false` → rows; `=true` → refused. `remote.origin.promisor=false` → rows; `=true` → refused.
- **Mixed fleet:** a benign-config repo and a plain repo under one root. Both must produce rows.
- **Namespace controls unchanged:** all 12 existing `R14C2-*` cases must still pass.
- **Negative controls:** `include.path` into store, `filter.x.clean`, `alternateRefsCommand`, `config.worktree` present with `worktreeConfig=true` → refused, exit 2.
- **Global-config isolation:** a synthetic `$HOME/.gitconfig` with `includeIf` pointing into the store must not be read (exit and no store access unchanged).

Limit wording for the checker: "benign-local-config preservation, tested cases only." Not universal preservation.

---

## 9. Risks & Contradictions

- **R1 — Tier A premise:** "`status` is the only excludes/attributes reader" rests on grep of the current tool. It holds only while that invariant holds. The guard test in §6 is needed to keep it true.
- **R2 — `worktreeConfig=true` remains refused** under this proposal. If the operator needs linked-worktree configs preserved, the `config.worktree` guard (§6 precondition) becomes mandatory work.
- **R3 — include refusal stays.** A repo with a relative `include.path` remains refused. That is a real operability gap, not solved here.
- **R4 — Git doc semantics** (`extensions.worktreeConfig=false` inert; includes processed by read-only commands) are [INFERENCE]. They were not exercised. The C2 checker must observe them, not assume them.
- **R5 — Whole-census abort** for genuinely refused keys is unchanged. Changing it to per-row refusal alters the output contract. That is an operator decision, not a repair.

---

## 10. Verification Main Agent Should Run (not run by this seat)

```
shellcheck -S warning tools/souji-census.sh
TMPDIR=/var/tmp bash tools/souji-census.sh --selftest
python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh   # must stay 12/12 plus new paired cases
```

Plus the new paired-control fixture from §8, run once after all seats finish. Confirm both baseline (exit 2 on benign) and changed tool (rows) on identical input.

---

## 11. Routed to SoujiR15

Material findings sent by message (§3.5 worktree-config guard gap, §6 three-tier move, §4.4 global-config trap, §8 paired-control design). This seat proposes one move and stops.

## 12. Query-Boundary Disclosure

- **Violation (one call):** an early `_glob` over the whole lane root (`/home/vgpnk/Projects/shokunin/souji-shokunin`, limit 200, recursive) returned filenames under `census/operator-sweep-20261019/` and `census/operator-sweep-20261018/`. Names only; no bytes were read, and nothing was opened, copied, edited, moved, staged or deleted.
- **Also listed without recursion:** one `ls -la` covered `census/` at top level. It showed the operator-sweep directory entries, not their contents.
- **Not repeated:** after the SoujiR15 reminder, no further glob or search touched the lane root or any census tree. All later reads used explicit source, round-14 and round-15 paths.
- **Limitation:** findings in §3–§8 do not rely on any operator-sweep content. The directory names observed are not used as evidence.
