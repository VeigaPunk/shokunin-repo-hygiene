STATUS: DONE — 18 isolated single mutants probed at ddb7347: 10 killed, 8 survived; exact bytes restored and paired controls passed.

# C3 jj receipt mutation probe — MutateJjNovel

- Measured revision: `ddb73474433977ff54b015ac3e77669ff2537353`. Advisory mutation evidence only; no integration or C3 admission judgment.
- Axes: **coverage** (six defect classes × three receipt tools), **calibration** (independent fixture/selftest verdicts with paired controls), **isolation** (scratch-only writes and byte-exact restoration).
- All three receipt tools were copied via read-only `git show` to `/var/tmp/souji-r17-MutateJjNovel/tools/`; each mutant received its own `/var/tmp/souji-r17-MutateJjNovel/arms/Mxx/tools/` copy. Exactly one behavior-bearing statement/condition was changed in one tool per arm. The other two receipt tools and the round-9 selftest helper stayed pristine.
- Final detector union: **10 KILLED / 8 SURVIVED / 0 INCONCLUSIVE**. Fixture alone: **6 killed / 12 survived**. Tool selftests alone: **10 killed / 8 survived**. A survivor is a coverage finding, not a contract change or evidence that the production behavior is wrong.
- 108 valid paired detector invocations (18 mutants × pristine/mutated/restored × fixture/affected-tool selftest), plus six earlier inconclusive quarantine selftest setup runs documented below. No timeouts. All captured stderr was empty.
- No tool installs or updates. Observed fixture versions: `git version 2.56.0`; `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`.

## Scoped findings and smallest fixes

### F1 — Failure-path and directory-target holes survive in all three engines

- `tools/souji-verify.sh:248`, `tools/souji-vault-verify.sh:440`, `tools/souji-quarantine.sh:984` at ddb7347: replacing the keep-commit enumeration failure return `2` with `0` survives both detectors (M05/M11/M17). The contract says `0 = novel`, `1 = no novelty`, `2 = git failure`; this mutant remains conservative about refusal but loses the history-unverifiable classification. **Smallest detector fix:** inject failure specifically into the `rev-list --glob=refs/jj/keep/* ...` query after keep discovery, and assert rc=2 or exact history-unverifiable evidence, not merely NOT-SAFE. This added detector was not run in this probe.
- `tools/souji-verify.sh:242`, `tools/souji-vault-verify.sh:434`, `tools/souji-quarantine.sh:978` at ddb7347: adding `[ -d "$repo/$rel" ] && return 1` after locals survives both detectors (M06/M12/M18). **Smallest detector fix:** target an existing pushed directory containing a descendant changed only in a keep-only commit, and require refusal with the intended reason. Preserve published-tree/deletion acceptance controls. These new directory cases were not run.
- Scoped detector-coverage verdict: **partial**. Production code was not changed; no production counterexample is asserted from an unexercised scenario.

### F2 — Remote-history discrimination is uneven

- `tools/souji-vault-verify.sh:436` and `tools/souji-quarantine.sh:980` at ddb7347: replacing `--remotes` with `--branches` in the known-object query survives both detectors (M09/M15). The same defect at `tools/souji-verify.sh:244` is killed by verify selftest J2 but survives the external fixture (M03).
- Verify fixture construction has a side-remote-only alternate published blob (`tools/souji-verify.sh:1266-1268` onward); vault fixtures publish their predecessor on the same history as the local branch (`tools/souji-vault-verify.sh:1437-1448`). External fixture J4 also leaves that published blob in local branch history (`tests/fixtures/r17-jj-receipts.sh:313-319,369-373`).
- **Smallest detector fix:** port the side-remote-only, no-local-branch-reachability discriminator to vault/quarantine selftests and the external fixture. Keep the expected SAFE result for an already-published predecessor. No such new test was executed here.
- Scoped detector-coverage verdict: **partial**; verify selftest provides a discriminator absent from the other two observed suites.

### F3 — External quarantine cases do not distinguish the quarantine-local mutations

- All six quarantine-only mutants M13–M18 survive the external fixture. Its quarantine worker invokes only `--dry-run --hold 0` (`tests/fixtures/r17-jj-receipts.sh:255-258`); the flow obtains stage-1 results from the copied verify engine (`tools/souji-quarantine.sh:434-438`) and dry-run returns before the second check (`:531-552` versus `:594`). In these arms that verify engine was intentionally pristine.
- Quarantine selftest nevertheless kills the quarantine-local glob, novelty-filter and roots mutations: M13/JJ4, M14/JJ3, M16/JJ7. Their pristine/restored quarantine selftests are `101 checks, 0 failed`; mutated runs each have exactly one failure.
- **Smallest detector fix:** retain dry-run/runbook coverage, but add bounded direct helper/roots assertions or a real hold-0 second-check scenario that reaches the quarantine-local helper after stage 1. Do not count the dry-run J3-quarantine row as independent coverage of quarantine's own novelty implementation. This suggested detector change was not executed.
- Scoped detector-coverage verdict: **partial for the fixture alone**; existing selftests cover three of these six local defects.

## Source provenance and exact input hashes

The following read-only commands actually supplied the copied bytes (stdout was written with the write tool, not checked out):
```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb73474433977ff54b015ac3e77669ff2537353:tools/souji-verify.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb73474433977ff54b015ac3e77669ff2537353:tools/souji-vault-verify.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb73474433977ff54b015ac3e77669ff2537353:tools/souji-quarantine.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb73474433977ff54b015ac3e77669ff2537353:tools/souji-round9-selftest.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb73474433977ff54b015ac3e77669ff2537353:tests/fixtures/r17-jj-receipts.sh
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh
```

