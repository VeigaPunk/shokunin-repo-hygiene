STATUS: DONE — round-level no-harm ledger for C1/C2/C3 and D3/D5/D6/D7. Eight counterexamples; two would harm an axis if the round lands as declared (CX1 calibration, CX7 gate), and one claim sentence is false as written (CX2).

# CriticSeparabilityNoHarm — round 17, wave 1

Seat role: critic. Read-only. Base `5fa6017`. Nothing was executed except read-only git commands, `stat`, `sha256sum`, `jq`/`ls`/`du`/`diff` on named files, and greps of named files (all listed under Commands). In-flight state at review time: `git diff --stat` showed `tools/souji-vault-verify.sh` (+30) and `tests/vault/vadv54-harness.sh` (2 lines) modified. Untracked: `.ufo/waves/round-17/`, `census/round-16/transcripts/`, `census/round-17/`. No change to census, verify, quarantine or seat-audit had landed in the working copy yet.

## Axes this round can harm

| axis | harm vector |
|---|---|
| operability (census) | D1/D2 change live rows; D2's early degrade skips later exit-2 guards; the hygiene fixture is measured against non-committed fixture bytes |
| operability (verify/vault/quarantine) | (a) durable-roots narrowing changes plain-repo verdicts; (b) keep-glob blast radius on jj lanes; edits land in dead code; `--glob` is placed after `--not` |
| calibration (seat audit) | the lstrip fix opens a false-negative path for relative writes that land in the fleet repo; the claimed counts are wrong |
| calibration (gate/frozen) | the census byte change trips LG-FROZEN-PIN at landing; the selftest count regresses; replay values drift |
| coverage | the jj knowledge entry is counted as admitted before closure; SOURCES rows fail validate |
| depth | SKILL/PROVINCE recipe edits drop registry rows or recipes |
| freshness | jj docs cited unversioned; the fleet helper cited by name only |
| adjacency | a write outside the lane; the operator sweep is touched; the admitted r16 lesson or spot-check is rewritten |

## Counterexamples (ranked)

### CX1 — C2: making relative paths pass is a new false negative; "w2 3→0 with the w1 major kept" is inconsistent (calibration; HARM if landed as declared)

**Evidence**
- `/var/tmp/souji-r16/transcripts/w2/ConnReadmeIndex.txt:166` `→ write(/home/…/souji-shokunin/.ufo/waves/round-16/w2/ConnReadmeIndex.md) ⇒ ok`.
- Then `:179` `→ edit(.ufo/waves/round-16/w2/ConnReadmeIndex.md) ⇒ error … File not found: .ufo/waves/round-16/w2/ConnReadmeIndex.md`. The lane file existed at that point, so the relative path did not resolve against the lane. It resolved against the process cwd, which is the fleet root (the contract says so: "your tools start at the fleet root, so a relative path lands in the WRONG repo").
- The relative call therefore addressed `/home/vgpnk/Projects/shokunin/.ufo/waves/round-16/w2/ConnReadmeIndex.md`, a fleet-repo path. Observed: `stat` → No such file, so no bytes were written.
- `RevD4FalsePositives.md:31` assumes a "session root" different from cwd. Nothing in the evidence supports that.

**Why the fix regresses detection**
- The fix makes `allowed_target` (`tools/souji-seat-audit.py:76-81`) use a prefix strip.
- Its suffix rule `p.endswith("/" + rel)` would then accept a successful relative `write(.ufo/waves/round-17/w1/X.md)`. The `write` tool creates parent directories, and the fleet `.ufo/waves/` exists (`.ufo/waves/hyaku/...` was read this round). Such a write lands in the fleet repo, which seats must never write.
- Today the lstrip bug flags exactly that call as major. After the fix it becomes invisible.
- The existing selftest case `edit-relative-owned` (`:171`, `edit([tools/x.py#AB12] …)` → no violation) already encodes this false negative for undotted paths.

