STATUS: DONE — the three C3 selftests are inventoried with exact commands and pinned 5fa6017 counts (40/51/91 checks, R9 16/16/28); the headline is that 6 of the 16 code sites named by C3 are dead code and none of the 10 live sites is exercised by a jj-shaped or unpushed-touching case.

Seat: SoujiR17-3.RevVerifySelftests (reviewer, leaf — no delegation, no commits, no lane writes except this file).
**PROBE DISCLOSURE (self-reported, voidable):** at ~13:52 I mistakenly ran `git reset -q -- .` in the lane while intending a status refresh. That is a forbidden git write under the probe rule. Observed post-state: `git diff --cached --name-only` is empty (0 staged paths), every concurrent worktree edit is still present and unstaged (` M tools/souji-{verify,vault-verify,census,landing-gate,seat-audit}.py|sh`), and `git reset` without `--hard` cannot modify the worktree or any commit. I cannot prove whether a sibling had staged paths at that instant; if one did, this reset unstaged them without altering their content. Treat this seat's evidence as audited-and-disclosed; L1 must decide admissibility. Nothing else below depends on the index.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`; rev measured: `5fa6017ddcae9f6bd4412df44765f6360cb16294` (r16 landing head).
No tool was installed or upgraded (none needed). No selftest, fixture, matrix runner or census was executed — this assignment says "No execution"; every claim below is a read, a `git show`/`git diff`/`git log`, or a `sha256sum`.

Blob identity at 5fa6017 (sha256 of `git show 5fa6017:<path>`, all three worktree files byte-identical at the start of this probe):

| path | sha256 | equals r13 record |
|---|---|---|
| tools/souji-verify.sh | `9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd` | `census/round-13/verification.json:7` |
| tools/souji-vault-verify.sh | `f9e778ca478c7aa8b33234ee793030df631c1b9fcebc942b1ff41d0008ed9c5b` | `census/round-13/verification.json:8` |
| tools/souji-quarantine.sh | `df4075112c36bae804b98766c4eb66b0e5b2b80b76d7333475ede27b06b168c4` | `census/round-13/verification.json:9` |
| tools/souji-round9-selftest.sh (shared dependency) | `dd7c636ebe39e70c489516500440a311167b5280d18c3a5e9db1399d2f62e5c2` | not pinned |

Caveat observed during the probe: executors began landing C3 in this worktree while this inventory was taken. `tools/souji-vault-verify.sh` went `M` at 13:40 (+31 lines, helper/comments only at that moment); by 13:56 both it (1676 lines, `745fedbe…`) and `tools/souji-verify.sh` (1355 lines, `84343136…`) carried in-flight edits, while `tools/souji-quarantine.sh` stayed byte-identical to 5fa6017 (`df407511…`) throughout. Line numbers below are 5fa6017-blob-relative. C3's "before" runs must use `git show 5fa6017:` bytes, and this report does not audit the in-flight implementations — only the baseline surface they must preserve.

## 1. Entry points and the exact command list

Registry rows (exact, current wording): `SKILL.md:137` souji-verify, `:138` souji-vault-verify, `:139` souji-census, `:140` souji-quarantine. All four are **probes**, verdict map `0 clean` / `1 failed selftest or could-not-evaluate setup (legacy debt)` / `2 could-not-evaluate usage`; the pinned-value column for all three C3 tools reads "**none; no pinned complete id set**" (`SKILL.md:137-138,140`). Authority note: `SKILL.md:135` requires `TMPDIR=/var/tmp` for the legacy selftests.

Run from the lane root. Every command below is read-only over the lane; all scratch is under `TMPDIR`/`/var/tmp`.

