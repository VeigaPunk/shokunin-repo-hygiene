# FrontierLimits — round 15 (souji), seat SoujiR15.FrontierLimits

Axes: **operability** (C1), **calibration** (C2). Mode: source inspection only; design review of current bytes against the round-15 contract. No tests, probes, builds, installs, edits outside this file, or access to credential/auth files, `~/.omp/agent`, or `census/operator-sweep-20261019/`.

Measured identity (read-only hash/rev-parse at this seat):

| file | sha256 / revision |
|---|---|
| tools/souji-census.sh | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` (round-14 changed tool, last touched `552cae4`) |
| tools/souji-repo-structure.sh | `80025137b20d5a6143db0120057552bd239fb60de1a504ede69896baade5aec2` |
| tests/fixtures/r14-census-boundary.py | `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2` |
| HEAD / round-15 baseline | `cc2168325768d5356a82c039dcdf787377c55784` (matches `census/round-15/claims.json` baseline) |

**Status of the C1 repair:** not present. The current `guard_git_config` is still the round-14 key-presence predicate (see below). The round-15 repair is therefore **design-only at this seat**: the findings below describe the current bytes and the acceptance the repair needs.

## Verdict summary

| axis | verdict (source-verified) | basis |
|---|---|---|
| operability | **Harm stands, unrepaired.** Benign local config is refused by key name, regardless of value, and one refusal aborts the whole census. | `tools/souji-census.sh:493-507`, `160-164`, `979-991`; spot-check `corpus/lessons/round-14-verifier-spotcheck.md:104-106,148,160` |
| calibration | **Gap is structural.** The admitted C2 evidence has 12 namespace cases and zero benign-config controls; SCORECARD still reports operability 8 "improved". | `tests/fixtures/r14-census-boundary.py:45-57,629-641`; `SCORECARD.md:15`; spot-check `:117,148` |

## Evidence (exact lines)

**Value-blind predicate.** `guard_git_config`:
- `:500` `git config --file "$cfg" --no-includes --name-only --list` reads key *names only*.
- `:503` lowercases the whole newline-joined list.
- `:504-506` refuses on a substring match, with no value parsing: `*include.*|*includeif.*|*filter.*.clean*|*filter.*.smudge*|*filter.*.process*|*core.hookspath*|*core.attributesfile*|*core.excludesfile*|*core.alternaterefscommand*|*remote.*.promisor*|*extensions.partialclone*|*extensions.worktreeconfig*`.
- Consequence [INFERENCE from source; not executed]: `core.hooksPath=/dev/null`, `extensions.worktreeConfig=false`, and `remote.<name>.promisor=false` are all refused, though each is benign.
- Substring artifact [INFERENCE from bash `case` semantics]: `*include.*` also matches a remote named `include` (`remote.include.url`). The `*` wildcards also span the newline-joined key list, so they can match across key boundaries.

**Fleet-wide abort.** `protected_fail` (`:160-164`) exits 2. `list_repos` calls `guard_git_surface` for every immediate repo (`:963-965`), and `emit_census` runs `list_repos` (`:979`) before printing the header (`:991`). One refused repo therefore yields exit 2 and no TSV, including for unaffected peers.

**Neutralization already present.** `count_dirty` (`:710-712`) runs `status` with `core.fsmonitor=false`, `core.hooksPath=/dev/null`, `core.excludesFile=/dev/null`, `core.attributesFile=/dev/null`. Linked worktrees use the same function (`worktree_extra_flags` `:831-832`). The only other git calls are `worktree list`, `for-each-ref`, `rev-list`, `rev-parse` (`:688, 694, 698, 702, 836, 859`), none of which read hooks, excludes, or attributes. Per-repo `--no-includes` is used only for the config read (`:500, 511`); the `status` calls *do* follow `include.*`, which is why includes must stay refused.

**Protection not present in the namespace tests.** The selftest has no config-refusal assertion (grep of the 1539-line tool). The 12 fixture cases `R14C2-01..12` (`r14-census-boundary.py:45-57,629-641`) cover roots (01–03), alias (04), compare (05), gitfile (06), normal fleet (07), scratch (08), `GIT_DIR` env (09), linked-worktree owner (10), alternates (11), symlink fleet (12). No case writes a local config key other than the `GIT_CONFIG_*` env scrub (lines 66-69, 143-146, 369-372, 606-609).

**Scorecard inconsistency.** `SCORECARD.md:15` reports operability 8 "improved r14 C2 within tested boundary"; the outside closure reports `operability | harmed` (`round-14-verifier-spotcheck.md:148`). This is a bookkeeping defect under QUALITY Q10 and must be reconciled by the integrator, not silently fixed here.

## Separation: config-support repair vs credential handling

Keep **byte-identical** in the repair (credential/namespace boundary, Q21):
- `protected_fail`, `protected_reason_input`, `guard_path`, `guard_target` (`:160-164`, `:422+`).
- `guard_git_files` nlink/nonregular checks (`:475-491`), `guard_git_links` (`:456-471`), `guard_alternates*` (`:426-454`), `guard_worktree_registrations` (`:555-601`), `gitfile_admin`, `guard_git_surface` routing (`:603-672`).
- The `~`-prefixed `core.worktree` refusal (`:514`) and the `core.worktree` boundary check (`:511-521`). This is path resolution, not support policy.
- GIT_* scrub and `GIT_CONFIG_GLOBAL/SYSTEM=/dev/null` (`:119-123`).
- Fixture cases `R14C2-01..06, 09..11` and their expected IDs.

**Config-support repair zone** (the only region the round-15 C1 change should modify): `guard_git_config` `:493-522`, the protected-boundary header prose `:84-91`, and the matching prose in SKILL.md `:182-218` and PROVINCE.md `:82-93`.

Note the boundary and the support policy are distinct: a `core.hooksPath` pointing into the credential namespace must still fail `path-protected` after repair. Repair should turn key-presence refusal into **value-checked boundary checks**, not drop the boundary check.

## Frontier moves (ranked; each checked for harm to other axes)

**M1 — entry-level, value-aware classification (operability, primary).** Replace the joined-string substring test with per-entry parsing (`git config --file "$cfg" --no-includes --null --list`), matching section and key exactly. Then:

| class | keys | repair action | why |
|---|---|---|---|
| keep refused | `include.*`, `includeif.*` | unchanged (refuse) | status follows includes; included file is unvetted config reachable through `~` expansion (git-config docs, `include.path`) |
| keep refused | `filter.*.clean/smudge/process`, `core.alternaterefscommand` | unchanged (refuse) | command execution via status/refs, not path access; scope change needs operator adjudication |
| keep refused (value-true) | `extensions.partialclone` | unchanged | F2/partial-clone boundary; separate probe owns it |
| refuse only if canonical bool true | `extensions.worktreeconfig`, `remote.*.promisor` | value-aware | git-config `--type=bool` canonicalizes to lowercase true/false (docs `:1310-1312`); `false` is not a refusal condition |
| boundary-check value, not refuse | `core.hookspath`, `core.excludesfile`, `core.attributesfile` | `guard_target` on the value (like `core.worktree`); keep the `-c` overrides in `count_dirty` | already neutralized for every status call; read-only plumbing runs no hooks [INFERENCE: standard git behaviour, to confirm in acceptance] |

Harm check: namespace fixture stays identical; `include.*` and `filter.*` still refuse, so no new read or execution path opens. A `core.hooksPath` into the protected store still fails `path-protected`. Net: operability up, boundary unchanged.

**M2 — remove substring artifacts (operability).** Section-exact matching fixes `remote.include.url` false refusal and cross-key glob matching. Harm check: `includeif.<cond>.path` must still refuse (section `includeif`, not substring).

**M3 — paired benign-config and mixed-fleet controls (calibration, required by M1).** New synthetic cases under `/var/tmp`, with the baseline run against the **current** tool bytes `fcff8b05…` (not the round-14 `a31642d` baseline, which predates the refusal):
- benign: `core.hooksPath=/dev/null`, `core.excludesFile=/dev/null`, `extensions.worktreeConfig=false`, `remote.origin.promisor=false`: baseline expected exit 2 `git-config-unsupported`; changed expected exit 0 with the repo row.
- mixed fleet: benign repo + normal peer (+ optionally a linked worktree): changed expects every row, exit 0.
- still-unsupported control: `include.path` or `filter.x.clean` in one repo with peers: changed expects exit 2, no TSV (documents the retained boundary; not a repair).
- boundary control: `core.hooksPath` pointing into the synthetic protected namespace: changed expects `path-protected` exit 2, and baseline must not silently pass it.

**M4 — checker requirements (calibration; implementation owned by the checker seats).** The admission checker must refuse:
- green-only evidence: each repair claim requires a committed baseline-red observation (exit code, finding ID, tool digest) and a changed-green observation on the same fixture.
- weakened evidence: `EXPECTED_IDS` and expected exit codes for `R14C2-01..12` pinned by digest; any removed or relaxed ID fails.
- missing namespace controls: the 12 existing cases plus the M3 cases must all be present.
- certification/deletion claims: checker output carries `certification: OFF` and no deletion authority (Q18).

**M5 — defer (not in round 15 without adjudication).** Converting whole-fleet abort into per-row "unsupported" skips would change exit semantics. Spot-check routed defect 1 requires operator/canonical scope-change adjudication for this; it is not a no-harm improvement and should not be bundled into C1.

## Acceptance the repair needs (exact)

1. `guard_git_config` contains no key-presence `case` for benign keys; diff confined to `:493-522` plus header prose.
2. Benign-config control: baseline `fcff8b05` exit 2 `git-config-unsupported`; changed exit 0 with the row. Recorded with exit code and digests.
3. Mixed-fleet control: changed exit 0 and every peer row present.
4. Namespace fixture `python3 tests/fixtures/r14-census-boundary.py --tool <changed>`: total 12, failed 0, exit 0, with `R14C2-01..12` IDs unchanged.
5. `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` remains 38/38 and `shellcheck -S warning tools/souji-census.sh` exits 0.
6. `tools/souji-repo-structure.sh` and `tests/fixtures/r13-repo-structure.sh` unchanged (F2).

## F2 / K5 / certification — unchanged check (source only)

- **F2**: `tools/souji-repo-structure.sh:197-233` still refuses partial/promisor repos (separate probe, sha above). SCORECARD `:44` and PROVINCE `:55-57` still say "F2 as a whole stays frontier". No round-15 repair touches this probe.
- **K5**: HELD. QUALITY Q4/Q16 and `corpus/lessons/round-13.md:33` still bind. No cross-device fixture exists or is proposed.
- **Certification**: OFF. SKILL.md `:12-16`, SCORECARD `:70-71, 95, 97-102` and `:82-95` state certification and deletion authority remain OFF. The round-15 checker may not change this.

## Remaining limitations (explicit)

1. Filter drivers, `alternateRefsCommand`, `include/includeIf`, partial clone, and `worktreeConfig=true` remain unsupported after repair; a present one still aborts the whole census (exit 2). The actual deployment incidence is unmeasured [INFERENCE only].
2. Namespace residuals unchanged: hardlinked object files, work-tree symlinks, bind/mount replacement, symlink-relocated stores, concurrent replacement. Not authenticated by the fence (SKILL.md `:209-213`; tool header `:95-99`).
3. Dirty counts use `status` with `excludesFile`/`attributesFile`/`hooksPath` neutralized. Ignored files may appear as untracked, over-counting `dirty`. That is the conservative direction for NOT-SAFE, but it is a real divergence from user-visible status.
4. All fixtures are synthetic. No real credential-store probe; no runtime evidence produced at this seat. Every behavioural claim above is source-derived or [INFERENCE] and needs a committed observation.
5. The round-14 harm for benign configs is source-established, not executed. The round-15 acceptance above must observe it, not infer it.
6. Git config semantics beyond the cited docs (`--null`, `--type=bool` on the installed git) are not verified on this host here; acceptance must confirm them.

## Process and tooling

- Read-only: `sha256sum`, `git rev-parse`, `git log -1` on the lane repo. No probe, test, build, or lint.
- External primary doc read: https://git-scm.com/docs/git-config (for `--type=bool` canonicalization `:1310-1312`, `include.path` `:1070-1072`, `config.worktree` `:745, 1154`).
- Tools installed/updated: **none**.
- Not opened: `~/.omp/agent/**`, any auth/credential file, `census/operator-sweep-20261019/`, sibling repos.

## Routing

Material findings (value-blind predicate; fleet-wide abort; SCORECARD operability 8 vs outside "harmed"; absent benign-config control) are sent to `SoujiR15` by id. Implementation and checker ownership sit with the ConfigRepair, ConfigFixture, and AdmissionChecker seats. This seat does not own edits.

## Boundary disclosure (no-query rule)

Authoritative reminder received via IRC from SoujiR15: query only explicit known source/tool/test/round-15 paths; never whole-lane or recursive census queries; no runtime probes.

Violation disclosed: my first call was `_glob` over the whole lane root (`/home/vgpnk/Projects/shokunin/souji-shokunin`, `gitignore: false`, `hidden: true`, `limit: 200`). It recursed and its output listed filenames under `census/operator-sweep-20261019/` (for example `stage-hold-delete.sh`, `kotodama-children-sizes.tsv`, `.hold.json`, `tmp-removed.tsv`). Only names were returned. I did not open, read, copy, hash, or modify any operator-sweep content, and I did not use those names for any finding. The same output also listed `census/round-*` and `results/` names, which are not part of this seat's evidence.

Other read-only calls were explicit: named source files, `.ufo/waves/round-15` paths, `corpus/` lessons and quality files, `tests/fixtures/r14-census-boundary.py`, `tools/` file names via explicit path, and `sha256sum` on three named files plus `git rev-parse`/`git log -1` on the lane repo. `sha256sum` and `git` are read-only fact checks, not behavioural probes, and no test or tool was executed.

Consequence for this report: the census-directory names seen in that glob are not evidence and are not cited. The conclusions rest on the explicit source and fixture reads listed above. No subsequent glob or search touched the operator sweep, and I did not repeat the whole-root glob.
