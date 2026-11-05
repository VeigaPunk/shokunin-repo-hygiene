# S67SentinelScope — souji round 67 scope and safety audit

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Instruments at 05eb2cee. Candidate: .ufo/waves/round-67/w1/S67ExecWriter/candidate/souji-receipt-write.py (sha256 62ca61e946c03699946bdb11a30cba04712ee706fe8e4ca7d6e4a67706058e46, matches its SHA256SUMS). Base writer tools/souji-receipt-write.py sha256 a8c47d36…97fc (unchanged). Git 2.56.0. Instrument hashes match the prereg: c1-counter 69f11706…, c2-counter 045b47d1…, c1-matrix 5d26b341…, c2-statements 8782a21d….

No lane, prereg, control, MANIFEST, .ufo/state or fleet-root file was written. All probes ran in scratch (/fast/scratch/hyaku/souji-r67/S67SentinelScope, removed at exit). The only git mutations were fixture-scoped (`git -C "$D"`, toplevel asserted) plus a `git replace` inside a `--shared` scratch clone of the lane.

## Verdict

- HIGH: none.
- MEDIUM: 2 instrument findings (M1, M2), 2 wave-contract findings (C1, C2).
- The candidate writer's security surface (Part B) is clean: no finding at MEDIUM or above.
- The frozen instruments are safe to run only with the caller environment scrubbed of GIT_COMMON_DIR and GIT_NO_REPLACE_OBJECTS (see M1, M2). Neither defect changes any frozen target or any claim verdict in the current lane state (verified below).

## Part A — instruments at 05eb2cee (read-only)

| check | result | evidence |
|---|---|---|
| (a) credential / secret shapes | PASS | Narrow scan of census/round-67 (counters, matrix, statements, controls, probes) for ghp_, github_pat_, sk-…, AKIA…, PRIVATE KEY, op://, xox[bp]-, JWT-shaped, /root/ and /home/ strings: no credential material. Only hits were "token" as a claim/refusal word (c1 l.190-191 GIT_ID_NAME/GIT_ID_EMAIL are throwaway fixture identities `C1 Counter` / `c1-counter@invalid`). |
| (b) env-value redaction | PASS for names; see L1 | r66 refusals print names only: base writer l.293-298 (RECEIPT-ENV-CONFIG-SET / REDIRECT-SET join names), l.304-306 `(value not shown)`. Candidate `mismatch` text (l.300-301) names the variable only. Probe A/B (below) shows a secret-shaped sentinel value and an empty value never reach stderr. Counter `# detail` lines (c1 l.705-707, 734-735) print writer stderr truncated to 160 chars; no value-leak check exists in the counter (L1). |
| (c) write scope | FAIL under ambient env — M1 | Counters guard --work (c1 l.915-925: must exist, not /tmp, /var/tmp, $TMPDIR, not in root); no tempfile/mkdtemp/TMPDIR use in c1 or c2; c2-mutate uses mkstemp beside --out (c2-mutate l.81-82). But counter-owned git calls inherit a caller GIT_COMMON_DIR and write into it (M1). |
| (d) network / subprocess / signals / sysctl | PASS | No urllib/socket/http imports. No shell=True, no os.system. Subprocess uses are git plumbing, `sys.executable` for the slot/fixture runs, and two inline helpers (CHMOD_CODE, RETARGET_CODE, c1 l.210-213). No kill/signal sends in instruments (c1 l.53-.. none; c2 none). No sudo/sysctl/pacman strings in any instrument. |
| (e) mutant recipes refuse ambiguous / non-compiling | PASS | c2-mutate: anchor must occur exactly once (l.55-57); SystemExit caught and mapped to rc 2 (l.76-80); --out must not exist (l.67-69); compile() check with tmp removal in finally (l.86-97). Verified: ambiguous anchor (2 hits) refused "occurs 2 times (need exactly 1)"; absent anchor refused "occurs 0 times"; overwrite rc 2. Non-compiling branch read, not exercised. |