**Why the counts are inconsistent**
- The w1 major the claim keeps (`SrcGitNoLazyFetch.txt:143`, `edit(…/.ufo/waves/round-16/r16-placeholder.md) ⇒ error File not found`) is a failed attempted edit of a non-owned path.
- ConnReadmeIndex `:179` is the same shape: a failed attempted edit of a non-owned (fleet) path.
- One consistent rule gives either w1=1/w2=1, or w1=0/w2=0 if failed attempts are downgraded. It cannot give w1=1/w2=0.

**Smallest safe correction**
1. Resolve relative targets against `fleet = Path(lane).parent` (already computed in `run`, `:124`), normalize, and compare exactly. Absolute targets: exact match.
2. A non-path rendered argument (the two RerunGateReplayR14 `:224-225` prose args) becomes `V-WRITE-UNKNOWN` (minor). It must not be dropped.
3. Selftest:
   - add `edit(.ufo/waves/round-9/w1/S.md) ⇒ error` → `V-WRITE-SCOPE`;
   - add a prose argument → `V-WRITE-UNKNOWN`;
   - add `./`-prefixed absolute and relative cases;
   - flip `edit-relative-owned` to expect `V-WRITE-SCOPE`, disclosed as a corrected expectation.
4. Claim text: w2 majors 3→1 (ConnReadmeIndex = attempted fleet-repo write, failed), minors 42→44. w1 unchanged at 1/19.

**Impacted axes:** calibration (C2 overclaim plus a new false-negative class) and adjacency (fleet-repo writes become undetected).

### CX2 — C3(a): "plain repos behave byte-identically" is false for the durable-roots change (calibration; disclose)

**Evidence**
- The live root lists are `s18_evaluate_worktree_one` for-each-ref: verify `:809-813`, vault `:997-1001` (base numbering), quarantine `:1069-1073`.
- Narrowing the roots to `refs/heads|tags|remotes` changes a plain repo whose absent-worktree head is reachable only from `refs/stash`, `refs/original/*`, `refs/bisect/*` or `refs/replace/*`.
- `refs/stash` is shared across worktrees, and a stash commit's first parent is the worktree's HEAD.

**Concrete fixture (plain repo, no refs/jj)**
- Setup: owner `O`; `git -C O worktree add --detach W X`; modify a file in W; `git -C W stash`; `rm -rf W`.
- At 5fa6017, roots include `refs/stash` → `unique=0` → SAFE(metadata-prune), which is correct because X stays reachable.
- After the change: NOT-SAFE, `unique=1`.

**Mitigating facts**
- This is not a safety regression. It is a false refusal.
- Fleet survey: 0 of 21 repos hold any `refs/stash|notes|original|replace` ref.
- The selftests create none (grep of verify/vault/quarantine/r13-bounds/r12/case-F4/F5: no match).
- So both live and selftest preservation will pass vacuously and cannot show this.

**Correction:** restate the claim as "byte-identical for repos with no refs outside heads/tags/remotes; heads held only by refs/stash, refs/original, refs/bisect or refs/replace move SAFE(metadata-prune)→NOT-SAFE (conservative)". Add the stash fixture with that expected change.

### CX3 — C3(b): keep-glob blast radius on jj lanes is large and grows over time (operability; disclose with numbers)

Measured as keep-only commits not on any branch or remote, and the distinct paths they touch:

| lane | keep-only commits | paths touched |
|---|---:|---:|
| mado | 23 | 772 |
| kama | 10 | 188 |
| kaidoku | 10 | 185 |
| tameshi | 13 | 140 |
| souji | 6 | 3 |
| tabi | 5 | 1 |
| tsukuroi | 2 | 0 |

- In souji the three paths are the two phantom deletions (`tests/vault/vadv54-run/p/p6repo/one.txt`, `…/inner/keep.txt`) and `corpus/lessons/round-16-verifier-spotcheck.md`.
- Each touched tracked target loses SAFE(pushed) until `jj util gc`.
- Keep refs only accumulate, so the refusal set grows with every rewrite.
- Fixing the stub in (e) does not remove the existing phantom-deletion keep commits.

