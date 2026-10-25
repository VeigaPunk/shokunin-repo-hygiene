author: hyaku closure (non-author integrator, @m_opus)

# Round 17 — non-author closure and verifier spot-check

## Decision

**Status: ok; admitted: true; verdict: admitted.** The report is real and committed, not a marker. All three declared claims verify within their declared scope:

- C1 (operability): re-measured with an independent census probe at both revisions, and its matrix evidence verified.
- C2 (calibration): verified from committed gate evidence. The replay digests bind to the 5fa6017 and 4f48343 auditors, and the selftest case count was confirmed statically.
- C3 (coverage): re-measured with independent keep-ref and plain-repository probes, and its fixture records verified.

No axis is harmed against the round baseline `5fa6017`. The 144 committed seat transcripts contain no credentials, tokens, API keys or private config values (sweep below).

Scope of this admission:

- C1 is not certified no-harm against pre-harm `a31642d`, and the lane does not claim it is. The inherited round-14/16 contractions stay open under L0 `souji | round-16`.
- C2's precision is measured only on the round-16 transcripts the defect came from, plus a lane-written synthetic held-out table. Precision on fresh transcripts is unmeasured, as the lane discloses.
- Five dead wave-2 static reviews were not redone by the lane. This closure's own probes covered the C1 and C3 behaviour. Its read of the quarantine runbook found a defect (R1 below) that the dead `RevQuarantineRunbook` seat would have checked.

Reviewed: before `5fa6017ddcae9f6bd4412df44765f6360cb16294`, after `2cfc6c0b2388367a5ab99d532bc02a2ebddb5984`. References: pre-harm `a31642d`, r14-harm `cc21683`.

All probes ran on `git archive` exports under `/tmp/souji-r17-close/<rev>` and on synthetic repositories under `/var/tmp/souji-r17-close-probe` with an isolated `HOME`. No lane gate was executed, per §Gate standard (Closure consequence). Re-dispatching auxiliary seats was refused by the session job cap (100), so this integrator ran every check itself.

Driver digest (copied from mutable `.ufo/watchdog.log`, lines 493 and 505):
- `2026-10-20T12:43:24-03:00 launch souji round=17 pgid=2966646 driver=hyaku-inline attempt=1`
- `2026-10-20T16:14:05-03:00 complete souji round=17; hyaku-inline attempt=1`

## Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report landed by lane | `git log --format='%an %H' -- .ufo/reports/round-17/souji.md` | `souji-shokunin 0e945371be63e799a95e9f20099d12ec51ca1830` (16:13:26 -03) | ok |
| report after lane tip | lane `2cfc6c0` 16:12:16 -03; report 16:13:26 -03 | | ok |
| cited hashes ancestors | `git cat-file -e <h>^{commit} && git merge-base --is-ancestor <h> refs/heads/master` for ddb7347 d7e648d 4f48343 95519a7 d98065d 2cfc6c0 | all `anc-ok` | ok |
| pushed | `jj-lane.sh state` | `local=remote=2cfc6c0… ahead=0 behind=0 head=detached tracked=0 untracked=1`; `ls-remote origin refs/heads/master` → `2cfc6c0…` | ok |
| no uncommitted round work | `git status --porcelain` | only `?? census/operator-sweep-20261019/`: operator-owned and inherited, unopened by the lane since r13. Its disposition is now L0 `souji \| round-17`. The uncommitted path the driver's verify saw is this one. | ok |
| SHONEN heading | report `## SHONEN` | 4 lines, all `[~]`; `SHONEN.md` unchanged (4 × `[~]`) | ok |
| L0 questions | fleet `23efcab` (author souji-shokunin) | `.ufo/l0-questions.md:66-67` (jj keep refs; operator-sweep disposition) | ok |
| prompt fidelity | Python `difflib`: `templates/round-prompt.md` (LANE/ROUND/FLEET_ROOT substituted) vs `.ufo/prompts/souji-round-17.md` before `## 6.` | 4 diff lines: the `<souji-repo>` working-dir expansion and the `{{AXES}}` expansion. §6 hyaku addendum present. The prompt was committed by souji-shokunin in `5348522`. | ok |
| SCORECARD | `git diff 5fa6017 2cfc6c0 -- SCORECARD.md` | scores coverage 8, calibration 7, operability 8 unchanged; observation prose updated; 3 capability rows; r18 planned | ok |