```sh
# C3, before and after (the three embedded suites)
TMPDIR=/var/tmp bash tools/souji-verify.sh --selftest
#   expect rc=0, last line exactly:  selftest: 40 checks, 0 failed
TMPDIR=/var/tmp SOUJI_CLI_BIN=/bin/false bash tools/souji-vault-verify.sh --selftest
#   expect rc=0, last line exactly:  selftest: 51 checks, 0 failed
TMPDIR=/var/tmp bash tools/souji-quarantine.sh --selftest
#   expect rc=0, last line exactly:  selftest: 91 checks, 0 failed
#   (quarantine also requires `rg` on PATH — hard exit 1 otherwise, tools/souji-quarantine.sh:1417)

# external regression for quarantine (gate row SKILL.md:145)
TMPDIR=/var/tmp bash tests/fixtures/r13-quarantine-bounds.sh > /var/tmp/r17-qbounds.out; echo rc=$?
grep '^SUMMARY' /var/tmp/r17-qbounds.out
#   expect rc=0 and:  SUMMARY	total=5	failed=0	hung=0

# optional, richer external battery for verify (NOT a registry row; 30 emit_case sites)
bash tests/runner-27.sh --out /var/tmp/r17-runner-27.json; echo rc=$?
#   always pass --out; the default writes tests/results/runner-27.json inside the lane

# C1 (sibling claim) — committed baseline at 5fa6017
TMPDIR=/var/tmp bash tools/souji-census.sh --selftest
#   expect rc=0, last line:  selftest: 38 checks, 0 failed
python3 tests/fixtures/r15-census-config.py --tool tools/souji-census.sh
#   expect exit 0 and:  SUMMARY	total=20	failed=0
python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh
#   expect exit 0 and:  SUMMARY	total=12	failed=0
python3 census/round-16/run-matrix.py --changed WORKTREE --output /var/tmp/r17-matrix-$(date +%s).json
#   the committed runner at this rev; refuses an existing output path; extracts arms with git show
#   and chmod 0755 each copy (census/round-16/run-matrix.py:1-20 and :101-114)

# C2 (routed, adjacent) — seat audit
python3 tools/souji-seat-audit.py --selftest
#   expectation at r16: 20 cases / 0 failures (corpus/lessons/round-16.md:13)
```

### 1.1 Old-bytes replay (for "after" comparisons)

The embedded selftests re-exec `"$SELF"` (verify:1259, vault:1221, quarantine:1345) and the shared R9 runner is resolved as `$SCRIPT_DIR/souji-round9-selftest.sh` (verify:1270, vault:1576, quarantine:1610), so a bare file copy fails. Recipe:

```sh
mkdir -p /var/tmp/souji-r17-base/tools && git init -q /var/tmp/souji-r17-base
for f in souji-verify.sh souji-vault-verify.sh souji-quarantine.sh souji-round9-selftest.sh; do
  git show 5fa6017:tools/$f > /var/tmp/souji-r17-base/tools/$f
done
chmod +x /var/tmp/souji-r17-base/tools/*.sh
cd /var/tmp/souji-r17-base
TMPDIR=/var/tmp bash tools/souji-verify.sh --selftest
TMPDIR=/var/tmp SOUJI_CLI_BIN=/bin/false bash tools/souji-vault-verify.sh --selftest
TMPDIR=/var/tmp bash tools/souji-quarantine.sh --selftest
```

Three mechanics that matter, all verified by reading:
- `chmod +x` is required — the r16 precedent is `census/round-16/RerunLegacySelftest.md` F1 (`env: … Permission denied`, exit 126 from a 0644 copy).
- All four files must sit in one `tools/` directory: R9 is a sibling dependency, and quarantine's default receipt engine is `$REPO_ROOT/tools/souji-verify.sh` (`tools/souji-quarantine.sh:158`, hard failure at `:592-595`).
- For quarantine, the **parent** directory must be a git repo: G1 runs `"$SELF" --hold 0 "$REPO_ROOT" …` (`:1451-1453`) and `run_mode` exits 2 on `[ ! -d "$Q_CREPO/.git" ]` (`:589-591`) before the live-fleet guard can return 4. `git init -q /var/tmp/souji-r17-base` satisfies it; `LIVE_FLEET_ROOT` is then `/var/tmp` (`:149`), so the guard still fires as G1 expects.

## 2. Expected counts at 5fa6017, with citations