Kill-power spot checks (scratch, pure in-memory): declared c2 selftest `SELFTEST pass cases=17 fail=0 EXIT=0`; reverted-rule mutant `SELFTEST pass cases=17 fail=1`, `m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`, EXIT=1; declared counter at pinned c13fbb4e: `FINDING SCOPE-OVERREACH s5`, `SUMMARY rows=5 findings=1 verdict=FAIL`, EXIT=1; enum-weakened at pinned: `SUMMARY rows=5 findings=0 verdict=PASS`, EXIT=0. All match the prereg targets.

### M1 (MEDIUM) — C1 counter writes outside --work when the ambient env carries GIT_COMMON_DIR

- Anchors: c1-counter.py `clean_env()` l.342-353 scrubs GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_*, GIT_REPLACE_REF_BASE, GIT_CONFIG_*, GIT_NO_REPLACE_OBJECTS, but NOT GIT_COMMON_DIR (nor GIT_NAMESPACE / GIT_CEILING_DIRECTORIES, L3). Every counter git call goes through it: `git_run` l.356-358 (build_repo init l.367, user.name/email config l.373-376, add/commit l.391-396, update-index l.440-443), `git_show` l.622-628, `git clone --shared` of the lane l.646-648, `run_slot` l.554 (`env=clean_env(env_extra)`), `run_fixture` l.661-663.
- Docstring claim it breaks: "Writes only under --work and --receipt" (c1 l.146-148), and the seat bound "counters write only under --work".
- Evidence (scratch stand-in repo S, fixture D, caller env GIT_COMMON_DIR=S/standin/.git, exactly the call shapes build_repo uses): `git -C D init -q` rc 0 created config, description, hooks, info, objects inside the stand-in common dir; `git -C D config user.name C1Counter` wrote `user.name=C1Counter` into the stand-in's .git/config; add/commit rc 0 and the stand-in object count went 3 → 6 (the fixture's blob, tree and commit landed in the stand-in's object store; the fixture cannot read its own HEAD commit without the variable).
- Lane impact: the lane itself was not used. If an operator's ambient env pointed GIT_COMMON_DIR at the lane's common dir, the same mechanism would write config and objects into the live lane [INFERENCE — same mechanism, not run against the lane]. The committed control receipts contain no GIT_COMMON_DIR text (grep count 0 in controls/c1-do-nothing.txt, c2-do-nothing-r66.txt, c2-do-nothing.txt), so no frozen control shows the variable set; no frozen result is affected.
- Smallest remediation (next round, new frozen counter, not an amendment): add GIT_COMMON_DIR, GIT_NAMESPACE, GIT_CEILING_DIRECTORIES to the clean_env scrub list, or refuse counter start when any GIT_* repository-redirect variable is set in os.environ. This round: the operator run procedure must start with `env -u GIT_COMMON_DIR -u GIT_NO_REPLACE_OBJECTS` (or equivalent) and the run receipt should carry `env` names. Main agent to record this in the round report.

### M2 (MEDIUM) — C2 binds pinned historical bytes through ambient replace refs and caller env

- Anchor: c2-counter.py `git_show` l.164-166 runs `git -C root show rev:rel` with no env argument. Unlike c1 (clean_env l.348 scrubs GIT_NO_REPLACE_OBJECTS) and the base writer (l.97 sets GIT_NO_REPLACE_OBJECTS=1), the C2 read honours repo-local `refs/replace/*` and any caller GIT_REPLACE_REF_BASE / GIT_NO_REPLACE_OBJECTS / GIT_DIR / GIT_OBJECT_DIRECTORY.
- Evidence (scratch `--shared` clone of the lane, `git replace <SKILL.md blob @ c13fbb4e> <blob 'x\n'>`, toplevel asserted): `git show c13fbb4e:SKILL.md` md5 401b30e3… by default vs fd03474b… with GIT_NO_REPLACE_OBJECTS=1. The unmodified C2 counter on that clone at the pinned rev prints `SUMMARY rows=5 findings=5 verdict=FAIL` by default, and `FINDING SCOPE-OVERREACH s5 … SUMMARY rows=5 findings=1 verdict=FAIL` with GIT_NO_REPLACE_OBJECTS=1. So the pinned C2 verdict depends on ambient replace refs and env, and the receipt binds only `rev=` and the counter sha.
- Lane state at audit: `git -C <lane> replace -l` empty; lane refs list shows no refs/replace; `git status` shows only the pre-existing `M corpus/QUALITY.md`. The frozen C2 target reproduces in the lane as prereg (FINDING s5, findings=1, EXIT=1).
- Smallest remediation: next round's C2 receipt records `git -C root replace -l | wc -l` and runs the reads with the replace/redirect env scrubbed (same tuple as c1 clean_env). This round: main agent to confirm `replace -l` is empty before the official C2 run.