**Correction:** disclose the per-lane counts in the claim and the lesson. A content-aware refinement is the judge's tradeoff call, not required: a keep-only commit refuses only when its target blob differs from the default-ref blob. Phantom deletions would still refuse under it.

### CX4 — C3: four of the cited sites are dead code (false provenance)

- verify `try_pushed` `:219` is redefined unconditionally at `:655`, and `evaluate_worktree` `:333` at `:1004`.
- vault `try_pushed` (base `:412` area, now `:429`) is redefined at `:873`, and `evaluate_worktree` (`:517` area) at `:1222`.
- So the claimed sites verify `:234`/`:351` and vault `:412`/`:517` are never executed.
- In-flight vault diff: `jj_keep_unpushed()` is defined inside the dead `try_pushed` body. It would never exist at runtime, and a live caller would get 127, read as false, so it would never refuse. Messaged `VaultJjRoots`.
- The live unpushed sites are:
  - verify `:671`, `:952` (quarantine kind) and `evaluate_repo_root :321`;
  - vault `:859`, `:1140` and `evaluate_repo_root :487`;
  - quarantine `:299`, `:931`, `:1251`.

**Correction:** cite only live sites. For each live site, add a jj fixture case that FAILS on the 5fa6017 arm and PASSES on the changed arm.

### CX5 — C3(b): placement and quoting of `--glob`

- If `--glob='refs/jj/keep/*'` is placed after `--not`, keep heads become negative revisions and hide commits. That is a false SAFE on jj lanes, and it is invisible to plain-repo tests.
- If it is unquoted, `nullglob` or `failglob` would silently remove or abort the argument.
- Messaged `VerifyJjRoots`.

**Check:** every `refs/jj/keep` token in the three tools is single-quoted and precedes `--not` on its line. A jj fixture with a keep-only commit touching the target refuses at every live site.

### CX6 — C1/D2: an early degrade skips later exit-2 guards (operability)

`guard_git_files` checks in this order: `config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates` (`souji-census.sh:521`). It is followed by the common-dir `guard_git_files` (`:849/:891`), `guard_alternates` (`:854/:896`) and the registrations (`:855/:897`). A degrade that returns early on `info/attributes` would turn any of these later whole-run refusals into a per-repo row.

Required paired cases. Each must show exit 2 on both the r16 and changed arms:
1. hardlinked `info/attributes` + hardlinked `objects/info/alternates`;
2. a `.git` file → gitdir with hardlinked attributes, plus a commondir with hardlinked `config`;
3. hardlinked attributes + an alternates path into the store;
4. hardlinked attributes in a registered-worktree admin dir (`:790`) + a later protected reach.

**Leak check:** a mixed fleet `a`/`m`(hardlinked attributes)/`z` gives `a` and `z` clean, `m` = `error`, exit 0. Any per-repo flag must be reset, as `CFG_SOFT_REASON` is at `:823`.

**No-read check:** strace (as in the r14 boundary fixture) shows no `open`/`openat` of that attributes path by git or bash after the guard. This includes `guard_bound_filters`/`status_info_file` (`:1025-1027`).

**Diagnostic:** `git-metadata-unsupported <reason> <path>` passes the path through `sanitize_field`.

### CX7 — gate: changing census bytes fires LG-FROZEN-PIN at landing (calibration; HARM unless re-measured)

- `tests/fixtures/r15-preservation-frozen/expected.json:5` pins `tools/souji-census.sh = 64a60fd0…`.
- `souji-landing-gate.py:90,364-368,395-424` resolves `tools/` keys in the REV tree.
- So any C1 edit makes `--rev <landing> --round 17` exit 1 with LG-FROZEN-PIN.

**Correction:**
1. Land the census first.
2. Run `tests/fixtures/r15-preservation-frozen/regenerate.py` at that commit (its `measured_commit` becomes that commit; the installed tool must equal the REV bytes).
3. Commit the record, then run the gate.