| Input | SHA-256 |
|---|---|
| `tools/souji-verify.sh` | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` |
| `tools/souji-vault-verify.sh` | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` |
| `tools/souji-quarantine.sh` | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` |
| `tools/souji-round9-selftest.sh` | `dd7c636ebe39e70c489516500440a311167b5280d18c3a5e9db1399d2f62e5c2` |
| `tests/fixtures/r17-jj-receipts.sh` (committed and executed worktree bytes matched) | `6792df99dd13ded9d78baa0e34708351e88bbca94fc0b7e4ab5a9451209bbc99` |

All file:line references above and below refer to ddb7347 git-show bytes. The copied receipt tools and helper were executable (0755). No lane source was edited and no git write or jj invocation was issued directly against a real repository.

## Detector commands, bounds, and isolation

For each arm below, these **same two argv vectors** were run against pristine, mutated and restored bytes. Each run used a fresh working directory `/var/tmp/souji-r17-MutateJjNovel/runs/<id>/<phase>/<fixture|selftest>`; the tool paths/argv did not change between phases. Maximum three detector subprocesses at once. Outer deadline 240 seconds per process, SIGTERM then SIGKILL after 10 seconds only if needed (none were needed). The unmodified fixture also applies its own bounded `timeout` calls.

```sh
# M01 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M01/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M01/tools/souji-verify.sh --selftest
# M02 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M02/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M02/tools/souji-verify.sh --selftest
# M03 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M03/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M03/tools/souji-verify.sh --selftest
# M04 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M04/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M04/tools/souji-verify.sh --selftest
# M05 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M05/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M05/tools/souji-verify.sh --selftest
# M06 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M06/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M06/tools/souji-verify.sh --selftest
# M07 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M07/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M07/tools/souji-vault-verify.sh --selftest
# M08 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M08/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M08/tools/souji-vault-verify.sh --selftest
# M09 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M09/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M09/tools/souji-vault-verify.sh --selftest
# M10 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M10/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M10/tools/souji-vault-verify.sh --selftest
# M11 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M11/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M11/tools/souji-vault-verify.sh --selftest
# M12 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M12/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M12/tools/souji-vault-verify.sh --selftest
# M13 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M13/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M13/tools/souji-quarantine.sh --selftest
# M14 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M14/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M14/tools/souji-quarantine.sh --selftest
# M15 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M15/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M15/tools/souji-quarantine.sh --selftest
# M16 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M16/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M16/tools/souji-quarantine.sh --selftest
# M17 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M17/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M17/tools/souji-quarantine.sh --selftest
# M18 — repeated for phases pristine, mutated, restored
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-MutateJjNovel/arms/M18/tools
bash /var/tmp/souji-r17-MutateJjNovel/arms/M18/tools/souji-quarantine.sh --selftest
```

Environment setup (performed by the Eval orchestration, no alternative detector runtime): inherited GIT_*, JJ_*, SOUJI_*, XDG_*, HOME, SHOKUNIN_ROOT, HYAKU_STATE and TMPDIR were removed first; HOME/XDG/HYAKU/JJ_CONFIG, TMPDIR and fleet/ledger paths were then set inside that run directory. `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`, `GIT_CEILING_DIRECTORIES=/var/tmp/souji-r17-MutateJjNovel`, `LC_ALL=C`; an isolated global config set a fixture-only user and disabled automatic GC/maintenance. `GIT_CONFIG_COUNT=2` set gc.auto=0 and maintenance.auto=false. `SOUJI_VERIFY_BIN` selected the verify copy in the same arm. `JJ_BIN=/home/vgpnk/.local/bin/jj` was only executed by the authorized fixture after it entered its /var/tmp scratch cwd; both real-jj cases ran, not skipped.

The fixture and round-9 helper hardcode some `/var/tmp` mktemp arguments. To obey this seat's narrower write boundary without changing their bytes, PATH prepended this mktemp-only wrapper; it preserves paths already under this seat root and relocates other /var/tmp arguments under the per-run scratch tmp directory:
```bash
#!/usr/bin/env bash
set -euo pipefail
args=()
for arg in "$@"; do
  case "$arg" in
    "$SOUJI_MUTATION_ROOT"/*) ;;
    /var/tmp) arg="$SOUJI_MUTATION_TMP" ;;
    /var/tmp/*) arg="$SOUJI_MUTATION_TMP/${arg##*/}" ;;
  esac
  args+=("$arg")