Committed evidence is `census/round-13/verification.json` — the only committed execution of these three suites in any `census/round-*`. I checked every round: only `round-13` contains `souji-{verify,vault-verify,quarantine}.sh-selftest` entries (`:113`, `:128`, `:143`; the rejected mirror is `verification-attempt-1.json:105,119,133`). r16 re-ran only the census selftest (`corpus/lessons/round-16.md:20`); nothing at r14/r15/r16 re-ran these three. The counts carry to 5fa6017 **because the blobs are byte-identical** (table above), not because anyone ran them at 5fa6017 — see F7.

| suite | recorded stdout tail | rc | R9 share | internal | cite |
|---|---|---|---|---|---|
| souji-verify | `selftest: 40 checks, 0 failed` | 0 | 16 | 24 | `census/round-13/verification.json:113` |
| souji-vault-verify | `selftest: 51 checks, 0 failed` | 0 | 16 | 35 | `census/round-13/verification.json:128` |
| souji-quarantine | `selftest: 91 checks, 0 failed` | 0 | 28 | 63 | `census/round-13/verification.json:143` |
| souji-census (C1) | `selftest: 38 checks, 0 failed` | 0 | 0 | 38 | `census/round-16/c1-matrix-final.json:155-156`; `corpus/lessons/round-16.md:20` |
| r13-quarantine-bounds | `SUMMARY total=5 failed=0 hung=0` | 0 | — | 5 | `census/round-13/verification.json:107` (name `:97`) |
| r15-census-config | `SUMMARY total=20 failed=0` | 0 | — | 20 | `census/round-16/c1-matrix-final.json:65` (changed arm); `corpus/lessons/round-16.md:20`; ids `tests/fixtures/r15-census-config.py:128-149` |
| r14-census-boundary | `SUMMARY total=12 failed=0` | 0 | — | 12 | `census/round-16/c1-matrix-final.json:8`; ids `tests/fixtures/r14-census-boundary.py:45-57` |

Summary sentence in the r13 lesson: "40/51/91/36 checks, zero failures" — `corpus/lessons/round-13.md:158`.
Arithmetic and selftest spans: `.ufo/waves/round-13/w1/CertProtocol.md:55-57` (verify 18 `st_case` + 3 `st_status` + H6 + H1/H5 + R9 16; vault 21 + 2 + 9 explicit + 3 audits + R9 16). Quarantine's 63 internal = 50 `st_check` sites + 12 `st_flow` rc checks (each `st_flow` calls `st_check "$id rc"`, `tools/souji-quarantine.sh:1343-1351`) + 1 `st_ok` (H2). **Do not use `CertProtocol.md:58`** — it records `selftest: 79 checks` for quarantine, which contradicts its own recorded 91 (F8).

### 2.1 Per-case identity at 5fa6017 (the invariant, not the total)

Counts move when jj cases are added; these id histograms (parsed from the recorded stdout) are what "plain-repo unchanged" should be checked against. `R9xN` is the shared runner's own PASS lines.

- verify — `F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 E1 E2 E3 E4 E5 E6 E7 E8 H2 H3 H4 H6 H1 H5` + `R9x16`, plus `ROUND9\t16\t0`.
- vault — `F1 F2 F3 F4 F5 F7 F8 F9 F10 V1 V2 V3 V4 V5 V6 V9 V12 V20 V10b V11b V13 V14 V15 V16 V17 V18 V19 V21 V22 V23 H4 H5 H1 H2 H3` + `R9x16`, plus `ROUND9\t16\t0`.
- quarantine — `G1x3 D1x5 D2x2 D3x4 N1x4 N2x2 N3x3 N4x3 P1x8 P2x4 P3x5 SKIP1x2 L1x3 A1x5 U1 U2 U3 U4 U5 H1 H2 H3x3` + `R9x28`, plus `ROUND9\t28\t0`.