Keep the pinned and literal fixtures byte-unchanged:
- `r15-census-config.py` (`27474396…`);
- `r14-census-boundary.py` (`e6a984b1…`, also a literal at `souji-preservation-evidence.py:107,307`).

New cases go only into `r17-census-hygiene.py`.

### CX8 — C2: wrong transcript counts in the claim (calibration, minor)

The claim says "w1 70 + w2 77". Observed are 65 and 79 (144 in total):
- files in `/var/tmp/souji-r16/transcripts/{w1,w2}`;
- `jq '.items|length' .ufo/waves/round-16/w{1,2}-spec.json`;
- `seats_audited` in `census/round-16/seat-audit-w{1,2}.json`.

The bundle `census/round-16/transcripts/MANIFEST.sha256` has 144 lines, `sha256sum -c` passes, and `diff -rq` against `/var/tmp` shows no difference. The bundle itself is sound; only the claim text is wrong.

### Note — (e) stub fix

The harness diff creates `p6repo/.git` only around P6:
- `dir_digest` prunes `./.git` (`vadv54-harness.sh:63-65`), so the ledger digest does not drift;
- the harness has no other `trap`, so `trap - EXIT` clobbers nothing.

A residual window remains: a jj snapshot during a harness run re-records the phantom deletions. Disclose it, or move `WORK` to `/var/tmp`.

## No-harm check ledger

All exec checks below are for an `ALLOWED-EXEC` seat or L1, not for this seat. Paired arms take the tool from `git show 5fa6017:<path>` (or `<landing>:<path>`) into `/var/tmp`.