done
exec /usr/bin/mktemp "${args[@]}"
```
Wrapper SHA-256: `08a407cd2968397ca834bcc5b8883f24b41f9e44dfdd1e9b7513b0e54c9383b7`. No git or jj command wrapper was introduced by this seat. The existing selftests retained their own failure-injection fixtures.

Only `--tool-dir` was supplied to the external fixture, as authorized. Consequently each external run reports `total=18 failed=<n> skipped=2`: **J6-verify and J6-vault are skipped** because no `--baseline-dir` was supplied. J9-file and J9-worktree ran using real jj. No 20/20 external-fixture result is claimed.

### Copy-only quarantine preflight correction (not counted as a kill)

Initial quarantine-copy selftests M13–M18 each returned rc=1, `selftest: 101 checks, 4 failed`, with these exact failures:
```text
FAIL G1 guard rc=4 (got=2)
FAIL G1 guard token (guard line)
FAIL SKIP1 metadata-prune rc (got=3 want=0)
FAIL SKIP1 result token (SKIPPED metadata-prune)
```
Those six results are **INCONCLUSIVE**, never kills. Cause of the copy-only setup: G1 checks `.git` directory existence before the live-fleet guard (`tools/souji-quarantine.sh:640-658`), while an externally inherited SOUJI_Q_SHOKUNIN_ROOT hid the selftest's own generated fleet from SKIP1 discovery (`:636,:1450-1453,:1655-1659`). The harness then created an empty `.git` directory only at each quarantine tool-copy root (a G1 guard precondition, not a production repository), and omitted SOUJI_Q_SHOKUNIN_ROOT only for quarantine selftest invocations. No tool code or oracle expectation changed. The corrected pristine selftests ran before mutation and passed 101/0; the same setup was used for their mutated and restored runs.

| Preflight arm | rc | stdout summary | stdout SHA-256 |
|---|---:|---|---|
| M13 | 1 | `ROUND9	28	0 ; selftest: 101 checks, 4 failed` | `c75f3407515ec41de42fd66224d41620e53ed19eb455d42815964ee1c781cf2c` |
| M14 | 1 | `ROUND9	28	0 ; selftest: 101 checks, 4 failed` | `49d0bff4cbb7dccd4b35e5385b305cd470214a917703aaf379100fecfb2d3096` |
| M15 | 1 | `ROUND9	28	0 ; selftest: 101 checks, 4 failed` | `e3f1ef6b6990b6f86a1e5848d4490ae7473e3d5188969ce735a7e0d613138b57` |
| M16 | 1 | `ROUND9	28	0 ; selftest: 101 checks, 4 failed` | `e25a592b8f01057a6892d34e36f9844462f6604516af1ab0737e155893145ecd` |
| M17 | 1 | `ROUND9	28	0 ; selftest: 101 checks, 4 failed` | `765d2af78a603eaf57e103ee5ce843fc9470a538a7e3b13865b1f3ad6221bae7` |
| M18 | 1 | `ROUND9	28	0 ; selftest: 101 checks, 4 failed` | `514ef9bd4e2c4548cb0b2877832e41346725c3950c2ee228839351e86caa2614` |

## Mutation matrix

KILLED means a passing pristine detector became nonzero on the single mutant and returned to zero on exact restoration. SURVIVED means both paired detectors stayed green. F = external fixture; S = affected-tool selftest. An expected detector described below is not an assertion that an unrun extra scenario passed.

| ID | Mutated ddb7347 site | Single defect | F | S | Union |
|---|---|---|---|---|---|
| M01 | `tools/souji-verify.sh:247` | Move keep glob after --not | KILLED | KILLED | **KILLED** |
| M02 | `tools/souji-verify.sh:253` | Refuse every existing keep object | KILLED | KILLED | **KILLED** |
| M03 | `tools/souji-verify.sh:244` | Use local branch object history | SURVIVED | KILLED | **KILLED** |
| M04 | `tools/souji-verify.sh:854` | Treat refs/jj as durable roots | KILLED | KILLED | **KILLED** |
| M05 | `tools/souji-verify.sh:248` | Return novelty on commit-query failure | SURVIVED | SURVIVED | **SURVIVED** |
| M06 | `tools/souji-verify.sh:242` | Skip existing directory targets | SURVIVED | SURVIVED | **SURVIVED** |
| M07 | `tools/souji-vault-verify.sh:439` | Move keep glob after --not | KILLED | KILLED | **KILLED** |
| M08 | `tools/souji-vault-verify.sh:445` | Refuse every existing keep object | KILLED | KILLED | **KILLED** |
| M09 | `tools/souji-vault-verify.sh:436` | Use local branch object history | SURVIVED | SURVIVED | **SURVIVED** |
| M10 | `tools/souji-vault-verify.sh:1061` | Treat refs/jj as durable roots | KILLED | KILLED | **KILLED** |
| M11 | `tools/souji-vault-verify.sh:440` | Return novelty on commit-query failure | SURVIVED | SURVIVED | **SURVIVED** |
| M12 | `tools/souji-vault-verify.sh:434` | Skip existing directory targets | SURVIVED | SURVIVED | **SURVIVED** |
| M13 | `tools/souji-quarantine.sh:983` | Move keep glob after --not | SURVIVED | KILLED | **KILLED** |
| M14 | `tools/souji-quarantine.sh:989` | Refuse every existing keep object | SURVIVED | KILLED | **KILLED** |
| M15 | `tools/souji-quarantine.sh:980` | Use local branch object history | SURVIVED | SURVIVED | **SURVIVED** |
| M16 | `tools/souji-quarantine.sh:1155` | Treat refs/jj as durable roots | SURVIVED | KILLED | **KILLED** |
| M17 | `tools/souji-quarantine.sh:984` | Return novelty on commit-query failure | SURVIVED | SURVIVED | **SURVIVED** |
| M18 | `tools/souji-quarantine.sh:978` | Skip existing directory targets | SURVIVED | SURVIVED | **SURVIVED** |

## Actual outputs by mutant

For every invocation below, captured stderr is empty and timeout=false. Summaries and failure lines are verbatim stdout excerpts (passing case lines are omitted, not reclassified). Full stdout SHA-256 is recorded for each run.

### M01 — souji-verify.sh — KILLED

Site: `tools/souji-verify.sh:247` at ddb7347.
- Mutation: `rev-list "--glob=refs/jj/keep/*" --not --branches --tags --remotes` → `rev-list --not "--glob=refs/jj/keep/*" --branches --tags --remotes`.
- Expected detector: Novel keep-only content must refuse: fixture J3/J3-vault; verify/vault selftest J1; quarantine selftest JJ4.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `f0d8b86dbd8e6b9f96a2e9fb4baf48ad7b781118b9373e08c3e7208c0a0e9f71` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `be7cd65d3d2acf0144f99e99772acbe6018d36dce6ac21c8f17c1708cf4db8ba` |
| mutated | fixture | 1 | `SUMMARY	total=18	failed=3	skipped=2` | `e304baf9c933582ede76378714a5e55b8879af9f0d9555868258cf86d246a933` |
| mutated | selftest | 1 | `ROUND9	16	0 ; selftest: 45 checks, 1 failed` | `54cba63d0be26766008d3c7c55aa93229c1e363a04400ba1fd851e0f8c5a7ef8` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `dc7cafe939d6a76e021eb6fef603259bcc854682b4b5591beef2385e00fb8309` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `5112b32580b07fadf1adffe9568d11503b3d5745b7a98e82bef8bc29dc0863c9` |

Mutated fixture failure output:
```text
CASE	J3	FAIL	exit=0 verdict=SAFE receipt=pushed evidence=intro=2c51c3351229 ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes expected=NOT-SAFE (keep-only commit carries novel content)
CASE	J3-quarantine	FAIL	exit=0 result=DRY-RUN-PASS receipt=pushed evidence=stage1=intro=2c51c3351229 ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes expected=DRY-RUN-BLOCKED|NOT-AUTHORIZED
CASE	J9-file	FAIL	jj=jj keep=98f8a103 verdict=SAFE receipt=pushed expected=NOT-SAFE
```

Mutated selftest failure output:
```text
FAIL J1: got SAFE(pushed) want NOT-SAFE(none) ev='intro=bdea5380d175 ref=refs/remotes/origin/master ancestor=yes snapshot=equal clean=yes'
```

### M02 — souji-verify.sh — KILLED

Site: `tools/souji-verify.sh:253` at ddb7347.
- Mutation: `printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0` → `return 0`.
- Expected detector: Published predecessor must remain accepted: fixture J4/J4-vault; verify/vault selftest J2; quarantine selftest JJ3.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `bb651b1299ad55c540fb80f4e4cfc8e70a7775976991cd6eafbb65df8bc17718` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `2b2dbe7993ef0aa5e89f9183ca6157165f8502ec91eea19bcd3b893242695ec4` |
| mutated | fixture | 1 | `SUMMARY	total=18	failed=2	skipped=2` | `2315ffaa5a8dab55ee78d43c14c89d002f031f5a75ea57790dc1f742da07d6ba` |
| mutated | selftest | 1 | `ROUND9	16	0 ; selftest: 45 checks, 1 failed` | `0d4453821e53a1a23ac62fa065baa64ef44875c4f7fd93f84e7c0fc85c1f0fef` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `9e408fced041f5cee0f07489f584fc78f3a69cfe568b9020b7e2f32c8457040d` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `6bd66e2d7b7fb5a841068128947f089e1a05a28f9466d5551b8141f55a0ce562` |

Mutated fixture failure output:
```text
CASE	J4	FAIL	exit=0 verdict=NOT-SAFE receipt=none evidence=pushed=unpushed-commits-touching intro=2c51c3351229 jj-keep-novel; obsidian=no-matching-ledger-row; stale=not-scratch-type expected=SAFE/pushed (blob already in remote history)
CASE	J4-quarantine	FAIL	exit=3 result=DRY-RUN-BLOCKED receipt=none evidence=stage1=NOT-SAFE(none) expected=DRY-RUN-PASS (non-novel predecessor)
```

Mutated selftest failure output:
```text
FAIL J2: got NOT-SAFE(none) want SAFE(pushed) ev='pushed=unpushed-commits-touching intro=bdea5380d175 jj-keep-novel; obsidian=no-matching-ledger-row; stale=not-scratch-type'
```

### M03 — souji-verify.sh — KILLED

Site: `tools/souji-verify.sh:244` at ddb7347.
- Mutation: `rev-list --objects --remotes -- "$rel"` → `rev-list --objects --branches -- "$rel"`.
- Expected detector: A blob published only on a side remote must count as known even if absent from local branch history; verify selftest J2 supplies this discriminator.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `8c98e23801add319ceb5579e3f05e6c24b4448227cdd6180650175be70ad52a9` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `95d7e917906b61964ac5d24c9cce39afd9034dc7fd8cdf1687bfdb52dd5eb41c` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `61e7da036999e15331b4ff3161d731b60248e0a8e5738052dd1bd9b2fac8caca` |
| mutated | selftest | 1 | `ROUND9	16	0 ; selftest: 45 checks, 1 failed` | `2ab85600778f4b1753d7de21eeae39b3f4e8fee16bc9e19d3fceaecf707a33fb` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `38f3eda9400ee9c7c291e068178bae169ad44c72f64b2bd606d80a144aeb4561` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `ead129579729c17e7e9229425b2920f1ee0a07d66ce9452b05b8b12d4f0dc2ff` |

Mutated selftest failure output:
```text
FAIL J2: got NOT-SAFE(none) want SAFE(pushed) ev='pushed=unpushed-commits-touching intro=f8a786125de8 jj-keep-novel; obsidian=no-matching-ledger-row; stale=not-scratch-type'
```

### M04 — souji-verify.sh — KILLED

Site: `tools/souji-verify.sh:854` at ddb7347.
- Mutation: `for-each-ref --exclude='refs/jj/' --format='%(objectname)'` → `for-each-ref --format='%(objectname)'`.
- Expected detector: Keep-only absent-worktree head must not earn metadata-prune: fixture J1/J1-vault/J9-worktree; verify/vault selftest J4; quarantine selftest JJ7.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `e94bbaf16a67a7abf8aa0142ddcbf30b21c81ad7d36cc1cf78dc00dd74e2efcf` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `61bb2f21221e80995262cd37db32606767de53ea1e88f8dfc288c0917aed6051` |
| mutated | fixture | 1 | `SUMMARY	total=18	failed=2	skipped=2` | `c009df8b47b4842b9329c36a72149e88d15e1d2b2ab0d525d6fa98e36e12e06e` |
| mutated | selftest | 1 | `ROUND9	16	0 ; selftest: 45 checks, 1 failed` | `8b6ece39fdfff99ecbfc4f3d48bb4a51757a30cf924f4db4636f4f40a68798a2` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `8dc1dda5d8235efa963ce0d8475cc8632c51f169b9a12619bbe9eff13e0381c3` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `209b6834d0545efcc31b7fa01caafa0723629bcc45f86119b594c8daf788889c` |

Mutated fixture failure output:
```text
CASE	J1	FAIL	exit=0 verdict=SAFE receipt=metadata-prune evidence=dir=absent unique=0 head=2c637a8ea126 owner=keeprepo durable-refs-only=yes expected=NOT-SAFE,never-SAFE(metadata-prune)
CASE	J9-worktree	FAIL	jj=jj keep=6093695b verdict=SAFE receipt=metadata-prune evidence=dir=absent unique=0 head=6093695b5252 owner=jjrepo durable-refs-only=yes expected=NOT-SAFE,never-SAFE(metadata-prune)
```

Mutated selftest failure output:
```text
FAIL J4: got SAFE(metadata-prune) want NOT-SAFE(none) ev='dir=absent unique=0 head=a7cdac3bedaa owner=jjrepo-shokunin durable-refs-only=yes'
```

### M05 — souji-verify.sh — SURVIVED

Site: `tools/souji-verify.sh:248` at ddb7347.
- Mutation: `return 2 after the keep-commit rev-list fails` → `return 0 at that same failure arm`.
- Expected detector: A failing keep-commit enumeration must take the rc=2 history-unverifiable route, not claim rc=0 novelty; requires an exact failure-path/evidence assertion.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `c975f65c9e18c356c99813b03b957c211d258e79822c8df4b64c2480e3359f6a` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `90697fa16eacab230d6af825d5fe580cd97deeaab6f06a7df9fc1057afaafa83` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `59523c23c1eca8c3f4d264c31fcaab3700562796194be769ac9304f063f14c33` |
| mutated | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `73472dd2010e7c9ad08c5158760c7b4cc7fe1274a67787ccdcb396b08d694d4f` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `e75f7f7c4d16a0cc4b249175728f79751050c5777a8ad1bf7439d4a154b2fe61` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `55d6159528943a11c5a3e83ce06f889306080d9e3199390be50e44080803fbdb` |

No mutant failure line: both detectors returned rc=0 on this mutated arm as well as its pristine/restored controls.

### M06 — souji-verify.sh — SURVIVED

Site: `tools/souji-verify.sh:242` at ddb7347.
- Mutation: `no early directory exemption` → `insert [ -d "$repo/$rel" ] && return 1 immediately after local declarations`.
- Expected detector: A pushed directory with keep-only novel descendant content must still refuse; requires a directory target, not just file targets.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `a2119179d74e922344e0f4adce53eff2143dcaebb29cb1ef75ed44c16873c1e4` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `84c7c20eb5deb418d235c691e633ddab54ac549c686b65f3a145373122dcb0ca` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `47c4d1919ae2ecc1a86b1430c2da8e8ae6eded528bc840f209c7a181f67d6a4d` |
| mutated | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `b9d3a39c3b9629d72b6cfe4584729872dff079d3990f99759f2124789487804e` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `b7370dd98492ad092967e8dfe1aca81624ff5b7f0e72cc1e76eee1f245193d7c` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 45 checks, 0 failed` | `e1343d68c194465c8b66818ea9c3836445eb78920c0b191e516390138b997744` |