## Part B — candidate writer (S67ExecWriter/candidate, read + scratch probes)

| check | result | evidence |
|---|---|---|
| (a) credential / secret shapes in delta | PASS | Narrow scan of the candidate: none. /tmp appears only in the docstring (l.22) and never as a path. |
| (b) refusal leaks no path / value | PASS | `_check_env_commondir` l.290-309 prints only the constant message (refuse() l.109-112 prints `refused: <msg>`). Probe A (secret-shaped nonexistent sentinel path) rc 2, stderr = constant text, sentinel count 0, no receipt. Probe B (empty value) identical. Probe E (root not a repo) same constant text. |
| (b') scrub tuple cannot leak caller value via git stderr | PASS | `git()` env builder (l.98-100) now drops GIT_COMMON_DIR with GIT_DIR and GIT_WORK_TREE. The new check runs before any writer git call (write_receipt l.338-339 precedes the first git at l.348; main() dispatches to write_receipt without a git call, l.1558-1593). |
| (b'') resolution stderr not echoed into any receipt | PASS | rev-parse result: stdout used only in realpath compare (l.307), stderr never read, `r.returncode != 0` maps to the constant refusal (l.305-306). |
| (c) write scope | PASS | Writer writes only OUT and a temp beside OUT (mkstemp, l.540). The new code writes nothing. `_status_z` (l.154-157) and all writer git calls go through `git()`; direct `subprocess` git calls at l.590-1019 are test-harness fixture builders only. |
| (d) no network / signals / sysctl / sudo | PASS | No new imports or subprocess call types. Wrapped command launch at l.467 has no env= and no cwd= (inherits writer env and cwd), unchanged from base. Overflow `proc.kill()` (l.480-483) is pre-existing r60 writer code, acts only on its own child. |

Probe results (scratch fixture D, `git -C D rev-parse --show-toplevel` asserted):
- A sentinel mismatch: rc 2, `refused: RECEIPT-ENV-COMMONDIR-MISMATCH: GIT_COMMON_DIR is set in the writer's environment and does not resolve to this repository's common dir (value not shown); unset it and retry`, no receipt.
- B empty value: rc 2, same text, no receipt.
- C equal absolute value `$D/.git`: rc 0.
- D unset control (--allow-dirty; the earlier untracked receipts/ dir tripped the writer's own dirty check, which is correct behaviour): rc 0.
- F equal value (--allow-dirty): rc 0.
- I relative equal value `<basename>/.git` with writer cwd = fixture parent (≠ root): rc 0. Consistent: the wrapped command runs in the same cwd and env, and git resolves a relative GIT_COMMON_DIR only alongside a discovered repository (probe J: `GIT_COMMON_DIR=<rel>` with no repo at cwd → "not a git repository", rc 128, fail-closed).
- K wrapped `pwd` ran in the writer's cwd, not --root (pre-existing r60 behaviour; see L6).
- G secret-shape grep over candidate: none. H /tmp / TMPDIR literal in non-test code: none.

### L2 (LOW) — misattributed refusal when --root is not a repository

- Anchor: candidate `_check_env_commondir` l.304-306 maps any rev-parse failure to the COMMONDIR mismatch text, and l.338-339 run before the `root is a directory` check (l.344-345). Probe E (root = a directory with no repo, GIT_COMMON_DIR set) prints the COMMONDIR message, not a not-a-repository reason. Diagnostic only; no value or path leak.

## Part C — wave contract (this context's bounds)

- C1 (MEDIUM) — report path contradicts the seat bounds. Target says deliver `.../w1/S67SentinelScope/scope.md`. The Report trailer says `.ufo/waves/round-67/w1/S67SentinelScope.md` (w1 level, outside the seat dir), and the trailer rule says "write at <that path> (i.e. inside .ufo/waves/round-67/w1/<SeatName>/)". The hard bound says "Deliver ONLY under .../w1/<YourSeatName>/". These cannot all hold. I delivered only the seat-dir file. Orchestrator to name the one path.
- C2 (MEDIUM) — the generic tooling directive can be read to authorize pacman and sudo, against the seat and host rules. Generic rules (2026-10-19, "always on, every agent") say "any agent installs or updates any tool… with full privilege, without asking", list `sudo pacman -S --needed --noconfirm` as the first channel, say passwordless sudo is available, and name `~/.local/bin` as the install target. The seat contract says pacman stays PAUSED (ruling 2026-10-20) and names ~/.local/bin as an install target, while the host guard says never create, modify or delete anything in ~/.local/bin. Precedence is not stated. Seat action: installed nothing; git 2.56.0 and python 3.14 were already present.
- C3 (LOW) — "/tmp holds files under 50 MB only" (Delivery/scratch bullet) reads as authorising /tmp writes, against "write only there" and the counters' own /tmp ban. Disclosure: my own test ran `c2-mutate.py --out /tmp/should-not-write-<pid>.py`; the file was verified and removed, and `ls /tmp/should-not-write-*` is empty.
- C4 (LOW) — the Milestone line lists "corpus drafts", "git source capture" and "env-export probes", none in this seat's Target, while the bounds say deliver only under the seat dir. The wording could be read to authorise corpus/ or census/ writes. Seat wrote nothing there.
- C5 (LOW) — "Seats never … run a mutating git/jj command anywhere" conflicts with the fixture rules, which allow commits in fixtures. The fixture exception should be stated explicitly. Seat mutations were fixture-scoped only; one `git replace` in the scratch clone ran after the toplevel assert had been made in an earlier cell (the clone itself was verified then; I did not re-assert in that cell).
- C6 (LOW) — "keep going until this ticket is closed" with an open milestone list has no explicit stop condition apart from the deliverable. Read as the Target only.
- C7 (INFO) — lane working tree is not clean at audit: `M corpus/QUALITY.md` (uncommitted). The round-start base was clean. Not this seat's; C1/C2 measurements use committed revisions and are unaffected.

## Remaining named items and what this seat did not cover

- L1 (LOW) — counter `# detail` lines (c1 l.705-707) carry writer stderr verbatim into committed receipts. Nothing checks for value echo, because W1/W2 values are counter-chosen paths. A sentinel-valued row is needed to test no-echo. Next round.
- L3 (LOW) — controls/c1-do-nothing.txt l.4 cites `--new-tool /fast/scratch/hyaku/souji-r67/l1/base-writer.py`, an L1 scratch file that the probes note says is removed at landing. The control is re-derivable only from the base blob (sha a8c47d36 = `--rev 3639087917…:tools/souji-receipt-write.py`). Reproducibility note.
- L4 (LOW) — c2-mutate `--out` is not confined; it writes wherever the caller points (by design; see C3).
- L6 (INFO) — wrapped `--command` runs in the writer's cwd, not --root (candidate l.467, pre-existing r60). Relevant to the prereg L2 wording, which assumes writer-cwd canonicalisation. Consistent with the check (probes I/J).
- Not covered: the full C1 matrix (31 rows) and C2 population/claim attacks are other seats' work; no full counter run was made in this seat. Part B covers the delta's security surface and probes only.

## Recommendations (summary)

1. M1: operator runs every counter with GIT_COMMON_DIR unset; next-round counter scrubs it (plus GIT_NAMESPACE, GIT_CEILING_DIRECTORIES).
2. M2: operator asserts `git -C LANE replace -l` empty before the official C2 run; next-round C2 receipt records it and scrubs replace env.
3. C1/C2: orchestrator names one report path and states the tooling-directive precedence (pacman PAUSED, no PATH-dir writes) explicitly.
4. L2: the candidate may map a non-repository --root to a distinct refusal; not required for the frozen claim.