Conformance defects (status-neutral) are routed as R2–R4 below.

## Credential sweep of the committed r16 transcripts

| check | command | observed |
|---|---|---|
| manifest | `cd census/round-16/transcripts && sha256sum -c --quiet MANIFEST.sha256`; file count | ok; 144 files, 144 manifest lines (w1 65 + w2 79); `MANIFEST.sha256` sha256 `4837d550…` equals the digest bound in both replay records |
| secret scanner | `gitleaks dir --redact -v census/round-16/transcripts` (gitleaks already installed) | `no leaks found` (~2.0 MB) |
| whole round | `gitleaks git --log-opts=5fa6017..2cfc6c0 <lane>` | 6 commits, ~5.2 MB, `no leaks found` |
| patterns | regex over transcripts: `sk-…`, `ghp_`, `github_pat_`, `xox?-`, `AKIA…`, bearer, `api_key=`, `authorization:`, `PRIVATE KEY`, `password=`, `_TOKEN=`, JWT; then emails other than `@shokunin.local`, `user.email/name =`, `signingkey`, `insteadOf`, URL userinfo, `.netrc`, `id_rsa`, `auth.json`, `models.yml` | no secret. The only hits are prose about credential helpers, the tooling-directive word "Passwordless", and `read(/home/vgpnk/.config/git/config) ⇒ ok · 49 lines`. Transcripts render tool calls as truncated argument summaries without output bodies, so no config values are present. |

Verdict: **no harm finding.** The transcripts do expose local path names (`/home/vgpnk/...`, `~/.omp/agent/sessions/<id>` headers), but no values.

## Per-claim re-check

### C1 operability: improved (re-measured by independent probe; matrix evidence verified)

| measurement | command | observed | vs claim |
|---|---|---|---|
| D1 sweep | grep every `status` invocation in `tools/souji-census.sh`@4f48343 (`tools/` identical at 2cfc6c0: `git diff --stat 4f48343 2cfc6c0 -- tools/` touches none) | one live status call, `:1124-1125`, carries `--untracked-files=normal`; 5fa6017 has 0 occurrences | agrees |
| D1 behaviour | synthetic root, repo `a` with `status.showUntrackedFiles=no` plus an untracked file; `bash <rev>/tools/souji-census.sh --root root2` | 5fa6017: `a dirty=0`; 4f48343: `a dirty=1 dirty,…` | agrees |
| D2 hardlink | repo `b` with `.git/info/attributes` hardlinked (nlink 2) beside `a`, `c` | 5fa6017: rc 2, `path-protected: git-metadata-hardlink`, no rows. 4f48343: rc 0, rows `a`, `c` measured, `b … error`, stderr `git-metadata-unsupported git-metadata-hardlink …` | agrees |
| D2 non-regular | same with a FIFO `info/attributes` | 4f48343: rc 0, `b … error`, `git-metadata-unsupported git-metadata-nonregular` | agrees |
| matrix | `jq` over `census/round-17/c1-matrix-4f48343.json` (`changed_rev`=`lane_head`=4f48343, `invalid_suites` []; hygiene fixture sha `8cd53c56…`, r15-config `27474396…` = committed bytes) | r17-hygiene failed/29: r16 14 (R17-01,02,03,04,07,08,09,14,15,16,20,24,26,29), changed 0, pre-harm 21, r14-harm 14. r15-config: 0/0/8/16. r14-namespace: 0/0/10/0. Selftest checks/failed: r16 38/0, changed 49/0. `bash -n` and shellcheck rc 0 on all arms. | agrees |
| live fleet | `jq` over `census/round-17/live-fleet.json` | both arms rc 0, census sha `64a60fd0…`/`006b9823…` = 5fa6017/4f48343 bytes; `rows_identical_excluding_mtime` true; 22 rows **including the header** = 21 repositories | report "22 rows" agrees; SCORECARD "22 repos" off by one (R3) |
| FIFO swap race | lesson `## Residuals` :86, Seat-reported failures :60 | sentinel F3 TOCTOU FIFO swap disclosed as open (r18) | agrees (disclosed) |