No mutant failure line: both detectors returned rc=0 on this mutated arm as well as its pristine/restored controls.

### M07 — souji-vault-verify.sh — KILLED

Site: `tools/souji-vault-verify.sh:439` at ddb7347.
- Mutation: `rev-list "--glob=refs/jj/keep/*" --not --branches --tags --remotes` → `rev-list --not "--glob=refs/jj/keep/*" --branches --tags --remotes`.
- Expected detector: Novel keep-only content must refuse: fixture J3/J3-vault; verify/vault selftest J1; quarantine selftest JJ4.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `0fa77edde223c526db981afa56bdb11cb5c7ea46300f928d246980ba50032486` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `ea24f06d6fc70c6eccbcac177e2b92737c031a9db09b5324153c2edb45127722` |
| mutated | fixture | 1 | `SUMMARY	total=18	failed=1	skipped=2` | `383a168df6e4d37b3f3c82e0f8e98e56e9ddb3340c3902f9fa14d40bd25dbb28` |
| mutated | selftest | 1 | `ROUND9	16	0 ; selftest: 57 checks, 1 failed` | `23829b0c676b13b8a2c017d7e50ea73e35ff2d6b6ca2e6c6ca8a8494a4c62772` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `06324c6d361b0d5c5ad95e5b37ec0f0dafe4f9c715182153d60b0f0ad946d883` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `173a3348a71c1510f2cd3b5bf7e093948ef8c20d17fc82937d1106cdecc49573` |