Case-list anchors: verify `:1232-1249` (`st_case`), `:1251-1253` (`st_status`), `:1259` (H6 re-exec), `:1267` (H1/H5 audit call, def `:1206`), `:1270-1278` (R9), `:1281` (summary). Vault `:1451-1470` (`st_case`), `:1513-1534` (V15–V18), `:1570-1571` (`st_status`), `:1576-1583` (R9), `:1587` (summary). Quarantine `:1412-1622` (cases `:1431-1586`, audit `:1588-1607`, R9 `:1610`, summary `:1621`).

## 3. Coverage map: the 16 sites C3 names, live vs dead

Each tool ships a base engine and then an inlined "S18 shared hardening" layer that **redefines the same function names later in the same file**; bash takes the last definition, so the earlier body is unreachable. This is stated in the tool itself: "S17 receipt engine … with the S18 shared hardening layer inlined after it … Renames: base evaluate_path -> s18_evaluate_path, which the guard's evaluate_path wrapper delegates to" (`tools/souji-verify.sh:480-486`; base `s18_evaluate_path` at `:403`, guard wrapper at `:829-848`). Verdict: **10 live, 6 dead.**

| tool | site (5fa6017) | what it is | status | exercised by |
|---|---|---|---|---|
| verify | `:234` | base `try_pushed` unpushed-touching | **dead** — base `try_pushed :219`, guard `try_pushed :655` wins | nothing |
| verify | `:321` | `evaluate_repo_root` unpushed count | live (never redefined) | F3 |
| verify | `:351` | base `evaluate_worktree` `--not --all` | **dead** — base `:333`, guard `:1004` wins | nothing |
| verify | `:671` | guard `try_pushed` unpushed-touching | live | F1, F9 |
| verify | `:809-813` | `s18_evaluate_worktree_one` durable roots | live | F4, E3 |
| verify | `:952` | `second_check` head-history | **dead** — inside `if [ "$S18_KIND" = quarantine ]` (`:850-958`); `S18_KIND=verify` at `:487` | nothing |
| vault | `:412` | base `try_pushed` | **dead** — base `:400`, guard `:843` wins | nothing |
| vault | `:487` | `evaluate_repo_root` | live | F3 |
| vault | `:517` | base `evaluate_worktree` `--not --all` | **dead** — base `:499`, guard `:1192` wins | nothing |
| vault | `:859` | guard `try_pushed` | live | F1, F9 |
| vault | `:997-1001` | `s18_evaluate_worktree_one` durable roots | live | F4, E3 |
| vault | `:1140` | `second_check` head-history | **dead** — inside `:1038-1146`; `S18_KIND=vault` at `:677` | nothing |
| quarantine | `:299` | `s18_second_check`, pushed class | live (`:262`, single definition) | P1, L1 |
| quarantine | `:931` | `try_pushed` | live (`:916`, single definition) | D1, D3, P1, L1 |
| quarantine | `:1069-1073` | `s18_evaluate_worktree_one` durable roots | live (`:1049`) | SKIP1 (wt-inside: registration with dir absent) |
| quarantine | `:1251` | `second_check` wrapper head-history | live — `:1230` inside `:1110-1257` with `S18_KIND=quarantine` (`:664`) | P1, L1 |

Flow→site mapping is static inference from the fixture builders (`tools/souji-verify.sh:1097-1170`, `tools/souji-quarantine.sh:1354-1409`) and the case list; I did not execute the suites.

Two consequences:
1. Patching `:234/:351/:952` (verify) or `:412/:517/:1140` (vault) changes no behavior. Any diff that touches only those sites satisfies "plain repos byte-identical" trivially while (a)/(b) remain unfixed.
2. Every fixture above is plain: heads live in `refs/heads`/`refs/remotes` and no commit is held only by a non-durable namespace, so **all ten live sites pass identically before and after C3**. The counts 40/51/91 can be green with zero of the new semantics implemented.

## 4. Findings

