# S67ConnectorOverlap — sibling overlap (read-only)

Scope: the 19 sibling lanes under `/home/vgpnk/Projects/shokunin/*-shokunin/` (souji excluded). Read-only.
Method: `git -C <repo> grep -n -I` over tracked files (any path, then code-only with `.md`, `.ufo/`, `evidence/`,
`knowledge/` and `SOURCES*` excluded), plus the grep tool over working trees. Terms: `GIT_COMMON_DIR`,
`core.fileMode`, `RECEIPT-ENV`, `--chronology` / `freeze-check --chronology`. Nothing was edited, committed or fetched.

## 1. `GIT_COMMON_DIR` — tracked code hits (repo, path:line)

Each entry is a **name-based scrub or a list**; none of them value-checks the variable (the souji C1 design).

| repo | path:line | what it does | owns / needs the route? |
|---|---|---|---|
| kumitate | scripts/receipt-bind.mjs:101-104 | `GIT_ENV_DROP` array, comment "a receipt is bound at a revision, so no inherited GIT_* override may redirect the read"; drops GIT_COMMON_DIR unconditionally | Own receipt tooling. Scrub-only, no value check; no honest-equal-value row. Closest analogue to souji's writer. |
| kumitate | scripts/cite-check.mjs:1851; control-replay.mjs:46; proxy-check.mjs:1622; round-gate.mjs:711; routed-ledger.mjs:64; jj-seat-demo.sh:44 | scrub / poison / unset lists | Own gates. Scrub-only. |
| kake | scripts/citing_set.py:166-170 | `GIT_LOCAL_ENV` tuple (includes GIT_COMMON_DIR, GIT_CONFIG*), filtered into `GIT_SUBPROCESS_ENV` | Own gate. History: `.ufo/waves/round-28/residual/CriticC1FollowUp.md:45-47` found an inherited GIT_DIR false clean; the fix was a scrub. |
| kotoba | verifiers/check_r86_routed_repairs_v3.py:148-149 | scrub list in `_git` | Own verifier. Scrub-only. |
| kotodama | reports/round-51/calibration/ruler.py:114-116; tools/check-claim-separability.py:115-116 | env pop list / names list | Own calibration tooling. Scrub-only. |
| kaidoku | tools/round-25/instrument-custody.py:98-100 | doc comment: all GIT_* dropped | Own tooling; prefix policy. |
| mado | quality/q36-successor-run.sh:19 | `unset ... GIT_COMMON_DIR` | Own quality script. |
| mori | .scratch/MutGateFirstParent/gate-v3-{mutant-preserved,mutant,pristine}.py:108,428/434; .scratch/MutGateReadd/gate-v3-readd-mutant.py:108,429 | `_clean_env` pop list in tracked scratch copies | Not a route owner; scratch files tracked in mori (hygiene note for mori's owner only). Display of 8 hits was capped; more may exist. |
| tameshi | tools/design-blob-audit.py:603-618 | ARM17 canary: poisons GIT_DIR/GIT_WORK_TREE/…/GIT_COMMON_DIR, asserts HEAD, refs and status unchanged | Own audit. A kill-test pattern (poison + invariant), not a route owner. Reusable idea for souji W-rows. |
| tsukuroi | tools/check-adjacency-table-r51.py:188-192 | `REDIRECT_ENV` table naming GIT_COMMON_DIR, plus `SIBLING_NAMES` (kama, kagi, mado, mori, kumitate, kaidoku, revenger, tameshi) | Cross-lane checker. Lists the same redirect class. |
| kama | tools/report-landing-audit.py:148-149 | prefix scrub: drops every `GIT_*`, pins GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM; selftest `inherited-GIT_DIR-untouched` at :1601-1606 | Own audit. Prefix policy, so GIT_COMMON_DIR is covered by name-free rule. History: `.ufo/waves/round-21/build/advice/AuditGitEnvSentinel.md:19` (F1 HIGH: inherited GIT_COMMON_DIR can write into the named repo); the fix is recorded in `.ufo/waves/round-23/build/advice/RevengeEnvDocstring.md:20-28`. |
| kama | tools/citation-provenance.py:142-144; tests/report-audit/promisor-grid.py:136-139; repo-state-grid.py:47-51; tests/llamacpp-live/install-io-grid.py:208-210 | fresh env dicts (no inheritance) or prefix scrubs | Not route owners. |
| kasegi, kengaku, mori, tsukuroi, kagi, others | corpus/evidence/*, knowledge/*, .ufo/* | quotations of git(1) / git-worktree docs (`$GIT_COMMON_DIR` as a documented variable) | Documentation captures, not routes. Excluded from the table. |

Sibling-owned route for the same name: none. No sibling *needs* souji's value-check design. Every sibling scrubs
(or fresh-builds its env); none refuses on mismatch.

## 2. `RECEIPT-ENV` — no overlap

- Zero tracked hits for `RECEIPT-ENV` in any sibling's code or docs except one term collision:
  `kasegi-shokunin/.ufo/waves/round-42/wave1/ConnWave2Seed.txt:38` ("RECEIPT-ENV-LANDMINE", a critic label for a
  byte-compare under a non-quiescent environment). Same prefix, different meaning. No sibling emits `RECEIPT-ENV-*` refusals.
- Souji's `tools/souji-receipt-write.py` has no `GIT_COMMON_DIR` text at the base (grep count 0), so the C1 route is souji-only.

## 3. `freeze-check --chronology` — no overlap

- No tracked `--chronology` anywhere in the siblings (git grep over tracked files, `.md` included). Only souji has it:
  `tools/souji-freeze-check.py` (usage lines 7-8; RECEIPT-MEASURED-BEFORE-FREEZE at :63, :387).
- Name collision only: `chousa-shokunin/tools/freeze-check.py` (its own gate, `--selftest`, rounds 60-69, LOG.md:1953 ff.).
  It has no chronology flag. Different tool, different contract.

## 4. `core.fileMode` — mode-bit owners (extra term, same axis as C1 W2)

Tracked code and docs with `core.fileMode`:

- `tameshi-shokunin/tools/executor-source-pin-measure-v2.py:21-24, 207-210`: with `core.fileMode=false` (git-for-windows
  default) it forces exec bits through `git update-index --chmod=±x` so the commit carries them. A positive forcing for a
  host default. Also `tameshi PROVINCE.md:141` (host default false), `LOG.md:2751`, `.ufo/evidence/round-61/win-host/differential.py:36`
  (`-c core.fileMode=true` probe), `.ufo/evidence/round-60/win-host/host-probe.txt:22`.
- `kaidoku-shokunin/.ufo/waves/round-45/w2/R45W2SentPreflight/scripts/stage_d.py:139`: a fixture sets `core.fileMode true`
  then chmods (a sentinel test, not a route).
- `mori-shokunin/.ufo/waves/round-23/falsify/ReviewFileModes.md:32`: review text.
- `kama`, `tsukuroi`, `chousa`: `.ufo` captures or quotations of git-config; `chousa` hit is a quotation of tameshi's report.

Verdict: tameshi is the sibling mode-bit owner. Its job is to *force* exec bits under `core.fileMode=false`; souji's W2 is the
inverse (a caller-injected config *hides* a tracked mode change from the dirty check). Same config key, opposite purpose.
No sibling needs souji's refusal.

## Contested scope candidates (reported, not absorbed)

1. **Fleet-wide git-env scrub helper.** Eleven-plus copies of GIT_* scrub lists, and they drift:
   kumitate `GIT_ENV_DROP` lacks GIT_CONFIG*; kake `GIT_LOCAL_ENV` lacks GIT_NAMESPACE and GIT_CEILING_DIRECTORIES;
   kama is prefix-based; kotoba/kotodama lists differ again. A shared helper is a fleet decision, not souji's.
2. **Scrub versus value-check (design choice, not a conflict).** Siblings scrub GIT_COMMON_DIR unconditionally. Souji C1
   refuses mismatch and accepts equal value (W3). An operator-level question whether the fleet adopts the value-check rule.
3. **GIT_NAMESPACE and GIT_CEILING_DIRECTORIES (prereg L3).** Most siblings scrub both (kumitate, kake, kotodama, kama prefix).
   Souji's frozen C1 leaves them out, so souji is the outlier. Named limit, unchanged this round; flag to the L1 and operator.
4. **tameshi ARM17 canary** (`tools/design-blob-audit.py:603-618`): a poison-plus-invariant arm. A pattern for the W-rows and
   the K3/K4/K6/K7 decision, not code to import.