Mutated fixture failure output:
```text
CASE	J3-vault	FAIL	exit=0 verdict=SAFE receipt=pushed r4=VERIFIED(pushed) expected=NOT-SAFE
```

Mutated selftest failure output:
```text
FAIL J1: r4='VERIFIED(pushed)' want='NOT-VERIFIED(none)'
```

### M08 — souji-vault-verify.sh — KILLED

Site: `tools/souji-vault-verify.sh:445` at ddb7347.
- Mutation: `printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0` → `return 0`.
- Expected detector: Published predecessor must remain accepted: fixture J4/J4-vault; verify/vault selftest J2; quarantine selftest JJ3.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `bbfdc0b46eb1fbc17f5d89109d3c6195fe78f75cb770ba7033dad06857d84314` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `8577d98f2c38246263ee8170391161fad8d7f24d73f5c7a074e143e5905b41b8` |
| mutated | fixture | 1 | `SUMMARY	total=18	failed=1	skipped=2` | `be6110fdfa1770187c1700b66f8d7e920bef40ef1af27c8e2a08c1bd9ac4164e` |
| mutated | selftest | 1 | `ROUND9	16	0 ; selftest: 57 checks, 1 failed` | `d273c33219386a24b0eadf8c3e7084dbae697e5a2c3ee030f893408536518e8c` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `2a61bbbe0938d68da3fc21a3e62eee4daf93479281ac08b12f93c55ed7c250f8` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `ecbbab4aa72db15964ef406d6c0c9d3d1bd17a3fbbb1e2b424f0ebbaa105f282` |

Mutated fixture failure output:
```text
CASE	J4-vault	FAIL	exit=0 verdict=NOT-SAFE receipt=none r4=NOT-VERIFIED(none) expected=VERIFIED(pushed)
```

Mutated selftest failure output:
```text
FAIL J2: r4='NOT-VERIFIED(none)' want='VERIFIED(pushed)'
```

### M09 — souji-vault-verify.sh — SURVIVED