### F1 — HIGH: 6 of the 16 C3 sites are dead code; the live set is unlabelled
Evidence in §3. The base engine is superseded by the inlined guard (`tools/souji-verify.sh:480-486`, `:850`/`S18_KIND=verify:487`; `tools/souji-vault-verify.sh:1038`/`S18_KIND=vault:677`). No test can distinguish "patched the live copy" from "patched the dead copy", because the verdicts are produced by the live copy and the fixture shape is unchanged.
Smallest fix: edit only the ten live sites; in the same change delete the six superseded bodies (or annotate each with `# superseded by <fn>:<line>`), and add the falsifier cases in F2/F3 so the live patch is the only way to turn them green. A grep for the two revset spellings after the change should return only live sites + header prose.

### F2 — HIGH: no case anywhere exercises unpushed-touching-target — C3(b)'s core clause is unmeasured
The r6 guard ("a later local-only commit on the file was still certified SAFE(pushed) by ancestry alone", `tools/souji-verify.sh:229-236`) refuses a pushed receipt when an unpushed commit touches the path. No selftest fixture creates that shape: verify's local-only commit `c3` adds `local/f2.txt` and `keep/f6.txt` while the pushed target is `keep/f1.txt` (`tools/souji-verify.sh:1114-1124`); quarantine's `c2` adds `local/unpushed.txt` (`tools/souji-quarantine.sh:1375-1377`); runner-27's C2a uses a local-only *introduction*, not a pushed target with a later local edit. So extending the guard to keep heads (`--glob=refs/jj/keep/*`) cannot be observed by 40/51/91 or by runner-27.
Smallest fix (one case per tool, or one shared R9 case): commit `keep/x.txt` pushed to `refs/remotes/origin/master`; then create a second commit editing `keep/x.txt` reachable only from `refs/jj/keep/k` (and none from branches/remotes); expect `NOT-SAFE` with `unpushed-commits-touching`/`jj-keep-unpushed`, while the branch-only control (same commit on a branch) already refuses — and a same-shape control where the extra commit touches a *different* path stays `SAFE(pushed)`.

### F3 — HIGH: no case pins the durable-namespace restriction — C3(a) is unmeasured
The live roots lists are `for-each-ref --format='%(objectname)'` over **all** namespaces (`verify:809`, `vault:997`, `quarantine:1069`). A registration whose head is absent but reachable only from `refs/jj/keep/*` is therefore excluded from the revset → `unique=0` → `SAFE(metadata-prune)` at 5fa6017. That is exactly the defect C3(a) claims to close, and no fixture contains `refs/jj` or `refs/stash` (F4/E3/SKIP1 all resolve through `refs/heads`/`refs/remotes`).
Note on the HEAD half of (a): the live lists never include HEAD (`for-each-ref` cannot), so "never HEAD" is already true live; `--not --all` (which does include HEAD) exists only in the dead `:351/:517`. A claim sentence that presents HEAD-exclusion as a live behaviour change overstates the diff.
Smallest fix: add one registration case per tool (or one in R9) where the head is reachable only from `refs/jj/keep/k` → expect `NOT-SAFE` (metadata-prune withheld); a second variant reachable only from `refs/stash`; positive control reachable from `refs/heads` → `SAFE(metadata-prune)`.

### F4 — MEDIUM: the `--glob` must precede `--not`, or it is read as an exclusion
`--not` flips the polarity of every following revision until the next `--not`. `--branches --not --remotes --glob='refs/jj/keep/*'` therefore **excludes** keep heads — the opposite of (b) — and is silent (same count as today). The in-progress vault helper gets this right by prepending the glob (`git log --format=%H --glob='refs/jj/keep/*' "$@"` where `$@` starts `--branches --not --remotes`, and the call site `--branches --glob='refs/jj/keep/*' --not --remotes`): current `git diff` of `tools/souji-vault-verify.sh`. Every remaining site must be audited for placement, and the F2 case must assert the *refusal* direction, not merely a changed count.
Smallest fix: use one spelling everywhere — `git log --format=%H <sep> --branches --glob='refs/jj/keep/*' --not --remotes --oneline -- "$target"` — and add a static selftest audit line asserting no `--not` appears before `--glob=refs/jj/keep` in `$SELF` (same pattern as the existing H1 source audit, def `tools/souji-verify.sh:1206`, called `:1267`).