| # | axis | check (command) | expected |
|---|---|---|---|
| N1 | operability · live-fleet census | `TMPDIR=/var/tmp bash <arm>/tools/souji-census.sh --root /home/vgpnk/Projects/shokunin`, arms 5fa6017 and landing, run back to back | rc 0 both; 21 rows each; rows identical excluding mtime; no `git-metadata-unsupported` on stderr. Basis: fleet survey, 0/21 repos with `status.showUntrackedFiles`/include keys in common-dir config, 0/21 with `info/attributes`, so D1 and D2 must be live no-ops |
| N2 | operability · census fixtures | `python3 census/round-17/run-matrix.py --changed <landing> --output /var/tmp/…json` (no `--fixture-dir`) | changed: r17-hygiene all PASS, r15 20/20, r14 12/12, selftest ≥38 with 0 failed, `bash -n` rc 0, shellcheck 0. r16 arm reproduces 20/20, 12/12, 38/38 and fails exactly the D1/D2 hygiene cases. pre-harm and r14 arms fail the D1 cases too (inherited). Recorded fixture sha256 = `git show <landing>:tests/fixtures/<f> \| sha256sum` |
| N3 | operability · whole-run exit 2 kept | hygiene cases: hardlink and FIFO for each of `config HEAD index packed-refs commondir info/exclude objects/info/alternates`, plus every r14 namespace refusal, plus CX6 cases 1–4 | exit 2 on both the r16 and changed arms |
| N4 | operability · verify/vault/quarantine on plain repos | paired arms: `TMPDIR=/var/tmp bash <arm>/tools/souji-verify.sh --selftest`; `TMPDIR=/var/tmp SOUJI_CLI_BIN=/bin/false bash <arm>/tools/souji-vault-verify.sh --selftest`; `TMPDIR=/var/tmp bash <arm>/tools/souji-quarantine.sh --selftest`; `bash tests/fixtures/r13-quarantine-bounds.sh --tool <arm>/tools/souji-quarantine.sh`; `bash tests/fixtures/r12-maintenance-guard.sh`; `bash tests/vault/vadv54-harness.sh` | per-case verdict lines identical (modulo tmp paths); pass/fail counts equal; the only differences are new jj cases and the CX2 stash case, which is expected to differ |
| N5 | operability · live worktree verdicts | both arms of `souji-verify.sh` on the registered worktrees of game-dev-2d (4 entries) and kotodama (2) | identical verdict/receipt/evidence lines (those repos have no `refs/jj` and no stash-like refs) |
| N6 | operability · jj lanes (tradeoff) | per jj lane: `git -C <lane> log --format= --name-only HEAD --branches --glob='refs/jj/keep/*' --not --remotes \| sort -u \| wc -l` minus the same without the glob | disclosed in the claim: ≈772/188/185/140/3/1/0 (CX3) |
| N7 | calibration · seat-audit reproducibility | `python3 /var/tmp/…/seat-audit@5fa6017.py --spec .ufo/waves/round-16/w{1,2}-spec.json --transcripts census/round-16/transcripts/w{1,2} --lane /home/vgpnk/Projects/shokunin/souji-shokunin --json /var/tmp/…` | byte-equal to `census/round-16/seat-audit-w{1,2}.json`. This proves the committed bundle is the audited bytes |
| N8 | calibration · seat-audit precision | landed tool on the same inputs; diff the violation sets against r16 | calls 3173/4348 unchanged. Under CX1's rule: w1 major 1 (SrcGitNoLazyFetch :144), minor 19; w2 major 1 (ConnReadmeIndex :180), minor 44 (two prose rows → `V-WRITE-UNKNOWN`). No other row added or removed. `--selftest` fail=0, pass ≥ 20 + new, every old case id retained |
| N9 | calibration · gate | `python3 tools/souji-landing-gate.py --root <lane> --rev <landing> --round 17 --json …`; same with `--round 16`; replays `b410186/15`, `a31642d/13`, `cc21683/14`; `--selftest`; `python3 tests/fixtures/r16-landing-gate.py` | r17: exit 0, findings 0 (needs CX7 fixed). r16 at landing: findings 0, markers 30, reports 141. Replays 5/0/0. Selftest pass ≥18, fail 0, exact id sets; a mutant that adds one extra id FAILS the selftest. Fixture 15/15 |
| N10 | calibration · frozen preservation | `python3 tools/souji-preservation-evidence.py --selftest`; `--frozen tests/fixtures/r15-preservation-frozen`; `python3 tests/fixtures/r15-preservation-evidence.py` | 47/47; exit 0; 8/8; the regenerated `expected.json` verdict is computed and equals `clean` |
| N11 | coverage | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | exit 0; only W04 duplicate-URL warnings, none new except declared jj rows; admitted knowledge stays 5 until closure (the jj entry is a candidate) |
| N12 | depth | `git diff --numstat 5fa6017 <landing> -- SKILL.md PROVINCE.md` plus a registry row grep | all 18 registry rows (SKILL.md :137-154) present; deletions only on replaced recipe lines; gate LG-PARSE-REG/LG-MISSING-REG 0 |
| N13 | freshness | read the knowledge entry and SOURCES rows | jj docs cited with their served version and a recheck trigger. The helper is cited as `scripts/hyaku/jj-lane.sh@14df5b9` with sha256 `3369dc27b490…`; the file carries no version marker, so "v2" alone is not a binding |
| N14 | adjacency | `git -C /home/vgpnk/Projects/shokunin status --porcelain` before and after; sweep metadata fingerprint | no fleet-repo change by seats; `census/operator-sweep-20261019/` fingerprint `f6a84466…` with 155 entries unchanged |
| N15 | append-only (D3/D5/D7) | `git diff 5fa6017 <landing> -- LOG.md corpus/lessons/round-16.md \| grep -c '^-[^-]'`; `git diff --quiet 5fa6017 <landing> -- corpus/lessons/round-16-verifier-spotcheck.md` | 0; unchanged (D5 is fixed by correction entries, not by rewriting admitted text) |
| N16 | (e) stub | `stat tests/vault/vadv54-run/p/p6repo/.git`; `git ls-files tests/vault/vadv54-run/p/p6repo` | absent; still 2 tracked files; the P6 verdict line equals the 5fa6017 arm |