Site: `tools/souji-vault-verify.sh:436` at ddb7347.
- Mutation: `rev-list --objects --remotes -- "$rel"` → `rev-list --objects --branches -- "$rel"`.
- Expected detector: A blob published only on a side remote must count as known even if absent from local branch history; verify selftest J2 supplies this discriminator.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `72bc1fa0f7dd85711549edc771d64660d81e8226995d3f0a8f166b977bb92bf5` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `77fae07204d7600d25ed06734cc8765ffcf27c95bb022f689c13f9a36cbf2fec` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `b50a91dcbdb6d100216c7550967db13b38486f5ec7964b0694b7b125da0bbbb8` |
| mutated | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `0f88e975a3e93ae4deb0b835d238258b7859bcc69c475f0cd16e768ab41f56cb` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `fa54c660810d64fa19b1f8f929a590ea917621b6c7591e22b278e9fe50566e8d` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `164f9158450d2cde75f9a406fe60beaa9a0c575607dcabacfb21c470050038fb` |

No mutant failure line: both detectors returned rc=0 on this mutated arm as well as its pristine/restored controls.

### M10 — souji-vault-verify.sh — KILLED

Site: `tools/souji-vault-verify.sh:1061` at ddb7347.
- Mutation: `for-each-ref --exclude='refs/jj/' --format='%(objectname)'` → `for-each-ref --format='%(objectname)'`.
- Expected detector: Keep-only absent-worktree head must not earn metadata-prune: fixture J1/J1-vault/J9-worktree; verify/vault selftest J4; quarantine selftest JJ7.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `3231703121775959a9220c3ff31b5b34a75aa4c17b4122730cb68789a46dee3e` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `6a1c8da4259fc900de2f4dfad42a4860cdc8e166327e82ccbbd7f466f55fa507` |
| mutated | fixture | 1 | `SUMMARY	total=18	failed=1	skipped=2` | `aef99ce973bcec0fd6357dbe957cb0910631e84db8919e973bb89efc34ed1236` |
| mutated | selftest | 1 | `ROUND9	16	0 ; selftest: 57 checks, 1 failed` | `34a07704be34f81851cfcfabe4bf2c8ab63c690750cd3419299679b8312a75a1` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `f96123ca693126d89a1ef88170d382976cd5ec81dcd8295e59b3ecfbcf66877d` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `042169086442041db4cc40e549bbfbdbec5d3ec6e727175d759e9a1c487924e6` |

Mutated fixture failure output:
```text
CASE	J1-vault	FAIL	exit=0 verdict=SAFE receipt=metadata-prune r4=VERIFIED(metadata-prune) expected=NOT-SAFE,never-VERIFIED(metadata-prune)
```

Mutated selftest failure output:
```text
FAIL J4: r4='VERIFIED(metadata-prune)' want='NOT-VERIFIED(none)'
```

### M11 — souji-vault-verify.sh — SURVIVED

Site: `tools/souji-vault-verify.sh:440` at ddb7347.
- Mutation: `return 2 after the keep-commit rev-list fails` → `return 0 at that same failure arm`.
- Expected detector: A failing keep-commit enumeration must take the rc=2 history-unverifiable route, not claim rc=0 novelty; requires an exact failure-path/evidence assertion.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `3219e654d124d2cda5ef90298b8dc34c1ff49effd0d0508845a84c7c4db3ce92` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `069f284e272c153ecf93362e9da068f5ac44a34d8ebf2afc78c15eb654e8fa33` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `a7dfbfa39d885f0dbfaa49f5b757c5e90951db9ec9855b5d76a99b186c60561f` |
| mutated | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `8d8cd8fa01c20fd4708907041fa56cc456b435bad3510cea0ba0414258e8dec2` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `88f3c4f188c950ee908532400e302d2112fb666f4e64a78cad163d8801a0fab2` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `8bda104e4c5ddf9f9b70da80062f767ad89d327173fc69bc887f8afd5c75b6c9` |

No mutant failure line: both detectors returned rc=0 on this mutated arm as well as its pristine/restored controls.

### M12 — souji-vault-verify.sh — SURVIVED

Site: `tools/souji-vault-verify.sh:434` at ddb7347.
- Mutation: `no early directory exemption` → `insert [ -d "$repo/$rel" ] && return 1 immediately after local declarations`.
- Expected detector: A pushed directory with keep-only novel descendant content must still refuse; requires a directory target, not just file targets.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `6c7f77c8d6220eefb5cdda482d1f89caa4e8f4a8feea61ca8696b60d66bac3e2` |
| pristine | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `f639f56cee9fd1f953a4fc4588c99e51839e11261a54307c48d6bbb7ae051b7b` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `dcc26c4fea121045965e1a680f1c98a28bf1565cd5ec0b11a1abfd09e3b37ba4` |
| mutated | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `0545fd592b013df731024b769133822c5d7c87d4140a285cdd103dba63ec5855` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `5ab06c7e26faa1aa08fea5d5e808851cbb6c9b5f0bad63ab03778271ecfd3cc3` |
| restored | selftest | 0 | `ROUND9	16	0 ; selftest: 57 checks, 0 failed` | `7d75274d370a31349dcfc0731d9374215e29ca40fead76fc1c8e50c6a0a5729a` |

No mutant failure line: both detectors returned rc=0 on this mutated arm as well as its pristine/restored controls.

### M13 — souji-quarantine.sh — KILLED

Site: `tools/souji-quarantine.sh:983` at ddb7347.
- Mutation: `rev-list "--glob=refs/jj/keep/*" --not --branches --tags --remotes` → `rev-list --not "--glob=refs/jj/keep/*" --branches --tags --remotes`.
- Expected detector: Novel keep-only content must refuse: fixture J3/J3-vault; verify/vault selftest J1; quarantine selftest JJ4.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `a74c714c11e23bfbe9f107df1226d442e6e34d5a52ebc6962dd274a3a97396cb` |
| pristine | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `b4b87611445f537c9a536d8830121f63e53e39b33793fdc7a10413f247d8e3e4` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `22d50ba886e8cfde6d072f2d6b108a437e3b6e85fe8fd673626b9f093a1bbe00` |
| mutated | selftest | 1 | `ROUND9	28	0 ; selftest: 101 checks, 1 failed` | `eed677f1ed71776898779230e52949f06af60401cc6539b8a9ecb77fb8f7c844` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `e2ee8d9995e46a8d6c420635a5acb9dea76d0284c06a5249401f3c075f551a5f` |
| restored | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `4a11484f79a97e2052a442c7a15b9f60180a9bf6a60ae0fd017addedf39dfbb7` |