### F5 — MEDIUM: totals are not identity; the registry pins no id set
`SKILL.md:137,138,140` explicitly say "none; no pinned complete id set". If C3 adds jj cases, 40/51/91 is expected to grow, and nothing in any gate detects a *deleted* legacy case as long as the tail count is patched. Check per-id (§2.1), and if C3 adds cases, add the id set to the registry row (the D6 pattern used by `r12-maintenance-guard`, `SKILL.md:141`).
Smallest fix: `grep -c` is insufficient; diff the `PASS <id>` lines against the recorded sets in §2.1 and require the new set to be a superset.

### F6 — MEDIUM: "plain repos byte-identical" is cheap to prove and should be measured, not asserted
All three suites build plain fixtures, so old-vs-new **full stdout** diff is a direct test of the claim (and covers the "no second git call when `refs/jj/keep/` is absent" fast path the vault helper introduces at `git diff` lines `jj_keep_unpushed`/`for-each-ref … refs/jj/keep/`). Commands are §1.1 plus `diff <(old) <(new)` per suite; expect the legacy id lines identical and only additions. `tests/runner-27.sh` (30 `emit_case` sites, C1–C17, includes `F5 unpushed-branch`, `C3` repo-root unpushed/dirty, `C13 --selftest ×2`) is the strongest external control for verify; it must be run with `--out /var/tmp/...`.
Smallest fix: land the old-bytes capture as a `--selftest` comparison script or as a wave artifact; do not accept a narrative "byte-identical" (r16 accepted exactly that class of claim once, per `corpus/lessons/round-16-verifier-spotcheck.md:41`).

### F7 — LOW: there is no committed execution of these three suites after r13
`census/round-13/verification.json` is the only record; rounds 14–16 contain no `*-selftest` entry for verify/vault-verify/quarantine (`corpus/lessons/round-16.md:20` re-ran census only). The expected counts at 5fa6017 are therefore inherited from blob identity (verified here by sha256), not from a run at that rev.
Smallest fix: record one `--selftest` stdout per tool, with `git rev-parse HEAD` and the file sha256, in the r17 evidence directory; that converts F7 and the F6 diff into a replayable record.

### F8 — LOW: `CertProtocol.md:58` state is stale for quarantine (79 vs 91)
`.ufo/waves/round-13/w1/CertProtocol.md:58` claims `selftest: 79 checks` / fallback 77 for quarantine; the recorded run is 91 (and verify/vault "38 if R9 locale SKIP"/49 fallbacks are not observed either). Use `census/round-13/verification.json:143` and `corpus/lessons/round-13.md:158`.
Smallest fix: correct the table or mark it superseded, so the next wave does not treat 79 as the baseline.

### F9 — LOW: C3(e)'s p6repo/.git stub is absent and untracked at 5fa6017 — it leaves no diff to review
`tests/vault/vadv54-run/p/p6repo/` contains only `inner/` and `one.txt`; `.git` does not exist (`stat` ENOENT) and was never tracked (`git ls-files --error-unmatch` fails; introduced with the directory at `48a64d8`). No committed script runs vadv54 — only historical `tests/results/vadv-*.json` reference `p6repo` (e.g. `tests/results/vadv-54.json:27`). So (e) can only be verified as an absence (`test ! -e …/p6repo/.git`) after the lane's jj runs, and a replayed historical result would no longer be byte-identical if the stub were reintroduced.
Smallest fix: state (e) as a worktree-hygiene check with the exact `test ! -e` line; do not cite it as changed artifact bytes.

### F10 — INFO: C3's counting command does not exist at 5fa6017
`census/round-17/run-matrix.py` and `tests/fixtures/r17-census-hygiene.py` are absent from the rev; `census/round-17/` was untracked at probe (`run-matrix.py` 10480 B, `transcript-manifest.py` 5402 B, created 13:34–13:36 by sibling seats). The baseline that *is* runnable from 5fa6017 is `census/round-16/run-matrix.py` over the current fixtures (`--changed WORKTREE`, fresh output path). For C3 this is harmless; for C1 it means "before" must be defined as the r16 runner at 5fa6017 plus fixture bytes at 5fa6017, not the r17 paths.