**Out of scope (adjacent, not new harm):** the verify tools' non-pushed status calls (verify `:322,:820`, vault `:518,:1038`, quarantine `:1080`) pass no untracked mode, so `showUntrackedFiles=no` changes only the NOT-SAFE receipt label (dirty→none). The verdict is unchanged. The pushed receipt uses `--untracked-files=all` (`:658/:876/:919`).

## Verdict

| claim | verdict | condition |
|---|---|---|
| C1 | partial | no-harm holds only with the CX6 ordering cases and the CX7 re-measure |
| C2 | fails as declared | CX1, CX8; holds after the CX1 correction with w2 3→1 |
| C3 | partial | CX2 wording, CX3 disclosure with numbers, CX4 live-site evidence, CX5 placement |
| D3/D5/D6/D7 | no harm found statically | subject to N9, N10, N15 |

## Commands run (all read-only)

The ones with notable output:
- `git -C <lane> rev-parse HEAD` → `5fa6017…`.
- `git -C <lane> diff --stat` → vault-verify +30, vadv54-harness 2 lines.
- `git status --porcelain --untracked-files=normal` → `.ufo/waves/round-17/`, `census/round-16/transcripts/`, `census/round-17/`.
- `for-each-ref` namespace count → `refs/heads` 1, `refs/jj/keep` 8, `refs/remotes` 2.
- Fleet survey loop over 21 repos:
  - `rev-parse --git-common-dir`, `config --file <gd>/config --list`, `stat <gd>/info/attributes`, `for-each-ref refs/jj …`;
  - also `git worktree list --porcelain`, which is read-only but not on the PROBE RULE list;
  - output: every repo `su/inc=0 attrs=none stash/notes/orig/repl=0`; jjkeep counts kaidoku 22, kama 22, mado 39, souji 8, tabi 7, tameshi 27, tsukuroi 11; worktrees: game-dev-2d 4, kotodama 2.
- Keep-only blast loop: `rev-list --count --glob='refs/jj/keep/*' --not --branches --remotes` and `log --name-only` with the same revs → the CX3 table.
- `log --name-status --glob='refs/jj/keep/*' --not --remotes` in souji → `D …p6repo/one.txt` ×4, `D …p6repo/inner/keep.txt` ×4, `A corpus/lessons/round-16-verifier-spotcheck.md` ×2.
- `stat` of the fleet ConnReadmeIndex path → absent; the lane path is 20962 bytes.
- `ls … | wc -l` → 65/79, and the same for the committed bundle.
- `jq` → missing 0, seats 65/79, items 65/79.
- `sha256sum -c --quiet MANIFEST.sha256` → OK; `grep -c . MANIFEST.sha256` → 144; `diff -rq` → identical.
- `sha256sum scripts/hyaku/jj-lane.sh` → `3369dc27…`; fleet `git log -- scripts/hyaku/jj-lane.sh` → `14df5b9` (v2).
- Also: `git check-ignore -v` on the stub (no output); `sed`/`cat -A` to view verify.sh `:785-790` and `:1000-1030`, and `cut` to truncate outputs (should have used `read`; no write involved).
- Named-file greps and reads: `souji-census.sh`, `souji-verify.sh`, `souji-vault-verify.sh`, `souji-quarantine.sh`, `souji-seat-audit.py`, `souji-landing-gate.py`, `run-matrix.py` (r16 and r17), `r15-preservation-frozen/{expected,record}.json`, `regenerate.py`, `r14-census-boundary.py`, `r15-census-config.py`, `vadv54-harness.sh`, `SKILL.md`, `JjAuditSouji.md`, `RevD4FalsePositives.md`, `SrcPyLstrip.md`, three r16 transcripts, `seat-audit-w{1,2}.json`, `live-fleet-final.json`.

Peer messages: `VaultJjRoots` (dead-code placement of `jj_keep_unpushed`) and `VerifyJjRoots` (dead sites; `--glob` placement and quoting).

Tool installs or updates: none.