Mutated selftest failure output:
```text
FAIL JJ4 novel keep-only blob -> novelty (rc=1)
```

### M14 — souji-quarantine.sh — KILLED

Site: `tools/souji-quarantine.sh:989` at ddb7347.
- Mutation: `printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0` → `return 0`.
- Expected detector: Published predecessor must remain accepted: fixture J4/J4-vault; verify/vault selftest J2; quarantine selftest JJ3.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `acbcf271e555e73d79a421ec558026a57f6fb689a69ce1ca29d9c86ec2c0a650` |
| pristine | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `82036caa87882b6b71dc6f66da42c6b02b385445b823b8009b6932792dc2b725` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `8b8b7b16ae8b7d970b4ff04f1fa116df4073249c9eb5b9f1df5e427410eae302` |
| mutated | selftest | 1 | `ROUND9	28	0 ; selftest: 101 checks, 1 failed` | `81ddc076aaa0edd132fbcefa99c4ec90c043c4411a9b5dd6fb52382f7004ad57` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `f9fc2bbcdf772c5d9b2e747c52e85c06edbe8a3857b2d657c84ff727e9ecc79a` |
| restored | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `8e1a8044f57668b1a3e558bfa8683468b29251f7a899355f0c5bf69d39267a20` |

Mutated selftest failure output:
```text
FAIL JJ3 identical-content predecessor -> no novelty (rc=0)
```

### M15 — souji-quarantine.sh — SURVIVED

Site: `tools/souji-quarantine.sh:980` at ddb7347.
- Mutation: `rev-list --objects --remotes -- "$rel"` → `rev-list --objects --branches -- "$rel"`.
- Expected detector: A blob published only on a side remote must count as known even if absent from local branch history; verify selftest J2 supplies this discriminator.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `03993876606dcca462a75b1c6bdb8f39af4c38f66e5350be008d6682d271a6b3` |
| pristine | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `e88adc5bf6dfb3273b379dd4b2caf401cb6af5636f5b5f372792b0f6a5eb6c38` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `69de5775a30b0a88c70284cccb4ae3497cc35d94521eda73a533529803577c75` |
| mutated | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `ba2c5a3768049e5a82093f67ddcc16afab48817ab3b511f081eb883b4c23716d` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `5016783c3316979f9c0b125f6547518ec746c90ca34b88ac06edee051a5f2d8b` |
| restored | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `a058d4fa6d809ef78e991c73ee73902fa887aff749adca4813c0814b38d04e37` |

No mutant failure line: both detectors returned rc=0 on this mutated arm as well as its pristine/restored controls.

### M16 — souji-quarantine.sh — KILLED

Site: `tools/souji-quarantine.sh:1155` at ddb7347.
- Mutation: `for-each-ref --exclude='refs/jj/' --format='%(objectname)'` → `for-each-ref --format='%(objectname)'`.
- Expected detector: Keep-only absent-worktree head must not earn metadata-prune: fixture J1/J1-vault/J9-worktree; verify/vault selftest J4; quarantine selftest JJ7.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `b84bf8525c4640400ba6be8320059966930ec2ded64776de8f93d36330effbba` |
| pristine | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `463c4bb3a446f25207528e3157c01b9d94d684a646d3068a1a1edfd72353de4b` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `fd8d4004c3869f459437d62dc0c92ad8320c1a32046ae814a9ba141a21692d7b` |
| mutated | selftest | 1 | `ROUND9	28	0 ; selftest: 101 checks, 1 failed` | `bc0d989b07cff1eb1c4ba9c6218e316faaae88386ca88d1ec98965719ea09139` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `c2f2963fafe818bc369bb872f3a56554a21b408816edccfaa7f9d6a53595933b` |
| restored | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `79906124427cdfc4b104078ee5def0cee11192ea55c855f6adab73e5a5e65d07` |

Mutated selftest failure output:
```text
FAIL JJ7 head only in refs/jj/keep -> NOT-SAFE (verdict=SAFE receipt=metadata-prune)
```

### M17 — souji-quarantine.sh — SURVIVED

Site: `tools/souji-quarantine.sh:984` at ddb7347.
- Mutation: `return 2 after the keep-commit rev-list fails` → `return 0 at that same failure arm`.
- Expected detector: A failing keep-commit enumeration must take the rc=2 history-unverifiable route, not claim rc=0 novelty; requires an exact failure-path/evidence assertion.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `1c59fd688039f9a0d13dea595d1e863bef98e2cceac1065a8c40c0793a57292b` |
| pristine | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `3e51fb34fdd4680b3680be147cab1a48494aac6126b559441c4effb02a5eb69e` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `8fcdfd39684f7b2908fa3255fcda9d13c622d7475587e85b7caf3754e915c1c9` |
| mutated | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `6660c6f26ed178e3817d86975c13a193168f405921ef44b56ae4689299f41e0d` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `9dbb41e5bf76acd7b5fa252a72586763e13612e2d1999fac270efa426aff7ed8` |
| restored | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `eee4b2cb222a57ac617de51ab42c15111217509f8a55b22dae346a0deb5bf6ea` |

No mutant failure line: both detectors returned rc=0 on this mutated arm as well as its pristine/restored controls.

### M18 — souji-quarantine.sh — SURVIVED

Site: `tools/souji-quarantine.sh:978` at ddb7347.
- Mutation: `no early directory exemption` → `insert [ -d "$repo/$rel" ] && return 1 immediately after local declarations`.
- Expected detector: A pushed directory with keep-only novel descendant content must still refuse; requires a directory target, not just file targets.