No-harm vs `5fa6017`: r15-config and namespace stay 0 failed. D2 replaces a whole-run exit 2 with a per-repository row, which is less contraction. The `ddb7347` empty-file and locale regression (R17-M5) was fixed before the final landing and pinned by R17-27 and R17-28.

### C2 calibration: improved, scoped to the committed r16 corpus (evidence-verified; gate not executed)

| measurement | command | observed | vs claim |
|---|---|---|---|
| auditor binding | `sha256sum <rev>/tools/souji-seat-audit.py` vs the replay record `auditor.sha256` | base record `c9ff355c…` = 5fa6017 bytes; after record `7eff210a…` = 4f48343 = 2cfc6c0 bytes | agrees (`git_rev` is "unbound"; the digest binds it) |
| majors/minors | `jq '.waves[].summary'` over both replay records | base: w1 major 1 (SrcGitNoLazyFetch) minor 19; w2 major 3 (ConnReadmeIndex, RerunGateReplayR14) minor 42. After: w1 1/24; w2 major 1 (ConnReadmeIndex) minor 48. Transcripts 65+79, missing [] | agrees |
| selftest size | static count in `selftest()`: tuple rows `:318-406` plus the two `run()` wiring checks | 2cfc6c0: 64 + 2 = 66; 5fa6017: 19 + 1 = 20. Run evidence: `.ufo/waves/round-17/w1/SeatAuditPrecision.md:44` `SELFTEST pass=66 fail=0` | agrees |
| R17-M1 (r16 closure reason wrong) | read `transcripts/w2/ConnReadmeIndex.txt:180` and `RerunGateReplayR14.txt:225-226`; `round-16-verifier-spotcheck.md:137-139` | `:180` is `edit(.ufo/waves/round-16/w2/ConnReadmeIndex.md) ⇒ error … File not found`, a relative target that the tool resolved against the fleet root, so it was a real out-of-scope attempt (no bytes written). r16 called it a false positive caused by `lstrip`. `:225-226` pass prose as the edit target `⇒ error`, which is consistent with minor `V-WRITE-UNPARSED`. | **agree** with the correction. The lstrip bug existed (S061), but it did not make the row false. |

Note: `V-WRITE-RELATIVE` stays major on `⇒ error` while `V-WRITE-UNPARSED` is minor on `⇒ error`. This is a deliberate asymmetry, stated in Q27.

### C3 coverage: improved (re-measured by independent probe; fixture records verified)

| measurement | command | observed | vs claim |
|---|---|---|---|
| root sites | grep the 3 tools @2cfc6c0 | `for-each-ref --exclude='refs/jj/'` at verify:866, vault:1074, quarantine:1158; remaining `--branches --not --remotes` and `--not --all` sites are the shadowed or branch-based ones the lane discloses | agrees |
| `jj_keep_novel` identity | `awk '/^jj_keep_novel\(\)/,/^}/' \| sha256sum` per tool | `7fc7cc6355593ee8…` in all three | agrees |
| `try_pushed` untouched | diff of the function body, 5fa6017 vs 2cfc6c0 | identical | agrees |
| keep-ref probe (J3-shaped) | bare remote + clone; pushed `f.txt`; novel commit held only by `refs/jj/keep/<id>`; branch reset; `souji-verify.sh f.txt` | 5fa6017: `SAFE pushed`; 4f48343: `NOT-SAFE … jj-keep-novel` | agrees |
| plain-repo identity (J6-shaped) | keep ref removed; `souji-verify.sh` and `souji-vault-verify.sh --fallback` on `f.txt` and an untracked file at both revisions; `cmp` | both byte-identical, rc 0 | agrees |
| fixture records | per-case tally of `census/round-17/jj-receipts-{base5fa6017,4f48343}.txt`; tool digests | base 20 PASS / 13 FAIL (J1, J1-vault, J3, J3-vault, J3-quarantine, J9-file, J9-worktree, J11×3, J12×3) / 2 SKIP (J6×2), `SUMMARY total=33` (= non-skipped); after 35 PASS, `total=35 failed=0 skipped=0`; tool digests = 5fa6017 / 4f48343 bytes | agrees |
| sources and knowledge | count `^\| S[0-9]{3}` and `\| mined \|` rows and `corpus/knowledge/` at 5fa6017 → d98065d | rows 50→63, mined 31→44; knowledge `.md` 6→7 (+ `jj-colocation-receipts.md`) | agrees |
| host jj binary | `jj --version` | 0.45.1-7c41cdeb (= S054 tag commit) | agrees |

