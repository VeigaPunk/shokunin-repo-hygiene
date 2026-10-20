STATUS: DONE — Q29–Q32 drafted for `corpus/QUALITY.md` `## Round 18 criteria`; each test column is unmet until its named build lands (see Landing dependencies).

# ScribeQualityRows — round 18, wave 1 (calibration)

Scope: draft four QUALITY rows. Per the seat contract a scribe writes only its report, so the table below is for L1 to paste under `## Round 18 criteria` in `corpus/QUALITY.md` after `## Round 17 criteria`. Columns are the existing ones: id | criterion | applies-to | test | lesson. Q7 text is not edited; Q29 names Q7 as the row it supersedes, per the file's own rule (a superseded criterion is never rewritten).

## Draft rows

```
## Round 18 criteria

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q29 | Supersedes Q7 for jj-colocated repositories only (`.jj/` and `.git/` at one root). In such a repository a lane or hygiene commit goes only through the owning lane's helper (`scripts/hyaku/jj-lane.sh commit --as <owner-id> -- <paths>`, where owner-id is the repository's recorded lane id), names BOTH the source and the destination of any move, and is followed by a `git cat-file -e <commit>:<path>` post-check on each named path. Q7 is not rewritten; it stays in force for plain repositories (no `refs/jj/`). | commits in jj-colocated repositories; `tools/souji-quarantine.sh` (`q_jj_commit_recipe`); SKILL lane-commit rule | the recipe printed for a non-souji owner carries `--as <owner-id>` and both paths (behaviour fixture assertion, landed with the R1 fix); the fleet helper accepts the printed command; `git -C <repo> cat-file -e <commit>:<dest>` succeeds and `cat-file -e <commit>:<source>` fails; a plain-repository commit still satisfies Q7 (`git show --stat --format= <hash>` lists only named paths) | corpus/lessons/round-17-verifier-spotcheck.md R4 (Q7 narrowed to plain repositories); same file R1 (`--as souji` hardcoded at tools/souji-quarantine.sh:247); corpus/knowledge/jj-colocation-receipts.md §8 (name both paths of a move) |
| Q30 | No single repository may hang the census. `tools/souji-census.sh` runs each repository's census in its own process group under a per-repository bound (`--repo-timeout N` or env `SOUJI_CENSUS_REPO_TIMEOUT`; integer 1..86400; default 600; invalid is usage exit 2). On timeout the group gets SIGTERM, then SIGKILL 2 s later; that repository becomes the row `<repo>\t0\t0\t0\t0\t\terror` with stderr `souji-census: repo-timeout <N>s <repo>`, and every other repository is still measured. A protected refusal (census_one exit 2) still exits the run 2; other failures still exit 1. Every fixture subprocess runs in its own session and is killed by process group on timeout. | `tools/souji-census.sh` (emit_census, census_one); each fixture `tests/fixtures/r18-<name>.sh` that runs census or git subprocesses (name fixed by the C1 build) | `bash tests/fixtures/r18-<name>.sh --tool-dir tools`: a FIFO planted over `.git/info/attributes` after the guard passes (PATH git shim) returns rc 0 within the bound, yields the hung repository's row and stderr line exactly as stated, and measures the healthy neighbours; an invalid bound exits 2; after the run `ps -eo pgid=` shows no process in the fixture's sessions; the red arm leaves 0 blocked processes | census/round-18/leaked-procs-before-1631.txt (58 processes, all from souji fixtures, blocked in deleted /var/tmp dirs: `r15-census-config` `rev-parse` and `r17-census-hygiene` `status`); corpus/lessons/round-17-verifier-spotcheck.md (D2 FIFO and the open TOCTOU residual) |
| Q31 | Authority-file evidence pointers resolve at the landing revision. Every repo-relative path token under `census/`, `tests/`, `tools/`, `corpus/` and `.ufo/waves/` cited in SKILL.md, SCORECARD.md, PROVINCE.md, corpus/QUALITY.md, corpus/README.md, corpus/knowledge/*.md, the round's lesson, or LOG.md's round section must exist in the tree at REV (a `path:line` suffix is stripped; tokens containing `<`, `>`, `*` or the literal `round-N` are skipped). A token that resolves only in the fleet repository is reported as `fleet`, not as a finding. A deliberate non-file is exempt only through a committed `corpus/pointer-exemptions.tsv` (path, reason). A frozen record whose `measured_commit` does not resolve is LG-FROZEN-MEASURED (closes the Q25(b) open item). | `tools/souji-landing-gate.py`, new finding `LG-DANGLING-PTR`, applied only when `--round` is 18 or higher; pinned historical replays in census/round-17/gate-replays-expected.json stay identical | `python3 tools/souji-landing-gate.py --root <lane> --rev <REV> --round 18` reports zero `LG-DANGLING-PTR` at the round tip (the changed gate at b576341 with `--round 18` reports the pre-fix count); `python3 tools/souji-landing-gate.py --selftest` covers a dangling token, a fleet-only token, a committed exemption and a non-resolving `measured_commit`; the round-17 replay record is byte-identical | corpus/lessons/round-17-verifier-spotcheck.md R2 (dangling census/round-17/gate-replays-ddb7347.json at SKILL.md:165 and LOG.md:916); the same dangling-pointer defect in the jj-receipts-ddb7347 pointer at corpus/knowledge/jj-colocation-receipts.md:2,44,126,148 (not routed by the closure) |
| Q32 | Process residue is governed as a listing surface only. `tools/souji-proc-census.sh` lists processes of the current uid whose cwd is deleted, or whose argv names a path under /var/tmp, /tmp or /dev/shm that no longer exists, reporting pid, ppid, pgid, age, state/wchan, reason and a redacted, truncated command. It reads only `/proc/<pid>/{stat,cmdline,cwd,wchan}` (never `environ`), is dry-run only, and never signals. Killing any listed process requires the operator's explicit approval in the conversation, is recorded in LOG.md, and is run by the operator, never by the census or a fixture. Extends the report-only pattern of Q14. | `tools/souji-proc-census.sh` (new in C3); `corpus/QUALITY.md` Q14 pattern | a fixture starts a sleep child whose argv names a /var/tmp directory, removes that directory, and runs the census: the child appears with pid, ppid, pgid, age, state, reason and redacted command; after the run `ps -p <pid>` still shows the child alive in the same state (no signal); a planted secret-like argv value is absent from the output; a spelling check that the source has no signalling call (`grep -nwE 'kill\|pkill\|killpg\|SIGKILL\|SIGTERM'`, paired with the behaviour check per Q19) | census/round-18/leaked-procs-before-1631.txt (58 blocked processes in deleted /var/tmp dirs, the residue class this criterion governs); corpus/QUALITY.md Q14 |
```