## 5. Residual risk and verification gaps

- No suite was executed (assignment: "No execution"). The live/dead mapping, the flow→site table and the plain-fixture argument are static reads of 5fa6017 bytes; they are falsifiable in one command each (§1, §1.1) and should be treated as a checklist, not a verdict.
- Line numbers are blob-relative, and the worktree moved under this seat: both `tools/souji-vault-verify.sh` and `tools/souji-verify.sh` carried in-flight C3 edits by the end of the probe (hashes in the caveat). Every "before" run must come from `git show 5fa6017:`; every "after" run must name the new sha256.
- The three suites are **probes**, not gates: `SKILL.md:137,138,140` pin no expected id set, and exit 1 conflates a real selftest failure with setup debt. A red → investigate; a green does not certify the jj edge class.
- R9 is a shared dependency (`tools/souji-round9-selftest.sh`, sha256 `dd7c636e…`): any edit to it changes all three totals at once (16/16/28), which is the cheapest place to add a shared jj case and also the easiest way to muddy before/after if not declared.
- If C3 adds cases, the "byte-identical plain repo" check must compare per-id lines (§2.1), not totals, or the claim becomes unfalsifiable.

## 6. Commands actually run (read-only except the disclosed reset; no lane writes besides this report)

```sh
git log --oneline -1; git rev-parse HEAD                      # 5fa6017ddcae…
for f in tools/souji-verify.sh tools/souji-vault-verify.sh tools/souji-quarantine.sh tools/souji-round9-selftest.sh; do
  printf '%s head=%s worktree=%s\n' "$f" "$(git show 5fa6017:$f | sha256sum | cut -d' ' -f1)" "$(sha256sum "$f" | cut -d' ' -f1)"; done
git show 5fa6017:tools/souji-census.sh | sha256sum; git show 5fa6017:tools/souji-census.sh | wc -l
  # 64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c / 1877  (matches round-16 record)
python3 - <<'EOF'  # parse census/round-13/verification.json and print per-suite rc/PASS/FAIL/tail
…  # → 40/0 rc0, 51/0 rc0, 91/0 rc0, ROUND9 16/16/28; id histograms of §2.1
    # (the same record holds census 36/0 rc0 from r13; r16's census is 38 — see §2)
EOF
python3 - <<'EOF'  # parse census/round-16/c1-matrix-final.json arms
…  # changed: r15-config 20/0 rc0, r14-namespace 12/0 rc0, selftest 38/0 rc0
EOF
grep -n '^try_pushed()\|^evaluate_worktree()\|^evaluate_repo_root()\|^s18_evaluate_worktree_one()\|^second_check()' tools/*.sh
grep -n 'S18_KIND' tools/souji-{verify,vault-verify,quarantine}.sh
grep -n 'not --all\|for-each-ref' tools/souji-{verify,vault-verify,quarantine}.sh
git diff --stat -- tools/; git diff -- tools/souji-vault-verify.sh   # at 13:47: vault M, +31 lines, helper only
stat -c '%F %s %n' tests/vault/vadv54-run/p/p6repo/.git            # ENOENT
git ls-files --error-unmatch tests/vault/vadv54-run/p/p6repo/.git   # path not tracked
ls -la .ufo/waves/round-17/ census/round-17/                         # report dir present; round-17 untracked
```

Not run, deliberately: any `--selftest`, the r13/r15/r14 fixtures, `census/round-16/run-matrix.py`, `tests/runner-27.sh`, and every other git write. Probe rule compliance is otherwise intact: exact named files only, no recursive search over the lane/fleet root, `census/operator-sweep-20261019/` never opened, no credentials read. The one exception is the `git reset -q -- .` disclosed at the top.