### Hygiene checks requested by the dispatcher

- **Phantom-deleted files.** `git ls-tree -r` shows `p6repo/inner/keep.txt` `5fd8799d…` and `p6repo/one.txt` `00508d39…` identical at 5fa6017 and 2cfc6c0. `git log 5fa6017..2cfc6c0 -- p6repo` is empty, so git never committed a deletion. The jj-side `@` was not inspected, because jj may run in the lane only through the helper.
- **Stub quarantine.** `tests/vault/vadv54-run/p/p6repo/.git` is absent. `.ufo/quarantine/round-17/…/dot-git-empty-stub` reads `stat` = `directory|1|0|30073199`, with 0 entries, matching the receipt. It is untracked, not ignored, and invisible to `git status` because the directory is empty.
- **Harness.** `tests/vault/vadv54-harness.sh` creates the stub only around case P6, with an `rmdir` trap.
- **SKILL `git add` recipe.** The old line ("`git -C <repo> add -- <approved paths>` then … commit") is replaced by a three-way rule:
  - souji lane: helper only;
  - jj repo: the owning lane's helper naming both paths, plus a `cat-file` post-check;
  - plain repo: guarded git naming both paths.

  The knowledge entry §5 agrees. `QUALITY.md` Q7 still says every lane commit uses `commit -- <paths>` (R4).

## Dead wave-2 seats

28 seats died on 429. The lane re-ran their executable checks but not these 5 static reviews: RevJjNovelPaths, RevVProbeRows, RevQuarantineRunbook, RevCensusHeaderTruth and RevKnowledgeEntry (the last was covered by CriticKnowledgeOverreach and ScribeKnowledgeFinal).

This closure's C1 and C3 probes stand in for the behaviour that the first and fourth reviews would have checked. Reading the runbook found R1, which RevQuarantineRunbook would have checked. No claim number depends on an un-redone review.

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 re-measured (D1/D2 probes) + matrix 14→0 failed, no new contraction vs 5fa6017 |
| calibration | improved | C2 evidence-verified (w2 majors 3→1, selftest 20→66 severity-exact, R17-M1 correction agreed). Scoped to the committed r16 corpus. |
| coverage | improved | C3 re-measured (keep-ref NOT-SAFE, plain identity) + fixture 13→0 failed; new governed edge class (F1-jj) |
| depth | unchanged | not claimed (SKILL gains jj error patterns, not measured as a move) |
| freshness | unchanged | not claimed |
| adjacency | unchanged | not claimed. Helper hazards were reported to the orchestrator-owned `scripts/hyaku/jj-lane.sh`, not changed. |

## Discernment spot-check (LEARNING.md)