Note: the fenced block above is the paste-ready text. Inside the cells, `\t` is a literal backslash-t as the census row spelling and `\|` is a literal pipe escape for the grep spelling (the rows use `|` only as the table separator, so the grep pattern must be written as `kill\|pkill` in the cell or as a `grep -E` alternation in prose if L1 prefers; do not paste a bare `|` into a table cell).

## Basis of each row (exact checks run)

Read-only checks by this seat (all on exact named paths or `ls` of one directory; no census, verify, quarantine, or proc-census script was run, no git write, no jj):

| check | command | observed |
|---|---|---|
| Q7 text and table shape | `read corpus/QUALITY.md` | Q7 row present unchanged; table columns `id \| criterion \| applies-to \| test \| lesson`; Round 17 heading at :67, Q27 :71, Q28 :72; highest id Q28 |
| R1 recipe | `read tools/souji-quarantine.sh:240-255` | `q_jj_commit_recipe` at :246-251 prints `jj-lane.sh commit %s --as souji -m …` (line 247) |
| r17 closure R1–R5 | `read corpus/lessons/round-17-verifier-spotcheck.md` | R1 at :149 (`--as souji`), R2 at :150 (gate-replays-ddb7347), R3 at :151 (22 vs 21), R4 at :152 (Q7 narrow), R5 at :153 |
| jj rule | `read corpus/knowledge/jj-colocation-receipts.md` | §8 at :71–75 (name both paths); the `jj-receipts-ddb7347` pointer at :2, :44, :126, :148 |
| leaked processes | `wc -l census/round-18/leaked-procs-before-1631.txt`; `head -3` | 58 lines; rows show `r15-census-config` `rev-parse` and `r17-…` fixture commands under deleted /var/tmp dirs |
| gate CLI | `grep add_argument tools/souji-landing-gate.py` | `--root`, `--rev`, `--round`, `--base`, `--json`, `--selftest` exist (:1353–1358); pinned finding ids at :56–57 and :116–122 (seven ids, no `LG-DANGLING-PTR` yet) |
| receipt fixture | `read tests/fixtures/r17-jj-receipts.sh:1-12` | exists; the `--tool-dir` interface is used by Q29/Q30 test prose |
| existence of cited tokens | `test -e` on each cited path | present: tools/souji-landing-gate.py, tools/souji-quarantine.sh, tools/souji-census.sh, tests/fixtures/r17-jj-receipts.sh, census/round-18/leaked-procs-before-1631.txt, corpus/lessons/round-17-verifier-spotcheck.md, corpus/knowledge/jj-colocation-receipts.md, census/round-17/jj-receipts-4f48343.txt, .ufo/waves/round-18/w1 |