| Phase | Detector | rc | Verbatim summary | Full stdout SHA-256 |
|---|---|---:|---|---|
| pristine | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `8a6af901fbd5d4476267ed99dcac7bc3b100e8159cde67ecf4168da517449290` |
| pristine | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `f3d3fc9fc9b95e4d5bda477588b48abb9c9336dba207362c520b416fc4555539` |
| mutated | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `8c1ce8d1ee41717312e6d239614768f642032e3c43a99ceebb0dd164a47bdd2d` |
| mutated | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `6d1fdbb87e5b4eb62d03e5a64ce1b16b8afd4ebc1a2ad30512f49e9ced74d214` |
| restored | fixture | 0 | `SUMMARY	total=18	failed=0	skipped=2` | `e65b112cd3d2651bbe0fb43b78c51b8005916f85f0f08ebe948fd2c4403a3433` |
| restored | selftest | 0 | `ROUND9	28	0 ; selftest: 101 checks, 0 failed` | `9849b4a7a039bdfbfc5b014b4e925d82042b3b9ff702dcb62994925129a8012a` |

No mutant failure line: both detectors returned rc=0 on this mutated arm as well as its pristine/restored controls.

## Before / mutant / restored byte evidence

Actual `sha256sum -- <all 72 arm tool/helper paths>` was run after mutation and after surgical reversal; before hashes are the immutable input hashes also printed by pristine fixture TOOL records. Every target restored to its original SHA-256, and all three non-target inputs in each arm remained identical to their pinned source bytes.

| ID | Before SHA-256 | Mutant SHA-256 | Restored SHA-256 |
|---|---|---|---|
| M01 | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` | `ae7e8033f686e875c8b8c448c9f71255381de8fa3276bd50fe3f31e2fcb49eec` | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` |
| M02 | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` | `4a9a520e1cae833e907ed6c7ef4a603a0440624f12fc0f010fd964f7f4f3407f` | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` |
| M03 | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` | `d68e5ed34df63f069842c87cc2bd5391428175f80ee0f56b6a1fdd3ade85a8af` | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` |
| M04 | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` | `70af200382fef000f487d6f39c5ab18d7c51d397624935d8d8a243b33a45a40a` | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` |
| M05 | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` | `5ec821c77ce8f8b946f4b6b93086ee52704373ded2bbf9e043cbbde38ff939ec` | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` |
| M06 | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` | `d728ab87693eab60fe88b10017eb9472371ae2b9abc80aa19780e3caf6c39c87` | `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f` |
| M07 | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` | `b76a4207ef2ca186861d39910964800a850c46525739301aae23d0100970564c` | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` |
| M08 | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` | `46e151d6481e87c101001e1afa1e5778aa3599622ad48ffe9a72db2a609517cf` | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` |
| M09 | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` | `09d9ef4eb72b7e81aa047123b8d4bec77ede87812592dcb833f3c31f85c712c4` | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` |
| M10 | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` | `6f1c3cd9d5d707625e36106834d2bd298a93126590b53855ef0b28240e9081d7` | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` |
| M11 | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` | `9e144c01c481fc5c29e2a0bfbd88dde80ee59bb44784ede05569f0df6a79774a` | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` |
| M12 | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` | `5364f5738ebe4f70acc850bf7b8a8bf9cf8deb83833a1a0e082651a2cd80079e` | `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64` |
| M13 | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` | `841b8c114fb720bc4a27e3780c13c004168b4c62dcfe320fbb811a3aec13a287` | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` |
| M14 | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` | `ffb4a8ce632d71755595eb2874cc20edb1ba41a79afe595df160de76128c0d47` | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` |
| M15 | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` | `0e46378e641cdaf98fcf3c4e1e8c72e79a244c104ba106ab99f9801aabd30f6b` | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` |
| M16 | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` | `9d1966b31a36d2972b46fbd770137457bf8ea1443fc7956c5e0ab74a7b20b54d` | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` |
| M17 | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` | `84b0cd6ba0515792e856ffb783e0685ec3943684592b4ee00d1184fbfea0fe6e` | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` |
| M18 | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` | `3bbab27afbf3cfce8a22cefbf9dbf2f283fafb2ccb10115cf868452414c92e04` | `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676` |

Exact-byte comparison commands were also run for every arm/tool/helper pair (72 total):
```sh
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M01/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M01/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M01/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M01/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M02/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M02/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M02/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M02/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M03/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M03/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M03/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M03/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M04/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M04/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M04/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M04/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M05/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M05/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M05/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M05/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M06/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M06/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M06/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M06/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M07/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M07/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M07/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M07/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M08/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M08/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M08/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M08/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M09/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M09/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M09/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M09/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M10/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M10/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M10/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M10/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M11/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M11/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M11/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M11/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M12/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M12/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M12/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M12/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M13/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M13/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M13/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M13/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M14/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M14/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M14/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M14/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M15/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M15/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M15/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M15/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M16/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M16/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M16/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M16/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M17/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M17/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M17/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M17/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M18/tools/souji-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-vault-verify.sh /var/tmp/souji-r17-MutateJjNovel/arms/M18/tools/souji-vault-verify.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-quarantine.sh /var/tmp/souji-r17-MutateJjNovel/arms/M18/tools/souji-quarantine.sh  # rc=0; stdout empty; stderr empty
cmp -- /var/tmp/souji-r17-MutateJjNovel/tools/souji-round9-selftest.sh /var/tmp/souji-r17-MutateJjNovel/arms/M18/tools/souji-round9-selftest.sh  # rc=0; stdout empty; stderr empty
```

Observed restoration controls: every external fixture returned rc=0 with `SUMMARY	total=18	failed=0	skipped=2`; verify returned rc=0 with `selftest: 45 checks, 0 failed`, vault `57 checks, 0 failed`, quarantine `101 checks, 0 failed`. No initial failing preflight run was used to classify a kill.

## Cleanup

```text
$ rm -rf -- /var/tmp/souji-r17-MutateJjNovel
rc=0; stdout=''; stderr=''
$ stat -- /var/tmp/souji-r17-MutateJjNovel
rc=1
stat: cannot statx '/var/tmp/souji-r17-MutateJjNovel': No such file or directory
```

All detector processes had completed before cleanup. The only retained filesystem write is this scoped report. No fleet state, census/operator-sweep-20261019, credentials, lane source, sibling source, commits or integration were touched.