| item | gate decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S054 jj `refs/jj/keep` | admit (mined) | `curl https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs` (sha256 `95147270…` = row) | agree | `:100` `const NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/";`; the quote at `:868-869` is verbatim. The lesson says "22 words"; `wc -w` gives 20 (≤25 either way). |
| S056 nested-repo skip | admit (mined) | `CHANGELOG.md` at v0.45.1 `:1218` `## [0.36.0] - 2025-12-03`, `:1268-1269` | agree | quote verbatim; grounds R17-M3 |
| S060 `--all` | admit (mined) | `man git-rev-list` (installed 2.56.0) | agree | "Pretend as if all the refs in refs/, along with HEAD, are listed…" verbatim, 19 words |
| S062 fifo(7) | admit (mined) | https://man7.org/linux/man-pages/man7/fifo.7.html | agree | "Normally, opening the FIFO blocks until the other end is opened also." verbatim; supports stat-only classification |
| S061 str.lstrip | admit (mined) | https://docs.python.org/3/library/stdtypes.html | agree | "…argument is not a prefix; rather, all combinations of its values are stripped" present |
| reject: `HEAD --not --all` output as keep-ref evidence | reject | command: `git update-ref refs/jj/keep/x HEAD; git log --oneline HEAD --not --all \| wc -l` | agree | 0 by construction (HEAD ∈ `--all`, S060), so it cannot show keep-held content |
| reject: durable roots = refs/heads\|tags\|remotes only | reject | S063 git-gc NOTES ("…and anything else in the refs/* namespace"), fixture J7 | agree | `refs/stash` is a gc-durable ref; dropping it would over-refuse plain repositories |

Quality criteria: Q27 cites R17-M1 and Q28 cites R17-M3, and both lessons rest on a re-read transcript line or a jj source row. Agreed as grounded.

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0, `souji ok`. W04 lists S035, S036, S038, S049, S057, S058, S059 and S063, all shared-URL scopes as reported.

## Trend verdicts

- **expansion: improved.** The admitted knowledge entry `jj-colocation-receipts.md` covers new ground (F1-jj, PROVINCE boundary). Its sources are mined rows S051–S063, and five of them were re-opened above. Three capabilities were added with committed evidence.
- **quality: improved.** D3 got append-only LOG corrections, the r16 seat-audit disposition was corrected (R17-M1), and the M5 regression was caught and fixed before final landing. No admitted entry failed re-check. New pointer defects (R2, R3) are routed below.
- **discernment: improved.** The spot-check agrees on 5 admits and 2 rejects. Both new criteria carry lessons.

## Routed defects (souji owes these next round)

- **R1 (C3 runbook, operability).** `tools/souji-quarantine.sh:246-251` `q_jj_commit_recipe` hardcodes `--as souji`. `scripts/hyaku/jj-lane.sh:516-517` refuses any `--as` other than the repo's lane id or `protocol`, so the printed recipe fails for every sibling jj lane. SKILL.md's own rule says "the OWNING lane's helper … `--as <owner-id>`". This fails closed (the helper refuses; no damage), but the report's "quarantine prints the helper runbook" is wrong for every repo except souji's own. Fix the recipe to use the owner id and add a fixture assertion.
- **R2 (evidence pointer).** `LOG.md:916` (D3 correction entry) and the SKILL registry row `r17-gate-replays` (`SKILL.md:165`, pinned-value column) cite `census/round-17/gate-replays-ddb7347.json`, which no commit in 5fa6017..2cfc6c0 contains. The committed record is `gate-replays-4f48343.json` (`r16-precarry` 79bbe7a exit 1, 29 findings, `match: true`). Fix with an appended LOG correction and a registry pointer fix.
- **R3 (SCORECARD precision).** The operability row's "live fleet paired rows identical (22 repos)" should read 21 repositories (22 rows include the header).
- **R4 (corrections sweep).** `corpus/QUALITY.md` Q7 still prescribes `commit -- <paths>` with `-c maintenance.auto=false` for "every lane or hygiene commit". Under the r17 SKILL rule, jj-colocated repos commit only through the helper. Narrow Q7 to plain repos.
- **R5 (carried).** Five dead wave-2 static reviews were not redone (see above). The census TOCTOU FIFO swap, keep-ref lifetime, and the inherited contractions vs `a31642d` stay open under the lane's L0 lines.

Operator note: the 4 SHONEN boxes look checkable by a non-author from committed evidence. Promotion is operator-owned and was not acted on here.

Tool installs by this closure: none (gitleaks, jq, jj 0.45.1 and shellcheck were already present).