## Landing dependencies (rows are drafts; these tokens are not in the tree at b576341)

A QUALITY row is an admission bar; its test must be true at the landing revision. These items are missing now and must land in the same round, or the row's test fails and the gate's pointer check flags it:

| token or behaviour | status at b576341 | owner |
|---|---|---|
| `tools/souji-proc-census.sh` (Q32) | MISSING | C3 build |
| `corpus/pointer-exemptions.tsv` (Q31) | MISSING | C2 build |
| `tests/fixtures/r18-<name>.sh` (Q30) | not present; the `<name>` placeholder is intentional (skipped by the pointer rule) | C1 build |
| `--repo-timeout` / `SOUJI_CENSUS_REPO_TIMEOUT` in tools/souji-census.sh | absent: `grep -c 'repo-timeout\|REPO_TIMEOUT' tools/souji-census.sh` → 0; `census_one` at :1261, `emit_census` at :1394 (the C1 change points) | C1 build |
| `LG-DANGLING-PTR` | absent; the pinned finding-id list at tools/souji-landing-gate.py:116–122 (and the comment at :56–57) must add it | C2 build |
| `q_jj_commit_recipe` owner id (Q29) | line 247 still `--as souji` | R1 fix |

## Findings for L1

1. **Pointer defect not routed by the closure.** `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148` cites `census/round-17/jj-receipts-ddb7347.txt`, which is absent. The committed record is `census/round-17/jj-receipts-4f48343.txt` (present; base is `jj-receipts-base5fa6017.txt`, also present). Q31's lesson column names it; the rows themselves avoid repeating the missing path, because QUALITY.md is scanned by the same gate. Verdict: holds as a finding; fix is a knowledge-entry pointer correction in the C2 lane, not in this draft.
2. **Q7 mechanics.** Q29 narrows Q7 by superseding row, leaving Q7's text intact as the file's rule requires. R4 (round-17 closure) asked for "narrow Q7 to plain repos"; the superseding-row form satisfies it without rewriting the criterion. Verdict: holds.
3. **Round-18 lesson file absent.** `corpus/lessons/round-18.md` does not exist at b576341, so no row cites it. The lesson column cites the round-17 closure, the leaked-process census file, and the existing knowledge entry. If ScribeLessonDraft lands `corpus/lessons/round-18.md`, L1 may add it as a lesson pointer for Q30 and Q32 once it exists. Verdict: partial until then.
4. **Test columns are unrun.** No row's test was executed by this seat (scribe; executing fixtures is the L1 gate). Each test names a command or observable a landing must produce. Verdict: unmet until the listed builds land.
5. **Shell-cell hazard.** The Q32 test cell contains a grep alternation with `|`, which breaks a markdown table. The draft escapes it as `\|`; L1 should keep that escape or move the spelling check into prose.

## Verdicts

- Q29: holds as a draft; test unmet until R1 lands (line 247).
- Q30: holds as a draft; test unmet until C1 lands.
- Q31: holds as a draft; test unmet until C2 lands (`LG-DANGLING-PTR`, exemptions file); closes the Q25(b) open item when `LG-FROZEN-MEASURED` also catches a dangling `measured_commit`.
- Q32: holds as a draft; test unmet until C3 lands.

## Out of scope / not done

- No edit to `corpus/QUALITY.md` (scribe seat; L1 integrates).
- No commit, no jj, no git write, no fleet-repo write, no census or tool execution, no operator-sweep file opened.
- No subagent dispatched (leaf seat).

## Tool installs

None. Read/grep/`test -e`/`wc`/`head` only.
